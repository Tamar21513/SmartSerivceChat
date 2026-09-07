import pandas as pd 
import spacy 
from spacy import displacy
from RuntimeSettings import load_runtime_settings
import TextCleaning
import re
settings = load_runtime_settings()


nlp = spacy.load("en_core_web_md")
pd.set_option("display.max_rows", 200)






#מציאת הItem המלא
def find_item(max_overlap,max_token, json_template):
    item = []
    values_list = [str(value).lower() for value in json_template.values() if value]  
    subtree_tokens =list(max_token.subtree) if max_overlap > -1 else []
  
    for i,t in enumerate(subtree_tokens):
        after = subtree_tokens[i + 1].text.lower() if i + 1 < len(subtree_tokens) else ""
        if t.text.lower() in settings["words_to_item"] and after in values_list:
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
def pricing_json_filling(text,json_data):
    json_data = json_data.copy()
    doc = nlp(text)
    print()
    print()
    print(text)
    open_list =[]
    i = 0
    #מילוי TYPE
    while i < len(doc) and doc[i].ent_iob_  == "O" and doc[i].text.lower() != "does":
        if doc[i].text.lower() not in settings["STOP_WORDS_FOR_JSON"]:
            open_list.append(doc[i].text.lower())
        i+=1
    if "cost" not in open_list and "price" not in open_list:
        open_list.append("cost")
    print(open_list)
    json_data["type"] = " ".join(open_list).lower()
    content = []
    #עיקר המשפט
    while i < len(doc):
        if doc[i].text.lower() not in settings["STOP_WORDS_FOR_JSON"]:
            content.append(doc[i].text.lower())
        i+=1
    print("content")
    print(content)


    for noun in doc.noun_chunks:
        if noun[0].i > 0:
            before = doc[noun.start - 1].text.lower() if noun.start > 0 else ""            
            #מקור
            if before.lower() == "from":
                text_clean = TextCleaning.text_cleaning(noun.text)
                json_data["origin"] = text_clean.lower()
            #יעד
            if before.lower() == "to":
                text_clean = TextCleaning.text_cleaning(noun.text)
                json_data["destination"] = text_clean.lower()
            #זמן/תאריך
            if before.lower() == "in":
                text_clean = TextCleaning.text_cleaning(noun.text)
                json_data["time"] = text_clean.lower()
            #כמות
            if before.lower() == "for":
                text_clean = TextCleaning.text_cleaning(noun.text)
                #text_clean = text_clean.split(" ")
                json_data["quantity"] = text_clean.lower()
                #if len(noun.text)>2:
                #    json_data["item"] = " ".join(text_clean[2:]).lower()
            #חברה מותג
            if before.lower() == "with":
                text_clean = TextCleaning.text_cleaning(noun.text)
                brand_words = [word.lower() for word in text_clean.split()if word.lower() not in ["cost", "price"]]
                json_data["brand"] = " ".join(brand_words)
        print(noun)
    print("---------------------------------")

    for token in doc:
        before = doc[token.i - 1].text.lower() if token.i > 0 else ""        
        if_has_in_brands = token.text.lower() in settings["BRANDS"]
        #מציאת המותג/החברה
        if if_has_in_brands == True and json_data["brand"] =="":
            json_data["brand"] = token.text.lower()
        #מילוי שאלה - שתי מילים
        if before.lower()+ " " +token.text.lower() in settings["question_words"] and json_data["type"] == "":
            json_data["type"] = before.lower()+ " "+token.text.lower()
        #מילוי שאלה מילה אחת
        if token.text.lower() in settings["question_words"] and json_data["type"] == "":
            json_data["type"] = token.text.lower()
    
    if json_data["item"] == "":
        list_item = []
        #הוצאת הערכים בJSON:
        keys = list(json_data.keys())
        selected_keys = keys[keys.index("type"):keys.index("quantity") + 1]
        words_to_item = [json_data[key] for key in selected_keys if json_data[key] != ""]
        words_to_item = " ".join(words_to_item).strip()
        words_to_item = words_to_item.split(" ")
        print(words_to_item)
        for word in content:
            if word not in words_to_item and word not in settings["STOP_WORDS_FOR_JSON"]:
                list_item.append(word.lower())
        json_data["item"] = " ".join(list_item)
    if "cost" not in json_data["type"].split(" ") and "price" not in json_data["type"].split(" "):
        open_list.append("cost")
        
    return json_data



#מילוי JSON של השאלת מפרט מוצר.
def product_specs_json_filling(text,json_data):
    json_data = json_data.copy()
    doc2 = nlp(text)
    word_split = []
    for token in doc2:
        if token.pos_ == "ADP" and token.text.lower() in settings["SPEC_SPLIT_WORDS"]:
            word_split.append(token.text)
    #מציאת מפרט מוצר
    if len(word_split) > 0:
        spec = text.split(word_split[0],1)[0].strip()
        products = text.split(word_split[0],1)[1].strip()
        spec2 = nlp(spec)
        products2 = nlp(products)
        chunks = list(spec2.noun_chunks)
        if chunks: 
            spec_words = chunks[-1]
            spec_words_cleaning = TextCleaning.text_cleaning(spec_words.text)
        else:
            spec_words_cleaning = spec2.text
        json_data["spec"] = spec_words_cleaning


    else:
        products2 = doc2
    #מילון COUNT לספירת HEAAD למילים
    dic_count_word_head = {}
    for token in products2:
        if_has_in_brands = token.text.lower() in settings["BRANDS"]
        #מציאת המותג/החברה
        if (token.pos_ == "PROPN" or if_has_in_brands == True) and json_data["brand"] =="":
            if if_has_in_brands == False:
                settings["BRANDS"].append(token.text.lower())
                if_has_in_brands = True
            json_data["brand"] = token.text.lower()
        #מילוי המודל
        if token.pos_ == "PROPN" and if_has_in_brands == False and json_data["brand"] !="" and json_data["model"] == "" :
            json_data["model"] = token.text.lower()
        #מילוי המספר דגם
        if re.search(r"\d", token.text) and json_data["model_code"] == "":
            json_data["model_code"] = token.text.lower()
        if token.is_punct or token.is_space:
            continue
        #הוספת 1 לHEAD של מילה זו - לצורך מציאת נושא
        if token.head.text.lower() in dic_count_word_head:
            dic_count_word_head[token.head.text.lower()] +=1
        else:
            dic_count_word_head[token.head.text.lower()] = 1
    #מילוי נושא
    if dic_count_word_head:
        json_data["product"] = max(dic_count_word_head, key=dic_count_word_head.get)
    #לא התמלא מפרט מוצר - ממלאים אותו משאריות המשפט
    if json_data["spec"] == "":
        #הוצאת הערכים בJSON:
        keys = list(json_data.keys())
        selected_keys = keys[keys.index("product"):keys.index("model_code") + 1]
        words_to_product_specs = [json_data[key] for key in selected_keys]
        for token in doc2:
            if token.text.lower() not in words_to_product_specs and token.pos_ == "NOUN":
                json_data["spec"] = json_data["spec"].strip()+ " "+ token.text.lower()

    return json_data
  


#מילוי JSON של השאלת  תלונה.
def complaint_json_filling(text, json_data):
    json_data = json_data.copy()
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
                json_data["reference_number"] = token.text
            #מילוי למה התלונה קשורה
            if token.pos_ == "NOUN" and token.text.lower() not in settings["STOP_WORDS_TO_Fill_JSON"]:
                sen.append(token.text.lower())

        if len(sen)>0 and json_data["target"] != "":
            json_data["target"] += " and "
        json_data["target"] += " ".join(sen)

    collect_issue  = False
    for token in doc:
        if collect_issue  == True:
            if token.pos_ == "PUNCT":
                collect_issue  = False
            else:
                json_data["issue"] = json_data["issue"]+" "+token.text.lower()
                #מציאת הנושא
        if token.text.lower() == settings["KEY_WORD"]:
            collect_issue  = True

    return json_data 


#מילוי JSON של השאלת  זמן-תאריך.
def date_and_time_json_filling(text, json_data):
    json_data = json_data.copy()
    doc = nlp(text)
    print()
    print()
    print(text)
    open_list =[]
    i = 0
    #מילוי TYPE
    while i < len(doc) and doc[i].ent_iob_  == "O" and doc[i].text.lower() not in ["the","there"]:
        if doc[i].text.lower() not in settings["STOP_WORDS_FOR_JSON"]:
            open_list.append(doc[i].text.lower())
        i+=1
    if "the" not in open_list and "there" not in open_list:
        open_list.append("the")
    print(open_list)
    json_data["type"] = " ".join(open_list).lower()
    content = []
    #עיקר המשפט
    while i < len(doc):
        if doc[i].text.lower() not in settings["STOP_WORDS_FOR_JSON"]:
            content.append(doc[i].text.lower())
        i+=1
    print("content")
    print(content)


    for noun in doc.noun_chunks:
        if noun[0].i > 0:
            before = doc[noun.start - 1].text.lower() if noun.start > 0 else ""            
            #מקור
            if before.lower() == "from":
                text_clean = TextCleaning.text_cleaning(noun.text)
                json_data["origin"] = text_clean.lower()
            #יעד
            if before.lower() == "to":
                text_clean = TextCleaning.text_cleaning(noun.text)
                json_data["destination"] = text_clean.lower()
            #זמן/תאריך
            if before.lower() == "in":
                text_clean = TextCleaning.text_cleaning(noun.text)
                json_data["time_type"] = text_clean.lower()
            #כמות
            if before.lower() == "for":
                text_clean = TextCleaning.text_cleaning(noun.text)
                text_clean = text_clean.split(" ")
                json_data["quantity"] = text_clean[0]
                json_data["event"] = " ".join(text_clean[1:]).lower()
            #חברה מותג
            if before.lower() == "with":
                text_clean = TextCleaning.text_cleaning(noun.text)
                brand_words = [word.lower() for word in text_clean.split()]
                json_data["brand"] = " ".join(brand_words)

        print(noun.text+ "------------------")
        for n in noun:
            print(n.text , n.pos_, n.ent_type_)
    print("---------------------------------")
    list_time = []
    for token in doc:
        if_has_in_brands = token.text.lower() in settings["BRANDS"]
        #מציאת המותג/החברה
        if (token.pos_ == "PROPN" and if_has_in_brands == True) and json_data["brand"] =="":
            json_data["brand"] = token.text.lower()
        #מילוי מספר חבילה
        if token.pos_ == "PROPN" and if_reference_number(token.text.lower()) == True:
            json_data["reference_number"] = token.text
            continue
        #מילוי סוג זמן
        if token.text.lower() in settings["WORD_TIME_TO_TYPE"]:
            json_data["time_type"] = token.text.lower()
        #מילוי זמן ספציפי
        if token.ent_type_ in ["TIME","DATE"]:
            list_time.append(token.text.lower())
    json_data["time_reference"] = " ".join(list_time)
    
    if json_data["event"] == "":
        list_item = []
        #הוצאת הערכים בJSON:
        keys = list(json_data.keys())
        selected_keys = keys[keys.index("type"):keys.index("reference_number") + 1]
        words_to_item = [json_data[key] for key in selected_keys if json_data[key] != ""]
        words_to_item = " ".join(words_to_item).strip()
        words_to_item = words_to_item.split(" ")
        print(words_to_item)
        for word in content:
            if word not in words_to_item and word not in settings["STOP_WORDS_FOR_JSON"]:
                list_item.append(word.lower())
        json_data["event"] = " ".join(list_item)
        
    return json_data
 


#main
def json_filling(topic, text,json_data):
    if topic == "pricing":
        return pricing_json_filling(text, json_data)
    if topic == "product_specs":
        return product_specs_json_filling(text, json_data)
    if topic == "complaint":
        return complaint_json_filling(text, json_data)
    if topic == "date_and_time":
        return date_and_time_json_filling(text, json_data)
    #אחרת זימון המודל המאומן על שאר הנושאים
    return filling_all_the_remaining_json(text,json_data)


#פונקציה המקבלת צומת בעץ , JSON ופריט וממלא בJSON במיקום הפריט ערך מתוך הצומת
def json_filling_form_missing_details(json_data,details,detail):
    if details != None:
        keys = list(json_data.keys())
        # כל המפתחות מתחילת ה-JSON עד search
        keys_list = keys[:keys.index("search")]
        # כל הערכים של המפתחות האלו
        values_list = [json_data[key].lower() if isinstance(json_data[key], str) else json_data[key] for key in keys_list]
        details_list = " ".join(details)
        doc = nlp(details_list)
        for token in doc:
            print(token.text, token.pos_)
            ent = token.ent_type_
            print(ent)
            if token.pos_ == detail["pos"] :# token.ent_type_ == detail["ent_type"]:
               print("true")
               json_data[detail["field"]] = token.text

        print(keys_list)
        print(values_list)
        print(details_list)
    return json_data


#זימון המודל למילוי הJSON הנותרים
def filling_all_the_remaining_json(text,json):
    return


#date_and_time =  {
#    "topic": "date_and_time",
#    "type": "When is there",
#    "event": "",
#    "time_type": "",
#    "origin": "",
#    "destination": "",
#    "brand": "",
#    "quantity": "",
#    "time_reference": "",
#    "reference_number": ""
#}
#print()
#print()
#print()
#print()
#print(pri("What time does the train from Haifa to Bnei Brak leave in the morning?",date_and_time))
#print()
#print()
#print()
#print()
#print(pri("When is there a bus from Ashdod to Jerusalem with Kavim after 6 PM?", date_and_time))
#print()
#print()
#print()
#print()
#print(pri("What time is the next ride from Ashdod to Beersheba?",date_and_time))
#print()
#print()
#print()
#print()
#print(pri("What time does the flight from Tel Aviv to London depart?",date_and_time))
#print()
#print()
#print()
#print()
#print(pri("When is the next bus from Jerusalem to Tel Aviv with Egged tomorrow?",date_and_time))

#data = {
#    "topic": "pricing",
#    "type": "how much",
#    "product": "flight",
#    "brand": "EL AL",
#    "origin": "",
#    "destination": "Greece",
#    "month": "April",
#    "passengers": 1,
#    "search": [
#        {"field": "type"},
#        {"field": "origin"},
#        {"field": "destination"}
#    ],
#    "required": ["type", "origin", "destination"]
#}
#
#df = {
# "field": "month",
# "pos": "NOUN",
# "ent_type": ""
#}
#
#print(json_filling_form_missing_details(data,["Israel","Asus","vivobook","114/15/17"],df)