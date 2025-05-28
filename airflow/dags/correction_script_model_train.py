from src.text_generation.models.text_repository import *
from src.text_generation.models.correction_script import *

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
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
from src.utils.write_json import write_json
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
    
    cfg, etc, target, generation_param, train_param = {}, [], [], {}, {}
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
            
        elif t == 'train_param':
            train_param[key] = v
        
    generation_lst = [dict(zip(cfg.keys(), combo)) for combo in product(*cfg.values())]
    return cfg, etc, target, generation_param, generation_lst, train_param

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
        "yaml_path": "airflow/config/correction_script/model_train/example.yaml"
    }

    Returns:
        None
    """
    dag_conf = kwargs.get('dag_run').conf if kwargs.get('dag_run') else {}
    relative_path = dag_conf.get('yaml_path', 'airflow/config/correction_script/model_train/example.yaml')
    cfg_path = project_path / relative_path
    cfg, etc, target, generation_param, generation_lst, train_param = load_config(cfg_path)
    payload = {
        'cfg_path': str(cfg_path),
        'cfg': cfg,
        'etc': etc,
        'target': target,
        'generation_param' : generation_param,
        'generation_lst': generation_lst,
        'train_param': train_param
    }

    logger.success(f"[Load Config]: {list(cfg.keys())}")
    
    for key, value in payload.items():
        logger.debug(f"[Load Config]: {key}: {value} \n")
        
    kwargs['ti'].xcom_push(key='example_generation_config', value=payload)

# 실제 예시 생성 및 DB 삽입
def write_train_data(**kwargs):
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
    dag_conf = kwargs.get('dag_run').conf if kwargs.get('dag_run') else {}
    train_data_path = dag_conf.get('train_data_path', 'data/train_corpus.json')    
    val_data_path = dag_conf.get('val_data_path', 'data/val_corpus.json')    
    logger.info(f"[Write Train Data]: {train_data_path}에 저장")
    session = SessionLocal()
    crud_mappings = get_crud_mappings(session)

    def make_params(num):
        # one shot prompt 생성 전략을 취하기 때문에 반드시 example_id를 받아와서 해당 행의 다양한 특징을 입력해야 합니다.
        params = {}
                    
        train_obj = crud_mappings['train'].read(num)
        instruction_prompt_id = train_obj.instruction_prompt_id
        instruction = crud_mappings['instruction_prompt_id'].read(instruction_prompt_id).prompt
        input_ = train_obj.input
        output = train_obj.output
        rejected = train_obj.rejected
        
        params['instruction'] = instruction
        params['input'] = input_
        params['output'] = output
        params['rejected'] = rejected
        
        return params

    iteration_num = payload.get('generation_param', {}).get('iteration_num', 1)
        
    train_result = []
    for _ in range(iteration_num):
        for num in payload['cfg']['train_id']:

            params = make_params(num)
            train_result.append(params)
    write_json(path=train_data_path, data=train_result)
    
    val_result = []
    for _ in range(iteration_num):
        for num in payload['cfg']['val_id']:

            params = make_params(num)
            val_result.append(params)
    write_json(path=val_data_path, data=val_result)
    
    logger.info(f"[Write Train Data] train 데이터 개수: {len(train_result)}")
    logger.info(f"[Write Train Data] val 데이터 개수: {len(val_result)}")
    
# DAG 정의
with DAG(
    dag_id="correction_script_model_train",
    start_date=datetime(2025, 5, 8),
    schedule_interval=None,
    catchup=False,
    description="1) YAML 로드 → 2) train data 저장 ",
    tags=["yaml", "llm", "test"],
    params={
        "yaml_path": "airflow/config/correction_script/model_train/example.yaml",
        'train_data_path': "data/train_corpus.json",
        'val_data_path': "data/val_corpus.json",
        "train_ip":None,
        "train_port":None,
        "host_name":None,
        "train_dir":None,
        "ssh_key":"/.ssh/id_rsa"
    }
) as dag:

    t1 = PythonOperator(
        task_id="prepare_generation_data",
        python_callable=prepare_generation_data,
        provide_context=True
    )

    t2 = PythonOperator(
        task_id="write_train_data",
        python_callable=write_train_data,
        provide_context=True
    )
    t3 = DockerOperator(
        task_id="train_model",
        image="llama3.2-sft:latest",
        api_version="auto",
        auto_remove=False,
        command=(
            "python -m src.train_sft "
            "--train_json /data/train_corpus.json "
            "--model_name meta-llama/Llama-3.2-1B-Instruct "
            "--output_dir /models/sft/llama3.2-1b "
            "--batch_size 4 "
            "--num_epochs 3 "
            "--save_total_limit 2"
        ),
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        volumes=[
            f"{project_path}/data:/data",
            f"{project_path}/models:/models"
        ],
        environment={
            "HF_HOME": "/cache/huggingface",
            "TRANSFORMERS_CACHE": "/cache/huggingface"
        }
    )

    t1 >> t2
