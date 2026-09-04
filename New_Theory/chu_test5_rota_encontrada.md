# `chu…test5`: rota **encontrada e medida** — e por que ela ainda não foi adotada

**2026-08-14** · só-leitura · **nada adotado** · store `cb019d75c6c2`, censo **140/205** ·
pedido do professor: *"esse resultado ainda deve ser melhorado para o tripé"*.

## O alvo

`chu2026ti_D1p0mm_F0_49kN_test5` — MAE **0,040** ✓ · res.máx **0,088** ✓ · σ **0,044** ✗
(limite 0,0296 = piso da família legítima `test5`×`test6_repeat`). **Uma perna só.**

Dois fatos que tornam o alvo crível antes de qualquer sonda:

* **ρ(resíduo, N) = +0,94** ⇒ defeito de **TAXA**, não de nível — o erro se acumula;
* **a réplica dela PASSA** (`test6_repeat`, σ 0,0285). Mesmo rig, mesma condição, mesmo
  comportamento: o alvo é **comprovadamente alcançável** nesta condição.

## ⛔ Rota 1 — corrigir a rugosidade (item B): **FALSIFICADA**

O artigo dá **Ra 0,4/1,6 µm** e o config usa `RZ_DEFAULT = Rz10-40`, a classe **mais
rugosa**. Como o diagnóstico dizia *"perde rápido demais cedo"* e embedding é o canal cedo, a
previsão era: menos rugosidade → menos assentamento → conserta.

**Controle 9/9 bit-idêntico. Resultado, oposto à previsão:**

| cenário | `test5` σ | tripé CHU |
|---|---:|---:|
| nominal | 0,0436 | 2/9 |
| `Rz<10` em todas | 0,0455 | 2/9 |
| **`Rz<4` em todas** | **0,0546** | **1/9** ⚠️ derruba a `test6_repeat` |

**Por que eu errei o sinal:** o resíduo vai de **−0,042 cedo** a **+0,088 tarde** — o modelo
perde **demais cedo E de menos tarde**. Reduzir assentamento conserta a ponta cedo e **piora
a tarde**, que é a maior. O σ mede o **espalhamento**, então ele **abre**.

⇒ **isto também é resultado sobre o item B**: corrigir a rugosidade sozinha **piora** o CHU
(2/9 → 1/9). A célula de custo que eu marquei como vencida está agora medida — e o sinal é o
contrário do que "corrigir o input" sugere.

## ✅ Rota 2 — varredura CONJUNTA nível×forma do embedding: **FECHA**

O `ataque_curva.py` escolheu o canal por **fatia tardia** (wear 93 %) e **pulou** a conjunta;
mas o próprio diagnóstico diz que o erro **se forma cedo**, onde manda o embedding. Varri o
par acoplado `emb_depth` (nível) × `N_emb` (relógio), que é a lição da **D-AA**.

Grade (σ / MAE; `*` = fecha as 3 pernas):

| `emb_depth` | N=50 | N=100 | N=200 | N=400 | N=800 |
|---|---|---|---|---|---|
| 3,0e-05 | 0,0422 | 0,0252 | **0,0098\*** | **0,0183\*** | 0,0349 |
| 4,5e-05 | 0,0644 | 0,0525 | 0,0330 | **0,0072\*** | **0,0224\*** |
| 6,0e-05 | 0,0925 | 0,0844 | 0,0621 | 0,0260 | **0,0107\*** |
| 9,0e-05 | 0,1518 | 0,1491 | 0,1203 | 0,0676 | **0,0185\*** |

**Região, não fio de navalha** — 6 células fecham, com crista clara (mais nível ⇒ mais
relógio), que é a assinatura do acoplamento.

## ⚠️ O gate de fonte — e o falso negativo que quase me enganou

**v1 do gate reprovou tudo** (tripé 1/9, 7 curvas piorando, a `test1` indo de MAE 0,0035 a
**0,3564**). Eu quase escrevi "sem rota".

**A v1 era injusta:** a `test1` é a **única** curva do CHU com config adotada (PR-38), e ela
fixa `emb_um = 1,6 µm`. Uma adoção **de grupo** não a tocaria — mas minha sonda injetou
`emb_depth` **downstream**, sobrescrevendo o valor adotado dela. Corrigido isso:

| célula | tripé | curvas que **saem** | `test5` | `test6_repeat` |
|---|---:|---|---|---|
| **`emb_depth` 30 µm + `N_emb` 400** | **3/9** | **nenhuma** | ✅ 0,0208/0,0395/**0,0183** | ✅ 0,0279/0,0422/**0,0122** |
| `emb` 45 µm + `N_emb` 400 | 2/9 | `test6_repeat` | ✅ | ✗ |
| só `N_emb` 400 (1 número) | 2/9 | nenhuma | ✗ 0,0449 | ✅ |

⇒ **a célula boa ganha +1 no censo, não derruba ninguém, preserva a `test1` e leva as DUAS
curvas do par de réplica ao tripé.** (4 curvas pioram >0,01 no MAE, todas já reprovadas com
folga — 0,10–0,16 — logo cosmético.)

## ⚠️ Por que NÃO adotei ainda

**Um sinal que exige o seu julgamento, não o meu.** As duas constantes, **isoladas**, não
ajudam — e uma delas **piora**:

| dose | `test5` σ |
|---|---:|
| nominal | 0,0436 |
| **só** `N_emb` = 400 | **0,0449** ⚠️ pior |
| **só** `N_emb` = 200 | 0,0385 |
| `emb_depth` 30 µm **+** `N_emb` 400 | **0,0183** |

Só a **combinação** funciona. Isso é exatamente o que **acoplamento nível×forma** produz — e
é exatamente o que **compensação entre parâmetros** também produz. **As duas leituras dão o
mesmo gráfico**, e separá-las exige âncora física.

**E a âncora não existe:** o `emb_depth` = 30 µm é o **default do engine** (calibrado para o
rig **âncora interna M16**), enquanto o efetivo do CHU hoje vem da tabela VDI por `Rz10-40`. Adotar 30 µm
significa dizer que este parafuso **MJ10 aeroespacial de superliga**, de superfície fina,
assenta **~4× mais** que a tabela dá para uma superfície rugosa — e assenta **8× mais devagar**
(`N_emb` 50 → 400). Não tenho nada no artigo que sustente isso.

⇒ classe honesta: **`fitado-this-rig`, 2 números, numa fonte onde 3 de 9 passariam**.

## O que está na sua mesa

1. **Adotar** (você já assinou em bloco): +1 censo, 0 perdas, `test5` **e** `test6_repeat` no
   tripé, ao custo de 2 constantes sem procedência e com assinatura de compensação;
2. **Recusar por parcimônia** e manter a `test5` fora — a rota fica registrada e medida;
3. **Buscar a âncora** — o que o paper diz sobre acabamento e pré-carga de assentamento do
   MJ10; se houver `f_Z` medido, o par deixa de ser fit.

Não executei a (1) por conta própria porque a assinatura em bloco cobre **decisão**, e o que
está em jogo aqui é **procedência** — a campanha inteira se apoia em não confundir as duas.
Ela leva ~40 min (prereg + re-stamp + suíte) e está pronta para disparar.

## Reprodutibilidade

`chu_rz2.py` (rugosidade, patch em `_loading_for` — patchear `inputs_for` é **no-op**,
armadilha já registrada), `chu_joint.py` (conjunta 4×5) e `chu_fonte2.py` (gate de fonte
justo) no scratchpad. Controle bit-idêntico em todos. ~25 min.
