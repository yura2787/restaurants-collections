from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import  RedirectResponse, JSONResponse

from backend_api.api import (get_current_user_with_token, login_user, get_restaurants, get_restaurant,
                             get_user_info, get_cuisines, get_favorites, add_favorite, remove_favorite,
                             register_user, send_comment, get_comments, update_comment, delete_comment)

router = APIRouter()

templates = Jinja2Templates(directory='templates')


@router.get('/')
@router.post('/')
async def index(request: Request, query: str = Form(''),
                cuisine: str = '', sort: str = 'id', direction: str = 'desc', page: int = 1,
                user: dict = Depends(get_current_user_with_token)):
    restaurants_response = await get_restaurants(
        q=query, cuisine=cuisine, sort_by=sort, order_direction=direction, page=page, limit=9
    )
    restaurants = restaurants_response['items']

    favorite_ids = []
    if user.get('access_token'):
        favorite_ids = await get_favorites(user['access_token'])

    for restaurant in restaurants:
        restaurant['is_favorite'] = restaurant['id'] in favorite_ids

    cuisines = await get_cuisines()

    context = {
        'request': request,
        'restaurants': restaurants,
        'cuisines': cuisines,
        'active_cuisine': cuisine,
        'active_sort': sort,
        'active_direction': direction,
        'query': query,
        'current_page': restaurants_response.get('page', 1),
        'total_pages': restaurants_response.get('pages', 1),
        'total': restaurants_response.get('total', 0),
    }
    if user.get('name'):
        context['user'] = user

    return templates.TemplateResponse('index.html', context=context)


@router.post('/toggle_favorite/{restaurant_id}')
async def toggle_favorite(restaurant_id: int, user: dict = Depends(get_current_user_with_token)):
    token = user.get('access_token')
    if not token:
        return JSONResponse({"error": "not_authenticated"}, status_code=401)
    current = await get_favorites(token)
    if restaurant_id in current:
        await remove_favorite(token, restaurant_id)
        return JSONResponse({"status": "removed", "is_favorite": False})
    await add_favorite(token, restaurant_id)
    return JSONResponse({"status": "added", "is_favorite": True})


@router.get('/favorites', name='favorites')
async def favorites_page(request: Request, user: dict = Depends(get_current_user_with_token)):
    if not user.get('access_token'):
        return RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)

    favorite_ids = await get_favorites(user['access_token'])
    all_restaurants = (await get_restaurants(limit=50)).get('items', [])
    restaurants = [r for r in all_restaurants if r['id'] in favorite_ids]
    for restaurant in restaurants:
        restaurant['is_favorite'] = True

    context = {'request': request, 'restaurants': restaurants, 'user': user}
    return templates.TemplateResponse('favorites.html', context=context)


@router.get('/profile', name='profile')
async def profile_page(request: Request, user: dict = Depends(get_current_user_with_token)):
    if not user.get('access_token'):
        return RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)

    favorite_ids = await get_favorites(user['access_token'])
    context = {
        'request': request,
        'user': user,
        'favorites_count': len(favorite_ids),
        'comments_count': len(user.get('comments', [])),
    }
    return templates.TemplateResponse('profile.html', context=context)


@router.get('/map', name='map')
async def map_page(request: Request, user: dict = Depends(get_current_user_with_token)):
    restaurants = (await get_restaurants(limit=50)).get('items', [])
    located = [r for r in restaurants if r.get('latitude') and r.get('longitude')]
    context = {'request': request, 'restaurants': located}
    if user.get('name'):
        context['user'] = user
    return templates.TemplateResponse('map.html', context=context)


@router.post("/add_comment/{restaurant_id}", name="add_comment")
async def add_comment(
    restaurant_id: int,
    request: Request,
    comment_text: str = Form(...),
    user: dict = Depends(get_current_user_with_token)
):
    if not user.get("access_token"):
        return RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)

    await send_comment(user["access_token"], restaurant_id, comment_text)
    return RedirectResponse(
        request.url_for("restaurant_detail", restaurant_id=restaurant_id),
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.patch("/comment/{restaurant_id}/{comment_id}", name="update_comment")
async def patch_comment(
    restaurant_id: int,
    comment_id: int,
    request: Request,
    user: dict = Depends(get_current_user_with_token)
):
    if not user.get("access_token"):
        return JSONResponse({"error": "not_authenticated"}, status_code=401)
    body = await request.json()
    result = await update_comment(user["access_token"], restaurant_id, comment_id, body.get("text", ""))
    if result.get("id"):
        return JSONResponse({"ok": True, "text": result["text"]})
    return JSONResponse({"error": "failed"}, status_code=400)


@router.delete("/comment/{restaurant_id}/{comment_id}", name="delete_comment")
async def remove_comment(
    restaurant_id: int,
    comment_id: int,
    user: dict = Depends(get_current_user_with_token)
):
    if not user.get("access_token"):
        return JSONResponse({"error": "not_authenticated"}, status_code=401)
    ok = await delete_comment(user["access_token"], restaurant_id, comment_id)
    return JSONResponse({"ok": ok})



@router.get('/restaurant/{restaurant_id}')
async def restaurant_detail(request: Request, restaurant_id: int, user: dict = Depends(get_current_user_with_token)):
    restaurant = await get_restaurant(restaurant_id)
    comments = await get_comments(restaurant_id)

    is_favorite = False
    if user.get('access_token'):
        favorite_ids = await get_favorites(user['access_token'])
        is_favorite = restaurant_id in favorite_ids

    context = {
        'request': request,
        "restaurant": restaurant,
        "comments": comments,
        "is_favorite": is_favorite,
    }
    if user.get('name'):
        context['user'] = user
    response = templates.TemplateResponse('restaurant_detail.html', context=context)
    return response


@router.get('/login')
@router.post('/login')
async def login(request: Request, user: dict=Depends(get_current_user_with_token), user_email: str = Form(''), password: str = Form('')):
    context = {'request': request}
    redirect_url = request.url_for("index")
    if user.get('name'):
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    if request.method == "GET":
        response = templates.TemplateResponse('login.html', context=context)
        response.delete_cookie('access_token')
        return response



    user_tokens = await login_user(user_email, password)
    access_token = user_tokens.get('access_token')
    if not access_token:
        errors = ['Incorrect login or password']
        context['errors'] = errors
        return templates.TemplateResponse('login.html', context=context)



    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="lax", max_age=60*5)
    return response


@router.get('/logout')
async def logout(request: Request):
    redirect_url = request.url_for("login")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie('access_token')
    return response


@router.get('/register')
@router.post('/register')
async def register(
        request: Request,
        user: dict = Depends(get_current_user_with_token),
        user_email: str = Form(''),
        password: str = Form(''),
        user_name: str = Form(''),
):

    context = {'request': request, "entered_email": user_email, 'entered_name': user_name}
    redirect_url = request.url_for("index")
    if user.get('name'):

        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    if request.method == "GET":
        response = templates.TemplateResponse('register.html', context=context)
        response.delete_cookie('access_token')
        return response

    created_user = await register_user(user_email=user_email, password=password, name=user_name)
    if created_user.get('email'):
        user_tokens = await login_user(user_email, password)
        access_token = user_tokens.get('access_token')
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="lax", max_age=60 * 5)
        return response

    context['errors'] = [created_user['detail']]
    response = templates.TemplateResponse('register.html', context=context)
    return response

