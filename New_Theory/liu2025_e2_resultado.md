# Adoção E2 do LIU_2025 — **ADOTADA**. O estágio 3 entra no canônico por física, dada a vida.

**Data:** 2026-07-28 · **Prereg:** `d721b14` (congelado com as contas) · **Execução autorizada** pelo professor
**Fingerprint novo:** `9ac44acd03de` (uniforme nos 203) · **Meta intacta:** 147/202 comparáveis

---

## 0. Veredicto

| gate | resultado |
|---|---|
| **E1** (CEGO) tripé 7/7 + nenhuma piora >+0,01 | **OK** — pior ΔMAE **+0,0006** (`amp0p6`); 4 curvas com Δ ≤ ±0,0002 |
| **E2g** — 196 de fora idênticas | OK (0 divergências) |
| **E3** — fingerprint novo e único | **OK após conserto de execução** (↓ §2) |
| **E4** — informacional | as 7 curvas agora TERMINAM como o dado (↓ §3) |

As **6 curvas cegas** seguraram exatamente como a previsão analítica das contas dizia
(`α(D_trim) ≤ 2,6e-6` ⇒ rampa numericamente nula na métrica): `amp0p25` +0,0000 ·
`amp0p3` +0,0000 · `amp0p5` +0,0001 · `amp0p6` +0,0006 · `amp0p8` −0,0001 ·
`fig2` −0,0002.

## 1. O que mudou no canônico

As 3 chaves adotadas (`LIU_2025`, `LIU_2025_amp0p4`, `LIU_2025_amp0p5`) ganharam o bloco
de fadiga+rampa com **`N_f` input-de-paper por curva** (7 `fat_C1` fixados no prereg —
tradução mecânica da coluna *cycles to end*, a mesma dos `trim_n_max`). Primeiro uso do
`per_case` para campos `fat_*`. Claim honesta: **"prevê a curva dada a vida"** — com
relógio lido a rampa já havia provado 10/10 nos gates v2.

## 2. E3 — o conserto que o prereg previu ERRADO, corrigido no fluxo

O prereg mandava re-carimbar `exemplo_m12_sintetico` via `parallel_batch --cases`.
**Medido: `nenhum caso selecionado`** — o caso está FORA do universo do batch (é por
isso que ele cobre 202 de 203; `--cases` filtra dentro do universo). Conserto real:
re-simulação direta via `runner.simulate_case` + carimbo (`engine_fingerprint()`),
com verificação campo a campo de que as métricas ficaram **bit-idênticas** (ficaram).
Ramo do prereg honrado: *"E3 ✗ = bug de execução; consertar sem reinterpretar"*.
Gotcha do CLAUDE.md corrigido com o método que funciona.

## 3. O que a adoção compra (A4/E4)

Com o relógio lido, as curvas full-range agora **terminam como o dado** — antes o
modelo retinha ~0,78–0,84 onde o paper mede fratura:

| curva | final_pred | canal `fatigue` na decomposição |
|---|---:|---:|
| amp0p25 | 0,140 | 0,702 de F₀ |
| amp0p3 | 0,061 | 0,784 |
| amp0p4 | 0,138 | 0,659 |
| amp0p5 | 0,090 | 0,698 |
| amp0p6 | 0,000 | 0,636 |
| amp0p8 | 0,336 | 0,191 |
| fig2 | 0,171 | 0,626 |

O report/galeria passa a mostrar a curva em S completa com a decomposição carregando o
estágio de fratura — o residual de forma nomeado no verdict do PR-9b (*"cliff terminal =
fratura"*) está fechado. **Métrica e trims intocados** (a rampa é nula nas janelas).

## 4. Reprodutibilidade

Prereg `d721b14` §5; store re-carimbado `9ac44acd03de`; report regenerado
(`New_Theory/validation_html/`); gates em `liu2025_adocao_result.json`.
