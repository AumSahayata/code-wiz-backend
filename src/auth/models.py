from sqlmodel import SQLModel, Field, Column, CHAR, DATETIME, BOOLEAN
from datetime import datetime
import uuid
import pyotp

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(CHAR(36), primary_key=True))
    first_name: str = Field(nullable=False)    
    last_name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    password_hash: str = Field(nullable=False, exclude=True)
    otp_secret: str = Field(
        default=pyotp.random_base32(),  # Automatically generate a secret key
        nullable=False
    )
    is_admin: bool = Field(default=False, sa_column=Column(BOOLEAN, nullable=False))
    created_at: datetime = Field(
        sa_column=Column("created_at", DATETIME(6), nullable=False, default=datetime.now)
    )
