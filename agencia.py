from typing import TypedDict, Annotated, Literal
from langgraph.graph import add_messages, StateGraph, END, START
from langchain_core.messages import BaseMessage, AIMessage
from gerente_agent import run_agent

class AgenciaState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_step: Literal["pesquisador", "redator", "fim", None]
    context_id: str

def call_redator(state: AgenciaState):
    return {
        "messages": [AIMessage(content="redator")]
    }

def call_pesquisador(state: AgenciaState):
    return {
        "messages": [AIMessage(content="pesquisador")]
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
workflow.add_edge("pesquisador", END)
workflow.add_edge("redator", END)
graph = workflow.compile()
