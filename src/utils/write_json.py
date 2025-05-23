from loguru import logger
from pathlib import Path
import json

def write_json(path, data, indent=2):
    """
    주어진 데이터를 JSON 형식으로 지정된 경로에 저장합니다.

    Args:
        path (str | Path): 저장할 파일 경로
        data (Any): JSON으로 직렬화 가능한 Python 객체
        indent (int, optional): 들여쓰기 수준. 기본값은 2입니다.

    Raises:
        Exception: 파일 저장 중 오류 발생 시 예외 발생
    """
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        logger.success(f"Json 파일 저장 완료: {path}")
    except Exception as e:
        logger.error(f"Json 저장 실패: {path} | 에러: {e}")
        raise
