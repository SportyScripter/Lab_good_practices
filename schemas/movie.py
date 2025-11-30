from pydantic import BaseModel


class MovieCreate(BaseModel):
    title: str
    genres: str


class MovieUpdate(BaseModel):
    movie_id: int
    title: str
    genres: str


class MovieDelete(BaseModel):
    movie_id: int
