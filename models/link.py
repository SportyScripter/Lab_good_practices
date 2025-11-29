from sqlalchemy import Column, Integer, String
from db.config import Base


class Link(Base):
    __tablename__ = "links"

    movie_id = Column(Integer, primary_key=True, index=True)
    imbdld = Column(String)
    tmdbld = Column(String)

    def to_dict(self):
        return {"movie_id": self.movie_id, "imbdld": self.imbdld, "tmdbld": self.tmdbld}
