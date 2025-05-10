from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptExample

class CorrectionScriptExampleCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        creativity_id: int,
        length_id: int,
        system_prompt_id: int,
        generation_prompt_id: int,
        form_id: int,
        mapping_emotion_form_id: int,
        speaker_id: int,
        example: str,
        style_id: int | None = None,
        theme_id: int | None = None,
        key_expression_id: int | None = None,
        etc: str | None = None
    ) -> CorrectionScriptExample:
        obj = CorrectionScriptExample(
            creativity_id=creativity_id,
            length_id=length_id,
            system_prompt_id=system_prompt_id,
            generation_prompt_id=generation_prompt_id,
            form_id=form_id,
            mapping_emotion_form_id=mapping_emotion_form_id,
            style_id=style_id,
            theme_id=theme_id,
            key_expression_id=key_expression_id,
            speaker_id=speaker_id,
            example=example,
            etc=etc
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, example_id: int) -> CorrectionScriptExample | None:
        return (
            self.session
            .query(CorrectionScriptExample)
            .filter(CorrectionScriptExample.id == example_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptExample]:
        return (
            self.session
            .query(CorrectionScriptExample)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        example_id: int,
        creativity_id: int | None = None,
        length_id: int | None = None,
        system_prompt_id: int | None = None,
        generation_prompt_id: int | None = None,
        form_id: int | None = None,
        mapping_emotion_form_id: int | None = None,
        style_id: int | None = None,
        theme_id: int | None = None,
        key_expression_id: int | None = None,
        speaker_id: int | None = None,
        example: str | None = None,
        etc: str | None = None
    ) -> CorrectionScriptExample | None:
        obj = self.read(example_id)
        if not obj:
            return None
        if creativity_id is not None:
            obj.creativity_id = creativity_id
        if length_id is not None:
            obj.length_id = length_id
        if system_prompt_id is not None:
            obj.system_prompt_id = system_prompt_id
        if generation_prompt_id is not None:
            obj.generation_prompt_id = generation_prompt_id
        if form_id is not None:
            obj.form_id = form_id
        if mapping_emotion_form_id is not None:
            obj.mapping_emotion_form_id = mapping_emotion_form_id
        if style_id is not None:
            obj.style_id = style_id
        if theme_id is not None:
            obj.theme_id = theme_id
        if key_expression_id is not None:
            obj.key_expression_id = key_expression_id
        if speaker_id is not None:
            obj.speaker_id = speaker_id
        if example is not None:
            obj.example = example
        if etc is not None:
            obj.etc = etc

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, example_id: int) -> CorrectionScriptExample | None:
        obj = self.read(example_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
