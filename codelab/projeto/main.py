from fastapi import FastAPI, Depends, Form, Request, Query, HTTPException, status
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

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode("utf-8")
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    
    encoded_pwd = password.encode("utf-8")
    encoded_hash = user["hashed_password"].encode("utf-8")
    if not bcrypt.checkpw(encoded_pwd, encoded_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, q: str = Query(default=""), session: Session = Depends(get_session)):
    statement = select(ExtensionGroup)
    if q:
        statement = statement.where(ExtensionGroup.name.contains(q))
    groups = session.exec(statement).all()
    
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(
            request=request,
            name="components/group_list.html",
            context={"request": request, "groups": groups}
        )
        
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={"request": request, "groups": groups}
    )

@app.get("/group/{group_id}", response_class=HTMLResponse)
async def get_group(request: Request, group_id: int, session: Session = Depends(get_session)):
    group = session.get(ExtensionGroup, group_id)
    return templates.TemplateResponse(
        request=request,
        name="group.html", 
        context={"request": request, "group": group}
    )

@app.get("/calendar", response_class=HTMLResponse)
async def calendar(request: Request, session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.date)
    events = session.exec(statement).all()
    groups = session.exec(select(ExtensionGroup)).all()
    return templates.TemplateResponse(
        request=request,
        name="calendar.html", 
        context={"request": request, "events": events, "groups": groups}
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.date)
    events = session.exec(statement).all()
    groups = session.exec(select(ExtensionGroup)).all()
    return templates.TemplateResponse(
        request=request,
        name="admin.html", 
        context={"request": request, "events": events, "groups": groups}
    )

@app.get("/events/{event_id}/edit", response_class=HTMLResponse)
async def edit_event(request: Request, event_id: int, session: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    event = session.get(Event, event_id)
    groups = session.exec(select(ExtensionGroup)).all()
    return templates.TemplateResponse(
        request=request,
        name="components/event_edit.html", 
        context={"request": request, "event": event, "groups": groups}
    )

@app.get("/events/{event_id}/row", response_class=HTMLResponse)
async def get_event_row(request: Request, event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    return templates.TemplateResponse(
        request=request,
        name="components/event_row.html", 
        context={"request": request, "event": event}
    )

@app.get("/events/{event_id}/row_admin", response_class=HTMLResponse)
async def get_event_row_admin(request: Request, event_id: int, session: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    event = session.get(Event, event_id)
    return templates.TemplateResponse(
        request=request,
        name="components/event_row_admin.html", 
        context={"request": request, "event": event}
    )

@app.post("/events", response_class=HTMLResponse)
async def create_event(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    group_id: int = Form(...),
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    event = Event(title=title, date=date, description=description, group_id=group_id)
    session.add(event)
    session.commit()
    session.refresh(event)
    return templates.TemplateResponse(
        request=request,
        name="components/event_row_admin.html",
        context={"request": request, "event": event}
    )

@app.put("/events/{event_id}", response_class=HTMLResponse)
async def update_event(
    request: Request,
    event_id: int,
    title: str = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    group_id: int = Form(...),
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    event = session.get(Event, event_id)
    if event:
        event.title = title
        event.date = date
        event.description = description
        event.group_id = group_id
        session.add(event)
        session.commit()
        session.refresh(event)
    return templates.TemplateResponse(
        request=request,
        name="components/event_row_admin.html",
        context={"request": request, "event": event}
    )

@app.delete("/events/{event_id}")
async def delete_event(event_id: int, session: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    event = session.get(Event, event_id)
    if event:
        session.delete(event)
        session.commit()
    return HTMLResponse("")
