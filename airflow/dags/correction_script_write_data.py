from airflow import DAG
from airflow.operators.python import PythonOperator

from src.text_generation.models.text_repository import *
from src.text_generation.models.correction_script import *
from src.text_generation.database import SessionLocal

from src.text_generation.crud.correction_script.train import CorrectionScriptTrainCRUD
from src.text_generation.crud.correction_script.instruction_prompt import CorrectionScriptInstructionPromptCRUD

from src.utils.load_dag_config import load_dag_config
from src.utils.write_json import write_json
from src.utils.logger import setup_logger

from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import os

# 환경 설정
load_dotenv()
log_level = os.getenv("LOG_LEVEL", "DEBUG")
logger = setup_logger(log_level)
project_path = Path(os.getenv('PROJECT_PATH'))

def get_crud_mappings(session):
    """
    SQLAlchemy 세션을 기반으로 필요한 CRUD 객체를 생성하여 매핑 딕셔너리로 반환합니다. 

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
    DAG 실행 시 전달받은 `dag_run.conf`로부터 YAML 경로를 받아 설정 파일을 파싱하고,
    텍스트 생성에 필요한 정보를 준비하여 XCom으로 전달합니다.

    XCom Key 예시: 'generated_text_config'

    dag_run.conf 예시:
    {
        "yaml_path": "airflow/config/correction_script/example/example.yaml"
    }

    Returns:
        None
    """
    dag_conf = kwargs.get('dag_run').conf if kwargs.get('dag_run') else {}
    relative_path = dag_conf.get('yaml_path', 'airflow/config/correction_script/write_data/example.yaml')
    cfg_path = project_path / relative_path
    cfg, etc, target, generation_param, generation_lst = load_dag_config(cfg_path)
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
        
    kwargs['ti'].xcom_push(key='write_data_config', value=payload)

# 실제 예시 생성 및 DB 삽입
def write_train_data(**kwargs):
    """
    """
    payload = kwargs['ti'].xcom_pull(key='write_data_config', task_ids='prepare_generation_data')
    dag_conf = kwargs.get('dag_run').conf if kwargs.get('dag_run') else {}
    generation_id = dag_conf.get('generation_id', '7883')  
    train_name = dag_conf.get('train_name', 'train_corpus.json')  
    val_name = dag_conf.get('val_name', 'train_corpus.json')  
    
    dir_path = f"data/{generation_id}"
    os.makedirs(dir_path, exist_ok=True)
    
    train_data_path = f"{dir_path}/{train_name}"
    val_data_path = f"{dir_path}/{val_name}"
      
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
    dag_id="correction_script_write_data",
    start_date=datetime(2025, 5, 8),
    schedule_interval=None,
    catchup=False,
    description="1) YAML 로드 → 2) train data 저장 ",
    tags=["yaml", "llm", "test"],
    params={
        "yaml_path": "airflow/config/correction_script/write_data/example.yaml",
        'generation_id' : "7883",
        "train_name" : "train_corpus.json",
        "val_name" : "val_corpus.json"
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

    t1 >> t2
