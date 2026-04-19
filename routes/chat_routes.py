from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ai_rag.rag_agent import agent
from utils.auth_util import get_current_user

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    thread_id: str = "1"


@router.post("/query")
def chat_query(
    request: QueryRequest,
    current_user=Depends(get_current_user),
):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}

        result = agent.invoke(
            {"messages": [("user", request.query)]},
            config
        )

        last_message = result["messages"][-1]

        # content list bhi ho sakta hai ya string bhi
        content = last_message.content

        # agar list hai → text extract karo
        if isinstance(content, list):
            text_output = " ".join(
                block["text"] for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            text_output = content  # already string hai

        return {
            "output": text_output,
            "thread_id": request.thread_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )