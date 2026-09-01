# PREREG — `chu2026ti_D0p4mm_F0_49kN_test2`: incubação + dano agnóstico — a 1ª exceção da prova-em-lei cai

**2026-08-21 (10:1x-10:3x)** · **gates congelados neste commit** · mandato das
10:12: *"ataque chu2026ti_D0p4mm_F0_49kN_test2"*.

## 1. Por que este ataque é legítimo contra a prova de 5 degraus

A prova do CHU (assinada 2026-08-14) falsificou **4 famílias estado-dirigidas
nomeadas** (k_wear uniforme, running-in, ratchet, onset×chute-tardio) e as
rotas de µ. O pacote daqui usa DUAS peças que **não estavam** na prova:
`slip_onset_W` (incubação — o gate Hill de 2026-07) e **`k_dmg_all`**
(amplificador tardio AGNÓSTICO de canal, PR-3 de 08-01, DORMENTE desde então
— criado exatamente para "o dado desaba no fim 2–225× mais rápido que o
modelo"). A prova continua válida para o que ela falsificou.

## 2. Anatomia e classe (medidas)

Dado: platô até ~160 ciclos → **aceleração contínua** (taxa 0,0004→0,0012/c,
ρ(res,N)=0,95) até 0,142 sem arresto. Modelo: desacelerante (wear Archard
dominante 0,265 — taxa ∝ µF·slip CAI com F). Classe mecânica instrumentada:
**GROSS SLIP total** (slip 398 µm = 2,0× δ/2, 100 % dos ciclos) ⇒ o gth é 0
por construção (stick-only) e o canal rotacional está morto (0,0055) — o
runaway não alcança. A única alavanca de aceleração que alcança é a agnóstica.

## 3. Pacote (per_case `test2` no grupo CHU_2026 — token colisão conferida)

| campo | valor | procedência |
|---|---|---|
| `slip_onset_W` | **4500 J** | ancorado no platô de ~160 ciclos (W/c ≈ 28 J em gross slip) |
| `slip_onset_sharpness` | 8 | fitado leve (default 4) |
| `k_dmg_all` | **9** | FITADO (região) |
| `c_D` / `W_ref` | 2,0 / 10 000 | **starters físicos DOCUMENTADOS** do damage (CLAUDE.md: "Damage physical starters: c_D=2, W_ref=1e4") |

Contagem: 2 fitados (k_all, sh) + W ancorado + 2 starters documentados.
Sandbox: 0,1567/0,5259/0,1909 → **0,0430/0,0827/0,0374 — FECHA** (limite σ da
fonte 0,0507). Região: **7 células conexas** (W 4300–4600 × k_all 8–10);
célula por centralidade 3/4 + pior perna 0,86×. G2 sandbox: **todas as irmãs
CHU bit-idênticas** (só o test2 no diferencial).

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito | 0,0430/0,0827/0,0374 pelo canônico — FECHA |
| **G2** | irmãs CHU bit-idênticas | |
| **G3** | isolamento Δ=0 fora do CHU no re-stamp; fingerprint único nos 210 | |
| **G4** | censo | 167 → **168/205 (82 %)** · exceções 22 → 21 (retirada por mérito da F5 do test2; a prova de 5 degraus SEGUE válida para as 5 irmãs — nota na retirada) |
| **G5** | ledger DOF | `k_dmg_all` SAI dos dormentes (1ª adoção; a guarda `_sem_dof_fitado` exigirá) |
| **G6** | sincronização | docs · triagem · aging · HTML |

## Estado

REVERTIDO 2026-08-21 (10:5x) — REPROVOU no gate de censo. O G1 bateu ao
digito (0,0430/0,0827/0,0374) mas o "FECHA" do prereg usava o limite sigma
ERRADO: escrevi 0,0507 de memoria e o limite REAL da fonte e **0,0296**
(apertado pelo bloqueio G/H de 08-14, que invalidou a familia delta=0,5 que
inflava o piso). O sigma 0,0374 = 1,27x NAO fecha, e NENHUMA celula da grade
fecha 0,0296 (piso da grade: 0,0366). 4a ocorrencia do erro "limite de
memoria em vez do helper" — desta vez ATRAVESSOU um prereg congelado, e o
que o pegou foi o gate de censo (168 previsto, 167 medido). Reversao
completa: per_case removido, excecao F5 restaurada com a nota do ataque,
k_dmg_all de volta aos dormentes, re-stamp de reversao. A MELHORIA
(3,6-6,4x) fica registrada como rota parcial: a incubacao ancorada + dano
agnostico e a melhor aproximacao ja medida do test2, e o que falta para
fechar e sigma 0,0374 -> 0,0296 (26%).

CONTINUACAO na mesma hora (mandato "continue", 10:53-11:0x): duas familias a
mais varridas atras do sigma — o RELOGIO do damage (c_D 1-4 x W_ref 6-16k:
minimo 0,0374, a crista nao cede) e emb/creep LIDOS per_case (emb 0,5 +
C_creep 0, precedente test1: PIORA — o trade-off dos 3 trechos do residuo e
CIRCULAR, consertar o inicio move o meio e o fim). O sigma trava em 0,037+
em TODAS as familias. VEREDITO: a prova em lei do CHU RESISTE ao arsenal
completo do arco 19-21/08 — fica registrado como o 6o degrau da prova
(incubacao ancorada + dano agnostico chegam a 1,27x do limite e travam na
curvatura que "onset/chute funcao explicita de (D,F0)" ja nomeava). O test2
segue excecao com a rota parcial anotada.
