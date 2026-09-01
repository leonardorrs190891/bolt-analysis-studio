# `ECCLES_2010` — dois pisos adotados que o dado **não sustenta**, e um deles é **portante**

**2026-08-16 (13:4x)** · só-leitura · **nada executado** · store `20be19aabe11`, censo
**144/205**, fila `form_limited` **1** · proposta **aguarda assinatura**.

---

## 0. De onde isto veio — a auditoria é filha do meu próprio erro

Uma hora atrás eu **retratei** a afirmação de que o `YANG_2023` *"arresta em 0,165"*: eu
havia lido `metric_data` (o dado **depois** do `FLOOR_TRIM` = 0,10) e chamado o último
valor dele de piso de arresto. O dado cru colapsa a 0,02–0,06 (`13ed862`).

Erro assim tem **raio de alcance**: se eu li um platô onde havia colapso, a pergunta
seguinte é **quem mais** fez isso — e principalmente se algum **piso ADOTADO** foi lido
assim, porque piso adotado entra na física de todas as curvas do grupo.

⇒ auditei os **33** `loose_arrest_floor` das configs adotadas.

## 1. A infraestrutura está limpa — e isso precisa ser dito primeiro

| leitor | o que passa | veredito |
|---|---|---|
| `validation/prefit.py` | `load_full_curve(rel)` = **CSV cru** | ✅ correto |
| `New_Theory/level_seven_probe.py` | `ratio_cru` (explícito no código e na prosa) | ✅ correto |
| `provenance.arrest_floor_from_curve` | agnóstico, **mas auto-guarda** com `plateau=False` quando a cauda ainda cai >2 % | ✅ bem desenhado |

⇒ **não há defeito de ferramenta.** O helper canônico até propaga a flag para o rótulo de
procedência (`"lido-do-dado (LIMITE INFERIOR — curva termina em queda)"`). O defeito, onde
existe, é de **quem gravou o número**.

## 2. ⚠️ O meu primeiro teste acusou 4 e estava ERRADO — registro porque é o mesmo vício

A 1ª varredura comparou o piso de cada grupo contra a **mediana das caudas de todas as
curvas da fonte** e acusou `fig3`, `fig7a`, `fig7b`, `fig7c`. Mas cada grupo do `ECCLES` é
**uma figura**, com sua própria curva — comparar contra a mediana da fonte é proxy, não
medição.

Refeito **por curva**, os 4 caem:

| grupo | piso adotado | leitura L24 do **cru** | `plateau` |
|---|---:|---:|:--:|
| `fig3` | 0,194 | **0,194** | True |
| `fig7a` | 0,216 | **0,213** | True |
| `fig7b` | 0,232 | **0,229** | True |
| `fig7c` | 0,182 | **0,180** | True |
| `fig8c` | 0,152 | **0,149** | True |
| `fig8b` | 0,000 | **0,000** | True |

⇒ **seis dos oito batem com o cru ao dígito.** O proxy fabricou as 4 suspeitas; a medição
por curva as devolveu. *(Mesmo vício da retratação: um atalho de leitura produzindo um
achado que a medição direta não confirma.)*

## 3. O que SOBREVIVE — dois grupos, e o pior tem prova aritmética

### 3a. `ECCLES_2010_fig7d` — o piso é a média **atravessando o colapso**

**Cauda crua da curva** (últimos 8 pontos, normalizados):

```
0,213 · 0,207 · 0,187 · 0,120 · 0,033 · 0,007 · 0,000 · 0,000
```

⇒ a curva **colapsa a zero exato** e fica lá. Leitura L24 canônica: **floor = 0,0000**,
`plateau = True`.

**Piso adotado: 0,137.** De onde ele vem? Varrendo a janela de cauda:

| `tail_frac` | floor | `plateau` |
|---:|---:|:--:|
| 0,05 | **0,0000** | ✅ True |
| 0,10 | 0,0023 | ❌ False |
| 0,20 | 0,0578 | ❌ False |
| 0,30 | 0,0959 | ❌ False |
| **0,40** | **0,1273** | ❌ **False** |

⇒ 0,137 corresponde a `tail_frac ≈ 0,40` — **exatamente a faixa em que o próprio helper
diz que NÃO há platô**. O número é a média de uma **rampa em queda**, e média de rampa não
é assíntota.

**E o rótulo de procedência afirma o contrário:**

```
loose_arrest_floor = "lido-do-dado (assintota final crua >=0.03;
                      fisica=torque de prevalencia)"
```

A assíntota final crua é **0,000**. O clamp declarado (`≥0,03`) daria **0,03** — não 0,137.
⇒ **o rótulo não descreve o número.**

### 3b. `ECCLES_2010_fig8a` — mesmo sinal, magnitude menor

Cauda crua plana em **0,0122** (`plateau=True` a `tail_frac`=0,05). Piso adotado **0,059**
= **4,8×** a leitura, e acima do clamp de 0,03 que o rótulo declara. Menos grave que a
`fig7d` (aqui existe platô de verdade, só que mais baixo), mas o rótulo também não fecha.

## 4. ⚠️ O achado incômodo: o piso não sustentado é **PORTANTE**

Sonda só-leitura, trocando o piso pela leitura honesta do cru:

| curva | | MAE | res.máx | σ_res |
|---|---|---:|---:|---:|
| `fig7d` | adotado (0,137) | 0,0665 | 0,0901 | 0,0538 |
| `fig7d` | **honesto (0,0)** | **0,1641** | **0,2530** | **0,0860** |
| `fig8a` | adotado (0,059) | 0,0489 | 0,1320 | 0,0395 |
| `fig8a` | **honesto (0,0)** | **0,0945** | **0,2245** | **0,0710** |

⇒ **corrigir a procedência PIORA as duas** — a `fig7d` em **2,5×** no MAE.

Isto é o que o achado realmente diz, e é mais interessante que "tem um número errado": o
piso está **segurando o modelo de pé**. Sem ele o modelo colapsa mais rápido que o dado,
e o piso vinha compensando isso. ⇒ **não é defeito de constante, é defeito de forma
mascarado por uma constante com rótulo generoso.**

⚠️ Nenhuma curva **aprovada** está em risco: as duas já estão **fora** do tripé hoje
(`fig7d` MAE 0,0665 > 0,05; `fig8a` res.máx 0,132 > 0,10). Corrigir não tira nada do censo
— só torna visível um erro que hoje está anestesiado.

## 4b. ⚠️ O QUE O PISO ESTAVA REALMENTE FAZENDO — medido 2026-08-16 (14:5x)

A §4 dizia *"o modelo colapsa mais rápido que o dado, e o piso compensava"*. Isso era
**inferência** a partir de "tirar piora", não medição. Medido agora, e a resposta é mais
específica — **e mais interessante**.

**Relógio do colapso** — em que ciclo cada um cruza o nível (dado **CRU**, não a janela):

| nível | dado cru | modelo (piso adotado) | modelo (piso 0) | razão mod/dado |
|---:|---:|---:|---:|---:|
| 0,60 | 64 | 73 | **65** | **1,01×** |
| 0,40 | 100 | 115 | **96** | 0,96× |
| 0,25 | 153 | 148 | 114 | 0,75× |
| **0,10** | **1643** | *nunca* | **130** | **0,08×** |

⇒ **o modelo acompanha o dado ao dígito até ≈0,40** (1,01× e 0,96×) e só então dispara.
O dado leva **1643 ciclos** para ir de 0,25 a 0,10; o modelo cobre o mesmo trecho em
**16** (114 → 130). ⇒ **o dado DESACELERA brutalmente na cauda; o modelo não tem
desaceleração nenhuma.**

A `fig8a` tem a mesma forma, mais branda (0,91× · 0,90× · 0,80× · **0,66×**).

### 4c. ⇒ O piso era um PROXY DE DESACELERAÇÃO, e o instinto estava certo

Com o piso adotado o modelo **nunca** alcança 0,10 — o que casa com o dado sendo
lentíssimo lá. `loose_arrest_floor` é a **única alavanca** que o engine oferece contra
runaway (`self_locking_gate`), então quem adotou usou-a para imitar a desaceleração — e
**teve de inflá-la acima da assíntota verdadeira** para que ela mordesse cedo o bastante.

**Isto reclassifica o achado:**

| leitura | veredito |
|---|---|
| *"o número está errado"* | ✅ verdade, mas é a parte pequena |
| *"erro de NÍVEL, o modelo fica baixo"* | ⛔ **falso** — bate a 1,01× até 0,40 |
| *"erro de TEMPO na CAUDA"* | ✅ **é isto** — 12,6× cedo demais em 0,10 |
| *"falta forma: desaceleração de cauda"* | ✅ e é território de **assinatura** |

⚠️ **Consequência para a decisão:** o R1 não expõe *"um déficit de forma"* genérico — ele
expõe uma **forma nomeada e localizada**: o canal rotacional não desacelera na cauda, e o
engine só sabe **travar** (piso) ou **correr** (runaway), sem meio-termo. É exatamente a
bifurcação arrest/zero que o `CLAUDE.md` já documenta em `self_locking_gate`, medida aqui
pela primeira vez **com relógio**.

⚠️ **E isso muda o custo do R1**: corrigir o piso sem repor a desaceleração deixa as duas
curvas piores **e sem alavanca** — honesto, mas sem rota. O R2 (re-rotular) passa a ser
defensável de outro jeito: o número **faz trabalho físico real** (imita desaceleração),
só não é o que o rótulo diz.

## 5. Proposta — **aguarda assinatura** (mexe em config adotada)

Três rotas, em ordem de honestidade decrescente e de custo decrescente:

| # | ação | efeito no censo | o que afirma |
|---|---|---|---|
| **R1** | corrigir os 2 pisos para a leitura L24 do cru (0,0 e 0,0122) | **0** (já estão fora) | *"a constante volta a ter a procedência que o rótulo declara; o déficit de forma fica exposto"* |
| **R2** | manter os números e **corrigir o RÓTULO** para `fitado-this-rig` | **0** | *"o número fica, mas para de se dizer lido do dado"* |
| **R3** | não mexer | 0 | ⛔ mantém rótulo que a medição contradiz |

**Recomendo R1.** O piso portante é justamente o que o §4.43 chama de número que envelhece
em silêncio: ele faz duas curvas parecerem 2,5× melhores do que a física do modelo entrega,
e o custo de expor isso é **zero no censo**. R2 é aceitável e mais barata, mas deixa de pé
um número que ninguém sabe de onde veio.

⛔ **Não executo nenhuma das três** — mudança de config adotada exige assinatura (protocolo
do cron, passo 4). Fica na mesa com o número medido.

## 6. ⚠️ ERRATA DA MINHA PRÓPRIA §6 — a guarda que propus está ERRADA

> A 1ª versão desta seção propunha: *"`loose_arrest_floor` com procedência `lido-do-dado`
> tem de vir de uma leitura com `plateau=True`"*. **Medido depois de escrever, e a regra
> cai:** das **87** curvas com piso efetivo > 0, apenas **29 (33 %)** têm `plateau=True`
> no cru. ⇒ **`plateau=False` é a NORMA**, não a exceção — curva de afrouxamento
> digitalizada raramente termina em platô dentro da janela publicada. A guarda marcaria
> **dois terços de tudo** e seria ruído.

### 6a. O teste que DISCRIMINA é rótulo-contra-valor, não `plateau`

Restringindo aos grupos que **afirmam** ler do dado (`prov` contém `lido-do-dado`):

| | n |
|---|---:|
| curvas cujo grupo rotula o piso como `lido-do-dado` | **21** |
| valor **bate** com a leitura L24 (tol 0,02) | **12** |
| valor **não bate** | **9** |

E a **direção** do desvio separa as 9 em duas espécies com significados opostos:

| espécie | n | curvas | leitura |
|---|---:|---|---|
| piso **ABAIXO** da leitura | **7** | `SUN_2025` (0,08 contra L24 0,26–0,98) | **conservador** — o piso segura menos do que o dado permitiria; não infla nada |
| piso **ACIMA** da leitura | **2** | `ECCLES` `fig7d` (0,137 × 0,000) e `fig8a` (0,059 × 0,012) | ⚠️ **portante** — o piso segura o modelo acima do que o dado sustenta |

⇒ **o achado das §3–§4 SOBREVIVE e fica mais forte**, porque agora está calibrado: as
duas curvas do `ECCLES` são as **únicas duas de 21** cujo desvio de procedência aponta na
direção que **favorece o modelo**. Não é "um número diferente" — é o único par em que a
diferença compra métrica.

⚠️ **E a guarda certa muda de forma:** não "`plateau=True`", mas **"piso rotulado
`lido-do-dado` que fique ACIMA da leitura L24 do cru"** — 2 casos hoje, ambos no item R.
Um piso abaixo da leitura é escolha conservadora e não precisa de alarme.

## 7. O que isto ensina, além do `ECCLES`

**A auto-guarda existia e ninguém a leu.** `arrest_floor_from_curve` **já devolvia**
`plateau=False` para a `fig7d` em toda janela ≥0,10, e o `prefit.py` **já sabe** traduzir
isso para `"LIMITE INFERIOR — curva termina em queda"`. O número de 0,137 só pôde ser
gravado como *"assíntota final crua"* porque **a flag foi descartada no caminho entre ler e
adotar**.

⇒ guarda barata e óbvia: **`loose_arrest_floor` com procedência `lido-do-dado` tem de vir de
uma leitura com `plateau=True`.** É verificável contra o CSV, não precisa de simulação.
(Não a implemento aqui: seria mudar o gate de adoção, que também é assinatura.)

## Reprodutibilidade

```bash
# leitura honesta e varredura da janela de cauda
PYTHONPATH=src py -3.12 -c "
import sys; sys.path[:0]=['src','New_Theory']
from library_common import load_full_curve
from bolt_analysis_studio.calibration.provenance import arrest_floor_from_curve
cyc, r = load_full_curve('<csv da fig7d>')
for tf in (0.05,0.10,0.20,0.30,0.40):
    print(tf, arrest_floor_from_curve(r, tail_frac=tf))"
```

Sondas usam `load_full_curve` (CRU), `arrest_floor_from_curve` e `rh.sres_para_censo` —
nenhuma reimplementa regra. ⚠️ E nenhuma lê `metric_data`, que foi o erro de origem.
