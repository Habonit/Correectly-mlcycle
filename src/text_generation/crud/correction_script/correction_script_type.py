from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptType

class CorrectionScriptTypeCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, type: str) -> CorrectionScriptType:
        obj = CorrectionScriptType(type=type)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, type_id: int) -> CorrectionScriptType | None:
        return (
            self.session.query(CorrectionScriptType)
            .filter(CorrectionScriptType.id == type_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptType]:
        return (
            self.session.query(CorrectionScriptType)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        type_id: int,
        type: str | None = None
    ) -> CorrectionScriptType | None:
        obj = self.read(type_id)
        if not obj:
            return None
        if type is not None:
            obj.type = type
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, type_id: int) -> CorrectionScriptType | None:
        obj = self.read(type_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj