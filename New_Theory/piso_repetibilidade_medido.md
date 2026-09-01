# Piso de repetibilidade do dado — a âncora dos limites do tripé

**Data:** 2026-07-29 · **Store:** `3546e6745448` · **Pedido do professor:**
*"vamos pensar em valores aceitáveis para o modelo conforme a literatura"*
**Decisão tomada com base neste documento:** tripé = **res.máx ≤ 0,10 · MAE ≤ 0,05
· σ_res ≤ 0,025** — **104 de 202** comparáveis no report (105 de 203 contando o
caso sintético, que fica fora do censo). **Instalado** em `report_html.py`
(`META_MAX`/`META_MAE`/`META_SRES`) com a justificativa renderizada na própria
página, e com os três limites **ajustáveis ao vivo** ali.
**Script:** a medição é pós-processamento puro dos vetores `metric_x/data` que o
store já guarda (zero re-simulação); reprodução no §5.

---

## 1. A pergunta

Um limite de erro só é honesto se estiver **acima da dispersão do próprio
experimento**. Abaixo dela, "reprovado" não mede o modelo — mede o dado, e um
modelo que passasse estaria perseguindo ruído de digitalização e de espécime,
que é a definição operacional de overfitting.

Isto **já era a regra da casa** e não estava no tripé: o
`New_Theory/convergence_indicator.py` carrega `FLOORS` (5 pisos medidos) e usa
`max(piso + 0,02; TARGET = 0,10)` como limite por caso desde a campanha antiga.
O que faltava era medir o piso para **todas** as famílias e aplicá-lo às **três**
pernas, não só ao MAE.

## 2. Método

- **Família** = curvas da MESMA fonte com a MESMA condição nominal, lida do
  `config_used` (`delta_mm`, `F_amp_N`, `mode`) — não do nome do arquivo, para
  não depender de convenção de sufixo (`_rep1`, `_t3`, `_test2`, `run1p2`…).
- Para cada **par** da família, compara **DADO contra DADO** por **interpolação**
  numa grade de 40 pontos na janela de `x` **comum** (interseção) e mede as três
  réguas do tripé: `MAE`, `res.máx` e `σ` do resíduo. Interpola-se o **dado**,
  nunca a métrica.
- Piso da família = **média dos pares**.

> ## ⚠️ ERRATA v1 → v2 (mesma sessão, 2026-07-29)
>
> A 1ª versão deste documento exigia abscissas **idênticas** (x arredondado a 3
> casas) para formar um par. Em curvas digitalizadas de figuras diferentes isso
> descarta quase todos os pares — e o que sobra **não é amostra aleatória**: é o
> par que por acaso caiu na mesma grade, que é o mais próximo. **Medido no BAUER
> fig6:** sobrava **1 par de 15**, piso de MAE **0,0218**; com os 15 pares,
> **0,0959**. O `FLOORS` legado do repo (pareado por nome) já dizia **0,115** ⇒
> era a **minha medição** que estava fora de linha, não o legado.
>
> | | v1 (grade idêntica) | **v2 (interpolação)** |
> |---|--:|--:|
> | famílias | 19 | **30** |
> | fontes com piso | 16 | **22** |
> | mediana MAE | 0,0598 | **0,0829** |
> | mediana res.máx | 0,0795 | **0,1279** |
> | mediana σ | 0,0241 | **0,0283** |
>
> **Consequência para os limites:** o `σ_res ≤ 0,025` foi escolhido na mediana da
> v1 (0,0241) e agora fica **12 % abaixo** da mediana corrigida. Pendência aberta
> no §11 de `f7_excecoes_por_prova_de_piso.md` (manter como ambição declarada, ou
> mover para 0,028–0,030 — impacto medido: 109 e 115 de 202 contra 104).
> **Consequência para as exceções:** a lista de prova de piso vai de 23 para
> **38** candidatas.
>
> O `_pisos_medidos` do report **já usa a v2**, então a página publica o número
> corrigido e imprime a nota de método ao lado.

## 3. O que foi medido — 19 famílias, 16 fontes

> **Rótulo de fonte = a chave do registry**, não o prefixo do `case_id`
> (`demir2024` é `ICMEZ_2025`, `liu2017` é `LIU_2017_AXIAL`, `liu2022` é
> `LIU_2022_RETIGHT`) — é assim que o report agrupa.
>
> ⚠️ **A tabela abaixo é da v1 e está SUPERADA pela errata do §2.** Fica como
> registro do que foi medido e do quanto o viés de amostragem custou; a tabela
> vigente (30 famílias, v2) é a que a **própria página renderiza** na seção "Por
> que estes limites", e a de piso por fonte está no §3 de
> `f7_excecoes_por_prova_de_piso.md`. Compare as duas: onde a família tinha
> muitos pares e poucos na mesma grade (BAUER fig6, ECCLES, LIU_2016), a v1
> subestimou; onde só havia 1 par de qualquer jeito (ICMEZ, ROUSSEAU), os dois
> valores são próximos.

| fonte / condição | n | MAE | res.máx | σ |
|---|--:|--:|--:|--:|
| JCSR_2023 d=0 F=0 | 5 | 0,2943 | 0,5786 | 0,2298 |
| ROUSSEAU_2025 d=0.5 F=4100 | 2 | 0,2179 | 0,5463 | 0,1957 |
| ICMEZ_2025 d=0.3 F=7040 | 2 | 0,1523 | 0,3005 | 0,1121 |
| ICMEZ_2025 d=0.3 F=5720 | 2 | 0,1284 | 0,2424 | 0,0861 |
| CACCESE_2009 d=0 F=0 | 7 | 0,1098 | 0,1448 | 0,0371 |
| ICMEZ_2025 d=0.4 F=7040 | 2 | 0,0918 | 0,1547 | 0,0446 |
| ICMEZ_2025 d=0.4 F=5720 | 2 | 0,0826 | 0,1462 | 0,0493 |
| LIU_2016 d=0 F=10000 | 10 | 0,0807 | 0,1133 | 0,0252 |
| ECCLES_2010 d=0.65 F=6000 | 10 | 0,0743 | 0,2058 | 0,0785 |
| LIU_2017_AXIAL d=0 F=10000 | 5 | 0,0598 | 0,0795 | 0,0221 |
| CHU_2026 d=1 F=19600 | 2 | 0,0498 | 0,0752 | 0,0241 |
| LIU_2022_RETIGHT d=0.3 F=10400 | 18 | 0,0382 | 0,0532 | 0,0180 |
| *(+7 famílias abaixo de 0,04 de MAE)* | | | | |
| LI_2022_TRIBOINT d=0 F=10000 | 4 | 0,0305 | 0,0436 | 0,0149 |
| SUN_2025_REASSY d=0,3 F=6000 | 5 | 0,0264 | 0,0524 | 0,0133 |
| BAUER_2024 d=0,07 F=8000 | 6 | 0,0218 | 0,0464 | 0,0182 |
| YANG_2021 d=0,8 F=5640 | 2 | 0,0086 | 0,0207 | 0,0075 |
| LI_2022_MARSTRUC d=0 F=0 | 6 | 0,0071 | 0,0109 | 0,0039 |
| LIU_2020_WEAR d=0,2 F=7200 | 3 | 0,0063 | 0,0121 | 0,0032 |
| GRZEJDA_2026 d=0 F=10000 | 2 | 0,0017 | 0,0032 | 0,0011 |

**Agregado:**

| régua | mediana | média | min | max |
|---|--:|--:|--:|--:|
| MAE (v1, superada) | 0,0598 | 0,0780 | 0,0017 | 0,2943 |
| res.máx (v1, superada) | 0,0795 | 0,1489 | 0,0032 | 0,5786 |
| σ_res (v1, superada) | 0,0241 | 0,0518 | 0,0011 | 0,2298 |

⚠️ **O piso do DADO se decompõe como o erro do modelo.** Entre réplicas, o σ
mediano é **0,0283** mas o MAE mediano é **0,0829** (v2) — a diferença é o **viés
entre espécimes**, e ele tem nome na literatura: dispersão de aperto (§4). Vale
`RMSE² = viés² + σ²` para o experimento também, e a consequência é que **a perna
de σ_res e a de MAE têm pisos de natureza diferente** — usar o mesmo raciocínio
de tolerância para as duas é erro de dimensão. (Na v1 os números eram 0,024 e
0,060; a razão entre eles quase não mudou — o achado é robusto ao método, foi a
escala que estava errada.)

**O `FLOORS` legado estava certo, e foi ele que denunciou o meu erro.** O legado
dá BAUER fig6 = **0,115** e a v1 media **0,0218** — uma discrepância de 5×. Na
primeira redação deste documento eu a expliquei como "os dois medem coisas
diferentes" e segui adiante. **Estava errado:** com a v2 o Bauer mede **0,0959**,
que é a mesma ordem do legado. A lição de método é a que interessa: uma
discrepância de 5× contra um número **já medido no repo** não é diferença de
definição, é sinal de erro — e explicá-la em prosa em vez de investigá-la custou
uma lista de exceções inteira (23 candidatas onde eram 38).

## 4. Âncoras normativas e de literatura (procedência no repo)

| âncora | valor | fonte |
|---|---|---|
| **Fator de aperto α_A** = F_M,max/F_M,min | 1,0–1,1 (tensionamento hidráulico) · **1,4–1,6 (torquímetro manual)** | VDI 2230 Parte 1 (2015) §5.4.3 — `Models/models/Part_IV_Loading_Models.md:992`, `LOAD_FACTORS_DESIGN.md:784` |
| Dispersão de pré-carga pela variabilidade de µ | **±50%** para o mesmo torque | `Models/models/LOOSENING_MECHANISMS_QUANTITATIVE.md:488` |
| Dispersão de pré-carga em flange real | até **45%**; **±2,1%** com 2 passes otimizados vs **25%** em passe único | `Models/CALIBRATION_AND_VALIDATION/59_60_61_62_wind_turbine_flange_studies.md:94,270` |
| Dispersão de aperto **vista no dado normalizado** | inícios de réplica **0,93–1,08** (±7,5% em F/F₀ antes do 1º ciclo) | `apparatus_notes/bauer2024_efa.md:39` |
| **Margem de decisão normativa** | ISO 16130:2015 zona "boa" em **85%** · DIN 25201-4 aprova em **80%** ⇒ a decisão mora numa faixa de **0,05 em F/F₀** | ISO 16130 / DIN 25201-4; aviso implementado em `coupled_loosening_analyzer.py:2143` |
| **Piso de digitalização** | **±0,005** em F/F₀ (resolução 5%/divisão, marcadores densos) | `apparatus_notes/liu2017_triboint_axial.md:54` |
| Dispersão de espécime em vida | **±17%** (número defensável da fonte) | `apparatus_notes/liu2025_scirep_M16.md:53` |

## 5. Como os limites saem daí

| perna | valor adotado | de onde vem |
|---|--:|---|
| **res.máx** | **0,10** | 22 % ABAIXO do piso mediano corrigido (0,1279; era 25 % acima pela v1) e **2× a margem ISO/DIN** — a única das três que já estava ancorada |
| **MAE** | **0,05** | **= a margem de decisão normativa** (0,85 − 0,80): um erro médio menor que ela não pode inverter o veredicto da norma. Fica **40 % abaixo** do piso mediano corrigido (0,0829; era 17 % pela v1) — escolha consciente de ambição |
| **σ_res** | **0,025** | escolhido na mediana da v1 (0,0241); com a v2 a mediana é **0,0283**, logo o limite ficou 12 % abaixo dela. É 5× o piso de digitalização (0,005), logo mensurável. Pendência no §11 da F7 |

**Contas de impacto (store `3546e6745448`, 203 comparáveis):**

| esquema | passam |
|---|--:|
| vigente até 2026-07-29 (MAE ≤ 0,10 E res.máx ≤ 0,10) | 149 |
| 0,10 / 0,05 / **0,010** (1ª proposta) | 45 |
| **0,10 / 0,05 / 0,025 — ADOTADO** | **105** |
| 0,10 / 0,060 / 0,025 (mediana em ambas) | 109 |
| 0,10 / 0,075 / 0,030 (piso + folga 25 %) | 123 |
| por fonte: max(piso + folga; 0,05/0,10/0,020) | 117 |

**Quantas curvas cada limite torna IMPOSSÍVEIS** (a fonte tem piso medido acima
do limite ⇒ nem o modelo perfeito passa):

| limite | curvas |
|---|--:|
| MAE ≤ 0,05 | 59 |
| MAE ≤ 0,10 | 26 |
| σ_res ≤ 0,010 | **107** |
| σ_res ≤ 0,020 | 68 |
| σ_res ≤ 0,025 | 50 |

É o mesmo argumento das exceções assinadas na F5 (*"a curva ideal já violaria a
meta"*), agora contado em vez de alegado. Sob o tripé adotado, **50 curvas** caem
nessa classe pelo σ_res e **59** pelo MAE — elas são candidatas naturais a
exceção **por prova de piso**, não por julgamento.

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/piso_repetibilidade.py          # regenera a tabela do §3
```

O script é só-leitura (não escreve store nem config) e determinista. Enquanto ele
não estiver versionado, a medição vive no scratchpad da sessão de 2026-07-29 e
esta tabela é o registro.
