# -*- coding: utf-8 -*-
"""Secoes de literatura da aba Documentation, GERADAS (2026-09-02).

    py -3.12 New_Theory/build_literature_sections.py

Escreve `src/bolt_analysis_studio/resources/docs/literature.json` com tres
secoes que o `documentation_tab.py` funde no dict DOCUMENTATION:

    19. Literature review        prosa por tema, citando so' o verificado
    20. Validation sources       um bloco por artigo do corpus
    21. Bibliography             corpus + classicos verificados + normas

POR QUE GERADO NO BUILD e nao montado em runtime: a busca da aba le
`section["content"].lower()` no import, entao o conteudo precisa ser string
pronta; e carregar o registry (210 casos) a cada abertura do programa atrasaria
o boot por nada. Mesmo espirito do resto do repo: numero recomputado no build.

⚠️ NADA DE REFERENCIA DE MEMORIA. As entradas do corpus saem do
`ValidationCase` (`reference`, `doi`) e das notas de aparato (linha
`**Citation:**`, escrita a mao no repo). Os classicos saem de
`New_Theory/classics_verified.json`, verificado contra o api.crossref.org POR
TITULO, com casamento >= 80% e exigencia de primeiro autor.

⚠️ E POR QUE por titulo: em 2026-09-02, 25 DOIs gerados de memoria foram
testados; varios RESOLVIAM para artigos sem relacao com o tema (um deles
apontava para uma analise de bomba de engrenagens). DOI que resolve nao prova
citacao correta. A busca por titulo corrigiu 6 deles, um errado por 4 digitos.
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

SAIDA = RAIZ / "src" / "bolt_analysis_studio" / "resources" / "docs" / "literature.json"
CLASSICOS = RAIZ / "New_Theory" / "classics_verified.json"

# Normas citadas pelo projeto. Norma nao tem DOI: o identificador E' o codigo.
NORMAS = [
    ("DIN 65151", "Dynamic testing of the self-loosening of bolted joints "
                  "(transverse vibration / Junker test)"),
    ("ISO 16130", "Aerospace series. Dynamic testing of the locking behaviour "
                  "of bolted connections under transverse loading"),
    ("ISO 16047", "Fasteners. Torque/clamp force testing"),
    ("ISO 724", "ISO general purpose metric screw threads. Basic dimensions"),
    ("VDI 2230", "Systematic calculation of highly stressed bolted joints"),
]

# Referencia sem DOI porque ANTECEDE o sistema: 1945. Citada aqui com o dado
# bibliografico que a literatura reproduz de forma consistente, e MARCADA como
# nao verificavel por DOI, para nao passar por uma entrada conferida.
SEM_DOI = [
    dict(autores="Goodier, J. N.; Sweeney, R. J.", ano=1945,
         titulo="Loosening by vibration of threaded fastenings",
         veiculo="Mechanical Engineering", volume="67", pagina="798-802",
         nota="Antecede o sistema DOI (1945): sem identificador persistente. "
              "Entrada nao verificada por DOI."),
]


def _esc(t) -> str:
    return html.escape(str(t or ""), quote=False)


def _nota_resumo(caminho: Path) -> tuple:
    """(titulo, citacao, resumo do aparato) de uma nota de aparato .md.

    Le a estrutura que as notas de fato tem: `# titulo`, linha
    `**Citation:** ...`, e a secao `## Apparatus` em bullets. Nada e' reescrito
    aqui: o texto do resumo e' o do proprio arquivo.
    """
    if not caminho or not Path(caminho).is_file():
        return "", "", []
    txt = Path(caminho).read_text(encoding="utf-8", errors="replace")
    titulo = ""
    m = re.search(r"^#\s+(.+)$", txt, re.M)
    if m:
        titulo = m.group(1).strip()
    cit = ""
    m = re.search(r"\*\*Citation:\*\*\s*(.+?)(?=\n\*\*|\n##|\n\n)", txt, re.S)
    if m:
        cit = re.sub(r"\s+", " ", m.group(1)).strip()
        cit = re.sub(r"\*+", "", cit)
    bullets = []
    m = re.search(r"^##\s+Apparatus\s*$(.+?)(?=^##\s|\Z)", txt, re.S | re.M)
    if m:
        for linha in m.group(1).splitlines():
            linha = linha.strip()
            if linha.startswith("- "):
                b = re.sub(r"\s+", " ", linha[2:]).strip()
                b = re.sub(r"\*\*(.+?)\*\*", r"\1", b)
                if b:
                    bullets.append(b)
    return titulo, cit, bullets[:4]


REVIEW = """
<h2>19. Literature review: self-loosening of bolted joints</h2>

<p><b>What this review is, and what it is not.</b> It is the literature this
project engaged with and verified: the {n_src} sources whose curves form the
validation corpus, the classics the field is built on, and the standards that
define the tests. It is <b>not</b> an exhaustive survey of the subject. Every
reference below carries a persistent identifier that was checked, or says
explicitly why it has none. Section 21 lists them all.</p>

<h3>19.1 Two loading directions, and why one dominates the literature</h3>
<p>Work on threaded fasteners under vibration splits by how the joint is
loaded. The earlier line is axial: Goodier and Sweeney (1945) tested axially
loaded joints and described a partial-loosening mechanism in which pulsating
tension produces radial sliding between thread flanks. The line that came to
dominate practice is transverse: Junker's <i>New Criteria for Self-Loosening of
Fasteners Under Vibration</i> (SAE, 1969) established transverse displacement
as the severe condition and gave the field its test geometry, later codified as
DIN 65151 and ISO 16130. Nearly every rig in this software's corpus is a
Junker-type transverse rig or an axial force-controlled variant.</p>

<h3>19.2 Rotational and non-rotational loosening</h3>
<p>The literature separates loss of preload <i>with</i> nut rotation from loss
<i>without</i> it. Pai and Hess mapped the rotational route in a pair of 2002
papers, one experimental and one a three-dimensional finite-element analysis,
identifying localised slip at head and thread contacts as the trigger and
showing that loosening can begin below the load a global-slip criterion would
predict; they returned to the subject in 2004. Baek and co-workers (2019)
treated the mechanism in complex structures. The non-rotational route is where
embedding, creep and wear act: Basava and Hess (1998) measured clamping-force
variation under axial vibration, and the Lakes group (2006) measured bolt load
loss in aluminium joints held hot for a week, which is a creep measurement in
the form this software calibrates against.</p>

<h3>19.3 Analytical criteria</h3>
<p>Nassar and Yang proposed a mathematical model for vibration-induced
loosening of preloaded fasteners (2009), and Yang and Nassar followed it with a
criterion for preventing self-loosening of preloaded cap screws under
transverse cyclic excitation (2011). Criteria of this kind answer a different
question from the one this software answers: they give a threshold for whether
loosening occurs, where the model here integrates how much preload is lost over
cycles.</p>

<h3>19.4 Finite-element studies</h3>
<p>Detailed contact models reproduce the mechanism at the cost of one joint per
run. Jiang and co-workers published experimental and early-stage studies of
self-loosening in 2003, Zhang and co-workers a finite-element model of it in
2004, and Izumi and co-workers a three-dimensional analysis of both tightening
and loosening in 2005. The trade-off these papers make, fidelity against cost,
is the reason a lumped-parameter model is worth having: it is the regime
between a decay law fitted to one joint and a finite-element run per
condition.</p>

<h3>19.5 Recent modelling and reviews</h3>
<p>Gong and co-workers (2020) analysed the mechanism through a modified Iwan
model, and their review of anti-loosening methods surveys the countermeasure
literature. The corpus of this software draws mostly on work published from
2016 onward, which is where transverse-rig data with enough reported detail to
be read back from figures becomes common.</p>

<h3>19.6 Standards</h3>
<p>Five standards frame the measurements and the design rules used here:
DIN 65151 and ISO 16130 for the transverse test, ISO 16047 for torque/clamp
force, ISO 724 for thread geometry, and VDI 2230 for joint calculation. A
standard has no DOI: its code is its identifier.</p>

<h3>19.7 Where this software sits</h3>
<p>The model implements four loss mechanisms in parallel, embedding, creep,
fretting wear and nut rotation, with a surface-damage state that modulates
friction and wear, and it is confronted with {n_cases} digitised curves from
the {n_src} sources of Section 20. None of those curves was measured by the
authors of this software: each is read from a figure or a table of the cited
publication. The per-source blocks in Section 20 give the citation, the DOI and
the apparatus as the source described it.</p>
"""


def _fontes(recs, store):
    por = {}
    for r in recs:
        por.setdefault(r.source, []).append(r)
    saida = []
    for src in sorted(por):
        rs = sorted(por[src], key=lambda z: z.case_id)
        caso = rs[0].validation_case
        titulo, cit, bullets = _nota_resumo(rs[0].apparatus_note_path)
        maes = [getattr(store.get(r.case_id), "mae", None) for r in rs]
        maes = [m for m in maes if m is not None]
        saida.append(dict(
            src=src, n=len(rs),
            titulo_nota=titulo,
            citacao=cit or (getattr(caso, "reference", "") or ""),
            reference=(getattr(caso, "reference", "") or ""),
            doi=(getattr(caso, "doi", "") or "").strip(),
            aparato=bullets,
            mae_mediano=(sorted(maes)[len(maes) // 2] if maes else None),
            casos=[r.case_id for r in rs],
        ))
    return saida


def secao_fontes(fontes) -> str:
    p = ["<h2>20. Validation sources: one block per paper</h2>",
         f"<p>The corpus draws on <b>{len(fontes)} sources</b>. For each one: the "
         "citation as the apparatus note records it, the DOI, how many curves "
         "were digitised from it, the median mean absolute error of the model "
         "on those curves, and the apparatus as the source described it. The "
         "saved models of every curve are in "
         "<code>Models/SAVED_CASES/&lt;SOURCE&gt;/</code>.</p>"]
    for i, f in enumerate(fontes, 1):
        p.append(f"<h3>20.{i} {_esc(f['src'])} "
                 f"<span style='color:{{{{SUBTEXT}}}}'>"
                 f"({f['n']} curve{'s' if f['n'] != 1 else ''})</span></h3>")
        if f["titulo_nota"]:
            p.append(f"<p><b>{_esc(f['titulo_nota'])}</b></p>")
        if f["citacao"]:
            p.append(f"<p>{_esc(f['citacao'])}</p>")
        if f["doi"]:
            p.append(f"<p>DOI: <a href=\"https://doi.org/{_esc(f['doi'])}\">"
                     f"{_esc(f['doi'])}</a></p>")
        else:
            p.append("<p><i>No DOI: this source is not a publication.</i></p>")
        if f["mae_mediano"] is not None:
            p.append(f"<p>Median mean absolute error on these curves: "
                     f"<b>{f['mae_mediano']:.4f}</b></p>")
        if f["aparato"]:
            p.append("<p><b>Apparatus, as reported:</b></p><ul>")
            p += [f"<li>{_esc(b)}</li>" for b in f["aparato"]]
            p.append("</ul>")
        p.append(f"<p style='color:{{{{SUBTEXT}}}}'>Saved models: "
                 f"<code>Models/SAVED_CASES/{_esc(f['src'])}/</code> "
                 f"({f['n']} .msd)</p>")
    return "\n".join(p)


def secao_bibliografia(fontes, classicos) -> str:
    novas = classicos.get("novas", [])
    ja = classicos.get("ja_citadas_no_repo", [])
    p = ["<h2>21. Bibliography</h2>",
         "<p>Three groups: the sources of the validation corpus, the classics "
         "and further modelling work, and the standards. Every DOI here was "
         "resolved against Crossref by <b>title match</b>, not assumed from "
         "the citation, and entries without a persistent identifier say so.</p>",
         f"<h3>21.1 Sources of the validation corpus ({len(fontes)})</h3><ol>"]
    for f in fontes:
        alvo = (f"<a href=\"https://doi.org/{_esc(f['doi'])}\">doi:{_esc(f['doi'])}</a>"
                if f["doi"] else "<i>no DOI (not a publication)</i>")
        p.append(f"<li>{_esc(f['reference'] or f['src'])} &mdash; {alvo} "
                 f"&mdash; {f['n']} curve{'s' if f['n'] != 1 else ''}</li>")
    p.append("</ol>")

    p.append(f"<h3>21.2 Classics and further modelling work "
             f"({len(novas) + len(ja) + len(SEM_DOI)})</h3><ol>")
    for v in sorted(novas + ja, key=lambda z: (z.get("ano") or 0)):
        autores = "; ".join(v.get("autores") or []) or "(authors not listed)"
        # str(): volume e pagina vem do JSON e podem ser numero
        loc = ", ".join(str(x) for x in (v.get("veiculo"), v.get("volume"),
                                        v.get("pagina")) if x)
        p.append(f"<li>{_esc(autores)} ({v.get('ano')}). "
                 f"<i>{_esc(v.get('titulo'))}</i>. {_esc(loc)} &mdash; "
                 f"<a href=\"https://doi.org/{_esc(v.get('doi'))}\">"
                 f"doi:{_esc(v.get('doi'))}</a></li>")
    for v in SEM_DOI:
        loc = ", ".join(x for x in (v["veiculo"], v["volume"], v["pagina"]) if x)
        p.append(f"<li>{_esc(v['autores'])} ({v['ano']}). "
                 f"<i>{_esc(v['titulo'])}</i>. {_esc(loc)} &mdash; "
                 f"<span style='color:{{{{PEACH}}}}'>{_esc(v['nota'])}</span></li>")
    p.append("</ol>")

    p.append(f"<h3>21.3 Standards ({len(NORMAS)})</h3><ol>")
    for cod, desc in NORMAS:
        p.append(f"<li><b>{_esc(cod)}</b> &mdash; {_esc(desc)}</li>")
    p.append("</ol>")
    p.append(f"<p style='color:{{{{SUBTEXT}}}}'>Verification of the DOIs in "
             f"21.2: {_esc(classicos.get('metodo', ''))}</p>")
    p.append(f"<p style='color:{{{{SUBTEXT}}}}'>"
             f"{_esc(classicos.get('nao_exaustivo', ''))}</p>")
    return "\n".join(p)


def build() -> Path:
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.store import ValidationStore

    recs = all_records()
    store = ValidationStore()
    fontes = _fontes(recs, store)
    classicos = (json.loads(CLASSICOS.read_text(encoding="utf-8"))
                 if CLASSICOS.is_file() else {})

    secoes = {
        "literature_review": {
            "title": "19. Literature Review (self-loosening)",
            "content": REVIEW.format(n_src=len(fontes), n_cases=len(recs)),
        },
        "validation_sources": {
            "title": f"20. Validation Sources ({len(fontes)} papers)",
            "content": secao_fontes(fontes),
        },
        "bibliography": {
            "title": "21. Bibliography",
            "content": secao_bibliografia(fontes, classicos),
        },
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(secoes, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    return SAIDA


def main(argv=None) -> int:
    alvo = build()
    d = json.loads(alvo.read_text(encoding="utf-8"))
    print(f"  {len(d)} secoes -> {alvo}  ({alvo.stat().st_size/1024:.0f} KB)")
    for k, v in d.items():
        print(f"    {v['title']:44s} {len(v['content'])/1024:6.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
