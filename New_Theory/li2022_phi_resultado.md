# Φ do LI_2022 — ADOTADO por procedência, com efeito NULO na métrica

**2026-08-05** · prereg D-P (`2026-08-05-li2022-phi-medido`), por delegação sob
o MANDATO PERMANENTE. Adoção: `New_Theory/li2022_phi_adota.py`. Derivação:
`li2022_phi_ancora.md`.

## Veredicto: ADOTA — e o valor está na procedência, não em curva fechada

`k_j_init` = **5,29e8** N/m para o grupo `LI_2022_TRIBOINT` ⇒ **Φ = 0,4673**,
contra os **0,1039** que o default `4e9` produzia (**4,5× pequeno**).

| gate | resultado |
|---|---|
| **G1 (efeito nulo)** | ✅ **Δ = 0,000e+00 exato** nas 4 curvas da fonte |
| **G2 (o número está certo)** | ✅ `Phi_eff(axial) = 0,46727` (alvo 0,467 ± 0,005) |
| G3 (isolamento) | ✅ só o grupo `LI_2022_TRIBOINT` |
| G4 (procedência escrita) | ✅ eq. 2 + Fig. 8(b) + conferência ao dígito no `prov` |
| G5 (acoplamento latente declarado) | ✅ `k_torsional` 7,6× no `prov` |

## A derivação, fechada com o dado do próprio paper

A eq. 2 (p2) dá a lei da carga: **`F = A_F + A_F·sin(2πft)`** com A_F = 10 kN ⇒
a carga externa varre **0 → 20 kN** (pico-a-pico **20 kN**). A Fig. 8(b) traz a
envoltória **medida** no parafuso a 10 Hz: **19,10 / 9,76 kN**.

```
Φ = 9,34 / 20 = 0,467
conferência:  F_B,max = 9,76 + 0,467·20 = 19,10 kN   ✅ ao dígito
              F_B,min = F₀ + Φ·0 = 9,76 kN = pré-carga residual
k_j = k_b(1−Φ)/Φ = 4,64e8 · 0,533/0,467 = 5,29e8 N/m
```

Plausibilidade: rig servo-hidráulico com **fixture custom** (upper/lower
clamping ends); o caminho de carga inclui o fixture — não é o Φ de uma junta
flangeada compacta.

## Por que a inércia é o resultado CERTO, e não decepção

Φ entra **apenas** em `L_ax = Φ_ax_active · sin(β) · F_ax` — o canal de
**afrouxamento rotacional**, que carrega **0,000 %** da perda nestas curvas
(medido). E o canal que carrega **57 %**, o de flanco, usa
**`s_th = F_ax / max(geom.k_b, 1.0)`** (engine linha 1248) — **sem passar por
Φ**.

⇒ O número estava errado por 4,5× e **não contaminava nada**.

### O teste que separa as duas leituras de um Δ=0

A regra do charter proíbe concluir "inerte" sem descartar a alternativa. As duas
hipóteses e seus testes:

| hipótese | teste | resultado |
|---|---|---|
| **(b)** sondei o campo errado (`kj_mode` sobrepõe) | `Phi_eff` muda quando `k_j_init` muda? | **0,10394 → 0,46727** ⇒ o campo **É lido**; `kj_mode` default é `''` |
| **(a)** inércia gateada por canal | o canal que Φ governa carrega quanto? | `rotational_loosening` = **0,000000** (0,000 %) |

⇒ **(a) confirmado, (b) refutado.** Não é a armadilha do campo errado que me
pegou três vezes hoje (`emb_um`, canal de flanco sem companheiro, `GA_member`).
E a predição de inércia foi **registrada antes** da medição
(`li2022_phi_ancora.md`, commit `f0222b8`).

## Isto desmente uma dívida que EU declarei no D-O

Escrevi no resultado do D-O que *"o slip de flanco está subestimado na mesma
proporção e qualquer `k_wear_flank` fitado hoje compensa o Φ errado"*.
**Falso.** Aritmética: o engine usa `10 000/4,64e8 = **21,6 µm**`; o correto
pela oscilação medida é `9 340/4,64e8 = **20,1 µm**` — **7 %**, não 4,5×.

O canal que decide já estava quase certo **por acidente de convenção**: o
engine usa a amplitude zero-a-pico da carga **aplicada** onde deveria usar a
oscilação do **parafuso**, e nesta junta os dois quase coincidem. Errata
publicada em `74a2fab`.

## Dois subprodutos que fecham pendências

1. **A ambiguidade de observável está RESOLVIDA.** `F_B,min` é o valor com a
   carga externa em zero ⇒ **é a pré-carga residual**, exatamente o que o
   modelo calcula. A nota de aparato dizia *"the residual"*; agora está
   **derivado**. O observável das curvas `axialmin` está **correto**.
2. **A correção de input do D-N era Φ(f)/Φ(10 Hz).** Φ medido por frequência:
   0,467 / 0,366 / 0,286 ⇒ razões **0,783** e **0,612** — idênticas às que usei
   para escalar o `F_amp`. O D-N capturou a dependência de frequência de Φ sem
   que eu soubesse que era isso.

## Acoplamento latente, declarado no `prov`

`k_torsional` no modo legado é `k_j_init·d_2/2`, logo esta mudança o altera
**7,6×**. Hoje é inócuo (o canal carrega 0), **mas** se um trabalho futuro
ativar o afrouxamento rotacional nesta fonte, o `k_torsional` estará 7,6×
diferente do que estava quando qualquer constante daquele canal foi calibrada.
Registrado para não virar surpresa.

## O que isto libera

O candidato de **saturação do canal de flanco** — apontado por três achados
independentes (o dado satura e o modelo não · o canal do paper é o do flanco ·
`delta_thread_fret` é estado acumulado que a lei nunca lê) — pode agora ser
pré-registrado **sem dívida herdada**: o Φ está certo no canônico e não há
suspeita de que o `k_wear_flank` esteja compensando outra coisa.
