import logging


# Config concurrency with Semaphore to avoid sending too many requests to the target/serveer
CONCURRENCY=5
# Config logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')


# Basic configs of the target website(s) to be scraped
INDEX_URL = 'https://spa5.scrape.center/api/book?limit=18&offset={offset}'
DETAILS_URL = 'https://spa5.scrape.center/api/book/{book_id}'
ITEMS_PER_PAGE = 18
PAGE_NUMBER = 1

# Configure async database
from motor.motor_asyncio import AsyncIOMotorClient
MONGO_CLIENT = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'scrape_books'
MONGO_COLLECTION_NAME = 'books'

db_client = AsyncIOMotorClient(MONGO_CLIENT)
db = db_client[MONGO_DB_NAME]
db_coll = db[MONGO_COLLECTION_NAME]
