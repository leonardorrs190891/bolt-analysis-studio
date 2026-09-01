# Liu 2025 — execução do pré-registro v2 + re-digitalização da Fig. 2

**Data:** 2026-07-28 · **Gates:** `specs/2026-07-28-liu2025-fracture-ramp-prereg-v2.md`,
**congelados no commit `5ce4324` ANTES desta medição**
**Fingerprint:** `4f5bedfbace4` (G0 reproduziu o store **bit-a-bit**, delta 0,00e+00 nas 3)
**Engine canônico:** não tocado (forma por `loss_mechanisms=[...]`); nada adotado.

---

## 0. Veredicto

| gate | resultado | |
|---|---|---|
| **G0** inércia | **PASSA — bit-a-bit** (0,00e+00 nas 3 do núcleo) | ✓ |
| **G1** forma em vida | **12/15** — falha parcial | ✗ |
| **G1b** platô não regride | **PASSA** (Δ = 0,0000 exato) | ✓ |
| **G2** não-fratura não regride | **PASSA** (Δ = 0,0000 exato) | ✓ |
| **G3** discriminância vs cliff | **FALHA** por depender do G1 — *mas o conteúdo é favorável* (↓ §3) | ✗ |
| **G4** arresto × fratura | **atravessa** — todas vão a 0,000 com `floor`=0,25 | registrado |

**Ramo pré-declarado que se aplica** (§4.1 do v2): *"G1 ✗ com ≥ 12/15 ⇒ falha
**parcial**: reportar quais níveis/curvas e propor escopo reduzido **declarado**.
Não é adoção."* É o que este documento faz. **Nada foi adotado.**

**A frase de uma linha:** com **um único par** (`D_on`=0,75, `q`=8), `amp0p4` e
`amp0p5` acertam **10 de 10** cruzamentos; as 3 falhas estão **todas** na
`amp0p6` e **todas** nos níveis altos — e o diagnóstico (§4) é que os níveis
altos estão sendo pontuados **no eixo errado**, não que a forma erre lá.

---

## 1. G1 — a grade completa (25 células × 15 cruzamentos)

Melhor célula **`D_on`=0,75 · `q`=8 → 12/15**. Erro de cruzamento, em ciclos:

| caso | r*=0,80 | 0,70 | 0,60 | 0,50 | 0,40 | tolerância |
|---|--:|--:|--:|--:|--:|--:|
| **amp0p4** | +1554 ok | +125 ok | +477 ok | +489 ok | +505 ok | 2550 |
| **amp0p5** | +801 ok | +138 ok | +260 ok | +506 ok | +498 ok | 1200 |
| **amp0p6** | **+2954 ✗** | **+2729 ✗** | **+1274 ✗** | +771 ok | +605 ok | 930 |

Duas leituras que a tabela dá de graça:

1. **`amp0p4` e `amp0p5` fecham 10/10** com o mesmo par — e não por folga: os
   erros nos 4 níveis baixos ficam em 125–506 ciclos contra tolerâncias de
   1200–2550. A forma da queda está certa nessas duas.
2. **As 3 falhas são monotônicas e do mesmo sinal** (+2954 → +2729 → +1274 →
   +771 → +605): o modelo entra no colapso **tarde** na `amp0p6` e vai
   recuperando. Não é ruído; é deslocamento de **quando**, não erro de **forma**.

**Margem sobre a resolução do dado** (informacional, medido antes dos gates): a
tolerância fica em 0,78–0,95 dos ±3 % de posicionamento de ciclo declarados pelo
artigo. Ou seja, o gate v2 opera **na resolução do dado** — apertado, mas
bem-posto. Comparar com o gate vertical do v1, que pedia 1,2× a 9× **abaixo** da
resolução.

---

## 2. G1b e G2 — os dois gates de não-regressão passam exatamente

Δ = **0,0000** em MAE e res.máx nos dois. Motivo estrutural, não sorte: com
`D_on`=0,75 e `q`=8 o termo `((D−D_on)/(1−D_on))^8` vale ~3e-8 no fim da janela
pré-trim — a rampa é **numericamente inexistente** antes do joelho. A forma
compra a cauda **sem tocar** no começo.

Informacional (não é gate), curva inteira sem trim: `amp0p25` 0,114/**0,418** e
`amp0p3` 0,127/**0,683**. O 0,683 é, de novo, o **último ponto legível do
digitalizador** — a assinatura *data-limited* da §4.44.

---

## 3. G3 — o gate falha, mas a evidência de discriminância é favorável

| | amp0p4 | amp0p5 | amp0p6 | total |
|---|---|---|---|--:|
| **sem forma** | `.....` | `.....` | `.....` | **0/15** |
| **cliff** (`D_on`=0,999) | `..XXX` | `..XXX` | `...XX` | **8/15** |
| **rampa** (0,75 / q=8) | `XXXXX` | `XXXXX` | `...XX` | **12/15** |

G3 está escrito como `rampa == 15/15 E alternativas < 15` ⇒ com G1 em 12/15 ele
**falha por construção**. Mas o que ele foi escrito para detectar — *a rampa
ganha os 2 parâmetros?* — tem resposta clara: **12 > 8 > 0**, e a rampa vence
exatamente onde o cliff perde (os níveis altos das duas curvas que fecham).

**Ganho metodológico, esse sim conclusivo:** o premeasure havia medido que *"a
métrica vertical não distingue as duas formas nesta fonte"* — a grade v1 melhorava
monotonicamente rumo ao cliff. **A métrica em vida distingue** (12 vs 8). O
problema não era a ausência de diferença entre rampa e cliff; era a métrica não
enxergá-la.

---

## 4. Diagnóstico das 3 falhas — POST-HOC, portanto não é gate

Por que a `amp0p6` falha nos níveis **altos** e as outras duas não? Porque
`r*` fixo cai em posições **diferentes** relativas ao joelho de cada curva:

| curva | r no joelho | posição de r*=0,80 | cruzamento de r*=0,80 (fração da vida) |
|---|--:|---|--:|
| amp0p4 | 0,853 | bem dentro do colapso | 0,878 |
| amp0p5 | 0,836 | dentro do colapso | 0,868 |
| **amp0p6** | **0,812** | **praticamente NO joelho** | **0,775** |

Na `amp0p6`, `r*`=0,80 está a 0,012 do joelho — região **rasa**, onde pontuar em
**vida** é tão mal-posto quanto pontuar vertical no trecho íngreme. É o **problema
espelhado** do que motivou o v2. O §4 do premeasure já havia medido que as três
curvas do núcleo são *a mesma rampa em coordenadas do joelho* (σ ≈ 0,01–0,02 em
`u`); o gate v2 as comparou em coordenadas **absolutas** de `r`, e foi essa
escolha — não a forma — que produziu as 3 falhas.

**Confirmação independente na Fig. 2 (§6):** com o dado fino, `fig2_single`
acerta 6 de 7 cruzamentos e a **única** falha é, de novo, `r*`=0,80 (+1871) — o
nível que ali também cai no trecho raso (joelho em 0,80).

⇒ **Proposta para um v3, a pré-registrar do zero** (post-hoc não vira gate):
níveis definidos em **coordenadas do joelho** (`v` = `r/r_joelho` ∈ {0,94 · 0,90 ·
0,85 · 0,80 · 0,70}), pontuados em vida; e o trecho raso pontuado no vertical.
**Não executar antes de assinar.**

---

## 5. Re-digitalização da Fig. 2 — o que dava para recuperar, e o que não dava

**Das 7 curvas, 6 são irrecuperáveis por re-digitalização.** A Fig. 3 tem o eixo
Y terminando em **20 kN = 0,333·F₀**: as curvas 0,4–0,8 mm saem pelo quadro e a
cauda **não está plotada**. E o inset da Fig. 3 amplia o **começo**
(0–5×10³ ciclos, 35–65 kN), **não** a cauda — a §7 do premeasure supunha o
contrário e estava **errada** nesse ponto.

**A Fig. 2 é a exceção**: plota o colapso inteiro até 0 kN.
`New_Theory/liu2025_fig2_redigitize.py` a re-traça por **varredura de linha** no
trecho vertical (por coluna o colapso teria ~25 px; por linha dá ~300).

| | CSV canônico | traço novo |
|---|--:|--:|
| pontos | 16 | **134** |
| pontos abaixo de F/F₀ = 0,33 | **2** | **45** |
| pontos no colapso, após `FLOOR_TRIM` | 1 | **35** |

**Validação (obrigatória, e ela reprovou duas vezes antes de aprovar):** o traço
é comparado aos 16 pontos canônicos sob o **orçamento de erro declarado da
fonte + rasterização** —
`tol(r) = 0,02 + 1px_r + |dr/dN|·(0,03·N + 1px_N)`, quatro termos, nenhum fitado.
Resultado: **14/14 dentro**, pior razão desvio/tolerância **0,69**.
As duas reprovações anteriores foram achados reais: (i) normalizar pelo centro da
banda na 1ª coluna em vez dos **60 kN nominais** inflava a curva inteira em ~7 %
(com 60 kN o traço reproduz o ponto (3000; 0,8300) **exatamente**); (ii) o
critério vertical de ±0,02 ignorava os ±3 % de ciclo da própria fonte, que no
joelho valem 0,030 em `F/F₀`.

⚠️ **Caveat de amostragem:** o CSV fino é reamostrado **uniforme em `r`**, então
35 de 124 pontos vivem nos últimos ~15 ciclos. Ele **pesa o colapso de
propósito** — MAE dele **não** é comparável com o MAE do CSV canônico (16 pontos,
quase todos no platô).

---

## 6. O teste que a re-digitalização tornou possível — e o achado que ele deu

Com o dado existindo na cauda, a forma acerta?

**Em VIDA: sim.** Cruzamentos do `fig2_single` fino, tolerância 300 ciclos:

| r* | 0,80 | 0,70 | 0,60 | 0,50 | 0,40 | 0,30 | 0,20 |
|---|--:|--:|--:|--:|--:|--:|--:|
| erro (ciclos) | **+1871 ✗** | +296 ok | −33 ok | −30 ok | +43 ok | +99 ok | +143 ok |

**6 de 7**, e a única falha é o nível raso do §4. Entre 0,60 e 0,50 o modelo erra
**30 ciclos** numa curva de 9 789.

**No VERTICAL: não — e não é por falta de dado.**

| config | MAE / res.máx na curva **fina**, sem trim |
|---|---|
| sem forma | 0,2292 / 0,6812 |
| **rampa** (0,75 / q=8) | **0,1011 / 0,3371** |
| cliff | 0,2292 / 0,6812 *(idêntico a "sem forma": cai depois do último ponto)* |

A rampa corta o MAE por 2,3× e o res.máx por 2,0×, e mesmo assim **não passa**.
O motivo é aritmético e **fecha o argumento**:

> No rabo, o dado cai de **0,20 para 0,104 em 5 ciclos**. Para `res.máx < 0,10` é
> preciso acertar o instante da fratura dentro de **±5 ciclos = 0,05 % da vida**
> — numa fonte cujo **scatter de espécime medido é 44 %** e cuja digitalização
> resolve ±20 ciclos. **Nenhuma forma determinística passa**, e **mais dado não
> resolve**: as séries brutas de 200 Hz dos autores dariam resolução melhor, mas
> não mudariam o fato de que a métrica vertical exige, num degrau vertical, uma
> precisão de cronômetro que o fenômeno não tem.

⇒ **Correção ao §4.44 e à §7 do premeasure.** O rótulo *data-limited* estava
**incompleto** para esta fonte. Há duas coisas distintas:

- **6 curvas (Fig. 3): DATA-LIMITED de verdade** — a cauda não foi publicada, e só
  os autores podem supri-la;
- **`fig2_single`: METRIC-LIMITED** — o dado existe, foi recuperado, a forma
  acerta em vida, e o tripé **vertical** segue impossível **por construção da
  métrica**, não por falta de dado nem de física.

E isso **muda a ação recomendada**: para as curvas de colapso quase-vertical, o
que destrava não é pedir dado — é **contar o tripé no eixo em que ele é
bem-posto**. Pedir as séries brutas aos autores continua valendo para as 6 da
Fig. 3 (e para medir o scatter de espécime), mas **não** resgataria o tripé
vertical de nenhuma delas.

---

## 7. O que fica para o professor decidir

1. **A forma não é adotada** (ramo pré-declarado: falha parcial). Fica registrada
   como validada em vida no núcleo `amp0p4/0p5` e falseada em coordenadas
   absolutas na `amp0p6`.
2. **v3 em coordenadas do joelho** — proposta no §4, **a pré-registrar do zero**.
   É a correção que o próprio dado indica, mas é post-hoc e não pode virar gate
   sem assinatura nova.
3. **Métrica por regime** (a decisão maior): admitir que curvas com colapso
   quase-vertical sejam pontuadas **em vida** no trecho vertical. Sem isso, essas
   curvas ficam permanentemente fora da meta por razão **metrológica**, e o trim
   §B é a única saída honesta — agora com justificativa medida, não suposta.
4. **CSV fino**: `New_Theory/liu2025_fig2_fine.csv` **não** substitui o canônico.
   Adotá-lo exige re-simulação, re-carimbo do fingerprint e gate próprio.

---

## 8. Reprodutibilidade

| script | o que faz | custo |
|---|---|---|
| `liu2025_ramp_v2_gates.py` | os 6 gates do prereg v2 (saída em `liu2025_ramp_v2_output.txt`, JSON em `liu2025_ramp_v2_result.json`) | ~13 min |
| `liu2025_fig2_redigitize.py` | re-traça a Fig. 2 (valida contra o CSV canônico; **não escreve se reprovar**) | ~2 s |
| `liu2025_fig2_fine_check.py` | testa a forma contra o traço fino (vertical **e** vida) | ~10 s |

Interpretador com `numpy`/`scipy` neste ambiente: **`py -3.12`** (o `python` do
PATH não tem numpy).
