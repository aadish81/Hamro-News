
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import delete
import datetime
from api.scheduler import scheduler
from api.Database.database import Base,engine,get_db
from api.Models.models import NewsCart, NewsInDetail,NewsInNepali
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from api.schema import NewsCartCreate,NewsCartRead,DetailCreate,DetailRead,CreateNewsInNepali

from sqlalchemy.orm import  selectinload
import json
from pydantic import HttpUrl


import logging




# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





async def create_tables():
    print("Creating tables in:", engine.url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created")


@asynccontextmanager 
async def lifespan(app:FastAPI):
    try:
        scheduler.start()
        # print("Scheduler disabled for debugging")
    except Exception as e:
        print(f"Scheduler error: {e}")
    try:
        await create_tables()
    except Exception as e:
        logger.error(f"Error while creatig tables: {e}")
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)





app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    logger.info("Everything is workig fine.")
    return {"message": "API is running"}

@app.get("/health")
async def health_check():
    """Simple health check without database"""
    return {
        "status": "healthy", 
        "service": "running",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }


@app.post("/create-cart/english/")
async def create_resource(new_cart: NewsCartCreate, db: AsyncSession = Depends(get_db)):
    try:
        # check if resource exists
        
        existing_news = await db.execute(select(NewsCart).where(NewsCart.id == new_cart.id))
        exists = existing_news.scalars().first()
        # If exists delete the existing row and create a new one (for updating the existing news)
        if exists:
            await db.delete(exists)
            await db.commit()
            
            
        new_resource = NewsCart(
            id = str(new_cart.id),  
            title=new_cart.title,
            cover_image=str(new_cart.cover_image),
            source=json.dumps(new_cart.source),
            category=new_cart.category,
            time_of_release=new_cart.time_of_release
        )
        db.add(new_resource)
        await db.commit()
        await db.refresh(new_resource)
        
        # Return the primary key (id)
        return {"id": new_resource.id}
    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Error creating resource: {e}")



@app.get("/news-carts/english/", response_model=list[NewsCartRead], operation_id="get news")
async def get_resources(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(NewsCart))
        carts = result.scalars().all()  
        if not carts:
            raise HTTPException(status_code=404, detail="No resources available")

        # convert string field in resource to python list
        for i in carts:
            i.source = json.loads(i.source)  # convert string to list
            i.cover_image = HttpUrl(i.cover_image)  # convert string to HttpUrl
            
            

        return carts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resources: {e}")





@app.post("/create-detail/english/")
async def create_detail(detail: DetailCreate, db: AsyncSession = Depends(get_db)):
    try:
        # check if resource exists
        result = await db.execute(select(NewsCart).options(selectinload(NewsCart.detail)).where(NewsCart.id == detail.cart_id))
        resource = result.scalars().first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # check if resource already has a detail, if exist update the detail
        
        # if resource.detail is not None:
        #     raise HTTPException(status_code=400, detail="Resource already has a detail")

        new_detail = NewsInDetail(
            description = detail.description,
            cart_id = detail.cart_id 
        )
        db.add(new_detail)
        await db.commit()
        await db.refresh(new_detail)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating detail: {e}")





@app.get("/details/english/", response_model=list[DetailRead])
async def get_details_english(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsInDetail))
    details = result.scalars().all()
    if not details:
        raise HTTPException(status_code=404, detail="No details available")

        # convert string field in resource to python list
    # for i in details:
    #     if i.cart is not None:
    #         i.cart.source = json.loads(i.cart.source)  
          
    #         i.cart.cover_image = HttpUrl(i.cart.cover_image)  # convert string to HttpUrl



    return details

@app.post("/create-details/nepali/")
async def create_or_update_news_in_nepali(news: CreateNewsInNepali, db: AsyncSession = Depends(get_db)):
    try:
        # First, check if NewsInNepali already exists with this ID
        result = await db.execute(
            select(NewsInNepali).where(NewsInNepali.cart_id == news.cart_id)
        )
        existing_news = result.scalars().first()

        if existing_news:
            # UPDATE existing record
            existing_news.title = news.title
            existing_news.description = news.description
            existing_news.cart_id = news.cart_id
            message = "News in Nepali updated successfully"
        else:
            # CREATE new record
            new_news_in_nepali = NewsInNepali(
                title=news.title,
                description=news.description,
                cart_id=news.cart_id
            )
            db.add(new_news_in_nepali)
            message = "News in Nepali created successfully"

        await db.commit()
        return {"message": message}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing news: {str(e)}")


@app.get("/details/nepali/",response_model=list[DetailRead])
async def get_details_nepali(db:AsyncSession=Depends(get_db)):
    try:
        result = await db.execute(select(NewsInNepali))
        all_news_nepali = result.scalars().all()
        if not all_news_nepali:
            raise HTTPException(status_code=404,detail="No news available.")
        
        return all_news_nepali
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error {e}")
    


@app.get("/news-carts/nepali/")
async def get_detail_nepali(db:AsyncSession=Depends(get_db)):
    try:
        result = await db.execute(select(NewsCart).options(selectinload(NewsCart.news_in_nepali)).where(NewsCart.news_in_nepali != None))
        nepali_news = result.scalars().all()
        
        if not nepali_news:
            raise HTTPException(status_code=404,detail="No news available yet.")
        
        for i in nepali_news:
            i.source = json.loads(i.source)
            i.cover_image = HttpUrl(i.cover_image)
        
        news = []
        for i in nepali_news:  
            news.append({
            "id":i.id,
            "title": i.news_in_nepali.title,
            "cover_image":i.cover_image,
            "source":i.source,
            "category": i.category,
            "time_of_release": i.time_of_release
                
            })  

        
        return news
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error: {e}")   





@app.get("/detail/nepali/{detail_id}")
async def get_detail_nepali(detail_id:str,db:AsyncSession=Depends(get_db)):
    try: 
        result = await db.execute(select(NewsCart).options(selectinload(NewsCart.news_in_nepali)).where(NewsCart.id == detail_id))
        detail = result.scalars().first()
        
        if not detail:
            raise HTTPException(status_code=404,details="No detail available for the given id")
        return {
            "id":detail.news_in_nepali.id,
            "description":detail.news_in_nepali.description
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error {e}")
    
    
    
    
    

@app.get("/detail/english/{detail_id}")
async def get_detail_english(detail_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsCart).options(selectinload(NewsCart.detail)).where(NewsCart.id == detail_id))
    cart = result.scalars().first()
    if not cart:
        raise HTTPException(status_code=404, detail="Detail not found")

    # convert string field in resource to python list
    # cart.source = json.loads(cart.source) if cart.source else []
    # cart.cover_image = HttpUrl(cart.cover_image)  # convert string to HttpUrl

    return {
        "id":cart.detail.id,
        "description": cart.detail.description,

    }

@app.get("/delete-all")
async def delete_all_rows(db: AsyncSession = Depends(get_db)):
    
    try:  
        await db.execute(delete(NewsCart))
        await db.execute(delete(NewsInDetail))
        await db.execute(delete(NewsInNepali))# DELETE FROM news_cart
        await db.commit()
        return {"message": "All rows deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting rows: {e}")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


 


