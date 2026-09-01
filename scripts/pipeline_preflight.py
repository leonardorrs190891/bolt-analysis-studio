# -*- coding: utf-8 -*-
"""PREFLIGHT do pipeline de otimizacao — falha RAPIDO, antes das horas de execucao.

Atividade G pre-pipeline (2026-07-29). O pipeline roda longo e sem supervisao;
uma condicao ausente descoberta as 3 horas de execucao custa a execucao inteira.
Este script verifica, em segundos, tudo de que ele depende — e imprime o motivo
de cada falha, nao so um codigo de saida.

Cada check e' UMA pergunta com resposta verificavel. Nenhum simula; nenhum
escreve. Uso:

    py -3.12 scripts/pipeline_preflight.py            # texto
    py -3.12 scripts/pipeline_preflight.py --json     # p/ consumo automatico

Sai 0 se todos os OBRIGATORIOS passam (avisos nao derrubam), 1 caso contrario.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

RES: list[dict] = []


def check(nome: str, obrigatorio: bool = True):
    """Decorator: registra o resultado e a razao, sem deixar excecao escapar."""
    def deco(fn):
        try:
            ok, detalhe = fn()
        except Exception as exc:                                # noqa: BLE001
            ok, detalhe = False, f"{type(exc).__name__}: {exc}"
        RES.append(dict(nome=nome, ok=bool(ok), obrigatorio=obrigatorio,
                        detalhe=str(detalhe)))
        return fn
    return deco


# ---------------------------------------------------------------- interpretador
@check("interpretador tem as dependencias")
def _dep():
    faltam = []
    for m in ("numpy", "pytest"):
        try:
            __import__(m)
        except ImportError:
            faltam.append(m)
    if faltam:
        return False, (f"faltam {faltam} — o `python` do PATH e' um 3.13 pelado; "
                       "use `py -3.12`")
    import numpy
    return True, f"numpy {numpy.__version__} · python {sys.version.split()[0]}"


# ---------------------------------------------------------------------- store
@check("store canonico: uniforme e completo")
def _store():
    p = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
    if not p.exists():
        return False, "ausente"
    d = json.loads(p.read_text(encoding="utf-8"))
    fps = {r.get("engine_fingerprint") for r in d.values()}
    sem_ok = [c for c, r in d.items() if not r.get("ok")]
    if len(fps) != 1:
        return False, f"{len(fps)} fingerprints distintos: {sorted(fps)}"
    return True, (f"{len(d)} registros · fingerprint unico {fps.pop()} · "
                  f"{len(sem_ok)} com ok=False")


@check("store bate com o fingerprint do engine AGORA")
def _fp():
    from bolt_analysis_studio.validation.runner import engine_fingerprint
    p = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    do_store = next(iter({r.get("engine_fingerprint") for r in d.values()}))
    agora = engine_fingerprint()
    if do_store != agora:
        return False, (f"store diz {do_store}, engine diz {agora} — alguma config "
                       "foi adotada sem re-carimbar; re-simule antes do pipeline")
    return True, f"{agora}"


# ------------------------------------------------------------------- criterio
@check("regua vigente e' a de 3 pernas")
def _regua():
    from bolt_analysis_studio.validation import report_html as rh
    if not hasattr(rh, "META_SRES"):
        return False, "META_SRES ausente — report_html esta na regua de 2 pernas"
    return True, (f"res.max {rh.META_MAX} · MAE {rh.META_MAE} · "
                  f"sigma_res {rh.META_SRES}")


@check("baseline existe, carrega a propria regua e casa com o store")
def _baseline():
    p = ROOT / "New_Theory" / "l1l7_baseline.json"
    if not p.exists():
        return False, "ausente — rode scripts/l1l7_baseline.py"
    b = json.loads(p.read_text(encoding="utf-8"))
    if "criterio" not in b:
        return False, ("sem o campo `criterio`: o baseline nao diz sob que regua "
                       "foi medido (regra §4.43)")
    from bolt_analysis_studio.validation import report_html as rh
    c = b["criterio"]
    if (c.get("mae"), c.get("res_max"), c.get("sigma_res")) != (
            rh.META_MAE, rh.META_MAX, rh.META_SRES):
        return False, (f"baseline medido em {c} mas a regua atual e' "
                       f"{rh.META_MAE}/{rh.META_MAX}/{rh.META_SRES} — re-pine")
    return True, (f"n={b['n']} · tripe {b.get('n_tripe')} · "
                  f"resolvidos {b.get('n_resolvidos')}")


@check("ledger tem entrada na regua vigente (o ZERO do pipeline)")
def _ledger():
    p = ROOT / "New_Theory" / "convergence_ledger.json"
    if not p.exists():
        return False, "ausente"
    led = json.loads(p.read_text(encoding="utf-8"))
    ult = led[-1]
    if "criterio" not in ult:
        return False, (f"a ultima entrada (#{len(led)}) nao declara `criterio` — "
                       "sem zero na regua nova o pipeline nao mede melhora")
    return True, (f"#{len(led)} · n={ult.get('n')} · tripe {ult.get('n_tripe')} · "
                  f"rmse_mean {ult.get('rmse_mean')}")


# ------------------------------------------------------------------- excecoes
@check("excecoes assinadas: listas DISJUNTAS e uniao coerente")
def _exc():
    from bolt_analysis_studio.validation import report_html as rh
    dup = set(rh._F5_EXCECOES) & set(rh._F7_EXCECOES)
    if dup:
        return False, f"{len(dup)} curva(s) nas duas listas: {sorted(dup)[:4]}"
    if len(rh._EXCECOES) != len(rh._F5_EXCECOES) + len(rh._F7_EXCECOES):
        return False, "a uniao nao e' a soma — chave duplicada?"
    return True, (f"F5 {len(rh._F5_EXCECOES)} + F7 {len(rh._F7_EXCECOES)} = "
                  f"{len(rh._EXCECOES)}")


# ------------------------------------------------------- instrumentos do gate
@check("instrumentos de medicao do gate presentes e importaveis")
def _instr():
    faltam = [n for n in ("sensitivity_sres.py", "forma_residuo_classes.py",
                          "sres_granularidade.py", "digitalizacao_lint.py",
                          "graded_scrit_alcance.py")
              if not (ROOT / "New_Theory" / n).exists()]
    if faltam:
        return False, f"faltam {faltam}"
    return True, "5 instrumentos (sensibilidade, forma, granularidade, lint, alcance)"


@check("template de gate escrito ANTES de medir")
def _gate():
    p = (ROOT / "docs" / "superpowers" / "specs"
         / "2026-07-29-gate-candidato-de-forma.md")
    if not p.exists():
        return False, "ausente — gate escrito depois da medicao e' cerimonial"
    t = p.read_text(encoding="utf-8")
    for k in ("G1", "G2", "G3", "G4", "PARCIAL", "COSMÉTICO"):
        if k not in t:
            return False, f"o template nao define {k}"
    return True, "G1-G4 + os 5 ramos de decisao"


# ------------------------------------------------------------------ guardas
@check("guardas de medicao cruzada passam", obrigatorio=True)
def _guardas():
    r = subprocess.run([sys.executable, "-m", "pytest",
                        "tests/test_medicoes_cruzadas.py", "-q", "--no-header"],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    ultima = [l for l in (r.stdout or "").splitlines() if l.strip()][-1:]
    if r.returncode != 0:
        return False, f"pytest saiu {r.returncode}: {ultima}"
    return True, (ultima[0] if ultima else "ok")


@check("arvore git limpa nos arquivos que o pipeline LE ou ESCREVE", obrigatorio=False)
def _git():
    r = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    # Precisao importa aqui: um preflight que sinaliza .md de pesquisa vira ruido e
    # passa a ser ignorado justamente quando sinalizar o store de verdade. So conta o
    # que muda um NUMERO do pipeline: o store (saida), os configs adotados e o bloco
    # `shared` (entram no engine_fingerprint), e os CSVs de referencia (o dado medido).
    def importa(caminho: str) -> bool:
        if caminho.endswith((".json",)) and (
                "validation_store" in caminho
                or "adopted_configs" in caminho
                or "joint_calibrations" in caminho):
            return True
        return caminho.endswith(".csv") and "curve_library" in caminho

    sujos = [l[3:].strip('"') for l in (r.stdout or "").splitlines()
             if importa(l[3:].strip('"'))]
    if sujos:
        return False, (f"{len(sujos)} arquivo(s) que MUDAM numero com alteracao nao "
                       f"commitada: {sujos[:3]} — commite ou restaure antes, senao a "
                       "adocao do pipeline mistura estados")
    return True, "store, configs adotados e CSVs de referencia sem mudanca pendente"


@check("nenhuma sessao paralela com o mesmo arquivo no indice", obrigatorio=False)
def _paralelo():
    r = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    st = [l for l in (r.stdout or "").splitlines() if l.strip()]
    if st:
        return False, (f"{len(st)} arquivo(s) STAGED por alguem: {st[:3]} — "
                       "1 escritor por branch (corrida de indice medida "
                       "2026-07-17)")
    return True, "indice vazio"


def main() -> int:
    obr_falhos = [r for r in RES if not r["ok"] and r["obrigatorio"]]
    avisos = [r for r in RES if not r["ok"] and not r["obrigatorio"]]
    if "--json" in sys.argv:
        print(json.dumps(dict(ok=not obr_falhos, checks=RES),
                         ensure_ascii=False, indent=1))
        return 0 if not obr_falhos else 1
    print(f"PREFLIGHT DO PIPELINE — {len(RES)} checks\n")
    for r in RES:
        marca = "ok  " if r["ok"] else ("FALHA" if r["obrigatorio"] else "aviso")
        print(f"  [{marca:5s}] {r['nome']}")
        print(f"           {r['detalhe']}")
    print()
    if obr_falhos:
        print(f"NAO PRONTO — {len(obr_falhos)} check(s) obrigatorio(s) falhou:")
        for r in obr_falhos:
            print(f"   · {r['nome']}: {r['detalhe']}")
    else:
        print("PRONTO para o pipeline."
              + (f" {len(avisos)} aviso(s) nao bloqueante(s)." if avisos else ""))
    return 0 if not obr_falhos else 1


if __name__ == "__main__":
    raise SystemExit(main())
