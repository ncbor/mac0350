CREATE TABLE grupo (
    grupo_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT,
    logo_url TEXT,
    website TEXT
);

CREATE TABLE evento (
    evento_id INTEGER PRIMARY KEY,
    grupo_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data TEXT NOT NULL,
    local TEXT,
    FOREIGN KEY (grupo_id) REFERENCES grupo(grupo_id)
);
