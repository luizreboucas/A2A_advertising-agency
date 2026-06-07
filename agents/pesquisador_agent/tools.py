from tavily import TavilyClient
from dotenv import load_dotenv
from langchain.tools import tool
import os

load_dotenv()
TAVILY_KEY=os.getenv("TAVILY_KEY")

client = TavilyClient(api_key=TAVILY_KEY)


@tool
def search_web(theme: str):
    """ 
        Use essa tool para buscar infromações na internet sobre determinado assunto.
        @args
            theme: tema a ser pesquisado
    """
    result = client.search(query=theme)
    return result

