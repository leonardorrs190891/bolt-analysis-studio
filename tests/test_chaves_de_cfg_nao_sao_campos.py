# -*- coding: utf-8 -*-
"""As chaves de CFG que NÃO são campos do engine, listadas e explicadas.

## Por que este arquivo existe

Três vezes em 2026-08-01/02 uma sonda deu **Δ = 0,0000 exato** e a leitura
óbvia — "alavanca morta" — estava ERRADA. Em todas, a causa era a mesma: o
que foi sondado era **chave de configuração adotada**, não campo de
`JointMaterial`; o override morre no filtro do runner **em silêncio**.

* `emb_um` (µm) → o campo é `emb_depth` (m) — matou uma grade inteira do N₉₅;
* `GA_member` → o campo é `k_member_shear` (= GA/t) — quase enterrou o
  re-fit do HDPE, que na verdade responde forte;
* (variante) canal de flanco sem `flank_transverse_on` — o campo existia,
  mas o COMPANHEIRO estava desligado.

O teste não impede a tradução (ela é legítima: `emb_um` é unidade humana,
`GA_member` é a grandeza física do paper). Ele **mantém a lista visível e
explicada**, para que a próxima sonda saiba que precisa do campo real.

Falha de dois modos, os dois úteis:
* chave nova sem explicação ⇒ alguém adicionou uma tradução silenciosa;
* chave da lista que virou campo do engine ⇒ a nota está vencida.
"""
import json
from pathlib import Path


# chave de cfg -> (campo/rota real no engine, quem traduz)
_TRADUZIDAS = {
    "emb_um":          ("emb_depth (m) = emb_um*1e-6", "suggest_overrides"),
    "emb":             ("emb_depth via classe de rugosidade VDI", "library_common"),
    "mu":              ("mu_thread/mu_bearing", "cfg escrito por extenso"),
    "k_wear_scale_tr": ("K_archard/k_wear_spec", "tuner_shim (Estágio B)"),
    "trim_n_max":      ("janela da MÉTRICA, não do engine", "runner._trim_n_for"),
    "d_hole_mm":       ("JointGeometry.d_hole (m)", "geometry_for_case"),
    "d_washer_mm":     ("JointGeometry.d_washer (m)", "geometry_for_case"),
    "GA_member":       ("k_member_shear (N/m) = GA_member/t", "runner (per-case)"),
    "delta_amp_mm":    ("amplitude imposta do CASO", "runner._delta_amp_override"),
    "delta_spectrum":  ("lista de blocos de amplitude", "runner (lê do cru)"),
    "c_D_per_lube":    ("c_D por lubrificação", "cfg por subgrupo"),
    "c_D_dry":         ("c_D (seco)", "cfg por subgrupo"),
    "c_D_oil":         ("c_D (lubrificado)", "cfg por subgrupo"),
}


def _cfg_keys():
    raiz = Path(__file__).resolve().parents[1]
    d = json.loads((raiz / "New_Theory" / "adopted_configs.json")
                   .read_text(encoding="utf-8"))
    out = set()
    for node in d["sources"].values():
        for k in (node.get("cfg") or {}):
            if k not in ("per_case", "prov", "verdict"):
                out.add(k)
    return out


def _campos():
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial)
    return set(JointMaterial.__dataclass_fields__)


def test_toda_chave_traduzida_esta_explicada():
    """Chave de cfg que não é campo do engine TEM de estar na lista com o
    campo real — senão a próxima sonda vai medir Δ=0 e concluir errado."""
    orfas = sorted(k for k in _cfg_keys() - _campos() if k not in _TRADUZIDAS)
    assert not orfas, (
        f"chaves de cfg SEM tradução documentada: {orfas}. Sondá-las via "
        f"_effective_overrides devolve Δ=0 EM SILÊNCIO (3 ocorrências em "
        f"2026-08-01/02). Documente o campo real em _TRADUZIDAS.")


def test_a_lista_nao_envelhece():
    """O inverso: se uma chave da lista VIROU campo do engine, a nota está
    vencida e o aviso passa a confundir em vez de ajudar."""
    virou = sorted(k for k in _TRADUZIDAS if k in _campos())
    assert not virou, (
        f"estas chaves agora SÃO campos de JointMaterial: {virou} — tire-as "
        f"de _TRADUZIDAS, a advertência não vale mais para elas.")


def test_os_tres_casos_medidos_seguem_traduzidos():
    """Pino dos três que de fato enganaram uma sonda — se algum sumir da
    lista sem virar campo, a lição foi perdida."""
    campos = _campos()
    for k in ("emb_um", "GA_member"):
        assert k in _TRADUZIDAS and k not in campos
    # o 3º caso é de COMPANHEIRO, não de tradução: o campo existe, mas só
    # age com `flank_transverse_on` ligado em fonte transversal.
    assert "flank_wear_on" in campos and "flank_transverse_on" in campos
