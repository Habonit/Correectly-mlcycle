# TODO: 삭제 예정
# from sqlalchemy.orm import Session
# from src.text_generation.models.text_repository import TextRepositoryExample


# class ExampleCRUD:
#     def __init__(self, session: Session):
#         self.session = session

#     def create(self, form_id: int, example: str) -> TextRepositoryExample:
#         obj = TextRepositoryExample(form_id=form_id, example=example)
#         self.session.add(obj)
#         self.session.commit()
#         self.session.refresh(obj)
#         return obj

#     def read(self, example_id: int) -> TextRepositoryExample | None:
#         return self.session.query(TextRepositoryExample).filter(TextRepositoryExample.id == example_id).first()

#     def read_all(self, skip: int = 0, limit: int = 100) -> list[TextRepositoryExample]:
#         return self.session.query(TextRepositoryExample).offset(skip).limit(limit).all()

#     def update(self, example_id: int, form_id: int = None, example: str = None) -> TextRepositoryExample | None:
#         obj = self.read(example_id)
#         if not obj:
#             return None
#         if form_id is not None:
#             obj.form_id = form_id
#         if example is not None:
#             obj.example = example
#         self.session.commit()
#         return obj

#     def delete(self, example_id: int) -> TextRepositoryExample | None:
#         obj = self.read(example_id)
#         if obj:
#             self.session.delete(obj)
#             self.session.commit()
#         return obj
