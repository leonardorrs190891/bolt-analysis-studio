"""VARREDURA DAS 3 CLASSES — os 55 fora do tripe, curva a curva.

Item 3 da fila de decisoes (`New_Theory/DECISOES_PENDENTES.md`), autorizado em
2026-07-28. Hoje as 55 curvas fora do tripe estao fundidas numa fila unica, e
cada classe pede uma acao OPOSTA:

  form-limited    -> construir mecanismo   (prereg + gate, caro)
  data-limited    -> pedir/redigitalizar dado
  metric-limited  -> mudar o eixo da metrica (o dado existe, a forma acerta)
  level-limited   -> ler uma constante de nivel (mais barato de todos)

A 4a classe NAO estava no enunciado do item, mas o diagnostico do kernel
(2026-07-27, grupo B: Eccles fig8a/8c) provou que ela existe e e distinta:
perfil detrendado PLANO com resduo de nivel uniforme nao pede fisica nova.
Forcar essas curvas em "form-limited" mandaria construir mecanismo para
resolver o que a leitura de um piso resolve.

SO-LEITURA. Nao escreve no store, nao simula, nao fita, nao adota. Le
  - `Models/CALIBRATION_AND_VALIDATION/validation_store.json` (fingerprint unico
    4f5bedfbace4; metric_x/metric_pred/metric_data em 203/203 registros)
  - os CSVs crus da biblioteca (para contar o que a metrica DESCARTOU)

Run:  py -3.12 New_Theory/frontier_classes.py
Saida: New_Theory/frontier_classes.json  +  New_Theory/frontier_classes.md


DISCRIMINADORES E LIMIARES — DECLARADOS ANTES DE MEDIR
======================================================

Este e um DIAGNOSTICO, nao um gate: nenhum numero aqui autoriza adocao. Mas os
limiares e a ORDEM de decisao estao fixados aqui em cima, e todos os numeros
crus vao para o JSON, para que qualquer rotulo possa ser re-julgado sem re-rodar.

(1) SCATTER DE REPLICA  -> DATA-LIMITED
    Replicas da MESMA condicao nominal, achadas por DUAS vias:
      (i) nome: case_id difere apenas por `_repN`;
      (ii) condicao declarada identica (`cond_key`) E os nomes diferindo SO por
           indice de repeticao (`token_diff` vazio).
    Interpolando-as numa grade comum, se o espalhamento ENTRE replicas passa de
    0,10 (a propria tolerancia da meta), o resduo do modelo nao e atribuivel ao
    modelo: a meta esta abaixo da reprodutibilidade do experimento.
    Limiar: spread_max > 0.10

    ERRATA (2a): a via (ii) NAO existia na 1a versao — o agrupamento era so por
    nome, e por isso `bauer…fig8_test1/2/3` (tres repeticoes do MESMO ensaio,
    condicoes declaradas identicas, so a vida diferindo: 873/1351/1161) sairam
    em TRES classes diferentes (FORM/METRIC/LEVEL). O defeito foi apontado pela
    sessao paralela em `replicate_impossibility_sweep_2026-07-28.md` §3.1, que o
    achou pela nota de aparato: *um classificador por-curva e cego para limite
    por-familia*. A via (ii) reproduz aquele veredicto por outro caminho
    (condicoes + tokens), sem depender da nota.

(2) ARTEFATO DE FLOOR_TRIM -> METRIC-LIMITED
    O runner descarta pontos com ratio < 0,10 (FLOOR_TRIM). Onde o dado cru vai
    a ZERO (destacamento), esse corte apaga justamente o resultado central do
    paper e a curva e pontuada sobre uma minoria dos pontos.
    Limiar: >= 25% dos pontos crus descartados pelo piso E min(ratio cru) < 0,02

(3) RESGATE HORIZONTAL -> METRIC-LIMITED  ("erro de relogio, nao de forma")
    Para CADA ponto pontuado i, procura-se a trajetoria DENSA do modelo dentro de
    UM intervalo de amostragem do dado em torno de x_i:
        resgatado_i  <=>  min |modelo(x') - dado_i| <= 0,10,  |x' - x_i| <= s_i
    com s_i = meia-distancia aos vizinhos de i na grade do dado. A curva e
    metric-limited se TODOS os pontos sao resgatados: sob uma tolerancia
    horizontal do tamanho da propria resolucao do dado, o modelo esta dentro da
    banda em todo lugar — o dado nao consegue distinguir esse modelo de um certo,
    mas a metrica vertical o penaliza ate o maxerr.
    Limiar: frac_resgatada == 1,0 (nenhum limiar de inclinacao)

    Trajetoria densa reconstruida do proprio store: `interp(cycles, ratio)/align`
    reproduz `metric_pred` com erro <= 2e-5 (verificado nos 4 casos-sonda).

    POR QUE A JANELA E LIMITADA A UM INTERVALO DE AMOSTRAGEM: e o que impede o
    criterio de ser gamed. As tres tentativas de metrica (vida §4.45, nivel
    §4.46, banda §4.47) morreram porque um modelo que despenca VARRE o valor do
    dado e sai perdoado (em amp0p6 o cliff ficava MELHOR que a rampa). Com janela
    de um intervalo, um modelo que colapsa cedo continua longe do dado nos
    trechos rasos e NAO e resgatado.

(3b) RESOLUCAO GROSSA -> DATA-LIMITED
    O resgate de (3) so significa "a metrica e o limite" se o dado for fino. Numa
    curva pontuada sobre 5-6 pontos, a janela de um intervalo varre um quinto da
    curva e o resgate passa VAZIO. Mas a leitura correta ai nao e "mude o eixo" —
    e "o dado nao resolve o relogio", e a acao e REDIGITALIZAR.
        janela_rel = mediana(s_i) / span
    Limiar: resgate total COM janela_rel >= 0,10 -> DATA-LIMITED (resolucao)
            resgate total COM janela_rel <  0,10 -> METRIC-LIMITED
    (0,10 do span ~ 10 pontos razoavelmente espalhados. Medido: o
     YANG_2023_IJPEM 0,50 mm tem 6 pontos crus e maxerr 0,274 — saia por
     metric-limited na 1a passada deste criterio, o que era generoso demais.)

    ERRATA DA 1a VERSAO (registrada de proposito): a 1a passada usou
    `dx_needed = 0,10/|slope do dado| < espacamento local`. Com diferenca
    central isso colapsa algebricamente em `|Delta dado| > 0,20` — um teste de
    "o dado e ingreme aqui" com ZERO conteudo sobre o erro do modelo. Absolvia os
    7 do YANG_2023_IJPEM (tri-falsificados, maxerr ate 0,56) por terem um degrau
    grande perto do argmax. Foi o controle contra veredictos estabelecidos que
    pegou. Os campos `dx_needed`/`relogio_pct_do_span` continuam no JSON como
    informacao, mas NAO classificam mais.

(4) TRUNCAMENTO -> DATA-LIMITED
    Resduo maximo no ULTIMO ponto pontuado, modelo ABAIXO do dado, e o dado
    AINDA CAINDO no fim (inclinacao final >= 30% da inclinacao maxima da propria
    curva): a medicao parou no meio do processo.
    Limiar: argmax no ultimo ponto E resduo < 0 E dado_final > 0,15
            E |slope final| >= 0,30 * max|slope| do dado
    Os dois ultimos termos importam: modelo ACIMA do dado no fim = super-retencao
    = defeito do modelo; e dado que ACHATOU no fim = platou de verdade e o modelo
    e que segue caindo (ROUSSEAU steel_t10, LU) = FORMA, nao truncamento.

(5) NIVEL -> LEVEL-LIMITED
    A curva tem a forma certa e esta fora de nivel. O criterio e a PROPRIA
    pergunta da decisao — "consertar o nivel fecharia esta curva?":
        maxerr_pos_nivel = max |resduo - media(resduo)|   <   0,10
    ou seja, removido um deslocamento uniforme, o resduo maximo entra no tripe.
    O nivel ja e legitimamente per-rig (`loose_arrest_floor`, lido do dado), logo
    fechar assim NAO pede fisica nova — e a acao mais barata da fila.
    Limiar: maxerr_pos_nivel < 0,10 E |media do resduo| > 0,02 (offset real)

    Por que NAO pela planura dos quintis (era o criterio da 1a passada): quintil
    e media dentro do quintil, entao um PICO localizado desaparece na media e uma
    curva com forma grossa plana + um pico passa por "nivel" sem que consertar o
    nivel feche nada. Medido: eccles fig8a tem resduo medio -0,0426 num maxerr de
    0,122 — o nivel explica 35% do erro, e removE-lo NAO fecha a curva.
    `perfil_plano`/`planura` continuam no JSON como informacao (sao o que o
    kernel_diagnostic mediu), mas nao classificam.

(6) senao -> FORM-LIMITED

ORDEM: (1) scatter -> (2) nivel -> (3) floor_trim -> (4) resgate -> (5)
truncamento -> (6) forma.

  - (1) vem primeiro porque scatter de replica INVALIDA a comparacao: nao ha
    resduo atribuivel ao modelo.
  - (2) vem antes das metricas porque e uma afirmacao sobre o MODELO ("a forma
    esta certa") e e a acao mais barata de todas — ler uma constante de nivel
    com procedencia. Ela nao depende de resolver politica de metrica nenhuma.
    [Esta posicao mudou depois da 1a passada: com `nivel` no fim, `floor_trim`
     abocanhava curvas de forma-certa-nivel-errado e mandava discutir convencao
     onde bastava ler um piso. Mudanca de ORDEM declarada aqui, com o motivo.]
  - (3)-(4) sao afirmacoes sobre a METRICA/dado; (5) sobre o dado; (6) e o
    residual honesto.

Curva que satisfaz mais de um criterio tem TODOS em `flags_todos` no JSON — o
rotulo e o primeiro na ordem. Nada e escondido pela escolha de ordem.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.inputs import load_full_curve  # noqa: E402
from bolt_analysis_studio.validation.runner import FLOOR_TRIM  # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
OUT_JSON = ROOT / "New_Theory" / "frontier_classes.json"
OUT_MD = ROOT / "New_Theory" / "frontier_classes.md"

TRIPE = 0.10                 # a meta: MAE < 0,10 E maxerr < 0,10
SPREAD_LIM = 0.10            # (1) scatter de replica
FLOOR_FRAC_LIM = 0.25        # (2) fracao de pontos comida pelo piso
FLOOR_ZERO = 0.02            # (2) "o dado cru vai a zero"
TRUNC_TAIL = 0.15            # (4) dado termina longe do piso
GRID_N = 800                 # pontos p/ dispersão entre curvas (ver _spread_of)
JANELA_FINA = 0.10           # (3b) mediana(s_i)/span p/ o dado contar como fino
LEVEL_MIN_OFFSET = 0.02      # (5) offset de nivel tem de ser real
FLAT_LIM = 0.03              # informacional: planura dos quintis (kernel_diag)

REP_RE = re.compile(r"_rep\d+$")


def cond_key(rec):
    """Assinatura de CONDIÇÃO declarada — a base honesta p/ achar réplicas.

    DEFEITO CONSERTADO (apontado pela sessão paralela em
    `replicate_impossibility_sweep_2026-07-28.md` §3.1): a 1a versao agrupava
    replicas pelo NOME (`_repN$`), o que pega `bauer…fig6_rep1` e PERDE
    `bauer…fig8_test1/2/3` — tres repeticoes do mesmo ensaio que sairam em TRES
    classes diferentes (FORM/METRIC/LEVEL). Tres repeticoes nao podem exigir
    tres consertos. A licao deles, literal: *um classificador por-curva e cego
    para limite por-familia.*

    Medido: os 3 `fig8_test*` tem amplitude/pre-carga/frequencia/parafuso
    IDENTICOS e diferem so na vida (873/1351/1161) — assinatura de replica. Esta
    chave acha isso independentemente do nome.

    NAO e prova de replica, e o motivo e ESTRUTURAL: **`ValidationCase` nao tem
    campo para a carga axial nem para a rugosidade** — no ECCLES a carga axial
    (0 / 0,7 / 1,1 / 2,7 / 3,1 / 3,5 kN) vive so no `notes` e no `case_id`, e no
    CHU a rugosidade so no `case_id` (`Ra1p6um`). Logo esta chave junta, sem
    querer, varreduras deliberadas: medido, ela merge as **10** curvas do ECCLES
    num "grupo" so. Por isso o resultado entra como CANDIDATO, e a incoerencia e
    filtrada pelos tokens do nome (`_token_diff`) antes de virar denuncia.
    O classificador **nunca reclassifica sozinho**; a regra da campanha continua
    valendo: onde nome e nota de aparato discordarem, a NOTA manda.
    """
    c = rec.validation_case
    return (rec.source, rec.family,
            round(float(getattr(c, "transverse_displacement_mm", 0.0) or 0.0), 4),
            round(float(getattr(c, "initial_preload_N", 0.0) or 0.0), 1),
            round(float(getattr(c, "frequency_Hz", 0.0) or 0.0), 4),
            round(float(getattr(c, "preload_percent_yield", 0.0) or 0.0), 2),
            round(float(getattr(c, "mu_initial", 0.0) or 0.0), 4),
            bool(getattr(c, "lubricated", False)),
            str(getattr(c, "bolt_size", "")))


INDEX_RE = re.compile(r"^(test|rep|run|r|no)\d*$", re.I)


def token_diff(members):
    """Tokens que DISTINGUEM os membros de um grupo, ignorando indices.

    `test1/test2/test3` sao indices de repeticao — nao carregam condicao. Ja
    `Ra1p6um` ou `axial3p5kN` carregam. Se o que separa os membros e so indice,
    condicoes declaradas iguais + nomes so-indice = replica de fato, e classes
    divergentes ali sao defeito DO CLASSIFICADOR. Se ha token de condicao, a
    diferenca esta no nome e o "grupo" era varredura deliberada.
    """
    sets = [set(re.split(r"[_\W]+", cid.lower())) for cid in members]
    comum = set.intersection(*sets) if sets else set()
    dif = sorted(t for s in sets for t in (s - comum) if t)
    return [t for t in dict.fromkeys(dif) if not INDEX_RE.match(t)]


# ---------------------------------------------------------------- dado cru
def raw_curve(rec):
    """Curva de referencia CRUA nas convencoes do runner, ANTES do FLOOR_TRIM.

    Copia fiel de runner.py:453-465 (offset -> escala -> normalizacao no 1o
    ponto). Precisamos do "antes" para contar o que a metrica descartou.
    """
    try:
        rel = rec.csv_path.relative_to(ROOT).as_posix()
    except ValueError:
        rel = str(rec.csv_path)
    cyc, r = load_full_curve(rel)
    case = rec.validation_case
    off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)
    scale = float(getattr(case, "csv_x_scale", 1.0) or 1.0)
    cyc = np.maximum(cyc - off, 0.0) * scale
    r = r / max(r[0], 1e-9)
    return cyc, r


# ------------------------------------------------------- (1) replicas
def _spread_of(members, store, lo=None, hi=None):
    """Maior espalhamento max-min entre curvas de dado, na grade comum.

    `lo`/`hi` fixam a janela (convenção da varredura de réplica: a janela
    pontuada por TODOS os membros do grupo). Sem eles, usa a interseção dos
    membros passados — que para um SUBCONJUNTO é mais larga e mais severa.
    """
    curves = []
    for cid in members:
        x = np.asarray(store[cid]["metric_x"], float)
        y = np.asarray(store[cid]["metric_data"], float)
        if x.size >= 3:
            curves.append((x, y))
    if len(curves) < 2:
        return None
    # GRADE: 40 pontos SUB-RESOLVE a dispersão em ~1%, e isso é suficiente para
    # virar um teste de limiar. Medido no BAUER fig6, subconjunto {rep2,3,4,5}:
    # spread 0,19478 (n=20) · 0,19944 (n=40) · 0,20037 (n=100) · 0,20134 (n=2000)
    # ⇒ com n=40 ele passa o limiar 0,20 e o teto do grupo sai 4; convergido,
    # falha e o teto é 3. A 1a versão deste módulo usava n=40 fixo e por isso
    # contradisse (erradamente) a varredura de réplica. 800 pontos = convergido
    # nos grupos desta biblioteca, com margem.
    lo = max(c[0][0] for c in curves) if lo is None else lo
    hi = min(c[0][-1] for c in curves) if hi is None else hi
    if hi <= lo:
        return None
    grid = np.linspace(lo, hi, GRID_N)
    stack = np.vstack([np.interp(grid, x, y) for x, y in curves])
    return float(np.max(stack.max(axis=0) - stack.min(axis=0)))


def viable_ceiling(members, store, tol=2 * TRIPE):
    """Teto de passes do grupo e as EXCEÇÕES NECESSÁRIAS, por busca exaustiva.

    Critério (formulado pela varredura de impossibilidade por réplica, versão
    corrigida de 2026-07-28): uma curva única fica a ≤ 0,10 de um subconjunto S
    **se e somente se** a dispersão de S ≤ 0,20 (aí a mediana ponto-a-ponto
    serve). Logo o TETO é o tamanho do maior subconjunto com dispersão ≤ 0,20.

    Uma curva é exceção **NECESSÁRIA** quando não aparece em NENHUM subconjunto
    viável de tamanho máximo — se aparece em algum, existe um modelo que a
    satisfaz junto com as outras, e ela não é necessariamente exceção.

    ERRATA 3a (e é o conserto do conserto): a errata 2a fez o critério (1)
    marcar TODOS os membros de um grupo com dispersão > 0,10 como DATA-LIMITED.
    Isso super-atribui — dispersão alta prova que **ao menos um** membro viola,
    não que todos violem. No BAUER fig8 o teto é 2 de 3 ⇒ **1** exceção, não 3.
    Trocar "todos" por "os que não cabem em nenhum subconjunto máximo" é a
    afirmação que o dado sustenta.

    CONVENÇÃO DE JANELA — e ela decide o resultado. A dispersão de um subconjunto
    é medida na janela pontuada por **TODOS os membros do grupo** (fixa), não na
    interseção do subconjunto. É a convenção da varredura de réplica ("medido na
    janela pontuada por todas"), e a diferença NÃO é cosmética: medido no BAUER
    fig8, o par `test2+test3` dá spread **0,0402** na janela fixa [26, 835] e
    **0,2815** na janela própria do par [7,3; 1139,6] ⇒ teto **2** contra **1**.
    A janela própria é mais severa porque inclui as caudas onde as réplicas
    divergem. Qual das duas corresponde à meta é **questão aberta** (a métrica
    pontua cada curva na sua PRÓPRIA faixa, o que puxa para a janela própria) —
    registrada no handoff, não decidida aqui.
    """
    from itertools import combinations
    ms = [m for m in members if len(store.get(m, {}).get("metric_x", [])) >= 3]
    if len(ms) < 2:
        return len(ms), []
    xs = [np.asarray(store[m]["metric_x"], float) for m in ms]
    lo, hi = max(x[0] for x in xs), min(x[-1] for x in xs)   # janela do GRUPO
    if hi <= lo:
        return len(ms), []
    for k in range(len(ms), 1, -1):
        viaveis = [set(c) for c in combinations(ms, k)
                   if (_spread_of(list(c), store, lo, hi) or 9.9) <= tol]
        if viaveis:
            uniao = set().union(*viaveis)
            return k, sorted(set(ms) - uniao)
    return 1, []          # nenhum par cabe: cada curva sozinha sempre "passa"


def condition_groups(recs_by_id, store):
    """Grupos CANDIDATOS de replica por condicao declarada identica (ver
    `cond_key`). Devolve {case_id: {membros, n, spread}} para grupos com >= 2.
    """
    groups = defaultdict(list)
    for cid in store:
        if cid in recs_by_id:
            groups[cond_key(recs_by_id[cid])].append(cid)
    out = {}
    for key, members in groups.items():
        if len(members) < 2:
            continue
        sp = _spread_of(members, store)
        # teto/exceções necessárias só fazem sentido em grupo de RÉPLICA (nomes
        # diferindo só por índice); num grupo que é varredura deliberada a
        # dispersão é o efeito estudado, não scatter.
        if token_diff(sorted(members)):
            k, nec = None, []
        else:
            k, nec = viable_ceiling(sorted(members), store)
        for cid in members:
            out[cid] = {"membros": sorted(members), "n": len(members),
                        "spread": None if sp is None else round(sp, 4),
                        "teto": k, "excecoes_necessarias": nec,
                        "necessaria": cid in nec}
    return out


def replicate_spread(recs_by_id, store):
    """Espalhamento entre replicas nominais (`..._repN`), por grupo.

    Interpola cada replica na grade comum (interseccao dos x) e devolve o
    maximo espalhamento max-min entre elas. Grupo com 1 membro -> None.
    """
    groups = defaultdict(list)
    for cid in store:
        if cid in recs_by_id and REP_RE.search(cid):
            groups[REP_RE.sub("", cid)].append(cid)
    out = {}
    for key, members in groups.items():
        if len(members) < 2:
            continue
        curves = []
        for cid in members:
            x = np.asarray(store[cid]["metric_x"], float)
            y = np.asarray(store[cid]["metric_data"], float)
            if x.size >= 3:
                curves.append((x, y))
        if len(curves) < 2:
            continue
        lo = max(c[0][0] for c in curves)
        hi = min(c[0][-1] for c in curves)
        if hi <= lo:
            continue
        grid = np.linspace(lo, hi, 40)
        stack = np.vstack([np.interp(grid, x, y) for x, y in curves])
        spread = float(np.max(stack.max(axis=0) - stack.min(axis=0)))
        for cid in members:
            out[cid] = {"grupo": key, "n_replicas": len(curves),
                        "spread_max": spread}
    return out


# --------------------------------------------------- perfil / quintis
def quintile_profile(res):
    """Media do resduo por quintil (indice), e a versao detrendada."""
    n = res.size
    edges = [int(round(k * n / 5)) for k in range(6)]
    raw = []
    for a, b in zip(edges[:-1], edges[1:]):
        seg = res[a:max(b, a + 1)]
        raw.append(float(seg.mean()) if seg.size else 0.0)
    m = float(res.mean())
    return raw, [q - m for q in raw]


def timing_need(x, data, i):
    """INFORMACIONAL (nao classifica — ver ERRATA no cabecalho).

    Precisao de relogio que a banda exige no ponto i, pela inclinacao do dado.
    Devolve (dx_needed, espacamento_local, slope_dado).
    """
    n = x.size
    lo, hi = max(i - 1, 0), min(i + 1, n - 1)
    dx = float(x[hi] - x[lo])
    dy = float(data[hi] - data[lo])
    if dx <= 0:
        return float("inf"), 0.0, 0.0
    slope = abs(dy) / dx
    spacing = dx / max(hi - lo, 1)
    dx_needed = (TRIPE / slope) if slope > 0 else float("inf")
    return dx_needed, spacing, slope


def spacings(x):
    """Meia-distancia aos vizinhos = UM intervalo de amostragem do dado."""
    n = x.size
    s = np.empty(n)
    for i in range(n):
        lo, hi = max(i - 1, 0), min(i + 1, n - 1)
        s[i] = (float(x[hi]) - float(x[lo])) / 2.0
    # ponto unico ou grade degenerada: usa o menor passo positivo da grade
    dx = np.diff(x)
    fallback = float(dx[dx > 0].min()) if np.any(dx > 0) else 0.0
    s[s <= 0] = fallback
    return s


def rescue(x, data, dense_x, dense_y):
    """Fracao dos pontos resgatados por deslocamento horizontal de <= 1 intervalo.

    Para cada ponto i, o menor desvio vertical que o modelo atinge dentro da
    janela [x_i - s_i, x_i + s_i], avaliado na grade DENSA do modelo mais as
    duas bordas da janela (interpoladas). Resgatado se esse desvio <= 0,10.
    """
    s = spacings(x)
    devs = np.empty(x.size)
    for i in range(x.size):
        a, b = float(x[i] - s[i]), float(x[i] + s[i])
        sel = dense_x[(dense_x >= a) & (dense_x <= b)]
        cand = np.concatenate(([a, b], sel))
        vals = np.interp(cand, dense_x, dense_y)
        devs[i] = float(np.min(np.abs(vals - data[i])))
    return devs


# ------------------------------------------------------------- varredura
def classify():
    store = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    reps = replicate_spread(recs, store)
    cgroups = condition_groups(recs, store)

    rows = []
    for cid, r in store.items():
        mae, maxerr = r.get("mae"), r.get("maxerr")
        if mae is None or maxerr is None:
            continue
        if mae < TRIPE and maxerr < TRIPE:
            continue                                   # dentro do tripe
        rec = recs.get(cid)
        x = np.asarray(r["metric_x"], float)
        pred = np.asarray(r["metric_pred"], float)
        data = np.asarray(r["metric_data"], float)
        if x.size < 3:
            continue
        res = pred - data
        i = int(np.argmax(np.abs(res)))
        # (5) o que sobraria do maxerr se o NIVEL fosse consertado
        maxerr_pos_nivel = float(np.max(np.abs(res - res.mean())))
        _, q_det = quintile_profile(res)
        dx_needed, spacing, slope = timing_need(x, data, i)
        span = float(x[-1] - x[0]) or 1.0

        # trajetoria DENSA do modelo (mesma que gerou metric_pred, erro <= 2e-5)
        dense_x = np.asarray(r["cycles"], float)
        dense_y = np.asarray(r["ratio"], float) / max(float(r["align"]), 1e-12)
        devs = rescue(x, data, dense_x, dense_y)
        n_resgatados = int(np.sum(devs <= TRIPE))
        frac_resg = n_resgatados / x.size
        # (3b) o resgate so vale como "limite da metrica" se o dado for fino
        janela_rel = float(np.median(spacings(x))) / span

        # inclinacao do DADO: no fim vs maxima da curva (platou ou foi cortado?)
        d_slope = np.abs(np.diff(data) / np.maximum(np.diff(x), 1e-12))
        slope_fim = float(d_slope[-1]) if d_slope.size else 0.0
        slope_max = float(d_slope.max()) if d_slope.size else 0.0
        slope_fim_rel = slope_fim / slope_max if slope_max > 0 else 0.0

        # o que a metrica descartou
        n_raw = n_floor = None
        raw_min = None
        if rec is not None and rec.case_class == "full_curve":
            try:
                _, r_all = raw_curve(rec)
                n_raw = int(r_all.size)
                n_floor = int(np.sum(r_all < FLOOR_TRIM))
                raw_min = float(r_all.min())
            except Exception as exc:                   # pragma: no cover
                print(f"  [aviso] {cid}: CSV cru ilegivel ({exc})")

        # ---- criterios, na ORDEM declarada no cabecalho ----
        flags = []
        rep = reps.get(cid)
        flat = max(abs(q) for q in q_det)
        # (1) EXCECAO NECESSARIA por teto do grupo de replica (errata 3a).
        # NAO basta "o grupo tem dispersao > 0,10": isso prova que ALGUM membro
        # viola, nao que este viole. So entra quem nao cabe em nenhum
        # subconjunto viavel de tamanho maximo.
        cg = cgroups.get(cid) or {}
        if cg.get("necessaria"):
            flags.append("scatter_replica")
        if maxerr_pos_nivel < TRIPE and abs(res.mean()) > LEVEL_MIN_OFFSET:
            flags.append("nivel")
        if (n_raw and n_floor is not None and raw_min is not None
                and n_floor / n_raw >= FLOOR_FRAC_LIM and raw_min < FLOOR_ZERO):
            flags.append("floor_trim")
        if frac_resg >= 1.0:
            flags.append("resgate_horizontal" if janela_rel < JANELA_FINA
                         else "resolucao_grossa")
        if (i == x.size - 1 and res[i] < 0 and data[-1] > TRUNC_TAIL
                and slope_fim_rel >= 0.30):
            flags.append("truncamento")

        classe = {"scatter_replica": "DATA-LIMITED", "nivel": "LEVEL-LIMITED",
                  "floor_trim": "METRIC-LIMITED",
                  "resgate_horizontal": "METRIC-LIMITED",
                  "resolucao_grossa": "DATA-LIMITED",
                  "truncamento": "DATA-LIMITED"}.get(flags[0] if flags else "",
                                                     "FORM-LIMITED")
        rows.append({
            "case_id": cid,
            "fonte": getattr(rec, "source", "?") if rec else "?",
            "classe": classe,
            "motivo": flags[0] if flags else "forma",
            "flags_todos": flags,
            "mae": round(float(mae), 4),
            "maxerr": round(float(maxerr), 4),
            "so_maxerr": bool(mae < TRIPE <= maxerr),
            "n_pontuados": int(x.size),
            "n_crus": n_raw,
            "n_comidos_pelo_piso": n_floor,
            "ratio_cru_min": None if raw_min is None else round(raw_min, 4),
            "trim_n_max": r["config_used"].get("trim_n_max"),
            "pos_maxerr": round(i / (x.size - 1), 3),
            "terminal": bool(i == x.size - 1),
            "sinal_no_max": "modelo_acima" if res[i] > 0 else "modelo_abaixo",
            "res_medio": round(float(res.mean()), 4),
            "maxerr_pos_nivel": round(maxerr_pos_nivel, 4),
            "perfil_detrendado": [round(q, 4) for q in q_det],
            "planura": round(flat, 4),
            "perfil_plano": bool(flat < FLAT_LIM),
            "frac_resgatada": round(frac_resg, 3),
            "janela_rel": round(janela_rel, 4),
            "n_nao_resgatados": int(x.size - n_resgatados),
            "desvio_resgate_max": round(float(devs.max()), 4),
            "slope_fim_rel": round(slope_fim_rel, 3),
            "slope_dado_no_max": float(f"{slope:.4g}"),
            "dx_needed": None if not np.isfinite(dx_needed) else float(f"{dx_needed:.4g}"),
            "espacamento_local": float(f"{spacing:.4g}"),
            "relogio_pct_do_span": (None if not np.isfinite(dx_needed)
                                    else round(100.0 * dx_needed / span, 4)),
            "spread_replica": None if not rep else round(rep["spread_max"], 4),
            "dado_final": round(float(data[-1]), 4),
            "grupo_condicao": (cgroups.get(cid) or {}).get("membros"),
            "spread_grupo_condicao": (cgroups.get(cid) or {}).get("spread"),
            "teto_grupo": (cgroups.get(cid) or {}).get("teto"),
            "excecoes_necessarias_do_grupo":
                (cgroups.get(cid) or {}).get("excecoes_necessarias"),
            "e_excecao_necessaria": bool((cgroups.get(cid) or {}).get("necessaria")),
        })
    rows.sort(key=lambda d: (d["fonte"], d["case_id"]))

    # CHECAGEM DE COERENCIA DE FAMILIA (nao reclassifica — DENUNCIA).
    # Membros do mesmo grupo de condicao que receberam classes DIFERENTES:
    # tres repeticoes do mesmo ensaio nao podem exigir tres consertos.
    byid = {d["case_id"]: d for d in rows}
    for d in rows:
        g = d["grupo_condicao"]
        irmaos = [byid[c]["classe"] for c in (g or []) if c in byid]
        d["classes_no_grupo"] = sorted(set(irmaos))
        td = token_diff(g) if g else []
        d["tokens_que_distinguem"] = td
        # incoerente = condicoes declaradas iguais E nomes so-indice E classes
        # divergentes. Com token de condicao, o "grupo" era varredura deliberada.
        d["familia_incoerente"] = bool(len(set(irmaos)) > 1 and not td)
    return rows


# ------------------------------------------------------------- relatorio
# Controle: veredictos ESTABELECIDOS por outros diagnosticos, contra o MESMO
# store. case_id conferidos contra o registry (a 1a versao deste dict chutou os
# nomes e 6 de 7 nao existiam — o "AUSENTE" mascarou o defeito do criterio 3).
CROSS = {
    "bauer2024_M8_fig6_rep1": (
        "DATA-LIMITED", "f5_excecoes_propostas: spread entre replicas 0,561"),
    "eccles2010_fig8a_no_axial_baseline1": (
        "LEVEL-LIMITED", "kernel_diagnostic grupo B: perfil detrendado plano "
                         "(max |0,022|), resduo bruto ~-0,043 uniforme"),
    "eccles2010_fig8c_no_axial_baseline2": (
        "LEVEL-LIMITED", "kernel_diagnostic grupo B: idem"),
    "eccles2010_fig8b_axial_0p7kN_intermittent": (
        "METRIC-LIMITED", "trilha B 07-27: FLOOR_TRIM corta 27 de 35 pontos"),
    "eccles2010_fig6_annotated_4kN_axial": (
        "METRIC-LIMITED", "trilha B 07-27: dado cru vai a ZERO (destacamento)"),
    "10_Yang_2023_phenomenological_model__0_25_mm__2": (
        "FORM-LIMITED", "fila item 1: tri-falsificado, k_ratchet INERTE, "
                        "delta_free BINARIO, loose_amp_exp PIORA"),
    "lu2024_M8_fig20_T4Nm": (
        "FORM-LIMITED", "lu2024_diagnostic: perda front-loaded (47% do dado vs "
                        "27% do modelo nos 1-2 primeiros ciclos)"),
    "chu2026ti_D0p4mm_F0_49kN_test2": (
        "FORM-LIMITED", "kernel_diagnostic grupo A: r>=0,90 com Yang19/Karlsen/"
                        "Zhang2006, colapsa cedo e trava tarde"),
    "rousseau2025_steel_t10": (
        "FORM-LIMITED", "rousseau prereg: arresto TERMINAL, perda-por-slip "
                        "satura cedo (retem 0,325 vs 0,137 medido)"),
}


ACAO = {
    "nivel": "ler o nível (`loose_arrest_floor`) com procedência — zero física nova",
    "scatter_replica": "nada a fazer no modelo: a meta está abaixo da reprodutibilidade do ensaio",
    "resolucao_grossa": "redigitalizar mais fino (hoje o dado não resolve o relógio)",
    "floor_trim": "decidir a convenção: isentar a família do `FLOOR_TRIM` e medir a curva inteira",
    "resgate_horizontal": "mudar o eixo da métrica (o dado existe e a forma acerta)",
    "truncamento": "pedir/estender o dado — a medição parou no meio do processo",
    "forma": "construir mecanismo (prereg + gate)",
}


def write_md(rows):
    by = defaultdict(list)
    for d in rows:
        by[d["classe"]].append(d)
    n_so_max = sum(1 for d in rows if d["so_maxerr"])
    L = []
    A = L.append
    A("# Varredura das 3 classes — os 55 fora do tripé, curva a curva\n")
    A("> **2026-07-28.** Item 3 da fila de decisões, autorizado. Medido no store")
    A("> certificado `4f5bedfbace4` (203 registros, fingerprint único, os 3 vetores")
    A("> da métrica presentes em 203/203). **Só-leitura:** nenhuma simulação, nenhum")
    A("> fit, nenhuma adoção. Script: `New_Theory/frontier_classes.py`; números")
    A("> crus por curva: `New_Theory/frontier_classes.json`.\n")
    A("> **Fronteira declarada (sessão paralela).** Uma segunda sessão tem um")
    A("> pré-registro de métrica ativo com gates congelados")
    A("> (`specs/2026-07-28-metrica-banda-v2-prereg.md`). Esta varredura mede sob a")
    A("> métrica **canônica de hoje** e **não é evidência a favor nem contra**")
    A("> aquele prereg: seus números não devem ser importados para os gates dele,")
    A("> sob pena de virar evidência post-hoc dentro de um pré-compromisso. Pela")
    A("> regra §4.43, se a métrica canônica mudar, **esta classificação vira")
    A("> suspeita e tem de ser re-rodada** — em particular a classe METRIC-LIMITED,")
    A("> que é definida contra a convenção vigente.\n")
    A("---\n")
    A("## 1. Resultado em uma frase\n")
    nf = len(by["FORM-LIMITED"])
    A(f"**{len(rows) - nf} das {len(rows)} curvas fora do tripé não pedem física "
      f"nova** — pedem ler um nível ({len(by['LEVEL-LIMITED'])}), decidir uma "
      f"convenção de métrica ({len(by['METRIC-LIMITED'])}) ou mexer no dado "
      f"({len(by['DATA-LIMITED'])}). As outras **{nf}** são form-limited de "
      f"verdade.\n")
    A("| classe | n | ação que fecha | custo |")
    A("|---|--:|---|---|")
    for k, custo in (("LEVEL-LIMITED", "leitura com procedência"),
                     ("METRIC-LIMITED", "decisão de convenção"),
                     ("DATA-LIMITED", "dado novo (ou exceção assinada)"),
                     ("FORM-LIMITED", "prereg + gate, 1 forma por vez")):
        acoes = sorted({ACAO[d["motivo"]].split(" —")[0].split(" (")[0]
                        for d in by[k]})
        A(f"| **{k}** | {len(by[k])} | {'; '.join(acoes)} | {custo} |")
    A("")
    n_lvl_max = sum(1 for d in by["LEVEL-LIMITED"] if d["so_maxerr"])
    A(f"**{n_so_max} das {len(rows)} violam SÓ o `maxerr`** (o MAE já está dentro)"
      f" — reprodução independente do censo de 07-27 (34 pelo pico, 21 pelos "
      f"dois), o que confirma que esta varredura lê o mesmo conjunto da "
      f"certificação. E **{n_lvl_max} das {len(by['LEVEL-LIMITED'])} "
      f"LEVEL-LIMITED** violam só o pico: nelas o nível é o único obstáculo.\n")
    A("---\n")
    A("## 2. As curvas que NÃO pedem forma\n")
    A("`sobra` = `max|resíduo − média(resíduo)|`, o que restaria do pico se o nível")
    A("fosse consertado. `resg` = fração dos pontos que o modelo alcança dentro de")
    A("0,10 deslocando-se no máximo UM intervalo de amostragem do dado.")
    A("`n` = pontos pontuados / pontos crus do CSV.\n")
    for k in ("LEVEL-LIMITED", "METRIC-LIMITED", "DATA-LIMITED"):
        A(f"### {k} ({len(by[k])})\n")
        A("| curva | fonte | MAE | maxerr | sobra | resg | n | motivo |")
        A("|---|---|--:|--:|--:|--:|--:|---|")
        for d in sorted(by[k], key=lambda z: z["maxerr"]):
            A(f"| `{d['case_id']}` | {d['fonte']} | {d['mae']:.3f} | "
              f"{d['maxerr']:.3f} | {d['maxerr_pos_nivel']:.3f} | "
              f"{d['frac_resgatada']:.2f} | {d['n_pontuados']}/{d['n_crus']} | "
              f"{d['motivo']} |")
        A("")
        A(f"**Ação:** " + " · ".join(sorted({ACAO[d['motivo']] for d in by[k]})) + "\n")
    A("> **Caveat da classe LEVEL-LIMITED — condição necessária, não prova.**")
    A("> `sobra < 0,10` diz que o erro *é* de nível: removido um deslocamento")
    A("> uniforme, o pico entra no tripé. Não prova que **ler o `loose_arrest_floor`**")
    A("> o remove, porque o piso age na **cauda**, não uniformemente em todos os")
    A("> ciclos. A direção necessária está na coluna `res.médio`: positivo = o modelo")
    A("> retém mais que o dado (precisa de piso **menor**), negativo = retém menos")
    A("> (piso **maior**). Fechar cada uma exige a leitura com procedência e o gate")
    A("> — o que esta varredura entrega é que essas 7 **não precisam de forma nova**.")
    A("> **[MEDIDO EM 2026-07-28, LEIA ANTES DE AGIR: `level_seven_probe.md`.](level_seven_probe.md)**")
    A("> As duas alavancas de nível que a campanha sabe **ler** do dado")
    A("> (`loose_arrest_floor` do platô, `emb_depth` da queda-inicial) foram sondadas")
    A("> nas 7: **fecham 1**, melhoram 1, 1 é inerte e **3 PIORAM**. Ou seja \"não")
    A("> precisa de forma nova\" **não** significa \"fecha de graça\" — o nível dessas")
    A("> curvas não é alcançável pelos leitores existentes, e a ação para 5 das 6 é")
    A("> uma pergunta aberta, não uma leitura.\n")
    A("| curva | res.médio | direção do piso |")
    A("|---|--:|---|")
    for d in sorted(by["LEVEL-LIMITED"], key=lambda z: z["res_medio"]):
        dirn = ("menor (modelo retém demais)" if d["res_medio"] > 0
                else "maior (modelo retém de menos)")
        A(f"| `{d['case_id']}` | {d['res_medio']:+.4f} | {dirn} |")
    A("")
    A("---\n")
    A("## 3. Controle: contra veredictos já estabelecidos\n")
    A("O classificador foi confrontado com 9 veredictos que **outros** diagnósticos")
    A("já fixaram sobre o mesmo store. **7 dos 9 coincidem.** As 2 divergências não")
    A("são ruído — cada uma corrige uma afirmação anterior, com número:\n")
    A("**(a) `eccles2010_fig6` — eu esperava METRIC-LIMITED, mediu FORM-LIMITED.**")
    A("A trilha B de 07-27 nomeou fig6 na família cujo dado cru vai a ZERO, e eu li")
    A("isso como \"dominada pelo `FLOOR_TRIM`\". Medido: o piso come **4 de 29**")
    A("pontos (14%) no fig6, contra **27 de 35** (77%) no fig8b. Além disso o fig6")
    A("tem planura 0,226 (forma francamente errada) e **32% dos pontos não são")
    A("resgatáveis** por deslocamento nenhum. Ou seja: pertencer à família do achado")
    A("do `FLOOR_TRIM` ≠ ser limitada por ele. **Consequência prática:** a decisão")
    A("(i) de 07-27 — isentar a família do piso e medir a curva inteira — mudaria o")
    A("veredicto do **fig8b**, e não do fig6/fig8d, que seguem form-limited")
    A("(coerente com o G-B1 FAIL: aplicar a receita levou o fig6 de 0,467 a 1,028).\n")
    A("**(b) `eccles2010_fig8c` — eu esperava LEVEL-LIMITED, mediu FORM-LIMITED por")
    A("0,002.** O `kernel_diagnostic` mediu o perfil detrendado do par fig8a+fig8c")
    A("**na média das 2 curvas** (máx |0,022|); por curva a planura é 0,047 e 0,054.")
    A("E o que decide: com o nível consertado sobra **0,0797** no fig8a (entra) e")
    A("**0,1021** no fig8c (**não** entra, por 0,0021). Então a recomendação nº 2")
    A("daquele diagnóstico — \"tentar nível antes de forma; se o floor fechar, custam")
    A("zero física nova\" — vale para **uma** das duas, não para as duas. O fig8c fica")
    A("na fronteira: nível quase fecha, e o que sobra é um pico localizado.\n")
    A("Os 3 números de `FLOOR_TRIM` que este script mede sozinho (fig6 **4/29**,")
    A("fig8b **27/35**, fig8d **7/37**) reproduzem **exatamente** os publicados em")
    A("07-27 — é a validação de que o pipeline de dado cru aqui é o do runner.\n")
    A("---\n")
    A("## 4. As 36 form-limited, por fonte\n")
    A("`resg mín` = a curva menos resgatável da fonte. Quanto menor, mais o erro é")
    A("de forma e não de relógio.\n")
    A("| fonte | n | maxerr | resg mín |")
    A("|---|--:|---|--:|")
    g = defaultdict(list)
    for d in by["FORM-LIMITED"]:
        g[d["fonte"]].append(d)
    for src in sorted(g, key=lambda s: (-len(g[s]), s)):
        ms = ", ".join(f"{d['maxerr']:.3f}" for d in sorted(
            g[src], key=lambda z: -z["maxerr"]))
        A(f"| {src} | {len(g[src])} | {ms} | "
          f"{min(d['frac_resgatada'] for d in g[src]):.2f} |")
    A("")
    A("O `resg mín` separa duas coisas dentro da mesma classe: **CHU (0,16)** e")
    A("**YANG_2023_AME (0,13)** erram de forma em quase todo ponto — nenhum")
    A("deslocamento salva. Já **JCSR (0,85)** e **KARLSEN (0,86)** erram em poucos")
    A("pontos, o que as torna as form-limited mais próximas de fechar.\n")
    A("---\n")
    A("## 5. O que isto muda na fila de decisões\n")
    A("1. **A fila deixa de ter 55 itens de uma classe só.** As ações se separam em")
    A("   4, e **19 curvas** saem da conta de \"precisa de física nova\" — que era o")
    A("   ponto do item 3.")
    A("2. **7 curvas de nível são o alvo mais barato da meta** (as 7 violam SÓ o")
    A("   pico), e estão em **7 fontes diferentes** — não é uma fonte com problema,")
    A("   é o piso lido por par. Nenhuma delas exige prereg de forma.")
    A("3. **A decisão de convenção do `FLOOR_TRIM` vale 3 curvas**, não a família")
    A("   toda: `eccles fig8b` + `lu2024 amp1p5/amp2p0` (o LU também tem dado que vai")
    A("   a zero — 33% e 46% dos pontos sob o piso, o que não estava registrado).")
    A("4. **`bauer2024_M8_fig6` ×4 confirma-se irredutível** — espalhamento entre")
    A("   réplicas **0,459** na sobreposição comum (a lista F5 traz 0,561, medido em")
    A("   janela maior; as duas são 4-5× a tolerância da meta).")
    A("5. **Uma curva do YANG_2023_IJPEM é data-limited, não form-limited:** a")
    A("   `0,50 mm` é pontuada sobre **5 pontos**, e com essa resolução o dado não")
    A("   distingue relógio nenhum. As outras 6 seguem form-limited com maxerr")
    A("   0,16-0,56 — a tri-falsificação do item 1 da fila continua válida para elas.\n")
    A("**Nada aqui autoriza adoção.** É diagnóstico: cada ação da coluna \"ação que")
    A("fecha\" continua exigindo a decisão e o gate que a campanha já prevê.\n")
    A("---\n")
    A("## 6. Errata 2ª: o classificador por-curva era cego a limite por-família\n")
    inc = [d for d in rows if d.get("familia_incoerente")]
    A("A sessão paralela achou o defeito por outro caminho")
    A("(`replicate_impossibility_sweep_2026-07-28.md` §3.1) e a frase é dela:")
    A("*um classificador por-curva é cego para limite por-família.*")
    A("`bauer2024_M12_fig8_test1/2/3` são **três repetições do mesmo ensaio** e a")
    A("1ª versão deste classificador as pôs em **três classes diferentes**")
    A("(FORM / METRIC / LEVEL) — três repetições não podem exigir três consertos.\n")
    A("**Por que passou:** o agrupamento de réplicas era por **nome** (`_repN$`),")
    A("e a fig8 do Bauer usa `testN`. A observação deles fecha o diagnóstico —")
    A("*\"a diferença de vocabulário (`test` na fig8 vs `rep` na fig6) é escolha do")
    A("digitalizador, não distinção de condição\"*.\n")
    A("**Conserto:** as réplicas passam a ser achadas por **condição declarada")
    A("idêntica** (`cond_key`) com os nomes diferindo **só por índice**")
    A("(`token_diff` vazio). Isso reproduz o veredicto deles **sem depender da")
    A("nota de aparato** — e as 3 curvas que eles provaram irredutíveis são")
    A("exatamente as 3 que este critério move.\n")
    A("| curva | classe na 1ª versão | agora |")
    A("|---|---|---|")
    for cid, antes in (("bauer2024_M12_fig8_test1", "FORM-LIMITED"),
                       ("bauer2024_M12_fig8_test2", "METRIC-LIMITED"),
                       ("bauer2024_M12_fig8_test3", "LEVEL-LIMITED")):
        agora = next((d["classe"] for d in rows if d["case_id"] == cid), "?")
        A(f"| `{cid}` | {antes} | **{agora}** |")
    A("")
    A("**Efeito no censo:** FORM 36 → **35** · METRIC 7 → **6** · LEVEL 7 → **6**")
    A("· DATA 5 → **8**. O número que o Manual publicou (36 form-limited) está")
    A("**superado** — 35.\n")
    A("**O que o conserto NÃO faz:** `ValidationCase` **não tem campo para carga")
    A("axial nem para rugosidade** (no ECCLES a axial vive no `notes`/`case_id`;")
    A("no CHU a rugosidade só no `case_id`), então a chave de condição sozinha")
    A("junta varreduras deliberadas — medido, ela merge as **10** curvas do")
    A("ECCLES num grupo. É o filtro de tokens que separa: dos 3 grupos com")
    A("classes divergentes, **1** é defeito real (Bauer, só índices) e **2** são")
    A("explicados por condição no nome (`ra1p6um`; `0p7kn…3p5kn`).")
    A(f"Denúncias vivas hoje: **{len(inc)}** curvas em famílias incoerentes.\n")
    A("---\n")
    A("## 6b. Errata 3ª: a errata 2ª super-atribuía — e o motivo era a GRADE\n")
    nec = sorted({d["case_id"] for d in rows if d.get("e_excecao_necessaria")})
    A("A errata 2ª fez o critério (1) marcar **todos** os membros de um grupo com")
    A("dispersão > 0,10 como DATA-LIMITED. Está errado: dispersão alta prova que")
    A("**ao menos um** membro viola, não que todos violem. Corrigido com o **teto")
    A("de grupo** por busca exaustiva — o maior subconjunto com dispersão ≤ 0,20 —")
    A("e só entra em DATA-LIMITED quem não cabe em **nenhum** subconjunto máximo.\n")
    A("**Achado de método, e o defeito era meu:** a 1ª tentativa deste cálculo")
    A("contradisse a varredura de réplica (dava teto 4 onde ela dá 3), e a causa")
    A("era a **grade de interpolação**. Medido no subconjunto `{rep2,3,4,5}` do")
    A("BAUER fig6:\n")
    A("| pontos na grade | dispersão | ≤ 0,20? |")
    A("|--:|--:|:--:|")
    for n, s in ((20, 0.19478), (40, 0.19944), (100, 0.20037), (400, 0.20125),
                 (2000, 0.20134)):
        A(f"| {n} | {s:.5f} | {'sim' if s <= 0.20 else '**não**'} |")
    A("")
    A("Com 40 pontos ele passa e o teto sai **4**; convergido, falha e o teto é")
    A("**3**. Uma sub-resolução de ~1 % virou um veredicto de teto — e a grade")
    A(f"agora é **{GRID_N}** pontos, convergida com margem.\n")
    A("**Onde as duas análises convergem e onde divergem** (contra a")
    A("`replicate_impossibility_sweep_2026-07-28.md`, versão corrigida):\n")
    A("| | varredura de réplica | aqui |")
    A("|---|---|---|")
    A("| teto BAUER fig6 | 3 de 6 | **3 de 6** ✅ |")
    A("| teto BAUER fig8 | 2 de 3 | **2 de 3** ✅ |")
    A("| nome no fig8 | `test1` | **`test1`** ✅ |")
    A("| nome no fig6 | `rep1`, `rep5`, `rep6` | **só `rep1`** ❌ |")
    A("")
    A("A divergência é precisa e é sobre **contagem vs nome**: o teto 3 de 6 diz")
    A("que **3 curvas têm de ser exceção** (isso bate), mas existem **3**")
    A("subconjuntos viáveis de tamanho 3 — `{rep2,rep3,rep4}` (0,0738),")
    A("`{rep3,rep4,rep5}` (0,1938) e `{rep3,rep5,rep6}` (0,1909). Como `rep5` e")
    A("`rep6` aparecem em algum deles, elas **não são necessariamente** exceção:")
    A("quais 3 falham depende de qual subconjunto o modelo realiza. Só `rep1` está")
    A("em nenhum. A varredura tomou o melhor subconjunto (`rep2/3/4`) como se")
    A("fosse o único.\n")
    A(f"**Exceções necessárias POR NOME neste conjunto: {len(nec)}** — ")
    A("`" + "` · `".join(nec) + "`.")
    A("**Por contagem**, somando os tetos de grupo, são **6** (3 do fig6 + 1 do")
    A("fig8 + 1 do Eccles no-axial + 1 de resolução grossa) — o mesmo total da")
    A("varredura de réplica. O Eccles não aparece nomeado aqui porque a chave de")
    A("condição **não isola o subgrupo no-axial**: `ValidationCase` não tem campo")
    A("de carga axial (§6).\n")
    A("---\n")
    A("## 7. Reprodutibilidade\n")
    A("```")
    A("py -3.12 New_Theory/frontier_classes.py")
    A("```")
    A("Critérios, limiares e ordem de decisão estão no cabeçalho do script,")
    A("com a errata das duas passadas descartadas. Todo `flags_todos` vai ao JSON:")
    A("curva que satisfaz mais de um critério não some na escolha de ordem.")
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    rows = classify()
    by_class = defaultdict(list)
    for d in rows:
        by_class[d["classe"]].append(d)

    print(f"\n{len(rows)} curvas fora do tripe\n")
    for k in ("FORM-LIMITED", "METRIC-LIMITED", "DATA-LIMITED", "LEVEL-LIMITED"):
        print(f"  {k:16s} {len(by_class[k]):3d}")

    print("\n-- controle: veredictos ja estabelecidos (mesmo store) --")
    hits = 0
    for cid, (want, why) in sorted(CROSS.items()):
        d0 = next((d for d in rows if d["case_id"] == cid), None)
        if d0 is None:
            print(f"  ?? {cid[:44]:44s} AUSENTE do conjunto fora-do-tripe")
            continue
        ok = got = d0["classe"]
        hits += got == want
        tag = "OK     " if got == want else "DIVERGE"
        print(f"  {tag} {cid[:44]:44s} esperado={want:15s} medido={got}"
              f" ({d0['motivo']})")
        if got != want:
            print(f"          -> {why}")
            print(f"          -> flags={d0['flags_todos']} planura={d0['planura']}"
                  f" resg={d0['frac_resgatada']} res_medio={d0['res_medio']}")
        del ok
    print(f"  -> {hits}/{len(CROSS)} coincidem")

    OUT_JSON.write_text(json.dumps(
        {"fingerprint": "4f5bedfbace4", "n": len(rows),
         "limiares": {"tripe": TRIPE, "spread": SPREAD_LIM,
                      "floor_frac": FLOOR_FRAC_LIM, "floor_zero": FLOOR_ZERO,
                      "trunc_tail": TRUNC_TAIL, "flat_info": FLAT_LIM,
                      "level_min_offset": LEVEL_MIN_OFFSET},
         "curvas": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
    write_md(rows)
    print(f"\nJSON -> {OUT_JSON.relative_to(ROOT)}")
    print(f"MD   -> {OUT_MD.relative_to(ROOT)}")
    return rows


if __name__ == "__main__":
    main()
