"""
This file is the main router for the FastAPI application. It includes the database and visualization routers.
"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# from endpoints.databaseEndpoints import db_router
from endpoints.visualizationEndpoints import viz_router
from endpoints.chatbotEndpoints import chatbot_router
from endpoints.userEndpoints import user_router
from endpoints.ProjectEndpoints import Project_router
from endpoints.insGenEndpoints import insGen_router

from endpoints.autoMLEndpoints import autoML_router

import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# TODO: Add Backend LOGGING
# app.include_router(db_router, prefix="")
app.include_router(viz_router, prefix="")
app.include_router(chatbot_router, prefix="")
app.include_router(user_router, prefix="")
app.include_router(Project_router, prefix="")
app.include_router(insGen_router, prefix="")
app.include_router(autoML_router, prefix="")
