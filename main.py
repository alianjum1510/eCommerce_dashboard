from fastapi import FastAPI
from routers import inventory,sales  # Import the router from the inventory module

app = FastAPI()
app.include_router(inventory.router)

app.include_router(sales.router)
