"""Build do instalador auto-contido (2026-09-02).

Spec:  docs/superpowers/specs/2026-09-02-instalador-auto-contido-design.md
Plano: docs/superpowers/plans/2026-09-02-instalador-auto-contido.md

As partes que DECIDEM sao puras (texto -> metadados, arvore -> o que podar,
arvore -> o que copiar) para poderem ser testadas sem baixar 10 MB de Python
nem montar uma arvore de 400 MB.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "New_Theory"))

import build_installer as bi                                    # noqa: E402


def test_metadados_saem_do_setup_py():
    texto = (
        'setup(\n'
        '    name="bolt-analysis-studio",\n'
        '    version="2.0.0",\n'
        '    author="Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva",\n'
        '    author_email="leorrs@ufu.br",\n'
        ')\n'
    )
    meta = bi._project_metadata(texto)
    assert meta["version"] == "2.0.0"
    assert meta["author"] == (
        "Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva")


def test_metadados_do_setup_py_real_do_repo():
    """Ancora contra o arquivo: se o setup.py mudar de forma que o build nao
    entenda, quebra aqui e nao na hora de compilar o instalador."""
    meta = bi._project_metadata(
        (RAIZ / "setup.py").read_text(encoding="utf-8"))
    # 1.0.0: e' a primeira versao publicada do programa. O "V2" do nome
    # interno era da teoria, nunca do software (decisao de 2026-09-03).
    assert meta["version"] == "1.0.0"
    assert "Leonardo" in meta["author"] and "Neilon" in meta["author"]


def test_metadados_faltando_versao_levanta():
    """Um instalador sem versao e' pior que um build que para: a entrada em
    Adicionar/Remover Programas fica sem numero e a proxima nao substitui."""
    import pytest
    with pytest.raises(SystemExit):
        bi._project_metadata('setup(name="x")\n')


def test_sha256_confere_conteudo_conhecido(tmp_path):
    import hashlib
    f = tmp_path / "x.bin"
    f.write_bytes(b"bolt analysis studio")
    assert bi._sha256(f) == hashlib.sha256(b"bolt analysis studio").hexdigest()


def test_zip_com_hash_errado_e_recusado(tmp_path):
    """Um instalador que vai ser distribuido nao nasce de download nao
    verificado: hash divergente ABORTA em vez de seguir."""
    import pytest
    z = tmp_path / "python-embed.zip"
    z.write_bytes(b"nao e' o pacote do python.org")
    with pytest.raises(SystemExit, match="sha256"):
        bi._check_embed(z)


def test_o_pin_do_python_embutido_esta_completo():
    assert bi.PY_EMBED["version"] == "3.12.10"
    assert bi.PY_EMBED["url"].endswith("python-3.12.10-embed-amd64.zip")
    assert len(bi.PY_EMBED["sha256"]) == 64


def test_enable_site_liga_o_site_e_o_site_packages(tmp_path):
    """O pacote embeddable vem com `import site` COMENTADO e sem
    site-packages no caminho. Sem corrigir isso, o pip instala com sucesso e o
    interpretador nao acha nada do que foi instalado."""
    pth = tmp_path / "python312._pth"
    pth.write_text("python312.zip\n.\n\n#import site\n", encoding="utf-8")
    bi._enable_site(tmp_path)
    conteudo = pth.read_text(encoding="utf-8")
    linhas = [l.strip() for l in conteudo.splitlines() if l.strip()]
    assert "import site" in linhas
    assert "#import site" not in conteudo
    assert r"Lib\site-packages" in linhas


def test_enable_site_e_idempotente(tmp_path):
    pth = tmp_path / "python312._pth"
    pth.write_text("python312.zip\n.\n#import site\n", encoding="utf-8")
    bi._enable_site(tmp_path)
    primeiro = pth.read_text(encoding="utf-8")
    bi._enable_site(tmp_path)
    assert pth.read_text(encoding="utf-8") == primeiro


def test_enable_site_sem_pth_levanta(tmp_path):
    import pytest
    with pytest.raises(SystemExit, match="_pth"):
        bi._enable_site(tmp_path)


def test_poda_remove_o_que_o_app_nao_importa(tmp_path):
    """Medido: o app importa QtWidgets, QtCore, QtGui, QtPrintSupport e QtSvg.
    Nada mais, e zero WebEngine ou QML."""
    q = tmp_path / "Lib" / "site-packages" / "PyQt6" / "Qt6" / "bin"
    q.mkdir(parents=True)
    for nome in ("Qt6Core.dll", "Qt6Widgets.dll", "Qt6Svg.dll",
                 "Qt6Quick.dll", "Qt6Qml.dll", "Qt6Designer.dll",
                 "avcodec-61.dll", "opengl32sw.dll"):
        (q / nome).write_bytes(b"x" * 1024)
    qml = tmp_path / "Lib" / "site-packages" / "PyQt6" / "Qt6" / "qml"
    qml.mkdir()
    (qml / "a.qml").write_bytes(b"y")

    bytes_fora, itens = bi._prune(tmp_path)

    restantes = {f.name for f in q.iterdir()}
    assert {"Qt6Core.dll", "Qt6Widgets.dll", "Qt6Svg.dll"} <= restantes
    assert not {"Qt6Quick.dll", "Qt6Qml.dll", "Qt6Designer.dll",
                "avcodec-61.dll"} & restantes
    assert not qml.exists()
    assert bytes_fora > 0 and itens > 0


def test_poda_preserva_o_opengl_de_software(tmp_path):
    """opengl32sw.dll sao 19,7 MB, e e' o caminho que faz o Qt desenhar em
    maquina sem driver de GPU decente. Podar economiza 20 MB e troca por
    'a janela abre preta no PC do laboratorio'. Fica."""
    q = tmp_path / "Lib" / "site-packages" / "PyQt6" / "Qt6" / "bin"
    q.mkdir(parents=True)
    (q / "opengl32sw.dll").write_bytes(b"x" * 1024)
    (q / "d3dcompiler_47.dll").write_bytes(b"x" * 1024)
    bi._prune(tmp_path)
    assert (q / "opengl32sw.dll").is_file()
    assert (q / "d3dcompiler_47.dll").is_file()


def test_poda_nao_toca_no_que_nao_casa(tmp_path):
    (tmp_path / "Lib").mkdir()
    guardar = tmp_path / "Lib" / "importante.txt"
    guardar.write_bytes(b"z")
    bi._prune(tmp_path)
    assert guardar.is_file()


def test_payload_nunca_inclui_pdf():
    """659 MB de PDF de editora. Nao entram por DIREITOS, nao por peso: o
    software le 1,3 MB de CSV digitalizado e notas, e nao precisa deles."""
    arquivos = bi._payload_files(RAIZ)
    pdfs = [p for p in arquivos if p.suffix.lower() == ".pdf"]
    assert pdfs == [], f"{len(pdfs)} PDF entrariam no instalador: {pdfs[:3]}"


def test_payload_traz_as_notas_de_aparato_das_rodadas_R4_R5():
    """case_registry.py:24-25 resolve as notas por caminho DENTRO de
    BAS_V2_papers/<rodada>/apparatus_notes, com espacos e parenteses no nome."""
    rel = {p.relative_to(RAIZ).as_posix() for p in bi._payload_files(RAIZ)}
    assert [r for r in rel if "Rodada 4" in r and "apparatus_notes" in r]
    assert [r for r in rel if "Rodada 5" in r and "apparatus_notes" in r]


def test_payload_traz_o_store_e_as_configs_adotadas():
    rel = {p.relative_to(RAIZ).as_posix() for p in bi._payload_files(RAIZ)}
    assert "Models/CALIBRATION_AND_VALIDATION/validation_store.json" in rel
    assert "New_Theory/adopted_configs.json" in rel
    assert "run_app.py" in rel and "requirements.txt" in rel
    assert "LICENSE" in rel and "DATA_LICENSE.md" in rel


def test_payload_traz_as_paginas_por_artigo():
    rel = {p.relative_to(RAIZ).as_posix() for p in bi._payload_files(RAIZ)}
    assert "New_Theory/variable_explorer/index.html" in rel
    estudos = [r for r in rel if "/variable_explorer/study_" in r]
    assert len(estudos) >= 27, f"so {len(estudos)} paginas por artigo"


def test_payload_traz_o_csv_de_TODOS_os_210_casos():
    """206 dos 210 CSV estao sob BAS_V2_papers ou curve_library, mas 4 nao —
    3 UFU_LAB em Models/EXPERIMENTAL_UFU e 1 USER em Models/USER_CASES. O
    store traz as 210 analises, entao esses 4 APARECEM na arvore; sem o CSV,
    'Re-simular caso' falha e eles ficam somente-leitura em silencio."""
    import sys as _s
    _s.path.insert(0, str(RAIZ / "src"))
    from bolt_analysis_studio.validation.case_registry import all_records

    no_payload = {p.resolve() for p in bi._payload_files(RAIZ)}
    faltando = [r.case_id for r in all_records()
                if r.csv_path is not None
                and Path(r.csv_path).resolve() not in no_payload]
    assert not faltando, f"{len(faltando)} casos sem CSV no payload: {faltando[:5]}"


def test_payload_nao_traz_backups_nem_pycache():
    rel = [p.relative_to(RAIZ).as_posix() for p in bi._payload_files(RAIZ)]
    assert not [r for r in rel if ".bkp_" in r]
    assert not [r for r in rel if "__pycache__" in r]


def test_copia_preserva_o_caminho_relativo(tmp_path):
    """A raiz da instalacao E' o repo root (repo_root() = parents[3] de
    inputs.py). Copiar achatando destroi isso."""
    n_arq, _bytes = bi._copy_payload(RAIZ, tmp_path)
    assert n_arq > 0
    alvo = tmp_path / "src" / "bolt_analysis_studio" / "validation" / "inputs.py"
    assert alvo.is_file()
    assert alvo.resolve().parents[3] == tmp_path.resolve()


def test_longpath_aplica_o_prefixo_estendido_do_windows():
    """MAX_PATH de 260 chars. Medido 2026-09-02: o CSV mais longo do payload
    tem 183 chars de caminho RELATIVO, entao qualquer raiz de instalacao acima
    de ~77 chars estoura — e o destino default,
    C:/Users/<nome>/AppData/Local/Programs/Bolt Analysis Studio V2, estoura.
    Sem o prefixo o instalador falharia em maquina real, nao so' no teste."""
    import os
    if os.name != "nt":
        return
    p = bi._longpath(Path(r"C:\a\b\c.txt"))
    # os quatro caracteres do prefixo, montados sem escape para o teste nao
    # depender de como a barra invertida sobrevive a quem escreveu o arquivo
    barra = chr(92)
    assert str(p).startswith(barra * 2 + "?" + barra), repr(str(p)[:6])
    assert str(p).endswith(r"a\b\c.txt")


def test_longpath_nao_duplica_o_prefixo():
    import os
    if os.name != "nt":
        return
    uma = bi._longpath(Path(r"C:\a\b"))
    duas = bi._longpath(uma)
    assert str(uma) == str(duas)


def test_copia_sobrevive_a_um_destino_com_caminho_longo(tmp_path):
    """Reproduz o estouro: destino aninhado o suficiente para passar de 260
    somado ao caminho relativo mais longo do payload."""
    fundo = tmp_path / ("z" * 40) / ("y" * 40)
    fundo.mkdir(parents=True)
    n, _b = bi._copy_payload(RAIZ, fundo)
    assert n > 0
    longos = [p for p in bi._payload_files(RAIZ)
              if len(str(fundo / p.relative_to(RAIZ))) > 259]
    assert longos, "o teste nao reproduziu o estouro; aumente o aninhamento"
    for p in longos[:3]:
        assert bi._longpath(fundo / p.relative_to(RAIZ)).exists(), p


def test_ico_e_gerado_e_legivel_de_volta(tmp_path):
    from PyQt6.QtGui import QImageReader
    ico = bi._make_ico(
        RAIZ / "src" / "bolt_analysis_studio" / "resources" / "icons" / "app_icon.svg",
        tmp_path / "bas.ico")
    assert ico.is_file() and ico.stat().st_size > 0
    r = QImageReader(str(ico))
    assert r.canRead(), "o .ico gerado nao e' legivel de volta"
    assert r.size().width() >= 128


def test_a_cor_do_icone_nao_e_a_do_tema_escuro():
    """icons.py usa Theme.TEXT por padrao, que hoje resolve para o tema ESCURO
    (#cdd6f4, claro). Um glifo quase branco sobre fundo transparente fica
    invisivel no Explorer e no proprio instalador: a cor tem de vir do tema
    CLARO."""
    import sys as _s
    _s.path.insert(0, str(RAIZ / "src"))
    from bolt_analysis_studio.gui.theme import THEME_DARK, THEME_LIGHT
    assert bi.ICO_FG == THEME_LIGHT["TEXT"]
    assert bi.ICO_FG != THEME_DARK["TEXT"]


def test_leiame_ensina_onde_estao_os_dados_de_calibracao(tmp_path):
    """O pedido de 2026-09-02 e' explicito: o leiame indica como usar E como
    ver os dados de calibracao."""
    meta = {"version": "2.0.0", "author": "Leonardo; Neilon"}
    alvo = bi._write_leiame(tmp_path / "LEIAME.html", meta, 29, 210, 205)
    html = alvo.read_text(encoding="utf-8")
    assert "Ctrl</kbd>+<kbd>5" in html and "Validation" in html
    assert "New_Theory/variable_explorer/index.html" in html
    assert "adopted_configs.json" in html
    assert "Report HTML" in html and "Report geral" in html
    assert "29 fontes" in html and "210 curvas" in html


def test_leiame_ensina_a_importar_uma_curva_como_modelo(tmp_path):
    """Ver a curva no Validation e' uma coisa; abrir aquela curva como modelo
    editavel e' outra, e e' o que o usuario pediu em 2026-09-03. O censo tem de
    aparecer com o numero certo e com o ponteiro para o Apendice B."""
    html = bi._write_leiame(tmp_path / "L.html",
                            {"version": "1.0.0", "author": "x"}, 29, 210, 205
                            ).read_text(encoding="utf-8")
    assert "Ctrl</kbd>+<kbd>I" in html
    assert "205" in html and "Ap&ecirc;ndice B" in html
    assert "SAVED_CASES" in html


def test_leiame_ensina_a_calibrar_e_diz_o_que_o_ajuste_nao_e(tmp_path):
    """O ajuste automatico e' o recurso que mais convida a mal-entendido: quem
    calibra contra a propria curva pode achar que produziu uma configuracao
    adotada. O leiame ensina o Ctrl+K, a regra da trava, e diz que nao e'."""
    html = bi._write_leiame(tmp_path / "L.html",
                            {"version": "1.0.0", "author": "x"}, 29, 210, 205
                            ).read_text(encoding="utf-8")
    assert "Ctrl</kbd>+<kbd>K" in html
    assert "n&atilde;o marca" in html          # a regra da trava
    assert "CSV" in html                       # a segunda origem da curva
    assert "n&atilde;o</b> &eacute; uma das" in html   # o que o ajuste NAO e'


def test_o_indice_dos_casos_entra_no_instalador():
    """O glob dos .msd nao pega a raiz de SAVED_CASES. Sem indice.json o
    seletor do Ctrl+I abre VAZIO na maquina instalada, com os 210 arquivos
    presentes — a falha silenciosa que a aceitacao ja' pegou duas vezes com
    outros arquivos de dados."""
    alvos = [p for p, _motivo in bi.PAYLOAD]
    assert "Models/SAVED_CASES/indice.json" in alvos, alvos


def test_leiame_traz_autores_versao_licenca_e_doi(tmp_path):
    meta = {"version": "2.0.0",
            "author": "Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva"}
    html = bi._write_leiame(tmp_path / "L.html", meta, 29, 210, 205).read_text(encoding="utf-8")
    assert "Leonardo Rosa Ribeiro da Silva" in html
    assert "Neilon de Souza da Silva" in html
    assert "2.0.0" in html and "MIT" in html
    assert "10.5281/zenodo.22233437" in html


def test_leiame_diz_o_que_nao_vem_e_por_que(tmp_path):
    """Quem procurar os PDF dos artigos tem de achar a explicacao e o caminho
    para a fonte, nao um diretorio vazio."""
    html = bi._write_leiame(tmp_path / "L.html",
                            {"version": "2.0.0", "author": "x"}, 29, 210, 205
                            ).read_text(encoding="utf-8")
    assert "PDF" in html and "DOI" in html


def test_leiame_declara_utf8_e_nao_deixa_placeholder(tmp_path):
    html = bi._write_leiame(tmp_path / "L.html",
                            {"version": "2.0.0", "author": "x"}, 29, 210, 205
                            ).read_text(encoding="utf-8")
    assert 'charset="utf-8"' in html.lower()
    assert "{versao}" not in html and "{autores}" not in html


def test_console_cmd_roda_com_o_preflight_ligado(tmp_path):
    """O atalho normal passa --skip-deps-check porque pythonw.exe nao tem
    console. Este .cmd existe para o caso contrario: console E preflight."""
    cmd = bi._write_console_cmd(tmp_path / "BAS-console.cmd").read_text()
    # so' as linhas EXECUTAVEIS: os comentarios `rem` citam de proposito tanto
    # pythonw quanto --skip-deps-check, para explicar o que este arquivo NAO
    # faz. Afirmar sobre o texto inteiro media' o comentario, nao o comando.
    exec_ = "\n".join(l for l in cmd.splitlines()
                      if l.strip() and not l.strip().lower().startswith(("rem", "@echo")))
    assert "python.exe" in exec_ and "pythonw" not in exec_
    assert "--skip-deps-check" not in exec_
    assert "run_app.py" in exec_
    assert "pause" in exec_


def _tpl():
    return (RAIZ / "New_Theory" / "installer" / "bas_v2.iss.template").read_text(
        encoding="utf-8")


def _iss():
    return bi._render_iss(_tpl(),
                          {"version": "2.0.0",
                           "author": "Prof. Leonardo Rosa Ribeiro da Silva, PhD; "
                                     "Neilon de Souza da Silva"},
                          Path(r"C:\build"), Path(r"C:\saida"))


def test_iss_recebe_versao_e_autores_do_setup_py():
    iss = _iss()
    assert "AppVersion=2.0.0" in iss
    assert "Neilon de Souza da Silva" in iss
    # sem "V2": e' a primeira versao publicada, e o nome do produto
    # deixou de carregar o sufixo em 2026-09-02
    assert "OutputBaseFilename=BAS-Setup-2.0.0" in iss
    linhas = [l.strip() for l in iss.splitlines()]
    assert "AppName=Bolt Analysis Studio" in linhas
    assert "Studio V2" not in iss


def test_iss_nao_deixa_campo_sem_substituir():
    """O `AppId={{GUID}` do Inno usa chave dupla de proposito, entao procurar
    '{{' acusaria falso positivo. O marcador deste template e' @CAMPO@."""
    import re
    iss = _iss()
    sobrou = [l for l in iss.splitlines()
              if re.search(r"@[A-Z]+@", l) and not l.lstrip().startswith(";")]
    assert not sobrou, sobrou


def test_iss_da_icone_ao_proprio_instalador_E_ao_atalho():
    """O pedido pede o icone NO ARQUIVO DE INSTALACAO. SetupIconFile e' o .exe
    do instalador; IconFilename e' o atalho. Sao coisas diferentes, e o pedido
    quer as duas."""
    iss = _iss()
    assert "SetupIconFile=" in iss
    assert "IconFilename:" in iss
    assert "UninstallDisplayIcon=" in iss


def test_iss_abre_o_leiame_ao_final():
    iss = _iss()
    corrida = [l for l in iss.splitlines() if "LEIAME.html" in l and "Flags:" in l]
    assert corrida, "nenhuma entrada [Run] para o leiame"
    assert "postinstall" in corrida[0] and "shellexec" in corrida[0]


def test_iss_instala_por_usuario_sem_uac():
    assert "PrivilegesRequired=lowest" in _iss()


def test_iss_atalho_aponta_para_o_pythonw_embutido():
    """A pilha existe para preservar sys.executable como Python real: atalho
    para outra coisa perde exatamente isso."""
    iss = _iss()
    atalho = [l for l in iss.splitlines()
              if l.startswith("Name:") and "{group}" in l and "run_app.py" in l]
    assert atalho, "nenhum atalho para o run_app.py"
    assert "python\\pythonw.exe" in atalho[0]
    assert "--skip-deps-check" in atalho[0]


def test_iss_leva_os_atalhos_dos_dados_de_calibracao():
    iss = _iss()
    assert "variable_explorer\\index.html" in iss
    assert "BAS-console.cmd" in iss


def test_compile_iss_avisa_quando_falta_o_inno(tmp_path, monkeypatch):
    """Sem ISCC o build tem de dizer o comando que resolve, nao estourar um
    FileNotFoundError cru."""
    import pytest
    monkeypatch.setattr(bi, "_iscc_path", lambda: None)
    with pytest.raises(SystemExit, match="winget install"):
        bi._compile_iss(tmp_path / "x.iss")


def test_aceitacao_passa_contra_o_proprio_repo():
    """Prova a ASSERCAO antes de usa-la contra a instalacao: rodando no repo
    de desenvolvimento, que sabemos bom, ela tem de passar. Se falhar aqui, o
    problema e' o teste e nao o instalador."""
    bi._acceptance(RAIZ, Path(sys.executable))


def test_aceitacao_reprova_layout_sem_dados(tmp_path):
    """E prova que ela REPROVA: sem o store, tem de falhar. Um teste de
    aceitacao que passa em qualquer coisa nao protege nada."""
    import pytest
    (tmp_path / "src").mkdir()
    with pytest.raises(SystemExit):
        bi._acceptance(tmp_path, Path(sys.executable))


def test_main_tem_help_sem_explodir():
    import pytest
    with pytest.raises(SystemExit) as e:
        bi.main(["--help"])
    assert e.value.code == 0


def test_etapas_do_pipeline_estao_todas_ligadas():
    """Contra o spec §5: sete etapas. Se alguem acrescentar uma funcao e
    esquecer de chama-la em main(), isto acusa."""
    import inspect
    fonte = inspect.getsource(bi.main)
    for nome in ("_fetch_embed", "_unpack_embed", "_enable_site",
                 "_pip_install", "_prune", "_copy_payload", "_make_ico",
                 "_write_leiame", "_write_console_cmd", "_render_iss",
                 "_compile_iss", "_acceptance"):
        assert nome in fonte, f"main() nao chama {nome}"
