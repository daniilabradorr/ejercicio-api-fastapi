"""En este arichivo lo que hago es definir las rutas REST
Los loans usasn el orquestador el reso usan el ORM diractamente
con las validaciones que le he puesto"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AuthorCreate, AuthorUpdate, AuthorOut
from app.models import Author

router = APIRouter(prefix="/authors", tags=["authors"])

@router.post("", response_model=AuthorOut, status_code=status.HTTP_201_CREATED)
def create_author(payload: AuthorCreate, db: Session = Depends(get_db)):
    #garantizo unicidad por nombre
    if db.query(Author).filter(Author.name == payload.name).first():
        raise HTTPException(409, "Author name already exists")
    obj = Author(name=payload.name)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=list[AuthorOut])
def list_authors(q: str | None = Query(default=None, min_length=1), db: Session = Depends(get_db)):
    #permito filtrar por nombre
    qs = db.query(Author)
    if q: qs = qs.filter(Author.name.ilike(f"%{q}%"))
    return qs.all()

@router.get("/{author_id}", response_model=AuthorOut)
def get_author(author_id: int = Path(ge=1), db: Session = Depends(get_db)):
    obj = db.get(Author, author_id)
    if not obj: raise HTTPException(404, "Author not found")
    return obj

@router.put("/{author_id}", response_model=AuthorOut)
def put_author(author_id: int, payload: AuthorCreate, db: Session = Depends(get_db)):
    obj = db.get(Author, author_id)
    if not obj: raise HTTPException(404, "Author not found")
    #vuelvo a comprobar unicidad si cambia el nombre
    if db.query(Author).filter(Author.name == payload.name, Author.id != author_id).first():
        raise HTTPException(409, "Author name already exists")
    obj.name = payload.name
    db.commit(); db.refresh(obj)
    return obj

@router.patch("/{author_id}", response_model=AuthorOut)
def patch_author(author_id: int, payload: AuthorUpdate, db: Session = Depends(get_db)):
    obj = db.get(Author, author_id)
    if not obj: raise HTTPException(404, "Author not found")
    if payload.name:
        if db.query(Author).filter(Author.name == payload.name, Author.id != author_id).first():
            raise HTTPException(409, "Author name already exists")
        obj.name = payload.name
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{author_id}", status_code=204)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    obj = db.get(Author, author_id)
    if not obj: raise HTTPException(404, "Author not found")
    db.delete(obj); db.commit()