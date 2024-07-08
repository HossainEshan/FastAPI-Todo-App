from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from api.database.models import Users
from passlib.context import CryptContext
from jose import JWTError, jwt
from starlette import status
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive data from environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

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

def create_access_token(username: str, id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': id, 'role': role}
    expire_time = datetime.now() + expires_delta
    encode.update({'exp': expire_time})
    
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=token, token_type='bearer')

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        id = payload.get('id')
        role = payload.get('role')
        if not username or not id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not verify user')
            
        return {'username': username, 'id': id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not verify user')

user_dependency = Annotated[dict, Depends(get_current_user)]
        
