# `CHU_2026` não é *form-limited*: **8 de 9 curvas rodam em DEFAULTS**

**2026-08-11** · só-leitura · **nada adotado** · store `bd74eaf0b11d`, censo **147/205** ·
primeira investigação da classe **GROSS** sob a taxonomia mecânica.

## Onde eu comecei, e a hipótese que morreu

As **7 abertas em GROSS SLIP** são 6 do `CHU_2026` + 1 do `ROUSSEAU`. Nas 6 do CHU o `wear`
carrega **0,25–0,57 absoluto** (dominante) com `k_wear_spec` no **default** — o cenário ideal da
receita D-AB.

**Hipótese testada:** o paradoxo da rugosidade do CHU (a correção de input **certa** melhora a
`test3` em 0,058 mas destrói as duas de D=1,0 mm) se explicaria por **classe mecânica**
diferente entre elas.

⛔ **Falsificada.** Medido: `test3`, `test5` e `test6` são **todas GROSS** (slip/δ = 0,998). A
única PARCIAL é a **`test1`** (slip/δ = **0,009** — praticamente na fronteira do stick). A
divisão de efeitos não vem da classe.

## ✅ E a varredura confirma a regra canal×classe

`k_wear_spec` per-fonte, 6 doses, com controle da fonte:

| dose | tripé | saem | pioram | mediana |
|---|---|---|---|---|
| ×0,3 | 3 → **1** | 2 | 7 | 0,1193 |
| ×0,5 | 3 → **1** | 2 | 7 | 0,0937 |
| ×0,7 | 3 → **1** | 2 | 7 | 0,0743 |
| ×1,5 | 3 → **2** | 1 | 3 | 0,1033 |
| ×2,0 | 3 → **1** | 2 | 7 | 0,1455 |
| ×3,0 | 3 → **1** | 2 | 8 | 0,2493 |

**Nenhuma dose ganha; todas perdem curvas.** A regra
(`regra_canal_vs_classe_resultado.md`) prevê isso — o CHU é **classe mista** (8 GROSS + 1
PARCIAL) e `k_wear_spec` é canal dirigido por slip. **Sétima predição correta da regra.**

## ⚠️ O achado que reenquadra a fonte

| curva | chaves de override adotadas |
|---|---|
| **`test1`** (D 0,3) | **15** (`C_creep`, `W_ref`, `c_D`, `c_bend`, `conform_driver`, `emb_depth`, …) |
| `test2`, `test7`, `test8`, `test9`, `test3`, `test4`, `test5`, `test6` | **0 — rodam em DEFAULTS** |

**8 das 9 curvas do `CHU_2026` não têm nenhuma constante adotada.** E há três coincidências que,
juntas, mudam a leitura da fonte:

1. a única curva com config fitada (`test1`) é a **única quase-perfeita** (0,0035/0,0082/0,0032);
2. ela é também a única **PARCIAL**, e a que menos escorrega (slip/δ = 0,009);
3. as outras 8 herdam o `RZ_DEFAULT` de rugosidade, que a própria nota do paper contradiz
   (Ra 0,4 µm nos testes 1–8; 1,6 µm no 9).

⇒ **`CHU_2026` está melhor descrita como NÃO-CALIBRADA por condição do que como form-limited.**
A fonte está na fila há semanas com 6 abertas, e o diagnóstico corrente ("form-limited com prova
em nível de lei", §4.54a) foi estabelecido quando o instrumento de sonda estava **cego** para
alavancas no default — o mesmo defeito que o `0c4477a` consertou.

## E é *isto* que barra a constante compartilhada, não só a classe

Qualquer mudança source-wide atinge as 9, e **uma delas carrega 15 constantes fitadas**. A
`test1` está no ótimo do seu próprio ajuste, então toda dose compartilhada **a tira de lá** — o
que aparece nas varreduras como "2 saem do tripé". A assimetria de calibração é a causa
proximal do null, e ela é **estrutural**, não física.

⚠️ **Não é conclusão de erro.** Ter uma condição calibrada e oito em defaults pode ter sido
decisão deliberada de parcimônia. O que está medido é que essa assimetria **impede** o
compartilhamento, e que a alternativa (`per_case` para as 8) nunca foi tentada nesta fonte.

## O que isto NÃO destrava sozinho

Nada. Calibrar 8 curvas per-case é **8 conjuntos de constantes** — o oposto da parcimônia que a
campanha persegue, e exatamente o tipo de coisa que precisa de argumento físico por condição
(δ e F₀ variam de forma conhecida: 0,3–1,0 mm e 49–73 kN). **É decisão do professor**, e o custo
em DOF tem de estar na mesa junto com o ganho.

E permanece de pé o item já na fila: **a rugosidade registrada contradiz o paper nas 9**, e
corrigi-la sozinha piora a métrica. As duas coisas se somam — corrigir o input **e** calibrar por
condição é a única combinação que a medição não exclui.

## Reprodutibilidade

```bash
py -3.12 -u New_Theory/ataque_curva.py chu2026ti_D0p5mm_F0_49kN_test3
```
Sondas no scratchpad: `gross_diag.py` (canais das 7 GROSS abertas), `chu_wear.py` (varredura +
capacidade absoluta), leitura de `_effective_overrides` por curva. Só-leitura.
