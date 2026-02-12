from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from src.users.auth.schemas import SUserRegister, UserOut
from src.users.dao import UserDAO 
from src.db.session import get_session


router = APIRouter()


@router.post("/register/")
async def register_user(user_data: SUserRegister, session: AsyncSession = Depends(get_session)) -> UserOut:
    user_dao = UserDAO(session)
    
    user = await user_dao.get_user_by_email(email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )

    new_user = await user_dao.create_user(user=user_data)
    
    return new_user


@router.get("/get_user/{id}")
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_session)) -> UserOut:
    user_dao = UserDAO(session)
    
    user = await user_dao.get_user_by_id(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден'
        )
    
    return user


@router.get("/get_users_list/")
async def get_user_by_id(session: AsyncSession = Depends(get_session)) -> List[UserOut]:
    user_dao = UserDAO(session)
    
    users_list = await user_dao.get_users_list()
    if not users_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователи не найдены'
        )
    
    return users_list