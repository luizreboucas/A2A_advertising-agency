from a2a.helpers.proto_helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from src.client_graph import graph
from src.client_graph import AgenciaState
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
            text=response["messages"][-1].content,
            task_id=context.task_id,
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
    

