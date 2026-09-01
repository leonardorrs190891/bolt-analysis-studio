# `indecidivel_sem_piso`: **15 de 15 legítimas** — a camada sobrevive à auditoria

**2026-08-15 (madrugada)** · só-leitura · **nada reclassificado** · store `85e8104420b0`,
censo **141/205**. Resultado **NULO** na camada, e um erro meu que vale o registro.

---

## 1. A premissa

A regra é `if piso is None: return "indecidivel_sem_piso"` — **função pura da fonte não ter
família de piso**. Isso colapsa duas situações epistemicamente diferentes:

* **(a)** o **experimento** nunca repetiu a condição ⇒ genuinamente indecidível; afirmação
  sobre o mundo;
* **(b)** a **réplica existe** e o nosso **pareamento** foi bloqueado (ex.
  `_SEM_FAMILIA_MECANICA`, quando a chave é cega a uma variável) ⇒ decidível em princípio,
  e o obstáculo é o nosso **instrumento**.

O motivo de suspeitar: a composição desta camada **mudou depois** da auditoria de 07/08-08 —
o bloqueio G+H de 2026-08-14 empurrou **5 curvas do `ICMEZ`** para dentro dela, por **herança
de bloqueio da fonte**, sem verificação individual. É o mesmo padrão que a `classe_parada`
exibiu na rodada anterior (3 de 8 sem a assinatura da classe).

## 2. ✅ Medido: **15 de 15 são (a)**

Para cada membro, agrupei **todas** as curvas da sua fonte por condição nominal e perguntei
se a dela se repete:

| fonte | membros | condição repetida na fonte? |
|---|---:|---|
| `YANG_2023_IJPEM` | 4 | não — a fonte **nunca** repete condição |
| `ICMEZ_2025` | 5 | não |
| `ROUSSEAU_2025` | 4 | não |
| `SUN_2025_CRIMP` | 2 | (falso positivo da sonda — §3) |

**A camada está correta nas 15.** Inclusive nas 5 do `ICMEZ`: o bloqueio invalidou o
pareamento **e** a fonte de fato não repete condição — as 8 curvas dela são 8 combinações
distintas de (δ, F₀, grip).

⇒ **null honesto**: a suspeita era razoável, a medição não a sustenta, e a camada fica.

## 3. ⚠️ A minha sonda cometeu **o defeito que estava auditando**

Ela marcou 2 curvas do `SUN_2025_CRIMP` como "(b) réplica existe". **Falso.** A tupla de
condição que escrevi era `(δ, F_amp, grip, rz, mode)` e **omitia lubrificação e o tratamento
crimp** — que são as variáveis que aquele experimento varre. As quatro curvas
`grease_crimp` · `grease_standard` · `nogrease_crimp` · `nogrease_standard` são um
**fatorial 2×2**, não réplicas.

**Construí uma chave cega às variáveis distintivas enquanto auditava uma chave cega ao
`grip_mm`.** A diferença é que aqui os **nomes** carregavam a distinção em texto claro, e
bastou lê-los.

## 4. ⚠️ E uma segunda inferência minha, também corrigida pela medição

Vendo `config_used` idêntico nas quatro (δ, F_amp, µ iguais), inferi *"nenhuma chave de
config pode distingui-las ⇒ o modelo deve prevê-las igualmente"*. **Medido: o modelo
separa** — razão `d_mod/d_dado` de **1,01 a 2,46**, todas ≥ 1.

Eu inferi de um **resumo impresso**; o resumo não continha tudo.

**Por onde a distinção chega:** `per_case` com tokens `_grease_crimp` / `nogrease_crimp`,
carregando constantes próprias (`tr_loose_gain` **2,44** vs **0,6**; `k_wear_spec`
**1,5e-15** vs **2,5e-14**; `emb_um` 1,1; `loose_arrest_floor` 0,142).

✅ E o **underscore inicial** em `_grease_*` é a guarda contra a armadilha que o `CLAUDE.md`
documenta — *"tokens casam por SUBSTRING: `grease` casa `nogrease`!"*. Alguém já tropeçou
nisto aqui e consertou.

## 5. O que o desvio entregou para o **item D**

O `SUN_2025_CRIMP` separa o seu fatorial 2×2 porque **cada célula tem as suas constantes
fitadas** — 4 condições, ~2–3 constantes cada. É exatamente a tensão que o item **D** nomeia
(*"calibrar N `per_case` — DOF vs ganho, o oposto da parcimônia"*), aqui com um caso
concreto e já **executado** em outra fonte.

⚠️ Leitura honesta nos dois sentidos: o modelo **acompanha** o dado nessa fonte (razão ≥ 1),
mas o mérito é de constantes por célula, não de física que atravesse as células. É o mesmo
que o painel do item **L** mede — e ali o `SUN_2025_CRIMP` aparece em **0,846**, entre as
melhores.

## Reprodutibilidade

`audit_indecidiveis.py` no scratchpad (~15 s, só-leitura). Usa o classificador **canônico**
(`T.classificar`) para achar os membros. ⚠️ A sua tupla de condição **não** deve ser reusada
sem acrescentar as variáveis de tratamento — ver §3.
