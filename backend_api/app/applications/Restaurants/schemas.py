from pydantic import BaseModel, Field
from enum import StrEnum

from pydantic import BaseModel, Field
from typing import Annotated, Optional

class RestaurantSchema(BaseModel):
    id: int
    name: str
    description: str
    menu: str
    comments: Optional[str] = None
    detailed_description: Optional[str] = None
    main_image: str
    images: list[str]

class SortEnum(StrEnum):
    ASC = 'asc'
    DESC = 'desc'


class SortByEnum(StrEnum):
    ID = 'id'
    PRICE = 'price'


class SearchParamsSchema(BaseModel):
    q: Annotated[Optional[str], Field(default=None)] = None
    page: Annotated[int, Field(default=1, ge=1)]
    limit: Annotated[int, Field(default=10, ge=1, le=50)]
    order_direction: SortEnum = SortEnum.DESC
    sort_by: SortByEnum = SortByEnum.ID
    use_sharp_q_filter: bool = Field(default=False, description='used to search exact q')
