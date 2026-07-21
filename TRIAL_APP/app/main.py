from fastapi import FastAPI 

from app.core.lifespan import lifespan
from app.core.config import settings

app = FastAPI(
    title = settings.APP_NAME,
    version = settings.APP_VERSION,
    lifespan= lifespan
)


