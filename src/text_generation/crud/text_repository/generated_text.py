# TODO: GeneratedTextCRUD는 text_repository에서 빠질 예정
# from sqlalchemy.orm import Session
# from src.text_generation.models.text_repository import GeneratedText


# class GeneratedTextCRUD:
#     def __init__(self, session: Session):
#         self.session = session

#     def create(
#         self,
#         system_prompt_id: int,
#         mapping_speaker_num_form_id: int,
#         mapping_emotion_form_id: int,
#         creativity_id: int,
#         length_id: int,
#         necessary_expression: str = None,
#         style: str = None,
#         theme: str = None,
#         generated_text: str = None
#     ) -> GeneratedText:
#         obj = GeneratedText(
#             system_prompt_id=system_prompt_id,
#             mapping_speaker_num_form_id=mapping_speaker_num_form_id,
#             mapping_emotion_form_id=mapping_emotion_form_id,
#             creativity_id=creativity_id,
#             length_id=length_id,
#             necessary_expression=necessary_expression,
#             style=style,
#             theme=theme,
#             generated_text=generated_text
#         )
#         self.session.add(obj)
#         self.session.commit()
#         self.session.refresh(obj)
#         return obj

#     def read(self, generated_text_id: int) -> GeneratedText | None:
#         return self.session.query(GeneratedText).filter(GeneratedText.id == generated_text_id).first()

#     def read_all(self, skip: int = 0, limit: int = 100) -> list[GeneratedText]:
#         return self.session.query(GeneratedText).offset(skip).limit(limit).all()

#     def update(
#         self,
#         generated_text_id: int,
#         necessary_expression: str = None,
#         style: str = None,
#         theme: str = None,
#         generated_text: str = None
#     ) -> GeneratedText | None:
#         obj = self.read(generated_text_id)
#         if not obj:
#             return None
#         if necessary_expression is not None:
#             obj.necessary_expression = necessary_expression
#         if style is not None:
#             obj.style = style
#         if theme is not None:
#             obj.theme = theme
#         if generated_text is not None:
#             obj.generated_text = generated_text
#         self.session.commit()
#         return obj

#     def delete(self, generated_text_id: int) -> GeneratedText | None:
#         obj = self.read(generated_text_id)
#         if obj:
#             self.session.delete(obj)
#             self.session.commit()
#         return obj
