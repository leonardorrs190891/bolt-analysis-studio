# `LIU_2020_WEAR`: religar o desgaste devolve a resposta à amplitude — **e o gate congelado barra a versão que ganha censo**

**2026-08-14 (noite II)** · só-leitura · **NADA ADOTADO** · store `c37618c5cc96`, censo
**141/205** · sequela de `censo_cegueira_a_condicao_varrida.md`.

---

## 1. O defeito, re-lembrado em uma linha

A fonte varre a amplitude transversal **4×** (0,1→0,4 mm, P₀ fixo em 18 kN) e o modelo
devolve **0,9650 nas quatro**. Cobertura **0 %**. A causa está na config adotada, que zera
`K_archard`, `k_wear_spec`, `tr_loose_gain` **e** `C_creep`.

**Verificações de pré-requisito (regra dos companheiros e da classe mecânica):**

* modo = **deslocamento** ⇒ o wear **não** é inerte (só o é em modo axial-força);
* `delta_mm` varia corretamente 0,1/0,2/0,3/0,4 ⇒ a amplitude **chega** ao engine;
* classe mecânica das quatro: **GROSS** (`slip/δ` = 0,990–0,998).

⇒ o canal **pode** agir; o que o desliga é a constante.

## 2. ⚠️ A primeira grade saturou na BORDA INFERIOR — e a disciplina D-L inverteu o veredito

A grade inicial começou em `k_wear_spec` = 5e-15 (um décimo do canônico) e **já passava do
alvo**: modelo em 0,82/0,71/0,62/0,55 contra dado 0,99/0,96/0,93/0,83. Concluir *"o canal
de wear é forte demais"* ali teria sido concluir de uma grade que nunca tocou a região
certa.

Estendida para baixo (~7,7× menor, estimado pelo alvo), a região existe:

| `k_wear_spec` | tripé (7 zinco) | pior piora de MAE | `AF0,4` entra? | espalhamento do modelo |
|---:|---:|---:|:--:|---:|
| 0 (hoje) | 6/7 | — | não | **0,0000** |
| 8,0e-16 | 6/7 | **+0,0082** ✅ | não | 0,0544 |
| 1,0e-15 | 6/7 | +0,0103 | não | 0,0674 |
| **1,2e-15** | **7/7** | **+0,0125** ⚠️ | **SIM** | **0,0801** |
| 1,4e-15 | 4/7 | +0,0146 | não | 0,0927 |

(espalhamento do **dado** nas quatro: **0,1569**)

## 3. O par tribológico separa o grupo — e isso não é conveniência

As duas curvas `fig15` são **DLC**; as sete restantes, **zinco eletrolítico**. A regra da
campanha para constante tribológica é **por par** (§4.7, `C_creep`: âncora 304SS 9,9e-13
contra fit UFU 1,2e-11, ICs disjuntos). Aplicar um `k_wear_spec` comum a zinco e DLC seria
violar a própria disciplina.

Com o grupo **só zinco**, as 2 DLC ficam **bit-idênticas** e a lista de pioras encolhe de
três curvas acima da tolerância para **uma**.

## 4. ⛔ As duas opções, e por que eu não escolhi nenhuma

| | **A — k = 1,2e-15** | **B — k = 8,0e-16** |
|---|---|---|
| censo | **+1** (fonte 8/9 → **9/9**) | 0 (8/9) |
| conteúdo preditivo | 0 % → **~51 %** | 0 % → ~35 % |
| gates padrão | ⚠️ **REPROVA**: `fig9_AF0,2` piora **+0,0125** (25 % acima de +0,01) | ✅ **passa** (pior +0,0082) |
| curvas que saem | 0 | 0 |
| DLC | bit-idênticas | bit-idênticas |

**Nenhuma dose satisfaz as duas coisas.** Entre 1,0e-15 e 1,2e-15 o ganho aparece e a
tolerância já está estourada; abaixo disso a tolerância cabe e o ganho some.

### Por que não auto-autorizei a opção A

O precedente é literal (**D-AA**): *"a `plain_seawater` foi barrada pelo MEU PRÓPRIO gate —
regra e gate discordaram e o **gate congelado mandou**."* E a assinatura em bloco do
professor cobre adoções que **passam** os gates; ela não cobre **afrouxar** um gate — as
emendas de tolerância do `LU_2024` foram assinadas **em sessão, separadamente e por
escrito** ((b) e (b′) do prereg daquela adoção). Estourar +25 % de tolerância depois de ver
o resultado é mover a trave.

### Por que não auto-autorizei a opção B, que passa os gates

Porque ela **piora 6 das 7 curvas** (todas ≤ +0,0088) para ganhar conteúdo preditivo que
**nenhum gate mede**. Seria a **primeira vez** que a campanha troca métrica por conteúdo
preditivo, e isso é política do projeto, não decisão de sessão — do mesmo tipo que a
adoção do D-P por procedência com efeito nulo, que também foi decisão declarada e não
inferida.

## 5. ⚠️ O que este resultado diz sobre o ajuste original — e é a favor dele

O fit parcimonioso zerou o wear **porque zerá-lo melhora a métrica**: com `k = 0` a fonte
faz 8/9 com MAE 0,005–0,019. O fit não errou — ele otimizou o que lhe foi pedido.

O que este documento acrescenta é que **o alvo estava incompleto**: nenhuma métrica da
campanha pergunta se o modelo reproduz a *variação* que o experimento produziu, e por isso
"desligar o canal" e "o canal não existe" ficam indistinguíveis. É o item **L** da mesa
com um caso concreto e um preço em número.

## 6. Reprodutibilidade

`liu2020_wear_religado.py` no scratchpad (classe mecânica + grade grossa) e a grade fina
inline. Só-leitura, controle bit-idêntico nas DLC, ~25 min.
