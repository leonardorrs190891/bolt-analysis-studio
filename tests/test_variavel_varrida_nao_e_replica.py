"""Duas curvas da MESMA fonte não podem ter a MESMA assinatura de input.

## O defeito que esta guarda existe para impedir

Tratar a **variável varrida** como se fosse **réplica** já reincidiu **7 vezes** neste
projeto, e cada vez custou horas e uma retratação:

* o `ECCLES_2010` pareava curvas de carga axial 0 a 3,5 kN como réplicas (P-15);
* o `ICMEZ_2025` pareava grip 13,8 × 19,8 mm nas 4 famílias (bloqueio G, −5 curvas);
* a família δ=0,5 do `CHU` pareava Ra 1,6 × 0,4 µm e **inflava o limite que aprovava** o
  `test5` da família boa (bloqueio H);
* o `LU_2024` cruzava **protocolos** (§3.1.3 half-sine de máquina × §3.2 manual) — 5 F7
  retratadas;
* o `ROUSSEAU` pareava **espessuras** diferentes como réplicas — 3 exceções retratadas;
* o `CACCESE` pareava as 7 condições entre si — 1 retratação, piso 0,121 → 0,0372;
* e o teste de premissa F5 lia a `eccles2010_fig7` como *"ensemble de 4 réplicas"* porque,
  **aos olhos do modelo, elas eram**: os 10 configs da fonte eram idênticos.

⚠️ **A defesa até 2026-08-23 eram DUAS LISTAS À MÃO** — `_SEM_FAMILIA_MECANICA` (bloqueia)
e `_PARES_REPLICA_DECLARADOS` (libera). Lista à mão é exatamente **por que** o erro voltou
sete vezes: ela protege o que alguém lembrou de escrever.

## A regra que este arquivo instala

**Duas curvas da mesma fonte são réplicas apenas se TODOS os inputs registrados forem
iguais.** Assinaturas iguais ⇒ ou são réplicas de verdade, ou **falta um input** — e o teste
obriga a dizer qual.

⚠️ **O ganho não é só bloquear: é LIBERAR.** O bloqueio manual do `ECCLES_2010` estava
*"certo em espécie e largo demais em escopo"* — proibia também o par `fig8a`×`fig8c`, que é
legítimo (mesmos `no_axial` baselines) e cuja declaração deu à fonte um piso válido. Uma
regra derivada dos inputs permite o par bom e barra o ruim, sem curadoria.

## Estado medido em 2026-08-23

Das **14** fontes hoje em `_SEM_FAMILIA_MECANICA`, os inputs **já distinguem** as curvas em
**8** — incluindo o `ECCLES_2010` com **10 assinaturas para 10 curvas**, que só passou a ser
verdade depois de a carga axial entrar no registry (`53996b7`). ⇒ **plumbar a variável
varrida converte um bloqueio manual em fonte tratável automaticamente**, e é essa a rota.

Varrendo o registry INTEIRO (não só as bloqueadas), **57 curvas em 11 fontes** colidem.
Delas, **9 fontes são TICKET de input faltante** — e a variável está **nomeada no próprio
`case_id`**, o que significa que alguém já a leu do paper e ela se perdeu no caminho até o
`ValidationCase`. As outras **2 são LEGÍTIMAS**: estágios de uma cadeia de reaperto
(`LIU_2022_RETIGHT`) e o mesmo teste publicado em duas figuras (`LU_2024`).

⚠️ Separar as duas classes é o que torna a guarda utilizável. Uma regra que só bloqueasse
chamaria as 17 curvas de reaperto de defeito, e seria descartada na primeira semana.
"""

from __future__ import annotations

import collections

import pytest

from bolt_analysis_studio.validation.case_registry import all_records, record

# Campos que HOJE compõem a assinatura de input. Acrescentar campo aqui é o que
# resolve uma colisão — não remover a curva da lista abaixo.
_CAMPOS = (
    "transverse_displacement_mm",
    "initial_preload_N",
    "frequency_Hz",
    "n_cycles",
    "external_axial_N",      # entrou em 53996b7 e resolveu o ECCLES_2010 inteiro
    "external_axial_mode",
    # VARREDURAS POR CURVA (2026-08-23): a fonte varre a variavel, o `case_id` a
    # nomeia, e ela nao chegava ao `ValidationCase`. Sem estes campos a assinatura
    # e' cega ao que distingue as curvas -- e a guarda mediria a divida ANTIGA,
    # que e' o modo de falha (A) do gotcha das quatro portas: instrumento lido
    # fora do dominio. Lidos em `_varredura_por_curva`.
    "axial_force_amplitude_N",
    "roughness_Ra_um",
    "grip_length_mm",
    "member_thickness_mm",
    "reassembly_count",
    "specimen_label",
    "bolt_diameter_mm",
    "pitch_mm",
    "mu_initial",
    "lubricated",
)

# ⚠️ BASELINE DECLARADO, não perdão — medido sobre o registry INTEIRO em 2026-08-23 (57 curvas,
# 11 fontes). A 1a versao deste dict foi montada medindo SO' as curvas de
# `_SEM_FAMILIA_MECANICA` e errou 3 numeros — populacao errada, o mesmo modo de
# falha que este projeto ja documentou em quatro escalas. O teste pegou.
#
# Duas CLASSES, e separa-las e' o que torna a guarda honesta:
#
#   (T) TICKET DE INPUT FALTANTE — a variavel que o paper varre nao esta no
#       `ValidationCase`. O `case_id` normalmente a NOMEIA, o que significa que
#       alguem ja a leu do paper e ela se perdeu no caminho. Reduzir e' trabalho.
#   (L) LEGITIMA — os inputs SAO iguais porque as condicoes sao as mesmas. Nao ha
#       o que consertar; a distincao vive noutro lugar (cadeia, figura).
_COLISOES_CONHECIDAS = {
    # (L) REPLICA DE VERDADE, e por isso ficou: `tapered_45kN_rep1`x`rep2` sao as
    # DUAS replicas da MESMA condicao -- o par declarado que mede o piso do D-I
    # (|rep1-rep2| = 0,0382). Aqui a assinatura identica e' a VERDADE do dado, e a
    # guarda apontando so' este par (5 -> 2) e' a prova de que ela separa replica
    # de variavel varrida. Resolveu as outras 3: `specimen_label`
    # (tapered/protruding/compblock/retighten = GEOMETRIA e PROTOCOLO).
    "CACCESE_2009": 2,
    # (L) LEGITIMA: t0/t1/t2/t3 sao ESTAGIOS do MESMO ensaio numa cadeia de
    # reaperto. Inputs iguais e' CORRETO -- quem distingue e' a cadeia
    # (`chain: "retight"`, F0 por estagio lido do 1o ponto do dado), nao um campo
    # de condicao. Nada a consertar.
    "LIU_2022_RETIGHT": 17,
    # (L) LEGITIMA: `fig18_amp1p0` e `fig20_T22Nm` sao o MESMO teste publicado em
    # DUAS figuras (Tabela 8@1,0mm == Tabela 9@22N.m ao digito), ja registrado
    # como `_CID_NAO_COMPARAVEL`. Assinatura identica e' a verdade do dado.
    "LU_2024": 2,
}

# ⚠️ OS 9 TICKETS FORAM PAGOS EM 2026-08-23 — 57 colisoes -> 21, e as 21 que
# restam sao as tres entradas (L) acima. Quem resolveu, por campo:
#
#   `axial_force_amplitude_N`  LIU_2016 8->3 ; LIU_2017_AXIAL 5->0   (af7p5..12p5kn)
#   `roughness_Ra_um`          LI_2022_MARSTRUC 4->0                 (Ra0p078..0p8)
#   `grip_length_mm`           ICMEZ_2025 4->0                       (lk13p8/lk19p8)
#   `member_thickness_mm`      ROUSSEAU_2025 2->0                    (t10/t12/t14)
#   `reassembly_count`         SUN_2025_REASSY 3->0                  (reassy02..10)
#   `specimen_label`           JCSR_2023 5->0 ; CACCESE 5->2 ; GRZEJDA 2->0 ;
#                              LIU_2016 (fig13a_dry/mos2, fig9a_m*nm) 3->0
#
# Todos LIDOS DO `case_id` em `_varredura_por_curva` (validation_cases.py) -- ou
# seja, do nome que alguem escreveu ao digitalizar o paper. O valor nunca esteve
# perdido; estava fora do dataclass.
#
# ⚠️ DOIS ACHADOS que so' apareceram porque a guarda NOMEIA as curvas que colidem:
#
# 1. `af8p75kn` tem DOIS digitos depois do `p`, e com `(?:p(\d))?` o casamento
#    INTEIRO falha (o `kn` nao encaixa) => campo 0.0 EM SILENCIO. Um parser
#    generico teria lido 8,7 e ninguem veria. A guarda listou o par 8,75/11,25 kN
#    ainda colidindo, e o defeito estava no nome.
# 2. Nenhum consumidor a jusante le estes 6 campos hoje: eles servem a DETECCAO DE
#    REPLICA. Isso e' DE PROPOSITO -- usa-los na fisica e' passo separado e gateado
#    (foi assim com `external_axial_N`, cuja camada C3 acabou FALSIFICADA). O
#    invariante de inercia esta em `test_os_campos_novos_sao_INERTES_na_fisica`.


def _assinaturas():
    """{fonte: {assinatura: [case_ids]}} sobre TODAS as curvas do registry."""
    por_fonte = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in all_records():
        vc = r.validation_case
        sig = tuple(
            (round(float(v), 9) if isinstance(v, (int, float)) and not isinstance(v, bool)
             else v)
            for v in (getattr(vc, c, None) for c in _CAMPOS))
        por_fonte[r.source][sig].append(r.case_id)
    return por_fonte


def test_nenhuma_fonte_NOVA_confunde_variavel_varrida_com_replica():
    """Colisão em fonte fora do baseline = variável varrida entrando como réplica."""
    novas = {}
    for fonte, grupos in _assinaturas().items():
        colidem = sum(len(v) for v in grupos.values() if len(v) > 1)
        if colidem and fonte not in _COLISOES_CONHECIDAS:
            exemplo = next(v for v in grupos.values() if len(v) > 1)
            novas[fonte] = (colidem, exemplo[:4])
    assert not novas, (
        "FONTE NOVA com curvas de assinatura de input IDÊNTICA:\n  "
        + "\n  ".join(f"{f}: {n} curvas, ex. {ex}" for f, (n, ex) in novas.items())
        + "\n\nOu são réplicas de verdade (declare o par), ou FALTA UM INPUT — e o "
          "`case_id` normalmente nomeia qual. Tratar variável varrida como réplica "
          "já retratou exceções 7 vezes; ver o docstring deste arquivo.")


@pytest.mark.parametrize("fonte,esperado", sorted(_COLISOES_CONHECIDAS.items()))
def test_colisao_conhecida_nao_CRESCE(fonte, esperado):
    """A dívida pode encolher (input novo) mas não crescer em silêncio."""
    grupos = _assinaturas().get(fonte, {})
    atual = sum(len(v) for v in grupos.values() if len(v) > 1)
    assert atual <= esperado, (
        f"{fonte}: colisões {esperado} -> {atual}. Curva nova entrou sem o input "
        f"que a distingue das existentes.")
    if atual < esperado:
        pytest.fail(
            f"{fonte}: colisões CAÍRAM de {esperado} para {atual} — provavelmente um "
            f"input novo entrou no registry. Atualize `_COLISOES_CONHECIDAS` para "
            f"{atual} (ou remova a entrada se chegou a 0) e registre qual campo "
            f"resolveu, no idioma do `external_axial_N` do ECCLES.")


def test_o_ECCLES_e_a_PROVA_DE_CONCEITO_e_segue_resolvido():
    """10 curvas, 10 assinaturas — e só depois de a carga axial entrar.

    Este caso é o argumento do arquivo: até 2026-08-21 as 10 curvas do `ECCLES_2010`
    tinham `to_solver_config()` IDÊNTICO, e nenhuma regra automática poderia
    distingui-las. Plumbar a variável que o paper varre (`53996b7`) resolveu a fonte
    inteira. Se este teste falhar, o input axial regrediu — e com ele a base para
    trocar o bloqueio manual por regra derivada.
    """
    grupos = _assinaturas().get("ECCLES_2010", {})
    total = sum(len(v) for v in grupos.values())
    colidem = {k: v for k, v in grupos.items() if len(v) > 1}
    assert total == 10, f"o ECCLES_2010 tem {total} curvas, esperava 10"
    assert not colidem, (
        f"o ECCLES_2010 voltou a colidir: {list(colidem.values())} — a carga axial "
        "externa saiu do registry?")


def test_a_lista_manual_e_MAIOR_que_o_necessario_e_isso_esta_medido():
    """Das fontes bloqueadas à mão, quantas os inputs já resolvem?

    Não falha por isso — mede. O bloqueio manual do `ECCLES` estava *certo em
    espécie e largo demais em escopo*: proibia também o par legítimo
    `fig8a`×`fig8c`. Este teste imprime o tamanho do excesso, para que a troca da
    lista pela regra seja decidida com número.
    """
    import bolt_analysis_studio.validation.report_html as rh
    bloq = {r.source for r in all_records()
            if r.case_id in getattr(rh, "_SEM_FAMILIA_MECANICA", ())}
    assin = _assinaturas()
    resolvidas = [f for f in bloq
                  if not any(len(v) > 1 for v in assin.get(f, {}).values())]
    # invariante frouxo de propósito: o que importa é que a medida exista e que
    # o ECCLES esteja entre as resolvidas (a prova de conceito).
    assert "ECCLES_2010" in resolvidas, (
        f"o ECCLES devia estar entre as fontes que os inputs já resolvem; "
        f"resolvidas={sorted(resolvidas)}")
    # CATRACA: o piso era 6 quando só o axial do ECCLES estava plumbado. Com os 6
    # campos de varredura são **12 de 14** (medido 2026-08-23), e travar o número
    # é o que impede o encanamento de regredir em silêncio — exatamente o modo de
    # falha que o `test_meta_numeros_nao_envelhecem` guarda do lado do censo.
    # Se cair, um input saiu do registry ou um regex parou de casar (e o `\b`
    # virando 0x08 já provou que isso acontece SEM erro nenhum).
    assert len(resolvidas) >= 12, (
        f"só {len(resolvidas)} das {len(bloq)} fontes bloqueadas são resolvidas "
        f"pelos inputs — era 12 de 14 em 2026-08-23. Um input saiu do registry, ou "
        f"um padrão de `_varredura_por_curva` deixou de casar. Resolvidas hoje: "
        f"{sorted(resolvidas)}")


# --------------------------------------------------------------------------- #
# Os campos novos: valores CERTOS e fisica INERTE                             #
# --------------------------------------------------------------------------- #

# ⚠️ Por que este bloco existe: a guarda de colisao so' exige que as assinaturas
# DIFIRAM. Um regex que lesse `t10` como 1,0 mm em vez de 10 mm a satisfaria
# perfeitamente -- valores distintos, todos errados. Distincao != correcao, e ler
# valor de NOME DE ARQUIVO e' precisamente onde a diferenca morde.
_VALORES_ESPERADOS = [
    # (case_id, campo, valor) -- lidos do `case_id`, conferidos contra o paper
    ("liu2016wear_fig11a_af7p5kn", "axial_force_amplitude_N", 7500.0),
    ("liu2016wear_fig11a_af8p75kn", "axial_force_amplitude_N", 8750.0),   # 2 digitos
    ("liu2016wear_fig11a_af11p25kn", "axial_force_amplitude_N", 11250.0),  # 2 digitos
    ("liu2017_axial_AF_12p5kN", "axial_force_amplitude_N", 12500.0),
    ("li2022marstruc_creep_10kN_Ra0p078_min", "roughness_Ra_um", 0.078),
    ("li2022marstruc_creep_10kN_Ra0p8_min", "roughness_Ra_um", 0.8),
    ("rousseau2025_steel_t10", "member_thickness_mm", 10.0),
    ("rousseau2025_hdpe_t14", "member_thickness_mm", 14.0),
    ("jcsr2023_stainless_seawater", "specimen_label", "stainless_seawater"),
]


@pytest.mark.parametrize("case_id,campo,esperado", _VALORES_ESPERADOS)
def test_o_valor_lido_do_case_id_e_o_do_PAPER(case_id, campo, esperado):
    """Ordem de grandeza e decimal, não só distinção.

    Os dois `af*p**kn` de dois dígitos estão aqui porque foram exatamente eles que
    o primeiro regex leu errado — e o casamento inteiro falhava, deixando **0.0 em
    silêncio**, com as duas curvas voltando a colidir.
    """
    vc = record(case_id).validation_case
    obtido = getattr(vc, campo)
    if isinstance(esperado, float):
        assert abs(obtido - esperado) < 1e-9, f"{case_id}.{campo} = {obtido}, esperava {esperado}"
    else:
        assert obtido == esperado, f"{case_id}.{campo} = {obtido!r}, esperava {esperado!r}"


def test_o_grip_do_ICMEZ_confere_com_a_FONTE_INDEPENDENTE():
    """Cross-check do parser contra `inputs_for`, que leu o grip do paper.

    ⚠️ Este é o único dos 6 campos com segunda fonte no repo, e por isso é o mais
    valioso: ele testa o *parser*, não a si mesmo. Se o `lk19p8` do nome e o
    `grip_mm` da nota de aparato divergirem, um dos dois está errado — e a guarda
    de colisão jamais notaria, porque valores errados também são distintos.
    """
    from bolt_analysis_studio.validation.runner import inputs_for
    vistos = 0
    for r in all_records():
        if r.source != "ICMEZ_2025":
            continue
        lido = float(r.validation_case.grip_length_mm)
        if lido <= 0.0:
            continue
        ref = inputs_for(r.validation_case).get("grip_mm")
        if ref is None:
            continue
        # `inputs_for` devolve {"value": x, "prov": "..."} — a PROCEDÊNCIA viaja
        # com o número, e é ela que torna este cross-check legítimo: não comparo
        # meu parser contra outro palpite, comparo contra valor rotulado como
        # LIDO DO PAPER. Se o rótulo mudar para fitado, o teste deixa de valer.
        assert ref.get("prov") == "paper", (
            f"{r.case_id}: grip_mm com procedência {ref.get('prov')!r}, não 'paper' — "
            "deixou de ser fonte independente para conferir o parser")
        assert abs(lido - float(ref["value"])) < 0.05, (
            f"{r.case_id}: grip {lido} do case_id x {ref['value']} do inputs_for")
        vistos += 1
    assert vistos >= 4, f"esperava >=4 curvas do ICMEZ com grip conferível, vi {vistos}"


def test_os_campos_novos_sao_INERTES_na_fisica():
    """Nada a jusante os lê — e isso é DE PROPÓSITO.

    Eles servem à **detecção de réplica**. Levá-los à física é passo separado e
    gateado: foi assim com o `external_axial_N`, cuja camada C3 (piso anulável)
    acabou **falsificada** pela monotonia piso-vs-axial. Um campo que entra no
    registry e na física no mesmo commit não tem como ser falsificado em separado.

    O teste é estrutural: `material_kwargs_for` filtra por `JointMaterial`, então
    basta que nenhum dos 6 nomes seja campo do dataclass — se um dia alguém quiser
    usá-los, o VarSpec obrigatório do explorador força a documentação primeiro.
    """
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    campos_material = set(JointMaterial.__dataclass_fields__)
    novos = {"axial_force_amplitude_N", "roughness_Ra_um", "grip_length_mm",
             "member_thickness_mm", "reassembly_count", "specimen_label"}
    vazam = novos & campos_material
    assert not vazam, (
        f"{sorted(vazam)} virou campo de JointMaterial — a física passou a ler o que "
        "existe para detectar réplica. Se é intencional, é adoção gateada: prereg, "
        "VarSpec no explorador e medição de Delta em todas as curvas da fonte.")


def test_o_que_NAO_casa_fica_em_zero_e_isso_e_afirmacao():
    """Curva sem variável varrida tem os 6 campos no default — não `None`.

    Zero/"" aqui significa **"não se aplica"**, e é o que permite comparar
    assinaturas sem tratar ausência como valor. `None` misturado com 0.0 faria duas
    curvas idênticas colidirem ou não conforme a ordem de leitura do CSV.
    """
    vc = record("bauer2024_M8_fig6_rep1").validation_case
    assert vc.axial_force_amplitude_N == 0.0
    assert vc.roughness_Ra_um == 0.0
    assert vc.grip_length_mm == 0.0
    assert vc.member_thickness_mm == 0.0
    assert vc.reassembly_count == 0
    assert vc.specimen_label == ""
