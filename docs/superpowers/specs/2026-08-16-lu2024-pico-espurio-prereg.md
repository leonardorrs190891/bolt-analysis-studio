# PREREG — correção de REGRESSÃO MINHA: pico espúrio nas 4 CSVs re-digitalizadas do LU_2024

## Estado — **EXECUTADO** (correção de dado; `fingerprint` intocado)

> Registrado em 2026-08-16 (07:0x) pela **sessão A**. A seção faltava, e a catraca
> `test_prereg_declara_estado` **não pegou** — ela casava `PENDENTE` por substring dentro
> de *"inde·pendente"*, palavra que aparece na prosa deste próprio arquivo. O casador foi
> corrigido no mesmo commit.

✅ **EXECUTADO em 2026-08-16** (`db88dcd`): pico espúrio removido de **6** CSVs do
`LU_2024`. Censo **143 → 144**; `engine_fingerprint` **20be19aabe11 INTOCADO** (é correção
de dado, não de física).

O que os gates descobriram, sem nenhum ser afrouxado: a **premissa da regra de reparo era
falsa** (os `.bkp_luD` têm valor no mesmo `x` e monótono — o `y` de pontos existentes foi
corrompido, não houve inserção), e a regra "descartar, não interpolar" fica de pé por
**outro** motivo, medido: as duas passadas têm viés sistemático de **+0,006** e enxertar
misturaria calibrações. O artefato da `fig18_amp0p5` tinha **dois** pontos que se
mascaravam, e foi o **G1** (zero picos) que obrigou a 2ª remoção.

⚠️ Consequência verificada depois (`lu2024_pos_pico_o_que_mudou_e_o_que_nao.md`): a
correção tocou **as duas metades** do par que define o piso de digitalização da fonte, e o
piso de fato mudou — mas `limite_sres(LU_2024)` **não**, porque o piso σ (0,0033) está
**7,7× abaixo** do global.

**2026-08-16 (01:4x)** · sessão B · **gates congelados neste commit** · store
`20be19aabe11`.

## O defeito, e de quem é

A adoção dado-only de 2026-08-13 (`a9541ec`, minha) reescreveu 7 CSVs do
`LU_2024` a partir da figura. Medido agora: **4 delas ganharam um ponto
impossível** — pré-carga SOBE e volta a cair no ciclo seguinte:

| curva | N | antes → pico → depois | res.máx da curva | onde está o res.máx |
|---|---:|---|---:|---|
| `fig20_T10Nm` | 84 | 0,329 → **0,896** → 0,310 | 0,802 | **no pico** |
| `fig20_T16Nm` | 84 | 0,200 → **0,537** → 0,190 | 0,442 | **no pico** |
| `fig20_T28Nm` | 81 | 0,273 → **0,369** → 0,250 | 0,270 | **no pico** |
| `fig18_amp0p5` | 77 | 0,276 → **0,457** → 0,407 | 0,180 | fora (N=17) |

**Os CSVs PRÉ-adoção tinham ZERO picos** (conferido nos `.bkp_luD` das 4) ⇒ a
regressão é da minha extração. Todos os picos caem em **N≈77–84**, a mesma
faixa de x nas quatro ⇒ é feature da FIGURA naquela coluna (caixa de legenda /
marcador), exatamente o hazard que a nota do CHU documenta ("legend-box
occlusion... o tracer travou na borda da legenda").

⚠️ **Por que o meu gate não pegou:** o G1 daquela adoção conferia as âncoras
das Tabelas 8/9 em **c1/c10/c50/c100**. O artefato está **entre** c50 e c100.
Round-trip em 4 pontos não detecta pico entre âncoras. **Lição:** curva de
decaimento de pré-carga é **monótona**; a checagem que faltava é de
monotonicidade, não de âncora.

## A correção — regra declarada ANTES

**DESCARTAR** o ponto espúrio (não interpolar): a coluna está ocluída na
figura, então o valor verdadeiro **não é observável** ali; inventá-lo por
interpolação seria fabricar dado. Precedente: as notas de digitalização do CHU
("bridging the resulting gap, since the true curve is simply not visible
there"). Critério de identificação, fixado: `y[i] > y[i-1] + 0,01` **e**
`y[i] > y[i+1] + 0,01` (sobe e volta).

## GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | **monotonicidade** | nenhuma curva do `LU_2024` mantém pico pelo critério acima |
| **G2** | **âncoras preservadas** | as âncoras das Tabelas 8/9 (c1/c10/c50/c100) seguem batendo a **±0,005** nas 7 curvas re-digitalizadas |
| **G3** | **cirurgia mínima** | todos os demais pontos das 4 curvas ficam **bit-idênticos**; só as linhas do pico saem |
| **G4** | **isolamento** | Δ = **0,0000 exato** em toda curva fora do `LU_2024` |
| **G5** | **censo** | o censo **não encolhe** (143/205 é o piso) |
| **G6** | **guarda permanente** | teste novo que falha se QUALQUER curva do store ganhar pico pelo mesmo critério — a regressão não pode voltar calada |

## Predição registrada

O `T10Nm` melhora forte no res.máx (0,802 → ~0,31) e no σ (0,155 → ~0,075) mas
**NÃO fecha** (MAE ~0,25, 5× o limite): o defeito de forma dele — perder demais
em F₀ baixo — é independente do artefato. Se fechar, procurar erro.

---

## ADENDO da execução (2026-08-16, mesma sessão) — três achados dos GATES

Nenhum gate foi afrouxado. Os três itens abaixo são coisas que os gates
congelados **descobriram** e que o texto acima dizia errado; ficam registrados
porque mudam o escopo e o desenho do G6.

### A1 — a premissa da regra de reparo era FALSA (a regra continua valendo)

O texto diz *"o valor verdadeiro não é observável ali"*. **Falso, medido:** os
`.bkp_luD` têm um valor em **exatamente o mesmo x** nas quatro, e ele é monótono
(`T10Nm` x=85: 0,327, entre 0,329 e 0,310). Eu não *inseri* pontos — **corrompi
o `y` de pontos existentes**; o x-grid é idêntico dos dois lados.

**A regra (descartar, não interpolar) fica de pé por outro motivo, também
medido:** as duas digitalizações têm calibrações diferentes, com viés
sistemático de **+0,006** em todos os pontos vizinhos. Enxertar o `y` antigo na
curva nova misturaria duas calibrações **num ponto só, em silêncio** — que é a
classe de defeito que esta campanha mais penaliza. Descartar nunca inventa dado.
Recuperar de verdade exige **re-digitalizar a coluna**, e isso é prereg próprio.

### A2 — o artefato da `fig18_amp0p5` tem DOIS pontos, e o G1 é que obriga o 2º

Removido o x=78, o x=85 (0,407) passou a satisfazer o mesmo critério — os dois
pontos corrompidos se **mascaravam mutuamente** enquanto vizinhos. O G1 pede
*zero* picos, então iterar não é mover a trave: é o que o gate literalmente
exige. `.bkp_luD` confirma: os dois valores pré-regressão (0,250 e 0,208) são
monótonos.

### A3 — o G1 puxou 2 curvas que NÃO são minha regressão, e o escopo é dele

`fig18_amp1p0` e `fig20_T22Nm` disparam o critério em **x=80** (0,085 →
**0,352** → 0,072). Medido contra `.bkp_luD`: **idênticas** ⇒ o artefato
**precede** `a9541ec`, não é meu. Mas o G1 congelado diz *"nenhuma curva do
`LU_2024`"*, e elas são do `LU_2024` ⇒ entram por força do gate.

Três fatos que sustentam o reparo delas sob a MESMA regra:
1. **Impossibilidade física**: triplicar a pré-carga e voltar, em Junker
   contínuo sem reaperto, não existe.
2. **As duas são o MESMO ensaio em 2 figuras** (Tabela 8@1,0 mm ≡ Tabela 9@22
   N·m) e trazem o artefato no mesmo x com o mesmo valor (0,352/0,353) ⇒ duas
   digitalizações independentes travaram na **mesma curva errada** — aqui a
   premissa de oclusão do texto original de fato vale.
3. Reparar **as duas juntas** preserva o **piso de digitalização** do par (que
   é o instrumento de exceção F7 da fonte); reparar uma só o corromperia.

### A4 — o G6 NÃO pode usar o critério de vizinhos (ele perderia minha regressão)

Medido: no critério `y[i] > vizinhos + 0,01`, o artefato de 2 pontos da
`fig18_amp0p5` dá salto de **0,050** — porque o 2º ponto corrompido *sustenta*
o 1º. Uma guarda com piso absoluto em 0,05 teria deixado passar exatamente a
regressão que ela existe para pegar.

A estatística que serve é a que a própria lição nomeia — **monotonicidade**:
`max(y − mínimo corrente)`, normalizada pela escala da curva (há curvas em % e
outras em fração). Medida no universo (210 curvas):

| população | valor |
|---|---:|
| mediana das 210 | **0,0000** (a maioria é exatamente monótona) |
| minha regressão (4, nos `.bkp_pico`) | 0,146 · 0,261 · 0,485 · **0,612** |
| artefato pré-existente (2) | 0,393 · 0,399 |
| pior **legítimo** não isento (`jcsr2023_plain_outdoor`) | **0,083** |
| protocolos que recuperam pré-carga (isentos, nomeados) | `eccles…intermittent` 0,429/0,062 · `caccese…retighten` 0,032 |

**Barra do G6: 0,10** — 1,2× acima do pior legítimo e **3,9× abaixo** do
artefato mais brando. A margem é assimétrica e fica declarada assim no teste;
protocolo que recupera pré-carga (intermitente/reaperto) é **isenção nomeada
com razão física**, nunca whitelist silenciosa.
