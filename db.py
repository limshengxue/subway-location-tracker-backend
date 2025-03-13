from dotenv import load_dotenv
from sqlmodel import Session, create_engine, SQLModel
import os

load_dotenv()
DB_URL = os.getenv("DB_CONN")
print(DB_URL)
engine = create_engine(DB_URL)

def get_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session