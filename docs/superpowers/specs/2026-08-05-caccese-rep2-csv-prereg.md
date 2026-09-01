# Prereg — correção da CSV `caccese2009_tapered_45kN_rep2`

**2026-08-05** · decisão **D-S** (por delegação, MANDATO PERMANENTE) · gates
escritos **antes de qualquer escrita**. Classe **dado**, como o D-R do ROUSSEAU.
Achados que motivam: `New_Theory/caccese_piso_e_dado_resultado.md` (extração
vetorial) e `New_Theory/fila_form_limited_3_anatomia.md` §2 (o resíduo do modelo,
independente).

## O defeito, com DUAS provas internas que dispensam o paper

`digitized_csv/caccese2009_tapered_45kN_rep2.csv` tem **26 pontos**. Nove deles
traçam a réplica **errada**. Comparação contra a polilinha vetorial da Fig. 9
(extração `page.get_drawings()`, calibração nos 9 rótulos de tick por eixo,
resíduo **2,3e-5** em F/F₀ e 0,78 h em t, verificada por redesenho sobre o
render — dados preservados em
`BAS_V2_papers/E. Rodada 4 …/vector_extractions/caccese2009_fig9_vector.json`):

| t (h) | CSV rep2 | vetor BAIXA | Δ | vetor MÉDIA | vetor ALTA | |
|---:|---:|---:|---:|---:|---:|---|
| 10 | 0,8004 | 0,8033 | −0,0029 | 0,8568 | 0,8745 | |
| 25 | 0,7736 | 0,7752 | −0,0016 | 0,8310 | 0,8479 | |
| **50** | 0,7955 | 0,7559 | **+0,0396** | 0,8117 | 0,8280 | ⚠️ |
| 75 | 0,7397 | 0,7424 | −0,0027 | 0,7994 | 0,8145 | |
| 100 | 0,7307 | 0,7350 | −0,0043 | 0,7919 | 0,8059 | |
| **150** | 0,7742 | 0,7208 | **+0,0534** | 0,7778 | 0,7906 | ⚠️ |
| **200** | 0,7650 | 0,7119 | **+0,0531** | 0,7689 | 0,7806 | ⚠️ |
| 300 | 0,6933 | 0,6971 | −0,0038 | 0,7540 | 0,7654 | |
| 400 | 0,6825 | 0,6863 | −0,0038 | 0,7433 | 0,7538 | |
| **500** | 0,7319 | 0,6783 | **+0,0536** | 0,7358 | 0,7445 | ⚠️ |
| **600** | 0,7247 | 0,6730 | **+0,0517** | 0,7286 | 0,7367 | ⚠️ |
| **700** | 0,7194 | 0,6672 | **+0,0522** | 0,7231 | 0,7300 | ⚠️ |
| **800** | 0,7135 | 0,6615 | **+0,0520** | 0,7173 | 0,7243 | ⚠️ |
| **900** | 0,7087 | 0,6578 | **+0,0509** | 0,7125 | 0,7195 | ⚠️ |
| **1000** | 0,7081 | 0,6537 | **+0,0544** | 0,7091 | 0,7149 | ⚠️ |
| 1100…2000 | 0,6459…0,6228 | 0,6500…0,6270 | −0,0038…−0,0042 | | | |

**A assinatura é binária, não gradual:** os 16 pontos limpos têm Δ = −0,0016 a
−0,0043 (**offset sistemático constante ≈ −0,004**, o viés do digitalizador); os
9 contaminados saltam a **+0,040 … +0,054** — e caem sobre a curva **MÉDIA**
(t=150/200/500…1000 ficam 0,004 abaixo dela, o MESMO offset) ou entre média e
baixa (t=50).

Prova 1 — **identidade ao dígito**: `rep2` em t=900 (**0,7087**) e t=1000
(**0,7081**) é *exatamente* `rep1` em t=900 (0,7087) e t=1000 (0,7081). Duas
réplicas independentes não concordam a 4 decimais.

Prova 2 — **não-monotonicidade**: `rep2` sobe (0,7736→0,7955 e 0,6825→0,7319) num
ensaio de relaxação **puramente estática** em que TODOS os traços publicados
decrescem monotonicamente.

Prova 3, **independente das duas** — o **resíduo do modelo** troca de sinal em
blocos, saltando ±0,05, exatamente nos 9 pontos; é isso, e só isso, que mantém
σ_res em 0,0258 (o viés é de apenas +0,0195 e removê-lo não muda σ, por
invariância de translação).

⚠️ **A nota de aparato erra o mecanismo** e precisa ser corrigida no mesmo
commit: descreve o trecho como *"an interpolated (not pixel-verified) stretch
≈420–980 h"*. Interpolar 0,6825@400 → 0,6459@1100 daria trecho **monótono**. Não
é interpolação — é **cópia de outra réplica**. Uma nota que se lê como "dado um
pouco mais mole aqui" é, de fato, "curva errada aqui".

## ⚠️ EMENDAS, declaradas depois de rodar os gates e ANTES de escrever

Os gates foram executados em modo só-leitura antes de qualquer escrita, e **dois
deles estavam defeituosos — foi a execução que denunciou**. As emendas ficam aqui
com o texto original preservado; nenhuma delas afrouxa uma barra.

**(a) G1a era VÁCUO.** Como escrito, comparava a CSV nova contra o vetor — e a
CSV nova **é** o vetor: deu `0,00000` exato. *Um gate que não pode falhar não é
gate.* Substituído por **G1a′**: a acurácia do próprio instrumento, isto é o
**resíduo de calibração da extração** ≤ 1e-4 em F/F₀ (medido **2,3e-5**), que é o
que de fato limita a fidelidade. A comparação CSV-velha-vs-vetor passa a ser
**informação** (rep2: máx 0,0544 · mediana 0,0041; rep1: máx 0,0139 · mediana
0,0035), não gate.

**(b) O G4 reprovou por ERRO MEU de instrumento, não por falha do dado.** Usei
`n = b(5) − 1` (0,945 − 1 = **−0,055**), tomando a coluna **b da Eq. (5)** como se
fosse o expoente da Eq. (2). Com `n` negativo `t^n` decresce e `1/(1+K₁t^n)`
**cresce** com o tempo — direção errada. Sintoma que denunciou: RMS ≈ **0,24 nas
três linhas** com razão **1,03×**, ou seja *"nenhuma linha explica a curva"*.
**Regra que isso gera:** gate que reprova TODAS as alternativas com razão ≈ 1 não
está medindo discriminância — está denunciando o instrumento.

Corrigido lendo a **Tabela 5 direto do PDF** (p. 11), com a âncora de sanidade que
o próprio texto da Eq. (2) fornece (Fox [18]: K₁ = 0,0861, **n = 0,2519**):

| Configuration | D (mm) | P₀ (kN) | K₁ | **n** | α(4) | α(5) | b(5) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tapered C/AL | 19,1 | 44,7 | 0,112 | **0,192** | 0,0530 | 0,0447 | 0,945 |
| Tapered C/AL | 19,1 | 44,8 | 0,173 | **0,165** | 0,0635 | 0,0459 | 0,895 |
| Tapered C/AL | 19,1 | 43,9 | 0,091 | **0,217** | 0,0488 | 0,0420 | 0,958 |

**(c) ESCOPO REDUZIDO PELO GATE: a `rep1` sai.** Com o instrumento consertado:

| curva | melhor linha | RMS | 2ª melhor | razão | G4 |
|---|---|---:|---:|---:|---|
| `rep2` (traço 135) | **44,8 kN** (esperado) | **0,0045** | 0,0501 | **11,07×** | **PASSA** |
| `rep1` (traço 241) | 44,7 kN (esperado) | 0,0051 | 0,0067 | **1,30×** | **REPROVA** |

A `rep1` casa a linha **certa** e com RMS baixo, mas a 2ª alternativa fica a
1,30× e o gate exige ≥ 2×. **A reprovação é real e não é defeito do gate:** os
traços MÉDIO e ALTO da Fig. 9 terminam em 0,6805 e 0,6828 — **0,0023 de
diferença** —, e o round-trip pela Eq. (2) genuinamente não os separa (é a
"fresta branca" que a contagem visual a 20× já havia notado).

Como a `rep1` (i) muda **zero** pontos acima de 0,02 (máx desvio 0,0139), (ii) já
**passa o tripé por mérito** e (iii) tem procedência **ambígua entre dois traços
quase coincidentes**, corrigi-la seria trocar dado bom por dado bom de
procedência incerta. **O gate decidiu; a razão mínima não foi afrouxada de 2 para
1,3.** O defeito menor da `rep1` (1 subida) fica **documentado e não corrigido**.

## Escopo: substituir DADO, ZERO números de modelo

* **Substituir 1 CSV pela polilinha vetorial** — `rep2` (traço **135**, o mais
  baixo) —, preservando a convenção de ancoragem `(t=0, 1.0)` que ela já usa.
  Substituir a curva inteira, em vez de remendar os 9 pontos: os 16 limpos
  carregam offset sistemático de −0,0039 (viés do digitalizador), e remendar só os
  9 deixaria degraus de 0,004 nas fronteiras. Medido: as duas variantes diferem
  por no máximo **0,0043** — abaixo do piso de digitalização, logo a escolha não
  muda conclusão nenhuma. *(A `rep1` estava neste escopo e **saiu por reprovação
  do G4** — ver emenda (c).)*
* **Fora de escopo, declarado:** (a) a **3ª réplica** (traço **188**, fim 0,6828,
  linha 43,9 kN da Tabela 5) **não** é adicionada — seria um `case_id` novo e
  mudaria o **denominador** (205→206), decisão do professor pelo precedente LU;
  registrado que o modelo a **passaria** (MAE 0,0263 · máx 0,0296 · σ 0,0054);
  (b) a **protruding preta** (2ª tracejada da Fig. 9) idem; (c) as Figs. 6/7
  (`compblock`, `retighten`) **não** são tocadas — as polilinhas vêm fragmentadas
  em 8–26 pedaços e a extração sem costura devolveu F₀ absurdos.
* **Nenhuma constante do modelo é tocada.** Se a correção pedir re-fit, é outro
  prereg.

## ⚠️ Esta correção PIORA o MAE da `rep2`, e o precedente manda fazer

Estimativa do subagente (reusa `metric_pred`/`metric_x` do store):

| curva | store (mae/mx/σ) | com o dado do paper |
|---|---|---|
| `rep2` | 0,0292 / 0,0468 / **0,0258** | **0,0349** / 0,0452 / **0,0083** |
| `rep1` | 0,0203 / 0,0260 / 0,0054 | 0,0181 / 0,0227 / 0,0051 |

O MAE da `rep2` **sobe 20 %** (0,0292 → 0,0349) porque a réplica verdadeira é
mais baixa e o viés do modelo cresce. O σ cai **3,1×** e a curva **entra no
tripé**. Precedentes explícitos de corrigir o dado mesmo piorando a métrica:
ROUSSEAU `hdpe_t10` em 2026-08-02 (MAE 0,058 → 0,101, adotado) e o erratum do
drive do aço em 2026-08-01. **O gate G2 abaixo diz isso por escrito para que
ninguém precise decidir de novo.**

## Gates (IMUTÁVEIS)

- ~~**G1a (fidelidade):** cada CSV novo casa a polilinha vetorial em todos os
  pontos com |Δ| ≤ 0,005.~~ **VÁCUO — ver emenda (a).** Substituído por
  **G1a′:** o resíduo de calibração da extração ≤ **1e-4** em F/F₀
  (medido **2,3e-5** ✅).
- **G1b (monotonicidade — o gate de fidelidade que de fato mede algo):** a
  relaxação estática é monótona não-crescente em t ⇒ **zero** subidas na saída.
  Medido: a CSV velha da `rep2` tem **3** subidas (o prereg dizia "duas" — a
  contagem exata é 3) e a nova tem **0** ✅. Qualquer subida na saída = extração
  falhou.
- **G2 (a métrica pode PIORAR, e isso NÃO reprova):** declarado antes de medir. O
  gate de "nenhum caso pior" **não se aplica a correção de dado** — ele protege
  contra ajuste que troca curva por curva, não contra corrigir o referencial.
  Registrar a piora com o número.
- **G3 (o que NÃO pode acontecer):** nenhuma curva de **outra fonte** muda, e
  nenhuma das outras **5** curvas do CACCESE muda. Só os 2 CSVs tapered.
- **G4 (round-trip contra o paper):** a curva corrigida casa a linha
  correspondente da **Tabela 5** via Eq. (2) `Pt/P0 = 1/(1+K₁t^n)` com RMS ≤
  **0,006**, e a atribuição tem de ser **inequívoca** (a 2ª melhor alternativa
  ≥ **2×** pior). Medido na 2ª execução, com o `n` correto da Tabela 5:
  `rep2` ↔ **44,8 kN**, RMS **0,0045**, 2ª a 0,0501 ⇒ **11,07×** ✅.
  *(A 1ª execução deu RMS 0,24 e razão 1,03× por erro meu de expoente — emenda
  (b). A `rep1` reprovou a 1,30× e saiu do escopo — emenda (c).)*
- **G5 (o piso é RE-MEDIDO, não herdado):** o piso do par declarado é recomputado
  do store novo. **Previsão registrada: cai** de σ 0,0234 para ~0,002–0,009 ⇒
  `limite_sres(CACCESE_2009)` **continua 0,0250** (o `max` com o global). Se
  subir acima de 0,025, **parar e investigar** — seria sinal de que a correção
  introduziu forma, não que o rig piorou.
- **G6 (procedência):** `vector_extractions/caccese2009_fig9_vector.json` fica
  versionado, o manifest da biblioteca registra figura/método/calibração, e a
  **nota de aparato é corrigida** em dois pontos: "2 tapered" → **3** e
  "interpolated stretch" → **cópia da réplica errada**.
- **G7 (sincronia):** o dado muda ⇒ re-simular as 2 curvas + censo + docs +
  páginas + testes no MESMO commit. ⚠️ **O fingerprint NÃO muda** (ele hasheia o
  bloco `shared` + configs adotadas, **não** os CSVs) — logo o store **não** se
  valida por hash: valida-se **re-simulando e comparando**, e as outras 208
  entradas têm de ficar **bit-idênticas**.

### Ramos

- **ADOTA (corrige o dado)** — G1, G3, G4, G5 cumpridos. A piora do MAE é
  registrada, não é motivo de recusa. Efeito esperado no censo: **+1 estrita**
  (134 → 135) e a fila form-limited cai de 3 para 2.
- **NÃO ADOTA (extração falhou)** — G1 falha: a polilinha não é recuperável com
  fidelidade, ou a saída tem subida. A CSV velha fica, **com o defeito
  documentado** — o que já é melhor que o estado de ontem.

## Ordem: DEPOIS do D-Q

O D-Q (saturação de flanco) está em voo e, se adotado, **muda o fingerprint** e
exige re-stamp uniforme dos 210. Fazer o D-S primeiro faria o re-stamp do D-Q
carregar as duas mudanças, tornando impossível atribuir efeito a causa — a mesma
razão que separou D-H (forma) de D-I (nível). **Escritor único no dado.**

## O que a correção NÃO resolve

O piso desta fonte é de **repetibilidade entre espécimes** e é **pequeno** (σ
0,002–0,009 por 4 instrumentos independentes, incluindo os ajustes Eq. (2) do
próprio paper) ⇒ `limite_sres` fica em 0,025 e **nenhuma perna de nenhuma curva
do CACCESE é afrouxada**. A rota "piso maior ⇒ exceção legítima" segue **fechada
por medição**. Corrigir o dado é sobre **estar certo**, não sobre fechar curva —
o fecho da `rep2` é consequência, não objetivo.
