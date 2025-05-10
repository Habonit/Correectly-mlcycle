# TODO: 삭제 예정
# from sqlalchemy.orm import Session
# from src.text_generation.models.text_repository import TextRepositoryMappingSpeakerNumForm

# class MappingSpeakerNumFormCRUD:
#     def __init__(self, session: Session):
#         self.session = session

#     def create(self, speaker_num_id: int, form_id: int) -> TextRepositoryMappingSpeakerNumForm:
#         obj = TextRepositoryMappingSpeakerNumForm(
#             speaker_num_id=speaker_num_id,
#             form_id=form_id,
#         )
#         self.session.add(obj)
#         self.session.commit()
#         self.session.refresh(obj)
#         return obj

#     def read(self, mapping_id: int) -> TextRepositoryMappingSpeakerNumForm | None:
#         return self.session.query(TextRepositoryMappingSpeakerNumForm).filter(TextRepositoryMappingSpeakerNumForm.id == mapping_id).first()

#     def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositoryMappingSpeakerNumForm]:
#         return self.session.query(TextRepositoryMappingSpeakerNumForm).offset(skip).limit(limit).all()

#     def update(self, mapping_id: int, speaker_num_id: int = None, form_id: int = None) -> TextRepositoryMappingSpeakerNumForm | None:
#         obj = self.read(mapping_id)
#         if not obj:
#             return None
#         if speaker_num_id is not None:
#             obj.speaker_num_id = speaker_num_id
#         if form_id is not None:
#             obj.form_id = form_id
#         self.session.commit()
#         return obj

#     def delete(self, mapping_id: int) -> TextRepositoryMappingSpeakerNumForm | None:
#         obj = self.read(mapping_id)
#         if obj:
#             self.session.delete(obj)
#             self.session.commit()
#         return obj
