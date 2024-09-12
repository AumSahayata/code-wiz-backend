from fastapi import APIRouter, status, HTTPException, Request
from .schemas import QueryModel, AnswerModel
from .services import BotServices
from src.config import Config

bot_router = APIRouter()
bot_service = BotServices(groq_api_key=Config.GROQ_API_KEY, google_api_key=Config.GOOGLE_API_KEY)

@bot_router.post("/ask", response_model=AnswerModel, status_code=status.HTTP_200_OK)
async def query(request: Request, user_query: QueryModel):
    
    token = request.state.token
    
    if token and token.get("type") == "access":
        vector_store = bot_service.load_vector_store("src/vectors")
        response = bot_service.get_answer(user_query.query, vector_store)
        if response:
            return AnswerModel(answer=response)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to get answer. Please try again.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@bot_router.post("/upload")
async def upload_pdf():
    # Generate and save vector store from uploaded PDFs 
    vector_store = bot_service.generate_vector_store()
    bot_service.save_vectors(vector_store, "src/vectors")
    return {"message": "PDFs processed and vectors saved."}