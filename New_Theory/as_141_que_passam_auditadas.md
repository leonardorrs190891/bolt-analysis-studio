# As **141 que passam**, auditadas — 4,3 % dependem da regra por fonte, e uma curva "perdida" voltou

**2026-08-15 (manhã)** · só-leitura · **nada mudado** · store `85e8104420b0`, censo
**141/205**.

Seis auditorias desta sessão olharam as **64 que falham** (as cinco camadas de estatuto + os
pisos). **As que passam nunca foram examinadas.**

---

## 1. Quantas dependem da regra POR FONTE?

A `_SRES_POR_FONTE` (adotada em **D1**) eleva o limite de σ para
`max(0,025; piso da fonte)`. Curva com σ > 0,025 que passa **só** porque o piso da sua fonte
é maior depende da **regra**, não da régua global.

**Medido: 6 de 141 — 4,3 %.**

| curva | fonte | σ | limite da fonte |
|---|---|---:|---:|
| `karlsen2022_M30_HV_run7p1` | KARLSEN_2022 | 0,0504 | 0,0903 |
| `bauer2024_M8_fig6_rep3` | BAUER_2024 | 0,0376 | 0,0900 |
| `karlsen2022_M30_HV_run2p2` | KARLSEN_2022 | 0,0364 | 0,0903 |
| `bauer2024_M8_fig6_rep2` | BAUER_2024 | 0,0344 | 0,0900 |
| `karlsen2022_M42_HV_run21p0` | KARLSEN_2022 | 0,0337 | 0,0903 |
| `karlsen2022_M30_HV_run6p2` | KARLSEN_2022 | 0,0300 | 0,0903 |

Todas de **duas** fontes, ambas com piso alto medido. ⇒ **o censo é 95,7 % independente do
D1**; se a regra fosse revertida, cairia **141 → 135**.

Isso é uma medição a favor da adoção: ela **não** está sustentando o número.

## 2. Margem — quão perto do limite

Fração do limite na perna mais apertada:

| faixa | curvas |
|---|---:|
| **≥ 95 %** (a um re-carimbo de sair) | **4** |
| 90–95 % | 13 |
| 75–90 % | 24 |
| **< 75 %** (folgadas) | **100** (71 %) |

A mais apertada é `li2022ti_axial_10Hz_full` a **99,4 %**. ⚠️ **17 curvas (12 %) acima de
90 %** — e o store foi re-carimbado **três vezes em 24 h**, então essa faixa é a que se
move primeiro.

## 3. ⚠️ Uma curva que o registro dá por PERDIDA passa por mérito

`eccles2010_fig7c_axial_2p7kN_constant` apareceu na lista de margem (94,8 %) — e o
comentário da **P-15** (2026-08-08), preservado em `report_html.py`, diz o contrário:

> *"Removido o piso falso, a curva volta a falhar (σ 0,0258 = **1,03×** o limite global) …
> Custo previsto e aceito na assinatura: **censo 140 → 139**.*
> *⚠️ Consequência: a `fig7c` fica **sem estatuto E sem rota** — a fonte perdeu o piso junto
> com a família falsa, logo **prova F7 é impossível** para ela até haver réplica de condição
> repetida."*

**Hoje:** MAE 0,0249 · res.máx 0,0530 · σ **0,0237** = **0,95×** o limite global. **Passa**,
sem exceção e sem declaração — por mérito.

⇒ **duas afirmações da nota estão vencidas:**

1. o custo *"140 → 139"* — a curva voltou;
2. *"sem rota, prova F7 impossível até haver réplica"* — ⚠️ **a réplica existe**: são as
   **4 curvas `no_axial`** que medi ontem (piso 0,1134/0,0443,
   `eccles_2_excecoes_sobre_piso_ja_invalidado.md` §4).

Nenhuma das duas é erro da P-15 — é o mundo tendo andado. Mas **nenhuma das duas está sob
guarda**: são prosa em comentário de código, exatamente a classe que a auditoria de
cobertura já identificou como desprotegida (as **células de custo**).

## 4. O que isto NÃO diz

Não diz que o censo esteja frágil: 71 % das curvas estão abaixo de 75 % do limite, e a
dependência da regra por fonte é de 4,3 %. Também não diz que a `fig7c` deva receber
estatuto — ela **não precisa**, passa por mérito.

## Reprodutibilidade

`audit_as_141.py` no scratchpad (~20 s, só-leitura). Usa `rh.limite_sres` e
`rh.sres_para_censo` — nunca reimplementa a regra.
