from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class Aluno(SQLModel, table=True):
    nusp: int = Field(default=None, primary_key=True)
    nome: str
    idade: int
    tarefas: List["Tarefa"] = Relationship(back_populates="aluno")

class Tarefa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    duracao: int
    aluno_nusp: int = Field(foreign_key="aluno.nusp")
    aluno: Aluno = Relationship(back_populates="tarefas")
