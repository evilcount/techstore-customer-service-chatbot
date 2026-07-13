# PARTE III — Módulo 3: O Atendente que Raciocina em Etapas (LangGraph)

---

# Capítulo 8 · Semana 7 — Abrindo a caixa-preta: o fluxo desenhado à mão

**Arquivos:** `Week7_LangGraph_Challenge.ipynb`, `src/chains/langgraph_challenge_agent.py`, `tests/test_langgraph_challenge_agent.py`

## O que foi construído

Na semana 3, o agente usava uma peça pronta — `create_react_agent` — que escondia todo o ciclo "pensar → usar ferramenta → pensar" dentro de uma única chamada. Funcionava, mas era uma **caixa-preta**: impossível ver, ajustar ou testar o que acontecia lá dentro.

A semana 7 abre a caixa: o mesmo tipo de agente é **reconstruído à mão** com a biblioteca **LangGraph**, como um **grafo de estados** (*StateGraph*) — um fluxograma executável onde cada etapa, cada decisão e cada proteção fica explícita e testável.

O agente em si é proposital e humildemente simples — sabe somar e multiplicar. A simplicidade é estratégica: com ferramentas triviais, toda a atenção vai para **a estrutura do fluxo**, que é o que as semanas 8 e 9 vão sofisticar.

## O fluxograma

```text
          START (chega a pergunta)
            ↓
        ┌───────┐
   ┌───►│ agent │  o LLM pensa: "preciso de ferramenta ou já sei responder?"
   │    └───┬───┘
   │        ↓  route_after_agent (a decisão, com trava de segurança)
   │   ┌────┴─────────┬──────────────┐
   │   ↓              ↓              ↓
 ┌─┴─────┐      ┌───────────┐      END (resposta pronta)
 │ tools │      │ safe_exit │
 └───────┘      └─────┬─────┘  "atingi o limite de segurança, vou parar"
 executa a            ↓
 ferramenta e        END
 volta ao agente
```

> **💡 Analogia** — a semana 3 comprou uma máquina de café de cápsula: aperta o botão, sai café, ninguém sabe como. A semana 7 monta a máquina peça por peça: moedor, aquecedor, válvulas — e agora dá para regular a moagem, trocar uma peça, e **instalar um desligamento automático** que a máquina de cápsula não tinha.

## As peças, uma a uma

### 1. O estado tipado com "regras de acúmulo" (`AgentState`)

O **estado** é a prancheta compartilhada que circula entre as etapas do fluxo. Cada campo declara **como novas informações se combinam com as existentes** (o *reducer* — a regra de acúmulo):

```python
class AgentState(TypedDict):
    messages:   Annotated[list[BaseMessage], add_messages]  # falas: novas são ANEXADAS
    tool_calls: Annotated[int, operator.add]                # contador: valores se SOMAM
    retries:    Annotated[int, operator.add]                # contador de re-tentativas
    errors:     Annotated[list[str], operator.add]          # lista de erros: concatena
```

*Tradução:* quando uma etapa devolve `{"tool_calls": 2}`, o LangGraph não *substitui* o contador — ele **soma** (regra `operator.add`). Isso elimina uma família inteira de bugs: nenhuma etapa consegue acidentalmente zerar o histórico ou o contador de outra. É a prancheta com regras de preenchimento impressas no cabeçalho.

### 2. Ferramentas que nunca explodem

Um detalhe de projeto fino: as ferramentas aceitam entradas "frouxas" (número **ou** texto) e **nunca lançam erro** — devolvem sempre uma resposta legível, mesmo para entrada inválida:

```python
@tool
def add(a: str | float | int, b: str | float | int) -> str:
    """Add two numbers and return their sum."""
    parsed_a, error_a = _parse_number(a)         # tenta converter para número
    if error_a:
        return f"ERROR:VALIDATION: invalid value for a - {error_a}"
        # ↑ devolve um erro EDUCADO E PADRONIZADO em vez de quebrar o programa
    ...
    return str(parsed_a + parsed_b)
```

*Por quê?* Se a ferramenta explodisse, o fluxo inteiro morreria no meio. Devolvendo o erro como texto padronizado (`ERROR:VALIDATION: ...`), **o agente fica sabendo do problema e pode reagir** — explicar ao usuário, tentar de novo, ou desistir com elegância. E o prefixo padronizado permite ao nó seguinte classificar o erro automaticamente: `VALIDATION` (fatal — não adianta repetir) ou `TRANSIENT` (passageiro — vale re-tentar).

> **💡 Analogia** — é a diferença entre um funcionário que diante de um formulário rasurado **para tudo e vai embora**, e um que anota "campo X ilegível, favor reenviar" e segue o expediente. Sistemas de produção precisam do segundo.

### 3. O nó-agente: pensar e prestar contas

```python
def agent_node(state):
    # 1. Confere os resultados das ferramentas da rodada anterior:
    #    algum devolveu "ERROR:..."? Registra na prancheta, classificado.
    for msg in reversed(state["messages"]):
        if not isinstance(msg, ToolMessage):
            break
        if content.startswith("ERROR:"):
            _, cls, detail = content.split(":", 2)    # separa a classe do erro
            new_errors.append(f"tool={msg.name} class={cls} ...")

    # 2. Pede ao LLM a próxima ação (responder? chamar ferramenta?)
    response = llm.invoke(state["messages"])

    # 3. Devolve o delta para a prancheta (os reducers acumulam)
    return {
        "messages": [response],
        "tool_calls": len(response.tool_calls),   # +N no contador
        "errors": new_errors,
        "retries": transient_count,
    }
```

### 4. A trava de segurança (`route_after_agent` + `safe_exit`)

O risco clássico de agentes: o **loop infinito** — o LLM fica pedindo ferramenta atrás de ferramenta, para sempre, queimando dinheiro. A proteção é uma **decisão condicional com limite**:

```python
MAX_TOOL_CALLS = 5    # o disjuntor: no máximo 5 usos de ferramenta por rodada

def route_after_agent(state):
    base_route = tools_condition(state)      # o LLM pediu ferramenta?
    if base_route != "tools":
        return END                           # não pediu → conversa encerrada
    if state["tool_calls"] >= MAX_TOOL_CALLS:
        return "safe_exit"                   # pediu, mas estourou o limite → saída segura
    return "tools"                           # pediu e há orçamento → executa
```

E a saída segura não é um erro seco — é uma **despedida honesta**:

```python
def safe_exit_node(state):
    message = AIMessage(content=(
        "I've hit the tool-call safety limit (5) for this turn. "
        "I'm stopping here rather than looping indefinitely. "
        "Please rephrase your request more specifically."))
    return {"messages": [message],
            "errors": [f"guard=loop_cap tool_calls={state['tool_calls']} limit=5"]}
```

> **💡 Analogia** — é o disjuntor da casa. Ninguém espera precisar dele, mas quando algo entra em curto, ele **desarma antes do incêndio** — e deixa registrado no quadro qual circuito caiu.

### 5. Checkpoint e viagem no tempo (a semente da semana 9)

O grafo é compilado com um **checkpointer** — um gravador que fotografa a prancheta **a cada etapa**:

```python
return workflow.compile(
    checkpointer=checkpointer,          # grava um snapshot do estado a cada passo
    interrupt_before=interrupt_before,  # opcional: pausar ANTES de um nó (ex.: ["tools"])
)
```

Isso habilita três superpoderes:

- **Retomar** — a conversa pode parar e continuar de onde estava (cada conversa tem um `thread_id`).
- **Pausar para aprovação** — `interrupt_before=["tools"]` congela o fluxo *antes* de executar uma ferramenta; alguém revisa e autoriza (a base do "humano no circuito" da semana 9).
- **Reexecutar (replay)** — voltar a qualquer fotografia e rodar de novo dali.

### 6. A fábrica testável (`build_graph`)

A função que monta tudo aceita **peças substituíveis**:

```python
def build_graph(llm=None, checkpointer=None, interrupt_before=None):
    if llm is None:   # sem injeção → usa o LLM real da OpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(TOOLS)
    ...
```

*Por que isso importa:* os testes automatizados injetam um **LLM falso** (um dublê programado com respostas fixas) — e assim toda a estrutura do grafo (roteamento, trava, erros, checkpoint) é testada **sem gastar um centavo de API e sem depender da internet**. É o crash-test com boneco: ninguém arrisca um motorista para testar o airbag.

## Os testes de aceitação

O notebook valida quatro cenários:

| Teste | O que prova |
|-------|-------------|
| **Cadeia matemática** — "some 2,5 e 7, depois multiplique por 3" | O agente encadeia duas ferramentas na ordem certa e responde 28,5 |
| **Trava de loop** — um dublê malicioso pede ferramentas sem parar | O `safe_exit` desarma no 5º uso, com mensagem educada e erro registrado |
| **Entrada inválida** — "some 'abc' e 7" | A ferramenta devolve o erro padronizado; o agente explica sem quebrar |
| **Replay** — reexecutar a partir de um checkpoint | O histórico gravado permite voltar no tempo e continuar dali |

*Nota de rigor:* o enunciado do desafio continha um erro aritmético — afirmava que (2,5 + 7) × 3 = 27. O projeto detectou e validou o valor correto, **28,5**, documentando a discrepância. Conferir o gabarito também é engenharia.

## Resumo da semana 7

| Conceito novo | O que resolve |
|---------------|----------------|
| StateGraph explícito | O fluxo deixa de ser caixa-preta: visível, ajustável, testável |
| Estado com reducers | Etapas não sobrescrevem dados umas das outras |
| Ferramentas que não explodem | Erros viram informação útil, não crash |
| Trava de loop + saída segura | Nunca roda para sempre; falha com elegância |
| Checkpointing | Retomar, pausar para aprovação, viajar no tempo |
| Injeção de dublês | Estrutura 100% testada sem custo de API |

Com a gramática do LangGraph dominada, as semanas 8 e 9 usam essas mesmas peças para montar algo muito maior: uma **equipe de agentes especialistas sob um supervisor**.

---

## Passo a passo: como o código foi construído

O módulo `langgraph_challenge_agent.py` tem 214 linhas e foi escrito de dentro para fora: estado → ferramentas → nós → roteamento → fábrica. E os testes foram escritos **junto** — cada peça nasceu com seu teste.

### Passo 1 — O estado (o contrato de dados de todo o fluxo)

```python
class AgentState(TypedDict):
    messages:   Annotated[list[BaseMessage], add_messages]
    tool_calls: Annotated[int, operator.add]
    retries:    Annotated[int, operator.add]
    errors:     Annotated[list[str], operator.add]
```

*Como ler `Annotated[tipo, regra]`:* o primeiro item é o tipo do campo, o segundo é a **regra de fusão** quando um nó devolve um valor novo. `add_messages` é a regra especializada do LangGraph para históricos de conversa (anexa e deduplica por id); `operator.add` soma números e concatena listas. Escolher a regra certa por campo é o design inteiro deste passo.

### Passo 2 — As ferramentas (com o porquê no docstring do módulo)

O próprio arquivo documenta a decisão não-óbvia:

```python
"""WHY loosely-typed tool arguments (str | float | int)
    LangChain gera automaticamente um schema Pydantic a partir dos type hints
    da função @tool. Se `a`/`b` fossem tipados como float, um valor ruim como
    "abc" seria rejeitado por ESSE schema gerado ANTES do corpo da ferramenta
    rodar — e a mensagem de erro seria do framework, não nossa.
    Afrouxar os tipos deixa o corpo da ferramenta validar e produzir a
    mensagem amigável."""
```

*Tradução:* existe um fiscal automático que rejeitaria a entrada errada **antes** da nossa função rodar — mas com uma mensagem técnica do framework. Afrouxando o tipo declarado, a entrada ruim **entra** na função, que a valida e devolve o erro educado padronizado (`ERROR:VALIDATION: ...`). O projeto prefere ser dono das próprias mensagens de erro.

E o auxiliar de conversão compartilhado pelas duas ferramentas:

```python
def _parse_number(value):
    try:
        return float(value), None                # sucesso: (número, sem erro)
    except (TypeError, ValueError):
        return None, f"could not parse {value!r} as a number"   # falha: (nada, motivo)
```

*O padrão de retorno duplo `(valor, erro)`* evita exceções no caminho comum — quem chama decide o que fazer com o motivo da falha.

### Passo 3 — O nó-agente como fábrica (`make_agent_node`)

Repare que `make_agent_node(llm)` é uma **função que devolve outra função**:

```python
def make_agent_node(llm):                    # recebe o LLM (real ou dublê)...
    def agent_node(state):                   # ...e fabrica o nó configurado com ele
        ...
        response = llm.invoke(state["messages"])
        ...
    return agent_node
```

*Por quê?* Nós do LangGraph recebem só o estado — não têm onde receber o LLM. A fábrica "embala" o LLM dentro do nó no momento da construção (o padrão *closure*). É essa embalagem que permite aos testes injetarem o dublê.

Dentro do nó, o **varredor de erros** examina os resultados de ferramentas da rodada anterior:

```python
for msg in reversed(state["messages"]):        # anda de trás para frente
    if not isinstance(msg, ToolMessage):        # parou de ver resultados de ferramenta?
        break                                   # fim do bloco — para de varrer
    if content.startswith("ERROR:"):
        _, cls, detail = content.split(":", 2)  # "ERROR:VALIDATION: detalhe" → 3 partes
        new_errors.append(f"tool={msg.name} class={cls} detail={detail.strip()[:160]}")
```

*Por que varrer de trás para frente é seguro:* o comentário no código explica — a única aresta que chega ao agente (além do START) é `tools → agent`, então os resultados de ferramenta recém-produzidos são sempre o bloco final contíguo das mensagens. Entender a topologia do próprio grafo permite código mais simples.

### Passo 4 — O roteamento com a trava (e uma sutileza de timing)

```python
def route_after_agent(state):
    """O loop-cap vive AQUI (na aresta condicional), não dentro do nó —
    nós só devolvem deltas de estado; só arestas escolhem o próximo passo.

    O contador tool_calls foi incrementado pelo agent_node ANTES desta função
    rodar (o LangGraph aplica o delta do nó antes de avaliar a aresta) —
    então um pedido acima do limite é roteado para safe_exit e ABANDONADO
    antes de ser executado."""
```

*A sutileza:* a ferramenta número 5 **nunca roda**. O contador conta *pedidos*, o delta é aplicado antes da decisão, e o pedido que estouraria o limite morre na triagem. O teste de loop confirma isso com precisão cirúrgica (abaixo).

### Passo 5 — A fábrica do grafo (`build_graph`)

```python
workflow = StateGraph(AgentState)                 # 1. a prancheta define o grafo
workflow.add_node("agent", make_agent_node(llm))  # 2. os três nós
workflow.add_node("tools", ToolNode(TOOLS))       #    (ToolNode: executor pronto do LangGraph)
workflow.add_node("safe_exit", safe_exit_node)

workflow.add_edge(START, "agent")                 # 3. as arestas fixas
workflow.add_conditional_edges(                   # 4. a aresta condicional com o MAPA
    "agent", route_after_agent,
    {"tools": "tools", "safe_exit": "safe_exit", END: END},
)                                                  #    (o que a função devolve → para onde ir)
workflow.add_edge("tools", "agent")               # 5. o ciclo: ferramenta volta ao agente
workflow.add_edge("safe_exit", END)

return workflow.compile(checkpointer=checkpointer,          # 6. compila com gravador
                        interrupt_before=interrupt_before)   #    e pausas opcionais
```

Seis passos declarativos — o fluxograma do início do capítulo, linha por linha.

### Passo 6 — Os testes: o dublê e as provas

O dublê de LLM cabe em 10 linhas — e é a chave de todo o rigor da semana:

```python
class FakeToolCallingLLM:
    """LLM falso: devolve respostas pré-programadas, uma por chamada."""
    def __init__(self, responses):
        self._responses = list(responses)     # o roteiro
        self.calls = []                       # o registro (para inspeção)

    def invoke(self, messages):
        self.calls.append(messages)           # anota o que recebeu
        return self._responses.pop(0)         # devolve a próxima fala do roteiro
```

**Teste 1 — a cadeia matemática** (com a correção do gabarito documentada):

```python
def test_math_chain_uses_both_tools_and_returns_28_5():
    # NOTA: o exemplo do enunciado ("some 2,5 e 7, multiplique por 3" → 27.0)
    # é aritmeticamente inconsistente: (2.5 + 7) * 3 = 28.5. Este teste valida
    # o resultado CORRETO em vez do número literal (errado) do enunciado.
    fake_llm = FakeToolCallingLLM([
        _tool_call_message("add",      {"a": 2.5, "b": 7}),   # roteiro: pede a soma
        _tool_call_message("multiply", {"a": 9.5, "b": 3}),   # depois a multiplicação
        AIMessage(content="2.5 + 7 = 9.5, then 9.5 * 3 = 28.5."),  # e conclui
    ])
    app = build_graph(llm=fake_llm, checkpointer=InMemorySaver())
    result = app.invoke(initial_state("Add 2.5 and 7, then multiply by 3."), ...)

    assert "28.5" in result["messages"][-1].content
    assert result["tool_calls"] == 2          # exatamente 2 ferramentas
    assert result["errors"] == []             # zero erros
    assert len(fake_llm.calls) == 3           # o LLM foi consultado exatamente 3 vezes
```

**Teste 2 — a trava**, com um dublê sabotador que **nunca** desiste:

```python
def test_loop_cap_exits_via_safe_exit_at_exactly_five():
    # O roteiro só tem pedidos de ferramenta — nunca uma resposta final
    responses = [_tool_call_message("add", {"a": 1, "b": 1})
                 for _ in range(MAX_TOOL_CALLS + 2)]
    ...
    assert result["tool_calls"] == MAX_TOOL_CALLS               # parou EXATAMENTE em 5
    assert "safety limit" in result["messages"][-1].content     # a despedida educada saiu
    assert any(e.startswith("guard=loop_cap") for e in result["errors"])  # e ficou registrado
    assert len(fake_llm.calls) == MAX_TOOL_CALLS   # o pedido que estouraria nunca executou
```

*A última asserção é a prova da sutileza do passo 4:* o dublê tinha 7 respostas no roteiro, mas só foi consultado 5 vezes — a triagem abandonou o excesso antes de executar. Testes bons não conferem só o resultado; conferem o **mecanismo**.
