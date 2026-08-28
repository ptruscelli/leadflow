from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import settings
# set up for SQLite + fastapi
engine = create_engine(settings.database_url,                    
                       connect_args={"check_same_thread": False})



SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)   

