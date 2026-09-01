# `YANG_2023_IJPEM` (0 de 9): as 4 abertas discordam **no sinal de nível E no sinal de taxa**

**2026-08-10** · só-leitura · **nada adotado** · store `d197fc4c491c`, censo 144/205.

## Por que esta fonte

É a **pior da biblioteca**: **0 de 9** no tripé, 4 abertas, e nunca foi atacada com o
`ataque_curva.py` **depois** do conserto que o tornou capaz de sondar as alavancas paradas no
default (`0c4477a`).

## O resultado — e ele é sobre DIREÇÃO, não sobre magnitude

| curva | tamanho | F₀ | viés | `ρ(resíduo, N)` | leitura |
|---|---|---:|---:|---:|---|
| `0_25_mm` | M8 | 14 300 | **+**0,166 | **+1,00** | rampa: modelo perde cada vez menos |
| `0_30_mm` | M6 | 11 000 | +0,047 | −0,03 | offset uniforme |
| `0_35_mm` | M8 | 14 300 | **−**0,159 | **−0,75** | rampa **invertida**: perde cada vez mais |
| `0_50_mm` | M6 | 11 000 | +0,239 | +0,70 | misto |

⚠️ **As quatro discordam nos dois eixos do diagnóstico**: o sinal do viés (+, +, −, +) e o sinal
de `ρ` (+1,00, −0,03, −0,75, +0,70). Uma curva quer mais perda com o tempo, outra quer menos, e
uma terceira quer um degrau.

**E não é o tamanho do parafuso.** O desacordo está **dentro** de cada grupo: as duas M8
(`0_25` e `0_35`) têm ρ de +1,00 e −0,75; as duas M6 (`0_30` e `0_50`) têm −0,03 e +0,70.

## Consequência: nem constante nem forma únicas podem servir

O shell confirma nas quatro: **nenhuma alavanca livre fecha**, e a varredura **conjunta**
nível×forma do canal dominante dá **0 de 25 células** em três delas (a quarta é a STICK, onde
o canal nem é sondável). O σ_res é a perna que manda nas quatro.

Isto é mais forte que "form-limited": **uma forma nova, qualquer que seja, tem de escolher um
sinal**, e duas destas curvas vão para o lado oposto dela. A regra
`regra_canal_vs_classe_resultado.md` já barra a constante compartilhada nesta fonte
(sinais mistos ⇒ sem direção única); esta medição estende o bloqueio à **forma** compartilhada.

## Onde a suspeita legítima passa a apontar

Se quatro curvas do **mesmo rig**, com os mesmos corpos-de-prova e a mesma matriz de ensaio,
exigem correções de sinal oposto, a hipótese de "modelo incompleto" perde poder explicativo
frente a duas alternativas mais simples:

1. **Digitalização.** A nota de aparato desta fonte foi escrita **sem o PDF** (paywall) a partir
   do `DEEP_RESEARCH_REPORT` + companion OA + medições no store, e **marca como FALTA** o que
   exige o paper. Nenhuma das 9 curvas tem conferência contra o impresso.
2. **Inputs.** A mesma nota registrava **dois desacordos** (frequência e F₀ do M6). Eles foram
   corrigidos num re-stamp de 2026-07-28 (freq 10 Hz, M6 11 kN) — e as 9 seguem **0 no tripé**,
   o que significa que a correção não era o defeito dominante, não que os inputs estão
   auditados.

⚠️ **Não afirmo que a digitalização está errada** — afirmo que ela é a única camada desta fonte
que nunca foi verificada, e que o padrão medido (sinais opostos intra-rig) é a assinatura que
uma digitalização inconsistente produziria. Verificar exige o PDF, que está sob paywall; a
decisão de substituir a fonte (política registrada do professor: *"substitua os artigos que não
tiver acesso"*) é dele, não minha.

## O que fica

* `YANG_2023_IJPEM` é **bloqueada por incoerência interna**, não por falta de alavanca — e isso
  é uma classe distinta de "form-limited" que vale nomear: **fonte sem direção comum**.
* As 3 curvas `below_threshold`/`n<6` já são declaradas; as 4 abertas ficam com este diagnóstico
  em vez de um candidato.
* O `delta_free` (0,15 mm no M6, 0,18 mm no M8) **já implementa** o limiar do paper — o split
  stick/parcial desta fonte é por desenho, não defeito.

## Reprodutibilidade

```bash
py -3.12 -u New_Theory/ataque_curva.py 10_Yang_2023_phenomenological_model__0_35_mm__3
```
