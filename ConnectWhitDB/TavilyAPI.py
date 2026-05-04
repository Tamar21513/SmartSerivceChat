from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

def search_in_DB(text):
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(text,  max_results=20)
    return response

    


#search_in_DB("know take pictures")