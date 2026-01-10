from fastapi import FastAPI
from fastapiprob.database import create_db_and_tables
from fastapiprob.routes import documents
from fastapiprob import models

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(documents.router)    
