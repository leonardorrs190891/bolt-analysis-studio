# -*- coding: utf-8 -*-
"""Split held-out MECÂNICO para os preregs da campanha de calibração.

Por que existe: o desenho leitura/held-out matou DOIS sobreajustes em
2026-07-29/30 antes de virarem adoção — o `slip_onset_W` único (trio: as 3
held-out reprovaram, F5) e teria matado o `emb` re-lido (9 de 12 métricas
pioraram). Nas duas vezes o split foi montado à mão dentro da sonda, e a parte
que carrega a honestidade — *o critério é declarado ANTES e não olha o erro* —
dependia de disciplina, não de código. Este módulo torna isso mecânico:

  * o split nasce de um CRITÉRIO NOMEADO (função + nome), aplicado item a item;
  * o objeto é CONGELADO (frozen dataclass): não há como re-particionar depois
    de ver métricas sem construir outro objeto — o que aparece no diff;
  * held-out vazio é ERRO, não aviso: sem conjunto de generalização, um fit
    "que funcionou" é um sobreajuste não testado (a lição do trio: se eu
    tivesse lido o W das 7 curvas, todas melhorariam e eu teria adotado 7
    números disfarçados de constante);
  * o veredito de generalização conta pioras com a MESMA tolerância dos gates
    (+0,01) e devolve medianas antes/depois — o formato que G2/G6 dos preregs
    já usam.

O critério deve ser de RESOLUÇÃO DO DADO (amostragem), nunca de resultado —
`feature_resolvability_matrix.md` cataloga os três critérios já declarados
(queda inicial, joelho, platô).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Sequence, Tuple


@dataclass(frozen=True)
class HoldoutSplit:
    """Partição congelada leitura/held-out, com o critério que a gerou."""
    criterio: str
    reads: Tuple[Any, ...]
    held: Tuple[Any, ...]

    def __post_init__(self):
        if not self.criterio or not str(self.criterio).strip():
            raise ValueError(
                "o critério do split tem de ser NOMEADO — split anônimo não "
                "deixa rastro no prereg nem no resultado")
        inter = set(self.reads) & set(self.held)
        if inter:
            raise ValueError(f"reads e held não são disjuntos: {sorted(inter)}")
        if not self.reads:
            raise ValueError(
                "conjunto de LEITURA vazio: não há de onde ler a âncora — "
                "o critério está estrito demais para esta fonte")
        if not self.held:
            raise ValueError(
                "held-out VAZIO: sem conjunto de generalização, o fit é um "
                "sobreajuste não testado (lição do trio, F5). Se o critério "
                "resolve todas as curvas, segure por OUTRO eixo declarado "
                "(amplitude alternada, F0, réplica) — nunca prossiga sem held")


def split_por_criterio(itens: Sequence[Any],
                       resolvel: Callable[[Any], bool],
                       criterio: str) -> HoldoutSplit:
    """Particiona por um predicado de RESOLUÇÃO DO DADO (nunca de erro).

    `resolvel(item) == True` ⇒ o item pode LER a âncora; False ⇒ held-out.
    O predicado deve olhar amostragem/feature do dado — se ele consultar
    métrica de erro, o split deixa de ser pré-registrável (é escolha por
    resultado com outro nome), e nenhum código detecta isso: é a única parte
    que continua sendo disciplina."""
    reads = tuple(i for i in itens if resolvel(i))
    held = tuple(i for i in itens if not resolvel(i))
    return HoldoutSplit(criterio=criterio, reads=reads, held=held)


def veredicto_generalizacao(antes: Dict[Any, float],
                            depois: Dict[Any, float],
                            split: HoldoutSplit,
                            tol: float = 0.01) -> Dict[str, Any]:
    """O número que decide o gate de generalização, no formato dos preregs.

    `antes`/`depois` = métrica por item (ex.: res.máx). Só o HELD-OUT entra no
    veredito — as leituras melhorarem não prova nada (elas informaram a
    âncora). Devolve pioras (> tol), medianas e o veredito `generaliza`
    (mediana do held não subiu E menos da metade piora)."""
    faltam = [k for k in split.held if k not in antes or k not in depois]
    if faltam:
        raise KeyError(f"held-out sem métrica antes/depois: {faltam}")
    hd = sorted(split.held)
    pioras = [k for k in hd if depois[k] > antes[k] + tol]
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else float("nan")
    m_a, m_d = med([antes[k] for k in hd]), med([depois[k] for k in hd])
    return {
        "criterio": split.criterio,
        "n_reads": len(split.reads), "n_held": len(hd),
        "pioras_held": tuple(pioras),
        "mediana_held_antes": m_a, "mediana_held_depois": m_d,
        "generaliza": (m_d <= m_a + 1e-12) and (len(pioras) * 2 < len(hd)),
    }
