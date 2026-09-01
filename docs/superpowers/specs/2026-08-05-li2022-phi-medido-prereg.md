# Prereg — Φ medido no LI_2022: procedência com efeito NULO

**2026-08-05** · decisão D-P (por delegação, MANDATO PERMANENTE) · fingerprint
de partida `e38eed05fa47`. Derivação completa em `li2022_phi_ancora.md`.

## O que se adota, e por quê

`k_j_init` = **5,29e8** N/m para o grupo `LI_2022_TRIBOINT`, dando
**Φ = 0,4673** contra os **0,1039** do default.

**Procedência — derivada, não fitada.** A eq. 2 do paper dá a lei da carga:
`F = A_F + A_F·sin(2πft)` com A_F = 10 kN ⇒ a carga externa varre **0 → 20 kN**
(pico-a-pico 20 kN). A Fig. 8(b) traz a envoltória **medida** no parafuso a
10 Hz: 19,10 / 9,76 kN ⇒ oscilação **9,34 kN**.

```
Φ = 9,34 / 20 = 0,467
conferência:  F_B,max = 9,76 + 0,467·20 = 19,10 kN  ✅ ao dígito
              F_B,min = F₀ + Φ·0 = 9,76 kN = a pré-carga residual
k_j = k_b(1−Φ)/Φ = 4,64e8 · 0,533/0,467 = 5,29e8 N/m
```

Plausibilidade: o rig é servo-hidráulico com **fixture custom (upper/lower
clamping ends)** e o caminho de carga inclui o fixture — não é o Φ de uma junta
flangeada compacta.

## ⚠️ Esta adoção NÃO melhora nenhuma métrica, e é isso que se afirma

**Δ = 0,00e+00 exato** nas 4 curvas da fonte, medido. E a razão está
estabelecida por dois testes que separam as duas explicações possíveis:

* **Teste do campo (descarta "sondei o errado"):** `Phi_eff` **muda**
  0,10394 → 0,46727 quando `k_j_init` muda. O campo **é lido**; `kj_mode`
  default é `''` (inativo).
* **Teste do canal (confirma a predição):** `rotational_loosening` =
  **0,000000** — 0,000 % da perda nas duas curvas. Φ só entra em
  `L_ax = Φ_ax_active · sin(β) · F_ax`, ou seja no afrouxamento rotacional.

⇒ Inércia **gateada por canal** (`channel_gated_levers`), com predição
registrada **antes** da medição em `li2022_phi_ancora.md`.

**O slip de flanco NÃO passa por Φ** (linha 1248:
`s_th = F_ax / max(geom.k_b, 1.0)`), e é por isso que o canal que decide não se
move. Aritmética: engine 21,6 µm vs correto 20,1 µm — **7 %**.

## Gates (IMUTÁVEIS)

- **G1 (efeito nulo — o gate que define a natureza da adoção):** as **210**
  curvas do store ficam **bit-idênticas** (Δ < 1e-12 em mae, res.máx, σ). Se
  QUALQUER curva mudar, a adoção deixa de ser higiene e vira alavanca — e aí
  precisa de outro prereg, com gates de ganho.
- **G2 (o número está certo):** `Phi_eff(axial)` da fonte = **0,467 ± 0,005**.
- **G3 (isolamento):** só o grupo `LI_2022_TRIBOINT`; nenhuma outra fonte
  recebe `k_j_init`.
- **G4 (procedência escrita):** o `prov` cita a eq. 2, a Fig. 8(b) e a
  conferência de F_B,max ao dígito, e diz **explicitamente** que o efeito na
  métrica é **nulo**.
- **G5 (acoplamento latente declarado):** `k_torsional` no modo legado é
  `k_j_init·d_2/2`, logo esta mudança o altera **7,6×**. Hoje é inócuo (o canal
  carrega 0), mas **tem de estar escrito no `prov`**: se um trabalho futuro
  ativar o afrouxamento rotacional nesta fonte, o `k_torsional` estará 7,6×
  diferente do que estava quando qualquer constante daquele canal foi calibrada.
- **G6 (sincronia):** fingerprint muda (o hash cobre as configs adotadas) ⇒
  re-stamp uniforme dos 210 + docs no MESMO commit, mesmo com métrica idêntica.

### Ramos

- **ADOTA** — G1..G5.
- **NÃO ADOTA (virou alavanca)** — G1 falha: alguma curva muda ⇒ o efeito não é
  nulo e a adoção precisa de gates de ganho, não de higiene.

## Previsão registrada

Espero **G1 passar exatamente** (Δ=0 já medido nas 4 da fonte; as outras 206 não
recebem nada). Espero o fingerprint mudar **sem nenhuma métrica mudar** — o que
é o caso raro em que o re-stamp existe só para manter a uniformidade do hash.
