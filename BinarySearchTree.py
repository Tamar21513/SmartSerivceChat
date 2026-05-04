NUM_TO_ANSWER = 10

class Node:
    def __init__(self, key, text):
        self.key = key
        self.text = text
        self.left = None
        self.right = None
i = 0
class BinartSearchThree:
    def __init__(self):
        self.Root = None
    
    def insert(self,number,text):
        self = self
        new_node = Node(number,text)

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

    def bst_to_list_from_high_to_low(self,node,lst_text):
        if node is None or len(lst_text) == NUM_TO_ANSWER:
            return lst_text
        lst_text = self.bst_to_list_from_high_to_low(node.right,lst_text)
        if len(lst_text)<NUM_TO_ANSWER:
            lst_text.append(node.text)
        if len(lst_text)<NUM_TO_ANSWER:
            lst_text = self.bst_to_list_from_high_to_low(node.left,lst_text)

        return lst_text

    def bst_to_list_10(self):
        lst_text = []
        lst_text = self.bst_to_list_from_high_to_low(self.Root,lst_text)
        return lst_text



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

