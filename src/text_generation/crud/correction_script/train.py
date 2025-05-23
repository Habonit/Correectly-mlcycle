from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptTrain

class CorrectionScriptTrainCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        instruction_prompt_id: int | None,
        input: str,
        output: str,
        rejected: str | None = None,
        generated_text_id: int | None = None,
        etc: str | None = None,
    ) -> CorrectionScriptTrain:
        obj = CorrectionScriptTrain(
            instruction_prompt_id=instruction_prompt_id,
            input=input,
            output=output,
            rejected=rejected,
            generated_text_id=generated_text_id,
            etc=etc,
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, train_id: int) -> CorrectionScriptTrain | None:
        return (
            self.session
            .query(CorrectionScriptTrain)
            .filter(CorrectionScriptTrain.id == train_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptTrain]:
        return (
            self.session
            .query(CorrectionScriptTrain)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def read_by_ids(self, ids: list[int]) -> list[CorrectionScriptTrain]:
        if not ids:
            return []
        return (
            self.session
            .query(CorrectionScriptTrain)
            .filter(CorrectionScriptTrain.id.in_(ids))
            .all()
        )

    def update(
        self,
        train_id: int,
        instruction_prompt_id: int | None = None,
        input: str | None = None,
        output: str | None = None,
        rejected: str | None = None,
        generated_text_id: int | None = None,
        etc: str | None = None,
    ) -> CorrectionScriptTrain | None:
        obj = self.read(train_id)
        if not obj:
            return None
        if instruction_prompt_id is not None:
            obj.instruction_prompt_id = instruction_prompt_id
        if input is not None:
            obj.input = input
        if output is not None:
            obj.output = output
        if rejected is not None:
            obj.rejected = rejected
        if generated_text_id is not None:
            obj.generated_text_id = generated_text_id
        if etc is not None:
            obj.etc = etc

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, train_id: int) -> CorrectionScriptTrain | None:
        obj = self.read(train_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
