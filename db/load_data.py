import requests
import zipfile
import io
import csv
from models.movie import Movie
from models.link import Link
from models.rating import Rating
from models.tag import Tag
from sqlalchemy.orm import Session


def init_db(db: Session):
    if db.query(Movie).first():
        print("Baza danych już zawiera filmy. Pomijanie pobierania.")
        return

    FILE_ID = "1ffJ15YV980hfVj-T1MdD0XIkPUEyqPsF"
    DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

    print("--- Pobieranie pliku ZIP ---")
    response = requests.get(DOWNLOAD_URL)
    if response.status_code != 200:
        raise Exception("Błąd pobierania pliku")

    print("--- Rozpakowywanie i zapisywanie do bazy SQLite ---")

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        all_files = z.namelist()

        """--- Movies ---"""
        movies_file = next((n for n in all_files if "movies.csv" in n), None)
        if movies_file:
            print("Wstawianie filmów...")
            with z.open(movies_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                movies_to_add = []
                for row in reader:
                    movies_to_add.append(
                        Movie(
                            movie_id=int(row["movieId"]),
                            title=row["title"],
                            genres=row["genres"],
                        )
                    )
                db.add_all(movies_to_add)
                db.commit()

        """--- Links ---"""
        links_file = next((n for n in all_files if "links.csv" in n), None)
        if links_file:
            print("Wstawianie linków...")
            with z.open(links_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                links_to_add = []
                for row in reader:
                    links_to_add.append(
                        Link(
                            movie_id=int(row["movieId"]),
                            imbdld=row["imdbId"],
                            tmdbld=row["tmdbId"],
                        )
                    )
                db.add_all(links_to_add)
                db.commit()

        """--- Tags ---"""
        tags_file = next((n for n in all_files if "tags.csv" in n), None)
        if tags_file:
            print("Wstawianie tagów...")
            with z.open(tags_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                tags_to_add = []
                for row in reader:
                    tags_to_add.append(
                        Tag(
                            user_id=int(row["userId"]),
                            movie_id=int(row["movieId"]),
                            tag=row["tag"],
                            timestamp=int(row["timestamp"]),
                        )
                    )
                db.add_all(tags_to_add)
                db.commit()

        """--- Ratings ---"""
        ratings_file = next((n for n in all_files if "ratings.csv" in n), None)
        if ratings_file:
            print("Wstawianie ocen (to najdłuższy etap)...")
            with z.open(ratings_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                ratings_to_add = []
                for row in reader:
                    ratings_to_add.append(
                        Rating(
                            user_id=int(row["userId"]),
                            movie_id=int(row["movieId"]),
                            rating=float(row["rating"]),
                            timestamp=int(row["timestamp"]),
                        )
                    )
                db.add_all(ratings_to_add)
                db.commit()

    print("--- Zakończono ładowanie danych do bazy ---")
