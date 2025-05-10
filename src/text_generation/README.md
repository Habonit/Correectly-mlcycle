# Text Generation Database

text_generation 프로젝트는 다양한 텍스트 생성 관련 데이터(형식, 감정, 화자 수, 길이, 창의성 등)를 관리하고, 샘플 데이터를 기반으로 데이터베이스를 구축하는 시스템입니다.

---

## 프로젝트 구조

```
src/
└── text_generation/
    ├── crud/                # 각 테이블별 CRUD 스크립트
    ├── sample/              # 샘플 데이터(.xlsx)
    ├── __init__.py
    ├── db_model.py            # DB 테이블 모델 정의
    ├── init_text_generation.py # DB 구축 + 샘플 데이터 삽입 스크립트
    ├── load_sample_data.py    # Excel 파일을 읽어 DB에 삽입
    └── README.md
```

---

## 환경 설정

`.env` 파일을 작성해 프로젝트 환경을 설정해야 합니다.

`.env.example` 파일을 복사해 `.env` 파일을 생성한 후, 다음과 같이 설정하세요:

```dotenv
# DB Connection Info
TEXT_GENERATION_DB_NAME=text_generation
TEXT_GENERATION_DB_USER=text_generation
TEXT_GENERATION_DB_PASSWORD=text_generation

# Options
INIT=true         # 처음 실행 시 기존 DB를 삭제하고 재생성
INSERT_SAMPLE=true # 테이블 생성 후 샘플 데이터 삽입 여부
```

---

## 초기화 방법 (Database Initialization)

### 1. 데이터베이스 및 유저 생성

```bash
python -m src.text_generation.init_text_generation.py
```

- 데이터베이스와 유저가 존재하지 않으면 생성합니다.
- 이미 존재하는 경우 오류 없이 넘어갑니다.


### 2. 테이블 생성 및 샘플 데이터 삽입

- `INIT=true`인 경우: 기존 테이블을 삭제하고 재생성합니다.
- `INSERT_SAMPLE=true`인 경우: `sample/text_generation_schema.xlsx` 파일을 읽어 데이터를 삽입합니다.

샘플 데이터 삽입만 별도로 실행하려면:
```python
from src.text_generation.load_sample_data import insert_sample_from_excel

session = SessionLocal()
insert_sample_from_excel(session, "src/text_generation/sample/text_generation_schema.xlsx")
```

---

## CRUD 구조

- 모든 테이블에 대해 CRUD 기능이 `crud/` 폴더에 분리되어 있습니다.
- `create`, `read`, `read_all`, `update`, `delete` 메서드를 제공합니다.
- Python 타입힌트를 이용해 명확한 인터페이스를 제공합니다.


---

## 시작 전 준비사항

1. `.env` 파일을 알맞게 설정합니다.
2. 다음 명령어를 실행합니다.(시작 경로: airflow container 접속 => cd /usr/local/project)

```bash
python -m src.text_generation.init_text_generation.py
```

---

## 주의사항

- Excel 파일의 NaN 값은 자동으로 NULL로 변환하여 삽입됩니다.
- 에러가 발생해도 프로세스가 중단되지 않고 다음 레코드로 계속 진행합니다.
- 기본적으로 PostgreSQL + SQLAlchemy 조합을 사용합니다.

---

## 추가 가능 기능

✔️ 필요 시:
- 테이블 별 전체 데이터 삭제 지원
- 필드별 Bulk Insert 최적화
- FastAPI와 연동하여 API 서버 개발
