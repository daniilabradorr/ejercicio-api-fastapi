#Hago este aricvho para encpsular el prestar,devolver,marcar tarde y que los oruters lo delegen auqi

#los imports 
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Loan, LoanStatus, LibraryBook, LibraryBookStatus, Member

class LoanService:
    """Lógica básica de préstamos."""

    def __init__(self, db: Session):
        self.db = db  # sesión de BD para operar

    def borrow(self, library_book_id: int, member_id: int, due_days: int = 7) -> Loan:
        """Crear un préstamo."""
        # ejemplar: debe existir y estar libre
        lb = self.db.get(LibraryBook, library_book_id)
        if not lb:
            raise HTTPException(404, "LibraryBook not found")
        if lb.status != LibraryBookStatus.AVAILABLE:
            raise HTTPException(409, "LibraryBook is not available")

        # miembro: debe existir y no estar bloqueado
        member = self.db.get(Member, member_id)
        if not member:
            raise HTTPException(404, "Member not found")
        if member.blocked:
            raise HTTPException(409, "Member is blocked")

        # no puede haber otro préstamo activo del mismo ejemplar
        exists_active = (
            self.db.query(Loan)
            .filter(Loan.library_book_id == library_book_id,
                    Loan.status == LoanStatus.ACTIVE)
            .first()
        )
        if exists_active:
            raise HTTPException(409, "Active loan already exists for this copy")

        # crear préstamo y marcar ejemplar como prestado
        now = datetime.now(timezone.utc)
        loan = Loan(
            library_book_id=library_book_id,
            member_id=member_id,
            loan_date=now,
            due_date=now + timedelta(days=due_days),
            status=LoanStatus.ACTIVE,
        )
        lb.status = LibraryBookStatus.LOANED

        # guardar cambios
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        self.db.refresh(lb)
        return loan

    def return_(self, loan_id: int) -> Loan:
        """Devolver un préstamo."""
        loan = self.db.get(Loan, loan_id)
        if not loan:
            raise HTTPException(404, "Loan not found")

        # si no está activo, no hacemos nada (idempotente)
        if loan.status != LoanStatus.ACTIVE:
            return loan

        # marcar como devuelto y liberar el ejemplar
        loan.status = LoanStatus.RETURNED
        loan.return_date = datetime.now(timezone.utc)
        lb = self.db.get(LibraryBook, loan.library_book_id)
        lb.status = LibraryBookStatus.AVAILABLE

        self.db.commit()
        self.db.refresh(loan)
        self.db.refresh(lb)
        return loan

    def mark_late(self, loan_id: int) -> Loan:
        """Marcar un préstamo como tarde (si procede)."""
        loan = self.db.get(Loan, loan_id)
        if not loan:
            raise HTTPException(404, "Loan not found")

        # solo tiene sentido si está activo y ya pasó la fecha
        if loan.status == LoanStatus.ACTIVE and datetime.now(timezone.utc) > loan.due_date:
            loan.status = LoanStatus.LATE
            self.db.commit()
            self.db.refresh(loan)

        return loan

