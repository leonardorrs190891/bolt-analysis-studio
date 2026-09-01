# Prereg R2 — creep com onset no ZHANG_2018, engenharia de adoção

**Data:** 2026-07-30 · **Baseline:** store `3546e6745448` · régua D1.
Rodada 2 do candidato do prereg `2026-07-30-zhang18-creep-onset-prereg.md`
(R1). Gates imutáveis. Execução por delegação (mandato 2026-07-30).

## 0. O que a R1 estabeleceu (e o que faltou)

R1 executada: **G1 ok** (mapa A→C linear, ±1 %), **G2 ok — superposição
essencialmente exata** (desvio máx 0,0005 em 9 curvas), **G3 GENERALIZA**
(held-out de 8 curvas: mediana σ 0,0242→0,0106, ZERO pioras de σ), **G5 ok**
(as 3 da fila fechavam). **G4 REPROVOU**: com (A=0,01261, N₀=562) três curvas
pioravam >+0,01 em **MAE** (test2, fig13_26kN e fig16_with_locker, esta
também em mx) — o premeasure não podia ver isso porque 8/9 curvas estavam
held e fora da restrição. **Nada foi adotado.** O MECANISMO está validado
(G2+G3); o que falhou foi a parametrização compartilhada naquele ponto.

## 1. Natureza da R2 (declarada)

R2 é **engenharia de adoção DENTRO da família validada** — não há nova
alegação de generalização (a evidência é a G3 da R1, banked). Por isso o
acervo INTEIRO (9 curvas, 3 pernas) entra como RESTRIÇÃO da seleção
analítica, o que a R1 proibia às held. Varredura A×N₀ com restrição
completa: **viável e fecha a fila 3/3 em config única** (sem per_case;
a variante per_case p/ locker também era viável e foi preterida por
parcimônia — uma física para a fonte inteira).

## 2. Leitura congelada

* **A = 0,00700** (fração de F₀/ln) · **N₀ = 1081 ciclos** → `t_0 = 108,1 s`
  a 10 Hz. `C'` calibrado por 2 sims (mapa linear, como na R1, no novo N₀).
* Config: só `C_creep = C'` e `t_0 = 108,1` mudam; o resto fica.

## 3. Previsões congeladas (σ analítico; sim confere em ±0,005)

| curva | σ antes | σ prev | MAE prev | mx prev |
|---|--:|--:|--:|--:|
| test1_1e3cyc | 0.0072 | 0.0078 | 0.0181 | 0.0273 |
| test2_1e4cyc | 0.0121 | 0.0101 | 0.0198 | 0.0433 |
| test3_1e5cyc | 0.0244 | 0.0150 | 0.0169 | 0.0444 |
| test4_5e5cyc (fila) | 0.0294 | **0.0157** | 0.0141 | 0.0437 |
| fig13_14kN (fila) | 0.0297 | **0.0181** | 0.0130 | 0.0575 |
| fig13_20kN | 0.0242 | 0.0118 | 0.0095 | 0.0281 |
| fig13_26kN | 0.0186 | 0.0056 | 0.0071 | 0.0228 |
| fig16_with_locker | 0.0091 | 0.0064 | 0.0154 | 0.0269 |
| fig16_without (fila) | 0.0263 | **0.0143** | 0.0103 | 0.0418 |

Previsto: **as 9 fecham o tripé efetivo** (lim σ 0,0250 · MAE 0,05 · mx 0,10)
— a fonte inteira sai da fila e das near-misses.

## 4. Gates (imutáveis; UMA execução, sem iterar)

* **G1′** mapa A→C linear no novo N₀: 2ª sim reproduz A em ±10 %.
* **G2′** σ_sim vs σ_prev em ±0,005 por curva (falha em >2 ⇒ INCONCLUSIVO).
* **G4′** acervo: nenhuma das 9 piora >+0,01 em NENHUMA perna, na sim real.
* **G5′** as 3 da fila fecham o tripé efetivo na sim real.

**PASSA = G1′∧G2′∧G4′∧G5′ ⇒ adotar por delegação** (`C_creep=C'`,
`t_0=108,1`; procedência: "onset lido do resíduo (L24); generalização
provada na R1 (G3, 8 held, mediana 0,0242→0,0106, 0 pioras); R2 = seleção
viável sob acervo completo; prereg R2 2026-07-30; por delegação"). Depois:
re-carimbar o store INTEIRO (fingerprint muda) + `exemplo_m12_sintetico`
direto + reports + fila/docs no mesmo push.

## 5. Falsificadores

* **F1′** G4′/G5′ reprovam na sim com o analítico dizendo que passam ⇒ a
  superposição falha exatamente nas bordas dos gates — registrar o desvio;
  NÃO iterar dentro desta execução (gates imutáveis); nova rodada só com
  novo prereg.
* **F2′** G1′/G2′ reprovam ⇒ INCONCLUSIVO de instrumento.
* A R2 **não** reabre a questão do mecanismo: reprovar aqui NÃO falsifica o
  creep-com-onset (já validado); só nega ESTA parametrização.
