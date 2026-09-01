# MEM Iteração 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline). Steps em checkbox `- [ ]`.

**Goal:** Primeira iteração da Metodologia de Evolução do Modelo (spec `2026-07-10-model-evolution-methodology-design.md`): tooling de diagnóstico (`error_budget` + painel do ledger + METHODOLOGY.md) e o **Sprint de Adoção** — promover ao canônico, com classe de procedência por constante, o que as regras permitem dos 35 casos do gap; meta mediana 0.181 → ≤ 0.10.

**Architecture:** `error_budget.py` classifica cada caso por heurísticas auditáveis e grava JSON + alimenta seção nova no mestre; o painel do ledger plota `convergence_ledger.json` com o BASCHART existente. O Sprint exige um mecanismo novo pequeno: **matching de config adotada por GRUPO** (chave `FONTE_token` aplica quando os tokens extras aparecem no case_id — resolve Bauer fig6/fig8, Liu2022 dry/oil, Icmez lk*), e então promoções = edições no `adopted_configs.json` (campanha escreve) com bloco `prov` por constante.

**Tech Stack:** stdlib+numpy; BASCHART já embutido; sem libs novas.

## Global Constraints

- `utf-8`, `ast.parse`, commit por tarefa, `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; não tocar engine; foreign files intactos.
- **Regras de promoção da spec §4 são LEI**: promove `lido-do-dado`, `fitado-this-rig` no DOF legítimo, `input de paper/estudo`; NÃO promove fit per-curva sem feature; forma nova não entra nesta iteração.
- Toda promoção: entrada no `adopted_configs.json` com `"prov": {constante: classe}` + justificativa; medição por fonte ANTES/DEPOIS; o que não promover recebe rótulo e motivo no orçamento.
- Fatos verificados: ledger = lista de entradas `{max, mean, median, n, n_above_bound, note, per_source, ts}`; gap por fonte: BAUER 8 (labels "CONTINUUM s_crit §4.33"), LIU_2022_RETIGHT 16 ("running-in wear k=5/N=100 + mu=0.2 dry / 0.1 oil §4.29"), LIU_2025 4 (label truncado — investigar), ROUSSEAU 6 (steel "pack + emb fino" → c_bend 0.3 do §4.12; HDPE multi-objetivo c/ campos de harness), LI_2022TI 1 (cauda de fratura out-of-model).
- Baseline congelado (2026-07-10): canônico mediana **0.1808** média 0.2124 (n=114); campanha mediana 0.0417.

## File Structure

**Create:** `src/bolt_analysis_studio/validation/error_budget.py`, `src/bolt_analysis_studio/docs/METHODOLOGY.md`, `tests/test_error_budget.py`.
**Modify:** `validation/report_html.py` (seção orçamento + painel ledger no mestre), `validation/runner.py` (`_adopted_for` por grupo), `gui/documentation_tab.py` (§18), `CLAUDE.md` (ponteiro), `New_Theory/adopted_configs.json` (promoções — Task 4), `New_Theory/convergence_ledger.json` (append — Task 5), `tests/test_validation_runner.py` (matching por grupo).

---

## Task 1: `error_budget.py` — classificador do orçamento de erro

**Files:**
- Create: `src/bolt_analysis_studio/validation/error_budget.py`
- Test: `tests/test_error_budget.py`

**Interfaces:**
- Consumes: `case_registry.all_records`, `store.ValidationStore`, `report_html.floor_of/data_points`, `inputs.inputs_for`.
- Produces: `classify_case(rec, result) -> dict` (`{label, sublabels, evidence}` com `label ∈ {no_piso, gap_adocao, nivel, forma, sem_simulacao}`); `error_budget(store=None) -> dict` (`{cases: {id: …}, by_source: {src: {label: n}}, totals}`), grava `Models/CALIBRATION_AND_VALIDATION/error_budget.json`; CLI `python -m bolt_analysis_studio.validation.error_budget`.

- [ ] **Step 1: Teste falhando** `tests/test_error_budget.py`:

```python
def _res(case_id, mae, cycles=None, ratio=None, final_pred=0.9, final_data=0.85):
    from bolt_analysis_studio.validation.runner import CaseResult
    return CaseResult(case_id=case_id, ok=True, mae=mae,
                      cycles=cycles or [0, 500, 1000],
                      ratio=ratio or [1.0, 0.95, 0.90],
                      final_pred=final_pred, final_data=final_data,
                      generated_at="t", engine_fingerprint="f")


def test_classify_labels():
    from bolt_analysis_studio.validation.case_registry import all_records, record
    from bolt_analysis_studio.validation.error_budget import classify_case
    recs = [r for r in all_records() if r.source != "USER"]
    # no_piso: caso YANG (piso 0.081) com mae 0.09
    yang = next(r for r in recs if r.source == "YANG_2019")
    assert classify_case(yang, _res(yang.case_id, 0.09))["label"] == "no_piso"
    # gap_adocao: galeria 0.03, canonico 0.25
    gal = next(r for r in recs if r.gallery_entry is not None
               and float(r.gallery_entry["mae"]) < 0.05)
    c = classify_case(gal, _res(gal.case_id,
                                max(2.5 * float(gal.gallery_entry["mae"]), 0.12)))
    assert c["label"] == "gap_adocao"
    # sem_simulacao
    other = next(r for r in recs if r.family == "other")
    from bolt_analysis_studio.validation.runner import CaseResult
    bad = CaseResult(case_id=other.case_id, ok=False, error="x",
                     generated_at="t", engine_fingerprint="f")
    assert classify_case(other, bad)["label"] == "sem_simulacao"


def test_budget_aggregates_and_writes(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import error_budget as eb
    monkeypatch.setattr(eb, "BUDGET_PATH", tmp_path / "eb.json")
    out = eb.error_budget()
    assert out["totals"]["n"] >= 114
    assert sum(sum(v.values()) for v in out["by_source"].values()) == out["totals"]["n"]
    assert (tmp_path / "eb.json").exists()
    import json
    saved = json.loads((tmp_path / "eb.json").read_text(encoding="utf-8"))
    assert saved["totals"] == out["totals"]
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `error_budget.py`:

```python
# -*- coding: utf-8 -*-
"""Orcamento de erro (MEM Etapa 1, spec 2026-07-10-model-evolution §3):
classifica cada caso por heuristicas AUDITAVEIS antes de qualquer mexida.
Rotulos: no_piso | gap_adocao | nivel | forma | sem_simulacao.
Campanhas LEEM este JSON p/ escolher a alavanca (hierarquia da Etapa 2)."""
from __future__ import annotations

import json
from typing import Optional

import numpy as np

from .case_registry import CaseRecord, all_records
from .inputs import inputs_for, repo_root
from .report_html import data_points, floor_of
from .runner import CaseResult
from .store import ValidationStore

BUDGET_PATH = repo_root() / "Models" / "CALIBRATION_AND_VALIDATION" / "error_budget.json"
ALVO = 0.10          # alvo por caso quando nao ha piso medido (spec Etapa 4)


def classify_case(rec: CaseRecord, result: Optional[CaseResult]) -> dict:
    if result is None or not result.ok:
        return {"label": "sem_simulacao",
                "evidence": (result.error if result else "nunca simulado")}
    if result.mae is None:
        return {"label": "no_piso",
                "evidence": "sem curva (comparação pontual do ratio final)"}
    floor = floor_of(rec.source, rec.case_id)
    lim = max(floor + 0.02, ALVO)
    if result.mae <= lim:
        return {"label": "no_piso",
                "evidence": f"mae {result.mae:.3f} <= max(piso+0.02, {ALVO})={lim:.3f}"}
    sub = []
    try:
        n_assumed = sum(1 for v in inputs_for(rec.validation_case).values()
                        if v.get("prov") == "assumed")
        if n_assumed:
            sub.append(f"{n_assumed} inputs 'assumed' (µ domina o OAT §4.42)")
    except Exception:
        pass
    if rec.gallery_entry is not None:
        g = float(rec.gallery_entry["mae"])
        if result.mae > max(2 * g, g + 0.05):
            return {"label": "gap_adocao", "sublabels": sub,
                    "evidence": f"canônico {result.mae:.3f} vs campanha {g:.3f} "
                                f"({rec.gallery_entry.get('label', '')[:60]})"}
    # nivel vs forma: residuo de um sinal so + estagios ~uniformes => nivel
    try:
        dx, dy = data_points(rec)
        mx = np.asarray(result.cycles, float)
        my = np.asarray(result.ratio, float)
        resid = np.interp(dx, mx, my) - np.asarray(dy)
        frac_over = float((resid > 0).mean())
        one_sided = frac_over > 0.8 or frac_over < 0.2
    except Exception:
        one_sided = abs((result.final_pred or 0) - (result.final_data or 0)) > 0.05
    label = "nivel" if one_sided else "forma"
    ev = ("resíduo de um sinal só (curva certa, nível errado — alavanca: "
          "constante/input per-rig)" if one_sided else
          "resíduo cruza zero (forma errada — candidato a falsificação)")
    return {"label": label, "sublabels": sub, "evidence": ev}


def error_budget(store: Optional[ValidationStore] = None) -> dict:
    store = store or ValidationStore()
    cases, by_source = {}, {}
    for rec in all_records():
        if rec.source == "USER":
            continue
        c = classify_case(rec, store.get(rec.case_id))
        cases[rec.case_id] = dict(c, source=rec.source, family=rec.family)
        by_source.setdefault(rec.source, {}).setdefault(c["label"], 0)
        by_source[rec.source][c["label"]] += 1
    totals = {"n": len(cases)}
    for c in cases.values():
        totals.setdefault(c["label"], 0)
        totals[c["label"]] += 1
    out = {"cases": cases, "by_source": by_source, "totals": totals}
    BUDGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    BUDGET_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                           encoding="utf-8")
    return out


def main() -> int:
    out = error_budget()
    print(f"orçamento: {out['totals']}")
    for src, d in sorted(out["by_source"].items()):
        print(f"  {src:20s} {d}")
    print(f"gravado em {BUDGET_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_error_budget.py -q; echo EXIT=$?` → **2 passed, EXIT=0**.
- [ ] **Step 5: Commit** — `git commit -m "feat(mem): error_budget — classificador auditavel do orcamento de erro (Etapa 1)"`

---

## Task 2: Mestre — seção "Orçamento de erro" + painel do ledger

**Files:**
- Modify: `src/bolt_analysis_studio/validation/report_html.py` (master_report_html)
- Test: `tests/test_validation_report_html.py` (append)

**Interfaces:**
- Consumes: `error_budget.BUDGET_PATH` (lê o JSON se existir), `convergence_ledger.json` (lista), `_chart_div` (BASCHART).
- Produces: seção `<h2>Orçamento de erro (MEM)</h2>` com tabela fonte×rótulo; seção `<h2>Convergência (ledger)</h2>` com gráfico lines (média e mediana por iteração).

- [ ] **Step 1: Teste falhando** — append:

```python
def test_master_has_budget_and_ledger_sections(qapp, tmp_path, monkeypatch):
    import json
    from bolt_analysis_studio.validation import error_budget as eb
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import master_report_html
    monkeypatch.setattr(eb, "BUDGET_PATH", tmp_path / "eb.json")
    eb.error_budget()                              # gera o JSON que o mestre le
    monkeypatch.setattr(
        "bolt_analysis_studio.validation.report_html._budget_path",
        lambda: tmp_path / "eb.json")
    rec = next(r for r in all_records() if r.case_class == "full_curve")
    master = master_report_html([rec], {rec.case_id: _fake_result(rec.case_id)})
    assert "Orçamento de erro" in master
    assert "gap_adocao" in master or "gap de adoção" in master
    assert "Convergência (ledger)" in master       # painel do ledger
    assert master.count("BASCHART v1") == 1        # mestre agora carrega o renderer
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** em `report_html.py`:

**(a)** helpers (junto dos outros privados):

```python
def _budget_path():
    return repo_root() / "Models" / "CALIBRATION_AND_VALIDATION" / "error_budget.json"


_BUDGET_LABELS = ("no_piso", "gap_adocao", "nivel", "forma", "sem_simulacao")


def _budget_section() -> str:
    p = _budget_path()
    if not p.exists():
        return ""
    try:
        b = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    hdr = "".join(f"<th>{l}</th>" for l in _BUDGET_LABELS)
    rows = "".join(
        f'<tr><td>{NICE.get(src, src)}</td>' + "".join(
            f'<td>{d.get(l, 0) or ""}</td>' for l in _BUDGET_LABELS) + "</tr>"
        for src, d in sorted(b.get("by_source", {}).items()))
    tot = b.get("totals", {})
    tots = " · ".join(f"{l}: <b>{tot.get(l, 0)}</b>" for l in _BUDGET_LABELS)
    return (f'<h2>Orçamento de erro (MEM)</h2>'
            f'<p class="sub2">classificação auditável ANTES de mexer '
            f'(metodologia 2026-07-10): {tots}</p>'
            f'<div class="ovx"><table class="idx"><thead><tr><th>fonte</th>{hdr}'
            f'</tr></thead><tbody>{rows}</tbody></table></div>')


def _ledger_section() -> str:
    p = repo_root() / "New_Theory" / "convergence_ledger.json"
    if not p.exists():
        return ""
    try:
        led = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(led, list) or len(led) < 2:
        return ""
    xs = list(range(1, len(led) + 1))
    mean = [float(e.get("mean", 0)) for e in led]
    med = [float(e.get("median", 0)) for e in led]
    chart = _chart_div(dict(
        type="lines", h=220, xlabel="iteração da campanha",
        ylabel="MAE global", name="convergencia_ledger",
        series=[dict(name="média", color="var(--di)", x=xs, y=mean),
                dict(name="mediana", color="var(--good)", x=xs, y=med)]))
    last = led[-1]
    return (f'<h2>Convergência (ledger)</h2>{chart}'
            f'<p class="sub2">{len(led)} iterações · última: média '
            f'{float(last.get("mean", 0)):.4f} · mediana '
            f'{float(last.get("median", 0)):.4f} · '
            f'{last.get("note", "")[:120]}</p>')
```

**(b)** em `master_report_html`, injetar `{_budget_section()}{_ledger_section()}`
logo após o bloco `head` (antes das tabelas por fonte) e adicionar
`{_CHART_JS}` antes de `{_MASTER_JS}` no fim do template do mestre.

- [ ] **Step 4: `ast.parse` + rodar** — suíte do report verde (`echo EXIT=$?`).
- [ ] **Step 5: Commit** — `git commit -m "feat(mem): mestre com orcamento de erro + painel do ledger (BASCHART)"`

---

## Task 3: `METHODOLOGY.md` + aba Documentation §18 + CLAUDE.md

- [ ] **Step 1: Teste falhando** — append em `tests/test_validation_docs_library.py`:

```python
def test_methodology_doc_exists():
    from pathlib import Path
    md = Path("src/bolt_analysis_studio/docs/METHODOLOGY.md").read_text(encoding="utf-8")
    for termo in ("Orçamento de erro", "gap_adocao", "lido-do-dado",
                  "falsificação", "piso", "error_budget"):
        assert termo in md, termo


def test_documentation_tab_has_methodology_section():
    from bolt_analysis_studio.gui.documentation_tab import DOCUMENTATION
    key = next((k for k in DOCUMENTATION if "methodology" in k.lower()
                or "metodolog" in k.lower()), None)
    assert key is not None and "18." in DOCUMENTATION[key]["title"]
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Escrever** `src/bolt_analysis_studio/docs/METHODOLOGY.md` — a spec
  §3-§5 operacionalizada como runbook (o ciclo, as regras de promoção como
  tabela, o comando de cada etapa: `error_budget` → alavanca → `--all` →
  ledger; guard-rails; critérios de parada; papel campanha-escreve/software-lê)
  + seção 18 na aba Documentation (resumo + comandos) + linha no CLAUDE.md
  (Reference docs) apontando p/ METHODOLOGY.md e a spec.
- [ ] **Step 4: Rodar** os testes de docs → verde.
- [ ] **Step 5: Commit** — `git commit -m "docs(mem): METHODOLOGY.md na biblioteca + secao 18 + ponteiro CLAUDE.md"`

---

## Task 4: Sprint de Adoção (a campanha da iteração 1)

**Mecanismo primeiro, promoções depois; medição por fonte a cada promoção.**

- [ ] **Step 4a: Matching por grupo no runner** (TDD). Teste (append em `tests/test_validation_runner.py`):

```python
def test_adopted_matching_by_group_tokens():
    from bolt_analysis_studio.validation.runner import _adopted_for
    # tokens extras da chave devem aparecer no case_id
    assert _adopted_for("BAUER_2024", "bauer2024_M8_fig6_rep2") != "BAUER_2024_fig8"
    # lk19p8 nao pode mais vazar p/ casos lk13p8
    got = _adopted_for("ICMEZ_2025", "demir2024_amp0p4_F17p6_lk13p8")
    assert got is None or "lk19p8" not in got
```

Implementação em `runner.py` — substituir `_adopted_for` por matching por
tokens: a chave casa se `source` é prefixo (case-insensitive) E todo token
extra da chave (após remover o prefixo) aparece no `case_id.lower()`;
empate → mais tokens casados vence; sem grupo → chave exata da fonte.

```python
def _adopted_for(source: str, case_id: str = ""):
    adopted = kb.adopted_sources()
    if "hdpe" in case_id.lower() and "ROUSSEAU_HDPE" in adopted:
        return "ROUSSEAU_HDPE"
    cid = case_id.lower()
    best, best_score = None, -1
    for s in adopted:
        sl, srcl = s.lower(), source.lower()
        pref = _common_prefix_len(srcl, sl)
        if pref < min(len(srcl), 4):              # exige prefixo real da fonte
            continue
        extra = [t for t in sl[pref:].split("_") if t]
        if any(t not in cid for t in extra):
            continue                              # grupo nao casa com o caso
        score = pref * 10 + len(extra)            # prefixo domina; grupo desempata
        if score > best_score:
            best, best_score = s, score
    return best
```

Rodar `tests/test_validation_runner.py` inteiro (paridade liu2025 intacta) e commitar:
`git commit -m "feat(mem): matching de config adotada por GRUPO (FONTE_token)"`.

- [ ] **Step 4b: Rodar o orçamento** — `PYTHONPATH=src python -m bolt_analysis_studio.validation.error_budget` e registrar a distribuição (esperado: gap_adocao ≈ 35).

- [ ] **Step 4c: Promoções, fonte a fonte** (editar `New_Theory/adopted_configs.json`; cada entrada ganha `"prov": {...}` e `"verdict"` citando a classe; medir a fonte com `--case`/batch parcial após cada uma):
  1. **BAUER_2024** — achatar a cfg aninhada em grupos: `BAUER_2024_fig6` (dano contínuo compartilhado §4.33: k_partial_slip 0.5, c_D 10, dmg_gross_exp 3.0, k_dmg_wear 6, k_dmg_mu 3 + c_bend 0.5) e `BAUER_2024_fig8_test1` (emb_um 0.5, c_bend 0.5, c_D 30, dmg_gross_exp 2.5 + bloco compartilhado) e `BAUER_2024_fig8` (test2/test3: emb_um 4.0, c_bend 0.3, c_D 8, dmg_gross_exp 2.5 + bloco). Classes: dano contínuo = constantes da forma validada §4.33 (fitado-this-rig, compartilhado no rig); c_bend = DOF legítimo; emb per-espectro = fitado-this-rig (grupo de protocolo). Remover a entrada aninhada antiga.
  2. **LIU_2022 dry/oil** — grupos `LIU_2022_dry` (mu_thread/mu_bearing 0.2) e `LIU_2022_oil` (0.1) por cima da cfg existente (running-in k_wear_running 5/N_wear_run 100 já adotada); classe: input do estudo §4.29 (µ por estado de lubrificação). Cobrem os 16 fig5 (RETIGHT casa LIU_2022_RET como antes — tokens “ret”? conferir stems fig9/10; se necessário, grupo `LIU_2022_fig5_dry/oil`).
  3. **ROUSSEAU_2025 (steel)** — adicionar `c_bend: 0.3` (fitado-this-rig §4.12) à cfg.
  4. **LIU_2025** — comparar config canônica vs label completo da galeria nos amp0p4-0p8 (imprimir `gallery_entry["label"]` inteiro); promover SÓ o que tiver classe (suspeita: o fit conjunto usou k_ratchet/W distintos por amplitude — se for per-curva sem feature, NÃO promove; registrar no orçamento).
  5. **ROUSSEAU_HDPE** — conferir se `k_member_shear` existe em `JointMaterial`; se sim, mapear GA_member→k_member_shear com a regra documentada e promover; F_eff stack-limited continua fora (forma no harness) — rotular resíduo.
  6. **li2022ti full** — NÃO promover (cauda de fratura out-of-model); rótulo `forma` com nota "trim de fratura pré-registrado = candidato da iteração 2".
  Gate por fonte: mediana da fonte melhora e NENHUMA outra fonte piora > 0.005 (rodar `--resume` após limpar só os casos afetados, ou batch completo no 4d).

- [ ] **Step 4d: Batch completo + medição** — `rm validation_store.json` + `--all` (background com `--resume` como no Plano A); comparar: mediana global ANTES 0.1808 → DEPOIS (meta ≤ 0.10); por fonte; re-rodar `error_budget` (gap_adocao deve despencar; resíduo rotulado).
- [ ] **Step 4e: Regenerar reports + commit** — `git commit -m "feat(mem): Sprint de Adocao — promocoes com classe de procedencia (iteracao 1)"` (inclui adopted_configs.json, store, reports, error_budget.json).

---

## Task 5: Ledger + STATUS + memória

- [ ] **Step 1: Apend no ledger** (formato existente): entrada com `mean/median/max/n/n_above_bound/per_source/ts` do batch novo e `note` = "MEM iteracao 1 (sprint de adocao): promocoes com classe de procedencia; mediana 0.181->X".
- [ ] **Step 2: STATUS** `docs/superpowers/plans/2026-07-10-mem-iteration-1-STATUS.md`: números antes/depois (global + por fonte), tabela de promoções (constante → classe → efeito), o que NÃO foi promovido e por quê, próximos alvos da iteração 2 (trim de fratura pré-registrado; liu2025 se ficou; inputs assumed→paper; formas do funil).
- [ ] **Step 3: Memória + CLAUDE.md** (baseline novo do canônico) + commit final.

---

## Self-Review

**Spec coverage:** Etapa 1 (Task 1-2), doc vivo (Task 3), Sprint §6 (Task 4), ledger/registro Etapa 5 (Task 5), regras de promoção §4 aplicadas com classes explícitas (Task 4c). ✔
**Placeholder scan:** Task 4c é procedural POR DESIGN (valores saem dos dados/labels na execução — é campanha, não código); cada sub-passo tem ação, fonte do valor e gate de medição. Sem TBDs. ✔
**Type consistency:** `classify_case(rec, result)->dict` (T1) usado no budget e implicitamente no mestre via JSON; `_budget_path()`/`_budget_section()`/`_ledger_section()` (T2) chamados no master; `_adopted_for(source, case_id)` assinatura preservada (T4a). ✔
**Riscos:** (a) matching por grupo pode mudar casos já bons (Icmez lk13p8 perde a cfg lk19p8) — gate do 4c exige nenhuma fonte piorar >0.005; se Icmez piorar, adicionar entrada base `ICMEZ_2025` com a mesma cfg; (b) paridade liu2025 amp0p25 é o canário (bit-exato deve permanecer); (c) meta ≤0.10 é META, não promessa — o STATUS reporta o que as regras permitiram.
