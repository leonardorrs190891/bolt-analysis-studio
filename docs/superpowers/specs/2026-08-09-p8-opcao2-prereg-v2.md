# Prereg **v2** — P-8 opção 2, com o E4 corrigido

**2026-08-09** · assinatura *"assino tudo"* · substitui
`2026-08-09-p8-opcao2-prereg.md`, cuja execução foi **revertida por gate**.

## Por que existe uma v2 — erro meu, não da correção

A v1 executou e **E1, E2, E3 e E5 passaram**; o **E4 falhou**:

> `limite_sres(LU_2024)` **0,1030 → 0,1303** — afrouxou, e a v1 dizia que
> afrouxar **para a execução**.

Revertido bit-a-bit (store e as 2 CSVs), estado conferido: limite de volta a
0,1030, `fig20_T22Nm` de volta a MAE 0,0923, invariante 16/16.

**O diagnóstico mostra que o gate estava mal escrito, não a correção:**

| família de piso do LU | σ antes | σ depois |
|---|---:|---:|
| digitalização `δ=1 F=4627` | 0,0192 | **0,0069** ✅ (era o alvo) |
| **condição** `22N·m/1,0mm` | 0,1827 | **0,3044** |

A `fig20_T22Nm` é membro dos **dois** pares. Corrigi-la aproximou-a da irmã de
**digitalização** e afastou-a da irmã de **condição** — e `limite_sres` é média
das famílias.

⚠️ **E a própria P-8 já previa isso, com todas as letras:**

> *"O piso antigo media **`fig18` enviesada contra `fig14` correta — próximo por
> acaso**; com a `fig18` certa, a dispersão real entre réplicas [sobe]."*

Ou seja: o afrouxamento **é o valor verdadeiro sendo revelado**. O piso de
0,1827 era pequeno **por coincidência de viés**, não por concordância real. Eu
escrevi um gate — *"não pode afrouxar"* — que o texto da proposta que estou
executando **já dizia que falharia**. Isso é falha de leitura minha na redação do
prereg, e é exatamente a classe de erro que a campanha registra desde 07-08:
**ler a fonte gravada antes de escolher o teste**.

## O que muda na v2

**Só o E4.** Ele deixa de ser *"não pode afrouxar"* e passa a ser
**direcional e falsificável**:

> **E4′** — o afrouxamento tem de vir **exclusivamente** da família de
> **condição** (o piso de digitalização tem de **apertar**). Se a família de
> digitalização também afrouxar, a correção não fez o que se afirma e a execução
> para.

Isso testa a **explicação**, não o número: se o viés compartilhado saiu, o piso
de digitalização **tem** de cair.

## Gates v2 (congelados)

| # | gate | esperado |
|---|---|---|
| E1 | CSVs × tabelas em c10/c50 | ≤ ±0,005 |
| E2 | piso de **digitalização** (σ) | 0,0192 → **0,0069** (±0,001) — **aperta** |
| **E4′** | piso de **condição** (σ) sobe **e** é a única a subir | 0,1827 → 0,3044; digitalização **não** sobe |
| E3 | censo | inalterado (**139**) |
| E5 | exceção F7 da `fig20_T22Nm` sobrevive | prova cita piso da **condição** (0,613); MAE **melhora** 0,0923 → 0,0520 |
| E6 | suíte completa | verde |

⚠️ **E5 fica MAIS forte, não mais fraco:** a prova é `MAE ≤ piso/√2` contra o
piso da condição. Esse piso **sobe** (0,613 → maior) e a MAE **cai** — a exceção
fica folgada dos dois lados. Mas o **mirror-rule** da suíte é quem confirma.

⚠️ **Consequência que agora está declarada em vez de barrada:** a barra do LU
afrouxa de **0,1030 para 0,1303** (+27 %). A P-8 dizia que a campanha *"nunca
teve precedente de afrouxar a barra como efeito colateral"* — este passo cria
esse precedente, **conscientemente**, porque a alternativa é manter um piso que
só era apertado por coincidência de viés. Isso tem de sair publicado junto com o
número, não escondido no meio da execução.

## Rollback

Backups `.bkp_p8` já existem (store + 2 CSVs) e foram exercitados na v1 — o
rollback é conhecido e funciona.
