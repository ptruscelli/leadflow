from sqlalchemy import create_engine, Integer, String, Column
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('sqlite:///leads.db', echo=True)
conn = engine.connect()