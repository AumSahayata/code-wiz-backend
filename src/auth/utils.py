from src.config import Config
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
import pyotp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .schemas import EmailSchema
from fastapi import HTTPException, status

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
OTP_EXPIRE = Config.OTP_EXPIRE_TIME_SECONDS


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    
    return hash

def verify_password(password: str, hash: str) -> bool:
    
    return password_context.verify(password, hash)

def create_token(data: dict, token_type: str, exp_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + exp_delta
    
    to_encode.update({"type": token_type, "exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_otp(secret: str):
    totp = pyotp.TOTP(secret, interval=OTP_EXPIRE)
    return totp.now()

def verify_otp_util(secret: str, otp: str) -> bool:
    totp = pyotp.TOTP(secret, interval=OTP_EXPIRE)
    return totp.verify(otp)

def send_email(email_data: EmailSchema):
    
    sender_email = str(Config.EMAIL_ID)
    password = str(Config.EMAIL_PASSWORD)
    
    receiver_email = email_data.email
    subject = email_data.subject
    body = email_data.body

    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()

    try:
        smtp_server.login(sender_email, password)
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))
        smtp_server.sendmail(sender_email, receiver_email, message.as_string())
        smtp_server.quit()
        return {"message": "Email sent successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get('sub')
        
        if uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "JWT"},
            )
        return payload
    
    except jwt.PyJWTError:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "JWT"},
            )