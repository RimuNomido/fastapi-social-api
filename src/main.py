from fastapi import FastAPI, Query, HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from src.exceptions import UserAlreadyExists
from src.security import create_access_token, decode_access_token
from src.models import User
from src.crud import db_create_user, db_get_user_by_id, db_get_users_by_name, db_create_post, db_get_posts_by_title, db_create_comment, db_get_post_comments, db_login_user
from pydantic import BaseModel, Field, EmailStr

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=24)
    email: EmailStr = Field(..., min_length=5, max_length=24)
    password: str = Field(..., min_length=8, max_length=36)

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str = Field(..., min_length=8, max_length=36)

class PostCreate(BaseModel):
    title: str = Field(..., min_length=4, max_length=200)
    description: str | None = Field(default=None, max_length=5000)

class CommentCreate(BaseModel):
    post_id: int
    description: str = Field(..., min_length=1, max_length=2000)

app = FastAPI()

@app.exception_handler(UserAlreadyExists)
async def user_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": 'Пользователь с таким email уже зарегистрирован'})

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db_get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

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
async def create_post(post_data: PostCreate, user: User = Depends(get_current_user)):
    created_post = await db_create_post(user_id=user.id, title=post_data.title, description=post_data.description)
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
async def create_comment(comment_data: CommentCreate, user: User = Depends(get_current_user)):
    created_comment = await db_create_comment(user_id=user.id, post_id=comment_data.post_id, description=comment_data.description)
    if created_comment is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return created_comment

@app.get('/comments')
async def get_comments(post_id: int):
    comments = await db_get_post_comments(post_id)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return comments

@app.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = await db_login_user(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = create_access_token(user.id)
    return {'access_token': token}