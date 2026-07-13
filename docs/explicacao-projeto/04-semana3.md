# Capítulo 3 · Semana 3 — Memória de longo prazo e mãos para trabalhar

**Arquivos principais:** `src/chains/memory_agent.py`, `src/components/hybrid_memory.py`, `src/components/customer_tools.py`, `src/mcp/notion_followup_server.py`

## O que foi construído

Até aqui o atendente conversava bem, mas tinha duas deficiências graves para o mundo real:

1. **Memória de peixinho** — ele lembrava da conversa atual, mas conversas longas iam ficando caras (reenviar o histórico inteiro a cada mensagem) e eventualmente estouravam o limite do LLM.
2. **Mãos amarradas** — ele *falava* sobre pedidos, mas não conseguia *consultar* um pedido de verdade, nem abrir um chamado, nem agendar nada.

A semana 3 resolve os dois problemas e ainda adiciona um terceiro superpoder: criar **tarefas de follow-up automaticamente no Notion** (um aplicativo de organização usado por empresas).

Também é a semana em que o chatbot deixa de morar num notebook (arquivo de experimentos) e passa a morar em **módulos organizados** na pasta `src/` — código de gente grande, testável e reutilizável.

## Peça 1 — A memória híbrida (`HybridMemory`)

### O problema

Reenviar a conversa inteira a cada mensagem tem dois custos: dinheiro (paga-se por **token** enviado) e um teto físico — o LLM tem um limite de quanto texto consegue receber (a **janela de contexto**). As soluções tradicionais têm defeitos espelhados:

- **Janela deslizante** (manter só as últimas N mensagens): barata, mas o começo da conversa é **esquecido silenciosamente** — o cliente disse o número do pedido na mensagem 1 e o bot pergunta de novo na mensagem 15.
- **Só resumo**: mantém o fio da meada, mas perde a precisão do que foi dito palavra por palavra.

### A solução: os dois ao mesmo tempo

```text
┌─────────────────────────────────────────────┐
│ MEMÓRIA HÍBRIDA de um cliente               │
│                                             │
│  [resumo acumulado]  ← conversas antigas,   │
│                        condensadas por um    │
│                        LLM barato            │
│                                             │
│  [últimas 6 falas]   ← palavra por palavra, │
│                        precisão total        │
│                                             │
│  [ficha do cliente]  ← nome, e-mail, VIP?,  │
│                        problemas anteriores  │
│                        (NUNCA é descartada)  │
└─────────────────────────────────────────────┘
```

```python
BUFFER_SIZE = 6        # quantas falas recentes ficam guardadas palavra por palavra
MAX_TOKENS = 4_000     # orçamento máximo de texto enviado ao LLM por vez

class CustomerContext(BaseModel):
    """Ficha do cliente — vive FORA da conversa, então sobrevive a qualquer poda."""
    email: str
    name: str | None = None
    category: str | None = None        # ex.: "vip", "regular"
    preferences: list[str] = ...       # preferências conhecidas
    previous_issues: list[str] = ...   # problemas anteriores
```

*Como funciona na prática:* quando a conversa passa de 6 falas, as mais antigas são **destacadas do buffer e resumidas** por uma chamada barata de LLM; o resumo vai se acumulando num parágrafo que é sempre reenviado. O cliente pode conversar por horas — o bot nunca perde o fio, e o custo por mensagem fica controlado.

> **💡 Analogia** — é como um médico numa consulta longa: ele não relê a gravação inteira das consultas anteriores; ele lê o **resumo do prontuário** (o sumário acumulado) + as **anotações da consulta atual** (o buffer) + a **ficha do paciente** (nome, alergias — que nunca sai da capa do prontuário).

Outro detalhe de projeto importante: **uma memória por cliente, sem compartilhamento**:

```python
self._memories: dict[str, HybridMemory] = {}   # chave: e-mail do cliente

def _memory_for(self, email):
    if email not in self._memories:
        self._memories[email] = HybridMemory(customer_email=email)
    return self._memories[email]
```

*Tradução:* se as memórias se misturassem, o bot confundiria clientes e **vazaria dados pessoais** de um para outro. Cada e-mail tem sua gaveta trancada — o mesmo padrão usado em sistemas corporativos multi-cliente.

## Peça 2 — As seis ferramentas (`customer_tools.py`)

Aqui o atendente ganha mãos. Uma **ferramenta** (*tool*) é uma função do nosso sistema que o LLM pode **decidir chamar** durante a conversa. As seis da TechStore:

| Ferramenta | O que faz |
|------------|-----------|
| `get_customer_info` | Busca o cadastro do cliente pelo e-mail |
| `get_order_status` | Consulta a situação de um pedido (ex.: TEC-2024-001) |
| `get_shipping_tracking` | Retorna código de rastreio e previsão de entrega |
| `get_customer_orders` | Lista todos os pedidos de um cliente |
| `get_customer_tickets` | Lista os chamados de suporte abertos do cliente |
| `create_support_ticket` | **Abre um chamado novo** de suporte |

```python
@tool                                             # ← este selo transforma a função numa
def get_order_status(order_number: str) -> str:   #   ferramenta que o LLM enxerga
    """Look up the current status of an order by its order number (e.g. TEC-2024-001)."""
    # ↑ Esta descrição não é decorativa: é o TEXTO QUE O LLM LÊ para decidir
    #   quando usar a ferramenta. Descrição ruim = ferramenta nunca usada.
    ...consulta o banco de dados e devolve a situação...
```

> **💡 Analogia** — imagine dar ao consultor do telefone acesso a um painel com seis botões etiquetados. Ele lê as etiquetas e decide sozinho: "o cliente perguntou do pedido TEC-2024-001... vou apertar o botão *consultar pedido*". O LLM não executa nada — ele **pede** que o nosso sistema execute, recebe o resultado e continua a conversa com a informação em mãos.

As consultas batem num **banco de dados simulado** (`src/database/mock_db.py`) com clientes, pedidos e chamados fictícios — o suficiente para exercitar o fluxo completo sem depender de sistemas reais.

## Peça 3 — O cérebro agêntico (`MemoryAgent` + ReAct)

Quem coordena tudo é o `MemoryAgent`, construído sobre o padrão **ReAct** (*Reason + Act* — raciocinar e agir), usando a peça pronta `create_react_agent` da biblioteca LangGraph:

```python
class MemoryAgent:
    def __init__(self, ...):
        self._llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        # O loop ReAct pronto: pensar → usar ferramenta se precisar → pensar → responder
        self._agent = create_react_agent(self._llm, tools=TOOLS)
        self._memories = {}    # uma memória por cliente

    def chat(self, customer_email, user_text):
        memory = self._memory_for(customer_email)       # pega a gaveta do cliente
        memory.append_user(HumanMessage(content=user_text))  # anota a pergunta

        result = self._agent.invoke({"messages": memory.build_messages()})
        # ↑ o agente roda o ciclo: pode chamar 0, 1 ou várias ferramentas antes de responder

        reply = result["messages"][-1]                  # a resposta final
        memory.append_assistant(reply)                  # anota na gaveta
        ...
```

O ciclo ReAct em câmera lenta, para a pergunta *"cadê meu pedido TEC-2024-001?"*:

```text
1. LLM pensa:   "preciso consultar o pedido" → pede a ferramenta get_order_status
2. Sistema age: executa a consulta no banco → "pedido enviado, chega dia 20"
3. LLM pensa:   "agora tenho a informação" → escreve a resposta final ao cliente
```

*A diferença filosófica:* até a semana 2, o **programador** definia o fluxo (analisar → rotear → responder, sempre). Agora **o LLM decide o próprio fluxo** — quantas ferramentas usar e em que ordem. Isso é o que define um **agente**.

## Peça 4 — Follow-up automático no Notion (+ MCP)

Última peça: quando a conversa termina com uma pendência (*"vou verificar e te retorno"*), um detector identifica isso e **cria automaticamente uma tarefa no Notion** da equipe:

```python
followup_task = detect_followup_task(customer_email, user_text, reply_text)
if followup_task is not None:
    task_client.create_task(followup_task)     # nasce um card no Notion da equipe
    return f"{reply_text}\n\nNotion follow-up created."
```

E o arquivo `notion_followup_server.py` expõe essa mesma capacidade via **MCP** (*Model Context Protocol*) — um padrão aberto que funciona como uma **tomada universal para ferramentas de IA**: qualquer assistente compatível (como o Claude) pode se conectar a esse servidor e criar follow-ups da TechStore, sem código sob medida para cada integração.

> **💡 Analogia** — o MCP está para as ferramentas de IA como o USB está para os periféricos: antes, cada impressora tinha seu cabo proprietário; com o padrão, qualquer dispositivo conversa com qualquer computador. O servidor MCP da TechStore é "um pendrive de criar tarefas" que qualquer IA compatível pode plugar.

## Resumo da semana 3

| Capacidade nova | Peça responsável |
|-----------------|------------------|
| Conversas longas sem estourar custo/limite | `HybridMemory` (buffer + resumo + ficha) |
| Isolamento entre clientes | Uma memória por e-mail |
| Consultar pedidos, rastreio, cadastro, chamados | 6 ferramentas `@tool` + banco simulado |
| Abrir chamado de suporte | `create_support_ticket` |
| Decidir sozinho quando usar cada ferramenta | Agente ReAct (`create_react_agent`) |
| Criar tarefas de follow-up para a equipe | Integração Notion + servidor MCP |

Com isso o módulo 1 tem um atendente completo — que entende, lembra, age e registra. O passo seguinte é o desafio M1: **tirar isso do laboratório e colocar no ar**, como um sistema de verdade com site, login e banco de dados.

---

## Passo a passo: como o código foi construído

A semana 3 é a primeira escrita fora de notebook — módulos Python em `src/`, cada um com um papel. A ordem de construção seguiu a dependência entre as peças: primeiro a memória (não depende de nada), depois as ferramentas (dependem do banco simulado), depois o agente (usa as duas), por fim as integrações.

### Passo 1 — A memória híbrida (`hybrid_memory.py`), por dentro

O estado interno de cada memória é minimalista — três coisas:

```python
def __init__(self, customer_email):
    self.context = CustomerContext(email=customer_email)   # a ficha permanente do cliente
    self._buffer: list[BaseMessage] = []                   # as falas recentes, verbatim
    self.running_summary: str = ""                         # o resumo acumulado (começa vazio)
```

**O gatilho automático de resumo.** Cada anotação verifica se o buffer estourou:

```python
def append_user(self, message):
    self._buffer.append(message)
    if len(self._buffer) > BUFFER_SIZE:      # passou de 6 falas?
        self._summarise_displaced()          # → condensa as mais antigas
```

**A condensação (`_summarise_displaced`)** — o coração da memória:

```python
def _summarise_displaced(self):
    displaced = self._buffer[:2]        # destaca o PAR mais antigo (cliente + bot)
    self._buffer = self._buffer[2:]     # o buffer encolhe de volta

    prompt = (
        "Update the running customer-service conversation summary.\n\n"
        f"Existing summary:\n{self.running_summary or 'No previous summary.'}\n\n"
        f"New turns to incorporate:\n{new_turns}\n\n"
        "Return a concise factual summary in 2-3 sentences. Preserve customer "
        "issues, order numbers, products, promised next steps, and unresolved questions."
    )       # ↑ repare: o resumo é ATUALIZADO, não recriado — o LLM recebe o resumo
            #   anterior + as falas novas e devolve a versão incorporada

    result = self._summariser.invoke([HumanMessage(content=prompt)])
    self.running_summary = result.content.strip()
```

*Três decisões finas aqui:* (1) o par completo é destacado junto — nunca fica uma pergunta sem a resposta; (2) o prompt lista **o que não pode ser perdido** (números de pedido, promessas, pendências) — instrução explícita contra o vício natural de resumos genéricos; (3) o resumidor é criado sob demanda (`if self._summariser is None`) — quem nunca passa de 6 falas nunca paga por ele.

**A montagem final (`build_messages`)** — o que o agente de fato recebe a cada turno:

```python
def build_messages(self):
    system_parts = [
        "You are TechStore Plus's memory-aware customer service agent.",
        "If a customer asks a follow-up like 'When will it arrive?', infer the "
        "order number from recent conversation memory before asking for clarification.",
        # ↑ instrução cirúrgica: usa a memória ANTES de pedir esclarecimento
        "Customer context:",
        self.context.to_context_string(),          # a ficha permanente
    ]
    if self.running_summary.strip():
        system_parts.extend(["Conversation summary so far:", self.running_summary])

    messages = [SystemMessage(content="\n".join(system_parts)), *self._buffer]
    return trim_messages(messages, max_tokens=MAX_TOKENS,     # a cinta de segurança final:
                         strategy="last", include_system=True) # nunca passa de 4.000 tokens,
                                                               # cortando do MAIS ANTIGO,
                                                               # mas NUNCA cortando o system
```

### Passo 2 — As ferramentas (`customer_tools.py`)

Cada ferramenta segue o mesmo gabarito de 4 partes — vale ver uma completa:

```python
@tool                                                    # (1) o selo que a torna visível ao LLM
def get_order_status(order_number: str) -> str:          # (2) entrada e saída tipadas
    """Look up the current status of an order by its order number (e.g. TEC-2024-001).

    Returns the current status, or an explanatory message if not found.
    """                                                  # (3) a descrição-vitrine que o LLM lê
    order = MOCK_ORDERS.get(order_number.upper().lstrip("#"))
    if order is None:                                    # (4) o caminho triste NUNCA explode:
        return f"No order found with number {order_number}."   #    devolve explicação educada
    return (f"Order {order_number}: {order['status']}. "
            f"Items: {', '.join(order['items'])}. Total: ${order['total']}.")
```

*O detalhe do `.upper().lstrip("#")`:* clientes digitam `#tec-2024-001`, `TEC-2024-001`, `tec-2024-001`... a normalização aceita todas as variações. Pequenas gentilezas de robustez que separam demo de produto.

### Passo 3 — O agente (`memory_agent.py`)

O fluxo do método `chat` — a espinha dorsal da semana — em versão anotada completa:

```python
def chat(self, customer_email, user_text):
    # 1. Pega a gaveta de memória DESTE cliente (cria se for a primeira vez)
    memory = self._memory_for(customer_email)
    memory.append_user(HumanMessage(content=user_text))

    # 2. Desvio RAG (plugado na semana 4): pergunta "de biblioteca" nem passa
    #    pelo agente — vai direto ao assistente de documentos
    if self._rag_assistant is not None and should_use_rag(user_text):
        reply_text = self._rag_assistant.answer(user_text)
        memory.append_assistant(AIMessage(content=reply_text))
        return reply_text

    # 3. O ciclo ReAct: o agente pensa, usa 0-N ferramentas, responde
    result = self._agent.invoke({"messages": memory.build_messages()})
    reply = result["messages"][-1]          # a última mensagem é a resposta final

    # 4. Anota SÓ a resposta final na memória (não as idas-e-vindas de ferramenta —
    #    isso manteria a memória inchada sem ganho)
    memory.append_assistant(reply)

    # 5. Pós-processamento: a conversa gerou uma pendência de follow-up?
    followup_task = detect_followup_task(customer_email, user_text, reply_text)
    if followup_task is None:
        return reply_text

    # 6. Tenta criar a tarefa no Notion — com DOIS níveis de fallback educado:
    if task_client is None:
        try:
            task_client = NotionTaskClient.from_env()
        except NotionConfigError:                    # sem credenciais? avisa, não quebra
            return f"{reply_text}\n\nNotion follow-up could not be created because " \
                   "Notion credentials are not configured."
    try:
        task_client.create_task(followup_task)
    except Exception as exc:                          # Notion fora do ar? avisa, não quebra
        return f"{reply_text}\n\nNotion follow-up could not be created: {exc}"

    return f"{reply_text}\n\nNotion follow-up created."
```

*O padrão dos passos 5-6:* a resposta ao cliente **nunca** é sacrificada por uma falha na integração. O Notion pode estar mal configurado, fora do ar, sem permissão — o cliente recebe sua resposta de qualquer jeito, com um adendo transparente sobre o follow-up. Integrações externas são sempre tratadas como "podem falhar".

### Passo 4 — O detector de follow-up (`followup_detector.py`)

Um classificador 100% baseado em regras (zero LLM) — e bilíngue:

```python
FOLLOWUP_PHRASES = (
    "crie um follow-up", "criar um follow-up", "follow-up", "follow up",
    "me lembre", "lembre-me", "acompanhe", "verifique amanhã",
    "check tomorrow", "remind me",
)                                          # ← português E inglês

HIGH_PRIORITY_WORDS = ("urgente", "emergency", "asap", "imediato")

CATEGORY_KEYWORDS = (
    ("billing",  ("refund", "invoice", "reembolso", "pagamento", "cobrança", ...)),
    ("returns",  ("return", "devolução", "troca", ...)),
    ("technical_support", ("technical", "não liga", "power", "router", ...)),
    ...
)
```

A detecção: se a mensagem contém alguma frase-gatilho, nasce um `FollowUpTask` com prioridade (alta se contém palavra urgente) e categoria (pela primeira lista de palavras-chave que casar). Determinístico, instantâneo, testável — de novo o princípio: **regra onde regra basta**.

### Passo 5 — O servidor MCP (`notion_followup_server.py`)

A construção é surpreendentemente curta — o padrão MCP faz o trabalho pesado:

```python
from mcp.server.fastmcp import FastMCP

app = FastMCP("techstore-notion-followups")    # nasce o servidor, com nome

@app.tool()                                     # expõe a função como ferramenta MCP
def create_followup(task: str, customer_email: str, priority: str = "medium", ...):
    """Create a follow-up task in the TechStore Notion database."""
    followup = build_followup_task(task, customer_email, priority, ...)
    client = NotionTaskClient.from_env()
    return client.create_task(followup)
```

Qualquer assistente compatível com MCP que se conectar a esse processo ganha o botão "criar follow-up da TechStore" — sem uma linha de código de integração específica.
