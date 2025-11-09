import aiohttp
from openai import AsyncOpenAI
from typing import Optional
import httpx
import asyncio
from dotenv import load_dotenv
import json 
import re
from embedding import logger
import os

load_dotenv()


failed_nepali_news = []



nepali_news = """
You are a professional Nepali news translator specialized in translating English news content into fluent, natural, and contextually accurate Nepali.

---

### Objective
Translate the provided English news content into **high-quality, reader-friendly Nepali** while preserving all facts, tone, and intent.  
Your translation should read naturally for Nepali audiences, as if originally written in Nepali journalism style.

---

### Input Format
You will always receive input in this exact JSON structure:
{
  "title": "English title text",
  "description": "English description text"
}

---

### Translation Guidelines
1. **Faithfulness & Fluency**
   - Translate meaning accurately — do not add, remove, or alter any information.
   - Use smooth, grammatically correct Nepali that feels natural in news writing.
   - Avoid awkward literal translation or word-by-word rendering.

2. **Language Balance**
   - Keep terms in **English** if they are:
   - Commonly used or more natural in English (e.g., “AI”, “startup”, “budget”, “Prime Minister”, “COVID-19”, “Facebook”).
   - Brand names, organizations, or global references.
   - Keep terms in **Nepali** if they sound more natural in Nepali context (e.g., “सरकार”, “अर्थतन्त्र”, “विद्यालय”, “स्वास्थ्य”, “खेलकुद”).
   - Strive for **bilingual readability** that reflects how Nepali media writes in practice.

3. **Style and Tone**
   - Maintain a formal yet natural tone appropriate for professional news.
   - Avoid idioms or slang unless commonly used in Nepali journalism.
   - Do not summarize or interpret; translate the full factual content.
   - Keep proper nouns, numbers, URLs, and dates exactly as-is.

4. **Length and Completeness**
   - Ensure the **description** contains all original details (no omissions).
   - Expand slightly if needed to maintain clarity, but never invent new facts.

---

### Output Format
Return the translation in **valid JSON** with the same structure:
{
  "title": "Nepali translation of title",
  "description": "Nepali translation of description"
}

---

### Output Constraints
- Return **only** the JSON object — no extra text, Markdown, or explanation.
- Ensure **valid JSON syntax** and proper encoding (UTF-8).
- If input is missing or invalid, return:
{
  "title": "null",
  "description": "null"
}


"""

get_details_from_cluster  = """
You are an expert news synthesis model trained to transform multiple unstructured news inputs into a single, factual, and well-written article with precise source citations.
---
####  Objective

Your task is to **analyze, consolidate, and rewrite** multiple pieces of raw news content from different sources into a **clean, coherent, and factual** English article.  
Every statement in your article must be supported by its corresponding source, cited in the style of `[1]`, `[2]`, etc.

---

---

### Step-by-Step Instructions

**1. Understand the Input**
- The input is a raw news text (in any language).  
- If it is not in English, translate it into *fluent, clear, and neutral English* while preserving the original meaning.  
- Never summarize or interpret beyond what is explicitly stated.

**2. Title Creation**
- Generate a short, factual, and engaging title that accurately reflects the content.  
- Avoid sensationalism, opinions, or any information not supported by the input.  

**3. Detail Rewriting**
  - The unified, readable news piece written in journalistic style, using numeric citations like `[1]`, `[2]`, etc.  
  - Each claim, figure, or piece of information must include a citation.  
  - When multiple sources support the same detail, cite them together like `[1][3]`.  
  - Citations should appear at the end of the sentence or clause they support. 
  - Writing Rules:

i.**Factual Integrity**
   - Never invent, assume, or infer information beyond what is verifiably stated in the inputs.  
   - Do not merge conflicting facts; instead, represent them as differing reports with clear attribution.  
   - Exclude filler, speculation, and emotional phrasing.  

ii. **Synthesis Logic**
   - Identify overlapping facts across sources and combine them into one clear statement.  
   - Prefer consensus details over isolated claims.  
   - Maintain chronological and logical flow of events. 
iii.**Style & Tone**
   - Neutral, formal, and journalistic.  
   - Short paragraphs for readability.  
   - Avoid redundant phrasing, clichés, or commentary. 
   
   
4. **Citation **
   - When you have created the details of news article and provided numbering of citation, this is the field that you will mapping the citation numbers.
   - It is a  numbered list that maps every citation number used in the article to its corresponding source.
    Each source must appear exactly once, in the order it first appears in the article.
    Do not include duplicate entries or sources that were not cited.
    Each list item should contain either the source’s URL or its name (if no URL is available).
    This field ensures traceability of every factual statement back to its verified origin.
   - Always include at least one citation per factual statement.  
   - Maintain compact citation placement: `[1]` immediately follows the supported fact.  
   - If a paragraph uses multiple sources, cite each as appropriate. 

**5. Image Searching Text**
A short, factual, and visually descriptive summary of the news, written to help another language model select the most contextually accurate and relevant image.
It should clearly describe the key visual elements or scene that best represent the news (e.g., people, places, objects, or events involved), without adding opinions or speculation.
Focus on what should be visible in the ideal image — not on abstract ideas or background details.

Example:
If the news is about an earthquake in Tokyo, the text might be:

“Collapsed buildings and emergency responders in Tokyo streets after an earthquake.”

**4. Categorization**
- Assign the article to one of the following predefined categories only:
  ```
  ["Politics", "Business", "Technology", "Science", "Health", 
   "Entertainment", "Sports", "World", "National", "Environment", 
   "Education", "Economy", "Travel", "Crime", "Weather"]
  ```
- If the article clearly does not fit any of these categories, return `"category": None`.
- If the content appears trivial, opinionated, or lacks factual relevance, or is just like opinion,greetings,etc, return `"title": None`, `"category": None`, and `"english_news": None`.

**5. Output Format**
- Return a single valid JSON object with this exact structure:
  ```json
  {
    "title": "..."
    "detail": "...",
    "category": "..."
    "image_search":"..."
    "citations": ["..","..", ... ]
  }
  ```
- Do **not** include explanations, comments, Markdown, or text outside the JSON.  
- Ensure that the JSON is valid, machine-readable, and contains only the keys above.

---

### Example

**Input:**
> नेपाल सरकारले नयाँ आर्थिक नीतिहरू घोषणा गरेको छ जसमा उद्योग र रोजगारीमा सुधार ल्याउने योजना समावेश गरिएको छ।

**Output:**
```json
{
  "title": "Government Announces New Economic Policies to Boost Industry and Employment",
  "detail": "The Government of Nepal has announced new economic policies that include plans to improve industry and employment opportunities.",
  "category": "Economy"
  "image_search":"Government of Nepal"
  "citations": [
    "https://www.reuters.com/article123",
    "BBC News",
    "CNN"
  ]
  
}
```

---

### Critical Rules
- Always ensure valid JSON syntax.  
- If uncertain about any part of the content, translate literally without assumption.  
- If any field cannot be determined, set its value to `"null"` (as a string).  
- Never fabricate facts, names, or data beyond the given text.



"""



convert_news_to_english = """
You are a specialized assistant responsible for processing and classifying news articles.  
Your output must be accurate, concise, and strictly follow the required format.  
Do not generate, infer, or assume information that is not present in the input.  

---

### Step-by-Step Instructions
**1. Evaluating news
- Check if it is really some news or a normal idea,opinion,thought,advertisement etc then just return `"title":None` and `"english_news":None`
- If the content appears trivial, opinionated, or lacks factual relevance, or is just like opinion,greetings,advertisement of any sort, etc, return `"title": None` and `"english_news": None`.
- Make sure you return `"title": None` and `"english_news": None` for any sort of marketing and advertisement

**2.Language Balance**
- Keep terms in **English** if they are:
- Commonly used or more natural in English (e.g., “AI”, “startup”, “budget”, “Prime Minister”, “COVID-19”, “Facebook”).
- Brand names, organizations, or global references.
- Keep terms in **Nepali** if they sound more natural in Nepali context (e.g., “सरकार”, “अर्थतन्त्र”, “विद्यालय”, “स्वास्थ्य”, “खेलकुद”).
- Strive for **bilingual readability** that reflects how Nepali media writes in practice.
- If it is already in English, keep it unchanged.

**3. Title Generation**
- Read the content carefully and create a *concise, factual, and engaging* title in English.
- The title must accurately reflect the article content and avoid exaggeration or interpretation.

**4. Output Format**
- The output must be a single valid JSON object with the following structure:
  ```json
  {
    "title": "...",
    "english_news": "..."
  }
  ```
- Do not include any explanations, comments, or extra text outside the JSON.

**5. Output Validation Rules**
- Always ensure the JSON is syntactically correct and parsable.
- Keys must remain exactly as specified.
- Values should be strings or `null` only — no nested objects, arrays, or additional fields.

---

### Example

**Input:**
> सरकारले नयाँ बजेट पेश गरेको छ जसमा शिक्षामा खर्च वृद्धि गरिएको छ।

**Output:**
```json
{
  "title": "Government Announces New Budget with Increased Education Spending",
  "english_news": "The government has presented a new budget that includes increased spending on education."
}
```

---

**Critical Rule:** If uncertain about translation accuracy, category, or relevance — return `None` values instead of guessing.


"""


class UseOpenai:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),  # or your actual API key
            base_url=os.getenv("BASE_URL"),   # or your actual endpoint
            default_query={"api-version": "2024-04-01-preview"},

        )
    
    async def get_query(self,context):
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role":"system","content":"""You are an expert news analyst specialized in generating concise and descriptive search queries for finding relevant news artilcles and images associated with the given news content. The query should be brief, hightly descriptive, and extremely explainatory enough for search engines. The response should strictly be in in this format {"search_query": "..."} without any extra text or explanation."""},
                    {"role":"user","content":f"Based on this context '{context}', generate a concise and descriptive search query for finding relevant news and images associated to them. "}
                ],
                temperature=0
            )
            logger.info(f"Query generation was successfull.")
        except asyncio.CancelledError as e:
            logger.error(f"Query generation was cancled: {e}")
        except asyncio.TimeoutError as e:
            logger.error(f"Query generation timeout : {e}")
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
        
        try:
            query = resp.choices[0].message.content
            logger.info(f"Generated search query: {query}")
        except (AttributeError, IndexError) as e:
            logger.error(f"Unexpected AI response structure during query generation: {e}")
            return None
        
        try:
            data_json = json.loads(query)
        except json.JSONDecoderError:
            match = re.search(r"\{.*\}", query, re.DOTALL)
            if match:
                data_json = json.loads(match.group())
            else:
                logger.error("No valid JSON found in AI response during query generation.")
                return None
        if "search_query" not in data_json:
            logger.error("Missing  'search_query' field in Ai response during Query generation.")
            return None
        return data_json["search_query"]
        
            

    async def generate_title(self,news):
        """
        Generate title, category, and English translation for news using Azure OpenAI
        """
        try:
            logger.info("Generating title and category via AI")

            # Step 1: Generate full news via Azure OpenAI async client
            resp = await self.client.chat.completions.create(
                model="gpt-4.1",  # Use your Azure deployment name
                messages=[
                    {"role": "system", "content": convert_news_to_english},
                    {"role": "user", "content": news},
                ],
                timeout=30.0  # Add timeout to prevent hanging
            )
            logger.info("AI response received successfully")

        except asyncio.CancelledError:
            logger.error("AI request was cancelled")
            
        except asyncio.TimeoutError:
            logger.error("AI request timed out")
            
        except Exception as e:
            logger.error(f"AI request failed: {e}")
            

        # Extract content
        try:
            content_str = resp.choices[0].message.content
            logger.info(f"AI response content: {content_str}")
            
        except (AttributeError, IndexError) as e:
            logger.error(f"Unexpected AI response structure: {e}")
            

        # Parse JSON safely with multiple fallback strategies
        data = None
        try:
            # First attempt: direct JSON parse
            data = json.loads(content_str)
            logger.info("JSON parsed successfully on first attempt")
        except json.JSONDecodeError as e:
            logger.error(f"Initial JSON parse failed: {e}")
            
            # Second attempt: Clean common JSON issues
            cleaned_content = content_str.strip()
            
            # Fix common JSON issues
            cleaned_content = cleaned_content.replace("'", '"')  # Single to double quotes
            cleaned_content = re.sub(r',\s*}', '}', cleaned_content)  # Remove trailing commas
            cleaned_content = re.sub(r',\s*]', ']', cleaned_content)  # Remove trailing commas in arrays
            
            try:
                data = json.loads(cleaned_content)
                logger.info("JSON parsed successfully after cleaning")
            except json.JSONDecodeError:
                logger.error("Cleaned JSON parse failed")
                
                # Third attempt: Extract JSON object with regex
                match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_content, re.DOTALL)
                if match:
                    try:
                        json_str = match.group()
                        # Final cleanup before parse
                        json_str = json_str.replace("'", '"')
                        json_str = re.sub(r'(\w+)\s*:', r'"\1":', json_str)  # Ensure quoted keys
                        data = json.loads(json_str)
                        logger.info("JSON parsed successfully after regex extraction")
                    except json.JSONDecodeError as e:
                        logger.error(f"Regex-extracted JSON parse failed: {e}")
                        
                else:
                    logger.error("No JSON object found in AI response")
                    

        # Validate expected fields
        required_fields = ["title",  "english_news"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.error(f"Missing fields in AI response: {', '.join(missing_fields)}")
            

        # Access fields with validation
        try:
            title = str(data["title"]).strip()
            detail = str(data["english_news"]).strip()   
                    
            logger.info(f"Generated title: {title}")
            
        except (KeyError, TypeError) as e:
            print(f" Error accessing response fields: {e}")
            raise ValueError(f"Error accessing response fields: {e}")

        return title, detail








    async def generate_news(self,data):
      #Generate news via AI
        try:
            resp = await  self.client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[
                        {"role": "system", "content": get_details_from_cluster},
                        {"role": "user", "content": data},
                    ],
                    timeout=60.0  # Add timeout to prevent hanging
                )
            
        except Exception as e:
            raise RuntimeError(f"AI request failed during generation of  detailed news: {e}") from e

        # Extract content string safely
        try:
            content_str = resp.choices[0].message.content
        except (AttributeError, IndexError) as e:
            raise ValueError(f"Unexpected AI response structure during generation of detailed news.: {e}")
        


        # Parse JSON safely
        try:
            data_json = json.loads(content_str)
        except json.JSONDecodeError:
            # fallback: extract JSON using regex if AI added extra text
            match = re.search(r"\{.*\}", content_str, re.DOTALL)
            if match:
                data_json = json.loads(match.group())
            else:
                raise ValueError("No valid JSON found in AI response during generation of detailed news.")

        # Validate required fields
        required_fields = ["title", "category", "detail","image_search","citations"]
        for field in required_fields:
            if field not in data_json:
                raise ValueError(f"Missing field '{field}' in AI response")

        # Build news cart
        news_cart = {
            "title": data_json["title"],
            "category": data_json["category"],
            "detail": data_json["detail"],
            "image_search":data_json["image_search"],
            "citations":data_json["citations"]

        }

        return news_cart
    
    
    async def convert_to_nepali(self,news):
        """
        Convert news to Nepali using Azure OpenAI
        """
        try:
            logger.info("Translating news to Nepali via AI")

            # Step 1: Generate full news via Azure OpenAI async client
            resp = await self.client.chat.completions.create(
                model="gpt-4.1",  # Use your Azure deployment name
                messages=[
                    {"role": "system", "content":nepali_news},
                    {"role": "user", "content": f"Translate the following news to Nepali:\n\n{news}"},
                ],
                timeout=30.0  # Add timeout to prevent hanging
            )
            logger.info("AI translation response received successfully")

        except asyncio.CancelledError:
            logger.error("AI translation request was cancelled")
            
        except asyncio.TimeoutError:
            logger.error("AI translation request timed out")
            
        except Exception as e:
            logger.error(f"AI translation request failed: {e}")
            return None

        # Extract translated content
        try:
            translated_json = resp.choices[0].message.content.strip()
            logger.info(f"Translated text: {translated_json}")

            
            
        except (AttributeError, IndexError) as e:
            logger.error(f"Unexpected AI translation response structure: {e}")
            return None
        
        try:
            data_json = json.loads(translated_json)
        except json.JSONDecodeError:
            # fallback: extract JSON using regex if AI added extra text
            match = re.search(r"\{.*\}", translated_json, re.DOTALL)
            if match:
                data_json = json.loads(match.group())
            else:
                raise ValueError("No valid JSON found in AI response during generation of detailed news.")

        # Validate required fields
        required_fields = ["title", "description"]
        for field in required_fields:
            if field not in data_json:
                raise ValueError(f"Missing field '{field}' in AI response")
        
        news_detail = {
            "title": data_json["title"],
            "description": data_json["description"],

        }
        return news_detail
    
    
    async def select_image(self):
        
        
        try:
            resp = await  self.client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[
                        {"role": "system", "content": get_details_from_cluster},
                        
                    ],
                    timeout=60.0  # Add timeout to prevent hanging
                )
            
        except Exception as e:
            raise RuntimeError(f"AI request failed during generation of  detailed news: {e}") from e

        # Extract content string safely
        try:
            content_str = resp.choices[0].message.content
        except (AttributeError, IndexError) as e:
            raise ValueError(f"Unexpected AI response structure during generation of detailed news.: {e}")
        


        # Parse JSON safely
        try:
            data_json = json.loads(content_str)
        except json.JSONDecodeError:
            # fallback: extract JSON using regex if AI added extra text
            match = re.search(r"\{.*\}", content_str, re.DOTALL)
            if match:
                data_json = json.loads(match.group())
            else:
                raise ValueError("No valid JSON found in AI response during website selection .")

        



        
        
    

    

class PostToDB:
    def __init__(self):
        pass


    async def Post_to_db(self,news_cart1, create_cart_url, create_detail_url):
        news_cart = {
        "id":news_cart1["id"],
        "title":news_cart1["title"],
        "cover_image":news_cart1["cover_image"],
        "category":news_cart1["category"],
        "source":news_cart1["source"],
        "time_of_release":news_cart1["time_of_release"]
        }
        
        async with httpx.AsyncClient() as client_http:
            # Create basic news
            response_basic = await client_http.post(create_cart_url, json=news_cart)
            print("Basic API Response:", response_basic.status_code, response_basic.text)

            if response_basic.status_code not in (200, 201):
                raise Exception(f"Failed to POST basic news. Status: {response_basic.status_code}, Body: {response_basic.text}")

            try:
                basic_id = response_basic.json().get("id")
            except Exception as e:
                raise Exception(f"Invalid JSON in basic response: {e}, Body: {response_basic.text}")

            if not basic_id:
                raise Exception("Backend did not return an 'id' for the basic news")

            # Construct schema for NewsInDetail table
            detail_news = {
                "description":news_cart1["detail"],  # double-check if backend expects "id" or "news_id"
                "cart_id": basic_id 
            }

            response_detail = await client_http.post(create_detail_url, json=detail_news)

            if response_detail.status_code not in (200, 201):
                raise Exception(f"Failed to POST detail news. Status: {response_detail.status_code}, Body: {response_detail.text}")

            return response_detail.json()      

    
    async def Post_nepali_news(self,news,receiverUrl ):
        

        async with httpx.AsyncClient() as client_http:
        # Create basic news
            response_basic = await client_http.post(receiverUrl, json=news)
            logger.debug(f"Basic API Response: {response_basic.status_code}")

            if response_basic.status_code not in (200, 201):
                failed_nepali_news.append(news)
                logger.error(f"Failed to POST basic news. Status: {response_basic.status_code}, Body: {response_basic.text}")
    
    
    
    