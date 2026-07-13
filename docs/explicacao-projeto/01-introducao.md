# TechStore Plus — A Jornada de um Atendente Virtual

## Explicação completa do projeto, semanas 1 a 9, para quem não é da área

---

# Introdução

## A história que este documento conta

Imagine uma loja de eletrônicos chamada **TechStore Plus**. Ela vende celulares, notebooks, fones de ouvido — e, como toda loja, recebe dezenas de mensagens de clientes por dia: *"meu pedido não chegou"*, *"como devolvo esse produto?"*, *"qual notebook você recomenda para estudar engenharia?"*.

Este projeto construiu, ao longo de nove semanas, um **atendente virtual** (um *chatbot*) capaz de responder essas mensagens. Mas não de qualquer jeito: a cada semana o atendente ganhou uma habilidade nova, como um funcionário que vai sendo treinado e promovido.

A evolução aconteceu em **três módulos**, cada um com três semanas e um desafio prático no final:

| Módulo | Semanas | O que o atendente aprendeu | Desafio |
|--------|---------|---------------------------|---------|
| **1 — O nascimento** | 1 a 3 | Conversar, entender o cliente, lembrar do que foi dito e usar ferramentas | Ir para produção: virar um site de verdade, no ar |
| **2 — O estudo** | 4 a 6 | Consultar documentos da loja antes de responder (a técnica chamada RAG) | Um sistema de consulta robusto, com trava contra respostas inventadas |
| **3 — O raciocínio** | 7 a 9 | Trabalhar em etapas planejadas, delegar para especialistas e desfazer erros | Uma equipe de atendentes coordenada por um supervisor |

Cada capítulo deste documento explica uma dessas semanas: **o que** foi construído, **por que** foi construído daquele jeito, e **como** o código funciona — sempre em linguagem comum, com analogias do dia a dia, e com trechos de código comentados linha por linha para quem quiser espiar por baixo do capô.

## Como ler este documento

Você **não precisa saber programar** para acompanhar. O documento foi organizado para três tipos de leitura:

1. **Leitura corrida** — leia só o texto e as analogias, pulando os quadros de código. Você vai entender o que o sistema faz e por quê.
2. **Leitura curiosa** — leia também os quadros "Por dentro do código". Cada trecho vem com uma tradução em português do que cada linha faz.
3. **Leitura de referência** — use o glossário no final sempre que um termo técnico aparecer. Termos do glossário aparecem em **negrito** na primeira vez que surgem em cada capítulo.

Os quadros seguem um padrão:

> **💡 Analogia** — uma comparação com o mundo real para fixar a ideia.

```python
# Os blocos como este são código de verdade do projeto,
# sempre acompanhados de comentários explicando cada parte.
```

---

# Conceitos Fundamentais — o mínimo que você precisa saber

Antes da semana 1, vale um mini-curso de dez minutos. São sete conceitos que aparecem no projeto inteiro. Se você já conhece, pule para o próximo capítulo.

## 1. O que é um programa de computador?

Um programa é uma **receita de bolo escrita para o computador**: uma lista de instruções, em ordem, que a máquina segue ao pé da letra. A diferença para uma receita de verdade é que o computador não improvisa — se a instrução estiver ambígua ou errada, ele erra junto, sem perceber.

## 2. O que é Python?

**Python** é a linguagem em que este projeto foi escrito — uma das "línguas" que humanos usam para escrever instruções que o computador entende. Foi escolhida por ser a mais popular no mundo da inteligência artificial e por ser relativamente legível: um código Python bem escrito quase se lê como inglês.

```python
# Exemplo do mundo real: três linhas de Python
nome = "Maria"                      # guarda o texto "Maria" numa caixinha chamada 'nome'
saudacao = f"Olá, {nome}!"          # monta a frase usando o conteúdo da caixinha
print(saudacao)                     # mostra na tela: Olá, Maria!
```

As "caixinhas" (`nome`, `saudacao`) se chamam **variáveis**. Blocos de instruções reutilizáveis se chamam **funções** — pense numa função como um eletrodoméstico: você coloca algo dentro (os *parâmetros*), aperta o botão, e sai um resultado.

## 3. O que é um LLM (o "cérebro" do chatbot)?

**LLM** significa *Large Language Model* — "grande modelo de linguagem". É um programa treinado com uma quantidade gigantesca de textos, que aprendeu a **prever qual palavra vem a seguir** em qualquer frase. Dessa habilidade aparentemente simples emerge algo poderoso: ele consegue conversar, resumir, traduzir e responder perguntas.

O LLM usado neste projeto se chama **GPT-4o-mini**, da empresa OpenAI (a mesma do ChatGPT). Ele não roda no computador do projeto — roda nos servidores da OpenAI, e o nosso código conversa com ele pela internet.

> **💡 Analogia** — o LLM é como um consultor extremamente culto que atende por telefone. Ele leu praticamente tudo que existe, mas: (1) você paga por minuto de conversa, (2) ele não conhece a *sua* empresa, e (3) de vez em quando ele responde com confiança algo que está errado. Boa parte deste projeto é aprender a trabalhar com esse consultor: dar contexto a ele, conferir as respostas e não gastar telefonema à toa.

## 4. O que é uma API?

**API** (*Application Programming Interface*) é a forma como dois programas conversam entre si. Se um site tem um balcão de atendimento para pessoas (botões, telas), a API é o **balcão de atendimento para outros programas**: um endereço na internet onde um programa faz um pedido padronizado e recebe uma resposta padronizada.

Quando nosso chatbot precisa do LLM, ele faz uma **chamada de API** para a OpenAI: envia a pergunta do cliente e recebe a resposta gerada. Cada chamada custa alguns centavos — por isso o projeto se preocupa tanto em fazer menos chamadas e chamadas mais inteligentes.

A **chave de API** (*API key*) é a senha que identifica quem está pedindo — como um cartão corporativo: quem tem o cartão pode usar o serviço, e a conta chega no dono do cartão. Por isso ela nunca é publicada junto com o código.

## 5. O que é um prompt?

**Prompt** é o texto de instruções que enviamos ao LLM. É literalmente o que você "fala" para o consultor do telefone antes de fazer a pergunta. Há dois tipos importantes no projeto:

- **Prompt de sistema** (*system prompt*): as instruções permanentes — "você é um atendente da TechStore Plus, seja educado, siga estes passos...". Define a personalidade e as regras.
- **Mensagem do usuário**: a pergunta do cliente naquele momento.

Grande parte da "programação" de um chatbot moderno é, na verdade, **escrever bons prompts** — instruções claras, com exemplos, que não deixem margem para o LLM inventar.

## 6. O que é JSON?

**JSON** é um formato de texto para organizar informações de um jeito que tanto humanos quanto programas conseguem ler. Pense numa **ficha cadastral padronizada**:

```json
{
  "cliente": "Maria Silva",
  "categoria": "devolução",
  "urgencia": "alta",
  "produtos_mencionados": ["iPhone 15"]
}
```

O projeto usa JSON o tempo todo: para guardar o histórico das conversas em arquivos, e para obrigar o LLM a responder de forma estruturada (em vez de um texto solto, uma ficha preenchida — que o programa consegue processar automaticamente).

## 7. O que são bibliotecas e frameworks?

Ninguém constrói uma casa fabricando os próprios tijolos. Em programação, **bibliotecas** são caixas de peças prontas feitas por outras pessoas, que o projeto importa e usa. As principais aqui:

| Biblioteca | O que faz no projeto |
|------------|---------------------|
| **OpenAI** | Conversa com o LLM GPT-4o-mini |
| **LangChain** | Organiza as etapas do chatbot como uma linha de montagem (semana 2 em diante) |
| **LangGraph** | Permite montar fluxos com decisões, desvios e memória (semanas 7-9) |
| **Pydantic** | Confere se os dados têm o formato certo — um "fiscal de qualidade" de fichas |
| **ChromaDB** | Banco de dados especial que busca por *significado*, não por palavra exata (semanas 4-6) |
| **FastAPI** | Cria o "balcão de atendimento" (API) do nosso próprio sistema (desafio M1) |
| **pytest** | Roda testes automáticos que conferem se tudo continua funcionando |

Um **framework** é uma biblioteca grande que dita a estrutura do programa — você preenche as lacunas dele, e não o contrário.

## Um mapa mental para levar para o resto do documento

Tudo que vem pela frente é variação de um mesmo ciclo:

```text
  mensagem do cliente
        ↓
  [preparar contexto]     ← o que o atendente precisa saber para responder bem?
        ↓
  [chamar o LLM]          ← o telefonema para o consultor
        ↓
  [conferir e estruturar] ← a resposta está no formato certo? é confiável?
        ↓
  [agir e registrar]      ← responder o cliente, salvar histórico, acionar ferramentas
```

- O **módulo 1** constrói esse ciclo e o coloca no ar.
- O **módulo 2** turbina a etapa "preparar contexto" com documentos da loja (RAG).
- O **módulo 3** transforma o ciclo único em um **fluxo com várias etapas e vários especialistas**.

Boa leitura!
