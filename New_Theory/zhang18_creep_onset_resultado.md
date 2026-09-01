# ZHANG_2018 — creep com onset ADOTADO: a fonte inteira fecha o tripé (9/9)

**2026-07-30** · preregs `2026-07-30-zhang18-creep-onset{,-r2}-prereg.md` ·
execuções `zhang18_creep_onset_exec{,2}.{py,json}` · **adotado por delegação
(mandato 2026-07-30)** após R2 gates 4/4. Origem do candidato: o re-run do
D2′ com teto único nomeou a **deriva tardia** (σ das curvas longas mora na
cauda) e a sonda `deriva_tardia_probe.py` mediu que o ZHANG_2018 tinha taxa
tardia **identicamente nula** — a config adotada zerava o creep
(`C_creep=0.0`) enquanto o dado seguia caindo ~0,01 além de 200 k.

## O que foi adotado

| campo | antes | depois | procedência |
|---|--:|--:|---|
| `C_creep` | 0.0 | **1.355e-11** | mapa A→C linear (G1′, 2 sims, ±0,7 %) |
| `t_0` | 1.0 s (default) | **108.1 s** | onset lido do resíduo: N₀=1081 ciclos @ 10 Hz (L24) |

A forma não é nova: `δ_creep = C·F₀·ln(t/t₀+1)` já estava no engine com
`t_0` per-par. Com N₀ grande a lei é quasi-linear cedo e põe a perda na
cauda — o motivo provável de o creep ter sido **zerado** na adoção original
é que com `t_0=1 s` (front-loaded) ele estragava o começo; o remédio era o
onset, não o desligamento.

## Os números (sim real, store-comparável)

| curva | σ antes→depois | MAE | mx | tripé |
|---|---|--:|--:|:--:|
| fig2_test1 (1e3 cyc) | 0.0072→0.0078 | 0.0182 | 0.0274 | fecha |
| fig2_test2 (1e4) | 0.0121→0.0101 | 0.0200 | 0.0433 | fecha |
| fig2_test3 (1e5) | 0.0244→0.0150 | 0.0170 | 0.0445 | fecha |
| fig2_test4 (5e5) · fila | 0.0294→**0.0157** | 0.0142 | 0.0438 | **fecha** |
| fig13_14kN · fila | 0.0297→**0.0184** | 0.0131 | 0.0575 | **fecha** |
| fig13_20kN | 0.0242→0.0118 | 0.0094 | 0.0282 | fecha |
| fig13_26kN | 0.0186→0.0055 | 0.0075 | 0.0229 | fecha |
| fig16_with_locker | 0.0091→0.0064 | 0.0156 | 0.0271 | fecha |
| fig16_without · fila | 0.0263→**0.0142** | 0.0102 | 0.0419 | **fecha** |

**9/9 sob o tripé efetivo (lim σ 0,0250)** — antes eram 6/9 fora ou
near-miss, 3 na fila-26. Config ÚNICA para a fonte (a variante `per_case`
para o locker foi preterida por parcimônia — e não fez falta: o locker
melhora σ 0,0091→0,0064 com MAE +0,0075 dentro da tolerância).

## Por que a adoção é legítima (a trilha completa)

1. **R1 provou o mecanismo e a generalização** com held-out de 8 curvas
   (fit em UMA): superposição analítica exata (desvio máx 0,0005), σ held
   mediana 0,0242→0,0106, **zero pioras de σ**. R1 **reprovou no G4** (MAE
   de 3 curvas piorava >+0,01 com A=0,01261, N₀=562) — nada foi adotado.
2. **R2 = engenharia de adoção dentro da família validada** (declarado no
   prereg): acervo completo como restrição, generalização banked da R1.
   Varredura analítica → (A=0,00700, N₀=1081) viável e fecha 9/9.
3. **Execução R2: gates 4/4** — G1′ linearidade ±0,7 %; G2′ desvio máx
   0,0003 (0 fora de ±0,005); G4′ zero pioras >+0,01; G5′ fila 3/3.
   A previsão analítica acertou σ de 9 sims ao 4º decimal.

## Instrumento que fica

`deriva_tardia_premeasure.py` + o **teto por curva da família aditiva**
(`fila_teto_log_onset.json`): antes de gastar sim em canal lento, o teto
analítico diz se a família FECHA a curva. Na fila-26: 12 fecháveis em
família aditiva; 14 provadamente além dela (chu ×6, sun, caccese,
yang2021 ×2, liu2025 amp0p8, li2022ti full, liu2022 t1/t2) ⇒ exigem forma
multiplicativa/limiar. **LIU_2016 morreu no F1 do premeasure** (nenhum
(A,N₀) compartilhado mantém as irmãs) — a cauda dele precisa de outro canal
(fonte é estudo de WEAR com medição própria; ancorar lá).

## Efeito na fila — CONFIRMADO no restamp (triagem 2026-07-30 tarde)

Fila form-limited 26 → **23** (−3 zhang; ZHANG_2018 fora da lista por fonte)
· tripé estrito **127/202** · resolvida/declarada **164/202** · mediana de
redução de σ_res necessária da fila 13 % → **11 %**. ZHANG_2018 sai também
das near-misses (test3 0,0244 e fig13_20kN 0,0242 estavam a <4 % do limite;
fecharam com folga: 0,0150/0,0118).
