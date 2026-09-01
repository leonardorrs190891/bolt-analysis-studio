# YANG_2019 `amp0p4_5Hz` — a única curva da fonte em outro REGIME, e é exatamente a que fica aberta

**2026-08-16 (00:3x)** · store `20be19aabe11` · só-leitura · **nada adotado**.
Complementa o dossiê de falsificações
`docs/superpowers/specs/2026-08-10-yang2019-tripe-prereg.md` (T1–T13) com a
**barra da 2ª linha da fila** — regime · canais · forma · dado · rota — medida
aqui em vez de citada.

## A medição

| curva | estatuto | MAE | σ_res | σ/ruído | stick % | `slip/δ` | terços (ini/meio/fim) | canais dominantes |
|---|---|---:|---:|---:|---:|---:|---|---|
| **`amp0p4_5Hz`** | **ABERTA** | 0,0966 | 0,0761 | **8,7** | **7 %** | **0,18** | **−0,093 / −0,131 / −0,007** | **embedding 57 % + creep 40 %** (rotacional 2 %) |
| `amp0p6_10Hz` | tripé | 0,0235 | 0,0210 | 3,9 | 0 % | 0,52 | −0,017/−0,034/+0,001 | rotacional 31 % + wear 26 % + creep 23 % |
| `amp0p6_5Hz` | tripé | 0,0158 | 0,0190 | 2,3 | 0 % | 0,68 | −0,012/−0,022/+0,012 | rotacional 30 % + embedding 29 % + wear 24 % |
| `varamp_large_to_small` | tripé | 0,0190 | 0,0217 | 2,9 | 0 % | 0,93 | −0,001/+0,034/+0,021 | wear 43 % + embedding 30 % |
| `varamp_small_to_large` | tripé | 0,0282 | 0,0154 | 5,8 | 0 % | 0,73 | −0,027/−0,039/−0,015 | wear 36 % + embedding 35 % |

## O que ela diz

1. **REGIME:** a `amp0p4` é a **única** da fonte em quase-stick — `slip/δ` =
   **0,18** contra 0,52 · 0,68 · 0,73 · 0,93 das quatro irmãs, todas no tripé.
2. **CANAIS:** e é a única cujos canais dominantes são os de **stick**
   (embedding 57 % + creep 40 %, rotacional 2 %); as irmãs vivem de
   **rotacional + wear** (55–70 %).
3. **FORMA:** o modelo perde **demais** nos dois primeiros terços
   (−0,093 / −0,131) e reencontra o dado no fim (−0,007).
4. **DADO:** limpo — σ_res é **8,7×** o ruído da própria curva.
5. **ROTA:** já descartada por **6 falsificações pré-registradas** (T1–T13):
   `s1_amp_gate` na perna errada · `graded_scrit` quebra o grupo ·
   `slip_onset_W` inerte em stick · cascata de µ destrói as 0,6 · PR-21
   completo 0/5 · **`gth` limitado POR CONSTRUÇÃO** (o corte de stick o prende
   ao limiar de slip).

## Por que isto importa além desta curva

É o **mesmo padrão** das quatro fontes já na 2ª linha: as constantes da fonte
foram fitadas onde os **canais de slip** dominam, e a única curva em que os
**canais de stick** dominam não segue. Não é "a curva é difícil" — é que a lei
de taxa dos canais de stick não tem a dependência que a separa das irmãs.

⚠️ E **não** é uma lei da campanha: a hipótese de que stick sub-produz e slip
super-produz foi testada nas 205 e **falsificada** (correlação +0,05 —
`yang2023_e_a_lei_do_sinal_resultado.md`). Cada fonte precisa do seu próprio
discriminante; este é o desta.

## Reprodutibilidade

Instrumentação de `resolve_transverse_slip` nas 5 curvas + decomposição do
`simulate_case` + ruído por segunda diferença do dado. Sanidade: os valores de
MAE/σ conferem com o store ao dígito.
