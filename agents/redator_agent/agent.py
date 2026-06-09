import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from langchain.agents import create_agent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentInterface
from langchain_core.messages import BaseMessage



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

redator_agent = create_agent(
    llm,
    name="redator",
    system_prompt="""
        Você é um redator extremamente hábil, escreve português perfeitamente, incluindo acentuação.
        Você recebe uma pesquisa feita por outro agente, entende o texto que foi recebido e cria um texto
        para uma agência de publicidade. O texto vai para o instagram.
        Use as melhores práticas de copy
        se você não tiver recebido nenhuma pesquisa retorne apenas: não tenho nenhuma pesquisa feita para escrever minha redação
        Você vai receber várias pesquisas, mas o texto é apenas um. Ele pode ser de no máximo 2 parágrafos

        se você não tiver pesquisa nas mensagens, não escreva a redação
    """,
)

skill = AgentSkill(
    description="Pode escrever postagens para publicidade",
    tags=["publicidade"],
    name="skill simples de escrita"
)

agent_card = AgentCard(
    capabilities=AgentCapabilities(push_notifications=False, streaming=False),
    description="esse agente escreve redações para publicidade",
    name="Redator Agent",
    version="1.0.0",
    skills=[skill],
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            protocol_version="1.0",
            url="http://redator_agent:8000"
        )
    ]
)

async def run_redator_agent(messages: list[BaseMessage]):
    response = await redator_agent.ainvoke({"messages": messages})
    return response


