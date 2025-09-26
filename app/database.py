from dotenv import load_dotenv
import databases
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

database = databases.Database(DATABASE_URL)