from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapiprob.database import create_db_and_tables
from fastapiprob.routes import auth, documents
from fastapiprob.settings import settings
from fastapiprob import models

app = FastAPI()

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(documents.router)
app.include_router(auth.router)
