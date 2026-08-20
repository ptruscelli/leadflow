from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# set up for SQLite + fastapi
engine = create_engine("sqlite:///./data/leads.db",
                       echo=True,                    
                       connect_args={"check_same_thread": False})

Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)   


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()