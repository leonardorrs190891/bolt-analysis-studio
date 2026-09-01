# PREREG — carga axial externa do ECCLES em TRÊS CAMADAS (registry · plumbing · piso anulável)

## Estado

**PENDENTE — gates congelados, nada implementado.** Escrito em 2026-08-21 (16:3x) contra o
store **`c61366365977`** (uniforme, 210), censo `_censo()` tripé **169/205**.

Autorização do professor: *"autorizo, faça as três camadas"*.

⚠️ **Este prereg SUBSTITUI o desenho de `d319537`** (partição alimentando o embedding). O
motivo está na §2: a nota de aparato corrigiu a física, e o `d319537` já estava morto por
falta de driver (`c9e589e`).

---

## 1. O defeito, medido

`to_solver_config()` das **10** curvas do `ECCLES_2010` devolve, em **todas**,
`initial_preload = 15000` e `transverse_force = 195000`. **Os 10 configs são idênticos** —
inclusive nas **seis** que trazem a carga axial no nome (4 · 3,5 · 3,1 · 2,7 · 1,1 · 0,7 kN).
⇒ a variável que o paper **varre** não entra no modelo, e as 6 axiais são simuladas como se
fossem as baselines.

E o caminho não existe ponta a ponta: `F_ax_ext` aparece em `dynamic_stiffness_analyzer.py`
apenas como parâmetro de `U_loaded` e como acessor (linha 2674) — **nunca é chamado** pelo
runner nem por canal de perda.

## 2. ⚠️ A física é a da NOTA DE APARATO, não a que eu havia desenhado

O `d319537` propunha particionar a carga (`F_joint = F₀ − (1−Φ)·F_ax`) e dirigir o
**embedding** com a pressão menor. A nota de aparato do ECCLES diz outra coisa, e é o achado
**central do paper**:

> *"Reproducing this paper's central finding (**residual-preload floor being overridden once
> FA exceeds it**) would need a new boundary-condition-level concept — e.g. treating `FA` as
> a hard floor that `RotationalLoosening` rotation continues to erode toward (analogous to
> how `slip_onset_gate`/`loose_arrest_floor` already implement a **self-generated** arrest
> floor, but here the floor is **externally imposed** and can also **DEMAND the state fall
> below** where it would otherwise arrest)."*

E a nota **classifica as curvas**:

| classe | figuras | case_ids |
|---|---|---|
| **piso SEGURA** (sem axial excedendo o residual) | 3, 7(a)–(c), 8(a), 8(c) | `fig3_typical` · `fig7a_no_axial` · `fig7b_axial_1p1kN` · `fig7c_axial_2p7kN` · `fig8a_baseline1` · `fig8c_baseline2` |
| **piso ANULADO** — o falsificador novo | **7(d), 8(b), 8(d)** | `fig7d_axial_3p1kN` · `fig8b_axial_0p7kN` · `fig8d_axial_3p5kN` |

⇒ *"these curves show the model's existing `loose_arrest_floor`-type behavior being
deliberately **OVERRIDDEN** by an external condition, i.e. a case where 'arrest' is NOT what
the physics should predict."*

**Dados do rig que fixam o desenho:** axial **force-controlled**, por macacos hidráulicos,
superposto **independentemente** do transversal; **sempre menor em magnitude que a
pré-carga**; dois modos — **constante** (7b/7c/7d) e **intermitente** (8b/8d).

⚠️ **A `fig6` NÃO está em nenhuma das duas listas da nota**, e o meu ataque de hoje
(`113cbb0`) mediu que o erro dela nasce em **u = 0,00** — assinatura **precoce**, não de piso
anulado (que é efeito **tardio**). ⇒ a `fig6` fica **fora do alvo deste item**, declarado
antes de medir para que o resultado não seja re-interpretado depois.

## 3. As três camadas

### C1 — registry: o valor entra
Campo de carga axial externa no `ValidationCase` (N), com o **modo** (`constant` ×
`intermittent`), lido do paper via nota de aparato. Valores: 4000 · 3500 · 3100 · 2700 ·
1100 · 700 N nas 6; **0** nas 4 baselines (que é o valor certo, não ausência).

### C2 — plumbing: o valor chega
`to_solver_config()` → `runner` → `step_cycle`/estado, expondo `F_ax_ext` por ciclo. Para o
modo **intermitente**, um ciclo de serviço (aplica/libera) — a nota diz *"applied/released
periodically while transverse motion continues"*; o duty é **input**, não constante fitada, e
se o paper não o der, a curva fica **declarada** em vez de suposta.

### C3 — piso anulável: `ax_floor_override`
```
ax_floor_override: float = 0.0     # 0 = OFF EXATO
```
Quando `> 0` e `F_ax_ext > 0`, o piso efetivo de arresto passa a ser

```
floor_eff = loose_arrest_floor · max(0, 1 − F_ax_ext / (ax_floor_override · F_sep))
```

com **`F_sep = F_sep_axial(state, geom, mat)`, que JÁ EXISTE** (usado em `U_loaded`). Física:
o axial externo consome o aperto residual; quando o consome por inteiro a interface separa e
**nada arresta** a rotação ⇒ `floor_eff → 0` e o afrouxamento segue até zero, que é
exatamente o que as 7(d)/8(b)/8(d) mostram.

⚠️ **Isolamento estrutural**: `F_ax_ext = 0` ⇒ `floor_eff = loose_arrest_floor` **exato** ⇒
as 4 baselines e **todas** as fontes transversais ficam bit-idênticas **por construção**, não
por default.

## 4. Gates CONGELADOS

| # | gate | critério |
|---|---|---|
| **G1** | OFF bit-idêntico | `ax_floor_override = 0` ⇒ **Δ = 0,0000 nas 210** |
| **G2** | isolamento estrutural | com o campo LIGADO, as **4 baselines** do ECCLES e **todas** as curvas de outras fontes ficam **bit-idênticas** (F_ax = 0 ⇒ identidade exata) |
| **G3** | **PREDIÇÃO DE CLASSE, registrada aqui** | nas **3** de piso anulado (7d/8b/8d) o res.máx tem de **CAIR**; nas **2** de piso que segura com axial (7b/7c) tem de **não piorar** >+0,01. Se a direção inverter em qualquer uma, **FALSIFICADA** — não se ajusta `ax_floor_override` para salvar o sinal |
| **G4** | o input é leitura, não fit | os 6 valores vêm do paper/nota; `ax_floor_override` é **1 número compartilhado** pela fonte. Mais de um valor por curva ⇒ vira fit e o item para |
| **G5** | controle de fonte | nenhuma das 10 piora >+0,01 no MAE; as **4 no tripé hoje** não saem |
| **G6** | conservação | residual de energia não degrada (o piso é gate multiplicativo em `dF_0`, e o `dE` acompanha pelo mesmo `d_theta` — sem energia criada) |
| **G7** | exceções re-julgadas | se alguma das 6 fechar por mérito, a exceção assinada é **retirada com prova preservada** (precedente **K6**), e o `declarado_total` é re-medido — não se deixa exceção redundante |
| **G8** | testes próprios | `tests/test_eccles_axial.py`: OFF-exato · identidade com F_ax=0 · direção do G3 · o intermitente com duty do paper |
| **G9** | suíte | completa, comparada ao baseline |

**Ramos:** `ADOTA` (9/9) · `CAPACIDADE FICA, NÃO ADOTA` (funciona e o G5 reprova ⇒
default-inerte no main) · **`FALSIFICADA`** (G3 inverte) · `INCONCLUSIVO` (o paper não dá o
duty do intermitente ⇒ C1/C2 entram só para as 3 constantes e as 2 intermitentes ficam
declaradas).

## 5. O que este item NÃO faz

- **Não** toca a `fig6`: assinatura precoce, fora do alvo (§2), e isso está declarado antes.
- **Não** inventa `F_sep`: usa o `F_sep_axial` que já existe.
- **Não** promete fechar as 6. O alvo mínimo honesto é **a direção do G3** — a classe
  "piso anulado" tem de responder, e a classe "piso segura" tem de ficar quieta.
- **Não** mexe em `loose_arrest_floor` (constante com procedência per-curva no ECCLES): o
  campo novo **multiplica** o piso, não o substitui.
