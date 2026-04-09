from fastapi import FastAPI, Depends, Form, Request, Query, HTTPException, status, File, UploadFile
import shutil
import os
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt

from database import create_db_and_tables, engine, get_session
from models import ExtensionGroup, Event

# Configurações do JWT e Segurança
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Admin hardcoded por enquanto
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode("utf-8")
    }
}

# Lógica de Login e Token
def authenticate_user(username: str, password: str, session: Session):
    admin_user = fake_users_db.get(username)
    if admin_user:
        encoded_pwd = password.encode("utf-8")
        encoded_hash = admin_user["hashed_password"].encode("utf-8")
        if bcrypt.checkpw(encoded_pwd, encoded_hash):
            return {"username": admin_user["username"], "role": "admin", "group_id": None}
    
    # Se não for admin, tenta logar como dono de um grupo (login = nome do grupo)
    groups = session.exec(select(ExtensionGroup)).all()
    for group in groups:
        login_expected = group.name.split()[0].lower()
        if username == login_expected and password == login_expected:
            return {"username": group.name, "role": "group", "group_id": group.id}
            
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)):
    # Tenta pegar o token do cookie se não veio no header (OAuth2 padrão)
    if not token:
        token = request.cookies.get("access_token")
        
    if not token:
        raise HTTPException(status_code=401, detail="Não autorizado")
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "group_id": payload.get("group_id")
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Inicialização do Banco
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Filtro pros templates saberem formatar data
def format_datetime(value):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d/%m/%Y às %Hh%M")
    except:
        return value

templates.env.filters["datetime"] = format_datetime

# --- Rotas Públicas ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})

@app.post("/token")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "group_id": user["group_id"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Salva no cookie pra persistir entre abas
    content = f'{{"access_token": "{access_token}", "token_type": "bearer"}}'
    response = HTMLResponse(content=content)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, q: str = Query(default=""), sort: str = "default", session: Session = Depends(get_session)):
    statement = select(ExtensionGroup)
    if q:
        statement = statement.where(ExtensionGroup.name.contains(q))
    
    if sort == "alpha":
        statement = statement.order_by(ExtensionGroup.name)
    elif sort == "alpha_desc":
        statement = statement.order_by(ExtensionGroup.name.desc())
        
    groups = session.exec(statement).all()
    
    # Resposta pro HTMX (filtragem dinâmica)
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(request=request, name="components/group_list.html", context={"request": request, "groups": groups})
        
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "groups": groups})

@app.get("/group/{group_id}", response_class=HTMLResponse)
async def get_group(request: Request, group_id: int, session: Session = Depends(get_session)):
    group = session.get(ExtensionGroup, group_id)
    now = datetime.now().isoformat(timespec='seconds')
    
    # Divide eventos em futuros e passados
    future = sorted([e for e in group.events if e.date >= now], key=lambda e: e.date)
    past = sorted([e for e in group.events if e.date < now], key=lambda e: e.date, reverse=True)
    
    return templates.TemplateResponse(
        request=request,
        name="group.html", 
        context={"request": request, "group": group, "future_events": future, "past_events": past}
    )

@app.get("/calendar", response_class=HTMLResponse)
async def calendar(request: Request, session: Session = Depends(get_session)):
    now = datetime.now().isoformat(timespec='seconds')
    future = session.exec(select(Event).where(Event.date >= now).order_by(Event.date)).all()
    past = session.exec(select(Event).where(Event.date < now).order_by(Event.date.desc())).all()
    groups = session.exec(select(ExtensionGroup)).all()
    
    return templates.TemplateResponse(
        request=request,
        name="calendar.html", 
        context={"request": request, "future_events": future, "past_events": past, "groups": groups}
    )

# --- Área Administrativa ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, session: Session = Depends(get_session)):
    # Pega usuário manual pra não travar se não tiver logado (o template cuida do redirect)
    token = request.cookies.get("access_token")
    user = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user = {"username": payload.get("sub"), "role": payload.get("role"), "group_id": payload.get("group_id")}
        except:
            pass
            
    events = session.exec(select(Event).order_by(Event.date)).all()
    groups = session.exec(select(ExtensionGroup)).all()
    
    current_group = None
    if user and user["role"] == "group":
        current_group = session.get(ExtensionGroup, user["group_id"])
        
    return templates.TemplateResponse(
        request=request,
        name="admin.html", 
        context={"request": request, "events": events, "groups": groups, "current_group": current_group}
    )

@app.get("/events/{event_id}/edit", response_class=HTMLResponse)
async def edit_event(request: Request, event_id: int, session: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404)
        
    # Só edita se for admin ou o dono do evento
    if user["role"] == "group" and event.group_id != user["group_id"]:
        raise HTTPException(status_code=403, detail="Não autorizado")
        
    groups = session.exec(select(ExtensionGroup)).all() if user["role"] == "admin" else [session.get(ExtensionGroup, user["group_id"])]
        
    return templates.TemplateResponse(
        request=request,
        name="components/event_edit.html", 
        context={"request": request, "event": event, "groups": groups}
    )

# Endpoints pro HTMX lidar com os rows da tabela
@app.get("/events/{event_id}/row", response_class=HTMLResponse)
async def get_event_row(request: Request, event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    return templates.TemplateResponse(request=request, name="components/event_row.html", context={"request": request, "event": event})

@app.get("/events/{event_id}/row_admin", response_class=HTMLResponse)
async def get_event_row_admin(request: Request, event_id: int, session: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    event = session.get(Event, event_id)
    if user["role"] == "group" and event.group_id != user["group_id"]:
        raise HTTPException(status_code=403)
    return templates.TemplateResponse(request=request, name="components/event_row_admin.html", context={"request": request, "event": event})

@app.post("/events", response_class=HTMLResponse)
async def create_event(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    location: str = Form(""),
    description: str = Form(...),
    group_id: int = Form(...),
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    if user["role"] == "group":
        group_id = user["group_id"]
        
    full_datetime = f"{date}T{time}:00" if len(time) == 5 else f"{date}T{time}"
    event = Event(title=title, date=full_datetime, location=location, description=description, group_id=group_id)
    session.add(event)
    session.commit()
    session.refresh(event)
    return templates.TemplateResponse(request=request, name="components/event_row_admin.html", context={"request": request, "event": event})

@app.put("/events/{event_id}", response_class=HTMLResponse)
async def update_event(
    request: Request,
    event_id: int,
    title: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    location: str = Form(""),
    description: str = Form(...),
    group_id: int = Form(...),
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    event = session.get(Event, event_id)
    if event:
        if user["role"] == "group" and event.group_id != user["group_id"]:
            raise HTTPException(status_code=403)
            
        event.title = title
        event.date = f"{date}T{time}:00" if len(time) == 5 else f"{date}T{time}"
        event.location = location
        event.description = description
        
        if user["role"] == "admin":
            event.group_id = group_id
            
        session.add(event)
        session.commit()
        session.refresh(event)
    return templates.TemplateResponse(request=request, name="components/event_row_admin.html", context={"request": request, "event": event})

@app.delete("/events/{event_id}")
async def delete_event(event_id: int, session: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    event = session.get(Event, event_id)
    if event:
        if user["role"] == "group" and event.group_id != user["group_id"]:
            raise HTTPException(status_code=403)
        session.delete(event)
        session.commit()
    return HTMLResponse("")

# Edição de perfil do grupo
@app.post("/groups/update", response_class=HTMLResponse)
async def update_group_profile(
    request: Request,
    description: str = Form(...),
    website: str = Form(...),
    logo_url: Optional[str] = Form(None),
    logo_file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    if user["role"] != "group":
        raise HTTPException(status_code=403)
        
    group = session.get(ExtensionGroup, user["group_id"])
    group.description = description
    group.website = website
    
    # Trata upload de imagem
    if logo_file and logo_file.filename:
        file_ext = os.path.splitext(logo_file.filename)[1]
        file_path = f"static/images/group_{group.id}{file_ext}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo_file.file, buffer)
        group.logo_url = f"/{file_path}"
    elif logo_url:
        group.logo_url = logo_url
        
    session.add(group)
    session.commit()
    session.refresh(group)
    
    msg = f"Perfil do grupo {group.name} atualizado!"
    return f'<div class="alert alert-success" style="padding: 1rem; background: var(--card-bg); color: var(--success); border: 1px solid var(--success); border-radius: 4px; margin-bottom: 1rem;">{msg}</div>'
