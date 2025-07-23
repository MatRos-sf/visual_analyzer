import pytest

from db import Base, DataBase


@pytest.fixture(scope="module")
def sample_db():
    db = DataBase("sqlite:///:memory:", Base)
    return db
