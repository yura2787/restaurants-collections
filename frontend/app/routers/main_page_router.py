from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import  RedirectResponse

from backend_api.api import get_current_user_with_token, login_user, get_restaurants, get_restaurant, get_user_info


from backend_api.api import register_user, send_comment

router = APIRouter()

templates = Jinja2Templates(directory='templates')




@router.get('/')
@router.post('/')
async def index(request: Request, query: str = Form(''), user: dict = Depends(get_current_user_with_token)):
    restaurants_response = await get_restaurants(query)
    restaurants = restaurants_response['items']

    for restaurant in restaurants:
        restaurant['comments'] = [
            {
                "text": comment["text"],
                "author": comment.get("author_name", "Anon")
            }
            for comment in user.get('comments', [])
                if int(comment["restaurant_id"]) == int(restaurant["id"])
        ]

    context = {'request': request, 'restaurants': restaurants}
    if user.get('name'):
        context['user'] = user

    return templates.TemplateResponse('index.html', context=context)


@router.post("/add_comment/{restaurant_id}", name="add_comment")
async def add_comment(
    restaurant_id: int,
    request: Request,
    comment_text: str = Form(...),
    user: dict = Depends(get_current_user_with_token)
):
    if not user.get("access_token"):
        return RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)


    await send_comment(user["access_token"], restaurant_id, comment_text, user["name"])


    updated_user = await get_user_info(user["access_token"])

    restaurants_response = await get_restaurants("")
    restaurants = restaurants_response["items"]

    for restaurant in restaurants:
        restaurant['comments'] = [
            {
                "text": comment["text"],
                "author": comment.get("author_name", "Anon")
            }
            for comment in updated_user.get("comments", [])
            if int(comment["restaurant_id"]) == int(restaurant["id"])
        ]

    context = {
        'request': request,
        'restaurants': restaurants,
        'user': updated_user
    }

    return templates.TemplateResponse("index.html", context=context)





@router.get('/restaurant/{restaurant_id}')
async def restaurant_detail(request: Request, restaurant_id: int, user: dict = Depends(get_current_user_with_token)):
    restaurant = await get_restaurant(restaurant_id)
    comments = []
    if user.get("comments"):
        comments = [
            comment["text"]
            for comment in user["comments"]
            if comment.get("restaurant_id") == restaurant_id
        ]
    context = {
        'request': request,
        "restaurant": restaurant,
        "comments": comments,
    }
    if user.get('name'):
        context['user'] = user
    response = templates.TemplateResponse('restaurant_detail.html', context=context)
    return response


@router.get('/login')
@router.post('/login')
async def login(request: Request, user: dict=Depends(get_current_user_with_token), user_email: str = Form(''), password: str = Form('')):
    context = {'request': request}
    print(user, 55555555555555555555555)
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
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60*5)
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
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60 * 5)
        return response

    context['errors'] = [created_user['detail']]
    response = templates.TemplateResponse('register.html', context=context)
    return response

