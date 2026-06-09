from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from typing import Literal, Any, TypedDict
import os
import logging
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentInterface

load_dotenv(override=True)
BASE_URL= os.getenv("BASE_URL")
MODEL=os.getenv("MODEL")
API_KEY=os.getenv("API_KEY")
AGENT_PUBLIC_URL = os.getenv("GERENTE_AGENT_URL", "http://localhost:8000")
logger = logging.getLogger(__name__)

if not BASE_URL or not MODEL or not API_KEY:
    raise ValueError("Variáveis de ambiente não foram carregadas")

logger.info("Gerente usando LLM base_url=%s model=%s", BASE_URL, MODEL)

llm = ChatOpenAI(
    base_url=BASE_URL,
    model=MODEL,
    api_key = API_KEY
)
class AgentInput(TypedDict):
    messages: list[AnyMessage | dict[str, Any]]

class LlmResponse(BaseModel):
    next_agent: Literal["redator", "pesquisador", "fim"]
skill = AgentSkill(
    id="decidir-proximo-agente",
    description="este agente pode definir para onde vai a próxima tarefa",
    name="skill simples de decisão"
)

agent_card = AgentCard(
    capabilities=AgentCapabilities(push_notifications=False, streaming=True),
    name="Gerente Agent",
    description="Esse agente pode decidir entre passar uma tarefa para um redator, pesquisador ou finalizar a execução",
    skills=[skill],
    version="1.0.0",
    supported_interfaces=[
        AgentInterface(
            url=AGENT_PUBLIC_URL,
            protocol_binding="JSONRPC",
            protocol_version="1.0"
        )
    ]
)

gerente_agent = create_agent(
    llm,
    system_prompt="""
        Você é um gerente de uma agência de publicidade, sua tarefa é saber se a tarefa precisa ir para 
        um pesquisador, um redator, ou finalizar.
        você deve responder sempre com uma palavra apenas, deve ser uma das três: redator, pesquisador, fim.
        Se você tiver a redação e a pesquisa pode chamar 
        {
            "next_agent": "fim"
        }
        OLHE TODO O HIStÓRICO DE CONVERSAS para ter certeza que o redator tem a pesquisa, e o pesquisador entregou a pesquisa
        se o pesquisador não tiver entregue a pesquisa, não chame o redator, chame o pesquisador.
        Se você já tiver a pesquisa no histório de mensagens, chame o redator.
        se tiver a pesquisa e a redação chame o fim
        exemplos de saídas:
        {
            "next_agent": "redator"
        }

        {
            "next_agent": "pesquisador"
        }
        
        {
            "next_agent": "fim"
        }

    """,
    response_format=LlmResponse
)

async def run_agent(messages: list[AnyMessage], context_id: str):
    agent_input: AgentInput = {
        "messages": list(messages)
    }
    response = await gerente_agent.ainvoke(agent_input)
    return response["structured_response"]
