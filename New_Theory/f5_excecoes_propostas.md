# Lista de exceções — PARA ASSINATURA (F5 / passo S4)

> **Status: ✅ ASSINADO pelo professor em 2026-07-28** (sessão guiada, 8/8
> decisões — todas na recomendação). Leitura da meta pós-assinatura:
> **146/202 no tripé + 17 exceções assinadas + 39 form-limited na fila =
> 163/202 resolvidos (81 %)**. Exceção não fecha curva: retira o caso da meta.
>
> Revisão **2026-07-27**, reescrita sobre o **censo certificado do S3** — todos os
> números abaixo foram lidos do baseline `New_Theory/l1l7_baseline.json`
> (fingerprint `4f5bedfbace4`, gerado 2026-07-27T18:33Z), não copiados da versão
> anterior. Onde a lista de 22/07 estava errada, a correção está marcada
> **[CORREÇÃO]**.

---

## ⓪ Censo CERTIFICADO (S3) — e por que ele vale mais que o de 22/07

| | valor |
|---|---:|
| casos comparáveis | **202** |
| **no tripé** (MAE ≤ 0,10 **E** res.máx ≤ 0,10) | **147 (73%)** |
| fora do tripé | **55** |
| mediana MAE / média | **0,03155 / 0,04464** |
| MAE > 0,10 | 21 |
| res.máx > 0,10 | 55 |
| fontes que fecham 100% | **12 de 28** |

**O número é o mesmo de 22/07 — o que mudou é o estatuto dele.** O censo antigo
vinha de um store remendado por 12 gerações de configuração; o do S3 vem da
**re-simulação completa dos 202 casos sob a configuração final**, com fingerprint
único em 203/203 registros e zero erros. O diff contra o store anterior deu
**exatamente 1 caso** (o conserto do S1) ⇒ ficou provado que o mosaico era inócuo.
É um resultado reproduzido, não uma afirmação herdada.

**Achado que reordena a prioridade — `MAE ⊆ maxerr`:**

| violam | quantos |
|---|---:|
| só o MAE | **0** |
| só o res.máx (pico) | 34 |
| os dois | 21 |

Nenhuma curva viola apenas o MAE. **O gargalo é o resíduo máximo**, e qualquer
esforço medido em MAE médio não move a meta. Consequência direta para a
assinatura: **afrouxar o critério para "MAE-only" não traria nenhuma curva para
dentro do tripé** — seria mudança de contabilidade, não progresso.

---

## ① O que esta assinatura decide (três coisas distintas)

1. **Ratificar os trims já aplicados na métrica** (§B). Eles não são exceções —
   são recortes de janela que fazem as curvas **passarem**. Negar um trim devolve
   o caso à lista de violadores.
2. **Aceitar ou recusar cada exceção**, item a item (§A, §C, §D). São **15** dos
   55 violadores, todos com prova quantitativa.
3. **Reconhecer que os 39 restantes são form-limited** (§E) — nenhuma constante os
   fecha. Eles ficam como fila aberta, dependente das decisões de forma.

Aritmética: 55 fora = **16 exceções-candidatas** + **39 form-limited**.
*(Revisada na tarde de 2026-07-27: era 15 + 40; o `eccles2010_fig8a` migrou do
bloco form-limited para a família §D quando o dado cru mostrou que ele perde 99%
da pré-carga — ver §D.)*

---

## ② A. Scatter de réplicas — a dispersão do próprio ensaio excede a meta

*7 curvas.* O argumento: quando réplicas nominalmente idênticas divergem mais que
a meta, **nenhum modelo determinístico único** pode ficar dentro dela. A prova é o
**desvio máximo à mediana do ensemble** — o res.máx que a curva ideal (a própria
mediana dos dados) já teria contra alguma réplica.

**BAUER_2024 fig6 ×4** (M8 zinc-flake, 6 réplicas nominais):

| caso | MAE | res.máx |
|---|---:|---:|
| `bauer2024_M8_fig6_rep4` | 0,0783 | **0,1709** |
| `bauer2024_M8_fig6_rep6` | 0,0757 | **0,1300** |
| `bauer2024_M8_fig6_rep1` | 0,0431 | **0,1259** |
| `bauer2024_M8_fig6_rep5` | 0,0494 | **0,1116** |

> **Prova re-medida hoje** (6 CSVs, grade comum na sobreposição N∈[0,150]):
> spread máx entre réplicas **0,520 @N=150**; **desvio máx à mediana 0,328**.
> ⇒ a curva única ideal já teria res.máx ≈ **3,3× a meta**.
> *[CORREÇÃO de método]* a lista de 22/07 dizia spread 0,561 e desvio 0,313. O
> desvio-à-mediana (a estatística que sustenta o argumento) reproduz; o spread
> bruto depende da grade de interpolação e por isso difere. Conclusão inalterada.

**BAUER_2024 fig8 ×3** (M12):

| caso | MAE | res.máx |
|---|---:|---:|
| `bauer2024_M12_fig8_test1` | 0,0745 | **0,3965** |
| `bauer2024_M12_fig8_test2` | 0,0290 | **0,1795** |
| `bauer2024_M12_fig8_test3` | 0,0241 | **0,1198** |

> **Prova re-medida hoje** (3 CSVs, N∈[26,873]): spread máx **0,384 @N=873**;
> **desvio máx à mediana 0,349 @N=835** (reproduz exatamente o valor de 21/07).
> test2 e test3 divergem em **sentidos opostos** sob o mesmo `k` graded — ajuste
> per-teste seria overfit, já rejeitado (PR-12e). Per-espécime `tr_loose_gain` já
> adotado (PR-22); per-réplica µ reprovado por coerência (PR-12f).

**[CORREÇÃO] `liu2025_M16_fig2_single` saiu desta seção.** Ela **passa** hoje
(MAE 0,0389 / res.máx 0,0546), coberta pelo trim. A prova de scatter de vida
(44%: fratura em 10k vs viva em 14,4k na mesma amplitude) permanece válida, mas
como justificativa do **trim** (§B), não como exceção.

---

## ③ B. Trims a RATIFICAR — recortes de janela já aplicados na métrica

*Não são exceções.* São 16 curvas cuja janela foi recortada por regra registrada
(`trim_n_max`, mecanismo do commit b50550d). **Quase todas passam graças a isso** —
por isso a ratificação importa: negar um trim devolve o caso à lista.

| grupo | trims aplicados (ciclos) | resultado hoje |
|---|---|---|
| **LIU_2025 ×6** *(era ×7; trim da amp0p8 REMOVIDO 2026-07-28, rider aprovado — ela passa SEM trim, 0,0381/0,0853)* | 240k / 180k / 60k / 30k / 18k / 8k | **7/7 passam** (fonte 100% fechada) |
| **YANG_2021 ×6** | 27000 / 14000 / 11800 / 5850 / 5450 / 3150 | **4 passam**, 2 seguem violando (vão para §C) |
| **LI_2022_TRIBOINT `full`** | 330000 | **passa** — MAE 0,0317 / res.máx 0,0517 |
| **SUN_2025_CRIMP secos ×2** | 6596 / 9514 | **2/2 passam** (0,0051/0,0103 e 0,0107/0,0165) |

### O que cada trim custa (medido 2026-07-27, store `4f5bedfbace4`)

A tabela acima diz quantos **ciclos** o trim mantém. Falta o número que a
decisão precisa: quanto da **perda de pré-carga medida** ele deixa de pontuar.
Nestas curvas o colapso é rápido, então manter 73–80 % dos ciclos **não**
significa manter 73–80 % do fenômeno.

| caso | trim N | F/F₀ no corte | F/F₀ no fim | **% da perda FORA da métrica** |
|---|---:|---:|---:|---:|
| liu2025 amp0p25 | 240 000 | 0,926 | 0,675 | 77 % |
| liu2025 amp0p3 | 180 000 | 0,900 | 0,683 | 68 % |
| liu2025 amp0p4 | 60 000 | 0,853 | 0,330 | 78 % |
| liu2025 amp0p5 | 30 000 | 0,836 | 0,330 | 76 % |
| liu2025 amp0p6 | 18 000 | 0,812 | 0,330 | 72 % |
| ~~liu2025 amp0p8~~ *(trim REMOVIDO 2026-07-28 — passa sem ele)* | — | — | — | — |
| liu2025 fig2_single | 8 000 | 0,800 | 0,000 | 80 % |
| li2022ti axial_10Hz_full | 330 000 | 0,835 | 0,087 | 82 % |
| sun2025 nogrease_crimp | 9 514 | 0,877 | 0,000 | 88 % |
| sun2025 nogrease_standard | 6 596 | 0,817 | 0,000 | 82 % |
| yang2021 amp0p5mm_ax8kN | 27 000 | 0,800 | — | 80 % |
| yang2021 amp0p6mm_ax8kN_r1 | 11 800 | 0,825 | — | 83 % |
| yang2021 amp0p7mm_ax11p2kN | 14 000 | 0,794 | — | 79 % |
| yang2021 amp0p8mm_ax6kN | 5 450 | 0,662 | — | 66 % |
| yang2021 amp1p0mm_ax2kN | 3 150 | 0,626 | — | 63 % |
| yang2021 fig2_typical | 5 850 | 0,655 | — | 66 % |

**Mediana 77,5 % · média 74,5 %** (16 curvas). Ou seja: os MAEs que estas 16
curvas exibem hoje descrevem, em média, o **primeiro quarto** da perda medida.

Isso **não** é argumento automático contra a ratificação — se a cauda é de fato
outra física (fratura), pontuá-la mede o modelo errado. É argumento para que o
número saia sempre acompanhado do recorte. Desde 2026-07-27 cada report por
caso declara o recorte e este percentual na própria página.

> **[CORREÇÃO 2026-07-28 — a justificativa do trim mudou, a ratificação FICA MAIS
> FORTE.]** Até ontem esta seção dizia que o trim era *"provisório enquanto a
> forma não existir"*, e que o pré-registro
> `specs/2026-07-27-liu2025-fracture-ramp-prereg.md` propunha a forma que, *"se
> passar, dispensa os 7 trims da LIU_2025"*. **Medido antes de assinar o prereg**
> (`New_Theory/liu2025_ramp_premeasure.md`, mesmo fingerprint `4f5bedfbace4`):
>
> - **a forma FUNCIONA** — no `fig2_single`, **sem trim nenhum**, a rampa entrega
>   **0,039 / 0,062**, praticamente o que hoje só se obtém *cortando* 20 % da
>   curva (0,0389 / 0,0546) — e é **discriminante** (sem o candidato: 0,093/0,481);
> - **mas ela NÃO dispensa os trims — ela custa 6 dos 7 passes.** Ligar a rampa e
>   remover os trims leva a `LIU_2025` de **7/7 para 1/7**;
> - **e o motivo não é o modelo:** em **4 das 6** que caem, o `res.máx` é
>   *exatamente o último valor do dado* — 0,330 é a **borda inferior do gráfico**
>   do artigo (20 kN) e 0,683 é o **último ponto legível** do digitalizador. O
>   modelo vai a zero na fratura que o paper declara; o dado digitalizado **acaba
>   antes**, e a métrica pontua a moldura da figura.
>
> ⇒ O trim é **provisório enquanto o DADO não existir**, não enquanto a forma não
> existir. A ação que o destrava não é mais trabalho de forma: é
> **re-digitalizar as caudas com passo fino** abaixo de F/F₀ = 0,33 (inset da
> Fig. 3 + Fig. 2), ou **pedir aos autores as séries brutas de 200 Hz** do
> DH5902N. Nenhuma forma pode "acertar" um ponto que não foi medido.

Justificativa por grupo:
- **LIU_2025** — estágio de fratura por fadiga; o paper declara todos os ensaios
  levados até a fratura, e as curvas 0,4–0,8 mm saem do plot em F/F₀ = 0,33
  (boundary do gráfico). Regra: taxa local > 3× a mediana do Estágio II, contígua
  até o fim.
  > **[3ª CORREÇÃO 2026-07-28, pós-adoção E2 — a justificativa mudou DE NOVO,
  > e a ratificação segue de pé em 6 das 7.]** "Fadiga in-model é inviável"
  > ficou FALSA: ela está **ADOTADA** (E2, §4.53 — relógio LIDO por curva,
  > N_f da mesma coluna da matriz que dá estes trims). Medido sob o canônico
  > pós-E2, SEM os trims: 6 curvas falham (MAE 0,08–0,19, res.máx 0,25–0,64)
  > por **duas** causas — o dado truncado na moldura (finais 0,33/0,68 contra
  > o modelo indo à fratura declarada) e a **não-linearidade do relógio
  > Miner+Goodman** (o Goodman vivo front-loada o dano; ancorar o FIM não pina
  > o INÍCIO da rampa). **Exceção medida: `amp0p8` PASSA sem trim
  > (0,0381/0,0853, MAE até melhor que o pós-trim 0,0487)** — o trim dela não
  > faz mais trabalho e **a remoção está APROVADA pelo professor (2026-07-28),
  > como rider obrigatório do próximo re-stamp** (receita executável na fila —
  > `DECISOES_PENDENTES.md`; remover trim = mudança de config ⇒ fingerprint
  > novo ⇒ re-sim; não vale sozinho). Ao executar, esta seção passa a contar
  > **15 trims (LIU_2025 ×6)**. Nota: com o relógio Miner nativo, o `fig2` NÃO passa sem trim
  > (0,0795/0,2548) — a leitura anterior (0,038 full) era da sonda com relógio
  > lido linear.
- **YANG_2021** — cauda terminal no N2 (tangente de 45° do próprio paper).
- **LI_2022_TRIBOINT** — cauda de fratura, mesma regra > 3× mediana.
- **SUN_2025_CRIMP secos** — Estágio III é trinca de cisalhamento do parafuso
  (F → 0), fora do modelo (PR-32).

> **[CORREÇÃO IMPORTANTE]** A lista de 22/07 dizia que o trim do
> `li2022ti_axial_10Hz_full` estava **"pendente de aplicar"** e que o caso violava
> com res.máx 0,239. Conferido hoje no cfg canônico: o trim **está aplicado**
> (`LI_2022_TRIBOINT → trim_n_max = {"full": 330000}`) e o caso **passa**
> (0,0317 / 0,0517). O item pendente da F3 foi executado; a fila é que ficou velha.

---

## ④ C. Forma faltante, com a melhoria máxima in-engine já aplicada

*5 curvas.* Já receberam tudo que o modelo atual permite; o resíduo é físico.

| caso | MAE | res.máx | por que fica |
|---|---:|---:|---|
| `jcsr2023_plain_outdoor` | 0,0621 | **0,1313** | cliff de corrosão + **rebound não-monotônico**: F₀ **se recupera** de verdade (Tabela 2 do paper) e **nenhum mecanismo do engine recupera pré-carga** |
| `jcsr2023_stainless_seawater` | 0,0619 | **0,1237** | idem (galvânica) |
| `yang2021_fig2_typical` | 0,0992 | **0,1625** | canal estrutural ξ-dependente **confundido**: o dado n=5 varia F_ax e δ **juntos** (PR-23 recusada por isso) |
| `yang2021_amp0p8mm_ax6kN` | 0,0938 | **0,1422** | idem |
| `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | 0,0729 | **0,1339** | salto de looseness ∝ A_F^1,5–1,6 → ^3,2 em 0,4 mm = **trinca de fadiga**, atribuição explícita do paper (§3.1.2) |

> **NOTA HONESTA sobre o liu2020** (a assinatura precisa saber): a regra automática
> de changepoint por taxa (> 3× mediana do Estágio II) **não achou o corte** nesta
> curva — 0 pontos cortados. A prova desta exceção é a **atribuição do paper**, não
> a regra. Se o critério for "só exceção com regra automática", este item cai.

Ambos os pares (JCSR e YANG_2021) têm alternativa: aceitar como exceção **ou**
mandar para forma nova futura (itens 2 e da fila em `DECISOES_PENDENTES.md`).

---

## ⑤ D. **NOVA (2026-07-27)** — família de sobreposição axial do Eccles

*3 violadores + 1 curva que passa por artefato.* Item novo, gerado pelo
**G-B1 FAIL** da Trilha B (prereg `docs/superpowers/specs/2026-07-27-eccles-g2-prereg.md`).

**A família — CORRIGIDA na tarde de 2026-07-27: são CINCO, e o critério não é
"axial".** A primeira revisão deu 4 curvas unidas por "a força axial excede o
torque de prevalência". Medindo o **dado cru** das 10 curvas do Eccles, o
critério verdadeiro é outro: **a junta perde essencialmente tudo** (mínimo do
dado < 0,05) e a métrica só enxerga o trecho acima do `FLOOR_TRIM`.

| curva | axial | mín. do dado CRU | cortados | MAE | res.máx | estado |
|---|---|---:|---:|---:|---:|---|
| `eccles2010_fig6_annotated_4kN_axial` | 4,0 kN | 0,000 | 4/29 | 0,1457 | **0,4668** | viola |
| `eccles2010_fig8d_axial_3p5kN_intermittent` | 3,5 kN | 0,000 | 7/37 | 0,1335 | **0,2523** | viola |
| `eccles2010_fig8b_axial_0p7kN_intermittent` | 0,7 kN | 0,000 | **27/35** | 0,0438 | **0,1296** | viola |
| **`eccles2010_fig8a_no_axial_baseline1`** | **NENHUM** | **0,012** | **14/24** | 0,0436 | **0,1223** | viola — **membro novo** |
| `eccles2010_fig7d_axial_3p1kN_constant` | 3,1 kN | 0,000 | 4/26 | 0,0668 | 0,0891 | **passa — por artefato** |

> **O `fig8a` derruba a explicação "sobreposição axial".** Ele **não tem carga
> axial nenhuma** e mesmo assim vai a 0,012. Pela nota de aparato, os 29 ensaios
> estão em **7 grupos de porca**, cada um com seu próprio baseline sem-axial: o
> `fig8a` e o `fig8c` são baselines de **porcas diferentes** e terminam em
> **0,012 contra 0,149** — variação de torque de prevalência **por espécime**, que
> é a própria tese do artigo. A família se une por *"a porca perde tudo"*; a carga
> axial é **uma** das causas (4 de 5), não a definição.
>
> **E o `fig8a` mostra o custo da convenção pelo lado oposto:** o modelo arresta
> em 0,059 — **mais perto do 0,012 real** do que os 0,129 que o platô truncado
> sugere — e ainda assim leva res.máx 0,122, por ser comparado com uma curva que
> "termina" em 0,102. O modelo mais certo é o mais punido.

**Adoção RECUSADA por física — registrada porque passou em todos os gates.**
Testei ler o piso do `fig8a` pelo platô final (`arrest_floor_from_curve`,
procedência `data_end_plateau`, idioma "ler em vez de fitar"): daria
`floor = 0,129`, e o resultado **passava tudo** — res.máx **0,1223 → 0,0465**,
entrada no tripé, **zero** casos afetados fora dele (a chave `ECCLES_2010_fig8a`
cobre só ele), mediana da fonte 0,1057 → 0,0828. **Recusei assim mesmo:** o dado
cru cai 0,395 → 0,299 → 0,224 → 0,156 → 0,102 nos últimos pontos visíveis, sem
platô algum; o "piso 0,129" é a **borda do trim**. Adotar seria travar o modelo
em 0,129 numa junta que perde 99% da pré-carga — comprar métrica com física. É a
mesma patologia da Prova 2 abaixo, vista do lado da tentação.

**Prova 1 — a receita existente piora, e a falha estava prevista.** Aplicar o
PR-31 a `fig6`/`fig8d` (grupo-de-porca lido da nota de aparato, `floor = 0` pelo
critério de destacamento do próprio paper) deu:

| alvo | MAE | res.máx |
|---|---|---|
| `fig6` | 0,146 → **0,421** | 0,467 → **1,028** |
| `fig8d` | 0,134 → **0,239** | 0,252 → **0,400** |

Os 8 casos já tratados saíram **bit-idênticos** (isolamento limpo, sandbox
`BAS_ADOPTED_CONFIGS`, canônico intocado). A nota de aparato já dizia, em V2
mapping: *"No existing V2 mechanism represents the combined axial+transverse
scenario"*, nomeando 7(d)/8(b)/8(d) como o falsificador-alvo. Estas curvas **não
ficaram de fora do PR-31 por esquecimento** — é a família em que uma condição de
contorno axial **externa** sobrepõe o piso de arresto, conceito que o engine não tem.

**Prova 2 — o `FLOOR_TRIM` apaga o resultado central do paper.** A convenção da
campanha descarta da métrica todo ponto com `ratio < 0,10`. Medido no CSV cru:

| curva | dado cru chega a | pontos cortados | métrica enxerga o final em |
|---|---|--:|--:|
| `fig6` | 0,000 | 4 de 29 | 0,137 |
| `fig7d` | 0,000 | 4 de 26 | 0,187 |
| **`fig8b`** | 0,000 | **27 de 35 (77%)** | 0,130 |
| `fig8d` | 0,000 (vales) | 7 de 37 | 0,220 |

O paper **existe** para demonstrar que a porca chega a zero e se destaca; a
convenção remove exatamente esse trecho. Três consequências que a assinatura
precisa conhecer:

1. O `fig8b` é pontuado sobre **8 de 35 pontos** — seu MAE 0,044 não significa o
   que parece.
2. O `fig7d` **passa no tripé porque sua cauda a zero é cortada** — está entre os
   147 aprovados por artefato de convenção.
3. Um modelo fisicamente **certo** nesta família (que vá a zero) é **penalizado**,
   por ser comparado com uma curva truncada que para em 0,137.

Não é defeito de modelo, é de **convenção de medida** — e não se conserta aqui,
porque mexer no `FLOOR_TRIM` afeta os 202 casos.

**Escolha (uma das três):**

- **(i)** isentar a família do `FLOOR_TRIM` e medir contra a curva inteira. O
  modelo passa a ser avaliado pelo que de fato acerta — e o `fig7d` **perde** a
  aprovação por artefato (o tripé cairia de 147 para 146 antes de qualquer ganho).
- **(ii)** declarar a família **fora-de-modelo** e mandar as **5** para exceção
  com esta prova. ✅ **RECOMENDADO**
- **(iii)** construir o mecanismo. **Atenção: com o `fig8a` dentro, (iii) ficou
  mais caro e menos definido** — a condição de contorno axial explicaria 4 das 5,
  mas não o `fig8a`, que perde tudo **sem carga axial**. Cobrir a família inteira
  exigiria também representar torque de prevalência ~nulo por espécime.

*Racional da recomendação:* são 5 curvas de **uma** fonte; o mecanismo é
conceitualmente novo (condição de **contorno**, não mecanismo de perda), **não
transfere** para nenhuma outra fonte da biblioteca hoje, e agora nem cobre a
família toda. (iii) só se a família crescer para fora do Eccles.

*Observação:* o `fig8c` **não** é desta família — dado cru com platô real em
0,149, zero pontos cortados, piso já correto no cfg (0,152). Ele fica em §E.

---

## ⑥ E. O que NÃO é exceção — os 39 form-limited (fila aberta)

Nenhuma constante fecha estes casos: falta **forma**. Não peça assinatura aqui —
peça a decisão de forma correspondente (`New_Theory/DECISOES_PENDENTES.md`).

| forma que falta | casos | fontes |
|---|--:|---|
| **kernel de colapso desacelerante** — **e NÃO é uma forma só** (ver nota) | **25** | LU_2024 10 · CHU_2026 7 · YANG_2019 4 · ECCLES fig8c 1 · KARLSEN 1 · SUN grease_standard 1 · ZHANG_2006 1 |
| **bifurcação de limiar de amplitude** | **7** | YANG_2023_IJPEM (tri-falsificado: nenhuma constante move) |
| **escala de rigidez com espessura de membro** | **3** | ROUSSEAU_2025 (prereg escrito 2026-07-27) |
| **incubação de assentamento** | **2** | UFU_LAB |
| **tripla combinação** (porca self-locking + CFRP + R=0) | **1** | YANG_2023_AME |
| **marginal** (res.máx 0,1035 — 3,5% acima do limiar) | **1** | LIU_2016 fig7 |

Notas de honestidade sobre este bloco:

- O **kernel desacelerante** vale **25 dos 39** — mas **não é uma forma só, e a
  primeira tentativa já FALHOU** (2026-07-27). Diagnóstico
  (`New_Theory/kernel_diagnostic_2026-07-27.md`): correlacionando os perfis de
  resíduo com o nível removido, as curvas se separam em **três** problemas —
  (A) Chu2026+Yang2019+Karlsen+Zhang2006, **13 curvas com r = 0,90–1,00** entre
  4 rigs; (B) Lu2024+Sun, perfil em **tigela**, r = −0,27 com (A); (C) fig8c,
  isolada. O prereg do grupo A foi escrito e **executado no mesmo dia**:
  **G3 FAIL** (a transferência PIOROU 9%, exigia-se −30%) e **G2 FAIL** (1 de 13
  entrou, 4 pioraram). Sobra **1 tentativa**, e ela exige forma **diferente**.
  ⇒ Estas 25 curvas estão mais longe de fechar do que a fila sugeria.
- **YANG_2019** entra com 4, não 3. Duas são as `varamp`, cujos números mudaram
  no S1: o ganho antes creditado à direção small→large era **artefato do bug de
  empate de chave** — com o próprio espectro a curva vai de 0,212 para **0,194**,
  não para 0,131. Já violava e continua violando. `yang2019_M10_amp0p6_5Hz` tem
  res.máx **0,517**, o maior desta linha.
- **LIU_2016 fig7** está a 0,0035 do limiar. É a única curva que uma leitura
  single-shot plausivelmente fecharia sem forma nova.
- **ROUSSEAU** tem prereg escrito, e o seu **G0 bloqueante foi EXECUTADO** em
  2026-07-27: o roadmap item 10 e a §4.20 foram re-baselinados. O
  `k_member_shear` está **vivo** desde o PR-14 e põe o t14 em stick permanente;
  os MAE hoje são 0,058/0,064/0,044 e **caem** com a espessura. As 3 curvas que
  restam são dois problemas distintos (arresto terminal no aço; tempo de joelho
  no HDPE), não uma forma faltante. Você já pode decidir sobre texto correto.

---

## ⑦ Bloco de assinatura

| § | item | curvas | decisão |
|---|---|--:|---|
| B | ratificar os trims (LIU_2025 ×6, YANG_2021 ×6, LI_2022_TRIBOINT full, SUN secos ×2) | **15** *(era 16; amp0p8 saiu por mérito em 2026-07-28)* | **☑ RATIFICADO** (2026-07-28) |
| A | scatter de réplicas BAUER fig6 ×4 | 4 | **☑ EXCEÇÃO** (2026-07-28) |
| A | scatter de réplicas BAUER fig8 ×3 | 3 | **☑ EXCEÇÃO** (2026-07-28) |
| C | JCSR ×2 (cliff/rebound de corrosão) | 2 | **☑ EXCEÇÃO** (2026-07-28) |
| C | YANG_2021 ×2 (canal ξ confundido) | 2 | **☑ EXCEÇÃO** (2026-07-28) |
| C | liu2020 fig9 (atribuição de paper, sem regra automática) | 1 | **☑ EXCEÇÃO** (2026-07-28; nota: com a rampa no engine pode migrar p/ modelada se houver N_f com procedência) |
| D | família "a porca perde tudo" ECCLES *(era "sobreposição axial")* | **5** (4 violam + `fig7d`) | **☑ (ii) EXCEÇÃO como família** (2026-07-28; `fig7d` sai dos aprovados ⇒ 146+17) |
| E | reconhecer os 39 form-limited como fila aberta | 39 | **☑ DE ACORDO** (2026-07-28; varredura das 3 classes L25 reclassifica em seguida) |

**Sutileza de contagem na §D** (vale para (i) e para (ii) igualmente): o `fig7d`
está hoje **entre os 147 que passam**, mas por artefato do `FLOOR_TRIM`. Se a
família for tratada como unidade — isentada do trim **ou** declarada exceção —,
ele sai da coluna dos aprovados. O resultado líquido é o mesmo nas duas opções:
**146 no tripé + 17 exceções**. Só a opção (iii) (construir o mecanismo) poderia
devolvê-lo por mérito.

**Se tudo for aceito como recomendado:** nenhuma curva nova entra no tripé —
**exceção não fecha curva, ela retira o caso da meta**. A meta passa a se ler
*"146/202 no tripé + 17 exceções assinadas + 39 form-limited na fila"* =
**163/202 resolvidos (81%)**.

**O que mudou na perspectiva dos 39 restantes (tarde de 2026-07-27):** a fila
dizia que **uma** decisão de forma fecharia 26 deles. Medido, são **três**
problemas distintos, e a primeira tentativa da maior família (13 curvas)
**falhou o gate de transferência**. Os 39 estão mais longe do que pareciam — e
essa é a informação que a assinatura precisa ter: assinar as 17 exceções **não**
deixa "só um passo" para o resto.

---

**ASSINATURA (S4 CONCLUÍDO): Prof. Leonardo Rosa Ribeiro da Silva, 2026-07-28,
via sessão guiada (Claude Code — 8 decisões apresentadas com prova e
recomendação; 8/8 assinadas na recomendação). Efeito: a meta passa a ser lida
como 146/202 no tripé + 17 exceções + 39 form-limited = 163/202 resolvidos
(81 %). O passo S4 da execução mestre está FECHADO.**

---

*Procedência: censo e todos os MAE/res.máx de `New_Theory/l1l7_baseline.json`
(fingerprint `4f5bedfbace4`). Spread do Bauer re-medido em 2026-07-27 dos CSVs de
`curve_library/digitized_csv/` pelo leitor canônico `validation.inputs.load_full_curve`.
Trims conferidos em `New_Theory/adopted_configs.json`. Evidência da §D:
`docs/superpowers/specs/2026-07-27-eccles-g2-prereg.md` (seção RESULTADO).*
