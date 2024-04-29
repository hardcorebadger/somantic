from sqlalchemy import Column, Integer, String, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from .embeddings import EmbeddingsClient

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String)
    role = Column(Enum('user', 'assistant', 'function', name='role_enum'))
    function_name = Column(String)
    conversation = Column(String)
    embedding = Column(Vector(1536))

    def __repr__(self):
        return f"<Message({self.role=}, {self.function_name=}, {self.message=}, {self.conversation=})>"
    