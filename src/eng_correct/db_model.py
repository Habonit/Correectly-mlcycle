from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from dotenv import load_dotenv
import os

Base = declarative_base()

class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)

class InstructionPrompt(Base):
    __tablename__ = 'instruction_prompt'
    id = Column(Integer, primary_key=True)
    instruction_prompt = Column(Text, nullable=False)

class SystemPrompt(Base):
    __tablename__ = 'system_prompt'
    id = Column(Integer, primary_key=True)
    system_prompt = Column(Text, nullable=False)
    
class GenerationPrompt(Base):
    __tablename__ = 'generation_prompt'
    id = Column(Integer, primary_key=True)
    context_prompt = Column(Text, nullable=False)
    example_prompt = Column(Text, nullable=False)  

class TaskInstructionMap(Base):
    __tablename__ = 'task_instruction_map'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    instruction_prompt_id = Column(Integer, ForeignKey('instruction_prompt.id'), nullable=False)

    task = relationship("Task")
    instruction_prompt = relationship("InstructionPrompt")
        
class TaskGenerationMap(Base):
    __tablename__ = 'task_generation_map'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    generation_prompt_id = Column(Integer, ForeignKey('generation_prompt.id'), nullable=False)

    task = relationship("Task")
    generation_prompt = relationship("GenerationPrompt")

class Train(Base):
    __tablename__ = 'train'
    id = Column(Integer, primary_key=True)
    task_instruction_map_id = Column(Integer, ForeignKey('task_instruction_map.id'), nullable=False)
    system_prompt_id = Column(Integer, ForeignKey('system_prompt.id'))
    context = Column(Text, nullable=False)
    example = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    task_instruction_map = relationship("TaskInstructionMap")
    system_prompt = relationship("SystemPrompt")

# TODO: FIXIT
# 환경변수 로드 
# load_dotenv(dotenv_path="/usr/local/project/postgres/.env")
# load_dotenv(dotenv_path="/usr/local/project/src/eng_correct/.env")
load_dotenv()

ENG_DB_NAME = os.environ["ENG_DB_NAME"]
ENG_DB_USER = os.environ["ENG_DB_USER"]
ENG_DB_PASSWORD = os.environ["ENG_DB_PASSWORD"]
POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]

DATABASE_URL = f"postgresql+psycopg2://{ENG_DB_USER}:{ENG_DB_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{ENG_DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)