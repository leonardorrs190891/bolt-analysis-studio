# -*- coding: utf-8 -*-
"""CATRACA: todo prereg NOVO declara o proprio ESTADO.

O cron de retomada manda, no passo 1 e no 3, LER o estado em vez de supor
("Backups .bkp_* com gates NAO fechados = execucao a meio: termine ou reverta";
"leia o cabecalho em vez de supor o que esta aberto"). Auditoria de 2026-08-13:
de **45** preregs de agosto, apenas **7** declaravam estado — o arquivo sozinho
nao dizia o que estava pendente, e dois deles eram MEUS (D-Z e D-AA, executados
com gates 5/5 e 6/6 e nunca carimbados; corrigidos no mesmo commit).

## O requisito e' satisfazivel NA ESCRITA

Um prereg recem-escrito nao tem resultado — mas pode e deve declarar-se
**PENDENTE**, como o do ECCLES fez ("NAO EXECUTADO — aguarda assinatura"). Por
isso a catraca nao atrapalha quem esta comecando: ela exige que o estado seja
DITO, nao que seja "executado".

Marcas aceitas: `## Estado`, `EXECUTADO`, `NAO EXECUTADO`, `aguarda assinatura`,
`PENDENTE`, `FALHA declarada`, `RETIRADA`, `INCONCLUSIVO`, `nao adota`.

## Escopo

Catraca, como a de procedência: o estoque legado esta DECLARADO no baseline e
crescimento e' proibido. Carimbar um legado e' LIVRE (ele so sai do baseline).
NAO carimbo prereg de outra sessao por inferencia — estado alheio se le, nao se
adivinha.
"""
from __future__ import annotations

import glob
import re
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPECS = RAIZ / "docs" / "superpowers" / "specs"

MARCAS = (
    "## Estado", "EXECUTAD", "NAO EXECUTADO", "NÃO EXECUTADO",
    "aguarda assinatura", "PENDENTE", "FALHA declarada", "RETIRAD",
    "INCONCLUSIV", "não adota", "NAO ADOTA",
)

# BASELINE medido em 2026-08-13. Preregs legados sem declaracao de estado.
_SEM_ESTADO_BASELINE = frozenset((
    "2026-07-22-f4-l1v2-prereg-b1v3.md", "2026-07-22-f4-l1v2-prereg2-r5-transversal.md",
    "2026-07-28-chu-test1-floor-prereg.md", "2026-07-28-liu2025-adocao-prereg.md",
    "2026-07-28-liu2025-e2-prereg.md", "2026-07-28-metrica-banda-prereg.md",
    "2026-07-28-metrica-nivel-prereg.md",
    "2026-07-30-yang2023ijpem-delta-free-v2-prereg.md",
    "2026-07-30-yang2023ijpem-trio-prereg.md",
    "2026-07-31-excecao-elastica-e-adocao-lu-final-prereg.md",
    "2026-07-31-lu2024-p3-r3-prereg.md", "2026-07-31-lu2024-p3-r4-prereg.md",
    "2026-07-31-pares-replica-declarados-prereg.md",
    "2026-08-01-familias-falsas-chave-cega-prereg.md",
    "2026-08-01-n-minimo-sres-prereg.md", "2026-08-01-resolucao-do-dado-prereg.md",
    "2026-08-09-p8-opcao2-prereg-v2.md", "2026-08-09-p8-opcao2-prereg.md",
    # ⚠️ ACRESCENTADOS 2026-08-16 ao apertar o casador (prefixo com fronteira).
    # Estes 7 passavam SO porque `PENDENTE` casava dentro de "independente" —
    # nunca declararam estado. Sao LEGADOS (julho/inicio de agosto); entram no
    # baseline em vez de serem reescritos, no idioma das outras catracas: o
    # estoque e declarado, o CRESCIMENTO e proibido.
    # ⚠️ O 8o (2026-08-16-lu2024-pico-espurio) NAO entrou aqui: e de hoje e ja
    # estava EXECUTADO, entao recebeu a secao `## Estado` de verdade.
    "2026-07-11-mem-iter3-preregistrations.md",
    "2026-07-28-metrica-banda-v2-prereg.md",
    "2026-07-28-metrica-em-vida-prereg.md",
    "2026-07-28-sun-bilinear-prereg.md",
    "2026-07-30-yang2023ijpem-delta-free-prereg.md",
    "2026-08-09-p9-freq-embedding-prereg-v2.md",
    "2026-08-09-p9-freq-embedding-prereg.md",
))


def _sem_estado() -> set:
    out = set()
    for p in sorted(glob.glob(str(SPECS / "*prereg*.md"))):
        t = Path(p).read_text(encoding="utf-8", errors="replace").lower()
        # ⚠️ FRONTEIRA DE PALAVRA NO PREFIXO (2026-08-16). Ate aqui era
        # `m.lower() in t`, casamento por SUBSTRING — e `PENDENTE` casava
        # dentro de "inde·PENDENTE", palavra comum na prosa da campanha.
        # Medido: 8 de 99 preregs passavam a catraca SEM declarar estado
        # nenhum, e um deles era de HOJE (o do pico espurio), ja EXECUTADO.
        # A guarda que existe para impedir prereg sem estado era satisfeita
        # por uma palavra sem relacao com estado.
        #
        # So o PREFIXO leva fronteira: `EXECUTAD` e RADICAL e precisa seguir
        # casando "EXECUTADO"/"EXECUTADA". Exigir fronteira no sufixo tambem
        # rejeitaria o marcador legitimo — erro que cometi na 1a medicao deste
        # defeito, e que inflava a conta para 10.
        if not any(re.search(r"(?<![0-9a-zà-ú])" + re.escape(m.lower()), t)
                   for m in MARCAS):
            out.add(os.path.basename(p))
    return out


def test_baseline_tem_o_tamanho_declarado():
    """Guarda o literal contra edicao sem medicao."""
    assert len(_SEM_ESTADO_BASELINE) == 25, (
        "baseline declarado tem %d entradas; era 18 e foi a 25 em 2026-08-16 "
        "ao apertar o casador de marcadores — re-meca antes de editar"
        % len(_SEM_ESTADO_BASELINE))


def test_prereg_novo_declara_estado():
    """CATRACA: nenhum prereg NOVO entra sem dizer em que estado esta."""
    novos = sorted(_sem_estado() - _SEM_ESTADO_BASELINE)
    assert not novos, (
        "%d prereg(s) NOVO(s) sem declaracao de estado: %s \n"
        "Acrescente uma secao `## Estado` dizendo PENDENTE (aguarda assinatura), "
        "EXECUTADO (com os gates medidos) ou RETIRADA. O cron le este arquivo "
        "para saber o que esta em voo — sem a marca, ele supoe."
        % (len(novos), ", ".join(novos)))


def test_carimbar_legado_e_livre():
    """Encolher o baseline NAO falha: documentar um legado e' bem-vindo."""
    atual = _sem_estado()
    assert atual <= _SEM_ESTADO_BASELINE | atual, "invariante trivial de conjunto"
    # sem assert de progresso, por desenho
