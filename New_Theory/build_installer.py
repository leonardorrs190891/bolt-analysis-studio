# -*- coding: utf-8 -*-
"""Instalador Windows auto-contido do BAS V2 (2026-09-02).

    py -3.12 New_Theory/build_installer.py [--out dir] [--skip-download]

Spec:  docs/superpowers/specs/2026-09-02-instalador-auto-contido-design.md
Plano: docs/superpowers/plans/2026-09-02-instalador-auto-contido.md

NAO e' PyInstaller, e o motivo esta' medido no spec §2: o app lanca o servidor
de calibracao com `[sys.executable, "-m", ...]` (main_window.py:8195) e resolve
dados por `repo_root()` (parents[3] de validation/inputs.py, sondando
New_Theory/), duas premissas que um bundle congelado quebra. Aqui o
interpretador vai embutido e o layout de repositorio e' preservado.
"""
from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def _project_metadata(texto: str) -> dict:
    """version e author do setup.py, que e' a fonte unica dos dois.

    Lido por AST e nao por regex porque o valor pode ser concatenacao de
    literais; e ABORTA se faltar, porque um instalador sem versao nao
    substitui o anterior em Adicionar/Remover Programas.
    """
    meta = {}
    for node in ast.walk(ast.parse(texto)):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg in ("version", "author"):
                try:
                    meta[kw.arg] = ast.literal_eval(kw.value)
                except ValueError:
                    pass
    faltando = [k for k in ("version", "author") if not meta.get(k)]
    if faltando:
        raise SystemExit(
            f"[installer] setup.py nao declara {', '.join(faltando)}; "
            f"o instalador precisa dos dois (versao e autores do software)")
    return meta


def _iscc_path() -> Path | None:
    """ISCC.exe do Inno Setup, que o winget instala POR USUARIO.

    Medido em 2026-09-02: foi para %LOCALAPPDATA%/Programs/Inno Setup 6, NAO
    para Program Files. Por isso o registro vem primeiro e os caminhos fixos
    sao so' fallback.
    """
    try:
        import winreg
    except ImportError:
        winreg = None
    if winreg is not None:
        chaves = [
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for raiz, sub in chaves:
            try:
                with winreg.OpenKey(raiz, sub) as k:
                    for i in range(winreg.QueryInfoKey(k)[0]):
                        nome = winreg.EnumKey(k, i)
                        if "inno setup" not in nome.lower():
                            continue
                        with winreg.OpenKey(k, nome) as sk:
                            try:
                                loc = winreg.QueryValueEx(sk, "InstallLocation")[0]
                            except OSError:
                                continue
                        exe = Path(loc) / "ISCC.exe"
                        if exe.is_file():
                            return exe
            except OSError:
                continue
    candidatos = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    ]
    for c in candidatos:
        if c.is_file():
            return c
    return None


# Pacote embeddable oficial, PINADO. Medido em 2026-09-02: 10,6 MB, 35
# arquivos, traz python312._pth e NAO traz pip (a etapa 3 resolve isso).
# A API de downloads do python.org devolve HTTP 400 para consulta de hash,
# entao o valor e' fixado aqui e conferido a cada build.
PY_EMBED = {
    "version": "3.12.10",
    "url": ("https://www.python.org/ftp/python/3.12.10/"
            "python-3.12.10-embed-amd64.zip"),
    "sha256": "4acbed6dd1c744b0376e3b1cf57ce906f9dc9e95e68824584c8099a63025a3c3",
}


def _sha256(caminho: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _check_embed(zip_path: Path) -> Path:
    obtido = _sha256(zip_path)
    if obtido != PY_EMBED["sha256"]:
        raise SystemExit(
            f"[installer] sha256 do pacote embutido nao confere.\n"
            f"  esperado {PY_EMBED['sha256']}\n"
            f"  obtido   {obtido}\n"
            f"  arquivo  {zip_path}\n"
            f"Apague o cache e tente de novo; se persistir, o pin de "
            f"PY_EMBED precisa ser revisto contra python.org.")
    return zip_path


def _fetch_embed(cache: Path) -> Path:
    import urllib.request
    cache.mkdir(parents=True, exist_ok=True)
    destino = cache / PY_EMBED["url"].rsplit("/", 1)[-1]
    if destino.is_file():
        try:
            return _check_embed(destino)
        except SystemExit:
            destino.unlink()          # cache corrompido: baixa de novo
    print(f"  [1/7] baixando Python {PY_EMBED['version']} embeddable")
    urllib.request.urlretrieve(PY_EMBED["url"], destino)
    return _check_embed(destino)


def _unpack_embed(zip_path: Path, dest: Path) -> Path:
    import zipfile
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)
    return dest


def _enable_site(py_dir: Path) -> None:
    """Liga `site` e o site-packages no ._pth do pacote embeddable.

    O pacote vem com `import site` COMENTADO e sem site-packages no caminho:
    e' um interpretador para embutir em outro app, nao para receber pip. Sem
    esta correcao o pip instala com sucesso e o interpretador nao acha nada.
    Idempotente, porque o build pode ser reexecutado sobre o mesmo dir.
    """
    pths = list(py_dir.glob("python*._pth"))
    if not pths:
        raise SystemExit(f"[installer] nenhum python*._pth em {py_dir}; "
                         f"o pacote embeddable mudou de formato")
    pth = pths[0]
    linhas = [l.rstrip() for l in pth.read_text(encoding="utf-8").splitlines()]
    saida, viu_site, viu_sp = [], False, False
    for l in linhas:
        if l.strip() in ("import site", "#import site"):
            if not viu_site:
                saida.append("import site")
                viu_site = True
            continue
        if l.strip().lower() == r"lib\site-packages".lower():
            viu_sp = True
        saida.append(l)
    if not viu_sp:
        saida.append(r"Lib\site-packages")
    if not viu_site:
        saida.append("import site")
    pth.write_text("\n".join(x for x in saida if x != "") + "\n",
                   encoding="utf-8", newline="")


def _pip_install(py_exe: Path, specs: list) -> None:
    """Instala com o PROPRIO Python embutido, o que garante wheel da
    plataforma e da versao certas (o pip do sistema resolveria para o
    interpretador do sistema)."""
    import urllib.request
    get_pip = py_exe.parent / "get-pip.py"
    if not get_pip.is_file():
        print("  [2/7] bootstrap do pip no interpretador embutido")
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip)
    subprocess.check_call([str(py_exe), str(get_pip), "--no-warn-script-location"])
    print(f"  [3/7] instalando {len(specs)} dependencias no embutido")
    subprocess.check_call([str(py_exe), "-m", "pip", "install",
                           "--no-warn-script-location", *specs])


# Poda por SUBSISTEMA, com motivo por entrada. Medido 2026-09-02: o app importa
# exatamente QtWidgets, QtCore, QtGui, QtPrintSupport e QtSvg — nada mais, e
# zero WebEngine ou QML. A lista e' explicita e conservadora: no que houver
# duvida de dependencia, FICA dentro, e o teste de aceitacao da §8 roda DEPOIS
# desta etapa justamente porque este e' o ponto mais fragil do pipeline.
PODA = [
    ("Lib/site-packages/PyQt6/Qt6/qml", "QML: o app nao tem uma linha de QML"),
    ("Lib/site-packages/PyQt6/Qt6/translations", "traducoes do Qt: a UI nao usa tr() do Qt"),
    ("Lib/site-packages/PyQt6/Qt6/qsci", "QScintilla: nenhum import no repo"),
    ("Lib/site-packages/PyQt6/bindings", "stubs .pyi de desenvolvimento"),
    ("Lib/site-packages/PyQt6/**/*.pyi", "stubs .pyi de desenvolvimento"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Quick*.dll", "Quick/Quick3D: sem QML"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Qml*.dll", "Qml: sem QML"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Designer*.dll", "Designer: nao editamos .ui em runtime"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6ShaderTools.dll", "ShaderTools: dependencia do Quick"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt63D*.dll", "Qt3D: sem 3D"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Multimedia*.dll", "Multimedia: sem audio/video"),
    ("Lib/site-packages/PyQt6/Qt6/bin/av*.dll", "FFmpeg do Multimedia (avcodec sozinho = 13,3 MB)"),
    ("Lib/site-packages/PyQt6/Qt6/bin/sw*.dll", "FFmpeg do Multimedia"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Bluetooth.dll", "Bluetooth"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Nfc.dll", "NFC"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Positioning*.dll", "Positioning"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6WebChannel.dll", "WebChannel: sem WebEngine"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6WebSockets.dll", "WebSockets: o tuner usa http simples"),
    ("Lib/site-packages/PyQt6/Qt6/bin/Qt6Test.dll", "Qt Test: nao vai para producao"),
    ("Lib/site-packages/PyQt6/QtQuick*.pyd", "binding do Quick"),
    ("Lib/site-packages/PyQt6/QtQml.pyd", "binding do Qml"),
    ("Lib/site-packages/PyQt6/QtOpenGL*.pyd", "binding de OpenGL: nenhum import"),
    ("Lib/site-packages/PyQt6/QtMultimedia*.pyd", "binding de Multimedia"),
    ("Lib/site-packages/PyQt6/QAxContainer.pyd", "ActiveX"),
    ("Lib/site-packages/PyQt6/Qt6/plugins/qmltooling", "ferramentas de QML"),
    ("Lib/site-packages/scipy/**/tests", "suite de testes do scipy"),
    ("Lib/site-packages/numpy/**/tests", "suite de testes do numpy"),
    ("Lib/site-packages/matplotlib/tests", "suite de testes do matplotlib"),
    ("Lib/site-packages/**/__pycache__", "bytecode: o instalador nao precisa levar"),
]

# NAO PODAR, com motivo. opengl32sw.dll (19,7 MB) e d3dcompiler_47.dll (4,0 MB)
# sao o caminho de desenho por software: sem eles, maquina sem driver de GPU
# decente abre janela preta. 24 MB e' barato contra esse chamado de suporte.
NAO_PODAR = ("opengl32sw.dll", "d3dcompiler_47.dll")


def _prune(root: Path) -> tuple:
    bytes_fora = itens = 0
    for padrao, _motivo in PODA:
        for alvo in sorted(root.glob(padrao), reverse=True):
            if alvo.name in NAO_PODAR:
                continue
            if alvo.is_dir():
                tam = sum(f.stat().st_size for f in alvo.rglob("*") if f.is_file())
                shutil.rmtree(alvo, ignore_errors=True)
            elif alvo.is_file():
                tam = alvo.stat().st_size
                alvo.unlink()
            else:
                continue
            bytes_fora += tam
            itens += 1
    return bytes_fora, itens


# O que viaja com o instalador, por padrao e com motivo. Medido 2026-09-02:
# ~84 MB. Lista de PADROES e nao de diretorios porque BAS_V2_papers inteiro e'
# 871 MB e curve_library e' 87 MB dos quais 85,9 sao 15 PDF: copiar diretorio
# multiplica o instalador por 8 e cria um problema de direitos.
PAYLOAD = [
    ("run_app.py", "o lancador"),
    ("requirements.txt", "fonte dos specs que o preflight do run_app.py le"),
    ("LICENSE", "MIT do software"),
    ("DATA_LICENSE.md", "termos do corpus digitalizado"),
    ("README.md", "documentacao do repo"),
    ("CITATION.cff", "como citar, com o DOI"),
    ("src/**/*.py", "o pacote"),
    ("src/**/*.json", "bases de dados de material do pacote"),
    ("src/**/*.svg", "icones do tema"),
    ("src/**/*.qss", "folhas de estilo"),
    ("Models/CALIBRATION_AND_VALIDATION/validation_store.json", "as 210 analises"),
    ("Models/CALIBRATION_AND_VALIDATION/curve_library/**/*.csv", "curvas digitalizadas"),
    ("Models/CALIBRATION_AND_VALIDATION/curve_library/**/*.md", "notas de aparato"),
    ("Models/CALIBRATION_AND_VALIDATION/curve_library/**/*.png", "recortes de figura"),
    ("New_Theory/adopted_configs.json", "constantes adotadas por rig"),
    ("New_Theory/ablation/*.json", "ablacao carimbada"),
    ("New_Theory/holdout/*.json", "hold-out carimbado"),
    ("New_Theory/paper/*.json", "cache de analise do artigo"),
    ("New_Theory/variable_explorer/**/*", "27 paginas por artigo + 207 reports"),
    ("BAS_V2_papers/*/apparatus_notes/*.md", "notas R4/R5 (caminho exigido pelo registry)"),
    ("BAS_V2_papers/*/digitized_csv/*.csv", "curvas R4/R5"),
    ("Models/EXPERIMENTAL_UFU/reference_curves/*.csv",
     "3 casos UFU_LAB: sem isto eles ficam somente-leitura no app instalado"),
    ("Models/USER_CASES/*.csv", "1 caso USER de exemplo, pelo mesmo motivo"),
    ("Models/USER_CASES/*.bascase.json",
     "o que REGISTRA o caso USER: sem o .bascase.json o registro desaparece e "
     "a analise dele no store fica orfa (pego pela aceitacao em 2026-09-02)"),
    # Levantado por `grep -rn "repo_root()" src/` em 2026-09-02, depois de a
    # aceitacao pegar dois destes um a um. Sao TODOS os arquivos de dados que o
    # app resolve a partir da raiz: faltando um, o app importa e quebra so' na
    # hora de abrir um caso.
    ("New_Theory/report_data.json", "semente da galeria, lida por case_registry"),
    ("New_Theory/joint_calibrations.json",
     "constantes congeladas (inputs.SHARED_JSON), lidas por material_kwargs_for"),
    ("New_Theory/convergence_ledger.json", "ledger de convergencia dos reports"),
    ("Models/CALIBRATION_AND_VALIDATION/error_budget.json",
     "orcamento de erro por fonte (error_budget.BUDGET_PATH)"),
]

# Nunca, sob nenhum padrao. O .pdf esta' aqui por DIREITOS: e' material de
# editora e o instalador e' distribuido.
NUNCA = (".pdf", ".pyc", ".pyo")
# `_needs_review` e' rascunho de digitalizacao: medido 2026-09-02, ZERO dos 210
# casos aponta para la', e sao os nomes mais longos do repo (183 chars de
# caminho relativo contra 173 sem eles) — o que importa por causa do MAX_PATH.
NUNCA_EM = ("__pycache__", ".bkp_", ".git", "_needs_review")


# Orcamento de caminho. O Windows corta em 260, e o ISCC do Inno le os arquivos
# de origem SEM o prefixo estendido: medido 2026-09-02, o build dentro do repo
# (95 chars) somado ao pior relativo (173) da' 269 e o ISCC aborta com "cannot
# find the path specified" no meio da compressao, sem dizer qual arquivo.
MAX_PATH = 260
ORCAMENTO_INSTALL = 80          # chars reservados para a raiz de instalacao


def _check_path_budget(build: Path, arquivos: list) -> int:
    """Aborta ANTES do ISCC se o caminho mais longo nao couber.

    Trocar a falha silenciosa do compilador por uma mensagem que diz o arquivo
    e o quanto falta. Devolve o pior comprimento relativo, para o relatorio.
    """
    if not arquivos:
        return 0
    pior = max(arquivos, key=lambda p: len(str(p)))
    n_pior = len(str(pior))
    total = len(str(build)) + 1 + n_pior
    if total >= MAX_PATH:
        raise SystemExit(
            f"[installer] o caminho de build passa do MAX_PATH e o ISCC nao "
            f"consegue ler os arquivos:\n"
            f"  raiz de build : {len(str(build))} chars ({build})\n"
            f"  pior relativo : {n_pior} chars ({pior})\n"
            f"  total         : {total} (limite {MAX_PATH})\n"
            f"Use --build-dir com um caminho mais curto.")
    if n_pior + 1 + ORCAMENTO_INSTALL >= MAX_PATH:
        print(f"  [AVISO] o pior caminho relativo tem {n_pior} chars; com uma "
              f"raiz de instalacao acima de {MAX_PATH - n_pior - 1} chars o "
              f"app nao achara' esse arquivo ({pior})")
    return n_pior


_PREFIXO = "\\\\?\\"        # os quatro caracteres  \\?\  do prefixo estendido


def _longpath(p: Path) -> Path:
    """Caminho com o prefixo estendido do Windows, que levanta o MAX_PATH.

    Medido 2026-09-02: o CSV mais longo do payload tem 183 chars de caminho
    RELATIVO, e o proprio caminho de origem ja' tem 251. Qualquer raiz de
    destino acima de ~77 chars passa dos 260 do MAX_PATH, e o destino default
    do instalador (%LOCALAPPDATA%/Programs/Bolt Analysis Studio V2 no perfil
    de um usuario) passa. Sem isto o build falha por FileNotFoundError num
    .csv do meio do corpus, em maquina real e nao so' no teste. O
    publish_snapshot.py resolve o mesmo problema na extracao do tar.
    """
    if os.name != "nt":
        return p
    s = str(p)
    if s.startswith(_PREFIXO):
        return p
    return Path(_PREFIXO + str(Path(s).resolve()))


def _mkdirs_long(d: Path) -> None:
    """mkdir -p que sobrevive ao MAX_PATH.

    Nem `Path(prefixado).mkdir(parents=True)` nem `os.makedirs(prefixado)`
    servem: os dois sobem a arvore de pais e chegam a tentar criar o proprio
    `\\\\?\\`, o que da' WinError 123. A saida e' descer a arvore a partir da
    parte curta, prefixando SO' a chamada de criacao de cada nivel.
    """
    partes = list(reversed([d, *d.parents]))
    for nivel in partes:
        if nivel.parent == nivel:          # a raiz do drive
            continue
        alvo = _longpath(nivel)
        if not os.path.isdir(alvo):
            try:
                os.mkdir(alvo)
            except FileExistsError:
                pass


def _payload_files(root: Path) -> list:
    achados = set()
    for padrao, _motivo in PAYLOAD:
        for p in root.glob(padrao):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if p.suffix.lower() in NUNCA or any(t in rel for t in NUNCA_EM):
                continue
            achados.add(p)
    return sorted(achados)


def _copy_payload(root: Path, dest: Path) -> tuple:
    n = total = 0
    for p in _payload_files(root):
        alvo = dest / p.relative_to(root)
        _mkdirs_long(alvo.parent)
        shutil.copy2(_longpath(p), _longpath(alvo))
        n += 1
        total += p.stat().st_size
    return n, total


# Cor do glifo do icone. Vem do tema CLARO e nao do padrao de icons.py
# (Theme.TEXT), que hoje resolve para o tema escuro (#cdd6f4): glifo quase
# branco sobre fundo transparente fica invisivel no Explorer e no instalador.
ICO_FG = "#4c4f69"          # THEME_LIGHT["TEXT"] de gui/theme.py

_ICO_SIZES = (16, 32, 48, 64, 128, 256)


def _make_ico(svg: Path, dest: Path) -> Path:
    """Renderiza o SVG monocromatico do tema em .ico.

    O SVG e' um TEMPLATE: traz o token literal `__FG__` no lugar da cor, que
    icons.py substitui em runtime. Aqui a substituicao e' por ICO_FG. Qt grava
    'ico' nativamente (QImageWriter), entao nao entra dependencia nova so'
    para isto.
    """
    from PyQt6.QtCore import QByteArray, Qt
    from PyQt6.QtGui import QImage, QPainter
    from PyQt6.QtSvg import QSvgRenderer

    original = svg.read_bytes()
    bruto = original.replace(b"__FG__", ICO_FG.encode("ascii"))
    if b"__FG__" in original and b"__FG__" in bruto:
        raise SystemExit("[installer] substituicao de __FG__ falhou")

    dest.parent.mkdir(parents=True, exist_ok=True)
    lado = max(_ICO_SIZES)
    img = QImage(lado, lado, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(img)
    QSvgRenderer(QByteArray(bruto)).render(pintor)
    pintor.end()
    if not img.save(str(dest), "ICO"):
        raise SystemExit(f"[installer] Qt nao gravou o .ico em {dest}")
    return dest


DOI_CONCEITO = "10.5281/zenodo.22233437"

_LEIAME = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Bolt Analysis Studio V2 {versao} - leia-me</title>
<style>
 body{{font:15px/1.6 "Segoe UI",system-ui,sans-serif;color:#2b2b2b;
      background:#fbfbfd;margin:0;padding:2.5rem 1.5rem}}
 main{{max-width:46rem;margin:0 auto}}
 h1{{font-size:1.6rem;margin:0 0 .2rem}}
 h2{{font-size:1.15rem;margin:2rem 0 .5rem;border-bottom:1px solid #dcdce4;
     padding-bottom:.3rem}}
 .sub{{color:#6b6b76;margin:0 0 1.5rem}}
 code{{background:#eef0f5;padding:.1rem .35rem;border-radius:3px;font-size:.9em}}
 kbd{{background:#fff;border:1px solid #c3c3cc;border-bottom-width:2px;
      border-radius:4px;padding:.05rem .35rem;font-size:.85em}}
 table{{border-collapse:collapse;width:100%;margin:.5rem 0}}
 th,td{{text-align:left;padding:.4rem .6rem;border-bottom:1px solid #e6e6ee;
        vertical-align:top}}
 th{{color:#555;font-weight:600}}
 .nota{{background:#fff8e6;border-left:3px solid #e0a900;padding:.7rem 1rem;
        margin:1rem 0}}
 footer{{margin-top:2.5rem;color:#6b6b76;font-size:.9em}}
 a{{color:#3b5bdb}}
</style></head><body><main>

<h1>Bolt Analysis Studio V2</h1>
<p class="sub">Vers&atilde;o {versao} &middot; {autores}</p>

<h2>Como abrir</h2>
<p>Menu Iniciar &rarr; <b>Bolt Analysis Studio V2</b>. Se a janela n&atilde;o
aparecer, rode <code>BAS-console.cmd</code> na pasta de instala&ccedil;&atilde;o:
&eacute; o mesmo programa, com console, mostrando a mensagem de erro.</p>

<h2>Onde est&atilde;o os exemplos dos artigos</h2>
<p>No m&oacute;dulo <b>Results</b> (<kbd>Ctrl</kbd>+<kbd>5</kbd>), sub-aba
<b>Validation</b>. Voc&ecirc; encontra uma &aacute;rvore <b>artigo &rarr;
curva</b>: {n_fontes} fontes da literatura e {n_casos} curvas, cada uma com o
erro m&eacute;dio absoluto ao lado. Selecionando uma curva, aparece o dado
digitalizado contra a previs&atilde;o do modelo.</p>

<h2>Como ver os dados de calibra&ccedil;&atilde;o</h2>
<table>
<tr><th>Caminho</th><th>O que mostra</th></tr>
<tr><td>Bot&atilde;o <b>Report HTML</b>, no m&oacute;dulo Validation</td>
    <td>Report daquele caso: condi&ccedil;&otilde;es do ensaio, modelo
        massa-mola-amortecedor, res&iacute;duo com as tr&ecirc;s pernas do
        crit&eacute;rio, decomposi&ccedil;&atilde;o por mecanismo e <b>as
        constantes com a proced&ecirc;ncia de cada uma</b></td></tr>
<tr><td>Bot&atilde;o <b>Report geral</b></td>
    <td>Report mestre, com todos os casos e o censo</td></tr>
<tr><td><a href="New_Theory/variable_explorer/index.html">New_Theory/variable_explorer/index.html</a></td>
    <td>Uma p&aacute;gina por artigo: figuras do paper, tabela de
        condi&ccedil;&otilde;es, DOI, nota de aparato e todas as curvas daquela
        fonte</td></tr>
<tr><td><code>New_Theory/adopted_configs.json</code></td>
    <td>As constantes adotadas por bancada, com o texto de
        proced&ecirc;ncia</td></tr>
</table>

<h2>O que n&atilde;o vem no instalador</h2>
<p>Os <b>PDF dos artigos de origem</b> n&atilde;o s&atilde;o
distribu&iacute;dos: s&atilde;o publica&ccedil;&otilde;es de editora, e
redistribu&iacute;-las n&atilde;o nos cabe. O que vem s&atilde;o as curvas
digitalizadas e as notas de aparato, que &eacute; do que o programa precisa.
Cada p&aacute;gina de artigo traz o <b>DOI</b> da fonte para voc&ecirc; buscar
o original.</p>

<div class="nota">Este instalador n&atilde;o &eacute; assinado digitalmente. Na
primeira execu&ccedil;&atilde;o o Windows pode exibir o aviso de aplicativo
n&atilde;o reconhecido.</div>

<footer>
<p>Licen&ccedil;a <b>MIT</b> para o software. Autores: {autores}.</p>
<p>Software e corpus arquivados em <code>https://doi.org/{doi}</code>.</p>
</footer>
</main></body></html>
"""


def _write_leiame(dest: Path, meta: dict, n_fontes: int, n_casos: int) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_LEIAME.format(versao=meta["version"],
                                   autores=meta["author"],
                                   n_fontes=n_fontes, n_casos=n_casos,
                                   doi=DOI_CONCEITO),
                    encoding="utf-8", newline="")
    return dest


# O atalho do Menu Iniciar usa pythonw.exe, que NAO tem console: uma mensagem
# do preflight de dependencias seria invisivel ali. Este .cmd e' o caminho de
# diagnostico — mesmo app, com console, e COM o preflight ligado.
_CONSOLE_CMD = (
    "@echo off\r\n"
    "rem Diagnostico: mesmo programa do atalho, mas com console e COM o\r\n"
    "rem preflight de dependencias ligado (o atalho passa --skip-deps-check\r\n"
    "rem porque pythonw.exe nao tem console onde mostrar a mensagem).\r\n"
    "cd /d \"%~dp0\"\r\n"
    "\"%~dp0python\\python.exe\" \"%~dp0run_app.py\" %*\r\n"
    "echo.\r\n"
    "pause\r\n"
)


def _write_console_cmd(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_CONSOLE_CMD, encoding="ascii", newline="")
    return dest


def _render_iss(template: str, meta: dict, build_dir: Path,
                out_dir: Path) -> str:
    """Substitui os campos @CAMPO@ do template.

    Usa @CAMPO@ e nao str.format porque o .iss e' cheio de {app}, {group} e
    {localappdata}: format() tentaria interpretar cada um como placeholder, e
    o proprio `AppId={{GUID}` do Inno usa chave dupla de proposito.
    """
    import re

    troca = {
        "@VERSION@": meta["version"],
        "@AUTHOR@": meta["author"],
        "@BUILDDIR@": str(build_dir),
        "@OUTDIR@": str(out_dir),
        "@ICO@": str(build_dir / "bas.ico"),
    }
    saida = template
    for k, v in troca.items():
        saida = saida.replace(k, v)
    # so' linhas de DIRETIVA: o cabecalho do template documenta a convencao
    # @MAIUSCULO@ de proposito, e acusa-la faria o build abortar por causa da
    # propria documentacao (";" e' comentario no .iss).
    sobrou = [l for l in saida.splitlines()
              if re.search(r"@[A-Z]+@", l) and not l.lstrip().startswith(";")]
    if sobrou:
        raise SystemExit(
            f"[installer] campo nao substituido no .iss: {sobrou[0].strip()}")
    return saida


def _compile_iss(iss: Path) -> Path:
    iscc = _iscc_path()
    if iscc is None:
        raise SystemExit(
            "[installer] ISCC.exe nao encontrado. Instale o Inno Setup:\n"
            "    winget install JRSoftware.InnoSetup")
    print(f"  [7/7] compilando com {iscc}")
    subprocess.check_call([str(iscc), str(iss)])
    return iss


# Roda DENTRO da instalacao, com o interpretador embutido. As assercoes sao as
# de tests/test_corpus_coverage.py: o mesmo contrato, aferido no artefato
# entregue em vez do repo de desenvolvimento.
ACEITE_SRC = r'''
import os, sys
_raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_raiz, "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"))

import numpy, scipy, matplotlib                                   # noqa: F401
matplotlib.use("Agg")
from PyQt6.QtWidgets import QApplication
app = QApplication([])

from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.store import ValidationStore
from bolt_analysis_studio.validation.gui_bridge import build_case_model
from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser

recs = all_records()
if not recs:
    raise SystemExit("ACEITE: registry vazio na instalacao")
store = ValidationStore()
if not store.all_ids():
    raise SystemExit("ACEITE: store vazio na instalacao (%s)" % store.path)

ids_reg, ids_st = {r.case_id for r in recs}, set(store.all_ids())
if ids_reg - ids_st:
    faltam = sorted(ids_reg - ids_st)
    raise SystemExit("ACEITE: %d casos sem analise: %s"
                     % (len(faltam), faltam[:5]))
if ids_st - ids_reg:
    # NOMEAR o orfao, nao contar: em 2026-09-02 este ramo acusou "1 analise
    # orfa" e o culpado era o .bascase.json do caso USER faltando no payload.
    # Sem o id, achar isso custou uma investigacao que a mensagem resolveria.
    orfas = sorted(ids_st - ids_reg)
    raise SystemExit("ACEITE: %d analises orfas (no store, sem registro): %s"
                     % (len(orfas), orfas[:5]))

for r in recs:
    res = store.get(r.case_id)
    for k in ("mae", "maxerr", "resid_std"):
        if getattr(res, k, None) is None:
            raise SystemExit("ACEITE: %s sem %s" % (r.case_id, k))
    if build_case_model(r) is None:
        raise SystemExit("ACEITE: %s nao abre no modelo" % r.case_id)
    if r.csv_path is not None and not os.path.isfile(str(r.csv_path)):
        raise SystemExit("ACEITE: %s sem o CSV (%s)" % (r.case_id, r.csv_path))

br = ValidationBrowser(store=store)
br.populate()
tree = br.tree
n_src = tree.topLevelItemCount()
celulas = [tree.topLevelItem(i).child(j)
           for i in range(n_src)
           for j in range(tree.topLevelItem(i).childCount())]
if len(celulas) != len(recs):
    raise SystemExit("ACEITE: arvore com %d casos, registry com %d"
                     % (len(celulas), len(recs)))
if n_src != len({r.source for r in recs}):
    raise SystemExit("ACEITE: contagem de fontes divergente")
ruins = [c.text(0) for c in celulas
         if c.text(1).strip() in ("", "\u2014", "erro")]
if ruins:
    raise SystemExit("ACEITE: %d casos sem analise na arvore: %s"
                     % (len(ruins), ruins[:3]))

print("ACEITE OK: %d fontes, %d casos" % (n_src, len(celulas)))
'''


def _acceptance(install_dir: Path, py_exe: Path) -> None:
    """Roda o app DA INSTALACAO e afere o contrato do corpus.

    E' o que transforma "auto-contido" em afirmacao verificada. Roda DEPOIS da
    poda de proposito: a poda e' o ponto mais fragil do pipeline.
    """
    script = install_dir / "_aceite.py"
    script.write_text(ACEITE_SRC, encoding="utf-8")
    try:
        r = subprocess.run([str(py_exe), str(script)], cwd=str(install_dir),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    finally:
        script.unlink(missing_ok=True)
    if r.returncode != 0:
        raise SystemExit(
            f"[installer] ACEITACAO REPROVADA, nenhum instalador entregue.\n"
            f"{(r.stdout or '').strip()}\n{(r.stderr or '').strip()}")
    linhas = [l for l in (r.stdout or "").strip().splitlines() if l.strip()]
    print(f"  {linhas[-1] if linhas else 'ACEITE OK'}")


def main(argv=None) -> int:
    import argparse
    import tempfile

    ap = argparse.ArgumentParser(
        description="Instalador Windows auto-contido do Bolt Analysis Studio V2")
    ap.add_argument("--out", default=str(RAIZ / "dist"),
                    help="diretorio de saida do .exe (padrao: dist/)")
    ap.add_argument("--build-dir", default=None,
                    help="arvore de montagem. O padrao fica no TEMP e NAO "
                         "dentro do repo de proposito: o repo esta' fundo "
                         "demais e o ISCC estoura o MAX_PATH ao ler os "
                         "arquivos de origem")
    ap.add_argument("--skip-download", action="store_true",
                    help="reusa o Python embutido ja desempacotado no build-dir")
    ap.add_argument("--skip-acceptance", action="store_true",
                    help="NAO use para entregar: pula a aceitacao da §8")
    args = ap.parse_args(argv)

    meta = _project_metadata((RAIZ / "setup.py").read_text(encoding="utf-8"))
    inst = RAIZ / "New_Theory" / "installer"
    # A montagem sai do repo: medido 2026-09-02, a raiz do _build dentro dele
    # tem 95 chars e o pior caminho relativo do payload 173, o que da' 269 e
    # faz o ISCC abortar sem dizer qual arquivo.
    build = (Path(args.build_dir) if args.build_dir
             else Path(tempfile.gettempdir()) / "bas_v2_build")
    py_dir = build / "python"
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Bolt Analysis Studio V2 {meta['version']}")
    print(f"  autores: {meta['author']}")

    if not args.skip_download:
        if build.exists():
            shutil.rmtree(build, ignore_errors=True)
        build.mkdir(parents=True, exist_ok=True)
        z = _fetch_embed(inst / "_cache")
        _unpack_embed(z, py_dir)
        _enable_site(py_dir)
        specs = [s.strip() for s in
                 (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines()
                 if s.strip() and not s.strip().startswith("#")]
        _pip_install(py_dir / "python.exe", specs)
        fora, n_itens = _prune(py_dir)
        print(f"  [4/7] poda: -{fora / 2**20:.1f} MB em {n_itens} itens")
    elif not (py_dir / "python.exe").is_file():
        raise SystemExit(f"[installer] --skip-download mas {py_dir} nao tem "
                         f"python.exe; rode uma vez sem a flag")

    relativos = [p.relative_to(RAIZ) for p in _payload_files(RAIZ)]
    n_pior = _check_path_budget(build, relativos)
    n_arq, tam = _copy_payload(RAIZ, build)
    print(f"  [5/7] payload: {n_arq} arquivos, {tam / 2**20:.1f} MB "
          f"(pior caminho relativo: {n_pior} chars)")

    _make_ico(RAIZ / "src" / "bolt_analysis_studio" / "resources" / "icons"
              / "app_icon.svg", build / "bas.ico")

    # contagem do leiame vem do REGISTRY, nunca digitada
    sys.path.insert(0, str(RAIZ / "src"))
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    n_fontes = len({r.source for r in recs})
    _write_leiame(build / "LEIAME.html", meta, n_fontes, len(recs))
    _write_console_cmd(build / "BAS-console.cmd")
    print(f"  [6/7] icone, leiame ({n_fontes} fontes, {len(recs)} casos) "
          f"e BAS-console.cmd")

    iss_txt = _render_iss(
        (inst / "bas_v2.iss.template").read_text(encoding="utf-8"),
        meta, build, out_dir)
    iss = build / "bas_v2.iss"
    iss.write_text(iss_txt, encoding="utf-8", newline="")
    _compile_iss(iss)

    exe = out_dir / f"BAS-V2-Setup-{meta['version']}.exe"
    if not exe.is_file():
        raise SystemExit(f"[installer] o ISCC terminou mas {exe} nao existe")

    if not args.skip_acceptance:
        with tempfile.TemporaryDirectory(prefix="bas_aceite_") as td:
            alvo = Path(td) / "BAS"
            print("  aceitacao: instalando em diretorio temporario")
            subprocess.check_call([str(exe), "/SILENT", "/SUPPRESSMSGBOXES",
                                   "/NORESTART", f"/DIR={alvo}"])
            try:
                _acceptance(alvo, alvo / "python" / "python.exe")
            finally:
                unins = alvo / "unins000.exe"
                if unins.is_file():
                    subprocess.call([str(unins), "/SILENT",
                                     "/SUPPRESSMSGBOXES", "/NORESTART"])

    print(f"\nOK: {exe}  ({exe.stat().st_size / 2**20:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
