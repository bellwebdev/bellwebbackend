from fastapi import FastAPI
import databases
import os

DATABASE_URL = os.getenv("DATABASE_URL")

database = databases.Database(DATABASE_URL)
app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/health")
async def health():
    return {"status": "ok"}
