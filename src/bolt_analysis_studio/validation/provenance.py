# -*- coding: utf-8 -*-
"""Procedencia citavel de um caso da validacao (2026-09-02).

Mora no PACOTE e nao no script de build porque a citacao e' propriedade do
CASO, nao da geracao: quem salva um caso pela GUI e quem gera os 210 em lote
precisam da mesma string, e duas copias divergiriam no primeiro ajuste.

Os campos saem do `ValidationCase` (`reference`, `doi`, `reference_csv_path`) e
da nota de aparato do `CaseRecord`. Nada e' redigitado aqui. Medido em
2026-09-02: 210 de 210 casos tem `reference`; 206 tem DOI, e os 4 sem DOI nao
sao publicacao (3 UFU_LAB, medicao do proprio laboratorio, e 1 USER, exemplo
sintetico), por isso DIZEM o que sao em vez de deixar um campo vazio que se
leria como omissao.
"""
from __future__ import annotations

from pathlib import Path

from .inputs import repo_root

_SEM_DOI = {
    "UFU_LAB": ("Measurement made at the LTAD/FEMEC laboratory of the "
                "Universidade Federal de Uberlandia. Not a publication: no DOI."),
    "USER": ("Synthetic example shipped with the software to exercise the "
             "import path. Not experimental data: no DOI."),
}

_DIGITISED = ("The curve was DIGITISED from a figure of the publication above "
              "by the authors of Bolt Analysis Studio. It is not original "
              "data: the measurements belong to the original authors, and the "
              "terms are in DATA_LICENSE.md.")


def _rel(caminho) -> str:
    """Caminho relativo a raiz, em barras normais.

    Absoluto vazaria o diretorio da maquina de quem gerou para dentro de um
    arquivo que vai ao repositorio publico.
    """
    if not caminho:
        return ""
    try:
        return Path(caminho).resolve().relative_to(repo_root()).as_posix()
    except (ValueError, OSError):
        return Path(caminho).name


def citation_block(rec) -> str:
    """A procedencia que viaja dentro do .msd salvo.

    Diz tres coisas que um leitor do arquivo precisa saber e nao pode adivinhar:
    de onde veio a curva, que ela foi DIGITALIZADA (nao e' o dado original), e
    que as constantes sao a configuracao adotada do caso.
    """
    caso = rec.validation_case
    ref = (getattr(caso, "reference", "") or "").strip()
    doi = (getattr(caso, "doi", "") or "").strip()

    linhas = [
        f"Bolt Analysis Studio - validation case {rec.case_id}",
        "Model built from the ADOPTED configuration of this case.",
        "",
        "SOURCE OF THE EXPERIMENTAL CURVE",
    ]
    if ref:
        linhas.append(ref)
    if doi:
        linhas.append(f"DOI: {doi}  (https://doi.org/{doi})")
        linhas += ["", _DIGITISED]
    else:
        linhas.append(_SEM_DOI.get(rec.source, "Not a publication: no DOI."))

    # Censo do artigo: 205 dos 210. O predicado e' `caso_comparavel`, o MESMO
    # que o Apendice B usa para listar os de fora — nao uma regra paralela que
    # poderia divergir do manuscrito.
    try:
        from .report_html import caso_comparavel
        no_censo = bool(caso_comparavel(rec.source, rec.case_id))
    except Exception:                                        # noqa: BLE001
        no_censo = None
    if no_censo is True:
        linhas += ["", "PAPER CENSUS",
                   "In the census of the accompanying paper (205 of 210 "
                   "records)."]
    elif no_censo is False:
        linhas += ["", "PAPER CENSUS",
                   "NOT in the census of the accompanying paper. It is "
                   "simulated and published, but counted in no number of the "
                   "manuscript; the reason is in Appendix B of the software "
                   "annex."]

    csv_rel = _rel(getattr(caso, "reference_csv_path", None) or rec.csv_path)
    nota_rel = _rel(rec.apparatus_note_path)
    linhas += ["", "PROVENANCE", f"Source key      : {rec.source}"]
    if csv_rel:
        linhas.append(f"Digitised curve : {csv_rel}")
    if nota_rel:
        linhas.append(f"Apparatus notes : {nota_rel}")
    linhas.append("Adopted constants: New_Theory/adopted_configs.json")
    return "\n".join(linhas)
