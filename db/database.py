from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os 

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

class Base(DeclarativeBase):
    pass

Base = declarative_base()  # ✅ Create the Base class for models to inherit from

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()