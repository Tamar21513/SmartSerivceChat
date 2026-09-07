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
# פונקציה לסיום שיחה ושליחת הדו"ח לשרת C#
def finish_conversation(data: FinishConversationRequest):
    # בדיקה אם קיימות הודעות לשמירה
    if len(dic_question_answer[data.userId]) <= 1:
        return {
            "success": True,
            "message": "No conversation to send."
        }
    # בניית גוף הבקשה לשליחה לשרת C#
    payload = {
        "userId": data.userId,
        "conversation": dic_question_answer[data.userId]
    }

    try:
        # שליחת השיחה לשרת C# לצורך שמירה במסד הנתונים
        response = requests.post(
            f"{settings['CSHARP_API_BASE_URL']}/api/reports/from-python",
            json=payload,
            timeout=10
        )
        # טיפול במקרה שבו שרת C# לא שמר את השיחה
        if not response.ok:
            print("C# save error:", response.status_code, response.text)
            return {
                "success": False,
                "message": "C# did not save the conversation."
            }
        
        # ניקוי רשימת השיחה לאחר שמירה מוצלחת
        dic_question_answer[data.userId].clear()
        # החזרת תשובה על הצלחת השמירה
        return {
            "success": True,
            "message": "Conversation sent to C# successfully."
        }

    except Exception as error:
        # טיפול בשגיאת תקשורת או שגיאה כללית בשליחה
        print("Error sending conversation to C#:", error)

        return {
            "success": False,
            "message": "Could not send conversation to C#."
        }