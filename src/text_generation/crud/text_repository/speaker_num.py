# TODO: 삭제 예정정
# from sqlalchemy.orm import Session
# from src.text_generation.models.text_repository import TextRepositorySpeakerNum

# class SpeakerNumCRUD:
#     def __init__(self, session: Session):
#         self.session = session

#     def create(self, speaker_num: int) -> TextRepositorySpeakerNum:
#         obj = TextRepositorySpeakerNum(speaker_num=speaker_num)
#         self.session.add(obj)
#         self.session.commit()
#         self.session.refresh(obj)
#         return obj

#     def read(self, speaker_num_id: int) -> TextRepositorySpeakerNum | None:
#         return self.session.query(TextRepositorySpeakerNum).filter(TextRepositorySpeakerNum.id == speaker_num_id).first()

#     def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositorySpeakerNum]:
#         return self.session.query(TextRepositorySpeakerNum).offset(skip).limit(limit).all()

#     def update(self, speaker_num_id: int, speaker_num: int = None) -> TextRepositorySpeakerNum | None:
#         obj = self.read(speaker_num_id)
#         if not obj:
#             return None
#         if speaker_num is not None:
#             obj.speaker_num = speaker_num
#         self.session.commit()
#         return obj

#     def delete(self, speaker_num_id: int) -> TextRepositorySpeakerNum | None:
#         obj = self.read(speaker_num_id)
#         if obj:
#             self.session.delete(obj)
#             self.session.commit()
#         return obj
