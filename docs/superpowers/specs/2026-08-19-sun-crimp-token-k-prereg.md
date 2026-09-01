# PREREG — `sun…grease_crimp`: o k do kernel cinemático da IRMÃ estende à crimp — ZERO número novo, a fonte SUN fecha 6/6

**2026-08-19/20 (23:1x)** · **gates congelados neste commit** · continuação da
fila (a crimp era a última aberta do SUN; σ 1,21× com MAE e mx já dentro).

## 1. A estrutura — o precedente C_creep-token da própria fonte

A standard fechou hoje com o kernel cinemático (k_graded=0,02 fitado-declarado
+ aexp=8 + floor lido 0,0284). A crimp tem o floor PRÓPRIO já adotado e com a
melhor procedência da fonte (**0,142 lido com platô VERDADEIRO** — validou o
leitor na errata do item R). A proposta: **estender o k=0,02 do token da irmã**
(mesma junta greased, conector crimpado) com **aexp=1 default** — o kernel
troca o `tr_loose_gain`=2,44 (fitado) por um valor de token: **fitado-declarado
sai, token entra; zero número novo**.

## 2. Pacote (per_case `_grease_crimp` — token existente)

| campo | valor | origem |
|---|---|---|
| `loose_rate_mode` | graded_scrit · s_crit=0 | forma da fonte (standard) |
| `k_loose_graded` | **0,02** | token da irmã standard (adotado lá) |
| `arrest_approach_exp` | 1,0 | **default** (o 8 da standard é da junta dela; não herda) |
| `loose_arrest_floor` | 0,142 | JÁ ADOTADO (lido, platô verdadeiro) — fica |
| `tr_loose_gain` | 0,0 | sai (o kernel graded substitui o torque) |
| `k_wear_spec` | 1,5e-15 | fica (canal de wear da adoção anterior) |

## 3. Sandbox — FECHA

**0,0221/0,0886/0,0303 → 0,0149/0,0370/0,0187** (0,30×/0,37×/0,75×).
Vizinhança: região 0,020–0,024 fecha (3 células contíguas); 0,018 não — o
token está na borda inferior, MAS o valor foi fixado ANTES pela irmã (a grade
só demonstra vizinhança, como no C_creep-token).

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha | 0,0149/0,0370/0,0187 ao dígito pelo canônico |
| **G2** | as 5 irmãs SUN bit-idênticas | |
| **G3** | isolamento no diferencial do carimbo (junto com as 2 lk19,8) | |
| **G4** | fingerprint único nos 210 | |
| **G5** | censo 153 → **156/205** (com as 2 lk19,8 do mesmo carimbo) · abertas 12 → 9 · **SUN 6/6 = TERCEIRA fonte fechada no dia** · ICMEZ 8/8 | |
| **G6** | sincronização completa | |

## Estado

EXECUTADO 2026-08-19/20 (23:1x): G1/G2 na hora; carimbo consolidado.
