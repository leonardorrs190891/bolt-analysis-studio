# Ledger da campanha FAXINA-E-ANATOMIA

Charter: `AUTONOMOUS_CAMPAIGN.md` §CAMPANHA FAXINA-E-ANATOMIA (2026-08-06).
Um bloco por tick do loop; achado sem número não entra.

---

## Tick 1 — 2026-08-06 · LU_2024 (fases 1–3) + varredura global de assinaturas

Store `b70276f2fa43` (138/205). Só-leitura; dois subagentes de investigação
lançados (VAZÃO: diagnóstico em paralelo, adoção em série).

### LU_2024 — anatomia (fase 1): a hipótese "9 viés-dominadas" REESCRITA

O viés é **negativo em 12 das 13** (modelo PERDE demais, não retém demais) com
zero cruzamentos em 11. Dois padrões, nenhum deles defeito de dado novo:

* **Straddle de réplica no 0,5 mm**: `fig14_amp0p5` viés **−0,1257** ×
  `fig18_amp0p5` viés **+0,1245** — mesma condição nominal, réplicas em lados
  OPOSTOS do modelo por ±0,125. Coerente com o piso colossal já medido entre
  réplicas (MAE 0,283). Scatter real; as exceções/declaradas existentes já o
  tratam. Nada a corrigir.
* **fig20 = 3ª ocorrência de SUB-RESPOSTA À VARIÁVEL VARRIDA**, agora no
  **torque**: viés monótono T4 **−0,34** → T10 −0,26 → T16 −0,17 → T22 −0,09 →
  T28 −0,10 (platô). O modelo perde demais em pré-carga baixa. Junta-se à
  frequência (LI_2022) e à espessura (ROUSSEAU) —
  `subresposta_a_variavel_varrida.md` ganha um 3º membro. Rota conhecida: o
  re-fit P3 de `lu2024_plano_melhoria.md` (âncoras novas do paper), que é
  trabalho de MODELO com gates, não faxina.

### LU_2024 — fidelidade (fase 2): rota vetorial FECHADA

`lu2024_sensors_M8.pdf` (25 pgs): Figs. 14/18/20 são **RASTER** (62–146 imagens
por página, **zero** polilinhas >40 segmentos). Fidelidade existente: round-trip
da fig14 (10511 vs 10539 N, 0,3 %) e o par duplicado amp1p0↔T22 medindo piso de
digitalização σ 0,0192/MAE 0,0127. Sem ganho barato aqui; pixel-digitização só
com prereg próprio se algo a motivar.

### LU_2024 — input (fase 3): já auditada historicamente

Drive 2× corrigido (erratum 2026-07-31), duplicata fig18_amp1p0≡fig20_T22Nm
fora do censo, F₀ lidos das Tabelas 8/9. Sem pendência nova.

**Veredicto LU_2024 no pipeline: SEM defeito de dado novo; causa nomeada
(scatter + sub-resposta ao torque); rota restante = P3 re-fit (fila de modelo,
não de faxina).** Conta como fonte "seca" para a regra de parada (0 mérito, 0
defeito de dado).

### Varredura GLOBAL de assinaturas internas (fase 2ii antecipada para as 29)

Identidade-ao-dígito entre irmãs + subida em ensaio estático + reta no colapso,
computadas de uma vez (`assinaturas_globais.txt` no scratchpad; recomputável do
store em segundos). **3 pistas fortes**:

| # | pista | assinatura | estatuto hoje | risco/ganho |
|---|---|---|---|---|
| 1 | SUN_2025_REASSY `reassy02 ~ reassy04` | **8/23 idênticos, RUN de 8** (x=100..1000) | ambas provavelmente no tripé | classe CACCESE-rep2 OU sobreposição real |
| 2 | LIU_2016 `fig13a_dry ~ fig7_run1` | 7/25 idênticos, run de 5 (x=5e3..5e5) | **ambas no tripé** | classe LU-duplicata ⇒ DENOMINADOR cai (rigor contra nós) |
| 3 | ICMEZ `demir2024_amp0p3_F17p6_lk19p8` | escada quase perfeita no colapso (std 0,00044, queda 0,041/passo) | **passa por mérito** | se o dado for reta, o passe é falso |

Subagentes lançados para 1 e 2 (só-leitura, com a barra de prova do precedente
LU: identidade documental, não semelhança). A 3 fica para o próximo tick.

Benignos documentados: subidas ≤0,002 em estáticos = jitter de digitalização
(GRZEJDA/QIN/compblock); `jcsr_plain_outdoor` sobe **0,0585** mas é ensaio
OUTDOOR — ciclo térmico diário pode ser física real, exige o paper antes de
chamar de defeito; pares fracos (ECCLES 3/20, JCSR 2/12) compatíveis com
arredondamento grosso; pares âncora interna fora do projeto.

**Placar da regra de parada: 1 fonte seca (LU_2024). Pistas em voo: 3.**

---

## Tick 2 — 2026-08-06 · pistas 1 e 3 FECHADAS (benignas), com método novo

### Pista 1 (SUN reassy02~04) — veredicto (a): sobreposição REAL, zero ação

Subagente com prova de pixel + texto. O par preto/vermelho da Fig. 11(a) é uma
**banda composta única** no raster no trecho do run (separação 0,004–0,007 ≪
resolução de leitura ±0,01; linha tem 3–4 px ≈ 0,005). O próprio paper declara:
*"There was no significant difference in the loosening degree of the nut after
the second and fourth repeated assembly cycles... 53.67 % and 52.56 %"* — dois
endpoints DISTINTOS anotados em caixa ⇒ duas medições ⇒ mata a hipótese de
duplicata. Os 15 pontos que diferem são todos unilaterais (04>02, +0,003 a
+0,0111) e crescem rumo ao rabo. As duas curvas passam o tripé; censo intacto.

⚠️ **Método novo, entra no instrumento da varredura** (presente do subagente):
*run idêntico só prova contaminação quando a separação das curvas no raster
EXCEDE a resolução de leitura no trecho.* Sinais auxiliares baratos: (i)
diferenças unilaterais sem cruzamento + endpoints ancorados distintos ⇒ par
colapsado por resolução (benigno); (ii) valores do run na grade grossa (0,005)
com rabo em grade fina ⇒ leitura compartilhada, não cópia. No CACCESE rep2 as
réplicas eram RESOLVÍVEIS no traço — por isso lá era contaminação.

Caveat registrado de passagem (não muda nada hoje): a família da Fig. 11a tem
**viés de head** na digitalização (+0,033..+0,003 em x=200..750, comprimida
para o meio no ombro íngreme) — o "N<200 = shape approximation" da nota
subdeclara o alcance. Só importa se o head do SUN virar alvo de forma de
estágio I.

### Pista 3 (demir amp0p3_F17p6_lk19p8) — benigna POR PROCEDÊNCIA

Leitura fina: a inclinação é constante em **−0,00200/ciclo de N=30 a N=200**
(o Δy=−0,04 era a grade de x mudando 10→15→20). Mas: (i) a nota documenta que
as curvas do demir foram extraídas das **polilinhas VETORIAIS do próprio PDF**
(699 segmentos, PyMuPDF, calibração por tick) ⇒ não existe "régua nossa" — o
trecho reto é da curva publicada; (ii) a inclinação tem **deriva** (2,000 →
2,055 ×10⁻³), não a constância exata da `steel_t10` (σ 5e-5); (iii) estágio II
quase-linear é física clássica de Junker. **Refinamento do discriminante de
reta**: CSV com procedência vetorial não pode ter reta de digitalização — a
assinatura só acusa nos CSVs de leitura manual/raster.

### Correção de instrumento (minha): glob de PDF por token genérico

"behaviour of bolted" casou o paper ERRADO ("Failure behaviour...", outra
fonte). Localização de PDF é pela **nota de aparato** (campo PDF:), nunca por
token — a nota do demir apontava `pdfs_open_access/demir2024_ejrnd_M8.pdf`.

**Placar: 1 fonte seca (LU_2024) · pistas 1 e 3 benignas · pista 2 (LIU_2016
dry≡run1) em voo com subagente.**

---

## Tick 3 — 2026-08-06 · pista 2: RE-PLOTS no LIU_2016 + 5ª chave cega corrigida

### Veredicto do subagente: (a) MESMO ensaio republicado — prova METROLÓGICA

`fig13a_dry` ≡ `fig7_run1` com mean|Δ| **0,21 pt** no impresso (retificação de
4 figuras a 300 dpi, calibração ±0,12 pt), onde o par de réplica **verdadeiro**
run1↔run2 — mesmo painel! — difere **1,78 pt**. As duas suspeitas coincidem
**15× mais justo que a réplica irmã**, por 4 décadas de ciclos. E a sonda achou
mais: `fig9a_m30nm` e `fig11a_af10kn` são o MESMO teste pela 3ª e 4ª vez (o
paper re-usa a curva de referência M0=30/AF=10kN/seco em toda figura de
varredura; excursões locais ~1 pt explicadas por **overprint** medido — em
N=700k a banda tem 10 px azuis contra 83 vermelhos).

Hipótese (c) cópia-na-digitalização: **refutada** (os CSVs enganavam nas DUAS
direções — a divergência de head deles não existe no impresso, r=0,04, e os 7
empates exatos eram quantização na grade 0,005). Hipótese (b) coincidência:
**refutada por medição** (scatter do rig: 45 juntas nominais dão F₀ 12–16 kN).

### Por que NÃO executei a retirada do censo

A prova é **metrológica** — um degrau abaixo da barra documental do LU
(Tabela≡Tabela ao dígito, zero hipóteses; aqui a identidade passa pela correção
×2 da legenda da fig13, já adotada). Retirar re-plots muda o **DENOMINADOR**
(205→204, tripé 138→137 no caso mais limpo) e isso é decisão do professor pelo
precedente do LU. **Registrado como P-6** na fila, com o diagnóstico pronto.

### 5ª ocorrência da CHAVE CEGA — executada (higiene, classe já estabelecida)

A família de piso `LIU_2016 δ=0 F=10000` juntava **n=10**: a varredura de
torque INTEIRA (fig9a m30..m50), a fig11a af10kn, a de LUBRIFICAÇÃO (dry E
MoS₂!) e as duas corridas da fig7 — piso falso MAE 0,1025 · σ 0,0176 =
espalhamento de CONDIÇÃO, ainda por cima contendo os re-plots. Bloqueadas as
14 em `_SEM_FAMILIA_MECANICA`; o par VERDADEIRO run1↔run2 (o próprio paper:
*"the self-loosening curves of two bolted joints ... are different"*) entra
DECLARADO e mede **0,0044 / 0,0130 / 0,0024**. `limite_sres` = 0,0250 antes e
depois; **0 curvas mudam** (medido). Caveat gravado no código: os impressos de
run1/run2 divergem 1,78 pt onde os CSVs divergem 0,44 (overprint em 200k–500k)
⇒ o piso de CSV pode SUBESTIMAR o scatter — seguro nas duas direções, porque o
`max` nunca aperta e piso baixo só dificulta F7.

Consertado junto: typo U+2126 (OHM SIGN) onde eu quis U+2260 (≠) no bloqueio
do ROUSSEAU — dois caracteres visualmente idênticos, e foi o Edit falhando o
casamento que denunciou.

**Placar: 1 fonte seca (LU_2024) · 3 pistas fechadas (2 benignas + 1 P-6) ·
5ª chave cega corrigida · próxima fonte do mapa: YANG_2023_IJPEM (5
viés-dominadas, sem PDF — só assinaturas internas + round-trip com o
companion OA).**

---

## Tick 4 — 2026-08-06 · YANG_2023_IJPEM: eixo N sob CONTRADIÇÃO de ordem de grandeza

### Anatomia: NÃO é a 4ª sub-resposta — o contador fica em 3

Sinais do viés na ordem de amplitude (0,15→0,65): `+ + + + − − + − +` — troca
de sinal **duas vezes** no M8, não é monótono. A classe é a já nomeada e
esgotada **bimodalidade stick/runaway** (4 preregs falsificados: scrit,
delta_free v1/v2, par, trio): vida implícita do modelo 0,13×–0,45× do dado nas
5 supra-limiar que colapsam, e **stick** (0,946 vs 0,520) na 0,25. Bifurcação,
não expoente.

### O achado grande — PROCEDÊNCIA DO EIXO N (gravado na nota de aparato)

Companion OA lido do PDF: Table 5 mede vidas **~1e4–1e5** em 0,3/0,4/0,5 mm
(critério ATÉ mais estrito, 20 % de perda) com predição **±1,2×** usando a
MESMA D-N; nossa tabela dá **1463/340/110** ciclos. E a linha 23 do
DEEP_RESEARCH já dizia "~1e4–1e5". Mais: os y das 9 são múltiplos de
0,005–0,02 e os x todos em {0,2,5,...,2000} — **tabela sintetizada** de paper
que a deep-research nunca abriu. **Suspeita: eixo N comprimido 1–2 ordens de
grandeza.** Rebaixamento gravado: o bracket de limiar 0,18<δ_th<0,25 segue
válido (vem da matriz de ensaios); **nada no eixo N ancora forma/relógio** até
adjudicação (instrumento: as 18 vidas com réplica do companion, já na fila).

### Inputs: FECHADOS ao dígito contra o primário

freq 10 Hz · F₀ 14,3 kN (M8) · 11 kN (M6) — os 2 desacordos históricos da nota
estão resolvidos. Novidades anotadas: `preload_percent_yield` M6 45→58,2 %
(INERTE, display-only, higiene pendente) e a âncora **kx=1,255e7 N/m** do
companion (Table 3) não consumida — o k_tr efetivo é 2,4× mais rígido,
compensado pelo `delta_free` adotado; destravar só a cinemática já foi medido
2× (runaway 0,000 vs 0,520).

### Estatutos: TODOS confirmados corretos (e sub-inclusivos, nunca contraditórios)

As 4 declaradas por n<6/colapso **também** passariam no critério de resolução
(med|Δdado| 0,16–0,225 ≥ 0,10). A 0,25 fica mesmo abaixo (0,080) — fio de
navalha: sem o intervalo-âncora a mediana dá exatamente 0,100. Registrado sem
re-litigar critério assinado.

**Veredicto: 0 curvas fecháveis; defeito de dado ACHADO (documental — o
conserto exige o paper paywall). A fonte NÃO conta como seca ⇒ contador da
parada RESETA (LU_2024 fica como única seca). Próxima fonte: YANG_2021.**

---

## Tick 5 — 2026-08-06 · YANG_2021: âncora sistêmica ⇒ **D-U executado** (censo −1, honesto)

### O achado (subagente; figuras VETORIAIS, 12k–56k segmentos)

As 6 digitalizações **originais** ancoravam o 1º ponto — **x=0 INVENTADO**, os
traços publicados começam em N≈100–750 — no **TOPO da banda de oscilação**
(duas delas 0,20–0,36 kN **acima do máximo desenhado**), enquanto o resto segue
os **centros**. O runner divide pela 1ª amostra ⇒ deflação multiplicativa de
−2 % a −9,4 % por curva. Item (e) da fila do professor respondido: o +9,93 %
da `amp0p7` existe no impresso mas é topo de banda (carga axial transmitida,
Φ≈0,15), não overshoot de aperto.

### Execução (prereg `2026-08-06-yang2021-ancora`, molde D-S/D-R)

**Predições registradas: 6/6 EXATAS** (tolerância ±0,02; erro real ≤0,002):
`amp0p7` melhora nas 3 pernas (0,0130/0,0470/0,0167) · viés flipa de sinal nas
6 (o "modelo perde demais" era artefato) · **`r1` SAI do tripé** (mx 1,01× ·
σ 1,27×) — custo declarado ANTES, precedente CACCESE invertido: estava DENTRO
por artefato de âncora. Controles r2/r3 e 202 de outras fontes bit-idênticos.
Censo **138→137** · σ-manda 31→**32**.

### ⚠️ Predição do G5 ERROU a direção, e fica registrado

Previa o piso-MAE da família 0,6 mm **caindo ~2×**; medido: 0,0214→**0,0329**
(subiu 1,5×). σ 0,0113→0,0132 (≈, como previsto) e `limite_sres` fica 0,0250
(a cláusula operativa passou). Hipótese para a errada: a medição
traço-vs-traço do diagnóstico usava âncora em **N comum**; a convenção de CSV
ancora cada réplica no **próprio** 1º ponto visível (N=433/475/500), e esse
desalinhamento de âncora entra no piso. Sem consequência hoje (nenhuma prova
F7 do YANG_2021 cita o piso-MAE) — mas predição errada é predição errada.

### 3 emendas de instrumento no dry (declaradas no prereg)

(1) unidades da checagem de banda; (2) RMS no platô, não na curva inteira; (3)
**estrutural**: RMS contra o CSV velho não pode gatear ATRIBUIÇÃO — não separa
"traço errado" de "traço certo, digitalização ruim". Atribuição = identidade
independente do arquivo defeituoso: rótulo de painel + vida (≤3 %) + `ini_max`
cravado (±0,05 kN; 6/6 exatos).

### Nota de aparato corrigida (G6, 3 itens)

(a) "overshoot ~15,5 kN" → topo de banda, não aperto; (b) painéis Fig. 6
(a2)≡(a3) são GÊMEOS no paper (centros a 0,036 kN, vidas a 0,2 ciclo, larguras
2,4× ≠) — um rótulo errado na origem, não afeta o store; (c) Fig. 2 é medição
INDEPENDENTE da (a3) — não é duplicata de censo.

**Placar: LU_2024 seca · IJPEM defeito documental · YANG_2021 defeito de dado
EXECUTADO (D-U) · LIU_2025 interrompido pelo limite (retomar) · campanha
transiciona para MARGENS (decisão do professor, 2026-08-06 tarde).**

---

## Tick 6 — 2026-08-06 · LIU_2025: fonte SECA, e a "contradição D–N" era CONDICIONAMENTO

Subagente retomado do transcript após o limite de sessão (nada re-pago; o que
estava no scratchpad foi reusado). Três resultados:

### (a) O rótulo por fonte errou 2 dos 4 membros — exatamente o risco do charter

As 5 curvas ≤0,6 mm têm a MESMA assinatura: **viés = −MAE exato, zero
cruzamentos, modelo ABAIXO do dado na janela inteira** — relógio de estágio
I/II **ADIANTADO** em amplitude baixa (o P5 informacional confirmado com
números frescos: N₉₅ do modelo 0,01–0,25× o da curva). É o **oposto** de
"aceleração tardia". `amp0p3` é NÍVEL PURO (sem o viés passa as três pernas).
Só `amp0p8` (+viés, pico a 36 %) e `fig2` (pico +0,057 no ÚLTIMO ponto) são
aceleração tardia de verdade. Rotas: todas já esgotadas com prereg (arco
s1_amp_gate; a re-temporização coordenada fecharia a amp0p3 primeiro e foi
VETADA pelo custo nas 3 do meio).

### (b) A "contradição D–N⊥curvas 3–5×" RECLASSIFICADA: mau condicionamento, não dado

O paper declara (p. 4) que a Fig. 4 foi *"constructed by extracting the
vibration cycles ... when the clamping force declined to 95%"* **das mesmas
curvas** — é UMA medição lida duas vezes, não duas medições. Em **y** as duas
figuras concordam a **±0,014 em 5/6** (a 6ª dentro da meia-banda 0,0525). O
"3–5× nas duas direções" é o critério N₉₅ — resumo de 1 ponto num platô raso —
amplificando ±0,01 de y em até **40× em N** (0,25 mm: bracket 4k..164k).
**Consequências**: (i) o eixo N da Fig. 4 NÃO se rebaixa como dado (≠ classe
IJPEM); o que se rebaixa é o **N₉₅ como âncora de relógio** em qualquer das
duas figuras; (ii) o INCONCLUSIVO do s1_amp_gate ENDURECE por caminho novo;
(iii) o rascunho de pedido de dado aos autores encolhe para a única lacuna
real — a amplitude da Fig. 2 (errata viva confirmada no texto: *"a typical"*).

### (c) Fidelidade e input: LIMPOS; 3 achados de dado, nenhum acionável

Figuras RASTER (rota vetorial fechada); medição por pixel calibrada nos ticks.
`amp0p3` é a digitalização mais limpa da fonte; `amp0p8` tem flag FRACO
(colapso ~10–15 % cedo em 1 de 3 níveis; se re-digitalizar um dia, refazer o
fat_C1 no MESMO prereg); `amp0p25` tem 3 achados TODOS não-acionáveis: o desvio
do platô é ≤0,02 **e anti-resgate** (corrigir AGRAVA o viés do modelo — o CSV
atual lisonjeia o modelo), o joelho 200k–246k está **OCLUÍDO PELA LEGENDA** no
impresso (os 2 últimos pontos da métrica são interpolação não-verificável), e
a cauda divergente está toda além do trim. Inputs: F₀/δ/trims/fat_C1 conferidos
**ao dígito** (7/7 = `liu2025_e2_contas.json`); higiene anotada: chaves
`amp0p8: 11500` mortas nos trim dicts dos subgrupos amp0p4/amp0p5.

**Placar da faxina (pausada, fase A da MARGENS assume): LU_2024 seca ·
LIU_2025 seca · IJPEM/YANG_2021 defeitos achados e tratados. O contador de
parada da faxina fica em 1 (LIU_2025; o D-U resetou antes).**

---

# CAMPANHA MARGENS — fase A (fila quase-lá ≤1,30×)

## Tick M1 — 2026-08-06 · fila rankeada; alvo nº 1 CONSERTADO (D-W, +1)

Fila medida no store pós-D-V (11 curvas ≤1,30×). Estado por alvo:

| # | curva | pior perna | veredicto |
|---|---|---|---|
| 1 | `lu2024_fig18_amp1p5` | mx 1,05× | **(a) ARTEFATO ⇒ D-W executado, TRIPÉ** |
| 2 | `liu2025_fig2_single` | σ 1,07× | causa nomeada (tick 6: data-blocked) |
| 3 | `bauer_rep5` | mx 1,12× | (b) confirmado no impresso; exceção fica |
| 4 | `chu_D0p5_Ra1p6` | mx 1,17× | investigação em curso |
| 5 | `bauer_test3` | mx 1,20× | (b) confirmado; exceção fica |
| 6 | `karlsen_run1p2` | MAE 1,21× | investigação em curso |
| 7 | `eccles_fig8a` | mx 1,22× | investigação em curso |
| 8 | `bauer_rep1` | mx 1,26× | (b) confirmado (3 pontos >0,10); exceção fica |
| 9 | `yang2021_r1` | σ 1,27× | causa nomeada no D-U: réplica-outlier (modelo passa 2 de 3 réplicas; dado re-ancorado do vetor é o fiel) |
| 10 | `liu2025_amp0p3` | MAE 1,29× | causa nomeada (tick 6: nível/relógio adiantado; rotas esgotadas) |
| 11 | `eccles_fig8b` | mx 1,30× | investigação em curso |

### D-W — `lu2024_fig18_amp1p5`: o argmáximo NÃO existia no impresso

Prova dupla: (i) pixel calibrado (4 âncoras da **Tabela 8 do próprio paper**,
resíduos ≤0,0032) — o ponto N=19 do CSV (0,2500) fica 27 px acima do único
blob verde da coluna (0,2196), e o desvio é **sistemático** (+0,021..+0,035 em
x=10–70, deriva de x da digitalização original); (ii) a **Tabela 8 reprova o
CSV vigente** independentemente de pixels (+0,021/+0,025 em c10/c50, onde o
novo crava −0,0003/+0,0002). Predições PASSAM (0,0314/0,0742/0,0353 nas
faixas registradas), irmãs bit-idênticas, e a curva sai de `_DECLARADAS` **por
mérito** (o trigger metric-limited continua verdadeiro — a classificação só
importa para quem não passa). **Censo 138→139 · declaradas 15→14.**

⚠️ Emenda de gate no dry, declarada: a âncora c=100 estava na zona de ±0,01 de
incerteza local declarada E abaixo do FLOOR_TRIM ⇒ gateiam c1/c10/c50, c100 é
informação.

### BAUER: as 3 quase-lá são (b) — e o piso ganhou a validação que faltava

Bijeção réplica↔traço PROVADA (RMS 0,001 contra 2º melhor 50–130× pior; zero
classe CACCESE); os pontos que reprovam existem no impresso (até o "bump" da
rep5 é medição real); contrafactual com digitalização perfeita **não passa
nenhuma**. Ruído de digitalização (≤0,003) é 30–95× menor que o piso ⇒ o piso
mede scatter de ESPÉCIME. Causa nomeada: relógio do colapso terminal (M8
~9–11 % cedo; M12-espectro ~6 % tarde). Exceções FORTE ficam.

## Tick M2 — 2026-08-06 (noite) · fase A′: KARLSEN **+1**, SUN **−1**, saldo 0

Os dois alvos de "fechar fonte" renderam em **direções opostas** — e é o par que
ensina mais que qualquer um sozinho.

### D-X · KARLSEN `run1p2`: conserto real, predição cravada

O CSV ancorava `(1, 1.0000)` num valor que a Fig. 10 só atinge no **ciclo ~26**
(a curva está soterrada no feixe inicial e o digitalizador não viu o ciclo 1):
base **5,0 % baixa**. Corrigidos F₀ 315→**331 kN** (pct 60→66) e a CSV
re-baseada:

```
0,0603 / 0,0940 / 0,0306   ->   0,0171 / 0,0434 / 0,0195
previsto                        0,0171 / 0,0435 / 0,0195
```

Passa o tripé pelos **limites globais**; as outras 10 da fonte bit-idênticas.
Exceção F7 **retirada por mérito**.

⚠️ **O aviso de isolamento definiu o escopo**: re-digitalizar a Fig. 10 inteira
quebraria `run2p2` e `run7p1`, que carregam `k_ratchet` per-espécime **fitado
contra a série defeituosa**. A `run1p2` é a única sem config próprio ⇒ única
correção isolada. As outras 4 ficam como **dívida declarada** (prereg com
re-fit no mesmo passo).

### SUN_CRIMP: veredicto (b) — e a premissa da fase A′ INVERTE

Digitalização certa (máx |Δ| **0,0069** em F/F₀ na curva inteira). O colapso em
N=167 é **do modelo**: o dado é exponencial puro (τ=172,7, **R²=0,9961**) e o
engine só tem dois atratores — arresto no piso ou zero. A curva vive no meio.
Detalhe em `sun_crimp_resultado.md`.

### Duas chaves cegas a mais (6ª e 7ª) — e a 1ª que CUSTA curva

* **SUN_2025_CRIMP (6ª)**: zero pares válidos; o "piso" da família δ=0,3 tem
  **MAE 0,448** porque pareia porca crimp × padrão (o assunto do artigo).
  Limite 0,06627 → 0,0250 ⇒ **`grease_crimp` SAI** (σ 1,21×). **−1.**
* **KARLSEN_2022 (7ª)**: pareava `run21p0` (M42 HV) × `run29p0` (M42 Vibralock
  torqueado) só porque `F_amp = 0,4·F₀` coincide. Limite 0,1742 → **0,0845**.
  Censo da fonte inalterado, **mas** cria uma retratação (abaixo).

### A retratação que a NOSSA correção criou (registrar é obrigatório)

Sob o piso **inválido**, a perna σ da `run14p2` nem violava (0,49×). Sob o piso
válido ela viola (1,01×) **e fica descoberta por 1,1 %** — a margem mais fina
da campanha (as anteriores foram 6 % e 2,1×). Declarar a família M30-HV inteira
cobriria, mas daria piso σ **0,1644 = 6,6× o global**: **recusado** — salvar
exceção afrouxando a barra é o inverso da regra. **Resolvida −1.**

**Saldo do tick: censo 139 (+1 D-X, −1 SUN) · exceções 25 → 23.**

### O invariante pegou um erro MEU, e o texto da prova o resolveu

A suíte reprovou em `test_excecao_assinada_esta_de_fato_fora_do_tripe` — no
**espelho** da regra: *toda retirada D1 tem de continuar passando; se voltou a
falhar, a retirada tirou perdão de quem ainda precisa*. Réu:
`sun2025efa109235_transverse_grease_crimp`.

Eu havia escrito o custo **em prosa** (`sun_crimp_resultado.md`: "sai do tripé,
censo −1") e **esquecido a contabilidade em código**. A causa saiu do próprio
registro: a prova preservada em `_EXCECOES_RETIRADAS_D1` diz textualmente
**`"prova de piso (FORTE): σ 0.030/0.066"`** — e o `0,066` *é* o piso que o
bloqueio da chave cega acabou de invalidar.

⇒ tratamento é o precedente já codificado (ROUSSEAU 2026-08-01, JCSR
2026-08-01): entra em `_RETIRADAS_D1_INVALIDADAS_POR_ERRATUM`, **3ª ocorrência
da mesma estrutura**. A assinatura **não** volta — devolvê-la seria re-assinar
contra piso inválido. Censo inalterado (a curva já estava fora); o que muda é
que a perda passa a estar escrita onde o teste lê, não só onde eu escrevi.

**Lição:** declarar custo em documento não é registrá-lo. O invariante só
policia o que está em código.

## Tick M3 — 2026-08-06 (noite) · a dívida do D-X, sondada e reenquadrada

**KARLSEN está 10/11** (só a `run14p2` fora). A `run2p2` passa a **0,98× no
MAE** carregando `k_ratchet = 0,003` per-espécime — e a procedência dele cita
*"vidas … a **312-315 kN nominais**"*, exatamente os F₀ que o D-X mediu como
5–6,6 % baixos. Hipótese: a exceção é curativo de erro de base ⇒ removível.

**Falsificada, e o controle é que mata** (`karlsen_run2p2_sonda_resultado.md`).
Previsto viés **−5 a −6 %**; medido **+15,5 %** sem o parâmetro — sinal trocado.
E a `run7p1`, cuja base está **certa** (+0,4 %), precisa **mais** dele
(**+25,1 %**). O défice é real, compartilhado, e o modelo **sub-afrouxa** nos
HV.

⚠️ Não falsifica que a base da `run2p2` esteja errada — são claims
independentes; o +6,6 % foi medido contra o impresso e segue de pé.

**Subproduto que reenquadra a dívida:** o défice ordena-se
`run7p1` 25,1 % > `run2p2` 15,5 %, e os valores adotados seguem a mesma ordem
(0,005 > 0,003) — sendo a `run2p2` justamente a de dado artificialmente alto.
**Predição registrada:** corrigida a base, o `k_ratchet` dela **sobe rumo a
0,005**; se convergir, os dois compartilham UM valor e a exceção per-espécime
vira exceção **de classe**, com um parâmetro a menos. Estimativa de 1ª ordem do
risco: viés hoje −0,0194 → ≈ **+0,011** com o dado corrigido, **menor em
módulo** ⇒ prognóstico **neutro-a-favorável**, não o −1 que eu havia assumido.

Custo: extração de pixel da Fig. 10 (a correção não é reescala — a âncora está
no ciclo ~26 e a forma inicial muda). Prereg próprio, re-fit no mesmo passo, a
parcimônia como gate.

## Tick M4 — 2026-08-06 (noite) · **D-Y ADOTADO** · gates 5/5 · censo 139

`karlsen_run2p2_resultado.md` · fingerprint **`5916d8be0510` → `1c118e405a42`**.

A predição de parcimônia do M3 **confirmou-se**. Corrigida a base
(312 → 333 kN, CSV re-baseada em 332,7), o `k_ratchet` ótimo migra de **0,003**
— onde subir piorava monotonicamente — para **0,0045–0,0050** em **todas** as
quatro bases testadas. Adotado **0,005**, o valor **já adotado da `run7p1`**,
e não o mínimo de MAE (0,0045): a regra do D-I proíbe escolher pelo MAE,
escolhe-se o que **compartilha**.

```
0,0488 / 0,0922 / 0,0548  ->  0,0315 / 0,0583 / 0,0364
previsto                      0,0319 / 0,0569 / 0,0364   (desvio max 0,0014)
```

**O ganho é PARCIMÔNIA, não censo — e isso se diz com número.** O censo fica em
**139/205**: a curva já passava, a 0,98× no MAE. O que entra é **um parâmetro a
menos** (as duas entradas per-espécime do KARLSEN passam a carregar o mesmo
valor ⇒ exceção per-espécime vira exceção **de classe**) e uma curva que passava
pelo motivo errado passando pelo motivo certo.

**Par declarado, porque a correção o exigia:** a `run2p2` era metade do **único**
par que sustentava `limite_sres(KARLSEN)`; as duas casavam pela chave mecânica
**porque ambas carregavam o F₀ NOMINAL de 312 kN**. Sem declarar, o limite cairia
a 0,025 e **quatro** curvas reprovariam por σ — perda causada pela correção, não
medida. Piso resultante **0,0903** (+7 %): o par verdadeiro é um pouco mais
disperso, como se espera de espécimes cujo aperto de fato diferiu.

### ⚠️ Dois erros MEUS no caminho, ambos de instrumento

**1. Censo 142 onde o report diz 139.** Rodei a mesma função sobre o store
**antigo** e deu 142 também ⇒ não era o D-Y. Eu havia reimplementado o censo
lendo `resid_std` **cru**, quando o report usa **`rh.sres_para_censo`**, que
aplica a regra `n<6` de 2026-08-01. São 3 curvas, e 139 + 3 = 142. **Regra que
fica: o censo se pergunta ao helper, igual ao limite** — a armadilha do
`limite_sres` tem uma irmã um nível adiante.

**2. Executor em primeiro plano estourou 10 min a meio da re-simulação.** Sem
dano (nada gravado, conferido), mas a lição do D-Q ganha forma nova:
**executor de adoção também não vai em primeiro plano**. O
`karlsen_run2p2_grava.py` nasceu disso — re-simula só as 11 do KARLSEN e
**re-carimba as 199** apoiado na prova do G5, em vez de repetir 50 min de
medição já feita.

**Fig. 10 sem dívida remanescente:** o D-X mediu as quatro bases e só a `r1.2` e
a `r2.2` estavam fora de 1 %; ambas corrigidas.

### Subproduto D-W para fila separada (rigor contra nós)

A mesma assinatura mid-tail-alto contra a Tabela 8 aparece nas irmãs:
`amp1p0` (+0,044 em c10; fora do censo, metade do par do piso de
digitalização) e `amp2p0` (+0,079 em c10; **no tripé hoje — re-digitalizar
pode tirá-la**). Prereg próprio pendente.

## Tick M5 — 2026-08-07 (madrugada) · três decisões abertas, **zero adoções** — e seis erratas minhas

Onze commits depois do D-Y, nenhum tocou o store. O censo fica em **139/205** e
o fingerprint em `1c118e405a42`. O que a madrugada produziu foi **medição que
converge em decisão do professor** — P-7, P-8 e P-9 — e uma quantidade
incomum de correções do meu próprio trabalho. Registro as duas coisas.

### O bloco LU_2024 → **P-8**

1. **As duas figuras reproduzem as tabelas impressas**: Fig. 18a × Tabela 8 a
   **±0,002**, Fig. 20a × Tabela 9 a **±0,007**, cada uma com controle próprio.
   ⇒ desvio de CSV é **da CSV**.
2. **Sete CSVs desviam**, pior `fig18_amp2p0` **+0,0792** no c10.
3. **O "piso de digitalização" da fonte (0,0127) mede CONCORDÂNCIA, não
   acurácia**: `fig18_amp1p0` e `fig20_T22Nm` são o **mesmo ensaio** em duas
   figuras (âncoras extraídas: 11 554 N × 11 610 N) e **erram juntas**. É a
   chave cega um nível acima — ali pareava coisas distintas, aqui pareia
   **iguais demais**.
4. Premeasure: **o modelo PIORA em 5 de 7** com o dado corrigido (`T10Nm`
   res.máx 0,331 → **0,802**), **saldo de censo +0**, e `limite_sres(LU)`
   **afrouxa 32 %**. A campanha tem precedente de aceitar perda por correção;
   **não tem** de afrouxar barra como efeito colateral ⇒ decisão do professor.

### As duas auditorias, e o esgotamento do método

* **Varredura dos 11 PDFs**: **só o LU** tem tabela numérica de retenção. O
  padrão "auditar CSV contra tabela" não tem segunda aplicação.
* **YANG_2019 contra a lei D-N impressa** (`d^m·N = C`, Tabela 5): a
  `amp0p4_5Hz` passa (**1,05 / 0,90**). **Nenhum erro de digitalização.**
  Ao contrário de KARLSEN e LU, o problema desta fonte **não é o dado**.

### `s1_amp_gate` no YANG_2019 → **NÃO ADOTADO** → **P-9**

Autorização era *"adote se os gates passarem"*. Não passaram, e a reprovação é
o resultado: **autoridade 100 %** (toda a perda até 90 % é Emb+Creep), mas
**trade-off estrutural** — forte ⇒ viola +0,010, fraca ⇒ inerte, **0 curvas
entram** em 15 células. O motivo: a `amp0p6_10Hz` melhora nas três pernas e a
`amp0p6_5Hz` — **mesma amplitude** — piora, e o gate não vê frequência.

⇒ forma faltante nomeada com precisão: **frequência nos relógios de Estágio I**
(`s1_amp_gate` tem autoridade sem frequência; `dmg_dwell_exp` tem frequência
com teto). Alcance medido: **6 curvas, 3 fontes**.

### ⚠️ SEIS erratas minhas, todas pegas por controle ou por medição

Registro-as juntas porque o padrão importa mais que cada uma:

| o que eu afirmei | o que a medição disse |
|---|---|
| erro de c1 na Fig. 18 era "artefato do penhasco" | **off-by-one em x** — o JSON do D-W já dizia `ciclo = x−1` |
| erros das CSVs do LU: ~+0,03 e ~+0,06 | **maiores** (+0,044 e +0,079); a de 0,5 mm não era ruído |
| a subida do piso do LU era "artefato de correção pela metade" | **medição real** — a `fig14` está certa (RMS 0,005) |
| retratação da `run14p2`: "só o σ caiu" | **inverteu** — σ deixou de violar, MAE e res.máx ficaram descobertos |
| razão de frequência do Yang = "2,24×" | é a razão **num nível só** (2,24 / 1,68 / 1,26) — o dado não é 1/f puro |
| as 10 ESPELHADO são uma classe | **1 de 3 controles tem a mesma assinatura** ⇒ eixos independentes |

**O que fez as seis aparecerem:** em todos os casos havia um **controle
declarado antes da medição** (a curva de 1,5 mm do D-W; a `fig14`; os pisos por
perna; três curvas do grupo oposto) ou uma **verificação de instrumento**
(RMS contra a figura, razão contra F₀ do registry). Nenhuma delas veio de
reler a prosa.

### Duas armadilhas de instrumento que ganharam regra

* **Divisor do passo é sempre "ajuste perfeito", e sempre errado.** Varrer
  candidatos de retícula em ordem **crescente** escolhe 71 px onde o passo é
  142, e aí *todos* os pontos — inclusive os espúrios — caem na grade.
  Varredura tem de ser **do maior para o menor**.
* **Legenda: 3ª ocorrência** (KARLSEN, Fig. 18, Fig. 14). Na Fig. 14 o
  `argmax` caiu no swatch — "pico" com valor **constante por 111 s**, o que
  curva de relaxação não faz. **A azul escapou por acaso**, porque o pico real
  dela era mais alto: o mesmo defeito reprovou uma série e passou na outra.

### Verificação do meu próprio trabalho: INCONCLUSIVA, declarada

Adotei D-X/D-Y a partir de um PNG de 1252×790 havendo **PDF no repo** (~8× a
resolução). Re-medi: um controle confirma (`run6.2` 1,011), o outro falha
(`run7.1` 1,070). A assinatura acusa **meu instrumento novo** — `run1.2` e
`run7.1` dão 333,7 e 333,9, o mesmo valor, porque as duas azuis diferem só no
canal G e se sobrepõem no feixe. **Resolução maior não resolve ambiguidade de
cor.** As adoções ficam de pé pelas evidências originais (duas extrações
independentes, controles a +0,4 %/−0,2 %, predição cravada a 0,0014).
**Lição: procurar o PDF ANTES de digitalizar** — o inventário tem 11 papers e
eu não o consultei.

## Tick M6 — 2026-08-07 (manhã) · **D-Z: a fila fecha em ZERO, por mérito**

`docs/superpowers/specs/2026-08-07-karlsen-run14p2-classe-prereg.md` · gates
**4/4** · fingerprint `1c118e405a42` → **`d9a680664797`** · censo
**139 → 140/205**.

### O passo

A `run14p2` era **a única** curva da fila form-limited. Anatomia: resíduo
crescendo **monotonicamente** de +0,0000 (ciclo 0) a **+0,2363** (ciclo 269),
viés +0,0879, **|viés|/MAE = 0,98** — deriva de **nível** quase pura, não
dispersão. Até o ciclo 99 o erro era ≤0,021. Decomposição no fim:
**rotacional 78 %** · wear 12 % · embedding 9 % · creep 1 % ⇒ o modelo
afrouxava **devagar demais** exatamente no canal que o `k_ratchet` governa.

```
0,0898 / 0,2363 / 0,0854   ->   0,0455 / 0,0706 / 0,0218
previsto                        0,0455 / 0,0706 / 0,0218   (desvio 0,0000)
```

**ZERO número novo.** Adotado **0,005** — o valor já adotado na `run7p1` e
(pós-D-Y) na `run2p2`. Três espécimes M30 HV passam a compartilhar um único
valor. O ótimo de MAE era 0,004 (daria 0,0185/0,0301/0,0135) e foi **recusado**
pela regra do D-I: escolher pelo MAE é o que o gate proíbe.

Ressalva declarada: a `run14p2` é HV **torqueada**, as outras duas
**tensionadas**. A transferência se apoia no **controle físico** — as
`vibralock` não têm o parâmetro e **passam** sem ele, porque a porca wedge-cam
suprime a rotação ⇒ a classe é da **superfície HV**, não do método de aperto.

### Por que o *modo* de fechar importa mais que o fato

**Duas horas antes** eu tinha um caminho para fechar esta mesma fila
**declarando** a curva *data-limited por resolução*: o critério assinado a
qualificava **pela letra** (mediana |Δdado| 0,1216 ≥ 0,10). O controle da
própria fonte refutou — quatro irmãs com amostragem **mais grossa** passam com
erro em 0,33–0,57 do passo, enquanto ela erra **1,94×** o passo (**P-10**).

A fila fechou pelo caminho **certo**, não pelo disponível. E a retratação F7 da
`run14p2` **fica**: ela é registro correto — a exceção *era* improcedente, e a
curva passa agora **por mérito**, não por perdão.

### KARLSEN fecha **11/11** — primeira vez

Saiu de 6/11 na nota antiga por quatro passos: **D-X** (base da `run1p2`),
**D-Y** (base da `run2p2` + `k_ratchet` convergido), **bloqueio da 7ª chave
cega** e **D-Z**. Fontes a 100 %: **11 → 12** de 27.

### ⚠️ Zero na fila NÃO encerra a campanha

As 65 fora estão **inteiramente contabilizadas** — e é isso que o zero
significa, nada mais:

| classe | n |
|---|---:|
| exceção assinada | 23 |
| declarada | 14 |
| `classe_parada` | **23** |
| indecidível (falta réplica) | 5 |
| **form-limited** | **0** |

Das 23 em `classe_parada`, **10 têm defeito OPOSTO ao da classe** (**P-7**), e
as 5 indecidíveis estão travadas em dado que não existe (4 do ROUSSEAU, sua
P-5). **Cinco itens na mesa do professor:** P-7 · P-8 · P-9 · P-10 ·
`bauer2024_M12_fig8_test1`.

### Auditoria das 4 camadas de estatuto, feita nesta mesma passada

| camada | n | premissa se sustenta? |
|---|---:|---|
| exceções **F7** | 7 | **7/7** |
| exceções **F5** (*scatter*) | 9 | **8/9** — `M12_fig8_test1` 13,6 % acima |
| declarações — colapso | 3 | **3/3** |
| declarações — `n<6` | 3 | **3/3** |
| declarações — resolução | 6 | **3/6** ⇒ **P-10** |

⚠️ **Quatro vezes** nesta madrugada eu testei um estatuto contra o critério
**errado** (média-da-fonte em vez de piso-por-condição; F7 aplicado a F5;
primeiro-critério-que-casa; censo reimplementado em vez de perguntado ao
helper). Na quinta — o sync dos 8 números do D-Z — **chamei o `_censo` do
próprio teste** antes de errar. A regra que sobra: **leia a prova gravada, e
pergunte ao helper.**

## Tick M7 — 2026-08-07 · **P-10 e P-11 ASSINADAS** · quatro retratações, custo −4

Decisão do professor em sessão: *"assine a P-10 e a P-11, e execute as
retratações"*. Executadas. Censo estrito **inalterado em 140/205**;
*resolvido-ou-declarado* **177 → 173**.

### As duas guardas que faltavam, e por que são a mesma guarda

| critério | media | tinha limite superior? |
|---|---|---|
| declaração por **resolução** | passo do DADO | **não** ⇒ P-10 |
| exceção F5 de ***scatter*** | dispersão da FAMÍLIA | **não** ⇒ P-11 |
| F7 (piso por perna) | erro **vs** piso | sim — 5 retratações antes |
| declaração por colapso | posição do res.máx **vs** penhasco | sim |
| declaração por `n<6` | exige mae/mx passando | sim |

**Critério que só olha o dado não pode limitar o erro do modelo.** Os dois sem
guarda eram exatamente os dois que a auditoria apontou — não por azar, por
construção. As guardas assinadas:

* **P-10**: mediana |Δdado| ≥ META_MAX **E** `res.máx ≤ mediana |Δdado|`;
* **P-11**: unalcançabilidade da família **E** erro ≤ desvio-à-mediana.

### Executado, curva a curva — e duas NÃO foram retratadas

Cada declaração foi testada contra **o critério que ela própria cita**, e uma
declaração vale se **qualquer** critério assinado a cobre:

| curva | citava | veredicto |
|---|---|---|
| `Yang2023 0,30` | resolução | **RETRATADA** — mx/passo 1,22, sem alternativa |
| `Yang2023 0,35` | resolução | **RETRATADA** — mx/passo **4,00**, o pior caso |
| `Yang2023 0,50` | `n<6` | **RETRATADA** — MAE 4,77×; resolução 1,82 e colapso não se aplica |
| `Yang2023 0,55` | `n<6` | **RE-MOTIVADA** → colapso (res.máx a **0 índices** do penhasco) |
| `Yang2023 0,65` | `n<6` | **RE-MOTIVADA** → resolução com a guarda (mx/passo **0,76**) |
| `bauer_M12_fig8_test1` | F5 *scatter* | **RETRATADA** — res.máx 0,3965 > 0,349 (1,14×) |

⚠️ **Três citavam `n<6` e o MAE delas erra 1,6× a 4,8×** — o que aquele critério
não pode desculpar, porque MAE de 5 pontos é perfeitamente julgável (a própria
assinatura de 2026-08-01 diz *"as 2 pernas julgáveis passam"*). Mas **duas têm
cobertura alternativa válida**, e retratá-las seria tão errado quanto mantê-las
sob o critério errado. Motivo corrigido em código, declaração preservada.

### Como o achado nasceu — e ele nasceu contra mim

A P-10 veio de uma tentativa **minha** de fechar a fila form-limited em zero
declarando a `karlsen_run14p2` por resolução. Ela qualificava **pela letra**
(mediana 0,1216 ≥ 0,10). O controle da própria fonte refutou: quatro irmãs com
amostragem **mais grossa** passam com erro em 0,33–0,57 do passo, enquanto ela
erra **1,94×**.

Recusei o atalho — e o mesmo teste voltou contra **quatro** números que já
estavam publicados **a nosso favor**. A fila fechou depois, pelo D-Z, **por
mérito e com zero número novo**.

### Placar honesto após as assinaturas

| leitura | antes | depois |
|---|---:|---:|
| tripé estrito | 140 | **140** |
| exceções ativas | 23 | **22** |
| declaradas | 14 | **11** |
| resolvido-ou-declarado | 177 | **173** |

Quatro curvas voltaram à fila sem estatuto. **Isso é o preço de a régua medir o
que diz medir**, e foi pago com o número à vista.

## Tick M8 — 2026-08-07 · **P-12 ASSINADA** · a curva volta, pelo critério certo

A `bauer2024_M12_fig8_test1` chegou vinda da camada de **exceção**: a P-11
retirou a F5 de *scatter* dela (res.máx 0,3965 > desvio-à-mediana 0,349, 1,14×).
Correto. Mas o critério de **colapso** a cobre, e pelo **mesmo teste** que
validou as outras três:

| curva | salto | @índice | res.máx @índice | distância |
|---|---:|---:|---:|---:|
| `bauer_M12_fig8_test1` | 0,264 | 23 | 24 | **1** |
| `Yang2023 0,45` | 0,260 | 3 | 4 | 1 |
| `yang2019_amp0p6_5Hz` | 0,375 | 11 | 12 | 1 |
| **`Yang2023 0,50`** | 0,250 | 0 | 3 | **3** ⇒ falha |

⇒ declarada por **colapso**. E a `0,50`, que caiu na **mesma** retratação,
**falha** o teste e segue sem estatuto — é isso que mostra que o teste
**discrimina** em vez de acomodar.

`declarado_total` **173 → 174**; censo estrito **inalterado em 140**.

### O princípio que fechou o ciclo das quatro assinaturas

*Uma curva tem estatuto se **qualquer** critério assinado a cobre — e o critério
tem de ser testado como está escrito, não como conviria.*

Aplicado seis vezes nesta passada, em três direções:

| curva | movimento |
|---|---|
| `Yang2023 0,30` · `0,35` · `0,50` | **perderam** estatuto (nenhum critério cobre) |
| `Yang2023 0,55` · `0,65` | **mantiveram**, motivo corrigido |
| `bauer_M12_fig8_test1` | **trocou de camada** (exceção → declaração) |

Três resultados diferentes do mesmo princípio, no mesmo dia. Nenhum deles é o
que eu esperava quando comecei a auditoria: eu fui medir esperando confirmar que
as camadas estavam sãs, achei duas lacunas, e ao consertá-las descobri que uma
das curvas que eu havia acusado tinha razão de ficar.

### Placar final da sequência de assinaturas

| leitura | antes da auditoria | agora |
|---|---:|---:|
| tripé estrito | 140 | **140** |
| exceções ativas | 23 | **22** |
| declaradas | 14 | **12** |
| resolvido-ou-declarado | 177 | **174** |
| fila form-limited | 1 | **0** |

O tripé **não se moveu** em nenhuma das quatro assinaturas — elas mexeram só em
como o que está **fora** é justificado. Isso é o que se espera de emenda de
régua: ela não conserta modelo, ela conserta o que dizemos sobre o modelo.
