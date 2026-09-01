# Prereg — recuperação ROUSSEAU pós-erratum (Fig. 10 held-out)

**2026-08-01** · sequência do erratum (`rousseau_erratum_resultado.md`).
Gates antes de medir.

## Fases

1. **Digitalizar** Fig. 10 (aço, varredura 0,03/0,05/0,10 mm) e Fig. 6
   (HDPE×aço a 0,2 mm) — ferramental da Fig. 14/6b provado; G1:
   round-trip contra prosa/eixos, ≥30 pts/curva OU nº de pontos do
   marcador da figura, overlay conferido.
2. **Re-fit do aço sob o drive REAL**: ≤2 números (`c_bend` do aço;
   `emb_depth` se preciso) fitados SÓ no trio da Fig. 5
   (0,05/0,05/0,04 mm). A **Fig. 10 é held-out** (zero olhada no fit).
3. **Gates de adoção**: G2 held-out — as 2 amplitudes NÃO-fitadas da
   Fig. 10 (0,03 e 0,10) com MAE ≤ 0,10 cada OU distância declarada sem
   adoção; G3 nenhuma HDPE piora >0,01; G4 procedência por número; G5
   sincronia total no mesmo commit (re-stamp se cfg mudar).
   Ramo INCONCLUSIVO: digitalização falha no G1 ⇒ parar e documentar.

## EMENDA (mesma sessão, ANTES de qualquer fit — vetagem das figuras)

**A Fig. 10 NÃO é curva de afrouxamento**: é laço de histerese (força
transversal × deslocamento, 3 amplitudes) — inutilizável para a métrica
F/F₀-vs-N; Figs. 7–8 idem (% de perda vs rigidez, 2 pontos de ciclo). O
held-out do plano passa a ser a **Fig. 6** (VETADA na imagem: preload
F_b vs ciclos 0–95, aço 3,5→~0,6 kN e HDPE 3,5→2,8 kN, t10, 0,2 mm,
F₀≈3,5 kN — condição NOVA para os dois ramos; atenção do tracer: a
rotação tracejada VERMELHA divide a cor com o F_b do aço — filtro de
runs curtos). Gates inalterados na substância: fit do aço SÓ na Fig. 5;
Fig. 6 (aço E HDPE, zero-refit no HDPE) é o held-out; G2 passa a ser
"as 2 curvas da Fig. 6 com MAE ≤ 0,10 OU distância declarada sem
adoção".

## Previsão registrada

Sob o drive real o aço está em regime de micro-slip (t14 já é stick):
espera-se sensibilidade FORTE a `c_bend` (k_tr define quanto slip resta) e
a Fig. 10 deve ordenar 0,03 < 0,05 < 0,10 em perda — se o modelo re-fitado
não reproduzir a ORDEM, a forma de amplitude no aço está errada
(informação classe-N₉₅, desta vez com dado consistente).
