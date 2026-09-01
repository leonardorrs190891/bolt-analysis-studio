# -*- coding: utf-8 -*-
"""ORQUESTRADOR dos geradores de relatorios HTML do BAS V2.

Roda, na ordem correta, os geradores de HTML do projeto (New_Theory/generate_*.py
+ convergence_indicator.py) via subprocess, com carimbo de frescor (data + hash
git curto) no fim. Descobre os geradores DINAMICAMENTE (glob) — um novo
generate_*.py e' pego automaticamente.

Ordem: primeiro o que PRODUZ um JSON insumo (generate_theta_gallery.py escreve
theta_gallery.json e computa o engine ~1-2 min), depois os CONSUMIDORES dos JSONs
canonicos (report_data.json, transverse_provenance.json, axial_emb_provenance.json,
sensitivity_study.json), e por fim convergence_indicator.py (dashboard + carimbo).

IMPORTANTE — insumos NAO sao regenerados aqui: os JSONs canonicos sao produzidos
por scripts SEPARADOS (ver INSUMO_PRODUCER: transverse_provenance.py,
axial_emb_provenance.py, sensitivity_study.py; report_data.json e' mantido pelos
scripts de adocao). Se um insumo faltar, o gerador FALHA e este orquestrador
REPORTA claramente (com o produtor sugerido) — nada de degradacao silenciosa.

Falha RUIDOSA: se qualquer gerador quebrar, o resumo marca FALHOU e o processo
sai com codigo != 0. convergence_indicator.py e' o unico caso especial — rc=3
significa "nao convergiu" (status normal, dashboard escrito), tratado como OK.

EFEITO COLATERAL: convergence_indicator.py APENDE uma entrada ao
convergence_ledger.json a cada execucao. Use --skip convergence_indicator para
evitar isso.

Uso:
  python New_Theory/build_reports.py                 # roda todos, na ordem
  python New_Theory/build_reports.py --list          # mostra o plano e sai
  python New_Theory/build_reports.py --only generate_validation_html
  python New_Theory/build_reports.py --skip generate_theta_gallery,convergence_indicator
  python New_Theory/build_reports.py --timeout 300   # timeout por gerador (s)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_THEORY = ROOT / "New_Theory"

# metadados por gerador CONHECIDO (prioridade menor roda antes). Geradores
# descobertos e nao listados aqui recebem prioridade 50 (banda do meio).
#   prio      -> ordem de execucao
#   desc      -> descricao curta
#   insumo    -> de onde le
#   out       -> saida primaria
#   args      -> argumentos extra de linha de comando
#   ok_codes  -> return codes tratados como sucesso (default (0,))
META = {
    "generate_theta_gallery.py": dict(
        prio=0, desc="galeria theta(N) - PRODUZ theta_gallery.json (computa engine ~1-2 min)",
        insumo="import theta_confront (harness canonico)",
        out="theta_gallery.json + validation_html/theta_loosening.html"),
    "generate_validation_html.py": dict(
        prio=10, desc="pagina standalone por-caso + index",
        insumo="report_data.json", out="validation_html/*.html"),
    "generate_case_reports.py": dict(
        prio=11, desc="reports individuais completos + indice mestre",
        insumo="report_data.json + adopted_configs.json + DIGITIZED_CASES",
        out="validation_html/reports/*.html + validation_report.html"),
    "generate_loosening_explorer.py": dict(
        prio=12, desc="explorador single-page das curvas de loosening",
        insumo="report_data.json", out="validation_html/loosening_explorer.html"),
    "generate_database_html.py": dict(
        prio=13, desc="indice navegavel do database de curvas",
        insumo="report_data.json + curve_library/", out="validation_html/database.html"),
    "generate_variables_html.py": dict(
        prio=14, desc="inventario de variaveis (introspeccao das dataclasses)",
        insumo="engine (dataclasses)", out="validation_html/variables.html"),
    "generate_transverse_gallery.py": dict(
        prio=15, desc="galeria transversal dado x modelo (com erros)",
        insumo="transverse_provenance.json", out="validation_html/transverse_provenance.html"),
    "generate_axial_emb_html.py": dict(
        prio=16, desc="galeria axial embedding-provenance (com erros)",
        insumo="axial_emb_provenance.json", out="validation_html/axial_emb_provenance.html"),
    "generate_sensitivity_html.py": dict(
        prio=17, desc="pagina de sensibilidade + inventario + reducao de DOF",
        insumo="sensitivity_study.json", out="validation_html/sensitivity.html"),
    "convergence_indicator.py": dict(
        prio=90, desc="indicador de convergencia + dashboard (APENDE ao ledger)",
        insumo="report_data.json",
        out="validation_html/dashboard.html + convergence_ledger.json",
        args=["--note", "build_reports"], ok_codes=(0, 3)),
}

# insumo JSON -> como (re)gera-lo (para o hint de 'insumo ausente')
INSUMO_PRODUCER = {
    "report_data.json": "mantido pelos scripts de adocao (rho_engine_adopt / "
                        "hdpe_adopt / lu_fig20_refit / zhang_* / liu2022_fig5_cases) "
                        "— deveria estar versionado",
    "transverse_provenance.json": "python New_Theory/transverse_provenance.py",
    "axial_emb_provenance.json": "python New_Theory/axial_emb_provenance.py",
    "sensitivity_study.json": "python New_Theory/sensitivity_study.py",
    "theta_gallery.json": "python New_Theory/generate_theta_gallery.py",
    "adopted_configs.json": "escrito pelas campanhas (base de conhecimento)",
}


def _stem(name: str) -> str:
    return name[:-3] if name.endswith(".py") else name


def discover():
    """Descobre os geradores: New_Theory/generate_*.py + convergence_indicator.py.
    Ordena por prioridade conhecida (default 50), depois por nome."""
    names = {p.name for p in NEW_THEORY.glob("generate_*.py")}
    if (NEW_THEORY / "convergence_indicator.py").exists():
        names.add("convergence_indicator.py")
    return sorted(names, key=lambda n: (META.get(n, {}).get("prio", 50), n))


def git_hash() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT),
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else "(sem git)"
    except Exception as e:                                   # git ausente/erro
        return f"(git indisponivel: {e})"


def run_one(name: str, timeout: int) -> dict:
    meta = META.get(name, {})
    cmd = [sys.executable, str(NEW_THEORY / name)] + list(meta.get("args", []))
    # forca UTF-8 no filho (evita UnicodeEncodeError em stdout no Windows/cp1252)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=env)
        ok = r.returncode in meta.get("ok_codes", (0,))
        return dict(name=name, ok=ok, rc=r.returncode, dt=time.time() - t0,
                    stdout=r.stdout or "", stderr=r.stderr or "")
    except subprocess.TimeoutExpired as e:
        out = e.stdout if isinstance(e.stdout, str) else ""
        return dict(name=name, ok=False, rc=None, dt=time.time() - t0,
                    stdout=out or "", stderr=f"TIMEOUT apos {timeout}s")
    except Exception as e:                                   # falha ao lancar
        return dict(name=name, ok=False, rc=None, dt=time.time() - t0,
                    stdout="", stderr=f"EXCECAO ao lancar: {e!r}")


def insumo_hint(res: dict):
    txt = (res.get("stderr") or "") + (res.get("stdout") or "")
    if not any(t in txt for t in ("FileNotFoundError", "No such file", "Errno 2")):
        return []
    return [f"insumo ausente '{insumo}' -> (re)gere com: {producer}"
            for insumo, producer in INSUMO_PRODUCER.items() if insumo in txt]


def _tail(s: str, n: int) -> str:
    return "\n".join((s or "").strip().splitlines()[-n:])


def main() -> int:
    # o filho pode imprimir unicode (▮, acentos); ao re-imprimir os tails no
    # console do pai (cp1252 no Windows) isso quebraria — forca UTF-8 na saida.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")             # py3.7+
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="Orquestra os geradores de relatorios HTML do BAS V2.")
    ap.add_argument("--list", action="store_true", help="mostra o plano e sai")
    ap.add_argument("--only", default="",
                    help="roda SO estes (nomes por virgula, com/sem .py)")
    ap.add_argument("--skip", default="",
                    help="PULA estes (nomes por virgula, com/sem .py)")
    ap.add_argument("--timeout", type=int, default=1200,
                    help="timeout por gerador em segundos (default 1200)")
    args = ap.parse_args()

    def norm(s):
        return {_stem(x.strip()) for x in s.split(",") if x.strip()}
    only, skip = norm(args.only), norm(args.skip)

    plan = discover()
    if only:
        plan = [n for n in plan if _stem(n) in only]
    if skip:
        plan = [n for n in plan if _stem(n) not in skip]
    if not plan:
        print("Nada a rodar (--only/--skip nao casaram com nenhum gerador).",
              file=sys.stderr)
        return 2

    bar = "=" * 74
    print(bar)
    print(f"BAS V2 - build_reports  |  {len(plan)} geradores  |  raiz={ROOT}")
    print(bar)
    for i, n in enumerate(plan, 1):
        m = META.get(n, {})
        print(f"  {i:2d}. {n:33s} {m.get('desc', '(descoberto - sem metadados)')}")
        print(f"      insumo: {m.get('insumo', '?')}")
        print(f"      saida : {m.get('out', '?')}")
    if args.list:
        print("\n(--list: nada foi executado)")
        return 0

    print("\nExecutando...\n")
    results = []
    for n in plan:
        print(f"[ RUN  ] {n} ...", flush=True)
        res = run_one(n, args.timeout)
        results.append(res)
        print(f"[{'  OK  ' if res['ok'] else 'FALHOU'}] {n}  "
              f"({res['dt']:.1f}s, rc={res['rc']})")
        if res["ok"]:
            body = _tail(res["stdout"], 3)
            for ln in body.splitlines():
                print("   | " + ln)
        else:
            print("  --- stderr (tail) ---")
            for ln in _tail(res["stderr"], 15).splitlines():
                print("   " + ln)
            for h in insumo_hint(res):
                print("  HINT: " + h)
        print("", flush=True)

    # ---- resumo + carimbo de frescor ----
    ok_all = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    print(bar)
    print("RESUMO")
    print(bar)
    for r in results:
        print(f"  [{'  OK  ' if r['ok'] else 'FALHOU'}] {r['name']:33s} "
              f"{r['dt']:7.1f}s  rc={r['rc']}")
    print("-" * 74)
    print(f"  {len(ok_all)}/{len(results)} OK   |   carimbo: "
          f"{time.strftime('%Y-%m-%d %H:%M:%S')}   |   git {git_hash()}")
    print(bar)

    if bad:
        print(f"\nFALHA: {len(bad)} gerador(es) quebraram: "
              + ", ".join(r["name"] for r in bad), file=sys.stderr)
        return 1
    print("\nTodos os geradores concluiram com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
