from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptInferenceEvaluation

class CorrectionScriptInferenceEvaluationCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        generated_text_id: int,
        evaluation_prompt_id: int,
        label: str,
        inference: str,
        etc: str | None = None
    ) -> CorrectionScriptInferenceEvaluation:
        obj = CorrectionScriptInferenceEvaluation(
            generated_text_id=generated_text_id,
            evaluation_prompt_id=evaluation_prompt_id,
            label=label,
            inference=inference,
            etc=etc
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, eval_id: int) -> CorrectionScriptInferenceEvaluation | None:
        return (
            self.session
            .query(CorrectionScriptInferenceEvaluation)
            .filter(CorrectionScriptInferenceEvaluation.id == eval_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptInferenceEvaluation]:
        return (
            self.session
            .query(CorrectionScriptInferenceEvaluation)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        eval_id: int,
        generated_text_id: int | None = None,
        evaluation_prompt_id: int | None = None,
        label: str | None = None,
        inference: str | None = None,
        etc: str | None = None
    ) -> CorrectionScriptInferenceEvaluation | None:
        obj = self.read(eval_id)
        if not obj:
            return None
        if generated_text_id is not None:
            obj.generated_text_id = generated_text_id
        if evaluation_prompt_id is not None:
            obj.evaluation_prompt_id = evaluation_prompt_id
        if label is not None:
            obj.label = label
        if inference is not None:
            obj.inference = inference
        if etc is not None:
            obj.etc = etc
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, eval_id: int) -> CorrectionScriptInferenceEvaluation | None:
        obj = self.read(eval_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
