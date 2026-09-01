# Karlsen (1) + Yang2019 (2) — diagnósticos por fonte (restos do kernel-A dissolvido)

**Data:** 2026-07-28 · **Custo:** zero preregs (leitura sobre medições já feitas:
`kernel_formA_leitura.json`, `kernel_f0slip_result.json`, `residual_drift_metric.json`)
**Contexto:** o "grupo A" dissolveu (§4.54/kernel_f0slip); a fila rebaixou para
estudo por fonte. Chu fechou hoje com prova em nível de lei. Restavam estes 3.

## 1. Karlsen run14p2 (M30 HV torqued) — falta 25 % de aceleração, não falta forma

- Estado: **0,090/0,236** (viola só o pico); deriva β=+0,240 (a mais alta do
  diagnóstico — o modelo fica otimista no FIM).
- Fatos de mecânica (sonda F₀×slip): o dado **acelera** (p=−0,68) e o modelo
  **também acelera** (canal rotacional +0,51, via crescimento do slip na transição
  partial→gross — s_slip=+0,32, diferente do Chu que é slip-constante). O gap é
  **quantitativo**: o modelo entrega ~75 % da aceleração que o dado pede.
- Por que não há receita: é **1 curva** — qualquer constante de aceleração fitada
  nela é o "tuner com nome bonito" que o G-A3 proíbe; não existe leitor (L24) para
  taxa de aceleração. Transferência intra-fonte impossível (n=1).
- **Veredicto: form-limited documentado** — reabrir só junto com outra fonte que
  peça a MESMA aceleração de canal rotacional em transição partial→gross
  (candidata natural: Yang2019 abaixo). Exceção NÃO recomendada (o resíduo é de
  forma bem-posta, não de moldura/dado).

## 2. Yang2019 (2 curvas do núcleo) — dois problemas com nomes DIFERENTES

### 2a. `amp0p4_5Hz` — resposta graduada perto do limiar (mesma família do Yang2023 IJPEM)

- Estado: **0,100/0,142**; p_dado=−3,8 (aceleração fortíssima = regime de limiar);
  a sonda mediu o modelo com taxas +8 no fim — **o modelo bifurca** (stick→runaway)
  onde o dado **gradua**.
- É a MESMA forma nomeada no item 1 das "Formas novas" (Yang2023 IJPEM: dado exige
  N_L ∝ δ^−3,5…−3,8, tri-falsificação de nível já feita). **Consolidar as duas
  fontes num único candidato de forma** — "resposta graduada de limiar" — dá o que
  faltava ao FAIL2: **transferência cross-rig testável** (M10 Yang2019 ↔ M6/M8
  Yang2023, 1+7 curvas).

### 2b. `varamp_large_to_small` — carry-over de história entre blocos

- Estado: **0,052/0,136**; espectro grande→pequeno (`delta_spectrum`, input PR-12);
  β=+0,171 — depois do bloco de amplitude grande, o dado **continua perdendo** no
  bloco pequeno; o modelo **arresta**.
- Leitura física: falta o **estado carregado** do bloco 1 acelerar o bloco 2 — que
  é exatamente o acoplamento `surface_damage` (dano por dissipação de slip
  amplificando wear/µ) que o engine TEM e está **desligado** neste rig (c_D=0).
- Custo de testar: trio (c_D, W_ref, k_dmg_wear) per-rig = fit de 2-3 constantes
  numa curva só ⇒ mesmo problema do Karlsen. MAS há um desenho melhor: o par
  `small_to_large` vs `large_to_small` (2 curvas, MESMO rig, ordens opostas) dá
  **transferência intra-fonte**: fitar o trio numa ordem e prever a outra
  zero-refit. A `small_to_large` está metric-limited terminal (candidata a trim),
  então o desenho exige decidir ANTES como pontuá-la (trim-com-prova da
  ratificação → só então o par vira banco de teste).

## 3. O que muda na fila

1. **Karlsen**: form-limited documentado, sem receita, sem exceção — dorme até
   aparecer segunda fonte com a mesma assinatura.
2. **Limiar graduado**: Yang2019 amp0p4 JUNTA-SE ao item Yang2023-IJPEM (7+1
   curvas, 2 rigs) — o candidato de forma ganha o teste cross-rig que faltava.
3. **Carry-over varamp**: candidato damage-per-rig com desenho de transferência
   intra-fonte (par de ordens opostas), **bloqueado** pela decisão de trim da
   `small_to_large` (ratificação).
