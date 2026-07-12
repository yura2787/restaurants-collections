import logging

import httpx
from settings import settings
from fastapi import Request

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(10.0)


async def login_user(user_email: str, password: str):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                url=f'{settings.BACKEND_API}/auth/login',
                data={"username": user_email, 'password': password}
            )
            return response.json()
    except Exception as e:
        logger.error(f"login_user error: {e}")
        return {}


async def register_user(user_email: str, password: str, name: str):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                url=f'{settings.BACKEND_API}/users/create',
                json={"name": name, 'password': password, "email": user_email},
                headers={'Content-Type': 'application/json'}
            )
            return response.json()
    except Exception as e:
        logger.error(f"register_user error: {e}")
        return {}


async def get_user_info(access_token: str):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                url=f'{settings.BACKEND_API}/auth/get_my_info',
                headers={"Authorization": f'Bearer {access_token}'}
            )
            if response.status_code != 200:
                return {}
            return response.json()
    except Exception as e:
        logger.error(f"get_user_info error: {e}")
        return {}


async def get_current_user_with_token(request: Request) -> dict:
    access_token = request.cookies.get('access_token')
    if not access_token:
        return {}
    user = await get_user_info(access_token)
    if user:
        user['access_token'] = access_token
    return user


async def get_restaurants(q: str = "", cuisine: str = "", sort_by: str = "id",
                          order_direction: str = "desc", page: int = 1, limit: int = 9):
    try:
        params = {"q": q, "page": page, "limit": limit,
                  "sort_by": sort_by, "order_direction": order_direction}
        if cuisine:
            params["cuisine"] = cuisine
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                url=f'{settings.BACKEND_API}/restaurants/',
                params=params
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"get_restaurants error: {e}")
        return {"items": [], "total": 0, "page": 1, "limit": limit, "pages": 0}


async def get_cuisines():
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url=f'{settings.BACKEND_API}/restaurants/cuisines')
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"get_cuisines error: {e}")
        return []


async def get_favorites(access_token: str) -> list[int]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                url=f'{settings.BACKEND_API}/users/favorites',
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code != 200:
                return []
            return response.json().get("favorite_ids", [])
    except Exception as e:
        logger.error(f"get_favorites error: {e}")
        return []


async def add_favorite(access_token: str, restaurant_id: int):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                url=f'{settings.BACKEND_API}/users/favorites/{restaurant_id}',
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
    except Exception as e:
        logger.error(f"add_favorite error: {e}")
        return {}


async def remove_favorite(access_token: str, restaurant_id: int):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.request(
                "DELETE",
                url=f'{settings.BACKEND_API}/users/favorites/{restaurant_id}',
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
    except Exception as e:
        logger.error(f"remove_favorite error: {e}")
        return {}


async def get_restaurant(pk: int):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                url=f'{settings.BACKEND_API}/restaurants/{pk}',
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"get_restaurant error: {e}")
        return {}


async def send_comment(access_token: str, restaurant_id: int, text: str, author_name: str = ""):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                url=f'{settings.BACKEND_API}/restaurants/{restaurant_id}/comments',
                json={"text": text},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
    except Exception as e:
        logger.error(f"send_comment error: {e}")
        return {}


async def get_comments(restaurant_id: int) -> list:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url=f'{settings.BACKEND_API}/restaurants/{restaurant_id}/comments')
            return response.json() if response.status_code == 200 else []
    except Exception as e:
        logger.error(f"get_comments error: {e}")
        return []


async def update_comment(access_token: str, restaurant_id: int, comment_id: int, text: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.patch(
                url=f'{settings.BACKEND_API}/restaurants/{restaurant_id}/comments/{comment_id}',
                json={"text": text},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
    except Exception as e:
        logger.error(f"update_comment error: {e}")
        return {}


async def delete_comment(access_token: str, restaurant_id: int, comment_id: int) -> bool:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.delete(
                url=f'{settings.BACKEND_API}/restaurants/{restaurant_id}/comments/{comment_id}',
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.status_code == 204
    except Exception as e:
        logger.error(f"delete_comment error: {e}")
        return False