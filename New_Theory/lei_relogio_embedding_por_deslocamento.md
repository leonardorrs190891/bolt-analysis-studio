# Lei do relógio de assentamento: **`N_emb ∝ 1/δ`** — expoente **1**, previsto pela física e validado zero-refit

**2026-08-14** · só-leitura · **nada adotado** · store `c37618c5cc96`, censo **141/205** ·
forma nova assinada pelo professor (*"assine tudo"*).

## De onde veio

A adoção `CHU_2026_D1p0` fechou a `test5` com `N_emb` = **400** (δ = 1,0 mm). A `test9`
(δ = 0,5 mm) fecha com `N_emb` = **800**. E **nenhum par único serve às duas**
(`chu_par_unificado_nao_existe.md`).

Razão **2 em N** para razão **2 em δ** ⇒ expoente **exatamente 1**:

```
N_emb_eff(δ) = N_emb_ref · (δ_ref / δ)
```

## ⚠️ O expoente 1 NÃO é ajuste — é o que a física prediz

Se o assentamento se esgota depois de uma **distância de slip acumulada** `S` (achatamento de
asperezas até a área real de contato saturar), então:

```
N_emb = S / (slip por ciclo)      e      slip por ciclo ∝ δ
⇒ N_emb ∝ 1/δ                     ⇒      q = 1
```

⇒ **o expoente não é um grau de liberdade**: ele cai em 1 por construção do mecanismo, e a
medição em dois pontos independentes o confirma. Era precisamente a âncora que faltava à
adoção anterior, cujo `prov` registra *"não há âncora no artigo"*.

## ✅ Predição ZERO-REFIT — registrada antes de medir, 4 de 4

Com `q = 1`, `δ_ref` = 1,0 mm e `N_ref` = 400, a lei **prediz** `N_emb` = **1000** a
δ = 0,4 mm e **571** a δ = 0,7 mm. Nenhuma dessas curvas entrou no ajuste:

| curva | δ | σ nominal | σ com a lei | Δ |
|---|---:|---:|---:|---:|
| `test2` | 0,4 | 0,1897 | **0,1508** | −21 % |
| `test7` | 0,4 | 0,1671 | **0,1417** | −15 % |
| `test8` | 0,4 | 0,1924 | **0,1692** | −12 % |
| `test4` | 0,7 | 0,1255 | **0,0911** | **−27 %** |

**4 de 4 melhoram**, e o controle reproduz os dois pontos de ajuste (`test5` e `test9`
fecham as três pernas).

## ⚠️ Mas a lei é REAL e PARCIAL — o que ela não faz

**Nenhuma das 4 fecha.** Elas ficam em σ 0,09–0,17 contra o limite 0,0296, e MAE 0,08–0,16
contra 0,05. A lei move a coisa certa na direção certa e **não é suficiente** para essa
população: o defeito delas tem mais do que o relógio de assentamento.

⇒ leitura honesta: **a lei explica a diferença ENTRE condições, não o erro absoluto de cada
uma.** É exatamente o que se espera de uma forma que corrige um **acoplamento faltante**, e
não de um ajuste que persegue o resíduo.

## Por que isto vale mais que o par per-condição

| rota | constantes | escala? |
|---|---|---|
| par `emb_depth`/`N_emb` **por condição** | 2 × nº de condições | ❌ e os pares são **mutuamente incompatíveis** |
| **`N_emb ∝ 1/δ`** | **1 referência** (`δ_ref`, `N_ref`), **expoente fixado pela física** | ✅ uma forma, N condições |

E há um teste de falsificação embutido: a lei prediz o `N_emb` de **qualquer** amplitude nova
da fonte, sem refit. Se uma condição futura precisar de outro expoente, a forma está errada.

## ⚠️ O que a campanha JÁ tem, e por que não serve aqui

A **ρ-unificação** (`emb_amp_exp`/`rho_ref_emb`, §4.18, adotada no `LIU_2017_axial`) modula o
alvo do embedding por amplitude — mas por **razão de força** `ρ = F_ax_amp/F₀_init`. O
`CHU_2026` roda **`F_amp` constante em 19 600 N** nas cinco amplitudes de deslocamento ⇒ ρ é
**o mesmo** nas cinco e a forma **não distingue** as condições.

⇒ a forma nova é **irmã** da ρ-unificação, não substituta: uma modula o **alvo** por força, a
outra o **relógio** por deslocamento. E ela só é necessária em rigs de **deslocamento
imposto** com `F_amp` fixo — que é a assinatura do Junker.

## Próximo passo (implementação)

Campo novo em `JointMaterial`, **default-inerte** (bit-idêntico quando desligado), no padrão
das formas anteriores desta campanha:

```
emb_clock_delta_ref : float = 0.0     # 0 = OFF exato
# quando > 0:  N_emb_eff = N_emb * (emb_clock_delta_ref / delta_amp)
```

Gates que a implementação terá de passar: inércia bit-a-bit nas **210** com o default; a
`test5`/`test9` fechando **com uma única entrada de config**; e as 4 predições zero-refit
reproduzindo os números desta tabela.

## Reprodutibilidade

`chu_lei.py` no scratchpad: aplica `N_emb = 400·(1,0/δ)` por curva via
`_effective_overrides`, com controle nos 2 pontos de ajuste. ~8 min, só-leitura.
