from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
usuarios = []

class Usuario(BaseModel):
    nome: str
    idade: int

html_pagina = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js"></script>
    <script src="https://unpkg.com/htmx.org@1.9.12/dist/ext/json-enc.js"></script>
    <title>Requests</title>
    <style>
        body { display: flex; gap: 2.5vw; justify-content: center; min-height: 90vh; background-color: #292827; color: #e0e0e0; font-family: sans-serif; }
        .secao-interacao, .secao-respostas { border: 2px solid #ff690a; border-radius: 15px; padding: 20px; width: 50%; }
        form { display: flex; flex-direction: column; }
        label { margin-top: 15px; color: #ff690a; }
        input, button { margin-top: 10px; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #1e1e1e; color: white; }
        button, input[type="submit"] { background: #ff690a; cursor: pointer; }
        #json-insert { color: #ff690a; font-size: 20px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="secao-interacao">
        <h1>Requests</h1>
        <form hx-post="/users" hx-target="#json-insert" hx-ext="json-enc">  
            <label>Nome</label><input type="text" name="nome">
            <label>Idade</label><input type="number" name="idade">
            <input type="submit" value="Enviar">
        </form>
        <hr>
        <input type="number" name="index" hx-get="/users" hx-target="#json-insert" placeholder="Índice do usuário">
        <hr>
        <button hx-get="/users" hx-target="#json-insert">Obter todos</button>
        <hr>
        <button hx-delete="/users" hx-target="#json-insert">Apagar todos</button>
    </div>
    <div class="secao-respostas">
        <h1>Respostas</h1>
        <div id="json-insert"></div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return html_pagina

@app.post("/users")
async def add(user: Usuario):
    usuarios.append(user)
    return usuarios

@app.get("/users")
async def get(index: int = None):
    if index is not None:
        return usuarios[index]
    return usuarios

@app.delete("/users")
async def delete():
    usuarios.clear()
    return []
