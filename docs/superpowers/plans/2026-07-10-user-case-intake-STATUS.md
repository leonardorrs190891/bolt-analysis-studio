# Intake de Casos do Usuário — Status (CONCLUÍDO)

**Data:** 2026-07-10 · **Plano:** `2026-07-10-user-case-intake.md` ·
**Spec:** `2026-07-10-user-case-intake-design.md` · **Modo:** inline

## O que foi entregue

O fluxo completo do pedido do professor: **prompt de IA copiável/baixável →
arquivo `.bascase.json` → importação → ajuste prévio per-rig → report v2**
(refinável editando o bloco `prefit`).

| Peça | Responsabilidade | Testes |
|---|---|---|
| `validation/intake_prompt.py` + `docs/INTAKE_PROMPT.md` | Prompt PT autocontido: entrevista (11 perguntas com o porquê de cada), regras de normalização da curva (txt/csv/kN/minutos), schema v1 embutido com exemplo, "responda com APENAS o JSON" | 2 |
| `validation/user_cases.py` | `validate_bascase` (erros por campo), `import_user_case` (cópia canônica `Models/USER_CASES/` + CSV derivado), `user_records` (scan); registry agrega fonte USER (`refresh_records`); `inputs_for` honra `_user_inputs` (proveniência "user") | 5 |
| `validation/prefit.py` | Doutrina §4.42/L24: `emb_depth` lido da queda inicial + `loose_arrest_floor` do platô (leitores de `calibration.provenance`), fit 1-D **só de c_bend** no transversal (grid log + refino; axial: nada fitado); bloco `prefit` gravado no JSON com proveniência por constante; runner honra `_prefit_overrides` | 3 |
| CLI `--import` + GUI | `report.py --import` (valida→prefit→simula→reports; exit 2 c/ erros); browser: "Importar caso…" / "Copiar prompt" / "Salvar prompt…"; controller: `import_case(path, prefit=True)`, `copy_prompt`, diálogos | 3 |
| Exemplo + docs | `Models/USER_CASES/exemplo_M12.bascase.json` importado DE VERDADE; seção 5 no `VALIDATION_CASE_REPORTS.md`; §17.3 na aba Documentation | (real) |

**Suítes: 60 validação/intake + 38 domínio + 22 chrome, verdes.**

## Números do exemplo real (M12 sintético, transversal)

- Prefit: `emb_depth` lido da queda inicial (data_implied_early_drop),
  `loose_arrest_floor` lido do platô, `c_bend` fitado — **MAE 0.0100**.
- Report gerado: `reports/exemplo_m12_sintetico.html`, fonte USER no mestre e
  no browser; "Abrir no Model/Run" funciona (herda o gui_bridge).

## Decisões/lições da execução

- Casos USER carregam **atributos dinâmicos** no `ValidationCase`
  (`_user_inputs`, `_prefit_overrides`, `_bascase`) — mesmo padrão de
  `model._v2_tuner_overrides`; a fonte é um shim (`.name="USER"`) para não
  tocar o enum.
- `relative_to(repo_root())` quebrava com casos fora do repo (testes tmp) —
  guards em runner/report_html/prefit.
- Slug normaliza unicode (NFKD→ascii): "sintético" → `sintetico`.
- Testes de contagem passaram a contar **128 não-USER** (o exemplo embarcado
  soma 129 no total).

## Limitações honestas

- Prefit transversal = ~11 simulações (com a curva completa do usuário; caso
  longo → minutos). Na GUI o import roda inline (sem thread) — aceito v1;
  se travar com curvas de 10⁵+ ciclos, mover p/ worker (follow-up).
- `c_bend` só age com `k_tr_mode="bending"` — o prefit escreve o pack LEGACY
  inteiro nos overrides para o fit ser coerente; o usuário que editar o bloco
  deve manter os modos.
- Digitalizar figura escaneada fica a critério da IA externa (o prompt pede
  tabela/valores).
- O refino v1 = editar `prefit.overrides` e re-importar (GUI de re-fit
  interativo é follow-up natural do módulo Validation).

## Follow-ups

GUI de refino (sliders sobre o prefit); prefit em QThread; aceitar múltiplas
curvas/repetições por caso (média + banda); validar `.bascase` contra bandas
de âncora (`knowledge_base.check_input`) e avisar fora-da-banda.
