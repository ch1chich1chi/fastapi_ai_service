from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str


class ErrorResponse(BaseModel):
    code: int
    message: str
    request_id: str

class ConversationCreate(BaseModel):
    title : str = Field(min_length=1,max_length=100)

class ConversationResponse(BaseModel):
    id : int
    title : str

class ConversationRename(BaseModel):
    title: str = Field(min_length=1, max_length=100)
