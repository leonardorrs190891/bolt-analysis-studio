# Varredura das 3 classes — os 55 fora do tripé, curva a curva

> **2026-07-28.** Item 3 da fila de decisões, autorizado. Medido no store
> certificado `4f5bedfbace4` (203 registros, fingerprint único, os 3 vetores
> da métrica presentes em 203/203). **Só-leitura:** nenhuma simulação, nenhum
> fit, nenhuma adoção. Script: `New_Theory/frontier_classes.py`; números
> crus por curva: `New_Theory/frontier_classes.json`.

> **Fronteira declarada (sessão paralela).** Uma segunda sessão tem um
> pré-registro de métrica ativo com gates congelados
> (`specs/2026-07-28-metrica-banda-v2-prereg.md`). Esta varredura mede sob a
> métrica **canônica de hoje** e **não é evidência a favor nem contra**
> aquele prereg: seus números não devem ser importados para os gates dele,
> sob pena de virar evidência post-hoc dentro de um pré-compromisso. Pela
> regra §4.43, se a métrica canônica mudar, **esta classificação vira
> suspeita e tem de ser re-rodada** — em particular a classe METRIC-LIMITED,
> que é definida contra a convenção vigente.

---

## 1. Resultado em uma frase

**19 das 55 curvas fora do tripé não pedem física nova** — pedem ler um nível (8), decidir uma convenção de métrica (8) ou mexer no dado (3). As outras **36** são form-limited de verdade.

| classe | n | ação que fecha | custo |
|---|--:|---|---|
| **LEVEL-LIMITED** | 8 | ler o nível | leitura com procedência |
| **METRIC-LIMITED** | 8 | decidir a convenção: isentar a família do `FLOOR_TRIM` e medir a curva inteira; mudar o eixo da métrica | decisão de convenção |
| **DATA-LIMITED** | 3 | nada a fazer no modelo: a meta está abaixo da reprodutibilidade do ensaio; redigitalizar mais fino | dado novo (ou exceção assinada) |
| **FORM-LIMITED** | 36 | construir mecanismo | prereg + gate, 1 forma por vez |

**34 das 55 violam SÓ o `maxerr`** (o MAE já está dentro) — reprodução independente do censo de 07-27 (34 pelo pico, 21 pelos dois), o que confirma que esta varredura lê o mesmo conjunto da certificação. E **8 das 8 LEVEL-LIMITED** violam só o pico: nelas o nível é o único obstáculo.

---

## 2. As curvas que NÃO pedem forma

`sobra` = `max|resíduo − média(resíduo)|`, o que restaria do pico se o nível
fosse consertado. `resg` = fração dos pontos que o modelo alcança dentro de
0,10 deslocando-se no máximo UM intervalo de amostragem do dado.
`n` = pontos pontuados / pontos crus do CSV.

### LEVEL-LIMITED (8)

| curva | fonte | MAE | maxerr | sobra | resg | n | motivo |
|---|---|--:|--:|--:|--:|--:|---|
| `liu2016wear_fig7_run2_5e6cyc` | LIU_2016 | 0.060 | 0.103 | 0.060 | 0.61 | 39/39 | nivel |
| `chu2026ti_D0p3mm_F0_49kN_test1` | CHU_2026 | 0.066 | 0.115 | 0.066 | 0.87 | 23/24 | nivel |
| `bauer2024_M12_fig8_test3` | BAUER_2024 | 0.024 | 0.120 | 0.097 | 1.00 | 23/24 | nivel |
| `eccles2010_fig8a_no_axial_baseline1` | ECCLES_2010 | 0.044 | 0.122 | 0.080 | 1.00 | 10/24 | nivel |
| `lu2024_M8_fig20_T22Nm` | LU_2024 | 0.052 | 0.125 | 0.073 | 0.92 | 13/18 | nivel |
| `bauer2024_M8_fig6_rep6` | BAUER_2024 | 0.076 | 0.130 | 0.083 | 0.93 | 27/27 | nivel |
| `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | LIU_2020_WEAR | 0.073 | 0.134 | 0.073 | 0.78 | 23/23 | nivel |
| `rousseau2025_hdpe_t12` | ROUSSEAU_2025 | 0.064 | 0.138 | 0.080 | 1.00 | 13/13 | nivel |

**Ação:** ler o nível (`loose_arrest_floor`) com procedência — zero física nova

### METRIC-LIMITED (8)

| curva | fonte | MAE | maxerr | sobra | resg | n | motivo |
|---|---|--:|--:|--:|--:|--:|---|
| `bauer2024_M8_fig6_rep5` | BAUER_2024 | 0.049 | 0.112 | 0.098 | 1.00 | 13/15 | resgate_horizontal |
| `chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9` | CHU_2026 | 0.045 | 0.117 | 0.102 | 1.00 | 25/26 | resgate_horizontal |
| `lu2024_M8_fig20_T16Nm` | LU_2024 | 0.035 | 0.129 | 0.138 | 1.00 | 17/17 | resgate_horizontal |
| `eccles2010_fig8b_axial_0p7kN_intermittent` | ECCLES_2010 | 0.044 | 0.130 | 0.110 | 0.88 | 8/35 | floor_trim |
| `lu2024_M8_fig18_amp0p5` | LU_2024 | 0.061 | 0.147 | 0.155 | 1.00 | 17/17 | resgate_horizontal |
| `bauer2024_M12_fig8_test2` | BAUER_2024 | 0.029 | 0.179 | 0.164 | 1.00 | 26/27 | resgate_horizontal |
| `lu2024_M8_fig18_amp2p0` | LU_2024 | 0.115 | 0.194 | 0.241 | 0.86 | 7/13 | floor_trim |
| `lu2024_M8_fig18_amp1p5` | LU_2024 | 0.107 | 0.278 | 0.294 | 0.90 | 10/15 | floor_trim |

**Ação:** decidir a convenção: isentar a família do `FLOOR_TRIM` e medir a curva inteira · mudar o eixo da métrica (o dado existe e a forma acerta)

### DATA-LIMITED (3)

| curva | fonte | MAE | maxerr | sobra | resg | n | motivo |
|---|---|--:|--:|--:|--:|--:|---|
| `bauer2024_M8_fig6_rep1` | BAUER_2024 | 0.043 | 0.126 | 0.084 | 0.93 | 14/16 | scatter_replica |
| `10_Yang_2023_phenomenological_model__0_50_mm__9` | YANG_2023_IJPEM | 0.156 | 0.274 | 0.195 | 1.00 | 5/6 | resolucao_grossa |
| `bauer2024_M12_fig8_test1` | BAUER_2024 | 0.074 | 0.397 | 0.329 | 0.76 | 25/26 | scatter_replica |

**Ação:** nada a fazer no modelo: a meta está abaixo da reprodutibilidade do ensaio · redigitalizar mais fino (hoje o dado não resolve o relógio)

> **Caveat da classe LEVEL-LIMITED — condição necessária, não prova.**
> `sobra < 0,10` diz que o erro *é* de nível: removido um deslocamento
> uniforme, o pico entra no tripé. Não prova que **ler o `loose_arrest_floor`**
> o remove, porque o piso age na **cauda**, não uniformemente em todos os
> ciclos. A direção necessária está na coluna `res.médio`: positivo = o modelo
> retém mais que o dado (precisa de piso **menor**), negativo = retém menos
> (piso **maior**). Fechar cada uma exige a leitura com procedência e o gate
> — o que esta varredura entrega é que essas 7 **não precisam de forma nova**.
> **[MEDIDO EM 2026-07-28, LEIA ANTES DE AGIR: `level_seven_probe.md`.](level_seven_probe.md)**
> As duas alavancas de nível que a campanha sabe **ler** do dado
> (`loose_arrest_floor` do platô, `emb_depth` da queda-inicial) foram sondadas
> nas 7: **fecham 1**, melhoram 1, 1 é inerte e **3 PIORAM**. Ou seja "não
> precisa de forma nova" **não** significa "fecha de graça" — o nível dessas
> curvas não é alcançável pelos leitores existentes, e a ação para 5 das 6 é
> uma pergunta aberta, não uma leitura.

| curva | res.médio | direção do piso |
|---|--:|---|
| `chu2026ti_D0p3mm_F0_49kN_test1` | -0.0663 | maior (modelo retém de menos) |
| `eccles2010_fig8a_no_axial_baseline1` | -0.0426 | maior (modelo retém de menos) |
| `bauer2024_M12_fig8_test3` | +0.0228 | menor (modelo retém demais) |
| `lu2024_M8_fig20_T22Nm` | +0.0517 | menor (modelo retém demais) |
| `rousseau2025_hdpe_t12` | +0.0572 | menor (modelo retém demais) |
| `liu2016wear_fig7_run2_5e6cyc` | +0.0603 | menor (modelo retém demais) |
| `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | +0.0729 | menor (modelo retém demais) |
| `bauer2024_M8_fig6_rep6` | +0.0744 | menor (modelo retém demais) |

---

## 3. Controle: contra veredictos já estabelecidos

O classificador foi confrontado com 9 veredictos que **outros** diagnósticos
já fixaram sobre o mesmo store. **7 dos 9 coincidem.** As 2 divergências não
são ruído — cada uma corrige uma afirmação anterior, com número:

**(a) `eccles2010_fig6` — eu esperava METRIC-LIMITED, mediu FORM-LIMITED.**
A trilha B de 07-27 nomeou fig6 na família cujo dado cru vai a ZERO, e eu li
isso como "dominada pelo `FLOOR_TRIM`". Medido: o piso come **4 de 29**
pontos (14%) no fig6, contra **27 de 35** (77%) no fig8b. Além disso o fig6
tem planura 0,226 (forma francamente errada) e **32% dos pontos não são
resgatáveis** por deslocamento nenhum. Ou seja: pertencer à família do achado
do `FLOOR_TRIM` ≠ ser limitada por ele. **Consequência prática:** a decisão
(i) de 07-27 — isentar a família do piso e medir a curva inteira — mudaria o
veredicto do **fig8b**, e não do fig6/fig8d, que seguem form-limited
(coerente com o G-B1 FAIL: aplicar a receita levou o fig6 de 0,467 a 1,028).

**(b) `eccles2010_fig8c` — eu esperava LEVEL-LIMITED, mediu FORM-LIMITED por
0,002.** O `kernel_diagnostic` mediu o perfil detrendado do par fig8a+fig8c
**na média das 2 curvas** (máx |0,022|); por curva a planura é 0,047 e 0,054.
E o que decide: com o nível consertado sobra **0,0797** no fig8a (entra) e
**0,1021** no fig8c (**não** entra, por 0,0021). Então a recomendação nº 2
daquele diagnóstico — "tentar nível antes de forma; se o floor fechar, custam
zero física nova" — vale para **uma** das duas, não para as duas. O fig8c fica
na fronteira: nível quase fecha, e o que sobra é um pico localizado.

Os 3 números de `FLOOR_TRIM` que este script mede sozinho (fig6 **4/29**,
fig8b **27/35**, fig8d **7/37**) reproduzem **exatamente** os publicados em
07-27 — é a validação de que o pipeline de dado cru aqui é o do runner.

---

## 4. As 36 form-limited, por fonte

`resg mín` = a curva menos resgatável da fonte. Quanto menor, mais o erro é
de forma e não de relógio.

| fonte | n | maxerr | resg mín |
|---|--:|---|--:|
| YANG_2023_IJPEM | 6 | 0.560, 0.427, 0.420, 0.360, 0.342, 0.160 | 0.43 |
| CHU_2026 | 5 | 0.464, 0.346, 0.271, 0.248, 0.174 | 0.16 |
| LU_2024 | 5 | 0.256, 0.231, 0.231, 0.225, 0.193 | 0.40 |
| YANG_2019 | 4 | 0.517, 0.194, 0.142, 0.136 | 0.42 |
| ECCLES_2010 | 3 | 0.467, 0.252, 0.145 | 0.40 |
| JCSR_2023 | 2 | 0.131, 0.124 | 0.85 |
| ROUSSEAU_2025 | 2 | 0.188, 0.153 | 0.79 |
| ANCORA_INTERNA | 2 | 0.176, 0.158 | 0.48 |
| YANG_2021 | 2 | 0.163, 0.142 | 0.57 |
| BAUER_2024 | 1 | 0.171 | 0.83 |
| KARLSEN_2022 | 1 | 0.236 | 0.86 |
| SUN_2025_CRIMP | 1 | 0.319 | 0.69 |
| YANG_2023_AME | 1 | 0.465 | 0.13 |
| ZHANG_2006 | 1 | 0.661 | 0.53 |

O `resg mín` separa duas coisas dentro da mesma classe: **CHU (0,16)** e
**YANG_2023_AME (0,13)** erram de forma em quase todo ponto — nenhum
deslocamento salva. Já **JCSR (0,85)** e **KARLSEN (0,86)** erram em poucos
pontos, o que as torna as form-limited mais próximas de fechar.

---

## 5. O que isto muda na fila de decisões

1. **A fila deixa de ter 55 itens de uma classe só.** As ações se separam em
   4, e **19 curvas** saem da conta de "precisa de física nova" — que era o
   ponto do item 3.
2. **7 curvas de nível são o alvo mais barato da meta** (as 7 violam SÓ o
   pico), e estão em **7 fontes diferentes** — não é uma fonte com problema,
   é o piso lido por par. Nenhuma delas exige prereg de forma.
3. **A decisão de convenção do `FLOOR_TRIM` vale 3 curvas**, não a família
   toda: `eccles fig8b` + `lu2024 amp1p5/amp2p0` (o LU também tem dado que vai
   a zero — 33% e 46% dos pontos sob o piso, o que não estava registrado).
4. **`bauer2024_M8_fig6` ×4 confirma-se irredutível** — espalhamento entre
   réplicas **0,459** na sobreposição comum (a lista F5 traz 0,561, medido em
   janela maior; as duas são 4-5× a tolerância da meta).
5. **Uma curva do YANG_2023_IJPEM é data-limited, não form-limited:** a
   `0,50 mm` é pontuada sobre **5 pontos**, e com essa resolução o dado não
   distingue relógio nenhum. As outras 6 seguem form-limited com maxerr
   0,16-0,56 — a tri-falsificação do item 1 da fila continua válida para elas.

**Nada aqui autoriza adoção.** É diagnóstico: cada ação da coluna "ação que
fecha" continua exigindo a decisão e o gate que a campanha já prevê.

---

## 6. Errata 2ª: o classificador por-curva era cego a limite por-família

A sessão paralela achou o defeito por outro caminho
(`replicate_impossibility_sweep_2026-07-28.md` §3.1) e a frase é dela:
*um classificador por-curva é cego para limite por-família.*
`bauer2024_M12_fig8_test1/2/3` são **três repetições do mesmo ensaio** e a
1ª versão deste classificador as pôs em **três classes diferentes**
(FORM / METRIC / LEVEL) — três repetições não podem exigir três consertos.

**Por que passou:** o agrupamento de réplicas era por **nome** (`_repN$`),
e a fig8 do Bauer usa `testN`. A observação deles fecha o diagnóstico —
*"a diferença de vocabulário (`test` na fig8 vs `rep` na fig6) é escolha do
digitalizador, não distinção de condição"*.

**Conserto:** as réplicas passam a ser achadas por **condição declarada
idêntica** (`cond_key`) com os nomes diferindo **só por índice**
(`token_diff` vazio). Isso reproduz o veredicto deles **sem depender da
nota de aparato** — e as 3 curvas que eles provaram irredutíveis são
exatamente as 3 que este critério move.

| curva | classe na 1ª versão | agora |
|---|---|---|
| `bauer2024_M12_fig8_test1` | FORM-LIMITED | **DATA-LIMITED** |
| `bauer2024_M12_fig8_test2` | METRIC-LIMITED | **METRIC-LIMITED** |
| `bauer2024_M12_fig8_test3` | LEVEL-LIMITED | **LEVEL-LIMITED** |

**Efeito no censo:** FORM 36 → **35** · METRIC 7 → **6** · LEVEL 7 → **6**
· DATA 5 → **8**. O número que o Manual publicou (36 form-limited) está
**superado** — 35.

**O que o conserto NÃO faz:** `ValidationCase` **não tem campo para carga
axial nem para rugosidade** (no ECCLES a axial vive no `notes`/`case_id`;
no CHU a rugosidade só no `case_id`), então a chave de condição sozinha
junta varreduras deliberadas — medido, ela merge as **10** curvas do
ECCLES num grupo. É o filtro de tokens que separa: dos 3 grupos com
classes divergentes, **1** é defeito real (Bauer, só índices) e **2** são
explicados por condição no nome (`ra1p6um`; `0p7kn…3p5kn`).
Denúncias vivas hoje: **7** curvas em famílias incoerentes.

---

## 6b. Errata 3ª: a errata 2ª super-atribuía — e o motivo era a GRADE

A errata 2ª fez o critério (1) marcar **todos** os membros de um grupo com
dispersão > 0,10 como DATA-LIMITED. Está errado: dispersão alta prova que
**ao menos um** membro viola, não que todos violem. Corrigido com o **teto
de grupo** por busca exaustiva — o maior subconjunto com dispersão ≤ 0,20 —
e só entra em DATA-LIMITED quem não cabe em **nenhum** subconjunto máximo.

**Achado de método, e o defeito era meu:** a 1ª tentativa deste cálculo
contradisse a varredura de réplica (dava teto 4 onde ela dá 3), e a causa
era a **grade de interpolação**. Medido no subconjunto `{rep2,3,4,5}` do
BAUER fig6:

| pontos na grade | dispersão | ≤ 0,20? |
|--:|--:|:--:|
| 20 | 0.19478 | sim |
| 40 | 0.19944 | sim |
| 100 | 0.20037 | **não** |
| 400 | 0.20125 | **não** |
| 2000 | 0.20134 | **não** |

Com 40 pontos ele passa e o teto sai **4**; convergido, falha e o teto é
**3**. Uma sub-resolução de ~1 % virou um veredicto de teto — e a grade
agora é **800** pontos, convergida com margem.

**Onde as duas análises convergem e onde divergem** (contra a
`replicate_impossibility_sweep_2026-07-28.md`, versão corrigida):

| | varredura de réplica | aqui |
|---|---|---|
| teto BAUER fig6 | 3 de 6 | **3 de 6** ✅ |
| teto BAUER fig8 | 2 de 3 | **2 de 3** ✅ |
| nome no fig8 | `test1` | **`test1`** ✅ |
| nome no fig6 | `rep1`, `rep5`, `rep6` | **só `rep1`** ❌ |

A divergência é precisa e é sobre **contagem vs nome**: o teto 3 de 6 diz
que **3 curvas têm de ser exceção** (isso bate), mas existem **3**
subconjuntos viáveis de tamanho 3 — `{rep2,rep3,rep4}` (0,0738),
`{rep3,rep4,rep5}` (0,1938) e `{rep3,rep5,rep6}` (0,1909). Como `rep5` e
`rep6` aparecem em algum deles, elas **não são necessariamente** exceção:
quais 3 falham depende de qual subconjunto o modelo realiza. Só `rep1` está
em nenhum. A varredura tomou o melhor subconjunto (`rep2/3/4`) como se
fosse o único.

**Exceções necessárias POR NOME neste conjunto: 2** — 
`bauer2024_M12_fig8_test1` · `bauer2024_M8_fig6_rep1`.
**Por contagem**, somando os tetos de grupo, são **6** (3 do fig6 + 1 do
fig8 + 1 do Eccles no-axial + 1 de resolução grossa) — o mesmo total da
varredura de réplica. O Eccles não aparece nomeado aqui porque a chave de
condição **não isola o subgrupo no-axial**: `ValidationCase` não tem campo
de carga axial (§6).

---

## 7. Reprodutibilidade

```
py -3.12 New_Theory/frontier_classes.py
```
Critérios, limiares e ordem de decisão estão no cabeçalho do script,
com a errata das duas passadas descartadas. Todo `flags_todos` vai ao JSON:
curva que satisfaz mais de um critério não some na escolha de ordem.
