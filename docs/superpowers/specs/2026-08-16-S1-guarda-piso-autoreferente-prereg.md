# ✅ EXECUTADO — ramo **ADOTADO**, gates **6/6**, predições **4/4**

> **Fechado 2026-08-16 (20:0x).** Arquivo: `tests/test_piso_lido_do_dado_nao_excede_a_curva.py`
> (5 testes). Suíte **988 → 993 passed · 1 skipped** (= +5, exatamente os novos).
> Config e store **INTOCADOS**; fingerprint segue `7a60cacb72de`, censo **144/205**.
>
> | gate | resultado |
> |---|---|
> | **G1** passa hoje | ✅ **5** alegações, **0** violações |
> | **G2** perturbação positiva | ✅ reconstruindo o estado pré-R2 da `fig7d` (piso 0,137 + rótulo antigo) **em memória**, a guarda dispara e cita 0,137 vs L24 **0,0000** |
> | **G3** unilateralidade | ✅ perturbação com piso 0,01 na `fig3` (L24 0,1936) **não** dispara |
> | **G4** lê o cru | ✅ perturbado: inserir `rec.metric_data` no arquivo **faz o teste estrutural falhar** |
> | **G5** inércia | ✅ censo, fingerprint, config e store idênticos; suíte sem falha nova |
> | **G6** mensagem útil | ✅ nomeia curva, grupo, piso, L24 e as **duas** saídas (corrigir valor **ou** re-rotular, como o R2 fez) |
>
> ⚠️ **Dois defeitos meus achados durante a execução, ambos "teste que não testa":**
> (a) o teste estrutural do G4 **acusava a si mesmo** — a própria mensagem de erro continha
> a literal `metric_data`; corrigido buscando o **acesso a atributo** (`.metric_data`), que
> é como código real o usaria. (b) o teste de unilateralidade nascera **vazio**: as 5
> alegações estão todas levemente *acima*, então a lista "abaixo" era vazia e ele assertava
> sobre nada; virou perturbação explícita.

---

# PREREG — item **S**, rota **S1**: guarda auto-referente do `loose_arrest_floor`

**2026-08-16 (19:3x)** · **gates congelados neste commit** · store `7a60cacb72de`,
censo **144/205** · assinatura do professor às 19:27 (*"confirme e assine tudo e prossiga"*).

---

## 1. A regra

> Piso cujo **rótulo de procedência afirma `lido-do-dado`** não pode ficar **ACIMA** da
> leitura L24 (`arrest_floor_from_curve`) do **CSV cru** da própria curva, além de uma
> tolerância de **0,02**.

**A referência é a própria curva** — não precisa de banda de literatura. É por isso que
esta é a única das três rotas do item S executável sem âncora nova: a S2 exigiria bandas
publicadas que eu teria de **buscar ou inventar**, e a S3 exige estrutura de par
tribológico que o repositório não tem.

⚠️ **A regra é UNILATERAL.** Piso **abaixo** da leitura é escolha **conservadora** (o piso
segura menos do que o dado permitiria) e **não** dispara. Só o excesso mente, porque só o
excesso compra métrica.

## 2. Baseline MEDIDO — e ele corrige dois números meus

Resolvendo o grupo que **de fato governa** cada curva via `rn._adopted_for(source, case_id,
bolt)` (o mesmo resolvedor do runner):

| | n |
|---|---:|
| curvas cujo grupo governante alega `lido-do-dado` p/ o piso | **5** |
| que a guarda **reprovaria hoje** | **0** |

| curva | grupo | piso | L24 do cru | Δ |
|---|---|---:|---:|---:|
| `eccles2010_fig3` | `ECCLES_2010_fig3` | 0,1940 | 0,1936 | +0,0004 |
| `eccles2010_fig7a` | `ECCLES_2010_fig7a` | 0,2160 | 0,2130 | +0,0030 |
| `eccles2010_fig7b` | `ECCLES_2010_fig7b` | 0,2320 | 0,2285 | +0,0035 |
| `eccles2010_fig7c` | `ECCLES_2010_fig7c` | 0,1820 | 0,1800 | +0,0020 |
| `eccles2010_fig8c` | `ECCLES_2010_fig8c` | 0,1520 | 0,1495 | +0,0025 |

⚠️ **DUAS ERRATAS minhas, das medições de 13:4x e 18:0x:**

1. *"9 grupos alegam"* / *"21 curvas com rótulo `lido-do-dado`"* / *"7 abaixo, 2 acima"* —
   **inflados**. Eu casava o grupo por **prefixo da fonte**, então toda curva de uma fonte
   com **algum** grupo alegando entrava na conta. Com o resolvedor canônico são **5**.
   (Mesma classe do proxy "mediana da fonte" que eu já retratara hoje de manhã.)
2. Uma medição intermediária mostrou `fig7d`/`fig8a` **ainda violando** — falso pelo mesmo
   motivo: o **R2 já trocou os rótulos delas**, e o prefixo as trazia de volta.

⇒ **a guarda nasce com 0 violações, e isso é CORRETO** — o R2 consertou as duas que
existiam. Um teste que passa por mérito no dia em que nasce **tem** de ser validado por
perturbação, não por captura ao vivo.

## 3. GATES — congelados

| # | gate | critério | bloqueante |
|---|---|---|:--:|
| **G1** | passa hoje | a guarda **não falha** no config atual; conta **5** alegações e **0** violações | ✅ |
| **G2** | **perturbação positiva** | restaurando o rótulo `lido-do-dado` **e** o valor 0,137 na `ECCLES_2010_fig7d`, a guarda **FALHA nomeando-a** e citando piso 0,137 vs L24 0,0000 | ✅ |
| **G3** | **unilateralidade** | um piso **abaixo** da leitura (perturbação: 0,01 na `fig3`, contra L24 0,1936) **NÃO** dispara | ✅ |
| **G4** | **lê o CRU** | a guarda usa `load_full_curve` + `arrest_floor_from_curve`; **nenhuma** referência a `metric_data` no arquivo (foi lê-lo que gerou o defeito de origem) | ✅ |
| **G5** | inércia | censo **144/205** e fingerprint **`7a60cacb72de`** inalterados (um teste não toca física); suíte completa sem falha nova (baseline **988 passed / 1 skipped**) | ✅ |
| **G6** | mensagem útil | a falha nomeia curva, grupo, piso, leitura L24 e aponta as 2 saídas (corrigir o valor **ou** re-rotular como o R2 fez) | ✅ |

**Ramos:** `ADOTADO` · `REPROVADO` · **`INCONCLUSIVO`** (p.ex. a perturbação do G2 não fazer
a guarda falhar ⇒ o teste não testa nada).

## 4. Predição registrada

1. G1 passa com **5 / 0** — se aparecer violação hoje, algo mudou desde 19:3x e o prereg
   precisa ser re-medido antes de executar.
2. A perturbação do G2 produz falha citando **0,137 vs 0,0000**.
3. A perturbação do G3 **não** produz falha (regra unilateral).
4. Censo e fingerprint **não se movem** — este passo não escreve config nem store.

## 5. O que este passo NÃO é

Não é adoção de constante, não é forma de engine, não é reclassificação de camada. É uma
**guarda de teste** que torna falsificável uma classe de afirmação que hoje não é — e cobre
exatamente **1 das 29** constantes que o item S mediu como infalsificáveis. As outras 28
seguem sem guarda, e o item S permanece aberto nas rotas S2/S3.
