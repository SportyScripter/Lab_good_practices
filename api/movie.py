from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.config import get_db
from models.movie import Movie
from schemas.movie import MovieCreate, MovieUpdate, MovieDelete

movies_router = APIRouter(tags=["movies"])


@movies_router.get("/all")
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).all()
    return [movie.to_dict() for movie in movies]


@movies_router.post("/", status_code=201)
def create_movie(movie_data: MovieCreate, db: Session = Depends(get_db)):
    if db.query(Movie).filter(Movie.title == movie_data.title).first():
        raise HTTPException(
            status_code=400, detail="Movie with this title already exists"
        )
    new_movie = Movie(title=movie_data.title, genres=movie_data.genres)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie.to_dict()


@movies_router.get("/{movie_id}")
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie.to_dict()


@movies_router.put("/", status_code=200)
def update_movie(update_movie_data: MovieUpdate, db: Session = Depends(get_db)):
    movie_exist = (
        db.query(Movie).filter(Movie.movie_id == update_movie_data.movie_id).first()
    )
    if movie_exist is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie_exist.title = update_movie_data.title
    movie_exist.genres = update_movie_data.genres
    db.commit()
    db.refresh(movie_exist)
    return movie_exist.to_dict()


@movies_router.delete("/", status_code=200)
def delete_movie(delete_movie_data: MovieDelete, db: Session = Depends(get_db)):
    movie_exist = (
        db.query(Movie).filter(Movie.movie_id == delete_movie_data.movie_id).first()
    )
    if not movie_exist:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie_exist)
    db.commit()
    return {"message": f"Movie: '{movie_exist.title}' Deleted successfully"}
