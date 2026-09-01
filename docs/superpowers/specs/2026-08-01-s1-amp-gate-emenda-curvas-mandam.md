# EMENDA ao PR-3 s1_amp_gate — "curvas mandam" (professor, 2026-08-01)

Decisão em sessão após o INCONCLUSIVO: entre a D-N da Fig. 4 e as curvas
digitalizadas (discordância de N₉₅ de 3–5× nas duas direções), **as
curvas são a autoridade**. Consequência declarada: a D-N do paper fica
**NÃO-reproduzida** pelo modelo adotado — registrado no `prov` do cfg e
no resultado; o G1 original (5/6 na D-N) permanece como validação da
FORMA, não da parametrização.

## Alvos novos (N₉₅ lidos das PRÓPRIAS curvas do store, congelados)

| amp | N₉₅ curva | amp | N₉₅ curva |
|---:|---:|---:|---:|
| 0,25 | 62.500 | 0,50 | 692 |
| 0,30 | 25.000 | 0,60 | 182 |
| 0,40 | 2.000 | 0,80 | 91 |

(`fig2_single` — mesma condição 0,8 mm com N₉₅=8, discordância 11× com a
amp0p8 — fica FORA do fit: dupla contagem da condição; julgada só no
gate de curvas.)

## Gates (imutáveis)

- **G1c**: fit de ≤3 números (δ*, p, floor) NOS 6 N₉₅ acima ⇒ modelo
  dentro de **3×** em ≥4/6.
- **G2c (o gate que manda)**: janela COMPLETA, 7 curvas da fonte — soma
  dos MAE das 4 fila cai ≥20 % **e nenhuma das 7 piora >+0,01 em
  qualquer perna**. (O fit usa só os N₉₅ — resumo de 1 ponto por curva;
  o julgamento é a curva inteira nas 3 pernas: mesmo espírito do E2,
  vida-como-input.)
- **G3c**: fora da fonte nada muda (cfg per-rig; engine default-inerte).
- **G4c**: procedência dos 3 números = N₉₅ das curvas (tabela acima);
  nota explícita "D-N Fig. 4 não-reproduzida por decisão 'curvas
  mandam'".
- **G5c**: adoção ⇒ fingerprint muda ⇒ batch re-stamp uniforme +
  `exemplo_m12_sintetico` direto + censo/_VIVAS/docs/páginas/suíte no
  mesmo commit. Falha em qualquer gate ⇒ sem adoção, relatório.

## Previsão registrada

A escada de g implícita das curvas tem inclinação log-log ~5–10 sem o
platô de fundo da D-N ⇒ floor menor (≤1,5e-4) e a tensão vai aparecer
entre 0,6 (g≈0,05) e 0,8 (g≈0,9) — o risco de G1c é a ponta 0,8 de novo,
agora por ser rápida demais para o Hill que serve o meio.
