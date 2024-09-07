from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from .auth.routes import auth_router
from .bot.routes import bot_router
from src.auth.utils import decode_token

app = FastAPI(title="Chatbot")

EXCLUDED_PATHS = ["/api/auth/login"]

@app.middleware("http")
async def check_token(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("JWT "):
        token = auth_header.split(" ")[1]
        try:
            token_data = decode_token(token)
            if token_data.get("type") == "access" or token_data.get("type") == "otp":
                request.state.token = token_data
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid authentication credentials"},
            headers={"WWW-Authenticate": "JWT"},
        )
    response = await call_next(request)
    return response 

app.include_router(auth_router, prefix="/api/auth")
app.include_router(bot_router, prefix="/api/bot")