# base.py
from sqlalchemy import MetaData, event
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import CreateSchema

# 모든 스키마에 동일하게 사용되는 base model입니다.
metadata = MetaData()
Base = declarative_base(metadata=metadata)

event.listen(
    Base.metadata,
    'before_create',
    CreateSchema('text_repository', if_not_exists=True)
)
event.listen(
    Base.metadata,
    'before_create',
    CreateSchema('correction_script', if_not_exists=True)
)