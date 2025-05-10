from sqlalchemy.orm import Session
from src.text_generation.models.correction_script import CorrectionScriptKeyExpression

class CorrectionScriptKeyExpressionCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, key_expression: str) -> CorrectionScriptKeyExpression:
        obj = CorrectionScriptKeyExpression(key_expression=key_expression)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, expr_id: int) -> CorrectionScriptKeyExpression | None:
        return (
            self.session
            .query(CorrectionScriptKeyExpression)
            .filter(CorrectionScriptKeyExpression.id == expr_id)
            .first()
        )

    def read_all(self, skip: int = 0, limit: int = 100) -> list[CorrectionScriptKeyExpression]:
        return (
            self.session
            .query(CorrectionScriptKeyExpression)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        expr_id: int,
        key_expression: str | None = None
    ) -> CorrectionScriptKeyExpression | None:
        obj = self.read(expr_id)
        if not obj:
            return None
        if key_expression is not None:
            obj.key_expression = key_expression
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, expr_id: int) -> CorrectionScriptKeyExpression | None:
        obj = self.read(expr_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj