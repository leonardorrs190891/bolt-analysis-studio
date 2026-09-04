# -*- coding: utf-8 -*-
"""CATRACA DE PROCEDENCIA — impede que o passivo de constantes sem `prov` CRESCA.

Auditoria de 2026-08-12, **CORRIGIDA em 2026-08-13**: das **467** constantes em
`adopted_configs.json`, **206 (44 %) nao tem procedencia registrada** — e a maioria
delas e' campo valido de `JointMaterial`, isto e, chega ao engine e carrega peso
metrico sem justificativa registrada.

## A correcao de 2026-08-13, e por que ela importa

A 1a versao deste teste (e o documento que o gerou) publicava **238 (51 %)**. O
numero estava **inflado em 32**: o lookup era `prov.get(campo)` **exato**, e a
campanha grava **chaves COMPOSTAS** quando um unico argumento cobre varias
constantes — por exemplo `'c_bend/emb_depth/floor'` no `ROUSSEAU_HDPE`, cujo valor
e' *"PR-14 fitado-this-rig (rig + assentamento + piso de arresto)"*.

Isso nao era detalhe: o `ROUSSEAU_HDPE::loose_arrest_floor` foi levado a decisao do
professor como *"constante fitada em silencio, `prov = None`, metrica depende 2,2x
dela"* — quando a procedencia **existia desde 2026-07-12**, declarava o valor como
`fitado-this-rig` e **nomeava o piso de arresto**. A auditoria estava medindo a
rigidez do proprio lookup, nao a lacuna real.

=> este teste agora casa **tokens** da chave composta (split em `/` e `,`) mais um
mapa de ALIAS curto (floor->loose_arrest_floor, emb->emb_depth, mu->mu_thread/
mu_bearing, creep->C_creep/t_0, dano->os 4 campos de dano). Token e' mais estrito
que substring de proposito.

## O que este teste faz, e o que NAO faz

FAZ: congela o conjunto conhecido (206) e **falha se aparecer um par
`(grupo, campo)` NOVO sem `prov`**. E' catraca, no espirito do
`test_meta_numeros_nao_envelhecem` e dos registros `_EXCECOES_RETIRADAS_*`:
o estoque e' declarado, o crescimento e' proibido.

NAO FAZ: exigir backfill. Encolher o baseline e' LIVRE e bem-vindo — quem
documentar uma constante nao precisa mexer aqui. Por isso a comparacao e'
`atual - baseline`, nunca igualdade.

## Como consertar quando falhar

A mensagem nomeia o par. Duas saidas legitimas:
  1. escrever a `prov` da constante nova (o caminho certo) — e se o argumento
     cobre varias constantes, a chave COMPOSTA e' idioma aceito e reconhecido;
  2. se ela e' deliberadamente sem procedencia, ACRESCENTAR ao baseline com um
     comentario dizendo por que — o que torna a escolha visivel em vez de tacita.

Nunca a terceira: deletar o teste.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

CFG = (Path(__file__).resolve().parents[1] / "New_Theory" / "adopted_configs.json")

# Chaves que NAO sao constante fisica: inputs por curva, espectros, geometria e
# metadados de execucao. Nao entram na conta (nem no baseline).
NAO_CONSTANTE = {
    "per_case", "trim_n_max", "chain", "pack", "delta_spectrum",
    "GA_member", "d_hole_mm", "d_washer_mm",
}

# ALIAS: token curto usado nas chaves COMPOSTAS -> campo(s) que ele cobre.
# Mantido deliberadamente pequeno; so entram tokens que a campanha de fato usa.
ALIAS = {
    "loose_arrest_floor": {"floor", "arrest", "piso"},
    "emb_depth": {"emb"}, "emb_um": {"emb"}, "N_emb": {"emb"},
    "mu_thread": {"mu"}, "mu_bearing": {"mu"},
    "K_archard": {"wear"}, "k_wear_spec": {"wear"}, "k_wear_scale_tr": {"wear"},
    "C_creep": {"creep"}, "t_0": {"creep"},
    "c_D": {"dano", "damage"}, "W_ref": {"dano", "damage"},
    "k_dmg_mu": {"dano", "damage"}, "k_dmg_wear": {"dano", "damage"},
}

# BASELINE re-medido em 2026-08-13 com o lookup token-aware. 206 pares.
_SEM_PROV_BASELINE = frozenset((
    "BAUER_2024_fig6::c_bend",
    "BAUER_2024_fig6::emb_depth",
    "BAUER_2024_fig6::loose_arrest_floor",
    "BAUER_2024_fig6::slip_regime_mode",
    "BAUER_2024_fig6_rep1::c_bend",
    "BAUER_2024_fig6_rep1::emb_depth",
    "BAUER_2024_fig6_rep1::loose_arrest_floor",
    "BAUER_2024_fig6_rep1::slip_regime_mode",
    "BAUER_2024_fig6_rep2::c_bend",
    "BAUER_2024_fig6_rep2::emb_depth",
    "BAUER_2024_fig6_rep2::loose_arrest_floor",
    "BAUER_2024_fig6_rep2::slip_regime_mode",
    "BAUER_2024_fig6_rep3::c_bend",
    "BAUER_2024_fig6_rep3::emb_depth",
    "BAUER_2024_fig6_rep3::loose_arrest_floor",
    "BAUER_2024_fig6_rep3::slip_regime_mode",
    "BAUER_2024_fig6_rep4::c_bend",
    "BAUER_2024_fig6_rep4::emb_depth",
    "BAUER_2024_fig6_rep4::loose_arrest_floor",
    "BAUER_2024_fig6_rep4::slip_regime_mode",
    "BAUER_2024_fig6_rep5::c_bend",
    "BAUER_2024_fig6_rep5::emb_depth",
    "BAUER_2024_fig6_rep5::loose_arrest_floor",
    "BAUER_2024_fig6_rep5::slip_regime_mode",
    "BAUER_2024_fig6_rep6::c_bend",
    "BAUER_2024_fig6_rep6::emb_depth",
    "BAUER_2024_fig6_rep6::loose_arrest_floor",
    "BAUER_2024_fig6_rep6::slip_regime_mode",
    "BAUER_2024_fig8::s_crit_loose",
    "CACCESE_2009_12p7mm::creep_alpha_sat",
    "CACCESE_2009_12p7mm::creep_t_c",
    "CACCESE_2009_19p1mm::creep_alpha_sat",
    "CACCESE_2009_19p1mm::creep_t_c",
    "CACCESE_2009_45kN::creep_alpha_sat",
    "CACCESE_2009_45kN::creep_t_c",
    "CACCESE_2009_compblock::creep_alpha_sat",
    "CACCESE_2009_compblock::creep_t_c",
    "CHU_2026_test1::C_creep",
    "CHU_2026_test1::W_ref",
    "CHU_2026_test1::c_D",
    "CHU_2026_test1::c_bend",
    "CHU_2026_test1::emb_um",
    "CHU_2026_test1::k_dmg_mu",
    "CHU_2026_test1::mu_thread",
    "KARLSEN_2022_run2p2::C_creep",
    "KARLSEN_2022_run2p2::W_ref",
    "KARLSEN_2022_run2p2::c_D",
    "KARLSEN_2022_run2p2::c_bend",
    "KARLSEN_2022_run2p2::k_dmg_mu",
    "KARLSEN_2022_run2p2::k_dmg_wear",
    "KARLSEN_2022_run7p1::C_creep",
    "KARLSEN_2022_run7p1::W_ref",
    "KARLSEN_2022_run7p1::c_D",
    "KARLSEN_2022_run7p1::c_bend",
    "KARLSEN_2022_run7p1::k_dmg_mu",
    "KARLSEN_2022_run7p1::k_dmg_wear",
    "LIU_2016_mos2::mu_bearing",
    "LIU_2017_axial::C_creep",
    "LIU_2017_axial::N_emb",
    "LIU_2017_axial::creep_conform_exp",
    "LIU_2017_axial::emb_amp_exp",
    "LIU_2017_axial::emb_depth",
    "LIU_2017_axial::rho_ref_emb",
    "LIU_2022::W_ref",
    "LIU_2022::c_D_dry",
    "LIU_2022::c_D_oil",
    "LIU_2022::emb",
    "LIU_2022::k_dmg_mu",
    "LIU_2022::k_dmg_wear",
    "LIU_2022::k_wear_scale_tr",
    "LIU_2022::mu",
    "LIU_2022_RET::N_wear_run",
    "LIU_2022_RET::W_ref",
    "LIU_2022_RET::c_D_per_lube",
    "LIU_2022_RET::emb",
    "LIU_2022_RET::k_emb_renew",
    "LIU_2022_RET::k_gall",
    "LIU_2022_RET::k_wear_running",
    "LIU_2022_RET::k_wear_scale_tr",
    "LIU_2022_RET::mu",
    "LIU_2022_RETIGHT_direct::N_wear_run",
    "LIU_2022_RETIGHT_direct::W_ref",
    "LIU_2022_RETIGHT_direct::c_D_per_lube",
    "LIU_2022_RETIGHT_direct::emb",
    "LIU_2022_RETIGHT_direct::k_gall",
    "LIU_2022_RETIGHT_direct::k_wear_running",
    "LIU_2022_RETIGHT_direct::k_wear_scale_tr",
    "LIU_2022_RETIGHT_direct::mu",
    "LIU_2022_RETIGHT_direct::retight_loss_gain",
    "LIU_2022_RETIGHT_dry::N_wear_run",
    "LIU_2022_RETIGHT_dry::W_ref",
    "LIU_2022_RETIGHT_dry::c_D_per_lube",
    "LIU_2022_RETIGHT_dry::emb",
    "LIU_2022_RETIGHT_dry::k_emb_renew",
    "LIU_2022_RETIGHT_dry::k_gall",
    "LIU_2022_RETIGHT_dry::k_wear_running",
    "LIU_2022_RETIGHT_dry::k_wear_scale_tr",
    "LIU_2022_RETIGHT_dry::mu",
    "LIU_2022_RETIGHT_fig8::N_wear_run",
    "LIU_2022_RETIGHT_fig8::W_ref",
    "LIU_2022_RETIGHT_fig8::c_D_per_lube",
    "LIU_2022_RETIGHT_fig8::emb",
    "LIU_2022_RETIGHT_fig8::k_gall",
    "LIU_2022_RETIGHT_fig8::k_wear_running",
    "LIU_2022_RETIGHT_fig8::k_wear_scale_tr",
    "LIU_2022_RETIGHT_fig8::mu",
    "LIU_2022_RETIGHT_fig8::retight_loss_gain",
    "LIU_2025::N_emb",
    "LIU_2025::W_conf_ref",
    "LIU_2025::emb_um",
    "LIU_2025::fat_Kt",
    "LIU_2025::fat_m1",
    "LIU_2025::fat_ramp_D_on",
    "LIU_2025::fat_ramp_q",
    "LIU_2025::fat_sigma_endurance",
    "LIU_2025::fat_sigma_knee",
    "LIU_2025::fat_sigma_uts",
    "LIU_2025::fat_stress_mode",
    "LIU_2025::fatigue_enabled",
    "LIU_2025::k_ratchet",
    "LIU_2025::k_wear_scale_tr",
    "LIU_2025_amp0p4::C_creep",
    "LIU_2025_amp0p4::N_emb",
    "LIU_2025_amp0p4::W_conf_ref",
    "LIU_2025_amp0p4::c_bend",
    "LIU_2025_amp0p4::delta_free",
    "LIU_2025_amp0p4::emb_um",
    "LIU_2025_amp0p4::fat_C1",
    "LIU_2025_amp0p4::fat_Kt",
    "LIU_2025_amp0p4::fat_m1",
    "LIU_2025_amp0p4::fat_ramp_D_on",
    "LIU_2025_amp0p4::fat_ramp_q",
    "LIU_2025_amp0p4::fat_sigma_endurance",
    "LIU_2025_amp0p4::fat_sigma_knee",
    "LIU_2025_amp0p4::fat_sigma_uts",
    "LIU_2025_amp0p4::fat_stress_mode",
    "LIU_2025_amp0p4::fatigue_enabled",
    "LIU_2025_amp0p4::k_ratchet",
    "LIU_2025_amp0p4::k_wear_scale_tr",
    "LIU_2025_amp0p4::loose_arrest_floor",
    "LIU_2025_amp0p5::C_creep",
    "LIU_2025_amp0p5::N_emb",
    "LIU_2025_amp0p5::W_conf_ref",
    "LIU_2025_amp0p5::c_bend",
    "LIU_2025_amp0p5::delta_free",
    "LIU_2025_amp0p5::emb_um",
    "LIU_2025_amp0p5::fat_C1",
    "LIU_2025_amp0p5::fat_Kt",
    "LIU_2025_amp0p5::fat_m1",
    "LIU_2025_amp0p5::fat_ramp_D_on",
    "LIU_2025_amp0p5::fat_ramp_q",
    "LIU_2025_amp0p5::fat_sigma_endurance",
    "LIU_2025_amp0p5::fat_sigma_knee",
    "LIU_2025_amp0p5::fat_sigma_uts",
    "LIU_2025_amp0p5::fat_stress_mode",
    "LIU_2025_amp0p5::fatigue_enabled",
    "LIU_2025_amp0p5::k_ratchet",
    "LIU_2025_amp0p5::k_wear_scale_tr",
    "LIU_2025_amp0p5::loose_arrest_floor",
    "LI_2022_TRIBOINT::fat_stress_mode",
    "LI_2022_TRIBOINT::fatigue_enabled",
    "LU_2024::emb_um",
    "ROUSSEAU_2025::emb_um",
    "ROUSSEAU_2025::free_spin",
    "ROUSSEAU_HDPE::free_spin",
    "ROUSSEAU_HDPE::mu_bearing",
    "ROUSSEAU_HDPE::mu_thread",
    "ancora_interna::W_ref",
    "ancora_interna::c_D",
    "ancora_interna::c_bend",
    "ancora_interna::k_dmg_mu",
    "ancora_interna::k_dmg_wear",
    "ancora_interna::k_wear_scale_tr",
    "ancora_interna::loose_arrest_floor",
    "ancora_interna::W_ref",
    "ancora_interna::c_D",
    "ancora_interna::c_bend",
    "ancora_interna::k_dmg_mu",
    "ancora_interna::k_dmg_wear",
    "ancora_interna::k_wear_scale_tr",
    "ancora_interna::loose_arrest_floor",
    "ancora_interna::W_ref",
    "ancora_interna::c_D",
    "ancora_interna::c_bend",
    "ancora_interna::k_dmg_mu",
    "ancora_interna::k_dmg_wear",
    "ancora_interna::k_wear_scale_tr",
    "ancora_interna::loose_arrest_floor",
    "YANG_2019::W_ref",
    "YANG_2019::c_D",
    "YANG_2019::dmg_dwell_exp",
    "YANG_2019::emb_um",
    "YANG_2019::f_ref_dmg",
    "YANG_2019::k_dmg_mu",
    "YANG_2019::k_dmg_wear",
    "YANG_2019::slip_onset_W",
    "YANG_2019_varamp::c_D",
    "YANG_2019_varamp::dmg_dwell_exp",
    "YANG_2019_varamp::emb_um",
    "YANG_2019_varamp::f_ref_dmg",
    "YANG_2019_varamp::k_dmg_mu",
    "YANG_2019_varamp::slip_onset_W",
    "ZHANG_2006_fig16::c_bend",
    "ZHANG_2006_fig16::emb_um",
    "ZHANG_2006_fig16::kj_mode",
    "ZHANG_2019::mu_thread",
))


def _tokens(chave: str) -> set:
    """Tokens de uma chave COMPOSTA de prov (split em / e ,)."""
    return {t.strip().lower() for t in re.split(r"[/,]", chave) if t.strip()}


def _tem_prov(campo: str, prov: dict) -> bool:
    """O campo tem procedencia registrada — exata OU por chave composta?"""
    if str(prov.get(campo) or "").strip():
        return True
    alvos = {campo.lower()} | {a.lower() for a in ALIAS.get(campo, ())}
    for chave, valor in prov.items():
        if ("/" in chave or "," in chave) and str(valor or "").strip():
            if _tokens(chave) & alvos:
                return True
    return False


def _sem_prov(sources: dict) -> set:
    """Pares grupo::campo presentes em cfg e sem procedencia em prov."""
    out = set()
    for g, e in sources.items():
        cfg = e.get("cfg") or {}
        prov = e.get("prov") or {}
        for k in cfg:
            if k in NAO_CONSTANTE:
                continue
            if not _tem_prov(k, prov):
                out.add("%s::%s" % (g, k))
    return out


def test_baseline_tem_o_tamanho_declarado():
    """Guarda o proprio literal: se alguem editar o baseline sem medir, isto
    denuncia.

    192 desde 2026-09-04, RE-MEDIDO. Eram 206 ate' os tres casos de bancada
    sairem do projeto; as 14 entradas que sumiram eram constantes daqueles
    grupos, e nao divida que alguem tenha pago. A catraca so' vale se o numero
    acompanhar o corpus — deixa-lo em 206 faria o teste falhar pelo motivo
    certo com a mensagem errada.
    """
    assert len(_SEM_PROV_BASELINE) == 192, (
        "o baseline declarado tem %d entradas, e o documento publica 192 — "
        "re-meca antes de editar" % len(_SEM_PROV_BASELINE))


def test_chave_composta_conta_como_procedencia():
    """Pina a CORRECAO de 2026-08-13 contra regressao.

    O ROUSSEAU_HDPE documenta tres constantes numa chave so
    (c_bend/emb_depth/floor). Se alguem voltar ao lookup exato, este caso
    reaparece como 'sem procedencia' — e foi exatamente esse falso alarme que
    gerou uma decisao do professor sobre um problema que nao existia.
    """
    sources = json.loads(CFG.read_text(encoding="utf-8"))["sources"]
    prov = sources["ROUSSEAU_HDPE"]["prov"]
    assert any("/" in k for k in prov), (
        "o ROUSSEAU_HDPE deixou de usar chave composta — re-avalie este teste")
    assert _tem_prov("loose_arrest_floor", prov), (
        "o piso de arresto do ROUSSEAU_HDPE tem procedencia na chave composta "
        "'c_bend/emb_depth/floor'; o lookup voltou a ser exato?")
    assert "ROUSSEAU_HDPE::loose_arrest_floor" not in _SEM_PROV_BASELINE


def test_passivo_de_procedencia_nao_cresce():
    """CATRACA: nenhuma constante NOVA entra sem prov."""
    sources = json.loads(CFG.read_text(encoding="utf-8"))["sources"]
    atual = _sem_prov(sources)
    novos = sorted(atual - _SEM_PROV_BASELINE)
    assert not novos, (
        "%d constante(s) NOVA(s) adotada(s) sem entrada em prov:\n  %s\n\n"
        "Escreva a procedencia (de onde veio o numero: paper, tabela, ancora, "
        "ou 'fitado-this-rig' com o gate que a justificou). Chave COMPOSTA "
        "(a/b/c) e' idioma aceito quando o argumento cobre varias. Se a "
        "ausencia for deliberada, acrescente ao _SEM_PROV_BASELINE com o "
        "motivo — nunca apague o teste." % (len(novos), "\n  ".join(novos)))


def test_backfill_e_livre_e_visivel():
    """Encolher o passivo NAO falha. Este teste so reporta o progresso, para
    que o numero publicado no MODEL_LEGITIMACY possa ser atualizado quando
    alguem documentar constantes."""
    sources = json.loads(CFG.read_text(encoding="utf-8"))["sources"]
    atual = _sem_prov(sources)
    documentadas = sorted(_SEM_PROV_BASELINE - atual)
    total = sum(1 for g, e in sources.items() for k in (e.get("cfg") or {})
                if k not in NAO_CONSTANTE)
    assert len(_SEM_PROV_BASELINE) <= total + len(documentadas), (
        "baseline (%d) maior que o universo de constantes (%d) + documentadas "
        "(%d) — o baseline esta stale de forma incoerente"
        % (len(_SEM_PROV_BASELINE), total, len(documentadas)))
