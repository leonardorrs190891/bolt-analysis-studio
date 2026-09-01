# ICMEZ_2025 — as 5 abertas não são "indecidíveis": o modelo **trava num piso que o dado atravessa**, e a forma que falta tem nome

**2026-08-15 (noite)** · store `20be19aabe11` · sondas **só-leitura** (sandbox
`BAS_ADOPTED_CONFIGS`) · **nada adotado** · 26 células medidas em 6 famílias de
alavanca, todas falsificadas.

## Por que esta fonte, e por que agora

A triagem publica **fila form-limited = 0**, e as 5 abertas do `ICMEZ_2025`
estavam na camada **`indecidivel_sem_piso`** — rótulo que descreve a
impossibilidade de **desculpá-las** (a fonte perdeu o piso de réplica no
bloqueio G de 08-14, porque as famílias pareavam `grip` 13,8 × 19,8 mm). Mas
"sem piso" **não** é "sem defeito diagnosticável": ninguém havia perguntado se
elas têm **rota de conserto**. Têm — e o diagnóstico é estrutural.

## 1. O dado é limpo: o σ é do MODELO, não do ruído

| curva | σ_res | ruído (2ª dif.) | σ/ruído | monotonia |
|---|---:|---:|---:|---|
| amp0p3_F14p3_lk13p8 | 0,0428 | 0,0057 | **7,5×** | exata |
| amp0p3_F14p3_lk19p8 | 0,0343 | 0,0030 | **11,5×** | exata |
| amp0p3_F17p6_lk13p8 | 0,0436 | 0,0051 | **8,6×** | exata |
| amp0p3_F17p6_lk19p8 | 0,0292 | 0,0020 | **14,5×** | exata |
| amp0p4_F17p6_lk13p8 | 0,0357 | 0,0061 | **5,9×** | exata |

Resíduo isotônico **0,0000** nas 8 (a digitalização é monotônica por
construção). ⇒ a hipótese *data-limited* está **descartada com número**: o
σ_res é 6–15× o ruído do próprio dado.

## 2. A anatomia: resíduo em "U" idêntico entre condições

Resíduo médio por terço (`pred − dado`; **+** = modelo retém demais):

| curva | início | meio | fim |
|---|---:|---:|---:|
| amp0p3_F14p3_lk13p8 | −0,013 | **−0,077** | +0,002 |
| amp0p3_F14p3_lk19p8 | −0,012 | **−0,078** | −0,044 |
| amp0p3_F17p6_lk13p8 | −0,002 | **−0,079** | −0,014 |
| amp0p4 (as 4) | +0,001…+0,033 | −0,022…+0,010 | +0,002…+0,059 |

O **−0,077 ± 0,001** nas três primeiras — através de `F_amp` (5720 × 7040 N) e
de `grip` (13,8 × 19,8 mm) — é assinatura de **mecanismo**, não de ajuste de
curva.

## 3. A trajetória mostra o mecanismo a olho nu

`amp0p3_F14p3_lk13p8` (dado × modelo):

| N | 100 | 120 | 140 | 160 | 175 |
|---|---:|---:|---:|---:|---:|
| dado | 0,415 | 0,354 | 0,304 | 0,260 | **0,228** |
| modelo | 0,356 | 0,321 | 0,305 | 0,297 | **0,292** |

O modelo **achata em ~0,29** e para; o dado segue caindo a taxa quase
constante. O número 0,29 não é coincidência: o `loose_arrest_floor` **adotado**
nesta fonte é **0,308** (PR-13, `fitado-this-rig`).

## 4. Medido NO SÍTIO (não inferido): o gate morre

Instrumentando `self_locking_gate` (o próprio site de chamada):

| curva | N=1 | ~50 % | ~75 % | fim |
|---|---:|---:|---:|---:|
| `amp0p3_F14p3_lk13p8` (dado 0,228 < piso) | 0,692 | 0,218 | 0,011 | **0,0000** |
| `amp0p3_F17p6_lk19p8` (dado 0,549 > piso) | 0,692 | 0,557 | 0,481 | 0,378 |

⇒ na 1ª o canal rotacional está **morto** no último quarto do ensaio; na 2ª
segue vivo. **Taxas medidas** (queda por 100 ciclos, fim ÷ meio):

| grupo | dado | modelo |
|---|---:|---:|
| 4 curvas cujo dado passa **abaixo** do piso | 0,48–0,57 | **0,18–0,26** |
| 4 curvas que ficam **acima** | 0,61–1,09 | 0,59–0,74 |

Separação perfeita: onde o dado cruza o piso, a taxa tardia do modelo colapsa a
~1/5 da sua própria taxa de meio, enquanto o dado mantém ~1/2.

## 5. Seis famílias de alavanca, 26 células, todas falsificadas

| # | candidato | células | resultado |
|---|---|---:|---|
| 1 | `N_emb` ↑ (relógio de assentamento — precedente T7/YANG_2019) | 2 | tripé 3/8 → **1/8 → 0/8** |
| 2 | `k_wear_scale_tr` ↑ (canal linear em N) | 2 | U **aprofunda** (−0,041→−0,048); tripé 3→3→**2** |
| 3 | `k_late_amp` × `crash_trigger_frac` (amplificador tardio, PR-3) | 6 | **0/8**, MAE mediano ×7–12 (0,033→0,40) |
| 4 | `loose_arrest_floor` ↓ (0,20/0,10/0,0) | 3 | **runaway**: 0/8, MAE 0,064/0,112/0,162 |
| 5 | piso ↓ **+** `loose_kin_ceiling` (transição gradual) | 9 | melhor **2/8** (pior que o baseline 3/8) |
| 6 | `tr_loose_gain` ↓ **+** piso ↓ | 4 | **0/8**; e `gain=0,5` deu resultado **idêntico** com piso 0,15 e 0,22 ⇒ *parâmetro morto* (o modelo nem chega ao piso) |

## 6. A forma que falta, nomeada

O canal rotacional do engine é **binário**: ou **arresta** no piso
(`self_locking_gate → 0`, ponto fixo estável) ou, com piso 0, entra em
**runaway** (`T_resist ∝ F_0` ⇒ colapso). O `ICMEZ_2025` exige o **meio-termo
que não existe**: afrouxamento **sustentado sub-arresto** — o dado atravessa o
limiar de auto-travamento e continua caindo a ~50 % da taxa de meio, sem
acelerar e sem parar.

⇒ **as 5 abertas são form-limited com forma nomeada**, não indecidíveis.

## 7. Audit campanha-wide: o piso do ICMEZ é o ÚNICO fitado que o dado falsifica

Comparando, **por curva** (via `config_used`, o que o engine de fato aplicou), o
piso aplicado com o último ponto do dado — 15 curvas passam abaixo do piso, mas:

- **14 delas por ≤ 0,005** (ECCLES ×5, SUN ×4, CHU test1): são pisos **lidos do
  dado** (leitor L24 `arrest_floor_from_curve`), pousados no platô final. O
  dado **faz platô** ali. Legítimos — e este audit é uma **validação positiva**
  do leitor.
- **as 5 do ICMEZ por 0,009 a 0,085** (até 38 % da pré-carga restante), com
  `prov = "PR-13 fitado-this-rig"` — piso **fitado**, não lido —, e o dado
  **não faz platô** (taxa tardia 0,48–0,57 da de meio).

⇒ a regra que isto sugere, e que vale além desta fonte: **piso de arresto só é
legítimo se o dado da própria curva PLATEAR nele**; piso fitado acima de um
dado que segue caindo é uma barreira artificial.

## 8. O que NÃO fazer (e por quê)

Baixar o piso do ICMEZ sem a forma nova **piora tudo** (0/8, MAE ×5): o
"conserto óbvio" troca uma barreira artificial por um colapso artificial. A
correção honesta exige a forma do §6 — construir, pré-registrar e gatear.

## 9. Reprodutibilidade

Sondas no scratchpad da sessão `3d12ac81` (instrumentação de
`self_locking_gate` e `resolve_transverse_slip`; grades das 6 famílias).
Sanidade de todas: célula vazia reproduz o store ao dígito.
