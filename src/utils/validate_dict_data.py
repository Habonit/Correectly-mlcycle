from loguru import logger

def validate_dict_data(config: dict, allowed_keys: list[str]):
    """
    config의 키들이 반드시 allowed_keys 집합과 정확히 일치하는지 검사합니다.
    - allowed_keys에 있지만 config에 없는 키 → missing
    - config에는 있지만 allowed_keys에 없는 키 → unexpected
    둘 중 하나라도 있으면 ValueError를 발생시키고, 상세 내용을 출력합니다.
    """
    allowed = set(allowed_keys)
    present = set(config.keys())

    missing = allowed - present
    unexpected = present - allowed

    errors = []
    if missing:
        errors.append(f"Missing keys: {', '.join(sorted(missing))}")
    if unexpected:
        errors.append(f"Unexpected keys: {', '.join(sorted(unexpected))}")

    if errors:
        msg = "YAML key validation failed: " + " | ".join(errors)
        logger.error(msg)        
        raise ValueError(msg)
    
    else:
        logger.debug(f"Validation passed. Keys: {sorted(present)}")
    
