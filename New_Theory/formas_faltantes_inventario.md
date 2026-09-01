# Inventário das FORMAS FALTANTES — a campanha nomeia **oito**, e só duas estão na fila

**2026-08-07** · síntese só-leitura · store `d9a680664797` · censo **140/205**.

## Por que este inventário

O `mapa_das_65_fora_resultado.md` mostrou que as 31 curvas sem estatuto se
distribuem por três decisões. Mas auditando as **9 exceções F5 de argumento
próprio** — o único grupo que a auditoria da madrugada não tocara — apareceu
que **quatro delas dizem, no próprio texto, que falta forma no engine**:

> *"o engine não tem contorno axial externo"* · *"cliff/rebound de corrosão
> (forma faltante)"* · *"canal estrutural ξ-dependente confundido"*

Ou seja: a camada de exceção está **carregando capacidade de engine que falta**.
Isso é honesto — uma exceção com forma nomeada é melhor que uma curva sem
explicação — mas torna as formas **invisíveis** como trabalho de engine, porque
elas ficam contadas como "resolvidas".

## As oito formas nomeadas na campanha

| # | forma faltante | curvas | fontes | onde está registrada |
|---|---|---:|---:|---|
| 1 | **frequência nos relógios de Estágio I** | 7 | 3 | **P-9** (fila) |
| 2 | **platô não-nulo do afrouxamento** (bifurcação arresto/zero) | 7 | 3 | **P-13** (fila) — ⚠️ ver errata abaixo |
| 3 | contorno axial externo | 2–4 | 1 | exceção F5 (ECCLES) |
| 4 | cliff/rebound de corrosão | 2 | 1 | exceção F5 (JCSR) |
| 5 | canal estrutural ξ-dependente | 2 | 1 | exceção F5 (YANG_2021) |
| 6 | plasticidade de furo em chapa mole | — | 1 | `lu2024_plano_melhoria.md` P6 |
| 7 | membro viscoelástico (matriz polimérica) | 1 | 1 | declaração de escopo (CFRP) |
| 8 | limiar graduado (`graded_scrit`) | — | 2 | existe no engine — **sem caso de uso demonstrado** (2026-08-07) |

**Só as duas primeiras estão na fila de decisão.** As de #3 a #5 estão em
exceções assinadas, a #6 num plano, a #7 numa declaração de escopo, e a #8 já
está construída e desligada.

## O que isto reenquadra

O `mapa` diz *"31 curvas abertas, cobertas por 3 decisões"*. Este inventário diz
outra coisa, e as duas são verdadeiras:

* **por curva**: 31 abertas + 34 fechadas por estatuto;
* **por capacidade**: pelo menos **7 formas distintas** que o engine não tem
  (a #8 tem), e **20 curvas** dependem delas somando as 5 primeiras.

⇒ a leitura por curva subestima o trabalho de engine, porque uma exceção
assinada **fecha a curva** sem fechar a **forma**.

## Ordem por alcance, se o critério for capacidade

| forma | curvas | evidência mais forte |
|---|---:|---|
| **#2 taxa fracionária constante** | 7 | 3 fontes; 0,01 mm move o final de 0,94 → 0,00 |
| **#1 frequência no relógio E1** | 7 | 3 fontes; autoridade 97–100 %; rig auditado disponível |
| #3 contorno axial | 2–4 | a receita PR-31 **piorou** (res.máx 0,467 → 1,028) |
| #4 corrosão | 2 | 1 fonte; ensaio outdoor/seawater, fora do escopo mecânico |
| #5 ξ-dependente | 2 | 1 fonte |

As duas da fila são também as de **maior alcance** e as **únicas com três fontes
independentes** — o que é coincidência favorável, não desenho.

## ⚠️ ERRATA de 2026-08-07 — duas linhas desta tabela mediam mal a capacidade

`arrest_exp_resultado.md` · `graded_scrit_sem_caso_de_uso.md`.

**Linha 8 (`graded_scrit`).** Dizia *"já existe no engine, default-inerte"*,
sugerindo rota disponível. Medido nas **três** populações que o docstring cita:
falsificada na P-13 (final 0,0000 em 16/16 células contra 0,52 do dado), **piora**
no BAUER (0,0431 → 0,3223 no valor de procedência) e **nada a ganhar** no
KARLSEN (11/11 desde o D-Z). ⇒ **capacidade existente sem caso de uso
demonstrado.** Não é motivo para removê-la; é motivo para **não contá-la como
rota** ao planejar engine.

**Linha 2 (P-13).** O nome estava errado — *"taxa fracionária constante"* — e o
alvo também. A lei do platô **existe**: o `self_locking_gate` tem ponto fixo
estável em `F_min`, e `arrest_approach_exp` é a forma da aproximação. Ela **não
resolve a P-13** (inerte nas fontes com piso 0; **piora** na única com piso > 0),
mas a linha deve ler *"platô não-nulo"*, não *"taxa constante"*.

**A regra que as duas errata compartilham, e que vale para as outras seis
linhas:** *uma forma só entra neste inventário depois de perguntar ao engine se
ela existe* — e, se existir, depois de conferir os **companheiros de canal** (o
`arrest_approach_exp` é lido apenas quando `loose_arrest_floor > 0`; **10 das 18**
curvas-alvo têm piso 0). É a sexta e sétima ocorrência da mesma lição na
campanha.

## ⚠️ Uma frase vencida encontrada no caminho

A prova da `eccles2010_fig7d` diz *"PASSA no tripé por ARTEFATO: o FLOOR_TRIM
corta os 4 pontos da cauda a zero"*. **Ela não passa mais**: MAE **0,0668 =
1,34×** sob a régua de três pernas. Sob a régua antiga (MAE ≤ 0,10) passava.

A exceção **continua válida** — o argumento dela é *sobreposição axial*, não
*"passa"* —, mas a frase descreve um estado que a régua de 2026-07-29 revogou.
É o §4.43 na camada de exceção, terceiro caso (os outros dois: as 7 provas do LU
com valor derivado, e a razão invertida da `run14p2`).

**Não retratada, não reescrita** — registro assinado não se edita sem
assinatura, e o veredicto não muda.

## Conferência de que os números citados NÃO derivaram

| exceção | cita | store hoje |
|---|---|---|
| `eccles_fig6` | res.máx **0,467** | **0,4668** ✓ |
| `eccles_fig8d` | res.máx **0,252** | **0,2523** ✓ |
| `eccles_fig8b` | MAE **0,044** | dentro do limite ✓ |

Os argumentos de forma estão ancorados em números que o store ainda tem — só a
frase de estatuto da `fig7d` envelheceu.

## Reprodutibilidade

Os textos das provas saem de `rh._F5_EXCECOES`; os números, do store. Ambos
recomputáveis em segundos.
