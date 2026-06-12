import FindSimilar
from RuntimeSettings import load_runtime_settings
from pydantic import BaseModel
from typing import List

settings = load_runtime_settings()

class ThingsTheUserHas(BaseModel):
    thingsTheUserHasId: int
    userId: int
    thingsTheUserHasTopic: str = ""
    thingsTheUserHasContent: List[str] = []

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.Root = None
    #הכנסת מחרוזת לעץ
    def insert_to_string(self,key,value):
        self = self
        #יצירת צומת חדשה
        new_node = Node(key,value)
        #אם הוא עץ חדש
        if self.Root == None:
            self.Root = new_node
            return 
        #מצביע לראש העץ
        current = self.Root
        #עובר על עץ - כל עוד המצביע לא שווה ל None 
        while current!=None:
            #אם הערך שלהצומת גדולה הערך הצומת החדשה 
            if current.key > new_node.key:
                if current.left == None:
                    # הגענו לסוף העץ - מכניסים את הצומת החדשה
                    current.left = new_node
                    return
                #פונים לשמאל
                current = current.left
            #אחרת  - הגענו לסוף העץ - מכניסים את הצומת החדשה
            elif current.right == None:
                current.right = new_node
                return
            else:
                #פונים ימין
                current = current.right
    
    #הכנסת מבנה - דברים שיש לו
    def insert_to_things(self,key,value):
        self = self
        new_node = Node(key,value)

        if self.Root == None:
            self.Root = new_node
            return 
        
        current = self.Root

        while current!=None:
            if settings["HALF"] > FindSimilar.matching_two_vectors(new_node.key, current.key):
                if current.left == None:
                    current.left = new_node
                    return
                current = current.left
            elif current.right == None:
                current.right = new_node
                return
            else:
                current = current.right

    #הכנסת מבנה לנושאי שיחה
    def insert_to_topic(self,key,value):
        self = self
        new_node = Node(key,value)

        if self.Root == None:
            self.Root = new_node
            return 
        
        current = self.Root

        while current!=None:
            if settings["HALF"] > FindSimilar.matching_two_vectors(new_node.key, current.key):
                if current.left == None:
                    current.left = new_node
                    return
                current = current.left
            elif current.right == None:
                current.right = new_node
                return
            else:
                current = current.right
    

    #פונקציה מחזירה מספר מסוים של קטעים שהמפתח שלהם הגבוה ביותר - מהגבוה לנמוך
    def bst_to_list_from_high_to_low(self,node,lst_text, len_par_to_anser, NUM_TO_ANSWER):
        #אם הגעת למספר או שהחוליה שאליה הגעת - תחזיר את הרשימה
        if node is None or len(lst_text)+len_par_to_anser == NUM_TO_ANSWER:
            return lst_text
        #זימון לימין
        lst_text = self.bst_to_list_from_high_to_low(node.right,lst_text, len_par_to_anser, NUM_TO_ANSWER)
        #טיפול באמצעי
        #אם אורך הרשימה קטן מ NUM_TO_ANSWER תוסיף את הקטע לרשימה
        if len(lst_text)+len_par_to_anser<NUM_TO_ANSWER:
            lst_text.append(node.value)
        #אם עדין אורך הרשימה קטן מ NUM_TO_ANSWER - זימון לשמאל
        if len(lst_text)+len_par_to_anser<NUM_TO_ANSWER:
            lst_text = self.bst_to_list_from_high_to_low(node.left,lst_text, len_par_to_anser, NUM_TO_ANSWER)
        #החזרת הרשימה
        return lst_text
    
    #פונקצית תווך למציאת מספר קטעים המתאימים ביותר
    def bst_to_list(self, len_par_to_anser , NUM_TO_ANSWER):
        #רשימת הקטעים
        lst_text = []
        #זימון הפונקציה למציאת מספר הקטעים המתאימים ביורת
        lst_text = self.bst_to_list_from_high_to_low(self.Root,lst_text,len_par_to_anser, NUM_TO_ANSWER)
        #החזרת רשימת הקטעים
        return lst_text
    
    #מעבר על עץ
    def print_tree(self,node_child,list_str):
        if node_child == None:
            return list_str
        #זימון לימין
        list_str = self.print_tree(node_child.right,list_str)
        list_str.append(str(node_child.value.thingsTheUserHasTopic))
        for detail in node_child.value.thingsTheUserHasContent:
            list_str.append(str(detail))
        list_str.append(" \n")
        #זימון לשמאל
        list_str = self.print_tree(node_child.left,list_str)
        #החזרת הרשימה
        return list_str



    #החזרת העץ כטקסט מוכן להכנסה ל SQL
    def tree_to_str(self):
        list_str = []
        list_str = self.print_tree(self.Root,list_str)
        print("\n".join(list_str))
        return "\n".join(list_str)



    #חיפוש הצומת המתאימה לנושא
    def search_node_in_tree(self,node,text_emb,text,issue):
        if node == None:
            #אם מתבצע חיפוש בנושאי השיחה
            if issue == "topics":
                #יצירת צומת חדשה עם נושא
                return self.insert_the_item_into_node(node,text_emb,text,"",issue)
            else:
                #אם זה משהו שיש לו - להוסיף חוליה חדשה
                return None
        print(node.value.thingsTheUserHasTopic)
        print(FindSimilar.matching_two_vectors(text_emb, node.key))
        if FindSimilar.matching_two_vectors(text_emb, node.key)>settings["60_percent"]:
            if FindSimilar.matching_two_vectors(text_emb, node.key)<settings["80_percent"]:
                return self.search_node_in_tree(node.right, text_emb,text,issue)
            if issue == "topics":
                #אם נמצא צומת מתאימה - הוספת הנתון לצומת
                node = self.insert_the_item_into_node(node,text_emb,node.value.thingsTheUserHasTopic ,text,issue)
            return node
        return self.search_node_in_tree(node.left, text_emb,text,issue)
    

    #הכנסת הערך לצומת העץ
    def insert_the_item_into_node(self,node,text_emb,title,text,issue):
        if node == None:
            thing = ThingsTheUserHas(thingsTheUserHasId= 0, userId = 0 , thingsTheUserHasTopic = title , thingsTheUserHasContent=[text] if title != text else [])
            if issue == "topics":
                self.insert_to_topic(text_emb,thing)
            else:
                self.insert_to_things(text_emb,thing)
            print(node)
            return  Node(text_emb, thing)
        #אם פרט זה קיים כבר במאגר - לא להכניס ולהחזיר את הצומת
        if title.lower() == node.value.thingsTheUserHasTopic.lower() and text.lower() in node.value.thingsTheUserHasContent or text.lower() == node.value.thingsTheUserHasTopic.lower() :
            return node
        node.value.thingsTheUserHasContent.append(text)
        return node
    






            

        




#
#items = [
#    ("B", 8),
#    ("D", 3),
#    ("A", 10),
#    ("E", 1),
#    ("C", 6),
#    ("AB", 18),
#    ("AD", 13),
#    ("AA", 110),
#    ("AE", 11),
#    ("AC", 16),
#    ("BB", 81),
#    ("BD", 31),
#    ("BA", 101),
#    ("BE", 13),
#    ("BC", 63),
#    ("CB", 83),
#    ("CD", 33),
#    ("CA", 103),
#    ("CE", 13),
#    ("CC", 63)
#]
#tree = BinartSearchThree()            
#for item in items:
#    tree.insert(item[1],item[0])            
#lst_text = tree.bst_to_list_15()
#print(lst_text)

