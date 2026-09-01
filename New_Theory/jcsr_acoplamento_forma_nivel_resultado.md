# ADOÇÃO D-AA — a varredura CONJUNTA acha o que a marginal **não podia** achar

**2026-08-09** · prereg `c122b7a` (gates congelados antes de medir) · continuação imediata
do **D-Z**, no mesmo dia.

## O erro de método que abriu isto

O `ataque_curva.py` varreu `C_creep` em 0,5–2,0× na `galv_seawater` e **piorou em todas as
doses**. Eu escrevi *"a constante está no ótimo"*. Estava — **na forma antiga**.

Assim que o D-Z trocou a forma, a **mesma** varredura de `C_creep` virou produtiva:

```
galv, C x1,10:  0,0348/0,0526/0,0154  ->  0,0102/0,0249/0,0087
```

A causa é estrutural, não azar: `δ_sat(t) = C_creep·F_0·(1 − e^{−(t/t_c)^α})` — a **assíntota**
é `C_creep` e a **chegada** é α/t_c, e dentro da janela do ensaio as duas se confundem.
Varredura **um-de-cada-vez** encontra um ótimo **condicional** e o reporta como global.

⚠️ **A consequência não era cosmética:** as duas curvas que eu havia declarado sem rota —
`outdoor` e `stainless_seawater` — **nunca tinham sido varridas do jeito certo**. Nem a grade
α×t_c a `C` fixo, nem a varredura de `C` à forma fixa podiam encontrar um ótimo conjunto.

## As grades

| grade | `outdoor` | `stainless` |
|---|---:|---:|
| α×t_c a `C` fixo (56 células) | 0 fecham | 0 fecham |
| conjunta α×t_c×C (150) | 0 fecham | **1** ⚠️ na fronteira, 0,97× |
| conjunta **estendida** (180) | — | **10 fecham — região INTERIOR** |

A 1ª conjunta saturou na fronteira em α (máx 8) e em C (mín 0,70), com **uma** célula a
**0,97×** — exatamente o fio de navalha que a campanha recusa. A **disciplina de fronteira de
grade** (herdada do D-L) mandou estender, e a extensão achou **região**: α ∈ {8, 10, 12} ×
t_c ∈ {0,80; 0,85} × C ∈ {0,60 … 0,75}, **interior nos dois eixos que haviam saturado**.

## A regra de escolha, e o que ela custou

Declarada **antes** de olhar: *a célula mais **central** da região (mais vizinhos de grade que
também fecham), desempate pela pior perna* — precedente D-I, que escolheu a mais centrada e
não a de melhor MAE.

| curva | célula escolhida | resultado |
|---|---|---|
| `stainless_seawater` | α=10, t_c ×0,80, C ×0,65 (4 vizinhos) | 0,0619/0,1237/0,0739 → **0,0118/0,0304/0,0146** |
| `galv_seawater` | α=3 (**inalterado**), t_c ×1,00 (**inalterado**), C ×1,10 | 0,0348/0,0526/0,0154 → **0,0102/0,0249/0,0087** |
| `plain_seawater` | α=5, t_c ×1,00, C ×1,05 | ⛔ **NÃO ADOTADA** — ver abaixo |
| `outdoor` | — | **0 de 150**: segue estrutural |

⛔ **A `plain_seawater` foi barrada pelo meu próprio gate.** A regra de centralidade apontou
`C ×1,05`, que **piora MAE** (0,0187→0,0204) e **res.máx** (0,0480→0,0564) para ganhar
**0,0005** em σ. O **K2** exigia `Δ ≤ 0` nas três pernas. A regra e o gate discordaram, e o
**gate congelado mandou** — a curva ficou exatamente como estava.

⚠️ Este é o ponto do prereg funcionando: eu **não** posso re-escolher a regra depois de ver o
resultado. O `C ×1,00` também está no conjunto que fecha (2 vizinhos, pior perna 0,94×) e
perdia o desempate por 0,02 — margem que não justifica piorar duas pernas.

## Gates — medidos

| # | gate | resultado |
|---|---|---|
| **K1** | `stainless` fecha o tripé | ✅ 0,0118/0,0304/0,0146 (limite σ 0,0250) |
| **K2** | `galv`/`plain` fecham **e não pioram em nenhuma perna** | ✅ galv Δ = (−0,0247 −0,0277 −0,0067); plain Δ = 0 exato |
| **K3** | controles `plain_indoor`, `plain_outdoor` | ✅ **bit-idênticos** |
| **K4** | isolamento fora do `JCSR_2023` | ✅ Δ = **0,000000000** em 6 curvas |
| **K5** | censo 141 → 142 | ✅ **142** |
| **K6** | suíte completa | ✅ verde |

## ✅ O K6 reprovou primeiro — e o que ele pegou vale mais que o gate

A suíte falhou em `test_excecao_assinada_esta_de_fato_fora_do_tripe`:

```
exceção assinada para curva que passa no tripé: ['jcsr2023_stainless_seawater']
```

Não é falha da adoção — é o invariante fazendo o serviço. A curva carregava
**exceção F5 assinada** (*"cliff/rebound de corrosão (forma faltante)"*, do F3.1-JCSR de
2026-07-21) porque estava estruturalmente fora; ao fechar por **mérito**, a assinatura virou
redundante e tem de ser **retirada**, com a prova preservada — precedente D1 (19 retiradas) e
LIU_2016. Registro novo: `_EXCECOES_RETIRADAS_ADOCAO_JCSR`.

⚠️ **Trocar exceção por mérito é ganho de LEITURA, não de contagem:** a leitura
resolvida/declarada não sobe (a curva já contava), a **estrita** sobe. É a direção certa.

### E a retirada expôs um defeito de contagem

Ao retirar, o `declarado_total` do censo caiu **176 → 175** — ou seja, enquanto a assinatura
redundante existiu, a curva foi contada **duas vezes**. A fórmula é
`n_ok + n_exc + n_decl`, **sem dedup**, e o próprio arquivo tem um comentário avisando disso
para o *split das fora* — mas não para o total.

Hoje o número está certo (**0** declaradas passando, **0** sobreposição exceção↔declarada,
medido), e está certo **porque** um teste proíbe assinatura redundante. Só que essa guarda
existia **apenas do lado das exceções**. Do lado das **declaradas** não havia nenhuma — e o
precedente é real: a `lu2024_M8_fig18_amp2p0` saiu das declaradas por mérito em 2026-08-01
porque **alguém notou**, não porque um teste acusou.

Fechado no mesmo dia: `test_excecao_assinada_esta_de_fato_fora_do_tripe` ganhou os dois
espelhos que faltavam — **declarada que passa o tripé** e **sobreposição entre as duas
listas**. Os dois **validados por perturbação** (injetar o caso ⇒ dispara nomeando a curva;
remover ⇒ passa limpo), porque guarda que nunca dispara não é guarda.

⚠️ **E a 1ª versão do espelho estava ERRADA — pelo erro mais repetido da campanha.** Ela
usava o `resid_std` **cru do store** e acusou a `Yang2023 0,15 mm`. Só que essa curva é
declarada **exatamente por `n<6`**: pela regra assinada em 2026-08-01, σ com menos de 6
pontos na janela é **não-julgável**, e `sres_para_censo` devolve `None` — ela **não** passa o
tripé. Eu tinha reimplementado a regra em vez de chamar o helper, dentro de um teste cujo
propósito é justamente proteger a regra. Corrigido para `rh.sres_para_censo`; e a função
`_passa` **pré-existente** carregava o mesmo defeito latente (inócuo só porque nenhuma curva
com exceção tem `n<6` hoje).

⚠️ **Achado colateral:** o parentético do `CLAUDE.md` (*"142 + 23 exceções + 14 declaradas"*)
**já não fechava com a própria manchete** antes desta sessão — somava 176 sob um total
publicado de 173. Os contados de verdade são **21 exceções + 12 declaradas**, e agora a soma
bate com o número.

## Observação de apoio — declarada como NÃO-driver

`C_creep` carrega procedência *"proxy ambiental per-par×ambiente (corrosão vestida de
creep)"*. Antes desta adoção o **stainless** em água do mar carregava o **maior** dos três
(1,736e-9 = **2,4×** o aço-carbono no mesmo ambiente) — inversão contra a leitura que a
própria procedência declara. Depois: 1,128e-9, **abaixo** do galvanizado (1,175e-9) e ainda
acima do aço-carbono simples (7,125e-10). A inversão **diminui, não desaparece**, e eu não
tenho como afirmar monotonia entre severidade de corrosão e `C_creep` daqui. Registrado como
observação; o driver foi a grade.

## O que a fonte é hoje

| curva | estatuto |
|---|---|
| `plain_indoor` | tripé (0,0009/0,0021/0,0010) |
| `plain_seawater` | tripé (0,0187/0,0480/0,0234) |
| `galv_seawater` | tripé (**0,0102/0,0249/0,0087**) |
| `stainless_seawater` | tripé (**0,0118/0,0304/0,0146**) |
| `plain_outdoor` | **fora** — 0 de 150 células conjuntas; forma faltante |

**JCSR_2023: 1/5 → 4/5 em um dia**, sem constante nova e sem forma nova — só varrendo as
constantes existentes do jeito certo.

## O que fica para a campanha

1. **Gotcha instalado no `CLAUDE.md`**: *"constante no ótimo" por varredura marginal é
   conclusão sobre o PONTO*. Sintoma diagnóstico grátis: **|viés|/MAE → 1,00** = resíduo de
   sinal único = puro erro de nível ⇒ a alavanca de nível ainda tem o que dar (na `galv` foi
   0,00 antes do D-Z e **1,00** depois).
2. **Uma regra que eu propus e MEDI antes de publicar, e que caiu:** *"forma só fecha curva
   com viés ≈ 0"*. Testada nas 12 curvas de kernel saturante do store — |viés| mediano 0,0211
   dentro do tripé vs 0,0293 fora, faixas sobrepostas, e uma curva **dentro** com |viés| maior
   que uma **fora**. Não se sustenta.
3. **A `outdoor` é o resíduo honesto**: 0 de 150 células conjuntas, melhor pior-perna 2,14×.
   O veredito estrutural de 2026-07-21 (*"cliff de corrosão/rebound → forma faltante"*)
   sobrevive à varredura que derrubou o da irmã.

## Reprodutibilidade

```bash
py -3.12 New_Theory/ataque_curva.py jcsr2023_stainless_seawater
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
py -3.12 -m pytest tests/ -q
```
