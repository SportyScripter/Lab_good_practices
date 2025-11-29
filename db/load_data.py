import requests
import zipfile
import io
import csv
from models.movie import Movie
from models.link import Link
from models.rating import Rating
from models.tag import Tag

data_store = {"movies": [], "links": [], "ratings": [], "tags": []}


def load_all_data():
    FILE_ID = "1ffJ15YV980hfVj-T1MdD0XIkPUEyqPsF"
    DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

    print("--- Rozpoczynanie pobierania pliku ZIP ---")
    response = requests.get(DOWNLOAD_URL)
    if response.status_code != 200:
        raise Exception("Błąd pobierania pliku")

    print("--- Plik pobrany. Rozpakowywanie i parsowanie ---")

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        all_files = z.namelist()

        """--- 1.  Przetwarzanie MOVIES ---"""
        movies_file = next((n for n in all_files if "movies.csv" in n), None)
        if movies_file:
            with z.open(movies_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                for row in reader:
                    data_store["movies"].append(
                        Movie(row["movieId"], row["title"], row["genres"])
                    )
            print(f"Załadowano {len(data_store['movies'])} filmów.")

        """--- 2. Przetwarzanie LINKS ---"""
        links_file = next((n for n in all_files if "links.csv" in n), None)
        if links_file:
            with z.open(links_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                for row in reader:
                    # Uwaga: tmdbId czasem jest puste w danych, warto to obsłużyć (tutaj zakładam że jest)
                    obj = Link(
                        movie_id=row["movieId"],
                        imbdld=row["imdbId"],  # Mapowanie: CSV imdbId -> Klasa imbdld
                        tmdbld=row["tmdbId"],  # Mapowanie: CSV tmdbId -> Klasa tmdbld
                    )
                    data_store["links"].append(obj)
            print(f"Załadowano {len(data_store['links'])} linków.")

        """--- 3. Przetwarzanie RATINGS ---"""
        ratings_file = next((n for n in all_files if "ratings.csv" in n), None)
        if ratings_file:
            with z.open(ratings_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                for row in reader:
                    obj = Rating(
                        user_id=row["userId"],
                        movie_id=row["movieId"],
                        rating=row["rating"],
                        timestamp=row["timestamp"],
                    )
                    data_store["ratings"].append(obj)
            print(f"Załadowano {len(data_store['ratings'])} ocen.")

        """--- 4. Przetwarzanie TAGS ---"""
        tags_file = next((n for n in all_files if "tags.csv" in n), None)
        if tags_file:
            with z.open(tags_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                for row in reader:
                    obj = Tag(
                        user_id=row["userId"],
                        movie_id=row["movieId"],
                        tag=row["tag"],
                        timestamp=row["timestamp"],
                    )
                    data_store["tags"].append(obj)
            print(f"Załadowano {len(data_store['tags'])} tagów.")
