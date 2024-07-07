from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from api.database.dbconfig import db_dependency
from api.database.models import Users
from starlette import status
from api.routers.utils import CreateUserRequest, Token, bcrypt_context, authenticate_user, create_access_token

router = APIRouter(prefix='/auth', tags=['auth'])

@router.get('/')
async def get_user():
    return {'user': 'authenticated'}

@router.post('/')
async def create_user(db: db_dependency, user: CreateUserRequest):
    new_user_model = Users(
        username = user.username,
        email = user.email,
        password_hash = bcrypt_context.hash(user.password),
        role = user.role,
        is_active = True
    )
    
    db.add(new_user_model)
    db.commit()
    
@router.post('/token', response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return token