# Projeto Individual MAC0350 | REGEx BCC IME-USP | Documentação

O projeto individual foi a construção de um portal unificado da REGEx, REunião dos Grupos de Extensão do IME USP, a fim de unificar o acesso e a divulgação das informações do grupo, com fácil gerenciamento por parte dos grupos de extensão. 

Foi implementado cumprindo as especificações detalhadas no projeto [WebMAC](https://webdev2025.lol/webmac/projeto.html).

## Como rodar o site localmente

Os arquivos de cache do Python, a pasta do ambiente virtual e o banco de dados não estão inclusos neste repositório. Para fazer a configuração inicial, instalar as dependências e popular o banco de dados (gerando o arquivo `database.db`), execute o script providenciado:

```bash
chmod +x setup.sh
./setup.sh
```

Após a configuração automatizada acima finalizar, para rodar o site localmente basta utilizar:

```bash
source venv/bin/activate
uvicorn main:app --reload
```

Acesse no seu navegador: `http://localhost:8000` ou `http://127.0.0.1:8000`

## Uso

O portal oferece funcionalidades distintas para visitantes e para os membros dos grupos de extensão.

### Para Visitantes
- **Exploração de Grupos**: Na página inicial, é possível ver todos os grupos registrados, com busca e filtros dinâmicos. Utilize a barra de pesquisa para encontrar grupos específicos. A listagem pode ser ordenada alfabeticamente ou manter a ordem padrão.
- **Calendário Unificado**: Acesse a aba "Calendário" para ver uma agenda completa com eventos futuros e o histórico de eventos passados.
- **Páginas de Grupo**: Cada grupo possui uma página dedicada com descrição, sua própria lista de eventos, link para o site oficial do grupo, e links auxiliares para divulgação (ainda não implementados)
- **Modo Escuro (Dark Mode)**: No cabeçalho, clique no ícone de tema para alternar entre as versões clara e escura do portal.

### Gerenciamento (Painel Administrativo)

Para gerenciar o conteúdo, clique em **Entrar** no menu superior. 

#### Como Logar
Existem dois níveis de permissão no site:

**1. Administrador Central**

- **Usuário**: `admin`
- **Senha**: `admin`

**2. Acesso de Grupo**
Permite gerenciar apenas o conteúdo (eventos e perfil) do seu próprio grupo.
- **Usuário**: Nome do grupo em minúsculas (ex: `imesec`, `codelab`, `maratonusp`, etc).
- **Senha**: Mesma do usuário.

#### Funcionalidades sobre o Banco de Dados:
- **Gerenciar Eventos**:
    - **Criar**: Adicionar novos eventos através do formulário dedicado.
    - **Editar**: Modificar detalhes de eventos existentes.
    - **Excluir**: Remover eventos da agenda.
- **Editar Perfil do Grupo**: 
    - Atualizar a descrição, o site oficial, e a imagem de logo (via URL externa ou realizando upload de arquivos).

### OBSERVAÇÃO IMPORTANTE:

**!!! O DIRETÓRIO NÃO ESTÁ SANITIZADO PARA VULNERABILIDADES DE SEGURANÇA !!!**


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
│   ├── css             -> Estilos usados + Dark Mode.
│   │   └── style.css   
│   └── images          -> Logos e imagens enviadas via upload.
│
└── templates       -> Páginas HTML utilizadas (Jinja2).
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


## Funcionalidades Implementadas

### 1. Interface e Responsividade
- **Múltiplas Rotas e Templates**: Utilização de Jinja2 para renderização de páginas distintas (`index`, `group`, `calendar`, `admin` e `login`).
- **Layout Responsivo**: Implementação de Flexbox e Grid em CSS puro, garantindo compatibilidade com diferentes resoluções de tela.
- **Gerenciamento de Temas**: Alternância entre tema claro e escuro persistida via `localStorage` e variáveis CSS (`:root`).

### 2. Persistência de Dados (SQLModel)
- **Modelagem Relacional**: Definição de entidades `ExtensionGroup` e `Event` com relacionamento de chave estrangeira (Um-para-Muitos).
- **Banco de Dados SQLite**: Uso do `SQLModel` para integração entre o modelo de dados e a persistência em arquivo local.
- **Idempotência no Seed**: Script de inicialização que verifica a existência prévia de registros para evitar duplicidade de dados.

### 3. Autenticação e Controle de Acesso
- **Autenticação via JWT**: Implementação de fluxos de login com geração e validação de JSON Web Tokens.
- **RBAC (Role-Based Access Control)**: Diferenciação de permissões entre o Administrador Central (acesso global) e Administradores de Grupo (acesso restrito aos dados da própria entidade).
- **Persistência de Sessão**: Armazenamento de tokens em Cookies e LocalStorage para manutenção do estado de autenticação.

### 4. Interatividade com HTMX
- **Filtragem Dinâmica**: Busca de grupos na página inicial via `hx-get`, realizando consultas parciais e atualização seletiva do DOM.
- **CRUD Administrativo**: Execução das operações de criação (`POST`), edição (`GET/PUT`) e remoção (`DELETE`) de eventos via requisições assíncronas HTMX.
- **Feedback de Interface**: Uso de confirmações nativas via `hx-confirm` e atualizações de status sem recarregamento da página.

### 5. Gerenciamento de Arquivos
- **Upload de Logos**: Suporte para recebimento de arquivos via multipart form data (`UploadFile`).
- **Persistência de Mídia**: Armazenamento de imagens no diretório `static/images/` com atualização automática dos endereços no banco de dados.
