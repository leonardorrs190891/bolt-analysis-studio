# YANG_2021 a fundo: a fonte está em **STICK PERMANENTE**, e o tripé completo não é alcançável com as alavancas do mandato

**2026-08-10** · pedido direto do professor (*"deep work on Yang 2021 … untill all cases are in
tripe"*) · só-leitura · **nada adotado** · store `061ce184eca5`.

## Resposta curta

**Não consegui pôr as 8 no tripé, e a razão não é falta de ajuste — é uma forma que falta.**
A fonte está em **stick permanente medido**: o slip transversal é **0,000 em 100 % dos
ciclos**, nas 8 curvas, com deslocamento imposto de 0,5 a 1,0 mm. Sem slip, três dos quatro
canais de perda têm **driver zero**, e o modelo só dispõe de embedding (que satura) e creep.
O dado exige 0,09 a 0,23 de queda sustentada.

Estado: **3 de 8 no tripé** (`r2`, `r3`, `amp0p7`), MAE médio 0,0416.

## 1. O defeito, nomeado: **rampa**, não nível

Resíduo médio por octil de N (`+` = modelo acima do dado = perde pouco):

| curva | o1 | o4 | o8 |
|---|---|---|---|
| `amp0p8mm_ax6kN` | +0,013 | +0,046 | **+0,180** |
| `fig2_typical` | +0,003 | +0,032 | **+0,173** |
| `amp1p0mm_ax2kN` | +0,004 | +0,035 | **+0,134** |
| `amp0p5mm_ax8kN` | −0,000 | +0,021 | **+0,115** |
| `amp0p6mm_ax8kN_r1` | +0,003 | +0,008 | +0,080 |
| `amp0p7mm_ax11p2kN` | −0,001 | +0,001 | +0,039 |

Todas partem de ≈0 e crescem monotonicamente: **`ρ(resíduo, N) = +1,00`**. É **déficit de
taxa que acumula**, não erro de nível.

⚠️ **Isto corrigiu o meu próprio diagnóstico.** O `|viés|/MAE = 1,00` que eu instalei no shell
ontem é **ambíguo**: resíduo de sinal único dá 1,00 tanto para um degrau uniforme quanto para
uma rampa que parte de zero — e eu quase propus alavanca de **nível** para um déficit de
**taxa**. O shell agora imprime `ρ(resíduo, N)` e nomeia a diferença (`|ρ|≥0,7` ⇒ rampa;
`≤0,3` ⇒ offset).

## 2. A causa-raiz, medida por instrumentação direta

Envolvi `resolve_transverse_slip` num wrapper (como o `CLAUDE.md` manda — *"não infira do
decomp"*):

| curva | δ imposto | chamadas | slip máx | zeros |
|---|---|---|---|---|
| `r2` | 0,6 mm | 29 298 | **0,000** | **100 %** |
| `amp0p8mm_ax6kN` | 0,8 mm | 11 200 | **0,000** | **100 %** |
| `amp1p0mm_ax2kN` | 1,0 mm | 6 500 | **0,000** | **100 %** |
| `fig2_typical` | 0,8 mm | 11 900 | **0,000** | **100 %** |

E a decomposição em valor **absoluto** confirma: `wear` = `rotational` = `thread_fretting` =
**0,0000 nas 8**. O modelo gasta tudo como embedding nos ~100 primeiros ciclos e depois
estabiliza.

Pela regra das três causas do `CLAUDE.md` (driver / constante / gate): o gate está **aberto**
(`slip_onset_W = 0`) e as constantes **não** estão zeradas (`k_wear_spec` 5e-14,
`tr_loose_gain` 2,0) ⇒ é o **driver**.

## 3. E a saída do stick é um PENHASCO, não uma rampa

Sonda de `c_bend` (o que governa `k_tr` no ramo `bending` do pack LEGACY desta fonte):

| `c_bend` | slip máx | fração de ciclos com slip | MAE |
|---|---|---|---|
| **0,1** (vigente) | 0,000 | 0 % | 0,0739 |
| 0,3 | **8,0e-4 m = o δ INTEIRO** | 98 % | **0,5984** |
| 1,0 … 30,0 | 8,0e-4 m | 79–82 % | 0,71–0,72 |

⇒ **não existe regime intermediário**: o modelo só sabe *travado* (perde 0,02) ou *gross slip
pleno* (colapsa para zero, MAE 0,60). O dado está no meio. É a bifurcação que o `CLAUDE.md`
registra para `loose_arrest_floor = 0` (*"runaway puro, sem meio"*) — e aqui ele é 0,0.

Em disp-mode a fórmula é `slip = max(0, δ − delta_free − F_slip/k_tr)`, **sem teto**: assim que
o onset cai abaixo de δ, o slip salta para quase δ.

## 4. Por que a P-14 (microslip) não resolve — e o motivo está no código

A P-14 é *"microslip abaixo do onset"*, seus **4 alvos incluem 3 destas curvas**, e o mecanismo
**já existe** (`k_partial_slip`, default 0 = OFF). Medido: **inerte em 6 ordens de grandeza**
(1e-6 a 1,0), bit-idêntico.

E a leitura do engine explica por quê — a cadeia está bloqueada em **três** pontos:

```python
if (k_partial_slip > 0 and slip_regime_mode == "cattaneo_mindlin"):
    ...  W_slip_cycle += dE_partial      # so alimenta o DRIVER DO DANO
if c_D > 0 and W_ref > 0:                # e c_D = 0,0 nesta fonte
```

`dE_partial` **não é perda de pré-carga** — é driver de dano; o dano amplifica **wear**; e wear
precisa de **slip**, que é zero. O `slip_regime_mode` está certo (`cattaneo_mindlin`, do pack
LEGACY), mas isso não basta.

⇒ **a P-14 não podia funcionar aqui por construção**, e o null pré-medido dela (*"saldo 0 em
toda dose"*) fica **explicado**, não apenas confirmado.

## 5. O único canal sustentado disponível é o creep — e ele troca as boas pelas ruins

`C_creep` é dirigido por **tempo**, então decai continuamente. Varredura source-wide:

| `C_creep` | tripé | as 5 fora | as 3 dentro |
|---|---|---|---|
| ×1 (vigente) | **3** | σ 1,3–2,5× | passam |
| ×4 | 1 | melhoram forte | `r2`/`r3` quebram |
| **×8** | **0** | **4 com MAE E res.máx dentro** (σ 1,2–1,8×) | `r2` **0,219** · `r3` **0,199** |

A ×8 as curvas fora ficam a **um passo** (só σ): `amp0p8` 0,040/**0,082**/0,043, `amp1p0`
0,047/**0,073**/0,031, `amp0p5` 0,040/**0,073**/0,034, `fig2` 0,041/**0,089**/0,044.

Mas `r2` e `r3` — as duas melhor digitalizadas (56–57 pontos) e que **passam hoje** — são
destruídas. **Uma constante da fonte não serve às duas populações** ⇒ não adotável, e um
`C_creep` **per-curva** dentro do mesmo rig, com os mesmos corpos-de-prova, não tem
justificativa física: seria fit puro.

## 6. O input que o paper varre não chega ao modelo

A fonte é *"composite excitation"*: deslocamento transversal **+ carga axial**, ambos a 10 Hz
com 90° de fase, e o critério do artigo é **ξ = amplitude transversal / amplitude axial**, com
ξ crítico 0,075 separando afrouxamento de fadiga.

As amplitudes axiais do paper são **2 / 6 / 8 / 11,2 kN**, estão escritas no campo `notes` de
cada caso — e o modelo recebe **`F_amp_N` = 5640 N nas oito** (0,4·F₀, um default genérico).
Não existe campo modelado de carga axial.

⚠️ A nota de aparato **já registra** que alimentar o F_ax per-curva dá **Δ=0,0000** — e isso
é **verdade e esperado**: em disp-mode o slip vem de `delta_amp`, e `F_amp` só entra pelo canal
rotacional, que carrega 0,000 aqui. Ou seja: **a inércia do F_ax não é evidência de que a carga
axial não importa fisicamente** — é evidência de que o engine não tem por onde ela agir neste
regime.

## 6b. ⚠️ O NUMERO que fecha o diagnostico — e ele torna o `c_bend` CIRCULAR

Instrumentando `k_tr_transverse` e `F_slip_transverse` **dentro** da corrida (o mesmo
metodo do slip; um calculo avulso com `geom=None` deu 1,2e9 e estava **3.700x errado** —
outro instrumento morto pego pela propria disciplina):

| | valor medido |
|---|---|
| `k_tr` real | **3,2762e5 N/m** = 0,33 kN/mm |
| `F_slip` | 665 – 973 N |
| **onset = F_slip/k_tr** | **2,9696 mm** |
| **onset / δ** | **2,97** (δ=1,0 mm) a **4,95** (δ=0,6 mm) |

⇒ o modelo acredita que a junta absorve **3 mm de deflexao transversal ELASTICA** antes de
qualquer escorregamento. Para um M8 num dispositivo de cunha isso e' fisicamente enorme — o
parafuso estaria dobrado muito alem do elastico.

**E aqui esta o problema de fundo.** Esse `k_tr` vem de `c_bend = 0,1`, cuja procedencia diz:
*"fitado-this-rig … banda INSENSIVEL 0,02–0,15 — valor no centro, nao identificado alem da
banda"*. Mas a insensibilidade e' **consequencia do proprio valor**: com `c_bend` nessa faixa a
junta fica em stick, e em stick **nada depende de `c_bend`**. O ajuste foi insensivel porque o
mecanismo que ele governa estava desligado pelo valor dele mesmo. **A banda de insensibilidade
e' artefato do stick, nao evidencia de constante bem determinada.**

Sanidade fisica: para um M8, a rigidez transversal deveria ser ~1e7–1e8 N/m, dando
onset ≈ 0,1 mm ≪ δ ⇒ **gross slip**. E foi exatamente o que a sonda de `c_bend`=0,3 mostrou:
MAE **0,598**, colapso.

⇒ **A fonte expoe um problema estrutural, agora com numero:** com rigidez transversal
FISICA o modelo prediz colapso imediato; com a rigidez FITADA ele fica travado e nao perde
nada. **Nenhum dos dois regimes produz a queda gradual de 3 estagios que o dado mostra**, e o
ajuste vigente sobrevive por ser fisicamente implausivel na direcao que desliga o mecanismo.

## 6c. A cadeia de dano foi testada por inteiro — e a graduacao nao e' ESTAVEL

Com os companheiros ligados (`k_partial_slip` + `c_D` + `W_ref` + `k_dmg_mu`), a cadeia
**funciona mecanicamente**: o slip deixa de ser zero. Mas:

| `k_dmg_mu` | slip | MAE |
|---|---|---|
| 0,03 | **0,000** (bit-identico ao nominal) | 0,0541 |
| 0,06 – 0,2 | engata | pior que o nominal (nenhuma celula da grade melhorou) |
| 1,0 | δ inteiro | **0,39 – 0,69** |

Motivo, agora derivavel do numero: cruzar o onset exige que µ caia **3 a 5x**
(`k_dmg_mu·D ≥ 0,66–0,80`). Existe uma janela em que `onset ≈ δ` e o slip seria parcial — mas
**`D` e' monotona crescente**, entao o modelo *atravessa* a janela e termina em gross slip.
**Partial slip exigiria que o onset se ESTABILIZASSE perto de δ, e nada no modelo o
estabiliza.**

## 7. Duas rotas nomeadas## 7. Duas rotas nomeadas — as duas são FORMA NOVA de engine

Fora do mandato autônomo; ficam especificadas para decisão do professor.

**(a) Perda de pré-carga por partial slip.** Hoje `dE_partial` só alimenta o dano. Deixá-la
produzir um decremento de pré-carga direto (com o gate Cattaneo-Mindlin que já existe) daria
exatamente a **taxa sustentada sob stick** que a rampa pede, e sem passar pelo penhasco do
gross slip. É a rota mais direta e reusa 3 mecanismos existentes.

**(b) Acoplamento com a amplitude AXIAL** — o item 4 do roadmap (*"F_amp ↔ delta_amp
coupling"*), que a própria nota chama de *"project priority #4"*. É o que diferenciaria as
curvas fisicamente (ξ de 0,0625 a 0,50 no dataset) em vez de por constante per-curva. Sem ela,
as 8 curvas são, para o modelo, **o mesmo ensaio com δ diferente** — e o experimento do paper
fica invisível.

## O que fica desta rodada

* **`r2`/`r3`/`amp0p7` seguem no tripé** — nada foi tocado, nada regrediu.
* `amp0p8` e `fig2` já têm **exceção F5 assinada**; `amp0p5`, `r1` e `amp1p0` estão na fila da
  **P-14**, cujo null agora tem **explicação de código**, não só medição.
* **Ferramenta melhorada:** o `ataque_curva.py` passou a distinguir **rampa de offset** por
  `ρ(resíduo, N)` — o defeito de diagnóstico que este trabalho encontrou em mim mesmo.
* A leitura *"F_ax é inerte"* da nota ganha a qualificação que faltava: inerte **neste regime**,
  por ausência de caminho, não por irrelevância física.

## Reprodutibilidade

```bash
py -3.12 New_Theory/ataque_curva.py yang2021_amp0p8mm_ax6kN
```
Sondas no scratchpad: `y21_estado.py`, `y21_slip.py` (wrapper em
`resolve_transverse_slip`), `y21_cbend.py`, `y21_instr.py`, `y21_creep.py`. Todas só-leitura.
