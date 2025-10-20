#el archivo donde defino las REST de libros

#los imports
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import BookCreate, BookUpdate, BookOut
from app.models import Book, Author, BookCategory

router = APIRouter(prefix="/books", tags=["books"])

@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    if not db.get(Author, payload.author_id):
        raise HTTPException(404, "Author not found")
    if db.query(Book).filter(Book.isbn == payload.isbn).first():
        raise HTTPException(409, "ISBN already exists")
    obj = Book(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=list[BookOut])
def list_books(
    q: str | None = Query(default=None, min_length=1),
    category: BookCategory | None = None,
    author_id: int | None = None,
    db: Session = Depends(get_db),
):
    qs = db.query(Book)
    if q: qs = qs.filter(Book.title.ilike(f"%{q}%"))
    if category: qs = qs.filter(Book.category == category)
    if author_id: qs = qs.filter(Book.author_id == author_id)
    return qs.all()

@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int = Path(ge=1), db: Session = Depends(get_db)):
    obj = db.get(Book, book_id)
    if not obj: raise HTTPException(404, "Book not found")
    return obj

@router.put("/{book_id}", response_model=BookOut)
def put_book(book_id: int, payload: BookCreate, db: Session = Depends(get_db)):
    obj = db.get(Book, book_id)
    if not obj: raise HTTPException(404, "Book not found")
    if not db.get(Author, payload.author_id):
        raise HTTPException(404, "Author not found")
    if db.query(Book).filter(Book.isbn == payload.isbn, Book.id != book_id).first():
        raise HTTPException(409, "ISBN already exists")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.patch("/{book_id}", response_model=BookOut)
def patch_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    obj = db.get(Book, book_id)
    if not obj: raise HTTPException(404, "Book not found")
    data = payload.model_dump(exclude_unset=True)
    if "author_id" in data and data["author_id"] and not db.get(Author, data["author_id"]):
        raise HTTPException(404, "Author not found")
    if "isbn" in data and data["isbn"]:
        if db.query(Book).filter(Book.isbn == data["isbn"], Book.id != book_id).first():
            raise HTTPException(409, "ISBN already exists")
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    obj = db.get(Book, book_id)
    if not obj: raise HTTPException(404, "Book not found")
    db.delete(obj); db.commit()