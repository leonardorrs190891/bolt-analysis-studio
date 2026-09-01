# P-9 EXECUTADA — frequência no `EmbeddingLoss`, e o gate no **alvo** foi a diferença

**2026-08-09** · assinada (*"assino tudo"*) · prereg **v2**
(`2026-08-09-p9-freq-embedding-prereg-v2.md`) · fingerprint
`d9a680664797` → **`337fc077c1dd`**.

## A forma

```python
def stage1_freq_gate(mat, freq):        # (f_ref/freq)^n ; n=0 => 1.0 exato
    ...
target = (mat.emb_depth * conformance * settling
          * stage1_freq_gate(mat, freq)     # ← no ALVO
          + emb_load_frac * ...)
```

**Zero números fitados:**

| constante | valor | procedência |
|---|---|---|
| `s1_freq_exp` | **1,0** | **D-V, assinado** — a mesma lei `1/f` do canal de flanco, transferida |
| `s1_freq_ref` | **5,0 Hz** | **input**: 4 das 5 curvas do `YANG_2019` rodam a 5 Hz |

## O resultado, com as 4 curvas de controle bit-idênticas

| curva | f | MAE/res.máx/σ | viés |
|---|---:|---|---:|
| `amp0p4_5Hz` | 5 | 0,0995 / 0,1423 / 0,0773 | **idêntica** |
| `amp0p6_5Hz` | 5 | 0,0857 / 0,5170 / 0,1534 | **idêntica** |
| `varamp` ×2 | 5 | — | **idênticas** |
| **`amp0p6_10Hz`** | **10** | 0,0552→**0,0310** · 0,0886→**0,0665** · 0,0365→**0,0351** | **−0,0524 → −0,0097** |

**As três pernas melhoram; o viés cai 81 %.** E a inércia nas 4 de 5 Hz é **por
construção** (em `f_ref` o fator é 1,0 exato), não por sorte.

## Gates 6/6

| gate | medido |
|---|---|
| G1 default inerte | Δ = 0,000000000 em 6 fontes ✅ |
| G2 as 4 de 5 Hz bit-idênticas | ✅ |
| G3 viés anda ≥50 % para zero | **81 %** ✅ |
| G4 melhora nas 3 pernas | ✅ |
| G5 censo não cai | **139**, inalterado ✅ |
| G6 suíte completa | ✅ |

Store re-carimbado: batch paralelo (209 em 26 min) + o `exemplo_m12_sintetico`
pelo método direto que o `CLAUDE.md` prescreve ⇒ **210 uniformes**.

## ⚠️ A v1 passou os gates sendo um NO-OP — a lição mais cara do dia

A primeira forma gateava o **incremento** `d_delta`, seguindo o precedente do
`stage1_amp_gate`. **F1–F4 passaram** e o efeito era de **1,5 %** (viés
−0,0524 → −0,0516).

**Causa medida:** `N_emb` = **50** ciclos, curva de **5300** — **106× a
constante de tempo**. A fração do alvo atingida é `1 − e^{−n/N}` = **1,0000 com e
sem gate**. Gatear o incremento de um canal **saturado** muda *quando* ele
completa, não *quanto*.

Duas lições distintas saem daí:

1. **De física:** o PR-3 pôs o gate de **amplitude** no incremento *de
   propósito* (*"sub-limiar o assentamento fica lento, não menor"*) — correto
   para amplitude. Para **frequência o argumento inverte**: o mesmo número de
   ciclos a 10 Hz dispõe de **metade do tempo**, logo consolida **menos**, não
   "mais devagar". Copiar o precedente sem checar o sinal do argumento foi o
   erro.
2. **De método:** meus gates pediam **direção sem magnitude**, e por isso
   aprovaram um no-op. O G3 da v2 exige **≥50 %**. *"Anda na direção certa"* não
   é resultado se anda 1,5 %.

## O que a P-9 NÃO faz, declarado

A `amp0p6_10Hz` **continua fora do tripé**: σ **0,0351** contra limite 0,0250
(**1,40×**, era 1,46×). A P-9 explica o **viés**, não o **σ** — e o censo segue
**139**. O que subiu foi a **fidelidade física**, não o placar.

E as outras 4 fontes da população P-9 (`ECCLES`, `LIU_2025`, `LU_2024`,
`YANG_2023_AME`) são **mono-frequência**: lá o parâmetro é inseparável de
`N_emb` e **não foi aplicado**. A P-9 fecha para 1 curva de 8.

## Reprodutibilidade

```bash
py -3.12 -m pytest tests/ -q
PYTHONPATH=src py -3.12 New_Theory/regra_de_parada_triagem.py
```
