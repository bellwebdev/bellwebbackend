from datetime import datetime
from fastapi import FastAPI, HTTPException
from app.database import database
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from typing import Optional

# Pydantic model for customers
class CustomerOut(BaseModel):
    id: int
    fname: str
    lname: str
    email: str
    company: Optional[str] = None
    message: str
    created_at: datetime

# Lifespan context: connect on startup, disconnect on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    print("Database connected")
    yield
    await database.disconnect()
    print("Database disconnected")

# Create FastAPI app with lifespan
app = FastAPI(title="Customers API", lifespan=lifespan)

# Endpoint: Read all customers
@app.get("/customers/", response_model=List[CustomerOut])
async def get_customers():
    query = "SELECT id, fname, lname, email, company, message, created_at FROM customers ORDER BY id"
    return await database.fetch_all(query=query)


@app.get("/customers/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: int):
    query = "SELECT id, fname, lname, email, company, message, created_at FROM customers WHERE id = :id"
    customer = await database.fetch_one(query=query, values={"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
