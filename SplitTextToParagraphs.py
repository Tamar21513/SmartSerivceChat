import re

#פונקציה המחלקת טקסט על פי מספר מילים
def split_text_to_chunks(text, chunk_size=120, overlap=30):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start += chunk_size - overlap

    return chunks

#בדיקה האם שורה היא כותרת - על פי מספר מילים
def is_title(line, max_title_words):
    line = line.strip()
    if not line:
        return False

    return len(line.split()) <= max_title_words


#פונקציה המקבלת טקסט ומחלקת על פי כותרת ופיסקה
def split_titles_and_large_sections(text, max_title_words=10, max_words_in_section=130, overlap=30):    
    sentences = [sentence.strip() for sentence in re.split(r'\n+(?=[A-Z])', text) if sentence.strip()]
    result = [] 
    current_title = None
    current_content = []    
    for line in sentences:
        if is_title(line, max_title_words=max_title_words):
            if current_title is not None:
                if len(current_content) != 0:
                    full_text = current_title + ". " + " ".join(current_content).strip()
                    word_count = len(full_text.split()) 
                    if word_count <= max_words_in_section:
                        result.append(full_text)
                    else:
                        result.extend(
                            split_text_to_chunks(full_text, chunk_size=max_words_in_section, overlap=overlap)
                        )
                    current_title = line
                else:
                    current_title = current_title + ". " +"".join(line)
            else:
                current_title = line
            current_content = []

        else:
            current_content.append(line)

    # שמירת הקטע האחרון
    if current_title is not None:
        full_text = current_title + ". " + " ".join(current_content).strip()
        word_count = len(full_text.split())

        if word_count <= max_words_in_section:
            result.append(full_text)
        else:
            result.extend(
                split_text_to_chunks(full_text, chunk_size=max_words_in_section, overlap=overlap)
            )

    return result

#text ="""Semantic Search
#Semantic search seeks to improve search accuracy by understanding the semantic meaning of the search query and the corpus to search over. Semantic search can also perform well given synonyms, abbreviations, and misspellings, unlike keyword search engines that can only find documents based on lexical matches.
#Background
#The idea behind semantic search is to embed all entries in your corpus, whether they be sentences, paragraphs, or documents, into a vector space. At search time, the query is embedded into the same vector space and the closest embeddings from your corpus are found. These entries should have a high semantic similarity with the query.
#SemanticSearch
#Symmetric vs. Asymmetric Semantic Search
#A critical distinction for your setup is symmetric vs. asymmetric semantic search:
#For symmetric semantic search your query and the entries in your corpus are of about the same length and have the same amount of content. An example would be searching for similar questions: Your query could for example be “How to learn Python online?” and you want to find an entry like “How to learn Python on the web?”. For symmetric tasks, you could potentially flip the query and the entries in your corpus.
#Related training example: Quora Duplicate Questions.
#Suitable models: Pre-Trained Sentence Embedding Models
#For asymmetric semantic search, you usually have a short query (like a question or some keywords) and you want to find a longer paragraph answering the query. An example would be a query like “What is Python” and you want to find the paragraph “Python is an interpreted, high-level and general-purpose programming language. Python’s design philosophy …”. For asymmetric tasks, flipping the query and the entries in your corpus usually does not make sense.
#Related training example: MS MARCO
#Suitable models: Pre-Trained MS MARCO Models
#It is critical that you choose the right model for your type of task.
#Tip
#For asymmetric semantic search, you are recommended to use SentenceTransformer.encode_query to encode your queries and SentenceTransformer.encode_document to encode your corpus.
#The more general SentenceTransformer.encode method differs in two ways from SentenceTransformer.encode_query and SentenceTransformer.encode_document:
#If no or is provided, it uses a predefined “query” or “document” prompt, if specified in the model’s dictionary.prompt_namepromptprompts
#It sets the to “document”. If the model has a Router module, it will use the “query” or “document” task type to route the input through the appropriate submodules.task
#Note that SentenceTransformer.encode is the most general method and can be used for any task, including Information Retrieval, and that if the model was not trained with predefined prompts and/or task types, then all three methods will return identical embeddings.
#Manual Implementation
#For small corpora (up to about 1 million entries), we can perform semantic search with a manual implementation by computing the embeddings for the corpus with SentenceTransformer.encode_document as well as for our query with SentenceTransformer.encode_query, and then calculating the semantic textual similarity using SentenceTransformer.similarity.
#"""
#
#list = split_titles_and_large_sections(text)
#print(len(list))
#index = 0
#for l in list:
#    print(f"------------------------{index}-------------")
#    index +=1
#    print(l)