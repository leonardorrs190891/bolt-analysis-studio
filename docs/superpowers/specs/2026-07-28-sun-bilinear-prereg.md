# Pré-registro — Su–N BILINEAR do Liu 2025: o joelho e o ramo de alto ciclo transferem entre tamanhos?

**Data:** 2026-07-28 · **Autorização:** professor, *"pré-registre a Su-N bilinear e rode"*
**Antecessor:** gate **L4** (`223187d`), que **falhou 0/5** por testar uma lei de potência
**única** contra dados que o próprio artigo declara **bilineares** — 5º defeito de autoria
de gate. Correção: **testar o modelo que a fonte declara.**
**Status:** PROPOSTO — gates IMUTÁVEIS depois de assinados

---

## 0. Declaração de perda de cegueira — leia antes dos gates

Ao diagnosticar a falha do L4 eu **já olhei** os dados M10. Sei, portanto:

| já medido, NÃO é mais cego | valor |
|---|---|
| inclinação de lei única, M16 | `m` = 5,94 (`R²` = 0,8484) |
| inclinação de lei única, M10 | `m` = 8,07 (`R²` = 0,9623) |
| razão `N_M10/N_M16` a σ = 398 MPa | **1,02** |
| idem a σ = 518 MPa | 1,84 |
| idem a σ = 783 MPa | **4,51** |

⇒ **Eu já sei que o ramo de baixo ciclo não transfere** (4,51×) e que **em σ ≈ 400 MPa há
concordância quase perfeita**. Um gate de "±25 % em todos os 5 pontos M10" seria teatro:
eu conheço a resposta.

**O que eu NÃO sei, e é o que estes gates medem:**

1. Onde cai o **joelho** de cada tamanho, e se ele **transfere** (S2).
2. Se o **ramo de alto ciclo transfere como ramo** — um ponto concordar a 2 % não diz que
   a reta inteira concorda (S3).
3. Se a **assimetria** que eu suspeito (alto ciclo transfere, baixo não) é a estrutura real
   ou só o efeito de dois pontos (S4).

Os gates são escritos sobre **essas três** perguntas, não sobre o que já vi.

---

## 1. Modelo sob teste — o que o artigo declara

O artigo descreve a Su–N como *"obvious high- and low-cycle boundaries and **bilinear**
characteristics"*. Nosso `sun_life()` **já implementa exatamente isso**:

```
N = C1 · σ^(−m1)      para σ >= σ_knee      (baixo ciclo / tensão alta)
N = C2 · σ^(−m2)      para σ <  σ_knee      (alto ciclo / tensão baixa)
N = ∞                 para σ <= σ_endurance
```

**Ajuste:** mínimos quadrados em log–log, com `σ_knee` varrido numa grade e **continuidade
imposta** no joelho (`C2 = C1·σ_knee^(m2−m1)`) ⇒ **4 parâmetros livres**
(`m1, m2, σ_knee, C1`) para **6 pontos** M16. Thin, e declarado como tal: por isso o teste
que vale é a **transferência a M10 com ZERO re-ajuste**.

**Dados (os mesmos do L4, sem alteração):**
- σ: Table 2 do artigo (interpolação linear; extrapolação pela reta ajustada fora da faixa,
  marcada no relatório).
- N: `New_Theory/liu2025_fig4_DN.json` — Fig. 4 digitalizada e **validada a 2,0 %** contra
  as nossas curvas da Fig. 3. **N é vida até `F/F₀ = 0,95`**, não até fratura.

---

## 2. GATES — com a conta de satisfazibilidade cobrindo o pior caso do escopo

**S0 — nada de canônico é tocado.** *Critério:* a execução é **pós-processamento puro** sobre
o JSON digitalizado + Table 2; a lista de arquivos escritos pelo script não contém `src/`
nem o store. *Conta:* por construção. *(Nota: NÃO uso `git status` como no C0 da 3ª
tentativa de métrica — aquilo media o **ambiente** numa árvore compartilhada, não a
mudança. Regra da §4.48.)*

**S1 — o bilinear é um ajuste legítimo em M16, não um artefato de parâmetros.**
*Critério:* `R²(log) ≥ 0,97` **E** o joelho cai **estritamente dentro** da faixa de σ dos
dados (não num extremo).
*Conta / pior caso do escopo:* a segunda cláusula é o que impede o gate de ser vazio — um
bilinear com joelho num extremo **é** uma reta única disfarçada, e aí o `R²` alto não
significaria nada. Com 4 parâmetros e 6 pontos o `R²` alto é fácil; a cláusula do joelho é
que carrega o gate. Satisfazível: a lei única dá 0,8484 e a curva é visivelmente encurvada.

**S2 — o JOELHO transfere (cego).** *Critério:* ajustando o bilinear **independentemente**
em M10, os dois `σ_knee` concordam dentro de **±20 %**.
*Conta:* **NÃO RODADA — é gate cego.** Sem cláusula condicional no escopo ⇒ sem
inconsistência interna possível.

**S3 — o ramo de ALTO CICLO transfere como RAMO (cego).** *Critério:* usando `(C2, m2)`
ajustados **só em M16**, **zero re-ajuste**, todo ponto M10 com `σ < σ_knee(M16)` cai
dentro de **±30 %**. *Cláusula de validade:* se **nenhum** ponto M10 cair nessa faixa, o
gate é **VOID** e é reportado como tal — não como aprovado.
*Conta:* **NÃO RODADA.** A cláusula de validade existe porque eu **não sei** quantos pontos
M10 ficarão abaixo do joelho do M16; sem ela, o gate poderia "passar" com zero pontos —
que é a armadilha do B6/C0 numa forma nova.

**S4 — a ASSIMETRIA é a estrutura, e não dois pontos.** *Hipótese declarada:* os pontos M10
com `σ ≥ σ_knee(M16)` caem **FORA** de ±30 % sob `(C1, m1)` do M16, e a razão
`N_M10/N_M16` **cresce monotonicamente** com σ.
*Critério:* a hipótese se confirma. **Se falhar** — isto é, se o ramo de baixo ciclo
**também** transferir — é **boa notícia** e deve ser reportada como achado positivo, não
como falha do estudo.
*Conta:* declarada como predição justamente porque §0 admite que eu já vi dois desses
pontos; escrevê-la torna o resultado falseável **nos dois sentidos**.

**S5 — o `sun_life()` do engine reproduz o ajuste.** *Critério:* alimentado com as
constantes ajustadas, `sun_life()` devolve o mesmo `N` dentro de **1e-9 relativo** nos 11
pontos (6 M16 + 5 M10).
*Conta / conversão de unidades explícita:* o engine usa **Pa**, o ajuste usa **MPa**, logo
`C_Pa = C_MPa · 1e6^m`. Com essa conversão a igualdade é **exata por construção** (mesma
fórmula), não assintótica — diferente do `M0` insatisfazível da 1ª tentativa de métrica.
`fat_sigma_endurance` fica **abaixo** do menor σ do conjunto para não truncar.

**S6 — nada é adotado nesta execução.** Nenhuma constante entra em
`adopted_configs.json` nem no bloco `shared`. Adoção seria decisão separada.

### 2.1 Interpretação pré-declarada

| resultado | leitura |
|---|---|
| **S1 ✓ · S2 ✓ · S3 ✓** | **o alto ciclo transfere entre tamanhos** — seria a 1ª constante cross-rig da campanha, escopada ao ramo de alto ciclo. Propor adoção em prereg separado |
| **S1 ✓ · S2 ✓ · S3 ✗** | o joelho transfere mas o ramo não ⇒ a normalização do artigo é **qualitativa**; registrar e encerrar |
| **S1 ✓ · S2 ✗** | nem o joelho transfere ⇒ a Su–N é **per-rig**, como todas as nossas constantes (§8). Encerrar a linha do Liu 2025 |
| **S1 ✗** | o bilinear não descreve nem o M16 ⇒ o modelo declarado pelo artigo **não se sustenta no dado publicado dele**. Achado forte, registrar |
| **S3 VOID** | reportar como void; o gate não opinou |
| **S4 ✗** | **boa notícia** — a discordância de baixo ciclo não é estrutural; investigar em prereg novo |
| **S5 ✗** | bug de conversão; consertar e re-rodar sem reinterpretar gate |

---

## 3. O que NÃO está sendo proposto

- **Não** adotar constante alguma (S6).
- **Não** re-ajustar nada em M10 — a transferência é **zero-refit** por definição.
- **Não** usar as vidas de **fratura**: o par correto é Table 2 × Fig. 4 (`N₉₅`), e foi
  confundi-los que invalidou a §4.1 do estudo de modelagem.
- **Não** mexer em `src/`, no store, na física ou no fingerprint.
- **Não** haverá reescrita do L4 — ele morreu como escrito e fica morto.

---

## 4. Reprodutibilidade

```bash
py -3.12 New_Theory/sun_bilinear_gates.py      # S0-S6, sem varredura, ~5 s
```
