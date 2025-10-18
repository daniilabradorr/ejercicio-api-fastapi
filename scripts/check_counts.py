#los imports
from app.database import SessionLocal
from app.models import Author, Book, Member, LibraryBook, Loan, LibraryBookStatus, LoanStatus
#este script es para verifoicar el conteo de los datos.

def main():
    db = SessionLocal()
    try:
        print("Authors:", db.query(Author).count())
        print("Books:", db.query(Book).count())
        print("Members:", db.query(Member).count())
        print("LibraryBooks:", db.query(LibraryBook).count())
        print("Loans:", db.query(Loan).count())

        # cuantos ejemplares por estado
        by_status = (
            db.query(LibraryBook.status, LibraryBook.id)
            .all()
        )
        loaned = sum(1 for s, _ in by_status if s == LibraryBookStatus.LOANED)
        available = sum(1 for s, _ in by_status if s == LibraryBookStatus.AVAILABLE)
        print("LibraryBooks AVAILABLE:", available, "LOANED:", loaned)

        # prestamos por estado
        loans_by = db.query(Loan.status, Loan.id).all()
        active = sum(1 for s, _ in loans_by if s == LoanStatus.ACTIVE)
        returned = sum(1 for s, _ in loans_by if s == LoanStatus.RETURNED)
        late = sum(1 for s, _ in loans_by if s == LoanStatus.LATE)
        print("Loans ACTIVE:", active, "RETURNED:", returned, "LATE:", late)
    finally:
        db.close()

if __name__ == "__main__":
    main()