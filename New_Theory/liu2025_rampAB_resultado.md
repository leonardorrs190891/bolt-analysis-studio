# A vs B, medido — a ESCOLHA: **Opção A com energética por incremento (A1)**

**Data:** 2026-07-28 · **Delegação:** professor, *"investigue mais a fundo e escolha a
opção que você recomendar"* · **Sonda:** `liu2025_rampAB_probe.py` (engine intocado)
**Previsão registrada ANTES de rodar** (cabeçalho da sonda): *"A1 ≈ B1 na forma da curva
(diferenças de 2ª ordem, B levemente mais lento no fim); residual de A0 pior que A1"*.

---

## 0. A escolha e o porquê em uma linha

> **Opção A (rampa aplica `dF_0` direto) com a energética do cliff por incremento.**
> Medido: B produz **a mesma curva** (Δ cruzamentos ≤ 60 ciclos, ≪ tolerâncias de
> 930–2550), **não conserta a `amp0p6`**, e **quebra a conservação de energia**
> (residual até **−20,5 J** contra **−0,017 J** do A1 no mesmo caso — três ordens de
> grandeza). A vantagem filosófica do B não sobrevive à medição neste carregamento.

---

## 1. O que a investigação estrutural achou antes de medir

Lendo o engine (não o argumento do prereg v1):

1. **O feedback "F₀ cai → mais slip → mais wear" NÃO passa por `k_b`.** Ele corre por
   `state.F_0` (`F_slip = μ·F₀` no slip disp-mode) — e portanto **as duas opções já o
   têm**. A narrativa "acoplamento de graça via k_b" do prereg v1 atribuía ao `k_b` um
   caminho que na verdade é do `F_0`.
2. **`k_tr` (modo bending) usa `d₂⁴`, não `k_b`** — o slip transversal é cego a `k_b`.
3. O que `k_b` de fato toca por ciclo: **o conversor `dF_0 = −k_b·dδ` de TODOS os outros
   mecanismos** (embedding/creep/wear/fretting/loosening), o **Φ** axial, o slip de
   flanco (`F_ax/k_b`, fretting — inerte em transversal) e o **`U_internal`**.
4. Logo, os canais próprios do B neste carregamento têm sinal **negativo** (parafuso mais
   mole perde *menos* pré-carga por múon de assentamento) ou são inertes — o oposto do
   "feedback positivo" imaginado.

## 2. O que a sonda mediu (A0 = sonda dos gates v2 · A1 = +energética · B1 = +k_b modulado)

**Forma da curva — idêntica.** Cruzamentos em vida (ciclos, assinado):

| caso | var | d@0,80 | d@0,70 | d@0,60 | d@0,50 | d@0,40 | passes |
|---|---|---:|---:|---:|---:|---:|---:|
| amp0p4 (tol 2550) | A1 | +1554 | −125 | −477 | −489 | −505 | 5/5 |
| | **B1** | +1558 | −132 | −503 | −531 | −557 | 5/5 |
| amp0p5 (tol 1200) | A1 | +801 | +138 | −260 | −506 | −498 | 5/5 |
| | **B1** | +803 | +137 | −271 | −525 | −522 | 5/5 |
| **amp0p6** (tol 930) | A1 | −2954 | −2729 | −1274 | −771 | −605 | 2/5 |
| | **B1** | **−2954** | **−2729** | −1268 | −760 | −601 | **2/5** |
| fig2 fino (tol 300) | A1 | +1871 | +296 | −33 | −30 | +43 | 4/5 |
| | **B1** | +1872 | +295 | −36 | −35 | +37 | 4/5 |

- **A0 reproduz os gates v2 exatamente** (mesmos números) — a sonda regride limpa.
- **A hipótese "B explicaria a `amp0p6`" está MORTA por medição:** os dois primeiros
  cruzamentos dela são idênticos ao dígito (−2954/−2729) e o passe segue 2/5. O desvio
  da `amp0p6` é do **relógio/coordenada**, não do acoplamento de rigidez.

**Decomposição na janela da rampa (N ≥ 0,75·N_f)** — o sinal dos canais do B, medido:

| mecanismo (amp0p6, o caso de maior wear) | A1 [kN] | B1 [kN] | B−A |
|---|---:|---:|---:|
| wear | −10,012 | −9,309 | **+0,703** (B perde MENOS) |
| rotational_loosening | −1,817 | −1,716 | +0,101 |
| fatigue (rampa) | −32,632 | −33,441 | −0,809 (compensa) |

Confirmado: os canais próprios do B **amortecem** (sinal +) e a rampa apenas compensa
para levar F₀ a zero do mesmo jeito. Efeito líquido na curva: nulo.

**Energia — a coluna que decide:**

| caso | A0 (dE=0) | **A1 (dE=ΔU)** | B1 |
|---|---:|---:|---:|
| amp0p4 | 1,9 | **0,148** | −1,86 |
| amp0p5 | 1,8 | **0,089** | −2,83 |
| amp0p6 | 0,741 | **−0,151** | −2,63 |
| fig2 | 1,73 | **−0,017** | **−20,5** |

A1 melhora o residual de A0 por **10–100×** — a energética do cliff (liberar
`ΔU_internal` por incremento → `W_diss_fracture`) transplanta limpa para a rampa. **B1 é
pior que a sonda crua:** modular `k_b` muda `U_internal = F₀²/(2k_b) + …` sem contraparte
de trabalho — com `k_b` caindo a `F₀` constante, energia elástica **aparece do nada**
(−20,5 J). Uma implementação B correta exigiria contabilizar o termo `∂U/∂k·dk` — custo
real, medido, para ganho de forma **zero**.

## 3. A decisão, registrada

**Escolhida: Opção A com energética por incremento (variante A1).**

- Reproduz **bit a bit** a forma validada nos gates v2 (10/10 no núcleo `amp0p4/0p5`).
- Residual de conservação ≤ |0,151| J nos 4 casos — dentro do padrão L7.
- Raio de mudança mínimo: um mecanismo, opt-in, sem tocar `geom`, `Φ`, `k_tr` nem os
  conversores dos outros mecanismos.
- **B fica REGISTRADO como candidato de forma para a família competitive-failure** — mas
  com o registro corrigido pelo que se mediu: neste carregamento seus canais são de
  2ª ordem e sinal negativo, ele não conserta a `amp0p6`, e carrega uma dívida de
  bookkeeping (`∂U/∂k`). Só volta se uma fonte com acoplamento transversal/axial forte
  o exigir — e aí com a energética resolvida no prereg dele.

## 4. Próximo passo (não executado)

O pré-registro de implementação da Opção A está escrito e congelado
(`specs/2026-07-28-ramp-capability-prereg.md`), com as contas de satisfazibilidade
**tiradas desta sonda**. Implementar = executar aquele prereg; aguarda a sua palavra.

## 5. Reprodutibilidade

```bash
py -3.12 New_Theory/liu2025_rampAB_probe.py    # ~2 min, engine intocado
```
Resultado bruto: `New_Theory/liu2025_rampAB_result.json`.
