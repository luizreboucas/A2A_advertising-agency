from a2a.helpers.proto_helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from gerente_agent import agent_card
from agencia import graph
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes import create_jsonrpc_routes, add_a2a_routes_to_fastapi, create_agent_card_routes
from fastapi import FastAPI
from agencia import AgenciaState
from uuid import uuid4
from langchain_core.messages import HumanMessage

class Executor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input()
        context_id = context.context_id or str(uuid4())
        initial_state: AgenciaState = {
            "context_id": context_id,
            "messages": [HumanMessage(content=user_text)],
            "next_step": None
        }
        response = await graph.ainvoke(initial_state)
        data = response["next_step"]
        message = new_text_message(
            context_id=context_id,
            text=data,
            task_id=context.task_id
        )
        await event_queue.enqueue_event(
            event=message
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id or str(uuid4()),
            context_id=context.context_id or str(uuid4()),
        )
        await updater.cancel()
    
request_handler = DefaultRequestHandler(
    agent_card=agent_card,
    agent_executor=Executor(),
    task_store=InMemoryTaskStore()
)

app = FastAPI()

add_a2a_routes_to_fastapi(
    app=app,
    agent_card_routes=create_agent_card_routes(agent_card=agent_card),
    jsonrpc_routes=create_jsonrpc_routes(request_handler=request_handler, rpc_url="/")
)
