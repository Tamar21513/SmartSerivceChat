from fastapi import APIRouter
from pydantic import BaseModel
import requests

from ConnectedWithReactAndC.SharedDataStructure import dic_question_answer
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()



router = APIRouter()



class FinishConversationRequest(BaseModel):
    userId: int


@router.post("/finish-conversation")
# End a conversation by sending its full Q&A history to the C# server for storage, then clear it locally
def finish_conversation(data: FinishConversationRequest):
    if len(dic_question_answer[data.userId]) <= 1:
        return {
            "success": True,
            "message": "No conversation to send."
        }
    payload = {
        "userId": data.userId,
        "conversation": dic_question_answer[data.userId]
    }

    try:
        response = requests.post(
            f"{settings['CSHARP_API_BASE_URL']}/api/reports/from-python",
            json=payload,
            timeout=10
        )
        if not response.ok:
            print("C# save error:", response.status_code, response.text)
            return {
                "success": False,
                "message": "C# did not save the conversation."
            }

        dic_question_answer[data.userId].clear()
        return {
            "success": True,
            "message": "Conversation sent to C# successfully."
        }

    except Exception as error:
        print("Error sending conversation to C#:", error)

        return {
            "success": False,
            "message": "Could not send conversation to C#."
        }