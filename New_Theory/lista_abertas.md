# Curvas ABERTAS — fora do tripé, sem exceção e sem declaração

**5 curvas.** Gerado por `py -3.12 New_Theory/lista_abertas.py`; recomputado do store a cada execução — **não editar à mão**.

Régua: res.máx ≤ 0,10 · MAE ≤ 0,05 · σ_res ≤ `max(0,025; piso da fonte)`. Os múltiplos são do limite que de fato vale para aquela fonte.

| fonte | curva | MAE | res.máx | σ_res | manda | só σ | camada | forma nomeada |
|---|---|---:|---:|---:|---|:--:|---|---|
| LIU_2025 | `liu2025_M16_amp0p8` | 0.0393 (0.8×) | 0.0863 (0.9×) | 0.0419 (1.7×) | sigma | ✅ | classe_parada(aceleracao tardia) | liu2025_par_de_taxas_opostas.md |
| LIU_2025 | `liu2025_M16_fig2_single` | 0.0279 (0.6×) | 0.0579 (0.6×) | 0.0270 (1.1×) | sigma | ✅ | classe_parada(aceleracao tardia) | liu2025_fig2_forma_rampa_fechada.md |
| YANG_2021 | `yang2021_amp0p5mm_ax8kN` | 0.0324 (0.6×) | 0.1083 (1.1×) | 0.0388 (1.6×) | sigma |  | classe_parada(aceleracao tardia) | yang2021_abertas_geometria_dos_inputs.md |
| YANG_2021 | `yang2021_amp1p0mm_ax2kN` | 0.0285 (0.6×) | 0.1074 (1.1×) | 0.0320 (1.3×) | sigma |  | classe_parada(aceleracao tardia) | yang2021_abertas_geometria_dos_inputs.md |
| YANG_2021 | `yang2021_amp0p6mm_ax8kN_r1` | 0.0167 (0.3×) | 0.0813 (0.8×) | 0.0268 (1.1×) | sigma | ✅ | classe_parada(aceleracao tardia) | yang2021_r1_sem_rota_resultado.md |

- reprovam **só** no σ_res: **3**
- perna que manda: sigma 5
- camada: classe_parada(aceleracao tardia) 5
- com forma nomeada: 5 de 5
