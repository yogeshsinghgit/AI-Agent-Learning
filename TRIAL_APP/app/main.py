from fastapi import FastAPI, Request

from app.core.lifespan import lifespan
from app.core.config import settings

from app.domains.api.routers import health, chat
from app.core.constants import API_V1_PREFIX

app = FastAPI(
    title = settings.APP_NAME,
    version = settings.APP_VERSION,
    lifespan= lifespan
)


app.include_router(health.router)
app.include_router(chat.router, prefix=API_V1_PREFIX)



