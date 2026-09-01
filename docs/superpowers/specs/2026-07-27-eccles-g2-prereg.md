# PRÉ-REGISTRO — Eccles 2010 (M8 prevailing-torque) e a decisão "G2"

> **IMUTÁVEL a partir de agora.** Gates escritos ANTES de qualquer fit. Máximo
> **2 preregs por candidato**; a segunda falha é falsificação documentada
> (FAIL2). Escrito 2026-07-27 sobre o store certificado no S3
> (fingerprint `4f5bedfbace4`, 203/203, zero erros).

---

## 0. Estado medido — a partida

| caso | grupo adotado | MAE | res.máx | onde | final prev./medido |
|---|---|--:|--:|--:|--:|
| fig3_typical_no_axial | `..._fig3` | 0.023 | 0.077 ✔ | 25 | 0.18 / 0.19 |
| fig7a_no_axial | `..._fig7a` | 0.027 | 0.060 ✔ | 25 | 0.20 / 0.21 |
| fig7b_axial_1p1kN | `..._fig7b` | 0.026 | 0.059 ✔ | 25 | 0.21 / 0.23 |
| fig7c_axial_2p7kN | `..._fig7c` | 0.025 | 0.061 ✔ | 100 | 0.17 / 0.18 |
| fig7d_axial_3p1kN | `..._fig7d` | 0.067 | 0.089 ✔ | 1500 | 0.12 / 0.19 |
| **fig8a_no_axial_base1** | `..._fig8a` | 0.044 | **0.122** | 175 (78% de N) | 0.06 / 0.10 |
| **fig8b_axial_0p7kN_int** | `..._fig8b` | 0.044 | **0.130** | 175 (100%) | **0.00** / 0.13 |
| **fig8c_no_axial_base2** | `..._fig8c` | 0.043 | **0.145** | 200 (12%) | 0.14 / 0.15 |
| **fig6_annotated_4kN** | **nenhum** | 0.146 | **0.467** | 250 | 0.12 / 0.14 |
| **fig8d_axial_3p5kN_int** | **nenhum** | 0.134 | **0.252** | 138 | 0.17 / 0.22 |

## 1. A decisão "G2", como está posta, está VENCIDA

`DECISOES_PENDENTES.md` item 6 (2026-07-15) oferece três caminhos: (a) aceitar
G2 = MAE-only e adotar; (b) autorizar o kernel de aproximação suave ao floor;
(c) manter baseline. **Nenhum dos três descreve o estado de hoje:**

- **(a) já aconteceu de fato.** A receita do PR-31 **está adotada** nos 8 grupos
  (`mu=0.132` EZP, `tr_loose_gain` por grupo-de-porca 1.64–2.08, `k_wear_spec`
  2.923e-15, `loose_arrest_floor` = prevailing lido por caso). O texto diz
  "maxerr<0.1 só em 4/8"; hoje são **5/8** — o fig7d saiu de 0.005 do corte para
  0.089. O baseline de 0.148 de mediana não existe mais.
  **Procedência da adoção (datada por `git log -S`):** commit `4402cd4`,
  **2026-07-15** — "PR-37' ADOTADO (instancias paralelas) + CSVs R4 de fato
  commitados; ledger #54". Isto é, a receita entrou no **mesmo dia** em que a
  entrada de decisão pendente foi escrita, carregada por um commit de OUTRO
  assunto, e a fila do professor nunca foi corrigida. **Lição de processo:**
  adoção que viaja de carona em PR alheio não fecha o item da fila — quem adota
  atualiza `DECISOES_PENDENTES.md` no mesmo commit, senão o professor decide
  sobre um mundo que não existe mais (foi o que quase aconteceu aqui).
- **(c) manter baseline** não é opção: o baseline foi substituído.
- **(a) como rota para a meta é impossível**, e isto é medida de hoje, não
  opinião: `MAE ⊆ maxerr` no conjunto inteiro — **zero curvas violam só o MAE**.
  Aceitar G2 = MAE-only **não move uma única curva** para dentro do tripé; é
  afrouxamento de contabilidade, não progresso. Se o objetivo é a meta, (a)
  entrega zero.

**O que sobrou não é uma decisão de gate — são dois problemas técnicos
distintos**, e é isso que este prereg registra.

## 2. As duas trilhas

### Trilha A — 3 curvas com receita aplicada e pico residual sobrando
`fig8a`, `fig8b`, `fig8c`: MAE excelente (0.043–0.044) e res.máx 0.122–0.145.
A causa registrada no PR-31f é que o **arresto do modelo é seco** enquanto o
dado se aproxima do platô progressivamente.

Mas o diagnóstico de hoje mostra que **não são o mesmo caso**:
- `fig8b` tem `loose_arrest_floor = 0.0` adotado e o modelo vai a **zero**
  (final 0.00 contra 0.13 medido). Não é arresto seco — é **runaway puro**,
  a bifurcação que o CLAUDE.md descreve para floor=0 ("sem meio").
- `fig8a` (floor 0.059) e `fig8c` (floor 0.152) têm floor > 0 e erram na
  **curvatura da aproximação**, não no destino.

Esta trilha é a mesma forma que `DECISOES_PENDENTES` chama de **decisão de maior
alavancagem**: kernel de colapso desacelerante com aproximação suave ao floor,
travando 4 fontes (~25–30 curvas: Lu2024, Eccles, Chu2026, Sun-standard).
**Recomendação de escopo: NÃO fazer um prereg só-Eccles para o kernel.** Três
curvas não justificam física nova; 25–30 em 4 rigs justificam, e o teste de
transferência entre fontes é o que dá valor científico. Este documento registra
os gates de Eccles como **parte** desse prereg maior.

### Trilha B — 2 curvas nunca tratadas
`fig6` e `fig8d` resolvem para **nenhum grupo adotado** (`_adopted_for` → None):
ficaram fora do escopo do PR-31 e rodam nos defaults. Não são form-limited,
são **não-tratadas** — e são as duas piores da fonte (0.467 e 0.252).
Antes de qualquer física nova, aplicar a receita que já existe e medir.
Custo: uma rodada de leitura. Esta é a trilha barata e deve vir primeiro.

## 3. Diagnóstico OBRIGATÓRIO antes de qualquer fit

- **D1** — Resíduo assinado vs N nas 5 violadoras. Separar "erra o destino" de
  "erra o caminho".
- **D2** — `fig8b`: o `floor = 0.0` é **leitura** (torque prevalecente esgotado,
  declarado no paper) ou **artefato de fit**? Decide por leitura se a curva é
  runaway legítimo ou se o floor foi mal lido. Sem isso, qualquer kernel vai
  compensar um input errado.
- **D3** — `fig6`/`fig8d`: por que ficaram fora do escopo do PR-31? Ler a nota
  de aparato (`apparatus_notes/`) e o paper. Hipótese a testar: são as duas com
  carga axial **anotada/intermitente** mais alta (4.0 e 3.5 kN) — pode ser
  condição fora do escopo da receita, não esquecimento.
- **D4** — Sonda de direção com **2 pontos** antes de qualquer bisseção, para
  cada lever candidato. Regra dura da campanha.
- **D5** — Aplicar `csv_x_scale` corretamente: Eccles tem o eixo em **segundos**
  (×12.5 → ciclos). Confirmar que o overlay e a métrica usam a convenção; um
  erro aqui simula outra coisa que não a curva do paper.

## 4. GATES — imutáveis

**G-B1 (Trilha B, barata, primeiro).** Aplicar a receita PR-31 existente a
`fig6` e `fig8d` com o grupo-de-porca correto lido do paper. *Passa* se ambas
melhorarem ≥30% no res.máx **e** nenhuma das 8 já tratadas piorar mais de
+0.01. Se o res.máx cair abaixo de 0.10, a curva fecha e sai da lista.
*Falha honesta prevista:* se a receita não se aplica porque a condição axial
está fora do escopo, isso é **resultado**, não fracasso — vira nota de escopo
no `prov` e as duas curvas passam para a Trilha A.

**G-A1 (Trilha A) — Inércia por construção.** O kernel nasce default-inerte:
com o parâmetro de suavização no valor OFF, os **202 casos** saem
**bit-idênticos** ao store `4f5bedfbace4`. Switch `fittable=False` no registry.

**G-A2 — Alvo local.** `fig8a`, `fig8b` e `fig8c` entram no tripé.
*Crédito parcial:* ≥2 de 3, com a terceira melhorando ≥30% no res.máx.

**G-A3 — Transferência entre FONTES (o gate que justifica a física nova).**
O parâmetro de forma do kernel é ajustado em **uma** fonte e prevê as outras
**sem re-fit**. Concretamente: ajustar em Lu2024 (10 curvas, a maior) e prever
Eccles `fig8a/b/c`, Chu2026 e Sun-standard zero-refit. *Passa* se ≥60% das
curvas previstas melhorarem ≥30% no res.máx sem nenhum re-ajuste.
**Se o kernel precisar de constante própria por fonte, ele NÃO é uma forma —
é um tuner com nome bonito, e não deve ser adotado.**

**G-A4 — Não-regressão global.** Nenhum caso da biblioteca piora mais de +0.01;
a mediana dos 202 não piora; as 5 curvas Eccles que hoje passam continuam
passando.

**G-A5 — O resíduo cai onde ele estava.** O res.máx tem de cair na posição do
`maxerr_at` original de cada curva. Proíbe deslocar o pico e melhorar a métrica
sem acertar a física.

**G-A6 — Procedência.** Toda constante nova declara classe (medida | âncora |
handbook | fitada-this-rig) e entra na contagem de DOF. O expoente/rigidez da
aproximação ao floor precisa de **justificativa física nomeada** — não vale
"é o que ajusta".

**G-A7 — Verificação adversarial.** ≥3 votos independentes tentando **refutar**
o "passou", com instrução de assumir refutado em caso de dúvida. Maioria
refutando = não adota. *Motivo específico:* um kernel com termo
`(1−floor/ratio)^m` é um absorvedor muito flexível — é exatamente o tipo de
forma que passa gate por flexibilidade, não por acerto. O precedente é o PR-10,
em que o floor 0.30 melhorava a mediana e foi corretamente recusado como
absorvedor cego.

## 5. Parada

- Trilha B tem **1** tentativa (é aplicação de receita existente, não física).
- Trilha A herda o FAIL2 do prereg multi-fonte do kernel; não gasta tentativa
  própria de Eccles.
- **FAIL2 no kernel** → `fig8a/b/c` viram exceção-candidata com prova
  quantitativa (a diferença medida entre aproximação suave e arresto seco), e a
  mesma decisão fecha Lu2024/Chu2026/Sun-standard da mesma forma.
- Em qualquer FAIL, statu quo **byte-idêntico**.

---

# RESULTADO — Trilha B executada em 2026-07-27 (tentativa única gasta)

> Seção acrescentada APÓS a execução. Os gates acima não foram alterados.

## G-B1: **FAIL**

Receita PR-31 aplicada em sandbox (`BAS_ADOPTED_CONFIGS`, canônico intocado),
com o grupo-de-porca lido da nota de aparato — `fig6` na porca do trio
fig7(a)-(d) (a nota liga o "4 kN" ao teste 7, 4.1 kN, mesmo grupo) e `fig8d` na
porca #3 do `fig8c` — e `loose_arrest_floor = 0.0`, porque o critério do próprio
paper diz que FA (4.0 e 3.5 kN) **excede** o residual sem axial (3.2 e 2.4 kN),
logo a rotação continua até zero e destacamento.

| alvo | MAE | res.máx |
|---|---|---|
| `fig6` | 0.146 → **0.421** | 0.467 → **1.028** |
| `fig8d` | 0.134 → **0.239** | 0.252 → **0.400** |

Os 8 casos já tratados saíram **bit-idênticos** (isolamento limpo). Piora muito
além do gate: FAIL sem ambiguidade. A tentativa única da Trilha B está gasta.

## Por que falhou — e a previsão estava escrita

A nota de aparato (`BAS_V2_papers/E. Rodada 4/apparatus_notes/eccles2010.md`)
já dizia, em V2 mapping: *"**No existing V2 mechanism represents the combined
axial+transverse scenario**"*, e nomeava Figs. 7(d), 8(b) e 8(d) como
*"the novel falsifier/target"*. `fig6` e `fig8d` **não ficaram de fora do PR-31
por esquecimento** — são a família em que uma condição de contorno axial
externa **sobrepõe** o piso de arresto, e o engine não tem esse conceito.
Com `floor=0` o modelo faz a única coisa que sabe fazer sem o mecanismo: dispara
para zero. É a mesma patologia do `fig8b` (modelo 0.00 contra 0.13 medido).

## O achado que vale mais que o gate: **o FLOOR_TRIM apaga o resultado do paper**

A convenção da campanha descarta da métrica todo ponto com `ratio < 0.10`.
Medido no CSV cru:

| curva | dado cru chega a | pontos cortados | métrica enxerga o final em |
|---|---|--:|--:|
| `fig6` | 0.000 | 4 de 29 | 0.137 |
| `fig7d` | 0.000 | 4 de 26 | 0.187 |
| **`fig8b`** | 0.000 | **27 de 35 (77%)** | 0.130 |
| `fig8d` | 0.000 (vales) | 7 de 37 | 0.220 |

O paper **existe** para demonstrar que a porca chega a zero e se destaca; a
convenção remove exatamente esse trecho. Três consequências:

1. O `fig8b` é pontuado sobre **8 de 35 pontos** — o MAE 0.044 dele não
   significa o que parece.
2. O `fig7d` **passa no tripé (0.089) porque sua cauda a zero é cortada.** Ele
   está na coluna dos aprovados por artefato de convenção.
3. Um modelo fisicamente CERTO nesta família (que vá a zero) é **penalizado**,
   porque é comparado com uma curva truncada que para em 0.137.

Não é problema de modelo — é de **convenção de medida**. E não pode ser
consertado dentro deste prereg: mexer no `FLOOR_TRIM` afeta os 202 casos.

## Roteamento — correção ao §2 deste prereg

O §2 dizia que, em caso de falha, `fig6`/`fig8d` "passam para a Trilha A"
(kernel desacelerante). **Errado:** elas não são kernel, são
**sobreposição axial**. A família correta tem 4 membros — `fig6`, `fig7d`,
`fig8b`, `fig8d` — unidos por FA > residual e por terem a cauda a zero cortada
da métrica. O kernel desacelerante segue valendo só para `fig8a`/`fig8c`.

## Decisão que isto gera (nova, para o professor)

Para a família de sobreposição axial (4 curvas), escolher:
- **(i)** isentar a família do `FLOOR_TRIM` (exceção de convenção por fonte) e
  medir contra a curva inteira — aí o modelo com `floor=0` passa a ser avaliado
  pelo que ele de fato acerta, e o `fig7d` perde a aprovação por artefato;
- **(ii)** declarar a família **fora-de-modelo** (o engine não tem condição de
  contorno axial externa) e mandar as 4 para exceção com esta prova;
- **(iii)** construir o mecanismo — condição axial externa que sobrepõe o piso
  de arresto —, que a nota de aparato já especifica em prosa.

Recomendação: **(ii) agora, (iii) só se a família crescer.** São 4 curvas de uma
fonte; o mecanismo é conceitualmente novo (contorno externo, não mecanismo de
perda) e não transfere para nenhuma outra fonte da biblioteca hoje.

---

## 6. NÃO autorizado por este prereg

- **Aceitar G2 = MAE-only.** Está medido que não move nenhuma curva para o
  tripé. Se for adotado assim mesmo, que seja como decisão explícita de
  contabilidade — com a consequência escrita de que as curvas seguem fora da
  meta e **não** contam como fechadas.
- Fitar `loose_arrest_floor` por curva sem leitura de paper que o sustente: o
  floor é **torque prevalecente medido**, é input, não botão.
- Prereg de kernel escopado só em Eccles (ver §2, Trilha A).
- Tocar em qualquer fonte fora de ECCLES_2010 na Trilha B.
