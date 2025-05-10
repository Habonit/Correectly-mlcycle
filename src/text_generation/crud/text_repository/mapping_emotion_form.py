from sqlalchemy.orm import Session
from src.text_generation.models.text_repository import TextRepositoryMappingEmotionForm

class MappingEmotionFormCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, emotion_id: int, form_id: int, tone: str = None) -> TextRepositoryMappingEmotionForm:
        obj = TextRepositoryMappingEmotionForm(
            emotion_id=emotion_id,
            form_id=form_id,
            tone=tone
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, mapping_id: int) -> TextRepositoryMappingEmotionForm | None:
        return self.session.query(TextRepositoryMappingEmotionForm).filter(TextRepositoryMappingEmotionForm.id == mapping_id).first()

    def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositoryMappingEmotionForm]:
        return self.session.query(TextRepositoryMappingEmotionForm).offset(skip).limit(limit).all()

    def update(self, mapping_id: int, emotion_id: int = None, form_id: int = None, tone: str = None) -> TextRepositoryMappingEmotionForm | None:
        obj = self.read(mapping_id)
        if not obj:
            return None
        if emotion_id is not None:
            obj.emotion_id = emotion_id
        if form_id is not None:
            obj.form_id = form_id
        if tone is not None:
            obj.tone = tone
        self.session.commit()
        return obj

    def delete(self, mapping_id: int) -> TextRepositoryMappingEmotionForm | None:
        obj = self.read(mapping_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj
