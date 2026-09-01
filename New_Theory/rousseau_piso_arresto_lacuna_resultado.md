# `ROUSSEAU`: o mesmo rig tem **dois pisos de arresto**, e só um tem procedência

> # ⛔ ERRATA DE 2026-08-13 — **a tese central deste documento é FALSA**
>
> **O `loose_arrest_floor = 0,2` do `ROUSSEAU_HDPE` TEM procedência registrada.** Ela está
> no `prov` sob a chave **composta** `'c_bend/emb_depth/floor'`, e diz:
>
> > **"PR-14 fitado-this-rig (rig + assentamento + piso de arresto)"**
>
> Ou seja: o valor está declarado como `fitado-this-rig` **e o piso de arresto é nomeado
> explicitamente**, desde **2026-07-12**. A "decisão do professor" que este documento pediu
> — opção (1), *declarar o 0,2 como `fitado-this-rig`* — **já estava tomada quando eu a
> pedi**.
>
> **Causa do erro:** minha sonda perguntava `prov.get('loose_arrest_floor')` — lookup
> **exato** —, e a campanha grava chave **composta** quando um único argumento cobre várias
> constantes (o que é bookkeeping *correto*: a justificativa realmente é conjunta). Eu
> estava medindo a rigidez do meu próprio lookup e lendo o resultado como lacuna do
> registro.
>
> **O que sobrevive desta página, e é o que importa:**
> * a **medição das 5 doses** (tabela abaixo) está certa e foi re-conferida — o piso
>   move o res.máx da `t10` por um fator **2,2×**, e o **censo não muda em dose nenhuma**;
> * a observação de que **o mesmo rig usa dois pisos** (aço 0,0 · HDPE 0,2) segue de pé,
>   e segue sem argumento físico que a *derive* — mas isso é **lacuna de derivação**, não
>   de bookkeeping, e é uma classe muito mais fraca de dívida;
> * a opção **(3)** (buscar no paper a compliance do HDPE e derivar o piso) continua sendo
>   a única que produziria procedência de *primeira ordem*. Ela é opcional, não devida.
>
> **O que NÃO sobrevive:** a frase *"constante fitada em silêncio"*, a contagem
> `prov = None`, e a leitura de que este caso era a 3ª ocorrência de "a métrica prefere o
> valor sem procedência" — **ele não pertence a essa série**. Restam duas (CHU/rugosidade e
> `gth_q`=7), e duas não são padrão.
>
> Pinado contra regressão em `tests/test_procedencia_catraca.py::
> test_chave_composta_conta_como_procedencia`. O texto original segue **intacto** abaixo,
> como registro do erro.

**2026-08-11** · só-leitura · **nada adotado** · store `bd74eaf0b11d`, censo **147/205** ·
achado ao investigar a classe de defeito **"bifurcação (rotacional 72–97 %)"**, que nunca havia
sido atacada.

## Como cheguei aqui

Das 26 abertas, **todas** têm defeito nomeado no mapa — o passo 4(b) do cron está esgotado. Mas
a listagem de defeitos expôs uma classe nunca investigada: **"bifurcação"**, 7 curvas, com o
canal rotacional carregando 72–97 % da perda. O `CLAUDE.md` documenta que
`loose_arrest_floor = 0` ⇒ *"runaway puro (bifurcação arrest/zero, sem meio)"*.

As 7 estão em 2 fontes, **ambas de classe mista** (`ROUSSEAU` 6P+1G+1S; `YANG_2023` 6P+3S) ⇒ a
regra canal×classe já barra constante compartilhada nas duas. Mas ao ler as constantes, apareceu
outra coisa.

## A inconsistência

| grupo | `loose_arrest_floor` | procedência registrada |
|---|---:|---|
| `ROUSSEAU_2025` (aço) | **0,0** | *"PROCEDÊNCIA DE APARATO, não fit: o rig apoia o membro móvel em **roletes INA-HYDREL FE**, declaradamente para REMOVER o atrito parasita (Sec. 2 + Fig. 3b). Sem esse atrito não há o auto-travamento que o floor representa"* |
| `ROUSSEAU_HDPE` | **0,2** | **`None`** |

**Mesmo rig, dois pisos, e só um tem argumento.** E o argumento registrado é de **fixação** —
os roletes são do dispositivo, não do corpo-de-prova; se removem o atrito parasita para os
espécimes de aço, removem para os de HDPE, que correm no mesmo aparato.

O 0,2 também não é herança: o default do pack é **0,08**, e o aço foi explicitamente movido de
0,08 para 0,0. O 0,2 é um **terceiro valor, sem registro**.

## O custo da consistência, medido

Aplicando ao grupo HDPE os valores entre 0,20 e 0,00 (sonda de instrumento primeiro: floor=0,2
reproduz o nominal ao dígito ✅):

| piso | `hdpe_t10` | `hdpe_t12` | tripé | pioram >0,01 |
|---:|---|---|---|---|
| **0,20** (vigente) | 0,0927/0,1786/0,0691 | 0,0566/0,1133/0,0456 | 4 | — |
| 0,15 | 0,0906/0,1669/0,0919 | 0,0542/0,1182/0,0600 | 4 | 0 |
| 0,10 | 0,1044/0,2317/0,1197 | 0,0635/0,2318/0,0908 | 4 | 1 |
| 0,08 (default do pack) | 0,1125/0,2593/0,1313 | 0,0694/0,2637/0,1039 | 4 | 2 |
| **0,00** (consistente com o aparato) | **0,1550/0,3999/0,1782** | **0,1023/0,3903/0,1490** | 4 | 2 |

**Monotônico:** quanto mais perto do valor que a procedência do rig implica, **pior** o modelo.
A `t10` vai de res.máx 0,179 para **0,400**. E o **censo não muda em dose nenhuma** (4 → 4): as
duas HDPE afetadas já estavam fora e continuam fora; as duas que passam (`t10_amp0p2`, `t14`)
são **insensíveis** ao piso (mudam na 4ª casa).

## ⚠️ O que eu NÃO afirmo

**Não afirmo que o 0,2 está errado.** Há razão física para o piso diferir por material do
membro: o `loose_arrest_floor` representa **auto-travamento**, e num membro de HDPE — muito mais
complacente — o parafuso pode embutir-se no polímero, o que é um mecanismo de arresto
**geométrico**, distinto do atrito parasita que os roletes removem. O argumento do aço não
*exclui* um piso não-nulo no HDPE; ele apenas **não o cobre**.

O que está medido é: (a) o valor **não tem procedência registrada**; (b) ele **não** é o default
nem o valor irmão; (c) a métrica **depende fortemente** dele (fator 2,2× no res.máx da `t10`).

## O que isto é: uma LACUNA DE PROCEDÊNCIA, não uma correção a fazer

A campanha inteira se apoia em constantes com procedência declarada — e esta é uma constante
**fitada em silêncio** que carrega 2,2× do res.máx de uma curva. Fechá-la exige o paper (a
compliance do membro HDPE, a geometria do embutimento) ou uma declaração explícita de que é
`fitado-this-rig`, com o número na mesa.

⚠️ **Terceira vez em três dias que a métrica prefere o valor SEM procedência ao valor COM
procedência** — CHU (rugosidade), `YANG_2021`/`gth_q`=7 (recusado por mim), e agora este. As
três apontam para o mesmo lugar: onde a procedência não cobre, o ajuste entrou, e a métrica
passou a depender dele.

## Decisão do professor

1. **declarar** o 0,2 como `fitado-this-rig` com o número e o custo registrados (honesto, custo 0
   no censo, fecha a lacuna de bookkeeping); ou
2. **corrigir** para 0,0 por consistência de aparato e aceitar `t10` 0,0927 → 0,1550 e `t12`
   0,0566 → 0,1023 (censo inalterado, mas a fonte piora); ou
3. **buscar no paper** a compliance do membro HDPE e derivar o piso — o único caminho que produz
   procedência de verdade.

Nenhuma delas muda o censo. A (2) **piora** o número publicado, o que é exatamente por que ela
precisa ser decidida e não escolhida por conveniência.

## Reprodutibilidade

`rous_floor.py` no scratchpad: sonda de instrumento + 5 doses no grupo HDPE, com o resto da
fonte como controle. Só-leitura, ~4 min.
