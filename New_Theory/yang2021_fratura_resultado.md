# `YANG_2021` — fratura terminal: **ramo PIORA, candidato REPROVADO** (prereg `a4f00ad`)

**Data:** 2026-07-29 (noite) · **Store:** `3546e6745448` · sonda só-leitura
(`New_Theory/yang2021_fratura_probe.py`, dados em `yang2021_fratura_probe.json`).
**Nada foi adotado. Store e `adopted_configs.json` intocados.**

Gates congelados em `docs/superpowers/specs/2026-07-29-yang2021-fratura-prereg.md`
(commit `a4f00ad`) **antes** destas medições. Avaliados nas **5 curvas cegas**; a
`amp0p7mm` é de treino e não conta.

---

## 1. Veredicto por gate

| gate | critério | medido | |
|---|---|---|:--:|
| **G1** | zero do modelo a ≤ 5 % de `N_frat` em 6/6 | **6/6, erro 0,0 %** (uma a 2,9 %) | ✅ |
| G1b | *"§3 converge em ≤ 4 passadas"* | **não se aplica** — o método da §3 foi substituído (ver §2); a bisseção leva 12 | ⚠️ |
| **G2** | res.máx melhora em ≥ 4 das 5 **e** nenhuma piora > +0,01 | res.máx melhora **5/5**, mas **`amp0p5mm` piora o MAE +0,035** (janela cheia) e **4 das 5** pioram na janela da convenção | ❌ |
| **G3** | uma única `(D_on, q)` para as 6 | `0,75/16` vence em **4 das 5**; a `amp0p5mm` prefere `0,85/8` ⇒ a melhor forma **varia por curva** | ❌ |
| **G4** | ≥ 2 das 6 passam o tripé | **0/6** nas **duas** leituras de janela | ❌ |
| G5 | batch sem regressão | **não executado** — sem adoção, não há o que carimbar | — |
| **G6** | procedência gravada | `fat_C1` de cada curva junto do `N_frat` que o gerou, no JSON | ✅ |

**Ramo acionado: `PIORA`** — *"qualquer curva do acervo além de +0,01 ⇒ falha, com o
caso nomeado"*. Casos nomeados: `yang2021_amp0p5mm_ax8kN` (o pior, +0,165 de MAE na
convenção), `fig2_typical`, `amp0p8mm`, `amp0p6mm_r1`.

## 2. O anchor funciona — e a versão do prereg estava mal posta

O prereg propôs `C1 = Σ σ_ar(n)^{m1}` até `N_frat`, com 2 passadas. **Medido: não
fecha.** Com `C1 = 3,2574e33` na `amp0p7mm`, ligar a rampa faz F₀ cair nos últimos
15 % do dano ⇒ `σ_m` cai ⇒ `σ_ar` cai ⇒ a soma encolhe para 3,2081e33 ⇒
`D(N_frat) = 0,985 < 1` e **a fratura estaciona** (ratio parou em 0,5115). O ponto
fixo de `S` **não é** a raiz de `D = 1`; é o Goodman vivo se auto-realimentando.

Correção: bisseccionar a raiz de `f(C1) = S(C1)/C1 − 1`, com a monotonicidade
verificada em **2 pontos antes** (`f = 0,033` em 1e35 · `f = 0,985` em 3,2574e33) —
regra da campanha, o bug de bisseção-sem-direção já apareceu 2×. Resultado:
**6/6 com erro 0,0 %**, `C1` de 1,2e33 a 3,1e33, 12 passos de bisseção em log.

⚠️ Isto é **correção de instrumento, não afrouxamento de critério**: o critério
("o zero cai na vida medida a ≤5 %") é o do prereg, intacto. O sub-critério das
"≤ 4 passadas" descrevia o procedimento substituído e **não** pode ser reportado
como satisfeito.

## 3. O achado maior: `FLOOR_TRIM = 0.10` tira o colapso final de 43 curvas

Investigando por que o modelo "nunca zerava", apareceu que o `runner.py` carrega
uma **convenção pré-registrada da campanha**: pontos com `ratio < 0,10` saem da
métrica **e `n_max` passa a ser o último ponto sobrevivente**. Duas consequências,
as duas medidas:

1. **A simulação para ANTES de `N_frat`** ⇒ a fratura é inobservável pelo runner. Era
   isto que quebrava o G1, não a álgebra.
2. **A fase final do colapso está fora do escopo da métrica em 43 das 203 curvas**
   (588 pontos, 13 fontes): `ECCLES_2010` 56 pts · `ANCORA_INTERNA` 449 · `LU_2024` 24 ·
   `SUN_2025_CRIMP` 12 · `LIU_2025` 10 · `ZHANG_2006` 9 · `BAUER_2024` 9 · `YANG_2021`
   6 · `YANG_2023_IJPEM` 6 · outras 4 fontes com 1–3.

⇒ *"o modelo não pega a queda no final"* tem **duas camadas**: abaixo de 10 % da
pré-carga **nada é pontuado, em nenhuma curva do acervo**, por convenção; e no
`YANG_2021` o trim da fonte tira mais 39–83 pontos percentuais acima disso.

## 4. Números (janela da CONVENÇÃO, `FLOOR_TRIM=0,10`, sem o trim da fonte)

| curva | sem fadiga | com fadiga ancorada (`0,75/16`) | Δ |
|---|---|---|---|
| `fig2_typical` | 0,0989 / 0,1625 / 0,0753 | 0,1443 / 0,4266 / 0,0951 | pior |
| `amp1p0mm` | 0,0760 / 0,3098 / 0,1021 | **0,0653 / 0,1576 / 0,0425** | melhor |
| `amp0p8mm` | 0,0993 / 0,1642 / 0,0862 | 0,1164 / 0,2707 / 0,0614 | misto |
| `amp0p6mm_r1` | 0,0731 / 0,5067 / 0,1408 | 0,0990 / 0,4011 / 0,1233 | misto |
| `amp0p7mm` *(treino)* | 0,0510 / 0,3715 / 0,0997 | 0,0506 / 0,2592 / 0,0898 | melhor |
| `amp0p5mm` | 0,0649 / 0,1850 / 0,0756 | 0,2297 / 0,7508 / 0,2511 | **muito pior** |

Na **janela cheia** (incluindo o ponto `y = 0,000`, fora da convenção) o mecanismo
parece muito melhor — res.máx cai de 0,68–0,86 para 0,16–0,45 em **5/5** — mas essa
janela não é comparável ao número publicado. As duas leituras concordam no que
decide: **0/6 passam o tripé**.

## 5. Por que ele falha, e por que isso não é surpresa

O mecanismo está **certo em espécie** (a curva termina onde o dado termina, com o
canal `fatigue` carregando 34 % da perda) e **errado em forma**: casar um colapso
quase vertical **ponto a ponto** faz o res.máx explodir com poucos por cento de erro
de relógio. Na `amp0p7mm`, **2 % em `C1`** move o res.máx de 0,0526 para 0,1949.

Isto **reproduz de forma independente** a conclusão já registrada em §4.44–§4.48a
(linha de métrica do Liu 2025, 4 tentativas / 4 mortes por gate): *"nenhuma métrica
automática sobre curvas digitalizadas esparsas distingue rampa de cliff no
colapso"*. O `YANG_2021` chega ao mesmo veredicto por outro caminho — o que reforça
a classe **metric-limited** em vez de sugerir que ela era preguiça de método.

### Consequência que corrige a leitura crítica dos trims

Eu havia escrito *"é o trim que aprova aquela curva"* com tom de denúncia. O tom
estava errado, e a medição é que corrige: modelar o colapso, com a vida **lida do
próprio dado** e a forma da rampa **compartilhada**, deixa as métricas **piores** em
4 das 5 cegas. O trim é a maneira **registrada** de tratar um trecho
*metric-limited*, com exceção assinada — não um artifício para inflar o número. O
que permanece verdadeiro é o **caveat**: a `amp0p7mm` passa o tripé sobre 11 de 14
pontos, e isso deve ser dito quando o número for reportado.

## 6. O que fica de reutilizável

1. **O anchor por bisseção de `D(N_frat) = 1`** — instrumento válido (6/6, 0,0 %) para
   qualquer fonte com fratura medida. É leitura da vida, não fit.
2. **O censo do `FLOOR_TRIM`** (43 curvas / 588 pontos / 13 fontes) — número que não
   existia e que muda como se lê "o modelo não pega o fim".
3. **A confirmação cruzada da classe metric-limited**, agora com duas fontes
   independentes (`LIU_2025` por 4 gates, `YANG_2021` por este).
4. **A dívida do `D_on`/`q` fica registrada como não-ancorável por esta via:** a melhor
   forma varia por curva dentro da mesma fonte (G3), o que é assinatura de ajuste
   per-curva, não de física compartilhada.

## 7. Reprodutibilidade

```bash
py -3.12 New_Theory/yang2021_fratura_probe.py            # 6 curvas, 2 formas
py -3.12 New_Theory/yang2021_fratura_probe.py --quick     # 2 curvas
```
