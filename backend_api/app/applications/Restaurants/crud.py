from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, select, func, or_, and_
import math

from applications.Restaurants.schemas import SearchParamsSchema, SortEnum, SortByEnum

from applications.Restaurants.models_restaurants import Restaurants


async def create_restaurant_in_db(restaurant_uuid, name, description, menu, detailed_description, comments, main_image, images, session) -> Restaurants:
    new_restaurant = Restaurants(
        uuid_data=restaurant_uuid,
        name=name.strip(),
        description=description.strip(),
        menu=menu,
        comments=comments,
        detailed_description=detailed_description,
        main_image=main_image,
        images=images,
    )
    session.add(new_restaurant)
    await session.commit()
    return new_restaurant


async def get_restaurants_data(params: SearchParamsSchema, session: AsyncSession):
    query = select(Restaurants)
    count_query = select(func.count()).select_from(Restaurants)

    order_direction = asc if params.order_direction == SortEnum.ASC else desc
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