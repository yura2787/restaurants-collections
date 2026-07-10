import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base_models import Base


class Restaurants(Base):
    __tablename__ = "Restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    uuid_data: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    menu: Mapped[str] = mapped_column(Text, nullable=False)
    comments: Mapped[str] = mapped_column(String(2500), nullable=True)
    main_image: Mapped[str] = mapped_column(nullable=False)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    detailed_description: Mapped[str] = mapped_column(Text, nullable=True)

    def __str__(self):
        return f'Restaurant {self.name} - {self.id}'


