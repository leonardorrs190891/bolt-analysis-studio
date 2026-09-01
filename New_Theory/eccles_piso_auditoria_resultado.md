# O piso do ECCLES: minha pista caiu, e a auditoria achou **outra coisa**

**2026-08-09** · só-leitura · **nada adotado**.

## O caminho

Diagnosticando onde o resíduo **se forma** nas curvas B "paradas", encontrei que
o defeito é o **joelho**: nas duas do ECCLES o maior salto está entre os ciclos
**150 e 188** (u = 0,09). O modelo desce tarde, **atravessa** o dado e arresta
**abaixo** dele — depois fica plano (`fig7c`: 0,180 → 0,166 em 1400 ciclos)
enquanto o dado se mantém em ~0,195.

Isso sugeria uma correção de procedência: o `loose_arrest_floor` da `fig7c` é
**0,182**, lido do *último ponto* (0,1800) — mas o **platô** parecia ser ~0,193,
e a física do piso é *"núcleo auto-travado"*, que é o platô. E 0,19–0,20 é
justamente a faixa que fecha a curva.

## ⛔ A pista caiu — o helper canônico me corrige

`provenance.arrest_floor_from_curve` devolve, para a `fig7c`:

```
valor 0,1800 · plateau = True · provenance "data_end_plateau" · n_tail = 2
```

**O helper considera que a curva TEM platô**, e o valor dele é 0,1800. O `0,182`
do config **bate**. O "platô 0,1930" que eu calculei era **definição minha
ad-hoc** — janela de 5 pontos de menor desvio —, não a regra canônica.

⇒ **não há correção legítima de procedência na `fig7c`.** O piso fica onde está,
e a curva segue form-limited.

⚠️ **Foi por pouco.** Eu tinha um argumento coerente (*"a física é o platô, não o
último ponto"*), um número que fechava a curva, e uma frase do docstring que
parecia me apoiar. O que impediu de adotar foi **chamar o helper** em vez de
usar a minha definição — exatamente a regra que a campanha repete: *pergunte ao
helper, não reimplemente a regra*.

## ✅ Mas a auditoria achou outra coisa: **3 pisos abaixo do limite inferior**

O docstring é explícito: *"curva que termina em queda (sem platô) ⇒ o valor é um
**LIMITE INFERIOR** do floor"*, e o breakdown marca `plateau=False`.

Três curvas do ECCLES estão nesse caso — e nas três o **config está ABAIXO do
limite inferior**:

| curva | cfg | helper (limite inferior) | déficit |
|---|---:|---:|---:|
| `eccles2010_fig7d_axial_3p1kN` | **0,137** | 0,1970 | **−0,060** |
| `eccles2010_fig8a_no_axial_baseline1` | **0,059** | 0,1291 | **−0,070** |
| `eccles2010_fig8b_axial_0p7kN` | **0,000** | 0,1633 | **−0,163** |

As outras 5 têm `plateau=True` e batem com o helper a ≤0,004.

⇒ **os três pisos que o helper não consegue fixar são exatamente os três que
divergem** — e divergem para **baixo**, ou seja o modelo tem licença para
afrouxar mais do que o dado autoriza.

⚠️ **Não é conclusão de erro.** O `prov` diz *"assíntota final crua ≥0,03"*, e o
cfg pode ter sido lido da **CSV crua** (que continua abaixo do `FLOOR_TRIM`),
enquanto o helper lê o `metric_data` **trimado**. As duas leituras respondem a
perguntas diferentes, e qual é a certa é decisão de método — não medição.

**O que está medido:** as 3 curvas com `plateau=False` são as 3 que divergem, o
sinal é sempre o mesmo (config **abaixo**), e o `fig8b` tem piso **0,000** contra
um limite inferior de **0,163**.

## Reprodutibilidade

```bash
py -3.12 -c "from bolt_analysis_studio.calibration import provenance as pv; ..."
```
Sondas no scratchpad: `arrest_floor_from_curve` sobre o `metric_data` das 8
curvas do ECCLES, comparado ao `cfg` efetivo. Segundos.
