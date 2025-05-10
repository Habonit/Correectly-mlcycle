from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptStyle

class CorrectionScriptStyleCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, style: str) -> CorrectionScriptStyle:
        obj = CorrectionScriptStyle(style=style)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, style_id: int) -> CorrectionScriptStyle | None:
        return (
            self.session.query(CorrectionScriptStyle)
            .filter(CorrectionScriptStyle.id == style_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptStyle]:
        return (
            self.session.query(CorrectionScriptStyle)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        style_id: int,
        style: str | None = None
    ) -> CorrectionScriptStyle | None:
        obj = self.read(style_id)
        if not obj:
            return None
        if style is not None:
            obj.style = style
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, style_id: int) -> CorrectionScriptStyle | None:
        obj = self.read(style_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
