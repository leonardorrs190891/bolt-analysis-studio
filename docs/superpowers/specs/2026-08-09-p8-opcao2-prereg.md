# Prereg — **P-8 opção 2**: corrigir o PAR de digitalização do LU

**2026-08-09** · assinatura do professor: *"assino tudo"* · gates **IMUTÁVEIS**
a partir daqui.

## Como estou lendo a assinatura

*"Assino tudo"* autoriza **a tentativa sob a disciplina da campanha**, não o
resultado: prereg antes, gates congelados, adoção **só se passarem**. Assinatura
não dispensa gate.

A P-8 traz **três opções e uma recomendação própria**: *"(2) agora, (1) quando
houver decisão sobre o re-fit"*. Executo a **(2)**. A **(1)** exige **re-fit
acoplado** do LU — calibração nova, com identificabilidade e procedência
próprias —, e merece prereg específico dizendo o que se re-fita; ela vem depois,
como a própria proposta ordena.

## Ação

Escrever em disco as CSVs corrigidas de **duas** curvas — o par que é o **mesmo
ensaio em duas figuras** (Tabela 8@1,0 mm ≡ Tabela 9@22 N·m):

* `lu2024_M8_fig18_amp1p0` (fora do censo — é a duplicata)
* `lu2024_M8_fig20_T22Nm` (no censo, **exceção F7 assinada**)

Construção já validada no premeasure: mesmos ciclos, `y` interpolado da série
extraída da figura, **1º ponto da tabela impressa**.

**Por que só o par:** as duas erram **juntas** (viés compartilhado), e é por isso
que o "piso de digitalização" de 0,0192 media **concordância, não acurácia**.
Corrigi-las tira o viés comum sem tocar nas 5 exceções das outras curvas.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **E1** | CSVs corrigidas × tabelas impressas em c10/c50 | **≤ ±0,005** |
| **E2** | piso de digitalização do par (σ) | **0,0192 → 0,0070** (±0,001) |
| **E3** | censo | **inalterado** (139) |
| **E4** | `limite_sres("LU_2024")` | **não pode AFROUXAR**; medir e publicar |
| **E5** | a exceção F7 da `fig20_T22Nm` sobrevive | prova cita o piso da **condição** (0,613), não o de digitalização; e a MAE dela **melhora** (0,0923 → 0,0520) |
| **E6** | suíte completa | verde |

⚠️ **E4 é o gate que mais me preocupa e por isso não prevejo valor.** A P-8 mede
que corrigir **as 7** afrouxa a barra 32 % — a campanha *"nunca teve precedente
de afrouxar a barra como efeito colateral"*. Corrigir só o par deveria **apertar
ou não mexer** (o σ do par cai). Se **afrouxar**, a opção 2 herda o problema que
era da opção 1 e a execução **para**.

⚠️ **E5 tem precedente fresco:** na P-15 o gate de suíte pegou uma consequência
na camada de exceções que o prereg não previra. Aqui a exceção é tocada
**diretamente** — os números dela mudam —, então E5 é explícito e E6 confirma.

## O que fica declarado, aconteça o que acontecer

`fig18_amp0p25` e `fig20_T4Nm` são **pretas** e não foram lidas (preto é também
moldura, escala e legenda). Após esta execução, elas e as outras 3 não-corrigidas
ficam com **dado antigo** — a fonte passa a ter **duas gerações de CSV**, e isso
tem de estar escrito no resultado.

## Rollback

Backups `.bkp_p8` das 2 CSVs. Qualquer gate divergente ⇒ restaura e registra.
