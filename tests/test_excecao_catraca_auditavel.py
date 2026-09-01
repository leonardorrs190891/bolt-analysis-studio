# -*- coding: utf-8 -*-
"""CATRACA DE AUDITABILIDADE — impede que entre exceção NOVA inauditável.

## O que motivou

Auditoria de 2026-08-15 (`cinco_camadas_auditadas_consolidado.md`): das **22**
exceções assinadas, só **2** registram a prova numa forma que a máquina confira —
o trio `(perna, valor, piso)`, como em

    "prova de piso (FORTE): res.máx 0.122/0.257 · σ 0.039/0.083"

As outras **20** dizem coisas legítimas mas não checáveis: *"prova em lei (5
degraus)"*, *"scatter de réplicas (desvio-à-mediana 0,349)"*, *"sobreposição
axial"*.

⚠️ **E as DUAS conferíveis foram as DUAS que falharam** — repousavam num piso que
a própria P-15 declarara inválido (6ª retratação da mesma estrutura). Isso não
prova que as 20 estejam erradas; destrói a leitura oposta. Com 2 de 2 falhando na
amostra verificável, o correto é tratá-las como **não verificadas**.

⇒ a camada com o **pior histórico** (6 retratações por piso inválido) é a **menos
verificável**. As `_DECLARADAS`, por contraste, são 4× mais checáveis (7 de 18) e
conferem **100 %** — e a diferença não é rigor de quem escreveu, é **forma**.

## O que este teste FAZ, e o que NÃO faz

FAZ: congela as 20 conhecidas e **falha se aparecer exceção NOVA sem o trio**.
Catraca, no idioma de `test_procedencia_catraca` e dos `_EXCECOES_RETIRADAS_*`:
o estoque é declarado, o crescimento é proibido.

NÃO FAZ: exigir reescrita das 20. Encolher o baseline é **livre** — quem
acrescentar o trio a uma prova antiga não precisa mexer aqui (a comparação é
`atual − baseline`, nunca igualdade).

NÃO FAZ, também: julgar se a prova está CERTA. Só se ela é **conferível**. Uma
prova em nível de lei pode estar perfeita e continuar fora do trio — por isso a
saída legítima nº 2 existe.

## Como consertar quando falhar

A mensagem nomeia a curva. Duas saídas:
  1. registrar o trio `(perna, valor, piso)` junto da prosa — o caminho certo,
     e o que torna a exceção auditável em toda re-medição futura;
  2. se a prova é genuinamente de outra natureza (lei, escopo, protocolo),
     ACRESCENTAR ao baseline com um comentário dizendo por quê — o que torna a
     escolha visível em vez de tácita.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ / "src"))

import bolt_analysis_studio.validation.report_html as R  # noqa: E402

# Trio conferível: <perna> <valor>/<piso>. É a forma que a auditoria de
# 2026-08-15 conseguiu recomputar — e a única que permitiu detectar o piso
# inválido do ECCLES.
_RX_TRIO = re.compile(r"(res\.máx|res\.max|σ|sigma|MAE)\s*[\d.]+\s*/\s*[\d.]+")

# BASELINE medido em 2026-08-15: 20 exceções cuja prova NÃO tem o trio.
# Não é acusação — várias são provas de LEI ou de ESCOPO, que não têm essa
# forma por natureza. É o estoque declarado, para que o crescimento seja visível.
_SEM_TRIO_BASELINE = frozenset((
    # BAUER — prova por scatter de réplicas (cita o desvio-à-mediana, não o trio)
    # test2 SAIU em 2026-08-20: fechou por mérito (limiar do espectro por
    # espécime, prereg bauer-fig8-scrit-especime) — retirada em
    # _EXCECOES_RETIRADAS_BAUER_SCRIT; a catraca encolhe como deve.
    # As 4 da fig6 SAÍRAM em 2026-08-21 pela SAÍDA 1 (a boa): o trio
    # conferível foi MEDIDO e acrescentado às provas — pisos par-a-par das
    # 6 réplicas (15 pares, janela da métrica): mx 0,2611 · MAE 0,1124 ·
    # σ 0,0916. Primeira vez que a catraca encolhe por DOCUMENTAÇÃO, não
    # por adoção; a fração conferível sobe de 2 para 6.
    "bauer2024_M12_fig8_test3",
    # CHU — prova em NÍVEL DE LEI (§4.54a: µ medido ≈ inerte, wear disp-mode é
    # Archard sem µ). Prova de lei não tem forma valor/piso, e está certo assim.
    "chu2026ti_D0p4mm_F0_49kN_test2",
    "chu2026ti_D0p4mm_F0_61kN_test7",
    "chu2026ti_D0p4mm_F0_73kN_test8",
    "chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9",
    "chu2026ti_D0p5mm_F0_49kN_test3",
    "chu2026ti_D0p7mm_F0_49kN_test4",
    # ECCLES — prova por sobreposição axial (G-B1)
    "eccles2010_fig6_annotated_4kN_axial",
    "eccles2010_fig7d_axial_3p1kN_constant",
    "eccles2010_fig8b_axial_0p7kN_intermittent",
    "eccles2010_fig8d_axial_3p5kN_intermittent",
    # demais — cliff de corrosão, fratura atribuída pelo paper, canal estrutural
    "jcsr2023_plain_outdoor",
    # liu2020_fig9_zinc_AF0.4mm SAIU em 2026-08-21 (2ª saída da catraca por
    # adoção): fechou por mérito com emb do settling lido — retirada em
    # _EXCECOES_RETIRADAS_LIU2020_SETTLING.
    "yang2021_amp0p8mm_ax6kN",
    "yang2021_fig2_typical",
    # ⚠️ SAÍDA 2 TOMADA em 2026-08-15 — 1ª vez que a catraca disparou de fato,
    # e foi sobre assinatura de OUTRA sessão (SUB-SLIP, 15:09, commit 9f660c5).
    # A prova gravada é:
    #   "sub-slip (stick 100% medido): dado colapsa sob stick e nenhuma alavanca
    #    alcança — gth (q=3,8 do próprio paper) varrido 27 células, máx. −48%
    #    sem fechar (0,086/0,296/0,113 na melhor)"
    # Classe "NENHUMA ALAVANCA ALCANÇA", irmã das provas em nível de lei do CHU:
    # não afirma "o modelo é tão bom quanto a dispersão do dado" (que exigiria
    # piso), e sim "o alcançável não contém o alvo". Os três números são as TRÊS
    # PERNAS da melhor célula, não um par valor/piso — por isso o trio não se
    # aplica, e forçá-lo produziria um denominador inventado.
    "10_Yang_2023_phenomenological_model__0_25_mm__2",
))


def _sem_trio() -> set:
    return {cid for cid, prova in R._EXCECOES.items()
            if not _RX_TRIO.search(str(prova or ""))}


def test_baseline_declarado_bate_com_o_medido():
    """O baseline tem de ser o que se mede HOJE — senão a catraca mente.

    Se este assert falhar, alguém mexeu nas provas sem re-medir o estoque.
    """
    assert len(_SEM_TRIO_BASELINE) == 15, (
        "o baseline declarado tem %d entradas; era 21 desde 2026-08-15, "
        "encolheu para 20 em 2026-08-20 (test2 do BAUER), 19 em 2026-08-21 "
        "(liu2020 AF0.4, mérito de adoção) e 15 no mesmo dia (as 4 BAUER "
        "fig6 ganharam o trio conferível — saída por DOCUMENTAÇÃO). "
        "Re-meça antes de editar" % len(_SEM_TRIO_BASELINE))


def test_a_fracao_conferivel_nao_encolhe():
    """⚠️ A TENSÃO QUE A 1ª ATIVAÇÃO DA CATRACA EXPÔS.

    A catraca oferece duas saídas, e a 2ª (declarar a prova como de outra
    natureza) faz o baseline **crescer**. Se toda exceção nova tomar a saída 2,
    a catraca deixa de travar o problema e passa apenas a **documentar a
    deriva** — que é melhor que o silêncio, mas não é o objetivo.

    Este teste torna a deriva **mensurável**: a fração de provas conferíveis
    não pode cair abaixo do piso observado. Hoje são 2 de 23 (8,7 %); o piso
    declarado é 2 em números absolutos, porque com uma amostra tão pequena uma
    fração percentual oscilaria com o denominador e daria falha por ruído.

    Se este teste falhar junto com a catraca, a leitura é clara: as exceções
    estão crescendo E ficando menos auditáveis ao mesmo tempo.
    """
    com_trio = len(set(R._EXCECOES) - _sem_trio())
    total = len(R._EXCECOES)
    assert com_trio >= 2, (
        "só %d de %d exceções têm prova conferível (o piso é 2). A camada "
        "está ficando MENOS auditável enquanto cresce — que é exatamente o "
        "que a catraca existe para tornar visível." % (com_trio, total))


def test_nao_entra_excecao_nova_sem_trio_conferivel():
    """CATRACA: exceção nova tem de registrar `(perna, valor, piso)`.

    ⚠️ O motivo está no histórico, não na estética: SEIS retratações por piso
    inválido, e a única vez que a máquina pôde conferir (2 de 22), as duas
    falharam. Prova que ninguém consegue recomputar é prova que envelhece em
    silêncio.
    """
    novas = sorted(_sem_trio() - _SEM_TRIO_BASELINE)
    assert not novas, (
        "estas exceções entraram SEM o trio conferível `(perna, valor, piso)`:\n"
        "  %s\n"
        "Registre a prova também na forma `res.máx <valor>/<piso> · σ "
        "<valor>/<piso>` junto da prosa — é o que permite re-medi-la quando o "
        "piso da fonte mudar (aconteceu 6 vezes). Se a prova é genuinamente de "
        "LEI, ESCOPO ou PROTOCOLO, acrescente ao _SEM_TRIO_BASELINE com um "
        "comentário dizendo por quê." % "\n  ".join(novas))


def test_o_estoque_so_encolhe():
    """Documentar uma prova antiga é livre — e o baseline deve acompanhar.

    Falha ruidosa (não silenciosa) quando alguém acrescenta o trio a uma prova
    antiga sem tirar a curva do baseline: o estoque declarado passa a mentir
    para cima, e a catraca fica frouxa sem ninguém notar.
    """
    documentadas = sorted(_SEM_TRIO_BASELINE - _sem_trio())
    assert not documentadas, (
        "estas exceções JÁ têm o trio conferível mas seguem no baseline:\n"
        "  %s\n"
        "Tire-as de `_SEM_TRIO_BASELINE` e ajuste o número em "
        "`test_baseline_declarado_bate_com_o_medido`. Baseline inflado deixa a "
        "catraca frouxa." % "\n  ".join(documentadas))


def test_as_duas_conferiveis_seguem_conferiveis():
    """As 2 que a auditoria pôde checar não podem virar prosa.

    Elas são a única amostra verificável da camada — e foi ela que expôs o piso
    inválido do ECCLES. Perdê-la cegaria a camada por completo.
    """
    com_trio = set(R._EXCECOES) - _sem_trio()
    assert len(com_trio) >= 2, (
        "a camada tem %d exceções com trio conferível; eram 2 e esse é o piso. "
        "Sem elas, NENHUMA prova de exceção é re-mensurável." % len(com_trio))
