# MEM Iteração 2 — Status (CONCLUÍDA)

**Data:** 2026-07-11 · ledger #35 · runbook: `docs/METHODOLOGY.md`

## Resultado

| Métrica (canônico, n=114) | Baseline | Iter. 1 | **Iter. 2** |
|---|---:|---:|---:|
| Mediana MAE | 0.1808 | 0.1376 | **0.1392** |
| Média MAE | 0.2124 | 0.2020 | **0.2005** |

Δ(média) da iteração = 0.0015 < 0.002 — **primeiro tique do critério de
parada (b)**. Leitura: a fase de promoção barata está esgotada; o resíduo
dominante agora exige trabalho ESTRUTURAL (formas/harness), não giro de
constante. Mais uma iteração ≤ 0.002 e o critério formal dispara.

## Gates da iteração (6 alvos atacados, 1 promovido)

| Alvo | Alavanca testada | Gate | Resultado/Aprendizado |
|---|---|---|---|
| **YANG_2023 (0.294)** | c_bend 1-D (9 curvas, 1º DOF da fonte) | **PASSOU** | c_bend 0.3 promovido → **0.228** |
| âncora interna (0.249) | c_bend 1-D | falhou | insensível — resíduo = mapear estados do Estágio A (D_init/emb_consumed) no runner |
| marstruc (0.649) | grip 20 mm (paper, âncora 1C) | falhou (piorou 0.85) | confirma mismatch ESTRUTURAL do caminho de creep — reproduzir o harness estático da âncora no runner |
| Yang2021 (0.65) | F_amp axial real do protocolo | falhou (inerte) | disp-mode não vê F_amp — protocolo composto (transversal+axial 90°) é **FORMA** p/ o funil de falsificação |
| fig5 (0.24) | grupo limpo (sem extras de retight) + c_D per-lube adotado | falhou (inerte/piora) | config §4.29 **não reconstruível** dos artefatos adotados — re-derivar na campanha |
| Karlsen HV (0.094) | C_creep do par + refit c_bend | falhou (0.127 no melhor) | **achado físico**: o C_creep da âncora interna inflado absorvia outro mecanismo; o paper aponta dano de asperezas ("not creep") → **candidato pré-registrado de falsificação** (colapso virgem dirigido por D) |

## Guard-rails exercidos

Nenhuma promoção sem gate; 5 reverts/não-promoções documentados com causa;
1 DOF por fonte respeitado; leitura-antes-de-fit mantida; pisos intactos.

## Fila da iteração 3 (estrutural, em ordem)

1. **Falsificação pré-registrada: colapso HV dirigido por dano** (gate a
   escrever ANTES: com D-driven asperity loss e C_creep físico do par, o
   modelo deve reproduzir o colapso HV E manter o branch travado em ~0.01).
2. **Caminho de creep estático no runner** (referência: `anchor_creep.py`) —
   resolve marstruc (0.649) e consistência §4.7.
3. **Forma do protocolo composto** (Yang2021) — excitação transversal+axial
   com fase; possivelmente reusa FatigueLoss p/ a cauda de fratura.
4. Estados Stage-A no runner (âncora interna); re-derivação §4.29 (fig5); forma graded
   §4.33 (Bauer); config Liu2025.
