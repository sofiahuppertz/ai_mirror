from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
import csv

Base = declarative_base()

class Page(Base):
    __tablename__ = 'pages_table'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    image = Column(LargeBinary)

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

    def __init__(self, name):
        self.name = name

    def set_occupation(self, occupation):
        self.occupation = occupation
    
    def set_email(self, email):
        self.email = email



class Question(Base):
    __tablename__ = 'questions_table'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    person_id = Column(Integer, ForeignKey('people_table.id'))

    def __init__(self, question, person_id):
        self.question = question
        self.answer = None
        self.person_id = person_id

    def change_person_id(self, new_id):
        self.person_id = new_id
    
    def add_answer(self, answer):
        self.answer = answer


class Answer(Base):
    __tablename__ = 'answers_table'

    id = Column(Integer, primary_key=True)
    answer = Column(String)
    person_id = Column(Integer, ForeignKey('people_table.id'))
    page_id = Column(Integer, ForeignKey('pages_table.id'))

    def __init__(self, answer, person_id, page_id):
        self.answer = answer
        self.person_id = person_id
        self.page_id = page_id
    
    def change_person_id(self, new_id):
        self.person_id = new_id


def init_db(engine):
    Base.metadata.create_all(engine)