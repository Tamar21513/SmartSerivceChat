import inflect
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet

#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('punkt_tab')
#nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger_eng')



p = inflect.engine()
trans = str.maketrans('', '', string.punctuation)
Lemmatizer = WordNetLemmatizer() 

# Replace standalone digit tokens in text with their spelled-out word form
def numbers_to_words(text):
    sen1 = text.split()
    result=[]
    for word in sen1:
        if word.isdigit():
            result.append(p.number_to_words(word))
        else:
            result.append(word)
    return ' '.join(result)


# Strip all punctuation characters from the text
def remove_punctuation(text):
    new_text = text.translate(trans)
    return new_text


# Collapse repeated whitespace into single spaces
def remove_extra_whitespace(text):
    return " ".join(text.split())

# Remove English stop words from the text, keeping "to"
def removing_stop_words(text):
    new_text = [w for w in text.split() if (w not in stopwords.words('english') or w == "to")]
    return " ".join(new_text)


#def find_lemmatizer(text):
#    return [[Lemmatizer.lemmatize(word[0], pos=get_wordnet_pos(word[1])),word[1]] for word in text]


#def pos_tag_tokens(text):
#    if isinstance(text, str):
#        text = word_tokenize(text)
#    return pos_tag(text)

#def get_wordnet_pos(treebank_tag):
#    if treebank_tag.startswith('J'):
#        return wordnet.ADJ
#    elif treebank_tag.startswith('V'):
#        return wordnet.VERB
#    elif treebank_tag.startswith('N'):
#        return wordnet.NOUN
#    elif treebank_tag.startswith('R'):
#        return wordnet.ADV
#    else:
#        return wordnet.NOUN




# Run the full text-cleaning pipeline: numbers to words, punctuation removal, whitespace cleanup, stop-word removal
def text_cleaning(text):
    text = numbers_to_words(text)
    text = remove_punctuation(text)
    text = remove_extra_whitespace(text)
    text = removing_stop_words(text)
    return text






#text = text_cleaning("Hey, did you know that       the summer break is coming? Amazing right !! It's only 5 more days !!")
#print(text)
#print(text_cleaning("How much does a flight to Greece cost in April for one person?"))




