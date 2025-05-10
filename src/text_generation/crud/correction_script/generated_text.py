from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptGeneratedText

class CorrectionScriptGeneratedTextCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        creativity_id: int,
        length_id: int,
        example_id: int,
        generated_text: str,
        etc: str | None = None
    ) -> CorrectionScriptGeneratedText:
        obj = CorrectionScriptGeneratedText(
            creativity_id=creativity_id,
            length_id=length_id,
            example_id=example_id,
            generated_text=generated_text,
            etc=etc
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, generated_id: int) -> CorrectionScriptGeneratedText | None:
        return (
            self.session
            .query(CorrectionScriptGeneratedText)
            .filter(CorrectionScriptGeneratedText.id == generated_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptGeneratedText]:
        return (
            self.session
            .query(CorrectionScriptGeneratedText)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        generated_id: int,
        creativity_id: int | None = None,
        length_id: int | None = None,
        example_id: int | None = None,
        generated_text: str | None = None,
        etc: str | None = None
    ) -> CorrectionScriptGeneratedText | None:
        obj = self.read(generated_id)
        if not obj:
            return None
        if creativity_id is not None:
            obj.creativity_id = creativity_id
        if length_id is not None:
            obj.length_id = length_id
        if example_id is not None:
            obj.example_id = example_id
        if generated_text is not None:
            obj.generated_text = generated_text
        if etc is not None:
            obj.etc = etc
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, generated_id: int) -> CorrectionScriptGeneratedText | None:
        obj = self.read(generated_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
