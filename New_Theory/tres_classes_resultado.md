# Varredura das 3 classes (L25) nos 39 form-limited — **36 são forma mesmo; 3 reclassificam**

**Data:** 2026-07-28 · **Pós-assinatura do S4** · **Diagnóstico, não adoção** (sem gates)
**Store:** fingerprint `294808504d83` · Script: `tres_classes_varredura.py` (pós-processamento puro)

---

## 0. Resultado em uma linha

A hipótese de que "parte dos 39 pode ser data/metric-limited" era **quase toda falsa**:
**36/39 são FORM-limited legítimos** — o resíduo vive no meio da curva ou em trechos
rasos onde a métrica é bem-posta. A fila de formas do §E é trabalho real, não moldura.

| classe | n | ação |
|---|--:|---|
| **FORM-limited** | **36** | fila de formas (kernel A/B/C etc.) — inalterada |
| **METRIC-limited** | 2 | `yang2019_M10_amp0p6_5Hz` (±3 % de N já vale **0,21** em r no pico) e `yang2019_M10_varamp_small_to_large` (**0,26**) — colapso terminal quase-vertical, mesma classe do Liu 2025; candidatos a **trim com prova** (a regra do trim é aplicada por julgamento, como ratificado) |
| **DATA-limited** | 1 | `lu2024_M8_fig20_T22Nm` — res.máx no último ponto, dado termina em **0,112 ≈ FLOOR/moldura**; ação = dado (ou aceitar o pico terminal como artefato de moldura) |

## 1. O que isto muda na fila

1. **Nada a subtrair do kernel**: os grupos A (Chu/Yang2019/Karlsen/Zhang2006), B (Lu
   nível) e C (Lu tigela) continuam como o diagnóstico de 2026-07-27 os deixou — com a
   exceção pontual de que **2 curvas do Yang2019 saem do alvo de forma** (são
   metric-limited terminais) e **1 do Lu2024 é moldura**, o que **enxuga o denominador**
   antes de qualquer FAIL2.
2. Os 2 metric-limited do Yang2019 têm o mesmo tratamento que a família Liu: **trim
   terminal com prova** (a fratura/colapso terminal não é pontuável verticalmente).
   Se adotados como trims, entram na próxima ratificação — **não** nesta (assinada).
3. Perfis medidos por curva (pico@, inclinação local, incerteza em r) ficam em
   `tres_classes_result.json` — insumo direto para os preregs de forma.

## 2. Honestidade do método

A varredura usa assinaturas **operacionais** (posição do pico, inclinação local do dado,
±3 % de N em unidades de r, proximidade do FLOOR) — não substitui leitura por fonte.
Um caso pode carregar as duas coisas (forma errada E cauda de moldura); a classe
reportada é a **dominante no ponto do res.máx**.
