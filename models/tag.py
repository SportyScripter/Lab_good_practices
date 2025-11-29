class Tag:
    def __init__(self, user_id: int, movie_id: int, tag: str, timestamp: int):
        self.user_id = user_id
        self.movie_id = movie_id
        self.tag = tag
        self.timestamp = timestamp
    def __repr__(self):
        return f"tags(user_id={self.user_id}, movie_id={self.movie_id}, tag={self.tag}, timestamp={self.timestamp})"