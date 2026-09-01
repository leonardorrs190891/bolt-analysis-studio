# PREREG — F_amp do YANG_2021: ler da Tabela 1 do paper (correção de REGISTRO, efeito Δ=0 já medido)

## Estado — **EXECUTADO em 2026-08-19 (15:2x), gates 6/6**

| gate | resultado |
|---|---|
| G1 round-trip | ✅ 7/7 com `prov="paper (Table 1)"`; `fig2_typical` no fallback honesto |
| G2 Δ=0 bit-a-bit | ✅ **as 8** re-simuladas idênticas ao store (MAE/res.máx/σ) — predição confirmada |
| G3 isolamento | ✅ zero vazamentos do idioma novo para outras fontes |
| G4 fingerprint | ✅ `7a60cacb72de` intocado após o re-stamp da fonte |
| G5 guarda | ✅ `tests/test_yang2021_famp_do_paper.py` (3 testes — valor+proveniência, fallback da fig2, e a INÉRCIA fixada: se o F_amp deixar de ser inerte, o teste falha pedindo re-baseline consciente) |
| G6 censo | ✅ 144/205 inalterado (consequência do G2) |

Store re-carimbado só na fonte: `config_used.F_amp_N` agora carrega os valores
do paper (2000/6000/8000/11200) nas 7 com match.

**2026-08-19 (15:0x)** · **gates congelados neste commit** · store
`7a60cacb72de`, censo 144/205. Origem: alvos 3–4 da sequência de ataque
(`yang2021_abertas_geometria_dos_inputs.md` §3, commit `7a64bf5`).

## O defeito

As 8 curvas do `YANG_2021` rodam com `F_amp_N = 5640` (= 0,4·F₀, fallback
universal) e proveniência ***"literature (Pai&Hess 2002)"*** — enquanto a
**Tabela 1 do paper** (transcrita na nota de aparato, e presente no próprio
`validation_cases.py` como variável `axkn` que só vai para a *string* da nota)
publica a carga axial **por ensaio**: 2,0 / 6,0 / 8,0 / 11,2 kN.

**Efeito físico: ZERO, e já está medido com instrumento validado** (gancho em
`settling_amplitude_factor` confirmando o valor recebido; 5640 → 2000 deu
Δ=0 bit-a-bit): o caso é montado com θ=90° e `F_ax = |F_amp·cos θ| = 0` ⇒ o
F_amp é estruturalmente inerte em fonte transversal-pura. **Isto é higiene de
proveniência, não adoção de mérito** — o registro afirma uma procedência falsa
para um número que o paper publica.

## A correção

Idioma novo, mínimo, no padrão do grip `("csv", ...)` que já existe:
`SOURCE_INPUTS["YANG_2021"]` ganha `F_amp=("csv", "paper (Table 1)")` e o
`inputs_for` parseia o stem — `_ax(\d+(?:p\d+)?)kN` → valor×1000. Sem match
(a `fig2_typical`, cuja condição a nota não fixa) ⇒ **fallback atual intacto**,
com a proveniência honesta que já tem.

## GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | **round-trip** | os F_amp parseados batem a Tabela 1 da nota: amp1p0→2000 · amp0p8→6000 · amp0p5/r1/r2/r3→8000 · amp0p7→11200; `fig2_typical` fica no fallback |
| **G2** | **Δ=0 bit-a-bit** | as métricas (MAE, res.máx, σ_res) das **8** curvas re-simuladas são **idênticas** às do store — é a predição registrada, e se alguma mudar o achado de inércia estava errado e o passo **PARA** (vira prereg de input com efeito) |
| **G3** | **isolamento** | `inputs_for` de **toda** fonte ≠ YANG_2021 devolve F_amp idêntico ao de antes (o idioma só age onde a chave existe) |
| **G4** | **fingerprint intocado** | inputs ficam fora do hash; o re-stamp da fonte no store não pode mudar o fingerprint `7a60cacb72de` |
| **G5** | **guarda** | teste novo fixando valor+proveniência dos F_amp do YANG_2021 (regressão não volta calada) |
| **G6** | **censo** | 144/205 inalterado (consequência do G2, conferida à parte) |

## Predição registrada

1. G2 passa com Δ=0 exato nas 8 — a inércia foi medida em 2 curvas e a causa é
   estrutural (θ=90° na fonte inteira).
2. O `config_used.F_amp_N` do store muda de 5640 para os valores do paper nas
   7 com match — é a única diferença visível no re-stamp.
3. Se **qualquer** métrica mover: o guard do cos(θ) não é o único caminho do
   F_amp e eu estava errado — PARAR e re-preregistrar como correção com efeito.
