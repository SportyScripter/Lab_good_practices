from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.config import get_db
from models.rating import Rating

router_rating = APIRouter(tags=["ratings"])


@router_rating.get("/ratings_list")
async def get_ratings(db: Session = Depends(get_db)):
    ratings = db.query(Rating).limit(1000).all()
    return [rating.to_dict() for rating in ratings]
