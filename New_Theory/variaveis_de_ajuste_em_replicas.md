# Como representar as variáveis de ajuste em ensaios com réplica — medido, 2026-08-25

**Pergunta do professor.** Só-leitura, nada adotado. Fingerprint `db7de97e682a`, censo
**171/205**.

---

## 1. Resposta curta

**A distinção que importa não é per-curva × per-condição — é PROCEDÊNCIA.** Um número por
curva **lido do paper** é legítimo; um número por curva **ajustado naquela curva** é fit. Os
dois existem hoje e são **estruturalmente indistinguíveis**: `per_case` tem **200 entradas
(token, campo)** e **147 sem procedência nenhuma**.

## 2. As quatro representações, com custo em DOF

| # | representação | DOF | falsificável? | onde já existe |
|---|---|---|---|---|
| **A** | **input medido por espécime** | **0** | sim — o input é conferível contra o paper | `fat_C1` do `LIU_2025` (N_f lido), `emb_um`, `free_spin_kin` |
| **B** | **constante por CONDIÇÃO** + espalhamento declarado | 1 / condição | sim — contra a banda | **9 das 15** condições com réplica |
| **C** | **hierárquico** `θ_ij = θ_cond + δ_ij`, `δ ~ N(0, σ_θ)` | 2 / família | **sim, e é a virtude** | **não implementado** |
| **D** | **constante por CURVA** | N | **não, por construção** | **10 grupos, 2 fontes** |

**Por que D é inaturalizável dentro da condição:** uma constante ajustada numa curva tem
exatamente **um** dado para explicar. Ela não pode errar. Já o `σ_θ` de C é um número que
**tem de bater com a banda observada** — se não bate, a representação está errada e o
projeto fica sabendo.

## 3. O que a medição diz de cada uma

### A — input medido: só onde a digitalização preservou, e onde preservou NÃO explica

O candidato natural é o **aperto alcançado por espécime** (`y[0]` da CSV crua) — o que a
nota do BAUER chama de *"tightening scatter, start values 0.93–1.08"*.

| fonte | `y[0]` medido | conclusão |
|---|---|---|
| `LIU_2017_AXIAL` | **1.000000 exato** nas 5 | normalizado fora **na digitalização** |
| `ZHANG_2018` · `ZHANG_2019` | spread 0,0000 | idem |
| `BAUER_2024` (6) | 0,9897 … 0,9298 (**spread 0,145**) | preservado |

E onde foi preservado, ele **não explica a banda**: correlacionando o desvio de cada réplica
contra o desvio do seu `y[0]`, **r² = 0,006** para uma banda de 0,520.

⇒ **A rota "representar o espalhamento como input medido" está fechada nos dados que temos.**
Nas fontes onde ela seria testável, o número foi normalizado fora; onde sobreviveu, não
explica.

⚠️ **Duas linhas da minha tabela original eram artefato e foram retiradas:** `YANG_2021`
deu r² = 0,999 com **n = 3** e a correção **piorou** a banda (0,524 → 0,557) — regressão
ajustando ruído; e `LIU_2022_RETIGHT` deu r² = 0,805, mas ali `y[0]` varia porque **cada
estágio começa num nível retido diferente** — é o mecanismo `chain: "retight"` funcionando,
não achado.

### B — já é a norma, e eu havia publicado o contrário

**9 das 15** condições com réplica **já compartilham** todas as constantes:
`CACCESE_2009` · `CHU_2026` · `LIU_2016` · `LIU_2017_AXIAL` · `LI_2022_TRIBOINT` ·
`LU_2024` · `YANG_2021` · `ZHANG_2018` · `ZHANG_2019`.

As que diferem, e o que difere:

| condição | grupos | campos que diferem | é fit? |
|---|---:|---|---|
| `BAUER_2024` (6) | **6** | `tr_loose_gain` | **sim** |
| `BAUER_2024` (3) | 1 | `k_loose_graded`, `s_crit_loose` | sim (via `per_case`) |
| `ECCLES_2010` (4) | **4** | `arrest_approach_exp`, `loose_arrest_floor`, `tr_loose_gain` | **sim** |
| `LIU_2020_WEAR` (3) | 1 | `mu`, `mu_thread`, canal de flanco | sim |
| `LIU_2022_RETIGHT` (18) | 4 | `c_D`, `k_emb_renew`, `retight_loss_base` | **não — são ESTÁGIOS** |
| `LIU_2025` (2) | 1 | `fat_C1` | **não — N_f LIDO do paper** |

### C — a única que torna o espalhamento falsificável

Não implementada. É a forma estatística padrão para réplica: **uma** constante da condição
mais **uma** dispersão da família. Custo: 2 números onde hoje o BAUER gasta 6. Ganho que
nenhuma das outras dá: `σ_θ` é **conferível contra a banda medida** — e a banda certa do
BAUER é **0,18** (vida normalizada), não 0,52 (ciclo absoluto), pelo artefato de duração já
medido.

### D — legítima SÓ com procedência

O `fat_C1` do `LIU_2025` é per-curva e **legítimo**: é a vida `N_f` **lida do paper** para
aquela curva, adotada na rota E2. O `tr_loose_gain` do `BAUER` é per-curva e é **fit**. Hoje
os dois moram no mesmo dict, com a mesma forma, e **quem conta DOF conta os dois igual**.

## 4. ⚠️ Errata de um número meu do ITEM Z

Publiquei *"40 grupos servem exatamente 1 curva"* como evidência de fit por curva. Medido
com o discriminante certo:

| | |
|---|---:|
| grupos que servem exatamente 1 curva | **37** |
| …cuja curva **tem irmã de réplica** ⇒ **fit por réplica** | **10** |
| …cuja curva está **sozinha na condição** | **27** |

**Um config para uma condição de n=1 não é fit por réplica — é um config para uma
condição.** O fit por réplica real são **10 grupos em 2 fontes**: `BAUER_2024_fig6_rep1..6`
e `ECCLES_2010_{fig3, fig7a, fig8a, fig8c}`. A estrutura é bem menos fit-like do que eu
publiquei.

## 5. A proposta concreta, e é barata

**Marcar procedência POR TOKEN em `per_case`** — `input` (medido/lido para aquela curva) ×
`fit` (ajustado nela). Três consequências:

1. o report pode publicar **"N constantes fitadas"** separado de **"N inputs por espécime"**
   — hoje é o mesmo número, e é por isso que o DOF publicado exagera;
2. o gate de adoção pode exigir que **todo token novo declare classe**, o que é a versão
   estrutural da regra que o projeto já aplica em prosa;
3. as 147 entradas sem procedência viram uma dívida **contável**, com alvo.

## 6. Recomendação por caso, em ordem de retorno

| caso | representação | por quê |
|---|---|---|
| `BAUER fig6` (6 grupos, `tr_loose_gain` por réplica) | **C** (θ_cond + σ_θ) | `y[0]` não explica (r²=0,006); σ_θ conferível contra a banda **0,18** em vida normalizada |
| `ECCLES` (4 grupos sem axial) | **B ou C** | mesma condição nominal, 4 configs — mas ⚠️ 2 delas acabaram de fechar pelo `arrest_approach_exp` **por protocolo**, então mexer aqui pede prereg |
| `LIU_2020_WEAR` (3) | **B** | difere em μ e canal de flanco entre curvas da mesma condição |
| as **9** que já compartilham | nada | já estão em B |
| `LIU_2022_RETIGHT` · `LIU_2025` | nada | estágios e input lido — não são fit |
| fontes com `y[0]` normalizado fora | registrar | é perda de dado **na digitalização**, e fecha a rota A ali |

## 7. Reprodutibilidade

Sondas só-leitura sobre `kb.adopted_config()` (nunca o JSON direto), `rn._adopted_for` para
atribuir grupo, `rh.condicoes_agregadas` para as famílias, e `load_full_curve` com
`(x−offset)·scale` para o `y[0]` **cru** — nunca `metric_data`, que é pós-`FLOOR_TRIM` e
pós-alinhamento e não preserva o aperto alcançado.
