"""MATRIZ DE PROCEDÊNCIA POR CONSTANTE — o objetivo declarado da Fase 2.

A Fase 1 fechou com o veredicto "formas/acoplamentos transferem cross-rig,
constantes não" (`MODEL_LEGITIMACY.md` §8), e a Fase 2 foi enunciada como
**"prover procedência por constante"**. O que faltava era o número: *das
constantes que o canônico de fato usa, quantas têm procedência, e de que tipo?*

Este script mede isso contra a UNIÃO da maquinaria de procedência do KB — não
contra um acessador só:

  kb.anchor_verdicts()   164 entradas (âncora + veredicto + nota)
  kb.anchor_priors()       7 bandas medidas com valor/banda/fonte
  kb.checkable_inputs()    7 nomes onde a guarda `check_input` de fato roda
  kb.wear_spec_anchor()    bandas de k_wear_spec por interface|par (R5)

SÓ-LEITURA: nada de simulação, fit, adoção ou escrita no store. Lê apenas o
bloco `shared` de `joint_calibrations.json` (o canônico) e o KB.

**Escopo declarado, e por quê:** a matriz cobre as constantes do bloco
`shared` — as COMPARTILHADAS, que a tese "uma física, N estados" põe em jogo.
Os configs adotados per-rig ficam FORA de propósito: (a) são por-rig por
construção, então "procedência universal" não se aplica a eles do mesmo modo;
e (b) `New_Theory/adopted_configs.json` estava sendo escrito por uma sessão
paralela quando isto rodou — medir um arquivo em escrita daria número torto.

Run:  py -3.12 New_Theory/provenance_matrix.py
Saída: New_Theory/provenance_matrix.json + .md


AS CLASSES DE PROCEDÊNCIA (declaradas antes de medir)
=====================================================

| classe | significado | o que a move |
|---|---|---|
| `BANDA_DENTRO`   | banda MEDIDA existe e o valor canônico está dentro | nada — está provado |
| `BANDA_FORA`     | banda MEDIDA existe e o valor está FORA | re-ancorar ou separar a constante |
| `DIRECAO`        | a âncora confirma o SINAL/direção, não a magnitude | medição de magnitude |
| `INPUT_POR_JUNTA`| não é constante universal: é input de tabela por junta | nada — é input, e por decisão |
| `FIXO_POR_DECISAO`| valor congelado por decisão declarada, não fitado | reabrir a decisão |
| `FIT_SEM_ANCORA` | fitado ao dataset E sem âncora nenhuma | é a dívida mais cara |
| `SEM_PROCEDENCIA`| nenhuma âncora, nenhuma banda, nenhuma decisão registrada | medir ou anular |

As duas únicas atribuições NÃO derivadas do KB são citadas do registro
documental (não inferidas aqui):
  - `emb_depth` = INPUT_POR_JUNTA — VDI 2230 tabela f_Z por classe de Rz;
    "a PER-JOINT input, not a universal constant" (CLAUDE.md, gotchas do V2);
    o bloco `shared` o manteve como **input** por decisão do professor.
  - `p_ref_conform` = FIXO_POR_DECISAO — "n=2/p_ref=5e8 fixos" (CLAUDE.md,
    bloco `shared` rev. 2026-07-04).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402

SHARED = ROOT / "New_Theory" / "joint_calibrations.json"
OUT_JSON = ROOT / "New_Theory" / "provenance_matrix.json"
OUT_MD = ROOT / "New_Theory" / "provenance_matrix.md"

# atribuições vindas do registro documental (ver docstring)
_DOC = {"emb_depth": ("INPUT_POR_JUNTA",
                      "VDI 2230 tabela f_Z por classe de Rz; input por junta, "
                      "mantido como input por decisão (bloco shared 2026-07-04)"),
        "p_ref_conform": ("FIXO_POR_DECISAO",
                          "n=2 / p_ref=5e8 declarados FIXOS no bloco shared "
                          "(rev. 2026-07-04)")}
# unidade do k_wear_spec canônico — bandas em outra unidade NÃO são comparáveis
_KWS_UNIT = "1/Pa"


def _band_of(name, priors, verdicts):
    """Procedência de `name` na UNIÃO das fontes do KB.

    Consulta, nesta ordem: `anchor_priors` (nome exato ou vizinho — o prior do
    `C_creep` chama-se `C_creep_por_par`), `anchor_verdicts`, e — só para o
    `k_wear_spec` — a tabela `wear_spec` da R5, cujas bandas NÃO aparecem em
    nenhum dos dois primeiros.

    Reconhece três formatos de banda, e a 1a versao deste script só via o
    primeiro (por isso classificou `C_creep` e `k_wear_spec` errado):
      `banda_medida`/`band`  -> banda direta
      `faixa_per_rig`        -> faixa dos valores per-rig LIDOS (N_emb)
      `pares`                -> âncora POR PAR tribológico (C_creep)
    """
    if name == "k_wear_spec":
        ws = {k: v for k, v in kb._r5()["wear_spec"].items()
              if v.get("unit") == _KWS_UNIT}          # só o que é comparável
        if ws:
            # NUNCA usar a ENVOLTÓRIA [min(pisos), max(tetos)] para classificar:
            # ela engole o canônico e devolve BANDA_DENTRO, que é o OPOSTO da
            # verdade — o valor está fora das duas bandas, no vão entre elas.
            # (Erro cometido na 2a versao deste script e pego aqui.)
            return dict(fonte="wear_spec(R5)", chave=", ".join(sorted(ws)),
                        banda=None, verdict="BANDA-POR-INTERFACE",
                        ref="; ".join(sorted({v["source"] for v in ws.values()})),
                        nota="bandas POR INTERFACE — classificar banda a banda",
                        pares=None,
                        bandas={k: v["band"] for k, v in ws.items()})
    for src, d in (("anchor_priors", priors), ("anchor_verdicts", verdicts)):
        cand = [k for k in d if k == name or k.startswith(name + "_")]
        if not cand:
            continue
        ent, key = d[cand[0]], cand[0]
        return dict(fonte=src, chave=key,
                    banda=(ent.get("banda_medida") or ent.get("band")
                           or ent.get("faixa_per_rig")),
                    verdict=ent.get("verdict"),
                    ref=ent.get("fonte") or ent.get("anchor"),
                    nota=(ent.get("note") or ent.get("nota") or "")[:400],
                    pares=ent.get("pares"), por_interface=False)
    return None


def wear_bands():
    """Bandas de k_wear_spec por interface, com compatibilidade de UNIDADE.

    `fretting|52100-52100` está em `norm-own` (normalização do próprio paper),
    NÃO em 1/Pa — compará-la ao canônico é erro de unidade, e é por isso que
    esta função separa comparáveis de não-comparáveis em vez de listar as 3.
    """
    out = []
    for key, v in sorted(kb._r5()["wear_spec"].items()):
        out.append(dict(chave=key, banda=v.get("band"), unidade=v.get("unit"),
                        fonte=v.get("source"), provenance=v.get("provenance"),
                        comparavel=(v.get("unit") == _KWS_UNIT)))
    return out


def build():
    sh = json.loads(SHARED.read_text(encoding="utf-8"))["shared"]
    consts, free = sh["constants"], set(sh["free_constants"])
    priors, verdicts = kb.anchor_priors(), kb.anchor_verdicts()
    checkable = kb.checkable_inputs()

    rows = []
    for name, val in sorted(consts.items()):
        b = _band_of(name, priors, verdicts)
        chk = kb.check_input(name, val) if name in checkable else None
        row = dict(constante=name, valor=val, fitada=name in free,
                   checavel=name in checkable,
                   check_input=chk,
                   banda=(b or {}).get("banda"),
                   verdict_kb=(b or {}).get("verdict"),
                   ancora=(b or {}).get("ref"),
                   nota_kb=(b or {}).get("nota"))
        bb: dict = b or {}
        row["pares"] = bb.get("pares")
        banda = bb.get("banda")
        num_banda = (banda if isinstance(banda, (list, tuple)) and len(banda) == 2
                     and all(isinstance(x, (int, float)) for x in banda) else None)
        # ---- classificação, na ordem declarada
        if bb.get("verdict") == "input":
            row["classe"] = "INPUT_POR_JUNTA"
            row["porque"] = (f"o KB marca verdict='input' ({bb.get('nota')}) — "
                             "tabela por junta, não constante universal")
        elif name in _DOC:
            row["classe"], row["porque"] = _DOC[name]
        elif bb.get("bandas"):
            # banda POR INTERFACE: dentro se cair em ALGUMA delas, individualmente
            bds = bb["bandas"]
            row["bandas_por_interface"] = bds
            dentro_de = [k for k, (lo, hi) in bds.items()
                         if lo <= float(val) <= hi]
            row["classe"] = "BANDA_DENTRO" if dentro_de else "BANDA_FORA"
            if dentro_de:
                row["porque"] = f"dentro da banda {dentro_de[0]} ({bb.get('ref')})"
            else:
                det = []
                for k, (lo, hi) in sorted(bds.items(), key=lambda kv: kv[1][1]):
                    det.append(f"{k} [{lo:g},{hi:g}]: "
                               + (f"{float(val)/hi:.3g}x ACIMA" if float(val) > hi
                                  else f"{lo/float(val):.3g}x abaixo"))
                row["porque"] = ("FORA de TODAS as bandas comparáveis (1/Pa) — "
                                 + " · ".join(det)
                                 + ". O valor cai no VÃO entre elas; nenhum valor "
                                   "único pode satisfazer as duas (L6)")
        elif bb.get("pares"):
            pares = bb["pares"]
            match = [p for p, pv in pares.items()
                     if isinstance(pv, (int, float))
                     and abs(pv - float(val)) <= 1e-3 * abs(float(val))]
            row["classe"] = "ANCORA_POR_PAR"
            row["porque"] = (f"âncora POR PAR ({bb.get('ref')}): {len(pares)} pares; "
                             f"o canônico É o par "
                             f"{match[0] if match else '(nenhum — verificar)'}")
        elif num_banda:
            lo, hi = num_banda
            dentro = lo <= float(val) <= hi
            row["classe"] = "BANDA_DENTRO" if dentro else "BANDA_FORA"
            fora = ("" if dentro else
                    f", {float(val)/hi:.3g}x ACIMA do teto" if float(val) > hi
                    else f", {lo/float(val):.3g}x abaixo do piso")
            ref = bb.get("ref") or ("faixa per-rig LIDA do dado"
                                    if bb.get("chave", "").startswith("N_emb")
                                    else "sem fonte registrada no KB")
            row["porque"] = (f"banda medida [{lo:g}, {hi:g}] ({ref}); "
                             f"valor {'dentro' if dentro else 'FORA'}{fora}")
        elif bb.get("verdict") == "DIRECAO":
            row["classe"] = "DIRECAO"
            row["porque"] = f"âncora confirma a direção, não a magnitude ({bb.get('ref')})"
        elif name in free:
            row["classe"] = "FIT_SEM_ANCORA"
            row["porque"] = "está em free_constants e não tem banda nem âncora"
        else:
            row["classe"] = "SEM_PROCEDENCIA"
            row["porque"] = "nenhuma banda, âncora ou decisão registrada no KB"
        rows.append(row)

    # k_wear_spec: o caso que precisa da tabela de interfaces
    kws = float(consts["k_wear_spec"])
    wb = wear_bands()
    for b in wb:
        lo, hi = b["banda"]
        b["dentro"] = bool(b["comparavel"] and lo <= kws <= hi)
        b["razao"] = (None if not b["comparavel"] else
                      round(kws / hi, 4) if kws > hi else round(lo / kws, 4))
        b["lado"] = (None if not b["comparavel"] else
                     "ACIMA do teto" if kws > hi else
                     "abaixo do piso" if kws < lo else "dentro")
    return rows, wb, kws, sh


# ------------------------------------------------------------------ relatório
def write_md(rows, wb, kws, sh):
    from collections import Counter
    cls = Counter(r["classe"] for r in rows)
    L = []
    A = L.append
    A("# Matriz de procedência por constante — o número da Fase 2\n")
    A("> **2026-07-28.** Só-leitura sobre o bloco `shared` canônico de")
    A("> `joint_calibrations.json` (fit de 2026-07-04) e a maquinaria de")
    A("> procedência do `knowledge_base`. Nenhuma simulação, fit, adoção ou")
    A("> escrita. Script: `New_Theory/provenance_matrix.py`; números:")
    A("> `provenance_matrix.json`.\n")
    A("> **Escopo:** as constantes **compartilhadas** — as que a tese \"uma")
    A("> física, N estados\" põe em jogo. Os configs adotados per-rig ficam fora")
    A("> de propósito (são por-rig por construção, e o `adopted_configs.json`")
    A("> estava em escrita por outra sessão quando isto rodou).\n")
    A("---\n")
    A("## 1. O número\n")
    A(f"O canônico usa **{len(rows)} constantes compartilhadas**. Por classe de")
    A("procedência:\n")
    A("| classe | n | o que a move |")
    A("|---|--:|---|")
    mv = {"BANDA_DENTRO": "nada — está provado",
          "BANDA_FORA": "re-ancorar, ou **separar a constante**",
          "ANCORA_POR_PAR": "nada p/ o par usado; generalizar exige medir o par novo",
          "DIRECAO": "medir a magnitude",
          "INPUT_POR_JUNTA": "nada — é input de tabela, por decisão",
          "FIXO_POR_DECISAO": "reabrir a decisão",
          "FIT_SEM_ANCORA": "é a dívida mais cara",
          "SEM_PROCEDENCIA": "medir, ou anular a constante"}
    for k, n in sorted(cls.items(), key=lambda kv: -kv[1]):
        A(f"| `{k}` | {n} | {mv.get(k, '')} |")
    A("")
    prov = cls["BANDA_DENTRO"] + cls["INPUT_POR_JUNTA"] + cls["FIXO_POR_DECISAO"]
    fora = [r["constante"] for r in rows if r["classe"] == "BANDA_FORA"]
    A(f"**Leitura honesta, e o título não é o \"quantas têm\":** só")
    A(f"**{prov} das {len(rows)}** estão em situação que dispensa trabalho")
    A("(banda medida com o valor dentro · input de tabela · fixo por decisão")
    A(f"declarada). **{cls['SEM_PROCEDENCIA']}** não têm procedência nenhuma")
    A(f"registrada. **{cls['FIT_SEM_ANCORA']}** é fitada ao dataset **sem")
    A("âncora** — o `W_conf_ref`, cuja caça a âncora **falhou por null decisivo**")
    A("em 2026-07-04 (§4.9).\n")
    A(f"**O achado é a linha `BANDA_FORA`: {cls['BANDA_FORA']} constantes têm")
    A(f"banda MEDIDA e o valor canônico está FORA dela** — `{'` e `'.join(fora)}`.")
    A("Isso é pior que não ter âncora: a medição existe, e o canônico a")
    A("contradiz. As duas estão detalhadas nos §3 e §4 — e das duas, **só a do")
    A("`k_wear_spec` é nova**; a do `N_emb` já estava registrada como *\"não")
    A("reconciliada\"* e aqui foi **reproduzida por rota independente**.\n")
    A("## 2. A matriz\n")
    A("| constante | valor | classe | fitada | por quê |")
    A("|---|--:|---|:--:|---|")
    for r in rows:
        # `|` no nome da interface (thread|35CrMo) quebraria a celula da tabela
        porque = r["porque"].replace("|", "\\|")
        A(f"| `{r['constante']}` | {r['valor']:.6g} | **{r['classe']}** | "
          f"{'sim' if r['fitada'] else '—'} | {porque} |")
    A("")
    A("---\n")
    A("## 3. `k_wear_spec`: o valor canônico cai no VÃO entre duas bandas\n")
    A("Este é o caso que a matriz existe para achar, e ele estava documentado")
    A("errado. O registro de 2026-07-28")
    A("(`l7_removal_energy_diagnostic_2026-07-28.md` e o Manual) diz que a R5")
    A("tem **\"única banda MEDIDA\"** e que o canônico está **~130× abaixo**")
    A("dela. Medido: a R5 tem **3** bandas, e a comparação depende da")
    A("**unidade**.\n")
    A("| interface\\|par | banda | unidade | comparável? | canônico 5e-14 |")
    A("|---|---|---|:--:|---|")
    for b in wb:
        lo, hi = b["banda"]
        cmp_ = "sim" if b["comparavel"] else "**NÃO**"
        ver = ("—" if not b["comparavel"] else
               f"{b['lado']} ({b['razao']}×)" if not b["dentro"] else "dentro")
        A(f"| `{b['chave']}` | [{lo:g}, {hi:g}] | {b['unidade']} | {cmp_} | {ver} |")
    A("")
    A("**Três correções ao que está escrito:**\n")
    A("1. **Não é \"única banda\": são 3.**")
    A("2. **`fretting|52100-52100` NÃO é comparável** — está em `norm-own` (a")
    A("   normalização do próprio paper), não em `1/Pa`. Compará-la ao canônico")
    A("   é erro de unidade, e é o que produziria o \"×6e8\" que aparece se a")
    A("   conta for feita sem olhar a unidade.")
    A("3. **A banda mais próxima não é a `faying` — é a `thread`**, e o canônico")
    A("   está **ACIMA** do teto dela, não abaixo do piso. Ou seja: a direção do")
    A("   argumento **inverte** conforme a interface.\n")
    A("**E o que sobra é mais forte que o erro.** As duas bandas comparáveis")
    A("**cercam o canônico pelos dois lados**:\n")
    cmpb = [b for b in wb if b["comparavel"]]
    if len(cmpb) == 2:
        lo_hi = sorted(cmpb, key=lambda b: b["banda"][1])
        A(f"    {lo_hi[0]['chave']}: teto {lo_hi[0]['banda'][1]:g}")
        A(f"      <  canônico k_wear_spec = {kws:g}  <")
        A(f"    {lo_hi[1]['chave']}: piso {lo_hi[1]['banda'][0]:g}")
        A("")
        gap = lo_hi[1]["banda"][0] / lo_hi[0]["banda"][1]
        A(f"As duas bandas medidas distam **{gap:.0f}×** entre si. O engine usa")
        A("`k_wear_spec` nos **dois** canais — `WearLoss` (faying/apoio) **e**")
        A("`ThreadFrettingLoss` (rosca) — então **nenhum valor único pode estar")
        A("dentro das duas**. Isso não é um valor a corrigir: é a **L6**")
        A("(não-universalidade de K/H por par) em números exatos, e é argumento")
        A("para **separar a constante por interface**, não para movê-la.\n")
    A("---\n")
    A("## 4. `N_emb` = 50 contra a faixa lida [3, 15]\n")
    A("> **Não é achado novo, e a correção é minha:** o §5 do relatório executivo")
    A("> do Manual já registra esta divergência como *\"registrada e não")
    A("> reconciliada\"*. Esta varredura a **reproduziu por rota independente**")
    A("> (leitura do prior + comparação com o canônico), o que vale como")
    A("> confirmação. O que é novo aqui são as **duas leituras** abaixo.\n")
    ne = next(r for r in rows if r["constante"] == "N_emb")
    A("O prior `N_emb` do KB não é uma banda de literatura: é a **faixa dos")
    A("valores per-rig LIDOS** do próprio dado, com a nota")
    A(f"*\"{ne['nota_kb']}\"*. A faixa é **{ne['banda']}** e o canônico")
    A(f"compartilhado é **{ne['valor']:g}** — **{ne['valor']/ne['banda'][1]:.2g}×")
    A("acima do topo**.\n")
    A("**O que isso é, e o que não é.** Não é erro aritmético nem valor")
    A("inventado: `N_emb` é a constante de tempo do assentamento, e o valor 50")
    A("saiu do fit compartilhado na escala UFU. A faixa [3, 15] saiu de ler o")
    A("**tempo de joelho** curva a curva. As duas coisas medem o mesmo relógio e")
    A("discordam por 3×. Duas leituras possíveis, e a varredura não decide entre")
    A("elas:\n")
    A("1. a faixa lida é **per-rig** e o canônico é uma média que nenhum rig")
    A("   individual exibe (mesma classe do `W_conf_ref` per-par);")
    A("2. o `N_emb` canônico está absorvendo atraso que pertence a outro")
    A("   mecanismo — e há candidato nomeado na fila: **incubação do")
    A("   assentamento** (item 8, UFU: *\"dado plano até N≈38 e o modelo assenta")
    A("   desde o ciclo 1\"*), que é exatamente um atraso que hoje não existe no")
    A("   engine.\n")
    A("A leitura (2) é a que vale checar primeiro, porque uma constante de tempo")
    A("inflada é **como** um modelo sem incubação compra um platô inicial.\n")
    A("---\n")
    A("## 5. Dois achados de instrumentação\n")
    A("**(a) `check_input` roda em 1 das 10.** Só")
    A(f"`{sorted(kb.checkable_inputs())}` têm guarda, e dessas apenas")
    A("**`k_wear_spec` e `conform_pressure_exp`** são constantes do bloco")
    A("`shared`. As outras 8 passam sem verificação nenhuma — e o contrato da")
    A("função devolve `None` tanto para \"dentro da banda\" quanto para \"não sei")
    A("checar\", ambiguidade que a própria docstring registra desde 07-28. A")
    A("consequência prática: **um valor fora de banda numa das 8 não dispara")
    A("nada.**\n")
    A("**(b) O único aviso que dispara é o do nosso próprio canônico.**")
    kws_row = next(r for r in rows if r["constante"] == "k_wear_spec")
    A(f"`check_input(\"k_wear_spec\", {kws:g})` devolve:\n")
    A("```")
    A(str(kws_row["check_input"]))
    A("```")
    A("O aviso cita a banda `faying` — a mais **distante** das duas comparáveis.")
    A("Pelo §3, o número que ele deveria citar depende do canal que domina a")
    A("perda naquele caso, e hoje ele cita um só.\n")
    A("---\n")
    A("## 6. O que isto propõe (nada adotado)\n")
    A("1. **`k_wear_spec` por interface** (`k_wear_spec_faying` /")
    A("   `k_wear_spec_thread`), cada um com a sua banda medida. É a única")
    A("   mudança que pode pôr o modelo **dentro** de procedência medida no")
    A("   canal de desgaste. Custo: constante nova (forma, não valor) ⇒ prereg.")
    A("2. **Ampliar `checkable_inputs` às 8 sem guarda**, mesmo com banda vazia,")
    A("   para que a ausência de âncora seja **visível** em vez de silenciosa.")
    A("3. **`N_emb`: checar a leitura (2) do §4** — se a incubação do")
    A("   assentamento (fila item 8) explicar o atraso, o `N_emb` canônico deve")
    A("   voltar para a faixa lida. Diagnóstico só-leitura, sem prereg.")
    A("4. **`W_conf_ref` segue a dívida mais cara**: fitada, sem âncora, e com a")
    A("   caça registrada como null decisivo. Nada aqui muda isso.")
    A("5. **Corrigir os 3 pontos** que dizem \"única banda medida / 130×\":")
    A("   `l7_removal_energy_diagnostic_2026-07-28.md`, Manual")
    A("   `00-relatorio-executivo.md` e `03-aplicar-o-software.md`.\n")
    A("> **Escopo do que NÃO foi medido, dito de propósito:** as 10 são as")
    A("> **compartilhadas**. Os configs adotados per-rig têm dezenas de")
    A("> constantes a mais, e a mesma varredura sobre eles é trabalho aberto —")
    A("> não foi feita aqui porque o arquivo estava em escrita por outra sessão.\n")
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    rows, wb, kws, sh = build()
    from collections import Counter
    print(f"\n{len(rows)} constantes compartilhadas\n")
    for k, n in sorted(Counter(r["classe"] for r in rows).items()):
        print(f"  {k:20s} {n}")
    print()
    for r in rows:
        print(f"  {r['constante']:22s} {r['valor']:12.4g}  {r['classe']:18s}"
              f" {'FIT' if r['fitada'] else ''}")
    print("\n-- k_wear_spec vs bandas R5 --")
    for b in wb:
        print(f"  {b['chave']:28s} {str(b['banda']):26s} {b['unidade']:9s}"
              f" comparavel={b['comparavel']} {b['lado'] or ''}"
              f" {(str(b['razao'])+'x') if b['razao'] else ''}")
    OUT_JSON.write_text(json.dumps(
        {"escopo": "bloco shared canonico", "n": len(rows),
         "constantes": rows, "wear_bands": wb,
         "shared_calibrated_at": sh.get("calibrated_at")},
        indent=1, ensure_ascii=False), encoding="utf-8")
    write_md(rows, wb, kws, sh)
    print(f"\nJSON -> {OUT_JSON.relative_to(ROOT)}")
    print(f"MD   -> {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
