# src/text_generation/crud_registry.py
from collections import OrderedDict

# from src.text_generation.crud.text_repository.speaker_num import SpeakerNumCRUD
from src.text_generation.crud.text_repository.form import FormCRUD
from src.text_generation.crud.text_repository.emotion import EmotionCRUD
from src.text_generation.crud.text_repository.mapping_emotion_form import MappingEmotionFormCRUD
from src.text_generation.crud.text_repository.system_prompt import SystemPromptCRUD
from src.text_generation.crud.text_repository.generation_prompt import GenerationPromptCRUD
from src.text_generation.crud.text_repository.creativity import CreativityCRUD
from src.text_generation.crud.text_repository.length import LengthCRUD

from src.text_generation.crud.correction_script.correction_script_type import CorrectionScriptTypeCRUD
from src.text_generation.crud.correction_script.style import CorrectionScriptStyleCRUD
from src.text_generation.crud.correction_script.theme import CorrectionScriptThemeCRUD
from src.text_generation.crud.correction_script.key_expression import CorrectionScriptKeyExpressionCRUD
from src.text_generation.crud.correction_script.speaker import CorrectionScriptSpeakerCRUD
from src.text_generation.crud.correction_script.example import CorrectionScriptExampleCRUD
from src.text_generation.crud.correction_script.generated_text import CorrectionScriptGeneratedTextCRUD
from src.text_generation.crud.correction_script.inference_evaluation import CorrectionScriptInferenceEvaluationCRUD
from src.text_generation.crud.correction_script.evaluation_prompt import CorrectionScriptEvaluationPromptCRUD

# 초기 각 테이블 멸 모든 crud를 등록해놓는 스크립트입니다.
# 반드시 샘플 데이터의 시트이름과 테이블 명이 일치해야 합니다.

text_repository_crud_mapping = OrderedDict([
    # ('speaker_num',               SpeakerNumCRUD),
    ('system_prompt',             SystemPromptCRUD),
    ('generation_prompt',         GenerationPromptCRUD),
    ('creativity',                CreativityCRUD),
    ('length',                    LengthCRUD),
    ('emotion',                   EmotionCRUD),
    ('form',                      FormCRUD),
    ('mapping_emotion_form',      MappingEmotionFormCRUD)
])

correction_script_crud_mapping = OrderedDict([
    ('correction_script_type', CorrectionScriptTypeCRUD),
    ('style', CorrectionScriptStyleCRUD),
    ('theme', CorrectionScriptThemeCRUD),
    ('key_expression', CorrectionScriptKeyExpressionCRUD),
    ('speaker', CorrectionScriptSpeakerCRUD),
    ('example', CorrectionScriptExampleCRUD),
    ('generated_text', CorrectionScriptGeneratedTextCRUD),
    ('evaluation_prompt', CorrectionScriptEvaluationPromptCRUD),
    ('inference_evaluation', CorrectionScriptInferenceEvaluationCRUD)
])


crud_mapping = [
    {
        "schema" : "text_repository",
        "excel_path" : "./src/text_generation/sample/text_repository.xlsx",
        "mapping" : text_repository_crud_mapping
    },
    {
        "schema" : "correction_script",
        "excel_path" : "./src/text_generation/sample/correction_script.xlsx",
        "mapping" : correction_script_crud_mapping
    }
]
