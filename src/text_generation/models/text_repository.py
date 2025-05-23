from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

# 어떤 스키마에 대하여 테이블 별로 정의된 것입니다.
# 현재는 fk-pk만 연결되어 있으며 세부 정책은 적용되어있지 않습니다.

class TextRepositoryForm(Base):
    __tablename__ = 'form'
    __table_args__ = {
        'schema': 'text_repository',
        'comment': '글의 형태를 정의하는 테이블'
    }

    id = Column(Integer, primary_key=True)
    form = Column(String, nullable=False)
    description = Column(String, nullable=False)
    speaker_num = Column(Integer, nullable=False)

class TextRepositoryEmotion(Base):
    __tablename__ = 'emotion'
    __table_args__ = {
        'schema': 'text_repository',
        'comment': '글의 감정 상태를 정의하는 테이블'
    }

    id = Column(Integer, primary_key=True)
    emotion = Column(String, nullable=False)

class TextRepositoryMappingEmotionForm(Base):
    __tablename__ = 'mapping_emotion_form'
    __table_args__ = {
        'schema': 'text_repository',
        'comment': '감정 상태와 글의 형태의 관계를 저장하여 글의 어조를 정의하는 테이블'
    }

    id = Column(Integer, primary_key=True)
    emotion_id = Column(Integer, ForeignKey('text_repository.emotion.id'), nullable=False)
    form_id = Column(Integer, ForeignKey('text_repository.form.id'), nullable=False)
    tone = Column(String, nullable=True)

    emotion = relationship("TextRepositoryEmotion")
    form = relationship("TextRepositoryForm")

class TextRepositorySystemPrompt(Base):
    __tablename__ = 'system_prompt'
    __table_args__ = {
        'schema': 'text_repository',
        'comment': '시스템 레벨에서 사용하는 프롬프트를 저장하는 테이블'
    }

    id = Column(Integer, primary_key=True)
    prompt = Column(Text, nullable=False)

class TextRepositoryGenerationPrompt(Base):
    __tablename__ = 'generation_prompt'
    __table_args__ = {
        'schema': 'text_repository',
        'comment': '생성 단계에 입력될 프롬프트 문장을 저장하는 테이블'
    }

    id = Column(Integer, primary_key=True)
    prompt = Column(Text, nullable=False)

class TextRepositoryCreativity(Base):
    __tablename__ = 'creativity'
    __table_args__ = {
        'schema': 'text_repository',
        'comment': '생성 텍스트의 창의성 수준을 정의하는 테이블'
    }

    id = Column(Integer, primary_key=True)
    degree = Column(Float, nullable=False)
    description = Column(String, nullable=False)

class TextRepositoryLength(Base):
    __tablename__ = 'length'
    __table_args__ = {
        'schema': 'text_repository',
        'comment': '생성 텍스트의 길이 수준을 정의하는 테이블'
    }

    id = Column(Integer, primary_key=True)
    length = Column(Integer, nullable=False)
    
__all__ = [
    "TextRepositoryCreativity",
    "TextRepositoryLength",
    "TextRepositorySystemPrompt",
    "TextRepositoryGenerationPrompt",
    "TextRepositoryForm",
    "TextRepositoryEmotion",
    "TextRepositoryMappingEmotionForm",
]