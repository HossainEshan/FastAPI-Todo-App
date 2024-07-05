from api.database.dbconfig import engine, SessionLocal
from api.database.models import Base, Todos
from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel

# Initialize the app
app = FastAPI()

# Create the database dynamically
Base.metadata.create_all(bind=engine)

# Routes -----------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get('/todos')
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@app.get('/todos/{todo_id}')
async def read_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    result = db.query(Todos).filter(Todos.id == todo_id).first()
    if result is not None:
        return result
    raise HTTPException(status_code=404, detail='Todo not found')