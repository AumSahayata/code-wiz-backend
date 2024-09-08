from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config

engine = AsyncEngine(
    create_engine(
        url = Config.DATABASE_URL,
        echo = True,
        pool_size=10,          # Maximum number of connections in the pool
        max_overflow=5,         # Number of additional connections beyond pool_size
        pool_timeout=30,        # Time to wait before timing out when all connections are in use
        pool_recycle=1800
    )
)

async def get_session() -> AsyncSession:
    
    Session = sessionmaker(
        bind = engine,
        class_= AsyncSession,
        expire_on_commit = False 
    )
    
    async with Session() as session:
        yield session