# As "réplicas" tiveram a mesma condição? — estudo medido, 2026-08-23

**Pedido do professor:** *"conduza um estudo das réplicas, para ver se as mesmas condições
foram aplicadas"*. Só-leitura, nada adotado. Fingerprint `db7de97e682a`, censo **171/205**.

---

## 1. Resposta curta

**Não, na maioria.** De **22 pares que se declaram réplica** (sufixo `repN`/`rN`/
`baselineN`/`repeat`/`runN`, ou par declarado), **apenas 1 se comporta como réplica
genuína**. Mas a causa **não é uma** — são **três**, com consertos diferentes, e uma delas é
**artefato da nossa métrica**, não do experimento.

## 2. O discriminante

Réplica verdadeira **cruza** a irmã e a diferença vagueia. Condição diferente mantém **sinal**
e/ou **cresce** com os ciclos. Medido par a par na janela comum (60 pontos):

- `offset` = `|média(d)| / média(|d|)` — **1,0 = diferença de sinal único** (sistemática)
- `ρ(d, N)` de Spearman — **|ρ| > 0,7 = a diferença CRESCE** (taxa diferente)

| veredito | pares | leitura |
|---|---:|---|
| **SISTEMÁTICO + CRESCE** | **15** | taxa diferente ⇒ condição diferente |
| SISTEMÁTICO constante | 4 | ponto de partida diferente |
| misto | 2 | — |
| **CRUZAM** (réplica genuína) | **1** | espalhamento aleatório |

⚠️ **Este recorte exigiu um filtro que a 1ª medição não tinha.** Rodando sobre *todas* as
famílias eu obtive 223 pares e 81 % sistemáticos — número **inflado**, porque a maior família
(`LIU_2022_RETIGHT`, 18 membros) são **estágios de reaperto** t0…t4, que o `CLAUDE.md` declara
serem *"o MESMO ensaio numa cadeia"*. Entre estágios, "sistemático e crescente" é **esperado e
correto**: t4 tem mais dano acumulado que t0. Publicar os 81 % teria sido medir a coisa errada.

## 3. ⚠️ Causa 1 — DURAÇÃO diferente, e o erro é da métrica

Comparei a banda de cada condição em **ciclo absoluto** (o que a métrica faz) e em **vida
normalizada** (`x/x_fim`, cada curva na sua própria fração de vida):

| condição | razão de duração | banda em ciclo | banda em vida | artefato |
|---|---:|---:|---:|---:|
| `BAUER_2024` (6) | 2,0× | **0,5201** | **0,1822** | **65 %** |
| `BAUER_2024` (3) | 1,5× | 0,3840 | 0,1360 | **65 %** |
| `CHU_2026` | 1,3× | 0,0989 | 0,0365 | **63 %** |
| `LIU_2025` | 1,5× | 0,7184 | 0,3261 | **55 %** |
| `CACCESE` · `ECCLES` · `LIU_2017` | 1,0–1,3× | — | — | ~0 % |

⇒ em **4 das 15** condições, **55–65 % da banda é artefato de duração**: as curvas rodaram
comprimentos diferentes e a métrica as compara no **ciclo absoluto**, onde a mais curta já
terminou e a mais longa está no meio da vida.

**Nas frações iguais de vida o espalhamento do BAUER é estável e pequeno:**

| fração da vida | 25 % | 50 % | 75 % | 100 % |
|---|---:|---:|---:|---:|
| espalhamento | 0,143 | 0,168 | 0,141 | 0,137 |

⇒ o espalhamento real de espécime no BAUER é **~0,15**, não **0,52**.

### ⚠️ Isto corrige o que EU escrevi há uma hora

No `robustez_rotas_medidas.md` publiquei *"o BAUER gasta 34 constantes num dado cuja banda é
0,459"*. A banda **irredutível** é ~0,15–0,18. O argumento de sobre-gasto **enfraquece** (34
constantes para 9 curvas ainda é muito, mas não é "gastar em ruído de 0,46"). Errata
registrada lá.

## 4. Causa 2 — famílias que não são réplicas em sentido nenhum

| condição | razão de duração |
|---|---:|
| `ZHANG_2018` (7) | **666×** (1 041 → 693 750 ciclos) |
| `ZHANG_2019` (4) | 194× |
| `LIU_2016` (2) | 5,0× |
| `LI_2022_TRIBOINT` (2) | 2,0× |

Sete curvas com duração de **1 041 a 693 750 ciclos** não são réplicas — são **ensaios de
comprimentos diferentes** agrupados porque a chave de família é **cega à duração**. A banda
delas não é piso de repetibilidade de nada.

⚠️ **Inócuo no censo hoje** — os pisos dessas fontes ficam abaixo de `META_SRES` (ZHANG_2018:
0,0056), então o `max()` os ignora e o limite segue 0,0250. Mas é família que não deveria
existir, e num dado com piso maior isso afrouxaria a barra.

⚠️ **E aqui a métrica de artefato da §3 NÃO VALE:** normalizar vida só faz sentido com
durações comparáveis. "50 % da vida" entre 1 041 e 693 750 ciclos não é um estado físico
comum, e é por isso que essas linhas dão artefato **negativo** (a banda *cresce* ao
normalizar). O instrumento vale até ~3× de razão; além disso ele mede ruído. Declarado, não
publicado como achado.

## 5. Causa 3 — e um achado de RÓTULO no BAUER

As durações do `BAUER fig6` são **perfeitamente ordenadas pelo índice do rótulo**:

| | rep1 | rep2 | rep3 | rep4 | rep5 | rep6 |
|---|---:|---:|---:|---:|---:|---:|
| duração [ciclos] | 150 | 190 | 206 | 248 | 269 | 300 |

**ρ = +1,000, p = 0,0000.** Sob espalhamento aleatório, seis durações saírem ordenadas tem
probabilidade 1/720.

⇒ **`repN` não é identidade de espécime — é um RANK.** Quem digitalizou nomeou as curvas em
ordem (de comprimento, ou de posição na figura). A nota de aparato chama de *"specimen
scatter"*, o que está certo **em espécie**, mas os rótulos carregam a ordenação e portanto o
conjunto **não é permutável**.

⚠️ **E foi isso que me enganou primeiro:** medi "retenção final" na janela comum e achei
ρ = +0,943 (p = 0,005), concluindo *"as réplicas estão ordenadas por taxa"*. **Falso** — nos
dados **crus**, nem o valor inicial (p = 0,47) nem o final (p = 0,32) são ordenados. O que é
ordenado é a **duração**, e avaliar todas no fim da mais curta transfere essa ordem para a
retenção aparente.

## 6. O que isto sugere fazer (nada executado)

**(a) Guarda por razão de duração, não mudança de chave.** Marcar como **não-comparável para
piso** qualquer família com razão de duração > 3×. Isso barra `ZHANG_2018` (666×),
`ZHANG_2019` (194×) e `LIU_2016` (5×) sem tocar nas famílias legítimas.

⚠️ **Por que NÃO pôr duração na chave:** duração é **ALCANÇADA** quando o ensaio corre até um
critério (o caso do BAUER, que para quando a pré-carga cai) e **AJUSTADA** quando corre um
número fixo de ciclos. É a mesma distinção que hoje matou `initial_preload_N` na chave —
grandeza alcançada na chave destrói pareamento legítimo.

**(b) Publicar a banda em VIDA NORMALIZADA ao lado da banda em ciclo,** para famílias com
razão ≤ 3×. É o que separa "espécimes diferem" de "os ensaios tiveram comprimentos
diferentes", e hoje o piso publicado mistura as duas.

**(c) Registrar que `repN` do BAUER é rank.** Enquanto o rótulo carregar a ordem, qualquer
estatística que assuma permutabilidade (média, centro, banda) está mal-posta ali.

**(d) Reler o §3 de `robustez_rotas_medidas.md`** com a banda corrigida: das 4 fontes que eu
apontei como "constante gasta em ruído", **2 eram artefato de duração**.

## 7. Reprodutibilidade

```bash
py -3.12 New_Theory/replicas_verdadeiras.py    # os 22 pares declarados replica
py -3.12 New_Theory/duracao_artefato.py        # banda em ciclo x em vida normalizada
```

Famílias pela chave de `_pisos_medidos`; pares filtrados por sufixo de réplica **ou**
`_PARES_REPLICA_DECLARADOS`. A §3/§4/§5 lê a **CSV crua** via `load_full_curve` com
`(x−offset)·scale` — **não** `metric_data`, porque o `FLOOR_TRIM` corta a cauda e mascararia
justamente a duração.
