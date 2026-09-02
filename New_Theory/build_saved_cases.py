# -*- coding: utf-8 -*-
"""Os 210 casos da validacao salvos como .msd na configuracao ADOTADA (2026-09-02).

    py -3.12 New_Theory/build_saved_cases.py [--out Models/SAVED_CASES]

Gera uma pasta por fonte (artigo) com um .msd por curva, importavel pelo
software por File > Open. O modelo sai do mesmo `build_case_model` que o botao
"Abrir no Model/Run" usa, entao carrega a cadeia MSD completa, o F0 do caso, o
atrito nos dois niveis e os dois canais de override com as constantes adotadas.

⚠️ Isto so' funciona a partir da correcao de 2026-09-02 em `MSDModel.to_dict`:
antes dela, salvar devolvia o modelo com os elementos, F0 e mu certos e ZERO
constantes adotadas. O arquivo PARECIA bom e nao era. `test_saved_cases.py`
trava isso nos 210.

CITACAO. Cada arquivo carrega uma curva DIGITALIZADA de uma publicacao de
terceiro e vai para um repositorio publico, entao a referencia da fonte viaja
dentro do .msd. Os campos saem do `ValidationCase` (`reference`, `doi`,
`reference_csv_path`) — nada e' redigitado aqui. Medido: 210 de 210 tem
`reference`; 206 tem DOI, e os 4 sem DOI nao sao publicacao (3 UFU_LAB, medicao
do proprio laboratorio, e 1 USER, exemplo sintetico), por isso DIZEM o que sao
em vez de deixar um campo vazio que se leria como omissao.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

DESTINO_PADRAO = RAIZ / "Models" / "SAVED_CASES"

# A citacao mora no PACOTE (validation/provenance.py) porque e' propriedade
# do caso, nao da geracao: a GUI tambem salva casos, e duas copias da mesma
# string divergiriam no primeiro ajuste.
from bolt_analysis_studio.validation.provenance import (   # noqa: E402
    citation_block, _rel)                                  # noqa: F401


def build_one(rec, destino: Path) -> Path:
    from bolt_analysis_studio.validation.gui_bridge import build_case_model

    model = build_case_model(rec)
    model.name = rec.name or rec.case_id
    model.description = citation_block(rec)
    pasta = destino / rec.source
    pasta.mkdir(parents=True, exist_ok=True)
    alvo = pasta / f"{rec.case_id}.msd"
    model.save(str(alvo))
    return alvo


def build_all(destino: Path) -> tuple:
    """Devolve (quantos, falhas). Nao aborta no primeiro erro: um caso que nao
    monta e' informacao, e parar esconderia os outros 209."""
    from bolt_analysis_studio.validation.case_registry import all_records

    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    n, falhas = 0, []
    for rec in all_records():
        try:
            build_one(rec, destino)
            n += 1
        except Exception as exc:                            # noqa: BLE001
            falhas.append((rec.case_id, f"{type(exc).__name__}: {exc}"))
    return n, falhas


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description="Salva os casos da validacao como .msd citados")
    ap.add_argument("--out", default=str(DESTINO_PADRAO))
    args = ap.parse_args(argv)

    # QApplication: build_case_model desce em new_analysis_wizard, que importa
    # QtWidgets. Offscreen para o gerador rodar sem sessao grafica.
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])

    destino = Path(args.out)
    n, falhas = build_all(destino)
    tam = sum(f.stat().st_size for f in destino.rglob("*.msd")) / 2**20
    fontes = len([p for p in destino.iterdir() if p.is_dir()])
    print(f"  {n} casos em {fontes} fontes -> {destino}  ({tam:.1f} MB)")
    for cid, err in falhas:
        print(f"  [FALHA] {cid}: {err}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
