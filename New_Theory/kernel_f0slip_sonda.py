"""Sonda F0 x slip do kernel A — POR QUE o modelo desacelera onde o dado acelera?

Wear e rotational (os canais que dominam 8/9 do nucleo) sao ambos ~ mu*F0*slip.
Em disp-mode, F0 CAI e slip = max(0, delta - delta_free - mu*F0/k_tr) CRESCE —
a competicao decide o sinal da taxa. Esta sonda instrumenta a simulacao
canonica (engine intacto, mecanismos default) e mede, na janela
pos-assentamento:

  s_F0    = dlog(F0)/dlogN        (negativo)
  s_slip  = dlog(slip)/dlogN      (positivo)
  s_rate  = dlog(taxa canal)/dlogN  (medido por canal: wear, rotational)
  a_impl  = expoente de F0 que o DADO exigiria no driver comum:
            a*s_F0 + s_slip = -p_dado  =>  a = (-p_dado - s_slip)/s_F0
            (p_dado por curva, da leitura kernel_formA_leitura.json)

Se a_impl for consistente entre curvas E rigs, ele e a semente de
satisfazibilidade do FAIL2 (expoente compartilhado no driver mu*F0*slip).
"""
import sys, json, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path('src').resolve()))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial, resolve_transverse_slip)

H = {}
exec(compile(pathlib.Path('New_Theory/liu2025_ramp_v2_gates.py')
             .read_text(encoding='utf-8').split('P = print')[0], 'harness', 'exec'), H)

CURVAS = ['chu2026ti_D0p4mm_F0_61kN_test7', 'chu2026ti_D0p5mm_F0_49kN_test3',
          'chu2026ti_D0p7mm_F0_49kN_test4',
          'karlsen2022_M30_HVtorqued_run14p2', 'yang2019_M10_amp0p4_5Hz']
P_DADO = json.load(open('New_Theory/kernel_formA_leitura.json',
                        encoding='utf-8'))['p_por_curva']
P = print
P('=' * 78)
P('SONDA F0 x slip — decomposicao da desaceleracao do modelo (janela >20%% N)')
P('=' * 78)
out = {}
for cid in CURVAS:
    rec, case, load, geom, kw, _ = H['build'](cid)
    mat = JointMaterial(**kw)
    ana = DynamicStiffnessAnalyzer(geom, mat, case.initial_preload_N)
    d = load['delta_mm'] * 1e-3 if load['mode'] == 'displacement' else None
    # referencia com as convencoes do runner (offset/scale + FLOOR_TRIM)
    from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root
    from bolt_analysis_studio.validation import runner as _rn
    cx, cr = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
    off = float(getattr(case, 'csv_x_offset', 0.0) or 0.0)
    cx = np.maximum(cx - off, 0.0) * float(getattr(case, 'csv_x_scale', 1.0) or 1.0)
    cr = cr / max(cr[0], 1e-9)
    keep = cr >= _rn.FLOOR_TRIM
    x = cx[keep]
    N = int(x[-1])
    F0a = np.empty(N + 1)
    F0a[0] = case.initial_preload_N
    slip = np.zeros(N + 1)
    dfw = np.zeros(N + 1)
    dfr = np.zeros(N + 1)
    for n in range(1, N + 1):
        slip[n] = resolve_transverse_slip(ana.state, mat, load['F_amp_N'],
                                          load['theta'], delta_amp=d, geom=geom)
        snap = ana.step_cycle(load['F_amp_N'], load['theta'],
                              case.frequency_Hz, delta_amp=d)
        ana.history.clear()
        F0a[n] = max(ana.state.F_0, 0.0)
        bym = snap.dF_0_by_mech
        dfw[n] = -bym.get('wear', 0.0)
        dfr[n] = -bym.get('rotational_loosening', 0.0)

    k = np.arange(N + 1) > 0.2 * N

    def slope(y):
        m = k & (y > 1e-15)
        if m.sum() < 10:
            return float('nan')
        n_ = np.arange(N + 1)[m]
        return float(np.polyfit(np.log10(n_), np.log10(y[m]), 1)[0])

    sF0 = slope(F0a)
    ssl = slope(slip)
    swear = slope(dfw)
    srot = slope(dfr)
    sdrv = slope(F0a * slip)
    p_d = P_DADO.get(cid, [float('nan')])[0]
    a_impl = ((-p_d) - ssl) / sF0 if (sF0 and not np.isnan(p_d)) else float('nan')
    out[cid] = dict(s_F0=sF0, s_slip=ssl, s_rate_wear=swear, s_rate_rot=srot,
                    s_driver=sdrv, p_dado=p_d, a_impl=a_impl,
                    slip_ini=float(slip[k][0]) if k.any() else None,
                    slip_fim=float(slip[-1]), F0_fim_frac=float(F0a[-1] / F0a[0]))
    P('')
    P('%s  (N=%d)' % (cid, N))
    P('  s_F0 %+7.3f | s_slip %+7.3f | driver(F0*slip) %+7.3f'
      % (sF0, ssl, sdrv))
    P('  taxa WEAR %+7.3f | taxa ROT %+7.3f | alvo (=-p_dado) %+7.3f'
      % (swear, srot, -p_d))
    P('  => expoente implicito a no driver F0^a*slip: a = %.2f' % a_impl)

vals = [v['a_impl'] for v in out.values() if not np.isnan(v['a_impl'])]
P('')
P('=' * 78)
P('a_impl por curva: %s' % ['%.2f' % v for v in vals])
if vals:
    P('mediana a_impl = %.2f   (a=1 e o engine de hoje; a<1 = a perda e menos'
      % float(np.median(vals)))
    P('punida pela queda de F0 => a taxa nao desaba => acompanha o slip)')
else:
    P('sem valores de a_impl')
json.dump(out, open('New_Theory/kernel_f0slip_result.json', 'w'), indent=1)
P('-> New_Theory/kernel_f0slip_result.json')
