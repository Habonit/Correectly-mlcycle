from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptInstructionPrompt

class CorrectionScriptInstructionPromptCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        type_id: int | None,
        prompt: str
    ) -> CorrectionScriptInstructionPrompt:
        obj = CorrectionScriptInstructionPrompt(
            type_id=type_id,
            prompt=prompt
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, prompt_id: int) -> CorrectionScriptInstructionPrompt | None:
        return (
            self.session
            .query(CorrectionScriptInstructionPrompt)
            .filter(CorrectionScriptInstructionPrompt.id == prompt_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptInstructionPrompt]:
        return (
            self.session
            .query(CorrectionScriptInstructionPrompt)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        prompt_id: int,
        type_id: int | None = None,
        prompt: str | None = None
    ) -> CorrectionScriptInstructionPrompt | None:
        obj = self.read(prompt_id)
        if not obj:
            return None
        if type_id is not None:
            obj.type_id = type_id
        if prompt is not None:
            obj.prompt = prompt
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, prompt_id: int) -> CorrectionScriptInstructionPrompt | None:
        obj = self.read(prompt_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj