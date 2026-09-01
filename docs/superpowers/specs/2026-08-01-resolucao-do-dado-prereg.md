# Prereg — declaração data-limited por RESOLUÇÃO do dado (critério global)

**2026-08-01** · sequência do "ok" do professor à recomendação 2 (rota das
3 da fila do YANG_2023_IJPEM após o PDF ficar inacessível). Critério
declarado ANTES da varredura; a hipótese consta na nota de aparato do
IJPEM desde 2026-07-28 ("Testar isso exige critério declarado antes — não
fazer post-hoc").

## Critério (irmão do metric-limited de colapso, já assinado)

Uma curva é **data-limited por resolução** quando a **mediana** de
|Δ(F/F₀)| entre pontos CONSECUTIVOS do dado, computada nos vetores da
métrica do store (`metric_data`, pós-trim), é **≥ META_MAX = 0,10** — o
passo típico do próprio dado vale a tolerância inteira da perna de pico:
entre dois pontos medidos o dado não restringe a curva a menos do que o
passo, então res.máx e σ_res medem o ESPAÇAMENTO DA AMOSTRAGEM, não o
modelo. (O metric-limited de colapso usa `max|Δdado| > 0,25` — pico; este
usa a MEDIANA — resolução crônica, não um degrau isolado.)

- Aplicação **GLOBAL** (203 comparáveis), não só ao IJPEM — critério que
  só varre a fonte que o motivou seria cherry-picking.
- Só muda estatuto de curva **fora do tripé e sem estatuto** (exceção e
  declaração existentes supersedem; curva no tripé não precisa).
- **Reabre com dado denso** (re-digitalização das figuras se o PDF um dia
  entrar; para o IJPEM os CSVs são de tabela/master-curve, 4–8 pts).

## Previsão registrada (falsificável, da tabela da nota de aparato)

No IJPEM: 0,30 mm (salto ~0,17) e 0,35 mm (~0,12) entram; **0,25 mm
(~0,08) NÃO entra** e fica na fila por mérito próprio. Fora do IJPEM:
desconhecido — a varredura diz.

## Gates

- **G1**: varredura computada dos vetores do store com o MESMO helper de
  censo (`caso_comparavel`, `limite_sres`); lista completa publicada no
  resultado (curva, fonte, mediana do salto, estatuto atual).
- **G2**: nenhuma curva no tripé ou já resolvida muda de estatuto.
- **G3**: declarações novas entram em `_DECLARADAS` com o critério e o
  número (mediana medida), marcadas "por delegação (mandato 2026-07-30;
  'ok' de 2026-08-01 à recomendação 2)".
- **G4**: censo/_VIVAS/docs/páginas re-sincronizados no mesmo commit.
