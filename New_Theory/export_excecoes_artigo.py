# -*- coding: utf-8 -*-
"""Exporta as EXCECOES ASSINADAS para o artigo do professor (2026-08-07).

Gera em `New_Theory/artigo_excecoes/`:
  · `tabela_excecoes.tex` — tabela booktabs pronta para \\input{}
  · `excecoes.csv`        — os mesmos dados, legiveis por maquina
  · `README_artigo_excecoes.md` — procedencia (fingerprint, data, contagens)

Fonte de verdade: os MESMOS dicts e helpers do report mestre
(`_EXCECOES`/`_F5_EXCECOES`, `caso_no_documento`, `NICE`, store canonico).
Este script nao mantem lista propria — se uma assinatura for retratada pela
campanha, a proxima geracao reflete sozinha. A decisao do professor esta
registrada na secao `#sec-excecoes` do mestre e na memoria da sessao: as
excecoes sao material de publicacao, entao a prova assinada e' texto de
artigo, nao rodape.

Uso:  py -3.12 New_Theory/export_excecoes_artigo.py  [--out DIR]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh          # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

# Escape TeX: so' os especiais; acentos/pt-BR ficam em UTF-8 (compilar com
# LuaLaTeX/XeLaTeX — dito no README). Simbolos matematicos das provas viram
# macros para nao depender de fonte com glifo.
_TEX = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#",
        "$": r"\$", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "σ": r"$\sigma$", "Δ": r"$\Delta$", "≤": r"$\leq$", "≥": r"$\geq$",
        "×": r"$\times$", "→": r"$\rightarrow$", "⇒": r"$\Rightarrow$",
        "±": r"$\pm$", "µ": r"$\mu$", "μ": r"$\mu$"}


def tex_esc(t: str) -> str:
    return "".join(_TEX.get(c, c) for c in str(t))


def linhas_excecoes():
    """(rec, res, classe, prova) por excecao VIVA, ordenado por fonte."""
    st = ValidationStore()
    recs = all_records()
    out = []
    for r in sorted(recs, key=lambda x: (x.source, x.case_id)):
        if r.case_id not in rh._EXCECOES:
            continue
        if not rh.caso_no_documento(r.source, r.case_id):
            continue
        classe = ("replicas (F5)" if r.case_id in rh._F5_EXCECOES
                  else "prova de piso (F7)")
        out.append((r, st.get(r.case_id), classe, rh._EXCECOES[r.case_id]))
    return out


def build(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    itens = linhas_excecoes()
    if not itens:
        raise SystemExit("nenhuma excecao viva — nada a exportar")
    fps = sorted({res.engine_fingerprint for _, res, _, _ in itens
                  if res and res.engine_fingerprint})
    fp = fps[0] if len(fps) == 1 else "%d geracoes (re-simule!)" % len(fps)

    def _num(v):
        return "%.3f" % float(v) if isinstance(v, (int, float)) else "---"

    # ---- teto per-curve (2026-08-15, pergunta do professor; NADA adotado) --
    # Cota INFERIOR do MAE alcancavel com constantes POR CURVA (sonda
    # excecoes_teto_por_curva.md). "no teto" = nenhuma alavanca move;
    # "transfer" = cai per-curve mas as constantes nao compartilham.
    _teto_p = Path(__file__).resolve().parent / "excecoes_teto_result.json"
    _TETO = (json.loads(_teto_p.read_text(encoding="utf-8"))
             if _teto_p.exists() else {})

    def _teto(cid, res):
        e = _TETO.get(cid)
        if not isinstance(e, dict) or not e.get("valido"):
            return None, "nao medido"
        t = float(e["teto"][0])
        v = float(getattr(res, "mae", 0.0) or 0.0)
        return t, ("no teto" if t >= v - 5e-4 else "transfer")

    # ---- .tex -------------------------------------------------------------
    # f-strings aqui de proposito: comentario TeX comeca com '%', e num
    # %-format o "% S" de "% Store" e' lido como especificador invalido —
    # foi um crash real na 1a execucao.
    tex = [
        "% Tabela das excecoes assinadas — GERADA, nao editar a mao.",
        "% Regenerar: py -3.12 New_Theory/export_excecoes_artigo.py",
        f"% Store fingerprint: {fp} · gerada em {date.today().isoformat()}",
        "% Requer: \\usepackage{booktabs} e compilacao LuaLaTeX/XeLaTeX (UTF-8).",
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Curvas sob exce\c{c}\~ao assinada: casos em que o erro do "
        r"modelo cabe dentro da repetibilidade medida do pr\'oprio dado "
        r"(F5) ou do piso da fonte (F7) --- nenhum modelo determin\'istico "
        r"passaria o crit\'erio ali.}",
        r"\label{tab:excecoes}",
        r"\small",
        r"\begin{tabular}{lllllll}",
        r"\toprule",
        r"caso & fonte & classe & MAE & res.\ m\'ax & teto p/curva & "
        r"prova assinada \\",
        r"\midrule",
    ]
    for r, res, classe, prova in itens:
        t, tcl = _teto(r.case_id, res)
        teto_txt = ("=" if tcl == "no teto"
                    else _num(t) if t is not None else "---")
        tex.append("%s & %s & %s & %s & %s & %s & %s \\\\" % (
            tex_esc(r.case_id), tex_esc(rh.NICE.get(r.source, r.source)),
            tex_esc(classe),
            _num(res.mae if res and res.ok else None),
            _num(res.maxerr if res and res.ok else None),
            teto_txt,
            tex_esc(prova)))
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    (out_dir / "tabela_excecoes.tex").write_text("\n".join(tex),
                                                 encoding="utf-8")

    # ---- .csv -------------------------------------------------------------
    with (out_dir / "excecoes.csv").open("w", newline="",
                                         encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "fonte", "classe", "mae", "maxerr",
                    "resid_std", "teto_mae_per_curve", "teto_classe",
                    "prova_assinada", "fingerprint"])
        for r, res, classe, prova in itens:
            t, tcl = _teto(r.case_id, res)
            w.writerow([r.case_id, rh.NICE.get(r.source, r.source), classe,
                        getattr(res, "mae", None),
                        getattr(res, "maxerr", None),
                        getattr(res, "resid_std", None),
                        t, tcl, prova, fp])

    # ---- README de procedencia ---------------------------------------------
    n_f5 = sum(1 for _, _, c, _ in itens if c.startswith("replicas"))
    (out_dir / "README_artigo_excecoes.md").write_text(
        "# Excecoes assinadas — material do artigo\n\n"
        "Gerado em %s por `New_Theory/export_excecoes_artigo.py` a partir do\n"
        "store canonico (fingerprint `%s`).\n\n"
        "- **%d** excecoes vivas: %d por scatter de replicas (F5, assinada\n"
        "  2026-07-28) + %d por prova de piso (F7, assinada 2026-07-29).\n"
        "- A fonte de verdade e' `_EXCECOES` em `report_html.py` (uniao\n"
        "  F5+F7); este export NAO mantem lista propria.\n"
        "- `tabela_excecoes.tex` requer `booktabs` e LuaLaTeX/XeLaTeX.\n"
        "- Coluna `teto p/curva`: cota INFERIOR do MAE com constantes POR\n"
        "  CURVA (sonda 2026-08-15, `excecoes_teto_por_curva.md`; NADA\n"
        "  adotado). `=` = nenhuma alavanca move a curva, o vigente ja e' o\n"
        "  teto (form/data-limited); numero = cai per-curve mas as\n"
        "  constantes nao compartilham (transfer-limited).\n"
        "- A leitura de estatuto: excecao conta como RESOLVIDA, nunca como\n"
        "  no tripe (secao `#sec-excecoes` do report mestre).\n"
        % (date.today().isoformat(), fp, len(itens), n_f5, len(itens) - n_f5),
        encoding="utf-8")
    return {"n": len(itens), "n_f5": n_f5, "fp": fp, "dir": str(out_dir)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=ROOT / "New_Theory" / "artigo_excecoes")
    r = build(ap.parse_args().out)
    print("excecoes exportadas: %d (%d F5 + %d F7) | fingerprint %s" % (
        r["n"], r["n_f5"], r["n"] - r["n_f5"], r["fp"]))
    print("saida:", r["dir"])
