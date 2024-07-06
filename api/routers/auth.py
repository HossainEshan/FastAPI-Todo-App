from fastapi import APIRouter
from pydantic import BaseModel
from api.database.models import Users

router = APIRouter()

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str

@router.get('/auth')
async def get_user():
    return {'user': 'authenticated'}

@router.post('/auth')
async def create_user(user: CreateUserRequest):
    new_user_model = Users(
        username = user.username,
        email = user.email,
        password = user.password,
        role = user.role,
        is_active = True
    )
    
    return new_user_model