"""
This file is the main router for the FastAPI application. It includes the database and visualization routers.
"""
from fastapi import FastAPI, APIRouter
# from endpoints.databaseEndpoints import db_router
from endpoints.visualizationEndpoints import viz_router
from endpoints.chatbotEndpoints import chatbot_router
from endpoints.userEndpoints import user_router
from endpoints.ProjectEndpoints import Project_router


import uvicorn

app = FastAPI()
# TODO: Add Backend LOGGING
# app.include_router(db_router, prefix="")
app.include_router(viz_router, prefix="")
app.include_router(chatbot_router, prefix="")
app.include_router(user_router, prefix="")
app.include_router(Project_router, prefix="")


if __name__ == "__main__":
    uvicorn.run("mainRouter:app", host="127.0.0.1", port=8000,reload=True,reload_dirs=["Backend"])
    