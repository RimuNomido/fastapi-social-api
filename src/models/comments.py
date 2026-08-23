from src.models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    description = Column(String, nullable=False)

    author = relationship("User", back_populates="comments")
