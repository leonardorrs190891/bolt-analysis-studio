# Volume 1 — Entender o modelo

> **O que este volume é.** O fio condutor da física do BAS V2: o que o modelo é,
> por que ele não é um ajuste de curva, qual a tese central do projeto, de onde
> vem cada constante, e o que já foi tentado e morreu. Ele **não duplica** o
> `MODEL_MATH_REFERENCE.md` (equações) nem o `MODEL_LEGITIMACY.md` (o registro
> vivo de física-vs-overfitting) — ele os costura e aponta.
>
> **Procedência dos números desta página.** Censo e MAEs vêm do store canônico
> `validation_store.json`, fingerprint **`4f5bedfbace4`**, via
> [`figs/numbers.json`](figs/numbers.json) (gerado por
> [`scripts/manual_figs.py`](../../scripts/manual_figs.py)). Constantes
> compartilhadas vêm do bloco `shared` de
> [`joint_calibrations.json`](../../New_Theory/joint_calibrations.json).
> Bandas e proveniências vêm de `calibration/knowledge_base.py`
> (`anchor_priors()`, `frozen_params()`, `dof_summary()`).

---

## 1. O paradigma: massa-mola-amortecedor com estado lento

O BAS V2 não é uma correlação empírica de perda de pré-carga. É um **sistema
massa-mola-amortecedor** (MSD) cuja matriz de rigidez é reavaliada a cada ciclo,
carregando um **vetor de estado lento**:

```
s = (F_0, δ_emb, δ_creep, δ_wear, θ_loose, D)
```

| símbolo | o que é | unidade |
|---|---|---|
| `F_0` | pré-carga corrente | N |
| `δ_emb` | assentamento (embedding) já consumido | m |
| `δ_creep` | fluência acumulada | m |
| `δ_wear` | material removido por desgaste | m |
| `θ_loose` | rotação de afrouxamento acumulada | rad |
| `D` | dano de superfície ∈ [0,1] | — |

Sobre esse estado agem **quatro mecanismos de perda em paralelo** — Embedding,
Creep, Wear e RotationalLoosening — e `D` **não é** um quinto mecanismo: ele
**modula** o atrito (`mu_bearing_eff = mu·(1−k_dmg_mu·D)`) e **amplifica** o
desgaste (`d_wear ·= 1+k_dmg_wear·D`). Todos os mecanismos leem o `F_0` do
**início** do ciclo, então não há dependência de ordem entre eles.

O acoplamento que fecha o laço é o da hélice: `F_0 → [K(s)] → Φ → afrouxamento →
F_0`. É dele que saem os dois regimes qualitativos — **runaway** (a perda se
realimenta) e **auto-travamento** (a perda se estanca num piso).

- Equações completas, símbolo por símbolo: [`MODEL_MATH_REFERENCE.md`](../../New_Theory/MODEL_MATH_REFERENCE.md)
- A mesma coisa em forma interativa: [modelo MSD](../../New_Theory/variable_explorer/concept_msd-model.html) ·
  [estado + mecanismos](../../New_Theory/variable_explorer/concept_mechanisms.html) ·
  [acoplamento](../../New_Theory/variable_explorer/concept_coupling.html)

### 1.1 Por que NÃO é um fit — as seis provas

Esta é a objeção número um, e ela tem resposta medida, não retórica. As seis
provas estão desenvolvidas (com gráfico ao vivo) em
[concept_not-a-fit.html](../../New_Theory/variable_explorer/concept_not-a-fit.html);
em resumo:

1. **Prevê condição não medida** — uma configuração física acerta as 6 amplitudes
   do Liu 2025. Uma interpolação precisaria dos pontos de cada amplitude.
2. **A interpolação falha fora do ajuste** — a reta ajustada ao ensaio de 0,25 mm
   vai de MAE 0,00 em 0,25 mm a **0,20** em 0,80 mm; o modelo fica em 0,05–0,10
   em **todas**.
3. **Transfere entre rigs e tamanhos** — as mesmas formas preveem de M8 (Bauer,
   ~20 kN) a M30/M42 (Karlsen, ~500 kN): ~5× em diâmetro, ~25× em carga.
4. **Uma equação, formas qualitativamente diferentes** — runaway, S-curve de
   auto-travamento e platô→colapso saem da MESMA física, mudando só entradas.
5. **Decompõe em mecanismos nomeados** — a perda é atribuída a
   embedding/creep/desgaste/afrouxamento (Norton, Archard, two-factor), não a
   coeficientes anônimos.
6. **Fecha o balanço de energia** — `W_ext + ΔU = Σ W_diss` com residual ≈ 0.

### 1.2 As três camadas

| camada | conteúdo | o que ela garante |
|---|---|---|
| **analítica** | Hooke (`k_b`), Coulomb, hélice (rotação↔pré-carga), conservação | não é ajustável; erra ou acerta |
| **empírica** | leis NOMEADAS de literatura: Norton (embedding), log-t (creep), Archard (desgaste), Greenwood-Williamson (amolecimento) | cada uma tem citação e domínio declarado |
| **constantes** | valores por par tribológico / por bancada | é **aqui** que a calibração vive — e só aqui |

O ponto de método: a camada 3 é a única com liberdade, e ela é **pequena**
(§4 abaixo). Formas novas nascem **default-inertes**, com bit-identidade testada.

---

## 2. Contabilidade de energia como invariante de projeto

O balanço `W_ext + ΔU = Σ W_dissipado` não é um resultado, é um **teste que roda
junto**: `analyzer.energy.conservation_residual` deve ficar ≈ 0. Duas
consequências de projeto que já custaram depuração e estão fixadas:

- **Amplificação de desgaste por dano mexe em `dF_0`, mas NÃO em `dE`.** O
  `d_wear ·= (1+k_dmg_wear·D)` aumenta a perda de pré-carga; a energia `dE` do
  desgaste continua sendo o trabalho de atrito real, e a perda extra é balanceada
  via `U_released`. Amplificar `dE` também quebra a conservação (~40% de
  residual). **Não fazer.**
- **A comporta de incubação (`slip_onset_gate`) também é "dF_0 sim, dE não"** —
  micro-slip continua dissipando calor e alimentando `W_slip_acc` mesmo quando a
  perda de pré-carga está suprimida.

**Onde a conservação degrada, declarado:** no regime de colapso por dano
(`F_0 → 0`) a energética de remoção por desgaste é fenomenológica. Isto deixou
de ser suspeita e passou a ser **medido** — ver §6.3.

Detalhe e barras de energia ao vivo: [concept_energy.html](../../New_Theory/variable_explorer/concept_energy.html).

---

## 3. A tese central: **formas transferem entre rigs; constantes não**

Esta é a afirmação de maior alcance do projeto, e ela foi **estabelecida por
confrontação**, não postulada. A Fase 1 a atacou por três frentes independentes
(§8 do [`MODEL_LEGITIMACY.md`](../../New_Theory/MODEL_LEGITIMACY.md)):

| frente | o que fez | o que achou |
|---|---|---|
| **B — trilho axial** | predição zero-refit num modo de carregamento diferente | as formas seguram; o nível pedia proveniência, não constante nova |
| **C — âncora de `C_creep`** | comparou o fit UFU com creep estático de literatura (304SS) | UFU **1,867e-11** vs âncora **9,9e-13** — intervalos de confiança **disjuntos** |
| **A — transferência transversal** | varreu a biblioteca aplicando a física de um rig aos outros | as formas transferem; as constantes **não** |

A frente C é a mais decisiva porque é a mais limpa: mesma lei, mesmo modo,
constantes separadas por mais de uma ordem de grandeza — e **isso não é falha do
modelo**, é a física do par tribológico. `C_creep` é **por par**, e o
`knowledge_base` hoje registra quatro: UFU 1,867e-11 · Liu2017 1,45e-11 · 304SS
9,9e-13 · Al5083 0,012–0,025/década.

**Como a tese governa a calibração.** Ela produz uma regra operacional:
*forma nova exige prereg + gate; constante exige **procedência**.* Uma forma que
funciona num rig é candidata legítima em todos; um número que funciona num rig
**não é** evidência para outro. É por isso que o trabalho migrou de "fitar menos"
para "**prover procedência por constante**".

E ela produz também a hierarquia de proveniência que classifica cada valor
(MEM/§4.26, `l1l7_final_report.md` §2):

> **medido** (valor experimental do par certo) > **derivado** (calculado dos
> dados do paper) > **forma** (a lei transfere, a constante não) > **contexto**
> (não transfere; serve de precedente)

---

## 4. Tabela de constantes ativas, com proveniência

O bloco canônico é o `shared` de
[`joint_calibrations.json`](../../New_Theory/joint_calibrations.json)
(schema 2, calibrado em 2026-07-04, `SharedCalibrator.fit_parsimonious`). O
titular do resultado é este:

> **três números fitados no dataset inteiro** — `W_conf_ref`, `C_creep` e o
> `F0_test` do sobretorque. Todo o resto é input, âncora, ou forma.

`free_constants` do bloco: `["W_conf_ref", "C_creep"]`. MAE global **0,0509**.

| constante | valor | onde vive | classe | proveniência |
|---|---:|---|---|---|
| `emb_depth` | 3,0e-5 m | `shared` | **input** | VDI 2230, tabela f_Z por classe de rugosidade Rz (`library_common.emb_depth_vdi`). **Não é constante universal** — o 30 µm só vale para o rig UFU; o trilho axial usou 9,5 µm (Rz<10) |
| `N_emb` | 50 | `shared` | **per-rig** | timing lido do dado (~metade do assentamento em 10–20 ciclos); banda medida em outros rigs **3–15** — a diferença é real e está registrada, não reconciliada |
| `k_wear_spec` | 5,0e-14 1/Pa | `shared` | **derivado** | razão canônica K/H (§4.42a) — `K_archard` e `hardness` são **não-identificáveis em separado**, só aparecem como razão |
| `C_creep` | 1,8667e-11 | `shared` | **FITADO** (por par) | fit UFU; âncora 304SS 9,9e-13 com IC disjunto (§4.7). A âncora re-centrada vive em `New_Theory/creep_anchor.json`, **fora** do canônico |
| `tr_loose_gain` | 2,0 | `shared` | **forma** | two-factor loosening (acoplamento anisotrópico Φ × hélice) |
| `c_D` | 2,0 | `shared` | **forma** | crescimento de dano dirigido pela dissipação de slip |
| `k_dmg_wear` | 4,0 | `shared` | **forma** | amplificação de desgaste pelo dano |
| `W_conf_ref` | 7671 J | `shared` | **FITADO**, sem âncora | conformação dependente de pressão; a Fase 3 tentou ancorar e **falhou** (§4.9, null decisivo — nenhum dado da biblioteca isola a constante). Experimento-âncora especificado, não executado |
| `conform_pressure_exp` (`n`) | 2,0 | `shared` | **banda medida** | 1,48–2,0 (liu2021 no-load vs preload) |
| `p_ref_conform` | 5,0e8 Pa | `shared` | **fixo** | ≈80% da carga de prova, consistente após o re-escalonamento físico de `A_contact` |
| `mu` (seco) | 0,15 | default | **banda medida** | 0,14–0,19 (qiao2025, 25 pontos + fator K do lu2024) — **PASSA** |
| `fat_sigma_endurance` | 5,0e7 Pa | default | **banda medida** | 4,6e7–6,3e7 (schaumann2015) |
| `F_amp_ratio` | 0,4 | default | **literatura** | 0,378–0,489 medido (pai2002) |

Os presets validados **por bancada** vivem em
[`adopted_configs.json`](../../New_Theory/adopted_configs.json) — **68 grupos**
adotados hoje — e são lidos pelo software por uma API única,
`calibration/knowledge_base.py` (`adopted_config(src)`,
`suggest_overrides(src)`). A regra da casa: *as campanhas ESCREVEM os JSONs; o
software LÊ por aqui* — nunca duplicar valores em código.

### 4.1 Graus de liberdade, contados com honestidade

`JointMaterial` tem **98 campos**, e 98 campos **não são** 98 graus de liberdade:

- **~45 são capabilities default-inertes** (0 DOF) — inclusive o canal L1 de
  flanco (gate B1 **FAIL**) e o `arrest_approach_exp` (gate grupo A **FAIL**);
- **4 estão congelados por sensibilidade nula** (`S≈0` no tornado §4.42),
  *enforced* em `parameter_registry.FROZEN_S_ZERO`: `k_j_init`, `alpha_GW`,
  `slip_capacity_coeff`, `partial_slip_exp`;
- **as constantes compartilhadas foram fitadas 1× no dataset inteiro** (Estágio A);
- livres por rig, hoje: no **transversal** `c_bend` e `loose_arrest_floor` (este
  **lido** do fim da curva, não fitado); no **axial**, **nenhuma**.

A camada de **9 tuners** multiplicativos que existia até 2026-07-09 foi
**removida** (Estágio B, §4.42c): o engine lê só constantes físicas, e `.msd`
legados são traduzidos na fronteira por
`calibration.tuner_shim.translate_legacy_tuners`.

Tornado de sensibilidade e a lista de congelados, em figura:
[`figs/fig4_tornado.svg`](figs/fig4_tornado.svg) (19 parâmetros, 4 congelados;
top-5 por sensibilidade: `mu` 0,147 · `tr_loose_gain` 0,123 · `c_bend` 0,114 ·
`eta_loose` 0,064 · `C_creep`).

### 4.2 Uma física, N estados

As quatro condições históricas (nova / reusada / sobretorque / reaperto) **não**
têm física diferente. Elas têm o mesmo bloco de constantes e diferem só por
**estados nomeados**:

| condição | estados | dano | MAE (fit) | MAE (LOCO) |
|---|---|:--:|---:|---:|
| nova | `F0=50 kN` (nominal) | off | 0,0741 | 0,0873 |
| reusada | `D_init=0,3`, `emb_consumed_frac=1,0` | on | 0,0562 | 0,0624 |
| sobretorque | `F0_test=120 kN` (estimado) | off | 0,0300 | 0,1206 |
| reaperto | `D_init=0,3` | on | 0,0433 | 0,0455 |

O LOCO (*leave-one-condition-out*) é o teste de generalização: quase igual ao fit
nas condições nominais. O **sobretorque é a exceção honesta** — 0,121 no LOCO
porque é a única condição de pressão elevada, então `W_conf_ref` não é
aprendível deixando-a de fora. Isso é limitação de **cobertura do dataset**, não
de forma.

---

## 5. As limitações L1–L7: o que era, o que supriu, qual gate validou

Relatório completo: [`l1l7_final_report.md`](../../New_Theory/l1l7_final_report.md).
Resultado **misto e declarado sem maquiagem** — e é isso que o torna útil:

| # | limitação | forma construída | gate | veredicto |
|---|---|---|---|---|
| **L1** | desgaste de flanco ∝ amplitude axial | canal de flanco per-rig | Gate B1, 2 preregs | **FALSIFICADO** (`FAIL2`) — a forma existe e é ~8× rasa demais para o slope do Liu2017. Não adotada |
| **L2** | rigidez de membro `k_j`(geometria, material) | lei de Pedersen 2008 (`kj_mode="pedersen"`) | Gate D5 Rousseau/Zhang | **PASS-inert** — 8/8, ΔMAE = 0,0 exato. Válida como **proveniência de geometria**, sem efeito comportamental no PACK adotado |
| **L3** | acoplamento `F_amp ↔ δ_amp` em disp-mode | `mu_eff_lo`, `mu_eff_F0_ref`, `gross_ceiling_decay` (default 0,0 = OFF exato) | bit-identidade + efeito físico | **capacidade default-inerte com proveniência**; falta calibrar per-rig |
| **L4** | conformação a ~1 GPa | — (nenhuma mudança de engine) | busca dirigida na literatura | **null reconfirmado 3×** (Rodadas 4 e 5). `W_conf_ref` segue dependente do experimento-âncora UFU |
| **L5** | creep | docstring corrigido (**log-t**, não Norton-Bailey) + forma saturante **opt-in** | suíte de creep sem regressão | **PASS** — default segue log-t |
| **L6** | `k_wear_spec` por par | tabela de âncoras no KB por interface+par | testes de KB | **PASS** — documenta e centraliza a não-universalidade; não a resolve |
| **L7** | energia específica de remoção | `EnergyBudget.removal_energy_check()` | banda Shipway 2021 (1,8–10,5 kJ/mm³) | **bound informacional** — nunca bloqueia, nunca é fitável |

**Adoções realizadas na branch L1–L7: ZERO.** Toda capacidade nasceu
default-inerte; ligar qualquer uma exige prereg, gate e decisão explícita.

---

## 6. Histórico de falsificações — e por que isso é força

O `MODEL_LEGITIMACY.md` registra cada tentativa que morreu. Um modelo que só
publica o que funcionou não é verificável; a lista abaixo é o que dá crédito ao
que sobrou.

### 6.1 Formas que morreram

| candidato | § | como morreu |
|---|---|---|
| **canal de flanco ∝ A_F (L1)** | 4.43 | Gate B1 `FAIL2` — slope ~8× raso demais |
| **canal de rotação θ(N)** | 4.23 | confronto zero-refit: falsificado por **equifinalidade** (vários caminhos dão o mesmo θ) |
| **nível de energia por ciclo** | 4.25 | loops medidos vs `W_diss`/ciclo: nível falsificado, **estrutura correta** |
| **gatilho de criticalidade (joelho do Bauer fig8)** | 4.30 | falsifica o crash gradual |
| **3 formas de erro de mid-curva** | 4.35 | TODAS falsificadas no modo dominante — e a fonte-líder estava **no piso** |
| **espectro multi-amplitude** | 4.36 | módulo construído, **premissa** falsificada — e a falsificação **nomeou a forma real** |
| **`flank_s_crit`** | F4 | morto por **não-discriminância**: 30/30 células passavam a banda, **inclusive as 6 sem o candidato** |
| **`arrest_approach_exp`** (aproximação suave do piso) | prereg grupo A | **G2 FAIL / G3 FAIL** |
| **`W_conf_ref` ancorável na biblioteca** | 4.9 | **null decisivo** — nenhum dado disponível isola a constante |

### 6.2 Uma falsificação que **venceu** — e a regra que ela gerou

O gate B1 axial falhou em 2026-07-03. A **ρ-unificação** (`emb_amp_exp=2,375`)
foi adotada em 2026-07-08 — cinco dias depois — e tornou o embedding dependente
da amplitude. **O gate nunca foi re-medido, e o texto ficou 24 dias errado.**
Re-medido em 2026-07-27 no store `4f5bedfbace4`: o modelo entrega **77,7%** da
sensibilidade `∂(fim)/∂A_F` (−1,7225e-5 /N vs −2,2160e-5 /N no dado), não 0%; a
fonte fecha **9/9 no tripé**.

Foi partir dessa falsificação não re-baselinada que matou o `flank_s_crit`. Daí a
regra, hoje válida (§4.43):

> **Toda falsificação ou pendência registrada carrega o fingerprint contra o qual
> foi medida, e vira suspeita assim que o fingerprint muda.**

Um roadmap que envelhece em silêncio não atrasa o trabalho — ele o **desvia**.
Quando essa regra foi aplicada aos 11 itens do roadmap, **sete** estavam vencidos
ou já feitos.

### 6.3 O que ainda não fecha, medido

- **Energia de remoção fora da banda física.** O check L7 está gravado nos 203
  registros: 93 casos sem energia implicada (desgaste ≈ 0), **110 com valor — só
  46 dentro da banda 1,8–10,5 kJ/mm³, 64 FORA**, de 951 J/mm³ (karlsen M42) a
  **1,27e6 J/mm³** (yang2019 amp0p4_5Hz) ≈ 120× o teto. Onde o desgaste carrega a
  perda, ele frequentemente implica um custo por volume removido
  **fisicamente implausível**. Apertar isso é candidato de **forma**.
- **Bookkeeping `W_ext`/`W_damp_visc` no modo axial-força.** O termo viscoso de
  Rayleigh acumula sem contraparte em `W_ext` (residual −242,8 a −11,7 J). **Não**
  realimenta `F_0` e **não** afeta MAEs, mas o orçamento de energia axial fica
  aberto.
- **36 das 55 curvas fora do tripé são *form-limited*** — nenhuma constante as
  fecha. As outras **19 não pedem física nova**: 8 pedem **ler um nível**, 8 pedem
  **decidir uma convenção de métrica** e 3 são **limitadas pelo dado** (exceções
  necessárias por nome; por *contagem* de teto de grupo são 6 — ver §6b do
  relatório de classes). Classificação curva-a-curva, só-leitura, no
  store `4f5bedfbace4`:
  [`frontier_classes.md`](../../New_Theory/frontier_classes.md).
  **Duas ressalvas que vêm com o número:**
  1. **"Não pedir física nova" ≠ "fechar de graça".** As 6 de nível foram
     sondadas com as duas alavancas que a campanha sabe **ler** do dado
     (`loose_arrest_floor`, `emb_depth`) e **só 1 fecha**; 2 são **inertes**
     (`loose_arrest_floor` não faz nada sem pack na entry — Δ = 0 exato) e as
     outras **pioram**. O erro *é* de nível; a alavanca é que não existe ainda
     ([`level_seven_probe.md`](../../New_Theory/level_seven_probe.md)).
  2. A classe METRIC-LIMITED é definida contra a convenção de métrica
     **vigente**, então pela regra §4.43 a classificação vira suspeita se a
     métrica canônica mudar.

  A fila de formas está em
  [`DECISOES_PENDENTES.md`](../../New_Theory/DECISOES_PENDENTES.md).

---

## 7. Onde ir depois

| quero… | vá para |
|---|---|
| as equações | [`MODEL_MATH_REFERENCE.md`](../../New_Theory/MODEL_MATH_REFERENCE.md) |
| o registro vivo de legitimidade | [`MODEL_LEGITIMACY.md`](../../New_Theory/MODEL_LEGITIMACY.md) |
| a metodologia de evolução (MEM) | [`METHODOLOGY.md`](../../src/bolt_analysis_studio/docs/METHODOLOGY.md) |
| explicar isso a um terceiro | [Volume 2 — Explicar](02-explicar-o-modelo.md) |
| usar o software | [Volume 3 — Aplicar](03-aplicar-o-software.md) |
| o que o modelo **não** cobre | [concept_coverage.html](../../New_Theory/variable_explorer/concept_coverage.html) |
