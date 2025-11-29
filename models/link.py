class Link:
    def __init__(self, movie_id, imbdld, tmdbld ):
        self.movie_id = int(movie_id)
        self.imbdld = imbdld
        self.tmdbld = tmdbld
        
        def __repr__(self):
            return f"Link(movie_id={self.movie_id}, imbdld={self.imbdld}, tmdbld={self.tmdbld})"