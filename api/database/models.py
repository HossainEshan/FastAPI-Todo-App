from api.database.dbconfig import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

# Class that represents SQL table
class Todos(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)