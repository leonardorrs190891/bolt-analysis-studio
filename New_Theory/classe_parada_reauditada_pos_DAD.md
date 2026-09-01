# `classe_parada` re-auditada depois da D-AD — o item N encolheu, e apareceu uma **armadilha latente**

**2026-08-15 (tarde)** · só-leitura · **nada reclassificado** · store `20be19aabe11`, censo
**143/205**, fora **62**, fila form-limited **0**.

---

## 1. Por que re-medir

O item N foi escrito quando a camada tinha **8 membros** e afirmava que **3** não carregavam a
assinatura da classe. Desde então a **D-AD** (`s1_amp_gate` no `LIU_2025`) fechou `amp0p25` e
`amp0p3` ⇒ a camada foi a **6**. §4.43: o enunciado do item mudou debaixo dele.

## 2. O item N hoje: **2 de 6**, não 3 de 8

Discriminante da campanha (`ρ(resíduo, N) ≥ +0,7` **ou** razão terminal `> 2`):

| curva | ρ | razão | assinatura |
|---|---:|---:|---|
| `liu2025_M16_amp0p8` | −0,52 | **0,53** | ⛔ **SEM** — e **invertida** (erro se forma *cedo*) |
| `yang2019_M10_amp0p4_5Hz` | +0,39 | **0,70** | ⛔ **SEM** — também invertida |
| `liu2025_M16_fig2_single` | +0,96 | 6,85 | ✅ |
| `yang2021_amp0p5mm_ax8kN` | +0,89 | 19,23 | ✅ |
| `yang2021_amp0p6mm_ax8kN_r1` | +0,63 | 35,08 | ✅ |
| `yang2021_amp1p0mm_ax2kN` | +1,00 | 17,75 | ✅ |

⇒ **a terceira curva do item N saiu por MÉRITO**, não por reclassificação. O item ficou menor
e mais nítido.

## 3. ⚠️ `YANG_2019` é falso positivo **INTEIRO** — padrão P-7 exato

A camada atribui **por FONTE** (`if fonte in _FONTES_CLASSE_PARADA`), e a **P-7 (assinada e
executada em 2026-08-08)** já removeu `LU_2024` e `SUN_2025_CRIMP` por serem *"falsos positivos
PUROS"*, usando **este mesmo discriminante de sinal**.

| fonte | membros | com assinatura | leitura |
|---|---:|---:|---|
| `YANG_2021` | 3 | **3** | toda com assinatura |
| `LIU_2025` | 2 | 1 | mista |
| **`YANG_2019`** | **1** | **0** | ⛔ **falso positivo inteiro** |

⇒ há uma proposta **de mesmo formato que um precedente assinado**, e mais estreita que a do
item N: remover `YANG_2019` de `_FONTES_CLASSE_PARADA`, em vez de trocar a atribuição de
por-fonte para por-curva.

## 4. ⚠️ O achado que eu não procurava: **2 das 5 entradas são INERTES**

| fonte na lista | curvas | no tripé | na `classe_parada` | capturadas ANTES | estado |
|---|---:|---:|---:|---:|---|
| `CHU_2026` | 9 | 3 | **0** | 6 (`excecao_assinada`) | **INERTE** |
| `JCSR_2023` | 5 | 4 | **0** | 1 (`excecao_assinada`) | **INERTE** |
| `LIU_2025` | 7 | 5 | 2 | 0 | ativa |
| `YANG_2019` | 5 | 4 | 1 | 0 | ativa |
| `YANG_2021` | 8 | 3 | 3 | 2 | ativa |

A camada **declara** alcance de 5 fontes e **tem** alcance de 3.

**Isto não é erro hoje — é armadilha latente**, e a campanha tem histórico exato dela: já
foram **6 retratações de exceção**. O `CHU_2026` carrega **6 exceções assinadas**. Se qualquer
uma for retratada, a curva **não vira trabalho visível**: ela escorrega em silêncio para
`classe_parada` e passa a contar como *"fechada com procedência"* — um estatuto que ninguém
decidiu conceder a ela.

⇒ **a retratação de exceção, que deveria ser custo, viraria troca de rótulo.** É a mesma
estrutura do defeito que o item O documenta em outra camada.

## 5. O que **não** estou fazendo

Reclassificação de camada **exige assinatura**. Nada foi tocado: `regra_de_parada_triagem.py`
e `report_html.py` intactos, censo **143/205** inalterado.

Vai para a mesa como **duas propostas separadas**, porque têm naturezas diferentes:

| proposta | formato | precedente | custo medido |
|---|---|---|---|
| **N′** — remover `YANG_2019` da lista | idêntico à P-7 | ✅ P-7 (2 fontes removidas) | ver tabela abaixo — **não cria trabalho** |
| **P** — tornar visível a inércia de `CHU_2026`/`JCSR_2023` | guarda, não reclassificação | — | zero hoje; impede o escorregamento futuro |

**Custo da N′, medido rodando o `regra_de_parada_triagem.main()` canônico com e sem a fonte:**

| | hoje | sem `YANG_2019` | Δ |
|---|---:|---:|---:|
| **tripé** | **143** | **143** | **+0** |
| `classe_parada` | 6 | 5 | −1 |
| `indecidivel_sem_piso` | 15 | 16 | +1 |
| **`form_limited`** | **0** | **0** | **+0** |

⚠️ **Eu havia escrito aqui que a fila form-limited iria a 1. Está errado e foi a medição que
pegou.** A curva não cai em `form_limited`: cai em **`indecidivel_sem_piso`**, porque o
`YANG_2019` **não tem piso medido**. Ou seja, a proposta **não gera trabalho** — ela troca um
estatuto que afirma *"encerrada pela classe, aguardando dado novo"* por outro que afirma
*"não julgável, falta réplica"*. O segundo é honesto sobre o motivo; o primeiro faz uma
afirmação sobre a **forma** do defeito que esta curva **não exibe** (razão terminal 0,70 — o
erro se forma cedo, não tarde).

⚠️ E fica dito o que a medição **não** decide: com MAE **1,93×** e σ **3,04×**, chamar a curva
de *"indecidível"* também é generoso. Qual dos dois rótulos ela merece é decisão de estatuto,
não de sonda.

⚠️ A **P** pode ser feita **sem mexer em estatuto nenhum**: basta uma guarda que falhe quando
uma fonte da lista tiver **zero membros** na camada *e* exceções assinadas — o que denuncia a
sombra antes de ela importar. Isso é teste, não reclassificação; mas como toca a semântica da
camada, fica como proposta.

## 6. ⚠️ Errei a MESMA coisa TRÊS vezes nesta sessão — e sempre por reimplementar a seleção

| # | o que fiz | o que deu | quem denunciou |
|---|---|---|---|
| 1 | classifiquei **todas** as curvas, não só as `fora` | **25** membros contra 6 | a divergência 25 ≠ 6 |
| 2 | passei `exc = _EXCECOES ∪ _DECLARADAS` | 18 declaradas viraram "exceção" (35 vs 22) | `declarada` sumiu da tabela |
| 3 | `continue` quando `sd is None` | 6 curvas evaporaram (`fora` 56 vs 62) | a soma não fechava |

O canônico é: só as `fora`; `exc = set(rh._EXCECOES)` **apenas** (as `_DECLARADAS` são um ramo
**dentro** de `classificar`); e curva com `σ` não julgável **fica em `fora`**, não é descartada.

⚠️ **Os três erros são invisíveis na contagem de `classe_parada`** — ela deu 6 nos três casos,
porque os ramos de exceção e declaração precedem o dela de qualquer jeito. Um número certo no
meio de uma tabela errada não valida a tabela.

**O que finalmente funcionou foi parar de replicar**: rodar `T.main()` com
`_FONTES_CLASSE_PARADA` monkeypatchado e comparar as saídas. Custa 2 execuções e usa
exatamente o caminho de código que publica o número.

⇒ **regra:** para medir efeito de mudança de camada, **execute o script canônico duas vezes**;
não reescreva o laço de seleção. O cron manda não reimplementar a *regra* — isto mostra que a
**seleção** é tão perigosa quanto ela.

## Reprodutibilidade

Sondas inline no corpo do commit. Usam `T.classificar`, `T.piso_da_fonte`, `rh.limite_sres` e
`rh.sres_para_censo` — nenhuma reimplementa regra; a **seleção** das `fora` replica o laço de
`regra_de_parada_triagem.main` (foi exatamente ela que eu errei na 1ª tentativa).
