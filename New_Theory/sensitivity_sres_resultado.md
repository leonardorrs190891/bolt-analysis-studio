# Sensibilidade do σ_res às alavancas — resultado

**Data:** 2026-07-29 · **Store:** `3546e6745448` · **Script:**
`New_Theory/sensitivity_sres.py` (só-leitura) · **Dados:**
`sensitivity_sres.json` · **Item 1** da lista de melhorias.

## Veredicto em uma linha

**Nenhuma das 18 alavancas fecha a perna do σ_res.** As que movem σ o suficiente
estragam o MAE na mesma jogada; as que movem σ preferencialmente são fracas por
1 a 2 ordens de grandeza. A perna nova pede **forma nova**, não recalibração — e
isso é decisão a tomar *antes* de gastar a campanha de otimização.

## Método

OAT ±20 % (mesma perturbação do estudo §4.42, para comparabilidade), medindo
`Δ|σ_res|`, `Δ|MAE|` e `Δ|res.máx|`. Três diferenças deliberadas:

1. perturba o **config canônico adotado**, pelo mesmo `_effective_overrides` que
   o runner usa — é nele que a adoção mexeria;
2. roda nas curvas que a campanha **precisa** consertar (10 das recusadas por
   prova de piso, uma por fonte, escolhidas pela razão valor/piso);
3. teto de 100 k ciclos por simulação, igual para nominal e perturbado — sem ele
   a varredura não termina (dois alvos são de 5·10⁶ ciclos). Ranking local, não o
   MAE de galeria daquele caso.

342 simulações, ~40 min.

## Ranking

`Δσ_res` e `ΔMAE` são o deslocamento médio por passo de ±20 %.

| alavanca | Δσ_res | ΔMAE | Δσ/ΔMAE | classe |
|---|--:|--:|--:|---|
| `emb_depth` | **0,03576** | 0,13379 | 0,27 | **NÍVEL** |
| `k_wear_spec` | 0,00251 | 0,00162 | 1,56 | **FORMA** |
| `mu_bearing` | 0,00204 | 0,00420 | 0,49 | NÍVEL |
| `p_ref_conform` | 0,00156 | 0,00098 | 1,59 | **FORMA** |
| `c_bend` | 0,00129 | 0,00374 | 0,34 | NÍVEL |
| `C_creep` | 0,00121 | 0,00258 | 0,47 | NÍVEL |
| `N_emb` | 0,00082 | 0,00120 | 0,68 | NÍVEL |
| `W_conf_ref` | 0,00078 | 0,00050 | 1,58 | **FORMA** |
| `conform_pressure_exp` | 0,00066 | 0,00049 | 1,36 | **FORMA** |
| `tr_loose_gain` | 0,00032 | 0,00035 | 0,93 | mista |
| `loose_arrest_floor` | 0,00020 | 0,00018 | 1,10 | mista |
| `k_j_init` | 0,00010 | 0,00010 | 1,05 | mista |
| `mu_thread` | 0,00009 | 0,00010 | 0,88 | mista |
| `alpha_GW` · `eta_loose` · `slip_regime_sharpness` · `slip_capacity_coeff` · `partial_slip_exp` | **0,00000** | 0,00000 | — | **INERTE** |

## A conta que transforma o ranking em decisão

Das curvas ainda na fila (fora do tripé e **não** cobertas por exceção
assinada), **51 violam o σ_res**. A queda necessária:

| | Δσ_res a fechar |
|---|--:|
| p25 | 0,0100 |
| **mediana** | **0,0446** |
| p75 | 0,1025 |
| máx | 0,1965 |

Quanto cada alavanca de FORMA precisaria mudar para entregar a queda **mediana**,
supondo linearidade (que é generoso — a resposta satura):

| alavanca | passos de ±20 % | mudança total |
|---|--:|--:|
| `k_wear_spec` | 17,7 | **+355 %** |
| `p_ref_conform` | 28,6 | +572 % |
| `W_conf_ref` | 56,9 | +1 139 % |
| `conform_pressure_exp` | 67,4 | +1 347 % |

Nenhuma dessas mudanças cabe em banda de procedência: o `k_wear_spec` canônico é
5e-14 e a banda medida da R5 já o cerca (§4.42a); multiplicá-lo por 4,5 sai da
literatura inteira.

**E a única alavanca com magnitude suficiente é de nível.** O `emb_depth` fecharia
a mediana em **1,2 passos** — mas arrasta o MAE em **0,134 por passo**, ou seja
~0,16 no total, contra um limite de MAE de **0,05**. Fechar o σ_res por ali
estoura o MAE por 3×. É o retrato do que a decomposição já dizia: `emb_depth` é o
parâmetro de nível do modelo, e nível não conserta forma.

## O que isto autoriza e o que proíbe

**Proíbe** (com número, não com opinião): abrir uma campanha de recalibração
esperando que ela feche a perna do σ_res. O ranking mostra que ela terminaria em
um destes dois lugares — constantes fora de banda, ou MAE estourado.

**Autoriza** três coisas:

1. **Tratar o σ_res como pergunta de FORMA.** As classes que a campanha já
   catalogou como *form-limited* (kernel desacelerante de run-in, bifurcação de
   limiar, canal estrutural ξ-dependente, incubação de assentamento) são
   candidatas — e agora há critério para escolher entre elas: a que reduzir σ_res
   sem mexer no nível. O prereg de qualquer forma nova deveria medir Δσ/ΔMAE como
   gate, não só o MAE.
2. **Congelar os 5 inertes** — `alpha_GW`, `eta_loose`, `slip_regime_sharpness`,
   `slip_capacity_coeff`, `partial_slip_exp` dão Δ = **0 exato** nas três réguas,
   nos 10 casos. É a diretiva do professor de 2026-07-09 (*"quanto menos graus de
   liberdade mais robusto"*) com medição nova. ⚠️ **Caveat obrigatório:** "Δ = 0"
   tem dois significados, e este documento só pode afirmar o primeiro —
   *inerte neste working point*. O `eta_loose` é documentado como **gateado por
   canal** (`kb.channel_gated_levers()`), logo o zero dele é esperado onde o canal
   rotacional carrega ~0 da perda, e ele voltaria a agir noutro regime. Congelar
   exige `parameter_registry`, não este .md.
3. **Usar `k_wear_spec` como alavanca de forma FINA.** Ela é a única com razão
   Δσ/ΔMAE > 1,5 e magnitude não desprezível; não fecha a mediana, mas é a certa
   para as 13 curvas cujo gap está abaixo de 0,010 (o p25).

## Dois defeitos que a própria varredura achou (no método, antes do resultado)

1. **`mu` não é campo de `JointMaterial`** — são `mu_bearing`/`mu_thread`.
   Perturbá-lo dava Δ = 0 exato, e eu teria publicado *"µ é inerte"*, que é
   falso. Virou teste (`test_medicoes_cruzadas.py`).
2. **`K_archard` está morto no canônico:** o bloco `shared` adota
   `k_wear_spec = 5e-14` e o engine ignora a via legada K/H quando ele é > 0.
   Varrer o parâmetro morto e concluir "desgaste é inerte" seria erro de rota.
   Também virou teste.

A lição comum vale para toda a campanha: **`Δ = 0` tem dois significados** —
inerte no regime, ou nome que nunca chegou ao engine. Só o segundo é bug, e
distinguir exige conferir o nome contra `__dataclass_fields__` e a via ativa
contra o bloco `shared`.

## Reprodutibilidade

```bash
py -3.12 New_Theory/sensitivity_sres.py          # ~40 min · 342 simulações
py -3.12 New_Theory/sensitivity_sres.py --quick  # smoke (3 casos × 5 alavancas)
```

Só-leitura: não escreve store nem `adopted_configs.json` (verificado — MD5 do
store idêntico antes e depois).
