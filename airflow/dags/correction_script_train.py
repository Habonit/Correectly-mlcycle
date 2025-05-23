from src.text_generation.models.text_repository import *
from src.text_generation.models.correction_script import *

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from itertools import product

from src.text_generation.database import SessionLocal

from src.text_generation.crud.correction_script.train import CorrectionScriptTrainCRUD
from src.text_generation.crud.correction_script.instruction_prompt import CorrectionScriptInstructionPromptCRUD
from src.text_generation.crud.correction_script.generated_text import CorrectionScriptGeneratedTextCRUD
from src.utils.load_yaml import load_yaml
from src.utils.logger import setup_logger

# 환경 설정
load_dotenv()
log_level = os.getenv("LOG_LEVEL", "DEBUG")
logger = setup_logger(log_level)
project_path = Path(os.getenv('PROJECT_PATH'))

def load_config(cfg_path: Path):
    """
    YAML 설정 파일을 로드하고, 텍스트 생성에 필요한 파라미터와 컬럼 설정을 파싱합니다.

    설정 파일로부터 필수 키의 존재 여부를 확인한 뒤, 필수 컬럼, 선택 컬럼, 타겟 컬럼을 분리합니다.
    필수 컬럼 값들의 모든 조합을 계산하여 반환합니다.

    Args:
        cfg_path (Path): 설정 파일의 경로입니다.
        required_keys (list[str], optional): 반드시 존재해야 하는 키 목록입니다. 기본값은 ['model', 'iteration_num']입니다.

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

def get_crud_mappings(session):
    """
    SQLAlchemy 세션을 기반으로 모든 필요한 CRUD 객체를 생성하여 매핑 딕셔너리로 반환합니다.

    Args:
        session (Session): SQLAlchemy 세션 객체

    Returns:
        dict[str, BaseCRUD]: 컬럼명 → CRUD 객체 매핑
    """
    return {
        'instruction_prompt_id': CorrectionScriptInstructionPromptCRUD(session),
        'generated_text_id': CorrectionScriptGeneratedTextCRUD(session),
        'train': CorrectionScriptTrainCRUD(session),
    }

# XCom에 직렬화 가능한 데이터만 전달
def prepare_generation_data(**kwargs):
    """
    Airflow DAG에서 실행되는 태스크.
    
    DAG 실행 시 전달받은 `dag_run.conf`로부터 YAML 경로를 받아 설정 파일을 파싱하고,
    텍스트 생성에 필요한 반복 횟수, 파라미터 조합 리스트, 타겟 컬럼 정보를 준비하여 XCom으로 전달합니다.

    XCom Key: 'example_generation_config'

    dag_run.conf 예시:
    {
        "yaml_path": "airflow/config/correction_script/train/example.yaml"
    }

    Returns:
        None
    """
    dag_conf = kwargs.get('dag_run').conf if kwargs.get('dag_run') else {}
    relative_path = dag_conf.get('yaml_path', 'airflow/config/correction_script/train/example.yaml')
    cfg_path = project_path / relative_path
    cfg, etc, target, generation_param, generation_lst = load_config(cfg_path)
    payload = {
        'cfg_path': str(cfg_path),
        'cfg': cfg,
        'etc': etc,
        'target': target,
        'generation_param' : generation_param,
        'generation_lst': generation_lst
    }

    logger.success(f"[Load Config]: {list(cfg.keys())}")
    
    for key, value in payload.items():
        logger.debug(f"[Load Config]: {key}: {value} \n")
        
    kwargs['ti'].xcom_push(key='example_generation_config', value=payload)

# 실제 예시 생성 및 DB 삽입
def create_train_data(**kwargs):
    """
    Airflow DAG에서 실행되는 태스크.

    XCom으로부터 generation config를 불러와,
    각 조합별로 LLM 프롬프트를 구성 → 응답 생성 → DB에 저장하는 전체 과정을 수행합니다.

    프롬프트 포맷은 YAML에 정의된 generation_prompt 템플릿에 따라 구성됩니다.
    CRUD 매핑을 통해 DB에 예시 데이터를 저장합니다.

    Returns:
        None
    """
    payload = kwargs['ti'].xcom_pull(key='example_generation_config', task_ids='prepare_generation_data')
    session = SessionLocal()
    crud_mappings = get_crud_mappings(session)

    def make_params(row, deliminator = "#####"):
        # one shot prompt 생성 전략을 취하기 때문에 반드시 example_id를 받아와서 해당 행의 다양한 특징을 입력해야 합니다.
        params = {}
                    
        if row.get('generated_text_id') is not None:
            generated_text = crud_mappings['generated_text_id'].read(row['generated_text_id']).generated_text
            generated_text_id = row['generated_text_id']
            
            input_ = generated_text.split(deliminator)[0]
            output = generated_text
            rejected = None
            
        else:
            generated_text = None
            generated_text_id = None
            
            input_ = None
            output = None
            rejected = None
        
        params['input'] = input_
        params['output'] = output
        params['rejected'] = rejected
        params['generated_text_id'] = generated_text_id
        
        return params

    iteration_num = payload.get('generation_param', {}).get('iteration_num', 1)
        
    for _ in range(iteration_num):
        for row in payload['generation_lst']:
            for name in payload['etc']:
                row[name] = None
            params = make_params(row)
            row['input'] = params['input']
            row['output'] = params['output']
            row['rejected'] = params['rejected']

            obj = crud_mappings['train'].create(**row)
            session.commit()
            session.refresh(obj)
    
    session.close()

# DAG 정의
with DAG(
    dag_id="correction_script_make_train_data",
    start_date=datetime(2025, 5, 8),
    schedule_interval=None,
    catchup=False,
    description="1) YAML 로드 → 2) train data 전용 전처리리",
    tags=["yaml", "llm", "test"],
    params={
        "yaml_path": "airflow/config/correction_script/train/example.yaml",
    }
) as dag:

    t1 = PythonOperator(
        task_id="prepare_generation_data",
        python_callable=prepare_generation_data,
        provide_context=True
    )

    t2 = PythonOperator(
        task_id="create_train_data",
        python_callable=create_train_data,
        provide_context=True
    )

    t1 >> t2
