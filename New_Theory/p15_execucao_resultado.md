# P-15 EXECUTADA — o piso do ECCLES media a variável varrida, e custou o que estava previsto

**2026-08-08** · assinada pelo professor · prereg
`docs/superpowers/specs/2026-08-08-p7-p15-execucao-prereg.md` · **gates 6/6**.

## O que mudou

**10 curvas** do `ECCLES_2010` entraram em `_SEM_FAMILIA_MECANICA` — as que a
chave mecânica agrupava em `δ=0,65 mm / F_amp=6000 N / disp`. É a **6ª
ocorrência** da mesma classe de defeito no arquivo, e a **primeira que não é
inócua**.

**Razão:** a chave é cega à **carga axial**, que é a variável varrida do paper.
Os σ da família iam de **0,0195** (sem axial) a **0,1887** (4 kN) — quase 10×, e
**monotônicos com a carga**. Isso não é dispersão de réplica; é o efeito que o
Eccles estava medindo.

## Gates — 6 de 6, todos como pré-registrados

| gate | esperado | medido |
|---|---|---|
| **G1** `limite_sres(ECCLES_2010)` | 0,0828 → 0,0250 | **0,0828 → 0,0250** ✅ |
| **G2** censo | 140 → 139 | **140 → 139** ✅ |
| **G3** sai exatamente 1, e é a `fig7c` | 1 | **1: `eccles2010_fig7c_axial_2p7kN_constant`**; 0 entram ✅ |
| **G4** isolamento fora da fonte | 0 | **0** ✅ |
| **G5** os 2 invariantes **devem** acusar | falham | **falharam** ✅ |
| **G6** suíte completa | verde | **verde** ✅ |

⚠️ **O G5 era gate de SUCESSO**, e é o que valida a decisão de ter escrito
aqueles invariantes 24 h antes: o `test_declaracao_nao_vira_ficcao` falhou
porque a entrada `("ECCLES_2010", 10)` deixou de existir, e o guarda de escopo
falhou porque nenhuma família morde mais. Se eles tivessem passado, a execução
não teria feito efeito e o resultado seria **INCONCLUSIVO**.

Confirmação independente no HTML: a regeneração do report tocou **11 arquivos** —
os 10 do ECCLES e o mestre. Nada mais.

## O custo, que era conhecido e foi aceito

Censo **140 → 139**. Sai a `eccles2010_fig7c_axial_2p7kN_constant`, σ **0,0258**
contra o limite global de 0,0250 — ela estava **3 % acima** e passava só porque
o piso falso afrouxava o limite da fonte **3,3×**.

⚠️ **Consequência que reabre uma categoria:** a `fig7c` agora é a **única** curva
sem estatuto **e sem rota de modelo** — a fonte perdeu o piso junto com a família
falsa, então prova F7 ficou impossível para ela. O `mapa_das_65_fora_resultado.md`
havia declarado essa categoria **vazia** na véspera; ela volta a ter **1**. Não é
regressão do modelo: é a curva deixando de ser sustentada por um piso que media a
coisa errada.

## ⚠️ O G6 PEGOU uma consequência que eu não havia previsto — e o precedente já existia

A suíte completa **falhou** em
`test_medicoes_cruzadas::test_excecao_assinada_esta_de_fato_fora_do_tripe`, na
**regra do espelho**:

> *"retirada de 2026-07-30 tirou a assinatura de curva que AINDA falha pela regra
> efetiva: `['eccles2010_fig7c_axial_2p7kN_constant']` — devolvê-la à
> `_F7_EXCECOES`."*

A `fig7c` **tinha** assinatura F7, **retirada no D1** (2026-07-30) porque passava
por mérito. Com o piso falso removido, ela volta a falhar — e o invariante pede
a assinatura de volta.

**Mas devolver seria errado**, e a prova gravada é quem diz. O registro da
retirada em `_EXCECOES_RETIRADAS_D1` é literalmente:

> `"prova de piso (FORTE): σ 0.026/0.083"`

O **0,083** é o piso falso que esta execução acabou de retratar. Devolver a
assinatura seria **re-assinar contra piso inválido**.

⇒ tratamento correto: `_RETIRADAS_D1_INVALIDADAS_POR_ERRATUM`, que existe
exatamente para isto — **4ª ocorrência** da mesma estrutura (ROUSSEAU ×2,
JCSR ×2, SUN ×1, agora ECCLES ×1). A curva perde a exceção **e** a proteção da
retirada, e fica como falha genuína sem rota.

⚠️ **Duas leituras de método valem a pena:**

1. **A prova gravada resolveu a decisão** — foi ler o `"σ 0.026/0.083"` que
   distinguiu *"devolver a assinatura"* de *"invalidar a retirada"*. É a regra
   que me custou 5 erros em 2026-08-07 (*leia a prova antes de escolher o
   teste*), aplicada aqui **antes** de agir;
2. **eu não previ isto no prereg.** Os gates G1–G5 cobriam o efeito no censo e
   nos invariantes de piso, e nenhum antecipava o efeito na camada de
   **exceções**. Foi a exigência de suíte completa (G6) que o pegou — o mesmo
   papel que ela teve no caso SUN, onde o custo estava escrito em prosa e
   esquecido no código.

## O que isto resolve além do número

A campanha tinha uma **inconsistência interna**: as exceções F5 assinadas do
próprio ECCLES argumentam **"sobreposição axial"** — ou seja, tratavam a carga
axial como variável **distintiva** ao provar exceção, e como **irrelevante** ao
medir piso. As duas coisas não podiam valer juntas. Agora vale uma só.

## Estado após a execução

| | |
|---|---|
| censo | **139/205** |
| fora | **66** = 34 com estatuto + **32** abertas |
| resolvido ou declarado | **173/205** |
| perna que manda | σ_res **41** · MAE **12** · res.máx **13** |
| famílias divergentes que afrouxam limite | **0** (eram 1) |

## Reprodutibilidade

```bash
py -3.12 New_Theory/pares_piso_impacto.py        # o impacto, re-medido
py -3.12 -m pytest tests/test_pares_piso_familia.py tests/test_meta_numeros_nao_envelhecem.py
```
