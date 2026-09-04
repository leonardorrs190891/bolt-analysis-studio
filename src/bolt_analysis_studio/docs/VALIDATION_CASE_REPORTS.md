# Bolt Analysis Studio — Biblioteca de Reports de Validação

**Escopo:** os **114 casos de validação comparáveis** (curva completa, simuláveis) da biblioteca de literatura + laboratório âncora interna, cada um com report individual completo + documento mestre.
**Rev.:** 2026-07-10 (report v2 — resíduo assinado, modelo MSD reproduzível,
decomposição por mecanismo).

---

## 1. O que é

Cada caso de validação (curva F/F₀ vs N digitalizada de artigo, ou ensaio âncora interna)
tem um **report HTML individual** com:

| Seção | Conteúdo |
|---|---|
| 1. Condições de contorno | F₀, modo de carga, amplitude, frequência, ciclos, lubrificação — com proveniência |
| 2. Modelo MSD (como preparado no software) | cadeia de elementos real (diagrama), tabela id/tipo/k/c/m/material/preload%, geometria do parafuso, carregamento global, **glossário de variáveis**, passo-a-passo p/ refazer |
| 3. Resultado e erro | curva artigo vs modelo, MAE/RMSE/erro máx, narrativa interpretada, **resíduo assinado** (modelo−artigo, banda ±MAE), erro por estágio I/II/III |
| 4. Decomposição por mecanismo | perda de F/F₀ cumulativa por embedding/creep/wear/loosening (área empilhada + shares; soma fecha exatamente 1−F/F₀) |
| 5. Constantes usadas | per-rig adotadas + bloco `shared` do Estágio A, cada uma com proveniência |
| 6. Caveats e veredicto | limitações do caso (fratura, creep em minutos, HDPE…) + nota de aparato |

O **documento mestre** (`validation_report.html`) agrega os 114: estatísticas
globais, tabela por fonte com MAE do runner canônico E da campanha (coluna
"campanha" = gap de adoção), pisos de repetibilidade, casos não simuláveis.

## 2. Onde vive / como abrir

- **Arquivos:** `New_Theory/validation_html/validation_report.html` (mestre) +
  `New_Theory/validation_html/reports/<caso>.html` (individuais).
- **Pelo software (V1):** menu **Validation Gallery** (gera se ausente e abre).
- **Pelo software (V2, `run_app.py --v2`):** módulo **Results** = navegador dos
  casos (curva + decomposição + staleness no próprio app; botões Report HTML /
  Report geral / **Abrir no Model/Run**), e menu **Help → Reports de Validação**.
- **Aba 📖 Documentation (V1):** seção "17. Validation Case Reports".

## 3. Como regenerar (fonte da verdade)

```bash
# regenera HTML do cache (rápido, sem simular)
python -m bolt_analysis_studio.validation.report --from-store
# re-simula os 128 e regenera tudo (~10 min)
python -m bolt_analysis_studio.validation.report --all [--resume]
# um caso só
python -m bolt_analysis_studio.validation.report --case liu2025_M16_amp0p25
```

Cache canônico: `Models/CALIBRATION_AND_VALIDATION/validation_store.json`
(carimbo `generated_at` + fingerprint do engine; resultados stale são marcados
"DESATUALIZADO" no navegador do V2).

## 4. Garantias e limitações

- O runner usa **exclusivamente** constantes com proveniência (bloco `shared`
  + configs adotadas per-rig via `knowledge_base`); reproduz a campanha
  bit-a-bit quando adotado == campanha. Divergências são **gap de adoção**,
  visível na coluna "campanha".
- O "Abrir no Model/Run" monta o MESMO modelo do report (fidelidade medida:
  Δmáx 1.6e-4 em F/F₀).
- Família `other` (Sandia modal): carregamento sem proveniência no runner v1 —
  reports degradam honestamente.

Specs: `docs/superpowers/specs/2026-07-10-validation-case-reports-design.md` e
`…/2026-07-10-report-v2-design.md`.

## 5. Casos do usuário (intake via IA)

Fluxo (spec `2026-07-10-user-case-intake-design.md`): no módulo **Results →
Validation**, use **"Copiar prompt"** (ou "Salvar prompt…"; referência:
`docs/INTAKE_PROMPT.md`). Cole o prompt numa IA junto com o arquivo bruto da
curva (txt/csv/planilha), responda às perguntas do ensaio e salve a resposta
como `<nome>.bascase.json`. Importe por **"Importar caso…"** ou pela CLI:

```bash
python -m bolt_analysis_studio.validation.report --import meu_ensaio.bascase.json
```

O software valida o schema (erros por campo), normaliza a curva (kN/N → F/F₀;
minutos → pseudo-ciclos p/ creep), salva a cópia canônica em
`Models/USER_CASES/` e faz o **ajuste prévio per-rig** (doutrina §4.42/L24):
lê `emb_depth` da queda inicial e `loose_arrest_floor` do platô final
(proveniência "lido-do-dado") e fita **apenas `c_bend`** no transversal
(axial: nada fitado). O caso entra como fonte **USER** no navegador e nos
reports — com decomposição por mecanismo e "Abrir no Model/Run" — e o bloco
`prefit` fica gravado no próprio `.bascase.json`. **Refinar** = editar
`prefit.overrides` no arquivo e re-importar (ou re-simular no módulo).
Exemplo embarcado: `Models/USER_CASES/exemplo_M12.bascase.json`
(prefit MAE 0.010 na curva sintética).

> **Nota (2026-07-11, diretriz do professor):** o conjunto contém apenas casos COMPARÁVEIS — os 8 built-in legados sem curva completa (só ratio final) e os 6 Sandia não-simuláveis foram removidos do registry, dos reports e do store. Os `ValidationCase` originais permanecem no core (suite V1).
