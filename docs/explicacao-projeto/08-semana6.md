# Capítulo 7 · Semana 6 — A biblioteca à prova de produção (desafio M2)

**Arquivo:** `Week6_Stop3_Production_RAG.ipynb` (código no repositório `c03-t05-bruno-pieri-m2-challenge`) · **Entrega avaliada do módulo 2**

## O que foi construído

A semana 6 é a entrega final do módulo 2 — e leva a biblioteca da semana 5 a nível de produção, adicionando três capacidades que sistemas RAG "de aula" não têm:

1. **Graph RAG** — um mapa de conexões entre entidades, para responder perguntas que **cruzam vários documentos**.
2. **Guardrails anti-alucinação** — um verificador que **confere cada afirmação** da resposta antes de entregá-la ao cliente.
3. **Busca multimodal** — além de texto, o sistema busca em **tabelas** (planilhas de especificações) e **imagens** (fotos e diagramas de produto).

## Componente 1 — Graph RAG: o mapa de conexões

### O problema que a busca vetorial não resolve

A busca por significado encontra trechos parecidos com a pergunta. Mas algumas perguntas exigem **seguir um caminho entre fatos que moram em documentos diferentes**: *"quais produtos são cobertos pela garantia estendida?"* — a resposta exige juntar o catálogo (produto A existe) com a política (o plano premium cobre a categoria X) com a tabela de planos (produto A está na categoria X). Nenhum trecho isolado contém a resposta inteira.

### A solução: extrair um grafo de conhecimento

Durante o preparo da biblioteca, um LLM lê os documentos e extrai **triplas** — fatos mínimos no formato *sujeito → relação → objeto*:

```text
  Laptop Pro X1  --tem_garantia-->     Premium Protection Plan
  Laptop Pro X1  --tem_memoria-->      16GB RAM
  Premium Plan   --cobre-->            danos acidentais
  Premium Plan   --dura-->             24 meses
```

Cada tripla guarda também **de onde veio** (documento fonte + a frase exata que a sustenta). As triplas viram um **grafo** — uma rede de bolinhas (entidades) e setas (relações):

```python
kg = TechStoreKnowledgeGraph()
kg.extract_and_build(docs)       # LLM lê o corpus e extrai as triplas
print(f"Graph: {kg.graph.number_of_nodes()} nodes, {kg.graph.number_of_edges()} edges")

# Na hora da pergunta: partir de uma entidade e caminhar 1-2 "pulos" pelas setas
snippets = kg.query_subgraph(["Laptop Pro X1"], hops=2)
# → devolve a vizinhança: garantia do X1 → o que essa garantia cobre → por quanto tempo
```

> **💡 Analogia** — é o quadro de investigação dos filmes policiais: fotos ligadas por barbantes. Perguntas simples se resolvem olhando uma foto ("qual o prazo de troca?"). Perguntas de investigação se resolvem **seguindo os barbantes**: da foto do laptop, dois barbantes adiante, chega-se à cobertura de danos acidentais. O `hops=2` significa "siga até dois barbantes de distância".

## Componente 2 — Guardrails: o revisor que barra invenções

A peça mais crítica para pôr um RAG na frente de clientes. Mesmo com contexto bom, o LLM pode **alucinar** — misturar o que leu com o que "acha". A semana 6 monta uma linha de defesa em três etapas:

```text
[1. ESCRITOR]     gera a resposta com uma citação [fonte] no fim de CADA frase
       ↓
[2. VERIFICADOR]  quebra a resposta em afirmações atômicas e confere cada uma
                  contra o trecho citado: o texto realmente sustenta isso?
       ↓
[3. PORTÃO]       decide o destino da resposta com base nas taxas de sustentação
```

```python
raw = build_cited_answer(question, top_docs)     # escritor: resposta com citações
result = verify_answer(raw, top_docs)            # verificador + portão

print(result.decision)             # a decisão do portão
print(result.claim_support_rate)   # % das afirmações confirmadas pelo texto
print(result.contradiction_rate)   # % que CONTRADIZ o texto (gravíssimo)
```

O portão tem **seis saídas possíveis**, em ordem decrescente de confiança:

| Decisão | Quando | O cliente recebe |
|---------|--------|------------------|
| `answer` | Tudo confirmado | A resposta normal |
| `answer_with_disclaimer` | Quase tudo confirmado | A resposta + um aviso de incerteza |
| `extractive` | Confiança baixa na redação | Só os trechos literais dos documentos, sem parafrasear |
| `no_answer` | O acervo não cobre o assunto | "Não encontrei isso na nossa documentação" |
| `ask_clarify` | Pergunta ambígua | Um pedido de esclarecimento |
| `refuse` | Pergunta inadequada | Recusa educada |

O notebook demonstra o portão funcionando com uma pergunta fora do escopo — *"qual é a capital da França?"* — que corretamente cai em `no_answer`: o sistema **prefere admitir ignorância a inventar**.

> **💡 Analogia** — é o processo editorial de uma revista séria: o repórter (escritor) só publica frase com fonte; o **checador de fatos** (verificador) confere cada afirmação contra a fonte citada; e o editor (portão) decide — publica, publica com ressalva, corta para as aspas literais, ou não publica. Nenhuma frase chega ao leitor sem passar pelos três.

## Componente 3 — Multimodal: texto + tabelas + imagens

Uma loja real tem informação em três formatos, e cada um pede um tratamento:

| Modalidade | Acervo | Como é buscado | Etiqueta de citação |
|------------|--------|----------------|---------------------|
| **Texto** | Manuais, políticas | Estante vetorial (MMR + re-rank, semana 5) | `[arquivo.txt]` |
| **Tabelas** | CSVs de especificações | Cada linha vira um documento buscável | `[TB:...]` |
| **Imagens** | Fotos e diagramas | Busca pela **legenda** descritiva de cada imagem | `[I:...]` |

```python
# Tabela: "quanto de RAM tem o Laptop Pro X1?" acha a LINHA certa do CSV
for doc in tr.retrieve("How much RAM does the Laptop Pro X1 have?"):
    print(doc.metadata['table_citation'], doc.page_content)

# Imagem: busca pela legenda descritiva
for doc in ir.retrieve("warranty tiers comparison figure"):
    print(doc.metadata['image_citation'], doc.page_content[:100])
```

E a **fusão tardia** (*late fusion*) junta tudo: cada modalidade é consultada **independentemente**, e os resultados são mesclados removendo duplicatas:

```python
def late_fusion_retrieve(question, vs, tr, ir, ...):
    text_docs  = rerank(question, retriever.invoke(question))   # modalidade texto
    table_docs = tr.retrieve(question, k=3)                      # modalidade tabela
    image_docs = ir.retrieve(question, k=2)                      # modalidade imagem

    # mescla, deduplicando pela fonte
    merged, seen = [], set()
    for doc in text_docs + table_docs + image_docs:
        if doc.metadata["source"] not in seen:
            seen.add(doc.metadata["source"])
            merged.append(doc)
    return merged
```

> **💡 Analogia** — "tardia" porque cada especialista pesquisa **na sua própria seção** primeiro (o de texto na biblioteca, o de dados nas planilhas, o de imagens no acervo visual) e só **depois** as descobertas são postas na mesma mesa. A alternativa (converter tudo para um formato único antes) perderia a estrutura da tabela e o conteúdo visual.

## A prova de fogo: 10 consultas difíceis + comparação com a semana 5

A entrega é validada com um conjunto de 10 perguntas **desenhadas para forçar cada capacidade nova**:

- *"Resuma a política de devolução citando pelo menos duas regras distintas"* (multi-citação)
- *"Quais produtos aparecem tanto na tabela de specs quanto no plano premium?"* (**cruzamento entre documentos** — Graph RAG)
- *"Quanto de RAM e armazenamento tem o Laptop Pro X1?"* (aterramento numérico — tabela)
- *"Identifique a imagem que mostra o Laptop Pro X1 e descreva o que ela mostra"* (imagem)
- *"A política permite reembolso após 30 dias?"* (armadilha temporal — a resposta certa é "não, o prazo é 7 dias")

E o rigor científico: as mesmas 10 perguntas rodam **também no pipeline da semana 5** (sem grafo, sem guardrails, sem multimodal), gerando um relatório comparativo com o que melhorou e — honestamente — o que regrediu (guardrails deixam o sistema mais conservador: ele responde "não sei" mais vezes, o que é o comportamento desejado em produção, mas derruba métricas ingênuas de "taxa de resposta").

## O que o módulo 2 entregou, em uma frase

Uma biblioteca de conhecimento que busca por significado **e** por conexões **e** em três formatos, responde só com base em evidência citável, **confere cada frase antes de entregar**, e prefere admitir ignorância a inventar — tudo medido contra a versão anterior.

O módulo 3 muda o foco: das *fontes de conhecimento* para a *forma de raciocinar* — fluxos com várias etapas, especialistas e supervisão.

---

## Passo a passo: como o código foi construído

O código do Stop 3 se distribui em três pastas novas do repositório M2 — `src/graph/`, `src/guardrails/`, `src/multimodal/` — construídas nessa ordem.

### Passo 1 — O grafo de conhecimento (`graph/knowledge_graph.py`)

**A extração de triplas** usa o LLM com saída estruturada, mas com um filtro de qualidade:

```python
def extract_and_build(self, documents):
    """Extrai triplas (sujeito, relação, objeto, citação) de cada documento
    via ChatOpenAI estruturado.

    Só entram no grafo triplas cuja relação está na DEFAULT_RELATION_ALLOWLIST —
    triplas de baixa confiança ou ruidosas são descartadas silenciosamente."""
```

*A allow-list de relações é o controle de qualidade:* o LLM extrai fatos livremente, mas só relações **conhecidas e úteis** (`tem_garantia`, `cobre`, `dura`...) entram no mapa. Sem isso, o grafo viraria um emaranhado de relações inventadas e inconsistentes ("está_associado_a", "relaciona-se_com"...) que ninguém consegue percorrer com confiança.

**A consulta por vizinhança** — uma busca em largura com raio limitado:

```python
def query_subgraph(self, seed_entities, hops=DEFAULT_HOPS, relation_allowlist=None):
    """A partir das entidades-semente, percorre o grafo até `hops` pulos.
    Cada resultado devolve:
        subject / relation / object   — o fato
        source_id                     — o ARQUIVO de onde o fato veio
        quote                         — a FRASE LITERAL que o sustenta
        hop                           — a distância da semente (1 ou 2)
    """
```

*O detalhe que muda tudo:* cada fato do grafo carrega **a frase literal de origem** (`quote`) e **o arquivo** (`source_id`). Quando o Graph RAG contribui para uma resposta, a contribuição é tão citável quanto um trecho da estante vetorial — o padrão de auditabilidade do projeto não abre exceções.

### Passo 2 — O escritor com citação obrigatória (`guardrails/writer.py`)

```python
def build_cited_answer(question, context_docs):
    """Gera a resposta com uma citação [arquivo_fonte] no FIM DE CADA FRASE.

    WHY CITATION BINDING?
        As citações servem a dois senhores: o usuário confere cada afirmação
        na fonte; e o verifier.py consegue checar cada claim olhando SÓ a
        fonte citada — O(claims) — em vez de comparar cada claim contra
        todos os chunks — O(claims × chunks)."""
```

O prompt do escritor impõe quatro regras: (1) usar SÓ o contexto; (2) terminar cada frase com `[arquivo]`; (3) se a resposta não estiver no contexto, dizer exatamente *"I don't have that information in our documentation."*; (4) nunca inventar números de modelo, preços ou datas.

*Repare no argumento de eficiência do docstring:* a citação por frase não é só transparência — ela **barateia a verificação**. O verificador sabe exatamente onde conferir cada afirmação, em vez de procurar em tudo. Design em que segurança e desempenho se reforçam.

### Passo 3 — O verificador e o portão (`guardrails/verifier.py`)

O procedimento em três atos:

```python
def verify_answer(answer, context):
    # 1. DECOMPOR: um LLM quebra a resposta em "claims atômicos"
    #    (uma afirmação factual por item, sem frases compostas)
    # 2. CONFERIR: para cada claim, outro prompt de "entailment" pergunta:
    #    o trecho citado SUSTENTA / CONTRADIZ / NÃO COBRE esta afirmação?
    # 3. DECIDIR: as taxas alimentam o portão
```

E o portão, com os limiares **documentados e justificados** no código:

```python
SUPPORT_RATE_THRESHOLD = 0.85

# A lógica do portão (do docstring do módulo):
#   suporte >= 0.85                        → decision="answer"
#   suporte < 0.85 E contradições == 0     → decision="answer_with_disclaimer"
#   contradições > 0                       → decision="extractive"
#                                            (devolve o trecho LITERAL mais relevante)
#   sem evidência (contexto vazio/unknown) → decision="no_answer"

# WHY THESE THRESHOLDS?
#   0.85: tolera inferências contextuais menores, mas barra respostas onde
#         menos de 85% dos claims são verificáveis.
#   contradição > 0: UMA única contradição já dispara o fallback extrativo,
#         porque uma resposta que contradiz a fonte é ATIVAMENTE enganosa —
#         pior que uma resposta meramente não-verificada.
```

*A hierarquia moral embutida:* não-verificado ganha um aviso; **contraditório perde o direito de parafrasear** — o cliente recebe o texto literal do documento. O sistema distingue "não tenho certeza" de "estou dizendo o contrário da fonte", e trata o segundo como muito mais grave.

### Passo 4 — Os retrievers multimodais (`multimodal/`)

**Tabelas (`table_retriever.py`)** — a sacada é a granularidade: cada **linha** do CSV vira um documento buscável independente ("Laptop Pro X1 | 16GB RAM | 512GB SSD" é um documento; a linha do outro laptop é outro). A pergunta "quanto de RAM tem o X1?" encontra exatamente a linha certa, com citação `[TB:laptop_specs:linha]`.

**Imagens (`image_retriever.py`)** — busca pela **legenda**: cada imagem do acervo tem uma descrição textual detalhada, e é a legenda que entra no índice. A pergunta "figura comparando os planos de garantia" casa com a legenda do diagrama certo, com citação `[I:nome_da_imagem]`. (Buscar pelo conteúdo visual em si exigiria embeddings de imagem — a legenda é a ponte pragmática.)

**A fusão tardia** (mostrada na seção anterior) junta os três com dois cuidados: cada modalidade falha **isoladamente** (um `try/except` por modalidade — se o índice de imagens quebrar, texto e tabelas continuam), e a deduplicação por fonte garante que a mesma evidência não entra duas vezes.

### Passo 5 — A validação comparativa (o notebook)

A construção do experimento final tem um detalhe metodológico digno de nota: o notebook **reimplementa o pipeline da semana 5 em miniatura** (`stop2_answer` — MMR + rerank + LLM direto, sem guardrails, sem grafo, sem multimodal) para rodar as mesmas 10 perguntas nos dois sistemas **nas mesmas condições**:

```python
def stop2_answer(question, vs):
    """Pipeline Stop 2 mínimo: MMR + rerank + LLM direto (sem guardrails)."""
    retriever = get_mmr_retriever(vs)
    mmr_docs = retriever.invoke(question)
    top_docs = rerank(question, mmr_docs)
    context = "\n---\n".join(d.page_content for d in top_docs)
    prompt = f"Answer the question using the context below.\n\nContext:\n{context}\n\nQuestion: {question}"
    ...
```

O relatório final compara os dois lado a lado e o notebook fecha com uma análise honesta em três seções: **o que melhorou** (cobertura de perguntas cruzadas, aterramento numérico, zero contradições não-sinalizadas), **limitações conhecidas** (o sistema ficou mais conservador — mais "não sei"; latência maior pelas checagens) e **próximos passos**. Entregar os trade-offs junto com as vitórias é o que diferencia um relatório de engenharia de um material de marketing.
