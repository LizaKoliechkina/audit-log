from enum import Enum, auto
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class LogLevel(str, Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class EventType(str, Enum):
    WRITE = auto()
    READ = auto()


class Event(str, Enum):
    # Add below all functionalities (endpoints) needed to be recorded in logs
    POST_FILTERED_REFERENCES = auto()
    POST_AGGREGATED_KPIS = auto()
    GET_COUNTRIES = auto()
    GET_FILTERS = auto()
    GET_GRAPH_SETTINGS = auto()
    POST_SET_PRICE = auto()
    POST_RESET_TO_DEFAULTS = auto()
    GET_DOWNLOAD_COUNTRY_DATA = auto()
    POST_POTENTIAL = auto()


def generate_uuid() -> str:
    return uuid4().hex


class LogEntry(Base):
    __tablename__ = 'log_entry'

    id = sa.Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=generate_uuid)
    user_id = sa.Column(sa.String(128), nullable=False)
    user_name = sa.Column(sa.String(128), nullable=False)
    log_level = sa.Column(sa.Enum(LogLevel))
    event = sa.Column(sa.Enum(Event))
    event_type = sa.Column(sa.Enum(EventType))
    message = sa.Column(sa.String(1000))
    created_at = sa.Column(sa.DateTime(), nullable=False, default=sa.func.now())
