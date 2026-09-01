# Como modelar o Liu 2025 na nossa metodologia — estudo detalhado

**Data:** 2026-07-28 · **Fonte primária relida:** Yang, Zhao, Yang, Shao, Xiao, Zhu & Yuan,
*"Bolt loosening evaluation method based on normalized screw root equivalent stress and
loosening life curve"*, **Sci. Rep. 15:20815 (2025)**, DOI 10.1038/s41598-025-02936-6
(open access, 14 páginas, texto integral extraído — não só as notas de aparato)
**Fingerprint do estado medido:** `4f5bedfbace4`

---

## 0. O que este estudo muda

1. **O artigo não modela a curva — modela a VIDA.** Nós modelamos a curva e não a vida.
   São métodos **complementares**, e o que falta ao nosso modelo está inteiro no artigo:
   o **driver com procedência**.
2. **A Table 2 do artigo é a peça que faltava**: a transferência δ → tensão na raiz do
   filete, medida para M10 **e** M16. Ela é **linear em δ** (desvio 2,5–2,9 %) e o efeito
   de tamanho é **fraquíssimo** (razão M10/M16 = **1,195**).
3. **Nosso proxy de fadiga tem a forma certa e a escala de tamanho errada por 2,1×.**
   `σ_a = Kt·E·d₂·δ/L_eff²` prevê razão 2,51 contra 1,195 medida. O `L_eff²` é o culpado.
4. **O relógio é MUITO melhor do que eu concluí hoje de manhã.** Com a tensão do artigo,
   uma **única** lei de potência dá `m = 3,012`, **R²(log) = 0,9894**, erros de **−19 % a
   +14 %** nas 6 amplitudes.
5. **⚠ CORREÇÃO DE REGISTRO: os "44 % de dispersão de espécime" NÃO estão estabelecidos.**
   A amplitude do ensaio da Fig. 2 **não é declarada no artigo** (§4). Eu construí sobre
   ela duas conclusões hoje.

---

## 1. O que o artigo realmente faz

O método é **stress-life**, não trajetória. A cadeia, equação por equação:

| eq. | conteúdo | o que é |
|---|---|---|
| (1) | `M = f(D, I_Z1, I_Z2, l₁, l₂, E_b)` via **Castigliano** | deslocamento transversal imposto → **momento fletor no parafuso** |
| (2)–(3) | `S₁(z), S₂(z), S_T(z)` com `λ₁,λ₂,λ₃` | distribuição de carga **filete a filete** ao longo do engajamento (Sopwith/Yamamoto) |
| (4)–(6) | `δ₁..δ₅` externo/interno, `δ = w·cosα/(k·E)` | **compliance do filete** por 5 modos (flexão, cisalhamento, inclinação, cisalhamento do filete, força radial) — Yamamoto & Kasei |
| (7) | `S_n, S_τ, S_b` | conversão para tensões normal e cisalhantes na raiz |
| (8) | `σ_n = √(½[(σ₁−σ₂)²+(σ₂−σ₃)²+(σ₃−σ₁)²])` | **von Mises** nominal na raiz do filete |
| (9) | `σ_t = K_t · σ_n` | tensão **verdadeira** na raiz |
| (10) | `M_c = E·W·√((ε₁−ε₃)²/4+(ε₂−ε₄)²/4)` | momento **medido** por 4 extensômetros (só na validação) |

Depois: **D–N → M–N → Su–N**, a Su–N sai **bilinear** com fronteira alto/baixo ciclo, e as
curvas de **M10 e M16 colapsam numa única curva normalizada** (Fig. 7). Para vibração
aleatória: **rainflow** sobre o histórico de `σ_t` + **Miner**.

**Validação (Table 3):** bancada de suporte de antena de truque de metrô, espectro
EN61373:2010, **pré-carga 20 kN** (contra 60 kN dos ensaios D–N):

| parafuso | dano/hora | vida prevista | vida medida | erro |
|---|---:|---:|---:|---:|
| I | 0,366 | 2,73 h | 2,82 h | **3,11 %** |
| II | 0,746 | 1,34 h | 1,43 h | **6,26 %** |

⚠️ **Ressalva que muda a leitura desse 6,26 %:** ali o momento fletor foi **MEDIDO** com
parafusos instrumentados (eq. 10), não previsto a partir do deslocamento. É validação da
**Su–N**, não da cadeia δ→M. Nós temos de prever o driver, então não herdamos esses 6 %.

---

## 2. Table 2 — a transferência que nos faltava

O artigo publica a conversão δ → tensão equivalente na raiz, para os dois tamanhos:

| δ (mm) | M10 (MPa) | M16 (MPa) |
|---:|---:|---:|
| 0,3 | 391,96 | 328,70 |
| 0,4 | 525,05 | 440,05 |
| 0,6 | 787,00 | 660,03 |
| 0,8 | 988,76 | 821,65 |

Medido a partir dela:

- **É linear em δ:** `σ/δ` = 1307/1313/1312/1236 (M10) e 1096/1100/1100/1027 (M16) MPa/mm
  — desvio de **2,5 %** e **2,9 %**. ⇒ `σ_root ≈ c_σ·δ` com `c_σ` = **1292** (M10) e
  **1081** (M16) MPa/mm.
- **O efeito de tamanho é quase nulo:** razão M10/M16 = 1,192/1,193/1,192/1,203, média
  **1,195**. É *por isso* que a Su–N normaliza entre tamanhos — a normalização não é um
  truque, é consequência de `c_σ` variar pouco.
- Os dois pontos de 0,8 mm caem ~6 % abaixo da reta: início de não-linearidade (plasticidade
  na raiz), coerente com a fronteira alto/baixo ciclo declarada.

**Parâmetros dos dois rigs (Table 1):** M10 — 45 steel, F₀ = 25,9 kN, grip 42 mm, passo 1,5;
M16 — 45 steel, F₀ = 60 kN, grip 85 mm, passo 2,0. Ambos ângulo 60°, hélice 3°, folga 1 mm.

---

## 3. Confronto com o nosso proxy — o defeito é de escala com o tamanho

Nosso `FatigueLoss` em modo `bending` usa `σ_a = K_t·E·d₂·δ/L_eff²`. Contra a Table 2:

| | M10 | M16 |
|---|---:|---:|
| nosso `σ_a` a 0,8 mm com `K_t=1` | 859,6 MPa | 341,8 MPa |
| `K_t` necessário p/ bater o artigo | **1,15** | **2,40** |
| razão de tamanho prevista pelo proxy | \multicolumn{2}{c}{**2,51**} |
| razão de tamanho medida no artigo | \multicolumn{2}{c}{**1,195**} |

**Diagnóstico:** a dependência em δ está certa (linear, ✓), mas o `L_eff²` faz a tensão cair
rápido demais com o grip. Um `K_t` único **não existe** — ele teria de valer 1,15 num rig e
2,40 no outro. Ou seja, o proxy **não normaliza entre tamanhos**, que é justamente a
propriedade que o artigo demonstra existir.

Fisicamente, o motivo é claro: o proxy é uma viga bi-engastada (`σ = 3E·d·δ/L²`), enquanto a
cadeia do artigo insere a **compliance do filete** (eqs. 4–6) em série, que amortece o efeito
do grip. Ignorar essa compliance é o erro.

---

> ## ⛔ ERRATA (mesmo dia, apos rodar o L4) — a §4.1 abaixo esta INVALIDA
>
> A §4.1 pareia as tensoes da Table 2 com as vidas de **FRATURA**. Errado: o artigo
> declara que a D–N da Fig. 4 — a que gera a Su–N e portanto a que acompanha a
> Table 2 — e' **vida ate `F/F₀ = 0,95`**, nao ate a fratura. Prova geometrica: o
> eixo x da Fig. 4 vai ate 10⁵ e as vidas de fratura chegam a 3,3×10⁵.
>
> Com o pareamento CORRETO (Table 2 × Fig. 4): **`m` = 5,94, `R²(log)` = 0,8484** —
> ajuste ruim, curva claramente bilinear. O `m = 3,012 / R² = 0,9894` da §4.1 era
> coincidencia de duas grandezas que crescem ambas com a amplitude.
>
> **Cai junto:** a "retro-justificacao" do `fat_m1 = 2,7` (§4.1) e a recomendacao
> `fat_m1 = 3,01` (§7 C2). Pior: **"2,7" nao aparece no texto do artigo** — a
> procedencia registrada no `LI_2022_TRIBOINT` nao e' rastreavel a fonte citada.
>
> A §4.2 (os "44 %" nao estabelecidos) **permanece valida**.
> Detalhe: `New_Theory/liu2025_L4_resultado.md`.

## 4. O relógio — e a correção de um número que usei hoje

### 4.1 Com a tensão certa, a vida é previsível a ~±17 %

Usando `σ_root` da Table 2 e as 6 vidas medidas da matriz de ensaios M16:

| δ (mm) | 0,25 | 0,30 | 0,40 | 0,50 | 0,60 | 0,80 |
|---|---:|---:|---:|---:|---:|---:|
| σ_root (MPa) | 273,9 | 328,7 | 440,1 | 550,0 | 660,0 | 821,6 |
| N_f medido | 330 000 | 250 000 | 77 000 | 38 000 | 24 200 | 14 400 |

> **Uma única lei de potência:** `N = 7,75e12 · σ^−3,012`, **R²(log) = 0,9894**,
> razões previsto/medido **0,81 · 1,07 · 1,10 · 1,14 · 1,03 · 0,90**.

Bilinear **não melhora** neste conjunto (erro máximo 14,8–17,2 % em qualquer ponto de
quebra) — a bilinearidade do artigo aparece ao juntar M10+M16, não dentro do M16 sozinho.

**Isto retro-justifica o `fat_m1 = 2,7` do PR-24.** Ele foi importado como *inclinação D–N*
(vida vs deslocamento) para um papel de *expoente de tensão*. Isso só é legítimo se
`σ ∝ δ` — e a Table 2 mostra que é, a 2,9 %. Nosso ajuste direto em tensão dá **3,01**;
o artigo declara 2,7 na D–N. Consistentes dentro da dispersão. **A importação era
defensável e agora tem prova.**

### 4.2 ⚠ Os "44 % de dispersão de espécime" não estão estabelecidos

Eu afirmei hoje, em §4.44a e repeti em §4.45–§4.48, nos pré-registros e em vários commits:

> *"`fig2` e `amp0p8` são a mesma amplitude nominal e fraturam com 44 % de diferença
> (10 k vs 14,4 k) — nenhum relógio determinístico vence isso."*

**Relendo o artigo: a amplitude do ensaio da Fig. 2 NÃO é declarada.** O texto diz apenas
*"a typical clamping-force recession process of a bolt under the action of a transverse
load"*. O "~0,8 mm class" veio de **inferência** nossa, registrada em
`apparatus_notes/liu2025_scirep_M16.md`, não do artigo.

E a lei D–N do próprio artigo explica a diferença **inteira** com amplitude, sem dispersão:

| expoente D–N | δ da Fig. 2 implícito | vs 0,80 nominal |
|---|---:|---:|
| 2,700 (declarado no artigo) | 0,916 mm | **+14,5 %** |
| 2,883 (nosso ajuste) | 0,908 mm | +13,5 % |

⇒ **Uma amplitude não reportada ~13–14 % maior explica 10 k vs 14,4 k com ZERO dispersão
de espécime.** Os 44 % não são dispersão medida; são a diferença de vida entre duas curvas
cuja amplitude relativa é desconhecida.

**O que isso invalida e o que não invalida:**

- **Invalida** a afirmação *"o relógio está fechado pelo dado"* como eu a escrevi. O número
  honesto é o de §4.1: **±17 %**, que já era o valor do PR-24.
- **Não invalida** o fechamento da linha de métrica (§4.48a) — aquela morreu nos gates de
  **discriminância**, que não dependem do scatter.
- **Não invalida** a classe `metric-limited`: o argumento aritmético (0,20→0,104 em 5 ciclos
  ⇒ ±0,05 % da vida para `res.máx<0,10`) permanece, e ±17 % continua muito acima disso.

Ação: corrigir a nota de aparato para dizer **"amplitude não reportada"** em vez de
"~0,8 mm class", e corrigir as §§ que citam 44 % como medida.

---

## 5. Outras fontes — a lei de forma que nos falta

A busca localizou a linha de **falha competitiva** do mesmo grupo (Yang et al.), que trata
justamente do que o Liu 2025 não trata: **a forma da curva**.

> *"Under a **large transverse load and small axial load**, the structural loosening period
> became **shorter and steeper**; the loss of clamping force became larger; the fatigue
> fracture period was relatively **smooth**. Under a **small transverse and large axial
> load**, the structural loosening period became **longer and smoother** … and the fatigue
> fracture period was relatively **steep**."*

Ou seja: **a razão carga transversal / carga axial governa a inclinação relativa dos dois
estágios.** Nosso modelo não tem esse acoplamento — ele trata afrouxamento e fratura como
canais independentes. Isso é uma **forma nomeada e faltante**, e explica por que uma única
rampa `(D_on, q)` serviu `amp0p4/0p5` e não a `amp0p6` (§4.47 do doc vivo).

Também confirma a definição do joelho que já usamos: **`N_D` = interseção da curva com a
tangente de 45°** (mesma regra citada nas notas do YANG_2021).

---

## 6. O que o nosso engine já tem

| peça | estado |
|---|---|
| `sun_life()` — Su–N **bilinear (Yang)** | **já existe**, mesma família do artigo |
| `FatigueLoss` — Miner + **Goodman vivo** (σ_m = F₀/A_s evolui) | já existe, `fatigue_enabled=False` por default |
| modo `bending`: `σ_a = K_t·E·d₂·δ/L_eff²` | existe — **é o elo com a escala errada** (§3) |
| rampa de perda de seção (`A_eff`→`k_b`→`F₀`) | **validada em forma hoje** (10/10 cruzamentos em `amp0p4`/`amp0p5`), mas só injetada por sonda; **não é capacidade do engine** |
| precedente adotado | `LI_2022_TRIBOINT`: `fatigue_enabled=True, fat_stress_mode='axial', fat_m1=2.7, fat_C1=2.977e29` |
| `LIU_2025` adotado hoje | `c_bend, delta_free, emb_um, k_ratchet, k_wear_scale_tr, loose_arrest_floor, slip_onset_W, N_emb, C_creep, W_conf_ref, trim_n_max` — **sem fadiga** |

Defaults de fadiga hoje: `fat_Kt=3.5, fat_m1=3.5, fat_C1=5e32, fat_sigma_uts=1.04 GPa`.

---

## 7. Proposta — como modelar o Liu na nossa metodologia

Nas três camadas do paradigma, e **sem inventar constante nova**:

### Camada 1 — analítica: trocar o driver, não a física

Substituir o proxy de viga por uma **transferência linear com procedência**:

```
σ_root(N) = c_sigma · δ_eff(N)          [Pa]
c_sigma: input-de-paper, Table 2 — 1081 MPa/mm (M16), 1292 MPa/mm (M10)
```

- Classe de procedência: **input-de-paper**, mesma de `emb_um`/`trim_n_max`.
- É **medido em dois tamanhos**, o que é raro na nossa biblioteca — a maioria das nossas
  constantes é per-rig.
- Interpolação para outros tamanhos: **não extrapolar** com o `L_eff²` (que sabemos errado
  por 2,1×). Enquanto só houver 2 pontos, `c_sigma` é **por-rig declarado**, não uma lei.
- **Alternativa mais ambiciosa**, se o professor quiser: implementar as eqs. (1)–(9) de
  verdade (Castigliano + compliance de Yamamoto). Custa mais e traz a compliance do filete
  para o engine — que é exatamente o que o `k_tr_mode='bending'` hoje aproxima grosso.

### Camada 2 — empírica: a Su–N já está lá, com o expoente certo

- `fat_stress_mode`: **novo modo `root`** que consome `σ_root` da Camada 1 (hoje só há
  `axial` e `bending`).
- `fat_m1 = 3,01` (ajustado às tensões da Table 2, R² 0,9894) — ou 2,7 se preferir a
  declaração do artigo; a diferença cai dentro dos ±17 %.
- `fat_C1`: **re-ancorar** contra as 6 vidas M16 medidas. Nosso ajuste dá 7,75e12 na forma
  `N = C·σ^−m` com σ em MPa — converter para as unidades do engine antes de usar.
- **Goodman vivo já está implementado** e é fisicamente necessário aqui: F₀ cai 20 % antes
  do joelho, o que estica N_D.

### Camada 3 — fenomenológica: a rampa de seção, promovida a capacidade

A forma B1 já validada:

```
A_eff/A_s = 1 − ((D_fat − D_on)/(1 − D_on))^q      para D_fat > D_on
k_b ∝ A_eff   ⇒   F_0 = δ_tot·k_b·k_m/(k_b+k_m)   cai junto
```

- `D_on ∈ [0,70; 0,90]` — banda **handbook** (propagação = últimos 10–30 % da vida em HCF),
  que bate com os 20–29 % medidos nesta fonte.
- `q` — **fitado-this-rig**, um valor para as 7 curvas.
- **Default inerte** (`fatigue_enabled=False` já garante isso).

### O que a proposta NÃO resolve — dito antes de qualquer gate

1. **±17 % em N_f desloca a janela de colapso** em ~60–85 % da própria largura dela
   (o colapso ocupa 20–29 % da vida). A forma fica **no lugar aproximado**, não no exato.
2. **O tripé vertical continua inatingível** nessas curvas (§4.44a/§4.48a) — isso é
   metrológico e a linha de métrica está fechada. **Os trims permanecem.**
3. **O acoplamento transversal/axial (§5) continua ausente** — é a forma que explicaria por
   que a `amp0p6` não obedece ao mesmo par `(D_on,q)`.
4. `c_sigma` só existe para **dois** tamanhos; fora deles, não há lei.

**Portanto o ganho honesto é:** o modelo passa a ter um **canal de fratura com procedência
de paper e validação cross-size**, em vez de um proxy com escala errada por 2,1× — e passa a
reproduzir a forma dessas curvas por física, não por trim. **Não** é um ganho de meta.

---

## 8. Plano de validação (para um pré-registro, se autorizado)

Gates candidatos, cada um com a conta a rodar **antes** de congelar (regra §4.47/§4.48):

- **L0** — inércia: `fatigue_enabled=False` reproduz os 203 casos **bit-a-bit**.
- **L1** — driver: com `c_sigma` da Table 2, o `σ_root` do engine reproduz os 8 pontos da
  Table 2 dentro de **3 %** (é o desvio da própria linearidade).
- **L2** — relógio: as 6 vidas M16 dentro de **±20 %** com **um** par `(C1, m1)`.
- **L3** — forma: com `N_f` do relógio (não lido), os cruzamentos em vida das 3 do núcleo
  dentro da tolerância do prereg v2 — **gate cego**, não usar `fig2` no desenho.
- **L4** — cross-size: o **mesmo** `(C1, m1)` prevê as vidas M10 dentro de ±25 %.
  *(É o teste da normalização do artigo, e o mais valioso: se passar, temos uma constante
  que transfere entre rigs — algo que a §8 do doc vivo diz que nunca aconteceu.)*
- **L5** — não-regressão: nenhuma das 196 curvas de fora piora > +0,01.

⚠️ **L4 exige as curvas M10**, que **não estão na nossa biblioteca**. Antes de qualquer
execução seria preciso digitalizar a Fig. 4 (D–N do M10) do artigo — 4 pontos, barato.

---

## 9. Reprodutibilidade

| item | onde |
|---|---|
| PDF integral | `curve_library/pdfs_open_access/liu2025_scirep_M16.pdf` (14 pp.) |
| texto extraído | `py -3.12 -c "import pypdf; ..."` (pypdf instalado nesta sessão) |
| Table 2, Table 1, Table 3 | §2, §1 e §1 deste documento |
| contas de §3 e §4.1 | reproduzíveis inline; ver blocos de código no changelog do commit |
| fontes secundárias | Yang et al., *Shock and Vibration* 2021 · *CJME* 2021 e 2023 (falha competitiva) |

**Fontes:**
- [Liu/Yang et al. 2025, *Sci. Rep.* 15:20815](https://www.nature.com/articles/s41598-025-02936-6) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12218038/)
- [Competitive Failure of Bolt Loosening and Fatigue under Different Preloads, *CJME* 2021](https://cjme.springeropen.com/articles/10.1186/s10033-021-00663-3)
- [Method for Evaluating Bolt Competitive Failure Life Under Composite Excitation, *CJME* 2023](https://cjme.springeropen.com/articles/10.1186/s10033-023-00923-4)
- [Competitive Failure of Loosening and Fatigue of Bolts under Composite Excitation, *Shock and Vibration* 2021](https://onlinelibrary.wiley.com/doi/10.1155/2021/1441122)
- [Analysis of competitive failure life of bolt loosening and fatigue, *Eng. Fail. Anal.* 2021](https://www.sciencedirect.com/science/article/abs/pii/S1350630721005586)
