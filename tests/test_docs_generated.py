"""Secoes geradas da aba Documentation: literatura (19-21) e interface (22).

Escrito em 2026-09-02, com dois invariantes que valem mais que os outros:

1. NENHUM DOI nas secoes pode existir sem origem rastreavel — o corpus
   (`ValidationCase.doi`) ou `New_Theory/classics_verified.json`. No mesmo dia,
   25 DOIs gerados de memoria foram testados e varios RESOLVIAM para artigos
   sem relacao com o tema. DOI que resolve nao prova citacao correta, e um
   software que acompanha artigo submetido nao pode carregar bibliografia
   plausivel e falsa.

2. Todo <img> da secao 22 tem de apontar para arquivo que existe. Imagem
   quebrada num help e' pior que help sem imagem: parece que falta conteudo.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))

import pytest                                                    # noqa: E402

RECURSOS = RAIZ / "src" / "bolt_analysis_studio" / "resources"
DOCS = RECURSOS / "docs"


def _json(nome):
    arq = DOCS / nome
    if not arq.is_file():
        pytest.skip(f"{nome} ausente: rode o gerador correspondente")
    return json.loads(arq.read_text(encoding="utf-8"))


def test_secoes_de_literatura_existem_e_tem_conteudo():
    d = _json("literature.json")
    assert set(d) == {"literature_review", "validation_sources", "bibliography"}
    for chave, s in d.items():
        assert s["title"].strip(), chave
        assert len(s["content"]) > 2000, f"{chave} suspeitamente curta"


def test_secao_de_interface_existe_e_tem_conteudo():
    d = _json("ui_reference.json")
    assert set(d) == {"ui_reference"}
    assert len(d["ui_reference"]["content"]) > 2000


def test_todo_img_da_secao_22_aponta_para_arquivo_que_existe():
    d = _json("ui_reference.json")
    srcs = re.findall(r'<img src="([^"]+)"', d["ui_reference"]["content"])
    assert srcs, "a secao de interface nao tem uma unica imagem"
    faltando = [s for s in srcs if not (RECURSOS / s).is_file()]
    assert not faltando, f"{len(faltando)} imagens quebradas: {faltando[:5]}"


def test_toda_superficie_descrita_foi_capturada():
    """Uma entrada com prosa e sem print deixaria texto sobre uma tela que
    ninguem ve; o inverso deixaria print sem explicacao."""
    import build_ui_reference as bur

    d = _json("ui_reference.json")
    html = d["ui_reference"]["content"]
    descritas = {s[0] for s in bur.SUPERFICIES}
    nos_prints = {p.stem for p in (RECURSOS / "ui_reference").glob("*.png")}
    no_html = set(re.findall(r'<img src="ui_reference/([^."]+)\.png"', html))

    assert descritas <= nos_prints, f"sem print: {sorted(descritas - nos_prints)}"
    assert descritas == no_html, (
        f"descritas mas fora do HTML: {sorted(descritas - no_html)}; "
        f"no HTML mas nao descritas: {sorted(no_html - descritas)}")


def test_nenhum_doi_das_secoes_e_sem_origem():
    """O invariante central: cada DOI citado sai do corpus ou da lista
    verificada. Um DOI que nao esteja em nenhuma das duas foi inventado por
    alguem, e passaria por conferido."""
    from bolt_analysis_studio.validation.case_registry import all_records

    def norm(d):
        return d.lower().rstrip(".,);")

    permitidos = {norm(getattr(r.validation_case, "doi", "") or "")
                  for r in all_records()}
    permitidos.discard("")
    verif = RAIZ / "New_Theory" / "classics_verified.json"
    if verif.is_file():
        cj = json.loads(verif.read_text(encoding="utf-8"))
        for grupo in ("novas", "ja_citadas_no_repo"):
            permitidos |= {norm(v["doi"]) for v in cj.get(grupo, [])}

    d = _json("literature.json")
    citados = set()
    for s in d.values():
        citados |= {norm(x) for x in
                    re.findall(r"10\.[0-9]{4,}/[A-Za-z0-9./()_;-]+", s["content"])}
    orfaos = sorted(citados - permitidos)
    assert not orfaos, (
        f"{len(orfaos)} DOI sem origem no corpus nem na lista verificada: "
        f"{orfaos[:5]}")


def test_todo_artigo_do_corpus_com_doi_aparece_na_bibliografia():
    from bolt_analysis_studio.validation.case_registry import all_records

    d = _json("literature.json")
    bib = d["bibliography"]["content"].lower()
    fora = sorted({(getattr(r.validation_case, "doi", "") or "").strip().lower()
                   for r in all_records()} - {""} - {""})
    ausentes = [x for x in fora if x not in bib]
    assert not ausentes, f"{len(ausentes)} fontes do corpus fora da bibliografia"


def test_a_revisao_declara_que_nao_e_exaustiva():
    """Chamar de completa uma revisao que nao e' seria a mesma inexatidao que
    inventar DOI: o texto tem de dizer o que e'."""
    d = _json("literature.json")
    t = d["literature_review"]["content"].lower()
    assert "not" in t and "exhaustive" in t


def test_a_aba_de_documentacao_funde_as_secoes_geradas(qapp):
    from bolt_analysis_studio.gui.documentation_tab import DOCUMENTATION

    for chave in ("literature_review", "validation_sources", "bibliography",
                  "ui_reference"):
        assert chave in DOCUMENTATION, f"{chave} nao chegou a aba"
    # a busca da aba le content.lower() no dict inteiro: string, nao preguicoso
    for s in DOCUMENTATION.values():
        assert isinstance(s["content"], str)
