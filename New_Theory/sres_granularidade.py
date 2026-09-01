"""O sigma_res exigido e' ALCANCAVEL por curva lisa? — piso de granularidade.

Pergunta que decide o desenho do pipeline. A F7 provou um piso vindo da
REPETIBILIDADE (dado contra dado, entre replicas). Falta o outro piso, que e'
independente dele: a GRANULARIDADE do proprio dado.

Argumento: o modelo e' liso (a saida do engine e' uma trajetoria continua). Se o
dado publicado zigue-zagueia entre pontos vizinhos com amplitude s, nenhuma curva
lisa passa por todos — ela passa pelo meio, e o residuo alterna, o que produz
sigma_res ~ s/2 no MELHOR caso. Logo existe um piso de sigma_res imposto pela
rugosidade do dado, e ele nao tem nada a ver com a fisica do modelo.

Medida (sem premissa de forma): sigma_rug = desvio-padrao de
(dado - media_movel_3(dado)) nos MESMOS pontos que a metrica usa. E' a rugosidade
do dado contra a sua propria versao suavizada — o quanto ele nao e' liso.

Se sigma_rug > 0,025 numa curva, o limite do sigma_res e' INALCANCAVEL ali por
qualquer modelo liso, e a curva e' metric-limited, nao form-limited.
"""
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\leo_r\OneDrive\BPL\Analitical\BAS_V2")
sys.path.insert(0, str(ROOT / "src"))
from bolt_analysis_studio.validation import report_html as rh  # noqa
from bolt_analysis_studio.validation.case_registry import all_records  # noqa

LIM = rh.META_SRES
store = json.load(open(ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
                       encoding="utf-8"))
src = {r.case_id: r.source for r in all_records()}


def rug_movel(d):
    """1o ESTIMADOR (INGENUO, mantido so para exibir o vies): sigma do dado
    contra a propria media movel de 3.

    NAO use para concluir: ele conta CURVATURA como rugosidade. Uma curva lisa
    de joelho agudo — que e' a forma tipica desta biblioteca — ja da residuo
    contra a propria media movel, porque a media de 3 pontos "corta" a curva.
    Medido: por este estimador 19 das 51 violadoras pareciam inalcancaveis; pelo
    robusto abaixo, UMA. As curvas do LU_2024, que ele acusava com 0,05-0,10 de
    rugosidade, tem ruido real de 0,007-0,010."""
    y = np.asarray(d, float)
    if len(y) < 4:
        return None
    suav = np.convolve(y, np.ones(3) / 3.0, mode="same")
    suav[0], suav[-1] = (y[0] + y[1]) / 2, (y[-1] + y[-2]) / 2
    return float(np.std(y - suav))


def ruido_d2(d):
    """2o ESTIMADOR (o que vale): ruido por SEGUNDA DIFERENCA com MEDIANA.

    Para ruido iid, Var(y[i+1] - 2y[i] + y[i-1]) = 6*sigma^2, logo
    sigma = |d2| / sqrt(6). A MEDIANA (x1,4826 para consistencia gaussiana) e' o
    que separa ruido de curvatura: no joelho a 2a diferenca e' grande por
    curvatura, mas sao POUCOS pontos, e a mediana os ignora. E' a correcao que
    inverteu a conclusao deste estudo."""
    y = np.asarray(d, float)
    if len(y) < 5:
        return None
    d2 = y[2:] - 2 * y[1:-1] + y[:-2]
    return float(np.median(np.abs(d2)) / np.sqrt(6) * 1.4826)


linhas = []
for cid, r in store.items():
    if src.get(cid) == "USER" or not r.get("ok"):
        continue
    md = r.get("metric_data")
    sd = r.get("resid_std")
    if not md or sd is None:
        continue
    rug, ruido = rug_movel(md), ruido_d2(md)
    if rug is None or ruido is None:
        continue
    linhas.append((cid, src.get(cid, "?"), float(sd), ruido, rug,
                   cid in rh._EXCECOES))

# l = (cid, fonte, sigma_res, ruido_robusto, rug_movel, e_excecao)
viol = [l for l in linhas if l[2] > LIM and not l[5]]
print(f"curvas com vetores: {len(linhas)} · violam sigma_res e nao sao excecao: "
      f"{len(viol)}\n")
print("PISO DE GRANULARIDADE — quantas dessas o limite ja e' inalcancavel por")
print("qualquer curva LISA (rugosidade do proprio dado > limite):")
imposs = [l for l in viol if l[3] > LIM]   # l[3] = ruido ROBUSTO
print(f"   sigma_rug > {LIM}: {len(imposs)} de {len(viol)} "
      f"({100 * len(imposs) / max(len(viol), 1):.0f}%)")
meio = [l for l in viol if LIM / 2 < l[3] <= LIM]
print(f"   entre {LIM/2} e {LIM} (metade do orcamento gasta em rugosidade): "
      f"{len(meio)}")
print(f"   abaixo de {LIM/2} (o limite e' de fato do modelo): "
      f"{len(viol) - len(imposs) - len(meio)}")
print()
print("As 14 piores (sigma_res medido contra a rugosidade do dado):")
print(f"   {'curva':44s} {'sigma_res':>9s} {'rug':>8s} {'razao':>6s}")
for cid, s, sd, ru, mv, _e in sorted(viol, key=lambda z: -z[3])[:14]:
    print(f"   {cid[:44]:44s} {sd:9.4f} {ru:8.4f} {mv:8.4f}")
print()
por_fonte = defaultdict(lambda: [0, 0])
for cid, s, sd, ru, mv, _e in viol:
    por_fonte[s][1] += 1
    if ru > LIM:
        por_fonte[s][0] += 1
print("POR FONTE (inalcancaveis / violadoras):")
for s, (a, b) in sorted(por_fonte.items(), key=lambda kv: -kv[1][0]):
    if b:
        print(f"   {s:22s} {a:2d}/{b:2d}")
print()
rugs = sorted(l[3] for l in linhas)   # ruido robusto
print(f"rugosidade em TODAS as {len(linhas)} curvas: mediana "
      f"{st.median(rugs):.4f} · p75 {rugs[3*len(rugs)//4]:.4f} · "
      f"p90 {rugs[int(.9*len(rugs))]:.4f} · max {rugs[-1]:.4f}")
print(f"curvas cuja rugosidade sozinha ja passa de {LIM}: "
      f"{sum(1 for v in rugs if v > LIM)} de {len(rugs)}")
