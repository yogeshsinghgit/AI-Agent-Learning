from fastapi import Request, Depends

from app.domains.ai.runtime_dependencies.checkpointer import CheckpointerClient
from app.domains.dependencies.app_state import AppState
from app.db.redis_client import RedisClient



def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state

def get_redis(request: Request) -> RedisClient:
    return request.app.state.app_state.redis

def get_checkpointer(request: Request) -> CheckpointerClient:
    return request.app.state.app_state.checkpointer

def get_graph(request: Request):
    return request.app.state.app_state.graph
