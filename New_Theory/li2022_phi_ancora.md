# Φ do LI_2022 — a âncora MEDIDA, e onde ela entra (ou não entra)

**2026-08-05** · investigação sob o MANDATO PERMANENTE, a pedido do professor
(*"resolva o Φ primeiro"*). Fingerprint `e38eed05fa47`. Só-leitura até aqui.

## A derivação, fechada com o dado do paper

O paper dá a lei da carga aplicada **explicitamente** (eq. 2, p2):

> *"The axial alternating load is controlled by sinusoidal loading, and the
> loading path is **F = A_F + A_F·sin(2πft)**, where **A_F = 10 kN**"*

⇒ a carga externa varre **0 → 20 kN** (pulsante, R = 0, média 10 kN,
amplitude zero-a-pico 10 kN, **pico-a-pico 20 kN**).

E a Fig. 8(b) traz a envoltória **medida** da força no parafuso. Fechando a
conta a 10 Hz:

| grandeza | valor | conferência |
|---|---:|---|
| oscilação aplicada (pico-a-pico) | 20 kN | eq. 2 |
| oscilação **medida** no parafuso | **9,34 kN** | Fig. 8(b): 19,10 − 9,76 |
| **Φ = 9,34 / 20** | **0,467** | |
| `F_B,min = F₀ + Φ·0` | 9,76 kN | ✅ é a **pré-carga residual** |
| `F_B,max = 9,76 + 0,467·20` | **19,10 kN** | ✅ confere ao dígito |

**Φ por frequência:** 0,467 (10 Hz) · 0,366 (15 Hz) · 0,286 (20 Hz).

### Isto resolve a ambiguidade de observável que estava pendente

`F_B,min` é o valor com a carga externa em **zero**, logo **é a pré-carga
residual** — exatamente o que o modelo calcula. A nota de aparato já dizia
*"the residual"*; agora está **derivado**, não assumido. **O observável das
curvas `axialmin` está CORRETO.**

### E confirma que a correção de input do D-N era Φ(f)/Φ(10 Hz)

As razões de Φ são **0,783** e **0,612** — idênticas às que usei para escalar
o `F_amp`. Ou seja: a correção de input do D-N capturou a **dependência de
frequência de Φ**, e o que ficou de fora foi o **nível absoluto**.

## O nível absoluto: modelo 0,104 contra 0,467 medido (4,5×)

`Φ = k_b/(k_b + k_j)` com `k_b = 4,64e8` e `k_j_init = 4e9` (default) ⇒
**Φ = 0,104**. Para Φ = 0,467 seria `k_j = k_b(1−Φ)/Φ ≈ **5,29e8**` — membro
~7,6× mais complacente que o default.

Plausibilidade: o rig é uma **máquina servo-hidráulica com fixture custom
(upper/lower clamping ends)**, e o caminho de carga inclui o fixture. Um Φ
alto (metade da carga chegando ao parafuso) é coerente com esse arranjo — não
é o Φ de uma junta flangeada compacta.

## ⚠️ Mas Φ pode NÃO propagar onde importa — e isso é decidível

Lendo o engine antes de mexer:

* **Linha 1248:** `s_th = F_ax / max(geom.k_b, 1.0)` — o slip de flanco no modo
  axial usa **`F_ax` DIRETO, sem passar por Φ**.
* **Linha ~1995:** `Phi_ax = Phi_eff(...)`, usado em
  `L_ax = Phi_ax_active · sin(β) · F_ax` — Φ entra no **afrouxamento
  rotacional**.

E a decomposição destas 4 curvas mostra o canal rotacional carregando **~0**.

⇒ **Predição registrada: corrigir `k_j` deve ser INERTE nestas curvas** — é a
classe `channel_gated_levers` do charter (alavanca gateada por canal que não
carrega perda). Sonda de 2 pontos em curso para confirmar.

Aritmética que sustenta a predição: o slip de flanco do engine é
`10 000/4,64e8 = **21,6 µm**`; o correto pela oscilação medida é
`9 340/4,64e8 = **20,1 µm**` — **7 % de diferença**. O canal que decide já
está quase certo, **por um acidente de convenção**: o engine usa a amplitude
zero-a-pico da carga aplicada onde deveria usar a oscilação do parafuso, e os
dois números quase coincidem nesta junta.

## Consequência para a dívida que eu declarei no D-O

Eu escrevi no D-O que *"qualquer `k_wear_flank` fitado hoje compensa o Φ
errado"*. **Isso está provavelmente ERRADO**, e pelo motivo acima: o
`k_wear_flank` é calibrado contra um slip que já está a 7 % do correto, não a
4,5×. A dívida é de **procedência do número Φ**, não de contaminação do fit.

Se a sonda confirmar a inércia, o conserto do Φ é **higiene de procedência
com efeito nulo na métrica** — o que é um resultado legítimo e vale ser dito
com esse nome, em vez de vendido como alavanca.
