# Pré-registro — ADOÇÃO per-rig LIU_2025: fadiga + rampa no config adotado

**Data:** 2026-07-28 · **Autorização:** professor (*"pré-registre a adoção per-rig do
LIU_2025"* + *"execute a adoção quando as contas fecharem"*)
**Capacidade base:** rampa mergeada em `f05a531` (gates 6/6, §4.51)
**Contas pré-congelamento:** `New_Theory/liu2025_adocao_contas.{py,log,json}` — RODADAS
**Status:** CONGELADO — a execução segue imediatamente (autorizada); gates IMUTÁVEIS.

> O residual de forma que esta adoção fecha está NOMEADO no verdict do próprio config
> adotado (PR-9b): *"cliff terminal = fratura (FatigueLoss precisa driver ~slip;
> candidato futuro)"*.

---

## 0. Cegueira — o que foi medido antes e o que decide os gates

**Medido pré-congelamento (contas):** `fat_Kt` da Table 2; `fat_C1` ancorado nas 6
vidas de fratura (2 passes, protocolo declarado no script ANTES de rodar); espalhamento
do relógio; tabela rampa-início vs trim; e a métrica pós-trim de **UMA** curva de
projeto (`amp0p4`). **Cego para os gates:** a métrica pós-trim das **outras 6 curvas**
(`amp0p25, amp0p3, amp0p5, amp0p6, amp0p8, fig2_single`) — os trajetos delas foram
descartados no script sem avaliar métrica — e tudo das 195 curvas de fora.

## 1. Receita congelada (nada é fitado na execução)

Bloco idêntico nas **3 chaves** adotadas (`LIU_2025`, `LIU_2025_amp0p4`,
`LIU_2025_amp0p5` — chaves standalone, sem herança):

```json
{"fatigue_enabled": true, "fat_stress_mode": "bending", "fat_Kt": 0.588,
 "fat_sigma_uts": 800e6, "fat_sigma_knee": 0.0, "fat_sigma_endurance": 1.0,
 "fat_m1": 3.12, "fat_C1": 4.02544e32, "fat_ramp_D_on": 0.75, "fat_ramp_q": 8.0}
```

| constante | valor | classe | origem |
|---|---|---|---|
| `fat_Kt` | **0,588** | per-rig (derivada de input-de-paper) | `c_σ`(Table 2, 1081 MPa/mm) / proxy de flexão **desta geometria de caso** (1838 MPa/mm) — σ_a passa a SER a tensão de raiz do artigo. *(0,588 ≠ o 2,4–2,5 do estudo porque o L_eff do caso ≠ grip nominal da Table 1 — Kt absorve a convenção; C1 é ancorado a jusante, comportamento invariante)* |
| `fat_m1` | 3,12 | medido-de-dados-do-paper | regressão N_frat × σ_root (R²(log) 0,9905) — pareamento NOSSO, declarado |
| `fat_C1` | **4,02544e32** | **fitado-this-rig (ÚNICO)** | ancorado nas 6 vidas de fratura, contexto canônico, **Goodman vivo**, 2 passes — **congelado aqui** |
| `fat_sigma_uts` | 800e6 | handbook | classe 8.8, d≤16 |
| `fat_ramp_D_on` | 0,75 | handbook | propagação = últimos 10–30 % da vida; N_D/N_f medido 0,72–0,80 |
| `fat_ramp_q` | 8,0 | per-rig (reuso) | par vencedor dos gates v2 — **sem refit** |
| knee=0 / endurance=1 Pa | — | forma | relógio de FRATURA é potência única (§3 do estudo); o joelho bilinear pertence ao N₉₅, emergente |

## 2. As contas (satisfazibilidade medida)

**Relógio (passe 2, C1 congelado):** N_pred/N_meas = 1,259 · 0,930 · 1,285 · 1,302 ·
1,361 · 0,734 — **pior caso ±36 %**, mais largo que os ±19 % da regressão estática
(efeito Goodman-vivo + trajetória). *Declarado: NÃO haverá 3º passe de C1 — o protocolo
do script fixou 2 passes antes de rodar; retunar agora seria mover a trave.*

**Rampa-início (0,75·N_pred) vs trim — o risco central, invertido pelo relógio:**

| curva | rampa@ | trim | posição |
|---|---:|---:|---|
| amp0p25 | 311 545 | 240 000 | fora |
| **amp0p3** | **174 321** | **180 000** | **DENTRO por 5 679 ciclos** |
| amp0p4 | 74 206 | 60 000 | fora *(curva de projeto: Δ medido = +0,0000/+0,0000)* |
| amp0p5 | 37 118 | 30 000 | fora |
| amp0p6 | 24 710 | 18 000 | fora |
| **amp0p8** | **7 931** | **11 500** | **DENTRO por 3 569 ciclos** |
| **fig2** *(analítico, δ=0,8 classe)* | ~7 931 | 8 000 | **DENTRO por ~69 ciclos** |

⇒ O gate cego A1 decide em **3 curvas com rampa dentro da janela da métrica**
(`amp0p3`, `amp0p8`, `fig2`) — nas demais a previsão é Δ≈0 como na curva de projeto.
Nota: o dado TAMBÉM cai nessas janelas (o joelho real está lá); o sinal do efeito é
indecidível a priori — é para isso que o gate existe.

## 3. GATES (imutáveis; execução imediata)

**A1 — tripé mantido e nenhuma curva pior (CEGO).** As 7 curvas LIU_2025, métrica
canônica pós-trim: **7/7 no tripé** E nenhuma piora **> +0,01 em MAE** (PR-37′).
**A2 — as 195 de fora não se movem.** Métricas idênticas (ignorando `generated_at` e
`engine_fingerprint`, que muda legitimamente com adoção).
**A3 — fingerprint novo e ÚNICO.** ≠ `4f5bedfbace4`, uniforme nos 203; store
re-carimbado inteiro numa re-simulação única.
**A4 — informacional (sem limiar):** res.máx full-curve por curva; decomposição com o
canal `fatigue` visível; report HTML regenerado; N₉₅/N_D emergentes.

### Interpretação pré-declarada

| resultado | ação |
|---|---|
| A1–A3 ✓ | adoção definitiva; **re-baselinar CLAUDE.md** (item 12 + fingerprint do Estado da meta) e o verdict do config |
| **A1 ✗** (qualquer curva) | **adoção REVERTIDA** (rollback do JSON + re-sim re-carimba de volta); capacidade fica; registrar a causa por curva (rampa-na-janela vs relógio) |
| A2 ✗ ou A3 ✗ | bug de execução; consertar sem reinterpretar |

## 4. O que NÃO está sendo proposto

- **Não** mexer em trims (metric-limited; linha fechada §4.48a) nem na métrica.
- **Não** re-fitar nada na execução (C1/q congelados; sem 3º passe).
- **Não** reivindicar precisão de vida: a claim é *"o estágio 3 existe por física no
  report/decomposição, dado um relógio ±36 %"* — não tripé, não N_f.
- **Não** tocar `LI_2022_TRIBOINT` (segue cliff) nem qualquer outra fonte.

## 5. Reprodutibilidade

```bash
py -3.12 New_Theory/liu2025_adocao_contas.py            # contas (ja rodadas)
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
py -3.12 New_Theory/liu2025_adocao_gates.py <backup>    # A1/A2/A3
python -m bolt_analysis_studio.validation.report        # HTML do store novo
```
