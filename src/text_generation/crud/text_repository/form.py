from sqlalchemy.orm import Session
from src.text_generation.models.text_repository import TextRepositoryForm

class FormCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create(self, form: str, description: str, speaker_num: int) -> TextRepositoryForm:
        obj = TextRepositoryForm(form=form, description=description, speaker_num=speaker_num)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def read(self, form_id: int) -> TextRepositoryForm | None:
        return self.session.query(TextRepositoryForm).filter(TextRepositoryForm.id == form_id).first()

    def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositoryForm]:
        return self.session.query(TextRepositoryForm).offset(skip).limit(limit).all()

    def update(self, form_id: int, form: str = None, description: str = None, speaker_num: int = None) -> TextRepositoryForm | None:
        obj = self.read(form_id)
        if not obj:
            return None
        if form is not None:
            obj.form = form
        if description is not None:
            obj.description = description
        if speaker_num is not None:
            obj.speaker_num = speaker_num
        self.session.commit()
        return obj

    def delete(self, form_id: int) -> TextRepositoryForm | None:
        obj = self.read(form_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj