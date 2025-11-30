from pydantic import BaseModel


class CreateTag(BaseModel):
    user_id: int
    movie_id: int
    tag: str
    timestamp: int


class UpdateTag(BaseModel):
    id: int
    tag: str
    timestamp: int


class DeleteTag(BaseModel):
    id: int
