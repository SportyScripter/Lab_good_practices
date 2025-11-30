from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.config import get_db
from models.tag import Tag
from schemas.tag import CreateTag, UpdateTag, DeleteTag
from models.movie import Movie

router_tag = APIRouter(tags=["tags"])


@router_tag.get("/tags_list")
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return [tag.to_dict() for tag in tags]


@router_tag.post("/", status_code=201)
def create_tag(
    tag_data: CreateTag,
    db: Session = Depends(get_db),
):
    movie_exist = db.query(Movie).filter(Movie.movie_id == tag_data.movie_id).first()
    if not movie_exist:
        raise HTTPException(status_code=400, detail="Movie with this ID does not exist")
    tag_exists = (
        db.query(Tag)
        .filter(Tag.movie_id == tag_data.movie_id, Tag.tag == tag_data.tag)
        .first()
    )
    if tag_exists:
        raise HTTPException(status_code=400, detail="Tag for this movie already exists")
    new_tag = Tag(
        user_id=tag_data.user_id,
        movie_id=tag_data.movie_id,
        tag=tag_data.tag,
        timestamp=tag_data.timestamp,
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag.to_dict()


@router_tag.get("/{tag_id}", status_code=200)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    print(tag)
    if tag:
        return tag.to_dict()
    raise HTTPException(status_code=404, detail="Tag not found")


@router_tag.put("/", status_code=200)
def update_tag(update_tag_data: UpdateTag, db: Session = Depends(get_db)):
    tag_to_update = db.query(Tag).filter(Tag.id == update_tag_data.id).first()
    if not tag_to_update:
        raise HTTPException(status_code=404, detail="Tag not found")
    duplicate_check = (
        db.query(Tag)
        .filter(
            Tag.movie_id == tag_to_update.movie_id,
            Tag.tag == update_tag_data.tag,
            Tag.id != update_tag_data.id,
        )
        .first()
    )
    if duplicate_check:
        raise HTTPException(
            status_code=400, detail="Tag with this name already exists for this movie"
        )
    tag_to_update.tag = update_tag_data.tag
    tag_to_update.timestamp = update_tag_data.timestamp
    db.commit()
    db.refresh(tag_to_update)

    return tag_to_update.to_dict()


@router_tag.delete("/", status_code=200)
def delete_tag(delete_tag_data: DeleteTag, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == delete_tag_data.id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted successfully"}
