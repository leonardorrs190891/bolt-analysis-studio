# -*- coding: utf-8 -*-
"""Triagem das curvas FORA do tripe — o instrumento da regra de parada.

SO-LEITURA (le o store; nao simula, nao escreve).

Por que existe: a regra de parada foi pedida sob a leitura "o sigma_res domina 89%
das reprovacoes, nenhuma alavanca o fecha, talvez a perna seja inalcancavel". Essa
leitura mistura numa fila de 98 quatro coisas com REMEDIOS DIFERENTES:

  · excecao ja assinada          -> resolvida, nao e' fila
  · sigma nao julgavel (n<6)     -> declarar; a estatistica nao existe
  · metric-limited (colapso)     -> declarar; nenhuma metrica automatica resolve
  · data-limited (piso > limite) -> dado novo, nao modelo novo
  · FORM-LIMITED                 -> o unico alvo legitimo do pipeline

Medido 2026-07-30 sob a 3a perna POR FONTE (D1 adotado): a fila legitima e' 26,
nao 78 nem 98. Sob a regua GLOBAL vencida dava 18 -- a diferenca sao as 9
data-limited que o D1 absorveu (o limite delas subiu, mas seguem fora).

    py -3.12 New_Theory/regra_de_parada_triagem.py [--json saida.json]
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh                   # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records           # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult                   # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
SALTO_COLAPSO = 0.25      # |Delta dado| entre pontos consecutivos da metrica
N_MIN = 6                 # abaixo disto o sigma_res nao tem suporte estatistico


def pisos_medidos(store: dict, recs: dict):
    """Estrutura de pisos do REPORT, passada inteira a `limite_sres`.

    ⚠️ A 1a versao desta funcao reduzia os pisos a um dict e comparava contra
    `rh.META_SRES` FIXO. Errado desde 2026-07-30: a flag `_SRES_POR_FONTE` foi
    ADOTADA e o limite da 3a perna passou a ser `max(META_SRES, piso da fonte)`.
    Resultado do erro: a triagem rodou sob a regua VENCIDA (tripe 105/fora 98 em
    vez de 124/78). Regra que fica: chame `rh.limite_sres`, NUNCA reimplemente a
    regra do limite -- e' a mesma advertencia que
    `tests/test_meta_numeros_nao_envelhecem.py` carrega.
    """
    pares = [(recs[c].source, CaseResult.from_dict(store[c]))
             for c in store if c in recs]
    return rh._pisos_medidos(pares)


def piso_da_fonte(pisos, fonte: str) -> float | None:
    """Mediana do piso de sigma medido daquela fonte (None se nao ha familia)."""
    v = [f[4] for f in pisos["fam"] if (f[0] or "").split()[0] == fonte]
    return float(np.median(v)) if v else None


# Fontes cuja classe foi ENCERRADA pela regra de parada (2026-08-02,
# "aceleracao tardia": 3 falsificacoes com prereg + 4o candidato
# data-blocked). LU_2024 e YANG_2021 entram porque tambem estao na
# classe (razao terminal >2), mesmo tendo sido excluidas do TESTE por
# cauda de fratura — a parada e' sobre a classe, nao sobre o teste.
# ⚠️ **P-7 ASSINADA e EXECUTADA (opção mínima) em 2026-08-08** — prereg
# `2026-08-08-p7-p15-execucao-prereg.md`. `LU_2024` e `SUN_2025_CRIMP` saíram:
# o discriminante de sinal do viés (`classe_parada_discriminante.py`) mostrou que
# as duas são **falsos positivos PUROS** — 0 curvas com o defeito da classe
# ("retém demais, acelerar mais ajuda") e 2 com o defeito **OPOSTO** (o modelo
# desaba cedo, e acelerar PIORA). O critério que as havia posto aqui é a razão
# de inclinação terminal, que é **cega ao sinal**: dá o mesmo número alto para
# "nunca acelerou" e para "já desabou e está parado no piso".
#
# Evidência independente por fonte: o `SUN` tem r = −0,74/−0,78 contra a forma do
# grupo A e o remédio da classe falsificado em 4 doses; o `LU_2024` entrou por
# decisão **documentada como frouxa** (excluído do teste por cauda de fratura e
# admitido só pela razão > 2 — ver o comentário logo acima).
#
# ⚠️ **Não é reclassificação de censo:** este marcador vive só na TRIAGEM. Ele
# não toca `limite_sres` nem o tripé — muda o que a fila **publica**, não o que
# o modelo acerta.
#
# As 3 fontes MISTAS (CHU_2026, YANG_2019, LIU_2025) e as 2 COERENTES
# (JCSR_2023, YANG_2021) ficam: a opção mínima só remove os falsos positivos
# puros. Decidir curva a curva era a opção 2 da P-7, **não executada** porque
# obriga a re-derivar o critério (c) da regra de parada — decisão nova.
# ⛔ ESTE MOTIVO VENCEU (corrigido 2026-08-20). O critério (c) foi FECHADO em
#    2026-08-14 (`regra_de_parada_proposta.md` §FECHO, achado a95efcc): ele
#    "não era avaliável", a re-derivação "69 %/3 = 23 %" está EXPLICITAMENTE
#    REJEITADA, as 3 camadas estão cumpridas, e o (c) fica preservado apenas
#    "com a redação original para uma fila FUTURA que volte a ter >=2 fontes
#    com rota". ⇒ mudar a população NÃO pode invalidar um critério que não está
#    sendo computado, logo a opção 2 não está mais bloqueada por ele.
#    ⚠️ Este comentário desatualizado me fez publicar, em 2026-08-20 (16:5x),
#    uma proposta afirmando "bloqueado pelo critério (c)" — eu li o comentário
#    em vez de conferir o fecho. Comentário que carrega MOTIVO de não-execução
#    envelhece junto com o motivo; quem executar a opção 2 confere o §FECHO.
#    A proposta viva está em DECISOES_PENDENTES ("a classe_parada esconde 1
#    falso positivo") com os gates G1-G6 congelados, e aguarda só assinatura.
# ⛔ N-LINHA 2026-08-15 (prereg 2026-08-15-nlinha-yang2019-fora-da-classe-parada,
#    assinado 21:42): `YANG_2019` SAI — falso positivo INTEIRO, exatamente o
#    padrao que a P-7 usou para tirar LU_2024 e SUN_2025_CRIMP. A fonte tinha
#    1 membro e ele NAO carrega a assinatura da classe: a
#    `yang2019_M10_amp0p4_5Hz` da rho +0,39 e razao terminal 0,70 — INVERTIDA,
#    o erro se forma CEDO, oposto de "aceleracao tardia".
#    Custo medido rodando este script 2x: tripe 143 -> 143, classe_parada
#    6 -> 5, indecidivel_sem_piso 14 -> 15, form_limited 0 -> 0. NAO gera
#    trabalho — a curva cai em indecidivel (a fonte nao tem piso), e a troca e
#    de "encerrada pela classe" por "nao julgavel, falta replica".
#
# ⚠️ CHU_2026 e JCSR_2023 seguem na lista e hoje tem ZERO membros — as curvas
#    delas sao capturadas antes por `excecao_assinada`. E CORRETO que sigam:
#    elas voltam a valer se a fonte perder excecoes. O risco de escorregamento
#    silencioso ja tem guarda — `test_classe_parada_nao_cresce_calada` fixa a
#    COMPOSICAO e falha nomeando a curva (verificado por perturbacao em
#    2026-08-15: retratar uma excecao do CHU dispara "entraram: [...]").
_FONTES_CLASSE_PARADA = {"CHU_2026", "LIU_2025", "JCSR_2023", "YANG_2021"}

# OPCAO 2 DA P-7 — EXECUTADA em 2026-08-20 sob assinatura do professor ("assinado,
# execute o W"), prereg `docs/superpowers/specs/2026-08-20-classe-parada-curva-a-
# curva-prereg.md`, gates G1-G6 congelados ANTES.
#
# A classe e' atribuida POR FONTE, e o criterio de admissao (razao de inclinacao
# terminal) e' CEGO AO SINAL. O discriminante assinado
# `classe_parada_discriminante.py` desempata pelo SINAL DO VIES TERMINAL
# `mean(modelo - dado)`: >0 retem demais (membro genuino), <0 desabou cedo
# (defeito ESPELHADO, e o remedio da classe -- acelerar mais -- PIORA).
#
# A P-7 (2026-08-08) e a N-linha (2026-08-15) removeram LU_2024, SUN_2025_CRIMP e
# YANG_2019 como falsos positivos PUROS -- fonte inteira sem membro genuino, caso em
# que a opcao MINIMA remove a FONTE. O `LIU_2025` e MISTO (1 genuino + 1 espelhado),
# entao remover a fonte levaria embora a `fig2_single`, que e membro legitimo. Daí a
# opcao 2: decidir CURVA A CURVA, com a exclusao nomeada e a medicao ao lado.
#
# ⚠️ O motivo pelo qual a opcao 2 estava barrada -- "obriga a re-derivar o criterio
# (c)" -- VENCEU: o (c) foi FECHADO em 2026-08-14 (`regra_de_parada_proposta.md`
# §FECHO). Ver o comentario mais abaixo, na lista de fontes.
_FORA_DA_CLASSE_PARADA = {
    # vies terminal MEDIDO (1/3 e 1/4 da cauda, as duas janelas concordam):
    #   -0.0192 / -0.0192  => ESPELHADO, sinal ESTAVEL (nao AMBIGUO)
    # Sai da classe e cai na fila form-limited, com UMA perna violada:
    #   MAE 0.0393 (0.79x) · res.max 0.0863 (0.86x) DENTRO · sigma 0.0419 (1.68x)
    # Piso da fonte = 0.0250 = o global => NAO ha rota F7 por piso.
    "liu2025_M16_amp0p8": (
        "ESPELHADO (vies terminal -0.0192 nas 2 janelas): o modelo esta ABAIXO do "
        "dado no fim, logo o remedio da classe (acelerar mais) PIORA. Mesma "
        "assinatura que tirou LU_2024/SUN_2025_CRIMP (P-7) e YANG_2019 (N-linha); "
        "aqui a fonte e MISTA, entao a exclusao e por CURVA. Forma nomeada em "
        "New_Theory/liu2025_par_de_taxas_opostas.md (8 alavancas varridas, nenhuma "
        "fecha) -- vai para form_limited, que e o estatuto verdadeiro."
    ),
}


def classificar(cid: str, rec: dict, fonte: str, piso: float | None,
                excecoes: set) -> str:
    """A ordem importa: excecao > n<6 > colapso > piso > indecidivel > forma.

    `data_limited_piso` = o piso MEDIDO da fonte esta acima do limite que de fato
    vale para ela (`rh.limite_sres`, que ja incorpora a regra por fonte quando
    `_SRES_POR_FONTE` esta ligada). Com a regra por fonte ADOTADA o limite e'
    `max(META_SRES, piso)`, logo esta classe fica vazia por construcao -- e isso
    e' informacao, nao bug: a adocao de D1 absorveu essa categoria.
    """
    mp = np.asarray(rec.get("metric_pred") or [], float)
    md = np.asarray(rec.get("metric_data") or [], float)
    if cid in excecoes:
        return "excecao_assinada"
    # DECLARADAS vivas do report (n<6, colapso, escopo, resolucao, ...):
    # camada propria ANTES das heuristicas locais — sem isto o script
    # re-classificava curva ja declarada (a fig20_T4Nm apareceu na fila
    # em 2026-08-01 estando declarada por escopo desde 31/07).
    if cid in rh._DECLARADAS:
        return "declarada"
    # CLASSE PARADA (decisao D-A, 2026-08-02): a "aceleracao tardia" foi
    # encerrada pela regra (3 falsificacoes com prereg; 4o candidato
    # data-blocked). Estas curvas NAO viram "declarada" — o modelo esta
    # errado nelas e nos sabemos; declarar inflaria o resolvido com
    # fracasso. O marcador so diz "fechada, aguardando dado novo", para o
    # leitor nao as ler como fila de trabalho.
    if fonte in _FONTES_CLASSE_PARADA and cid not in _FORA_DA_CLASSE_PARADA:
        return "classe_parada(aceleracao tardia)"
    # ⚠️ GUARDAS P-10 e P-11 (assinadas 2026-08-07). Ate aqui estas camadas
    # classificavam SO' pelo dado (n de pontos, tamanho do salto) e nunca
    # comparavam ao ERRO do modelo — e por isso ofereciam de volta declaracoes
    # que a assinatura acabara de REJEITAR (a `Yang2023 0,50` caia em
    # `metric_limited_n_baixo` com MAE 4,8x, que `n<6` nao desculpa: MAE de 5
    # pontos e' perfeitamente julgavel). Sem estas guardas as linhas "efeito
    # das camadas" contam como ganho uma re-declaracao ilegitima.
    if len(mp) < N_MIN:
        # `n<6` justifica so' o sigma; se as pernas JULGAVEIS falham, nao cobre.
        mae = float(rec.get("mae") or 0.0)
        mx = float(rec.get("maxerr") or 0.0)
        if mae <= rh.META_MAE and mx <= rh.META_MAX:
            return "metric_limited_n_baixo"
    if len(md) > 2 and float(np.max(np.abs(np.diff(md)))) > SALTO_COLAPSO:
        # o argumento do colapso exige que o res.max caia NA VIZINHANCA do
        # penhasco; as declaradas validas ficam a 0-1 indices dele.
        i_sal = int(np.argmax(np.abs(np.diff(md))))
        i_res = int(np.argmax(np.abs(mp - md))) if len(mp) == len(md) else -99
        if abs(i_res - i_sal) <= 2:
            return "metric_limited_colapso"
    if piso is None:
        return "indecidivel_sem_piso"
    if piso > rh.META_SRES and not rh._SRES_POR_FONTE:
        return "data_limited_piso"
    return "form_limited"


def main() -> int:
    store = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pisos = pisos_medidos(store, recs)
    exc = set(rh._EXCECOES)

    def limite(fonte: str) -> float:
        """O limite da 3a perna QUE VALE para esta fonte — helper do report."""
        return float(rh.limite_sres(fonte, pisos))

    tripe, fora = [], []
    for cid, r in store.items():
        if not r.get("ok") or cid not in recs:
            continue
        # censo canonico do report: exclui USER/UFU_LAB ("por enquanto",
        # 2026-08-01) e a duplicata amp1p0<->T22 — sem isto o script contava
        # 208 "comparaveis" e estrita 137 onde o censo e' 203/136 (medido
        # em 2026-08-01; era o proprio envelhecimento que ele denuncia).
        if not rh.caso_comparavel(recs[cid].source, cid):
            continue
        sd = r.get("resid_std")
        # regra n<6 (assinada 2026-08-01): sigma nao-julgavel => fora do
        # tripe; o classificador da fila ja rota estas p/ "declarada".
        md_n = len(r.get("metric_data") or [])
        if sd is not None and md_n and md_n < N_MIN:
            sd = None
        if sd is None and (r.get("resid_std") is None):
            continue
        if (sd is not None
                and r["maxerr"] <= rh.META_MAX and r["mae"] <= rh.META_MAE
                and sd <= limite(recs[cid].source)):
            tripe.append(cid)
        else:
            fora.append(cid)

    cat: dict[str, list] = defaultdict(list)
    for cid in fora:
        r = store[cid]
        src = recs[cid].source
        c = classificar(cid, r, src, piso_da_fonte(pisos, src), exc)
        cat[c].append((cid, src, r["mae"], r["maxerr"], r["resid_std"],
                       limite(src)))

    print(f"TRIAGEM - store {next(iter(store.values())).get('engine_fingerprint')}")
    print(f"  3a perna POR FONTE: {rh._SRES_POR_FONTE} "
          f"(limite = max({rh.META_SRES}, piso da fonte))")
    print(f"  regua: res.max<={rh.META_MAX} MAE<={rh.META_MAE}")
    print(f"  passam o tripe: {len(tripe)}   -   fora: {len(fora)}\n")
    ordem = ["excecao_assinada", "declarada",
             "classe_parada(aceleracao tardia)", "metric_limited_n_baixo",
             "metric_limited_colapso", "data_limited_piso",
             "indecidivel_sem_piso", "form_limited"]
    for k in ordem:
        v = cat.get(k, [])
        print(f"  {k:26s} {len(v):3d}  {100*len(v)/max(len(fora),1):5.0f}% das fora")

    fl = cat.get("form_limited", [])
    # ------------------------------------------------ A FILA, EM DUAS LINHAS
    # (assinado pelo professor em 2026-08-15 20:04, "assine e continue em loop";
    #  medicao em `fila_zero_e_parcialmente_estrutural.md`)
    #
    # ⚠️ POR QUE DUAS LINHAS E NAO UMA. `form_limited` e' o rotulo do
    # classificador, e o rotulo e' uma CONJUNCAO: nao desculpavel E nao
    # explicavel por metrica/escopo E **a fonte tem piso medido**. Como
    # `indecidivel_sem_piso` PRECEDE `form_limited` na ordem de `classificar`,
    # curva de fonte SEM PISO nunca pode receber o rotulo — tenha ou nao defeito
    # diagnosticavel. Medido: **55 das 205** curvas estao em fontes sem piso
    # (10 fontes), barradas POR CONSTRUCAO, passem ou nao.
    #
    # A sessao B (b434c35) exibiu 5 curvas do ICMEZ_2025 com FORMA NOMEADA e
    # rota — o modelo trava no `loose_arrest_floor` 0,308 e o dado atravessa —
    # que jamais poderiam entrar na fila. ⇒ **uma curva pode ser TRABALHO sem
    # ser ROTULADA trabalho**, e publicar so' o rotulo faz "fila ZERO" ser lido
    # como "nao ha trabalho".
    #
    # `_FORMA_NOMEADA` e' lista DECLARADA, no idioma de `_EXCECOES`/
    # `_DECLARADAS`: entra curva cuja forma faltante foi NOMEADA por medicao,
    # com o documento que a prova. Nao e' estatuto — nao desculpa nada, nem sai
    # do censo. E' so' a resposta a "ja sabemos o que consertar?".
    _FORMA_NOMEADA = {
        # LU_2024 T10Nm (2026-08-16). A UNICA curva form-limited do projeto, e
        # ela so' reapareceu na fila porque a correcao do pico espurio tirou o
        # colapso FALSO que a fazia contar como metric-limited. Barra:
        #   REGIME  : transversal 1,0 mm; a fonte varre F0 em 7x (2105-15027 N);
        #   CANAIS  : embedding 62% da perda (0,698 abs contra 0,189 rotacional);
        #   FORMA   : profundidade de encaixe INDEPENDENTE da pre-carga => o
        #             excesso de perda no 1o ciclo vai com 1/F0 (r = +0,995), e
        #             TROCA DE SINAL na maior pre-carga (T28 perde de MENOS);
        #   DADO    : limpo, e recem-conferido pela guarda de monotonicidade;
        #   CONTROLE: no CACCESE_2009 (embedding 0,2% da perda) o sinal SOME
        #             (-0,447) — a ausencia esta onde o canal esta ausente;
        #   ROTA JA DESCARTADA: 4 alavancas livres varridas, nenhuma fecha;
        #             grade conjunta emb_depth x N_emb 0 de 25; forma de cauda
        #             impossivel por aritmetica (incremento tardio 0,0034); e o
        #             SPLIT absoluto<->proporcional (emb_depth x emb_load_frac,
        #             16 celulas) falsificado nos DOIS eixos — subir o termo
        #             proporcional PIORA a alvo, e o emb_depth que ela pede e'
        #             2,7x menor do que a `fig18_amp0p25` (protegida) permite.
        #   ROTA MEDIDA (prereg 2026-08-16, `lu2024_embedding_pressao_
        #             resultado.md`): o campo `emb_pressure_exp` foi construido
        #             default-inerte e a lei CONSERTA o que o diagnostico
        #             nomeou — a queda no 1o ciclo vai de 0,627 para 0,344
        #             contra 0,362 do dado (residuo em N=1: -0,265 -> +0,018),
        #             com as 12 irmas movendo +0,0000 (isolamento estrutural
        #             pelo `min(1,.)`). Mas ela NAO fecha sozinha (3,2x): ao
        #             arrumar o 1o ciclo aparece um SEGUNDO defeito atras dele
        #             — o modelo trava no `loose_arrest_floor`=0,10 da fonte e
        #             o dado retem 0,310. Os dois juntos FECHAM com folga
        #             (0,0112/0,0284/0,0138, pior perna 0,55x), mas o piso NAO
        #             TEM LEI de pre-carga aqui (retencao do dado 0,037/0,309/
        #             0,187/0,064/0,234 pela Tabela 9 do PAPER, nao-monotona,
        #             corr com 1/F0 = -0,51; nucleo absoluto variando 45x)
        #             => seria fit por curva. NADA ADOTADO.
        #             ⚠️ ERRATA 2026-08-16 (manha): a 1a redacao publicava
        #             0,142/0,310/0,190/0,102/0,233 — o ultimo ponto ACIMA do
        #             FLOOR_TRIM de 0,10, nao o terminal. Conclusao inalterada.
        #   PERGUNTA RESPONDIDA no mesmo dia lendo o PDF
        #             (lu2024_fig20_nao_monotonia_e_fisica.md): a nao-monotonia
        #             e' FISICA e PUBLICADA (Tabela 9 + p.19: 4 N.m "nao atinge
        #             o efeito de aperto"; 10 N.m e' o otimo; de 10 a 22 N.m a
        #             atenuacao acelera com o torque; 28 N.m recupera). Mistura
        #             de protocolos REFUTADA para a fig20 (1 protocolo, 1
        #             amplitude, 1 maquina) e NENHUM estatuto muda.
        #             ⛔ RETRATADO no mesmo dia: eu publiquei "o MODELO
        #             reproduz a nao-monotonia (Spearman +0,700)" e era FALSO —
        #             com FLOOR_TRIM ligado a simulacao e' TRUNCADA e o
        #             np.interp grampeia, entao comparei o modelo em N=54 com o
        #             dado em N=99. Re-simulado sem piso, o terminal do modelo
        #             e' PLANO: 0,000 na T4 e 0,092/0,094/0,095/0,097 nas
        #             outras — faixa de 0,005 contra os 0,272 do dado; Spearman
        #             cai a +0,300. O terminal e' fixado pelo
        #             loose_arrest_floor, FRACAO UNICA de F0, que por
        #             construcao nao espalha. Isso REFORCA o fecho da rota:
        #             o dado nao tem lei E o modelo nao tem espalhamento.
        #             REGRA que fica: toda leitura de TERMINAL exige
        #             FLOOR_TRIM = 0 no sandbox.
        # ⚠️ COMPLEMENTO (sessao A, 2026-08-16 04:1x, medicao independente):
        # a linha acima mede a RETENCAO DO DADO e a acha NAO-MONOTONA em
        # torque (corr com 1/F0 = -0,22) => 'nao ha lei de pre-carga no dado'.
        # Medi outra coisa e ela e' complementar: o VIES DO MODELO e MONOTONO
        # em torque — MAE 0,342/0,251/0,157/0,036/0,101 em T4/10/16/22/28,
        # rho(torque,vies) = +0,900, os 5 vieses NEGATIVOS, e o minimo cai
        # EXATAMENTE na T22, que e' a curva contra a qual a fonte foi
        # calibrada (mesmo ensaio da fig18_amp1p0).
        # ⇒ dado nao-monotono + erro do modelo monotono com minimo na ANCORA
        # = a dependencia espuria de torque e' DO MODELO, nao do dado. E' a
        # assinatura mais limpa de sobreajuste a ancora que a campanha mediu.
        # E o erro inteiro e UM DEGRAU no 1o ciclo (salto -0,2650 entre os
        # ciclos 0 e 1, |vies|/MAE = 1,00, tardio total 0,00338), com o
        # embedding a 0,698 da perda — exatamente o que emb_pressure_exp
        # (945f363, default-inerte) modela. Prova:
        # New_Theory/lu2024_fig20_v_centrado_na_ancora.md
        # ✅ RETIRADA 2026-08-19 (catraca de estatuto): a curva FECHOU o tripe
        # pela adocao emb_pressure_exp=3,0 + floor LIDO 0,3195 (prereg
        # lu2024-t10-pressao-mais-piso-lido, gates 6/6; 0,2514->0,0198/
        # 0,0344/0,0176). A forma nomeada acima esta ADOTADA — a entrada sai
        # da lista porque a curva saiu das abertas, nao porque a prova
        # envelheceu.
        # (entrada removida: "lu2024_M8_fig20_T10Nm")
        # RE-MEDIDAS 2026-08-20 (ataque das 9): a forma que as 3 exigem tem
        # NOME AGORA — o decay e' EXPONENCIAL (dF/dN ~ F: 0,30mm perde 94% com
        # tau~170 ciclos; taxa relativa ~constante), a assinatura do kernel de
        # TORQUE (T ~ F). Mas o torque NAO DISPARA nelas (ratchet=0 => F_fim
        # 0,94-1,17) e o k_ratchet vigente (~slip) tem forma OPOSTA (acelera
        # onde o dado desacelera) — dai os "3 sinais". Sem leitura disponivel
        # p/ as constantes do disparo (IJPEM sem rotacao publicada, mu sem
        # medicao) => seguem ABERTAS; reabrem com o PDF/observavel novo.
        # AS 3 DO YANG_2023 FORAM RETIRADAS em 2026-08-16 (13:0x), 4 h depois
        # de eu as ter acrescentado. A forma que nomeei ("o dado arresta em
        # 0,165 e o modelo nao arresta") e FALSA: eu li `metric_data`, que e o
        # dado DEPOIS do FLOOR_TRIM=0,10, e chamei o ultimo valor dele de piso.
        # O dado CRU colapsa a 0,02-0,06 nas 6 => loose_arrest_floor=0 esta
        # CERTO. E os vieses sao MISTOS em sinal (-0,159 a +0,239), o que
        # confirma o veredito anterior da sessao paralela (16300e8): "3
        # regimes, 3 sinais, NAO e uma classe". Retratacao integral em
        # New_Theory/yang2023_piso_nunca_lido.md.
        # RETIRADA 2026-08-19/20 (catraca de estatuto): FECHOU o tripe pela
        # adocao Fig. 3 + particao (serie lk13p8) — ver prov em adopted_configs.
        # (entrada removida: "demir2024_amp0p3_F14p3_lk13p8")
        # RETIRADA 2026-08-19/20 (catraca): FECHOU pela adocao settling do intercepto + taxa constante (floor 0 pela leitura da TAXA).
        # (entrada removida: "demir2024_amp0p3_F14p3_lk19p8")
        # RETIRADA 2026-08-19/20 (catraca de estatuto): FECHOU o tripe pela
        # adocao Fig. 3 (phi* dos autores) + particao — ver prov em adopted_configs.
        # (entrada removida: "demir2024_amp0p3_F17p6_lk13p8")
        # RETIRADA 2026-08-19/20 (catraca): FECHOU pela adocao settling do intercepto + taxa constante.
        # (entrada removida: "demir2024_amp0p3_F17p6_lk19p8")
        # RETIRADA 2026-08-19/20 (catraca de estatuto): FECHOU o tripe pela
        # adocao Fig. 3 + particao (serie lk13p8) — ver prov em adopted_configs.
        # (entrada removida: "demir2024_amp0p4_F17p6_lk13p8")
        # YANG_2021 (2026-08-15 23:0x, assinatura "assine tudo"). Forma nomeada
        # pela sessao B em `yang2021_stick_sustentado_resultado.md` e conferida
        # por mim contra a barra do ICMEZ — ela e tao especifica quanto:
        #   REGIME  : 8 de 8 curvas em STICK (slip=0 em 100% dos ciclos);
        #   CANAIS  : embedding 54-83% + creep 10-28% (rotacional <=10%);
        #   FORMA   : residuo ~0 no inicio CRESCENDO ate o fim (+0,045 a
        #             +0,122) — o dado segue perdendo pre-carga SOB STICK e a
        #             lei vigente nao acompanha;
        #   DADO    : limpo, sigma_res e 8-17x o ruido da propria curva;
        #   ROTA JA DESCARTADA: o `gth` ja esta adotado aqui (1,5e-7) e mexer
        #             nele da NET ZERO (5e-7 fecha 2 e quebra 2); acima disso,
        #             colapso (MAE x5 a x22). 6 celulas.
        # ⚠️ Nao e "falta forma": a forma existe. Falta-lhe a DEPENDENCIA que
        # separa estas curvas — e isso e um defeito NOMEADO, nao uma lacuna.
        # amp0p5 e amp1p0 fechadas em 2026-08-19 (alvos 3-4 da sequencia) por
        # GEOMETRIA DOS INPUTS: o sinal do residuo tardio alterna 3x ao longo
        # do unico input que varia (+0,5 / +-0,6 / -0,7 / +0,8 / +1,0) e as
        # abertas CERCAM as protegidas — nenhuma lei monotona de amplitude da
        # taxa as pontas sem dar ao meio (e o meio ja e' negativo: e' o porque
        # do net-zero do gth_k). E replicas nominais identicas tem sinais
        # OPOSTOS (r1 +0,045 x r2 -0,052 x r3 -0,027, mesma celula 0,6/8kN) —
        # nenhuma f(inputs) separa inputs IGUAIS. Colaterais: o canal tardio
        # da amp1p0 e' o GTH (as alavancas rotacionais classicas dao Delta=0
        # por RAMO, nao por companheiro); e o F_amp axial do paper (2-11,2 kN,
        # 90 graus defasado) NAO entra no modelo (theta=90 => cos=0 => inerte
        # estrutural, medido com instrumento validado) — forma faltante
        # honesta que NAO destravaria as abertas (r1/r2/r3 provam).
        "yang2021_amp0p5mm_ax8kN": "yang2021_abertas_geometria_dos_inputs.md",
        # r1 re-diagnosticada em 2026-08-19 (alvo 1 da sequencia de ataque): o
        # defeito DELA nao e o stick sustentado das irmas — e' DISPERSAO DE VIDA
        # entre especimes (r1 morre em 12400, r2/r3 em 14649/16251) invadindo a
        # janela da metrica. QUATRO fechamentos medidos: F7 fechada (sigma do
        # modelo 2,6x o piso, inclusive na grade esparsa da propria r1); rampa
        # de fratura POR ESPECIME com N_f lido do dado = ancora perfeita
        # (D(N_frat)=1,000 nas 3) mas a metrica PIORA (sigma 0,0268 -> 0,0689 e
        # 0,0752 nas 2 formas do treino; cliff bit-identico por construcao);
        # trim vigente consistente com a convencao da fonte; instrumento de
        # grade descartado. O modelo esta no CENTRO das 3 replicas (sigma 0,007
        # vs r2, 0,006 vs r3, 0,027 vs r1) — move-lo quebraria as 2 que fecham.
        "yang2021_amp0p6mm_ax8kN_r1": "yang2021_r1_sem_rota_resultado.md",
        "yang2021_amp1p0mm_ax2kN": "yang2021_abertas_geometria_dos_inputs.md",
        # SUN_2025_CRIMP (2026-08-15 23:4x). Diagnostico meu pelo shell
        # canonico, contra a MESMA barra do ICMEZ/YANG_2021/ROUSSEAU:
        #   FORMA  : residuo TROCA DE SINAL (+0,027 -> -0,079 -> -0,174),
        #            rho -0,69, curvatura sub-classe B;
        #   CANAL  : rotacional domina o TOTAL (0,655 x 0,268 do embedding)
        #            e tem 0% do incremento TARDIO — ele MORRE antes do fim
        #            enquanto o dado segue caindo. Mesma estrutura do ICMEZ
        #            (canal arresta, dado atravessa) e do ROUSSEAU.
        #   ROTA   : melhor alavanca (tr_loose_gain=2,058) leva sigma 4,73x ->
        #            3,20x, e a dose seguinte EXPLODE (5,91x).
        # ⚠️ SO a `grease_standard` entra. A irma `grease_crimp` e OUTRO
        # DEFEITO: residuo NAO troca de sinal (rho -0,10 = OFFSET), erro se
        # forma CEDO, e ela falha SO no sigma por 21%. Mesma fonte, ambas
        # abertas, ambas com rotacional dominante no total — e forma OPOSTA.
        # Este e o ponto exato onde raciocinar POR SIMETRIA erraria: a barra
        # e a FORMA MEDIDA, nao o parentesco de fonte.
        # ✅✅ FECHADA EM 2 PASSOS em 2026-08-19 (mandato "melhore a modelagem"
        # + "trabalhe mais"). PASSO 1 (prereg sun-standard-kernel-cinematico):
        # kernel torque-runaway -> graded_scrit SO nesta curva, MESMO DOF
        # (k_graded 0,02 + aexp 8,0 substituem gain 2,94 + floor mal-rotulado;
        # floor re-lido 0,0284, plateau=False declarado). 0,0999/0,3193/0,1182
        # -> 0,0604/0,1103/0,0404 (4,73x -> 1,62x). PASSO 2 (prereg
        # sun-standard-ccreep-token): sobrou um ARCO (modelo 23% lento cedo,
        # 53% rapido tarde) e a rota foi ZERO-numero-novo — estender o C_creep
        # 9e-11 do token `standard` (ja adotado nos 2 axiais standard) a
        # transversal greased. A greased CRIMP rejeita o valor (medido ANTES:
        # 3x pior) — consistente com os axiais crimp, que nunca o receberam.
        # Resultado: 0,0191/0,0431/0,0223 — FECHA O TRIPE (censo 144->145).
        # ✅ RETIRADA 2026-08-19 (catraca de estatuto, mesma regra da T10 do
        # LU): a curva fechou => sai da lista de formas nomeadas de ABERTAS;
        # a prova segue em sun_standard_kernel_cinematico_resultado.md.
        # (entrada removida: "sun2025efa109235_transverse_grease_standard")
        # LIU_2025 (2026-08-16 00:5x). As 2 abertas tem erros de taxa OPOSTOS,
        # e a rampa de fratura JA ESTA LIGADA nas duas (fat_ramp_D_on=0,75,
        # q=8,0) — minha hipotese de que estivesse desligada foi falsificada.
        #   amp0p8      curvatura B, rho -0,52, erro no MEIO/FIM (u=0,97);
        #               tardio 0,466 = wear 47% + fatigue 43%; as 8 alavancas
        #               varridas e NENHUMA fecha (as 2 que melhoram o sigma
        #               quebram o res.max: 1,20x e 1,42x).
      # 3a releitura 2026-08-20: D_on=0,89 (o joelho MEDIDO do especime,
      # lido para CIMA — a direcao que a procedencia permite) e' INERTE
      # (0,0270 identico): o deficit-rampa acumula desde cedo, nao no fim.
      # Rotas esgotadas: 0/8 (16/08) + fat re-ancorados (19/08) + D_on lido.
        #   fig2_single curvatura A, rho +0,97 = RAMPA (deficit de TAXA, o erro
        #               ACUMULA e alavanca de nivel nao conserta), tardio
        #               90% fadiga; falha SO o sigma, por 8%.
        # ⚠️ Mesma fonte, direcoes OPOSTAS — o mesmo que o par do SUN mostrou.
        # amp0p8 SAIU em 2026-08-21 (17:0x): ganhou estatuto de DECLARADA
        # (decisao (b) do item 8 — ESGOTAMENTO MEDIDO, 17 estruturas
        # falsificadas incl. a forma onset_burst_W desenhada para ela;
        # par_de_taxas §5-§7). Excecao/declaracao supersede forma nomeada.
        # fig2 re-sondada em 2026-08-19 (alvo 2 da sequencia): as fat_* NAO sao
        # "alavancas livres" e ficaram fora da varredura anterior — sondadas
        # agora com C1 RE-ANCORADO por celula (licao D-Z). A direcao EXISTE
        # (D_on 0,75->0,60 melhora as 3 pernas, rho +0,96->+0,76) mas nao fecha
        # (sigma 0,0262 = 1,05x) e morre POR PROCEDENCIA: o joelho MEDIDO da
        # fig2 e' 0,89 da vida — o MAIS TARDIO da fonte — e abaixar D_on
        # contraria o dado do proprio especime e o handbook; alem de o degrau
        # seguinte (0,60->0,50) explodir (sigma 0,0983): fio de navalha (D-L).
        # Colateral: o par de "replicas" tem 46% de dispersao de VIDA (9870 vs
        # 14400) — mesma estrutura do yang2021_r1.
        "liu2025_M16_fig2_single": "liu2025_fig2_forma_rampa_fechada.md",
        # SUN grease_crimp (2026-08-16 01:1x) — a mais perto de fechar de todo
        # o conjunto aberto: falha SO o sigma, por 21%.
        # O shell diz que ela FECHA com loose_arrest_floor=0,162, mas a
        # procedencia esta TRAVADA (lido-do-dado, assintota final crua). Em vez
        # de aceitar o cadeado, VERIFIQUEI a leitura:
        #    floor vigente 0,142  x  assintota do dado 0,1422 (media dos
        #    ultimos 10%; ultimo ponto 0,1420) => o cadeado esta CERTO.
        # ⇒ o 0,162 que fecha a metrica NAO e o piso do dado: ele faria o
        # modelo PARAR ACIMA de onde o ensaio parou — fecharia o sigma tornando
        # o modelo ERRADO sobre o ponto final. E o fim ja esta certo
        # (metric_pred 0,1400 x dado 0,1420).
        # FORMA: o modelo chega ao valor final certo pela perda total certa,
        # mas por um CAMINHO diferente — offset formado nos primeiros ciclos
        # (rho -0,10 = nivel uniforme, maior salto em u=0,00) que nunca se
        # resolve. Tardio total 0,00133 => forma sobre o fim nao move a curva.
        # RETIRADA 2026-08-19/20 (catraca): FECHOU pela adocao k do token da irma standard (ZERO numero novo) + floor 0,142 lido.
        # (entrada removida: "sun2025efa109235_transverse_grease_crimp")
        # ROUSSEAU_2025 (2026-08-15 23:3x, assinatura "assine e continue" —
        # sessao B, simetria com as duas entradas acima e a MESMA barra):
        #   REGIME  : as 4 abertas sao as 4 ROTACIONAL-DOMINADAS da fonte
        #             (72-83%); as 3 em STICK (embedding+creep) PASSAM o tripe
        #             — a separacao e' por canal, nao por material nem por
        #             espessura;
        #   CANAIS  : rotacional 72-83%, embedding 9-20%, wear ~0;
        #   FORMA   : vies POSITIVO nas 4 (+0,052 a +0,155) com |vies|/MAE
        #             0,90-1,00 (erro de NIVEL, sinal unico) e o deficit
        #             CRESCE com o slip resolvido;
        #   DADO    : limpo, sigma_res e 4,7-14x o ruido da propria curva;
        #   ROTA JA DESCARTADA: 10 celulas de `k_ratchet` (com e sem expoente
        #             de amplitude). Os otimos sao DISJUNTOS dentro da fonte —
        #             ~0,003-0,005 para a `steel_t10` e EXATAMENTE 0 para as
        #             outras 3 — porque os slips do mesmo rig diferem 10x
        #             (0,03 vs 0,44 mm) e o deficit e' comparavel. O expoente
        #             nao resolve: `LOOSE_AMP_REF`=0,5 mm esta ACIMA de todos
        #             os slips do rig, entao exp<1 AMPLIFICA em vez de
        #             comprimir (7,1x em 0,03 mm contra 1,09x em 0,44 mm).
        # ⚠️ Mesma leitura das outras duas fontes: a forma EXISTE (canal
        # rotacional + ratchet cinematico); falta-lhe a DEPENDENCIA de slip.
        # ✅✅ FECHADA EM 2 PASSOS 2026-08-19 (steel_t10): o traco de ROTACAO
        # publicado (Fig. 5, eixo secundario) deu TODAS as constantes —
        # passo 1 por LEITURA direta (dF/dtheta=919,7 N/deg r2=0,9997 =>
        # free_spin_kin=0,7195; emb=creep=0 do ponto (20,1.0000)): 0,155 ->
        # 0,0289, sigma 1,30x; passo 2 por REGRESSAO a taxa observada (LSQ
        # Hill*arrest r2=0,891, floor 0,0295 NAO-barreira, degenerescencia
        # (floor,aexp) declarada): 0,0158/0,0324/0,0098 — TRIPE, folga >=60%.
        # Vizinhanca 8/8 fecha. RETIRADA da lista pela catraca de estatuto;
        # prova em rousseau_t10_ratchet_lido_resultado.md. As 3 do HDPE tem
        # traco theta na Fig. 4 => mesma rota, leituras proprias (prereg
        # futuro).
        # (entrada removida: "rousseau2025_steel_t10")
        # RETIRADA 2026-08-19/20 (catraca de estatuto): FECHOU o tripe pela
        # adocao fig6-theta (leituras proprias da Fig. 6 + particao) — ver prov em adopted_configs.
        # (entrada removida: "rousseau2025_steel_t10_amp0p2")
        # RETIRADA 2026-08-19/20 (catraca de estatuto): FECHOU o tripe pela
        # adocao particao + theta bisectado (Fig. 4 re-extraida) — ver prov em adopted_configs.
        # (entrada removida: "rousseau2025_hdpe_t10")
        # RETIRADA 2026-08-19/20 (catraca de estatuto): FECHOU o tripe pela
        # adocao particao + theta bisectado (Fig. 4 re-extraida) — ver prov em adopted_configs.
        # (entrada removida: "rousseau2025_hdpe_t12")
        # YANG_2019 amp0p4_5Hz (2026-08-16 00:3x, sessao B). O dossie T1-T13
        # (2026-08-10) ja a declarava form-limited com SEIS falsificacoes
        # pre-registradas; o que faltava era a barra desta lista, MEDIDA agora
        # em vez de citada:
        #   REGIME  : e' a UNICA da fonte em quase-stick — slip/delta = 0,18
        #             (7% dos ciclos em stick) contra 0,52 · 0,68 · 0,73 · 0,93
        #             das 4 irmas, todas no tripe;
        #   CANAIS  : embedding 57% + creep 40% (rotacional 2%) — canais de
        #             STICK; as 4 irmas vivem de rotacional+wear (55-70%);
        #   FORMA   : o modelo perde DEMAIS nos dois primeiros tercos
        #             (-0,093 / -0,131) e reencontra o dado no fim (-0,007);
        #   DADO    : limpo, sigma_res 8,7x o ruido da propria curva;
        #   ROTA JA DESCARTADA: 6 falsificacoes com prereg (s1_amp_gate na
        #             perna errada; graded_scrit quebra o grupo; slip_onset_W
        #             inerte em stick; cascata de mu destroi as 0,6; PR-21
        #             completo 0/5; `gth` LIMITADO POR CONSTRUCAO — o corte de
        #             stick o prende ao limiar de slip).
        # ⚠️ Mesmo padrao das outras quatro fontes desta lista: as constantes
        # foram fitadas onde os canais de SLIP dominam, e a unica curva em que
        # os canais de STICK dominam nao segue.
        # ATUALIZACAO 2026-08-20 (ataque das 9): o DADO re-lido e' PLATO ate
        # N~4700 (1,000-1,004!) + ACELERACAO progressiva — nao settling. A forma
        # nova gth_accel_p (lida: p=2,87, LSQ integral r2=0,969) + emb=creep=0
        # do plato publicado entrega +-0,014 ate N=9000; o modelo ALCANCA a
        # transicao stick->slip em F=0,916 (onde o dado acelera!) mas RE-TRAVA
        # num equilibrio espurio (dF=0,000 exato pos-8900) onde o dado colapsa
        # sem volta => a forma que falta e' HISTERESE DE TRANSICAO (oxido
        # quebrado nao re-trava). Ganho nao-adotavel: mx piora (0,141->0,188).
        # REFINADO 2026-08-20 (2a passada, mandato 09:49): a historese
        # mu_s/mu_k FOI CONSTRUIDA (mu_kinetic_frac + latch stick_broken,
        # default-inerte, TDD 3/3) e a CADEIA COMPLETA medida — a causa-raiz
        # do congelamento era o slip_onset_W=40000 do GRUPO (gate Hill zera o
        # canal; W so acumula com slip). Com o gate liberado + mu_k, o
        # colapso EMERGE mas e' AVALANCHE (~1000 ciclos vs 2000+ do dado,
        # comecando cedo demais) — o feedback mu_k->slip->dreno do modelo e'
        # mais rapido que o real. Persegui-lo custaria 6 numeros por curva =
        # fit por partes (item D). FICA: capacidade no engine + observaveis
        # nomeados (joelho 0,916; taxa da avalanche).
        # RETIRADA 2026-08-20 (catraca): FECHOU pela adocao gth-lido + trim@9000
        # (16o trim do secB, transicao de regime out-of-model; prereg
        # yang2019-amp0p4-gth-trim, 6 estruturas falsificadas). 0,0966 -> 0,0087.
        # (entrada removida: "yang2019_M10_amp0p4_5Hz")
        # ⛔ NAO entram (medido 2026-08-15 23:2x,
        # `yang2023_e_a_lei_do_sinal_resultado.md`): as 3 abertas do
        # `YANG_2023_IJPEM` (0,30 · 0,35 · 0,50 mm) NAO formam classe — tres
        # regimes (13% · 68% · 0% de stick) e tres SINAIS de residuo
        # diferentes. Nomear forma exige discriminante medido, e aqui ele
        # aponta para tres coisas distintas; entrar seria rotular sem prova.
    }
    # ⚠️ POR QUE cada aberta SEM forma nomeada nao tem forma. Declarado, nao
    # deduzido (2026-08-16 19:0x).
    #
    # Ate aqui a saida deixava as sem-forma ANONIMAS e as explicava com uma
    # frase sobre OUTRA populacao ("das 16 varridas em 97b82c5..."). As 3 de
    # hoje nao estao entre aquelas 16: elas sairam de `_FORMA_NOMEADA` na
    # RETRATACAO de 2026-08-16 13:0x, quando a forma que eu havia nomeado para
    # elas ("o dado arresta em 0,165") caiu — eu lera `metric_data`, que e o
    # dado DEPOIS do FLOOR_TRIM=0,10, e chamara o ultimo valor de piso.
    #
    # O veredito correto JA ESTAVA neste arquivo, no comentario do bloco acima.
    # So' nao chegava a quem le a SAIDA. Duas coisas diferentes que a versao
    # antiga confundia:
    #   "ninguem olhou"                 -> trabalho pendente
    #   "olhou e mediu que nao ha forma" -> resultado, nao lacuna
    #
    # Curva que caia aqui SEM entrada neste dict e' o 1o caso: aparece como
    # SEM MOTIVO DECLARADO, em vez de ser absorvida por uma explicacao que nao
    # a cobre.
    _SEM_FORMA_MOTIVO = {
        "10_Yang_2023_phenomenological_model__0_30_mm__8":
            "3 regimes/3 sinais - nao formam classe (yang2023_e_a_lei_do_sinal)",
        "10_Yang_2023_phenomenological_model__0_35_mm__3":
            "3 regimes/3 sinais - nao formam classe (yang2023_e_a_lei_do_sinal)",
        "10_Yang_2023_phenomenological_model__0_50_mm__9":
            "3 regimes/3 sinais - nao formam classe (yang2023_e_a_lei_do_sinal)",
    }
    abertas = [cid for cid in fora
               if cid not in exc and cid not in rh._DECLARADAS]
    com_forma = sorted(c for c in abertas if c in _FORMA_NOMEADA)
    print(f"\nTRABALHO - leitura em DUAS linhas (o rotulo nao e' a fila real)")
    print(f"  (1) `form_limited` (rotulo do classificador) ......... {len(fl)}")
    print(f"  (2) fora, SEM estatuto assinado, com FORMA NOMEADA ... {len(com_forma)}"
          f"  de {len(abertas)} abertas")
    for c in com_forma:
        print(f"        {c[:44]:44s} {_FORMA_NOMEADA[c]}")
    if len(abertas) > len(com_forma):
        # ⚠️ ATUALIZADO 2026-08-15 20:4x — §4.43 no proprio codigo, 40 min depois
        # de escrito. A versao original dizia "as outras NAO foram perguntadas,
        # o (2) e' PISO nao total". ELAS FORAM: varri as 16 pelo ataque_curva.py
        # (commit 97b82c5). Resultado: 15 devolveram "NENHUMA alavanca livre
        # fecha" e 1 (yang2021_amp0p6mm_ax8kN_r1) fechava com C_creep=3,733e-11
        # — rota REFUTADA pelo controle da fonte, porque as PROPRIAS REPLICAS
        # r2/r3 saem do tripe (licao D-I: fitar um membro contra as irmas).
        #
        # ⚠️ E a varredura ensinou a distincao que este numero depende: o
        # veredito "candidata a FORMA" e' AUSENCIA DE ROTA POR CONSTANTE, e nao
        # FORMA NOMEADA. Nomear a forma e' trabalho mais fundo (o que a sessao B
        # fez no ICMEZ). Por isso 15 vereditos "candidata a FORMA" acrescentam
        # ZERO a `_FORMA_NOMEADA` — e o (2) e' EXATO, nao piso.
        # ⚠️ NUMERO FIXO AQUI MENTE NA HORA (medido 2026-08-15 23:0x): a versao
        # anterior imprimia "'candidata a FORMA' (15 delas)", fixo da varredura
        # de 16 curvas. No instante em que 3 delas passaram para _FORMA_NOMEADA,
        # o 15 ficou errado ao lado de um "13" calculado ao vivo. So o FATO
        # HISTORICO da varredura e fixo (16 perguntadas, 0 com rota); o resto
        # se calcula.
        sem = sorted(c for c in abertas if c not in _FORMA_NOMEADA)
        print(f"  as outras {len(sem)} abertas — NOMEADAS com o motivo MEDIDO "
              f"(ausencia tem de ser visivel):")
        orfas = 0
        for c in sem:
            motivo = _SEM_FORMA_MOTIVO.get(c)
            if motivo is None:
                orfas += 1
                motivo = "*** SEM MOTIVO DECLARADO — ninguem mediu esta ***"
            print(f"        {c[:44]:44s} {motivo}")
        if orfas:
            # ASCII puro: este print SO e' alcancado quando ha orfas, e a 1a
            # vez que isso aconteceu (2026-08-23, retratacao das 2 provas de
            # piso do ECCLES) ele MATOU a triagem inteira com
            # UnicodeEncodeError no console cp1252 -- o instrumento de censo
            # parou de rodar por causa de um emoji num caminho raro. E o
            # gotcha "prints ASCII em scripts" do CLAUDE.md, e a licao extra e
            # que caminho de erro raro tem de ser ASCII **por construcao**:
            # ele so aparece no pior momento, quando algo ja deu errado.
            print(f"     [!] {orfas} sem motivo declarado: sao trabalho PENDENTE,")
            print(f"        nao resultado. Medir e declarar em _SEM_FORMA_MOTIVO.")
        print(f"     => 'sem forma nomeada' NAO e' o mesmo que 'ninguem olhou'.")
        print(f"       As com motivo acima FORAM medidas e o resultado foi que")
        print(f"       nao ha forma unica a nomear. Registro historico: das 16")
        print(f"       varridas em 97b82c5, ZERO tinham rota por constante livre")
        print(f"       — e 'candidata a FORMA' (o veredito daquela varredura) e")
        print(f"       AUSENCIA DE ROTA, nao forma nomeada.")

    print(f"\nFILA FORM-LIMITED - {len(fl)} curvas (o unico alvo legitimo)")
    print(f"  {'curva':34s} {'MAE':>7s} {'x':>5s} {'res.max':>7s} {'x':>5s} "
          f"{'sigma':>7s} {'x':>5s} {'red.sigma':>9s} {'piso':>7s}")
    need = []
    for cid, src, a, b, s, p in sorted(fl, key=lambda t: t[4]):
        # distancia ao limite QUE VALE para a fonte (nao ao global)
        red = max(0.0, 1.0 - (p or rh.META_SRES) / s)
        need.append(red)
        print(f"  {cid[:34]:34s} {a:7.4f} {a/rh.META_MAE:5.2f} {b:7.4f} "
              f"{b/rh.META_MAX:5.2f} {s:7.4f} {s/(p or rh.META_SRES):5.2f} "
              f"{100*red:8.0f}% {p or float('nan'):7.4f}")
    if need:
        need = np.array(need)
        print("\n  reducao de sigma_res necessaria:")
        for lim in (0.0, 0.05, 0.10, 0.20, 0.50):
            rot = "ja dentro" if lim == 0 else f"<= {100*lim:3.0f}%"
            print(f"    {rot:12s}: {int(np.sum(need <= lim + 1e-12)):2d} curvas")
        print(f"    mediana {100*np.median(need):.0f}%  -  maxima {100*need.max():.0f}%")
        print(f"  pernas violadas: MAE {sum(1 for c in fl if c[2] > rh.META_MAE)} - "
              f"res.max {sum(1 for c in fl if c[3] > rh.META_MAX)} · "
              f"sigma {sum(1 for c in fl if c[4] > (c[5] or rh.META_SRES))}")
        print("  por fonte: " + ", ".join(
            f"{s} x{n}" for s, n in Counter(c[1] for c in fl).most_common()))

    # efeito de cada camada da regra no numero publicado
    base = len(tripe) + len(cat.get("excecao_assinada", []))
    print(f"\nEFEITO DAS CAMADAS (de {len(tripe)+len(fora)} comparaveis):")
    acc = base
    print(f"  hoje (tripe + excecao assinada)          {acc:3d}")
    for k, rot in (("metric_limited_n_baixo", "declarar n<6"),
                   ("metric_limited_colapso", "declarar metric-limited colapso"),
                   ("data_limited_piso", "declarar data-limited por piso")):
        acc += len(cat.get(k, []))
        print(f"  + {rot:38s} {acc:3d}")
    print(f"  fila de forma que sobra                  {len(fl):3d}")
    print(f"  indecidivel (falta replica)              "
          f"{len(cat.get('indecidivel_sem_piso', [])):3d}")
    print("\n  ATENCAO: o numero maior le-se 'resolvidas OU declaradas com")
    print("  procedencia', NAO 'o modelo acerta'. A leitura estrita segue "
          f"{len(tripe)}.")

    if "--json" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--json") + 1])
        dest.write_text(json.dumps(
            {k: [c[0] for c in v] for k, v in cat.items()},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\ngravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
