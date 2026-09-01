# D-S — a CSV `caccese2009_tapered_45kN_rep2` corrigida

**2026-08-05** · decisão **D-S** (por delegação, MANDATO PERMANENTE) · prereg
`docs/superpowers/specs/2026-08-05-caccese-rep2-csv-prereg.md`. Classe **dado**.
Fingerprint **não muda** (`b70276f2fa43`) — o hash cobre o bloco `shared` + configs
adotadas, **não** os CSVs.

## O que estava errado

**9 dos 26 pontos traçavam a réplica errada** (a MÉDIA em vez da BAIXA), erro
+0,040 a +0,054 em t = 50, 150, 200, 500, 600, 700, 800, 900 e 1000 h. Os 16
pontos limpos carregavam offset sistemático constante de **−0,0039** (viés do
digitalizador). A assinatura é **binária, não gradual**.

Três provas independentes, e **nenhuma delas precisou do PDF**:

1. **Identidade ao dígito**: `rep2` em t=900 (0,7087) e t=1000 (0,7081) é
   *exatamente* `rep1` nesses tempos. Réplicas independentes não concordam a 4
   decimais.
2. **Não-monotonicidade**: 3 subidas (0,7736→0,7955 e 0,6825→0,7319) num ensaio de
   relaxação **puramente estática** em que todos os traços publicados decrescem.
3. **Resíduo do modelo**: troca de sinal em blocos, ±0,05, exatamente nos 9
   pontos — lido na sonda de anatomia da fila, sem tocar no artigo.

E uma prova externa: a polilinha **vetorial** da Fig. 9
(`page.get_drawings()`, resíduo de calibração **2,3e-5** em F/F₀, verificada por
redesenho sobre o render).

## Gates

| gate | resultado |
|---|---|
| **G1a′** acurácia do instrumento (resíduo de calibração ≤ 1e-4) | 2,3e-5 ✅ |
| **G1b** monotonicidade (zero subidas na saída) | 3 → **0** ✅ |
| **G3** isolamento (nenhuma outra curva muda) | **6 de 7 bit-idênticas** ✅ |
| **G4** round-trip à Tabela 5, atribuição inequívoca (≥ 2×) | 44,8 kN · RMS **0,0045** · **11,07×** ✅ |
| **G5** piso re-medido, `limite_sres` inalterado | σ 0,0234 → **0,0100**, limite **0,0250** ✅ |
| **G2** a métrica pode piorar | MAE +20 %, registrado ✅ |

### Efeito na curva

| | MAE (÷0,05) | res.máx (÷0,10) | σ_res (÷0,025) | tripé |
|---|---|---|---|---|
| antes | 0,0292 (0,58×) | 0,0468 (0,47×) | **0,0258 (1,03×)** | REPROVA |
| **depois** | 0,0349 (0,70×) | 0,0452 (0,45×) | **0,0083 (0,33×)** | **PASSA** |

σ cai **3,1×**. **A predição registrada era 0,0349 / 0,0452 / 0,0083 e bateu
exato.** O MAE **sobe 20 %** porque a réplica verdadeira é mais baixa e o viés do
modelo cresce — o G2 declarou isso por escrito antes de medir, e o precedente
manda fazer (ROUSSEAU `hdpe_t10` foi corrigida em 2026-08-02 saindo de MAE 0,058
para 0,101).

## ⚠️ Duas coisas que NÃO saíram como previsto, e ficam escritas

**(a) O piso de σ não caiu na banda prevista.** O prereg previa 0,002–0,009; o
medido é **0,0100**, ~11 % acima do topo. Causa rastreável: a re-medição compara a
`rep2` **corrigida** contra a `rep1` **não corrigida** — que o **G4 tirou do
escopo** —, e o offset residual de −0,004 dela entra na conta. As estimativas
vetor-contra-vetor do subagente (0,0015–0,0087) comparavam **as duas** corrigidas.
A conclusão sobrevive (piso < 0,025 ⇒ `limite_sres` fica no global), o número não.

**(b) O piso de MAE SUBIU, de 0,0372 para 0,0543** — e isso é correto: a réplica
verdadeira é mais baixa, então as duas divergem mais. Consequência que vale
registrar:

> **O modelo está mais perto de cada réplica do que elas estão uma da outra.**
> MAE modelo↔`rep1` = **0,0203** · modelo↔`rep2` = **0,0349** · `rep1`↔`rep2` =
> **0,0543**.

É a afirmação mais forte disponível para uma condição com réplicas — e ela **não
precisa de exceção**, porque a curva passa por mérito. (Sob a régua F7 o MAE de
0,0349 estaria abaixo da barra PROVA de 0,0543 e até da barra FORTE de 0,0384.)

## Escopo: a `rep1` saiu **por reprovação do gate**

A `rep1` estava no escopo e foi retirada porque **reprovou o G4**: casa a linha
certa da Tabela 5 (44,7 kN, RMS 0,0051 — a melhor das três) mas a 2ª alternativa
fica a **1,30×**, e o gate exige ≥ 2×. A reprovação é **real**: os traços MÉDIO e
ALTO da Fig. 9 terminam em 0,6805 e 0,6828 — **0,0023 de diferença** — e o
round-trip pela Eq. (2) genuinamente não os separa. Como a `rep1` muda **zero**
pontos acima de 0,02 (máx desvio 0,0139) e já passava o tripé, corrigi-la seria
trocar dado bom por dado bom de procedência incerta. **A razão mínima não foi
afrouxada de 2 para 1,3.**

Fica **não corrigido e documentado**: o defeito menor da `rep1` (1 subida) e o
offset de +0,0008.

## Fora de escopo, disponível

* **3ª réplica** (traço 188, linha **43,9 kN** da Tabela 5, fim 0,6828): não
  digitalizada. Levaria o par declarado a **n=3** e mudaria o **denominador**
  (205→206) — decisão do professor pelo precedente LU. Medido que o modelo **a
  passaria** (MAE 0,0263 · máx 0,0296 · σ 0,0054).
* **Protruding preta** (2ª tracejada da Fig. 9): idem, criaria um 2º par
  declarado.
* **Figs. 6/7** (`compblock`, `retighten`): polilinhas fragmentadas em 8–26
  pedaços; extração sem costura devolve F₀ absurdos. Não tocadas.

## Censo

| | antes | depois |
|---|---|---|
| tripé (estrita) | 135/205 | **136/205** |
| resolvida/declarada | 175/205 | **176/205** |
| **fila form-limited** | 2 | **1** |
| CACCESE_2009 | 6/7 | **7/7** |

A fonte fecha **100 %**. Resta na fila **uma** curva: `li2022ti_axialmin_10Hz`,
cuja causa está medida e **não é constante** — o modelo é cego à frequência nesta
janela (perda 0,1539/0,1537/0,1535 a 10/15/20 Hz contra 2,0× de variação no dado),
logo o remédio é uma **lei de frequência**. Ver
`fila_form_limited_3_anatomia.md`.

## Correções de documentação no mesmo arco (G6)

A nota de aparato (`caccese2009.md`) tinha **três** erros, todos consequência da
mesma medição, corrigidos em `edce022`:

1. *"Fig. 9's 4 raw traces (2 tapered + 2 protruding)"* → são **5** (3 tapered).
2. *"an interpolated (not pixel-verified) stretch ≈420-980 h"* → **nomeia o
   mecanismo errado**. Interpolação está descartada por aritmética (interpolar
   0,6825@400 → 0,6459@1100 daria trecho **monótono**). É **cópia da réplica
   errada**. Uma nota que se lê como *"dado um pouco mais mole aqui"* dizia, de
   fato, *"curva errada aqui"* — e foi ela que fez a contaminação parecer
   aceitável.
3. Rótulos "upper/lower" trocados: a `rep1` segue o traço do **MEIO**; o **upper**
   é a 3ª réplica não digitalizada.
