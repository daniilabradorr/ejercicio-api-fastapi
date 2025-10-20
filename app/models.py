#los imports
from __future__ import annotations
from datetime import datetime,timezone
import enum

from sqlalchemy import (
    String, Integer, Text, DateTime, ForeignKey, UniqueConstraint, Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

#declaro los enums para la depencia cuando declare los modelos para el ORM
class BookCategory(str, enum.Enum):
    SciFi = "SciFi"
    History = "History"
    Kids = "Kids"
    Fantasy = "Fantasy"
    Other = "Other"

class LibraryBookStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    LOANED = "LOANED"
    LOST = "LOST"
    DAMAGED = "DAMAGED"

class LoanStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    LATE = "LATE"


#declaro los modelos
class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)

    # 1:N con Book
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete")


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        UniqueConstraint("isbn", name="uq_books_isbn"),
        Index("ix_books_title", "title"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)

    isbn: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    category: Mapped[BookCategory] = mapped_column(
        SQLEnum(BookCategory, native_enum=False), default=BookCategory.Other, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    author: Mapped["Author"] = relationship(back_populates="books")
    library_books: Mapped[list["LibraryBook"]] = relationship(back_populates="book", cascade="all, delete")


class Member(Base):
    __tablename__ = "members"
    __table_args__ = (
        UniqueConstraint("email", name="uq_members_email"),
        Index("ix_members_name", "full_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), nullable=False)
    blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    loans: Mapped[list["Loan"]] = relationship(back_populates="member")


class LibraryBook(Base):
    __tablename__ = "library_books"
    __table_args__ = (
        UniqueConstraint("inventory_code", name="uq_librarybook_inventory_code"),
        Index("ix_library_books_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)

    inventory_code: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[LibraryBookStatus] = mapped_column(
        SQLEnum(LibraryBookStatus, native_enum=False),
        default=LibraryBookStatus.AVAILABLE, nullable=False
    )
    location: Mapped[str | None] = mapped_column(String(80))
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    book: Mapped["Book"] = relationship(back_populates="library_books")
    # añado cascade para que al borrar un ejemplar se borren sus loans devueltos
    loans: Mapped[list["Loan"]] = relationship(back_populates="library_book", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        Index("ix_loans_libbook_status", "library_book_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    library_book_id: Mapped[int] = mapped_column(ForeignKey("library_books.id"), nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)

    loan_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    return_date: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[LoanStatus] = mapped_column(
        SQLEnum(LoanStatus, native_enum=False),
        default=LoanStatus.ACTIVE, nullable=False
    )

    library_book: Mapped["LibraryBook"] = relationship(back_populates="loans")
    member: Mapped["Member"] = relationship(back_populates="loans")
