class Movie:
    def __init__(self, movie_id, title, genres ):
        self.movie_id = int(movie_id)
        self.movie_title = title
        self.movie_genres = genres
    
    def __repr__(self):
        return f"Movie(movie_id={self.movie_id}, title={self.movie_title}, genres={self.movie_genres})"