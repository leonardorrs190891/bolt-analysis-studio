# A última curva da fila: o modelo é cego à frequência, e o teto é ALGÉBRICO

**2026-08-05** · sonda só-leitura `New_Theory/li2022_lei_frequencia_sonda.py`,
store `b70276f2fa43` (pós-D-Q e D-S). Nada escrito.

Depois das adoções **D-Q** (saturação de flanco) e **D-S** (correção da CSV do
CACCESE), a fila form-limited é **1 curva**: `li2022ti_axialmin_10Hz`
(MAE 0,0589 = **1,18×**; res.máx 0,80×; σ 0,90×).

## O defeito, em uma linha

A perda total do MODELO nas três frequências é **0,1539 / 0,1537 / 0,1535**
(espalhamento **0,03 %**). A do DADO varia **2,0×**: 0,1792 / 0,1417 / 0,0892.

## A dependência é REAL — sobrevive à dispersão do próprio paper

Ajustando `perda ∝ f^−a`:

| par | a |
|---|---:|
| 10–15 Hz | 0,579 |
| **10–20 Hz** | **1,006** |
| 15–20 Hz | 1,609 |
| global (mín. quadrados log-log) | **0,978** |

Com a dispersão publicada na Fig. 8(d) (±0,0240 / 0,0190 / 0,0130 em F/F₀), o
pior caso em cada direção dá **a ∈ [0,603 · 1,415]**. **A banda exclui zero** — e
o modelo entrega **a = 0,000**.

`a ≈ 1` significa **perda proporcional ao TEMPO decorrido, não aos ciclos**
(t = N/f: 20 000 s a 10 Hz contra 10 000 s a 20 Hz).

## Decomposição: quem carrega a perda, e quem varia com f

| canal | 10 Hz | 15 Hz | 20 Hz | amplitude |
|---|---:|---:|---:|---:|
| embedding | 78,1 % | 78,6 % | 78,9 % | 0,8 pp |
| **creep** | **12,6 %** | 12,1 % | 11,7 % | **1,0 pp** |
| thread_fretting | 9,3 % | 9,4 % | 9,4 % | 0,2 pp |
| wear · fadiga · afrouxamento | −0,0 % | −0,0 % | −0,0 % | 0,0 pp |

**Nenhuma fatia se move.** O creep é o único canal f-dependente **por
construção** (a lei é função de `t = N/f`) e ele varia 1 ponto percentual onde o
dado varia 100 %.

## ⚠️ TETO DE AUTORIDADE: re-pesar canais está FALSIFICADO por álgebra

Sonda do charter (*suprima/sature o canal e pergunte se o alvo está no
alcançável*), aplicada ao kernel logarítmico do creep, `δ = C·log(t/t₀+1)`:

| t₀ | razão interna do creep (10 Hz ÷ 20 Hz) | fatia que ela EXIGIRIA |
|---:|---:|---:|
| 1 s | 1,0753 | **1341 %** |
| 10 s | 1,1003 | 1006 % |
| 100 s | 1,1491 | 677 % |
| 1000 s | 1,2697 | 374 % |

Razão alcançável com o creep **de hoje** (12,6 %): **1,0095**.
Razão alcançável com o creep a **100 % da perda**: **1,0753**.
Alvo: **2,009**.

⇒ **mesmo se o creep carregasse TODA a perda da curva, o kernel log fica em
1,08 onde o dado pede 2,01.** O alvo está fora do conjunto alcançável por
qualquer redistribuição entre os canais atuais. Isto é falsificação **por
álgebra**, na mesma classe do amplificador puro `(1+g)^n` morto em 2026-08-05
(contradomínio [1,∞) quando o fator necessário era <1) e dos gates Hill que só
sabiam atrasar.

**Custo poupado:** esta conta vale 1 simulação e teria evitado qualquer varredura
de `C_creep`/`t_0_creep` nesta fonte.

## As duas rotas que sobram, com o preço de cada uma

### (a) Flanco — `fret_freq_exp`

A lei de `flank_wear_from_slip` tem expoente de frequência **explícito**. Com a
fatia de 9,3 %, o expoente necessário é

> **`fret_freq_exp` = 3,57**

Medição anterior (`li2022ti_fret_freq_resultado.md`): melhora o 20 Hz nas **três**
pernas e **destrói a curva longa**. Não foi falsificação pré-registrada — foi
recusa por custo. ⚠️ E precisa ser **re-medida sob o config pós-D-Q**: a saturação
de flanco corta justamente a magnitude do canal onde o sinal de frequência mora
(anti-sinergia já medida: a razão degrada de 0,529 para 0,814 conforme a saturação
aperta).

### (b) Kernel do creep — trocar log por algo com razão 2,0 em 2× de tempo

Razão 2,0 em dobro de tempo ⇒ **~linear em t** (lei de potência com n ≈ 1).

⚠️ **Raio de explosão desproporcional:** o kernel de creep serve **toda** a
população dominada por creep — CACCESE_2009 (7/7 no tripé), JCSR_2023, QIN_2024,
LI_2022_MARSTRUC, ZHANG_2018 (9/9) —, dezenas de curvas, **por +1 curva**. E o
D-H acabou de adotar `creep_mode="saturating"` no CACCESE justamente porque lá a
curvatura do log estava errada **na direção oposta**.

Isto **não** é decisão de sessão. É mudança da lei de creep do modelo, e vai à
fila do professor com o número na mão.

## Onde isto deixa a regra de parada

A regra exige (a) classe identificada por ≥2 instrumentos independentes, (b)
**todo** membro falsificado por predição pré-registrada, (c) retorno marginal
nulo.

* **(a) cumprido** — dois instrumentos: a re-atribuição creep→flanco (que
  entregou 0 % → 93 % da dependência) e a invariância de perda + teto de
  autoridade medidos aqui.
* **(b) NÃO cumprido** — a re-pesagem de canais está falsificada (por álgebra,
  que é mais forte que predição), mas `fret_freq_exp = 3,57` e o kernel de creep
  **não** foram falsificados: um foi recusado por custo, o outro nem foi tentado.
* **(c)** a fila é 1 curva; fechá-la vale +1 em 205.

⇒ **a regra NÃO autoriza parar.** O que ela autoriza é dizer exatamente o que
falta: duas medições pré-registradas, uma delas (o kernel) com raio de explosão
que exige assinatura antes de ser sequer medida em adoção.

## Pergunta que o dado levanta e o modelo não responde

Se `a ≈ 1`, a parte dominante da perda desta fonte é **time-driven**. Mas o canal
que carrega 78 % é o **embedding**, cuja lei é *state-based* e função do número de
ciclos, não do tempo. Ou (i) o embedding deste rig é na verdade viscoplástico
(e então a atribuição está errada, não a lei), ou (ii) há um mecanismo
time-driven não modelado que o embedding está absorvendo. **A decomposição não
distingue as duas** — distinguir exige dado com f varrida a N fixo **e** t fixo,
que este paper não publica.
