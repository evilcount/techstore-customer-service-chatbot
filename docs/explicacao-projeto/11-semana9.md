# Capítulo 10 · Semana 9 — A equipe supervisionada (M3, stop 3 — entrega avaliada)

**Repositório:** `c03-t05-bruno-pieri-m3-challenge` · **Arquivos:** `src/graph/specialists.py`, `src/graph/supervisor.py`, `src/selector/bigtool.py`, `src/timetravel/repair.py`, `tests/test_stop3.py`

## O que foi construído

A entrega final do curso reúne tudo num sistema multi-agente de nível profissional, com **quatro capacidades** que respondem a quatro problemas reais de produção:

| Problema de produção | Solução do stop 3 |
|----------------------|-------------------|
| Um agente só não escala para muitos domínios | **Supervisor** coordenando especialistas independentes |
| LLMs se atrapalham com muitas ferramentas | **BigTool**: seleção dinâmica das 4 melhores por pedido |
| Ações de risco não podem ser 100% automáticas | **HITL**: pausa para aprovação humana antes de criar chamado |
| Quando algo dá errado, refazer tudo é caro | **Time-travel**: editar um checkpoint e retomar dali |

## Peça 1 — O supervisor e os subgrafos (hub-and-spoke)

A evolução em relação ao stop 2 é estrutural: cada especialista deixa de ser uma função solta e vira um **subgrafo compilado** — um grafo completo e independente (com seu próprio estado, ferramentas e proteções) que é **plugado como uma peça** dentro do grafo do supervisor:

```python
# COMPILA os grafos internos primeiro...
order    = build_order_specialist()      # grafo completo do especialista de pedidos
kb       = build_kb_specialist()         # ...da base de conhecimento
warranty = build_warranty_specialist()   # ...de garantia (com o portão HITL dentro)

# ...DEPOIS pluga cada um como um nó do grafo do supervisor
builder.add_node("order", order)
builder.add_node("kb", kb)
builder.add_node("warranty", warranty)
```

```text
                    ┌────────────┐
      cliente ────► │ SUPERVISOR │  lê a mensagem e decide o domínio
                    └─────┬──────┘
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ╔═════════════╗ ╔═════════════╗ ╔══════════════╗
   ║ SUBGRAFO    ║ ║ SUBGRAFO    ║ ║ SUBGRAFO     ║   cada um é um grafo
   ║ pedidos     ║ ║ conhecimento║ ║ garantia     ║   COMPLETO e independente
   ║ (LLM+tools) ║ ║ (LLM+tools) ║ ║ (LLM+tools+  ║
   ╚══════╤══════╝ ╚══════╤══════╝ ║  portão HITL)║
          │               │        ╚══════╤═══════╝
          └───────────────┼───────────────┘
                          ▼
                   ┌────────────┐
                   │ AGREGADOR  │ → resposta final ao cliente
                   └────────────┘
```

> **💡 Analogia** — o stop 2 era um escritório com três funcionários na mesma sala, dividindo a mesma prancheta. O stop 3 é uma empresa com **três departamentos**, cada um com sua sala, seus arquivos e seus processos internos — e um **gerente geral** (supervisor) que recebe o cliente, decide qual departamento resolve, e um **secretário** (agregador) que redige a resposta final. Departamentos podem ser testados, trocados ou promovidos sem mexer nos outros.

Um refinamento técnico que virou correção de bug real: as ferramentas do catálogo eram funções anônimas sem descrição, e tanto o executor quanto o LLM **precisam da descrição** para montar o esquema da ferramenta. A solução (`_resolve_tools`) embrulha cada entrada do catálogo num `StructuredTool` com nome, descrição (`use_for`) e esquema de argumentos vindos do próprio catálogo — sem isso, o grafo nem compilava.

## Peça 2 — BigTool: a caixa de ferramentas sob demanda

### O problema

Um sistema maduro acumula dezenas de ferramentas. Mas LLMs **degradam com mais de ~5 ferramentas à vista**: a latência sobe e os erros de escolha se multiplicam. Dar o catálogo inteiro ao agente é como despejar 50 chaves na bancada do mecânico.

### A solução: filtrar por política, ranquear, entregar no máximo 4

```python
RISK_ORDER = {"low": 0, "med": 1, "high": 2}    # escala de risco das ferramentas

def select(self, request, ctx):
    # Passo 1 — FILTRO DE POLÍTICA (portão duro, não desempate):
    candidates = [s for s in CATALOG if self._passes_policy(s, ctx)]

    # Passo 2 — RANQUEAR por aderência ao pedido:
    tokens = set(request.lower().split())
    def score(spec):
        overlap = len(tokens & set(spec.use_for.lower().split()))  # palavras em comum
        return (overlap, -RISK_ORDER[spec.risk])   # empate? vence a mais SEGURA
    candidates.sort(key=score, reverse=True)

    # Passo 3 — entregar NO MÁXIMO 4:
    return candidates[:4]
```

E o filtro de política — quatro portões que a ferramenta precisa atravessar:

```python
def _passes_policy(self, spec, ctx):
    if not spec.healthy:                                   # serviço fora do ar? barrada.
        return False
    if spec.region != "global" and spec.region != ctx.region:   # região errada? barrada.
        return False
    if not (spec.scopes & ctx.scopes):                     # sem permissão? barrada.
        return False
    if RISK_ORDER[spec.risk] > RISK_ORDER[ctx.risk_ceiling]:    # risco acima do teto? barrada.
        return False
    return True
```

*O detalhe de projeto que o módulo enfatiza:* **a política filtra ANTES do ranking** — é um portão, não um critério de desempate. Se fosse depois, uma ferramenta perigosa mas "muito relevante" poderia passar na frente. Segurança não disputa pontos com conveniência.

> **💡 Analogia** — é o almoxarifado de um hospital: o funcionário não leva o depósito inteiro ao centro cirúrgico. Ele confere **quem** está pedindo e **que autorização tem** (política), separa o que serve **para aquele procedimento** (ranking) e leva **uma bandeja pequena** (top-4). E material vencido ou interditado nem entra na triagem.

## Peça 3 — HITL: o humano no circuito

**HITL** (*Human-In-The-Loop*) é a resposta à pergunta: *o que um agente autônomo NÃO deve fazer sozinho?* Aqui, a ação sensível é **criar um chamado de garantia** (`ticket_create`) — algo que dispara processos reais na empresa. Antes de executá-la, o grafo **congela e espera um humano**:

```python
# Dentro do especialista de garantia, no nó que antecede a criação do chamado:
interrupt("ticket_create requires operator approval. Resume to proceed.")
# ↑ o grafo INTEIRO suspende aqui. O estado fica gravado no checkpoint.
#   Um operador humano inspeciona e, se aprovar, o fluxo RETOMA do ponto exato.
```

Um detalhe arquitetural deliberado: o portão vive **dentro do subgrafo de garantia**, não no supervisor. A regra de aprovação pertence a quem executa a ação — se um dia outro caminho chegar à mesma ação, o portão continua lá, impossível de contornar.

> **💡 Analogia** — o caixa do banco resolve consultas de saldo sozinho, mas transferências acima de um valor **travam no sistema até a assinatura do gerente**. O sistema não confia na boa vontade do caixa: a trava está embutida na própria operação.

É a colheita do que a semana 7 plantou: o `interrupt` só é possível porque **cada passo do grafo é checkpointado** — dá para congelar, guardar e retomar sem perder nada.

## Peça 4 — Time-travel: consertar o passado sem refazer tudo

A capacidade mais surpreendente. Como cada transição de estado vira um **checkpoint** (fotografia), é possível — quando algo deu errado no meio de uma execução — **voltar à fotografia problemática, corrigi-la, e retomar dali**, sem re-executar tudo do zero:

```python
def repair_run(app, config, edit, as_node):
    # 1. Lista o histórico de fotografias (mais recente primeiro)
    history = list(app.get_state_history(config))
    before_state = dict(history[0].values)          # 2. guarda o "antes"

    # 3. Aplica a correção NO checkpoint — isso cria um RAMO NOVO na árvore;
    #    o ramo original defeituoso é PRESERVADO (auditoria!)
    resumed_cfg = app.update_state(target_cfg, edit, as_node=as_node)

    # 4. Retoma a execução a partir do checkpoint corrigido
    app.invoke(None, resumed_cfg)                    # None = "continue de onde parou"

    # 5. Devolve o diff: antes × depois × id do novo ramo
    return {"before": before_state, "after": after_state, "branch_id": branch_id}
```

Quando usar cada abordagem (critério documentado no próprio código):

| Situação | Abordagem | Custo |
|----------|-----------|-------|
| A **entrada** estava errada (e-mail com typo, pedido errado) | Re-executar do zero | Alto — o grafo inteiro roda de novo |
| O fluxo rodou certo mas **um dado no meio** estava velho/errado | Time-travel: editar o checkpoint e retomar | Baixo — só o trecho após a correção roda |

> **💡 Analogia** — um documento com controle de versões. Descobriu-se um número errado na página 12 de um relatório de 200 páginas: ninguém redige o relatório inteiro de novo — volta-se à versão da página 12, corrige-se o número, e o restante é regenerado a partir dali. E a versão errada **fica no histórico**, porque auditoria importa: o novo ramo não apaga o antigo.

## A validação: os três casos obrigatórios

A entrega é aprovada por três testes automatizados (`tests/test_stop3.py`) — os mesmos que este projeto validou com a API real:

| Caso | O que prova | Precisa de LLM real? |
|------|-------------|:---:|
| **A — Roteamento do supervisor** | Uma conversa com perguntas de domínios diferentes aciona **≥ 2 especialistas** distintos | Sim |
| **B — Política e top-K do BigTool** | Ferramentas doentes/sem permissão/de risco são barradas; saem no máximo 4, ordenadas | Não (puro Python) |
| **C — Time-travel** | A edição de checkpoint muda o estado (`before ≠ after`) e **cria um ramo novo** | Sim |

*(Histórico da entrega: o código foi implementado e validado com LLM simulado quando a chave da API estava sem créditos; os casos A e C foram posteriormente re-executados com a API real — os três passam — e as tags `stop-1`, `stop-2` e `stop-3` foram publicadas no repositório.)*

## O que o módulo 3 entregou, em uma frase

Uma equipe de agentes especialistas — cada um um grafo independente com suas ferramentas selecionadas dinamicamente sob política de segurança — coordenada por um supervisor, com aprovação humana embutida nas ações sensíveis e a capacidade de auditar e **consertar execuções passadas** sem refazê-las.

---

## Passo a passo: como o código foi construído

O stop 3 preencheu 13 blocos `TODO` em quatro arquivos — e corrigiu um bug do scaffolding no caminho. A ordem de implementação seguiu as dependências: primeiro o seletor (não depende de nada), depois os especialistas (usam o seletor indireto via catálogo), depois o supervisor (usa os especialistas), por fim o time-travel (usa o grafo pronto).

### Passo 0 — O bug do scaffolding (`_resolve_tools`)

Antes de qualquer TODO, o grafo nem compilava. O catálogo fornecido (Task 0) define cada ferramenta como uma função anônima (*lambda*) — que não tem nome nem docstring próprios. E tanto o executor (`ToolNode`) quanto o `bind_tools` do LLM **precisam de uma descrição** para montar o esquema da ferramenta. A correção:

```python
def _resolve_tools(allow_list):
    """As entradas do CATALOG são lambdas cruas sem docstring — a conversão
    automática do LangChain não consegue montar o schema delas. Cada entrada
    é embrulhada explicitamente num StructuredTool usando os campos do
    próprio ToolSpec."""
    return [
        StructuredTool.from_function(
            func=spec.fn,                    # a função crua do catálogo
            name=spec.name,                  # o nome vem do ToolSpec
            description=spec.use_for,        # a descrição-vitrine vem do ToolSpec
            args_schema=spec.args_schema,    # o esquema de argumentos também
        )
        for spec in CATALOG
        if spec.name in allow_list           # só as ferramentas DESTE especialista
    ]
```

*A lição:* o catálogo já tinha toda a informação (nome, descrição, esquema) — só que em campos de dados, não nos lugares onde o framework procura. O embrulho `StructuredTool.from_function` faz a ponte. Diagnosticar isso exigiu ler o erro de compilação do grafo até a causa raiz.

### Passo 1 — O BigTool (`selector/bigtool.py`)

Implementação mostrada na seção anterior (filtro → ranking → top-4). O detalhe adicional do passo a passo é o **contexto de seleção** — a "credencial" que o chamador apresenta:

```python
class SelectionContext(BaseModel):
    region: str                  # onde o pedido está sendo atendido (ex.: "us")
    scopes: set[str]             # permissões de quem pede (ex.: {"orders:read"})
    risk_ceiling: str = "med"    # o risco máximo tolerado neste contexto
```

Cada pedido chega com sua credencial, e o seletor cruza credencial × catálogo. A mesma pergunta pode receber ferramentas diferentes dependendo de **quem** pergunta e **em que contexto** — controle de acesso dinâmico, não fixo.

### Passo 2 — Os especialistas como subgrafos (`graph/specialists.py`)

Cada `build_*_specialist()` monta e **compila** um grafo completo. O de pedidos, anotado:

```python
def build_order_specialist():
    order_tool_fns = _resolve_tools(ORDER_ALLOW_LIST)    # só ferramentas de pedido
    tool_node = ToolNode(order_tool_fns)

    def _route_after_order_llm(state):
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "order_tools"      # pediu ferramenta → executa
        return END                     # respondeu → fim DESTE subgrafo

    builder = StateGraph(SpecialistState)
    builder.add_node("order_llm", _order_node)          # o cérebro do especialista
    builder.add_node("order_tools", tool_node)          # as mãos
    builder.add_edge(START, "order_llm")
    builder.add_conditional_edges("order_llm", _route_after_order_llm,
                                  {"order_tools": "order_tools", END: END})
    builder.add_edge("order_tools", "order_llm")        # o ciclo pensar↔agir

    return builder.compile()      # ← COMPILA aqui: nasce uma peça fechada e plugável
```

*É a anatomia da semana 7 em miniatura* — cada especialista é um mini-agente completo. A restrição do LangGraph v1 documentada no código: **compile o grafo interno primeiro, depois `add_node`** — a ordem inversa não funciona.

### Passo 3 — O portão HITL cirúrgico (dentro do especialista de garantia)

O roteamento do especialista de garantia tem **três saídas** em vez de duas — e é aí que mora a segurança:

```python
def _route_after_warranty_llm(state):
    last = state["messages"][-1]
    calls = getattr(last, "tool_calls", None) or []
    if any(call.get("name") == "ticket_create" for call in calls):
        return "warranty_hitl_gate"     # ferramenta de ALTO RISCO → portão primeiro
    if calls:
        return "warranty_tools"         # ferramenta comum → executa direto
    return END                          # sem ferramenta → resposta final
```

E o portão em si é um nó de uma linha útil:

```python
def _warranty_hitl_gate_node(state):
    # interrupt() SUSPENDE o grafo inteiro aqui. O estado fica no checkpoint.
    # O operador inspeciona a chamada pendente e retoma com Command(resume=True).
    interrupt("ticket_create requires operator approval. Resume to proceed.")
    return {}    # aprovação é binária — retomou, passou; nenhum dado extra necessário
```

*A topologia é a política de segurança:* consultas de garantia (`warranty_check`, `refund_status` — risco baixo) fluem sem fricção; **só** o ramo do `ticket_create` passa pelo portão. E depois da aprovação, `warranty_hitl_gate → warranty_tools` — a ferramenta roda normalmente. No notebook, a retomada é:

```python
from langgraph.types import Command
app.invoke(Command(resume=True), config)    # o "carimbo do gerente"
```

### Passo 4 — O supervisor (`graph/supervisor.py`)

Com os subgrafos prontos, o supervisor é quase montagem: classificar (`supervisor_node`, heurística de palavras-chave — order/warranty/kb com kb como fallback), encaminhar (`_route_from_supervisor`, que valida a rota e usa kb para qualquer valor estranho), plugar os três subgrafos compilados, agregar (`aggregator_node` extrai a última mensagem do especialista como `final_answer`).

O contrato de montagem: `build_supervisor_graph(checkpointer)` **recebe o checkpointer de fora** — os testes passam `InMemorySaver` (rápido, descartável), um notebook de produção pode passar `SqliteSaver` (persistente em arquivo). Mesma peça, persistência à escolha do dono.

### Passo 5 — O time-travel (`timetravel/repair.py`)

A implementação (mostrada na seção anterior) segue os cinco passos do docstring: listar histórico → capturar o "antes" → `update_state(target_cfg, edit, as_node=...)` (que **cria o ramo novo**) → `invoke(None, resumed_cfg)` (retomar do checkpoint remendado) → devolver o diff `{before, after, branch_id}`.

*O detalhe do `as_node`:* a edição precisa declarar **de qual nó** ela finge vir — porque o LangGraph precisa saber de onde continuar o fluxo. Editar o estado "como se fosse o nó X" faz a retomada seguir as arestas que saem de X.

### Passo 6 — A validação e o fechamento

Os três casos de `tests/test_stop3.py` fecham o ciclo:

- **Caso A** monta o supervisor real e manda uma conversa multi-domínio, afirmando que ≥ 2 especialistas foram acionados (leitura dos checkpoints prova quais subgrafos rodaram).
- **Caso B** ataca o seletor puro: injeta um catálogo com ferramentas doentes, de região errada, sem escopo e de risco alto, e afirma que **nenhuma** passa — e que o resultado tem no máximo 4, ordenados.
- **Caso C** roda o grafo, executa um `repair_run` com uma edição, e afirma `before != after` e `branch_id` não-vazio.

O commit final do stop 3 registra tudo: os 13 TODOs preenchidos, o bug do `_resolve_tools` corrigido, o caso B passando em qualquer ambiente e os casos A e C validados — primeiro com dublê (quando a chave estava sem créditos), depois re-executados com a API real. As tags `stop-1`, `stop-2` e `stop-3` publicadas encerram formalmente a entrega.
