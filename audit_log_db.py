from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from patterns import SingletonMeta

Base = declarative_base()


def get_audit_log_db():
    db = AuditLogDatabase().get_session_local()
    try:
        yield db
    finally:
        db.close()


class AuditLogDatabase(metaclass=SingletonMeta):
    def __init__(self, db_url=None):
        if db_url: self.db_url = db_url
        self.engine = create_engine(db_url)
        self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session_local(self):
        return self.session_local()

    def dispose(self):
        self.engine.dispose()
