# `crash_trigger_frac` contra a aceleração tardia — FALSIFICADO por construção

**2026-08-01** · prereg `2026-08-01-crash-trigger-classe`. A classe estava
provada (7 fontes), a forma existia no engine e nunca fora adotada — era o
candidato mais promissor do dia. **Morreu no G0, e o motivo é estrutural.**

## G0 — direção errada nas 5 fontes testadas

Uma curva por fonte, `crash_trigger_frac` ∈ {0,80; 0,60}:

| fonte | curva | fim base | cf=0,80 | cf=0,60 | dado |
|---|---|---:|---:|---:|---:|
| YANG_2019 | amp0p4_5Hz | 0,843 | 0,848 | 0,850 | 0,727 |
| CHU_2026 | D0p4_49kN_test2 | 0,606 | 0,607 | 0,610 | 0,142 |
| LIU_2025 | amp0p3 | 0,847 | 0,847 | 0,847 | 0,900 |
| JCSR_2023 | plain_outdoor | 0,601 | 0,601 | 0,601 | 0,729 |
| SUN | transverse_grease | 0,048 | 0,052 | 0,059 | 0,111 |

O fim **sobe** (menos perda) onde o dado pede **descer**. Em 4 das 5 o
efeito é ínfimo; na única que move de verdade (SUN) o MAE **piora**
(0,0999 → 0,1435 em cf=0,60).

## Por que — e é uma verdade sobre a forma, não sobre o fit

O gate é, no engine (`dynamic_stiffness_analyzer.py` ~L1959):

```
g_trigger = ft / (ft + ratio**k)      # ft = crash_trigger_frac**k
```

⇒ **g_trigger ∈ (0, 1] SEMPRE**. Ele multiplica a taxa **para baixo**:
produz um joelho **atrasando** a perda enquanto F₀ está alto, e no melhor
caso devolve a taxa **base** depois do limiar. **Nunca acelera além da
taxa base.**

O déficit desta classe é o oposto: a taxa tardia do modelo é **15× a 225×
lenta demais** (medido em 7 fontes). Nenhum valor de `crash_trigger_frac`
pode produzir isso — não é questão de calibrar, é o contradomínio do
gate.

## O que isso deixa registrado (e economiza)

1. **A classe continua válida** (`aceleracao_tardia_classe.md`, 7 fontes,
   3 instrumentos independentes). O que caiu foi o candidato, não o
   diagnóstico.
2. **O requisito de uma forma que sirva ficou preciso**: precisa de
   **amplificação tardia** (fator > 1 sobre a taxa) governada por estado
   acumulado — não de supressão inicial. Isso descarta, sem testar, toda
   a família de gates Hill do engine, que são todos ≤ 1 por construção
   (`slip_onset_gate`, `conformation_gate`, `g_slip_regime`,
   `self_locking_gate`, `crash_trigger`).
3. **Candidato remanescente com essa propriedade**: o `surface_damage`
   D, que **amplifica** wear (`d_wear ·= 1 + k_dmg_wear·D`) e cresce com
   a dissipação acumulada — é o único mecanismo do engine cujo fator
   passa de 1. Já é usado per-rig em algumas fontes (LIU_2022 c_D=0,5).
   Testá-lo contra a classe é o próximo passo natural — **com o aviso**:
   é a mesma máquina que o CHU já falsificou como dose única
   (`chu_veredicto_completo.md`), então o prereg tem de perguntar se ela
   serve à CLASSE, não à curva.

## Estado

Nada adotado; censo **129/205** e fingerprint `a410d6537c83` intactos.
Suíte 873/1 (o único vermelho foi corrida com a regeneração de páginas —
re-executado isolado: passa).
