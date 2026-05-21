from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs"
OUTPUT_FILE = OUTPUT_DIR / "explicacao_funcoes_techstore_chatbot.pdf"


CONTENT = [
    ("title", "Explicacao das Funcoes do Projeto TechStore Plus"),
    (
        "body",
        "Este documento detalha a logica por tras do projeto de chatbot de atendimento "
        "da loja ficticia TechStore Plus. O projeto tem duas versoes principais: uma "
        "versao inicial usando a API da OpenAI diretamente e uma versao refatorada com "
        "LangChain LCEL, Pydantic e uma arquitetura em cadeia.",
    ),
    ("heading", "Visao Geral"),
    (
        "body",
        "O fluxo geral e: mensagem do cliente -> analise/classificacao da intencao -> "
        "geracao da resposta personalizada -> criacao de resumo estruturado -> "
        "salvamento em JSON -> consolidacao dos atendimentos.",
    ),
    (
        "body",
        "A ideia central e separar tres responsabilidades: entender o problema do "
        "cliente, responder de forma adequada ao caso e registrar o atendimento de "
        "forma estruturada.",
    ),
    ("heading", "Notebook Semana 1: OpenAI Direto"),
    (
        "body",
        "Arquivo: TechStorePlus_Customer_Service_Chatbot_Project.ipynb. Esta versao "
        "usa funcoes Python tradicionais, chamadas diretas ao modelo e parsing manual "
        "de JSON.",
    ),
    ("subheading", "ConversationSession"),
    (
        "body",
        "Classe responsavel por guardar o estado de uma conversa. Ela mantem o ID do "
        "cliente, o horario de criacao e uma lista de mensagens com os papeis system, "
        "user e assistant.",
    ),
    ("subheading", "__init__(customer_id=None)"),
    (
        "body",
        "Cria uma nova sessao. Se nenhum customer_id for informado, gera um ID automatico "
        "no formato CUST-XXXXXXXX. Tambem inicializa o historico com a mensagem system, "
        "que contem o comportamento esperado do chatbot e o contexto da empresa.",
    ),
    ("subheading", "add_user_message(message)"),
    (
        "body",
        "Adiciona ao historico uma mensagem enviada pelo cliente. Isso permite que as "
        "proximas chamadas ao modelo tenham contexto do que ja foi dito.",
    ),
    ("subheading", "add_assistant_message(message)"),
    (
        "body",
        "Adiciona ao historico uma resposta do chatbot. Assim, a conversa fica completa "
        "e pode ser reutilizada em respostas futuras ou em resumos.",
    ),
    ("subheading", "get_public_history()"),
    (
        "body",
        "Retorna o historico sem a mensagem system. A mensagem system e uma instrucao "
        "interna para o modelo e nao deve aparecer em resumos ou registros externos.",
    ),
    ("subheading", "analyze_customer_query(query)"),
    (
        "body",
        "Analisa a mensagem do cliente com o modelo gpt-4o-mini. A funcao pede que o "
        "modelo retorne apenas JSON valido contendo sentimento, emocoes, categoria, "
        "urgencia, produtos mencionados, informacoes extraidas, roteamento recomendado "
        "e um resumo do raciocinio.",
    ),
    (
        "body",
        "A temperatura e 0 porque classificacao deve ser previsivel. Depois da chamada, "
        "a funcao usa json.loads para converter a resposta em dicionario Python. Se o "
        "modelo devolver JSON dentro de bloco Markdown, a funcao remove as crases e "
        "tenta converter novamente.",
    ),
    ("subheading", "generate_personalized_response(session, user_query, analysis)"),
    (
        "body",
        "Gera a resposta final para o cliente usando o historico da sessao, a mensagem "
        "do usuario, a analise estruturada e as politicas da TechStore Plus. Primeiro "
        "adiciona a mensagem do cliente ao historico, depois envia o historico completo "
        "mais uma instrucao de resposta ao modelo.",
    ),
    (
        "body",
        "A temperatura e 0.4 para permitir uma resposta mais natural, mas ainda controlada. "
        "Depois de receber o texto, a funcao salva a resposta no historico da sessao e "
        "retorna esse texto.",
    ),
    ("subheading", "chatbot_reply(session, user_query)"),
    (
        "body",
        "Funcao principal da Semana 1. Ela orquestra duas etapas: primeiro chama "
        "analyze_customer_query para entender a mensagem; depois chama "
        "generate_personalized_response para responder. Retorna customer_id, query, "
        "analysis e reply.",
    ),
    ("subheading", "generate_conversation_summary(...)"),
    (
        "body",
        "Cria um resumo estruturado da conversa. Na versao com OpenAI, pega o historico "
        "publico da sessao, pede ao modelo para resumir em um paragrafo e monta um JSON "
        "com timestamp, customer_id, categoria, sentimento, urgencia, produtos, "
        "informacoes extraidas, status de resolucao, acoes tomadas e follow-up.",
    ),
    ("subheading", "save_conversation_json(conversation_summary)"),
    (
        "body",
        "Salva o resumo da conversa em conversation_data com nome no formato "
        "conversation_{customer_id}_{timestamp}.json. Retorna o caminho do arquivo salvo.",
    ),
    ("subheading", "consolidate_conversations(output_file='consolidated_conversations.json')"),
    (
        "body",
        "Le todos os arquivos conversation_*.json da pasta conversation_data, junta os "
        "registros em uma lista e salva um arquivo consolidado com generated_at, "
        "total_conversations e conversations.",
    ),
    ("heading", "Modo Mock da Semana 1"),
    (
        "body",
        "O modo mock e ativado com MOCK_MODE = True. Ele substitui funcoes que chamariam "
        "a API por implementacoes locais baseadas em regras, permitindo demonstrar o "
        "projeto sem gastar tokens.",
    ),
    ("subheading", "mock_extract_products(query)"),
    (
        "body",
        "Procura nomes de produtos com base em palavras-chave. Por exemplo, se a frase "
        "contem iphone 15, adiciona iPhone 15 a lista de produtos mencionados.",
    ),
    ("subheading", "mock_extract_information(query)"),
    (
        "body",
        "Usa expressoes regulares para extrair numero de pedido, valores em dolar e datas "
        "em ingles. Retorna um dicionario com order_number, purchase_date e amount.",
    ),
    ("subheading", "analyze_customer_query(query) no mock"),
    (
        "body",
        "Classifica urgencia, sentimento, emocoes, categoria e roteamento usando regras. "
        "Termos como emergency, urgent e tomorrow levam a urgencia high. Termos como "
        "thank e excellent indicam sentimento positivo. Termos como never arrived e "
        "doesn't work indicam sentimento negativo.",
    ),
    (
        "body",
        "A categoria tambem vem de palavras-chave: receipt e payment viram billing; "
        "return e refund viram return; warranty vira warranty; configure e doesn't work "
        "viram technical; stock, shipping, recommend e budget viram product_information. "
        "Se a urgencia for high, o roteamento recomendado vira Priority Support Team.",
    ),
    ("subheading", "generate_personalized_response(...) no mock"),
    (
        "body",
        "Monta uma resposta com blocos fixos: abertura conforme urgencia ou sentimento, "
        "acao conforme categoria, detalhes de pedido/produto, roteamento recomendado e "
        "observacao de prioridade quando o caso e urgente. Tambem atualiza o historico "
        "da sessao.",
    ),
    ("subheading", "generate_conversation_summary(...) no mock"),
    (
        "body",
        "Cria o JSON final sem chamar o modelo. Usa a ultima mensagem do cliente, a "
        "categoria, o sentimento e a urgencia para montar uma frase de resumo local.",
    ),
    ("subheading", "mock_analyze_customer_query(query)"),
    (
        "body",
        "Versao mock mais simples, usada como fallback/demonstracao. Classifica urgencia, "
        "sentimento e categoria, mas nao extrai produtos e informacoes com o mesmo nivel "
        "da versao mock principal.",
    ),
    ("heading", "Notebook Semana 2: LangChain LCEL"),
    (
        "body",
        "Arquivo: TechStorePlus_LangChain_LCEL_Chatbot.ipynb. Esta versao organiza o "
        "projeto como uma cadeia modular usando LangChain LCEL e modelos Pydantic.",
    ),
    ("subheading", "ExtractedEntities"),
    (
        "body",
        "Modelo Pydantic que define as entidades extraidas da consulta: product_name, "
        "order_number e date. Isso torna a saida da analise mais previsivel.",
    ),
    ("subheading", "QueryAnalysis"),
    (
        "body",
        "Modelo Pydantic que define a estrutura da analise: query_category, urgency_level, "
        "customer_sentiment e entities. O uso de Literal limita os valores aceitos e "
        "impede categorias inventadas pelo modelo.",
    ),
    ("subheading", "analysis_chain"),
    (
        "body",
        "Componente LCEL equivalente a analyze_customer_query. Ele conecta o prompt de "
        "analise ao modelo com structured output: analysis_prompt | "
        "analysis_llm.with_structured_output(QueryAnalysis). Assim, a resposta precisa "
        "seguir o schema Pydantic.",
    ),
    ("subheading", "CATEGORY_PROMPTS"),
    (
        "body",
        "Dicionario com prompts especificos por categoria: technical_support, billing, "
        "returns, product_inquiry e general_information. Cada categoria muda a persona "
        "e as instrucoes do atendente.",
    ),
    ("subheading", "route_response(inputs)"),
    (
        "body",
        "Funcao de roteamento dinamico. Ela recebe a query e a analise, le "
        "analysis.query_category, escolhe o prompt correto em CATEGORY_PROMPTS, monta "
        "uma mini-chain prompt | response_llm e invoca essa chain com query, sentimento, "
        "urgencia, entidades e contexto da empresa.",
    ),
    ("subheading", "ConversationSummary"),
    (
        "body",
        "Modelo Pydantic para o resultado final do atendimento. Define timestamp, "
        "customer_id, conversation_summary, query_category, customer_sentiment, "
        "urgency_level, mentioned_products, extracted_information, resolution_status, "
        "actions_taken e follow_up_required.",
    ),
    ("subheading", "_response_text(response)"),
    (
        "body",
        "Extrai texto legivel de uma resposta LangChain. Se a resposta tiver atributo "
        "content, usa esse atributo. Se o conteudo for lista, junta as partes em uma "
        "string. Caso contrario, converte para string.",
    ),
    ("subheading", "_short_action_from_response(response)"),
    (
        "body",
        "Cria uma versao curta da resposta para registrar em actions_taken. Remove quebras "
        "de linha, limita a 180 caracteres e adiciona reticencias quando necessario.",
    ),
    ("subheading", "build_summary(inputs)"),
    (
        "body",
        "Monta o ConversationSummary a partir da analise e da resposta. Nao chama LLM. "
        "Extrai produto, pedido e data; mapeia urgencia para status; cria uma frase de "
        "resumo; monta actions_taken; define follow_up_required como verdadeiro para "
        "urgencia high ou medium.",
    ),
    (
        "body",
        "O mapeamento de status e: high -> escalated, medium -> pending e low -> resolved. "
        "Essa regra e logica de negocio, nao uma decisao livre do modelo.",
    ),
    ("subheading", "save_conversation_json(summary)"),
    (
        "body",
        "Salva o ConversationSummary em JSON dentro de conversation_data. Na Semana 2, "
        "os arquivos comecam com week2_conversation_, separando-os dos arquivos da "
        "Semana 1.",
    ),
    ("subheading", "consolidate_conversations(output_file='week2_consolidated_conversations.json')"),
    (
        "body",
        "Consolida apenas os arquivos week2_conversation_*.json, criando um arquivo final "
        "com generated_at, total_conversations e conversations.",
    ),
    ("subheading", "chain_with_context"),
    (
        "body",
        "Cadeia LCEL completa que preserva informacoes intermediarias. Primeiro adiciona "
        "analysis, depois response e depois summary. Isso permite visualizar analise, "
        "resposta e resumo na mesma execucao.",
    ),
    ("subheading", "full_chain"),
    (
        "body",
        "Versao final da cadeia que retorna apenas x['summary']. Ela existe porque a "
        "saida esperada formalmente e uma instancia de ConversationSummary.",
    ),
    ("heading", "starter.ipynb"),
    (
        "body",
        "O arquivo starter.ipynb tem uma funcao simples chamada greet(name), usada como "
        "exemplo inicial. Ela nao participa da arquitetura principal do chatbot.",
    ),
    ("heading", "Resumo Final"),
    (
        "body",
        "A Semana 1 mostra o chatbot funcionando de forma direta: funcoes Python -> "
        "OpenAI API -> JSON manual -> resposta -> arquivo. A Semana 2 melhora a "
        "arquitetura: LCEL chain -> analise validada -> roteamento por categoria -> "
        "resumo estruturado.",
    ),
    (
        "body",
        "A diferenca mais importante e que a Semana 2 separa melhor as responsabilidades. "
        "A analise vira um objeto validado, o roteamento fica centralizado em "
        "route_response() e o resumo final e criado por regra em build_summary(), sem "
        "depender de mais uma resposta do modelo.",
    ),
]


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "TechStore Plus - Explicacao do Codigo")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def build_pdf():
    OUTPUT_DIR.mkdir(exist_ok=True)

    doc = BaseDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Explicacao das Funcoes do Projeto TechStore Plus",
        author="Codex",
    )

    frame = Frame(doc.leftMargin, doc.bottomMargin + 0.5 * cm, doc.width, doc.height - 0.5 * cm)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=14,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subheading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceBefore=9,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyTextCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#111827"),
            spaceAfter=6,
        )
    )

    story = []
    style_map = {
        "title": styles["DocTitle"],
        "heading": styles["Heading"],
        "subheading": styles["Subheading"],
        "body": styles["BodyTextCustom"],
    }

    for kind, text in CONTENT:
        story.append(Paragraph(text, style_map[kind]))
        if kind in {"title", "heading"}:
            story.append(Spacer(1, 4))

    doc.build(story)
    return OUTPUT_FILE


if __name__ == "__main__":
    print(build_pdf())
