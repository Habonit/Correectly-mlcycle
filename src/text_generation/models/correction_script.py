from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

# 어떤 스키마에 대하여 테이블 별로 정의된 것입니다.
# 현재는 fk-pk만 연결되어 있으며 세부 정책은 적용되어있지 않습니다.

class CorrectionScriptType(Base):
    __tablename__  = 'correction_script_type'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id   = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)    
    
class CorrectionScriptKeyExpression(Base):
    __tablename__  = 'key_expression'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id   = Column(Integer, primary_key=True)
    key_expression = Column(String, nullable=False)
    
class CorrectionScriptStyle(Base):
    __tablename__  = 'style'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id      = Column(Integer, primary_key=True)
    style    = Column(String, nullable=False)

class CorrectionScriptTheme(Base):
    __tablename__  = 'theme'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id      = Column(Integer, primary_key=True)
    theme   = Column(String, nullable=False)
    
class CorrectionScriptSpeaker(Base):
    __tablename__  = 'speaker'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id      = Column(Integer, primary_key=True)
    speaker   = Column(String, nullable=False)
    
class CorrectionScriptExample(Base):
    __tablename__  = 'example'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id      = Column(Integer, primary_key=True)
    
    creativity_id                 = Column(Integer, ForeignKey('text_repository.creativity.id'), nullable=False)
    length_id                     = Column(Integer, ForeignKey('text_repository.length.id'), nullable=False)
    system_prompt_id              = Column(Integer, ForeignKey('text_repository.system_prompt.id'), nullable=False)
    generation_prompt_id          = Column(Integer, ForeignKey('text_repository.generation_prompt.id'), nullable=False)
    form_id                       = Column(Integer, ForeignKey('text_repository.form.id'), nullable=False)
    mapping_emotion_form_id       = Column(Integer, ForeignKey('text_repository.mapping_emotion_form.id'), nullable=False)
    style_id           = Column(Integer, ForeignKey('correction_script.style.id'), nullable=True)
    theme_id           = Column(Integer, ForeignKey('correction_script.theme.id'), nullable=True)
    key_expression_id  = Column(Integer, ForeignKey('correction_script.key_expression.id'), nullable=True)
    speaker_id         = Column(Integer, ForeignKey('correction_script.speaker.id'), nullable=False)
    
    etc = Column(Text, nullable=True)
    example = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    creativity            = relationship("TextRepositoryCreativity")
    length                = relationship("TextRepositoryLength")
    system_prompt         = relationship("TextRepositorySystemPrompt")
    generation_prompt     = relationship("TextRepositoryGenerationPrompt")
    form                  = relationship("TextRepositoryForm")
    mapping_emotion_form  = relationship("TextRepositoryMappingEmotionForm")
    style             = relationship("CorrectionScriptStyle")
    theme             = relationship("CorrectionScriptTheme")
    key_expression    = relationship("CorrectionScriptKeyExpression")
    speaker           = relationship("CorrectionScriptSpeaker")

class CorrectionScriptGeneratedText(Base):
    __tablename__  = 'generated_text'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id                 = Column(Integer, primary_key=True)
    
    creativity_id                 = Column(Integer, ForeignKey('text_repository.creativity.id'), nullable=False)
    length_id                     = Column(Integer, ForeignKey('text_repository.length.id'), nullable=False)
    example_id                    = Column(Integer, ForeignKey('correction_script.example.id'), nullable=False)
    
    etc = Column(Text, nullable=True)
    generated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    creativity        = relationship("TextRepositoryCreativity")
    length            = relationship("TextRepositoryLength")
    example             = relationship("CorrectionScriptExample")
 
class CorrectionScriptInstructionPrompt(Base):
    __tablename__  = 'instruction_prompt'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id                 = Column(Integer, primary_key=True)
    
    type_id = Column(Integer, ForeignKey('correction_script.correction_script_type.id'), nullable=True)
    prompt = Column(Text, nullable=False)
    
    correction_script_type = relationship("CorrectionScriptType")
    
class CorrectionScriptTrain(Base):
    __tablename__  = 'train'
    __table_args__ = {
        'schema': 'correction_script', 
        'comment': ''
    }
    id                 = Column(Integer, primary_key=True)
    
    instruction_prompt_id = Column(Integer, ForeignKey('correction_script.instruction_prompt.id'), nullable=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    rejected = Column(Text, nullable=True)
    generated_text_id = Column(Integer, ForeignKey('correction_script.generated_text.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    etc = Column(Text, nullable=True)
    
    correction_script_instruction_prompt = relationship("CorrectionScriptInstructionPrompt")
    correction_script_generated_text = relationship("CorrectionScriptGeneratedText")
    
__all__ = [
    "CorrectionScriptType",
    "CorrectionScriptKeyExpression",
    "CorrectionScriptStyle",
    "CorrectionScriptTheme",
    "CorrectionScriptSpeaker",
    "CorrectionScriptExample",
    "CorrectionScriptGeneratedText",
    "CorrectionScriptInstructionPrompt",
    "CorrectionScriptTrain",
]