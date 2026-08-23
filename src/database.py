from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

DB_URL = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

engine = create_async_engine(DB_URL, echo=False)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)