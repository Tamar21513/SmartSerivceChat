import spacy
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()


# טען מודל אנגלי
nlp = spacy.load("en_core_web_sm")


#פונקציה החזירה את הנושאים מתוך טקסט חדש
def extract_topics(text):
    new_topic = nlp(text)
    # הוצאת noun chunks (ביטויים שמייצגים דברים/נושאים)
    filtered_words = []
    for chunk in new_topic.noun_chunks:
        # בחר ביטויים שמכילים לפחות שם עצם
        if any(token.pos_ == "NOUN" for token in chunk):
            words = [w.text for w in chunk if w.text.lower() not in settings["STOP_WORDS_TO_FIND_TOPIC"] and len(w.text) > 2]
            if words:
                filtered_words.append(" ".join(words))
            # בחר ביטויים שמכילים לפחות שם עצם
    return filtered_words




#פונקציה החזירה את הפעלים מתוך טקסט חדש
def extract_verbs(text):
    new_topic = nlp(text)
    filtered_words = []
    for chunk in new_topic:
        #מציאת פועל
        if chunk.pos_ == "VERB":
            filtered_words.append("".join(chunk.text))
    return filtered_words



#בדיקה - ברוך השם עובד!!!
#path_db = r'C:\Tamarush\programming\project\ChatTM\Felis_python\ConversationSummaries\tamar_moriel'
#topics = extract_topics("i want to know how take pictures.")
#print(fSimilarTopic.find_similar_topic_to_new_text(path_db,topics))




#message = "How much does it cost to fly from Israel to Greece with El Al in April for one person?"
##message = "I am interested in buying an iron, how much does a steam iron cost?"
##message = "How to get from Jerusalem to Tel Aviv by public transportation"
##message = "How much does a box cost?"
#
#import TextCleaning
##הוצאת הנושאים מהטקסט
#topics = extract_topics(message)
#print(topics)
##חלוקת הנושאים למילים
#topic_words = set()
#for t in topics:
#    topic_words.update(t.split())
##מציאת פעלים
#verbs = extract_verbs(message)
#print(verbs)
#words = []
#verb_seen = False
#topic_seen = False
##הרכבת משפט מהנושאים והפעלים על פי סדר הופעתם במשפט
#message_clean = TextCleaning.text_cleaning(message)
#word_message = message_clean.split()
#for word in word_message:
#    # אם זו מילה שהיא פועל
#    if word in verbs:
#        words.append(word)
#        verb_seen = True
#        print(word)
#    # אם זו מילה שהיא נושא ויש כבר פועל לפני
#    elif word in topic_words :#and verb_seen:
#        words.append(word)
#        topic_seen = True
#    #elif topic_seen:
#    #    verb_seen = False
#
#text_question = " ".join(words)
#print("----------the question------------------")
#print(text_question)















#-----------------------------------------

#from collections import Counter
#import re
#
## Basic English stop words (can be extended)
#STOP_WORDS = {
#    "the", "a", "an", "is", "are", "was", "were",
#    "to", "of", "on", "in", "for", "and", "or",
#    "with", "this", "that", "it", "as", "by"
#}
#
#def extract_topic(text, top_k=3):
#    # Clean text: lowercase + keep only letters
#    text = text.lower()
#    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
#
#    words = text.split()
#
#    # Remove stop words and very short tokens
#    filtered_words = [
#        w for w in words
#        if w not in STOP_WORDS and len(w) > 2
#    ]
#
#    # Count word frequency
#    counter = Counter(filtered_words)
#
#    # Return top keywords as topic
#    return [word for word, _ in counter.most_common(top_k)]
#
#
## Example
#text = "I need help with connecting my JBL speaker to my phone."
#print(extract_topic(text))
