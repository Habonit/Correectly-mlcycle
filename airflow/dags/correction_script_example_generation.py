from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from itertools import product

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
from src.module.llm.gpt import GPTClient
from src.utils.load_yaml import load_yaml
from src.utils.logger import setup_logger

# 환경 설정
load_dotenv()
log_level = os.getenv("LOG_LEVEL", "DEBUG")
logger = setup_logger(log_level)
project_path = Path(os.getenv('PROJECT_PATH'))
relative_path = Variable.get(
    "yaml_path",
    default_var="airflow/config/correction_script/example/example.yaml"
)
test_prompt = Variable.get(
    "test_prompt",
    default_var='정수 2이상 12이하의 소수의 개수를 구해주세요.'
)

# YAML 로드 및 파싱

def load_config(cfg_path: Path):
    raw = load_yaml(cfg_path)
    model = raw['model']['value']
    iteration_num = raw['iteration_num']['value']
    cfg, etc, target = {}, [], None
    for key, val in raw.items():
        t = val['type']; v = val['value']
        if t == 'necessary_column':
            cfg[key] = v
        elif t == 'optional_column':
            (cfg if v else etc).append(key) if isinstance(v, list) else etc.append(key)
            if v:
                cfg[key] = v
        elif t == 'target_column':
            target = key
    generation_lst = [dict(zip(cfg.keys(), combo)) for combo in product(*cfg.values())]
    return model, iteration_num, cfg, etc, target, generation_lst

# XCom에 직렬화 가능한 데이터만 전달

def prepare_generation_data(**kwargs):
    cfg_path = project_path / relative_path
    model, iteration_num, cfg, etc, target, generation_lst = load_config(cfg_path)
    payload = {
        'cfg_path': str(cfg_path),
        'model': model,
        'iteration_num': iteration_num,
        'cfg': cfg,
        'etc': etc,
        'target': target,
        'generation_lst': generation_lst
    }
    kwargs['ti'].xcom_push(key='example_generation_config', value=payload)
    logger.success(f"Loaded config keys: {list(cfg.keys())}")

# LLM 동작 테스트

def test_llm_generation(**kwargs):
    payload = kwargs['ti'].xcom_pull(key='example_generation_config', task_ids='prepare_generation_data')
    gpt = GPTClient(model=payload['model'])
    response = gpt.send_hard_temporary_message(test_prompt)
    logger.success(f"[LLM Test] Prompt: {test_prompt} | Response: {response}")
    kwargs['ti'].xcom_push(key='test_generation_data', value=response)

# 실제 예시 생성 및 DB 삽입

def create_example(**kwargs):
    payload = kwargs['ti'].xcom_pull(key='example_generation_config', task_ids='prepare_generation_data')
    session = SessionLocal()
    crud_mappings = {
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
        'example': CorrectionScriptExampleCRUD(session)
    }

    def make_params(row):
        params = {}
        # creativity_id → temperature
        if row.get('creativity_id') is not None:
            params['temperature'] = float(
                crud_mappings['creativity_id'].read(row['creativity_id']).degree
            )
        else:
            params['temperature'] = None
        # length_id → max_tokens
        if row.get('length_id') is not None:
            params['max_tokens'] = (
                crud_mappings['length_id'].read(row['length_id']).length
            )
        else:
            params['max_tokens'] = None
        # system_prompt_id → system_prompt
        if row.get('system_prompt_id') is not None:
            params['system_prompt'] = (
                crud_mappings['system_prompt_id'].read(row['system_prompt_id']).prompt
            )
        else:
            params['system_prompt'] = None
        # generation_prompt_id → raw_prompt
        if row.get('generation_prompt_id') is not None:
            raw_prompt = (
                crud_mappings['generation_prompt_id']
                .read(row['generation_prompt_id'])
                .prompt
            )
        else:
            raw_prompt = ''
        # form_id → form, form_description
        if row.get('form_id') is not None:
            form_obj = crud_mappings['form_id'].read(row['form_id'])
            form = form_obj.form
            form_description = form_obj.description
        else:
            form = None
            form_description = None
        # mapping_emotion_form_id → tone
        if row.get('mapping_emotion_form_id') is not None:
            tone = (
                crud_mappings['mapping_emotion_form_id']
                .read(row['mapping_emotion_form_id'])
                .tone
            )
        else:
            tone = None
        # style_id → style
        if row.get('style_id') is not None:
            style = (
                crud_mappings['style_id']
                .read(row['style_id'])
                .style
            )
        else:
            style = None
        # key_expression_id → key_expression
        if row.get('key_expression_id') is not None:
            key_expression = (
                crud_mappings['key_expression_id']
                .read(row['key_expression_id'])
                .key_expression
            )
        else:
            key_expression = None
        # theme_id → theme
        if row.get('theme_id') is not None:
            theme = (
                crud_mappings['theme_id']
                .read(row['theme_id'])
                .theme
            )
        else:
            theme = None
        # speaker_id → speaker
        if row.get('speaker_id') is not None:
            speaker = (
                crud_mappings['speaker_id']
                .read(row['speaker_id'])
                .speaker
            )
        else:
            speaker = None
        # example (기존 예시) → example_text
        if row.get('example') is not None:
            example_text = (
                crud_mappings['example']
                .read(row['example'])
                .example
            )
        else:
            example_text = None
        # etc 컬럼 그대로
        etc = row.get('etc', None)
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

    for _ in range(payload['iteration_num']):
        for row in payload['generation_lst']:
            for name in payload['etc']:
                row[name] = None
            params = make_params(row)
            # 방어 코드: generation_prompt가 없으면 에러
            gen_prompt = params.get('generation_prompt') or ''
            sys_prompt = params.get('system_prompt') or ''
            gpt = GPTClient(model=payload['model'], system_prompt=sys_prompt)
            resp = gpt.send_hard_temporary_message(
                gen_prompt,
                max_tokens=params.get('max_tokens'),
                temperature=params.get('temperature')
            )
            row[payload['target']] = resp['message']
            obj = crud_mappings[payload['target']].create(**row)
            session.commit()
            session.refresh(obj)

# DAG 정의
with DAG(
    dag_id="correction_script_example_generation",
    start_date=datetime(2025, 5, 8),
    schedule_interval=None,
    catchup=False,
    description="1) YAML 로드 → 2) LLM 테스트 → 3) 예시 생성",
    tags=["yaml", "llm", "test"]
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
        task_id="create_example",
        python_callable=create_example,
        provide_context=True
    )

    t1 >> t2 >> t3
