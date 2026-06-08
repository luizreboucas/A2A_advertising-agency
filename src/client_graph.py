from typing import TypedDict, Annotated, Literal
from langgraph.graph import add_messages, StateGraph, END, START
from langchain_core.messages import BaseMessage, AIMessage
from src.gerente_agent import run_agent
from a2a.client.card_resolver import A2ACardResolver
import httpx
from uuid import uuid4
from a2a.client import ClientConfig, ClientFactory
from a2a.types import SendMessageRequest, Message,StreamResponse, Role, Part
from src.utils import call_agent, AGENTS

class AgenciaState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_step: Literal["pesquisador", "redator", "fim", None]
    context_id: str

async def call_redator(state: AgenciaState):
    response = await call_agent(messages=state["messages"], agent_url=AGENTS["redator"], context_id=state["context_id"])
    return {
        "messages": [AIMessage(content=response)],
    }

async def call_pesquisador(state: AgenciaState):
    response = await call_agent(messages=state["messages"], agent_url=AGENTS["pesquisador"], context_id=state["context_id"])
    return {
        "messages": [AIMessage(content=f"[PESQUISA]\n{response}")]
    }

async def call_gerente(state: AgenciaState):
    response = await run_agent(context_id=state["context_id"], messages=state["messages"])
    next_agent = response.next_agent
    return {
        "next_step": next_agent
    }

def router(state: AgenciaState):
    return state["next_step"]

workflow = StateGraph(AgenciaState)
workflow.add_node("pesquisador", call_pesquisador)
workflow.add_node("redator", call_redator)
workflow.add_node("gerente", call_gerente)
workflow.add_conditional_edges(
    "gerente",
    router,
    {
        "pesquisador": "pesquisador",
        "redator": "redator",
        "fim": END
    }
)
workflow.add_edge(START, "gerente")
workflow.add_edge("pesquisador", "gerente")
workflow.add_edge("redator", "gerente")

graph = workflow.compile()
