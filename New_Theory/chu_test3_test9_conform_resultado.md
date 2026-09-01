# CHU test3/test9 — o `creep_conform_exp` abre as duas pernas do test3 e o MAE satura a 1,09×; a rota de leitura do emb NÃO existe no dado

**2026-08-21 (17:3x-17:5x)** · só-leitura · **nada adotado** · store
`c61366365977` · mandato *"continue e atualize o html quando chegar no tripé"*.
Continuação natural da investigação do test2 (17:1x): as 2 exceções CHU mais
próximas do censo eram test3 (σ 1,02×!) e test9 (MAE dentro, mx 1,05×).

## 1. test3 (`D0p5mm_F0_49kN`) — 0,0800/0,1139/0,0303

- **Shell canônico**: nenhuma constante isolada fecha; a única direção é
  `creep_conform_exp` (0→1,5 ⇒ 0,0564/0,0854/**0,0274** — mx e σ FECHAM).
- **Dose estendida satura**: e=2,0 ⇒ 0,0547; e=2,5 ⇒ 0,0538 — o MAE trava a
  **1,08–1,09×** e não desce mais.
- **Composição fecha, mas sem procedência**: conform 1,5–2,0 × emb_depth
  2,45–2,8 µm fecha as 3 pernas em **10 de 18 células**
  (melhor 0,0464/0,0737/0,0267). O C_creep é quase indiferente (3 doses
  fecham nas mesmas células — 1 DOF efetivo do par conform×emb).
- ⛔ **Escopo de GRUPO destrói as irmãs**: conform+emb no grupo inteiro
  derruba as D=1,0 do tripé (test5 0,0208→**0,1101**, test6 0,0279→0,0840)
  — saldo 3→2, rede **−1**. O emb de grupo não é uniformizável.
- ⛔ **A rota de leitura do emb morreu no dado**: o precedente T16 do LU
  (emb ancorado no c1 publicado) exige degrau de assentamento legível; o
  test3 começa em **1,0259** (acima de 1, ruído de digitalização) e desce
  gradual (74 ciclos → 0,9926) — **não há c1 de assentamento para ler**.
  O emb 2,45 µm seria fit puro per-case ⇒ a regra corta.

**Veredito test3**: quase-fecha estrutural — conform no rig (fitado-declarado
com região) deixa 1,09× no MAE; fechar exige 1 constante sem âncora.
A exceção em lei segue sendo o estatuto correto.

## 2. test9 (`Ra1p6um`) — 0,0459/0,1053/0,0549

Com conform 1,5–2,0 no grupo: 0,0542–0,0552/0,0900–0,0912/**0,0583–0,0587**
— o mx encosta (0,090) mas o **σ não responde** (1,86×→1,98×, piora). O σ do
test9 é a chegada em estágios (a mesma classe do test2, oscilação de fase).
Sem rota nova.

## 3. O que fica

1. `creep_conform_exp` ≈ 1,5–2,5 no rig CHU melhora **todas** as 5 D≤0,5
   sem quebrar as 3 do tripé (test5 paga 0,0208→0,0349, dentro) — mas
   **fecha zero** curvas sozinho ⇒ *melhoria sem fecho não adota* (regra).
   Fica registrado como componente para quando alguma outra peça fechar a
   última perna.
2. As 6 exceções CHU seguem corretas: test2 (teto de grade 1,24×, anatomia
   de fase), test3 (1,09× sem âncora restante), test9 (σ não responde),
   test4/7/8 (1,3–5×, prova em lei).

## Reprodutibilidade

Sondas inline com `rn._effective_overrides` embrulhado; limite σ da fonte
**0,0296** SEMPRE via `rh.limite_sres('CHU_2026', pisos)` (piso do par
válido 0,0432/0,0779/0,0296) — nunca de memória (5ª vez que a regra salva).
