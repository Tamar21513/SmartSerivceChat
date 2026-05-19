from fastapi import APIRouter
from pydantic import BaseModel
import sys
import os

from ConnectedWithReactAndC.SharedDataStructure import tree_things

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from MessageHandling import message_handling


router = APIRouter()


class ChatMessageRequest(BaseModel):
    userId: int
    message: str


@router.post("/chat-message")
def receive_chat_message(data: ChatMessageRequest):
    message = data.message.strip()

    if message == "":
        return {
            "success": False,
            "answer": ""
        }

    print("User ID:", data.userId)
    print("Message:", message)


    try:
        answer = message_handling(message)

        if answer is None:
            answer = "I could not build an answer for this message."
        else:
            print()
            print()
            print()
            print()
            print(answer)

        return {
            "success": True,
            "answer": answer
        }

    except Exception as error:
        print("Chat message handling error:", error)

        return {
            "success": False,
            "answer": "An error occurred while processing your message."
        }