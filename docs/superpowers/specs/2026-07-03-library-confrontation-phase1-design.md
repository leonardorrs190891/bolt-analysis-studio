# Confronto com a biblioteca — Fase 1 (transferência zero-refit, trilho axial, âncora de C_creep) — design

**Data:** 2026-07-03
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (PhD) + Claude Code (consolidação de duas frentes)
**Status:** Design em revisão pelo usuário. Mandato: "fazer da maneira que fique mais robusto",
usando `BAS_V2_papers/HANDOFF.md` (biblioteca integrada no commit `3931f1c`).
**Relacionado:**
- `BAS_V2_papers/HANDOFF.md` (mapa da biblioteca: 308 curvas, 16 notas de aparato, 128 ValidationCases)
- `Models/CALIBRATION_AND_VALIDATION/curve_library/apparatus_notes/MSD_BLOCK_COVERAGE.md` (lacunas + regras de preenchimento)
- `docs/superpowers/specs/2026-07-02-shared-physics-model-design.md` (constantes do Estágio A a CONGELAR)
- `docs/superpowers/specs/2026-07-03-parameter-activation-registry-design.md` (registro filtra candidatos do trilho axial)
- `New_Theory/MODEL_LEGITIMACY.md` §5 (estimação vs curve-fit; procedência ideal das constantes)

---

## 0. Objetivo e princípio

A prova que falta ao modelo (MODEL_LEGITIMACY §8) é **predição fora da amostra**.
A biblioteca digitalizada permite três ataques complementares, TODOS sob a mesma
disciplina do shared-physics: **constantes congeladas ou estimadas de dados
independentes; diferenças entre rigs entram só como inputs nomeados e
documentados** (geometria, F₀, amplitude, μ/lubrificação das notas de aparato —
nunca knobs livres por curva).

| Sub-campanha | Pergunta | Dados |
|---|---|---|
| **A. Transferência zero-refit** | as constantes do Estágio A (M16 shear UFU) predizem rigs alheios mudando SÓ inputs? | sweeps transversais disp-mode: Liu2025 (M16, 0.25–0.8 mm), Lu2024 (M8, 0.25–2.0 mm), Icmez/demir2024 (M8 fatorial), Bauer2024 (M8/M12), Yang2019 (M10), Rousseau2025 (M12 aço), Karlsen2022 (M30/M42) |
| **B. Trilho axial (1º fit)** | o modelo fecha carregamento AXIAL força-controlada com as constantes sempre-ativas (embedding/creep) + loosening axial — sem K_archard/tr_loose_gain (registro exclui por construção)? | liu2017 (9 curvas: sweeps de P0 15–21 kN e A_F 7.5–12.5 kN, 30 Hz) + li2022ti (4: A_F 10 kN, 10/15/20 Hz) |
| **C. Âncora independente de C_creep** | estimar C_creep de creep ESTÁTICO (sem vibração) — a constante mais fraca do fit compartilhado (IC ×2.30) | li2022marstruc (6 curvas, eixo x = MINUTOS, 5/10/15 kN, sweep de Ra, M16 304SS) |

## 1. Pré-registro (congelado NESTE spec, antes de qualquer resultado)

1. **Sub-campanha A é 100% out-of-sample:** as constantes vêm do bloco `shared`
   do `joint_calibrations.json` (Estágio A) e **não são reajustadas** para
   nenhuma curva da biblioteca. Não há split treino/teste — o treino foi o
   dataset UFU; a biblioteca inteira é teste.
2. **Casos incluídos em A (v1):** todos os casos transversais disp-mode dos 9
   papers prioritários listados acima, com os **trims obrigatórios** do HANDOFF
   §5.4 (caudas de fratura por fadiga são out-of-model: Yang2021 pós-N2,
   liu2022_fig8_multi_t4 >~1200, Liu2025 pós-N_D). **Excluídos de A:** axiais
   (vão para B), compostos yang2021 (Fase 2, acoplamento F↔δ), reaperto
   liu2022 fig6–8 (Fase 2, renewal), creep li2022marstruc (vai para C),
   Sandia modal (diâmetro não reportado), HDPE Rousseau (par tribológico
   polimérico — fora do domínio declarado do modelo; registrar como limite).
3. **Inputs por caso:** dos `ValidationCases`/notas de aparato: d, p, A_s,
   grip→L_eff, F₀, amplitude, freq, n_cycles, μ (nota do paper; se ausente,
   regra do MSD_BLOCK_COVERAGE: μ via coeficiente de torque ou default ISO,
   registrado no relatório com procedência `assumed`). Demais constantes:
   valores do Estágio A congelados.
3a. **`emb_depth` é INPUT por junta, não constante universal** (diagnóstico
   2026-07-03, thread paralela): assentamento f_Z depende da rugosidade e do
   nº de interfaces — tabelas publicadas (VDI 2230 f_Z por classe de
   acabamento; DIN 25201-4). Evidência: no M12 curto/retificado do Liu2017,
   os 30 µm do rig UFU engolem ~99% da perda predita; ~3 µm reproduz o dado.
   **Disciplina anti-knob:** o valor por fonte vem DA TABELA (procedência
   `handbook`: classe de Rz + nº de interfaces documentados), NUNCA do ajuste
   à curva; sensibilidade pré-registrada = classe de rugosidade adjacente.
   O valor UFU (30 µm) permanece o do rig UFU. Implicação futura (fora deste
   spec): no registro de ativação, `emb_depth` tende a migrar de constante
   fitável para estado nomeado com proveniência — decidir após a Fase 1.
4. **Métricas:** MAE_pred por curva; agregado por paper e por regime;
   distribuição (mediana, p90); comparação com dois baselines honestos:
   (i) "sem perda" (ratio≡1) e (ii) decaimento exponencial 1-parâmetro fitado
   por curva (o que um curve-fit local faria). Predição zero-refit ganhar do
   baseline (ii) em parte relevante dos casos = evidência forte; perder em
   quase todos = falsificação de transferência, documentada.
5. **Análise de sensibilidade aos inputs preenchidos:** para casos com μ/grip
   `assumed`, repetir a predição com μ±25% e grip 2×d↔3×d; reportar a banda.
   Conclusões que dependem da banda são marcadas `inconclusive`.
6. **Sub-campanha B é PREDIÇÃO-primeiro, fit só se falhar** (revisado pelo
   diagnóstico §1.3a — mais forte que o fit declarado original):
   **B1 (zero-refit):** predizer as 13 curvas axiais (9 Liu2017 + 4 li2022ti,
   trim >3.3e5 ciclos do full-run por fadiga; li2022ti é normalizado em N=200
   — alinhar a simulação da mesma forma) com constantes do Estágio A +
   `emb_depth` de tabela (§1.3a) + geometria ISO por fonte; comparar também os
   GRADIENTES dado-vs-modelo (∂perda/∂P₀ — análogo axial do sobretorque —,
   ∂perda/∂A_F, ∂perda/∂freq); monitorar o residual de conservação (≈0
   esperado). **B2 (somente se B1 falhar):** `fit_parsimonious` com orçamento
   ≤2 constantes, treinando nos 2 pontos centrais e predizendo os outros 11;
   candidatos = registro (sem constantes transversais); qualquer constante
   liberada é candidata a falsificação de forma, documentada.
7. **Sub-campanha C:** modo estático no engine = ciclos a F_amp=0, delta_amp=0,
   freq tal que 1 ciclo = 1 minuto (1/60 Hz) → só embedding+creep ativos.
   Fit de C_creep (+ emb_depth por nível de Ra, conforme a nota do paper) às 6
   curvas. **Uso honesto:** 304SS ≠ par UFU — o valor NÃO substitui o do
   Estágio A por decreto; ele **re-centra o prior e aperta os bounds** de
   C_creep (log-prior de literatura → log-prior de dado independente) e o
   Estágio A é re-rodado com esse prior para medir o impacto.

## 2. Artefatos

- `New_Theory/transfer_validation.py` — harness da sub-campanha A: itera os
  casos pré-registrados, monta `JointGeometry`+inputs por caso, roda o engine
  com constantes congeladas, aplica trims, computa métricas/baselines/
  sensibilidade, gera `New_Theory/transfer_report.md` (tabelas por paper) +
  `transfer_validation.png` (grids) + bloco JSON `transfer` em arquivo próprio
  (`New_Theory/transfer_results.json` — NÃO no joint_calibrations.json).
- `New_Theory/calibrate_axial.py` — sub-campanha B (espelha calibrate_shared).
- `New_Theory/anchor_creep.py` — sub-campanha C (fit estático + novo prior).
- `MODEL_LEGITIMACY.md` §4.6 (transferência), §5.1 atualização de procedência
  (C_creep: "prior de dado independente"), changelog. CLAUDE.md: comandos.

## 3. Critérios de sucesso (por sub-campanha, honestos)

- **A:** relatório completo com TODAS as curvas pré-registradas (nenhum drop
  silencioso); cada conclusão anotada com a banda de sensibilidade; falhas por
  regime identificam o mecanismo (ex.: M30/M42 Karlsen testa escala; travas
  químicas/Vibralock são out-of-model declarado).
- **B:** perfil axial com ≤3 constantes fitadas; registro exclui transversais
  automaticamente (evidência viva do spec 2026-07-03); LOCO documentado.
- **C:** C_creep com IC melhor que ×2.30; impacto no re-fit do Estágio A
  reportado (MAE e valor das constantes antes/depois).
- Nenhuma constante nova no engine; nenhum knob por curva; tudo reproduzível
  por script único por sub-campanha.

## 4. Fora de escopo (fases seguintes, já mapeadas)

Fase 2: sobretorque (F₀-bound 133 kN + hipótese de wear dependente de pressão —
nota: a hipótese GW k_tr(F₀) tem sinal DESFAVORÁVEL na equação de slip atual,
ver análise 2026-07-03), embedding renewal (liu2022 fig6–8), acoplamento F↔δ
(yang2021). Fase 3: colapso adimensional, profile likelihood. Fase 4 (lab UFU):
campanha de generalização, F₀ do TP6, Exp 1–5.

## 5. Riscos

| Risco | Mitigação |
|---|---|
| Erro de digitalização (2–5%) contamina conclusões | métricas comparadas aos baselines, não a zero; bandas de sensibilidade |
| Inputs preenchidos viram graus de liberdade disfarçados | procedência por input (`paper`/`assumed`) + sensibilidade pré-registrada |
| Modo estático (C) força o engine fora do uso normal | F_amp=0 → wear/loosening estruturalmente inertes (mesma lógica registry-truth); validar conservação no modo |
| Volume (dezenas de curvas) vira relatório ilegível | agregação por paper/regime + grids; curva a curva só no JSON |
