from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.config import get_db
from models.rating import Rating
from schemas.rating import CreateRating, UpdateRating, DeleteRating
from models.movie import Movie

router_rating = APIRouter(tags=["ratings"])


@router_rating.get("/list")
async def get_ratings(db: Session = Depends(get_db)):
    ratings = db.query(Rating).limit(1000).all()
    return [rating.to_dict() for rating in ratings]


@router_rating.post("/", status_code=201)
def create_rating(
    rating_data: CreateRating,
    db: Session = Depends(get_db),
):
    movie_exist = db.query(Movie).filter(Movie.movie_id == rating_data.movie_id).first()
    if not movie_exist:
        raise HTTPException(status_code=404, detail="Movie with this ID does not exist")
    existing_rating = (
        db.query(Rating)
        .filter(
            rating_data.movie_id == Rating.movie_id,
            rating_data.user_id == Rating.user_id,
        )
        .first()
    )
    if existing_rating:
        raise HTTPException(
            status_code=400, detail="Rating for this movie by this user already exists"
        )
    new_rating = Rating(
        user_id=rating_data.user_id,
        movie_id=rating_data.movie_id,
        rating=rating_data.rating_value,
        timestamp=rating_data.timestamp,
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating.to_dict()


@router_rating.get("/{rating_id}", status_code=200)
def read_rating(rating_id: int, db: Session = Depends(get_db)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if rating:
        return rating.to_dict()
    raise HTTPException(status_code=404, detail="Rating not found")


@router_rating.put("/", status_code=200)
def update_rating(
    update_rating_data: UpdateRating,
    db: Session = Depends(get_db),
):
    rating_to_update = (
        db.query(Rating)
        .filter(
            Rating.movie_id == update_rating_data.movie_id,
            Rating.user_id == update_rating_data.user_id,
        )
        .first()
    )
    if not rating_to_update:
        raise HTTPException(status_code=404, detail="Rating not found")
    rating_to_update.rating = update_rating_data.rating_value
    rating_to_update.timestamp = update_rating_data.timestamp
    db.commit()
    db.refresh(rating_to_update)
    return rating_to_update.to_dict()


@router_rating.delete("/", status_code=200)
def delete_rating(delete_rating_data: DeleteRating, db: Session = Depends(get_db)):
    rating = db.query(Rating).filter(Rating.id == delete_rating_data.movie_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    db.delete(rating)
    db.commit()
    return {"message": f"Rating with id {rating.id} deleted successfully"}
