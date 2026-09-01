# O shell de ataque estava **CEGO** para metade das alavancas — e isso invalida vereditos meus

**2026-08-09 (noite)** · só-leitura · **nada adotado** · consequência direta de estender o
shell com a varredura conjunta do **D-AA**.

## O defeito, em uma frase

`ataque_curva.py` lia a base de cada alavanca de **`_effective_overrides`** — que só contém o
que o `adopted_configs.json` declara **explicitamente**. Toda constante parada no **default de
`JointMaterial`** era **pulada em silêncio**, sem uma linha no relatório.

Duas das mais importantes estavam exatamente nessa situação em quase toda curva:

| constante | default | aparecia na sonda? |
|---|---:|---|
| `N_emb` (relógio do embedding) | **50** | **não**, salvo se o cfg a declarasse |
| `tr_loose_gain` (ganho rotacional) | **2,0** | **não**, idem |

⇒ o shell imprimia *"NENHUMA alavanca livre fecha — candidata a FORMA, não a constante"*
**sem ter tocado metade das constantes do canal**. O veredito parecia medição e era ausência
de medição.

## Quanto isso muda — medido na `rousseau2025_steel_t10_amp0p2`

| | antes do conserto | depois |
|---|---|---|
| alavancas sondadas | **2** (`creep_conform_exp`, `emb_depth`) | **7** |
| melhor resultado | nenhum move | `N_emb`=25 → **0,0486 / 0,0939** / 0,0342 |
| veredito | *"candidata a FORMA"* | **MAE e res.máx PASSAM**; só o σ viola (1,37×) |

Nominal: 0,0957/0,1545/0,0412. Com `N_emb`=25 o MAE cai **49 %** e o res.máx entra no limite.
Não é "a curva fechou" — é que a distância deixou de ser 3 pernas e passou a ser 1, e o
diagnóstico anterior dizia o oposto.

Outras que também moveram e antes nem apareciam: `C_creep` ×4 → 0,0534/0,0949/0,0398;
`k_wear_spec` ×10 → 0,0745/0,1271/0,0381; `emb_depth` ×1,3 → 0,0575/0,0992/0,0394.

## ⚠️ E o caso que muda um veredito MEU do mesmo dia: `eccles2010_fig7c`

De manhã eu publiquei, sobre esta curva, que *"não há correção legítima de procedência"* e que
ela *"segue form-limited"*. A parte de procedência continua de pé (o helper canônico dá
`plateau=True`, valor 0,1800, e o cfg 0,182 bate). **A parte de alavanca não:** com o
instrumento consertado, **quatro doses fecham o tripé**, três delas com procedência LIVRE.

| alavanca | dose | resultado | prov |
|---|---|---|---|
| `N_emb` | **35** | **0,0229 / 0,0748 / 0,0203** | livre |
| `C_creep` | 3,73e-11 | 0,0247 / 0,0490 / 0,0217 | livre |
| `C_creep` | 2,8e-11 | 0,0249 / 0,0530 / 0,0237 | livre |
| `emb_depth` | 1,43e-05 | 0,0327 / 0,0749 / 0,0168 | livre |

Nominal: 0,0250/0,0612/0,0258 (σ a 1,03× do limite — ela reprova **por 3 %**).

Nenhuma dessas alavancas aparecia no relatório anterior: `N_emb` porque estava no default, e
as demais porque o canal delas nem chegava a ser listado. ⇒ **a `fig7c` é candidata a adoção,
não a form-limited.** Adotar exige prereg com gates congelados e assinatura — está fora do
mandato autônomo, e fica registrado como candidato medido.

## Segundo defeito, achado no mesmo passo: alavanca **não-injetável** lida como morta

`emb_depth` é **derivado de `emb_um`** dentro de `material_kwargs_for`, **depois** dos
overrides. Injetá-lo por override é **no-op**, e a sonda marcava `= nominal (INERTE)` — texto
que se lê como *"o parâmetro não faz nada"* quando o correto é *"o instrumento não alcança o
parâmetro"*. São afirmações opostas sobre a física.

⚠️ **A minha primeira versão desse aviso estava errada** e a `fig7c` a derrubou na mesma
hora: eu marcava a alavanca como não-injetável **pela presença de `emb_um` no cfg**, e a
`fig7c` tem `emb_um` **e** responde a `emb_depth` (0,0250 → 0,0327). Presença do input **não
implica** no-op. O que decide é a **inércia medida**; o input apenas nomeia o suspeito. O
shell agora só escreve a suspeita quando as **duas** condições valem:

```
inerte E derivavel de `emb_um` -- SUSPEITA de no-op do injetor,
nao conclua 'parametro morto' sem checar
```

Onde isso de fato se aplica é a `yang2021_amp0p5mm_ax8kN`: ali `N_emb` é inerte nas **4**
doses **e** `emb_depth` é inerte nas 2, com o embedding sendo o canal **dominante**. Uma
curva cujo canal dominante não responde a nenhuma das suas duas constantes é sinal de que o
injetor não a alcança — ou de algo mais estranho. Veredito honesto: **não sei**, não *"é
forma"*.

## ⚠️ O que isto obriga a reabrir

Todo veredito *"nenhuma alavanca fecha / candidata a FORMA"* que este shell produziu **antes
desta noite** foi emitido pelo instrumento cego. Isso inclui os que **eu publiquei hoje**:
`jcsr2023_galv_seawater`, `jcsr2023_plain_seawater` (resolvidas depois por outra via — D-Z e
D-AA —, logo o erro não propagou), `jcsr2023_plain_outdoor`, `jcsr2023_stainless_seawater`
(resolvida no D-AA) e `eccles2010_fig7c_axial_2p7kN_constant`.

**A regra que fica:** um veredito negativo de sonda só vale acompanhado da **lista do que foi
sondado**. "Nenhuma fecha" sem essa lista é indistinguível de "nada foi testado" — foi
literalmente o caso aqui, com 2 de 7.

## Isto é a mesma classe de erro de três outros da campanha

1. **`creep_sat_tc` / `creep_sat_alpha`** (D-Z, hoje de manhã): campo inexistente, filtrado em
   silêncio pelo `JointMaterial`.
2. **`flank_transverse_on`** (2026-08-01): Δ=0 lido como "canal morto" quando o companheiro do
   canal estava desligado.
3. **`trim_n_max` via overrides** (2026-07-30): no-op silencioso porque o runner o lê direto do
   `kb`.

Todos têm a mesma forma: **o caminho de injeção não alcança o parâmetro, e o silêncio é lido
como resultado.** O conserto genérico é o que o shell passou a fazer — declarar o que **não**
consegue alcançar, em vez de reportar o valor nominal como se fosse resposta.

## Reprodutibilidade

```bash
py -3.12 New_Theory/ataque_curva.py rousseau2025_steel_t10_amp0p2
py -3.12 New_Theory/ataque_curva.py yang2021_amp0p5mm_ax8kN
```
