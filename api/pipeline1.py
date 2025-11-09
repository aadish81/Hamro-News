import asyncio
import httpx
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv()

from filter_newest_news import filter_last_24_hours, get_latest_timestamp
from generator import failed_nepali_news, UseOpenai, PostToDB
from embedding import add_news_to_clusters, clusters, logger
from imageGenerator import FirecrawlSearch

class NewsProcessor:
    """Main class to process news from multiple sources."""
    
    def __init__(self):
        self.sources = [
            "routineofnepalbanda","indepthstory","24ghantanepal","nepalpolice","nepalitimes"
        ]
        self.url_fragment = "{media{id,caption,timestamp,media_url}}"
        self.base_url = "https://graph.facebook.com/v23.0/17841477428983090"
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.todays_news: List[Dict[str, Any]] = []
        self.use_ai = UseOpenai()
        self.post = PostToDB()

    async def fetch_news_from_source(self, client: httpx.AsyncClient, source: str) -> Optional[Dict]:
        """Fetch news from a single source."""
        # global clusters
        # clusters = {}
        url = f"{self.base_url}?fields=business_discovery.username({source}){self.url_fragment}&access_token={self.access_token}"
        
        try:
            timeout = httpx.Timeout(10.0, connect=5.0)
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except asyncio.TimeoutError:
            logger.error(f"Timeout error for {source}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {source}")
        except httpx.RequestError as e:
            logger.error(f"Request error for {source}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {source}: {e}")
        
        return None

    def extract_news_items(self, response_data: Dict, source: str) -> List[Dict]:
        """Extract news items from API response."""
        try:
            business_discovery = response_data.get("business_discovery", {})
            media_data = business_discovery.get("media", {})
            news_items = media_data.get("data", [])
            
            if not isinstance(news_items, list):
                logger.warning(f"Unexpected data format for {source}: 'data' is not a list")
                return []
                
            return news_items
        except Exception as e:
            logger.error(f"Error extracting news for {source}: {e}")
            return []

    def filter_and_add_news(self, news_items: List[Dict], source: str):
        """Filter news from last 24 hours and add to today's news."""
        for news in news_items:
            try:
                if not isinstance(news, dict):
                    logger.warning(f"Skipping invalid news for {source}")
                    continue
                    
                if "timestamp" not in news:
                    logger.warning(f"News item missing timestamp for {source}")
                    continue
                
                if filter_last_24_hours(news["timestamp"]):
                    news_copy = news.copy()
                    news_copy["source"] = source
                    self.todays_news.append(news_copy)
                    logger.debug(f"Added news from {source}")
            except Exception as e:
                logger.error(f"Error processing news item for {source}: {e}")

    async def process_sources(self):
        """Process all news sources concurrently."""
        timeout = httpx.Timeout(10.0, connect=5.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            tasks = [self.fetch_news_from_source(client, source) for source in self.sources]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source, response in zip(self.sources, responses):
                if response and isinstance(response, dict):
                    news_items = self.extract_news_items(response, source)
                    self.filter_and_add_news(news_items, source)

    async def enhance_news_with_ai(self):
        """Add title and English translation to news using AI."""
        valid_news = []
        
        for news in self.todays_news:
            if not news.get("caption"):
                logger.error(f"No caption in news: {news.get('id', 'unknown')}")
                continue
            
            try:
                title, english_news = await self.use_ai.generate_title(news["caption"])
                
                if not title or not english_news:
                    logger.error(f"AI failed to generate title/translation for news: {news.get('id', 'unknown')}")
                    continue
                
                news["title"] = title
                news["caption"] = english_news
                valid_news.append(news)
                logger.debug(f"Successfully enhanced news: {title}")
                
            except Exception as e:
                logger.error(f"Error enhancing news {news.get('id', 'unknown')}: {e}")
        
        self.todays_news = valid_news

    async def cluster_news(self):
        """Cluster news based on title similarity."""
        for news in self.todays_news:
            if "title" not in news:
                logger.error(f"Missing title in news: {news}")
                continue
            
            try:
                await add_news_to_clusters(news["title"])
            except Exception as e:
                logger.error(f"Error adding news to cluster: {e}")
        
        logger.info(f"Total {len(clusters)} clusters formed from {len(self.todays_news)} news items.")

    async def process_image(self, image_urls: List[str], search_query: str) -> str:
        """Process and select the best image for the news."""
        if not image_urls:
            return ""
            
        async with FirecrawlSearch() as searcher:
            is_acceptable = await searcher.check_image_for_news(image_urls, search_query)
            
            if is_acceptable:
                logger.info(f"Using original image URL: {is_acceptable}")
                return is_acceptable
            
            logger.info(f"Image search using: {search_query}")
            success = await searcher.scrape_pages(search_query)
            
            if success and searcher.image_urls:
                logger.info(f"Selected images URLs: {searcher.image_urls}")
                result = await searcher.select_image(search_query)
                
                if result:
                    logger.info(f"Best fit image by scraping: {result}")
                    return result
            
            fallback_image = image_urls[-1] if image_urls else ""
            logger.info(f"Using fallback image: {fallback_image}")
            return fallback_image

    async def create_news_carts(self, news_detail: Dict, cluster_id: int, 
                         sources: List[str], timestamp: str, image_url: str):
        """Create English and Nepali news carts."""
        english_cart = {
            "id": str(cluster_id),
            "title": news_detail["title"],
            "cover_image": image_url,
            "category": news_detail["category"],
            "detail": news_detail["detail"],
            "source": sources,
            "time_of_release": timestamp
        }
        
        nepali_news = await self.use_ai.convert_to_nepali({
            "title": news_detail["title"],
            "description": news_detail["detail"]
        })
        
        nepali_cart = {
            "title": nepali_news["title"],
            "description": nepali_news["description"],
            "cart_id": str(cluster_id)
        }
        
        return english_cart, nepali_cart

    async def process_clusters(self):
        """Process each cluster to generate detailed news and post to backend."""
        for cluster_id, cluster in list(clusters.items()):
            context_parts = []
            sources = []
            dates = []
            image_urls = []
            
            # Gather cluster data
            for title in cluster["texts"]:
                matching_news = [news for news in self.todays_news if news.get("title") == title]
                
                for news in matching_news:
                    context_parts.append(news.get("caption", ""))
                    
                    if news.get("source") and news["source"] not in sources:
                        sources.append(news["source"])
                    
                    dates.append(news.get("timestamp", ""))
                    image_urls.append(news.get("media_url", ""))
            
            # Validate cluster data
            if not all([context_parts, sources, dates]):
                logger.error(f"Incomplete data for cluster {cluster_id}")
                clusters.pop(cluster_id, None)
                continue
            
            # Generate detailed news
            try:
                context = " ".join(" ".join(context_parts).split())
                news_detail = await self.use_ai.generate_news(context)
                
                if not all([news_detail.get("category"), news_detail.get("title"), 
                           news_detail.get("detail")]):
                    logger.error(f"Incomplete AI response for cluster {cluster_id}")
                    clusters.pop(cluster_id, None)
                    continue
                    
            except Exception as e:
                logger.error(f"Error generating news for cluster {cluster_id}: {e}")
                continue
            
            # Process image
            image_url = await self.process_image(image_urls, news_detail.get("image_search", ""))
            
            # Add metadata and create news carts
            news_detail.update({
                "source": sources,
                "timestamp": get_latest_timestamp(dates),
                "cluster_id": cluster_id
            })
            
            try:
                english_cart, nepali_cart = await self.create_news_carts(
                    news_detail, cluster_id, sources, news_detail["timestamp"], image_url
                )
                
                # Post to backend
                await self.post.Post_to_db(
                    english_cart, 
                    os.getenv("CREATE-CARD"),
                    os.getenv("CREATE-DETAIL-E")
                )
                logger.info(f"English news posted for cluster {cluster_id}")
                
                await self.post.Post_nepali_news(
                    nepali_cart,
                    os.getenv("CREATE-DETAIL-N")
                )
                logger.info(f"Nepali news posted for cluster {cluster_id}")
                
            except Exception as e:
                logger.error(f"Error posting news for cluster {cluster_id}: {e}")

    async def retry_failed_nepali_news(self, max_retries: int = 3):
        """Retry posting failed Nepali news."""
        for attempt in range(max_retries):
            if not failed_nepali_news:
                break
                
            logger.info(f"Retry attempt {attempt + 1} for {len(failed_nepali_news)} failed news")
            
            successful_news = []
            for news in list(failed_nepali_news):
                try:
                    await self.post.Post_nepali_news(
                        news, os.getenv("CREATE-DETAIL-N")
                    )
                    successful_news.append(news)
                    logger.info(f"Successfully posted failed news: {news.get('cart_id')}")
                except Exception as e:
                    logger.error(f"Failed to post news {news.get('cart_id')}: {e}")
            
            # Remove successfully posted news
            for news in successful_news:
                failed_nepali_news.remove(news)

    async def create_news(self):
        """Main method to orchestrate the news processing pipeline."""
        logger.info("Starting news processing pipeline")
        
        # Step 1: Fetch and filter news
        await self.process_sources()
        logger.info(f"Fetched {len(self.todays_news)} news items")
        
        # Step 2: Enhance with AI
        await self.enhance_news_with_ai()
        logger.info(f"Enhanced {len(self.todays_news)} news items with AI")
        
        # Step 3: Cluster news
        await self.cluster_news()
        
        # Step 4: Process clusters and post to backend
        await self.process_clusters()
        
        # Step 5: Retry failed Nepali news
        await self.retry_failed_nepali_news()
        
        logger.info("News processing pipeline completed")


async def NewsFetcher():
    """Main entry point."""
    processor = NewsProcessor()
    await processor.create_news()


# if __name__ == "__main__":
#     asyncio.run(main())