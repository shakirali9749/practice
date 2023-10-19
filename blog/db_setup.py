from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    subject = Column(String(250), nullable=False)
    post = Column(String(250), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow)

    def as_dict(self):
       return {
           'subject': self.subject,
           'content': self.post,
       }


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    email = Column(String(120), nullable=True)


engine = create_engine('sqlite:///blog.db')
Base.metadata.create_all(engine)
