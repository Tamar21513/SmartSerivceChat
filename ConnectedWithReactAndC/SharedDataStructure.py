import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


from BinarySearchTree import BinarySearchTree

tree_things = BinarySearchTree()


list_question_answer = []


def insert_to_things(self, key, value):
    tree_things.insert_to_things(key,value)