# Capítulo 6 · Semana 5 — Afinando a biblioteca (otimização do RAG)

**Arquivo:** `Week5_RAG_Optimization.ipynb` (usando o código do repositório `c03-t05-bruno-pieri-m2-challenge`)

## O que foi construído

A biblioteca da semana 4 funciona, mas tem três vícios de biblioteca nova:

1. **Traz 4 cópias do mesmo assunto** — se a pergunta é sobre garantia, a busca por similaridade tende a devolver 4 trechos quase iguais da mesma seção, desperdiçando espaço de contexto.
2. **A ordem nem sempre é a melhor** — o trecho *realmente* certo às vezes vem em 3º ou 4º lugar (ou fica de fora).
3. **Ninguém mediu nada** — "parece melhor" não é critério de engenharia.

A semana 5 ataca os três com quatro componentes: **MMR**, **re-ranking com cross-encoder**, um **experimento de tamanho de pedaço**, e **métricas objetivas** comparando antes × depois.

## Componente 1 — MMR: o bibliotecário que evita repetição

**MMR** (*Maximal Marginal Relevance*) muda o critério da busca: em vez de "os 4 trechos mais parecidos com a pergunta", passa a ser "os trechos mais parecidos com a pergunta **que sejam diferentes entre si**".

> **💡 Analogia** — você pede ao bibliotecário material sobre "garantia". O bibliotecário ingênuo traz 4 fotocópias de páginas vizinhas do mesmo capítulo. O bibliotecário MMR traz: 1 página do capítulo de garantia, 1 da política de garantia estendida, 1 do procedimento de acionamento e 1 da tabela de prazos — **cobertura**, não redundância.

O notebook prova isso com uma consulta propositalmente ampla:

```python
broad_query = "TechStore Plus products support warranty return policy"
mmr_docs = retriever.invoke(broad_query)

# Verificação: os resultados vêm de arquivos DISTINTOS?
unique_sources = len({d.metadata['source'] for d in mmr_docs})
print("✓ Diversity check passed" if unique_sources >= 3 else "⚠ Low diversity")
```

*Como o MMR funciona por dentro:* ele primeiro pesca um lote maior de candidatos (ex.: 20), depois monta o resultado um a um — cada escolha pontua **relevância para a pergunta** menos **semelhança com o que já foi escolhido**. Ganha quem agrega informação nova.

## Componente 2 — Re-ranking com cross-encoder: a segunda opinião

A busca vetorial é rápida mas aproximada — ela compara "endereços de significado" calculados **separadamente** para pergunta e documento. O **cross-encoder** é um modelo mais lento e mais preciso que lê **pergunta e trecho juntos, lado a lado**, e dá uma nota de relevância real para o par.

A arquitetura em dois estágios usa cada um no que é bom:

```text
pergunta do cliente
   ↓
[Estágio 1 — MMR]            rápido, pesca 6 candidatos diversos na estante inteira
   ↓
[Estágio 2 — Cross-encoder]  lento porém preciso, lê os 6 com atenção e reordena
   ↓
top-3 vão para o LLM         (contexto menor E melhor)
```

```python
mmr_candidates = retriever.invoke(rerank_query)   # estágio 1: 6 candidatos
top_docs = rerank(rerank_query, mmr_candidates)   # estágio 2: reordena, fica com top-3

# Cada trecho sai com sua nota de relevância:
#   [1] score=+5.1042 | policy_extended_warranty.txt
#   [2] score=+3.8871 | policy_warranty.txt
#   [3] score=-1.2094 | product_catalog.txt
```

> **💡 Analogia** — é um processo seletivo em duas fases: a triagem de currículos (rápida, olha palavras-chave, elimina 95%) e a entrevista presencial (lenta, mas avalia de verdade — só para os finalistas). Entrevistar todo mundo seria inviável; contratar só pela triagem seria arriscado. A combinação é barata **e** precisa.

Bônus: o contexto enviado ao LLM **encolhe** (de 6 para 3 trechos) e ao mesmo tempo **melhora** — menos tokens pagos, resposta mais focada.

## Componente 3 — O experimento do tamanho do pedaço

Qual o tamanho ideal de cada pedaço da biblioteca? Em vez de chutar, a semana 5 testou três configurações com as mesmas perguntas:

| Configuração | Relevância (1-5) | Qualidade (1-5) | O que se observou |
|--------------|:---:|:---:|-------------------|
| 250 caracteres | 3 | 3 | **Fragmentação** — cláusula de garantia cortada no meio da frase; o LLM reconstrói regras parciais |
| **500 caracteres ← escolhido** | **5** | **5** | **Melhor equilíbrio**: uma seção de política por pedaço, redundância mínima |
| 1000 caracteres | 4 | 4 | Um pedaço longo domina a busca; a diversidade de contexto cai |

*A lição de engenharia:* pedaço pequeno demais **quebra o sentido**; grande demais **dilui a busca**. O meio-termo (500) venceu — e agora essa escolha tem **evidência**, não opinião.

## Componente 4 — As métricas: Precision@k e MRR

A parte mais importante da semana: **medir**. Duas métricas clássicas de busca, avaliadas sobre um conjunto de perguntas com gabarito (para cada pergunta, sabemos quais documentos são os certos):

- **Precision@k** ("precisão nos k primeiros"): dos k trechos que a busca trouxe, quantos eram certos? Se trouxe 3 e acertou 2, P@3 = 0,67.
- **MRR** (*Mean Reciprocal Rank*, "posição média do primeiro acerto"): o primeiro resultado certo veio em que posição? 1º lugar vale 1,0; 2º vale 0,5; 3º vale 0,33... Mede se **o melhor trecho chega no topo**.

```python
# As funções são testadas com casos de gabarito conhecido antes de usar:
p3 = precision_at_k(["a", "b", "c"], relevant=["a", "c"], k=3)   # = 2/3 ✓
m  = mrr(["b", "a", "c"], relevant=["a"])                        # = 0.5 ✓ (acerto na 2ª posição)
```

E então o confronto — o mesmo conjunto de perguntas, os dois pipelines:

```python
# Baseline (semana 4): busca por similaridade simples, k=4
# Otimizado (semana 5): MMR pesca 6 → cross-encoder fica com top-3

print(f"{'Pipeline':<35} {'P@3':>6} {'P@6':>6} {'MRR':>6}")
print(f"Baseline (similarity, k=4)          ...")
print(f"Optimised (MMR k=6 + rerank top-3)  ...")
# Requisito do Stop 2: MRR otimizado ≥ MRR baseline → ✓ PASSED
```

O notebook fecha com a tabela comparativa completa e o detalhamento pergunta a pergunta — provando com números que a otimização melhorou (ou pelo menos não piorou) cada métrica.

## O toque final: citação obrigatória por afirmação

O prompt do pipeline otimizado ficou ainda mais exigente que o da semana 4 — agora **cada afirmação factual** precisa citar o arquivo de origem:

```python
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a TechStore Plus customer support assistant. "
     "Answer the question using ONLY the provided context. "
     "End every factual claim with the source filename in brackets, "
     "e.g. [policy_return_policy.txt]."),          # ← cada frase factual sai com fonte!
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])
```

*Resultado:* respostas do tipo *"A garantia padrão cobre 12 meses [policy_warranty.txt]. A estendida adiciona 1 ano [policy_extended_warranty.txt]."* — auditáveis frase a frase.

## Resumo da semana 5

| Vício da semana 4 | Remédio da semana 5 |
|--------------------|---------------------|
| 4 trechos repetidos do mesmo assunto | MMR (relevância + diversidade) |
| O melhor trecho nem sempre no topo | Cross-encoder re-ranking em 2 estágios |
| Tamanho de pedaço escolhido no chute | Experimento 250/500/1000 com evidência |
| "Parece melhor" | Precision@k e MRR, baseline × otimizado, com gabarito |
| Fontes só no rodapé | Citação por afirmação factual |

A biblioteca agora é rápida, diversa, precisa e **medida**. Falta o último degrau: deixá-la à prova de produção — com trava contra respostas inventadas, capacidade de responder perguntas que cruzam vários documentos, e busca também em imagens. É a semana 6.

---

## Passo a passo: como o código foi construído

O código da semana 5 mora no repositório do desafio M2 (`c03-t05-bruno-pieri-m2-challenge/src/pipeline/`), em três módulos: `vectorstore.py` (ganhou o MMR), `reranker.py` (novo) e `metrics.py` (novo). O notebook `Week5_RAG_Optimization.ipynb` os demonstra em sequência.

### Passo 1 — O retriever MMR (`vectorstore.py::get_mmr_retriever`)

O código não só implementa — **documenta a matemática da decisão** no próprio docstring:

```python
def get_mmr_retriever(vectorstore):
    """WHY MMR (not simple similarity)?
        Similarity search returns the top-k closest vectors. In a corpus where
        warranty terms appear in both policy_warranty_terms.txt and each
        product manual, all top-k results may be warranty chunks — the LLM
        receives redundant context and misses more specific product information.

        MMR selects the first document by pure similarity, then each subsequent
        document by the trade-off:
            lambda * sim(d, q) - (1 - lambda) * max_sim(d, selected)
        With lambda_mult=0.85, relevance is weighted more heavily than diversity
        while still reducing duplicate chunks. With fetch_k=20 >> k=6, MMR has
        enough candidates to find diverse results."""
```

Traduzindo a fórmula para português: *a nota de cada candidato = 85% de "quão relevante para a pergunta" − 15% de "quão parecido com o que eu já escolhi"*. Os três números calibrados:

| Parâmetro | Valor | Significado |
|-----------|:---:|-------------|
| `fetch_k` | 20 | O lote inicial pescado por similaridade pura (matéria-prima para diversificar) |
| `k` | 6 | Quantos sobrevivem à seleção MMR |
| `lambda_mult` | 0.85 | O dial relevância ↔ diversidade (1.0 = só relevância; 0 = só diversidade) |

### Passo 2 — O re-ranker (`reranker.py`)

**A escolha do modelo**, documentada como constante:

```python
_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
# Treinado no MS MARCO (pares pergunta-resposta, similar a suporte ao cliente).
# Rápido (6 camadas). Para mais precisão ao custo de latência:
# cross-encoder/ms-marco-electra-base.

RERANK_TOP_N = 3     # só 3 trechos chegam ao LLM — contexto enxuto e preciso

# Singleton de módulo: o modelo é carregado UMA vez, não a cada chamada
_cross_encoder = None
```

*O padrão singleton:* carregar um modelo de rede neural demora segundos; a variável de módulo `_cross_encoder = None` + o `if _cross_encoder is None` dentro da função garantem que o carregamento acontece na primeira chamada e nunca mais. (É o mesmo truque do `@lru_cache` do desafio M1 — outra grafia, mesma ideia.)

**A função `rerank`** — com validação de entrada e rastro nos metadados:

```python
def rerank(query, docs, top_n=RERANK_TOP_N):
    if not docs:
        raise ValueError("docs must be non-empty")     # falha clara, não silêncio
    if top_n < 1:
        raise ValueError("top_n must be >= 1")

    # O cross-encoder pontua cada par (pergunta, trecho) LADO A LADO
    pairs = [(query, doc.page_content) for doc in docs]
    scores = _cross_encoder.predict(pairs)

    # Ordena por nota decrescente e fica com os top_n
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)[:top_n]

    # Cada trecho sai com a nota gravada nos metadados — transparência p/ depurar
    for doc, score in ranked:
        doc.metadata["rerank_score"] = float(score)
    return [doc for doc, _ in ranked]
```

*O contrato não muda:* entra lista de `Document`, sai lista de `Document` (menor e melhor). O resto do pipeline não precisa saber que o re-ranking existe — a peça é encaixável e removível.

### Passo 3 — As métricas (`metrics.py`)

As duas funções centrais são pequenas o bastante para mostrar inteiras:

```python
def precision_at_k(retrieved, relevant, k):
    """Dos top-k recuperados, que fração está no gabarito?"""
    if k <= 0:
        raise ValueError("k must be >= 1")
    hits = set(retrieved[:k]) & set(relevant)     # & = interseção de conjuntos
    return len(hits) / k
    # Exemplo: retrieved=[a,b,c], relevant=[a,c], k=3 → |{a,c}|/3 = 0.667

def mrr(retrieved, relevant):
    """1 / posição do primeiro acerto. Sem acerto → 0."""
    relevant_set = set(relevant)
    for i, doc_id in enumerate(retrieved):
        if doc_id in relevant_set:
            return 1.0 / (i + 1)      # 1º lugar → 1.0; 2º → 0.5; 3º → 0.33...
    return 0.0
```

O módulo traz também `EVAL_SET` (o conjunto de perguntas com gabarito — para cada pergunta, a lista dos arquivos que a respondem) e `evaluate_retriever` (roda qualquer retriever sobre o conjunto inteiro e agrega as médias).

### Passo 4 — O notebook amarra tudo (na ordem do método científico)

1. **Setup** — ancora o diretório no repositório do desafio e carrega a estante existente (ou constrói, se for a primeira vez).
2. **Demonstração do MMR** — a consulta ampla de teste + a checagem de diversidade (`unique_sources >= 3`).
3. **Demonstração do re-ranker** — antes × depois, com as notas visíveis.
4. **Experimento de chunk** — a tabela 250/500/1000 com observações qualitativas.
5. **Auto-teste das métricas** — antes de medir os pipelines, o notebook confere as próprias réguas com casos de gabarito conhecido:

```python
assert abs(precision_at_k(["a","b","c"], ["a","c"], k=3) - 2/3) < 1e-9
assert mrr(["b","a","c"], ["a"]) == 0.5
```

*Isso é meta-rigor:* medir com régua não aferida é pior que não medir. Três `assert` de uma linha eliminam a dúvida.

6. **O confronto final** — os dois pipelines definidos como funções intercambiáveis, avaliados sobre o mesmo `EVAL_SET`:

```python
# Baseline: a semana 4 pura
baseline_retriever = vs.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Otimizado: o pipeline novo em uma função de duas linhas
def optimised_retriever_fn(query):
    mmr_docs = retriever.invoke(query)     # MMR pesca 6 diversos
    return rerank(query, mmr_docs)         # cross-encoder fica com top-3

# Mesma régua nos dois:
baseline_results,  baseline_agg  = evaluate_retriever(baseline_retriever.invoke, EVAL_SET)
optimised_results, optimised_agg = evaluate_retriever(optimised_retriever_fn,    EVAL_SET)
```

7. **Tabela comparativa + veredito automatizado** — a última célula imprime P@3, P@6 e MRR lado a lado, calcula os deltas, e confere o requisito de aprovação do Stop 2 (`MRR otimizado ≥ MRR baseline`) imprimindo `✓ PASSED` ou `✗ FAILED`. O critério de sucesso não é uma opinião no relatório — é uma linha de código que qualquer pessoa pode re-executar.
