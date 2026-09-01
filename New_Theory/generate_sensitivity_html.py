"""Pagina de SENSIBILIDADE + INVENTARIO DE VARIAVEIS + reducao de DOF.

Diretiva do professor 2026-07-09: "o que podemos fazer para reduzir o numero de
variaveis e tornar nosso modelo mais robusto? gere uma lista de variaveis e faca
um estudo de sensitividade".

Le sensitivity_study.json (OAT x1.2 / /1.2, S = deslocamento medio da predicao)
e gera validation_html/sensitivity.html:
  1. contagem honesta de DOF: 88 campos != 88 graus de liberdade (classes);
  2. inventario COMPLETO classificado (input / per-rig / constante compartilhada
     / tuner==1 / capability inerte / modo / dinamica);
  3. tornado de sensibilidade por familia (transversal / axial);
  4. propostas de reducao fundamentadas (merge K/H, Estagio B, congelar
     insensiveis, ler-em-vez-de-fitar).

Run: python New_Theory/generate_sensitivity_html.py
"""
from __future__ import annotations
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
DATA = ROOT / "New_Theory/sensitivity_study.json"
OUT = ROOT / "New_Theory/validation_html/sensitivity.html"

# ---------------------------------------------------------------- inventario
# classe -> (titulo, descricao, cor-token)
CLASSES = {
    "input":   ("INPUT por junta", "medido/handbook/lido-do-dado — nunca fitado", "in"),
    "perrig":  ("PER-RIG", "constante por bancada (fitada-this-rig ou lida de feature)", "pr"),
    "shared":  ("CONSTANTE compartilhada", "fisica do modelo, congelada 1x (Estagio A/pack)", "sh"),
    "tuner":   ("TUNER ≡ 1.0", "camada legada congelada — alvo de remocao (Estagio B)", "tn"),
    "inert":   ("CAPABILITY inerte", "default OFF ⇒ 0 DOF; per-rig SO quando ligada", "cp"),
    "mode":    ("MODO (switch)", "escolha discreta de formulacao, nao DOF continuo", "md"),
    "dyn":     ("DINAMICA/bookkeeping", "nao afeta a trajetoria de pre-carga", "dy"),
}
# campo -> (classe, nota curta)
INVENTORY = {
    # inputs
    "mu_thread": ("input", "atrito rosca — Motosh de T+F0 ou assumido 0.15"),
    "mu_bearing": ("input", "atrito apoio — idem"),
    "emb_depth": ("input", "f_Z: VDI por Rz OU data-implicito da queda-inicial (L24, axial)"),
    # per-rig
    "c_bend": ("perrig", "compliance transversal (bending) — o knob per-rig dominante; sobrecarregado (§4.35)"),
    "loose_arrest_floor": ("perrig", "piso de arresto — LIDO do fim do dado"),
    "N_emb": ("shared", "cte de tempo do assentamento (50); Zhang per-rig 8 (dado tabela)"),
    # constantes compartilhadas
    "k_wear_spec": ("shared", "razao K/H IDENTIFICAVEL [1/Pa] — parametro canonico do merge §4.42a (0 = via legada)"),
    "K_archard": ("shared", "LEGADO (merged → k_wear_spec §4.42a; so lido se k_wear_spec=0)"),
    "hardness": ("shared", "LEGADO (merged → k_wear_spec §4.42a; so lido se k_wear_spec=0)"),
    "k_j_init": ("shared", "rigidez GW inicial — CONGELADO §4.42c (enforced no registry)"),
    "alpha_GW": ("shared", "expoente GW — CONGELADO §4.42c (enforced no registry)"),
    "C_creep": ("shared", "Norton — POR PAR tribologico (§4.7; ancora 304SS distinta)"),
    "t_0": ("shared", "tempo de referencia Norton"),
    "tr_loose_gain": ("shared", "amplificacao dinamica transversal (2.0)"),
    "eta_loose": ("shared", "rigidez torsional efetiva (bolt_torsion, 15)"),
    "W_conf_ref": ("shared", "conformacao — per-par UFU, sem ancora (§4.9 null)"),
    "conform_pressure_exp": ("shared", "expoente de pressao da conformacao (2)"),
    "p_ref_conform": ("shared", "pressao de referencia da conformacao"),
    "slip_regime_sharpness": ("shared", "nitidez do gate de gross-slip (1.0)"),
    "slip_capacity_coeff": ("shared", "kappa CM — CONGELADO §4.42c (enforced no registry)"),
    "partial_slip_exp": ("shared", "expoente partial-slip — CONGELADO §4.42c (enforced no registry)"),
    # tuners ==1
    "k_emb_scale": ("tuner", ""), "k_creep_scale": ("tuner", ""),
    "k_wear_scale_ax": ("tuner", ""), "k_wear_scale_tr": ("tuner", ""),
    "k_loose_scale_ax": ("tuner", ""), "k_loose_scale_tr": ("tuner", ""),
    "Phi_ax_correction": ("tuner", ""), "Phi_tr_correction": ("tuner", ""),
    "k_damage_scale": ("tuner", ""),
    # capabilities inertes (0/off por default)
    "k_thread_fret": ("inert", "fretting axial ∝A_F (§4.6)"),
    "fret_freq_exp": ("inert", "freq-dependencia do fretting (§4.39)"),
    "f_ref_fret": ("inert", "companheira de fret_freq_exp"),
    "emb_conform_exp": ("inert", "supersedida por S_ρ (§4.18)"),
    "p_ref_emb": ("inert", "companheira"),
    "creep_conform_exp": ("inert", "conformacao no creep"),
    "emb_amp_exp": ("inert", "ρ-settling (§4.18)"),
    "rho_ref_emb": ("inert", "companheira"),
    "emb_load_frac": ("inert", "settling ∝carga (§4.19)"),
    "k_member_shear": ("inert", "cisalhamento de membro (HDPE, §4.20)"),
    "dmg_dwell_exp": ("inert", "dwell de dano ×freq (§4.21)"),
    "f_ref_dmg": ("inert", "companheira"),
    "free_spin": ("inert", "rotacao pos-arresto (§4.23)"),
    "member_loss_eta": ("inert", "viscoelastico de membro (§4.27)"),
    "emb_slip_gate": ("inert", "bedding gateado por slip (§4.29)"),
    "k_wear_running": ("inert", "running-in de wear (=1 off, §4.29)"),
    "N_wear_run": ("inert", "companheira"),
    "crash_trigger_frac": ("inert", "gatilho de criticalidade (§4.30)"),
    "crash_trigger_sharpness": ("inert", "companheira"),
    "k_partial_slip": ("inert", "energia de partial-slip (§4.32)"),
    "dmg_gross_exp": ("inert", "onset continuo de dano (§4.33)"),
    "c_D": ("inert", "crescimento de dano D"),
    "W_ref": ("inert", "companheira de c_D"),
    "k_dmg_mu": ("inert", "dano→atrito"),
    "k_dmg_wear": ("inert", "dano→wear"),
    "W_crit": ("inert", "limiar de energia (legado por-curva)"),
    "dmg_onset_sharpness": ("inert", "companheira"),
    "slip_onset_W": ("inert", "incubacao (platô estagio-1)"),
    "slip_onset_sharpness": ("inert", "companheira"),
    "k_ratchet": ("inert", "ratchet cinematico (per-rig quando ligada, §4.15)"),
    "delta_free": ("inert", "take-up fixo (LIDO do dado quando ligada)"),
    "ratchet_torque_coupled": ("inert", "forma-produto do ratchet"),
    "couple_famp_slip": ("inert", "acoplamento F_amp↔slip (#4)"),
    "loose_kin_ceiling": ("inert", "teto cinematico em serie (§4.35)"),
    "s_crit_loose": ("inert", "taxa graduada (§4.37)"),
    "k_loose_graded": ("inert", "taxa graduada (§4.37)"),
    "k_emb_renew": ("inert", "renovacao no reaperto (§4.10)"),
    "k_gall": ("inert", "galling/recovery (§4.11)"),
    "fatigue_enabled": ("inert", "fadiga→cliff (§ fatigue-tail)"),
    "fat_Kt": ("inert", "fadiga"), "fat_sigma_uts": ("inert", "fadiga"),
    "fat_sigma_knee": ("inert", "fadiga"), "fat_C1": ("inert", "fadiga"),
    "fat_m1": ("inert", "fadiga"), "fat_C2": ("inert", "fadiga"),
    "fat_m2": ("inert", "fadiga"), "fat_sigma_endurance": ("inert", "fadiga"),
    "fatigue_residual_frac": ("inert", "fadiga"),
    # modos
    "k_tr_mode": ("mode", "axial_frac | bending"),
    "loosening_slip_coupling": ("mode", "off | gross_fraction"),
    "loose_torsion_mode": ("mode", "legacy | bolt_torsion"),
    "conform_driver": ("mode", "raw | effective"),
    "slip_regime_mode": ("mode", "off | cattaneo_mindlin"),
    "loose_rate_mode": ("mode", "torque | graded_scrit"),
    # dinamica
    "rayleigh_alpha": ("dyn", ""), "rayleigh_beta": ("dyn", ""),
    "m_x": ("dyn", ""), "m_y": ("dyn", ""), "I_theta": ("dyn", ""),
}

NICE_P = {"mu": "µ (rosca+apoio)", "emb_depth": "emb_depth (f_Z)",
          "K_archard": "K_archard (≡K/H)"}


def check_inventory():
    import dataclasses
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    fields = {f.name for f in dataclasses.fields(JointMaterial)}
    missing = fields - set(INVENTORY)
    extra = set(INVENTORY) - fields
    if missing or extra:
        raise SystemExit(f"inventario dessincronizado: faltam {missing}, sobram {extra}")
    return fields


def tornado_svg(rank, W=760, title=""):
    """rank = [(param, S_mean, S_max, n_casos)] desc. Barras horizontais."""
    if not rank:
        return ""
    rh, gap, top = 21, 5, 8
    H = top + len(rank) * (rh + gap) + 26
    smax = max(r[2] for r in rank) or 1e-9
    ml, mr = 190, 60
    bw = W - ml - mr
    s = [f'<svg viewBox="0 0 {W} {H}" class="plot" xmlns="http://www.w3.org/2000/svg" role="img">']
    for i, (p, sm, sx, n) in enumerate(rank):
        y = top + i * (rh + gap)
        wm = sm / smax * bw
        wx = sx / smax * bw
        nm = NICE_P.get(p, p)
        s.append(f'<text x="{ml-8}" y="{y+rh*0.72:.0f}" class="pl" text-anchor="end">{nm}</text>')
        s.append(f'<rect x="{ml}" y="{y+3}" width="{wx:.1f}" height="{rh-8}" class="bx"/>')
        s.append(f'<rect x="{ml}" y="{y}" width="{wm:.1f}" height="{rh-2}" class="bm"/>')
        s.append(f'<text x="{ml+wx+5:.1f}" y="{y+rh*0.72:.0f}" class="pv">{sm:.3f}</text>')
    s.append(f'<text x="{ml}" y="{H-6}" class="axl">S = deslocamento médio da predição '
             f'[F/F₀] por ±20% no parâmetro · barra clara = pior caso</text>')
    s.append('</svg>')
    return "".join(s)


def main():
    check_inventory()
    res = json.loads(DATA.read_text(encoding="utf-8"))

    # ranking por familia
    ranks = {}
    for fam in ("transverse", "axial"):
        agg = {}
        for r in res:
            if r["fam"] != fam:
                continue
            for p, s in r["params"].items():
                if s.get("mean") is not None:
                    agg.setdefault(p, []).append(s["mean"])
        rank = sorted(((p, statistics.mean(v), max(v), len(v))
                       for p, v in agg.items()), key=lambda t: -t[1])
        ranks[fam] = rank

    # classes de veredicto do estudo (limiares em unidades de F/F0)
    def verdict(p):
        st = ranks["transverse"]
        sa = ranks["axial"]
        vt = next((r[1] for r in st if r[0] == p), None)
        va = next((r[1] for r in sa if r[0] == p), None)
        vals = [v for v in (vt, va) if v is not None]
        if not vals:
            return "—", ""
        m = max(vals)
        if m >= 0.05:
            return "DOF real", "vh"
        if m >= 0.01:
            return "sensível", "vm"
        return "congelável", "vl"

    # inventario agrupado
    groups = {}
    for f, (cls, note) in INVENTORY.items():
        groups.setdefault(cls, []).append((f, note))
    counts = {cls: len(v) for cls, v in groups.items()}

    inv_rows = []
    for cls in ("input", "perrig", "shared", "tuner", "inert", "mode", "dyn"):
        title, desc, tok = CLASSES[cls]
        inv_rows.append(f'<tr class="ghead"><td colspan="4"><b>{title}</b> '
                        f'({counts.get(cls,0)}) — {desc}</td></tr>')
        for f, note in sorted(groups.get(cls, [])):
            vd, vc = verdict("mu" if f in ("mu_thread", "mu_bearing") else f) \
                if cls in ("input", "perrig", "shared") else ("", "")
            badge = f'<span class="vb {vc}">{vd}</span>' if vd else ""
            inv_rows.append(f'<tr><td class="fn">{f}</td><td class="cl {tok}">'
                            f'{title.split()[0]}</td><td>{note}</td><td>{badge}</td></tr>')

    active_dof = counts.get("input", 0) + counts.get("perrig", 0) + counts.get("shared", 0)
    total = sum(counts.values())

    tor_t = tornado_svg(ranks["transverse"], title="transversal")
    tor_a = tornado_svg(ranks["axial"], title="axial")
    case_list = ", ".join(f'{r["name"]} (MAE₀ {r["mae0"]:.3f})' for r in res)

    html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sensibilidade e redução de variáveis — BAS V2</title>
<style>
:root{{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --di:#2f6f8f;--err:#c0392b;--good:#1a7a4c;--warn:#b3452c;--accent:#2f6f8f;
  --bm:#2f6f8f;--bx:#c9dbe6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;
  --card:#211e18;--bd:#332e26;--di:#6bb6d6;--err:#e8776b;--good:#5fd39a;--warn:#e8936b;
  --accent:#6bb6d6;--bm:#6bb6d6;--bx:#2e4652}}}}
:root[data-theme=dark]{{--bg:#16140f;--fg:#ece7de;--mut:#9a938a;--card:#211e18;--bd:#332e26;
  --di:#6bb6d6;--err:#e8776b;--good:#5fd39a;--warn:#e8936b;--accent:#6bb6d6;--bm:#6bb6d6;--bx:#2e4652}}
:root[data-theme=light]{{--bg:#faf9f7;--fg:#1c1a17;--mut:#6b655c;--card:#fff;--bd:#e6e1d8;
  --di:#2f6f8f;--err:#c0392b;--good:#1a7a4c;--warn:#b3452c;--accent:#2f6f8f;--bm:#2f6f8f;--bx:#c9dbe6}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 -apple-system,"Segoe UI",Roboto,sans-serif;padding:26px 20px 70px}}
.wrap{{max-width:1100px;margin:0 auto}}
.back{{font-size:.8rem;margin:0 0 8px}}.back a{{color:var(--accent);text-decoration:none}}
h1{{font-size:1.45rem;margin:0 0 4px;letter-spacing:-.01em}}
.lede{{color:var(--mut);margin:0 0 14px;max-width:78ch;font-size:.92rem}}
h2{{font-size:1rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);
  margin:30px 0 10px;border-bottom:1px solid var(--bd);padding-bottom:5px}}
.card{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:14px 16px;margin-bottom:14px}}
.plot{{width:100%;height:auto;display:block}}
.pl{{fill:var(--fg);font-size:11.5px;font-family:Consolas,monospace}}
.pv{{fill:var(--mut);font-size:10.5px;font-family:Consolas,monospace}}
.axl{{fill:var(--mut);font-size:10.5px}}
.bm{{fill:var(--bm)}}.bx{{fill:var(--bx)}}
.dof{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}}
.dof .b{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:10px 12px;text-align:center}}
.dof .n{{font-size:1.6rem;font-weight:750;font-family:Consolas,monospace;color:var(--accent)}}
.dof .l{{font-size:.72rem;color:var(--mut);line-height:1.35}}
table{{border-collapse:collapse;width:100%;font-size:.8rem}}
td{{padding:4px 10px;border-bottom:1px solid var(--bd);vertical-align:top}}
.fn{{font-family:Consolas,monospace;white-space:nowrap}}
.cl{{font-size:.7rem;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}}
.ghead td{{padding-top:14px;color:var(--accent)}}
.vb{{font-size:.7rem;font-weight:700;padding:1px 8px;border-radius:999px;white-space:nowrap}}
.vb.vh{{background:var(--err);color:#fff}}
.vb.vm{{background:var(--warn);color:#fff}}
.vb.vl{{background:var(--good);color:#fff}}
ol.prop{{max-width:80ch;padding-left:22px}}ol.prop li{{margin-bottom:10px}}
.note{{background:var(--card);border:1px solid var(--bd);border-left:3px solid var(--accent);
  border-radius:8px;padding:10px 14px;margin:10px 0 16px;font-size:.85rem;max-width:82ch}}
code{{font-family:Consolas,monospace;font-size:.92em}}
</style></head><body><div class="wrap">
<p class="back"><a href="index.html">&#8592; índice de validação</a></p>
<h1>Sensibilidade e redução de variáveis</h1>
<p class="lede">Estudo OAT (±20% em cada constante ativa, S = deslocamento médio da
predição em unidades de F/F₀) sobre {len(res)} casos representativos, + inventário
completo dos {total} campos de <code>JointMaterial</code> classificados por papel.
Menos graus de liberdade efetivos = mais robustez — mas a contagem honesta importa:
<b>{total} campos ≠ {total} DOF</b>.</p>

<h2>Contagem honesta de graus de liberdade</h2>
<div class="dof">
  <div class="b"><div class="n">{total}</div><div class="l">campos no dataclass</div></div>
  <div class="b"><div class="n">{counts.get("inert",0)}</div><div class="l">capabilities INERTES<br>(OFF ⇒ 0 DOF)</div></div>
  <div class="b"><div class="n">{counts.get("tuner",0)}</div><div class="l">tuners ≡ 1.0<br>(Estágio B remove)</div></div>
  <div class="b"><div class="n">{counts.get("mode",0)+counts.get("dyn",0)}</div><div class="l">modos + dinâmica<br>(não-DOF contínuo)</div></div>
  <div class="b"><div class="n">{active_dof}</div><div class="l">ativos no canônico<br>(inputs + per-rig + compartilhadas)</div></div>
  <div class="b"><div class="n">2</div><div class="l">livres POR BANCADA nova<br>(transversal: c_bend + floor)</div></div>
</div>
<div class="note">Para uma junta transversal NOVA, os DOF realmente livres são
<b>c_bend</b> e <b>loose_arrest_floor</b> (o floor é lido do fim do dado ⇒ na prática
1 fitado). No axial, o <b>emb</b> é lido da queda-inicial (L24) ⇒ zero fitado; a
fraqueza é o <b>C_creep por-par</b> (§4.7). As constantes compartilhadas são fitadas
UMA vez no dataset inteiro (Estágio A), não por junta.</div>

<h2>Tornado — transversal (7 casos)</h2>
<div class="card">{tor_t}</div>
<h2>Tornado — axial (2 casos, modo força)</h2>
<div class="card">{tor_a}</div>
<div class="note"><b>Leitura:</b> barra escura = S médio entre casos; clara = pior caso.
Badges no inventário: <span class="vb vh">DOF real</span> S≥0.05 (precisa proveniência),
<span class="vb vm">sensível</span> 0.01–0.05, <span class="vb vl">congelável</span> S&lt;0.01
(fixar no nominal sem custo). Working point: PACK canônico + per-rig declarado
(ranking local; casos: {case_list}).</div>

<h2>Inventário completo — {total} campos classificados</h2>
<div class="card" style="overflow-x:auto"><table>
<tr><td><b>campo</b></td><td><b>classe</b></td><td><b>nota</b></td><td><b>veredicto do estudo</b></td></tr>
{''.join(inv_rows)}
</table></div>

<h2>Propostas de redução (fundamentadas no estudo)</h2>
<ol class="prop">
<li><b>Merge estrutural K_archard/hardness ⇒ <code>k_wear_spec = K/H</code> [1/Pa].</b>
  Os dois só aparecem como razão (wear e fretting) — não-identificáveis separadamente.
  −1 variável, zero custo, remove uma equifinalidade exata.</li>
<li><b>Estágio B: remover a camada de tuners (≡1.0).</b> −{counts.get("tuner",0)} variáveis
  (roadmap #8, spec 2026-07-02 §3; shim p/ .msd legados). Já congelados — a remoção é
  higiene de API que impede regressão a fits por multiplicador.</li>
<li><b>Congelar os "congeláveis" do tornado</b> (badges verdes): fixar no nominal e
  retirar de qualquer rotina de fit/registro de candidatos (parameter_registry) — DOF
  nominal → 0 sem mudança de predição mensurável.</li>
<li><b>Ler em vez de fitar (converter DOF em proveniência):</b> emb ← queda-inicial
  (feito no axial, L24: 12 condições, −90% erro); floor ← fim do dado (feito);
  delta_free ← regressão de onset (feito no Liu2025). Restante: c_bend é o único knob
  transversal sem leitura conhecida (§4.41) — alvo de instrumentação futura
  (medir compliance da fixação), não de fit.</li>
<li><b>Capabilities inertes ({counts.get("inert",0)} campos) não são DOF</b> — cada uma
  liga SÓ com falsificação dupla + gate (doutrina). Higiene proposta p/ Estágio B:
  movê-las a um bloco <code>forms</code> separado do núcleo, deixando o dataclass
  principal com ~{active_dof} campos físicos.</li>
<li><b>Dinâmica (rayleigh/m/I) fora de JointMaterial</b> — são parâmetros de solver,
  não de material; não afetam a trajetória de pré-carga.</li>
</ol>
<p class="lede" style="font-size:.8rem">Gerado por <code>New_Theory/generate_sensitivity_html.py</code>
a partir de <code>sensitivity_study.json</code> (OAT ±20%). Veredicto: MODEL_LEGITIMACY §4.42.</p>
</div></body></html>'''
    OUT.write_text(html, encoding="utf-8")
    print(f"escrito: {OUT}")
    for fam in ("transverse", "axial"):
        print(f"[{fam}] top-5: " + ", ".join(
            f"{p}={sm:.3f}" for p, sm, _, _ in ranks[fam][:5]))


if __name__ == "__main__":
    main()
