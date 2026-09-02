# -*- coding: utf-8 -*-
"""Secoes 23-25 do help, BILINGUES e geradas (2026-09-02).

    py -3.12 New_Theory/build_help_sections.py

Escreve `src/bolt_analysis_studio/resources/docs/help_sections.json`:

    23. Tipos de elemento e de ligacao   os 17 do enum, um por um
    24. Construir um modelo do zero      o fluxo real, com prints
    25. Dialogos e erros                 os 82 titulos de QMessageBox

Cada secao sai em PT e EN. O mecanismo e' o `Lang.tr` de gui/i18n.py, que
existia completo e SEM NENHUM consumidor; a aba Documentation passa a ser o
primeiro.

O que este gerador EXTRAI do codigo (e por isso nao envelhece calado):
  - `ElementType`: os 17 tipos. Tipo novo sem prosa = lacuna acusada.
  - `ELEMENT_VISUALS`: nome de paleta, simbolo, rigidez padrao e a descricao
    de uma linha. Tambem revela os 3 tipos que existem no modelo e NAO estao
    na paleta (MEMBER, THERMAL, BEAM_CONNECTOR).
  - `QMessageBox.*`: titulo E CORPO de cada dialogo, com arquivo e linha.

Profundidade PROPORCIONAL, declarada: falha (critical/warning) revisada ganha
causa e acao; informativo revisado ganha uma linha; e o que ainda nao foi
revisado sai com o TEXTO REAL da mensagem no fonte, marcado como extraido. Isso
da' cobertura 82/82 sem fingir analise onde nao houve.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))
if str(RAIZ / "New_Theory") not in sys.path:
    sys.path.insert(0, str(RAIZ / "New_Theory"))

SAIDA = RAIZ / "src" / "bolt_analysis_studio" / "resources" / "docs" / "help_sections.json"

_PAT_MSG = re.compile(
    r"QMessageBox\.(warning|critical|information|about|question)\s*\("
    r"\s*[^,]+,\s*[\"']([^\"']{3,60})[\"']\s*,\s*(?:f?[\"'])([^\"']{0,180})",
    re.S)


def _esc(t) -> str:
    return html.escape(str(t or ""), quote=False)


def extrai_dialogos() -> dict:
    """{titulo: {tipo, corpo, ocorrencias:[(arquivo, linha)]}} do codigo."""
    achados = {}
    for f in sorted((RAIZ / "src").rglob("*.py")):
        txt = f.read_text(encoding="utf-8", errors="replace")
        for m in _PAT_MSG.finditer(txt):
            tipo, titulo, corpo = m.group(1), m.group(2), (m.group(3) or "")
            linha = txt[:m.start()].count("\n") + 1
            e = achados.setdefault(titulo, {"tipo": tipo, "corpo": "",
                                            "ocorrencias": []})
            if len(corpo.strip()) > len(e["corpo"]):
                e["corpo"] = corpo.strip()
            e["ocorrencias"].append((f.relative_to(RAIZ).as_posix(), linha))
    return achados


def secao_elementos(lang: str) -> str:
    from bolt_analysis_studio.core.models.element import ElementType
    from bolt_analysis_studio.gui.msd_builder import ELEMENT_VISUALS
    from help_content import ELEMENTOS

    pt = lang == "pt"
    vis = {k.upper(): v for k, v in ELEMENT_VISUALS.items()}
    corpos = [e for e in ElementType
              if ELEMENTOS.get(e.name, {}).get("papel") != "ligacao"]
    ligas = [e for e in ElementType
             if ELEMENTOS.get(e.name, {}).get("papel") == "ligacao"]

    p = [f"<h2>23. {'Tipos de elemento e de ligacao' if pt else 'Element and connection types'}</h2>"]
    p.append("<p>" + (
        f"O modelo tem <b>{len(list(ElementType))} tipos</b>: "
        f"<b>{len(corpos)}</b> de corpo, que carregam massa e rigidez, e "
        f"<b>{len(ligas)}</b> de ligacao, que carregam a tribologia. A "
        f"distincao importa mais do que parece: <b>a perda de pre-carga "
        f"acontece nas ligacoes, nao nos corpos</b>. Rigidez padrao, nome de "
        f"paleta e simbolo abaixo saem do proprio codigo."
        if pt else
        f"The model has <b>{len(list(ElementType))} types</b>: "
        f"<b>{len(corpos)}</b> bodies, which carry mass and stiffness, and "
        f"<b>{len(ligas)}</b> connections, which carry the tribology. The "
        f"distinction matters more than it looks: <b>preload loss happens at "
        f"the connections, not in the bodies</b>. The default stiffness, "
        f"palette name and symbol below come from the code itself.") + "</p>")

    n = 0
    for grupo, titulo_pt, titulo_en in ((corpos, "Corpos", "Bodies"),
                                        (ligas, "Ligacoes", "Connections")):
        p.append(f"<h3>23.{'1' if grupo is corpos else '2'} "
                 f"{titulo_pt if pt else titulo_en}</h3>")
        for e in grupo:
            n += 1
            v = vis.get(e.name)
            info = ELEMENTOS.get(e.name)
            rotulo = getattr(v, "name", e.name.replace("_", " ").title())
            simb = getattr(v, "symbol", "")
            p.append(f"<h4>{_esc(simb)} {_esc(rotulo)} "
                     f"<span style='color:{{{{SUBTEXT}}}}'>"
                     f"<code>{e.name}</code></span></h4>")
            if v is not None:
                p.append(f"<p style='color:{{{{SUBTEXT}}}}'>"
                         + ("Paleta: " if pt else "Palette: ")
                         + f"<i>{_esc(getattr(v, 'description', ''))}</i> "
                         f"&middot; k = {getattr(v, 'default_k', 0):.3g} N/m"
                         f"</p>")
            else:
                p.append("<p style='color:{{PEACH}}'>" + (
                    "Existe no modelo e NAO esta' na paleta: nao da' para "
                    "arrasta-lo." if pt else
                    "Exists in the model and is NOT in the palette: it cannot "
                    "be dragged.") + "</p>")
            if info:
                for par in info["pt" if pt else "en"]:
                    p.append(f"<p>{par}</p>")
            else:
                p.append("<p style='color:{{RED}}'>" + (
                    "Sem texto revisado para este tipo." if pt else
                    "No reviewed text for this type.") + "</p>")
    return "\n".join(p)


def secao_do_zero(lang: str) -> str:
    from help_content import PASSOS

    pt = lang == "pt"
    p = [f"<h2>24. {'Construir um modelo do zero' if pt else 'Building a model from scratch'}</h2>"]
    p.append("<p>" + (
        "Sete passos, do wizard ao arquivo salvo. Esta secao nomeia as portas "
        "de entrada reais &mdash; o <i>New Analysis Wizard</i> e o MSD "
        "Builder &mdash; porque a maior parte do trabalho de montar uma junta "
        "esta' em nao esquecer as ligacoes."
        if pt else
        "Seven steps, from the wizard to the saved file. This section names "
        "the real entry points &mdash; the <i>New Analysis Wizard</i> and the "
        "MSD Builder &mdash; because most of the work of assembling a joint "
        "is in not forgetting the connections.") + "</p>")
    for i, passo in enumerate(PASSOS, 1):
        titulo, *paragrafos = passo["pt" if pt else "en"]
        p.append(f"<h3>24.{i} {titulo.split('. ', 1)[-1]}</h3>")
        for par in paragrafos:
            p.append(f"<p>{par}</p>")
        img = passo.get("print_")
        if img and (RAIZ / "src" / "bolt_analysis_studio" / "resources"
                    / "ui_reference" / f"{img}.png").is_file():
            p.append(f'<p><img src="ui_reference/{img}.png" width="820"></p>')
    return "\n".join(p)


def secao_dialogos(lang: str, dlgs: dict) -> tuple:
    from help_content import DIALOGOS, DIALOGOS_SIMPLES

    pt = lang == "pt"
    ORDEM = {"critical": 0, "warning": 1, "question": 2,
             "information": 3, "about": 4}
    NOME = {"critical": ("Erros criticos", "Critical errors"),
            "warning": ("Avisos", "Warnings"),
            "question": ("Perguntas de confirmacao", "Confirmation questions"),
            "information": ("Mensagens informativas", "Information messages"),
            "about": ("Sobre", "About")}

    revisados = extraidos = 0
    por_tipo = {}
    for titulo, info in dlgs.items():
        por_tipo.setdefault(info["tipo"], []).append((titulo, info))

    corpo = []
    for tipo in sorted(por_tipo, key=lambda t: ORDEM.get(t, 9)):
        itens = sorted(por_tipo[tipo])
        corpo.append(f"<h3>{NOME[tipo][0 if pt else 1]} ({len(itens)})</h3>")
        corpo.append("<table><tr>"
                     f"<th>{'Titulo na barra' if pt else 'Dialog title'}</th>"
                     f"<th>{'O que significa e o que fazer' if pt else 'What it means, and what to do'}</th>"
                     "</tr>")
        for titulo, info in itens:
            if titulo in DIALOGOS:
                revisados += 1
                t = DIALOGOS[titulo]["pt" if pt else "en"]
                celula = f"<b>{_esc(t[0])}</b><br>{_esc(t[1])}"
            elif titulo in DIALOGOS_SIMPLES:
                revisados += 1
                celula = _esc(DIALOGOS_SIMPLES[titulo][0 if pt else 1])
            else:
                extraidos += 1
                msg = info["corpo"] or ("(sem corpo fixo)" if pt
                                        else "(no fixed body)")
                celula = (f"<i>{_esc(msg)}</i><br>"
                          f"<span style='color:{{{{PEACH}}}}'>"
                          + ("Texto extraido do codigo; ainda sem analise "
                             "revisada." if pt else
                             "Text extracted from the source; not yet "
                             "reviewed.")
                          + "</span>")
            arq, lin = info["ocorrencias"][0]
            celula += (f"<br><span style='color:{{{{SUBTEXT}}}};"
                       f"font-size:{{{{FONT_SIZE_MICRO}}}}'>"
                       f"{_esc(arq)}:{lin}</span>")
            corpo.append(f"<tr><td><b>{_esc(titulo)}</b></td>"
                         f"<td>{celula}</td></tr>")
        corpo.append("</table>")

    cab = [f"<h2>25. {'Dialogos e erros' if pt else 'Dialogues and errors'}</h2>",
           "<p>" + (
        f"Os <b>{len(dlgs)} titulos de dialogo</b> que o programa pode "
        f"mostrar, extraidos do codigo com arquivo e linha. "
        f"<b>{revisados}</b> tem texto revisado; <b>{extraidos}</b> trazem a "
        f"mensagem como ela esta' no fonte, marcada como nao revisada &mdash; "
        f"cobertura completa, sem fingir analise onde nao houve. Um dialogo "
        f"novo no codigo aparece aqui automaticamente."
        if pt else
        f"The <b>{len(dlgs)} dialog titles</b> the program can show, "
        f"extracted from the source with file and line. <b>{revisados}</b> "
        f"have reviewed text; <b>{extraidos}</b> carry the message as it "
        f"stands in the source, marked as unreviewed &mdash; complete "
        f"coverage, without pretending to an analysis that was not done. A "
        f"new dialog in the code appears here automatically.") + "</p>"]
    return "\n".join(cab + corpo), revisados, extraidos


def build() -> tuple:
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    dlgs = extrai_dialogos()

    secoes = {}
    for chave, tit_pt, tit_en, fn in (
        ("element_types", "23. Tipos de elemento e de ligacao",
         "23. Element and Connection Types", secao_elementos),
        ("from_scratch", "24. Construir um modelo do zero",
         "24. Building a Model from Scratch", secao_do_zero),
    ):
        secoes[chave] = {
            "title": tit_en, "content": fn("en"),
            "title_pt": tit_pt, "content_pt": fn("pt"),
        }

    en, rev, ext = secao_dialogos("en", dlgs)
    pt, _r, _e = secao_dialogos("pt", dlgs)
    secoes["dialogues"] = {
        "title": f"25. Dialogues and Errors ({len(dlgs)})", "content": en,
        "title_pt": f"25. Dialogos e Erros ({len(dlgs)})", "content_pt": pt,
    }

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(secoes, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    return SAIDA, len(dlgs), rev, ext


def main(argv=None) -> int:
    alvo, n_dlg, rev, ext = build()
    d = json.loads(alvo.read_text(encoding="utf-8"))
    print(f"  {len(d)} secoes bilingues -> {alvo}  "
          f"({alvo.stat().st_size/1024:.0f} KB)")
    for v in d.values():
        print(f"    {v['title']:44s} EN {len(v['content'])/1024:5.1f} KB  "
              f"PT {len(v['content_pt'])/1024:5.1f} KB")
    print(f"  dialogos: {n_dlg} titulos, {rev} revisados, {ext} extraidos "
          f"({100*rev/max(n_dlg,1):.0f}% revisado)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
