import numpy as np
import CreateTopicListFromDB as cTopicList
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import util
from ModelManager import embedding_model
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()


model_embedder = embedding_model

#פונקציה שממירה מטקסט לוקטור מספרי
def embeddings_encode(list_text):
    return model_embedder.encode(list_text)



#פונקציה שמחזירה את הניתובים לקבצים שאחד מהנושאים שלהם גדול שווה ל 0.6
def get_similar_topic_indexes(similarity_scores,folder_path):
    #פונקציה מקוצרת שמחזירה את כל האינדקסים של הנושאים שההתאמה שלהם למשפט החדש גדול מ 0.6
    get_row_indexes = lambda arr: [i for i, row in enumerate(arr) if np.any(row >= settings["SIMILARITY_THRESHOLD"])]
    #זימון הפונקציה על המערך של ה similarity_scores
    arr_indexes = get_row_indexes(similarity_scores)
    phats_to_similar_topic =  cTopicList.phat_to_similar_topics(arr_indexes,folder_path)
    return phats_to_similar_topic

#מציאת אחוזי התאמה בין שני וקטורים
def matching_two_vectors(new_emb,topic_emb):
    #בודק שהוקטור במימד 2
    if topic_emb.ndim == 1:
        topic_emb = topic_emb.reshape(1, -1)
    #בודק שהוקטור במימד 2
    if new_emb.ndim == 1:
        new_emb = new_emb.reshape(1, -1)
    #מציאת אחוזי התאמה בין הוקטורים של הנושאים לוקטור של הנושא החדש
    return cosine_similarity(new_emb,topic_emb)[0]


#פונקציה המחזירה את הניתובים לנושאים הדומים לנושא החדש מתוך סיכומי השיחות הקודמו של אותו לקוח
def find_similar_topic_to_new_text(folder_path,new_topic):
    similarity_scores = []

    #יצירת מטריצת נושאים קודמים
    topics_dict = cTopicList.create_topic_list(folder_path)

    #המרת הנושא החדש לוקטור מספרי
    new_emb = embeddings_encode(new_topic)
    # המרת הערכים לרשימה מתוך המילון
    key_txt_list = list(topics_dict.keys())
    values_topics_list = list(topics_dict.values())
    i = 0
    for value in values_topics_list:
        print(key_txt_list[i])
        i+=1
        #המרה לוקטור מספרי - עבור כל נושא
        topic_emb = embeddings_encode(value)
        similarity_scores.append(matching_two_vectors(new_emb,topic_emb))
    print(similarity_scores)
    #זימון הפעולה
    paths_to_similar_topic = get_similar_topic_indexes(similarity_scores,folder_path)
    return paths_to_similar_topic






#מציאת אזורי טקסטים הדומים לשאלה - לצורך מענה
def semantic_search_from_corpus(corpus,question):
    # יצירת וקטור לקורפוסים
    corpus_embeddings = model_embedder.encode(corpus, convert_to_tensor=True)

    # מציאת  5settings["NUM_SENTENCES"]  המשפטים הקרובים ביותר בקורפוס עבור כל השאלה בדמיון סמנטי
    top_k = min(settings["NUM_SENTENCES"], len(corpus))
    # יצירת וקטור לשאלה
    query_embedding = model_embedder.encode(question, convert_to_tensor=True)

    # 
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)
    hits = hits[0]
    return hits












#print('\n')
#print('------------1---------')
#print(find_similar_topic_to_new_text(r'C:\Tamarush\programming\project\ChatTM\Felis_python\ConversationSummaries\tamar_moriel',"JBL speaker"))
#print('\n')
#print('------------2---------')
#print(find_similar_topic_to_new_text(r'C:\Tamarush\programming\project\ChatTM\Felis_python\ConversationSummaries\tamar_moriel',"I need help with connecting my JBL speaker to my phone."))



#-------BERTopic----------------------------

#from bertopic import BERTopic
#
## טקסט ראשוני של שיחה
#text = """
#The customer called to check on the status of his order. The product he ordered did not arrive on time, and he wants to know when the shipment will arrive and what to do in case of a delay.
#"""
#
## יוצרים מודל BERTopic
#topic_model = BERTopic(min_topic_size=1) 
#
## מריצים fit_transform על המסמך היחיד
#topics, probs = topic_model.fit_transform([text])
#
## מזהים את הנושא והביטויים המרכזיים
#topic_id = topics[0]
#representative_words = topic_model.get_topic(topic_id)

#print("נושא (ID):", topic_id)
#print("מילים מייצגות לנושא:", representative_words)


#-------BERTopic Steps----------------------------


#from umap import UMAP
#from hdbscan import HDBSCAN
#from sentence_transformers import SentenceTransformer
#from sklearn.feature_extraction.text import CountVectorizer
#
#from bertopic import BERTopic
#from bertopic.representation import KeyBERTInspired
#from bertopic.vectorizers import ClassTfidfTransformer
#
#
## Step 1 - Extract embeddings
#embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
#
## Step 2 - Reduce dimensionality
#umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')
#
## Step 3 - Cluster reduced embeddings
#hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
#
## Step 4 - Tokenize topics
#vectorizer_model = CountVectorizer(stop_words="english")
#
## Step 5 - Create topic representation
#ctfidf_model = ClassTfidfTransformer()
#
## Step 6 - (Optional) Fine-tune topic representations with
## a `bertopic.representation` model
#representation_model = KeyBERTInspired()
#
## All steps together
#topic_model = BERTopic(
#  embedding_model=embedding_model,          # Step 1 - Extract embeddings
#  umap_model=umap_model,                    # Step 2 - Reduce dimensionality
#  hdbscan_model=hdbscan_model,              # Step 3 - Cluster reduced embeddings
#  vectorizer_model=vectorizer_model,        # Step 4 - Tokenize topics
#  ctfidf_model=ctfidf_model,                # Step 5 - Extract topic words
#  representation_model=representation_model # Step 6 - (Optional) Fine-tune topic representations
#)



#-------KeyBert----------------------------

#from keybert import KeyBERT
#
#text = """
#הלקוח התקשר כדי לבדוק מה מצב ההזמנה שלו. המוצר שהזמין לא הגיע בזמן, והוא רוצה לדעת מתי המשלוח יגיע ומה אפשר לעשות במקרה של עיכוב.
#"""
#
## יוצרים מודל KeyBERT
#kw_model = KeyBERT()
#
## מחפשים 5 מילות מפתח מרכזיות
#keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='hebrew', top_n=5)
#
#print("מילות מפתח מרכזיות:", keywords)

#-------Sentence-Transformers + cosine similarity----------------------------

#בשביל עקיפת NETFREE
#import os
#os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
#
#



#-------paraphrase-MiniLM-L3-v2----------------------------

#from sentence_transformers import SentenceTransformer
#model = SentenceTransformer("paraphrase-MiniLM-L3-v2")