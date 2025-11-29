from fastapi import APIRouter
from db.load_data import data_store

movies_router = APIRouter(tags=["movies"])

@movies_router.get("/movies_lists")
def get_movies():
    return [item.__dict__ for item in data_store["movies"]]
