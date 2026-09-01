# Pré-registro v2 — rampa de fratura do Liu 2025, gateada em VIDA

**Data:** 2026-07-28 · **Fonte-alvo:** `LIU_2025` · **Substitui:** `2026-07-27-liu2025-fracture-ramp-prereg.md` (v1, **arquivado sem assinar**)
**Fingerprint contra o qual foi medido:** `4f5bedfbace4` (re-verificado hoje: 203 casos, único)
**Status:** PROPOSTO — gates abaixo são IMUTÁVEIS depois de assinados (§4.43)

---

## 0. Por que existe um v2

O v1 foi submetido a uma **checagem de mensurabilidade** antes de assinar
(`New_Theory/liu2025_ramp_premeasure.md`, §4.44 do `MODEL_LEGITIMACY.md`). Ela
achou três defeitos que **não são de rigor, mas de mensurabilidade** — e
corrigi-los **aumenta** a exigência:

| defeito do v1 | correção do v2 |
|---|---|
| gate vertical (`res.máx < 0,10`) num trecho onde a incerteza do **próprio dado** vale 0,124–0,900 em `F/F₀` | **E1** — gate em **VIDA**: erro no ciclo de cruzamento de cada nível |
| conflaciona *prever QUANDO* (fechada pelo dado: 5 % exigido vs 44 % de scatter) com *prever a FORMA* | **E2** — `N_f` **lido** da matriz de ensaios; só a forma é gateada |
| banco de prova = `fig2_single`, a **pior** curva da fonte (±0,90 de incerteza) | **E3** — banco de prova = núcleo coerente `amp0p4/0p5/0p6` |

**Consequência de protocolo, declarada:** os gates do v1 já foram medidos, então
assiná-lo seria ceremonial. Os gates do v2 recaem sobre grandezas **ainda não
medidas** (erro de cruzamento em vida; coerência do núcleo sob essa métrica;
discriminância contra o cliff) — a cegueira é **restaurada**.

---

## 1. A forma sob teste (inalterada em relação ao v1)

Candidato **B1**: a trinca reduz a seção resistente, `k_b ∝ A_eff` cai, e com o
deslocamento de montagem travado `F_0` cai junto.

```
A_eff/A_s = 1 − ((D − D_on)/(1 − D_on))^q          para D > D_on
g         = (1−α)(1+ρ)/((1−α)+ρ),   ρ = k_j/k_b,  α = 1 − A_eff/A_s
dF_0/ciclo = F_0 · (g_n/g_{n−1} − 1)
```

Injetada por `loss_mechanisms=[...]`. **Engine canônico não é tocado** nesta
execução; adoção é passo separado (§6).

### 1.1 Relógio: LIDO, não previsto (E2)

`D = N/N_f` com **`N_f` lido da coluna *cycles to end* da matriz de ensaios** do
artigo:

| caso | amp0p25 | amp0p3 | amp0p4 | amp0p5 | amp0p6 | amp0p8 | fig2 |
|---|--:|--:|--:|--:|--:|--:|--:|
| `N_f` (paper) | 330 000 | 250 000 | 77 000 | 38 000 | 24 200 | 14 400 | 10 000 |

**Custo honesto, declarado antes de medir:** são **7 números para 7 curvas**, e a
claim que este pré-registro pode ganhar é ***"o modelo prevê a FORMA do colapso
dada a vida"***, **não** *"o modelo prevê a vida"*. A segunda está **fechada pelo
dado** (§4.44: orçamento exige `|ε| ≤ 5 %`, scatter de espécime é 44 %). Classe de
procedência de `N_f`: **input-de-paper**, mesma de `emb_um`/`delta_spectrum`/
`trim_n_max`. Precedente adotado: `LI_2022_TRIBOINT` roda com `fat_C1` ancorado
no `N_frat` **medido**.

---

## 2. A métrica de vida (E1) — definição operacional

Onde `|dr/dN|` excede o que a digitalização resolve, pontuar **horizontalmente**.

**Níveis gateados:** `r*` ∈ **{0,80 · 0,70 · 0,60 · 0,50 · 0,40}** — todos
alcançados pelas 3 curvas do núcleo (que terminam em 0,330) e todos **acima** da
borda do gráfico, de modo que nenhum cruzamento é lido na moldura.

**Cruzamento:** primeiro `N` em que a curva desce a `r ≤ r*`, por interpolação
linear. Modelo **alinhado** exatamente como a métrica canônica (dividido pelo
próprio valor no 1º ciclo do dado) — o mesmo alinhamento de `CaseResult.align`.
Se o modelo **nunca** cruza, conta como **violação** (não como dado ausente).

**Normalizador — e por que não é `N_f`.** O colapso ocupa só 20–29 % da vida, então
±15 % de `N_f` (ou de `N_cruzamento`, que ali é quase o mesmo) é **mais largo que
a própria janela de colapso** e deixaria passar até um cliff. A tolerância é
relativa à **largura da janela de colapso**:

```
Δ_col   = N_f(paper) − N_joelho          N_joelho := trim_n_max REGISTRADO da curva
tolerância = 0,15 · Δ_col                        (o ±15 % do precedente PR-39)
PASSA o nível r* sse |N_modelo(r*) − N_dado(r*)| ≤ 0,15 · Δ_col
```

Ambos os termos são números **já registrados** e independentes deste estudo
(`N_f` do paper; `trim_n_max` do cfg adotado). Valores resultantes:

| curva | `N_f` | `trim_n_max` | `Δ_col` | **tolerância** |
|---|--:|--:|--:|--:|
| amp0p4 | 77 000 | 60 000 | 17 000 | **2 550 ciclos** |
| amp0p5 | 38 000 | 30 000 | 8 000 | **1 200 ciclos** |
| amp0p6 | 24 200 | 18 000 | 6 200 | **930 ciclos** |

⇒ **15 cruzamentos gateados** (5 níveis × 3 curvas).

---

## 3. Espaço de busca — DECLARADO ANTES

Grade exaustiva, **um único par** `(D_on, q)` para as três curvas:

```
D_on ∈ {0,70 · 0,75 · 0,80 · 0,85 · 0,90}      q ∈ {1 · 2 · 3 · 5 · 8}
```

`D_on` fica dentro da banda **handbook** (propagação = últimos 10–30 % da vida em
HCF) ⇒ classe *handbook*. `q` é *fitado-this-rig*, **1 valor para as 3**. Nenhum
outro parâmetro é tocado: nada de re-fit de `emb`, `floor`, `µ` ou wear.

---

## 4. GATES (imutáveis depois de assinados)

**G0 — inércia.** Com a forma desligada, as 3 curvas do núcleo reproduzem
**exatamente** o que o store `4f5bedfbace4` registra. Falhou ⇒ PARA.

**G1 — forma correta em VIDA, no núcleo coerente.** Existe **UM** par
`(D_on, q)` da grade §3 para o qual **os 15 cruzamentos** de §2 passam. Não é
permitido par por curva. *(Este é o gate que prova ou mata a forma.)*

**G1b — o platô não regride.** Na janela `N ≤ trim_n_max` — onde a métrica
vertical **é** bem-posta — as 3 do núcleo não pioram mais que **+0,01** em MAE
nem em res.máx contra o store. A forma não pode comprar a cauda estragando o
começo.

**G2 — não regride quem não fratura no range.** `amp0p25` e `amp0p3`, sob a
**métrica canônica vigente (pós-trim)**, não pioram mais que **+0,01** em MAE.
*(Declarado: o v1 gateava estas duas na curva inteira e falhava por razão de
**dado** — `amp0p3` termina em 0,683, o último ponto legível do digitalizador.
Os números sem trim serão reportados como **informacionais**, não como gate.)*

**G3 — discriminância contra o CLIFF** *(substitui o G5 do v1, que era
infalseável aqui)*. As mesmas 15 células rodam com **duas** alternativas:
(i) **sem a forma**; (ii) **cliff** (`D_on = 0,999`, `q = 1` — a forma que o
`FatigueLoss` já tem e que o PR-24 rejeitou). A rampa só sobrevive se **passar
onde as duas falham**. Se o cliff também passar, a rampa **não ganhou seus 2
parâmetros** ⇒ MORRE, independentemente do G1.

**G4 — a interação arresto×fratura fica declarada.** Registrar se a perda de
seção atravessa o `loose_arrest_floor = 0,25`. *(Medido no v1: **atravessa** —
`fig2`→0,140, `amp0p5`→0,000. Re-registrar sob a config do v2.)*

**G5 — extremas medidas, não gateadas.** `amp0p25`, `amp0p3`, `amp0p8`, `fig2`
rodam com o par vencedor e entram no relatório. **Não são gate** — o §4 do
premeasure já mostrou que as extremas desviam sistematicamente da rampa do
núcleo (0,25/0,30 rampam mais tarde; 0,80 é o espécime do scatter de 44 %).
Declarado antes para que o escopo não seja esticado depois.

**G6 — pré-condição de ADOÇÃO (não desta execução).** Só na adoção: nenhuma das
196 curvas de fora piora > +0,01 em MAE, e o store re-carimba com fingerprint
novo e único.

### 4.1 Interpretação pré-declarada (todos os ramos)

| resultado | leitura |
|---|---|
| **G1 ✓ · G1b ✓ · G2 ✓ · G3 ✓** | forma **validada sob métrica bem-posta**. Propor adoção per-rig com `N_f` input-de-paper; claim declarada = *"prevê a forma dada a vida"* |
| **G1 ✓ · G3 ✗** (cliff passa também) | a rampa não ganha os 2 parâmetros ⇒ **morre**; se o cliff passar sozinho, ele é o candidato barato — avaliar em prereg próprio, não aqui |
| **G1 ✓ · G1b ✗** | a forma compra a cauda estragando o platô ⇒ não adotar; investigar acoplamento com embedding/wear |
| **G1 ✗ com ≥ 12/15** | falha **parcial**: reportar quais níveis/curvas, e propor escopo reduzido **declarado** (ex.: só acima de `r*`=0,50). Não é adoção |
| **G1 ✗ com < 12/15** | **falsificação da forma sob métrica bem-posta.** `LIU_2025` é *data-limited* **e** *form-limited*; o trim §B vira **permanente** |
| **G2 ✗** | a forma regride quem não fratura ⇒ não adotar sem gating por regime |

---

## 5. O que NÃO está sendo proposto

- **Não** prever a vida (`N_f`) — fechada pelo dado (§4.44). `N_f` é **lido**.
- **Não** usar os `_tozero.csv` (extrapolação, §2.1 do v1).
- **Não** gatear `fig2_single` — é a pior curva da fonte (±0,90).
- **Não** mexer na métrica canônica, nos trims vigentes, nem no engine.
- **Não** adotar nada nesta execução: G6 é pré-condição separada.

---

## 6. Reprodutibilidade

```bash
python New_Theory/liu2025_ramp_v2_gates.py          # execução dos gates
python New_Theory/parallel_batch.py --sources LIU_2025 --workers 6 --store   # baseline
```

Dado: `curve_library/digitized_csv/liu2025_M16_*.csv` (registrados, sem `_tozero`)
Notas de aparato: `curve_library/apparatus_notes/liu2025_scirep_M16.md`
Medição pré-execução que motivou o v2: `New_Theory/liu2025_ramp_premeasure.md`
