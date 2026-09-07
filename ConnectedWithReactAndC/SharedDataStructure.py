import sys
import os
import FindSimilar
from BinarySearchTree import BinarySearchTree, ThingsTheUserHas


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

dic_BinarySearchTree = {}

dic_tree_things = {}

dic_list_to_answer = {}

dic_question_answer = {}


#יצירת צאט חדש
def create_empty_chat():
    return {
        "messages": [
            "Bot: Hello, I am Smart Service Chat. How can I help you?"
        ],
        "is_changed": False,
        # עץ נושאי השיחה הנוכחית
        "topics_tree": BinarySearchTree()
    }


#החזרת שיחה של צאט מסוים
def get_chat(chat_id):
    chat_id = str(chat_id)

    if chat_id not in dic_question_answer:
        dic_question_answer[chat_id] = create_empty_chat()

    return dic_question_answer[chat_id]


#החזרת שאלה-תשובה של שיחה מסוימת
def get_chat_messages(chat_id):
    chat = get_chat(chat_id)
    return chat["messages"]


#החזרת עץ הנושאים לשיחה ספציפית
def get_chat_topics_tree(chat_id):
    chat = get_chat(chat_id)

    if "topics_tree" not in chat or chat["topics_tree"] is None:
        chat["topics_tree"] = BinarySearchTree()

    return chat["topics_tree"]


# הוספת הודעה למילון שיחות נוכחיות
def add_question_answer_to_dic(chat_id, text):
    chat = get_chat(chat_id)
    chat["messages"].append(text)
    chat["is_changed"] = True

#בדיקה אם שיחה השתנת
def is_chat_changed(chat_id):
    chat = get_chat(chat_id)
    return chat["is_changed"]

#לאחר שמירת השיחה - עדכונה שFALSE
def mark_chat_as_saved(chat_id):
    chat = get_chat(chat_id)
    chat["is_changed"] = False

#החזרת השיחות שהשתנו וצריכות שמירה
def get_changed_chats():
    changed_chats = {}

    for chat_id, chat in dic_question_answer.items():
        if chat["is_changed"]:
            changed_chats[chat_id] = chat

    return changed_chats


#מחיקת שיחות מתשתמש מתוך המילון היוצא מן המערכת 
def delete_user_chats_from_dic(user_id):
    user_id = int(user_id)

    chats_to_delete = []

    for chat_id, chat in dic_question_answer.items():
        chat_user_id = chat.get("user_id")

        if chat_user_id is not None and int(chat_user_id) == user_id:
            chats_to_delete.append(chat_id)

    for chat_id in chats_to_delete:
        del dic_question_answer[chat_id]

    return len(chats_to_delete)


# החזרת הנושאים שהיו בשיחה מתוך סיכום השיחה
def extract_topics_section_from_report(report_content, chat_id):
    if not report_content:
        return False

    start_marker = "Topics in report:"
    end_marker = "Sentiment and Emotions:"

    if start_marker not in report_content:
        return False

    # לוקח את כל מה שאחרי Topics in report:
    topic_content = report_content.split(start_marker, 1)[1]

    # אם קיים Sentiment and Emotions: חותך עד אליו בלבד
    if end_marker in topic_content:
        topic_content = topic_content.split(end_marker, 1)[0]


    if topic_content == "":
        return False
    print(topic_content)
    topic_tree = get_chat_topics_tree(chat_id)

    building_tree_topic(topic_tree, topic_content)

    return True

#בנית עץ הנושאים
def building_tree_topic(self, topic_content):
    degel = False
    for top in topic_content.split('\n'):
        if degel == False:
            degel = True
            thing = ThingsTheUserHas(thingsTheUserHasId=0, userId=0, thingsTheUserHasTopic = top , thingsTheUserHasContent=[])
            continue
        if len(top)<2:
            degel = False
            self.insert_to_topic(FindSimilar.embeddings_encode(thing.thingsTheUserHasTopic),thing)
            print(thing)
            continue
        if degel == True:
            thing.thingsTheUserHasContent.append(top)
            continue

#הכנסה לעץ הקטעים המתאימים
def insert_dic_BinarySearchTree(chat_id,the_sentence):
    chat_id = str(chat_id)

    if chat_id not in dic_BinarySearchTree:
        dic_question_answer[chat_id] = BinarySearchTree()

    dic_BinarySearchTree[chat_id].insert_to_string(the_sentence)







