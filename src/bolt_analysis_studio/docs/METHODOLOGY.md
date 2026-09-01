# Metodologia de Evolução do Modelo (MEM) — Runbook

**Rev.:** 2026-07-10 (v1) · **Spec:** `docs/superpowers/specs/2026-07-10-model-evolution-methodology-design.md`
· **Objetivo:** reduzir o erro do modelo canônico contra os dados experimentais
de forma sistemática, auditável e sem overfitting.

---

## 0. Princípios inegociáveis

1. **O erro é medido no CANÔNICO** (o que o software mostra: bloco `shared` +
   `adopted_configs.json`), nunca no experimento da campanha.
2. **Pisos de repetibilidade são limite físico** — erro ≤ piso+0.02 não se
   persegue (perseguir seria fitar ruído do próprio dado).
3. **Campanhas ESCREVEM os JSONs; o software LÊ** (`knowledge_base`). Nunca
   duplicar valor em código.
4. **Formas transferem entre bancadas; constantes não** (lição central da
   biblioteca, MODEL_LEGITIMACY §8) — constante é per-rig/per-par com classe
   de procedência; forma nova só entra por falsificação pré-registrada.
5. **Otimização per-paper é legítima e esperada** (diretriz do professor,
   2026-07-10): atrito, rigidez, amortecimento e demais parâmetros variam de
   paper para paper — otimizá-los por bancada é parte do método, DENTRO da
   disciplina de DOF (poucas constantes, cada uma com classe de procedência,
   gate de medição por fonte, e leitura-do-dado antes de fit). Dispositivos
   físicos declarados no paper (travamento, lubrificação, protocolo) entram
   como grupos `FONTE_token` com a física do dispositivo mapeada nas
   variáveis MSD (ex.: wedge-cam ⇒ rotação suprimida — caso Vibralock).

## 1. O ciclo (uma iteração = uma campanha)

```
0 BASELINE ─▶ 1 ORÇAMENTO DE ERRO ─▶ 2 ALAVANCA ─▶ 3 GUARD-RAILS ─▶ 4 PARADA? ─▶ 5 ADOÇÃO+REGISTRO ↩
```

### Nota — as duas réguas do ledger

O `convergence_ledger.json` tem DUAS bases de medição, marcadas no campo
`basis` de cada entrada: até #33, a **fronteira experimental da campanha**
(galeria, melhor config por caso, subconjunto); de #34 em diante, o
**canônico adotado** sobre os 114 comparáveis (a régua da MEM). O degrau
entre as séries É o gap de adoção — nunca comparar números de bases
diferentes. Toda entrada nova deve declarar `basis`.

### Etapa 0 — Baseline
```bash
python -m bolt_analysis_studio.validation.report --all    # batch canônico (~10 min)
```
Métricas no mestre: mediana/média global, por família, por fonte, fração no
piso. Fingerprint do engine carimba tudo.

### Etapa 1 — Orçamento de erro
```bash
python -m bolt_analysis_studio.validation.error_budget
```
Cada caso fora do piso recebe UM rótulo dominante (heurísticas auditáveis;
tabela "Orçamento de erro (MEM)" no report mestre):

| Rótulo | Significado | Alavanca indicada |
|---|---|---|
| `no_piso` | mae ≤ max(piso+0.02, 0.10) | nenhuma (não perseguir) |
| `gap_adocao` | campanha já resolve ≫ melhor que o canônico | promoção (Etapa 2.2) |
| `nivel` | resíduo de um sinal só (curva certa, deslocada) | constante/input per-rig |
| `forma` | resíduo cruza zero / estágio dominante errado | funil de falsificação |
| `sem_simulacao` | família sem carregamento parametrizado | fora do orçamento |

### Etapa 2 — Alavancas em ordem de legitimidade
1. **Procedência de input** (custo 0 DOF): `assumed` → paper para µ, grip,
   Rz, F_amp/F₀ (µ primeiro — domina o OAT §4.42). Fonte: notas de aparato.
2. **Promoção ao adotado** — regras da §2 abaixo.
3. **DOF per-rig legítimo**: `c_bend` no transversal (fit 1-D); `emb_depth`
   e `loose_arrest_floor` **lidos** da curva (leitores de
   `calibration.provenance`); axial: **nada fitado**.
4. **Forma nova SÓ por falsificação pré-registrada**: predição-primeiro,
   gate escrito ANTES de rodar, implementação default-inerte, adoção =
   decisão do professor (separada da validação).
5. **Âncora experimental** para constante órfã (W_conf_ref, tr_loose_gain).

### Etapa 3 — Guard-rails (invariantes de toda iteração)
Identificabilidade (nunca fitar pares K/H-like); LOCO por fonte quando um
fit compartilhado muda; parcimônia forward-selection (tol 0.005);
conservação de energia ≈ 0 (fora de colapso agressivo); contagem honesta de
DOF (`knowledge_base.dof_summary`).

### Etapa 4 — Parada
(a) todo caso ≤ max(piso+0.02, 0.10); OU (b) Δ(média global) < 0.002 por 3
iterações do ledger → mínimo global operacional. Só formas novas/âncoras
reabrem o ciclo.

**Meta permanente por curva (professor, 2026-07-14):** além do MAE, o
**resíduo assinado (modelo − artigo) deve ficar |<0.10| em TODOS os pontos**
de cada plot (`maxerr < 0.10` do runner, computado na grade do dado pós-trim
e alinhamento) — e o σ dos resíduos assinados (`resid_std`, PR-25) deve ser
minimizado (erro ~constante ao longo da curva, sem "reta atravessando
curva"). O tripé por curva é: MAE ≤ 0.10 **E** maxerr < 0.10 **E** resid_std
baixo. Gates de PRs novas devem testar as três; o ledger acompanha
`n_maxerr_above` (curvas com maxerr>0.10; estado no #48: 110/178 —
base-114: 52, R4: 58) e os reports mestre/all_plots exibem `res.máx` por
caso com a meta.

### Etapa 5 — Adoção e registro
Hash no bloco canônico; §4.x no `MODEL_LEGITIMACY.md`; entrada no
`convergence_ledger.json`; reports regenerados (o fingerprint muda →
staleness avisa em todos os casos).

## 1b. Operação contínua (diretiva do professor, 2026-07-14)

A campanha roda **autônoma e continuamente** ("sem que seja necessário eu
interferir"): o programa durável está em `New_Theory/AUTONOMOUS_CAMPAIGN.md`
(protocolo por iteração, ordem de alvos, regras operacionais, parada). O que
o §2 reserva ao professor (formas novas de engine, adoções de escopo) NÃO
bloqueia o loop: acumula com diagnóstico em `New_Theory/DECISOES_PENDENTES.md`
e a campanha segue nos alvos alcançáveis por condição/constante. Cada
iteração fecha com ledger + reports + commit + resumo legível no chat.

## 2. Regras de promoção (campanha → canônico)

| Classe de procedência | Exemplos | Promove? |
|---|---|---|
| `lido-do-dado` (feature medida identificável) | emb da queda inicial; floor do platô; W_crit no joelho | **SIM** — direto, com a regra de leitura registrada |
| `fitado-this-rig` no DOF legítimo | c_bend (transversal); C_creep **por par** (§4.7) | **SIM** — constante per-rig/per-par etiquetada |
| `input de paper/estudo` | grip/µ/Rz da nota de aparato; µ por estado de lubrificação | **SIM** (é input, não fit) |
| fit per-curva SEM feature identificável | multiplicador ad-hoc; timing solto | **NÃO** — fica experimental (rotular o resíduo com o motivo) |
| forma nova | gate de falsificação PASSOU + default-inerte | **decisão do professor**, caso a caso |

Toda promoção entra no `adopted_configs.json` com bloco
`"prov": {constante: classe}` e justificativa no `verdict`. Configs por
GRUPO usam chave `FONTE_token` (o token deve aparecer no id do caso —
ex. `BAUER_2024_fig8_test1`).

## 3. Onde olhar

- Report mestre: menu *Validation Gallery* (V1) ou Results→Validation (V2) —
  seções "Orçamento de erro (MEM)" e "Convergência (ledger)".
- `Models/CALIBRATION_AND_VALIDATION/error_budget.json` — o orçamento cru.
- `New_Theory/convergence_ledger.json` — a história das iterações.
- `MODEL_LEGITIMACY.md` — o registro de física (falsificações, adoções).

## 4. Histórico

- **Iteração 1 (2026-07-10, Sprint de Adoção):** baseline canônico mediana
  0.181 vs campanha 0.042 (35 casos no gap). Promoções por classe — ver
  `docs/superpowers/plans/2026-07-10-mem-iteration-1-STATUS.md` (números
  antes/depois, o que não foi promovido e por quê).
