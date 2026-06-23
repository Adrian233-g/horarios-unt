from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from auth import require_secretaria
from database import get_db
from models import Curricula, EscuelaProfesional, Usuario
from schemas import CurriculaCreate, CurriculaResponse, CurriculaUpdate

router = APIRouter(prefix="/api/curriculas", tags=["curriculas"])


def _load_one(db: Session, curricula_id: int) -> Curricula | None:
    return (
        db.query(Curricula)
        .options(joinedload(Curricula.escuela))
        .filter(Curricula.id == curricula_id)
        .first()
    )


@router.get("", response_model=list[CurriculaResponse])
def list_curriculas(
    escuela_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_secretaria),
):
    query = db.query(Curricula).options(joinedload(Curricula.escuela))
    if escuela_id:
        query = query.filter(Curricula.escuela_id == escuela_id)
    return query.order_by(Curricula.nombre).all()


@router.get("/{curricula_id}", response_model=CurriculaResponse)
def get_curricula(
    curricula_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_secretaria),
):
    curricula = _load_one(db, curricula_id)
    if not curricula:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curricula no encontrada")
    return curricula


@router.post("", response_model=CurriculaResponse, status_code=status.HTTP_201_CREATED)
def create_curricula(
    data: CurriculaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_secretaria),
):
    if not db.query(EscuelaProfesional).filter(EscuelaProfesional.id == data.escuela_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escuela no encontrada")

    curricula = Curricula(
        nombre=data.nombre,
        escuela_id=data.escuela_id,
        activa=data.activa,
    )
    db.add(curricula)
    db.commit()
    db.refresh(curricula)
    return _load_one(db, curricula.id)


@router.put("/{curricula_id}", response_model=CurriculaResponse)
def update_curricula(
    curricula_id: int,
    data: CurriculaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_secretaria),
):
    curricula = db.query(Curricula).filter(Curricula.id == curricula_id).first()
    if not curricula:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curricula no encontrada")
    if data.escuela_id is not None:
        if not db.query(EscuelaProfesional).filter(EscuelaProfesional.id == data.escuela_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escuela no encontrada")

    for field in ("nombre", "escuela_id", "activa"):
        val = getattr(data, field)
        if val is not None:
            setattr(curricula, field, val)
    db.commit()
    return _load_one(db, curricula.id)


@router.delete("/{curricula_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curricula(
    curricula_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_secretaria),
):
    curricula = db.query(Curricula).filter(Curricula.id == curricula_id).first()
    if not curricula:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curricula no encontrada")
    # check if there are associated courses
    if curricula.cursos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la curricula tiene cursos asignados",
        )
    db.delete(curricula)
    db.commit()
