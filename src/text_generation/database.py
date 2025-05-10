from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
# DB 정보를 받아오는 곳입니다.
load_dotenv()

DB_NAME = os.environ["TEXT_GENERATION_DB_NAME"]
DB_USER = os.environ["TEXT_GENERATION_DB_USER"]
DB_PASSWORD = os.environ["TEXT_GENERATION_DB_PASSWORD"]
DB_HOST = os.environ["POSTGRES_HOST"]
DB_PORT = os.environ["POSTGRES_PORT"]

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)