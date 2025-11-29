from sqlalchemy import Column, Integer, Float
from db.config import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    movie_id = Column(Integer, index=True)
    rating = Column(Float)
    timestamp = Column(Integer)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "rating": self.rating,
            "timestamp": self.timestamp,
        }
