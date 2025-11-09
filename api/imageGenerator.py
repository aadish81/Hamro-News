import os
import aiohttp
import json
from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
from embedding import logger

load_dotenv()

class FirecrawlSearch:
    def __init__(self, base_url=os.getenv("FIRECRAWL_URL"), api_key=None):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("BASE_URL"),
            default_query={"api-version": "2024-04-01-preview"},
        )
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
        self.potential_pages = []
        self.image_urls = []
        self.authentic_resources = [
            "en.setopati.com",
            "english.onlinekhabar.com",
            "kathmandupost.com",
            "thehimalayantimes.com",
            "english.ratopati.com"
        ]
        
        
        
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
            
            
            
    
    def _safe_json_parse(self, json_string):
        """Safely parse JSON that might have formatting issues"""
        try:
            # First try direct JSON parsing
            return json.loads(json_string)
        except json.JSONDecodeError:
            try:
                # Try fixing common issues: single quotes, trailing commas
                fixed_json = json_string.replace("'", '"')
                # Remove trailing commas
                fixed_json = fixed_json.replace(',}', '}').replace(',]', ']')
                return json.loads(fixed_json)
            except json.JSONDecodeError:
                try:
                    # Extract JSON using regex as last resort
                    import re
                    json_match = re.search(r'\{.*\}', json_string)
                    if json_match:
                        return json.loads(json_match.group().replace("'", '"'))
                except:
                    pass
        return None
    
    
    
    
    
    
    async def search_for_sites(self, query):
        """Simple search using Firecrawl"""
        endpoints = "/v1/search"  # Using v1 which is more stable
        enhanced_query = f"{query} images photos"
        payload = {
            "query": enhanced_query,
            # "limit": limit
        }
        
        try:
            url = f"{self.base_url}{endpoints}"
            logger.info(f"Searching with endpoint: {endpoints}")
            print(f"Query: {query}")
            
            async with self.session.post(url, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        logger.info(f"Search successful, found {len(data.get('data', []))} results")
                        return data
                    else:
                        logger.error(f"API error: {data.get('error')}")
                else:
                    logger.info(f"HTTP {response.status}")
                    logger.info(f"Response: {await response.text()}")
                    
        except Exception as e:
            logger.error(f"Endpoint failed: {e}")
        
        return None
    
    
    
    
    
    

    
    
    
    
    async def select_url(self, query):
        """Select the best URL from search results using AI"""
        logger.info(f"Selecting URL for query: '{query}'")
        data = await self.search_for_sites(query)
        
        if not data or not data.get('data'):
            logger.error("No search results found")
            return False
        
        logger.info(f"Found {len(data['data'])} search results")
        
        for result in data['data']:
            self.potential_pages.append(result.get("url"))
        

        logger.info(f"Potential Pages: {self.potential_pages}")
        return True

        

    async def check_image_for_news(self, image_urls,query):
        """Check if the image is relevant for news using AI"""
        try:
            resp = await self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an image verifier used by an automated news pipeline. You will be given one or more image URLs and must choose a single image that is appropriate for use as a news illustration **only if** it meets all quality rules below. Follow these rules strictly and return exactly one JSON object as the final output. Do not include any explanation, markdown, or extra text.

                            --- RULES (must be enforced) ---
                            1. Text detection:
                            - The image **must not** contain prominent readable text as part of the image content. This includes headlines, captions, banners, stickers, memes, screenshots, or any overlayed sentence or phrase that would appear as written news on the image.
                            - Small unobtrusive watermarks or photographer credits in a corner are acceptable, but large or centrally placed text is disqualifying.
                            - If you cannot reliably determine whether visible text exists, treat the image as containing text (fail-safe).

                            2. Image relevance:
                            - The image must be visually relevant to the provided news subject or headline (e.g., if the news is about a flood in Kathmandu, images of flooded streets or rescue operations are relevant).
                            - Avoid images that are obviously staged adverts, memes, screenshots of social feeds, artwork/illustrations (unless the article explicitly asks for illustration), or generic stock placeholders that do not depict the subject matter.

                            3. Photo quality:
                            - Prefer clear photographs (good focus, correct orientation) over low-quality, heavily compressed, or too-small thumbnails.
                            - If multiple candidate images meet rules, prefer the one that most clearly and specifically depicts the news subject.

                            4. Single output policy:
                            - If **no** images meet all criteria, return exactly:
                                {"is_relevant": false}
                            - If **one or more** images meet all criteria, return exactly one URL — the single best image — in this format:
                                {"is_relevant": "https://chosen-image-url.example/path.jpg"}
                            - Do not return arrays, reasons, scores, or any other fields.

                            5. Safety & conservatism:
                            - If the image shows screenshots of articles, images with obvious headline text, screenshots of social media posts, or any readable embedded news text — fail the image.
                            - If uncertain about whether text is present or whether the image is relevant, be conservative and return false.

                            --- INPUT CONTRACT ---
                            You will receive:
                            - The news context or headline (short) and
                            - A list of candidate image URLs.

                            Example input (for your internal system):
                            {
                            "headline": "Heavy monsoon flooding in Kathmandu",
                            "image_urls": ["https://site/img1.jpg", "https://site/img2.jpg", "..."]
                            }

                            --- OUTPUT CONTRACT (MANDATORY) ---
                            Return **only one** JSON object, exactly one line, valid JSON. Either:
                            {"is_relevant": false}
                            or
                            {"is_relevant": "https://chosen-image-url.example/path.jpg"}

                            --- EXAMPLES ---
                            Valid success:
                            {"is_relevant":"https://news-site.com/images/kathmandu-flood-01.jpg"}

                            Valid failure:
                            {"is_relevant": false}

                            --- FINAL NOTE ---
                            Do not append any other text. Do not include analysis, reasoning, or other metadata. If you cannot confidently pick a single image that strictly meets all rules, return {"is_relevant": false}.
                            """
                    },
                    
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Context: {query} \n\n Available image URL:\n: " + "\n".join([f"- {url}" for url in image_urls])
                            }
                        ]+[
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                            for image_url in image_urls
                        ]
                    }
                ],
                max_tokens=100,
                temperature=0
            )
            
            response_json = resp.choices[0].message.content.strip()
            response_data = self._safe_json_parse(response_json)
            
            if response_data and "is_relevant" in response_data:
                return response_data["is_relevant"]
            else:
                logger.error("Invalid response format from AI")
                return False
                
        except Exception as e:
            logger.error(f"Image verification failed: {e}")
            return False
            
        
        
        
        
        
    
    async def scrape_pages(self, query):
        """Scrape a page and extract main image"""
        logger.info(f"Starting scrape process for: '{query}'")
        urls = await self.select_url(query)
        
        if not urls:
            logger.error("No URL selected for scraping")
            return False
            
        
        
        # Use v1 scrape endpoint
        endpoints = "/v1/scrape"
        global flag 
        flag = False
        for url in self.potential_pages:
            payload = {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True
            }

            try:
                
                logger.info(f"Scraping URL: {url}")
                full_url = f"{self.base_url}{endpoints}"
                logger.info(f"Using endpoint: {endpoints}")
                
                async with self.session.post(full_url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            logger.info("Page scraped successfully")
                            
                            
                            metadata = data.get('data', {}).get('metadata',{})
                            if metadata.get('ogImage'):
                                self.image_urls.append(metadata.get('ogImage'))
                                flag = True
                                continue
                                
                                
                                                                                 

                        else:
                            logger.error(f"Scrape API error: {data.get('error')}")
                            continue
                    else:
                        logger.error(f"HTTP {response.status}")
                        continue
                        
            except Exception as e:
                logger.error(f"Scrape endpoint failed: {e}")
                continue
        return True if flag else False
    
                
                
                
                
                
    async def select_image(self, query):
        try:
            resp = await self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a perfect image selector. 
                        Select ONE image URL from the provided URLs that best fits the context.
                        Return strictly in JSON format: {"url": "chosen_url"}
                        You MUST choose ONLY from the provided URLs."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Context: {query}\n\nAvailable image URLs:\n" + "\n".join([f"- {url}" for url in self.image_urls])
                            }
                        ] + [
                            {
                                "type": "image_url",
                                "image_url": {"url": url}
                            }
                            for url in self.image_urls  
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0
            )
            
            image_json = resp.choices[0].message.content.strip()
            image_data = self._safe_json_parse(image_json)
            
            if image_data and "url" in image_data:
                selected_url = image_data["url"]
                
                # Validate URL is in our list
                if selected_url in self.image_urls:
                    return selected_url
                else:
                    logger.warning(f"AI returned invalid URL: {selected_url}")
                    
                    return None
                    
            else:
                logger.error("Invalid response format from AI")
                return None
                
        except Exception as e:
            logger.error(f"Image selection failed: {e}")
            return None
                


    # def _fallback_image_selection(self):
    #     """Fallback method when AI selection fails"""

    #     logger.info("Using fallback image selection")
    #     return self.image_urls[0] if self.image_urls else None
    
    
    
    

async def main():
    print("🚀 Starting Firecrawl Search Demo")
    async with FirecrawlSearch() as searcher:
        query = "Japan PM seeks meeting with North Korean leader over abductees"
        data = await searcher.search_for_sites(query)
        # img = await searcher.select_image(query)
        
        print(f"\n📋 FINAL RESULT: {data}")
        
        

if __name__ == "__main__":
    asyncio.run(main())