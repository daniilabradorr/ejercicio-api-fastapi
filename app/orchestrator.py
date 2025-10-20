"""Hago este arichvo para moestra arquitectura 
por capas ya que aqui podria añadir pasos 
extras como logs, etc ahoa solo delego en el servicio"""

from sqlalchemy.orm import Session
from app.services.loan_service import LoanService

class Orchestrator:
    #orquesto flujos de préstamo. Ahora mismo delego en el servicio.

    def __init__(self, db: Session):
        self.db = db

    def borrow(self, library_book_id: int, member_id: int, days: int = 7):
        # Aquí podría hacer preprocesado; de momento delego
        return LoanService(self.db).borrow(library_book_id, member_id, days)

    def return_(self, loan_id: int):
        return LoanService(self.db).return_(loan_id)

    def mark_late(self, loan_id: int):
        return LoanService(self.db).mark_late(loan_id)