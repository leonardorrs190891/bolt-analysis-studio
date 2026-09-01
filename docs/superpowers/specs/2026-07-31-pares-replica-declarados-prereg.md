# Prereg — PARES DE RÉPLICA DECLARADOS na maquinaria de pisos

**2026-07-31 (noite)** · continuação autorizada do arco LU (P4 → este passo
→ re-adoção → P6 se sobrar). Mudança D1-adjacente em `_pisos_medidos`.

## Problema (medido)

A chave mecânica de pareamento `(fonte, δ, F_amp, modo)` exige F_amp EXATO.
Réplicas reais têm F₀ ALCANÇADO distinto (aperto nunca repete): os 3 pares
fig14×fig18/20 do LU diferem **4,2 % / 5,7 % / 14,1 %** — nenhum pareia.
Tolerância global não serve: ±8 % pega 2 pares e perde o de 14 %, e roça os
degraus de 10 % da varredura de F₀ do liu2017 (falso-par catastrófico).

## Desenho (congelado)

`_PARES_REPLICA_DECLARADOS` em `report_html.py` — lista explícita
`(cid_a, cid_b, proveniência)`, consumida por `_pisos_medidos` como
famílias ADICIONAIS (mesma via de janela-comum interpolada). Mesmo padrão
idiomático de `_EXCECOES`/`_DECLARADAS`: cada par carrega prova; zero risco
às outras fontes; a chave mecânica continua para as famílias automáticas.

Pares declarados (3, todos com a condição nominal na proveniência):
1. `fig14_amp0p25_long ↔ fig18_amp0p25` (22 N·m / 0,25 mm; §3.1.3×Fig 18)
2. `fig14_amp0p5_long ↔ fig18_amp0p5` (22 N·m / 0,5 mm)
3. `fig14_amp1p0_long ↔ fig20_T22Nm` (22 N·m / 1,0 mm; o lado fig18_amp1p0
   é duplicata da T22 — o par declarado usa o membro canônico)

## Efeitos previstos (congelados; a execução confere)

Famílias do LU_2024: 1 (digitalização) → **4**. `por_fonte` = mediana das
famílias por métrica ⇒ MAE ~0,19 · σ ~0,10 · mx ~0,39 (medianas de
{0,013/0,096/0,283/0,634} etc.). `limite_sres(LU) = max(0,025; ~0,10)`.
Tripé: sem mudança esperada (o MAE segue reprovando as fora). O que abre é
a rota F7 (prova de piso): T16 0,123 / T22 0,110 / T28 0,119 / amp0p5
0,061 ≤ FORTE(0,19/√2=0,134); T10 0,209 fica FORA até da PROVA (0,19) —
honesto. Assinaturas F7 = passo separado, curva a curva.

## Gates

* **G1 monotonia**: nenhuma fonte PERDE piso nem tem piso reduzido (só o
  LU ganha famílias).
* **G2 censo**: re-medido; toda mudança enumerada (esperado: tripé
  estável; `limite_sres(LU)` sobe para ~0,10).
* **G3 docs**: `_VIVAS` re-sincronizados no MESMO commit; guards verdes
  (incl. concordância com FLOORS legado — LU não tem entrada legada desde a
  retratação de hoje).
* **G4 bit-idêntico fora do LU**: `por_fonte` das outras 27 fontes idêntico
  antes/depois (o dict só tem pares do LU).
