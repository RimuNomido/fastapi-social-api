from src.database import async_session_maker
from src.models import User, Post, Comment
from src.security import verify_password, hash_password
from sqlalchemy import select, update, delete
from typing import List

async def db_create_user(name: str, email: str, password: str) -> User:
    async with async_session_maker() as session:
        hashed_password = hash_password(password)
        user = User(name=name, email=email, password_hash=hashed_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def db_get_users_by_name(name: str) -> List[User]:
    async with async_session_maker() as session:
        result = await session.scalars(select(User).where(User.name==name))
        return result.all()

async def db_login_user(email: str, password: str) -> User | None:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.email==email))
        if user is None:
            return None
        if verify_password(password, user.password_hash):
            return user
        else:
            return None

async def db_create_post(user_id: int, title: str, description: str | None = '') -> Post:
    async with async_session_maker() as session:
        if description is None:
            description = ''
        post = Post(author_id=user_id, description=description, title=title)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

async def db_get_posts_by_title(title: str) -> List[Post]:
    async with async_session_maker() as session:
        result = await session.scalars(select(Post).where(Post.title == title))
        return result.all()

async def db_create_comment(post_id: int, user_id: int, description: str) -> Comment:
    async with async_session_maker() as session:
        comment = Comment(post_id=post_id, user_id=user_id, description=description)
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

async def db_get_post_comments(post_id: int) -> List[Comment]:
    async with async_session_maker() as session:
        result = await session.scalars(select(Comment).where(Comment.post_id == post_id))
        return result.all()