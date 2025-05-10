from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptEvaluationPrompt

class CorrectionScriptEvaluationPromptCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        type_id: int | None,
        evaluation_prompt: str
    ) -> CorrectionScriptEvaluationPrompt:
        obj = CorrectionScriptEvaluationPrompt(
            type_id=type_id,
            evaluation_prompt=evaluation_prompt
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, prompt_id: int) -> CorrectionScriptEvaluationPrompt | None:
        return (
            self.session
            .query(CorrectionScriptEvaluationPrompt)
            .filter(CorrectionScriptEvaluationPrompt.id == prompt_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptEvaluationPrompt]:
        return (
            self.session
            .query(CorrectionScriptEvaluationPrompt)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        prompt_id: int,
        type_id: int | None = None,
        evaluation_prompt: str | None = None
    ) -> CorrectionScriptEvaluationPrompt | None:
        obj = self.read(prompt_id)
        if not obj:
            return None
        if type_id is not None:
            obj.type_id = type_id
        if evaluation_prompt is not None:
            obj.evaluation_prompt = evaluation_prompt
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, prompt_id: int) -> CorrectionScriptEvaluationPrompt | None:
        obj = self.read(prompt_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj