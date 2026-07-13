# Capítulo 9 · Semana 8 — Do agente único à central de especialistas (M3, stops 1 e 2)

**Repositório:** `c03-t05-bruno-pieri-m3-challenge` · **Arquivos:** `challenge.ipynb`, `src/graph/stop1_agent.py`, `src/graph/stop2_agent.py`, `src/database/mock_db.py`

## O contexto: o desafio final (M3) começa

O módulo 3 fecha o curso com um desafio em três paradas (*stops*), no mesmo modelo dos anteriores: as duas primeiras são formativas (exercícios de construção) e a terceira é a entrega avaliada. Todas usam a TechStore Plus como cenário e um **banco de dados simulado** fornecido pronto (`mock_db.py` — clientes, pedidos, garantias, chamados).

- **Stop 1** — reconstruir o agente básico, agora com ferramentas de loja de verdade.
- **Stop 2** — reorganizá-lo numa **central de triagem**: um roteador + três especialistas.
- **Stop 3** (capítulo 10) — promover tudo a uma equipe supervisionada, com seleção dinâmica de ferramentas e aprovação humana.

## Stop 1 — O agente básico, versão TechStore

O stop 1 é a semana 7 aplicada ao domínio da loja: mesma anatomia (estado tipado, ToolNode, trava de loop, checkpointing), mas as ferramentas deixam de ser `add`/`multiply` e passam a consultar o banco da loja:

```python
@tool
def customer_lookup(email: str) -> str:
    """Look up a customer's profile and loyalty tier by email address."""
    customer = db.get_customer(email)
    if customer is None:
        return f"No customer found for email {email!r}."     # nunca explode: responde educado
    return (f"{customer['name']} ({customer['id']}) - tier: {customer['tier']}, "
            f"status: {customer['status']}, region: {customer['preferred_region']}.")

@tool
def order_status(order_id: str) -> str:
    """Look up an order's current status, tracking number, and delivery estimate."""
    order = db.get_order(order_id)
    ...
```

O estado ficou até mais enxuto que o da semana 7 — sinal de fluência na ferramenta:

```python
class Stop1State(TypedDict):
    messages:   Annotated[list[BaseMessage], add_messages]   # o histórico
    tool_calls: Annotated[int, operator.add]                  # o contador da trava
```

Nada aqui é novidade conceitual — é o **kata de consolidação**: repetir a estrutura até ela ficar automática, porque os stops seguintes vão empilhar complexidade em cima dela.

## Stop 2 — A central de triagem: roteador → especialistas → agregador

Aqui está a mudança arquitetural da semana. Um agente único com todas as ferramentas funciona, mas tem defeitos que crescem com a escala:

- **Ferramenta errada na mão errada** — com 20 ferramentas disponíveis, o LLM às vezes escolhe mal.
- **Prompt genérico** — um faz-tudo não tem a profundidade de um especialista.
- **Sem controle de acesso** — qualquer pergunta pode acionar qualquer ferramenta.

A solução espelha um call center real:

```text
                      mensagem do cliente
                             ↓
                      ┌─────────────┐
                      │   ROTEADOR   │  classifica SEM chamar o LLM (grátis!)
                      └──────┬──────┘
        ┌──────────────┬─────┴──────┬──────────────┐
        ↓              ↓            ↓              ↓
  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐
  │ ESPECIALISTA│ │ESPECIALISTA│ │ESPECIALISTA│ │ FAILSAFE │
  │ de PEDIDOS │  │  de BASE   │ │de GARANTIA │ │(não sei  │
  │            │  │de CONHECIM.│ │            │ │ triar)   │
  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘
        └──────────────┴─────┬────────┴──────────────┘
                             ↓
                      ┌─────────────┐
                      │  AGREGADOR   │  formata a resposta final COM CITAÇÕES
                      └─────────────┘
```

### O roteador que não gasta um centavo

Detalhe de engenharia elegante: a triagem **não usa LLM** — é uma heurística de palavras-chave, instantânea e gratuita:

```python
def router_node(state):
    """Classifica em order / kb / warranty / failsafe. A ordem dos testes importa:
    'garantia do pedido ORD-002' deve cair em WARRANTY, não em ORDER —
    a palavra 'warrant' é mais específica que 'order'."""
    text = _latest_query(state).lower()
    if "warrant" in text:
        route = "warranty"                     # garantia vence (mais específica)
    elif re.search(r"\bord-\d+\b", text) or any(kw in text for kw in ("order", "tracking", ...)):
        route = "order"                        # menciona pedido/rastreio
    elif any(kw in text for kw in ("polic", "return", "product", "faq")):
        route = "kb"                           # pergunta de política/produto
    else:
        route = "failsafe"                     # não sei triar → resposta segura
    return {"route": route}
```

*Lição repetida do curso:* **não use IA onde uma regra resolve.** A triagem de 4 categorias com palavras-chave óbvias não precisa de um LLM — e a ordem dos testes (do mais específico ao mais genérico) resolve as ambiguidades.

> **💡 Analogia** — é a atendente da recepção que ouve 5 segundos e já transfere o ramal — sem consultar ninguém. E repare no **failsafe**: quando ela não sabe para onde transferir, existe um protocolo educado em vez de uma transferência aleatória.

### Especialistas com crachá de acesso restrito

Cada especialista recebe **apenas as suas ferramentas** — uma *allow-list* (lista de permissões):

```python
ORDER_TOOLS    = [lookup_order_s2, lookup_customer_s2]   # o de pedidos consulta pedidos e cadastro
KB_TOOLS       = [search_kb_s2]                          # o de conhecimento só busca artigos
WARRANTY_TOOLS = [warranty_days_s2]                      # o de garantia só calcula prazos
```

*Por que isso importa (segurança e qualidade):* o especialista de base de conhecimento **fisicamente não consegue** consultar dados de pedidos de clientes — errar de ferramenta virou impossível, não improvável. Cada um também tem seu prompt focado e um limite de **uma chamada de ferramenta por turno** (disciplina que evita vagueio).

Os nomes levam o sufixo `_s2` de propósito: os três stops mantêm **espaços de ferramentas separados** (stop 1, stop 2, stop 3), sem compartilhamento acidental — higiene de código em projeto com fases.

### O agregador e as citações

A última etapa formata a resposta final e **anexa citações** de onde cada informação veio — a mesma disciplina de auditabilidade do módulo 2, agora no mundo dos agentes:

```python
class Stop2State(TypedDict):
    messages:  Annotated[list[BaseMessage], add_messages]
    route:     str                                    # decidido uma vez pelo roteador
    citations: Annotated[list[str], operator.add]     # acumula: ["order:ORD-001", "kb:return_policy"]
```

Cada uso de ferramenta gera uma etiqueta (`order:ORD-001`, `kb:return_policy`) que o agregador junta à resposta. Quem lê sabe exatamente **qual consulta sustentou qual afirmação**.

### A mini base de conhecimento

O especialista de conhecimento busca em quatro artigos internos (política de devolução, garantia, envio, catálogo) com um casamento simples de palavras-chave — um RAG de brinquedo, suficiente para exercitar o fluxo. O projeto sabe onde mora a versão séria disso: no módulo 2.

## O que os dois stops entregaram

| | Stop 1 | Stop 2 |
|--|--------|--------|
| Estrutura | 1 agente + ferramentas | roteador → 3 especialistas + failsafe → agregador |
| Triagem | o LLM decide tudo | heurística gratuita, sem LLM |
| Ferramentas | todas no mesmo bolso | allow-list por especialista |
| Resposta | texto do LLM | texto + **citações** das consultas |
| Proteções | trava de loop, checkpoint | idem + rota failsafe |

Mas os especialistas do stop 2 ainda são **funções simples** dentro do grafo principal — todos dividem a mesma prancheta, e a triagem por palavra-chave tem seus limites. O stop 3 promove cada especialista a um **subgrafo independente e compilado**, coloca um **supervisor** de verdade no comando, adiciona **seleção dinâmica de ferramentas** e um **portão de aprovação humana**. É o capítulo final.

---

## Passo a passo: como o código foi construído

O stop 2 (`src/graph/stop2_agent.py`, 300 linhas) é o mais instrutivo para dissecar, porque mostra a **transição** — o momento em que a arquitetura muda de forma. Vamos na ordem do arquivo.

### Passo 1 — O estado com dois estilos de campo

```python
class Stop2State(TypedDict):
    """`route` usa o reducer padrão de SOBRESCRITA (o roteador o define uma vez);
    `citations` ACUMULA entre turnos de ferramenta via operator.add."""
    messages:  Annotated[list[BaseMessage], add_messages]
    route:     str                                    # sem Annotated = sobrescreve
    citations: Annotated[list[str], operator.add]     # com operator.add = acumula
```

*A escolha por campo é deliberada:* a rota é uma decisão única (o valor novo substitui), as citações são um diário (valores novos se somam). Errar essa escolha causaria bugs sutis — uma rota que "acumula" viraria lixo; citações que "sobrescrevem" perderiam histórico.

### Passo 2 — As ferramentas com namespace próprio

As quatro ferramentas do stop 2 (`lookup_order_s2`, `lookup_customer_s2`, `search_kb_s2`, `warranty_days_s2`) seguem o gabarito de sempre (docstring-vitrine, nunca explodem, normalizam entrada). A busca da mini base de conhecimento merece uma olhada — um "RAG de 10 linhas":

```python
def _kb_search(query):
    """Casamento ingênuo: conta palavras do slug presentes na pergunta."""
    query_lower = query.lower()
    best_slug, best_score = None, 0
    for slug, content in KB_ARTICLES.items():        # ex.: slug = "return_policy"
        score = sum(1 for keyword in slug.split("_")  # palavras: "return", "policy"
                    if keyword in query_lower)         # quantas aparecem na pergunta?
        if score > best_score:
            best_slug, best_score = slug, score        # guarda o melhor
    return (best_slug, KB_ARTICLES[best_slug]) if best_slug else (None, None)
```

### Passo 3 — O coração: `_run_specialist` (o turno de um especialista)

A função genérica que **todos** os especialistas compartilham — só mudam as ferramentas e o domínio:

```python
def _run_specialist(state, tools, domain, llm):
    tools_by_name = {t.name: t for t in tools}        # o catálogo DESTE especialista
    response = llm.invoke(state["messages"])           # 1º pensamento do LLM

    if not getattr(response, "tool_calls", None):
        return {"messages": [response]}                # não pediu ferramenta? já respondeu.

    if len(response.tool_calls) > 1:                   # pediu VÁRIAS? disciplina:
        logger.warning("%s specialist requested %d tool calls; truncating to the first.",
                       domain, len(response.tool_calls))
        response = response.model_copy(update={"tool_calls": response.tool_calls[:1]})
        # ↑ corta para UMA, registrando o desvio no log (visibilidade sem drama)

    call = response.tool_calls[0]
    tool_fn = tools_by_name[call["name"]]              # só encontra ferramentas do SEU bolso
    result = tool_fn.invoke(call["args"])              # executa
    tool_message = ToolMessage(content=result, name=call["name"], tool_call_id=call["id"])

    citation = _citation_for(call["name"], call["args"], result, domain)   # gera a etiqueta
    follow_up = llm.invoke(state["messages"] + [response, tool_message])   # 2º pensamento:
                                                       # redigir a resposta COM o resultado
    return {
        "messages": [response, tool_message, follow_up],
        "citations": [citation] if citation else [],   # a etiqueta vai para o diário
    }
```

*O ritmo de um turno:* pensar → (no máximo uma) ferramenta → pensar de novo com o resultado → responder. A regra de "uma ferramenta por turno" não é limitação técnica — é **disciplina imposta**, com log de aviso quando o LLM tenta exagerar.

### Passo 4 — A fábrica de especialistas com carregamento preguiçoso

```python
def _build_specialist_node(tools, domain, llm=None):
    def node(state):
        # Construído PREGUIÇOSAMENTE: especialistas não-roteados nunca criam
        # um ChatOpenAI real (e nunca precisam de OPENAI_API_KEY) numa execução.
        active_llm = llm or ChatOpenAI(model=MODEL, temperature=0).bind_tools(tools)
        return _run_specialist(state, tools, domain, active_llm)
    return node
```

*Dois ganhos numa tacada:* (1) uma pergunta de garantia **nunca** cria os LLMs de pedidos e conhecimento — não paga o custo do que não usa; (2) o parâmetro `llm=None` é a porta dos testes — o dublê entra por aqui, especialista por especialista (`llms={"order": fake, ...}` na fábrica do grafo).

### Passo 5 — Agregador e failsafe (os dois finais possíveis)

```python
def aggregator_node(state):
    """Anexa as etiquetas de citação acumuladas à resposta final."""
    last = state["messages"][-1]
    tags = " ".join(f"[{c}]" for c in state.get("citations", []))
    content = f"{last.content} {tags}".strip() if tags else last.content
    return {"messages": [AIMessage(content=content)]}
    # resultado: "Seu pedido chega dia 20. [order:ORD-001]"

def failsafe_node(state):
    """Entrada ambígua → pede esclarecimento e vai DIRETO para END
    (não passa pelo agregador — não há consulta a citar)."""
    return {"messages": [AIMessage(content=
        "I'm not sure how to help with that — could you clarify whether this is "
        "about an order, a warranty, or a general product question?")]}
```

*Repare que até a topologia comunica:* o failsafe liga direto no END, sem agregador — porque não tem citação a anexar. O desenho do grafo reflete o significado.

### Passo 6 — A montagem do grafo

```python
workflow = StateGraph(Stop2State)
workflow.add_node("router", router_node)
workflow.add_node("order_specialist",    _build_specialist_node(ORDER_TOOLS, "order", ...))
workflow.add_node("kb_specialist",       _build_specialist_node(KB_TOOLS, "kb", ...))
workflow.add_node("warranty_specialist", _build_specialist_node(WARRANTY_TOOLS, "warranty", ...))
workflow.add_node("aggregator", aggregator_node)
workflow.add_node("failsafe", failsafe_node)

workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    lambda state: state["route"],          # a decisão é simplesmente LER o campo route
    {"order": "order_specialist", "kb": "kb_specialist",
     "warranty": "warranty_specialist", "failsafe": "failsafe"},
)
workflow.add_edge("order_specialist", "aggregator")     # os 3 especialistas convergem
workflow.add_edge("kb_specialist", "aggregator")
workflow.add_edge("warranty_specialist", "aggregator")
workflow.add_edge("aggregator", END)
workflow.add_edge("failsafe", END)                       # o failsafe sai direto
```

*Um refinamento em relação à semana 7:* a aresta condicional agora é um `lambda` trivial que só lê `state["route"]` — porque a decisão **já foi tomada e gravada** pelo roteador. Separar "decidir" (nó) de "encaminhar" (aresta) deixa a decisão testável isoladamente: o teste do roteador não precisa rodar o grafo.
