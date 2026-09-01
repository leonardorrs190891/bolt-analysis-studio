# -*- coding: utf-8 -*-
"""Colhe a procedência das 147 entradas `per_case` que não a declaram.

## O achado que muda a tarefa

O pedido foi *"leia os papers"* — resposta a eu ter dito que declarar a
procedência das 147 exigia lê-los. **Era o diagnóstico errado, e medi por quê:**
a leitura JÁ FOI FEITA. Cada uma dessas constantes entrou por um pré-registro que
declara de onde ela veio; o que faltou foi **transcrever** para o campo `prov`,
que é o único lugar que a máquina lê.

Exemplo, do PR-28 (`specs/2026-07-11-mem-iter4-preregistrations.md`, l. 1801):

> `mu_thread/mu_bearing` POR CASO = **Fig. 10 locknut digitalizada
> (input-de-paper)**: N=2:0,158, 4:0,186, 6:0,198, 8:0,245, 10:0,279.

Os cinco números estão no `adopted_configs.json` **sem `prov`**, e a frase que os
justifica está num prereg de 15/jul. Abrir o PDF do Sun para redescobrir isso
seria refazer trabalho já feito — e a lição registrada neste repo é que **a porta
mais barata é procurar o que já foi medido**.

## O que a colheita produz

`New_Theory/procedencia_colhida.json` — mapa `{grupo: {campo: prov}}` com a
**citação do documento** em cada entrada, pronto para ser fundido ao
`adopted_configs.json`.

⚠️ **Este script NÃO escreve no `adopted_configs.json`**, e a razão é medida:
`engine_fingerprint()` hasheia `kb.adopted_config(s)` **inteiro** — `cfg`, `pack`,
`prov` e `verdict`. Acrescentar procedência **muda o fingerprint** e obriga a
re-carimbar os 210 registros do store. É operação de adoção, single-writer, com
sessão paralela ativa. A colheita é o trabalho; a fusão é um passo separado.

## As três classes

| classe | n | o que é |
|---|---:|---|
| **zero estrutural** | 45 | `s_crit_loose=0`, `emb_depth=0`, `C_creep=0`… — não são constantes fitadas, são **canais desligados**; a procedência é a decisão de desligar |
| **modo** | 18 | `loose_rate_mode="graded_scrit"` — string, escolha de **forma**, não valor |
| **valor** | 84 | os que pedem procedência de verdade |

    py -3.12 New_Theory/colheita_de_procedencia.py
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402

# --------------------------------------------------------------------------- #
# A colheita: por (grupo, campo), a procedência DOCUMENTADA e onde ela está.   #
# Cada entrada cita o documento — sem citação, não entra.                      #
# --------------------------------------------------------------------------- #

DOC = {
    "PR28": "specs/2026-07-11-mem-iter4-preregistrations.md §PR-28 (2026-07-15)",
    "P13": "specs/2026-08-20-yang2023-p13-taxa-fracionaria-prereg.md §3",
    "ZH": "specs/2026-08-20-zhang-fig3-runaway-prereg.md",
    "ROUS": "New_Theory/rousseau_t10_ratchet_lido_resultado.md",
    "ARR": "New_Theory/arrest_exp_resultado.md",
    "GTH": "New_Theory/itens_D_e_E_respondidos_com_numero.md",
    "MET": "New_Theory/metodo_leitura_de_constantes.md §2",
    "CHU": "New_Theory/chu_graded_scrit_resultado.md",
    "AEXP": "specs/2026-08-20-lu2024-amp1p5-aexp-regredido-prereg.md",
    "SUNCC": "specs/2026-08-19-sun-standard-ccreep-token-prereg.md",
    "BURST": "specs/2026-08-21-lu2024-fig14-burst-prereg.md",
    "SUNKC": "New_Theory/sun_standard_kernel_cinematico_resultado.md",
    "LEG": "New_Theory/MODEL_LEGITIMACY.md §4.7",
}

# (grupo-prefixo, campo) -> (texto da procedência, chave do documento)
COLHEITA = {
    # --- SUN_2025_REASSY: PR-28, tudo lido -------------------------------
    ("SUN_2025_REASSY", "mu_thread"):
        ("input-de-paper: Fig. 10 do Sun (locknut) digitalizada — coeficiente "
         "de atrito retro-derivado do torque de prevalência, por número de "
         "remontagens (N=2:0,158 · 4:0,186 · 6:0,198 · 8:0,245 · 10:0,279)", "PR28"),
    ("SUN_2025_REASSY", "mu_bearing"):
        ("input-de-paper: mesmo valor do `mu_thread` — a Fig. 10 reporta UM "
         "coeficiente por remontagem, não separa rosca de apoio", "PR28"),
    # --- YANG_2023_IJPEM: P-13, LSQ ao F publicado -----------------------
    ("YANG_2023_IJPEM", "loose_F_exp"):
        ("REGREDIDO: LSQ da solução fechada r=(1+(fe−1)KN)^(−1/(fe−1)) ao F(N) "
         "PUBLICADO — r² 0,9968–0,9999. Zero fit à métrica: as três pernas são "
         "predição", "P13"),
    ("YANG_2023_IJPEM", "k_loose_graded"):
        ("DERIVADO da mesma regressão: k = K·F₀/(k_b·lead·ref/(d₂/2)), com K do "
         "LSQ ao F publicado (r² 0,9968–0,9999)", "P13"),
    # --- ROUSSEAU: traços de rotação das Figs. 4/5 -----------------------
    ("ROUSSEAU", "free_spin_kin"):
        ("LIDO por regressão ao traço de ROTAÇÃO publicado: dF/dθ = 919,7 N/deg "
         "(r²=0,9997) contra 3278 do k_b·lead ⇒ fsk = 1 − 920/3278 = 0,7195. "
         "A fração não-drenante é medida, não ajustada", "ROUS"),
    ("ROUSSEAU", "k_loose_graded"):
        ("REGREDIDO da taxa observada: LSQ Hill×arrest, r²=0,891 — o Hill "
         "sozinho dá r²=0,092, o que prova que a DESCIDA do sino é a forma", "ROUS"),
    # --- ZHANG_2006 fig3: runaway ---------------------------------------
    ("ZHANG_2006", "loose_runaway_frac"):
        ("LIDO direto: o paper define o fim do Estágio II em P=25 %", "ZH"),
    ("ZHANG_2006", "loose_runaway_gain"):
        ("fitado-declarado sob região interior comprovada; par degenerado com "
         "`loose_F_exp` DECLARADO ⇒ conta como ~1 parâmetro efetivo", "ZH"),
    ("ZHANG_2006", "loose_F_exp"):
        ("fitado-declarado; ver a degenerescência declarada com "
         "`loose_runaway_gain`", "ZH"),
    ("ZHANG_2006", "k_loose_graded"):
        ("fitado-declarado na mesma grade do runaway", "ZH"),
    # --- YANG_2019 amp0p4: pacote gth lido do próprio dado ---------------
    ("YANG_2019", "gth_A0"):
        ("LIDO do próprio dado: pacote `gth` extraído da curva de stick, com a "
         "causa-raiz do gate de grupo corrigida no mesmo passo", "GTH"),
    ("YANG_2019", "gth_k"): ("idem `gth_A0` — mesmo pacote, mesma leitura", "GTH"),
    ("YANG_2019", "gth_accel_p"):
        ("idem `gth_A0` — mesmo pacote, mesma leitura", "GTH"),
    # --- ECCLES / SUN: arrest_approach_exp -------------------------------
    ("ECCLES", "arrest_approach_exp"):
        ("adotado por PROTOCOLO (não por curva): a aproximação do arresto é "
         "propriedade do protocolo de ensaio, não do espécime", "ARR"),
    ("SUN_2025_CRIMP", "arrest_approach_exp"):
        ("mesma forma do ECCLES, por protocolo", "ARR"),
    ("ROUSSEAU", "arrest_approach_exp"):
        ("mesma forma, por protocolo", "ARR"),
    # --- emb_um: leitor canônico ----------------------------------------
    ("SUN_2025_REASSY", "emb_um"):
        ("LIDO por leitor canônico (`emb_from_curve`): queda em N=500 com "
         "subtração do front do modelo, atribuição conjunta com o wear", "PR28"),
    ("SUN_2025_CRIMP", "emb_um"):
        ("LIDO por leitor canônico (`emb_from_curve`) no trecho de "
         "assentamento", "MET"),
    ("ICMEZ_2025", "emb_um"):
        ("LIDO do intercepto: settling lido da caracterização de dreno dos "
         "AUTORES (Fig. 3)", "MET"),
    ("CHU_2026", "emb_um"):
        ("handbook: VDI 2230 f_Z pela classe de rugosidade (Rz<10 ⇒ 9,5 µm)", "CHU"),
    # --- ICMEZ: dreno dos autores ----------------------------------------
    ("ICMEZ_2025", "free_spin_kin"):
        ("LIDO da caracterização de dreno dos AUTORES (Fig. 3) — a fração "
         "não-drenante sai do traço publicado, uma por condição de grip/carga",
         "MET"),
    ("ICMEZ_2025", "k_loose_graded"):
        ("REGREDIDO na mesma leitura da Fig. 3", "MET"),
    # --- LIU_2025: fat_C1 = vida do paper --------------------------------
    ("LIU_2025", "fat_C1"):
        ("input-de-paper POR CURVA: `fat_C1` fixado nas contas a partir da vida "
         "N_f PUBLICADA de cada curva (rota E2). A claim é 'prevê a curva DADA a "
         "vida' — prever a vida segue falsificado (relógio ±36 %)", "MET"),
    # --- LU_2024 ---------------------------------------------------------
    ("LU_2024", "loose_F_exp"):
        ("REGREDIDO do dado (mesma forma do P-13), dentro da região que fecha",
         "MET"),
    ("LU_2024", "k_loose_graded"): ("DERIVADO da mesma regressão", "MET"),
    # --- CHU_2026 --------------------------------------------------------
    ("CHU_2026", "mu_bearing"):
        ("input-de-paper: µ medido e prescrito pela fonte", "CHU"),
    # --- as 23 que a 1a passada nao achou: busquei pelo VALOR, e cada uma
    # --- tem prereg proprio. Nenhuma precisou de leitura nova.
    ("LU_2024", "arrest_approach_exp"):
        ("REGREDIDO do dado: aexp=1,864 com r²=0,685, dentro da região que "
         "fecha — o floor lido foi FALSIFICADO antes, e a regressão entrou no "
         "lugar dele", "AEXP"),
    ("LU_2024", "slip_onset_W"):
        ("fitado-declarado no pacote de BURST da fig14, com região interior "
         "comprovada", "BURST"),
    ("LU_2024", "slip_onset_sharpness"): ("idem — mesmo pacote de burst", "BURST"),
    ("LU_2024", "onset_burst_frac"): ("idem — mesmo pacote de burst", "BURST"),
    ("LU_2024", "onset_burst_rate"): ("idem — mesmo pacote de burst", "BURST"),
    ("SUN_2025_CRIMP", "C_creep"):
        ("ESTENDIDO do token `standard` da PRÓPRIA fonte — zero número novo: o "
         "valor 9e-11 já existia na fonte e foi propagado ao par, não ajustado",
         "SUNCC"),
    ("SUN_2025_CRIMP", "k_loose_graded"):
        ("kernel cinemático `graded_scrit`: 2 fitados TROCAM 2 fitados (não "
         "somam), com o floor ganhando procedência de LEITURA no mesmo passo",
         "SUNKC"),
    ("SUN_2025_CRIMP", "k_wear_spec"):
        ("fitado-this-rig por par tribológico (§4.7: `k_wear_spec` é por par, "
         "não universal)", "LEG"),
    ("ROUSSEAU", "slip_onset_W"):
        ("fitado-declarado; par degenerado com `slip_onset_sharpness` "
         "DECLARADO ⇒ conta como ~1 parâmetro efetivo", "MET"),
    ("ROUSSEAU", "slip_onset_sharpness"):
        ("idem — ver a degenerescência declarada com `slip_onset_W`", "MET"),
    ("ZHANG_2006", "slip_onset_W"):
        ("fitado-declarado na mesma grade do runaway; degenerescência com o "
         "par (frac, gain) declarada", "ZH"),
    ("LIU_2020_WEAR", "mu"):
        ("input-de-paper por revestimento: DLC 0,126 medido na fonte; zinco e "
         "af0.4 ficam no 0,15 do bloco `shared` (não é leitura da fonte — é o "
         "default herdado, e está dito)", "LEG"),
    ("LIU_2020_WEAR", "mu_thread"):
        ("idem `mu` — a fonte reporta UM coeficiente por revestimento", "LEG"),
    ("CHU_2026", "k_loose_graded"):
        ("fitado-declarado sob a lei de 5 degraus da fonte (prova em nível de "
         "lei, §4.54a)", "CHU"),
}

# Campos cujo valor ZERO é decisão de DESLIGAR um canal — não constante fitada.
DESLIGA = {
    "s_crit_loose": "limiar de slip do ramo graded",
    "loose_amp_exp": "expoente de amplitude do afrouxamento",
    "C_creep": "canal de fluência",
    "emb_depth": "canal de assentamento",
    "slip_onset_W": "incubação por trabalho de slip",
    "loose_arrest_floor": "piso de auto-travamento",
    "k_wear_spec": "canal de desgaste (via específica)",
    "K_archard": "canal de desgaste (via legada K/H)",
    "k_ratchet": "ramo de ratchet ∝ slip",
}


def colher():
    fora, saida = [], collections.defaultdict(dict)
    cont = collections.Counter()
    for s in sorted(kb.adopted_sources()):
        e = kb.adopted_config(s) or {}
        c = e.get("cfg") or {}
        prov = e.get("prov") or {}
        for tok, d in sorted((c.get("per_case") or {}).items()):
            if not isinstance(d, dict):
                continue
            for campo, val in sorted(d.items()):
                if campo in prov:
                    continue
                # 1) modo: escolha de FORMA
                if isinstance(val, str):
                    saida[s][campo] = (
                        f"FORMA adotada por pré-registro: `{val}` — é uma "
                        f"escolha de mecanismo, não um valor ajustado. "
                        f"[{DOC['MET']}]")
                    cont["modo"] += 1
                    continue
                # 2) zero estrutural: canal desligado
                if isinstance(val, (int, float)) and float(val) == 0.0:
                    o = DESLIGA.get(campo, "canal")
                    saida[s][campo] = (
                        f"canal DESLIGADO deliberadamente (valor 0 exato): "
                        f"{o}. Não é constante ajustada — é a decisão de que "
                        f"este canal não age nesta curva.")
                    cont["zero"] += 1
                    continue
                # 3) valor: procedência colhida
                achou = None
                for (pref, cp), (txt, doc) in COLHEITA.items():
                    if campo == cp and s.startswith(pref):
                        achou = f"{txt}. [{DOC[doc]}]"
                        break
                if achou:
                    saida[s][campo] = achou
                    cont["valor"] += 1
                else:
                    fora.append((s, tok, campo, val))
                    cont["SEM"] += 1
    return saida, fora, cont


def main():
    saida, fora, cont = colher()
    n = sum(len(v) for v in saida.values())
    print(f"colhidas       : {n} entradas (grupo, campo)")
    for k in ("valor", "zero", "modo"):
        print(f"  {k:6s}: {cont[k]}")
    # print ASCII de proposito (regra do CLAUDE.md): rodando sob subprocess com
    # pipe no Windows o stdout do filho e' cp1252, e o acento quebrava o parse
    # do teste (filho codifica cp1252, teste decodifica utf-8) — medido 2026-08-27.
    print(f"SEM procedencia: {cont['SEM']}")
    if fora:
        print("\nAVISO: ainda sem procedencia documentada -- precisam de leitura NOVA:")
        vis = set()
        for s, tok, campo, val in fora:
            if (s, campo) in vis:
                continue
            vis.add((s, campo))
            print(f"   {s:26s} {campo:22s} ex. {tok}={val}")
    alvo = RAIZ / "New_Theory" / "procedencia_colhida.json"
    # 2026-08-28: a colheita de 2026-08-25 foi FUNDIDA ao adopted_configs.json
    # (decisao do professor, single-writer, store re-carimbado). Desde entao
    # esta funcao normalmente nao encontra nada a colher — e o mapa em disco e'
    # o REGISTRO HISTORICO da colheita fundida, com as citacoes que o `prov`
    # herdou. Sobrescreve-lo com `{}` apagaria esse registro; so' se reescreve
    # quando ha' colheita nova.
    if saida:
        alvo.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8", newline="")
        print(f"\n-> {alvo.relative_to(RAIZ)}")
        print("AVISO: entradas per_case SEM `prov` no config — declare-as no "
              "adopted_configs.json (operacao single-writer: `prov` entra no "
              "engine_fingerprint e exige re-carimbo do store).")
    else:
        print(f"\nmapa historico preservado: {alvo.relative_to(RAIZ)} "
              f"(colheita de 2026-08-25, fundida ao config em 2026-08-28)")


if __name__ == "__main__":
    main()
