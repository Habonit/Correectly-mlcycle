from sqlalchemy.orm import Session
from src.text_generation.models.text_repository import TextRepositoryCreativity

class CreativityCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, degree: int, description: str) -> TextRepositoryCreativity:
        obj = TextRepositoryCreativity(degree=degree, description=description)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, creativity_id: int) -> TextRepositoryCreativity | None:
        return self.session.query(TextRepositoryCreativity).filter(TextRepositoryCreativity.id == creativity_id).first()

    def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositoryCreativity]:
        return self.session.query(TextRepositoryCreativity).offset(skip).limit(limit).all()

    def update(self, creativity_id: int, degree: int = None, description: str = None) -> TextRepositoryCreativity | None:
        obj = self.read(creativity_id)
        if not obj:
            return None
        if degree is not None:
            obj.degree = degree
        if description is not None:
            obj.description = description
        self.session.commit()
        return obj

    def delete(self, creativity_id: int) -> TextRepositoryCreativity | None:
        obj = self.read(creativity_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
