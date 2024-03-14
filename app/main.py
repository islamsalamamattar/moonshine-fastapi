import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.core.config import settings
from app.core.database import sessionmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs")

# Mount the static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/")
async def root():
    # Read the HTML file and return it as a response
    return FileResponse("app/static/templates/landing.html")

@app.get("/chat")
async def root():
    return FileResponse("app/static/templates/chat.html")

@app.get("/image")
async def root():
    return FileResponse("app/static/assets/img/assistant2.png")



# Routers
app.include_router(auth_router)
app.include_router(chat_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
