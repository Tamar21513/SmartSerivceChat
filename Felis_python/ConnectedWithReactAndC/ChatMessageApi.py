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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from MessageHandling import message_handling


router = APIRouter()

CSHARP_API_BASE_URL = "http://localhost:5199"


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


class SyncChatItem(BaseModel):
    chatId: str
    reportId: Optional[int] = None
    title: Optional[str] = "New conversation"
    isChanged: bool = False
    conversation: List[str] = []
    reportContent: Optional[str] = ""


class SyncChatsRequest(BaseModel):
    userId: int
    chats: List[SyncChatItem]


class SaveChatIfChangedRequest(BaseModel):
    userId: int
    chatId: str
    reportId: Optional[int] = None
    title: Optional[str] = "New conversation"
    conversation: List[str] = []


class ClearUserChatsRequest(BaseModel):
    userId: int


class SyncThingsRequest(BaseModel):
    userId: int
    things: Any = None


# Build a fresh in-memory chat entry (user info, messages, changed flag, empty topics tree) for dic_question_answer
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


# Build the topics tree for a chat from its saved report content, if the chat exists and has report content
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


# Send a POST request with a JSON body to the C# server and return its parsed JSON response
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


# Save a chat's messages and topics tree to the C# server, skipping the save if nothing changed or no real user message exists
def save_chat_to_csharp(user_id: int, chat_id: str):
    chat_id = str(chat_id)

    if chat_id not in dic_question_answer:
        return {
            "success": False,
            "message": "Chat was not found in Python."
        }

    chat = dic_question_answer[chat_id]

    if not chat.get("is_changed", False):
        return {
            "success": True,
            "message": "Chat was not changed. No save needed.",
            "reportId": chat.get("report_id")
        }

    messages = chat.get("messages", [])

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

    conversation_for_save = list(messages)

    topics_tree = chat.get("topics_tree")
    topics_text = ""
    if topics_tree is not None and topics_tree.Root is not None:
        topics_text = topics_tree.tree_to_str()

    conversation_for_save.append("")
    conversation_for_save.append("Topics in report:")

    if topics_text.strip() != "":
        conversation_for_save.extend(topics_text.splitlines())

    conversation_for_save.append("Sentiment and Emotions:")
    conversation_for_save.append("Sentiment: Neutral")
    conversation_for_save.append("Emotions detected: Neutral")

    body = {
        "userId": user_id,
        "reportId": chat.get("report_id"),
        "conversation": conversation_for_save
    }

    saved_data = make_csharp_post_request(
        f"{CSHARP_API_BASE_URL}/api/reports/save-chat",
        body
    )

    if "reportId" in saved_data:
        chat["report_id"] = saved_data["reportId"]

    chat["is_changed"] = False

    return saved_data


@router.post("/sync-chats")
# Receive all of a user's chats from React after loading them from SQL, and rebuild each one's in-memory structure and topics tree
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


@router.post("/save-chat-if-changed")
# Update a chat in memory (creating it if needed) and save it to C#/SQL only if it actually changed
def save_chat_if_changed(data: SaveChatIfChangedRequest):
    try:
        chat_id = str(data.chatId)
        if chat_id not in dic_question_answer:
            dic_question_answer[chat_id] = create_chat_structure(user_id=data.userId, chat_id=data.chatId, report_id=data.reportId, title=data.title or "New conversation", conversation=data.conversation, is_changed=True)
        else:
            chat = dic_question_answer[chat_id]
            chat["user_id"] = data.userId
            chat["report_id"] = data.reportId
            chat["title"] = data.title or chat.get("title", "New conversation")
            chat["messages"] = data.conversation
            chat["is_changed"] = True

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


@router.post("/clear-user-chats")
# Delete all of a user's chats from the in-memory dictionary, typically called after logout once chats are saved to SQL
def clear_user_chats(data: ClearUserChatsRequest):
    try:
        deleted_count = delete_user_chats_from_dic(data.userId)

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


@router.post("/sync-things-the-user-has")
# Temporary endpoint for receiving ThingsTheUserHas data from React, kept for backward compatibility
def sync_things_the_user_has(data: SyncThingsRequest):
    return {
        "success": True,
        "message": "ThingsTheUserHas synced to Python."
    }


@router.post("/chat-message")
# Handle an incoming chat message from the user: store it, run it through message_handling, and return the bot's answer
def receive_chat_message(data: ChatMessageRequest):
    message = data.message.strip()
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
    if chat_id not in dic_question_answer:
        dic_question_answer[chat_id] = create_chat_structure(
            user_id=data.userId,
            chat_id=data.chatId,
            report_id=data.reportId,
            title="New conversation",
            conversation=[],
            is_changed=False
        )

    dic_question_answer[chat_id]["user_id"] = data.userId
    dic_question_answer[chat_id]["report_id"] = data.reportId
    if ("topics_tree" not in dic_question_answer[chat_id] or dic_question_answer[chat_id]["topics_tree"] is None):
        dic_question_answer[chat_id]["topics_tree"] = BinarySearchTree()

    add_question_answer_to_dic(chat_id, "User: " + message)

    try:
        chat_history = get_chat(chat_id)
        answer = message_handling(message, user_data, chat_history)
        if answer is None:
            answer = "I could not build an answer for this message."

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
