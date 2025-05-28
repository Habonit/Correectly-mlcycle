from airflow import DAG
from airflow.operators.python import PythonOperator

from src.text_generation.models.text_repository import *
from src.text_generation.models.correction_script import *
from src.text_generation.database import SessionLocal

from src.text_generation.crud.correction_script.train import CorrectionScriptTrainCRUD
from src.text_generation.crud.correction_script.instruction_prompt import CorrectionScriptInstructionPromptCRUD
from src.text_generation.crud.correction_script.generated_text import CorrectionScriptGeneratedTextCRUD

from src.utils.load_dag_config import load_dag_config
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
        'generated_text_id': CorrectionScriptGeneratedTextCRUD(session),
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
    relative_path = dag_conf.get('yaml_path', 'airflow/config/correction_script/train/example.yaml')
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

    # 해당함수는 row 한 줄을 받아서 새롭게 데이터를 정의합니다.
    # DAG마다 달라질 수 있습니다. 
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
    dag_id="correction_script_train",
    start_date=datetime(2025, 5, 8),
    schedule_interval=None,
    catchup=False,
    description="1) YAML 로드 → 2) train data 전용 전처리",
    tags=["correction_script", "train_table"],
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
