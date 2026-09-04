# Matriz de procedência por constante — o número da Fase 2

> **2026-07-28.** Só-leitura sobre o bloco `shared` canônico de
> `joint_calibrations.json` (fit de 2026-07-04) e a maquinaria de
> procedência do `knowledge_base`. Nenhuma simulação, fit, adoção ou
> escrita. Script: `New_Theory/provenance_matrix.py`; números:
> `provenance_matrix.json`.

> **Escopo:** as constantes **compartilhadas** — as que a tese "uma
> física, N estados" põe em jogo. Os configs adotados per-rig ficam fora
> de propósito (são por-rig por construção, e o `adopted_configs.json`
> estava em escrita por outra sessão quando isto rodou).

---

## 1. O número

O canônico usa **10 constantes compartilhadas**. Por classe de
procedência:

| classe | n | o que a move |
|---|--:|---|
| `BANDA_FORA` | 2 | re-ancorar, ou **separar a constante** |
| `SEM_PROCEDENCIA` | 2 | medir, ou anular a constante |
| `ANCORA_POR_PAR` | 1 | nada p/ o par usado; generalizar exige medir o par novo |
| `FIT_SEM_ANCORA` | 1 | é a dívida mais cara |
| `BANDA_DENTRO` | 1 | nada — está provado |
| `INPUT_POR_JUNTA` | 1 | nada — é input de tabela, por decisão |
| `FIXO_POR_DECISAO` | 1 | reabrir a decisão |
| `DIRECAO` | 1 | medir a magnitude |

**Leitura honesta, e o título não é o "quantas têm":** só
**3 das 10** estão em situação que dispensa trabalho
(banda medida com o valor dentro · input de tabela · fixo por decisão
declarada). **2** não têm procedência nenhuma
registrada. **1** é fitada ao dataset **sem
âncora** — o `W_conf_ref`, cuja caça a âncora **falhou por null decisivo**
em 2026-07-04 (§4.9).

**O achado é a linha `BANDA_FORA`: 2 constantes têm
banda MEDIDA e o valor canônico está FORA dela** — `N_emb` e `k_wear_spec`.
Isso é pior que não ter âncora: a medição existe, e o canônico a
contradiz. As duas estão detalhadas nos §3 e §4 — e das duas, **só a do
`k_wear_spec` é nova**; a do `N_emb` já estava registrada como *"não
reconciliada"* e aqui foi **reproduzida por rota independente**.

## 2. A matriz

| constante | valor | classe | fitada | por quê |
|---|--:|---|:--:|---|
| `C_creep` | 1.86673e-11 | **ANCORA_POR_PAR** | sim | âncora POR PAR (sec4.7 + denotter): 4 pares; o canônico É o par da âncora interna |
| `N_emb` | 50 | **BANDA_FORA** | — | banda medida [3, 15] (faixa per-rig LIDA do dado); valor FORA, 3.33x ACIMA do teto |
| `W_conf_ref` | 7671.21 | **FIT_SEM_ANCORA** | sim | está em free_constants e não tem banda nem âncora |
| `c_D` | 2 | **SEM_PROCEDENCIA** | — | nenhuma banda, âncora ou decisão registrada no KB |
| `conform_pressure_exp` | 2 | **BANDA_DENTRO** | — | banda medida [1.48, 2] (liu2021_noload_vs_preload); valor dentro |
| `emb_depth` | 3e-05 | **INPUT_POR_JUNTA** | — | o KB marca verdict='input' (por classe Rz (Bolt Science Rz<4 fino)) — tabela por junta, não constante universal |
| `k_dmg_wear` | 4 | **SEM_PROCEDENCIA** | — | nenhuma banda, âncora ou decisão registrada no KB |
| `k_wear_spec` | 5e-14 | **BANDA_FORA** | — | FORA de TODAS as bandas comparáveis (1/Pa) — thread\|35CrMo-SCM435 [4e-15,2e-14]: 2.5x ACIMA · faying\|Q355B-Q235B [6.49e-12,7e-12]: 130x abaixo. O valor cai no VÃO entre elas; nenhum valor único pode satisfazer as duas (L6) |
| `p_ref_conform` | 5e+08 | **FIXO_POR_DECISAO** | — | n=2 / p_ref=5e8 declarados FIXOS no bloco shared (rev. 2026-07-04) |
| `tr_loose_gain` | 2 | **DIRECAO** | — | âncora confirma a direção, não a magnitude (eccles2010_torque_residual) |

---

## 3. `k_wear_spec`: o valor canônico cai no VÃO entre duas bandas

Este é o caso que a matriz existe para achar, e ele estava documentado
errado. O registro de 2026-07-28
(`l7_removal_energy_diagnostic_2026-07-28.md` e o Manual) diz que a R5
tem **"única banda MEDIDA"** e que o canônico está **~130× abaixo**
dela. Medido: a R5 tem **3** bandas, e a comparação depende da
**unidade**.

| interface\|par | banda | unidade | comparável? | canônico 5e-14 |
|---|---|---|:--:|---|
| `faying|Q355B-Q235B` | [6.49e-12, 7e-12] | 1/Pa | sim | abaixo do piso (129.8×) |
| `fretting|52100-52100` | [3.2e-05, 0.00024] | norm-own | **NÃO** | — |
| `thread|35CrMo-SCM435` | [4e-15, 2e-14] | 1/Pa | sim | ACIMA do teto (2.5×) |

**Três correções ao que está escrito:**

1. **Não é "única banda": são 3.**
2. **`fretting|52100-52100` NÃO é comparável** — está em `norm-own` (a
   normalização do próprio paper), não em `1/Pa`. Compará-la ao canônico
   é erro de unidade, e é o que produziria o "×6e8" que aparece se a
   conta for feita sem olhar a unidade.
3. **A banda mais próxima não é a `faying` — é a `thread`**, e o canônico
   está **ACIMA** do teto dela, não abaixo do piso. Ou seja: a direção do
   argumento **inverte** conforme a interface.

**E o que sobra é mais forte que o erro.** As duas bandas comparáveis
**cercam o canônico pelos dois lados**:

    thread|35CrMo-SCM435: teto 2e-14
      <  canônico k_wear_spec = 5e-14  <
    faying|Q355B-Q235B: piso 6.49e-12

As duas bandas medidas distam **324×** entre si. O engine usa
`k_wear_spec` nos **dois** canais — `WearLoss` (faying/apoio) **e**
`ThreadFrettingLoss` (rosca) — então **nenhum valor único pode estar
dentro das duas**. Isso não é um valor a corrigir: é a **L6**
(não-universalidade de K/H por par) em números exatos, e é argumento
para **separar a constante por interface**, não para movê-la.

---

## 4. `N_emb` = 50 contra a faixa lida [3, 15]

> **Não é achado novo, e a correção é minha:** o §5 do relatório executivo
> do Manual já registra esta divergência como *"registrada e não
> reconciliada"*. Esta varredura a **reproduziu por rota independente**
> (leitura do prior + comparação com o canônico), o que vale como
> confirmação. O que é novo aqui são as **duas leituras** abaixo.

O prior `N_emb` do KB não é uma banda de literatura: é a **faixa dos
valores per-rig LIDOS** do próprio dado, com a nota
*"timing lido: ~metade do assentamento em 10-20 ciclos"*. A faixa é **[3, 15]** e o canônico
compartilhado é **50** — **3.3×
acima do topo**.

**O que isso é, e o que não é.** Não é erro aritmético nem valor
inventado: `N_emb` é a constante de tempo do assentamento, e o valor 50
saiu do fit compartilhado na escala da âncora interna. A faixa [3, 15] saiu de ler o
**tempo de joelho** curva a curva. As duas coisas medem o mesmo relógio e
discordam por 3×. Duas leituras possíveis, e a varredura não decide entre
elas:

1. a faixa lida é **per-rig** e o canônico é uma média que nenhum rig
   individual exibe (mesma classe do `W_conf_ref` per-par);
2. o `N_emb` canônico está absorvendo atraso que pertence a outro
   mecanismo — e há candidato nomeado na fila: **incubação do
   assentamento** (item 8, âncora interna: *"dado plano até N≈38 e o modelo assenta
   desde o ciclo 1"*), que é exatamente um atraso que hoje não existe no
   engine.

A leitura (2) é a que vale checar primeiro, porque uma constante de tempo
inflada é **como** um modelo sem incubação compra um platô inicial.

---

## 5. Dois achados de instrumentação

**(a) `check_input` roda em 1 das 10.** Só
`['F_amp_ratio', 'conform_pressure_exp', 'fat_sigma_endurance', 'k_wear_spec', 'mu_bearing', 'mu_dry', 'mu_thread']` têm guarda, e dessas apenas
**`k_wear_spec` e `conform_pressure_exp`** são constantes do bloco
`shared`. As outras 8 passam sem verificação nenhuma — e o contrato da
função devolve `None` tanto para "dentro da banda" quanto para "não sei
checar", ambiguidade que a própria docstring registra desde 07-28. A
consequência prática: **um valor fora de banda numa das 8 não dispara
nada.**

**(b) O único aviso que dispara é o do nosso próprio canônico.**
`check_input("k_wear_spec", 5e-14)` devolve:

```
k_wear_spec=5e-14 fora de TODAS as bandas medidas R5 (1/Pa) — faying|Q355B-Q235B: [6.49e-12, 7e-12] (Li 2025 EngStruct 10.1016/j.engstruct.2025.121158); thread|35CrMo-SCM435: [4e-15, 2e-14] (Zhang 2019 EFA 10.1016/j.engfailanal.2019.05.001)
```
O aviso cita a banda `faying` — a mais **distante** das duas comparáveis.
Pelo §3, o número que ele deveria citar depende do canal que domina a
perda naquele caso, e hoje ele cita um só.

---

## 6. O que isto propõe (nada adotado)

1. **`k_wear_spec` por interface** (`k_wear_spec_faying` /
   `k_wear_spec_thread`), cada um com a sua banda medida. É a única
   mudança que pode pôr o modelo **dentro** de procedência medida no
   canal de desgaste. Custo: constante nova (forma, não valor) ⇒ prereg.
2. **Ampliar `checkable_inputs` às 8 sem guarda**, mesmo com banda vazia,
   para que a ausência de âncora seja **visível** em vez de silenciosa.
3. **`N_emb`: checar a leitura (2) do §4** — se a incubação do
   assentamento (fila item 8) explicar o atraso, o `N_emb` canônico deve
   voltar para a faixa lida. Diagnóstico só-leitura, sem prereg.
4. **`W_conf_ref` segue a dívida mais cara**: fitada, sem âncora, e com a
   caça registrada como null decisivo. Nada aqui muda isso.
5. **Corrigir os 3 pontos** que dizem "única banda medida / 130×":
   `l7_removal_energy_diagnostic_2026-07-28.md`, Manual
   `00-relatorio-executivo.md` e `03-aplicar-o-software.md`.

> **Escopo do que NÃO foi medido, dito de propósito:** as 10 são as
> **compartilhadas**. Os configs adotados per-rig têm dezenas de
> constantes a mais, e a mesma varredura sobre eles é trabalho aberto —
> não foi feita aqui porque o arquivo estava em escrita por outra sessão.

