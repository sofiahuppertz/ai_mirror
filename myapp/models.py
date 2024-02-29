from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Page(Base):
    __tablename__ = 'pages_table'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)

    new_answers = relationship("Answer", backref="page")
   
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


class Person(Base):
    __tablename__ = 'people_table'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    occupation = Column(String)
    email = Column(String)

    questions = relationship("Question", backref="person")

    def __init__(self, name, occupation, email):
        self.name = name
        self.occupation = occupation
        self.email = email


class Question(Base):
    __tablename__ = 'questions_table'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    person_id = Column(Integer, ForeignKey('people_table.id'))

    def __init__(self, question, person_id):
        self.question = question
        self.person_id = person_id


class Answer(Base):
    __tablename__ = 'answers_table'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    ansswer = Column(String)
    person_id = Column(Integer, ForeignKey('people_table.id'))
    book_id = Column(Integer, ForeignKey('pages_table.id'))

def init_db(engine):
    Base.metadata.create_all(engine)