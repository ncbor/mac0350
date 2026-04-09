from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates_dia8")
likes = 0

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "likes": likes, "aba": "likes"})

@app.get("/aba/{nome}")
def get_aba(nome: str, request: Request):
    if nome == "likes":
        return templates.TemplateResponse("likes.html", {"request": request, "likes": likes})
    return HTMLResponse(f"<h2>{nome.capitalize()}</h2><p>Conteúdo da aba {nome}</p>")

@app.post("/curtir")
def curtir(request: Request):
    global likes
    if "reset" in request.query_params:
        likes = 0
    else:
        likes += 1
    return templates.TemplateResponse("likes_content.html", {"request": request, "likes": likes})
