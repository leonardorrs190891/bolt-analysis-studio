# É modelo ou é fit? — auditoria MEDIDA, 2026-08-23

**Store `c61366365977`** (uniforme, 210 registros) · `_censo()`: tripé **169/205** · fora 36
· 27 fontes, 17 fechadas 100 %. Só-leitura; nada adotado.

Pedido do professor: *"verifique a integridade do nosso modelo ante aos resultados,
garantindo que não é um fit e sim um modelo"*.

---

## Veredito

**É um MODELO com uma camada de calibração POR RIG — não um fit — e a evidência mais forte
não é a contagem de constantes: são as 38 falsificações registradas.** Um fit não se
falsifica; ele absorve. Este projeto reprovou 17 estruturas numa única curva e registrou
cada uma.

> ⚠️ **ERRATA de 2026-08-23 (sessão do loop), e a culpa é da FONTE, não desta
> auditoria:** este documento dizia **15** aqui e na §2(c) porque
> `liu2025_par_de_taxas_opostas.md` publicava o número como **soma de parciais em
> prosa** (11 → 15 → 16 em seções sucessivas, nenhuma delas se declarando
> parcial). O total correto é **17**, agora derivado de **lista enumerada** no
> topo daquele doc — e o 16 que a declaração canônica citava também estava baixo,
> porque herdava um *"8 constantes"* onde o shell varre **9** alavancas. Número
> que se lê de prosa acumulada não é recomputável: era essa a falha, e ela é
> exatamente do tipo que esta auditoria existe para caçar.

⚠️ **Mas há uma camada fit-like real, medida, em 83 das 207 curvas servidas**, e a §4 diz
exatamente onde.

## 1. A contagem, e por que a média engana

| | |
|---|---|
| volume de dado | **210 curvas · 5256 pontos** pontuados |
| campos numéricos distintos em uso | **79** |
| valores distintos somados | **300** |
| chaves de MODO (string, não consomem DOF) | 8 |
| **razão global** | **1,07 curva por constante fitada** (207 curvas / 194 fitados) |

A razão global de **1,07** é, sozinha, assinatura de **fit**. Mas ela é uma média sobre uma
distribuição fortemente bimodal, e a média é o número errado:

| faixa | grupos | curvas |
|---|---:|---:|
| **ZERO constante fitada** | 12 | **42** |
| ≥ 4 curvas por constante | 7 | **48** |
| 2–4 curvas por constante | 4 | 34 |
| **< 2 curvas por constante (fit-like)** | **48** | **83** |

⇒ **90 curvas (42 + 48) são servidas por grupos model-like**; **83 estão em 48 grupos
fit-like**. O projeto é as duas coisas ao mesmo tempo, em proporções mensuráveis — e dizer
apenas "é modelo" ou apenas "é fit" seria falso nas duas direções.

**Exemplos das duas pontas, medidos:**

| grupo | curvas | fitados | razão |
|---|---:|---:|---|
| `ZHANG_2018` | 9 | **0** | ∞ |
| `LIU_2022_RET` · `CHU_2026` · `LIU_2022_RETIGHT_dry` | 6 cada | **0** | ∞ |
| `LIU_2016` | 13 | 1 | **13,0** |
| `LIU_2020_WEAR` | 9 | 1 | 9,0 |
| `YANG_2021` | 8 | 2 | 4,0 |
| `SUN_2025_CRIMP` | 8 | 6 | **1,3** |
| `YANG_2023_IJPEM_m8` | 6 | 4 | **1,5** |

## 2. O que sustenta "modelo" — quatro evidências independentes

**(a) UMA física para 205 curvas.** Os mecanismos do engine (Embedding, Creep, Wear,
RotationalLoosening, Fatigue) são **os mesmos** em todas as fontes. Nenhuma curva ganha um
mecanismo próprio. As formas transferem cross-rig; as constantes não — que é a posição
declarada do projeto (§8 do `MODEL_LEGITIMACY`) e não uma desculpa retroativa.

**(b) 42 curvas fecham com ZERO constante fitada no grupo** — 3 rodando em default+shared
puro, 39 em grupos cuja procedência é toda de leitura/âncora. Um fit não tem curvas assim.

**(c) 38 falsificações/retratações registradas em git.** Exemplos medidos nos últimos dias:
17 estruturas falsificadas na `liu2025_M16_amp0p8` (ver a errata no topo); a forma da rampa varrida em 28 células
com teto de 1,13×; o `chu test2` adotado, **reprovado no gate e revertido**; a forma axial
do ECCLES **morta antes da primeira linha de código** por falta de driver. ⇒ **o
instrumento tem poder de dizer "não"**, e diz — inclusive contra trabalho já feito.

**(d) O campo mais espalhado é majoritariamente LIDO, não fitado.** O
`loose_arrest_floor` tem **26 valores distintos** — o maior espalhamento do projeto. Dos
**23 grupos** com piso não-nulo, apenas **4** têm procedência `fitado/proxy`; os outros **19
são `lido-do-dado`** (assíntota final da própria curva). ⇒ o espalhamento é **medição por
curva**, não ajuste por curva.

⚠️ **Isto corrige uma afirmação minha de 2026-08-21**, feita ao falsificar a rota do piso
anulável: eu escrevi que os pisos do ECCLES são `proxy-de-desaceleracao-de-cauda
(fitado-this-rig)`. Verdade para `fig7d` e `fig8a` — e eu deveria saber, porque **fui eu que
re-rotulei esses dois na adoção R2**. Mas `fig7a`/`fig7b` são `lido-do-dado`. A família é
**mista**, e a frase "o efeito do axial está absorvido num piso fitado" era mais forte do
que o medido: ele está absorvido em pisos **majoritariamente lidos do próprio dado**. A
falsificação **sobrevive** (a monotonia piso-vs-axial é o que a sustenta, e ela é a mesma),
mas o diagnóstico muda de "fit disfarçado" para "medição no lugar de derivação".

## 3. O teste que mais aproxima de "modelo" — e que o projeto passa

Predição **zero-refit**: constantes calibradas numa condição preverem outra **sem refit**.
Registrado: o `ROUSSEAU_HDPE` previu a Fig. 6 (condição inédita, 2,5× fora da amplitude do
fit) em **0,0267/0,0755/0,0245** — dentro do tripé, sem tocar em nada. E o joelho Su-N
transferiu **M16 ↔ M10** a 5,9 % em tensão de raiz.

⇒ um fit não extrapola 2,5× fora do seu domínio de ajuste e acerta.

## 4. Onde É fit-like, sem eufemismo

**(a) 48 `per_case` tokens em 16 grupos.** Constante **por curva** é a assinatura mais
direta de fit. Piores: `LU_2024` e `SUN_2025_CRIMP` (6 tokens cada), `LIU_2025` e
`ICMEZ_2025` (5), `SUN_2025_REASSY` (5).

**(b) 48 grupos com < 2 curvas por constante, cobrindo 83 curvas.** Nesses, o número de
botões é da ordem do número de curvas que eles explicam. **Não** é possível chamar isso de
predição.

**(c) O caso ECCLES, que é o mais instrutivo do projeto.** A carga axial externa — variável
que o paper **varre** — não entrava no modelo (medido 2026-08-21: os 10 configs eram
IDÊNTICOS). O efeito dela aparecia através de pisos ajustados/lidos **por curva**, que
decrescem monotonicamente com o axial (0,232 / 0,182 / 0,137 para 1,1 / 2,7 / 3,1 kN).
⇒ **um efeito físico entrando por constante per-curva em vez de por lei.** É assim que um
modelo degrada em fit, e é medível.

## 5. O que faria a integridade subir, em ordem de retorno

1. **Derivar** o `loose_arrest_floor` do que o governa (carga axial no ECCLES; torque de
   prevalência da porca) — trocaria até 26 valores por **1 lei + 1 constante**. É a maior
   redução de DOF disponível no projeto.
2. **Reduzir os 48 `per_case`**: cada token é uma dívida de generalização. Onde o token
   existe porque a fonte varre uma variável que o modelo não representa, a rota é
   representar a variável (como o C1/C2 do axial acabou de fazer), não parametrizar a curva.
3. **Publicar a razão curvas/constante por fonte** ao lado do MAE. Hoje o report mostra erro
   e não mostra custo — e as duas juntas é que dizem se a fonte foi explicada ou ajustada.

## 6. A resposta em uma frase

**Não é um fit** — 42 curvas fecham sem nenhuma constante fitada, 38 estruturas foram
falsificadas contra o próprio interesse do projeto, e há predição zero-refit 2,5× fora do
domínio de ajuste. **E não é um modelo puro** — 83 curvas vivem em grupos com quase uma
constante por curva, e 48 `per_case` são dívida de generalização. O que existe é **um núcleo
de física compartilhada com uma casca de calibração per-rig**, e o valor honesto do projeto
está em ter a casca **medida e rotulada** em vez de escondida.

## Reprodutibilidade

Sondas inline (só-leitura) sobre `New_Theory/adopted_configs.json`, o store canônico e
`rn._adopted_for`; classificação de procedência por palavra-chave no campo `prov`
(`fitado|fit-|grade|varredura|proxy|ajust` × `lido|paper|tabela|handbook|norma|âncora|
regressão|medido`). Contagem de falsificações por `git log --all` com padrão
`FALSIFICAD|REPROVAD|MORTO|RETRATAD`.

⚠️ **Limitação declarada da própria auditoria:** a classificação é por **palavra-chave no
rótulo**, não por leitura de cada procedência. Ela erra nos dois sentidos — um
`fitado-this-rig per-par` fisicamente justificado (§4.7, ICs disjuntos) conta como fit, e um
rótulo mal escrito conta como leitura. O número de 194 fitados é, portanto, um **limite
superior**; a §2(d) mostra o tamanho do efeito num campo onde eu verifiquei um a um (23
grupos, 4 fitados de fato contra 19 lidos).
