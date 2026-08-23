from fastapi import FastAPI, Query, HTTPException, status
from src.crud import db_create_user, db_get_users_by_name, db_create_post, db_get_posts_by_title, db_create_comment, db_get_post_comments
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=24)
    email: EmailStr = Field(..., min_length=5, max_length=24)
    password: str = Field(..., min_length=8, max_length=36)

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    user_id: int
    title: str = Field(..., min_length=4, max_length=200)
    description: str | None = Field(default=None, max_length=5000)

class CommentCreate(BaseModel):
    user_id: int
    post_id: int
    description: str = Field(..., min_length=1, max_length=2000)

app = FastAPI()

@app.post("/create_user", response_model=UserOut)
async def create_user(user_data: UserCreate):
    created_user = await db_create_user(name=user_data.name, email=user_data.email, password=user_data.password)
    if created_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return created_user

@app.get("/search/users")
async def search_users(name: str | None = Query(default=None, min_length=1, max_length=24,description="Search users")):
    if name:
        users = await db_get_users_by_name(name)
        return users
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post('/create_post')
async def create_post(post_data: PostCreate):
    created_post = await db_create_post(user_id=post_data.user_id, title=post_data.title, description=post_data.description)
    if created_post is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return created_post

@app.get('/search/posts')
async def search_posts(title: str | None = Query(default=None, min_length=4, max_length=200, description="Search posts")):
    if title:
        posts = await db_get_posts_by_title(title)
        return posts
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post('/comments')
async def create_comment(comment_data: CommentCreate):
    created_comment = await db_create_comment(user_id=comment_data.user_id, post_id=comment_data.post_id, description=comment_data.description)
    if created_comment is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return created_comment

@app.get('/comments')
async def get_comments(post_id: int):
    comments = await db_get_post_comments(post_id)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return comments