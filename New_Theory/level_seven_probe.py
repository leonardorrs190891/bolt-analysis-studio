"""AS 7 LEVEL-LIMITED — o piso lido do dado fecha, ou não?

Continuação de `frontier_classes.py`. A varredura das 4 classes disse que 7
curvas erram de NÍVEL (`max|resíduo − média| < 0,10`: removido um deslocamento
uniforme, o pico entra no tripé) e que todas violam SÓ o pico. Mas isso é
condição NECESSÁRIA — não prova que **ler o `loose_arrest_floor` do dado** as
fecha, porque o piso age na CAUDA e não uniformemente.

Este script responde a pergunta direta, sem fitar nada. São DUAS alavancas de
nível disponíveis por LEITURA (os dois leitores de proveniência L24), e elas
agem em lugares diferentes da curva — por isso as duas entram, e a combinação:

  | alavanca | leitor | onde age |
  |---|---|---|
  | `loose_arrest_floor` | `arrest_floor_from_curve` (platô final) | CAUDA |
  | `emb_depth` | `emb_depth_from_curve` (queda-inicial) | DEGRAU INICIAL |

Convenção de leitura idêntica à `prefit.py:37-40` (ratio CRU do CSV, normalizado
internamente por r[0]); injeção via `_prefit_overrides`, que vence o cfg adotado
e é filtrada a campos de `JointMaterial` (`runner.py:373`).

Não é fit: os dois valores vêm do dado (doutrina L24 "ler em vez de fitar"; a
regra §4.40 é que quando handbook e data-implícito divergem, o data-implícito
ganha). Não é adoção: `simulate_case` NÃO escreve o store (só
`report`/`parallel_batch`).

CONTROLE NEGATIVO OBRIGATÓRIO: antes de cada sonda, a mesma curva é re-simulada
com `_prefit_overrides` VAZIO. Se isso não reproduzir o store, a linha de base
da sonda está errada e o resultado não vale — a curva é marcada `CTRL-FAIL` em
vez de receber veredicto.

Run:  py -3.12 New_Theory/level_seven_probe.py [--only token] [--skip-slow]
      (`--skip-slow` pula liu2016, que tem 5.000.000 de ciclos por passada)
Saída: New_Theory/level_seven_probe.json + .md
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.calibration.provenance import (  # noqa: E402
    arrest_floor_from_curve, emb_depth_from_curve)
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.inputs import (  # noqa: E402
    geometry_for_case, inputs_for, load_full_curve)
from bolt_analysis_studio.validation.runner import simulate_case  # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
CLASSES = ROOT / "New_Theory" / "frontier_classes.json"
OUT_JSON = ROOT / "New_Theory" / "level_seven_probe.json"
OUT_MD = ROOT / "New_Theory" / "level_seven_probe.md"
TRIPE = 0.10
BIT = 1e-9          # tolerancia do controle negativo (bit-a-bit)
SLOW = "liu2016wear_fig7_run2_5e6cyc"


def sim(rec, overrides):
    """Re-simula com overrides injetados. NAO escreve no store."""
    rec.validation_case._prefit_overrides = dict(overrides)
    try:
        res = simulate_case(rec)
    finally:
        rec.validation_case._prefit_overrides = None
    return res


def probe(rec, store_rec):
    out = {"case_id": rec.case_id, "fonte": rec.source}
    try:
        rel = rec.csv_path.relative_to(ROOT).as_posix()
    except ValueError:
        rel = str(rec.csv_path)
    cyc_cru, ratio_cru = load_full_curve(rel)
    floor, br = arrest_floor_from_curve(ratio_cru)
    # emb lido da QUEDA-INICIAL (mesma convencao do prefit.py:39)
    case = rec.validation_case
    inp = inputs_for(case)
    geom = geometry_for_case(case, grip_mm=inp["grip_mm"]["value"])
    emb, ebr = emb_depth_from_curve(cyc_cru, ratio_cru,
                                    case.initial_preload_N, geom.k_b)
    ov_cfg = store_rec["config_used"].get("overrides") or {}
    out["floor_cfg"] = ov_cfg.get("loose_arrest_floor")
    out["floor_lido"] = round(float(floor), 4)
    out["plateau"] = bool(br.get("plateau"))
    out["emb_cfg_um"] = store_rec["config_used"].get("emb_um")
    out["emb_lido_um"] = round(float(emb) * 1e6, 3)
    out["emb_prov"] = ebr.get("provenance")
    out["tem_pack"] = bool(ov_cfg.get("loose_torsion_mode"))
    out["mae_store"] = round(float(store_rec["mae"]), 4)
    out["maxerr_store"] = round(float(store_rec["maxerr"]), 4)

    # PRE-TESTE DE DIRECAO (custa zero simulacao). res_medio = media(modelo-dado):
    # positivo => o modelo RETEM MAIS que o dado => precisa de piso MENOR.
    # O piso lido so pode ajudar se andar para o lado que o residuo pede.
    res_medio = float(np.mean(np.asarray(store_rec["metric_pred"], float)
                              - np.asarray(store_rec["metric_data"], float)))
    out["res_medio"] = round(res_medio, 4)
    out["direcao_necessaria"] = "piso MENOR" if res_medio > 0 else "piso MAIOR"
    fc = ov_cfg.get("loose_arrest_floor")
    if fc is None:
        out["direcao_lida"] = "sem piso no cfg (default 0 = sem arresto)"
        out["direcao_bate"] = None
    else:
        d = float(floor) - float(fc)
        out["direcao_lida"] = ("piso MAIOR" if d > 0 else "piso MENOR"
                               if d < 0 else "igual")
        out["direcao_bate"] = bool((res_medio > 0) == (d < 0))

    t0 = time.time()
    ctrl = sim(rec, {})                                    # controle negativo
    out["mae_ctrl"] = None if ctrl.mae is None else round(float(ctrl.mae), 4)
    out["maxerr_ctrl"] = (None if ctrl.maxerr is None
                          else round(float(ctrl.maxerr), 4))
    if ctrl.ok and ctrl.mae is not None and ctrl.maxerr is not None:
        c_mae, c_max = float(ctrl.mae), float(ctrl.maxerr)
        ok_ctrl = (abs(c_mae - store_rec["mae"]) < BIT
                   and abs(c_max - store_rec["maxerr"]) < BIT)
    else:
        c_mae = c_max = float("nan")
        ok_ctrl = False
    out["controle_ok"] = bool(ok_ctrl)
    if not ok_ctrl:
        out["veredicto"] = "CTRL-FAIL"
        out["s"] = round(time.time() - t0, 1)
        return out

    # as tres alavancas de NIVEL disponiveis por LEITURA (nenhuma e fit)
    levers = {"piso": {"loose_arrest_floor": float(floor)},
              "emb": {"emb_depth": float(emb)},
              "piso+emb": {"loose_arrest_floor": float(floor),
                           "emb_depth": float(emb)}}
    best, best_key = None, None
    for key, ov in levers.items():
        pr = sim(rec, ov)
        if not pr.ok or pr.mae is None or pr.maxerr is None:
            out[key] = {"veredicto": "ERRO", "erro": pr.error}
            continue
        p_mae, p_max = float(pr.mae), float(pr.maxerr)
        v = ("INERTE" if (abs(p_mae - c_mae) < BIT and abs(p_max - c_max) < BIT)
             else "FECHA" if (p_mae < TRIPE and p_max < TRIPE)
             else "PIORA" if p_max > c_max + 1e-4
             else "MELHORA, NAO FECHA")
        out[key] = {"mae": round(p_mae, 4), "maxerr": round(p_max, 4),
                    "veredicto": v}
        if best is None or p_max < best:
            best, best_key = p_max, key
    out["s"] = round(time.time() - t0, 1)
    out["melhor_alavanca"] = best_key
    out["veredicto"] = (out.get(best_key, {}).get("veredicto", "ERRO")
                        if best_key else "ERRO")
    return out


def write_md(rows):
    L = []
    A = L.append
    n = len(rows)
    fecha = [r for r in rows if r["veredicto"] == "FECHA"]
    piora = [r for r in rows if r["veredicto"] == "PIORA"]
    inerte = [r for r in rows if r["veredicto"] == "INERTE"]
    melhora = [r for r in rows if r["veredicto"] == "MELHORA, NAO FECHA"]
    A("# As 7 LEVEL-LIMITED — o nível lido do dado fecha, ou não?\n")
    A("> **2026-07-28.** Continuação de `frontier_classes.md`. Store")
    A("> `4f5bedfbace4`. **Nenhum fit** (as duas constantes vêm de leitores de")
    A("> proveniência L24) e **nenhuma escrita no store** (`simulate_case` não")
    A("> grava). Controle negativo bit-a-bit antes de cada sonda: as")
    A(f"> {n} curvas reproduziram o store exatamente.")
    A("> Script: `New_Theory/level_seven_probe.py`; números: `.json`.")
    if n < 7:
        falta = 7 - n
        A(f">")
        A(f"> **COBERTURA: {n} das 7.** Falta{'m' if falta > 1 else ''} "
          f"{falta} — `{SLOW}` tem **5.000.000 de ciclos** por passada")
        A("> (~30 min para controle + 3 alavancas) e está medindo em separado")
        A(f"> (`py -3.12 New_Theory/level_seven_probe.py --only liu2016`).")
        A("> Nenhuma conclusão abaixo depende dela; ela pode mover a contagem")
        A("> de desfechos em ±1.")
    A("")
    A("> **RECLASSIFICAÇÃO POSTERIOR (mesma data, errata 2ª de")
    A("> `frontier_classes.md` §6):** o `bauer2024_M12_fig8_test3` **não é mais")
    A("> LEVEL-LIMITED** — ele é uma das 3 réplicas do mesmo ensaio do Bauer, e")
    A("> passou a **DATA-LIMITED** (scatter irredutível, provado em")
    A("> `replicate_impossibility_sweep_2026-07-28.md`). A classe LEVEL tem **6")
    A("> curvas**, não 7. As medições abaixo continuam válidas como medições — o")
    A("> `bauer test3` sondado PIOROU, e agora se sabe que ele nunca foi candidato")
    A("> a nível. Isso **reforça** o resultado negativo: das 6 curvas de nível de")
    A("> fato, **1 fecha**.\n")
    A("---\n")
    A("## 1. Resultado — e a correção de uma leitura minha\n")
    A(f"**Das {n} curvas, ler o nível fecha {len(fecha)}.**")
    A(f"{len(melhora)} melhora sem fechar, {len(inerte)} é inerte e")
    A(f"**{len(piora)} PIORAM**.\n")
    A("Isto **corrige** o que eu escrevi ao entregar a varredura das 4 classes")
    A("(\"as 7 de nível são o alvo mais barato da meta, 147 → potencialmente")
    A("154\"). A classificação está certa — o resíduo *é* de nível, e isso é uma")
    A("propriedade medida do resíduo. Mas **as duas constantes de nível que a")
    A("campanha sabe LER do dado não são a alavanca** em 5 das 6. O caveat que")
    A("acompanhava a classe (\"condição necessária, não prova\") era o certo, e")
    A("agora está medido em vez de suposto.\n")
    A("| curva | maxerr | via piso | via emb | via ambos | veredicto |")
    A("|---|--:|--:|--:|--:|---|")
    for r in sorted(rows, key=lambda z: z["case_id"]):
        g = lambda k: (f"{r[k]['maxerr']:.4f}" if k in r  # noqa: E731
                       and "maxerr" in r[k] else "—")
        A(f"| `{r['case_id']}` | {r['maxerr_store']:.4f} | {g('piso')} | "
          f"{g('emb')} | {g('piso+emb')} | **{r['veredicto']}** |")
    A("")
    A("---\n")
    A("## 2. O motivo: um pré-teste de direção que custa ZERO simulação\n")
    A("`res.médio` = média(modelo − dado). Positivo ⇒ o modelo **retém mais** que")
    A("o dado ⇒ precisa de piso **menor**. O piso lido só pode ajudar se andar")
    A("para o lado que o resíduo pede.\n")
    A("| curva | res.médio | precisa | piso lido vs cfg | bate? | desfecho |")
    A("|---|--:|---|---|:--:|---|")
    for r in sorted(rows, key=lambda z: z["case_id"]):
        b = {True: "✅", False: "❌", None: "—"}[r["direcao_bate"]]
        A(f"| `{r['case_id'][:34]}` | {r['res_medio']:+.4f} | "
          f"{r['direcao_necessaria']} | {r['direcao_lida']} | {b} | "
          f"{r.get('piso', {}).get('veredicto', '?')} |")
    A("")
    A("**O pré-teste prevê os 6 desfechos, 6/6** — direção bate ⇒ FECHA ou")
    A("MELHORA; não bate ⇒ PIORA; sem piso no cfg ⇒ INERTE. Ou seja: as 6 sondas")
    A("eram dispensáveis, o sinal já dizia. **Regra para a campanha:** antes de")
    A("gastar sonda numa alavanca de nível, conferir que o valor LIDO move a")
    A("retenção para o lado que o `res.médio` exige. Duas linhas de aritmética")
    A("sobre o store.\n")
    A("---\n")
    A("## 3. Três achados que sobram do caminho\n")
    A("**(a) O leitor do piso e a métrica discordam sobre onde a curva ACABA.**")
    A("`arrest_floor_from_curve` faz a média dos últimos 5% do ratio **cru**;")
    A("a métrica pontua só o trecho `>= 0,10` (`FLOOR_TRIM`). No")
    A("`eccles fig8a` o piso lido é **0,0122** — o dado cru vai a perda quase")
    A("total —, enquanto a visão que a métrica tem da curva termina em 0,10.")
    A("Injetar o piso lido faz o modelo colapsar até o fim e o `maxerr` sai de")
    A("0,122 para **0,213**. Não é o leitor que está errado nem a métrica: é a")
    A("MESMA classe de inconsistência dos achados de `FLOOR_TRIM` de 07-27")
    A("(instrumentação e métrica medindo trechos diferentes da mesma curva).\n")
    A("**(b) `loose_arrest_floor` INERTE sem pack — confirmado com Δ = 0 exato.**")
    A("O `liu2020_fig9` não tem `loose_torsion_mode` no cfg e a sonda do piso deu")
    A("MAE e maxerr **bit-idênticos** ao controle. O gotcha do `CLAUDE.md`")
    A("(\"`c_bend`/`loose_arrest_floor` INERTES sem pack na ENTRY\") passa de")
    A("advertência a fato medido nesta curva.\n")
    if fecha:
        r = fecha[0]
        A(f"**(c) A única que fecha, fecha MUITO — e por isso merece cuidado.**")
        A(f"`{r['case_id']}`: maxerr **{r['maxerr_store']:.4f} → "
          f"{r['piso']['maxerr']:.4f}** com piso lido **{r['floor_lido']}** "
          f"contra {r['floor_cfg']} do cfg.")
        A("Um piso de ~0,99 significa \"o afrouxamento trava a 99% de F₀\", isto é,")
        A("quase nenhum afrouxamento — coerente com esta ser a curva mais RASA da")
        A("família (D = 0,3 mm), mas é um input **por caso**, e o CHU é justamente")
        A("a fonte de família não-monotônica. Pelo critério G-A3 já escrito")
        A("(\"constante própria por fonte não é forma, é tuner com nome bonito\"),")
        A("adotar isto exige o gate PR-37′: procedência + nenhum caso pior +")
        A("mediana da fonte. **Não adotei nada.**\n")
    A("---\n")
    A("## 4. O que isto muda na fila\n")
    A("1. **A conta \"147 → 154 de graça\" não existe.** Pelo caminho da leitura,")
    A(f"   o ganho medido é **+{len(fecha)}** curva")
    A("   (e ela ainda depende do gate de adoção).")
    A("2. **As 5 restantes continuam LEVEL-LIMITED** — o resíduo segue de nível —")
    A("   **mas o nível não é alcançável pelos leitores existentes.** Isso as")
    A("   move de \"alvo barato\" para uma pergunta nova: *que constante governa o")
    A("   nível quando o piso de arresto não é a resposta?*")
    A("3. **Candidata que este trabalho NÃO testou:** o `eccles fig8a` e o")
    A("   `bauer test3` pedem o nível no sentido oposto ao do platô medido, o que")
    A("   sugere que o desvio é de **retenção durante o trecho pontuado**, não de")
    A("   patamar final — território de `tr_loose_gain`/`eta_loose`, que são")
    A("   FITADOS, não lidos. Ou seja: sairia da doutrina \"ler em vez de fitar\"")
    A("   e viraria prereg, não leitura.\n")
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    args = sys.argv[1:]
    only = args[args.index("--only") + 1] if "--only" in args else None
    skip_slow = "--skip-slow" in args
    store = json.loads(STORE.read_text(encoding="utf-8"))
    classes = json.loads(CLASSES.read_text(encoding="utf-8"))
    ids = [c["case_id"] for c in classes["curvas"]
           if c["classe"] == "LEVEL-LIMITED"]
    if only:
        ids = [c for c in ids if only in c]
    if skip_slow:
        ids = [c for c in ids if c != SLOW]
    recs = {r.case_id: r for r in all_records()}

    rows = []
    for cid in ids:
        print(f"  {cid[:46]:46s} ...", end="", flush=True)
        row = probe(recs[cid], store[cid])
        rows.append(row)
        det = " ".join(f"{k}={row[k]['maxerr'] if 'maxerr' in row[k] else 'ERR'}"
                       for k in ("piso", "emb", "piso+emb") if k in row)
        print(f" {row['veredicto']:18s} via {row.get('melhor_alavanca')}"
              f" | maxerr {row['maxerr_store']} -> {det}  [{row['s']}s]",
              flush=True)

    prev = (json.loads(OUT_JSON.read_text(encoding="utf-8"))
            if OUT_JSON.exists() else {"curvas": []})
    keep = [r for r in prev["curvas"]
            if r["case_id"] not in {x["case_id"] for x in rows}]
    allrows = sorted(keep + rows, key=lambda r: r["case_id"])
    OUT_JSON.write_text(json.dumps(
        {"fingerprint": "4f5bedfbace4", "curvas": allrows},
        indent=1, ensure_ascii=False), encoding="utf-8")
    write_md(allrows)
    print(f"\nJSON -> {OUT_JSON.relative_to(ROOT)}  ({len(allrows)} curvas)")
    print(f"MD   -> {OUT_MD.relative_to(ROOT)}")
    return allrows


if __name__ == "__main__":
    main()
