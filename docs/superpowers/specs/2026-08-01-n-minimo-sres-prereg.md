# Prereg — n<6 ⇒ σ_res NÃO-JULGÁVEL (assinatura "tudo assinado", 2026-08-01)

Pendência do professor desde 2026-07-30 ("n<6 vira 'não julgável'?"),
assinada em 2026-08-01 ("tudo assinado, siga do melhor jeito possível").
Semântica declarada ANTES de implementar:

- **Regra**: com menos de **6 pontos** na janela da métrica, a 3ª perna
  (σ_res) não tem suporte estatístico — o tripé (afirmação de TRÊS
  pernas) **não pode ser afirmado**. A curva fica NO censo, vai a "fora",
  e recebe estatuto **declarada não-julgável** (não é reprovação do
  modelo; é ausência de suporte do dado — a declaração carrega o motivo).
- **Onde**: `N_MIN_SRES = 6` + condição em `_tripe_ok` (helper canônico);
  mesmo teste no `_censo` do meta-teste e na triagem (que já usa
  `N_MIN=6` para a classe `metric_limited_n_baixo` — fica coerente).
- **Simetria**: vale nos dois sentidos — curva que "passaria" e curva que
  "falharia" pelo σ com n<6 têm o mesmo estatuto (as 3 que falhavam JÁ
  estão declaradas desde 2026-07-31).

## Premeasure (congelado; store `3d432a65c7e8`, censo 203)

Exatamente **6** comparáveis com n<6: 3 já declaradas (IJPEM
0,50/0,55/0,65) e **3 no tripé que saem**: IJPEM 0,15 mm (n=4, σ 0,0087),
IJPEM 0,18 mm (n=5, σ 0,0103), `zhang19_fig4` (n=5, σ 0,0016).

## Gates

- **G1**: só as 3 curvas do premeasure mudam de estatuto
  (tripé→declarada); nenhuma outra curva do censo muda em NADA.
- **G2**: `resolvida/declarada` fica **177/203** (133+29+15) — a regra
  move estatuto, não resolve nem cria pendência; fila segue 26.
- **G3**: censo/_VIVAS/docs vivos/páginas re-sincronizados no mesmo
  commit; guardas verdes.
- Reverter = retirar a condição + as 3 entradas de `_DECLARADAS` no
  mesmo commit (documentado aqui).
