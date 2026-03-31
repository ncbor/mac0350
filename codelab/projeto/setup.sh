#!/bin/bash

python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlmodel jinja2 python-multipart
python3 seed.py

echo "Configuração inicial concluída com sucesso. Banco de dados gerado."
