# Premeasure da re-digitalização do LU — a correção NÃO pode ser feita em pedaços, e o modelo absorveu o erro

**2026-08-07 (madrugada)** · `lu2024_redigit_premeasure.py` (só-leitura) ·
store `1c118e405a42` · **nenhum prereg escrito, nada adotado**.

## A construção está certa — conferido antes de ler qualquer conclusão

CSVs corrigidas = **mesmos ciclos** da CSV atual, y interpolado da série
extraída da figura, **1º ponto vindo da tabela impressa** (o c1 de pixel tem
resíduo declarado que os controles não explicam). Conferência de sanidade:

| curva | c10 novo / tabela | c50 novo / tabela |
|---|---|---|
| `fig18_amp0p5` | 0,467 / 0,465 | 0,344 / 0,344 |
| `fig18_amp1p0` | 0,433 / 0,429 | 0,123 / 0,121 |
| `fig18_amp2p0` | 0,176 / 0,173 | — |
| `fig20_T10Nm` | 0,448 / 0,448 | 0,350 / 0,352 |
| `fig20_T16Nm` | 0,472 / 0,472 | 0,243 / 0,242 |
| `fig20_T22Nm` | 0,425 / 0,429 | 0,121 / 0,121 |
| `fig20_T28Nm` | 0,465 / 0,465 | 0,319 / 0,317 |

Todas a **±0,004**. Logo os `|dy|` grandes (até 0,57) são correção real em
pontos intermediários, não defeito da construção.

## ✅ O par de digitalização melhora 2,7× — o viés compartilhado sai

```
familia  delta=1 F=4627   MAE 0,0127 -> 0,0078   mx 0,0718 -> 0,0281
                          sigma 0,0192 -> 0,0070
```

As duas metades do par, puxadas cada uma para a mesma verdade impressa,
passam a concordar **melhor**. É a confirmação direta do achado do viés
compartilhado.

## ⚠️ MAS o modelo PIORA em 5 de 7 — e isso é diagnóstico, não acidente

| curva | antes | depois |
|---|---|---|
| `fig18_amp2p0` | 0,0463 / 0,0722 / 0,0226 | **0,0110 / 0,0299 / 0,0124** |
| `fig20_T22Nm` | 0,0923 / 0,2138 / 0,0512 | 0,0520 / **0,2554** / 0,0600 |
| `fig18_amp1p0` | 0,0659 / 0,1069 / 0,0356 | 0,0595 / **0,2543** / 0,0610 |
| `fig18_amp0p5` | 0,1245 / 0,1682 / 0,0434 | 0,1284 / 0,1796 / **0,0795** |
| `fig20_T16Nm` | 0,1672 / 0,2541 / 0,0654 | 0,1750 / **0,4417** / 0,0881 |
| `fig20_T28Nm` | 0,0984 / 0,1872 / 0,0723 | 0,1097 / **0,2704** / 0,0930 |
| `fig20_T10Nm` | 0,2592 / 0,3310 / 0,0767 | 0,2881 / **0,8024** / 0,1553 |

**Saldo no censo: +0.**

O modelo fica **pior** quando o dado fica **mais certo**. Isso é a assinatura de
uma calibração que **absorveu o erro de digitalização** — exatamente o padrão
que o `CLAUDE.md` já registra para o erro de *drive* das fig20 em 2026-07-31
(*"as fig20 re-simuladas com o drive real PIORAM; a calibração antiga absorvia
o input errado"*). Aqui é o mesmo, no eixo y.

⇒ **a re-digitalização do LU é inseparável de um re-fit**, como a `run2p2` foi
no D-Y. Corrigir o dado sozinho entrega dado certo com modelo pior e censo
igual — o pior dos três mundos para publicar e o melhor para a verdade.

## ⛔ ERRATA (2026-08-07, mesma noite): a subida do piso é REAL, não artefato

A seção seguinte **estava errada** e fica preservada abaixo como registro. Ela
afirmava que o `limite_sres(LU)` 0,1030 → 0,1361 era *"artefato de correção
pela metade"* — e essa leitura **pressupunha que a `fig14` estivesse errada**.

Medido em `lu2024_fig14_confere.py` (CSV commitada contra a própria figura,
única aferição possível: a `fig14` é corrida de repetição e **não tem tabela**):

| curva | pico figura | F₀ registry | razão | **RMS(CSV × figura)** |
|---|---:|---:|---:|---:|
| `fig14_amp0p5_long` | 12 504 | 12 498 | **1,000** | **0,0053** |
| `fig14_amp1p0_long` | 13 203 | 13 198 | **1,000** | **0,0043** |

**As digitalizações da `fig14` estão corretas.** Logo o piso antigo (σ 0,1827)
media *`fig18` enviesada contra `fig14` correta* — próximo **por acaso**. Com a
`fig18` corrigida, a dispersão **real** entre réplicas independentes é
**σ 0,3044**, e o piso da fonte sobe legitimamente.

⇒ **`limite_sres(LU)` 0,1030 → 0,1361 é medição, não defeito.** A consequência
— afrouxar as 5 provas F7 do LU em 32 % — é real e tem de ir ao professor
**antes** de qualquer execução, não depois.

⚠️ E o pré-requisito (1) da lista abaixo **cai**: não é preciso extrair a
Fig. 14 para descontaminar o piso; ela já está boa. Ficam o (2) re-fit e o (3)
as duas pretas.

⚠️ **3ª ocorrência da armadilha da LEGENDA** nesta campanha (KARLSEN, Fig. 18,
agora Fig. 14): os *swatches* são traços horizontais da mesma cor das séries. O
`argmax` da vermelha caiu no swatch — "pico" em t=821,5 s com valor **constante
por 111 s**, assinatura inconfundível (curva de relaxação não fica plana no
máximo), dando RMS **0,4638**. A azul escapou **por acaso**, porque o pico real
dela é mais alto que o swatch: o mesmo defeito reprovou uma série e passou na
outra. Excluída por retângulo.

### (registro) O que esta seção dizia antes da errata

## ⚠️ DEFEITO do meu próprio premeasure: correção parcial contamina o piso

`limite_sres(LU)` saiu **0,1030 → 0,1361 (+32 %)**, e eu havia previsto essa
subida. **Mas o número está contaminado e não deve ser citado.**

Os três pares declarados do LU são `fig14_*_long × fig18/fig20`. Eu corrigi as
fig18/fig20 e **não** as fig14 — não tenho extração delas. Então esses pares
passaram a comparar uma curva **corrigida** contra uma **não corrigida**, e é
por isso que os σ deles explodem (1,0 mm: 0,1827 → **0,3044**; 0,5 mm: 0,1536 →
0,1768). Não é medição de dispersão; é artefato de correção pela metade.

O único piso **limpo** nesta execução é o do par de digitalização (as duas
metades corrigidas), e ele **melhora**.

## Consequência: o prereg NÃO pode ser escrito ainda

Três pré-requisitos, agora com número:

1. **Extrair também a Fig. 14** (as três `_long`), senão os pares declarados
   ficam meio-corrigidos e o piso da fonte vira ficção. Sem isso não há como
   medir honestamente o efeito no `limite_sres`.
2. **Re-fit no mesmo passo.** A piora em 5 de 7 mostra que os parâmetros
   adotados do LU carregam o erro do dado. O passo é dado+ajuste, como o D-Y.
3. **Resolver `fig18_amp0p25` e `fig20_T4Nm`** (as duas pretas), ou declarar
   explicitamente que ficam fora da correção — hoje elas seriam as únicas duas
   da família com dado antigo.

## O que já pode ser afirmado sem prereg

* As duas figuras do LU reproduzem as tabelas (±0,002 e ±0,007).
* As CSVs de 1,0 mm e 22 N·m erram **juntas** contra o impresso, e o "piso de
  digitalização" de 0,0127 media essa concordância, não acurácia.
* A `fig18_amp2p0` é a que mais ganha com a correção (0,0463 → **0,0110**), e é
  também a de maior erro de CSV (+0,0792). Coerente.

## Reprodutibilidade

```bash
py -3.12 New_Theory/lu2024_redigit_premeasure.py --json New_Theory/lu2024_redigit_premeasure.json
```

---

## ADENDO (sessão B, 2026-08-13 20:2x) — o pré-requisito 1 JÁ ESTAVA satisfeito; o pacote pode ser escrito

Releitura com a procedência na mão: **a extração da Fig. 14 existe desde o P4
(2026-07-31, `digitize_lu2024_fig14.py`)** e é da mesma classe de instrumento
exigida aqui — auto-calibração de moldura+ticks (a 1ª versão de olho errou
145 px e foi pega), classificação por cor a 600 dpi, e **round-trip contra as
âncoras da prosa com `assert` que DERRUBA o script** (fim 0,25 mm = 10 539 N
±450; pico 1,0 mm na banda 12,3–14,0 kN; piso 0,5 mm < 250 N). "Não tenho
extração delas" era falta de *JSON no formato desta passada*, não de extração
validada.

**Consequência que muda a leitura dos pares:** os σ "explodidos"
(0,5 mm 0,1768 · 1,0 mm 0,3044) não são artefato de meia-correção — são o
scatter REAL de espécime nas condições de colapso, coerente com os pisos
colossais que o próprio P4 mediu (MAE 0,096/0,283/0,634 por amplitude). Sob
esses pisos, as duas únicas form-limited restantes do projeto ficam DENTRO da
banda de réplica nas 3 pernas (`amp0p5_long` σ 0,1235 < 0,1768; `amp1p0_long`
σ 0,2894 < 0,3044; MAEs em FORTE/PROVA da régua F7).

**O pacote (próxima iteração, prereg único, molde D-Y dado+ajuste):**
1. adotar as CSVs corrigidas fig18/fig20 (extrações `lu2024_fig{18,20}_extrai.py`,
   round-trip Tabelas 8/9 já medido);
2. resolver as 2 pretas (`fig18_amp0p25`, `fig20_T4Nm`) ou declará-las fora com
   motivo;
3. re-fit LU no MESMO passo (as constantes adotadas absorveram a deriva antiga
   — 5 de 7 pioram sem re-fit, medido acima);
4. re-medir pisos/`limite_sres(LU)` e re-julgar as 5 provas F7 vigentes +
   propor F7 das 2 `_long`;
5. gates: round-trip por curva ≤ piso de digitalização; censo global só cresce;
   nenhuma curva fora do LU muda (isolamento per-fonte); re-stamp uniforme.
