# Execução do TRIO — **mecanismo CONFIRMADO, parametrização FALSIFICADA pelo held-out**

**Executado em 2026-07-30.** Prereg:
`docs/superpowers/specs/2026-07-30-yang2023ijpem-trio-prereg.md`.
Sonda: `New_Theory/yang2023_trio_exec.py`. **Nada adotado**; store e
`adopted_configs.json` intocados. Congelados: `delta_free` 122,96/129,18 µm ·
`loose_arrest_floor` 0,1025 · `slip_onset_W` **12,45 J**.

| gate | resultado |
|---|---|
| **G2** saturadas não regridem | **PASSA** — mediana 0,2928 → 0,2863 |
| **G3** sub-crítico bit-idêntico | **PASSA** |
| **G4** 0,35 ≤ 0,1788 e nada +0,01 | **REPROVA** — mas **não** no 0,35 |
| **G5** incubação no estágio I | **PASSA** — μ(I) do 0,35: −0,1648 → **−0,0602** |
| **F4′** canal ≤ F₀(1−piso) | **ok** — a correção do falsificador estava certa |
| **G6/F5** held-out | **F5 DISPARA** — 2 de 3 pioram |
| **G7** resto do store | **PASSA** |

---

## O alvo do prereg foi atingido

O prereg existia para consertar a regressão do 0,35 mm. Conseguiu:

* **MAE 0,2103 → 0,1775**, abaixo do baseline de 0,1788 ⇒ a cláusula do G4 sobre
  o 0,35 **passa**;
* **res.máx 0,5100 → 0,4598**;
* e o **G5 confirma que o conserto foi no lugar certo**: a média do resíduo do
  estágio I foi de **−0,1648 para −0,0602** (2,7× menor em módulo). Não foi
  compensação em outro estágio — foi a incubação agindo onde o defeito estava.

**A incubação é o mecanismo certo.** Isso fica estabelecido.

## O que reprovou — e é o held-out fazendo o seu trabalho

G4 reprova em **0,50 mm** e **0,65 mm**, que são **duas das três held-out** (as
que não leram o W porque o joelho delas não é resolvível no dado):

| δ | own W (J) | MAE par → trio | res.máx par → trio |
|---:|---:|---|---|
| 0,50 | **4,45** | 0,2306 → **0,3496** | 0,3913 → **0,5811** |
| 0,65 | **8,17** | 0,0532 → **0,1601** | 0,0906 → **0,3131** |
| 0,55 | **15,25** | 0,1211 → **0,0955** | 0,3243 → **0,1867** |

E o padrão é **exato**, não vago:

* as **4 que LERAM** o W (0,25 · 0,30 · 0,35 · 0,45) melhoram;
* das 3 held-out, **piora quem tem `own W < 12,45`** (0,50 com 4,45 · 0,65 com
  8,17) e **melhora quem tem `own W > 12,45`** (0,55 com 15,25).

A leitura física é direta: um W único **atrasa demais** o colapso das curvas cujo
limiar próprio é menor. E como o W próprio **não** é constante (4,45 a 19,95 J,
espalhamento 4,5×, sem monotonia com a amplitude), **um limiar de trabalho único
não é lei nesta fonte** — é exatamente o que o F5 declarou que mataria a hipótese.

## Por que isto é o resultado certo, e não um fracasso

Se eu tivesse lido o W das **7** curvas em vez de 4, o trio teria "funcionado":
todas melhorariam e eu teria adotado um **sobreajuste** — 7 números
disfarçados de constante. O critério de resolubilidade, escrito por argumento de
amostragem **antes** de ver qualquer erro, é o que criou o conjunto held-out; e o
held-out é o que matou a hipótese.

O F4′ corrigido também passa em todas as 9 (canal rotacional drena 0,84–0,88 kN
contra tetos de 9,9–12,8 kN), confirmando que a correção pedida estava certa: o
piso promete sobre o **canal**, não sobre o `ratio` total.

## O saldo contra o baseline original

| δ | baseline | trio | |
|---:|---:|---:|---|
| 0,30 | 0,1200 | **0,1005** | melhora |
| 0,35 | 0,1788 | **0,1775** | melhora |
| 0,45 | 0,1042 | **0,0956** | melhora |
| 0,55 | 0,1192 | **0,0955** | melhora |
| 0,50 | 0,2386 | 0,3496 | **piora** |
| 0,65 | 0,0822 | 0,1601 | **piora** |
| 0,25 | 0,1664 | 0,2797 | piora (isenta) |

4 melhoram, 3 pioram. **Nenhuma curva entra no tripé** — como declarado antes de
rodar.

## O que fica estabelecido

1. **incubação é a forma que faltava** no estágio I (G5, medido no lugar do
   defeito);
2. **`slip_onset_W` único NÃO é lei** nesta fonte (F5, com direção consistente:
   piora quem tem limiar próprio menor);
3. o **piso de arresto** segue sendo ≈ constante da bancada (o par já mostrou);
4. o **F4′** corrigido é a formulação certa do falsificador;
5. a **transição (0,25 mm)** continua sem forma — a incubação melhorou o MAE dela
   (0,3171 → 0,2797) mas o patamar segue errado.

## Follow-up — e uma decisão que não é minha

O caminho técnico óbvio é `slip_onset_W` **dependente da amplitude**. Mas isso
deixa de ser input lido e passa a ser **forma nova com parâmetro por amplitude** —
e a fonte tem 7 curvas úteis para no máximo 2 constantes se a parcimônia for
mantida. Antes de construir isso, vale a pergunta que a matriz de âncoras (D2b) já
formulou: **o limiar de incubação é ancorável em alguma fonte com varredura de
amplitude E joelho bem amostrado?** Nesta, metade das curvas não resolve o joelho.

Ou seja: pode ser que este caminho precise de **dado**, não de forma — e essa é a
mesma conclusão que o LU_2024 e o ECCLES_2010 já tinham dado por outro caminho.
