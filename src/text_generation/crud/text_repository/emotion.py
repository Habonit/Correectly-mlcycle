from sqlalchemy.orm import Session
from src.text_generation.models.text_repository import TextRepositoryEmotion

class EmotionCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, emotion: str) -> TextRepositoryEmotion:
        obj = TextRepositoryEmotion(emotion=emotion)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, emotion_id: int) -> TextRepositoryEmotion | None:
        return self.session.query(TextRepositoryEmotion).filter(TextRepositoryEmotion.id == emotion_id).first()

    def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositoryEmotion]:
        return self.session.query(TextRepositoryEmotion).offset(skip).limit(limit).all()

    def update(self, emotion_id: int, emotion: str = None) -> TextRepositoryEmotion | None:
        obj = self.read(emotion_id)
        if not obj:
            return None
        if emotion is not None:
            obj.emotion = emotion
        self.session.commit()
        return obj

    def delete(self, emotion_id: int) -> TextRepositoryEmotion | None:
        obj = self.read(emotion_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
