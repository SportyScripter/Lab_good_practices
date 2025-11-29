from fastapi import APIRouter
from db.load_data import data_store

router_rating = APIRouter(tags=["ratings"])

@router_rating.get("/ratings_list")
async def get_ratings():
    return [item.__dict__ for item in data_store["ratings"]]