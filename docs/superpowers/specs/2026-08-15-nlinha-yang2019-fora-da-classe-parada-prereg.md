# PREREG — item **N′**: remover `YANG_2019` de `_FONTES_CLASSE_PARADA`

**Data:** 2026-08-15 (21:4x) · **Autorização:** professor, *"assine e prossiga"* (21:42),
sobre as propostas N′ e P de `classe_parada_reauditada_pos_DAD.md` ·
**Store de partida:** `20be19aabe11`, censo **143/205**, `classe_parada` **6**,
`indecidivel_sem_piso` **14**, fila form-limited **0**.

⚠️ **Gates IMUTÁVEIS depois de escritos.**

---

## 1. O que se remove, e por quê

`YANG_2019` sai da lista `_FONTES_CLASSE_PARADA`. A camada afirma *"aceleração tardia —
classe encerrada, aguardando dado novo"*, e o discriminante da campanha é
`ρ(resíduo, N) ≥ +0,7` **ou** razão terminal `> 2`.

**Medido** (`classe_parada_reauditada_pos_DAD.md`): a fonte tem **1 membro** e ele **não
carrega a assinatura** —

| curva | ρ | razão terminal | assinatura |
|---|---:|---:|---|
| `yang2019_M10_amp0p4_5Hz` | **+0,39** | **0,70** | ⛔ **SEM** — e **invertida** (o erro se forma *cedo*) |

⇒ **falso positivo INTEIRO**: 1 membro, 0 com assinatura.

## 2. Precedente exato: a P-7

A **P-7** (assinada e executada em 2026-08-08) removeu `LU_2024` e `SUN_2025_CRIMP` da mesma
lista, pelo **mesmo discriminante**, com o mesmo diagnóstico — *"falsos positivos PUROS: 0
curvas com o defeito da classe e 2 com o defeito OPOSTO"*. Este é o mesmo ato, uma fonte
depois.

⚠️ E o comentário da própria lista registra por que o defeito recorre: a camada **atribui por
FONTE** (`if fonte in _FONTES_CLASSE_PARADA`), então basta uma curva sem a assinatura cair
numa fonte listada para receber um rótulo que a medição não sustenta.

## 3. Custo — MEDIDO antes, rodando o canônico duas vezes

| | hoje | sem `YANG_2019` |
|---|---:|---:|
| **tripé** | **143** | **143** |
| `classe_parada` | 6 | **5** |
| `indecidivel_sem_piso` | 14 | **15** |
| **`form_limited`** | **0** | **0** |

⚠️ **Não gera trabalho.** A curva não cai em `form_limited` — cai em
`indecidivel_sem_piso`, porque o `YANG_2019` **não tem piso medido**. A troca é de um
estatuto que afirma *"encerrada pela classe"* por outro que afirma *"não julgável, falta
réplica"*. O segundo é honesto sobre o motivo; o primeiro faz uma afirmação sobre a **forma**
do defeito que esta curva **não exibe**.

## 4. Predições registradas ANTES de executar

1. **Censo inalterado em 143/205.** A remoção muda rótulo, não veredito. Se o censo mover, o
   teste está inválido.
2. **`classe_parada` 6 → 5** e **`indecidivel_sem_piso` 14 → 15**; soma das camadas segue
   **62**.
3. **`form_limited` continua 0.**
4. **Δ = 0 em toda curva fora do `YANG_2019`** — a lista é consultada por nome de fonte.
5. **A 2ª linha da fila continua 5** — `_FORMA_NOMEADA` não muda.

## 5. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | censo | `_censo()["tripe"]` = **143**, `n` = **205**, `fora` = **62** |
| **G2** | camadas | `classe_parada` = 5 · `indecidivel_sem_piso` = 15 · soma = **62** |
| **G3** | fila | `form_limited` = **0**; 2ª linha = **5** |
| **G4** | isolamento | nenhuma curva fora do `YANG_2019` muda de camada |
| **G5** | baseline da composição | `_CLASSE_PARADA` em `test_classe_parada_nao_cresce_calada` atualizado **no mesmo commit**, com o motivo — senão a guarda fica mentindo |
| **G6** | suíte | completa verde |
| **G7** | documentos vivos | `test_meta_numeros_nao_envelhecem` verde; cabeçalho da mesa re-sincronizado no MESMO commit |

## 6. Ramos

**ADOTA** (G1–G7 passam) · **REVERTE** (qualquer gate falha) · **INCONCLUSIVO** (a remoção não
muda nada ⇒ a lista não era consultada como eu suponho).

## 7. ⚠️ O item **P** NÃO entra — já está coberto, e verifiquei

A proposta P era uma guarda contra as **entradas inertes** (`CHU_2026` com 0 membros e **6
exceções assinadas**; `JCSR_2023` com 0 e 1), cujo risco é: retratar uma exceção faz a curva
**escorregar em silêncio** para `classe_parada` e contar como *"fechada com procedência"*.

**Testado por perturbação:** removendo `chu2026ti_D0p4mm_F0_49kN_test2` de `_EXCECOES` em
memória, o `test_classe_parada_nao_cresce_calada` **falha nomeando a curva**
(`entraram: [...]`). ⇒ **a defesa já existe**; construir outra seria redundância.

O risco fica **registrado** (as duas entradas inertes seguem na lista, e é correto que sigam —
elas voltam a valer se a fonte perder exceções), mas **sem guarda nova**.
