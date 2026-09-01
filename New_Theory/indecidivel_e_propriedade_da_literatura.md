# `indecidivel_sem_piso` não é lacuna de escrituração — é **fatorial sem réplica** no artigo

**2026-08-15 (17:xx)** · só-leitura · **nada reclassificado** · store `20be19aabe11`, censo
**143/205**, fora **62**, fila form-limited **0**.

---

## 1. A premissa que ninguém tinha testado

`indecidivel_sem_piso` é a **maior** das camadas de estatuto "brando" — **14** das 21 curvas
que estão fora sem assinatura. O nome diz *"não há piso medido para esta fonte"*, e lê-se
naturalmente como **falta de dado**.

⚠️ **`piso = None` tem duas causas, e a camada trata as duas igual:**

1. **ausência genuína** — a fonte não tem nenhum par candidato a réplica;
2. **pareamento BLOQUEADO** — o par existe e a campanha decidiu que **não é réplica**, porque
   as duas curvas diferem numa **variável varrida**.

## 2. Medido nas 14: **11 bloqueadas, 3 ausência genuína**

| curva | fonte | causa |
|---|---|---|
| `demir2024_*` ×5 | `ICMEZ_2025` | ⛔ grip **13,8 ≠ 19,8 mm** — rigidez varrida |
| `rousseau2025_hdpe_t10` · `_t12` | `ROUSSEAU_2025` | ⛔ espessura ≠ (chave cega) |
| `rousseau2025_steel_t10` | `ROUSSEAU_2025` | ⛔ **t=10 ≠ t=12 mm** — espessura *é* a variável |
| `rousseau2025_steel_t10_amp0p2` | `ROUSSEAU_2025` | ⛔ material ≠ (aço × HDPE) |
| `sun2025…grease_crimp` · `…grease_standard` | `SUN_2025_CRIMP` | ⛔ tipo de porca ≠ **e** lubrificação ≠ |
| `10_Yang_2023_…_0,30/0,35/0,50 mm` ×3 | `YANG_2023_IJPEM` | ausência genuína |

⇒ **para 11 de 14, o dado EXISTE.** O que não existe é a **réplica** — o artigo varreu
parâmetros em vez de repetir condição.

## 3. O mesmo padrão no corpus inteiro

| | fontes |
|---|---:|
| **com** piso medido | **16** de 27 |
| **sem** piso, por **pareamento bloqueado** (todo par candidato caiu) | **7** |
| **sem** piso, sem par candidato nenhum | **4** |

Chaves bloqueadas acumuladas: **81 case_ids**.

⚠️ **"Bloqueado" NÃO implica "sem piso"** — e a tabela força a distinção: `CACCESE_2009` tem
as **7** curvas bloqueadas e **mesmo assim tem piso** (0,0100), porque o par válido é outro
(`rep1↔rep2`, mesma condição). O `LIU_2016` idem (14 bloqueadas, piso 0,0024). Os **7** são as
fontes onde **todo** par candidato caiu.

## 4. Por que isto reenquadra a camada

O rótulo sugere pendência de bancada nossa. A medição diz outra coisa: **a razão dominante
pela qual não conseguimos julgar o modelo contra a repetibilidade do próprio dado é uma
propriedade do desenho experimental publicado** — 7 das 11 fontes sem piso rodaram **fatorial
sem replicação**, e os pares candidatos foram examinados e **corretamente rejeitados**.

E há confirmação histórica direta: a campanha registra **6 retratações por piso inválido**.
Cada uma foi um pareamento que **deveria** ter sido bloqueado e não estava. As 81 chaves de
hoje são a defesa acumulada contra exatamente esse erro — e este documento mostra que ela
**está mordendo**: 11 das 14 curvas da camada devem seu estatuto a ela.

⇒ **a camada não é dívida nossa; é o limite do que a literatura publicou.** Resolver essas 11
exige **réplica em condição repetida**, não análise.

## 5. O que NÃO estou afirmando

Não afirmo que as 11 estejam certas no modelo — elas estão **fora do tripé**. Afirmo que a
**pergunta** *"o erro do modelo é maior que a dispersão do próprio dado?"* é **inrespondível**
para elas com o que os artigos publicaram. São coisas diferentes, e confundi-las inflaria o
resolvido com fracasso.

Também não proponho reclassificar nada: a camada está **correta** como está. O que proponho é
que o **nome** e a **prosa** distingam as duas causas, porque hoje um leitor razoável entende
"falta medir" onde o certo é "o artigo não replicou".

## 6. ⚠️ Dois erros meus nesta mesma auditoria

1. **Inferi o nome da fonte pelo prefixo do `case_id`**: escrevi `DEMIR_2024`; a fonte é
   **`ICMEZ_2025`** (os case_ids é que são `demir2024_*`). Errata já commitada em `c5d3b18`.
2. **Procurei num dict de `case_id` usando nome de FONTE** e concluí *"as 4 fontes não estão
   bloqueadas"* — o oposto exato do verdadeiro (3 das 4 estão). O que denunciou foi olhar as
   chaves antes de aceitar o resultado: `_SEM_FAMILIA_MECANICA` tem **81** entradas e
   nenhuma casava, o que é forte demais para ser verdade.

⇒ os dois são a **mesma** falha: ler um identificador do lugar errado. É a classe que este
documento está justamente auditando nos pareamentos.

## Reprodutibilidade

Sondas inline no corpo do commit. Usam `T.classificar`, `T.piso_da_fonte`, `rh.limite_sres`,
`rh.sres_para_censo` e `rh._SEM_FAMILIA_MECANICA` — nenhuma reimplementa regra; a seleção das
`fora` replica o laço canônico de `regra_de_parada_triagem.main`.
