# P-8 opção 2 EXECUTADA — o par de digitalização corrigido, e a barra afrouxa **de propósito**

**2026-08-09** · assinada (*"assino tudo"*) · prereg **v2**
(`2026-08-09-p8-opcao2-prereg-v2.md`) · **gates 6/6**.

## O que mudou

Duas CSVs re-escritas a partir da figura, com o **1º ponto vindo da tabela
impressa** — o par que é o **mesmo ensaio em duas figuras** (Tabela 8@1,0 mm ≡
Tabela 9@22 N·m):

| curva | MAE | res.máx | σ |
|---|---|---|---|
| `fig18_amp1p0` (fora do censo — duplicata) | 0,0659 → **0,0595** | 0,1069 → 0,2543 | 0,0356 → 0,0610 |
| `fig20_T22Nm` (exceção F7) | 0,0923 → **0,0520** | 0,2138 → 0,2554 | 0,0512 → 0,0600 |

Reproduz o premeasure **ao dígito** nas 6 métricas.

## Gates — 6 de 6

| gate | esperado | medido |
|---|---|---|
| E1 CSVs × tabelas (c10/c50) | ≤ ±0,005 | **0,004 / 0,002** e **0,004 / 0,000** ✅ |
| E2 piso de **digitalização** (σ) | 0,0192 → 0,0069, aperta | **0,0069** ✅ |
| **E4′** piso de **condição** sobe, e é a única | 0,1827 → 0,3044 | **0,3044**, digitalização não sobe ✅ |
| E3 censo | 139 | **139** ✅ |
| E5 exceção F7 sobrevive | MAE melhora | **0,0923 → 0,0520**, exceção viva ✅ |
| E6 suíte completa | verde | **913 passed, 1 skipped** ✅ |

## ⚠️ A v1 foi REVERTIDA, e o erro foi do gate — não da correção

A primeira execução passou E1/E2/E3/E5 e **falhou o E4**, que eu escrevera como
*"`limite_sres` não pode afrouxar"*. Revertida bit-a-bit e re-executada sob a v2.

O diagnóstico explica tudo, e **estava na própria P-8**:

> *"O piso antigo media **`fig18` enviesada contra `fig14` correta — próximo por
> acaso**; com a `fig18` certa, a dispersão real entre réplicas [sobe]."*

A `fig20_T22Nm` é membro de **dois** pares. Corrigi-la aproximou-a da irmã de
**digitalização** (σ 0,0192 → 0,0069) e afastou-a da irmã de **condição**
(σ 0,1827 → 0,3044). Como `limite_sres` é média das famílias, a barra afrouxa.

⇒ **eu escrevi um gate que o texto da proposta em execução já dizia que
falharia.** É a classe de erro que a campanha registra desde 07-08 — *ler a fonte
gravada antes de escolher o teste* — agora cometida na **redação do prereg**, não
na escolha do experimento. A v2 corrige só o E4, tornando-o **direcional**
(*"o afrouxamento tem de vir só da condição; a digitalização tem de apertar"*),
o que testa a **explicação** em vez do número.

## ⚠️ PRECEDENTE CRIADO CONSCIENTEMENTE: a barra do LU afrouxa 27 %

`limite_sres(LU_2024)`: **0,1030 → 0,1303**.

A P-8 registrava que a campanha *"nunca teve precedente de afrouxar a barra como
efeito colateral"*. **Este passo cria esse precedente**, e a justificativa é que
a alternativa é pior: manter um piso que era apertado **por coincidência de
viés**, não por concordância real entre réplicas.

O piso de 0,1827 nunca mediu repetibilidade — media uma curva enviesada contra
uma correta que, por acaso, ficavam perto. O 0,3044 é a dispersão que existe.

## ⚠️ Duas gerações de CSV na mesma fonte

As outras **5** CSVs com desvio medido (`fig18_amp0p5`, `fig18_amp2p0`,
`fig20_T10Nm`, `fig20_T16Nm`, `fig20_T28Nm`) **não** foram corrigidas — a opção 1
exige re-fit acoplado e tem prereg próprio pendente. E `fig18_amp0p25` /
`fig20_T4Nm` são **pretas**, nunca lidas.

⇒ o `LU_2024` passa a ter **duas gerações de CSV**, e quem citar o piso da fonte
tem de saber disso.

## O que fica para a opção 1

Corrigir as 5 restantes **junto com** o re-fit — porque o premeasure mediu que o
modelo **piora em 5 de 7** quando o dado fica mais certo, assinatura de
calibração que absorveu o erro de digitalização (mesmo padrão do erro de *drive*
de 2026-07-31, agora no eixo y).

## Reprodutibilidade

```bash
py -3.12 New_Theory/p8_opcao2_exec.py --dry    # só mede
py -3.12 New_Theory/p8_opcao2_exec.py          # escreve (backups .bkp_p8)
```
