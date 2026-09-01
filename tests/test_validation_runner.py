import numpy as np


def _short_transverse_record():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = [r for r in all_records()
            if r.family == "transverse" and r.case_class == "full_curve"]
    return min(recs, key=lambda r: r.validation_case.n_cycles)


def test_simulate_transverse_with_decomposition():
    from bolt_analysis_studio.validation.runner import simulate_case
    rec = _short_transverse_record()
    res = simulate_case(rec, n_cap=1500)
    assert res.ok and res.error is None
    assert res.mae is not None and 0.0 <= res.mae < 1.0
    assert len(res.cycles) == len(res.ratio) > 10
    # decomposicao: soma dos mecanismos == perda total (fechamento exato do engine)
    total_loss = 1.0 - res.ratio[-1]
    decomp_sum = sum(v[-1] for v in res.decomp.values())
    assert abs(decomp_sum - total_loss) < 1e-6
    assert set(res.decomp) >= {"embedding", "creep", "wear"}


def test_simulate_axial_force_mode():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import simulate_case
    rec = next(r for r in all_records() if r.family == "axial")
    res = simulate_case(rec, n_cap=1500)
    assert res.ok
    assert res.config_used["mode"] == "force"
    assert res.config_used["F_amp_N"] > 0


def test_final_ratio_case_compares_endpoint():
    # classe removida do registry (2026-07-11); a via de comparacao pontual
    # continua coberta por record sintetico (casos USER futuros podem usa-la)
    from bolt_analysis_studio.validation.case_registry import CaseRecord, all_records
    from bolt_analysis_studio.validation.runner import simulate_case
    base = next(r for r in all_records() if r.family == "transverse")
    rec = CaseRecord(case_id="sintetico_fr", name="s", source=base.source,
                     family="transverse", case_class="final_ratio", caveats=[],
                     validation_case=base.validation_case, csv_path=None,
                     apparatus_note_path=None, gallery_entry=None)
    res = simulate_case(rec, n_cap=1500)
    assert res.ok
    assert res.final_data is not None            # expected_final_preload_ratio
    assert res.mae is None                       # sem curva -> sem MAE


def test_unparameterized_loading_degrades_honestly():
    # familia 'other' removida do registry (2026-07-11) — via coberta sintetica
    from bolt_analysis_studio.validation.case_registry import CaseRecord, all_records
    from bolt_analysis_studio.validation.runner import simulate_case
    base = all_records()[0]
    rec = CaseRecord(case_id="sintetico_other", name="s", source=base.source,
                     family="other", case_class="full_curve", caveats=[],
                     validation_case=base.validation_case, csv_path=base.csv_path,
                     apparatus_note_path=None, gallery_entry=None)
    res = simulate_case(rec, n_cap=500)
    assert (not res.ok) and "proveni" in res.error


def test_material_kwargs_match_simulation_config():
    # fonte unica: os kwargs expostos sao EXATAMENTE o que simulate_case monta
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import inputs_for
    from bolt_analysis_studio.validation.runner import material_kwargs_for
    rec = record("liu2025_M16_amp0p25")
    kw = material_kwargs_for(rec, inputs_for(rec.validation_case))
    assert set(kw) <= set(JointMaterial.__dataclass_fields__)
    assert kw["emb_depth"] == 4.9999999999999996e-06     # adotada vence a VDI
    assert kw["slip_onset_W"] == 250000.0                # cfg adotada LIU_2025 (PR-9b)
    assert kw["k_tr_mode"] == "bending"                  # pack LEGACY
    JointMaterial(**kw)                                  # constroi sem erro


def test_loading_for_public_alias():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import loading_for
    rec = next(r for r in all_records() if r.family == "axial")
    load = loading_for(rec)
    assert load["mode"] == "force" and load["F_amp_N"] > 0


def test_adopted_matching_by_group_tokens():
    from bolt_analysis_studio.validation.runner import _adopted_for
    # tokens extras da chave devem aparecer no case_id (grupo por protocolo)
    got_fig6 = _adopted_for("BAUER_2024", "bauer2024_M8_fig6_rep2")
    assert got_fig6 != "BAUER_2024_fig8"
    # lk19p8 nao pode vazar p/ casos lk13p8
    got = _adopted_for("ICMEZ_2025", "demir2024_amp0p4_F17p6_lk13p8")
    assert got is None or "lk19p8" not in got
    # FRONTEIRA ESTRITA: LI_* nunca casa chave LIU_* (primos foneticos) —
    # regressao real da iteracao 1 (creep marstruc pegou cfg do LIU_2022).
    # Pode casar a PROPRIA chave (LI_2022_MARSTRUC foi promovida na iter.1).
    got_mar = _adopted_for("LI_2022_MARSTRUC",
                           "li2022marstruc_creep_5kN_Ra0p8_min")
    assert got_mar is None or got_mar.startswith("LI_2022")
    got_ti = _adopted_for("LI_2022_TRIBOINT", "li2022ti_axialmin_10Hz")
    assert got_ti is None or got_ti.startswith("LI_2022")
    # prefixos legitimos continuam: chave prefixo da fonte (RET<-RETIGHT)
    assert _adopted_for("LIU_2022_RETIGHT", "liu2022_fig9_x") == "LIU_2022_RET"


def test_adopted_matching_by_bolt_size(monkeypatch):
    # PR-8: grupos por tamanho de parafuso (YANG_2023_IJPEM_m6/_m8) casam via
    # bolt_size quando o stem nao carrega o tamanho. Backward-compat: sem o
    # argumento bolt, grupos _m6/_m8 nao casam.
    from bolt_analysis_studio.validation import runner
    real = runner.kb.adopted_sources
    monkeypatch.setattr(runner.kb, "adopted_sources",
                        lambda: list(real()) + ["YANG_2023_IJPEM_m6",
                                                "YANG_2023_IJPEM_m8"])
    got_m6 = runner._adopted_for("YANG_2023_IJPEM",
                                 "10_yang_2023_phenomenological_model__0_50_mm__9",
                                 bolt="M6x1.0")
    got_m8 = runner._adopted_for("YANG_2023_IJPEM",
                                 "10_yang_2023_phenomenological_model__0_65_mm__6",
                                 bolt="M8x1.25")
    assert got_m6 == "YANG_2023_IJPEM_m6"
    assert got_m8 == "YANG_2023_IJPEM_m8"
    # sem bolt: cai no grupo base (tokens m6/m8 nao aparecem no stem)
    assert runner._adopted_for(
        "YANG_2023_IJPEM",
        "10_yang_2023_phenomenological_model__0_65_mm__6") == "YANG_2023_IJPEM"


def test_fat_stress_mode_bending_dn_curve():
    # PR-24: fat_stress_mode="bending" => tensao de fadiga ~E*d*delta/L^2 (flexao
    # do parafuso); N_D (=1/dD por ciclo) DECRESCE com a amplitude = D-N. Modo
    # "axial" (default) usa Kt*F_amp/A_s. fatigue_enabled=False => inerte.
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        FatigueLoss, JointGeometry, JointMaterial, SlowState)
    geom = JointGeometry(A_s=157e-6, L_eff=0.04, d_2=14.7e-3, pitch=2e-3,
                         r_bearing=12e-3, A_contact=200e-6)
    st = SlowState(F_0=60e3, F_0_init=60e3)
    fl = FatigueLoss()

    def n_d(delta, mode, enabled=True):
        mat = JointMaterial(fatigue_enabled=enabled, fat_stress_mode=mode,
                            fat_C1=6.7e30, fat_m1=2.7, fat_sigma_knee=1.0)
        r = fl.rate(st, geom, mat, 24e3, 1.5708, 12.5, 1,
                    slip_amp_override=0.1e-3, delta_amp=delta)
        dD = r["ds"].get("D_fatigue", 0.0)
        return (1.0 / dD) if dD > 0 else float("inf")

    n4, n8 = n_d(0.4e-3, "bending"), n_d(0.8e-3, "bending")
    assert n8 < n4                                    # maior amplitude => fratura antes (D-N)
    assert 3e4 < n4 < 2e5                              # ~76k (calibrado a Liu2025)
    # axial (default) ignora delta => N_D diferente (usa F_amp)
    assert n_d(0.4e-3, "axial") != n4
    # fatigue_enabled=False => inerte (sem dano)
    assert n_d(0.4e-3, "bending", enabled=False) == float("inf")


def test_loose_amp_exp_bit_identical_and_steeper():
    # PR-21: loose_amp_exp=1.0 => ratchet LINEAR (bit-identical); >1 => resposta
    # de amplitude mais ingreme (menos loosening a baixa amplitude, mais a alta).
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)
    geom = JointGeometry(A_s=157e-6, L_eff=0.04, d_2=14.7e-3, pitch=2e-3,
                         r_bearing=12e-3, A_contact=200e-6)
    def final(exp, delta):
        mat = JointMaterial(mu_thread=0.15, mu_bearing=0.15, k_ratchet=0.02,
                            loose_amp_exp=exp)
        ana = DynamicStiffnessAnalyzer(geom, mat, 50e3)
        for _ in range(200):
            ana.step_cycle(20e3, 1.5708, 1.0, delta_amp=delta)
        return ana.state.F_0 / 50e3
    # exp=1.0 bit-identical vs baseline sem o campo (default e' 1.0)
    base = final(1.0, 0.5e-3)
    matb = JointMaterial(mu_thread=0.15, mu_bearing=0.15, k_ratchet=0.02)
    anab = DynamicStiffnessAnalyzer(geom, matb, 50e3)
    for _ in range(200):
        anab.step_cycle(20e3, 1.5708, 1.0, delta_amp=0.5e-3)
    assert abs(base - anab.state.F_0 / 50e3) < 1e-12       # default 1.0 = bit-identical
    # exp>1 => a ALTA amplitude afrouxa MAIS (final menor) que exp=1
    assert final(3.0, 0.8e-3) <= final(1.0, 0.8e-3) + 1e-9


def test_delta_amp_override_per_thickness(monkeypatch):
    # PR-14: cfg adotado com delta_amp_mm (escalar OU dict por token t) sobrepoe
    # a amplitude do caso. Default-inerte: sem a chave, usa case.transverse_*.
    from bolt_analysis_studio.validation import runner
    from bolt_analysis_studio.validation.case_registry import record
    real = runner.kb.adopted_config

    def with_amp(key):
        e = dict(real(key) or {})
        e["cfg"] = dict(e.get("cfg", {}),
                        delta_amp_mm={"t10": 0.5, "t12": 0.49, "t14": 0.38})
        return e

    monkeypatch.setattr(runner.kb, "adopted_config", with_amp)
    rec14 = record("rousseau2025_hdpe_t14")
    load = runner._loading_for(rec14)
    assert abs(load["delta_mm"] - 0.38) < 1e-9        # t14 -> 0.38 (paper Tabela 2)
    rec10 = record("rousseau2025_hdpe_t10")
    assert abs(runner._loading_for(rec10)["delta_mm"] - 0.5) < 1e-9


def test_delta_spectrum_cycles_pattern(monkeypatch):
    # PR-12: cfg adotado com delta_spectrum [[n1,d1],[n2,d2]] cicla o padrao
    # de amplitude por ciclo (blocos do paper Bauer fig8: 18x80um + 2x155um).
    # Default-inerte: sem a chave, delta constante (bit-identico).
    from bolt_analysis_studio.validation import runner
    pat = [[18, 8.0e-5], [2, 1.55e-4]]
    seq = runner._spectrum_delta_seq(pat, 40)
    assert len(seq) == 40
    assert seq[0] == 8.0e-5 and seq[17] == 8.0e-5      # base
    assert seq[18] == 1.55e-4 and seq[19] == 1.55e-4   # picos
    assert seq[20] == 8.0e-5 and seq[38] == 1.55e-4    # padrao cicla
    assert runner._spectrum_delta_seq(None, 5) is None  # inerte sem chave
    # caminho cfg CRU -> overrides: a LISTA sobrevive (regressao PR-12d:
    # suggest_overrides so passa escalares => espectro era descartado)
    real = runner.kb.adopted_config

    def with_spec(key):
        entry = dict(real(key) or {})
        entry["cfg"] = dict(entry.get("cfg", {}), delta_spectrum=pat)
        return entry

    monkeypatch.setattr(runner.kb, "adopted_config", with_spec)
    out = runner._adopted_overrides("BAUER_2024", {}, "bauer2024_M12_fig8_test2",
                                    bolt="M12x1.5")
    assert out.get("delta_spectrum") == pat


def test_ga_member_translated_per_thickness(monkeypatch):
    # PR-10: cfg adotado com GA_member [N] vira k_member_shear = GA/t_member
    # por caso, t_member lido do token t(\d+) do stem (mm). Default-inerte:
    # sem GA_member no cfg, nada muda; sem token t no stem, descarta (honesto).
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    from bolt_analysis_studio.validation import runner
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import inputs_for
    real = runner.kb.suggest_overrides

    def with_ga(key):
        cfg = dict(real(key) or {})
        cfg["GA_member"] = 1.2e5
        return cfg

    # LIDO DO CFG CRU (adopted_config), nao de suggest_overrides (que descarta
    # GA_member por estar no _NON_ENGINE — bug do PR-10, corrigido no PR-14)
    real = runner.kb.adopted_config

    def with_ga(key):
        e = dict(real(key) or {})
        e["cfg"] = dict(e.get("cfg", {}), GA_member=1.2e5)
        return e

    monkeypatch.setattr(runner.kb, "adopted_config", with_ga)
    rec10 = record("rousseau2025_hdpe_t10")
    rec14 = record("rousseau2025_hdpe_t14")
    kw10 = runner.material_kwargs_for(rec10, inputs_for(rec10.validation_case))
    kw14 = runner.material_kwargs_for(rec14, inputs_for(rec14.validation_case))
    assert abs(kw10["k_member_shear"] - 1.2e5 / 0.010) < 1e-6   # t10 -> 10 mm
    assert abs(kw14["k_member_shear"] - 1.2e5 / 0.014) < 1e-6   # t14 -> 14 mm
    assert "GA_member" not in kw10                          # nao e campo do engine
    JointMaterial(**kw10)                                   # constroi sem erro


def test_arrest_approach_exp_inert_at_default():
    # G1 do prereg grupo A (2026-07-27): com o default 1.0 o gate devolve a
    # expressao anterior BIT-IDENTICA. Garantido por early-return explicito, nao
    # por confiar em pow(x, 1.0) == x do libm — o gate exige zero diferenca.
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial, SlowState, self_locking_gate)

    for f0_init, f0, floor in [(50000.0, 40000.0, 0.10), (1e5, 1.5e4, 0.09),
                               (4000.0, 500.0, 0.20), (7e4, 6.9e4, 0.05)]:
        st = SlowState(F_0=f0)
        st.F_0_init = f0_init
        mat = JointMaterial(loose_arrest_floor=floor)
        assert mat.arrest_approach_exp == 1.0            # default inerte
        esperado = max(0.0, 1.0 - floor * f0_init / f0)
        assert self_locking_gate(st, mat) == esperado    # igualdade EXATA


def test_arrest_approach_exp_decelerates_toward_floor():
    # exp>1 tem de (a) reduzir o gate em todo ponto acima do piso e (b) reduzi-lo
    # PROPORCIONALMENTE MAIS perto do piso — que e' o que significa "desacelerar
    # na aproximacao" e o que distingue a forma de um ganho global constante.
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial, SlowState, self_locking_gate)

    f0_init, floor = 50000.0, 0.20
    base = JointMaterial(loose_arrest_floor=floor)
    steep = JointMaterial(loose_arrest_floor=floor, arrest_approach_exp=2.5)

    razoes = []
    for f0 in (45000.0, 30000.0, 15000.0, 11000.0):      # do longe ao perto
        st = SlowState(F_0=f0)
        st.F_0_init = f0_init
        g1, g2 = self_locking_gate(st, base), self_locking_gate(st, steep)
        assert 0.0 <= g2 < g1                            # (a) sempre reduz
        razoes.append(g2 / g1)
    # (b) a razao encolhe monotonicamente conforme F_0 se aproxima do piso
    assert all(b < a for a, b in zip(razoes, razoes[1:])), razoes

    # o piso continua ponto fixo: gate = 0 exatamente nele
    st = SlowState(F_0=floor * f0_init)
    st.F_0_init = f0_init
    assert self_locking_gate(st, steep) == 0.0


def test_k_member_shear_visible_in_config_used():
    # G0 do prereg Rousseau (2026-07-27): o `config_used` gravado no store TEM
    # de mostrar o que o engine recebeu. Antes nao mostrava — `simulate_case`
    # montava sua propria copia dos overrides e a injecao GA_member ->
    # k_member_shear so acontecia dentro de `material_kwargs_for`, entao uma
    # constante ATIVA e fitada-this-rig ficava invisivel na auditoria. Foi
    # assim que o "INERTE no pack CM" do PR-10 sobreviveu por 16 dias.
    from bolt_analysis_studio.validation import runner
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import inputs_for

    rec = record("rousseau2025_hdpe_t12")
    kw = runner.material_kwargs_for(rec, inputs_for(rec.validation_case))
    res = runner.simulate_case(rec)
    assert res.ok, res.error
    kms = res.config_used["overrides"].get("k_member_shear")
    assert kms is not None, "k_member_shear ativo mas ausente do config_used"
    # a trilha de auditoria bate com o que o JointMaterial recebeu
    assert abs(kms - kw["k_member_shear"]) < 1e-9
    # ...e com a aritmetica declarada: k_member_shear = GA_member / t.
    #
    # O `GA_member` vem LIDO da config adotada, nao digitado: ate 2026-08-02
    # este assert fixava `20000.0` e quebrou na adocao legitima que o levou a
    # 22000 (re-fit apos a re-digitalizacao da t10). Um teste de TRILHA DE
    # AUDITORIA nao deve reprovar porque a constante auditada mudou — o que
    # ele possui e' a igualdade `config_used == o que o engine recebeu ==
    # GA/t`. A banda fisica abaixo continua pegando config corrompida.
    from bolt_analysis_studio.calibration import knowledge_base as kb
    ga = kb.adopted_config("ROUSSEAU_HDPE")["cfg"]["GA_member"]
    assert 5e3 <= ga <= 1e5, f"GA_member fora da ordem fisica do HDPE: {ga}"
    assert abs(kms - ga / 0.012) < 1e-6


def test_k_member_shear_inert_on_steel():
    # Controle negativo: o aco Rousseau resolve para ROUSSEAU_2025, que NAO
    # declara GA_member ⇒ o termo fica fora (G~80 GPa torna o cisalhamento do
    # membro desprezivel). Se aparecer aqui, a injecao vazou de grupo.
    from bolt_analysis_studio.validation import runner
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import inputs_for

    rec = record("rousseau2025_steel_t12")
    kw = runner.material_kwargs_for(rec, inputs_for(rec.validation_case))
    assert "k_member_shear" not in kw or kw["k_member_shear"] == 0.0
    assert "k_member_shear" not in runner._effective_overrides(rec, {})


def test_retight_chain_carries_state(monkeypatch):
    # PR-5: maquinaria de cadeia (t0 -> retighten -> ... -> tN com estado
    # herdado) VALIDADA mas NAO ADOTADA — o gate global falhou (oil 10x
    # melhor, dry piorou; promocao parcial = decisao do professor). O ramo e
    # default-inerte: so ativa quando o adopted declara chain='retight'; o
    # teste ativa via patch (nenhum grupo canonico declara hoje).
    from bolt_analysis_studio.validation import runner
    from bolt_analysis_studio.validation.case_registry import record
    real = runner.kb.adopted_config

    def with_chain(key):
        entry = dict(real(key) or {})
        entry["chain"] = "retight"
        entry["cfg"] = {**entry.get("cfg", {}), "c_D": 0.5, "k_dmg_mu": 1.0,
                        "k_dmg_wear": 4.0, "W_ref": 1e4}
        return entry

    monkeypatch.setattr(runner.kb, "adopted_config", with_chain)
    t0 = runner.simulate_case(record("liu2022_fig6a_dry_release_t0"), n_cap=800)
    t1 = runner.simulate_case(record("liu2022_fig6a_dry_release_t1"), n_cap=800)
    assert t0.ok and t1.ok
    assert abs(t0.ratio[0] - 1.0) < 1e-9 and abs(t1.ratio[0] - 1.0) < 1e-9
    # dano herdado: o estagio t1 comeca com D>0 (dry acumula) => config gravada
    assert t1.config_used.get("chain") == "retight"
    assert t1.config_used.get("chain_stage") == 1
    assert t1.config_used.get("D_at_start", 0) > 0     # estado herdado do t0


def test_fingerprint_stable_and_result_roundtrip():
    from bolt_analysis_studio.validation.runner import (CaseResult,
                                                        engine_fingerprint,
                                                        simulate_case)
    assert engine_fingerprint() == engine_fingerprint()
    rec = _short_transverse_record()
    res = simulate_case(rec, n_cap=300, now="2026-07-10T00:00:00")
    d = res.to_dict()
    back = CaseResult.from_dict(d)
    assert back.case_id == res.case_id and back.mae == res.mae
    assert back.generated_at == "2026-07-10T00:00:00"


def test_emb_um_dict_per_case(monkeypatch):
    # PR-27: emb_um DICT por token de caso (proveniencia L24 por curva —
    # Liu2016, estagio rapido dependente de AF/F0) -> emb_depth do caso via
    # cfg CRU (dicts morrem no suggest_overrides). Sem token que case: nao
    # seta. Escalar segue o caminho antigo (bit-identico).
    from bolt_analysis_studio.validation import runner
    real_srcs = runner.kb.adopted_sources
    monkeypatch.setattr(runner.kb, "adopted_sources",
                        lambda: list(real_srcs()) + ["LIU_2016"])
    real_cfg = runner.kb.adopted_config
    monkeypatch.setattr(
        runner.kb, "adopted_config",
        lambda k: ({"cfg": {"emb_um": {"m30nm": 7.2, "af12p5kn": 9.3}}}
                   if k == "LIU_2016" else real_cfg(k)))
    real_sug = runner.kb.suggest_overrides
    monkeypatch.setattr(runner.kb, "suggest_overrides",
                        lambda k: {} if k == "LIU_2016" else real_sug(k))
    out30 = runner._adopted_overrides("LIU_2016", {}, "liu2016wear_fig9a_m30nm")
    assert abs(out30["emb_depth"] - 7.2e-6) < 1e-12
    out125 = runner._adopted_overrides("LIU_2016", {},
                                       "liu2016wear_fig11a_af12p5kn")
    assert abs(out125["emb_depth"] - 9.3e-6) < 1e-12
    outx = runner._adopted_overrides("LIU_2016", {},
                                     "liu2016wear_fig7_run1_1e6cyc")
    assert "emb_depth" not in outx


def test_per_case_block(monkeypatch):
    # PR-28: cfg adotado com per_case {token: {campo: valor}} resolve inputs
    # POR CURVA (mu de paper, floor lido, emb_um um->m). Sem token: nada.
    from bolt_analysis_studio.validation import runner
    real_srcs = runner.kb.adopted_sources
    monkeypatch.setattr(runner.kb, "adopted_sources",
                        lambda: list(real_srcs()) + ["SUN_2025_REASSY"])
    real_cfg = runner.kb.adopted_config
    pc = {"reassy02": {"mu_thread": 0.158, "mu_bearing": 0.158,
                       "loose_arrest_floor": 0.55, "emb_um": 3.0},
          "reassy10": {"mu_thread": 0.279, "mu_bearing": 0.279}}
    monkeypatch.setattr(
        runner.kb, "adopted_config",
        lambda k: ({"cfg": {"per_case": pc}} if k == "SUN_2025_REASSY"
                   else real_cfg(k)))
    real_sug = runner.kb.suggest_overrides
    monkeypatch.setattr(runner.kb, "suggest_overrides",
                        lambda k: {} if k == "SUN_2025_REASSY" else real_sug(k))
    o2 = runner._adopted_overrides("SUN_2025_REASSY", {},
                                   "sun2025efa110030_fig11a_loosening_reassy02")
    assert abs(o2["mu_thread"] - 0.158) < 1e-12
    assert abs(o2["loose_arrest_floor"] - 0.55) < 1e-12
    assert abs(o2["emb_depth"] - 3.0e-6) < 1e-12
    o10 = runner._adopted_overrides("SUN_2025_REASSY", {},
                                    "sun2025efa110030_fig11a_loosening_reassy10")
    assert abs(o10["mu_thread"] - 0.279) < 1e-12
    assert "emb_depth" not in o10 and "loose_arrest_floor" not in o10


def test_kb_sandbox_env_override(tmp_path, monkeypatch):
    # 2026-07-15: BAS_ADOPTED_CONFIGS redireciona SO adopted_configs.json
    # (sandbox p/ fits paralelos por fonte); sem a env, caminho canonico.
    import json
    from bolt_analysis_studio.calibration import knowledge_base as kb
    alt = tmp_path / "sandbox_configs.json"
    alt.write_text(json.dumps({"sources": {"FONTE_SANDBOX": {"cfg": {"c_bend": 9.9}}}}),
                   encoding="utf-8")
    monkeypatch.setenv("BAS_ADOPTED_CONFIGS", str(alt))
    assert kb.adopted_sources() == ["FONTE_SANDBOX"]
    assert kb.adopted_config("FONTE_SANDBOX")["cfg"]["c_bend"] == 9.9
    monkeypatch.delenv("BAS_ADOPTED_CONFIGS")
    assert "FONTE_SANDBOX" not in kb.adopted_sources()   # canonico de volta
