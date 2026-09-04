# Instalador Windows auto-contido do BAS V2 — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** gerar `BAS-V2-Setup-2.0.0.exe`, instalador Windows x64 por usuário que
carrega o interpretador Python, as 4 dependências, o código, as 210 análises
pré-calculadas e a documentação por artigo, sem exigir nada instalado no destino.

**Architecture:** pacote *embeddable* oficial do Python 3.12.10 + `pip install`
das dependências dentro dele + payload copiado no layout que `repo_root()`
exige, tudo empacotado pelo Inno Setup. Não é PyInstaller: o app lança
subprocesso com `sys.executable -m` e resolve dados por caminho de repositório,
duas premissas que um bundle congelado quebra (spec §2).

**Tech Stack:** Python 3.12 (stdlib: `urllib`, `hashlib`, `zipfile`, `ast`,
`subprocess`, `shutil`), PyQt6 (só para gerar o `.ico`), Inno Setup 6.7.3
(`ISCC.exe`), pytest.

**Spec:** `docs/superpowers/specs/2026-09-02-instalador-auto-contido-design.md`

## Global Constraints

- **Plataforma:** Windows x64 apenas. O build precisa de rede (python.org +
  PyPI); o instalador gerado não precisa de rede.
- **Python embutido pinado:** versão `3.12.10`, URL
  `https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip`,
  SHA-256 `4acbed6dd1c744b0376e3b1cf57ce906f9dc9e95e68824584c8099a63025a3c3`
  (10,6 MB, 35 arquivos, traz `python312._pth`, não traz pip). Verificado em
  2026-09-02.
- **Dependências:** lidas de `requirements.txt` (`numpy>=1.21.0`,
  `scipy>=1.7.0`, `matplotlib>=3.5.0`, `PyQt6>=6.4.0`). Nunca digitadas de novo
  no build: o `run_app.py` já lê desse arquivo.
- **Versão e autores:** lidos do `setup.py` (`version="2.0.0"`, `author=`).
  Nunca digitados no `.iss`.
- **PDF nunca entram.** Nenhum padrão do payload pode casar `*.pdf`. São 659 MB
  de material de editora; embutir é redistribuição (spec §4).
- **Layout obrigatório:** `repo_root()` = `parents[3]` de
  `src/bolt_analysis_studio/validation/inputs.py`, com fallback `parents[2]`
  sondando `New_Theory/`. A raiz da instalação **é** o repo root.
- **Módulos Qt que o app usa (medido):** `QtWidgets`, `QtCore`, `QtGui`,
  `QtPrintSupport`, `QtSvg`. Nada mais. Zero uso de WebEngine ou QML.
- **Nomes de rodada preservados literalmente:** `BAS_V2_papers/E. Rodada 4
  (deep-research 2026-07-11)/apparatus_notes` e `.../F. Rodada 5 (limitacoes
  2026-07-16)/apparatus_notes` — com espaços, ponto e parênteses.
- **Estilo do repo:** testes em `tests/test_*.py`, funções simples, sem classes;
  comentários explicam o *porquê*. O build imprime progresso por etapa como os
  outros `New_Theory/build_*.py`.

---

### Task 1: Metadados do projeto e localização do ISCC

**Files:**
- Create: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: nada (primeira task).
- Produces: `RAIZ: Path` (raiz do repo), `_project_metadata(texto: str) -> dict`
  com chaves `version: str` e `author: str`; `_iscc_path() -> Path | None`.

- [ ] **Step 1: Write the failing test**

```python
"""Build do instalador auto-contido (2026-09-02).

Spec: docs/superpowers/specs/2026-09-02-instalador-auto-contido-design.md
As partes que DECIDEM sao puras (texto -> metadados, arvore -> o que podar,
arvore -> o que copiar) para poderem ser testadas sem baixar 10 MB de Python
nem montar uma arvore de 400 MB.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "New_Theory"))

import build_installer as bi                                   # noqa: E402


def test_metadados_saem_do_setup_py():
    texto = (
        'setup(\n'
        '    name="bolt-analysis-studio",\n'
        '    version="2.0.0",\n'
        '    author="Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva",\n'
        '    author_email="leorrs@ancora_interna.br",\n'
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
    assert meta["version"] == "2.0.0"
    assert "Leonardo" in meta["author"] and "Neilon" in meta["author"]


def test_metadados_faltando_versao_levanta():
    """Um instalador sem versao e' pior que um build que para: a entrada em
    Adicionar/Remover Programas fica sem numero e a proxima nao substitui."""
    import pytest
    with pytest.raises(SystemExit):
        bi._project_metadata('setup(name="x")\n')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_installer'`

- [ ] **Step 3: Write minimal implementation**

Crie `New_Theory/build_installer.py`:

```python
# -*- coding: utf-8 -*-
"""Instalador Windows auto-contido do BAS V2 (2026-09-02).

    py -3.12 New_Theory/build_installer.py [--out dir] [--skip-download]

Spec: docs/superpowers/specs/2026-09-02-instalador-auto-contido-design.md

NAO e' PyInstaller, e o motivo esta' medido no spec §2: o app lanca o servidor
de calibracao com `[sys.executable, "-m", ...]` e resolve dados por
`repo_root()`, duas premissas que um bundle congelado quebra. Aqui o
interpretador vai embutido e o layout de repositorio e' preservado.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def _project_metadata(texto: str) -> dict:
    """version e author do setup.py, que e' a fonte unica dos dois.

    Lido por AST e nao por regex porque o valor pode ser uma concatenacao de
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

    Medido em 2026-09-02: foi para %LOCALAPPDATA%\\Programs\\Inno Setup 6, NAO
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Verify ISCC is found on this machine**

Run: `py -3.12 -c "import sys; sys.path.insert(0,'New_Theory'); import build_installer as b; print(b._iscc_path())"`
Expected: `C:\Users\leo_r\AppData\Local\Programs\Inno Setup 6\ISCC.exe`

- [ ] **Step 6: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: metadados do setup.py e ISCC localizado pelo registro"
```

---

### Task 2: Baixar e verificar o Python embutido

**Files:**
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: `RAIZ` da Task 1.
- Produces: `PY_EMBED: dict` com `version`/`url`/`sha256`;
  `_sha256(path: Path) -> str`; `_fetch_embed(cache: Path) -> Path` (devolve o
  zip verificado).

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k "sha256 or pin or hash"`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute '_sha256'`

- [ ] **Step 3: Write minimal implementation**

Acrescente a `New_Theory/build_installer.py`:

```python
import hashlib
import urllib.request

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (6 passed)

- [ ] **Step 5: Verify the real download against the pin**

Run: `py -3.12 -c "import sys; sys.path.insert(0,'New_Theory'); import build_installer as b; from pathlib import Path; print(b._fetch_embed(Path('New_Theory/installer/_cache')))"`
Expected: imprime o caminho do zip, sem exceção (baixa ~10,6 MB na primeira vez)

- [ ] **Step 6: Ignore the cache in git**

Acrescente a `.gitignore`:

```
New_Theory/installer/_cache/
New_Theory/installer/_build/
dist/
```

- [ ] **Step 7: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py .gitignore
git commit -m "instalador: Python embutido pinado e verificado por sha256"
```

---

### Task 3: Habilitar pip no embutido e instalar as dependências

**Files:**
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: `_fetch_embed` da Task 2.
- Produces: `_unpack_embed(zip_path: Path, dest: Path) -> Path` (devolve o dir
  do python); `_enable_site(py_dir: Path) -> None`;
  `_pip_install(py_exe: Path, specs: list[str]) -> None`.

- [ ] **Step 1: Write the failing test**

```python
def test_enable_site_liga_o_site_e_o_site_packages(tmp_path):
    """O pacote embeddable vem com `import site` COMENTADO e sem
    site-packages no caminho. Sem corrigir isso, o pip instala e o
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k enable_site`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute '_enable_site'`

- [ ] **Step 3: Write minimal implementation**

```python
import zipfile


def _unpack_embed(zip_path: Path, dest: Path) -> Path:
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


def _pip_install(py_exe: Path, specs: list[str]) -> None:
    """Instala com o PROPRIO Python embutido, o que garante wheel da
    plataforma e da versao certas (pip do sistema resolveria para o
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
```

Acrescente `import shutil` ao topo do arquivo.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (9 passed)

- [ ] **Step 5: Prove the embedded interpreter really imports the deps**

```bash
py -3.12 - <<'PY'
import sys; sys.path.insert(0, "New_Theory")
import build_installer as b
from pathlib import Path
z = b._fetch_embed(Path("New_Theory/installer/_cache"))
d = b._unpack_embed(z, Path("New_Theory/installer/_build/python"))
b._enable_site(d)
b._pip_install(d / "python.exe", ["numpy>=1.21.0", "scipy>=1.7.0",
                                  "matplotlib>=3.5.0", "PyQt6>=6.4.0"])
PY
py -3.12 -c "import subprocess; subprocess.check_call([r'New_Theory\installer\_build\python\python.exe','-c','import numpy,scipy,matplotlib,PyQt6;from PyQt6.QtWidgets import QApplication;print(\"embutido OK\", numpy.__version__)'])"
```

Expected: `embutido OK 2.x.x` — se falhar aqui, `_enable_site` não fez o
serviço e nada adiante funciona.

- [ ] **Step 6: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: pip habilitado no embeddable e dependencias instaladas nele"
```

---

### Task 4: A poda, com tamanho medido

**Files:**
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: o dir do python da Task 3.
- Produces: `PODA: list[tuple[str, str]]` (padrão, motivo);
  `_prune(root: Path) -> tuple[int, int]` (bytes removidos, itens removidos).

- [ ] **Step 1: Write the failing test**

```python
def test_poda_remove_o_que_o_app_nao_importa(tmp_path):
    """Medido: o app importa QtWidgets, QtCore, QtGui, QtPrintSupport e QtSvg.
    Nada mais, e zero WebEngine ou QML."""
    q = tmp_path / "Lib" / "site-packages" / "PyQt6" / "Qt6" / "bin"
    q.mkdir(parents=True)
    for nome in ("Qt6Core.dll", "Qt6Widgets.dll", "Qt6Svg.dll",
                 "Qt6Quick.dll", "Qt6Qml.dll", "Qt6Designer.dll",
                 "avcodec-61.dll", "opengl32sw.dll"):
        (q / nome).write_bytes(b"x" * 1024)
    (tmp_path / "Lib" / "site-packages" / "PyQt6" / "Qt6" / "qml").mkdir()
    (tmp_path / "Lib" / "site-packages" / "PyQt6" / "Qt6" / "qml" / "a.qml").write_bytes(b"y")

    bytes_fora, itens = bi._prune(tmp_path)

    restantes = {f.name for f in q.iterdir()}
    assert {"Qt6Core.dll", "Qt6Widgets.dll", "Qt6Svg.dll"} <= restantes
    assert not {"Qt6Quick.dll", "Qt6Qml.dll", "Qt6Designer.dll",
                "avcodec-61.dll"} & restantes
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k poda`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute '_prune'`

- [ ] **Step 3: Write minimal implementation**

```python
# Poda por SUBSISTEMA, com motivo por entrada. Medido 2026-09-02: PyQt6 sao
# 207 MB, dos quais Qt6/bin = 143 MB em 109 arquivos; os 5 modulos que o app
# importa somam 28,8 MB de DLL. A lista e' explicita e conservadora: no que
# houver duvida de dependencia, fica dentro, e o teste de aceitacao da Task 9
# roda DEPOIS desta etapa justamente porque este e' o ponto mais fragil.
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


def _prune(root: Path) -> tuple[int, int]:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (12 passed)

- [ ] **Step 5: Measure the real prune, and prove Qt still starts**

```bash
py -3.12 - <<'PY'
import sys, subprocess; sys.path.insert(0, "New_Theory")
import build_installer as b
from pathlib import Path
d = Path("New_Theory/installer/_build/python")
antes = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
fora, n = b._prune(d)
depois = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
print(f"antes {antes/2**20:.1f} MB -> depois {depois/2**20:.1f} MB "
      f"(-{fora/2**20:.1f} MB em {n} itens)")
subprocess.check_call([str(d/"python.exe"), "-c",
    "from PyQt6.QtWidgets import QApplication;"
    "from PyQt6.QtSvg import QSvgRenderer;"
    "import PyQt6.QtPrintSupport, scipy, matplotlib;"
    "a=QApplication([]);print('Qt de pe apos a poda')"],
    env={**__import__('os').environ, "QT_QPA_PLATFORM": "offscreen"})
PY
```

Expected: imprime a redução e `Qt de pe apos a poda`. Registre o número medido
no commit.

- [ ] **Step 6: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: poda por subsistema com motivo, e o opengl de software fica"
```

---

### Task 5: O payload, no layout que `repo_root()` exige

**Files:**
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: `RAIZ` da Task 1.
- Produces: `PAYLOAD: list[tuple[str, str]]` (padrão, motivo);
  `_payload_files(root: Path) -> list[Path]`;
  `_copy_payload(root: Path, dest: Path) -> tuple[int, int]`.

- [ ] **Step 1: Write the failing test**

```python
def test_payload_nunca_inclui_pdf():
    """659 MB de PDF de editora. Nao entram por DIREITOS, nao por peso: o
    software le 1,3 MB de CSV digitalizado e notas, e nao precisa deles."""
    arquivos = bi._payload_files(RAIZ)
    pdfs = [p for p in arquivos if p.suffix.lower() == ".pdf"]
    assert pdfs == [], f"{len(pdfs)} PDF entrariam no instalador: {pdfs[:3]}"


def test_payload_traz_as_notas_de_aparato_das_rodadas_R4_R5():
    """case_registry.py:24-25 resolve as notas por caminho DENTRO de
    BAS_V2_papers/<rodada>/apparatus_notes, com espacos e parenteses no nome.
    Perder esses arquivos nao quebra o import: quebra em silencio a nota de
    aparato de parte do corpus."""
    rel = {p.relative_to(RAIZ).as_posix() for p in bi._payload_files(RAIZ)}
    r4 = [r for r in rel if "Rodada 4" in r and "apparatus_notes" in r]
    r5 = [r for r in rel if "Rodada 5" in r and "apparatus_notes" in r]
    assert r4, "notas de aparato da Rodada 4 ausentes do payload"
    assert r5, "notas de aparato da Rodada 5 ausentes do payload"


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
    """Medido 2026-09-02: 206 dos 210 CSV estao sob BAS_V2_papers ou
    curve_library, mas 4 nao — 3 ANCORA_INTERNA em Models/EXPERIMENTAL_ANCORA e 1 USER
    em Models/USER_CASES. O store traz as 210 analises pre-calculadas, entao
    esses 4 APARECEM na arvore; sem o CSV, porem, `Re-simular caso` falha e
    eles ficam somente-leitura. Achado revisando o plano, nao rodando."""
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k payload`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute '_payload_files'`

- [ ] **Step 3: Write minimal implementation**

```python
# O que viaja com o instalador, por padrao e com motivo. Medido 2026-09-02:
# 84 MB. Lista de PADROES e nao de diretorios porque BAS_V2_papers inteiro e'
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
    ("Models/EXPERIMENTAL_ANCORA/reference_curves/*.csv",
     "3 casos ANCORA_INTERNA: sem isto eles ficam somente-leitura no app instalado"),
    ("Models/USER_CASES/*.csv", "1 caso USER de exemplo, pelo mesmo motivo"),
]

# Nunca, sob nenhum padrao. O .pdf esta' aqui por DIREITOS: e' material de
# editora e o instalador e' distribuido.
NUNCA = (".pdf", ".pyc", ".pyo")
NUNCA_EM = ("__pycache__", ".bkp_", ".git")


def _payload_files(root: Path) -> list[Path]:
    achados: set[Path] = set()
    for padrao, _motivo in PAYLOAD:
        for p in root.glob(padrao):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if p.suffix.lower() in NUNCA or any(t in rel for t in NUNCA_EM):
                continue
            achados.add(p)
    return sorted(achados)


def _copy_payload(root: Path, dest: Path) -> tuple[int, int]:
    n = total = 0
    for p in _payload_files(root):
        alvo = dest / p.relative_to(root)
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, alvo)
        n += 1
        total += p.stat().st_size
    return n, total
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (18 passed)

- [ ] **Step 5: Measure the payload**

Run:
```bash
py -3.12 -c "import sys; sys.path.insert(0,'New_Theory'); import build_installer as b; from pathlib import Path; f=b._payload_files(b.RAIZ); print(len(f),'arquivos,', sum(p.stat().st_size for p in f)/2**20, 'MB')"
```
Expected: ~84 MB. Se passar de 100 MB, algum padrão está pegando PDF ou
diretório inteiro — investigue antes de seguir.

- [ ] **Step 6: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: payload por padroes, sem PDF, no layout do repo_root"
```

---

### Task 6: O `.ico` a partir do SVG do tema

**Files:**
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: `RAIZ` da Task 1.
- Produces: `ICO_FG: str`; `_make_ico(svg: Path, dest: Path) -> Path`.

- [ ] **Step 1: Write the failing test**

```python
def test_ico_e_gerado_em_varios_tamanhos(tmp_path):
    from PyQt6.QtGui import QImageReader
    ico = bi._make_ico(
        RAIZ / "src" / "bolt_analysis_studio" / "resources" / "icons" / "app_icon.svg",
        tmp_path / "bas.ico")
    assert ico.is_file() and ico.stat().st_size > 0
    r = QImageReader(str(ico))
    assert r.canRead(), "o .ico gerado nao e' legivel de volta"


def test_a_cor_do_icone_nao_e_a_do_tema_escuro():
    """icons.py usa Theme.TEXT por padrao, que hoje resolve para o tema
    ESCURO (#cdd6f4, claro). Um glifo quase branco sobre fundo transparente
    fica invisivel no Explorer e no proprio instalador. A cor tem de vir do
    tema CLARO."""
    import sys as _s
    _s.path.insert(0, str(RAIZ / "src"))
    from bolt_analysis_studio.gui.theme import THEME_LIGHT, THEME_DARK
    assert bi.ICO_FG == THEME_LIGHT["TEXT"]
    assert bi.ICO_FG != THEME_DARK["TEXT"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k ico`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute '_make_ico'`

- [ ] **Step 3: Write minimal implementation**

```python
# Cor do glifo do icone. Vem do tema CLARO e nao do padrao de icons.py
# (Theme.TEXT), que hoje resolve para o tema escuro (#cdd6f4): glifo quase
# branco sobre fundo transparente fica invisivel no Explorer e no instalador.
ICO_FG = "#4c4f69"          # THEME_LIGHT["TEXT"] de gui/theme.py

_ICO_SIZES = (16, 32, 48, 64, 128, 256)


def _make_ico(svg: Path, dest: Path) -> Path:
    """Renderiza o SVG monocromatico do tema em .ico multi-resolucao.

    O SVG e' um TEMPLATE: traz o token literal `__FG__` no lugar da cor, que
    icons.py substitui em runtime. Aqui a substituicao e' por ICO_FG.
    Qt grava 'ico' nativamente (QImageWriter), entao nao entra dependencia
    nova so' para isto.
    """
    from PyQt6.QtCore import QByteArray, Qt
    from PyQt6.QtGui import QImage, QPainter
    from PyQt6.QtSvg import QSvgRenderer

    bruto = svg.read_bytes().replace(b"__FG__", ICO_FG.encode("ascii"))
    if b"__FG__" in svg.read_bytes() and ICO_FG.encode("ascii") not in bruto:
        raise SystemExit("[installer] substituicao de __FG__ falhou")
    imagens = []
    for lado in _ICO_SIZES:
        img = QImage(lado, lado, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        QSvgRenderer(QByteArray(bruto)).render(p)
        p.end()
        imagens.append(img)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # a maior resolucao define o arquivo; o Windows reamostra as menores
    if not imagens[-1].save(str(dest), "ICO"):
        raise SystemExit(f"[installer] Qt nao gravou o .ico em {dest}")
    return dest
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (20 passed)

- [ ] **Step 5: Look at the icon**

Run: `py -3.12 -c "import sys; sys.path.insert(0,'New_Theory'); import build_installer as b; from pathlib import Path; print(b._make_ico(b.RAIZ/'src/bolt_analysis_studio/resources/icons/app_icon.svg', Path('New_Theory/installer/_build/bas.ico')))"`
Expected: gera o arquivo. Abra-o e confirme que o glifo é visível sobre fundo
claro — o spec §9 já avisa que é um glifo de UI, não um logo.

- [ ] **Step 6: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: .ico do SVG do tema, com a cor do tema CLARO"
```

---

### Task 7: O `LEIAME.html`

**Files:**
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: `_project_metadata` da Task 1.
- Produces: `_write_leiame(dest: Path, meta: dict, n_fontes: int, n_casos: int) -> Path`.

- [ ] **Step 1: Write the failing test**

```python
def test_leiame_ensina_onde_estao_os_dados_de_calibracao(tmp_path):
    """O pedido de 2026-09-02 e' explicito: o leiame indica como usar E como
    ver os dados de calibracao."""
    meta = {"version": "2.0.0", "author": "Leonardo; Neilon"}
    alvo = bi._write_leiame(tmp_path / "LEIAME.html", meta, 29, 210)
    html = alvo.read_text(encoding="utf-8")
    assert "Ctrl+5" in html and "Validation" in html
    assert "New_Theory/variable_explorer/index.html" in html
    assert "adopted_configs.json" in html
    assert "Report HTML" in html and "Report geral" in html


def test_leiame_traz_autores_versao_licenca_e_doi(tmp_path):
    meta = {"version": "2.0.0",
            "author": "Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva"}
    html = bi._write_leiame(tmp_path / "L.html", meta, 29, 210).read_text(encoding="utf-8")
    assert "Leonardo Rosa Ribeiro da Silva" in html
    assert "Neilon de Souza da Silva" in html
    assert "2.0.0" in html and "MIT" in html
    assert "10.5281/zenodo.22233437" in html


def test_leiame_diz_o_que_nao_vem_e_por_que(tmp_path):
    """Quem procurar os PDF dos artigos tem de achar a explicacao e o caminho
    para a fonte, nao um diretorio vazio."""
    html = bi._write_leiame(tmp_path / "L.html",
                            {"version": "2.0.0", "author": "x"}, 29, 210
                            ).read_text(encoding="utf-8")
    assert "PDF" in html and "DOI" in html


def test_leiame_declara_utf8(tmp_path):
    """Sem o charset o navegador exibe 'Anlise' em vez de 'Análise'."""
    html = bi._write_leiame(tmp_path / "L.html",
                            {"version": "2.0.0", "author": "x"}, 29, 210
                            ).read_text(encoding="utf-8")
    assert 'charset="utf-8"' in html.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k leiame`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute '_write_leiame'`

- [ ] **Step 3: Write minimal implementation**

```python
DOI_CONCEITO = "10.5281/zenodo.22233437"

_LEIAME = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Bolt Analysis Studio V2 {versao} — leia-me</title>
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
</style></head><body><main>

<h1>Bolt Analysis Studio V2</h1>
<p class="sub">Versão {versao} · {autores}</p>

<h2>Como abrir</h2>
<p>Menu Iniciar → <b>Bolt Analysis Studio V2</b>. Se algo der errado e a janela
não aparecer, rode <code>BAS-console.cmd</code> na pasta de instalação: é o
mesmo programa, com console, mostrando a mensagem de erro.</p>

<h2>Onde estão os exemplos dos artigos</h2>
<p>No módulo <b>Results</b> (<kbd>Ctrl</kbd>+<kbd>5</kbd>), sub-aba
<b>Validation</b>. Você encontra uma árvore <b>artigo → curva</b>:
{n_fontes} fontes da literatura e {n_casos} curvas, cada uma com o erro médio
absoluto ao lado. Selecionando uma curva, aparece o dado digitalizado contra a
previsão do modelo.</p>

<h2>Como ver os dados de calibração</h2>
<table>
<tr><th>Caminho</th><th>O que mostra</th></tr>
<tr><td>Botão <b>Report HTML</b> no módulo Validation</td>
    <td>Report daquele caso: condições do ensaio, modelo massa-mola-amortecedor,
        resíduo com as três pernas do critério, decomposição por mecanismo e
        <b>as constantes com a procedência de cada uma</b></td></tr>
<tr><td>Botão <b>Report geral</b></td>
    <td>Report mestre com todos os casos e o censo</td></tr>
<tr><td><a href="New_Theory/variable_explorer/index.html">New_Theory/variable_explorer/index.html</a></td>
    <td>Uma página por artigo: figuras do paper, tabela de condições, DOI, nota
        de aparato e todas as curvas daquela fonte</td></tr>
<tr><td><code>New_Theory/adopted_configs.json</code></td>
    <td>As constantes adotadas por bancada, com o texto de procedência</td></tr>
</table>

<h2>O que não vem no instalador</h2>
<p>Os <b>PDF dos artigos de origem</b> não são distribuídos: são publicações de
editora, e redistribuí-las não nos cabe. O que vem são as curvas digitalizadas
e as notas de aparato, que é do que o programa precisa. Cada página de artigo
traz o <b>DOI</b> da fonte para você buscar o original.</p>

<div class="nota">Este instalador não é assinado digitalmente. Na primeira
execução o Windows pode exibir o aviso de aplicativo não reconhecido.</div>

<footer>
<p>Licença <b>MIT</b> para o software. Autores: {autores}.</p>
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (24 passed)

- [ ] **Step 5: Read the rendered page**

Run: `py -3.12 -c "import sys; sys.path.insert(0,'New_Theory'); import build_installer as b; from pathlib import Path; import webbrowser; p=b._write_leiame(Path('New_Theory/installer/_build/LEIAME.html'), b._project_metadata((b.RAIZ/'setup.py').read_text(encoding='utf-8')), 29, 210); webbrowser.open(p.as_uri())"`
Expected: abre no navegador, acentos corretos, os dois autores no rodapé.

- [ ] **Step 6: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: LEIAME.html com os caminhos dos dados de calibracao"
```

---

### Task 8: O script do Inno Setup

**Files:**
- Create: `New_Theory/installer/bas_v2.iss.template`
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: `_project_metadata` (Task 1), o `.ico` (Task 6), o `_build/` montado
  (Tasks 3-5, 7).
- Produces: `_render_iss(template: str, meta: dict, build_dir: Path, out_dir: Path) -> str`;
  `_compile_iss(iss: Path) -> Path`.

- [ ] **Step 1: Write the failing test**

```python
def test_iss_recebe_versao_e_autores_do_setup_py():
    tpl = (RAIZ / "New_Theory" / "installer" / "bas_v2.iss.template").read_text(
        encoding="utf-8")
    meta = {"version": "2.0.0",
            "author": "Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva"}
    iss = bi._render_iss(tpl, meta, Path(r"C:\b"), Path(r"C:\o"))
    assert "AppVersion=2.0.0" in iss
    assert "Neilon de Souza da Silva" in iss
    assert "{{" not in iss and "}}" not in iss, "sobrou placeholder no .iss"


def test_iss_da_icone_ao_proprio_instalador_e_ao_atalho():
    """O pedido pede o icone NO ARQUIVO DE INSTALACAO. SetupIconFile e' o
    .exe do instalador; IconFilename e' o atalho. Sao coisas diferentes."""
    tpl = (RAIZ / "New_Theory" / "installer" / "bas_v2.iss.template").read_text(
        encoding="utf-8")
    iss = bi._render_iss(tpl, {"version": "2.0.0", "author": "x"},
                         Path(r"C:\b"), Path(r"C:\o"))
    assert "SetupIconFile=" in iss
    assert "IconFilename:" in iss


def test_iss_abre_o_leiame_ao_final():
    tpl = (RAIZ / "New_Theory" / "installer" / "bas_v2.iss.template").read_text(
        encoding="utf-8")
    iss = bi._render_iss(tpl, {"version": "2.0.0", "author": "x"},
                         Path(r"C:\b"), Path(r"C:\o"))
    assert "LEIAME.html" in iss
    assert "postinstall" in iss and "shellexec" in iss


def test_iss_instala_por_usuario_sem_uac():
    tpl = (RAIZ / "New_Theory" / "installer" / "bas_v2.iss.template").read_text(
        encoding="utf-8")
    iss = bi._render_iss(tpl, {"version": "2.0.0", "author": "x"},
                         Path(r"C:\b"), Path(r"C:\o"))
    assert "PrivilegesRequired=lowest" in iss


def test_iss_atalho_aponta_para_o_pythonw_embutido():
    """A pilha existe para preservar sys.executable como Python real
    (spec §2). Atalho para outra coisa perde exatamente isso."""
    tpl = (RAIZ / "New_Theory" / "installer" / "bas_v2.iss.template").read_text(
        encoding="utf-8")
    iss = bi._render_iss(tpl, {"version": "2.0.0", "author": "x"},
                         Path(r"C:\b"), Path(r"C:\o"))
    assert r"python\pythonw.exe" in iss
    assert "run_app.py" in iss
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k iss`
Expected: FAIL — arquivo `bas_v2.iss.template` não existe

- [ ] **Step 3: Write minimal implementation**

Crie `New_Theory/installer/bas_v2.iss.template` (os campos entre `@` são
substituídos por `_render_iss`; `{` do Inno fica intacto):

```
; Bolt Analysis Studio V2 - instalador auto-contido
; GERADO por New_Theory/build_installer.py a partir de bas_v2.iss.template.
; Nao editar o gerado: editar o template.
; Versao e autores vem do setup.py, que e' a fonte unica dos dois.

[Setup]
AppId={{8E4C1F2A-6B7D-4A91-9C3E-BAS2V2INSTALL}
AppName=Bolt Analysis Studio V2
AppVersion=@VERSION@
AppPublisher=@AUTHOR@
AppPublisherURL=https://github.com/leonardorrs190891/bolt-analysis-studio
DefaultDirName={localappdata}\Programs\Bolt Analysis Studio V2
DefaultGroupName=Bolt Analysis Studio V2
OutputDir=@OUTDIR@
OutputBaseFilename=BAS-V2-Setup-@VERSION@
SetupIconFile=@ICO@
UninstallDisplayIcon={app}\bas.ico
UninstallDisplayName=Bolt Analysis Studio V2 @VERSION@
LicenseFile=@BUILDDIR@\LICENSE
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; O layout de destino E' o repo root: repo_root() sobe 3 niveis de
; src/bolt_analysis_studio/validation/inputs.py e tem de cair em {app}.
Source: "@BUILDDIR@\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Bolt Analysis Studio V2"; Filename: "{app}\python\pythonw.exe"; \
      Parameters: """{app}\run_app.py"" --skip-deps-check"; \
      WorkingDir: "{app}"; IconFilename: "{app}\bas.ico"
Name: "{group}\Leia-me"; Filename: "{app}\LEIAME.html"
Name: "{group}\Dados de calibracao (por artigo)"; \
      Filename: "{app}\New_Theory\variable_explorer\index.html"
Name: "{autodesktop}\Bolt Analysis Studio V2"; Filename: "{app}\python\pythonw.exe"; \
      Parameters: """{app}\run_app.py"" --skip-deps-check"; \
      WorkingDir: "{app}"; IconFilename: "{app}\bas.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; \
      GroupDescription: "Atalhos:"

[Run]
Filename: "{app}\LEIAME.html"; Description: "Ver o leia-me (como usar e onde estao os dados de calibracao)"; \
      Flags: postinstall shellexec skipifsilent nowait
Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\run_app.py"" --skip-deps-check"; \
      WorkingDir: "{app}"; Description: "Abrir o Bolt Analysis Studio V2"; \
      Flags: postinstall nowait skipifsilent unchecked
```

E acrescente a `New_Theory/build_installer.py`:

```python
def _render_iss(template: str, meta: dict, build_dir: Path,
                out_dir: Path) -> str:
    """Substitui os campos @...@ do template.

    Usa @CAMPO@ e nao str.format porque o .iss e' cheio de {app}, {group} e
    {localappdata}: format() tentaria interpretar cada um como placeholder.
    """
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
    sobrou = [l for l in saida.splitlines() if "@" in l and l.strip().startswith(
        ("App", "Output", "Setup", "License", "Source"))]
    if sobrou:
        raise SystemExit(f"[installer] campo nao substituido no .iss: {sobrou[0]}")
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (29 passed)

- [ ] **Step 5: Commit**

```bash
git add New_Theory/installer/bas_v2.iss.template New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: template do Inno com icone no setup, atalhos e leiame no final"
```

---

### Task 9: O teste de aceitação da instalação

**Files:**
- Modify: `New_Theory/build_installer.py`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: nada das tasks anteriores em tempo de teste (roda contra um dir
  qualquer que tenha o layout).
- Produces: `ACEITE_SRC: str` (o script que roda DENTRO da instalação);
  `_acceptance(install_dir: Path, py_exe: Path) -> None`.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k aceitacao`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute '_acceptance'`

- [ ] **Step 3: Write minimal implementation**

```python
# Roda DENTRO da instalacao, com o interpretador embutido. As assercoes sao
# as de tests/test_corpus_coverage.py: e' o mesmo contrato, aferido no
# artefato entregue em vez do repo de desenvolvimento.
ACEITE_SRC = r'''
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")

import numpy, scipy, matplotlib                                   # noqa: F401
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
ids_reg, ids_st = {r.case_id for r in recs}, set(store.all_ids())
if ids_reg - ids_st:
    raise SystemExit(f"ACEITE: {len(ids_reg - ids_st)} casos sem analise")
if ids_st - ids_reg:
    raise SystemExit(f"ACEITE: {len(ids_st - ids_reg)} analises orfas")

for r in recs:
    res = store.get(r.case_id)
    for k in ("mae", "maxerr", "resid_std"):
        if getattr(res, k, None) is None:
            raise SystemExit(f"ACEITE: {r.case_id} sem {k}")
    if build_case_model(r) is None:
        raise SystemExit(f"ACEITE: {r.case_id} nao abre no modelo")

br = ValidationBrowser(store=store)
br.populate()
tree = br.tree
n_src = tree.topLevelItemCount()
celulas = [tree.topLevelItem(i).child(j)
           for i in range(n_src)
           for j in range(tree.topLevelItem(i).childCount())]
if len(celulas) != len(recs):
    raise SystemExit(f"ACEITE: arvore com {len(celulas)} casos, registry com {len(recs)}")
if n_src != len({r.source for r in recs}):
    raise SystemExit("ACEITE: contagem de fontes divergente")
ruins = [c.text(0) for c in celulas if c.text(1).strip() in ("", "\u2014", "erro")]
if ruins:
    raise SystemExit(f"ACEITE: {len(ruins)} casos sem analise na arvore: {ruins[:3]}")

print(f"ACEITE OK: {n_src} fontes, {len(celulas)} casos")
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
                           capture_output=True, text=True)
    finally:
        script.unlink(missing_ok=True)
    if r.returncode != 0:
        raise SystemExit(
            f"[installer] ACEITACAO REPROVADA, nenhum instalador entregue.\n"
            f"{r.stdout.strip()}\n{r.stderr.strip()}")
    print(f"  {r.stdout.strip().splitlines()[-1]}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (31 passed) — o primeiro teste roda o aceite contra o repo e
imprime `ACEITE OK: 29 fontes, 210 casos`

- [ ] **Step 5: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py
git commit -m "instalador: aceitacao rodada DENTRO da instalacao, e que reprova de verdade"
```

---

### Task 10: Orquestração e build de ponta a ponta

**Files:**
- Modify: `New_Theory/build_installer.py`
- Modify: `CLAUDE.md`
- Test: `tests/test_build_installer.py`

**Interfaces:**
- Consumes: tudo das Tasks 1-9.
- Produces: `main(argv=None) -> int`; artefato `dist/BAS-V2-Setup-2.0.0.exe`.

- [ ] **Step 1: Write the failing test**

```python
def test_main_aceita_skip_download_e_nao_explode_no_parse():
    """Contrato de linha de comando: --out e --skip-download existem, e --help
    nao levanta. O build de verdade e' exercitado no passo manual, nao aqui:
    baixa 10 MB e leva minutos."""
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
                 "_write_leiame", "_render_iss", "_compile_iss",
                 "_acceptance"):
        assert nome in fonte, f"main() nao chama {nome}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q -k "main or etapas"`
Expected: FAIL — `AttributeError: module 'build_installer' has no attribute 'main'`

- [ ] **Step 3: Write minimal implementation**

```python
def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Instalador Windows auto-contido do Bolt Analysis Studio V2")
    ap.add_argument("--out", default=str(RAIZ / "dist"),
                    help="diretorio de saida do .exe (padrao: dist/)")
    ap.add_argument("--skip-download", action="store_true",
                    help="reusa o Python embutido ja' desempacotado em _build/")
    ap.add_argument("--skip-acceptance", action="store_true",
                    help="NAO use para entregar: pula a aceitacao da §8")
    args = ap.parse_args(argv)

    meta = _project_metadata((RAIZ / "setup.py").read_text(encoding="utf-8"))
    inst = RAIZ / "New_Theory" / "installer"
    build = inst / "_build"
    py_dir = build / "python"
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Bolt Analysis Studio V2 {meta['version']}")
    print(f"  autores: {meta['author']}")

    if not args.skip_download:
        if build.exists():
            shutil.rmtree(build)
        build.mkdir(parents=True)
        z = _fetch_embed(inst / "_cache")
        _unpack_embed(z, py_dir)
        _enable_site(py_dir)
        specs = [s.strip() for s in
                 (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines()
                 if s.strip() and not s.strip().startswith("#")]
        _pip_install(py_dir / "python.exe", specs)
        fora, n_itens = _prune(py_dir)
        print(f"  [4/7] poda: -{fora/2**20:.1f} MB em {n_itens} itens")

    n_arq, tam = _copy_payload(RAIZ, build)
    print(f"  [5/7] payload: {n_arq} arquivos, {tam/2**20:.1f} MB")

    _make_ico(RAIZ / "src" / "bolt_analysis_studio" / "resources" / "icons"
              / "app_icon.svg", build / "bas.ico")
    from bolt_analysis_studio.validation.case_registry import all_records  # noqa
    # contagem para o leiame: do REGISTRO, nunca digitada
    sys.path.insert(0, str(RAIZ / "src"))
    recs = all_records()
    _write_leiame(build / "LEIAME.html", meta,
                  len({r.source for r in recs}), len(recs))
    print(f"  [6/7] icone e leiame ({len({r.source for r in recs})} fontes, "
          f"{len(recs)} casos)")

    iss_txt = _render_iss(
        (inst / "bas_v2.iss.template").read_text(encoding="utf-8"),
        meta, build, out_dir)
    iss = inst / "_build" / "bas_v2.iss"
    iss.write_text(iss_txt, encoding="utf-8", newline="")
    _compile_iss(iss)

    exe = out_dir / f"BAS-V2-Setup-{meta['version']}.exe"
    if not exe.is_file():
        raise SystemExit(f"[installer] o ISCC terminou mas {exe} nao existe")

    if not args.skip_acceptance:
        import tempfile
        with tempfile.TemporaryDirectory(prefix="bas_aceite_") as td:
            alvo = Path(td) / "BAS"
            print("  aceitacao: instalando em diretorio temporario")
            subprocess.check_call([str(exe), "/SILENT", "/SUPPRESSMSGBOXES",
                                   "/NORESTART", f"/DIR={alvo}"])
            _acceptance(alvo, alvo / "python" / "python.exe")
            subprocess.call([str(alvo / "unins000.exe"), "/SILENT"])

    print(f"\nOK: {exe}  ({exe.stat().st_size/2**20:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.12 -m pytest tests/test_build_installer.py -q`
Expected: PASS (33 passed)

- [ ] **Step 5: Run the real build, end to end**

Run: `py -3.12 New_Theory/build_installer.py`
Expected: as 7 etapas, `ACEITE OK: 29 fontes, 210 casos`, e
`OK: …\dist\BAS-V2-Setup-2.0.0.exe (~150-200 MB)`.

Se a aceitação reprovar, o suspeito nº 1 é a poda (Task 4): reveja `PODA`,
tire a entrada suspeita e rode de novo. **Não** contorne com
`--skip-acceptance`.

- [ ] **Step 6: Install it yourself and look**

Rode o `.exe` gerado. Confira, na ordem: o ícone aparece no próprio arquivo do
instalador; a tela de licença mostra o MIT; o nome dos autores aparece como
editor; ao final o leiame abre no navegador; o atalho do Menu Iniciar abre a
GUI; o módulo Results → Validation lista 29 fontes e 210 casos; e o
*Adicionar/Remover Programas* traz a entrada com a versão.

- [ ] **Step 7: Record it in CLAUDE.md**

Acrescente à seção de comandos, junto do `publish_snapshot.py`:

```markdown
# INSTALADOR auto-contido (Windows x64, ~150-200 MB). Python 3.12.10 embeddable
# PINADO com sha256 + pip dentro dele + payload no layout que repo_root() exige.
# NAO e' PyInstaller, e o motivo esta' medido no spec: main_window.py:8195 lanca
# `[sys.executable, "-m", ...]` (o tuner morreria congelado) e repo_root() e'
# parents[3] de inputs.py sondando New_Theory/. ⚠️ Os PDF dos artigos (659 MB)
# NAO entram: material de editora, e o app le so' 1,3 MB de CSV+notas.
# ⚠️ O build ABORTA se a aceitacao (instala em temp e afere 29 fontes/210 casos
# rodando o app DA INSTALACAO) reprovar — a poda do PyQt6 e' o ponto fragil e o
# teste roda DEPOIS dela. Nunca entregue com --skip-acceptance.
py -3.12 New_Theory/build_installer.py            # -> dist/BAS-V2-Setup-<versao>.exe
```

- [ ] **Step 8: Commit**

```bash
git add New_Theory/build_installer.py tests/test_build_installer.py CLAUDE.md
git commit -m "instalador: orquestracao das 7 etapas, e o build aborta se a aceitacao reprovar"
```

---

## Autorrevisão do plano

**Cobertura do spec.** §1 → Task 10 (artefato) · §2 → é a premissa de toda a
Task 3 e do teste `test_iss_atalho_aponta_para_o_pythonw_embutido` · §3 →
Task 5 (`test_copia_preserva_o_caminho_relativo` afere `parents[3]`) · §4 →
Task 5 (`test_payload_nunca_inclui_pdf`) · §5 etapas 1-2-3 → Tasks 2 e 3;
etapa 4 → Task 4; etapa 5 → Task 5; etapa 6 → Task 6; etapa 7 → Task 8 · §6 →
Task 8 (`[Icons]`, `SetupIconFile`, e o `BAS-console.cmd` **falta**: ver
lacuna abaixo) · §7 → Task 7 · §8 → Task 9 · §9 → o aviso de assinatura entra
no leiame (Task 7, `test_leiame_diz_o_que_nao_vem_e_por_que` cobre os PDF; o
aviso do SmartScreen está no template `_LEIAME`).

**Lacuna encontrada e fechada:** o spec §6 promete um `BAS-console.cmd` na raiz
da instalação para diagnóstico, e nenhuma task o criava. Acrescente à **Task 7**,
depois do Step 3:

- [ ] **Step 3b: Criar o `BAS-console.cmd` junto do leiame**

```python
_CONSOLE_CMD = (
    "@echo off\r\n"
    "rem Mesmo programa do atalho, mas com console e COM o preflight de\r\n"
    "rem dependencias ligado: pythonw.exe nao tem console, entao uma mensagem\r\n"
    "rem do preflight seria invisivel no atalho normal.\r\n"
    "cd /d \"%~dp0\"\r\n"
    "\"%~dp0python\\python.exe\" \"%~dp0run_app.py\" %*\r\n"
    "echo.\r\n"
    "pause\r\n"
)


def _write_console_cmd(dest: Path) -> Path:
    dest.write_text(_CONSOLE_CMD, encoding="ascii", newline="")
    return dest
```

Teste correspondente, a acrescentar na Task 7 Step 1:

```python
def test_console_cmd_roda_com_o_preflight_ligado(tmp_path):
    """O atalho normal passa --skip-deps-check porque pythonw.exe nao tem
    console. Este .cmd existe para o caso contrario: console E preflight."""
    cmd = bi._write_console_cmd(tmp_path / "BAS-console.cmd").read_text()
    assert "python.exe" in cmd and "pythonw" not in cmd
    assert "--skip-deps-check" not in cmd
    assert "pause" in cmd
```

E chame `_write_console_cmd(build / "BAS-console.cmd")` em `main()` (Task 10,
Step 3), junto do `_write_leiame`; acrescente `_write_console_cmd` à lista do
teste `test_etapas_do_pipeline_estao_todas_ligadas`.

**Segunda lacuna, achada ao revisar o plano antes de executar:** o PAYLOAD
não incluía `Models/EXPERIMENTAL_ANCORA/` nem `Models/USER_CASES/`, onde vivem
os CSV de 4 dos 210 casos (3 `ANCORA_INTERNA` + 1 `USER`, os únicos que não são
artigo). Eles apareceriam na árvore, vindos do store, mas `Re-simular caso`
falharia. Fechada com dois padrões e o teste
`test_payload_traz_o_csv_de_TODOS_os_210_casos`, que afere contra o registry
em vez de contra uma lista escrita à mão.

**Varredura de placeholders.** Nenhum "TBD", "TODO" ou "implemente depois". Os
passos de código trazem o código.

**Consistência de tipos.** `_project_metadata` devolve `dict` com `version` e
`author`, e é assim consumida nas Tasks 7, 8 e 10 · `_prune` e `_copy_payload`
devolvem tuplas de 2, desempacotadas como tal em `main()` · `_make_ico`,
`_write_leiame` e `_write_console_cmd` devolvem `Path` · `_acceptance` não
devolve nada e levanta `SystemExit` — é o que `main()` espera · `_iscc_path`
devolve `Path | None` e `_compile_iss` trata o `None`.
