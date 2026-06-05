from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from typing import Literal
import os
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentInterface

load_dotenv()
BASE_URL= os.getenv("BASE_URL")
MODEL=os.getenv("MODEL")
API_KEY=os.getenv("API_KEY")

if not BASE_URL or not MODEL or not API_KEY:
    raise ValueError("Variáveis de ambiente não foram carregadas")

llm = ChatOpenAI(
    base_url=BASE_URL,
    model=MODEL,
    api_key = API_KEY
)

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
            url="http://localhost:8001",
            protocol_binding="JSONRPC",
            protocol_version="1.0"
        )
    ]
)

gerente_agent_instance = create_agent(
    llm,
    system_prompt="""
        Você é um gerente de uma agência de publicidade, sua tarefa é saber se a tarefa precisa ir para 
        um pesquisador, um redator, ou finalizar.
        você deve responder sempre com uma palavra apenas, deve ser uma das três: redator, pesquisador, fim.

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

async def run_agent(messages: list[BaseMessage], context_id: str):
    response = await gerente_agent_instance.ainvoke({"messages": messages})
    return response["structured_response"]
