# Liu 2025 — medição PRÉ-EXECUÇÃO do pré-registro da rampa de fratura

**Data:** 2026-07-28 · **Alvo:** `docs/superpowers/specs/2026-07-27-liu2025-fracture-ramp-prereg.md`
**Fingerprint medido:** `4f5bedfbace4` — **idêntico** ao do pré-registro ⇒ §4.43 satisfeita,
os números do prereg **não** precisam de re-baseline.
**Código canônico:** NÃO alterado. Tudo por mecanismo injetado (`loss_mechanisms=[...]`).

---

## 0. Veredicto

**A forma funciona.** Na curva que o prereg elegeu como banco de prova
(`fig2_single`), **sem trim nenhum**, a rampa entrega **MAE 0,039 / res.máx
0,062** — praticamente os mesmos números que hoje só se obtêm *cortando* 20 % da
curva (0,0389 / 0,0546), mas agora pontuando o colapso inteiro. E ela é
**discriminante**: sem o candidato a mesma célula dá 0,093 / 0,481.

**Mas ela não dispensa os 7 trims — ela custa 6 dos 7 passes.** Ligando a rampa e
removendo os trims, a `LIU_2025` vai de **7/7 para 1/7** no tripé. E o motivo
**não é o modelo**: em 4 das 6 que caem, o res.máx é **exatamente o último valor
do dado** (0,330 = borda inferior do gráfico do artigo; 0,683 = último ponto
legível do digitalizador). O modelo leva `F_0` a zero na fratura que o paper
declara; o dado digitalizado **acaba antes**, e a métrica pontua a moldura da
figura.

| gate | resultado medido | leitura |
|---|---|---|
| **G1** (`fig2` sem trim) | **0,039 / 0,062 / σ 0,0285** em `D_on=0,85, q=5` | **passa MAE e res.máx**; o veredicto final depende de uma ambiguidade na redação (§3.1) |
| **G2** (`amp0p25`/`amp0p3`) | **FALHA em todas as 7 células**, por 30–40× | estrutural, e não é da forma (§2, §3) |
| **G3** (um par para as 7) | parcial: 0,40/0,50/0,60 colapsam numa única rampa (σ ≈ 0,01–0,02); extremas desviam | forma tem assinatura repetível (§4) |
| **G4** (arresto × fratura) | **atravessa**: `fig2` termina em 0,140 e `amp0p5` em 0,000, com `floor = 0,250` | confirmado por código *e* número (§5) |
| **G5** (discriminância) | **passa**: nenhuma das 7 passa o tripé sem o candidato | a forma faz trabalho real |

**Recomendação:** não assinar como está. Três emendas (§6) tornam os gates
mensuráveis. A mais importante: **no trecho vertical, tolerância em vida, não em
`F/F₀`** — porque ali a incerteza do próprio dado chega a **±0,90** (§3).

---

## 1. O que confirmei do pré-registro (replicação independente)

Cheguei à mesma leitura física antes de ler o documento — bom sinal de que ela
não é artefato de quem a escreveu:

| grandeza | prereg | esta medição | fonte |
|---|---|---|---|
| razão de rigidez `k_m/k_b` | "≈ 5" (estimativa) | **5,096** | `k_j_ax`/`geom.k_b` no rig real |
| lei D-N | `N_D ∝ δ^−2,90`, R²(log) 0,982 | `N_f ∝ δ^−2,883`, R²(log) 0,981 | LSQ 6 pts |
| joelho / vida | 20–29 % | `N_joelho/N_f` = 0,714–0,799 (média 0,758) | 7 curvas |
| `FatigueLoss` ignora o arresto | §3.2, "não verificado" | **confirmado** | `self_locking_gate` só é chamado em `RotationalLooseningLoss` (linhas 1790, 1873); `FatigueLoss` (1715–1759) não o chama |

O diagnóstico central também se confirma com números novos: **o modelo fica PLANO
exatamente onde o dado dobra.** Nas duas amplitudes baixas ele não tem nenhum
mecanismo capaz de acelerar — `wear` e `rotational_loosening` são **exatamente
zero** (partial slip; `W_slip/ciclo = 0` medido no engine), sobrando `embedding`
(assíntota exponencial) e `creep` (log t), ambos desacelerantes:

```
amp0p25   N       240000   270000   290000   300000   310000   320000   327000
          dado     0.926    0.916    0.898    0.878    0.845    0.762    0.675
          modelo   0.845    0.844    0.843    0.843    0.843    0.842    0.842
```

Isso **descarta a rota wear/dano** por dois caminhos independentes: (i) em
0,25/0,30 mm o relógio de slip-work **nunca liga**, então não pode cronometrar um
joelho que existe nessas curvas; (ii) onde o wear está ativo, o check L7 desta
fonte já implica **42 000–201 000 J/mm³** contra a banda 1 800–10 500 — 4× a 19×
acima do teto. Empurrar mais perda por ali agrava uma violação já registrada.

---

## 2. Achado 1 — orçamento de precisão do relógio (mata G2)

O colapso ocupa `φ` = 20–29 % da vida. Se o relógio erra `ε` em `N_f`, a janela
de colapso do modelo desloca-se em bloco e a sobreposição com a do dado é
`max(0, 1 − |ε|/φ)`:

| curva | φ | ε (m1 lido + 1 âncora) | sobrep. | ε (PR-24: m1=2,7 + escala) | sobrep. |
|---|---:|---:|---:|---:|---:|
| amp0p25 | 0,27 | −13,8 % | 49 % | −16,8 % | 38 % |
| amp0p3 | 0,29 | **−34,6 %** | **0 %** | — | — |
| amp0p4 | 0,22 | −7,4 % | 66 % | 0,0 % | 100 % |
| amp0p5 | 0,21 | 0,0 % | 100 % | — | — |
| amp0p6 | 0,26 | +3,6 % | 86 % | — | — |
| amp0p8 | 0,20 | **−34,4 %** | **0 %** | −14,3 % | 29 % |
| fig2 | 0,20 | −5,5 % | 73 % | — | — |

**Para 75 % de sobreposição em todas: `|ε| ≤ 5,0 %`.** Disponível: 17 % (PR-24,
melhor caso publicado) a 35 % (âncora de 1 ponto). E o piso é duro: `fig2` e
`amp0p8` são a **mesma amplitude nominal** e fraturam com **44 % de diferença** —
nenhum relógio determinístico vence isso.

Consequência medida (rampa Paris-integrada de 1 constante, relógio Miner):

```
                  hoje(pós-trim)   com a rampa (melhor R)      sobreposição
amp0p25  MAE/máx    0.076/0.095       0.331/0.845                  49%
amp0p3              0.065/0.087       0.410/0.900                   0%
amp0p8              0.049/0.085       0.284/0.680                   0%
```

Nas quatro em que o relógio acerta, a mesma forma **melhora muito**:
`amp0p4` 0,101/0,452 → 0,089/0,236 · `amp0p5` 0,083/0,437 → 0,042/0,169 ·
`amp0p6` 0,054/0,188 → 0,047/0,124 · `fig2` 0,093/0,481 → 0,054/0,153
(baselines aqui são **sem trim**, para comparar maçã com maçã).

---

## 3. Achado 2 — G1 é imensurável no dado que existe

`apparatus_notes/liu2025_scirep_M16.md` declara o erro de digitalização: **±0,02
em F/F₀ e ±3 % no posicionamento de ciclo.** No colapso a curva é quase vertical,
então o erro de ciclo vira erro **grande** em F/F₀:

| curva | \|dr/dN\| máx | ±3 % de N | **incerteza do dado em r** | gate pede |
|---|---:|---:|---:|---|
| amp0p25 | 1,25e−5 | 9 810 | **0,124** | < 0,10 ✗ |
| amp0p3 | 9,25e−6 | 7 560 | 0,073 | ok |
| amp0p4 | 1,8e−4 | 2 295 | **0,414** | < 0,10 ✗ |
| amp0p5 | 3,4e−4 | 1 140 | **0,388** | < 0,10 ✗ |
| amp0p6 | 3,75e−4 | 726 | **0,273** | < 0,10 ✗ |
| amp0p8 | 3,0e−4 | 432 | **0,131** | < 0,10 ✗ |
| **fig2** | 3,0e−3 | 300 | **0,900** | < 0,10 ✗ |

**6 das 7 têm incerteza própria maior que o gate** — e a curva eleita banco de
prova é a **pior**: ±0,90. Lido pelo avesso: no colapso, 0,10 de resíduo vertical
equivale a **0,33–4,3 % da vida** (`fig2`: 33 ciclos). O gate está, sem dizê-lo,
pedindo o relógio de fratura com **0,33 %** de precisão numa fonte com 44 % de
scatter medido.

Que o `fig2` **passe** MAE e res.máx nessas condições (§0) é notável, mas é sorte
de alinhamento entre uma rampa e um trecho que o dado não resolve — não é
evidência da força que o gate pretendia colher.

### 3.1 Duas lacunas na redação dos gates (decidem o resultado)

Gates ficam imutáveis depois de assinados, então estas duas têm de ser resolvidas
**antes**:

1. **A cláusula σ_res do G1 é ambígua — e é ela que decide o G1.** O texto diz
   *"σ_res não pior que o valor pós-trim de hoje (0,0389 / 0,0546)"*, mas
   0,0389/0,0546 são o **MAE e o res.máx** de hoje; o σ_res real do `fig2` no
   store é **0,0224**. Medido: a melhor célula dá σ_res = **0,0285**.
   ⇒ leitura literal (≤ 0,0389): **G1 PASSA**. Leitura estrita (≤ 0,0224):
   **G1 falha por 0,006**. A mesma execução dá dois veredictos opostos.
2. **G2 não tem ramo de interpretação.** O §4.1 cobre "G0–G6 ✓", "G1 ✓ e G3 ✗",
   "G1 ✗" e "G5 ✗". O caso medido — **G1 ✓, G5 ✓, G2 ✗** — não está previsto.

### 3.2 O dado de gate não é o que o prereg supõe

`FLOOR_TRIM = 0.10` descarta pontos abaixo de 0,10, então o `fig2` que a métrica
vê **termina em 0,300 (N = 9 900)**, não em 0,000. A premissa "única curva com
colapso medido até 0,000" **não vale para a métrica canônica** — o ponto zero é
descartado antes de chegar nela.

---

## 4. Achado 3 — a rampa É universal (boa notícia para G3)

Medido no dado cru, em coordenadas do próprio joelho (`u` = fração da vida entre
joelho e fratura, `v` = `r/r_joelho`):

| amp | r_joelho | u(v=0,97) | u(0,94) | u(0,90) | u(0,85) | u(0,80) | u(0,70) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0,25 | 0,926 | 0,553 | 0,692 | 0,797 | 0,861 | 0,908 | — |
| 0,30 | 0,900 | 0,321 | 0,541 | 0,735 | 0,878 | 0,971 | — |
| **0,40** | 0,853 | **0,274** | **0,438** | **0,594** | **0,702** | **0,782** | **0,866** |
| **0,50** | 0,836 | **0,261** | **0,446** | **0,613** | **0,699** | **0,777** | **0,867** |
| **0,60** | 0,812 | **0,246** | **0,412** | **0,587** | **0,705** | **0,787** | **0,864** |
| 0,80 | 0,680 | 0,141 | 0,281 | 0,416 | 0,550 | 0,656 | 0,805 |
| fig2 | 0,800 | 0,384 | 0,502 | 0,621 | 0,707 | 0,768 | 0,839 |

As três do meio são **a mesma curva** (σ ≈ 0,01–0,02 em `u` para todo `v`);
`fig2` fica próximo. As extremas desviam sistematicamente: 0,25/0,30 rampam **mais
tarde**, 0,80 **mais cedo** (e é o espécime cujo joelho já está anômalo em 0,680 —
o par do scatter de 44 %). Um par único (`D_on`, `q`) serve 4 curvas com folga.

---

## 5. A grade completa (forma B1 do prereg, relógio lido do artigo)

`N_f` lido da matriz de ensaios (coluna *cycles to end*), para isolar a rampa do
relógio. MAE/res.máx na curva **inteira**; "hoje" é o tripé **pós-trim**:

| caso | hoje | 0,75/q2 | 0,75/q3 | 0,80/q2 | 0,80/q3 | 0,80/q5 | 0,85/q3 | **0,85/q5** |
|---|---|---|---|---|---|---|---|---|
| amp0p25 | 0,076/0,095 | 0,227/0,597 | 0,192/0,562 | 0,203/0,579 | 0,169/0,537 | 0,130/0,463 | 0,142/0,498 | 0,107/**0,407** |
| amp0p3 | 0,065/0,086 | 0,195/0,683 | 0,171/0,683 | 0,177/0,683 | 0,157/0,683 | 0,135/0,683 | 0,142/0,683 | 0,125/**0,683** |
| amp0p4 | 0,046/0,062 | 0,137/0,390 | 0,110/0,318 | 0,118/0,350 | 0,093/0,267 | 0,062/0,181 | 0,072/0,207 | 0,050/**0,140** |
| amp0p5 | 0,029/0,052 | 0,130/0,398 | 0,105/0,355 | 0,112/0,375 | 0,090/0,330 | 0,067/0,330 | 0,075/0,330 | 0,058/**0,330** |
| amp0p6 | 0,023/0,065 | 0,136/0,400 | 0,119/0,353 | 0,124/0,370 | 0,108/0,330 | 0,091/0,330 | 0,096/0,330 | 0,082/**0,330** |
| amp0p8 | 0,049/0,085 | 0,111/0,330 | 0,097/0,330 | 0,101/0,330 | 0,087/0,330 | 0,073/0,330 | 0,077/0,330 | 0,068/**0,330** |
| **fig2** | 0,039/0,055 | 0,110/0,336 | 0,084/0,266 | 0,093/0,297 | 0,066/0,217 | **0,044/0,093** | 0,051/0,144 | **0,039/0,062** |
| **tripé** | **7/7** | 0/7 | 0/7 | 0/7 | 0/7 | **1/7** | 0/7 | **1/7** |

Duas leituras que só a grade dá:

1. **Em 4 das 7 curvas o res.máx é EXATAMENTE o último valor do dado** — isto é,
   o modelo prevê 0 ali e o resíduo passa a ser o próprio ponto: `amp0p8` = 0,330
   nas 7 células, `amp0p3` = 0,683 nas 7, `amp0p5` e `amp0p6` = 0,330 nas células
   mais fortes. E 0,330 é a **borda inferior do gráfico** do artigo (20 kN);
   0,683 é o **último ponto legível** do digitalizador. Não é erro de física: é o
   modelo indo a zero na fratura que o paper declara contra uma curva que acaba
   antes. Nenhuma forma pode "acertar" um ponto que não foi medido. (As três
   restantes — `amp0p25` 0,407 · `amp0p4` 0,140 · `fig2` 0,062 — não saturam.)
2. **A grade melhora monotonicamente na direção do cliff** (`D_on`→1, `q`→∞).
   Ou seja: nesta métrica, **o dado prefere o cliff à rampa** — o que é o mesmo
   veredicto do PR-24 visto pelo outro lado. A métrica vertical não distingue as
   duas formas nesta fonte.

**G4 respondido:** a perda de seção **atravessa** o `loose_arrest_floor = 0,25`
(`fig2` termina em 0,140; `amp0p5` em 0,000). Coerente com a leitura de código
(§1) e provavelmente desejado — a fratura ignora auto-travamento — mas fica
**registrado** como acoplamento entre duas formas adotadas em momentos distintos.

**G5 respondido:** sem o candidato, **nenhuma** das 7 passa o tripé sem trim —
MAE 0,054–0,101 e res.máx **0,161–0,481**, todas violando o pico. A forma faz
trabalho real; não morre calada como o `flank_s_crit`.

---

## 6. Emendas recomendadas ANTES de assinar

Os três defeitos são de **mensurabilidade**, não de rigor — corrigi-los **aumenta**
a exigência:

**E1 — tolerância horizontal no trecho vertical.** Onde `|dr/dN|` excede o que a
digitalização resolve, pontuar em **vida**: *o N em que o modelo cruza cada nível
de `r` deve cair dentro de ±15 % do N medido* — exatamente o gate que o **PR-39 já
usou** ("cliff capturado dentro de ±15 % do medido"). Métrica bem-posta, e mais
dura que um `res.máx` que o ruído do dado já viola.

**E2 — separar as duas afirmações que o prereg conflaciona.** São claims distintas
com evidências distintas:
- **(a) prever QUANDO** o colapso começa (relógio D-N) — **fechada pelo dado**:
  orçamento pede 5 %, scatter de espécime dá 44 %;
- **(b) prever a FORMA** do colapso dado o quando — **aberta, e §0/§5 mostram que
  funciona**.

Testar (b) exige tirar (a) do caminho: `N_f` **lido** da matriz de ensaios (dado
publicado, mesma classe de `emb_um`/`delta_spectrum`/`trim_n_max`). Precedente
adotado: `LI_2022_TRIBOINT` roda com `fat_C1` per-material ancorado no `N_frat`
**medido**. Custo honesto a declarar: com 7 curvas e 44 % de scatter, "ler `N_f`"
são **7 números para 7 curvas**, e a claim cai de *"o modelo prevê a vida"* para
*"o modelo prevê a curva dada a vida"*. Defensável — vida de fadiga de parafuso é
tratada estatisticamente em VDI 2230/ISO — mas tem de ser dito nesses termos.

**E3 — trocar o banco de prova.** `fig2_single` é a **pior** curva para gatear
(±0,90 de incerteza no colapso). O núcleo `amp0p4/0p5/0p6` é o melhor: incerteza
maior, mas rampas **mutuamente consistentes** (§4), o que permite gate de
*coerência* — a forma tem de servir as três com um par só —, mais forte que
ajustar uma curva.

---

## 7. Consequência para a lista F5 §B

O prereg é citado em `f5_excecoes_propostas.md` §B como a forma que, *"se passar,
dispensa os 7 trims da LIU_2025"*. **A medição diz o contrário:** ligar a rampa e
remover os trims leva a fonte de **7/7 para 1/7** — e em 4 dessas 6 quedas o
res.máx é literalmente o último ponto do dado (**borda da figura** em 0,330, fim
da digitalização em 0,683), não erro de modelo.

Isso **reforça** a ratificação do §B em vez de enfraquecê-la, mas muda a
justificativa: o trim não é "provisório enquanto a forma não existir" — a forma
existe e funciona. É **provisório enquanto o DADO não existir**. E isso aponta
para uma ação diferente da que o prereg supõe:

- **re-digitalizar as caudas com passo fino** abaixo de F/F₀ = 0,33 (o inset da
  Fig. 3 e a Fig. 2 podem dar mais pontos), ou
- **pedir aos autores as séries brutas de 200 Hz** do DH5902N — é dado que existe
  e que resolveria o colapso inteiro,

antes de gastar mais trabalho de forma.

---

## 8. Reprodutibilidade

Sondas deste estudo, em `New_Theory/` (**engine intacto** — a forma entra por
`loss_mechanisms=[...]`, nada de canônico foi tocado). Rodar da raiz do repo, com
o interpretador que tem `numpy`/`scipy` (aqui: Python 3.12):

| script | mede |
|---|---|
| `liu2025_ramp_tail_shape.py` | joelho/vida, lei D-N, colapso da cauda |
| `liu2025_ramp_untrimmed.py` | trimado vs curva inteira, perfil do resíduo (§1) |
| `liu2025_ramp_clock_discriminator.py` | `W_slip/ciclo` por amplitude, colapso de `f = r_dado/r_modelo` |
| `liu2025_ramp_paris_probe.py` | rampa Paris-integrada (1 constante), varredura de R, relógio Miner (§2) |
| `liu2025_ramp_prereg_gates.py` | grade (`D_on`,`q`) da forma B1 + G1/G2/G4/G5 (§5) — ~25 min |
| `liu2025_ramp_overlap_budget.py` | orçamento de precisão do relógio (§2) |
| `liu2025_ramp_gate_measurability.py` | incerteza do dado vs limiar do gate (§3) |
| `liu2025_ramp_shape_g3.py` | universalidade da rampa em coordenadas do joelho (§4) |

Baseline: `python New_Theory/parallel_batch.py --sources LIU_2025 --workers 6 --store`
Dado: `curve_library/digitized_csv/liu2025_M16_*.csv` (sem `_tozero`, conforme §2.1 do prereg)
