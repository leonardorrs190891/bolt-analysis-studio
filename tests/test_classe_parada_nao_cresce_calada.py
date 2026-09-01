# -*- coding: utf-8 -*-
"""Invariante: a classe ENCERRADA nao ganha membro em silencio.

## Por que so' esta camada

A triagem tem 8 camadas de estatuto e a maioria se move a cada adocao — guardar
todas seria ruido. A `classe_parada (aceleracao tardia)` e' diferente por
CONSTRUCAO: ela declara uma classe **encerrada pela regra de parada** ("as curvas
estao erradas, nos sabemos, e paramos de trabalha-las"). Curva estacionada ali
**nao volta a ser olhada**. Crescer sem aviso e' exatamente o defeito.

## O defeito MEDIDO que motivou este arquivo (2026-08-14)

Depois do bloqueio dos pisos ilegitimos (G+H, commit `2335090`) a camada foi
**8 -> 9**, e o membro novo — `chu2026ti_D1p0mm_F0_49kN_test5` — entrou por
**pertencer a fonte**, nao por ter o defeito: o `classificar` roteia por
`_FONTES_CLASSE_PARADA`, que e' uma lista de FONTES, entao qualquer curva de uma
delas que passe a falhar herda o rotulo. A `test5` passou a falhar porque o
LIMITE apertou (0,0507 -> 0,0296) quando o piso falso caiu; o sigma dela sempre
foi 0,0436.

E a medicao mostrou que o rotulo nao descreve o caso: a `test5` tem a MESMA
assinatura de residuo da sua propria replica (`test6_repeat`, rho +0,86 contra
+0,94) — e a replica **PASSA**. A diferenca e' de MAGNITUDE (sigma 0,0436 x
0,0285), nao de especie. Detalhe: `New_Theory/classe_parada_atribui_por_fonte.md`.

## O que este teste faz, e o que NAO faz

FAZ: congela a composicao e **falha quando ela muda**, nomeando quem entrou e
quem saiu. Entrada nova exige decidir se a curva **tem** o defeito da classe ou
so' caiu na fonte errada.

NAO FAZ: mover curva, mudar estatuto ou tocar o censo. Reclassificacao e'
proposta e proposta se assina. Este arquivo so' torna a mudanca **audivel**.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Composicao medida em 2026-08-14, store `cb019d75c6c2`, censo 140/205.
# ⚠️ A `chu...test5` esta AQUI e o registro diz por que isso e' suspeito — ela
# entrou por fonte, nao por defeito. Mante-la declarada (em vez de excluida) e'
# deliberado: a decisao de move-la exige assinatura, e enquanto isso a lista tem
# de refletir a REALIDADE, nao a preferencia de quem a escreveu.
# ✅ A `chu2026ti_D1p0mm_F0_49kN_test5` SAIU em 2026-08-14 ~15:50 — e a saida
# VINDICA o motivo pelo qual ela estava marcada como suspeita aqui.
#
# Ela entrou na camada em 12:45 por PERTENCER A FONTE (o classificador roteia por
# _FONTES_CLASSE_PARADA), nao por ter o defeito da classe; e a medicao mostrou que
# tinha a MESMA assinatura de residuo da propria replica (`test6_repeat`, que
# PASSA). O registro dizia: "e' o pior lado de um par de replicas cujo lado bom
# passa", nao membro de classe encerrada.
#
# Em 15:50 ela FECHOU O TRIPE com 2 constantes de assentamento (prereg
# 2026-08-14-chu-test5-embedding): 0,0402/0,0880/0,0436 -> 0,0208/0,0395/0,0183.
# ⇒ curva de classe GENUINAMENTE ENCERRADA nao se resolve com um par nivel/forma
# do embedding. O rotulo estava errado, e a correcao provou.
#
# ⚠️ Licao que fica para a proxima entrada: quando uma curva entrar aqui por
# mudanca de LIMITE (correcao de piso) e nao por defeito, ela e' candidata a ter
# rota — e nao deveria ser estacionada.
# ✅ SAÍRAM DUAS EM 2026-08-15 — `liu2025_M16_amp0p25` e `liu2025_M16_amp0p3`,
# pela adoção **D-AD** (`s1_amp_gate` no `LIU_2025`, commit 42568f4). Hoje passam
# o tripé com folga: 0,72x/0,49x/0,53x e 0,72x/0,51x/0,73x das respectivas pernas.
#
# ⚠️ É a SEGUNDA vez que a mesma lição se repete — e agora ela pesa mais que na
# primeira. A `chu test5` (acima) saiu com 2 constantes de assentamento; estas
# duas saíram com **UM** número de gate de amplitude. Somando: **três** curvas
# de uma classe declarada ENCERRADA foram resolvidas, duas delas por uma forma
# que já estava no engine, default-inerte.
#
# ⇒ o rótulo "aceleração tardia" descreve a FONTE, não a curva (o classificador
# roteia por `_FONTES_CLASSE_PARADA`), e cada saída dessas mostra que o
# roteamento por fonte estaciona curva com rota. Medição que quantifica isso:
# `New_Theory/classe_parada_reauditada_pos_DAD.md` — das 6 que restam, **2 não
# têm a assinatura da classe** e uma fonte inteira (`YANG_2019`) é falso
# positivo. Proposta N′ na mesa.
# ⛔ SAIU EM 2026-08-15 (item N-linha, prereg
# 2026-08-15-nlinha-yang2019-fora-da-classe-parada, assinado 21:42):
# `yang2019_M10_amp0p4_5Hz` — a fonte YANG_2019 foi REMOVIDA de
# `_FONTES_CLASSE_PARADA` por ser falso positivo INTEIRO (1 membro, 0 com a
# assinatura da classe: rho +0,39 e razao terminal 0,70, INVERTIDA — o erro se
# forma CEDO, oposto de "aceleracao tardia"). Mesmo padrao e mesmo
# discriminante da P-7, que tirou LU_2024 e SUN_2025_CRIMP.
#
# ⚠️ NAO saiu por merito: a curva NAO fechou o tripe. Ela migrou para
# `indecidivel_sem_piso` (o YANG_2019 nao tem piso medido) — troca de um
# estatuto que afirma "encerrada pela classe" por outro que afirma "nao
# julgavel, falta replica". Censo 143/205 INALTERADO; form_limited segue 0.
# ⛔ SAIU EM 2026-08-20 (item W / opção 2 da P-7, prereg
# `docs/superpowers/specs/2026-08-20-classe-parada-curva-a-curva-prereg.md`,
# assinado às 23:0x — "assinado, execute o W"): `liu2025_M16_amp0p8`, pelo MESMO
# discriminante e o MESMO padrão da P-7/N-linha, mas com uma diferença que muda o
# instrumento: aqui a fonte é **MISTA**, não falso positivo puro.
#
#   vies terminal `mean(modelo - dado)`, janelas 1/3 e 1/4:
#     liu2025_M16_amp0p8       -0.0192 / -0.0192   ESPELHADO  <- SAIU
#     liu2025_M16_fig2_single  +0.0542 / +0.0562   classe     <- FICA
#
# Remover a FONTE (opção mínima da P-7) levaria embora a `fig2_single`, que é
# membro genuíno ⇒ a exclusão teve de ser por CURVA, via
# `_FORA_DA_CLASSE_PARADA` no classificador. É a 1ª vez que a campanha desce ao
# grão da curva nesta camada.
#
# ⚠️ NÃO saiu por mérito: ela **não** fecha o tripé. Migrou para `form_limited`,
# que é o estatuto verdadeiro — uma perna violada (σ 0.0419 = 1.68×; MAE 0.79× e
# res.máx 0.86× DENTRO), sem rota F7 (piso da fonte = o global 0.0250) e com forma
# nomeada em `liu2025_par_de_taxas_opostas.md` (8 alavancas varridas, nenhuma
# fecha). Censo **166/205 INALTERADO** e bit-idêntico (G1); a fila form-limited
# volta de 0 para **1**, e isso é o ponto do item: publicar 0 lia-se como "não
# sobrou trabalho legítimo" quando havia 1 escondido por etiqueta que o
# discriminante da própria campanha reprova.
#
# ⚠️ O motivo que barrava a opção 2 — "obriga a re-derivar o critério (c)" —
# estava VENCIDO: o (c) foi FECHADO em 2026-08-14 (`regra_de_parada_proposta.md`
# §FECHO, achado a95efcc; a re-derivação "69 %/3" está explicitamente rejeitada e
# o critério fica preservado só na redação para uma fila futura com ≥2 fontes).
# Mudar a população não pode invalidar um critério que não está sendo computado.
_CLASSE_PARADA = {
    "liu2025_M16_fig2_single",
    "yang2021_amp0p5mm_ax8kN",
    "yang2021_amp0p6mm_ax8kN_r1",
    "yang2021_amp1p0mm_ax2kN",
}


@pytest.fixture(scope="module")
def composicao():
    """case_ids classificados hoje na camada, pelo classificador DA TRIAGEM."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    cam = ROOT / "New_Theory" / "regra_de_parada_triagem.py"
    spec = importlib.util.spec_from_file_location("_tri", cam)
    tri = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(tri)
    except SystemExit:      # o script tem main() com sys.exit
        pass
    rh = tri.rh
    store = json.loads(Path(tri.STORE).read_text(encoding="utf-8"))
    store = store.get("cases", store)
    recs = {r.case_id: r for r in tri.all_records()}
    pis = tri.pisos_medidos(store, recs)
    exc = set(rh._EXCECOES)

    fora = set()
    for cid, r in store.items():
        if not r.get("ok") or cid not in recs:
            continue
        src = recs[cid].source
        if not rh.caso_comparavel(src, cid):
            continue
        sd = r.get("resid_std")
        n = len(r.get("metric_data") or [])
        if sd is not None and n and n < tri.N_MIN:
            sd = None
        if sd is None and r.get("resid_std") is None:
            continue
        lim = float(rh.limite_sres(src, pis))
        if (sd is not None and r["maxerr"] <= rh.META_MAX
                and r["mae"] <= rh.META_MAE and sd <= lim):
            continue
        cls = tri.classificar(cid, r, src, tri.piso_da_fonte(pis, src), exc)
        if cls.startswith("classe_parada"):
            fora.add(cid)
    return fora


def test_classe_encerrada_nao_muda_de_composicao_calada(composicao):
    """Entrou ou saiu curva da classe ENCERRADA? Isso tem de ser audivel."""
    entraram = sorted(composicao - _CLASSE_PARADA)
    sairam = sorted(_CLASSE_PARADA - composicao)
    assert not (entraram or sairam), (
        "A CLASSE ENCERRADA mudou de composição.\n"
        f"  entraram: {entraram or '—'}\n"
        f"  saíram:   {sairam or '—'}\n"
        "⚠️ `classe_parada` significa 'paramos de trabalhar esta classe' — curva "
        "estacionada ali NÃO volta a ser olhada.\n"
        "Antes de atualizar esta lista, decida o que a entrada É: a curva tem o "
        "DEFEITO da classe, ou só caiu numa das 5 fontes de "
        "`_FONTES_CLASSE_PARADA` por outro motivo (mudança de limite, correção "
        "de piso, re-digitalização)? O classificador roteia POR FONTE e não "
        "distingue os dois — foi assim que a `chu...test5` entrou em 2026-08-14 "
        "com a assinatura de resíduo da sua própria réplica, que PASSA.\n"
        "Detalhe: `New_Theory/classe_parada_atribui_por_fonte.md`.")
