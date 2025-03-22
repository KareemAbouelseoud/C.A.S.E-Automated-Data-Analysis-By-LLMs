"""
This file is the main router for the FastAPI application. It includes the chatbot and visualization routers.
"""
from fastapi import FastAPI
from .vizGenerationEndpoints import viz_router
from .chatbotEndpoints import chatbot_router
from .automlEndpoints import autoML_router, cache_cleanup
import asyncio
from contextlib import asynccontextmanager

app = FastAPI()
# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    cleanup_task = asyncio.create_task(cache_cleanup())
    yield
    # Shutdown event
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        print("Cleanup task was cancelled during shutdown.")

app.router.lifespan_context = lifespan

# TODO: Add Backend LOGGING
# app.include_router(db_router, prefix="")
app.include_router(viz_router, prefix="")
app.include_router(chatbot_router, prefix="")
app.include_router(autoML_router, prefix="")





