# Declarar um par muda o tripé de uma fonte inteira **sem mover o fingerprint**

**2026-08-16 (23:0x)** · só-leitura · **nada executado** · store `7a60cacb72de`, censo
**144/205** · **proposta aguarda assinatura**.

---

## 1. Como cheguei aqui

O passo 3 do cron manda **ler** o cabeçalho de estado do `DECISOES_PENDENTES.md` — o que
torna o cabeçalho auditável. Ele **omite** a adoção do par `fig8a`×`fig8c` do `ECCLES`
(item O, sessão paralela), que moveu `limite_sres(ECCLES_2010)` de **0,025 → 0,0698**.

Ao investigar por que o fingerprint não registrou isso, achei a razão — e ela é estrutural.

## 2. O fingerprint não cobre onde os pares declarados vivem

```python
def engine_fingerprint() -> str:
    """sha256 curto do estado que muda predicoes: bloco shared + configs adotadas."""
    consts, _ = frozen_constants()
    adopted = {s: kb.adopted_config(s) for s in kb.adopted_sources()}
    blob = json.dumps({"shared": consts, "adopted": adopted}, ...)
```

⇒ ele hasheia **`{shared, adopted}`** e mais nada. Os pares de réplica declarados vivem em
**`report_html.py::_PARES_REPLICA_DECLARADOS`** (linha ~1276), que **não entra no hash**.

E o par declarado alimenta `_pisos_medidos` → `limite_sres(fonte)` → **a 3ª perna do
tripé**. ⇒ **acrescentar uma linha àquela lista muda o veredito de uma fonte inteira, e o
fingerprint não se move um bit.**

**Magnitude medida no caso real:** a barra de σ do `ECCLES_2010` ficou **2,8× mais
permissiva** (0,025 → 0,0698) sem qualquer alteração de hash.

## 3. Quantos vereditos dependem disso — número CORRIGIDO

Curvas que passam a perna σ **só** porque o limite da fonte é maior que o global:

| fonte | curvas | viram | limite | par **declarado**? |
|---|---:|---:|---:|:--:|
| `BAUER_2024` | 9 | **7** | 0,0900 | ❌ automático |
| `KARLSEN_2022` | 11 | **4** | 0,0903 | ✅ **declarado** |
| `ECCLES_2010` | 10 | **4** | 0,0698 | ✅ **declarado** |
| `CHU_2026` | 9 | 0 | 0,0296 | — |

⚠️ **Errata da minha 1ª leitura:** eu ia publicar *"15 curvas dependem de pares
declarados"*. **Falso** — `_pisos_medidos` mede pisos do store por pareamento
**automático** também, e só **5** pares são declarados à mão (`CACCESE`, `ECCLES`,
`LI_2022`, `LIU_2016`, `KARLSEN`). Cruzando as listas, o número honesto é **8** (KARLSEN 4
+ ECCLES 4); as 7 do `BAUER` vêm de pareamento automático.

> ⛔ **ERRATA 2026-08-17 (09:5x) — o número é 4, não 8, e a fonte é só uma.**
>
> Eu contei as curvas que *"passam a perna σ só porque o limite da fonte é maior que o
> global"* — mas **sem exigir que estivessem no tripé**. Curva que passa o σ pelo piso e
> reprova no MAE ou no res.máx **não está no censo**, logo o par declarado não decide nada
> sobre ela.
>
> Medido com o filtro certo (**está no tripé** *e* σ > 0,025):
>
> | curva | fonte |
> |---|---|
> | `karlsen2022_M30_HV_run2p2` | `KARLSEN_2022` |
> | `karlsen2022_M30_HV_run6p2` | `KARLSEN_2022` |
> | `karlsen2022_M30_HV_run7p1` | `KARLSEN_2022` |
> | `karlsen2022_M42_HV_run21p0` | `KARLSEN_2022` |
>
> ⇒ **4 de 144 (2,8 %)**, todas do `KARLSEN_2022`. **Zero do `ECCLES`** — as 4 curvas do
> `ECCLES` que eu contara reprovam em outra perna e estão fora do censo de qualquer modo.
>
> ⚠️ O argumento **estrutural** não muda (o fingerprint segue cego à lista, e a barra do
> `ECCLES` ainda saltou 2,8× em silêncio), mas a **magnitude cai à metade** e o alvo é **uma
> fonte, não duas**. Nona correção da mesma família em dois dias: contar sem aplicar o filtro
> de pertinência.

⇒ **4 de 144 curvas do tripé (2,8 %) têm a 3ª perna decidida por uma lista que o
fingerprint não vigia** — todas do `KARLSEN_2022` (ver errata acima).

## 3a. O que o baseline da parada (`0a9e5f7`) cobre — e o que não

A sessão paralela transformou a cláusula de reabertura em **invariante**
(`New_Theory/parada_baseline.{py,json}` + `tests/test_parada_reabre_quando_deve.py`, 4
testes, validados por perturbação nos 4 gatilhos). O baseline congela o **piso da fonte** de
cada curva — logo declarar um par que mova um piso **dispara** a guarda deles.

⚠️ **Mas só para as 6 curvas da `fila_julgavel`.** Medido: as 4 afetadas **não** estão entre
elas — são curvas **no tripé**, e o baseline não as cobre.

| guarda | cobre | n |
|---|---|---:|
| `test_parada_reabre_quando_deve` (deles) | curvas da **fila julgável** | 6 |
| item **V** (esta proposta) | curvas **no censo** com σ decidido por par declarado | 4 |

⇒ as duas são **complementares, não redundantes**. A deles protege a *decisão de parar*; o
V protege o *número publicado*.

## 4. Por que isto importa, e o que NÃO estou dizendo

**Não estou dizendo que os pares declarados são ilegítimos.** Cada um tem prova escrita, e
a campanha já **retratou 5 pareamentos inválidos** quando a prova não sustentava — a
disciplina existe e funciona.

O problema é o **sinal**. O `CLAUDE.md` §4.43 diz: *"toda falsificação ou pendência
registrada carrega o fingerprint contra o qual foi medida, e vira suspeita assim que o
fingerprint muda"*. Uma mudança que **não** move o fingerprint **nunca dispara essa
suspeita** ⇒ um documento medido antes da declaração continua carimbado com o mesmo hash
depois dela, e nada o marca como suspeito — mesmo que suas conclusões sobre aquelas 8
curvas tenham mudado.

⚠️ **Sendo justo com a regra de parada:** a cláusula de reabertura dela **já cobre** este
caso explicitamente — *"reabre se … o `n` ou o **piso** de qualquer curva da fila mudar"*.
⇒ o furo é do **§4.43 / fingerprint**, não da regra de parada.

## 5. Proposta — **aguarda assinatura**

| # | ação | custo |
|---|---|---|
| **V1** (recomendada) | incluir `_PARES_REPLICA_DECLARADOS` no `engine_fingerprint`. ⚠️ **Muda o fingerprint hoje** e obriga um re-carimbo dos 210 — mas passa a ser o **último** que essa lista causa em silêncio | médio (1 linha + re-stamp) |
| **V2** | guarda de teste que congela a composição da lista e **falha quando ela muda**, nomeando quem entrou/saiu — o padrão de `test_classe_parada_nao_cresce_calada.py` | baixo (1 teste), **não** re-carimba |
| **V3** | não mexer | ⛔ mantém 8 vereditos governados por lista não vigiada |

**Recomendo V2 primeiro.** Ele torna a mudança **audível** sem custo de re-carimbo, e o
precedente já existe no repo. O V1 é mais forte e mais caro; vale se você quiser que o
fingerprint seja de fato *"tudo que muda predição"* — e hoje ele **não é**, porque a 3ª
perna sai dele.

⛔ **Não executo** — V1 mexe no fingerprint (adoção) e V2 cria guarda que bloqueia commits;
ambos exigem assinatura.

## 6. ⚠️ Nota sobre acúmulo na mesa

Este é o **3º item meu** aguardando assinatura hoje (**T** rótulo da `fig8a`, **U** critério
(c) da parada, **V** este). Nenhum é urgente e nenhum move censo. **Sugiro decisão em
bloco**, e se preferir despachar rápido: **T1 · U1+U2 · V2** são os três de menor custo, os
três satisfeitos pelo estado atual, e nenhum reabre a parada.

## Reprodutibilidade

Leitura de `runner.engine_fingerprint` e `report_html._PARES_REPLICA_DECLARADOS`; contagem
via `rh.limite_sres`, `rh.sres_para_censo`, `rh.META_SRES` e `T.pisos_medidos` — nenhuma
reimplementa regra.
