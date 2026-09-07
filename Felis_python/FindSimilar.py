import numpy as np
import CreateTopicListFromDB as cTopicList
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import util
from ModelManager import embedding_model
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()


model_embedder = embedding_model

# Encode text (or list of texts) into a numeric embedding vector using the sentence embedder
def embeddings_encode(list_text):
    return model_embedder.encode(list_text)



# Return the file paths whose topics have a similarity score at or above the configured threshold
def get_similar_topic_indexes(similarity_scores,folder_path):
    get_row_indexes = lambda arr: [i for i, row in enumerate(arr) if np.any(row >= settings["SIMILARITY_THRESHOLD"])]
    arr_indexes = get_row_indexes(similarity_scores)
    phats_to_similar_topic =  cTopicList.phat_to_similar_topics(arr_indexes,folder_path)
    return phats_to_similar_topic

# Compute the cosine similarity between two embedding vectors, reshaping either if needed
def matching_two_vectors(new_emb,topic_emb):
    if topic_emb.ndim == 1:
        topic_emb = topic_emb.reshape(1, -1)
    if new_emb.ndim == 1:
        new_emb = new_emb.reshape(1, -1)
    return cosine_similarity(new_emb,topic_emb)[0]


# Find the previous-conversation summary files whose topics are similar to a new topic
def find_similar_topic_to_new_text(folder_path,new_topic):
    similarity_scores = []

    topics_dict = cTopicList.create_topic_list(folder_path)

    new_emb = embeddings_encode(new_topic)
    key_txt_list = list(topics_dict.keys())
    values_topics_list = list(topics_dict.values())
    i = 0
    for value in values_topics_list:
        i+=1
        topic_emb = embeddings_encode(value)
        similarity_scores.append(matching_two_vectors(new_emb,topic_emb))
    paths_to_similar_topic = get_similar_topic_indexes(similarity_scores,folder_path)
    return paths_to_similar_topic






# Find the corpus text segments most semantically similar to a question, for use in answering it
def semantic_search_from_corpus(corpus,question):
    corpus_embeddings = model_embedder.encode(corpus, convert_to_tensor=True)

    top_k = min(settings["NUM_SENTENCES"], len(corpus))
    query_embedding = model_embedder.encode(question, convert_to_tensor=True)

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
#text = """
#The customer called to check on the status of his order. The product he ordered did not arrive on time, and he wants to know when the shipment will arrive and what to do in case of a delay.
#"""
#
#topic_model = BERTopic(min_topic_size=1)
#
#topics, probs = topic_model.fit_transform([text])
#
#topic_id = topics[0]
#representative_words = topic_model.get_topic(topic_id)


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
#"""
#
#kw_model = KeyBERT()
#
#keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='hebrew', top_n=5)

#-------Sentence-Transformers + cosine similarity----------------------------

#import os
#os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
#
#



#-------paraphrase-MiniLM-L3-v2----------------------------

#from sentence_transformers import SentenceTransformer
#model = SentenceTransformer("paraphrase-MiniLM-L3-v2")