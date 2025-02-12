"""
This file is the main router for the FastAPI application. It includes the database and visualization routers.
"""
from fastapi import FastAPI, APIRouter
from databaseEndpoints import db_router
from visualizationEndpoints import viz_router
from chatbotEndpoints import chatbot_router
import uvicorn

app = FastAPI()

app.include_router(db_router, prefix="")
app.include_router(viz_router, prefix="")
app.include_router(chatbot_router, prefix="")

if __name__ == "__main__":
    uvicorn.run("mainRouter:app", host="127.0.0.1", port=8000,reload=True)
    