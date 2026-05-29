from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_DEV_ROOT = Path(__file__).parents[3].resolve()
_CMS_ROOT = (_DEV_ROOT / "klucon-cms").resolve()
_EDITORJS_SRC = (_DEV_ROOT / "plugin" / "plg_editorjs" / "src" / "plugins").resolve()
_THIS_SRC = (Path(__file__).parents[1] / "src" / "plugins").resolve()

if str(_CMS_ROOT) not in sys.path:
    sys.path.insert(0, str(_CMS_ROOT))

import src.plugins as _sp  # noqa: E402

for path in (_EDITORJS_SRC, _THIS_SRC):
    if str(path) not in _sp.__path__:
        _sp.__path__.insert(0, str(path))

os.environ.setdefault("IS_INSTALLED", "true")
os.environ.setdefault("SECRET_KEY", "test_secret_key_32_bytes_long_xxxx")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("ALLOWED_ORIGINS", "[]")

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # noqa: E402
from src.config import get_settings  # noqa: E402
from src.constants import ROLE_ADMIN, ROLE_SUPER_ADMIN, ROLE_VIEWER  # noqa: E402
from src.core.db import get_optional_db_session  # noqa: E402
from src.core.security import hash_password  # noqa: E402
from src.database.base import Base, get_db_session  # noqa: E402
from src.database.models import Role, SystemSettings, User  # noqa: E402
from src.i18n.translator import translator as _translator  # noqa: E402

get_settings.cache_clear()

_translator.load_domain("plg_editorjs", _EDITORJS_SRC / "plg_editorjs" / "i18n")
_translator.load_domain("plg_editorjs_button", _THIS_SRC / "plg_editorjs_button" / "i18n")

from jinja2 import FileSystemLoader  # noqa: E402
from src.core.templates import admin_templates  # noqa: E402

_EDITORJS_TPL = _EDITORJS_SRC / "plg_editorjs" / "templates"
if not any(
    isinstance(ldr, FileSystemLoader) and str(_EDITORJS_TPL) in ldr.searchpath
    for ldr in getattr(admin_templates.loader, "loaders", [])
):
    admin_templates.loader.loaders.append(FileSystemLoader(str(_EDITORJS_TPL)))

# Inicializace plg_editorjs (registruje builtins + globals)
from src.plugins.plg_editorjs import _CORE_ASSETS  # noqa: E402
from src.plugins.plg_editorjs.renderer import _config as _editorjs_config  # noqa: E402
from src.plugins.plg_editorjs.tools import _REGISTRY as _editorjs_registry  # noqa: E402

admin_templates.globals["editorjs_config"] = _editorjs_config
admin_templates.globals["editorjs_registry"] = _editorjs_registry
admin_templates.globals["editorjs_core_assets"] = _CORE_ASSETS

# Spustí setup() pluginu: registruje button tool + admin router
from src.main import app as _cms_app  # noqa: E402

from src.plugins.plg_editorjs_button import admin as _btn_admin  # noqa: E402
from src.plugins.plg_editorjs_button import setup as _btn_setup  # noqa: E402


class _FakeRegistry:
    def __init__(self) -> None:
        self.routers: list[object] = []

    def register_router(self, router: object, name: str | None = None) -> None:
        self.routers.append(router)


_btn_setup(_FakeRegistry())

if not any(
    getattr(r, "path", "").startswith("/admin/plg_editorjs_button")
    for r in _cms_app.routes
):
    _cms_app.include_router(_btn_admin.router)

_web = [r for r in _cms_app.router.routes if "web" in getattr(r, "tags", [])]
_non_web = [r for r in _cms_app.router.routes if "web" not in getattr(r, "tags", [])]
_cms_app.router.routes = _non_web + _web

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
_BCRYPT_ROUNDS = 4


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        _TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await _seed(session)
        yield session

    await engine.dispose()


async def _seed(session: AsyncSession) -> None:
    for name in [ROLE_SUPER_ADMIN, ROLE_ADMIN, ROLE_VIEWER]:
        session.add(Role(name=name, description=""))
    session.add(SystemSettings(
        id=1, site_title="Test CMS", locale="cs_CZ", route_overrides={},
        password_min_length=4, username_min_length=3, username_max_length=50,
        bcrypt_rounds=_BCRYPT_ROUNDS, access_token_expire_minutes=30,
        refresh_token_expire_days=7, rate_limit_free="100/hour",
        rate_limit_paid="10000/hour", login_max_attempts=3, login_lockout_minutes=1,
        marketplace_url="https://marketplace.klucon.cz", marketplace_public_key="",
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    ))
    await session.commit()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_db():
        yield db_session

    _cms_app.dependency_overrides[get_db_session] = _override_db
    _cms_app.dependency_overrides[get_optional_db_session] = _override_db

    async with AsyncClient(transport=ASGITransport(app=_cms_app), base_url="http://test") as c:
        yield c

    _cms_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def superadmin(db_session: AsyncSession) -> User:
    from sqlalchemy import select

    role = (
        await db_session.execute(select(Role).where(Role.name == ROLE_SUPER_ADMIN))
    ).scalar_one()
    user = User(
        username="superadmin", email="superadmin@test.com",
        hashed_password=hash_password("heslo1234", rounds=_BCRYPT_ROUNDS),
        is_active=True, role_id=role.id,
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, superadmin: User):
    resp = await client.post(
        "/admin/login",
        data={"username": "superadmin", "password": "heslo1234"},
        follow_redirects=False,
    )
    assert resp.status_code in (200, 303)
    return client
