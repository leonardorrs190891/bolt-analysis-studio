# Auditoria da camada mais forte: as **exclusões do denominador**

**2026-08-07** · só-leitura · **nada alterado** · a premissa **se confirma**.

## Por que esta camada, e por que ela é a mais forte

As camadas auditadas até aqui (F7, F5, declarações, `n<6`) **excusam** uma curva:
ela continua no denominador e o placar mostra que ela não passa. A camada de
`caso_comparavel` faz outra coisa — **retira a curva do censo**. Não é perdão, é
remoção da conta. Nunca tinha sido auditada.

São **5 de 210** registros:

| curva | fonte | motivo | audita? |
|---|---|---|---|
| `ancora_interna` · `ancora_interna` · `ancora_interna` | `ANCORA_INTERNA` | decisão do professor (2026-08-01: *"a âncora interna não faz parte mais desse projeto"*) | não — é instrução explícita |
| `exemplo_m12_sintetico` | `USER` | caso **sintético**, não é dado | não — não há o que medir |
| **`lu2024_M8_fig18_amp1p0`** | `LU_2024` | *"duplicata de `fig20_T22Nm`; mesmo teste em 2 figuras"* | **sim** |

## A que merecia escrutínio — e por quê

A exclusão por duplicata **beneficiaria o número publicado** se a curva
descartada fosse a que reprova: `fig18_amp1p0` tem MAE **0,0659**, acima do
limite de 0,05. Uma escolha de *qual* das duas manter pode virar escolha de
placar sem que ninguém note.

E a premissa é forte e testável: *"o mesmo teste"* ⇒ mesmo veredito, mesmo
modelo, dados concordando no piso de digitalização.

## O que a medição diz — a premissa passa em todos os testes

| teste | resultado | veredito |
|---|---|---|
| as duas recebem o mesmo veredito? | `fig18_amp1p0` **reprova** (0,0659 / 0,1069 / 0,0356) e `fig20_T22Nm` **reprova** (0,0923 / 0,2138 / 0,0512) | ✅ mesma conclusão |
| a exclusão beneficia o placar? | **não** — a mantida também reprova, e é carregada como exceção F7 | ✅ neutra |
| configs iguais? | **0 campos diferem**; δ = 1,0 mm e `n_cycles` = 99 nos dois | ✅ |
| modelo é a mesma curva? | MAE modelo-vs-modelo **0,0035** | ✅ |
| dados concordam no piso? | MAE **0,0131** · σ **0,0209** — bate com o piso registrado (0,0127 / 0,0192) | ✅ |

## O fio que sobrava, e sua explicação

Os erros de modelo diferem em **0,0264**, mais que os **0,0131** de discordância
do dado — o que pareceria violar a desigualdade triangular. Não viola: as
**janelas da métrica diferem**, `[0..56]` contra `[0..54]`, com 13 pontos cada
mas em **abscissas distintas** e finais 0,1000 × 0,1124.

⇒ **MAE em suportes diferentes não é comparável por desigualdade triangular.**
As duas métricas medem a mesma coisa em grades distintas. É uma armadilha geral
de comparação de digitalizações, e vale registrá-la: para comparar erros entre
duas digitalizações do mesmo ensaio, **interpole na janela comum primeiro** — foi
o que a linha do "dado-vs-dado" faz e a do "MAE do store" não.

## Conclusão

**A exclusão do denominador está íntegra nos 5 casos.** Três são instrução
explícita, uma é sintética, e a única com argumento técnico foi testada em cinco
frentes e passa em todas — inclusive na que poderia tê-la derrubado (não
beneficia o placar).

⚠️ **Auditoria que CONFIRMA é resultado**, não trabalho perdido: esta era a única
camada de estatuto ainda não testada, e agora as **cinco** (F7 · F5 · declarações
· `n<6` · exclusão do denominador) têm auditoria registrada.

## Reprodutibilidade

`rh.caso_comparavel` + `rh._SRC_NAO_COMPARAVEL` / `rh._CID_NAO_COMPARAVEL` sobre
o store; a concordância dado-vs-dado e modelo-vs-modelo por interpolação na
janela comum. Segundos.
