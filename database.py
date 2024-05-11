from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.invoiceModelDetailed import DetailedReportDetails  # Ensure this inheritance is needed or correct
from models.sessionModel import Session
import os
import logging

# Assuming Session is a class you want to use as a MongoDB document model
class Sessions(Document, Session):
    pass

async def init_db():
    logging.info("Initializing database connection...")
    try:
        client = AsyncIOMotorClient(create_mongo_url())
        await init_beanie(database=client["MyDB"], document_models=[Sessions])
        logging.info("Database connection initialized successfully.")
    except Exception as e:
        logging.critical(f"Error initializing database connection: {e}", exc_info=True)

def create_mongo_url() -> str:
    # It's better to use environment variables to manage sensitive data
    username = os.getenv("MONGO_USER", "rootuser")
    password = os.getenv("MONGO_PASS", "rootpass")
    host = os.getenv("MONGO_HOST", "mongodb")
    port = os.getenv("MONGO_PORT", "27017")
    mongo_url = "mongodb://rootuser:rootpass@127.0.0.1:27017/"
    return mongo_url

# Configure logging here if this is the entry point of your application
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example async call in Python's asyncio event loop
    import asyncio
    asyncio.run(init_db())
