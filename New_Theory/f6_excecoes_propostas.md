# Lista de exceções F6 — PROPOSTA (aguarda assinatura; sucessora da F5 assinada em 2026-07-28)

> **Status: ☐ NÃO ASSINADA.** Reúne os candidatos gerados DEPOIS do S4 (mesma
> noite, 2026-07-28) pelos fechamentos Chu/Lu/Karlsen/Yang e pela varredura das
> 3 classes. Doutrina herdada da F5: **exceção retira da meta, não fecha curva**;
> form-limited genérico fica na FILA (§E da F5), não vira exceção — só entra
> aqui o que tem **prova além do genérico**. Baseline: store `294808504d83`
> (re-stamp do piso do chu test1 em curso quando isto foi escrito).

---

## ① Classe §C (forma faltante com o esgotamento in-engine PROVADO) — CHU_2026 ×6

`test2 · test3 · test4 · test7 · test8 · test9` (test1 fecha com o piso lido,
prereg `cb86970`; test5/6 já passam).

**A prova, em três degraus (§4.54/§4.54a do MODEL_LEGITIMACY; é a mais forte da
biblioteca para uma família form-limited):**
1. µ-livre (estado atual): 6 violadoras.
2. **µ(t) MEDIDO pelo paper (Fig. 5, digitalizada) e PRESCRITO** no engine
   (`mu_bearing_schedule`, F3.2-CHU): quase inerte (|Δ|~0,01) — fato de engine:
   wear disp-mode é Archard, sem µ; o canal de 93 % do Chu é cego ao µ medido.
3. **Lei recolorida** (wear energético `k_E·µ_medido·p·slip`): morre **inclusive
   na âncora** (test4 0,118/0,249 no melhor k_E; cegas 0/3).

O candidato restante é o torque acumulado do próprio paper (`M⁻∝N^1,65`,
acumulação explícita no relógio) — ≥3 constantes per-rig sobre 4 curvas =
não-adotável sob parcimônia (G-A3). Reabre se outra fonte exibir a mesma
aceleração N-explícita.

**Decisão pedida:** ☐ exceção como família (6) ☐ manter na fila de formas

## ② Classe §B (trim-com-prova) — YANG_2019 ×2 terminais

`yang2019_M10_amp0p6_5Hz` e `yang2019_M10_varamp_small_to_large` — reclassificadas
METRIC-LIMITED terminais pela varredura das 3 classes (L25): **±3 % de N vale
0,21/0,26 em r no pico** — mesma classe metrológica dos trims do Liu (§4.44–4.48a:
nenhuma métrica automática distingue forma no colapso quase-vertical; o trim por
julgamento humano documentado é a saída honesta).

**Se ratificado:** aplicar `trim_n_max` por julgamento (janela até o início do
colapso terminal), com o ciclo completo de adoção (config → gates PR-37′ →
re-stamp uniforme) ANTES de contar qualquer efeito na meta. Nota de desenho: a
`small_to_large` trimada destrava o par de ordens opostas como banco de teste do
carry-over de história (diagnóstico Karlsen/Yang2019 §2b).

**Decisão pedida:** ☐ ratificar os 2 trims (com gates) ☐ deixar como estão

## ③ Data-limited POR NOME — YANG_2023_IJPEM 0,50 mm

`10_Yang_2023_phenomenological_model__0_50_mm__9` — **5 pontos** de métrica, salto
mediano do próprio dado 0,22 (2× a tolerância); prova formal em
`data_limited_proof_2026-07-28.md` §2. Com a correção de input F₀ 8,5→11 kN
(companion OA, aplicada em 2026-07-28) a curva piora para ~0,24/0,41 — reforça
que o dado, nessa resolução, não resolve o relógio de nenhum modelo.
(Os outros 2 data-limited da varredura — bauer fig6_rep1, fig8_test1 — **já estão
cobertos** pelas exceções §A da F5.)

**Decisão pedida:** ☐ exceção data-limited ☐ pedir/redigitalizar dado mais fino

## ③b Classe §A/§C (scatter de espécime no joelho, com prova par-a-par) — ROUSSEAU HDPE ×2

`rousseau2025_hdpe_t10` (0,058/0,153) e `rousseau2025_hdpe_t12` (0,064/0,138) —
trilha B do prereg Rousseau, executada 2026-07-28 (`rousseau_execucao_2026-07-28.md`).
**A prova é mais forte que um FAIL2:** a alavanca que fecha o t10 (gate CM 0,5 →
0,042/0,089, tripé) **quebra o t12 na direção oposta** (0,138→0,151, resíduo vira
para −0,151), com amplitudes de ensaio quase idênticas (Tabela 2: 0,50/0,49 mm).
Todas as alavancas sondadas (N_emb, emb, CM) puxam os dois em sentidos opostos —
scatter de espécime no tempo de joelho, irredutível a forma única (H-B3 do
prereg, cujo próprio ramo de parada previa esta exceção). Finais dos dois
ACERTAM (−0,013/−0,020) — o modelo captura o nível; o joelho é do espécime.

**Decisão pedida:** ☐ exceção por espécime (2) ☐ deixar na fila

## ④ O que fica FORA desta lista (fila aberta, sem mudança de estatuto)

- **LU_2024 ×10** — form-limited com descrição afinada (front-load heterogêneo
  por condição; 3 linhas mortas em contas, `lu2024_frontload_resultado.md`).
- **Karlsen run14p2** e **Sun grease-standard** — form-limited n=1, dormem até
  segunda fonte com a mesma assinatura.
- **Yang2023 IJPEM ×6 restantes + Yang2019 amp0p4** — candidato consolidado
  "resposta graduada de limiar" (2 rigs, 1+7 curvas — agora com teste cross-rig
  possível; `karlsen_yang2019_diagnostico.md` §2a).

## ⑤ Leitura da meta SE tudo for aceito como recomendado

146/202 no tripé (147 com o chu test1 do prereg `cb86970` se o GT3 passar)
+ 17 exceções F5 + **6 Chu** + **1 Yang2023-0p50** = 24 exceções; os 2 trims
Yang2019, se ratificados E gateados, movem-se de form-limited para trimadas
(podem ENTRAR no tripé — contagem só após re-stamp). Form-limited na fila:
39 − 6 (Chu) − 1 (0p50) − 2 (trims) ≈ **30**.

## ⑥ Bloco de assinatura (preencher na ratificação)

| § | item | curvas | decisão |
|---|---|--:|---|
| C | CHU_2026 família (prova em nível de lei) | 6 | ☐ |
| B | trims-com-prova YANG_2019 terminais | 2 | ☐ |
| D | YANG_2023_IJPEM 0,50 mm data-limited | 1 | ☐ |
| A/C | ROUSSEAU HDPE joelho por espécime (prova par-a-par) | 2 | ☐ |
