from a2a.server.agent_execution import AgentExecutor,RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.helpers.proto_helpers import new_text_message
from langchain_core.messages import HumanMessage, AIMessage
from uuid import uuid4
from agents.pesquisador_agent.agent import run_pesquisador_agent


class Executor(AgentExecutor):
    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        user_input = context.get_user_input()
        context_id = context.context_id or uuid4()
        
        response = await run_pesquisador_agent(messages=[HumanMessage(content=user_input)])
        data = response["full_research"]
        message = new_text_message(
            context_id=context_id,
            text=AIMessage(content=data),
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