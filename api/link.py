from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.config import get_db
from models.link import Link

router_link = APIRouter(tags=["links"])


@router_link.get("/links_list")
async def get_links(db: Session = Depends(get_db)):
    links = db.query(Link).all()
    return [link.to_dict() for link in links]
