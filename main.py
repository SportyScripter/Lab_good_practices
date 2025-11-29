from fastapi import FastAPI, APIRouter
from api.movie import movies_router
from api.link import router_link
from api.rating import router_rating
from api.tag import router_tag
from db.load_data import load_all_data

app = FastAPI()
router = APIRouter()

load_all_data()

app.include_router(movies_router)
app.include_router(router_link)
app.include_router(router_rating)
app.include_router(router_tag)


app.get("/hello_world")


def read_root():
    return {"Hello": "World"}
