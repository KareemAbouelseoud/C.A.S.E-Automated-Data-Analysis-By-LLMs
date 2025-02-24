"""
This file is the main router for the FastAPI application. It includes the database and visualization routers.
"""
from fastapi import FastAPI
from vizGenerationEndpoints import viz_router
from chatbotEndpoints import chatbot_router
import uvicorn

app = FastAPI()
# TODO: Add Backend LOGGING
# app.include_router(db_router, prefix="")
app.include_router(viz_router, prefix="")
app.include_router(chatbot_router, prefix="")