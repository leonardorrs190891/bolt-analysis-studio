# Consulta e Reports dos Casos de Validação — Design

**Data:** 2026-07-10 · **Status:** aprovado pelo professor (com adição: decomposição por mecanismo no report por caso)

## 1. Problema

O professor quer (a) consultar **cada caso de validação individualmente** da
biblioteca dentro do software, (b) o **report do caso** (modelo MSD, condições
de contorno, curva do artigo vs curva do software, análises de erro,
**decomposição por mecanismo**), e (c) um **report geral** com a validação de
todos os casos.

Estado atual: `New_Theory/generate_case_reports.py` (2026-07-09) gera 82
reports HTML + índice mestre, e a V1 abre o índice pelo menu ("Validation
Gallery"). Lacunas: **46 dos 128 casos sem report**; reports são fotografias
(não regeneráveis pelo software); lógica canônica (inputs por caso, geometria)
vive na sandbox `New_Theory/` sem testes; chrome V2 sem nada. (Nota
2026-07-10: a suspeita de bug de encoding nos HTML foi VERIFICADA E DESCARTADA
— os arquivos são UTF-8 válidos; o mojibake era do console de inspeção.)

## 2. Decisões (validadas com o professor)

1. **Interface:** navegador de casos nativo no chrome V2 (sub-mode Validation
   do módulo Results, antecipando o Plano 5) **+ HTML** como artefato de
   arquivo/impressão. V1 mantém o menu.
2. **Frescor híbrido:** consulta abre instantânea do snapshot (cache com
   carimbo "gerado em" + fingerprint do engine); "Re-simular caso" (segundos)
   e "Re-simular tudo" (job background, minutos) atualizam o cache.
3. **Cobertura:** todos os **128 casos com degradação honesta** — curva
   completa → report rico; só ratio final → comparação pontual + aviso;
   fora-de-modelo (fratura, creep) → seção de caveats do apparatus_notes.
   O índice geral marca a classe de cada caso.
4. **Lógica canônica portada para o produto** (`src/bolt_analysis_studio/validation/`),
   com teste de paridade contra a galeria atual; `New_Theory` delega ao pacote
   depois (follow-up). Constantes continuam vindo dos JSONs versionados via
   `knowledge_base` — o que é portado é **código** (fórmulas, montagem).
5. **Decomposição por mecanismo no report por caso** (adição do professor):
   perda de pré-carga atribuída a Embedding/Creep/Wear/Loosening por ciclo
   (área empilhada + tabela de shares finais), vinda do próprio engine
   (`CycleSnapshot.dF_0_by_mech`, mesmo dado do plot "Mechanism Decomposition"
   do Run). A soma dos 4 fecha exatamente `F0·(1−ratio)`.

## 3. Arquitetura — pacote `validation` (core, sem GUI)

```
src/bolt_analysis_studio/validation/
├── __init__.py
├── case_registry.py   # CaseRecord: 128 casos unificados + classe + paths
├── runner.py          # simulate_case(record) -> CaseResult (engine V2)
├── store.py           # cache JSON por caso + fingerprint + seed da galeria
└── report_html.py     # report por caso (128) + report geral, UTF-8
```

- **`case_registry.py`** — `CaseRecord` por caso: id estável (nome do CSV p/
  digitalizados; slug do nome p/ built-in), fonte, classe
  (`full_curve`/`final_ratio`/`out_of_model`+trim), condições de contorno
  estruturadas (do `ValidationCase`), paths (CSV de referência,
  `apparatus_notes/<paper>.md`, report HTML), entrada da galeria
  (`report_data.json`) quando existir. `all_records()`, `record(case_id)`.
- **`runner.py`** — `simulate_case(record) -> CaseResult`: monta geometria
  (port de `library_common.geometry_for`, paridade testada), material com
  proveniência (constantes adotadas per-rig via
  `knowledge_base.adopted_config/suggest_overrides` + bloco `shared`), roda
  `DynamicStiffnessAnalyzer` respeitando os modos especiais já codificados
  nos casos (axial força `delta_amp=None`, creep freq 1/60 Hz, trim de
  fratura). Retorna curva modelo, métricas interpoladas (MAE/RMSE/maxerr),
  **decomposição cumulativa por mecanismo** e trajetória de `D` quando ativa.
- **`store.py`** — um JSON de cache (`Models/CALIBRATION_AND_VALIDATION/validation_store.json`)
  com, por caso: curva modelo, métricas, decomposição, `generated_at`,
  `engine_fingerprint` (sha256 curto de `default_v2_params` + bloco `shared` +
  constantes adotadas). **Seed inicial importado do `report_data.json`** (82
  casos abrem instantâneos; seeds não têm decomposição — preenchida na
  primeira re-simulação). API: `get(case_id)`, `put(case_id, result)`,
  `is_stale(case_id)`.
- **`report_html.py`** — port do gerador atual (mantendo UTF-8 explícito),
  estendido aos 128. Conteúdo por caso: §1 condições de contorno; §2 modelo
  MSD (junta, geometria, F0 com proveniência); §3 curva do artigo vs curva do
  modelo (SVG inline) + análises de erro (MAE/RMSE/maxerr, por segmento
  I/II/III quando curva completa); **§4 decomposição por mecanismo** (área
  empilhada SVG + tabela de shares finais; omitida com aviso quando só há
  seed); §5 constantes usadas com proveniência; §6 caveats/veredicto
  (apparatus_notes). Report geral: estatísticas globais (média/mediana MAE,
  tabela por fonte, comparação com pisos de repetibilidade do
  `convergence_indicator.FLOORS`, contagem no-limite-do-dado), classe de cada
  caso, links aos individuais, carimbo global.
- **CLI:** `python -m bolt_analysis_studio.validation.report [--case ID] [--all] [--from-store]`
  — `--all` re-simula os 128 e regenera tudo (~minutos, offline).

## 4. Acesso no software

- **Chrome V2 (Plano B):** `ValidationController` no padrão consolidado
  (controller por módulo): página no `_center` com árvore fonte→caso à
  esquerda e detalhe no centro (plot artigo vs modelo, métricas, condições,
  decomposição, carimbo/staleness). Botões: Re-simular caso · Re-simular tudo
  (QThread com progresso) · Abrir report HTML · Gerar report geral. Ativado
  pelo módulo Results (sub-mode Validation).
- **V1:** menu "Validation Gallery" passa a **gerar via pacote** quando o HTML
  estiver ausente ou stale, depois abre no navegador (comportamento atual de
  abrir preservado).

## 5. Tratamento de erro / degradação

- Caso sem CSV legível → report com aviso "curva de referência indisponível"
  + comparação pontual (mesmo padrão import-time-degrade do `DIGITIZED_CASES`).
- Runner que levanta exceção → `CaseResult.error` registrado no store e
  exibido no report/GUI (não derruba o batch; o geral lista os failed).
- Seed sem decomposição → seção §4 mostra "re-simule para obter a decomposição".

## 6. Testes

- Registry: 128 records, classes corretas, paths existentes p/ amostra.
- Runner: **paridade com a galeria** (MAE do runner vs `report_data.json` em
  casos-amostra de fontes distintas, tolerância apertada); decomposição soma
  exatamente `F0·(1−ratio)`; modos especiais (axial força, creep) corretos.
- Store: round-trip, staleness por fingerprint, seed import.
- Report: gera 128 sem exceção; UTF-8 (título com acento intacto); seções
  presentes por classe; report geral com contagens certas.
- GUI (Plano B): controller expõe árvore/detalhe; re-sim atualiza; padrão de
  testes offscreen dos Planos 1-3.

## 7. Execução — 2 planos

1. **Plano A (core):** pacote `validation` completo + reports dos 128 +
   encoding + rewire do menu V1 + CLI. Entrega o pedido consultável via
   navegador.
2. **Plano B (GUI V2):** módulo Validation no chrome com re-simulação
   interativa e job background.

## 8. Fora de escopo

- Reorganização Basic/Advanced do inspector (segue nos planos do chrome).
- Fazer `New_Theory/library_common.py` importar do pacote novo (follow-up
  pós-adoção, para extinguir a duplicação de `geometry_for`).
- PDF dos papers embutido no report (link relativo quando o PDF existir na
  `BAS_V2_papers/`; sem embed).
