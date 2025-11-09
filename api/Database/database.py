from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import logging
import asyncpg

logger = logging.getLogger(__name__)
load_dotenv()



# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing")

logger.info(f"Original DATABASE_URL: {DATABASE_URL[:20]}...")  # Log first 20 chars

# Better connection string handling for Supabase
def get_async_database_url():
    """Convert DATABASE_URL to async format properly"""
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        return DATABASE_URL
    elif DATABASE_URL.startswith("postgresql://"):
        return DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    elif DATABASE_URL.startswith("postgres://"):  # Common format
        return DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
    else:
        # If it's already in some other format, ensure it's async
        if "postgresql" in DATABASE_URL and "+asyncpg" not in DATABASE_URL:
            # Insert asyncpg into the connection string
            parts = DATABASE_URL.split("://")
            if len(parts) == 2:
                return f"postgresql+asyncpg://{parts[1]}"
        return DATABASE_URL

ASYNC_DATABASE_URL = get_async_database_url()
logger.info(f"Async DATABASE_URL: {ASYNC_DATABASE_URL[:20]}...")

try:
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=True,  
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        # Add connection timeout for serverless
        connect_args={
            "command_timeout": 10,
            "server_settings": {
                "jit": "off"
            }
        }
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    raise

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

Base = declarative_base()