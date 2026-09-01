# Su–N bilinear — **o joelho transfere entre tamanhos (5,9 %)**. Primeiro resultado positivo da linha.

**Data:** 2026-07-28 · **Gates congelados em `3794090`**, antes de rodar
**Execução:** pós-processamento puro — `src/`, store, física e fingerprint **intocados**
**Nada adotado** (S6). Proposta de adoção = pré-registro separado.

---

## 0. Veredicto

| gate | resultado |
|---|---|
| S0 nada de canônico tocado | **OK** |
| **S1** bilinear legítimo em M16 | **OK** — `R²(log)` = **0,9970** (lei única: 0,8484), joelho estritamente dentro |
| **S2** o **joelho transfere** *(cego)* | **OK** — 513,5 vs 544,0 MPa = **5,9 %** (critério ±20 %) |
| **S3** ramo de alto ciclo transfere *(cego)* | **OK** — erro **−1,3 %**, zero re-ajuste — **mas 1 ponto só** (§3) |
| **S4** assimetria é estrutura | **NÃO confirmada** ⇒ pré-declarado como **boa notícia** |
| S5 `sun_life()` reproduz o ajuste | **OK** — 1,29e-15 |
| S6 nada adotado | OK |

**Ramo pré-declarado que se aplica:** *"**S1 ✓ · S2 ✓ · S3 ✓** ⇒ o alto ciclo transfere
entre tamanhos — seria a 1ª constante cross-rig da campanha, escopada ao ramo de alto
ciclo. Propor adoção em prereg separado."*

---

## 1. O ajuste

| | m₁ (tensão alta) | m₂ (tensão baixa) | σ_joelho | C₁ | C₂ | R²(log) |
|---|---:|---:|---:|---:|---:|---:|
| **M16** | 12,03 | 1,38 | **513,5 MPa** | 3,046e36 | 4,151e7 | **0,9970** |
| **M10** | 10,07 | 1,61 | **544,0 MPa** | — | — | 0,9946 |

**O bilinear descreve o dado; a lei única não.** `R²` sobe de 0,8484 para 0,9970 no M16.
Era exatamente este o defeito do L4 — ele testou o modelo errado, e o artigo dizia qual era
o certo.

**Leitura física dos expoentes.** `m₁` ≈ 10–12 é extremamente íngreme e `m₂` ≈ 1,4–1,6 é
quase plano. Isso **não** é uma S–N clássica de fadiga (m ≈ 3–5): é a assinatura de um
**limiar de afrouxamento** — abaixo do joelho o parafuso quase não afrouxa (vida longa até
95 % de F₀), acima ele afrouxa rápido. Coerente com o que o próprio artigo cita de Yang et
al.: *"bolts did not loosen when the transverse displacement amplitude was less than a
certain critical value, which is similar to the fatigue limit of the material."*

**O joelho, traduzido de volta para amplitude:**

| | σ_joelho | δ_crítico | 
|---|---:|---:|
| M16 | 513,5 MPa | **0,475 mm** |
| M10 | 544,0 MPa | **0,421 mm** |

Diferença em **tensão: 5,9 %**; em **amplitude: 11,4 %**. ⇒ **A transformação da Table 2
absorve metade da diferença de tamanho.** É isso que a palavra "normalização" do artigo
significa, medido — não um truque de plotagem.

## 2. O que o gate cego comprou

**S2 e S3 eram cegos** — eu não havia calculado nem o joelho do M10 nem o ramo como ramo
(§0 do prereg declara exatamente o que eu já sabia e o que não sabia).

- **S2:** os joelhos concordam a **5,9 %**. Duas juntas de tamanhos diferentes, pré-cargas
  diferentes (60 vs 25,9 kN) e grips diferentes (85 vs 42 mm) partilham a mesma fronteira
  alto/baixo ciclo **em tensão de raiz**.
- **S3:** o único ponto M10 abaixo do joelho do M16 é previsto com **−1,3 %** de erro,
  usando `(C₂, m₂)` ajustados **só no M16**, **zero re-ajuste**.

## 3. As três ressalvas, com o mesmo destaque

1. **S3 repousa em UM ponto.** A cláusula de validade do prereg previa o caso de **zero**
   pontos (VOID); um ponto passa, mas é fino. O que sustenta o resultado não é o S3
   sozinho — é a **conjunção** S2 (joelho a 5,9 %) + S3 (−1,3 %) + S4 (o ponto de 518 MPa
   também dentro, −5,3 %). São **três** concordâncias independentes na região de alto
   ciclo, não uma.
2. **4 parâmetros para 6 pontos** no ajuste M16 — declarado no prereg §1. Por isso o teste
   que vale é a transferência **zero-refit** a M10, não o `R²`.
3. **A transferência quebra acima de ~780 MPa**, e muito: −77,6 %, −71,8 %, −90,9 %. A
   razão `N_M10/N_M16` na faixa comum é **1,02 → 1,84 → 4,51** com σ crescente. **A
   normalização vale no alto ciclo e não vale no baixo.**

## 4. S4 não confirmada — e por que isso é bom

A hipótese declarada era que **todos** os pontos de baixo ciclo cairiam fora de ±30 %. O
ponto em **518,3 MPa ficou dentro** (−5,3 %), mesmo estando acima do joelho do M16. Ou
seja: **a transferência não morre exatamente no joelho — ela se estende um pouco além e só
colapsa a partir de ~780 MPa.** A fronteira útil é mais larga do que a hipótese supunha.

O prereg declarou de antemão que uma falha do S4 seria *"boa notícia, a reportar como
achado positivo"*. É o que é. E o gate só pôde dizer isso porque a hipótese foi escrita
**antes** — se eu tivesse apenas medido, teria lido "4 pontos fora" e perdido o ponto de
518 MPa.

## 5. O que isto significa para a campanha

A §8 do doc vivo diz, desde a Fase 1: **"formas/acoplamentos transferem cross-rig,
constantes não — são por par/rig/junta."** Este é o **primeiro candidato a contra-exemplo
medido**:

> No **ramo de alto ciclo**, a Su–N do Liu 2025 transfere entre M10 e M16 — joelho a 5,9 %,
> vida a −1,3 % com zero re-ajuste — desde que o driver seja a **tensão de raiz da Table 2**
> e não a amplitude nominal.

Escopo honesto do candidato: **σ ≲ 550 MPa** (equivalente a δ ≲ 0,42–0,48 mm), dois
tamanhos, mesmo material (45 steel), mesmo laboratório. Não é uma lei universal; é uma
constante que atravessou **um** eixo (tamanho) que nenhuma outra atravessou.

**Não adotei nada** (S6). A adoção exige pré-registro próprio, e ele teria de responder o
que este estudo não responde: se o `c_σ` da Table 2 pode ser calculado para um rig que
**não** esteja na Table 2 — porque hoje ele existe para exatamente dois tamanhos, e a
nossa própria fórmula de flexão erra essa escala por 2,1× (§3 do estudo de modelagem).

---

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/sun_bilinear_gates.py     # S0-S6, ~5 s, nao toca src/ nem o store
```
Dados: `New_Theory/liu2025_fig4_DN.json` (Fig. 4 digitalizada, validada a 2,0 %) +
Table 2 do artigo. Resultado: `New_Theory/sun_bilinear_result.json`.
