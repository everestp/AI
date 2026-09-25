import os

from dotenv import load_dotenv
from pymongo  import AsyncMongoClient

load_dotenv()
mongo_client : AsyncMongoClient = AsyncMongoClient(os.getenv("MONGO_URL"),)

