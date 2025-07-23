import pytest
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import IntegrityError

from db import Base, DataBase, Face, Person


def test_should_create_base_table():
    """Verify that the base table ('Person' and 'Face') is created when the class is initialized."""
    db = DataBase("sqlite:///:memory:", Base)
    inspector = Inspector.from_engine(db.engine)
    assert Person.__tablename__ in inspector.get_table_names()
    assert Face.__tablename__ in inspector.get_table_names()


class TestSimpleAddRecord:
    def _expected_error(self, engine):
        engine_name = engine.dialect.name
        if engine_name.lower() == "postgresql":
            from psycopg2.errors import UniqueViolation

            return UniqueViolation
        else:
            return IntegrityError

    def test_should_add_record(self, sample_db):
        with sample_db.get_session() as session:
            session.add(Person(name="John", surname="Doe"))

        with sample_db.get_session() as session:
            assert session.query(Person).count() == 1
            result = session.query(Person).first()

            assert result.name == "John"
            assert result.surname == "Doe"
            assert result.nickname == ""
            assert not result.faces

    def test_should_not_add_duplicate_record(self, sample_db):
        expected_error = self._expected_error(sample_db.engine)

        with sample_db.get_session() as session:
            session.add(Person(name="John", surname="Doe"))

        with pytest.raises(expected_error):
            with sample_db.get_session() as session:
                session.add(Person(name="John", surname="Doe"))

        with sample_db.get_session() as session:
            assert session.query(Person).count() == 1
