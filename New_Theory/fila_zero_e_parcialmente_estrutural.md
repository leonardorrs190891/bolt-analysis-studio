# *"Fila form-limited ZERO"* é **parcialmente estrutural** — 55 de 205 curvas não podem receber o rótulo

**2026-08-15 (20:xx)** · só-leitura · **nada reclassificado** · store `20be19aabe11`, censo
**143/205**, fora **62**.

Reconcilia duas medições independentes do mesmo dia — a minha das 17:xx
(`indecidivel_e_propriedade_da_literatura.md`) e a da **sessão B** da noite
(`icmez_arresto_sub_piso_resultado.md`, commit `b434c35`).

---

## 1. Havia aparência de conflito, e não há

O cabeçalho da mesa, com o item **Q**, diz que as 5 abertas do `ICMEZ_2025` são
*"form-limited com forma nomeada, **não indecidíveis**"*. Eu havia medido, horas antes, que
elas estão em `indecidivel_sem_piso` por **pareamento bloqueado**.

**As duas coisas são verdadeiras, porque são perguntas diferentes:**

| pergunta | resposta | medição |
|---|---|---|
| dá para **desculpá-las** contra a dispersão do próprio dado? | **não** — fatorial 2×2×2, zero réplicas | minha, 17:xx |
| sabemos **o que está errado**? | **sim** — o modelo trava no `loose_arrest_floor` e o dado atravessa | sessão B, noite |

⇒ a única frase que excede é *"não indecidíveis"*: elas **são** `indecidivel_sem_piso` (e
corretamente) **e** têm forma nomeada. O documento da sessão B, aliás, já diz isso com
precisão — *"'sem piso' **não** é 'sem defeito diagnosticável'"*.

## 2. Verifiquei a medição da sessão B, e ela se sustenta

| checagem | resultado |
|---|---|
| `loose_arrest_floor` adotado no `ICMEZ_2025` | **0,308**, e chega à curva como override efetivo |
| o modelo achata? | sim: **0,3053 → 0,2965 → 0,2918** enquanto o dado vai 0,3041 → 0,2596 → **0,2280** |
| a camada canônica mudou? | **não** — as 5 seguem `indecidivel_sem_piso` |

## 3. ⚠️ O que a reconciliação expõe: a ORDEM do classificador

```
excecao → declarada → classe_parada → n<6 → colapso → PISO IS NONE → form_limited
```

`indecidivel_sem_piso` **precede** `form_limited`. Logo **curva de fonte sem piso NUNCA pode
ser rotulada `form_limited`** — tenha ela defeito diagnosticável ou não.

**Quem barra cada uma das 62 fora:**

| ramo | curvas |
|---|---:|
| exceção assinada | 23 |
| declarada | 18 |
| fonte em `classe_parada` | 6 |
| **fonte SEM PISO** | **14** |
| colapso métrico | 1 |

E o alcance é maior que as fora: **55 das 205** curvas estão em fontes sem piso medido —
barradas **por construção**, passem ou não. As 10 fontes: `ICMEZ_2025`, `JCSR_2023`,
`LI_2022_MARSTRUC`, `QIN_2024`, `ROUSSEAU_2025`, `SUN_2025_CRIMP`, `YANG_2019`,
`YANG_2023_AME`, `YANG_2023_IJPEM`, `ZHANG_2006`.

## 4. A leitura honesta do número publicado

**`form_limited = 0` não é falso.** É uma afirmação correta sobre o **rótulo**, e o rótulo é
uma **conjunção**:

> não desculpável **e** não explicável por métrica/escopo **e** a fonte tem piso medido

O que engana é lê-lo como *"não há trabalho"*. A sessão B exibiu **5 curvas** que satisfazem
*"há trabalho, com forma nomeada e rota"* e que **nunca** poderiam receber o rótulo — porque
o `ICMEZ_2025` não tem piso.

⇒ **uma curva pode ser trabalho sem ser rotulada trabalho.**

⚠️ E o mecanismo é o **mesmo** que eu medi às 17:xx por outro caminho: 11 das 14 curvas de
`indecidivel_sem_piso` estão lá por **pareamento bloqueado**, não por ausência de dado. Ou
seja, **a mesma decisão de rigor** (bloquear pareamento falso) que protege o censo de pisos
inflados é a que **esvazia a fila** — não porque o trabalho sumiu, mas porque o rótulo exige
um piso que a literatura não publicou.

## 5. O que isto NÃO é

Não é proposta de mudar o classificador: a ordem está **certa** (não faz sentido chamar de
"fila de forma" uma curva que talvez esteja dentro da dispersão do próprio dado — só que não
dá para saber). Não é crítica à sessão B, cuja medição eu **verifiquei e confirmei**. E não é
correção de número: **nenhum** número publicado está errado.

É uma afirmação sobre **como o número deve ser lido**, agora com o mecanismo medido de duas
direções independentes.

## 6. Proposta (exige assinatura — é semântica de camada)

Publicar a fila em **duas linhas** em vez de uma:

| leitura | hoje |
|---|---:|
| `form_limited` (rótulo do classificador) | **0** |
| **curvas fora, sem estatuto assinado, com forma nomeada** | **≥ 5** (as do `ICMEZ_2025`) |

O *"≥"* é honesto: ninguém perguntou às outras 16 abertas se têm forma nomeada. Foi
exatamente essa pergunta que a sessão B fez ao `ICMEZ_2025` e que produziu o item **Q**.

## Reprodutibilidade

Sondas inline no corpo do commit; usam `T.classificar`, `T.piso_da_fonte`, `rh.limite_sres`,
`rh.sres_para_censo`, `kb.adopted_config` e `rn._effective_overrides` — nenhuma reimplementa
regra. A ordem dos ramos foi lida do código-fonte de `T.classificar`, não suposta.
