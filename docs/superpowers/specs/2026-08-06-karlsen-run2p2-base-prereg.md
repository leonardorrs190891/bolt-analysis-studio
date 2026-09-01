# Prereg — base da `karlsen2022_M30_HV_run2p2` + convergência do `k_ratchet` (D-Y)

**2026-08-06 (noite)** · classe **dado + input + parcimônia**, molde D-X ·
gates escritos ANTES da execução · fingerprint `5916d8be0510` (não muda —
registry e CSV ficam fora do hash ⇒ **validar re-simulando**).
Premeasure: `karlsen_run2p2_premeasure.{py,json}` · falsificação anterior:
`karlsen_run2p2_sonda_resultado.md`.

## O defeito

A CSV, multiplicada pelo F₀ = 312 do registry, dá valores **redondos** —
300 / 250 / 200 / 150 / 90 / 38 kN. O digitalizador leu **cruzamentos de linha
de grade** e **ancorou o ciclo 1 no F₀ nominal do registry** em vez de ler o
valor da figura. Na Fig. 10 a laranja no ciclo 1 está em:

| instrumento | valor |
|---|---:|
| subagente D-X (raster, atribuição por swatch da legenda) | **332,7 kN** |
| esta sessão (topo do traço, x = 127) | **332,0 kN** |
| idem, corrigida pelo viés dos controles (−2,7 kN) | **329,3 kN** |

Controles lidos na **mesma coluna x**, o que prova que ela é o ciclo 1:
`run7.1` → 313,15 vs registry 312 (**+0,4 %**) · `run6.2` → 339,39 vs 340
(**−0,2 %**). Calibração y por 17 gridlines, resíduo máx. **0,48 kN**;
calibração x conferida contra as VIBRALOCK (CSVs terminam em 3080; extração
dá 3186 no último pixel).

⇒ base verdadeira em **329–333 kN** contra **312**: **+5,5 a +6,6 %**.

## A transformação — e por que ela NÃO precisa de re-extração

O ciclo em que a curva cruza um nível de kN **não depende do F₀ assumido**.
Os 6 pontos do meio já são leituras válidas; só o **divisor** muda:

```
novo_ratio(ciclo 1) = 1,0                     (por definição)
novo_ratio(demais)  = antigo × (312 / base)
```

⚠️ **Instrumento declarado insuficiente para o meio da curva:** pixels
**amarelos anti-serrilhados** (`run 6.2` misturado com branco) caem mais perto
do laranja que do amarelo puro e contaminam o traço — numa coluna aparecem
223 kN e 123 kN juntos. Por isso a correção usa a leitura-por-nível da CSV
original, não uma re-digitalização. Declarado para que ninguém leia a
concordância como validação do meio.

## A hipótese de PARCIMÔNIA (o que de fato se testa)

Registrada em `karlsen_run2p2_sonda_resultado.md` **antes** da grade: corrigida
a base, o `k_ratchet` que a curva pede **sobe rumo aos 0,005 da `run7p1`**.

Premeasure (grade 5 bases × 6 valores, `limite_sres(KARLSEN)` = **0,0845**):

| base | melhor `k_ratchet` | MAE | mx | σ |
|---:|---:|---:|---:|---:|
| 312 (atual) | 0,0030 | 0,0488 | 0,0922 | 0,0548 |
| 329,3 | 0,0050 | 0,0377 | 0,0753 | 0,0384 |
| 331,0 | 0,0050 | 0,0348 | 0,0660 | 0,0372 |
| 332,7 | 0,0050 | 0,0319 | 0,0569 | 0,0364 |
| 334,0 | 0,0050 | 0,0297 | 0,0631 | 0,0359 |

**Em 312 o ótimo é 0,003 e subir piora monotonicamente; em TODAS as bases
corrigidas o ótimo migra para 0,0045–0,0050.** Oito células passam o tripé,
todas nesse intervalo. Adota-se **`k_ratchet` = 0,005** — o valor **já
adotado** da `run7p1` — e não o mínimo de MAE (0,0045), pela mesma regra do
D-I: escolher pelo MAE é o que o gate proíbe; escolhe-se a que **compartilha**.

Resultado: **um parâmetro a menos** — as duas entradas per-espécime viram
**uma exceção de CLASSE** com valor único.

## ⚠️ Acoplamento: a `run2p2` é METADE do par que sustenta o piso da fonte

`limite_sres(KARLSEN)` = 0,0845 vem de **uma única família**, `F = 124 800 N`
(= 0,4 × 312 000), com n = 2: o par é **`run2.2` ↔ `run7.1`**. Mudar o F₀ da
`run2.2` muda o F_amp dela e a chave mecânica **deixa de pareá-las**.

Sem o par, `limite_sres` cairia a 0,025 e **quatro** curvas reprovariam por σ
(`run6p2` 0,0300 · `run7p1` 0,0504 · `M42_run21p0` 0,0337 · a própria `run2p2`
corrigida 0,0364). Por isso a correção **inclui no mesmo passo** a entrada em
**PARES DECLARADOS** (`prereg 2026-07-31-pares-replica-declarados`), classe
criada exatamente para *"réplicas cujo F₀ ALCANÇADO difere (aperto nunca
repete: 4-14 % nos pares do LU) e que a chave mecânica nunca casaria"*.

Isto é **mais** honesto que o estado atual: hoje o par é mantido por um F₀
**nominal** que sabemos errado numa das duas.

## Edições (todas por-caso, nenhuma global)

1. `validation_cases.py`: `("HV r2.2", 312, 59, …)` → **`("HV r2.2", 333, 63, …)`**
2. `digitized_csv/karlsen2022_M30_HV_run2p2.csv` re-baseada em **332,7 kN**
3. `adopted_configs.json` → `KARLSEN_2022_run2p2.cfg.k_ratchet` 0,003 → **0,005**
   (+ `prov` reescrita: passa de "colapso 0.003" para valor **compartilhado**
   com a `run7p1`)
4. `report_html.py` → par declarado `("karlsen2022_M30_HV_run2p2",
   "karlsen2022_M30_HV_run7p1", …)`

## Gates (IMUTÁVEIS a partir daqui)

- **G1 (predição registrada, ±0,015/perna):** base 332,7 + `k_ratchet` 0,005 ⇒
  MAE **0,0319** · res.máx **0,0569** · σ_res **0,0364**. Fora da tolerância ⇒
  INCONCLUSIVO e rollback pelos backups.
- **G2 (parcimônia, o ponto do passo):** a curva passa o tripé com o `k_ratchet`
  **da `run7p1` (0,005)**, sem valor próprio. Se só passar com valor exclusivo,
  o passo perde a razão de ser ⇒ **não adota**.
- **G3 (robustez de base):** o veredito não pode depender da escolha entre
  329,3 e 334,0 — as duas pontas têm de passar o tripé. (Premeasure diz que
  sim; re-conferir na execução.)
- **G4 (piso preservado):** com o par declarado, `limite_sres(KARLSEN)`
  permanece **≥ 0,0845 × 0,90**. Se cair abaixo, as 4 curvas de risco são
  re-medidas e **nenhuma pode sair do tripé** — se sair, rollback.
- **G5 (isolamento):** as outras **10** curvas do KARLSEN e as 194 restantes
  **bit-idênticas** na re-simulação.
- **G6 (sincronia):** store + reports + censo + docs + suíte no MESMO commit.

### Ramos

**ADOTA** (G1–G5) · **INCONCLUSIVO** (G1 ou G3 fora — rollback) ·
**NÃO ADOTA** (G2 falha: passa, mas só com `k_ratchet` exclusivo — o ganho
seria de censo, não de física, e o censo já a conta hoje) · **ROLLBACK**
(G4 ou G5).

### O que este passo NÃO faz

Não toca `run6p2`/`run7p1`/`run14p2` (bases dentro de 1 %) nem re-digitaliza o
meio de curva nenhuma. A dívida das demais curvas da Fig. 10 **não existe** —
o D-X mediu as quatro e só a `run1.2` e a `run2.2` estavam fora de 1 %.
