# ADOÇÃO D-AB — `C_creep` per-par no ECCLES: a `fig7c` fecha, e o controle inverteu minha escolha

**2026-08-09 (noite)** · prereg `824cc1b` (gates congelados **antes** de qualquer medição da
execução) · executada sob a delegação permanente do professor (*"adote se os gates
passarem… tomando as decisões sozinho"*, reafirmada com *"continue o loop sem parar"*).

## De onde veio

A `eccles2010_fig7c_axial_2p7kN_constant` estava classificada como **form-limited** — veredito
que **eu publiquei na manhã do mesmo dia**, e que saiu do `ataque_curva.py` **cego**, que
sondava **2 de 7** alavancas (defeito consertado em `0c4477a`). Com o instrumento certo, **4
doses fecham o tripé**. Ela reprovava por **3 %** no σ (0,0258 contra 0,0250).

## ⚠️ O controle inverteu a escolha que a curva-alvo sugeria

| candidato | `fig7c` | ECCLES no tripé | pioram MAE >+0,01 |
|---|---|---|---|
| **`C_creep` = 2,8e-11** | 0,0249/0,0530/**0,0237** | 3 → **4** | **0** |
| `C_creep` = 3,733e-11 | 0,0247/0,0490/0,0217 | 3 → 4 | 1 |
| `N_emb` = 35 | **0,0229/0,0748/0,0203** | 3 → **1** | 3 |
| `emb_depth` = 1,43e-05 | 0,0327/0,0749/0,0168 | 3 → **1** | 7 |

A alavanca com o **melhor ajuste na curva-alvo** é a **segunda pior para a fonte**: `N_emb`=35
derruba **duas irmãs que já passavam**. Olhando só a `fig7c` eu teria escolhido exatamente a
errada — é o argumento inteiro a favor de o controle ser **gate**, e não conferência posterior.

## A física

As 8 configs do ECCLES **não declaravam `C_creep`**: a fonte herdava o valor do bloco
`shared`, **1,8667e-11**, que é o **fit da âncora interna**. A adoção cria um valor **per-fonte** de
**2,8e-11** (×1,5).

Isso é o que a §4.7 documenta como correto — **`C_creep` é POR PAR tribológico**, não universal
(âncora 304SS 9,9e-13 vs fit da âncora interna 1,2e-11, **ICs disjuntos**) — e os pares são distintos: a nota
de aparato do ECCLES registra **parafuso M8 eletro-zincado**, com a porca apoiando **direto na
placa móvel, sem arruela**. Zinco relaxa mais que aço nu, e ×1,5 é movimento de mesma ordem.

⚠️ **O que NÃO sustenta, e está escrito na procedência:** `kb.check_input("C_creep", 2.8e-11)`
devolve `None`, e isso **não é aprovação** — `C_creep` não está em `checkable_inputs()`, logo o
`None` quer dizer *"não sei checar"*. Não existe banda de âncora para esta constante.

## ⚠️ O erro da execução, e o que o pegou

O prereg registrava que são **10 curvas e 8 grupos** de config, e que a execução criaria os 2
faltantes (`fig6`, `fig8d`) — senão o **mesmo par tribológico** ficaria com **dois `C_creep`**.

Criei-os **copiando o grupo-molde inteiro**. Resultado:

| curva | previsto pelo controle | medido com a cópia | ΔMAE |
|---|---|---|---:|
| `fig6_annotated_4kN_axial` | 0,1466/0,4737/0,1892 | **0,2581/0,8457/0,2821** | **+0,1123** |
| `fig8d_axial_3p5kN` | 0,1290/0,2459/0,0927 | **0,2288/0,4000/0,0956** | **+0,0953** |

**E3 reprovou.** A causa: essas duas curvas tinham **zero** overrides — nenhuma config adotada
—, e copiar o grupo do `fig7c` injetou **11 constantes de uma vez** (`mu_thread`, `mu_bearing`,
`tr_loose_gain`, `k_wear_spec`, `loose_arrest_floor`, `pack: PACK`, …). Eu queria adotar **uma**
constante e adotei doze.

**O que pegou:** uma **checagem de predição registrada antes de medir** — a tabela do controle
do prereg, confrontada curva a curva com tolerância de 5e-4. Sem ela, o E3 acusaria "2 pioram"
e eu poderia ter lido isso como *"o candidato custa mais do que o previsto"* em vez de *"o
instrumento de adoção está fazendo outra coisa"*. São diagnósticos opostos.

**Conserto:** grupos **MÍNIMOS**, com `pack: ""` e `cfg: {"C_creep": 2.8e-11}` e nada mais.
As 10 curvas passaram a reproduzir a predição do controle **exatamente**.

## Gates — medidos

| # | gate | resultado |
|---|---|---|
| **E1** | `fig7c` fecha o tripé | ✅ **0,0249 / 0,0530 / 0,0237** (limite σ 0,0250) |
| **E2** | nenhuma curva do ECCLES sai do tripé | ✅ 3 → **4** |
| **E3** | nenhuma piora MAE >+0,01 | ✅ **0** (pior +0,0053) |
| **E4** | isolamento fora do `ECCLES_2010` | ✅ Δ = **0,000000000** em 7 curvas |
| **E5** | censo 142 → 143 | (abaixo) |
| **E6** | suíte completa | (abaixo) |
| *extra* | predição do controle reproduzida nas 10 | ✅ (reprovou na 1ª tentativa e **foi ela que denunciou a cópia**) |

## Efeito nas 10

4 melhoram, 6 pioram, pior custo **+0,0053**, nenhuma sai. `fig7d` (0,0665/0,0901/**0,0538**)
segue fora só pelo σ; `fig8a`/`fig8c` idem.

## Lição de método

**Adotar uma constante criando um grupo novo não é adotar uma constante** — o grupo é a unidade
de config, e criá-lo por cópia importa tudo o que o molde carrega. Quando a adoção precisar de
um grupo que não existe, ele nasce **mínimo**: só o campo que a adoção decide, e `pack` igual
ao que a curva tinha (aqui, vazio).

Isto tem irmã na campanha: o `per_case` que casa por substring e o empate de tokens do
`YANG_2019` — em ambos, **o mecanismo de endereçamento da config fez algo diferente do que a
adoção pretendia, em silêncio**. A defesa que funcionou aqui foi a mesma que funciona lá:
**medir contra uma predição escrita antes**.

## Reprodutibilidade

```bash
py -3.12 New_Theory/ataque_curva.py eccles2010_fig7c_axial_2p7kN_constant
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
py -3.12 -m pytest tests/ -q
```
