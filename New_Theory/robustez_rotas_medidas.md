# O que melhorar para o modelo ser robusto, e não fit de curvas — medido, 2026-08-23

**Pergunta do professor.** Só-leitura, nada adotado. Fingerprint `db7de97e682a`, censo
**tripé 171/205**.

⚠️ **Isto NÃO é a lista da manhã** (`integridade_modelo_ou_fit.md`, outro fingerprint). Dois
números dela mudaram de significado e a rota que ela recomendava está **fechada por
medição** — §3.

---

## 1. Resposta curta

**A rota "transformar constante em lei" está fechada: as constantes per-curva NÃO seguem lei
nas variáveis que temos.** O que está aberto é outra coisa, e é mais simples: **as constantes
estão sendo gastas onde o dado não consegue discriminar.** A alocação segue a *dificuldade
de ajustar*, não a *qualidade do dado* — e isso é exatamente o que um fit faz.

## 2. O estado, re-medido

| | |
|---|---:|
grupos de config que servem curva | **71** |
**grupos que servem EXATAMENTE 1 curva** | **40** ⚠️ ver errata |
valores distintos | **212** |
"slots" de constante (soma por grupo) | **633** |
razão global | **0,33 curva por constante** |
tokens `per_case` | **48** em 16 grupos |

⚠️ **Errata da auditoria da manhã:** ela publicou *"1,07 curva por constante"*. A diferença é
o **denominador** — 212 valores **distintos** contra 633 **slots**. Os dois respondem
perguntas diferentes (*"quantos números independentes?"* × *"quantos botões o conjunto
expõe?"*) e nenhum é errado, mas **publicar um sem dizer qual é** foi o defeito. O número
mais afiado, e que não depende de convenção, é **40 grupos de uma curva só**.

> ⚠️ **ERRATA de 2026-08-25 — o "40" acima mede menos do que eu disse.** Re-medido com o
> discriminante certo (`variaveis_de_ajuste_em_replicas.md` §4): são **37**, e só **10** têm
> irmã de réplica; **27 estão sozinhas na condição**. Um config para uma condição de n=1
> **não é fit por réplica** — é um config para uma condição. O fit por réplica real são
> **10 grupos em 2 fontes** (`BAUER fig6 ×6`, `ECCLES ×4`), e não 40. A estrutura é menos
> fit-like do que esta seção afirma.

## 3. ⛔ A rota "constante → lei" está FECHADA por medição

Testei todas as constantes com ≥6 curvas e ≥3 valores contra 11 variáveis do registry
(amplitude, pré-carga, frequência, rugosidade, grip, espessura, remontagens, força axial,
diâmetro, ciclos).

**Entre fontes, r² alto é IDENTIFICAÇÃO DE FONTE disfarçada de física.** `frequency_Hz` e
`n_cycles` são quase constantes dentro de uma fonte e diferem entre fontes, então
`creep_t_c ~ n_cycles` a **r² = 0,993** não é lei — é **tautologia**: o D-H define
`t_c = 100·t_end`. O teste válido é **intra-fonte**.

**Intra-fonte, só 6 candidatos com r² ≥ 0,75, e nenhum sobrevive ao escrutínio:**

| constante | fonte | n | valores | variável | r² | por que não é lei |
|---|---|---:|---:|---|---:|---|
| `mu_thread` | SUN_REASSY | 5 | 5 | remontagens | 0,912 | n=5, varredura monótona ⇒ r² quase garantido |
| `mu_bearing` | SUN_REASSY | 5 | 5 | remontagens | 0,912 | idem |
| `emb_um` | LI_2022_MARSTRUC | 6 | 3 | rugosidade | 0,867 | **ANTI-FÍSICO** — ver §4 |
| `emb_um` | SUN_REASSY | 5 | 5 | remontagens | 0,820 | n=5 |
| `loose_arrest_floor` | ROUSSEAU | 8 | 3 | amplitude | 0,781 | 3 valores |
| `loose_arrest_floor` | SUN_REASSY | 5 | 5 | remontagens | 0,779 | n=5 |

A cautela do n pequeno não é teórica: **hoje mesmo** o projeto rejeitou uma lei de amplitude
com r² = 0,998 sobre **3 pontos**, e a mesma armadilha derruba as 4 do `SUN_REASSY`.

⇒ **Isto é conhecimento negativo útil:** pare de procurar leis nas variáveis que já temos. Se
uma lei existir, ela precisa de variável que **não está no registry** (dureza medida,
acabamento real do par, torque de prevalência), e isso é campanha de leitura de paper, não de
fit.

## 4. ⚠️ Um achado que vale mais que a lei que eu procurava

O `emb_um` adotado no `LI_2022_MARSTRUC`, contra a rugosidade **medida**:

| Ra [µm] | `emb_um` adotado |
|---:|---:|
| 0,078 | 0,0874 |
| 0,122 | 0,0693 |
| 0,306 | **0,01** |
| 0,80 | **0,01** |

**Cai com a rugosidade** — e o VDI 2230 f_Z diz o contrário: superfície mais rugosa encaixa
**mais**. E 4 das 6 curvas sentam em **0,01 µm**, que para embedding é *praticamente zero*
(a tabela VDI opera na casa de 1–10 µm).

Leitura honesta: nessas curvas o embedding foi **desligado** pelo ajuste, e nas duas mais
lisas recebeu um valor pequeno. Pode ser legítimo (a fonte é **creep dominante**, 99 % da
perda) — mas então **diga isso**, em vez de deixar um valor anti-físico posando de
calibração. O projeto tem o helper `emb_depth_vdi` (procedência `handbook`) e **não o usa
aqui**.

> ## ⚠️ ERRATA de 2026-08-23 (mesma noite) — a §5 abaixo usa banda INFLADA
>
> O estudo das réplicas (`estudo_das_replicas.md`) mediu que **55–65 % da banda de 4
> condições é ARTEFATO DE DURAÇÃO**, não dispersão de espécime: as curvas rodaram
> comprimentos diferentes e a métrica as compara no **ciclo absoluto**. No `BAUER` a banda
> irredutível é **0,15–0,18**, não 0,4587 (em vida normalizada: 0,52 → 0,18).
>
> ⇒ **das 4 fontes que a §5 aponta como "constante gasta em ruído", 2 eram artefato.** O
> argumento de sobre-gasto do `BAUER` **enfraquece**: 34 constantes para 9 curvas segue muito,
> mas não é "gastar num ruído de 0,46". A tabela abaixo fica como registro do que foi medido
> **antes** da correção; a leitura vigente é a do estudo das réplicas.

## 5. A rota que a evidência de fato sustenta: **orçar constante pela BANDA**

Cruzando as constantes por fonte com a banda de réplica medida hoje
(`erro_contra_condicao_vs_replica.md`):

| fonte | banda do dado | grupos | constantes | leitura |
|---|---:|---:|---:|---|
| `BAUER_2024` | **0,4587** | 7 | **34** | o dado não discrimina — constante em ruído |
| `ECCLES_2010` | 0,1866 | 10 | **54** | banda média, gasto alto |
| `LIU_2022_RETIGHT` | 0,1402 | 4 | **48** | idem |
| `LIU_2025` | 0,0428 | 3 | **64** | dado bom, gasto altíssimo |
| `LU_2024` | 0,0162 | 1 | 34 | dado bom |
| `LIU_2016` | **0,0136** | 2 | **14** | **melhor dado do conjunto, menor gasto** |

**A alocação é descorrelacionada da qualidade do dado.** O `BAUER` gasta 34 constantes onde
as réplicas discordam em 0,459; o `LIU_2016`, com banda 34× menor, recebe 14.

### O caso BAUER fecha um pacote coerente

- 7 grupos de config, um por réplica (`fig6_rep1`, `rep2`, `rep3`…) ⇒ **fit por curva por
  construção**.
- Banda 0,4587: as réplicas discordam quase tanto quanto a própria queda.
- E as **4 curvas que hoje reprovam passariam no nível da condição** (medido: 0,0369/0,0586/
  0,0196).

⇒ **Proposta:** no `BAUER`, **um config por CONDIÇÃO** (2 grupos, não 7) e o veredito lido
contra a condição. É a única fonte em que as três medições — banda, censo e contagem de
grupos — apontam para o mesmo lugar. Custo esperado: o MAE por curva **piora**, porque um
config só não persegue mais cada réplica; o ganho é 5 grupos e ~24 constantes a menos, e uma
afirmação que se pode defender.

## 6. Rotas de custo ZERO, medidas

**Colapsar grupos com `cfg` efetivo IDÊNTICO:** 10 grupos em 4 classes ⇒ **6 grupos
redutíveis sem tocar em número nenhum**.

| classe | grupos |
|---|---|
| `BAUER_2024_fig6_rep2/rep3/rep4` | 3 idênticos |
| `KARLSEN_2022_run2p2/run7p1/run14p2` | 3 idênticos |
| `ancora_interna/def` | 2 idênticos |
| `LI_2022_MARSTRUC_ra0p8/ra0p306` | 2 idênticos |

⚠️ Menor que o *"116 de 200 parâmetros são repetição"* da manhã, porque aquilo contava
**parâmetros** e isto conta **grupos com cfg efetivo idêntico** — critério mais estrito e o
único em que colapsar é **provadamente** de custo zero. O `LI_2022_MARSTRUC_ra0p8` ×
`ra0p306` idênticos é a §4 aparecendo de outro ângulo: dois níveis de rugosidade com o mesmo
config.

## 7. O que já funcionou, e é o único mecanismo com efeito medido

**Representar a variável varrida como INPUT.** Nesta semana: `external_axial_N` (ECCLES),
depois 9 campos de varredura (grip, rugosidade, espessura, remontagens, força axial,
frequência, espécime). Efeito medido: pareamento espúrio **74 → 24** curvas e bloqueio manual
de 81 curvas a **ZERO**.

⚠️ Mas note o limite: isso entrou na **detecção de réplica**, não na **física**. Levar à
física é passo gateado, e a única tentativa desta semana (`ax_floor_override`, camada C3)
foi **falsificada**. ⇒ o mecanismo funciona para *organizar*; para *predizer* ele ainda tem
de passar por gate, e um de dois falhou.

## 8. Ranking, com custo

| # | rota | ganho medido | custo | precisa de assinatura? |
|---|---|---|---|---|
| 1 | **`BAUER` com 1 config por condição** | −5 grupos, ~−24 constantes | MAE por curva piora | **sim** (muda config e veredito) |
| 2 | Colapsar os 6 grupos idênticos | −6 grupos | **zero** | sim (toca config) |
| 3 | Declarar `creep_t_c` como **derivado** de `t_end` | DOF publicado cai; para de contar botão que não existe | zero | sim (é afirmação de legitimidade) |
| 4 | Resolver o `emb_um` anti-físico do MARSTRUC | 1 valor por procedência, ou declaração | pode piorar 2 curvas | sim |
| 5 | Publicar a **banda** ao lado do erro | triagem de esforço deixa de ser cega | zero | sua decisão (ITEM Y) |
| 6 | ~~constante → lei~~ | **FECHADA** por medição (§3) | — | — |

**Sobre o #1, e é a parte desconfortável:** ele **piora** o número publicado por curva. A
tese é que um modelo que usa 2 configs para 9 curvas e erra um pouco mais é mais defensável
que um que usa 7 e erra menos — e que a diferença, no `BAUER`, cabe inteira dentro da banda
do próprio experimento. Isso é decisão sua, não medição.

## 9. Reprodutibilidade

Sondas só-leitura sobre `kb.adopted_sources()`/`kb.adopted_config()` (nunca lendo o JSON
direto — a 1ª versão desta medição leu o arquivo e devolveu **0 campos**, porque a estrutura
é `{cfg, pack, prov, verdict}` e não `{overrides}`) e sobre
`New_Theory/condicao_vs_curva.json`. Grupos atribuídos por `rn._adopted_for`, o mesmo matcher
do runner.
