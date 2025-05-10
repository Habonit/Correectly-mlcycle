import pandas as pd
import os
from datetime import datetime

from src.text_generation.crud_registry import crud_mapping
from src.utils.logger import setup_logger

logger = setup_logger()

now = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("logs", exist_ok=True)
logger.add(f"logs/insert_sample_{now}.log", level="DEBUG", encoding="utf-8")

EXCLUDE_FIELDS = ("id", "created_at", "modified_at")
OPTIONAL_FIELDS = ("key_expression_id", "style_id", "theme_id", "etc")

def insert_sample_from_excel(session, target_sheets: list[str] = None):
    for item in crud_mapping:
        
        schema = item.get('schema')
        excel_path = item.get('excel_path')
        mapping = item.get('mapping')
        
        df_dict = pd.read_excel(excel_path, sheet_name=None)

        for sheet_name, CrudClass in mapping.items():
            # sheet_name: 스키마별 테이블명 
            # CrudClass: 테이블당 crud 클래스
            
            # target_sheets에 있는 테이블만 샘플 데이터로 넣을 경우
            # 그렇지 않으면 넘어갑니다.
            if target_sheets and sheet_name not in target_sheets:
                continue

            # crud의 테이블명과 실제 샘플 데이터의 테이블명이 안 맞는 경우우
            if sheet_name not in df_dict:
                logger.warning(f"[스킵] '{sheet_name}' 시트 없음")
                continue
            
            df = df_dict[sheet_name]
            crud = CrudClass(session)
            inserted_count = 0

            for record in df.to_dict(orient="records"):
                clean = {
                    k: (None if pd.isna(v) else v)
                        for k, v in record.items()
                            if k not in EXCLUDE_FIELDS
                }
                for optional in OPTIONAL_FIELDS:
                    if clean.get(optional) is None and optional in clean:
                        clean.pop(optional)
                try:
                    crud.create(**clean)
                    inserted_count += 1
                    
                except Exception as e:
                    session.rollback()
                    logger.error(f"[에러] {sheet_name} 레코드 삽입 중 오류: {e}")
                    # 계속 진행
                    continue

            try:
                session.commit()
                logger.success(f"[완료] '{sheet_name}' 테이블에 {inserted_count}개 레코드 삽입 완료.")
            except Exception as e:
                session.rollback()
                logger.error(f"[에러] '{sheet_name}' 테이블 커밋 중 오류: {e}")
