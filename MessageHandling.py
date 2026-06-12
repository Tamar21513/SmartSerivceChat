import FindSimilar 
import AnswerBuilding
import CategorizedByTopic
import JsonToTopic
import JsonFilling
from BinarySearchTree import BinarySearchTree
from ConnectedWithReactAndC.SharedDataStructure import dic_tree_things, dic_BinarySearchTree
from RuntimeSettings import load_runtime_settings
import SearchInDB

settings = load_runtime_settings()


















#בניית שאלה מתוך הJSON
def build_question(json):
    #רשימת השאלה
    the_question = []
    #רשימת משקלי מילות השאלה
    token_weights = [0.2,3.0, 1.0, 1.0]
    #הוצאת רשימת הערכים לחיפוש מהJSON
    search = json["search"]
    #מעבר על הערכים
    for item in search:
        bool = False
        #במידה ויש מילה להוסיף לפני הערך במידה וערך זה מלא
        if "text_if_field_exists" in item:
            bool = True
        #הוצאת הערך 
        field = item["field"]
        #אם הוא ריק לא להוסיף ךשאלה - לא אותו ולא את המילת קישור שלו.
        if json[field] == '':
            bool = False
            continue
        #אם הוא לא ריק ויש מילת קישור לפני
        if bool ==  True:
            #מוסיפים לשאלה את המילת קישור
            the_question.append(item["text_if_field_exists"])
            #הוספת מישקל כללי למילת הקישור
            token_weights.append(1.0)
            bool = False
        #הוספת הערך לשאלה
        the_question.append(json[field])
        #הוספת משקלים לרשימת המשקלים על פי הערכים המסומנים.
        for word in json[field].split(" "):
            token_weights.append(item["token_weight"])
    #החזרת רשימה, במיקום הראשון - השאלה המקוצרת כמחרוזת, במיקום השני - רשימת המשקלים
    return [" ".join(the_question) , token_weights]


#האם כל הפרטים החשובים מלאים? מחזיר מערך של הפרטים החסרים.
#במקרה ולא חסר פרטים מחזיר מערך ריק
def if_everything_full(json):
    #רשימת הערכים החסרים
    missing_item = []
    #הוצאת רשימת הערכים החשובים
    required = json["required"]
    print("required-----------------------")
    print(required)
    #מעבר על הערכים החשובים
    for item in required:
        #אם הערך ריק 
        if json[item] == "":
            #הוספת הערך לרשימת הערכים החשובים החסרים
            missing_item.append(item)
    #החזרת רשימת הערכים החסרים
    return missing_item

#מציאת פרטים חסרים
def finding_missing_details(json_question, user_data, chat_history):
    #שליפת רשימת ההנחיות למציאת הפרטים מתוך ה JSON
    search_missing_details = json_question["search_missing_details"]
    details_topics = None
    details = None
    #מעבר על הרשימה
    for item in search_missing_details:
        print("item")
        print(item)
        #אם הפריט שצריך להתקיים מלא
        if json_question[item["if_field_exists"]] != "":
            print(json_question[item["if_field_exists"]] )
            where_search = ""
            if details_topics == None:
                #חיפוש הערך החסר בעץ נושאי השיחה
                details_topics = chat_history["topics_tree"].search_node_in_tree(chat_history["topics_tree"].Root, FindSimilar.embeddings_encode(json_question[item["if_field_exists"]]),json_question[item["if_field_exists"]],"topics")
            print()
            print()
            print()
            print("details_topics")
            print(details_topics.value)
            #תעבור על הפריטים שאולי ריקים
            for detail in item["if_fields_missing"]:
                print(detail)
                #אם הפריט ריק
                if json_question[detail["field"]] == "":
                    #שליפת עבור פריט זה איפה לחפש - מה שהוא/מה שיש לו
                    where_search = item["search_missing_value_in"]
                    print(where_search)
                    #אם חיפוש הפריט החסר הוא בדברים שיש לו
                    if where_search == "ThingsTathUserHas":
                        print(where_search)
                        print(dic_tree_things[user_data["userId"]].Root)
                        print()
                        print()
                        print()
                        if details != None:
                            print("details")
                            print(details.value)
                        #מילוי הערך החסר מתוך נושאי שיחה
                        json_question = JsonFilling.json_filling_form_missing_details(json_question,details_topics.value.thingsTheUserHasContent,detail)
                        #אם לא נמצא מתאים
                        if details_topics == None or json_question[detail["field"]] == "":
                            #מציאת הצומת בעץ הדברים שיש לו המתאימה לערך המלא
                            details = dic_tree_things[user_data["userId"]].search_node_in_tree(dic_tree_things[user_data["userId"]].Root,FindSimilar.embeddings_encode(json_question[item["if_field_exists"]]),json_question[item["if_field_exists"]],"things")
                        if details != None:
                            print(details.value.thingsTheUserHasContent)
                            #מילוי הפריט החסר מתוך עץ הדברים שיש לו
                            json_question = JsonFilling.json_filling_form_missing_details(json_question,details.value.thingsTheUserHasContent,detail)
                            
                        print(json_question)
                    else:
                        print(user_data.get(detail["search_value"],""))
                        json_question[detail["field"]] = user_data.get(detail["search_value"],"")
                print(json_question[item["if_field_exists"]])
                #הכנסת הפריט לנושאי השיחה 
                details_topics = chat_history["topics_tree"].insert_the_item_into_node(details_topics, FindSimilar.embeddings_encode(json_question[item["if_field_exists"]]) , json_question[item["if_field_exists"]], json_question[detail["field"]],"topics")

            print("----json_question------")
            print(json_question)
    return json_question







#טיפול בהודעה
def message_handling(text, user_data,chat_history):
    #tree_things.print_tree(tree_things.Root)
    #מציאת סוג הפניה
    category = CategorizedByTopic.categories(text)
    print("category")
    print(category)
    #שאיבת הJSON המתאים לסוג הפניה
    json_question = JsonToTopic.get_json(category)
    #מילוי הJSON בערכים משאלת הלקוח
    full_json = JsonFilling.json_filling(category,text,json_question)
    print("full_json")
    print(full_json)
    #מציאת הנתונים החסרים
    json_question = finding_missing_details(json_question, user_data, chat_history)
    #בדיקה שכל הערכים הנחוצים בJSON מלאים 
    missing_item = if_everything_full(full_json)
    if len(missing_item) > 0:
        print("The following items are missing:")
        print("missing_item")
        print(missing_item)
        return "The following items are missing: " + ", ".join(missing_item)
    #בנית השאלה המקוצרת
    the_question = build_question(full_json)
    print("the_question[0]")
    print(the_question[0])
    print("the_question[1]")
    print(the_question[1])
        
    # סוג הפניה לא תלונה
    if category != "complaint" and category != "other":
        item_in_question = json_question["required"]
        if settings["brand"] in json_question:
            name_company = json_question[settings["brand"]]
        else:
            name_company = ""
        #חיפוש תשובה במסד נתונים
        lst_par_to_answer = SearchInDB.handling_company_database(the_question[0],json_question[item_in_question[1]],category,name_company, user_data)
        if len(lst_par_to_answer) < settings["NUM_TO_ANSWER"]:
            #במקרה הצורך - חיפוש כללי
            contents = SearchInDB.handling_Internet_database(the_question)
            dic_BinarySearchTree[user_data["userId"]] = BinarySearchTree()
            #טיפול במאמרים שנפתחו
            SearchInDB.select_most_suitable_simplifyers(contents, the_question, category, user_data)
            #הוצאת מספר התשובות המקוצרות המתאימות ביותר
            text_to_answer = dic_BinarySearchTree[user_data["userId"]].bst_to_list(len(lst_par_to_answer),settings["NUM_TO_ANSWER"])
            lst_par_to_answer = lst_par_to_answer + text_to_answer
        print()
        print()
        print("len(text_to_answer)")
        print(len(text_to_answer))
        print('\n')

        if(len(text_to_answer) == 0):
            return "Error, The URL not opening AND There is no suitable answer."


#        #מציאת חלקים לתשובות המכילים נושאים שונים
#        set_topic = set()
#        dic_par = {}
#        paragraphs_to_answer = []
#        #הכנסת הערכים של התשובה הקצרה הראשונה
#        paragraphs_to_answer.append(text_to_answer[0])
#        #הוצאת הנושאים מתוך התשובה המקוצרת והכנסתם לSET
#        set_topic.update(FindTopic.extract_topics(text_to_answer[0]))
#        #מעבר על החלקים לתשובה הכנסה לרשימה את הטקסטים שאין ביניהם נושאים משותפים
#        #כאשר יש נושאים משותפים - מכניסים למילון את מספר הטקסט מהרשימה וכמה נושאים משותפים.
#        for index, par in enumerate(text_to_answer[1:], start=0):
#            par_topic = FindTopic.extract_topics(par)
#            overlap = set_topic & set(par_topic)
#            if len(overlap) == 0:
#                set_topic.update(par_topic)
#                paragraphs_to_answer.append(par)
#            else:
#                dic_par[index+1] = len(overlap)
#        print("len(paragraphs_to_answer)")
#        print(len(paragraphs_to_answer))

        #במידה ומספר הטקסטים השונים לתשובה קטנים מ 5 נעבור על המילון 
        #ונוסיף את בטקסטים שמספר הנושאים החופפים קטן ביותר עד שנגיעה ל5 טקסטים לתשובה
#        if len(paragraphs_to_answer)<NUM_PARAGRAPHS_TO_ANSWER:
#            mone = NUM_PARAGRAPHS_TO_ANSWER-len(paragraphs_to_answer)
#            while mone>0 and dic_par:
#                sorted_items = sorted(dic_par.items(), key=lambda x: x[1])
#                print(sorted_items)
#                paragraphs_to_answer.append(text_to_answer[sorted_items[0][0]])
#                del dic_par[sorted_items[0][0]]
#                mone-=1
#        print()
#        print()
#        print()
#        print("-----------paragraphs to answer-------------")
#        print("\n\n\n".join(paragraphs_to_answer))

        print("-----------text_to_answer-------------")
        print("\n\n\n".join(text_to_answer))

        #בנית התשובה
        answer_final = AnswerBuilding.create_answer(the_question,"\n".join(text_to_answer), category, the_question[1])
        return answer_final
    #
    #
    #
    #
    #
    
    else:
        if category == "other":
            return "I am not allowed to answer this question because it does not deal with customer service."
        #טיפול בתלונה
        else:
            return complaint_handling(text, user_data, chat_history)

#טיפול בתלונה
def complaint_handling(text, user_data, chat_history):
    return

        
        








#text_to_search = message_handling("When is there a flight from Israel to Greece in April with El Al  at time 17:00 for one person?")
#text_to_search = message_handling("I am very disappointed with the service I received because my order AB124586 was delayed, the support team did not answer clearly, and the issue is still unresolved. ")
#text_to_search = message_handling("Does the Samsung Galaxy S24 support wireless charging?")
#text_to_search = message_handling("What is the screen size of the ASUS vivobook 14/15/17 computer?")
#text_to_search = message_handling("What is the screen size of the ASUS computer?")
#text_to_search = message_handling("What is the screen size of the ASUS computer?")
#text_to_search = message_handling("How much would it cost to install a new battery in my laptop, including the part price and the technician’s service fee?")
#text_to_search = message_handling("Could you tell me how much it would cost to repair a broken laptop screen, including the service fee and any extra charges?")
#text_to_search = message_handling("Hi, I’m trying to check something and I’m not sure exactly how to ask it — I need to know the price for one person, maybe sometime in April, to fly from Israel to Greece, preferably with El Al, and I want to understand how much it would cost overall.")
#text_to_search = message_handling("I would like to know how much it costs to fly from Israel to Greece with El Al in April for one person, including the basic ticket price and any possible additional fees.")
#text_to_search = message_handling("How much does it cost to fly from Israel to Greece with El Al in April for one person?")
#text_to_search = message_handling("How much does a JBL GO 4 speaker cost?")
#text_to_search = message_handling("I have a really good camera and I want to know how to take good pictures.")
#text_to_search = message_handling("How to get from Jerusalem to Tel Aviv by public transportation")
print()
print()
print()
print()
print()
print()
print(f"-----------------------------answer final---------------------")
print()
#print(text_to_search)

#TavilyAPI.search_in_DB(text_to_search)