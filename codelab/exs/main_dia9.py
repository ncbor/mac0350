from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, SQLModel, create_engine, Field
from typing import Optional

class Aluno(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

app = FastAPI()
templates = Jinja2Templates(directory="templates_dia9")
engine = create_engine("sqlite:///dia9.db")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(Aluno)).first():
            for i in range(1, 26):
                session.add(Aluno(nome=f"Aluno {i}"))
            session.commit()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/lista")
def listar(request: Request, page: int = 1):
    limit = 5
    offset = (page - 1) * limit
    with Session(engine) as session:
        alunos = session.exec(select(Aluno).offset(offset).limit(limit)).all()
        total = len(session.exec(select(Aluno)).all())
        has_next = (offset + limit) < total
        has_prev = page > 1
        return templates.TemplateResponse("lista.html", {
            "request": request, 
            "alunos": alunos, 
            "page": page, 
            "has_next": has_next, 
            "has_prev": has_prev
        })
