from typing import TypedDict, Annotated, Literal
from langgraph.graph import add_messages, StateGraph, END, START
from langchain_core.messages import BaseMessage, AIMessage
from src.gerente_agent import run_agent
from a2a.client.card_resolver import A2ACardResolver
import httpx
from uuid import uuid4
from a2a.client import ClientConfig, ClientFactory
from a2a.types import SendMessageRequest, Message,StreamResponse, Role, Part

AGENTS = {
            "gerente": "http://localhost:8001",
            "pesquisador": "http://localhost:8002",
            "redator": "http://localhost:8003"
        }

def get_text_from_message(message: Message) -> str:
    texts = []

    for part in message.parts:
        if part.text:
            texts.append(part.text)

    return "\n".join(texts)


def get_text_from_stream_response(response: StreamResponse) -> str | None:
    if response.message:
        return get_text_from_message(response.message)

    if response.task:
        # Algumas respostas A2A vêm como artifacts da task.
        for artifact in response.task.artifacts:
            texts = []
            for part in artifact.parts:
                if part.text:
                    texts.append(part.text)

            if texts:
                return "\n".join(texts)

        # Às vezes o texto vem no status.message.
        if response.task.status.message:
            return get_text_from_message(response.task.status.message)

    return None

async def call_agent(messages: list[BaseMessage], agent_url: str, context_id: str):
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=agent_url
        )
        agent_card = resolver.get_agent_card()
        config = ClientConfig(
            httpx_client=httpx_client,
            agent_card=agent_card,
            context_id=context_id,
            messages=messages
        )
        client = ClientFactory(config).create(card=agent_card)
        request = SendMessageRequest(
            message=Message(
                message_id=str(uuid4()),
                context_id=context_id,
                role=Role.ROLE_USER,
                parts=[
                    Part(text=str(messages[-1].content)),
                ],
            )
        )
        final_text = ""
        async for response in client.send_message(request):
            text = get_text_from_stream_response(response)
            if text:
                final_text += text
        return final_text