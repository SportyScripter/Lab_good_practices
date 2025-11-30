from fastapi import FastAPI
from api.movie import movies_router
from api.link import router_link
from api.rating import router_rating
from api.tag import router_tag
from db.load_data import init_db
from db.config import Base, engine, SessionLocal

app = FastAPI()

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    init_db(db)

app.include_router(movies_router, prefix="/movies")
app.include_router(router_link, prefix="/links")
app.include_router(router_rating, prefix="/ratings")
app.include_router(router_tag, prefix="/tags")
