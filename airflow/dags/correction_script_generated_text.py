from airflow import DAG
from airflow.operators.python import PythonOperator

from src.text_generation.models.text_repository import *
from src.text_generation.models.correction_script import *
from src.text_generation.database import SessionLocal

from src.text_generation.crud.text_repository.creativity import CreativityCRUD
from src.text_generation.crud.text_repository.length import LengthCRUD
from src.text_generation.crud.text_repository.system_prompt import SystemPromptCRUD
from src.text_generation.crud.text_repository.generation_prompt import GenerationPromptCRUD
from src.text_generation.crud.text_repository.form import FormCRUD
from src.text_generation.crud.text_repository.mapping_emotion_form import MappingEmotionFormCRUD
from src.text_generation.crud.correction_script.style import CorrectionScriptStyleCRUD
from src.text_generation.crud.correction_script.key_expression import CorrectionScriptKeyExpressionCRUD
from src.text_generation.crud.correction_script.theme import CorrectionScriptThemeCRUD
from src.text_generation.crud.correction_script.speaker import CorrectionScriptSpeakerCRUD
from src.text_generation.crud.correction_script.example import CorrectionScriptExampleCRUD
from src.text_generation.crud.correction_script.generated_text import CorrectionScriptGeneratedTextCRUD

from src.module.llm.gpt import GPTClient
from src.utils.logger import setup_logger
from src.utils.load_dag_config import load_dag_config

from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import os

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
        'creativity_id': CreativityCRUD(session),
        'length_id': LengthCRUD(session),
        'system_prompt_id': SystemPromptCRUD(session),
        'generation_prompt_id': GenerationPromptCRUD(session),
        'form_id': FormCRUD(session),
        'mapping_emotion_form_id': MappingEmotionFormCRUD(session),
        'style_id': CorrectionScriptStyleCRUD(session),
        'key_expression_id': CorrectionScriptKeyExpressionCRUD(session),
        'theme_id': CorrectionScriptThemeCRUD(session),
        'speaker_id': CorrectionScriptSpeakerCRUD(session),
        'example_id': CorrectionScriptExampleCRUD(session),
        'generated_text': CorrectionScriptGeneratedTextCRUD(session)
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
    relative_path = dag_conf.get('yaml_path', 'airflow/config/correction_script/generated_text/example.yaml')
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
        
    kwargs['ti'].xcom_push(key='generated_text_config', value=payload)

# LLM 동작 테스트
def test_llm_generation(**kwargs):
    """
    테스트용 프롬프트(`test_prompt`)를 이용해 
    LLM의 응답을 테스트하고, 결과를 로그에 출력합니다.

    결과는 XCom key 'test_generation_data'로 저장됩니다.

    dag_run.conf 예시:
    {
        "test_prompt": "정수 2이상 12이하의 소수의 개수를 구해주세요. 이 때 소수의 정의를 한 문장으로 정의, 이를 기준으로 2부터 12까지 소인수분해를 모두 진행, 소수의 개수를 구하는 3단계로 설명해주세요."
    }

    Returns:
        None
    """
    dag_conf = kwargs.get('dag_run').conf if kwargs.get('dag_run') else {}
    test_prompt = dag_conf.get('test_prompt', '정수 2이상 12이하의 소수의 개수를 구해주세요. 이 때 소수의 정의를 한 문장으로 정의, 이를 기준으로 2부터 12까지 소인수분해를 모두 진행, 소수의 개수를 구하는 3단계로 설명해주세요.')

    payload = kwargs['ti'].xcom_pull(key='generated_text_config', task_ids='prepare_generation_data')
    model = payload.get('generation_params', {}).get('model', 'gpt-4o-mini')
    gpt = GPTClient(model=model)
    response = gpt.send_hard_temporary_message(test_prompt)
    logger.success(f"[LLM Test] Prompt: {test_prompt}: Answer: {response['message']}")
    for key, value in response.items():
        if key != 'message':
            logger.debug(f"[LLM Test] {key}: {value}")
    kwargs['ti'].xcom_push(key='test_generation_data', value=response)

def create_genereated_text(**kwargs):
    """
    XCom으로부터 generation config를 불러와,
    각 조합별로 LLM 프롬프트를 구성 → 응답 생성 → DB에 저장하는 전체 과정을 수행합니다.

    프롬프트 포맷은 YAML에 정의된 generation_prompt 템플릿에 따라 구성됩니다.
    CRUD 매핑을 통해 DB에 예시 데이터를 저장합니다.

    Returns:
        None
    """
    payload = kwargs['ti'].xcom_pull(key='generated_text_config', task_ids='prepare_generation_data')
    session = SessionLocal()
    crud_mappings = get_crud_mappings(session)

    # 해당함수는 row 한 줄을 받아서 새롭게 데이터를 정의합니다.
    # DAG마다 달라질 수 있습니다. 
    def make_params(row):
        
        # one shot prompt 생성 전략을 취하기 때문에 반드시 example_id를 받아와서 해당 행의 다양한 특징을 입력해야 합니다.
        print(row.keys())
        if row.get('example_id') is not None:
            obj = crud_mappings['example_id'].read(row['example_id'])
            system_prompt_id = obj.system_prompt_id
            generation_prompt_id = obj.generation_prompt_id
            form_id = obj.form_id
            mapping_emotion_form_id = obj.mapping_emotion_form_id
            style_id = obj.style_id
            key_expression_id = obj.key_expression_id
            theme_id = obj.theme_id
            speaker_id = obj.speaker_id
            example_text = obj.example
        else :
            message = f"[create_train_data] | 정책 상 example_id가 없으면 훈련 데이터를 생성할 수 없습니다."
            logger.error(message)
            raise ValueError("[create_train_data] | 정책 상 example_id가 없으면 훈련 데이터를 생성할 수 없습니다.")
                    
        params = {}
        # creativity_id → temperature
        if row.get('creativity_id') is not None:
            params['temperature'] = float(
                crud_mappings['creativity_id'].read(row['creativity_id']).degree
            )
        else:
            params['temperature'] = None
        logger.debug(f"[create_train_data] | temperature: {params['temperature']}")
        
        # length_id → max_tokens
        if row.get('length_id') is not None:
            params['max_tokens'] = (
                crud_mappings['length_id'].read(row['length_id']).length
            )
        else:
            params['max_tokens'] = None
        logger.debug(f"[create_train_data] | max_tokens: {params['max_tokens']}")    
            
        # etc 컬럼 그대로
        etc = row.get('etc', None)
        # system_prompt_id → system_prompt
        if system_prompt_id is not None:
            params['system_prompt'] = (
                crud_mappings['system_prompt_id'].read(system_prompt_id).prompt
            )
        else:
            params['system_prompt'] = None
        logger.debug(f"[create_train_data] | system_prompt: {params['system_prompt']}")
            
        # generation_prompt_id → raw_prompt
        if generation_prompt_id is not None:
            raw_prompt = (
                crud_mappings['generation_prompt_id']
                .read(generation_prompt_id)
                .prompt
            )
        else:
            raw_prompt = ''
        logger.debug(f"[create_train_data] | raw_prompt: {raw_prompt}")    
            
        # form_id → form, form_description
        if form_id is not None:
            form_obj = crud_mappings['form_id'].read(form_id)
            form = form_obj.form
            form_description = form_obj.description
        else:
            form = None
            form_description = None
        logger.debug(f"[create_train_data] | form: {form}")    
        logger.debug(f"[create_train_data] | form_description: {form_description}")        
            
        # mapping_emotion_form_id → tone
        if mapping_emotion_form_id is not None:
            tone = (
                crud_mappings['mapping_emotion_form_id']
                .read(mapping_emotion_form_id)
                .tone
            )
        else:
            tone = None
        logger.debug(f"[create_train_data] | tone: {tone}")        
            
        # style_id → style
        if style_id is not None:
            style = (
                crud_mappings['style_id']
                .read(style_id)
                .style
            )
        else:
            style = None
        logger.debug(f"[create_train_data] | style: {style}")          
            
        # key_expression_id → key_expression
        if key_expression_id is not None:
            key_expression = (
                crud_mappings['key_expression_id']
                .read(key_expression_id)
                .key_expression
            )
        else:
            key_expression = None
        logger.debug(f"[create_train_data] | key_expression: {key_expression}")       
            
        # theme_id → theme
        if theme_id is not None:
            theme = (
                crud_mappings['theme_id']
                .read(theme_id)
                .theme
            )
        else:
            theme = None
        logger.debug(f"[create_train_data] | theme: {theme}")      
            
        # speaker_id → speaker
        if speaker_id is not None:
            speaker = (
                crud_mappings['speaker_id']
                .read(speaker_id)
                .speaker
            )
        else:
            speaker = None
        logger.debug(f"[create_train_data] | speaker: {speaker}")     
        logger.debug(f"[create_train_data] | example: {example_text}") 

        # 최종 generation_prompt 포맷
        params['generation_prompt'] = raw_prompt.format(
            form_form=form,
            form_description=form_description,
            speaker_speaker=speaker,
            mapping_emotion_form_tone=tone,
            example_example=example_text,
            key_expression_key_expression=key_expression,
            theme_theme=theme,
            style_style=style,
            etc=etc
        )
        return params

    iteration_num = payload.get('generation_param', {}).get('iteration_num', 1)
    model = payload.get('generation_param', {}).get('model', 'gpt-4o-mini')

    for _ in range(iteration_num):
        for row in payload['generation_lst']:
            for name in payload['etc']:
                row[name] = None
            params = make_params(row)
            gen_prompt = params.get('generation_prompt') or ''
            sys_prompt = params.get('system_prompt') or ''
            
            gpt = GPTClient(model=model, system_prompt=sys_prompt)
            resp = gpt.send_hard_temporary_message(
                gen_prompt,
                max_tokens=params.get('max_tokens', 1024),
                temperature=params.get('temperature', 0.7)
            )
            row[payload['target'][0]] = resp['message']
            obj = crud_mappings[payload['target'][0]].create(**row)
            session.commit()
            session.refresh(obj)
    
    session.close()

# DAG 정의
with DAG(
    dag_id="correction_script_generated_text",
    start_date=datetime(2025, 5, 8),
    schedule_interval=None,
    catchup=False,
    description="1) YAML 로드 → 2) LLM 테스트 → 3) 훈련 데이터 생성",
    tags=["correction_script", "generated_text_table"],
    params={
        "yaml_path": "airflow/config/correction_script/generated_text/example.yaml",
        "test_prompt": "정수 2이상 12이하의 소수의 개수를 구해주세요."
    }
) as dag:

    t1 = PythonOperator(
        task_id="prepare_generation_data",
        python_callable=prepare_generation_data,
        provide_context=True
    )

    t2 = PythonOperator(
        task_id="test_llm_generation",
        python_callable=test_llm_generation,
        provide_context=True
    )

    t3 = PythonOperator(
        task_id="create_genereated_text",
        python_callable=create_genereated_text,
        provide_context=True
    )

    t1 >> t2 >> t3
