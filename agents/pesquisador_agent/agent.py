from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentInterface
from typing import Literal
from agents.pesquisador_agent.tools import search_web
import logging

load_dotenv()
BASE_URL= os.getenv("BASE_URL")
MODEL=os.getenv("MODEL")
API_KEY=os.getenv("API_KEY")

logger = logging.getLogger(__name__)


if not BASE_URL or not MODEL or not API_KEY:
    raise ValueError("Variáveis de ambiente não foram carregadas")

llm = ChatOpenAI(
    base_url=BASE_URL,
    model=MODEL,
    api_key = API_KEY
)

#class LlmResponse(BaseModel):
#    full_research: str

pesquisa = AgentSkill(
    description="Pesquisa na internet",
    tags=["pesquisa"]
)

agent_card = AgentCard(
    capabilities=AgentCapabilities(push_notifications=False, streaming=False),
    description="esse agente é um pesquisador e trás resultados de pesquisa na internet",
    name="Pesquisador Agent",
    version="1.0.0",
    skills=[pesquisa],
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            protocol_version="1.0",
            url="http://localhost:8001"
        )
    ],

)

pesquisador_agent = create_agent(
    llm,
    name="pesquisador",
    system_prompt="""
        Você é um pesquisador com habilidades de pesquisa na internet, o seu papel é trazer toda informação possível sobre o 
        tópico que o usuário trouxer. pode ser um tópico ou uma sentença. Traga toda informação possível
    """,
    tools=[search_web]
)

async def run_pesquisador_agent(messages: list[BaseMessage]):
    logger.info("Mensagens chegando no pesquisador:\n {messages}")
    response = await pesquisador_agent.ainvoke({"messages": messages})
    logger.info("Resposta do pesquisador:\n {response}")
    return response