from sqlalchemy import Column, Integer, String
from db.config import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    movie_id = Column(Integer)
    tag = Column(String)
    timestamp = Column(Integer)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "tag": self.tag,
            "timestamp": self.timestamp,
        }
