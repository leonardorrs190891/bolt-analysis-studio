# Prereg — item **L**: publicar o **conteúdo preditivo por fonte** no report mestre

**2026-08-14 (noite VII)** · assinatura em bloco do professor (*"continue o loop, eu assino
tudo"*, 22:34), com a posse registrada pela sessão B em `5bb00be`: *"K · L · M ·
censo-conta-curvas · classe artigo×store — ASSINADOS PARA O PROPONENTE executar"* ·
gates **IMUTÁVEIS** depois desta linha.

---

## Estado

✅ **EXECUTADO em 2026-08-15 (madrugada) — código no report mestre; regeneração do HTML
NÃO (gate G7).**

⚠️ **Eu tinha me bloqueado mais do que o necessário.** A versão anterior deste bloco dizia
*"PENDENTE — aguarda janela livre"*, tratando o item como parado pela política D3. Mas o
**meu próprio G7** separa **código** de **regeneração**: só a segunda depende do D3. Com
`report_html.py` livre, o código era executável — e foi.

| gate | resultado |
|---|---|
| **G1** nenhum número de censo muda | ✅ tripé **141** · fora **64** · declarado **181** — idênticos |
| **G2** piso de **réplica da fonte**, não global | ✅ `CACCESE_2009` = **1,043** (piso 0,0543 impresso na tabela), não < 0,2 |
| **G3** mediana, nunca contagem | ✅ `LIU_2022_RETIGHT` **0,847** entre as melhores, com **100** pares |
| **G4** texto diz que não é meta nem 4ª perna | ✅ no corpo do painel |
| **G5** guardas | ✅ |
| **G6** suíte completa | ✅ |
| **G7** HTML **não** regenerado neste commit | ✅ só `report_html.py` |

### O painel já registra o efeito da adoção da mesma noite

O `LIU_2020_WEAR` — o caso que motivou este item, com cobertura **0 %** — aparece agora em
**0,756**, porque o canal de flanco foi adotado horas antes (`631d4a1`). **Mediana das
medianas 0,804 → 0,846.**

⚠️ **Dois nomes que eu inventei e o módulo já tinha**, corrigidos antes de rodar:
`_PISO_DIGIT` (existe como **`_PISO_DIGITALIZACAO`** = 0,005, Liu 2017) e uma
interpolação à mão (o módulo já importa **`numpy`**; agora usa `np.interp`, a mesma
convenção das sondas que mediram estes números). Constante duplicada é a forma clássica de
duas partes do código divergirem em silêncio.

---

## O que se publica

Uma tabela nova no report mestre, **informacional**, no mesmo estatuto da deriva β:

> **razão `d_mod / d_dado` por fonte** — quanto o modelo separa as condições, comparado
> com quanto o dado as separa.

Método (medido em `censo_cegueira_a_condicao_varrida.md` §1 e §5b): par a par **dentro da
fonte**, na janela comum, **só entre curvas que passam o tripé**; descarta o par se
`d_dado` estiver abaixo do **piso de réplica DAQUELA fonte**; publica a **mediana** por
fonte.

## Por que isto é necessário — o caso que o motiva

O `LIU_2020_WEAR` varre a amplitude transversal **4×** (AF 0,1→0,4 mm, P₀ fixo) e o modelo
devolve **0,9650 nas quatro**. Cobertura **0 %**. A fonte está **8/9 no tripé**, o que se lê
como *"o modelo vai bem aqui"*. A leitura correta é: **9 curvas, 4 predições distintas.**

Nenhuma métrica da campanha faz essa pergunta hoje, e por isso *"desligar o canal"* e *"o
canal não existe"* ficam indistinguíveis.

## Números medidos (o que a tabela mostraria)

**Mediana das medianas 0,804** · 22 fontes julgáveis · 371 pares.

| fonte | razão | tripé |
|---|---:|---:|
| `QIN_2024` | **0,024** | 3/3 |
| `LIU_2020_WEAR` | **0,115** | 8/9 |
| `LI_2022_TRIBOINT` | 0,264 | 4/4 |
| `LI_2022_MARSTRUC` | 0,342 | 6/6 |
| `LIU_2025` | 0,378 | 3/7 |
| … | | |
| `LIU_2016` | 0,949 | 14/14 |
| `KARLSEN_2022` | 1,033 | 11/11 |
| `CACCESE_2009` | 1,043 | 7/7 |

⇒ **5 fontes com razão < 0,40 carregam 24 das 141 curvas do censo (17 %).**

## ⚠️ As duas advertências que a implementação TEM de carregar

1. **Piso de RÉPLICA DA FONTE, não o global.** Com o piso global o `CACCESE_2009` aparece
   como "cego" quando o que ocorre é que o **scatter entre réplicas (0,0549) excede o
   efeito de geometria (0,0101–0,0449)** — o dado não pode exigir a separação. Com o piso
   certo ele é dos **melhores** (1,043). ⚠️ Na 1ª execução eu usei `pisos.get(src)`, mas
   `pisos_medidos` devolve `{'fam':…, 'med':…, 'por_fonte':{fonte:(mae,mx,sres)}}` — deu
   `None` em todas e o piso global em todo lugar; **30 % dos pares** entraram indevidamente
   e o `BAUER_2024` virou acusação falsa.
2. **A razão NÃO é meta.** Forçá-la a 1 seria pedir que o modelo reproduzisse o scatter.
   Ela é leitura, como o RMSE na cunha.

E uma terceira, sobre como **não** apresentar: **contagem absoluta de pares cegos inverte a
ordenação** (pares crescem com n²). O `LIU_2022_RETIGHT` lidera em contagem (17) e é uma das
**melhores** normalizado (0,847 sobre 100 pares). A tabela publica **mediana**, nunca
contagem.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **G1** | nenhum número de censo muda | tripé, fora e camadas **idênticos** ao pré-execução |
| **G2** | a tabela usa `pisos_medidos(...)['por_fonte']`, não o global | verificado no código E no valor do `CACCESE_2009` (≈1,04, não <0,2) |
| **G3** | a tabela publica **mediana** por fonte, nunca contagem de pares | `LIU_2022_RETIGHT` aparece entre as melhores, não entre as piores |
| **G4** | o texto da página diz explicitamente que **não é meta** e **não é 4ª perna** | presente |
| **G5** | guardas verdes, incl. `test_meta_numeros_nao_envelhecem` | todas |
| **G6** | suíte completa verde | ≥ 941/1 |
| **G7** | regeneração do HTML **não** entra no mesmo commit que o código | o D3 (38 MB no git) é decisão de política do professor, não desta execução |

⚠️ **G1 é o que mata**: item L é **informacional**. Se algum número de censo se mover, a
implementação vazou para o veredito e tem de ser revertida.

⚠️ **G7 existe porque a regeneração move ~38 MB** nos 203 reports versionados. O código
entra; a regeneração fica para quando o professor decidir o D3.

## Bloqueio operacional no momento da escrita

`report_html.py` está **limpo** agora, mas a sessão B tem um re-stamp **em voo** (store em
15:49, vários `python.exe` ativos, `adopted_configs.json` e `inputs.py` modificados). A
execução deste item **espera a janela livre** — a regra de 1 escritor vale para o módulo do
report tanto quanto para a config.

## Rollback

Mudança confinada a `report_html.py` (função nova + chamada). Reverter = `git checkout` do
arquivo; nada de config, store ou fingerprint é tocado.
