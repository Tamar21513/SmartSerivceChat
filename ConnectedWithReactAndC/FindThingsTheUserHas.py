from ConnectedWithReactAndC.SharedDataStructure import dic_tree_things
from fastapi import APIRouter
from BinarySearchTree import ThingsTheUserHas,BinarySearchTree

router  = APIRouter()

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import FindSimilar




@router.post("/things-the-user-has")
def building_tree_things_the_user_has(data: ThingsTheUserHas):
    print("User ID:", data.userId)
    print("Things ID:", data.thingsTheUserHasId)
    print("Topic:", data.thingsTheUserHasTopic)
    print("Content list:", data.thingsTheUserHasContent)
    dic_tree_things[data.userId] = BinarySearchTree()
    degel = False
    for top in data.thingsTheUserHasContent[0].split('\n'):
        if degel == False:
            degel = True
            thing = ThingsTheUserHas(thingsTheUserHasId = data.thingsTheUserHasId, userId = data.userId, thingsTheUserHasTopic = top , thingsTheUserHasContent=[])
            continue
        if len(top)<2:
            degel = False
            dic_tree_things[data.userId].insert_to_things(FindSimilar.embeddings_encode(thing.thingsTheUserHasTopic),thing)
            print(thing)
            continue
        if degel == True:
            thing.thingsTheUserHasContent.append(top)
            continue


    return {
        "success": True,
        "message": "Python received ThingsTheUserHas successfully",
        "userId": data.userId,
        "contentCount": len(data.thingsTheUserHasContent)
    }




#לא בשימוש
#מציאת הצומת המתאימה לנושא והכנסתו לעץ
#def find_thing_that_user_has_in_tree(topic):
#    node_tree = tree_things.search_node_in_tree(tree_things.Root,FindSimilar.embeddings_encode(topic.thingsTheUserHasTopic),topic.thingsTheUserHasTopic)
#    print(node_tree)


