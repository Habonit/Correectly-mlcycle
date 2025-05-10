from loguru import logger
from pathlib import Path
import yaml

def load_yaml(yaml_path):
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        logger.error(f"YAML 파일을 찾을 수 없습니다: {yaml_path}")
        raise FileNotFoundError(f"YAML not found at {yaml_path}")
    
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
