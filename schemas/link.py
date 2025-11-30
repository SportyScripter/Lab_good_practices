from pydantic import BaseModel


class LinkCreate(BaseModel):
    movie_id: int
    imbdld: str
    tmdbld: str


class LinkUpdate(BaseModel):
    movie_id: int
    imbdld: str
    tmdbld: str
