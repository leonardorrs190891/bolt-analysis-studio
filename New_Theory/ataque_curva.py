# -*- coding: utf-8 -*-
"""SHELL DE ATAQUE a uma curva — diagnostico + alavancas + veredito, num comando.

    py -3.12 New_Theory/ataque_curva.py <case_id> [--doses] [--json out.json]

## Por que existe

Atacar uma curva a mao repete sempre os mesmos 5 passos, e eu errei 3 deles
nesta campanha em 2026-08-09. Este script os executa na ordem certa e com os
guardas que cada erro ensinou:

1. **DIAGNOSTICO** — as 3 pernas contra os limites VIGENTES (`rh.limite_sres`,
   nunca reimplementado), o sinal do vies e a forma do residuo por terco.
2. **ONDE o erro se forma** — o maior salto de residuo. Erro que chega pronto ao
   fim nao se conserta mexendo no fim.
3. **CAPACIDADE, nao fatia** ⚠️ — para cada mecanismo, a fatia do incremento E o
   valor ABSOLUTO. Uma forma sobre um canal que move 0,004 de pre-carga nao pode
   fechar um deficit de 3 % (licao do wear saturante, `CLAUDE.md`).
4. **PROCEDENCIA** — cada alavanca e' marcada LIVRE ou TRAVADA lendo o `prov` do
   `adopted_configs.json`. Constante com procedencia nao se move para fechar
   metrica (licao da fig7c).
5. **SONDA de 2 pontos** por alavanca LIVRE, com o veredito por perna.

## O que ele NAO faz

Nao adota, nao escreve config nem store. O que ele produz e' insumo de prereg.

⚠️ Grade que devolve resultado IDENTICO ao digito = INERCIA, nao robustez — o
script marca isso explicitamente (`= nominal`), porque ler empate como
"parametro robusto" ja custou uma sessao inteira a esta campanha.

⚠️ E o SINTOMA GEMEO: mudanca CATASTROFICA numa curva que estava boa tambem e'
teste invalido, nao falsificacao (medido 2026-08-09 no JCSR — uma curva de
0,0009/0,0021/0,0010 virou 0,22/0,34/0,096 porque eu passara nome de campo
inexistente E um t_0 errado que inflou o fator 48x). O script marca `EXPLODIU`
quando uma dose piora o MAE em mais de 5x, para que isso nao seja lido como
resultado.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn                  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (          # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult        # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
CFG = ROOT / "New_Theory" / "adopted_configs.json"
MEC = ("embedding", "creep", "wear", "rotational_loosening",
       "thread_fretting", "fatigue")

# alavanca -> (doses, mecanismo que ela governa)
_DOSES = {
    "C_creep":            ("mult", (0.5, 0.75, 1.5, 2.0), "creep"),
    "creep_conform_exp":  ("abs", (0.0, 0.5, 1.5), "creep"),
    # ⚠️ ERA `t_0_creep` ATE 2026-08-21 — campo que NAO EXISTE em JointMaterial
    # (o campo e `t_0`). A injecao era filtrada em silencio por
    # `__dataclass_fields__` em `material_kwargs_for`, entao a dose era NO-OP e o
    # shell reportava "= nominal (INERTE)" — que e' exatamente o que o docstring
    # deste arquivo adverte NAO confundir com "o parametro nao faz nada": era o
    # instrumento nao alcancando o parametro. Mesmo erro que o CLAUDE.md ja
    # registra ("`t_0_creep` em vez de `t_0`, o que inflou o fator a 48x"), agora
    # do lado da TABELA DE DOSES em vez do lado da sonda ad-hoc.
    # A guarda estrutural logo abaixo impede a reincidencia.
    "t_0":                ("mult", (0.3, 3.0), "creep"),
    "N_emb":              ("mult", (0.5, 0.7, 1.5, 2.0), "embedding"),
    "emb_depth":          ("mult", (0.7, 1.3), "embedding"),
    "k_wear_spec":        ("mult", (0.3, 3.0), "wear"),
    # ⚠️ K_archard ENTROU EM 2026-08-21 — sem ele o canal de wear era
    # INSONDAVEL em toda fonte que usa a via LEGADA K/H, e essas existem.
    # O `k_wear_spec` acima e' dose MULTIPLICATIVA, e multiplicar ZERO da
    # ZERO: onde o cfg zera `k_wear_spec` (idioma `k_wear_scale_tr=0.0` via
    # tuner_shim, hoje o `LIU_2025`), o engine cai na via legada K/H com
    # `K_archard`/`hardness` nos DEFAULTS (1e-4 / 2e9 => K/H = 5e-14, o valor
    # canonico) e o canal RODA — na `liu2025_M16_amp0p8` ele carrega 0,286 da
    # perda e 47 % do incremento tardio.
    # Custo real medido: o veredito "NENHUMA alavanca livre fecha" daquela
    # curva — a UNICA da fila form-limited do projeto — foi dado sem que o
    # canal dominante fosse sondado uma vez. Ele SOBREVIVEU a sonda (o nominal
    # 1e-4 e otimo INTERIOR nas 3 pernas: 0,79x/0,86x/1,68x contra 0,94/0,85/
    # 2,05 em 1,5e-4 e 1,30/1,21/2,91 em 7e-5), mas isso passou a ser MEDIDO em
    # vez de assumido — e o proximo caso pode nao sobreviver.
    # Nota de identificabilidade: K_archard e hardness sao NAO-identificaveis em
    # separado (so a razao K/H entra na lei), logo dosar K_archard e dosar K/H.
    "K_archard":          ("mult", (0.5, 0.7, 1.5, 2.0), "wear"),
    "tr_loose_gain":      ("mult", (0.7, 1.3), "rotational_loosening"),
    "loose_arrest_floor": ("delta", (-0.02, +0.02), "rotational_loosening"),
    "arrest_approach_exp": ("abs", (1.5, 2.0), "rotational_loosening"),
}

# GUARDA ESTRUTURAL (2026-08-21) — alavanca que nao e campo de `JointMaterial` e
# NO-OP SILENCIOSO: `material_kwargs_for` filtra por `__dataclass_fields__`, a
# dose nao chega ao engine, e o shell reporta "= nominal (INERTE)". O leitor
# entende "o parametro nao faz nada" quando o fato e "o instrumento nao alcanca o
# parametro" — a distincao que o docstring deste arquivo faz questao de marcar.
# Foi assim que `t_0_creep` (campo inexistente; o certo e `t_0`) ficou na tabela
# dosando o vazio, e o CLAUDE.md ja registrava a MESMA troca de nome como erro
# pago numa sonda ad-hoc. Falhar no import e' o unico jeito de nao repetir: o
# defeito nao produz excecao nem numero errado, produz um veredito TRANQUILO.
def _valida_doses() -> None:
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial as _JMv)
    orfas = sorted(k for k in _DOSES if k not in _JMv.__dataclass_fields__)
    if orfas:
        raise SystemExit(
            "ataque_curva: alavanca(s) em _DOSES que NAO sao campos de "
            "JointMaterial: %s\nA dose seria filtrada em silencio por "
            "material_kwargs_for e o shell reportaria INERTE. Corrija o NOME "
            "(ex.: t_0, nao t_0_creep) ou remova a entrada." % orfas)


_valida_doses()


# NIVEL x FORMA por canal — o par que a varredura MARGINAL nao sabe separar.
# `nivel` fixa QUANTO o canal perde no limite; `formas`, QUANDO essa perda
# chega. Dentro da janela de um ensaio os dois se confundem, entao varrer um
# com o outro errado devolve um otimo CONDICIONAL — foi assim que eu declarei
# "C_creep no otimo" no JCSR um dia antes de a conjunta fechar a curva (D-AA).
_PARES_ACOPLADOS = {
    # creep e' o caso limpo: delta_sat = C_creep*F_0*(1-e^{-(t/t_c)^alpha}).
    "creep": ("C_creep", ("creep_t_c", "creep_alpha_sat")),
    # embedding: emb_depth e' a profundidade final; N_emb, o relogio.
    "embedding": ("emb_depth", ("N_emb",)),
    # rotacional: tr_loose_gain e' o ganho; o piso/expoente de arresto dizem
    # onde a perda para.
    "rotational_loosening": ("tr_loose_gain",
                             ("loose_arrest_floor", "arrest_approach_exp")),
    # wear NAO entra: Archard e' LINEAR no coeficiente (dV = K/H*F*s), entao o
    # canal nao tem constante de forma propria para acoplar — mexer em
    # `k_wear_spec` escala a curva inteira e ponto. Nao e' lacuna do registro,
    # e' propriedade da lei. (Verificado contra `JointMaterial`: nao existe
    # nenhum expoente de amplitude do wear transversal; `flank_amp_exp` e
    # `fret_freq_exp` sao do canal de FLANCO, que e' outro mecanismo.)
}


def _prov_travada(fonte: str, alavanca: str):
    """A constante tem procedencia registrada? Devolve (travada?, texto)."""
    try:
        J = json.loads(CFG.read_text(encoding="utf-8"))["sources"]
    except Exception:
        return False, ""
    for k, e in J.items():
        if not k.startswith(fonte):
            continue
        pv = (e.get("prov") or {}).get(alavanca)
        if pv:
            txt = str(pv)
            # "lido-do-dado", "input", "handbook", "assinado" => TRAVADA.
            # "fitado" => livre (ja e' um numero de ajuste deste rig).
            travada = any(t in txt.lower() for t in
                          ("lido-do-dado", "lido de", "input", "handbook",
                           "assinad", "norma", "tabela", "paper"))
            return travada and "fitado" not in txt.lower()[:24], txt
    return False, ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("case_id")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    cid = a.case_id
    if cid not in S or cid not in recs:
        print("curva desconhecida: %s" % cid)
        return 2
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])
    fonte = recs[cid].source
    r0 = res[cid]
    L = rh.limite_sres(fonte, pisos)
    sd0 = rh.sres_para_censo(r0)

    # ---------- 1. diagnostico ----------
    print("=" * 74)
    print("ATAQUE A %s   (%s)" % (cid, fonte))
    print("=" * 74)
    print("\n1. DIAGNOSTICO — pernas contra os limites VIGENTES")
    for nome, val, lim in (("MAE", r0.mae, rh.META_MAE),
                           ("res.max", r0.maxerr, rh.META_MAX),
                           ("sigma_res", r0.resid_std, L)):
        m = val / lim
        print("   %-10s %8.4f  limite %.4f   %5.2fx   %s"
              % (nome, val, lim, m, "VIOLA" if m > 1 else "ok"))
    manda = rh._perna_manda(r0.mae, r0.maxerr, sd0, rh.META_MAE, rh.META_MAX, L)
    print("   perna que MANDA: %s" % (manda or "nenhuma (passa)"))

    x = np.asarray(r0.metric_x, float)
    p = np.asarray(r0.metric_pred, float)
    d = np.asarray(r0.metric_data, float)
    resid = p - d
    t3 = [float(np.mean(z)) for z in np.array_split(resid, 3)]
    troca = max(t3) > 0 > min(t3)
    print("   vies %+.4f · residuo por terco %+.4f %+.4f %+.4f · troca de sinal: %s"
          % (float(np.mean(resid)), *t3, "SIM" if troca else "nao"))
    if troca:
        print("   sub-classe de curvatura: %s"
              % ("A (rapido cedo, devagar tarde)" if t3[2] > t3[0]
                 else "B (devagar cedo, rapido tarde)"))
    # |vies|/MAE: diagnostico GRATIS de nivel-vs-forma. 1,00 = TODO ponto do
    # residuo do mesmo lado => o erro e' um offset uniforme (a forma esta
    # certa, so a constante de NIVEL do canal esta errada); 0,00 = residuo
    # simetrico em torno de zero => puro erro de forma. Instalado depois do
    # D-AA (2026-08-09), onde a `galv` do JCSR foi de 0,00 para 1,00 ao trocar
    # a forma — e foi exatamente esse 1,00 que denunciou que a alavanca de
    # nivel, antes declarada "no otimo", ainda tinha o que dar.
    # ⚠️ |vies|/MAE e' AMBIGUO entre OFFSET e RAMPA (medido 2026-08-10 no
    # YANG_2021, e o ambiguo me fez propor alavanca de NIVEL para um deficit de
    # TAXA): residuo de sinal unico da 1,00 tanto quando e' um degrau uniforme
    # quanto quando cresce de ~0 ate o fim. O discriminante e' a CORRELACAO do
    # residuo com N (Spearman sobre a janela da metrica):
    #   |rho| ~ 0  -> offset (nivel)      |rho| ~ 1 -> rampa (taxa)
    def _rho(a, b):
        if len(a) < 4:
            return float("nan")
        ra = np.argsort(np.argsort(np.asarray(a, float)))
        rb = np.argsort(np.argsort(np.asarray(b, float)))
        sa, sb = ra.std(), rb.std()
        if sa < 1e-12 or sb < 1e-12:
            return float("nan")
        return float(((ra - ra.mean()) * (rb - rb.mean())).mean() / (sa * sb))
    rho = _rho(x, resid)
    vmae = abs(float(np.mean(resid))) / max(r0.mae, 1e-12)
    print("   rho(residuo, N) %+.2f  -> %s" % (
        rho,
        "RAMPA: deficit de TAXA -- o erro se ACUMULA, e alavanca de nivel nao "
        "conserta (ela desloca em bloco)" if abs(rho) >= 0.7 else
        ("OFFSET: erro de nivel uniforme" if abs(rho) <= 0.3 else "misto")))
    print("   |vies|/MAE %.2f  -> %s" % (
        vmae,
        "residuo de SINAL UNICO -- leia junto com o rho acima: offset pede "
        "constante de nivel, RAMPA pede taxa" if vmae >= 0.80 else
        ("erro de FORMA puro (residuo simetrico): a constante de nivel nao "
         "resolve" if vmae <= 0.20 else "misto nivel+forma: varra os DOIS JUNTOS")))

    # ---------- 2. onde o erro se forma ----------
    print("\n2. ONDE o erro se forma")
    dif = np.abs(np.diff(resid))
    j = int(np.argmax(dif))
    u = (x[j] - x[0]) / max(x[-1] - x[0], 1e-9)
    print("   maior salto entre ciclos %.0f e %.0f  (delta %+.4f, u=%.2f)"
          % (x[j], x[j + 1], resid[j + 1] - resid[j], u))
    print("   %s" % ("erro se forma CEDO — mexer no fim nao adianta" if u < 0.35
                     else "erro se forma no MEIO/FIM"))

    # ---------- 3. capacidade, nao fatia ----------
    print("\n3. CAPACIDADE dos canais (fatia E valor ABSOLUTO)")
    dec = r0.decomp or {}
    A = {k: np.asarray(dec.get(k, []), float) for k in MEC}
    n = len(next((v for v in A.values() if len(v)), [1]))
    cap = {}
    if n >= 6:
        i2 = 2 * n // 3
        inc_t = {k: abs(float(v[n - 1]) - float(v[i2])) for k, v in A.items() if len(v) == n}
        tot_t = sum(inc_t.values()) or 1e-12
        tot_g = {k: abs(float(v[n - 1]) - float(v[0])) for k, v in A.items() if len(v) == n}
        print("   %-22s %9s %11s %11s" % ("mecanismo", "fatia tarde", "ABS tarde", "ABS total"))
        for k in MEC:
            if k not in inc_t or tot_g.get(k, 0) <= 0:
                continue
            cap[k] = tot_g[k]
            print("   %-22s %8.0f%% %11.5f %11.5f"
                  % (k, 100 * inc_t[k] / tot_t, inc_t[k], tot_g[k]))
        print("   incremento tardio TOTAL: %.5f  %s" % (
            tot_t, "<<< pequeno: forma sobre o fim NAO move a curva" if tot_t < 0.02 else ""))

    # ---------- 4/5. alavancas: procedencia + sonda ----------
    print("\n4/5. ALAVANCAS — procedencia e sonda de 2 pontos")
    # ⚠️ A BASE TEM DE SER A REAL (`frozen_constants`), NAO `{}` — consertado
    # 2026-08-21. Com base vazia o `tuner_shim` decide o ROTEAMENTO errado: ele
    # so' manda `k_wear_scale_tr` para `k_wear_spec` se `k_wear_spec` estiver
    # ATIVO na base, e com `{}` ele nao esta ⇒ o valor 0,0 vai para
    # `K_archard`. Resultado: `ov0["K_archard"] = 0.0`, o probe pula a alavanca
    # por "base e' 0", e o canal fica INSONDAVEL. Na execucao real
    # (`simulate_case` chama `_effective_overrides(rec, consts)` com
    # `consts, _ = frozen_constants()`), `k_wear_spec` = 5e-14 esta ativo, o
    # roteamento vai para `k_wear_spec=0` e `K_archard` FICA no default 1e-4 —
    # com o canal rodando. Medido na `liu2025_M16_amp0p8`: wear carrega 0,286
    # da perda e 47 % do incremento tardio, e o veredito "NENHUMA alavanca livre
    # fecha" saiu sem que ele fosse sondado uma vez.
    # ⚠️ O comentario logo abaixo existe porque ler SO' do override "apagava em
    # SILENCIO toda alavanca parada no default". A correcao estava escrita — e
    # foi derrotada por alimentar a funcao com a base errada. Guarda contra
    # apagamento silencioso tambem precisa de entrada certa.
    _consts0, _ = rn.frozen_constants()
    ov0 = rn._effective_overrides(record(cid), _consts0)
    # BASE EFETIVA: override se houver, senao o valor que o material de fato
    # recebe. Ler so do override apagava em SILENCIO toda alavanca parada no
    # default de `JointMaterial` -- o `N_emb` (=50) nunca foi sondado em curva
    # nenhuma cujo cfg nao o declare, e o `tr_loose_gain` (=2) idem. Defeito
    # medido em 2026-08-09: a sonda dizia "candidata a FORMA" sem ter tocado
    # metade das constantes do canal.
    try:
        from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer             import JointMaterial as _JM
        _mat = _JM(**rn.material_kwargs_for(
            record(cid), rn.inputs_for(record(cid).validation_case)))
    except Exception:
        _mat = None

    def _base(n):
        v = ov0.get(n)
        if v is not None:
            return float(v)
        return getattr(_mat, n, None) if _mat is not None else None

    # Constantes que o runner DERIVA de um input do cfg DEPOIS dos overrides:
    # injeta-las por override e' no-op silencioso. `emb_depth` vem de `emb_um`
    # (um->m) em `material_kwargs_for`, entao numa curva com `emb_um` no cfg a
    # sonda de `emb_depth` marca INERTE -- e isso NAO quer dizer "o parametro
    # nao faz nada", quer dizer "o instrumento nao alcanca este parametro".
    _nao_injetaveis = ({"emb_depth": "emb_um"}
                       if (r0.config_used or {}).get("emb_um") is not None else {})
    _E: dict = {}
    _o = rn._effective_overrides
    rn._effective_overrides = (lambda rec, b:
                               {**_o(rec, b), **_E} if _E and rec.case_id == cid
                               else _o(rec, b))
    linhas = []
    print("   %-20s %-8s %9s %8s %8s %9s %s"
          % ("alavanca", "prov", "dose", "MAE", "res.max", "sigma", "veredito"))
    try:
        for alav, (modo, doses, mec) in _DOSES.items():
            if cap and cap.get(mec, 0.0) <= 1e-6:
                print("   %-20s %-8s %9s   canal com capacidade ~0 — PULADO"
                      % (alav, "-", "-"))
                continue
            trav, txt = _prov_travada(fonte, alav)
            base = _base(alav)
            for dz in doses:
                if modo == "mult":
                    if base in (None, 0):
                        continue
                    val = float(base) * dz
                elif modo == "delta":
                    if base is None:
                        continue
                    val = float(base) + dz
                else:
                    val = float(dz)
                _E.clear(); _E[alav] = val
                try:
                    r = rn.simulate_case(record(cid))
                except Exception as ex:
                    print("   %-20s %-8s %9.4g   ERRO %s" % (alav, "", val, str(ex)[:30]))
                    continue
                finally:
                    _E.clear()
                ident = (abs(r.mae - r0.mae) + abs(r.maxerr - r0.maxerr)
                         + abs(r.resid_std - r0.resid_std)) < 1e-12
                sd = rh.sres_para_censo(r)
                fecha = (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                         and sd is not None and sd <= L)
                explodiu = (r0.mae > 0 and r.mae > 5.0 * r0.mae)
                ver = ("= nominal (INERTE)" if ident else
                       ("EXPLODIU (%.0fx o MAE) — suspeite de TESTE INVALIDO"
                        % (r.mae / max(r0.mae, 1e-9)) if explodiu else
                        ("FECHA" if fecha else "sd %.2fx" % (r.resid_std / L))))
                if ident and alav in _nao_injetaveis:
                    # So aqui: a dose saiu IDENTICA ao nominal E existe um
                    # input do cfg do qual o runner deriva esta constante
                    # DEPOIS dos overrides. As duas coisas juntas -- nunca so
                    # a segunda: medido 2026-08-09, a `eccles fig7c` tem
                    # `emb_um` no cfg e mesmo assim `emb_depth` MOVE a curva,
                    # entao a presenca do input NAO implica no-op. O que
                    # decide e' a inercia; o input so nomeia o suspeito.
                    ver = ("inerte E derivavel de `%s` -- SUSPEITA de no-op do "
                           "injetor, nao conclua 'parametro morto' sem checar"
                           % _nao_injetaveis[alav])
                if trav and not ident:
                    ver += "  [PROV TRAVADA]"
                print("   %-20s %-8s %9.4g %8.4f %8.4f %9.4f  %s"
                      % (alav, "TRAVADA" if trav else "livre", val,
                         r.mae, r.maxerr, r.resid_std, ver))
                linhas.append(dict(alavanca=alav, prov_travada=trav, dose=val,
                                   mae=r.mae, maxerr=r.maxerr, sd=r.resid_std,
                                   fecha=bool(fecha), inerte=bool(ident),
                                   prov=txt[:200]))
    finally:
        rn._effective_overrides = _o

    ok = [l for l in linhas if l["fecha"] and not l["prov_travada"]]
    print("\nVEREDITO: %s" % (
        "fecha com %s = %.4g (prov LIVRE)" % (ok[0]["alavanca"], ok[0]["dose"])
        if ok else
        "NENHUMA alavanca livre fecha — candidata a FORMA, nao a constante"))
    if ok:
        # ⚠️ O veredito e' POR CURVA e nao sabe nada de CONTROLE DE FONTE — a
        # checagem que decide se a dose e' adotavel. Medido em 2026-08-21 na
        # `liu2025_M16_fig2_single`: o shell anunciou "fecha com C_creep =
        # 2.6e-11" com folga de 60 %, e o controle mostrou +1 / -5 (as 5 irmas
        # no tripe SAEM). E o padrao D-AB: a alavanca otima no ALVO pode ser
        # desastrosa para a FONTE, e a grade que fixou o valor vigente
        # normalmente ja o escolheu como otimo DE FONTE.
        # Sem esta linha, quem ler so' o veredito adota o que destroi as irmas.
        _b = ok[0]
        margem = min(1.0 - float(_b["mae"]) / rh.META_MAE,
                     1.0 - float(_b["maxerr"]) / rh.META_MAX,
                     1.0 - float(_b["sd"]) / L)
        print("   ⚠️ veredito POR CURVA. Antes de propor: (a) rode o CONTROLE DE "
              "FONTE (as irmas no tripe nao podem sair — precedente D-AB) e "
              "(b) confira a MARGEM.")
        print("   folga na perna mais apertada desta dose: %.1f%%%s"
              % (100.0 * margem,
                 "  <== FOLGA ~ZERO: o precedente ECCLES rebaixou veredito por "
                 "margem desta ordem" if margem < 0.05 else ""))
    trav_ok = [l for l in linhas if l["fecha"] and l["prov_travada"]]
    if trav_ok:
        print("   ⚠️ fecharia com %s, mas a procedencia esta TRAVADA: %s"
              % (trav_ok[0]["alavanca"], trav_ok[0]["prov"][:110]))

    # ---------- 6. varredura CONJUNTA nivel x forma do canal dominante ----------
    # Instalada depois do D-AA. O passo 4/5 acima e' MARGINAL, e varredura
    # marginal encontra otimo CONDICIONAL: no JCSR ela declarou "C_creep no
    # otimo" e a conjunta, na MESMA curva, achou uma regiao que fecha o tripe.
    # Nivel e forma de um mesmo canal sao acoplados por construcao (o creep e'
    # o caso limpo: assintota = C_creep, chegada = alpha/t_c), entao sondar um
    # com o outro no valor errado responde a pergunta errada.
    conj = []
    if cap:
        dom = max(cap, key=cap.get)
        par = _PARES_ACOPLADOS.get(dom)
        print("\n6. CONJUNTA nivel x forma — canal dominante: %s" % dom)
        if not par:
            print("   sem par nivel/forma registrado para este canal — PULADO")
        else:
            niv, formas = par
            b_niv = _base(niv)
            if b_niv in (None, 0):
                print("   nivel `%s` ausente/zero no material efetivo — PULADO" % niv)
            else:
                tn, _ = _prov_travada(fonte, niv)
                print("   nivel `%s`=%.5g (%s) x forma %s"
                      % (niv, float(b_niv), "TRAVADA" if tn else "livre",
                         " x ".join("`%s`" % f for f in formas)))
                bases = {f: _base(f) for f in formas}
                mortas = [f for f in formas if bases.get(f) in (None, 0)]
                vivas = [f for f in formas if f not in mortas]
                if mortas:
                    print("   forma(s) inertes a fator multiplicativo (base 0/ausente): %s"
                          % ", ".join("`%s`" % f for f in mortas))
                if not vivas:
                    print("   nenhuma forma viva — o par nao e' sondavel nesta curva")
                    formas = []
                grade = [(fn, fv) for fn in (0.6, 0.8, 1.0, 1.25, 1.6)
                         for fv in (0.5, 0.7, 1.0, 1.4, 2.0)]
                _E.clear()
                rn._effective_overrides = (lambda rec, b:
                                           {**_o(rec, b), **_E}
                                           if _E and rec.case_id == cid else _o(rec, b))
                try:
                    for fn, fv in grade:
                        ov = {niv: float(b_niv) * fn}
                        for f in formas:
                            if bases.get(f) in (None, 0):
                                continue
                            ov[f] = float(bases[f]) * fv
                        if len(ov) == 1:          # nenhuma forma existe no cfg
                            continue
                        _E.clear(); _E.update(ov)
                        try:
                            r = rn.simulate_case(record(cid))
                        except Exception:
                            continue
                        finally:
                            _E.clear()
                        sd = rh.sres_para_censo(r)
                        pior = max(r.mae / rh.META_MAE, r.maxerr / rh.META_MAX,
                                   (sd if sd is not None else 9.9) / L)
                        conj.append(dict(nivel_x=fn, forma_x=fv, mae=r.mae,
                                         maxerr=r.maxerr, sd=r.resid_std,
                                         pior=pior, fecha=bool(pior <= 1.0),
                                         nivel_travado=bool(tn)))
                finally:
                    rn._effective_overrides = _o
                fech = [c for c in conj if c["fecha"]]
                print("   %d celulas, %d FECHAM" % (len(conj), len(fech)))
                if conj:
                    for c in sorted(conj, key=lambda z: z["pior"])[:5]:
                        print("     nivel x%.2f forma x%.2f  %.4f/%.4f/%.4f  pior %.2fx %s"
                              % (c["nivel_x"], c["forma_x"], c["mae"], c["maxerr"],
                                 c["sd"], c["pior"], "FECHA" if c["fecha"] else ""))
                if fech:
                    nx = sorted({c["nivel_x"] for c in fech})
                    fx = sorted({c["forma_x"] for c in fech})
                    borda = (min(nx) == 0.6 or max(nx) == 1.6
                             or min(fx) == 0.5 or max(fx) == 2.0)
                    print("   regiao: nivel x%s · forma x%s   %s"
                          % (nx, fx,
                             "⚠️ NA FRONTEIRA — estenda a grade antes de propor "
                             "(disciplina D-L)" if borda else "INTERIOR"))
                    if tn:
                        print("   ⚠️ o nivel tem PROCEDENCIA TRAVADA: a regiao existe, "
                              "mas mover o nivel exige assinatura, nao ajuste")
                elif conj:
                    print("   nenhuma celula fecha — o par nivel x forma NAO e' a rota")

    if a.json:
        a.json.write_text(json.dumps(dict(case_id=cid, fonte=fonte,
                                          limite_sres=L, linhas=linhas),
                                     indent=1, default=float), encoding="utf-8")
        print("json -> %s" % a.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
