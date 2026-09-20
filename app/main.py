import secrets
import string

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="shortlink",
    description="Небольшой сервис сокращения ссылок — junior DevOps pet-проект.",
    version="1.0.0",
)

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7


def generate_code(db: Session) -> str:
    for _ in range(10):
        code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
        exists = db.query(models.Link).filter(models.Link.code == code).first()
        if not exists:
            return code
    raise RuntimeError("Не удалось сгенерировать уникальный код, попробуйте ещё раз")


@app.get("/health", tags=["service"])
def health():
    """Проверка живости сервиса — используется Docker healthcheck-ом."""
    return {"status": "ok"}


@app.post("/links", response_model=schemas.LinkOut, status_code=201, tags=["links"])
def create_link(payload: schemas.LinkCreate, db: Session = Depends(get_db)):
    code = generate_code(db)
    link = models.Link(code=code, target_url=str(payload.target_url))
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@app.get("/links/{code}", response_model=schemas.LinkOut, tags=["links"])
def get_link_stats(code: str, db: Session = Depends(get_db)):
    link = db.query(models.Link).filter(models.Link.code == code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    return link


@app.get("/{code}", tags=["redirect"])
def follow_link(code: str, db: Session = Depends(get_db)):
    link = db.query(models.Link).filter(models.Link.code == code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    link.clicks += 1
    db.commit()
    return RedirectResponse(url=link.target_url, status_code=307)
