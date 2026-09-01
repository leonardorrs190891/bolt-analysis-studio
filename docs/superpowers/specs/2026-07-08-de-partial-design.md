# dE_partial — canal de energia de partial-slip (design, 2026-07-08)

**Origem:** dupla falsificação convergente — §4.25 (loops Rousseau, energia 7-8x baixa =
partial-slip nao dissipado) + §4.31 (joelho Bauer fig8: dano nao dispara no plato porque
W_slip_acc so acumula gross slip). Ambas nomeiam a MESMA forma.

## Física
No contato Cattaneo-Mindlin abaixo do gross slip (r=Q/(muF0k)<1) existe um ANEL de
micro-slip que dissipa energia por ciclo (fretting), mesmo sem escorregamento macroscopico.
O modelo hoje: `partial_slip_gate` computa a FRACAO de energia CM g=1-(1-min(r,1))^m, mas
`W_slip_acc` (driver do onset do dano) e o budget de energia so contam GROSS slip => no
plato (partial slip puro) W_slip_acc=0 e os loops ficam 7-8x baixos.

## Forma
    dE_partial = k_partial_slip * g_partial(r) * 4 * mu_eff * F0 * delta_t
- g_partial: fracao CM (partial_slip_gate, channel="wear") — <1 no plato, 1 em gross.
- delta_t = F_slip_transverse/k_tr = amplitude de micro-slip do anel travado.
- Alimenta: (a) state.W_slip_acc => damage_onset_gate dispara no plato => D cresce => joelho;
  (b) energy.W_diss_wear (budget §4.25); (c) energy.W_ext (conservacao, sourced externamente).
- NAO drena preload direto (energia-only; o efeito de preload emerge via D->wear amplificado).
- k_partial_slip=0 => 0.0 exato (bit-identical).

## Gates
- G1 default-inert: W_slip_acc e F_0 bit-identicos com k_partial_slip=0.
- G2 plato: em regime partial (r<1, gross=0), W_slip_acc CRESCE (era 0) com k>0.
- G3 conservacao: residual inalterado (W_ext sourca dE_partial).
- G4 Bauer: com dano ativo, dE_partial dispara D no plato => joelho fig8 (interp melhora
  SEM piorar a mediana por-pontos, ao contrario do gate unico §4.30).
