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
`reference`; 206 tem DOI, e os 4 sem DOI nao sao publicacao (3 ANCORA_INTERNA, medicao
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




def _censo_e_criterio(recs, store) -> tuple:
    """(no_censo, atende) por case_id, pelas MESMAS funcoes do artigo.

    `caso_comparavel` e' o predicado do Apendice B; `_tripe_ok` com
    `limite_sres` e o piso por fonte e' o criterio do §4. Reimplementar
    qualquer um deles aqui criaria uma segunda verdade que divergiria do
    manuscrito no primeiro ajuste — e o piso importa: sem ele o censo que
    atende cai de 171 para 162.
    """
    from bolt_analysis_studio.validation import report_html as rh

    res = {r.case_id: store.get(r.case_id) for r in recs}
    censo = {r.case_id: bool(rh.caso_comparavel(r.source, r.case_id))
             for r in recs}
    comp = [r for r in recs if censo[r.case_id] and res.get(r.case_id)]
    pisos = rh._pisos_medidos([(r.source, res[r.case_id]) for r in comp])
    atende = {}
    for r in recs:
        try:
            atende[r.case_id] = bool(
                censo[r.case_id]
                and rh._tripe_ok(res[r.case_id],
                                 rh.limite_sres(r.source, pisos)))
        except Exception:                                    # noqa: BLE001
            atende[r.case_id] = False
    return censo, atende


def escreve_indice(destino: Path, recs, store, censo, atende) -> tuple:
    """INDICE.md legivel + indice.json que o seletor do app le.

    O JSON existe para o dialogo de importacao abrir instantaneo: carregar o
    registry e o store a cada abertura custaria segundos por nada.
    """
    import json as _json

    linhas_md = [
        "# Casos de validacao salvos como modelo",
        "",
        f"{len(recs)} arquivos `.msd`, um por curva, na configuracao adotada de "
        "cada caso. Abra qualquer um por **Arquivo > Abrir projeto** "
        "(`Ctrl+O`) ou, mais direto, por **Arquivo > Importar caso da "
        "validacao** (`Ctrl+I`).",
        "",
        f"- **{sum(censo.values())}** estao no **censo do artigo** — sao os que "
        "o manuscrito conta.",
        f"- **{sum(atende.values())}** desses atendem ao criterio de aceitacao "
        "das tres pernas.",
        f"- **{len(recs) - sum(censo.values())}** ficam fora do censo: "
        "simulados e publicados, contados em nenhum numero do manuscrito. O "
        "motivo de cada um esta' no Apendice B do anexo.",
        "",
        "Gerado por `New_Theory/build_saved_cases.py`. O censo usa "
        "`caso_comparavel`, o mesmo predicado do Apendice B.",
        "",
        "| Caso | Fonte | Censo | Criterio | MAE |",
        "|---|---|---|---:|---:|",
    ]
    itens = []
    for r in sorted(recs, key=lambda z: (z.source, z.case_id)):
        res = store.get(r.case_id)
        mae = getattr(res, "mae", None)
        itens.append({
            "case_id": r.case_id, "source": r.source, "name": r.name,
            "arquivo": f"{r.source}/{r.case_id}.msd",
            "censo": censo[r.case_id], "criterio": atende[r.case_id],
            "mae": (round(float(mae), 4) if mae is not None else None),
            "doi": (getattr(r.validation_case, "doi", "") or "").strip(),
            "reference": (getattr(r.validation_case, "reference", "") or "").strip(),
        })
        linhas_md.append(
            f"| `{r.case_id}` | {r.source} | "
            f"{'sim' if censo[r.case_id] else '**nao**'} | "
            f"{'sim' if atende[r.case_id] else '-'} | "
            f"{'' if mae is None else f'{mae:.4f}'} |")

    md = destino / "INDICE.md"
    js = destino / "indice.json"
    md.write_text("\n".join(linhas_md) + "\n", encoding="utf-8", newline="")
    js.write_text(_json.dumps({
        # Data real da geracao. Estava literal, e uma data escrita a mao
        # envelhece calada — dizia 03-09 num indice gerado em 04-09.
        "gerado_em": __import__("datetime").date.today().isoformat(),
        "total": len(itens),
        "no_censo": sum(censo.values()),
        "atendem_criterio": sum(atende.values()),
        "casos": itens,
    }, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    return md, js

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

    # indice: e' o que torna visivel, olhando a pasta, quais dos arquivos o
    # ARTIGO conta. Sem ele os 205 do censo ficam indistinguiveis dos 210.
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore()
    recs = all_records()
    censo, atende = _censo_e_criterio(recs, store)
    escreve_indice(destino, recs, store, censo, atende)
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
