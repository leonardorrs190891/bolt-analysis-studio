# "Curvatura" não é uma classe — são **duas, de sinal oposto**

**2026-08-09** · só-leitura · **nada adotado** · explica por que **todo**
candidato de curvatura falhou.

## O que se sabia, e o que faltava

O `sigma_res_decomposicao_por_estagio.md` (2026-07-29) estabeleceu que o defeito
dominante é **curvatura**: nas 84 curvas em que o σ manda, **63 % trocam de
sinal** ao longo do ensaio, e **59,7 %** da variância está **entre** estágios.
Desde então a campanha tratou isso como **uma** classe e testou candidatos contra
ela — `graded_scrit`, kernel desacelerante, Cattaneo–Mindlin, `arrest_approach_exp`.
**Todos falharam.**

Faltava perguntar se a classe é homogênea.

## Não é. Medida a forma do resíduo, ela se parte em duas

Critério: σ **manda** (é a perna de maior múltiplo) **e** o resíduo troca de
sinal. Dá **15 curvas**. Separadas pelo sinal de `r(3/3) − r(1/3)`:

### A — modelo **rápido cedo, devagar tarde** (resíduo sobe) — **10 curvas**

| curva | fonte | r 1/3 | r 3/3 | σ× |
|---|---|---:|---:|---:|
| `liu2025_fig2_single` | LIU_2025 | −0,008 | +0,054 | **1,07×** |
| `yang2019_amp0p6_10Hz` | YANG_2019 | −0,031 | +0,034 | 1,40× |
| `jcsr2023_plain_seawater` | JCSR_2023 | −0,027 | +0,025 | 1,48× |
| `jcsr2023_galv_seawater` | JCSR_2023 | −0,044 | +0,043 | 1,87× |
| `yang2019_varamp` ×2 | YANG_2019 | −0,043/−0,064 | +0,077/+0,101 | 2,32/3,21× |
| `chu2026ti_test7`/`test8` | CHU_2026 | −0,195/−0,158 | +0,181/+0,269 | 3,30/3,80× |
| `yang2019_amp0p6_5Hz` | YANG_2019 | −0,055 | +0,190 | 6,14× |
| `eccles2010_fig6_4kN` | ECCLES_2010 | −0,287 | −0,035 | 7,55× |

### B — modelo **devagar cedo, rápido tarde** (resíduo desce) — **5 curvas**

| curva | fonte | r 1/3 | r 3/3 | σ× |
|---|---|---:|---:|---:|
| **`eccles2010_fig7c`** | ECCLES_2010 | **+0,010** | **−0,022** | **1,03×** |
| `liu2025_M16_amp0p8` | LIU_2025 | +0,036 | −0,014 | 1,58× |
| `eccles2010_fig7d` | ECCLES_2010 | +0,029 | −0,083 | 2,26× |
| `jcsr2023_stainless_seawater` | JCSR_2023 | −0,023 | −0,100 | 2,96× |
| `sun2025..._grease_standard` | SUN_2025_CRIMP | +0,027 | −0,174 | 4,73× |

## ⚠️ O controle que descarta artefato de fonte

O **`JCSR_2023` aparece nas duas**: `plain` e `galv` na **A**, `stainless` na
**B**. Mesmo rig, mesmo protocolo, mesma campanha de ensaio — e defeitos de
**sinal oposto** conforme o **material**.

Isso é decisivo: se a divisão fosse artefato de digitalização, de aparato ou de
config por fonte, ela não apareceria **dentro** de uma fonte. O `LIU_2025` e o
`ECCLES_2010` também se dividem.

## O que isto explica

**Por que todo candidato de curvatura falhou.** Cada um foi medido contra uma
população que **contém o próprio oposto**: uma forma que acelera o início
conserta a A e piora a B, e vice-versa. Com 10 contra 5, um candidato "bom para
A" seria reprovado no G2 pelas 5 da B, e um "bom para B" nem chegaria ao gate.

É a mesma armadilha que o `classe_parada_discriminante` expôs em 2026-08-06 — um
critério **cego ao sinal** juntando defeitos opostos —, agora um nível acima: na
própria classe que a campanha elegeu como o gargalo.

## O que isto muda no método

> **Nenhuma forma de curvatura deve ser proposta para "a classe". Ela é proposta
> para A ou para B, e é medida SÓ contra a sua.**

E o alvo mais barato de cada lado já está identificado, os dois a ~1 % do limite:

| sub-classe | curva mais próxima | σ× | MAE× | res.máx× |
|---|---|---:|---:|---:|
| **A** | `liu2025_M16_fig2_single` | **1,07×** | 0,55 | 0,57 |
| **B** | **`eccles2010_fig7c`** | **1,03×** | 0,50 | 0,61 |

Nas duas, as outras pernas têm folga de ~2×: qualquer forma que corrija a
curvatura **no sinal certo** as fecha.

## ⚠️ O que NÃO está estabelecido

Que exista uma **causa física** distinta por trás de cada sinal. O split é
**fenomenológico** — medido no resíduo. A hipótese natural (A = o modelo satura
cedo demais; B = o modelo arresta tarde demais) é plausível e **não testada**.
O `fig7c` dá uma pista para a B: o rotacional arresta no piso e o **embedding
continua descendo depois** (`fig7c_ataque_resultado.md`).

## Reprodutibilidade

Sonda no scratchpad: filtra por *σ manda* + *troca de sinal*, normaliza o
resíduo por amplitude e abscissa, e separa pelo sinal de `r(3/3) − r(1/3)`.
Segundos.
