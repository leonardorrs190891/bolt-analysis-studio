# PREREG — correção das CSVs da fig18 do LU (0,5/1,0/2,0 mm) pelo instrumento validado — campanha de ESTAR-CERTO com saldo declarado

**2026-08-21 (13:4x)** · **gates congelados neste commit** · mandato das 13:38
(*"continue"*) — executa a recomendação de `lu2024_fig18_familia_tab8.md`
(2026-08-06) com o instrumento de `lu2024_fig18_extracao_resultado.md`
(2026-08-07, controle 1,5 mm reproduzindo o D-W a ±0,002).

## 1. O que se corrige, e por quê (erros MEDIDOS contra a Tabela 8)

| curva | erro da CSV @c10 | fator sobre o ruído do instrumento |
|---|---:|---:|
| `amp2p0` (TRIPÉ) | **+0,0792** | ~40× |
| `amp1p0` (fora do censo; metade do PAR DO PISO) | **+0,0439** | ~20× |
| `amp0p5` (DECLARADA órfã) | **+0,0100** | ~5× |
| `amp0p25` | **NÃO-DECIDÍVEL** (âncora ilegível: série preta × moldura preta) — INTOCADA | |
| `amp1p5` | já corrigida (D-W) — INTOCADA | |

Regra do doc: **o 1º ciclo vem da Tabela 8** (o pixel tem ±0,05 no penhasco);
os demais pontos do traço extraído, amostrados no MESMO grid-x das CSVs
atuais (comparabilidade da métrica).

## 2. SALDO DECLARADO ANTES (a campanha é de estar-certo, não de censo)

| curva | hoje | risco declarado |
|---|---|---|
| `amp2p0` | **0,0110/0,0300/0,0124 — TRIPÉ** | pode SAIR (o modelo foi visto contra CSV inflada em +0,08 no c10) — **−1 aceito ANTES**, como o D-U tirou a yang2021_r1 |
| `amp0p5` | 0,1324/0,1795/0,0449 — declarada | pode melhorar; fechar exigiria mérito completo |
| `amp1p0` | 0,0432/0,0784/0,0238 — `_CID_NAO_COMPARAVEL` | não move censo; MAS é metade do par do piso amp1p0↔T22 ⇒ **o piso de digitalização re-mede no mesmo commit** (regra do erratum ROUSSEAU); se o piso σ novo ficar < 0,025, `limite_sres(LU)` não muda |

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | round-trip das CSVs NOVAS contra a Tabela 8 | c1 EXATO (vem dela); c10/c50/c100 a ±0,005 |
| **G2** | as intocadas (amp0p25, amp1p5, fig20 ×5, fig14 ×3) bit-idênticas | |
| **G3** | piso do par amp1p0↔T22 re-medido e publicado no commit | |
| **G4** | fingerprint único nos 210 (CSV não entra no hash — validar por re-sim: as 3 afetadas mudam, o resto Δ=0) | |
| **G5** | censo re-medido com o saldo REAL contra o declarado; docs/aging/HTML | |

## Estado

SEM OBJETO 2026-08-21 (13:5x) — **a correcao ja existia desde `a9541ec`
(2026-08-13, "7 CSVs corrigidas, c1 da tabela")**. A geracao desta execucao
produziu bytes IDENTICOS aos vigentes (git diff vazio nas 3) porque usa o
mesmo instrumento e a mesma Tabela — e por isso as metricas re-simuladas
sairam bit-identicas ao store. 5a ERRATA do mapa de rotas: a recomendacao de
2026-08-06 que este prereg executava ja fora cumprida em 08-13, e o doc de
rotas de 08-20 a listou como "mesa" sem verificar o git da CSV. O que fica
de VALOR: (a) G1 re-validou as CSVs vigentes contra a Tabela 8 (±0,004 nas
11 ancoras — validacao independente da adocao a9541ec); (b) o piso do par
amp1p0<->T22 re-medido: MAE 0,0030 / sigma 0,0026 (o "0,0127/0,0192" citado
em docs esta vencido; nao muda `limite_sres` pois < 0,025); (c) a rota
"re-digitalizacao" da amp0p5 esta MORTA — a CSV dela ja e correta, o
0,1324/0,1795/0,0449 e contra dado bom, e a curva e form-limited genuina
(orfa de protocolo sem rota restante).
