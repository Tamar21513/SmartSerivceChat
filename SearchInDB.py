import pyodbc
import FindSimilar
from ConnectWhitDB import TavilyAPI as tavilApi
from sklearn.metrics.pairwise import cosine_similarity
from RuntimeSettings import load_runtime_settings
from custom_transformer.predict import predict_match
import trafilatura
from BinarySearchTree import BinarySearchTree
import distilBert
import SplitTextToParagraphs
import re
from ConnectedWithReactAndC.SharedDataStructure import dic_BinarySearchTree, dic_list_to_answer



settings = load_runtime_settings()



conn = pyodbc.connect( 
   "Driver={SQL Server};" 
   "Server=.\SQLEXPRESS;" 
   "Database=SmartServiceChatDB;" 
   "Trusted_Connection=yes;" 
) 

#להרצת שאילתות
cursor = conn.cursor()

#מציאת קוד קטגוריה המתאים ביותר
def search_catgory(text):
    cursor.execute(
        '''
        SELECT category_id , category_name
        FROM Category
        '''
    )
    #כל הקטגוריות
    rows = cursor.fetchall()
    text_emb = FindSimilar.embeddings_encode(text)
    max_similar = 0.0
    max_catgory_id = 0
    max_catgory_name = ""
    for row in rows:
        res_emb = FindSimilar.embeddings_encode(row.category_name)
        similar_emb = FindSimilar.matching_two_vectors(text_emb, res_emb)
        print(row.category_name)
        print(similar_emb)
        if similar_emb > max_similar:
            max_similar = similar_emb
            max_catgory_id = row.category_id
            max_catgory_name = row.category_name
    print("----------max---------------")
    print(max_catgory_name)
    print(max_similar)
    return max_catgory_id



#שליפת החברות המתאימות לקטגוריה
def select_company(topic, company_id, question, user_data, if_has_company, category_id = 0):
    #חיפוש בחברה ספציפית
    if company_id > 0 and if_has_company == True:
        #חיפוש מסד נתונים של חברה מסוימת
        cursor.execute(
            '''
            SELECT c.company_name, cd.data_id, cd.content, cd.topic
            FROM CompanyData cd
            INNER JOIN Company c
                ON cd.company_id = c.company_id
            WHERE cd.company_id = ?
            ''',
            company_id
        )
        result = cursor.fetchone()
        search_in_db(result, topic, question, user_data)

    else:
        #שליפת כל הקטגוריה לחברה המתאימה לקטגוריה
        cursor.execute(
            '''
            SELECT company_id , priority
            FROM CompanyCategories
            Where category_id =?
            ORDER BY priority ASC
            ''',
            category_id
        )
        rows = cursor.fetchall()
        print("rows")
        print(rows)
        #מעבר כל החברות
        for row in rows:
            #זימון מסד הנתונים
            cursor.execute(
                '''
                SELECT c.company_name, cd.data_id, cd.content, cd.topic, c.company_id
                FROM CompanyData cd
                INNER JOIN Company c
                    ON cd.company_id = c.company_id
                WHERE cd.company_id = ?
                ''',
                (row.company_id,)
            )
            result = cursor.fetchone()
            if result[4] == company_id:
                continue
            print(result)
            search_in_db(result, topic, question, user_data)
            if len(dic_list_to_answer[user_data["userId"]]) >= settings["NUM_TO_ANSWER"]:
                break


#חלוקת הטקסט לרשימת לנקים ולרשימת תאורים
def split_to_links_description(link_and_description):
    links = []
    descriptions = []

    lines = link_and_description.split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("link - "):
            links.append(line.replace("link - ", "", 1).strip())

        elif line.startswith("description - "):
            descriptions.append(line.replace("description - ", "", 1).strip())
    return [links,descriptions]


#מציאת אחוז התאמה לתאורי לינקים
def matching_to_description(the_question ,titles ,results):
    #מציאת התאמה
    similarity_scores = matching_percentages(the_question[0] , titles)
    print(similarity_scores)
    #יצירת זוגות: אחוז התאמה עם תשובת האינטרנט 
    pairs = list(zip(results, similarity_scores))
    # סינון לפי סף התאמה
    filtered = [p for p in pairs if p[1]]
    # מיון לפי אחוז התאמה (מהגבוה לנמוך)
    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered
            


#חיפוש במסד נתונים ספציפי
def search_in_db(result, topic, question, user_data):
    dic_BinarySearchTree[user_data["userId"]] = BinarySearchTree()
    if result != None:
        line = result[3].split("\n")
        #מציאת מקום החיפוש על פי הנחיות מסד הנתונים
        for l in line:
            if l.split(" - ")[0].lower() == topic.lower():
                search_in = l.split(" - ")[1]
                break
        word = search_in.split(", ")
        for ww in word:
            print(ww)
            content_db = result[2].split(ww+":"+"\n")
            content_db = re.search(r"^(.*?)(?=\n[A-Za-z][A-Za-z ]*:\n)",content_db[1],re.DOTALL)
            if not content_db:
                link_and_title = content_db.strip()
            else:
                link_and_title = content_db.group(1).strip()
            print("link_and_title")
            print(link_and_title)
            #חלוקת לרשימת לינקים ולרשימת תיאורים 
            links_description = split_to_links_description(link_and_title)
            #מציאת אחוז התאמה בין תיאורי הלינקים לשאלה וסידורים מהגדול לקטן
            filtered = matching_to_description(question,  links_description[1], links_description[0])
            print(filtered)
            urls = []
            for pair in filtered:
                urls.append(pair[0])
            #פתיחת ה URL המתאימים ביותר
            contents = information_from_URL(urls)
            print(contents)
            #מציאת המשפטים המתאימים ביותר והכסתם לעץ
            select_most_suitable_simplifyers(contents, question, topic, user_data, result[0])

        #הוצאת מספר התשובות המקוצרות המתאימות ביותר
        dic_list_to_answer[user_data["userId"]].extend(dic_BinarySearchTree[user_data["userId"]].bst_to_list(0,settings["NUM_TO_ANSWER_TO_COMPANY"]))


#מציאת ת.ז. חברה עבור שם חברה
def id_company_from_name_company(name_company):
    #חיפוש מסד נתונים של חברה מסוימת
    cursor.execute(
        '''
        SELECT c.company_id
        FROM Company c
        WHERE c.company_name = ?
        ''',
        name_company.lower()
    )
    result = cursor.fetchone()
    if result != None:
        return result[0]
    return 0



#חיפוש במסד חברה - main
#מחזירה רשימה של קטעים נבחרים
def handling_company_database(question,item,topic,name_company, user_data):
    print()
    print()
    print(f"{item}-------------------------------")
    dic_list_to_answer[user_data["userId"]] = []
    company_id = 0
    if name_company !="":
        company_id = id_company_from_name_company(name_company)
    if company_id > 0:
        select_company(topic, company_id, question, user_data, True)
        if len(dic_list_to_answer[user_data["userId"]]) < settings["NUM_TO_ANSWER"]:
            return dic_list_to_answer[user_data["userId"]] 
    category_id = search_catgory(item)
    print(category_id)
    select_company(topic, company_id, question, user_data, False, category_id)
    return dic_list_to_answer[user_data["userId"]] 



#מציאת enb ואחוזי התאמה לנושא של השאלה
def matching_percentages(text_to_search,titles):
    similarity_scores = []
    #המרת הנושא החדש לוקטור מספרי
    new_emb = FindSimilar.embeddings_encode(text_to_search).reshape(1, -1)
    titles_emb = FindSimilar.embeddings_encode(titles)
    #מציאת אחוזי התאמה
    similarity_scores = cosine_similarity(new_emb, titles_emb)[0]

    return similarity_scores


#שליפת מידע המURL המתאימים ביותר
def information_from_URL(list_url):
    if len(list_url) == 0:
        return []
    contents =[]
    index = 0
    for url in list_url:
        if len(contents) < settings["TOP_3"]:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                if text ==None:
                    print(f"--------------{index}-the text None----------------------")
                else:
                    contents.append(text)
                    print()
                    print(f"----------------------{index} open good------------------------")
                    index+=1
            else:
                print()
                print(f"--------------{index}-error----------------------")
        else:
            return contents
    return contents

#במקרה הצורך - חיפוש כללי - main
def handling_Internet_database(the_question):
    response = tavilApi.search_in_DB(the_question[0])
    results = response["results"]
    print("Number of results:", len(results))
    print("\n")
    #הוצאת הכותרות
    titles = [r["title"].rsplit("-", 1)[0].strip() for r in response["results"]]
    #התאמה בין השאלה לתאורי הלינקים
    filtered = matching_to_description(the_question, titles, results)
    # שלושת התוצאות הטובות ביותר
    #top3 = filtered[:settings["TOP_3"]]

    #איחוד URL בכדי למצוא תשובה
    urls = []
    for url in filtered:
        urls.append(url[0]["url"])
    print(urls)

    #פתיחת הURL המתאימים ביותר
    contents = information_from_URL(urls)
    return contents


#מציאת המשפטים המתאימים ביותר
def select_most_suitable_simplifyers(contents, the_question, category, user_data, start = ""):
    print(f"num contents: {len(contents)}")
    #מעבר על האתרים שפתחנו מהURL
    for content in contents:
        #חלוקת התוכן לפסקאות
        paragraphs  = SplitTextToParagraphs.split_titles_and_large_sections(content)
        #עבור כל פסקה
        for par in paragraphs:
            #מציאת התשובה המתאימה ביותר באותה פסקה
            short_sen = distilBert.pipeline_DistilBert(par,the_question[0])
            #בדיקת אחוז ההתאמה - כמה התשובה הקצרה בתאימה לשאלת הלקוח בתור תשובה
            score = predict_match("topic: " + category + " , question: " + the_question[0] + " , answer: " +  short_sen + " " + start , the_question[1])
            print(score)
            #הכנס התשובהה הקצרה לעץ כשהמפתח הוא אחוז ההתאמה
            dic_BinarySearchTree[user_data["userId"]].insert_to_string(score,short_sen)




#handling_company_database("how much cost Bamba Nouget?","Bamba Nougat","pricing",0)
