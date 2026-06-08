from tavily import TavilyClient
from dotenv import load_dotenv
from langchain.tools import tool
import os
import requests
from ddgs.ddgs import DDGS
from bs4 import BeautifulSoup

# load_dotenv()
# TAVILY_KEY=os.getenv("TAVILY_KEY")

# client = TavilyClient(api_key=TAVILY_KEY)

@tool
def search_web(theme: str):
    """ 
        Use essa tool para buscar infromações na internet sobre determinado assunto.
        @args
            theme: tema a ser pesquisado
    """
    client = DDGS()
    results = client.text(theme)
    responses = []
    for result in results[:5]:
        url = result["href"]
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            text = BeautifulSoup(html, "html.parser").get_text()
            clean_text = " ".join(text.split())
            responses.append(clean_text[:400])
        else:
            continue
    final = "\n".join(response for response in responses)
    return final

