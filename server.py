from executor import Executor
from a2a.server.request_handlers import DefaultRequestHandler
from fastapi import FastAPI
from a2a.server.routes import create_jsonrpc_routes, add_a2a_routes_to_fastapi, create_agent_card_routes
from a2a.server.tasks import InMemoryTaskStore
from gerente_agent import agent_card

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