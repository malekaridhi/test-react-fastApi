from fastapi import FastAPI
from database import engine
from models import Base
# from api import router as api_router    


app = FastAPI(title="Genie OPs test", version="1.0.0")
# Create the database tables
Base.metadata.create_all(bind=engine)
#routes
# app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Genie OPs test API"}