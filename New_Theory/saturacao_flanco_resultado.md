# D-Q — SATURAÇÃO DO CANAL DE FLANCO por profundidade restante

**2026-08-05** · decisão **D-Q** (por delegação; o professor autorizou em sessão:
*"adote se o G1 passar"*) · prereg
`docs/superpowers/specs/2026-08-05-saturacao-flanco-prereg.md`, fingerprint de
partida `b072b24fd3a8`.

## A forma, e o laço que ela fecha

```
d_w *= max(0, 1 − state.delta_thread_fret / flank_fret_depth)
```

Mesma estrutura *state-based* que o `EmbeddingLoss` recebeu em 2026-07-02: o
incremento depende da **profundidade que ainda falta**, não do relógio.
`flank_fret_depth = 0` ⇒ **OFF exato** (G0 verificado: bit-idêntico).

**`delta_thread_fret` já era acumulado** (engine linha 1853) e lido **só** para
contabilidade de energia (linha 2374) — **nunca realimentava a lei que o
alimenta**. Esta forma fecha esse laço.

Física: o fretting de flanco remove material até a folga acomodar o movimento;
então o contato re-conforma, a área cresce, a pressão cai e o transporte líquido
para. É o regime de **shakedown** que o docstring de `flank_wear_from_slip` já
citava (Mantyla 2020 / Juoksukangas 2016).

## G1 — o gate que decidia: transferência CEGA para o LIU_2016

O `LIU_2016` tem o canal de flanco ativo (`flank_wear_on=1`, `flank_amp_exp=1,5`,
`k_wear_flank=4,325e-14`) e estava **14/14 no tripé**. Recebeu a **mesma**
`flank_fret_depth`, compartilhada.

**Previsão registrada antes de medir: "não sei se sobrevive; palpite honesto
50/50."** O argumento a favor era que o `k_wear_flank` do LIU_2016 é **5× menor**
(4,32e-14 contra 2,15e-13), logo acumula profundidade mais devagar e isso poderia
compensar corridas 15–25× mais longas. Foi esse lado que ganhou.

| dep | tripé | pior Δ em qualquer perna | curva do pior |
|---|---|---:|---|
| 3,5e-6 | **14/14** | **+0,0020** | `fig7_run2_5e6cyc` |
| 2,5e-6 | **14/14** | **+0,0027** | `fig7_run2_5e6cyc` |

**G1 PASSA nos dois · G2 PASSA nos dois** (barra: +0,010). A curva de **5 milhões
de ciclos** — apontada no prereg como o teste mais severo, porque a saturação age
sobre profundidade **acumulada** — é justamente a de maior Δ, e fica **3,7×**
abaixo da barra com σ praticamente intacto (+0,0003). As três curvas coladas nos
limites sobreviveram: `fig9a_m40nm` MAE 0,0477 → 0,0487 · `fig7_run1` σ 0,0225 →
0,0230 · `fig9a_m30nm` σ 0,0227 → 0,0231.

### Validação de instrumento que veio de graça

O G1 rodou **duas vezes por caminhos independentes**: um heredoc lançado antes da
compactação da sessão (e que só escreveu o resultado depois) e o script versionado
`New_Theory/saturacao_flanco_g1.py`, reescrito do zero. Os **14 pares
(mae, σ) são bit-idênticos** entre os dois. Isto importa porque o modo de falha
mais perigoso desta medição seria o override **não chegar** ao engine — Δ = 0 em
bloco se leria como "transfere". O script novo checa o instrumento antes de medir
(`flank_fret_depth` chega ao runner **e** `flank_wear_on` está ligado) e a
concordância entre os dois caminhos confirma que a checagem não é decorativa.

## A varredura LI_2022 — G3, G4, G5, e o que ela mostra que 3 pontos não mostravam

`New_Theory/saturacao_flanco_li2022.py`, 8 profundidades × 4 curvas
(`mae/σ` por curva):

| dep | `full` | `axialmin_10Hz` | `15Hz` | `20Hz` | tripé | pior Δ |
|---|---|---|---|---|:---:|---:|
| base | 0,0317/0,0365 | 0,0526/0,0242 | 0,0298/0,0206 | 0,0201/0,0248 | 2/4 | — |
| 4,0e-5 | 0,0305/0,0352 | 0,0531/0,0240 | 0,0298/0,0202 | 0,0197/0,0243 | 2/4 | +0,0004 |
| 1,0e-5 | 0,0273/0,0315 | 0,0544/0,0235 | 0,0299/0,0193 | 0,0186/0,0229 | 2/4 | +0,0017 |
| 5,0e-6 | 0,0250/0,0274 | 0,0560/0,0231 | 0,0300/0,0182 | 0,0172/0,0211 | 2/4 | +0,0033 |
| 3,5e-6 | 0,0233/0,0244 | 0,0573/0,0228 | 0,0310/0,0175 | 0,0160/0,0196 | **3/4** | +0,0046 |
| **2,5e-6** | **0,0227/0,0214** | 0,0589/0,0226 | 0,0323/0,0166 | 0,0146/0,0179 | **3/4** | +0,0062 |
| 2,0e-6 | 0,0258/0,0194 | 0,0602/0,0226 | 0,0334/0,0161 | 0,0135/0,0165 | 3/4 | +0,0075 |
| 1,5e-6 | 0,0303/0,0174 | 0,0621/0,0227 | 0,0350/0,0155 | 0,0118/0,0144 | 3/4 | +0,0095 |
| 1,0e-6 | 0,0371/0,0166 | 0,0655/0,0234 | 0,0379/0,0150 | 0,0090/0,0111 | 3/4 | **+0,0129 ✗** |

* **G3 (ganho):** a `full` entra no tripé (σ ≤ 0,025) a partir de **3,5e-6**. ✅
* **G4 (nenhum pior > +0,010):** passa até **1,5e-6**; viola em 1,0e-6. ✅ para a
  célula adotada. E o **pior Δ recai inteiramente sobre a `axialmin_10Hz`**, curva
  que já reprovava — nenhuma curva **aprovada** é prejudicada em nenhuma célula
  viável (o pior numa aprovada é +0,0025 de MAE na 15 Hz).
* **G5 (fronteira interior):** o ótimo **não** está na borda da grade
  [1,0e-6 … 4,0e-5]. ✅

### Por que 2,5e-6, e não a célula que o critério do script elegeria

O script ordena por (tripé, menor dano) e elegeria **3,5e-6** (dano +0,0046 contra
+0,0062). Registrado, porque a escolha foi **outra** e o motivo tem de ficar
auditável.

**σ é MONÓTONO na grade inteira** (0,0352 → 0,0166) — ele não tem mínimo, logo σ
sozinho empurraria a profundidade a **zero**, matando o canal. **σ não pode
selecionar valor.** O MAE da curva-alvo, sim: tem **mínimo interior em 2,5e-6**
(0,0227, subindo para 0,0233 em 3,5e-6 e 0,0258 em 2,0e-6). É onde o kernel
saturado reproduz melhor a trajetória, e é critério de **forma**, não de placar.

Segundo motivo, prático e com precedente amargo nesta campanha: a 3,5e-6 a `full`
entraria com σ 0,0244 = **0,98× do limite — 2,4 % de margem**. Números a 1,03×
já mordoram a campanha várias vezes (a `rep2` do CACCESE está fora hoje por 3 %),
e re-carimbos movem σ em 0,001–0,003. A 2,5e-6 a margem é **14 %**.

Terceiro: a **`axialmin_20Hz` passava com σ 0,0248 = 0,99×** e vai a **0,0179 =
0,72×**. Uma célula que dá 14 % de folga à curva que entra E 28 % à curva que já
estava no fio é mais robusta que uma que economiza 0,0016 de dano numa curva já
reprovada.

## Verificação da adoção: rota CONFIG ≡ rota OVERRIDE

Os gates foram todos medidos por **override**; a adoção age por **config**. Se as
duas rotas divergissem, os gates teriam medido outra coisa — e o modo de falha
perigoso é o override **não chegar** ao engine, caso em que Δ = 0 em bloco se
leria como "transfere". Medido (`saturacao_flanco_verifica.py`, 18 curvas):

* `kb.adopted_config(...)` devolve `flank_fret_depth = 2,5e-06` nos dois grupos;
* as **14 curvas do LIU_2016** saem **`identico`** (|Δ| < 1e-12 nas três pernas)
  entre as duas rotas;
* `li2022ti_axial_10Hz_full` **ENTROU** (0,0317/0,0365 → **0,0227/0,0214**);
* **saíram: nenhuma · pior > +0,010: nenhuma · divergiu: nenhuma.**

### Isolamento por CONSTRUÇÃO, não por medição

Só **2 dos 69** grupos do `adopted_configs.json` têm `flank_wear_on` ativo
(`LI_2022_TRIBOINT` e `LIU_2016`) — exatamente os dois que recebem
`flank_fret_depth`. A saturação multiplica `d_w` **dentro** de
`flank_wear_from_slip`, que só é chamada com o companheiro ligado. As outras 192
curvas do store não podem mudar; o re-carimbo confirma isso por bit.

### ⚠️ A adoção foi interrompida no meio, e o registro fica

A 1ª execução de `saturacao_flanco_adota.py` **escreveu o config** e foi morta na
fase de verificação por timeout — de novo por `| tail`, que bufferiza e mata sem
deixar rastro do que faltava (o mesmo gotcha que o `CLAUDE.md` registra para
`pytest | tail`). Estado resultante: config aplicado, store **não** re-carimbado,
gate incompleto. Fechado sem reescrever nada: o backup `.bkp_dq` foi conferido
chave por chave (**exatamente 4 diferenças** — os dois `cfg.flank_fret_depth` e os
dois `prov`; a âncora `k_j_init` do D-P intacta ⇒ o backup é o estado pré-D-Q e o
rollback é limpo) e a verificação rodou **sem pipe**, num script versionado.
**Regra:** executor de adoção nunca via pipe — ele escreve antes de verificar, e
um pipe transforma "gate incompleto" em "sem rastro".

## G6 — escala física declarada

`2,5e-6 m = 2,5 µm` contra `emb_depth = 9,5 µm` da tabela VDI 2230 para este rig:
**mesma ordem**, a escala de rugosidade da interface, que é onde o fretting de
flanco opera. Dentro da faixa 0,5–50 µm que o prereg fixou como "tem escala
física"; não precisa ser declarado como fit sem escala.

## ⚠️ Limite declarado, e ele NÃO é azar de parametrização

A `axialmin_10Hz` **piora monotonicamente** com a saturação (MAE 0,0526 → 0,0589):
ela é **MAE-bound** e precisa de **mais** perda, enquanto a `full` é **σ-bound** e
precisa de **menos** perda tardia. Duas curvas do MESMO ensaio com demandas
opostas ⇒ **nenhuma profundidade serve às duas**, e a fonte fica em 3/4.

A medição de 2026-08-05 (`fila_form_limited_3_anatomia.md`) mostra **por quê** — e
é estrutural, não numérico: a perda total do modelo nas três frequências é
**0,1539 / 0,1537 / 0,1535** (espalhamento **0,03 %**) contra **2,0×** de variação
no dado. O modelo é praticamente **cego à frequência** nesta janela, e o erro de
nível **troca de sinal** com f. A saturação de flanco é alavanca de **forma sem
dependência de frequência**: pelo contradomínio, ela não pode cobrir um déficit de
**lei de frequência**. O que a `axialmin_10Hz` pede é a lei — candidato já medido
(re-atribuição creep→fretting, 0 % → 93 % da dependência) e recusado por custar
uma curva.

## ⚠️ NÃO combinar com a re-atribuição creep→flanco

O teto medido **em pares** (pré-teste 4 do charter) mostrou **ANTI-SINERGIA**: a
razão de frequência 20 Hz/10 Hz degrada de **0,529** (re-atribuição pura) para
**0,593 → 0,814** conforme a saturação aperta, porque o sinal de frequência está
na **magnitude** do flanco e a saturação a corta. Ver
`li2022_reatribuicao_resultado.md`.

## Re-carimbo e efeito no censo

Fingerprint **`b072b24fd3a8` → `b70276f2fa43`**, uniforme nos **210** (209 pelo
`parallel_batch --workers 6 --store`, 1427 s; o `exemplo_m12_sintetico` fica fora
do batch por construção e foi re-simulado **direto** — é ele que quebra a
uniformidade quando esquecido).

**G4-isolamento medido, e deu PERFEITO: 0 das 192 curvas fora das duas fontes
mudou** em qualquer perna. Dentro das duas, **17 das 18** mudaram; a 18ª,
`liu2016wear_fig13a_mos2`, ficou **bit-idêntica** — lubrificada com MoS₂, o canal
de fretting de flanco praticamente não carrega perda ali, então a saturação não
tem o que saturar. Coerência física, não defeito.

| | antes | depois |
|---|---|---|
| tripé (estrita) | 134/205 | **135/205** |
| fila form-limited | 3 | **2** |
| LI_2022_TRIBOINT | 2/4 | **3/4** |
| LIU_2016 | 14/14 | **14/14** |

A fila que resta é `caccese2009_tapered_45kN_rep2` (defeito de **dado**, D-S
enfileirado, provado) e `li2022ti_axialmin_10Hz` (**lei de frequência**, ver o
limite declarado acima).

⚠️ **A `axialmin_10Hz` piorou de 1,05× para 1,18× no MAE** (0,0526 → 0,0589), como
o prereg declarou antes de medir. Ela já estava fora e continua fora; o que mudou
é a distância. Isto é preço pago com número, não efeito colateral escondido.

## Registro de método

**⚠️ Slip de ordem, já declarado no prereg:** o valor 3,5e-6 foi encontrado numa
varredura **antes** do prereg — a varredura era a medição, não pré-teste. O que
preservou a disciplina foi existir um **held-out intocado** e o gate que decide
ser sobre ele: o G1 perguntou algo cujo resultado eu não conhecia, e a previsão
registrada ("50/50") está no prereg, escrita antes.
