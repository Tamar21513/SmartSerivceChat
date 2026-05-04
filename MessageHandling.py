import TextCleaning
import FindTopic 
from ConnectWhitDB import TavilyAPI as tavilApi
import FindSimilar 
from sklearn.metrics.pairwise import cosine_similarity
import trafilatura
import FindSimilar 
import SplitTextToParagraphs
import distilBert
import FindTopic
import BinarySearchTree
import AnswerBuilding
THRESHOLD = 0.6
NUM_PARAGRAPHS_TO_ANSWER = 5


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
        return False
    contents3 =[]
    index = 0
    for url in list_url:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text ==None:
                print(f"--------------{index}-the text None----------------------")
            else:
                contents3.append(text)
                print()
                print(f"----------------------{index} open good------------------------")
                index+=1
        else:
            print()
            print(f"--------------{index}-error----------------------")
    return contents3




#טיפול בהודעת המשתמש
def message_handling(message):
    #הוצאת הנושאים מהטקסט
    topics = FindTopic.extract_topics(message)
    print(topics)
    #חלוקת הנושאים למילים
    topic_words = set()
    for t in topics:
        topic_words.update(t.split())
    #מציאת פעלים
    verbs = FindTopic.extract_verbs(message)
    print(verbs)
    words = []
    verb_seen = False
    topic_seen = False
    #הרכבת משפט מהנושאים והפעלים על פי סדר הופעתם במשפט
    message_clean = TextCleaning.text_cleaning(message)
    word_message = message_clean.split()
    for word in word_message:
        # אם זו מילה שהיא פועל
        if word in verbs:
            words.append(word)
            verb_seen = True
            print(word)
        # אם זו מילה שהיא נושא ויש כבר פועל לפני
        elif word in topic_words and verb_seen:
            words.append(word)
            topic_seen = True
        elif topic_seen:
            verb_seen = False

    text_question = " ".join(words)
    print("-----------the question-----------------")
    print(text_question)

    #חיפוש תשובה באינטרנט
    response = tavilApi.search_in_DB(message)
    results = response["results"]
    print("Number of results:", len(results))
    print("\n")

    #הוצאת הכותרות
    titles = [r["title"].rsplit("-", 1)[0].strip() for r in response["results"]]
    #מציאת התאמה
    similarity_scores = matching_percentages(message , titles)
    print(similarity_scores)

    #יצירת זוגות: אחוז התאמה עם תשובת האינטרנט 
    pairs = list(zip(results, similarity_scores))
    # סינון לפי סף התאמה
    filtered = [p for p in pairs if p[1] >= THRESHOLD]
    # מיון לפי אחוז התאמה (מהגבוה לנמוך)
    filtered.sort(key=lambda x: x[1], reverse=True)
    # שלושת התוצאות הטובות ביותר
    top3 = filtered[:3]

    #איחוד URL בכדי למצוא תשובה
    url3 = []
    for url in top3:
        url3.append(url[0]["url"])
    print(url3)

    #לשאול את המורה האם להוסיף פה את הקישורים של סיכומי שיחות קודמות הקשורות
    #כי אני רק אמור להישען על מידע משם לא ליצר תשובות מסיכומי השיחות

    #זימון הפעולה המחלצת טקסט מתוך URL
    contents = information_from_URL(url3)
    tree = BinarySearchTree.BinartSearchThree()
    print(f"num contents: {len(contents)}")
    for content in contents:
        paragraphs  = SplitTextToParagraphs.split_titles_and_large_sections(content)
        for par in paragraphs:
            short_sen = distilBert.pipeline_DistilBert(par,text_question)
            matching_perc = FindSimilar.semantic_search_from_corpus(short_sen ,text_question)
            tree.insert(matching_perc[0]['score'],short_sen)
    text_to_answer = tree.bst_to_list_10()
    print()
    print()
    print("len(text_to_answer)")
    print(len(text_to_answer))
    print('\n')

    if(len(text_to_answer) == 0):
        return "Error, The URL not opening"


    #מציאת חלקים לתשובות המכילים נושאים שונים
    set_topic = set()
    dic_par = {}
    paragraphs_to_answer = []
    paragraphs_to_answer.append(text_to_answer[0])
    set_topic.update(FindTopic.extract_topics(text_to_answer[0]))
    #מעבר על החלקים לתשובה הכנסה לרשימה את הטקסטים שאין ביניהם נושאים משותפים
    #כאשר יש נושאים משותפים - מכניסים למילון את מספר הטקסט מהרשימה וכמה נושאים משותפים.
    for index, par in enumerate(text_to_answer[1:], start=0):
        par_topic = FindTopic.extract_topics(par)
        overlap = set_topic & set(par_topic)
        if len(overlap) == 0:
            set_topic.update(par_topic)
            paragraphs_to_answer.append(par)
        else:
            dic_par[index+1] = len(overlap)
    print("len(paragraphs_to_answer)")
    print(len(paragraphs_to_answer))

    #במידה ומספר הטקסטים השונים לתשובה קטנים מ 5 נעבור על המילון 
    #ונוסיף את בטקסטים שמספר הנושאים החופפים קטן ביותר עד שנגיעה ל5 טקסטים לתשובה
#    if len(paragraphs_to_answer)<NUM_PARAGRAPHS_TO_ANSWER:
#        mone = NUM_PARAGRAPHS_TO_ANSWER-len(paragraphs_to_answer)
#        while mone>0 and dic_par:
#            sorted_items = sorted(dic_par.items(), key=lambda x: x[1])
#            print(sorted_items)
#            paragraphs_to_answer.append(text_to_answer[sorted_items[0][0]])
#            del dic_par[sorted_items[0][0]]
#            mone-=1
    print()
    print()
    print()
    print("-----------paragraphs to answer-------------")
    print("\n\n\n".join(paragraphs_to_answer))

    answer_final = AnswerBuilding.create_answer(message,"\n".join(paragraphs_to_answer))
    return answer_final




    

        
        








text_to_search = message_handling("How much does it cost to fly from Israel to Greece with El Al in April for one person?")
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
print(text_to_search)

#TavilyAPI.search_in_DB(text_to_search)