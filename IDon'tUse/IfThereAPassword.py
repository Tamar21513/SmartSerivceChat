#import re
##פונקציה המחזירה נכון במקרה ובטקסט זה יש סיסמה
#def detect_password_phrases_and_patterns(text):
#    #האם יש תבנית סיסמתאי בטקסט
#    password_pattern = re.compile(r'\b(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[_@$!%*?&])[A-Za-z\d_@$!%*?&]{6,}\b')
#    check = password_pattern.findall(text)
#    if len(check)>0:
#        return True
#    
#    #האם יש ביטוי לשוני של סיסמא בטקסט
#    phrases = [
#        "my password is", 
#        "the password is", 
#        "password for this is",
#        "log in with"
#    ]
#
#    for phrase in phrases:
#        if phrase in text.lower():
#            return True
#        
#    
#    return False
#
#
#
#
#print(detect_password_phrases_and_patterns("my name tamar moriel, 9Sd54@$f")) 
#print(detect_password_phrases_and_patterns("my name tamar moriel, and my password is:ASDF"))
#print(detect_password_phrases_and_patterns("my name tamar moriel, and i leav in rechasim"))




#11111111111

import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span 


#טעינת המודל לשפת אנגלית
spacynlp = spacy.load('en_core_web_sm')

#The input text as a Document object
txt ="Natural Language Processing serves as an interrelationship between human language and computers. Natural Language Processing is a subfield of Artificial Intelligence that helps machines process, understand and generate natural language intuitively."
doc = spacynlp(txt)
Tokens = []
for token in doc:
    Tokens.append(token)

print('Tokens:',Tokens)
print('Number of token :',len(Tokens))

matcher = Matcher(spacynlp.vocab)

#יצירת התבניות
pattern_username = [
    {'LOWER': ['username','name']},
    {'IS_PUNCT': True, 'OP': '?'},
    {'IS_ALPHA': True}
]

pattern = [[{'LOWER': 'language'}],[{'LOWER':'human'}]]

#הוספת התבנית לאוביקט
matcher.add("TokenMatch",pattern)

matches = matcher(doc)

#חילוץ התשובה לאחר מענה שקיים
for m_id, start, end in matches:
    string_id = spacynlp.vocab.strings[m_id]  
    span = doc[start:end]
    print('match_id:{}, string_id:{}, Start:{}, End:{}, Text:{}'.format(
        m_id, string_id, start, end, span.text)
         )



#2222222222222222222
#
#import spacy
#from spacy.matcher import PhraseMatcher
#
#spacynlp = spacy.load('en_core_web_sm')
#
#txt ="Natural Language Processing serves as an interrelationship between human language and computers. Natural Language Processing is a subfield of Artificial Intelligence that helps machines process, understand and generate natural language intuitively."
#doc = spacynlp(txt)
#print(doc)
#
#matcher = PhraseMatcher(spacynlp.vocab, attr='LOWER')
#
## list of phrases
#term_list = ["Language Processing", "human language"]
## phrases into document object
#patterns = [spacynlp.make_doc(t) for t in term_list]
#
#matcher.add("Phrase Match", None, *patterns)
#
## Matcher object called. It returns Span objects directly
#matches = matcher(doc, as_spans=True)
##Extracting matched results
#for span in matches:
#    print(span.text,":-", span.label_)