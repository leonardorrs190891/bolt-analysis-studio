# Auditoria de inputs da fila pós-adoções — 4 alvos, 3 vereditos de F1, 1 gap real e inerte

**2026-07-30 (noite)** · continuação do mandato após a fronteira declarada;
tudo só-leitura + sondas de 2 pontos. Store `02577541893d`.

## YANG_2021 ×2 (o achado principal)

* **Gap de representação REAL**: o paper aplica axial senoidal + transversal
  senoidal simultâneos (10 Hz; amplitudes axiais documentadas POR CURVA:
  2,0 / 8,0 / 11,2 / 6? kN — tabela da nota). O runner roda a família
  transversal com `theta=π/2` fixo e `F_amp=0,4·F₀` default ⇒ o axial
  documentado é estruturalmente descartado (cos π/2 = 0).
* **Mas o gap é INERTE hoje** (sonda de 2 pontos, bit-idêntico): corrigir o
  VALOR de F_amp e até expor `theta=0` não muda NADA — nenhum mecanismo
  ativo da config lê F_ax (`k_thread_fret=0`, L1 é só força-modo,
  `fatigue_enabled` off, `couple_famp_slip` off).
* **Canal aditivo F_ax: F1** — scan da família fretting com F_ax documentado
  por curva (a escala de amplitude vem de graça): o melhor ponto viável
  fecha só as 2 que JÁ passavam; as 2 da fila mal se movem (amp0p5 piora
  MAE 0,0549→0,0646; amp1p0 Δsd 0,0001).
* **Rota de fadiga**: já sondada por sessão anterior — ramo **PIORA**
  (registro vivo; só a âncora de vida por bisseção presta, 6/6 a 0,0 %).
* ⇒ As duas curvas ficam form-limited com o diagnóstico completo: o defeito
  é a FORMA da competição afrouxamento-fadiga (ξ do paper), não input nem
  canal aditivo. Qualquer candidato novo precisa de forma (PR-3).

## SUN_2025_CRIMP ×1

Freq 12,5 Hz está **documentada** na nota (transversal 12,5 / axial 25 Hz)
— não é o erro do default (o precedente YANG_2023_IJPEM não se repete aqui).
A fonte também é carga combinada; o axial de 25 Hz é invisível na fiação
atual pela mesma razão do yang2021 (e pela mesma medição, inerte sem
mecanismo que leia F_ax). Fica form-limited.

## CACCESE_2009 ×1

Caso de creep estático (freq 1/3600 Hz, F_amp=0, delta=0) — não há input
dinâmico para auditar; o σ 0,0354 vs lim 0,0270 é forma da lei de creep na
janela. A exceção da rep1 é por MAE/piso e não cobre a rep2 (σ é a perna).

## LIU_2022_RETIGHT ×3 (âncora de renovação: direção ERRADA)

A ideia "ancorar `k_emb_renew` no fig3 do liu2016 (12 reapertos sem
vibração)" morre na aritmética do próprio engine: `retighten()` renova
`δ_emb·(1−k_emb_renew·D)` — renovar MAIS ⇒ mais assentamento fresco ⇒ MAIS
perda nos estágios seguintes. t1/t2 precisam de MENOS perda (resíduo
−0,07..−0,09) ⇒ a âncora empurraria contra. O defeito da cadeia é o
transporte de estado com sinais opostos ao longo dela (t4 precisa de MAIS
perda) — dois mecanismos, n=7–11 por curva, 18 irmãs passando como
restrição. Estrutural; fila do professor.

## Instrumento re-medido

`fila_teto_log_onset.json` regenerado no store `02577541893d` (o anterior
era pré-adoções): universo amplo de 34 fora não-exceção/declarada, teto
em-família fecha **9/34**. Uso: triagem de candidatos aditivos antes de
gastar sim.
