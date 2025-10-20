#arcihvo donde defino las REST de los prestamos

#los imports
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LoanCreate, LoanPatch, LoanOut
from app.orchestrator import Orchestrator
from app.models import Loan, LoanStatus

router = APIRouter(prefix="/loans", tags=["loans"])

@router.post("", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
def create_loan(payload: LoanCreate, db: Session = Depends(get_db)):
    # Yo delego la acción en el orquestador (flujo de negocio)
    return Orchestrator(db).borrow(payload.library_book_id, payload.member_id, days=7)

@router.get("", response_model=list[LoanOut])
def list_loans(
    status_: LoanStatus | None = None,
    member_id: int | None = None,
    library_book_id: int | None = None,
    db: Session = Depends(get_db)
):
    qs = db.query(Loan)
    if status_: qs = qs.filter(Loan.status == status_)
    if member_id: qs = qs.filter(Loan.member_id == member_id)
    if library_book_id: qs = qs.filter(Loan.library_book_id == library_book_id)
    return qs.all()

@router.get("/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: int = Path(ge=1), db: Session = Depends(get_db)):
    obj = db.get(Loan, loan_id)
    if not obj: raise HTTPException(404, "Loan not found")
    return obj

@router.patch("/{loan_id}", response_model=LoanOut)
def patch_loan(loan_id: int, payload: LoanPatch, db: Session = Depends(get_db)):
    if payload.status is None:
        raise HTTPException(422, "status is required: RETURNED or LATE")
    # Yo uso el orquestador para las transiciones de estado
    orch = Orchestrator(db)
    if payload.status == LoanStatus.RETURNED:
        return orch.return_(loan_id)
    if payload.status == LoanStatus.LATE:
        return orch.mark_late(loan_id)
    raise HTTPException(422, "Unsupported status")

@router.delete("/{loan_id}", status_code=204)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    obj = db.get(Loan, loan_id)
    if not obj: raise HTTPException(404, "Loan not found")
    db.delete(obj); db.commit()