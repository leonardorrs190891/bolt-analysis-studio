# Metodologia de Evolução do Modelo (MEM) — Design

**Data:** 2026-07-10 · **Status:** aprovado pelo professor (alvo: gap de
adoção primeiro; entrega: doc vivo + tooling)

## 1. Pedido (professor, verbatim)

"Vamos criar uma metodologia para evoluir nosso modelo e diminuir o erro ante
aos dados teóricos. Seja refinando variáveis, condições de contorno da
simulação, ou outras sugestões que tiver."

## 2. Baseline (medido 2026-07-10, engine canônico)

| Fronteira | mediana MAE | média | n |
|---|---:|---:|---:|
| Canônico adotado (o que o software mostra) | 0.181 | 0.212 | 114 |
| Melhor da campanha (galeria; ledger 33 iterações) | 0.042 | 0.052 | 78 |

**35 casos** concentram o gap (canônico ≫ campanha). Conclusão de partida: a
maior redução disponível é **fechar o gap de adoção com disciplina de
procedência** — o modelo já demonstrou ~0.05; o processo de promoção é o
gargalo. Física nova entra depois, pelo funil de falsificação.

## 3. O ciclo MEM (uma iteração = uma campanha)

```
0. BASELINE congelado ──▶ 1. ORÇAMENTO DE ERRO ──▶ 2. ALAVANCA (hierarquia)
        ▲                    (classificar antes         │
        │                     de mexer)                 ▼
5. ADOÇÃO+REGISTRO ◀── 4. PARADA? ◀── 3. GUARD-RAILS (aplicar c/ gates)
   (hash, §4.x, reports)
```

**Etapa 0 — Baseline congelado.** Erro medido SEMPRE no canônico
(`validation_store` + fingerprint), nunca no experimento. Métricas: mediana/
média global, por família, por fonte, fração no piso de repetibilidade.
Pisos medidos (FLOORS) = limite físico: erro ≤ piso+0.02 **não se persegue**.

**Etapa 1 — Orçamento de erro** (ferramenta `error_budget`). Cada caso fora
do piso recebe UM rótulo dominante, POR HEURÍSTICA AUDITÁVEL, antes de
qualquer mexida:
- `no_piso` — mae ≤ max(piso+0.02, 0.10);
- `gap_adocao` — galeria existe e canônico > max(2×galeria, galeria+0.05);
- `nivel` — resíduo de um sinal só e estágios ~uniformes (curva certa,
  deslocada) → alavancas de constante/input;
- `forma` — resíduo cruza zero ou estágio II ≫ demais (forma errada) →
  candidato a falsificação/forma;
- `input_assumido` — sub-rótulo: nº de inputs com proveniência `assumed`
  (µ/grip/Rz/F_amp), ponderado pela sensibilidade OAT (§4.42: µ domina);
- `sem_simulacao` — família `other`/erro (fora do orçamento).
Saída: `error_budget.json` (por caso) + tabela agregada por fonte no report
mestre ("onde está o erro") + painel do ledger de convergência.

**Etapa 2 — Alavancas em ordem de legitimidade** (só desce na lista quando a
de cima esgotou para o caso):
1. **Procedência de input** (custo 0 DOF): assumed→paper para µ, grip, Rz,
   F_amp/F₀ (voltar às notas de aparato/paper; µ primeiro).
2. **Promoção ao adotado** (regras da §4 abaixo) — fecha `gap_adocao`.
3. **DOF per-rig legítimo**: c_bend no transversal (fit 1-D, o prefit já
   implementa), emb/floor **lidos** da curva; axial: nada fitado (§4.42).
4. **Forma nova SÓ por falsificação pré-registrada**: predição-primeiro,
   gate escrito antes de rodar, implementação default-inerte, validação
   separada da adoção (decisão do professor).
5. **Âncora experimental** para constante órfã (W_conf_ref: experimento de
   fretting spec'd; tr_loose_gain = alvo #1 de procedência).

**Etapa 3 — Guard-rails** (invariantes de toda iteração): identificabilidade
(nunca fitar pares K/H-like); LOCO por fonte quando um fit compartilhado
muda; parcimônia forward-selection (tol 0.005); conservação de energia
(residual ≈ 0 fora de colapso agressivo); contagem honesta de DOF
(`dof_summary`); nunca perseguir erro < piso.

**Etapa 4 — Parada** (critérios do indicador existente): (a) todo caso ≤
max(piso+0.02, 0.10); OU (b) Δ(média global) < 0.002 por 3 iterações do
ledger. Atingido → mínimo global operacional; only formas novas/âncoras
reabrem.

**Etapa 5 — Adoção e registro.** O que passa vira canônico
(`adopted_configs.json`/bloco `shared` com hash), `MODEL_LEGITIMACY.md`
ganha §4.x, reports regeneram (fingerprint muda → staleness avisa), ledger
recebe a entrada. **Campanhas ESCREVEM os JSONs; o software LÊ via
`knowledge_base`** — nunca duplicar valor em código.

## 4. Regras de promoção (o coração do gap de adoção)

Um achado da campanha promove ao canônico se, e só se, tem **classe de
procedência**:

| Classe | Exemplos | Promove? |
|---|---|---|
| `lido-do-dado` (feature medida identificável) | emb da queda inicial; floor do platô; W_crit no joelho | **SIM**, direto, com a regra de leitura registrada |
| `fitado-this-rig` no DOF legítimo | c_bend (transversal); C_creep por PAR (§4.7) | **SIM**, como constante per-rig/per-par etiquetada |
| `input de paper` | grip/µ/Rz da nota de aparato | **SIM** (é input, não fit) |
| fit per-curva SEM feature identificável | timing de espectro ad-hoc; multiplicador solto | **NÃO** — fica experimental até ganhar regra de leitura ou virar forma falsificável |
| forma nova | gate de falsificação PASSOU + default-inerte | **decisão do professor**, caso a caso |

Consequência prática imediata: os 35 casos do gap se distribuem em Bauer
(cfg aninhada per-espectro — W_crit/c_D **têm** leitura do joelho → promover
com regra de leitura + achatar o schema do adopted p/ grupos por-figura),
Rousseau steel/HDPE (c_bend per-rig + leituras; campos de harness
GA_member/F_eff precisam de forma equivalente no engine ou tradução),
creep Li2022 (C_creep por-par é DOUTRINA §4.7 → promover o valor do par),
e casos onde a campanha usou config experimental não-promovível (ficam, com
o motivo registrado no orçamento).

## 5. Tooling (novo)

- **`validation/error_budget.py`** — `classify_case(rec, result) -> dict`
  (rótulo + evidências) e `error_budget(store) -> dict` (por caso + agregado
  por fonte); grava `Models/CALIBRATION_AND_VALIDATION/error_budget.json`;
  CLI `python -m bolt_analysis_studio.validation.error_budget`.
- **Report mestre**: seção "Orçamento de erro" (tabela por fonte × rótulo,
  com % e contagens) + **painel do ledger** (gráfico BASCHART da média/
  mediana por iteração, lendo `convergence_ledger.json`).
- **`docs/METHODOLOGY.md`** (biblioteca de documentação do software): o
  protocolo completo (este design operacionalizado), as regras de promoção,
  o runbook de uma iteração; seção 18 na aba Documentation; ponteiro no
  CLAUDE.md.

## 6. Primeira iteração (Sprint de Adoção — executa junto)

1. Rodar `error_budget` → confirmar a distribuição dos rótulos.
2. Promover, fonte a fonte, o que as regras da §4 permitem (editar
   `adopted_configs.json` com classe de procedência por constante; estender
   `suggest_overrides`/schema para grupos por-figura do Bauer).
3. Re-rodar o batch (`--all`), regenerar reports, apender ao ledger.
4. Meta da iteração: mediana canônica 0.181 → ≤ 0.10 (o que as regras
   permitirem; o que NÃO promover fica rotulado com motivo — honestidade
   sobre o resíduo).

## 7. Fora de escopo (desta spec)

Loop automático recorrente (decisão: professor no gate de cada adoção);
formas novas (entram pelo funil da Etapa 2.4 nas iterações seguintes);
âncoras experimentais físicas (spec própria quando o professor decidir).
