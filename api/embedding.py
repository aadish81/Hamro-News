import cohere
import uuid
import random
import asyncio
import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
import json 
import logging 
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger('fetch_news')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler) 

# Initialize Cohere client
co = cohere.Client(os.getenv("COHERE_API_KEY2"))

clusters = {}  # {cluster_id: { "texts": [], "mean_embedding": array, "count": int, "delete":bool}}

SIMILARITY_THRESHOLD = 0.65





async def get_embeddings(texts):
    """Get embeddings from Cohere API with robust error handling"""
    # Ensure texts is a list         
    if not isinstance(texts, str):
        logger.error("Input to get_embeddings must be a string or list of strings")
        
    texts = [texts]
        
    await asyncio.sleep(random.uniform(2,4))  # Simulate network delay
    try:
       
     
        
        # Simple Cohere API call with timeout
        response = co.embed(
            model="embed-english-v2.0",
            texts=texts
        )
        
        # Check if response has embeddings
        if hasattr(response, 'embeddings') and response.embeddings:
            embeddings = [np.array(emb) for emb in response.embeddings]
            return embeddings[0] if len(embeddings) == 1 else embeddings
        else:
            logger.error("No embeddings found in Cohere response")
            return _get_fallback_embedding(texts)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return _get_fallback_embedding(texts)

        
    except Exception as e:
        logger.error(f"Error fetching embeddings: {e}")
        return _get_fallback_embedding(texts)
    
    
    
    
    
    
    

def _get_fallback_embedding(texts):
    """Return fallback embeddings when API fails"""
    logger.info("Using fallback embeddings")
    if isinstance(texts, list):
        return [np.zeros(4096) for _ in texts]
    return np.zeros(4096)

# def calculate_cosine_similarity(vec1, vec2):
#     """Calculate cosine similarity between two vectors"""
#     try:
#         # Ensure both are numpy arrays
#         vec1 = np.array(vec1)
#         vec2 = np.array(vec2)
        
#         # Check if vectors have same dimension
#         if vec1.shape != vec2.shape:
#             logger.error("Vectors have different dimensions")
#             return 0.0
            
#         # Reshape for sklearn cosine_similarity
#         vec1_2d = vec1.reshape(1, -1)
#         vec2_2d = vec2.reshape(1, -1)
        
#         similarity = cosine_similarity(vec1_2d, vec2_2d)[0][0]
#         return float(similarity)
        
#     except Exception as e:
#         logger.error(f"Error calculating cosine similarity: {e}")
#         return 0.0




def calculate_cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors - pure numpy version"""
    try:
        # Ensure both are numpy arrays
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # Check if vectors have same dimension
        if vec1.shape != vec2.shape:
            logger.error("Vectors have different dimensions")
            return 0.0
        
        # Calculate dot product
        dot_product = np.dot(vec1, vec2)
        
        # Calculate magnitudes
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure value is within valid range (floating point precision)
        similarity = max(-1.0, min(1.0, similarity))
        
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0








async def add_news_to_clusters(news_text):
    global clusters
        
    # Step 1: Embed the new news using Cohere
    embedding = await get_embeddings(news_text)
    
    # If no clusters exist, create first one
    if not clusters:
        cluster_id = str(uuid.uuid4())
        clusters[cluster_id] = {
            "texts": [news_text],
            "mean_embedding": embedding.copy(),
            "count": 1,
            "delete": False
        }

        return cluster_id, 0.0
    
    # Step 2: Find the best matching cluster
    best_cluster_id, best_score = None, 0
    for cluster_id, data in clusters.items():
        try:
            similarity = calculate_cosine_similarity(embedding, data["mean_embedding"])

            
            if similarity > best_score:
                best_score = similarity
                best_cluster_id = cluster_id
        except Exception as e:
            logger.error(f"Error comparing with cluster {cluster_id}: {e}")
            continue
    
    # Step 3: Assign to cluster or create new
    if best_score >= SIMILARITY_THRESHOLD and best_cluster_id:
        # Update mean embedding (moving average)
        n = data["count"]
        data["mean_embedding"] = (data["mean_embedding"] * n + embedding) / (n + 1)

        data["texts"].append(news_text)
        data["count"] += 1
        

    else:
        # Create new cluster
        cluster_id = str(uuid.uuid4())
        clusters[cluster_id] = {
            
            "texts": [news_text],
            "mean_embedding": embedding.copy(),
            "count": 1,
            "delete": False
        }

    

    