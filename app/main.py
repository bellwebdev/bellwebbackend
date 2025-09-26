from fastapi import FastAPI
from dotenv import load_dotenv
import databases
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

database = databases.Database(DATABASE_URL)
app = FastAPI()

print("DATABASE_URL:", DATABASE_URL)

@app.get("/health")
async def health():
    return {"status": "ok"}
