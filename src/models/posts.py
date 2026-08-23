from src.models.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    author = relationship("User", back_populates="posts")