from sqlmodel import SQLModel, create_engine, Session

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

# Cria as tabelas no SQLite
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Injeção de dependência pra pegar a sessão do bd
def get_session():
    with Session(engine) as session:
        yield session
