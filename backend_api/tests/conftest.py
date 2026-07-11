import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database.base_models import Base
from database.session_dependencies import get_async_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
session_maker_test = async_sessionmaker(engine_test, expire_on_commit=False)


async def override_get_async_session():
    async with session_maker_test() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

    from app_factory import get_application
    app = get_application()
    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient):
    response = await client.post("/users/create", json={
        "email": "test@example.com",
        "name": "TestUser",
        "password": "password123"
    })
    return response.json()
