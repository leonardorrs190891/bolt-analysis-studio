# `surface_damage` contra a classe — G0 FALHA (1 de 5) e fecha a busca no engine atual

**2026-08-01** · prereg `2026-08-01-damage-classe`. Último candidato:
o **único mecanismo do engine cujo fator passa de 1**.

## Pré-check (a regra do repo, aplicada antes do fit)

Alavanca multiplicativa é limitada pela fatia do canal que ela multiplica.
O dano amplifica **só o wear** (`d_wear ·= 1 + k_dmg_wear·D`). Fatia do
wear nas fontes da classe:

| fonte | wear | quem carrega de fato |
|---|---:|---|
| CHU_2026 | **63,9 %** | wear |
| SUN_2025_CRIMP | 1,5 % | rotacional 69 % |
| YANG_2019 | 1,0 % | embedding 56 % + creep 38 % |
| LIU_2025 | **0,0 %** | **fadiga 83 %** |
| JCSR_2023 | **0,0 %** | **creep 82 %** |

## G0 medido — confirma o pré-check ao dígito

| fonte | fim base | c_D=0,5 | c_D=2,0 | dado |
|---|---:|---:|---:|---:|
| CHU_2026 | 0,606 | **0,466** | **0,305** | 0,142 |
| YANG_2019 | 0,843 | 0,823 | 0,831 | 0,727 |
| JCSR_2023 | 0,601 | 0,601 | 0,601 | 0,729 |
| SUN | 0,048 | 0,048 | 0,048 | 0,111 |

**Age em 1 de 5** (gate exigia ≥3). No CHU o MAE até melhora
(0,1543 → 0,1275) — e é exatamente onde a grade de 54 pontos já
falsificou a dose única (`chu_veredicto_completo.md`). Nas outras quatro
o efeito é nulo ou negativo, **como o prereg previu por escrito**.

⇒ **G0 FALHA. Nada adotado.** Censo `129/205`, fingerprint intacto.

## O que fecha com isso (a conclusão estrutural do dia)

A classe "aceleração tardia" é real (7 fontes, 3 instrumentos) e **nenhum
mecanismo do engine atual pode atacá-la**:

1. **Toda a família de gates Hill** — `slip_onset`, `conformation`,
   `slip_regime`, `self_locking`, `crash_trigger` — tem contradomínio
   **(0, 1]**: só sabe atrasar, nunca acelerar (falsificado por
   construção, prereg anterior).
2. **O único amplificador** (`surface_damage`) multiplica um canal que
   está **morto em 4 das 5 fontes** da classe.

**Não é falta de calibração nem de tentativa: é falta de mecanismo.**

## A especificação que sai daqui (para o PR-3 do professor)

A forma que serviria tem três requisitos, todos medidos hoje:

1. **Amplificar** (fator > 1), não gatear;
2. governada por **estado acumulado** (o defeito é tardio, não inicial);
3. agir sobre o **canal dominante de cada fonte** — e ele MUDA: wear no
   CHU, rotacional no SUN, embedding+creep no YANG_2019, fadiga no
   LIU_2025, creep no JCSR. Um amplificador amarrado ao wear (como o
   dano de hoje) nasce inerte em 4 dessas 5.

Isso é uma decisão de física do modelo, não de calibração — **fica na sua
mesa**. O caminho barato alternativo continua sendo dado de bancada.
