from sqlalchemy.orm import Session
from src.text_generation.models.text_repository import TextRepositoryGenerationPrompt

class GenerationPromptCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, prompt: str) -> TextRepositoryGenerationPrompt:
        obj = TextRepositoryGenerationPrompt(prompt=prompt)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, generation_prompt_id: int) -> TextRepositoryGenerationPrompt | None:
        return self.session.query(TextRepositoryGenerationPrompt).filter(TextRepositoryGenerationPrompt.id == generation_prompt_id).first()

    def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositoryGenerationPrompt]:
        return self.session.query(TextRepositoryGenerationPrompt).offset(skip).limit(limit).all()

    def update(self, generation_prompt_id: int, prompt: str = None) -> TextRepositoryGenerationPrompt | None:
        obj = self.read(generation_prompt_id)
        if not obj:
            return None
        if prompt is not None:
            obj.prompt = prompt
        self.session.commit()
        return obj

    def delete(self, generation_prompt_id: int) -> TextRepositoryGenerationPrompt | None:
        obj = self.read(generation_prompt_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
