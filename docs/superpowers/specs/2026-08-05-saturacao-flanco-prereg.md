# Prereg — SATURAÇÃO DO CANAL DE FLANCO por profundidade restante

**2026-08-05** · decisão D-Q (por delegação, MANDATO PERMANENTE) · fingerprint
de partida `b072b24fd3a8`.

## ⚠️ Slip de ordem, declarado antes dos gates

**O valor `flank_fret_depth = 3,5e-6` foi encontrado ANTES deste prereg**, numa
varredura sobre o LI_2022. A varredura era a medição, não pré-teste — a ordem
estava errada, pela segunda vez nesta sessão.

**O que preserva a disciplina:** existe um **held-out que eu não toquei**, e o
gate que decide é sobre ele. Nada abaixo é ajustado ao que já sei do LI_2022;
o G1 pergunta algo cujo resultado eu **não conheço**.

## A forma, e o estado que ela reativa

```
d_w *= max(0, 1 − state.delta_thread_fret / flank_fret_depth)
```

Mesma estrutura *state-based* que o `EmbeddingLoss` recebeu em 2026-07-02: o
incremento depende da **profundidade que ainda falta**, não do relógio.
`flank_fret_depth = 0` ⇒ OFF exato (**G0 já verificado: bit-idêntico**).

**`delta_thread_fret` já era acumulado** (engine linha 1853) e lido **só** para
contabilidade de energia (linha 2374) — nunca realimentava a lei que o alimenta.
Esta forma fecha esse laço.

Física: o fretting de flanco remove material até a folga acomodar o movimento;
então o contato re-conforma, a área cresce, a pressão cai e o transporte líquido
para. É o regime de **shakedown** que o docstring de `flank_wear_from_slip` já
cita (Mantyla 2020 / Juoksukangas 2016).

## O que já se sabe (LI_2022 — NÃO é o gate que decide)

| dep | full σ | full MAE | 10 Hz | 15 Hz | 20 Hz | tripé |
|---:|---:|---:|---:|---:|---:|---:|
| base | 0,0365 | 0,0317 | 0,0526 | 0,0298 | 0,0201 | 2/4 |
| 5,0e-6 | 0,0274 | 0,0250 | 0,0560 | 0,0300 | 0,0172 | 2/4 |
| **3,5e-6** | **0,0244** | 0,0233 | 0,0573 | 0,0310 | 0,0160 | **3/4** |

E o **teto em pares** (charter, pré-teste 4) já mostrou que **saturação e
re-atribuição BRIGAM**: a razão de frequência vai de 0,529 (re-atribuição pura)
para 0,593 → 0,814 conforme a saturação aperta, porque o sinal de frequência
está na **magnitude** do flanco e a saturação a corta. **Este prereg adota a
saturação SOZINHA**; a re-atribuição fica de fora, falsificada como par.

## G1 — O GATE QUE DECIDE: transferência para o LIU_2016 (CEGO)

O `LIU_2016` também tem o canal de flanco ativo (`flank_wear_on=1`,
`flank_amp_exp=1,5` — **mesma forma**, nível diferente) e está **14/14 no
tripé**. Aplico a **MESMA** `flank_fret_depth`, compartilhada.

**Por que é o teste mais severo disponível:** as curvas do LIU_2016 correm até
**1e6 e 5e6 ciclos** contra 200k–330k do LI_2022. A saturação age sobre
profundidade **acumulada**, logo corridas longas saturam **mais**. E várias
estão colada nos limites — `fig9a_m40nm` MAE 0,0477 · `fig7_run1` σ 0,0225 ·
`fig9a_m30nm` σ 0,0227: não há folga para absorver erro.

- **G1:** o `LIU_2016` permanece **14/14**. Uma única curva que saia ⇒
  **FALSIFICADO (não transfere)**, e a forma passa a ser fudge por fonte.
- **G2:** nenhuma das 14 piora > **+0,010** em qualquer perna.

## Gates restantes (IMUTÁVEIS)

- **G3 (ganho, já conhecido):** a `axial_10Hz_full` entra no tripé
  (σ ≤ 0,025). Declarado como **conhecido**, não como mérito do gate.
- **G4 (nenhum pior no LI_2022):** nenhuma das 4 piora > +0,010 (medido:
  10 Hz +0,0047 · 15 Hz +0,0012 · 20 Hz melhora).
- **G5 (fronteira interior):** o ótimo **não** pode estar no extremo da grade
  varrida (`4e-5 … 1,5e-6`). Se estiver, **estender antes de adotar**.
- **G6 (escala física declarada):** 3,5 µm contra `emb_depth` = **9,5 µm** da
  tabela VDI para este rig — mesma ordem, a escala de rugosidade da interface,
  que é onde o fretting de flanco opera. Se o valor adotado sair dessa ordem
  (fora de 0,5–50 µm), **declarar** que é fit sem escala física.
- **G7 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos 210 +
  censo/docs/páginas/testes no MESMO commit; `VarSpec` do campo novo no
  explorador; tripwire de DOF revisto.

### Ramos

- **ADOTA** — G1..G6.
- **FALSIFICADO (não transfere)** — G1 falha: a forma quebra o LIU_2016 ⇒ é
  ajuste por fonte, não mecanismo. **Prefiro este ramo a soltar um segundo
  `flank_fret_depth` por fonte** — o valor do candidato está na transferência.
- **NÃO ADOTA (fronteira)** — G5 falha e a extensão não converge.

## Previsão registrada

**Não sei se o LIU_2016 sobrevive.** A saturação corta o flanco, e as curvas
longas dele acumulam 15–25× mais profundidade que as do LI_2022 — com
`dep = 3,5e-6` o fator de saturação nelas pode ir a **zero**, matando o canal
por inteiro. Se isso acontecer, o MAE delas piora e o G1 reprova.

**Palpite honesto: 50/50.** O que me faz apostar em transferência é que
`k_wear_flank` do LIU_2016 é **5× menor** (4,32e-14 vs 2,15e-13), logo ele
acumula profundidade **mais devagar** — o que pode compensar a corrida mais
longa. Mas isso é aritmética de guardanapo, não medição, e é exatamente o que o
G1 vai decidir.
