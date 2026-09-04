# O `censo_por_proposta` reportava **um só sentido** — progresso sim, crescimento não

**2026-08-15 (17:xx)** · store `20be19aabe11`, censo **143/205**, fora **62**, fila
form-limited **0** · **nada reclassificado, nada adotado** — um script de sonda e um teste.

---

## 1. Como apareceu

Rodando os três instrumentos que o protocolo de retomada pede, os números **não fecharam**:

| instrumento | fora | declarada | indecidível |
|---|---:|---:|---:|
| `regra_de_parada_triagem` (canônico) | **62** | 18 | 14 |
| `censo_por_proposta` | **56** | 17 | 9 |

O `censo_por_proposta` roda sobre `mapa_das_65_fora.json`, um **retrato congelado** — e isso
é deliberado (ele mede **cobertura de proposta**, não censo). Mas ele imprimia a decomposição
sob o rótulo *"classificador canônico da triagem"*, sem dizer o denominador. Ao lado do
canônico, isso lê como **divergência de instrumento**.

## 2. A assimetria, que é o defeito de verdade

O script sempre reportou as que **FECHARAM** desde o mapa. **Nunca** as que estão fora **hoje**
e o mapa não conhece.

Medido:

| | curvas |
|---|---:|
| mapa congelado | **66** |
| fora hoje (canônico) | **62** |
| interseção (= o que o script contava) | **56** |
| **fecharam** desde o mapa (o script **já** reportava) | **10** |
| **fora hoje e ausentes do mapa** (o script **não** reportava) | **6** |

⇒ num relatório de **cobertura**, reportar só as saídas é o viés errado: mostra progresso e
esconde crescimento.

**As 6 ausentes:** 5 curvas `demir2024_*` + `lu2024_fig18_amp1p5`.
**Camadas:** 5 `indecidivel_sem_piso` · 1 `declarada`.

> ⚠️ **ERRATA 2026-08-15 (17:xx).** A 1ª versão desta linha dizia *"5 do `DEMIR_2024`,
> fonte posterior ao mapa"*. **A fonte é `ICMEZ_2025`** — eu inferi o nome pelo prefixo
> do `case_id`, que é `demir2024_*`. Erro do tipo que este mesmo documento registra na
> §4: nome lido do lugar errado.
>
> O que **se sustenta** na medição: (a) *"posterior ao mapa"* está **certo** — **0 das 8**
> curvas do `ICMEZ_2025` estão no mapa congelado; (b) o `piso=None` que as põe em
> `indecidivel_sem_piso` está **certo** — as 8 formam um **fatorial 2×2×2**
> (amp 0,3/0,4 mm × F₀ 14,3/17,6 kN × grip 13,8/19,8 mm) com **8 células únicas e zero
> réplicas exatas**.
>
> ✅ E isto **confirma independentemente** o **BLOQUEIO G/H de 2026-08-14**, que retirou
> 5 pareamentos do `ICMEZ_2025` por cruzarem grip 13,8×19,8 mm: os tokens `lk13p8`/
> `lk19p8` **são** esses comprimentos de aperto. O piso ausente não é lacuna de dado —
> é a **geometria do desenho experimental**.

⚠️ **Nenhuma é `form_limited`** ⇒ a afirmação central do script (*"ABERTAS 0"*) **sobrevive
intacta**. O ponto cego existe e hoje **não esconde trabalho**.

## 3. O que foi feito

**(a) O script passou a imprimir as duas direções** e a declarar o denominador: a
decomposição agora diz *"SOMENTE sobre as 66 curvas do MAPA CONGELADO"* e avisa, em texto, que
**não é o censo** — com a razão pela qual a confusão é fácil.

**(b) Guarda nova** — `test_o_ponto_cego_do_mapa_congelado_nao_esconde_trabalho`: nenhuma
ausente do mapa pode ser `form_limited`. Ausente com estatuto é escrituração atrasada; ausente
que é **fila de trabalho** é trabalho que nenhuma proposta cobre e que ninguém está vendo.

⚠️ **A guarda é hoje VACUOSA e isso está declarado**: com `form_limited` = 0 globalmente ela
não pode falhar. Validei o **encanamento** em vez de supor — plantando uma órfã falsa via
`classificar` monkeypatchado, a guarda **falha e nomeia a curva**, e volta a passar quando a
perturbação sai. É o que separa "teste que passa" de "teste que funciona".

## 4. Dois erros meus na mesma escrita, ambos pegos antes de publicar

1. **Parse do mapa com a chave errada.** Usei `case_id`; a chave é **`cid`**. O set virou de
   tamanho **1** e eu estava a um passo de publicar *"ponto cego de 62 curvas"*. O que
   denunciou foi o próprio absurdo do número — mapa de 1 curva não existe.
2. **Esqueci o filtro de comparabilidade** na seção nova. Deu **10** em vez de 6: entraram as
   3 `ancora_interna*` (fora do projeto desde 08-01) e a duplicata `lu2024_fig18_amp1p0`
   (`_CID_NAO_COMPARAVEL`) — exatamente as que **não estão no censo**. Corrigido na mesma
   escrita, com o motivo em comentário: o `res` do script inclui incomparáveis **de
   propósito**, e todo consumidor novo precisa re-aplicar `rh.caso_comparavel`.

## 5. O que NÃO mudou

Censo **143/205**, store `20be19aabe11`, fila form-limited **0**, camadas **23/18/6/14/1**,
`_EXCECOES`/`_DECLARADAS` intactos, `regra_de_parada_triagem.py` e `report_html.py` **não
tocados**, nenhuma config alterada.

## Reprodutibilidade

`py -3.12 New_Theory/censo_por_proposta.py` (as duas direções agora saem na tela) ·
`py -3.12 -m pytest tests/test_instrumentos_de_censo_concordam.py -q` · perturbação do
encanamento inline no corpo do commit.
