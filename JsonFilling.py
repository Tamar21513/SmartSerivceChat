import pandas as pd 
import spacy 
import json
#import requests 
#from bs4 import BeautifulSoup
nlp = spacy.load("en_core_web_sm")
pd.set_option("display.max_rows", 200)
question_words = [
    "what", "who", "whom", "whose", "which", "does", "is",
    "when", "where", "why", "how", "how much", "how many",
    "how long", "how far", "how often", "how old", "how soon",
    "how fast", "how late", "how early"]
words = {"from", "to", "for", "with", "in"}
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were",
    "to", "of", "on", "in", "for", "and", "or",
    "with", "this", "that", "it", "as", "by", "my","help","issue"
}
KEY_WORD = "because"
punctuations = [",", ".", "!", "?"]


#מציאת הItem המלא
def find_item(max_token, json_template):
    item = []
    values_list = [str(value).lower() for value in json_template.values() if value]  
    subtree_tokens = list(max_token.subtree)
  
    for i,t in enumerate(subtree_tokens):
        after = subtree_tokens[i + 1].text.lower() if i + 1 < len(subtree_tokens) else ""
        if t.text.lower() in words and after in values_list:
            if len(item) > 0:
                break
            continue
        item.append(t.text)
    return " ".join(item)


#האם יש מספר הזמנה-חבילה
def if_reference_number(text):
    has_digit = any(ch.isdigit() for ch in text)
    has_letter = any(ch.isalpha() for ch in text)
    return has_digit and has_letter





#מילוי JSON של השאלת מחיר.
def pricing_json_filling(text, json_template):
    doc = nlp(text)
    for ent in doc.ents:
        before = doc[ent.start - 1].text.lower() if ent.start > 0 else ""
        after = doc[ent.end].text.lower() if ent.end < len(doc) else ""
        print(before ,ent.text, ent.start_char, ent.end_char, ent.label_)
        #חברה/ספק/ארגון מסוים
        if before == "with" and ent.label_ == "GPE":
            json_template["provider"] = ent.text
            continue
        #מאיפה
        if before == "from" and ent.label_ == "GPE":
            json_template["origin"] = ent.text
            continue
        #לאיפה
        if before == "to" and ent.label_ == "GPE":
            json_template["destination"] = ent.text
            continue
        #תאריך - זמן
        if before == "in" and ent.label_ == "DATE":
            json_template["time"] = ent.text
            continue
        #כמות
        if before == "for" and ent.label_ == "CARDINAL":
            json_template["quantity"] = ent.text +" "+ after
            continue
    max_overlap = 0
    max_token = ""
    for token in doc:
        after = doc[token.i + 1].text.lower() if token.i + 1 < len(doc) else ""
        #מילוי מילת שאלה עם שתי מילים
        if token.text.lower() +" "+after.lower() in question_words and json_template["type"] == "":
            json_template["type"] = token.text.lower() +" "+ after
            continue
        #מילוי מילת שאלה בודדת
        if token.text.lower() in question_words and json_template["type"] == "":
            json_template["type"] = token.text
            continue

        #מילוי נושא חיפוש
        if token.pos_ == "VERB":
            children_words = [child.text.lower() for child in token.children]
            overlap = set(children_words) & words
            if len(overlap) >= max_overlap:
                max_overlap = len(overlap)
                max_token = token
                print()
                print("max-----------")
                print(max_overlap)
                print(max_token)
    str_item = find_item(max_token,json_template)
    json_template["item"] = str_item
    return json_template 



#מילוי JSON של השאלת מפרט מוצר.
def product_specs_json_filling(text, json_template):
    doc = nlp(text)
    for chunk in doc.noun_chunks:
        print()
        print("noun_chunks")
        print(chunk)
        bool = False
        # בחר ביטויים שמכילים לפחות שם עצם
        for token in chunk:
            after_text = doc[token.i + 1].text.lower() if token.i + 1 < len(doc) else ""
            after_pos = doc[token.i + 1].pos_ if token.i + 1 < len(doc) else ""
            print(token.text, token.pos_,token.head.text)
            #מילוי חברה
            if token.pos_ == "PROPN" and json_template["brand"] == "":
                json_template["brand"] = token.text.lower()
                if after_pos == "NOUN" or after_pos == "PROPN" and json_template["model"] == "":
                    json_template["model"] = after_text.lower()
                bool = True
                continue
            #מילוי מספר דגם
            if token.text.lower() == json_template["model"] and after_pos == "PROPN" and json_template["model_code"] == "":
                json_template["model_code"] = after_text.lower()
                bool = True
                continue
            if bool == False: 
                #מה לבדוק על המוצר
                if token.pos_ != "PRON" and token.text.lower() not in STOP_WORDS:
                    json_template["spec"] = json_template["spec"]+ " " + token.text.lower()   
    max_overlap = 0
    max_token = ""
    for token in doc:
        print(token.text, token.pos_ ,token.head.text)
        after = doc[token.i + 1].text.lower() if token.i + 1 < len(doc) else ""
        #מילוי מילת שאלה עם שתי מילים
        if token.text.lower() +" "+after.lower() in question_words and json_template["type"] == "":
            json_template["type"] = token.text.lower() +" "+ after
            continue
        #מילוי מילת שאלה בודדת
        if token.text.lower() in question_words and json_template["type"] == "":
            json_template["type"] = token.text.lower()
            continue
            #מילוי נושא חיפוש
        if token.pos_ == "NOUN":
            children_words = [child.text.lower() for child in token.children]
            overlap = set(children_words) & words
            if len(overlap) >= max_overlap:
                max_overlap = len(overlap)
                max_token = token
                print()
                print("max-----------")
                print(max_overlap)
                print(max_token)

    values_list = [str(value).lower() for value in json_template.values() if value] 
    values_list = " ".join(values_list)
    values_list = values_list.split(" ")
    print("values_list")
    print(values_list)
    if max_token.text.lower() not in values_list:
        json_template["product"] = max_token.text.lower()
    return json_template   


#מילוי JSON של השאלת  תלונה.
def complaint_json_filling(text, json_template):
    doc = nlp(text)
    for chunk in doc.noun_chunks:
        print()
        print("noun_chunks")
        print(chunk)
        sen = []
        for token in chunk:
            print(token.text, token.pos_)
            #מילוי מספר חבילה
            if token.pos_ == "PROPN" and if_reference_number(token.text.lower()) == True:
                json_template["reference_number"] = token.text
            #מילוי למה התלונה קשורה
            if token.pos_ == "NOUN" and token.text.lower() not in STOP_WORDS:
                sen.append(" " +token.text.lower())

        if len(sen)>0 and json_template["target"] != "":
            json_template["target"] += " and "
        json_template["target"] += "".join(sen)

    bool = False
    for token in doc:
        if bool == True:
            if token.pos_ == "PUNCT":
                bool = False
            else:
                json_template["issue"] = json_template["issue"]+" "+token.text.lower()
                #מציאת הנושא
        if token.text.lower() == KEY_WORD:
            bool = True

    return json_template 


#מילוי JSON של השאלת  זמן-תאריך.
def date_and_time_json_filling(text, json_template):
    doc = nlp(text)
    for ent in doc.ents:
        before = doc[ent.start - 1].text.lower() if ent.start > 0 else ""
        after = doc[ent.end].text.lower() if ent.end < len(doc) else ""
        print(before ,ent.text, ent.start_char, ent.end_char, ent.label_)
        #חברה/ספק/ארגון מסוים
        if before == "with" and ent.label_ == "GPE":
            json_template["provider"] = ent.text
            continue
        #מאיפה
        if before == "from" and ent.label_ == "GPE":
            json_template["origin"] = ent.text
            continue
        #לאיפה
        if before == "to" and ent.label_ == "GPE":
            json_template["destination"] = ent.text
            continue
        #תאריך - זמן
        if before == "in" and ent.label_ == "DATE":
            json_template["time_type"] = ent.text
            continue
        #שעה
        if ent.label_ == "TIME":
            json_template["time_reference"] = ent.text
            continue
        #כמות
        if before == "for" and ent.label_ == "CARDINAL":
            json_template["quantity"] = ent.text +" "+ after
            continue
    max_overlap = 0
    max_token = ""
    print()
    print()
    for token in doc:
        print(token.text, token.pos_)
        after = doc[token.i + 1].text.lower() if token.i + 1 < len(doc) else ""
        ##מילוי מילת שאלה עם שתי מילים
        #if token.text.lower() +" "+after.lower() in question_words and json_template["type"] == "":
        #    json_template["type"] = token.text.lower() +" "+ after
        #    continue
        ##מילוי מילת שאלה בודדת
        #if token.text.lower() in question_words and json_template["type"] == "":
        #    json_template["type"] = token.text
        #    continue
        #מילוי מספר חבילה
        if token.pos_ == "PROPN" and if_reference_number(token.text.lower()) == True:
            json_template["reference_number"] = token.text
            continue

        #מילוי נושא חיפוש
        if token.pos_ == "NOUN":
            children_words = [child.text.lower() for child in token.children]
            overlap = set(children_words) & words
            if len(overlap) >= max_overlap:
                max_overlap = len(overlap)
                max_token = token
                print()
                print("max-----------")
                print(max_overlap)
                print(max_token)
    str_item = find_item(max_token,json_template)
    json_template["event"] = str_item
    return json_template  


#main
def json_filling(topic, text,json):
    if topic == "pricing":
        return pricing_json_filling(text, json)
    if topic == "product_specs":
        return product_specs_json_filling(text, json)
    if topic == "complaint":
        return complaint_json_filling(text, json)
    if topic == "date_and_time":
        return date_and_time_json_filling(text, json)
    #אחרת זימון המודל המאומן על שאר הנושאים