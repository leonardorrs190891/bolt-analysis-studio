# Fig. 7 do Rousseau — rótulo ERRADO no paper, e um round-trip que valida nossa digitalização

**2026-08-02** · continuação do ataque às 6 curvas do ROUSSEAU (maior
bloco fora da classe parada). Só-leitura; nenhum número do modelo mudou.

## 1. A figura contradiz o próprio rótulo

A Fig. 7 diz **"% of Preload Loss"** vs rigidez da junta, com duas séries:
`Nb = 100` e `Nb = 182` ciclos. Mas a série de **182 ciclos está ABAIXO
da de 100** (62 contra 79; 43 contra 62). Mais ciclos com **menos perda**
é impossível ⇒ **o eixo é RETENÇÃO (% da pré-carga que resta), não
perda.** O paper rotulou errado.

## 2. E isso vira um round-trip que valida a nossa Fig. 4

Lendo a Fig. 7 como retenção e comparando com as curvas que já tínhamos
digitalizado da Fig. 4:

| Kj (Fig. 7) | Fig. 7: Nb=100 / 182 | nossa curva | digitalizado: N=100 / 182 |
|---|---|---|---|
| ~107 | 97 / 96 | **t14** | **97,9 / 96,2** ✅ |
| ~113 | 79 / 62 | **t12** | **80,1 / 62,3** ✅ |
| ~120 | 62 / 43 | **t10** | 67,2 / 46,3 ⚠️ |

t14 e t12 batem **dentro de 1 ponto percentual** — validação
independente da digitalização (duas figuras diferentes do mesmo paper,
extraídas em momentos diferentes, concordando).

## 3. O desvio da t10 é sinal, não ruído

A t10 é a **única** que discorda, e discorda nas duas leituras no mesmo
sentido: nossa curva retém **~5 pontos a mais** (67,2 vs 62; 46,3 vs 43).
Com t14 e t12 batendo a 1 ponto, 5 pontos na t10 é grande demais para ser
leitura de marcador.

**Consequência prática:** a `rousseau2025_hdpe_t10` é hoje uma das piores
da fonte (2,29× o limite) — e parte disso pode ser **dado**, não modelo.
Fica registrado como caveat de digitalização com número; re-digitalizar a
Fig. 4 (curva t10) é o teste que decide, e é barato com o ferramental de
hoje.

## 4. O que a figura ainda oferece (não usado)

A Fig. 7 publica a **rigidez de junta por espessura**: 107 → 113 → 120
(unidades ambíguas: o eixo diz `kN/mm` com multiplicador `×10²`, o que
daria 10,5–12,1 MN/mm — implausível para membros de HDPE; lido como
N/mm dá 10,5–12,1 kN/mm, que é a ordem certa). **A RAZÃO, que é o que
importa, é limpa: +12 % de t14 para t10.** É âncora para o
`k_member_shear`/`k_j` — utilizável assim que a unidade for resolvida, o
que exige o texto que descreve o cálculo de Kj (não localizado).

## Estado

Nada adotado; censo `129/205` intacto. Dois itens acionáveis nascem daqui:
re-digitalizar a t10 (barato, decide 1 curva) e resolver a unidade de Kj
(dá âncora de rigidez para 6 curvas).


---

## ADENDO (2026-08-02) — a t10 foi re-digitalizada, e o modelo PIOROU

Executado o prereg `2026-08-02-rousseau-t10-redigitalizacao`.

**A hipótese estava certa**: a t10 é uma banda oscilante e a versão antiga
seguia o **topo**. Traçando o **centro** (mediana do run), os dois
checkpoints independentes da Fig. 7 passam de primeira:

| | alvo (Fig. 7) | antiga | **nova** |
|---|---|---|---|
| retenção em N=100 | 62 | 67,2 ✗ | **62,8** ✅ |
| retenção em N=182 | 43 | 46,3 ✗ | **44,3** ✅ |

Controles (não tocados, extraídos pelo mesmo script): t12 77,9/61,2 e
t14 96,9/95,4 — dentro da tolerância dos alvos 80/62 e 98/96.

**E o modelo piora contra a curva verdadeira**: MAE **0,0579 → 0,1010**,
res.máx 0,153 → 0,185, σ 0,057 → 0,071. **A curva nova vale mesmo assim**
— o prereg pré-comprometeu isto por escrito ("o critério é o alvo do
paper, não o nosso ajuste").

**O que isso significa, dito sem rodeio**: parte da qualidade aparente
desta curva era **erro de digitalização a nosso favor**. O ajuste estava
sendo lisonjeado por um dado errado. Agora está pior e verdadeiro.

Caveats registrados: a curva nova cobre **0–332 de ~390 ciclos** (86 %) —
a cauda pálida (≈1200→800 N) escapa mesmo com máscara alargada e
monotonicidade folgada; e tem **165 pontos contra 16** da antiga (10× de
resolução). Censo inalterado: a t10 já estava fora (2,29× → agora 2,82×).


---

## ADENDO 2 (2026-08-02) — a unidade do Kj RESOLVIDA, e um erro de input que é quase inerte

**A unidade**: a Fig. 8 (aço) usa a MESMA escala `Kj (kN/mm) ×10²` com
valores **4000–5250**, contra **105–121** da Fig. 7 (HDPE). Só a leitura
em **N/mm** dá ordens plausíveis nas duas (HDPE ≈ 10,7–12,0 kN/mm; aço
≈ 400–525 kN/mm) — em kN/mm o aço daria 400–525 MN/mm, centenas de vezes
o razoável para um M12. ⇒ **segundo rótulo errado no mesmo paper** (o
primeiro é o "% of Preload Loss" da Fig. 7).

**O erro de input que isso expõe**: os seis casos do ROUSSEAU rodam com
**E = 210 GPa para o membro**, inclusive os de **HDPE**. Com
`kj_mode="pedersen"` isso dá:

| caso | k_j do modelo | k_j do paper | razão |
|---|---:|---:|---:|
| hdpe_t10 | 3517 kN/mm | 12,0 | **293×** |
| hdpe_t12 | 3250 | 11,3 | 288× |
| hdpe_t14 | 3047 | 10,7 | 285× |
| steel_t10 | 3517 | 525 | 6,7× |
| steel_t12 | 3250 | 460 | 7,1× |
| steel_t14 | 3047 | 400 | 7,6× |

Qualitativamente invertido no HDPE: o modelo trata o membro como **5×
mais rígido que o parafuso**; na realidade ele é **59× mais mole**.

**E o efeito medido é ~1 %.** Sonda direta no engine (não pelo runner, que
poderia filtrar o override): variar `k_j_init` de 12 a 3517 kN/mm move
F₀ de 102,3 para 101,3 N no ciclo 10 — **1 %** para um fator de **293×**.
Pelo runner, as três curvas dão **Δ = 0,0000 exato**.

**Por quê**: em modo deslocamento a perda é dirigida pelo **slip**, que
depende de `k_tr` (transversal); `k_j` (axial) entra só na repartição de
carga e em `U_internal` — segunda ordem aqui.

**Conclusão prática**: o input está errado e fica **registrado como
caveat de procedência**, mas **não justifica re-fit** do grupo HDPE — o
que seria um trabalho grande movendo 1 %. ⚠️ **Isto muda em modo AXIAL/
força**, onde `k_j` reparte a carga de primeira ordem: qualquer caso
axial deste rig teria de corrigir E do membro antes de qualquer fit.
