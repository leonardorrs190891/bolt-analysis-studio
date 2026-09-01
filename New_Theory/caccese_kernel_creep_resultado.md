# Kernel de creep saturante no CACCESE — ADOTADO, e o σ cai nas 7

**2026-08-04** · prereg `2026-08-04-caccese-kernel-creep-prereg.md` (decisão
D-H, por delegação). Executor `New_Theory/caccese_kernel_creep_exec.py`,
adoção `New_Theory/caccese_kernel_adota.py`.

## Veredicto: ADOTA `creep_mode="saturating"`, `α = 0,2`, `t_c = 100·t_end`

**2 números de forma, compartilhados pelas 7 curvas da fonte. Nenhum
`C_creep` refitado.**

| curva | σ_res antes | depois | Δ | tripé |
|---|---:|---:|---:|:--:|
| compblock_34kPa | 0,0100 | **0,0061** | −39 % | ✅→✅ |
| compblock_71kPa | 0,0094 | **0,0047** | −50 % | ✅→✅ |
| protruding_45kN | 0,0201 | **0,0083** | −59 % | ✅→✅ |
| retighten_12p7mm | 0,0172 | **0,0071** | −59 % | ✅→✅ |
| **retighten_19p1mm** | 0,0263 | **0,0148** | **−44 %** | ❌→**✅** |
| tapered_45kN_rep1 | 0,0218 | **0,0137** | −37 % | ❌ (MAE) |
| tapered_45kN_rep2 | 0,0354 | **0,0270** | −24 % | ❌ (σ 1,08×) |

**σ médio 0,0200 → 0,0117 (−42 %).** Cai nas **7 de 7** — que era o gate G1,
e é o que separa "a curvatura era do kernel" de "ajustei uma curva".

## O que a adoção TROCA — medido no store re-carimbado

Fingerprint `63722b266dc0` → **`8f4b29218b6e`** (210 registros, uniforme).
**G4 (isolamento): perfeito** — 0 curvas não-CACCESE mudaram, exatamente 7
CACCESE mudaram. Censo estrito **129 → 130/205**.

A tabela completa, com as três pernas, mostra que a correção **troca MAE por
forma** — e isso não estava dito com precisão acima:

| curva | MAE | res.máx | σ_res |
|---|---|---|---|
| compblock_34kPa | 0,0073 → 0,0093 (+) | 0,0372 → **0,0201** | 0,0100 → **0,0061** |
| compblock_71kPa | 0,0084 → 0,0099 (+) | 0,0280 → **0,0184** | 0,0094 → **0,0047** |
| protruding_45kN | 0,0179 → **0,0157** | 0,0567 → **0,0251** | 0,0201 → **0,0083** |
| retighten_12p7mm | 0,0153 → 0,0220 (+) | 0,0569 → **0,0403** | 0,0172 → **0,0071** |
| **retighten_19p1mm** | 0,0245 → 0,0253 (+) | 0,0890 → **0,0554** | 0,0263 → **0,0148** ✅ |
| tapered_45kN_rep1 | 0,0523 → **0,0602** (+) | 0,0649 → 0,0677 (+) | 0,0218 → **0,0137** |
| tapered_45kN_rep2 | 0,0274 → **0,0254** | 0,0805 → **0,0651** | 0,0354 → **0,0270** |

**O res.máx melhora em 6 de 7 e o σ nas 7; o MAE piora em 5 de 7**, sempre
abaixo da tolerância de +0,010 (pior caso +0,0079). Isso é coerente com a
construção: a renormalização preserva a perda no **ponto final**, não a
**média** — então o nível se redistribui enquanto a forma melhora.

⚠️ **Consequência que corrige o que escrevi na seção da escolha:** a `rep1`
não só deixa de fechar na célula adotada — ela se **afasta** (MAE 0,0523 →
0,0602). Na célula recusada (α=0,3) ela fechava. Então o custo da escolha por
parcimônia é mais duro do que "fecha 1 em vez de 2": é *fecha 1 em vez de 2 e
piora a segunda*. A escolha se sustenta — constante de tempo igual à duração
do ensaio não é constante de material —, mas o preço tem de estar escrito com
esse número, não com um eufemismo.

## Por que isto não recicla a reprovação de 2026-07-30

O `creep_mode="saturating"` foi reprovado no G2 daquela data (8 de 18 curvas
pioram > +0,01, uma de 0,0396 → 0,2232). Aquela população era de **curvas
transversais onde o creep não domina**. Esta é a oposta, e foi medida antes de
testar: as 7 curvas do CACCESE são **99,5–99,9 % creep** (o canal carrega
0,385 de 0,385 kN), num ensaio de relaxação estática de 2000 **horas**. A
forma nunca havia sido testada onde ela é a única coisa que age.

O defeito também foi medido como **sistemático antes de propor a correção**:
6 das 7 curvas tinham o mesmo sinal de resíduo (positivo no 1º quinto,
negativo no 5º), inclusive as 4 que já passavam. Um kernel errado deixa essa
assinatura; uma curva ruim não.

## O teste é de FORMA porque a amplitude foi renormalizada por aritmética

Os dois ramos têm amplitude com significados diferentes: log dá
`C·F₀·log(t/t₀+1)` (fator 6,909 no fim da janela), saturante dá no máximo
`1,0·C·F₀`. Usar o mesmo `C_creep` compararia amplitude, não forma. Então:

```
C_sat = C_log · log(t_end/t₀ + 1) / (1 − e^{−(t_end/t_c)^α})
```

Fechada, sem otimização, **preservando a perda no ponto final**. E o fator é
**por grupo**, porque `t_0` difere: 21,037 nos grupos com t₀=7200 s e
**17,463** no `compblock` (t₀=23340,76 s). Um fator único teria movido o
compblock 20 % de nível em silêncio.

G0 mediu o desvio no ponto final: **0,1 %** na célula adotada (tolerância
2 %). Nas células com α=0,15 o desvio chegou a **4,6 %** e o G0 as reprovou —
a aritmética da renormalização deixa de valer quando a saturação é forte, e o
gate pegou isso em vez de deixar passar como "a forma falhou".

## A escolha entre as duas células aprovadas — e a lacuna do meu prereg

⚠️ **O prereg não declarou regra de escolha** entre células que passam todos
os gates. Lacuna minha; declaro aqui em vez de resolvê-la em silêncio. Duas
passaram:

| célula | σ médio | fecha | |
|---|---:|---:|---|
| α=0,3 · `t_c = 1·t_end` | 0,0179 (−11 %) | **2** | `t_c` = duração do ensaio |
| **α=0,2 · `t_c = 100·t_end`** | **0,0117 (−42 %)** | 1 | adotada |

Adotei a de **menor σ**, que fecha **uma curva menos**. Razões, nesta ordem:

1. **`t_c = 1·t_end` significa constante de tempo igual à duração do ensaio.**
   Isso é fitar a janela, não o material. Se um revisor perguntar por que não
   escolhi a que fecha mais curvas, *"porque a constante de tempo dela é o
   comprimento do nosso ensaio"* é uma resposta; *"porque fechava mais uma"*
   não é.
2. **Parcimônia efetiva.** Em `t_c ≫ t_end` o kernel é lei de potência
   (`1−e^{−(t/t_c)^α} ≈ (t/t_c)^α`) e `t_c`/`C_sat` **não são separadamente
   identificáveis** — só a combinação age. Logo a célula adotada tem **1
   parâmetro de forma efetivo**, a outra tem 2.
3. σ −42 % contra −11 %: a demonstração de que o defeito era do kernel é 4×
   mais forte.

**Limite de identificabilidade declarado:** a grade era `t_c/t_end ∈
{1, 10, 100}`. Ela **não identifica** `t_c`; distingue apenas dois regimes
(saturação dentro da janela vs lei de potência). O valor adotado é a
afirmação *"não há saturação observável em 2000 h"*, não *"t_c = 23 anos"*.

## Predição registrada: 2 acertos e 1 ERRO meu, a favor

Previ σ caindo nas 7 ✅, a `retighten_19p1mm` fechando ✅, e a **`rep1` fora
do alcance por ser NÍVEL** ❌ — **errei**. Na célula α=0,3 a `rep1` **fecha**.
Meu raciocínio foi: "a renormalização preserva o total, logo o nível não
muda". O total no **ponto final** é preservado; a **média** do resíduo não é.
Preservar um ponto não preserva a integral. O erro foi na direção favorável, o
que não o torna menos erro — e ele mostra que meu modelo mental do kernel
estava incompleto quando escrevi a previsão.

## O que NÃO fechou, e por quê

`tapered_45kN_rep2` foi de σ 0,0354 para **0,0270** — a 8 % do limite, depois
de −24 %. E ela **não tem rota F7**: medido em 2026-08-04, o piso de σ do par
rep1↔rep2 é **0,0233**, abaixo do limite global e abaixo do erro do modelo
(`_SEM_ROTA_F7_MEDIDO`). Segue na fila, agora muito mais perto.

`tapered_45kN_rep1` continua fora pelo **MAE** (0,0523). Ela era exceção
assinada até hoje, quando a assinatura foi **retratada por piso inválido**
(3º bloco; a prova citava piso 0,121 de um pareamento cego entre as 7
condições da fonte).
