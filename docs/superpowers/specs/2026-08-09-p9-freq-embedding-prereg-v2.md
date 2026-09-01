# Prereg **v2** — P-9: o gate de frequência vai no **ALVO**, não no incremento

**2026-08-09** · substitui `2026-08-09-p9-freq-embedding-prereg.md`, cuja forma
**passou os gates sendo um no-op medido**.

## Por que existe uma v2 — e o que ela ensina

A v1 aplicou `(f_ref/f)^n` ao **incremento** `d_delta`, seguindo o precedente do
`stage1_amp_gate`. Gates F1–F4 **passaram**… sobre um efeito de **1,5 %**:

| | antes | depois (incremento) |
|---|---:|---:|
| viés da `amp0p6_10Hz` | −0,0524 | **−0,0516** |

**Causa medida, e é estrutural:** `N_emb` = **50** ciclos e a curva roda
**5300** — **106× a constante de tempo**. A fração do alvo atingida é
`1 − e^{−n/N}` = **1,0000 com e sem o gate**. Gatear o incremento de um canal
**saturado** muda *quando* ele completa, não *quanto* — o efeito no fim da curva
é ~nulo **por construção**.

⚠️ **Isto é a lição do `graded_scrit` outra vez, no outro canal:** satura-se a
*taxa* e o *destino* não se move. E é também um alerta sobre gates: **F3 e F4
passaram sobre um no-op** porque eu pedi *direção* sem pedir *magnitude*.

## A correção, e por que ela é fisicamente a certa

O PR-3 escolheu o **incremento** para a amplitude **de propósito**:
*"sub-limiar o assentamento fica lento, não menor"*. Para amplitude isso é
correto — menos vibração adia o assentamento, não o reduz.

**Para frequência o argumento inverte.** Se o assentamento tem componente
dependente do **tempo**, então o mesmo número de ciclos a 10 Hz dispõe de
**metade do tempo** — e o que muda é **quanto consolida**, não só quando. O gate
pertence ao **alvo**:

```python
target = (mat.emb_depth * embedding_conformance_factor(...)
          * settling_amplitude_factor(...)
          * stage1_freq_gate(mat, freq)          # ← P-9 v2
          + mat.emb_load_frac * g_slip * ...)
```

## Medido (sonda, monkeypatch, nada escrito)

| curva | f | antes | depois | viés |
|---|---:|---|---|---|
| `amp0p6_5Hz` | 5 | 0,0857/0,5170/0,1534 | **idêntica** | +0,0339 → +0,0339 |
| `amp0p6_10Hz` | 10 | 0,0552/0,0886/0,0365 | **0,0310/0,0665/0,0351** | **−0,0524 → −0,0097** |
| `amp0p4_5Hz` | 5 | 0,0995/0,1423/0,0773 | **idêntica** | igual |
| `varamp` ×2 | 5 | — | **idênticas** | igual |

**As três pernas melhoram e o viés cai 81 %**, com os mesmos **zero números
fitados**.

## Gates v2 (congelados) — agora com MAGNITUDE

| # | gate | esperado |
|---|---|---|
| **G1** | default `s1_freq_exp=0` ⇒ bit-idêntico | Δ = 0,000000 |
| **G2** | as 4 curvas de **5 Hz** | **bit-idênticas** |
| **G3** | `amp0p6_10Hz`: viés anda para zero **em ≥50 %** | −0,0524 → ≤ −0,026 |
| **G4** | `amp0p6_10Hz`: melhora nas **3** pernas | MAE, res.máx e σ todos ≤ |
| **G5** | censo | **não cai** (139) |
| **G6** | suíte completa | verde |

⚠️ **G3 exige magnitude de propósito.** Foi a ausência dela que deixou a v1
passar sobre um no-op. *"Anda na direção certa"* não é resultado se anda 1,5 %.

⚠️ **O que isto NÃO resolve, e fica declarado:** a `amp0p6_10Hz` **continua fora
do tripé** — σ 0,0351 contra limite 0,0250 (**1,40×**, era 1,46×). A P-9 explica
o **viés**, não o σ. O censo não sobe; o que sobe é a fidelidade física.

## Rollback

`.bkp_p9` no engine. Qualquer gate divergente ⇒ restaura e registra.
