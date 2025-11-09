# from filter_newest_news import filter_last_24_hours,get_latest_timestamp
# from generator import failed_nepali_news,UseOpenai,PostToDB
# from embedding import add_news_to_clusters,clusters
# import asyncio
# import httpx
# from embedding import logger
# from imageGenerator import FirecrawlSearch


# # sources = ["routineofnepalbanda","indepthstory","24ghantanepal","nepalpolice","nepalitimes" ]

# sources = ["routineofnepalbanda","indepthstory","24ghantanepal","nepalpolice","nepalitimes"]
# todays_news = [] # [{"id":1,"caption":"news caption","timestamp":"2023-10-01T12:00:00+0000","media_url":"http://example.com/image.jpg","source":"source_name","title":"title","category":"category","detail":"detailed news in english"}]}]
# url_fragment = "{media{id,caption,timestamp,media_url}}"






# async def create_news():
#     use_ai = UseOpenai()
#     post = PostToDB()
#     global todays_news  
#     for account_index, account in enumerate(sources):
#         url = f"https://graph.facebook.com/v23.0/17841477428983090?fields=business_discovery.username({account}){url_fragment}&access_token=EAAJP3VRQ384BPYCgZBHxjl3CGWi5R7xnNVZAbmsxsxutIcdGA1tMp2GL4Wln1AdUsjZCDqj2AOeFKvZBaHUb9mkNYZAh0j60AsiNIVVFjNFgGqBdmr0RjJFV6D6Ozw9bBZBTEdzXAJfmZBgOZBIXsp2LRcZAXzPD2v9YpsdVg9JM342RENbvs5JVWeMhSFjAchaepqeAWHOeqtFVZC73xEZCY7ZBmdDrXIw5y4uSiiDhZAqrS"
    
#         #Fetching news
#         try:
#             timeout = httpx.Timeout(10.0,connect=5.0)
#             async with httpx.AsyncClient(timeout=timeout) as client:
#                 response = await client.get(url)
#                 response.raise_for_status()  # Raise an error for bad responses
                
        
#         except asyncio.TimeoutError as e:
#             logger.error(f"Timeout error for {account}: {e}")
#             continue  # Skip to the next account            
                
#         except httpx.HTTPStatusError as e:
#             logger.error(f"HTTP error {e.response.status_code} for {account}")
#             continue  # Skip to the next account
        
#         except httpx.RequestError as e:
#             logger.error(f"Request error for {account}: {e}")
#             continue  # Skip to the next account
        
#         except Exception as e:
#             logger.error(f"Unexpected error for {account}: {e}")
#             continue  # Skip to the next account
        
        
            
        
#         # Parse JSON response   
#         try:            
#             response = response.json()
#         except ValueError as e:
#             logger.error(f"Invalid JSON response for  {account}: {e}")
#             continue  # Skip to the next account
        
        
        
        
#         # Extracing news safely form response 
#         try:
#             business_discovery = response.get("business_discovery", {})
#             media_data = business_discovery.get("media", {})
#             news_items = media_data.get("data", [])

#             if not isinstance(news_items, list):
#                 logger.error(f"Unexpected data format for {account}: 'data' is not a list")
#                 news_items = []
#         except Exception as e:
#             logger.error(f"Error extracting news for {account}: {e}")
#             continue
        
        
#         # Filter news from last 24 hours and add source   
#         for news in list(news_items):
#             try:
#                 if not isinstance(news,dict):
#                     logger.warning(f"Skipping invalid news  for {account}")
#                     continue
#                 if "timestamp" not in news:
#                     logger.warning(f"News item missing timestamp for  {account}")
#                     continue
                
#                 if filter_last_24_hours(news["timestamp"]):
#                     # Create a copy to avoide modifying original data
#                     news_copy = news.copy()
#                     # Add field source to news
#                     news_copy["source"] = account
#                     # Append news to todays_news
#                     todays_news.append(news_copy)
                    
#                     logger.debug(f"Added news form {account}.")
#                 else:
#                     continue
#             except Exception as e:
#                 logger.error(f"Missing key in news item for {account}. Error: {e}")
#                 continue
            
        

                




#     #Send news to llm for filteration to get title and news in english
    
#     for news in list(todays_news):
#         # improve it by checking for caption,timestamp and media-url
#         if not "caption" in news:
#             todays_news.remove(news)
#             logger.error(f"No caption in {news}")
#             continue
#         if not news["caption"]:
#             todays_news.remove(news)
#             continue
            
#         # Generate title and translated news    
#         try:
#             title,english_news = await use_ai.generate_title(news["caption"])
#         except Exception as e:
#             todays_news.remove(news)
#             logger.error(f"Couldn't get title and translated news of {news}.")
#             continue
            
#         if not title or title == None:
#             todays_news.remove(news)
#             logger.error(f"No titile for {news}")
#             continue
            
            
#         if not english_news or english_news == None:
#             try:
#                 todays_news.remove(news)
#             except Exception as e:
#                 logger.error(f"The news has been already deleted. Error:{e}")
#             logger.error(f"News hasn't been converted to english for {news}")
#             continue
            
#         news["title"] = title
#         news["caption"] = english_news

        
#         logger.debug(f" Title and Caption(translated in englis ) added successfully for {news}")
        
                
    
#     # Cluster the news based on similarity 
#     for news in todays_news:
#         if "title" not in news:
#             logger.error(f"Expected keys (title) not found in API response for {news}")
#             continue
#         try:
#             await add_news_to_clusters(news["title"])
#         except Exception as e:
#             logger.error(f"{news} not added to the cluster.")
#             continue
#     logger.info(f"Total {len(clusters)} clusters formed from {len(todays_news)} news items.")

   

    
        


#     # Generate detailed news for each cluster and post to backend

#     context = "" # to accumulate details of news in same cluster
#     news_source = []
#     image_urls = []
#     date = []
#     for cluster_id, cluster in list(clusters.items()):
#         context = ""  # reset for each cluster
#         news_source = [] # reset for each cluster
#         date = [] # reset for each cluster
#         image_urls = [] # reset for each cluster
        
#         # Accumulate captions of all news in the cluster to form news detail for each cluster
#         for title in cluster["texts"]:
#             # Find news based on the titles in a cluster
#             matches = [d for d in todays_news if d.get("title") == title] 
#             # Form context by accumulating captions of all news in the cluster   
#             for news in matches:# matches are news form todays_news that belong to same clusters
#                 context += news.get("caption", "")
#                 if news.get("source") not in news_source:
#                     news_source.append(news.get("source", ""))
            
#                 date.append(news.get("timestamp",""))
#                 image_urls.append(news.get("media_url","")) # get image url from last news in the cluster
                
            
        
#         if not context:
#             logger.error(f"No context for cluster {cluster_id}")
#             continue
#         if not news_source:
#             logger.error(f"No source for cluster {cluster_id}")
#             continue
#         if not date:
#             logger.error(f"No date for cluster {cluster_id}")
#             continue
        
        

#         # Generate detailed news for the cluster using LLM       
#         try:
#             context = " ".join(context.split()) #Remove excessive whitespaces
#             news_detail = await use_ai.generate_news(context)
#         except Exception as e:
#             logger.error(f"Couldn't generate detailed news for cluster {cluster_id}: {e}")
#             continue
#         if news_detail["category"] == None or news_detail["title"]  == None or news_detail["detail"] == None or not isinstance(news_detail, dict):
#             clusters.pop(cluster_id, None)  
#             continue

#         # Add source, cluster id, and timestamp to the news cart
#         news_detail["source"] = news_source
#         news_detail["timestamp"] = get_latest_timestamp(date)
#         news_detail["cluster_id"] = cluster_id
        
        
        
        
#         # Image processing
        
#         result = image_urls[-1]
#         async with FirecrawlSearch() as searcher:
#             query = news_detail["image_search"]
#             is_acceptable = await searcher.check_image_for_news(image_urls,query)
            
#             if not is_acceptable:                
#                 logger.info(f"Image search using {query}")
#                 success = await searcher.scrape_pages(query)
#                 if success :
#                     logger.info(f"Selected images URLs: {searcher.image_urls}")
#                     result = await searcher.select_image(query)
#                     if not result:
#                         logger.info("No suitable image selected by AI")
#                         result = image_urls[-1]
#                     else:
#                         logger.info(f"Best fit image by scrapping is : {result}")
#                 else:
#                     logger.info(f"Using original image URL: {image_urls[-1]}")

            
#             else :
#                 result = is_acceptable
#                 logger.info(f"Using original image URL:{result}")

        
        
        
        
        
        
            
           
        
        
        
        
        
#         # Convert news informations to news cart to post to backend
#         try:
#             english_news_cart = {
#             "id":str(cluster_id),
#             "title":news_detail["title"],
#             "cover_image":result if result else "",
#             "category":news_detail["category"],
#             "detail":news_detail["detail"],
#             "source":news_detail["source"],
#             "time_of_release":news_detail["timestamp"]
#             }
            
#             get_nepali_news = await use_ai.convert_to_nepali({"title":news_detail["title"],"descrition":news_detail["detail"]})
#             nepali_news_cart = {
#                 "title":get_nepali_news["title"],
#                 "description":get_nepali_news["description"],
#                 "cart_id":str(cluster_id) 

#                 }
#         except Exception as e:
#                 logger.error(f"couldn't access translated news.")
#                 continue
            
                
#         except KeyError as e:
#             logger.error(f"Missing expected key {e} in news_detail for cluster {cluster_id}")
#             continue
        
#         try:
#             response = await post.Post_to_db(english_news_cart,"http://127.0.0.1:8000/create-cart/english/","http://127.0.0.1:8000/create-detail/english/")
#             logger.info(f"News with culuster id :{cluster_id} successfully stored in the backend.")
#         except Exception as e:
#             logger.error(f"Failed to post news for cluster {cluster_id} to backend: {e}")
#             continue
#         # post nepali news
#         try:
#             res = await post.Post_nepali_news(nepali_news_cart,"http://127.0.0.1:8000/create-details/nepali/")
#             logger.info(f"News with culuster id :{cluster_id} successfully stored in the backend.")
#         except Exception as e:
#             logger.error(f"Failed to post news for cluster {cluster_id} to backend: {e}")
#             continue

#     limit = 0    
#     if failed_nepali_news and cluster:
        
#         while len(failed_nepali_news) != 0:
#             if limit > 3:
#                 break
#             # Create a copy of the dictionary items for iteration
#             for i in list(failed_nepali_news):
#                 try:
#                     res = await post.Post_nepali_news(i, "http://127.0.0.1:8000/create-details/nepali/")
#                     if res.status_code not in (200, 201):
#                         logger.error(f"Once again failed to post news for cluster {cluster_id} to backend: {e}")
#                         continue
#                     logger.info(f"News with cluster id :{i['cart_id']} successfully stored in the backend this time.")
#                     failed_nepali_news.remove(i)  # Fixed variable name from 'news' to 'i'
#                 except Exception as e:
#                     logger.error(f"Once again failed to post news for cluster {cluster_id} to backend: {e}")
            
#             limit += 1
            
        
        



# # asyncio.run(create_news())
    
    

