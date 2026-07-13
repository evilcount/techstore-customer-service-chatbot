# PARTE I — Módulo 1: O Nascimento do Atendente

---

# Capítulo 1 · Semana 1 — Conversando com a IA do jeito mais direto

**Arquivo:** `TechStorePlus_Customer_Service_Chatbot_Project.ipynb`

## O que foi construído

Na primeira semana nasceu a versão mais simples possível do atendente: um programa que recebe a mensagem do cliente, liga para o "consultor" (o LLM **GPT-4o-mini**, da OpenAI), e devolve a resposta. Sem atalhos, sem frameworks — cada passo escrito à mão, justamente para entender o que acontece por baixo.

Mesmo simples, essa versão já faz cinco coisas que um atendente de verdade faria:

1. **Entende e classifica** a mensagem: é problema técnico? cobrança? devolução? Qual a urgência? O cliente está irritado?
2. **Responde** de forma personalizada, seguindo as políticas da loja.
3. **Lembra da conversa** enquanto ela dura (se o cliente disse o nome na primeira mensagem, o bot não pergunta de novo na terceira).
4. **Resume e arquiva** cada conversa num arquivo padronizado.
5. **Encaminha** o caso para o time certo (suporte técnico, faturamento, devoluções...).

> **💡 Analogia** — pense num atendente de balcão no primeiro dia de trabalho, com um manual da empresa na mão. Ele ainda não conhece os sistemas internos nem o estoque, mas já sabe: ouvir, entender o tipo de problema, responder com educação seguindo o manual, anotar tudo numa ficha e encaminhar para o setor certo.

## As peças, uma a uma

### 1. O manual da empresa (`COMPANY_CONTEXT`)

Lembra que o LLM é um consultor culto que **não conhece a sua empresa**? A primeira peça resolve isso: uma "ficha da empresa" com tudo que o atendente precisa saber — nome, horários, produtos, políticas de troca e frete.

```python
# Ficha da empresa: um dicionário Python (pares "rótulo: valor")
COMPANY_CONTEXT = {
    "company_name": "TechStore Plus",
    "business_hours": {
        "monday_friday": "09:00-18:00",   # seg-sex, 9h às 18h
        "saturday": "10:00-14:00"          # sábado, 10h às 14h
    },
    "products": ["Laptops", "Smartphones", "Tablets", "Headphones", ...],
    "policies": {
        "shipping": "Free nationwide shipping for purchases over $500.",
        "returns": "30 days for exchanges and 7 days for refunds.",
        # ... garantia de 12 meses, financiamento etc.
    },
}
```

*Tradução:* isso é só uma estrutura de dados — uma ficha organizada. O pulo do gato é o que fazemos com ela a seguir.

### 2. As instruções permanentes (`SYSTEM_ROLE`)

Aqui a ficha da empresa é **injetada dentro do prompt de sistema** — as instruções permanentes que o LLM recebe antes de qualquer conversa:

```python
SYSTEM_ROLE = f"""
You are a professional customer service assistant for {COMPANY_CONTEXT['company_name']}.

Your behavior:
- Be polite, helpful, clear, and professional.        # seja educado e profissional
- If the customer is upset, acknowledge with empathy. # se o cliente estiver chateado, demonstre empatia
- Do not invent unavailable company policies.         # NÃO invente políticas que não existem
- Use the company context below as your source of truth.  # use a ficha abaixo como fonte da verdade

Company context:
{json.dumps(COMPANY_CONTEXT, indent=2)}   # ← a ficha inteira entra aqui, em formato JSON

Conversation flow:
1. Personalized greeting.                  # 1. cumprimente
2. Collect basic customer information...   # 2. colete nome, e-mail, nº do pedido
3. Identify inquiry type...                # 3. identifique o tipo de dúvida
4. Route the case...                       # 4. encaminhe para o time certo
5. Give clear next steps.                  # 5. dê os próximos passos
"""
```

*Tradução:* o `f"""..."""` é um texto com lacunas — o Python preenche `{...}` com valores reais. Estamos literalmente escrevendo o **roteiro de treinamento do atendente**, incluindo a regra de ouro dos chatbots corporativos: *"não invente políticas"*. Sem essa instrução, o LLM tenderia a responder qualquer pergunta com confiança — mesmo inventando prazos de devolução que não existem.

### 3. A memória da conversa (`ConversationSession`)

Um detalhe surpreendente sobre LLMs: **eles não lembram de nada entre uma chamada e outra**. Cada telefonema para o consultor começa do zero. Quem lembra da conversa é o *nosso* programa — e ele reenvia o histórico inteiro a cada nova mensagem.

```python
class ConversationSession:
    """Guarda o histórico de conversa de um cliente."""

    def __init__(self, customer_id=None):
        # Cada cliente ganha um código único, tipo protocolo: CUST-78C546C3
        self.customer_id = customer_id or f"CUST-{uuid.uuid4().hex[:8].upper()}"
        # A lista de mensagens já nasce com as instruções permanentes dentro
        self.messages = [{"role": "system", "content": SYSTEM_ROLE}]

    def add_user_message(self, message):        # anota o que o cliente disse
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message):   # anota o que o bot respondeu
        self.messages.append({"role": "assistant", "content": message})
```

*Tradução:* uma `class` é um molde para criar objetos — aqui, o molde de uma "pasta de atendimento". Cada cliente novo ganha sua pasta com número de protocolo, e cada fala (do cliente ou do bot) vai sendo anexada nela. Quando o bot precisa responder, ele manda **a pasta inteira** para o LLM — é assim que o "consultor sem memória" parece lembrar da conversa.

> **💡 Analogia** — é como um call center em que cada ligação cai num atendente diferente, mas todos têm acesso à ficha completa das ligações anteriores. O atendente individual não lembra de você; a *ficha* lembra.

### 4. O classificador (`analyze_customer_query`)

Antes de responder, o sistema faz uma **primeira chamada ao LLM só para entender a mensagem** — e exige a resposta em formato de ficha (JSON), não texto livre:

```python
def analyze_customer_query(query):
    prompt = f"""
Analyze the following customer service query.

Return ONLY valid JSON with this exact structure:   # devolva SOMENTE JSON, neste formato exato:
{{
  "customer_sentiment": "positive | neutral | negative",   # sentimento do cliente
  "query_category": "technical | billing | return | ...",  # categoria (8 opções)
  "urgency_level": "low | medium | high",                  # urgência
  "mentioned_products": ["product names if any"],          # produtos citados
  "recommended_routing": "team or department name",        # para qual time encaminhar
  "reasoning_summary": "short explanation"                 # justificativa curta
}}

Customer query:
{query}                                                     # ← a mensagem real do cliente entra aqui
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,        # temperatura 0 = modo "burocrata": máxima consistência, zero criatividade
        messages=[...]
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)          # tenta ler a ficha JSON
    except json.JSONDecodeError:
        # Plano B: o LLM às vezes devolve a ficha embrulhada em ```json ... ```
        cleaned = content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
```

Dois detalhes importantes aqui:

- **`temperature=0`** — a "temperatura" controla a criatividade do LLM. Zero significa: responda sempre do jeito mais previsível. Para classificar, queremos um burocrata, não um poeta.
- **O plano B do `try/except`** — o LLM às vezes desobedece e devolve o JSON embrulhado em formatação extra. O código limpa manualmente. *Guarde esse incômodo:* a semana 2 existe em grande parte para eliminar essa gambiarra.

### 5. O redator (`generate_personalized_response`)

Com a análise em mãos, uma **segunda chamada ao LLM** gera a resposta ao cliente — desta vez com `temperature=0.4` (um pouco de naturalidade na escrita) e com instruções que usam a análise:

```python
response_instruction = f"""
Customer query analysis:
{json.dumps(analysis, indent=2)}          # ← a ficha da análise entra aqui

Generate a professional customer service response.
Requirements:
- If sentiment is negative, start with empathy.       # cliente irritado? comece com empatia
- If urgency is high, acknowledge priority...          # urgente? reconheça e dê passos imediatos
- Include specific information from company policy.    # cite a política real da loja
- End with the next best action.                        # termine com o próximo passo
"""
```

*Tradução:* o sistema usa a classificação para **calibrar o tom**. É a diferença entre um atendente que responde tudo com o mesmo script e um que percebe "essa pessoa está com pressa e chateada — primeiro acalmo, depois resolvo".

### 6. O orquestrador (`chatbot_reply`)

A função que junta tudo — o "gerente" que coordena analista e redator:

```python
def chatbot_reply(session, user_query):
    analysis = analyze_customer_query(user_query)                       # 1º telefonema: entender
    reply = generate_personalized_response(session, user_query, analysis)  # 2º telefonema: responder
    return {
        "customer_id": session.customer_id,
        "query": user_query,
        "analysis": analysis,
        "reply": reply,
    }
```

### 7. O arquivista (resumo + persistência)

Ao fim da conversa, uma **terceira chamada ao LLM** escreve um resumo, e o resultado vira um arquivo JSON padronizado em disco — um por conversa — mais um arquivo consolidado com todas:

```json
{
  "timestamp": "2026-05-14T18:53:14",
  "customer_id": "CUST-78C546C3",
  "conversation_summary": "Cliente relatou pedido não entregue...",
  "query_category": "general_information",
  "customer_sentiment": "negative",
  "urgency_level": "high",
  "resolution_status": "escalated",
  "follow_up_required": true
}
```

> **💡 Analogia** — é o fechamento do protocolo de atendimento: o que aconteceu, como o cliente saiu, se alguém precisa ligar de volta. Com milhares desses arquivos, a loja consegue medir: quais problemas mais aparecem? Quantos casos urgentes por semana?

## O modo simulação (Mock Mode)

Cada chamada ao LLM custa dinheiro. Para desenvolver e testar sem gastar, o notebook tem um **modo simulação**: uma chave (`MOCK_MODE = True`) que troca as três funções que chamam a OpenAI por versões locais baseadas em regras simples (procurar palavras-chave como "refund", "receipt", "install" na mensagem).

> **💡 Analogia** — é o simulador de voo do projeto: os pilotos treinam os procedimentos sem gastar combustível. As respostas do simulador são mais burras que as do LLM real, mas o *encanamento* (fluxo, arquivos, roteamento) é exercitado de verdade.

## Validação: os 10 casos de teste

O notebook termina rodando 10 mensagens típicas de clientes e conferindo a classificação — de *"o iPhone 15 tem em estoque?"* (informação de produto, urgência baixa) até *"EMERGÊNCIA: meu pedido nunca chegou e preciso do notebook amanhã"* (urgência alta → encaminhado ao time prioritário).

## Limitações que motivam a semana 2

| Incômodo da semana 1 | Consequência |
|----------------------|--------------|
| JSON lido "na unha", com gambiarra de limpeza | Se o LLM mudar o formato, o programa quebra silenciosamente |
| Roteamento espalhado pelo código | Difícil de manter quando as categorias mudam |
| Resumo gasta uma 3ª chamada de LLM | Custo desnecessário — o resumo podia ser montado com dados que já temos |
| Nenhuma visibilidade interna | Se algo sai errado, ninguém sabe em qual etapa foi |

A semana 2 ataca exatamente essa lista.

---

## Passo a passo: como o código foi construído

Esta seção percorre o notebook **na ordem em que ele foi escrito**, célula por célula. É a reconstituição do trabalho: o que se digita primeiro, o que vem depois, e por quê.

### Passo 1 — Preparar o terreno (importações e pastas)

Todo programa Python começa declarando as caixas de peças (bibliotecas) que vai usar:

```python
import os                      # conversar com o sistema operacional
import json                    # ler/escrever o formato JSON
import uuid                    # gerar códigos únicos (o protocolo do cliente)
from datetime import datetime  # carimbos de data e hora
from pathlib import Path       # manipular pastas e arquivos

from openai import OpenAI      # a biblioteca oficial da OpenAI

# Carrega o arquivo .env (onde mora a chave secreta da API)
from dotenv import load_dotenv
load_dotenv()

# Cria o cliente — ele lê a OPENAI_API_KEY do ambiente sozinho
client = OpenAI()

# Garante que a pasta de conversas salvas existe
DATA_DIR = Path("conversation_data")
DATA_DIR.mkdir(exist_ok=True)      # exist_ok=True: se já existir, não reclama
```

*Detalhe de segurança:* a chave da API **não aparece no código**. Ela vive num arquivo `.env` separado, que fica fora do controle de versão (o `.gitignore` o exclui). Quem clonar o projeto no GitHub não leva a chave junto.

### Passo 2 — Escrever a ficha da empresa (`COMPANY_CONTEXT`)

Um dicionário Python com os dados da loja (mostrado na seção anterior). Sem mistério técnico — o trabalho aqui foi **de conteúdo**: decidir o que um atendente precisa saber (horários, políticas, produtos, serviços, contato) e estruturar isso de forma organizada.

### Passo 3 — Escrever o roteiro do atendente (`SYSTEM_ROLE`)

O prompt de sistema, um texto de ~40 linhas. As decisões de escrita que importam:

1. **Persona primeiro** — "You are a professional customer service assistant for TechStore Plus".
2. **Regras de comportamento** — educação, empatia com clientes chateados, adaptação de tom.
3. **A regra anti-invenção** — "Do not invent unavailable company policies" + "Use the company context below as your source of truth". Estas duas linhas são a diferença entre um bot confiável e um bot que promete frete grátis que não existe.
4. **A ficha injetada** — `{json.dumps(COMPANY_CONTEXT, indent=2)}` cola a ficha inteira dentro do texto.
5. **O fluxo em 5 etapas numeradas** — cumprimentar → coletar dados → identificar o tipo → rotear → dar próximos passos. LLMs seguem bem listas numeradas.

### Passo 4 — Construir a pasta de atendimento (`ConversationSession`)

A classe de memória (mostrada na seção anterior). A ordem das decisões ao escrevê-la:

1. Cada sessão precisa de **identidade** → gerar `CUST-` + 8 caracteres aleatórios (`uuid`).
2. A lista de mensagens **nasce com o SYSTEM_ROLE dentro** → o roteiro sempre viaja com a conversa.
3. Dois métodos de anotação (`add_user_message`, `add_assistant_message`) → cada fala é registrada com seu papel (`role`), que é como a API da OpenAI distingue quem disse o quê.
4. Um método de leitura **sem o sistema** (`get_public_history`) → para exibir a conversa ao usuário ou resumi-la, as instruções internas não devem aparecer.

### Passo 5 — O primeiro telefonema: o analista (`analyze_customer_query`)

A anatomia de uma chamada à API da OpenAI, que se repete no projeto inteiro:

```python
response = client.chat.completions.create(   # "faça uma ligação"
    model="gpt-4o-mini",                     # com qual consultor falar
    temperature=0,                           # dial de criatividade (0 = burocrata)
    messages=[                               # o que dizer na ligação:
        {"role": "system", "content": "You are an expert...classifier..."},  # as instruções
        {"role": "user", "content": prompt}                                   # o pedido
    ]
)
content = response.choices[0].message.content   # a resposta vem aqui dentro
```

E o tratamento defensivo da resposta — a primeira lição de "LLMs desobedecem":

```python
try:
    return json.loads(content)                  # caminho feliz: o JSON veio limpo
except json.JSONDecodeError:                    # caminho triste: veio embrulhado
    cleaned = content.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)                  # desembrulha e tenta de novo
```

### Passo 6 — O segundo telefonema: o redator (`generate_personalized_response`)

Três decisões de construção nesta função:

1. **A análise entra no prompt** — o redator recebe a ficha do analista (`json.dumps(analysis)`) e instruções condicionais ("SE o sentimento é negativo, comece com empatia; SE a urgência é alta, reconheça prioridade").
2. **O histórico inteiro vai junto** — `messages = session.messages + [instrução]`: o redator vê a conversa completa, por isso não repete perguntas.
3. **`temperature=0.4`** — um dedo de naturalidade. Textos para humanos não podem soar robóticos; classificações para máquinas não podem variar. Cada chamada tem seu dial.

### Passo 7 — O gerente (`chatbot_reply`)

Quatro linhas que definem a arquitetura: analisar → responder → devolver tudo num pacote. A elegância está no que ela **não** faz: nenhuma lógica própria, só coordenação. Funções pequenas com um papel claro cada — o princípio que o projeto carrega até o fim.

### Passo 8 — O terceiro telefonema: o arquivista (`generate_conversation_summary`)

```python
summary_prompt = f"""
Summarize the following customer service conversation in one concise paragraph.

Conversation:
{json.dumps(public_history, indent=2)}          # o histórico SEM o system role
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.2,                             # quase burocrata: resumo fiel, sem floreio
    messages=[...]
)
concise_summary = response.choices[0].message.content

# O resumo do LLM é UM CAMPO da ficha final — o resto vem da análise já feita:
conversation_json = {
    "timestamp": datetime.now().isoformat(timespec="seconds"),
    "customer_id": session.customer_id,
    "conversation_summary": concise_summary,                       # ← único campo do LLM
    "query_category": latest_analysis.get("query_category", "general_information"),
    "customer_sentiment": latest_analysis.get("customer_sentiment", "neutral"),
    "urgency_level": latest_analysis.get("urgency_level", "low"),
    ...
    "resolution_status": resolution_status,     # informado por quem encerra o caso
    "follow_up_required": follow_up_required,
}
```

*Repare nos `.get(campo, padrão)`:* se a análise vier sem algum campo, o código usa um valor padrão em vez de quebrar. Programação defensiva de novo.

### Passo 9 — Salvar e consolidar

```python
def consolidate_conversations(output_file="consolidated_conversations.json"):
    all_conversations = []
    # Varre a pasta atrás de TODOS os arquivos conversation_*.json
    for file_path in DATA_DIR.glob("conversation_*.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            all_conversations.append(json.load(file))

    consolidated_data = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_conversations": len(all_conversations),   # contagem automática
        "conversations": all_conversations,               # todas dentro
    }
    # ensure_ascii=False: preserva acentos legíveis no arquivo
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(consolidated_data, file, indent=2, ensure_ascii=False)
```

O padrão `with open(...)` garante que o arquivo é fechado mesmo se algo der errado no meio — o equivalente a "feche a gaveta ao terminar, aconteça o que acontecer".

### Passo 10 — O modo simulação (a célula MOCK)

A célula mais extensa do notebook (~270 linhas) reescreve os três "telefonemas" como funções locais baseadas em regras. Dois exemplos do miolo:

```python
def mock_extract_products(query):
    """Extrai produtos conhecidos por palavra-chave — substitui a IA no modo simulação."""
    product_keywords = {
        "iphone 15": "iPhone 15",
        "gaming headphones": "Gaming Headphones",
        "macbook pro": "MacBook Pro",
        ...
    }
    lower_query = query.lower()                  # tudo minúsculo para comparar
    products = []
    for keyword, product_name in product_keywords.items():
        if keyword in lower_query and product_name not in products:
            products.append(product_name)        # achou? anota (sem duplicar)
    return products

def mock_extract_information(query):
    """Extrai nº de pedido, valores e datas com expressões regulares."""
    order_match  = re.search(r"#?[A-Z]{3}-\d{4}-\d{3}", query)   # padrão TEC-2024-001
    amount_match = re.search(r"\$\s?\d+(?:\.\d{2})?", query)     # padrão $800 ou $59.99
    ...
```

*Sobre a linha `r"#?[A-Z]{3}-\d{4}-\d{3}"`:* é uma **expressão regular** — uma linguagem de padrões de texto. Lê-se: "um `#` opcional, 3 letras maiúsculas, hífen, 4 dígitos, hífen, 3 dígitos". É assim que o modo simulação encontra `#TEC-2024-001` no meio da frase sem nenhuma IA.

Com `MOCK_MODE = True`, as funções falsas **substituem** as verdadeiras (mesmos nomes, mesmas entradas e saídas) — o resto do notebook nem percebe a troca. Esse é o conceito de **interface estável**: peças intercambiáveis porque o encaixe é idêntico.

### Passo 11 — Rodar de verdade (demonstração + 10 testes)

A célula de demonstração exercita o fluxo completo com o caso mais dramático:

```python
session = ConversationSession()
user_query = "This is an emergency! My order #TEC-2024-001 never arrived and I need that laptop for work tomorrow!"

result = chatbot_reply(session, user_query)          # analisa + responde
summary = generate_conversation_summary(              # resume + estrutura
    session=session,
    latest_analysis=result["analysis"],
    resolution_status="escalated",                    # urgência alta → escalado
    actions_taken=[
        "Acknowledged urgent delivery issue",
        "Requested confirmation of delivery address",
        "Routed case to priority support",
    ],
    follow_up_required=True,
)
saved_file = save_conversation_json(summary)          # grava em disco
```

E a bateria final roda as **10 mensagens de teste** (uma por categoria/urgência) num laço, imprimindo a classificação de cada uma para conferência manual — o embrião dos testes automatizados que as semanas seguintes formalizam.
