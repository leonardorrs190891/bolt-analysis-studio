# ADOÇÃO D-AD — o `gth` na fonte 8/8 STICK: mediana **−27 %** com **1 número**, censo inalterado

**2026-08-10** · prereg `7c15134` (gates congelados antes de medir) · **passo de QUALIDADE** sob
o gate PR-37′, declarado como tal **antes** de medir.

## Duas medições independentes se encontrando

1. Outra sessão embarcou hoje o **`gth`** (`74c17d9`) — *ratchet de regime de STICK*,
   default-inerte, 7 testes de contrato, conservação fechada nos dois lados. Ele acumula
   **somente** quando `slip_amp ≤ 1e-9`, e em gross slip é **0 exato**.
2. O meu censo instrumentado do mesmo dia mede o **`YANG_2021` como 8/8 STICK**, e o trabalho
   profundo da fonte isolou **"perda sustentada sob stick"** como o defeito, com
   `ρ(resíduo, N) = +1,00` em 6 curvas (rampa: déficit de taxa que acumula).

⚠️ **A outra sessão declarou NÃO-ADOÇÃO do `gth`, e estava certa para o alvo dela:** testou no
`YANG_2019`, que o censo mede como **5/5 PARCIAL**, onde o mecanismo é **inerte por
construção**. O mecanismo estava certo e a **fonte** era a errada. Isto não corrige a decisão
dela — aplica o mecanismo à fonte para a qual ele foi desenhado.

## ⚠️ Eu quase quebrei uma trava de procedência

A varredura **conjunta** achou `gth_q = 7,0` com `k = 3e-8` dando **tripé 3→4 com custo ZERO** —
melhor que qualquer célula no expoente legítimo.

**Recusado.** `gth_q = 3,8` é a **lei do IJPEM** (`N_L ~ δ^{−3,8}`, PR-21), declarada como
constante de procedência no prereg da outra sessão (§G1-T13). Mover um expoente de literatura
para fechar uma curva é o oposto da disciplina — e a tentação era grande justamente porque
funcionava. Fica registrado como **rota recusada com número**, não como rota não vista.

## A dose: a maior com custo zero, não a que sobe a contagem

No `q` travado:

| `gth_k` | tripé | saem | pioram >0,01 | mediana MAE |
|---|---|---|---|---|
| 1e-7 | 3 | 0 | 0 | 0,0362 (−13 %) |
| **1,5e-7** ✅ | **3** | **0** | **0** | **0,0304 (−27 %)** |
| 2e-7 | **2** | 1 (`r2`) | 3 | 0,0304 |
| 2,5e-7 | 4 | 1 (`r2`) | 3 | 0,0312 |
| 3e-7 | 4 | 1 (`r2`) | 3 | 0,0310 |

As doses que **fecham** curvas (`2,5e-7`/`3e-7` põem `r1` e `amp1p0` no tripé) **tiram a `r2`** e
pioram 3 ⇒ reprovariam o *"nenhum caso pior +0,01"* do PR-37′. **Escolhi a que passa o gate.**

## Efeito medido nas 8

| curva | antes | depois | ΔMAE |
|---|---|---|---:|
| `amp0p5mm_ax8kN` | 0,0434/0,1297/0,0441 | 0,0324/0,1083/0,0388 | **−0,0110** |
| `amp0p6mm_ax8kN_r1` | 0,0264/0,1012/0,0317 | 0,0167/0,0813/0,0268 | **−0,0097** |
| `amp0p6mm_ax8kN_r2` ✅ | 0,0403/0,0487/0,0088 | 0,0483/0,0587/0,0103 ✅ | +0,0080 |
| `amp0p6mm_ax8kN_r3` ✅ | 0,0209/0,0387/0,0093 | 0,0285/0,0387/**0,0073** ✅ | +0,0076 |
| `amp0p7mm_ax11p2kN` ✅ | 0,0130/0,0470/0,0167 | 0,0159/**0,0272**/**0,0111** ✅ | +0,0029 |
| `amp0p8mm_ax6kN` | 0,0739/0,2078/0,0607 | 0,0542/0,1737/0,0511 | **−0,0196** |
| `amp1p0mm_ax2kN` | 0,0541/0,1527/0,0454 | 0,0285/0,1074/0,0320 | **−0,0256** |
| `fig2_typical` | 0,0609/0,1970/0,0611 | 0,0404/0,1614/0,0511 | **−0,0205** |

**5 melhoram, 3 pagam ≤ +0,008, nenhuma sai.** A `amp1p0` melhora 47 % no MAE e a `fig2` 34 %.
As 3 que pagam são as que **já estavam no tripé** e continuam nele com folga.

## Gates — medidos

| # | gate | resultado |
|---|---|---|
| **W1** | `gth_q`/`gth_dref` nos defaults (procedência) | ✅ asserção no executor + conferido no material efetivo (3,8 / 5e-4) |
| **W2** | nenhuma sai do tripé | ✅ 3 → 3 |
| **W3** | nenhuma piora MAE >+0,01 | ✅ **0** (máx. +0,0080) |
| **W4** | mediana da fonte cai ≥20 % | ✅ 0,0419 → 0,0304 = **−27 %** |
| **W5** | isolamento nas outras curvas em **STICK** | ✅ Δ = **0,000000000** em 10 sondas |
| **W6** | censo 144 → 144 | ⚠️ **NÃO AVALIÁVEL** — base movida por sessão paralela; ver seção própria |
| **W7** | suíte completa | (abaixo) |
| *extra* | predição do prereg reproduzida nas 8 | ✅ |

⚠️ **O W5 era o gate novo e valia cada minuto.** É a primeira constante desta campanha cujo
**alcance é definido por REGIME** (`slip_amp ≤ 1e-9`), não por chave de config — a biblioteca tem
**18** curvas em stick e só 8 são desta fonte. Δ=0 exato nas 6 outras (`YANG_2023` ×3,
`LIU_2025` ×2, `ROUSSEAU` ×1) prova que a chave per-fonte confina o mecanismo. Assumir isso
teria sido plausível **e** não-medido.

## ⚠️ O W6 saiu 147, e o motivo NÃO é esta adoção — o store estava PARCIALMENTE carimbado

O prereg congelou **W6: censo 144 → 144**. O re-stamp devolveu **147**. Investigado antes de
escrever qualquer número:

* O `diff` do `adopted_configs.json` é de **4 inserções / 2 remoções, e é todo meu**
  (`gth_k` + a sua `prov`). Não havia mudança de outra sessão pendente ali.
* O store, porém, tinha **209 registros no fingerprint antigo** (`d197fc4c491c`) e **1** — o
  sintético — em **`ca1473211659`**. Ou seja: a sessão paralela **adotou e sincronizou os
  documentos**, mas o re-stamp dos 209 não foi concluído. É exatamente o cenário que o
  `CLAUDE.md` registra: *"um store escrito por sessão interrompida só se valida re-simulando —
  o hash não denuncia divergência"*.
* Prova de que os documentos já estavam certos: `test_meta_numeros_nao_envelhecem` passa
  **16/16** contra o censo 147 **sem eu tocar em nenhum número publicado**.

⇒ **O +3 é da adoção deles, que o store ainda não refletia. A minha contribuição é 0**, e isso
está medido de forma independente do censo: **W2** (tripé 3→3 dentro do `YANG_2021`) e **W5**
(Δ = 0 exato fora dela). O batch **reparou** a inconsistência em vez de criar uma.

**Estatuto honesto do W6: NÃO AVALIÁVEL COMO ESCRITO** — a linha de base mudou entre o
congelamento e a medição, por escrita de outra sessão. Não o declaro aprovado. A **intenção**
dele (esta adoção não move o censo) está coberta por W2+W5, ambos medidos contra o store
anterior.

⚠️ **Lição de método:** um gate de **censo absoluto** é frágil sob escritor paralelo. O gate
robusto é o **diferencial confinado** — "nada muda fora do meu escopo" (W5) mais "nada sai
dentro dele" (W2) —, que não depende do que outra sessão fez no intervalo.

## O que isto NÃO é

**Não é ganho de censo** — declarado no prereg **antes** de medir, para que o resultado não fosse
lido como contagem. Nenhuma das 5 curvas fora fecha: `amp0p5` fica em σ 1,55×, `r1` em 1,07×,
`amp0p8` em 2,04×, `fig2` em 2,04×, e a `amp1p0` chega a **σ 1,28×** (era 1,81×).

**A `r1` a 1,07× é a mais próxima que esta fonte já esteve** — e ela está na fila da P-14.

## O que fica

* A rota **forma** que o trabalho profundo do `YANG_2021` especificou existe agora no engine e
  **age na direção certa**: os 6 resíduos-rampa encolhem.
* O que impede o fechamento não é mais "falta mecanismo": é que a dose que fecharia **cobra de
  uma réplica**. Isso muda a classe do bloqueio de *forma faltante* para **tensão réplica-vs-fit**
  — a mesma que o D-I resolveu no CACCESE pelo **centro das réplicas**, e que aqui esbarra em
  `r1`/`r2`/`r3` terem janelas de métrica diferentes (r1 começa em N=500, r2/r3 em N≈20).
* **Candidato natural para a próxima rodada:** alinhar as janelas das 3 réplicas antes de
  re-escolher a dose. Se a comparação passar a ser sobre o mesmo intervalo, o "custo na `r2`"
  pode ser artefato de janela — exatamente o que o trabalho profundo mediu como causa dos sinais
  de viés opostos.

## Reprodutibilidade

```bash
py -3.12 -u New_Theory/ataque_curva.py yang2021_amp1p0mm_ax2kN
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
py -3.12 -m pytest tests/ -q
```
