# Rampa de fratura como capacidade do engine — EXECUTADO. Todos os gates passam.

**Data:** 2026-07-28 · **Prereg:** `specs/2026-07-28-ramp-capability-prereg.md` (congelado em `ea028ef`)
**Autorização:** professor, *"execute o prereg da rampa"*
**Resultado:** capacidade **implementada e mergeada** — a única física que faltava para o
software gerar a curva em S completa do Liu 2025 (estudo `liu2025_estudo_curvas.md` §4).

---

## 0. Veredicto

| gate | resultado |
|---|---|
| **P0** inércia total (203 casos re-simulados) | **OK — bit-idêntico** (0 divergências fora `generated_at`) |
| **P1** paridade com a sonda A1 | **OK — EXATA**: 0,00 ciclos de delta nos **20 cruzamentos** (4 casos × 5 níveis) |
| **P2** cliff adotado não se move | **OK** — `LI_2022_TRIBOINT` 4/4 idêntico campo a campo |
| **P3** conservação | **OK** — residuais 0,148 / 0,089 / −0,151 / −0,017 J (≤ 0,2; idênticos à sonda) |
| **P4** curva em S no Run | **OK** — teste permanente `test_run_path_generates_s_curve_via_overrides` |
| **P5** informacional | medido (↓ §3) |
| **P6** nenhuma curva de fora piora | **OK** — Δ=0 exato nas 196 (mesma comparação do P0) |

Ramo pré-declarado: *"P0–P4, P6 ✓ ⇒ capacidade mergeável; adoção LIU_2025 vira decisão
seguinte."* Fingerprint segue `4f5bedfbace4` (a capacidade é default-inerte e nenhum config
adotado a liga). Meta segue **147/202** — como o prereg declarou, isto não é ganho de meta.

## 1. O que entrou no código

- **`JointMaterial`:** `fat_ramp_D_on = 1.0` (default = **sem rampa**, cliff intocado) e
  `fat_ramp_q = 5.0`. Comentário no código carrega a procedência (D_on handbook, N_D/N_f
  medido 0,72–0,80; §4.50 para o A-vs-B).
- **`FatigueLoss.rate`:** ramo opt-in antes do cliff — `A_eff/A_s = 1−((D−D_on)/(1−D_on))^q`,
  liberação série `g=(1−α)(1+ρ)/((1−α)+ρ)`, `dE = ΔU_internal` por incremento (mesma rota
  `W_diss_fracture` do cliff). Em rampa, `fatigue_residual_frac` não é lido (g(1)=0 ⇒ F₀→0).
- **Explorador de variáveis:** 2 `VarSpec` novos (bilíngues, grupo fatigue; sliders vivos —
  `test_non_negligible_sliders_are_live` passa).
- **Testes:** `tests/test_fatigue_ramp.py` — 8 testes: defaults inertes, semântica do cliff
  preservada com `D_on=1`, silêncio abaixo de `D_on`, descarga suave sem degrau, energética
  = ΔU, rampa vai a 0 (não ao `residual_frac`), S-curve integrada, e o P4 do Run.

## 2. Os números da paridade (P1) — o gate central

O `FatigueLoss` nativo, com relógio neutralizado (Goodman off) e ancorado (`N_f = N_f(paper)`),
reproduz a sonda A1 **ao ciclo**: os 20 cruzamentos dão delta **0,00**, e os quatro residuais
de conservação são os mesmos da sonda até o 4º dígito. A capacidade **é** a forma validada
nos gates v2 (10/10 no núcleo `amp0p4/0p5`), sem deriva de implementação.

## 3. P5 — o achado informacional que vira insumo da adoção

N₉₅ emergente do canônico (store) vs Fig. 4:

| δ (mm) | 0,25 | 0,30 | 0,40 | 0,50 | 0,60 | 0,80 |
|---|---:|---:|---:|---:|---:|---:|
| razão modelo/dado | 0,02 | 0,02 | 0,01 | 0,02 | 0,08 | **1,24** |

O assentamento do modelo canônico é **front-loaded**: cruza 0,95 em 23–391 ciclos onde o
dado leva 460–16 157 (exceto na amplitude alta, onde bate). Consistente com o fato de o
`N_emb` do config LIU_2025 ter sido calibrado em MAE pós-trim, não no cruzamento precoce.
**Não é gate** (leitura vertical no platô é mal-posta em N — a lição do dia); é o primeiro
número dessa fidelidade e um insumo para a adoção per-rig, se vier.

## 4. O que fica aberto (fila do professor)

1. **Adoção per-rig do LIU_2025** com fadiga+rampa ligadas: exige prereg próprio — `fat_C1`
   ancorado no N_f medido **no contexto canônico** (Goodman vivo ≈ 50 % de efeito, §3 do
   estudo), `fat_m1 ≈ 3,1` (regressão N_f × σ_root), `D_on` handbook, `q` per-rig. Os trims
   **permanecem** (metric-limited, linha fechada) — a adoção mudaria a decomposição e o
   report, não o tripé.
2. **`_CAP = 100000` do Run** — as curvas de 250k/330k ciclos ainda truncariam na GUI.
3. **Rótulo de procedência do `fat_m1 = 2,7`** do LI_2022_TRIBOINT (não rastreável ao artigo).

## 5. Reprodutibilidade

```bash
py -3.12 -m pytest tests/test_fatigue_ramp.py -q          # 8 testes da capacidade
py -3.12 New_Theory/ramp_capability_gates.py               # P1/P3/P5 (~3 min)
py -3.12 New_Theory/parallel_batch.py --workers 6 --store  # P0 (re-sim ~23 min)
py -3.12 New_Theory/ramp_p0_compare.py <backup.json>       # comparador P0/P2/P6
```
Resultados brutos: `ramp_capability_result.json` · `ramp_p0_batch.log`.
