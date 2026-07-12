import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from applications.auth.router import router_auth
from applications.Restaurants.router import router_restaurants
from applications.users.router import router_users
from database.base_models import Base
from database.session_dependencies import engine
from settings import settings

# import models so their tables are registered on Base.metadata
from applications.users.models import User  # noqa: F401
from applications.users.favorite_model import Favorite  # noqa: F401
from applications.Restaurants.models_restaurants import Restaurants  # noqa: F401

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured")
    yield


def get_application() -> FastAPI:
    app = FastAPI(root_path="/api", root_path_in_servers=True, debug=settings.DEBUG, lifespan=lifespan)

    app.include_router(router_users, prefix="/users", tags=["Users"])
    app.include_router(router_restaurants, prefix="/restaurants", tags=["Restaurants"])
    app.include_router(router_auth, prefix="/auth", tags=["Auth"])
    return app
