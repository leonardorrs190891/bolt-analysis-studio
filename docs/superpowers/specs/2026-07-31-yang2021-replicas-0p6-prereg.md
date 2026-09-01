# Prereg — réplicas 0,6 mm–8 kN do YANG_2021 (Fig. 6b2/6b3)

**2026-07-31** · executor do plano `plano_tripe_restante.md` (Bloco 6,
autorizado: "concordo"). Gates escritos ANTES de qualquer medição.
**Objetivo**: digitalizar as 2 réplicas não-digitalizadas da condição
0,6 mm–8 kN (r2/r3; r1 = `yang2021_amp0p6mm_ax8kN_r1` já no censo) e
medir o **primeiro piso de réplica de BANCADA real** da fonte — o piso
atual (σ 0,0143) vem do par fig2↔amp0p8, cuja independência é incerta
(Fig. 2 é "typical curve" sem condição declarada; vidas 5.850 vs 5.450).

## Estado congelado (fingerprint `3d432a65c7e8`, censo 201)

| curva | mae | mx | σ | estatuto |
|---|---|---|---|---|
| amp0p6_r1 | 0,0266 | 0,0415 | 0,0223 | TRIPÉ |
| amp0p5_ax8kN | 0,0549 | 0,0945 | 0,0458 | fila (viola mae 1,1× · σ 1,8×) |
| amp1p0_ax2kN | 0,0580 | 0,0919 | 0,0476 | fila (viola mae 1,2× · σ 1,9×) |
| fig2_typical / amp0p8 | — | — | — | exceção F5 (ξ-confundido) |

Piso da fonte HOJE: MAE 0,0146 · mx 0,0732 · σ 0,0155 (1 família);
`limite_sres` = 0,025. Âncora de prosa: Tabela 3 dá **N(0,6–8) = 14.666**
ciclos; nota de aparato dá vida r1 ≈ 12.500.

## Gates (imutáveis)

- **G1 — integridade da digitalização**: (a) round-trip: média das 3
  vidas (r1 do CSV + r2/r3 novas) dentro de **14.666 ± 8 %**; (b) cada
  curva com ≥ 30 pts e F/F₀ inicial em [0,95; 1,15] (overshoot documentado
  até ~15,5 kN/14,1); (c) overlay de debug por painel salvo e conferido;
  (d) normalização por F0 nominal 14,1 kN (convenção da fonte).
- **G2 — piso**: interpolação pairwise na janela comum (método
  `_pisos_medidos` v2); reportar (MAE, mx, σ) dos 3 pares r1↔r2, r1↔r3,
  r2↔r3 + piso da família = **mediana por métrica**.
- **G3 — ramos declarados antes de medir**:
  - r2/r3 entram como CASOS do censo (precedente Fig. 14a do LU): censo
    201→203, simulados sob o config adotado vigente da fonte (zero fit).
  - Perna σ de TODA curva YANG_2021 re-julgada por D1 (`limite_sres` =
    max(0,025; piso mediano da fonte)) — mecânico, sem assinatura.
  - F7 por condição PRÓPRIA: r2/r3 podem assinar PROVA/FORTE contra o
    piso da família 0,6–8 se TODAS as pernas violadas forem cobertas
    (regra endurecida 2026-07-31). **Cross-condição (0,5–8 e 1,0–2 vs
    piso 0,6–8) NÃO assina nesta execução** — só reporta distância
    (lição LU: amp0p25 ficaram fora de propósito).
  - Ramo INCONCLUSIVO: G1 falha ⇒ nada entra, nada se assina.
- **G4 — sincronia**: casos novos ⇒ pins de contagem, `_VIVAS`, docs
  vivos e páginas re-sincronizados NO MESMO commit; batch com re-stamp
  uniforme + `exemplo_m12_sintetico` direto.

## Previsão registrada (falsificável)

Vidas r2 ≈ 14–15 k, r3 ≈ 16–17 k (leitura visual dos painéis) ⇒ spread
de vida ~30 % ⇒ piso-σ da família plausivelmente ≥ 0,04. Se der < 0,025,
a fonte é mais repetível que o modelo erra, e a fila fica como está.
