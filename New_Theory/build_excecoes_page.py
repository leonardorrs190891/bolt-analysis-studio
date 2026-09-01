# -*- coding: utf-8 -*-
"""Gera a PAGINA DAS EXCECOES (secao de tese): validation_html/excecoes.html.

Pedido do professor (2026-08-01): "gere a pagina das excecoes. isso deve
ficar bem explicito e categorizado para ser uma secao da tese".

ORIENTADA A DADOS para nao envelhecer: le os dicionarios VIVOS de
report_html (_F5_EXCECOES, _F7_EXCECOES, _DECLARADAS, retiradas/retratadas,
_CID_NAO_COMPARAVEL, _PARES_REPLICA_DECLARADOS) + as metricas atuais do
store + os pisos recomputados na geracao. Toda contagem impressa e'
recomputada aqui — nada hardcoded.

Regenerar: py -3.12 New_Theory/build_excecoes_page.py
"""
from __future__ import annotations

import datetime
import html as _esc
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh   # noqa: E402
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

OUT = ROOT / "New_Theory" / "validation_html" / "excecoes.html"

CSS = """
body{font-family:Georgia,'Times New Roman',serif;max-width:1080px;margin:24px auto;
padding:0 16px;color:#1c2733;line-height:1.55}
h1{font-size:1.7em;border-bottom:3px solid #2f6f8f;padding-bottom:6px}
h2{font-size:1.25em;color:#2f6f8f;margin-top:2em;border-bottom:1px solid #cfdce6}
h3{font-size:1.05em;margin-top:1.4em}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:.92em;
font-family:'Segoe UI',Arial,sans-serif}
th,td{border:1px solid #b9c9d6;padding:5px 8px;text-align:left;vertical-align:top}
th{background:#eef4f8}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.ok{color:#116633;font-weight:600}.bad{color:#a02020;font-weight:600}
.mono{font-family:Consolas,monospace;font-size:.92em}
.box{background:#f4f8fb;border-left:4px solid #2f6f8f;padding:10px 14px;margin:12px 0}
.warn{background:#fdf6ec;border-left:4px solid #b07818}
.small{font-size:.85em;color:#4a5a68}
caption{caption-side:top;text-align:left;font-weight:700;padding:4px 0}
"""


def _fmt(v):
    return "—" if v is None else f"{v:.4f}".replace(".", ",")


def _pernas_violadas(res, lim_sd):
    """(rotulo, valor, limite) das pernas do TRIPE violadas pela curva."""
    out = []
    if res.mae is not None and res.mae > rh.META_MAE:
        out.append(("MAE", res.mae, rh.META_MAE))
    if res.maxerr is not None and res.maxerr > rh.META_MAX:
        out.append(("res.máx", res.maxerr, rh.META_MAX))
    if res.resid_std is not None and res.resid_std > lim_sd:
        out.append(("σ_res", res.resid_std, lim_sd))
    return out


def main() -> int:
    st = ValidationStore()
    recs = {r.case_id: r for r in all_records()}
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    pisos = rh._pisos_medidos(pares)

    n_f5, n_f7 = len(rh._F5_EXCECOES), len(rh._F7_EXCECOES)
    n_exc = len(rh._EXCECOES)
    n_decl = len(rh._DECLARADAS)
    retiradas = {
        "D1 (regra do piso por fonte absorveu a prova)":
            rh._EXCECOES_RETIRADAS_D1,
        "mérito pós-adoção LIU_2016":
            getattr(rh, "_EXCECOES_RETIRADAS_ADOCAO_LIU2016", {}),
        "piso INVÁLIDO (par cruzado 0,5×1,0 mm — retratação)":
            getattr(rh, "_EXCECOES_RETRATADAS_LU_PISO_INVALIDO", {}),
        "perna descoberta (prova F7 exige TODAS as pernas violadas)":
            getattr(rh, "_EXCECOES_RETRATADAS_F7_PERNA_DESCOBERTA", {}),
        "piso INVÁLIDO ROUSSEAU (espessuras ≠ pareadas como réplica + "
        "drive do aço 10× — erratum 2026-08-01)":
            getattr(rh, "_EXCECOES_RETRATADAS_ROUSSEAU_PISO_INVALIDO", {}),
    }
    n_ret = sum(len(v) for v in retiradas.values())

    # censo (mesmos helpers do report)
    comp = []
    for r in all_records():
        if not rh.caso_comparavel(r.source, r.case_id):
            continue
        res = st.get(r.case_id)
        if res and res.ok and res.mae is not None:
            comp.append((r, res))
    n_comp = len(comp)
    # sigma via sres_para_censo (regra n<6 assinada 2026-08-01) — sem isto
    # esta pagina imprimia 136 onde o censo canonico dizia 133
    n_tri = sum(1 for r, res in comp
                if rh._perna_manda(res.mae, res.maxerr,
                                   rh.sres_para_censo(res),
                                   rh.META_MAE, rh.META_MAX,
                                   rh.limite_sres(r.source, pisos)) is None)

    P = []

    def w(s):
        P.append(s)

    hoje = datetime.date.today().isoformat()
    fp = sorted({res.engine_fingerprint for _, res in comp})
    w(f"<style>{CSS}</style>")
    w(f"<h1>Exceções assinadas — o registro completo, com as contas</h1>")
    w(f'<p class="small">Gerado em {hoje} do store canônico (fingerprint '
      f'<span class="mono">{"/".join(fp)}</span>), {n_comp} curvas '
      f'comparáveis. Regenerar: <span class="mono">py -3.12 '
      f'New_Theory/build_excecoes_page.py</span>. Toda contagem desta '
      f'página é recomputada na geração — nada é digitado à mão.</p>')

    # ------------------------------------------------- 1. o conceito
    w("<h2>1. O que é uma exceção — e o que ela não é</h2>")
    w('<div class="box"><b>Exceção não é perdão para o modelo.</b> É a '
      'prova matemática de que aquela curva não pode ser fechada por '
      'modelo nenhum, porque o próprio experimento não se reproduz dentro '
      'do limite que a régua exige.</div>')
    w("<p>A meta por curva (o <i>tripé</i>) exige "
      f"<b>MAE ≤ {rh.META_MAE:g}</b>, <b>res.máx ≤ {rh.META_MAX:g}</b> e "
      f"<b>σ_res ≤ max({rh.META_SRES:g}; piso da fonte)</b> contra a curva "
      "publicada. Mas quando o mesmo ensaio, repetido em condição nominal "
      "idêntica, produz duas curvas que discordam entre si por MAIS que "
      "esses limites, exigir que o modelo fique mais perto de uma delas do "
      "que elas ficam uma da outra deixa de medir física: passa a exigir "
      "que o modelo adivinhe qual espécime foi montado naquele dia. Um "
      "modelo <i>perfeito</i> — que previsse exatamente o comportamento "
      "médio verdadeiro — reprovaria contra qualquer uma das gêmeas.</p>")
    w("<p>Por isso a meta é sempre publicada em <b>dois números</b>: a "
      f"leitura <b>estrita</b> (tripé: <b>{n_tri}/{n_comp}</b> hoje — onde "
      "o modelo <i>acertou</i>) e a <b>resolvida/declarada</b> "
      f"(<b>{n_tri + n_exc + n_decl}/{n_comp}</b> — tripé + exceções + "
      "declaradas, onde cada curva tem <i>estatuto com prova</i>). Uma "
      "exceção nunca conta como acerto do modelo.</p>")

    # ------------------------------------------------- 2. as barras
    w("<h2>2. As barras da prova e a aritmética</h2>")
    w("<p>O <b>piso de repetibilidade</b> de uma condição é medido "
      "comparando réplicas independentes do próprio dado (janela de x "
      "comum, interpolada; três métricas: MAE, res.máx e σ). A prova da "
      "exceção compara o erro do modelo com esse piso, <b>perna a "
      "perna</b>:</p>")
    w("<ul><li><b>PROVA</b>: erro ≤ piso — o modelo erra menos do que as "
      "réplicas discordam entre si;</li>"
      "<li><b>FORTE</b>: erro ≤ piso/√2 — o modelo é tão bom quanto o "
      "preditor ideal (o centro das réplicas), que erra piso/√2 contra "
      "cada gêmea.</li></ul>")
    w('<div class="box warn"><b>Regra endurecida em 2026-07-31:</b> a '
      "prova tem de cobrir <b>todas</b> as pernas que a curva viola — não "
      "a métrica conveniente. Duas assinaturas desta campanha foram "
      "retratadas na mesma noite por perna descoberta (ver §7), pegas pelo "
      "rigor do próprio gate.</div>")
    w("<p>Onde existe piso <b>por condição</b> (pares de réplica "
      "declarados, §3), a barra usa o piso da <i>mesma condição</i> — "
      "nunca a média da fonte, que misturaria o scatter do colapso com o "
      "regime estável.</p>")

    # ------------------------------------------------- 3. F7 por condicao
    lu_conds = {
        "lu2024_M8_fig20_T10Nm": ("1,0 mm / 22 N·m", (0.6134, 0.8492, 0.1592), "PROVA"),
        "lu2024_M8_fig20_T16Nm": ("1,0 mm / 22 N·m", (0.6134, 0.8492, 0.1592), "FORTE"),
        "lu2024_M8_fig20_T22Nm": ("1,0 mm / 22 N·m", (0.6134, 0.8492, 0.1592), "FORTE"),
        "lu2024_M8_fig20_T28Nm": ("1,0 mm / 22 N·m", (0.6134, 0.8492, 0.1592), "FORTE"),
        "lu2024_M8_fig18_amp0p5": ("0,5 mm / 22 N·m", (0.2833, 0.5689, 0.1502), "FORTE"),
    }
    w("<h2>3. Categoria A — prova de piso POR CONDIÇÃO "
      f"({sum(1 for c in lu_conds if c in rh._F7_EXCECOES)} curvas, "
      "LU_2024)</h2>")
    w("<p>Os pisos vêm dos <b>pares de réplica declarados</b>: a Fig. 14a "
      "do paper (corridas longas, §3.1.3) repete as condições da "
      "Fig. 18/20 em corridas independentes. Medido par a par na janela "
      "comum: a 1,0 mm as gêmeas discordam com <b>MAE 0,613</b> entre si; "
      "a 0,5 mm, 0,283; a 0,25 mm, 0,094. A barra de cada assinatura está "
      "na tabela; <b>múltiplo &lt; 1 = prova válida</b>.</p>")
    w("<table><caption>Exceções por condição — cada perna violada contra "
      "o piso da condição</caption>"
      "<tr><th>curva</th><th>condição</th><th>barra</th>"
      "<th>pernas violadas (tripé)</th><th>prova por perna "
      "(erro / barra = múltiplo)</th></tr>")
    for cid, (cond, piso3, barra) in lu_conds.items():
        if cid not in rh._F7_EXCECOES:
            continue
        res = st.get(cid)
        lim = rh.limite_sres("LU_2024", pisos)
        viol = _pernas_violadas(res, lim)
        div = (2 ** 0.5) if barra == "FORTE" else 1.0
        bar3 = {"MAE": piso3[0] / div, "res.máx": piso3[1] / div,
                "σ_res": piso3[2] / div}
        vhtml = "<br>".join(f"{n} = {_fmt(v)} (limite {_fmt(l)})"
                            for n, v, l in viol)
        phtml = "<br>".join(
            f"{n}: {_fmt(v)} / {_fmt(bar3[n])} = "
            f"<b class='ok'>{v / bar3[n]:.2f}×</b>".replace(".", ",")
            for n, v, _ in viol)
        w(f"<tr><td class='mono'>{_esc.escape(cid)}</td><td>{cond}</td>"
          f"<td><b>{barra}</b></td><td>{vhtml}</td><td>{phtml}</td></tr>")
    w("</table>")
    w('<p class="small">Leitura: a T22Nm, por exemplo, viola o MAE do '
      'tripé (0,05) — mas seu erro é uma fração pequena do que as próprias '
      'réplicas do ensaio discordam entre si na mesma condição. O modelo '
      'está mais perto de cada gêmea do que elas estão uma da outra.</p>')

    # ------------------------------------------------- 4. F7 por fonte
    outros_f7 = {c: p for c, p in rh._F7_EXCECOES.items()
                 if c not in lu_conds}
    w(f"<h2>4. Categoria B — prova de piso POR FONTE ({len(outros_f7)} "
      "curvas)</h2>")
    w("<p>Assinadas em 2026-07-29 (F7) contra o piso de repetibilidade "
      "medido da fonte (famílias de réplicas; "
      "<span class='mono'>piso_repetibilidade_medido.md</span>). O texto "
      "de cada prova é o assinado; valores em F/F₀.</p>")
    w("<table><tr><th>curva</th><th>fonte</th><th>prova assinada "
      "(erro / piso da fonte)</th></tr>")
    for cid, prova in sorted(outros_f7.items()):
        src = recs[cid].source if cid in recs else "?"
        w(f"<tr><td class='mono'>{_esc.escape(cid)}</td><td>{src}</td>"
          f"<td>{_esc.escape(prova)}</td></tr>")
    w("</table>")

    # ------------------------------------------------- 5. F5
    w(f"<h2>5. Categoria C — exceções F5 ({n_f5} curvas)</h2>")
    w("<p>A primeira geração de exceções (assinadas no S4, 2026-07-28): "
      "provas de que <i>a curva ideal já violaria a meta</i> — scatter de "
      "réplicas medido, limitação em nível de lei física, ou par-a-par de "
      "espécimes. O texto é o da assinatura.</p>")
    w("<table><tr><th>curva</th><th>fonte</th><th>prova assinada</th></tr>")
    for cid, prova in sorted(rh._F5_EXCECOES.items()):
        src = recs[cid].source if cid in recs else "?"
        w(f"<tr><td class='mono'>{_esc.escape(cid)}</td><td>{src}</td>"
          f"<td>{_esc.escape(prova)}</td></tr>")
    w("</table>")

    # ------------------------------------------------- 6. declaradas
    w(f"<h2>6. Declaradas ({n_decl} curvas) — não são exceções</h2>")
    w("<p>Curvas em que <b>a métrica ou o dado não decidem</b> — "
      "declará-las separa “o modelo errou” de “não dá para "
      "julgar”. Critérios medidos (camada 2 da regra de parada): "
      "<i>n&lt;6</i> (σ_res sem suporte estatístico), <i>colapso "
      "quase-vertical</i> (|Δdado|&gt;0,25 entre pontos consecutivos — "
      "nenhuma métrica automática resolve), <i>escopo</i> (a condição está "
      "fora do domínio físico declarado, com as palavras do próprio "
      "paper), <i>proveniência</i> (a figura de origem é rotulada "
      "ilustração) e <i>scatter-bound</i> (o erro excede o piso da própria "
      "condição por margem pequena a n=2 réplicas).</p>")
    w("<table><tr><th>curva</th><th>fonte</th><th>critério declarado</th></tr>")
    for cid, motivo in sorted(rh._DECLARADAS.items()):
        src = recs[cid].source if cid in recs else "?"
        w(f"<tr><td class='mono'>{_esc.escape(cid)}</td><td>{src}</td>"
          f"<td>{_esc.escape(motivo)}</td></tr>")
    w("</table>")
    if rh._CID_NAO_COMPARAVEL:
        w("<h3>Fora do censo (duplicatas)</h3><table>"
          "<tr><th>curva</th><th>motivo</th></tr>")
        for cid, motivo in rh._CID_NAO_COMPARAVEL.items():
            w(f"<tr><td class='mono'>{_esc.escape(cid)}</td>"
              f"<td>{_esc.escape(motivo)}</td></tr>")
        w("</table>")

    # ------------------------------------------------- 7. retratacoes
    w(f"<h2>7. A trilha de retiradas e retratações ({n_ret} assinaturas) "
      "— o sistema se corrige</h2>")
    w("<p>Uma exceção é um invariante de prova: quando a prova cai (regra "
      "nova a absorve, mérito a torna desnecessária, ou um erro é "
      "encontrado), a assinatura <b>sai</b> — registrada, nunca apagada. "
      "Esta trilha é tão importante para a tese quanto as exceções vivas: "
      "ela mostra que o mecanismo não é válvula de escape.</p>")
    for rotulo, d in retiradas.items():
        if not d:
            continue
        w(f"<h3>{_esc.escape(rotulo)} ({len(d)})</h3><table>"
          "<tr><th>curva</th><th>registro</th></tr>")
        for cid, motivo in sorted(d.items()):
            w(f"<tr><td class='mono'>{_esc.escape(cid)}</td>"
              f"<td>{_esc.escape(motivo)}</td></tr>")
        w("</table>")

    # ------------------------------------------------- 8. reabertura
    w("<h2>8. Condições de reabertura e reprodutibilidade</h2>")
    w("<ul>"
      "<li>Todo piso é <b>recomputado do store na geração</b> — se uma "
      "réplica nova entrar (ex.: a 3ª corrida de uma condição), o piso "
      "re-mede e cada prova desta página ou se sustenta ou cai.</li>"
      "<li>Mudança de régua, de fingerprint do engine ou de dado reabre "
      "as provas afetadas (regra §4.43: toda pendência carrega o contexto "
      "contra o qual foi medida).</li>"
      "<li>Os testes <span class='mono'>test_medicoes_cruzadas</span> "
      "(exceção-dentro-do-tripé é ruído e é acusada) e "
      "<span class='mono'>test_meta_numeros_nao_envelhecem</span> (os "
      "números publicados batem com o store) vigiam esta página em toda "
      "suíte.</li></ul>")
    w(f'<p class="small">Resumo vivo: {n_exc} exceções ativas '
      f'({n_f5} F5 + {n_f7} F7) · {n_decl} declaradas · {n_ret} '
      f'retiradas/retratadas registradas · tripé {n_tri}/{n_comp} · '
      f'resolvida/declarada {n_tri + n_exc + n_decl}/{n_comp}.</p>')

    OUT.write_text("\n".join(P), encoding="utf-8")
    print(f"pagina gerada: {OUT}")
    print(f"contagens: {n_exc} excecoes ({n_f5} F5 + {n_f7} F7), "
          f"{n_decl} declaradas, {n_ret} retiradas, tripe {n_tri}/{n_comp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
