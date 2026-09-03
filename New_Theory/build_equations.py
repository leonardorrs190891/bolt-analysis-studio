# -*- coding: utf-8 -*-
"""Equacoes da secao 10 do help, renderizadas como imagem (2026-09-02).

    py -3.12 New_Theory/build_equations.py

Escreve `src/bolt_analysis_studio/resources/equations/<nome>_{dark,light}.png`
e um manifesto JSON. O `documentation_tab` troca o sufixo conforme o tema
ativo.

POR QUE IMAGEM. As equacoes estavam escritas como texto num <div>, e o motor de
rich text do Qt nao tem matematica: `mu(N) = mu_0 + (mu_peak - mu_0)(1-e^(-N/N_1))`
sai com o expoente na linha e o indice como underscore. Com mathtext do
matplotlib — a MESMA tecnica que o repo ja' usa nas figuras do artigo — sai
tipografado, com fracao, expoente e indice no lugar.

DUAS VARIANTES DE COR, e nao uma transparente: o app tem 5 temas, e um glifo de
cor unica sobre fundo transparente ou fica invisivel no claro ou no escuro.
Foi exatamente o que quase aconteceu com o icone do instalador, e a licao
custou uma rodada. Aqui o build gera as duas e o display escolhe.

⚠️ AS EQUACOES SAO TRANSCRITAS do texto que ja' estava na secao 10, nao
derivadas nem inventadas: a fonte da fisica e' New_Theory/MODEL_MATH_REFERENCE.md
e o proprio conteudo da aba. Qualquer mudanca de formula e' mudanca de MODELO e
nao de estetica, e nao cabe a um gerador de figura.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

SAIDA = RAIZ / "src" / "bolt_analysis_studio" / "resources" / "equations"
MANIFESTO = (RAIZ / "src" / "bolt_analysis_studio" / "resources" / "docs"
             / "equations.json")

# (nome, latex, altura em polegadas). Transcritas da secao 10 da aba.
EQUACOES = [
    ("eq_motion",
     r"$[M]\{\ddot{x}\} + [C]\{\dot{x}\} + [K]\{x\} = \{F(t)\}$", 0.62),
    ("eq_k_bolt",
     r"$\dfrac{1}{k_{bolt}} = \dfrac{1}{k_{head}} + \dfrac{1}{k_{shank}}"
     r" + \dfrac{1}{k_{thread}}$", 0.95),
    ("eq_k_system",
     r"$k_{system} = \dfrac{k_{bolt}\,k_{member}}{k_{bolt} + k_{member}}$", 0.95),
    ("eq_phi",
     r"$\Phi = \dfrac{k_{bolt}}{k_{bolt} + k_{member}}$", 0.9),
    ("eq_friction",
     r"$\mu(N) = \mu_0 + (\mu_{peak}-\mu_0)\,(1-e^{-N/N_1})\,e^{-N/N_2}"
     r" + (\mu_{steady}-\mu_0)\,(1-e^{-N/N_3})$", 0.68),
    ("eq_mu_crit",
     r"$\mu_{crit} = \dfrac{p}{2\pi}\cdot"
     r"\dfrac{2\cos\alpha}{d_2 + 2\,r_{eff}\cos\alpha}$", 0.95),
    ("eq_t_pitch", r"$T_{pitch} = F_p\,\dfrac{p}{2\pi}$", 0.85),
    ("eq_t_thread",
     r"$T_{thread} = \mu_t\,F_p\,\dfrac{d_2}{2\cos\alpha}$", 0.9),
    ("eq_t_bearing", r"$T_{bearing} = \mu_b\,F_p\,r_{eff}$", 0.6),
    ("eq_margin",
     r"$\mathrm{Margin} = \dfrac{T_{thread} + T_{bearing}}{T_{pitch}}$", 0.95),
    ("eq_slip_bearing", r"$|F_{trans}| > \mu_{bearing}\,F_p$", 0.6),
    ("eq_slip_thread",
     r"$|F_{trans}| > \mu_{thread}\,F_p\,\cos\lambda$", 0.6),
]

# Cor do glifo por variante. Do tema, nao inventada: TEXT do escuro e do claro.
VARIANTES = {"dark": "#cdd6f4", "light": "#4c4f69"}


def build() -> tuple:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    SAIDA.mkdir(parents=True, exist_ok=True)
    feitos = {}
    for nome, latex, alt in EQUACOES:
        larguras = {}
        for var, cor in VARIANTES.items():
            fig = plt.figure(figsize=(6.6, alt), dpi=200)
            fig.patch.set_alpha(0.0)          # fundo transparente: a caixa do
            t = fig.text(0.5, 0.5, latex, ha="center", va="center",
                         color=cor, fontsize=15)   # help e' que da' a cor
            alvo = SAIDA / f"{nome}_{var}.png"
            fig.savefig(alvo, transparent=True, bbox_inches="tight",
                        pad_inches=0.06)
            plt.close(fig)
            larguras[var] = alvo.stat().st_size
        feitos[nome] = {"latex": latex, "bytes": larguras}
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTO.write_text(json.dumps(feitos, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    return feitos, SAIDA


def main(argv=None) -> int:
    feitos, pasta = build()
    total = sum(f.stat().st_size for f in pasta.glob("*.png")) / 1024
    print(f"  {len(feitos)} equacoes x {len(VARIANTES)} variantes "
          f"-> {pasta}  ({total:.0f} KB)")
    for nome in feitos:
        print(f"    {nome}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
