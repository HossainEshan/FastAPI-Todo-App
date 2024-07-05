from fastapi import FastAPI
from api.database.dbconfig import engine
from api.database.models import Base
from api.routers import todos, auth

# Initialize the app
app = FastAPI()

app.include_router(todos.router)
app.include_router(auth.router)

# Create the database dynamically
Base.metadata.create_all(bind=engine)