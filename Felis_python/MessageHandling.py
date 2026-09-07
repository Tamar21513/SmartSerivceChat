import FindSimilar
import AnswerBuilding
import CategorizedByTopic
import JsonToTopic
import JsonFilling
from BinarySearchTree import BinarySearchTree
from ConnectedWithReactAndC.SharedDataStructure import dic_tree_things, dic_BinarySearchTree
from RuntimeSettings import load_runtime_settings
import SearchInDB

settings = load_runtime_settings()



# Build the shortened search question and its per-word token weights from the filled-in JSON
def build_question(json):
    the_question = []
    token_weights = [0.2,3.0, 1.0, 1.0]
    search = json["search"]
    for item in search:
        bool = False
        if "text_if_field_exists" in item:
            bool = True
        field = item["field"]
        if json[field] == '':
            bool = False
            continue
        if bool ==  True:
            the_question.append(item["text_if_field_exists"])
            token_weights.append(1.0)
            bool = False
        the_question.append(json[field])
        for word in json[field].split(" "):
            token_weights.append(item["token_weight"])
    return [" ".join(the_question) , token_weights]


# Return the list of required JSON fields (other than "brand") that are still empty
def if_everything_full(json):
    missing_item = []
    required = json["required"]
    for item in required:
        if item != "brand":
            if json[item] == "":
                missing_item.append(item)
    return missing_item

# Fill in missing required fields by searching the chat's topics tree and the user's "things" tree, or from user_data
def finding_missing_details(json_question, user_data, chat_history):
    search_missing_details = json_question["search_missing_details"]
    details_topics = None
    details = None
    for item in search_missing_details:
        if json_question[item["if_field_exists"]] != "":
            where_search = ""
            if details_topics == None:
                details_topics = chat_history["topics_tree"].search_node_in_tree(chat_history["topics_tree"].Root, FindSimilar.embeddings_encode(json_question[item["if_field_exists"]]),json_question[item["if_field_exists"]],"topics")
            for detail in item["if_fields_missing"]:
                if json_question[detail["field"]] == "":
                    where_search = item["search_missing_value_in"]
                    if where_search == "ThingsTathUserHas":
                        json_question = JsonFilling.json_filling_form_missing_details(json_question,details_topics.value.thingsTheUserHasContent,detail)
                        if details_topics == None or json_question[detail["field"]] == "":
                            details = dic_tree_things[user_data["userId"]].search_node_in_tree(dic_tree_things[user_data["userId"]].Root,FindSimilar.embeddings_encode(json_question[item["if_field_exists"]]),json_question[item["if_field_exists"]],"things")
                        if details != None:
                            json_question = JsonFilling.json_filling_form_missing_details(json_question,details.value.thingsTheUserHasContent,detail)
                    else:
                        json_question[detail["field"]] = user_data.get(detail["search_value"],"")
                details_topics = chat_history["topics_tree"].insert_the_item_into_node(details_topics, FindSimilar.embeddings_encode(json_question[item["if_field_exists"]]) , json_question[item["if_field_exists"]], json_question[detail["field"]],"topics")
    return json_question






# Main pipeline for handling an incoming user message: classify it, fill in its JSON, find missing details, and build an answer
def message_handling(text, user_data,chat_history):
    #tree_things.print_tree(tree_things.Root)
    topic = CategorizedByTopic.categories(text)
    json_question = JsonToTopic.get_json(topic)
    json_question = JsonFilling.json_filling(topic,text,json_question)
    json_question = finding_missing_details(json_question, user_data, chat_history)
    missing_item = if_everything_full(json_question)
    if len(missing_item) > 0:
        return "The following items are missing: " + ", ".join(missing_item)
    the_question = build_question(json_question)

    if topic != "complaint" and topic != "other":
        list_required = json_question["required"]
        name_company = ""
        if ("brand" in list_required) == True:
            name_company = json_question["++"]
        else:
            name_company = ""
        lst_par_to_answer = SearchInDB.handling_company_database(the_question[0],json_question[list_required[1]],topic,name_company, user_data)
        if len(lst_par_to_answer) < settings["NUM_TO_ANSWER"]:
            contents = SearchInDB.handling_Internet_database(the_question)
            dic_BinarySearchTree[user_data["userId"]] = BinarySearchTree()
            SearchInDB.select_most_suitable_simplifyers(contents, the_question, topic, user_data)
            text_to_answer = dic_BinarySearchTree[user_data["userId"]].bst_to_list(len(lst_par_to_answer),settings["NUM_TO_ANSWER"])
            lst_par_to_answer = lst_par_to_answer + text_to_answer

        if(len(text_to_answer) == 0):
            return "Error, The URL not opening AND There is no suitable answer."


#        set_topic = set()
#        dic_par = {}
#        paragraphs_to_answer = []
#        paragraphs_to_answer.append(text_to_answer[0])
#        set_topic.update(FindTopic.extract_topics(text_to_answer[0]))
#        for index, par in enumerate(text_to_answer[1:], start=0):
#            par_topic = FindTopic.extract_topics(par)
#            overlap = set_topic & set(par_topic)
#            if len(overlap) == 0:
#                set_topic.update(par_topic)
#                paragraphs_to_answer.append(par)
#            else:
#                dic_par[index+1] = len(overlap)
#        print("len(paragraphs_to_answer)")
#        print(len(paragraphs_to_answer))

#        if len(paragraphs_to_answer)<NUM_PARAGRAPHS_TO_ANSWER:
#            mone = NUM_PARAGRAPHS_TO_ANSWER-len(paragraphs_to_answer)
#            while mone>0 and dic_par:
#                sorted_items = sorted(dic_par.items(), key=lambda x: x[1])
#                print(sorted_items)
#                paragraphs_to_answer.append(text_to_answer[sorted_items[0][0]])
#                del dic_par[sorted_items[0][0]]
#                mone-=1
#        print()
#        print()
#        print()
#        print("-----------paragraphs to answer-------------")
#        print("\n\n\n".join(paragraphs_to_answer))

        answer_final = AnswerBuilding.create_answer(the_question[0],"\n".join(text_to_answer), topic)
        return answer_final

    else:
        if topic == "other":
            return "I am not allowed to answer this question because it does not deal with customer service."
        else:
            return complaint_handling(text, user_data, chat_history)



# Handle a complaint-topic message (not yet implemented)
def complaint_handling(text, user_data, chat_history):
    return










#text_to_search = message_handling("When is there a flight from Israel to Greece in April with El Al  at time 17:00 for one person?")
#text_to_search = message_handling("I am very disappointed with the service I received because my order AB124586 was delayed, the support team did not answer clearly, and the issue is still unresolved. ")
#text_to_search = message_handling("Does the Samsung Galaxy S24 support wireless charging?")
#text_to_search = message_handling("What is the screen size of the ASUS vivobook 14/15/17 computer?")
#text_to_search = message_handling("What is the screen size of the ASUS computer?")
#text_to_search = message_handling("What is the screen size of the ASUS computer?")
#text_to_search = message_handling("How much would it cost to install a new battery in my laptop, including the part price and the technician’s service fee?")
#text_to_search = message_handling("Could you tell me how much it would cost to repair a broken laptop screen, including the service fee and any extra charges?")
#text_to_search = message_handling("Hi, I’m trying to check something and I’m not sure exactly how to ask it — I need to know the price for one person, maybe sometime in April, to fly from Israel to Greece, preferably with El Al, and I want to understand how much it would cost overall.")
#text_to_search = message_handling("I would like to know how much it costs to fly from Israel to Greece with El Al in April for one person, including the basic ticket price and any possible additional fees.")
#text_to_search = message_handling("How much does it cost to fly from Israel to Greece with El Al in April for one person?")
#text_to_search = message_handling("How much does a JBL GO 4 speaker cost?")
#text_to_search = message_handling("I have a really good camera and I want to know how to take good pictures.")
#text_to_search = message_handling("How to get from Jerusalem to Tel Aviv by public transportation")
#print(text_to_search)

#TavilyAPI.search_in_DB(text_to_search)
