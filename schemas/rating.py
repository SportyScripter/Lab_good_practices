from pydantic import BaseModel


class CreateRating(BaseModel):
    user_id: int
    movie_id: int
    rating_value: float
    timestamp: int


class UpdateRating(BaseModel):
    user_id: int
    movie_id: int
    rating_value: float
    timestamp: int


class DeleteRating(BaseModel):
    movie_id: int
