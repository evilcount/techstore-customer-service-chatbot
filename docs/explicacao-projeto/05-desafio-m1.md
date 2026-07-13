# Capítulo 4 · Desafio M1 — Do laboratório para o ar

**Repositório:** `c03-t05-bruno-pieri-m1-challenge` · **Pastas principais:** `backend/`, `frontend/`, `render.yaml`

## O que foi construído

Tudo até aqui vivia em *notebooks* — arquivos de laboratório onde o próprio desenvolvedor executa o código célula por célula. Ótimo para aprender; inútil para um cliente de verdade, que quer abrir um site, digitar e receber resposta.

O desafio M1 fecha essa lacuna: transforma o agente da semana 3 num **sistema em produção**, com três camadas independentes:

```text
┌──────────────────┐     internet      ┌──────────────────┐     ┌──────────────────┐
│   FRONTEND        │ ────────────────► │   BACKEND         │ ──► │  BANCO DE DADOS   │
│   (o site)        │  ◄──────────────  │   (a cozinha)     │ ◄── │  (o arquivo)      │
│   Next.js         │                   │   FastAPI         │     │  PostgreSQL       │
│   hospedado na    │                   │   hospedado no    │     │  hospedado no     │
│   Vercel          │                   │   Render          │     │  Render           │
└──────────────────┘                   └──────────────────┘     └──────────────────┘
                                                │
                                                ▼
                                        MemoryAgent (semana 3)
                                        + OpenAI + Notion
```

> **💡 Analogia** — o restaurante ficou pronto. O **frontend** é o salão: mesas, cardápio, garçom — o que o cliente vê e toca. O **backend** é a cozinha: onde os pedidos são de fato preparados (é lá que mora o agente da semana 3). O **banco de dados** é a despensa e o livro de comandas: nada se perde quando o restaurante fecha e reabre. E cada parte funciona num prédio separado, alugado de um provedor de nuvem.

## Peça 1 — O backend (FastAPI): o balcão de pedidos do nosso sistema

Na introdução vimos que **API** é o balcão de atendimento entre programas. Agora nós construímos o **nosso próprio balcão**, usando o framework **FastAPI**. Ele expõe "guichês" (chamados *endpoints*) na internet:

| Guichê (endpoint) | O que faz |
|-------------------|-----------|
| `GET /health` | Responde "estou vivo" — usado pelo provedor para monitorar o serviço |
| `POST /api/auth/...` | Valida a senha de acesso ao demo |
| `POST /api/chat/sessions` | Abre uma nova sessão de conversa para um e-mail |
| `POST /api/chat/sessions/{id}/messages` | Recebe uma mensagem e devolve a resposta do agente |
| `GET /api/chat/sessions/{id}/messages` | Lista o histórico da conversa |

O coração do backend, comentado:

```python
app = FastAPI(title="TechStore Plus Chat API")     # cria o "prédio" da API

app.add_middleware(
    CORSMiddleware,                                # porteiro de segurança do navegador:
    allow_origins=[settings.frontend_origin],      # só aceita pedidos vindos do NOSSO site
    ...
)

app.include_router(auth_router)                    # pendura o guichê de autenticação
app.include_router(chat_router)                    # pendura os guichês de chat

@app.get("/health")                                # o guichê "estou vivo"
def health():
    return {"status": "ok"}
```

*Sobre o CORS:* navegadores têm uma regra de segurança que impede o site A de fazer pedidos ao servidor B sem permissão explícita. O `CORSMiddleware` é onde declaramos "o site oficial da TechStore pode falar comigo; o resto, não".

### Os contratos de entrada e saída

Cada guichê define **formulários rígidos** (Pydantic de novo!) para o que entra e o que sai:

```python
class CreateSessionRequest(BaseModel):
    customer_email: EmailStr        # EmailStr valida que é um e-mail DE VERDADE
                                    # "banana" é rejeitado antes de chegar ao agente

class SendMessageResponse(BaseModel):
    session_id: str                 # o protocolo da conversa
    assistant_message: str          # a resposta do agente
    created_at: datetime            # carimbo de hora
```

*Tradução:* é a mesma filosofia da semana 2 (moldes rígidos), agora aplicada à fronteira com o mundo externo — onde ela é ainda mais importante, porque da internet chega de tudo.

### A tranca da porta

O demo é protegido por senha. Cada pedido ao chat precisa trazer a senha num campo especial do cabeçalho:

```python
def require_demo_password(x_demo_password: str = Header(default="")):
    if x_demo_password != get_settings().demo_password:
        raise HTTPException(status_code=401, detail="Invalid demo password.")
        # 401 = código universal de "não autorizado"

router = APIRouter(
    prefix="/api/chat",
    dependencies=[Depends(require_demo_password)],   # TODA rota de chat passa pela tranca
)
```

*Tradução:* o `Depends(...)` prende a verificação em **todos** os guichês de chat de uma vez — impossível esquecer a tranca numa porta nova.

### A conexão com a semana 3

E onde entra o agente? Numa dobradiça mínima e elegante:

```python
@lru_cache                          # ← cria o agente UMA vez e reaproveita sempre
def get_agent() -> Agent:           #   (criar o agente é caro; reutilizar é grátis)
    return MemoryAgent()            # ← o MESMO MemoryAgent da semana 3, sem alterações
```

*Tradução:* o backend não reinventa nada — ele **embrulha** o agente da semana 3 e o serve pela internet. É a recompensa por ter organizado o código em módulos: a peça encaixou sem retrabalho.

## Peça 2 — O banco de dados (PostgreSQL): a memória que sobrevive

Até aqui, o histórico das conversas vivia na memória do programa — desligou, perdeu. Em produção isso é inaceitável. Entra o **PostgreSQL**, um banco de dados profissional, com duas "planilhas" (tabelas):

```text
  SESSIONS (as conversas)              MESSAGES (as falas)
  ┌────────────┬───────────────┐       ┌──────┬─────────┬──────────┬───────────┐
  │ session_id │ customer_email│       │ id   │ session │ role     │ content   │
  ├────────────┼───────────────┤       ├──────┼─────────┼──────────┼───────────┤
  │ abc-123    │ ana@mail.com  │ ←──── │ 1    │ abc-123 │ user     │ "Cadê..." │
  │ def-456    │ ze@mail.com   │       │ 2    │ abc-123 │ assistant│ "Seu..."  │
  └────────────┴───────────────┘       └──────┴─────────┴──────────┴───────────┘
```

Cada fala de cada conversa vira uma linha permanente. O servidor pode reiniciar, cair, ser atualizado — as conversas continuam lá.

## Peça 3 — O frontend (Next.js): o rosto do sistema

O `frontend/` contém o site em si, feito com **Next.js** (framework da linguagem TypeScript, prima do Python voltada para interfaces web). O fluxo do usuário:

1. Abre o site → tela pede a **senha do demo**.
2. Informa seu **e-mail** → o site pede ao backend para abrir uma sessão.
3. Digita mensagens numa **tela de chat** → cada mensagem viaja ao backend, que aciona o agente e devolve a resposta.

O frontend não tem inteligência nenhuma — de propósito. Ele é só a vitrine; toda a lógica mora no backend. Essa separação permite, por exemplo, trocar o site inteiro sem tocar no agente, ou criar um aplicativo de celular que usa o mesmo backend.

## Peça 4 — O deploy (Render + Vercel): alugando os prédios

"**Deploy**" é o ato de publicar o sistema em servidores na internet. O projeto usa dois provedores com planos gratuitos:

- **Render** hospeda o backend + o banco PostgreSQL.
- **Vercel** hospeda o frontend.

E aqui entra um conceito bonito: **infraestrutura como código**. Em vez de clicar em dezenas de telas de configuração, o arquivo `render.yaml` descreve tudo que o Render precisa criar:

```yaml
services:
  - type: web
    name: techstore-chat-api
    runtime: python
    plan: free                                          # plano gratuito
    buildCommand: pip install -r backend/requirements.txt   # como construir
    startCommand: uvicorn backend.app.main:app --port $PORT # como ligar
    healthCheckPath: /health                            # onde conferir se está vivo
    envVars:
      - key: DATABASE_URL
        fromDatabase: {name: techstore-chat-db, ...}    # conecta ao banco automaticamente
      - key: OPENAI_API_KEY
        sync: false                                     # segredo: preenchido à mão, NUNCA no código

databases:
  - name: techstore-chat-db                             # o banco também nasce daqui
    plan: free
```

*Tradução:* esse arquivo é a **planta baixa do restaurante**. Entregue a planta ao Render e ele constrói tudo: o serviço web, o banco, as conexões. Se um dia for preciso reconstruir do zero, a planta garante que sai idêntico. Repare no `sync: false` das chaves — os **segredos** (senhas, chaves de API) ficam fora do código e são informados direto no painel do provedor.

## Peça 5 — Os testes: a rede de segurança

O backend tem uma bateria de testes automáticos (`pytest`): autenticação, envio de mensagens, persistência, configuração de CORS, o guichê de saúde. Eles rodam com um **agente falso** (que responde sempre a mesma coisa) — porque o objetivo é testar o *encanamento* do backend, não a inteligência.

> **💡 Analogia** — antes de abrir o restaurante, o bombeiro testa os hidrantes com água comum — não precisa de um incêndio real. Os testes garantem que, quando o agente de verdade estiver plugado, os canos aguentam.

## O teste de fumaça final

O README define o ritual de verificação pós-deploy (o *smoke test* — "ligou, saiu fumaça?"):

1. Abrir o site na Vercel → digitar a senha do demo
2. Informar um e-mail → mandar *"Hello, can you help me?"*
3. Conferir que o assistente responde
4. Pedir *"Pode criar um follow-up para verificar meu ticket amanhã?"*
5. Conferir que **um card aparece no Notion da equipe**

Se os cinco passos passam, o circuito completo está vivo: navegador → Vercel → Render → agente → OpenAI/Notion → banco → de volta ao navegador.

## O que o módulo 1 entregou, em uma frase

Um atendente virtual que entende, lembra, consulta sistemas, age e registra — **acessível por qualquer pessoa com um navegador**, rodando em infraestrutura de nuvem descrita em código, com testes e monitoramento.

O módulo 2 ataca a fraqueza restante: o conhecimento do atendente ainda cabe num prompt. E quando a loja tiver manuais, políticas e catálogos de centenas de páginas?

---

## Passo a passo: como o código foi construído

O backend segue uma **arquitetura em camadas** — cada pasta é uma camada com uma responsabilidade, e as camadas só conversam com as vizinhas. Construir de baixo para cima:

```text
backend/app/
├── db/         camada 1: o arquivo (modelos de tabela + repositório + conexão)
├── core/       camada 2: configuração e segurança
├── services/   camada 3: a ponte para o agente da semana 3
├── api/        camada 4: os guichês HTTP (auth + chat)
└── main.py     a montagem final
```

### Passo 1 — As tabelas (`db/models.py`)

Com a biblioteca SQLAlchemy, cada tabela do banco é declarada como uma classe Python:

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"                     # nome da tabela no banco

    id: Mapped[str] = mapped_column(Text, primary_key=True,
                                    default=lambda: str(uuid4()))  # id único automático
    customer_email: Mapped[str] = mapped_column(Text, nullable=False)  # obrigatório
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",     # apagar a sessão apaga as mensagens dela
    )

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[str] = ...
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"))
    #                                        ↑ a "linha de costura": toda mensagem
    #                                          aponta para a sessão a que pertence
    role: Mapped[str] = ...        # "user" ou "assistant"
    content: Mapped[str] = ...     # o texto da fala
```

*Dois detalhes de qualidade:* o `utc_now()` usa fuso **UTC** (o padrão universal — servidores em países diferentes não podem discordar da hora); e o `cascade="all, delete-orphan"` garante que não sobram mensagens órfãs se uma sessão for apagada.

### Passo 2 — O repositório (`db/repository.py`)

O padrão **Repository** concentra todo o acesso ao banco num único lugar — nenhuma outra camada escreve consultas:

```python
class ChatRepository:
    def create_session(self, customer_email):
        session = ChatSession(customer_email=customer_email)
        self.db.add(session)          # prepara a inserção
        self.db.commit()              # grava de fato (a "assinatura no cartório")
        self.db.refresh(session)      # relê o registro (agora com id e timestamps)
        return session

    def add_message(self, session_id, role, content):
        message = ChatMessage(session_id=session_id, role=role, content=content)
        session = self.get_session(session_id)
        if session is not None:
            session.updated_at = utc_now()    # a sessão "acorda": atualiza o carimbo
        self.db.add(message)
        self.db.commit()
        ...

    def list_messages(self, session_id):
        return (self.db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)   # só desta conversa
                .order_by(ChatMessage.created_at.asc())          # em ordem cronológica
                .all())
```

*Por que isolar?* Se um dia o banco mudar (PostgreSQL → outro), ou uma consulta precisar de otimização, **um arquivo** muda. E os testes conseguem substituir o repositório inteiro por um dublê.

### Passo 3 — Configuração e segurança (`core/`)

`config.py` lê as variáveis de ambiente (URL do banco, senha do demo, origem permitida do CORS...) numa classe de settings validada. `security.py` (mostrado na seção anterior) implementa a tranca de senha. Separar configuração do código é o que permite o **mesmo código** rodar no laptop (com SQLite e senha "demo") e no Render (com PostgreSQL e segredos reais) sem nenhuma alteração.

### Passo 4 — A ponte para o agente (`services/chat_service.py`)

O arquivo inteiro tem 16 linhas — e é uma aula de encaixe limpo:

```python
from src.chains.memory_agent import MemoryAgent    # ← importa a semana 3

class Agent(Protocol):                              # o "contrato": qualquer coisa com
    def chat(self, customer_email, user_text): ...  #   um método chat() serve

@lru_cache                                          # memoização: cria UMA vez, reusa sempre
def get_agent() -> Agent:
    return MemoryAgent()
```

*O `Protocol` é o pulo do gato dos testes:* os endpoints não exigem um `MemoryAgent` — exigem "algo que tenha `.chat()`". Nos testes, entra um dublê que responde instantaneamente e de graça. Em produção, entra o agente real. Mesmo encaixe.

### Passo 5 — O guichê principal (`api/chat.py`)

O endpoint de envio de mensagem, o coração do sistema, anotado linha a linha:

```python
@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
def send_message(
    session_id: str,                          # vem da URL
    payload: SendMessageRequest,              # vem do corpo do pedido (validado!)
    db: Session = Depends(get_db),            # o FastAPI INJETA a conexão de banco
    agent: Agent = Depends(get_agent),        # ...e o agente (real ou dublê)
):
    repo = ChatRepository(db)
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
        # ↑ sessão inexistente? 404 claro, nunca um erro genérico

    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
        # ↑ mensagem vazia? 422 explicando o problema

    repo.add_message(session_id, "user", user_message)        # 1. grava a pergunta
    assistant_message = agent.chat(session.customer_email,     # 2. aciona o agente
                                   user_message)               #    (semana 3 inteira roda aqui)
    saved_reply = repo.add_message(session_id, "assistant",    # 3. grava a resposta
                                   assistant_message)
    return SendMessageResponse(                                # 4. devolve ao site
        session_id=session_id,
        assistant_message=assistant_message,
        created_at=saved_reply.created_at,
    )
```

*A ordem gravar-perguntar-gravar importa:* a pergunta do cliente é persistida **antes** de acionar o agente. Se o agente falhar no meio, a pergunta não se perde — o histórico conta a verdade.

*Sobre o `Depends(...)`:* é a **injeção de dependências** do FastAPI — o framework entrega a cada pedido uma conexão de banco fresca e o agente compartilhado. O endpoint não sabe *de onde* eles vêm; só declara *do que precisa*. É isso que torna cada guichê testável isoladamente.

### Passo 6 — A montagem (`main.py`) e o ciclo de vida

```python
app = FastAPI(title="TechStore Plus Chat API")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], ...)
app.include_router(auth_router)        # pendura os guichês de autenticação
app.include_router(chat_router)        # pendura os guichês de chat

@app.on_event("startup")
def startup():
    create_tables()                     # ao ligar: cria as tabelas se não existirem

@app.get("/health")
def health():
    return {"status": "ok"}             # o "estou vivo" que o Render consulta
```

### Passo 7 — Os testes do encanamento

A bateria de testes cobre cada guichê com o agente-dublê. Exemplo do padrão (de `test_chat_api.py`):

```python
def test_send_message_returns_assistant_reply(client):
    # 1. abre uma sessão
    created = client.post("/api/chat/sessions",
                          json={"customer_email": "ana@example.com"},
                          headers={"X-Demo-Password": "demo"})
    session_id = created.json()["session_id"]

    # 2. envia uma mensagem
    response = client.post(f"/api/chat/sessions/{session_id}/messages",
                           json={"message": "Hello!"},
                           headers={"X-Demo-Password": "demo"})

    # 3. confere o contrato: status 200, resposta presente, persistência ok
    assert response.status_code == 200
    assert response.json()["assistant_message"]
```

Sem senha → 401. Sessão inexistente → 404. Mensagem vazia → 422. Cada regra do guichê tem seu teste — e o conjunto roda em segundos, sem tocar na OpenAI.
