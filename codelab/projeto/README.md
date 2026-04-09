# REGEx BCC IME-USP - Documentação Final

O portal para divulgar, unificar e facilitar o gerenciamento dos grupos de extensão do BCC IME-USP foi implementado cumprindo as especificações detalhadas no projeto [WebMAC](https://webdev2025.lol/webmac/projeto.html).

## Como Rodar o Web App Localmente

Os arquivos de cache do Python e a pasta do ambiente virtual não estão inclusos neste repositório. Para fazer a configuração inicial, instalar as dependências e popular o banco de dados gerando o arquivo `database.db`, execute o script providenciado:

```bash
chmod +x setup.sh
./setup.sh
```

Após a configuração automatizada acima finalizar, para rodar o servidor basta utilizar:

```bash
source venv/bin/activate
uvicorn main:app --reload
```

Acesse no seu navegador: `http://localhost:8000`

## Descrição do diretório

```
.
├── README.md       -> Este arquivo (descrição do projeto e guia de uso).
├── afazeres.txt    -> Lista de pendências e melhorias futuras.
├── database.py     -> Manuseamento de SQLModel.
├── main.py         -> Servidor FastAPI com as rotas e lógicas básicas
├── models.py       -> Definições das classes de Grupos e Eventos.
├── seed.py         -> Script para popular o banco inicial.
├── setup.sh        -> Script para inicialização do ambiente.
│
├── static
│   ├── css
│   │   └── style.css -> Estilos usados + Dark Mode.
│   └── images -> Logos e imagens enviadas via upload.
│
└── templates           -> Páginas HTML utilizadas (Jinja2).
    ├── admin.html      -> Painel de controle administrativo.
    ├── base.html       -> Estrutura comum do site (cabeçalho, scripts, etc).
    ├── calendar.html   -> Agenda únificada pública de eventos.
    ├── group.html      -> Estrutura das páginas dos grupos.
    ├── index.html      -> Homepage do site com busca de grupos.
    ├── login.html      -> Formulário de autenticação para login.
    └── components      -> Fragmentos a serem importados em outros arquivos.
        ├── event_edit.html       -> Formulário de edição de eventos.
        ├── event_row.html        -> Linha simples de eventos.
        ├── event_row_admin.html  -> Linha com botões de excluir/editar.
        └── group_list.html       -> Grid de grupos da Home.
```

### Como Logar no Painel Administrativo

A plataforma suporta dois níveis de hierarquia de acesso (role-based) para facilitar o gerenciamento cooperativo:

**1. Administrador Central**
Possui poder de gerenciar, editar, cadastrar e apagar **todos os eventos de qualquer grupo**.
- **Usuário**: `admin`
- **Senha**: `admin`

**2. Acesso Limitado por Grupo**
Para limitar os líderes a editar/apagar APENAS os eventos da sua própria página, pode-se logar com as credenciais cadastradas daquele grupo. O painel listará exclusivamente as suas propriedades. O nome de usuário e senha devem ser **a primeira palavra do nome do grupo, em letras minúsculas**.
- **Usuário**: `usp` (para USP Game Dev), `uspcodelab` (para USPCodeLab), `flusp` (para FLUSP), `hardware` (para Hardware Livre), etc.
- **Senha**: Igual ao usuário (ex: `usp`, `uspcodelab`, `flusp`, etc)

## Funcionalidades Implementadas

### 1. Requisitos de Telas: HTML, CSS, JS e Responsividade
Criou-se diversas rotas usando o poderoso CSS puro (`static/css/style.css`):
- Página Inicial: Listagem de grupos de extensão.
- Página do Calendário: Tabela completa de eventos.
- Página do Grupo: Exibição focada por grupo específico.

A responsividade foi alcançada através de `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))` no CSS, `media actions` e `flex` containers, garantindo que os cards se adaptem ordenadamente no celular, e o menu alinhe verticalmente em telas menores que 768px.

### 2. O Banco de Dados e SQLModel
Aplicou-se o `FastAPI` e a lib de banco de dados ensinada `SQLModel` gerando 2 entidades de relacionamento `One-to-Many`:
- ExtensionGroup: Possui id, logo_url, descrição e múltiplos eventos.
- Event: Possui data, grupo associado (ForeignKey), descrição e link com um ExtensionGroup.

### 3. HTMX para Busca Viva (hx-get)
Implementou-se o requisito "Busca de objetos" usando HTMX.
Na página inicial, o usuário tem a Barra de Pesquisa de Grupos.
Enquanto o usuário digita na barra (com delay de `300ms`), um sinal `hx-get="/"` enviará parâmetros na requisição e renderizará apenas as linhas filtradas sem estourar nenhum load inteiro na página (`hx-target="#groups-grid"`).

### 4. Ciclo de CRUD Completo usando HTMX

No painel `/calendar`, gerenciou-se todos os Eventos através do front-end apenas utilizando tags HTML com propriedades `HTMX`:

- Ler (hx-get): Além da pesquisa da home, as rotas `/events/{id}/edit` e `/events/{id}/row` recuperam os fragmentos individuais para montagem inline no HTML.
- Criar (hx-post): O cadastro de novo evento ao fim do HTML de Calendário adiciona o elemento diretamente na tabela com a propriedade `hx-target="#events-tbody" hx-swap="beforeend"`.
- Apagar (hx-delete): Os botões vermelhos utilizam a rota para apagar via `hx-delete="/events/{{id}}"`. Há suporte dinâmico com `hx-confirm="Deletar este evento?"`.
- Atualizar (hx-put): Ao pressionar Editar via HTMX, a linha da tabela é re-renderizada exibindo inputs. Após confirmada a edição, envia-se um formulário com os valores a atualizar sob a rota PUT, o que reflete no servidor FastAPI com `session.commit`.
