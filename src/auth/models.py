from sqlmodel import SQLModel, Field, Column
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg
import uuid
import pyotp

class User(SQLModel, table=True):
    __tablename__ = "users"

    # Unique user ID (Primary Key)
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),  # PostgreSQL UUID type
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )
    )
    first_name: str = Field(nullable=False)    
    last_name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    password_hash: str = Field(nullable=False, exclude=True)
    otp_secret: str = Field(
        default=pyotp.random_base32(),  # Automatically generate a secret key
        nullable=False
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, default=datetime.now)
    )
