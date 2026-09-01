# O segundo defeito sob a rampa — **é curvatura, e ela ordena pela amplitude** (atividade F)

**Data:** 2026-07-29 · **Store:** `3546e6745448` · dados: `chu_segundo_defeito.json`
**Medição só-leitura.** Nada escrito no store nem em `adopted_configs.json`.

A atividade B deixou uma pendência explícita: *"a próxima medição útil é caracterizar
o resíduo depois de remover a rampa (rodar a célula Pareto e reclassificar)"*. Ela foi
tentada assim, **falhou por construção**, e o conserto mudou o resultado.

---

## 1. A rota por alavanca é impossível — e isso é o primeiro achado

Rodei a célula Pareto (`s_crit_loose=50 µm`, `k_loose_graded=1e-3`) nas duas curvas
com mais células Pareto. Ela remove **19 %** da rampa (β 0,576 → 0,465; R² 0,83 → 0,75),
não a rampa. Fui então buscar no `graded_scrit_alcance.json` a célula que de fato
**zera** o β — e ela é inutilizável:

| célula | β | σ_res | MAE | res.máx |
|---|--:|--:|--:|--:|
| nominal | +0,5763 | 0,1897 | 0,1543 | 0,4639 |
| Pareto (50 µm, 1e-3) | +0,4650 | 0,1612 | 0,1391 | 0,3500 |
| **β≈0 (50 µm, 1e-2)** | **+0,0098** | **0,2018** | **0,4573** | 0,7472 |

A célula que endireita o resíduo **triplica o MAE** (0,154 → 0,457) e o σ_res fica
*pior* que o nominal. No vocabulário do template de gate isto é **TROCA** com G2 < 0.

⇒ **Não existe estado do modelo em que a rampa saia e o resto fique intacto.** Medir
"o que sobra" nessa célula mediria a estrutura que a própria alavanca introduziu, não
o defeito do modelo. A caracterização tem de ser **algébrica**.

### 1a. Correção de um erro no relatório da atividade B

A §"Uma verificação interna que fecha o argumento" de `graded_scrit_alcance_resultado.md`
afirmava: *"Medido na célula que zerou o β: **0,111** (59 % do original)"*, e concluía que
sobrava σ_res ≈ 0,11. **Os dois números vêm de células diferentes:** a que zerou o β
(50 µm, 1e-2) tem σ_res = **0,2018**; a que tem σ_res = 0,1112 é (200 µm, 1e-2), com
β = −0,085 **e MAE 0,326**. A conclusão que dependia disso — *"o segundo defeito é
σ_res ≈ 0,11 e domina"* — **está errada**. O valor correto está na §2. O relatório da B
foi corrigido no mesmo commit.

## 2. Decomposição algébrica: rampa + curvatura + resto

Sobre o resíduo **nominal** (`e = pred − dado`, sem alavanca nenhuma), com o ciclo
normalizado em `s ∈ [0,1]`, ajustando polinômio de grau 1 e depois 2, e corrigindo o
σ por graus de liberdade (`σ = √(SS/(n−p))`, p = 2 e 3) — sem a correção, uma
quadrática sobre n=7 consome 3 dos 7 pontos e o σ sai viesado ~22 % baixo:

| curva | n | σ_res | −rampa | −curvatura | × limite | curvatura `a` |
|---|--:|--:|--:|--:|--:|--:|
| `chu…D0p4mm_F0_73kN_test8` | 31 | 0,1924 | 0,0836 | 0,0466 | 1,9 | +0,85 |
| `chu…D0p4mm_F0_49kN_test2` | 27 | 0,1897 | 0,0815 | **0,0229** | **0,9** | +0,94 |
| `chu…D0p4mm_F0_61kN_test7` | 31 | 0,1671 | 0,0735 | 0,0634 | 2,5 | +0,47 |
| `10_Yang_2023…0_2…` | 7 | 0,1452 | 0,0483 | 0,0184 | 0,7 | −0,43 |
| `rousseau2025_steel_t10` | 14 | 0,0981 | 0,0576 | 0,0248 | 1,0 | +0,57 |
| `karlsen2022_M30_HVtorqued_run14p2` | 7 | 0,0854 | 0,0313 | 0,0053 | 0,2 | +0,28 |
| `UFU_13A_first_preload_decay` | 254 | 0,0718 | 0,0224 | 0,0158 | 0,6 | −0,21 |
| `yang2019_M10_varamp_large_to_small` | 15 | 0,0580 | 0,0267 | 0,0267 | 1,1 | +0,08 |
| `chu…D0p5mm_F0_49kN_Ra1p6um_test9` | 25 | 0,0547 | 0,0269 | 0,0275 | 1,1 | −0,02 |
| `chu…D1p0mm_F0_49kN_test5` | 21 | 0,0436 | 0,0148 | 0,0135 | 0,5 | +0,08 |
| `bauer2024_M8_fig6_rep1` | 14 | 0,0430 | 0,0247 | 0,0133 | 0,5 | −0,21 |
| `li2022ti_axial_10Hz_full` | 7 | 0,0365 | 0,0231 | 0,0211 | 0,8 | −0,13 |
| `demir2024_amp0p3_F17p6_lk19p8` | 17 | 0,0292 | 0,0163 | 0,0072 | 0,3 | +0,17 |
| `chu…D1p0mm_F0_49kN_test6_repeat` | 23 | 0,0285 | 0,0145 | 0,0091 | 0,4 | +0,13 |
| `liu2022_fig8_multi_t4` | 7 | 0,0270 | 0,0161 | 0,0134 | 0,5 | +0,10 |
| `liu2022_fig8_multi_t1` | 7 | 0,0269 | 0,0127 | 0,0120 | 0,5 | +0,06 |

**Orçamento da dispersão (mediana, com a correção de DOF):** rampa **53 %** ·
curvatura **16 %** · resto **31 %**. (Sem a correção sairia 57/15/28 — a quadrática
parece explicar mais do que explica.)

**σ mediano depois de rampa + curvatura: 0,0171 = 0,7× o limite. 12 das 16 curvas
passariam a 3ª perna** se essas duas formas fossem capturadas (13 antes da correção
de DOF — a correção derrubou uma).

Este é o número que substitui o 0,11 do relatório anterior. A leitura muda de
*"sobra um defeito que domina e não sabemos o que é"* para **"sobram duas formas
nomeáveis, e a segunda é lisa"**: na `test2`, rampa + quadrática explicam **99 %** da
variância do resíduo (R² 0,83 → 0,99).

Resíduo por terços da `test2` (nominal): início −0,134 · meio −0,085 · fim +0,196 —
modelo **abaixo** do dado no começo e **acima** no fim: decai rápido demais cedo e
depois estagna enquanto o dado continua caindo. É a assinatura de **joelho adiantado**,
não de nível errado.

## 3. A curvatura do CHU ordena pela AMPLITUDE (9,9×)

| curva | D [mm] | F₀ [kN] | `a` | σ_res |
|---|--:|--:|--:|--:|
| `test8` | 0,4 | 73 | +0,85 | 0,1924 |
| `test2` | 0,4 | 49 | +0,94 | 0,1897 |
| `test7` | 0,4 | 61 | +0,47 | 0,1671 |
| `test9` | 0,5 | 49 | −0,02 | 0,0547 |
| `test5` | 1,0 | 49 | +0,08 | 0,0436 |
| `test6_repeat` | 1,0 | 49 | +0,13 | 0,0285 |

`|a|` médio em D = 0,4 mm: **0,75**; em D ≥ 0,5 mm: **0,08** ⇒ razão **9,9×**.

**Caveat honesto, e ele importa:** a correlação com F₀ sai **+0,546**, mas é
**confundida** — F₀ varia (49/61/73) só dentro do grupo D = 0,4, e todas as curvas de
D ≥ 0,5 têm F₀ = 49. *Dentro* do grupo D = 0,4 a ordem por F₀ é não-monotônica
(0,94 / 0,47 / 0,85), isto é, **sem tendência**. Com n = 6, a correlação com D
(−0,678) também não é significativa por si. O que sustenta o achado é a **razão de
grupo 9,9×** somada ao mecanismo da §4 — não o coeficiente de correlação.

## 4. O candidato tem nome, já existe no engine, e está desligado

`slip_onset_W` (gate de Hill sobre a perda dirigida por slip) — o mecanismo de
**incubação de estágio 1**. Estado atual: `slip_onset_W = 0.0` no default do engine e
**ausente** do cfg adotado do `CHU_2026` ⇒ gate ≡ 1, sem incubação.

**Predição declarada ANTES de medir** (é o que a torna testável): o acumulador é
`W_slip_acc += 4·µ·F₀·slip` por ciclo, então o número de ciclos para o gate abrir
escala como `W_onset/(4µF₀·slip)`. Em amplitude **pequena** o gate demora muito ⇒
platô longo, joelho tardio. Em amplitude **grande** abre no 1º ciclo ⇒ **inerte**.
Logo `|a|` deve **cair com D** — que é o medido.

**Discriminante:** um mecanismo de forma genérico, não dirigido por trabalho de slip,
**não** ordenaria pela amplitude. E a predição é falsificável na direção oposta: a
incubação também prevê que `|a|` caia com **F₀** (mais pré-carga ⇒ mais trabalho por
ciclo ⇒ gate abre antes). Os dados de D = 0,4 mm **não** mostram essa ordem. Isto é
uma **falsificação parcial declarada**, não um detalhe: ou o driver não é `4µF₀·slip`
como escrito, ou o efeito de F₀ está mascarado por outra dependência. O prereg tem de
carregar essa tensão, não escondê-la.

## 5. O que o pipeline deve fazer com isto

1. **A fila do σ_res tem estrutura, não é uma lista de 51 casos iguais.** 16 são DERIVA
   e nessas o orçamento é 53 % rampa + 16 % curvatura + 31 % resto. **12 das 16 fecham
   com duas formas**, o que é um alvo concreto — não "achar uma forma nova".
2. **`graded_scrit` continua COMPONENTE** (trata a rampa), e agora se sabe que a
   segunda componente é *lisa e nomeável*. O par a testar é **rampa + incubação**, não
   cada um sozinho.
3. **O teste discriminante já está escrito:** `|a|` deve ordenar pela amplitude. Rodar
   as 6 curvas do CHU com `slip_onset_W` varrido, medir `a` por curva, e confrontar
   com a tabela da §3 — a incubação passa se reduzir `a` **nas de D = 0,4 e ficar
   inerte nas de D = 1,0**. Se reduzir em todas por igual, o mecanismo alegado está
   errado mesmo que o MAE melhore.
4. **Não confundir com a §4.54a.** O fechamento por medição de 2026-07-28 (Chu =
   *form-limited* com prova em nível de lei) diz que **µ prescrito é inerte** — e isto
   não o contradiz: a forma que falta aqui é temporal (quando o joelho ocorre), não
   friccional. A prova de lei fecha a via de recolorir µ; esta abre outra.
5. **`slip_onset_W` precisaria de procedência** para virar canônico. Ele é energia
   acumulada de slip [J] — em princípio ancorável no ciclo em que o dado sai do platô,
   que é *lível da curva* (mesma classe de "ler em vez de fitar" do L24). Registrar
   como leitura, não como fit, se for adotado.

## 6. Achado lateral: a decomposição por canal **não** decide inércia de alavanca

A sessão paralela mediu, no mesmo dia e por instrumento independente (lei da variância
por estágio, `sigma_res_decomposicao_por_estagio.md`), que a 2ª forma é **curvatura** —
63 % das 84 curvas trocam de sinal entre estágios. **As duas medições concordam**, o que
é forte: projeção polinomial e partição de variância são instrumentos diferentes.

Mas ela também concluiu que em `test7`/`test8` o canal de afrouxamento está **morto**
(≤ 5 % da perda) e que por isso o `graded_scrit` seria *"inerte aqui, para qualquer valor
de parâmetro"*. **A sonda direta mede o contrário**, e o mecanismo do engano é
generalizável:

| | embedding | creep | wear | **rotacional** | total | σ_res | res.máx |
|---|--:|--:|--:|--:|--:|--:|--:|
| `test8` nominal | 0,0699 | 0,0427 | 0,3946 | **0,0120** | 0,5192 | 0,1924 | 0,3456 |
| `test8` +graded | 0,0699 | 0,0411 | 0,3752 | **0,1619** | 0,6481 | 0,1638 | 0,2382 |
| Δ | 0,0000 | −0,0015 | −0,0194 | **+0,1498** | | | |

O canal carrega **2,3 %** no nominal e cresce **13×** ao ligar a alavanca, passando a
25 % do total; **88 % de tudo o que se moveu** veio do próprio canal, não de
realimentação por F₀. (No `test7`: 2,9 % → 32 %, +0,2442 kN, 82 % do movimento.)

**A regra que isto estabelece:**

> Uma alavanca que **multiplica** um canal existente (`loose_arrest_floor`, `eta_loose`)
> está limitada pela fatia daquele canal — aí a decomposição **decide** a inércia. Uma
> alavanca que **substitui a lei de taxa** (`loose_rate_mode="graded_scrit"`) não está:
> ela pode inflar um canal quase nulo, porque mudar a lei é exatamente o que muda a
> fatia. **A fração medida no nominal é atribuição a posteriori de UMA
> parametrização, não cota de capacidade do canal.**

Isto refina o gotcha do repo (que já dizia que inércia de alavanca de canal "não é
decidível do config; confira a decomposição"): **a decomposição também não decide** —
para alavanca de lei de taxa, só a sonda de 2 pontos decide. Sem isso, 2 das 18 curvas
que a outra medição descartou por construção seguiriam descartadas, e uma delas
(`test8`) é justamente onde a alavanca melhora as **três** pernas.

Não invalida a conclusão maior daquela medição — **são pelo menos duas decisões de
forma**, e o alvo em embedding/creep/wear continua de pé. Corrige o roteamento de 2
curvas e o método de decidir inércia.

## 7. Reprodutibilidade

```bash
# a decomposicao (segundos, le o store; nao simula)
py -3.12 New_Theory/chu_segundo_defeito.py

# a sonda por alavanca que motivou a correcao da secao 1a (~15 min)
py -3.12 New_Theory/graded_scrit_alcance.py
```
