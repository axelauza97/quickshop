import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from models.db.base import Base
from models.db.session import get_engine, make_session
from routers import cart, categories, health, orders, products, users
from services.fixture_seed import maybe_seed_catalog_fixtures


load_dotenv()


def _initialize_app_state() -> None:
    Base.metadata.create_all(bind=get_engine())
    session = make_session()
    try:
        seeded = maybe_seed_catalog_fixtures(session)
        if seeded:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _initialize_app_state()
    yield


ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(title="QuickShop API", lifespan=lifespan)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    detail = str(exc.orig) if exc.orig else "constraint violation"
    return JSONResponse(status_code=400, content={"detail": detail})


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(cart.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
