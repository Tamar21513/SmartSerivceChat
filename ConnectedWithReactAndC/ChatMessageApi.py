from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Any
import sys
import os
import traceback
import urllib.request
import urllib.error
import json

from BinarySearchTree import BinarySearchTree

from ConnectedWithReactAndC.SharedDataStructure import (
    add_question_answer_to_dic,
    get_chat_messages,
    get_chat,
    dic_question_answer,
    delete_user_chats_from_dic,
    extract_topics_section_from_report
)

print("!!!!!!!! LOADED ChatMessageApi.py FROM:", __file__, flush=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from MessageHandling import message_handling


router = APIRouter()

# כתובת שרת ה־C# ששומר בפועל את השיחות והדוחות ל־SQL
CSHARP_API_BASE_URL = "http://localhost:5199"


# מודל בקשה עבור הודעת צ'אט חדשה שמגיעה מ־React.
# כל הודעה כוללת את פרטי המשתמש, מזהה השיחה, מזהה הדוח אם קיים, ואת ההודעה עצמה.
class ChatMessageRequest(BaseModel):
    userId: int
    chatId: str
    reportId: Optional[int] = None
    nameUser: str
    email: str
    city: str
    age: int
    occupation: str
    role: str
    message: str


# מודל של שיחה אחת שמגיעה מ־React לסנכרון מול Python.
# השיחה כוללת את מזהה השיחה, הדוח, הכותרת, האם השתנתה, ההודעות, ותוכן הדוח מה־SQL.
class SyncChatItem(BaseModel):
    chatId: str
    reportId: Optional[int] = None
    title: Optional[str] = "New conversation"
    isChanged: bool = False
    conversation: List[str] = []
    reportContent: Optional[str] = ""


# מודל בקשה לסנכרון כמה שיחות של משתמש אחד.
# React שולח רשימת שיחות, ו־Python מכניס אותן למילון הפנימי.
class SyncChatsRequest(BaseModel):
    userId: int
    chats: List[SyncChatItem]


# מודל בקשה לשמירת שיחה אחת אם היא השתנתה.
# משמש כשעוברים בין שיחות, פותחים שיחה חדשה, או יוצאים מהמערכת.
class SaveChatIfChangedRequest(BaseModel):
    userId: int
    chatId: str
    reportId: Optional[int] = None
    title: Optional[str] = "New conversation"
    conversation: List[str] = []


# מודל בקשה למחיקת כל השיחות של משתמש מהמילון של Python.
# משמש בדרך כלל אחרי Logout, אחרי שהשיחות נשמרו ל־SQL.
class ClearUserChatsRequest(BaseModel):
    userId: int


# מודל גמיש לקבלת ThingsTheUserHas אם React עדיין מזמן את הנתיב הזה.
# Any מאפשר לקבל מבנים שונים בלי לגרום לשגיאת ולידציה.
class SyncThingsRequest(BaseModel):
    userId: int
    things: Any = None


# יוצר מבנה פנימי חדש של שיחה בתוך המילון dic_question_answer.
# לכל שיחה נשמרים פרטי המשתמש, מזהה השיחה, מזהה הדוח, ההודעות, מצב שינוי,
# וגם עץ נושאים ריק שבו יישמרו topics שהוצאו מתוך reportContent.
def create_chat_structure(
    user_id: int,
    chat_id: str,
    report_id: Optional[int],
    title: str,
    conversation: List[str],
    is_changed: bool
):
    return {
        "user_id": user_id,
        "chat_id": str(chat_id),
        "report_id": report_id,
        "title": title or "New conversation",
        "messages": conversation or [],
        "is_changed": is_changed,
        "topics_tree": BinarySearchTree()
    }


# בונה עץ נושאים לשיחה אחת לפי תוכן הדוח שנשמר ב־SQL.
# הפונקציה בודקת שיש reportContent,
# בודקת שהשיחה קיימת במילון,
# מוודאת שיש לה topics_tree,
# ואז מזמנת את extract_topics_section_from_report שמחלצת את Topics in report ובונה את העץ.
def build_topics_tree_for_chat(chat_id: str, report_content: Optional[str]):
    chat_id = str(chat_id)

    if not report_content:
        return

    if chat_id not in dic_question_answer:
        return

    if (
        "topics_tree" not in dic_question_answer[chat_id]
        or dic_question_answer[chat_id]["topics_tree"] is None
    ):
        dic_question_answer[chat_id]["topics_tree"] = BinarySearchTree()

    extract_topics_section_from_report(
        report_content=report_content,
        chat_id=chat_id
    )


# שולח בקשת POST מ־Python אל שרת ה־C#.
# משמש לשמירת שיחה/דוח ב־SQL דרך ה־API של C#.
# אם C# מחזיר JSON, הפונקציה מחזירה אותו כ־dict.
def make_csharp_post_request(url: str, body: dict):
    data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            response_text = response.read().decode("utf-8")

            if response_text:
                return json.loads(response_text)

            return {}

    except urllib.error.HTTPError as error:
        error_text = error.read().decode("utf-8")
        print("C# HTTP error:", error.code, error_text)
        raise Exception(error_text)

    except Exception as error:
        print("C# request error:", error)
        raise


#שמירת השיחה+נושאי שיחה ב SQL
def save_chat_to_csharp(user_id: int, chat_id: str):
    chat_id = str(chat_id)

    if chat_id not in dic_question_answer:
        return {
            "success": False,
            "message": "Chat was not found in Python."
        }

    #הצאט הנוכחי
    chat = dic_question_answer[chat_id]

    #לא נעשה שינוי בשיחה - לא שומרים מחדש
    if not chat.get("is_changed", False):
        return {
            "success": True,
            "message": "Chat was not changed. No save needed.",
            "reportId": chat.get("report_id")
        }

    #רשימת השאלה-תשובה
    messages = chat.get("messages", [])

    # בדיקה שהלקוח שאל שאלה וזה לא צאט ריק - רק עם הודעת פתיחת הצאט
    has_user_message = any(
        isinstance(message, str) and message.strip().startswith("User:")
        for message in messages
    )

    if not has_user_message:
        return {
            "success": True,
            "message": "Chat has no real user message. No save needed.",
            "reportId": chat.get("report_id")
        }

    #סיכום השיחה
    conversation_for_save = list(messages)

    topics_tree = chat.get("topics_tree")
    topics_text = ""
    #הפיכת עץ נושיא השיחה לטקסט
    if topics_tree is not None and topics_tree.Root is not None:
        topics_text = topics_tree.tree_to_str()

    #הוספת כותרת
    conversation_for_save.append("")
    conversation_for_save.append("Topics in report:")

    if topics_text.strip() != "":
        conversation_for_save.extend(topics_text.splitlines())

    #הוספת רגשות
    conversation_for_save.append("Sentiment and Emotions:")
    conversation_for_save.append("Sentiment: Neutral")
    conversation_for_save.append("Emotions detected: Neutral")

    #גוף שליחת הAPI
    body = {
        "userId": user_id,
        "reportId": chat.get("report_id"),
        "conversation": conversation_for_save
    }

    #שליחת השיחה
    saved_data = make_csharp_post_request(
        f"{CSHARP_API_BASE_URL}/api/reports/save-chat",
        body
    )

    if "reportId" in saved_data:
        chat["report_id"] = saved_data["reportId"]

    chat["is_changed"] = False

    return saved_data


# React מזמן את הפונקציה הזאת אחרי טעינת השיחות מה־SQL.
# כאן Python מקבל את כל השיחות של המשתמש,
# מכניס כל שיחה למילון dic_question_answer,
# יוצר לכל שיחה topics_tree חדש,
# ואם יש reportContent — בונה ממנו את עץ הנושאים.
@router.post("/sync-chats")
def sync_chats(data: SyncChatsRequest):
    try:
        for chat in data.chats:
            chat_id = str(chat.chatId)

            dic_question_answer[chat_id] = create_chat_structure(
                user_id=data.userId,
                chat_id=chat.chatId,
                report_id=chat.reportId,
                title=chat.title or "New conversation",
                conversation=chat.conversation,
                is_changed=chat.isChanged
            )
            build_topics_tree_for_chat(
                chat_id=chat_id,
                report_content=chat.reportContent
                
            )

        return {
            "success": True,
            "message": "Chats synced to Python successfully.",
            "count": len(data.chats)
        }

    except Exception as error:
        print("Sync chats error:", error, flush=True)
        traceback.print_exc()

        return {
            "success": False,
            "message": "Failed to sync chats to Python."
        }


# React מזמן את הפונקציה הזאת במעבר שיחה, פתיחת שיחה חדשה, או יציאה.
# Python מעדכן את השיחה במילון,
# מסמן אותה כמשתנה,
# ואז מזמן את save_chat_to_csharp כדי לשמור ב־SQL רק אם באמת צריך.
@router.post("/save-chat-if-changed")
# פונקציה לסיום שיחה ושליחת הדו"ח לשרת C#
def save_chat_if_changed(data: SaveChatIfChangedRequest):
    try:
        chat_id = str(data.chatId)
        #אם השיחת נ=הצאט לא קיימת במילון
        if chat_id not in dic_question_answer:
            dic_question_answer[chat_id] = create_chat_structure(user_id=data.userId, chat_id=data.chatId, report_id=data.reportId, title=data.title or "New conversation", conversation=data.conversation, is_changed=True)
        else:
            chat = dic_question_answer[chat_id]
            chat["user_id"] = data.userId
            chat["report_id"] = data.reportId
            chat["title"] = data.title or chat.get("title", "New conversation")
            chat["messages"] = data.conversation
            chat["is_changed"] = True

            #אם לא קיים עץ נושאי שיחה
            if ("topics_tree" not in chat or chat["topics_tree"] is None):
                chat["topics_tree"] = BinarySearchTree()

        saved_data = save_chat_to_csharp(data.userId, chat_id)

        return saved_data

    except Exception as error:
        print("Save chat if changed error:", error)
        traceback.print_exc()

        return {
            "success": False,
            "message": "Failed to save chat."
        }


# React מזמן את הפונקציה הזאת אחרי Logout.
# אחרי שהשיחות נשמרו ב־SQL, Python מוחק מהמילון את כל השיחות של אותו משתמש.
# זה מונע מצב שבו משתמשים שונים יראו בטעות מידע שנשאר בזיכרון.
@router.post("/clear-user-chats")
def clear_user_chats(data: ClearUserChatsRequest):
    try:
        deleted_count = delete_user_chats_from_dic(data.userId)

        print("User chats deleted from Python dictionary")
        print("User ID:", data.userId)
        print("Deleted chats:", deleted_count)

        return {
            "success": True,
            "message": "User chats deleted from Python dictionary.",
            "deletedCount": deleted_count
        }

    except Exception as error:
        print("Clear user chats error:", error)
        traceback.print_exc()

        return {
            "success": False,
            "message": "Failed to delete user chats from Python dictionary."
        }


# פונקציה זמנית לקבלת ThingsTheUserHas מ־React.
# אם אצלך השמירה של הדברים שיש למשתמש כבר מתבצעת דרך C# או דרך עץ הנושאים,
# אפשר להשאיר את הנתיב הזה רק לצורך תאימות לאחור.
@router.post("/sync-things-the-user-has")
def sync_things_the_user_has(data: SyncThingsRequest):
    print("ThingsTheUserHas received in Python")
    print("User ID:", data.userId)
    print("Things:", data.things)

    return {
        "success": True,
        "message": "ThingsTheUserHas synced to Python."
    }


# React מזמן את הפונקציה הזאת בכל פעם שהלקוח שולח הודעה בצ'אט.
# הפעולות:
# 1. בדיקה שההודעה לא ריקה.
# 2. בניית user_data.
# 3. יצירת שיחה במילון אם היא לא קיימת.
# 4. הוספת הודעת User למילון.
# 5. שליחת ההודעה ל־message_handling.
# 6. הוספת תשובת Bot למילון.
# 7. החזרת התשובה והודעות השיחה ל־React.
@router.post("/chat-message")
#קבלת הודעה מצד לקוח
def receive_chat_message(data: ChatMessageRequest):
    message = data.message.strip()
    #אם הודעה ריקה
    if message == "":
        return {
            "success": False,
            "answer": "",
            "chatId": data.chatId,
            "messages": get_chat_messages(data.chatId)
        }
    
    user_data = {
        "userId": data.userId,
        "username": data.nameUser,
        "email": data.email,
        "city": data.city,
        "age": data.age,
        "occupation": data.occupation,
        "role": data.role
    }

    chat_id = str(data.chatId)
    #אם צאט זה לא קיים במילון שאלה-תשובה
    if chat_id not in dic_question_answer:
        #הוספת השיחה למילון
        dic_question_answer[chat_id] = create_chat_structure(
            user_id=data.userId,
            chat_id=data.chatId,
            report_id=data.reportId,
            title="New conversation",
            conversation=[],
            is_changed=False
        )

    #עדכון פרטי משתמש
    dic_question_answer[chat_id]["user_id"] = data.userId
    dic_question_answer[chat_id]["report_id"] = data.reportId
    #אם לא קיים מצביע לעץ חיפוש בנארי - לנושאי השיחה
    if ("topics_tree" not in dic_question_answer[chat_id] or dic_question_answer[chat_id]["topics_tree"] is None):
        dic_question_answer[chat_id]["topics_tree"] = BinarySearchTree()

    # הוספת הודעה למילון שיחות נוכחיות
    add_question_answer_to_dic(chat_id, "User: " + message)

    print("User ID:", data.userId)
    print("Chat ID:", data.chatId)
    print("Report ID:", data.reportId)
    print("Message:", message)
    print("User data:", user_data)

    try:
        #פרטי שיחה נוכחית
        chat_history = get_chat(chat_id)
        #זימון פונקצית טיפול בהודעה
        answer = message_handling(message, user_data, chat_history)
        #אם ההודעה הינה None - מודפס
        if answer is None:
            answer = "I could not build an answer for this message."
        else:
            print()
            print(answer)

        #הוספת התשובה למילון על פי קוד צאט
        add_question_answer_to_dic(chat_id, "Bot: " + answer)

        return {
            "success": True,
            "answer": answer,
            "chatId": chat_id,
            "reportId": dic_question_answer[chat_id].get("report_id"),
            "messages": get_chat_messages(chat_id)
        }

    except Exception as error:
        print("Chat message handling error:", error)
        traceback.print_exc()

        return {
            "success": False,
            "answer": "An error occurred while processing your message.",
            "chatId": chat_id,
            "reportId": dic_question_answer[chat_id].get("report_id"),
            "messages": get_chat_messages(chat_id)
        }