from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from api.database.models import Users
from passlib.context import CryptContext
from api.database.dbconfig import db_dependency
from jose import JWTError, jwt
from starlette import status

router = APIRouter(prefix='/auth', tags=['auth'])


SECRET_KEY = 'o4v4kj35345h3c4h5vjhv99hgc9gfx43jhbk23jb24v2ruifgbvh'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated ='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class Token(BaseModel):
    access_token: str
    token_type: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str
    
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.password_hash):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expire_time = datetime.now() + expires_delta
    encode.update({'exp': expire_time})
    
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=token, token_type='bearer')

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        if not username or user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not verify user')
        return {'username': username, 'user_id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not verify user')


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