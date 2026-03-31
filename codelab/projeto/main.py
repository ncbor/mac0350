from fastapi import FastAPI, Depends, Form, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from contextlib import asynccontextmanager

from database import create_db_and_tables, engine, get_session
from models import ExtensionGroup, Event

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

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

@app.get("/events/{event_id}/edit", response_class=HTMLResponse)
async def edit_event(request: Request, event_id: int, session: Session = Depends(get_session)):
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

@app.post("/events", response_class=HTMLResponse)
async def create_event(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    group_id: int = Form(...),
    session: Session = Depends(get_session)
):
    event = Event(title=title, date=date, description=description, group_id=group_id)
    session.add(event)
    session.commit()
    session.refresh(event)
    return templates.TemplateResponse(
        request=request,
        name="components/event_row.html",
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
    session: Session = Depends(get_session)
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
        name="components/event_row.html",
        context={"request": request, "event": event}
    )

@app.delete("/events/{event_id}")
async def delete_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if event:
        session.delete(event)
        session.commit()
    return HTMLResponse("")
