# Prereg — re-digitalização da `rousseau2025_hdpe_t10` (alvo independente)

**2026-08-02** · decorre de `rousseau_fig7_validacao.md`: a t10 é a única
das três HDPE que discorda da Fig. 7, e discorda nas duas leituras no
mesmo sentido (+5 pontos de retenção).

## Hipótese (declarada antes de traçar)

Na Fig. 4 a curva de 10 mm é uma **banda oscilante larga** (linha fina e
ruidosa, ao contrário da t12 e da t14, que são traços limpos). A
digitalização antiga provavelmente seguiu o **topo da banda** em vez do
**centro** — o que produz exatamente um viés positivo de retenção, e só
na curva ruidosa. É por isso que t12/t14 batem a 1 ponto e a t10 não.

## Alvo — independente, e do próprio paper

A Fig. 7 (lida como retenção; errata registrada) dá para a t10:
**62 % em N=100** e **43 % em N=182**. Esses números **não vêm da Fig. 4**
nem do nosso modelo ⇒ servem de gate honesto.

## Gates

- **G1 (alvo)**: a curva nova tem de dar **62 ± 2** em N=100 e
  **43 ± 2** em N=182. (A atual dá 67,2 e 46,3 ⇒ falha nos dois.)
- **G2 (não quebrar o que estava certo)**: as curvas t12 e t14 **não são
  tocadas** (já batem a 1 ponto); se o mesmo script as re-extrair, elas
  têm de continuar em 80±2 / 62±2 e 98±2 / 96±2.
- **G3 (traço)**: centro da banda por mediana do run contíguo, com a
  monotonicidade do preload (só desce) para não pular na curva de rotação
  — mesma maquinaria da Fig. 6.
- **G4 (efeito no censo)**: re-simular só a t10 e reportar o antes/depois.
  Se o MAE **piorar**, a curva nova vale mesmo assim (o critério é o alvo
  do paper, não o nosso ajuste) — e isso fica dito.
- **INCONCLUSIVO**: se o traço do centro não alcançar 62/43, a hipótese
  do "topo da banda" cai e o desvio é outro — documentar e parar.

## Previsão registrada

Se a hipótese estiver certa, o centro da banda deve descer ~5 pontos em
relação à curva atual **de forma aproximadamente uniforme** (a largura da
banda é visualmente constante), não só no fim.
