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

cursor = conn.cursor()

# Find the category in the DB whose name best matches the given text, by embedding similarity
def search_catgory(text):
    cursor.execute(
        '''
        SELECT category_id , category_name
        FROM Category
        '''
    )
    rows = cursor.fetchall()
    text_emb = FindSimilar.embeddings_encode(text)
    max_similar = 0.0
    max_catgory_id = 0
    max_catgory_name = ""
    for row in rows:
        res_emb = FindSimilar.embeddings_encode(row.category_name)
        similar_emb = FindSimilar.matching_two_vectors(text_emb, res_emb)
        if similar_emb > max_similar:
            max_similar = similar_emb
            max_catgory_id = row.category_id
            max_catgory_name = row.category_name
    return max_catgory_id



# Search a specific company's data, or every company in a category (ordered by priority) if no company was matched
def select_company(topic, company_id, question, user_data, if_has_company, category_id = 0):
    if company_id > 0 and if_has_company == True:
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
        for row in rows:
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
            search_in_db(result, topic, question, user_data)
            if len(dic_list_to_answer[user_data["userId"]]) >= settings["NUM_TO_ANSWER"]:
                break


# Split a "link - .../description - ..." formatted block of text into a list of links and a list of descriptions
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


# Score each link's description against the question and pair/sort the results by similarity, highest first
def matching_to_description(the_question ,titles ,results):
    similarity_scores = matching_percentages(the_question[0] , titles)
    pairs = list(zip(results, similarity_scores))
    filtered = [p for p in pairs if p[1]]
    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered



# Look up the company's stored data for the given topic, fetch and score the linked pages, and store the best answers in the tree
def search_in_db(result, topic, question, user_data):
    dic_BinarySearchTree[user_data["userId"]] = BinarySearchTree()
    if result != None:
        line = result[3].split("\n")
        for l in line:
            if l.split(" - ")[0].lower() == topic.lower():
                search_in = l.split(" - ")[1]
                break
        word = search_in.split(", ")
        for ww in word:
            content_db = result[2].split(ww+":"+"\n")
            content_db = re.search(r"^(.*?)(?=\n[A-Za-z][A-Za-z ]*:\n)",content_db[1],re.DOTALL)
            if not content_db:
                link_and_title = content_db.strip()
            else:
                link_and_title = content_db.group(1).strip()
            links_description = split_to_links_description(link_and_title)
            filtered = matching_to_description(question,  links_description[1], links_description[0])
            urls = []
            for pair in filtered:
                urls.append(pair[0])
            contents = information_from_URL(urls)
            select_most_suitable_simplifyers(contents, question, topic, user_data, result[0])

        dic_list_to_answer[user_data["userId"]].extend(dic_BinarySearchTree[user_data["userId"]].bst_to_list(0,settings["NUM_TO_ANSWER_TO_COMPANY"]))


# Look up a company's id in the DB from its name
def id_company_from_name_company(name_company):
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



# Main entry point for searching the company database: try the named company first, then fall back to its category
def handling_company_database(question,item,topic,name_company, user_data):
    dic_list_to_answer[user_data["userId"]] = []
    company_id = 0
    if name_company !="":
        company_id = id_company_from_name_company(name_company)
    if company_id > 0:
        select_company(topic, company_id, question, user_data, True)
        if len(dic_list_to_answer[user_data["userId"]]) < settings["NUM_TO_ANSWER"]:
            return dic_list_to_answer[user_data["userId"]]
    category_id = search_catgory(item)
    select_company(topic, company_id, question, user_data, False, category_id)
    return dic_list_to_answer[user_data["userId"]]



# Compute the embedding similarity between a search text and a list of titles
def matching_percentages(text_to_search,titles):
    similarity_scores = []
    new_emb = FindSimilar.embeddings_encode(text_to_search).reshape(1, -1)
    titles_emb = FindSimilar.embeddings_encode(titles)
    similarity_scores = cosine_similarity(new_emb, titles_emb)[0]

    return similarity_scores


# Download and extract the readable text content from up to TOP_3 of the given URLs
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
                    pass
                else:
                    contents.append(text)
                    index+=1
        else:
            return contents
    return contents

# Fallback entry point for a general internet search when no matching company data was found
def handling_Internet_database(the_question):
    response = tavilApi.search_in_DB(the_question[0])
    results = response["results"]
    titles = [r["title"].rsplit("-", 1)[0].strip() for r in response["results"]]
    filtered = matching_to_description(the_question, titles, results)
    #top3 = filtered[:settings["TOP_3"]]

    urls = []
    for url in filtered:
        urls.append(url[0]["url"])

    contents = information_from_URL(urls)
    return contents


# Split fetched page contents into paragraphs, extract the best-matching answer sentence from each, score it, and store it in the tree
def select_most_suitable_simplifyers(contents, the_question, category, user_data, start = ""):
    for content in contents:
        paragraphs  = SplitTextToParagraphs.split_titles_and_large_sections(content)
        for par in paragraphs:
            short_sen = distilBert.pipeline_DistilBert(par,the_question[0])
            score = predict_match("topic: " + category + " , question: " + the_question[0] + " , answer: " +  short_sen + " " + start , the_question[1])
            dic_BinarySearchTree[user_data["userId"]].insert_to_string(score,short_sen)




#handling_company_database("how much cost Bamba Nouget?","Bamba Nougat","pricing",0)
