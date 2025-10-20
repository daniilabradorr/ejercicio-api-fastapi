#en este arichvo realizo las REST de la relacion libros-libreria

#los imports
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from app.database import get_db

from app.schemas import LibraryBookCreate, LibraryBookUpdate, LibraryBookOut
from app.models import LibraryBook, Book, Loan, LoanStatus, LibraryBookStatus



router = APIRouter(prefix="/library-books", tags=["library_books"])

@router.post("", response_model=LibraryBookOut, status_code=status.HTTP_201_CREATED)
def create_library_book(payload: LibraryBookCreate, db: Session = Depends(get_db)):
    if not db.get(Book, payload.book_id):
        raise HTTPException(404, "Book not found")
    if db.query(LibraryBook).filter(LibraryBook.inventory_code == payload.inventory_code).first():
        raise HTTPException(409, "Inventory code already exists")
    obj = LibraryBook(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj






@router.get("", response_model=list[LibraryBookOut])
def list_library_books(
    status_: LibraryBookStatus | None = None,
    book_id: int | None = None,
    db: Session = Depends(get_db),
):
    qs = db.query(LibraryBook)
    if status_: qs = qs.filter(LibraryBook.status == status_)
    if book_id: qs = qs.filter(LibraryBook.book_id == book_id)
    return qs.all()

@router.get("/{lb_id}", response_model=LibraryBookOut)
def get_library_book(lb_id: int = Path(ge=1), db: Session = Depends(get_db)):
    obj = db.get(LibraryBook, lb_id)
    if not obj: raise HTTPException(404, "LibraryBook not found")
    return obj





@router.put("/{lb_id}", response_model=LibraryBookOut)
def put_library_book(lb_id: int, payload: LibraryBookCreate, db: Session = Depends(get_db)):
    obj = db.get(LibraryBook, lb_id)
    if not obj: raise HTTPException(404, "LibraryBook not found")
    if not db.get(Book, payload.book_id):
        raise HTTPException(404, "Book not found")
    if db.query(LibraryBook).filter(LibraryBook.inventory_code == payload.inventory_code, LibraryBook.id != lb_id).first():
        raise HTTPException(409, "Inventory code already exists")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.patch("/{lb_id}", response_model=LibraryBookOut)
def patch_library_book(lb_id: int, payload: LibraryBookUpdate, db: Session = Depends(get_db)):
    obj = db.get(LibraryBook, lb_id)
    if not obj: raise HTTPException(404, "LibraryBook not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj




@router.delete("/{lb_id}", status_code=204)
def delete_library_book(lb_id: int, db: Session = Depends(get_db)):
    obj = db.get(LibraryBook, lb_id)
    if not obj: raise HTTPException(404, "LibraryBook not found")
    #impido borrar si hay un préstamo activo o tarde
    blocking = db.query(Loan).filter(
        Loan.library_book_id == lb_id,
        Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.LATE])
    ).first()
    if blocking:
        raise HTTPException(409, "Cannot delete: active or late loan exists")
    db.delete(obj); db.commit()


