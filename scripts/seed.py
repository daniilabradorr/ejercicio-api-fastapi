# scripts/seed.py
from datetime import datetime, timedelta, timezone
from app.database import SessionLocal
from app.models import (
    Author, Book, Member, LibraryBook, Loan,
    BookCategory, LibraryBookStatus, LoanStatus
)


today = datetime.now(timezone.utc)

def main():
    db = SessionLocal()
    try:
        # 1) Autores (5)
        authors = [Author(name=n) for n in [
            "Isaac Asimov","Jane Austen","J.R.R. Tolkien","George Orwell","J.K. Rowling"
        ]]
        db.add_all(authors); db.flush()

        # 2) Libros (5) -> cada uno con su author_id (1 autor por libro)
        books = [
            Book(isbn="978000000001", title="Fundación", category=BookCategory.SciFi,   author_id=authors[0].id),
            Book(isbn="978000000002", title="Orgullo y Prejuicio", category=BookCategory.History, author_id=authors[1].id),
            Book(isbn="978000000003", title="El Hobbit", category=BookCategory.Fantasy, author_id=authors[2].id),
            Book(isbn="978000000004", title="1984", category=BookCategory.SciFi,       author_id=authors[3].id),
            Book(isbn="978000000005", title="Harry Potter y la Piedra Filosofal", category=BookCategory.Kids, author_id=authors[4].id),
        ]
        db.add_all(books); db.flush()

        # 3) Miembros (5)
        members = [
            Member(full_name="Ana Gómez",  email="ana@example.com"),
            Member(full_name="Luis Pérez", email="luis@example.com"),
            Member(full_name="Sara Ríos",  email="sara@example.com"),
            Member(full_name="Joel Díaz",  email="joel@example.com"),
            Member(full_name="Mar Vega",   email="mar@example.com"),
        ]
        db.add_all(members); db.flush()

        # 4) Ejemplares  dejo 2 disponibles para pruebas happy-path
        lbooks = [
            LibraryBook(book_id=books[0].id, inventory_code="LB-0001", status=LibraryBookStatus.AVAILABLE),
            LibraryBook(book_id=books[0].id, inventory_code="LB-0002", status=LibraryBookStatus.AVAILABLE),
            LibraryBook(book_id=books[1].id, inventory_code="LB-0003", status=LibraryBookStatus.AVAILABLE),
            LibraryBook(book_id=books[2].id, inventory_code="LB-0004", status=LibraryBookStatus.AVAILABLE),
            LibraryBook(book_id=books[3].id, inventory_code="LB-0005", status=LibraryBookStatus.AVAILABLE),
            LibraryBook(book_id=books[4].id, inventory_code="LB-0006", status=LibraryBookStatus.AVAILABLE),
            LibraryBook(book_id=books[4].id, inventory_code="LB-0007", status=LibraryBookStatus.AVAILABLE),
        ]
        db.add_all(lbooks); db.flush()

        # 5) Préstamos (5): 3 ACTIVE, 1 RETURNED, 1 LATE
        today = datetime.utcnow()
        loans = [
            Loan(library_book_id=lbooks[0].id, member_id=members[0].id,
                 loan_date=today, due_date=today+timedelta(days=7), status=LoanStatus.ACTIVE),
            Loan(library_book_id=lbooks[1].id, member_id=members[1].id,
                 loan_date=today, due_date=today+timedelta(days=5), status=LoanStatus.ACTIVE),
            Loan(library_book_id=lbooks[2].id, member_id=members[2].id,
                 loan_date=today, due_date=today+timedelta(days=10), status=LoanStatus.ACTIVE),
            Loan(library_book_id=lbooks[3].id, member_id=members[3].id,
                 loan_date=today-timedelta(days=10), due_date=today-timedelta(days=3),
                 status=LoanStatus.RETURNED, return_date=today-timedelta(days=2)),
            Loan(library_book_id=lbooks[4].id, member_id=members[4].id,
                 loan_date=today-timedelta(days=10), due_date=today-timedelta(days=2),
                 status=LoanStatus.LATE),
        ]
        db.add_all(loans)

        # marco ejemplares prestados como LOANED
        loaned_ids = {ln.library_book_id for ln in loans if ln.status in (LoanStatus.ACTIVE, LoanStatus.LATE)}
        for ex in lbooks:
            if ex.id in loaned_ids:
                ex.status = LibraryBookStatus.LOANED

        db.commit()
        print("Seed OK")
    finally:
        db.close()

if __name__ == "__main__":
    main()