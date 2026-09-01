# Pré-registro — queda abrupta do Liu 2025 como PERDA PROGRESSIVA DE SEÇÃO

**Data:** 2026-07-27 · **Fonte-alvo:** `LIU_2025` (7 curvas, M16×120 8.8, δ 0,25–0,80 mm)
**Fingerprint contra o qual foi medido:** `4f5bedfbace4`
**Status:** PROPOSTO — **NÃO ASSINAR COMO ESTÁ** (medição pré-execução 2026-07-28)
Gates abaixo são IMUTÁVEIS depois de assinados (§4.43)

> ## ⛔ MEDIÇÃO PRÉ-EXECUÇÃO — 2026-07-28 (`New_Theory/liu2025_ramp_premeasure.md`)
>
> Antes de assinar, os gates foram testados quanto à **mensurabilidade** no dado
> que existe. Fingerprint re-medido: `4f5bedfbace4` — **idêntico** ⇒ §4.43
> satisfeita, os números deste documento **não** precisam de re-baseline.
> Engine canônico **não** tocado (a forma entra por `loss_mechanisms=[...]`).
>
> **Resultado em uma linha: a forma funciona, mas os gates, como escritos, não
> medem o que pretendem.**
>
> | gate | medido | leitura |
> |---|---|---|
> | **G1** | 0,039 / 0,062 / σ 0,0285 (`D_on`=0,85, `q`=5, `fig2` **sem trim**) | passa MAE e res.máx — mas o veredicto depende de uma **ambiguidade na redação** (↓ L1) |
> | **G2** | **FALHA nas 7 células, por 30–40×** | estrutural, e **não é da forma**: é o relógio (↓ §2 do premeasure) |
> | **G3** | parcial — 0,40/0,50/0,60 colapsam numa rampa única (σ ≈ 0,01–0,02) | a forma tem assinatura repetível |
> | **G4** | **atravessa** o arresto: `fig2` → 0,140 e `amp0p5` → 0,000 com `floor`=0,25 | confirmado por código *e* número |
> | **G5** | **passa** — nenhuma das 7 passa o tripé sem o candidato | a forma faz trabalho real |
>
> ### Duas lacunas que DECIDEM o resultado — resolver antes de congelar
>
> **L1 — a cláusula σ_res do G1 é ambígua, e é ela que decide o G1.** O texto pede
> *"σ_res não pior que o valor pós-trim de hoje (0,0389 / 0,0546)"*, mas
> 0,0389/0,0546 são o **MAE e o res.máx** de hoje; o σ_res real do `fig2` no store
> é **0,0224**. A célula medida dá σ_res = **0,0285**. ⇒ leitura literal
> (≤ 0,0389): **G1 PASSA**. Leitura estrita (≤ 0,0224): **G1 falha por 0,006**.
> A mesma execução, dois veredictos opostos.
>
> **L2 — o §4.1 não tem ramo para o resultado medido.** Ele cobre "G0–G6 ✓",
> "G1 ✓ e G3 ✗", "G1 ✗" e "G5 ✗". O caso real — **G1 ✓, G5 ✓, G2 ✗** — não está
> previsto.
>
> ### Duas premissas do documento que a medição derrubou
>
> - **§4/G1 supõe que `fig2_single` tem colapso medido até 0,000 na métrica.**
>   Não tem: `FLOOR_TRIM = 0.10` descarta os pontos abaixo de 0,10 **antes** da
>   métrica, então o `fig2` que ela vê **termina em 0,300 (N = 9 900)**.
> - **§5 supõe que, se a forma passar, "os trims saem por consequência".**
>   Medido: ligar a rampa e remover os trims leva a fonte de **7/7 para 1/7** — e
>   em **4 das 6** quedas o `res.máx` é *exatamente o último ponto do dado*
>   (0,330 = borda do gráfico; 0,683 = fim do digitalizador). O trim é
>   **data-limited**, não form-limited.
>
> ### ⚠ Consequência de protocolo (decisão do professor)
>
> Os gates deste documento **já foram medidos**. Assiná-lo agora não é mais um
> pré-compromisso cego — seria ceremonial. As duas saídas honestas:
>
> 1. **Não assinar**, e registrar o premeasure como o **resultado** (é um: forma
>    validada + discriminante; relógio fechado pelo dado; trim re-justificado);
> 2. **Assinar uma versão EMENDADA** cujos gates recaiam sobre grandezas ainda
>    **não** medidas — as emendas E1/E2/E3 do premeasure fazem exatamente isso
>    (tolerância em **vida** ±15 % no trecho vertical · separar *quando* de
>    *forma* · trocar o banco de prova de `fig2` para o núcleo
>    `amp0p4/0p5/0p6`), o que **restaura** a cegueira e **aumenta** a exigência.
>
> Motivo de E1, em número: no colapso a incerteza do **próprio dado** (±3 % em N,
> declarada nas notas de aparato) vale **0,124 a 0,900** em F/F₀ — **6 das 7
> curvas têm incerteza maior que o limiar do gate**, e a curva eleita banco de
> prova (`fig2`) é a **pior**: ±0,90.

> **Regra §4.43 aplicada:** este documento carrega o fingerprint contra o qual foi
> medido. Se o fingerprint mudar antes da execução, cada número aqui vira
> **suspeito** e precisa ser re-medido antes de servir de baseline. Foi partir de
> falsificação não re-baselinada que matou o `flank_s_crit` na F4.

---

## 1. O fenômeno, e por que ele não é afrouxamento

As 7 curvas do Liu 2025 têm a mesma assinatura: platô longo, joelho, e **colapso
liso e acelerante até zero**. O paper não deixa ambiguidade sobre o que é o
colapso (`apparatus_notes/liu2025_scirep_M16.md`):

- *"each test ran until **bolt fracture**"*;
- locais de falha observados = **raio de concordância sob a cabeça** ou
  **primeiro filete engajado** (fotos do inset da Fig. 2);
- estágios declarados na Fig. 2: *material-loosening* (fim M1 ≈ 7×10²) →
  *structural-loosening* → **fatigue-fracture** (joelho N_D → colapso a 0 em M2);
- o próprio título é uma tese de fadiga: *"…based on normalized **screw root
  equivalent stress** and **loosening life curve**"*.

**Portanto: a queda é fratura por fadiga, não runaway de auto-afrouxamento.**
Qualquer forma que a produza por atrito/rotação é form-fantasma.

### 1.1 Fenomenologia medida (do CSV digitalizado)

| caso | δ (mm) | N_fim | r no joelho | Δ do colapso | % da vida | % da **perda** no colapso |
|---|---:|---:|---:|---:|---:|---:|
| amp0p25 | 0,25 | 327 000 | 0,926 | ~87 k | 27 % | 77,2 % |
| amp0p3 | 0,30 | 252 000 | 0,900 | ~72 k | 29 % | 68,5 % |
| amp0p4 | 0,40 | 76 500 | 0,853 | ~16 k | 22 % | 78,1 % |
| amp0p5 | 0,50 | 38 000 | 0,836 | ~8 k | 21 % | 75,5 % |
| amp0p6 | 0,60 | 24 200 | 0,812 | ~6 k | 26 % | 71,9 % |
| amp0p8 | 0,80 | 14 400 | 0,680 | ~3 k | 20 % | 52,2 % |
| fig2 | ~0,80 | 10 000 | 0,800 | ~2 k | 20 % | 80,0 % |

Três regularidades:

1. **O colapso é fração quase fixa da vida** (20–29 %), não um nº absoluto de
   ciclos. Assinatura de *propagação*, não de evento súbito.
2. **É liso e acelerante.** amp0p5: 0,836 → 0,800 → 0,750 → 0,650 → 0,500 →
   0,330 em 8 k ciclos. Concavidade de Paris, não degrau.
3. **Lei D-N:** `N_D ∝ δ^−2,90` (LSQ 6 pts, R²(log) = 0,982). O paper declara
   2,7 — e esse 2,7 já é o `fat_m1` adotado em `LI_2022_TRIBOINT`, com
   procedência literal *"inclinacao D-N Liu2025, PR-24"*.

### 1.2 Custo atual da exclusão

Hoje o colapso é recortado da métrica por `trim_n_max` (regra: taxa local > 3×
mediana do Estágio II, contígua até o fim). Os **7/7 no tripé e MAE 0,047 são
pós-trim**. Medido: o trim mantém 73–80 % dos *ciclos* mas exclui, em média,
**71,9 % da perda de pré-carga medida**. Ratificação pendente em
`f5_excecoes_propostas.md` §B (bloco de 16 curvas: LIU_2025 ×7 + YANG_2021 ×6 +
LI_2022_TRIBOINT `full` + SUN secos ×2).

---

## 2. O que já existe (e por que não bastou)

`FatigueLoss` (`dynamic_stiffness_analyzer.py:1715`, spec 2026-07-08): Miner
sobre Su-N bilinear + **Goodman vivo** (σ_m = F_0/A_s evolui com o afrouxamento).
Dois modos — `"axial"` (σ_a = Kt·F_amp/A_s) e **`"bending"`** (σ_a =
Kt·E·d₂·δ/L_eff², construído no PR-24 exatamente para ensaio transversal).
`fatigue_enabled=False` por default ⇒ inerte bit-idêntico.

**PR-24 (2026-07-13) já validou a forma nesta fonte:** com `m1=2.7` + **uma**
escala (`fat_C1=6.7e30`), N_D reproduz a varredura inteira — logerr 0,07 (~17 %
em 6 amplitudes). **Precedente adotado:** `LI_2022_TRIBOINT` roda com fadiga
ligada, `fat_C1` per-material ancorado no N_frat medido (410 k).

### 2.1 Os quatro obstáculos medidos

Qualquer proposta tem de atravessá-los; estão todos no repo:

1. **Forma errada.** `FatigueLoss` é **cliff de 1 ciclo**: `dF_0 = 0` até
   `D_fatigue ≥ 1`, aí cai tudo. O dado desce em ~20 % da vida. PR-24: *"o erro
   real é a **aceleração PRÉ-fratura**, NÃO o cliff instantâneo"*.
2. **Dispersão de espécime de 44 %.** `fig2_single` e `amp0p8` são a mesma
   amplitude nominal (0,8 mm): uma fratura em 10 k, a outra vive até 14,4 k.
   PR-39v2: *"cliff representável só per-espécime (não-preditivo)"*.
3. **Conflito de âncora.** PR-39v2 mediu que as janelas exigiriam
   `C1 ≥ 7,81e30` contra a âncora **4,97e30**.
4. **A D-N não é potência limpa.** Inclinação local: 1,52 → **4,09** → 3,16 →
   2,52 → 1,87. O global 2,90 é média de uma curva que serpenteia por fator 2,7.

**Limite de dado (duro):** as curvas 0,4–0,8 mm **saem pela borda do gráfico em
F/F₀ = 0,33** — o último ponto é a moldura, não a fratura. Só `fig2_single` tem
colapso completo até 0,000 no CSV registrado. Os arquivos
`liu2025_M16_amp0p4_tozero.csv` / `..._fig2_single_tozero.csv` **não estão
registrados em manifest nem em `DIGITIZED_CASES`**, e a cauda do `amp0p4_tozero`
abaixo de 0,33 é **extrapolação, não medição** — não podem servir de gate.

---

## 3. Forma proposta (candidato B)

> Trinca cresce → área resistente A(a) encolhe → `k_b ∝ A` cai → com o
> deslocamento de montagem travado, `F_0 = δ_tot·k_b·k_m/(k_b+k_m)` cai junto →
> **e o F_0 caindo realimenta o laço de afrouxamento que já existe** (menos F_0
> → mais slip → mais wear/rotação).

Uma única forma compra a **rampa** e a **aceleração pré-fratura** que o PR-24
nomeou como faltante — a segunda de graça, pelo acoplamento que o engine já tem.

**Checagem de magnitude (fecha):** com `k_m ≈ 5·k_b`, metade da seção leva F/F₀ a
0,545 — quase proporcional, levemente amortecido pelo membro. E F/F₀ → 0 exige
A → 0, que é literalmente a separação. Bate com o dado, inclusive o 0,000 exato
do `fig2`.

### 3.1 Duas implementações, custos diferentes

**B1 — barata, sem estado novo.** Reusar `state.D_fatigue` (Miner já acumula) e
mapear para knock-down de seção:

```
A_eff/A_s = 1 − ((D_fatigue − D_on)/(1 − D_on))^q     para D_fatigue > D_on
```

- Procedência de `D_on`: em HCF a iniciação ocupa a maior parte da vida e a
  **propagação os últimos ~10–30 %** — resultado clássico, e bate com os 20–29 %
  medidos na tabela §1.1. Classe: *handbook*, não *fitado-this-rig*.
- Custo: **2 parâmetros** fenomenológicos (`D_on`, `q`).

**B2 — ancorada.** Estado próprio de comprimento de trinca com Paris
(`da/dN = C·(ΔK)^m`, `ΔK = Y·σ_a·√(πa)`), `Y` de solução de SIF para raiz de
rosca.
- Custo: 2 parâmetros **com banda de material** — a diferença entre
  *fitado-this-rig* e *handbook* na taxonomia de procedência.

**Recomendação:** começar por **B1** (barata, reusa estado existente, testável em
uma tarde). Só escalar para B2 se B1 passar o gate G1 mas falhar G3 (coerência
cross-amplitude) — aí o problema é a lei de crescimento, e Paris é a resposta.

### 3.2 Interação com formas já adotadas (não testada)

`loose_arrest_floor = 0.25` faz o modelo travar em 0,25·F₀ via
`self_locking_gate`. **`FatigueLoss` não chama esse gate** — então um `dF_0` de
perda de seção passa por baixo do arresto. Isso é provavelmente o desejado (a
fratura ignora auto-travamento), mas é **acoplamento entre duas formas adotadas
em momentos diferentes, nunca verificado junto**. G4 abaixo cobre isso.

---

## 4. GATES (imutáveis depois de assinados)

**G0 — inércia por default.** Com a forma desligada, os **203 casos** do store
reproduzem `4f5bedfbace4` **bit-a-bit**. Falhou ⇒ PARA.

**G1 — a rampa aparece onde há dado completo.** Em `fig2_single` **sem trim**
(única curva com colapso medido até 0,000): tripé completo — MAE ≤ 0,10 **E**
res.máx < 0,10 **E** σ_res não pior que o valor pós-trim de hoje (0,0389 /
0,0546). Esta é a curva que prova ou mata a forma.

**G2 — não regride quem não fratura no range.** `amp0p25` e `amp0p3` terminam em
0,68 sem chegar à fratura. Nenhuma das duas pode piorar em **mais de +0,01** de
MAE nem violar res.máx < 0,10. (O PR-24 tropeçou exatamente aqui.)

**G3 — coerência cross-amplitude com UMA constante.** O mesmo par
(`D_on`, `q`) — não um por curva — serve as 7. Ordenação de N_D preservada
(monotônica em δ). Explicitamente: **não é gate** reproduzir a inclinação local
(§2.1 obstáculo 4); é gate não *inverter* a ordem.

**G4 — a interação arresto×fratura é declarada.** Medir e registrar se a perda
de seção atravessa o `self_locking_gate`. Qualquer que seja o resultado, ele
entra no doc. Sem isso, G1 não conta.

**G5 — discriminância (lição do `flank_s_crit`).** Rodar as células de gate
**também com a forma desligada**. Se as células passam sem o candidato, o
candidato não está fazendo trabalho ⇒ MORRE, independentemente de G1.

**G6 — nenhum caso pior fora da fonte.** Nas 196 curvas restantes: nenhuma piora
> +0,01 em MAE.

### 4.1 Interpretação pré-declarada

- **G0–G6 todos ✓** ⇒ adotar per-rig, com `D_on`/`q` na classe de procedência
  que a execução de fato usar (handbook se vier da faixa 10–30 %; senão
  *fitado-this-rig* e assim rotulado).
- **G1 ✓ mas G3 ✗** ⇒ escalar para B2 (Paris). A lei de crescimento é o
  problema, não a ideia.
- **G1 ✗** ⇒ registrar como falsificação: a rampa de fratura **não** é
  redutível a perda de seção sob esta cinemática; o Liu 2025 fica
  form-limited e o trim §B vira permanente, não provisório.
- **G5 ✗** ⇒ morre calado, sem adoção, como o `flank_s_crit`.

---

## 5. O que NÃO está sendo proposto

- **Não** adotar o cliff `FatigueLoss` como está (obstáculos 1–3 já o mataram).
- **Não** acoplar `D_fatigue` a µ ou ao `loose_arrest_floor` (candidato C do
  levantamento): a fratura não é fenômeno de atrito; seria form-fantasma e a
  cláusula de morte do PR-3 se aplica.
- **Não** usar os `_tozero.csv` como dado de gate (§2.1: extrapolação).
- **Não** mexer na métrica canônica nem nos trims vigentes — se a forma passar,
  os trims da `LIU_2025` deixam de ser necessários e saem por consequência,
  não por decisão separada.
- **Vida estocástica** (Weibull/lognormal em N_D) é a resposta honesta ao
  obstáculo 2, mas quebra a métrica determinística por curva e exigiria métrica
  de banda. **Fora de escopo**, registrado aqui para não se perder.

---

## 6. Procedência das constantes

| constante | valor de partida | classe | origem |
|---|---|---|---|
| `fat_m1` | 2,7 | **input-de-paper** | inclinação D-N declarada pelo Liu 2025; já adotada em `LI_2022_TRIBOINT` |
| `fat_C1` | a re-ancorar | fitado-this-rig | PR-24 achou 6,7e30; PR-39v2 registrou conflito com a âncora 4,97e30 — **resolver antes de adotar** |
| `D_on` | 0,80 | handbook (a confirmar) | fração de vida em propagação, HCF (10–30 %); bate com 20–29 % medidos |
| `q` | a fitar | fitado-this-rig | 1 valor para as 7 (G3) |

---

## 7. Reprodutibilidade

```bash
# baseline (deve dar 4f5bedfbace4, 203 casos)
python New_Theory/parallel_batch.py --workers 6 --store
python -m bolt_analysis_studio.validation.report

# fonte-alvo isolada
python New_Theory/parallel_batch.py --sources LIU_2025 --workers 6 --store
```

Dados: `Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/liu2025_M16_*.csv`
Notas de aparato: `curve_library/apparatus_notes/liu2025_scirep_M16.md`
Histórico: PR-24 e PR-39v2 em `docs/superpowers/specs/2026-07-11-mem-iter4-preregistrations.md`
