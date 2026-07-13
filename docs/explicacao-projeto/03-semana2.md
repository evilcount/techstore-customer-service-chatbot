# Capítulo 2 · Semana 2 — A linha de montagem (LangChain LCEL)

**Arquivo:** `TechStorePlus_LangChain_LCEL_Chatbot.ipynb`

## O que foi construído

A semana 2 pega o mesmo atendente da semana 1 e o **reconstrói com ferramentas profissionais**. O que ele faz não muda muito — entender, responder, resumir, arquivar. *Como* ele faz muda completamente: em vez de funções soltas costuradas à mão, o fluxo vira uma **linha de montagem formal** usando a biblioteca **LangChain** e sua notação **LCEL** (*LangChain Expression Language*).

> **💡 Analogia** — a semana 1 foi uma oficina de fundo de quintal: funciona, mas cada mecânico aperta os parafusos do seu jeito. A semana 2 transforma a oficina numa **fábrica com esteira**: cada estação faz uma coisa só, o carro passa de estação em estação, e há câmeras de inspeção em cada ponto. Se algo sair torto, sabemos exatamente em qual estação foi.

As três estações da esteira:

```text
mensagem do cliente
   ↓
[Estação 1: ANÁLISE]     classifica a mensagem numa ficha validada (Pydantic)
   ↓
[Estação 2: RESPOSTA]    encaminha para 1 de 5 "personas especialistas" e gera a resposta
   ↓
[Estação 3: RESUMO]      monta o resumo final SEM chamar o LLM (de graça!)
   ↓
ficha final da conversa (ConversationSummary)
```

## As melhorias, uma a uma

### 1. Adeus, gambiarra de JSON — chega o fiscal de qualidade (Pydantic)

Lembra do "plano B" da semana 1, que limpava manualmente o JSON que o LLM devolvia errado? A semana 2 elimina isso com **Pydantic**: em vez de *pedir* um formato e torcer, definimos um **molde rígido** e a biblioteca *garante* que a resposta se encaixa nele.

```python
class ExtractedEntities(BaseModel):
    """Informações específicas extraídas da mensagem."""
    product_name: Optional[str] = Field(None, description='The specific product mentioned')
    order_number: Optional[str] = Field(None, description='The order number (e.g. #TEC-2024-001)')
    date: Optional[str]         = Field(None, description='Any date mentioned')

class QueryAnalysis(BaseModel):
    """A ficha de classificação — agora com campos de preenchimento OBRIGATÓRIO e restrito."""
    query_category:     Literal['technical_support', 'billing', 'returns',
                                'product_inquiry', 'general_information']
    urgency_level:      Literal['low', 'medium', 'high']
    customer_sentiment: Literal['positive', 'neutral', 'negative']
    entities:           ExtractedEntities
```

*Tradução:* o tipo `Literal[...]` significa "**só** estes valores são aceitos". Se o LLM tentar devolver `urgency_level: "muito alta"`, o programa rejeita na hora com um erro claro — em vez de aceitar silenciosamente e quebrar três etapas depois.

> **💡 Analogia** — na semana 1, o formulário era de papel e o atendente podia escrever qualquer coisa nos campos. Agora o formulário é **digital com menus de seleção**: no campo "urgência" só existem três opções clicáveis. Ficou impossível preencher errado.

E a mágica que conecta o molde ao LLM é uma linha só:

```python
analysis_chain = analysis_prompt | analysis_llm.with_structured_output(QueryAnalysis)
```

O `with_structured_output(QueryAnalysis)` diz ao LLM: "sua resposta DEVE se encaixar neste molde" — e a OpenAI força isso do lado de lá. A gambiarra de limpeza morreu.

### 2. O símbolo `|` — a esteira em notação de código

Repare no `|` (barra vertical) da linha acima. Na notação **LCEL**, ele significa "**e depois passa para**": `prompt | llm` lê-se "monte o prompt *e depois passe para* o LLM". É a esteira da fábrica escrita em código. A linha de montagem completa fica:

```python
chain_with_context = (
    RunnablePassthrough.assign(          # Estação 1: adiciona o campo "analysis" à ficha
        analysis=RunnableLambda(lambda x: {'query': x['query']}) | analysis_chain
    )
    | RunnablePassthrough.assign(        # Estação 2: adiciona o campo "response"
        response=RunnableLambda(route_response)
    )
    | RunnablePassthrough.assign(        # Estação 3: adiciona o campo "summary"
        summary=RunnableLambda(build_summary)
    )
)
```

*Tradução:* `RunnablePassthrough.assign(...)` é uma estação que **acrescenta uma informação nova ao pacote que passa pela esteira**, sem apagar as anteriores. O pacote entra só com a pergunta do cliente e sai com pergunta + análise + resposta + resumo.

### 3. Cinco especialistas em vez de um generalista (`CATEGORY_PROMPTS`)

Na semana 1, um único prompt tentava dar conta de tudo. Agora existem **cinco prompts distintos, um por categoria**, cada um com sua persona e suas regras:

```python
CATEGORY_PROMPTS = {
    'technical_support': ChatPromptTemplate.from_messages([
        ('system',
         'You are a TechStore Plus technical support specialist.\n'   # persona: técnico
         'Guidelines:\n'
         '- Begin with empathy if sentiment is negative.\n'            # comece com empatia
         '- Provide 2-3 concrete troubleshooting steps.\n'             # dê 2-3 passos práticos
         '- If urgency is high, offer escalation to a senior tech.'),  # urgente? escale
        ...
    ]),
    'billing': ChatPromptTemplate.from_messages([
        ('system',
         'You are a TechStore Plus billing specialist.\n'              # persona: financeiro
         '- Be professional and formal in tone.\n'                     # tom formal
         '- Reference the order number if mentioned.'),                # cite o nº do pedido
        ...
    ]),
    # ... + returns, product_inquiry, general_information
}
```

E a função `route_response` é o **porteiro** que lê a categoria na ficha de análise e entrega a mensagem ao especialista certo. Um técnico responde diferente de um vendedor — e agora isso está explícito e organizado num lugar só.

> **💡 Analogia** — deixou de ser um balcão único e virou uma **central com ramais**: "para suporte técnico, ramal 1; para financeiro, ramal 2...". A diferença é que quem digita o ramal é o próprio sistema, baseado na classificação automática.

### 4. O resumo de graça (`build_summary`)

Melhoria de custo elegante: na semana 1, o resumo final era uma **terceira chamada ao LLM** (mais latência, mais centavos). Na semana 2, percebeu-se que todas as informações do resumo **já estavam em mãos** — categoria, sentimento, urgência, produtos, entidades vieram da Estação 1; a resposta veio da Estação 2. Então o resumo é **montado por código comum**, sem IA:

```python
def build_summary(inputs):
    analysis = inputs['analysis']         # ficha da Estação 1 (já validada)
    response = inputs['response']         # resposta da Estação 2
    return ConversationSummary(
        timestamp=datetime.now().isoformat(),
        query_category=analysis.query_category,        # copia da análise
        customer_sentiment=analysis.customer_sentiment,
        urgency_level=analysis.urgency_level,
        resolution_status=STATUS_MAP[analysis.urgency_level],  # regra fixa: alta→escalado,
        ...                                                    # média→pendente, baixa→resolvido
    )
```

*Tradução:* uma chamada de LLM a menos por conversa = resposta mais rápida e mais barata, com resultado **determinístico** (sempre igual para a mesma entrada). Lição de arquitetura: **não use IA onde uma regra simples resolve**.

A regra fixa de status é um bom exemplo:

| Urgência detectada | Status do caso |
|--------------------|----------------|
| alta | `escalated` (escalado para humano) |
| média | `pending` (pendente) |
| baixa | `resolved` (resolvido) |

### 5. As câmeras de inspeção (LangSmith)

A semana 2 também liga a **observabilidade**: com uma chave opcional, cada execução da esteira é gravada na plataforma **LangSmith** — que mostra, para cada conversa, quanto tempo e quantos **tokens** (a unidade de cobrança dos LLMs) cada estação consumiu, e o que exatamente entrou e saiu de cada uma.

```python
# Precisa ser configurado ANTES de criar qualquer LLM — a biblioteca lê isso na criação
os.environ.setdefault('LANGCHAIN_PROJECT', 'Advanced-Customer-Agent')
if os.getenv('LANGCHAIN_API_KEY', '').strip():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'    # liga as câmeras
```

> **💡 Analogia** — é a caixa-preta do avião + as câmeras da fábrica. Quando um cliente receber uma resposta estranha, dá para "rebobinar a fita" e ver: a classificação errou? O prompt do especialista estava ruim? O LLM alucinou? Sem isso, depurar um chatbot é adivinhação.

## Semana 1 vs. Semana 2 — o placar

| Aspecto | Semana 1 (na unha) | Semana 2 (LCEL) |
|---------|--------------------|------------------|
| Leitura do JSON | Manual, com gambiarra de limpeza | Pydantic valida automaticamente |
| Formato errado do LLM | Quebra silenciosa | Erro claro e imediato (`ValidationError`) |
| Roteamento | Espalhado pelo código | Encapsulado num roteador explícito |
| Resumo | 3ª chamada de LLM (paga) | Montado por código (grátis) |
| Visibilidade | Nenhuma | LangSmith: tempo e custo por etapa |
| Categorias | 8 genéricas | 5 com persona especialista cada |

## O que ainda falta

O atendente já é organizado e inspecionável, mas ainda tem duas limitações grandes:

1. **Memória curta e sem consulta a sistemas** — ele lembra da conversa atual, mas não consegue *fazer* nada: não consulta pedidos, não agenda visita, não abre chamado.
2. **Só sabe o que está no prompt** — as políticas cabem numa ficha, mas e quando a base de conhecimento tiver 200 páginas de manuais?

A primeira limitação é atacada na **semana 3** (ferramentas + memória híbrida). A segunda, no **módulo 2 inteiro** (RAG).

---

## Passo a passo: como o código foi construído

O notebook da semana 2 foi construído em três "componentes" + a montagem final — exatamente nesta ordem, com um teste isolado após cada componente.

### Passo 1 — Setup: as câmeras ligam antes de tudo

```python
from langchain_openai import ChatOpenAI                       # o LLM embrulhado pelo LangChain
from langchain_core.prompts import ChatPromptTemplate         # moldes de prompt com lacunas
from langchain_core.runnables import RunnablePassthrough, RunnableLambda  # peças da esteira
from pydantic import BaseModel, Field                         # o fiscal de formato

# ⚠️ ORDEM IMPORTA: o rastreamento precisa ser configurado ANTES de criar
# qualquer LLM — a biblioteca lê essas variáveis NO MOMENTO da criação.
os.environ.setdefault('LANGCHAIN_PROJECT', 'Advanced-Customer-Agent')
if os.getenv('LANGCHAIN_API_KEY', '').strip():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'     # com chave → câmeras ligadas
else:
    os.environ['LANGCHAIN_TRACING_V2'] = 'false'    # sem chave → roda normal, sem gravação
```

*O bug que essa ordem evita:* se o LLM fosse criado antes dessas linhas, o rastreamento silenciosamente não funcionaria — sem erro, sem aviso. Bugs de ordem de inicialização são dos mais traiçoeiros, e o notebook documenta isso em comentário.

### Passo 2 — Componente 1: o classificador com molde (células 6-7)

Primeiro, os moldes (do menor para o maior — `ExtractedEntities` é usado dentro de `QueryAnalysis`):

```python
class ExtractedEntities(BaseModel):
    """As informações pontuais extraídas da mensagem."""
    product_name: Optional[str] = Field(None, description='The specific product mentioned')
    order_number: Optional[str] = Field(None, description='The order number (e.g. #TEC-2024-001)')
    date:         Optional[str] = Field(None, description='Any date mentioned')
```

*Repare nos `description=`:* essas descrições **não são comentários** — elas são enviadas ao LLM como parte do esquema, ensinando o que cada campo significa. Documentação que funciona.

Depois, o LLM e o prompt de análise — com uma decisão sutil de design:

```python
analysis_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Prompt de sistema MINIMALISTA de propósito: sem dicas de categoria no texto,
# para não enviesar a classificação. A mensagem humana leva SÓ a pergunta crua.
analysis_prompt = ChatPromptTemplate.from_messages([
    ('system', 'You are an expert customer service query classifier...\n'
               'Categories: technical_support | billing | returns | product_inquiry | general_information\n'
               'Urgency: low | medium | high ...'),
    ('human', '{query}'),          # ← a lacuna que será preenchida em tempo de execução
])

# A linha que une tudo — o primeiro trecho de LCEL do projeto:
analysis_chain = analysis_prompt | analysis_llm.with_structured_output(QueryAnalysis)
```

E imediatamente o **teste isolado** — antes de construir a próxima peça, prova-se que esta funciona:

```python
test_result = analysis_chain.invoke({'query': 'This is an emergency! My order #TEC-2024-001 never arrived!'})
print(test_result.query_category)     # general_information
print(test_result.urgency_level)      # high
print(test_result.entities.order_number)  # '#TEC-2024-001'  ← extraído e validado
```

*Repare:* `test_result` não é um texto ou dicionário solto — é um **objeto `QueryAnalysis` validado**. Se o LLM tivesse devolvido lixo, essa linha teria explodido com um erro claro apontando o campo problemático.

### Passo 3 — Componente 2: os cinco especialistas (célula 9)

A célula mais longa do notebook (~150 linhas) define os cinco prompts especialistas. O padrão de cada um:

```python
'technical_support': ChatPromptTemplate.from_messages([
    ('system',
     'You are a TechStore Plus technical support specialist.\n'
     'Company context: {company_context}\n\n'          # a ficha da empresa entra por lacuna
     'Guidelines:\n'
     '- Begin with empathy if sentiment is negative.\n'
     '- Provide 2-3 concrete, actionable troubleshooting steps.\n'
     '- If urgency is high, offer immediate escalation to a senior technician.\n'
     '- End with a clear next step the customer should take.'),
    ('human',
     'Customer query: {query}\n'
     'Sentiment: {sentiment} | Urgency: {urgency} | Entities: {entities_json}\n\n'
     #            ↑ a análise do Componente 1 entra AQUI, campo a campo
     'Provide a helpful, empathetic technical support response with clear next steps.')
]),
```

Cada categoria tem seu tom calibrado: o técnico dá passos de solução; o financeiro é formal e cita o número do pedido; devoluções explica prazos; vendas recomenda produtos dentro do orçamento; o generalista acolhe o resto.

E o roteador — a função que escolhe o especialista em tempo de execução:

```python
def route_response(inputs):
    analysis = inputs['analysis']      # a ficha que o Componente 1 acabou de produzir
    query = inputs['query']

    # Escolhe o prompt pela categoria; se vier algo desconhecido, cai no generalista
    prompt = CATEGORY_PROMPTS.get(analysis.query_category,
                                  CATEGORY_PROMPTS['general_information'])

    # Monta uma mini-esteira na hora (prompt escolhido | LLM) e executa
    chain = prompt | response_llm
    return chain.invoke({
        'query': query,
        'sentiment': analysis.customer_sentiment,
        'urgency': analysis.urgency_level,
        'entities_json': analysis.entities.model_dump_json(),
        'company_context': COMPANY_CONTEXT_STR,
    })
```

*Por que uma função e não um `|` fixo?* O comentário no próprio código explica: a esteira LCEL é **estática** — não sabe se ramificar sozinha. A decisão de qual prompt usar só existe **depois** que a análise rodou. Embrulhar a função em `RunnableLambda` a torna uma estação legítima da esteira, mantendo toda a lógica de desvio num único lugar. E o `.get(..., fallback)` garante: categoria desconhecida nunca quebra — cai no generalista.

### Passo 4 — Componente 3: o resumo determinístico (célula 11)

Primeiro o molde do resultado final (`ConversationSummary`, espelhando o JSON da semana 1 — compatibilidade proposital: os arquivos das duas semanas convivem na mesma pasta). Depois, duas funções auxiliares pequenas e uma decisão de design:

```python
def _short_action_from_response(response):
    """Mantém o resumo final conectado à resposta que foi de fato gerada."""
    text = _response_text(response).replace('\n', ' ').strip()
    return 'Generated customer response: ' + text[:180] + ('...' if len(text) > 180 else '')
```

*O `_` no início do nome* é a convenção Python para "função interna, não faz parte da interface pública" — organização silenciosa que facilita a manutenção.

E o `build_summary` copia os campos categóricos **da análise validada** (nunca re-perguntando ao LLM), aplica a regra fixa urgência→status, e carimba a hora. Zero tokens gastos.

### Passo 5 — A montagem final (célula 13)

```python
chain_with_context = (
    RunnablePassthrough.assign(
        analysis=RunnableLambda(lambda x: {'query': x['query']}) | analysis_chain
    )                                     # após esta estação: {query, customer_id, analysis}
    | RunnablePassthrough.assign(
        response=RunnableLambda(route_response)
    )                                     # após esta: {..., response}
    | RunnablePassthrough.assign(
        summary=RunnableLambda(build_summary)
    )                                     # após esta: {..., summary}
)

# A cadeia "oficial" devolve só o resumo (o formato pedido pela entrega);
# a versão with_context existe para as demos poderem exibir também a resposta.
full_chain = chain_with_context | RunnableLambda(lambda x: x['summary'])
```

*O detalhe do `lambda x: {'query': x['query']}`:* a `analysis_chain` espera receber **só** `{"query": ...}`, mas o pacote da esteira carrega mais coisas (customer_id etc.). Essa mini-função extrai apenas o campo necessário antes de entregar — um adaptador de tomada entre duas peças de encaixes diferentes.

### Passo 6 — Rodar, salvar, consolidar

As células finais processam as mensagens de teste pela `full_chain`, salvam cada `ConversationSummary` como JSON individual (mesmo formato de arquivo da semana 1) e geram o consolidado:

```python
saved_files = []
for item in results:
    file_path = save_conversation_json(item['result'])   # um arquivo por conversa
    saved_files.append(file_path)

consolidated = consolidate_conversations()                # o arquivo agregado
```

Com o LangSmith ligado, cada uma dessas execuções vira um **trace navegável**: as três estações, seus tempos, seus tokens, suas entradas e saídas — a régua com que as próximas semanas serão medidas.
