from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta,timezone
from sqlalchemy import delete
from Database.database import AsyncSessionLocal
from Models.models import NewsCart
from pipeline1 import NewsFetcher


scheduler = AsyncIOScheduler()




scheduler = AsyncIOScheduler()

async def delete_expired_news():                    
    expiry_time = datetime.now(timezone.utc) - timedelta(hours=10)
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(
                delete(NewsCart).where(NewsCart.time_of_release < expiry_time)
            )
            await db.commit()
            print("Expired news deleted successfully.")
    except Exception as e:
        
        print(f"Error deleting expired news: {e}")
  


scheduler.add_job(delete_expired_news, "interval", minutes=600)
scheduler.add_job(NewsFetcher, "interval", minutes=200)








