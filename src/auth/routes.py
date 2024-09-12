from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from .schemas import UserLoginModel, UserCreateModel, OTPVerificationModel, EmailSchema
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .models import User
from .services import AuthServices
from datetime import timedelta
from src.config import Config
from .utils import create_token, generate_otp, verify_otp_util, send_email
from fastapi import BackgroundTasks

auth_router = APIRouter()
auth_services = AuthServices()

@auth_router.get("/")
async def test():
    return {"Message":"Hello world"}


@auth_router.post("/login")
async def login(user: UserLoginModel, session: AsyncSession = Depends(get_session), background_tasks: BackgroundTasks = None):
    
    user_in_db = await auth_services.authenticate_user(email=user.email, password=user.password, session=session)
    
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate and send OTP
    otp = generate_otp(user_in_db.otp_secret)
    
    email_data = EmailSchema(
        email=user_in_db.email,
        subject="Login OTP for chatbot",
        body=f"Your login OTP is {otp}.\nThe OTP will expire in 2 minutes."
    )
    
    background_tasks.add_task(send_email, email_data)
    
    otp_token_expires = timedelta(minutes=Config.OTP_TOKEN_EXPIRE_MINUTES)
    otp_token = create_token(
        data={"sub": str(user_in_db.uid)},
        token_type="otp",
        exp_delta=otp_token_expires
    )
    
    return {
        "otp_token": otp_token,
        "token_type": "otp",
    }


@auth_router.get("/resend-otp")
async def resend_otp(request: Request, session: AsyncSession = Depends(get_session), background_tasks: BackgroundTasks = None):
    
    token = request.state.token
    
    if token and token.get("type") == "otp":
        
        user_id = token.get("sub")
        user_in_db = await auth_services.get_user_by_uid(user_id, session=session)
        
        if user_in_db:
            # Generate and send OTP
            otp = generate_otp(user_in_db.otp_secret)
            
            email_data = EmailSchema(
                email=user_in_db.email,
                subject="Login OTP for chatbot",
                body=f"Your login OTP is {otp}.\nThe OTP will expire in 1 minute."
            )
            background_tasks.add_task(send_email, email_data)
            return {
                "message":"success"
            }
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@auth_router.post("/verify-otp")
async def verify_otp(request: Request, data: OTPVerificationModel, session: AsyncSession = Depends(get_session)):
    
    token = request.state.token
    
    if token and token.get("type") == "otp":
        user_id = token.get('sub')
        user_in_db = await auth_services.get_user_by_uid(user_id, session=session)
        
        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        if not verify_otp_util(user_in_db.otp_secret, data.otp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP. Please try again."
            )

        access_token_expires = timedelta(days=Config.ACCESS_TOKEN_EXPIRE_DAYS)
        access_token = create_token(
            data={"sub": str(user_in_db.uid)},
            token_type="access",
            exp_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "access",
        }
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@auth_router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    # token = request.state.token
    
    # if token:
        
    #     admin_uid = token.get("sub")
        
    #     admin = await auth_services.get_user_by_uid(admin_uid, session=session)
    #     role = admin.is_admin
        
    #     if role:
            email = user_data.email

            user_exists = await auth_services.user_exists(email, session)

            if user_exists:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User with email already exists",
                )

            await auth_services.create_user(user_data, session)

            return Response(content="successful", status_code=201)
    #     else:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not admin')
    # else:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)