from loguru import logger
from pathlib import Path
import json

def load_json(path):
    path = Path(path)
    if not path.exist():
        logger.error(f"Json 파일을 찾을 수 없습니다: {path}")
        raise FileNotFoundError(f"Json not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
