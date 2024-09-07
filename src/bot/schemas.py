from pydantic import BaseModel, Field

class QueryModel(BaseModel):
    query: str
    
class AnswerModel(BaseModel):
    answer: str