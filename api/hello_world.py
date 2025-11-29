from fastapi import FastAPI, APIRouter


router_movie = APIRouter(tags=["movies"])

router_movie.get("/list")
async def get_movies():
    return {"message": "List of movies"}


