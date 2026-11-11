from fastapi import APIRouter

from src.clients.deepseek import DeepSeekClient
from src.config_loader import load_config
from src.schemas import ChatRequest, ChatResponse
from src.services.chat_service import ChatService


router = APIRouter()

config = load_config()
client = DeepSeekClient(
    model=str(config["model"]),
    timeout=int(config["timeout"]),
)
service = ChatService(client)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    answer = service.reply(request.question)
    return ChatResponse(answer=answer)
