from fastapi import APIRouter, Depends, status, Body, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.s3.s3 import s3_storage
from database.session_dependencies import get_async_session
import uuid
from applications.Restaurants.crud import create_restaurant_in_db, get_restaurants_data, get_restaurant_by_pk, get_cuisines
from applications.Restaurants.schemas import RestaurantSchema, SearchParamsSchema
from applications.auth.security import admin_required
from typing import Annotated

router_restaurants = APIRouter()


@router_restaurants.post("/create", status_code=status.HTTP_201_CREATED,
                         dependencies=[Depends(admin_required)])
async def create_restaurant(
        main_image: UploadFile,
        images: list[UploadFile] = None,
        name: str = Body(..., max_length=50),
        description: str = Body(...),
        menu: str = Body(...),
        comments: str = Body(..., max_length=2500),
        detailed_description: str = Body(...),
        session: AsyncSession = Depends(get_async_session)
) -> RestaurantSchema:
    restaurant_uuid = uuid.uuid4()
    main_image = await s3_storage.upload_product_image(main_image, restaurant_uuid=restaurant_uuid)
    images = images or []
    images_urls = []
    for image in images:
        url = await s3_storage.upload_product_image(image, restaurant_uuid=restaurant_uuid)
        images_urls.append(url)

    created_restaurant = await  create_restaurant_in_db(restaurant_uuid=restaurant_uuid, name=name,
                                                        description=description, menu=menu,
                                                        comments=comments, detailed_description=detailed_description,
                                                        main_image=main_image, images=images_urls,
                                                        session=session)

    return created_restaurant


@router_restaurants.post("/create_by_url", status_code=status.HTTP_201_CREATED,
                         dependencies=[Depends(admin_required)])
async def create_restaurant_by_url(
        name: str = Body(...),
        description: str = Body(...),
        menu: str = Body(...),
        detailed_description: str = Body(default=""),
        comments: str = Body(default=""),
        main_image: str = Body(...),
        images: list[str] = Body(default=[]),
        cuisine: str = Body(default=None),
        address: str = Body(default=None),
        phone: str = Body(default=None),
        working_hours: str = Body(default=None),
        price_range: str = Body(default=None),
        latitude: float = Body(default=None),
        longitude: float = Body(default=None),
        session: AsyncSession = Depends(get_async_session)
) -> RestaurantSchema:
    restaurant_uuid = uuid.uuid4()
    created_restaurant = await create_restaurant_in_db(
        restaurant_uuid=restaurant_uuid, name=name, description=description,
        menu=menu, comments=comments, detailed_description=detailed_description,
        main_image=main_image, images=images, session=session,
        cuisine=cuisine, address=address, phone=phone, working_hours=working_hours,
        price_range=price_range, latitude=latitude, longitude=longitude
    )
    return created_restaurant


@router_restaurants.get('/cuisines')
async def list_cuisines(session: AsyncSession = Depends(get_async_session)) -> list[str]:
    return await get_cuisines(session)


@router_restaurants.get('/{pk}')
async def get_product(pk: int, session: AsyncSession = Depends(get_async_session), ) -> RestaurantSchema:
    product = await get_restaurant_by_pk(pk, session)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with pk #{pk} not found")
    return product


@router_restaurants.get('/')
async def get_restaurants(params: Annotated[SearchParamsSchema, Depends()],
                          session: AsyncSession = Depends(get_async_session)):
    result = await get_restaurants_data(params, session)
    return result
