"""Gera o PDF do documento de explicação do projeto.

Fluxo: concatena os capítulos .md em ordem → converte para HTML estilizado
(print CSS) → imprime em PDF com Chrome headless.

Uso:
    python build_pdf.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).parent
CHROME = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
OUT_HTML = HERE / "TechStorePlus_Explicacao_Completa.html"
OUT_PDF = HERE.parent / "TechStorePlus_Explicacao_Completa.pdf"

CHAPTERS = sorted(HERE.glob("[0-9][0-9]-*.md"))

CSS = """
@page { size: A4; margin: 22mm 18mm; }
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  font-family: 'Segoe UI', Calibri, Arial, sans-serif;
  font-size: 11pt; line-height: 1.55; color: #1a1a2e;
  max-width: 100%; margin: 0;
}
h1 {
  font-size: 21pt; color: #16325c; border-bottom: 3px solid #2e6fd0;
  padding-bottom: 6px; margin-top: 0; page-break-before: always;
}
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 15pt; color: #1f4e96; margin-top: 1.6em; page-break-after: avoid; }
h3 { font-size: 12.5pt; color: #2a5aa8; page-break-after: avoid; }
p { text-align: justify; }
blockquote {
  background: #f0f6ff; border-left: 4px solid #2e6fd0;
  margin: 1em 0; padding: 8px 14px; border-radius: 0 6px 6px 0;
  page-break-inside: avoid;
}
blockquote p { text-align: left; margin: 4px 0; }
pre {
  background: #f6f8fa; border: 1px solid #d5dbe3; border-radius: 6px;
  padding: 10px 12px; overflow-x: hidden; white-space: pre-wrap;
  word-wrap: break-word; font-size: 8.6pt; line-height: 1.45;
  page-break-inside: avoid;
}
code {
  font-family: Consolas, 'Courier New', monospace; font-size: 9pt;
  background: #eef1f5; padding: 1px 4px; border-radius: 3px;
}
pre code { background: none; padding: 0; font-size: 8.6pt; }
table {
  border-collapse: collapse; width: 100%; margin: 1em 0;
  font-size: 9.5pt; page-break-inside: avoid;
}
th { background: #16325c; color: #fff; padding: 6px 9px; text-align: left; }
td { border: 1px solid #c9d2dd; padding: 5px 9px; vertical-align: top; }
tr:nth-child(even) td { background: #f4f7fb; }
hr { border: none; border-top: 1px solid #c9d2dd; margin: 2em 0; }
strong { color: #14213d; }
.cover {
  page-break-after: always; text-align: center; padding-top: 220px;
}
.cover h1 { border: none; page-break-before: avoid; font-size: 30pt; }
.cover .subtitle { font-size: 15pt; color: #445; margin-top: 12px; }
.cover .meta { margin-top: 160px; color: #667; font-size: 10.5pt; line-height: 1.9; }
.toc { page-break-after: always; }
.toc h1 { page-break-before: avoid; }
.toc ul { list-style: none; padding-left: 0; font-size: 11.5pt; line-height: 2.0; }
.toc ul ul { padding-left: 22px; font-size: 10.5pt; line-height: 1.8; }
"""

COVER = """
<div class="cover">
  <h1>TechStore Plus</h1>
  <div class="subtitle">A Jornada de um Atendente Virtual Inteligente</div>
  <div class="subtitle" style="font-size:12pt; margin-top:24px;">
    Explicação completa do projeto — semanas 1 a 9<br>
    escrita para quem não é da área de programação
  </div>
  <div class="meta">
    Bruno Conte Pieri<br>
    Programa DevOps / ML Serving — Pluralit<br>
    Julho de 2026
  </div>
</div>
"""

TOC = """
<div class="toc">
<h1>Sumário</h1>
<ul>
  <li><strong>Introdução</strong> — a história, como ler, conceitos fundamentais</li>
  <li><strong>PARTE I — Módulo 1: O Nascimento do Atendente</strong>
    <ul>
      <li>Capítulo 1 · Semana 1 — Conversando com a IA do jeito mais direto</li>
      <li>Capítulo 2 · Semana 2 — A linha de montagem (LangChain LCEL)</li>
      <li>Capítulo 3 · Semana 3 — Memória de longo prazo e mãos para trabalhar</li>
      <li>Capítulo 4 · Desafio M1 — Do laboratório para o ar</li>
    </ul>
  </li>
  <li><strong>PARTE II — Módulo 2: O Atendente que Estuda (RAG)</strong>
    <ul>
      <li>Capítulo 5 · Semana 4 — Ensinando o atendente a consultar documentos</li>
      <li>Capítulo 6 · Semana 5 — Afinando a biblioteca (otimização do RAG)</li>
      <li>Capítulo 7 · Semana 6 — A biblioteca à prova de produção (desafio M2)</li>
    </ul>
  </li>
  <li><strong>PARTE III — Módulo 3: O Atendente que Raciocina em Etapas</strong>
    <ul>
      <li>Capítulo 8 · Semana 7 — Abrindo a caixa-preta: o fluxo desenhado à mão</li>
      <li>Capítulo 9 · Semana 8 — Do agente único à central de especialistas</li>
      <li>Capítulo 10 · Semana 9 — A equipe supervisionada (desafio M3)</li>
    </ul>
  </li>
  <li><strong>Conclusão</strong> — a linha do tempo e os cinco princípios</li>
  <li><strong>Glossário</strong> — todos os termos técnicos, sem jargão</li>
  <li><strong>Apêndice</strong> — mapa de repositórios e arquivos</li>
</ul>
</div>
"""


def build() -> None:
    md = markdown.Markdown(extensions=["tables", "fenced_code"])
    bodies = []
    for chapter in CHAPTERS:
        text = chapter.read_text(encoding="utf-8")
        bodies.append(md.reset().convert(text))

    html = (
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<title>TechStore Plus — Explicação Completa do Projeto</title>"
        f"<style>{CSS}</style></head><body>"
        + COVER + TOC + "\n".join(bodies) + "</body></html>"
    )
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"HTML: {OUT_HTML} ({len(html) // 1024} KB)")

    subprocess.run(
        [
            str(CHROME), "--headless", "--disable-gpu",
            f"--print-to-pdf={OUT_PDF}", "--no-pdf-header-footer",
            str(OUT_HTML.as_uri()),
        ],
        check=True, capture_output=True, timeout=180,
    )
    size_kb = OUT_PDF.stat().st_size // 1024
    print(f"PDF:  {OUT_PDF} ({size_kb} KB)")


if __name__ == "__main__":
    sys.exit(build())
