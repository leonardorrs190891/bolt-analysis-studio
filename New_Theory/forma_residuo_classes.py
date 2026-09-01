"""QUAL FORMA FALTA? — classifica as curvas da fila pelo PERFIL do resíduo.

Atividade A pré-pipeline (2026-07-29). O item 1 (sensibilidade) mostrou que
**nenhuma alavanca existente** fecha a perna do σ_res, logo o pipeline tem de
propor FORMA. Este script responde *qual* forma, por dado em vez de intuição:
lê o resíduo assinado de cada curva da fila e o descreve por quatro
características independentes, que juntas dão a assinatura do defeito.

As quatro (todas sobre `e_i = modelo_i − dado_i` nos MESMOS pontos que a métrica
comparou, com o progresso normalizado `s_i ∈ [0,1]`):

  ONDE   em que terço o |resíduo| é máximo — INICIO / MEIO / FIM. Diz em que
         estágio o modelo se descola: assentamento, regime, ou colapso.
  DERIVA β = slope de e vs s. Sinal + = o modelo fica otimista no fim (retém
         mais que o dado); − = pessimista. Já é a métrica informacional §4.48a.
  SINAL  fração do resíduo acima de zero: 1,0 = o modelo mora ACIMA do dado
         (sub-prevê a perda), 0,0 = mora abaixo, ~0,5 = cruza.
  CURVA  o resíduo tem curvatura sistemática? (2ª diferença média com sinal, em
         unidades do próprio σ_res). Positiva = o modelo é "raso" no meio e o
         dado cava; negativa = o oposto. É o que distingue "constante errada"
         de "forma errada": erro de constante dá resíduo com deriva mas SEM
         curvatura sistemática.

A combinação (ONDE, sinal de β, SINAL, sinal de CURVA) é a assinatura. O script
agrupa as curvas por assinatura e conta — cluster grande = defeito compartilhado,
que é candidato a UMA forma nova, não a N ajustes.

SÓ-LEITURA. Run: py -3.12 New_Theory/forma_residuo_classes.py [--md]
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh  # noqa
from bolt_analysis_studio.validation.case_registry import all_records  # noqa

MD = "--md" in sys.argv
store = json.loads((ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
                    / "validation_store.json").read_text(encoding="utf-8"))
src = {r.case_id: r.source for r in all_records()}


def assina(cid, r):
    mp, md, mx = r.get("metric_pred"), r.get("metric_data"), r.get("metric_x")
    if not (mp and md and mx and len(mp) == len(md) == len(mx) >= 5):
        return None
    e = np.asarray(mp, float) - np.asarray(md, float)
    x = np.asarray(mx, float)
    s = ((x - x[0]) / (x[-1] - x[0])) if x[-1] > x[0] else np.linspace(0, 1, len(x))
    n = len(e)
    t = n // 3 or 1
    tercos = [np.max(np.abs(e[:t])), np.max(np.abs(e[t:2 * t] if n > 2 * t else e[t:])),
              np.max(np.abs(e[2 * t:]))]
    onde = ("INICIO", "MEIO", "FIM")[int(np.argmax(tercos))]
    beta = float(np.polyfit(s, e, 1)[0]) if np.ptp(s) > 0 else 0.0
    frac_pos = float(np.mean(e > 0))
    d2 = e[2:] - 2 * e[1:-1] + e[:-2]
    sd = float(np.std(e)) or 1e-12
    curva = float(np.mean(d2) / sd)
    # R2 DA TENDENCIA LINEAR — o discriminador que decide CONSTANTE vs FORMA.
    # `curva` (media da 2a diferenca) e' fraco por construcao: num residuo que
    # oscila ele CANCELA, e "reta" passa a significar duas coisas opostas
    # (linear de verdade, ou oscilando simetrico). O R2 do ajuste e ~ beta*s
    # separa: ALTO => o residuo e' DERIVA suave (falta termo monotono — taxa ou
    # constante); BAIXO => o residuo e' ONDULADO, e nenhuma constante o remove,
    # e' forma faltante de verdade. Como a perna que reprova e' o sigma_res
    # (dispersao), esta e' a pergunta operativa do pipeline.
    fit = np.polyval(np.polyfit(s, e, 1), s)
    ss_tot = float(np.sum((e - np.mean(e)) ** 2)) or 1e-18
    r2 = max(float(1.0 - np.sum((e - fit) ** 2) / ss_tot), 0.0)
    return dict(cid=cid, fonte=src.get(cid, "?"), onde=onde, beta=beta,
                fpos=frac_pos, curva=curva, sd=sd, n=n, r2=r2)


# fila de FORMA: fora do tripé, não exceção assinada, e violando o σ_res
fila = []
for cid, r in store.items():
    if src.get(cid) == "USER" or cid in rh._EXCECOES or not r.get("ok"):
        continue
    sd = r.get("resid_std")
    if r.get("mae") is None or sd is None or float(sd) <= rh.META_SRES:
        continue
    a = assina(cid, r)
    if a:
        fila.append(a)

print(f"fila de forma (violam σ_res, não são exceção, ≥5 pontos): {len(fila)}\n")


def rot(a):
    return (a["onde"],
            "β+" if a["beta"] > 0.01 else ("β−" if a["beta"] < -0.01 else "β0"),
            "acima" if a["fpos"] > 0.8 else ("abaixo" if a["fpos"] < 0.2 else "cruza"),
            "cava" if a["curva"] > 0.15 else ("infla" if a["curva"] < -0.15 else "reta"))


grupos = defaultdict(list)
for a in fila:
    grupos[rot(a)].append(a)

print("ASSINATURAS (onde · deriva · lado · curvatura) — cluster grande = defeito")
print("compartilhado, candidato a UMA forma nova:\n")
for k, v in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
    fontes = Counter(a["fonte"] for a in v)
    print(f"  {len(v):3d}  {' · '.join(k):34s} fontes: "
          + ", ".join(f"{s}×{c}" for s, c in fontes.most_common(4)))

print("\nDERIVA vs ONDULACAO — a pergunta operativa (R2 da tendencia linear):")
for lbl, lo, hi in (("DERIVA (R2>=0,7): falta termo monotono", 0.7, 1.01),
                    ("mista (0,3-0,7)", 0.3, 0.7),
                    ("ONDULADO (R2<0,3): nenhuma constante remove", -0.01, 0.3)):
    g = [z for z in fila if lo <= z["r2"] < hi]
    fon = Counter(z["fonte"] for z in g)
    print(f"  {len(g):3d}  {lbl:44s} "
          + ", ".join(f"{s2}x{c}" for s2, c in fon.most_common(4)))

print("\nMARGINAIS (cada característica isolada):")
for campo, f in (("onde", lambda a: a["onde"]),
                 ("deriva", lambda a: rot(a)[1]),
                 ("lado", lambda a: rot(a)[2]),
                 ("curvatura", lambda a: rot(a)[3])):
    c = Counter(f(a) for a in fila)
    print(f"  {campo:10s} " + " · ".join(f"{k} {v}" for k, v in c.most_common()))

print("\nOS 12 DE MAIOR σ_res, com a assinatura:")
print(f"  {'curva':42s} {'σ_res':>7s} {'onde':>6s} {'β':>8s} {'lado':>6s} {'R2':>5s}")
for a in sorted(fila, key=lambda z: -z["sd"])[:12]:
    print(f"  {a['cid'][:42]:42s} {a['sd']:7.4f} {a['onde']:>6s} "
          f"{a['beta']:+8.4f} {rot(a)[2]:>6s} {a['r2']:5.2f}")

if MD:
    p = ROOT / "New_Theory" / "forma_residuo_classes.md"
    L = ["# Qual forma falta — assinatura do resíduo na fila de forma", "",
         f"**Curvas:** {len(fila)} (violam σ_res, não são exceção assinada)", "",
         "| curva | fonte | σ_res | onde | β | lado | R2 linear |",
         "|---|---|--:|---|--:|---|--:|"]
    for a in sorted(fila, key=lambda z: -z["sd"]):
        r = rot(a)
        L.append(f"| `{a['cid']}` | {a['fonte']} | {a['sd']:.4f} | {a['onde']} "
                 f"| {a['beta']:+.4f} | {r[2]} | {a['r2']:.2f} |")
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nescrito: {p.relative_to(ROOT)}")
