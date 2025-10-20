# hago este archivo para validar y “documentar” los payloads sin exponer el ORM

#los imports
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from app.models import BookCategory, LibraryBookStatus, LoanStatus

# autores
class AuthorCreate(BaseModel):
    #valido longitud y dejo claro en /docs
    name: str = Field(min_length=2, max_length=120, description="Nombre único del autor")

class AuthorUpdate(BaseModel):
    #en PATCH todo opcional
    name: str | None = Field(None, min_length=2, max_length=120)

class AuthorOut(BaseModel):
    #en v2 meto todo en ConfigDict para no mutar luego
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"id": 1, "name": "Isaac Asimov"}]}
    )
    id: int
    name: str

# libros
class BookCreate(BaseModel):
    isbn: str = Field(min_length=8, max_length=20, description="ISBN único")
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    category: BookCategory
    author_id: int = Field(ge=1, description="ID de autor existente")

class BookUpdate(BaseModel):
    isbn: str | None = Field(default=None, min_length=8, max_length=20)
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    category: BookCategory | None = None
    author_id: int | None = Field(default=None, ge=1)

class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int
    isbn: str
    title: str
    description: str | None
    category: BookCategory
    created_at: datetime

# miembros
class MemberCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStr  # uso EmailStr para validar emails

class MemberUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=120)
    email: EmailStr | None = None
    blocked: bool | None = None

class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    blocked: bool
    created_at: datetime

# relacion lirbos
class LibraryBookCreate(BaseModel):
    book_id: int = Field(ge=1)
    inventory_code: str = Field(min_length=3, max_length=50, description="Código de inventario único")
    status: LibraryBookStatus = LibraryBookStatus.AVAILABLE
    location: str | None = Field(default=None, max_length=80)

class LibraryBookUpdate(BaseModel):
    status: LibraryBookStatus | None = None
    location: str | None = Field(default=None, max_length=80)

class LibraryBookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    book_id: int
    inventory_code: str
    status: LibraryBookStatus
    location: str | None
    acquired_at: datetime

# prestamos
class LoanCreate(BaseModel):
    #pido solo IDs; las reglas van en el servicio
    library_book_id: int = Field(ge=1)
    member_id: int = Field(ge=1)

class LoanPatch(BaseModel):
    #PATCH para RETURNED o LATE
    status: LoanStatus | None = None

class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    library_book_id: int
    member_id: int
    loan_date: datetime
    due_date: datetime
    return_date: datetime | None
    status: LoanStatus
