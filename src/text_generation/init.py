import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
from src.text_generation.models.base import Base
from src.text_generation.database import SessionLocal
from src.text_generation.load_sample_data import insert_sample_from_excel

load_dotenv()

db_user = os.environ["TEXT_GENERATION_DB_USER"]
db_password = os.environ["TEXT_GENERATION_DB_PASSWORD"]
db_name = os.environ["TEXT_GENERATION_DB_NAME"]
db_host = os.environ["POSTGRES_HOST"]
admin_user = os.environ["POSTGRES_USER"]
admin_password = os.environ["POSTGRES_PASSWORD"]
db_port = os.environ["POSTGRES_PORT"]

init_flag = os.environ.get("INIT", "false").lower() == "true"
sample_flag = os.environ.get("INSERT_SAMPLE", "false").lower() == "true"

def create_db_and_user():
    conn = psycopg2.connect(
        dbname="postgres",
        user=admin_user,
        password=admin_password,
        host=db_host,
        port=db_port
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}';")
    except Exception as e:
        print(f"유저 생성 생략 또는 실패: {e}")
    try:
        cur.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")
    except Exception as e:
        print(f"DB 생성 생략 또는 실패: {e}")
    cur.execute(f"GRANT ALL ON SCHEMA public TO {db_user};")
    conn.close()

def create_tables():
    url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(url)

    if init_flag:
        print("INIT=true → 기존 테이블 삭제 후 재생성 중...")
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)
    print("text_repository 스키마마 생성 완료")

    if sample_flag:
        print("🧪 INSERT_SAMPLE=true → 샘플 데이터 삽입 중...")
        session = SessionLocal()

        insert_sample_from_excel(session)
        session.close()

if __name__ == "__main__":
    create_db_and_user()
    create_tables()
