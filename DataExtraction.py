import re
#import Login as login



mapping = {
    "capital A": "A", "uppercase A": "A", "lowercase A": "A", "small A": "a",
    "capital B": "B", "uppercase B": "B", "lowercase B": "b", "small B": "b",
    "capital C": "C", "uppercase C": "C", "lowercase C": "c", "small C": "c",
    "capital D": "D", "uppercase D": "D", "lowercase D": "d", "small D": "d",
    "capital E": "E", "uppercase E": "E", "lowercase E": "e", "small E": "e",
    "capital F": "F", "uppercase F": "F", "lowercase F": "f", "small F": "f",
    "capital G": "G", "uppercase G": "G", "lowercase G": "g", "small G": "g",
    "capital H": "H", "uppercase H": "H", "lowercase H": "h", "small H": "h",
    "capital I": "I", "uppercase I": "I", "lowercase I": "i", "small I": "i",
    "capital J": "J", "uppercase J": "J", "lowercase J": "j", "small J": "j",
    "capital K": "K", "uppercase K": "K", "lowercase K": "k", "small K": "k",
    "capital L": "L", "uppercase L": "L", "lowercase L": "l", "small L": "l",
    "capital M": "M", "uppercase M": "M", "lowercase M": "m", "small M": "m",
    "capital N": "N", "uppercase N": "N", "lowercase N": "n", "small N": "n",
    "capital O": "O", "uppercase O": "O", "lowercase O": "o", "small O": "o",
    "capital P": "P", "uppercase P": "P", "lowercase P": "p", "small P": "p",
    "capital Q": "Q", "uppercase Q": "Q", "lowercase Q": "q", "small Q": "q",
    "capital R": "R", "uppercase R": "R", "lowercase R": "r", "small R": "r",
    "capital S": "S", "uppercase S": "S", "lowercase S": "s", "small S": "s",
    "capital T": "T", "uppercase T": "T", "lowercase T": "t", "small T": "t",
    "capital U": "U", "uppercase U": "U", "lowercase U": "u", "small U": "u",
    "capital V": "V", "uppercase V": "V", "lowercase V": "v", "small V": "v",
    "capital W": "W", "uppercase W": "W", "lowercase W": "w", "small W": "w",
    "capital X": "X", "uppercase X": "X", "lowercase X": "x", "small X": "x",
    "capital Y": "Y", "uppercase Y": "Y", "lowercase Y": "y", "small Y": "y",
    "capital Z": "Z", "uppercase Z": "Z", "lowercase Z": "z", "small Z": "z",
    "exclamation mark": "!", "at": "@", "Underline": "_", "dollar": "$",
    "percent": "%", "sulamit": "#", "asterisk": "*", "question mark": "?", "dot": ".",
}


# רשימת מילים שמסמנות סוף שם
stop_words = ["and", "to", ".",",", "for", "at", "is", "was", "on", "in", "the"]
stop_pattern = "|".join(stop_words)

#לבדיקה האם הסיסמא היא סיסמא חזקה
PASSWORD_RE = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[_@$!%#*?])[A-Za-z\d_@$!%#*?]{8,}$'
#לחלוקת הטקסט מתחילת הסיסמא
PASSWORD_RE2 = r'password\s*(?:is)?\s*:?\s*(.+)$'
USERNAME_RE = r'(?:username|name)\s*(?:is|:)*(?:)?\s*([A-Za-z]+\s*([A-Za-z]+))'
#USERNAME_RE = rf'(?:username|name)\s*(?:is|:)?\s*([A-Za-z]+(?:\s[A-Za-z]+)*?)(?:\s(?:{stop_pattern})|$)'
#לבדיקה האם המייל הוא מייל טוב
EMAIL_RE    = r'\b\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+\b' #צורת מייל
#לחלוקת הטקסט מתחילת המייל ועד
EMAIL_RE2 = r'mail\s*(?:is)?\s*:?\s*(.+)$'



#מחזירה את כל המחרוזת מתחילת הסיסמא ועד הסוף
def Cut_text_from_password(text):
    check = re.search(PASSWORD_RE2, text)
    if check:   
        return check.group(1)
    return ""


#האם הסיסמא היא סיסמא חזקה
def Is_strong_password(text):
    password_pattern = re.compile(PASSWORD_RE)
    check = password_pattern.findall(text)
    if check:    
            return True
    return False


#מחזירה את כל המחרוזת מתחילת המייל ועד הסיסמא
def Cut_the_text_from_mail(text):
    check = re.search(EMAIL_RE2, text)
    if check:   
        return check.group(1)
    return ""


##לבדיקה האם המייל היא מייל טוב
def Check_if_good_mail(text):
    email_pattern = re.compile(EMAIL_RE)
    check = email_pattern.findall(text)
    if check:    
            return True
    return False

#פונקציה לנרמול המייל והסיסמא על ידי המילון
def Build_from_mapping(text,name_funcation):
    words = text.split()
    result = ""
    i = 0
    while i<len(words) and (name_funcation(result) == False):
        if i + 1 < len(words):
            sen = " ".join(words[i:i+2])
            if sen in mapping:
                result+=(mapping[sen])
                i+=2
                continue
            result += mapping.get(words[i], words[i])
        i+=1
    return result

#חילוץ מייל
def Mail_extraction(text):
    result = Build_from_mapping(text, Check_if_good_mail)
    if Check_if_good_mail(result) == True:
        return result
    else:
        return "None"

#חילוץ סיסמא
def Password_extraction(text):
    result = Build_from_mapping(text, Is_strong_password)
    if Is_strong_password(result) == True:
        return result
    else:
        return "None"


#חילוץ שם משתמש
def Username_extraction(text):
    check = re.search(USERNAME_RE, text)
    if check:
        return check.group(1)
    else:
        return "None"





#שליפת מייל סיסמא ושם של המתשמש מתוך טקסט
def Mail_password_username_extraction(text):
    arrResult =["None"]*3
    #שליפת המייל
    textLower = text.lower()
    raw_text = Cut_the_text_from_mail(textLower)
    clean_text =  raw_text.replace(",", "")
    arrResult[0] = Mail_extraction(clean_text)

    #שליפת הסיסמא
    raw_text = Cut_text_from_password(text)
    clean_text =  raw_text.replace(",", "").replace(".", "")
    arrResult[1] = Password_extraction(clean_text)

    #שליפת השם
    textLower = text.lower()
    arrResult[2] = Username_extraction(textLower)
    #החזרת המערך
    return arrResult




def If_exists_inDB(text):
    if text != None:
        print(text)
        arr = Mail_password_username_extraction(text)
        print('\n')
        print("mail:"+ arr[0])
        print("password:"+ arr[1])
        print("username:"+ arr[2])
        detail = arr[0]
        if arr[0] == "None":
            detail = arr[2]
        print("detail: "+detail)
        login.login_user(detail,arr[1])


#שם+מייל+סיסמא
#If_exists_inDB(r"C:\Tamarush\programming\project\ChatTM\Audios\name_mail_password6.mp3")
#שם+סיסמא
#IfExsistInDB(r"C:\Tamarush\programming\project\ChatTM\Audios\tamarMoriel.mp3")

#def CheckIfGood():
#    sentences = ["my name temar shalom , yael1@gmail.com and my password capital a capital a small s 485 #15 end",
#                 "Hello!! username: Mosh Choen, email: mc123456@gmail.com, password: As485#15 HI",
#                 "Hello!! name: Tamar moriel, and the password is Ab215131129! goodby",
#                 "Hello!! my name is: shoshi david, my email is yael3@gmail.com and the password is My_Pass1 tanke tou",
#                 " my username is thila levi email: yael4@gmail.com , my password is: 1234 ",
#                 " my name is Yael chazon , ",
#                 " my password is Abhd45!mk "]
#
#
#    for sen in sentences:
#        IfExsistInDB(sen)
     


#CheckIfGood()



##ניסוי חילוץ סיסמא
#def exex(text):
#    match1 = re.search(PASSWORD_RE2 , text)
#
#    if match1:    
#        print(match1.group())
#        match2 = re.search(PASSWORD_RE , match1.group())
#        if match2:
#            return match2.group()
#    return None


#בדיקה אם קיים טקסט מובנה
#def is_structured(text):
#    lowerText = text.lower()
#    return (
#        (re.search(USERNAME_RE, lowerText) or
#        re.search(EMAIL_RE, lowerText)) and
#        re.search(PASSWORD_RE, text)
#    )
    #return bool(re.search(r'(username|email|password)\s*[:=]', text.lower()))
   
#USERNAME_RE = r'username\s*[:=]\s*\S+'
#USERNAME_RE1 = r'(username|name)\s*(?:is|:)*(?:)?\s*([a-z])+\s*([a-z][^0-9])*\S'
#PASSWORD_RE = r'\s(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[_@$!%*?&]).{6,}\s' #לפחות אות אחת גדולה אות קטנה מספר ותו מהרשימה סה"כ לפחות 6 תוים
#PASSWORD_RE1 = r'password\s*(?:is|:)?\s*(\S+)' #לפחות אות אחת גדולה אות קטנה מספר ותו מהרשימה סה"כ לפחות 6 תוים
#PASSWORD_RE2 = r'password\s*(?:is|:)?\s*(\S+)(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[_@$!%*?&]).{6,}\s' #לפחות אות אחת גדולה אות קטנה מספר ותו מהרשימה סה"כ לפחות 6 תוים
#PASSWORD_RE3 = r'\b(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[_@$!%*?&])[A-Za-z\d_@$!%*?&]{6,}\b'

#חילוץ שם מתוך טקסט
#def userNameExtraction(text):
#    lowerText = text.lower()
#    userName_pattern = re.compile(USERNAME_RE)
#    check = userName_pattern.findall(lowerText)
#    if check:    
#            return check[0][1]+' '+ check[0][2]
#    return None


#חילוץ מייל מתוך טקסט
#def emailExtraction(text):
#    lowerText = text.lower()
#    check = re.search(EMAIL_RE, lowerText)
#    if check:
#        return check.group()
#    return None
#
#
##חילוץ שם מתוך טקסט
#def userNameExtraction(text):
#    textL = text.lower()
#    check = re.search(USERNAME_RE, textL)
#    if check:
#        return check.group(1)
#    return None


   #check = re.search(EMAIL_RE, text)
   #if check:
   #    arrResult[0] = check.group()