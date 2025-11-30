from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.config import get_db
from models.link import Link
from schemas.link import LinkCreate, LinkUpdate
from models.movie import Movie

router_link = APIRouter(tags=["links"])


@router_link.get("/all")
async def get_links(db: Session = Depends(get_db)):
    links = db.query(Link).all()
    return [link.to_dict() for link in links]


@router_link.post("/", status_code=201)
def create_link(new_link_data: LinkCreate, db: Session = Depends(get_db)):
    movie_exist = (
        db.query(Movie).filter(Movie.movie_id == new_link_data.movie_id).first()
    )
    if not movie_exist:
        raise HTTPException(status_code=404, detail="Movie with this ID does not exist")
    if db.query(Link).filter(Link.movie_id == new_link_data.movie_id).first():
        raise HTTPException(
            status_code=400, detail="Link for this movie already exists"
        )
    new_link_data = Link(
        movie_id=new_link_data.movie_id,
        imbdld=new_link_data.imbdld,
        tmdbld=new_link_data.tmdbld,
    )
    db.add(new_link_data)
    db.commit()
    db.refresh(new_link_data)
    return new_link_data.to_dict()


@router_link.get("/{movie_id}", status_code=200)
def read_link(movie_id: int, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.movie_id == movie_id).first()
    if link:
        return link.to_dict()
    raise HTTPException(
        status_code=404, detail="Link with this movie ID does not exist"
    )


@router_link.put("/", status_code=200)
def update_link(link_data: LinkUpdate, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.movie_id == link_data.movie_id).first()
    if not link:
        raise HTTPException(
            status_code=404, detail="Link with this movie ID does not exist"
        )
    link.imbdld = link_data.imbdld
    link.tmdbld = link_data.tmdbld
    db.commit()
    db.refresh(link)
    return link.to_dict()


@router_link.delete("/{movie_id}", status_code=200)
def delete_link(movie_id: int, db: Session = Depends(get_db)):
    link_exist = db.query(Link).filter(Link.movie_id == movie_id).first()
    if not link_exist:
        raise HTTPException(
            status_code=404, detail="Link with this movie ID does not exist"
        )
    db.delete(link_exist)
    db.commit()
    return {"message": f"Link '{link_exist.movie_id}' deleted successfully"}
