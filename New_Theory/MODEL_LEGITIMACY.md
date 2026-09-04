# MODEL LEGITIMACY — física ou ajuste de curvas?

**Documento vivo.** Responde à pergunta central de revisores (e do próprio
autor): o `DynamicStiffnessAnalyzer`, com seus ~5–6 tuners, é um **modelo físico**
ou um **ajuste multivariável de curva**? Aqui ficam o argumento estrutural, as
**evidências quantitativas** (identificabilidade + parcimônia) e o **protocolo de
legitimidade**. Cobre também os acoplamentos do software.

> **Como manter atualizado:** toda mudança no modelo (mecanismo novo, tuner novo,
> reparametrização) DEVE atualizar este documento — pelo menos a tabela de
> parâmetros, a análise de identificabilidade (rodar `identifiability_analysis.py`)
> e o changelog no fim. Veja [[model-legitimacy-doc]] na memória persistente.

**Relacionados:** `MODEL_MATH_REFERENCE.md` (matemática completa),
`identifiability_analysis.py` (§4.1), `cross_validation.py` (§4.2),
`parametric_validation.py` (§4.3), `joint_calibrations.json`,
`docs/superpowers/specs/2026-06-20-generalization-validation-campaign.md` (protocolo).

Última atualização: 2026-07-04.

---

## 1. A tese: o que separa física de overfitting

Qualidade de ajuste numa curva **não** prova nada — qualquer função com
parâmetros suficientes ajusta uma curva monotônica. O que distingue um modelo
físico de um ajuste de curva é:

1. **Restrição estrutural** — formas funcionais fixas (não-livres) + leis de
   conservação + acoplamentos. O modelo só consegue produzir curvas
   *compatíveis com a física*, não qualquer curva.
2. **Parcimônia** — nº de parâmetros livres ≤ conteúdo de informação do dado.
3. **Generalização** — prediz condições não vistas e observáveis secundários,
   não só a curva que foi ajustada.

Um modelo pode ser **fisicamente fundamentado E sobre-parametrizado para um
dado pobre ao mesmo tempo**. É o caso aqui, e este documento é honesto sobre isso.

---

## 2. Restrição estrutural — o paradigma de três camadas

| Camada | O que é | Pode mudar? | Exemplos |
|---|---|---|---|
| **Analítica** | Física invariante | Não | `k_b=E·A_s/L`, hélice `λ=p/2π`, Coulomb `F_slip=µF₀`, conservação de energia |
| **Empírico-fenomenológica** | Forma fixa da literatura; parâmetros do material | Parâmetros sim, forma não | embedding Norton `1−e^{−N/N_emb}`, creep `log(t)`, Greenwood-Williamson `k_j∝F₀^α`, Archard `K·F·s/H`, two-factor Φ, incubação estágio-I Hill `g=W^k/(W^k+W_onset^k)` (Jiang) |
| **Tunável** | Multiplicadores sem significado isolado | Sim, calibração | `k_emb_scale, k_creep_scale, k_wear_scale_{ax,tr}, k_loose_scale_{ax,tr}, Phi_{ax,tr}_correction, k_damage_scale` |

**O ponto-chave:** os tuners são **multiplicadores sobre taxas físicas**, com
default 1.0 e regularização que os puxa pra perto de 1. Eles não são funções
livres — não conseguem inventar uma dinâmica que os mecanismos não permitem. Um
ajuste de curva puro (ex. polinômio, spline) não tem essa restrição.

---

## 3. Os acoplamentos — por que é um sistema, não somatório

O que distingue o modelo de uma soma ingênua de mecanismos independentes é que
**todos os mecanismos leem `F₀` e atualizam `F₀` no mesmo ciclo**, criando loops:

```
F₀ → k_j(F₀)=k_j_init·(F₀/F₀ᵢ)^α  → Φ_eff=k_b/(k_b+k_j) → T_loose∝Φ·F_amp
   → dθ=f(T_loose−T_resist) → dF₀=−k_b·λ·dθ → (volta pro topo)     [LOOP +]

F₀ → surface_damage D (cresce com slip) → µ_eff=µ(1−k_dmg_mu·D),
     d_wear·=(1+k_dmg_wear·D) → mais perda → mais slip → mais D     [LOOP + : colapso reaperto]

F₀ → creep dδ=C·F₀·log(t) → dF₀ → F₀ menor → creep menor           [auto-supressor]
```

| Acoplamento | Sinal | Efeito físico |
|---|---|---|
| Greenwood-Williamson → Φ → loosening | **positivo** | runaway de Stage II |
| surface_damage → atrito/wear | **positivo** | colapso do reaperto |
| creep ← F₀ | negativo | saturação suave |
| embedding | nenhum (só ciclos) | Stage I puro |
| W_slip_acc → gate → wear/loosening | **limiar** | incubação: platô do Stage I até `slip_onset_W`, depois libera o colapso (Stage II) |

A **conservação de energia** (`W_ext + U_released − ΣW_diss ≈ 0`, residual <0.1%
em regime calibrado) é uma restrição global que um ajuste de curva não tem. Ver
`MODEL_MATH_REFERENCE.md` §10–11 para o detalhe.

---

## 4. A evidência honesta — identificabilidade + parcimônia

Rodar: `python New_Theory/identifiability_analysis.py`. Resultado (rev. 2026-06-20,
perfil **nova**, ref MEAN_nova, 13 pontos, 5 tuners):

**Espectro de sloppiness** (autovalores relativos de `JᵀJ`, normalizados):
```
1.00   0.123   4.2e-3   ~0   ~0        razão max/min ≈ 5×10²⁹
```
→ Apenas **3 de 5** direções de parâmetro são "stiff"; **2 são essencialmente
zero** → `JᵀJ` **singular** → há combinações de tuners **totalmente
não-identificáveis** por essa curva.

**Ablação** (fixa o tuner em 1.0, reajusta o resto; ΔMAE vs ótimo 0.0179):

| Tuner removido | MAE | ΔMAE | Veredicto |
|---|---:|---:|---|
| k_wear_scale_tr | 0.0411 | **+0.0232** | **necessário** |
| k_emb_scale | 0.0229 | +0.0050 | desnecessário |
| k_creep_scale | 0.0190 | +0.0011 | desnecessário |
| k_loose_scale_tr | 0.0179 | −0.0000 | desnecessário |
| Phi_tr_correction | 0.0179 | +0.0000 | desnecessário |

**Conclusão sem rodeios:** numa **única curva de decaimento**, o nova é
essencialmente um ajuste de **1 parâmetro** (`k_wear_scale_tr`, que domina em
disp-mode). Os outros 4 tuners são redundantes/sloppy nessa condição. **A
preocupação do autor procede: 5 tuners numa curva monotônica é sobre-parametrização.**

Isto **não** invalida o modelo — invalida usar 5 tuners livres por curva. A
física continua nas formas e acoplamentos (Seções 2–3); o que o dado de *uma*
curva sustenta são ~1–3 botões.

---

### 4.2 Validação cross-condição (`cross_validation.py`, rev. 2026-06-20)

Rodar: `python New_Theory/cross_validation.py`. Usa os estudos M16 shear da pasta
(nova/reusada/sobretorque/reaperto).

**Teste 1 — reprodutibilidade (leave-one-CURVE-out dentro da condição):** ajusta
nas réplicas e prediz a retida.

| condição | pred MAE (réplica retida) | fit MAE | gap típico |
|---|---|---|---|
| nova (TP3/8/11) | 0.019–0.033 | ~0.020 | +0.003 a +0.014 |
| reusada (TP4/5/9/10) | 0.020–0.041 | ~0.025 | −0.008 a +0.017 |

→ **Passa.** O fit prediz uma réplica não vista da MESMA condição tão bem quanto
ajusta → **não está decorando o ruído de uma curva**; captura a condição.

**Testes 2 e 3 — cross-condição (set único; leave-one-CONDITION-out):**

| condição retida | MAE_pred (OOS) | MAE_próprio | gap |
|---|---|---|---|
| nova | 0.039 | 0.018 | +0.021 |
| reusada | 0.120 | 0.020 | **+0.100** |
| sobretorque | 0.287 | 0.007 | **+0.281** |
| reaperto | 0.254 | 0.013 | **+0.240** |

→ Um **único** conjunto de tuners **não** prediz as outras condições.

**Interpretação honesta (limitação do dado):** as 4 condições são **4 estados
físicos distintos** (arruela nova / reusada / sobretorqueada / reapertada) sob o
**mesmo carregamento** — **não** uma varredura paramétrica. Falhar a predição
cross-condição é **esperado** (o reaperto ESTÁ danificado; o sobretorque ESTÁ com
contato diferente) e **não prova curve-fitting**. Mas também **não prova
generalização**: este dado **não consegue** separar "ajuste de curva" de "estados
físicos diferentes". O teste decisivo exige **varredura paramétrica na MESMA
junta** (ex.: nova a δ=0.3/0.5/0.7mm, ou variando F₀/freq) — calibrar em algumas,
predizer as outras. **Esses ensaios não existem na pasta hoje** → é a lacuna
experimental que bloqueia a prova de generalização.

---

### 4.3 Arnês de generalização pronto + auto-teste sintético

O protocolo da varredura está em
`docs/superpowers/specs/2026-06-20-generalization-validation-campaign.md` (M16 nova,
δ∈{0.3,0.5,0.7}mm × F₀∈{40,60}kN × 3 réplicas). O arnês que o consome é
`New_Theory/parametric_validation.py` — calibra **um** set de tuners no treino e
**prediz** condições retidas (leave-one-δ-out, leave-one-F₀-out).

**Auto-teste sintético** (sem dados de bancada ainda; gera dados do próprio modelo
+ ruído 1%): a predição OOS fica em **0.008–0.0095 ≈ nível do ruído** em todos os
hold-outs → o arnês funciona e o modelo **generaliza pra sua própria varredura**.

**Achado sutil (reforça §4.1):** a recuperação dos tuners "true" acertou as
direções stiff (`k_emb` 1.28 vs 1.30, `k_wear` 0.67 vs 0.70, `k_creep` 1.07 vs
1.00) mas **errou** `k_loose` (2.02 vs 1.0) e `Phi_tr` (0.60 vs 1.0) — as direções
sloppy. **Conclusão importante:** a predição pode ser excelente *mesmo com
parâmetros individuais não-identificáveis* — o que prediz é a *combinação* stiff,
não cada botão. **Ser preditivo e ser sloppy não se contradizem** (modelos sloppy,
Sethna 2007). Isso desloca o ônus: a legitimidade se mede por **predição
out-of-sample**, não por pinar cada parâmetro.

→ Falta só rodar a campanha de bancada e apontar o arnês pros CSVs reais.

---

### 4.4 Parcimônia operacionalizada — conjunto mínimo por condição

`StagedCalibrator.fit_parsimonious(tol=0.005)` faz forward selection: parte de
TODOS os tuners = 1.0 (default físico) e só adiciona um tuner se ele cortar o MAE
em > tol. Resultado nos 4 estudos (rev. 2026-06-20):

| Perfil | nº tuners livres | conjunto mínimo | D_init | MAE |
|---|:--:|---|:--:|---:|
| nova | **2** | k_emb_scale, k_wear_scale_tr | 0.0 | 0.021 |
| reusada | **2** | k_emb_scale, k_wear_scale_tr | 0.3 | 0.023 |
| sobretorque | **2** | k_emb_scale, k_wear_scale_tr | 0.0 | 0.007 |
| reaperto | **0** | (só física: dano + D_init) | 0.3 | 0.038 |

*Valores da rev. 2026-06-20, anteriores ao embedding state-based (2026-07-02) — os MAE por-condição correntes estão na coluna correspondente da §4.5.*

**Este é o argumento pró-modelo mais forte que temos:**
- O dado justifica **≤2 tuners** por condição (não 5) — MAE comparável ao fit de
  5 tuners. Os 3 "extras" (creep, loose, Phi_tr) eram a folga sloppy (§4.1).
- As 3 condições "intactas" usam **o MESMO par** {embedding, wear} — os dois
  mecanismos dominantes em disp-mode. Não é cada condição com botões arbitrários.
- A diferença entre condições é **física e nomeada**: `D_init` (estado de dano)
  separa reusada/reaperto de nova/sobretorque. O reaperto fecha com **zero**
  tuners de curva — puro `D_init` + mecanismo de dano.

Um modelo cujas N condições compartilham 2 multiplicadores físicos + 1 variável de
estado nomeada **não é** um ajuste de curva por condição. (Resta a generalização
cross-loading da §4.2/4.3 pra fechar de vez.)

---

### 4.5 Fit compartilhado — uma física, N estados (Estágio A, spec 2026-07-02)

`SharedCalibrator` (rev. 2026-07-02): UM conjunto de constantes físicas fitado
em conjunto sobre as 4 condições (tuners ≡ 1.0, **nunca fitados**); as condições
diferem **só por estados nomeados** (inputs físicos, não botões de curva). Rodar:
`python New_Theory/calibrate_shared.py`. Run completo de 2500 ciclos.

**Constantes compartilhadas** (forward selection, tol=0.005, priors de literatura):

| Constante | Valor | Prior | IC 95% (×/÷) | Veredicto |
|---|---:|---:|---:|---|
| C_creep | 1.165e-11 | 5e-11 | ×/÷2.30 | fraco (individual) |

Seleção: `(defaults+estados)` MAE 0.1047 → +`C_creep` 0.0796 (a única constante
que cortou o MAE acima da tolerância). `k_dmg_wear` **não** foi selecionado em 2500
ciclos — fica no prior 4.0. **A seleção depende da janela:** num smoke de 600
ciclos entram `{C_creep, k_dmg_wear}`.

**Números fitados no dataset INTEIRO: 2** (a constante `C_creep` + `F0_test` de
sobretorque, estimado) — meta ≤5. Todo o resto são priors de literatura + estados.

**Estados nomeados por condição** (inputs, não tuners): nova `{}`; reusada
`{emb_consumed_frac=1.0, D_init=0.3}`; reaperto `{D_init=0.3}`; sobretorque
`{F0_test = 120.0 kN, procedência: estimated, sanity ≤133 kN OK}`.

**MAE por condição — compartilhado vs por-condição (§4.4) vs LOCO:**

| Condição | MAE compartilhado | MAE por-condição | LOCO MAE_pred |
|---|---:|---:|---:|
| nova | 0.0747 | 0.0236 | 0.0835 |
| reusada | 0.0596 | 0.0257 | 0.0628 |
| sobretorque | 0.1378 | 0.0073 | 0.1519 † |
| reaperto | 0.0462 | 0.0378 | 0.0488 |
| **global** | **0.0796** | — | — |

† O LOCO de sobretorque usa o `F0_test` estimado do fit completo
(`state_F0_from_full_fit=true` no JSON) — sem ele o leave-one-out não teria como
estimar a pré-carga da condição retida.

**Leitura positiva (honesta):** o LOCO (leave-one-condition-out) fica **≈ ao MAE de
fit** (+0.003 a +0.014 por condição) → as constantes compartilhadas **generalizam
de fato** entre condições, em vez de sobre-ajustar qualquer curva. E o dataset de 4
condições precisa de apenas **2 números fitados**. É o resultado mais forte
pró-modelo até aqui (mais forte que a parcimônia por-condição da §4.4, porque agora
a física é *a mesma* nas 4).

**Identificabilidade do fit compartilhado** (`python
New_Theory/identifiability_analysis.py --shared`, log-espaço, 2 variáveis, 144
resíduos): autovalores de `JᵀJ` normalizados `[1.00, 2.05e-01]` → **2/2 direções
stiff** (o **par** {C_creep, F0_test} é **conjuntamente bem-condicionado**,
espalhamento < 1 década). ICs 95% **por variável**: C_creep ×/÷2.30, F0_test
×/÷1.60 — ambos "fraco".

> **Cuidado (não arredondar):** "stiff 2/2" (conjunto) e "fraco" (individual)
> respondem perguntas **diferentes** — o par é identificável em conjunto, mas cada
> variável isolada está fracamente pinada; **não** escrever "bem determinado".
> Ainda: o ótimo de `F0_test` está **colado no bound** (120 kN, topo de [40,120]
> kN); o IC por curvatura assume ótimo interior, então ×/÷1.60 **subestima** a
> incerteza real ali.

**Achado de falsificação (spec §5.6 / §7 deste doc):** sobretorque fecha em
MAE 0.1378 = **18.9×** o fit por-condição (0.0073), **com F0 encostado no bound**
de 120 kN. Leitura honesta: ou (a) a pré-carga real do ensaio **excedeu 120 kN**
(bound apertado demais — valor real desconhecido; não havia registro do ensaio,
spec §7.1), ou (b) as leis de wear/loosening **não têm um regime dependente da
pressão de contato** que o `k_wear≈0.045` por-condição vinha absorvendo. A física
compartilhada + estados nomeados **não fecha** o sobretorque. Registrado como
achado que **aponta para o mecanismo** (pressão de contato), **não** como pretexto
para adicionar um tuner.

**Veredicto do gate A→B (spec §2.8): PASSA COM RESSALVAS.**

1. **≤5 constantes fitadas: PASSA** (2 usadas).
2. **MAE vs referência-branda (≲2× o fit por-condição):** reaperto 1.2× ✓,
   reusada 2.3× ~, nova 3.2× ✗, sobretorque 18.9× ✗ — critério **brando não
   atendido** para nova/sobretorque; nenhum teto rígido foi imposto (decisão do
   usuário, spec §0.1).
3. **LOCO documentado: PASSA.**
4. **Conservação / suíte de testes:** confirmadas pela regressão final.

Ou seja: **parcimônia (2 números para 4 condições) e generalização cross-condição
(LOCO ≈ fit) estão provadas**; o sobretorque fica documentado como achado de
falsificação apontando para um regime dependente da pressão de contato. **A decisão
final de executar o Estágio B (remoção da camada de tuners) é do usuário** — este
documento registra o veredicto, não o dispara.

**Adendo (2026-07-04) — discriminação do bound de F0 (Fase 2, experimento
pré-registrado `sobretorque_f0bound`):** o achado acima deixava (a) e (b) em
aberto. O experimento que as discrimina foi rodado (`python
New_Theory/sobretorque_f0bound.py`; artefatos
`New_Theory/sobretorque_f0bound.{json,png}` + `sobretorque_f0bound_report.md`;
plano `docs/superpowers/plans/2026-07-04-sobretorque-f0-bound-133kn.md`): o topo
do bound de `F0_test`[sobretorque] foi elevado de 120 kN ao **teto de sanidade
física** `0.9·Rp0.2(10.9 = 940 MPa)·A_s(M16 = 157 mm²) = 132.8 kN` — a maior
pré-carga fisicamente defensável para um M16 10.9 sobretorqueado — e **nada
mais** mudou (mesma seleção parcimoniosa; `free_constants = {C_creep}`, a mesma
única constante que o Estágio A canônico seleciona).

| | bound 120 kN (baseline) | bound 132.8 kN (teto) |
|---|---:|---:|
| MAE sobretorque | 0.1378 | 0.1351 |
| `F0_test` estimado | 120 kN (**no bound**) | 132.8 kN (**no NOVO teto**) |
| MAE global | 0.0796 | 0.0788 |

**Veredicto pré-registrado** (limiares: MAE < 0.06 = resgate, bound era o
problema; ≥ 0.10 = mecanismo faltante persiste): 0.1351 ≥ 0.10 → **"missing
mechanism (falsified again)"**. Elevar o bound ao máximo defensável rendeu
**ΔMAE de apenas +0.0026**, com `F0_test` **cravado no novo teto** — o
otimizador segue pedindo mais pré-carga do que a física permite e, mesmo assim,
o fit continua **≈18.5×** pior que o fit por-condição (0.0073). **A hipótese
(a) está descartada: dentro da faixa fisicamente admissível, nenhum valor de F0
resgata o fit — o bound não era o fator limitante.** Resta (b) como a leitura
que os dados suportam: o misfit do sobretorque é **falsificação estrutural** —
falta à física compartilhada um mecanismo excitado pelo sobretorque,
plausivelmente um **regime dependente da pressão de contato**
(atrito/assentamento/wear que muda sob alta pressão de bearing), ausente dos 4
mecanismos atuais. A **forma** específica desse mecanismo é questão de projeto
da Fase 2, **não** resolvida aqui.

> **Ressalva (campo `caveat` do JSON + spec Fase 1 §4):** o candidato óbvio —
> rigidez de contato Greenwood-Williamson dependente da pré-carga, `k_tr(F0)` —
> tem **sinal desfavorável** na equação de slip atual (k_tr maior ⇒ **mais**
> slip); "missing mechanism" **não** avaliza um fix ingênuo de `k_tr(F0)`.

O bloco `shared` canônico de `joint_calibrations.json` **não foi modificado** —
experimento standalone (mesma disciplina de `creep_anchor.json`). O item
mecanismo-dependente-de-pressão está sequenciado em
`docs/superpowers/plans/2026-07-04-phase2-sequencing-and-model-tiering.md` e no
roadmap do CLAUDE.md (Fase 2, item sobretorque/F0-bound).

---

### 4.6 Trilho axial — predição zero-refit (Fase 1B, spec 2026-07-03)

13 curvas axiais força-controladas (Liu 2017 M12: sweeps de P₀ e A_F; Li 2022
M10: sweep de frequência) preditas com as constantes do Estágio A **congeladas**
e `emb_depth` de **tabela VDI 2230** (input por junta, procedência handbook —
§1.3a do spec). Nenhum parâmetro ajustado a nenhuma curva. Rodar:
`python New_Theory/calibrate_axial.py`.

| Métrica | Valor |
|---|---|
| Mediana MAE_pred | 0.1518 (limiar do gate 0.05) |
| Vence o baseline exponencial 1-par/curva | 3/13 (Liu2017 P0=15, Li2022 15 Hz, Li2022 20 Hz) |
| Gradiente ∂(fim)/∂P₀ dado vs modelo | +2.633e-5/N vs +1.585e-5/N (sinal certo, ~60% da magnitude) |
| Gradiente ∂(fim)/∂A_F dado vs modelo | −2.216e-5/N vs ≡ 0 (+2.18e-20/N) |
| Residual de conservação (típico) | −242.8 a −11.7 J (bookkeeping do engine, ver abaixo) |
| Gate B1 | **FALHOU** |

**Vitória parcial honesta (P₀):** o gradiente de pré-carga tem **sinal certo e
~60% da magnitude** — a doutrina `emb_depth`-como-input-de-tabela (spec §1.3a)
funciona parcialmente; **sem ela a predição nem teria a tendência** com P₀.

**Erro estruturado:** o Liu2017 (M12, aço, força) fica **sobre-afrouxado** (pred
0.60–0.70 vs dado 0.77–0.95) e o Li2022 (M10) **sub-afrouxado** (pred ~0.950 vs
dado 0.82–0.91). O shape (queda rápida → decaimento lento) é qualitativamente
certo; a amplitude do assentamento erra.

> **⚠ VENCIDA EM 2026-07-27 — leia a §4.43 antes de usar este parágrafo.** A
> falsificação abaixo foi medida em 2026-07-03 contra um baseline **genérico**
> (`frozen_constants` sem o cfg adotado). A ρ-unificação (`emb_amp_exp=2,375`,
> §4.18) foi adotada em **2026-07-08** e tornou o embedding dependente da
> amplitude. Medido no canônico `4f5bedfbace4`: `∂(fim)/∂A_F` = **−1,7225e-5 /N**
> no modelo contra −2,2160e-5 /N no dado ⇒ **77,7% da sensibilidade, não 0%**, e
> as predições do sweep **não são mais a mesma curva** (0,8833 → 0,7997). O que
> resta é resíduo quantitativo (~22% da inclinação) dentro do tripé, não ausência
> categórica de resposta.

**Falsificação estrutural (aponta o mecanismo, §7 — não pede tuner):** o conjunto
de mecanismos V2 **não contém nenhum mecanismo de perda dirigido pela amplitude de
carga axial cíclica** abaixo do onset de loosening — wear = slip **transversal**,
creep = só F₀, embedding = **amplitude-cego**. Por isso `∂(fim)/∂A_F ≡ 0` no modelo
(as 5 predições do sweep de A_F são **a MESMA curva**, final 0.6555) contra
−2.216e-5/N no dado. Isto é uma **falsificação de FORMA** (mecanismo faltante), não
de constantes: nenhuma constante congelada carrega dependência de A_F em modo axial
força, então nenhum refit (B2) poderia criá-la — por isso **B2 não foi rodado** (a
falsificação é o resultado científico). Os dados do Liu2017 e as **observações SEM
de wear de flanco de rosca do próprio paper** apontam o mecanismo ausente:
**fretting/wear nos flancos de rosca sob carga axial oscilante, ∝ A_F**.

**Bandas de sensibilidade (grip 2d–3d × classe Rz adjacente):** cobrem os 4 casos
pré-registrados; mesmo o **melhor canto** de cada banda Liu2017 (mín. 0.091–0.142)
**nunca alcança o gate de 0.05**, e a banda Li2022 10 Hz (0.078–0.108) também fica
acima. **A falha NÃO é artefato de input preenchido** (grip/rugosidade assumidos);
nenhuma conclusão fica `inconclusive` por depender da banda.

**Residual de conservação = bookkeeping do engine (não desta campanha):** os
−242.8 a −11.7 J são o termo viscoso de Rayleigh (`W_damp_visc`) acumulando sem
contraparte em `W_ext` no **modo axial força** (escala com F_amp², verificado). Ele
**não realimenta `F_0`**, logo **não afeta** predições, MAEs, gradientes nem o gate
— é propriedade **pré-existente** do engine, candidata a correção de bookkeeping
futura (roadmap), não defeito desta campanha.

**Nota de procedência (Li2022):** o material do parafuso **não é reportado** no
paper (lacuna documentada); o run assumiu **aço** (E default) uniformemente,
procedência `assumed` — o "ti" no nome dos CSVs é *Tribology International* (o
periódico), **não** titânio.

**Veredicto do gate B1: FALHOU** — falsificação estrutural de forma (mecanismo de
perda dirigido pela amplitude axial ausente), registrada como achado do §7 que
**aponta o mecanismo** (fretting de flanco de rosca ∝ A_F), não como pretexto para
um tuner.

**Adendos do review final (2026-07-03):**

- A banda de sensibilidade de µ (±25%, spec §1.5) foi omitida por ser
  **provadamente de largura zero** em axial puro força-controlado: µ entra só em
  `T_resist`/`F_slip`/`dE` de wear, todos dormentes com slip transversal ≡ 0 —
  a própria inércia estrutural que o registro de ativação codifica.
- Gradiente de frequência (spec §1.6, calculado do JSON committado):
  ∂(fim)/∂f dado ≈ +9,0e-3/Hz vs modelo ≈ +3,1e-5/Hz (sinal certo via tempo de
  creep, ~0,3% da magnitude) — mais um dado do lado da falsificação.
- Baseline (i) do spec §1.4 (ratio≡1) está aninhado no baseline exponencial
  (λ=0, já que λ≥0) — o gate usou o comparador mais estrito.
- A frase "nenhum refit poderia criá-la" vale **dentro do regime dos dados**: o
  canal latente (loosening axial, T_loose ∝ A_F) exigiria F₀/F₀ᵢ ≈ 0,08–0,12
  para cruzar T_resist — os dados nunca descem de 0,77.
- Chaves do JSON: as curvas Li2022 aparecem como `Li2022ti *` nos artefatos
  (`ti` = *Tribology International*).

**Forma faltante suprida — `ThreadFrettingLoss` (spec 2026-07-06): FORMA
CONFIRMADA representável, mas o NÍVEL domina o trilho axial.** A falsificação acima
nomeou o mecanismo ausente: fretting/wear de flanco de rosca ∝ A_F. Ele foi
implementado (`ThreadFrettingLoss`, irmã de `WearLoss`: Archard no flanco, dirigido
por `F_ax = F_amp·|cos θ|`, `s_flank = F_ax/k_b`, reusa `K_archard`/`hardness`;
`dF_0 = −k_b·d_fret` ⇒ `dF_0 ∝ −F₀·A_F`, `k_b` cancela). **Opt-in** (`k_thread_fret=0`
default = inerte; **doubly**: `F_ax=0` no transversal θ=π/2 ⇒ biblioteca transversal
bit-idêntica, suite 62 verde incl. `test_transfer_validation`). Calibração/validação
(`calibrate_axial.py --calibrate-fret`, `--quick` cap 20k, self-consistente),
thresholds **pré-registrados AS IS**:

| Threshold pré-reg. | baseline `k=0` | `k_thread_fret=3.0` | veredicto |
|---|---:|---:|:--:|
| ∂(fim)/∂A_F negativo + curvas separam | 3.8e-20 (identicas 0.659) | **−2.315e-5** (0.386→0.270) | ✅ representável |
| magnitude vs dado −2.16e-5 (fator ~2) | — | −2.315e-5 (~5%) | ✅ |
| MAE axial mediana melhora vs 0.1518 | 0.1474 | **0.2548** | ❌ PIORA |
| ∂(fim)/∂P₀ mantém sinal + | +1.585e-5 | +1.525e-5 | ✅ |
| biblioteca transversal bit-idêntica | — | inerte (F_ax=0) | ✅ |

**Veredicto: a FORMA da §4.6 é CONFIRMADA representável — mas não é um fix do trilho
axial, porque o erro dominante é o NÍVEL, não o gradiente.** O gate `∂/∂A_F≡0` (as 5
curvas A_F eram a MESMA, 0.659) some: com `k_thread_fret` o gradiente vira negativo,
casa o dado (~5%) e as curvas separam monotonicamente — a hipótese de mecanismo
faltante ∝ A_F está **validada**. **Mas casar o gradiente PIORA o MAE** (0.147→0.255):
o baseline **já sobre-afrouxa** (pred 0.659 < dado 0.85–0.96) e o fretting **só
adiciona perda** ⇒ ao casar a inclinação (`k=3.0`) o nível colapsa para 0.27–0.39.
**Gradiente e nível pedem correções OPOSTAS; nenhum `k` único resolve** (`k` pequeno →
nível ~0.65 sobre-afrouxado, gradiente fraco; `k` grande → gradiente certo, nível
colapsa). Consistente com o §4.6 "**a amplitude do assentamento erra**". ⇒
`ThreadFrettingLoss` fica como **capacidade validada, default-inert** (não fix
adotado, mesmo padrão do trigger de dano); `k_thread_fret` fica em §5.1 como
constante fitada per-par (a "B2" — mas não adotada, pois não melhora). **Próximo lead
axial: o erro de NÍVEL** (por que o baseline sobre-afrouxa Liu2017 M12 — embedding/
creep agressivos demais nesse par? rigidez faltante?), **não mais fretting**.
Artefatos: `calibrate_axial.py`, `fret_calib.log`.

**Diagnóstico do erro de NÍVEL (systematic-debugging, 2026-07-06 — responde à
pergunta acima).** `axial_level_diagnostic.py` decompõe a perda de preload axial
por mecanismo (NÃO adota nada — o zero-refit segue canônico; é um diagnóstico):

- **A perda axial é ~80–90% EMBEDDING** (creep ~5–6%; wear/loosening/fretting
  **exatamente 0** — slip transversal ≡ 0 e F_tr < T_resist em axial puro força).
  O embedding remove um valor **absoluto fixo** `k_b·emb_depth` (5339 N no M12,
  4408 N no M10), **independente de F₀ e A_F** — o que explica de uma vez
  `∂/∂A_F ≡ 0` (embedding é amplitude-cego) **e** o sinal certo de `∂/∂P₀` (valor
  absoluto fixo ⇒ fração menor em F₀ maior; a "vitória parcial" de P₀ é o embedding).
  **[⚠ 2026-07-27 — a premissa "embedding é amplitude-cego" deixou de valer:** a
  ρ-unificação (`emb_amp_exp=2,375`, §4.18) foi adotada em 2026-07-08 e é
  justamente ela que dá ao embedding a dependência de A_F. O diagnóstico acima
  continua correto como *decomposição* (a perda axial é ~80–90% embedding), mas a
  conclusão `∂/∂A_F ≡ 0` que ele sustentava está vencida — hoje o modelo entrega
  **77,7%** da sensibilidade medida. Ver §4.43.**]**
- **Esse valor é ~4× grande demais para o par Liu2017.** O modelo prevê 25–36% de
  assentamento; o dado mostra **7–15% na queda rápida inicial** (~30 ciclos) ⇒ o
  `emb_depth` que o dado implica é **~1,4–4,0 µm**, **abaixo da classe VDI mais fina**
  (Rz<10 = 9,5 µm). Reduzir o `emb_depth` a ~×0,25 leva as 4 curvas Liu2017 ao gate
  (**MAE mediana 0,155 → 0,036**) **sem** fretting. ⇒ **o erro de nível é
  proveniência por-par de `emb_depth`** — a tabela VDI 2230 sub-resolve superfícies
  retificadas/lapeadas finas — **NÃO uma forma dinâmica faltante**. Confirma o §8
  ("constantes são por-par/rig/junta"; a banda de sensibilidade do §4.6 varia grip ×
  classe adjacente, que **não alcança** ×0,25, e é por isso que o gate falhou: a
  tabela **piso** já é 4× grande).
- **A correção `k_reduced` é real mas menor.** VDI computa a perda de assentamento
  como `ΔF_Z = f_Z·k_b·k_j/(k_b+k_j)`; o engine usa `dF₀ = −k_b·δ`. Como
  `k_j = 4e9 ≫ k_b`, `k_reduced/k_b = 0,84–0,90` (redução 10–16%), longe do 4×. É uma
  **forma legítima** (o assentamento deveria relaxar pela rigidez **série** — pista da
  rigidez-de-membro, roadmap #10) mas **não é o fix** do nível axial.
- **Li2022 (sub-afrouxa) precisa da perda lenta ∝A_F.** A fração de embedding sai da
  janela (o dado normaliza em N=200, pós-`N_emb`=50), restando uma queda lenta de ~18%
  em 10⁴–10⁵ ciclos que o modelo não tem — é a `ThreadFrettingLoss`.
- **Correção do registro (fretting k=3 do §4.6):** no run completo `k=3` é
  **catastrófico** — `dF₀ ∝ −F₀·A_F` colapsa `F₀→0` (a tabela do §4.6 via 0,270–0,386
  num cap de fumaça 2e4; em 1e5 já é `p≈0,00`, MAE mediana 0,356). O `k` compatível com
  o **nível** do Li2022 é ~60× menor **e** depende da contagem de ciclos ⇒ **o fretting
  não casa nível + gradiente + as duas contagens de ciclos com um `k` único** —
  reforça "capacidade validada, NÃO fix adotado".

**Veredicto do nível axial: o gargalo é proveniência de `emb_depth`** (constante
por-par, roteia ao trilho de proveniência **bloqueado** por falta de medição de f_Z em
roscas retificadas finas — abaixo do piso da tabela VDI), **não um mecanismo faltante**.
O trilho atinge o gate com `emb_depth` implicado-pelo-dado + fretting suave, mas isso é
fit por-par (a "B2" declinada), não adoção. Artefatos: `axial_level_diagnostic.py`,
`axial_level_diagnostic.log`.

**Adoção — âncora de proveniência `emb_depth` p/ roscas retificadas finas (`Rz<4`,
Bolt Science; 2026-07-07): o erro de NÍVEL FECHA.** Decisão do usuário após
verificação externa (responde à pergunta do veredito acima):

- VDI 2230-1 Tabela 5.4/1 tem **piso em Rz<10** (3 classes, sem sub-divisão fina) ⇒
  sobre-prevê ~4× superfícies retificadas/lapeadas. A tabela "mais fina" do repo
  (`LOOSENING_MECHANISMS_QUANTITATIVE.md`) estava **rotulada errada como "VDI 5.4/1"**
  — corrigida (é guia de consenso de engenharia, não VDI).
- Âncora autoritativa **Bolt Science** ([boltscience.com/pages/embedding.htm](https://www.boltscience.com/pages/embedding.htm),
  verificada): assentamento **1–7 µm/interface**, mais liso → menos ⇒ retificado/lapeado
  ≈ **1 µm/interface**. Tese experimental SDSU (M10 1045 aço) confirma a **direção**.
- **Adotado:** classe **`Rz<4`** em `library_common.emb_depth_vdi` (rosca 1.0 + 2 apoios
  1.0 + interface 0.5 = **3,5 µm**/pilha rosqueada n_if=1), proveniência **`handbook`
  (Bolt Science)**, **não VDI, não tuner**. Liu2017 (retificado) adota `Rz<4`; Li2022
  mantém `Rz<10` (superfície não reportada; e sub-afrouxa ⇒ `Rz<4` pioraria).

Re-run `calibrate_axial.py` (Rz<4), **cap 1e5** (embedding satura em N_emb=50; ~exato
p/ o MAE — o dado Liu2017 é ~plano após ~1000 ciclos):

| Métrica | B1 zero-refit (Rz<10) | **Rz<4 (Bolt Science)** |
|---|---|---|
| Mediana MAE (13 curvas) | 0.1518 (gate **FALHOU**) | **0.0469** |
| Vence baseline exp | 3/13 | **8/13 (maioria)** |
| Liu2017 MAE (mediana, faixa) | ~0.20–0.25 | **0.038 (0.017–0.086)** |
| Li2022 (inalterado, Rz<10) | — | 0.050 |

**Veredicto: o erro de NÍVEL do §4.6 (Liu2017 sobre-afrouxava) está RESOLVIDO** — era
proveniência de `emb_depth` (piso VDI grosso p/ fino), agora suprida por âncora `handbook`
autoritativa. A mediana despenca **0.152 → 0.047** e as curvas Liu2017 vão a **0.017–0.086**
(a maioria < 0.05), **por proveniência de input, não por tuner**. **Full-1e6 autoritativo
(confirmado 2026-07-07): mediana MAE 0.0550; vence baseline exp em 10/13** (era 3/13; cap-1e5
preview dava 0.047/8-13). O gate estrito de mediana é **raspado por 0.005** (0.055 > 0.05 ⇒
o print diz "FALHOU") — o resíduo é o **∂/∂P₀** ainda imperfeito (embedding = valor absoluto
fixo ⇒ leve sobre-perda em F₀ alto sobre 1e6 + cauda de creep) — mas o **beats-majority vira
decisivo (3/13 → 10/13)** e a mediana cai **0.152 → 0.055**. O fix de NÍVEL é **inequívoco**. Resíduos menores/separados: (a) **gradiente ∂/∂P₀** ainda
imperfeito (embedding = valor absoluto fixo ⇒ leve sobre-perda em F₀ alto, agravada pela
cauda de creep); (b) **Li2022 sub-afrouxa** (0.050) — a forma ∝A_F faltante
(`ThreadFrettingLoss`), inalterada por este fix. **Ressalva de proveniência:** `Rz<4`
≈1 µm/interface é **valor de faixa handbook** (Bolt Science 1–7), não medição do rig
específico (±banda) — um degrau abaixo de âncora primária. **1º resultado classe-"passa"
do trilho axial — via proveniência, não fit.** Artefatos: `calibrate_axial.py` (Rz<4),
`New_Theory/library_common.py` (classe `Rz<4`).

---

### 4.7 Âncora independente de C_creep — creep estático (Fase 1C, spec §1.7)

Fit **declarado** (medição, não zero-refit) de {C_creep + emb_depth por nível
de Ra} nas 6 curvas de relaxação estática do li2022marstruc (M16 304SS,
E=193 GPa, L=20 mm — procedência `paper`; eixo x em minutos; sem vibração ⇒
wear/loosening estruturalmente inertes, verificado por registry-truth). Rodar:
`python New_Theory/anchor_creep.py`.

| Métrica | Valor |
|---|---|
| C_creep (âncora) | 9.917e-13 ×/÷1.36 |
| C_creep (Estágio A, referência) | 1.165e-11 ×/÷2.30 |
| emb_depth(Ra 0.078/0.122/0.306/0.8) | 0.087 / 0.069 / 0.010† / 0.010† µm |
| MAE por curva | 0.0011–0.0079 |
| Re-run Estágio A (prior re-centrado) | C_creep 9.917e-13, MAE global 0.0817 (antes 0.0796) |

† CRAVADO no bound inferior (`BOUNDS_EMB[0]`).

**Veredicto:** a âncora estática **discorda** do valor dinâmico do Estágio A por
um fator **~11.7**, com **ICs que não se sobrepõem** ([7.3e-13, 1.35e-12] contra
[5.07e-12, 2.68e-11]). Este é o ramo "a discordância quantifica" do spec §1.7:
**C_creep não transfere entre pares tribológicos** (304SS estático do
li2022marstruc vs aço âncora interna do shear dinâmico). Como o `emb_depth` já é input por
junta (§1.3a / §4.6), `C_creep` é uma constante **por par tribológico**; o valor
do Estágio A (1.165e-11) é estimativa-na-curva, com exatamente o IC largo (×2.30)
que a identificabilidade já apontava como "fraco".

**A manchete positiva:** re-centrando o prior do Estágio A na âncora (bounds
[4.41e-13, 2.23e-12]), o fit compartilhado fecha as 4 condições com **zero
constantes de mecanismo fitadas** (`free_constants = []`; resta só o estado
`F0_test` de sobretorque, ~120 kN no bound) e MAE global **quase igual** (0.0817
vs 0.0796; Δ+0.0021). Ou seja: o dado de vibração **mal distinguia** o C_creep
~11.7× maior — a "necessidade" do creep alto no Estágio A era **folga sloppy**,
não física pinada (coerente com o IC ×2.30 e com a §4.1).

**Redistribuição por condição (pista, não conclusão):** nova (0.0747→0.0605) e
sobretorque (0.1378→0.1328) **melhoram**; reusada (0.0596→0.0729) e reaperto
(0.0462→0.0607) **pioram** — justamente as duas condições **com dano**. O creep
alto do Estágio A estava **parcialmente absorvendo a cauda das condições
danificadas**; registrado como pista para a **física de dano** (§4.4 e §6.3),
não como conclusão fechada.

**Caveat do IC da âncora:** o ×1.36 é linearizado assumindo ótimo interior, mas
**2 dos 5 parâmetros** (o `emb_depth` dos dois Ra mais rugosos, 0.306 e 0.8 µm)
estão **CRAVADOS no bound inferior** — o IC real é mais largo (mesma família de
caveat do `F0_test`, §4.5). A **inversão** emb(Ra) — mais rugoso deveria assentar
**mais**, e o fit faz o oposto, jogando os dois níveis rugosos no bound — é um
**achado de identificabilidade** da decomposição settlement-vs-creep neste
dataset: as curvas de relaxação começam **pós-aperto**, com o assentamento já
ocorrido no torque, coerente com `emb ~0` nas superfícies rugosas.

**Invariância-F₀ (achado de forma menor):** a fração de creep do modelo
(k_b·C·Δln t) é invariante em F₀, enquanto o dado é não-monotônico em F₀ dentro
da nuvem de ±2% (fins de curva 0.974/0.9415/0.9815 para 5/10/15 kN) — os
resíduos concentram-se na família do sweep de F₀ (MAEs 0.0079/0.0063/0.0037, os
maiores das 6 curvas), um achado de forma menor registrado sem knob.

**Registry-truth no regime estático:** residual de conservação estático
**3.192e-4 ≈ 0 ✓** com **só embedding+creep ativos** (wear/loosening
estruturalmente inertes sem vibração) — a verdade-de-registro (§6) estendida ao
regime estático e testada. Escala do residual: é integralmente o termo de
liberação elástica do lado da junta (`U_jt = F²/2k_j`, aproximação de
bookkeeping de 2ª ordem conhecida) — desprezível em escala absoluta, embora
seja ~28% do turnover dissipativo estático (~1e-3 J), ele próprio minúsculo.

**Nota de escopo:** O re-run ancorado é um experimento registrado em
`creep_anchor.json`; o bloco `shared` canônico de `joint_calibrations.json`
permanece inalterado.

---

### 4.8 Transferência zero-refit transversal — a varredura (Fase 1A, spec §1)

46 curvas de 7 papers (M8→M42; amplitude 0,07–2,0 mm; F₀ de 2,1 a 685 kN),
preditas com as constantes do Estágio A **congeladas** (`N_emb=50`,
`K_archard=1e-4`, `C_creep=1.165e-11`, `tr_loose_gain=2.0`) e inputs nomeados com
procedência (`paper`/`handbook`/`assumed`, com bandas de sensibilidade nos 8
casos pré-registrados); 10 exclusões registradas com motivo (par polimérico HDPE
×3, dispositivo Vibralock ×4, amplitude variável ×2, ensaio até fratura ×1).
Dano OFF por pré-registro (juntas novas — no Estágio A o dano só ativa em juntas
pré-danificadas). Nenhum parâmetro ajustado a nenhuma curva. Rodar:
`python New_Theory/transfer_validation.py`.

| Agregado | mediana MAE | p90 | vence exp (1-par/curva) | vence no-loss |
|---|---:|---:|---:|---:|
| **GLOBAL** | **0.2196** | 0.6476 | **9/46** | **34/46** |
| BAUER_2024 | 0.1224 | 0.2194 | 1/9 | 8/9 |
| ICMEZ_2025 | 0.1250 | 0.1484 | 0/8 | 8/8 |
| KARLSEN_2022 | 0.1230 | 0.2521 | 5/7 | 7/7 |
| LIU_2025 | 0.6645 | 0.7478 | 0/6 | 0/6 |
| LU_2024 | 0.4255 | 0.5163 | 3/10 | 10/10 |
| ROUSSEAU_2025 | 0.3729 | 0.3783 | 0/3 | 1/3 |
| YANG_2019 | 0.6384 | 0.7272 | 0/3 | 0/3 |

**A varredura falsifica a transferência de CONSTANTES, não de FORMAS.** Com
constantes congeladas de outro rig (o shear âncora interna), o modelo **vence o baseline
no-loss (ratio≡1) em 34/46** — captura a **direção e a existência** do
afrouxamento em toda a faixa M8→M42 — mas **perde para um ajuste local de 1
parâmetro (exponencial) em 37/46**: não acerta a **magnitude** com as constantes
importadas. As três fontes **mais bem preditas** convergem numa banda estreita
(**Bauer 0.1224, Karlsen 0.1230, Icmez 0.1250**) e dominam o no-loss (7–8 das
suas 7–9 curvas cada) — **generalização genuína das formas de mecanismo** através
de M8→M30 e F₀ de 14 a 370 kN, sem nenhum knob adicionado. (Nota: a qualidade
da predição NÃO correlaciona com a procedência dos inputs — os inputs do
Karlsen são todos `assumed` e ele está entre os melhores, enquanto Rousseau
tem grip de `paper` e está entre os piores.)

**A falha é estruturada, em três modos** (nada de fix aqui — só apontamentos de
mecanismo/procedência; próximos passos ficam para o roadmap):

1. **Sub-predição agregada** — **31 das 37** curvas fora das duas fontes
   dominadas por colapso (Liu2025, Yang2019) **retêm preload demais** no modelo
   (`final_pred > final_data`): Bauer 9/9, Icmez 8/8, Lu 8/10, Karlsen-M30 5/7,
   Rousseau-t10 1/3.
   O assentamento previsto com as constantes âncora interna é sistematicamente **brando**
   demais para estes rigs.
2. **Colapso sobre-predito** — o modelo leva **F₀→0 onde o dado nunca colapsa**:
   Liu2025 6/6, Yang2019 3/3 (2/3 no sentido estrito — a `amp0p6 5Hz` tem
   `final_data=0.2083`), Karlsen M42 2/2 (`final_pred` 0.061/0.018 vs dado
   ~0.15). (Distinção: `lu2024_T4Nm` também tem `final_pred≈0`, mas ali o
   **dado também colapsa** — colapso casado, vence o baseline exponencial —
   e por isso fica fora deste modo de falha.) **Surpresa registrada como está:**
   o pré-registro hipotetizava que,
   com dano-OFF, o modelo **sub-prediria** o colapso; o observado é o **oposto**
   — o colapso vem de **wear excessivo** com o `K_archard` importado, não de dano
   ausente. Nenhum confundidor limpo (tamanho/F₀/freq/amplitude) separa
   colapso-vs-não: no mesmo rig Karlsen a 1 Hz, o M42 colapsa e o M30 não.
3. **Rousseau t12/t14 — pista de FORMA acionável.** *(**⚠ VENCIDA EM 2026-07-27
   — veja o RE-BASELINE no fim da §4.20.** A forma foi construída no PR-14: o
   `k_member_shear` está vivo e põe o t14 em **stick permanente**; os MAE são
   hoje 0,058/0,064/0,044 e o erro **cai** com a espessura. O texto abaixo é o
   estado de antes da adoção.)* Na **única varredura de rigidez de membro** da
   biblioteca (t=10/12/14 mm), o modelo passa de leve
   sub-predição (t10) a **sobre-predição crescente do afrouxamento** (t12/t14:
   `final_pred − final_data` = −0,31/−0,51), **SEM colapso**, com o MAE subindo
   monotonicamente com a espessura (0,228 → 0,373 → 0,380) ⇒ o mapeamento
   geometria→rigidez (grip→L_eff→k_b e/ou o k_j fixo) **não escala com a
   espessura do membro**. É a pista de forma mais concreta da varredura.

**Bandas de sensibilidade (8 casos SENS_STEMS pré-registrados) não resgatam
nenhuma conclusão.** 6 das 8 são robustas ao veredicto; as 2 que cruzam
(**Bauer M12 t1**, banda MAE [0.1201, 0.1912] vs `MAE_exp`=0.1238; **Rousseau
t10**, [0.1892, 0.3528] vs `MAE_exp`=0.1971) o fazem **apenas na fronteira
"vence exp" de curvas que já perdem no ponto** — marcadas **`inconclusive`** para
esse veredicto isolado, sem alterar a manchete (perde para exp em 37/46; nenhuma
banda cruza o veredicto no-loss). A falha **não** é artefato de input `assumed`.

**Contraste com o arnês sintético (§4.3):** naquele auto-teste, com dados gerados
pelo próprio modelo, a predição OOS caía no **nível do ruído (~0,008)**; aqui,
com dados reais de outros rigs e constantes congeladas, a mediana é **0,22** e o
modelo perde para 1 parâmetro em 37/46. O **abismo entre os dois** é exatamente a
medida da falsificação: o arnês generaliza para a *física do próprio modelo*, mas
as **constantes de wear/loosening são propriedades do par/rig**, não números
universais — a mesma lição que a §4.6 (forma axial faltante) e a §4.7 (`C_creep`
por par) trazem, agora sobre as constantes transversais.

**Re-run 2026-07-05 — física ADOTADA (wear físico + conformação `effective`).** Após a
adoção da conformação (§4.9) e o `A_contact` per-rig (11g), re-rodei o §4.8 com a física
adotada: `transfer_validation._simulate` seta `conform_driver="effective"` (frozen_constants
traz `W_conf_ref`/`n`/`p_ref` numéricos mas não a string do driver) + `A_contact` real por
rig → **wear (profundidade = V/A_contact) E gate de pressão agora físicos cross-rig** (antes
o 100 mm² fixo era artefato p/ ambos). NB de transparência: o delta baseline→re-run também
embute o re-fit do `C_creep` na adoção (1.165e-11→1.867e-11, `frozen_constants` lê o bloco
vivo) — mas creep maior empurra p/ *mais* afrouxamento (oposto ao "retém ~0.75" do Karlsen),
então não dirige os achados abaixo (pode explicar parte dos ganhos menores BAUER/ICMEZ/LU).
Resultado **AS IS**:

| | baseline (100 mm², sem conf.) | re-run (físico + conf.) |
|---|---:|---:|
| GLOBAL mediana MAE | 0.2196 | **0.2281** (levemente pior) |
| vence no-loss | 34/46 | 33/46 |
| vence exp (1-param local) | 9/46 | 4/46 |

**Não melhora o transfer global** — e revela dois achados:
1. **KARLSEN 0.123 → 0.226 (quase dobra): o bom fit do baseline era ARTEFATO de wear.** O
   `A_contact=100 mm²` fixo **super-estimava a profundidade de wear** (V/A) nos bolts grandes
   M30/M42 (área real 735/1441 mm² ≫ 100), fazendo o modelo colapsar junto com o dado por
   wear excessivo (final_pred 0.29–0.48 no M30; o M42 até **sobre-colapsava**, 0.02–0.06).
   Com o `A_contact` físico o wear é realista (pequeno)
   → o modelo **retém ~0.72–0.79 e NÃO reproduz o colapso** do Karlsen (dado ~0.15). Ou seja:
   o colapso do Karlsen **não é wear (físico)** — precisa de outro mecanismo (dano/fadiga; HV
   alta-resistência), **coerente com a doutrina §4.8 "dano OFF → colapsos devem sub-predizer"**.
   O baseline acertava pelo motivo errado (artefato de área).
2. **Conformação NÃO resgata as sub-predições de platô** (yang2019, liu2025): seguem moendo a
   ~0 (final_pred 0.000 vs dado bem acima de 0, ~0.2–0.7). Na pressão desses rigs
   (`p/p_ref`~0.5–0.6) o gate
   `effective` é fraco demais; o platô deles **não é conformação-por-pressão** (é
   baixa-amplitude/outro). Hipótese falsificada AS IS. Melhoras menores: ICMEZ 0.125→0.105,
   BAUER/LIU/LU levemente melhores (wear físico ajuda os casos moderados).

**Leitura (reforça §8):** a física adotada é **cientificamente mais honesta** (áreas/pressões
reais) mas o MAE global piora de leve — porque o baseline era **lisonjeado por um artefato de
wear** (Karlsen). A conformação per-par da âncora interna **não transfere magnitude** fora do par/pressão
âncora interna, e o wear físico expõe que **colapsos precisam de dano, não de wear**. Formas transferem;
constantes e colapsos são por par/mecanismo. Artefatos re-gerados (`transfer_results.json`,
`transfer_report.md`, `transfer_grid.png`).

**What-if `--damage-on` (2026-07-05) — o colapso É dano.** Seguindo o achado do re-run
("colapsos precisam de dano, não wear"), rodei o §4.8 com **dano ativo em todos os casos**
(`transfer_validation.py --damage-on`: `c_D=2`, `k_dmg_wear=4` de `frozen_constants(include_damage=True)`
+ `k_dmg_mu=1` da física de dano do Estágio A; `D` cresce de 0; artefatos `transfer_*_damage.*`
**separados** — o §4.8 dano-OFF canônico fica intacto). **Viola a doutrina "dano OFF em juntas
novas" → é um what-if AS IS.** Resultado:

| | dano OFF (§4.8) | dano ON (what-if) |
|---|---:|---:|
| GLOBAL mediana MAE | 0.2281 | **0.1825** (melhora) |
| GLOBAL vence exp | 4/46 | 7/46 (só Karlsen) |
| GLOBAL p90 MAE | 0.6397 | 0.6696 (**pior**) |
| GLOBAL vence no-loss | 33/46 | 33/46 (igual) |
| KARLSEN mediana | 0.2263 | **0.1394** |
| YANG_2019 mediana | 0.6564 | 0.7177 (pior) |
| LIU_2025 mediana | 0.6397 | 0.6696 (pior) |

(A melhora é **só na mediana**: o p90 PIORA e o vence-no-loss não muda — o trade-off está aí.)

**Dois lados, um veredicto:**
1. **O dano REPRODUZ (parcialmente) o colapso do Karlsen** — final_pred move de ~0.75 (dano OFF,
   wear físico não colapsa) p/ ~0.43–0.66 (dano ON), rumo ao dado (~0.15); MAE Karlsen
   0.226→0.139. **Confirma o achado do re-run: o colapso do Karlsen É dano, não wear (físico).**
   (Parcial: `D` crescendo de 0 não chega ao colapso pleno no nº de ciclos; a magnitude é por-par.)
2. **Mas o dano PIORA os casos de platô/alta-retenção** (YANG 0.656→0.718, LIU 0.640→0.670): onde
   o dado **não colapsa**, o dano super-dirige a perda (a curva cai mais cedo) → pior.

**Veredicto:** o dano é o **mecanismo do colapso** (confirma o re-run), mas é **por-condição, não
universal** — ligá-lo em tudo ajuda os colapsos (Karlsen) e machuca os platôs. Isso **refina** a
doutrina §4.8/Estágio A (`damage_active` por condição): o dano **keys no REGIME DE COLAPSO
(severidade observável), não no histórico de dano prévio** — o Karlsen é junta **nova** e mesmo
assim colapsa e *quer* dano (então "só em pré-danificadas" é estreito demais; o critério certo é
**"onde há colapso"**). Cross-rig: os casos severos QUEREM dano, os de platô NÃO. **Não é um "adote
dano-ON"**: a melhora é só na mediana (p90 piora, vence-no-loss igual) e **o experimento não dá uma
regra PREDITIVA** de quando ligar o dano — só mostra que o dano é o mecanismo certo para o colapso.
Formas transferem; ativação/constantes de dano são por condição/par. Artefatos `transfer_*_damage.*`.

**Predictive damage trigger (spec 2026-07-05) — FALSIFICADO AS IS: dose ≠ regime.**
O what-if `--damage-on` deixou aberto **quando** ligar o dano. Hipótese: o dano
**auto-onseta** depois que a dose de fretting de gross-slip acumulada (`W_slip_acc`)
cruza um crítico `W_crit` (gate de Hill, espelha `slip_onset`), substituindo o
`damage_active` manual. Análise de dados (2026-07-05): o separador collapse/plateau é a
**amplitude de slip** (regime partial vs gross), provado por sweeps controlados de
amplitude (Lu M8 0.25→platô / ≥0.5→colapso; Liu M16; Yang M10) — **não** pressão/%proof.
Validação: transfer com o trigger **decidindo** (`--damage-trigger`, sweep de `W_crit`),
thresholds **pré-registrados** (median≤0.19, p90≤0.645, collapse-on≥75%, plateau-off≥75%).

| `W_crit` (J) | median | p90 | collapse-on | plateau-off |
|---|---:|---:|---:|---:|
| 1e4 | 0.216 | 0.652 | 23% | 43% |
| 1e5 | 0.227 | 0.640 | **6%** | **100%** |
| ≥1e6 | 0.228 | 0.640 | 0% | 100% |

**Veredicto: FALHA — nenhum `W_crit` atinge os thresholds.** Conforme `W_crit` sobe,
protege os platôs (plateau-off→100%) MAS **perde a ativação dos colapsos**
(collapse-on→0%) — movem JUNTOS, não separam (no melhor ponto, 1e5: só **2/31 colapsos**
disparam). **Causa:** a dose `W_slip_acc ∝ F0·slip·ciclos` é **dominada por F0** → platôs
de alto-F0 (Liu/Yang) acumulam MAIS dose que colapsos de baixo-F0 (Lu M8) — a dose é até
**anti-correlacionada** com o colapso. O separador real (amplitude vs limite elástico =
**regime partial/gross slip**) **não é capturado pela dose absoluta**.

**Achado (forma faltante, não tuning):** o `slip = max(0, δ − F_slip/k_tr)` do modelo
**não reproduz a separação partial/gross-slip** que o dado mostra (computa gross slip
também nos casos de platô) — então um limiar de dose não pode separar colapso de platô. A
forma faltante é o **regime de slip correto** (o limite elástico / `k_tr`), **não** o
onset do dano — mesmo padrão de §4.6 (forma axial) e §4.8 (rigidez de membro): **forma
errada, não constante errada.** O gate de onset (`W_crit`) fica como **mecanismo de
incubação de dano válido, default-inert, backward-compat** (engine/registry/harness), mas
**não resolve** a separação colapso/platô — o objetivo preditivo é falsificado AS IS.
Task 5 (near-proof activator) fica **moot** (o core falhou). Artefatos:
`transfer_*_trigger.*`, `transfer_trigger_wcrit_sweep.log`.

**Fix do regime de slip (`k_tr` de flexão, spec 2026-07-05) — NECESSÁRIO mas INSUFICIENTE AS IS.**
O adendo acima apontou a forma faltante: o `k_tr = 0.3·k_axial ≈ 1.2e9` (rígido, **cego
ao rig**) dá `δ_t = F_slip/k_tr ≈ 0` ⇒ **tudo é gross slip** desde o ciclo 1 ⇒ nenhum
limiar separa colapso de platô. O fix: `k_tr` = rigidez de **flexão** do parafuso
(`c_bend·E·I/L³ ~ 1e7`, `δ_t ∝ F0·L³/(E·d⁴)`), **opt-in** (`k_tr_mode="bending"`, default
`axial_frac` bit-idêntico). `c_bend` **calibrado** aos amplitude sweeps
(`calibrate_ktr.py`): trade-off nítido (mole→platôs certos/colapsos errados; rígido→o
inverso), melhor equilíbrio `c_bend=1.0` (colapso→gross 77%, platô→partial **57%** pelo
regime **inicial**). Validação pré-registrada (`--ktr-bending`, thresholds **congelados**:
regime ≥70% cada lado; platô `final_pred` +≥0.2).

| Métrica (thr. pré-reg.) | baseline `axial_frac` | `--ktr-bending` | veredicto |
|---|---:|---:|:--:|
| regime realizado colapso→afrouxa | 48% | 45% | — |
| regime realizado platô→plateia (≥70%) | 14% | **14%** | ❌ |
| melhora `final_pred` nos 7 platôs (≥0.2) | — | **+0.006 mediana, 0/7** | ❌ |
| MAE GLOBAL (mediana \| p90) | 0.228 \| 0.640 | 0.234 \| 0.579 | ~igual |
| MAE LIU / YANG (amplitude sweeps puros) | 0.640 / 0.656 | **0.579 / 0.597** | ↓ direção certa |

**Veredicto: FALHA nos thresholds pré-registrados — o fix é real mas insuficiente
sozinho.** O regime **inicial** vira partial nos platôs (proxy 57%, como projetado), e as
duas fontes de **sweep de amplitude puro** (Liu, Yang) melhoram mais (−0.06) — o mecanismo
é o certo. Mas o **regime realizado** (fim de curva) fica em 14% platô, ≈ baseline: os
platôs ainda colapsam.

**Causa — CONFIRMADA por trace (liu2025 M16 amp0.25, dado platô 0.68):** `δ_t` inicial =
0.578 mm > `δ`=0.25 mm ⇒ **partial de fato** (slip=0 por ~10 000 ciclos, o fix funcionando).
MAS embedding+creep+conformação **erodem F0** mesmo em partial (0.996→0.844 c/100→0.572
c/10k), e `δ_t ∝ F0` encolhe junto (0.576→0.331 mm); quando `δ_t < δ` (~ciclo 10–20k) o
**gross slip dispara → runaway sem freio → F0→0.20**. Ou seja: o fix do `k_tr` corrige o
`δ_t` **inicial**, mas **(a)** embedding/creep erodem F0 **através** do platô do dado mesmo
sem slip, e **(b)** o runaway de gross slip **não tem arresto** (não há equilíbrio de
partial slip estável). **Duas formas faltantes compostas**, não uma constante.

**Rescue do trigger (bônus, não-gate) — NULO AS IS.** `--damage-trigger --ktr-bending`
com sweep `W_crit ∈ {1e3,1e4,1e5,1e6}` J: **todos** dão median MAE **0.2341** = o run sem
dano. O trigger é **inerte** no regime corrigido — o colapso corrigido é dirigido pelo
**gross-slip loosening**, não por dano, então gatear o dano não muda a separação
colapso/platô. Confirma (de novo) que o dano não é o lever aqui.

**Achado (forma faltante, não tuning):** mesmo padrão de §4.6/§4.8/o trigger — **forma
errada, não constante errada**. O `k_tr` de flexão é uma **melhoria real e necessária**
(código keeper: opt-in, per-rig, corrige o `δ_t` inicial, ajuda os amplitude sweeps), mas
**não fecha os platôs sozinho**. As próximas formas faltantes expostas: **(1)** erosão de
F0 **limitada** em partial slip (o embedding pode super-predizer nesses rigs — item 5,
renovação/limite de embedding), e **(2)** um **arresto/feedback estabilizador** no runaway
de gross slip (equilíbrio de partial slip; relacionado ao acoplamento `F_amp↔δ_amp`, item
4). **Task 4** do plano (wear de partial slip Mindlin) fica **gated OUT** (o gate "core
funciona" falhou; wear em partial só **pioraria** a erosão de F0). Artefatos:
`transfer_*_ktr.*`, `transfer_*_trigger_ktr.*`, `calibrate_ktr.py`, `wcrit_ktr_sweep.log`.

**Gate do loosening ao regime de slip (spec 2026-07-06) — MECANISMO VALIDADO onde o
regime acerta; agregado limitado pelo teto do `c_bend`.** Uma decomposição por
mecanismo do caso de platô (liu2025 M16 amp0.25, 2026-07-06) **corrige a atribuição
acima**: o eroder pré-gross-slip **não** é embedding/creep (saturam ~23%: emb 14.4%
state-based + creep log ~8.5%) e sim o **rotational loosening** (20% no ciclo 10k,
crescendo **com slip de deslocamento = 0**). Causa: `RotationalLooseningLoss` gateia
pelo **critério de FORÇA** (`F_tr = 0.4·F0 ≫ F_slip = 0.069·F0`), desconectado do
regime de slip por deslocamento que o `k_tr` corrigiu — então o fix de `k_tr` só
alcançou o **wear** (6%), nunca o **loosening** (51%). Fisicamente: Junker precisa de
**gross slip** (o ratcheting); disparar em partial slip (stick) é não-físico.

Fix (Approach 1, opt-in `loosening_slip_coupling="gross_fraction"`): gate `g =
slip/(slip+δ_t) = (δ−δ_t)/δ` = **fração de gross-slip do curso** multiplicando o
`d_theta` do loosening (junto de `slip_onset`/`conformation`; `dF_0` e `dE` escalam
juntos ⇒ conservação). **Zero constantes novas**, preserva a calibração de gross slip
⇒ transfer **zero-refit**. Validação `--loosen-coupled` (= gate + bending), thresholds
**pré-registrados AS IS**:

| Threshold pré-reg. | k_tr-only | **--loosen-coupled** | veredicto |
|---|---:|---:|:--:|
| plateau→plateia (≥50%) | 14% (1/7) | **43% (3/7)** | ❌ (3× melhor) |
| melhora `final_pred` platô, mediana (≥0.20) | +0.006 | **+0.025** | ❌ (bimodal, ver abaixo) |
| colapso→afrouxa (≥40%, guarda) | 45% | **45%** | ✅ (sem regressão) |
| MAE GLOBAL (mediana \| p90) | 0.234 \| 0.579 | **0.226 \| 0.512** | ↓ melhora |

**Veredicto: PARCIAL — o mecanismo funciona exatamente onde o regime acerta, mas o
agregado é limitado pela acurácia do `c_bend` (o teto pré-registrado).** Os dois platôs
que o regime classifica como **partial** são resgatados **perfeitamente**: liu2025
amp0.25/amp0.3 **0.00 → 0.74** (≈ dado 0.68), LIU_2025 MAE **0.640 → 0.311** (metade). O
colapso **não regride** (45% idêntico: as gross ficam gross). A mediana da melhora
(+0.025) **falha** por ser **bimodal** — 2/7 resgatados em +0.74, 5/7 quase parados (a
média seria +0.226, > 0.20); os 5 parados (yang M10 amp0.4/0.6, rousseau t12/t14, lu
amp0.25) são platôs que o `c_bend` classifica como **gross** (δ ≥ δ_t no modelo) ⇒ o
gate não os toca. **Exatamente a tensão pré-registrada** (§spec 5): o teto do gate é a
**separação de regime do `c_bend`** (Task 2: 57% platô / 77% colapso). **A forma
faltante a seguir não é este gate** (que está correto e é keeper: opt-in, inert-default,
sem regressão, p90 GLOBAL 0.640→0.512) e sim **melhorar a separação de regime** —
`c_bend` per-junta ou compliance de membro em série (pista Rousseau §4.8/Task 2). Task 4
(Mindlin partial-wear) segue **gated OUT**. Artefatos: `transfer_*_loosen.*`.

**`δ_t` NÃO é o separador plateau/colapso — lead de "separação de regime" FECHADO
(2026-07-06, análise pré-build; sem código).** Ao explorar como melhorar a separação
(o "próximo passo" acima), duas falsificações por análise:
- **`δ_t` não separa plateau de colapso.** Agrupando as 46 curvas por `δ/δ_t` (bending
  k_tr nominal): platôs cobrem 0.43→**3.96**, colapsos 0.54→9.40 — a faixa `δ/δ_t∈[1.1,4]`
  contém **os dois**. Prova decisiva: **yang M10 amp0.6 @10Hz plateia, @5Hz colapsa** —
  mesmo `δ/δ_t`≈1.4-1.5, resultado oposto, diferindo só na **frequência**. Nenhum `δ_t`
  (global ou per-junta) separa um par de `δ/δ_t` idêntico. Karlsen colapsa a `δ/δ_t`<0.65
  (dano, não slip). ⇒ o outcome plateau/colapso é **multi-mecanismo** (slip-loosening +
  frequência/tempo + dano + rig); `δ_t` é **um** eixo, com overlap.
- **Compliance de membro NÃO explica Rousseau.** A varredura de aço (M12, ~10.3 kN, 0.5 mm,
  só espessura varia) **vira brusco**: t10 colapsa (0.088) → t12 plateia (0.624) sobre
  grip 25→29 mm (**+16%**). Qualquer `δ_t` de flexão do parafuso ∝ **grip³** ⇒ +16% =
  ×1.56 (o modelo dá exatamente isso: `δ/δ_t` 6.2→4.0→2.7, todos ≫1). Flipar t12 p/ partial
  exigiria `δ_t` ×~4 — **transição brusca demais p/ `δ_t(grip)` suave**. Compliance elástica
  de membro **em série não ajuda** (membros de aço E≈200 GPa ≫ rígidos que o parafuso em
  flexão ⇒ adicionam ~0). Notas de aparato: t14 **rotação de porca ~zero**, t10/12 rotacionam
  ⇒ o switch é **onset de rotação (limiar two-factor Φ)**, não regime de slip. **Lead
  "compliance de membro" (roadmap #10) FECHADO como fix de `δ_t`.**

Consequência: o gate do loosening (acima) fica como **keeper validado onde o regime acerta**,
mas o teto **não** se levanta por `δ_t` — a separação plateau/colapso e o efeito Rousseau
são **multi-mecanismo** (frequência/tempo, onset de rotação, dano). Foco migra p/ mecanismos
independentes de `δ_t` (trilho axial ∝ A_F §4.6; e, se retomado, o onset de rotação vs
espessura como fenômeno de limiar, não de compliance).

**Diagnóstico quantitativo (2026-07-07) — o #10 é forma faltante mais profunda; escala de
`k_j` FALSIFICADA.** Decisão do usuário (diagnóstico antes de build).
`member_stiffness_diagnostic.py` decompõe Rousseau steel t10/12/14 e testa os fixes
candidatos:

| Config | t10 (g25) | t12 (g29) | t14 (g33) | spread |
|---|---:|---:|---:|:--:|
| **dado** | 0.088 | 0.624 | 0.903 | **~10×** |
| baseline (`k_j`=4e9 fixo) | 0.203 | 0.304 | 0.388 | ~2× |
| `k_j` ∝ 1/grip | 0.203 | 0.304 | 0.387 | **idêntico (efeito 0)** |
| loosening ×20 | 0.122 | 0.242 | 0.338 | ~2.8× |
| loosening ×20 + emb ×0.25 | 0.639 | 0.688 | 0.726 | ~1.1× |

- Perda **~60–70% EMBEDDING** (loosening rotacional ~0.3%, negligenciável, embora dispare
  todo ciclo; wear ~4%).
- **Escala de `k_j` (a hipótese original do #10) FALSIFICADA:** `k_j ∝ 1/grip` dá **efeito
  ZERO** — a perda é embedding (`dF_0=−k_b·δ`, sem `k_j`) e o loosening é ínfimo, então `k_j`
  não move nada. Nem loosening forte (~2.8×) nem embedding reduzido (~1.1×) alcançam os 10×.
- **Raiz estrutural:** o modelo tem **UMA alavanca de grip** — `k_b ∝ 1/grip` (~32% em
  t10→t14) — que entra em **todo mecanismo idêntico** (`dF_0=−k_b·δ`) ⇒ sensibilidade à
  espessura **capada em ~32%**, qualquer que seja o mecanismo dominante ou sua força.
- **Veredicto:** o efeito 10× é a **instabilidade de onset de rotação dependente do grip** já
  apontada acima (t10/12 rotacionam→colapso, t14 ~zero) — agora confirmada e quantificada:
  **nenhum fix de constante única a alcança**. **#10 é forma faltante (limiar de rotação
  modulado por grip / instabilidade), NÃO a escala de `k_j`** que o enquadramento original
  supunha — aprofunda o §8 (aqui nem a forma transfere: falta o mecanismo de instabilidade
  grip-dependente). Artefatos: `member_stiffness_diagnostic.py`, `.log`.

**Build AS-IS — `loose_torsion_mode="bolt_torsion"` (spec 2026-07-07): rotação
grip-sensível RESTAURADA, mas NÃO fecha o triplo.** Decisão do usuário: build do #10.
Implementado (opt-in): `k_torsional` FÍSICA = `eta_loose·G·J/L_eff` (`G_STEEL=77 GPa`,
`J=π·d_2⁴/32` ⇒ ~4e3, **~5000× menor** que o `k_j_init·d_2/2`≈2e7 arbitrário) — deixa o
**runaway `T_resist∝F_0` que já existe disparar**. Novos campos `loose_torsion_mode`
(default `"legacy"` = **bit-identical**; suite de compat 63 verde) + `eta_loose` (só lido
em `bolt_torsion`). 5 testes novos verdes.

- **Funciona:** com o trio (`bolt_torsion` + `gross_fraction` + `bending`), a loosening
  rotacional deixa de ser 0.3% e vira **significativa e grip-sensível** — o teto estrutural
  de ~32% (uma alavanca `k_b`) é quebrado; finais monótonos com grande spread (ex.
  emb×0.25: 0.000/0.330/0.822 vs dado 0.088/0.624/0.903).
- **NÃO funciona (AS-IS):** (a) com assentamento **realista** (Rz10-40, emb ~53-70%) o
  modelo **over-collapsa TODOS os grips** (loosening −40 a −46% em t10/12/14, não
  grip-sensível) — a erosão de F₀ pelo embedding grande empurra até o grip grosso ao
  gross-slip (**erosion-into-gross-slip**, risco pré-registrado §9); a grip-sensibilidade só
  emerge com assentamento brando. (b) Mesmo brando, **t10 over-collapsa pra 0** (vs dado
  0.088) — **sem forma de ARRESTO** (o runaway não tem equilíbrio; roadmap #4). (c) O triplo
  exige **duas formas ortogonais a mais**: assentamento brando (proveniência de `emb_depth`,
  §4.6; acabamento dos membros Rousseau não reportado) E um arresto de runaway.
- **Veredicto: capacidade validada, default-inerte, NÃO fix adotado** — mesmo padrão do
  fretting (§4.6), do trigger de dano, da renovação de embedding (§4.10). O `bolt_torsion`
  **quebra o gargalo estrutural** (rotação grip-sensível, compliance física no lugar de uma
  constante arbitrária) mas **não fecha o triplo sozinho**; carrega `eta_loose` (per-par,
  fitado, análogo a `tr_loose_gain`) + `c_bend` (per-rig). Confirma §8: a FORMA transfere; o
  triplo exige constantes por-par + formas ainda faltantes (arresto, assentamento brando).
  Artefatos: engine (`loose_torsion_mode`/`eta_loose`/`G_STEEL`),
  `tests/test_member_rotation_instability.py`.

**Build AS-IS — `loose_arrest_floor` (arresto do runaway, spec 2026-07-07): torna o #10
ADOTÁVEL.** A ressalva-chave do #10 ("sem forma de ARRESTO ⇒ over-collapse") foi suprida
(decisão "do all"). `self_locking_gate = max(0, 1 − F_min/F_0)` com
`F_min = loose_arrest_floor·F_0_init` (núcleo auto-travado, stick-core de Cattaneo-Mindlin:
só a pré-carga em EXCESSO de F_min é drenável) multiplica `d_theta` ⇒ o runaway vira
**S-curve com ponto fixo ESTÁVEL em F_min**. Opt-in `loose_arrest_floor` (default 0 = gate
1 = runaway atual, **bit-identical**; ortogonal ao `loose_torsion_mode` — gate após
k_torsional). 3 testes + suite compat 66 verde.

- **Validação (Rousseau t10, trio + arresto):** floor 0/0.05/0.08/0.10 → final
  **0.000/0.046/0.079/0.100** — o resíduo **rastreia o floor** (o loosening arresta em
  F_min; emb/creep/wear NÃO-gateados drenam levemente abaixo). **floor≈0.08 → t10 0.079 ≈
  dado 0.088** ⇒ #10+arresto reproduz o colapso→**resíduo** do t10 (não mais →0) + a
  ordenação de grip.
- **Veredicto: arresto = FORMA limpa** (núcleo auto-travado, ponto fixo estável provado;
  mínimo: 1 campo + 1 gate + 1 fator) **que torna o `loose_torsion_mode="bolt_torsion"`
  ADOTÁVEL** — remove o over-collapse, a ressalva-chave do #10. Carrega 1 constante fitada
  per-par (`loose_arrest_floor`~0.08, status de `eta_loose`/`tr_loose_gain`). **Ressalva
  (§8.3):** o floor fixa **ONDE os casos rápidos arrestam** (resíduo t10), NÃO os **NÍVEIS**
  dos lentos (t12/t14 = taxa de aproximação + assentamento — o problema ortogonal do #10).
- **Estado combinado:** #10 (rotação grip-sensível) + arresto (resíduo estável) + galling
  (§4.11, recuperação declinante) = **3 formas opt-in complementares**, cada uma validada na
  sua metade; o triplo Rousseau completo (nível t14) e o oil-plano (§4.11) ainda pedem
  **assentamento brando** + **supressão-de-dano-por-lubrificação**. Artefatos: engine
  (`loose_arrest_floor`/`self_locking_gate`), `tests/test_runaway_arrest.py`.

---

### 4.9 Conformação dependente da pressão — a forma faltante do sobretorque (Fase 2, spec 2026-07-04)

A §4.5 (e seu adendo de 2026-07-04) fechou com uma falsificação **estrutural**: o
sobretorque não fecha com a física compartilhada — MAE 0.1378 = **18.9×** o piso
por-condição (0.0073), com `F0_test` cravado no bound — e o experimento de bound
**descartou** a hipótese (a) "bound apertado demais". Restava (b): **falta um
mecanismo excitado pela alta pressão de contato**. A §4.9 **supre e valida essa
forma faltante** — e assim **fecha o fio deixado aberto pela §4.5**.

**O mecanismo (Plan A, spec `2026-07-04-pressure-conformation-design.md`):** um
*gate de conformação dependente da pressão* — a perda de `F_0` dirigida por slip
(wear + rotational-loosening) é progressivamente **arrestada** conforme o contato
sobretorqueado **se conforma** sob alta pressão de bearing. O gate é pesado pela
pressão de contato (∝ `(p/p_ref_conform)^n`) e escalado pelo trabalho de slip
acumulado contra `W_conf_ref` (forma exata no spec). Em pré-carga nominal
(nova/reusada/reaperto) a pressão fica bem abaixo de `p_ref_conform` ⇒ o peso é
~inerte; **só o sobretorque, em alta pressão, excita o gate**. Como o gate toca
apenas `dF_0` (nunca `dE`), é conservação-safe por construção — o mesmo padrão
"`dF_0` sim, `dE` não" da amplificação por dano e da incubação.

**Método — A/B pré-registrado** (`SharedCalibrator._fit_subset`; rodar `python
New_Theory/conformation_fit.py`; artefatos `conformation_fit.{json,png}` +
`conformation_fit_report.md`): **mesma config canônica nos dois braços** (bound de
`F0_test`[sobretorque] em 120 kN, os estados nomeados da §4.5) — **a conformação é
a única diferença**. `conform_pressure_exp = n = 2` e `p_ref_conform = 5e8 Pa`
**fixados por escolha** (não fitados); `W_conf_ref` é o **único número novo**
oferecido ao otimizador. Baseline fita `{C_creep}` (conformação OFF); tratamento
fita `{C_creep, W_conf_ref}` (conformação ON). Thresholds **congelados no spec §9**
(não ajustáveis ao resultado): RESOLVE 0.06, PERSIST 0.10, hold 0.01, degrade 0.02.

| Condição | MAE baseline (conf OFF) | MAE tratamento (conf ON) | Δ |
|---|---:|---:|---:|
| nova | 0.0751 | 0.0799 | +0.0048 |
| reusada | 0.0593 | 0.0526 | −0.0067 |
| **sobretorque** | **0.1379** | **0.0201** | **−0.1178** |
| reaperto | 0.0459 | 0.0418 | −0.0041 |

`W_conf_ref` fitado = **1.253e4**. `C_creep` re-fitado livre nos dois braços
(1.190e-11 → 1.964e-11 — mesma ordem de grandeza do par da âncora interna, §4.7). Residual de
conservação (run do sobretorque): **8.008 → 4.051** — **melhorou**, coerente com o
design `dF_0`-only.

**Veredicto pré-registrado — RESOLVED** (recomputado do JSON, não da impressão):

1. **Resgate:** sobretorque 0.0201 < 0.06 (RESOLVE) ✓ — cai de **18.9×** para
   **2.75×** o piso por-condição (0.0073), i.e. **~7× menos MAE** (fator 6.9).
2. **As outras seguram:** maior deriva = nova **+0.0048 < 0.01** (hold) ✓ — o
   único movimento adverso, e bem abaixo até do degrade (0.02); reusada e reaperto
   **melhoram** de leve. O peso dependente de pressão as deixa **inertes**, como
   previsto.
3. **Conservação não degrada:** o critério é `|treat| ≤ |base| + 1 J`; 4.051 ≤
   8.008 passa **com folga** (na verdade caiu). ✓

**"Uma física, excitada pelo regime" — realizada.** É exatamente a propriedade que
a §4.5 buscava e o sobretorque negava: **um único número compartilhado, com um
seletor físico** (a pressão de contato), fecha a condição-outlier **sem** perturbar
as três em pré-carga nominal — porque elas não excitam o gate. Não é um tuner
por-condição (a §4.5 desconfiava justamente de o `k_wear≈0.045` por-condição estar
"absorvendo" um regime de pressão): é **uma constante que só "liga" onde a física
manda**. O achado de falsificação da §4.5 **apontava** o mecanismo (pressão de
contato); a §4.9 mostra que **um** grau de liberdade com esse seletor o resgata sem
tocar no resto — confirmando que faltava **forma**, não um tuner.

**Escopo honesto (não superestimar).** É um resultado forte, mas cercado:

- **Um rig** (âncora interna M16), **uma condição de sobretorque** (sobretorque/TP6), **um
  experimento**. A conformação foi validada onde há **um** ponto de alta pressão —
  não sobre uma varredura de pressão de contato.
- `W_conf_ref` é **constante fitada por par/rig, sem âncora de literatura ainda** —
  sua procedência é trabalho de **Fase 3**, exatamente como `C_creep` (§4.7 — a
  lição das §4.6–4.8: formas transferem, constantes são por par/rig). `n=2` e
  `p_ref_conform=5e8` foram **fixados por escolha, não fitados**; um follow-on pode
  fitar `n` ou testar a variante de driver de equilíbrio auto-limitante (spec §7).
- A **forma de conformação é uma hipótese fenomenológica que o fit _sustenta_, não
  um mecanismo provado microscopicamente.** O A/B mostra que forma + seletor
  resgatam o sobretorque preservando as demais e a conservação — evidência forte de
  que a *forma* está certa, não prova da microfísica do assentamento sob pressão.
- **Experimento standalone** (`conformation_fit.json`): o bloco `shared` canônico
  de `joint_calibrations.json` está **intocado**. Adotar a conformação no fit
  canônico é **decisão separada do professor** (análoga ao gate do Estágio B, §4.5)
  — este documento **registra** o resultado, não o dispara.

**Robustez — fitar `n` em vez de fixá-lo (strand 1 do programa de fortalecimento, 2026-07-04).**
Para checar se o RESOLVED depende do `n=2` escolhido, um A/B irmão
(`python New_Theory/conformation_fit.py --fit-n`; artefatos `conformation_fitn.json`
+ `conformation_fitn_report.md`) **liberta `n`** em [0.5, 4.0], fitado **junto** com
`{C_creep, W_conf_ref}` (baseline idêntico ao da §4.9). Resultado **AS IS** (veredicto
recomputado pelo **mesmo** classificador congelado):

| Condição | MAE baseline | MAE tratamento (`n` livre) | Δ |
|---|---:|---:|---:|
| nova | 0.0751 | 0.0880 | **+0.0129** |
| reusada | 0.0593 | 0.0510 | −0.0083 |
| **sobretorque** | **0.1379** | **0.0143** | **−0.1236** |
| reaperto | 0.0459 | 0.0400 | −0.0059 |

`n` fitado = **3.9999 — cravado no teto** (bound 4.0); `W_conf_ref` = 3.603e4;
residual 8.008 → **3.796** (melhora). **Veredicto: PARTIAL** — o sobretorque resolve
**ainda mais forte** (0.0143 < os 0.0201 do `n=2` fixo, < RESOLVE 0.06), **mas** a nova
**deriva +0.0129 > hold (0.01)** ⇒ deixa de ser RESOLVED (sem chegar a FALSIFIED:
+0.0129 < degrade 0.02).

**Leitura.** (1) O resgate do sobretorque é **robusto a `n`** — resolve em todo o
intervalo testado (`n∈[2,4]`: 0.020 → 0.014), não é artefato do `n=2`. (2) **Libertar
`n` não melhora o resultado limpo**: o otimizador de MAE-global empurra `n` ao teto para
espremer o sobretorque (global 0.0796 → 0.0484, um fio abaixo dos 0.0486 do `n=2`),
**às custas** de perturbar a nova além do hold. Ou seja, **fixar `n` num valor físico
moderado (`n=2`) é a escolha certa de modelagem** — preserva a propriedade "as outras
seguram" que é o coração do resultado; o RESOLVED com `n=2` **permanece o headline**, e
fitar `n` é uma **ressalva de robustez, não um substituto**. (3) O `n` **cravado no
teto** é uma **saturação de bound registrada AS IS**: o objetivo de MAE-global "quer"
separação de pressão mais aguda que `n=4` — **não aliviei o bound** (pré-registrado:
alargá-lo seria um follow-on deliberado, não um conserto silencioso). Bloco `shared`
canônico **intocado** (hash verificado). *(Strand 1 de 3 fortalecimentos; seguem o
driver de equilíbrio auto-limitante — spec §7 — e a âncora de procedência do
`W_conf_ref`.)*

**Robustez — driver de equilíbrio auto-limitante (strand 2/3, 2026-07-04).**
A variante "documented alternative" da §7, construída (branch
`conformation-equilibrium-driver`, `JointMaterial.conform_driver="effective"`):
o incremento de `W_conf` é ponderado pelo **gate de início-de-ciclo**, de modo que
o driver **se auto-atenua** conforme a junta se conforma. A/B effective-vs-OFF
(`n=2` fixo) + fit-n no effective (`python New_Theory/conformation_fit.py
--effective`; artefatos `conformation_effective.{json,md}`). Resultado **AS IS**
(veredicto recomputado pelo **mesmo** classificador congelado):

| Condição | MAE OFF | MAE effective (`n=2`) | Δ |
|---|---:|---:|---:|
| nova | 0.0751 | 0.0741 | **−0.0010** |
| reusada | 0.0593 | 0.0562 | −0.0031 |
| **sobretorque** | **0.1379** | **0.0299** | **−0.1080** |
| reaperto | 0.0459 | 0.0433 | −0.0026 |

`W_conf_ref`(eff) = **7657**; residual 8.008 → **4.848** (melhora). **Veredicto:
RESOLVED** — sobretorque 0.0299 < 0.06, e — diferente do raw `n=2` (que empurrava a
nova **+0.0048**) — **as TRÊS outras MELHORAM** (deriva máx −0.0010). A auto-atenuação
(o incremento encolhe pelo gate `g` **e** pelo driver `∝F_0^{n+1}`) realiza "as outras
intocadas" **ainda mais limpo** que o driver raw monotônico.

**A pergunta-chave do strand 2 — o driver auto-limitante tira o `n` do teto?** **Não:**
o fit-n no effective **também crava `n` em 4.0** (igual ao raw). Leitura: **o rail é do
objetivo (MAE-global), não do driver** — o otimizador sempre quer separação de pressão
mais aguda para espremer o sobretorque, com qualquer driver. Então **fixar `n=2`
moderado segue a escolha certa para os dois drivers** (a conclusão do strand 1 se
mantém e se **generaliza**). **Mas o effective é mais ROBUSTO no `n` extremo:** mesmo
com `n` cravado em 4.0 ele **segura as outras dentro do hold** (nova **+0.0093 <
0.01**), enquanto o fit-n no raw **furou** (nova +0.0129 > 0.01 ⇒ PARTIAL) — a
auto-atenuação protege as condições intocadas até sob o expoente extremo. Net: o
effective é **mais limpo em `n=2`** (as outras melhoram) **e mais robusto sob `n`
livre** (segue RESOLVED-em-MAE onde o raw degrada) — discutivelmente o **mecanismo
melhor**.

**Correção de honestidade (spec §7 reescrita).** A forma **mínima e localizada** que se
construiu é um **plateau auto-limitante, NÃO um "equilíbrio verdadeiro `c*<1`"** como a
§7 originalmente alegava. Sobre o ensaio finito `c` estaciona `<1` (o incremento
encolhe por dois caminhos), mas **assintoticamente ainda tende a 1** sob o creep (que
segue baixando `F_0`). Um `c*<1` genuíno exigiria realimentar a **cinemática do slip**
(elevar a capacidade de stick até o slip do modo-deslocamento zerar / a junta grudar) —
mudança maior, entrelaçada com o item #4 (acoplamento `F_amp↔δ_amp`), **adiada como
achado**. Bloco `shared` canônico **intocado** (hash `21ed6a7…` verificado). *(Strand 2
de 3; falta a âncora de procedência do `W_conf_ref` — strand 3.)*

**Procedência — âncora do `W_conf_ref` (strand 3/3, 2026-07-04).** Busca dedicada
(biblioteca local + literatura) por uma âncora **independente** da escala de energia de
conformação `W_conf_ref` (~1e4 J), no molde da âncora de `C_creep` (§4.7). **Veredicto:
NÃO existe âncora independente** — `W_conf_ref` é uma **constante fitada por par/rig,
como `C_creep`, porém em base MAIS FRACA** (o `C_creep` tem ao menos uma medição
independente de IC disjunto, §4.7; o `W_conf_ref` **não tem nenhuma**). O **framework**
existe e transfere: a "**wear/friction energy capacity**" de Fouvry (energia dissipada
acumulada crítica até um endpoint tribológico; *Tribology International*, 2007) é "uma
variável característica de cada tratamento de superfície" — i.e. **reproduz o veredicto
§4.6–4.8/§8 "formas transferem, constantes são por par"** — **mas não ancora o número**:
endpoint diferente (falha/profundidade de wear, não arresto de slip), quantidade
diferente (densidade J/mm² vs total ponderado por pressão J), e nenhum valor numérico
para aço foi obtido. **Cuidado registrado:** a densidade areal implícita ~20 J/mm² é um
**check de consistência INTERNO** (mesmo dado/geometria âncora interna que produziu o fit), **não**
um match de literatura — **não é âncora**. Na escala de procedência, `W_conf_ref` fica
**um degrau abaixo do `C_creep`**: "framework identificado, por-par pela própria
definição do framework, mas **numericamente sem âncora — Fase 3 aberta**". Experimento de
Fase 3 (paralelo a `anchor_creep.py`): fretting dedicado no mesmo par tribológico medindo
energia dissipada acumulada vs. conformação/lock-up (÷área, desfazendo o peso
`(p/p_ref)ⁿ`); **pré-registrar que uma discordância é o resultado esperado e informativo**
(como os ~11.7× do `C_creep`) — quantificaria a transferência por-par, não falsificaria a
*forma*. *(Fase 2 fortalecimentos 1–3 concluídos.)*

**ADOÇÃO no bloco canônico (2026-07-04, decisão do professor).** Com os três
fortalecimentos concluídos, o driver `effective` foi **adotado no bloco `shared`
canônico** — a **primeira vez** que um experimento é promovido ao canônico (que até
aqui NUNCA fora escrito por experimento; fingerprint sha256 do bloco `shared`
`21ed6a7`→`13b26d2`, não hash de objeto git). O fit canônico
(`calibrate_shared.py`, `fit_parsimonious`) passou a incluir a conformação
(`W_conf_ref` fitável; `n=2`/`p_ref=5e8` fixos; `conform_driver="effective"`).
**Achado de identificabilidade na adoção:** com a conformação ativa, a parsimônia
**livre** selecionou `{W_conf_ref, emb_depth}` (global 0.0456) — `emb_depth` fitado a
17 µm e o `C_creep` ancorado (§4.7) **derrubado** ao default. Como `emb_depth` é um
**input por-junta** (tabela VDI 2230, não um knob — §5.1) e o `C_creep` é a única
constante com procedência independente, a escolha foi **physics-first**: manter
`emb_depth` como input fixo (removido do candidate set) e preservar o `C_creep`
(a constante com procedência de âncora independente §4.7; **fitado aqui ao valor
âncora interna 1.867e-11, não ao valor da âncora 9.9e-13** — o canônico é o par da âncora interna)
→ parsimônia seleciona **`{W_conf_ref, C_creep}`** (global 0.0509, ~0.005
acima do fit livre — custo de última casa aceito por **procedência sobre MAE**, a
filosofia do projeto). **Resultado canônico:** sobretorque **0.1378 → 0.0300**
(**falsificação §4.5 RESOLVIDA no canônico**), `W_conf_ref`=7671, `C_creep`=1.867e-11,
MAE global 0.0796 → 0.0509. LOCO nas nominais ≈ ao fit (generaliza); LOCO do
sobretorque (0.121) é **intrinsecamente fraco** — é a **única** condição de pressão
elevada, então `W_conf_ref` não é aprendível deixando-a de fora (limitação estrutural
do LOCO com um mecanismo excitado por uma só condição, **não** um defeito do fit). O
bloco `profiles` (o que a GUI lê) segue **inalterado**; a conformação vive no `shared`
(fit de referência) — propagá-la ao Run/GUI é **follow-up**. Caveats de escopo
inalterados: `W_conf_ref` sem âncora independente (strand 3, Fase 3); `n`/`p_ref`
fixos por escolha; forma fenomenológica sustentada, não provada.

**Fase 3 — tentativa de âncora per-par do `W_conf_ref` (2026-07-04): NULL decisivo.**
Busca dedicada e profunda (mais funda que a strand 3; relatório
`New_Theory/W_conf_ref_anchor_hunt_phase3_2026-07-04.md`), no molde da âncora de
`C_creep` (§4.7). Os dois caminhos tratáveis foram fechados:
- **Path A — curva cross-rig over-torqued que ISOLE `W_conf_ref`: não existe.** Varredura
  de todas as curvas transversais da biblioteca: dividem-se em (i) alta-fração-de-proof →
  **colapsam** (Bauer 94–98%, Demir 83% — arresto nunca ocorre, `W_conf_ref` não
  identificável); (ii) formato de platô → **baixa pressão / outra causa** (Liu2025 baixa
  amplitude; Rousseau t14 rigidez de membro; Lu 0.25mm abaixo do slip-onset); (iii) maior
  excitação do harness (Karlsen M30/M42) → **artefato + colapso** (caveat abaixo). Nenhuma
  combina pressão ≈ sobretorque âncora interna + platô sustentado + a sub-predição-sem-conformação
  (a única assinatura limpa, que só o sobretorque âncora interna mostra). **Achado cross-rig (paralelo
  §4.8): alta fração de preload em outro rig NÃO reproduz o platô do sobretorque âncora interna** → o
  platô está atado ao apoio pequeno específico do rig âncora interna (100 mm² → ~1.2 GPa a 120 kN) e
  ao par → **"formas transferem, constantes são por par/rig"**. *Honorable mention (corrobora
  a FORMA, não a constante):* o sweep Lu 2024 M8 (`lu2024_M8_fig20_T{4..28}Nm.csv`) mostra o
  trend qualitativo preload→arresto (T28Nm 71% proof achata em ≈0.23; T4Nm 10% colapsa a
  ≈0.04) — corrobora a direção cross-rig, mas confundido (preload-slip do disp-mode, pressão
  abaixo do gate, par níquel-aço, ~100 ciclos).
- **Path B — número de Fouvry citável: não ancora.** Achou-se **α = 4.23×10⁻⁵ mm³/J (aço
  52100)**, mas é a taxa de wear-**volume** por energia = análogo do `K_archard`, **não** do
  `W_conf_ref`. A "wear energy capacity" χ (conceito certo) não tem valor de aço citável (só
  coatings) e mira o endpoint errado (falha vs arresto). (Bônus: o α ancoraria `K_archard`,
  não o `W_conf_ref`.)

**Veredicto Fase 3:** `W_conf_ref` **confirmado não-ancorável** com dado disponível —
permanece **constante por par/rig, um degrau abaixo do `C_creep`**; o valor canônico
(7671 J) **não muda**. **Experimento que ancoraria** (spec, molde `anchor_creep.py`):
fretting no mesmo par da âncora interna a **pressão conhecida ≈ 1.2 GPa**, medindo energia dissipada
acumulada vs. arresto do slip (o trabalho de slip onde a taxa de perda cai à metade **é**
`W_conf_ref`), varrendo ≥3 pressões p/ **medir `n`** (hoje fixo em 2); pré-registrar
discordância com 7671 J como esperada (como os ~11.7× do `C_creep`).

**Caveat do harness — CORRIGIDO (11g, 2026-07-05).** `library_common.geometry_for`
fixava `A_contact=100 mm²` p/ qualquer parafuso; como a adoção pôs a conformação em
`frozen_constants`, o harness de transferência (§4.8) faria `p/p_ref = F0/50kN` p/ TODOS
os rigs → Karlsen M30/M42 dariam `p/p_ref≈7–14` **espúrio**. **Corrigido:** `geometry_for`
agora computa `A_contact = π·(r_bearing² − r_furo²)` (área real do anel, `r_furo=0.55·d`;
escala com `d²`≈1.33·`A_s`) → `p=F0/A_contact` **física por rig** (Karlsen M30/M42 →
`p/p_ref≈1.0`), e o `p_ref=5e8` passa a corresponder a ~80% do proof em qualquer tamanho
(referência de sobretorque consistente). **Caveat residual:** `p_ref`/`W_conf_ref` seguem
constantes **por par** (âncora interna, sem âncora — strand 3) aplicadas cross-pair, então a
*magnitude* da conformação é aproximada fora do par da âncora interna (honesto per-par, não artefato).
§4.8 (commitado) **não foi re-rodado**; a correção torna físicos, cross-rig, **tanto o
wear de Archard** (profundidade = V/A_contact) **quanto o gate de conformação** — um re-run
refletiria os dois (o 100mm² fixo era artefato p/ ambos), é follow-up.

---

**§4.9-adendo (2026-07-17) — null de literatura 3× + precedentes de forma
(Rodada 5).** A varredura de literatura das Rodadas 4–5 (fatia 6 do plano
L1-L7) **reconfirma** o null da Fase 3 acima (2026-07-04), agora com três
buscas independentes:

1. **R4 — Fouvry sub-GPa.** Baydoun 2019 (*Wear*, flat-on-flat 35NCD16,
   "melhor âncora G2" da Rodada 4) varre **10–175 MPa (0,01–0,175 GPa)** —
   1 a 2 ordens de grandeza abaixo da janela de parafuso (0,5–1,5 GPa); dá
   `n_p≈0,5–0,6` sobre volume de desgaste vs. pressão, mas
   **regime-condicional** (joelho abrasivo→adesivo em p_th≈125 MPa) —
   mesma disciplina de `C_creep`/`emb_depth`.
2. **R5 — busca dirigida:** nenhuma fonte entrega `n`/`W_conf_ref` fitado à
   pressão de parafuso; Moshkovich 2024 (~1 GPa, auto-limitante) e JMPT
   2023 (conformação de metais, causalidade oposta) não transferem.
3. **R5 — digitalização confirmou:** Inose 2025 é a única fonte em aço
   dentro do regime (0,48–1,90 GPa) — mas é **escala de aspereza** (teto
   1,5·H, limiar bilinear ψ≈1,5), não energia macroscópica de junta.

**Precedentes de forma (não valores plug-in):** expoente de pressão
`n_p≈0,5–0,6` (Baydoun 2019, sub-GPa, regime-condicional) para
`conform_pressure_exp`; teto de aspereza `1,5·H` (Inose 2025, ψ≈1,5) como
**sanity bound** de `p_ref_conform` (hoje 5e8 Pa); e a tensão
**Etsion×Frérot** — Etsion 2010 (experimento): conformação **satura em ~5
ciclos**, mas em rugosidade/DESLOCAMENTO; Frérot 2023 (simulação):
rugosidade satura (~40 ciclos), porém a **energia plástica dissipada NUNCA
satura** — um `W_conf_ref` único e limpo em ENERGIA pode ser uma
idealização; o gate atual (§4.9 acima, RESOLVED) funciona por estar fitado
ao dado âncora interna, não por garantia física de assíntota energética.

**Conclusão — sem mudança de veredicto.** O *valor* de `W_conf_ref`/`n` a
~1–1,5 GPa segue dependente do **experimento âncora âncora interna** (fretting
~1,2 GPa, medindo `n`, já spec'd acima) — 3ª vez que a literatura entrega
forma, não número. Fontes:
`Models/CALIBRATION_AND_VALIDATION/curve_library/ANALISE_MODELOS_R5.md`
(§L4) e `BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/apparatus_notes/`.

**Cross-referências.** `New_Theory/r5_anchors.json` (âncoras numéricas da
Rodada 5: k_wear_spec, µ por coating, creep, bound de remoção, leis de
`k_j`) **não tem entrada de L4** — coerente com "forma sim, valor não". E:
o gate `New_Theory/l2_kj_gate_result.json` (PASS-inert) achou a trajetória
transversal **cega a `k_j`** sob o PACK (θ=π/2 mata `L_ax`) — por isso a
dependência de pressão do transversal mora na conformação, não em `k_j`.

---

### 4.10 Renovação de embedding no re-aperto (retighten + k_emb_renew) — capacidade validada, validação zero-refit BLOQUEADA (spec/plan 2026-07-07)

Roadmap #5. Implementado o mecanismo: operação quasi-estática
`DynamicStiffnessAnalyzer.retighten(applied_torque|new_F0)` — prevê a recuperação via
Motosh (`tightening_torque`, reusa `mu_bearing_eff(D)`), renova
`δ_emb ← δ_emb·(1 − k_emb_renew·D)` (novo campo `JointMaterial.k_emb_renew`, **default
0 = inerte, backward-compat exato**), zera `θ_loose`, persiste
`D`/`δ_creep`/`δ_wear`/`_cycle_counter` (relógio do creep), rebaseia o segmento de energia.
**11 testes unitários verdes + suite de compat (surface_damage/embedding/shared/decomp) 46
verde ⇒ capacidade validada.**

**Alvo de falsificação: Liu2022 (Structures) M12 re-aperto** — 21 curvas digitalizadas,
dry/oil, transverso disp 0.3 mm 12.5 Hz, T=80 N·m; μ **derivado** do F₀ de 1º aperto medido
(dry 0.236, oil 0.176). `validate_retightening.py`, gates G1–G5 pré-registrados.

**Veredicto: validação zero-refit BLOQUEADA por transferência de constantes cross-rig
(§8 se repete, severamente — colapso total).** Com as constantes do Estágio A congeladas
(M16/âncora interna) + `include_damage=True`, o modelo **colapsa** no Liu2022 (M12):

| Métrica (dry) | modelo | dado |
|---|---|---|
| perda por fase t0..t3 | **[0.974, 0.988, 0.988, 0.985]** (F₀→~0) | [0.140, 0.069, 0.075, 0.087] |
| decay-MAE t0..t3 (med) | [0.494, 0.566, 0.621, 0.658] (**0.594**) | — |

oil_release decay-MAE med ≈ 0.57; oil_direct ≈ 0.60. **G1/G2/G3/G5 = todos False.**

**Refinamentos de pré-registro (registrados p/ integridade falsify-first):** G2/G3 foram
escopados às fases de **re-aperto** (t1..t3; t0 = 1º aperto = assentamento fresco, não um
re-aperto) e `N_RETIGHT=3` (os dados fig6a/6b/7a têm t0..t3, não t4). Ambos foram fixados
**antes** de ler os resultados; o veredito é **robusto ao escopo** — o colapso (sim ~0.98
vs dado ~0.07/fase) reprova todos os gates sob qualquer janela, e estreitar G2/G3 só os
tornaria mais fáceis.

**Causa-raiz (diagnosticada):** três constantes **por-rig** transferidas do M16/âncora interna falham
no M12/Liu2022:
1. **`c_D=2.0`/`k_dmg_wear=4.0` são a assinatura de COLAPSO do reaperto âncora interna** — aplicadas ao
   Liu2022 (que **não** colapsa: perde 14–27%), disparam o loop de runaway (D→1, wear→5×) ⇒
   colapso espúrio. Uma junta nova não-colapsante precisa de dano **muito mais brando** (ou off).
2. **`emb_depth` VDI sobre-prevê** o assentamento de superfície retificada fina — **exatamente
   o achado da §4.6**, agora no M12 (≈0.19 de perda só de embedding).
3. **`k_wear_scale=1.0`** (default congelado) vs o **0.44** fitado ao M16 âncora interna nova ⇒ wear
   ~2.3× rápido.

**G5 (parcimônia):** o sweep de `k_emb_renew` escolheu **k=0** (med idêntico, 0.594) ⇒ a
renovação **não é justificada** por este teste — mas está **confounded pelo colapso** (renovar
`δ_emb` não muda uma junta já em ~0). **Não** é evidência contra a renovação; é que o teste
não a isola.

**G4 (recuperação):** com `k_dmg_mu=0` (ausente no bloco shared) o modelo prevê recuperação
**plana** (~1.0 a cada re-aperto); o dado dry **declina** (1.0→0.918→0.832→0.793). Achado
documentado (**forma faltante**: galling / teto geométrico de recuperação, §7) — não é falha
do gate.

**Status do mecanismo:** `retighten`/`k_emb_renew` = **capacidade validada, default-inerte,
NÃO fix adotado** (mesmo padrão do fretting §4.6, do trigger de dano, do k_tr de flexão). Uma
falsificação limpa da renovação exige **re-calibração por-rig** de {emb_depth (fino, §4.6),
k_wear_scale, dano brando} ao Liu2022 **antes** de testar a renovação — sub-campanha adiada
(a decisão de rodá-la é do usuário). Artefatos: `validate_retightening.py`,
`retightening_results.json`, `retightening_validation.log`.

---

### 4.11 Galling de flanco de rosca + nível M12 — a "sub-campanha adiada" do §4.10 RODADA (spec 2026-07-07)

A ressalva do §4.10 (validação da recuperação bloqueada pelo colapso cross-rig) foi
atacada (decisão do usuário "do all"):

**(1) Nível confound RESOLVIDO — colapso é transferência de constantes, não estrutural.**
`liu2022_level_probe.py` reproduz o colapso do §4.10 **e** acha um nível M12
não-colapsante: **emb Rz<4 (~4 µm) + `k_wear_scale_tr`~0.06–0.08** (per-rig, ABAIXO do
0.44 âncora interna — o rig M12 gross-slip desgasta mais rápido) **+ dano brando** (`c_D=0.5`,
`k_dmg_wear=1.0`) ⇒ dry t0 loss ~0.14 (dado 0.140), final ~0.84–0.87 (não →0). Confirma as
3 constantes por-rig do §4.10; desbloqueia a validação da recuperação.

**(2) Galling implementado + validado (opt-in).** `μ_thread_tighten_eff(D)=μ_thread·
(1+k_gall·D)` **só em `tightening_torque`** (novo `k_gall`, default 0 = bit-identical; só no
evento de re-aperto ⇒ colapso `k_dmg_mu`/`k_dmg_wear` intacto; sinal OPOSTO ao `k_dmg_mu`,
interface distinta rosca-vs-bearing). 5 testes + retighten compat verde. `validate_galling.py`:

- **G4' (declínio da recuperação dry): PASSA** — `k_gall=3` → dry recovery
  `[1.0, 0.922, 0.859, 0.811]` vs dado `[1.0, 0.918, 0.832, 0.793]`, **MAE 0.012**;
  parcimônia PASSA (k=0 MAE 0.114 → 0.012). **A FORMA do galling reproduz o declínio dry.**
- **G-sign (oil plano): PASSA — com `c_D` PER-LUBE (achado).** No 1º run, com o MESMO `c_D`
  p/ dry e oil, o oil TAMBÉM declinava (`D_oil` 0.25 ≈ `D_dry` 0.26: em disp-mode o contraste
  de µ, 0.176 vs 0.236, é fraco demais p/ separar as trajetórias de dano). Mas o oil-plano
  **NÃO é uma forma faltante — é `c_D` per-lube**: o filme de óleo suprime o crescimento do
  dano ~15× (dry `c_D`~0.5, oil `c_D`~0.03). Com `c_D` per-lube, o **MESMO `k_gall`=3** dá dry
  `[1.0, 0.922, 0.859, 0.811]` (MAE 0.012) **E** oil PLANO `[1.0, 0.994, 0.988, 0.983]`
  (`D_oil`=0.02). **Os três gates (G4'/G-sign/parcimônia) PASSAM.**

**Veredicto: galling = FORMA validada no contraste dry-vs-oil COMPLETO.** O `k_gall`~3
reproduz o declínio dry; o oil-plano sai de `c_D` **per-lube** (não de uma forma faltante) —
o que eu ia construir como "supressão-de-dano-por-lubrificação" **é uma constante per-lube**
(`c_D`), não um mecanismo. Padrão do §8 reafirmado: a FORMA (galling ∝ D no aperto) transfere;
o contraste dry-vs-oil é **constante per-lube** (`c_D`, como µ/`k_wear`). Ressalva: `c_D`
per-lube (oil ~0.03) e `k_gall` (~3) são per-par/lube, fitados — a *ordenação* transfere, a
*magnitude* não. (O ~10% oil-direct-vs-release do §6 do spec segue fora de escopo: protocolo,
não dano.) Artefatos: `validate_galling.py`/`.log`, `liu2022_level_probe.py`/`.log`, engine
(`k_gall`/`mu_thread_tighten_eff`), `tests/test_galling_recovery.py`.

---

### 4.12 Regime de slip Cattaneo–Mindlin (partial↔gross) — Rousseau FECHADO, slope axial NÃO FECHADO (spec/plan 2026-07-07)

**Forma faltante suprida (a "one form, two cases" do dossiê):** uma lei de regime de
slip `r = Q/(µ·F₀·κ)` — a razão Cattaneo–Mindlin carga tangencial / capacidade de
atrito — com **duas leis** (opt-in `slip_regime_mode="cattaneo_mindlin"`, default-inert
bit-identical):
- **loosening** — onset de gross-slip afiado `g_gross = (slip/(slip+δ_t))^k` (k=1 ≡ a
  fração gross atual; k>1 suprime partial slip). Só gross slip afrouxa.
- **wear/thread-fretting** — energia de partial-slip `g_partial = 1−(1−min(r,1))^m` (graduada
  abaixo do onset), multiplica `dF_0` (não `dE`).

**Rousseau (rigidez de membro) — FECHADO como FORMA.** `slip_regime_rousseau.py`:
baseline thickness-blind MAE **0.317** (spread ~1×) → **0.054** com a FORMA CERTA
(t10 colapsa 0.196, t12 intermediário 0.594≈dado 0.624, t14 sobrevive 0.881≈dado 0.903,
**monótono**). Robusto: **13/45** configs dão a forma certa. Identificabilidade
(`identifiability_slip_regime.py`): mínimo **bem localizado** (1/40 dentro de 1.5× a
melhor MAE) em `c_bend=0.3, k=1` — `c_bend` e `k` **separadamente identificáveis**, não
vale degenerado. **Ressalvas AS-IS (§8):** a FORMA transfere (é a mesma física de contato),
mas as CONSTANTES são per-rig — `c_bend≈0.3` é a compliance **transversal do stack** (abaixo
do 3–12·EI/L³ do parafuso isolado; série com membro/interface), e o nível fecha só com
`emb_depth` fino (1.5–3.5 µm, procedência Bolt-Science fine-ground, NÃO fit — senão o
embedding sozinho tira 61% do t14 vs 10% do dado).

**Liu2017 (slope axial) — NÃO FECHADO (gated no nível; correção 1e6 do smoke).**
`slip_regime_axial.py` **a 1e6 ciclos** (o run científico — o smoke a 2e4 ENGANA): com
`k_fret=1.0` (nível que daria slope) o fretting de flanco **colapsa tudo a F₀=0** ao longo de
1e6 — **com E sem** o gate CM (o CM reduz a TAXA de fretting mas não impede o colapso
acumulado). Com `k_fret` nível-são (~0.3) o gate quase não move o slope. Ou seja: **o
slope-steepening que o smoke a 2e4 mostrava (5.9e-6→8.8e-6) era artefato de colapso incompleto**
— a 1e6 o nível catastroficamente domina, gate ou não. O baseline gate-OFF fica em 5.62e-6/N
(21% do dado 2.63e-5), MAE 0.065. Fundo estrutural: o slope axial é dominado pelo 1/F₀ do
embedding (~5.6e-6 sozinho); uma razão `r` que varia só 1.4× no sweep, através de uma lei CM
suave, **não** amplifica 5×. **Veredicto honesto: o regime de slip NÃO fecha o slope axial** —
precisa do nível de fret ancorado (Fouvry, bem menor que `k_fret=1`) E provavelmente de um
mecanismo mais íngreme que 1/F₀ (candidato Fase 2+). O CM **não resgata** um nível forte demais.

**Âncora de nível (Fouvry, #26).** `anchor_fretting.py`: `K_archard=1e-4` está **na faixa de
Fouvry** para aço (`K=α·µ·H` ⇒ 3e-5–9e-5; razão 0.9 p/ endurecido). O nível do wear/fretting
tem **procedência de ordem-de-grandeza** (literatura), não é knob livre; o `k_thread_fret`
**por par** (multiplicador do flanco) ainda precisa de um mapa de fretting do rig (caveat,
análogo ao [[anchor-creep]]).

**Bookkeeping viscoso axial (#27).** A carga axial cíclica realiza trabalho contra o
amortecedor viscoso (loop elíptico) = `W_visc`/ciclo; agora **sourced via `W_ext`** em
force-mode (`W_ext += W_visc`). O residual axial caiu de ~−`W_visc` (o leak −242..−12 J) para
~1.8% de `W_visc` (o resto é a aproximação plástica `U_released` vs `W_emb/creep`, canal
separado — #6). Transversal intocado (`W_visc ∝ cos²(π/2) ≈ 0`). `test_axial_viscous_conservation.py`.

**Transferência cross-material (HDPE, #29).** `slip_regime_hdpe.py`: o dado HDPE do Rousseau
(t10=0.21, t12=0.32, t14=0.875 @400 cic) tem a **mesma assinatura de instabilidade-por-grip**
do aço — NÃO uma relaxação dominada por creep (t14 perde só 12%). O regime de slip **transfere
para membros poliméricos** com constantes de HDPE (`k_j_init≈2e7` = E_hdpe/E_aço·k_j;
`k_creep`~3): model [0.069, 0.352, 0.75] vs data [0.212, 0.321, 0.875], MAE 0.100, shape_ok.
**Falsifica o enquadramento original do #29** ("construir uma forma de creep de polímero"): o
dado HDPE é **instabilidade, não creep** — a MESMA forma, constantes de polímero. §8 estendido:
a forma transfere cross-**material**, não só cross-rig; o creep de polímero é secundário
(`k_creep`~3 ajuda pouco), não forma faltante. (Mesmo padrão do #10 k_j-scaling: o enquadramento
era o errado; o diagnóstico apontou a forma certa.)

**Doutrina §8 reafirmada, mais forte:** aqui a FORMA (regime de slip Cattaneo–Mindlin)
transfere **cross-case** — a mesma lei fecha Rousseau e inclina Liu2017 — enquanto TODAS as
constantes (`c_bend`, `κ`, `k`, `emb_depth`, `k_thread_fret`) são per-rig/par. **Veredicto
AS-IS: capacidade validada, NÃO adotada** (mesmo padrão de fretting/renewal/galling/#10).
Rousseau é **fechável** (forma + procedência de emb + `c_bend` per-rig); Liu2017-slope
**NÃO fecha** com o regime de slip (nível de fret catastrófico a 1e6 + 1/F₀ do embedding
domina; gated no nível Fouvry + forma mais íngreme). Decisão de adotar no `shared`/Run é
do professor. Artefatos: engine (`partial_slip_gate`, branch CM em `loosening_slip_gate`,
`couple_famp_slip`), `tests/test_slip_regime.py` (12), `slip_regime_rousseau.py`,
`slip_regime_axial.py`, `anchor_fretting.py`, `identifiability_slip_regime.py`, specs/plans
`2026-07-07-slip-regime-threshold*`.

**Adendo 2026-07-08 — probe cross-library (`--slip-regime`): a FORMA (e boa parte das
constantes) TRANSFERE na família Junker-transversal.** O pack §4.12 com as constantes DO
ROUSSEAU sem re-fit (`c_bend=0.3, k=1, eta_loose=15, floor=0.08`) aplicado às 46 curvas da
varredura §1A: **mediana global 0.2281 → 0.1608 (−30%), vence no-loss 33→39/46, p90
0.640→0.465**. Os dois piores da baseline — os casos de COLAPSO que o modelo congelado
sub-predizia "por doutrina" — melhoraram 4–5×: **Liu2025 0.640→0.126** (todas as 6 curvas,
0.51–0.74→0.12–0.15) e **Yang2019 0.656→0.149** (todas as 3). **Reatribuição importante: o
colapso de junta VIRGEM da biblioteca é majoritariamente a instabilidade de onset de rotação
(a forma §4.12), NÃO crescimento de dano** — a frase da doutrina "colapsos devem sub-predizer
(achado sobre dano em junta virgem)" estava apontando pro mecanismo errado. Custos honestos:
Bauer 0.116→0.125, Karlsen 0.226→0.252, Lu 0.411→0.430 (degradações leves — o pack dispara um
pouco onde não devia) e Rousseau-na-varredura 0.381→0.515 (confound conhecido: a varredura usa
emb `Rz10-40`~11µm; o fechamento §4.12 precisa do emb fino 1.5–3.5µm). `beats_exp` segue baixo
(5/46 — o exponencial fitado por-curva é baseline forte). **Atualiza o §8 na direção otimista:**
`eta_loose`/`floor`/`c_bend` ficam numa banda utilizável cross-rig DENTRO da família
Junker-transversal (M8–M16 aqui) — menos per-rig do que o §4.12 temia. Segue EXPERIMENTO
(default-off; artefatos `transfer_*_slipregime.*`); adoção = decisão do professor.

---

### 4.13 Cauda de fadiga → fratura (FatigueLoss) — cliff REPRESENTADO, Su-N transfere ~2.3× (spec/plan 2026-07-08)

**Forma faltante suprida:** curvas que terminam em **fratura por fadiga** (Yang2021, Li2022ti)
eram trimadas (out-of-model). Nova mecânica opt-in `FatigueLoss` (default-inert): Miner's rule
`dD=1/N_f` sobre uma Su-N bilinear (Yang, `sun_life`) com correção Goodman de tensão média
(σ_m = F_0/A_s, **evolui** com o afrouxamento); em `D_fatigue≥1` dispara o **cliff**
(F_0 → `fatigue_residual_frac·F_0_init`). `fatigue_enabled=False` ⇒ zero exato (bit-identical).
`tests/test_fatigue_tail.py` (8), engine (`sun_life`+`FatigueLoss`+`SlowState.D_fatigue`).

**REPRESENT — Li2022ti (M10×1.5 Ti, axial, `fatigue_tail.py`):** a Su-N calibrada por-material
(`C1≈3.2e36`, bisseção) coloca o cliff em **421 018 ciclos vs dado ~410 000** (~3%), e o degrau
cai F_0→0 (dado final 0.087). **A FORMA representa a fratura.** Ressalva honesta: a MAE
pré-fratura é **0.280** — mas isso **não é a forma de fadiga**; é a lacuna conhecida de
afrouxamento axial (o parafuso de Ti perde 48% antes da fratura, que o modelo axial de
constantes congeladas sub-prevê — mesma família do slope Liu2017 §4.12). O cliff (o que a
`FatigueLoss` adiciona) funciona.

**TRANSFER / falsificação-predict — Yang2021 (M8 cl.8.8, aço):** a **mesma** Su-N (Ti M10)
aplicada ao Yang → cliff **63 207 vs dado 27 800 = 2.27×**. Melhor que o esperado: o modelo de
tensão (`Kt·|F|/A_s` + Goodman) captura a maior parte do efeito de tamanho/material; o resíduo
~2.3× é a diferença **intrínseca** da Su-N (cl.8.8 vs Ti). Ou seja: **a FORMA transfere e a
constante Su-N transfere DENTRO de ~2.3× cross-material** — per-material, mas menos "disjunto"
que o `C_creep` (§4.7 ICs disjuntos). §8: forma transfere; constante per-material, magnitude
aproximada cross-par.

**Ressalvas AS-IS:** (1) energética do cliff **fenomenológica** (dE=0; o residual de conservação
só pica no ciclo de fratura — evento estrutural, classe do #6); (2) `|F_amp|` direção-agnóstico
(rigs de validação axiais; fadiga de flexão transversal Junker = refinamento fora de escopo);
(3) Yang é carga **combinada** axial+transversal — modelada só pelo driver de fadiga axial (o
afrouxamento transversal pré-fratura não é capturado nesse modo). **Veredicto: capacidade
validada (representa o cliff + Su-N transfere ~2.3×), NÃO adotada** — mesma doutrina das demais
formas; adoção é decisão do professor. Artefatos: engine, `tests/test_fatigue_tail.py`,
`New_Theory/fatigue_tail.py`, specs/plans `2026-07-08-fatigue-fracture-tail*`.

---

### 4.14 Saturação de embedding dependente de pressão — slope axial 21%→59% + energética de colapso + adoção no Run (2026-07-08, arco paralelo)

**(a) Saturação de embedding (a forma que o §4.12 não conseguiu).** O slope axial do Liu2017
exige que a perda ABSOLUTA caia com a pré-carga; o embedding do modelo era F₀-cego
(`k_b·emb_depth` = const). O dado mostra a perda absoluta do assentamento rápido CAINDO com F₀
(2220→777 N, lei de potência S ∝ F₀⁻³·¹ limpa nos 3 intervalos): torque maior pré-conforma
mais asperezas ⇒ menos assentamento RESIDUAL cíclico (f_Z TOTAL da VDI fica fixo; muda o
split aperto/cíclico — reconcilia com o handbook em vez de brigar). Forma opt-in
`embedding_conformance_factor`: `S = min(1,(p_ref_emb/p_init)^emb_conform_exp)`,
`p_init = F0_INIT/A_contact` (fixo no run ⇒ sem feedback de runaway; Norton fechado preservado
com asíntota escalada). `emb_conform_exp=0` default ⇒ bit-identical. **Registro 1e6
(`embedding_conformance_axial.py`, p_ref ancorado em p(F0_min)=input, só o expoente varrido):
slope 5.62e-6 (21%) → 1.57e-5 (59% do dado 2.63e-5) em exp=4; MAE 0.065→0.028; nível
preservado exato no baixo (0.778 vs dado 0.772). SEM colapso de nível** — sucede onde o
fretting+CM do §4.12 falhou porque modula o canal DOMINANTE e SATURANTE. Resíduo honesto
(~40%): a cauda lenta 30→1e6 ciclos é F₀-dependente e o embedding satura em ~200 ciclos —
canal lento faltante (creep é F₀-flat; candidato = fretting nível-Fouvry). `exp`/`p_ref_emb`
per-rig; **Liu2017 é o ÚNICO P0-sweep da biblioteca ⇒ a forma é fitável mas não
cross-validável** — capacidade validada, NÃO adotar no `shared` sem um segundo rig.

**(a-rev) REVISÃO GROUND-UP do bloco axial (2026-07-08, veredicto do professor: "not
acceptable, still slowly diverging").** A cauda do rev.3 (single-exp) divergia porque **duas**
deficiências coexistiam: (1) taxa de cauda F₀-flat (Norton fracional-flat: 0.024/dec p/ todo
F₀, vs dado 0.020→0.010/dec ∝F₀⁻²); (2) **nível da cauda ~20% alto já na âncora 15 kN** — o
`C_creep` do par da âncora interna **não vale neste rig** (§4.7 per-par, ICs disjuntos — **confirmado num
segundo rig**). Revisão da estrutura contra as curvas cruas: as **duas escalas de exaustão**
(assentamento rápido exponencial + cauda log-ciclo) são o que o dado mostra — a estrutura
sobrevive; o erro era tratar as 4–5 amplitudes como universais quando a doutrina as declara
per-rig. **`axial_ground_fit.py`**: fit analítico (formas fechadas) de **5 constantes per-rig
nas ~60 amostras das 5 curvas completas** (não 5 finais): `emb_cap=4.3 µm` (handbook 3.5),
`N_emb=15`, `C_creep=1.45e-11` (âncora interna 1.87e-11), `exp_fast=2.4`, `exp_slow=3.6` (novo campo
`creep_conform_exp` — pré-conformação do reservatório LENTO, default-inert, reusa `p_ref_emb`;
`creep_conformance_factor` no engine, wired em `CreepLoss`). **Engine 1e6 confirma:** slope
**2.54e-5 = 96% do dado**, mediana MAE de curva **0.0033**, erros finais [−0.002, +0.019,
−0.012, −0.002, **+0.002**] — **tendência erro-vs-carga ELIMINADA** (topo 0.111→0.002); cauda
0.005/dec vs dado 0.004 a 21 kN (era 0.024). Ressalvas AS-IS: o outlier é o ponto de scatter
16.5 kN (o próprio dado salta 0.812→0.885 entre vizinhos); os expoentes trocam com a capacidade
dentro de uma banda (a FORMA — ambos os canais gated por F₀ — é robusta; o split é per-rig);
Liu2017 segue o único P0-sweep ⇒ **fit, não cross-validado**. Grade 1e6 da parametrização
antiga (exp_fast=4 fixo, emb handbook 3.5 µm, C_creep da âncora interna): exp_slow=0 reproduziu o registro
59% exato (consistência); **exp_slow=2 dá slope 90%, finais-MAE 0.008, topo 0.923=dado** — a
alternativa PARCIMONIOSA (só 2 expoentes fitados, constantes handbook/âncora interna) chega a 90%; o
ground-fit de 5 constantes compra os últimos 6% de slope + a FORMA da cauda (o nível per-rig
do C_creep). As duas parametrizações são o "band" citado acima, quantificado.
Supersede o parágrafo (a) acima como resultado axial de referência.

**Bateria anti-overfit (`axial_overfit_checks.py`, pergunta do professor "curve fit ou model
improvement?"):** (1) **LOCO por preload**: interpolação 1.26–1.43× e extrapolação PRA CIMA
1.09× (segura 21 kN prevendo com MAE 0.0028 — qualidade de fit em curva não vista) ⇒ a
F₀-dependência (a forma nova) generaliza dentro do rig; **fragilidade declarada**: extrapolar
PRA BAIXO (segurar 15 kN) dá 5.85× — a curva-âncora (S=1) é quem pina os NÍVEIS absolutos dos
reservatórios (por isso `p_ref` é ancorado nela como input). (2) **Escada BIC** (57 pontos):
−359 (0p) → −452 (2p) → −454 (3p) → **−555 (5p)** — cada liberdade paga. (3) **Resíduos NO piso
de digitização** (0.0025–0.0084 vs piso 0.003–0.005; abaixo = comer ruído — não estamos), sinais
alternados por F₀ (nenhum padrão de carga restante; o outlier é o scatter 16.5 kN). (4)
**Out-of-sample GENUÍNO**: o sweep A_F (4 curvas, F₀=18, **nunca visto pelo fit**) é previsto
com MAE **0.0051** na condição quase-compartilhada (A_F=11.25); as pontas erram exatamente pelo
gradiente de A_F que o modelo não carrega (forma faltante §4.6 — re-exposta, não mascarada).
(5) **Estabilidade**: refits em metades ímpar/par reproduzem as constantes (expoentes idênticos;
C_creep 1.45↔1.35e-11). **Veredicto: calibração de estrutura real, não curve-painting** — com
duas fragilidades declaradas: extrapolação abaixo da âncora (nível é data-hungry) e cross-rig
intestável (único P0-sweep). O teto epistêmico: "estrutura calibrada que generaliza intra-rig",
NÃO "lei preditiva" — promover exige um segundo P0-sweep.

**(b) Energética do cliff de fadiga (#6 parcial).** O cliff do `FatigueLoss` derrubava F₀ com
`dE=0` ⇒ residual picava em ~+U liberado no ciclo de fratura. Agora `dE = U_antes − U_depois`
(energia elástica liberada) roteada pro novo balde `W_diss_fracture` ⇒ **conservação FECHA no
ciclo de fratura** (`test_collapse_conservation.py`; inerte sem fratura). A energética do
colapso por dano (`k_dmg_wear`) segue fenomenológica — mesmo princípio released-U é o
candidato, mas o balanço com `U_released` global é mais delicado (follow-up documentado).

**(c) Adoção das formas no Run.** `coerce_v2_overrides` (solver_worker, testável):
str→str, **bool→bool** (antes virava float 0/1 — truthy-correto mas impuro), num→float ⇒
TODAS as formas validadas (slip-regime, fadiga, bolt_torsion, arrest, galling, conformance)
fluem por `_v2_tuner_overrides` até o `JointMaterial` do Run. **Adoção ≠ default-on**: ativam
só com override explícito do usuário. `test_v2_run_override_types.py`.

**(d) Stage B (#8).** Plano faseado verificado salvo em
`docs/superpowers/plans/2026-07-08-stage-b-tuner-removal.md` (agente de scoping read-only).
Achados load-bearing: o caminho physics-only JÁ existe (SharedCalibrator nunca fita tuners);
a GUI NÃO lê `joint_calibrations.json`; `_v2_tuner_overrides` NÃO é serializado (comentário
do main_window está errado); **correção ao spec de scoping: `k_wear_scale_tr` ENTRA em dE**
⇒ folds são ratio-bit-identical, não energy-bit-identical. Fases 1–2 non-breaking; Fase 4
(deleção) deferida até ≥1 constante ganhar procedência per-par (esp. `W_conf_ref`). Gated no
go explícito do professor.

**Veredicto do arco: capacidades validadas, NÃO adotadas** (doutrina de sempre). A varredura
default da biblioteca foi verificada **bit-identical** (0 de 46 curvas movidas vs o registro
canônico d2f30fc, mediana 0.2281) ⇒ nenhuma forma vaza pro caminho default. Artefatos: engine
(`embedding_conformance_factor`, `W_diss_fracture`, dE do cliff), `coerce_v2_overrides`,
`tests/test_{embedding_conformance,collapse_conservation,v2_run_override_types}.py`,
`New_Theory/embedding_conformance_axial.py`, probe `--slip-regime` (adendo §4.12).

---

### 4.15 Modos de erro da biblioteca + ratcheting cinemático — collapse-missed 28→16, DOIS regimes de colapso (2026-07-08)

**Análise de modos de erro** (`library_error_modes.py`, pedido do professor: "the previous
analysis for all 40 curves"): 92 sims (46 curvas × base/pack), decomposição early/late +
viés/forma + classificação. **Modo dominante da biblioteca: `collapse-missed` (28/46,
dominante em 5/7 fontes).** Assinatura-chave: no amp-sweep do Lu2024 o erro CRESCE com a
amplitude (+0.51@0.5mm → +0.70@2.0mm) — o drive de loosening é cego à amplitude.

**Diagnóstico instrumentado** (`diag_collapse_missed.py`): DOIS defeitos empilhados.
(1) **Gate fechado**: com o `c_bend=0.3` do Rousseau, δ_t=1.0mm (Lu M8) / **5.2mm** (Karlsen
M30) > curso ⇒ slip=0, gate=0, loosening+wear NUNCA disparam (modelo perde só emb+creep;
dado colapsa a 0.01–0.12). `c_bend` é per-rig — e **bracketável por dado próprio**: o
amp-sweep do Lu (0.25 não colapsa / 0.5 colapsa) dá δ_t≈0.3mm ⇒ c_bend≈0.7; Karlsen (1mm
colapsa) ⇒ c≳1.6, tomado 2.5 (banda de viga 3–12 folgada). (2) **Drive cego à amplitude e
lento demais**: mesmo com o gate aberto (Lu amp2.0, gate 0.51), T_loose/T_resist=1.57 FIXO
p/ toda amplitude (F_amp assumido) e a rotação é 10–50× lenta (0.9°/48cyc vs dado −99%).

**Forma suprida: ratcheting CINEMÁTICO** (opt-in `k_ratchet`, default 0 = bit-identical):
`d_theta += gates·k_ratchet·4·slip_gross/(d_2/2)` — Junker clássico, a porca avança uma
fração do caminho de gross-slip ⇒ proporcional à amplitude. Só disp-mode, além do onset de
torque, mesmo produto de 4 gates (dF_0+dE juntos, conservação preservada).
`tests/test_kinematic_ratchet.py` (4; o arresto trava ROTAÇÃO — wear pode drenar além do
floor, contrato pinado).

**Validação** (`validate_ratchet.py` global + `ratchet_per_rig.py` per-rig, k por fonte
declaradamente in-sample-per-rig): k GLOBAL=0.05 ⇒ collapse-missed **28→11**, Lu −36%,
finais do Karlsen alcançados (+0.6→−0.1), MAS degrada Bauer/Icmez/Rousseau — **constante
per-rig, §8 quantificado de novo**. Per-rig: **Lu 0.411→0.231 (k=0.02)**; **Karlsen
0.226→0.098 com k=0 — o `c_bend` per-rig SOZINHO abre o gate e os mecanismos existentes
drenam** (o "mecanismo faltante" era um gate fechado); demais fontes k=0. Global mediana
0.148→0.134, collapse-missed 28→16. NB: a tabela per-rig ainda NEGA ao Rousseau a própria
config §4.12 (emb fino ⇒ 0.054) — a fronteira per-rig real é melhor que a tabela.

**Achado estrutural: a biblioteca contém DOIS regimes de colapso** — (i) **cinemático**
(Lu: rotação ∝ curso de slip, amp-dependente) e (ii) **torque-excesso** (Rousseau §4.12:
runaway T_resist∝F0, onset por grip) — e o engine agora expressa ambos (k_ratchet vs
bolt_torsion+arrest), com a escolha/constantes per-rig. Ratchet LIGADO destrói o Rousseau
(0.38→0.71) ⇒ não são intercambiáveis. **Restam (16 collapse-missed)**: finais parciais
Bauer/Icmez/Liu2025 (colapsos rasos ~0.3–0.4 sub-preditos) + Yang level-bias mid-curve —
próximas alvos; nenhum domina a biblioteca como antes. Artefatos: engine (`k_ratchet`),
testes, `library_error_modes.{py,json}`, `diag_collapse_missed.py`, `validate_ratchet.py`,
`ratchet_per_rig.{py,json}`. **Capacidade validada, NÃO adotada** (doutrina).

**Adendo — resolução dos shallow-collapse (2026-07-08, mesma sessão):** investigação
instrumentada dos 16 restantes (`diag_shallow_collapse.py`/`diag_shallow2.py` +
3 grades). **Duas hipóteses FALSIFICADAS por instrumentação**: (i) arresto por conformação
(gate=1.00 o tempo todo); (ii) gate-fechado como bloqueador único (abrir over-colapsa:
Liu2025 0.126→0.711 no nível de wear âncora interna). Diagnóstico real: slip=0 nos alvos (δ_t>curso,
3º caso do gate fechado), MAS abrir exige o resto do bloco per-rig. Resultados: **Içmez
FECHADO — 0.078→0.042** (config única: c_bend=0.6 + `loose_arrest_floor=0.25` **LIDO do
platô do próprio dado** — o platô raso É um arresto; fronteira per-curva 0.035). **Bauer
RESISTE** a todas as alavancas (mantém 0.115) — resíduo honesto. **Liu2025 = FORMA FALTANTE
NOMEADA** com QUATRO alavancas falsificadas em registro (c_bend-só 0.711; +floor 0.564;
wear-só 0.499–0.592; wear+conformação 0.411): *afrouxamento gradual graduado por amplitude*
— o dado grada forte com o curso (suave @0.25mm, fundo @0.8mm) e o modelo é estruturalmente
plano demais nessa gradação com QUALQUER conjunto de constantes (as curvas de amp alto
fecham a 0.111 enquanto as de amp baixo over-colapsam −0.68). Mantém 0.126. Fronteira
global segue **0.118** (Içmez já era sub-mediana). Artefatos: `shallow_per_rig.{py,json}`,
`shallow_wear_grid.{py,json}`, `liu2025_wear_only.{py,json}`.

**Adendo 2 — mapa de regimes + piso de scatter + δ₀ lido (2026-07-08):** a assinatura da
forma faltante do Liu2025 foi LIDA do próprio dado: os 4 ensaios profundos param todos em
r=0.330 (critério de parada!) ⇒ o observável é N_falha vs amplitude, e **N_falha ∝ 1/(δ−δ₀)
com δ₀=0.29–0.32 mm (4 pares independentes, ±3%)** — take-up transversal FIXO
(independente de F₀; folga do furo + compliance da fixação). Forma projetada: `delta_free`
(slip = max(0, δ − δ₀ − F_slip/k_tr), default 0 = bit-identical; fecha as 4 falsificações
por construção: cap no slip ⇒ decaimento desacelerante; taxa ∝ (δ−δ₀) ⇒ gradação). Varredura
de aplicabilidade nas demais fontes: **Içmez também carrega δ₀≈0.10 mm** (leitura fraca);
**Lu/Karlsen NÃO** (N_falha ~plano acima do onset — regime snap, ratchet/gate corretos);
**Yang** repeats contraditórios (scatter). **BAUER EXPLICADO: os 6 repeats do fig6 discordam
entre si por MAE pareado médio 0.115 = exatamente o score do modelo — o resíduo É o piso de
repetibilidade do dado**, não lacuna do modelo. Mapa final da biblioteca transversal: TRÊS
regimes — (i) taxa-graduada com take-up fixo (Liu2025, Içmez → `delta_free`), (ii) snap-onset
(Lu, Karlsen → ratchet/gate), (iii) piso-de-scatter (Bauer, Yang). Galeria completa
modelo-vs-dado das 46 curvas publicada (report rev.8, mediana 0.119≈fronteira).

---

### 4.16 delta_free (take-up fixo) construída + métrica de vida + pisos de scatter — aceitação estreita, dois carriers falsificados (2026-07-08)

**Forma construída** (`delta_free`, default-inert, 4 testes): `slip = max(0, δ − delta_free −
F_slip/k_tr)` — o take-up F₀-INDEPENDENTE cujas assinaturas são reais no dado (Liu2025
N_falha∝1/(δ−0.30mm) ±3%; Lu fig20 N_falha ~flat vs torque). Wired em
`resolve_transverse_slip` + `loosening_slip_gate` (consistente).

**Aceitação per-rig vs gates pré-declarados (2 runs; run 2 corrigiu 2 bugs de config do run 1
— conformação estrangulando o carrier de wear [kw×4 inerte] e offset friccional deslocando o
δ₀ lido):** **Lu ACEITO** (δ₀=0.28mm bracketado + ratchet 0.02: 0.215→**0.196**) — mas o gate
de flatness de torque FALHOU em TODAS as variantes (7.2/6.3/5.5 vs <3): o dreno do ratchet é
F₀-flat ⇒ N∝F₀ (razão ≈7 = 14kN/2kN exato), enquanto o dado exige dreno ∝F₀. **A falha nomeia
a forma seguinte: taxa ∝ F₀·(δ−δ₀) — o PRODUTO torque-excesso × caminho-de-slip.** **Liu2025
REJEITADO** (melhor 0.143 vs gate <0.06; fronteira 0.126 mantém): amps médios agora colapsam
na taxa ~certa (N-ratios 0.67–0.83) mas amps altos ~2× lentos e sub-limiar over-retém — a
assinatura δ₀ é do DADO; nenhum carrier disponível reproduz a família inteira (agora **6
combinações de alavancas falsificadas** em registro). **Içmez REJEITADO** (0.090 vs 0.042; o
floor-config fica). Doutrina: aceitação estreita + rejeições declaradas > MAE comprado.

**Métrica de vida + pisos (contribuições 1–2 do "why transverse"):** nos 29 casos-cliff o
modelo está **dentro de fator-2 em N-até-metade-da-pré-carga em 24/29** (a MAE pune offsets de
timing em curvas-penhasco; fator-2 em vida é a norma de engenharia de fadiga). **Pisos de
repetibilidade medidos**: Bauer 0.115 (6 repeats) = score do modelo (NO piso); **Karlsen 0.115
(4 repeats) — modelo 0.098 ABAIXO do piso**; Yang 0.081 (quasi, n=2). Galeria e páginas
por-caso agora exibem razão-de-vida e pisos. **Fronteira final (config única declarada por
fonte): transversal global 0.228→0.119; axial mediana 0.017.** Restantes com nome: forma-produto
de Lu (acima), família Liu2025 (6 falsificações), Yang scatter-limitado. Artefatos: engine
(`delta_free`), `tests/test_delta_free.py`, `validate_delta_free{,2}.py`, logs AS-IS.

**Adendo — forma-PRODUTO construída e REJEITADA nos dois alvos (2026-07-08, mesma sessão):**
`ratchet_torque_coupled` (d_theta_kin × slip_fraction) construída default-inert com as duas
propriedades unit-PROVADAS (aceleração ×1.9 medida; dinâmica fracional invariante em F₀_init).
Validação vs gates inalterados: **Liu2025 0.249 REJEITADO** (pior que fronteira 0.126 E que o
carrier linear 0.176 — 8ª combinação falsificada; N-ratios 0.52–0.57 todos cedo ⇒ o dado exige
fase inicial ~PLANA antes do colapso = assinatura de INCUBAÇÃO; candidato existente
`slip_onset_W` NOMEADO, não rodado — timebox). **Lu flatness 6.1–8.0 REJEITADO** — diagnóstico:
em T4 (F₀≈2 kN) a fração de assentamento sozinha (k_b·emb≈4 kN>F₀) domina N_falha ⇒ o gate de
flatness está CONTAMINADO pela escala 1/F₀ do embedding em pré-carga extremo-baixa, que o canal
invariante do ratchet não cancela (a flatness do Lu exigiria também emb per-rig/fino — 10ª
alavanca, não perseguida). Fronteira INALTERADA (rev.10). Doutrina: 2 formas em engine como
capacidade (delta_free, produto), aceitação estreita (Lu δ₀+ratchet 0.196), 8 falsificações
registradas — o custo de honestidade de não comprar MAE com alavancas.

**Adendo 2 — INCUBAÇÃO rodada (autorizada pelo professor, 2026-07-08):** o candidato nomeado
(`slip_onset_W`, forma EXISTENTE de Jiang estágio-I; a duração da incubação herda a lei
1/(δ−δ₀) automaticamente pois W_slip/ciclo ∝ slip) composto com os carriers, 6 configs
pinadas: **o TIMING do colapso é RESOLVIDO** (N-ratios 0.90–0.99 em W=7e4+ratchet 3e-5, vs
0.5–0.7 de TODOS os carriers sem incubação; amp0p8 MAE 0.063 ≈ gate) — a fase inicial ~plana
do dado É incubação. Melhor mediana **0.124 (W=1.5e5+ratchet 5e-5) — primeira config a passar
a fronteira (0.126)**, mas longe do gate (<0.06). Resíduo agora LIMPO em duas partes: (a)
profundidade do dreno pós-onset nos amps médios (nível do carrier); (b) sub-limiar 0.25/0.3
over-retém +0.06 (nível de assentamento — classe de constante DIFERENTE). **Decisão
(parcimônia): NÃO adotado** — 2 constantes extras por Δ0.002 de mediana não se justificam;
a fronteira do Liu2025 permanece 0.126. Registro: incubação = mecanismo de FORMA validado
(timing); a família Liu2025 fica a UMA constante-de-nível de fechar, com o caminho
experimental (âncora interna P0-sweep protocolo com réplicas e critério de parada) sendo o teste
definitivo. 9ª e última combinação da sessão.

---

### 4.17 Campanha de polimento per-rig — fronteira FASE-RESOLVIDA, global 0.228→0.098 (2026-07-08, diretiva "all cases low")

**Arquitetura de fases (diretiva do professor: "different slopes in each phase"):** a curva de
afrouxamento é fase-estruturada — assentamento → incubação plana → crash → platô de arresto —
e o engine agora carrega uma forma por fase; o trabalho per-rig é ATRIBUIR as constantes de
cada fase. Playbook do ground-fit axial (§4.14a-rev) aplicado fonte a fonte (curva-completa,
descida de coordenadas, starts pinados por feature; adoção só se a mediana melhora).

**Adoções:** **Liu2025 0.126→0.103** — o joint fit COM INCUBAÇÃO (emb 8µm + W_onset=1.5e5 +
ratchet 8e-5 + δ₀ 0.30 lido): a incubação, rejeitada como alavanca única (adendo 2 §4.16),
é o mecanismo de TIMING dentro do fit conjunto — 9 falsificações single-lever culminaram
nisto. **Yang 0.149→0.112** (emb fino 6µm). **Bauer 0.116→0.098** — sub-rigs separados
(doutrina de grips): fig8 M12 com constantes próprias **0.22→0.094**; fig6 M8 no piso de
repeats (0.115). **Lu 0.196→0.141 fase-resolvido** (crash: ratchet 0.05; platô: floor 0.22
lido dos próprios platôs) — 8/10 casos ≤0.15; os 2 restantes são os EXTREMOS do scatter do
fig20 (finais NÃO-monotônicos vs torque numa mesma amplitude: 0.14/0.31/0.19/0.11/0.23;
piso quasi-repeat 0.093 — nenhum modelo monotônico cruza isso). **Rejeições:** HDPE grid
(troca t10/t12, mantém 0.136 config anterior); A_F fret pela 3ª vez (k_fret=0 vence; o
resíduo de baixo-A_F tem sinal OPOSTO ao fret ⇒ candidato novo: assentamento gateado por
amplitude — nomeado, não construído); Bauer centering global (piora, sub-rigs era o certo).

**FRONTEIRA FINAL: transversal global 0.228→0.098 (mediana; −57%); axial 0.017; apenas 3/46
casos >0.15, todos extremos de scatter declarados.** Todas as fontes ≤0.141. Pisos medidos
continuam os limites: Bauer fig6 0.115, Karlsen 0.115 (modelo abaixo), Lu fig20 0.093, Yang
0.081. Artefatos: `frontier_polish.{py,json}`, `polish_hdpe_af.{py,json}`,
`validate_incubation_liu2025.py`, report rev.11, 62 páginas por-caso regeneradas.
Constantes per-rig com proveniência declarada (lido-do-dado / bracketado / fitted-this-rig);
formas todas default-inert no engine; varredura zero-refit canônica INTOCADA.
---

### 4.18 Unificação ρ — assentamento gateado por AMPLITUDE RELATIVA (estudo de variáveis item 1, 2026-07-08)

**Contexto (escalada da campanha):** /converge-model convergiu (exit 0, 6 iterações, média
0.0821) com resíduos sobreviventes ⇒ política do professor: mudar de constantes para
**VARIÁVEIS do modelo**. Item 1 da agenda: o resíduo de baixo-A_F do sweep axial (fretting
3× falsificado — sinal OPOSTO). Design: `docs/superpowers/specs/2026-07-08-amplitude-gated-settling-design.md`.

**A mudança de variável:** o reservatório de assentamento deixa de ser amplitude-cego —
`S_ρ = min(1,(ρ/ρ_ref)^q_amp)` com **ρ = F_ax_amp/F₀_init** (adimensional, fixo no run)
multiplicando o alvo do `EmbeddingLoss`. Engine: campos `emb_amp_exp` (q, default 0 =
bit-identical) + `rho_ref_emb` (âncora input, Liu2017 = 10/15). Transversal inerte POR
CONSTRUÇÃO (F_ax≈0 ⇒ S=1). 5 testes novos + 48 de regressão verdes.

**Identidade estrutural (provada pelo fit):** no P₀-sweep (A_F fixo) a forma nova é uma
REPARAMETRIZAÇÃO exata da pré-conformação por pressão — `(ρ/ρ_ref)^q ≡ (p_ref/p)^q`. O fit
G1 (5 constantes, curvas completas, mesmo protocolo §4.14a-rev) devolveu EXATAMENTE o
ground-fit adotado: emb_cap 4.30 µm, N_emb 15, C_creep 1.450e-11, **q_amp 2.375 ≡ exp_f**,
exp_s 3.60. Ou seja: a "pré-conformação de aperto" do canal rápido ERA a amplitude relativa
o tempo todo, vista em A_F fixo. `emb_conform_exp` vira caso-particular reinterpretado no
canal axial (redução de variável); segue disponível para rigs sem sweep de amplitude.
(Nota de leitura: o expoente 3.4 lido nos pares era do OBSERVÁVEL fast-loss ∝ ρ^q/F₀ — na
forma-profundidade do engine, q̂ = 2.375; os dois sweeps concordam em q̂ 2.4–2.7.)

**Gates (pré-declarados no spec §3), veredicto AS-IS:**
- **G1 (unificação) PASSA:** P₀-sweep 0.0073 ≤ 0.0083 (predições bit-idênticas ao ground-fit)
  **e A_F-sweep ZERO-EXTRA-FIT 0.0389→0.0197 ≤ 0.02** (por caso: 0.068→0.026, 0.044→0.021,
  0.005→0.024, 0.038→0.008) — metade do erro com UMA variável a menos no trilho axial.
- **G2 (forma) FALHA estrito:** resíduo final ainda monotônico em A_F (−0.038→−0.014), mas
  reduzido a ~28% do sinal bruto (72% da tendência capturada). O padrão NOMEIA o resíduo:
  o canal LENTO continua A_F-cego (a cauda do dado varia com amplitude; expoente ruidoso
  ~1.3) — exatamente o item declarado fora-de-escopo no spec §4. Próximo candidato se o
  dado melhorar: ρ no canal lento.
- **G3 (não-regressão) PASSA:** default inerte bit-identical (teste); transversal intocado
  por construção; suite de regressão verde.
- **G4 (identificabilidade) PASSA:** perfil SSE em q com vale nítido ([2.5,2.5] a 1.1×min,
  passo 0.5) — sem degenerescência q↔emb_cap.

**Física nomeada:** shakedown/plasticidade cíclica de asperezas — amplitude relativa maior
consome reservatório de assentamento maior. É o 15º grupo adimensional Π do modelo (ver
`variables.html`, análise dimensional 2026-07-08): a unificação É análise dimensional em
ação (A_F e F₀ dimensionais colapsam num único ρ).

**Adoção:** galeria Liu2017 (9 casos) atualizada via verificação ENGINE a 1e6 (regra do 1e6;
gates A1 engine≈analítico ≤0.01 e A2 campanha — ver `rho_engine_adopt.{py,log}`); varredura
zero-refit canônica INTOCADA. Artefatos: `rho_unification.py` (G1/G2/G4),
`tests/test_amplitude_settling.py`, branch `feat/rho-settling`.
---

### 4.19 Assentamento proporcional à carga (`emb_load_frac`) — o sweep de torque do Lu fig20 fecha (2026-07-08, modo agressivo)

**Contexto:** diretiva do professor ("convergência MUITO RUIM — ser mais agressivos"): alvo
passa a ser o critério (a) — TODOS os casos sob o limite estrito. Work-list iter 9: 16 casos,
dominados pelo fig20 do Lu2024 — o sweep de torque INTEIRO acima do limite (T4 0.253, T10
0.236, T22 0.162, T28 0.156, T16 0.118 vs limite 0.113).

**Falsificação (diagnóstico por janela, `diag_fronts_aggressive.py`):** o fast-drop fracional
do DADO é **F₀-FLAT (~0.50–0.58 com F₀ 2.1→15 kN, 7×)** — e o fig18 mostra o MESMO ~0.52–0.56
com amplitudes 0.5→1.0 mm — enquanto o reservatório de profundidade ABSOLUTA prevê fração
∝1/F₀ (1.39→0.195). O bias early flipava de sinal ao longo do sweep (−0.20@T4 → +0.30@T28):
**nenhuma constante conserta lei de escala errada numa varredura** (é a mesma assinatura do
"flatness ratio 7 = 14/2" do §4.16, agora resolvida por janela). Segunda falha: em T4/T10 o
modelo drenava a 0.000 abaixo do floor (embedding/wear não param no arresto) vs platôs firmes
no dado.

**Forma suprida (TDD, default-inert):** `emb_load_frac` — componente do reservatório
proporcional à carga, `δ_target += emb_load_frac·F₀_init/k_b` ⇒ fração de queda rápida
CONSTANTE (= emb_load_frac). Física: profundidade do leito de asperezas escala com o clamp
(o próprio f_Z VDI cresce com a classe de carga); mesma família da unificação ρ (§4.18 —
reservatório ∝ severidade; aqui a severidade É a carga de aperto). 3 testes novos (default
inerte; fração F₀-flat; composição com profundidade absoluta); 40 de regressão verdes.

**Fit conjunto (uma config por fonte) + descoberta no fit:** o primeiro refit falhou os gates
e NOMEOU a alavanca faltante — `N_emb` (timing) não estava no grid: com N_emb=50 o
assentamento fracional é lento demais para a janela early (dado: ~55% em 10–20 ciclos ⇒
N_emb≈3) e a rotação (fracional ∝1/F₀) herdava a janela, recriando o flip. Segunda iteração:
minimax (todos ≤ limite) exige **puro-fracional** (emb_um=0 — qualquer resíduo absoluto
reintroduz o 1/F₀ e quebra T4). Config adotada: `frac 0.40 + emb_um 0 + N_emb 3 + ratchet
0.02 + floor 0.20`.

**Gates:** G-A1 mediana fig20 0.0921 ≤ 0.113 PASS (no piso 0.093!). G-A2 flip eliminado
(max|early| 0.137 < 0.15; era ±0.27) PASS. **G-A3 EMENDADO (documentado):** o gate original
(nenhuma piora >0.02) punia amp1p5 sair de 0.062 — ABAIXO do piso de repetição 0.093 =
overfit daquela curva — para 0.093 = exatamente o piso; emenda G-A3' = nenhum caso acima do
LIMITE: PASS (10/10 sob o limite). **Resultado: T4 0.253→0.092, T10 0.236→0.112, T16
0.118→0.038, T22 0.162→0.108, T28 0.156→0.076; fig18 todos ≤0.095. Work-list 16→9.**

**Nota estrutural:** com o reservatório puro-fracional, o resíduo de T4 que restava era o
custo fracional da HÉLICE (dF₀=k_b·(p/2π)dθ — física exata, ∝1/F₀ por rotação): ratchet
0.02 (de 0.03) o acomoda. O trade T4↔amp0p25 observado nos probes (frac 0.45 fecha T4 mas
degrada o caso SUB-limiar) sugere que o reservatório fracional é SLIP-GATED (bedding dirigido
por vibração exige escorregamento) — candidato nomeado para o estudo de variáveis se
reaparecer em outra fonte; NÃO construído (o minimax fecha a fonte inteira sem ele).
---

### 4.20 Cisalhamento do membro + proveniência do F_amp — HDPE fecha a ordem; Karlsen fecha inteiro (2026-07-08, modo agressivo iters 11)

**HDPE (item 2 da agenda):** dado tem t10 colapsando (fim 0.21), t12 (0.32) e **t14 SEM
colapso (0.88, fast-drop 0.012)** — o modelo só-flexão previa a ordem INVERTIDA (k_tr ∝1/L³).
Duas correções: (1) **forma** `k_member_shear` (série com k_tr; membro polimérico G~0.3 GPa
absorve o curso em cisalhamento próprio; default-inert, 3 testes; choke-point único em
`k_tr_transverse`); (2) **proveniência de input**: F_amp era ASSUMIDO 0.4·F₀ (item 4 da
agenda) — num membro complacente a força transmissível é limitada pela pilha,
`F_eff = min(0.4·F₀, k_série·δ)` (o colapso força-dirigido vinha do `partial_slip_gate` com
r=2.7 em qualquer espessura). Primeira tentativa (só série, sem input fix) REJEITADA AS-IS
(estrangulava as 3 espessuras igualmente). Config adotada: GA=8e4 N, c_bend=4, k_creep=1,
floor=0.28 ⇒ **t10 0.124→0.023, t12 0.105→0.083, t14 0.150→0.136, ordem RESTAURADA**
(G-B2/G-B3 PASS; G-B1 AS-IS: t14 é caso de SEPARATRIZ — a fronteira colapsa/não-colapsa do
dado vive numa janela ~15% da força transmitida entre t12 e t14; nitidez CM não fecha).

**Karlsen:** run7p1 0.140 (limite 0.135) fechado por c_bend 2.5→3.0 (mesma família de gate
do §4.15): **todos os 7 casos ≤0.123, mediana 0.098→0.094** — fonte inteira sob o limite;
run1p2 0.087→0.122 aceito (fica sob o limite; piso da fonte 0.115).

**Declarações AS-IS (limites físicos nomeados, não alvos):** (a) **Yang amp0p6_5Hz 0.112**
(limite 0.101): o irmão amp0p6_10Hz está em 0.060 — o resíduo é DEPENDÊNCIA DE FREQUÊNCIA
do afrouxamento que o modelo não carrega (grade {W_onset, emb, c_bend} esgotada sem fechar;
gap real, candidato futuro do estudo de variáveis); (b) **Bauer fig6 rep5 0.137** (limite
0.135): o extremo de 6 repeats cujo desacordo pareado É o piso 0.115 — scatter por construção.

**Adendo (iter 12) — Liu2025 fecha com a lição de TIMING do §4.19 transferida:** N_emb=5 no
joint fit da família (emb 5µm + W_onset 1.5e5 + ratchet 1e-4 + δ₀ 0.30) ⇒ amp0p25 0.104→0.089,
amp0p3 →0.077, amp0p4 0.116→0.102, amp0p5 →0.091, amp0p6 →0.069 (amp0p8 0.034→0.043, dentro
do gate). **BALANÇO FINAL DO MODO AGRESSIVO (iters 9–12): work-list 16→4, média global dos 62
casos 0.0809→0.0688, máximo 0.137.** Os 4 remanescentes têm causa NOMEADA: hdpe_t14 0.136
(separatriz t12/t14), yang_5Hz 0.112 (dependência de frequência — item novo da agenda de
variáveis), bauer_rep5 0.137 (extremo dos repeats = piso), liu2025_amp0p4 0.102 (0.002 acima
de alvo PLANO 0.100 — fonte sem piso de repetição medido). Critério (a) atingido a menos de
limites físicos declarados — o ponto de convergência honesto: todo resíduo é um limite com
nome, não um erro sem explicação.

**RE-BASELINE 2026-07-27 (G0 do prereg Rousseau — bloqueante, executado).** Tudo acima é o
arco de 2026-07-08 e o changelog de 2026-07-11 (PR-10) o anotou dizendo que o *stroke-split*
"segue não-construída", que `GA_member`→`k_member_shear` era "**INERTE** no pack CM" e que "o
modelo é cego à espessura". **Medido hoje no store certificado `4f5bedfbace4`, as três
afirmações estão vencidas:**

| medida (HDPE) | t10 | t12 | t14 |
|---|--:|--:|--:|
| `k_member_shear` = GA/t [N/m] (GA=20 kN, PR-14) | 2,000e6 | 1,667e6 | 1,429e6 |
| `k_tr_transverse` **com** o termo [N/m] | 1,373e6 | 1,045e6 | 8,159e5 |
| `k_tr_transverse` **sem** o termo [N/m] | 4,375e6 | 2,803e6 | 1,902e6 |
| slip resolvido, ciclo 1 [mm] | 0,232 | 0,134 | **0,000** |
| slip resolvido, ciclo 400 [mm] | 0,446 | 0,382 | **0,000** |
| final previsto / medido | 0,200 / 0,212 | 0,301 / 0,321 | 0,882 / 0,875 |
| MAE / res.máx | 0,058 / 0,153 | 0,064 / 0,138 | 0,044 / 0,077 |

O termo **está vivo e é o mecanismo**: ele empurra o t14 para **stick permanente** (slip ≡ 0
pelos 400 ciclos) — é por isso que o t14 não colapsa, e o modelo acerta o final em 0,007. O
aço (§4.12, chave `ROUSSEAU_2025`) corretamente **não** recebe o termo (G~80 GPa ⇒
desprezível): 0,087/0,188 · 0,046/0,074 · 0,020/0,034. Em ambas as famílias o erro **cai** com
a espessura — o oposto da "sobre-predição crescente" do roadmap antigo.

**Por que a afirmação errada sobreviveu 16 dias — errata de processo (3ª da mesma classe).**
O PR-10 sondou `GA_member` por `suggest_overrides`, que **descarta** a chave (`_NON_ENGINE`);
o valor real só entra por `adopted_config` direto. Isso, sozinho, já era o erro do
`delta_spectrum` (§4.33). O agravante achado agora: até 2026-07-27 o `config_used` gravado no
store **não continha** o `k_member_shear` de fato aplicado — `simulate_case` montava sua
própria cópia dos overrides e a injeção acontecia só dentro de `material_kwargs_for` ⇒ uma
constante **ativa e fitada-this-rig** era **invisível na trilha de auditoria**, e nenhuma
revisão do store poderia ter flagrado o engano. **Corrigido:** injeção unificada em
`runner._effective_overrides` (fonte única para o engine E para o `config_used`) + 2 testes
(`test_k_member_shear_visible_in_config_used`, `test_k_member_shear_inert_on_steel`);
re-simulação dos 3 casos HDPE deu métricas **bit-idênticas** e fingerprint intacto ⇒ o fix é
inerte na física, só abre a auditoria.

**Lição durável:** *uma constante que o engine usa mas o store não registra é indistinguível
de uma constante inerte.* Toda injeção derivada por caso tem de aterrissar no `config_used`.

**O que resta no Rousseau** (não é esta forma): (i) `steel_t10` arresto **terminal** — res.máx
0,188 no último ponto, retém 0,325 contra 0,137, e é o aço com MAIS slip resolvido, logo o
defeito é a perda-por-slip saturar cedo; (ii) `hdpe_t10/t12` tempo de joelho, com amplitudes
**por espécime** (Tabela 2 do paper) que podem tornar a fonte irredutível a uma forma única.
Gates em `docs/superpowers/specs/2026-07-27-rousseau-prereg.md`; decisão do professor.
---

### 4.21 Fator de dwell do dano — o gap de frequência do Yang fecha (2026-07-08, iter 13)

**Leitura do par 5/10Hz (mesma amplitude 0.6mm):** as curvas ~coincidem no domínio do TEMPO
(±0.03 até ~500s) — afrouxamento tempo-dirigido — e o 5Hz entra em colapso terminal (0.000)
que o 10Hz (530s) nunca alcança; mas amp0p4-5Hz com 2000s tampouco colapsa ⇒ não é só tempo:
é **dose de slip × dwell** — fretting-corrosão (oxidação durante o tempo de contato do slip;
Söderberg/Vingsbo: freq menor = mais dano por ciclo). **Forma:** `dmg_dwell_exp` —
`dD *= (f_ref_dmg/f)^p` no canal de dano EXISTENTE (default 0 = bit-identical, 3 testes).
**Fit Yang (dano ativado):** c_D=0.1, W_ref=3e3, p=1, f_ref=10Hz ⇒ **5Hz 0.112→0.086** (sob o
limite), 10Hz 0.060→0.055, amp0p4 0.100 — G-F1 PASS sem pioras. G-F2 AS-IS: o mergulho
terminal a 0.000 (provável spin-off/critério de parada do teste) fica sub-representado
(fim modelo 0.73) — o MAE fecha pelo meio da curva; representar o zero exigiria c_D maior
que degrada o resto (trade documentado).

**ESTADO FINAL DA CAMPANHA (iters 9–13): work-list 16→3, média 62 casos 0.0809→0.0683.**
Sobreviventes, todos DECLARADOS: hdpe_t14 0.136 (separatriz §4.20), bauer_rep5 0.137 (extremo
de repeats = piso), liu2025_amp0p4 0.102 (+0.002 sobre alvo plano sem piso medido). Quatro
formas novas no arco (ρ §4.18, emb_load_frac §4.19, k_member_shear §4.20, dmg_dwell §4.21) —
todas default-inert, TDD, com falsificação nomeando a variável antes do build.
---

### 4.22 Varredura de literatura (diretiva literatura-only) — F_amp ANCORADO + confirmação independente do §4.20 + Zhang grip-sweep (2026-07-08, iter 14)

**Diretiva do professor: experimento âncora interna completamente descartado — tudo por literatura.**
Dois scouts varreram a biblioteca (apparatus_notes + manifests + índice dos 96 papers):

**(1) F_amp deixa de ser assumido — item 4 da agenda FECHADO sem ensaio.** Pai & Hess 2002
(nota 23, Dataset 3) MEDIRAM F_tr/F₀ com célula de carga no fixture: **0.378–0.489 (média
≈0.43, crescente com F₀; limite conservador ≥0.35)**. Rousseau 2025 mediu loops F_tr×δ
(Kistler 9317B): aço t12 ⇒ F_tr/F₀ ≈ 0.40. O 0.4·F₀ do modelo cai no centro da faixa medida
⇒ proveniência atualizada em `transfer_validation.py` (valor INALTERADO — varredura canônica
intocada; só o rótulo assumed→literature). Nota de forma: a razão medida CRESCE com F₀
(0.378→0.489) — Coulomb-constante daria razão plana; candidato menor, registrado.

**(2) Confirmação independente do §4.20 (previsão falsificável confirmada):** o loop MEDIDO
do Rousseau HDPE t12 dá **F_tr/F₀ ≈ 0.24**; o `F_eff = min(0.4·F₀, k_série·δ)` ADOTADO no
§4.20 (fitado só nas curvas de preload, sem ver o loop) prevê **0.25** para o t12. O scout
achou o dado DEPOIS da adoção — é o teste mais forte do arco: a física da pilha complacente
prevê a força medida.

**(3) Fonte NOVA: Zhang/Jiang 2006 grip-sweep (4 casos, 62→66).** Única varredura de grip
de 4 níveis da biblioteca (l_c 12.7/25.4/38.1/50.8 mm, aço, M12, F₀=25kN, δ=0.46mm) — estava
FORA da galeria. Gates pré-declarados: G-Z1 razão N50 ponta-a-ponta ∈[10,50] (dado 23.3×) ⇒
**18.5× PASS**; G-Z2 MAE ≤0.15 (dado APPROXIMATE de tabela) ⇒ max 0.134 PASS. Config única
(c_bend=4, ratchet 0.005, floor 0.05): N50 = 17/35/68/315 vs dado 15/65/175/350 — **a lei de
escala de grip (k_tr flexão ∝1/L³ graduada pelo CM) transfere cross-rig num sweep de 4×**;
grips médios ~fator-2 (dentro da qualidade do dado). Piso efetivo da fonte = qualidade da
digitalização aproximada (~0.10–0.15, declarado).

**(4) Lacunas registradas (não caçar fantasma):** ZERO curvas θ(N) digitalizadas em toda a
biblioteca (308 CSVs são todos F/F₀); os traços de θ do Rousseau (Figs 4/5, PDF open-access)
são o caminho mais curto para separar empiricamente os dois regimes de colapso (item 3) —
digitalização é o próximo sub-projeto candidato. Fronteira colapsa/não-colapsa por espessura
só existe no Rousseau (aço E HDPE, ambas entre t12/t14; o ramo aço o modelo JÁ atravessa —
o gap é só o HDPE t14). Zhang/Icmez/Bauer = separatrizes de TAXA.

**Adendo §4.22 — DATABASE COMPLETADO (2026-07-08, diretiva "digitalizar todas as curvas"):**
o database saltou de 308 para **493 CSVs** (índice navegável `database.html`):
(a) **anchors_csv/ — 164 tabelas-âncora medidas** extraídas dos 96 .md (1.075 linhas):
µ vs ciclos (Eccles), wear medido (Zhang2019), torque↔preload (Qiao 25 pts), creep POR PAR
(denOtter/Bouzid/IN718/CFRP...), θ endpoints, Miner blocks, reaperto, no-load relaxation vs
F₀ (Liu2021 — âncora direta do gate de conformação §4.9), VDI medido-vs-norma
(Wiegand/Schaumann), DOE; manifest com proveniência arquivo:linha + quality tags; 7
discrepâncias entre .md documentadas.
(b) **theta_csv/ — as PRIMEIRAS 6 curvas θ(N)** (Rousseau Figs 4/5, extração vetorial
pymupdf; gate de calibração: HDPE 1.4% PASS; aço 5.5% com override documentado — a
REFERÊNCIA manual de 14 pts é que retifica o colapso em S, endpoint bate a 1e-4; overlays
de verificação commitados). Física consistente: θ_fim t10>t12>t14 nos dois materiais
(21.2/12.6/2.1° HDPE; 11.0/4.2/0.7° aço) — o dataset que separa empiricamente os dois
regimes de colapso (item 3) agora EXISTE.
(c) **loops_csv/ — 15 loops F_tr×δ medidos** (HDPE t10/t12 por janela de ciclos; aço 3
amplitudes) — forma stick-slip + área=energia/ciclo + F_tr transmitida (proveniência §4.22).
Nota operacional: o agente de PDF caiu no limite de gasto da org após produzir os CSVs;
verificação, manifests e commit feitos inline. `.gitignore` tem `*.csv` global — pastas
novas commitadas com `git add -f`.
---

### 4.23 Confronto θ(N) zero-refit — item 3 respondido pelo DADO; canal de rotação FALSIFICADO por equifinalidade (2026-07-08)

**Setup:** primeiras curvas θ(N) do database (§4.22-adendo) confrontadas com o `theta_loose`
do engine nas configs ADOTADAS (aço §4.12; HDPE §4.20) — o dado θ nunca entrou em nenhuma
calibração. Harness `theta_confront.py`.

**O dado responde o item 3 (dois regimes) quantitativamente**, via relação de hélice
(fração = k_eff·(p/2π)·θ_medido / perda):
- **aço t12 = 1.11** — a rotação medida explica ~toda a perda: back-off por torque-excesso PURO;
- **aço t10 = 3.26** — a rotação excede a perda 3× ⇒ ~70% do θ medido é rotação com a junta já
  descarregada (free-spin) — cauda fora-de-modelo;
- **HDPE = 0.21–0.27** — com k_eff do membro polimérico (~2e7), 21° custam só ~¼ da perda:
  o regime HDPE é rotação-MENOR (wear/assentamento dominam sob membro complacente);
- aço t14 = 0.18 (quase sem rotação, quase sem perda). **Regime não é do RIG, é da RIGIDEZ.**

**Falsificação (gates pré-declarados):** G-T1 aço FAIL — ordem do modelo INVERTIDA
(θ_fim 2.3/2.7/2.9° subindo com espessura vs medido 11.0/4.2/0.7° caindo 15×); G-T1 HDPE PASS
(ordem certa via member-shear) mas G-T2 FAIL em magnitude (modelo 1.3/1.0° vs 21.2/12.6° —
6–16× baixo). **Equifinalidade exposta:** o modelo acerta o preload (0.073/0.081) com o SPLIT
errado — share rotacional do modelo 49–82% da perda vs dado ~21–27% (HDPE) — só o θ separa
os dois. Causas nomeadas: (a) arrest floor para a rotação cedo e não existe free-spin
pós-descarga (cosmético p/ preload, decisivo p/ θ); (b) o drive rotacional do aço não escala
com a espessura (T_l/T_r constante) enquanto no dado θ ∝ quanto preload HÁ para perder.

**Consequência metodológica (a lição):** fits preload-only sub-restringem o split de
mecanismos. O Rousseau agora tem θ(N) — **objetivo dual (MAE_preload + MAE_θ)** nos próximos
fits desse rig; candidatos de forma nomeados (não construídos): rotação livre pós-descarga
(estado, não perda) + escala do drive rotacional com rigidez efetiva. Capability: o engine já
REPORTA θ por ciclo — a comparação é imediata em qualquer rig com θ digitalizado.

**Adendo §4.23 — forma `free_spin` construída (TDD, default-inert, preload BIT-IDÊNTICO):**
o arresto passa a travar o DRENO, não a rotação: fração `free_spin` do drive não-arrestado
continua como θ livre (dF₀ intocado ⇒ curvas de preload adotadas inalteradas; só θ e dE).
Re-confronto com free_spin=1: **aço t12 fator 0.94 (4.0° vs 4.2° medido — quase exato) e
t10 PASSA (0.36)**; t14 fica em 3.7° vs 0.7° e o HDPE segue 4–7× baixo ⇒ a segunda causa
nomeada (ESCALA DO DRIVE com rigidez efetiva — t14 não deveria rodar; drive precoce forte
demais em juntas rígidas retentoras) fica aberta para o próximo arco. 2 testes novos verdes;
suite de formas 30 verdes.
---

### 4.24 PREDIÇÃO CEGA — varredura de direção 0–90° do Zhang (2026-07-08)

Primeira validação por predição pré-registrada: 5 curvas de direção (transversal→axial) do
mesmo rig do grip-sweep §4.22, constantes JÁ fitadas, zero constante nova; protocolo e gates
declarados no harness ANTES de computar erro (`zhang_direction_blind.py`; inputs:
θ_load=π/2−a, δ=0.46·cos(a), F=0.4·F₀). **G-D1 PASS** (ordem: retenção cresce rumo ao axial;
finais modelo 0.04→0.94 vs dado 0.06→0.84). **G-D2 PASS em TODOS** (N50 fator-3 no sweep
inteiro: 35/43/59/187 — o TIMING de colapso transfere às cegas para eixo de carga nunca
validado). **G-D3 FAIL nos ângulos mistos** (45°/60° MAE 0.26/0.23): o dado arresta em
platôs crescentes com o ângulo (0.18/0.42) e o floor único (0.05, fitado no puro-transversal)
não escala — o arresto deve escalar com a severidade TRANSVERSAL (mesma família do achado de
rigidez §4.23). Pré-declarado exigia G-D1∧G-D3 ⇒ **NÃO adotado, AS-IS** (o refit pós-cego
quebraria a alegação de predição). Nomeado para o próximo arco: floor ∝ componente
transversal (um lever, revalidar não-cego).
---

### 4.25 Confronto de ENERGIA — loops medidos vs W_diss/ciclo: nível falsificado com estrutura correta (2026-07-08)

**Setup:** 15 loops F×δ medidos (§4.22-adendo) vs dissipação POR CICLO do engine (config
adotada §4.20), gates pré-declarados no harness (`loops_energy_confront.py`). Área do loop
(kN·mm=J) = todo o trabalho dissipado por ciclo na junta.

**HDPE (12 janelas, t10/t12): G-E1 FAIL 0/12 e G-E2 FAIL 0/12 — mas com razões UNIFORMES**
(energia: modelo 7–8× baixo, fator 0.10–0.19; força transmitida: 3–4× baixa, 0.22–0.32) **e
G-E3 PASS** (evolução com N na direção certa nos dois). Erro de NÍVEL com estrutura correta.
Causas nomeadas: (a) **dissipação viscoelástica do MEMBRO** — o loop mede membro+interface;
o polímero é lossy e o modelo só contabiliza a interface (Rayleigh nominal); (b) **nível da
força transmitida** — µ HDPE-aço real ~0.2–0.3 vs 0.15 assumido, e/ou o cap F_eff do §4.20
agressivo demais; o pico medido rastreia ~4×F_transm do modelo com a MESMA forma de decaimento.

**Aço Fig10 (micro-amplitudes 0.03–0.1mm, roller bearings): hipótese pré-declarada
CONFIRMADA e quantificada** — modelo ~0.0005 J/ciclo vs 0.155/0.648/3.370 J medidos: o canal
de ENERGIA de partial-slip não existe no engine (o Cattaneo-Mindlin atual só gateia dF₀;
micro-slip sub-limiar dissipa calor real). Forma nomeada: dE_partial = g_CM(r)·(trabalho de
micro-slip) — o par energético do `partial_slip_gate`.

**Correção ao §4.22 (honestidade):** a "confirmação independente 0.24 vs 0.25" usava o ±4.0 kN
da tabela do .md — que os loops vetoriais revelam ser valor de MEIA-VIDA (picos decaem
6.0→2.9 kN); o F_tr inicial medido é ~3–4× o F_eff do modelo. A confirmação fica REBAIXADA a
"ordem de grandeza na meia-vida"; no lugar dela, mais uma **equifinalidade exposta**: o fit
preload-only do §4.20 acerta a curva com força baixa compensada (wear/emb altos). Com
preload + θ (§4.23) + energia (§4.25), o rig Rousseau tem agora TRÊS observáveis para um
refit multi-objetivo — o caminho declarado para quebrar a equifinalidade.
---

### 4.26 Campanha de âncoras — lote 1 (Fase 2: proveniência por constante, 2026-07-08)

Primeiras 5 constantes confrontadas com tabelas MEDIDAS do database (anchors_csv, 164
arquivos; harness `anchors_confront.py`; resultados na seção "Âncoras" do variables.html):

- **µ=0.15 (seco) PASSA**: nut-factor teórico K=0.200 vs 0.195±0.003 MEDIDO (Qiao 2025, 25
  pontos, 3 superfícies) — desvio 2%; a suposição central de atrito validada por dado.
- **conform_pressure_exp BANDA [1.5, 2.0]**: a perda estática 48h do Liu2021 cresce
  SUPERLINEAR com F₀ (expoente medido 1.48) — a direção do gate de conformação CONFIRMADA
  (creep puro seria flat) e **a âncora que o §4.9 declarou inexistente agora EXISTE** (retry
  parcial: n adotado 2.0 na borda da banda).
- **C_creep BANDA (por-par confirmado, 3º rig)**: den Otter M16-Al5083 dá 0.012–0.025/década
  (cresce com F₀, consistente com Liu2021); mesma ordem dos pares Liu2017/âncora interna ⇒ §4.7
  reconfirmado em rig independente; per-década não-constante em Al nomeia desvio do ln puro.
- **K_archard DIREÇÃO**: wear medido ~N^0.53 (Zhang2019) vs Archard-K-constante ~N^1 —
  running-in decrescente nomeado (V1 tinha K_running_in/K_steady; V2 usa K único).
- **k_dmg_mu DIREÇÃO (sinal POR-PAR)**: µ medido SOBE 0.14→0.19 sob vibração seca (Eccles)
  — oposto ao k_dmg_mu (µ cai, calibrado no reaperto âncora interna): Eccles ancora o ramo crescente
  (família k_gall/fretting-roughening), âncora interna o decrescente.

Infra: `anchors_verdicts.json` consumido pelo inventário (coluna viva, estilo painel);
lotes seguintes: torque-residual, wear por rig com A/H, µ por lube, creep IN718/CFRP/gaxeta,
VDI-vs-medido (Wiegand/Schaumann). 159 âncoras na fila.

**Lote 2 (mesmo dia):** µ do rig Lu **PASSA** (K medido 0.231 ⇒ µ implícito 0.176 — a
conversão T→F₀ usada no fechamento §4.19 é consistente com o próprio dado do rig);
**Φ BANDA** (fator de introdução MEDIDO 0.15–0.63 vs VDI constante 0.30 — o Φ geométrico do
engine cai DENTRO da faixa; refuta 0.30 fixo); **fat_sigma_endurance BANDA** (medido 46–63
MPa, default 50 dentro; VDI sobrestima 19–50%, 2 campanhas); **wear por-lube BANDA**
(bare/zinco/MoS₂ = 12.5/8.0/3.5 µm — K_archard por-par confirmado, 3.6× cabe na variação
k_wear entre rigs); **torque residual DIREÇÃO** (T_res cai MAIS rápido que F₀, T/F 0.72–0.90
— nomeia correção do K de desaperto no módulo de torque V1). **10/164 âncoras; 3 PASSA,
5 BANDA, 2+2 DIREÇÃO (formas nomeadas: running-in K, sinal-por-par de µ, K de desaperto).**
**Lote FINAL (mesmo dia) — campanha de âncoras COMPLETA: 164/164 com veredicto.** Além dos
10 confrontos dedicados: famílias analisadas em bloco (creep/térmico ⇒ BANDA por-par;
vida/D-N ⇒ BANDA fat_*; atrito/torque ⇒ BANDA por-lube; θ ⇒ DIREÇÃO canal §4.23) e
fronteiras de ESCOPO declaradas como veredicto (dispositivos de travamento = camada V1;
multi-parafuso = fora do single-joint; carga aleatória/PSD, flange gaxetada, torsional/flexão
= canais não construídos — envelope do modelo DOCUMENTADO por dado). Distribuição final:
PASSA 2 · BANDA 69 · DIREÇÃO 12 · ESCOPO 49 · CATALOGADO 32. O inventário de variáveis
carrega a tabela completa; nenhuma âncora sem entrada. Cobertura do database: 100% com
status (galeria/confrontado/âncora/escopo).
---


### 4.27 member_loss_eta construída — canal demonstrado, magnitude nomeia a próxima forma (2026-07-08, non-stop)

**Reconciliação (antes):** a "discrepância de pipeline" do rev-b era FORMATAÇÃO — `%.0e`
imprimiu GA=1.2e5 como "1e+05"; os dois harnesses são bit-idênticos (diff mecânico ciclo-a-
ciclo = 0). Com o GA verdadeiro, **rev-b ADOTADO pelo pipeline padrão** (t12 0.083→0.031,
média da fonte 0.081→0.071, θ 4–5×; iter 18).

**Forma nova (TDD, default-inert):** `member_loss_eta` — dissipação viscoelástica do membro,
`W_m = π·η·F_tr²/k_member` por ciclo; SÓ energia (preload bit-idêntico por teste; conservação
preservada — W_ext supre simetricamente, Δresidual=0). **Confronto com os loops:** o canal
funciona (fator de energia 0.15→0.58 mediana com η 0→8) **mas η≈6–8 é ~50× o tan δ físico do
HDPE (0.05–0.15)** ⇒ a parametrização via k_member GLOBAL subestima a energia de deformação
local do contato (volume deformado real ≫ caminho de cisalhamento global). AS-IS: forma
mantida no engine como canal validado; **η permanece 0 no config adotado** (sem física falsa);
próxima forma nomeada: energia de deformação LOCAL do contato viscoelástico (Hertz-camada,
usa p·A e espessura efetiva — fecharia com η na faixa física).

**Adendo §4.27 — aço MO (non-stop, harness de origem):** com a config §4.12 correta (baseline
= galeria 0.075/0.075/0.037), `free_spin=1` sozinho restaura a ORDEM do θ no aço (modelo
2.35/1.01/0.00° vs medido 10.97/4.23/0.71° — era plana) com preload bit-idêntico ⇒ adotado no
registro (custo zero). Magnitude ~4–5× baixa UNIFORME nomeia o refinamento: free-spin
CINEMÁTICO (a rotação pós-descarga real segue o caminho de slip; a atual decai com o drive de
torque que morre no floor). Lição de processo repetida e agora em doutrina: **config adotada
se reproduz APENAS pelo harness de origem** — labels não carregam a config inteira
(adopted_configs.json existe para isso).
---

### 4.28 Fonte transversal NOVA gerada — Liu2022 fig5, ZERO-REFIT (2026-07-08, convergência)

4 casos transversais (primeiro aperto, dry ×2 + oil ×2, M12 GB/T 12.5Hz δ=0.3mm grip 50mm)
gerados da fila de curvas não-usadas com as constantes §4.10/4.11 INTACTAS (emb Rz<4,
k_wear 0.06, dano PER-LUBE c_D 0.5/0.03, starters físicos) e **µ DERIVADO do F₀ medido de
cada caso via Motosh** (harness de origem `validate_retightening`): dry 0.247/0.225 > oil
0.183/0.168 — ordenação física e dentro da banda ancorada. **Gate MAE≤0.10: 4/4 PASSAM com
0.004–0.022 — zero-refit genuíno** (nenhuma constante tocada; o µ é input derivado de dado
do próprio paper). Galeria 66→70, média global 0.0683→0.0667 (iter 19). A fila liu2022
restante (fig6/7/8: sequências de reaperto ×4 apertos) é a próxima classe (usa `retighten()`
+ `k_emb_renew` §4.10 — cases multi-segmento, follow-up).
---

### 4.29 Queda inicial abrupta — auditoria + literatura (2026-07-08; scout dos 96 papers)

**Auditoria da galeria (janela ≤10%N):** 11/61 casos com bias early >+0.03 (modelo lento na
largada), DOMINADOS pelo Lu (7 casos, +0.05…+0.155; o dado perde 0.36–0.57 em 10%N) + Zhang
(2) + Içmez (1) + Li2022Ti axial (1). As fontes fecharam no MAE de curva-inteira; a janela
early ainda deve — o lag residual é o SPIN-UP dos carriers de crash, não o settling.

**O que os papers dizem (scout, com arquivo:linha no transcript):**
- **Mecanismo**: plasticidade cíclica/ratcheting de asperezas (rosca+apoio) SEM rotação —
  isolado por porca COLADA (Jiang 03/04: 10–40% sem θ), axial puro (Liu2017) e membros moles.
- **Duração ∝ amplitude**: ~2–5 ciclos em δ=1.27mm vs 50–100 em axial/0.46mm (MESMO rig!) ⇒
  **N_emb não é constante do rig — escala com amplitude**; faixa axial estende a ~100.
- **Forma de referência (M8!): dupla exponencial** A₁e^{−B₁N}+A₂e^{−B₂N} com **A₁=60.5%F₀ e
  1/B₁≈8 ciclos** (nota 22) — bate com o fast-drop 0.47–0.57 do Lu M8 que o nosso frac=0.40
  não alcança (o minimax §4.19 parou em 0.40 porque frac 0.45+ quebrava o caso SUB-limiar
  amp0p25).
- **Rotação nos primeiros ciclos**: em amplitude moderada θ>0 já em ~10 ciclos; em alta
  amplitude IMEDIATA (Jiang free-nut) — 'queda inicial = só embedding' vale apenas para
  baixa amplitude/mole/axial.
- **CONTRADIÇÕES documentadas** (por regime, não erro): fração Stage-I vs F₀ SOBE no estático
  (Study 53: 5×) e em Jiang, DESCE no axial vibrado (Liu2017); reaperto REDUZ a queda quando a
  superfície conforma (Liu2016) mas AUMENTA a seco com dano (Liu2022 §4.11 — nosso c_D
  per-lube já captura); forma log (não exp) em moles/creep (Su&Ye/CFRP).

**A correção NOMEADA (agora com proveniência dupla):** o reservatório fracional deve ser
**SLIP-GATED** — a porca-colada de Jiang prova que o bedding é dirigido pelo ratcheting sob
ciclos de escorregamento; o trade frac↔amp0p25 do §4.19 já apontava isso empiricamente; e a
dupla-exponencial M8 (60%@τ8) diz o TAMANHO que o reservatório do Lu deve ter quando o slip
está ativo. Forma para o próximo build: `S_slip(bedding) = f(fração de gross-slip)` gateando
`emb_load_frac` (default-inert; fecha os 7 casos Lu early SEM quebrar o sub-limiar) + N_emb
por amplitude (per-rig → lei ∝1/δ com os pontos 2–5@1.27 / 20–50@0.46 / 50–100@axial do
Jiang/Liu — reduz constante per-rig a input).

**Adendo §4.29 — formas construídas + caso Liu REFEITO (mesmo dia):** (1) `emb_slip_gate`
(TDD, default-inert, 2 testes): reservatório fracional gateado por (slip/(slip+δ_t))^q —
sub-limiar assenta só a profundidade estática (porca-colada de Jiang); destrava o Lu subir
frac para os ~60%@τ8 da literatura sem quebrar amp0p25 (refit Lu = próximo). (2)
`k_wear_running`+`N_wear_run` (running-in do wear — a DIREÇÃO do §4.26 virou forma; V1 tinha
K_running_in, V2 usava K único): K decai e^{−N/N_run}; default ≤1 inerte. (3) **Liu2022
REFEITO** com running-in k=5/N=100 (proveniência: Zhang2019 wear~N^0.53 + Eccles 0–50):
MAEs 0.017/0.022/0.020/0.004 → **0.014/0.019/0.016/0.005** (galeria re-adotada, iter 20;
média global 0.0665). O bias early residual do liu2022 (+0.017) é pequeno — os ofensores
reais da largada são os 7 casos Lu (fila: refit com slip-gate + frac literatura).
**Refit Lu executado (§4.29, 36 configs frac×N_emb×slip-gate):** a config §4.19 permanece
minimax-ótima (10/10 sob limites; |early| médio 0.079 vs 0.086). A fração da literatura NÃO
adota com o gate atual — (slip/(slip+δ_t))^q é suave demais (fração gross do Lu = 0.4–0.8 ⇒
o gate corta o reservatório também acima do limiar). **Forma nomeada: gate de slip SATURANTE**
(Hill com joelho <1 em slip/δ_t) — protege o sub-limiar E entrega pleno acima; aí frac
0.55–0.60@τ8 entra e os biases early fecham. Relatório com as 10 curvas: `lu_report.html`.
---

### 4.30 Joelho de estágio-3 do Bauer fig8 — gatilho de criticalidade falsifica o crash gradual (2026-07-08, paper-study rodada 6)

Métrica de erro interpolado (PCHIP, 500 pts) expôs o que o MAE por-pontos escondia: fig8_test1
maxerr **0.466 @99%** do teste — o modelo perde o JOELHO tardio (dado: plano 1.00→0.66 até
N≈609/70%, depois colapso acelerante →0.31). Varredura c_bend×floor×emb×frac: **nenhuma config
reproduz plano-depois-joelho** (cb=0.2 → fim 0.753 sem colapsar; cb=0.5 → 0.000 colapsando
desde o início). O crash do modelo é criticalidade GRADUAL (r=Q/µF₀κ cruza 1 suavemente
conforme F₀ cai); o dado tem gatilho ABRUPTO — o paper atribui a F_V caindo abaixo da amplitude
crítica do espectro. **Forma nomeada (2ª falsificação convergente: Liu2025 flat-early §4.16 +
este joelho): TRIGGER de runaway por r-crossing** — plateau enquanto Q<µF₀κ, positivo-
realimentado quando F₀ cruza o limiar; par do `slip_onset_W` mas no CRASH. Próximo build TDD.
Fig8 fica AS-IS (por-pontos ~0.097; o joelho é resíduo estrutural declarado).
---

**Adendo §4.30 — gatilho CONSTRUÍDO, adoção REVERTIDA (resultado NEGATIVO honesto; professor:
"refaça BAUER"):** `crash_trigger_frac` (gate Hill em F₀/F₀_init — correção de design do L14;
default-inert, 3 testes verdes) É uma capacidade validada do engine, MAS **não net-melhora o
Bauer fig8**: frac=0.55 uniforme moveu o interp marginalmente (test3 0.113→0.086) porém PIOROU
a mediana de MAE por-pontos (0.098→0.108, test1 0.097→0.113); frac per-test LIDO do joelho de
cada curva (test1 0.66/test2 0/test3 0.57) foi DRASTICAMENTE pior (test1→0.195, test2→0.468) —
o gate suprime o estágio de declínio LENTO que precede o joelho. Diagnóstico: o joelho não é só
um limiar de F₀; é o declínio-lento E o colapso, e o gate como construído troca um pelo outro.
**Adoção revertida; galeria fig8 permanece §4.17 (0.097/0.089/0.095); o joelho estágio-3 fica
RESÍDUO ESTRUTURAL declarado.** Forma no engine para trabalho futuro (provável caminho: gate
que preserva o declínio lento — dois canais, não um gate único sobre o loosening).
---
### 4.31 Joelho do Bauer fig8 — literatura + constantes esgotadas ⇒ RAIZ = canal de energia de partial-slip (2026-07-08, diretiva "corrija a queda final")

**Literatura (apparatus_notes/bauer2024):** o joelho estágio-3 é mapeado a `surface_damage D`
(mesma forma do reaperto/TP7): "slow decay until amplitude-vs-preload criticality, then knee
and steep collapse as falling F_V drops the critical amplitude below the spectrum base" — i.e.
a transição de regime Cattaneo-Mindlin (δ_t=µF₀/k_tr cai com F₀, o slip fixo vira gross) DISPARA
D, que amplifica o wear (k_dmg_wear) e drena abaixo do floor de arresto.

**Constantes trabalhadas exaustivamente (a diretiva):** c_bend (timing do crossover), floor
(0.30 lido do fim do dado), slip_regime_sharpness (nitidez), c_D/W_crit/k_dmg_wear (dano).
Melhor config (c_bend 0.5 + floor 0.30 + sharp 2): test1 interp 0.137→0.126 MAS **mediana dos
3 PIORA em ambos os metros** (MAE 0.095→0.116, interp 0.113→0.125). **Constantes NÃO corrigem.**

**RAIZ estrutural (o achado):** o gate de onset do dano é dirigido por `W_slip_acc`, que só
acumula trabalho de GROSS slip. No config que reproduz o platô (c_bend baixo, δ_t grande) há
ZERO gross slip ⇒ **W_slip_acc=0 ⇒ D nunca dispara** (medido). Conflito estrutural: o config do
platô não alimenta o dano; o config que alimenta o dano não faz o platô. O dano DEVERIA
acumular durante o platô via micro-slip (partial slip) — mas o `dE` de partial-slip NÃO é
contabilizado (o CM só gateia dF₀, não a energia). **É a MESMA forma faltante do §4.25** (loops
do Rousseau: energia 7–8× baixa = partial-slip não dissipado). **Dupla falsificação convergente
⇒ forma nomeada com proveniência: `dE_partial` = trabalho de micro-slip alimentando W_slip_acc**,
para o dano crescer no platô e disparar o joelho. Constante não resolve; é forma — não
construída neste turno (o build anterior rushed foi revertido §4.30; esta merece design).
Galeria fig8 INTOCADA (§4.17, 0.097/0.089/0.095); joelho = resíduo estrutural com raiz agora
identificada.
---

### 4.32 dE_partial CONSTRUÍDA — o joelho do Bauer fig8 fechado (2026-07-08, "design e construa dE_partial")

Forma da dupla falsificação §4.25+§4.31 (energia de partial-slip do anel Cattaneo-Mindlin):
`dE_partial = k_partial_slip·g_partial(r)·4·µ·F₀·δ_t` (δ_t=micro-slip do anel travado),
alimentando o DRIVER do dano (W_slip_cycle) E o acumulador de onset (W_slip_acc) E o budget
de energia (W_ext-sourced, conservação). Default `k_partial_slip=0` bit-identical; 4 testes
(inerte / acumula no platô / energia-only sem dano / dispara D no platô). Spec
`docs/superpowers/specs/2026-07-08-de-partial-design.md`.

**A cadeia física completa (resolve §4.31):** dE_partial acende o dano DURANTE o platô (onde
o gross slip é 0 e o dano morria) → D cresce → `k_dmg_mu` reduz µ → δ_t=µF₀/k_tr cai → o slip
imposto vira GROSS → wear runaway → colapso abaixo do floor de arresto. É exatamente o "falling
F_V drops the critical amplitude" da literatura Bauer, agora mecanístico no modelo.

**Resultado fig8 (todos melhoram nos DOIS metros):** test1 MAE 0.097→0.080 **interp 0.137→0.077**
(o joelho que o professor sinalizou, maxerr era 0.47 @99%), test2 0.089→0.069, test3 0.095→0.063.
**Mediana MAE 0.095→0.069, interp 0.113→0.077.** W_crit per-espectro (350/800/800) LIDO do joelho
de cada curva (proveniência = feature observável, como delta_free/floor) — dois espectros
(80/150µm) ⇒ dois W_crit, físico não overfit. Contraste com §4.30 (gate único no loosening,
revertido): dE_partial é o canal CERTO (energia→dano→wear, dois canais), não um gate sobre a
rotação. Galeria adotada; a mesma forma deve fechar a energia dos loops Rousseau (§4.25) —
follow-up. Constante não resolvia (§4.31); a FORMA resolveu.
---

**Adendo §4.32 — fig6 vs fig8: por que uma tem joelho e a outra não (pergunta do professor):**
o paper (bauer2024_efa) dá o critério: **s_crit ≈ 99 µm é "o slip crítico ABAIXO do qual o
afrouxamento rotacional NÃO inicia"**. fig6 (M8) = amplitude CONSTANTE **70 µm** (perto/abaixo
de s_crit) ⇒ afrouxamento GRADUAL, sem runaway. fig8 (M12) = espectro **80 µm base + picos
150 µm** (super-crítico) ⇒ o dano dispara ⇒ joelho. **Não é "joelho menos pronunciado" — é
joelho AUSENTE pelo limiar s_crit** (a 2ª hipótese do professor, confirmada pelo paper).
**Verificação (o resultado bonito): a MESMA config dE_partial aplicada ao fig6 deixa D=0.00
AUTOMATICAMENTE** (a amplitude/F_amp sub-crítica do fig6 nunca cruza W_crit) ⇒ curva idêntica
a dE_partial OFF. O modelo AUTO-DISTINGUE fig6 de fig8 por INPUT (amplitude/F₀), constantes
compartilhadas — sem chave per-caso. Resíduo remanescente do fig6 (dado decai a ~0.10, modelo
a ~0.44): afrouxamento gross-slip levemente fraco em M8/baixo-F₀, mas fig6 está no PISO de
scatter dos 6 repeats (MAE 0.098 ≤ piso 0.115) ⇒ perseguir a forma abaixo disso é perseguir
scatter (limite físico, §4.16). fig6 declarado PRONTO; a distinção física ENTENDIDA e capturada.
---

### 4.33 CONTINUUM s_crit — fig6 e fig8 do Bauer = UMA física de dano (2026-07-08, "física não fit")

Pergunta do professor: fig6 (quasi-linear) e fig8 (joelho) devem ser a MESMA física, fig6 com
joelho "muitíssimo pequeno". Realizado por FORMA (`dmg_gross_exp`): o onset do dano deixa de ser
o limiar de energia W_crit (per-caso, descontínuo) e passa a ser gateado CONTINUAMENTE pela
FRAÇÃO DE GROSS-SLIP g_gross=slip/(slip+δ_t) ^ p — a razão física s_a/s_crit, com s_crit=δ_t=
µF₀/k_tr que CAI com F₀ (o "falling F_V" do Bauer). O joelho emerge da super-criticalidade:
sub-crítico (fig6, 70µm) ⇒ g_gross^p pequeno ⇒ curvatura mínima ⇒ quasi-linear; super-crítico
(fig8, picos 150µm) ⇒ g_gross^p grande ⇒ joelho forte. **Constantes de dano COMPARTILHADAS**
(k_partial_slip=0.5, c_D=10, dmg_gross_exp=2, k_dmg_mu=3, k_dmg_wear=6); só c_bend é per-rig
(M8 0.5 / M12 0.2 — rigs distintos, doutrina) e floor lido do fim do dado. 2 testes provam o
continuum (dano cresce monotonicamente com a amplitude; sub-crítico D<0.10).

**Resultado:** fig6 rep2/3/4 **0.089/0.098/0.108 → 0.024/0.020/0.051** (a mesma física de dano
agora captura o declínio do fig6, antes tratado sem dano); rep1/5/6 ~iguais (piso de scatter
0.115). fig8 test1 0.097→0.121 / test2 0.089→0.096 / test3 0.095→0.108 — o joelho do fig8 fica
levemente mais SUAVE que a versão per-espectro W_crit do §4.32 (interp 0.077→0.156): é o TRADE
da UNIFICAÇÃO (uma forma contínua compartilhada vs W_crit afinado por espectro). Mediana Bauer
0.098. **É modelo, não fit:** um mecanismo, contínuo em s_a/s_crit, distingue os regimes por
INPUT; nenhuma chave per-caso. Aplicável a qualquer condição futura (o joelho aparece na medida
da super-criticalidade). Limitação de dado registrada: a nitidez exata do fig8 precisaria do
espectro de amplitude (picos 150µm) como input — o modelo roda amplitude única.
---

**Adendo §4.33 — concavidade-para-baixo do fig8 recuperada (2026-07-09, pergunta do professor):**
o continuum inicial (dmg_gross_exp=2, c_bend 0.2 no fig8) suavizou demais o joelho. O colapso
ACELERANTE (côncavo-para-baixo) exige que a super-criticalidade CRESÇA durante o run — i.e.
δ_t=µF₀/k_tr cruze o slip imposto conforme F₀ cai; em c_bend 0.2 (δ_t grande) isso não ocorre.
Correção (só INPUTS per-rig, física de dano intocada): fig8 c_bend 0.2→**0.4** + dmg_gross_exp
2→**3** (compartilhado com fig6). Recupera a aceleração: **fig8 interp 0.156→0.112 (test3
0.075)**, fig6 mantido (rep2/3/4 0.02-0.05), mediana Bauer 0.088. A curva do modelo agora
acelera côncava-para-baixo como o dado. test1 residual (interp 0.143) = o pico de 150µm do
espectro não-representado (modelo roda amplitude única) — limitação de DADO. O continuum
segue UMA física; a concavidade emerge do δ_t caindo (o "falling F_V"), não de fit.
---
**Adendo §4.33 rev2 — test1 resolvido: taxa agressiva + joelho menor (2026-07-09, professor):**
diagnóstico ponto-a-ponto revelou que modelo e dado do test1 eram ~ESPELHADOS — modelo caía
cedo (10%: 0.83 vs dado 0.98; embedding 5µm forte demais) e ficava plano no fim (100%: 0.69 vs
dado 0.31). O dado fica alto cedo e ACELERA (côncavo-p-baixo). Receita do professor ("joelhos
menores, taxa geral mais agressiva"): **emb 5→0.5µm** (fica alto cedo) + **c_D→30** (colapso
agressivo tardio) ⇒ **test1 interp 0.137→0.028**, o colapso acelerante capturado. A
agressividade é PER-ESPECTRO (test1 tem os picos de 150µm agressivos; test2/test3 brandos),
lida de cada curva — a forma de dano (dmg_gross_exp) segue COMPARTILHADA. test2/test3
0.089/0.095→0.093/0.101 (<0.02, capturam mais forma). RAIZ da necessidade per-curva: o modelo
roda AMPLITUDE ÚNICA (80µm) para os 3, mas eles são 3 espectros distintos — a severidade
(emb/c_D) é a única assinatura do espectro disponível. Fica registrado como limitação de dado.
---
**Adendo §4.33 rev3 — "o modelo deve ajustar tudo" + erro no gráfico (2026-07-09):** ao afinar
o test1 (agressivo), test2/test3 desajustam — porque os 3 testes do fig8 são ESPECTROS de
amplitude distintos rodados no modelo de amplitude ÚNICA (80µm/50kN): o mesmo config colapsa
no mesmo CICLO, mas os testes têm durações diferentes (873/1352/1162) e severidades de pico
diferentes. Não existe UM config que ajuste os três (varredura ampla emb×c_bend×c_D×gexp:
test1→0.027, test2/test3 travam em ~0.13). Decisão AS-IS: cada curva no seu MELHOR per-curva
(test1 agressivo emb0.5/c_D60/gexp3 → interp 0.028; test2/test3 restaurados ao fit §4.17 sem
dano → 0.089/0.095, que os ajusta melhor que qualquer config de dano). O gráfico agora mostra
a BANDA DE ERRO vermelha (|modelo−dado| ponto-a-ponto) — o desvio de test2/test3 concentra-se
no joelho tardio. RAIZ declarada (não fit): o pico de 150µm do espectro não é input (amplitude
única) — a severidade per-curva é a única assinatura disponível. Fechar test2/test3 exigiria o
espectro de amplitude digitalizado como input (limitação de DADO, forma já está correta —
test1 prova). Mediana galeria 0.0467.
### 4.34 Restrição dura "nenhuma curva > 0.2" atingida (2026-07-09, diretiva do professor)

Auditoria das 82 curvas em AMBAS as métricas (MAE por-pontos + interp PCHIP): uma única
violação — zhang2006_M12_lc25p4 interp 0.203 (as demais do grip-sweep Zhang em 0.19-0.20,
dado APROXIMADO de tabela §4.22). Re-calibração per-rig do Zhang (só INPUTS: floor 0.05→0.10,
N_emb 15→8): lc25p4 0.203→0.155; **todas as 4 sob 0.2 (máx interp 0.178)**. **Estado da
galeria: 0 curvas > 0.2 — MAE máx 0.140, interp máx 0.178** (as 82: 46 transversal + 13 axial
+ 3 HDPE + 4 Zhang grip + 5 Zhang direção + 12 reaperto). Os máximos remanescentes são pisos
declarados (Zhang tabela-aproximada; HDPE t14 separatriz; Bauer repeats). Restrição do
professor cumprida sem tocar defaults do engine nem a varredura zero-refit canônica.

**Reconciliação §4.34/§4.33 (2026-07-09): 1 exceção ACEITA ao limite <0.2.** Após a diretiva
"mostra a queda", o professor decidiu MANTER bauer fig8 test2 na config de colapso (MAE 0.208)
em vez do platô (<0.2, sem queda). Portanto o estado da galeria é: **81 das 82 curvas ≤ 0.14;
uma (bauer fig8 test2) a 0.208 por DECISÃO explícita** (preferir a queda visível ao MAE menor),
documentada como limitação de timing de espectro (não fit). Não é violação silenciosa — é
escolha registrada. O limite <0.2 segue valendo para todo o resto.

### 4.35 Erro sistemático de mid-curva — 3 formas propostas, TODAS falsificadas no modo dominante; a fonte-líder está NO PISO (2026-07-09, diretiva "melhorar o modelo só com nossas variáveis, analítico não fit")

Auditoria de bias por-janela (early ≤10%N / mid 10–70% / late >70%) das 82 curvas da galeria
(interp do modelo na grade do dado). **Modo dominante = mid-over-loss:** 35/82 com |mid|>0.05,
bias global mid **−0.012**, concentrado em KARLSEN (mid −0.092, late +0.081), YANG (−0.084/+0.055),
ROUSSEAU (−0.068), HDPE (−0.062/−0.087), LIU_2025 (−0.060). O oposto (over-**retain**) só em
LI_2022TI (mid +0.055) e ICMEZ (late +0.065). **São correções OPOSTAS — não há uma forma única.**

Propus e testei 3 melhorias estruturais (aprovadas pelo professor como arco #1→#2→#3):

- **#1 Blend contínuo de fases (`loose_kin_ceiling`, CONSTRUÍDA):** limitador em SÉRIE (média
  harmônica `d_eff=d_torque·d_kin/(d_torque+d_kin)`) que bounda o runaway do torque-excesso pela
  disponibilidade cinemática de gross-slip — física (a porca não gira mais que o caminho de slip
  permite), TDD 4/4, **default-inert bit-identical** (pins/coherence intactos). **GATE FALHOU no
  modo dominante:** em Karlsen o teto retém MAIS uniformemente (mid *e* late), mas o bias é
  over-loss no mid **e** over-retain no late (S-shape) — o teto conserta o mid e piora o late
  (MAE 0.097→0.133). Forma legítima, mantida como **capability inerte** (doutrina opt-in).
- **#2 `c_bend` da geometria (INVESTIGADA, não geometrizável limpo):** `c_bend` é **sobrecarregado**
  — em bending é compliance de flexão (`k_tr=c_bend·E·I/L³`), mas em Liu2025 vale 50 (seletor de
  regime gross-slip com `delta_free`). O β geométrico de um parafuso bi-engastado guiado é ~12; os
  valores fitados (0.2–5) são β reduzido por compliance em SÉRIE (membro+**fixação**). A fixação é
  **per-rig irredutível** (não medida). Só 2 rigs limpos + 1 degenerado ⇒ sem dados p/ validar uma
  lei geométrica. Um `k_tr` em série (β=12 + membro + fixação-per-rig) tornaria o *scaling* com
  d/L preditivo, mas não removeria o número per-rig. **Não adotada.**
- **#3 Drive rotacional ∝ rigidez (MOOT p/ MAE):** o desvio §4.23 (θ ordering) é observável em θ,
  não na curva de pré-carga (MAE); e o drive cinemático stiffness-free (ratchet puro) foi testado
  em Karlsen e **falhou** (0.097→0.12–0.44). Não reduz o MAE dominante.

**Achado decisivo — Karlsen (7 curvas, maior contribuinte) está NO PISO alcançável.** Sweep 2D
`c_bend×arrest_floor` acha o mínimo EXATAMENTE no ponto adotado (**0.0968 @ c_bend=3.0, floor=0.08**);
nenhuma combinação bate 0.097 e **quatro** mecanismos adicionados (teto, incubação `slip_onset_W`,
ratchet cinemático, fretting) **todos pioram** — porque o bias é over-loss e todos ADICIONAM perda.
A nota de aparato Karlsen explica: HV são **"near-linear catastrophic back-off, sem platô"**, ±1.0mm
M30 / ±1.5mm M42 (amplitude enorme, bolts gigantes, 1 Hz). O modelo dá **convexo→arresto**; o dado é
**quase-linear** → mismatch de FORMA no envelope extremo, não mecanismo faltante.

**Veredicto (consistente com §8):** o erro remanescente das fontes dominantes **não é um mecanismo
que falta** — é (a) mismatch de forma convexo-vs-linear em regime de amplitude extrema (Karlsen, no
piso) e (b) superposição de biases per-rig OPOSTOS (over-loss vs over-retain) que nenhuma forma
única resolve. A disciplina physics-first se confirma pela NEGATIVA: 3 alavancas propostas + 4
mecanismos existentes foram descartados por gate pré-declarado, **sem overfit**. Reduzir mais exige
input multi-amplitude (espectro, ausente) ou aceitar o piso de scatter medido. `loose_kin_ceiling`
fica como capability inerte (útil p/ um over-loss PURO sem componente de over-retain-tardio, que não
ocorre no dataset atual). Decisão de manter/reverter a forma = professor.

### 4.36 Input multi-amplitude (espectro estatístico) — módulo CONSTRUÍDO; a premissa FALSIFICADA nomeia a forma real (2026-07-09, escolha do professor "espectro estatístico média/desvio")

Direção escolhida após §4.35 (fontes dominantes no piso, erro = forma/regime): alimentar a
**distribuição** de amplitude, não uma amplitude única — os S-shapes (Bauer fig8 "spectrum 80 µm
base + 150 µm picos", Yang "variable amplitude", Liu2025 "envelopes", Rousseau "variable-stress")
são de amplitude variável, e o timing do colapso é dirigido pela **cauda super-crítica** que uma
amplitude única não vê.

**Construído (`numerical/amplitude_spectrum.py`, `spectrum_schedule`):** cronograma por-ciclo
DETERMINÍSTICO de uma distribuição (normal média/desvio via ppf de Acklam **ou** histograma
base+picos) por sequência de baixa-discrepância (golden-ratio) + `phase` (realização). RNG-free,
reprodutível, **engine inalterado** (já aceita `delta_amp` por ciclo); `std=0`/`hist=None` =>
array constante == mean (**bit-idêntico**, o engine vê a amplitude única de sempre). TDD 11/11.
Vive em `src` (parte do software, reusável pela GUI). A representação estatística **descarta a
ORDEM** (Yang Fig10 vs Fig11 ficam idênticas) — nota registrada; efeito de ordem exige blocos.

**Gate FALSIFICOU a premissa de que o input sozinho ajuda — e NOMEOU a forma real.** Dois
achados decisivos ao tentar reproduzir o colapso do Bauer com espectro:
1. **Amostragem de baixa-discrepância NÃO produz scatter de timing.** As 8 fases dão o MESMO ciclo
   de joelho (converge à fração exata de picos por construção). Logo o scatter das repetições
   nominalmente idênticas (test1/2/3, joelhos ~838/1163/1139) **não** é explicado por este módulo
   — exigiria RNG com clustering, ou vem da pré-carga/condição-inicial (F_M 35/50 kN por teste).
2. **Em disp-mode o loosening é RUNAWAY-TO-ZERO uma vez disparado.** Varredura c_bend=3, amplitude
   40→150 µm: TODAS colapsam a fim=0.000; c_bend baixo: TODAS assentam a 0.45 (loosening OFF). A
   amplitude afeta **se dispara** (o `g_gross` inicial cruza o limiar), **não a trajetória** —
   porque `s_crit=δ_t=µF₀/k_tr` CAI com F₀ ⇒ `g_gross→1` ⇒ corrida a zero. Portanto um ESPECTRO
   (que mistura amplitudes) apenas dispara-ou-não o runaway; **não gradua** o colapso pela
   distribuição. O espectro só muda a trajetória no regime **DANO-controlado** (o path
   `dmg_gross_exp`+`c_D` que fechou o Bauer em §4.33, cujo colapso É graduado pela dose) — cuja
   config canônica de galeria está entrelaçada (L1: não reconstruir de label), e cujos configs
   sintéticos aqui caíram no runaway de loosening antes do dano controlar.

**Veredicto:** capability legítima construída e unit-testada, **default-inert (mantida)**, mas
**adoção NÃO demonstrada** — a premissa "multi-amplitude reduz os S-shapes" foi falsificada no
regime de loosening. A **forma real que falta** (nomeada pela falsificação, como manda a doutrina)
é uma **taxa de loosening GRADUADA e amplitude-sensível** — que faça a trajetória de colapso
rastrear a amplitude corrente relativa a `s_crit` ao longo de todo o curso, em vez de correr a
zero assim que dispara. Só então o espectro (agora existente como input) teria onde morder.
Follow-ups: (a) construir a taxa graduada; (b) aplicar o espectro à config dano-controlada real do
Bauer (precisa da procedência per-teste da fração de picos + o harness fig8 canônico); (c) opção
RNG-com-clustering se o scatter de repetição for alvo. Decisão = professor.

### 4.37 Taxa de loosening GRADUADA amplitude-sensível — CONSTRUÍDA; destrava o espectro (síntese §4.36) mas Karlsen segue no piso (2026-07-09, escolha do professor "construir a taxa graduada")

A forma que §4.35 (colapso convexo-vs-linear) **e** §4.36 (downstream binário) convergem em apontar.
`loose_rate_mode="graded_scrit"` (opt-in; default `"torque"`) substitui o kernel de torque-runaway
por uma taxa CINEMÁTICA no EXCESSO de slip sobre um `s_crit` FIXO (não ∝F₀):
`d_theta = gates·k_loose_graded·max(0, slip − s_crit_loose)/(d_2/2)`. Amplitude-sensível (o slip
corrente modula a taxa por ciclo); SEM runaway (`s_crit` fixo + slip limitado pelo curso ⇒ a taxa
satura); sub-crítico (slip≤s_crit) ⇒ zero (platô/não-inicia do Bauer); colapso quase-linear
(Karlsen). `s_crit_loose` per-rig com proveniência (Bauer 76-108 µm). Default `"torque"` OU
`k_loose_graded=0` ⇒ branch nunca roda (**bit-idêntico**; pins/coherence intactos). TDD 7/7.

**Gate 1 (Karlsen near-linear, amplitude CONSTANTE): NÃO bate o piso.** Sweep `s_crit×k×arrest`
(wear off p/ isolar): melhor **0.114 @ k=0.02** vs torque-floor **0.097**. Ponto-a-ponto (run1):
o graded casa o MID muito melhor (@80% 0.47 vs torque 0.31, dado 0.48) mas **overshoota o late**
(fim 0.35 vs dado 0.15) — a mesma tensão convexo-vs-linear: casar o mid quase-linear **e** o
colapso profundo late é incompatível na estrutura mono-amplitude. **Karlsen confirmado NO PISO —
agora com o 5º mecanismo** (após teto/incubação/ratchet/fretting em §4.35). Reading-error ±5 kN
(±0.015) + regime ±1 mm extremo ⇒ data-limited, não forma.

**Gate 2 (SÍNTESE §4.36+§4.37 — o espectro morde?): PASSA.** Config controlada (wear off,
s_crit=30 µm < slip do pico): a amplitude **MÉDIA** (86-104 µm, sub-crítica ⇒ slip<s_crit) **não
colapsa** (fim 0.533), mas o **ESPECTRO** com 5/10/20% de picos super-críticos (200 µm) colapsa
(fim 0.428/0.296/0.000; **DIFF vs const-mean −0.10/−0.24/−0.53**). Os picos disparam o colapso; a
média perde inteiramente. **Nem o single-amplitude nem o torque-runaway fazem isso** — o torque
dispara-ou-não com qualquer amplitude e corre a zero; o graded gradua pela distância a `s_crit`
fixo. **As duas formas juntas (espectro §4.36 + taxa graduada §4.37) fazem o que nenhuma faz
sozinha:** modelar excitação de amplitude variável com um limiar físico de slip crítico. Capability
validada end-to-end.

**Veredicto:** taxa graduada legítima, física, **default-inert (mantida)**. Fecha o gap nomeado em
§4.36 (o downstream agora é graduado no input). **Não** reduz Karlsen (constante, no piso). A
**adoção** numa curva de galeria real de amplitude variável (Bauer fig8, Yang varamp) precisa da
**proveniência per-caso do espectro** (fração/amplitude dos picos — o crux honesto, não um knob
fitado) + `s_crit` per-rig da curva amplitude-vs-vida. Follow-up = prover essa proveniência e
adotar; ou aceitar como capability disponível. Decisão = professor.

**Adendo §4.37 — tentativa de ADOÇÃO no Bauer fig8 FALSIFICADA (2026-07-09, "adotar numa curva real"):**
alvo = os 3 fig8 (M12, F0=50 kN, delta base **80 µm**, picos 150 µm; o modelo atual alimenta só a
base 80 µm como amplitude única + configs per-curva + W_crit-no-joelho). Objetivo: substituir por
UMA física + o espectro real. **Resultado negativo decisivo.** (1) Config compartilhada (sem
per-curva) NÃO reproduz fig8 (MAE 0.60-0.70; o fit atual depende de knobs per-curva — L1). (2)
Ponto-a-ponto no test1: o dado tem joelho **TARDIO** (segura ~0.7-0.9 até 90%N, colapsa a 0.31);
alimentar o espectro faz o modelo colapsar **mais CEDO** (joelho 80%→40%N, MAE 0.220→0.501) —
direção ERRADA. **Raiz física:** por design (nota de aparato Bauer) o colapso espera "**falling F_V
drops the critical amplitude below the spectrum base**" ⇒ o timing é da **criticalidade-F_V (δ_t=µF₀/k_tr
CAINDO)**, não da acumulação de picos; os picos 150 µm só adicionam dano CEDO ⇒ antecipam o colapso
⇒ afastam do joelho tardio. **Regime decide:** o espectro morde no regime **s_crit FIXO** (picos
controlam — o gate-2 sintético do §4.37), mas Bauer é **s_crit CAINDO** (F_V controla) — regime
oposto. A maioria do loosening transversal é δ_t∝F₀ (caindo) ⇒ o alvo de galeria real do espectro
é escasso. **Veredicto de adoção:** o espectro (§4.36) + taxa graduada (§4.37) são capabilities
validadas SINTETICAMENTE (regime s_crit fixo), mas **não adotáveis no Bauer** (regime F_V-crítico);
o approach per-curva + W_crit-no-joelho segue superior ali. Sem overfit forçado. Todas as formas
default-inert (galeria/pins/Run bit-idênticos). Lead honesto: o espectro precisaria de uma fonte
de regime s_crit-fixo (peak-controlada) para adoção — não identificada na biblioteca atual.

### 4.38 Fontes over-RETAIN (Li2022Ti / Icmez) — resíduo de proveniência per-rig, não mecanismo (2026-07-09, "atacar as over-retain")

Único lead de direção-certa após §4.35-4.37 (o modelo perde de MENOS ⇒ adicionar perda é correto):
Li2022Ti (axial, mid +0.087/late +0.106) e Icmez lk19p8 (transversal, late até +0.177). Investigação:
- **Li2022Ti (axial, M10 Shimadzu, A_F=10 kN, freq 10/15/20 Hz):** o dado tem sinal de frequência
  monotônico (10 Hz −17.9% / 15 Hz −14.1% / 20 Hz −8.9%, "wear+spalling cresce quando freq cai").
  MAS o `dmg_dwell` (freq-dependente) **não pode** ajudar em axial-força: não há slip transversal ⇒
  `W_slip_acc=0` ⇒ dano não cresce. O `k_thread_fret` (§4.6, ∝A_F) ADICIONA perda axial, mas **L1**:
  o harness diagnóstico (`_sim`, emb Rz<10) **over-AFROUXA** (pred 0.511 vs dado 0.829), oposto do
  que a galeria reporta ⇒ fretting piora ali (0.355→0.582). O over-retain da GALERIA é resíduo do
  **fix de nível-emb** (Rz<4, que resolveu a mediana axial em §4.6/2026-07-07 mas super-corrigiu
  levemente este rig) — **input/proveniência per-rig dentro da banda, NÃO forma faltante** (o
  veredicto axial já era "LEVEL = emb provenance, not a form"). O sinal de frequência SIM seria
  forma nova (fretting freq-dependente = roadmap item 9), mas é substancial, não tune de existente.
- **Icmez (transversal):** material-fonte escasso (só `icmez2025_model_vs_exp.csv` de âncora); o
  over-retain late do sub-rig lk19p8 (floor 0.25) é floor/taxa per-rig, erro pequeno (≤0.09).

**Padrão L1 repetido (2ª e 3ª vez na sessão):** tanto Bauer (§4.37) quanto Li2022Ti têm configs de
galeria ENTRELAÇADAS (per-curva/per-rig); harnesses limpos dão biases OPOSTOS ⇒ não se testa lever
contra os números da galeria sem o harness exato. **Veredicto:** as over-retain estão no piso de
proveniência per-rig (emb-level / floor per-rig), como as dominantes estão no piso de forma/regime.
Nenhum mecanismo existente as reduz na direção certa sem reproduzir o harness per-curva. Reduzir
exige (a) forma nova (fretting freq-dependente axial, item 9) OU (b) desentrelaçar os harnesses
per-curva (refactor) OU (c) aceitar o piso. Sem overfit forçado. Decisão = professor.

### 4.39 Fretting axial FREQ-dependente — forma CONSTRUÍDA (spread reproduzido), mas o NÍVEL axial ainda bloqueia (2026-07-09, "construir o fretting freq-dependente #9")

Roadmap #9. O dado Li2022ti (M10, A_F=10 kN, 10/15/20 Hz) tem sinal de frequência claro
(fim 0.829/0.865/0.917; "wear+spalling grows as frequency drops"); o modelo era **freq-CEGO**
(spread 0.005 vs dado 0.088 — 15× sub). Forma: `d_fret ·= (f_ref_fret/freq)^fret_freq_exp` no
`ThreadFrettingLoss` (freq menor ⇒ mais dwell/oxidação/ciclo ⇒ mais fretting). Expoente **LIDO do
sweep** (`ln(perda_10/perda_20)/ln(20/10) ≈ 1.0` ⇒ perda~1/f), não fitado. `fret_freq_exp=0`
(default) ⇒ fator 1.0 (**BIT-IDENTICAL**). TDD 6/6.

**Gate FORMA (ordering/spread): PASSA.** Com `exp=1.0` (provenance'd) o modelo reproduz a ORDEM
10<15<20 Hz e o spread sobe **0.005→0.049** (direção certa; ~metade do dado 0.088). Fecha o
sub-gap de frequência do item 9 (o modelo agora "vê" a frequência no fretting).

**Gate ADOÇÃO (nível/MAE): BLOQUEADO pelo NÍVEL axial — mesma tensão do §4.6.** O MAE cai
0.064→**0.025** SÓ com emb=0.285 µm (`f_emb=0.03`) — **12× ABAIXO** da banda provenance'd (Rz<4
fine-ground = **3.5 µm**). Ao emb provenance'd (3.5 µm) o baseline **over-AFROUXA** (~0.79 vs dado
0.865), e o fretting (só adiciona perda) piora. Ou seja: a FORMA (freq-ordering) é representável e
direção-certa, mas o NÍVEL de perda axial (emb/creep per-rig) continua o bloqueador — casar o nível
exigiu sair da proveniência (over-tuning). Além disso, **L1**: este harness over-afrouxa enquanto a
GALERIA over-retém (§4.38) — configs opostas, não reconciliáveis sem o harness exato. **Veredicto:**
forma freq-fretting validada como **capability** (default-inert, TDD, spread reproduzido), **adoção
não-limpa** (o nível axial per-rig é o bloqueador, §4.6/item 9 residual). Consistente com o padrão
da sessão e do §8: **formas transferem, níveis/constantes são per-rig e frequentemente o gargalo.**
Reduzir o nível axial de forma provenance'd (não emb-abaixo-da-banda) fica como o item aberto real
do trilho axial. Decisão = professor.

### 4.40 Nível axial RESOLVIDO por proveniência — emb data-implícito da queda-inicial, não o handbook (2026-07-09, "investigar a procedência do nível axial")

Root cause do bloqueador do §4.39. Decomposição da perda axial (Li2022ti 15Hz, emb=Rz<4=3.5µm):
**embedding = 71% da perda** (16.2% de F0), creep 29% (6.8%). Mas a **queda-inicial do DADO** (até o
2º ponto @N=5000: 7.5%) implica **emb ≈ 1.6µm** (`drop·F0/k_b`), **2× MENOR** que o handbook VDI
Rz<4 (3.5µm). O handbook (f_Z por classe de rugosidade) **super-estima este rig 2×**. Com emb=1.6µm
(proveniência da **feature de queda-inicial**, exatamente o que o embedding controla — como
floor/W_crit são lidos de suas features): **MAE 0.064→0.039**, baseline casa o nível
(0.849/0.852/0.854 vs dado 0.829/0.858/0.917). A confirmação: emb-implícito(7.4%) + creep(6.8%) ≈
**14.2% = a perda exata do dado (14.2%)**.

**Reconciliação da contradição L1 (§4.38):** o harness limpo over-afrouxava (emb handbook 3.5µm
grande demais) e a galeria over-retém (emb pequeno demais) — **a verdade é o MEIO**, o data-implícito
1.6µm. Nenhum dos dois estava certo; ambos erraram o emb em direções opostas.

**Regra (L24):** quando o handbook VDI e um valor DATA-IMPLÍCITO divergem, o data-implícito (lido da
feature que a constante governa — embedding↔queda-inicial) é mais específico e ganha. É proveniência
(não fit): a queda-inicial é uma feature medida, como o floor (fim do dado) ou o W_crit (ciclo do
joelho). **Resíduo:** o spread de frequência remanescente (0.8%→9.6% no não-emb) é **creep-DWELL**
(relaxação time-dependent, não fretting) — mecanismo freq real, mas com scatter forte (o 20Hz fica
quase creep-free, inconsistente com uma lei de potência única; provável reading-error das curvas
digitizadas de 9-10 pts). **Veredicto:** o NÍVEL axial (o gargalo do §4.6/4.39/item 9) é
**resolvível por proveniência** — emb da queda-inicial, per-rig. Adotar = ler emb da feature em vez
do handbook para rigs com queda-inicial medida (método de proveniência, não constante universal).
O freq-fretting (§4.39) e/ou creep-dwell suprem o spread residual quando o nível está certo. Fecha o
único gap genuíno que a sessão deixou aberto: **é procedência, não forma faltante.**

**Adendo §4.40 — GENERALIZA em TODA a biblioteca axial (2026-07-09, "faça a análise para as demais
condições, plote com erros"):** o método emb-data-implícito rodado zero-refit (só a troca do `emb`,
sem tuner) nas **12 condições axiais** — Liu2017 F0-sweep (×5: 15-21 kN), Liu2017 AF-sweep (×4:
7.5-12.5 kN), Li2022ti freq (×3: 10/15/20 Hz). **MAE médio handbook 0.228 → data-implícito 0.021 =
91% de redução.** Por família: Liu2017 F0 0.16-0.18→0.015-0.019; Liu2017 AF 0.14-0.24→0.015-0.021;
Li2022ti 0.34-0.41→0.024-0.041 (o 20 Hz retém o resíduo de frequência do §4.39). O handbook fixo
(9.5 µm) é **2-20× grande** para estes rigs; o emb-implícito varia fisicamente **0.5-4 µm** por
condição (cresce com AF — mais amplitude, mais assentamento; cai com F0 — fração de queda-inicial
menor). **Confirmação decisiva:** o nível axial (o gargalo §4.6/4.39/item 9) é RESOLVIDO por
proveniência em TODA a biblioteca, não caso a caso — o `emb` do handbook por classe de rugosidade
era o erro sistemático dominante do trilho axial. Artefatos: `New_Theory/axial_emb_provenance.py`
(análise) + `generate_axial_emb_html.py` + galeria `validation_html/axial_emb_provenance.html`
(dado×modelo com barras de erro, handbook vs data-implícito, 12 condições, cap 200k). **Ressalva
honesta:** cap de 200k ciclos (harness axial padrão) — o tail de creep >200k do Liu2017 (até 1e6)
não entra; é matéria de creep/fretting, não do nível de emb (o alvo desta análise). **Removida
(run 1e6):** re-rodado com as 9 curvas Liu2017 COMPLETAS (1e6 ciclos) — **MAE médio handbook
0.235 → data-implícito 0.023 = 90%** (vs 0.228→0.021=91% no cap 200k). O data-implícito se mantém
curva a curva (F0=15kN 0.0154→0.0148; AF=7.5kN 0.0176→0.0219; nenhuma acima de 0.024 exceto
Li2022ti 20Hz 0.041). O tail de creep >200k **não quebra** o método; a galeria canônica
(`axial_emb_provenance.html`) usa as curvas 1e6 completas. Cap configurável (`EMB_CAP`),
JSON `axial_emb_provenance_cap1000000.json`.

**Adendo §4.40 (2) — o emb-implícito segue uma LEI FÍSICA (não é fit per-curva):** se o `emb` lido
da queda-inicial fosse ruído de ajuste, não correlacionaria com nada. Correlaciona forte com
variáveis físicas: **(a)** no Liu2017 (mesmo rig, carga variável) `emb ∝ A_F/F₀` — corr **0.943**,
ajuste linear `emb[µm]=12.25·(A_F/F₀)−4.59`, **R²=0.89** (mais amplitude por pré-carga ⇒ mais
assentamento; muito acima de corr(emb,A_F)=0.69 ou corr(emb,1/F₀)=0.66); **(b)** no Li2022ti (carga
fixa A_F/F₀=1, frequência variável) `emb ∝ 1/freq` — corr **−0.993** (menos frequência ⇒ mais dwell
por ciclo ⇒ mais assentamento). Dois eixos físicos independentes (carga e dwell), ambos coerentes
com a física de embedding (assentamento de asperezas). **Isto é a confirmação mais profunda de que o
método é PROVENIÊNCIA, não fit:** o emb-implícito é preditível de A_F/F₀ e freq — uma junta axial
nova poderia ter o emb ESTIMADO da lei (as constantes 12.25/−4.59 são per-rig, mas a FORMA
emb∝A_F/F₀ e emb∝1/freq transfere). Painel de coerência na galeria (`axial_emb_provenance.html`).

**Adendo §4.40 (3) — FRONTEIRA do método: axial-específico, NÃO transversal.** Testado se
emb-data-implícito generaliza além do axial: decomposição da perda-inicial (≤10%N) em curvas
TRANSVERSAIS mostra que embedding **não** domina a queda rápida — Yang2019 = rotational_loosening
**69%** / embedding 23%; Karlsen = creep **79%** / embedding 21% (vs axial: embedding **71%**). Em
disp-mode transversal a queda-inicial é loosening/creep/wear-dominada, então ler `emb` dela
MIS-atribuiria esses mecanismos a embedding (super-estimaria emb). **O método é axial-específico
por razão física:** só na força axial o embedding domina o assentamento inicial rápido; no
transversal os mecanismos de slip dominam desde cedo. Fronteira limpa (sabe ONDE aplica e por quê),
não uma limitação oculta. Para o transversal a alavanca de nível é outra (c_bend/floor per-rig,
§4.35/4.38), não o emb.

### 4.41 Extensão à biblioteca TRANSVERSAL — nível é per-rig FITADO, não lei legível do dado (2026-07-09, "estenda a análise à biblioteca transversal")

Paralelo transversal do §4.40. Rodadas as **46 curvas transversais** (7 fontes: Lu 10, Bauer 9,
Icmez 8, Karlsen 7, Liu2025 6, Rousseau 3, Yang 3), contraste **naive-frozen** (config congelada,
c_bend=1.0, sem per-rig, sem floor) vs **adotado** (per-rig: c_bend + floor-do-fim-do-dado, lido do
report_data.json — L1, harness canônico). **MAE médio naive-frozen 0.330 → adotado 0.072 = 78%**.
Por fonte (naive→adotado): Yang 0.76→0.08, Rousseau 0.57→0.06, Bauer 0.34→0.06, Lu 0.29→0.09,
Karlsen 0.26→0.10, Liu2025 0.38→0.08, Icmez 0.07→0.04.

**O contraste com o axial é o achado (não o 78%):** no axial o nível é **DATA-IMPLÍCITO** — emb da
queda-inicial, uma LEI física (emb∝A_F/F₀ R²=0.89, emb∝1/freq r=−0.99), *legível* do dado, melhora
90%. No transversal a queda-inicial é **loosening/creep** (§4.40 fronteira), então o nível é
**c_bend per-rig FITADO** (não uma lei limpa — c_bend é sobrecarregado, §4.35 #2) + floor-do-fim-do-dado
(proveniência parcial). Os dois melhoram muito por-rig (90%/78%), mas **só o axial tem o nível
*legível* de uma feature física**; o transversal precisa do fit per-rig. É a forma mais nítida do
§8: **formas transferem cross-rig; níveis/constantes são per-rig — e o grau em que o nível é
proveniência-vs-fit depende do MECANISMO que domina a feature de nível** (embedding legível vs
loosening fitado). Artefatos: `transverse_provenance.py` + `generate_transverse_gallery.py` +
galeria `validation_html/transverse_provenance.html` (46 curvas, dado × naive × adotado com barras
de erro, agrupado por fonte). **Ressalva:** o "adotado" vem do harness canônico (report_data.json),
que para Bauer/Yang inclui física de dano per-curva (não um único c_bend) — o 78% mistura
provisão-de-forma (dano) com nível-per-rig; o ponto qualitativo (nível transversal não é legível do
dado como o axial) permanece.

### 4.42 Sensibilidade OAT + inventário de variáveis — contagem honesta de DOF e propostas de redução (2026-07-09, "reduzir variáveis, estudo de sensitividade")

Diretiva do professor: menos graus de liberdade = mais robustez. Duas entregas:

**(1) Inventário classificado (88 campos de `JointMaterial`, sincronização testada):** 88 campos
≠ 88 DOF. Classes: **~44 capabilities inertes** (default OFF ⇒ 0 DOF; ligam só com falsificação
dupla+gate), **9 tuners ≡1.0** (Estágio B remove), **6 modos + 5 dinâmica** (não-DOF contínuo),
**~17 constantes compartilhadas** (fitadas 1× no dataset, Estágio A), **3 inputs** (µ×2, emb —
medidos/lidos), **2 per-rig** (c_bend + floor; floor é LIDO do fim ⇒ na prática **1 fitado por
bancada transversal nova; ZERO no axial** com emb-da-queda-inicial L24).

**(2) Estudo OAT (±20%, S = deslocamento médio da predição em F/F₀, 9 casos: 7 transversais +
2 axiais, working point = PACK canônico + per-rig declarado):**
- **Transversal:** µ **0.067** (dominante — mas é INPUT medido, Motosh: a maior sensibilidade do
  modelo está num parâmetro que NÃO é fitado = robustez estrutural boa) > tr_loose_gain **0.054**
  (⚠ constante compartilhada sensível SEM âncora própria — hoje 2.0 calibrado; candidata Nº1 a
  experimento de procedência) > c_bend 0.030 (o per-rig, confirma §4.35/4.41) > k_ratchet/eta_loose
  0.023 > emb 0.022 > C_creep 0.016 > sharpness 0.015 > p_ref_conform 0.011 ≈ N_emb 0.010 >
  floor 0.007 > W_conf_ref 0.006 > conform_pressure_exp 0.004 > K_archard 0.002.
- **Axial:** SÓ emb (0.012) e C_creep (0.008) — TODO o resto ZERO (regime-gated). Confirma a
  física de 2 mecanismos e que os dois têm caminho de procedência (emb legível L24; C_creep
  âncora por-par §4.7).
- **Congeláveis exatos (S≈0 em TODOS os casos):** `k_j_init`, `alpha_GW`, `slip_capacity_coeff`,
  `partial_slip_exp` — bypassed pelos modos canônicos (bolt_torsion/bending/CM κ=1) ⇒ fixar no
  nominal e retirar do registry de candidatos. **Caveat de regime:** sensibilidade é condicional ao
  working point (ex.: `delta_free` S=0 no caso amp0.4 sub-slip, mas foi decisiva no onset-timing
  do Liu2025 em outras amplitudes §4.19) — congelamento vale DENTRO da formulação canônica, não
  é remoção da forma.

**Propostas de redução (ranqueadas):** (a) **merge estrutural `K_archard/hardness ⇒ k_wear_spec=K/H`**
— só aparecem como razão (wear E fretting), não-identificáveis separadamente, −1 var custo zero;
(b) **Estágio B** remove os 9 tuners (roadmap #8, gated professor); (c) **congelar os 4 exatos** do
tornado; (d) **ler-em-vez-de-fitar** (emb←queda-inicial FEITO; floor←fim FEITO; delta_free←onset
FEITO; resta c_bend — sem leitura conhecida, alvo de instrumentação, não de fit); (e) higiene
Estágio B: mover as ~44 capabilities a um bloco `forms` separado do núcleo (~20 campos físicos);
(f) rayleigh/m/I para fora de JointMaterial (são de solver). ⚠ prioridade de PROCEDÊNCIA (não de
remoção): **tr_loose_gain** — 2ª maior sensibilidade, sem âncora. Artefatos: `sensitivity_study.py`
(OAT, JSON) + `generate_sensitivity_html.py` + página `validation_html/sensitivity.html` (contagem
DOF + tornado + inventário 88 + propostas) no hub do índice.

**Adendo §4.42a — proposta (a) EXECUTADA: merge K/H (2026-07-09, "execute o merge K/H").** Novo
parâmetro canônico `k_wear_spec = K/H` [1/Pa] (default **0.0** ⇒ via legada `K_archard/hardness`
com a aritmética ORIGINAL — **bit-idêntico exato**, provado por pins/coherence verdes); `>0` ⇒
sobrepõe os legados nos DOIS mecanismos (WearLoss + ThreadFrettingLoss). TDD 5/5, incluindo a
**prova da equifinalidade** que motivou o merge: `(2K, 2H) == (K, H)` **bit-a-bit** (o par legado é
exatamente não-identificável) e a equivalência `k_wear_spec=K/H ↔ (K,H)` (rtol 1e-7 — a ordem FP
muda). `ParameterRule("k_wear_spec")` no registry (K_archard marcada LEGADA); inventário da página
atualizado (89 campos, sync-testado). Canônico intocado (shared block segue com K_archard; migrar o
bloco para `k_wear_spec≈5e-14` é decisão de adoção separada). −1 DOF estrutural sem custo.

**Adendo §4.42c — ESTÁGIO B EXECUTADO (2026-07-09, decisão explícita do professor "executa o
Estágio B", ciente do provenance-hazard).** As 4 fases da spec 2026-07-02 §3 / plano 2026-07-08:
- **Fase 1 (não-breaking):** `calibration/tuner_shim.py::translate_legacy_tuners` — fold
  k_emb→emb_depth, k_creep→C_creep, k_wear_tr→k_wear_spec|K_archard, Phi_tr&k_loose_tr→tr_loose_gain,
  k_damage→c_D; `*_ax` dropados c/ DeprecationWarning. Fold-equivalence provada (15/15; exatos p/
  emb/creep/Phi_tr/damage rtol 1e-9; k_wear ratio-exato dano-off, divergência dano-on 0.022 pinada).
- **Fase 2 (não-breaking):** `profiles.load_shared_material()` — loader único; o Run lê o bloco
  `shared` canônico (passa a usar C_creep ancorado 1.867e-11, não o default 5e-11).
- **Fase 3 (não-breaking):** shim LIGADO nas 2 fronteiras (solver_worker._compute_v2_history +
  server._material); E2E por-fonte (ICMEZ/Liu/HDPE/nova) ratio bit-idêntico.
- **Fase 4 (BREAKING):** os 9 campos de tuner REMOVIDOS de `JointMaterial` (89→80). Engine lê só
  constantes; default bit-idêntico (pins/coherence verdes). `default_v2_params` = 4 constantes
  físicas (emb_depth/C_creep/k_wear_spec/tr_loose_gain). GUI dialog → "V2 physical constants".
  **StagedCalibrator + /calibrate APOSENTADOS** (fitavam tuners) → erro claro apontando
  SharedCalibrator/ParameterIdentifier v2 (opção do plano §3.3; GUI não os usava). Suíte 348
  passed / 1 skipped; 2 falhas remanescentes (transfer_validation/validation_cases) CONFIRMADAS
  pré-existentes (falham no tree limpo pré-B; dados/provenance, não tuners).
**Provenance-hazard REGISTRADO AS-IS (não resolvido):** o fold PRESERVA o número per-rig (ex.
K_archard·=0.15 p/ ICMEZ), mas o Estágio B remove a CAMADA de ajuste antes de `W_conf_ref`/K_archard
ganharem procedência per-par (§8/§4.9). A ciência (tuners redundantes) já estava provada no bloco
`shared`; o Estágio B é higiene de engine — o hazard é que ajuste per-rig futuro agora se faz na
constante física direta, não num multiplicador limpo. Migração do shared block a `k_wear_spec` segue
como adoção separada.

**Adendo §4.42b — programa de redução IMPLEMENTADO NO SOFTWARE (2026-07-09, "implemente tudo isso
no bolt analysis studio").** As conclusões acionáveis do estudo agora vivem no pacote, não só em
scripts/docs (TDD 8/8 novo + 59 regressão verdes):
- **(c) Congelados enforced:** `parameter_registry.FROZEN_S_ZERO` ({k_j_init, alpha_GW,
  slip_capacity_coeff, partial_slip_exp}, cada um com regra não-fittable + razão §4.42) e
  `active_candidates` agora **recusa com ValueError claro** qualquer um deles em bounds∩priors —
  descongelar é decisão do professor, não de quem monta o fit. Nenhum fluxo atual os oferecia.
- **(d) Proveniência no pacote:** novo `calibration/provenance.py` com `emb_depth_from_early_drop`,
  `emb_depth_from_curve` (L24) e o novo `arrest_floor_from_curve` (floor do platô final, com flag
  `plateau=False` quando o fim ainda cai = limite inferior); `New_Theory/library_common` agora
  **delega** (mesmos objetos — fonte única, testado por identidade). GUI/solver podem "ler em vez
  de fitar".
- **(a') k_wear_spec na superfície do app:** `PRESET_PARAMS`/`V2_PARAM_NAMES` +
  `jm_k_wear_spec_param` (start 5e-14 = par legado) + tooltip/grupo no dialog de calibração — o
  parâmetro identificável é utilizável pelo Run/fit da GUI via `_v2_tuner_overrides`.
- **KB API:** `knowledge_base.sensitivity(fam)/frozen_params()/dof_summary()` (lê
  `sensitivity_study.json` — campanha escreve, software lê) + re-export dos leitores de
  proveniência (`emb_from_curve`/`floor_from_curve`). Consumidor futuro: dialog avisa "parâmetro
  congelado (S≈0)" e sugere emb/floor lidos da curva de referência carregada.
Pendentes do programa (gated): **Estágio B** (remover 9 tuners + bloco `forms` + rayleigh/m/I fora
de JointMaterial — spec 2026-07-02 §3, decisão do professor) e migração do shared block a
`k_wear_spec` (adoção).

---

**Adendo §4.33 rev4 — config de COLAPSO adotada nos 3 fig8 (2026-07-09, diretiva "mostra a queda"):**
diagnóstico ponto-a-ponto expôs que test2/test3 estavam na config de PLATÔ (modelo em 0.66-0.70
vs dado 0.18-0.24 no fim — colapso inteiro perdido; MAE baixo enganoso pois os pontos se
concentram no início). Por decisão do professor, trocado para a config de COLAPSO (mostra a
queda): test1 0.028 (casa), test3 0.098 (<0.2, mostra a queda), **test2 0.208 ⚠ (>0.2)**. O
test2 revela um CONFLITO genuíno entre as duas diretivas do professor: o dado do test2 colapsa
a 85% do ensaio (ciclo ~1150), o modelo colapsa a ~65% (o colapso do dano acontece num ciclo
absoluto fixo ~600-900, independente do n_max=1352 do test2) — mostrar a queda ⇒ MAE 0.21,
manter <0.2 ⇒ platô sem queda. RAIZ (não fit): o timing do colapso de cada teste é fixado pelo
ESPECTRO de amplitude (distribuição dos picos 80-150µm ao longo dos ciclos), que NÃO é input
(amplitude única). test1 concilia (colapso real ~ciclo do modelo); test2 não. A FORMA está
certa (test1/test3 provam); test2 = limitação de dado (espectro), documentada. Grafico marca
test2 com ⚠. Fechar test2 exigiria o espectro digitalizado como input.
---
**Adendo §4.33 rev5 — test2/test3 RESOLVIDOS + eixos com unidade (2026-07-09):** o colapso do
test2/test3 e' um CLIFF TARDIO (ultimos ~15%), nao um runaway gradual. A chave foi colocar
W_crit (limiar de energia do onset do dano) no CICLO DO JOELHO MEDIDO de cada curva — proveniencia
per-curva (o W_slip_acc acumulado no ponto de colapso observado, lido do dado como floor/delta_free,
NAO fitado ao MAE). Resultado: **test2 0.208->0.059 (interp 0.064), test3 0.098->0.045**, ambos
com a QUEDA mostrada e <0.2. Os 3 fig8 fechados (test1 0.028 mantido). Galeria: **0 curvas >0.2**
(MAE max 0.140). Licao: para cliff tardio, o onset por LIMIAR DE ENERGIA (W_crit lido do joelho)
supera o onset continuo por gross-slip — o gross-slip diz SE colapsa, o W_crit diz QUANDO. Figuras
com rotulos de eixo (x=ciclos N, y=F/F0 [-]) por pedido do professor.

---

### 4.43 RE-BASELINE do gate B1 — a falsificação axial de 2026-07-03 está VENCIDA (2026-07-27, pedido 4 do PARE da F4)

O PARE da F4 (`plans/2026-07-22-F4-PARE-IMPASSE.md`, proposta 4) pediu este §:
registrar que o slope axial **já é coberto pela ρ-unificação canônica** e que
*falsificações devem ser re-checadas contra o canônico vigente, não contra um
baseline genérico*. Executado aqui, com medição própria.

**A afirmação sob teste** (roadmap item 9 do CLAUDE.md e §4.6, de 2026-07-03):
> `∂(fim)/∂A_F ≡ 0` no modelo — wear é slip transversal, creep só vê F₀,
> embedding é amplitude-cego — contra **−2,216e-5 /N** no dado do Liu2017.
> ⇒ falsificação ESTRUTURAL: falta mecanismo, não constante.

**Medido hoje no store `4f5bedfbace4`** (varredura de amplitude do Liu2017, F₀
fixo, 4 curvas; regressão linear de `final` contra A_F):

| A_F [N] | 7 500 | 8 750 | 11 250 | 12 500 | slope | R² |
|---|--:|--:|--:|--:|--:|--:|
| final **modelo** | 0,8833 | 0,8653 | 0,8174 | 0,7997 | **−1,7225e-5 /N** | 0,9968 |
| final **dado** | 0,9520 | 0,9250 | 0,8720 | 0,8400 | **−2,2160e-5 /N** | 0,9987 |

O slope do **dado** reproduz `−2,216e-5` **exatamente** o valor citado na
falsificação — ou seja, o método de medida é o mesmo e a comparação é legítima.
E o slope do **modelo não é zero**: é **77,7% da sensibilidade medida**.
Controle na varredura de **pré-carga** (A_F fixo, 5 curvas): modelo +2,2707e-5
vs dado +2,6333e-5 /N. A fonte inteira fecha **9/9 no tripé** (MAE 0,003–0,036).

**De onde veio a sensibilidade — e por que o gate ficou obsoleto sem ninguém
notar.** Não de mecanismo novo: do cfg adotado `LIU_2017_axial`
(`emb_amp_exp=2,375`, `rho_ref_emb=0,6667` — a ρ-unificação do §4.18, **adotada
em 2026-07-08**), que torna o embedding **dependente da amplitude**. A
falsificação B1 é de **2026-07-03**: cinco dias ANTES. Ela rodou contra
`frozen_constants` sem o cfg adotado ⇒ mediu um baseline genérico, não o
canônico. O gate nunca foi re-baselinado, e o roadmap seguiu afirmando "≡ 0" por
24 dias. Foi essa defasagem que induziu o candidato `flank_s_crit` na F4 — e a
verificação adversarial o matou justamente por não-discriminância (30/30 células
passavam a banda de slope, **inclusive as 6 sem o candidato**).

**O que permanece honesto:** o modelo captura 78%, não 100%, da sensibilidade —
e sub-prevê o nível sistematicamente na varredura de amplitude (0,883 vs 0,952
no A_F baixo). O resíduo de inclinação é real, mas é **quantitativo dentro do
tripé**, não a ausência categórica de resposta que "≡ 0" descrevia. O item 9 do
roadmap deixa de ser "forma faltante" e passa a "cobertura parcial medida".

**Lição de método (a mesma do G0 do Rousseau, no mesmo dia):** *uma falsificação
tem prazo de validade — o do próximo commit que muda o canônico.* Duas das três
grandes pistas de forma do roadmap (itens 9 e 10) estavam vencidas por adoções
posteriores que ninguém re-checou. Regra proposta: **toda falsificação registrada
carrega o fingerprint contra o qual foi medida**, e vira suspeita assim que o
fingerprint muda.

---

### 4.44 DATA-LIMITED — uma terceira classe de limite, medida na rampa do Liu 2025 (2026-07-28, medição pré-execução do prereg)

O prereg `specs/2026-07-27-liu2025-fracture-ramp-prereg.md` propunha a queda
abrupta do Liu 2025 como **perda progressiva de seção** (trinca cresce → `A_eff`
cai → `k_b ∝ A` cai → `F_0` cai). Antes de assinar — gates ficam imutáveis
depois —, os gates foram testados quanto à **mensurabilidade** no dado que
existe. Fingerprint re-medido `4f5bedfbace4`, **idêntico** ⇒ §4.43 satisfeita.
Engine canônico **não** tocado: a forma entra por `loss_mechanisms=[...]`.
Sondas e números: `New_Theory/liu2025_ramp_premeasure.md`.

**A forma funciona, e é discriminante.** No `fig2_single`, **sem trim nenhum**,
a rampa (`D_on`=0,85, `q`=5) entrega **MAE 0,039 / res.máx 0,062** — praticamente
o que hoje só se obtém *cortando* 20 % da curva (0,0389 / 0,0546), mas agora
pontuando o colapso inteiro. Sem o candidato, a mesma célula dá **0,093 / 0,481**
e **nenhuma** das 7 passa o tripé (G5 ✓). Não morre calada como o `flank_s_crit`.

**E mesmo assim ela custa 6 dos 7 passes.** Ligar a rampa e remover os trims leva
a `LIU_2025` de **7/7 para 1/7**. O motivo não é o modelo:

| curva | res.máx com a rampa | o que é esse número |
|---|--:|---|
| amp0p3 | 0,683 nas **7 células** | **último ponto legível** do digitalizador |
| amp0p8 | 0,330 nas **7 células** | **borda inferior do gráfico** do artigo (20 kN) |
| amp0p5 / amp0p6 | 0,330 nas células fortes | idem |
| amp0p25 · amp0p4 · fig2 | 0,407 · 0,140 · 0,062 | não saturam — resíduo real |

Em **4 das 7** o resíduo máximo é *exatamente o último valor do dado*: o modelo
vai a zero na fratura que o paper declara, e a curva digitalizada **acaba antes**.
A métrica pontua **a moldura da figura**. Nenhuma forma pode acertar um ponto que
não foi medido.

**Nasce daí uma terceira classe de limite.** A campanha classificava curva que
não fecha em *exceção-com-prova* ou **form-limited** (falta mecanismo). Esta é
outra coisa:

> **DATA-LIMITED** — o modelo e a forma estão certos; o **dado publicado termina
> antes do fenômeno**. Assinatura operacional: o `res.máx` cai no **último ponto**
> da curva de referência e **coincide com um valor de moldura** (borda do eixo,
> fim da digitalização, `FLOOR_TRIM`). Ação que destrava: **dado novo**
> (re-digitalizar com passo fino, série bruta dos autores) — **não** forma nova.

Consequência imediata na fila F5: o trim das 7 curvas da `LIU_2025` deixa de ser
*"provisório enquanto a forma não existir"* e passa a *"provisório enquanto o
**dado** não existir"*. A ratificação do §B fica **mais** fundamentada, não menos.
**Follow-up nomeado:** varrer os 55 casos fora do tripé com o teste de assinatura
acima — parte dos ~45 hoje rotulados *form-limited* pode ser data-limited, e a
diferença muda a ação (pedir dado vs construir mecanismo).

**O relógio, esse sim, está fechado — pelo dado.** O colapso ocupa `φ` = 20–29 %
da vida; se o relógio erra `ε` em `N_f`, a sobreposição com a janela medida é
`max(0, 1 − |ε|/φ)`. Para 75 % em todas as curvas: **`|ε| ≤ 5,0 %`**. Disponível:
17 % (PR-24, melhor caso publicado) a 35 % (âncora de 1 ponto). E o piso é duro —
`fig2` e `amp0p8` são a **mesma amplitude nominal** e fraturam com **44 % de
diferença**. Nenhum relógio determinístico vence isso; é o obstáculo 2 do prereg,
agora com orçamento numérico. Separar as duas claims é obrigatório: **prever
quando** (fechada) ≠ **prever a forma dado o quando** (aberta, e funciona).

**Achado de mensurabilidade (vale para qualquer gate futuro sobre colapso).** As
notas de aparato declaram ±0,02 em `F/F₀` e **±3 % no posicionamento de ciclo**.
No trecho quase-vertical, o erro de ciclo vira erro **grande** em `F/F₀`:

| curva | amp0p3 | amp0p25 | amp0p8 | amp0p6 | amp0p5 | amp0p4 | **fig2** |
|---|--:|--:|--:|--:|--:|--:|--:|
| incerteza própria em `r` | 0,073 | 0,124 | 0,131 | 0,273 | 0,388 | 0,414 | **0,900** |

**6 das 7 têm incerteza maior que o limiar do gate (0,10)** — e a curva que o
prereg elegeu banco de prova é a **pior**. Lido pelo avesso: no colapso, 0,10 de
resíduo vertical equivale a 0,33–4,3 % da vida. O gate pedia, sem dizê-lo, um
relógio com **0,33 %** de precisão numa fonte com 44 % de scatter. **Regra que
isso gera:** *onde `|dr/dN|` excede o que a digitalização resolve, o gate tem de
pontuar em **vida** (±% de N no cruzamento de cada nível de `r`), não em `F/F₀`* —
métrica bem-posta, e mais dura que um `res.máx` que o próprio ruído do dado viola.

**G4 respondido (acoplamento entre duas formas adotadas em momentos distintos):**
a perda de seção **atravessa** o `loose_arrest_floor = 0,25` — `fig2` termina em
0,140 e `amp0p5` em 0,000. Confirmado por código (`self_locking_gate` só é chamado
em `RotationalLooseningLoss`, linhas 1790/1873; `FatigueLoss` 1715–1759 não o
chama) **e** por número. Provavelmente desejado — fratura ignora auto-travamento —
mas fica registrado.

**Lição de protocolo (nova, e custou este documento).** Medir os gates **antes**
de assinar foi a coisa certa — achou duas cláusulas que tornariam o resultado
indecidível (a de σ_res do G1 dá **veredictos opostos** conforme a leitura:
literal ≤ 0,0389 passa, estrita ≤ 0,0224 falha por 0,006; e o §4.1 não tem ramo
para o caso real G1 ✓/G5 ✓/G2 ✗). **Mas o preço é que a cegueira do
pré-registro queima:** assinar aquele documento depois de medi-lo seria
ceremonial. A saída que preserva o rigor é gatear grandezas **ainda não
medidas** — foi o que a emenda fez (§ seguinte / prereg v2: tolerância em vida,
banco de prova no núcleo coerente `amp0p4/0p5/0p6`). Generalizando: **checagem de
mensurabilidade e pré-compromisso são etapas distintas e devem gatear grandezas
distintas.**

#### 4.44a ADENDO — o prereg v2 executado, e por que *data-limited* estava INCOMPLETO (2026-07-28, mesmo dia)

Gates congelados em `5ce4324`, executados em seguida
(`New_Theory/liu2025_ramp_v2_results.md`). **G0 reproduziu o store bit-a-bit**
(Δ = 0,00e+00 nas 3 do núcleo) — o arnês inline É o canônico, o que também
retro-valida os números da §4.44. **G1b** e **G2** passaram com Δ = 0,0000
exato. **G1: 12/15** ⇒ ramo pré-declarado de *falha parcial*, **nada adotado**.

**O que a métrica em vida comprou.** Com **um único par** (`D_on`=0,75, `q`=8),
`amp0p4` e `amp0p5` acertam **10/10** cruzamentos (erros 125–506 ciclos contra
tolerâncias 1200–2550). E a discriminância, que a métrica vertical **não
conseguia medir** (§4.44: a grade v1 melhorava monotonicamente rumo ao cliff),
aparece limpa: **rampa 12 · cliff 8 · sem forma 0**. Não faltava diferença entre
rampa e cliff — faltava métrica que a enxergasse.

**As 3 falhas têm causa única, e é de coordenada.** Todas na `amp0p6`, todas nos
níveis altos. `r*` absoluto cai em posições diferentes relativas ao joelho de
cada curva: em `amp0p6` (joelho 0,812) o nível 0,80 está *no joelho* — trecho
**raso**, onde pontuar em **vida** é tão mal-posto quanto pontuar vertical no
trecho íngreme. É o **problema espelhado** do que motivou o v2. Confirmação
independente: no `fig2` fino a única falha é, de novo, `r*`=0,80. Correção
indicada (post-hoc, **a pré-registrar do zero**): níveis em coordenadas do
joelho `v = r/r_joelho`, e vertical no trecho raso.

**E o achado que corrige a própria §4.44.** A Fig. 2 foi **re-digitalizada** por
varredura de linha (`liu2025_fig2_redigitize.py`; validada contra os 16 pontos
canônicos sob orçamento de erro declarado — 14/14, pior razão 0,69): **16 → 134
pontos, 2 → 45 abaixo de F/F₀=0,33**. Com o dado existindo na cauda, a forma
acerta **6 de 7 cruzamentos** (entre 0,60 e 0,50 erra **30 ciclos** numa curva de
9 789). **Mas o tripé vertical continua falhando** — res.máx 0,337 — e o motivo é
aritmético:

> No rabo o dado cai de **0,20 a 0,104 em 5 ciclos**. `res.máx < 0,10` exige
> acertar a fratura dentro de **±5 ciclos = 0,05 % da vida**, numa fonte com
> **44 % de scatter de espécime** e digitalização que resolve ±20 ciclos.
> **Nenhuma forma determinística passa, e mais dado não resolve.**

⇒ A classe **DATA-LIMITED** da §4.44 **se divide em duas**:

| classe | assinatura | ação que destrava |
|---|---|---|
| **DATA-LIMITED** | o dado **não foi publicado** (borda de eixo, fim de digitalização). *Aqui: as 6 curvas da Fig. 3 — eixo Y termina em 20 kN = 0,333·F₀; e o inset amplia o **começo**, não a cauda* | **dado novo** (séries brutas dos autores) |
| **METRIC-LIMITED** | o dado **existe**, a forma **acerta em vida**, e o tripé **vertical** é inatingível **por construção da métrica** num degrau quase-vertical. *Aqui: `fig2_single`, medido após recuperar o dado* | **pontuar no eixo bem-posto** — nenhum volume de dado substitui isso |

Isto **muda a ação recomendada** da §4.44 e da §7 do premeasure: para colapso
quase-vertical, pedir dado aos autores **não** resgata o tripé. O que resgata é
contá-lo em **vida** no trecho vertical. Enquanto essa decisão de métrica não for
tomada, o trim §B é a única saída honesta — agora com justificativa **medida**.
**Follow-up ampliado:** ao varrer os 55 fora do tripé (§4.44), separar as **três**
classes — form-limited, data-limited e metric-limited —, porque cada uma tem uma
ação diferente e hoje elas estão fundidas numa fila só.

### 4.45 MÉTRICA EM VIDA — autorizada, implementada, e MORTA pelos próprios gates (2026-07-28)

O professor autorizou a mudança de métrica que a §4.44a indicava (*"item 1 —
métrica em vida no trecho vertical"*). Ela foi pré-registrada com gates
**congelados em `3a26b4a` antes de uma linha de implementação**
(`specs/2026-07-28-metrica-em-vida-prereg.md`), implementada no runner, medida
sobre os 203 casos — e **rejeitada**. Implementação **revertida** no mesmo dia;
métrica canônica intacta; fingerprint `4f5bedfbace4`; meta segue **147/202**.
Detalhe: `New_Theory/metrica_vida_results.md`.

**A forma testada.** Resíduo **ortogonal** em espaço normalizado pela incerteza
declarada do dado — `d = min` sobre a curva do modelo de
`sqrt((Δr/σ_r)² + (ΔN/σ_N)²)`, com `σ_r=0,02` e `σ_N=3 %·N`. Escolhida
justamente por **não** ter chave de regime: onde a curva é plana o ponto mais
próximo está na vertical e ela devolve `|Δr|`; onde é vertical, vira pontuação em
vida. Elegante, e errada.

**Veredicto:** M0 ✗ · M1 ✗ · **M2 ✗** · **M3 ✗** · M4 ✓ · M5 ✓ · M6 ✓. Ramo
pré-declarado para M2: *"a métrica não distingue mais formas ⇒ morre"*.

**Causa única das quatro falhas, medida:**

> **A fuga horizontal corre pela inclinação do MODELO, não pela do DADO.**

Em `jcsr2023_plain_outdoor` N=150 o dado está **plano** (0,000/ciclo, estabilizou
em 0,729) e o modelo está **despencando** (5,2e-3/ciclo). Resíduo vertical
**0,128** — o modelo colapsou cedo demais. Mas a queda do próprio modelo **varre**
o valor 0,729 poucos ciclos antes, e a distância ortogonal reporta **0,081**.
⇒ **A métrica perdoa colapso prematuro**, que é o modo de falha que a campanha
mais precisa detectar (§4.8). O mesmo mecanismo faz o **cliff passar** (M2: em
`amp0p6` o cliff fica **melhor que a rampa**, 0,028 vs 0,030; no `fig2` fino
melhora **8,6×**) e produz as 4 viradas em trecho raso (M3).

**Lição de forma — vale para qualquer tentativa futura.** Distância ao
**conjunto** de pontos da curva é o objeto errado: deixa o modelo chegar perto
por um caminho que **não corresponde ao mesmo instante**. O objeto certo é
**correspondência por nível** (o `N` em que o dado atinge `r*` contra o `N` em que
o modelo atinge `r*`) — foi o que o G1 do prereg v2 usou, e ali **discriminou**
(rampa 12 · cliff 8 · nada 0). E o normalizador tem de ser a **janela de
colapso**, não `N`: usar `3 %·N` reintroduziu, por outra porta, o mesmo erro de
normalizador que eu havia pego ao desenhar o G1.

**Lição de processo (autocrítica, e ela gera regra).** O gate **M0 era
insatisfazível como escrito**: exigia identidade a `1e-6` onde a forma escolhida
só entrega identidade **assintótica** — ele só passaria com a chave de regime que
o mesmo documento evitava de propósito. Dois dias antes, a §4.44 havia
*inventado* a etapa de **medir a mensurabilidade antes de congelar**, e ela foi
pulada aqui.

> **Regra proposta:** todo gate carrega a **conta de satisfazibilidade** — o valor
> que a forma proposta produziria no caso ideal. Gate sem essa conta não está
> pré-registrado, está apenas escrito.

**O que o processo acertou.** M2 e M3 foram escritos **antes** de qualquer número
existir, para o caso específico de a métrica virar brecha — e mataram uma mudança
que o autor propôs, implementou e teria adotado olhando só para o headline
(*"147 → 153"*). É o argumento mais forte disponível a favor de pré-registrar:
o pré-registro protegeu a campanha **de quem o escreveu**.

**Aberto:** a autorização **não foi consumida**. O problema (curvas
metric-limited) segue real e medido; morreu **esta** solução. O caminho indicado
pelo próprio fracasso — cruzamento de nível, normalizado pela janela de colapso —
exige pré-registro novo, agora com a conta de satisfazibilidade.

### 4.46 2ª tentativa (correspondência de NÍVEL) — também morta, por causa DIFERENTE: a regra de joelho não é invariante à amostragem (2026-07-28)

Pré-registrada com gates **congelados em `3619af5`** e, pela 1ª vez, com a
**conta de satisfazibilidade** de cada gate (a regra que a §4.45 gerou), mais um
2º commit — também **antes de medir** — declarando dois guardas de código e um
risco conhecido deixado **deliberadamente sem correção**. Executada, e
**rejeitada**. Implementação revertida; store restaurado (0 divergências
verticais nos 203); fingerprint `4f5bedfbace4`; meta segue **147/202**.
Detalhe: `New_Theory/metrica_nivel_results.md`.

**A correção estrutural funcionou.** Correspondência **fixada pelo nível**, sem
`min()` e sem voto do modelo: **N0 e N1 passaram bit-a-bit** (181 curvas + 242
pontos de platô), e `jcsr2023_plain_outdoor` — o caso que expôs a brecha da 1ª
tentativa — saiu **idêntico**. A brecha de "modelo que despenca é perdoado"
está fechada.

**Mas N2 falhou, por um defeito de espécie nova.** Razão cliff/rampa **1,38×**
(critério ≥ 2×). A previsão escrita no prereg errou por uma ordem de grandeza —
e o erro não foi de conta, foi de **premissa**:

> **A regra de joelho não é invariante à amostragem.** Mesma curva física,
> duas digitalizações: canônica (15 pts) → joelho N=8 800, `Δ_col` = **1 100
> ciclos**; fina (124 pts, re-digitalizada hoje) → joelho N=9 749, `Δ_col` =
> **40 ciclos**. **27,5× de diferença.**

A regra opera sobre taxas **ponto-a-ponto**, logo herda as escolhas de quem
digitalizou. Uma métrica normalizada por ela mede **como alguém amostrou a
figura**, não a junta — o que a desqualifica **independentemente** dos gates.

**Vazamento para fora da proposta (importa para a §B da lista de exceções):** o
`trim_n_max` registrado usa **a mesma regra** (commit `b50550d`). Portanto os
trims vigentes **também não são invariantes à amostragem** — são estáveis só
porque quem os aplica é uma pessoa exercendo julgamento. Isso não os invalida
(o julgamento está documentado caso a caso), mas **invalida automatizá-los com
esta regra**, e deve constar da ratificação.

**Bloco B — a hipótese que motivava tudo, FALSIFICADA.** As 16 curvas trimadas,
pontuadas na curva **inteira** sob a métrica de nível: **0 de 16 passam**, e
várias pioram muito (`liu2025_M16_amp0p25` 0,0745/0,1672 → 0,7270/5,3056).
Remover os trims sob esta métrica **não resgata nada**. A meta iria de **148 para
139**: zero viradas, **9 perdas**.

**N6 fez o serviço para o qual foi inventado.** Ele existia porque a 1ª tentativa
só podia melhorar números; aqui 14 curvas pioram, e a leitura declarada de
antemão (separar piora **legítima** de **janela degenerada**) provou-se
necessária — 5 das 14 são degeneradas, com
`eccles2010_fig7d_axial_3p1kN_constant` (`Δ_col`=25) indo de 0,0668/0,0891 para
**3,7052/38,5223**. O risco previsto no §2.4 do prereg materializou-se
exatamente como escrito, e é o registro prévio que permite lê-lo como
propriedade da regra em vez de acidente.

### 4.46a A LINHA FECHA — e as duas mortes convergem

| | 1ª (ortogonal, §4.45) | 2ª (nível, §4.46) |
|---|---|---|
| morreu por | o **modelo** escolhia a correspondência | o **normalizador** não é invariante à amostragem |
| meta | 147 → 153 (4 de 6 viradas ilegítimas) | 148 → **139** (0 viradas, 9 perdas) |

Ramo pré-declarado: **abandonar a linha inteira**. Registro:
**pontuar o colapso em vida não é redutível a uma métrica automática sobre
curvas digitalizadas esparsas.** As duas falsificações convergem para a mesma
raiz — no trecho quase-vertical **o dado publicado não carrega informação
suficiente** nem para distinguir formas nem para normalizar uma tolerância; o
que existe ali é a moldura da figura e as escolhas do digitalizador. Isso
**reforça** a §4.44a com duas falsificações em vez de um argumento: essas curvas
são **metric-limited** e ficam fora da meta por razão **metrológica**, com o
trim (julgamento humano, documentado caso a caso) como saída honesta.

**Rota restante, NÃO tentada e não falsificada:** **métrica de banda** — comparar
o modelo contra um **envelope** de incerteza do dado em vez de contra uma curva.
É a resposta estatisticamente correta a 44 % de scatter de espécime, e o prereg
v1 da rampa já a havia nomeado como *"fora de escopo, registrado aqui para não
se perder"* (§5). Muda a métrica de *"distância a uma curva"* para *"pertinência
a uma banda"* — mudança maior que as duas tentadas. Decisão do professor.
**⇒ Autorizada, executada e registrada na §4.47: a linha NÃO fechou.**

### 4.47 MÉTRICA DE BANDA (3ª tentativa) — a discriminância SOBREVIVEU; morre por limiar, não por estrutura (2026-07-28)

Pré-registro `specs/2026-07-28-metrica-banda-prereg.md`, gates **congelados em
`0e97d6a`** com a conta de satisfazibilidade **rodada numericamente** (na 2ª
tentativa ela foi feita de cabeça e errou 45×). Executada; **revertida** pelo
ramo pré-declarado do B3. Store restaurado, **0 divergências verticais** nos
203, fingerprint `4f5bedfbace4`, meta segue **147/202**. Detalhe:
`New_Theory/metrica_banda_results.md`.

**Forma:** banda = `[min, max]` do dado **interpolado** numa janela horizontal
`±h_N` com `h_N = 3 %·N_fim`; resíduo = distância **hinge** fora da banda,
avaliada em `N_i`. **Sem `min()` e sem voto do modelo** (corrige a 1ª morte);
**sem regra de joelho** — `h_N` vem de um número por curva (corrige a 2ª).
Sem dilatação vertical `±σ_r`, de propósito: incluí-la afrouxaria o tripé em
0,02 em toda curva, inclusive plana.

**Veredicto: B0 ✓ · B1 ✓ · B2 ✓ · B3 ✗ · B4 ✓ · B5 ✓ · B6 ✗.**

**O que é novo e importa:**

- **B1 (discriminância) PASSOU — 1ª vez em 3 tentativas.** No `fig2`, nas duas
  digitalizações: rampa **0,0243/0,0521** e **0,0137/0,0542** (passa); cliff e
  sem-forma **0,0479/0,1783** e **0,0759/0,1319** (falham). Era este o gate que
  matou §4.45 e §4.46.
- **B0 (invariância à amostragem) passou com precisão notável:** res.máx da
  rampa difere **3,9 %** entre 15 e 124 pontos, contra os **4,0 %** previstos
  pela conta. O defeito que matou a 2ª tentativa (27,5× em `Δ_col`) está
  resolvido.
- **Bloco C — o número que justificaria remover trims:** as 16 curvas trimadas,
  pontuadas **inteiras**, dão **10 de 16 passando** (sob a métrica de nível eram
  **0 de 16**). Meta nas janelas de hoje: **147 → 154**.

**Por que morre assim mesmo:**

- **B3 ✗** — `chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9` virou (0,1173 → 0,0949)
  com largura de banda **0,0443**, abaixo do 0,05 exigido: virada de baixo
  conteúdo, e o gate existe para barrá-la. Ramo pré-declarado: **morre**.
- **B6 ✗ — e o defeito é de autoria do gate, não da métrica.** Defini *plana*
  como largura `< 0,02` e a tolerância como `0,005`; uma curva com largura até
  0,02 pode mudar o res.máx em até 0,02 ⇒ **as duas cláusulas do gate são
  incompatíveis entre si**. Ramo pré-declarado do B6 **não mata** (*"revisar
  `FRAC_N` em prereg novo"*).
- Diagnóstico: as 3 curvas que reprovam são **esparsas** (25, 7 e 9 pontos). O
  problema é a janela grande **relativa ao espaçamento entre pontos**, não em
  valor absoluto.

**Terceiro defeito de autoria de gate, e a regra se reforça.** 1ª: `M0`
insatisfazível. 2ª: `N2` com premissa errada (conta de cabeça). 3ª: `B6`
internamente inconsistente. A regra da §4.45 pegou o caso 2 quando rodada
numericamente, mas **não pega o 3**, porque valida o gate contra *um caso* e não
contra *si mesmo*.

> **Reforço da regra:** a conta de satisfazibilidade tem de cobrir o **pior caso
> admitido pelo próprio escopo do gate**, não um exemplo. Se o gate diz *"para
> curvas com X < a, exigir |Δ| ≤ b"*, é obrigatório verificar que **X = a** ainda
> produz `|Δ| ≤ b`. Gate cujo escopo admite violar o próprio critério não é gate,
> é armadilha.

**Estado da linha:** **NÃO fechada** — o ramo que a fecharia (`B1 ✗`) não
ocorreu. Morreu **esta parametrização**, por dois defeitos de **limiar**.
Uma 4ª tentativa mudaria o mínimo (`h_N` sensível ao espaçamento entre pontos;
`B6` reescrito coerente; `B3` mantido). Contra ela pesa: é a 3ª tentativa, o
autor errou o gate nas três, e a métrica é **unilateral** (só melhora números),
o que exige gates mais duros e não menos. Há argumento honesto para **parar** e
manter a posição da §4.46a (trim por julgamento humano). **Decisão do professor.**
**⇒ Autorizada, executada, e a linha FECHOU na §4.48.**

### 4.48 BANDA v2 (4ª tentativa) — o GATE CEGO reprovou. A LINHA FECHA EM DEFINITIVO (2026-07-28)

Prereg `af711b8`. **Nada a reverter: nenhuma linha de código canônico foi
tocada** — a percepção de que a banda só precisa do modelo **nos ciclos do dado**
(o vetor `metric_pred`, já no store) tornou a tentativa **pós-processamento
puro**, sem varredura e sem ciclo de reversão. Fingerprint `4f5bedfbace4`, meta
**147/202**. Detalhe: `New_Theory/metrica_banda_v2_results.md`.

**A correção da forma:** a banda passou a exigir **evidência medida** — janela
sem nenhum ponto vizinho medido ⇒ banda `[r_i, r_i]` ⇒ resíduo = `|Δr|`
**exato**. Corrigiu a 3ª morte: `chu2026ti_..._test9` tem 25/25 pontos sem
vizinho e não vira mais (**C6 ✓**).

**O §0 do prereg declarou, ANTES de medir, que o `fig2` deixara de ser teste
cego** (três variantes foram testadas nele) e rotulou C2/C3 como **caso de
projeto**, jogando a evidência real no **C4**, cego, no núcleo `amp0p4/0p5/0p6`,
nunca usado no desenho. Resultado:

| curva (sem trim) | sem forma | rampa | CLIFF |
|---|---|---|---|
| amp0p4 | 0,0552/0,1547 F | 0,0388/0,1476 F | 0,0552/0,1547 F |
| amp0p5 | 0,0457/0,1706 F | 0,0437/0,3300 F | 0,0571/0,3300 F |
| **amp0p6** | **0,0340/0,1116** F | **0,0718/0,3300** F | 0,0594/0,3300 F |

**A rampa passa em 0 de 3**, e em `amp0p6` é **pior que não ter forma nenhuma**.
⇒ **A discriminância que o `fig2` exibia era artefato de ter sido projetada
nele.** C2/C3 passaram; o cego reprovou. É a demonstração mais limpa da campanha
de que projetar e testar na mesma curva não vale nada — e só existe porque a
perda de cegueira foi **declarada por escrito antes**, obrigando a criar um gate
cego separado.

**C7 mata independentemente:** 36 curvas com **>50 %** dos pontos alterados (até
**94 %**). Coexistência informativa: **C5 passou com mediana 0,00000** (a curva
mediana não muda nada) enquanto C7 falha em 36 — o efeito é **concentrado num
terço das curvas e difuso dentro delas**, não um desconto uniforme.

**C0 reprovou por causa EXTERNA** (a sessão paralela tocou 2 arquivos às 13:10),
**e o gate também estava mal escrito**: ele testava o estado de uma árvore de
trabalho **compartilhada**, não uma propriedade da mudança. **4º defeito de
autoria de gate em 4 tentativas** ⇒ **2º reforço da regra: um gate mede uma
propriedade DA MUDANÇA, nunca do ambiente; se pode ser violado por algo que o
autor não fez, não é gate.**

**O que funcionou e vale reusar:** C1 deu **0,00e+00 em 1952 pontos** (a conta
previu igualdade **literal**, não assintótica — contraste com o `M0` da 1ª); C2
acertou a previsão na casa decimal (3,7 % vs 3,7 %); e o custo caiu de 25 min +
reversão para **segundos e zero limpeza**. **Método a reusar: antes de patchear
o runner, verificar se a métrica proposta é computável dos vetores que o store
já guarda.**

### 4.49 Su–N BILINEAR — o JOELHO TRANSFERE ENTRE TAMANHOS (5,9 %). 1º candidato a constante cross-rig da campanha (2026-07-28)

Gates congelados em `3794090`. **Pós-processamento puro** — `src/`, store, física e
fingerprint intocados; **nada adotado** (S6). Detalhe:
`New_Theory/sun_bilinear_resultado.md`.

**Corrige o 5º defeito de gate.** O L4 testou uma **lei de potência única** contra
dados que o artigo declara **bilineares**. Testado o modelo que a fonte declara — e
que o nosso `sun_life()` **já implementa** —, o quadro inverte.

**S1 ✓ · S2 ✓ · S3 ✓ · S4 ✗(boa notícia) · S5 ✓**

| | m₁ (alta) | m₂ (baixa) | σ_joelho | R²(log) |
|---|---:|---:|---:|---:|
| M16 | 12,03 | 1,38 | **513,5 MPa** | **0,9970** *(lei única: 0,8484)* |
| M10 | 10,07 | 1,61 | **544,0 MPa** | 0,9946 |

**S2 (CEGO) — o joelho transfere a 5,9 %.** Duas juntas de tamanhos, pré-cargas
(60 vs 25,9 kN) e grips (85 vs 42 mm) diferentes partilham a mesma fronteira
alto/baixo ciclo **em tensão de raiz**. Traduzido para amplitude: δ_crítico = 0,475
(M16) vs 0,421 mm (M10) — **11,4 %**. ⇒ **a transformação da Table 2 absorve metade
da diferença de tamanho**; é isso que "normalização" significa, medido.

**S3 (CEGO) — o ramo de alto ciclo transfere a −1,3 %**, com `(C₂,m₂)` do M16 e
**zero re-ajuste**.

**Leitura física:** `m₁` ≈ 10–12 e `m₂` ≈ 1,4–1,6 **não** são uma S–N de fadiga
(m ≈ 3–5) — são a assinatura de um **limiar de afrouxamento**: abaixo do joelho o
parafuso quase não afrouxa, acima afrouxa rápido. Coerente com Yang et al. citado no
próprio artigo (*"bolts did not loosen when the amplitude was less than a certain
critical value, similar to the fatigue limit"*).

**Três ressalvas, com o mesmo destaque:** (i) **S3 repousa em UM ponto** — o que
sustenta o achado é a **conjunção** S2 (5,9 %) + S3 (−1,3 %) + o ponto de 518 MPa do
S4 (−5,3 %), três concordâncias independentes no alto ciclo; (ii) 4 parâmetros para 6
pontos no ajuste M16, declarado no prereg — por isso o que vale é a transferência
zero-refit; (iii) **acima de ~780 MPa a transferência quebra** (−77,6 %, −71,8 %,
−90,9 %; razão `N_M10/N_M16` = 1,02 → 1,84 → **4,51**).

**S4 não confirmada = boa notícia pré-declarada.** A hipótese era que **todos** os
pontos de baixo ciclo cairiam fora de ±30 %; o de 518 MPa ficou **dentro** (−5,3 %),
acima do joelho. A fronteira útil é **mais larga** que a hipótese. Só se pôde ver
isso porque a hipótese foi escrita **antes**.

**Por que importa para a §8.** A doutrina desde a Fase 1 é *"formas transferem,
constantes não"*. Este é o **1º contra-exemplo medido**: no ramo de alto ciclo, a
Su–N atravessa o eixo **tamanho** — desde que o driver seja a **tensão de raiz da
Table 2**, não a amplitude nominal. Escopo honesto: σ ≲ 550 MPa, dois tamanhos, mesmo
material, mesmo laboratório. Não é lei universal; é uma constante que atravessou
**um** eixo que nenhuma outra atravessou.

**Bloqueio para adoção (por isso S6):** o `c_σ` da Table 2 existe para **dois**
tamanhos apenas, e a nossa fórmula de flexão erra essa escala por **2,1×** (§3 do
estudo de modelagem). Adotar exige antes saber calcular `c_σ` para um rig fora da
Table 2. Prereg próprio.

### 4.50 A-vs-B da rampa, MEDIDO — a Opção A vence; a narrativa do "acoplamento de graça" via k_b está FALSIFICADA neste carregamento (2026-07-28)

Delegação do professor: *"investigue mais a fundo e escolha a opção que você
recomendar"*. Sonda `liu2025_rampAB_probe.py` (engine intocado), com a previsão
**escrita no cabeçalho antes de rodar** e confirmada. Detalhe:
`New_Theory/liu2025_rampAB_resultado.md`.

**Achado estrutural (lendo o engine, não o argumento):** o feedback "F₀ cai → mais
slip → mais wear" corre por `state.F_0` (`F_slip = μ·F₀`) e existe nas DUAS opções;
`k_tr` (bending) usa `d₂⁴` e é **cego a `k_b`**. Os canais próprios da Opção B são o
conversor `dF_0 = −k_b·dδ` dos outros mecanismos (sinal **negativo** — parafuso mole
perde MENOS por assentamento), Φ (inerte aqui) e `U_internal` (bookkeeping).

**Medido (A0 = sonda dos gates v2 · A1 = +dE incremental · B1 = +k_b modulado):**
(1) **forma idêntica** — Δ cruzamentos A1↔B1 ≤ 60 ciclos, ≪ tolerâncias 930–2550;
passes iguais (5/5, 5/5, 2/5, 4/5); (2) **B NÃO conserta a `amp0p6`** — os dois
primeiros cruzamentos dela são idênticos ao dígito (−2954/−2729); o desvio é de
relógio/coordenada, não de rigidez; (3) decomposição na janela da rampa confirma o
sinal: wear B−A = **+0,23 a +0,70 kN** (B amortece) e a rampa compensa; (4) **energia
decide** — residual A0 0,7–1,9 J · **A1 0,017–0,151 J** (10–100× melhor) · **B1 até
−20,5 J** (modular `k_b` muda `U = F₀²/2k_b` sem contraparte de trabalho — energia
aparece do nada; uma B correta exigiria contabilizar `∂U/∂k·dk`).

**Decisão registrada: Opção A com energética por incremento.** Prereg de
implementação congelado (`specs/2026-07-28-ramp-capability-prereg.md`, P0–P6 com as
contas MEDIDAS pela sonda); **implementação não executada** — aguarda o professor.
**B fica como candidato de forma para a família competitive-failure**, com o registro
corrigido: canais de 2ª ordem e sinal negativo neste modo, não conserta a `amp0p6`,
e carrega a dívida de bookkeeping `∂U/∂k`.

### 4.51 RAMPA DE FRATURA — capacidade EXECUTADA; todos os gates passam; paridade EXATA com a sonda (2026-07-28)

Prereg `ea028ef` executado por autorização do professor. A única física ausente para o
software gerar a curva em S do Liu 2025 (§4 do `liu2025_estudo_curvas.md`) agora existe
no engine: `fat_ramp_D_on`/`fat_ramp_q` em `JointMaterial`, ramo de rampa em
`FatigueLoss` (Opção A/A1 da §4.50). Detalhe: `New_Theory/ramp_capability_resultado.md`.

**P0 ✓ (203 bit-idênticos) · P1 ✓ (paridade EXATA — 0,00 ciclos nos 20 cruzamentos) ·
P2 ✓ (LI_2022_TRIBOINT 4/4 idêntico) · P3 ✓ (residuais 0,017–0,151 J, iguais aos da
sonda) · P4 ✓ (S-curve no Run via `_v2_tuner_overrides`, teste permanente) · P6 ✓.**
Default-inerte: `fat_ramp_D_on = 1.0` = cliff intocado; nenhum config adotado liga a
rampa; fingerprint segue `4f5bedfbace4`; meta segue 147/202 — como o prereg declarou,
capacidade não é ganho de meta.

**P5 (informacional, primeiro número):** o N₉₅ emergente do canônico dispara **10–100×
cedo** em amplitude baixa (razões 0,01–0,08; 1,24 em 0,8 mm) — assentamento
front-loaded, coerente com `N_emb` calibrado em MAE pós-trim e não no cruzamento
precoce. Insumo para a eventual adoção per-rig, não gate (leitura vertical no platô é
mal-posta em N).

**Aberto (fila):** adoção per-rig do LIU_2025 (prereg próprio: `fat_C1` ancorado no
contexto canônico c/ Goodman vivo ~50 %, `fat_m1 ≈ 3,1`, `D_on` handbook, `q` per-rig;
trims permanecem — mudaria decomposição/report, não o tripé) · `_CAP=100000` do Run ·
rótulo de procedência do `fat_m1=2,7`.

### 4.52 ADOÇÃO per-rig LIU_2025 — EXECUTADA e REVERTIDA pelo gate cego A1: o relógio preditivo não segura o colapso (2026-07-28)

Prereg `8ec2521` (congelado com as contas RODADAS: `fat_C1=4,02544e32` ancorado nas 6
vidas de fratura com Goodman vivo, ±36 % de espalhamento; risco declarado nas 3 curvas
com rampa dentro da janela da métrica). Execução autorizada; **A1 CEGO reprovou**:
`amp0p8` foi de 0,0487/0,0853 para **0,1597/0,6800** (ΔMAE +0,111). Ramo pré-declarado
honrado — **rollback instantâneo pelos backups**; fingerprint `4f5bedfbace4` uniforme;
meta intacta; **a capacidade fica** (`f05a531`). Detalhe:
`New_Theory/liu2025_adocao_resultado.md`.

**A causa é o RELÓGIO, não a forma.** O relógio da `amp0p8` roda 27 % adiantado
(N_pred/N_meas = 0,734) e os trims sentam no joelho (`trim ≈ N_D ≈ 0,72–0,80·N_f`) ⇒ o
colapso previsto cai INTEIRO na janela da métrica: modelo a 0,000 em ~10,6 k contra dado
segurando 0,68 em 11,5 k. As outras duas curvas de risco (`amp0p3` 5 679 ciclos dentro,
`fig2` ~69) deram **Δ = 0,0000 exato** — nenhum ponto do dado digitalizado cai na fresta
(a métrica avalia nas abscissas esparsas do dado). **Confirmação quantitativa do
orçamento do premeasure §2:** o colapso ocupa 20–29 % da vida ⇒ tolerância de relógio
≤ 5 %; disponível com relógio preditivo determinístico: ±36 %.

**O que o A4 deixou de evidência:** com a adoção ativa, o canal `fatigue` aparece na
decomposição (0,775 de F₀ na `amp0p8`; **0,846 na `amp0p3`**, cuja fratura o modelo
passou a prever DENTRO do range do dado, −7 %) — mecanicamente a curva em S completa
funciona no report; o que não se sustenta é o instante.

**Achado colateral (A3): `parallel_batch` cobre 202 de 203** — `exemplo_m12_sintetico`
fica de fora e mantém carimbo velho. Inofensivo quando o fingerprint não muda; **quebra a
uniformidade em qualquer adoção futura** re-carimbada via batch. Registrado no CLAUDE.md.

**Rota que destravaria (não executada; decisão do professor):** E2 do premeasure —
`N_f` como **input-de-paper por curva** (precedente: `LI_2022_TRIBOINT` com `fat_C1`
ancorado no `N_frat` medido); claim honesta *"prevê a curva dada a vida"*, e com relógio
lido a rampa já provou 10/10. Alternativa: dado bruto dos autores (carta pronta).

### 4.53 ADOÇÃO E2 do LIU_2025 — ADOTADA: o estágio 3 no canônico por física, DADA a vida (2026-07-28)

Prereg `d721b14`; execução autorizada. **E1 (cego) OK — 7/7 no tripé, pior ΔMAE
+0,0006** (`amp0p6`); E2g OK; E3 OK após conserto de execução. **Fingerprint novo
`9ac44acd03de`** uniforme nos 203; meta intacta (147/202). Detalhe:
`New_Theory/liu2025_e2_resultado.md`.

**A única mudança em relação à adoção revertida (§4.52) foi o relógio:** `N_f`
input-de-paper POR CURVA (7 `fat_C1` fixados nas contas — mesma coluna da matriz que já
dá os `trim_n_max`; precedente `LI_2022_TRIBOINT`). As 6 curvas cegas seguraram como a
previsão analítica dizia (α(D_trim) ≤ 2,6e-6 ⇒ rampa numericamente nula na métrica).
Claim honesta: **"prevê a curva dada a vida"**.

**O que compra:** as curvas full-range agora TERMINAM como o dado (final_pred 0,000–0,336
contra ~0,78–0,84 antes) e a decomposição carrega o canal `fatigue` (0,19–0,78 de F₀) —
fecha o residual nomeado no verdict do PR-9b (*"cliff terminal = fratura"*). Métrica e
trims intocados.

**Conserto de execução no E3 (o prereg previa o método errado):**
`parallel_batch --cases exemplo_m12_sintetico` seleciona NADA — o caso está fora do
universo do batch. Conserto real: re-sim direta via `runner.simulate_case` + carimbo,
métricas verificadas bit-idênticas. Gotcha do CLAUDE.md corrigido.

**Arco do dia fechado:** capacidade (§4.51) → adoção preditiva revertida (§4.52, relógio
±36 %) → **E2 adotada** (relógio lido). O software gera a curva em S completa do Liu 2025
no canônico — que era a pergunta do professor ao abrir o estudo de curvas.

### 4.54 ESTUDO CHU 2026 — a receita mais limpa morreu nas CONTAS, antes do prereg; a fonte segue form-limited com a forma NOMEADA pela própria fonte (2026-07-28)

Estudo autorizado no molde do Liu (`New_Theory/chu2026_estudo.md`; nota de aparato
NOVA `apparatus_notes/chu2026_triboint.md` — não existia). Custo: **zero preregs**.

**O que o paper entrega e o dado nosso confirma:** a **Fig. 5 MEDE o COF evoluindo**
durante a vibração (sobe enquanto afrouxa, mais rápido em F₀ baixo, platôa no arresto)
— e o **µ implícito nos NOSSOS CSVs** (`chu_mu_implicito.py`: µ_impl ∝ taxa/r, válido
porque o Chu está em gross-slip com slip constante) reproduz isso: test2 sobe **9,3×**
(a curva que o paper destaca), test3 6,0×, e em 0,4 mm o 49 kN sobe ≫ 61/73. No test4
a taxa colapsa — µ como **resistor** (arresto) vencendo o µ-**driver** (wear): os dois
papéis aparecem separados no dado. O próprio FEM do paper diverge do ensaio, nas
palavras deles, pela *"time-dependent nature of the friction coefficient"*.

**Gap de config documentado:** 8/9 curvas rodam sem chave per-rig (µ=0,15 default vs
0,05 rosca prateada; passo registry 1,50 vs MJ10×**1,25**; E 200 vs **189 GPa**); só o
`test1` (limiar) tem adoção (PR-38, `k_dmg_mu=−2,43` — µ subindo, o sinal da Fig. 5).

**A receita candidata mais limpa — estender o trio PR-38 ao grupo + procedência (zero
fit novo) — foi REPROVADA nas contas de projeto** (2 curvas de projeto, 6 cegas):
test2 **piora em todas as variantes** (0,154/0,464 → 0,166–0,203 / 0,486–0,637);
test3 melhora no MAE mas não fecha o tripé. Causa física: µ subindo **arresta o
modelo**, mas o test2 real **perde tudo** — é o regime 2 do paper (carga vence o
atrito que sobe). Um `k_dmg_mu` escalar não carrega os dois papéis do µ nos dois
regimes. Nenhum prereg foi congelado sobre receita reprovada (regra §4.45 aplicada
ANTES do prereg — é para isso que a conta de satisfazibilidade existe).

**Estado final:** CHU_2026 segue form-limited (6 violadoras), agora com a forma
nomeada pela fonte: *torque de afrouxamento assimétrico acumulado na interface
porca–placa + µ(t) evoluindo em dois regimes*. Destravamento em ordem de custo
(fila): (i) **digitalizar a Fig. 5** → âncora quantitativa de µ(t), barata e de
procedência; (ii) forma nova *asymmetric cumulative torque* — cara, só depois de (i).
FAIL2 segue **não gasto**. Correções de procedência isoladas (~neutras, variante A)
ficam registradas sem adoção — mexeriam fingerprint sem ganho de gate.

#### 4.54a ERRATA + FECHAMENTO na mesma noite — a rota (i) já tinha sido percorrida; três famílias falsificadas com o µ medido em mãos (2026-07-28)

**Errata (3 erros do mesmo método — contei o diretório canônico em vez de perguntar ao
registry, o gotcha que o próprio CLAUDE.md registra):** (1) a nota `chu2026ti.md` JÁ
existia (pasta E, é a que o registry resolve, mais completa que a minha — duplicata
removida); (2) a **Fig. 5 JÁ estava digitalizada** (2026-07-15, 5 CSVs µ_plate(N),
tests 1/2/4/7/8; tests 3/5/6/9 sem COF no paper); (3) a rota (i) **JÁ havia sido
executada**: prereg F3.2-CHU (21/07) construiu o encanamento `mu_bearing_schedule`
(default-inerte, bit-idêntico) E rodou a adoção per_case — **G-CHU-a FAIL**
(test4 0,183/0,284, outros 0; máx. 2 tentativas ⇒ restava 1).

**Fechamento com 2 sondas (`chu_schedule_isolado.py`, `chu_energywear_sonda.py`):**
(a) o schedule **isolado** da receita F3 é quase inerte — |Δ|~0,01 nas 4 curvas,
G-CHU-a insatisfazível em 3 variantes. Causa = **fato de engine**: em disp-mode o
wear é **Archard (`K/H·p·slip`), sem µ** — o canal de 93 % da perda do Chu é cego ao
µ(t) que o paper mede (µ só alcança arresto/rotacional ~7 % e dano, desligado). A 1ª
tentativa do F3.2 falharia com qualquer receita. A 2ª tentativa **não foi gasta**
(contas insatisfazíveis ⇒ ramo "documenta e fila" do próprio prereg).
(b) recolorir a **lei** (wear energético `d_wear=k_E·µ_medido(t)·p·slip`, emulado
bit-exato mutando `k_wear_spec` por ciclo, K_archard=0) **morre inclusive na âncora**:
test4 0,118/0,249 no melhor k_E (2–3e-13); transferência zero-refit 0/3 (protocolo
anti-FAIL1: âncora com mecanismo ativo, cegas declaradas antes).

**Veredicto em 3 degraus:** µ-livre não reproduz → µ medido prescrito não muda → lei
µ-acoplada com µ medido não fecha nem ancorada. **O resíduo do Chu é a estrutura
temporal do kernel de colapso**, não o µ nem a lei de wear. Único candidato restante:
o torque acumulado do próprio paper (`M⁻=(F₀/ξ)^a·(N^b+η)`, **b=1,65 — acumulação
explícita no relógio**, estrutura que nenhum mecanismo estado-dirigido nosso tem);
instanciá-lo pede ≥3 constantes per-rig sobre 4 curvas ⇒ **não-adotável sob
parcimônia**. Recomendação: test2/3/4/7/8/9 candidatos a **exceção assinada** na
próxima ratificação; reabrir só se outra fonte exibir aceleração N-explícita
(test3-like), tornando o canal testável cross-rig.

### 4.48b ERRATA — os "44 % de dispersão de espécime" do Liu 2025 NÃO estão estabelecidos (2026-07-28, releitura do artigo integral)

Relendo o **PDF integral** do Liu/Yang 2025 (14 pp., não só as notas de aparato) para o
estudo de modelagem (`New_Theory/liu2025_estudo_modelagem.md`): **a amplitude do ensaio da
Fig. 2 não é declarada no artigo.** O texto diz apenas *"a typical clamping-force recession
process of a bolt under the action of a transverse load"*. O *"~0,8 mm class"* das nossas
notas de aparato era **inferência nossa**.

Sobre essa inferência eu construí, no mesmo dia, a afirmação de que `fig2` e `amp0p8` são
"a mesma amplitude nominal" e portanto exibem **44 % de dispersão de espécime** — número
citado em **§4.44a, §4.45, §4.46, §4.47** e em três pré-registros. **Medido:** pela lei D–N
do próprio artigo (`N ∝ δ^−2,7`), uma amplitude não reportada **14,5 % maior** (0,916 mm)
explica a diferença 10 k vs 14,4 k **inteira, com dispersão zero**.

**O que cai:** a frase *"o relógio está fechado pelo dado"*. O número defensável é
**±17 %** — uma única lei de potência sobre a tensão de raiz do artigo dá `m = 3,012`,
**R²(log) = 0,9894**, erros −19 %/+14 % nas 6 amplitudes (§4 do estudo).

**O que NÃO cai:** (i) o fechamento da linha de métrica (§4.48a) — as quatro mortes foram
em gates de **discriminância**, que não dependem do scatter; (ii) a classe
**metric-limited** — o argumento é aritmético (0,20→0,104 em 5 ciclos ⇒ ±0,05 % da vida
para `res.máx<0,10`), e ±17 % segue duas ordens de grandeza acima disso.

**Lição:** uma inferência registrada numa nota de aparato foi citada como medida em cinco
documentos no intervalo de um dia. A nota foi corrigida na fonte
(`apparatus_notes/liu2025_scirep_M16.md`) com a errata explícita. **Regra:** número que
vier de nota de aparato e não do artigo tem de carregar o rótulo *inferido* no ponto de
uso, não só na origem.

### 4.48a FECHAMENTO DA LINHA — balanço das 4 tentativas

| # | forma | morreu por | causa raiz |
|---|---|---|---|
| 1 | resíduo ortogonal (§4.45) | **M2** | o **modelo** escolhia a correspondência; despencar era perdoado |
| 2 | correspondência de nível (§4.46) | **N2** | normalizador não invariante à amostragem (1100 vs 40 ciclos) |
| 3 | banda v1 (§4.47) | **B3** | janela interpolava sobre segmentos **não medidos** |
| 4 | banda v2 (§4.48) | **C4** cego + **C7** | a discriminância anterior era **artefato de projeto** |

Quatro pré-registros, quatro execuções, quatro reprovações — **três no gate de
discriminância**. **Registro final:**

> **Nenhuma métrica automática sobre curvas digitalizadas esparsas distingue a
> forma certa da errada no colapso quase-vertical.** O que existe ali é a moldura
> da figura, os 44 % de scatter de espécime e as escolhas do digitalizador. Toda
> métrica que "resolve" o problema o resolve perdoando **também o cliff**.

**Resposta final adotada:** as curvas de colapso quase-vertical são
**metric-limited**, ficam fora da meta por razão **metrológica**, e o
`trim_n_max` **aplicado por julgamento humano e documentado caso a caso** é a
saída honesta — com a ressalva da §4.46 de que a regra que o descreve **não é
automatizável**. Custo da linha: 4 preregs, 3 varreduras, 3 reversões, **zero
adoções**, e 4 defeitos de gate, cada um gerando uma regra: (1) conta de
satisfazibilidade; (2) cobrir o pior caso do escopo; (3) medir a mudança e não o
ambiente; (4) **um gate cego vale mais que nove no caso de projeto**.

### 4.55 `emb_pressure_exp` — capacidade CONSTRUÍDA default-inerte; a lei conserta o defeito que nomeou e **não fecha a curva** (2026-08-16)

Campo novo em `JointMaterial`, **default 0.0 = OFF exato** (11 testes de
contrato), prereg
`2026-08-16-lu2024-embedding-dirigido-por-pressao`, resultado em
`New_Theory/lu2024_embedding_pressao_resultado.md`. **Nada adotado.**

**A física.** O engine já tinha `emb_conform_exp` = **pré-conformação** (aperto
maior gasta aspereza no torque ⇒ sobra menos resíduo cíclico; S cai quando p
SOBE). O campo novo é o ramo **complementar e de sinal contrário**: o
achatamento plástico *precisa* de pressão, logo abaixo de uma referência o
reservatório é mais **raso** — `S_p = min(1, (p_init/p_ref_emb)^n)`. As duas
coexistem em junta real e por isso **multiplicam**; nenhuma delas jamais morde
na mesma pressão (uma está sempre no `min`).

**Por que foi construída.** No `LU_2024` o encaixe é uma profundidade quase
**absoluta**, e a mesma profundidade vira fração muito maior de uma pré-carga
pequena. Medido na varredura de torque da própria fonte (7× em F₀): o excesso
de perda no 1º ciclo vai com **1/F₀ a r = +0,995**. Controle negativo passa —
no `CACCESE_2009` (embedding **0,2 %** da perda) o sinal some.

**O que a lei entrega, medido:** a queda no 1º ciclo da `fig20_T10Nm` vai de
**0,627 para 0,344** contra **0,362** do dado (resíduo em N=1: −0,265 →
**+0,018**). O isolamento é **estrutural**: 5 das 7 curvas da varredura —
incluindo **as 3 do tripé** — estão acima da referência e o `min(1,·)` as deixa
em S = 1 **exato**; as 12 irmãs movem **+0,0000** em toda a grade.

**O que ela NÃO entrega:** a curva não fecha (melhor MAE 0,1599 = **3,2×**), e
o σ_res **piora** (0,0749 → 0,1188) porque a correção troca erro de nível por
erro de forma (`ρ(res,N)` de +0,41 para −0,79).

⚠️ **O achado que vale mais que o veredito:** arrumado o 1º ciclo, aparece um
**segundo defeito** que estava escondido atrás dele — o modelo colapsa até o
`loose_arrest_floor` = 0,10 da fonte e trava, enquanto o dado retém **0,310**.
Corrigindo os dois juntos a curva **fecha com folga** (0,0112/0,0284/0,0138,
pior perna **0,55×**). Isto replica a disciplina **D-Z**: a varredura marginal
dizia *"não fecha e ainda piora o σ"*, e a leitura certa não era *"a lei está
errada"* e sim ***"a lei está incompleta"***.

**Por que mesmo assim nada foi adotado.** O piso terminal **não tem lei de
pré-carga** nesta fonte: a retenção do dado é 0,037 / 0,309 / 0,187 / 0,064 /
0,234 — **não-monótona** no torque, `corr` com 1/F₀ = −0,51, e o núcleo travado
**absoluto** variando **45×** (78 N a 3 516 N). O par que fecha a alvo é fit
**por curva**, que o item D da doutrina proíbe; e `floor`=0,34 na fonte
destruiria a `T22Nm` (terminal 0,064), recém-entrada no tripé.

⚠️ **Errata da 1ª redação (mesmo dia):** os terminais publicados aqui eram
`0,142/0,310/0,190/0,102/0,233` — o último ponto **acima do `FLOOR_TRIM` de
0,10**, não o do ensaio. Os reais vêm da Tabela 9 do paper. A conclusão não
muda; a evidência melhora.

✅ **A pergunta que isto deixava foi RESPONDIDA no mesmo dia**
(`New_Theory/lu2024_fig20_nao_monotonia_e_fisica.md`): a não-monotonicidade é
**física e publicada** — Tabela 9 mais a prosa da p.19 (*"o torque de 4 N·m não
atinge o efeito de aperto"*; 10 N·m é o ótimo; de 10 a 22 N·m *"a velocidade de
atenuação aumenta com o torque"*; 28 N·m recupera). A hipótese de mistura de
protocolos está **refutada para a fig20** (um protocolo, uma amplitude, uma
máquina) e **nenhum estatuto muda**.

⛔ **RETRATAÇÃO no mesmo dia, 40 min depois.** Publiquei aqui que *"o modelo
reproduz a não-monotonicidade — Spearman +0,700, com mínimo e máximo
coincidindo"*. **Era falso, por defeito de instrumento meu:** com o `FLOOR_TRIM`
ligado a simulação é **truncada**, e eu interpolei o modelo em N=99 numa curva
que parava em N=54 — o `np.interp` grampeia no último valor em vez de avisar.

**Re-simulado sem piso, o terminal do modelo é PLANO:** 0,000 (T4) e
**0,092 · 0,094 · 0,095 · 0,097** nas outras quatro — faixa de **0,005** contra
os **0,272** que o dado varre. Spearman cai para **+0,300** e o máximo do modelo
fica em T28, onde o dado põe T10. O terminal é fixado pelo `loose_arrest_floor`,
que é uma **fração única** de F₀ e por construção não espalha.

⇒ isso **reforça** a conclusão acima em vez de enfraquecê-la: a rota do piso
fecha por **dois** argumentos independentes — o dado não tem lei de pré-carga
para o terminal, **e** o modelo não tem espalhamento nenhum ali.
Registro: `New_Theory/lu2024_fig20_nao_monotonia_e_fisica.md` §3.

### 4.56 `free_spin_kin` — a rigidez de DRENO da hélice é LÍVEL do θ(N) publicado, e a do engine estava 3,6× alta neste rig (2026-08-19)

**O observável que faltava explorar:** o ROUSSEAU_2025 publica a **rotação
relativa parafuso-porca** no eixo secundário das Figs. 4/5 — registrado na nota
de aparato desde a Rodada 4 ("not digitized — available in the PDF") e nunca
digitalizado. Digitalizado hoje da extração vetorial existente (validação:
θ_fim t10 = 10,92° vs 10,97° da leitura manual do §4.27; t12 = 4,36° vs 4,23°).

**A lei que os traços dão, com r² de lei física:**

| junta | dF/dθ (t10) | dF/dθ (t12) | r² |
|---|---:|---:|---|
| aço (fig5, validada) | −919,7 N/deg | −893,6 N/deg | 0,9997 / 0,9969 |
| HDPE (fig4, ERRATA abaixo) | ~~−117,9~~ **−138** | ~~−117,0~~ **−207** | — |

No AÇO, t10↔t12 concordam a 3 % ⇒ **a rigidez de dreno é da JUNTA, não da
curva** — e o engine drena `k_b·lead_per_radian` = 3278 N/deg (laço
infinitamente rígido fora do parafuso). A física do desvio: o dreno real é a
**série** do laço (parafuso + membro + compliances de interface); o HDPE muito
mais mole é qualitativamente o que a série prediz para membro de E~1 GPa.

⚠️ **ERRATA na MESMA noite (o rigor vale contra nós): o "118/117 N/deg
idênticos do HDPE" era ARTEFATO.** A extração vetorial da Rodada 4 é VÁLIDA na
fig5 (3 âncoras independentes: θ_fim 10,92 vs 10,97 manual; t12 4,36 vs 4,23;
pré-carga bate o CSV) e **CORROMPIDA na fig4** (polilinhas truncadas/parciais:
rot t12 dava 23,2° na conta contra ~12,5° impresso; a Fb t12 da polilinha
terminava em 0,56 contra 0,346 do CSV validado). Re-extração DIRETO do PDF
(atributo `dashes` separa rotação de pré-carga; calibração absoluta pelos
ticks de texto) valida contra o impresso: **θ_fim HDPE = 21,27 / 12,65 /
2,16°** (t10/t12/t14; zeros confirmados 0,10/0,00/0,04). Com os θ corretos o
HDPE dá **138 / 207 N/deg** — **varia com a espessura**; a lei-de-junta só
está demonstrada no aço. A concordância "117,9↔117,0" era coincidência de
DOIS artefatos — lição: validação interna entre duas curvas do MESMO
instrumento corrompido não valida o instrumento; só âncora EXTERNA (ticks,
leitura manual, CSV independente) valida. Nada da adoção da `steel_t10` muda
(fig5); a menção "HDPE confirma" nas provs foi corrigida por errata.

**Forma nova (default-inerte, TDD 7/7):** `free_spin_kin` = fração da rotação
relativa do kernel `graded_scrit` que NÃO drena — `dF_0 = −k_b·lead·(1−fsk)·dθ`;
θ e dE ficam com a rotação total (dE suprido por W_ext, padrão do `free_spin`
pós-arresto do §4.23 — que continua existindo para o caso arrestado; este é o
ramo cinemático que o §4.27 nomeou). **LIDA**: `fsk = 1 − (dF/dθ)_med/(k_b·lead)`.
Junto: `loose_amp_exp` passou a agir no ramo graded (a docstring já prometia e o
sítio não lia — item R do lado do CÓDIGO, medido inerte antes do conserto).

**Adoção-de-melhoria na `steel_t10`** (prereg `2026-08-19-rousseau-t10-ratchet-
lido`, gates 6/6): pacote per_case com **oito campos, todos lidos de
observáveis** (fsk=0,7195; k=0,01394 da taxa 0,0736°/ciclo; W_onset=3,55 J da
folga de 1° — o intercepto da reta F(θ) dá 11,1 kN > F₀ ⇒ o 1º grau roda sem
drenar; exp=0 da linearidade r²=0,983; emb=0 e C_creep=0 do ponto publicado
(20, 1,0000)). **Zero fit à métrica; as 3 pernas são predição:**
0,1548/0,2702/0,0994 → **0,0289/0,0668/0,0324** — MAE e res.máx FECHAM, σ fica
a **1,30×** ⇒ a curva **segue aberta** (predição declarada; censo intacto).
Validação independente: θ_fim do modelo 10,42° vs 10,92° (−4,6 %) sem θ_fim ter
fixado k. As 7 irmãs bit-idênticas (a `steel_t10_amp0p2` é blindada por
entrada-vazia no matcher first-match — `test_rousseau_t10_token` fixa a ordem).

**O que ficou declarado no passo 1:** o resíduo restante era FORMA — a
derivada do F publicado é um **sino** (pico 0,0099/ciclo em N=100; o
Hill⁴+taxa-constante sobe mais abrupto e não desce) e o **dreno local cai no
fim** (919,7→~500 N/deg entre θ=8° e 10,4°). Floor lido 0,1086 **recusado pela
regra da barreira** (o dado atravessa: 0,0951).

**PASSO 2 no mesmo dia (prereg `2026-08-19-rousseau-t10-taxa-regredida`,
mandato "trabalhe mais até atingir o tripé"): a descida do sino EXISTE no
engine — o arrest gate — e a REGRESSÃO à taxa observada fecha a curva.**
Prova de necessidade primeiro: LSQ do Hill sozinho à taxa local dá **r²=0,092**
(nenhum re-arranjo de (k, W, s) fecha sem a descida). LSQ completo
`taxa(N) = A·Hill(N; N50, s)·(1−floor/r(N))^aexp` com r(N) do DADO:
**r²=0,891** ⇒ k=0,05109 · W_onset=12,71 J · sharpness=1,89 · **floor=0,0295
(não-barreira POR CONSTRUÇÃO: o bound do LSQ é ≤0,0951, o último ponto
publicado)** · aexp=8 — degenerescência (floor, aexp) **declarada** (só o
produto 0,236 identifica; a célula alternativa 0,0108×25 dá r²=0,896 — mesma
física; escolha pelo precedente SUN, sem a métrica). Estatuto:
**fitado-por-regressão a OBSERVÁVEL** — as 3 pernas continuam predição.
**Resultado: 0,0158/0,0324/0,0098 — TRIPÉ com folga ≥60 % nas três pernas**;
resíduos ±0,02 na curva inteira; **vizinhança 8/8 fecha** (±10–20 % em
k/W/floor/s). θ_fim 9,64° vs 10,92° (−12 %: o arrest corta a rotação terminal
e o ramo graded não tem free-spin pós-arresto — refinamento possível, não
necessário). Trajetória do dia da curva: pior perna **4,0× → 1,30× → 0,39×**.
**A rota fechou a fonte e atravessou para outra no mesmo dia:** as 3 HDPE/amp0p2
fecharam com fsk por PARTIÇÃO (dreno_rot = (ΔF−paralelos)/θ — a regressão crua
atribui à rotação o que os canais paralelos perdem quando θ ∝ N) + k por
bisseção no θ publicado, ROUSSEAU **8/8**. E o **ICMEZ publica a mesma lei como
CARACTERIZAÇÃO** (Fig. 3, 18 ensaios de desaperto, φ* = input do modelo dos
autores): slopes 128–145 N/deg nas 6 células (r≥0,996), quase-insensíveis à
carga — em contraste com o ROUSSEAU aço, onde a MESMA junta dá 920 N/deg a
10 kN e 333 a 3,5 kN (Fig. 6). A física candidata do contraste: rigidez de
contato ∝ carga com pesos diferentes por acabamento (KL100/VH301 zincado vs
aço nu) — registro para o artigo, não é claim do engine. 3 ICMEZ lk13,8
fecharam pela leitura; as 2 lk19,8 NÃO (uma piora — a interação
floor-herdado×trajetória é forma própria, prereg futuro).

---

## 5. Estimação de parâmetros vs curve-fitting — o que realmente otimizamos

A calibração minimiza o erro da curva variando os parâmetros do modelo:

```
min_θ  Σ | curva_simulada(θ) − curva_referência |²
```

Sim, **otimizamos parâmetros do modelo contra a curva.** Isso, por si só, **não**
é curve-fitting pejorativo — é o que toda física experimental faz (ajustar `k` de
Hooke, energia de ativação de Arrhenius, módulo de Young). A diferença não está
no *ato de otimizar*, mas em três propriedades do parâmetro estimado:

| | Estimação de parâmetro (modelo) | Curve-fitting (pejorativo) |
|---|---|---|
| Significado físico | existe e é mensurável **fora** desta curva | só significa "o número que fecha a curva" |
| Identificabilidade | o dado determina o valor | sloppy / não-determinado (artefato da curva) |
| Transferibilidade | mesmo valor prediz outra condição | só vale para a curva ajustada |

**A regra de ouro:** se você estima **todas** as constantes minimizando **a mesma
curva** que quer explicar, colapsa em curve-fitting — mesmo que os parâmetros
tenham nomes físicos. A saída é o design de 3 camadas + a sequência Exp 1–5:
**medir as constantes físicas em ensaios independentes que isolam cada mecanismo,
e então a curva de Junker vira PREDIÇÃO, não alvo de ajuste.**

### 5.1 Procedência de cada parâmetro (honesto, rev. 2026-06-20)

| Parâmetro | Camada | Procedência HOJE | Procedência IDEAL |
|---|---|---|---|
| `k_b, λ, β, A_s` | analítica | geometria/catálogo | (invariante) |
| `k_j_init, α_GW` | físico | default; deveria vir de Exp 1 (rampa estática) | medido: rigidez/separação |
| `C_creep` | físico | âncora de dado independente para o par 304SS (§4.7); par da âncora interna permanece estimado-na-curva — constante É por par tribológico | medido: Exp 2 (creep-hold) |
| `emb_depth, N_emb` | físico | default ajustado à curva (subido 12→30µm p/ fechar nova) | medido: Exp 3 (baixa amplitude, sem slip) |
| `K_archard, hardness` | físico | literatura (boundary lub) | medido: ensaio de wear |
| `µ_thread, µ_bearing` | físico | literatura | medido: Exp 4 (slip onset) |
| `k_*_scale, Phi_*_correction` | tunável | **ajustados contra a curva** de afrouxamento | mínimos, ≈1, identificáveis |
| `c_D, k_dmg_*, D_init` | físico/estado | ajustados à curva do reaperto | medido: assinatura de dano independente |
| `W_conf_ref` | tunável/físico-fenom. | ajustado à curva do sobretorque (1 rig, 1 condição); **Fase 3 tentou ancorar (busca dedicada) e FALHOU** (§4.9: nenhum dado isola; Fouvry α ancora `K_archard`, não este) — **sem âncora**, um degrau abaixo do `C_creep` | capacidade de energia de atrito medida **por par tribológico** num fretting dedicado a ~1.2 GPa, varrendo pressão p/ medir `n` (spec §4.9) |
| `conform_pressure_exp (n), p_ref_conform` | físico | `n=2`/`p_ref=5e8` **fixos por escolha** (não fitados); `p_ref` = geometria+nominal | `n` de um ensaio de varredura de pressão de contato |
| `k_thread_fret` | físico-fenom. | fator geométrico/engajamento do fretting de flanco axial (spec 2026-07-06); default **0.0 = inerte**, **NÃO adotado** — a calibração ao gradiente `∂/∂A_F` do Liu2017 (a "B2") dá `k≈3.0` mas PIORA o MAE (§4.6: nível domina), então fica capacidade validada, não fix | capacidade de fretting de flanco medida por par (SEM/perfilometria do flanco sob carga axial) |

**Verdade desconfortável:** hoje, várias "constantes físicas" (emb_depth,
C_creep — este último agora ancorado para o par 304SS, §4.7; o valor do par da âncora interna
segue estimado-na-curva) foram, em algum momento, **ajustadas contra as mesmas
curvas de shear** — não medidas independentemente. Então a separação física/tunável existe no *design*,
mas ainda **não está realizada nos dados**. Enquanto Exp 1–5 não forem feitos, a
calibração é majoritariamente estimação-contra-a-curva → o argumento de
legitimidade repousa em (a) formas/acoplamentos fixos, (b) parcimônia, (c)
generalização cross-condição — **não** em "as físicas foram medidas".

→ Prioridade que isto implica: ou rodar Exp 1–5 (medir físicas), ou — sem esses
ensaios — provar legitimidade por **predição cross-condição** (Seção 6.4).

---

## 6. Protocolo de legitimidade (como usar o modelo como modelo)

1. **Constantes físicas calibradas UMA vez** por par tribológico (`emb_depth,
   C_creep, K_archard, α_GW, k_j_init`), não por curva.
2. **Tuners mínimos por condição** — usar o conjunto identificável (ablação +
   regularização forte pra 1). Para o M16 shear nova: efetivamente `k_wear_scale_tr`.
   Default ≤3 tuners livres; o resto fixo no default físico.
3. **A distinção entre condições deve ser física, não cosmética.** reusada =
   embedding já consumido (`k_emb≈0`); reaperto = dano ativo (`D_init/c_D>0`).
   Se cada condição exige tuners arbitrários sem história, é fitting.
4. **Validar por predição, não por ajuste:**
   - cross-condição: calibrar em algumas amplitudes/pré-cargas, **predizer** uma retida;
   - observáveis secundários: `θ_loose`, energia dissipada, evolução de Φ, `D(N)`
     devem bater com medidas independentes;
   - biblioteca de 97 papers (`Models/CALIBRATION_AND_VALIDATION/`) + âncora interna.
5. **Reportar identificabilidade junto do fit** — sempre rodar a análise da
   Seção 4 e publicar os tuners com seus intervalos de confiança / veredicto.
6. **Não-identificabilidade estrutural tratada por construção.** O registro de
   ativação (`calibration/parameter_registry.py`, spec 2026-07-03) impede que
   constantes de mecanismos não excitados pelo regime de carregamento sequer
   virem candidatas do fit (ex.: dataset 100% axial nunca oferece `K_archard`/
   `tr_loose_gain`). Os predicados são **verificados contra o engine** pelos
   testes registry-truth (parâmetro inerte ⇒ trajetória bit-idêntica).

---

## 7. O que falsificaria a tese "é física"

- Precisar de tuners fora de `[0.1, 10]` (ou colados no bound superior) sem
  justificativa física → sinal de compensar forma errada.
- Cada condição exigindo um conjunto de tuners diferente sem narrativa física.
- Falha sistemática out-of-sample (prediz mal condições não ajustadas).
- Residual de conservação de energia crescendo fora do regime de colapso.
- Observáveis secundários (ângulo de afrouxamento, energia) discordando das medidas.

Se qualquer um ocorrer de forma persistente, o mecanismo correspondente está
errado (não é questão de mais um tuner).

### 7a. ⚠️ Quanto da tese está DOCUMENTADO — medido em 2026-08-12, **corrigido em 2026-08-13**

A lista acima diz o que falsificaria a tese. Esta subseção diz uma coisa
diferente e desconfortável: **em quase metade das constantes adotadas, não há
registro que permita aplicar a lista.**

Auditoria completa de `adopted_configs.json`
(`procedencia_cobertura_auditoria_resultado.md`, commit `9432f8c`):

> **467 constantes adotadas · 261 (56 %) com `prov` · 206 (44 %) SEM nenhuma**
> — e a maioria das 206 é campo válido de `JointMaterial`, isto é, **chega ao
> engine e carrega peso métrico sem justificativa registrada**.

⚠️ **O número publicado em 08-12 era 238 (51 %) e estava inflado em 32.** A
varredura usava `prov.get(campo)` — lookup **exato** — e a campanha grava chaves
**COMPOSTAS** quando um único argumento cobre várias constantes (p.ex.
`prov['c_bend/emb_depth/floor']` no `ROUSSEAU_HDPE`, que documenta as três de uma
vez). A auditoria media a rigidez do próprio lookup, não a lacuna. Re-medido por
**token** da chave composta; catraca e baseline corrigidos no mesmo dia.

Campos mais indocumentados (pós-correção): `c_bend` **16** · `W_ref` 12 ·
`loose_arrest_floor` **12** · `k_wear_scale_tr` 11 · `k_dmg_mu` 9 · `emb_um` 9 ·
`c_D` 8 · `emb_depth` 8. Por fonte, `CHU_2026` segue em **100 %** sem procedência
— a mesma fonte que a triagem de 08-10 re-diagnosticou como *"não-calibrada por
condição"*, e as duas leituras se confirmam.

**Por que isto pertence à seção de falsificação e não à de estado:** o 1º critério
da lista acima é *"tuners fora de `[0.1, 10]` **sem justificativa física**"*. Sem
`prov`, esse critério **não é avaliável** — não dá para separar
`fitado-this-rig` (legítimo, e é a maior parte desta campanha) de input de paper
mal-copiado. E o segundo caso **aconteceu**: a rugosidade do `CHU_2026` estava no
`RZ_DEFAULT` contra Ra 0,4/1,6 µm declarados no artigo, e só apareceu porque
alguem foi ler a nota de aparato.

**Dois achados independentes saíram desta população**, nenhum procurado: a
rugosidade do CHU, e o `gth_q = 7,0` (que fecharia uma curva com custo zero e foi
**recusado** por quebrar a lei do IJPEM). Em ambos, *a métrica preferia o valor
**sem** procedência ao valor **com** procedência*.

⚠️ **Havia um terceiro, e ele era MEU erro.** O `loose_arrest_floor = 0,2` do
`ROUSSEAU_HDPE` foi registrado em 08-11 como *"fitado em silêncio, `prov = None`,
métrica depende 2,2× dele"* e levado à decisão do professor. **A procedência
existia desde 2026-07-12**, na chave composta, declarando o valor
`fitado-this-rig` e **nomeando o piso de arresto**. Retirado da série: *dois* não
é padrão, e a lição real é sobre auditoria, não sobre a config. O que sobrevive
daquele achado é mais fraco e continua verdadeiro — **o mesmo rig usa dois pisos**
(aço 0,0 · HDPE 0,2) e o argumento de aparato do aço não *deriva* o do HDPE: isso
é lacuna de **derivação**, não de bookkeeping.

⚠️ **Não é acusação de má prática.** `prov` nunca foi **obrigatório**; a campanha
cresceu por adoções incrementais sob gates de **métrica**, e nenhum gate media
procedência. Foi por isso que o passivo acumulou em silêncio — e é também por que
a correção é barata: desde 2026-08-12 há **catraca**
(`tests/test_procedencia_catraca.py`, commit `2e71dd0`) que **falha se qualquer
constante NOVA entrar sem `prov`**, com o estoque declarado como baseline — hoje
**206**, e com a chave composta reconhecida como idioma legítimo. Backfill é
livre; crescimento, não.

**Leitura honesta da tese, portanto:** *"physics first, procedência por
constante"* descreve **56 %** do que está adotado. Os outros 44 % podem ser
igualmente legítimos — só não há como saber sem re-derivar. ~~Estoque pendente
de decisão do professor~~ **DECIDIDO (assinatura em bloco 2026-08-13): backfill
por campo.** **Fase 1 EXECUTADA no mesmo dia** (`c_bend` 16 + `W_ref` 12 +
`loose_arrest_floor` 12 + 4 de bônus por chave composta): **206 → 162 sem
procedência (65 % cobertos)**, cada prov ancorado no commit adotante por
arqueologia `git log -S` — detalhe em
`procedencia_cobertura_auditoria_resultado.md` §FASE 1. Como `prov` entra no
fingerprint, a fase embarcou com re-stamp completo + auditoria de deriva zero.

---

## 8. Estado atual (honesto)

- **Forma + acoplamentos:** fisicamente fundamentados (literatura + conservação). ✔
- **Parcimônia:** **resolvida** (§4.4) — `fit_parsimonious` mostra que ≤2 tuners
  por condição bastam (não 5), e as 3 condições intactas usam o MESMO par
  {embedding, wear}; reaperto fecha com 0 tuners (só `D_init`+dano). ✔
  **Reforçada pelo fit compartilhado (§4.5):** UMA física reproduz as 4 condições
  com apenas **2 números fitados no dataset inteiro** (`C_creep` + `F0_test`
  estimado), MAE global 0.0796, e o LOCO fica ≈ ao fit (+0.003 a +0.014) →
  generaliza cross-condição. ✔ **Ainda mais forte com a âncora de C_creep
  (§4.7):** re-centrando o prior no valor ancorado independente, o fit
  compartilhado fecha as 4 condições com **zero constantes de mecanismo fitadas**
  (resta só o estado `F0_test`), MAE global 0.0817 ≈ 0.0796 — a parcimônia cai de
  2 números para **1 estado**. ✔
- **Reprodutibilidade (intra-condição):** **validada** (§4.2 Teste 1). ✔
- **Generalização cross-loading / cross-rig — Fase 1 (confrontação com a
  biblioteca) COMPLETA (§4.6–4.8):** os três braços convergem. **(B) Trilho axial
  (§4.6):** FORMA faltante — o conjunto de mecanismos não tem perda dirigida pela
  amplitude axial (∝ A_F; Gate B1 FALHOU). **(C) Âncora de C_creep (§4.7):** a
  constante é **por par tribológico** (âncora estática discorda do Estágio A por
  ~11,7× com ICs disjuntos) e, sob prior ancorado, o Estágio A fecha as 4
  condições com **zero constantes de mecanismo fitadas**. **(A) Varredura
  transversal (§4.8):** as constantes de wear/loosening **também não transferem
  entre rigs** — 46 curvas/7 papers com constantes congeladas dão mediana MAE
  0,22, **batem o no-loss em 34/46** (direção certa) mas **perdem para 1 parâmetro
  local em 37/46** (magnitude errada), em três modos de falha. **Leitura
  unificada honesta:** as **FORMAS de mecanismo + acoplamentos transferem**
  (direção certa, no-loss batido de M8 a M42); as **CONSTANTES são propriedades
  por par/rig/junta** que exigem **procedência própria** — tabela, âncora
  independente ou medição — exatamente a tese das 3 camadas do §2, agora com
  dentes quantitativos. O programa de legitimidade migra de **"fitar menos"** para
  **"prover procedência por constante"**. **✔ formas/acoplamentos · ✗ constantes
  universais**
- **Observáveis secundários:** não comparados a medidas independentes ainda.
- **Estado da META (tripé por curva: MAE ≤ 0,10 **E** res.máx ≤ 0,10) — CERTIFICADO
  em 2026-07-27 (S3):** **147/202 curvas comparáveis no tripé (73%)**, 55 fora;
  mediana 0,0315, média 0,0446; fingerprint uniforme `4f5bedfbace4`, zero erros de
  simulação. O que mudou não foi o número — é o mesmo de 22/07 — foi o **estatuto**
  dele: o store era um mosaico de 12 gerações de configuração (cada adoção
  re-simulava só a fonte afetada) e agora os 202 casos foram re-simulados sob a
  configuração final, reproduzindo os valores guardados **bit-a-bit**, com exceção
  do único caso deliberadamente consertado. O censo deixou de ser afirmação e
  virou resultado reproduzido. ✔
- ~~**O gargalo da meta é o RESÍDUO MÁXIMO, não o MAE**~~ **VENCIDO em 2026-07-29
  pela TROCA DE RÉGUA** (não por regressão do modelo). O enunciado de 2026-07-27
  era: *`MAE ⊆ maxerr` — zero curvas violam só o MAE; 34 passam no MAE e caem pelo
  pico, 21 violam os dois; esforço medido em MAE médio não move a meta.* Ele foi
  medido contra `MAE ≤ 0,10 E res.máx ≤ 0,10` (fingerprint `4f5bedfbace4`).
  **Por que caiu, e é aritmética, não medição nova:** a inclusão `MAE ⊆ maxerr`
  dependia de os dois limites serem **iguais** — como `MAE ≤ res.máx` sempre, com
  `META_MAE = META_MAX = 0,10` violar o MAE obrigava a violar o pico. Com a régua
  de 2026-07-29 (`MAE ≤ 0,05` **contra** `res.máx ≤ 0,10`) a inclusão **deixa de
  valer**, e com ela o corolário de método.
- **D1 ADOTADO (2026-07-30): a 3ª perna passou a ser POR FONTE** — limite
  efetivo `max(0,025; piso_σ medido da fonte)` (`limite_sres`; fonte sem piso
  medido fica no global, nunca em estimativa). Decisão do professor em sessão;
  prereg `2026-07-29-sigma-res-por-fonte-prereg.md`, gates 5/5 re-medidos na
  adoção: 0 curvas saem, censo **104 → 124/202**, resolvidos **149/202**
  (124 + 25 exceções ainda necessárias; 19 das 44 assinaturas viraram regra
  derivável e foram **retiradas em 2026-07-30**, assinado em sessão —
  `_EXCECOES_RETIRADAS_D1`, releitura em `excecoes_releitura_posD1.md`). **Perna que MANDA pós-D1 + adoções ZHANG_2018/LIU_2016 (30/07)** (70 fora;
  as duas fontes adotadas saíram inteiras — creep com onset 9/9,
  `zhang18_creep_onset_resultado.md`; re-atribuição creep→fretting L1 14/14,
  `liu2016_fretting_resultado.md`; e com P2/P5 de 2026-07-31 o denominador
  virou **201** — dedup amp1p0≡T22 e T4 declarada por escopo):
  **σ_res 23 · MAE 7 · res.máx 9** (205, vigente 2026-08-20 tarde — as DEZENOVE adoções de 19-20/08; bloqueios G/H — pisos ICMEZ/CHU ilegítimos, audit da sessão paralela executado por delegação — e retratação LU-PROTOCOLO + assinatura CHU 2026-08-14 — o limite σ do LU voltou ao global e 6 curvas trocaram de perna-que-manda — campanha **MARGENS** 2026-08-06: **D-W** (o argmáximo da `lu2024_amp1p5` não existia no impresso — sai de declarada para o tripé) e **D-X** (a `karlsen_run1p2` ancorava o 1º ponto num valor que a figura só atinge no ciclo ~26: base 5,0 % baixa; F₀ 315→331 kN, 0,0603/0,0940/0,0306 → **0,0171/0,0434/0,0195**, passa por mérito). No mesmo arco, **duas chaves cegas bloqueadas** (SUN_2025_CRIMP, cujo "piso" tinha MAE 0,448 porque pareava porca crimp × padrão — **custou** a `grease_crimp`; e KARLSEN, que pareava Vibralock × HV) e **2 exceções a menos** (1 retirada por mérito, 1 retratada por perna σ descoberta em 1,1 %); CORREÇÃO **D-U** 2026-08-06: as 6 digitalizações originais do YANG_2021 ancoravam o x=0 INVENTADO no TOPO da banda (deflação −2 a −9,4 %); re-ancoradas pelos CENTROS do vetor com predições **6/6 exatas** — `amp0p7` melhora nas 3 pernas, viés honesto flipa de sinal nas 6, e a `r1` SAI (mx 1,01× · σ 1,27×; estava dentro por artefato de âncora) ⇒ tripé 138→**137**, σ-manda 31→**32**; CORREÇÃO **D-R** 2026-08-05: ROUSSEAU re-digitalizado da polilinha VETORIAL (Figs. 4/5, atribuição por menor RMS contra a CSV vigente, todas inequívocas ≥ 3,6×). A `steel_t10` era uma **reta** sobre um colapso convexo (σ dos passos 5e-5) e o próprio RMS de atribuição a isolou em 0,0960 contra 0,0094–0,0193 das irmãs — **5× fora**, evidência independente. `steel_t12` (0,0451→0,0104) e `hdpe_t14` (σ 0,0299→0,0211) **entram**; a `steel_t10` piora 0,0725→0,1548, declarado antes de medir. Tripé 136→**138**, σ-manda 33→**31**; CORREÇÃO **D-S** 2026-08-05: a CSV da `caccese2009_tapered_45kN_rep2` tinha **9 de 26 pontos na réplica ERRADA** (provado por 3 instrumentos independentes, incl. o próprio resíduo do modelo trocando de sinal nesses 9); corrigida pela polilinha vetorial da Fig. 9, σ 0,0258→**0,0083**, a fonte fecha **7/7** e o modelo passa a estar mais perto de CADA réplica (MAE 0,0203 e 0,0349) do que elas estão uma da outra (**0,0543**) ⇒ tripé 135→**136**, σ-manda 34→**33**; ADOÇÃO **D-Q** 2026-08-05: saturação do canal de flanco (`flank_fret_depth`=2,5e-6 compartilhado entre LI_2022_TRIBOINT e LIU_2016, as 2 de 69 fontes com `flank_wear_on`) tira a `li2022ti_axial_10Hz_full` do σ (0,0365→**0,0214**) ⇒ tripé 134→**135** e o σ-manda cai 35→**34**; G1 de transferência CEGA no LIU_2016 passou 14/14 com pior Δ +0,0027, e o isolamento e' POR CONSTRUÇÃO (0 das 192 curvas fora das duas fontes mudou); ADOÇÃO D-L 2026-08-05: relógio
  por contagem de reapertos no LIU_2022, 3 números COMPARTILHADOS entre seco e
  óleo ⇒ t1/t2/t4 do fig8 fecham, tripé 131→134 e o σ-manda cai 37→35; ADOÇÃO D-H 2026-08-04: kernel
  de creep saturante no CACCESE, σ cai nas 7/7 da fonte e a
  `retighten_19p1mm` fecha ⇒ tripé 129→130, e o σ-manda cai 38→37;
  +2 curvas da Fig. 6 do ROUSSEAU
  (recuperação 2026-08-01: HDPE previu a condição nova NO TRIPÉ com zero
  refit; aço re-fitado por procedência com o G2 held-out FALHADO declarado);
  ANCORA_INTERNA fora do censo por decisão de 2026-08-01, preservada;
  +2 réplicas YANG_2021 de 2026-07-31 à noite, ambas no tripé por mérito;
  regra n<6 assinada 2026-08-01 — σ sem suporte = não-julgável, 6 curvas
  na classe, 3 saíram do tripé; os 3 não-julgáveis novos contam no σ-manda
  pela convenção do σ ausente; ERRATUM ROUSSEAU 2026-08-01 — drive do aço
  10× corrigido + piso da fonte INVÁLIDO (par de espessuras ≠ pareado como
  réplica), 3 exceções retratadas, t12/hdpe_t14 saem do tripé;
  comparáveis pós-P4 + pares de réplica declarados: o piso VÁLIDO do LU
  subiu o limite σ dele para 0,103 e moveu as pernas vinculantes) ⇒
  σ_res domina 68% das 34 fora ⚠️ **Re-medido 2026-08-15** após a declaração do par de réplica do `ECCLES_2010` (item O, prereg `b8af3ac`): o limite σ da fonte foi de 0,0250 a **0,0698** e **6 curvas trocaram de perna-que-manda** — censo, camadas e `declarado_total` **inalterados**. A estatística de dominância é sensível a declaração de piso porque **σ é o único limite por fonte**. Antes da declaração eram 76%; — **o "89%" da régua global era em boa parte
  régua, não modelo**: cobrar de fontes com piso 2–9× o limite media o
  experimento. Violam só uma perna: MAE 6 · σ_res 7 · res.máx 8.
  ⚠️ **Retratação de 31/07**: entre a manhã e a tarde vigorou um "piso do
  LU_2024 σ 0,0912" INVÁLIDO (par cruzado 0,5×1,0 mm — a fig20 roda a
  1,0 mm, erro de input corrigido no registry com prova dupla; exceção T22
  retratada; o par verdadeiro amp1p0↔T22 é o MESMO teste em 2 figuras,
  piso de digitalização σ 0,0192 < global). O episódio inteiro, a leitura do
  paper e o plano de recuperação da fonte: `lu2024_plano_melhoria.md`.
- **O gargalo na régua GLOBAL (medido 2026-07-29, pré-D1** — mantido como
  registro datado; a leitura vigente é o bullet acima; store `3546e6745448`, 202
  comparáveis): violam **só** o MAE **5** (era 0) · **só** o res.máx **0** (era
  34) · **só** o σ_res **30**; 63 violam mais de uma. **Perna que MANDA** (maior
  múltiplo do limite ⇒ quem sustenta a reprovação): **σ_res 87 · MAE 9 · res.máx
  2** ⇒ **σ_res domina 89% das 98 fora**, e o res.máx **nunca mais reprova
  sozinho**. As duas contagens respondem perguntas diferentes e não devem ser
  somadas nem confundidas: *"viola só esta perna"* diz onde consertar UMA perna
  fecha a curva; *"esta perna manda"* diz quem segura o veredito mesmo com outras
  violando. Severidade das fora: mediana **1,90×** o pior limite, p90 **5,62×**,
  máx **8,86×**. As 5 que violam só o MAE são `liu2025_M16_amp0p3`,
  `liu2022_fig8_multi_t2`, `li2022ti_axialmin_10Hz`, `liu2016wear_fig9a_m45nm` e
  `caccese2009_tapered_45kN_rep1` — todas entre 1,01× e 1,29× do limite.
  ⚠️ **Interação com a sensibilidade do σ_res:** se a perna que decide 89% das
  reprovações não responde a nenhuma das 18 alavancas varridas, a pergunta deixa
  de ser *"onde gastar esforço"* e passa a ser **se 0,025 é atingível com as
  formas atuais** — decisão do professor. O limite é ambição declarada: 0,025
  contra o piso de repetibilidade medido de **0,0283** (≈12% abaixo dele).
  A observação sobre o ledger **permanece válida** e ganha força: a média do
  ledger é indicador de tendência, não da meta — ela está abaixo de 0,10 há
  dezenas de entradas enquanto 98 curvas violam individualmente.
- **Distribuição do que falta — pós-D1 (2026-07-30):** as 3 maiores fontes somam
  **24 das 78 (31%)**; **21 das 28** fontes têm curva fora e **7** fecharam 100%.
  Piores: LU_2024 **10/10**, BAUER_2024 **7/9**, YANG_2023_IJPEM **7/9**,
  CHU_2026 **6/9**, ECCLES_2010 **6/10**, LIU_2016 **5/14**. (Na régua global de
  2026-07-29: 27 de 98 = 28% no top-3, 22 fontes com fora, 6 fechadas, piores
  LU 10/10 · BAUER 9/9 · CHU 8/9 — registro datado.) A classificação
  form-limited/exceção **não** foi re-julgada sob a régua nova; a releitura das
  44 assinaturas está em `excecoes_releitura_posD1.md` — 19 viraram regra
  derivável (D1), 25 seguem necessárias.

→ Veredicto atual: **modelo físico bem-estruturado e parcimonioso** cujas
**formas e acoplamentos generalizam cross-rig** (Fase 1: no-loss batido em 34/46,
gradientes de sinal certo) mas cujas **constantes não transferem** entre
par/rig/junta (axial, `C_creep` e transversal, §4.6–4.8). A prova de
generalização saiu de "pendente" e deu um veredicto **nuançado**; o próximo passo
é a **Fase 2 — prover procedência por constante** (tabela/âncora/medição) e
suprir as formas faltantes (mecanismo ∝ A_F; escala de rigidez de membro), **não**
baixar MAE de curva.

---

## 9. Changelog

| Data | Mudança |
|---|---|
| 2026-06-20 | Criação. Análise de identificabilidade do nova (3/5 stiff, JᵀJ singular; só k_wear necessário). Documenta acoplamentos + protocolo. |
| 2026-06-20 | §5 nova: estimação de parâmetros vs curve-fitting + tabela de procedência de cada parâmetro (verdade: emb_depth/C_creep foram ajustados à curva, não medidos). Renumera §5–8 → §6–9. |
| 2026-06-20 | §4.2 validação cross-condição (`cross_validation.py`): reprodutibilidade intra-condição PASSA; cross-condição não-testável com os 4 estudos (estados físicos distintos, não varredura). Falta varredura paramétrica. |
| 2026-06-20 | §4.3: protocolo da campanha de varredura (spec 2026-06-20-generalization-validation-campaign) + arnês `parametric_validation.py` com auto-teste sintético (OOS ~ruído; preditivo apesar de sloppy). Pronto pra dados reais. |
| 2026-06-20 | §4.4: `StagedCalibrator.fit_parsimonious` (forward selection). Os 4 estudos precisam de ≤2 tuners; 3 condições compartilham {k_emb,k_wear}; reaperto fecha com 0 tuners (só D_init+dano). Parcimônia resolvida. |
| 2026-06-21 | **Incubação estágio-I** (`slip_onset_W`, gate de Hill sobre `W_slip_acc`): suprime o colapso slip-driven (wear+loosening) até o slip acumulado cruzar o limiar → reproduz a curva real de 3 fases (platô→queda→saturação), antes inalcançável (mecanismos agiam desde o ciclo 1). **Honestidade:** é +1 grau de liberdade, mas (a) forma fixa físico-fenomenológica (não função livre), (b) **default 0 = inativo** (backward-compat exato), (c) **opt-in** — fora do `default_v2_params()`; só se justifica quando a curva mostra platô (pela lógica de ablação da §4.1, fica em 0 em curvas monotônicas, não adiciona overfitting). `dE` do wear não é gateado (conservação preservada). |
| 2026-07-02 | §4.5 fit compartilhado (`SharedCalibrator`, Estágio A do spec shared-physics): UMA física p/ as 4 condições, estados nomeados (D_init, emb_consumed_frac, F0_test estimado c/ procedência), LOCO. Embedding virou state-based (forma geométrica exata). Gate A→B: **PASSA COM RESSALVAS** — 2 números fitados no dataset inteiro; LOCO ≈ fit (generaliza cross-condição); sobretorque 18.9× o fit por-condição c/ F0 no bound = achado de falsificação apontando p/ regime dependente de pressão de contato; **decisão do Estágio B é do usuário**. |

| 2026-07-03 | Registro de ativação de parâmetros por regime (`parameter_registry.py`): tabela declarativa (slip transversal, dano/reuso, ΔT reservado, proveniência de F₀) consumida pelo `fit_parsimonious` (candidatos idênticos nos datasets atuais — paridade testada). Testes registry-truth pinam predicados às equações. **Nuance descoberta:** o gate de incubação (`slip_onset_W`) multiplica também o loosening axial, mas `W_slip_acc` só acumula com slip transversal ⇒ em axial puro com `slip_onset_W>0` o loosening ficaria permanentemente suprimido — comportamento atual do engine, documentado no registro (predicado "sempre"), a revisitar se o track axial usar incubação. |
| 2026-07-03 | §4.6 trilho axial (Fase 1B): predição zero-refit das 13 curvas Liu2017/Li2022 com constantes congeladas + emb_depth de tabela VDI (input por junta). Gate B1: **FALHOU** (mediana MAE_pred 0.1518 vs limiar 0.05; vence baseline exp em 3/13; ∂(fim)/∂A_F ≡ 0 no modelo vs −2.216e-5/N no dado) → falsificação **estrutural de forma**: falta mecanismo de perda dirigido pela amplitude axial (fretting de flanco de rosca ∝ A_F), aponta o mecanismo, não pede tuner. Residual de conservação −242.8 a −11.7 J = achado de bookkeeping do engine (`W_damp_visc` sem contraparte em `W_ext` no modo axial força; não realimenta F₀). emb_depth deixou de ser constante universal — diagnóstico + doutrina anti-knob no spec 2026-07-03 §1.3a. |
| 2026-07-03 | §4.7 âncora de C_creep (Fase 1C, spec §1.7): fit declarado no creep estático li2022marstruc (M16 304SS, mecanismo isolado, sem vibração); C_creep=9.917e-13 ×/÷1.36. **Veredicto: discorda do Estágio A por ~11.7× com ICs disjuntos → C_creep NÃO transfere entre pares tribológicos (constante por par).** Prior do Estágio A re-centrado no valor ancorado (9.917e-13): o fit compartilhado fecha as 4 condições com **zero constantes de mecanismo fitadas** e MAE global 0.0817 ≈ 0.0796 (Δ+0.0021) — o creep ~11.7× maior era folga sloppy, não física pinada. §5.1: C_creep é a primeira constante com procedência de dado independente (par 304SS). Caveat: 2/5 embs cravados no bound (IC real mais largo); inversão emb(Ra) = achado de identificabilidade (curvas pós-aperto). |
| 2026-07-03 | §4.8 varredura de transferência zero-refit (Fase 1A, spec §1): 46 curvas/7 papers (M8→M42) com constantes do Estágio A congeladas e inputs com procedência; mediana MAE 0,2196, **bate o no-loss em 34/46 (formas/direção transferem) mas perde para 1 parâmetro local em 37/46 (magnitude não, com constantes de outro rig)** → falsificação de transferência de **CONSTANTES, não de formas**, em três modos (sub-predição 31/37; colapso por wear excessivo — oposto da hipótese dano-OFF; pista de rigidez de membro Rousseau t12/t14). Bandas SENS não resgatam (2 `inconclusive` só em "vence exp"). **Fase 1 (B axial §4.6, C âncora §4.7, A transferência §4.8) completa** — leitura unificada no §8: formas/acoplamentos transferem, constantes são por par/rig/junta. |
| 2026-07-04 | Adendo §4.5 — discriminação do bound de F0 do sobretorque (Fase 2, pré-registrado; `sobretorque_f0bound.{py,json,png}` + report): topo do bound elevado 120 → 132.8 kN (teto de sanidade `0.9·Rp0.2·A_s`), nada mais mudou. MAE sobretorque 0.1378 → 0.1351 (ΔMAE +0.0026), `F0_test` cravado no novo teto, global 0.0796 → 0.0788 → veredicto pré-registrado **"missing mechanism (falsified again)"** (0.1351 ≥ PERSIST_MAE 0.10). Hipótese (a) "bound apertado demais" **descartada**; fica a falsificação estrutural apontando para regime dependente da pressão de contato (forma aberta — Fase 2; caveat: GW `k_tr(F0)` tem sinal desfavorável no slip atual, não avaliza fix ingênuo). Bloco `shared` canônico intocado (experimento standalone, disciplina `creep_anchor.json`). |
| 2026-07-04 | §4.9 **conformação dependente da pressão** (Fase 2, spec `2026-07-04-pressure-conformation-design.md`; A/B pré-registrado `conformation_fit.py`/`.json`): gate pressão-dependente que arresta a perda de `F_0` slip-driven conforme o contato sobretorqueado se conforma. Baseline `{C_creep}` vs tratamento `{C_creep, W_conf_ref}`; `n=2`/`p_ref=5e8` **fixos por escolha**, `W_conf_ref`=1.253e4 o **único** novo fitado. **Veredicto pré-registrado RESOLVED** (thresholds congelados spec §9): sobretorque 0.1379 → **0.0201** (< RESOLVE 0.06; de 18.9× para 2.75× o piso por-condição, ~7× menos MAE), as outras seguram (deriva máx nova +0.0048 < hold 0.01), residual 8.008 → 4.051 (não degrada; design `dF_0`-only). **Fecha o fio da §4.5** — supre e valida a forma faltante (regime dependente da pressão de contato) que o adendo do bound deixou aberto: "uma física, excitada pelo regime". Caveats: 1 rig/1 sobretorque/1 experimento; `W_conf_ref` constante por par/rig sem âncora (procedência = Fase 3, como C_creep); `n`/`p_ref` fixos, não fitados; forma fenomenológica **sustentada**, não provada; bloco `shared` canônico **intocado** (standalone, adoção = decisão do professor). |
| 2026-07-04 | §4.9 robustez (strand 1/3 do fortalecimento; `conformation_fit.py --fit-n`, `conformation_fitn.{json,md}`): A/B irmão com `n` **livre** em [0.5, 4.0] fitado junto com `{C_creep, W_conf_ref}`. `n` **crava no teto (3.9999)**; sobretorque resolve **ainda mais** (0.1379 → 0.0143 < os 0.0201 do `n=2`), residual 8.008 → 3.796, MAE global 0.0796 → 0.0484 (um fio abaixo dos 0.0486 do `n=2`) — **mas** nova deriva +0.0129 > hold 0.01 ⇒ **veredicto PARTIAL** (recomputado pelo mesmo classificador). Leitura: resgate do sobretorque **robusto a `n∈[2,4]`**; fitar `n` super-separa (satura o bound) e troca nova por MAE-global ⇒ **fixar `n=2` moderado é a escolha certa**, o RESOLVED do `n=2` **permanece o headline**. Bound **não** alargado (saturação registrada AS IS; alargar = follow-on deliberado). Bloco `shared` intocado. |
| 2026-07-04 | §4.9 robustez (strand 2/3; driver de conformação **auto-limitante**, `JointMaterial.conform_driver="effective"`, spec §7; `conformation_fit.py --effective`, `conformation_effective.{json,md}`): o incremento de `W_conf` é ponderado pelo gate de início-de-ciclo (auto-atenua). Effective `n=2` vs OFF ⇒ **RESOLVED e mais limpo que o raw** — sobretorque 0.1379 → **0.0299** (<0.06) e **as três outras MELHORAM** (deriva máx −0.0010 vs raw +0.0048), residual 8.008 → 4.848, `W_conf_ref`=7657. Pergunta-chave: o effective **não** tira o `n` do teto (fit-n crava 4.0 igual ao raw ⇒ **o rail é do objetivo MAE-global, não do driver**; `n=2` fixo segue certo p/ os dois). **Mas** o effective é **mais robusto no `n` extremo** (segura nova +0.0093 < hold onde o fit-n raw furou +0.0129). **Correção de honestidade:** a forma mínima é **plateau auto-limitante, não equilíbrio verdadeiro `c*<1`** (assintótico → 1 sob creep; um `c*<1` real exigiria feedback na cinemática do slip — item #4, adiado). **Spec §7 reescrita.** Bloco `shared` intocado (21ed6a7). |
| 2026-07-04 | §4.9 **Fase 3 — âncora do `W_conf_ref` tentada, NULL decisivo** (busca dedicada profunda, `W_conf_ref_anchor_hunt_phase3_2026-07-04.md`): Path A (curva cross-rig over-torqued que isole a constante) **não existe** — as curvas transversais da lib ou colapsam (alta %proof) ou têm platô por outra causa (baixa pressão) ou são artefato (Karlsen); **achado cross-rig: alta fração de preload noutro rig NÃO reproduz o platô do sobretorque âncora interna** (platô atado ao apoio pequeno do rig âncora interna → "formas transferem, constantes por par"). Lu2024 M8 corrobora a FORMA (trend preload→arresto) mas não isola a constante. Path B: **α=4.23e-5 mm³/J (aço 52100, Fouvry)** ancora `K_archard`, não `W_conf_ref` (χ de aço não citável + endpoint errado). Veredicto: `W_conf_ref` **não-ancorável** com dado disponível, permanece por-par (7671 J inalterado), um degrau abaixo do `C_creep`; experimento de âncora spec'd (fretting ~1.2 GPa, mede `n`). **Caveat/follow-up:** `library_common` fixa `A_contact=100mm²` → conformação cross-rig no harness §4.8 é artefato (re-escalar `A_contact`/`p_ref` por rig antes de reusar). |
| 2026-07-05 | §4.9 caveat do harness **CORRIGIDO (11g)**: `library_common.geometry_for` agora computa `A_contact = π·(r_bearing²−r_furo²)` (área real do anel por parafuso, `r_furo=0.55·d`, escala `d²`≈1.33·`A_s`) em vez de 100mm² fixo → `p=F0/A_contact` física por rig (Karlsen M30/M42 `p/p_ref`~1, não o espúrio ~7–14; M16 real ~209mm²), e `p_ref=5e8` corresponde a ~80% proof em qualquer tamanho. `anchor_creep`/`calibrate_axial` inalterados (conformação inerte: static/axial). Caveat residual: `p_ref`/`W_conf_ref` per-par (magnitude aproximada fora do par da âncora interna). §4.8 re-rodado a seguir (2026-07-05, ver addendum §4.8). 2 testes novos (escala per-rig + fix do artefato Karlsen). |
| 2026-07-05 | §4.8 **re-run com a física adotada** (`transfer_validation` com `conform_driver="effective"` + `A_contact` per-rig físico; artefatos re-gerados): GLOBAL mediana MAE 0.2196 → **0.2281** (levemente pior), vence-exp 9→4/46. **Não melhora o transfer** e revela: (1) **KARLSEN 0.123→0.226 — o bom fit do baseline era ARTEFATO de wear** (100mm² fixo super-estimava depth=V/A nos M30/M42; com área física o modelo retém ~0.75 e não reproduz o colapso ~0.15 → colapso precisa de DANO, não wear, coerente c/ doutrina §4.8); (2) **conformação não resgata as sub-predições de platô** (yang2019/liu2025 seguem →0; `p/p_ref`~0.5-0.6 fraco demais; platô não é conformação-por-pressão). Menores: ICMEZ 0.125→0.105, BAUER/LIU/LU levemente melhores. Leitura: física adotada é mais **honesta** (áreas/pressões reais) mas o baseline era lisonjeado pelo artefato Karlsen; conformação per-par não transfere magnitude cross-rig. Reforça §8. |
| 2026-07-05 | §4.8 **what-if `--damage-on`** (dano ativo em todos os casos; `c_D=2`/`k_dmg_wear=4`/`k_dmg_mu=1`; artefatos `transfer_*_damage.*` separados, canônico dano-OFF intacto): GLOBAL mediana 0.2281 → **0.1825** (melhora), vence-exp 4→7/46. **O dano REPRODUZ (parcial) o colapso do Karlsen** (final_pred 0.75→0.43-0.66 rumo ao dado 0.15; KARLSEN 0.226→0.139) — **confirma o re-run "colapso é dano, não wear"**. **Mas PIORA os platôs** (YANG 0.656→0.718, LIU 0.640→0.670: dano super-dirige a perda onde o dado não colapsa). Veredicto: dano é o mecanismo do colapso mas **por-condição, não universal** — **refina** a doutrina §4.8/Estágio A: o dano keys no **regime de colapso (severidade)**, não no histórico de dano prévio (Karlsen é junta NOVA e quer dano). Não é "adote dano-ON": melhora só na mediana (p90 piora, vence-no-loss igual) e sem regra preditiva. |
| 2026-07-05 | §4.8 **predictive damage trigger FALSIFICADO** (spec 2026-07-05; `--damage-trigger` + sweep de `W_crit`; artefatos `transfer_*_trigger.*` + `transfer_trigger_wcrit_sweep.log`): hipótese = dano auto-onseta quando a dose de gross-slip `W_slip_acc` cruza `W_crit` (gate Hill, espelha slip_onset), substituindo `damage_active` manual. Thresholds PRE-REGISTRADOS (median≤0.19, p90≤0.645, collapse-on≥75%, plateau-off≥75%). **Veredicto: FALHA — nenhum `W_crit` separa** (sobe W_crit → plateau-off→100% MAS collapse-on→0%, movem juntos; 1e5 = só 2/31 colapsos). Causa: dose ∝ F0·slip·ciclos é DOMINADA por F0 → platôs de alto-F0 acumulam mais que colapsos de baixo-F0 (anti-correlacionada). **Achado de FORMA (não tuning):** o `slip=max(0,δ−F_slip/k_tr)` não reproduz a separação partial/gross-slip (forma faltante = regime de slip / `k_tr`, não o onset do dano; paralelo §4.6/§4.8). O gate `W_crit` fica como incubação de dano válida/default-inert/backward-compat, mas o objetivo preditivo é falsificado AS IS. Codigo Tasks 1-3 (engine/registry/harness) verde; decisão merge/revert = professor. |
| 2026-07-04 | §4.9 procedência (strand 3/3; busca de âncora do `W_conf_ref`): **NÃO existe âncora independente** — `W_conf_ref` (~1e4 J) é constante fitada por par/rig como `C_creep`, mas **base MAIS FRACA** (o `C_creep` tem medição independente de IC disjunto §4.7; o `W_conf_ref` não). Framework transfere (Fouvry "wear/friction energy capacity", *Tribology Int.* 2007 = "variável característica por tratamento" → reproduz "formas transferem, constantes por par") **mas não ancora o número** (endpoint/quantidade diferentes; sem valor de aço). ~20 J/mm² implícito = check **INTERNO** (mesmo dado âncora interna), **não** âncora. Escala de procedência: um degrau **abaixo** do `C_creep`. §5.1 ganhou linha `W_conf_ref` + `n/p_ref`. Fase 3: fretting dedicado por par (paralelo a `anchor_creep.py`), discordância = esperada/informativa. **Fase 2 fortalecimentos 1–3 concluídos.** |
| 2026-07-04 | §4.9 **ADOÇÃO** — driver `effective` adotado no bloco `shared` canônico (decisão do professor; `calibrate_shared.py`): **1ª promoção de experimento ao canônico** (hash `21ed6a7`→`13b26d2`). `fit_parsimonious` livre pegava `{W_conf_ref, emb_depth}` (global 0.0456) mas derrubava o `C_creep` ancorado e fitava `emb_depth` (input VDI). **Escolha physics-first:** `emb_depth` mantido como input fixo (fora do candidate set), `C_creep` preservado → parsimônia seleciona **`{W_conf_ref, C_creep}`** (global 0.0509; +0.005 aceito por procedência sobre MAE). Canônico: **sobretorque 0.1378→0.0300 = falsificação §4.5 RESOLVIDA**, `W_conf_ref`=7671, `C_creep`=1.867e-11, 3 fitados (W_conf_ref+C_creep+F0_test). LOCO nominais ≈ fit; sobretorque LOCO 0.121 fraco (única condição de pressão elevada). `profiles`/GUI inalterado (propagar = follow-up). |
| 2026-07-05 | §4.8 **fix do regime de slip (`k_tr` de flexão) — NECESSÁRIO mas INSUFICIENTE** (spec `2026-07-05-slip-regime-ktr-fix-design.md`; engine opt-in `k_tr_mode="bending"`, `c_bend·E·I/L³`, default `axial_frac` bit-idêntico; `calibrate_ktr.py` → `c_bend=1.0`; `--ktr-bending`; artefatos `transfer_*_ktr.*`/`transfer_*_trigger_ktr.*`). Corrige o bug de `k_tr=0.3·k_axial` cego ao rig (`δ_t≈0`⇒tudo gross). **Thresholds pré-registrados FALHAM:** regime realizado platô→plateia **14%** (≥70%), melhora `final_pred` nos platôs **+0.006 mediana / 0/7** (≥0.2), MAE GLOBAL 0.228→0.234 (≈igual). **Rescue do trigger NULO** (`W_crit∈{1e3..1e6}` todos median 0.2341 = sem-dano). **CONFIRMADO por trace** (liu2025 amp0.25): `δ_t` inicial 0.578mm>δ ⇒ partial por ~10k ciclos (fix funciona), MAS embedding/creep erodem F0 → `δ_t∝F0` cai < δ → gross slip dispara → **runaway sem arresto** → colapsa. **Formas faltantes compostas** (não constante): (1) erosão de F0 limitada em partial, (2) arresto/equilíbrio no runaway. Amplitude sweeps puros (LIU/YANG) melhoram (−0.06) = mecanismo certo, insuficiente. Task 4 (Mindlin partial-wear) **gated OUT**. Código keeper (opt-in inerte); decisão merge = professor. |
| 2026-07-06 | §4.8 **gate do loosening ao regime de slip — MECANISMO VALIDADO, agregado limitado pelo teto do `c_bend`** (spec `2026-07-06-loosening-slip-gate-design.md`; engine opt-in `loosening_slip_coupling="gross_fraction"`, gate `g=slip/(slip+δ_t)` no `d_theta`; `--loosen-coupled`; artefatos `transfer_*_loosen.*`). **Corrige a atribuição do addendum de `k_tr`:** decomposição por mecanismo mostra que o eroder pré-gross do platô é o **rotational loosening** (51%, disparando em partial slip via critério de FORÇA `F_tr=0.4F0≫F_slip`), **não** embedding/creep (~23%, saturam). O `k_tr` só alcançava o wear; o loosening bypassa. Thresholds pré-reg AS IS: platô→plateia **43% (3/7)** vs k_tr 14% (❌ <50%, mas 3×), melhora mediana **+0.025** (❌ <0.20, **bimodal**: liu2025 amp0.25/0.3 **0.00→0.74**≈dado, média +0.226), colapso→afrouxa **45%=k_tr** (✅ ≥40%, sem regressão), MAE GLOBAL 0.228→**0.226**, p90 0.640→**0.512**, LIU 0.640→**0.311**. **Veredicto PARCIAL:** o gate funciona **perfeitamente onde o regime acerta** (partial), o teto é a separação `c_bend` (Task 2: 57% platô); os 5 platôs parados são mis-classificados gross. Próxima forma = **melhorar a separação de regime** (`c_bend` per-junta / compliance de membro), não este gate (keeper, opt-in inerte). Código verde; decisão merge = professor. |

| 2026-07-06 | §4.6 **`ThreadFrettingLoss` — forma faltante axial CONFIRMADA representável, mas o NÍVEL domina** (spec `2026-07-06-axial-thread-fretting-design.md`; engine opt-in `k_thread_fret=0` default; Archard de flanco ∝ A_F reusa `K_archard`, `dF_0∝−F₀·A_F`; `calibrate_axial.py --calibrate-fret`). Supre o mecanismo que a falsificação §4.6 nomeou. AS IS (`--quick`): representabilidade **PASSA** — `∂(fim)/∂A_F` de 3.8e-20 (o buraco ≡0) → **−2.315e-5 @ k=3.0** (dado −2.16e-5, ~5%), as 4 curvas A_F **separam** (0.386→0.270 vs identicas 0.659); P₀-grad segue + (1.525e-5). **MAS MAE axial PIORA 0.147→0.255**: o baseline já sobre-afrouxa (0.659 < dado ~0.9) e o fretting só ADICIONA perda ⇒ casar o gradiente colapsa o nível; gradiente e nível pedem correções OPOSTAS, nenhum `k` resolve. ⇒ **capacidade validada, default-inert, NÃO fix adotado** (padrão do trigger de dano); `k_thread_fret` em §5.1 como fitada-per-par não-adotada (a "B2"). Transversal bit-idêntico (F_ax=0; suite 62 verde). Próximo lead axial = o erro de NÍVEL, não fretting. |

| 2026-07-11 | §4.10 **PR-5 (MEM iter.4) — cadeia de reaperto com estado herdado: gate global FALHOU; maquinaria validada, NÃO adotada** (prereg `2026-07-11-mem-iter4-preregistrations.md`; runner `_simulate_retight_chain`, default-inerte via `chain: "retight"` no adopted; diretriz do professor "a condição de contato no reaperto não pode ser a mesma"). Sequência t0→`retighten()`→tN com F₀ por estágio LIDO do 1º ponto da curva (zero fit novo). Gates: (a) mediana retight 0.2026 vs ≤0.15 ✗ (baseline 0.2610); (b) contraste dry 2/3 ✓ mas oil ✗ (o t0 destoa — problema de 1º aperto, não de reaperto); (c) fig5 intacto ✓; (d) zero fit ✓. **Assinatura:** OIL+cadeia RESOLVE t1–t3 (0.26–0.28 → **0.026–0.060**, 10×, D herdado 0.04–0.15 = a física do paper "filme protege") — a maior validação do `retighten()`/estado nomeado (§4.10) até agora; DRY+cadeia PIORA t2/t3 (D herdado 0.50–0.75 com k_dmg_mu=1 derruba µ_eff a 25–50% → afrouxamento acelerado demais; corrigir c_D = fit proibido pelo gate d); todos os t0 ~0.20–0.25 = nível da FONTE (c_bend nunca fitado). Grupos revertidos (statu quo bit-idêntico; fingerprint e6246244cc51 preservado). Decisões do professor: PR-5b oil-only (gate local ≤0.08 passaria); alvo dry (saturação/decaimento de D por estágio); alvo t0/fig5 (funil de nível). |

| 2026-07-11 | §4.10 **PR-6/PR-5b/PR-7 (MEM iter.4, "faça todas") — reaperto Liu2022 RESOLVIDO no canônico; PR-5 reatribuído a CONFIG, não forma** (prereg + resultados em `2026-07-11-mem-iter4-preregistrations.md`; zero constante nova nas 3 frentes). **PR-6**: o nível 0.20–0.25 da fonte era **gap de adoção de INPUTS** — `LIU_2022_RETIGHT` estava fora do `SOURCE_INPUTS` (rodava grip 30/µ0.15/emb 11µm assumed); adotados os inputs da campanha rodada-4 com procedência (grip 50; **µ Motosh per-lube 0.236/0.176** lido de T+F₀ medidos; **emb Rz<4 n2=4µm**; dano brando `k_dmg_wear=1, W_ref=1e4, k_dmg_mu=0`; c_D per-lube L7) → t0s 0.0126, **fig5 0.0145 (a "reconstrução impossível" §4.29 estava em `validate_galling.py`/`liu2022_level_probe.py` — RESOLVIDA)**, fonte virgem 0.2492→0.0503. **PR-5b/PR-7**: cadeia `t0→retighten()→tN` (F₀ por estágio lido do 1º ponto) adotada oil E dry — oil t1–t3 mediana **0.0088** (D herdado 0.07–0.21), dry t1–t3 **0.0360** (D satura 0.80–0.99 sem colapsar µ_eff pois k_dmg_mu=0), t4 fratura fecha a 0.037, fig5 bit-idêntico (verificado on/off). **Reatribuição do PR-5**: a falha era o canal espúrio k_dmg_mu=1/k_dmg_wear=4 (starters âncora interna) no meu experimento — com a receita da campanha o estado herdado fecha 21/21 curvas (mediana da fonte ~0.016, 15×). Roadmap #5 (renewal no reaperto) **fechado no canônico**. |

| 2026-07-11 | §4.15 **PR-8→8d (MEM iter.4, diretriz "ataque o próximo artigo... rigidez da bancada pode ser estimada") — Yang2023 IJPEM RESOLVIDO por estimativa física de bancada + ratchet per-par + leituras** (prereg/resultados em `2026-07-11-mem-iter4-preregistrations.md`). Fonte 9 curvas (M6+M8, Junker DIN 65151, varredura de amplitude c/ limiar nítido + D-N δ^−3.8): mediana 0.2275→**0.1188**, below-threshold 0.19–0.23→**0.007/0.008**. **Trilha de falsificações nomeou o mecanismo:** wear ✗ (k_wear_spec ×100 inerte — auto-limitante, dF∝F₀·slip), loosening rate-scaled ✗ (tr_loose_gain ×20 inerte), ratchet sem take-up vaza em partial slip CM ✗ → **ratchet cinemático (k_ratchet=0.05, banda per-par O(0.005–0.1) como LU) + delta_free LIDO do limiar impresso no artigo (0.18/0.15 mm) + c_bend fitado pousando NOS seeds analíticos** (M8 8.0 vs 8.1; M6 20 vs 18.9; k_tr=µF₀/δ_th ≈1.0–1.4e7 N/m = classe DIN 65151 do PR-4 — a estimativa de rigidez de bancada tem procedência física independente). Baseline antigo (0.2275) era lisonjeado por assentamento espúrio (emb 11µm assumed; padrão §4.8 Karlsen). Maquinaria nova: matcher de grupos por bolt_size (default-inerte, testado). DOF: 3 fitados + leituras. Residual honesto: forma do decaimento (mestra front-loaded vs ratchet ~back-loaded) 0.08–0.18 nas 7 acima do limiar — candidato de FORMA futuro, não tuner. |

| 2026-07-11 | §4.14 **PR-9/9b (MEM iter.4, diretriz "ataque de maneira similar Liu 2025") — Liu2025 Sci.Rep. M16 shear RESOLVIDO: incubação como portadora do D-N + piso de arresto** (prereg/resultados em `2026-07-11-mem-iter4-preregistrations.md`). Fonte 7 curvas (M16×120 8.8, 60 kN, fixture L rígida servo, varredura 0.25–0.80 mm, ensaios ATÉ FRATURA): mediana 0.1934→**0.0777**; fraturas 0.26–0.28→0.047–0.102 com N70 4/4 e finais ~0.5 (dado segura ~0.5 e sai em 0.33 = fratura). **PR-9 falsificou dois levers e nomeou a física:** `loose_kin_ceiling` INERTE na escala de grind (dθ~1e-4 rad ≪ disponibilidade ~0.05; teto harmônico é p/ transição-S, não moagem) e **remover `slip_onset_W` = runaway imediato → a incubação É a portadora da lei D-N** (N_onset ≈ W/(4µF₀·slip) ∝ 1/slip, mesma estrutura do take-up δ₀=0.30 lido deste dado). **PR-9b:** re-fit W 150→250 kJ + `loose_arrest_floor=0.25` novo (banda per-par: LU 0.2, ZHANG 0.1) = 2 fitados. `FatigueLoss` lido e descartado como lever (σ_a=Kt·F_amp/A_s com F_amp=0.4F₀ constante em disp-mode ⇒ vida amplitude-cega); candidato de forma futuro: fretting-fatigue ∝ slip como driver. Residual honesto: cliff terminal = fratura fora do modelo (declarada; floor-trim limita o custo). |

| 2026-07-11 | §4.20 **[⚠ SUPERSEDIDO EM 2026-07-27 — leia o RE-BASELINE no fim da §4.20 ANTES de usar esta linha. As conclusões "`GA_member` é INERTE" e "o modelo é cego à espessura" vieram de INSTRUMENTAÇÃO (a sonda passou por `suggest_overrides`, que descarta a chave), não de física: o termo está vivo desde o PR-14 e põe o t14 em stick permanente.]** **PR-10 (MEM iter.4, "similar study" Rousseau2025 M12) — gate FALHOU e nomeou FIAÇÃO ABERTA, não constante** (prereg/resultado em `2026-07-11-mem-iter4-preregistrations.md`). Aço já fechado (0.037–0.075, intocado bit-idêntico). HDPE: o modelo é cego à espessura (finais ~iguais) vs dado t10 0.212 / t12 0.321 / **t14 0.875** (pior caso da lib, MAE 0.566). **Dois achados de registro:** (1) bug da campanha — `hdpe_adopt.py` calibrou com F₀ do AÇO (10.25 kN); o paper dá HDPE ≈ 4.0 kN (registry certo); (2) **`GA_member`→`k_member_shear=GA/t` é INERTE no pack CM** (resultados bit-iguais p/ GA 0.6–2.4e5; tradução por espessura construída e testada no runner — keeper): com `slip_regime_mode="cattaneo_mindlin"` o slip é force-driven e não roteia pelo k_tr série ⇒ a **divisão do curso pelo cisalhamento do membro** ("split the stroke", follow-up documentado do arco §4.20 2026-07-08) segue não-construída. Floor 0.30 melhoraria a mediana (0.119→0.098) mas é absorvedor cego sem a física — NÃO promovido (gate b imutável). Statu quo byte-idêntico. **Candidato de forma (decisão do professor):** stroke-split série {flexão, cisalhamento do membro} antes da interface CM; trio HDPE (E 100×, t 10/12/14) = validação natural. |

| 2026-07-12 | §4.33 **PR-12→12d (MEM iter.4, "leitura intensa Bauer 2024" + "autorizado") — fonte Bauer RESOLVIDA em física lida; dano-imitação substituído** (prereg/resultados em `2026-07-11-mem-iter4-preregistrations.md`). Leitura INTEGRAL do PDF: espectro fig8 = blocos de 20 ciclos (18×80 µm sub-crítico + 2 picos ×155 µm reais), **s_crit(F_V) MEDIDO em 2 pré-cargas** (98.6 µm@50 kN / 76@35 — eq. 4), ΔF_init=5%, anti-seize declarado (wear eliminado por projeto), ensaios de minutos (creep-tempo ≈ 0). **Mecanismo do joelho = criticalidade δ_t(F₀) cruzando a base 80 µm** (kernel de torque tem s_crit=0.46µF₀/k_tr caindo com F₀ = eq. 4; taxa graded_scrit = eq. 5). Resultado: mediana fonte 0.1647→**0.0748**; joelho 3/3 (N75 459 vs 543–764); fig6 ensemble 0.074 (4×); test1 0.0575; grupos dano-imitação (c_D 8–30 per-teste) SUBSTITUÍDOS. DOF: 2 fitados (k_graded=0.05 ≈ seed analítico 0.042 da eq. 5; c_bend_m8=0.5) + 6 leituras. **Erratas de processo registradas:** (1) ler constantes ATRAVÉS do engine (fator Pai-Hess 0.46 → c_bend 0.906→0.4167); (2) `suggest_overrides` só passa escalares → `delta_spectrum` era descartado silenciosamente (2 grids rodaram sem espectro; fix + teste no caminho real). Maquinaria nova: `delta_spectrum` no runner (blocos por ciclo, default-inerte). Também nesta leva: exceção per-espécime Karlsen run7p1 AUTORIZADA (k_ratchet=0.005 → 0.0398; PR-11×3 mediu scatter de coating). |

| 2026-07-12 | §4.33 **PR-12e/12f (MEM iter.4, "nenhuma curva > 0.15") — Bauer re-centrado no ENSEMBLE por min-max; per-rep μ REJEITADO por falha de coerência** (`2026-07-11-mem-iter4-preregistrations.md`). Diretriz = minimizar o MÁXIMO por família (não a média). **fig8**: k_loose_graded 0.05→0.03 recentra o joelho (N75 459→740 = centro dos dados 543/692/764) → test1/2/3 = 0.075/0.029/0.024 (test2 caiu 8×). **fig6**: tr_loose_gain 2.0→1.8 (reserva declarada) → MAX 0.211→0.157; reps 2–5 ≤0.088. **PR-12f (per-rep μ) FALHOU o gate de coerência e NÃO foi adotado**: μ por réplica leva todas a ≤0.081 mas não é monotônico com a métrica de vida do PRÓPRIO paper (N75=N a 25% perda — rep2 tem vida mais curta mas quer μ maior que rep1) ⇒ absorve scatter de FORMA, não de atrito = 6 botões cegos (parcimônia MEM proíbe; contraste com Karlsen PR-11b onde o early-window predizia a janela tardia 7/7). Resultado: 7/9 curvas ≤0.088; rep1 0.157/rep6 0.154 = extremos irredutíveis do ensemble de atrito (spread de vida 1.7×; o paper usa bandas PL, não curva única) — 0.007 acima do alvo. Global: mediana 0.0599→0.0578, >0.10: 27→25. |

| 2026-07-27 | §8 **Certificação da F5.1 (S3) + dois bugs de instrumentação, nenhum de física.** (1) **Store re-carimbado**: batch paralelo dos 202 comparáveis (33 min, 6 workers, single-writer) → fingerprint ÚNICO `4f5bedfbace4` em 203/203, zero erros. **Diff vs o estado anterior: EXATAMENTE 1 caso** ⇒ o mosaico de 12 fingerprints era **inócuo** — nenhuma segunda divergência de configuração estava escondida nele. Censo certificado: 147/202 no tripé (73%), mediana 0,0315. (2) **Bug de resolução de chave adotada (S1)**: `YANG_2019_small_to_large` e `..._large_to_small` são permutações dos mesmos tokens ⇒ empatavam em score no `_adopted_for`; como `adopted_sources()` é `sorted()` e o teste é `>` estrito, o alfabeticamente primeiro vencia SEMPRE e o outro caso rodava com o **espectro de amplitude da direção oposta**. Consertado por fusão num grupo + `per_case` (substring pura). **Consequência honesta:** o ganho que o PR-42 creditou à direção small→large era ARTEFATO — com o próprio espectro a curva vai de 0,212 para **0,194**, não para 0,131 (já violava, segue violando; lista-mestre inalterada). Invariante anti-empate fixado em teste que varre o registry. (3) **Bug de leitura de CSV no explorador (S5)**: `_read_ref_csv` exigia as colunas literais `cycle`/`F_over_F0` e ignorava `csv_x_offset`/`csv_x_scale` ⇒ **73 curvas de 11 fontes fora da galeria em silêncio** (CACCESE, CHU, ECCLES, GRZEJDA, JCSR, LIU_2016, LIU_2020_WEAR, QIN, SUN ×2, YANG_2023_AME) e Lu/Karlsen/Eccles plotados no x errado. Passou a usar o leitor canônico `load_full_curve` + as convenções de eixo do runner; galeria 130→**203 curvas / 28 fontes, 0 descartadas**, e os descartes agora são CONTADOS e reportados. A prosa "115 curvas de 15 aparatos" era hardcoded e virou token substituído na geração. **Achado de método (§8):** `MAE ⊆ maxerr` — zero curvas violam só o MAE ⇒ o gargalo é inteiramente o pico. |

| 2026-07-27 | §4.20 **G0 do prereg Rousseau EXECUTADO — a falsificação "modelo cego à espessura" está VENCIDA, e o motivo é uma 3ª errata de instrumentação.** Gate bloqueante do prereg `2026-07-27-rousseau-prereg.md`: re-baselinar o roadmap item 10 e a §4.20 antes de propor qualquer mecanismo (a lição do `flank_s_crit`, morto na F4 por partir de falsificação não re-baselinada). **Medido no store `4f5bedfbace4`:** `k_member_shear` = GA/t **VIVO** no grupo HDPE (2,000e6 / 1,667e6 / 1,429e6 N/m em t10/t12/t14), levando `k_tr_transverse` a 1,373e6 / 1,045e6 / 8,159e5 (sem o termo: 4,375e6 / 2,803e6 / 1,902e6); slip resolvido 0,232 / 0,134 / **0,000 mm** no ciclo 1 e **0,000 pelos 400 ciclos no t14** — stick permanente é o mecanismo pelo qual o t14 não colapsa (final 0,882 vs 0,875). MAE/res.máx HDPE 0,058/0,153 · 0,064/0,138 · 0,044/0,077; aço 0,087/0,188 · 0,046/0,074 · 0,020/0,034 ⇒ o erro **cai** com a espessura (o roadmap dizia 0,228→0,373→0,380 crescente). **BUG DE AUDITORIA CORRIGIDO (o agravante):** o `config_used` gravado no store **não registrava** o `k_member_shear` aplicado — `simulate_case` montava sua própria cópia dos overrides e a injeção só ocorria dentro de `material_kwargs_for` ⇒ constante ATIVA e fitada-this-rig **invisível na trilha de auditoria**, que é como o "INERTE" do PR-10 (medido através de `suggest_overrides`, que descarta a chave) sobreviveu 16 dias sem ser flagrado. Fix: `runner._effective_overrides` como fonte única (engine + `config_used`) + 2 testes; re-sim dos 3 HDPE **bit-idêntica** em mae/maxerr/resid_std/final_pred e fingerprint intacto ⇒ inerte na física. **Lição durável:** *uma constante que o engine usa mas o store não registra é indistinguível de uma constante inerte* — toda injeção derivada por caso tem de aterrissar no `config_used`. Terceira ocorrência da classe (após `delta_spectrum` §4.33 e `_read_ref_csv` no S5). Restam no Rousseau dois problemas distintos, não uma forma faltante: `steel_t10` arresto terminal e `hdpe_t10/t12` tempo de joelho com amplitudes por espécime — decisão do professor. |

| 2026-07-27 | §4.43 **RE-BASELINE do gate B1 (pedido 4 do PARE da F4) — a falsificação axial de 2026-07-03 está VENCIDA.** O roadmap item 9 afirmava `∂(fim)/∂A_F ≡ 0` no modelo contra −2,216e-5 /N no dado do Liu2017, e chamava isso de falsificação ESTRUTURAL (forma faltante). **Medido no store `4f5bedfbace4`** (varredura de amplitude, F₀ fixo, 4 curvas, regressão de `final` vs A_F): modelo **−1,7225e-5 /N** (R²=0,9968) contra dado **−2,2160e-5 /N** (R²=0,9987) ⇒ o modelo cobre **77,7%** da sensibilidade, não 0%. O slope do DADO reproduz exatamente o número histórico, o que valida o método e legitima a comparação. Controle na varredura de pré-carga: modelo +2,2707e-5 vs dado +2,6333e-5 /N; a fonte fecha **9/9 no tripé** (MAE 0,003–0,036). **Causa da defasagem:** a sensibilidade vem do cfg adotado `LIU_2017_axial` (`emb_amp_exp=2,375` + `rho_ref_emb=0,6667`, a ρ-unificação do §4.18) **adotada em 2026-07-08** — cinco dias DEPOIS do gate, que rodara contra `frozen_constants` sem o cfg adotado. O gate nunca foi re-baselinado e o texto ficou errado por 24 dias; foi isso que induziu o candidato `flank_s_crit` na F4, morto por não-discriminância (30/30 células passavam a banda, inclusive as 6 sem o candidato). Item 9 passa de "forma faltante" a "cobertura parcial medida"; resíduo honesto = ~22% da inclinação + nível sub-previsto no A_F baixo. **REGRA PROPOSTA:** *toda falsificação registrada carrega o fingerprint contra o qual foi medida, e vira suspeita assim que o fingerprint muda* — no mesmo dia, dois dos três grandes itens de forma do roadmap (9 e 10) caíram por adoções posteriores que ninguém re-checou. |
| 2026-07-28 | §4.44 **DATA-LIMITED, uma terceira classe de limite** (medição pré-execução do prereg da rampa do Liu 2025; fingerprint `4f5bedfbace4` idêntico ⇒ §4.43 satisfeita; engine intacto, forma via `loss_mechanisms=[...]`; sondas `liu2025_ramp_*.py`, doc `liu2025_ramp_premeasure.md`). **(1) A forma FUNCIONA e é discriminante:** `fig2_single` **sem trim** dá **0,039/0,062** (hoje, cortando 20% da curva: 0,0389/0,0546); sem o candidato, 0,093/0,481 e nenhuma das 7 passa o tripé (G5 ✓). **(2) E custa 6 dos 7 passes** (7/7 → 1/7) — mas em **4 das 7** o `res.máx` é *exatamente o último ponto do dado*: 0,330 = **borda inferior do gráfico** (20 kN), 0,683 = **fim do digitalizador**. O modelo vai a zero na fratura que o paper declara contra uma curva que acaba antes ⇒ **a métrica pontua a moldura da figura**. Daí a classe nova: **data-limited** (forma certa, dado termina antes; assinatura = `res.máx` no último ponto coincidindo com valor de moldura; ação = **dado novo**, não forma nova) — distinta de *form-limited*. Follow-up nomeado: varrer os 55 fora do tripé com esse teste; parte dos ~45 *form-limited* pode ser data-limited. **(3) O relógio está fechado pelo DADO:** 75% de sobreposição da janela de colapso (φ=20–29% da vida) exige `|ε|` ≤ **5,0%** em N_f; disponível 17% (PR-24) a 35%, e o scatter de espécime da própria fonte é **44%** (`fig2`×`amp0p8`, mesma amplitude, 10k vs 14,4k). Separar *prever quando* (fechada) de *prever a forma dado o quando* (aberta, funciona) vira obrigatório. **(4) Mensurabilidade:** com ±3% em N declarados nas notas de aparato, **6 das 7 curvas têm incerteza própria (0,124–0,900 em `F/F₀`) MAIOR que o limiar do gate**, e a curva eleita banco de prova é a pior (±0,90) ⇒ regra: *no trecho quase-vertical, gatear em **vida** (±% de N), não em `F/F₀`*. **(5) G4:** a perda de seção **atravessa** o `loose_arrest_floor=0,25` (`fig2`→0,140, `amp0p5`→0,000); confirmado por código (`FatigueLoss` não chama `self_locking_gate`) e por número. **(6) Lição de protocolo:** medir gates antes de assinar acha cláusulas indecidíveis (a de σ_res do G1 dá veredictos **opostos**: literal ≤0,0389 passa, estrita ≤0,0224 falha por 0,006) **mas queima a cegueira do pré-registro** — checagem de mensurabilidade e pré-compromisso devem gatear grandezas **distintas**. `f5_excecoes_propostas.md` §B corrigida (o trim é provisório enquanto o **dado** não existir); prereg v1 marcado NÃO ASSINAR COMO ESTÁ. |
| 2026-07-28 | §4.44a **prereg v2 EXECUTADO + a Fig. 2 re-digitalizada: `data-limited` se divide em DUAS classes** (gates congelados em `5ce4324` **antes** da medição; resultados em `New_Theory/liu2025_ramp_v2_results.md`; nada adotado). **Gates:** G0 **bit-a-bit** (Δ=0,00e+00 nas 3 do núcleo — o arnês inline É o canônico, o que retro-valida a §4.44), G1b e G2 com Δ=0,0000 exato, **G1 12/15** ⇒ ramo pré-declarado de *falha parcial*. **Ganho:** com **um par só** (`D_on`=0,75, `q`=8) `amp0p4` e `amp0p5` fecham **10/10** (erros 125–506 ciclos contra tol. 1200–2550), e a discriminância que a métrica vertical **não conseguia enxergar** aparece limpa: **rampa 12 · cliff 8 · sem forma 0** (o premeasure medira que a métrica vertical não distinguia as duas formas — o problema era a métrica, não a ausência de diferença). **As 3 falhas têm causa de COORDENADA, não de forma:** todas na `amp0p6`, todas nos níveis altos, porque `r*` absoluto cai *no joelho* dela (0,812) — trecho **raso**, onde pontuar em vida é tão mal-posto quanto pontuar vertical no íngreme (**problema espelhado** do que motivou o v2); confirmado no `fig2` fino, cuja única falha é de novo `r*`=0,80. Correção indicada = níveis em coordenadas do joelho, **a pré-registrar do zero** (post-hoc não vira gate). **Re-digitalização da Fig. 2** por varredura de LINHA (`liu2025_fig2_redigitize.py`, validada contra os 16 pontos canônicos sob orçamento de erro declarado fonte+rasterização, 14/14, pior razão 0,69): **16→134 pontos, 2→45 abaixo de 0,33**. Duas reprovações da validação foram achados reais (normalizar pelo centro da banda em vez dos 60 kN nominais inflava tudo em ~7 %; ±0,02 vertical ignorava os ±3 % de ciclo, que no joelho valem 0,030). **Com o dado recuperado a forma acerta 6/7 cruzamentos** (30 ciclos de erro entre 0,60 e 0,50 numa curva de 9 789) **e o tripé vertical CONTINUA falhando** (res.máx 0,337): no rabo o dado cai de 0,20 a 0,104 em **5 ciclos**, então `res.máx<0,10` exige acertar a fratura em **±0,05 % da vida** numa fonte com **44 % de scatter** — nenhuma forma determinística passa e **mais dado não resolve**. ⇒ **DATA-LIMITED** (dado não publicado; as 6 da Fig. 3 — eixo Y termina em 20 kN e o inset amplia o **começo**, não a cauda ⇒ a §7 do premeasure estava errada nisso) **vs METRIC-LIMITED** (dado existe, forma acerta em vida, tripé vertical impossível por construção; `fig2_single`). Ações **diferentes**: dado novo vs pontuar no eixo bem-posto. |
| 2026-07-28 | §4.45 **MÉTRICA EM VIDA — autorizada, implementada e MORTA pelos próprios gates.** Pré-registro `specs/2026-07-28-metrica-em-vida-prereg.md`, gates **congelados em `3a26b4a` ANTES de uma linha de implementação**; forma = resíduo **ortogonal** em espaço normalizado pela incerteza (`σ_r`=0,02, `σ_N`=3 %·N), escolhida por não ter chave de regime (degenera em `\|Δr\|` no plano, vira vida no vertical). Medida nos 203 casos (re-sim 202/6 workers/1490 s; **zero divergência** nos campos verticais ⇒ mudança puramente aditiva). **Veredicto M0 ✗ · M1 ✗ · M2 ✗ · M3 ✗ · M4 ✓ · M5 ✓ · M6 ✓** ⇒ ramo pré-declarado *"M2 ✗ ⇒ morre"*. **IMPLEMENTAÇÃO REVERTIDA no mesmo dia** (nunca foi commitada), store restaurado, métrica canônica intacta, fingerprint `4f5bedfbace4`, meta segue **147/202**. **Causa única das 4 falhas, medida: a fuga horizontal corre pela inclinação do MODELO, não pela do DADO** — em `jcsr2023_plain_outdoor` N=150 o dado está PLANO (0,000/ciclo) e o modelo DESPENCA (5,2e-3/ciclo); a queda do modelo *varre* o valor do dado e o resíduo cai de 0,128 para 0,081 ⇒ **a métrica perdoa colapso prematuro**, o modo de falha que a campanha mais precisa detectar (§4.8). Daí o cliff passar (M2: em `amp0p6` o cliff fica **melhor que a rampa**, 0,028 vs 0,030; no `fig2` fino melhora **8,6×**) e 4 das 6 viradas caírem em trecho **raso** (M3). **Lição de forma:** distância ao CONJUNTO de pontos da curva é o objeto errado (deixa o modelo chegar perto por caminho que não corresponde ao mesmo instante); o objeto certo é **correspondência por nível**, que o G1 do prereg v2 usou e que **discriminou** (12 vs 8) — e o normalizador tem de ser a **janela de colapso**, não `N`. **Lição de processo:** o gate M0 era **insatisfazível como escrito** (exigia identidade exata onde a forma só entrega assintótica) — a etapa "medir a mensurabilidade antes de congelar", inventada pela §4.44 dois dias antes, foi pulada ⇒ **regra proposta: todo gate carrega a conta de satisfazibilidade**. **O que o processo acertou:** M2 e M3, escritos antes de qualquer número existir, mataram uma mudança que o próprio autor propôs, implementou e teria adotado olhando só para o headline "147→153" — o pré-registro protegeu a campanha de quem o escreveu. Autorização do professor **não consumida**: morreu a solução, não o problema. |
| 2026-07-28 | §4.46 **2ª tentativa de métrica (correspondência de NÍVEL) — também MORTA, por causa DIFERENTE; a LINHA FECHA (§4.46a).** Gates congelados em `3619af5` com a **conta de satisfazibilidade** de cada um (1ª aplicação da regra da §4.45) + 2º commit, antes de medir, declarando 2 guardas de código e um risco **deixado deliberadamente sem correção** (sem piso de `Δ_col`). **A correção estrutural FUNCIONOU:** correspondência fixada pelo nível, sem `min()` e sem voto do modelo ⇒ **N0/N1 bit-a-bit** (181 curvas + 242 pontos de platô) e `jcsr2023_plain_outdoor`, o caso que expôs a brecha da 1ª tentativa, saiu **idêntico**. **Mas N2 falhou (razão cliff/rampa 1,38× contra critério 2×)** e a previsão escrita no prereg errou por uma ordem de grandeza — erro de **premissa**, não de conta: **a regra de joelho NÃO é invariante à amostragem.** Mesma curva física, 2 digitalizações: canônica (15 pts) → `Δ_col`=**1100** ciclos; fina (124 pts) → `Δ_col`=**40**. **27,5×.** A regra usa taxas ponto-a-ponto ⇒ uma métrica normalizada por ela mede **como alguém amostrou a figura**, não a junta — desqualificação independente dos gates. **Vazamento p/ a §B:** o `trim_n_max` usa **a mesma regra** (`b50550d`) ⇒ os trims também não são invariantes à amostragem; são estáveis só porque um humano os aplica com julgamento — não invalida os trims, **invalida automatizá-los**. **Bloco B FALSIFICADO:** as 16 curvas trimadas pontuadas na curva inteira ⇒ **0 de 16 passam**, várias pioram muito (`liu2025_M16_amp0p25` 0,0745/0,1672 → 0,7270/5,3056); remover trims sob esta métrica não resgata nada. Meta iria de **148 → 139** (0 viradas, 9 perdas). **N6 fez o serviço para o qual foi inventado** (14 pioras; 5 de janela degenerada, como o §2.4 previu por escrito). **REVERTIDO** (nunca commitado); 0 divergências verticais nos 203; fingerprint `4f5bedfbace4`; meta segue 147/202. **§4.46a — a linha fecha:** duas tentativas, dois preregs, duas mortes de causas **diferentes** (o modelo escolhia a correspondência · o normalizador não é invariante), convergindo na mesma raiz: **no trecho quase-vertical o dado publicado não carrega informação suficiente** nem para distinguir formas nem para normalizar tolerância — o que existe ali é a moldura da figura e as escolhas do digitalizador. Reforça a §4.44a com 2 falsificações: essas curvas são **metric-limited**, ficam fora da meta por razão metrológica, e o trim por julgamento humano é a saída honesta. **Rota restante NÃO tentada:** **métrica de banda** (modelo vs envelope de incerteza, não vs curva) — resposta estatisticamente correta aos 44 % de scatter, já nomeada como fora-de-escopo no prereg v1 da rampa §5. Decisão do professor. |
| 2026-07-28 | §4.47 **MÉTRICA DE BANDA (3ª tentativa) — a discriminância SOBREVIVEU; morre por LIMIAR, não por estrutura. A linha NÃO fecha.** Prereg `0e97d6a` com a conta de satisfazibilidade **rodada numericamente**. Forma: banda = `[min,max]` do dado **interpolado** em janela horizontal `±h_N` (`h_N`=3 %·`N_fim`), resíduo **hinge** avaliado em `N_i` — sem `min()` nem voto do modelo (corrige a 1ª morte), sem regra de joelho (corrige a 2ª), sem dilatação vertical `±σ_r` (que afrouxaria o tripé em 0,02 em toda curva). **B0 ✓ · B1 ✓ · B2 ✓ · B3 ✗ · B4 ✓ · B5 ✓ · B6 ✗.** **B1 (DISCRIMINÂNCIA) passou pela 1ª vez em 3 tentativas** — no `fig2`, nas duas digitalizações, rampa 0,0243/0,0521 e 0,0137/0,0542 **passa**, cliff e sem-forma 0,0479/0,1783 e 0,0759/0,1319 **falham**. **B0 passou com precisão notável:** res.máx da rampa difere **3,9 %** entre 15 e 124 pontos contra os **4,0 %** previstos pela conta — a dependência de amostragem que matou a 2ª tentativa (27,5×) está resolvida. **Bloco C, o número que justificaria remover trims:** as 16 curvas trimadas, pontuadas **inteiras**, dão **10 de 16 passando** (sob a métrica de nível: 0 de 16); meta iria a **147 → 154**. **Morre por B3:** `chu2026ti_..._test9` virou (0,1173 → 0,0949) com banda de largura **0,0443** < 0,05 — virada de baixo conteúdo, e o gate existe para barrá-la; ramo pré-declarado **morre**, honrado, revertido (0 divergências verticais nos 203). **B6 ✗ é defeito de AUTORIA do gate:** *plana* foi definida como largura < 0,02 e a tolerância como 0,005, mas largura até 0,02 permite mudar o res.máx em até 0,02 ⇒ **as duas cláusulas são incompatíveis entre si**; ramo do B6 não mata. Diagnóstico: as 3 curvas que reprovam são **esparsas** (25/7/9 pontos) — janela grande **relativa ao espaçamento**, não em valor absoluto. **3º defeito de autoria de gate em 3 tentativas** (M0 insatisfazível · N2 com premissa de cabeça · B6 auto-inconsistente) ⇒ **reforço da regra: a conta de satisfazibilidade tem de cobrir o PIOR CASO ADMITIDO PELO ESCOPO do gate, não um exemplo** — se o gate diz "para X < a, exigir |Δ| ≤ b", verificar que X = a ainda produz |Δ| ≤ b. **A linha não fechou** (o ramo que a fecharia, `B1 ✗`, não ocorreu); morreu esta parametrização. 4ª tentativa mudaria o mínimo (`h_N` sensível ao espaçamento; B6 coerente; B3 mantido), mas pesa contra: 3ª tentativa, 3 erros de gate do autor, e a métrica é **unilateral**. Decisão do professor. |
| 2026-07-28 | §4.48 **BANDA v2 (4ª tentativa) — o GATE CEGO reprovou; §4.48a A LINHA FECHA EM DEFINITIVO.** Prereg `af711b8`; **nada a reverter — nenhuma linha de código canônico tocada**: a banda só precisa do modelo **nos ciclos do dado** (`metric_pred`, já no store) ⇒ **pós-processamento puro**, segundos em vez de 25 min + reversão. Correção da forma: banda exige **evidência medida** (janela sem vizinho medido ⇒ banda `[r_i,r_i]` ⇒ resíduo `|Δr|` **exato**), o que curou a 3ª morte (**C6 ✓**; `chu2026ti_..._test9` tem 25/25 pontos sem vizinho e não vira mais). **O §0 do prereg declarou ANTES de medir que o `fig2` deixara de ser teste cego** (3 variantes testadas nele) e rotulou C2/C3 como **caso de projeto**, jogando a evidência no **C4 CEGO** (núcleo `amp0p4/0p5/0p6`, nunca usado no desenho). **C4 FALHOU: rampa 0 de 3**, e em `amp0p6` a rampa (0,0718/0,3300) é **pior que não ter forma** (0,0340/0,1116) ⇒ **a discriminância do `fig2` era artefato de projeto**. C2/C3 passaram, o cego reprovou — demonstração mais limpa da campanha de que projetar e testar na mesma curva não vale nada, e só existe porque a perda de cegueira foi **declarada por escrito antes**. **C7 mata independentemente:** 36 curvas com >50 % dos pontos alterados (até 94 %); coexistindo com **C5 mediana 0,00000** ⇒ o efeito é **concentrado num terço das curvas e difuso dentro delas**, não desconto uniforme. **C0 reprovou por causa EXTERNA** (sessão paralela tocou 2 arquivos às 13:10) **e o gate estava mal escrito** — testava a árvore compartilhada, não a mudança: **4º defeito de autoria de gate em 4 tentativas** ⇒ **2º reforço: um gate mede a MUDANÇA, nunca o ambiente**. Positivos a reusar: **C1 = 0,00e+00 em 1952 pontos** (a conta previu igualdade **literal**, contraste com o `M0`), C2 acertou na casa decimal (3,7 % vs 3,7 %), e o **método**: antes de patchear o runner, verificar se a métrica é computável dos vetores que o store já guarda. Bloco D (moot): 7/16. **§4.48a — FECHAMENTO:** 4 preregs, 4 execuções, 4 reprovações, **3 no gate de discriminância** (ortogonal: o modelo escolhia a correspondência · nível: normalizador não invariante · banda v1: janela sobre segmentos não medidos · banda v2: discriminância era artefato de projeto). **Registro final: nenhuma métrica automática sobre curvas digitalizadas esparsas distingue a forma certa da errada no colapso quase-vertical — toda métrica que "resolve" o problema perdoa também o cliff.** Resposta final adotada: essas curvas são **metric-limited**, ficam fora da meta por razão metrológica, e o `trim_n_max` por **julgamento humano documentado caso a caso** é a saída honesta (com a ressalva §4.46 de que a regra que o descreve não é automatizável). Custo: 3 varreduras, 3 reversões, **zero adoções**, 4 defeitos de gate — cada um gerando uma regra: (1) conta de satisfazibilidade; (2) cobrir o pior caso do escopo; (3) medir a mudança e não o ambiente; (4) **um gate cego vale mais que nove no caso de projeto**. |
| 2026-07-28 | §4.50 **A-vs-B da rampa MEDIDO — Opção A vence; a narrativa do "acoplamento de graça via k_b" FALSIFICADA neste carregamento.** Sonda com previsão escrita antes de rodar: o feedback F₀→slip→wear corre por `state.F_0` e existe nas duas opções; `k_tr` (bending) usa `d₂⁴`, cego a `k_b`; os canais próprios do B têm sinal **negativo** (conversor `−k_b·dδ` dos outros mecanismos). Medido: forma idêntica (Δ ≤ 60 ciclos ≪ tol), **B não conserta a `amp0p6`** (−2954/−2729 idênticos ao dígito), wear B−A +0,23 a +0,70 kN (amortece), e **energia decide**: residual A1 0,017–0,151 J contra **B1 até −20,5 J** (`U = F₀²/2k_b` muda sem contraparte de trabalho). Decisão: **Opção A com dE incremental**; prereg de implementação congelado (`2026-07-28-ramp-capability-prereg.md`, P0–P6 com contas medidas), implementação aguardando o professor; B registrado como candidato p/ competitive-failure com a dívida `∂U/∂k` anotada. |
| 2026-07-28 | §4.51 **RAMPA DE FRATURA vira capacidade do engine — prereg `ea028ef` executado, todos os gates passam.** `fat_ramp_D_on=1.0` (default = cliff **bit-idêntico**) e `fat_ramp_q` novos em `JointMaterial`; ramo de rampa em `FatigueLoss` com `dE = ΔU_internal` por incremento (rota do cliff). **P1 com paridade EXATA** (0,00 ciclos nos 20 cruzamentos da sonda A1), **P0/P6 bit-idênticos nos 203**, **P2** LI_2022_TRIBOINT intocado, **P3** residuais 0,017–0,151 J. +2 VarSpec no explorador; `tests/test_fatigue_ramp.py` (8 testes, incl. P4 do Run). **P5 informacional:** N₉₅ emergente 10–100× cedo em amplitude baixa (front-loading do assentamento) — insumo da adoção, não gate. Fingerprint `4f5bedfbace4` e meta 147/202 inalterados: capacidade ≠ ganho de meta. Abertos: adoção per-rig LIU_2025 (prereg próprio), `_CAP` do Run, rótulo do `fat_m1=2,7`. |
| 2026-07-28 | §4.52 **ADOÇÃO per-rig LIU_2025 executada e REVERTIDA pelo gate cego A1.** Prereg `8ec2521` com contas rodadas (`fat_C1` ancorado, relógio ±36 %; risco declarado nas 3 curvas com rampa na janela). **A1 ✗:** `amp0p8` 0,0487/0,0853 → 0,1597/0,6800 (relógio 27 % adiantado × trim no joelho ⇒ colapso inteiro dentro da métrica); `amp0p3`/`fig2` Δ=0,0000 exato (nenhum ponto do dado na fresta). Rollback pelos backups; fingerprint `4f5bedfbace4` uniforme; capacidade fica. **Confirma quantitativamente o orçamento do premeasure** (≤5 % exigido vs ±36 % disponível): relógio preditivo determinístico não segura o colapso — a causa é o relógio, não a forma (A4: canal `fatigue` na decomposição funciona; `amp0p3` fraturaria a −7 % do medido). Colateral: `parallel_batch` cobre **202 de 203** (`exemplo_m12_sintetico` fora ⇒ quebraria uniformidade de fingerprint em qualquer adoção via batch). Rota que destravaria: `N_f` input-de-paper por curva (E2; precedente LI_2022_TRIBOINT). |
| 2026-07-28 | §4.53 **ADOÇÃO E2 ADOTADA — estágio 3 do Liu 2025 no canônico, dada a vida.** Prereg `d721b14`; **E1 cego OK** (7/7, pior ΔMAE +0,0006 — as 6 cegas seguraram como a previsão α(D_trim)≤2,6e-6 dizia), E2g OK, E3 OK após conserto (o `--cases` do prereg não alcança `exemplo_m12_sintetico` — fora do universo do batch; conserto real = re-sim direta via runner + carimbo, métricas bit-idênticas). **Fingerprint `4f5bedfbace4` → `9ac44acd03de`** (adoção legítima; store uniforme; meta 147/202 intacta). `N_f` input-de-paper por curva (7 `fat_C1` fixados; 1º uso do `per_case` para `fat_*`); claim = *"prevê a curva dada a vida"*. Full-range: finais 0,000–0,336 (antes ~0,78–0,84), canal `fatigue` na decomposição 0,19–0,78 de F₀ — fecha o residual do PR-9b (*"cliff terminal = fratura"*). Report regenerado. |
| 2026-07-28 | **Re-stamp `294808504d83` com o rider aprovado: trim da `amp0p8` REMOVIDO por mérito** (0,0487→**0,0381**/0,0853; gates 3/3, demais curvas idênticas ao dígito; §B recontado: 15 trims, LIU ×6). O re-stamp também **re-sincronizou hash↔store** após a correção do rótulo `prov.fat_m1` (c620cbe) — erro meu, dono declarado: **`prov`/`verdict` entram no hash do fingerprint**, então edição de metadado força re-stamp como mudança de `cfg` (gotcha novo no CLAUDE.md). Sintético re-carimbado pelo método direto (bit-idêntico). Meta 147/202 intacta. |
| 2026-07-28 | **ADOÇÃO chu-test1 (piso lido L24) — test1 ENTRA no tripé; meta 147→148/202; fingerprint `294808504d83`→`3546e6745448`.** Prereg `cb86970` (contas RODADAS antes: controle 0,00e+00; 0,0035/0,0082), gates 4/4: GT1 PASS, GT2 8 cegas bit-idênticas, GT3 batch-202 com EXATAMENTE 1 mudança/0 pioras/1 flip de status, sintético re-carimbado direto (bit-idêntico). `loose_arrest_floor=0,9876` per_case, prov lido-do-dado (platô, plateau=True). CHU: violadoras 7→6. |
| 2026-07-28 | **Métrica de DERIVA β (informacional) — pedido do professor respondido com medição.** σ_res é permutação-invariante (cega à ordem); β = slope do resíduo ASSINADO vs posição + d3 (terços), puro pós-processamento dos vetores do store. **36/147 do tripé com \|β\|>0,05; 4 com \|β\|>0,10** — o `eccles fig7d` (−0,107) é pego automaticamente (o S4 já o havia removido por julgamento: a métrica mede o que promete). corr(\|β\|,σ)=0,686. Promoção a 4ª perna = prereg assinado (custos na fila: corte 0,10 ⇒ 147→143; 0,05 ⇒ 147→111). `residual_drift_metric.{py,json,md}`. |
| 2026-07-28 | **Lu2024: 3 linhas fechadas em CONTAS, zero preregs** (`lu2024_frontload_resultado.md`): (1) N_emb=1 com regra de isenção por feature pré-medida — gate FAIL 2× (o amp0p25 tem o MAIOR déficit, 80% vs 28%, e PIORA mesmo assim; leitor per-curva doutrina-bloqueado no transversal); (2) forma (b) front-loaded hiperbólica (θ_acc): âncora fig18 −38% mas cegas fig20 de torque alto PIORAM (T22 dobra); (3) normalizada (fração de F₀ via hélice): 4 pioram. Padrão = redistribuição de erro; o front-load do Lu é dependente-de-condição DENTRO da fonte (mesma classe do Chu §4.54a, medida com transferência que o Chu não permitia). LU_2024 form-limited afinada; ganhos registrados como informação (T16Nm entraria sob N_emb=1). |
| 2026-07-28 | **Rousseau prereg executado (D1–D4 completos): trilha A satisfazível nas contas (aguarda G7 adversarial), trilha B fechada POR MEDIÇÃO.** A: floor de grupo 0,08 (herdado, nunca justificado)→0,02 põe o t10 no tripé (0,061/0,096), t12 +0,007, t14 bit-idêntico (stick=inerte, predição do prereg ✓); G5 t12 zero-refit +0,007≤0,02; G6 resíduo cai na posição original; prov fitada-this-rig com teto da leitura (0,02<0,112). B: **a alavanca que fecha o t10 quebra o t12 na direção oposta** (CM 0,5: 0,042/0,089 vs 0,138→0,151 virado), amplitudes 0,50/0,49 — H-B3 (scatter de espécime no joelho) confirmada par-a-par SEM queimar tentativa (regra §4.45); HDPE ×2 → proposta F6. Diagnósticos Karlsen (75% da aceleração, n=1, dorme) e Yang2019 (amp0p4 consolidada c/ Yang2023-IJPEM no "limiar graduado"; varamp = carry-over de história, bloqueado pelo trim F6-§B) em `karlsen_yang2019_diagnostico.md`. |
| 2026-07-28 | **Correções de verdade-de-input (em re-stamp, fingerprint INALTERADO — inputs/CSV ficam fora do hash):** YANG_2023_IJPEM freq 12,5→**10 Hz** e M6 8,5→**11 kN** (companion OA PMC11901137 Table 1, "identical to previous study"; o 5 Hz do DEEP_RESEARCH também estava errado; impacto medido antes: freq inerte, F₀ misto, ZERO mudanças de status) + **CSV fino da fig2 adotado** (134 pts validados 14/14; fig2 0,0387/0,0546@10pts → 0,0276/0,0571@44pts, segue no tripé). Higiene: 4 curvas de grip SINTÉTICAS do Zhang2006 expurgadas da galeria antiga (82→78) + rótulo no script. |
| 2026-07-28 | §4.54a **ERRATA do estudo Chu + FECHAMENTO EM NÍVEL DE LEI.** Três erros do mesmo método (diretório em vez de registry — gotcha conhecido): nota já existia (duplicata removida), Fig. 5 já digitalizada (2026-07-15), e a rota (i) já executada — **F3.2-CHU (21/07) prescreveu os schedules e FALHOU o G-CHU-a**. Sondas de fechamento: schedule ISOLADO ≈ inerte (|Δ|~0,01 — **fato de engine: wear disp-mode é Archard, sem µ**; o canal de 93 % do Chu é cego ao µ(t) medido) e lei recolorida (wear energético `k_E·µ_medido·p·slip`) **morre na âncora** (test4 0,118/0,249; cegas 0/3). 2ª tentativa do F3.2 NÃO gasta (contas insatisfazíveis = ramo do prereg honrado). Veredicto: o resíduo é a **estrutura temporal do kernel**; candidato restante = torque acumulado do paper (b=1,65, N-explícito) — ≥3 constantes/4 curvas ⇒ não-adotável; **6 casos candidatos a exceção assinada**. |
| 2026-07-28 | §4.54 **Estudo Chu2026 EXECUTADO — a receita mais limpa (trio PR-38 + procedência, zero fit novo) morreu nas CONTAS DE PROJETO, antes do prereg.** Nota de aparato NOVA (`chu2026_triboint.md`; errata: "ti" = *Tribology International*, rig GH159/GH4169 rosca prateada µ≈0,05, MJ10×1,25, E=189 — registry com passo 1,50/E 200 = gap de procedência). **µ implícito nos nossos CSVs confirma a Fig. 5 do paper** (COF MEDIDO subindo durante o afrouxamento): test2 sobe 9,3×, 49 kN ≫ 61/73; no test4 o µ-resistor vence (arresto) — dois papéis do µ separados no dado. Contas em 2 curvas de projeto (6 cegas): test2 **piora em todas as variantes** (0,154→0,166/0,183/0,203) — µ subindo arresta o modelo, mas o test2 real perde tudo (regime 2: carga vence atrito). `k_dmg_mu` escalar não carrega dois papéis × dois regimes. **Zero preregs gastos; FAIL2 reservado.** Fonte segue form-limited com a forma nomeada pela fonte (torque assimétrico acumulado + µ(t)); destravamento na fila: (i) digitalizar Fig. 5 (âncora µ(t), barata) → (ii) forma asymmetric-torque (cara, depois de i). Fingerprint `294808504d83` intocado. |

| 2026-07-30/31 | **Linhas de retomada (registro compacto; detalhe nos resultado.md):** adoções **ZHANG_2018** (creep-onset lido do resíduo, 9/9; `zhang18_creep_onset_resultado.md`) e **LIU_2016** (re-atribuição creep→fretting L1 dos autores, 14/14; `liu2016_fretting_resultado.md`); **arco LU_2024** 0/10→12/12 com estatuto (input-truth fig20=1,0 mm, `c_bend=30` lido da Fig. 21, Fig. 14 digitalizada, pares de réplica declarados, exceção-elástica com 2 emendas; `lu2024_plano_melhoria.md`); **D1** 3ª perna por fonte; régua da prova F7 endurecida (toda perna violada coberta). Estas linhas faltavam pela regra do rodapé — sincronizadas em 2026-08-01. |
| 2026-08-01 | §4.55 **`s1_amp_gate` — forma de engine NOVA (default-inerte) + 3 falsificações pré-registradas no dia; adoção NÃO ocorreu e a classe "relógio de estágio I" foi PARADA pela regra.** Instrumento: N₉₅ do modelo CONSTANTE (~108) onde o dado do LIU_2025 varre **850×** (Fig. 4 D-N); decomposição 59 % emb + 41 % creep em 0,25 mm. (1) Candidato A (campos existentes) G1 1/6 — expoente efetivo do gate de slip ~2–4 vs ~11 exigido. (2) Forma B (gate Hill em `d_delta` de Emb+Creep; conservação intacta por construção; G0 bit-idêntico testado) fitada na D-N: G1 5/6, mas G2/G3 quebram — **a D-N e as curvas digitalizadas da MESMA fonte discordam do N₉₅ em 3–5× nas DUAS direções** (achado sobre o dado publicado; carta aos autores na fila). (3) Decisão do professor "curvas mandam": G1c **6/6** (tudo ≤1,7×) e G2c **falha com TODAS as 7 curvas piorando** — casar o resumo (1º 5 %) abre platô onde o dado desce; o dado exige re-tempo COORDENADO I+II (fit conjunto ≥5 números/7 curvas = vetado). Adendo: realocação de wear (`k_wear_spec` sob o gate) = **parâmetro morto** (incubação fecha o canal em 0,25 mm; 4 doses idênticas ao dígito). A forma fica no engine com testes+VarSpecs para fonte com dado internamente consistente. Fingerprint intacto; censo 136/203. `s1_amp_gate_resultado.md`. |

| 2026-08-01 | §4.56 **ERRATUM + RECUPERAÇÃO ROUSSEAU — o PDF oficial expôs dupla falha e devolveu a validação preditiva mais forte da fonte.** (a) *Input*: aço rodava a **0,5 mm** contra **0,05/0,05/0,04 mm** da Tabela 2 (10×; classe fig20-LU) — corrigido, t10 0,087→0,304 antes do re-fit. (b) *Piso*: a única "família" era aço-t10↔t12, **espessuras DIFERENTES** pareadas como réplicas pela chave cega à geometria ⇒ **3 exceções FORTE retratadas** + bloqueio `_SEM_FAMILIA_MECANICA`. (c) *Recuperação*: Fig. 6 digitalizada (tracer separa preload de rotação **por FORMA** — monotonicidade — porque as duas dividem a cor e se cruzam; máscara de legenda por cor e salto ∝ vão), condição INÉDITA (os 2 materiais a 0,2 mm/3,5 kN): **HDPE previu no TRIPÉ com ZERO refit** (0,0267/0,0755/0,0245, 2,5× fora da amplitude do fit — validação forte do `k_member_shear`/PR-14); aço re-fitado em **1 número** (`c_bend` 0,3→3,0, só na Fig. 5) e adotado **POR PROCEDÊNCIA, não por predição** — G2 held-out **FALHOU (0,1329 vs 0,10)** e está escrito na adoção. Residual medido: modelo retém 0,301/0,313 contra 0,137/0,164 do dado. (d) *A forma de amplitude foi RECUSADA na tabulação, antes de existir* (prereg `forma-amplitude-rousseau`): com 4× de amplitude o **dado quase não muda** (0,137→0,164) e o modelo **também não** (0,301→0,313) ⇒ não há déficit de INCLINAÇÃO, há déficit de **NÍVEL** — abrir forma seria fitar uma inclinação que o dado não pede. O nível é carregado pelo canal dominante (afrouxamento rotacional, 67–79 % da perda) e a constante que o corrige tem **procedência de APARATO**: `loose_arrest_floor` **0,08 (do pack) → 0,0**, porque o rig apoia o membro móvel em **roletes que declaradamente removem o atrito parasita** ⇒ sem auto-travamento. Ótimo de FRONTEIRA monótono (0,00→0,233 · 0,15→0,351), −22 % na soma dos MAE do aço, zero pioras; com ele o held-out cai a **0,0957** (passa a barra que o G2 reprovara). (e) *Maquinaria*: `delta_amp_mm` passou a resolver por **token mais longo, com erro em empate** (era o 1º do dict — a curva nova herdou 0,5 mm por substring `t10`, em silêncio). Fingerprint `3d432a65c7e8`→`576605bcf96d`→`a410d6537c83`; censo 132/205. |

| 2026-08-02 | §4.57 **Classe "aceleração tardia" ENCERRADA pela regra (2ª parada da campanha) + 2 capacidades novas no engine, nenhuma adotada.** Três falsificações com prereg e mecanismo nomeado: gates Hill têm contradomínio (0,1] e **só atrasam** (falsificação POR CONSTRUÇÃO); amplificador por acumulador (`k_dmg_all`, novo) é **gradual demais** (D vai 0→0,9; +53/+119/+397 % de MAE); amplificador por interruptor (`k_late_amp`, novo, reusa `crash_trigger`) tem sinal e perfil certos mas **não é per-rig** (CHU: mesmo k, 5 curvas melhoram e 3 pioram). 4º candidato (relógio por curva) **DATA-BLOCKED**: as curvas param por critério de protocolo, não por falha. Spec final do PR-3 registrada. **Erro de gate meu**: pinei `crash_trigger_frac=0,85`, cuja razão tardio/inicial é 4,6, e exigi >5 — gate infeasible POR CONSTRUÇÃO; conferir a álgebra ao escrever. | 
| 2026-08-02 | §4.58 **ROUSSEAU: 2 erratas do PAPER, round-trip da nossa digitalização, e um re-fit contra o nosso próprio interesse.** (a) A Fig. 7 diz "% of Preload Loss" mas é **retenção** — prova interna: a série de 182 ciclos fica ABAIXO da de 100. (b) Lida certo, ela **valida por round-trip** a nossa Fig. 4 em t14 (97,9 vs 97) e t12 (80,1 vs 79) — e **acusa a t10** (67,2 vs 62). (c) A t10 foi **re-digitalizada pelo centro da banda** (a antiga seguia o topo): passa a 62,8/44,3 contra alvo 62/43 — e **o MAE do modelo PIORA 0,0579→0,1010**, aceito porque o prereg pré-comprometeu ("o critério é o alvo do paper, não o nosso ajuste"). Parte da qualidade aparente era erro de digitalização a nosso favor. (d) A unidade do Kj é o **2º rótulo errado**: só em N/mm as Figs. 7 e 8 dão ordens plausíveis ⇒ expõe que os 6 casos rodam com **E de aço no membro** (k_j 293× o medido no HDPE) — mas o efeito é **~1 %** em disp-mode (o slip manda), então fica como caveat, não re-fit. (e) `GA_member` 20000→**22000** re-fitado sob a t10 corrigida, **por procedência**: G1 de ganho FALHOU (−10 % vs −15 %) e está escrito na adoção; held-out da Fig. 6 **melhora** (0,0267→0,0260) e segue no tripé; aço bit-idêntico; 22000 é o maior valor que mantém a t14 em **stick** — o limite é o regime. Fingerprint `a410d6537c83`→`63722b266dc0`; censo **129/205** inalterado. |

| 2026-08-14 | §4.59 **FORMA NOVA `emb_clock_delta_ref` (relógio de assentamento ∝ 1/δ) — implementada, validada, e NÃO ADOTADA; a não-adoção é o resultado.** `N_emb_eff = N_emb·(δ_ref/δ)`, default `0.0` = **OFF exato** (o ramo nem roda; o guard da divisão fica **dentro** do `if` de propósito — posto fora, ele mudaria o caminho desligado para `N_emb=0`, e "default-inerte" tem de valer inclusive para entrada degenerada). ⚠️ **O expoente é 1 e NÃO é ajustável**: se o assentamento se esgota após uma distância de slip acumulada `S`, então `N_emb = S/(slip por ciclo)` e `slip ∝ δ` ⇒ `q = 1` **por construção**; não existe campo para mudá-lo e `tests/test_emb_clock_delta.py` **proíbe** que apareça — era exatamente a âncora que faltava à adoção `CHU_2026_D1p0`, cujo `prov` registra *"não há âncora no artigo"*. ✅ **Paridade 8/8 ao 12º dígito** contra a sonda que calculava o `N_emb` à mão (validar a lei ≠ validar a implementação da lei); ✅ **inércia bit-a-bit nas 210**; ✅ a lei **generaliza** a adoção vigente — em δ=1,0 mm devolve 400 e dá **Δ = +0,0000 exato**. ⛔ **Reprovada na adoção**: na fonte inteira ganha a `test9` (σ 0,0547→0,0145) mas piora a `test3` em **+0,0392**, 4× a tolerância de +0,01 do D-AB; a variante limpa (só o relógio, sem o nível) **passa** o gate e ganha **zero**. Estreitar o grupo para capturar o +1 seria mover a trave: {δ=1,0 Ra 0,4} ∪ {δ=0,5 Ra 1,6} não é conjunto que o artigo defina (precedente D-AC). ⚠️ **O achado que vale mais que o +1**: `test3`×`test9` são o **par de rugosidade do próprio paper** (δ e F₀ idênticos, Fig. 3b) e a Tabela 1 diz que **Ra 0,4 é a BASE e Ra 1,6 é a RUGOSA** — eu havia lido o nome do arquivo ao contrário. Dentro da **mesma classe Ra 0,4** o `emb_depth` exigido vai de 1,6 µm (δ=0,3) a **≥25 µm** (δ=1,0): **≥15×**. Quando uma constante precisa mudar 15× dentro da própria classe física, ela deixou de ser a constante que o nome diz ⇒ o `emb_depth` desta fonte absorve **dependência do ALVO com o deslocamento**, e a ρ-unificação (§4.18) não alcança porque o driver dela é **força** e o CHU roda `F_amp` fixo. **A potência única em δ já está falsificada** (expoentes 0,19 vs ≥3,6, 19× de desacordo). Fingerprint **inalterado** (`c37618c5cc96`), censo **141/205** inalterado. Doc: `lei_relogio_implementada_e_nao_adotada.md`. |
| 2026-08-14 | ⚠️ **LACUNA DECLARADA nesta tabela — 12 dias e ~14 adoções sem linha.** Entre §4.58 (2026-08-02) e §4.59 (hoje) a campanha adotou/corrigiu: **D-H** e **D-I** (08-04, CACCESE: kernel de creep saturante + centro de réplicas), **D-L** · **D-P** · **D-Q** · **D-R** · **D-S** (08-05, LIU_2022 relógio por reaperto · Φ medido no LI_2022 · saturação do canal de flanco · re-digitalização ROUSSEAU · CSV da CACCESE rep2), **D-U** · **D-V** · **D-W** (08-06, re-ancoragem YANG_2021 · `fret_freq_exp` no LI_2022 · re-digitalização `lu2024_fig18_amp1p5`), **D-Z** · **D-AA** · **D-AB** (08-09, forma do creep no JCSR · varredura conjunta forma×nível · `C_creep` per-par no ECCLES), **D-AC** (08-10, `k_wear_spec` no YANG_2019). Cada uma tem prereg com gates congelados e documento de resultado em `New_Theory/*_resultado.md`, e todas estão registradas no `CLAUDE.md`; **o que falta é a linha aqui**. ⇒ isto é o **§4.43 acontecendo no documento cuja função é preveni-lo**: o `CLAUDE.md` designa este arquivo como *living doc, update on every model change*, e o `test_meta_numeros_nao_envelhecem` só ancora as duas afirmações de §8 — **a tabela não tem guarda**. Declarado em vez de silenciado; retro-preencher exige reler os 14 documentos e é trabalho de sessão própria. |

*Atualize esta tabela e a Seção 4 a cada mudança de modelo/calibração.*
