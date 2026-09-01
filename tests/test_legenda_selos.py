# -*- coding: utf-8 -*-
"""Invariantes dos SELOS da lista mestre e da legenda que os explica.

Existe por causa de um defeito MEDIDO em 2026-07-31: `_badges` ficou na régua
VENCIDA de duas pernas — comparava o MAE contra `META` (= `META_MAX` = 0,10, o
alias legado) em vez de `META_MAE` = 0,05, e **não olhava a 3ª perna**. Como
`_tripe_ok` já julgava as três, toda curva que reprovava só pelo σ_res — a perna
que hoje manda na maioria das fora — saía com um `✖` de rótulo VAZIO e
`title="viola a meta por "`. Eram **34 selos mudos** no documento mestre, e
nenhum teste reclamava: o defeito não quebra nada, só cala.

Por que testar aqui e não confiar no `test_meta_numeros_nao_envelhecem`: aquele
persegue NÚMERO divergente em prosa; este persegue VOCABULÁRIO mudo no HTML.
Um selo que não diz nada tem número nenhum para envelhecer.
"""
import re

import pytest

from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.store import ValidationStore

# O selo carrega a descricao em `data-tip` (breve) + `data-tipx` (numeros), NAO
# em `title` — ver `_selo`: com `title` presente o navegador desenharia o
# tooltip nativo EM CIMA do nosso.
BDG = re.compile(r'<span class="bdg (\w+)"[^>]*?data-tip="([^"]*)"[^>]*>'
                 r'(.*?)</span>')
BDG_QUALQUER = re.compile(r'<span class="bdg (\w+)"([^>]*)>(.*?)</span>')


@pytest.fixture(scope="module")
def mestre():
    """HTML do mestre a partir do store canônico (só leitura, não simula)."""
    store = ValidationStore()
    records = all_records()
    if not store.all_ids():
        pytest.skip("store vazio — rode `report --all` antes")
    results = {r.case_id: store.get(r.case_id) for r in records}
    return rh.master_report_html(records, results), records, results


def _selos(html):
    return [(m.group(1), m.group(2), m.group(3)) for m in BDG.finditer(html)]


def test_nenhum_selo_de_reprova_sem_motivo(mestre):
    """O defeito original: `✖` sem nomear nenhuma perna.

    Duas assinaturas do mesmo mal, porque o rótulo e a descrição podem
    divergir: descrição vazia e rótulo com só o glifo."""
    html, _, _ = mestre
    selos = _selos(html)
    assert selos, "nenhum selo encontrado — o seletor mudou?"
    mudos_tip = [s for s in selos if not s[1].strip()]
    mudos_lab = [s for s in selos
                 if s[0] == "no" and s[2].strip() in ("&#10006;", "")]
    assert not mudos_tip, f"{len(mudos_tip)} selos com data-tip vazio"
    assert not mudos_lab, f"{len(mudos_lab)} selos com rótulo só de glifo"


def test_todo_selo_tem_descricao_e_rota_assistiva(mestre):
    """Todo selo desenhado precisa de `data-tip` E `aria-label`.

    O hover é rota de mouse: em toque não existe e leitor de tela não o vê. O
    `aria-label` é a rota assistiva (anunciado em modo de leitura, sem precisar
    de foco) e a legenda é a rota visível. **Não** se exige `tabindex`: com os
    selos focalizáveis a página ia a 687 paradas de Tab, 256 delas selos (37%),
    e o que o tooltip mostra já está nas colunas MAE / res.máx / σ_res da
    própria linha — mesmo critério que manteve os pontos do 3D fora do tab."""
    html, _, _ = mestre
    # Escopo: só os selos que ficam NA FRENTE DE UM CASO. A classe `.bdg` é
    # reusada em dois outros lugares que legitimamente não têm tooltip por
    # caso — as amostras dentro da própria legenda (exigir tooltip ali é
    # circular: a legenda É a descrição) e os chips "FONTE n/n" de
    # `_fontes_fechadas_html`. A 1ª versão deste teste varria o documento todo
    # e reprovou esses 14.
    celulas = re.findall(
        r'<a href="reports/[^"]+\.html">[^<]*</a>'
        r'((?:<span class="bdg[^>]*>.*?</span>)+)', html)
    assert celulas, "nenhuma célula de caso com selo encontrada"
    sem = []
    tabbable = []
    for cel in celulas:
        for c, a, _l in BDG_QUALQUER.findall(cel):
            if 'data-tip="' not in a or 'aria-label="' not in a:
                sem.append((c, a[:70]))
            if "tabindex=" in a:
                tabbable.append((c, a[:70]))
    assert not sem, f"{len(sem)} selos sem descrição/rota acessível: {sem[:3]}"
    # A ausência de `tabindex` é DELIBERADA e medida; se alguém reintroduzir,
    # a página volta a 687 paradas de Tab com 37% delas em selos.
    assert not tabbable, (
        f"{len(tabbable)} selos com `tabindex` — 256 paradas de Tab a mais; "
        f"a rota sem mouse é a legenda + as colunas da linha")


def test_selo_nao_usa_title_nativo(mestre):
    """`title` num selo faria o navegador desenhar DOIS tooltips.

    Regressão fácil de reintroduzir (o `title` era o mecanismo antigo), e
    invisível em teste de conteúdo: os dois tooltips dizem a mesma coisa."""
    html, _, _ = mestre
    com_title = [(c, a[:70]) for c, a, _l in BDG_QUALQUER.findall(html)
                 if "title=" in a]
    assert not com_title, (
        f"{len(com_title)} selos ainda com `title` — o tooltip nativo vai "
        f"aparecer junto com o `.tipbox`: {com_title[:3]}")


def test_tooltip_js_nao_usa_captura_de_ponteiro(mestre):
    """`setPointerCapture` retargeta o `click` para quem capturou.

    Foi assim que o link dos pontos do 3D morreu em 2026-07-29 (registrado no
    CLAUDE.md). Cada selo fica ao lado de um `<a>` para `reports/<cid>.html`;
    um tooltip que capture o ponteiro rouba esse clique. O tooltip também tem
    de ser `pointer-events:none`, senão intercepta o clique por cima."""
    html, _, _ = mestre
    # A CHAMADA, não a palavra: o documento cita `setPointerCapture` em dois
    # comentários (o do tooltip e o aviso pré-existente do painel 3D). A 1ª
    # versão deste teste proibia a palavra e reprovou o próprio comentário que
    # documenta a proibição.
    assert ".setPointerCapture(" not in html, (
        "tooltip usando captura de ponteiro — mata o clique do link do caso")
    assert "pointer-events:none" in html, (
        "`.tipbox` sem `pointer-events:none` — a caixa intercepta o clique")
    assert "position:fixed" in html, (
        "`.tipbox` precisa ser fixed: os selos estão dentro de `div.ovx` "
        "(overflow-x:auto), que recorta caixa absoluta")


def test_selo_nao_diverge_do_juiz(mestre):
    """`_badges` não pode reprovar sem que alguma perna exceda o limite.

    Se aparecer, é o selo reimplementando a régua e discordando de
    `_tripe_ok` — exatamente o que o rótulo `fora (?)` foi feito para gritar."""
    html, _, _ = mestre
    assert "fora (?)" not in html, (
        "selo 'fora (?)': o veredito reprova mas nenhuma perna excede — "
        "selo e juiz divergiram")


def test_selo_nomeia_as_tres_pernas_pelo_limite_certo(mestre):
    """Cada perna nomeada tem de estar de fato acima do SEU limite.

    Pega a regressão que originou o teste: MAE julgado contra 0,10. Uma curva
    com MAE em 0,07 (acima de `META_MAE`, abaixo de `META_MAX`) tem de aparecer
    com "MAE" no rótulo."""
    html, records, results = mestre
    pis = rh._pisos_medidos([(r.source, results[r.case_id]) for r in records
                             if results.get(r.case_id)])
    checados = 0
    for rec in records:
        res = results.get(rec.case_id)
        if res is None or not res.ok or res.resid_std is None:
            continue
        lim_sd = rh.limite_sres(rec.source, pis)
        if rh._tripe_ok(res, lim_sd) is not False:
            continue
        # `[^<]*</a>` e NÃO `.*?</a>`: com `.*?` o regex atravessava o
        # documento — a seção de exceções (2026-08-07) criou uma ocorrência do
        # link SEM selo ao lado, e o backtracking ia parar no `✖` de OUTRO
        # caso (media rep1 contra o rótulo do primeiro Yang da tabela). Sem
        # curinga, a ocorrência sem selo não casa e o `search` segue para a
        # linha de tabela certa.
        m = re.search(
            r'<a href="reports/%s\.html">[^<]*</a>'
            r'<span class="bdg no"[^>]*>&#10006; ([^<]*)</span>'
            % re.escape(rec.case_id), html)
        if not m:
            continue
        rotulo = m.group(1).strip()
        esperado = set()
        # regra n<6 (assinada 2026-08-01): sigma nao-julgavel NUNCA e'
        # violacao nomeada (o valor nao tem suporte) — o selo lista as
        # pernas JULGAVEIS violadas, e "σ n<6" quando nenhuma outra viola.
        # Mesmo helper do report, nunca uma 2a implementacao.
        if res.mae is not None and res.mae > rh.META_MAE:
            esperado.add("MAE")
        if res.maxerr is not None and res.maxerr > rh.META_MAX:
            esperado.add("res.máx")
        if rh.sres_para_censo(res) is None:
            if not esperado:
                esperado.add("σ n&lt;6")   # rotulo vem do HTML, com entidade
        elif res.resid_std > lim_sd:
            esperado.add("σ_res")
        assert set(rotulo.split("+")) == esperado, (
            f"{rec.case_id}: rótulo {rotulo!r} != pernas violadas {esperado} "
            f"(MAE {res.mae} / {rh.META_MAE}, res.máx {res.maxerr} / "
            f"{rh.META_MAX}, σ {res.resid_std} / {lim_sd})")
        checados += 1
    assert checados > 0, "nenhuma curva reprovada conferida — store mudou?"


def test_legenda_existe_e_cobre_todos_os_selos_desenhados(mestre):
    """A legenda tem de explicar TODO tipo de selo que o documento desenha.

    Sem isto a legenda vira decoração: um selo novo em `_badges` passaria sem
    entrada, e o leitor veria um símbolo sem verbete."""
    html, _, _ = mestre
    assert 'id="legendaselos"' in html, "toggle da legenda ausente"
    i = html.find('id="legendaselos"')
    bloco = html[i:html.find("</details>", i)]
    classes_desenhadas = {c for c, _t, _l in _selos(html)}
    classes_na_legenda = {m.group(1)
                          for m in re.finditer(r'<td><span class="bdg (\w+)"',
                                               bloco)}
    faltam = classes_desenhadas - classes_na_legenda
    assert not faltam, f"selos desenhados sem verbete na legenda: {faltam}"


def test_contagem_da_legenda_bate_com_os_selos_desenhados(mestre):
    """Número da legenda tem de vir do store, não da mão (§4.43).

    Cada caso é desenhado 2x (tabela única + tabela da fonte), então a
    contagem de CASOS é metade dos spans. Se alguém trocar o layout para uma
    tabela só, este teste falha e obriga a revisar a divisão — falhar aqui é o
    comportamento certo, não um falso positivo."""
    html, _, _ = mestre
    i = html.find('id="legendaselos"')
    bloco = html[i:html.find("</details>", i)]
    m = re.search(r'&#10004; trip.*?<td><b>(\d+)</b></td>', bloco, re.S)
    assert m, "linha do tripé não encontrada na legenda"
    n_legenda = int(m.group(1))
    spans_ok = sum(1 for c, _t, lab in _selos(html)
                   if c == "ok" and "trip" in lab)
    assert n_legenda == spans_ok // 2, (
        f"legenda diz {n_legenda} casos no tripé, mas o documento desenha "
        f"{spans_ok} selos (= {spans_ok / 2} casos)")


def test_legenda_declara_o_limite_por_fonte_da_terceira_perna(mestre):
    """Com `_SRES_POR_FONTE` ligado, a legenda não pode citar um σ único.

    O CLAUDE.md registra o erro inverso como armadilha medida: dizer "piso
    0,028" no singular inverte o argumento a favor do limite por fonte, porque
    o piso vai de ~0,001 a ~0,22 conforme a fonte."""
    html, _, _ = mestre
    i = html.find('id="legendaselos"')
    bloco = html[i:html.find("</details>", i)]
    if not rh._SRES_POR_FONTE:
        pytest.skip("3ª perna por fonte desligada — limite é global")
    assert "piso da fonte" in bloco, (
        "a legenda tem de dizer que o limite da 3ª perna é max(global; piso "
        "DA FONTE) — citar um valor único contradiz a régua vigente")
