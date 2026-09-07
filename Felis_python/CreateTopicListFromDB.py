import os




# Return the paths of all .txt files in the given folder
def fill_phats_files(path_folder):
    try:
        return [
            os.path.join(path_folder, f)
            for f in os.listdir(path_folder)
            if f.endswith(".txt")
        ]
    except FileNotFoundError:
        print("Folder not found")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


# Extract the "Topics Discussed" section text from a conversation summary file's content
def find_topic(content):
    parts = content.split("Topics Discussed:")
    if len(parts) > 1:
        topics_text = parts[1].strip() 
    else:
        topics_text = ""
        print("No topics found")
    return topics_text

# Split a topics string by commas and store the resulting list under the file's name in the dict
def insert_to_dict(dict_topic,topics,file_name):
    parts = [p.strip() for p in topics.replace("\n", "").split(",")]
    dict_topic[f"{file_name}"] = parts
    return dict_topic


# Given a list of indices, return the corresponding file paths from the folder's text files
def phat_to_similar_topics(arr_index, folder_path):
    try:
        text_files = fill_phats_files(folder_path)
        paths_st = []
        for index in arr_index:
            paths_st.append(text_files[index])
        return paths_st

    except Exception as e:
        print(f"Error in phat_to_similar_topics: {e}")
        return []


# Build a dict mapping each conversation-summary file name to its list of discussed topics
def create_topic_list(folder_path):
    dict_topic ={}
    text_files = fill_phats_files(folder_path)

    for path_txt in text_files:
        try:
            with open(path_txt, "r", encoding="utf-8") as f:
                content = f.read()
            topics = find_topic(content)
            dict_topic = insert_to_dict(dict_topic,topics,os.path.basename(path_txt))
        except FileNotFoundError:
            print(f"Error: The file {os.path.basename(path_txt)} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    return dict_topic





#def find_topic(content):
    #words = content.split()
    #i=0
    #d = False
    #topics = ""
    #while i<len(words):
    #    if i+1<len(words) and words[i]+" "+words[i+1] == "Topics Discussed:" and d == False:
    #        d=True
    #        i+=1
    #    else:
    #        if d==True:
    #            topics = topics+" "+words[i]
    #    i+=1
    #return topics