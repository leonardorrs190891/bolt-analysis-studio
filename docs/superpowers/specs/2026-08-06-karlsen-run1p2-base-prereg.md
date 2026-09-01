# Prereg — base de normalização da `karlsen2022_M30_HV_run1p2` (D-X)

**2026-08-06 (noite)** · campanha MARGENS fase A′ · classe **dado + input**,
molde D-S/D-U/D-W · gates antes da execução. Fingerprint `5916d8be0510` (não
muda — nem registry nem CSV entram no hash ⇒ **validar re-simulando**).
Diagnóstico: subagente MARGENS.

## O defeito

O CSV ancora `(1, 1.0000)` num valor que a figura só atinge no **ciclo ~26**: a
`run1p2` está soterrada no feixe inicial da Fig. 10 e o digitalizador não
enxergou o ciclo 1. Medido contra o impresso (raster, atribuição **por cor do
swatch da legenda** + vida impressa; calibração validada — y exata em 17
gridlines, x com **rms 0,39 px** em 46 rótulos):

| run | F₀ registry | figura @ciclo 1 | erro |
|---|---:|---:|---:|
| **1.2** | 315 | **~331** (2 estimativas indep.: 331,6 / 331,9) | **+5,0 %** |
| 2.2 | 312 | 332,7 | +6,6 % |
| 6.2 | 340 | 343,4 | +1,0 % ✓ |
| 7.1 | 312 | 313,2 | +0,4 % ✓ |
| 14.2 | 370 | 373,6 | +1,0 % ✓ |
| M42 (4 curvas) | — | — | ≤0,8 % ✓ |

O erro é **exatamente** nas duas soterradas no feixe; a Fig. 11 (sem feixe) está
limpa. **Não é a classe CACCESE** (base trocada por rótulo) — é *primeiro ponto
lido tarde*. `csv_x_offset=1.0`/`x_scale=1.0` estão **corretos** (verificado).

## Escopo: SÓ a `run1p2` — e o motivo é isolamento, não conveniência

⚠️ Re-digitalizar a Fig. 10 inteira mexe em 5 curvas e **quebraria duas**:
`run2p2` e `run7p1` carregam `k_ratchet` per-espécime **adotado** (0,003/0,005)
**fitado contra a série defeituosa** — corrigir o dado sem re-fitar as tira do
tripé. A `run1p2` **não tem config per-espécime** (roda no grupo) ⇒ é a única
correção isolada. As demais ficam como **dívida declarada** (prereg próprio,
com re-fit no mesmo passo).

Duas edições, ambas por-caso:
1. `validation_cases.py`: `("HV r1.2", 315, 60, …)` → **`("HV r1.2", 331, 66, …)`**
2. `digitized_csv/karlsen2022_M30_HV_run1p2.csv` re-baseado em **331,0 kN**.

## Gates (IMUTÁVEIS)

- **G1 (predição registrada, ±0,02/perna):** MAE **0,0171** · res.máx **0,0435**
  · σ_res **0,0195** ⇒ **entra no tripé pelos limites GLOBAIS**. Fora da
  tolerância ⇒ INCONCLUSIVO, rollback pelos backups.
- **G2 (robustez da base):** o resultado não pode depender de 1 kN — medido
  base 328 → 0,0187/0,0517/0,0198 e base 334 → 0,0173/0,0358/0,0201; ambos
  passam. Se a sensibilidade for maior que isso na execução, parar.
- **G3 (isolamento):** as outras **10** curvas do KARLSEN e as 194 de outras
  fontes **bit-idênticas** na re-simulação. (O `c_D=0,3` do grupo foi fitado
  conjuntamente nas 7 HV incluindo a defeituosa; **não re-fitar** é a escolha
  conservadora e a predição acima já é sem re-fit.)
- **G4 (estatuto por MÉRITO):** a exceção F7 da `run1p2` é **retirada** (passa
  sozinha), com a prova preservada em código.
- **G5 (sincronia):** store + reports + censo + docs + suíte no MESMO commit.

## Acoplado, e declarado: o piso da fonte é INVÁLIDO (7ª chave cega)

O piso vigente **0,2348 / 0,5402 / 0,1742** é média de duas famílias, e uma é
inválida: `run21p0` (M42 **HV**, cai a 0,073) × `run29p0` (M42 **Vibralock
torqueado**, plano em 0,949) — piso 0,3666/0,8336/**0,2639**. Elas só pareiam
porque `F_amp = 0,4·F₀` e ambas têm F₀=685 kN; a chave é **cega ao sistema de
porca**, que é a variável independente do paper (*"Comparative study on
loosening of anti-loosening bolt and standard bolt system"*).

Piso válido: **0,1142 / 0,2617 / 0,0835** ⇒ `limite_sres` 0,1742 → **0,0835**.
**Censo não muda** (0 curvas saem). Mas há consequência de exceção:

* `run1p2`: MAE 0,0603 ≤ barra FORTE 0,0807 ⇒ a FORTE **sobreviveria** ao piso
  válido — e vira irrelevante, porque o conserto a faz passar por mérito.
* **`run14p2`: σ 0,0854 > piso 0,0835 ⇒ PERNA DESCOBERTA** ⇒ candidata a
  retratação (`_EXCECOES_RETRATADAS_F7_PERNA_DESCOBERTA`). Margem fina (2,3 %),
  mas foi o mesmo rigor que retratou LU e CACCESE. **Custo: resolvida −1.**

Bloqueio da chave cega + retratação entram **neste** commit, com os números.

### Ramos

**ADOTA** (G1–G3) · **INCONCLUSIVO** (G1/G2 fora — rollback) · a perda de
resolvida pela retratação **não** é motivo de recusa (rigor contra nós).
