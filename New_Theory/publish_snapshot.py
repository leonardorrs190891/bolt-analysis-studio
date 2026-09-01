# -*- coding: utf-8 -*-
"""Build the PUBLIC single-commit snapshot of this repository (2026-08-29).

Decision of the authors: the public repository carries only the current version,
not the development history. The snapshot is therefore taken from `git archive
HEAD` (committed content only: no untracked files, no PDFs, no local lab data),
a SNAPSHOT.md records the source commit, and a fresh repository is initialised
with ONE commit and one annotated tag.

The dated artefacts the paper relies on travel with the snapshot as JSON:
New_Theory/holdout/frozen_*.json, adopted_configs_<date>_<hash>.json,
config_history_digest.json, New_Theory/paper/temporal_holdout.json and
New_Theory/ablation/ablation_*.json.

    py -3.12 New_Theory/publish_snapshot.py --dest ..\\bolt-analysis-studio-public
                                           [--remote https://github.com/leonardorrs190891/bolt-analysis-studio.git]
                                           [--tag v2.0.0] [--push]

Without --push nothing leaves this machine: the script prints the two commands
that would. It refuses a destination that exists and is not empty.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import subprocess
import tarfile
import io
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Committed content that must NOT be published, each with the reason. Checked
# against the extracted tree, so an entry that stops matching is reported
# instead of passing unnoticed.
EXCLUIR = [
    ("CLAUDE.md",
     "working notes for the coding assistant: 1900 lines of internal "
     "development narrative, retractions and quoted decisions"),
    (".claude",
     "assistant configuration, not part of the software"),
    (".superpowers",
     "assistant framework notes, not part of the software"),
    ("Bolted",
     "third-party document (What is a Joint Diagram.docx) and notes derived "
     "from a vendor tutorial: not ours to redistribute"),
    ("New_Theory/Materiais_Metalicos_EPL_Gb.docx",
     "unrelated document (materials for explosion-protected enclosures)"),
    ("New_Theory/paper",
     "the manuscript: article, supplementary material, highlights, submission "
     "artwork and superseded drafts. Decision of 2026-09-01: only the software "
     "is published"),
    ("New_Theory/build_paper_docx.py",
     "the manuscript in source form: its text lives here as string literals, "
     "so shipping it would publish what the .docx exclusion withholds. Nothing "
     "else in the repository imports it"),
    ("New_Theory/annex/BAS_V2_software_annex.docx",
     "companion document of the article. Its generator stays, because three "
     "analysis tools import it, so `py -3.12 New_Theory/build_annex_docx.py` "
     "rebuilds the document from the store"),
    # loose models left at the repository root by day-to-day work; the two the
    # documentation actually loads (model.msd, jiang_1.msd) and the named
    # literature case (Zhang_Jiang_2006_M12_25mm_grip.msd) stay
    ("A1A1.msd", "scratch model"),
    ("AA.msd", "scratch model"),
    ("jiang_2.msd", "scratch model"),
    ("jt.msd", "scratch model"),
    ("model_wizard.msd", "scratch model"),
    ("teste.msd", "scratch model"),
    ("ufu1.msd", "scratch model of a rig outside the project"),
]


def _ajusta_readme(dest):
    """Four references to the withheld manuscript, rewritten for the public
    tree. Each substitution asserts its anchor: a dead reference in a published
    README is worse than a release that stops and says why."""
    arq = dest / "README.md"
    txt = arq.read_text(encoding="utf-8")
    trocas = [
        ("| `New_Theory/build_paper_docx.py`, `build_annex_docx.py` | Generators "
         "of the manuscript and of the software annex (Word) |",
         "| `New_Theory/build_annex_docx.py` | Generator of the software annex "
         "(Word), every number recomputed from the store |"),
        ("5. **Documents**: reports, annex and manuscript are generated from the "
         "store;",
         "5. **Documents**: the reports and the software annex are generated "
         "from the store;"),
        ("# 3. software annex and manuscript (Word), every number recomputed\n"
         "python New_Theory/build_annex_docx.py\n"
         "python New_Theory/build_paper_docx.py",
         "# 3. software annex (Word), every number recomputed from the store\n"
         "python New_Theory/build_annex_docx.py"),
        ("Every number in the companion paper\nand in the software annex is "
         "recomputed from this repository by the generators\nlisted below.",
         "Every number in the companion paper and in the software annex is\n"
         "recomputed from this repository. The paper itself is not part of it: "
         "what\nis published here is the software, the corpus, the "
         "configurations and the\nresults it is built on."),
        ("## Reproducing the paper", "## Reproducing the results"),
        ("analyses of the paper rely on are included as JSON under "
         "`New_Theory/holdout/`\nand `New_Theory/paper/`.",
         "analyses of the paper rely on are included as JSON under "
         "`New_Theory/holdout/`\nand `New_Theory/ablation/`. The manuscript "
         "itself is not part of this repository."),
    ]
    for velho, novo in trocas:
        if velho not in txt:
            raise SystemExit(
                "[snapshot] README.md changed and this anchor no longer "
                "matches, so the public README would keep a dead reference to "
                f"the withheld manuscript:\n    {velho[:90]}...")
        txt = txt.replace(velho, novo)
    arq.write_text(txt, encoding="utf-8", newline="")
    print(f"[snapshot] README.md adjusted for the public tree "
          f"({len(trocas)} references to the withheld manuscript)")


def _remove_excluidos(dest):
    """Delete the excluded paths from the extracted tree and report each one.
    An entry that matches nothing is a warning: it means the repository moved
    and the exclusion is no longer doing what its reason says."""
    import shutil
    n_arq = 0
    for rel, motivo in EXCLUIR:
        alvo = dest / rel
        if not alvo.exists():
            print(f"[snapshot] WARNING: exclusion {rel} matched nothing "
                  f"(reason on record: {motivo})")
            continue
        if alvo.is_dir():
            k = sum(1 for _ in alvo.rglob("*") if _.is_file())
            shutil.rmtree(alvo)
        else:
            k = 1
            alvo.unlink()
        n_arq += k
        print(f"[snapshot] excluded {rel} ({k} file{'s' if k > 1 else ''}): {motivo}")
    return n_arq


def _git(*args, cwd=RAIZ, check=True) -> str:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{r.stderr}")
    return r.stdout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="publish_snapshot")
    ap.add_argument("--dest", required=True, help="new folder for the public snapshot")
    ap.add_argument("--remote", default=None, help="GitHub URL of the EMPTY repository")
    ap.add_argument("--tag", default="v2.0.0")
    ap.add_argument("--push", action="store_true", help="actually push (needs credentials)")
    args = ap.parse_args(argv)

    dest = Path(args.dest).resolve()
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"{dest} exists and is not empty; refusing to overwrite")
    dest.mkdir(parents=True, exist_ok=True)

    head = _git("rev-parse", "HEAD").strip()
    data = _git("log", "-1", "--format=%ad", "--date=short").strip()
    sujo = _git("status", "--porcelain").strip()
    if sujo:
        print("[snapshot] WARNING: working tree has uncommitted changes; the snapshot "
              "is taken from HEAD, so they are NOT included:")
        print("\n".join("    " + l for l in sujo.splitlines()[:12]))

    # 1) committed content only
    raw = subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=str(RAIZ),
                         capture_output=True).stdout
    # Windows MAX_PATH (260) bites on the deep corpus paths: extract through the
    # extended-length prefix, which lifts the limit for the file API.
    alvo_extracao = ("\\\\?\\" + str(dest)) if os.name == "nt" else str(dest)
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as tf:
        tf.extractall(alvo_extracao, filter="data")

    # 1b) what must not be published
    n_fora = _remove_excluidos(dest)
    print(f"[snapshot] {n_fora} files withheld from the public tree")
    _ajusta_readme(dest)

    # 2) provenance of the snapshot
    (dest / "SNAPSHOT.md").write_text(
        f"# Public snapshot\n\n"
        f"This repository is published as a single release, taken on "
        f"{_dt.date.today().isoformat()} from source commit `{head}` (dated {data}). "
        f"It carries the current version of the code, the digitised validation "
        f"corpus, the adopted configurations, the canonical result store and the "
        f"stamped analysis artefacts (`New_Theory/ablation/`, `New_Theory/holdout/`). "
        f"Pre-registration documents live under `docs/superpowers/specs/`; analysis "
        f"records under `New_Theory/`.\n\n"
        f"Withheld from this public tree: the working notes written for the "
        f"coding assistant and its configuration, one third-party document, one "
        f"unrelated document, and scratch models left at the repository root. "
        f"**The manuscript is not published here**: only the software, the "
        f"corpus, the configurations and the results are, so the article, its "
        f"supplementary material and the generator that writes them are "
        f"withheld. Nothing the software needs to run, or to recompute a "
        f"number, is among the exclusions; the list with a reason per entry is "
        f"in `New_Theory/publish_snapshot.py`.\n",
        encoding="utf-8", newline="")

    n_files = sum(1 for _ in dest.rglob("*") if _.is_file())   # incl. SNAPSHOT.md

    # 3) one commit, one tag. `-f`: the shipped .gitignore ignores *.csv and *.png,
    #    which the development repository force-adds; the snapshot must carry
    #    every file the archive contains (measured 2026-08-29: 3212 extracted,
    #    2373 staged without -f, the corpus CSVs among the missing).
    _git("init", "-q", "-b", "main", cwd=dest)
    _git("add", "-A", "-f", cwd=dest)
    n_staged = len(_git("diff", "--cached", "--name-only", cwd=dest).splitlines())
    if n_staged != n_files:
        raise SystemExit(f"staged {n_staged} files but extracted {n_files}; refusing to "
                         f"commit an incomplete snapshot")
    _git("-c", "user.name=Leonardo Rosa Ribeiro da Silva", "-c", "user.email=leorrs@ufu.br",
         "commit", "-q", "-m",
         f"Bolt Analysis Studio V2: public release snapshot (source commit {head[:12]})",
         cwd=dest)
    _git("-c", "user.name=Leonardo Rosa Ribeiro da Silva", "-c", "user.email=leorrs@ufu.br",
         "tag", "-a", args.tag, "-m", f"BAS V2 {args.tag}: release accompanying the paper",
         cwd=dest)
    print(f"[snapshot] {n_files} files from {head[:12]} -> {dest}")
    print(f"[snapshot] single commit on main, tag {args.tag}")

    if args.remote:
        _git("remote", "add", "origin", args.remote, cwd=dest)
        print(f"[snapshot] remote origin = {args.remote}")
    cmd = f"cd \"{dest}\" && git push -u origin main && git push origin {args.tag}"
    if args.push and args.remote:
        _git("push", "-u", "origin", "main", cwd=dest)
        _git("push", "origin", args.tag, cwd=dest)
        print("[snapshot] pushed main and", args.tag)
    else:
        print("[snapshot] nothing pushed. To publish:\n    " + cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
