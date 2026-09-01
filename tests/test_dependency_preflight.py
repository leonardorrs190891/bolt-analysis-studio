"""Preflight de dependencias do lancador (2026-09-01).

Numa maquina limpa `python run_app.py` morria com um ImportError cru de PyQt6,
que nao diz ao usuario o que fazer. O preflight le os specs do
requirements.txt, mede o que falta e oferece instalar no interpretador que esta
rodando.

As duas partes que DECIDEM sao puras de proposito: texto -> specs, e specs +
versoes instaladas -> lacunas. Assim da' para testar a decisao inteira sem
tocar no ambiente de quem roda o teste, que e' justamente o que um instalador
nao deveria fazer sem permissao.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import run_app                                                    # noqa: E402


def test_parse_requirements_ignora_comentarios_e_linhas_vazias():
    """O requirements.txt do repo tem um bloco de opcionais COMENTADO. Le-lo
    como se fosse obrigatorio faria o preflight instalar reportlab, openpyxl e
    jinja2 em quem so' quer abrir o programa."""
    texto = (
        "# Bolt Analysis Studio v4.0 - Requirements\n"
        "\n"
        "numpy>=1.21.0\n"
        "scipy>=1.7.0\n"
        "\n"
        "# Optional: Report generation (Phase 8)\n"
        "# reportlab>=4.0.0\n"
        "PyQt6>=6.4.0\n"
    )
    assert run_app._parse_requirements(texto) == [
        ("numpy", (1, 21, 0)),
        ("scipy", (1, 7, 0)),
        ("PyQt6", (6, 4, 0)),
    ]


def test_parse_requirements_aceita_spec_sem_versao():
    assert run_app._parse_requirements("matplotlib\n") == [("matplotlib", None)]


def test_lacunas_acusam_o_ausente_e_o_desatualizado():
    specs = [("numpy", (1, 21, 0)), ("scipy", (1, 7, 0)), ("PyQt6", (6, 4, 0))]
    instalado = {"numpy": "1.26.4", "scipy": "1.5.0"}      # PyQt6 ausente
    assert run_app._dependency_gaps(specs, instalado.get) == [
        "scipy>=1.7.0", "PyQt6>=6.4.0"]


def test_nada_a_fazer_quando_tudo_esta_presente_e_novo():
    specs = [("numpy", (1, 21, 0)), ("matplotlib", None)]
    assert run_app._dependency_gaps(specs, lambda _n: "9.9.9") == []


def test_versao_ilegivel_nao_bloqueia_o_lancamento():
    """O preflight existe para destravar quem NAO tem a dependencia. Uma versao
    que ele nao consegue comparar nao pode virar um impedimento inventado em
    quem tem: no empate, deixa passar."""
    specs = [("PyQt6", (6, 4, 0))]
    assert run_app._dependency_gaps(specs, lambda _n: "unknown") == []


def test_sufixo_de_pre_release_nao_conta_como_desatualizado():
    specs = [("PyQt6", (6, 4, 0))]
    assert run_app._dependency_gaps(specs, lambda _n: "6.4.0.dev0+g12ab") == []


def test_o_requirements_do_repo_e_legivel_pelo_preflight():
    """Ancora contra o arquivo real: se o requirements.txt mudar de forma que o
    preflight nao entenda, isto quebra aqui e nao na maquina do usuario."""
    specs = run_app._parse_requirements(
        (RAIZ / "requirements.txt").read_text(encoding="utf-8"))
    nomes = [n for n, _v in specs]
    assert nomes == ["numpy", "scipy", "matplotlib", "PyQt6"]


def test_o_ambiente_que_roda_o_teste_satisfaz_o_requirements():
    """Fecha o circulo: as mesmas funcoes, contra o ambiente de verdade."""
    specs = run_app._parse_requirements(
        (RAIZ / "requirements.txt").read_text(encoding="utf-8"))
    assert run_app._dependency_gaps(specs, run_app._installed_version) == []


def test_comando_impresso_protege_o_spec_do_shell():
    """`pip install numpy>=1.21.0` colado num shell e' REDIRECIONAMENTO: o '>'
    faz o shell criar um arquivo chamado '=1.21.0' e instalar 'numpy'. A
    instrucao de recuperacao quebraria justamente quem ela deveria socorrer."""
    texto = run_app._command_text(
        ["python", "-m", "pip", "install", "numpy>=1.21.0"])
    assert texto == 'python -m pip install "numpy>=1.21.0"'


def test_comando_impresso_protege_caminho_com_espaco():
    """O interpretador alvo costuma estar em 'Program Files'."""
    texto = run_app._command_text([r"C:\Program Files\Py\python.exe", "-m", "pip"])
    assert texto == r'"C:\Program Files\Py\python.exe" -m pip'
