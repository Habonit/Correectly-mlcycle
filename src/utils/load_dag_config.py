from src.utils.load_yaml import load_yaml

from itertools import product
from pathlib import Path

def load_dag_config(cfg_path: Path):
    """
    YAML 설정 파일을 로드하고, 텍스트 생성에 필요한 파라미터와 컬럼 설정을 파싱합니다.

    설정 파일로부터 필수 키의 존재 여부를 확인한 뒤, 필수 컬럼, 선택 컬럼, 타겟 컬럼을 분리합니다.
    필수 컬럼 값들의 모든 조합을 계산하여 반환합니다.

    Args:
        cfg_path (Path): 설정 파일의 경로입니다.

    Returns:
        tuple:
            - model (str): 설정된 모델 이름입니다.
            - iteration_num (int): 반복 횟수입니다.
            - cfg (dict[str, list[Any]]): 필수 컬럼과 그 값 목록입니다.
            - etc (list[str]): 값이 비었거나 형식이 맞지 않는 선택 컬럼 목록입니다.
            - target (str | None): 타겟 컬럼의 이름입니다. 없으면 None을 반환합니다.
            - generation_lst (list[dict[str, Any]]): 필수 컬럼들의 값 조합 리스트입니다.

    Raises:
        KeyError: required_keys에 포함된 키가 설정 파일에 존재하지 않을 경우 발생합니다.
    """
    raw = load_yaml(cfg_path)
    
    cfg, etc, target, generation_param = {}, [], [], {}
    for key, val in raw.items():
        t = val['type']; v = val['value']
        
        if t == 'necessary_column':
            if isinstance(v, list) and v:
                cfg[key] = v
            elif isinstance(v, str) and '~' in v:
                start, end = map(int, v.split('~'))
                cfg[key] = list(range(start, end+1))
                
        elif t == 'optional_column':
            if isinstance(v, list) and v:
                cfg[key] = v
            elif isinstance(v, str) and '~' in v:
                start, end = map(int, v.split('~'))
                cfg[key] = list(range(start, end+1))
            else:
                etc.append(key)
                
        elif t == 'target_column':
            target.append(key)
            
        elif t == 'generation_param':
            generation_param[key] = v
        
    generation_lst = [dict(zip(cfg.keys(), combo)) for combo in product(*cfg.values())]
    return cfg, etc, target, generation_param, generation_lst