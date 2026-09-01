# Intake de Casos do Usuário via Prompt de IA — Design

**Data:** 2026-07-10 · **Status:** aprovado pelo professor (doutrina per-rig +
JSON único com curva embutida)

## 1. Pedido (professor, verbatim)

"Criar uma prompt que seja baixável do programa ou copiável e que o usuário
pudesse enviar os dados da curva experimental em txt, csv ou outros formatos,
junto com características dos testes (perguntas que ajudem a montar o msd
model) como carga, frequência, n de ciclos, tipo de controle por carga ou
deslocamento e etc, e assim pudéssemos gerar um arquivo que o software possa
importar e gere um report como esse que temos com um ajuste prévio do modelo
(que pode no futuro ser refinado pelo usuário)."

## 2. Fluxo

```
software ──"Copiar/Salvar prompt"──▶ usuário ──prompt + curva bruta──▶ IA externa
   ▲                                                                      │
   │                                             .bascase.json (schema v1)│
   └──"Importar caso…" / CLI --import ◀───────────────────────────────────┘
        │
        ├─ valida schema → normaliza curva → salva cópia canônica em Models/USER_CASES/
        ├─ AJUSTE PRÉVIO (doutrina per-rig): lê emb (queda inicial) + floor (platô)
        │  da curva; fita SÓ c_bend (transversal; axial nada) → grava no .bascase.json
        └─ registra como fonte "USER" no registry → runner/report v2/browser/
           "Abrir no Model/Run" funcionam sem mudança
```

## 3. Decisões (validadas)

1. **Ajuste prévio = doutrina per-rig (§4.42/L24)**: `emb_depth` via
   `emb_depth_from_curve` (proveniência `data_implied_early_drop`),
   `loose_arrest_floor` via `arrest_floor_from_curve` (platô do fim), e fit
   1-D de **`c_bend`** apenas (o único DOF legítimo por bancada transversal
   nova; axial: nenhum fit). Valores gravados no próprio `.bascase.json`
   (bloco `prefit`, cada um com proveniência) — o refino futuro = editar/
   refitar esses campos.
2. **Formato = JSON único** `.bascase.json` com curva embutida, schema
   versionado (`bascase_version: 1`).

## 4. Schema v1 (`.bascase.json`)

```json
{
  "bascase_version": 1,
  "name": "Ensaio M12 bancada X",
  "description": "texto livre",
  "test": {
    "bolt_size": "M12x1.75",
    "bolt_diameter_mm": 12.0, "pitch_mm": 1.75,
    "grip_mm": 30.0,
    "preload_N": 30000.0, "preload_percent_yield": 70.0,
    "loading_type": "TRANSVERSE",
    "control_mode": "displacement",
    "delta_amplitude_mm": 0.5, "F_amplitude_N": null,
    "frequency_Hz": 12.5, "n_cycles": 2000,
    "mu": null, "lubricated": false,
    "rz_class": "Rz10-40", "material_pair": "aço/aço",
    "notes": "texto livre"
  },
  "curve": {"x_unit": "cycles", "y_unit": "F_over_F0",
            "points": [[0, 1.0], [100, 0.97]]},
  "provenance": {"generated_by": "BAS intake prompt v1 + <IA>",
                 "date": "2026-07-10"},
  "prefit": {}
}
```

Regras: `bolt_size` OU (`bolt_diameter_mm`+`pitch_mm`); `preload_N` OU
`preload_percent_yield` (um dos dois obrigatório; ambos → `preload_N` vence);
`y_unit ∈ {F_over_F0, F_kN, F_N}` (o importador normaliza p/ ratio dividindo
por F₀ — se `F_over_F0`, valida início ≈1); `x_unit ∈ {cycles, minutes}`
(minutes → pseudo-ciclos com freq=1/60, regra dos casos de creep);
transversal exige `delta_amplitude_mm`>0; força/axial exige `F_amplitude_N`;
≥ 4 pontos, x crescente, y ∈ (0, 1.5]. Campos desconhecidos = null (o
importador aplica a regra assumed da biblioteca: grip 2.5d, µ 0.15, Rz
default). Erros de validação nomeiam o campo.

## 5. Componentes

- **`validation/intake_prompt.py`** — `INTAKE_PROMPT: str` (PT): instruções
  p/ a IA entrevistar o usuário (perguntas do bloco `test`, com explicação de
  cada variável — reusa a linguagem do glossário do report), aceitar a curva
  em qualquer formato, normalizar (regras explícitas), checar sanidade e
  emitir SÓ o JSON (schema embutido no prompt com exemplo). Constante única
  (fácil de copiar p/ clipboard/arquivo).
- **`validation/user_cases.py`** — `validate_bascase(data) -> list[str]`
  (erros); `import_user_case(path, dest_dir=None) -> CaseRecord`: valida,
  normaliza curva, salva cópia canônica `Models/USER_CASES/<slug>.bascase.json`,
  constrói o record (source="USER", família por loading_type, classe
  full_curve). `user_records(dest_dir=None) -> list[CaseRecord]` (scan);
  `case_registry.all_records()` passa a incluí-los (aditivo; os 128 testes
  existentes continuam valendo por filtragem source!="USER").
- **`validation/prefit.py`** — `prefit_user_case(rec, n_cap=None) -> dict`:
  lê emb/floor pelos leitores de `calibration.provenance` (via k_b da
  geometria do caso), fita `c_bend` por busca 1-D (grid log 0.1-50, ~8-10
  simulações com n_cap) minimizando o MAE do runner; grava bloco `prefit` no
  JSON canônico com proveniências. O runner consome: para source USER, os
  overrides vêm do bloco `prefit` do arquivo (não de adopted_configs).
- **GUI (ValidationBrowser/Controller)** — botões "Importar caso…"
  (QFileDialog → import → prefit em QThread → repopula árvore, seleciona,
  report) e "Copiar prompt" (clipboard) + "Salvar prompt…" (QFileDialog).
- **CLI** — `python -m bolt_analysis_studio.validation.report --import X.bascase.json`
  (importa + prefit + regenera reports).
- **Docs** — seção no `VALIDATION_CASE_REPORTS.md` + o prompt salvo como
  referência em `src/bolt_analysis_studio/docs/INTAKE_PROMPT.md`.

## 6. Tratamento de erro

Import inválido → lista de erros por campo (GUI: diálogo; CLI: stdout, exit 2);
curva sem platô → floor marcado limite-inferior (breakdown do leitor);
prefit que falhe em algum passo → caso importado mesmo assim com defaults e
aviso no report (bloco prefit registra o que degradou).

## 7. Testes

Schema: casos válidos/invál. (campo faltante, unidade errada, curva curta);
import: round-trip, normalização kN→ratio, minutos→ciclos; registry inclui
USER e mantém 128+N; prefit: emb/floor lidos = leitores diretos, c_bend
melhora MAE vs zero-fit num caso sintético; runner usa prefit do arquivo;
report v2 gerado p/ caso USER; GUI: botões emitem sinais/copiam prompt;
CLI --import.

## 8. Fora de escopo

Upload direto para IA de dentro do software; refino iterativo guiado (GUI de
re-fit) — o refino v1 = editar o bloco `prefit`/re-importar; digitalização de
imagem de gráfico (o prompt pede à IA que extraia se o usuário colar tabela,
mas figura escaneada fica a critério da IA externa).
