from sqlalchemy import Column, Integer, String
from db.config import Base


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    genres = Column(String)

    def to_dict(self):
        return {"movie_id": self.movie_id, "title": self.title, "genres": self.genres}
