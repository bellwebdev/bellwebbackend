from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
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

class CustomerIn(BaseModel):
    fname: str
    lname: str
    email: str
    company: Optional[str] = None
    message: str

class CustomerUpdate(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None


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

# -------------------------
# Enable CORS
# -------------------------
# origins = [
#     "http://localhost:3000",   # Your frontend local URL
#     "https://yourfrontend.com" # Production frontend URL
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can also use ["*"] for all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/customers/", response_model=CustomerOut)
async def create_customer(customer: CustomerIn = Body(...)):
    query = """
        INSERT INTO customers (fname, lname, email, company, message)
        VALUES (:fname, :lname, :email, :company, :message)
        RETURNING id, fname, lname, email, company, message, created_at
    """
    new_customer = await database.fetch_one(query=query, values=customer.dict())
    return new_customer

@app.patch("/customers/{customer_id}", response_model=CustomerOut)
async def patch_customer(customer_id: int, customer: CustomerUpdate = Body(...)):
    # Build dynamic query based on provided fields
    update_fields = {k: v for k, v in customer.model_dump().items() if v is not None}
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys()])
    query = f"""
        UPDATE customers
        SET {set_clause}
        WHERE id = :id
        RETURNING id, fname, lname, email, company, message, created_at
    """
    values = {**update_fields, "id": customer_id}
    updated_customer = await database.fetch_one(query=query, values=values)

    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return updated_customer

from fastapi import HTTPException

@app.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: int):
    query = "DELETE FROM customers WHERE id = :id RETURNING id"
    deleted = await database.fetch_one(query=query, values={"id": customer_id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return None
