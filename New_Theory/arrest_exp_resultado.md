# `arrest_approach_exp`: a P-13 pedia forma que o engine **já tem** — e ela fecha 3 curvas

**2026-08-07** · só-leitura · **nada adotado** · corrige a P-13 e a torna um
pedido mais preciso.

## O erro que este trabalho corrige — meu, na própria P-13

Escrevi a P-13 assim:

| lei | destino | quem a tem |
|---|---|---|
| torque (default) | zero, acelerando | engine |
| `graded_scrit` | zero, linear | engine (inerte) |
| **∝ pré-carga restante** | **platô não-nulo** | **ninguém** |

**"Ninguém" estava errado.** Antes de propor forma nova eu li o
`self_locking_gate`, e o docstring dele diz o oposto:

```
g = max(0, 1 - F_min/F_0),  F_min = loose_arrest_floor * F_0_init
"o runaway (T_resist ∝ F_0) vira S-curve com ponto fixo ESTAVEL em F_min"
"exp > 1 faz a taxa morrer mais cedo perto do piso => DESACELERACAO AO PLATO"
```

O ponto fixo estável em `F_min` **é** o platô não-nulo da P-13, e
`arrest_approach_exp` (prereg grupo A, 2026-07-27) **é** a forma da aproximação.
Testei o **piso** (nível) nas três fontes e o achei falsificado; **nunca testei o
expoente** (forma). Sexta ocorrência da lição *"pergunte ao engine antes de
declarar forma faltante"* — desta vez pega **antes** de propor, não depois.

## A armadilha de companheiro, conferida ANTES de medir

```python
if mat.loose_arrest_floor <= 0.0 or state.F_0 <= 0.0:
    return 1.0            # <- early-return: o expoente nem e' lido
```

Das 18 curvas com defeito de bifurcação, **10 têm piso 0** (IJPEM, ROUSSEAU aço,
ECCLES) ⇒ o expoente é **inerte por construção** nelas, e medir lá seria o teste
inválido do `graded_scrit` outra vez. Medi só as **8 com piso > 0**.

## O resultado: 3 fecham, e os platôs acertam o dado

| curva | nominal (MAE/mx/σ) | **exp = 2,0** | final nom. | final exp2 | **dado** |
|---|---|---|---:|---:|---:|
| `bauer_fig6_rep1` | 0,0431 / 0,1259 / 0,0430 | **0,0152 / 0,0418 / 0,0181** ✅ | 0,0611 | 0,1452 | 0,1870 |
| `bauer_fig6_rep5` | 0,0494 / 0,1116 / 0,0586 | **0,0285 / 0,0709 / 0,0282** ✅ | 0,0529 | **0,1337** | **0,1357** |
| `bauer_fig8_test2` | 0,0290 / 0,1795 / 0,0461 | **0,0163 / 0,0396 / 0,0149** ✅ | 0,3236 | **0,4886** | **0,5031** |
| `bauer_fig6_rep4` | 0,0783 / 0,1709 / 0,0932 | 0,0711 / 0,1239 / 0,0797 | 0,0496 | 0,0693 | 0,1488 |
| `bauer_fig6_rep6` | 0,0757 / 0,1300 / 0,0464 | 0,1027 / 0,1574 / 0,0544 ❌ | **0,1847** | 0,2916 | **0,1801** |
| `bauer_fig8_test3` | 0,0241 / 0,1198 / 0,0251 | 0,0435 / 0,2740 / 0,0559 ❌ | 0,3617 | 0,5159 | 0,2419 |
| `rousseau_hdpe_t10` | 0,0927 / 0,1786 / 0,0691 | 0,1670 / 0,2391 / 0,0667 ❌ | 0,2289 | 0,4214 | 0,2665 |
| `rousseau_hdpe_t12` | 0,0566 / 0,1133 / 0,0456 | 0,1143 / 0,1919 / 0,0743 ❌ | 0,3333 | 0,5303 | 0,3458 |

**Duas leituras que o número sozinho não dá:**

* onde ajuda, ajuda **nas três pernas ao mesmo tempo** e o **platô acerta o
  dado** (`rep5` 0,1337 vs 0,1357; `test2` 0,4886 vs 0,5031). É o mecanismo
  funcionando, não erro que se cancela;
* o expoente tem **uma direção só** (retém mais) e o sinal do efeito é previsível
  pelo sinal do erro de final: ajuda quem retém de menos, atrapalha quem já está
  certo (`rep6`) ou retém demais (`test3`).

## ⛔ Não é adoção: um valor compartilhado reprova no G2

Com `exp = 2,0` para todos: **3 fecham**, 1 melhora, **4 pioram** em
0,019–0,074 de MAE — muito além da tolerância de +0,01. Não existe valor único
que sirva à população.

## A hipótese que eu tinha, FALSIFICADA por procedência

Ao ver que as 6 réplicas da mesma condição carregam **4 valores** de
`tr_loose_gain` (2,2 / 1,8 / 1,8 / 1,8 / 1,6 / 1,4), li como *"botão por curva
carregando o que devia ser constante compartilhada"* — o padrão D-Z ao
contrário. **Errado, por dois testes independentes:**

**(a) A procedência diz que são lidos, não fitados.** O `adopted_configs.json`
registra, por réplica:

> *"atrito per-especime (paper: μ 0,09–0,14 zinc-flake scatter, **6 bolts
> distintos**); gain=2,2 COERENTE com a **vida N50=86**"*

e a atribuição é **monotônica com a vida medida**:

| réplica | N50 | gain |
|---|---:|---:|
| `rep1` | 86 | 2,2 |
| `rep4` | 108 | 1,8 |
| `rep5` | 165 | 1,6 |
| `rep6` | 205 | 1,4 |

Eu comparei o ganho contra o **final**; ele foi atribuído pela **velocidade**.
Observáveis diferentes.

**(b) A varredura de parcimônia confirma.** Grade 6×5 de
`(tr_loose_gain, arrest_approach_exp)` **compartilhados**, 180 simulações:

| | números | tripé | soma de MAE |
|---|---:|---:|---:|
| baseline (4 ganhos per-curva) | 4 | **2/6** | **0,3220** |
| melhor célula compartilhada (1,8; 1,0) | 2 | 2/6 | 0,5925 |

**Nenhuma** célula passa de 2/6, e a melhor tem soma de MAE **84 % maior**. Os
ganhos per-especime não são substituíveis por constante compartilhada — eles
carregam informação real do dado.

## O que fica, e como isto muda o pedido da P-13

O ganho codifica a **velocidade** corretamente; o que falta é o **arresto
acompanhar a velocidade**. Os espécimes rápidos passam do platô: `rep1` (N50=86)
termina em 0,061 onde o dado diz 0,187, enquanto `rep6` (N50=205) acerta sozinho.

⇒ a P-13 deixa de ser *"falta a lei do platô"* e passa a ser:

> **a lei do platô existe (`self_locking_gate` + `arrest_approach_exp`), está
> desligada por default, e fecha 3 curvas com um valor — mas o expoente precisa
> depender da taxa de afrouxamento do espécime, e hoje é constante.**

Isso é um pedido muito mais preciso, e barato de testar.

⚠️ **A dependência sugerida NÃO está estabelecida.** Os melhores expoentes por
curva são 2,0 (`rep1`, gain 2,2) · **3,0** (`rep4`, gain 1,8) · 2,0 (`rep5`,
gain 1,6) · 1,0 (`rep6`, gain 1,4) — sugestivo nas pontas e **não-monotônico no
meio**. A `rep4` é o contraexemplo, e o ótimo dela é fracamente determinado
(melhora 0,0783→0,0652 e nunca fecha). Quatro pontos com dois graus de liberdade
não sustentam uma lei; sustentam uma **hipótese nomeada**.

---

# ⛔ ADENDO QUE ENCERRA A LINHA: a população é SCATTER-LIMITED

A hipótese acima **não deve ser perseguida**, e o motivo é medido, não
argumentado.

## O piso de réplica do BAUER, medido nos dois grupos

Antes de propor que o expoente varie, perguntei quanto as próprias réplicas
discordam entre si. As 6 curvas da `fig6` são réplicas da **mesma condição
nominal** (M8, 0,07 mm), e as 3 da `fig8` também (M12, 0,08 mm):

| grupo | pares | **MAE mediano entre réplicas** | barra FORTE (`piso/√2`) |
|---|---:|---:|---:|
| `fig6` | 15 | **0,1065** | **0,0753** |
| `fig8` | 3 | **0,0837** | **0,0592** |

E o erro do modelo:

| curva | MAE do modelo | vs barra FORTE |
|---|---:|---|
| `fig6_rep1` | 0,0431 | **abaixo** |
| `fig6_rep2` | 0,0420 | **abaixo** |
| `fig6_rep3` | 0,0336 | **abaixo** |
| `fig6_rep4` | 0,0783 | 4 % acima |
| `fig6_rep5` | 0,0494 | **abaixo** |
| `fig6_rep6` | 0,0757 | 0,5 % acima |
| `fig8_test2` | 0,0290 | **abaixo** |
| `fig8_test3` | 0,0241 | **abaixo** |

⇒ **o modelo concorda com cada réplica melhor do que as réplicas concordam entre
si**, em 6 das 8; as outras 2 estão *na* barra (4 % e 0,5 %).

## O que isso faz com o resultado de cima

A `rep1` indo de 0,0431 para **0,0152** é um movimento de **0,028** numa família
cujas réplicas diferem por **0,107** — quatro vezes menor que o ruído do próprio
dado. **É ajuste de ruído, não medição de física.**

E explica, de uma vez, **por que todo parâmetro compartilhado reprovou no G2**
(o expoente **e** o piso, testados separadamente, ajudam `rep1`/`rep5` e
prejudicam `rep2`/`rep6`): está-se pedindo a uma constante que reproduza
**dispersão espécime-a-espécime**, que por definição não é função de nenhum
input do modelo.

Varredura do piso compartilhado, para registro (ganhos per-espécime
preservados):

| `loose_arrest_floor` | tripé | soma de MAE | G2 |
|---:|---:|---:|---|
| 0,05 (vigente) | 2/6 | 0,3220 | — |
| **0,08** | **3/6** | **0,3039** | ❌ `rep2` +0,0131 · `rep6` +0,0182 |
| 0,10 | 3/6 | 0,3149 | ❌ pior |

## Veredicto final sobre `arrest_approach_exp`

| população | piso | o expoente… |
|---|---:|---|
| IJPEM · ROUSSEAU aço · SUN · ECCLES | **0** | **inerte por construção** (early-return) |
| ROUSSEAU HDPE | 0,2 | **live, e PIORA** monotonicamente (0,0927 → 0,2638) |
| BAUER fig6 + fig8 | 0,05 / 0,08 | live, "melhora" — **abaixo do piso de réplica** |

⇒ **a constante não é calibrável nesta biblioteca.** Não porque esteja errada:
porque a única população que a lê não tem sinal acima do próprio ruído, e as
populações que a P-13 mira ou não a leem ou respondem ao contrário.

## O que isto deixa para a P-13 — que é o valor real desta passada

A P-13 fica **de pé**, e ganha uma eliminação que ela não tinha:

> a lei do platô **existe** (`self_locking_gate` com ponto fixo em `F_min`), e o
> `arrest_approach_exp` **não é** a resposta da P-13 — ele é inerte nas fontes
> dela com piso 0 e piora a única com piso > 0.

E ganha um **critério de admissibilidade** que faltava: qualquer candidato futuro
à P-13 deve ser medido **contra o piso de réplica da fonte**, porque o BAUER
mostrou que uma família inteira pode "fechar curvas" sem que nada tenha sido
medido.

⚠️ **Consequência retroativa favorável:** as **4 exceções F5 assinadas** na
`fig6` (`rep1`, `rep4`, `rep5`, `rep6`) e as **2** na `fig8` argumentam
*scatter*. Esta medição as confirma **com número** — piso 0,1065 / 0,0837 contra
erros de modelo de 0,024–0,078.

## Reprodutibilidade

```bash
py -3.12 New_Theory/arrest_exp_premeasure.py     # 8 curvas x 5 expoentes
py -3.12 New_Theory/bauer_fig6_parcimonia.py     # grade 6x5 compartilhada
```

O piso de réplica e a varredura de piso estão no scratchpad, recomputáveis em
minutos com `itertools.combinations` sobre os `metric_data` do store.
