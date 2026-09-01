"""A prova de uma exceção assinada tem de continuar VERDADEIRA no store de hoje.

## Por que este arquivo existe

As exceções assinadas são **material de publicação** do professor: cada uma afirma
que o erro do modelo naquela curva está dentro do piso de repetibilidade do próprio
dado, e cita **os números**. A guarda que já existia
(`test_meta_numeros_nao_envelhecem`, ramo de assinatura redundante) responde a uma
pergunta **diferente**: *"esta curva passou a fechar por mérito?"* — o precedente K6.
Nada verificava o inverso: *"o número que a prova CITA ainda é o número que o store
MEDE?"*

O risco não é hipotético. O store foi re-carimbado várias vezes por dia durante a
campanha (12 adoções em 2026-08-19/20, censo 144 → 165), e um re-carimbo move as
pernas da curva **sem tocar no texto da prova**. Uma prova que cite
`res.máx 0,1320/0,1866` continua *parecendo* válida depois de a curva passar a medir
0,19 — e o texto é o que vai para o artigo.

## ⚠️ O erro que este teste evita, medido em 2026-08-20

A primeira versão da auditoria comparou **todo** número com 3+ decimais citado na
prova contra as pernas vigentes, e acusou **10 das 22**. Era falso positivo inteiro:
prova cita legitimamente

* **pisos e limites** (o denominador — `0,1866`, `0,0698`);
* **scatter / desvio-à-mediana** (`0,328`, `0,349`) — propriedade do **DADO**, que
  não se move quando o modelo se move;
* **valores históricos RETRATADOS**, preservados de propósito (`0,257/0,083`, o piso
  inválido que a P-15 retratou).

⇒ o teste tem de ser **estreito**: só os pares `valor/limite` no formato que as
provas F7 usam, e neles só o **valor** é confrontado com a perna. Contar denominador
como órfão é ler o instrumento fora do domínio.

## O que é e o que NÃO é verificado

* **É:** todo par `res.máx A/B`, `σ A/B`, `MAE A/B` — `A` bate com a perna vigente
  (1e-4) **e** `A <= B`.
* **NÃO é:** o scatter das provas F5. Ele é propriedade do dado; mudaria numa
  **re-digitalização** (D-W, D-R, D-S, D-U, pico espúrio), não num re-carimbo. Guardá-lo
  contra as pernas do modelo seria o falso positivo descrito acima. Fica **declarado
  como descoberto**, não silenciosamente omitido.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import bolt_analysis_studio.validation.report_html as rh

_STORE = Path(__file__).resolve().parents[1] / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"

# formato das provas F7: "res.máx 0.1320/0.1866 · σ 0.0395/0.0698"
_PADROES = (
    ("res.max", r"res\.m[aá]x\s+(\d+\.\d+)\s*/\s*(\d+\.\d+)", "maxerr"),
    ("sigma", r"σ\s+(\d+\.\d+)\s*/\s*(\d+\.\d+)", "resid_std"),
    ("MAE", r"MAE\s+(\d+\.\d+)\s*/\s*(\d+\.\d+)", "mae"),
)


def _store() -> dict:
    s = json.loads(_STORE.read_text(encoding="utf-8"))
    return s.get("cases", s)


def _pares(prova: str):
    """(rotulo, valor_citado, limite_citado, campo_do_store) de cada par na prova."""
    for rot, pat, campo in _PADROES:
        for val, lim in re.findall(pat, prova):
            yield rot, float(val), float(lim), campo


def test_toda_excecao_tem_registro_no_store():
    """Exceção sobre curva que não existe no store é prova sem objeto."""
    recs = _store()
    orfas = sorted(cid for cid in rh._EXCECOES if cid not in recs)
    assert not orfas, f"exceção assinada sem registro no store: {orfas}"


def _quebras_de_sincronia(recs: dict) -> list[str]:
    """O número que a prova CITA x o número que `recs` MEDE. Fatorado para que o
    teste de perturbação exercite ESTA função, e não uma cópia dela."""
    out = []
    for cid, prova in sorted(rh._EXCECOES.items()):
        rec = recs.get(cid)
        if rec is None:
            continue
        for rot, val, _lim, campo in _pares(prova):
            cur = rec.get(campo)
            if cur is None or abs(val - cur) > 1e-4:
                out.append(f"{cid} [{rot}]: prova cita {val:.4f}, store mede {cur}")
    return out


def _quebras_de_verdade(recs: dict) -> list[str]:
    """`valor <= limite` — a afirmação em si, não só a sincronia do número."""
    out = []
    for cid, prova in sorted(rh._EXCECOES.items()):
        rec = recs.get(cid)
        if rec is None:
            continue
        for rot, _val, lim, campo in _pares(prova):
            cur = rec.get(campo)
            if cur is not None and cur > lim:
                out.append(f"{cid} [{rot}]: {cur:.4f} > limite citado {lim:.4f}")
    return out


def test_valor_citado_bate_com_a_perna_vigente():
    quebras = _quebras_de_sincronia(_store())
    assert not quebras, (
        "PROVA DE EXCEÇÃO VENCIDA — o texto vai para o artigo:\n  " + "\n  ".join(quebras)
    )


def test_a_prova_ainda_e_verdadeira():
    quebras = _quebras_de_verdade(_store())
    assert not quebras, (
        "A AFIRMAÇÃO da exceção é falsa no store de hoje:\n  " + "\n  ".join(quebras)
    )


def test_ha_pares_para_verificar():
    """Meta-teste: se o formato das provas mudar, os outros dois ficam VÁCUOS.

    Um teste que não encontra nada passa em silêncio, o que é pior que falhar. Hoje
    há 4 pares (as 2 exceções F7 × 2 pernas cada). Se cair a zero, o `_PADROES`
    deixou de casar o formato e a guarda está morta sem avisar.
    """
    n = sum(1 for _cid, prova in rh._EXCECOES.items() for _ in _pares(prova))
    assert n >= 4, (
        f"só {n} pares valor/limite casaram — o formato das provas mudou e "
        f"`_PADROES` precisa acompanhar, senão as guardas passam vácuas"
    )


def test_scatter_das_f5_fica_declarado_como_nao_verificado():
    """O que este arquivo NÃO cobre tem de estar visível, não omitido.

    As provas F5 citam scatter de réplica (propriedade do dado). Elas mudariam numa
    re-digitalização, não num re-carimbo — e confrontá-las com as pernas do modelo foi
    exatamente o falso positivo de 10-em-22 que o docstring registra. Este teste fixa
    que a distinção está escrita, para o próximo leitor não "consertar" a omissão.
    """
    doc = Path(__file__).read_text(encoding="utf-8")
    assert "propriedade do dado" in doc
    assert "re-digitaliza" in doc
    # e que existem, de fato, provas sem par valor/limite (as F5)
    sem_par = [cid for cid, p in rh._EXCECOES.items() if not list(_pares(p))]
    assert sem_par, "nenhuma prova sem par — a distinção F5/F7 deixou de existir"


# ---------------------------------------------------------------------------
# O OUTRO LADO DO ESTATUTO: as 13 DECLARADAS
#
# `declarado_total` (200) = tripé + exceções + declaradas, e até 2026-08-20 só as
# exceções tinham guarda. As declaradas dividem-se em duas naturezas, e **só uma é
# verificável**:
#
# * **medição** — `n < 6` (σ_res sem suporte) e `data-limited por resolução`
#   (mediana |Δdado| ≥ 0,10). Estas citam números que o store mede ⇒ envelhecem, e
#   são as que os testes abaixo cobrem.
# * **juízo** — fora de escopo (material/junta apertada), órfã de protocolo,
#   proveniência ("Illustration of self-loosening"). Não há número do store que as
#   confirme ou refute: mudam por decisão do professor ou por leitura do paper, não
#   por re-carimbo. **Declaradas aqui como NÃO verificáveis**, para que a ausência de
#   teste seja escolha registrada e não esquecimento.
# ---------------------------------------------------------------------------

_RE_N_MIN = re.compile(r"n\s*=\s*(\d+)\s*<\s*6")
_RE_RESOLUCAO = re.compile(r"\|Δdado\|\s*=\s*(\d+[.,]\d+).*?res\.máx\s*(\d+[.,]\d+)")


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def test_declaracao_n_menor_que_6_ainda_vale():
    """O `n` citado é o `n` de hoje, segue < 6, e o helper canônico concorda.

    Três coisas, porque falham por caminhos diferentes: o número pode dessincronizar
    (re-digitalização acrescenta ponto), o `n` pode chegar a 6 (a declaração perde o
    fundamento e a curva volta a ser julgável), e `sres_para_censo` pode passar a
    devolver valor (a regra N_MIN_SRES mudou de limiar).
    """
    recs = _store()
    quebras = []
    achou = 0
    for cid, just in sorted(rh._DECLARADAS.items()):
        m = _RE_N_MIN.search(just)
        if not m:
            continue
        achou += 1
        rec = recs.get(cid, {})
        n_vig = len(rec.get("metric_data") or [])
        n_cit = int(m.group(1))
        if n_vig != n_cit:
            quebras.append(f"{cid}: declaração cita n={n_cit}, store tem n={n_vig}")
        if n_vig >= 6:
            quebras.append(f"{cid}: n={n_vig} >= 6 — a declaração perdeu o fundamento")
        if rh.sres_para_censo(rec) is not None:
            quebras.append(f"{cid}: sres_para_censo devolveu valor — n<6 não se aplica mais")
    assert achou >= 5, f"só {achou} declarações n<6 casaram o padrão (eram 5)"
    assert not quebras, "DECLARAÇÃO n<6 VENCIDA:\n  " + "\n  ".join(quebras)


def test_declaracao_por_resolucao_ainda_vale():
    """`mediana |Δdado| ≥ 0,10` e `res.máx ≤ mediana` — o critério P-10 pré-registrado."""
    recs = _store()
    quebras = []
    achou = 0
    for cid, just in sorted(rh._DECLARADAS.items()):
        m = _RE_RESOLUCAO.search(just)
        if not m:
            continue
        achou += 1
        rec = recs.get(cid, {})
        md = rec.get("metric_data") or []
        if len(md) < 2:
            quebras.append(f"{cid}: metric_data com {len(md)} pontos — sem passo para medir")
            continue
        passos = [abs(md[i + 1] - md[i]) for i in range(len(md) - 1)]
        passos.sort()
        k = len(passos)
        dmed = passos[k // 2] if k % 2 else (passos[k // 2 - 1] + passos[k // 2]) / 2
        cit_d, cit_mx = _num(m.group(1)), _num(m.group(2))
        mx = rec.get("maxerr")
        if abs(dmed - cit_d) > 1e-4:
            quebras.append(f"{cid}: mediana |Δdado| citada {cit_d:.4f}, vigente {dmed:.4f}")
        if mx is None or abs(mx - cit_mx) > 1e-4:
            quebras.append(f"{cid}: res.máx citado {cit_mx:.4f}, vigente {mx}")
        if dmed < 0.10:
            quebras.append(f"{cid}: mediana {dmed:.4f} < 0,10 — critério P-10 não vale mais")
    assert achou >= 1, "nenhuma declaração por resolução casou o padrão"
    assert not quebras, "DECLARAÇÃO POR RESOLUÇÃO VENCIDA:\n  " + "\n  ".join(quebras)


def test_declaracoes_de_juizo_ficam_declaradas_como_nao_verificaveis():
    """As de escopo/protocolo/proveniência não têm número — e isso é explícito.

    Sem este teste, alguém que contasse "6 declarações cobertas de 13" leria as outras
    7 como lacuna de rigor, quando são de outra natureza. Aqui a partição é medida: o
    que sobra depois das verificáveis tem de ser exatamente juízo.
    """
    verificaveis, juizo = [], []
    for cid, just in rh._DECLARADAS.items():
        (verificaveis if (_RE_N_MIN.search(just) or _RE_RESOLUCAO.search(just))
         else juizo).append(cid)
    assert len(verificaveis) + len(juizo) == len(rh._DECLARADAS)
    assert verificaveis, "nenhuma declaração verificável — os 2 testes acima ficaram vácuos"
    # "esgotamento" entrou em 2026-08-21 (decisão (b) do item 8): a classe
    # "form-limited por ESGOTAMENTO MEDIDO" é juízo-com-números — cada
    # falsificação é verificável uma a uma (par_de_taxas §5-§7), mas o
    # "não há mais rota" é juízo qualificado, não regra automática como
    # n<6/resolução. A marca torna a natureza explícita, como o teste pede.
    marcas = ("escopo", "protocolo", "proveniência", "Illustration",
              "ESGOTAMENTO")
    sem_marca = [c for c in juizo if not any(k in rh._DECLARADAS[c] for k in marcas)]
    assert not sem_marca, (
        "declaração que não é verificável NEM se identifica como juízo — "
        f"natureza indeterminada: {sem_marca}"
    )


@pytest.mark.parametrize("campo", ["maxerr", "resid_std"])
def test_guarda_pega_perturbacao(campo):
    """Validação por perturbação: a guarda tem de FALHAR num store adulterado.

    Sem isto, "testes verdes" não distingue *guarda funcionando* de *guarda que não
    olha nada* — e a 1ª versão deste próprio arquivo trazia uma perturbação VÁCUA
    (assertava `0,05 > 1e-4`, aritmética que não exercitava a guarda). Aqui a
    perturbação passa pelas MESMAS funções que os testes reais usam, sobre uma cópia
    em memória; **o store no disco não é tocado.**
    """
    recs = _store()
    alvo = next(
        (cid for cid, p in sorted(rh._EXCECOES.items())
         if cid in recs and any(c == campo for *_, c in _pares(p))),
        None,
    )
    assert alvo, f"nenhuma exceção com par sobre {campo} — perturbação não aplicável"

    # baseline: com o store real as duas guardas estao limpas
    assert not _quebras_de_sincronia(recs)
    assert not _quebras_de_verdade(recs)

    limite = next(l for _r, _v, l, c in _pares(rh._EXCECOES[alvo]) if c == campo)
    adulterado = {k: dict(v) for k, v in recs.items()}
    adulterado[alvo][campo] = limite + 0.05   # acima do limite CITADO

    sinc = _quebras_de_sincronia(adulterado)
    verd = _quebras_de_verdade(adulterado)
    assert any(alvo in q for q in sinc), (
        f"a guarda de SINCRONIA não viu {campo} de {alvo} sair do valor citado"
    )
    assert any(alvo in q for q in verd), (
        f"a guarda de VERDADE não viu {campo} de {alvo} passar do limite citado"
    )
    # e a perturbacao tem de ser LOCAL: nenhuma outra curva acusada
    assert len([q for q in sinc if alvo not in q]) == 0, f"contaminou outras: {sinc}"
