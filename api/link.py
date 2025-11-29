from fastapi import APIRouter
from db.load_data import data_store

router_link = APIRouter(tags=["links"])

@router_link.get("/links_list")
async def get_links():
    return [item.__dict__ for item in data_store["links"]]