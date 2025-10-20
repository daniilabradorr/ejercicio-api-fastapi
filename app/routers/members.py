#donde defino las REST de miembros
 
#los imporst
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MemberCreate, MemberUpdate, MemberOut
from app.models import Member

router = APIRouter(prefix="/members", tags=["members"])

@router.post("",response_model=MemberOut,status_code=status.HTTP_201_CREATED,summary="Crear miembro")
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    #no dejo crear dos miembros con el mismo email
    if db.query(Member).filter(Member.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    obj = Member(**payload.model_dump())  # creo el objeto ORM desde el DTO
    db.add(obj); db.commit(); db.refresh(obj)
    return obj




@router.get("", response_model=list[MemberOut], summary="Listar miembros")
def list_members(q: str | None = Query(default=None, min_length=1), db: Session = Depends(get_db)):
    #si viene 'q' filto por nombre
    qs = db.query(Member)
    if q:
        qs = qs.filter(Member.full_name.ilike(f"%{q}%"))
    return qs.all()



@router.get("/{member_id}", response_model=MemberOut, summary="Detalle de miembro")
def get_member(member_id: int = Path(ge=1), db: Session = Depends(get_db)):
    obj = db.get(Member, member_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Member not found")
    return obj





@router.put("/{member_id}", response_model=MemberOut, summary="Reemplazar miembro (PUT)")
def put_member(member_id: int, payload: MemberCreate, db: Session = Depends(get_db)):
    obj = db.get(Member, member_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Member not found")
    #evito duplicar email en otro miembro
    if db.query(Member).filter(Member.email == payload.email, Member.id != member_id).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    obj.full_name = payload.full_name
    obj.email = payload.email
    db.commit(); db.refresh(obj)
    return obj

@router.patch("/{member_id}", response_model=MemberOut, summary="Actualizar miembro (PATCH)")
def patch_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    obj = db.get(Member, member_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Member not found")
    data = payload.model_dump(exclude_unset=True)
    #si cambian el email vuelvo a comprobar duplicados
    if "email" in data:
        if db.query(Member).filter(Member.email == data["email"], Member.id != member_id).first():
            raise HTTPException(status_code=409, detail="Email already exists")
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj



@router.delete("/{member_id}", status_code=204, summary="Eliminar miembro")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    obj = db.get(Member, member_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(obj); db.commit()