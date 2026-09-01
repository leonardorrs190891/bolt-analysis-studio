# `graded_scrit`: forma construída, documentada, parametrizada — e **sem caso de uso demonstrado** na biblioteca

**2026-08-07** · só-leitura · **nada adotado** · fecha a linha aberta em
`graded_scrit_falsificado_resultado.md`.

## As três populações onde ele poderia servir, todas medidas

| população | por que era candidata | resultado |
|---|---|---|
| **P-13** (SUN · ROUSSEAU HDPE · IJPEM) | o docstring diz que ele remove o *runaway* que medi nas três | **falsificado**: final **0,0000** em 16/16 células; o dado quer 0,52 |
| **BAUER fig6** | o docstring cita a procedência: *"Bauer 76-108 µm; curva amplitude-vs-vida"* | **piora**: MAE 0,0431 → **0,3223** no valor de procedência; tripé **2 → 1** abaixo dele |
| **KARLSEN** | o docstring cita *"near-linear catastrophic back-off"* | **nada a ganhar**: a fonte fecha **11/11** desde o D-Z |

## O que o teste do BAUER mostrou, e onde eu errei a previsão

Medi o slip que o **modelo** calcula na família fig6: mediana **57–61 µm** — e o
`s_crit` de procedência é **76–108 µm**. Previ que o branch ficaria **inerte**
(`excess = max(0, slip − s_crit) = 0`), como no IJPEM.

**Errado.** Em `s_crit` = 76 µm o resultado não é idêntico ao nominal; é muito
pior:

| curva | nominal | s_crit 76 µm (procedência) | s_crit 30 µm |
|---|---|---|---|
| `rep1` | 0,0431 / 0,1259 | **0,3223 / 0,7061** | 0,1455 / 0,3296 |
| `rep2` | 0,0420 / 0,0862 **SIM** | 0,3000 / 0,5985 | 0,0702 / 0,1424 |
| `rep3` | 0,0336 / 0,0698 **SIM** | 0,2470 / 0,5101 | 0,0356 / 0,0651 **SIM** |
| `rep4` | 0,0783 / 0,1709 | 0,3554 / 0,7191 | 0,0556 / 0,1064 |

**A razão:** o branch **substitui** o kernel de torque por inteiro (`return`
antecipado). Mesmo quando o termo graduado contribui pouco, ele **remove** o que
havia. Inércia exigiria que o branch nem rodasse — e ele roda, porque a
*distribuição* de slip tem caudas acima da mediana.

⇒ lição: `excess ≤ 0` na **mediana** não implica branch inerte. O que decide é a
cauda, e um kernel que substitui outro nunca é inerte por ser pequeno.

## O veredicto, com o escopo declarado

**Nenhuma das três populações citadas melhora.** A forma existe, está
documentada com física plausível e procedência, tem três parâmetros — e **não há
hoje, nas 205 curvas, um caso onde ela ajude**.

⚠️ **Escopo honesto — dois dos três testes são CONFUNDIDOS:**

* **BAUER e KARLSEN**: troquei o kernel mantendo as constantes fitadas para o
  kernel **antigo**. É o mesmo confundimento do premeasure do LU, e um re-fit
  poderia mudar o veredicto.
* **P-13**: este **não** é confundido. O que se mede lá é o **destino**
  (final = 0,0000 em todas as células, contra 0,52 do dado), e destino é
  estrutural: nenhuma escolha de `k_loose_graded` ou `s_crit_loose` faz uma taxa
  constante parar num platô. Re-fitar não muda isso.

⇒ a afirmação forte que fica é só sobre a P-13: **`graded_scrit` não a resolve, e
não é questão de calibração.** Sobre BAUER/KARLSEN, o que fica é *"não ajuda com
as constantes atuais"*, o que é mais fraco.

## Consequência para o inventário

`formas_faltantes_inventario.md` listava a forma #8 como *"já existe no engine,
default-inerte"* — sugerindo capacidade disponível. A leitura correta agora:

> **capacidade existente sem caso de uso demonstrado.** Ligá-la exige (a)
> encontrar a população que a pede e (b) re-fitar as constantes do rig, porque
> ela substitui o kernel em vez de compor com ele.

Isso não é motivo para removê-la — é motivo para **não contá-la como rota
disponível** quando se planeja o trabalho de engine.

## Reprodutibilidade

Todas as varreduras (P-13, BAUER × 2 valores de `s_crit`) e a instrumentação de
`resolve_transverse_slip` estão no scratchpad, recomputáveis em minutos.
