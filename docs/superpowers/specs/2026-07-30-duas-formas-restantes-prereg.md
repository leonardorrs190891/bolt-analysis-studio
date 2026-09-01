# PRÉ-REGISTRO — as duas formas restantes da classe "taxa dependente do estado acumulado"

**Escrito em 2026-07-30, ANTES de medir.** Congelado no commit que o introduz;
os discriminantes da §3 são **imutáveis** depois dele.

**Por que existe:** a regra de parada (`New_Theory/regra_de_parada_proposta.md`)
exige, no requisito (b), que *todo membro enumerado da classe seja falsificado por
predição pré-registrada* antes de a campanha parar. A classe tem quatro membros;
dois já foram medidos (`graded_scrit` = componente; incubação `slip_onset_W` =
**falsificada**) e **dois nunca foram sondados**. Este prereg cobre os dois.

## 1. População: as 18 curvas FORM-LIMITED (não as 98)

A triagem de 2026-07-30 mostrou que das 98 fora do tripé, **44 são exceção
assinada**, 21 são metric/data-limited e 15 indecidíveis. A fila legítima é **18**,
com distância **mediana de 9 %** no σ_res (máx. 47 %); 3 delas já têm σ_res dentro
e reprovam só no MAE, e 9 das 18 violam o MAE.

Fontes: `LIU_2025` ×4 · `LIU_2016` ×4 · `LIU_2022_RETIGHT` ×3 · `ZHANG_2018` ×3 ·
`LI_2022_TRIBOINT` ×2 · `YANG_2021` ×2.

## 2. As realizações no engine (ambas default-inertes)

| classe | realização | inerte por | por que esta |
|---|---|---|---|
| **kernel desacelerante** | `creep_mode="saturating"` + `creep_t_c > 0` (`creep_alpha_sat` molda) | `creep_mode=""` | troca a lei log-t **ilimitada** por `δ_max·(1−e^{−(t/t_c)^α})`, **limitada**: a taxa desacelera até parar. É literalmente um kernel desacelerante |
| **bifurcação de limiar** | `slip_regime_mode="cattaneo_mindlin"` + `slip_capacity_coeff` κ | `"off"` | bifurca partial↔gross slip na capacidade `cap = µ·F₀·κ`; e como `cap ∝ F₀`, a curva pode **cruzar o limiar durante o ensaio** ⇒ redistribui perda no tempo, que é a definição da classe |

⚠️ **`W_crit` foi DESCARTADO como realização, por medição prévia:** ele gateia o
*crescimento do dano*, e `c_D = 0` nas **seis** fontes da fila ⇒ multiplica um canal
que carrega exatamente zero ⇒ **inerte por construção**. É a classe
*alavanca-que-multiplica*, decidível pela decomposição (gotcha do `CLAUDE.md`).
Registrado aqui para não ser re-sondado como se fosse candidato vivo.

## 3. DISCRIMINANTES — imutáveis a partir deste commit

Cada candidato tem de **acertar seu discriminante**, não apenas mover o número. Foi
essa exigência que matou a incubação com proveito: lá, 68 % de redução de `|a|` numa
curva teria passado por confirmação sem o discriminante.

### D1 · kernel desacelerante

**Mecanismo alegado:** o creep saturante perde **menos** no fim do ensaio que a lei
log-t (em `t/t_c ~ 10³–10⁵`, `ln` dá ~11× o teto), então o modelo **retém mais**
pré-carga tarde.

**Predição:** a melhora tem de se concentrar nas curvas em que **(i)** o canal de
creep carrega fração não-trivial da perda **e (ii)** o resíduo **tardio é negativo**
(`e_late < 0` = modelo abaixo do dado no fim = perdendo demais tarde). Tem de ser
**inerte** onde o canal de creep ≈ 0.

**PASSA o discriminante se:** a melhora média de σ_res nas curvas com
`(creep ≥ 5 %) E (e_late < 0)` exceder a das demais em **≥ 15 pontos percentuais**,
**e** as curvas com creep < 5 % ficarem dentro de ±0,002 em σ_res.

**FALSIFICADO se:** melhora curvas com `e_late > 0`, ou melhora onde o creep ≈ 0, ou
a diferença entre os dois grupos ficar abaixo de 15 pp.

### D2 · bifurcação de limiar

**Mecanismo alegado:** abaixo de `cap = µ·F₀·κ` o slip é parcial (wear/fretting
gateados para baixo); acima, é bruto. A transição depende de `F₀`, que **cai** ao
longo do ensaio.

**Predição:** a melhora tem de **ordenar pela proximidade do limiar** — medida por
`r = F_amp/cap` no 1º ciclo. Curvas com `r` perto de 1 (transição dentro do ensaio)
melhoram; curvas com `r ≫ 1` (gross slip profundo do início ao fim) ficam
**inertes**.

**PASSA o discriminante se:** a correlação de Spearman entre `|log r|` e a melhora
de σ_res for **≤ −0,5** (mais perto do limiar ⇒ mais melhora), **e** as curvas com
`r > 5` ficarem dentro de ±0,002.

**FALSIFICADO se:** melhora uniforme (|ρ| < 0,3), ou melhora ordenada ao contrário,
ou melhora as de `r > 5`.

## 4. Gates de mérito (além dos discriminantes)

| # | critério |
|---|---|
| **G1** | ≥ 1 curva das 18 **fecha o tripé** (passa as três pernas) |
| **G2** | nenhuma curva do acervo piora > **+0,01** em qualquer perna (PR-37′) |
| **G3** | a melhora **não** é troca: `Δσ/ΔMAE ≥ 1` onde o σ melhora |
| **G4** | uma única parametrização por FONTE (não por curva) — se o melhor valor variar por curva dentro da fonte, é fit |

## 5. Ramos de decisão

- **PASSA** — discriminante acertado **e** G1–G4 ok ⇒ propor adoção gateada.
- **COMPONENTE** — discriminante acertado, G1 falha ⇒ registrar como componente
  (mesmo destino do `graded_scrit`), não adotar sozinho.
- **FALSIFICADO** — discriminante errado ⇒ **morto**, mesmo que as métricas melhorem.
  O número bonito sem o mecanismo é ajuste.
- **INERTE** — Δ = 0 exato ⇒ classificar em (a) campo inexistente / (b) gate de modo
  / (c) canal morto, e dizer qual.

## 6. Consequência para a regra de parada

Se **ambos** forem FALSIFICADOS ou INERTES, o requisito (b) da regra passa a estar
satisfeito para esta classe: os 4 membros enumerados terão sido medidos. Junto com o
requisito (c) — que pede 3 candidatos com predição pré-registrada e retorno marginal
nulo, e este prereg fornece o 2º e o 3º — **a regra poderá disparar**, e a
recomendação passará a ser: declarar a classe exaurida e mover o limite do σ_res para
**por fonte** (capacidade já construída, `_SRES_POR_FONTE`, hoje inerte).

Se **qualquer um** passar, a classe segue viva e a parada não se aplica.

## 7. Reprodutibilidade

```bash
py -3.12 New_Theory/duas_formas_probe.py [--quick]
```
