from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, select, func, or_, and_
import math

from applications.Restaurants.schemas import SearchParamsSchema, SortEnum, SortByEnum

from applications.Restaurants.models_restaurants import Restaurants


async def create_restaurant_in_db(restaurant_uuid, name, description, menu, detailed_description, comments, main_image, images, session,
                                  cuisine=None, address=None, phone=None, working_hours=None,
                                  price_range=None, latitude=None, longitude=None) -> Restaurants:
    new_restaurant = Restaurants(
        uuid_data=restaurant_uuid,
        name=name.strip(),
        description=description.strip(),
        menu=menu,
        comments=comments,
        detailed_description=detailed_description,
        main_image=main_image,
        images=images,
        cuisine=cuisine,
        address=address,
        phone=phone,
        working_hours=working_hours,
        price_range=price_range,
        latitude=latitude,
        longitude=longitude,
    )
    session.add(new_restaurant)
    await session.commit()
    return new_restaurant


async def get_cuisines(session: AsyncSession) -> list[str]:
    query = select(Restaurants.cuisine).where(Restaurants.cuisine.isnot(None)).distinct()
    result = await session.execute(query)
    return sorted([c for c in result.scalars().all() if c])


async def get_restaurants_data(params: SearchParamsSchema, session: AsyncSession):
    query = select(Restaurants)
    count_query = select(func.count()).select_from(Restaurants)

    order_direction = asc if params.order_direction == SortEnum.ASC else desc

    if params.cuisine:
        query = query.filter(Restaurants.cuisine == params.cuisine)
        count_query = count_query.filter(Restaurants.cuisine == params.cuisine)

    if params.q:
        search_fields = [Restaurants.name, Restaurants.description]
        if params.use_sharp_q_filter:
            cleaned_query = params.q.strip().lower()
            search_condition = [func.lower(search_field) == cleaned_query for search_field in search_fields]
            query = query.filter(or_(*search_condition))
            count_query = count_query.filter(or_(*search_condition))
        else:
            words = [word for word in params.q.strip().split() if len(word) > 1]
            search_condition = or_(
                and_(*(search_field.icontains(word) for word in words)) for search_field in search_fields
            )
            query = query.filter(search_condition)
            count_query = count_query.filter(search_condition)

    sort_column = getattr(Restaurants, params.sort_by.value, Restaurants.id)
    query = query.order_by(order_direction(sort_column))
    query = query.limit(params.limit).offset((params.page - 1) * params.limit)

    result = await session.execute(query)
    result_count = await session.execute(count_query)
    total = result_count.scalar()

    return {
        "items": result.scalars().all(),
        "total": total,
        'page': params.page,
        'limit': params.limit,
        'pages': math.ceil(total / params.limit)
    }

async def get_restaurant_by_pk(pk: int, session: AsyncSession) -> Restaurants | None:
    query = select(Restaurants).filter(Restaurants.id == pk)
    result = await session.execute(query)
    return result.scalar_one_or_none()