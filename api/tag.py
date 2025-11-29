from fastapi import APIRouter
from db.load_data import data_store

router_tag = APIRouter(tags=["tags"])

@router_tag.get("/tags_list")
async def get_tags():
    return [item.__dict__ for item in data_store["tags"]]