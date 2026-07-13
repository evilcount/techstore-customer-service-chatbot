# PARTE II — Módulo 2: O Atendente que Estuda (RAG)

---

# Capítulo 5 · Semana 4 — Ensinando o atendente a consultar documentos

**Arquivos:** `Week4_RAG_TechStore.ipynb`, `Week4_RAG_Python_Library.ipynb`, pasta `src/rag/`

## O problema que abre o módulo 2

O atendente do módulo 1 sabe **o que está no prompt** — aquela ficha da empresa com meia dúzia de políticas. Mas uma empresa real tem manuais de produto, tabelas de garantia, guias de solução de problemas, políticas com letras miúdas... **centenas de páginas**. Não cabe tudo no prompt (limite físico), e mesmo se coubesse, custaria uma fortuna reenviar tudo a cada mensagem.

A resposta da indústria para isso tem nome: **RAG** — *Retrieval-Augmented Generation*, ou "geração aumentada por busca". A ideia em uma frase:

> Em vez de fazer o atendente **decorar** a biblioteca inteira, ensinamos ele a **consultar** a biblioteca — achar as 3 ou 4 páginas relevantes para a pergunta e responder **só com base nelas**.

> **💡 Analogia** — é a diferença entre uma prova decoreba e uma **prova com consulta**. O atendente RAG não precisa saber a política de devolução de cor; ele precisa saber *onde procurar* e *como ler*. De bônus, quando a política mudar, basta trocar o documento na estante — não é preciso "retreinar" ninguém.

## O fluxo RAG em cinco passos

```text
FASE DE PREPARO (feita uma vez, "montando a biblioteca"):
  1. CARREGAR   docs da loja (.md, .txt, .pdf)          → document_loader.py
  2. PICAR      em pedaços de ~700 caracteres (chunks)   → text_splitter.py
  3. INDEXAR    cada pedaço vira um "endereço numérico"
                (embedding) e vai para a estante ChromaDB → vector_store.py

FASE DE USO (a cada pergunta do cliente):
  4. BUSCAR     os 4 pedaços mais parecidos com a pergunta → similarity_search
  5. RESPONDER  o LLM responde SÓ com base nesses pedaços,
                citando as fontes                          → rag_chain.py
```

## Passo a passo, com o código real

### Passo 1-2 — Picar os documentos (`text_splitter.py`)

Por que picar? Porque a busca funciona melhor com trechos focados: se a pergunta é sobre prazo de reembolso, queremos achar **o parágrafo** do reembolso, não o manual inteiro de 40 páginas diluindo a relevância.

```python
DEFAULT_CHUNK_SIZE = 700       # cada pedaço tem ~700 caracteres (~1 parágrafo bom)
DEFAULT_CHUNK_OVERLAP = 120    # pedaços vizinhos compartilham 120 caracteres

splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=["\n\n", "\n", ". ", " ", ""],   # preferência de onde cortar:
)                                                # parágrafo > linha > frase > palavra
```

Dois detalhes espertos:

- **A sobreposição (overlap)** de 120 caracteres: se uma informação importante caísse exatamente na fronteira de dois pedaços, ela seria cortada ao meio e perdida. A sobreposição garante que fronteiras sempre existam **inteiras em pelo menos um pedaço**.
- **A ordem dos separadores**: o cortador tenta primeiro cortar em quebras de parágrafo (limpo), só recorrendo a cortes no meio de frases em último caso — como fatiar um bolo respeitando as camadas.

### Passo 3 — A estante mágica (`vector_store.py` + ChromaDB)

Aqui entra o conceito mais bonito do módulo: o **embedding**. Um modelo especial (aqui, o `text-embedding-3-small` da OpenAI) converte qualquer texto numa **lista de ~1500 números** que funciona como o "endereço do significado" daquele texto. Textos que falam da mesma coisa ganham endereços próximos — **mesmo sem usar as mesmas palavras**.

```python
class TechStoreVectorStore:
    def __init__(self, ...):
        # o tradutor de texto → números
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        # a estante persistente no disco (pasta chroma_db/)
        self._client = chromadb.PersistentClient(path=str(self.persist_directory))
        self._collection = self._client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents):
        texts = [d.page_content for d in documents]
        self._collection.upsert(                    # guarda na estante:
            ids=ids,                                 # etiqueta única de cada pedaço
            documents=texts,                         # o texto em si
            metadatas=[d.metadata for d in documents],  # de qual arquivo veio, posição...
            embeddings=self.embeddings.embed_documents(texts),  # o "endereço de significado"
        )

    def similarity_search(self, query, *, k=4):
        # converte a PERGUNTA para o mesmo sistema de endereços...
        # ...e pede à estante os k pedaços com endereços mais próximos
        result = self._collection.query(
            query_embeddings=[self.embeddings.embed_query(query)],
            n_results=k,
        )
```

> **💡 Analogia** — uma biblioteca comum organiza livros por ordem alfabética: "reembolso" e "devolução do dinheiro" ficam em estantes distantes, apesar de serem o mesmo assunto. A estante vetorial organiza por **assunto no espaço**: tudo que fala de devolver dinheiro fica na mesma prateleira, não importa a palavra usada. Quando chega a pergunta *"quero meu dinheiro de volta"*, o bibliotecário calcula o "endereço" da pergunta e vai direto à prateleira certa.

Isso resolve o problema clássico de buscas por palavra exata: o cliente pergunta *"posso trocar?"* e o documento diz *"política de devolução"* — a busca vetorial encontra mesmo assim, porque o **significado** é vizinho.

### Passo 4-5 — Responder com consulta (`rag_chain.py`)

A peça final junta busca + LLM, com as duas regras de ouro do RAG no prompt:

```python
def answer(self, question):
    documents = self._retriever.similarity_search(question, k=self._k)   # busca os 4 melhores
    if not documents:
        return self._not_found_message         # nada achado? admite, não inventa

    context = _format_context(documents)       # cola os 4 trechos num bloco numerado
    prompt = (
        f"{self._system_prompt} "
        f"Answer the question using only the context below. "          # REGRA 1: responda SÓ
        f"If the context does not contain the answer, say: "           #   com base no contexto
        f"{self._not_found_message}\n\n"                                # REGRA 2: se não estiver
        f"Context:\n{context}\n\n"                                      #   lá, diga "não sei"
        f"Question: {question}"
    )
    response = self._llm.invoke([HumanMessage(content=prompt)])
    sources = _format_sources(documents)
    return f"{response.content}\n\nSources: {sources}"                  # cita as fontes!
```

*Tradução:* o LLM recebe a pergunta **grampeada nos 4 trechos encontrados** e é instruído a não usar nada além deles. E a resposta sai com a lista de fontes — o cliente (ou o auditor) pode conferir de onde veio cada afirmação. É o principal antídoto contra a **alucinação** (o LLM inventar resposta com confiança).

### A integração com o chatbot — o porteiro do RAG

Nem toda pergunta precisa da biblioteca (*"oi, tudo bem?"* não requer consulta). Uma função simples decide:

```python
RAG_KEYWORDS = {"return", "refund", "warranty", "shipping", "policy",
                "product", "troubleshoot", "manual", "support", ...}

def should_use_rag(user_text):
    """Se a mensagem menciona algum assunto 'de biblioteca', consulta o RAG."""
    return any(keyword in user_text.lower() for keyword in RAG_KEYWORDS)
```

E o `MemoryAgent` da semana 3 ganhou este desvio: perguntas "de biblioteca" vão para o assistente RAG; o resto segue o fluxo normal do agente. As duas capacidades convivem.

## O mini-projeto: RAG sobre documentação da biblioteca Requests

Para provar que a receita é **genérica**, a semana 4 inclui um segundo notebook que monta o mesmo pipeline sobre outro acervo: a documentação oficial da *Requests* (uma biblioteca Python famosa). Mesmos passos — baixar páginas, picar, indexar (numa coleção ChromaDB separada), responder perguntas técnicas — e um bônus importante: **métricas de qualidade de busca** (precisão, revocação, F1 e curva ROC), medindo *quantos dos trechos recuperados eram de fato relevantes*.

Esse bônus planta a semente da semana 5: **como saber se o RAG está bom?** Não basta "parece que funciona" — é preciso medir.

## Resumo do que a semana 4 entregou

| Peça | Papel na "biblioteca" |
|------|----------------------|
| `document_loader.py` | Recebe os livros (`.md`, `.txt`, `.pdf`) |
| `text_splitter.py` | Pica em trechos de ~700 caracteres com sobreposição |
| `vector_store.py` + ChromaDB | A estante que organiza por significado |
| `rag_chain.py` | O bibliotecário: busca, responde só com base no texto, cita fontes |
| `should_use_rag` | O porteiro: decide quais perguntas vão à biblioteca |
| Mini-projeto Requests | Prova que a receita serve para qualquer acervo + primeiras métricas |

A biblioteca está de pé — mas é uma biblioteca ingênua: a busca às vezes traz 4 trechos quase idênticos, o trecho certo às vezes fica em 5º lugar (fora do top 4), e ninguém mediu sistematicamente a qualidade. A **semana 5** existe para afinar exatamente isso.

---

## Passo a passo: como o código foi construído

A semana 4 foi construída como uma **caixa de peças em `src/rag/`** — cinco módulos pequenos, cada um dono de uma etapa — e um notebook que os encadeia e demonstra. Ordem de construção: da entrada (carregar) para a saída (responder).

### Passo 1 — O recebedor de livros (`document_loader.py`)

```python
SUPPORTED_TEXT_EXTENSIONS = {".md", ".txt"}

def load_document(path):
    """Carrega UM documento, com os metadados que a busca vai precisar."""
    document_path = Path(path)
    if not document_path.exists():
        raise FileNotFoundError(f"Document not found: {document_path}")   # falha clara e cedo

    extension = document_path.suffix.lower()
    if extension in SUPPORTED_TEXT_EXTENSIONS:
        return [_load_text_document(document_path)]     # texto: leitura direta
    if extension == ".pdf":
        return _load_pdf_document(document_path)         # PDF: uma página = um Document
    raise ValueError(f"Unsupported document type: {extension}")
```

O detalhe central é que **todo documento sai carimbado**:

```python
def _load_text_document(path):
    return Document(
        page_content=path.read_text(encoding="utf-8").strip(),   # o texto
        metadata={
            "source": str(path),                    # de onde veio (para as citações!)
            "title": path.name,                     # o nome amigável
            "document_type": path.suffix.lower().lstrip("."),    # md/txt/pdf
        },
    )
```

*Esses metadados são a matéria-prima das citações lá na frente:* quando a resposta disser "Sources: policy_returns.md", é este carimbo, colocado na hora do carregamento, que viajou pelo pipeline inteiro. E no PDF, cada página ainda ganha `page_number` — citação com página.

*Note também o tratamento do PDF:* a biblioteca de PDF só é importada **dentro** da função (`import` tardio), com uma mensagem de erro que ensina a instalar o que falta. Quem só usa `.md` nunca paga o custo da dependência de PDF.

### Passo 2 — O picador (`text_splitter.py`)

Já dissecado na seção anterior — 26 linhas, uma função. O acréscimo do passo a passo é o **carimbo de posição**:

```python
chunks = splitter.split_documents(documents)
for index, chunk in enumerate(chunks):
    chunk.metadata = {**chunk.metadata, "chunk_index": index}
    #                 ↑ preserva os metadados originais E adiciona a posição
```

O `chunk_index` vai ser usado no passo 3 para dar a cada pedaço uma **identidade estável**.

### Passo 3 — A estante (`vector_store.py`)

A classe `TechStoreVectorStore` embrulha o ChromaDB. As decisões de construção:

**Identidade estável dos pedaços** — a função que gera a etiqueta de cada chunk:

```python
def _document_id(document, index):
    source = str(document.metadata.get("source", "unknown"))
    chunk_index = document.metadata.get("chunk_index", index)
    return f"{source}:{chunk_index}"        # ex.: "docs/kb/policy_returns.md:3"
```

*Por que isso importa:* o método de gravação usa `upsert` (update + insert) — se o mesmo documento for indexado duas vezes, os pedaços **substituem** os antigos em vez de duplicar. Rodar o preparo de novo é seguro; a estante nunca acumula cópias fantasmas. (Termo técnico: a operação é *idempotente*.)

**A tradução de volta** — a busca devolve dados crus do ChromaDB, e o código os re-embrulha em `Document` para o resto do pipeline não precisar conhecer o formato interno do banco:

```python
def similarity_search(self, query, *, k=4):
    result = self._collection.query(
        query_embeddings=[self.embeddings.embed_query(query)],   # pergunta → números
        n_results=k,
    )
    documents = result.get("documents", [[]])[0]      # defensivo: se vier vazio, lista vazia
    metadatas = result.get("metadatas", [[]])[0]
    return [Document(page_content=content, metadata=metadata or {})
            for content, metadata in zip(documents, metadatas)]
```

### Passo 4 — O bibliotecário (`rag_chain.py`)

Dissecado na seção anterior. O acréscimo aqui é a estrutura interna do contexto — como os 4 trechos são "grampeados" para o LLM:

```python
def _format_context(documents):
    parts = []
    for index, document in enumerate(documents, start=1):
        title = document.metadata.get("title") or document.metadata.get("source", "Unknown")
        parts.append(f"[{index}] {title}\n{document.page_content}")
        #             ↑ cada trecho numerado e identificado — o LLM consegue
        #               referenciar "[2]" e o leitor consegue conferir
    return "\n\n".join(parts)

def _format_sources(documents):
    sources = []
    for document in documents:
        source = document.metadata.get("title") or document.metadata.get("source", ...)
        if source not in sources:          # deduplicação: cada fonte citada UMA vez
            sources.append(str(source))
    return ", ".join(sources)
```

### Passo 5 — O indexador de linha de comando (`index_knowledge_base.py`)

Um script de 31 linhas que junta os passos 1-3 num comando único: carregar `docs/knowledge_base/` → picar → gravar na estante. É o botão "reconstruir a biblioteca" — roda uma vez no preparo, ou sempre que os documentos mudarem.

### Passo 6 — O notebook demonstra o ciclo completo

As células do `Week4_RAG_TechStore.ipynb` seguem os títulos: **1. Load Documents** → **2. Split Into Chunks** → **3. Generate Embeddings And Store In ChromaDB** → **4. Reload And Retrieve** → **5. Ask Grounded Questions**.

A célula 4 tem um teste sutil e importante: ela **recarrega a estante do disco** (nova instância apontando para a mesma pasta `chroma_db/`) antes de buscar — provando que a persistência funciona de verdade, e não só enquanto o objeto original está na memória.

### Passo 7 — O mini-projeto Requests (generalização + métricas)

O segundo notebook (`Week4_RAG_Python_Library.ipynb`) reusa as mesmas peças sobre outro acervo, com dois módulos novos:

- **`python_library_docs.py`** — baixa páginas selecionadas da documentação oficial da Requests e guarda cópias `.txt` locais (o acervo não depende de internet depois do preparo).
- **`evaluation.py`** — as primeiras métricas do projeto: para um conjunto de perguntas com gabarito (quais documentos são relevantes para cada uma), calcula **precisão** (dos recuperados, quantos eram certos?), **revocação** (dos certos, quantos foram recuperados?), **F1** (a média harmônica dos dois) e os pontos da **curva ROC**.

E um bônus de usabilidade: `scripts/requests_rag_chatbot.py` empacota tudo num chatbot de terminal (`python scripts/requests_rag_chatbot.py --question "How do I set a timeout?"`) — a primeira interface "de usuário" do RAG.
