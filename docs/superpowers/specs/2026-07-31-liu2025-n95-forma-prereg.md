# Prereg — forma N₉₅ do LIU_2025 (relógio de assentamento cego à amplitude)

**2026-07-31 (noite)** · Bloco 1 do `plano_tripe_restante.md` (aprovado:
"concordo"). Gates escritos ANTES de qualquer fit. Instrumento e
decomposição já medidos (só-leitura, nesta sessão):

## O defeito, MEDIDO (fingerprint `3d432a65c7e8`)

| amplitude | N₉₅ dado (Fig. 4 D-N do paper) | N₉₅ modelo (store) | razão |
|---:|---:|---:|---:|
| 0,25 | 16.157 | 108 | 150× cedo |
| 0,30 | 13.516 | 108 | 125× cedo |
| 0,40 | 9.099 | 108 | 84× cedo |
| 0,50 | 2.745 | 108 | 25× cedo |
| 0,60 | 460 | 108 | 4,3× cedo |
| 0,80 | 19 | 108 | **5,9× TARDE** |

**O N₉₅ do modelo é CONSTANTE (~108) onde o dado varre 850×.** Não é
adiantamento uniforme — é relógio **cego à amplitude**: a inclinação
d(N₉₅)/d(amp) do modelo é ~0. Decomposição em 0,25 mm: perda de 11 % já em
N=2.000, **59 % embedding + 41 % creep** — os dois relógios de estágio I
correm à velocidade plena em amplitude baixa.

Sonda de direção executada: `emb_slip_gate` puro é **INERTE** aqui (Δ=0
exato) — ele gateia só o reservatório `emb_load_frac`, que o config
adotado tem = 0. O reservatório de profundidade tem alvo ρ-escalado
(`emb_amp_exp`) mas relógio `N_emb` fixo; o creep (`C_creep` log-t) é
100 % cego à amplitude.

## Âncora (ler, não fitar as curvas da fila)

A **Fig. 4 D-N (N₉₅ por amplitude, 6 pontos M16)** é dado do paper
independente das 4 curvas da fila — é ELA que o relógio novo tem de
reproduzir. As curvas da fila (amp0p25/0p3/0p8/fig2) ficam como
**held-out**: nenhum parâmetro é escolhido olhando o MAE delas.

## Candidatos (ordem de legitimidade; A não muda engine)

- **A. Re-parametrização per-rig com campos EXISTENTES** (padrão da
  adoção LU): mover o assentamento de 0,25 mm do reservatório de
  profundidade para o fracional slip-gated — `emb_um`↓, `emb_load_frac`>0
  + `emb_slip_gate`>0 (bedding vibração-dirigido §4.29) — e/ou onset de
  creep `t_0` (padrão ZHANG_2018, lível do resíduo). Fit de ≤3 números na
  D-N (6 pontos), zero olhada na fila.
- **B. Forma de engine (creep slip-gated)** — só se A não alcançar a
  inclinação; vira PR-3 com spec própria (o creep amplitude-dependente
  não existe no engine e a decisão é do professor).

## Gates (imutáveis)

- **G1 (alcance)**: o candidato A, com ≤3 parâmetros fitados NA D-N,
  reproduz a inclinação: N₉₅ do modelo dentro de **3×** do dado em ≥4 das
  6 amplitudes (hoje: 0 das 6; o pior erro é 150×). Falhou ⇒ ramo B
  (relatório, sem adoção).
- **G2 (held-out)**: com os números do G1 congelados, as 4 curvas da fila
  melhoram em conjunto: soma dos MAE cai ≥20 % E nenhuma das 4 piora
  >+0,01 em qualquer perna.
- **G3 (nenhum caso pior)**: as 7 curvas da fonte em tripé/estatuto
  (incl. E2/fadiga) não pioram >+0,01 em nenhuma perna; fora da fonte,
  nada muda (config per-rig).
- **G4 (procedência)**: cada número adotado com origem declarada (D-N do
  paper; resíduo; handbook) — nenhum "fitou porque coube".
- **G5 (sincronia)**: adoção ⇒ batch re-stamp uniforme + exemplo_m12
  direto + censo/_VIVAS/docs/páginas no mesmo commit.
- Ramo **INCONCLUSIVO** declarado: se a D-N e as curvas discordarem do
  N₉₅ (definições de F₀ de referência), o teste não testou — documentar e
  parar.

## Previsão registrada (falsificável)

Com bedding slip-gated + t_0 de creep, o N₉₅ em 0,25 mm sobe ordens de
grandeza (o gate (slip/(slip+δt))^q com slip pequeno em 0,25 mm suprime o
reservatório fracional; t_0 desloca o joelho do creep). O risco declarado:
a ponta de 0,8 mm exige N₉₅ MENOR que o atual (19 vs 108) — o candidato A
precisa ACELERAR o relógio em amplitude alta (emb_load_frac com gate
próximo de 1 lá) sem quebrar o E2/fadiga; se as duas pontas não fecharem
juntas, G1 falha e o veredicto é "forma B necessária".
