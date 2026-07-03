# Guia de Estudo das Weeks 1 a 7 - Design

## Objetivo

Produzir um documento didatico em portugues, com aproximadamente 90 a 120
paginas, que explique a evolucao do projeto TechStore Plus da Week 1 ate a
Week 7. O leitor-alvo e uma pessoa iniciante em Python, inteligencia artificial,
RAG e LangGraph, mas que deseja compreender o que foi construido, por que cada
decisao foi tomada e como verificar o funcionamento da aplicacao.

O resultado principal sera um PDF pronto para estudo. Uma versao-fonte sera
mantida em formato editavel para permitir correcoes e novas edicoes.

## Principios editoriais

Cada conceito deve ser apresentado nesta ordem:

1. problema em linguagem cotidiana;
2. conceito tecnico necessario;
3. solucao adotada no projeto;
4. motivo da escolha;
5. codigo relevante comentado;
6. forma de executar e testar;
7. resultado esperado;
8. limitacoes e proximos passos.

Termos tecnicos nao devem aparecer sem uma definicao simples na primeira
ocorrencia. Analogias podem ser usadas, mas devem ser acompanhadas da definicao
tecnica correta. O texto deve distinguir claramente fatos observados no codigo,
requisitos dos desafios e interpretacoes pedagogicas.

## Fontes de verdade

O conteudo sera levantado e conferido a partir de:

- PDFs oficiais dos desafios disponiveis para as Weeks 1 a 7;
- repositorios M1, M2 e M3 publicados na organizacao Pluralit;
- codigo e notebooks existentes no workspace local;
- testes automatizados e suas saidas atuais;
- historico Git, commits e tags de cada etapa;
- READMEs e documentos de arquitetura existentes.

Quando o PDF do desafio e o codigo divergirem, o documento explicara a
divergencia. Exemplo conhecido: o calculo `(2.5 + 7) * 3` resulta em `28.5`,
embora um enunciado apresente `27.0`.

Nenhuma chave, token, senha, conteudo de `.env` ou dado pessoal sera copiado
para o documento, arquivos-fonte ou logs de geracao.

## Estrutura do documento

### Parte I - Orientacao para iniciantes

1. Capa, autoria e versao.
2. Como utilizar o guia.
3. Visao geral do TechStore Plus.
4. Preparacao do ambiente no Windows.
5. Python, ambiente virtual, dependencias e variaveis de ambiente.
6. Git, GitHub, notebooks e testes.
7. Glossario inicial.

### Parte II - Evolucao cronologica

Cada Week tera um capitulo independente com objetivo, contexto anterior,
arquitetura, implementacao, codigo explicado, testes e conclusao.

- Week 1: fundacao do chatbot e primeiro fluxo de atendimento.
- Week 2: ferramentas, dados e operacoes de atendimento.
- Week 3: agente, memoria, persistencia de conversa e integracoes.
- Week 4: carregamento de documentos, chunks, embeddings, ChromaDB e RAG.
- Week 5: MMR, cross-encoder, re-ranking, experimentos e metricas.
- Week 6: Graph RAG, tabelas, imagens, citacoes, guardrails e observabilidade.
- Week 7: StateGraph, ToolNode, reducers, checkpoint, streaming, limites e
  validacao segura.

### Parte III - Visao integrada

1. Arquitetura final do sistema.
2. Como uma pergunta percorre o chatbot.
3. Evolucao do fluxo entre as Weeks.
4. Relacao entre o chatbot original, RAG e LangGraph.
5. Decisoes tecnicas importantes e alternativas.
6. Limitacoes conhecidas e melhorias futuras.

### Parte IV - Guia pratico de testes

1. Preparacao limpa do ambiente.
2. Validacao das variaveis sem revelar segredos.
3. Testes das Weeks 1 a 3.
4. Testes do RAG basico e persistencia do ChromaDB.
5. Testes de recuperacao e metricas da Week 5.
6. Testes de Graph RAG, guardrails e multimodalidade.
7. Testes do agente LangGraph e checkpoint.
8. Execucao dos notebooks.
9. Interpretacao de resultados e warnings.
10. Solucao de erros comuns.

### Parte V - Referencia

1. Mapa de arquivos e responsabilidades.
2. Comandos essenciais.
3. Glossario completo.
4. Referencias e links dos repositorios.
5. Checklist de aprendizagem.

## Modelo de capitulo semanal

Cada capitulo das Weeks seguira o mesmo formato:

```text
Objetivo
O que ja existia
Problema a resolver
Conceitos essenciais
Arquitetura da solucao
Implementacao por arquivo
Codigo comentado
Por que esta abordagem foi escolhida
Como executar
Como testar
Resultado esperado
Problemas encontrados e correcoes
Limitacoes
Resumo e perguntas de revisao
```

Esse padrao permite comparar as etapas sem transformar o documento em uma
colecao de resumos desconectados.

## Explicacao de codigo

O PDF nao reproduzira arquivos inteiros quando isso prejudicar a leitura. Cada
trecho sera escolhido por representar uma responsabilidade importante, como:

- criacao de ferramentas;
- definicao de estado;
- construcao de chains e grafos;
- carregamento e divisao de documentos;
- embeddings e vector store;
- recuperacao, re-ranking e metricas;
- verificacao de respostas;
- checkpoint e retomada.

Antes do trecho, o texto explicara entradas, saidas e dependencias. Depois do
trecho, cada bloco logico sera interpretado em linguagem simples e conectado ao
fluxo geral. O caminho do arquivo real sera informado para que o leitor possa
consultar o codigo completo.

## Guia de testes

Cada procedimento de teste deve declarar:

- objetivo do teste;
- pre-requisitos;
- diretorio correto;
- comando exato para PowerShell;
- comportamento esperado;
- exemplo de saida sem dados sensiveis;
- significado do resultado;
- diagnostico para falhas frequentes.

Testes que dependem de API serao identificados separadamente dos testes offline.
Custos, conectividade e disponibilidade de modelos serao mencionados quando
relevantes. Warnings conhecidos nao serao descritos como falhas.

## Elementos visuais

O documento utilizara diagramas simples e legiveis para:

- evolucao arquitetural das Weeks 1 a 7;
- fluxo de uma pergunta pelo chatbot;
- pipeline RAG;
- MMR e re-ranking;
- Graph RAG e fontes multimodais;
- fluxo do StateGraph e suas saidas seguras;
- relacao entre arquivos e componentes.

Tabelas serao usadas para comparar configuracoes, metricas, decisoes e
resultados. Capturas de tela serao usadas apenas quando agregarem informacao que
nao possa ser comunicada melhor por texto ou diagrama.

## Processo de producao

1. Inventariar fontes e identificar lacunas das Weeks 1 a 7.
2. Validar a correspondencia entre desafios, codigo e repositorios publicados.
3. Criar uma matriz por Week com requisitos, arquivos, testes e resultados.
4. Redigir primeiro em Markdown estruturado.
5. Gerar diagramas e tabelas.
6. Executar comandos de teste novamente e registrar resultados sanitizados.
7. Gerar o PDF com sumario, cabecalhos, rodapes e numeracao.
8. Inspecionar visualmente todas as paginas.
9. Verificar links, caminhos, comandos e ausencia de segredos.
10. Entregar PDF, fonte editavel e relatorio curto de validacao.

## Artefatos previstos

- `docs/study-guide/weeks-1-7-guia-completo.md`
- `docs/study-guide/assets/` para diagramas e imagens autorizadas;
- `docs/study-guide/weeks-1-7-guia-completo.pdf`
- `scripts/generate_weeks_1_7_study_guide.py` para geracao reproduzivel;
- `docs/study-guide/validation-report.md` com verificacoes executadas.

## Criterios de aceitacao

O trabalho sera considerado concluido quando:

- as sete Weeks estiverem cobertas;
- cada Week explicar o que, por que e como testar;
- os principais componentes possuirem codigo comentado;
- todos os comandos apresentados tiverem sido conferidos;
- o PDF possuir aproximadamente 90 a 120 paginas sem repeticao artificial;
- indice, links, diagramas, tabelas e blocos de codigo estiverem legiveis;
- nenhum texto ou elemento visual estiver cortado ou sobreposto;
- nao houver segredos ou dados pessoais;
- o PDF abrir corretamente e a contagem de paginas for validada;
- o documento-fonte permitir regeneracao do PDF.

## Fora de escopo

- explicar integralmente bibliotecas de terceiros;
- reproduzir todos os arquivos do repositorio no PDF;
- documentar o BrunoAudioManager, que nao pertence ao percurso Weeks 1 a 7;
- alterar o comportamento das aplicacoes para facilitar a documentacao;
- publicar o PDF em repositorios remotos sem solicitacao explicita.
