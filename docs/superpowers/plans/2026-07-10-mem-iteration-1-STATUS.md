# MEM Iteração 1 — Status (CONCLUÍDA)

**Data:** 2026-07-10 · **Plano:** `2026-07-10-mem-iteration-1.md` ·
**Spec:** `2026-07-10-model-evolution-methodology-design.md` · engine final
carimbado no store; ledger entrada #34.

## Resultado global

| Métrica (canônico, n=114) | ANTES | DEPOIS | Δ |
|---|---:|---:|---:|
| **Mediana MAE** | 0.1808 | **0.1376** | **−24%** |
| Média MAE | 0.2124 | 0.2020 | −5% |
| Casos > 0.2 | — | 41 | (n_above_bound no ledger) |

Meta da iteração era ≤ 0.10: **não atingida** — as regras de promoção só
permitiram parte do gap (o resto exige formas/harness, listado abaixo). A
meta permanece para as próximas iterações.

## Tooling entregue (Etapas 0-1 permanentes)

`validation/error_budget.py` (classificador auditável + JSON + CLI), seção
"Orçamento de erro (MEM)" + painel "Convergência (ledger)" no report mestre,
`docs/METHODOLOGY.md` (runbook, com a diretriz do professor: otimização
per-paper é legítima dentro da disciplina de DOF) + §18 na aba Documentation.

## Promoções (com classe de procedência — auditáveis no adopted_configs)

| Fonte/grupo | O quê | Classe | Efeito (mediana) |
|---|---|---|---|
| ROUSSEAU_2025 | c_bend 0.3 | fitado-this-rig (§4.12) | steel 0.16-0.35 → **0.037-0.075 (= campanha, FECHADO)** |
| BAUER_2024_fig6 / fig8_test1 / fig8 | flatten do bloco §4.33 (dano contínuo + c_bend + emb per-espectro) | fitado-this-rig (forma validada §4.33) | 0.21-0.30 → 0.16-0.24 (parcial) |
| LIU_2022_RETIGHT_dry | µ seco 0.2 | input do estudo §4.29 | marginal |
| LI_2022_MARSTRUC | C_creep 9.9e-13 | **âncora medida do par** (Fase 1C, §4.7) | 0.740 → 0.649 (residual = harness) |
| **KARLSEN_2022_vibralock** | tr_loose_gain 0 + wear off + emb lido (3.68 µm) + C_creep do par 1e-12 | input de paper (wedge-cam suprime rotação) + lido-do-dado (L24) + fitado-this-rig/par (prior âncora 304SS) | **0.706 → 0.0101** (diretriz do professor) |

## Testado e REVERTIDO (gate falhou — honestidade)

- **LIU_2025 joint-fit** (emb 8µm/ratchet 8e-5 do frontier): mediana da
  família não melhorou (amp0p4 piorou) — a config da galeria não é
  recuperável dos artefatos; alvo iter.2.
- **LIU_2022_RET_oil** (µ 0.1): piorou sozinho — a supressão por óleo é
  `c_D` per-lube (§4.11), não só µ; alvo iter.2.

## Bug real exposto e corrigido pela iteração

**Matching LI↔LIU**: o best-match fuzzy deixava `LI_2022_MARSTRUC` casar
`LIU_2022` (e, desde o Plano A, os casos de creep usavam a cfg do
`LIU_2017_axial` **por acidente** — números "bons" com física de outro par).
Corrigido com **fronteira estrita** (chave prefixo da fonte ou fonte prefixo
da chave; grupos por token no case_id). O baseline honesto do creep piorou ao
corrigir — e foi parcialmente recuperado com a âncora DO PAR.

## Alvos da iteração 2 (rotulados no orçamento)

1. **YANG_2021 (0.652)** — excitação composta (transversal+axial 90°): sem
   config adotada; física do protocolo não mapeada.
2. **LI_2022_MARSTRUC (0.649)** — runner genérico ≠ harness da âncora de
   creep estático (Fase 1C); usar anchor_creep como referência do caminho.
3. **YANG_2023_IJPEM (0.294)** — sem entrada adotada; nunca calibrado.
4. **LIU_2022 fig5 (0.249)** — §4.29 completo (running-in + c_D per-lube).
5. **UFU_LAB (0.249)** — c_bend per-rig nunca fitado (lever 3 direto).
6. **LIU_2025 (0.193)** — reconstruir a config da galeria com procedência.
7. **BAUER (0.165)** — forma graded do §4.33 (k_loose_graded?) não promovida.
8. **KARLSEN HV** — propagar C_creep=1e-12 do par com refit de c_bend.

## Guard-rails exercidos

Gate de medição por fonte em toda promoção (2 reverts); leitura-antes-de-fit
(emb L24 no vibralock); 1 constante fitada por grupo (C_creep no branch
travado, 4 curvas); paridade liu2025_amp0p25 preservada; pisos respeitados
(YANG_2019 e outros no_piso não foram tocados).
