# O **denominador** (205) auditado pela 1ª vez — está são

**2026-08-15 (18:xx)** · só-leitura · **nada mudado** · store `20be19aabe11`, censo
**143/205**, fora **62**, fila form-limited **0**.

---

## 1. Por que este alvo

Toda auditoria desta campanha olhou o **numerador** (as 143 que passam) ou as **camadas** (as
62 que falham). O **denominador** — quem decide o *"de 205"* — nunca foi examinado.

Ele importa mais que qualquer camada: se `caso_comparavel` excluir algo que não devia, **todo
número publicado desloca**, inclusive os que estão sob guarda.

## 2. A contagem, ponta a ponta

| | casos |
|---|---:|
| registry | **210** |
| com entrada no store | **210** (nenhum faltando) |
| com `ok = True` | **210** |
| **e comparáveis** | **205** ← o denominador publicado |
| **excluídos** | **5** |

## 3. Os 5 excluídos, um a um

| caso | fonte | motivo | verificável? |
|---|---|---|---|
| `ancora_interna` | `ANCORA_INTERNA` | fonte fora do projeto (decisão do professor, 2026-08-01) | decisão |
| `ancora_interna` | `ANCORA_INTERNA` | idem | decisão |
| `ancora_interna` | `ANCORA_INTERNA` | idem | decisão |
| `exemplo_m12_sintetico` | `USER` | caso sintético, não é dado experimental | escopo |
| `lu2024_M8_fig18_amp1p0` | `LU_2024` | **duplicata** de `fig20_T22Nm` — mesmo teste em 2 figuras | ✅ **medível** |

Quatro são **decisão ou escopo** (a fonte saiu do projeto; o caso é sintético). Só **uma**
carrega afirmação **factual** sobre o dado — e é a única que, se falsa, mudaria o denominador
para **206**.

## 4. A afirmação factual, testada

Comparando as duas curvas cruas na janela comum (200 pontos interpolados, normalizadas pelo
próprio 1º ponto — a convenção do runner):

| | valor |
|---|---|
| drive | **idêntico**: amp 1,0 mm nas duas |
| janela | `N` = 0 a 99 nas duas |
| final | 0,0648 × 0,0634 |
| **`|diff|` médio** | **0,00341** |
| `|diff|` máximo | 0,02118 |

⇒ **a duplicata confere.** As duas séries concordam bem abaixo de qualquer piso de
digitalização da fonte. **O denominador 205 é são.**

## 5. Uma nota de calibração, não de defeito

O `CLAUDE.md` documenta para **este mesmo par** um piso de digitalização de **MAE 0,0127**
(medido em 2026-07-31); eu meço **0,00341** na janela comum interpolada — fator 3,7.

⚠️ **O número não é carga.** O próprio texto que o registra conclui *"< global ⇒ limite fica
0,025"*, e o helper hoje confirma: `piso_da_fonte(LU_2024)` = **0,00695** (σ) e
`limite_sres(LU_2024)` = **0,0250**. Seja 0,0127 ou 0,0034, o limite da fonte é o global. Não
há decisão pendurada nessa diferença — ela é de método de janela, não de veredito.

## 6. O que este resultado NÃO é

Não é descoberta: é **confirmação**. O valor está em que o denominador nunca tinha sido
verificado, e agora foi — inclusive a única de suas 5 exclusões que faz afirmação sobre o
dado.

⇒ **resultado negativo, gravado de propósito.** Auditoria que só se publica quando acha erro
enviesa o registro: a próxima pessoa não consegue distinguir "já olhamos e está certo" de
"ninguém olhou".

## 7. ⚠️ Erro meu, pego pelo confronto de duas sondas

Uma sonda minha reportou *"piso do LU_2024 pelo helper: None"* enquanto outra dava **0,00695**.
Não era contradição do dado — era bug do meu laço de busca. `piso_da_fonte` lê a **mediana das
famílias** (`pisos["fam"]`), e `LU_2024` **está** em `por_fonte` com
`(MAE 0,00781 · res.máx 0,02807 · σ 0,00695)`.

Regra que isto reforça: **duas sondas discordando é sempre bug de sonda até prova em
contrário** — hoje eu já tinha errado três vezes por reimplementar seleção, e o reflexo certo
foi perguntar ao helper, não escolher entre os dois números.

## Reprodutibilidade

Sondas inline no corpo do commit. Usam `rh.caso_comparavel`, `rh._SRC_NAO_COMPARAVEL`,
`rh._CID_NAO_COMPARAVEL`, `rh._pisos_medidos`, `rh.limite_sres`, `T.piso_da_fonte` e
`load_full_curve` — nenhuma reimplementa regra.
