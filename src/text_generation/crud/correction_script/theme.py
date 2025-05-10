from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptTheme

class CorrectionScriptThemeCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, theme: str) -> CorrectionScriptTheme:
        obj = CorrectionScriptTheme(theme=theme)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, theme_id: int) -> CorrectionScriptTheme | None:
        return (
            self.session.query(CorrectionScriptTheme)
            .filter(CorrectionScriptTheme.id == theme_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptTheme]:
        return (
            self.session.query(CorrectionScriptTheme)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        theme_id: int,
        theme: str | None = None
    ) -> CorrectionScriptTheme | None:
        obj = self.read(theme_id)
        if not obj:
            return None
        if theme is not None:
            obj.theme = theme
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, theme_id: int) -> CorrectionScriptTheme | None:
        obj = self.read(theme_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj