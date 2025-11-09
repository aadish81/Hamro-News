# from tavily import TavilyClient



# tavily_client = TavilyClient(api_key="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")
# response = tavily_client.search(f"find image for the title 'Nepal to Bat First in Match Against Qatar'")

# print(response)






# from serpapi import GoogleSearch

# params = {
#   "engine": "google_images",
#   "q": "Election Commission seeks additional documents from 3 new political parties including Harka Sampang’s",
#   "api_key": "65a973c1c257e24706817061d5775b864a77aa17442972d222a3fe2a7bc3a61a"
# }

# search = GoogleSearch(params)
# results = search.get_dict()

# print(results)









# from openai import AsyncOpenAI
# import os
# from dotenv import load_dotenv
# import asyncio

# load_dotenv()

# client = AsyncOpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),  # or your actual API key
#     base_url=os.getenv("BASE_URL"),   # or your actual endpoint
#     default_query={"api-version": "2024-04-01-preview"},

# )

# async def generate():
  
#   resp = await client.images.generate(
#     model = "gpt-image-1",
#     prompt = "A scenic view of the Himalayas during sunrise with vibrant colors and clear skies.",
#     size="1024x1024"
#   )
#   print("result:",resp)
#   print(f"Generated image URL: {resp.data[0].url}")
  # except Exception as e:
  #   print(f"Error occured : {e}")
# asyncio.run(generate())
    
# async def describe():
#   resp = await client.chat.completions.create(
#   model="gpt-4.1",  # Use your Azure deployment name
#     messages=[
#     {"role": "system", "content": "You are a image describer. You will get image that you need to describe it in terms of what is it? what is its content etc."},
#       {"role": "user", "content":[
#         {"type":"image_url","image_url":{"url":"https://scontent.cdninstagram.com/v/t51.82787-15/562865905_18389254576135775_3349645420942216506_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=1&ccb=1-7&_nc_sid=18de74&efg=eyJlZmdfdGFnIjoiRkVFRC5iZXN0X2ltYWdlX3VybGdlbi5DMyJ9&_nc_ohc=vEueW4pEGKYQ7kNvwEN5gKd&_nc_oc=Adm7eZYmMf1jLpkN3NibD5qgnuIVxjcdsXi8f5k8_5ZjTJrJSlIFjIjQM-C5Ua9UauRMRceAtMv79IqevzBE72q1&_nc_zt=23&_nc_ht=scontent.cdninstagram.com&edm=AL-3X8kEAAAA&_nc_gid=K8LSO68HTstiVahopXS06g&oh=00_AfeKQtZUeKcBfdpVbr67FXkoo7QEr7lpXcvsO41UYkHzOA&oe=68F30334"}}
#         ]} 
#     ],
#     timeout=30.0  # Add timeout to prevent hanging
#     )
  
#   try:
#     content_str = resp.choices[0].message.content
#     print(f"AI response content: {content_str}")
        
#   except (AttributeError, IndexError) as e:
#         print(f"Unexpected AI response structure: {e}")

# asyncio.run(describe())

# "Select  me a best fit  image for the context: {query} \n From the following image urls, choose the best one that fits the context. If none fits, return a random one."
# "Your job is to find the most relevent image for given context you receive. Return strictly in json format. For example {\"url\":\"chosen image url\"}
# from openai import AsyncOpenAI
# import os
# from dotenv import load_dotenv
# import asyncio

# load_dotenv()

# client = AsyncOpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),  # or your actual API key
#     base_url=os.getenv("BASE_URL"),   # or your actual endpoint
#     default_query={"api-version": "2024-04-01-preview"},

# )
# img_urls = ["https://english.onlinekhabar.com/wp-content/uploads/2025/10/aftab-aalam-news-2.jpg","https://english.onlinekhabar.com/wp-content/uploads/2025/07/suradeach-saetang-jrA2l3JjD5k-unsplash.jpg","https://english.onlinekhabar.com/wp-content/uploads/2023/02/Hydropower-projects-in-Nepal-8.jpg"]
# query = "Gold price reached $80,000 in Nepal amid global market fluctuations."
# async def describe():
#   resp = await client.chat.completions.create(
#   model="gpt-4.1",  # Use your Azure deployment name
#     messages=[
#     {"role": "system", "content": "You select the url of an image that you receive which best fits the given description."},
#       {"role": "user", "content":[
#         {"type":"text","text":f"From these image urls https://english.onlinekhabar.com/wp-content/uploads/2025/10/aftab-aalam-news-2.jpg ,https://english.onlinekhabar.com/wp-content/uploads/2025/07/suradeach-saetang-jrA2l3JjD5k-unsplash.jpg,https://english.onlinekhabar.com/wp-content/uploads/2023/02/Hydropower-projects-in-Nepal-8.jpg. Return me the best fit image for the context: {query} in json format strictly."},
#                                   ]+[
#                                     {"type":"image_url","image_url":{"url":img_url} } for img_url in img_urls
#                                   ]
#        } 
#     ],
#     timeout=30.0  # Add timeout to prevent hanging
#     )
  
#   try:
#     content_str = resp.choices[0].message.content
#     print(f"AI response content: {content_str}")
        
#   except (AttributeError, IndexError) as e:
#         print(f"Unexpected AI response structure: {e}")

# asyncio.run(describe())