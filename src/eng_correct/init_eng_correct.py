import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.eng_correct.db_model import Base, SessionLocal
from src.eng_correct.load_sample_data import insert_sample_from_directory

# TODO: FIXIT
# 환경변수 로드 (공통 → 개별 순으로 덮어쓰기 가능)
# load_dotenv(dotenv_path="/usr/local/project/postgres/.env")                  # 공통 admin 정보
# load_dotenv(dotenv_path="/usr/local/project/src/eng_correct/.env")      # eng_correct 전용 설정
load_dotenv()

container = False

# eng_correct DB 및 유저 정보
eng_user = os.environ["ENG_DB_USER"]
eng_pw = os.environ["ENG_DB_PASSWORD"]
eng_db = os.environ["ENG_DB_NAME"]

# PostgreSQL 관리자 정보
admin_user = os.environ["POSTGRES_USER"]
admin_pw = os.environ["POSTGRES_PASSWORD"]
host = os.environ["POSTGRES_HOST"]
port = os.environ["POSTGRES_PORT"]

init_flag = os.environ.get("INIT", "false").lower() == "true"
sample_flag = os.environ.get("INSERT_SAMPLE", "false").lower() == "true"

def create_eng_db_and_user():
    conn = psycopg2.connect(
        dbname="postgres",
        user=admin_user,
        password=admin_pw,
        host=host,
        port=port
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE USER {eng_user} WITH PASSWORD '{eng_pw}';")
    except Exception as e:
        print(f"ℹ 유저 생성 생략 또는 실패: {e}")
    try:
        cur.execute(f"CREATE DATABASE {eng_db} OWNER {eng_user};")
    except Exception as e:
        print(f"ℹ DB 생성 생략 또는 실패: {e}")
    cur.execute(f"GRANT ALL ON SCHEMA public TO {eng_user};")
    conn.close()

def create_tables():
    url = f"postgresql+psycopg2://{eng_user}:{eng_pw}@{host}:{port}/{eng_db}"
    engine = create_engine(url)

    if init_flag:
        print("♻️ INIT=true → 기존 테이블 삭제 후 재생성 중...")
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)
    print("✅ eng_correct 테이블 생성 완료")

    if sample_flag:
        print("🧪 INSERT_SAMPLE=true → 샘플 데이터 삽입 중...")
        session = SessionLocal()
        insert_sample_from_directory(session, "./src/eng_correct/sample")

if __name__ == "__main__":
    create_eng_db_and_user()
    create_tables()