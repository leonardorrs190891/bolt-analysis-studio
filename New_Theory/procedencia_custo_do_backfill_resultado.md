# O backfill de procedência é **2/3 transcrição** — e as outras duas sondas mentiram

**2026-08-13** · só-leitura · **nada adotado** · store `bd74eaf0b11d`, censo **147/205** ·
serve o **item A** da fila (ASSINADO) · sequela da errata que corrigiu o passivo de
**238 (51 %) → 206 (44 %)**.

## A pergunta

O professor assinou o backfill de procedência "por campo". Antes de gastar o trabalho, a
pergunta que decide **como** fazê-lo:

> Das 206 constantes sem `prov`, quantas já têm o número **escrito em algum registro** — e
> quantas exigem re-derivar, medir ou ler o paper?

A diferença é de ordem de grandeza no custo: transcrever é minutos por constante; re-derivar
é uma sonda, às vezes um prereg.

## ✅ A resposta, com precisão conferida à mão

Casando **campo + valor + fonte** na mesma janela de 300 caracteres, sobre **359 arquivos
`.md`** da campanha (excluídos os documentos que *falam sobre* o passivo — ver a armadilha
abaixo):

| classe | n | % | leitura |
|---|---:|---:|---|
| **TRANSCRIÇÃO** — o número já está escrito num registro | **129** | **63 %** | custo baixo; é bookkeeping |
| **PESQUISA** — o número não aparece em lugar nenhum | **77** | **37 %** | custo real; exige medir ou ler |

**Precisão verificada por amostragem manual:** li **8 hits sorteados**; **6 são procedência
genuína** (nomeiam fonte, campo, valor **e** a razão), 2 são plausíveis mas o trecho exibido
não prova. ⇒ precisão ≈ **85 %**, então a leitura conservadora é *"por volta de 110 das 206
são transcrição"*.

Exemplos do que "transcrição" significa na prática — nenhum deles precisa de medição nova:

* `BAUER_2024_fig6_rep6::slip_regime_mode = off` → *"grupos Bauer com `slip_regime_mode="off"`
  (limiar de Coulomb duro `slip = max(0, δ − µF₀/k_tr)`)"*
* `LIU_2022_RETIGHT_dry::k_wear_scale_tr = 0,06` → *"mantidos: `k_emb_renew` 1.0, `k_gall` 3.0,
  **`k_wear_scale_tr` 0.06** … já adotados"*
* `LIU_2025_amp0p4::c_bend = 50` → *"Liu2025 `c_bend`=50 provavelmente satura no limite
  RÍGIDO"*

## Onde está o trabalho de verdade (as 77)

| campo | n | | fonte | n |
|---|---:|---|---|---:|
| `W_ref` | **12** | | **`LIU`** | **35** |
| `emb_um` | 7 | | `KARLSEN` | 8 |
| `emb_depth` | 7 | | `CACCESE` | 8 |
| `k_dmg_mu` | 5 | | `BAUER` | 7 |
| `mu` | 5 | | `âncora interna` | 6 |
| `c_bend` | 5 | | `YANG` | 5 |
| `c_D_per_lube` · `k_wear_running` · `creep_alpha_sat` · `creep_t_c` | 4 cada | | `ROUSSEAU` · `CHU` | 3 cada |

⇒ **as fontes `LIU_*` sozinhas concentram 45 % do trabalho real.** E o `W_ref` lidera como
campo — coerente com ele ser o denominador de energia do dano, um número que a campanha
sempre herdou do *starter* (1e4) sem ancorar: os 12 que sobram são justamente os que **não**
valem 1e4.

## ⚠️ Duas sondas antes desta deram números confiantes e ERRADOS — na mesma pergunta

Este é o conteúdo metodológico do dia, e vale mais que a tabela.

| versão | critério | resultado | por que estava errado |
|---|---|---:|---|
| v1 | campo mencionado **perto da fonte** | **99 %** transcrição | **auto-referência**: o corpus incluía as próprias tabelas de auditoria que *enumeram* os campos indocumentados. Todo campo aparecia "perto da sua fonte" porque **eu havia listado**. O `ROUSSEAU_HDPE::mu_bearing` casou no documento que eu escrevera horas antes, na linha *"`mu_bearing` 8"*. |
| v2 | campo + **valor** (sem fonte) | **81 %** transcrição | **valores comuns**: exigi o número mas larguei o vínculo com a fonte, e `0,2`/`1,0`/`0,0` estão em toda parte. O `LU_2024::emb_um` foi "achado" num documento do **CHU**. |
| **v3** | campo + valor + **fonte**, corpus limpo, **+ conferência manual** | **63 %** | o que está publicado acima |

**O que pegou cada erro foi ler as amostras, não revisar a fórmula** — a mesma coisa que
pegou o audit de trim em 08-12 (as curvas "mais trimadas" tinham `trim = None`). Um número
agregado plausível não se autodenuncia; **uma linha específica sim**.

⇒ regra que isto acrescenta ao charter: **sonda de proximidade textual sobre o corpus da
própria campanha precisa excluir os documentos que falam do objeto medido**, senão o
instrumento lê a própria saída como evidência. E **todo agregado sai com amostra conferida à
mão**, ou não sai.

## Consequência prática para o item A

O backfill assinado deve ser feito em **duas levas, não uma**:

1. **Transcrição (~129, precisão ~85 %)** — mecânica, barata, sem risco de inventar: o texto
   fonte existe e é citado. Pode embarcar **junto do próximo re-stamp que já vá acontecer**
   (custo marginal zero), o que também evita o problema de escalonamento descrito abaixo.
2. **Pesquisa (77)** — priorizada por `W_ref` (12, argumento único e repetido) e pelas fontes
   `LIU_*` (35). Cada uma exige ler o registro de adoção ou medir; **não** é trabalho de uma
   sessão.

⚠️ **O passivo real é ainda menor que 206 pelo mesmo motivo que já era menor que 238.** O
`CHU_2026_test1::k_dmg_mu = −2,43` foi flagrado hoje como *"fitado, sinal invertido, sem
registro"* e a âncora estava no `MODEL_LEGITIMACY.md` §… (*"PR-38 — µ subindo, o sinal da
Fig. 5"*), confirmada de forma independente pela sessão paralela no mesmo dia (`775ca09`).
**"Sem `prov`" quer dizer "não indexado onde a auditoria olha", não "sem origem".**

## Estado do backfill

⛔ **ADIADO por colisão de escritor** — prereg
`docs/superpowers/specs/2026-08-13-backfill-procedencia-prereg.md`. As 38 primeiras entradas
(os *starters* de dano, `slip_regime_mode='off'`, o default de pack e a herança do grupo-pai
`LIU_2025`) estão escritas e verificadas (gate P4: **0 grupos com `cfg` alterado**), mas o
re-stamp mudaria o `engine_fingerprint()` **debaixo da campanha CHU em curso** na sessão
paralela. Trabalho preservado e idempotente; re-aplicar embarcado no re-stamp deles.

## Reprodutibilidade

`transcrivel.py` (v1, errada — mantida como registro), `transcrivel2.py` (v2, errada) e a v3
inline no histórico da sessão. Só-leitura, ~2 min cada sobre 359 arquivos.

---

## ⚠️ NOTA DE COORDENAÇÃO (sessão B, 2026-08-13 ~20:15) — a FASE 1 foi executada DEPOIS desta medição

A tabela acima fotografa o passivo **antes** do commit `c6aed9d` (20:1x): a
fase 1 assinada (c_bend 16 + W_ref 12 + loose_arrest_floor 12, +4 por chave
composta) foi executada por arqueologia de commit — **atual: 162**. Em
particular, os **W_ref 12** listados como "trabalho real" saíram pelo argumento
de CLASSE (starter físico 1e4, CLAUDE.md 2026-06-20) + dossiê YANG (6e19494) +
re-key CHU — sem pesquisa nova por constante. Re-stamp `66356f20faf8` uniforme,
deriva zero nos 210; guards 22/22.

**Protocolo para as fases 2+** (LIU 35 · KARLSEN 8 · CACCESE 8 …): 1 escritor
por vez em `adopted_configs.json`; quem tomar uma fase **declara aqui antes**
(idioma escritor-declarado), porque cada lote de prov exige re-stamp completo
e dois re-stamps concorrentes colidem no store.

### 🔒 FASE 2 TOMADA pela sessão A (2026-08-13 ~20:20) — *starters* de dano + canal off

Declarado **antes de escrever**, conforme o protocolo acima. Escopo **fechado e
disjunto** do que a fase 1 fez (conferido: 0 sobreposição):

| bloco | campo · valor | n | argumento |
|---|---|---:|---|
| *starter* de dano | `k_dmg_mu` = **1,0** | 8 | `CLAUDE.md` (design surface_damage, 2026-06-20): *"Damage physical starters: c_D=2, k_dmg_mu=1, k_dmg_wear=4, W_ref=1e4"* |
| *starter* de dano | `k_dmg_wear` = **4,0** | 6 | idem |
| *starter* de dano | `W_ref` = **1e4** | 1 | idem (o `CHU_2026_test1`, que a fase 1 não pegou) |
| canal desligado | `slip_regime_mode` = **`'off'`** | 7 | não é constante fitada — desliga o canal; e o registro nomeia a razão física (*"grupos Bauer com `slip_regime_mode='off'`: limiar de Coulomb duro `slip = max(0, δ − µF₀/k_tr)"*) |

**Total: 23** ⇒ passivo **162 → 139** esperado. Mesmo idioma da fase 1: argumento de
**CLASSE**, escrito por executor que **confere o valor antes de escrever** (só escreve onde
o número bate com o *starter*), portanto **não** documenta os outliers — `YANG_2019::W_ref`
= 3000, `CHU_2026_test1::c_D` = 5,5 e `LU_2024::emb_um` = 0 seguem no passivo, de propósito.

Gates: `cfg` intocado · **deriva zero** nos 210 · censo 147/205 · catraca sem pares novos ·
suíte verde.

#### ✅ EXECUTADA — gates 5/5

| gate | resultado |
|---|---|
| `cfg` intocado | **0 grupos alterados** · `prov` 344 → 367 |
| **deriva** | **210 de 210 bit-idênticos** nas 3 pernas (MAE, res.máx, σ_res) — igualdade **exata**, não tolerância |
| fingerprint | `66356f20faf8` → **`72a7aca6311e`**, uniforme nos 210 |
| catraca | passivo **162 → 141**; **0** pares novos; guards **22/22** |
| suíte | verde |

**Passivo do item A na sessão de hoje: 238 (publicado) → 206 (errata) → 162 (fase 1, sessão B)
→ 141 (fase 2).** Cobertura de procedência: 49 % → **70 %**.

### 🔒 FASE 3 TOMADA pela sessão A (2026-08-13 ~21:05) — os campos **auto-documentados**

Declarada antes de escrever. Escopo **deliberadamente estreito**: só os campos cujo **valor
carrega a própria procedência**, onde a citação é exata e não há pesquisa nova.

| campo · valor | n | por que o valor já É a procedência |
|---|---:|---|
| `emb` = `'Rz<4'` (1 como `'Rz<4 (VDI)'`) | **5** | é a **classe de rugosidade da tabela f_Z da VDI 2230**, lida por `library_common.emb_depth_vdi`. O `CLAUDE.md` registra: *"`emb_depth` é um input POR JUNTA … vem da tabela VDI 2230 f_Z por classe de rugosidade"* — input de tabela, nunca knob |
| `mu` = `'Motosh (0.236 dry / 0.176 oil)'` (1 variante per-caso) | **5** | o valor **nomeia o método** (Motosh) **e os números**; adotado no `LIU_2022_RETIGHT` (MEM iter.4, PR-6/5b/7), registrado no `CLAUDE.md` como *"µ Motosh per-lube 0.236/0.176"* |
| `c_D_per_lube` = `'0.5/0.03'` | **4** | chave **`_NON_ENGINE` declarada** em `knowledge_base` — não chega ao engine; estabelecido na auditoria de 08-12 ao desmontar o alarme das "17 órfãs" |

**Total: 14** ⇒ passivo **141 → 127** esperado.

⚠️ **O que ficou FORA, e por quê:** `k_wear_scale_tr` (11), `emb_um` (9), `emb_depth` (8),
`c_D` (6), `C_creep` (6) — todos **dispersos em valor**, logo sem argumento de classe: cada
um exige ler o registro da adoção que o fixou. Também ficaram fora `fatigue_enabled` (4) e
`fat_stress_mode` (4): são uniformes, mas a justificativa é **por curva** (*"esta curva
fratura, conforme o paper"*), não de classe — documentá-los como classe seria o erro que
este trabalho existe para evitar.

#### ✅ EXECUTADA — gates 5/5

| gate | resultado |
|---|---|
| `cfg` intocado | **0 grupos alterados** · `prov` 367 → 381 |
| **deriva** | **210 de 210 bit-idênticos** nas 3 pernas — igualdade exata |
| fingerprint | `72a7aca6311e` → **`98f90e11ebb0`**, uniforme nos 210 |
| catraca | passivo **141 → 127**; **0** pares novos |
| suíte | verde |

**Predição exata:** 14 escritas ⇒ 14 de redução. Sem a redundância da fase 2, porque campos
de **string** não são alcançados por chave composta — o desvio anterior tinha causa
identificada, e ela não se aplica aqui.

**As 14 caem todas na família `LIU_2022*`**, que é parte do balde de "pesquisa" (LIU 35):
⇒ **21 dos 35 do `LIU` seguem sem procedência**, e esses sim exigem ler adoção a adoção.

---

## Placar do item A ao fim de 2026-08-13

| momento | passivo | cobertura |
|---|---:|---:|
| publicado em 08-12 | 238 | 49 % |
| **errata** (chaves compostas) | 206 | 56 % |
| fase 1 — `c_bend` + `W_ref` + `floor` (sessão B) | 162 | 65 % |
| fase 2 — *starters* de dano + canal off (sessão A) | 141 | 70 % |
| **fase 3 — campos auto-documentados (sessão A)** | **127** | **73 %** |

**Metade do passivo original saiu num dia**, e **nenhuma linha de física mudou**: as três
fases somam **deriva zero provada em 210 curvas × 3 pernas**, três vezes seguidas. O que
resta (127) é majoritariamente o balde de pesquisa — sem argumento de classe, uma constante
por vez.

### 🔒 FASE 4 TOMADA pela sessão A (2026-08-13 ~22:45) — **arqueologia com citação verificada**

Primeira fase do balde de **PESQUISA**: sem argumento de classe, cada bloco exigiu **achar o
registro da adoção que fixou o número**. Declarada antes de escrever.

| campo · valor | n | citação **encontrada e verificada** |
|---|---:|---|
| `k_wear_scale_tr` = **0,06** (`LIU_2022*`) | **5** | prereg `2026-07-11-mem-iter4`: *"**nível M12 não-colapsante** (level probe): `k_wear_scale_tr=0.06`"*, com o `liu2022_level_probe.py` no `MODEL_LEGITIMACY` §4.10 |
| `k_wear_scale_tr` = **0,0** (`LIU_2025*`) | **3** | **desliga o canal**: via `tuner_shim` o 0,0 leva `k_wear_spec` a 0 — medido na auditoria de 08-12. Mesmo idioma do `slip_regime_mode='off'` |
| `emb_depth` = **1,09e-06** (`BAUER_2024_fig6*`) | **7** | prereg `2026-07-11-mem-iter4`: *"fig6 PASSA … com c_bend_m8=3.0 (1 fit) + **emb LIDO 1,09 µm**"* — idioma **L24** da campanha (`provenance.emb_from_curve`, "ler em vez de fitar") |

**Total: 15** ⇒ passivo **127 → 112** esperado.

⛔ **`k_wear_scale_tr` = 0,15 do `ANCORA_INTERNA` (3) NÃO entra: busca no corpus deu ZERO
citações.** E é o resultado certo — a âncora interna **saiu do projeto** (decisão do professor,
2026-08-01), então pesquisar procedência ali seria trabalho jogado fora. Fica no passivo,
declaradamente.

Também fora: `emb_depth` = 4,3e-06 do `LIU_2017_axial` (valor diferente, registro próprio) e
os 9 `emb_um`, dispersos em 5 valores.

#### ✅ EXECUTADA — gates 5/5

| gate | resultado |
|---|---|
| `cfg` intocado | **0 grupos alterados** · `prov` 381 → 396 |
| **deriva** | **210 de 210 bit-idênticos** nas 3 pernas |
| fingerprint | `98f90e11ebb0` → **`523ea0069b0d`**, uniforme nos 210 |
| catraca | passivo **127 → 112** (cobertura **76 %**); **0** pares novos |
| suíte | verde |

**Predição exata outra vez:** 15 escritas ⇒ 15 de redução.

⚠️ **O que a fase 4 prova sobre o balde de "pesquisa": ele é menos caro do que a rotulagem
sugeria — mas só porque a campanha escreveu bem os preregs.** As 15 saíram de **duas**
frases já escritas em 2026-07-11 (*"nível M12 não-colapsante (level probe):
`k_wear_scale_tr=0.06`"* e *"emb **lido** 1,09 µm"*), mais um argumento semântico que a
auditoria de 08-12 já havia medido. Nada foi re-derivado; tudo foi **encontrado**. A
distinção transcrição-vs-pesquisa da tabela lá em cima mede *"o valor aparece perto do campo
e da fonte"* — e subestima o que um **prereg bem escrito** guarda, porque lá o número
costuma estar a mais de 300 caracteres do nome do campo.

---

## Placar final do item A em 2026-08-13

| momento | passivo | cobertura |
|---|---:|---:|
| publicado em 08-12 | 238 | 49 % |
| **errata** (chaves compostas) | 206 | 56 % |
| fase 1 — `c_bend` + `W_ref` + `floor` (sessão B) | 162 | 65 % |
| fase 2 — *starters* de dano + canal off | 141 | 70 % |
| fase 3 — campos auto-documentados | 127 | 73 % |
| **fase 4 — arqueologia com citação verificada** | **112** | **76 %** |

**53 % do passivo original saiu em um dia, com deriva zero provada em 210 curvas × 3 pernas,
quatro vezes seguidas.** Nenhuma linha de física foi alterada em nenhuma das quatro.

### 🔒 FASE 5 TOMADA pela sessão A (2026-08-14 ~00:20) — forma do creep do CACCESE + zeros de canal

| campo · valor | n | citação |
|---|---:|---|
| `creep_alpha_sat` = **0,2** e `creep_t_c` = **7,2e8** (`CACCESE_2009*`) | **8** | **adoção D-H** (2026-08-04, prereg `caccese-kernel-creep`): o registro adota literalmente *"`creep_mode="saturating"`, **α = 0,2**, **`t_c` = 100·t_end**"* como **dois números de FORMA compartilhados pelas 7 curvas**. `t_c` = 7,2e8 s confere com 100·t_end |
| `c_D` = **0** (`ANCORA_INTERNA` ×3) · `C_creep` = **0** (`CHU_2026_test1`) · `emb_um` = **0** (`LU_2024`) | **5** | **canal desligado** — zera dano / creep / assentamento; mesmo idioma de `slip_regime_mode='off'` (fase 2) e `k_wear_scale_tr=0` (fase 4) |

**Total: 13** ⇒ passivo **112 → 99** esperado.

⚠️ **Achado de bookkeeping que vale registrar:** o `creep_mode` dos mesmos 4 grupos **já
tinha `prov`**, citando a D-H. Ou seja, a campanha documentou **um dos três números da mesma
adoção** e deixou os outros dois de fora — não por decisão, por descuido de escrita.

#### ✅ FASE 5 EXECUTADA — gates 5/5

`cfg` intocado (0 grupos) · **deriva 210/210 bit-idênticos** · fingerprint
`523ea0069b0d` → **`918128de556b`** uniforme · catraca **112 → 99** (cobertura **79 %**),
0 pares novos · suíte verde.

### 🔎 O filtro de COMPANHEIRAS, medido — e por que ele NÃO é licença

Testando a hipótese acima sobre as 99 restantes (campo sem `prov` num grupo cuja `prov`
cita alguma adoção — `PR-nn`, `D-XX`, prereg, §4.x):

| | n | % |
|---|---:|---:|
| **companheira** de constante já documentada | **92** | **93 %** |
| grupo sem nenhuma `prov` citada | 7 | 7 % |

⇒ **o passivo é, quase todo, omissão de escrita DENTRO de adoções documentadas** — não
constantes que entraram sem justificativa. Concentração: `LIU_2025*` **45** das 92.

⚠️ **E aqui vem o limite que impede transformar isso em atalho.** *"O grupo cita uma
adoção"* **não** implica *"aquela adoção cobre ESTE campo"*. Exemplo real do próprio
levantamento: `CHU_2026_test1::emb_um = 1,6` está num grupo cuja `prov` cita o PR-38, mas o
texto do PR-38 fala de *"mu0 por teste lido da Fig. 5; `c_bend`…"* — **não do assentamento**.
Escrever "PR-38" ali seria inventar procedência com aparência de rastreabilidade, que é
**pior que o silêncio atual**, porque desarma a auditoria seguinte.

⇒ **o filtro é heurística de BUSCA, não de conclusão.** Ele diz onde procurar (e reduz o
espaço de 99 para 92 com pista forte), mas cada entrada continua exigindo **abrir o registro
citado e confirmar que o campo aparece lá**. Foi assim nas fases 4 e 5, e é por isso que
elas renderam 15 e 13 — não 92.

### 🔒 FASE 6 TOMADA pela sessão A (2026-08-14 ~01:05) — o estágio 3 do `LIU_2025`

Aplicando o filtro ao maior aglomerado (`LIU_2025*`, 45 das 92), o registro entregou algo
melhor que pistas: **`liu2025_estudo_curvas.md` §6 é uma TABELA DE PROCEDÊNCIA** das
constantes do estágio 3, com **classe e origem por constante**. Nada a inferir.

| campo · valor | classe declarada | origem registrada |
|---|---|---|
| `fat_m1` = **3,12** | **medido-de-dados-do-paper** | regressão `N_f × σ_root`, **R² = 0,9905**; *"substitui o 2,7 sem procedência"* |
| `fat_Kt` = **0,588** | **input-de-paper (Table 2)** | driver per-rig via `c_σ` = 1081 MPa/mm (M16); caveat do próprio registro: só 2 tamanhos, generalização = pesquisa futura |
| `fat_ramp_D_on` = **0,75** | **handbook** | propagação = últimos 10–30 % da vida HCF ⇒ 0,70–0,90; e `N_D/N_f` **medido** nesta fonte dá **0,72–0,80** |
| `fat_ramp_q` = **8** | **fitado-this-rig** | banda ~5–8, **um** valor para a fonte inteira |
| `fat_stress_mode` = **`'bending'`** | forma | `σ_a = fat_Kt·E·d₂·slip/L_eff²`, prereg `2026-07-11-mem-iter4` |
| `fatigue_enabled` = **True** | adoção | **E2** (2026-07-28, prereg `d721b14`): *"fadiga+rampa com N_f INPUT-DE-PAPER por curva"* — ligar o canal **é** a adoção |
| `W_conf_ref` = **0** | canal off | zera a conformação; não consome DOF |

**7 campos × 3 grupos = 21** ⇒ passivo **99 → 78** esperado.

⚠️ **Isto REVERTE uma exclusão que eu mesmo fizera na fase 3.** Eu havia deixado
`fatigue_enabled` e `fat_stress_mode` de fora, escrevendo que a justificativa deles era *"por
curva, não de classe"*. Estava errado para esta fonte: a **E2 é uma adoção de fonte** cuja
substância é exatamente ligar fadiga+rampa, e o `fat_stress_mode` tem fórmula registrada.
**A evidência mudou, a decisão muda** — e o registro do porquê fica, para que a reversão não
pareça inconsistência.

### 🔒 FASE 7 (2026-08-14 ~01:55) — 14 constantes de uma citação **que eu já tinha em mãos**

O prereg `2026-07-11-mem-iter4` traz a frase que a **fase 4 já usou**:

> *"mantidos: `k_emb_renew` **1.0**, `k_gall` **3.0**, `k_wear_scale_tr` **0.06**,
> `k_wear_running` **5**, `N_wear_run` **100** (já adotados)"*

Ela nomeia **cinco** constantes. Na fase 4 eu extraí **uma**. As outras quatro conferem ao
dígito nos 4 grupos do `LIU_2022_RETIGHT`: `k_gall` 4 · `k_wear_running` 4 · `N_wear_run` 4 ·
`k_emb_renew` 2 = **14** ⇒ passivo **78 → 64** (cobertura **86 %**).

Gates 5/5: `cfg` intocado 0 · **deriva 210/210 bit-idênticos** · fingerprint
`12799ce558d8` → **`054ac8753df1`** uniforme · catraca 78 → 64, 0 pares novos · suíte verde.

#### 💡 O padrão que as fases 5–7 expõem, e que muda a economia do trabalho

A procedência desta campanha foi **escrita em BLOCOS** — uma frase de prereg adota N
constantes de uma vez — mas foi **transcrita para o `prov` em UNIDADES**. Daí o passivo:
não é falta de justificativa, é *sub-extração* de justificativas que já existem.

Três ocorrências medidas, todas do mesmo formato:

| fase | o bloco | documentado antes | extraído agora |
|---|---|---:|---:|
| 5 | adoção D-H (`creep_mode`, `α`, `t_c`) | 1 de 3 | +2 campos × 4 grupos |
| 6 | tabela §6 do estágio 3 | 0 de 7 | +7 campos × 3 grupos |
| 7 | frase "mantidos: …" do mem-iter4 | 1 de 5 | +4 campos × ~4 grupos |

⇒ **reler um registro JÁ verificado procurando as outras constantes que ele nomeia rende
mais do que abrir um registro novo** — e custa quase nada, porque a verificação de
confiabilidade da fonte já foi paga. É a regra operacional para as fases seguintes.

### 🔒 FASE 8 (2026-08-14 ~04:05) — registros NOVOS, e o retorno cai

Primeira fase sem bloco pronto: cada citação exigiu abrir um registro ainda não lido.

| campo · valor | n | citação |
|---|---:|---|
| `emb_amp_exp` = **2,375** e `rho_ref_emb` = **0,6667** (`LIU_2017_axial`) | **2** | **ρ-unificação** (§4.18, adotada 2026-07-08): `S_ρ = min(1,(ρ/ρ_ref)^q)` com `ρ = F_ax_amp/F₀_init` multiplicando o alvo do `EmbeddingLoss` — tira o assentamento da cegueira à amplitude |
| `mu_thread` · `mu_bearing` = **0,2** (`ROUSSEAU_HDPE`) | **2** | transcreve a chave curta `prov['mu']` do próprio grupo: *"0.2 = HDPE do paper (Tabela 1)"* |
| `dmg_dwell_exp` = **1,0** e `f_ref_dmg` = **10,0** (`YANG_2019*`) | **4** | `yang2019_freq_sonda_resultado.md`: *"`dmg_dwell_exp` = 1,0 com `f_ref_dmg` = 10,0 está **adotado**"*; física de fretting-corrosão por *dwell* (Söderberg/Vingsbo) |

**Total: 8** ⇒ passivo **64 → 56** (cobertura **88 %**). Gates 5/5, fingerprint
`054ac8753df1` → **`2c05ea70c046`**, deriva 210/210.

⚠️ **No `dmg_dwell_exp` o caveat foi gravado JUNTO do número, e ele é a parte que importa:**
a sonda mediu **teto de autoridade** — a razão de vida @90 % dá **1,10 para todo expoente de
0 a 8**, e o alvo do dado (1,68–2,24×) está **fora do alcançável**. Uma `prov` que só
dissesse *"adotado 1,0"* documentaria o valor e **esconderia que o canal não explica o efeito
que deveria explicar**. Procedência honesta inclui a medida do que a constante **não** faz.

### 🧩 Terceira convenção de escrita descoberta — e por que NÃO mudei o lookup

O `ROUSSEAU_HDPE` guardava `prov['mu']` cobrindo **dois** campos (`mu_thread`, `mu_bearing`)
sob um **nome curto de família** — nem chave exata, nem composta. É a terceira convenção,
depois da exata e da composta.

Afeta só **2** constantes, e por isso **não** estendi o lookup outra vez. O conserto foi
escrever a **entrada explícita**: chave explícita não exige que o próximo leitor decifre a
convenção, e cada camada de esperteza no lookup é mais uma coisa que pode estar errada sem
avisar — foi exatamente assim que a auditoria original inflou 32.

---

## Encerramento da série (8 fases, 2026-08-13/14)

| momento | passivo | cobertura |
|---|---:|---:|
| publicado 08-12 | 238 | 49 % |
| errata (chaves compostas) | 206 | 56 % |
| f1 (sessão B) · f2 · f3 · f4 | 162 · 141 · 127 · 112 | 65 · 70 · 73 · 76 % |
| f5 · f6 · f7 · **f8** | 99 · 78 · 64 · **56** | 79 · 83 · 86 · **88 %** |

**76 % do passivo original resolvido**, com **deriva zero provada em 210 curvas × 3 pernas
nas oito fases** — nenhuma linha de física alterada em nenhuma delas, suíte 929/1 em todas.

**Rendimento por fase: 23 · 14 · 15 · 13 · 21 · 14 · 8.** A queda é estrutural, não
cansaço: os **blocos** (uma frase que adota N constantes) acabaram, e o que resta exige abrir
um registro por constante. As 56 restantes concentram-se em `LIU_2025*` (≈24, sobretudo
`fat_C1`, `fat_sigma_*`, `delta_free`, `k_ratchet`) e `LIU_2017_axial` (4).

### 🔒 FASE 9 (2026-08-14 ~06:20) — o encerramento foi PREMATURO: mais um bloco existia

Eu havia encerrado a série em 56 escrevendo *"os blocos acabaram"*. **Estava errado**: o
prereg da adoção **E2** (`2026-07-28-liu2025-adocao-prereg.md`, commit `d721b14`) traz uma
**tabela de procedência completa** do bloco de fadiga — classe e origem por constante — e o
bloco JSON congelado, idêntico nas 3 chaves.

| campo | n | classe · origem registrada |
|---|---:|---|
| `fat_sigma_uts` = 800e6 | 3 | **handbook** — *"classe 8.8, d ≤ 16"*. Não é fit: é a UTS da classe do parafuso |
| `fat_sigma_knee` = 0 · `fat_sigma_endurance` = 1 | 6 | membros do **bloco congelado**; zeram o joelho bilinear da Su-N, deixando a **potência única** `m1` — coerente com a leitura registrada *"potência única m≈3,1 sobre σ_root da Table 2"* |
| `fat_C1` | 2 | **o ÚNICO fitado da receita**: ancorado nas 6 vidas de fratura no contexto canônico, **Goodman vivo**, 2 passes, protocolo declarado ANTES de rodar |
| `emb_um` · `N_emb` · `k_ratchet` | 9 | membros do bloco per-rig enumerado em `liu2025_estudo_modelagem.md`; classe *fitado-this-rig no DOF legítimo* |
| `C_creep` · `delta_free` (subgrupos) | 4 | mesmo valor e mesma origem do grupo-pai (chaves standalone no config, mas o número veio da mesma medição) |

**Total: 24** ⇒ passivo **56 → 32** (cobertura **93 %**). Gates 5/5, fingerprint
`2c05ea70c046` → **`55273eab12b0`**, deriva 210/210.

⚠️ **A tabela me fez corrigir o que eu ia escrever.** O prereg **congelou** `fat_C1` =
**4,02544e32**, e o config traz **3,27225e32** / **3,26716e32** — valores **per-curva**,
porque o *rider* da E2 passou a fixá-los pelo `N_f` input-de-paper (mesma coluna da matriz
que os `trim_n_max`). Citar o valor congelado seria acertar o registro e errar o número. A
`prov` gravada descreve a derivação real **e** carrega a claim honesta da E2: *"prevê a curva
**dada** a vida"* — prever a vida segue falsificado pelo relógio (±36 %).

⇒ **lição sobre o meu próprio encerramento:** declarei "blocos esgotados" depois de esgotar
os blocos **que eu conhecia**. O que existia era um prereg de adoção que eu não abrira. A
regra correta não é *"reler o que já verifiquei"* (fase 7) e sim **"todo prereg de adoção é
candidato a tabela de procedência — abra-o antes de declarar esgotamento"**.

### 🔒 FASE 10 (2026-08-14 ~08:20) — sub-extração outra vez, agora espalhada

Aplicando a regra da f9 às fontes restantes. **As quatro entradas são o mesmo padrão:**

| campo | n | citação |
|---|---:|---|
| `ZHANG_2006_fig16::kj_mode` = `'pedersen'` | 1 | **três grupos irmãos** (`ROUSSEAU_HDPE`, `ROUSSEAU_2025`, `ZHANG_2006`) carregam a `prov` **idêntica** — *"Pedersen 2008, rank +24 % Rousseau 2024; substitui `k_j_init` fixo"*. Só o `fig16` ficou sem |
| `retight_loss_gain` = 0,88 | 2 | **adoção D-L**: *"os TRÊS COMPARTILHADOS entre seco e óleo: `base`=0,45, **`gain`=0,88**, `k_emb_renew` 1,0→0,65"*. O `base` já tinha `prov` desta adoção; o `gain`, não |
| `LIU_2022::c_D_dry` = 0,5 · `c_D_oil` = 0,03 | 2 | os irmãos `LIU_2022_RET*` documentam **os mesmos valores** em `prov['c_D']`: *"L7 per-lube **dry**"* = 0,5 e *"**oil**"* = 0,03 |
| `LI_2022_TRIBOINT::fatigue_enabled` · `fat_stress_mode` | 2 | é **o precedente registrado de fadiga do projeto** (*"precedente adotado: `LI_2022_TRIBOINT: fatigue_enabled=True`"*) — e é por causa dele que a rampa do `LIU_2025` nasceu opt-in com default bit-idêntico ao cliff. O `'axial'` é o **default do engine**, registrado para que *ausência de escolha* fique distinguível de *escolha não documentada* |
| `LIU_2016_mos2::mu_bearing` = 0,029 | 1 | transcreve `prov['mu_thread/mu_bearing **(mos2)**']` = *"input-de-paper (DIN 946: 0,029)"* |

**Total: 8** ⇒ passivo **32 → 24** (cobertura **95 %**). Gates 5/5, fingerprint
`55273eab12b0` → **`00197980da92`**, deriva 210/210.

⚠️ **QUARTA variante de chave de `prov` descoberta — e a política se manteve.** O
`LIU_2016_mos2` guarda a chave **composta com anotação**: `'mu_thread/mu_bearing (mos2)'`. O
tokenizador quebra em `/` e `,`, então o token vira `mu_bearing (mos2)` e não casa
`mu_bearing`. **Não estendi o lookup pela quarta vez** — escrevi a entrada explícita, como na
terceira (fase 8). O inventário das convenções encontradas, para quem vier depois:

| # | convenção | exemplo |
|---|---|---|
| 1 | chave **exata** | `prov['C_creep']` |
| 2 | chave **composta** | `prov['c_bend/emb_depth/floor']` |
| 3 | **nome curto de família** | `prov['mu']` cobrindo `mu_thread`+`mu_bearing` |
| 4 | **composta anotada** | `prov['mu_thread/mu_bearing (mos2)']` |

Cada camada de esperteza no leitor é mais uma coisa que pode errar em silêncio — foi
exatamente assim que a auditoria original inflou o passivo em 32.

### 🔒 FASE 11 (2026-08-14 ~09:30) — a **quinta** convenção: a chave NARRATIVA

| campo | n | citação |
|---|---:|---|
| `CHU_2026_test1::mu_thread` = 0,05 · `emb_um` = 1,60 | 2 | ⬅️ **`prov['leituras']`**, uma entrada em **prosa** que documenta várias constantes: *"`mu_thread`=0.05 **paper**; `emb_um`=1.60 **data_implied_early_drop** na curva below-threshold test1 (**leitor L24**; handbook 11.0 µm divergia)"* |
| `ROUSSEAU_2025::emb_um` = 1,0 | 1 | **PR-25 shape-refit** (2026-07-14), no verdict do grupo: *"emb 1.5→1.0 µm — aço melhora mae E std (t10 0,073/0,082 → 0,052/0,057)"* — valor, direção **e** efeito medido |
| `free_spin` = 1,0 (`ROUSSEAU_2025`, `_HDPE`) | 2 | **§4.23** do `MODEL_LEGITIMACY`: forma construída em TDD, *"o arresto passa a travar o DRENO, não a rotação"*. ⚠️ E o registro traz o que mais importa junto do número: **inerte para o tripé** (*"dF₀ intocado ⇒ curvas de preload adotadas inalteradas; só θ e dE"*) |
| `BAUER_2024_fig8::s_crit_loose` = 0 | 1 | membro da forma `graded_scrit` do **PR-12e**, cuja prov o grupo já carrega: *"graded_scrit = **eq. (5) do paper**; k=0,05 fitado-this-rig (seed analítico 0,042 da própria eq. 5)"* |

**Total: 6** ⇒ passivo **24 → 18** (cobertura **96 %**). Gates 5/5, fingerprint
`00197980da92` → **`d3299c170e9d`**, deriva 210/210.

#### ⚠️ O inventário fecha em CINCO convenções — e a melhor prosa é a pior de auditar

| # | convenção | exemplo | achada na fase |
|---|---|---|---|
| 1 | chave **exata** | `prov['C_creep']` | — |
| 2 | chave **composta** | `prov['c_bend/emb_depth/floor']` | errata (08-13) |
| 3 | **nome curto de família** | `prov['mu']` → `mu_thread`+`mu_bearing` | 8 |
| 4 | **composta anotada** | `prov['mu_thread/mu_bearing (mos2)']` | 10 |
| 5 | **NARRATIVA** | `prov['leituras']` documentando 4 constantes em prosa | **11** |

⇒ **a campanha sempre documentou; nunca padronizou ONDE.** Uma auditoria que assume uma
convenção mede a própria suposição — foi isso que produziu 238 contra 206.

E há uma assimetria que vale nomear: a chave **narrativa** é a **melhor prosa do arquivo**
(explica a leitura, cita o instrumento, **rejeita a alternativa com o motivo** — o `emb_um`
do CHU descarta o handbook de 11 µm explicitamente) e simultaneamente a **pior de auditar**,
porque não tem chave própria. **Qualidade do registro e auditabilidade são eixos
independentes**, e otimizar um não entrega o outro.

## As 18 que restam — enumeráveis, e a maioria não é trabalho

| grupo · campo | n | situação |
|---|---:|---|
| `LIU_2017_axial`: `C_creep`, `N_emb`, `creep_conform_exp`, `emb_depth` | 4 | ρ-unificação já documentada; **estes 4 seguem sem registro próprio** |
| `YANG_2019*`: `emb_um` ×2, `slip_onset_W` ×2, `c_D` | 5 | prereg `2026-08-10-yang2019-tripe` é candidato não aberto |
| `KARLSEN_2022_run{2p2,7p1}`: `C_creep`, `c_D` | 4 | o verdict da D-Y cobre `k_ratchet` e a base, **não** estes |
| `ANCORA_INTERNA` ×3: `k_wear_scale_tr` = 0,15 | 3 | ⛔ **zero citações no corpus**, e a âncora interna **saiu do projeto** — pesquisar aqui é trabalho descartado |
| `ZHANG_2006_fig16::emb_um` · `ZHANG_2019::mu_thread` | 2 | isoladas |

⇒ **3 das 18 não devem ser trabalhadas** (âncora interna fora do projeto). O alvo real é **15**.

> # ⚠️ ERRATA DE 2026-08-14 ~10:45 — a classificação abaixo ERROU POR 4, e a causa é a sexta
> # forma de a procedência se esconder
>
> Declarei "13 sem registro" e fui investigar a única coisa que me parecia contraditória — o
> `LIU_2017_axial::emb_depth` = **4,3 µm** contra os **9,5 µm** da §4.6. **Não era
> contradição: era rejeição deliberada e medida do handbook**, e o mesmo parágrafo documenta
> **os quatro** campos do grupo:
>
> > `axial_ground_fit.py` — fit analítico de **formas fechadas** em **~60 amostras das 5
> > curvas COMPLETAS** (não nos 5 pontos finais): `emb_cap` = **4,3 µm** (handbook 3,5) ·
> > `N_emb` = **15** · `C_creep` = **1,45e-11** (âncora interna 1,87e-11) · `exp_fast` = 2,4 ·
> > `exp_slow` = **3,6** (= o campo `creep_conform_exp`).
> > Validação: *slope 2,54e-5 = **96 % do dado**, mediana MAE de curva **0,0033**, tendência
> > erro-vs-carga **ELIMINADA** (topo 0,111 → 0,002)*. Ressalva do próprio registro:
> > *"Liu2017 segue o único P0-sweep ⇒ **fit, NÃO cross-validado**"*.
> > E o handbook VDI foi rejeitado **com número**: MAE médio **0,228 → 0,021 (−91 %)** nas 12
> > condições axiais, porque a tabela sub-resolve superfícies retificadas/lapeadas finas.
>
> ⇒ **fase 12 escreveu 5** (os 4 do `LIU_2017_axial` + `YANG_2019_varamp::c_D`), passivo
> **18 → 13** (cobertura **97 %**).
>
> **A SEXTA forma de esconder procedência:** o registro descreve as constantes pelo **papel
> num script de fit**, com os valores **inline**, numa seção sobre **outro assunto** (o erro
> de nível axial), e escreve a fonte como *"Liu2017"* — não `LIU_2017_axial`. Minha busca
> exigia nome-do-campo **+** valor **+** fonte na mesma janela; **nada disso casava**.
>
> ⇒ regra que fecha o arco: **"sem procedência" só é afirmável depois de LER o registro, nunca
> depois de CONSULTÁ-LO por padrão.** Eu declarei convergência com base numa busca, e o limite
> era a busca — não o arquivo.
>
> As **13** que sobram foram re-buscadas por leitura (incluindo varredura de valores por
> vizinhança semântica, não só por nome) e **seguem sem registro**. A tabela abaixo vale para
> elas, menos as 4 linhas do `LIU_2017_axial`, que estão resolvidas.

## 🏁 O backfill CONVERGIU — as 15 medidas uma a uma (2026-08-14 ~10:00)

Abri os registros das 15 restantes. **Duas têm citação; treze não têm.**

### ✅ As 2 com citação (a escrever no próximo re-stamp que já for acontecer)

| campo | citação |
|---|---|
| `YANG_2019_varamp::c_D` = 0,1 | o grupo irmão traz a composta *"**trio de dano v2 do varamp** — ADOTA `6e19494` (2026-08-10), dossiê `2026-08-10-yang2019-tripe-prereg.md` (5 rodadas pré-registradas, PR-37′ verde, held-out zero-refit melhora as 3 pernas)"* — o texto descreve **esta** adoção, e os dois grupos têm o mesmo 0,1 |
| `LIU_2017_axial::creep_conform_exp` = 3,6 | derivação documentada: *"`creep_conform_exp` + `p_ref_emb` = spread do slope log com F₀ (**regressão nos slopes medidos**)"* |

⚠️ **Não abri um ciclo só para elas.** Cada lote custa um re-stamp completo (~25 min) mais a
suíte (~15 min); duas constantes não pagam isso. A regra eficiente — e a que a fase 1 já
usou — é **embarcar no próximo re-stamp que aconteça por outro motivo**, a custo marginal
zero.

### ⛔ As 13 sem registro, classificadas por POR QUE resistem

| grupo · campo | n | por que não dá para documentar |
|---|---:|---|
| `KARLSEN_2022_run{2p2,7p1}::c_D` = 0,3 | 2 | os companheiros declaram *"`W_ref` **não fitada** — o dano é parametrizado por `c_D`/`k_dmg_*`"*, e 0,3 ≠ o starter 2 ⇒ **foi ajustado**. Mas **o registro do fit não existe no corpus** |
| `KARLSEN::C_creep` = 1e-12 | 2 | o verdict da D-Y cobre `k_ratchet` e a base de F₀, não este |
| `YANG_2019*::slip_onset_W` = 40000 | 2 | o prereg diz *"`slip_onset_W` (**herdado** 40000)"* — herdado **de onde** não está escrito |
| `YANG_2019*::emb_um` = 5,0 | 2 | o prereg diz *"`emb_um` **intocado**"* ⇒ o valor precede o registro |
| `LIU_2017_axial`: `C_creep`, `N_emb`, `emb_depth` | 3 | o verdict é *"sec4.18 — ρ-unificação"*, que cobre `emb_amp_exp`/`rho_ref_emb` (fase 8), não estes. ⚠️ E o `emb_depth` = **4,3 µm** não bate com os **9,5 µm** que o `MODEL_LEGITIMACY` §4.6 registra para a trilha axial |
| `ZHANG_2006_fig16::emb_um` · `ZHANG_2019::mu_thread` | 2 | isoladas, sem irmão nem adoção que as nomeie |

⚠️ **Por que eu NÃO escrevo `prov` para estas.** Seria fácil gravar *"fitado-this-rig,
registro do fit não localizado"* e zerar o passivo. Isso **pioraria** a auditoria: a entrada
contaria como documentada e a lacuna sumiria do radar. **"Ajustado, origem desconhecida" não
é procedência — é a ausência dela, com melhor redação.** O passivo honesto é 18 (15 + 3 do
âncora interna), e é assim que deve ser publicado.

**Sinal de qualidade que fica junto:** das 13, **nenhuma** é constante nova. Todas
antecedem a disciplina de `prov` obrigatória, e a **catraca impede que o conjunto cresça** —
foi essa a decisão que valeu, não o backfill.

## Placar final do item A

| | passivo | cobertura |
|---|---:|---:|
| publicado em 08-12 | 238 | 49 % |
| errata (chaves compostas) | 206 | 56 % |
| f1 → f11 | 162 · 141 · 127 · 112 · 99 · 78 · 64 · 56 · 32 · 24 · **18** | 65 → **96 %** |

**92 % do passivo original resolvido em ~20 h**, com **deriva zero provada em 210 curvas × 3
pernas nas onze fases** e **nenhuma linha de física alterada**.

⚠️ **Dois desvios da predição, ambos meus e ambos registrados:**

1. **Escrevi 23, o passivo caiu 21.** Meu executor pula por `prov.get(campo)` **exato** — o
   mesmo ponto cego que a errata de hoje corrigiu na auditoria, ainda presente **nele**. Em
   2 campos já cobertos por chave composta ele gravou uma entrada explícita redundante.
   Inócuo (a entrada apenas repete o que a composta dizia), mas é exatamente o tipo de coisa
   que vira número errado quando ninguém confere.
2. **O batch grava 209 de 210** — o `exemplo_m12_sintetico` fica fora do universo dele
   (gotcha documentado). Consertado por re-simulação direta: métricas **bit-idênticas** ao
   store anterior antes de gravar, e só então o carimbo. ⚠️ Ao regravar, usei `indent=1` e o
   store foi de 8,3 MB / 1 linha para **10,5 MB / 597 446 linhas** — um diff ilegível num
   repo cujo `.git` já é o gargalo. Regravado com `json.dumps` puro: **8 258 258 bytes, o
   mesmo tamanho ao byte**, diff de 1 linha. **Formato de arquivo grande é parte do
   contrato**, não detalhe de serialização.
