from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))
    nickname = Column(
        String(50),
        doc="This field is optional when name and surname are exists in the database.",
        default="",
    )

    faces = relationship("Face", back_populates="person")

    __table_args__ = (
        UniqueConstraint("name", "surname", "nickname", name="person_repr"),
    )

    def __repr__(self):
        return f"<Person(name={self.name}, surname={self.surname}, nickname={self.nickname})>"


class Face(Base):
    __tablename__ = "face"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    media_type = Column(String(50))
    media_original_path = Column(String(500))
    media_re_path = Column(
        String(250),
        doc="Short relative path to media_original_path. Used to located the file after media is moved to a new root directory.",
    )
    encoding = Column(LargeBinary, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    person = relationship("Person", back_populates="faces")
