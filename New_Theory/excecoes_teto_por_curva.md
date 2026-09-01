# Teto de MAE POR CURVA das 22 exceções vivas — capacidade vs disciplina

**2026-08-15 ~12:00 · pergunta do professor:** *"consegue reduzir o MAE dos
exceção em todas as curvas para níveis menores?"* · store `85e8104420b0` ·
sonda só-leitura (sandbox `BAS_ADOPTED_CONFIGS`), **NADA adotado**.

## Resposta curta

**Sob as regras da campanha (constantes compartilhadas + gates + procedência):
não** — é exatamente por isso que são exceções; cada uma carrega falsificações
pré-registradas. **Por curva (constantes per-case livres): 9 das 22 caem, 13
já estão no teto.** A sonda mediu descida coordenada em 7 alavancas × 2
passadas por curva (célula "sem override" reproduz o store como sanidade;
teto = cota INFERIOR da capacidade, com estas alavancas).

## A tabela (MAE vigente → teto per-curve)

| curva | vigente | teto | mx@teto | σ@teto | leitura |
|---|---:|---:|---:|---:|---|
| chu test3 | 0,0800 | **0,0191** | 0,0957 | 0,0259 | **FECHA O TRIPÉ per-curve** (σ ≤ 0,0296 da fonte) |
| chu test2 | 0,1567 | 0,0969 | 0,3097 | 0,1217 | −38 %, não fecha |
| chu test4 | 0,1352 | 0,0832 | 0,3170 | 0,1139 | −38 %, não fecha |
| chu test8 | 0,1613 | 0,0951 | 0,2071 | 0,1105 | −41 %, não fecha |
| chu test7 | 0,1499 | 0,1387 | 0,2284 | 0,1560 | −7 % |
| chu test9 | 0,0459 | 0,0336 | **0,0802** | 0,0401 | MAE+mx fecham; σ 1,35× |
| yang21 amp0p8 | 0,0542 | 0,0340 | 0,1426 | 0,0443 | −37 %, mx fora |
| yang21 fig2 | 0,0404 | 0,0297 | 0,1326 | 0,0444 | −26 %, mx fora |
| bauer fig6 ×4 + fig8 ×2 | 0,024–0,078 | **= vigente** | — | — | **zero alavanca move** (scatter de réplicas) |
| eccles ×6 | 0,043–0,147 | **= vigente** | — | — | **zero alavanca move** (contorno axial inexistente) |
| jcsr outdoor | 0,0621 | **= vigente** | — | — | cliff de corrosão |
| liu2020 zinc | 0,0526 | **= vigente** | — | — | trinca de fadiga |

Ótimos per-curve (registro): test3 `{emb 1,6µm · N_emb 1000 · C_creep 0 ·
slip_onset_W 500 · tr_loose_gain 0,5}`; test9 `{N_emb 200 · C_creep 3e-11}`
sobre o emb adotado; test2/4/8 combinam emb/N_emb/onset/chute-tardio.

## O que isto significa (e por que NÃO adotar)

1. **13 das 22 já estão no teto** — nenhuma constante, nem per-curve, reduz o
   MAE delas. São limitadas por FORMA ou DADO (scatter de réplicas, contorno
   axial, corrosão, fratura), exatamente como os dossiês dizem. A resposta
   para elas é *não — o número vigente É o teto*.
2. **As 9 que caem são o retrato da limitação de TRANSFERÊNCIA**: o modelo TEM
   forma para cada curva do CHU isolada (test3 fecha o tripé inteiro!), mas os
   ótimos são disjuntos entre curvas da MESMA fonte — a assinatura M⁻/µ(N) do
   dossiê de 5 degraus, agora com números per-curve. Adotar esses ótimos =
   22 conjuntos de constantes sem procedência = o overfitting que a doutrina
   (ratificada em 2026-08-13, item D) proíbe — e destruiria o valor
   científico das exceções para o artigo, que é documentar o limite honesto.
3. **Para o artigo**, a coluna "teto per-curve" separa as exceções em duas
   classes publicáveis: *transfer-limited* (CHU ×6, YANG ×2 — a física serve,
   as constantes não compartilham) e *form/data-limited* (BAUER ×6, ECCLES ×6,
   JCSR, LIU_2020 — nem constantes livres movem).

## Erro de instrumento pego no caminho (e consertado)

A 1ª medição do test9 deletou o `emb_um=9,5` ADOTADO ao limpar o per_case (o
probe substituía em vez de MESCLAR) — base 0,0630 ≠ store 0,0459, curva
marcada INVÁLIDA pela própria sanidade e re-medida com o input preservado.
Mesma classe do gotcha D-AB ("grupo nasce mínimo"): célula de sonda nunca
pode remover input adotado.

## Reprodutibilidade

Sonda: `excecoes_teto.py` + re-medição test9 (scratchpad da sessão 3d12ac81);
resultado bruto: `excecoes_teto_result.json`. Alavancas: emb_um, N_emb,
C_creep, k_wear_spec, slip_onset_W, (k_late_amp, crash_trigger_frac),
tr_loose_gain. Critério de melhora: ΔMAE ≥ 0,0005.
