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
    # Initialize a tree node holding a key and its associated value
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    # Initialize an empty binary search tree
    def __init__(self):
        self.Root = None
    # Insert a string key/value pair into the tree using plain key comparison
    def insert_to_string(self,key,value):
        self = self
        new_node = Node(key,value)
        if self.Root == None:
            self.Root = new_node
            return
        current = self.Root
        while current!=None:
            if current.key > new_node.key:
                if current.left == None:
                    current.left = new_node
                    return
                current = current.left
            elif current.right == None:
                current.right = new_node
                return
            else:
                current = current.right

    # Insert a "things the user has" entry into the tree, comparing keys by embedding similarity
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

    # Insert a conversation-topic entry into the tree, comparing keys by embedding similarity
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


    # Recursively collect up to NUM_TO_ANSWER node values from the tree, highest key to lowest
    def bst_to_list_from_high_to_low(self,node,lst_text, len_par_to_anser, NUM_TO_ANSWER):
        if node is None or len(lst_text)+len_par_to_anser == NUM_TO_ANSWER:
            return lst_text
        lst_text = self.bst_to_list_from_high_to_low(node.right,lst_text, len_par_to_anser, NUM_TO_ANSWER)
        if len(lst_text)+len_par_to_anser<NUM_TO_ANSWER:
            lst_text.append(node.value)
        if len(lst_text)+len_par_to_anser<NUM_TO_ANSWER:
            lst_text = self.bst_to_list_from_high_to_low(node.left,lst_text, len_par_to_anser, NUM_TO_ANSWER)
        return lst_text

    # Entry point that returns the list of the best-matching segments from the tree
    def bst_to_list(self, len_par_to_anser , NUM_TO_ANSWER):
        lst_text = []
        lst_text = self.bst_to_list_from_high_to_low(self.Root,lst_text,len_par_to_anser, NUM_TO_ANSWER)
        return lst_text

    # Recursively traverse the tree (right, node, left) and collect its topics/content as strings
    def print_tree(self,node_child,list_str):
        if node_child == None:
            return list_str
        list_str = self.print_tree(node_child.right,list_str)
        list_str.append(str(node_child.value.thingsTheUserHasTopic))
        for detail in node_child.value.thingsTheUserHasContent:
            list_str.append(str(detail))
        list_str.append(" \n")
        list_str = self.print_tree(node_child.left,list_str)
        return list_str



    # Return the whole tree as a newline-joined string ready for SQL insertion
    def tree_to_str(self):
        list_str = []
        list_str = self.print_tree(self.Root,list_str)
        return "\n".join(list_str)



    # Recursively search the tree for the node matching the given topic/text, inserting a new one if needed
    def search_node_in_tree(self,node,text_emb,text,issue):
        if node == None:
            if issue == "topics":
                return self.insert_the_item_into_node(node,text_emb,text,"",issue)
            else:
                return None
        if FindSimilar.matching_two_vectors(text_emb, node.key)>settings["60_percent"]:
            if FindSimilar.matching_two_vectors(text_emb, node.key)<settings["80_percent"]:
                return self.search_node_in_tree(node.right, text_emb,text,issue)
            if issue == "topics":
                node = self.insert_the_item_into_node(node,text_emb,node.value.thingsTheUserHasTopic ,text,issue)
            return node
        return self.search_node_in_tree(node.left, text_emb,text,issue)


    # Insert a new value into the tree at this node, or append text to an existing matching node
    def insert_the_item_into_node(self,node,text_emb,title,text,issue):
        if node == None:
            thing = ThingsTheUserHas(thingsTheUserHasId= 0, userId = 0 , thingsTheUserHasTopic = title , thingsTheUserHasContent=[text] if title != text else [])
            if issue == "topics":
                self.insert_to_topic(text_emb,thing)
            else:
                self.insert_to_things(text_emb,thing)
            return  Node(text_emb, thing)
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

