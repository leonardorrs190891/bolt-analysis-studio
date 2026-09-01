"""MEDIÇÕES CRUZADAS — cada número derivado preso a um SEGUNDO caminho.

Item 4 das melhorias de 2026-07-29. Por que existe: naquele dia eu errei quatro
números, e os quatro pelo mesmo motivo — **número derivado por um único caminho,
sem confronto independente**:

 1. piso de repetibilidade enviesado 5× (exigia abscissas idênticas, e sobrava 1
    par de 15 no Bauer fig6). Só foi pego porque o `FLOORS` legado do repo
    existia e discordava — sorte, não método;
 2. barra de histograma cortada pelo limite pintada de verde: o olho somava 124
    aprovadas onde eram 109;
 3. extração de figura pela legenda trouxe tensão de atrito e foto de bancada;
 4. "104 + 38 = 142" exceções, ignorando que 9 estavam nas duas listas.

Cada teste aqui reproduz um número por um caminho diferente do que o produz.
Nenhum deles simula: leem o store e as estruturas. São rápidos de propósito —
guarda que demora não é rodada.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.runner import CaseResult

STORE = (Path(__file__).resolve().parents[1]
         / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json")


@pytest.fixture(scope="module")
def store():
    if not STORE.exists():
        pytest.skip("store canônico ausente (clone sem os dados)")
    return json.loads(STORE.read_text(encoding="utf-8"))


# --------------------------------------------------------------- 1. exceções
def test_uniao_de_excecoes_nao_conta_duas_vezes():
    """O erro nº 4: somar as listas. A união é dict, então a chave impede a
    dupla contagem — mas só se as duas listas forem DISJUNTAS por construção.
    Se alguém acrescentar à F7 uma curva que já está na F5, o total do painel
    não muda (o dict absorve) e a tabela do documento passa a mentir. Este teste
    é o que avisa."""
    dup = set(rh._F5_EXCECOES) & set(rh._F7_EXCECOES)
    assert not dup, (
        f"{len(dup)} curva(s) nas DUAS listas de exceção: {sorted(dup)}. "
        "As sobrepostas devem ficar só na F5 — senão o documento soma 2 e o "
        "painel conta 1.")
    assert len(rh._EXCECOES) == len(rh._F5_EXCECOES) + len(rh._F7_EXCECOES)


def _limites_efetivos(store):
    """{case_id: limite efetivo da 3ª perna} pelos MESMOS helpers do report
    (D1: max(global, piso da fonte) via `limite_sres`)."""
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import CaseResult
    pares, recs = [], {}
    for rec in all_records():
        recs[rec.case_id] = rec
        d = store.get(rec.case_id)
        if d:
            pares.append((rec.source, CaseResult.from_dict(d)))
    pisos = rh._pisos_medidos(pares)
    return {cid: rh.limite_sres(recs[cid].source, pisos) for cid in recs}


def test_excecao_assinada_esta_de_fato_fora_do_tripe(store):
    """Exceção para curva que PASSA no tripé é ruído: ela não precisa de perdão.
    Se aparecer, ou a régua mudou (e a lista precisa ser relida) ou a entrada
    está errada.

    Desde a retirada de 2026-07-30 o juízo é pelo limite EFETIVO (D1,
    `limite_sres`) — foi exatamente este teste, na régua global, que NÃO tinha
    como acusar as 19 assinaturas que o D1 cobriu (elas falhavam no global e
    passavam no efetivo). Com o efetivo, uma futura assinatura já coberta pela
    regra falha aqui no dia em que entrar."""
    lim = _limites_efetivos(store)

    def _passa(cid):
        r = store.get(cid)
        if not r or not r.get("ok") or r.get("mae") is None:
            return None
        # σ_res pelo HELPER CANÔNICO, não pelo `resid_std` cru: a regra n<6
        # assinada em 2026-08-01 diz que σ com menos de 6 pontos na janela é
        # NÃO-JULGÁVEL, e `sres_para_censo` devolve None nesse caso. Usar o cru
        # faz uma curva declarada-por-n<6 parecer aprovada (medido 2026-08-09:
        # a `Yang2023 0,15 mm`, n=4, cujo mae/mx passam com folga — é POR ISSO
        # que ela é declarada). Reimplementar a regra em vez de chamar o helper
        # é o erro que a campanha mais repete.
        sd = rh.sres_para_censo(CaseResult.from_dict(r))
        return (r["maxerr"] <= rh.META_MAX and r["mae"] <= rh.META_MAE
                and sd is not None and sd <= lim.get(cid, rh.META_SRES))

    dentro = [cid for cid in rh._EXCECOES if _passa(cid)]
    assert not dentro, (
        f"exceção assinada para curva que passa no tripé: {dentro} — a régua "
        "mudou desde a assinatura? releia a lista antes de publicar o número.")

    # O MESMO para as DECLARADAS — lacuna achada em 2026-08-09 (D-AA) e fechada
    # no mesmo dia. Não era hipotética: `declarado_total` do censo é
    # `n_ok + n_exc + n_decl` SEM dedup, então uma curva que passa o tripé E
    # carrega estatuto é contada DUAS vezes e o número publicado infla em
    # silêncio. A metade das exceções já tinha guarda (acima, e foi ela que
    # pegou a `jcsr2023_stainless_seawater` no dia em que ela fechou por
    # mérito); a metade das declaradas não tinha nenhuma, e o precedente existe
    # — a `lu2024_M8_fig18_amp2p0` SAIU das declaradas por mérito em
    # 2026-08-01, e essa saída dependeu de alguém notar, não de um teste.
    decl_dentro = [cid for cid in rh._DECLARADAS if _passa(cid)]
    assert not decl_dentro, (
        f"curva DECLARADA que passa no tripé: {decl_dentro} — declaração é "
        "'não dá para julgar', não perdão; se a curva fecha por mérito ela sai "
        "da lista (precedente: lu2024_M8_fig18_amp2p0, 2026-08-01). Enquanto "
        "ficar, o `declarado_total` a conta duas vezes.")

    # E as duas listas não podem se sobrepor, pela mesma aritmética.
    ambos = sorted(set(rh._EXCECOES) & set(rh._DECLARADAS))
    assert not ambos, (
        f"curva em _EXCECOES E _DECLARADAS: {ambos} — `declarado_total` soma "
        "as duas contagens, então a sobreposição infla o número publicado.")
    # e o ESPELHO: toda RETIRADA tem de passar pela regra (senão a retirada
    # tirou perdão de quem ainda precisa — reverter a curva para a F7)
    # erratum ROUSSEAU 2026-08-01: retiradas D1 cuja base era o piso
    # RETRATADO voltam a falhar por motivo novo — nao se devolve assinatura
    # contra piso invalido; a lista explicita no report carrega o porque.
    presas = [cid for cid in rh._EXCECOES_RETIRADAS_D1
              if cid not in rh._RETIRADAS_D1_INVALIDADAS_POR_ERRATUM
              and _passa(cid) is False]
    assert not presas, (
        f"retirada de 2026-07-30 tirou a assinatura de curva que AINDA falha "
        f"pela regra efetiva: {presas} — devolvê-la à _F7_EXCECOES.")
    assert not (set(rh._EXCECOES_RETIRADAS_D1) & set(rh._EXCECOES)), \
        "curva ao mesmo tempo retirada e ativa"


# ------------------------------------------------------------------ 2. tripé
def test_contagem_do_tripe_por_dois_caminhos(store):
    """`_tripe_ok` (que a página usa) contra uma recontagem crua do store."""
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = [r for r in all_records()
            if rh.caso_comparavel(r.source, r.case_id)]
    via_api = sum(1 for r in recs
                  if rh._tripe_ok(CaseResult.from_dict(store[r.case_id]))
                  is True for _ in [0] if r.case_id in store)
    cru = 0
    for r in recs:
        d = store.get(r.case_id)
        if not d or not d.get("ok") or d.get("mae") is None:
            continue
        sd = d.get("resid_std")
        # regra n<6 (assinada 2026-08-01, N_MIN_SRES): sigma sem suporte
        # nao afirma o tripe — a recontagem crua espelha o juiz.
        md = d.get("metric_data") or []
        if md and len(md) < rh.N_MIN_SRES:
            sd = None
        if (d["maxerr"] <= rh.META_MAX and d["mae"] <= rh.META_MAE
                and sd is not None and sd <= rh.META_SRES):
            cru += 1
    assert via_api == cru, (
        f"_tripe_ok conta {via_api} e a recontagem crua {cru} — alguma das duas "
        "não está aplicando as três pernas")


# ------------------------------------------------- 3. identidade do resíduo
def test_identidade_rmse_vies_sigma(store):
    """`RMSE² = viés² + σ_res²` é exata. É ela que sustenta a leitura de que
    σ_res mede FORMA e o viés mede NÍVEL; se o store violar, algum dos três
    campos foi calculado sobre outro vetor."""
    pior, n = 0.0, 0
    for cid, r in store.items():
        mp, md = r.get("metric_pred"), r.get("metric_data")
        rmse, sd = r.get("rmse"), r.get("resid_std")
        if not (mp and md and len(mp) == len(md)) or rmse is None or sd is None:
            continue
        e = [float(p) - float(d) for p, d in zip(mp, md)]
        bias = sum(e) / len(e)
        esq = float(rmse) ** 2
        dir_ = bias ** 2 + float(sd) ** 2
        pior = max(pior, abs(esq - dir_))
        n += 1
    assert n > 50, f"só {n} registros com vetores — store degradado?"
    assert pior < 1e-9, f"identidade violada em até {pior:.3e} (n={n})"


def test_ordem_das_tres_normas(store):
    """MAE ≤ RMSE ≤ res.máx: são normas-p (p=1,2,∞) do MESMO vetor. Violação =
    os três não vêm do mesmo resíduo, e aí o painel compara maçã com laranja."""
    maus = []
    for cid, r in store.items():
        mae, rmse, mx = r.get("mae"), r.get("rmse"), r.get("maxerr")
        if None in (mae, rmse, mx):
            continue
        if not (mae - 1e-12 <= rmse <= mx + 1e-12):
            maus.append((cid, mae, rmse, mx))
    assert not maus, f"{len(maus)} violações da ordem: {maus[:3]}"


# ------------------------------------------------------- 4. nomes de alavanca
def test_alavancas_da_varredura_existem_no_engine():
    """O erro que quase publiquei: `mu` não é campo de `JointMaterial` (são
    `mu_bearing`/`mu_thread`), então perturbá-lo dava Δ=0 e eu leria "µ é
    inerte". Nome que não chega ao engine é INDISTINGUÍVEL de alavanca inerte
    pelo número — só pela verificação do nome."""
    sens = pytest.importorskip("New_Theory.sensitivity_sres",
                               reason="varredura de σ_res não instalada")
    campos = set(JointMaterial.__dataclass_fields__)
    fora = [p for p in sens.PARAMS if p not in campos]
    assert not fora, (
        f"alavancas que NÃO são campo de JointMaterial: {fora} — perturbá-las "
        "dá Δ=0 e o resultado seria lido como 'inerte'")


def test_alavanca_de_desgaste_e_a_via_ATIVA():
    """`K_archard` está morto quando o canônico adota `k_wear_spec > 0` (o
    engine ignora a via legada K/H). Varrer o parâmetro morto e concluir
    'desgaste é inerte' seria erro de rota, não medição."""
    import sys
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "New_Theory"))
    try:
        from library_common import frozen_constants
    except ImportError:
        pytest.skip("library_common indisponível")
    consts, _ = frozen_constants()
    kws = consts.get("k_wear_spec") or 0
    sens = pytest.importorskip("New_Theory.sensitivity_sres",
                               reason="varredura de σ_res não instalada")
    if kws > 0:
        assert "k_wear_spec" in sens.PARAMS, (
            "o canônico adota k_wear_spec>0, então é ELE que a varredura tem de "
            "perturbar")
        assert "K_archard" not in sens.PARAMS, (
            "K_archard está morto com k_wear_spec>0 — varrê-lo publica um "
            "'inerte' que é artefato de rota")


# ------------------------------------------- 4b. projeção 3D em duas línguas
def test_projecao_3d_publica_as_constantes_que_usa():
    """O 3D é desenhado DUAS vezes: em Python (estado inicial, imprimível) e em
    JS (ao girar / trocar o eixo de profundidade). Duplicar a fórmula é
    inevitável — girar exige reprojetar — mas o INVARIANTE é que o JS leia os
    mesmos constantes que o Python publicou em `data-*`, nunca as próprias.

    Este teste prende as duas pontas: (a) o SVG do Python publica todos os
    parâmetros da projeção; (b) o JS lê cada um deles do dataset; (c) a posição
    que o Python desenha é a que a fórmula documentada dá com esses parâmetros —
    se alguém mexer na projeção só de um lado, um dos três quebra."""
    import re
    svg = rh._svg_scatter3([(0.02, 0.05, 0.010, "alfa"),
                            (0.10, 0.30, 0.030, "beta")])
    attrs = dict(re.findall(r'data-([a-z0-9]+)="([^"]+)"', svg))
    for k in ("ml", "mt", "wp", "hp", "y0", "dx", "dy", "cx", "cy", "cz"):
        assert k in attrs, f"o SVG não publica data-{k} — o JS não tem como ler"
    js = rh._JS_PAINEL
    for k in ("ml", "wp", "hp", "y0", "dx", "dy", "cx", "cy"):
        assert f"dataset.{k}" in js, (
            f"o JS não lê data-{k}: se ele usa constante própria, a projeção "
            "diverge do estado inicial ao primeiro giro")
    ML, Wp, Hp = float(attrs["ml"]), float(attrs["wp"]), float(attrs["hp"])
    y0, DX, DY = float(attrs["y0"]), float(attrs["dx"]), float(attrs["dy"])
    cx, cy, cz = float(attrs["cx"]), float(attrs["cy"]), float(attrs["cz"])
    a, b, c = 0.02, 0.05, 0.010
    esp_x = ML + (a / cx) * Wp + (c / cz) * DX * Wp
    esp_y = y0 - (b / cy) * Hp - (c / cz) * DY * Hp
    # `data-cid` vive no <a> e a marca é desenhada por `_marca3` (círculo, ou
    # triângulo quando o ponto é recortado na borda) — pego o 1º par cx/cy que
    # aparece DEPOIS do link, para o teste não depender da forma escolhida.
    i = svg.find('data-cid="alfa"')
    assert i > 0, "ponto 'alfa' não encontrado no SVG"
    m = re.search(r'cx="([\d.]+)"\s+cy="([\d.]+)"', svg[i:i + 400])
    assert m, "a marca do ponto 'alfa' não expõe cx/cy"
    assert abs(float(m.group(1)) - esp_x) < 0.2, (
        f"x projetado {m.group(1)} contra {esp_x:.2f} pela fórmula publicada")
    assert abs(float(m.group(2)) - esp_y) < 0.2, (
        f"y projetado {m.group(2)} contra {esp_y:.2f} pela fórmula publicada")


def test_ponto_do_3d_e_link_de_verdade():
    """`window.open` era bloqueado como popup em `file://` — o modo em que a
    página é usada. O ponto tem de ser `<a href>` nos DOIS geradores, senão o
    clique volta a falhar só em produção."""
    svg = rh._svg_scatter3([(0.02, 0.05, 0.01, "meucaso")])
    assert '<a href="reports/meucaso.html"' in svg, (
        "o SVG do Python não embrulha o ponto num link — sem JS ele fica morto")
    js = rh._JS_PAINEL
    # `window.open(` com o parêntese: a 1ª versão procurava a string nua e
    # falhava quando um COMENTÁRIO do próprio arquivo explicava por que ela não
    # deve ser usada. Asserção sobre código tem de casar chamada, não menção.
    assert "window.open(" not in js, (
        "window.open é bloqueado como popup em file://; use <a href>")
    assert "<a href=" in js and "reports/" in js, (
        "o JS não emite link nos pontos — ao girar, o clique morre")


# --------------------------------------- 4c. classificação de DOF vs o código
def _engine_src() -> str:
    p = (Path(__file__).resolve().parents[1] / "src" / "bolt_analysis_studio"
         / "numerical" / "dynamic_stiffness_analyzer.py")
    return p.read_text(encoding="utf-8")


def test_k_j_init_e_alpha_GW_sao_lidos_SEMPRE():
    """VERDADE-DE-CÓDIGO contra a razão do congelamento. Os dois estão em
    `FROZEN_S_ZERO`, e até 2026-07-29 a razão dizia que **não eram lidos nos
    caminhos canônicos**. São: `k_j_ax()` os lê sem gate algum, e ela alimenta o
    laço principal, o orçamento de energia (`U_int`) e o ρ = k_j_ax/k_b.

    Congelar por MAGNITUDE é legítimo (Δ ≤ 4,5e-4 medido). Congelar por
    AUSÊNCIA seria falso, e a diferença importa: quem lê "não é lido" ignora um
    parâmetro que está no caminho da rigidez."""
    src = _engine_src()
    assert "mat.k_j_init * ratio**mat.alpha_GW" in src, (
        "a leitura conjunta em k_j_ax mudou de forma — reveja a razão do "
        "congelamento antes de confiar nela")
    linhas = src.splitlines()
    i = next(i for i, l in enumerate(linhas)
             if "mat.k_j_init * ratio**mat.alpha_GW" in l)
    corpo = "\n".join(linhas[max(0, i - 20):i])
    assert "mode ==" not in corpo, (
        "apareceu um gate de modo acima da leitura: se k_j_ax passou a ser "
        "condicional, a classificação de DOF tem de mudar junto")
    from bolt_analysis_studio.calibration.parameter_registry import FROZEN_S_ZERO
    for p in ("k_j_init", "alpha_GW"):
        r = FROZEN_S_ZERO[p].lower()
        assert "magnitude" in r or "medido" in r, (
            f"a razão de {p} voltou a ser por ausência/bypass; ele É lido "
            "sempre via k_j_ax")


def test_slip_regime_sharpness_e_gate_de_MODO_nao_congelado():
    """A varredura de σ_res mediu Δ=0 em 10 casos canônicos e o parâmetro
    parecia candidato a `FROZEN_S_ZERO` ("S=0 sempre"). **Não é** — é gate de
    MODO, demonstrado por sonda de 2 pontos nos dois sentidos (Δ=0 exato com
    `slip_regime_mode="off"`, Δ≈2,5e-5 com `cattaneo_mindlin`). E o modo é
    CANDIDATO DE FORMA da campanha: congelá-lo mataria um candidato em silêncio.
    """
    from bolt_analysis_studio.calibration import parameter_registry as pr
    assert "slip_regime_sharpness" not in pr.FROZEN_S_ZERO, (
        "slip_regime_sharpness NÃO é S=0 sempre — é gate de modo; congelá-lo "
        "mata o candidato de forma cattaneo_mindlin sem aviso")
    assert "slip_regime_sharpness" in pr._GATE_POR_MODO
    campo_modo, ativa, _default, _o = pr._GATE_POR_MODO["slip_regime_sharpness"]
    assert (campo_modo, ativa) == ("slip_regime_mode", "cattaneo_mindlin")
    src = _engine_src()
    usos = [l for l in src.splitlines() if "mat.slip_regime_sharpness" in l]
    assert len(usos) == 1, (
        f"{len(usos)} leituras de slip_regime_sharpness: o gate de modo cobre "
        "uma só — reveja o mapa se apareceu outra")


# ----------------------------------------------------------------- 5. o piso
def test_piso_v2_concorda_com_o_FLOORS_legado(store):
    """O erro nº 1. O `FLOORS` legado (MAE pareado por nome, campanha antiga) é
    a única medição INDEPENDENTE de repetibilidade que o repo tem. Onde os dois
    existem, têm de ficar na mesma ordem de grandeza — foi a discrepância de 5×
    que denunciou o viés de amostragem da 1ª versão. Banda generosa (fator 3):
    os métodos diferem de propósito; o que não pode é discordar por ordem."""
    from bolt_analysis_studio.validation.case_registry import all_records
    pares = []
    for r in all_records():
        d = store.get(r.case_id)
        if d:
            pares.append((r.source, CaseResult.from_dict(d)))
    pisos = rh._pisos_medidos(pares)
    checados = 0
    for (src, tok), legado in rh.FLOORS.items():
        v2 = pisos["por_fonte"].get(src)
        if not v2:
            continue
        checados += 1
        raz = v2[0] / legado
        assert 1 / 3 <= raz <= 3, (
            f"{src}: piso v2 {v2[0]:.4f} contra legado {legado:.3f} "
            f"({raz:.2f}×) — discordância de ordem entre dois métodos de medir "
            "a MESMA coisa é sinal de erro, não de definição diferente")
    assert checados >= 2, "nenhuma fonte com os dois pisos — teste vazio"


def test_piso_e_ordenado_como_as_reguas(store):
    """No piso valem os limites UNIVERSAIS das três estatísticas do mesmo vetor:
    `MAE ≤ res.máx` e `σ ≤ res.máx` (porque σ ≤ RMS ≤ máx). Quebrar isso
    significa que os três números não vieram do mesmo vetor de diferenças.

    ⚠️ **O limite gaussiano NÃO vale aqui, e isso foi medido.** A 1ª versão deste
    teste exigia `σ ≤ MAE·√(π/2) ≈ 1,253·MAE`, que é a relação para resíduo
    normal de média zero — e falhou legitimamente em `BAUER_2024 δ=0,08`
    (σ 0,1073 contra 0,0995). A diferença entre aquelas réplicas é **spiky**, não
    gaussiana: as três curvas da fig8 andam juntas e divergem no fim (uma colapsa,
    outra não), o que dá média absoluta pequena e σ grande.

    Consequência para a F7 (§10, caveat 4): o fator `1/√2` da barra FORTE assume
    normalidade. Com cauda pesada o fator verdadeiro é **maior** — ou seja, a
    barra que usamos é mais **exigente** que a ideal, e a lista de exceções erra
    para o lado conservador. O caveat estava escrito por precaução; agora há pelo
    menos uma família medida onde a premissa de fato não vale."""
    from bolt_analysis_studio.validation.case_registry import all_records
    pares = [(r.source, CaseResult.from_dict(store[r.case_id]))
             for r in all_records() if r.case_id in store]
    pisos = rh._pisos_medidos(pares)
    assert pisos["fam"], "nenhuma família de réplica medida"
    for f in pisos["fam"]:
        rot, mae, mx, sd = f[0], f[2], f[3], f[4]
        assert mae <= mx + 1e-9, f"{rot}: piso de MAE {mae} > res.máx {mx}"
        assert sd <= mx + 1e-9, f"{rot}: piso de σ {sd} > res.máx {mx}"
        assert mae > 0 and mx > 0, f"{rot}: piso nulo — família degenerada"


def test_gaussianidade_do_piso_e_declarada_nao_suposta(store):
    """Quantas famílias violam o limite gaussiano `σ ≤ MAE·√(π/2)`. NÃO é falha:
    é a medição do quanto a premissa da barra `piso/√2` (F7 §2) se afasta do
    ideal. O teste falha só se a violação virar a REGRA (>40% das famílias), o
    que tornaria a barra FORTE indefensável como está."""
    from bolt_analysis_studio.validation.case_registry import all_records
    pares = [(r.source, CaseResult.from_dict(store[r.case_id]))
             for r in all_records() if r.case_id in store]
    fam = rh._pisos_medidos(pares)["fam"]
    viol = [f[0] for f in fam if f[4] > f[2] * math.sqrt(math.pi / 2) + 1e-9]
    frac = len(viol) / max(len(fam), 1)
    assert frac <= 0.40, (
        f"{len(viol)} de {len(fam)} famílias ({frac:.0%}) têm resíduo de réplica "
        f"longe de gaussiano: {viol[:5]}. A barra piso/√2 da F7 assume "
        "normalidade; se isto virar regra, a barra precisa ser re-derivada.")


# --------------------------------------------------------------------------- F
# Duas invariantes da atividade F (2026-07-29). Ambas existem porque o número
# errado que elas prendem PASSOU por revisão: o primeiro por parecer
# aritmeticamente coerente, o segundo por ser inferência plausível sobre dado real.

def test_sigma_sem_forma_lisa_e_corrigido_por_graus_de_liberdade():
    """Remover uma quadrática consome 3 DOF. Sobre n=7 isso é 3 dos 7 pontos, e o
    `np.std` do resíduo restante sai ~22% viesado para BAIXO — uma curva
    "passaria" a 3ª perna por artefato de ajuste. O script da F tem de corrigir
    por `sqrt(SS/(n-p))`; este teste reproduz a correção num caso construído em
    que o viés é conhecido analiticamente."""
    import numpy as np

    rng = np.random.default_rng(20260729)
    n, p = 7, 3
    # residuo puramente aleatorio: NAO ha forma para remover, logo o sigma
    # honesto e' ~1 e qualquer polinomio ajustado esta' ajustando ruido.
    viés_std, viés_dof = [], []
    for _ in range(400):
        e = rng.normal(0.0, 1.0, n)
        s = np.linspace(0.0, 1.0, n)
        r = e - np.polyval(np.polyfit(s, e, 2), s)
        ss = float(np.sum(r ** 2))
        viés_std.append(float(np.std(r)))
        viés_dof.append(float(np.sqrt(ss / (n - p))))
    m_std, m_dof = float(np.mean(viés_std)), float(np.mean(viés_dof))
    assert m_std < 0.85, (
        f"o np.std do resíduo pós-quadrática deveria ser bem menor que 1 "
        f"(viés de DOF), veio {m_std:.3f} — a premissa do teste mudou")
    assert m_dof > m_std * 1.15, (
        f"a correção de DOF ({m_dof:.3f}) tem de recuperar o σ contra o std "
        f"viesado ({m_std:.3f}); se não recupera, o estimador da F está errado")


def test_fracao_do_canal_nao_e_cota_de_capacidade():
    """A fração da perda num canal, medida no config NOMINAL, não limita o que
    aquele canal pode carregar sob outra LEI DE TAXA — e portanto não decide a
    inércia de uma alavanca que troca a lei.

    Medido em 2026-07-29: `chu…test8` tem 2,3% da perda no canal rotacional e vai
    a ~25% (13×) com `loose_rate_mode="graded_scrit"`. Este teste não simula (não
    seria uma guarda rápida); ele prende a DISTINÇÃO estrutural que a lição gerou:
    a `knowledge_base` tem de continuar separando alavanca-que-multiplica de
    alavanca-que-troca-a-lei, senão a lição se perde no código."""
    from bolt_analysis_studio.calibration import knowledge_base as kb

    gated = kb.channel_gated_levers()
    assert "loose_arrest_floor" in gated and "eta_loose" in gated, (
        "as alavancas MULTIPLICATIVAS de canal saíram de channel_gated_levers(): "
        f"{sorted(gated)}. A distinção da §6 da F depende dessa lista existir.")
    # `loose_rate_mode` troca a lei, nao multiplica um canal: nao pode ser
    # classificada junto, senao o proximo estudo a descarta por fatia pequena.
    assert "loose_rate_mode" not in gated, (
        "`loose_rate_mode` é alavanca de LEI DE TAXA e foi classificada como "
        "gated-por-canal. Medido que ela infla um canal de 2,3% para 25% — "
        "classificá-la assim autoriza descartá-la por fração pequena no nominal, "
        "que é exatamente o erro corrigido em 2026-07-29.")
