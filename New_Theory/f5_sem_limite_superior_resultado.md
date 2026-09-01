# A exceção F5 de *scatter* não tem **limite superior** — e minha acusação anterior era o 5º erro de critério

**2026-08-07 (manhã)** · só-leitura · **nada retratado**.

## ⛔ Errata: a `bauer2024_M12_fig8_test1` NÃO está "acima da própria barra"

`excecoes_f5_premissa_resultado.md` (commit `2ecd296`) publicou que ela é *"a
única cuja perna coberta pela prova excede a barra da prova"* — res.máx 0,3965
contra 0,349. **A leitura está errada, e o erro é meu, de categoria.**

Duas coisas medidas:

1. **Não houve deriva.** `f5_excecoes_propostas.md` registra a `test1` com
   res.máx **0,3965** — exatamente o valor de hoje. Ela foi assinada assim.
2. **O argumento F5 de *scatter* não é limite por curva.** Está escrito:
   *"quando réplicas nominalmente idênticas divergem mais que a meta, **nenhum
   modelo determinístico único** pode ficar dentro dela. A prova é o desvio
   máximo à mediana do ensemble."* ⇒ é **unalcançabilidade da FAMÍLIA**, não
   cobertura da curva individual. Não existe "barra da prova" a exceder.

Quinta ocorrência do mesmo erro nesta passada: testar um estatuto contra o
critério errado. As anteriores: média-da-fonte em vez de piso-por-condição · F7
aplicado a F5 · primeiro-critério-que-casa · censo reimplementado.

## ⚠️ Mas a errata expõe algo mais sério que o defeito que eu acusei

O argumento F7 é **por curva**: erro ≤ piso (PROVA) ou ≤ piso/√2 (FORTE). Ele
tem **limite superior** — uma curva ruim o bastante deixa de ser coberta, e foi
assim que a campanha retratou **5** exceções.

O argumento F5 de *scatter*, como enunciado, **não tem limite superior algum**.
Se o desvio-à-mediana da família é 0,349, a conclusão *"a meta 0,10 é
inalcançável aqui"* vale **independentemente do erro da curva**. Formalmente,
uma curva com res.máx **1,0** seguiria coberta pelo mesmo texto.

Medido no caso concreto:

| curva | res.máx | desvio-à-mediana da família | razão |
|---|---:|---:|---:|
| `bauer2024_M12_fig8_test1` | **0,3965** | 0,349 | **1,14×** |
| `bauer2024_M12_fig8_test2` | 0,1795 | 0,349 | 0,51× |
| `bauer2024_M12_fig8_test3` | 0,1198 | 0,349 | 0,34× |
| `bauer2024_M8_fig6_rep4` | 0,1709 | 0,328 | 0,52× |
| `bauer2024_M8_fig6_rep1/5/6` | 0,112–0,130 | 0,328 | 0,34–0,40× |

Oito das nove estão **abaixo** da estatística da família — isto é, satisfariam
um limite por curva se ele existisse. **Só a `test1` está acima**, e por 14 %.

⇒ o problema **não** é a `test1` violar uma regra; é a regra **não existir**.
Hoje, a única exceção que um limite superior pegaria é justamente a que já me
chamou atenção — o que é evidência de que o limite seria **discriminante**, não
decorativo.

## PROPOSTA (P-11) — dar limite superior à classe F5 de *scatter*

> uma exceção por *scatter de réplicas* exige, além da unalcançabilidade da
> família (desvio-à-mediana > meta), que o erro da curva **não exceda** esse
> mesmo desvio-à-mediana — o mesmo teste por curva que o F7 já aplica.

**Custo medido, se assinada:** **1 exceção** (`bauer2024_M12_fig8_test1`) perde
cobertura ⇒ leitura *resolvido-ou-declarado* **177 → 176**. Censo estrito
**inalterado em 140** (exceção nunca contou nele). As outras 8 sobrevivem com
folga de 2× a 3×.

⚠️ **Não executo.** As 9 foram assinadas em 2026-07-28 e o limite que as testaria
é **novo** — não é medição que mudou, é critério que ganharia condição. Mesma
natureza da **P-10**, e o charter reserva emenda de camada à sua assinatura.

## Simetria com a P-10, que vale registrar

| critério | mede | tem limite superior? |
|---|---|---|
| F7 (piso por perna) | erro da curva vs piso | **sim** — 5 retratações |
| F5 *scatter* | dispersão da família | **não** ⇒ **P-11** |
| declaração por colapso | posição do res.máx vs penhasco | **sim** (0–1 índice) |
| declaração por `n<6` | suporte estatístico do σ | **sim** (mae/mx têm de passar) |
| declaração por resolução | passo do dado | **não** ⇒ **P-10** |

Os dois critérios sem limite superior são exatamente os dois que a auditoria
desta madrugada apontou. Não é coincidência: **critério que só olha o DADO
(dispersão, passo) não pode limitar o ERRO do modelo** — precisa de uma segunda
condição que compare os dois.

## Reprodutibilidade

```bash
py -3.12 New_Theory/excecoes_f5_teste_premissa.py --json New_Theory/excecoes_f5_teste_premissa.json
```
