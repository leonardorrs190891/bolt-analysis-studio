# Adoção per-rig LIU_2025 — EXECUTADA e **REVERTIDA pelo gate cego A1**

**Data:** 2026-07-28 · **Prereg:** `8ec2521` (congelado com as contas) · **Execução autorizada** pelo professor
**Estado final:** config e store **restaurados dos backups** (rollback instantâneo — o backup É o
estado pré-adoção); fingerprint `4f5bedfbace4` uniforme; meta intacta; **a capacidade fica** (`f05a531`).

---

## 0. Veredicto

| gate | resultado |
|---|---|
| **A1** (CEGO) tripé 7/7 + nenhuma piora >+0,01 | **FALHA** — `amp0p8`: 0,0487/0,0853 → **0,1597/0,6800** (ΔMAE **+0,111**) |
| A2 — 196 de fora idênticas | OK (0 divergências) |
| A3 — fingerprint novo e único | **FALHA por bug de cobertura** (↓ §3) — moot com a reversão |
| A4 — informacional | canal `fatigue` visível na decomposição (↓ §2) |

**Ramo pré-declarado honrado:** *"A1 ✗ ⇒ adoção REVERTIDA, capacidade fica; registrar a
causa por curva."* Rollback via backups (equivalente e instantâneo em vez da re-sim de
restauração; o backup é bit-idêntico ao estado pré-adoção).

## 1. A causa, por curva — o relógio, não a forma

Das 3 curvas cegas de risco (rampa dentro da janela da métrica):

| curva | relógio (N_pred/N_meas) | rampa@ vs trim | efeito medido |
|---|---:|---|---|
| **amp0p8** | **0,734** (fratura 27 % cedo) | 7 931 vs 11 500 — **3 569 dentro** | o colapso INTEIRO cai na janela: modelo chega a **0,000** em ~10,6 k, dado segura **0,68** em 11,5 k ⇒ res.máx 0,6800 |
| amp0p3 | 0,930 | 174 321 vs 180 000 — 5 679 dentro | **Δ = +0,0000** — nenhum ponto do dado digitalizado cai nos 5,7 k ciclos da fresta (a métrica avalia nas abscissas do dado, esparsas) |
| fig2 | — | ~69 dentro | Δ = −0,0000, mesmo motivo |

**Leitura:** a forma da rampa nunca foi o problema (com relógio lido: 10/10 nos gates v2;
paridade exata na capacidade). O que falhou é o que o premeasure §2 já tinha orçado: o
colapso ocupa 20–29 % da vida e os trims sentam no joelho (`trim ≈ N_D ≈ 0,72–0,80·N_f`),
então **qualquer curva cujo relógio rode ≥ ~20 % adiantado põe o colapso previsto dentro da
janela da métrica**. O relógio ancorado espalha ±36 % (contas); o orçamento pedia ≤ 5 %.
A adoção com relógio **preditivo** confirma quantitativamente o veredicto do premeasure.

## 2. O que o A4 mostrou (e fica como evidência da capacidade)

Com a adoção ativa, a decomposição carregava o canal `fatigue`: 0,775 de F₀ na `amp0p8`,
**0,846 na `amp0p3`** (o modelo passou a prever a fratura dela DENTRO do range do dado:
~232 k contra 250 k medido, −7 %) e 0,299 no `fig2`. A curva em S completa aparece no
report — mecanicamente, tudo funciona. O que não se sustenta é o **instante** com relógio
preditivo determinístico.

## 3. Achado colateral do A3 — bug de cobertura do `parallel_batch`

O A3 exigia fingerprint novo e **único**; mediu `{d9d9acb8daed, 4f5bedfbace4}`. Causa:
**`parallel_batch` cobre 202 de 203 casos** — `exemplo_m12_sintetico` fica de fora e
mantém o carimbo velho. Inofensivo quando o fingerprint não muda (todos os re-sims desta
sessão), **mas quebra a uniformidade em QUALQUER adoção futura** re-carimbada via
`parallel_batch`. Correção candidata: incluir o caso no batch ou re-carimbar à parte no
fluxo de adoção. Registrado no CLAUDE.md (maquinaria de cfg adotado).

## 4. O que destravaria uma nova tentativa (não executado; decisão do professor)

O caminho **E2 do premeasure**, com precedente adotado: `N_f` como **input-de-paper por
curva** (7 números da matriz de ensaios), como o `LI_2022_TRIBOINT` roda com `fat_C1`
ancorado no `N_frat` medido. Custo honesto: a claim vira *"prevê a curva dada a vida"* —
e com relógio lido, a rampa já provou 10/10. Alternativa: dado bruto dos autores
(carta pronta em `liu2025_data_request_DRAFT.md`).

## 5. Reprodutibilidade

```bash
py -3.12 New_Theory/liu2025_adocao_gates.py <store_pre_adocao.json>   # gates
# rollback = restaurar os 2 backups (config + store)
```
Artefatos: `liu2025_adocao_result.json` · `adocao_batch.log` · contas em
`liu2025_adocao_contas.{py,log,json}` · prereg `8ec2521`.
