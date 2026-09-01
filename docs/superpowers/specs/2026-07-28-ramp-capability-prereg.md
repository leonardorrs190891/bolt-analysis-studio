# Pré-registro — RAMPA DE FRATURA como capacidade do engine (Opção A/A1)

**Data:** 2026-07-28 · **Escolha de arquitetura:** delegada pelo professor
(*"escolha a opção que você recomendar"*) e decidida por medição —
`New_Theory/liu2025_rampAB_resultado.md`: **Opção A com energética por incremento**.
**Status:** PROPOSTO, CONGELADO — **implementação NÃO autorizada ainda** (o professor
gateou implementação duas vezes; executar este prereg = a autorização que falta).
**Fingerprint vigente:** `4f5bedfbace4` (203 casos).

---

## 1. O que será construído (e só isso)

Estender `FatigueLoss` com uma **descarga em rampa** opt-in, no lugar do cliff de
1 ciclo, reusando o estado `D_fatigue` que o Miner já acumula:

```
campos novos em JointMaterial (todos default-inertes):
  fat_ramp_D_on: float = 1.0    # 1.0 = SEM rampa => cliff de hoje, bit-idêntico
  fat_ramp_q:    float = 5.0    # expoente da rampa (só lido se D_on < 1)

física (a MESMA da sonda validada, B1 do prereg v1):
  para D_on < 1 e D_fatigue > D_on:
    α     = min(((D − D_on)/(1 − D_on))^q, 1)
    g(D)  = (1−α)(1+ρ)/((1−α)+ρ),  ρ = k_j/k_b        [liberação série bolt–junta]
    dF_0  = F_0·(g(D₁)/g(D₀) − 1)  ≤ 0
    dE    = U_internal(antes) − U_internal(depois)      [rota do cliff: W_diss_fracture]
```

**Não** se toca em: `geom` (nada de `k_b` dinâmico — Opção B morta por medição),
`Φ`, `k_tr`, conversores dos outros mecanismos, métrica, trims, store schema.

## 2. GATES (imutáveis depois de assinados) — contas MEDIDAS pela sonda A/B

**P0 — inércia total.** Defaults (`fatigue_enabled=False`; e `=True` com
`fat_ramp_D_on=1.0`) reproduzem o store `4f5bedfbace4` **bit a bit** (203 casos).
*Conta:* `D_on=1.0` torna a condição `D > D_on` inalcançável antes de `D ≥ 1`, onde o
cliff de hoje dispara — caminho de código idêntico por construção. ✔

**P1 — paridade com a sonda validada.** Com relógio neutralizado para reproduzir o da
sonda (Goodman desligado via `fat_sigma_uts` alto + `fat_C1` ancorado tal que
`N_f = N_f(paper)` exato), o engine reproduz os cruzamentos da variante **A1** da sonda
em ±1 ciclo nos 4 casos. *Conta (medida, é a tabela do resultado):* amp0p4
+1554/−125/−477/−489/−505 · amp0p5 +801/+138/−260/−506/−498 · amp0p6
−2954/−2729/−1274/−771/−605 · fig2 fino +1871/+296/−33/−30/+43. ✔ por construção
(mesma fórmula, mesmo D linear) — o gate pega deriva de implementação.

**P2 — o cliff adotado não se move.** `LI_2022_TRIBOINT` (única fonte com
`fatigue_enabled=True` no canônico) re-simulada: métricas **bit-idênticas**.
*Conta:* default `fat_ramp_D_on=1.0` ⇒ ramo novo nunca entra. ✔

**P3 — conservação.** Com a rampa ativa nos 4 casos da sonda, residual de conservação
`|res| ≤ 0,2 J`. *Conta medida (A1):* 0,148 / 0,089 / −0,151 / −0,017 J. ✔ com margem;
o pior caso admitido pelo escopo é o próprio conjunto de 4 (não há cláusula condicional).

**P4 — a curva inteira aparece no software.** O Run (GUI) gera a curva em S completa do
`fig2` (10 k ciclos, dentro do `_CAP=100000`) com `_v2_tuner_overrides` carregando os
campos `fat_*` — que **já passam** pelo filtro `__dataclass_fields__` (verificado).
As duas curvas lentas (250k/330k) ficam **explicitamente fora deste gate** — dependem
da decisão pendente do `_CAP` (fila, item do professor).

**P5 — informacional (não-gate).** Primeira medição da fidelidade dos relógios
emergentes: `N₉₅` e `N_D` do engine vs dado, nas 7 curvas. Números novos, sem limiar.

**P6 — nenhuma curva de fora piora.** As 196 restantes: Δ = 0 exato (a capacidade é
opt-in e nenhum config adotado a liga nesta execução). Nada é adotado; adoção per-rig
do LIU_2025 (com `fat_C1` ancorado no contexto canônico, Goodman vivo — efeito ~50 %
medido) é **prereg separado**.

### Interpretação pré-declarada

| resultado | leitura |
|---|---|
| P0–P4, P6 ✓ | capacidade mergeável; adoção LIU_2025 vira decisão seguinte |
| **P1 ✗** | a implementação derivou da sonda ⇒ consertar sem reinterpretar |
| **P2 ✗** ou **P0 ✗** ou **P6 ✗** | quebra de inércia ⇒ PARA, reverte |
| **P3 ✗** | energética errada ⇒ consertar a rota de `dE`, não relaxar o limiar |

## 3. Reprodutibilidade

```bash
py -3.12 -m pytest tests/ -q            # + P0/P2 via parallel_batch --store em cópia
py -3.12 New_Theory/liu2025_rampAB_probe.py    # referência de paridade (A1)
```
