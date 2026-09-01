# `classe_parada`: **3 das 8** não têm a assinatura da classe — e duas a têm **invertida**

**2026-08-15 (madrugada)** · só-leitura · **nada reclassificado** · store `85e8104420b0`,
censo **141/205**.

---

## 1. A premissa que faltava testar

A camada `classe_parada` ("aceleração tardia", encerrada pela regra de parada em
2026-08-02) atribui **por FONTE** — `_FONTES_CLASSE_PARADA` na triagem —, não por defeito
medido na curva. Isso já se mostrou falho **uma vez**: em 2026-08-14 a
`chu2026ti_D1p0mm_F0_49kN_test5` estava rotulada *"classe encerrada"* e **fechou com duas
constantes de assentamento**. Curva de classe genuinamente encerrada não se resolve assim.
Ela saiu por mérito.

**As 8 restantes herdaram o rótulo da fonte e nunca foram verificadas uma a uma.**

## 2. O discriminante — o da própria campanha

A classe afirma **quando** o erro acontece: o modelo desacelera enquanto o dado acelera, ou
seja o resíduo **cresce no fim**. Dois testes que a campanha já usa:

* **ρ(resíduo, N)** de Spearman — `|ρ| ≥ 0,7` ⇒ defeito de **taxa** (rampa);
* **razão terminal** — `|resíduo|` do último terço / do primeiro terço, `> 2`.

## 3. Medido

| curva | fonte | ρ | razão terminal | \|viés\|/MAE | assinatura? |
|---|---|---:|---:|---:|:--:|
| `liu2025_M16_fig2_single` | LIU_2025 | **+0,966** | **6,43** | 0,80 | ✅ |
| `yang2021_amp1p0mm_ax2kN` | YANG_2021 | **+1,000** | **17,75** | 1,00 | ✅ |
| `yang2021_amp0p5mm_ax8kN` | YANG_2021 | **+0,891** | **19,23** | 0,89 | ✅ |
| `yang2021_amp0p6mm_ax8kN_r1` | YANG_2021 | +0,633 | **35,08** | 0,89 | ✅ |
| `liu2025_M16_amp0p25` | LIU_2025 | −0,733 | 1,88 | 1,00 | ✅ (por ρ) |
| **`liu2025_M16_amp0p3`** | LIU_2025 | −0,233 | 1,51 | **1,00** | ⛔ |
| **`liu2025_M16_amp0p8`** | LIU_2025 | −0,448 | **0,47** | 0,73 | ⛔ |
| **`yang2019_M10_amp0p4_5Hz`** | YANG_2019 | +0,392 | **0,70** | 0,80 | ⛔ |

**5 com assinatura · 3 sem.**

## 4. ⚠️ Duas das três têm a assinatura **invertida**, não ausente

`amp0p8` (razão **0,47**) e `amp0p4_5Hz` (**0,70**) têm o resíduo **menor no fim** que no
início. Isso não é "aceleração tardia fraca": é o **extremo oposto** — o erro se forma
**cedo** e o modelo o recupera ao longo do ensaio.

A camada nomeia **quando** o defeito acontece. Nestas duas, acontece na outra ponta.

## 5. O que isto NÃO é

**Não é reclassificação** — a camada é decisão assinada e mexer nela exige assinatura. E
**não é** afirmação de que as três têm rota aberta: uma curva pode estar legitimamente
fechada por outro motivo. O que a medição sustenta é mais estreito e mais firme:

> o **rótulo** é uma afirmação sobre o defeito, e para 3 das 8 curvas essa afirmação **não
> é sustentada pelo próprio discriminante da campanha**.

## 6. O que a medição sugere sobre o defeito real

Duas das três (`amp0p3` e a já-conforme `amp0p25`) têm **|viés|/MAE = 1,00** — resíduo de
**sinal único**, que é a assinatura de erro de **NÍVEL puro**, não de forma. Para nível a
campanha tem alavancas (foi assim que o D-Z/D-AA moveram o JCSR). Se isso as aproxima ou não
é **medição a fazer** — e é medição que a camada, como está, desencoraja: ela diz "fechada,
aguardando dado novo".

## 6b. ✅ MEDIDO (2026-08-15, rodada seguinte): **1 das 3 TEM ROTA — e fecha**

O §6 era pista. Medi a consequência prática, porque *"o rótulo está errado"* sozinho não diz
ao professor se importa.

⚠️ **Ordem obrigatória cumprida**: classe mecânica **antes** da alavanca.

| curva | classe | `slip/δ` |
|---|---|---:|
| `liu2025_M16_amp0p3` | **STICK** | 0,0000 |
| `liu2025_M16_amp0p8` | PARCIAL | 0,6136 |
| `yang2019_M10_amp0p4_5Hz` | PARCIAL | 0,2008 |

### `liu2025_M16_amp0p3` — **fecha o tripé** com meia constante, em DUAS alavancas

| dose | MAE | res.máx | σ | veredito |
|---|---:|---:|---:|---|
| nominal | 0,0645 | 0,0865 | 0,0249 | reprova (MAE) |
| `emb_depth` **×0,5** | **0,0373** | **0,0563** | **0,0167** | ✅ **PASSA** |
| `C_creep` **×0,5** | **0,0360** | **0,0511** | **0,0183** | ✅ **PASSA** |

O nominal já estava com σ em **0,0249 contra o limite 0,0250** — 99,6 %. Quem reprova é o
**MAE**, e é exatamente o que uma alavanca de **nível** corrige. Consistente com o
`|viés|/MAE = 1,00` do §3.

✅ **Confirmação interna que vale mais que o resultado:** a curva é **STICK**, e em stick só
embedding e creep alcançam. O `tr_loose_gain` deu **bit-idêntico nas duas doses** (0,0645 em
ambas). A regra do charter — *classifique a classe mecânica antes de escolher a alavanca* —
**previu quais seriam inertes**, e a medição confirmou ao dígito.

### As outras duas: **sem rota** nas alavancas de nível

* `liu2025_M16_amp0p8` — reprova **só no σ** (0,0396 contra 0,0250); melhor dose melhora
  0,0027. Nada chega perto.
* `yang2019_M10_amp0p4_5Hz` — `emb_depth` ×0,5 melhora o MAE (0,0966 → 0,0732) mas **piora o
  res.máx** (0,1411 → 0,1661). Não fecha.

⇒ **1 de 3 tem rota; 2 não.**

## 7. Proposta (não executada — exige assinatura)

Trocar a atribuição **por fonte** por atribuição **por curva medida**: a curva entra em
`classe_parada` se exibir o discriminante (`|ρ| ≥ 0,7` **ou** razão terminal `> 2`), e as
que não exibirem voltam para a fila com o defeito que de fato têm.

Custo previsto: **3 curvas** saem da camada e voltam a `form_limited` — a fila deixa de ser
zero. ⚠️ **Isso é o preço correto de uma classificação honesta**, não um retrocesso: hoje
elas contam como "fechadas com procedência" carregando um rótulo que a medição não sustenta.

✅ **E o §6b mostra que não é só escrituração:** das 3, **uma fecha o tripé** com meia
constante. Reclassificar não apenas corrige o registro — **destrava uma curva**. O saldo é
fila 0 → 2 (as duas sem rota) e censo **141 → 142** se a rota da terceira for adotada com
procedência e gates próprios.

⚠️ E há um precedente que pesa a favor: a `test5`, também rotulada por fonte, **fechou** —
o único teste independente que a camada já sofreu, ela reprovou.

## Reprodutibilidade

`audit_classe_parada.py` no scratchpad (~10 s, só-leitura). Usa o classificador **canônico**
da triagem (`T.classificar`) para achar os membros — nunca reimplementa a regra da camada.
