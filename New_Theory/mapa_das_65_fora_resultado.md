# Mapa das 65 fora — **toda** curva sem estatuto tem defeito nomeado e decisão que a cobre

**2026-08-07** · `mapa_das_65_fora.py` (só-leitura) · store `d9a680664797` ·
censo **140/205**.

> ## ⚠️ ATUALIZADO em 2026-08-07 (tarde) — o classificador tinha um BURACO
>
> `p7_orfas_resultado.md`. O teste do relógio media o cruzamento de **0,90
> fixo**, e em **12 das 65** o **dado nunca cai a 90 %** ⇒ razão `n/a` ⇒ a curva
> **não era testada**. Ela não *passava*: o teste **não rodava** — e o
> `classe_parada`, atribuído por FONTE, a absorvia em silêncio. Mesma classe do
> ramo `INCONCLUSIVO` do charter, num classificador em vez de num prereg.
>
> Conserto conservador (0,90 quando o dado o alcança; metade da queda total
> quando não): **9 curvas mudaram de defeito**.
>
> | mudança | curvas |
> |---|---:|
> | `classe parada` → **sub-perda** (o modelo nunca alcança o dado) | **5**, todas `YANG_2021` |
> | `classe parada` → **relógio E1** | 1 (`liu2025_M16_amp0p25`, razão **0,032**) |
> | `sem piso`/`não classificado` → defeito nomeado | 3 |
>
> **Duas consequências que mudam a leitura:**
>
> * o `YANG_2021` ser *"coerente com a classe"* fica **confirmado e afiado** — o
>   defeito dele não é "retém demais", é **"nem chega ao nível do dado"**;
> * a categoria **"dado"** (falta réplica, nenhuma rota de modelo) ficou
>   **vazia** ⇒ a frase *"a 31ª precisa de dado que não existe"*, abaixo, está
>   **superada**: **as 31 têm defeito do lado do modelo nomeado**.
>
> ~~Contagem vigente das sem estatuto: **P-7 16 · P-9 8 · P-13 7**.~~
>
> ⚠️ **Re-corrigida na mesma tarde** (`censo_por_proposta_resultado.md`): a classe
> `sub-perda` apontava para a **P-7**, e era **erro meu de atribuição** — a P-7 é
> sobre reclassificar a camada `classe_parada`, sem relação com *"o modelo não
> alcança o dado"*. Reapontada para a **P-14**. Contagem vigente:
>
> | decisão | abertas | viés + | viés − |
> |---|---:|---:|---:|
> | **P-7** | **12** | 7 | 5 |
> | **P-9** | 8 | 2 | **6** |
> | **P-13** | 7 | **6** | 1 |
> | **P-14** | **4** | **4** | 0 |
>
> A coluna do **sinal do viés** é nova e não é decorativa: **P-9 e P-13 têm
> defeitos de sinal OPOSTO** (o modelo perde rápido demais × retém demais) — o
> que demonstra que não são duas descrições do mesmo problema. E ela impõe um
> filtro que a fila não tinha: forma que *adiciona* perda só ajuda quem tem
> **viés positivo**.

> ## ⚠️ RE-MEDIDO em 2026-08-08 — a **P-15 foi ASSINADA e EXECUTADA**
>
> O bloqueio da família de piso do `ECCLES_2010` (prereg
> `2026-08-08-p7-p15-execucao-prereg.md`) apertou `limite_sres` de **0,0828 para
> 0,0250** e a `eccles2010_fig7c_axial_2p7kN` saiu do tripé — **custo previsto e
> aceito**. Censo **140 → 139**, fora **65 → 66**, abertas **31 → 32**.
>
> **Todos os números do corpo abaixo são de 2026-08-07** e ficam como registro
> datado. A contagem vigente por decisão é:
>
> | decisão | abertas |
> |---|---:|
> | **P-7** | **12** |
> | **P-9** | 8 |
> | **P-13** | 7 |
> | **P-14** | 4 |
> | dado (a `fig7c`, agora sem piso) | **1** |
>
> ⚠️ A categoria **"dado"** — que este documento havia declarado **vazia** na
> tarde de 07-08 — **voltou a ter 1**: é a própria `fig7c`, que perdeu o piso da
> fonte junto com a família falsa. Ela não é regressão do modelo; é a curva
> deixando de ser sustentada por um piso que media a variável varrida.

## Por que este mapa

A fila form-limited fechou em zero (D-Z) e as quatro camadas de estatuto foram
auditadas e emendadas (P-10 · P-11 · P-12). O que resta está todo atrás de
decisão sua — mas espalhado por uma dúzia de documentos. Isto é **uma tabela**.

⚠️ Nenhum rótulo aqui é novo: cada assinatura já foi medida e publicada num
resultado desta campanha. O script apenas junta.

## O resultado

**34 fora do tripé** = **30 com estatuto** (19 exceção + 11 declarada; as 4 classe-encerrada contam como ABERTAS na definição do oráculo, vigente 2026-08-23 21:2x — as 2 do ECCLES retratadas FECHARAM POR MÉRITO no mesmo dia (`arrest_approach_exp` por protocolo) ⇒ censo **171/205** e fila ZERO; antes, no mesmo dia — as 2 provas de piso do ECCLES foram RETRATADAS em 2026-08-23 — o denominador estava inflado por contagem dupla do par declarado, prereg `fecha-tickets-e-dedup`; era 32 com 21 exceções até 2026-08-21 17:0x
— a 11ª declarada é a `liu2025_M16_amp0p8`, decisão (b) do item 8: ESGOTAMENTO MEDIDO
com 17 estruturas falsificadas, e a fila form-limited encerra em ZERO; antes, tarde de 08-21
manhã — a `lu2024_M8_fig20_T22Nm` saiu da lista de declaradas porque passou a **fechar por
mérito** quando o pico espúrio do CSV foi removido; as DEZESSEIS adoções de 2026-08-19/20 — SUN ×2, LU T10, ROUSSEAU ×4, ICMEZ ×5,
YANG_2023 ×3, YANG_2019 amp0p4 — tiraram 16; a 0,50 entrou DECLARADA n<6) +
**4 sem estatuto** (as 4 classe-encerrada; as 2 do ECCLES que perderam a exceção FECHARAM POR MÉRITO — a fila de forma reabriu em 2 e voltou a ZERO no mesmo dia — reconhecido em `parada_baseline.json`, e a parada segue válida porque a rota estrutural do ECCLES está falsificada, não inexplorada).

### As 31 sem estatuto, pela decisão que as cobre

| decisão | curvas | o que é |
|---|---:|---|
| **P-7** | **16** | `classe_parada` — e **10 das 23** têm defeito **oposto** ao da classe |
| **P-13** | **7** | bifurcação: canal rotacional ≥70 %, só dois atratores |
| **P-9** | **7** | relógio de Estágio I: cruza 90 % em ≤½ dos ciclos, ≥80 % emb+creep |
| dado | 1 | falta réplica; nenhuma rota de modelo |

**A P-7 é a maior alavanca isolada — 16 de 31 (52 %)** —, e é a única das três
que **não exige forma nova no engine**: é reclassificação de camada.

### Por fonte

| fonte | sem estatuto |
|---|---:|
| `CHU_2026` | 6 |
| `YANG_2023_IJPEM` · `LIU_2025` · `ROUSSEAU_2025` · `YANG_2019` | 4 cada |
| `YANG_2021` | 3 |
| `JCSR_2023` · `LU_2024` · `SUN_2025_CRIMP` | 2 cada |

### Por defeito (todas as 65, com ou sem estatuto)

| defeito | n |
|---|---:|
| classe parada | 24 |
| **bifurcação** (P-13) | **18** |
| **relógio E1** (P-9) | **12** |
| não classificado | 6 |
| sem piso | 5 |

⚠️ **As 6 "não classificadas" têm TODAS estatuto** — 5 exceções do
ECCLES/LIU_2020 e a `zhang19_fig4`, que é declarada por `n<6` e cujo MAE é
**0,0027** (ela não tem defeito; só não tem σ julgável). ⇒ **nenhuma curva sem
estatuto ficou sem defeito nomeado.** O mapa é completo onde importa.

## O que isto muda na leitura da campanha

Antes desta passada, "65 fora" era um número com uma dúzia de explicações
espalhadas. Agora:

* **34** estão fechadas por estatuto assinado, e as quatro camadas que os
  sustentam foram auditadas curva a curva nesta madrugada;
* **31** estão abertas, e cada uma tem **um** item da fila que a cobre;
* **zero** estão sem explicação.

A campanha não tem mais trabalho de medição dentro do mandato autônomo: as três
decisões abertas cobrem 30 das 31, e a 31ª precisa de dado que não existe.

## Ordem de retorno, se for útil decidir por impacto

1. **P-7** — 16 curvas, **sem forma nova**. É reclassificação: 10 das 23
   estacionadas têm defeito oposto ao da classe que as parkou.
2. **P-13** — 7 curvas, forma nova (taxa fracionária constante), **3 fontes
   independentes** e o discriminante mais nítido da campanha (0,01 mm move o
   final de 0,94 a 0,00).
3. **P-9** — 7 curvas, forma nova (frequência nos relógios de Estágio I),
   autoridade medida em 97–100 % e o rig instrumentado já identificado
   (`YANG_2019`, dado auditado contra a lei D-N impressa).

**P-8** (correção das CSVs do LU) fica fora desta conta: ela não move o censo
(+0 medido) — é decisão sobre **estar certo**, não sobre placar.

## Reprodutibilidade

```bash
py -3.12 New_Theory/mapa_das_65_fora.py --json New_Theory/mapa_das_65_fora.json
```
