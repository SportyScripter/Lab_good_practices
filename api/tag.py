from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.config import get_db
from models.tag import Tag

router_tag = APIRouter(tags=["tags"])


@router_tag.get("/tags_list")
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return [tag.to_dict() for tag in tags]
