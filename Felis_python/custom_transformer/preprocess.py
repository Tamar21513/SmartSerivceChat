import re
# Normalize text by spacing out punctuation, collapsing whitespace, and lowercasing
def my_split(text: str)->str:
    text = re.sub(r"([.,!?;:])", r" \1 ", text)
    text=re.sub(r"[\r\n\t]+"," ",text)
    text = re.sub(r"\s+", " ", text).strip()
    text=text.lower()
    return text
