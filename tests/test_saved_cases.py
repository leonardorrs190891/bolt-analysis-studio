"""Os 207 casos salvos como .msd, citados (2026-09-02).

Pedido: "os modelos finais salvos na melhor configuracao", numa pasta de .msd
importada pelo software, e "SENDO CITADOS CORRETAMENTE" no git.

Citacao nao e' formalidade aqui: cada modelo carrega uma curva DIGITALIZADA de
uma publicacao de terceiro, e os arquivos vao para um repositorio publico. O
`ValidationCase` ja' guarda `reference` e `doi` — nada e' redigitado.

Medido no dia: dos 207 casos, 210 tem `reference` e 206 tem DOI. Os 4 sem DOI
sao os que NAO sao publicacao (3 ANCORA_INTERNA, medicao do proprio laboratorio, e 1
USER, exemplo sintetico), e por isso dizem o que sao em vez de deixar um campo
vazio que se leria como omissao.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))

import pytest                                                    # noqa: E402


@pytest.fixture(scope="module")
def gerados(tmp_path_factory, qapp):
    """Gera os 207 numa pasta temporaria, uma vez para todos os testes."""
    import build_saved_cases as bsc
    destino = tmp_path_factory.mktemp("saved_cases")
    n, falhas = bsc.build_all(destino)
    assert not falhas, f"{len(falhas)} casos falharam: {falhas[:3]}"
    return destino, n


def test_todo_caso_virou_arquivo(gerados):
    from bolt_analysis_studio.validation.case_registry import all_records
    destino, n = gerados
    arquivos = list(destino.rglob("*.msd"))
    assert n == len(all_records())
    assert len(arquivos) == n, f"{n} casos, {len(arquivos)} arquivos"


def test_arquivos_organizados_por_fonte(gerados):
    """A pasta espelha a arvore do modulo Validation: fonte -> caso."""
    from bolt_analysis_studio.validation.case_registry import all_records
    destino, _n = gerados
    pastas = {p.name for p in destino.iterdir() if p.is_dir()}
    assert pastas == {r.source for r in all_records()}


def test_toda_citacao_esta_no_arquivo(gerados):
    """Nenhum .msd sai sem a referencia da fonte: sao dados derivados de
    publicacao de terceiro num repositorio publico."""
    import json
    from bolt_analysis_studio.validation.case_registry import all_records
    destino, _n = gerados
    por_id = {r.case_id: r for r in all_records()}

    sem = []
    for arq in destino.rglob("*.msd"):
        d = json.loads(arq.read_text(encoding="utf-8"))
        desc = d.get("description") or ""
        rec = por_id[arq.stem]
        ref = (getattr(rec.validation_case, "reference", "") or "").strip()
        if ref and ref not in desc:
            sem.append(arq.stem)
    assert not sem, f"{len(sem)} arquivos sem a referencia: {sem[:5]}"


def test_doi_aparece_quando_existe_e_nunca_e_inventado(gerados):
    import json
    from bolt_analysis_studio.validation.case_registry import all_records
    destino, _n = gerados
    por_id = {r.case_id: r for r in all_records()}

    faltou, inventou = [], []
    for arq in destino.rglob("*.msd"):
        desc = json.loads(arq.read_text(encoding="utf-8")).get("description") or ""
        doi = (getattr(por_id[arq.stem].validation_case, "doi", "") or "").strip()
        if doi and doi not in desc:
            faltou.append(arq.stem)
        if not doi and "doi.org/10." in desc:
            inventou.append(arq.stem)
    assert not faltou, f"DOI existe e nao foi citado: {faltou[:5]}"
    assert not inventou, f"DOI citado sem existir: {inventou[:5]}"


def test_caso_sem_doi_diz_o_que_e(gerados):
    """Os 4 que nao sao publicacao declaram o motivo, para um campo ausente
    nao ser lido como esquecimento."""
    import json
    from bolt_analysis_studio.validation.case_registry import all_records
    destino, _n = gerados
    sem_doi = [r for r in all_records()
               if not (getattr(r.validation_case, "doi", "") or "").strip()]
    assert sem_doi, "o corpus deixou de ter casos sem DOI; revise este teste"
    for r in sem_doi:
        arq = next(destino.rglob(f"{r.case_id}.msd"))
        desc = json.loads(arq.read_text(encoding="utf-8")).get("description") or ""
        assert "no DOI" in desc, f"{r.case_id} nao explica a ausencia de DOI"


def test_a_melhor_configuracao_sobrevive_no_arquivo(gerados):
    """O ponto de tudo: reabrir o .msd tem de devolver as constantes adotadas.
    Antes da correcao de 2026-09-02 isto voltava vazio e o modelo PARECIA bom."""
    from bolt_analysis_studio.core.models.model import MSDModel
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    destino, _n = gerados

    arq = next(destino.rglob("lu2024_M8_fig18_amp0p5.msd"))
    esperado = build_case_model(record("lu2024_M8_fig18_amp0p5"))
    lido = MSDModel.load(str(arq))
    assert getattr(lido, "_v2_tuner_overrides", {}) == esperado._v2_tuner_overrides
    assert getattr(lido, "_v2_geometry_overrides", {}) == esperado._v2_geometry_overrides
    assert len(lido.elements) == len(esperado.elements)


def test_nenhum_arquivo_fica_sem_constantes_adotadas(gerados):
    """Varredura nos 207: um caso que saia sem overrides seria um modelo
    plausivel e errado, que e' o pior resultado possivel."""
    import json
    destino, _n = gerados
    vazios = [a.stem for a in destino.rglob("*.msd")
              if not json.loads(a.read_text(encoding="utf-8")).get("v2_tuner_overrides")]
    assert not vazios, f"{len(vazios)} arquivos sem constantes adotadas: {vazios[:5]}"
