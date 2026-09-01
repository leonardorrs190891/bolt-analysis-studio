# Diagnóstico do "kernel de colapso desacelerante" — ANTES do prereg

> **2026-07-27.** Medido no store certificado `4f5bedfbace4`, sobre as 26 curvas
> que a fila classifica como travadas por esta forma. **Nenhuma tentativa de
> prereg foi gasta** — o protocolo manda diagnosticar antes de fitar, e o
> diagnóstico mudou o alvo.
>
> Scripts: assimetria por fonte e correlação de formas detrendadas (reproduzíveis
> a partir do store; ver §5).

---

## 1. Resultado em uma frase

**A fila nomeia as quatro fontes erradas.** A "DECISÃO DE MAIOR ALAVANCAGEM" diz
que *a mesma forma* trava **Lu2024, Eccles2010, Chu2026 e Sun-crimp**. Medido, a
família coerente é **Chu2026 + Yang2019 + Karlsen + Zhang2006** — e **Lu2024,
Eccles e Sun não pertencem a ela**.

---

## 2. Como foi medido

Para cada curva fora do tripé, o resíduo `modelo − dado` foi reamostrado na grade
do dado (mesmas convenções de eixo e `FLOOR_TRIM` do runner) e resumido em
quintis. Duas passadas:

1. **Bruta** — mede nível + forma juntos.
2. **Detrendada** — média removida **por curva**, isolando só a *forma*. Esta é a
   passada que importa: o **nível** já é legitimamente per-rig no modelo
   (`loose_arrest_floor` é lido do dado por par), então um desacordo de nível
   **não** justifica forma nova. Só um desacordo de *forma* justifica.

---

## 3. Perfis de forma (resíduo detrendado, 5 quintis)

| fonte | n | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|--:|--:|--:|--:|--:|--:|
| LU_2024 | 10 | **+0,093** | −0,030 | −0,065 | −0,029 | +0,025 |
| CHU_2026 | 7 | −0,102 | −0,065 | −0,000 | +0,068 | **+0,130** |
| YANG_2019 | 4 | −0,054 | −0,068 | −0,019 | +0,024 | **+0,168** |
| ECCLES fig8a/8c | 2 | +0,022 | −0,019 | +0,015 | −0,014 | +0,001 |
| KARLSEN | 1 | −0,091 | −0,039 | +0,029 | +0,083 | **+0,148** |
| SUN grease-standard | 1 | +0,080 | +0,115 | +0,022 | **−0,186** | −0,038 |
| ZHANG_2006 | 1 | −0,164 | −0,204 | −0,075 | +0,185 | **+0,319** |

**Correlação entre perfis** (1,0 = mesma forma; <0 = formas opostas):

| | LU | CHU | YANG19 | ECCLES | KARLSEN | SUN | ZHANG |
|---|--:|--:|--:|--:|--:|--:|--:|
| **LU_2024** | 1,00 | −0,27 | +0,08 | +0,47 | −0,33 | +0,24 | −0,03 |
| **CHU_2026** | −0,27 | 1,00 | **+0,92** | −0,29 | **+1,00** | −0,74 | **+0,96** |
| **YANG_2019** | +0,08 | **+0,92** | 1,00 | −0,07 | **+0,90** | −0,52 | **+0,94** |
| **ECCLES** | +0,47 | −0,29 | −0,07 | 1,00 | −0,30 | +0,30 | −0,21 |
| **KARLSEN** | −0,33 | **+1,00** | **+0,90** | −0,30 | 1,00 | −0,71 | **+0,94** |
| **SUN_std** | +0,24 | −0,74 | −0,52 | +0,30 | −0,71 | 1,00 | −0,78 |
| **ZHANG_2006** | −0,03 | **+0,96** | **+0,94** | −0,21 | **+0,94** | −0,78 | 1,00 |

11 dos 21 pares têm correlação **negativa**. Não existe *uma* forma comum às 26.

---

## 4. O que existe de verdade: três grupos, não um

### Grupo A — forma coerente, **13 curvas, 4 rigs independentes**

**CHU_2026 (7) · YANG_2019 (4) · KARLSEN (1) · ZHANG_2006 (1)** — correlações
mútuas **0,90 a 1,00**. Perfil monótono de negativo a positivo: o modelo
**colapsa cedo demais e trava tarde demais**. Assimetria fim−início: +0,20
(Chu), +0,16 (Yang), +0,20 (Karlsen), +0,45 (Zhang).

Isto é **exatamente o que "uma forma que transfere" parece**: quatro aparatos
independentes, com bolt sizes, materiais e amplitudes diferentes, exibindo o
mesmo erro de forma com r ≥ 0,90. **É este grupo que merece o prereg**, e o
G-A3 (transferência entre fontes) tem aqui um teste honesto: ajustar em CHU (o
maior, 7 curvas) e prever Yang2019/Karlsen/Zhang **sem re-fit**.

### Grupo B — **ECCLES fig8a/8c (2 curvas): não é forma, é NÍVEL**

Perfil detrendado **essencialmente plano** (máximo |0,022| nos 5 quintis), com
resíduo bruto ~**−0,043 uniforme**. Ou seja: a curva tem a forma certa e está
deslocada. Isso **não pede forma nova** — pede revisão do nível, que é
`loose_arrest_floor`, per-par e lido do dado por procedência estabelecida.
**Contradiz o prereg do Eccles**, que mandou fig8a/8c "pagarem pedágio no kernel
desacelerante": elas não têm o erro de forma do kernel.

### Grupo C — **LU_2024 (10) + SUN grease-standard (1): outra forma**

LU tem perfil em **tigela** (+0,093 / −0,030 / −0,065 / −0,029 / +0,025): o erro
é máximo no **meio** e some nas pontas — assinatura de **tempo de joelho**, não
de aproximação ao piso. SUN é diferente de todos (correlação −0,74 a −0,78 com o
grupo A). Correlação LU↔SUN = **+0,24**: fracos até entre si.

**Consequência para o item mais caro da fila:** as 10 curvas do Lu2024 — a maior
fonte fora do tripé — **não** seriam fechadas pelo kernel do grupo A. Elas são um
problema separado, e menos definido, porque o LU sozinho não tem par com quem
transferir.

---

## 5. O que isto muda na fila

| item da fila | como está escrito | medido |
|---|---|---|
| alcance | "~25-30 curvas, 4 fontes, a MESMA forma" | **13 curvas, 4 fontes** na família coerente |
| membros | Lu2024, Eccles2010, Chu2026, Sun-crimp | **Chu2026, Yang2019, Karlsen, Zhang2006** |
| Lu2024 (10) | dentro | **fora** — forma em tigela, r=−0,27 com Chu |
| Eccles 8a/8c (2) | dentro | **fora** — erro é de NÍVEL, forma plana |
| Sun grease-std (1) | dentro | **fora** — r=−0,74 com Chu |
| Yang2019 (4) | não citado | **dentro**, r=+0,92 |
| Karlsen (1), Zhang2006 (1) | não citados | **dentro**, r=+1,00 e +0,96 |

---

## 6. Recomendação

1. **Prereg do kernel escopado no grupo A** (13 curvas, 4 rigs) — não nas quatro
   fontes da fila. O G-A3 vira um teste real: ajustar em CHU, prever os outros 3
   rigs zero-refit. Se falhar aí, falha honestamente, contra a melhor hipótese
   disponível em vez de contra uma mistura.
2. **Eccles fig8a/8c: tentar nível antes de forma.** São 2 curvas com resíduo de
   nível quase puro; se o floor lido fechar, custam zero física nova.
3. **Lu2024 + Sun: diagnóstico próprio.** A forma em tigela do LU é uma pergunta
   diferente ("quando o joelho acontece"), e é onde estão 10 das 40 curvas
   form-limited. Merece o seu próprio par diagnóstico→prereg.

**Nenhuma tentativa de prereg foi gasta neste documento.** O valor dele é ter
mudado o alvo antes do gasto: um prereg de kernel nas quatro fontes da fila
teria misturado formas anticorrelacionadas (r até −0,78) e falhado por
construção — e o FAIL2 resultante teria enterrado uma hipótese que, no escopo
certo, ainda está viva.

---

## 7. Reprodutibilidade

Os três diagnósticos leem apenas o store canônico e os CSVs da biblioteca
(nenhum fit, nenhuma escrita):

1. sinal do resíduo por quintil e classificação trava-cedo/dispara/misto;
2. assimetria início-vs-fim por fonte (nível + forma);
3. correlação entre perfis **detrendados** (forma pura) — a tabela do §3.

Convenções aplicadas em todos: `(x − csv_x_offset)·csv_x_scale`, normalização no
primeiro ponto e `FLOOR_TRIM`, idênticas às do runner — o resíduo medido aqui é o
mesmo contra o qual a métrica foi computada.
