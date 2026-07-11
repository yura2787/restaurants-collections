import uuid

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from applications.auth.password_handler import PasswordEncrypt
from applications.users.models import User


async def create_user_in_db(email, name, password, session: AsyncSession) -> User:
    hashed_password = await PasswordEncrypt.get_password_hash(password)
    new_user = User(email=email,hashed_password=hashed_password,name=name)
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user_by_email(email, session: AsyncSession) -> User | None:
    query = select(User).filter(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def activate_user_account(user_uuid, session: AsyncSession) -> None:
    query = select(User).filter(User.uuid_data == user_uuid)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='Provided data does not belong to known user')

    user.is_verified = True
    session.add(user)
    await session.commit()


async def add_favorite(user_id: int, restaurant_id: int, session: AsyncSession) -> None:
    from applications.users.favorite_model import Favorite
    existing = await session.execute(
        select(Favorite).filter(Favorite.user_id == user_id, Favorite.restaurant_id == restaurant_id)
    )
    if existing.scalar_one_or_none():
        return
    session.add(Favorite(user_id=user_id, restaurant_id=restaurant_id))
    await session.commit()


async def remove_favorite(user_id: int, restaurant_id: int, session: AsyncSession) -> None:
    from applications.users.favorite_model import Favorite
    result = await session.execute(
        select(Favorite).filter(Favorite.user_id == user_id, Favorite.restaurant_id == restaurant_id)
    )
    fav = result.scalar_one_or_none()
    if fav:
        await session.delete(fav)
        await session.commit()


async def get_favorite_ids(user_id: int, session: AsyncSession) -> list[int]:
    from applications.users.favorite_model import Favorite
    result = await session.execute(
        select(Favorite.restaurant_id).filter(Favorite.user_id == user_id)
    )
    return list(result.scalars().all())