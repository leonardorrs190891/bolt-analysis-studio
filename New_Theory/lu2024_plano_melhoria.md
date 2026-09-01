# LU_2024 (Sensors) — plano de melhoria das 10 curvas, ancorado na LEITURA DO PAPER

**2026-07-31** · pedido do professor: *"leia o paper, vamos traçar um plano"*.
PDF lido (25 pp., `pdfs_open_access/lu2024_sensors_M8.pdf`); estado: 0/10 no
tripé, MAE médio 0,089; 7 declaradas (colapso), config adotada
`{N_emb=3, delta_free=0.28mm, k_ratchet=0.02, loose_arrest_floor=0.21,
c_bend=12, emb_um=0}`.

## Os TRÊS achados da leitura (dois mudam o que já está no repo)

### A1 — ⚠️ A fig20 rodou a 1,0 mm, NÃO 0,5 mm (registry ERRADO)

Prova dupla: (i) p.19, prosa: *"After 100 cycles of tangential **1 mm**
displacement, the remaining pre-loading is 78 / 1845 / 1568 / 742 / 3523 N"*;
(ii) a linha 22 N·m da Tabela 9 é **idêntica dígito a dígito** à linha 1,0 mm
da Tabela 8 (36,8 / 57,1 / 87,9 / 93,6 %) — a curva T22 da fig20 É a curva
1,0 mm da fig18 (mesmo teste). O registry
(`core/validation_cases.py`) declara `0.5` para as cinco fig20 ⇒ **as 5
curvas simulam com metade do drive real**. Com `delta_free=0,28 mm` adotado,
o excesso de curso real é (1,0−0,28)=0,72 mm, não 0,22 — fator ~3,3 no
excesso. Toda a calibração per-source foi feita sobre esse input errado.

### A2 — ⚠️ RETRATAÇÃO: o "piso do LU" de hoje cedo é INVÁLIDO

O par que casei de manhã (`fig18_amp0p5 ↔ fig20_T22Nm`) cruzava **0,5 mm
contra 1,0 mm** — mediu diferença de amplitude, não repetibilidade (σ 0,0909
era isso). Consequências a desfazer: (i) a exceção F7 da `fig20_T22Nm` foi
assinada sobre piso errado → **retirar**; (ii) o piso por fonte do LU sai da
tabela até ser re-medido com par válido. O par VERDADEIRO (`amp1p0 ↔ T22`,
mesmo teste) mede **MAE 0,0131 · σ 0,0210 · mx 0,1043** — mas sendo o mesmo
teste replotado, isso é piso de **digitalização**, não de repetibilidade
(o mx alto é a frente quase-vertical: Δx minúsculo ⇒ Δy grande).
A harmonização de F0 11567 muda de alvo: quem tem de casar com a T22 é a
**amp1p0** (prova: mesmo teste ⇒ mesmo F0, e a Tabela 9 dá 11567); a
`amp0p5` volta a 12000 (base original da nota; a premissa da manhã caiu).

### A3 — o paper dá o que faltava: RÉPLICAS REAIS e ÂNCORAS de rigidez/atrito

* **§3.1.3 (p.14): TRÊS corridas a 22 N·m / 1,0 mm** com F0 = 12398 / 12285 /
  12696 N (Fig. 14) — réplicas verdadeiras, digitalizáveis ⇒ piso de
  REPETIBILIDADE real. E corridas de **0,25 mm até 1000 ciclos** e **0,5 mm
  até 500 ciclos** (janelas 5–10× mais longas que as da fig18).
* **Fig. 21: rigidez tangencial inicial MEDIDA por torque** — 5,04 / 8,55 /
  9,21 / 9,84 / 11,52 ×10⁴ N/mm para 4/10/16/22/28 N·m ⇒ âncora direta de
  `k_tr`/`c_bend` por F0 (hoje c_bend=12 é fitado).
* **Fig. 19: força máxima por ciclo a 1,0 mm** — 4697 → 3022 → 1546 → 1030 N
  (ciclos 1/15/50/100) ⇒ âncora da EVOLUÇÃO do atrito/resistência (µ_eff·F0
  por ciclo, queda de 78 %).
* **Mecanismo dos autores (p.20)**: estágio 1 (ciclos 1–5/10) = **escoamento
  PLÁSTICO local** da chapa de aço-níquel mole (extrusão do furo + pressão
  sob a cabeça) — 36–50 % de perda no 1º ciclo; estágio 2 = afrouxamento
  rotacional por deslizamento acumulado. Furo ⌀10 vs parafuso ⌀8 (folga
  diametral 2 mm) — o `delta_free=0,28 mm` adotado tem física por trás, e o
  paper permite lê-lo por condição.
* **Tabelas 8/9**: checkpoints exatos de F/F0 em N=1/10/50/100 para as 10
  condições — régua de conferência da digitalização.
* **T4Nm**: o próprio paper diz que 4 N·m *"does not reach the tightening
  effect"* (F0=2105 N) — candidata a exclusão/declaração por condição fora
  do escopo de junta apertada, com as palavras dos autores como procedência.

## O plano (sequência, custo, gate)

| # | ação | custo | gate/saída |
|---|---|---|---|
| **P0** | **Corrigir input fig20: 0,5→1,0 mm** (5 curvas) + F0 da amp1p0→11567 (mesmo teste da T22) + reverter amp0p5→12000 | edit + 6 sims (~100 ciclos cada) | prova dupla no doc; re-sim; censo antes/depois; ZERO fit novo |
| **P1** | **Retratação**: retirar exceção T22 (piso inválido); piso LU re-medido do par verdadeiro com rótulo honesto "digitalização, mesmo teste" | edits + censo | invariantes de exceção verdes; docs _VIVAS re-sync |
| **P2** | **Decisão (professor): dedup** — amp1p0 ≡ T22 (mesmo teste em 2 figuras): manter as duas no censo é contar a mesma medição 2× | decisão | se dedup: 202→201 comparáveis (mexe em TODA a contagem publicada) |
| **P3** | **Re-diagnóstico pós-P0**: com o drive certo, re-ler a fonte (a config atual foi calibrada no input errado). Sondar se `{k_ratchet, delta_free, floor}` re-lidos COM as âncoras novas (Fig. 21 k_tr; Fig. 19 µ_eff(N)) fecham fig18+fig20 | grade ~30-50 sims curtas | premeasure→prereg→gates (playbook zhang/liu2016) |
| **P4** | **Digitalizar Fig. 14** (3 réplicas 1,0 mm + 0,25/0,5 mm janelas longas) | subagente PyMuPDF + digitização (~1 h) | piso de repetibilidade REAL + 3–5 curvas novas de validação |
| **P5** | **Decisão (professor): T4Nm** fora de escopo ("não atinge efeito de aperto", palavras do paper) | decisão | declarada por proveniência, como a zhang2006_fig3 |
| **P6** | Estágio-1 plástico: se após P0/P3 o 1º ciclo ainda escapar (36–50 % de perda), a física é plasticidade de furo em chapa mole — fronteira de forma (PR-3), com a Fig. 21 (rigidez degradando) como âncora do candidato | prereg futuro | só com sua autorização |

> ## ESTADO DA EXECUÇÃO (2026-07-31, noite)
>
> **P0+P1 ✅** (input fig20=1,0 mm + retratações) · **P5 ✅** (T4 declarada,
> autorização do professor) · **P2 ✅** (dedup amp1p0≡T22, denominador 201) ·
> **P3 EXECUTADO EM 4 RODADAS PRÉ-REGISTRADAS — NAO PASSA, FIM (sem R5)**:
> gates finais G1✓ G2✓ G5✓ (2 leituras fecham; mediana −18 %), reprova em
> G3-mae/G4 com a fronteira PROVADA — nos 17 pontos c1-viáveis de 162 o
> T10Nm fica ≥0,20 em todos ⇒ a fig20 de torque médio/baixo sob o drive
> real está além das formas atuais (é a plasticidade de furo F₀-dependente
> da p.20 — P6). Saldo sem adoção: c_bend=30 lido da Fig. 21; 4 defeitos de
> instrumento documentados; held-out generalizando 4/4. **Próximos: P4
> (Fig. 14) e P6 (PR-3).** Preregs/execs: `2026-07-31-lu2024-p3{,-r2,-r3,
> -r4}-prereg.md` + `lu2024_p3{,_r2,_r3,_r4}_exec.*`.

**Ordem recomendada: P0+P1 imediatos** (input-verdade + honestidade do piso;
sem eles qualquer fit é sobre dado errado), **P3 em seguida** (a fonte pode
melhorar muito só com o drive certo + âncoras), P4 quando houver janela de
digitização, P2/P5 são suas decisões, P6 por último.

## Riscos e honestidades

* O P0 vai **piorar** algumas métricas fig20 antes de melhorar (o modelo
  atual foi ajustado ao drive errado) — é o custo de medir contra a verdade;
  publicar antes/depois.
* As 7 declaradas (colapso quase-vertical) continuam metric-limited mesmo
  com tudo certo — o colapso de 1º ciclo é abrupto DE VERDADE; o alvo
  realista do tripé nesta fonte são as curvas lentas (amp0p25, T10–T28 pós
  P0/P3) + exceções por piso real (pós P4).
* O piso de digitalização (σ 0,021) NÃO substitui repetibilidade — só a
  Fig. 14 dá o número honesto.
