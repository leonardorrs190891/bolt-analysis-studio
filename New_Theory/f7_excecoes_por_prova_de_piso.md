# F7 — Exceções por PROVA DE PISO (tripé 0,10 / 0,05 / 0,025)

**Data:** 2026-07-29 · **Store:** `3546e6745448` · **Status:** ✅ **ASSINADA
(2026-07-29)** — §A + §B aprovadas pelo professor, com a recusa parcial §B″ que
o próprio documento recomendava.

> ## ⚠️ ERRATA DE ARITMÉTICA descoberta ao aplicar a assinatura
>
> O §4 dizia "104 + 38 = 142". **Errado por baixo, e por um motivo que só
> aparece ao cruzar as duas listas: 9 das 38 JÁ eram exceção assinada no S4**
> (`bauer2024_M8_fig6_rep1/rep5/rep6`, `bauer2024_M12_fig8_test2/test3`,
> `jcsr2023_plain_outdoor`, `jcsr2023_stainless_seawater`,
> `eccles2010_fig8b`, `eccles2010_fig7d`). Somar as listas contaria essas 9 duas
> vezes; mas as 16 do S4 também trazem **7 que o F7 não tem**, e essas somam.
>
> | | curvas |
> |---|--:|
> | F5/S4 assinadas em 2026-07-28 | 16 |
> | F7 §A+§B assinadas hoje | 38 |
> | sobreposição (uma vez só) | −9 |
> | §B″ recusada (marginal 4 %) | −1 |
> | **união distinta** | **44** |
> | no tripé | 104 |
> | **resolvidos** | **148 de 202 (73 %)** |
>
> **Como o código impede o erro de se repetir:** as duas listas viram um
> `dict` de leitura única (`_EXCECOES = {**_F5_EXCECOES, **_F7_EXCECOES}`), e as
> 9 sobrepostas ficam **só** na F5. Chave de dict não conta duas vezes — a
> estrutura carrega o invariante, não a disciplina de quem edita.
>
> **§B′ virou sem efeito:** `eccles2010_fig7d` já era exceção pela F5, então não
> há o que excluir — ela conta uma vez, pelo motivo do S4 (artefato de
> `FLOOR_TRIM`), que é razão independente e mais forte que a de piso.
> **§B″ aplicada:** `caccese2009_retighten_19p1mm` (σ 0,0263 contra piso 0,0270,
> margem de 4 %) fica **fora**. Uma palavra sua a traz de volta e a meta vai a
> 149.

**Pedido:** *"monte essa lista de exceções por prova de piso"*.
**Base de medição:** `New_Theory/piso_repetibilidade_medido.md` (piso v2, §3
abaixo) · reprodução no §8.

---

## 1. A tese, e o limite dela

Uma curva não pode ser reprovada por **não superar a repetibilidade do próprio
experimento**. Se duas réplicas do mesmo ensaio discordam entre si por mais do
que o limite, então o limite é inalcançável ali — e "reprovado" deixou de medir o
modelo.

**Mas o piso da fonte estar acima do limite NÃO absolve a curva.** Se o erro do
modelo está acima do piso, a parte acima é erro de modelo de verdade. Por isso a
prova é **por curva**, comparando o valor de cada perna violada com o piso
daquela fonte — não por fonte em bloco. Foi o que separou 38 candidatas de 33
recusas.

## 2. A correção estatística que decide quem entra

O piso é `|dado_i − dado_j|` entre duas réplicas. Com `dado_i = verdade + ruído_i`
(ruído independente, desvio `s`), para ruído gaussiano:

- `E|dado_i − dado_j| = 2s/√π ≈ 1,128 s` — é o **piso** que medimos;
- `E|modelo_no_centro − dado_i| = s·√(2/π) ≈ 0,798 s` — é o erro de um modelo que
  acertou o **centro** do conjunto de réplicas.

Razão: **0,798 / 1,128 = 1/√2 ≈ 0,707**. O mesmo fator vale para o σ
(`σ(d_i − d_j) = √2·σ(modelo − d_i)`).

⇒ **A barra para "o modelo está tão bom quanto o centro do conjunto" é
`piso/√2`, não o piso.** Usar o piso puro seria generoso em **41 %**. As duas
barras estão nas tabelas e definem as duas classes:

| classe | critério (em TODAS as pernas violadas) | leitura |
|---|---|---|
| **FORTE** | valor ≤ piso/√2 | o modelo está tão bom quanto o centro das réplicas |
| **PROVA** | piso/√2 < valor ≤ piso | dentro da dispersão do dado, leitura generosa |
| SEM | valor > piso | o modelo é pior que a dispersão do dado — **não absolve** |
| S/PISO | a fonte não tem réplica em condição repetida | **não é provável hoje** |

## 3. O piso (v2) — e a errata do meu próprio método

Piso medido por **interpolação** das réplicas numa grade de 40 pontos na janela
de x **comum**, usando **todos** os pares da família. Família = mesma fonte +
mesma condição nominal do `config_used` (não o nome do arquivo).

> ⚠️ **ERRATA (mesma sessão).** A 1ª versão exigia abscissas **idênticas** para
> formar um par. Em curvas digitalizadas de figuras diferentes isso descarta
> quase todos os pares, e o que sobra **não é amostra aleatória**: é o par que
> por acaso caiu na mesma grade — o mais próximo. Medido no BAUER fig6: sobrava
> **1 par de 15**, piso de MAE **0,0218**; com os 15 pares, **0,0959**. O
> `FLOORS` legado do repo (pareado por nome) dizia **0,115** ⇒ era a **minha 1ª
> medição** que estava fora de linha, não o legado. Consequência direta: o Bauer
> saía inteiro como "SEM PROVA" e agora entra com 7 das 9 curvas.
>
> **Efeito nas medianas:** famílias 19 → **30**; fontes com piso 16 → **22**;
> mediana MAE 0,0598 → **0,0829**, res.máx 0,0795 → **0,1279**, σ 0,0241 →
> **0,0283**. O `_pisos_medidos` do report já usa a v2, então a página publica o
> número corrigido.

**Pisos por fonte usados nesta proposta** (média das famílias da fonte):

| fonte | MAE | res.máx | σ |
|---|--:|--:|--:|
| SUN_2025_CRIMP | 0,2104 | 0,2746 | 0,0663 |
| KARLSEN_2022 | 0,2348 | 0,5402 | 0,1742 |
| JCSR_2023 | 0,3356 | 0,5869 | 0,2214 |
| ROUSSEAU_2025 | 0,2061 | 0,5463 | 0,1859 |
| ICMEZ_2025 | 0,1500 | 0,2104 | 0,0574 |
| CACCESE_2009 | 0,1208 | 0,1437 | 0,0270 |
| BAUER_2024 | 0,0933 | 0,2854 | 0,0900 |
| CHU_2026 | 0,0782 | 0,1389 | 0,0507 |
| LIU_2016 | 0,1025 | 0,1121 | 0,0176 |
| ECCLES_2010 | 0,0863 | 0,2572 | 0,0828 |
| LIU_2017_AXIAL | 0,0735 | 0,0792 | 0,0120 |
| LIU_2022_RETIGHT | 0,0417 | 0,0585 | 0,0125 |
| LI_2022_TRIBOINT | 0,0413 | 0,0590 | 0,0117 |
| SUN_2025_REASSY | 0,0342 | 0,0557 | 0,0120 |
| LIU_2025 | 0,0220 | 0,0349 | 0,0149 |
| YANG_2021 | 0,0146 | 0,0732 | 0,0155 |
| ZHANG_2018 | 0,0106 | 0,0173 | 0,0056 |
| LI_2022_MARSTRUC | 0,0082 | 0,0124 | 0,0023 |
| LIU_2020_WEAR | 0,0068 | 0,0092 | 0,0018 |
| ZHANG_2019 | 0,0067 | 0,0225 | 0,0063 |
| QIN_2024 | 0,0065 | 0,0099 | 0,0019 |
| GRZEJDA_2026 | 0,0017 | 0,0030 | 0,0009 |

## 4. O número, se assinada

| | curvas |
|---|--:|
| no tripé hoje | **104** de 202 |
| fora | 98 |
| **§A FORTE** | **32** |
| **§B PROVA** | **6** |
| §C SEM prova (ficam na fila) | 33 |
| §D sem piso medido (não prováveis hoje) | 27 |
| **resolvidos (união com as 16 do S4, menos §B″)** | **104 + 44 = 148 de 202 (73 %)** — ver a errata de aritmética no topo |

## 5. §A — FORTE (32 curvas) · valor ≤ piso/√2 em todas as pernas violadas

Formato: `perna valor / piso da fonte`.

| curva | fonte | pernas violadas · valor / piso |
|---|---|---|
| `bauer2024_M12_fig8_test2` | BAUER_2024 | res.máx 0,1795/0,2854 · σ_res 0,0461/0,0900 |
| `bauer2024_M12_fig8_test3` | BAUER_2024 | res.máx 0,1198/0,2854 · σ_res 0,0251/0,0900 |
| `bauer2024_M8_fig6_rep1` | BAUER_2024 | res.máx 0,1259/0,2854 · σ_res 0,0430/0,0900 |
| `bauer2024_M8_fig6_rep2` | BAUER_2024 | σ_res 0,0344/0,0900 |
| `bauer2024_M8_fig6_rep3` | BAUER_2024 | σ_res 0,0376/0,0900 |
| `bauer2024_M8_fig6_rep5` | BAUER_2024 | res.máx 0,1116/0,2854 · σ_res 0,0586/0,0900 |
| `caccese2009_tapered_45kN_rep1` | CACCESE_2009 | MAE 0,0523/0,1208 |
| `chu2026ti_D1p0mm_F0_49kN_test6_repeat` | CHU_2026 | σ_res 0,0285/0,0507 |
| `eccles2010_fig7c_axial_2p7kN_constant` | ECCLES_2010 | σ_res 0,0258/0,0828 |
| `eccles2010_fig8a_no_axial_baseline1` | ECCLES_2010 | res.máx 0,1223/0,2572 · σ_res 0,0394/0,0828 |
| `eccles2010_fig8b_axial_0p7kN_intermittent` | ECCLES_2010 | res.máx 0,1296/0,2572 · σ_res 0,0552/0,0828 |
| `eccles2010_fig8c_no_axial_baseline2` | ECCLES_2010 | res.máx 0,1452/0,2572 · σ_res 0,0390/0,0828 |
| `demir2024_amp0p3_F14p3_lk19p8` | ICMEZ_2025 | σ_res 0,0343/0,0574 |
| `demir2024_amp0p3_F17p6_lk19p8` | ICMEZ_2025 | σ_res 0,0292/0,0574 |
| `demir2024_amp0p4_F17p6_lk13p8` | ICMEZ_2025 | σ_res 0,0357/0,0574 |
| `jcsr2023_galv_seawater` | JCSR_2023 | σ_res 0,0468/0,2214 |
| `jcsr2023_plain_outdoor` | JCSR_2023 | res.máx 0,1313/0,5869 · MAE 0,0621/0,3356 · σ_res 0,0597/0,2214 |
| `jcsr2023_plain_seawater` | JCSR_2023 | σ_res 0,0371/0,2214 |
| `jcsr2023_stainless_seawater` | JCSR_2023 | res.máx 0,1237/0,5869 · MAE 0,0619/0,3356 · σ_res 0,0739/0,2214 |
| `karlsen2022_M30_HV_run1p2` | KARLSEN_2022 | MAE 0,0603/0,2348 · σ_res 0,0306/0,1742 |
| `karlsen2022_M30_HV_run2p2` | KARLSEN_2022 | σ_res 0,0548/0,1742 |
| `karlsen2022_M30_HV_run6p2` | KARLSEN_2022 | σ_res 0,0300/0,1742 |
| `karlsen2022_M30_HV_run7p1` | KARLSEN_2022 | σ_res 0,0504/0,1742 |
| `karlsen2022_M30_HVtorqued_run14p2` | KARLSEN_2022 | res.máx 0,2363/0,5402 · MAE 0,0898/0,2348 · σ_res 0,0854/0,1742 |
| `karlsen2022_M42_HV_run21p0` | KARLSEN_2022 | σ_res 0,0337/0,1742 |
| `liu2016wear_fig9a_m45nm` | LIU_2016 | MAE 0,0504/0,1025 |
| `rousseau2025_hdpe_t10` | ROUSSEAU_2025 | res.máx 0,1529/0,5463 · MAE 0,0579/0,2061 · σ_res 0,0572/0,1859 |
| `rousseau2025_hdpe_t12` | ROUSSEAU_2025 | res.máx 0,1375/0,5463 · MAE 0,0642/0,2061 · σ_res 0,0561/0,1859 |
| `rousseau2025_hdpe_t14` | ROUSSEAU_2025 | σ_res 0,0302/0,1859 |
| `rousseau2025_steel_t10` | ROUSSEAU_2025 | res.máx 0,1881/0,5463 · MAE 0,0866/0,2061 · σ_res 0,0981/0,1859 |
| `rousseau2025_steel_t12` | ROUSSEAU_2025 | σ_res 0,0309/0,1859 |
| `sun2025efa109235_transverse_grease_crimp` | SUN_2025_CRIMP | σ_res 0,0303/0,0663 |

**Sobreposição com o que já foi decidido:** as 5 do ROUSSEAU_2025 e as 2 do
JCSR_2023 com três pernas violadas já estavam na fila como *form-limited*; a
prova de piso as reclassifica. As 4 do ECCLES_2010 fig8 são as que o prereg da
decisão G2 (MAE-only) tratava — aqui elas passam por piso, o que **dispensa** a
decisão G2 para elas. Os 6 do BAUER eram o caso-tipo do argumento de scatter da
F5, agora com número por curva em vez de "spread 0,561".

## 6. §B — PROVA (6 curvas) · dentro do piso, acima de piso/√2

| curva | fonte | pernas violadas · valor / piso |
|---|---|---|
| `bauer2024_M8_fig6_rep6` | BAUER_2024 | res.máx 0,1300/0,2854 · MAE 0,0757/0,0933 · σ_res 0,0464/0,0900 |
| `caccese2009_retighten_19p1mm_no_retighten` | CACCESE_2009 | σ_res 0,0263/0,0270 |
| `chu2026ti_D1p0mm_F0_49kN_test5` | CHU_2026 | σ_res 0,0436/0,0507 |
| `eccles2010_fig7d_axial_3p1kN_constant` | ECCLES_2010 | MAE 0,0668/0,0863 · σ_res 0,0565/0,0828 |
| `demir2024_amp0p3_F14p3_lk13p8` | ICMEZ_2025 | σ_res 0,0428/0,0574 |
| `demir2024_amp0p3_F17p6_lk13p8` | ICMEZ_2025 | σ_res 0,0436/0,0574 |

⚠️ **`caccese2009_retighten_19p1mm` é marginal por 4 %** (0,0263 contra piso
0,0270) — se você quiser um critério mais duro, ela é a primeira a cair.
⚠️ **`eccles2010_fig7d`** já havia sido tirada dos aprovados no S4 por artefato de
`FLOOR_TRIM`; a prova de piso a devolveria. **Recomendo manter a decisão do S4**
(o artefato é razão independente) e não usar esta linha.

## 7. §C — SEM PROVA (33 curvas): o piso **não** as absolve

Aqui o erro do modelo está **acima** da dispersão do próprio dado. O limite ser
difícil não desculpa a curva; elas continuam na fila de forma/constante.

| fonte | n | pior razão valor/piso |
|---|--:|---|
| CHU_2026 | 6 | σ_res até **8,0×** o piso |
| LIU_2016 | 4 | σ_res 1,1–1,3× |
| LIU_2025 | 4 | (piso da fonte é 0,0149 em σ — muito apertado) |
| YANG_2021 | 4 | MAE até **11,5×** |
| LIU_2022_RETIGHT | 3 | 1,5× |
| ZHANG_2018 | 3 | σ_res ~1,1–5× (piso 0,0056, o mais apertado do acervo) |
| BAUER_2024 | 2 | σ_res até 5,1× (rep4) e res.máx 8,6× (fig8 test1) |
| ECCLES_2010 | 2 | σ_res 2,4× |
| LI_2022_TRIBOINT | 2 | σ_res 2,5× |
| CACCESE_2009 · LIU_2020_WEAR · SUN_2025_CRIMP | 1 cada | até 11,6× |

**Leitura útil:** as fontes com piso muito **apertado** (ZHANG_2018 0,0056 ·
LIU_2020_WEAR 0,0018 · LIU_2025 0,0149) são as que reproduzem melhor — e é
justamente nelas que a prova de piso não ajuda. Elas são o teste mais honesto do
modelo que temos.

## 8. §D — SEM PISO MEDIDO (27 curvas): não prováveis **hoje**

Não é "sem prova": é **medição ausente**. Em quase todas essas fontes cada curva
está numa condição nominal distinta, então **não existe par de réplica** no nosso
conjunto digitalizado — o piso é *inmensurável*, não apenas não medido.

| fonte | fora | condições distintas / curvas | o que destravaria |
|---|--:|---|---|
| LU_2024 | 10 | 10 / 10 | tem `FLOORS` legado de **MAE** 0,093 (fig20), mas ver §9 |
| YANG_2023_IJPEM | 7 | 9 / 9 | nenhuma réplica publicada; a nota registra que o PDF é paywall |
| LIU_2025 | 4 | 6 / 7 | 1 par existe (`amp0p8`+`fig2`), já usado — as 4 caem em §C |
| UFU_LAB | 3 | 3 / 3 | **é a sua bancada**: 2 corridas na mesma condição fecham isto |
| ZHANG_2006 | 1 | 2 / 2 | — |
| YANG_2023_AME | 1 | 1 / 1 | — |
| demais | 1 cada | — | — |

**Ação de menor custo, e é sua:** as 3 do `UFU_LAB` são as únicas cujo piso está
ao seu alcance direto — **duas corridas na mesma condição** dão o piso e movem
essas 3 curvas de "não provável" para uma das classes.

## 9. Resultado NULO que fecha um atalho tentador

O `FLOORS` legado do repo (BAUER fig6 0,115 · fig8 0,093 · KARLSEN 0,115 ·
LU_2024 fig20 0,093 · YANG_2019 0,081) é um piso **de MAE apenas**. Testei se ele
absolveria alguma das 27 sem piso: **zero**. Motivo: toda curva sem piso que
viola o MAE **também viola o σ_res**, e usar um piso de MAE para desculpar uma
violação de σ seria fabricar medição. O legado continua valendo como número
conservador de MAE, mas **não** estende esta lista.

## 10. Limites do método (o que esta lista NÃO prova)

1. **O piso é da FONTE, não da curva.** Uma fonte com uma família dispersa e
   outra apertada recebe a média. Onde isso importa (SUN_2025_CRIMP: famílias
   0,4485 e 0,0450 de MAE) a média é generosa — marcar como caveat, não usar como
   prova forte.
2. **A chave de família é `(fonte, δ, F_amp, modo)` e ignora a DURAÇÃO.** Curvas
   de mesma amplitude e pré-carga mas número de ciclos diferente entram na mesma
   família; o que impede a fabricação de piso é a exigência de janela de x comum.
   No ZHANG_2018 isso rendeu piso de 7 curvas que são ensaios de duração
   diferente — **o piso 0,0056 dessa fonte é suspeito de ser baixo por isso**.
3. **Interpolação do dado** (40 pontos na janela comum) suaviza: em curva com
   joelho agudo o piso sai levemente menor que o real ⇒ conservador para a
   proposta (dificulta a absolvição), o que é o lado certo de errar.
4. **Ruído gaussiano** na dedução do fator 1/√2. Com cauda pesada o fator é maior
   (mais generoso) — de novo, conservador como está.
5. **O tripé assinado é de 2026-07-29.** Se o limite do σ_res mudar (ver §11), as
   classes mudam e esta lista tem de ser recalculada — o script é determinista.

## 11. ✅ DECIDIDO (2026-07-29): **manter 0,025**

> **Decisão do professor, 2026-07-29: *"vamos manter"*.** O `σ_res ≤ 0,025`
> permanece, e passa a ser lido como **ambição declarada** — o mesmo estatuto do
> MAE 0,05 (que é a margem normativa e também fica abaixo do piso). A ancoragem
> exata na mediana deixa de ser a justificativa; a justificativa é a margem de
> engenharia, com o piso ao lado para o leitor ver a distância. A página já
> imprime as duas coisas juntas, então nada a refazer. **A lista deste documento
> vale para 0,025** e não precisa ser recalculada.

O limite `σ_res ≤ 0,025` foi escolhido por você **na mediana do piso medido pela
v1 (0,0241)**. Com a v2 a mediana é **0,0283**. Ou seja: o limite deixou de ser
"na mediana" e passou a ficar **12 % abaixo** dela. As três leituras que estavam
na mesa, para registro:

1. **Manter 0,025** — vira uma escolha de ambição declarada (como o MAE 0,05 já
   é), não mais uma âncora exata. Nada a refazer.
2. **Mover para a mediana corrigida** — impacto medido agora, no universo de 202
   do report (com res.máx 0,10 e MAE 0,05 fixos): `σ ≤ 0,0283` (a mediana exata)
   dá **111/202**; `σ ≤ 0,028` dá **109**; `σ ≤ 0,030` dá **115**. Contra
   **104** com 0,025. Esta lista de exceções encolhe na mesma medida — as curvas
   que entram no tripé saem dela.
3. **Manter 0,025 e registrar a errata** — é o estado atual do código e da
   página, que já publica a nota de método e o piso corrigido lado a lado.

## 12. Reprodutibilidade

```bash
# piso v2 + classes (o script desta lista)
py -3.12 New_Theory/piso_repetibilidade.py --excecoes
# a página recomputa o piso a cada geração:
python -m bolt_analysis_studio.validation.report
```

Enquanto o script não estiver versionado, ele vive no scratchpad da sessão de
2026-07-29 e estas tabelas são o registro. O piso que a **página** mostra é
recomputado do store na geração, então divergência entre a página e este
documento é sinal de que o store mudou — e o documento é que está velho.

---

## 13. Assinatura

| § | o que se assina | curvas | decisão |
|---|---|--:|---|
| A | FORTE — valor ≤ piso/√2 | 32 | ☑ **aprovado** (2026-07-29) |
| B | PROVA — valor ≤ piso | 6 | ☑ **aprovado** (2026-07-29) |
| B′ | `eccles2010_fig7d` | — | **sem efeito**: já era exceção pela F5, conta uma vez |
| B″ | excluir `caccese2009_retighten_19p1mm` (marginal 4 %) | −1 | ☑ **aplicada** |
| 11 | limite do σ_res | — | ☑ **MANTER 0,025** (decidido 2026-07-29) |

**APLICADO em 2026-07-29** (commit da assinatura): `_F7_EXCECOES` com 28
entradas (38 − 9 já na F5 − 1 recusada em §B″) + `_EXCECOES` como união de
leitura. A meta passa a ser lida como **104 no tripé + 44 exceções assinadas =
148 de 202 resolvidos (73 %)**; as 33 do §C e as 27 do §D seguem na fila.
