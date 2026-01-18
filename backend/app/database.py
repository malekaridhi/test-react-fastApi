from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
load_dotenv()
import os
# the db url  b in the .env file
DATABASE_URL = os.getenv("DATABASE_URL")
# create the database engine
engine = create_engine(DATABASE_URL)
# create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# create a base class for our models
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
Base = declarative_base()