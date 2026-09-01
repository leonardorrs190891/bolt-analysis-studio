# Pré-registro — MÉTRICA POR CORRESPONDÊNCIA DE NÍVEL (2ª tentativa)

**Data:** 2026-07-28 · **Autorização:** professor, *"pré-registre. siga com as próximas etapas"*
**Substitui:** `2026-07-28-metrica-em-vida-prereg.md` (1ª tentativa, **REJEITADA** — M2/M3, §4.45)
**Fingerprint vigente:** `4f5bedfbace4` (203 casos) · **Status:** PROPOSTO — gates IMUTÁVEIS depois de assinados

> **Regra nova, aplicada aqui pela 1ª vez (§4.45):** todo gate abaixo carrega sua
> **conta de satisfazibilidade** — o valor que a forma proposta produziria no
> caso ideal. Foi a ausência dessa conta que deixou passar o gate M0
> insatisfazível da 1ª tentativa. **Custo declarado:** a conta é uma divulgação
> parcial e reduz a cegueira. Ela é feita **só no caso de referência declarado**
> (`fig2_single` fino) e o resultado previsto está escrito aqui, para que a perda
> de cegueira seja auditável em vez de silenciosa.

---

## 1. Por que a 1ª tentativa morreu, e o que muda

A forma rejeitada media **distância ao conjunto** de pontos da curva do modelo,
tomando o **mínimo** entre a fuga vertical e a horizontal. Com isso o modelo
**escolhia** a correspondência — e um modelo que despenca *varre* o valor do
dado e é perdoado (`jcsr2023_plain_outdoor`: resíduo 0,128 → 0,081 com o dado
**plano** e o modelo **despencando**). A métrica absolvia colapso prematuro.

**A correção é estrutural, não numérica:** a correspondência passa a ser
**fixada pelo nível**, 1-para-1, sem `min()` e sem escolha do modelo.

| | rejeitada | esta |
|---|---|---|
| correspondência | mínimo sobre a curva — **o modelo escolhe** | **fixada pelo nível `r_i`** |
| escapes | dois (vertical **e** horizontal) | **um**, decidido pela geometria do DADO |
| normalizador | `σ_N = 3 %·N` | **`Δ_col`**, a largura da janela de colapso |
| unilateral? | **sim** (só melhora) — daí o risco | **não** (N6 exige que alguma piore) |

---

## 2. A forma proposta

### 2.1 Joelho (regra JÁ registrada, reusada)

Na curva de referência da janela métrica, com taxas locais `|Δr/ΔN|` entre
pontos consecutivos e `m` = mediana das taxas dos primeiros 80 % dos pontos:

> **joelho** = o primeiro índice `k` tal que **todas** as taxas de `k` até o fim
> excedem `3·m`.

É literalmente a regra do `trim_n_max` (*"taxa local > 3× a mediana do Estágio
II, contígua até o fim"*, commit `b50550d`). **Sem joelho ⇒ nenhum ponto é
pontuado em vida** e a métrica é a de hoje, bit-a-bit.

`Δ_col = N_último − N_joelho` (da **própria curva de referência**; nada de `N_f`
de paper, que não existe para a maioria das fontes).

### 2.2 Resíduo por ponto

Para cada ponto `i = (N_i, r_i)` da janela métrica:

```
ANTES do joelho  ->  resid_i = | r_modelo(N_i) - r_i |          (VERTICAL, hoje)

DEPOIS do joelho ->  N_m = primeiro N em que o modelo DESCE a r_i
                     resid_i = 0.10 * |N_m - N_i| / (TOL_LIFE * Delta_col)
                     se o modelo NUNCA atinge r_i: resid_i = |r_modelo(N_i) - r_i|
sinal_i = sinal(N_m - N_i)   (modelo atrasado = retém mais = positivo, como no vertical)
```

**`TOL_LIFE = 0,15`** — precedente PR-39 (*"cliff capturado dentro de ±15 % do
medido"*) e o mesmo valor do gate G1 do prereg v2, que **discriminou** rampa de
cliff (12 vs 8). A normalização faz o limiar do tripé (`0,10`) significar
exatamente **"errar o instante por 15 % da janela de colapso"**.

**Sem `min()`.** O eixo é decidido pela posição do ponto em relação ao joelho —
geometria do **dado** — e o modelo não tem voto. O fallback quando o modelo não
atinge `r_i` é **vertical e punitivo**, nunca "pular o ponto".

### 2.3 Escopo real (calculado antes de medir — muda o que se espera)

Os `trim_n_max` vigentes **já recortam o colapso** de 16 curvas. Nelas, a janela
métrica de hoje **não contém joelho** ⇒ a métrica nova é **inerte por
construção**. Portanto:

> **Esta mudança, sozinha, quase não move a meta.** O valor dela é **habilitar a
> remoção dos trims**. Medir só o Bloco A e chamar de sucesso seria vender
> inércia como resultado.

Daí os dois blocos de medição do §4.

---

### 2.4 Esclarecimentos de implementação — declarados ANTES de medir

Escritos aqui porque afetam resultados e porque descobri-los depois seria
indistinguível de ajuste post-hoc. Os dois primeiros são **guardas adicionadas no
código** que **não** constam do §2.1; ambas tornam a métrica **mais inerte**
(mais conservadora), nunca mais permissiva:

1. **`k = 0` ⇒ sem joelho.** Se a regra apontar o primeiro ponto, a curva
   "inteira" seria colapso — o que não é um joelho, é ausência de platô.
2. **Menos de 2 pontos após o joelho ⇒ sem joelho.** Não há janela a medir.

3. **Não há guarda de `Δ_col` mínimo — e isso é um risco conhecido, deixado
   deliberadamente sem correção.** Contagem feita agora, antes de medir: das
   **203** curvas, **21** têm joelho na janela métrica de hoje (182 não têm ⇒
   inertes). Entre as 21, várias têm janelas **degeneradas**:

   | curva | `Δ_col` | pts no colapso | tolerância `0,15·Δ_col` |
   |---|--:|--:|--:|
   | `bauer2024_M8_fig6_rep2` | **2** | 2 | **0,3 ciclo** |
   | `eccles2010_fig6_annotated_4kN_axial` | 25 | 2 | 3,8 ciclos |
   | `rousseau2025_steel_t12` | 25 | 3 | 3,8 ciclos |
   | `karlsen2022_M30/M42_vibralock` | 60 | 2 | 9 ciclos |
   | `chu2026ti_D0p5mm_F0_49kN_test3` | 65 | 2 | 9,8 ciclos |

   Uma tolerância de fração de ciclo é obviamente absurda e fará essas curvas
   **piorarem muito**. **Corrigir isso agora seria mexer na forma depois de
   congelá-la** — exatamente o vício que este processo existe para impedir.
   Portanto: **fica como está, é medido, e é reportado.** Se o resultado for
   dominado por joelhos degenerados, a leitura correta não é "a métrica falhou",
   e sim *"a regra de joelho registrada, aplicada ponto-a-ponto a curvas
   digitalizadas esparsas, produz janelas de colapso degeneradas"* — o que é um
   achado sobre a **regra do trim**, que hoje é aplicada por julgamento humano e
   não por essa fórmula.

   **Consequência declarada para o N6:** ele será satisfeito (haverá pioras), mas
   possivelmente **pelo motivo errado**. A leitura do N6 no relatório terá de
   distinguir piora por janela degenerada de piora legítima.

## 3. Implementação declarada

Campos **novos** ao lado dos atuais (os verticais permanecem, para auditoria):
`mae_lvl`, `maxerr_lvl`, `maxerr_lvl_at`, `resid_std_lvl`, `metric_lvl`,
`knee_n`, `delta_col`. Nenhum número histórico é sobrescrito. Não se toca em
`align`, `FLOOR_TRIM`, `trim_n_max`, física, nem `engine_fingerprint()`.

---

## 4. GATES (imutáveis depois de assinados) — cada um com sua conta

### Bloco A — sobre as janelas canônicas de hoje

**N0 — inércia total onde não há joelho.**
*Critério:* curvas sem joelho detectado saem **bit-a-bit** iguais (`Δ = 0` exato
em MAE e res.máx). *Conta:* sem joelho, todo ponto cai no ramo vertical e o
código devolve `|r_modelo(N_i) − r_i|`, a expressão de hoje ⇒ **Δ = 0 exato é
alcançável**. Diferente do M0 rejeitado, que pedia identidade exata de uma
fórmula só assintoticamente idêntica. ✔ satisfazível.

**N1 — inércia no platô das curvas COM joelho.**
*Critério:* pontos antes do joelho têm resíduo **idêntico** ao vertical (`≤ 1e-12`).
*Conta:* mesma construção do N0, ramo idêntico. ✔ satisfazível.

**N2 — DISCRIMINÂNCIA (o gate que matou a 1ª tentativa).**
*Critério:* no `fig2_single` **fino**, o **cliff** deve ter res.máx **≥ 2×** o da
rampa **e** falhar o tripé.
*Conta (declarada, com os números previstos):* `Δ_col = 9789 − 8000 = 1789`,
tolerância `0,15·1789 = 268` ciclos. Em `r = 0,70` o dado cruza em `N = 9169`; o
**cliff** só atinge 0,70 ao despencar em `≈ 9990` ⇒ `ΔN ≈ 821` ⇒ resíduo
**≈ 0,306**. A **rampa** cruza em 9465 ⇒ `ΔN = 296` ⇒ resíduo **≈ 0,110**.
**Razão prevista ≈ 2,8× e o cliff falha** ⇒ ✔ satisfazível, **com margem
estreita** (o critério é 2×). Previsão adicional, escrita para ser conferida: a
**rampa também falha** (0,110 > 0,10) — esta métrica **não** resgata o `fig2`.

**N3 — toda virada é do colapso.**
*Critério:* curva que vire falha→passe tem de ter o máximo-residual antigo
**depois do joelho**. *Conta:* só pontos pós-joelho mudam de valor ⇒
**deterministicamente satisfeito**. Fica como **teste de bug**, não como
descoberta — e é declarado assim.

**N4 — teto de 25 viradas.** *Conta:* não calculável a priori; é ponto de
**parada obrigatória** para reportar, não critério de correção. Declarado.

**N5 — fingerprint inalterado** (`4f5bedfbace4`). *Conta:* nada que o
`engine_fingerprint()` hasheia é tocado ⇒ ✔ por construção.

**N6 — a métrica NÃO pode ser unilateral.**
*Critério:* **pelo menos uma** curva tem de **piorar**.
*Conta:* pós-joelho o resíduo vira `0,10·ΔN/(0,15·Δ_col)`, que **não** é
dominado pelo vertical `≈ s·ΔN`: onde a inclinação `s` é modesta mas o ponto já
passou do joelho, o termo em vida **excede** o vertical. Logo pioras existem.
*Por que este gate existe:* a 1ª tentativa era `≤` o vertical em **todo** ponto —
só podia melhorar números, e foi essa unilateralidade que tornou o "147 → 153"
vazio. Uma métrica que só melhora **não é métrica**. Se nada piorar ⇒ **PARA**.

### Bloco B — a pergunta que de fato importa (declarada como medição, não gate)

Sobre as **16 curvas com `trim_n_max`**, pontuadas na **curva inteira** (sem
trim) com a métrica nova: quantas passam o tripé? É este número — e não o do
Bloco A — que diria se os trims podem cair. **Não é gate nesta rodada**; é o
insumo da decisão do professor sobre a §B da lista de exceções.

### 4.1 Interpretação pré-declarada

| resultado | leitura |
|---|---|
| N0–N3, N5, N6 ✓ e N4 ✓ | métrica adotável; Bloco B vira insumo da decisão sobre os trims |
| **N2 ✗** | mesma morte da 1ª tentativa ⇒ **abandonar a linha inteira** e registrar que correspondência por nível também não discrimina |
| **N6 ✗** (nada piora) | métrica unilateral disfarçada ⇒ **morre** |
| **N0 ✗** ou **N1 ✗** ou **N3 ✗** ou **N5 ✗** | bug; consertar e re-rodar sem reinterpretar gate |
| **N4 ✗** (> 25) | **PARAR** e reportar antes de adotar |

---

## 5. O que NÃO está sendo proposto

- **Não** remover trim algum nesta rodada (Bloco B é medição, não ação).
- **Não** substituir os campos verticais (ficam, para auditoria).
- **Não** mexer em `align`, `FLOOR_TRIM`, física ou fingerprint.
- **Não** ressuscitar a métrica ortogonal rejeitada (§4.45).
- **Não** adotar a rampa do Liu 2025 (segue em falha parcial, G1 12/15).

---

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/metrica_nivel_gates.py          # N0-N6 + Bloco B
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
```
