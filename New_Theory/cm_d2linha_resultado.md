# D2′ re-executado com teto único — **o mérito do Cattaneo-Mindlin era 100 % artefato de teto**

**Executado em 2026-07-30** (pendência do handoff: *"re-rode o D2′ com o teto
corrigido"*). Sonda: `New_Theory/cm_discriminante_d2linha.py` · resultado bruto:
`cm_discriminante_d2linha.json` (meta: `teto_unico=true`, régua D1).
**Nada adotado** (driver `cm_adocao_driver.py`, política declarada antes).

## O resultado, em uma linha

Com o **mesmo teto nas duas pontas** (baseline re-simulado a 200 k, não lido do
store), o ganho do CM é **+0,0000 nas 18 curvas** — `sd0@cap == sd_CM` ao
dígito. As "7 que fechavam" fecham **no baseline também**: era o truncamento
cortando a cauda (onde o σ cresce), não o mecanismo. As 7 confirmações
full-length dão **fecha_full=False em todas**, retornando exatamente aos valores
do store (0,0365 · 0,0328 · 0,0281…) — a consistência interna fecha o caso.

| gate | resultado |
|---|---|
| **A** atribuição | ok — 0 curvas movem com gates em g≡1 (nada se move) |
| **B** gate congelado | **INCONCLUSIVO** — nenhuma curva se moveu o suficiente |
| **C** ordenação | **INCONCLUSIVO** — nan em 50 % da fila (guarda do prereg) |
| G1 store-comparável | **0** curvas fecham |

**Ramo do prereg: INCONCLUSIVO.** Pela letra do §6/§7: *não conta como
falsificação* para o requisito (b) da regra de parada — o instrumento mostrou
que **não há efeito a discriminar** nesta parametrização, o que mata o MÉRITO
(nada a adotar) sem julgar o MECANISMO.

## A contaminação, agora quantificada

`|σ_store − σ@200k|` nas 10 truncadas: máx **0,0127** (`li2022ti_axial_full`
0,0365→0,0238; `liu2016 fig7_run2` 0,0328→0,0206). Era o "ganho" inteiro da
1ª execução.

## Os dois subprodutos que valem mais que o veredicto

1. **O σ_res das curvas longas é dependente do comprimento** — e para o cluster
   `liu2016 ×4 · zhang18 ×3 · li2022ti` o excesso mora **inteiro na cauda além
   de 200 k** (todas passam a 3ª perna no teto e falham no full). O defeito
   dessas 7–9 curvas da fila é **deriva tardia** (estágio III), não
   assentamento. Alvo de forma: lei de taxa de longa duração (creep log /
   wear steady), não gates de slip.
2. **Instrumentação:** em 6 das 18 os dois sítios do CM **nunca operam**
   (force-mode ⇒ `slip_amp=None`; canal de wear não avaliado) — qualquer
   candidato futuro nesses casos precisa de sítio que exista no modo da curva.

## Efeito na regra de parada (§7 do prereg, aplicado)

Classe "taxa dependente do estado acumulado": incubação **FALSIFICADA** ·
kernel desacelerante **FALSIFICADO** (mantido — as pioras eram em curvas
curtas, sem truncamento) · CM **INCONCLUSIVO (não conta)** · `graded_scrit`
**componente vivo** · bifurcação de limiar **nunca sondada**.
⇒ requisito (b) **não** satisfeito; a parada **não dispara**; o pipeline segue
com dois membros por medir e um alvo novo (deriva tardia) que **não** é desta
classe.
