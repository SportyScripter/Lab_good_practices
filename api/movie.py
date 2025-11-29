from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.config import get_db
from models.movie import Movie

movies_router = APIRouter(tags=["movies"])


@movies_router.get("/movies_lists")
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).all()
    return [movie.to_dict() for movie in movies]
