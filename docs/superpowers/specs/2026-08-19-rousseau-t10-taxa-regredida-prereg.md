# PREREG — `rousseau2025_steel_t10` PASSO 2: o gate re-lido por REGRESSÃO à taxa observada FECHA o tripé

**2026-08-19 (19:2x)** · **gates congelados neste commit** · mandato das 19:13:
*"trabalhe mais até atingir o tripé"* · sucede o prereg
`2026-08-19-rousseau-t10-ratchet-lido` (adoção-de-melhoria, σ 1,30×) — padrão
SUN de 2 passos no mesmo dia.

## 1. Por que o passo 1 não fechou, medido

O resíduo do passo 1 era a ONDA da taxa: a derivada do F publicado é um
**sino** (0,0040 em N=40 → pico 0,0099 em N=100 → 0,0029 em N=170) e o modelo
Hill⁴+taxa-constante não desce. LSQ do Hill sozinho à taxa local: **r²=0,092**
(encaixa a subida, ignora a descida) — prova quantitativa de que nenhum
re-arranjo de (k, W, s) fecha sem a descida.

## 2. A descida EXISTE no engine: o arrest gate — e a regressão completa lê tudo

`taxa(N) = A · Hill(N; N50, s) · (1 − floor/r(N))^aexp`, com **r(N) do DADO**
(observável). LSQ sobre as 12 taxas locais do F publicado:

| parâmetro | valor | tradução ao engine |
|---|---|---|
| A | 0,02420 frac/ciclo | `k_loose_graded` = A·10250/919,7/5,28 = **0,05109** |
| N50 | 89,5 | `slip_onset_W` = 0,142·N50 = **12,7064 J** |
| s | 1,89 | `slip_onset_sharpness` = **1,89** |
| floor | **0,0295** | `loose_arrest_floor` (≤ 0,0951 = último ponto publicado ⇒ **não-barreira por construção**) |
| aexp | **8,0** | `arrest_approach_exp` |

**r² = 0,891.** Degenerescência declarada: (floor, aexp) só identificam o
produto (célula alternativa 0,0108×25 dá r²=0,896 com produto 0,27 ≈ 0,236) —
escolhida a célula de aexp=8 (precedente SUN) SEM olhar a métrica. Estatuto
das constantes: **fitadas-por-regressão a OBSERVÁVEL** (a taxa do F publicado),
não à métrica do tripé — um degrau ACIMA do fitado-declarado da SUN (que fitou
k/aexp na própria métrica). `fsk`/`exp=0`/`emb=0`/`C_creep=0` mantidos do
passo 1 (lidos). O dreno 919,7 N/deg segue sendo a constante da junta.

## 3. Medições sandbox (já feitas)

**0,0289/0,0668/0,0324 → 0,0158/0,0324/0,0098 — FECHA O TRIPÉ com folga ≥60 %
nas três pernas.** Resíduos ±0,02 na curva inteira. θ_fim = 9,64° vs 10,92°
medido (−12 %: o arrest corta a rotação no fim e o ramo graded não tem o
free-spin PÓS-arresto do kernel torque — declarado; o free_spin=1,0 do grupo
não age no graded). **Vizinhança: 8 de 8 perturbações (±10–20 % em k, W,
floor, s) FECHAM** — região, não navalha.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha | 0,0158/0,0324/0,0098 ao dígito pelo caminho canônico |
| **G2** | irmãs | as 7 bit-idênticas (token-vazio da amp0p2 preservado) |
| **G3** | isolamento | Δ=0 exato fora do ROUSSEAU no re-stamp |
| **G4** | re-stamp íntegro | fingerprint único nos 210 (gotcha do sintético) |
| **G5** | censo | **146 → 147** · abertas 19 → 18 · ROUSSEAU 4 → 3 abertas |
| **G6** | sincronização | triagem (t10 sai por catraca), docs vivos, aging, HTML, lista_abertas |

## 5. Predições registradas

1. G1 ao dígito. 2. Censo **147/205** — terceira curva a fechar por modelo no
mesmo dia (SUN standard, LU T10, ROUSSEAU t10), as três pela MESMA estrutura
(forma certa + constantes com procedência de leitura/regressão a observável).
3. A pior aberta do ROUSSEAU passa a ser a `hdpe_t10` (0,0927). 4. As 3 HDPE
abertas têm a mesma rota (traço θ na Fig. 4, dF/dθ=118) — prereg próprio.


## Estado

EXECUTADO 2026-08-19 (19:2x-20:0x): G1 ao digito (0,0158/0,0324/0,0098 — FECHA com folga >=60%), 7 irmas bit-identicas, censo 146->147 no re-stamp 3bb2ca3c9128, vizinhanca 8/8. Resultado no sec7 de rousseau_t10_ratchet_lido_resultado.md.
