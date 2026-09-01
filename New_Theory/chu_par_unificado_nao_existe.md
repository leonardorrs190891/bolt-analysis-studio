# `CHU_2026`: **não existe par unificado** — e isso mede o preço do item D

**2026-08-14** · só-leitura · **nada adotado** · store `c37618c5cc96`, censo **141/205** ·
sequela da adoção `CHU_2026_D1p0` (que levou a `test5` ao tripé).

## A pergunta certa depois do primeiro sucesso

A `test5` fechou com um par nível×forma do embedding. A tentação óbvia era repetir a receita
curva a curva — que é exatamente o que o **item D** da mesa adverte: *"calibrar 8 `per_case`
(8 conjuntos de constantes) — DOF vs ganho, o oposto da parcimônia"*.

Antes de repetir, medi se a fonte é **uma classe**, o que permitiria **um par para N curvas**.

## ✅ A fonte É quase uma classe só

| curva | ρ(resíduo,N) | \|viés\|/MAE | sub-classe |
|---|---:|---:|---|
| `test2` · `test7` · `test8` | 0,90–0,91 | 0,10–0,36 | **A** (rápido cedo, devagar tarde) |
| `test9` | **0,93** | 0,34 | **A** |
| `test5` | **0,94** | 0,79 | **A** |
| `test4` | 0,21 | 0,24 | A (fraca) |
| `test1` (passa) | 0,16 | 0,85 | sem defeito (MAE 0,0035) |
| `test3` · `test6_repeat` | **−0,47 / −0,60** | **1,00** | nível puro |

**Seis das nove** são a mesma sub-classe, com ρ ≈ 0,9. O diagnóstico da `test9` é idêntico em
espécie ao da `test5`: erro se forma **cedo**, wear 94 % do incremento tardio, ρ +0,93.

## ⛔ Mas o par unificado NÃO existe — medido

`test9` fecha sozinha com `emb_depth` 3,0e-5 · `N_emb` **800** (0,0393/0,0682/**0,0145**), e as
irmãs de classe A **melhoram ou ficam paradas** — nenhuma quebra. Porém, aplicando **um único
par a toda a fonte** (preservando a `test1`, que tem config própria):

| par | `test5` | `test9` | tripé | saem |
|---|---|---|---:|---|
| `emb` 3,0e-5 · `N_emb` **400** | ✅ | ✗ (mx 0,108) | **3/9** | — |
| `emb` 3,0e-5 · `N_emb` **800** | ✗ | ✅ | **3/9** | `test5` |
| `emb` 3,0e-5 · `N_emb` **1600** | ✗ | ✅ | **3/9** | `test5` |
| `emb` 4,5e-5 · `N_emb` **800** | ✅ | ✗ | **3/9** | — |

⇒ **todas dão 3/9.** O par serve δ=1,0 mm **ou** δ=0,5 mm, nunca os dois. É **troca, não
ganho**, e levar a `test9` junto exigiria um **segundo grupo por condição**.

## ⚠️ A rota elegante foi verificada e NÃO existe aqui

O `N_emb` precisar ser **400 a δ=1,0 mm e 800 a δ=0,5 mm** é a assinatura clássica de uma
**dependência de amplitude faltante** — e a campanha **tem** essa forma: a **ρ-unificação**
(`emb_amp_exp`/`rho_ref_emb`, §4.18, adotada no `LIU_2017_axial`), que modula o alvo do
embedding por `ρ = F_ax_amp / F₀_init`.

**Ela não serve aqui, e o motivo é do dado:** o `CHU_2026` roda **`F_amp` constante em
19 600 N** nas cinco amplitudes (δ = 0,3 · 0,4 · 0,5 · 0,7 · 1,0 mm). Como ρ é razão de
**força**, ele é **o mesmo** nas cinco ⇒ a forma **não distingue** as condições desta fonte.

⇒ a dependência que o `N_emb` está absorvendo é de **deslocamento**, e o engine só tem a de
**força**. Isso é **forma faltante nomeada com precisão**, não "falta calibrar".

## O que isto entrega para a decisão do item D

**O preço está medido**: cada curva adicional do CHU custa **o seu próprio par**, e os pares
são **mutuamente incompatíveis** entre condições. Não há desconto por volume — é literalmente
2 constantes por condição.

| opção | custo | ganho |
|---|---|---|
| parar onde está | 0 | censo 141, CHU 3/9 |
| adotar 2º par (δ=0,5) | +2 constantes, +1 grupo | +1 (`test9`) ⇒ CHU 4/9 |
| forma nova: embedding dependente de **deslocamento** | prereg de forma (fora do mandato autônomo) | potencialmente as 6 da classe A com **1** forma |

⚠️ **A terceira é a única que escala**, e é a única que exige assinatura de forma nova. As
outras duas são aritmética de DOF.

## Reprodutibilidade

`chu9.py` (conjunta na `test9` + efeito nas irmãs) e `chu_unif.py` (par único na fonte,
preservando a `test1`) no scratchpad. Controle bit-idêntico em ambos. ~20 min.
