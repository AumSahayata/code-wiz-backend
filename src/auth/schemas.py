from pydantic import BaseModel, Field

class UserLoginModel(BaseModel):
    email: str
    password: str = Field(min_length=6)
    
class UserCreateModel(BaseModel):
    
    first_name: str = Field(max_length=15)
    last_name: str = Field(max_length=15)
    email: str
    password: str = Field(min_length=6)

class EmailSchema(BaseModel):
    email: str
    subject: str
    body: str

class OTPVerificationModel(BaseModel):
    otp: str

class TokenData(BaseModel):
    uid: str