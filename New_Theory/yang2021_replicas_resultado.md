# YANG_2021 — réplicas 0,6 mm–8 kN digitalizadas: +2 tripé por mérito, rota F7 fechada por medição

**2026-07-31 (noite)** · Bloco 6 do `plano_tripe_restante.md`, executado sob o
prereg `docs/superpowers/specs/2026-07-31-yang2021-replicas-0p6-prereg.md`
(gates imutáveis, escritos antes de qualquer medição). Ferramental:
`New_Theory/digitize_yang2021_replicas.py` (arquitetura do digitalizador da
Fig. 14 do Lu). Fingerprint inalterado `3d432a65c7e8` (casos novos não mudam
config); censo **201→203**.

## O que entrou

As duas réplicas não-digitalizadas da condição crítica ξ=0,075 (Fig. 6b2/6b3
do paper, open access): `yang2021_amp0p6mm_ax8kN_r2` (vida 14.699) e `_r3`
(vida 16.251), normalizadas por F0 nominal 14,1 kN como a r1.

**G1 (integridade) PASSOU com folga**: média das 3 vidas = **14.483 vs
Tabela 3 = 14.666 (desvio 1,2 %**, gate ±8 %) — a Tabela 3 é evidentemente a
média das três réplicas, e a digitalização a reproduz. Overlays conferidos
(traço sobre a curva no platô, joelho, ruído de fretting e colapso); N_F
digitalizado 13.963/13.743 sobre as tracejadas dos próprios painéis; 101/107
pts. Dois defeitos instrumentais achados e consertados no caminho (ticks
deste periódico apontam para FORA e têm ~10 px — a janela de 21 px diluía a
soma; margem de 3 px comia o pico de overshoot colado no eixo-y).

## Os DOIS pisos — e por que os dois números são verdade

| medição | janela | MAE | mx | σ |
|---|---|---|---|---|
| curvas completas (standalone) | até o colapso | 0,0423 | **0,4717** | **0,0787** |
| maquinaria `_pisos_medidos` (canônica) | métrica [0, 11.800] | 0,0282 | 0,0540 | **0,0071** |

O trim assinado da condição (`trim_n_max=11800`, exclusão da queda
crack-driven — nota de aparato: "final drop is CRACK-driven, not loosening")
casa por token com as TRÊS réplicas ⇒ julgamento consistente na mesma janela.
O scatter GRANDE (σ 0,079; colapso variando 12,5→16,3 k = ±13 % de vida) vive
inteiro **fora da janela da métrica**; dentro dela a bancada repete a
**σ 0,0071** — 3,5× MELHOR que o limite global de 0,025.

## Consequências (ramos do prereg, todos declarados antes)

1. **r2/r3 no TRIPÉ por mérito** (zero fit, config adotado da fonte):
   r2 MAE 0,0403 · mx 0,0487 · σ 0,0088; r3 MAE 0,0209 · mx 0,0387 ·
   σ 0,0093. Julgado contra 3 corridas independentes da mesma condição, o
   modelo erra 0,021–0,040 onde as réplicas diferem entre si 0,028 —
   **modelo-vs-dado ≈ dado-vs-dado**; nenhuma exceção foi necessária.
2. **D1 não move o limite**: piso da fonte (média das 2 famílias) = MAE
   0,0214 · mx 0,0636 · σ **0,0113** < 0,025 ⇒ `limite_sres` fica 0,025.
3. **A rota F7 para as 2 da fila está FECHADA por medição** — ramo
   previsto no prereg ("se der < 0,025, a fonte é mais repetível que o
   modelo erra"): o σ da `amp0p5` (0,0458) e da `amp1p0` (0,0476) é **6,5×
   o ruído real do dado na janela**. São **form-limited de verdade**
   (competição afrouxamento×fadiga entre condições ξ — F1 aditivo e
   fadiga-PIORA já falsificados). A previsão do prereg (piso-σ ≥ 0,04)
   valia para a curva completa (0,079 ✓) e ERROU na janela da métrica
   (0,0071) — registrado como aprendizado: *scatter de colapso ≠ piso da
   métrica quando o trim exclui o colapso*.
4. Cross-condição: nada assinado (G3, lição LU).

## Censo após o bloco

**n=203 · tripé 136 (67 %) · fora 67 = 29 exceções + 9 declaradas + 29
não-resolvidas (a MESMA fila)** · resolvida/declarada **174/203**. Pins
206→208 (registry) sincronizados; `_VIVAS` /203; docs vivos no mesmo commit.

## O que o bloco ensina para o plano

O retorno veio de onde não se esperava: não pelo piso (rota F7), mas por
**+2 curvas de validação grátis no tripé** e pela **prova de que a fila da
fonte é form-limited** — o instrumento decidiu a classe, que era o objetivo.
Próximo do plano: auditoria de réplicas do YANG_2019 (mesma técnica).
