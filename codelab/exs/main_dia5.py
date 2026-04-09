from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="templates")
db = []

class User(BaseModel):
    nome: str
    senha: str
    bio: str

def get_user(sessao: Annotated[str | None, Cookie()] = None):
    for u in db:
        if u["nome"] == sessao:
            return u
    raise HTTPException(status_code=401)

@app.get("/")
def show_create(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/users")
def create(user: User):
    db.append(user.dict())
    return {"ok": True}

@app.get("/login")
def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    for u in db:
        if u["nome"] == username and u["senha"] == password:
            response.set_cookie(key="sessao", value=username)
            return Response(headers={"Location": "/home"}, status_code=303)
    raise HTTPException(status_code=401)

@app.get("/home")
def home(request: Request, user: dict = Depends(get_user)):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})
