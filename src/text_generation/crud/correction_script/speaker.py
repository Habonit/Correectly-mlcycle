from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptSpeaker

class CorrectionScriptSpeakerCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, speaker: str) -> CorrectionScriptSpeaker:
        obj = CorrectionScriptSpeaker(speaker=speaker)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, expr_id: int) -> CorrectionScriptSpeaker | None:
        return (
            self.session
            .query(CorrectionScriptSpeaker)
            .filter(CorrectionScriptSpeaker.id == expr_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptSpeaker]:
        return (
            self.session
            .query(CorrectionScriptSpeaker)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        expr_id: int,
        speaker: str | None = None
    ) -> CorrectionScriptSpeaker | None:
        obj = self.read(expr_id)
        if not obj:
            return None
        if speaker is not None:
            obj.speaker = speaker
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, expr_id: int) -> CorrectionScriptSpeaker | None:
        obj = self.read(expr_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj