"""LINT DE DIGITALIZAÇÃO — acha dado ruim ANTES de o otimizador ajustar a ele.

Item 3 das melhorias de 2026-07-29. A §3b do report tornou a conferência
possível (figura do artigo ao lado da curva lida); isto torna a conferência
ESCALÁVEL: varre as 202 curvas e sinaliza o que um olho treinado sinalizaria.

Por que antes da campanha: ajustar o modelo a uma curva mal digitalizada é a pior
forma de overfitting, porque parece progresso — o MAE cai e o erro está no dado.

Os checks (todos sobre o CSV CRU, com as convenções de eixo da fonte aplicadas):
  X_NAO_CRESCE   x com passo <= 0 (ordem trocada ou duplicata)
  X_DUPLICADO    abscissa repetida
  POUCOS_PONTOS  menos de 6 pontos (σ_res e forma não significam nada)
  Y_FORA_FAIXA   F/F0 fora de [0, 1.2] DEPOIS de aplicar `csv_y_scale`
  Y0_ACIMA_DE_1  1º ponto > 1.05 — suspeito sempre (a normalização não é ali?)
  Y0_ABAIXO_DE_1 1º ponto < 0.95 FORA de cadeia de reaperto (nela é a física:
                 cada estágio parte do que sobrou do anterior)
  Y_SOBE         F/F0 sobe mais que 0.05 acima do máximo corrente (pré-carga não
                 se recupera sozinha) — legítimo só em cadeia de reaperto
  N_INCOMPATIVEL max(x) discorda do `n_cycles` do registry por mais de 3x
  METRIC_LIMITED degrau entre pontos vizinhos >= a tolerância inteira (0.10).
                 NÃO é defeito de digitalização: é a granularidade do dado
                 contra a régua. Ação = trim/re-digitalizar, não ajustar

Cada achado é uma SUSPEITA com número, não um veredicto: a saída diz o que
conferir na figura do artigo (§3b do report daquele caso).

SÓ-LEITURA. Run: py -3.12 New_Theory/digitalizacao_lint.py [--md]
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation.case_registry import all_records  # noqa
from bolt_analysis_studio.validation.inputs import load_full_curve  # noqa

TOL = 0.10          # a tolerância da régua do res.máx


def _em_cadeia(rec) -> bool:
    """O caso é estágio de uma cadeia de reaperto? Aí começar abaixo de 1 é a
    física, não erro de leitura. Pergunto ao runner (`_chain_of`), que é quem
    resolve isso de verdade — não ao nome do arquivo."""
    try:
        from bolt_analysis_studio.validation.runner import _chain_of
        return _chain_of(rec) is not None
    except Exception:                                          # noqa: BLE001
        return False
MD = "--md" in sys.argv


def checa(rec):
    """[(codigo, detalhe)] das suspeitas desta curva."""
    out = []
    csv = getattr(rec, "csv_path", None)
    if not csv:
        return [("SEM_CSV", "o caso não tem curva de referência (ratio final)")]
    try:
        x, y = load_full_curve(csv)
    except Exception as exc:                                  # noqa: BLE001
        return [("CSV_ILEGIVEL", f"{type(exc).__name__}: {exc}")]
    case = rec.validation_case
    esc = getattr(case, "csv_x_scale", 1.0) or 1.0
    off = getattr(case, "csv_x_offset", 0.0) or 0.0
    # `csv_y_scale` existe porque parte da biblioteca publica F/F0 em PORCENTO
    # (Liu 2020: 96.39..100.0 com y_scale=0.01). A 1ª versão deste lint não o
    # aplicava e acusou 9 curvas de Y_FORA_FAIXA que estão corretas — o defeito
    # era do lint, não do dado. Aplicar a convenção declarada é obrigatório em
    # TODO consumidor do CSV cru (gotcha do CLAUDE.md).
    yesc = getattr(case, "csv_y_scale", 1.0) or 1.0
    x = np.asarray(x, float)
    y = np.asarray(y, float) * yesc
    xs = np.clip((x - off) * esc, 0.0, None)
    n = len(xs)
    if n < 6:
        out.append(("POUCOS_PONTOS", f"{n} pontos"))
    d = np.diff(xs)
    if n > 1 and (d < 0).any():
        out.append(("X_NAO_CRESCE",
                    f"{int((d < 0).sum())} passo(s) negativo(s)"))
    if n > 1 and (d == 0).any():
        out.append(("X_DUPLICADO", f"{int((d == 0).sum())} repetição(ões)"))
    if (y < -1e-9).any() or (y > 1.2).any():
        out.append(("Y_FORA_FAIXA",
                    f"min {y.min():.3f} · max {y.max():.3f}"))
    # O 1º ponto: DOIS casos com significados opostos, e a 1ª versão os juntou.
    #  · abaixo de 1 é LEGÍTIMO em cadeia de reaperto (cada estágio parte da
    #    pré-carga que sobrou do anterior — `chain: retight` nos grupos
    #    adotados, F0 por estágio lido do 1º ponto). Dos 21 que a 1ª versão
    #    acusou, 9 eram estágios do LIU_2022_RETIGHT: o lint estava sinalizando
    #    física declarada.
    #  · ACIMA de 1 é suspeito em qualquer caso: se o artigo normaliza em F/F0,
    #    o 1º ponto não pode passar de 1 por mais que o ruído de leitura.
    if n and y[0] > 1.05:
        out.append(("Y0_ACIMA_DE_1",
                    f"1º ponto = {y[0]:.4f} — a normalização não é o 1º ponto?"))
    elif n and y[0] < 0.95 and not off and not _em_cadeia(rec):
        out.append(("Y0_ABAIXO_DE_1",
                    f"1º ponto = {y[0]:.4f} (fora de cadeia de reaperto)"))
    if n > 2:
        # recuperação real: quanto o y sobe acima do máximo JÁ VISTO antes dele
        acum = np.maximum.accumulate(y)
        sub = float(np.max(y - np.concatenate(([y[0]], acum[:-1]))))
        if sub > 0.05:
            out.append(("Y_SOBE", f"+{sub:.3f} acima do máximo corrente"))
    ncyc = getattr(case, "n_cycles", None)
    if ncyc and n and xs.max() > 0:
        raz = xs.max() / float(ncyc)
        if raz > 3 or raz < 1 / 3:
            out.append(("N_INCOMPATIVEL",
                        f"max(x)={xs.max():.0f} contra n_cycles={ncyc} "
                        f"({raz:.2f}×)"))
    if n > 1:
        salto = float(np.max(np.abs(np.diff(y))))
        if salto >= TOL:
            # NÃO é defeito de digitalização, e a 1ª versão deste lint o
            # classificou como tal: é a granularidade do DADO contra a régua.
            # Se o degrau entre dois pontos vizinhos já vale a tolerância
            # inteira, nenhuma curva de modelo pode passar entre eles — a curva
            # é METRIC-LIMITED (classe §4.48a), e a ação é rever o trim ou
            # re-digitalizar mais fino, não ajustar o modelo.
            out.append(("METRIC_LIMITED",
                        f"degrau máximo entre pontos vizinhos {salto:.3f} >= "
                        f"tolerância {TOL:.2f} — nenhum modelo passa entre eles"))
    return out


def main():
    recs = [r for r in all_records() if r.source != "USER"]
    achados, por_codigo = {}, Counter()
    por_fonte = defaultdict(int)
    for r in recs:
        f = checa(r)
        if f:
            achados[r.case_id] = (r.source, f)
            por_fonte[r.source] += 1
            for c, _ in f:
                por_codigo[c] += 1
    print(f"varridas {len(recs)} curvas · {len(achados)} com suspeita "
          f"({100 * len(achados) / max(len(recs), 1):.0f}%)\n")
    print("POR CÓDIGO:")
    for c, k in por_codigo.most_common():
        print(f"   {c:16s} {k:3d}")
    print("\nPOR FONTE (curvas com ao menos uma suspeita):")
    for s, k in sorted(por_fonte.items(), key=lambda kv: -kv[1]):
        print(f"   {s:22s} {k:3d}")
    print("\nDETALHE (ordenado por nº de suspeitas):")
    for cid, (src, f) in sorted(achados.items(),
                                key=lambda kv: (-len(kv[1][1]), kv[0])):
        print(f"\n  {cid}  [{src}]")
        for c, det in f:
            print(f"     {c:16s} {det}")
    if MD:
        p = ROOT / "New_Theory" / "digitalizacao_lint.md"
        L = ["# Lint de digitalização — suspeitas nas curvas de referência", "",
             f"**Varridas:** {len(recs)} · **com suspeita:** {len(achados)}",
             "", "> Cada linha é uma SUSPEITA com número, não veredicto. Confira",
             "> na §3b do report do caso (figura do artigo ao lado da curva).",
             "", "| curva | fonte | código | detalhe |", "|---|---|---|---|"]
        for cid, (src, f) in sorted(achados.items()):
            for c, det in f:
                L.append(f"| `{cid}` | {src} | **{c}** | {det} |")
        p.write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"\nescrito: {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
