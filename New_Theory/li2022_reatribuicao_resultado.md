# Re-atribuição `creep`→`fretting` no LI_2022 — MECANISMO CONFIRMADO, adoção RECUSADA

**2026-08-05** · prereg D-O
(`2026-08-05-li2022-reatribuicao-creep-fretting`), por delegação sob o MANDATO
PERMANENTE. Fingerprint intacto: `e38eed05fa47`. **NADA FOI ADOTADO.**

## Veredicto: NÃO ADOTA (o nível não fecha) — ramo declarado

E as duas metades do veredicto, juntas, **são** o achado: o mecanismo está
confirmado e a adoção é recusada pela mesma medição.

## G1 — o gate de mecanismo PASSA, com folga

| cenário | razão de perda 20 Hz / 10 Hz |
|---|---:|
| base (modelo cego) | **1,005** |
| só input corrigido (Fig. 8b) | 0,716 |
| só `C_creep = 0` | **1,000** (nada isolado) |
| **`C_creep=0` + input, todas as doses** | **0,529 – 0,539** |
| DADO | **0,498** |
| banda declarada no prereg | ≤ 0,56 ✅ |

**A re-atribuição PRODUZ a dependência de frequência**, como a álgebra previa
(x→1 ⇒ 0,478; medido 0,529 com o embedding remanescente de 6,7 % diluindo).
O modelo passa de **0 %** para **~93 %** da dependência medida.

## G4 e G5 — falham decisivamente

Varredura de `k_wear_flank` (base 2,154e-13), com `C_creep=0` + input:

| k_flank | razão | 10 Hz | 15 Hz | 20 Hz | full | fecham |
|---:|---:|---:|---:|---:|---:|---:|
| 2,154e-13 | 0,539 | 0,0934 | 0,0765 | 0,0418 | 0,0471 | 1/4 |
| 3,0e-13 | 0,531 | 0,0791 | 0,0676 | 0,0351 | 0,0464 | 1/4 |
| 3,5e-13 | 0,529 | 0,0709 | 0,0624 | 0,0313 | 0,0510 | 1/4 |
| 4,0e-13 | 0,529 | 0,0627 | 0,0572 | 0,0280 | 0,0589 | 1/4 |
| 4,5e-13 | 0,529 | 0,0573 | 0,0521 | 0,0263 | 0,0665 | 1/4 |
| 5,5e-13 | 0,530 | **0,0530** | 0,0476 | 0,0257 | 0,0807 | **0/4** |

* **G4 falha:** a `axialmin_10Hz` — a curva da fila — **nunca fecha**. Melhor
  MAE **0,0530** contra o limite 0,050, e na dose que a aproxima a `full`
  estoura (0,0807) e fecham **0/4**.
* **G5 falha:** a `axialmin_15Hz` sai do tripé (0,0298 → 0,0476 na melhor
  dose, **+0,018**) e a `full` piora +0,015 a +0,049.
* **Saldo da fonte: 2/4 → 1/4.** A re-atribuição **custa** uma curva.

O prereg previa este ramo por escrito: *"NÃO ADOTA (o nível não fecha) — a
forma está certa e o nível não alcança. Registrar com o número; **não** soltar
um segundo parâmetro."* Cumprido: nenhum parâmetro adicional foi liberado.

## Por que a forma certa custa curvas — a tensão que isto revela

* **creep é `log(t)`** — desacelera, dá a *forma* certa, e é **cego à
  frequência**;
* **flanco é linear em ciclos** — dá a *frequência* certa, e **não desacelera**.

Trocar um pelo outro troca um acerto por outro. E é exatamente o defeito
original da `axial_10Hz_full`, medido no início deste ataque: **o dado satura e
o modelo não** (resíduo +0,0466 em 20 k, cruza zero em 200 k, −0,0441 em 330 k;
49,7 % da variância nos 2 pontos tardios).

### A tensão de forma, medida em σ_res

| curva | σ base (creep log) | σ re-atribuído (flanco linear) | Δ |
|---|---:|---:|---:|
| axialmin_10Hz | 0,0242 | 0,0358 | **+0,0116** |
| axialmin_15Hz | 0,0206 | 0,0285 | +0,0079 |
| axialmin_20Hz | 0,0248 | **0,0174** | **−0,0075** |
| axial_10Hz_full | 0,0365 | 0,0590 | **+0,0225** |
| **médio** | **0,0265** | **0,0352** | **+33 %** |

**σ piora em 3 de 4 e melhora só no 20 Hz** — e isso é diagnóstico, não ruído.
O 20 Hz é a curva com a **menor oscilação no parafuso** (Φ=0,286), logo a que
tem **menos flanco** e menos sofre com a forma linear dele; e é a que mais ganha
com a correção de frequência. **O estrago escala com quanto flanco há**: a
`full` (80 % flanco) piora +0,0225.

Assinatura limpa de *"o canal certo com a lei de taxa errada"*.

## Três achados independentes convergem na MESMA forma faltante

1. **Saturação** — o dado da `full` satura e o modelo não (medido ponto a
   ponto).
2. **Atribuição** — o canal que o paper mede (fretting de rosca, Fig. 9 = três
   micrografias SEM) é o que carrega 57 % da perda, e trocar creep por ele
   confirma a frequência mas perde a forma.
3. **Estado ocioso** — `SlowState.delta_thread_fret` **já é acumulado** (linha
   1853) e a lei **nunca o lê de volta**. É acumulador de saída, não estado que
   realimenta.

⇒ **A forma faltante é a SATURAÇÃO DO CANAL DE FLANCO por profundidade
restante**, exatamente a estrutura que o `EmbeddingLoss` recebeu em 2026-07-02
(incremento ∝ profundidade restante). Ela daria **as duas coisas**: a
dependência de frequência (é o canal do flanco) e a desaceleração (que o creep
estava fingindo). E o docstring do próprio canal já cita o regime de
*shakedown* (Mantyla 2020 / Juoksukangas 2016), onde o fretting para de
transportar material.

Isto é candidato de **forma**, com estado já existente e precedente interno —
não de constante. Merece prereg próprio.

## Dívida declarada que qualquer prereg futuro herda

**O Φ desta junta está errado por fator grande.** A Fig. 8(b) mede a oscilação
da força no parafuso: **9,34 kN** a 10 Hz. O modelo calcula Φ=0,104 ⇒ **1,04
kN**. Se A_F = 10 kN for amplitude zero-a-pico (varrendo 20 kN), o parafuso
absorve 47 % ⇒ **Φ ≈ 0,47**, contra 0,104 — e como `Φ = k_b/(k_b+k_j)` com
`k_b = 4,64e8`, isso implica `k_j ≈ 5,2e8` medido contra **4,0e9** no modelo:
rigidez de membro ~8× dura.

⚠️ **ERRATA da própria seção (mesma sessão, `li2022_phi_ancora.md`):** eu
escrevi aqui que *"o slip de flanco está subestimado na mesma proporção e
qualquer `k_wear_flank` fitado hoje compensa o Φ errado"*. **Isso está
ERRADO**, e a leitura do engine mostra por quê: **linha 1248,
`s_th = F_ax / max(geom.k_b, 1.0)`** — o slip de flanco no modo axial usa
`F_ax` **direto, sem passar por Φ**.

Aritmética: o engine usa `10 000/4,64e8 = **21,6 µm**`; o correto pela
oscilação medida é `9 340/4,64e8 = **20,1 µm**` — **7 % de diferença**, não
4,5×. O canal que decide já está quase certo, **por acidente de convenção** (o
engine usa a amplitude zero-a-pico da carga aplicada onde deveria usar a
oscilação do parafuso, e nesta junta os dois quase coincidem).

⇒ A dívida é de **procedência do número Φ**, **não** de contaminação do fit. E
o Φ correto foi derivado do paper (eq. 2 dá `F = A_F + A_F·sin(2πft)`, logo a
carga varre 0→20 kN ⇒ **Φ = 9,34/20 = 0,467**), com dois subprodutos: a
ambiguidade de observável está **resolvida** (`F_B,min` é a pré-carga residual,
o que o modelo calcula) e a correção de input do D-N era exatamente
**Φ(f)/Φ(10 Hz)**.

Predição registrada em `li2022_phi_ancora.md`: corrigir `k_j` deve ser
**INERTE** nestas curvas, porque Φ só entra no canal de afrouxamento
rotacional, que carrega ~0 aqui.

## Gates, um a um

| gate | resultado |
|---|---|
| **G1** (mecanismo, razão ≤0,56) | ✅ **0,529–0,539** em todas as doses |
| G2 (ordenação estrita) | ✅ |
| G3 (isolamento) | n/a — sem adoção |
| **G4** (≥2/4 com a 10 Hz entre elas) | ❌ a 10 Hz **nunca fecha** (melhor 0,0530) |
| **G5** (nenhum pior >+0,010) | ❌ 15 Hz **+0,018**, full +0,015 a +0,049 |
| G6/G7/G8 | n/a |

## Slip de sequenciamento, registrado no prereg

Lancei a varredura **antes** de escrever o prereg. O que preservou a
substância: a saída estava **vazia** ao escrevê-lo (o `| tail` retém tudo até o
fim) e nenhum resultado foi visto. Os gates foram fixados às cegas e o
veredicto é o deles — sem reescrita.
