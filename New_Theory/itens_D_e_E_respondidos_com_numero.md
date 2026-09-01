# Itens **D** e **E** — respondidos com número, e a resposta é **não** nos dois

**2026-08-15 (22:2x)** · só-leitura · **nada executado** · store `20be19aabe11`, censo
**143/205**, camadas 23/18/5/15/1, fila **0 · 5 de 21**.

Assinatura do professor às 22:22 (*"assine e continue"*) sobre os itens que restam e são meus
(o **Q** é área ativa da sessão paralela). Os dois pediam decisão; nenhum tinha sido medido
**no que decide**.

---

## 1. Item **D** — calibrar 8 `per_case` no `CHU_2026`: **NÃO**

O item já se auto-descrevia como *"o oposto da parcimônia"*, mas ninguém mediu **o que
compraria**. Medido:

| curva | MAE (×lim) | res.máx (×) | σ (×) | estatuto |
|---|---:|---:|---:|---|
| `test1` | 0,07 | 0,08 | 0,11 | ✅ tripé |
| `test5` | 0,42 | 0,39 | 0,62 | ✅ tripé |
| `test6_repeat` | 0,56 | 0,42 | 0,41 | ✅ tripé |
| `test9` | 0,92 | 1,05 | **1,86** | exceção assinada |
| `test3` | 1,60 | 1,14 | 1,03 | exceção assinada |
| `test4` | 2,70 | 2,26 | **4,23** | exceção assinada |
| `test7` | 3,00 | 2,70 | **5,66** | exceção assinada |
| `test2` | 3,13 | **5,26** | **6,46** | exceção assinada |
| `test8` | 3,23 | 3,93 | **6,55** | exceção assinada |

**3 de 9 no tripé — e as 6 fora são TODAS exceção assinada**, com prova em **nível de lei**
(§4.54a: µ medido prescrito ≈ inerte; wear disp-mode é Archard, sem µ).

⇒ os 8 conjuntos `per_case` perseguiriam curvas **já contabilizadas com procedência**, e o
fariam a partir de erros de **até 6,55×** o limite. Fechar a `test8` (σ 6,55×) com constantes
por curva não é calibração — é ajuste de curva, e destrói exatamente a afirmação que é a
manchete do método (*"3 números fitados no dataset inteiro"*).

**Ganho máximo teórico:** +6 no censo. **Custo:** 8 conjuntos de constantes para 9 curvas.
⇒ **recusado, com número.**

## 2. Item **E** — `YANG_2021` / `YANG_2023`: **NÃO**, e por dois motivos distintos

O item mistura duas coisas que precisam de respostas diferentes.

### 2a. `YANG_2023` — remover **não é** substituir

| fonte | tripé | erros |
|---|---:|---|
| `YANG_2023_IJPEM` | **0 de 9** | MAE até **4,77×**, σ até **8,47×** |
| `YANG_2023_AME` | **0 de 1** | MAE **7,75×** |

A digitalização **nunca foi conferida** — o PDF está sob paywall. Erros de 2× a 8,5× numa
fonte não verificável são sinal de **dado**, não de modelo, e a instrução permanente do
professor diz: *"não quero carta a autores, **substitua** os artigos que não tiver acesso"*.

⚠️ **Mas o custo medido de simplesmente REMOVER decide contra:**

| | tripé | taxa |
|---|---|---:|
| hoje | 143/205 | **69,8 %** |
| sem `YANG_2023` | 143/195 | **73,3 %** |

⇒ **+3,6 pontos percentuais sem consertar uma única curva.** E **6 das 10 já são
`declarada`** — têm procedência registrada; removê-las apaga trabalho contabilizado e infla
a manchete de graça.

⇒ **substituir exige uma fonte NOVA**, e eu não tenho candidata. Remover sem repor seria
transformar uma instrução de *qualidade de dado* num *aumento cosmético do número*. **Não
executo.**

### 2b. `YANG_2021` — ⛔ **ERRATA: a forma NÃO é nova, ela JÁ ESTÁ ADOTADA**

> ⚠️ **Corrigido em 2026-08-15 22:5x.** Este parágrafo dizia que o `YANG_2021` *"pede
> forma nova de engine (perda sustentada sob stick), fora do mandato autônomo"*. **Está
> errado.** A sessão paralela mediu (`f6a8eed`) e eu **verifiquei independentemente**:
>
> * `gth_k = 1,5e-07` **está adotada** no `YANG_2021` e chega às curvas como override
>   efetivo — a forma de stick **existe e está em uso**;
> * **8 de 8 curvas são 100 % STICK** (slip = 0 em *todos* os ciclos, mediana 0).
>
> ⇒ o problema **não** é falta de forma. É que **uma constante compartilhada não serve à
> própria fonte**: mexer no `gth` para 5e-7 fecha 2 abertas e **quebra 2 protegidas** —
> **net zero** em 6 células (medição deles).

**O quadro combinado, com três rotas medidas e fechadas por dois instrumentos
independentes:**

| rota | veredito | de quem |
|---|---|---|
| **forma de stick** (`gth`) — já adotada | ⛔ **net zero**: fecha 2, quebra 2 | sessão B |
| **constante** (`C_creep` que fecha a `r1`) | ⛔ **refutada pelo controle**: `r2` e `r3` saem, pior ΔMAE **+0,0283** | minha |
| **desculpa de scatter** para a `r1` | ⛔ **recusada pela medição**: réplicas concordam a σ 0,0129/0,0099 e o modelo está em 0,0268 — **2,1× fora** | sessão B |

⇒ **o veredito é mais forte do que "falta forma"**: a forma está lá, a constante não
generaliza dentro da própria fonte, e a curva não é *scatter-bound*. Isso não é item de
assinatura de forma — é diagnóstico de que **a lei de stick vigente não tem a dependência
que separa estas curvas**.

⚠️ E fica registrado o que EU errei: afirmei *"forma nova"* sem checar se a forma já
estava adotada na fonte. Bastava ler o `adopted_config` — que é o que a checagem de
verificação fez em 30 segundos.

**Estado da fonte:** 3 de 8 no tripé; a `r1` a **7 %** do limite de σ (1,07×).

⚠️ **Este parágrafo continha a versão errada e foi substituído pela errata acima.** O que
ele afirmava — *"o que resta é forma nova, fora do mandato"* — está **falsificado por
medição**: a forma existe, está adotada, e mexer nela dá net zero.

## 3. O que fica na mesa

| item | veredito |
|---|---|
| **D** | ⛔ **recusado com número** — 8 conjuntos para perseguir 6 curvas já resolvidas, a até 6,5× |
| **E-dado** (`YANG_2023`) | ⛔ **remover recusado** (+3,6 pontos de graça); **substituir aguarda fonte candidata** |
| **E-forma** (`YANG_2021`) | ⛔ **3 rotas medidas e FECHADAS** por 2 instrumentos: forma (`gth`, já adotada) dá **net zero**; constante (`C_creep`) **refutada pelo controle**; scatter **recusado pela medição** (2,1× fora). Não é falta de forma — é a lei de stick vigente sem a dependência que separa estas curvas |
| **Q** | 🔄 sessão paralela, ativa |

⇒ **os três abertos passam a ter veredito medido.** Nenhum vira trabalho meu esta noite, e
isso é o resultado — não a ausência dele.

## 4. O que eu NÃO fiz, de propósito

Não removi curva, não calibrei `per_case`, não construí forma. As três coisas subiriam o
número publicado; nenhuma consertaria o modelo. ⚠️ A que mais tenta é a remoção do
`YANG_2023`: **+3,6 pontos com uma linha de código**, e é exatamente por isso que ela precisa
de fonte substituta antes, não depois.

## Reprodutibilidade

Sondas inline no corpo do commit; usam `T.classificar`, `T.piso_da_fonte`, `rh.limite_sres`,
`rh.sres_para_censo`, `rh.caso_comparavel` e o `_censo()` canônico do
`test_meta_numeros_nao_envelhecem` — nenhuma reimplementa regra.
