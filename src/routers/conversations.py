from fastapi import APIRouter,HTTPException, Response

from src.database import connect_database, create_conversation, get_conversation, list_conversations,rename_conversation,delete_conversation
from src.errors import AppError
from src.schemas import ConversationCreate, ConversationResponse,ConversationRename


router = APIRouter()

@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=201,
)
def create_conversation_api(
    request: ConversationCreate,
) -> ConversationResponse:
    if not request.title.strip():
        raise AppError("title 不能为空")

    conn = connect_database()
    try:
        conversation_id = create_conversation(conn, request.title)
    finally:
        conn.close()

    return ConversationResponse(
        id=conversation_id,
        title=request.title,
    )

@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
)
def list_conversations_api() -> list[ConversationResponse]:
    conn = connect_database()
    try:
        rows = list_conversations(conn)
    finally:
        conn.close()

    result = []
    for row in rows:
        result.append(
            ConversationResponse(id=row[0], title=row[1])
        )

    return result

@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation_api(
    conversation_id: int,
) -> ConversationResponse:
    conn = connect_database()
    try:
        row = get_conversation(conn, conversation_id)
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="会话不存在",
        )

    return ConversationResponse(id=row[0], title=row[1])

@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def rename_conversation_api(
    conversation_id: int,
    request: ConversationRename,
) -> ConversationResponse:
    if not request.title.strip():
        raise AppError("title 不能为空")

    conn = connect_database()
    try:
        row = get_conversation(conn, conversation_id)
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="会话不存在",
            )

        rename_conversation(conn, conversation_id, request.title)
    finally:
        conn.close()

    return ConversationResponse(
        id=conversation_id,
        title=request.title,
    )

@router.delete(
    "/conversations/{conversation_id}",
    status_code=204,
)
def delete_conversation_api(conversation_id: int) -> Response:
    conn = connect_database()
    try:
        row = get_conversation(conn, conversation_id)
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="会话不存在",
            )

        delete_conversation(conn, conversation_id)
    finally:
        conn.close()

    return Response(status_code=204)