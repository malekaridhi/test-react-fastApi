from fastapi import FastAPI
from database import engine, get_db,Base
from models import Base
from fastapi.middleware.cors import CORSMiddleware
from routes import  leads, leadMagnet, landingPage, emailTamplate

import logging
from contextlib import asynccontextmanager
# from api import router as api_router    

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown: Cleanup if needed
    logger.info("Shutting down application...")
app = FastAPI(title="Genie OPs test", version="1.0.0",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leadMagnet.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(landingPage.router, prefix="/api")
app.include_router(emailTamplate.router, prefix="/api")
# Create the database tables
Base.metadata.create_all(bind=engine)
#routes
# app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Lead Magnet Generator API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "leadMagnet": "/api/lead-magnets",
            "leads": "/api/leads",
            "landingPage": "/api/landing-pages",
            "emailTamplate": "/api/email-templates"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# API documentation available at /docs (Swagger UI) and /redoc (ReDoc)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)