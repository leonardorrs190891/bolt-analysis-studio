# PRÉ-REGISTRO — fratura terminal do `YANG_2021` por fadiga+rampa, com `fat_C1` ancorado em forma fechada

> ## ⛔ EXECUTADO E REPROVADO — ramo `PIORA` (2026-07-29, mesma noite)
>
> Resultado completo: **`New_Theory/yang2021_fratura_resultado.md`**. Nada foi
> adotado; store e `adopted_configs.json` intocados. Resumo: **G1 ✅** (o anchor
> acerta a vida medida em 6/6, erro 0,0 %) · **G2 ❌** (4 das 5 cegas pioram > +0,01)
> · **G3 ❌** (a melhor `(D_on,q)` varia por curva) · **G4 ❌** (0/6 passam, precisava
> ≥ 2). Caso nomeado pelo ramo: `yang2021_amp0p5mm_ax8kN` (+0,165 de MAE).
>
> Duas coisas que a execução mudou e que **não** são afrouxamento de gate:
> (a) a ancoragem da §3 (soma de Miner em 2 passadas) **está mal posta** — o ponto
> fixo de `S` não é a raiz de `D = 1`, porque o Goodman vivo se auto-realimenta;
> substituída por bisseção da raiz com direção verificada, mantendo o critério do G1
> intacto e declarando que o sub-critério "≤ 4 passadas" **deixou de se aplicar**;
> (b) descobriu-se que `FLOOR_TRIM = 0.10` (convenção da campanha) já tira o colapso
> final de **43 das 203 curvas**, e faz a simulação parar antes de `N_frat` — era isso
> que tornava a fratura inobservável, não a álgebra.
>
> Os gates da §4 abaixo **não foram editados**.

**Escrito em 2026-07-29 (noite), ANTES de medir o que está abaixo.** Congelado no
commit que o introduz. Os gates da §4 são **imutáveis** depois deste commit — é a
única coisa que separa pré-registro de relato.

**Origem:** observação do professor ao abrir `yang2021_amp0p7mm_ax11p2kN` — *"o fit
não ficou bom, pois não pega a queda no final. Esse resultado é similar ao Liu 2025
— M16 shear (Sci. Rep.)"*. A leitura está correta e o precedente é exato.

---

## 1. O fato que motiva (medido antes deste prereg — declarado como tal)

As **6 curvas** do `YANG_2021` terminam em `F/F₀ = 0,000` (fratura). Todas estão
**trimadas** logo antes da queda, cortando 2–4 pontos finais que valem **39 a 83
pontos percentuais**. `fatigue_enabled` está **ausente** no cfg adotado da fonte.

| curva | N_frat medido | trim | queda cortada | hoje (MAE/res.máx/σ, janela trimada) | tripé |
|---|--:|--:|--:|---|---|
| `yang2021_fig2_typical` | 6020 | 5850 | 60,3 pp | 0,0992 / 0,1625 / 0,0604 | reprova |
| `yang2021_amp1p0mm_ax2kN` | 3300 | 3150 | 39,0 pp | 0,0580 / 0,0919 / 0,0476 | reprova |
| `yang2021_amp0p8mm_ax6kN` | 5700 | 5450 | 53,2 pp | 0,0938 / 0,1422 / 0,0552 | reprova |
| `yang2021_amp0p6mm_ax8kN_r1` | 12500 | 11800 | 80,1 pp | 0,0266 / 0,0415 / 0,0223 | **passa** |
| `yang2021_amp0p7mm_ax11p2kN` | 15000 | 14000 | 83,0 pp | 0,0173 / 0,0621 / 0,0221 | **passa** |
| `yang2021_amp0p5mm_ax8kN` | 27800 | 27000 | 70,9 pp | 0,0549 / 0,0945 / 0,0458 | reprova |

**Consequência medida na `amp0p7mm`:** na janela **inteira** e sem fadiga ela dá
0,0510 / **0,3715** / 0,0997 — reprova nas três. **É o trim que a aprova.** Em
x = 14700 o dado está em 0,484 e o modelo em 0,855.

## 2. O que JÁ foi medido antes deste prereg (divisão treino/teste declarada)

Honestidade obrigatória, porque contamina qualquer gate que a ignore: a dupla
`(D_on, q)` foi escolhida por **grade sobre UMA curva** — a `amp0p7mm`, já aberta
com o professor. Naquela curva, com `fat_C1 = 3,2e33`:

| `D_on` | `q` | MAE | res.máx | σ_res | tripé |
|--:|--:|--:|--:|--:|---|
| 0,75 (valor do Liu) | 8 | 0,0231 | 0,1213 | 0,0378 | reprova |
| 0,75 | 16 | 0,0198 | 0,0624 | 0,0243 | passa |
| **0,85** | **8** | **0,0199** | **0,0526** | **0,0249** | **passa** |
| 0,85 | 16 | 0,0241 | 0,0772 | 0,0284 | reprova |
| 0,92 | 8 | 0,0234 | 0,0655 | 0,0268 | reprova |
| 0,92 | 16 | 0,0304 | 0,1086 | 0,0394 | reprova |

⇒ **`amp0p7mm` é a curva de TREINO. As outras 5 são o teste CEGO.** Os gates da §4
são avaliados **nas 5**, nunca na de treino. Reportar sucesso na `amp0p7mm` como
evidência seria circular.

Uma tentativa anterior de generalizar deu **1 de 6**, mas com `fat_C1` ancorado por
**laço iterativo** que **não convergiu em 4 das 6** (esgotou 5 iterações) — logo
aquele resultado é **inconclusivo**, não negativo, e é a razão de existir a §3.

## 3. A ancoragem em FORMA FECHADA (o conteúdo técnico da proposta)

O laço iterativo falha porque o Goodman é **vivo**: `σ_ar = σ_a/(1 − σ_m/uts)` com
`σ_m = F₀/A_s`, então à medida que a junta afrouxa `σ_ar` **cai** e a vida
**estica** (o repo já registra 30–70 %). A atualização linear de `C1` oscila.

Mas a acumulação de Miner é **linear em `1/C1`**:

```
dD(n) = 1/N_f(n) = σ_ar(n)^m1 / C1        (ramo de alta tensão, fat_sigma_knee=0)
D(N)  = (1/C1) · Σ_{n=1..N} σ_ar(n)^m1
```

Impor `D(N_frat) = 1` dá o anchor **exato, sem iteração e sem parâmetro livre**:

```
C1  =  Σ_{n=1..N_frat} σ_ar(n)^m1
```

E com a rampa (`fat_ramp_D_on < 1`), `α = ((D−D_on)/(1−D_on))^q` chega a 1 **só em
D = 1** ⇒ `g → 0` exatamente em `N_frat` ⇒ **a pré-carga do modelo zera no ciclo de
fratura medido**. Isto é uma **LEITURA** da vida medida (classe "ler em vez de
fitar", L24), não um ajuste.

**Duas passadas, e a razão de serem só duas:** abaixo de `D_on` o ramo da rampa
devolve `dF_0 = 0` (verificado no engine, linhas ~1775), logo `F₀(n)` — e portanto
`σ_ar(n)` — **não depende da fadiga nos primeiros 85 % do dano**. Só os últimos 15 %
mudam ao ligar a rampa. Procedimento:

1. passada 0: rodar com fadiga ligada e `C1 = 10³⁵` (não fratura), **instrumentando
   `sun_life`** para gravar o `σ_ar` que o engine de fato usa em cada ciclo — não uma
   re-derivação minha, que poderia divergir da implementação;
2. `C1 ← Σ_{n ≤ N_frat} σ_ar(n)^m1`;
3. passada 1: re-rodar com esse `C1`, recolher `σ_ar(n)` de novo (agora com a rampa
   ativa nos últimos 15 %) e recomputar. Convergência declarada quando
   `|ΔC1|/C1 ≤ 2 %`, com **máximo de 4 passadas**.

`N_frat` de cada curva é lido do CSV digitalizado (1º x com `y ≤ 0,01`) — a coluna
já está na tabela da §1. **Nenhum `N_frat` é ajustado.**

### Constantes e sua procedência

| constante | valor | procedência |
|---|---|---|
| `fat_stress_mode` | `"bending"` | mesma do `LIU_2025` adotado: rig transversal, o parafuso flexiona pelo δ imposto |
| `fat_Kt` | 0,588 | idem `LIU_2025` (adotado) |
| `fat_sigma_uts` | 800 MPa | idem `LIU_2025` |
| `fat_m1` | 3,12 | idem `LIU_2025`; é a inclinação `N_frat × σ_root` que o dado do Liu sustenta |
| `fat_sigma_knee` / `endurance` | 0,0 / 1,0 | idem — ramo único de alta tensão |
| `fat_C1` | **por curva** | **LEITURA** de `N_frat` medido, via §3 |
| `fat_ramp_D_on`, `fat_ramp_q` | fixados no treino | **dívida declarada**: forma per-rig sem âncora independente. 0,85/8 aqui contra 0,75/8 adotado no Liu |

⚠️ **A dívida do `D_on` é o ponto fraco desta proposta e não deve ser escondida:**
`D_on = 0,85` foi escolhido por grade numa curva. A alternativa `0,75/16` também
passa no treino e mantém o `D_on` do Liu. O gate **G3** decide entre as duas **pelas
5 curvas cegas**, não pela de treino.

## 4. GATES — imutáveis a partir deste commit

Avaliados nas **5 curvas cegas** (`fig2_typical`, `amp1p0`, `amp0p8`, `amp0p6_r1`,
`amp0p5`). A `amp0p7mm` é reportada, nunca contada.

| # | gate | critério de PASSA |
|---|---|---|
| **G1** | a ancoragem faz o que promete | o zero do modelo cai a **≤ 5 %** de `N_frat` medido em **6 de 6** (inclui o treino: é verificação de implementação, não de mérito) e a §3 converge em ≤ 4 passadas |
| **G2** | o mecanismo ajuda na **mesma** janela | comparando **curva inteira com fadiga** vs **curva inteira sem fadiga**: res.máx melhora em **≥ 4 das 5**, e **nenhuma** das 5 piora mais de **+0,01** em qualquer perna |
| **G3** | a forma é **compartilhada** | uma única `(D_on, q)` para as 6. Testar **as duas** candidatas do treino (0,85/8 e 0,75/16) e adotar a que vence nas 5 cegas. Se a melhor `(D_on,q)` diferir por curva, **G3 FALHA** — é fit, não forma |
| **G4** | efeito líquido na meta, declarado ANTES | nº das 6 que passam o tripé na **janela inteira** com fadiga **≥ 2** (= o que hoje passa com a queda trimada). Abaixo de 2 ⇒ não adotável como está |
| **G5** | nada mais se move | batch completo: **zero** curvas fora do `YANG_2021` com qualquer perna alterada, e **zero** curvas piores em > +0,01 no acervo (gate PR-37′) |
| **G6** | procedência gravada | cada `fat_C1` gravado junto com o `N_frat` que o gerou; `D_on`/`q` marcados como **dívida per-rig sem âncora** no `adopted_configs.json` |

**Guardas herdados** (template `2026-07-29-gate-candidato-de-forma.md` §3): sonda é
só-leitura — **store e `adopted_configs.json` intocados durante a medição**; adoção é
passo separado; `Δ = 0` classificado em (a) nome inexistente / (b) gate de modo /
(c) magnitude; comparação contra o **piso da fonte**, não contra zero.

## 5. Ramos de decisão (escritos antes, com a ação de cada um)

- **PASSA** — G1–G6 ok ⇒ propor adoção gateada ao professor, com o efeito na meta
  explícito e a remoção dos 6 trims da lista de exceções da F5.
- **PARCIAL** — G1 e G2 ok, G4 < 2 ⇒ o mecanismo é **real e a forma está certa**, mas
  a adoção **troca aprovação-por-trim por reprovação-honesta**. Registrar como
  componente, **não adotar sem decisão explícita** do professor, e dizer o número.
- **FORMA POR CURVA** — G3 falha (melhor `(D_on,q)` varia entre curvas) ⇒ é ajuste
  per-curva disfarçado de física. **Não adotar.** Registrar a variação medida.
- **ANCHOR QUEBRADO** — G1 falha ⇒ a derivação da §3 está errada (ou o engine não
  acumula Miner como eu li). Conserto e re-medição; nenhuma conclusão sobre física.
- **PIORA** — qualquer curva do acervo além de +0,01 ⇒ falha, com o caso nomeado.

## 6. O que este prereg NÃO pretende

- **Não** prevê a vida: `N_frat` é **input** lido do dado, exatamente como o
  `LIU_2025` E2. A claim máxima é *"prevê a curva DADA a vida"*.
- **Não** ancora `D_on`/`q` — fica dívida declarada (§3).
- **Não** toca as outras 27 fontes.
- **Não** decide sobre a normalização pelo 1º ponto (`yang2021_amp0p7mm` tem o 1º
  ponto do CSV em 1,0993) — é outra pendência, do professor, e as duas não devem ser
  misturadas no mesmo re-carimbo.

## 7. Reprodutibilidade

```bash
py -3.12 New_Theory/yang2021_fratura_probe.py          # sonda completa, so-leitura
py -3.12 New_Theory/yang2021_fratura_probe.py --quick   # 2 curvas, smoke
```
