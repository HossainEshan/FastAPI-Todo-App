from api.database.dbconfig import db_dependency
from api.database.models import Todos
from fastapi import HTTPException, Path, APIRouter
from starlette import status
from api.routers.utils import user_dependency

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/alltodos', status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    
    return db.query(Todos).all()

@router.delete('/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
        
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
