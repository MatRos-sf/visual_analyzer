from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker


class DataBase:
    def __init__(self, database_url, base_model: Any, echo: bool = False):
        self.engine = create_engine(database_url, echo=echo)
        self.session = sessionmaker(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # init db
        base_model.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> SessionType:
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
