from pydantic import BaseModel
from typing import List
from ConnectedWithReactAndC.SharedDataStructure import tree_things
from fastapi import APIRouter

router  = APIRouter()

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import FindSimilar



class ThingsTheUserHas(BaseModel):
    thingsTheUserHasId: int
    userId: int
    thingsTheUserHasTopic: str = ""
    thingsTheUserHasContent: List[str] = []


@router.post("/things-the-user-has")
def building_tree_things_the_user_has(data: ThingsTheUserHas):
    print("User ID:", data.userId)
    print("Things ID:", data.thingsTheUserHasId)
    print("Topic:", data.thingsTheUserHasTopic)
    print("Content list:", data.thingsTheUserHasContent)

    degel = False
    for top in data.thingsTheUserHasContent[0].split('\n'):
        if degel == False:
            degel = True
            thing = ThingsTheUserHas(thingsTheUserHasId = data.thingsTheUserHasId, userId = data.userId, thingsTheUserHasTopic = top , thingsTheUserHasContent=[])
            continue
        if len(top)<2:
            degel = False
            tree_things.insert_to_things(FindSimilar.embeddings_encode(thing.thingsTheUserHasTopic),thing)
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