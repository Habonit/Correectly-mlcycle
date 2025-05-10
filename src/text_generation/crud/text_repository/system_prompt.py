from sqlalchemy.orm import Session
from src.text_generation.models.text_repository import TextRepositorySystemPrompt

class SystemPromptCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, prompt: str) -> TextRepositorySystemPrompt:
        obj = TextRepositorySystemPrompt(prompt=prompt)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, prompt_id: int) -> TextRepositorySystemPrompt | None:
        return self.session.query(TextRepositorySystemPrompt).filter(TextRepositorySystemPrompt.id == prompt_id).first()

    def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositorySystemPrompt]:
        return self.session.query(TextRepositorySystemPrompt).offset(skip).limit(limit).all()

    def update(self, prompt_id: int, prompt: str = None) -> TextRepositorySystemPrompt | None:
        obj = self.read(prompt_id)
        if not obj:
            return None
        if prompt is not None:
            obj.prompt = prompt
        self.session.commit()
        return obj

    def delete(self, prompt_id: int) -> TextRepositorySystemPrompt | None:
        obj = self.read(prompt_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
