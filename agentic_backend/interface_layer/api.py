from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from memory_layer.models import User
from memory_layer.db import get_db

router = APIRouter()


# ------------------------------
# Pydantic Models
# ------------------------------
class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    age: int
    hobbies: str
    language: str


class UserRead(BaseModel):
    id: int
    username: str
    password: str
    first_name: str
    last_name: str
    age: int
    hobbies: str
    language: str

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


# ------------------------------
# API Endpoints
# ------------------------------
@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/login", response_model=UserRead)
def login_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            User.username == credentials.username, User.password == credentials.password
        )
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user
