# Excecoes assinadas — material do artigo

Gerado em 2026-08-16 por `New_Theory/export_excecoes_artigo.py` a partir do
store canonico (fingerprint `20be19aabe11`).

- **23** excecoes vivas: 21 por scatter de replicas (F5, assinada
  2026-07-28) + 2 por prova de piso (F7, assinada 2026-07-29).
- A fonte de verdade e' `_EXCECOES` em `report_html.py` (uniao
  F5+F7); este export NAO mantem lista propria.
- `tabela_excecoes.tex` requer `booktabs` e LuaLaTeX/XeLaTeX.
- Coluna `teto p/curva`: cota INFERIOR do MAE com constantes POR
  CURVA (sonda 2026-08-15, `excecoes_teto_por_curva.md`; NADA
  adotado). `=` = nenhuma alavanca move a curva, o vigente ja e' o
  teto (form/data-limited); numero = cai per-curve mas as
  constantes nao compartilham (transfer-limited).
- A leitura de estatuto: excecao conta como RESOLVIDA, nunca como
  no tripe (secao `#sec-excecoes` do report mestre).
