# Fila de decisões do professor (campanha autônoma)

A campanha contínua NÃO bloqueia nestes itens — eles acumulam aqui com
diagnóstico pronto. Decida quando quiser; cada item diz o que destrava.

---

### ⚠️ AVISO ATIVO (2026-08-20 10:5x) — o store da adoção EM VOO está **209 + 1**, não uniforme

> **Medido agora**, enquanto a adoção do `yang2019 amp0p4` (`2163b40`) ainda está em voo:
>
> ```
> config  305e6abaa655
> store   {'305e6abaa655': 209, 'c7a141e2ee06': 1}
> ```
>
> O registro atrasado é **`exemplo_m12_sintetico`** — e é **exatamente** o gotcha que o
> `CLAUDE.md` documenta e que eu **paguei** na adoção R2 de 08-16: o `parallel_batch` cobre
> **209 de 210** e esse caso fica **fora do universo do batch**.
>
> ⚠️ **`--cases exemplo_m12_sintetico` NÃO conserta** (seleciona nada — está fora do
> universo). O que funciona é **re-sim direta com carimbo manual**:
>
> ```python
> r = rn.simulate_case(recs["exemplo_m12_sintetico"])
> d = r.to_dict(); d["engine_fingerprint"] = rn.engine_fingerprint()
> d["generated_at"] = <iso>          # single-writer, e RELER depois de escrever
> ```
>
> **Por que avisar agora e não depois:** um gate de uniformidade de fingerprint reprovaria
> por **1** registro, e o custo de descobrir isso depois do commit é re-abrir a adoção. No
> meu R2 foi essa mesma linha que separou G4-passa de G4-reprova.
>
> ⚠️ **Não conserto** — store é recurso de um escritor só, e a adoção é deles.
>
> ✅ **RESOLVIDO — medido às 16:5x de 2026-08-20**, e o aviso fica preservado porque a
> LIÇÃO vale (o `parallel_batch` cobre 209 de 210 e o sintético fica fora do universo):
>
> ```
> config  4d1211958122
> store   {'4d1211958122': 210}      divergentes: []
> ```
>
> Uniforme, 210 registros, zero divergentes — a sessão paralela carimbou o
> `exemplo_m12_sintetico` junto. ⚠️ **"AVISO ATIVO" é, por construção, afirmação sobre o
> PRESENTE** — diferente de registro datado, que o §4.43 não policia de propósito. Deixá-lo
> como ativo custaria ao próximo leitor uma re-simulação de um problema já consertado, que é
> exatamente o modo de falha que o item pretendia evitar.
>
> ⚠️ **E os fingerprints de store deste documento envelhecem MAIS RÁPIDO que os números**:
> só hoje ele cita `305e6abaa655`, `df35fd990380` e `f2c01a123c8c`, e o vigente é
> **`4d1211958122`**. O censo (165) atravessou os quatro. ⇒ **cite o censo, meça o
> fingerprint** — o segundo se move a cada adoção, o primeiro só quando uma curva muda de
> estatuto.

### ✅ DECISÕES TOMADAS POR DELEGAÇÃO em 2026-08-25 — *"faça as decisões mais coerentes"*

> **O critério que usei em todas, declarado antes:** escolher a opção que **não mexe na
> régua publicada** e que fecha a lacuna com o **menor custo declarado**. Trocar a régua é
> decisão do professor; construir o instrumento é minha.
>
> | item | decisão | por quê |
> |---|---|---|
> | **AC(b)** figura da âncora interna | **SAI** | a âncora interna saiu do projeto em 01/08; preservar curva no store **não é** publicar figura dela. Retirada dos **3** lugares; a função fica marcada, porque apagá-la perderia o registro |
> | **AC(a)** exportador | **versionado + as 8 que faltavam** | era o gargalo real, e é trabalho meu, não decisão de domínio |
> | **AB(a)** matriz no report | **ENTRA** | mede o que o engenheiro usa, os números já existiam, custa **zero** ao censo |
> | **AB(b)** falso seguro | **GATE de adoção, NÃO 4ª perna** | 4ª perna mudaria o **censo publicado**, e a sessão de 07-29 mostrou como perna nova cascateia por todo documento vivo. Gate custa zero e pega a direção perigosa |
> | **AB(c)** as 3 aprovadas | **marca INFORMACIONAL** | mesmo estatuto da deriva β: informa sem mudar veredito |
> | **AA** procedência por token | **estrutura + dívida contada, sem inventar** | declarar a procedência de 147 entradas exige ler os papers; fabricar seria o oposto do objetivo. E `adopted_configs.json` é recurso **single-writer** com sessão paralela ativa |
>
> **O que ficou construído:** `scripts/export_thesis_figures.py` versionado com **20
> figuras** (PNG + **PDF vetorial**), a matriz de decisão no report mestre nomeando as 3
> curvas, e `tests/test_falso_seguro_nao_cresce.py` (5 testes) como gate.
>
> ⚠️ **Dois defeitos pré-existentes que a execução expôs no exportador**, ambos de 6 semanas
> de defasagem: (a) `fig_per_source_medians` **estourava** — o `per_source` do ledger virou
> `{fonte: float}` e o código esperava `{fonte: {"median", "n"}}`; (b) a mesma figura
> desenhava a linha de limite em **0,10** sob o título *"régua canônica"* quando o MAE
> vigente é **0,05** — num artigo, erro material. Passa a ler `rh.META_MAE`, nunca literal.
>
> **O que segue seu:** promover falso seguro a 4ª perna (muda o censo) e declarar a
> procedência das 147 entradas (exige os papers).

### ✅ ITEM AC (2026-08-25) — figuras do artigo: EXECUTADO (ver decisões acima)

> **Pergunta do professor:** *"para mostrar o funcionamento do software em um artigo, o que me
> sugere de gráficos e imagens?"* Plano completo: `New_Theory/figuras_para_o_artigo.md`.
>
> **10 figuras, na ordem do argumento** — e o argumento não é *"ajustamos 205 curvas bem"*, é
> *"ajustamos 205 curvas, medimos quanto custou e registramos o que falhou"*. As duas
> centrais:
>
> - ⭐ **Fig. 5 — "uma física, N comportamentos":** as 4 curvas da fig. 18 do `LU_2024` com
>   **constantes idênticas** e retenção de **0,771 a 0,113**. Responde à objeção *"vocês não
>   estão apenas ajustando cada curva?"*.
> - ⚠️ **Fig. 8 — decisão de engenharia:** ISO/DIN com os **7 falsos seguros** nomeados, **3
>   deles aprovados pelo tripé**. É a figura que **compra credibilidade** — um revisor não
>   espera encontrar isso, e encontrar muda a leitura de todo o resto.
>
> **⚠️ O gargalo NÃO é o quê, é o COMO.** Existe `scripts/export_thesis_figures.py` (19,6 KB,
> `--dpi 300 --pdf`, captura de GUI offscreen), mas:
>
> | | medido |
> |---|---|
> | **não versionado** | `git log` não tem nenhum commit dele |
> | 6 semanas desatualizado | de 14/jul |
> | ⚠️ **figura VENCIDA** | `ancora_interna` — a âncora interna **saiu em 01/08**; as 3 curvas seguem no store (**0 comparáveis**), então a figura **ainda gera** com dado fora do projeto. Num artigo é **erro material**. |
> | cobre | **2 das 10** figuras recomendadas |
>
> As outras 8 existem como **SVG de tela** — tema escuro, fonte 10 px, sem numeração. Revista
> pede traço/cinza, fonte legível em coluna e PDF vetorial.
>
> **Duas decisões suas:** (a) versiono e atualizo o exportador, com as 8 figuras que faltam em
> qualidade de publicação? (b) a figura da âncora interna sai ou ganha marca de "fora do escopo"?
>
> **E uma dívida que bloqueia uma TABELA, não figura:** a tabela de constantes com procedência
> — a que separa o artigo de um exercício de ajuste — **não pode ser escrita por inteiro
> hoje**: 147 de 200 entradas `per_case` não têm procedência declarada (ITEM AA).

### ⚠️ ITEM AB (2026-08-25) — o tripé aprova 3 curvas em que o modelo diz "SEGURO" e o ensaio diz que afrouxou

> **Achado ao responder** *"que outras curvas e gráficos sugere para qualificar o
> software?"*. Medição: `New_Theory/qualificacao_o_que_falta.md` · página
> `metodologia/qualificacao.html`. Nada adotado.
>
> **A classificação que o software de fato entrega**, medida nas 205 comparáveis no ponto
> final:
>
> | norma | limiar | acerto | falso alarme | **falso SEGURO** |
> |---|---|---:|---:|---:|
> | ISO 16130 | ≥ 85 % | 94,1 % | 5 | **7** |
> | DIN 25201-4 | ≥ 80 % | 95,6 % | 3 | **6** |
>
> ⚠️ **3 dos 7 falsos seguros PASSAM o tripé:**
>
> | curva | dado | modelo | MAE |
> |---|---:|---:|---:|
> | `rousseau2025_hdpe_t10_amp0p2` | 0,799 | **0,869** | **0,0260** |
> | `liu2022_fig8_multi_t4` | 0,845 | **0,924** | 0,0380 |
> | `sun2025efa109235_axial_F17.5kN_standard` | 0,814 | **0,861** | 0,0330 |
>
> A primeira tem **MAE 0,0260** — fidelidade excelente — e informaria *"87 % de retenção"*
> onde o ensaio mede **80 %**. **O tripé mede fidelidade de curva; ele não mede acerto de
> decisão.** Não é defeito do tripé — é uma pergunta que ele não faz, e que o projeto nunca
> publicou.
>
> E a paridade explica o mecanismo: **viés médio +0,0083** (o modelo retém **mais** que o
> ensaio, na média), R² 0,9455 contra a reta 1:1, 78 % dentro de ±0,05.
>
> **Três decisões suas:** (a) a matriz de decisão ISO/DIN entra no report mestre? (b) falso
> seguro vira **4ª perna** ou gate de adoção — *"nenhuma adoção pode aumentar o número de
> falsos seguros"*? (c) as 3 aprovadas ganham marca no report, ou ficam só nesta página?
>
> **Ainda falta, com custo declarado (§ do doc):** conservação de energia por caso — o engine
> calcula e **o store não grava**; independência de passo de integração; held-out sistemático.
> Os dois primeiros são **verificação**, e o projeto não tem nenhum gráfico dela.

### ✅ ITEM AA — COLHIDO em 2026-08-25: a leitura já estava feita, e o número era outro

> ✅ **FUNDIDO em 2026-08-28** por decisão do professor (*"resolva todas"* as três dívidas que o
> anexo do artigo declarava): as 74 chaves grupo×campo da colheita (cobrindo as 147 entradas
> `per_case`) entraram no `prov` do `adopted_configs.json` com o texto colhido + sufixo de
> rastreio, e as **11 constantes compartilhadas** sem texto (KARLSEN run7p1/run2p2 `C_creep`,
> `c_D` herdadas do grupo-pai; YANG_2019/varamp `emb_um` 5,0 e `slip_onset_W` 40 kJ desde o
> registro 385ed72, classe conservadora fitado-this-rig; ZHANG_2006_fig16 `emb_um` 1,58 lido do
> fig16, `d_hole` ISO 273, `d_washer` ISO 7089 como o irmão; ZHANG_2019 `mu_thread` 0,241
> input-de-paper, Tabela 2 via nota de aparato) ganharam texto com documento ou commit de
> introdução. Escrita single-writer com round-trip de formato, parser anti-duplicata e releitura
> valor a valor; fingerprint `db7de97e682a` → `79af1f607cb7`, store re-carimbado (210).
> `test_toda_entrada_per_case_TEM_prov_no_config` fixa o invariante novo; o mapa
> `procedencia_colhida.json` fica como registro histórico. Terceira dívida do mesmo pedido:
> `CaseResult.energy_budget` (resíduo de conservação) passou a ser gravado no store.
>
> **Pedido:** *"leia os papers"*, em resposta a eu ter dito que declarar a procedência das
> 147 exigia lê-los. **Era o meu diagnóstico, e estava errado.** Resultado:
> `New_Theory/leitura_dos_papers_resultado.md`.
>
> **A leitura JÁ TINHA SIDO FEITA.** Cada uma das 147 entrou por um pré-registro que
> declara a origem; o campo `prov` é que nunca foi preenchido. Do PR-28, de **15/jul**:
> *"`mu_thread/mu_bearing` POR CASO = **Fig. 10 locknut digitalizada (input-de-paper)**:
> N=2:0,158 … 10:0,279"* — os cinco números estão no config **sem `prov`**, e a frase que os
> justifica tem seis semanas.
>
> ⚠️ **E o número "147 sem procedência" era leitura errada dele mesmo:**
>
> | classe | n | o que é |
> |---|---:|---|
> | **zero estrutural** | **45** | canais DESLIGADOS (`s_crit_loose=0`…) — não são constantes |
> | **modo** | **18** | `loose_rate_mode` — seletor de forma, não valor |
> | **valor** | **84** | os que pedem procedência de verdade |
>
> ⇒ **63 das 147 não são constantes.** Mesmo modo de falha dos *"40 grupos de uma curva
> só"*, que eram **10** — publicar contagem sem separar as classes. Segunda instância no
> mesmo dia.
>
> **Colhido: 147 de 147, zero pendente** (`colheita_de_procedencia.py` →
> `procedencia_colhida.json`, 74 pares grupo×campo). Cada entrada **cita o documento** —
> PR-28, prereg P-13 (LSQ ao F publicado, r² 0,9968–0,9999), `rousseau_t10_ratchet_lido`
> (dF/dθ r²=0,9997), prereg zhang-fig3-runaway (`frac`=0,25 **lido do paper**), e mais 5.
>
> ⚠️ **Honestidade que a colheita forçou:** o μ=0,15 do `LIU_2020_WEAR` em `zinc`/`af0.4`
> **não é leitura da fonte** — é o default do `shared`, herdado. Só o DLC (0,126) é medido.
> A procedência colhida **diz isso**, em vez de deixar os três parecerem igualmente lidos.
>
> **O que segue seu — a FUSÃO, não a leitura:** `engine_fingerprint()` hasheia
> `adopted_config(s)` **inteiro**, incluindo `prov`. Fundir muda o fingerprint e obriga a
> re-carimbar os **210** registros: é operação de adoção, single-writer, com sessão paralela
> ativa. **O artefato está pronto para ela.**
>
> **Isto destrava a tabela de constantes com procedência** que o ITEM AC apontou como *"a
> que separa o artigo de um exercício de ajuste"* e que não podia ser escrita por inteiro.

<details><summary>enunciado original do ITEM AA (preservado)</summary>

### ITEM AA (2026-08-25) — variáveis de ajuste em ensaios com réplica: o eixo é PROCEDÊNCIA, não granularidade

> **Pergunta do professor:** *"como podemos representar as variáveis de ajuste dentro de
> ensaios com réplica?"* Medição: `New_Theory/variaveis_de_ajuste_em_replicas.md`. Nada
> adotado.
>
> **A distinção que importa não é per-curva × per-condição — é PROCEDÊNCIA.** O `fat_C1` do
> `LIU_2025` é per-curva e **legítimo** (é a vida `N_f` **lida do paper**); o
> `tr_loose_gain` do `BAUER` é per-curva e é **fit**. Hoje moram no mesmo dict, com a mesma
> forma: **200 entradas (token, campo)** em `per_case`, **147 sem procedência nenhuma** — e
> quem conta DOF conta os dois igual.
>
> **Quatro representações, com custo:**
>
> | # | representação | DOF | falsificável? | onde já existe |
> |---|---|---|---|---|
> | **A** | input medido por espécime | **0** | sim | `fat_C1`, `emb_um`, `free_spin_kin` |
> | **B** | constante por CONDIÇÃO | 1/cond. | sim (contra a banda) | **9 das 15** |
> | **C** | hierárquico `θ_cond + σ_θ` | 2/família | **sim, e é a virtude** | não implementado |
> | **D** | constante por CURVA | N | **não, por construção** | 10 grupos, 2 fontes |
>
> ⇒ **D não pode ser falsificada dentro da condição:** uma constante ajustada numa curva tem
> **um** dado para explicar, e não pode errar. O `σ_θ` de C **tem de bater com a banda
> observada** — se não bate, a representação está errada e o projeto fica sabendo.
>
> ⛔ **A rota A está FECHADA nos dados que temos.** O candidato natural é o aperto alcançado
> por espécime (`y[0]` cru). No `LIU_2017` ele é **1.000000 exato** nas 5 curvas — foi
> **normalizado fora na digitalização** (idem ZHANG_2018/2019). No `BAUER`, onde sobreviveu
> (spread **0,145**, o *"tightening scatter"* da nota), ele **não explica**: r² = **0,006**
> contra banda 0,520.
>
> ⚠️ **ERRATA do meu ITEM Z:** publiquei *"40 grupos servem 1 curva"* como evidência de fit.
> Medido com o discriminante certo: **37**, e só **10** têm irmã de réplica; **27 estão
> sozinhas na condição** — e *um config para uma condição de n=1 não é fit por réplica*. O
> fit por réplica real são **10 grupos em 2 fontes** (`BAUER fig6 ×6`, `ECCLES ×4`). **A
> estrutura é bem menos fit-like do que eu publiquei.**
>
> **PROPOSTA (barata, estrutural):** marcar procedência **por token** em `per_case` —
> `input` × `fit`. Faz o report publicar *"N constantes fitadas"* separado de *"N inputs por
> espécime"* (hoje é o mesmo número, e por isso o DOF publicado exagera), dá alvo ao gate de
> adoção e torna as 147 sem procedência uma dívida **contável**.
>
> **Recomendação por caso:** `BAUER fig6` → **C** (σ_θ conferido contra a banda **0,18** em
> vida normalizada, não 0,52) · `LIU_2020_WEAR` → **B** · `ECCLES` → B/C **mas pede prereg**
> (2 das 4 acabaram de fechar pelo `arrest_approach_exp` por protocolo) · as 9 que já
> compartilham → nada · fontes com `y[0]` normalizado fora → registrar a perda de dado.

</details>

### ⚠️ ITEM W2 (2026-08-23, 22:4x) — o cão de guarda do D1 DISPAROU, e o achado é de legitimidade

> **`tests/test_sres_por_fonte.py::test_gates_do_prereg_no_store` está VERMELHO**, e não é
> ruído: o gate G2 do prereg D1 exige que o ganho do limite-por-fonte seja *"de método, não
> de contagem — 19 das 20 já eram exceção assinada"*. Medido agora: **9 curvas ganham** pelo
> limite por fonte e **3 não têm assinatura cobrindo**, onde o prereg mediu **1**.
>
> **Duas das 3 sou eu**: as provas de piso `eccles fig8a`/`fig8c`, cujas assinaturas retirei
> às 20:0x. E o que a medição mostra é mais forte que a contagem:
>
> | curva | σ_res | tripé com global 0,025 | tripé com o da fonte 0,0432 | exceção? |
> |---|---:|:--:|:--:|:--:|
> | `fig8a` | 0,0254 | **NÃO** (por 0,0004) | sim | não |
> | `fig8c` | 0,0341 | **NÃO** | sim | não |
>
> ⇒ o *"fecham por MÉRITO"* da adoção `arrest_approach_exp` vale **só sob a barra afrouxada
> por fonte**. As duas estão no censo (171) apoiadas **apenas** no D1, sem prova de piso — e
> a `fig8a` erra a barra global por **0,0004**.
>
> ⚠️ **Não relaxei o gate** (é gate de prereg, imutável) e **não re-assinei** as exceções — a
> retratação segue correta, porque o denominador estava inflado por contagem dupla. O que
> mudou é que a régua que as sustenta passou a ser o D1 puro.
>
> **Três decisões suas:** (a) 3 curvas apoiadas no D1 sem prova de piso é aceitável, ou o G2
> do D1 precisa de re-leitura formal? (b) o gate G2 deve continuar sendo re-medido contra o
> store de hoje — ele é *pré-adoção* e o D1 foi adotado há 24 dias, então ele **vai** derivar
> por construção — ou vira watchdog explícito com limite próprio? (c) vale re-assinar as 2 do
> ECCLES sob a prova nova (agora elas passam as 3 pernas contra o piso deduplicado), o que as
> re-cobriria sem tocar no D1?

### 🆕 ITEM Z (2026-08-23) — robustez: a rota "constante → lei" está FECHADA, e a aberta é **orçar constante pela banda**

> **Pergunta do professor:** *"o que podemos melhorar para deixar o modelo robusto, e não um
> fit de curvas?"* Medição: `New_Theory/robustez_rotas_medidas.md`. Nada adotado.
>
> **Estado re-medido:** 71 grupos servem 207 curvas, **40 servem EXATAMENTE 1 curva**, 212
> valores distintos / **633 slots** de constante, 48 tokens `per_case`. ⚠️ **Errata da
> auditoria da manhã:** ela publicou *"1,07 curva por constante"* — a diferença é o
> **denominador** (212 distintos × 633 slots); os dois são legítimos para perguntas
> diferentes, mas publicar um sem dizer qual foi o defeito.
>
> ⛔ **"Constante → lei" FECHADA por medição.** Testadas todas as constantes com ≥6 curvas
> contra 11 variáveis do registry. **Entre fontes**, r² alto é **identificação de fonte
> disfarçada de física** (`creep_t_c ~ n_cycles` a r²=0,993 é **tautologia** — o D-H o define
> como `100·t_end`). **Intra-fonte**, só 6 candidatos ≥0,75 e nenhum sobrevive: 4 são
> `SUN_REASSY` com **n=5** e varredura monótona (r² quase garantido — mesma armadilha que
> hoje derrubou uma lei de r²=0,998 com 3 pontos), 1 é anti-físico e 1 tem 3 valores.
> ⇒ **conhecimento negativo útil:** se existir lei, ela precisa de variável que **não está no
> registry** (dureza medida, acabamento do par, torque de prevalência) — campanha de leitura
> de paper, não de fit.
>
> ⚠️ **Achado que vale mais que a lei que eu procurava:** o `emb_um` do `LI_2022_MARSTRUC`
> **cai** com a rugosidade (0,0874 → 0,0693 → 0,01 → 0,01 para Ra 0,078/0,122/0,306/0,80) —
> **contra o VDI 2230**, onde superfície mais rugosa encaixa MAIS —, e 4 de 6 sentam em
> 0,01 µm, que é embedding **praticamente desligado**. Pode ser legítimo (a fonte é 99 %
> creep), mas então **diga**, em vez de deixar valor anti-físico posando de calibração. O
> helper `emb_depth_vdi` existe e não é usado ali.
>
> ✅ **A ROTA ABERTA: as constantes estão sendo gastas onde o dado NÃO discrimina.**
>
> | fonte | banda do dado | grupos | constantes |
> |---|---:|---:|---:|
> | `BAUER_2024` | **0,4587** | 7 | **34** |
> | `ECCLES_2010` | 0,1866 | 10 | **54** |
> | `LIU_2022_RETIGHT` | 0,1402 | 4 | **48** |
> | `LIU_2025` | 0,0428 | 3 | **64** |
> | `LIU_2016` | **0,0136** | 2 | **14** |
>
> A alocação é **descorrelacionada da qualidade do dado**: o `BAUER` gasta 34 constantes onde
> as réplicas discordam em 0,459; o `LIU_2016`, com banda **34× menor**, recebe 14. Ela segue
> a **dificuldade de ajustar** — que é o que um fit faz.
>
> **O `BAUER` fecha um pacote coerente:** 7 grupos (um por réplica) + banda 0,4587 + as 4
> curvas que hoje reprovam **passariam no nível da condição** ⇒ **1 config por CONDIÇÃO
> (2 grupos, não 7)**, veredito lido contra a condição. Custo: o MAE por curva **piora**. A
> tese é que 2 configs para 9 curvas errando um pouco mais é mais defensável que 7 errando
> menos — e que a diferença cabe **dentro da banda do próprio experimento**. Isso é decisão
> sua, não medição.
>
> **Custo ZERO, medido:** 6 grupos com `cfg` efetivo **idêntico** a um irmão, colapsáveis sem
> tocar em número nenhum (`BAUER fig6_rep2/3/4`, `KARLSEN run2p2/7p1/14p2`, `âncora interna 13A
> first/def`, `MARSTRUC ra0p8/ra0p306` — este último é a §4 de outro ângulo: dois níveis de
> rugosidade com o mesmo config).
>
> **Ranking com custo (§8 do doc):** 1) BAUER por condição · 2) colapsar os 6 idênticos ·
> 3) declarar `creep_t_c` como **derivado** (para de contar botão que não existe) ·
> 4) resolver o `emb_um` anti-físico · 5) publicar a banda (ITEM Y) · 6) ~~constante → lei~~
> fechada.

### 🆕 ITEM Y (2026-08-23) — erro contra a **CONDIÇÃO**, não contra a réplica

> **Pergunta do professor:** *"não ajustamos a curva do ensaio, e sim a condição"*.
> Medição completa: `New_Theory/erro_contra_condicao_vs_replica.md`. **Nada executado** —
> mudança de métrica é decisão sua.
>
> **A tese já está adotada no projeto, para UMA adoção e não para a métrica.** O D-I
> (CACCESE 45 kN) registra: *"quando a condição tem réplicas, o alvo legítimo é o CENTRO
> delas; fitar contra uma é escolha arbitrária, e foi ela que produziu o defeito"*. A
> métrica nunca seguiu — ela pontua cada réplica contra o dado *daquela* réplica, e as duas
> correções que existem (**D1** afrouxa a barra por fonte; **F7** desculpa a curva) mexem no
> veredito sem mudar a **pergunta**.
>
> **Medido** (15 condições com réplica, **65 das 205** curvas, comparação pareada na mesma
> grade): o modelo está **DENTRO da banda que o dado não resolve em 10 das 15**, e o erro
> contra a réplica é **sempre ≥** o erro contra a condição. Se fosse porta, **7 curvas hoje
> reprovadas passariam**. O `LIU_2025` reprova nos **dois** níveis ⇒ a leitura
> **discrimina, não absolve**.
>
> ⚠️ **A RECOMENDAÇÃO INVERTEU no meio da medição, por experimento natural do mesmo dia.**
> Eu ia recomendar a leitura por condição como **porta**. Às 20:0x retratei as 2 provas do
> ECCLES e o erro contra a condição era 0,0851 — dentro da meta. Às 20:4x a sessão paralela,
> **porque as duas voltaram para a fila**, achou o `arrest_approach_exp` e adotou: res.máx
> individual **0,1320 → 0,0488** e **0,1463 → 0,0708**, as duas passando por MÉRITO. Com o
> dado **idêntico**, a diferença entre as duas leituras caiu de 0,0603 para **0,0211** (3×) e
> a banda não mudou (0,1866).
>
> ⇒ **duas consequências, e as duas mudam a proposta:** (a) a diferença entre as leituras
> **não é** o espalhamento do dado — ela caiu 3× sem o dado mudar, logo o erro por réplica
> cobra do modelo o espalhamento **e** o erro de forma dele interagindo com o espalhamento, e
> **uma medição isolada não separa os dois**; (b) como porta, ela teria custado a melhoria —
> ninguém procuraria a rota se as curvas tivessem "passado". Segunda instância do precedente
> **D-M** (*"recusar declarar-para-desbloquear forçou a medição que deu o resultado
> MELHOR"*), e vindica a retratação de hoje: ela não foi custo, foi o que pôs as curvas onde
> alguém as consertaria.
>
> **PROPOSTA REVISADA — diagnóstico publicado, NÃO porta.** A métrica por curva segue sendo a
> única porta (é ela que mantém a pressão que produz física). Ao lado dela, publicar erro
> contra a condição + banda + **razão** entre as leituras, e usar a razão como **triagem de
> esforço**: razão ≈1 com modelo fora de banda estreita (`LIU_2016`, `LU_2024`, `LIU_2025`) =
> defeito de forma, ataque direto; razão alta com banda larga (`BAUER` 1,6× em banda 0,46) =
> o experimento é o limitante e nenhuma forma nova resolve. A F7 fica como está.
>
> **O achado que sobrevive a qualquer decisão:** banda estreita + modelo fora = defeito;
> banda larga + modelo dentro = o dado não sabe responder. **A métrica de hoje não distingue
> as duas.**
>
> **Suas decisões:** (a) publicar o diagnóstico no report mestre, no por-caso, ou só no doc?
> (b) a razão entra como 4ª coluna da triagem de esforço? (c) reabrir a questão de porta se
> aparecer uma 2ª instância em que a leitura por condição aprove curva que **nenhuma** física
> conhecida fecha?

### ✅ ITEM X (2026-08-23) — ASSINADO E EXECUTADO no mesmo dia

> **Resultado:** `New_Theory/chave_estendida_pareamento_resultado.md` · prereg
> `specs/2026-08-23-chave-estendida-pareamento-prereg.md` · **8 gates verdes, G6 reprova
> como escrito** (gate mal especificado, não a mudança — está explicado nos dois docs e
> **não** foi reescrito).
>
> **O número que justifica:** a cegueira à variável varrida **inflava** a barra de σ do
> `ECCLES_2010` em **51 %** — piso 0,0852 com chave cega, 0,0698 com a lista manual,
> **0,0565** com a chave estendida. Barra inflada não reprova: **aprova**. Censo intacto
> (169/205), as 21 exceções preservadas, nenhum limite afrouxa.
>
> **Sobra, e é passo separado:** as **14 curvas** de `KARLSEN_2022` / `LI_2022_MARSTRUC` /
> `LI_2022_TRIBOINT` seguem bloqueadas à mão. O registry tem os 3 campos
> (`locking_device_type`, `initial_preload_N`, `frequency_Hz`); a chave não os lê porque
> entrariam na chave de **toda** fonte e mudariam pareamento onde ele está certo.
> ⚠️ **Não executar sem gate de isolamento próprio.**

<details><summary>enunciado original do item (preservado)</summary>

### ITEM X (2026-08-23) — trocar a lista manual de bloqueio por CHAVE ESTENDIDA

> **O que é:** a chave de família de réplicas é `(src, delta_mm, F_amp_N, mode)` — **cega** a
> grip, rugosidade, espessura, carga axial e espécime. É por isso que existe
> `_SEM_FAMILIA_MECANICA`, lista à mão com **81 curvas em 14 fontes**. Proposta: estender a
> chave pelos campos de input e aposentar a lista onde a chave já basta.
>
> **Por que agora:** os 6 campos de varredura entraram no `ValidationCase` hoje
> (`varredura_nao_e_replica_resultado.md`), lidos do `case_id`. Colisões de assinatura
> **57 → 21**, e as 21 restantes são todas corretas. O dado que a chave precisa **já existe**.
>
> **Medido (só-leitura, lista desligada + chave estendida):** pareamento espúrio
> **74 → 24 curvas (−68 %)**. Fontes resolvidas por inteiro: `ICMEZ_2025` · `JCSR_2023` ·
> `QIN_2024` · `ROUSSEAU_2025` · `SUN_2025_CRIMP` (+ `CHU_2026` reduzido à repetição
> genuína). Resíduo correto que **deve** ficar (15 curvas): `CACCESE rep1+rep2` ·
> `YANG_2021 r1+r2+r3` · `CHU test5+test6_repeat` · `LU amp1p0+T22Nm` ·
> `LIU_2016 1e6cyc+5e6cyc` · as 4 baselines sem axial do ECCLES (inclui o `fig8a`×`fig8c`,
> par legítimo que o bloqueio manual **proibia**).
>
> ⚠️ **O achado que muda o custo: os 3 tickets restantes (9 curvas) pedem, TODOS, campo que o
> registry JÁ TEM** — `frequency_Hz` (LI_2022_TRIBOINT, 10/15/20 Hz), `initial_preload_N`
> (LI_2022_MARSTRUC, 5/10/15 kN a Ra 0,8) e `locking_device_type` (KARLSEN, `M42_HV_run21p0`
> × `M42_vibralock_torqued_run29p0`, mesmo F_amp 274 kN).
> ⇒ **a lista compensa uma chave GROSSA — não falta de dado.** Levar `frequency_Hz` e
> `initial_preload_N` à chave é uma linha cada.
>
> ✅ **O precedente que valida a tese já está no repo, e foi pago à MÃO:** o par
> `eccles fig8a`×`fig8c` é **declarado** desde o prereg `eccles-par-replica-declarado`
> (2026-08-15), com **duas provas de exceção assinadas** repousando no piso dele. O motivo
> registrado no `report_html.py` é literalmente esta tese: *"o anterior era o piso INVÁLIDO
> que a P-15 retratou: dispersão entre cargas axiais de 0 a 3,5 kN, **a variável varrida do
> paper**"*. ⇒ o defeito já estava diagnosticado e foi consertado **declarando um par para uma
> fonte**; isto é o mesmo conserto **sistêmico**, a partir do input.
>
> **Por que NÃO executei:** a chave alimenta a **medição do piso**, e o piso é o que assina as
> exceções F7. Mexer nela sem gates poderia (a) fazer uma prova assinada perder o piso que a
> sustenta — e as 2 do ECCLES acima são o caso concreto —, ou (b) **subir** um piso e aprovar
> curva hoje reprovada. Pede prereg com gates sobre as provas vigentes; o §4.43 manda
> re-medir, não confiar no número de hoje.
>
> **O que destrava:** trocar 81 linhas de julgamento humano por regra derivada dos inputs, que
> é o pedido original (*"o que podemos fazer para não considerar replica uma variável?"*).

</details>

## 📍 ESTADO EM 2026-08-17 (00:5x) — medido, não citado

> ⚠️ **A 3ª perna NÃO é 0,025 em todo lugar, e o cabeçalho nunca dissera isso.** O limite é
> `max(0,025; piso medido da fonte)`, e **4 fontes** rodam com barra afrouxada — quem lê
> "censo 144/205" sem esta linha assume 0,025 em tudo:
>
> | fonte | `limite_sres` | × o global |
> |---|---:|---:|
> | `KARLSEN_2022` | 0,0903 | **3,6×** |
> | `BAUER_2024` | 0,0900 | **3,6×** |
> | `ECCLES_2010` | 0,0698 | **2,8×** |
> | `CHU_2026` | 0,0296 | 1,2× |
>
> ⚠️ O `ECCLES` saltou de 0,025 → 0,0698 na adoção do par `fig8a`×`fig8c` (item O, sessão
> paralela) — **sem mover o fingerprint**, porque a lista de pares declarados vive fora do
> hash (item **V** na mesa). **4 de 156** curvas do tripé têm a 3ª perna decidida por par
> declarado à mão — todas do `KARLSEN_2022` (`run2p2` · `run6p2` · `run7p1` · `M42_run21p0`), **re-medido 2026-08-20 sob o store `f2c01a123c8c`**. As demais fontes seguem no global.
>
> ⛔ **Este parágrafo dizia "8 de 144" — os DOIS números estavam vencidos.** O 8 eu já havia retratado para 4 em 2026-08-17 (contei curvas que passam a perna σ pelo piso **sem exigir que estivessem no tripé**), e o 144 é o censo de antes das 12 adoções de 08-19. A correção não chegara a esta linha — §4.43 dentro do meu próprio item.

Store **`db7de97e682a`** · censo **171/205** · fora **34** · **fila form-limited 0** ·
⚠️ re-carimbado em 2026-08-19/20 por **NOVE adoções que FECHAM no mesmo dia**
(SUN standard ×2 passos · LU T10 · ROUSSEAU ×4 — a fonte 8/8 — · ICMEZ ×3;
preregs próprios com gates congelados; a estrutura comum é constante com
procedência de LEITURA/regressão a observável de ROTAÇÃO publicado — Figs. 4/5/6
do Rousseau, Fig. 3 do ICMEZ = a caracterização de dreno dos autores) ·
⚠️ re-carimbado em 2026-08-16 (17:2x) pela **adoção R2** (item R, prereg `1f1a16d`): trocar
o **rótulo** de procedência de 2 pisos do `ECCLES` muda o fingerprint, porque o hash cobre a
entry inteira incl. `prov` — censo **inalterado**, 0 de 210 curvas com métrica alterada
(`eccles_rotulo_R2_resultado.md`). Antes: `20be19aabe11` ·
⚠️ fingerprint re-carimbado 2x em 2026-08-14/15: `c37618c5cc96` → `c9f028b015c0` (B/H-raiz, sessão B) → **`85e8104420b0`** (flanco no `LIU_2020_WEAR`, item M) → **`20be19aabe11`** (D-AD, `s1_amp_gate` no `LIU_2025`).
Censo **inalterado** nos dois primeiros; a D-AD levou **141 → 143**, e a correção do
pico espúrio do `LU_2024` (2026-08-16, dado-only ⇒ fingerprint **intocado**) levou
**143 → 144** ·
estatuto das 34 — exceção **19** · declarada **11** · classe-encerrada **4** ·
indecidível-sem-piso **0** · metric-limited **0** (soma **34** + fila **0** = **34** ✓ —
a fila havia ENCERRADO em 2026-08-21 17:0x com a decisão (b) do item 8 (a `amp0p8`
declarada por esgotamento medido, 17 estruturas falsificadas) e **REABRIU em 2** em
2026-08-23: as 2 provas de piso do `ECCLES` perderam a exceção quando o dedup de par
declarado tirou a **contagem dupla** do denominador. ⚠️ Não é o modelo que piorou — é
um piso **meu** que estava inflado. A parada segue **VÁLIDA**, com o reconhecimento
gravado em `parada_baseline.json`: a rota estrutural do ECCLES está **falsificada** (a
forma axial C3 morreu na monotonia piso-vs-axial, `53996b7`), não inexplorada, e nenhum
gatilho de mérito disparou. Prereg `fecha-tickets-e-dedup`.

> ✅ **Item W EXECUTADO em 2026-08-20 (23:0x)** — assinatura do professor
> (*"assinado, execute o W"*), prereg
> `docs/superpowers/specs/2026-08-20-classe-parada-curva-a-curva-prereg.md`,
> **gates G1–G6**. A `liu2025_M16_amp0p8` saiu da `classe_parada` por ser **falso
> positivo ESPELHADO** (viés terminal `mean(modelo−dado)` = **−0,0192** nas duas
> janelas ⇒ o modelo está *abaixo* do dado no fim, e o remédio da classe — acelerar
> mais — a **piora**). A fonte é **MISTA** (a `fig2_single` é membro genuíno, +0,0542),
> então a exclusão teve de ser **por curva** — 1ª vez que a campanha desce ao grão da
> curva nesta camada; a opção mínima da P-7 remove a *fonte* e levaria a irmã boa.
>
> **Censo `_censo()` bit-idêntico** (tripé 166 · resolvidos 188 · declarado_total 200);
> `classe_parada` 5→**4** e `form_limited` 0→**1**, e **nenhuma outra camada moveu**.
> ⇒ o item não melhora número nenhum: ele torna **honesta a fila publicada**, porque
> *"form-limited 0"* lia-se como *"não sobrou trabalho legítimo"* havendo **1** escondido
> por etiqueta que o discriminante da própria campanha reprova.
>
> A curva entra na fila com **uma perna violada** — σ_res 0,0419 (**1,68×**), MAE 0,79×
> e res.máx 0,86× **dentro** —, **sem rota F7** (piso da fonte = o global 0,0250) e com
> forma nomeada em `liu2025_par_de_taxas_opostas.md` (8 alavancas varridas, nenhuma
> fecha). Precisa de **40 %** em σ_res.

> ⚠️ **A "fila form-limited ZERO" de 2026-08-15 era artefato de DADO, não conquista.**
> A `lu2024_M8_fig20_T10Nm` carregava um pico espúrio (0,329 → **0,896** → 0,310) que
> a fazia cair >0,25 entre pontos vizinhos ⇒ o classificador a lia como *metric-limited
> por colapso quase-vertical* e ela saía da fila. Removido o artefato, ela **volta a ser
> a fila** — e é hoje a **única** curva form-limited do projeto. `metric-limited` foi de
> 1 para **0** pelo mesmo motivo. Correção: prereg `2026-08-16-lu2024-pico-espurio`.

> ⛔ **N′ EXECUTADO em 2026-08-15 (21:4x)** — `YANG_2019` saiu de
> `_FONTES_CLASSE_PARADA` (falso positivo inteiro, prereg `52a1a87`, assinado 21:42).
> `classe-encerrada` 6→**5**, `indecidível` 14→**15**, **censo 143/205 inalterado**,
> `form_limited` segue **0**. A curva **não fechou** — migrou de *"encerrada pela
> classe"* para *"não julgável, falta réplica"*.
>
> ✅ **P FECHADO SEM CÓDIGO NOVO**: a guarda que eu ia construir **já existe**. O risco
> (retratar exceção do `CHU_2026` faz a curva escorregar em silêncio para
> `classe_parada`) é pego pelo `test_classe_parada_nao_cresce_calada`, verificado por
> **perturbação** — removendo `chu2026ti_D0p4mm_F0_49kN_test2` de `_EXCECOES` em
> memória, ele falha nomeando a curva. Verificar bateu construir.

> ✅ **Esta linha passou a ser VIGIADA em 2026-08-15 (16:0x)** — 5 âncoras novas em
> `_VIVAS` + a guarda estrutural `test_a_soma_das_camadas_e_o_fora`, alimentadas pelo
> helper `_camadas()`, que chama o **classificador canônico** da
> `regra_de_parada_triagem` em vez de reimplementá-lo.
>
> ⚠️ **O motivo é medido, não estético:** o par “64 / classe-encerrada 8” conviveu com
> “fora 62” **no mesmo parágrafo**; consertei à mão às 14:5x e **às 15:51 já estava errada
> de novo** (exceção 22→23, indecidível 15→14, pela assinatura SUB-SLIP das 15:09). Uma
> linha que envelhece em **uma hora** não se conserta à mão — se guarda.

> ### 🔧 Forma nova no engine, **validada e NÃO adotada** — e a não-adoção é o resultado
>
> `emb_clock_delta_ref` (relógio de assentamento ∝ 1/δ) está no engine, **default-inerte**,
> com **paridade 8/8 ao 12º dígito** contra a sonda que calculava o `N_emb` à mão, e
> **inércia bit-a-bit nas 210**. O expoente **1 não é ajustável** — vem do mecanismo, e um
> teste proíbe que apareça campo para mudá-lo.
>
> ⛔ **Não foi adotada**: na fonte inteira ela ganha a `test9` mas piora a `test3` em
> **+0,0392** no σ, **4× acima** da tolerância de +0,01. A variante limpa (só o relógio,
> sem o nível) passa o gate e ganha **zero**. As duas maneiras de escopar o grupo estão
> medidas; nenhuma é adotável, e estreitar o grupo para capturar o +1 seria mover a trave.
>
> ⚠️ **O que isso descobriu vale mais que o +1**: dentro da **mesma classe de rugosidade**
> (Ra 0,4 µm, Tabela 1 do artigo) o `emb_depth` exigido salta **≥15×** entre δ=0,3 e
> δ=1,0 mm. Quando uma constante precisa mudar 15× dentro da própria classe física, ela
> deixou de ser a constante que o nome diz. ⇒ **item B fica insuficiente em princípio** e
> nasce o **item I** (alvo dependente do deslocamento) — com o candidato óbvio, potência
> única em δ, **já falsificado** pelos 3 pontos.
>
> Prova: `New_Theory/lei_relogio_implementada_e_nao_adotada.md`.

### Estado do meio-dia (2026-08-14) — preservado

## 📍 ESTADO EM 2026-08-14 (meio-dia) — medido, não citado

Store **`cb019d75c6c2`** · censo **141/205** · suíte **933/1** · **fila form-limited ZERO** ·
item **A CONVERGIDO** (13/467, cobertura **97 %**) · leitura dupla: estrita **140**,
resolvida/declarada **180**.

> ## 🏁 A FILA DE TRABALHO LEGÍTIMA ESTÁ VAZIA (2026-08-14, item F executado)
>
> As 8 órfãs de protocolo do `LU_2024` foram declaradas ⇒ **`form_limited` = 0**. Toda curva
> fora do tripé tem agora **estatuto documentado**: 22 exceção · 18 declarada ·
> 9 classe-encerrada · 15 indecidível-sem-piso · 1 metric-limited.
>
> ⚠️ **Isto NÃO é "o modelo acertou".** A leitura estrita segue **140/205**, e o modelo erra
> nas 65 de fora — em algumas, muito (`fig14_amp1p0_long` a 9,6× o limite de MAE). O que
> acabou foi a fila de curvas que **ainda tinham rota**; o que resta é bloqueado por dado,
> por protocolo ou por classe encerrada, cada uma com a prova registrada.

⚠️ **O censo caiu 146 → 140 às 12:45** com a execução de **G+H** (`2335090`): pisos ilegítimos
bloqueados (`ICMEZ` cego ao grip, `CHU` δ=0,5 cego à rugosidade). **Predição 10/10 exata** —
as 6 que eu previ que sairiam saíram, as 4 que sobreviveriam por mérito sobreviveram, e o
limite do `CHU` caiu para 0,0296 ao dígito. As 5 do `ICMEZ` foram para
`indecidivel_sem_piso` (10 → 15). **Não é regressão do modelo: é a retirada de censo que
repousava em piso falso.**

⚠️ **Na mesa agora: 7 itens** (A convergiu; **F**, **G** e **H** entraram em 08-14; **G** e
**H** já executados às 12:45). Os três novos vieram de auditorias de **premissa não testada**,
e os três têm custo **negativo** de censo — o que é o sinal de que são correções, não ganhos.

### 🔍 As células de CUSTO foram re-medidas em 2026-08-14 ~13:55 — 1 de 4 estava vencida

Motivo: **contagem tem guarda (`_VIVAS`), estimativa de custo não** — e é o custo que decide.
Um censo errado é constrangedor; um **custo** errado faz escolher a opção errada.

| item | célula publicada | conferida hoje |
|---|---|---|
| **B** | "tripé CHU **3→1**" | ⚠️ **VENCIDA** — o CHU está em **2/9** desde o G+H; o "3" não existe mais e o delta precisa ser re-medido |
| **D** | "**8 de 9** curvas do CHU rodam em DEFAULTS" | ✅ **exata**: só a `test1` tem override (15 campos); as outras 8 em defaults |
| **E** | "`r1` a **7 %** do σ" | ✅ **exata**: σ 0,0268 contra limite 0,0250 = **107 %** |
| **F** | 8 órfãs, 3 instrumentos, sem rota | ✅ medida hoje |

⇒ **a assimetria é estrutural:** o censo é recomputável do store a qualquer momento; o custo é
uma **contrafactual** que só existe no registro de quem a mediu. A única defesa é **datá-lo e
invalidá-lo quando a base se move** — foi o que o G+H fez com o item B.

⚠️ **Erro de bookkeeping meu, consertado aqui:** havia **duas** linhas de item A no arquivo
(uma na tabela "o que mudou", outra na tabela da mesa) e eu vinha atualizando **só a
primeira** — a tabela que o professor lê ficou parada na fase 2 (141/70 %) enquanto a outra
dizia 24/95 %. É o §4.43 cometido por mim, e o `test_meta_numeros_nao_envelhecem` não pega
porque ancora afirmações específicas, não toda linha de tabela.

### Estado anterior (2026-08-13, noite) — preservado

Store **`72a7aca6311e`** · censo **147/205** · fora **58 = 32 com estatuto + 26 abertas** ·
**fila form-limited 2** (as duas `lu2024_M8_fig14_*_long`) · suíte **929/1** · leitura dupla:
estrita **147**, resolvida/declarada **179**.

Abertas por proposta: **P-7** 8 · **P-13** 7 · **P-9** 5 · **P-14** 4 · **dado** 2.

Estatuto das 58 fora, medido: exceção assinada **21** · declarada **11** ·
classe-de-parada (aceleração tardia) **14** · indecidível sem piso **10** · form-limited **2**.

### O que mudou em 2026-08-13

| | |
|---|---|
| **item A** | passivo **238 → 206 (errata) → … → 32 → 24 → **13** (2026-08-23)**; cobertura **49 % → 95 %** — **90 % do passivo original resolvido**, deriva **zero** provada nos 210 nas **dez** fases | restam 24, sem concentração | ⚠️ **4 convenções de chave de `prov`** achadas (exata · composta `a/b/c` · nome curto de família · composta **anotada**); política: **entrada explícita**, nunca mais uma camada de esperteza no lookup |
| **item C** | ⛔ **FECHADO — a premissa era falsa.** A `prov` que ele dizia faltar existia desde 2026-07-12, numa **chave composta**; a assinatura ficou sem objeto |
| fingerprint | `bd74eaf0b11d` → `66356f20faf8` → `72a7aca6311e` → `98f90e11ebb0` → **`523ea0069b0d`** (f4) |
| catraca | corrigida (lookup token-aware) e **apertada**: baseline 238 → 206 |

⚠️ **O ESPAÇO DE ARGUMENTO DE CLASSE ESTÁ EXAURIDO** (medido ao fim da fase 3). As três
fases pegaram tudo que se documenta por **uma frase para N constantes**: campo uniforme em
valor (*starters*, defaults de pack, canal desligado) ou valor auto-documentado (`emb='Rz<4'`
= classe VDI; `mu='Motosh …'` = método + números). O que resta são **127 constantes
dispersas em valor** — `k_wear_scale_tr` 11 · `emb_um` 9 · `emb_depth` 8 · `c_D` 6 ·
`C_creep` 6 —, e cada uma exige **ler a adoção que a fixou**. Não há mais atalho barato:
**as fases 4+ são arqueologia por constante**. ⚠️ **A fase 4 (2026-08-13) mostrou que isso e' mais barato do que parece — mas só porque os preregs da campanha são bem escritos**: as 15 saíram de DUAS frases já escritas em 2026-07-11 (*"nível M12 não-colapsante (level probe)"* e *"emb LIDO 1,09 µm"*). Nada foi re-derivado; tudo foi **encontrado**.

Protocolo **escritor-declarado** em `procedencia_custo_do_backfill_resultado.md` — quem tomar
uma fase declara lá antes, porque cada lote exige re-stamp completo e dois re-stamps
concorrentes destroem a **prova de deriva** (não os números).

### Adoções desde 08-09 (todas com prereg de gates congelados ANTES)

| passo | o que | gates |
|---|---|---|
| **D-Z** | forma do creep nas 2 curvas de água do mar do `JCSR_2023` | 5/5 |
| **D-AA** | varredura **CONJUNTA** forma×nível — fecha a `stainless` | 6/6 |
| **D-AB** | `C_creep` **per-par** no `ECCLES_2010` — a `fig7c` fecha | 6/6 |
| **D-AC** | `k_wear_spec` no `YANG_2019` — a regra do **artigo** escolheu | 6/6 |
| **D-AD** | `gth` (ratchet de stick) no `YANG_2021` — mediana **−27 %**, censo 0 | 6/7, W6 não avaliável |

### ⚠️ As 6 lições de método que valem mais que as adoções

1. **Varredura MARGINAL declara ótimo CONDICIONAL.** Diagnóstico grátis:
   `|viés|/MAE → 1,00` = resíduo de sinal único. ⚠️ **e ele é AMBÍGUO** entre offset e
   **rampa** — o discriminante é `ρ(resíduo, N)` (≥0,7 ⇒ taxa; ≤0,3 ⇒ nível).
2. **CLASSE MECÂNICA antes da alavanca.** Instrumentando `resolve_transverse_slip` nas 150
   curvas disp-mode: **STICK 18** (tripé 33 %) · **GROSS 70** (76 %) · **PARCIAL 62** (52 %).
   Alavancas **disjuntas** por classe; em STICK nenhuma alavanca de slip alcança.
3. **Constante COMPARTILHADA exige DRIVER uniforme.** Canal de **tempo** (creep) atravessa
   fonte mista; canal de **slip** só funciona em fonte **homogênea de classe** *e* de
   **modo** (disp × força). **7 predições corretas.** Corolário medido: **o espaço de
   canal-de-slip compartilhável está EXAURIDO** — 22 das 26 abertas barradas por
   heterogeneidade, 2 por mistura de modos, e as 2 fontes elegíveis estão fechadas.
4. **Gate de censo ABSOLUTO é frágil sob escritor paralelo**; o robusto é o **diferencial
   confinado** (nada muda fora do escopo + nada sai dentro dele).
5. **Auditoria que não conhece o formato do que audita mede a própria rigidez** (08-13). A
   varredura de procedência usava lookup **exato** e a campanha grava **chaves compostas**
   (`'c_bend/emb_depth/floor'`) quando um argumento cobre várias constantes ⇒ **32 falsos
   positivos**, um passivo inflado de 206 para 238, e **uma decisão pedida ao professor sobre
   um problema inexistente** (item C). Antes de publicar cobertura, confira como o dado é
   **armazenado**, não só se a chave existe. Corolário: *"sem `prov`"* quer dizer **"não
   indexado onde eu olhei"** — o `k_dmg_mu = −2,43` do CHU parecia fit cego e a âncora (*"µ
   subindo, o sinal da Fig. 5"*) estava no `MODEL_LEGITIMACY` que eu mesmo mantenho.
6. **Sonda de proximidade textual sobre o corpus da própria campanha lê a própria saída como
   evidência** (08-13, dois números errados na mesma pergunta). v1 exigia campo perto da
   fonte → **99 %**, porque o corpus incluía as tabelas de auditoria que *enumeram* os campos
   indocumentados. v2 exigia o valor sem vínculo com a fonte → **81 %**, porque `0,2`/`1,0`
   estão em toda parte. v3 (campo + valor + fonte, corpus limpo) → **63 %**, e só esse saiu
   publicado, com **8 hits conferidos à mão** (6 genuínos ⇒ precisão ~85 %). ⇒ **exclua os
   documentos que falam do objeto medido, e nenhum agregado sai sem amostra lida.** O que
   pegou os dois erros foi **ler as linhas**, não revisar a fórmula — igual ao audit de trim,
   cujas curvas "mais trimadas" tinham `trim = None`.

### ✅ MARCO 2026-08-19 (18:5x) — `form_limited` = **0**, e desta vez o zero é REAL

> **Medido, não citado:** censo **146/205** · fora 59 · abertas 19 · **`form_limited` 0** ·
> config e store **sincronizados** em `4c14f69f1d81`. Duas curvas fecharam **por modelo** no
> mesmo dia (sessão paralela): `sun…transverse_grease_standard` e `lu2024_M8_fig20_T10Nm`.
>
> ⚠️ **A primeira coisa a fazer com um "fila ZERO" aqui é DESCONFIAR DELE**, porque o
> `CLAUDE.md` registra que a *"fila form-limited ZERO"* de **2026-08-15 era ARTEFATO** — um
> pico espúrio tirava a `T10Nm` da fila por colapso falso. Conferi com a guarda que pegou
> aquele: `test_curvas_sem_pico_espurio` **7/7 verde**.
>
> **E as duas fecham com FOLGA nas três pernas, não na borda:**
>
> | curva | MAE | res.máx | σ |
> |---|---:|---:|---:|
> | `lu2024_M8_fig20_T10Nm` | **0,40×** | **0,34×** | **0,70×** |
> | `sun…transverse_grease_standard` | 0,38× | 0,43× | 0,89× |
>
> A `T10Nm` vinha de **5,03× · 3,15× · 3,00×**. ⇒ o zero **não é** artefato de dado.

> ⚠️ **O QUE O ZERO NÃO SIGNIFICA.** Ele diz que **nenhuma curva aberta tem hoje rota de
> trabalho identificada** — não que o modelo esteja pronto. As **19 abertas** seguem fora:
> **5** em classe encerrada, **14** `indecidivel_sem_piso` (o dado não permite julgar; a
> Fase 1 da sessão paralela mediu que **não existe par válido** nas 5 fontes), e **3** com
> motivo medido (`YANG_2023`: 3 regimes, 3 sinais, não formam classe). A leitura honesta
> segue sendo dupla, e a que falta é **dado novo** — que é o item **F3** desta mesma mesa.

### ✅ ATUALIZAÇÃO 2026-08-19 (21:1x) — as guardas vermelhas caíram de 17 para **1**, e ela é UM NÚMERO

> **Medido, não citado.** A sessão paralela fechou a dívida de escrituração das adoções de
> hoje: `test_prereg_declara_estado` **verde** (declararam estado nos 5 preregs), as **40**
> guardas de censo **verdes** (documentos vivos re-sincronizados), `test_curvas_sem_pico_espurio`
> **7/7**, e a minha S1 **verde** (13 alegações, 0 violações).
>
> **Sobra exatamente UMA:** `test_dof_reduction_software::test_kb_sensitivity_and_dof`, e o
> assert virou **`assert 118 < 118`** — é o **tripwire de CONTAGEM de campos** de
> `JointMaterial`, não mais o `arrest_approach_exp` virando fitado.
>
> ⚠️ **E o requisito COMPANHEIRO já está cumprido**, o que estreita muito o que falta: o
> `CLAUDE.md` manda que campo novo de `JointMaterial` ganhe um `VarSpec` senão o
> `test_variable_explorer` falha — **ele passa 19/19**. Os dois campos novos
> (`free_spin_kin`, `arrest_approach_exp`) **estão** documentados; `JointMaterial` está em
> **118**.
>
> ⇒ a dívida não é de física, nem de cobertura, nem de procedência: é **o limiar do tripwire
> não tendo acompanhado os 2 campos que a adoção adicionou** (116→117→118 é a série que o
> próprio `CLAUDE.md` registra). Segue sendo dos donos da adoção — mas é um número, não uma
> investigação.

### ⚠️ AVISO DE ESTADO (2026-08-19 16:4x) — DUAS guardas VERMELHAS deixadas por adoção

> **Não é meu e não conserto** (um escritor por recurso) — mas guarda vermelha sem resposta
> lê como *"a suíte está quebrada"* em vez de *"uma adoção deve uma declaração"*, e a
> próxima sessão que rodar a suíte inteira vai encontrar isso primeiro.
>
> A adoção do **kernel cinemático na `sun…grease_standard`** (`7adaca7` + `bfaf773`) pousou
> corretamente: store re-carimbado **`76a39eb7e17b`** uniforme (210), config sincronizada,
> pior perna **4,73× → 1,62×**. ✅ Censo **144/205 inalterado** (a curva melhorou sem fechar).
>
> **Ficaram 2 testes vermelhos, os dois pedindo ação explícita:**
>
> | teste | o que ele diz |
> |---|---|
> | `test_dof_reduction_software::test_kb_sensitivity_and_dof` | **`arrest_approach_exp`** *"deixou de ser dormente e agora é FITADO por config adotada"*; campos tocados por alguma adoção: **65**. A mensagem exige *"tire-o da lista e atualize §4.42/MODEL_LEGITIMACY, **ou reverta a adoção**"* |
> | `test_prereg_declara_estado::test_prereg_novo_declara_estado` | o prereg `2026-08-19-sun-standard-kernel-cinematico` está **sem declaração de estado** no formato que o teste exige |
>
> ⚠️ **A 1ª está em tensão com a manchete da própria adoção**, que diz *"troca de forma,
> **MESMO DOF**"*. As duas podem ser verdadeiras ao mesmo tempo — "mesmo DOF" no sentido de
> *nenhum parâmetro livre novo no fit* (troca de forma), e o tripwire medindo a **contagem
> de campos TOCADOS**, que cresceu. Mas a distinção precisa ser **escrita**, porque é
> exatamente o que o teste pede: ele não aceita "mesmo DOF" como resposta, aceita a lista
> atualizada **ou** a reversão.

### Na mesa do professor — ✅ DECIDIDAS POR DELEGAÇÃO em 2026-08-20 ("tome as decisões por mim", 08:14)

> ✅ **F3 (dado novo ICMEZ) — RETIRADA POR MÉRITO.** A motivação era "5 curvas
> dependem de repetir uma condição"; as 5 (e as 8 da fonte) **fecharam por
> modelo em 2026-08-19/20** (Fig. 3 = a caracterização de dreno dos autores +
> settling lido). O pedido de réplica perdeu o objeto para o CENSO; fica
> registrado como *validação externa desejável* (uma réplica ICMEZ testaria as
> predições sem custo de modelo) — prioridade baixa, não bloqueia nada.
>
> ✅ **F4 (regra de parada) — NÃO DISPARA; avaliação vencida em 3 dias.** O
> critério (c) exigia *retorno marginal nulo*; entre a avaliação (2026-08-16)
> e a decisão (2026-08-20) houve **12 fechamentos por mérito num dia** (censo
> 144→156), a maioria por FORMA NOVA (`free_spin_kin`) + leitura — exatamente
> o que o plano dizia não estar acontecendo. A regra fica NÃO-ASSINADA; o 3 %
> do critério (c) será re-derivado quando o ritmo estabilizar (guarda de
> reabertura `test_parada_reabre_quando_deve` segue armada).
>
> ✅ **YANG_2021 ×3 — exceções NÃO assinadas (o rigor vale contra nós).**
> Medido em 2026-08-20 pelo helper canônico: o trio 0,6 mm/8 kN tem piso
> σ = **0,0103** — as réplicas concordam entre si 2,6× melhor que o modelo
> concorda com elas (r1: 0,0268). A prova F7 exige piso da MESMA condição
> cobrindo as pernas violadas: a r1 tem piso e ele NÃO a cobre (defeito de
> MODELO demonstrado por réplica — material de artigo, não de exceção);
> amp0p5/amp1p0 não têm réplica na condição (violam mx E σ; prova impossível).
> As 3 ficam ABERTAS com veredicto medido.
>
> ✅ **Régua de "dispersão de espécime" (4 fontes) — SEM régua nova.** A
> mecânica F7 existente já é a régua: exceção exige prova de piso da própria
> condição. Classe reconhecida como fenômeno (registrada nos dossiês), não
> como categoria de assinatura automática.

> ✅ **Item (e) da fila antiga (conferência visual do 1º ponto,
> `yang2021_amp0p7` +9,9 % e `yang2019_varamp` +8,5 %) — EXECUTADA 2026-08-21
> (21:0x), os dois sinais têm explicação MEDIDA e a conferência sai da fila de
> manutenção também.** A amp0p7 foi re-ancorada pelo D-U: y[0] cru = **1,0000
> exato** hoje (o +9,9 % morreu com a re-ancoragem por centros). O +8,5 % da
> varamp EXISTE no cru (y[0]=1,0846) e é **overshoot de aperto DOCUMENTADO na
> nota de aparato** (`yang2019_sv_M10.md` L41: *"starts ~1.08: tightening
> overshoot band"*) — verdade-de-dado da digitalização, não erro de âncora.
> Nada a corrigir; 6ª instância de "a prova já estava escrita no repositório".
>
> ✅ **Item (c) da fila antiga (publicar estrito e declarado juntos ou só um) —
> FORMALIZADO: sempre DUPLO.** Já era a prática de todos os docs vivos
> (estrita 156/205 · resolvida/declarada 196/205); vira regra declarada.

#### (registro histórico do que estava na mesa)

### ~~Na mesa do professor — **2 decisões** vindas do plano das 21 abertas (sessão paralela)~~

> ⚠️ **PONTEIRO, não análise minha** (acrescentado 2026-08-16 20:1x). O plano da sessão
> paralela (`bac5bf7`, `New_Theory/plano_das_21_abertas.md`) contém **duas decisões que são
> suas** e que ficaram só no arquivo — a mesa dizia "ZERO abertos" enquanto elas esperavam.
> O conteúdo é deles; aqui vai só o índice.
>
> **O achado que as motiva:** uma pergunta medível — *a fonte tem piso de repetibilidade?* —
> parte as 21 em dois grupos com trabalhos **diferentes**, e em nenhum o próximo passo é
> "atacar a curva". **Grupo A (6)**: o piso existe e as **condena** (o σ do modelo é 1,8× a
> 23× o ruído do próprio dado). **Grupo B (15)**: o piso **não existe**, e não é falta de
> procurar — os pares candidatos diferem em grip, espessura, tratamento, ou a fonte
> simplesmente não repete condição. ⇒ para 15 das 21 **não se sabe se o modelo erra ou se a
> barra é dura, e a resposta não está no modelo**.
>
> | | decisão | de quem |
> |---|---|---|
> | **F3** | só **dado novo** resolve o Grupo B. Alvo mais barato: **`ICMEZ`** — mesmo rig, 8 curvas já existem, falta **repetir UMA condição sem mudar o grip**. 5 curvas dependem disso, e 4 delas já passam MAE e res.máx | **sua** |
> | **F4** | rodar a **regra de parada** com número: os 3 critérios parecem satisfeitos (18/21 com forma nomeada; as últimas 4 candidaturas caíram todas por gate próprio; os ganhos recentes vieram de **dado** e **procedência**, não de forma nova) | eles medem, **você decide** |
>
> **O que eles explicitamente NÃO recomendam:** atacar as 21 como fila; baixar a barra de
> σ (o dado do Grupo A é 1,8–23× mais repetível que o limite); declarar as 15 para inflar o
> "resolvido" — isso transformaria limitação de **dado** em aparência de **acerto**.
>
> ⚠️ **Verifiquei o que o plano afirma sobre a minha área** e confere: o par
> `fig8a`×`fig8c` do `ECCLES` foi adotado e `limite_sres(ECCLES_2010)` é hoje **0,0698**
> (era 0,025). Confirmei também que a adoção deles **não varreu** os meus rótulos do R2
> (`proxy-de-desaceleracao-de-cauda` segue nos 2 grupos) e que a guarda S1 continua em
> **5 alegações · 0 violações**.

### Itens MEUS — **3 abertos** (**T** · **U** · **V**), nenhum urgente, nenhum move censo

> 💡 **SUGESTÃO DE DESPACHO EM BLOCO:** **T1 · U1+U2 · V2** são os três de menor custo, os
> três já satisfeitos pelo estado atual, e **nenhum reabre a parada nem move o censo**.
>
> ⚠️ **ITEM V (2026-08-16, 23:0x) — declarar um par muda o tripé de uma fonte inteira SEM
> mover o fingerprint.** Aguarda assinatura; **nada executado**.
> Detalhe: `New_Theory/par_declarado_muda_o_tripe_sem_mover_o_fingerprint.md`.
>
> `engine_fingerprint()` hasheia **`{shared, adopted}`** e mais nada. Os pares de réplica
> declarados vivem em **`report_html.py::_PARES_REPLICA_DECLARADOS`**, que **não entra no
> hash** — e alimentam `_pisos_medidos` → `limite_sres(fonte)` → **a 3ª perna do tripé**.
> ⇒ uma linha naquela lista muda o veredito de uma fonte inteira e o fingerprint **não se
> move um bit**. Caso real: a barra de σ do `ECCLES_2010` ficou **2,8× mais permissiva**
> (0,025 → **0,0698**) em silêncio.
>
> **Medido — quantos vereditos dependem disso: 4 de 144 (2,8 %)**, todas do
> `KARLSEN_2022` (`run2p2` · `run6p2` · `run7p1` · `M42_run21p0`).
> ⛔ **ERRATA 2026-08-17 (09:5x): eu publiquei 8 e o número é 4.** Contei curvas que passam
> a perna σ pelo piso **sem exigir que estivessem no tripé** — curva que passa o σ e reprova
> no MAE ou res.máx **não está no censo**, logo o par não decide nada sobre ela. **Zero do
> `ECCLES`.** (E antes disso eu ia publicar **15**, corrigido para 8 porque `_pisos_medidos`
> também pareia **automaticamente** — as 7 do `BAUER` vêm do automático.) O argumento
> estrutural não muda; a magnitude caiu à metade e o alvo é **uma** fonte.
>
> ⚠️ **O baseline da parada (`0a9e5f7`, sessão paralela) NÃO cobre isto — e é complementar.**
> Eles congelam o **piso da fonte** por curva, então declarar par que mova um piso dispara a
> guarda deles — **mas só para as 6 curvas da `fila_julgavel`**. As 4 afetadas estão **no
> tripé**, fora daquela lista. ⇒ a guarda deles protege a **decisão de parar**; o item V
> protege o **número publicado**.
>
> **O problema é o SINAL, não a legitimidade dos pares** (cada um tem prova, e a campanha já
> retratou 5 pareamentos inválidos). O §4.43 diz que uma pendência *"vira suspeita assim que
> o fingerprint muda"* — mudança que **não** move o fingerprint **nunca dispara** isso.
> ⚠️ **Justiça com a regra de parada:** a cláusula de reabertura dela **já cobre** o caso
> (*"reabre se … o piso de qualquer curva da fila mudar"*). O furo é do **§4.43**.
>
> | rota | ação | custo |
> |---|---|---|
> | **V2** (recomendada) | guarda que **congela a composição** da lista e falha nomeando quem entrou/saiu — padrão do `test_classe_parada_nao_cresce_calada.py`. Torna audível **sem re-carimbo** | baixo |
> | **V1** | incluir a lista no `engine_fingerprint` — mais forte, mas **muda o fingerprint hoje** e obriga re-carimbo dos 210 | médio |
> | **V3** | não mexer | ⛔ 8 vereditos governados por lista não vigiada |
>
> ⚠️ **SÍNTESE 2026-08-19 (14:5x) — o piso de σ é estreitado DUAS VEZES, e isso compõe
> com o item V.** A sessão paralela mediu (`e41bc4b`) *dispersão de ESPÉCIME invadindo a
> janela da métrica* em **3 fontes independentes** (`YANG_2021` vidas 12400/14649/16251 com
> sinais de resíduo OPOSTOS na mesma célula de inputs; `LIU_2025` par da mesma condição com
> vidas 9870/14400, **46 %**; `LU_2024` retenção terminal não-monótona **publicada**), e
> apontaram que o piso *"é medido na janela comum, onde os espécimes ainda coexistem no
> platô — a dispersão de vida na cauda NÃO entra nele"*.
>
> ✅ **Conferido no fonte, e é mais forte do que eles enunciaram.** `_pisos_medidos`:
> (a) interpola *"numa grade de 40 pontos na janela de x **comum** (interseção)"* (L3020)
> ⇒ se uma réplica colapsa antes, a janela termina onde a mais curta termina, **excluindo a
> divergência**; e (b) lê **`metric_x`/`metric_data`** (L3041), que já são **pós-`FLOOR_TRIM`**
> ⇒ a cauda abaixo de 0,10 está fora **por construção**.
>
> ⇒ **a barra de σ tem TRÊS propriedades estruturais que apontam todas na mesma direção**
> (barra apertada demais em relação ao scatter real):
>
> | # | propriedade | de quem |
> |---|---|---|
> | 1 | governada por lista que o **fingerprint não vigia** (4 vereditos) | item **V** (meu) |
> | 2 | medida na **interseção** das janelas ⇒ exclui a divergência | conferido agora |
> | 3 | medida sobre **`metric_data`** ⇒ exclui a cauda < 0,10 | conferido agora |

> ⚠️ **Não proponho mexer no piso.** Eles escreveram a frase certa — *"se isso virar
> régua, é decisão do professor; não desenho a barra que me aprova"* — e ela vale para mim
> igual. O que a síntese muda é o **peso do V2**: uma guarda sobre a composição da lista
> custa pouco e passa a proteger um número cuja fragilidade agora tem **três** causas
> medidas, não uma.


> ⚠️ **ITEM U (2026-08-16, 22:0x) — o critério (c) da regra de parada é satisfeito com MAIS
> facilidade quanto PIORES os instrumentos.** Aguarda assinatura; **nada executado**.
> Detalhe: `New_Theory/criterio_c_da_parada_e_infalsificavel.md`.
>
> **Observação independente sobre a F4** (`4f74790`, sessão paralela). **Não contesto o
> veredito** — (a) e (b) satisfeitos, (b) já com ressalva de escopo escrita por eles. É
> sobre a **estrutura** do (c).
>
> O (c) pede: *"após os 3 candidatos mais recentes, zero curvas saíram por mérito **e** a
> mediana caiu < 3 %"*. O argumento que o satisfaz é *"nenhum foi adotado, logo nada
> mudou"*. ⛔ Mas se nenhum é adotado a mediana **não pode** se mover — por aritmética, não
> por evidência. ⇒ o (c) fica satisfeito por **qualquer** sequência de reprovações,
> **inclusive as que reprovaram porque o TESTE era inválido**.
>
> **Forma afiada:** campanha com instrumento quebrado produz candidatos que todos falham,
> nada se move, e o (c) declara *"retorno marginal nulo"* — quando a verdade é *"não
> conseguimos medir"*. Inverte o sentido do critério.
>
> ⚠️ **A própria regra já tem o antídoto — só não no (c).** A tabela de candidatos marca o
> Cattaneo-Mindlin como `INCONCLUSIVO` com a nota *"**não conta para (b)**"*. O vocabulário
> existe e a proteção está anexada ao **(b)**; o **(c)** não a tem — e é justo o critério
> onde *ausência de movimento é o sinal*, logo cego a **por que** nada se moveu. Mesma lição
> que a campanha pagou em 2026-07-30 (2×), um nível abaixo.
>
> **E a lista de 4 da F4 já contém um caso da espécie:** o **piso do `YANG_2023`** é
> **INCONCLUSIVO**, não falsificado — o prereg (`093050e`) congelou gates sobre a premissa
> *"o dado arresta em 0,165"*, que é **falsa** (eu lera `metric_data`; o cru colapsa a
> 0,02–0,06). Retratado em `13ed862`/`0822572`. **Aquele candidato nunca foi testado**, e
> contá-lo é contar um teste vazio a favor de parar.
>
> | rota | ação |
> |---|---|
> | **U1** (recomendada) | anexar ao (c) a **mesma** cláusula do (b): ramo `INCONCLUSIVO` **não conta** para os 3. Custo: uma frase |
> | **U2** (junto) | exigir que ≥1 dos 3 tenha sido `FALSIFICADO` **por mérito** com predição cumprida — hoje **satisfeito com folga**: **3 de 4** (`emb_pressure_exp`, `loose_arrest_residual`, `k_ratchet`) |
>
> ⛔ **ERRATA 2026-08-17 (22:5x) — o placar era 2 de 4 e é 3 de 4.** Eu classificara o `loose_arrest_residual` como *"não é candidato — nunca foi proposto"* e criara sobre isso uma **terceira espécie**. **Falso:** o prereg existe (`2026-08-15-lei-de-taxa-rotacional-prereg.md`, 7 gates) e o §RESULTADO dele diz *"adoção **FALSIFICADA** pelos próprios gates · NÃO ADOTADO"*. Errei por procurar prereg pelo **nome do campo** em vez do nome da **lei**. Quem me corrigiu foi o prompt anti-redescoberta da sessão paralela (`eedc424`), que diz certo. ⇒ a **terceira espécie não tem membro e está retirada**; o argumento central do U **sobrevive** (o `YANG_2023` segue sendo teste que nunca rodou contado a favor de parar), mas em **1 de 4**, não 2. Detalhe: `criterio_c_da_parada_e_infalsificavel.md` §5a–5b.
> | **U3** | não mexer |
>
> ⚠️ **U1+U2 são satisfeitos pelo estado de hoje** ⇒ adotá-los **não reabre a parada**; só a
> torna defensável pela razão certa.

> ⛔ **ITEM T (2026-08-16, 21:0x) — o rótulo que EU adotei às 17:2x super-afirma na
> `fig8a`.** Aguarda assinatura; **nada executado**.
> Detalhe: `New_Theory/r2_rotulo_superafirma_na_fig8a.md`.
>
> A adoção **R2** trocou o `prov.loose_arrest_floor` de **dois** grupos por **um mesmo
> texto**, cuja justificativa (*"imita a desaceleração medida da cauda — dado leva **1643**
> ciclos de 0,25 a 0,10 e o modelo **16**"*) é da **`fig7d`**. Apliquei-a à `fig8a` **por
> analogia, nunca por medição**.
>
> **Medido agora** (ciclos do dado cru por nível):
>
> | curva | 0,40 | 0,25 | 0,15 | 0,10 | trecho final |
> |---|---:|---:|---:|---:|---:|
> | `fig7d` | 100 | 153 | **1626** | 1643 | **10,6×** — trava |
> | `fig8a` | 124 | 166 | 203 | 226 | 1,34 · 1,22 · **1,11** — não trava |
>
> ⇒ na `fig7d` a claim é **verdadeira** (com o piso o modelo **nunca** chega a 0,10; sem
> ele, em 130 ciclos). Na `fig8a` **não há desaceleração de cauda**: o modelo é ~12–25 %
> rápido em todo o percurso e o piso o atrasa **parelho**. Isso é trabalho legítimo para uma
> constante — só não é o que o rótulo diz.
>
> ⚠️ **A ironia é o ponto:** o R2 existiu para matar um rótulo que afirmava mais do que a
> medição sustentava, e eu **cometi o mesmo erro dentro do conserto**, reusando um texto
> justificado numa curva para outra que não o fora. **Rótulo compartilhado herda a
> justificativa da curva onde ela foi medida**, e o texto idêntico é o que torna isso
> invisível.
>
> ⚠️ **A guarda S1 não pega**, por construção: ela checa rótulos `lido-do-dado`, e este diz
> `fitado-this-rig`. É uma das "85 % infalsificáveis" que o item S mediu — e caiu por
> medição manual, como as duas do R2.
>
> | rota | ação | censo |
> |---|---|---|
> | **T1** (recomendada) | **separar os rótulos**: `fig7d` mantém (é verdadeiro lá); `fig8a` recebe texto próprio dizendo *erro de TAXA uniforme*, com os ciclos dela | **0** |
> | **T2** | generalizar o texto p/ cobrir os dois sem citar números | 0, mas **perde** procedência específica |
> | **T3** | não mexer | ⛔ deixa afirmação contradita pela medição |
>
> ⚠️ T1 **muda o fingerprint** e obriga re-carimbo dos 210 (o hash cobre a entry inteira,
> incl. `prov`) — não é edição cosmética.

> ✅ **ITEM S — rota S1 EXECUTADA em 2026-08-16 (20:0x), gates 6/6.** Assinatura às 19:27
> (*"confirme e assine tudo e prossiga"*); prereg `b3dc0b3`. Arquivo:
> `tests/test_piso_lido_do_dado_nao_excede_a_curva.py`. Suíte **988 → 993**.
>
> **A regra:** piso cujo rótulo afirma `lido-do-dado` não pode ficar **ACIMA** da leitura
> L24 do **CSV cru** da própria curva (tolerância 0,02). **A referência é a própria
> curva** — por isso é a única rota do item S executável sem âncora nova. **Unilateral:**
> piso *abaixo* é escolha conservadora e não dispara.
>
> **Baseline: 5 alegações, 0 violações** — o R2 já consertara as 2 que existiam. Guarda que
> nasce passando **tem** de ser validada por perturbação, e as 4 perturbações estão no
> arquivo.
>
> ⚠️ **A execução corrigiu dois números meus:** *"9 grupos alegam / 21 curvas / 7 abaixo,
> 2 acima"* estava **inflado** — eu casava o grupo por **prefixo da fonte** em vez de usar
> `runner._adopted_for`, o resolvedor canônico. São **5**. (Mesma classe do proxy "mediana
> da fonte" retratado de manhã.)
>
> ⛔ **S2 e S3 NÃO executadas, com motivo:** a **S2** exigiria bandas de literatura que eu
> teria de buscar ou **inventar** — e inventar banda é o oposto do que o S1 conserta; a
> **S3** (`C_creep` por par, 17 grupos) exige estrutura de par tribológico que o repo não
> tem. Ficam disponíveis.
>
> **Escopo honesto:** o S1 torna falsificável **1 das 29** constantes que o item S mediu
> como infalsificáveis. As outras 28 seguem sem guarda.

> ⚠️ **ITEM S (2026-08-16, 18:0x) — 85 % das afirmações de procedência são
> INFALSIFICÁVEIS.** Aguarda assinatura; **nada executado**.
> Detalhe: `New_Theory/procedencia_85pct_infalsificavel.md`.
>
> **Origem:** o item **R**, adotado 40 min antes. Ele provou que o `prov` de 2 grupos do
> `ECCLES` **afirmava** *"lido-do-dado (assíntota final crua)"* sobre valores que o dado não
> sustenta. Pergunta seguinte: quantas outras afirmações alguém consegue **sequer checar**?
>
> **Medido** (denominador limpo — só chave que é campo de `JointMaterial` **e** valor
> numérico; descartadas 71 chaves de texto livre e 12 string/flag):
>
> | | n |
> |---|---:|
> | pares (grupo, constante) afirmando dado/âncora/handbook | **115** |
> | que `check_input` consegue checar | **17 (15 %)** |
> | **infalsificáveis** | **98 (85 %)** |
> | constantes distintas sem checagem possível | **29** |
>
> ⚠️ **Caso-prova:** `loose_arrest_floor` **não é checável** e `check_input` devolve `None`
> — que o próprio docstring avisa ser **ambíguo** ("dentro da banda" OU "não sei checar").
> Ele afirma procedência de dado em **10 grupos**, e hoje se descobriu, **por medição
> manual**, que 2 eram falsas. A guarda **não poderia** tê-las pego.
>
> ⚠️ **O que NÃO se afirma:** que 98 valores estejam errados. `check_input` sinaliza, não
> julga, e fora-da-banda pode ser legítimo (`k_wear_spec=0` é idioma de *wear desligado*;
> tribologia por par sai de banda global por construção). Uma 1ª leitura minha —
> *"15 de 17 fora da banda"* — foi **retirada** ao ler a semântica da função.
>
> | rota | ação | custo |
> |---|---|---|
> | **S1** (recomendada) | guarda **auto-referente** p/ `loose_arrest_floor`: piso rotulado `lido-do-dado` **ACIMA** da leitura L24 do cru falha. **A referência é a própria curva** — não precisa de âncora nova | baixo (1 teste) |
> | **S2** | estender `checkable_inputs()` às constantes com âncora publicada (`emb_depth` tem VDI 2230; `fat_*` têm handbook) | médio |
> | **S3** | `C_creep` **por par tribológico** (17 grupos, o topo da lista) — exige estruturar a informação de par, que o repo não tem | alto |
>
> ⚠️ A regra do S1 é **unilateral**: piso **abaixo** da leitura é conservador e não deve
> alarmar. Medido: das 21 curvas com rótulo `lido-do-dado`, **7 ficam abaixo** (todas
> `SUN_2025`, legítimas) e só **2 acima** — as duas do item R.

> ✅ **ITEM R EXECUTADO em 2026-08-16 (17:2x), rota R2 — gates 6/6.** Assinatura às 16:37
> (*"assine tudo e continue"*); prereg `1f1a16d`. Detalhe: `eccles_rotulo_R2_resultado.md`.
>
> **Mudou só o rótulo**: `prov.loose_arrest_floor` dos grupos `ECCLES_2010_fig7d` e `_fig8a`
> passa de *"lido-do-dado (assintota final crua)"* para
> **`proxy-de-desaceleracao-de-cauda (fitado-this-rig…)`**. Os números (**0,137** e
> **0,059**) ficam **intocados**, e os outros 6 grupos do `ECCLES` mantêm o rótulo antigo —
> diff de **exatamente 2 linhas**.
>
> ⚠️ **A recomendação foi REVISTA de R1 para R2 pela medição do relógio**, não por
> preferência: o modelo bate o dado **a 1,01×** até ratio 0,40 e só dispara na cauda (0,08×
> em 0,10 — o dado leva **1643** ciclos de 0,25 a 0,10 e o modelo **16**). Não é erro de
> nível: o piso estava **imitando uma desaceleração** que o engine não tem, porque
> `loose_arrest_floor` é a única alavanca anti-runaway. ⇒ **o número faz trabalho físico
> real; o rótulo é que mentia.** R1 deixaria as 2 curvas piores **e sem alavanca**.
>
> **Gates 6/6** · **predições 4/4** (incl. a que valida a doutrina: o fingerprint mudou
> porque `prov` entra no hash — se não tivesse, o ramo era `INCONCLUSIVO` e o `CLAUDE.md`
> estaria errado). Censo **144/205 inalterado**, 0 de 210 curvas com métrica alterada,
> fingerprint **210 uniforme**. As 2 seguem **fora** do tripé: R2 **não compra censo**.
>
> ⚠️ **Fica como candidata de assinatura própria** a forma que a medição nomeou —
> **desaceleração de cauda no canal rotacional** —, com escopo **medido**: 5 curvas em 3
> fontes, e o `KARLSEN_2022` (7 curvas) como **controle negativo** que impede chamá-la de
> classe (`relogio_de_cauda_e_subpopulacao.md`).

> 🆕 **ITEM R (2026-08-16, 13:4x) — `ECCLES_2010`: dois pisos adotados que o dado NÃO
> sustenta, e um deles é PORTANTE.** Aguarda assinatura; **nada executado**.
> Detalhe: `New_Theory/eccles_piso_nao_sustentado_pelo_dado.md`.
>
> **Origem:** auditoria disparada pela **minha própria retratação** de 1 h antes
> (`13ed862` — li a janela da métrica e chamei de dado). Se eu li platô onde havia
> colapso, a pergunta é quem mais leu — e piso adotado entra na física do grupo inteiro.
> Varri os **33** `loose_arrest_floor` das configs adotadas.
>
> ✅ **A ferramenta está limpa:** `prefit.py` usa `load_full_curve` (CRU),
> `level_seven_probe` usa `ratio_cru`, e `arrest_floor_from_curve` **auto-guarda** com
> `plateau=False`. **6 dos 8 pisos do ECCLES batem com o cru AO DÍGITO** (0,194/0,194 ·
> 0,216/0,213 · 0,232/0,229 · 0,182/0,180 · 0,152/0,149 · 0,000/0,000).
>
> ⛔ **Sobram 2.** A `fig7d` tem cauda crua `0,213 · 0,207 · 0,187 · 0,120 · 0,033 ·
> 0,007 · **0,000 · 0,000**` ⇒ leitura L24 = **0,0000** com `plateau=True`. O piso
> adotado é **0,137**, que corresponde a `tail_frac ≈ 0,40` — **a faixa em que o próprio
> helper diz que NÃO há platô**. É média de rampa em queda. E o rótulo afirma
> *"assíntota final crua ≥0,03"*: a assíntota é 0,000 e o clamp daria 0,03. **O rótulo
> não descreve o número.** A `fig8a` é o mesmo sinal, menor (0,059 contra 0,0122 lidos).
>
> ⚠️ **O incômodo:** corrigir **PIORA as duas** — `fig7d` MAE 0,0665 → **0,1641** (2,5×),
> `fig8a` 0,0489 → 0,0945. O piso está **segurando o modelo de pé** ⇒ não é defeito de
> constante, é **defeito de forma mascarado por constante com rótulo generoso**.
>
> **Custo no censo: ZERO** — as duas já estão fora hoje (`fig7d` MAE 0,0665 > 0,05;
> `fig8a` res.máx 0,132 > 0,10). Corrigir não tira nada; só desanestesia.
>
> | rota | ação | censo | afirma |
> |---|---|---|---|
> | **R1** (recomendada) | pisos → leitura L24 do cru (0,0 e 0,0122) | **0** | a constante recupera a procedência que o rótulo declara |
> | **R2** | manter números, rótulo → `fitado-this-rig` | 0 | o número fica, mas para de se dizer lido do dado |
> | **R3** | não mexer | 0 | ⛔ mantém rótulo que a medição contradiz |
>
> ⚠️ **MEDIDO ÀS 14:5x — o piso era um PROXY DE DESACELERAÇÃO, e isso REORDENA as rotas.**
> A versão de 13:4x dizia *"o modelo colapsa mais rápido que o dado"* — **inferência** a
> partir de "tirar piora", não medição. Medido o **relógio** (dado CRU, não a janela):
>
> | nível | dado cru | modelo (piso 0) | razão |
> |---:|---:|---:|---:|
> | 0,60 | 64 | **65** | **1,01×** |
> | 0,40 | 100 | **96** | 0,96× |
> | 0,25 | 153 | 114 | 0,75× |
> | **0,10** | **1643** | **130** | **0,08×** |
>
> ⇒ **não é erro de NÍVEL** — o modelo bate o dado **a 1,01×** até 0,40. É erro de
> **TEMPO na CAUDA**: o dado leva **1643** ciclos de 0,25 a 0,10 e o modelo cobre isso em
> **16**. O dado desacelera brutalmente; o modelo não tem desaceleração nenhuma.
>
> ⇒ `loose_arrest_floor` é a **única alavanca** anti-runaway do engine, então quem adotou
> a usou para **imitar desaceleração** — e teve de inflar acima da assíntota para ela
> morder cedo o bastante. **O número e o rótulo estão errados; o INSTINTO estava certo.**
>
> ⚠️ **Isto reordena as rotas.** O R1 corrige a procedência mas deixa as 2 curvas piores
> **e sem alavanca** — honesto e sem rota. O **R2 fica mais defensável**: o número faz
> **trabalho físico real** (imita a desaceleração medida), só não é o que o rótulo diz.
> **Recomendação REVISTA: R2**, com rótulo *"proxy de desaceleração de cauda,
> fitado-this-rig"* — e a forma faltante registrada como candidata de assinatura.
>
> ⚠️ **FORMA NOMEADA que isto produz** (não executo — forma nova exige assinatura):
> **desaceleração de cauda no canal rotacional**. O engine hoje só sabe **travar** (piso)
> ou **correr** (runaway) — a bifurcação arrest/zero que o `CLAUDE.md` documenta em
> `self_locking_gate`, aqui medida **com relógio pela 1ª vez** (12,6× cedo em 0,10, com
> 1,01× em 0,60 ⇒ o defeito é **exclusivo da cauda**).
>
> ⚠️ **ERRATA da própria proposta (13:5x, medida depois de escrita):** a guarda que eu
> sugeri — *"piso `lido-do-dado` tem de ter `plateau=True`"* — **está errada**. Das **87**
> curvas com piso efetivo > 0, só **29 (33 %)** têm `plateau=True`: **`plateau=False` é a
> NORMA**. A regra marcaria dois terços de tudo.
>
> **O teste que discrimina é rótulo-contra-valor.** Das **21** curvas cujo grupo afirma
> `lido-do-dado`: **12 batem** com a leitura L24, **9 não**. E a **direção** separa:
> **7 (todas `SUN_2025`) ficam ABAIXO** da leitura (0,08 contra 0,26–0,98) = conservador,
> não infla nada; **2 ficam ACIMA** — `ECCLES` `fig7d` e `fig8a`, exatamente as deste item.
>
> ⇒ **o item R fica MAIS forte:** as duas são as **únicas 2 de 21** cujo desvio de
> procedência aponta na direção que **compra métrica**. Guarda certa: piso rotulado
> `lido-do-dado` que fique **ACIMA** da leitura L24 do cru (2 casos hoje, ambos aqui).

> ⛔ **RETRATADO ÀS 13:0x — o MARCO das "21 de 21" era meu e CAI. São 18 de 21.**
>
> Às 09:0x eu declarei que as 3 do `YANG_2023_IJPEM` tinham forma nomeada: *"o dado
> arresta em **0,165** e o modelo é binário porque `loose_arrest_floor` = 0 — ninguém leu
> o piso desta fonte"*. **A afirmação central é falsa.**
>
> ⚠️ **Li `metric_data`, que é o dado DEPOIS do `FLOOR_TRIM` = 0,10, e chamei o último
> valor dele de "piso de arresto do dado".** O dado **cru** não arresta: colapsa a
> **0,02–0,06** nas 6 curvas acima do limiar (0,06 · 0,05 · 0,05 · 0,02 · 0,05 · 0,03).
> ⇒ `loose_arrest_floor = 0` está **CERTO** para esta fonte, e a rota de procedência que
> eu propus (`floor_from_curve`) **não tem o que ler**. A proposta sai da mesa.
>
> ⚠️ **E o pior não é o erro — é o que ele atropelou.** Este MESMO arquivo já carregava,
> mais abaixo, o veredito **medido** que dizia o contrário: *"as 3 do `YANG_2023` ficam
> FORA por medição — três regimes (13 % · 68 % · 0 % de stick) e três **sinais** de
> resíduo distintos; não formam classe, e entrar seria rotular sem prova"*
> (`yang2023_e_a_lei_do_sinal`). Eu **sobrescrevi uma exclusão medida com uma afirmação
> não medida**, e a re-medição confirma a versão antiga: os vieses são MISTOS em sinal
> (+0,047 · −0,159 · −0,094 · **+0,239** · −0,119 · +0,018), `ρ(res,N)` de −0,90 a +0,70.
>
> ⚠️ **A lição de método é NOVA e não estava coberta.** O
> `test_meta_numeros_nao_envelhecem` guarda contra número **vencido**; nenhuma guarda
> pega uma afirmação nova que **contradiz um veredito já escrito no mesmo arquivo**. O
> §4.43 protege o eixo do TEMPO, não o da COERÊNCIA INTERNA. Antes de nomear forma numa
> fonte, **procure a fonte no documento** — o veredito pode já estar lá.
>
> **Fica de pé:** a coerência interna da fonte (`ρ(amp, retenção)` = −0,745 ⇒
> digitalização não embaralhada) e a recusa de remover a fonte (+3,6 pontos de graça).
> Retratação integral: `New_Theory/yang2023_piso_nunca_lido.md`.

> ⚠️ **§4.43 no cabeçalho de novo** (corrigido 2026-08-15 23:5x): esta linha dizia *"1
> aberto (Q)"*, mas o **Q foi FECHADO às 23:27** (`3eb67d1`) e o próprio arquivo já o
> registra — só a linha que CONTA ficou para trás. **Terceira vez hoje** que a contagem
> de itens envelhece: ela é prosa e não está sob guarda, e a mitigação continua sendo o
> passo 3 do cron (*ler* o cabeçalho, não supor).

| item | veredito |
|---|---|
| **D** | ⛔ recusado com número — 8 conjuntos `per_case` para perseguir 6 curvas **já resolvidas com prova em nível de lei**, a até σ 6,55× |
| **E-dado** (`YANG_2023`) | ⛔ remover recusado (**+3,6 pontos de graça**); substituir aguarda fonte candidata. E as 3 abertas **não são classe** (3 regimes, 3 sinais) |
| **E-forma** (`YANG_2021`) | ⛔ 3 rotas fechadas por 2 instrumentos; forma nomeada, entrou na 2ª linha |
| **N′** | ✅ executado (gates 7/7) — `YANG_2019` fora da `classe_parada` |
| **O** | ✅ executado (gates 8/8) — par de réplica declarado no `ECCLES` |
| **P** | ✅ fechado **sem código novo** — a guarda já existia |
| **Q** | ✅ fechado (23:27) — forma construída, adoção falsificada pelos gates |

⇒ **o que resta não é decisão, é trabalho**: as **21** curvas com forma nomeada na 2ª linha
da fila — e **ZERO** abertas ainda sem forma (marco de 2026-08-16). O `form_limited` segue **0** e o censo,
**143/205**.

> ✅ **A 2ª linha da fila foi de 5 para 8 em 2026-08-15 (23:0x)**, assinatura *"assine tudo"*.
> As **3 abertas do `YANG_2021`** entraram em `_FORMA_NOMEADA` — a forma foi nomeada pela
> sessão B (`yang2021_stick_sustentado_resultado.md`) e **conferida por mim contra a barra
> do ICMEZ**: regime (8/8 em STICK) · canais (embedding 54–83 % + creep 10–28 %) · forma
> (resíduo ~0 no início **crescendo até o fim**, +0,045 a +0,122) · dado limpo (σ_res 8–17×
> o ruído) · **rota já descartada** (`gth` adotado dá net zero; acima, colapso).
>
> ⚠️ **Não é falta de forma — a forma existe.** Falta-lhe a **dependência que separa estas
> curvas**, e isso é defeito **nomeado**. O censo segue **143/205**: a 2ª linha mede
> *trabalho visível*, não curva fechada.

> ✅ **D e E respondidos com NÚMERO em 2026-08-15 (22:2x)**, assinatura das 22:22 —
> `itens_D_e_E_respondidos_com_numero.md`. Os dois pediam decisão e nenhum tinha sido
> medido no que decide.
>
> ⛔ **D — recusado.** O `CHU_2026` é **3 de 9**, e as **6 fora são TODAS exceção
> assinada** com prova em nível de lei (§4.54a). Os 8 conjuntos `per_case` perseguiriam
> curvas **já contabilizadas**, a partir de erros de até **σ 6,55×** e **MAE 3,23×**. Ganho
> máximo +6 no censo; custo 8 conjuntos de constantes para 9 curvas — o oposto da manchete
> do método.
>
> ⛔ **E-dado (`YANG_2023`) — remover recusado.** É **0 de 10** nas duas fontes, com erros
> de 2× a **8,5×**, e a digitalização nunca foi conferida (paywall). ⚠️ **Mas remover subiria
> a taxa de 69,8 % para 73,3 % — +3,6 pontos SEM consertar nada**, e 6 das 10 já são
> `declarada`. A instrução permanente diz **substituir**; substituir exige fonte nova, que
> não existe ainda. **Remover sem repor seria inflação cosmética.**
>
> ⛔ **E-forma (`YANG_2021`) — ERRATA 22:5x: a forma NÃO é nova, JÁ ESTÁ ADOTADA** (`gth_k`=1,5e-07, verificado; e 8/8 curvas são 100 % stick). Mexer nela dá **net zero** (fecha 2, quebra 2). Somando às minhas medições: **3 rotas fechadas por 2 instrumentos** — forma (net zero) · constante (`C_creep` refutado pelo controle, `r2`/`r3` saem) · scatter (recusado: réplicas a σ 0,0129/0,0099 contra modelo 0,0268 = 2,1× fora). Não é item de assinatura de forma; é diagnóstico de que a **lei de stick vigente não tem a dependência que separa estas curvas**. E sem
> alvo medido: a única rota por constante (o `C_creep` que fecha a `r1`) foi **refutada pelo
> controle** hoje — as próprias réplicas `r2`/`r3` saem do tripé, pior ΔMAE +0,0283.

> ⚠️ **§4.43 no próprio cabeçalho, 20 min depois de escrito** (corrigido 2026-08-15 22:0x):
> esta linha dizia **5** com `N′` e `P` dentro, mas os dois saíram no commit `3b92999`.
> Eu atualizei os NÚMEROS das camadas e escrevi a nota do N′/P, e esqueci a linha que os
> CONTA — a mesma classe de defeito que a guarda das 5 camadas foi construída para pegar,
> num campo que ela não cobre (a contagem de itens da mesa não está ancorada).
>
> ⛔ **N′ EXECUTADO** (21:4x, prereg `52a1a87`, gates 7/7): `YANG_2019` fora da
> `classe_parada` por falso positivo inteiro. Censo **143/205 inalterado**; a curva migrou
> para `indecidivel_sem_piso`, não fechou.
>
> ✅ **P FECHADO SEM CÓDIGO NOVO**: a guarda proposta **já existia**
> (`test_classe_parada_nao_cresce_calada`), verificado por perturbação. Verificar bateu
> construir.
>
> ⚠️ **Q entrou em 2026-08-15 (noite)** pela sessão B (`b434c35`): as 5 abertas do
> `ICMEZ_2025` são **form-limited com forma nomeada**, não indecidíveis. Este
> cabeçalho dizia 4 porque foi escrito antes; a correção é de quem o venceu.

> ✅ **O item O saiu em 2026-08-15 (19:xx)** — opção (a) assinada pelo professor e
> executada sob prereg com gates congelados; **8/8**, censo **inalterado em 143/205**.
> Detalhe na linha do próprio item, abaixo.

> ⚠️ **O item N foi RE-MEDIDO em 2026-08-15 (tarde) e mudou de forma** — o enunciado antigo
> ("3 das 8 curvas da `classe_parada` sem a assinatura") está **vencido**: a **D-AD** fechou
> `amp0p25` e `amp0p3`, a camada foi a **6**, e a terceira curva saiu **por mérito**. Hoje são
> **2 de 6** — `liu2025_M16_amp0p8` (razão **0,53**) e `yang2019_M10_amp0p4_5Hz` (**0,70**),
> ambas com a assinatura **invertida** (o erro se forma *cedo*, oposto de "aceleração tardia").
> Ele se desdobra em duas propostas de naturezas diferentes, medidas em
> `classe_parada_reauditada_pos_DAD.md`:
>
> **N′ — remover `YANG_2019` de `_FONTES_CLASSE_PARADA`.** É **falso positivo inteiro**
> (1 membro, 0 com assinatura), formato **idêntico ao da P-7 assinada em 08-08**, que removeu
> `LU_2024` e `SUN_2025_CRIMP` pelo mesmo discriminante. Custo medido rodando o
> `regra_de_parada_triagem.main()` canônico com e sem a fonte: **tripé 143 → 143**,
> `classe_parada` 6 → 5, `indecidivel_sem_piso` 15 → 16, **fila form-limited 0 → 0**.
> ⚠️ **Não gera trabalho** — troca *"encerrada pela classe"* por *"não julgável, falta
> réplica"*. O que a sonda **não** decide: com MAE 1,93× e σ 3,04×, "indecidível" também é
> generoso.
>
> **P — a camada tem DUAS ENTRADAS INERTES, e isso é armadilha latente.** `CHU_2026` e
> `JCSR_2023` estão na lista com **zero membros**: todas as suas curvas fora do tripé são
> capturadas antes por `excecao_assinada`. A camada **declara** alcance de 5 fontes e **tem**
> alcance de 3. Hoje é inócuo; o risco é de amanhã — a campanha já **retratou 6 exceções** e o
> `CHU_2026` tem **6 assinadas**. Se uma cair, a curva **não vira trabalho visível**: escorrega
> em silêncio para `classe_parada` e passa a contar como *"fechada com procedência"* sem que
> ninguém tenha decidido. ⇒ **a retratação, que deveria ser custo, viraria troca de rótulo.**
> Conserto proposto (teste, não reclassificação): guarda que falhe quando uma fonte da lista
> tiver **0 membros na camada** *e* exceções assinadas.


| **O** 🆕 ⚠️ | **DUAS exceções assinadas repousam num piso que a campanha JÁ DECLAROU INVÁLIDO — 6ª ocorrência da mesma estrutura.** `eccles2010_fig8a` e `fig8c` citam `res.máx 0,257 · σ 0,083`; a **P-15 (assinada e executada em 08-08)** registra que esse 0,083 *"era dispersão entre cargas AXIAIS de 0 a 3,5 kN — **a variável varrida do paper**"* e **retratou a `fig7c`** por isso. As outras duas ficaram de pé sobre ele. Hoje `pisos['por_fonte']['ECCLES_2010']` é **`None`** — o denominador das provas **não é reproduzível** | retratar as duas, preservando a prova em `_EXCECOES_RETRATADAS_ECCLES_PISO_INVALIDO`, no idioma das 5 anteriores | ✅ **o piso VÁLIDO foi medido**: a fonte tem **4 curvas `no_axial`** (mesmo `F_amp` 6000 N, δ 0,65) ⇒ piso **0,1134/0,0443**, **3× menor** que o citado. As duas **falham as duas pernas** (0,1320 e 0,1463 contra barra FORTE 0,0802) e nem na barra PROVA (0,1134) passam. **Custo:** `declarado_total` 181→179, exceções 22→20, **censo 141 inalterado**. ⚠️ **Ganho junto:** com a família medida o ECCLES deixa de ter piso `None`, o que reabre prova F7 legítima que a P-15 dava por impossível. Prova: `eccles_2_excecoes_sobre_piso_ja_invalidado.md`. ⛔ **NÃO EXECUTAR — MEDIDO EM 2026-08-15 (19:xx) que o veredito depende de um pareamento NUNCA DECLARADO.** O bloqueio do ECCLES está **certo em espécie e largo demais em escopo**: as 10 curvas estão em `_SEM_FAMILIA_MECANICA` por *"carga axial ≠"*, mas as **4 `no_axial` têm axial ZERO** e não diferem na variável varrida. A rota do desenho é **declarar o par** (o docstring de `_pisos_medidos` diz que bloqueadas *"nunca entram em família automática — pares declarados continuam possíveis"*), não desbloquear. ⚠️ **E aí o item quebra:** medindo pelo helper os **6** pares possíveis da família, saem **3 vereditos** — 4 pares reprovam as duas, `fig7a`×`fig8a` dá PROVA/PROVA, e **`fig8a`×`fig8c` dá FORTE/PROVA**. O item cita piso 0,1134 / barra 0,0802, que bate com os pares **FRACOS**; o par que o **artigo declara** (`baseline1`×`baseline2`) dá piso **0,1866 / σ 0,0698** e o resultado **OPOSTO**. ⇒ é a **7ª** vez que a campanha enfrenta validade de piso e a **1ª em sentido DEFENSIVO** — impede retratar exceções que o piso **correto** sustenta. **Decisão de procedência, não medição:** (a) declarar `fig8a`×`fig8c` ⇒ ECCLES ganha piso, `limite_sres` 0,0250→**0,0698**, as 2 sobrevivem com denominador válido (⚠️ mexe no limite da fonte ⇒ **pode mover o censo**, exige prereg); (b) declarar outro par ou nenhum ⇒ retratar como escrito. Ressalva: a `fig8a` fica a **1,6·10⁻⁵** da barra FORTE — o GRAU da prova não é numericamente estável, o veredito PROVA é. Prova: `item_O_nao_executar_o_veredito_depende_do_par.md`. ✅ **RESOLVIDO em 2026-08-15 (19:xx) — opção (a) ASSINADA pelo professor (*"assine e continue"*, 19:14) e EXECUTADA** sob o prereg `2026-08-15-eccles-par-replica-declarado` (`b8af3ac`, gates congelados antes). O par `fig8a`×`fig8c` entrou em `_PARES_REPLICA_DECLARADOS` com a procedência do **rótulo do autor** (baseline1/baseline2, ambos axial=0); a fonte **não** foi desbloqueada — o bloqueio segue certo para os 6 pares que cruzam cargas axiais. **Efeito medido:** `piso_da_fonte(ECCLES_2010)` `None` → **(MAE 0,0541 · res.máx 0,1866 · σ 0,0698)**, `limite_sres` 0,0250 → **0,0698**. ⚠️ **Censo INALTERADO em 143/205** — nenhuma curva entrou nem saiu; a adoção valida o **denominador** das 2 exceções, não move curvas. Provas **reescritas** com o denominador válido e **rebaixadas de FORTE para PROVA**: a `fig8a` passa a barra FORTE por **4·10⁻⁶**, margem que não sobrevive a arredondamento (o veredito é estável, o grau não). Gates **8/8**. ⚠️ Extrapolação declarada: o piso novo vale para as **10** curvas da fonte, inclusive as 6 que cruzam cargas axiais, porque a regra **D1** é **por fonte**, não por família. |

⚠️ **Achado estrutural do mesmo ciclo:** **20 das 22** provas de exceção estão em prosa livre, sem o formato `valor/piso` — a camada com o **pior histórico de invalidação** (5 retratações, agora 6) é a **menos verificável por máquina**. Não é defeito de quem escreveu (prova de lei e de escopo não têm essa forma), mas significa que a campanha não consegue **perguntar à máquina** se as próprias exceções ainda valem.

| **N** 🆕 | **`classe_parada` atribui por FONTE e 3 das 8 curvas NÃO têm a assinatura da classe** (medido 2026-08-15 com o discriminante da própria campanha: `|ρ|≥0,7` ou razão terminal `>2`). ⚠️ **Duas a têm INVERTIDA**: `liu2025_M16_amp0p8` (razão **0,47**) e `yang2019_M10_amp0p4_5Hz` (**0,70**) têm o resíduo **menor no fim** — o erro se forma **cedo**, extremo oposto do que o nome da camada afirma. A 3ª é `liu2025_M16_amp0p3` (ρ −0,233, e **\|viés\|/MAE = 1,00** ⇒ nível puro, defeito para o qual há alavancas) | trocar atribuição **por fonte** por atribuição **por curva medida**: entra na camada quem exibir o discriminante | ⚠️ **custo: 3 curvas saem e a fila form-limited deixa de ser zero.** É o preço de classificação honesta, não retrocesso — hoje elas contam como "fechadas com procedência" sob rótulo que a medição não sustenta. Precedente: a `test5`, também rotulada por fonte, **fechou** — o único teste independente que a camada sofreu, ela reprovou. ✅ **MEDIDO em 2026-08-15 (rodada seguinte): 1 das 3 TEM ROTA E FECHA.** A `liu2025_M16_amp0p3` (**STICK**, `slip/δ`=0,0000) passa o tripé com `emb_depth` **×0,5** (0,0373/0,0563/0,0167) **ou** `C_creep` **×0,5** (0,0360/0,0511/0,0183) — o nominal já tinha σ em 0,0249 contra 0,0250 e reprovava pelo **MAE**, que é o que alavanca de nível corrige. ✅ E o `tr_loose_gain` deu **bit-idêntico** nas duas doses, como a classe STICK prevê. As outras 2 **não têm rota** (a `amp0p8` reprova só no σ e a melhor dose move 0,0027). ⇒ **saldo: fila 0 → 2, e censo 141 → 142** se a rota for adotada com procedência e gates próprios. Reclassificar **destrava uma curva**, não é só registro. Prova: `classe_parada_3_de_8_sem_assinatura.md` §6b. ⛔ **REFUTADO PELO CONTROLE em 2026-08-15** — a rota existe e a curva fecha, mas a **fonte paga**: `C_creep`=6,5e-12 aplicada ao `LIU_2025` fecha 2 (`amp0p25` de bônus) e **tira a `amp0p6`** (σ 0,0213→0,0447), explodindo a `amp0p8` (MAE 0,0381→**0,1225**, ×3,2) ⇒ **G2 reprova** (+0,0844 contra tolerância +0,01). Causa **nomeada e medida por 2 instrumentos independentes**: o viés do `LIU_2025` é **monótono em amplitude** — `ρ(amp, viés) = +1,000` **exato** nas 6, R² 0,978, de −0,0757 (0,25 mm) a +0,0278 (0,8 mm), cruzando zero em ≈0,66 mm; e a própria tabela de doses reproduz a inclinação (ganho decrescente que vira dano no mesmo ponto). ⇒ o que cada curva exibe como **nível** (`|viés|/MAE = 1,00`) é, na fonte, uma **inclinação** — nenhuma constante plana a fecha, porque a correção necessária vai de −49 % a +4 % da perda. Candidato legítimo: **`s1_amp_gate_*`**, já no engine e default-inerte (ressalva registrada: satura em 1, logo **não** pode fechar a `amp0p8`, que precisa de *mais* perda). Prova: `liu2025_inclinacao_amplitude_resultado.md` |

⚠️ Contagem re-conferida em 2026-08-14 (tarde): **A**, **C** e **F** fechados; **G** e
**H** executados em `2335090`; **I** nasceu e **morreu no mesmo dia** (classe inteira
falsificada pela Tabela 1); **J** entrou. O cabeçalho antigo dizia "5 itens" e a tabela
já listava nove linhas — a discrepância é o §4.43 dentro do próprio arquivo.

⚠️ **A `CHU_2026` está EXAURIDA de rotas de FORMA.** Item I fecha a última classe de lei
de amplitude. O que sobra é **input** (item **K** — o mais forte, com valor medido no
artigo), **dado** (item J), **procedência** (item B, com custo medido de −2 curvas) e uma
classe de forma — **regime de fretting com máximo na transição** — que **não é
proponível hoje**, porque o modelo classifica δ=0,4 a 1,0 no **mesmo** regime e o
discriminante teria de vir antes da forma.

> ### ⚠️ ERRATA (2026-08-14, noite IV) — **NÃO havia sessão paralela ativa**; eu li a data errada
>
> Nas rodadas de 19h e 20h eu afirmei que a sessão paralela estava trabalhando no `CHU_2026`
> (*"`sandbox_configs_CHU.json` é o arquivo mais recente do repo"*) e **excluí os itens B, D,
> J e K da minha mesa por duas rodadas** pela regra de um-escritor-por-recurso.
>
> **Era falso.** Os sandboxes são de **2026-07-15** — um mês atrás. Eu listei com
> `--time-style=+%H:%M`, um formato que mostra a hora e **omite a data**, e li "19:18" como
> recente porque o relógio marcava 18:40. Os commits que tocaram os scripts com `M` no status
> são de **07-07/07-08**. Não há evidência de sessão paralela ativa em nenhum momento do dia.
>
> ⚠️ **A lição não é "confira a data"** — é que escolhi um instrumento cuja saída **não
> continha o campo que decide**, e tratei a resposta dele como se contivesse. Mesma classe do
> `sres_para_censo` recebendo o tipo errado. E de novo **sem absurdo que denunciasse**: "19:18"
> é um horário perfeitamente plausível.
>
> **Custo real:** os itens **J** e **K** eram executáveis e ficaram parados duas rodadas.
> A afirmação também está no commit `c847bd1`; fica retratada aqui.
>
> ✅ **VIABILIDADE DO ITEM J, medida agora que o CHU voltou à mesa:** a Fig. 2 do Chu é
> **raster** (1938×705 px, **300 DPI**, JPEG) — os "367 desenhos vetoriais" da página são
> **mobília** (traços de 1 segmento: filetes e sublinhados), então a rota **vetorial** do D-R
> **não existe** aqui; é pixel calibrado, rota **D-W**. As curvas **separam-se por cor**:
> 4,01 % da área em pixels cromáticos, **9 matizes** distintas (roxo · azul · violeta · verde
> · petróleo · azul-médio · vermelho · oliva · âmbar) para 6 curvas + marcadores de legenda.
> Imagem extraída em `chu_fig2.jpg` no scratchpad. **Alvo de round-trip: 325 ciclos** (Tabela 1
> do artigo, conferida contra o PDF primário).

> ### 🔧 FERRAMENTA CONSERTADA (2026-08-14, noite III) — `censo_por_proposta.py` reportava **19 abertas** onde há **0**
>
> O script que o próprio cron manda rodar para decidir usava
> `tem = cid in rh._EXCECOES or cid in rh._DECLARADAS` — **duas** camadas de estatuto num
> sistema que hoje tem **cinco**. As curvas de `classe_parada` (8), `metric_limited` (1) e
> `indecidivel_sem_piso` (10 no recorte do mapa) caíam em **ABERTAS**, e quem lesse a saída
> concluiria que há **19 curvas acionáveis** onde a triagem canônica reporta **zero**.
>
> ⚠️ O cabeçalho do próprio arquivo documenta com precisão o §4.43 que ele foi feito para
> evitar — *"a PERTINÊNCIA de cada curva tem de ser RE-MEDIDA contra o store"* — e ele faz
> isso **certo**. Envelheceu num eixo que o autor não previu: não a **lista** de curvas, e
> sim o **vocabulário** de estatuto. **Guardar contra uma forma de envelhecimento não
> guarda contra as outras.**
>
> Conserto: chama `classificar()` da triagem — o classificador **canônico**, importado e
> não reimplementado. Saída passa a **0 abertas** e imprime a distribuição por camada.
>
> ✅ **Reconciliação fechada:** triagem **64** fora × mapa **58** ⇒ diferença **6**, e são
> exatamente as 5 `ICMEZ` do bloqueio G+H e a `lu2024_fig18_amp1p5` da retratação de
> protocolo — **todas posteriores ao congelamento do mapa**. Os dois instrumentos concordam.
>
> ⚠️ **E eu repeti o mesmo erro na sonda que fez essa conferência**: passei o dict cru do
> store a `rh.sres_para_censo`, que espera `CaseResult`, e ela devolveu "205 de 205 fora".
> O absurdo denunciou na hora — enquanto o erro do `censo_por_proposta` sobreviveu semanas
> porque **19 é um número plausível**. Erro que produz número plausível custa mais caro que
> erro que produz absurdo.

✅ **O PDF do artigo ESTÁ na biblioteca** (`E. Rodada 4/…Chu 2026 Tribol Int.pdf`) — os
itens J e K são executáveis, não bloqueados por acesso. A Tabela 1 foi **conferida contra
o primário** e bate ao dígito com a nota de aparato.

| # | item | o que decide | custo medido |
|---|---|---|---|
| ~~**A**~~ | ✅ **CONVERGIDO em 2026-08-14** — **12 fases: 238 → 206 (errata) → … → 13 (2026-08-14) → 3 de 467 (2026-08-28) → **0** de 458 (2026-09-04)**; cobertura **49 % → 97 % → 99 %** | nada a decidir: as **13** de 08-14 foram verificadas **por leitura** e **não tinham registro** — 3 são `ANCORA_INTERNA` (fora do projeto) | deriva **zero** provada nos 210 × 3 pernas nas **doze** fases; zero linha de física. ⚠️ **Recusei zerar o passivo** em 08-14: gravar *"fitado, origem não localizada"* contaria como documentado e tiraria a lacuna do radar. ✅ **2026-08-28, a pedido do professor (*"resolva todas"*): 13 → 3.** Os 10 não-âncora interna ganharam texto com **rastro**, não rótulo: KARLSEN run7p1/run2p2 `C_creep`/`c_D` = mesmo valor do grupo-pai KARLSEN_2022, cuja `prov` já declarava a classe (cisão per-run PR-12c `4ea4ad6` / D-Y); ZHANG_2006_fig16 `emb_um` 1,58 lido do fig16 (`zhang2006_fig3_estudo_do_caso.md`), `d_hole` ISO 273 e `d_washer` ISO 7089 como o irmão ZHANG_2006 (F1 `e519c25`); ZHANG_2019 `mu_thread` 0,241 = **input-de-paper** (Tabela 2 via nota de aparato `zhang.md` l.89, adotado na Opção A `6960a26`). Os **2 do YANG_2019** (`emb_um` 5,0 e `slip_onset_W` 40 kJ, no config desde o registro `385ed72` com verdict §4.21) declaram **no próprio texto** *"sem leitura L24 registrada ⇒ classe conservadora fitado-this-rig"* — a lacuna segue visível, agora dentro do documento. Os 3 que restavam eram das curvas de bancada, e o passivo foi a **0 em 2026-09-04 por REMOÇÃO, não por resolução**: aqueles casos saíram do projeto (dado sigiloso, decisão do professor) e levaram junto as 14 entradas do baseline de procedência (206 → 192) e 3 curvas do corpus (210 → 207). Registrar isso como dívida paga seria contar como trabalho o que foi supressão. Store re-carimbado `db7de97e682a` → `79af1f607cb7` → re-carimbado de novo em 2026-09-04 (a procedência mudou de texto, a física não) |
| ~~**B**~~ ✅ **EXECUTADO pela sessão B em `42580a4` (2026-08-14 22:xx)** — verificado hoje: `SOURCE_INPUTS[CHU_2026]` tem **`rz="Rz<4"`** e as 9 curvas rodam com **`emb_um = 3,5 µm`**; a `test9` (Ra 1,6) vem por `per_case` em **9,5 µm**. **Censo inalterado** — `test1`/`test5`/`test6` têm o `emb` **pinado nos próprios grupos**, então o `rz` não as alcança. ⚠️ **ERRATA DA MINHA CÉLULA DE CUSTO:** eu publiquei *"item B custa −2 curvas"* medindo uma variante que **sobrepunha os grupos pinados** (injetei `emb_depth`=1,6e-6 em tudo). A variante de fato executada **não os toca**, e por isso custou **zero**. Contrafactual errado, não medição errada. | (registro do enunciado original) | ⚠️ **as opções (a) e (b) foram MEDIDAS e são insuficientes EM PRINCÍPIO** (2026-08-14, tarde) — resta (c) dívida declarada, ou atacar a causa real (item **I**) | ✅ **RE-MEDIDO**: CHU está em **3/9** (`test1`·`test5`·`test6_repeat`). E o achado que decide: dentro da **MESMA classe Ra 0,4** o `emb_depth` exigido vai de **1,6 µm** (δ=0,3) a **≥25 µm** (δ=1,0) — **≥15×**. Nenhum valor por classe de acabamento serve, porque **a exigência não é governada pela rugosidade** nesta fonte, e sim pela **amplitude**. Corrigir o Ra move o número certo na direção certa e **não fecha nada**. Prova: `lei_relogio_implementada_e_nao_adotada.md` §4 |
| ~~**C**~~ | ✅ **FECHADO em 2026-08-13 — a premissa era FALSA.** O `prov` do `ROUSSEAU_HDPE` documenta o piso na chave composta `'c_bend/emb_depth/floor'` = *"PR-14 fitado-this-rig (rig + assentamento + **piso de arresto**)"*, desde 2026-07-12 | nada a decidir: a opção (a) **já estava executada** quando eu a propus | zero — nenhuma config muda; errata em 2 docs + pino de regressão |
| **D** ⚠️ **premissa VENCIDA, re-medida 2026-08-15** | **eram 8 de 9 em defaults; hoje são 4 de 9 COM override** (`test1` 15 campos · `test5`/`test6` o par `D1p0` · `test9` o `emb_um` da classe rugosa). O enunciado *"a única com config fitada é a única quase-perfeita"* deixou de valer. ⚠️ **E o contexto mudou mais que a contagem:** o item **I** fechou a classe de leis de amplitude e o item **K** fechou a rota do µ medido (inerte por lei, §4.54a) ⇒ calibrar `per_case` é **a única coisa que resta** no CHU — e é justamente o que este item chama de *oposto da parcimônia*. A decisão ficou mais nítida, não mais fácil | calibrar 8 `per_case` (8 conjuntos de constantes) | DOF vs ganho — o oposto da parcimónia |
| **E** | **`YANG_2021` / `YANG_2023`** — forma nova (perda sustentada sob stick) e **dado** (digitalização nunca conferida, PDF sob paywall) | assinar forma, ou substituir a fonte | `r1` a **7 %** do σ, 3 rotas medidas e fechadas |
| ~~**F**~~ | ✅ **EXECUTADO em 2026-08-14** (assinatura em bloco; prereg `2026-08-14-item-F-orfas-de-protocolo-prereg.md`): as 8 declaradas **órfãs de protocolo** | gates **9/9** — tripé **140 inalterado** · `declarado_total` 172 → **180** · `fora_aberta` 33 → **25** · **fila form-limited 8 → 0** | **4 instrumentos**: o paper separa §3.1.3 × §3.2; o dado mostra platô 27–56 × 1 ciclo (3/3); o modelo é 3–9× melhor num lado; e a rota de forma de onda foi **falsificada por medição** |
| **G** | **`ICMEZ_2025`: chave de família CEGA AO `grip_mm`** (13,8 × 19,8 mm) — as 4 famílias pareiam rigidezes diferentes, MAE de piso **0,105–0,209** | bloquear (idioma `_SEM_FAMILIA_MECANICA`, cirúrgico) ou declarar que 0,2 de MAE é repetibilidade | **censo 146 → 141**; 3 das 8 sobrevivem por mérito. Mesma assinatura de `SUN`/`KARLSEN`/`ROUSSEAU`, **já bloqueados** |
| **H** | **`CHU_2026`: a dívida de rugosidade CORROMPE O PISO** — a família δ=0,5 pareia `Ra1p6um_test9` com `test3` sem Ra, porque o config usa o default nas duas | ⇒ ~~resolve-se de graça pelo item B~~ ⚠️ **NÃO se resolve pelo B** (medido 08-14 tarde: o B é insuficiente em princípio); segue valendo bloquear a família | **censo −1** (`test5`, σ 0,0436, vem da família *boa* e passa por causa da *ruim*) — já executado em `2335090` |
| ~~**I**~~ | ⛔ **CLASSE INTEIRA FALSIFICADA no mesmo dia (2026-08-14, tarde).** Não é o expoente nem o canal: na Tabela 1 do artigo o **expoente exigido salta ~5 unidades dentro da fonte** — de **≈ −1,1** entre δ=0,4→0,7 (N *sobe*: 278 → 406) para **≈ +4,9** entre 0,7→1,0 (N despenca a **72**) | nada a decidir: **nenhuma lei de potência única em δ ordena esta fonte** — ancorada no trecho íngreme ela prevê `N(0,4) ≈ 6 300` contra **278** medidos, erro de **23×** | 3 candidatos falsificados um a um antes de eu ler a coluna que os condenava em bloco (relógio ∝1/δ · potência no alvo · severidade `k∝δ`). ⚠️ **Errata da 1ª redação:** eu apoiara isto na *não-monotonicidade*, mas a prosa do artigo afirma tendência monotônica e declara **~25 % de scatter** (par `test5`/`test6`: 72 vs 54) — a inversão 278→406 cabe nele. O que **não** cabe é o fator **5,6×** de 0,7→1,0. ⚠️ A classe compatível é **regime de fretting** (taxa com **máximo na transição**, Vingsbo–Söderberg) — mas o modelo põe δ=0,4..1,0 **todas em GROSS** (`slip/δ` 0,993–0,998), então o discriminante teria de vir antes da forma. Prova: `chu_nenhuma_lei_monotonica_serve.md` |
| ~~**M**~~ | ✅ **EXECUTADO em 2026-08-15 (madrugada), gates 9/9 — mas pela rota que o ARTIGO atribui, não pela que eu propus.** Ao ler o `prov` da config, os zeros de `K_archard`/`k_wear_spec` revelaram-se **leitura do paper** (*"SEM/EDX: desgaste no FLANCO da rosca, não no bearing; rollers isolam placa-placa"*), não artefato de fit ⇒ religar o bearing **contradiria o artigo**. Adotado o **canal de flanco** (`flank_wear_on`/`flank_transverse_on`/`k_wear_flank`=1,2e-15), **só no par zinco**, via `per_case` | conteúdo preditivo da varredura de amplitude **0 % → ~50 %** (espalhamento do modelo 0,0000 → **0,0777**; dado 0,1569); censo **141 inalterado**; DLC **bit-idênticas**; isolamento **perfeito** (7 mudaram, todas da fonte) | ⚠️ A `AF0,4mm` melhora forte **sem entrar**: `res.máx` 0,1339→**0,0766** e σ 0,0345→**0,0227** passam, só o MAE bloqueia por **0,0026**. ⚠️ **1ª config do canônico a ligar `flank_transverse_on`** — o ramo transversal do flanco nunca estivera ativo. Fingerprint → **`85e8104420b0`**. Prereg: `2026-08-14-liu2020-flanco-prereg.md` |
| ~~**M (registro)**~~ | **`LIU_2020_WEAR`: religar o desgaste devolve a resposta à amplitude — e as duas doses possíveis esbarram em coisas diferentes.** Verificado antes: modo **deslocamento** (wear não é inerte), `delta_mm` varia, as 4 são **GROSS** ⇒ o canal pode agir. Grupo **só zinco** (as 2 `fig15` são **DLC**, par tribológico distinto — regra §4.7); DLC ficam **bit-idênticas** | **(A)** `k_wear_spec`=**1,2e-15**: censo **+1** (fonte 8/9→**9/9**), preditivo 0 %→**51 %**, mas a `fig9_AF0,2` piora **+0,0125** = **25 % acima** do gate de +0,01 ⇒ exige **emenda de tolerância assinada** (precedente LU_2024 (b)/(b′), assinadas em sessão). **(B)** `k`=**8,0e-16**: passa **todos** os gates (pior +0,0082), censo **0**, preditivo 0 %→~35 % — mas piora 6 de 7 curvas para ganhar conteúdo que **nenhum gate mede**: seria a 1ª vez que a campanha troca métrica por conteúdo preditivo ⇒ **política, não sessão** | ⚠️ **A 1ª grade saturou na borda INFERIOR** e dizia "o wear é forte demais"; estendida (disciplina D-L) o veredito **inverteu**. ⚠️ **O fit original não errou** — zerar o wear **melhora** a métrica (8/9, MAE 0,005–0,019); o **alvo** é que estava incompleto, e é o item L com preço em número. Prova: `liu2020_wear_religado_proposta.md` |
| ~~**L**~~ | ✅ **EXECUTADO em 2026-08-15 (madrugada), gates 7/7** — a razão `d_mod/d_dado` **por fonte** entra no report mestre como painel **informacional** (mesmo estatuto da deriva β), sem mover censo. Mediana das medianas **0,846** em 21 fontes. ⚠️ O painel já registra o efeito da adoção da mesma noite: o `LIU_2020_WEAR`, o caso que motivou o item com cobertura **0 %**, aparece em **0,756**. ⚠️ **Regeneração do HTML NÃO entrou** (gate G7): move ~38 MB nos 203 reports versionados e isso é o item **D3**, decisão de política. Prereg: `2026-08-14-item-L-conteudo-preditivo-prereg.md` |
| ~~**L (registro)**~~ | **O censo conta CURVAS, não PREDIÇÕES** — medido: `LIU_2020_WEAR` varre a amplitude transversal **4×** (0,1→0,4 mm, perda do dado 0,012→0,169, **14×**, monotônica) e o modelo devolve **0,9650 nas quatro, ao dígito**. Sensibilidade: dado **0,523/mm**, modelo **0,000/mm** ⇒ **cobertura 0 %**. **3 dessas curvas estão no tripé**; a 4ª só reprova porque o efeito ultrapassou a tolerância | publicar a razão `d_mod/d_dado` por fonte no report mestre, **informacional** (como a deriva β), sem mover o censo | ✅ **manchete honesta é BOA: mediana 0,869** em 532 pares — o modelo tipicamente separa 87 % do que o dado separa; **64 pares (12 %)** abaixo de 0,20. ⚠️ Causa no `LIU_2020`: a config zera `K_archard`/`k_wear_spec`/`tr_loose_gain`/`C_creep` — **exatamente os canais por onde a amplitude age** ⇒ não-modelado por construção. ⚠️ **`CACCESE_2009` NÃO é cegueira**: o scatter réplica-réplica (0,0549) **excede** o efeito de geometria (0,0101–0,0449) — com o piso certo ele é dos **melhores** (1,043). ✅ **MEDIDO POR FONTE (o número que decide):** mediana das medianas **0,804** em 371 pares; **5 fontes com razão < 0,40 carregam 24 das 141 curvas do censo (17 %)** — `QIN_2024` **0,024** (3/3) · `LIU_2020_WEAR` **0,115** (8/9) · `LI_2022_TRIBOINT` 0,264 (4/4) · `LI_2022_MARSTRUC` 0,342 (6/6) · `LIU_2025` 0,378 (3/7). Prova: `censo_cegueira_a_condicao_varrida.md` §5b |
| ~~**K**~~ ⛔ **FECHADO 2026-08-15 — já estava falsificado com prova de LEI (§4.54a) e re-verificado hoje** | **A Fig. 5 foi digitalizada — e ela EXPLICA a Tabela 1.** µ medido por amplitude (F₀=49 kN, Ra 0,4): δ=0,3 → **0,078→0,135 (plano)** · δ=0,4 → **0,114→0,258** · δ=0,7 → **0,139→0,473**; δ=1,0 → **0,6** (p.7, fora da Fig. 5). ⚠️ **Errata da minha própria nota**: eu escrevera *"cresce até 0,6"* como valor geral — 0,6 é só de δ=1,0. **Atrito maior ⇒ afrouxamento mais lento**, e é por isso que N(0,9F₀) vale **406** a δ=0,7 contra **278** a δ=0,4: a não-monotonicidade que eu declarara sem mecanismo é a **competição atrito×slip**, medida | calibrar `c_D`+`k_dmg_mu` **por fonte** contra as 3 curvas de µ — alvo **medido**, 3 curvas para 2 números (sobredeterminado), e o veredito na pré-carga vira **predição** | ✅ o engine já tem a forma (`µ_eff = µ·(1−k_dmg_mu·D)` com `k_dmg_mu` **negativo** ⇒ µ sobe com o dano, que vem do slip) e a `test1` **já carrega −2,43** — aplicado a 1 curva, nunca confrontado com a Fig. 5. ⚠️ **Gate a congelar antes**: ajustado ao µ, **não** pode ser re-ajustado se a pré-carga não fechar. CSVs em `New_Theory/chu2026_mu_medido/`; prova: `chu_mu_medido_explica_a_tabela1.md` |
| ~~**K (registro)**~~ | **INPUT com procedência direta: o µ da interface é MEDIDO e CRESCE até 0,6; as 9 rodam com `mu = 0,15` constante.** Artigo p.7: *"the simulation used µ_plate = **0,6**, corresponding to the **final measured value in tests**"*; p.4 Eq. (1) computa µ ciclo a ciclo do dado (`µ = (R_max−R_min)/2F`) e a Fig. 5 traz a **evolução**, crescente por desgaste. ⚠️ A `test1` — a única que fecha quase perfeita — já tem `k_dmg_mu = **−2,43**` (negativo = µ **subindo**); as outras 8 não têm nada | calibrar `c_D`+`k_dmg_mu` **por fonte** contra a Fig. 5 (2 constantes, mecanismo **já existente**, alvo **medido**) — não é forma nova | ⚠️ **sonda de 2 pontos feita: µ constante em 0,6 PIORA as 4** (σ sobe em todas) ⇒ a pista é a **EVOLUÇÃO**, não o nível. Sinal parcial: a `test3` melhora MAE 0,1381→**0,0624** e res.máx 0,1741→**0,1150**, piorando só σ. Digitalizar a Fig. 5 é o pré-requisito |
| ~~**J**~~ | ⛔ **RETRATADO em 2026-08-14 (noite IV) — a `test3` está CERTA e o defeito era da minha medição.** Round-trip refeito sobre a **CSV crua**: **327** contra **325** impressos (**+1 %**), e a ordenação `test2` 272 < `test3` 327 **reproduz o artigo** (278 < 325). Verificação independente por **extração vetorial da figura** (pixel calibrado, ticks conferidos contra a moldura nos dois eixos): a curva da Fig. 2(a) e a nossa CSV concordam a **MAE 0,0034** — abaixo do piso de digitalização de 0,005 | nada a fazer: **não há defeito de dado no CHU**. Das 9, cinco batem a ±2 %; as três discrepantes (`test5` −33 %, `test9` +30 %, `test6` +22 %) são as mais **curtas e íngremes** (N de 54 a 233) ⇒ geometria, não digitalização | ⚠️ **Causa do alarme falso:** computei o round-trip sobre `metric_x`/`metric_data`, que são os vetores **ALINHADOS** da métrica; o `align` divide pelo 1º ponto (1,0259) e derruba tudo 2,6 %, levando o cruzamento de 0,90 a 253 em vez de 327. Comparei valor **impresso cru** contra vetor **alinhado** — o `CLAUDE.md` adverte exatamente isso, e eu apliquei a advertência ao modelo e esqueci dela do lado do dado |
| ~~**J (registro)**~~ | **DADO: a `test3` está 20 % adiantada e a ordenação está INVERTIDA** — round-trip contra a Tabela 1 dá 260 contra **325** impresso; no artigo a `test3` é 17 % **mais lenta** que a `test2`, no nosso CSV é 10 % **mais rápida** | re-digitalizar a Fig. 2a com alvo de round-trip 325 (precedente D-W/D-R: pixel/polilinha calibrada) | as outras 8 fecham em ±13 %. ⚠️ É a curva que a campanha vem perseguindo — pode estar sendo perseguida contra alvo errado. **Não altera o §1**: a não-monotonicidade sobrevive à correção |

### ✍️ ASSINATURA EM BLOCO — professor, 2026-08-13 19:00 (“assino tudo, continue o loop sem parar”)

Promulgação registrada pela sessão executora, opção por opção, pela regra da
própria campanha (physics-first + parcimônia + catraca de procedência):

- **A ASSINADO** — backfill de procedência autorizado, por CAMPO (começar
  pelos maiores: `c_bend` 16, `W_ref` 12, `loose_arrest_floor` 12); a catraca
  já impede crescimento do passivo. ⚠️ **Primeira ação executada em 08-13 foi
  MEDIR se o passivo era real, e ele estava inflado em 32** — ver a errata.
- **B ASSINADO na opção (b)** — corrigir a rugosidade do CHU_2026 para os
  Ra do artigo (0,4/1,6 µm) E calibrar — coerente com D.
- ~~**C ASSINADO na opção (a)**~~ ⛔ **A ASSINATURA FICOU SEM OBJETO.** Ao ir
  executá-la (08-13) descobri que a opção (a) **já estava executada desde
  2026-07-12**: o `prov` do `ROUSSEAU_HDPE` traz `'c_bend/emb_depth/floor'` =
  *"PR-14 fitado-this-rig (rig + assentamento + piso de arresto)"* — o rótulo
  pedido, com o piso **nomeado**. Eu havia lido `prov = None` porque a minha
  sonda fazia lookup **exato** e a campanha usa chave **composta**. Nenhuma
  config muda; a lacuna que resta é de **derivação** (por que 0,2 e não 0,0 no
  mesmo rig), que é dívida bem mais fraca e segue facultativa.
- **D ASSINADO com emenda de parcimônia** — calibrar o CHU_2026 em
  GRUPO/CONDIÇÃO (2 sub-grupos pelos Ra do artigo), NÃO 8 conjuntos
  per_case; per_case só para inputs de paper, como sempre.
- **E ASSINADO em princípio** — a forma “perda sustentada sob stick” e/ou a
  substituição do dado ficam autorizadas QUANDO houver discriminante ou dado
  novo; nada executável hoje (3 rotas medidas e fechadas).

### Rotas RECUSADAS com número (não re-propor)

* `gth_q = 7,0` — fechava a `amp1p0` com **custo zero** e quebra a lei do IJPEM. Recusada.
* **Re-ancorar as réplicas** do `YANG_2021` na janela comum — **no-op** para a `r1` e só
  afrouxa as duas que **já passam**.
* `tr_loose_gain` per-fonte — **nenhuma dose ganha** em 5 fontes testadas.
* `C_creep` per-fonte no `LIU_2025` — as curvas pedem **direções opostas** (×0,5 vs ×1,5),
  porque 2 são STICK (creep é 100 % da perda) e 2 são PARCIAL (1 de 4 canais).
* `k_wear_spec` per-fonte no `CHU_2026` — 6 doses, **todas** perdem curvas.

---


Store `061ce184eca5` · censo **144/205** · fora **61 = 33 com estatuto + 28 abertas** ·
**fila form-limited 2** (as duas `lu2024_M8_fig14_*_long`) · suíte **913/1** · leitura dupla:
estrita **144**, resolvida/declarada **177** (144 + 21 exceções + 12 declaradas).

**Cinco adoções em 24 h, censo 139 → 144**, todas com prereg de gates congelados antes:
D-Z e D-AA (JCSR, 1/5→4/5), D-AB (ECCLES `C_creep` per-par), D-AC (YANG_2019 `k_wear_spec`).

### ⚠️ O que mudou de MÉTODO — vale mais que as adoções

1. **Varredura MARGINAL declara ótimo CONDICIONAL** (D-Z/D-AA). Diagnóstico grátis:
   **|viés|/MAE → 1,00** = erro de nível puro; → 0 = forma.
2. **O `ataque_curva.py` estava CEGO** para metade das alavancas (2 de 7): lia a base dos
   *overrides*, então constante no default de `JointMaterial` era pulada **em silêncio**.
   Consertado (`0c4477a`) — e foi isso que revelou o candidato do D-AB.
3. **O CONTROLE DA FONTE decide, não a curva-alvo** (D-AB): a alavanca de melhor ajuste no
   alvo derrubava 2 irmãs. E quando duas empatam no controle, a **regra de escolha é
   declarada antes e vem do ARTIGO** (D-AC: o invariante impresso de frequência).
4. **Adotar constante criando GRUPO NOVO não é adotar constante** (D-AB): grupo nasce
   **mínimo**; por cópia importa tudo do molde (11 constantes de uma vez, E3 reprovou).
5. **LER A PROVA GRAVADA antes de agir** mudou o resultado **4 vezes em 2 dias**: retirou o
   candidato do CHU, levantou e resolveu a suspeita contra a P-9, e avisou do artefato de
   sensor no D-AC.
6. **Null só vale com prova de instrumento vivo** — 3 "idênticos ao dígito" foram
   instrumento morto no mesmo dia.

Store `e01d597c5037` · censo **142/205** · fora **63 = 33 com estatuto + 30
abertas** · **fila form-limited 2** (as duas `lu2024_M8_fig14_*_long`) · suíte
**913/1** · leitura dupla: estrita **142**, resolvida/declarada **175**
(142 + 21 exceções + 12 declaradas).

Dois passos novos no dia, ambos com prereg e gates congelados antes de medir:

| passo | o que | gates |
|---|---|---|
| **D-Z** | re-fit da FORMA do creep nas 2 curvas de água do mar do `JCSR_2023` | 5/5 |
| **D-AA** | varredura **CONJUNTA** forma×nível — fecha a `stainless`, melhora a `galv` | 6/6 |

`JCSR_2023` foi de **1/5 para 4/5** sem constante nova e sem forma nova.

### ⚠️ O que mudou de MÉTODO, e vale mais que os dois passos

1. **Varredura MARGINAL declara ótimo CONDICIONAL.** Nível e forma de um mesmo
   canal são acoplados por construção; varrer um com o outro errado responde a
   pergunta errada. Foi assim que escrevi *"`C_creep` no ótimo"* um dia antes de a
   conjunta fechar a curva. Diagnóstico grátis: **|viés|/MAE → 1,00** = resíduo de
   sinal único = erro de NÍVEL puro.
2. **O `ataque_curva.py` estava CEGO para metade das alavancas** (2 de 7 sondadas):
   lia a base dos *overrides*, então toda constante no default de `JointMaterial`
   (`N_emb`=50, `tr_loose_gain`=2,0) era pulada **em silêncio**. Consertado
   (`0c4477a`). **Todo veredito "candidata a FORMA" emitido antes disso é suspeito.**

### ✅ D-AB EXECUTADA (09-08 noite) — `C_creep` per-par no ECCLES, censo 142 → **143**

A `eccles2010_fig7c` saiu de *form-limited* (veredito meu, do shell **cego**) para o tripé.
O **controle da fonte inverteu a escolha**: `N_emb`=35 dava o melhor ajuste na curva-alvo e
derrubava **2 irmãs**; a adotada, `C_creep`=**2,8e-11**, foi a única com **zero** pioras
(ECCLES 3→**4**). Prereg `824cc1b`, gates 6/6, `eccles_c_creep_per_par_resultado.md`.
⚠️ **Regra nova:** adotar uma constante criando **grupo novo** não é adotar uma constante —
criei os 2 grupos faltantes por **cópia** e injetei **11 constantes**; o E3 reprovou e quem
denunciou foi a **checagem contra a predição escrita antes**. Grupo nasce **mínimo**.

### 2 candidatos NOVOS, medidos com controle de fonte — prontos para prereg

Varredura da receita D-AB nas **29 abertas** (`varredura_29_abertas_resultado.md`): 5 têm
alavanca livre que fecha; o **controle da fonte reprova 3 e aprova 2**.

| candidato | fonte | tripé | pioram | veredito |
|---|---|---|---|---|
| ~~`chu2026ti test9` · `N_emb`=100~~ | CHU_2026 (9) | ~~3 → 4~~ | ~~0~~ | ⛔ **RETIRADO 10-08** — ajuste empilhado sobre **input errado** (abaixo) |
| `yang2019_M10_amp0p6_10Hz` | YANG_2019 (5) | 0 → **1** | **0** | ✅ **duas** alavancas: `k_wear_spec`×3 ou `tr_loose_gain`×1,3 |

⚠️ No YANG_2019 a escolha entre as duas precisa de **regra declarada antes** (precedente
D-AA): a fonte tem **0 de 5** no tripé, então a constante escolhida passa a governar as
outras 4 — escolher pela curva que fecha repetiria o erro que o D-AB pegou.

⛔ **CHU_2026 — candidato RETIRADO por leitura da PROVA GRAVADA.** A nota de aparato diz
**Ra 0,4 µm (tests 1-8)** e **1,6 µm (test 9)**, e adverte por escrito para usar o mapeamento
VDI *"rather than fitting a new roughness tuner"*. As 9 curvas estão com o **`RZ_DEFAULT`
`Rz10-40`** — ninguém declarou a rugosidade da fonte —, o que deixa o `emb_depth` das 8 base
**3,1× alto**. ⚠️ **Corrigir o input PIORA a métrica**: tripé CHU **3 → 1** (as duas de
D=1,0 mm **saem**), enquanto a `test3` melhora **0,058**. **O modelo precisa hoje da rugosidade
errada para manter 2 curvas.** Decisão do professor (`chu_rugosidade_input_resultado.md`):
**(a)** corrigir e aceitar 143→141; **(b)** corrigir junto com a dependência de amplitude do
embedding — **forma nova, fora do mandato**; **(c)** registrar como dívida conhecida.

⛔ **LIU_2025 falsificado para `C_creep` per-fonte:** `amp0p25`/`amp0p3` pedem ×0,5 e a
`fig2_single` pede ×1,5 — **direções opostas**. ×0,5 tira a `amp0p6` do tripé e piora a
`amp0p8` em +0,0844; ×1,5 tira duas e piora cinco. Rota que sobra é `per_case`, que exige
argumento próprio.

**24 das 29** não têm nenhuma alavanca livre de dose única que feche, agora **com a lista do
que foi sondado** por trás do veredito (6 alavancas × 2–4 doses, base efetiva).

### 16 das 30 abertas têm |viés|/MAE ≥ 0,80 (12 delas exatamente 1,00)

Agrupam por fonte **e** mecanismo, com o mesmo sinal: `YANG_2021` ×3 (embedding,
+1,00), `ROUSSEAU` aço ×2 (rotacional, +1,00), `LU_2024` fig14 ×2 (rotacional,
−1,00), `LIU_2025` ×2 (fadiga, −1,00). Assinatura de erro de **nível por rig**.
Já medido: a conjunta nível×forma **não** fecha `lu2024 fig14` (0/25) nem
`rousseau steel` (0/25); na `yang2021` o canal dominante não responde a nenhuma
das suas duas constantes — veredito **não sei**, não "é forma".

---

## 📍 ESTADO EM 2026-08-07 (fim do dia) — o que está VIVO, em 12 linhas

Store `d9a680664797` · censo **140/205** · fora **65 = 34 com estatuto + 31
abertas** · **fila form-limited 0** · suíte **909/1** · as **cinco** camadas de
estatuto com auditoria registrada (F7 · F5 · declarações · `n<6` ·
**exclusão do denominador**, esta última auditada hoje).

| item | o que decide | abertas que cobre | custo medido |
|---|---|---:|---|
| ✅ **P-7** | ~~reclassificar `classe_parada`~~ **EXECUTADA 08-08** (opção mínima) | 12 → **10** | gates 4/4; fila form-limited 0 → **2**; "dado" 1 → 3 |
| ✅ **P-15** | ~~bloquear a família de piso do ECCLES~~ **EXECUTADA 08-08** | — | gates 6/6; censo **140 → 139**, como previsto |
| ✅ **P-8** (opção 2) | ~~corrigir as CSVs do LU~~ **EXECUTADA 09-08** — par de digitalização | 0 | gates 6/6; barra do LU **0,1030 → 0,1303**, declarado |
| ✅ **P-8** (opção 1) | ~~corrigir as 5 restantes + re-fit acoplado~~ **OBSOLETA 2026-08-16** | 0 | re-medida contra as CSVs de hoje: a família fig18 **já casa** a Tabela 8 (a `amp2p0` caiu de **+0,0792 → +0,0031**, fator 25; `amp1p0` +0,0439→+0,0036; `amp0p5` +0,0100→+0,0023). O trabalho foi feito pela **correção do pico espúrio**, não por ela. Resta só a `amp0p25` a −0,0125 (offset uniforme, abaixo da barra de um prereg). ⛔ E o script que a mediria (`lu2024_csv_vs_tabelas.py`) **pareava a fig14 contra a Tabela 8 da fig18** — o cruzamento de protocolos que a retratação de 2026-08-14 invalidou —, listando 3 curvas falsas como "piores". Guarda de figura instalada; o pior real é `fig20_T4Nm` 0,0557, **curva já declarada por escopo**. `lu2024_tab8_p8_obsoleta_e_o_script_pareava_errado.md` |
| ✅ **P-9** | ~~forma nova: frequência no `EmbeddingLoss`~~ **EXECUTADA 09-08** | 8 → **7** | gates 6/6; **zero números fitados**; viés da 10 Hz **−81 %**; censo **139** inalterado |
| **P-13** | forma nova: **platô não-nulo** do afrouxamento | **7** (6 viés+ · 1 viés−) | forma nova ⇒ fora do mandato autônomo |
| ⛔ **P-14** | ~~forma nova: microslip abaixo do onset~~ **PREMEDIDA 09-08 — não adotável** | 4 | saldo **0** em toda dose; troca réplica por réplica |
| ⛔ **P-13** | ~~platô não-nulo~~ **pista FALSIFICADA 09-08** | 7 | o acoplamento `F_amp∼F_0` faria reter MAIS, e 6 das 7 já retêm demais |

⚡ **P-7 e P-15 assinadas e executadas em 2026-08-08** (*"assine a P-7 e a P-15,
e execute"*; prereg `2026-08-08-p7-p15-execucao-prereg.md`; resultados em
`p7_execucao_resultado.md` e `p15_execucao_resultado.md`). Estado após as duas:
censo **139/205** · fora **66** = 34 com estatuto + 32 abertas · **fila
form-limited 2** · famílias divergentes que afrouxam limite: **0**.

⚠️ ~~**A P-8 ficou mais relevante:** as 2 curvas que a P-7 tornou visíveis na
fila são exatamente as que a P-8 corrigiria.~~ **ERRATA da mesma noite — é
falso.** A própria P-8 estabelece que *"a `fig14` está certa"* (RMS 0,005 contra
a figura); as 7 CSVs que desviam são `fig18`/`fig20`, e as 2 da fila são
**`fig14`**. A via indireta também não fecha: a P-8 afrouxa `limite_sres(LU)`
para 0,1361, mas isso só governa o **σ**, e as duas reprovam por **MAE (2,5× e
9,6×)** e **res.máx (3,9× e 8,6×)**. ⇒ **a P-8 não move nenhuma das duas.** O que
ela decide segue sendo **estar certo**, com censo **+0**.

**Três leituras que só apareceram em 2026-08-07 e mudam como decidir:**

1. **"curva fora" ≠ "ganho de censo"** — 34 das 65 já têm estatuto; consertá-las
   não move o placar. E dentro das abertas, o **sinal do viés** filtra de novo:
   forma que *adiciona* perda só serve a quem **retém demais**.
2. **P-9 e P-13 têm defeitos de sinal OPOSTO** (perde rápido demais × retém
   demais) ⇒ são propostas distintas, não duas descrições do mesmo problema.
3. **A P-14 não se justifica pelo placar** (−1) — só como **correção de
   física**. O argumento físico é forte e independente: um único `max(0, ·)` em
   `resolve_transverse_slip` desliga **três** canais de uma vez, nenhuma
   constante os religa (varredura de 3 ordens de grandeza), e a maquinaria de
   partial slip existente não pode agir porque roda **a jusante do zero**.

### ⚠️ Uma questão de ESCOPO que eu não resolvo sozinho

Sua autorização de 2026-08-07 17:41 (*"se tiver que assinar algo, assine
automaticamente, não quero intervir pelas próximas 24h"*) foi dada à sessão do
**pipeline de documentos**, que registrou e teve ratificado às 18:03 um escopo
onde **adoções, preregs e assinatura/retratação de exceções ficam de FORA** —
declarando-os *"recurso da outra sessão"* (esta).

**Aquela sessão declinou autoridade sobre este recurso; isso não a transfere
para cá.** Não li a mesma frase como mandato para mexer no canônico, porque
seria eu alargar uma delegação que a outra sessão estreitou, sem você presente —
e a instrução permanente desta sessão é explícita: *reclassificação de camada é
PROPOSTA, nunca edição sem assinatura*, e forma nova de engine está fora do
mandato autônomo.

⇒ ~~**P-7, P-9, P-13 e P-14 seguem aguardando.**~~ **RESOLVIDO em 2026-08-08:**
o professor assinou a **P-7** e a **P-15** de forma explícita (*"assine a P-7 e a
P-15, e execute"*), e as duas estão executadas com gates fechados. **P-8, P-9,
P-13 e P-14 seguem aguardando** — as três últimas são forma nova de engine.

> ## 🆕 P-10 · O critério de declaração por RESOLUÇÃO mede o passo do dado e nunca o erro do modelo — 3 declarações vivas sem premissa
>
> **2026-08-07 (madrugada)** · medido, **nada declarado nem retratado** ·
> `resolucao_criterio_lacuna_resultado.md` · `declaracoes_teste_premissa.py`.
>
> ### Como apareceu
>
> Apliquei o critério **assinado** de 2026-08-01 (mediana |Δ(F/F₀)| entre pontos
> consecutivos ≥ META_MAX), que é explicitamente **global**. A curva que
> qualifica é a **`karlsen2022_M30_HVtorqued_run14p2`** — a única sobrevivente da
> fila form-limited. Declará-la fecharia a fila em **zero**, que é a condição de
> parada do loop. Foi essa conveniência que me fez testar a premissa.
>
> ### O controle da própria fonte refuta
>
> O critério argumenta que *"o dado não restringe a curva a menos do que o
> passo"* — o que exige erro **da ordem** do passo:
>
> | curva (KARLSEN) | passo | res.máx | **mx/passo** | tripé |
> |---|---:|---:|---:|---|
> | `run7p1` | 0,1603 | 0,0916 | 0,57 | SIM |
> | `run6p2` | 0,1470 | 0,0489 | 0,33 | SIM |
> | `M42_run20p0` | 0,1515 | 0,0558 | 0,37 | SIM |
> | **`run14p2`** | 0,1216 | 0,2363 | **1,94** | não |
>
> Quatro curvas da **mesma fonte** com amostragem **mais grossa** passam, com
> erro em 0,33–0,57 do passo. E o **MAE** dela (1,80× o limite) não é inflado
> por passo grosso de jeito nenhum. **Não declarei.**
>
> ### A emenda proposta
>
> > data-limited por resolução exige mediana ≥ META_MAX **E**
> > `res.máx ≤ mediana` — sem a 2ª condição o critério afirma que o erro é
> > invisível quando ele é **maior** que a régua que o esconderia.
>
> **Custo medido:** `run14p2` **não** é declarada (fila fica em **1**, não 0) e
> **3 declarações do IJPEM** são retratadas (`0,30` mx/passo 1,22 · `0,35` 4,00 ·
> `0,50` falha nos dois critérios aplicáveis) ⇒ leitura
> *resolvido-ou-declarado* **176 → 173**. Censo estrito **inalterado em 139**.
>
> ### Os outros critérios estão SÃOS — auditei os três
>
> * **colapso** (`max|Δdado| > 0,25`): premissa se sustenta em **100 %** dos
>   casos onde se aplica (`0,45` · `0,55` · `yang2019_amp0p6_5Hz`, todos com
>   res.máx a **0–1 índice** do maior salto do dado);
> * **`n<6`**: as 3 declaradas sob ele (`0,15` · `0,18` · `zhang19_fig4`) têm
>   mae/mx passando com folga — exatamente como a assinatura registrou;
> * **escopo/procedência** (4 curvas): sem premissa numérica, nada a testar.
>
> ⚠️ **Errata minha na mesma madrugada:** publiquei **5** declarações sem
> premissa e são **3**. Eu testava cada uma contra o *primeiro* critério que
> casava; uma declaração está justificada se **qualquer** critério assinado se
> sustentar. A `0,45` e a `0,55` têm colapso válido, a `0,65` passa pela própria
> resolução.
>
> ### Por que não executo
>
> As declarações foram assinadas por você e o teste que as acusa é **novo** —
> não é medição que mudou, é critério que ganharia condição. O charter reserva
> emenda de camada à sua assinatura. E registro o viés: fui aplicar o critério
> **esperando** fechar a fila em zero.

> ## ⛔ P-12 RETIRADA em 2026-08-20 (19:5x) — a curva FECHOU POR MÉRITO, e a guarda do projeto PROÍBE declará-la
>
> **Não é decisão sua: a medição a encerrou.** Re-medido contra o store
> **`245dc93087d1`** (uniforme, 210) com o helper canônico `rh._tripe_ok`:
>
> | curva | MAE | res.máx | σ_res | limite σ | `_tripe_ok` |
> |---|---:|---:|---:|---:|:--:|
> | **`bauer2024_M12_fig8_test1`** | 0,0305 | **0,0719** | 0,0282 | 0,0900 (BAUER) | ✅ **True** |
> | `Yang2023 0,45` *(citada como declarada)* | 0,0102 | 0,0154 | 0,0115 | 0,0250 | ✅ True |
> | `yang2019_amp0p6_5Hz` *(citada como declarada)* | 0,0158 | 0,0394 | 0,0190 | 0,0250 | ✅ True |
>
> **Três coisas, cada uma suficiente por si:**
>
> 1. **O sujeito fecha por mérito.** O res.máx era **0,3965** em 08-07 e hoje é
>    **0,0719** — 5,5× melhor, por alguma das adoções desde então. Declará-la a
>    **tiraria** do censo estrito (tripé 166 → 165), inflando `declarado_total`
>    com uma curva que o modelo **acerta**. É o precedente K6 ao contrário.
> 2. **Os dois precedentes que a proposta invoca não existem mais.** Nenhum dos
>    dois está em `_DECLARADAS` hoje — **ambos fecharam por mérito** —, e é por isso
>    que a camada `metric_limited_colapso` mede **0**. O argumento *"satisfaz o
>    colapso exatamente como as duas já declaradas sob ele"* ficou **sem referente**.
> 3. **A guarda congelada a rejeita.** `test_medicoes_cruzadas.py::
>    test_excecao_assinada_esta_de_fato_fora_do_tripe` contém
>    `decl_dentro = [cid for cid in rh._DECLARADAS if _passa(cid)]`. **Verificado por
>    perturbação:** passa no baseline e, ao executar a P-12 em memória, falha com
>    *"curva DECLARADA que passa no tripé: ['bauer2024_M12_fig8_test1'] — declaração
>    é 'não dá para julgar', não perdão"*. Assinar exigiria quebrar um teste que
>    existe exatamente para impedir isto.
>
> ⚠️ **Os números de linha-de-fundo da proposta também estavam vencidos** —
> *"resolvido-ou-declarado 173 → 174, censo estrito inalterado em 140"*. Hoje são
> **200** e **166**. §4.43 dentro de um item da própria mesa, e é o segundo desta
> semana (o item V teve o mesmo).
>
> ✅ **O que SOBREVIVE e vale guardar:** o **teste de colapso discrimina** — a
> `Yang2023 0,50` falhava a premissa (distância 3, não 1). Isso continua verdadeiro
> e é reutilizável quando aparecer curva que **não** feche por mérito.
>
> ### (registro) O que a proposta dizia
>
> **2026-08-07** · uma linha de decisão · medido, **nada executado**.
>
> A P-11 retirou a exceção F5 dela (res.máx 0,3965 > desvio-à-mediana 0,349).
> Correto. Mas medindo o critério de **colapso**, cuja premissa é *"o res.máx
> cai na vizinhança do penhasco"*:
>
> | curva | salto | @índice | res.máx @índice | distância | |
> |---|---:|---:|---:|---:|---|
> | `bauer_M12_fig8_test1` | 0,264 | 23 | 24 | **1** | premissa **OK** |
> | `Yang2023 0,45` (declarada) | 0,260 | 3 | 4 | 1 | OK |
> | `yang2019_amp0p6_5Hz` (declarada) | 0,375 | 11 | 12 | 1 | OK |
> | `Yang2023 0,50` (retratada) | 0,250 | 0 | 3 | **3** | **falha** |
>
> Ela satisfaz o colapso **exatamente como as duas já declaradas sob ele**, e a
> `0_50` — que também caiu na retratação — **falha**, o que mostra que o teste
> discrimina.
>
> ⇒ deixá-la sem estatuto **sub-classifica**: existe critério assinado que a
> cobre. Mas isto é **mudança de classe** (exceção → declaração), não correção
> de motivo como nas `0_55`/`0_65`, e muda o número publicado.
>
> **Se declarada:** *resolvido-ou-declarado* **173 → 174**. Censo estrito
> **inalterado em 140**.
>
> Registro do que fiz sem esperar: instalei as guardas P-10/P-11 no
> `regra_de_parada_triagem.py`, que classificava só pelo dado e **oferecia de
> volta** a declaração `n<6` da `0_50` que a assinatura rejeitara. Isso é
> implementar a assinatura, não emendá-la — a linha "efeito das camadas" caiu de
> 164 para **163**.

> ## 🆕 P-15 · A chave que mede o PISO e' cega a carga axial — o ECCLES agrupa a variavel VARRIDA como se fosse replica
>
> **2026-08-07 (noite)** · medido, **nada alterado** ·
> `pares_piso_auditoria.md` · `pares_piso_{sonda,impacto}.py`.
>
> Premissa ADJACENTE as 5 camadas de estatuto, nunca varrida: **quais curvas o
> `_pisos_medidos` agrupa como replicas**. Pareamento errado INFLA o piso, piso
> inflado AFROUXA `limite_sres`, e limite afrouxado aprova curva que nao deveria.
> Ja custou **3 blocos de retratacao** (ROUSSEAU, CACCESE, SUN).
>
> A chave, lida no sitio: `(src, delta_mm, F_amp_N, mode)` — cega a espessura,
> material, frequencia, torque **e carga AXIAL**.
>
> **4 de 20 familias** tem membros com condicao divergente; **so' 1 tem efeito**:
>
> | fonte | n | difere | limite hoje | sem ela |
> |---|---:|---|---:|---:|
> | **`ECCLES_2010`** | **10** | `conform_driver`, `k_tr_mode`, μ | **0,0828** | **0,0250** |
> | `LIU_2022_RETIGHT` | 18 | μ 0,176 × 0,236 (oleo × seco) | 0,0250 | 0,0250 |
> | `SUN_2025_REASSY` | 5 | `emb_depth`, μ (n de remontagens) | 0,0250 | 0,0250 |
> | `LIU_2020_WEAR` | 3 | `mu_thread` | 0,0250 | 0,0250 |
>
> As 3 inocuas tem piso medido ABAIXO do global => `max(0,025; piso)` da 0,025 de
> qualquer modo. Erradas em conceito, inocuas em efeito.
>
> **O ECCLES junta 10 curvas de "sem axial" a 3,5 kN axial** — a variavel varrida
> do paper. Os σ vao de **0,0195 a 0,1887** (quase 10x) e sao **monotonicos com a
> carga axial**: nao e' dispersao de replica, e' o efeito que o paper media.
>
> ⚠️ **Inconsistencia interna:** as excecoes F5 assinadas do proprio ECCLES
> argumentam *"sobreposicao axial"* — a campanha trata a carga axial como
> DISTINTIVA ao provar excecao e como IRRELEVANTE ao medir piso.
>
> **Impacto medido, e ele e' CONTRA nos:** censo **140 → 139**. Exatamente uma
> curva passa so' por causa do piso inflado — `eccles2010_fig7c_axial_2p7kN`,
> σ **0,0258** contra limite 0,0828, ou seja **3 % acima** do limite global.
>
> **Proposta:** acrescentar as 10 curvas do `ECCLES_2010` δ=0,65/F=6000 a
> `_SEM_FAMILIA_MECANICA`, mesma maquinaria dos 3 bloqueios anteriores.
> Custo **−1 no censo**.
>
> ⚠️ **Nao executei** — bloquear familia muda `limite_sres`, logo muda o censo:
> e' estatuto, e a regra e' PROPOSTA, nunca edicao sem assinatura.
>
> ⚠️ **Nao medido:** que as 3 inocuas fiquem inocuas. Elas dependem de o piso
> seguir abaixo de 0,025; curva nova numa delas pode fazer o pareamento errado
> morder **sem aviso**. Um invariante que RECUSE familia com condicao divergente
> seria o conserto duravel — tambem proposta.

> ## 🆕 P-14 · O slip do engine e' BINARIO por construcao — microslip abaixo do onset
>
> **2026-08-07 (tarde)** · medido, **nada implementado** ·
> `subperda_stick_resultado.md` · `yang2021_stick_premeasure.py`.
>
> Ao consertar o buraco do classificador do mapa, **7 curvas** ganharam
> assinatura propria: *o modelo nunca alcanca o nivel que o dado alcanca*. O
> extremo perde **5 %** onde o dado perde **48 %**.
>
> **Mecanismo medido:** **6 das 7 tem slip exatamente `0,0000 um`** com
> `delta_amp` de **0,25 a 1,0 mm** => wear e rotacional em **0 %**, sobrando
> embedding e creep, que **saturam por construcao**. Modelo cujos unicos canais
> ativos saturam nao pode produzir perda sustentada.
>
> **A procedencia do `c_bend` registrava o sintoma sem reconhece-lo:** *"banda
> INSENSIVEL 0,02-0,15, valor no centro, nao identificado alem da banda"*. Em
> toda a banda a junta esta travada => nada muda => o parametro **parece**
> insensivel. E' a regra *"grade identica = INERCIA, nao robustez"* acontecendo
> dentro de uma adocao assinada.
>
> **Destravar NAO conserta** (varredura de 3 ordens de grandeza, 8 curvas):
>
> | `c_bend` | slip | soma MAE | tripe |
> |---:|---:|---:|---:|
> | **0,1** (vigente) | 0,00 um | **0,3328** | **3/8** |
> | **1,0** | **433 um** | **6,0281** | **0/8** |
> | 100,0 | 598 um | 6,1519 | 0/8 |
>
> O stick **nao e' bug — e' o que torna a fonte ajustavel**. Fora dele o modelo
> vai direto a gross slip e perde tudo (soma de MAE **18x** pior).
>
> ### Endereco exato do defeito
>
> ```python
> delta_slip_onset = mat.delta_free + F_slip / k_tr
> return max(0.0, delta_amp - delta_slip_onset)
> #   docstring: "Zero significa stick (SEM HYSTERESIS)"
> ```
>
> Limiar **duro**: abaixo do onset, dissipacao **nula**. Fisicamente falso — em
> partial slip (Cattaneo-Mindlin) a zona anular escorrega e dissipa **antes** do
> gross slip.
>
> ### ⚡ REFORCADA no mesmo dia: o limiar desliga **TRES** canais, nao dois
>
> `flanco_transversal_resultado.md`. Testei a hipotese de que o canal de FLANCO
> ofereceria rota que o stick nao bloqueia (ele e' dirigido por carga AXIAL).
> **Falsificada pelo codigo** — `ThreadFrettingLoss.rate()`, ramo transversal:
>
> ```python
> if (mat.flank_wear_on > 0 and mat.flank_transverse_on > 0
>         and delta_amp is not None and slip_amp_override is not None
>         and slip_amp_override > 1e-12 and F_clamp > 0):
> ```
>
> O ramo transversal e' gateado pelo **mesmo slip resolvido** que esta zerado; e
> o ramo axial exige `delta_amp is None` (modo forca), fechado em fonte
> disp-mode. Logo:
>
> | canal | como o zero o mata |
> |---|---|
> | `wear` | `slip_amp` e' o driver direto |
> | `rotational_loosening` | `loosening_slip_gate` recebe slip 0 |
> | **`thread_fretting`** (transversal) | **gate explicito `slip_amp_override > 1e-12`** |
>
> **Um unico limiar duro desliga a fisica dissipativa INTEIRA em disp-mode.**
>
> ⚠️ **Corolario verificado:** NENHUMA config adotada liga `flank_transverse_on`
> => o ramo transversal, construido em 2026-08-01, **nunca esteve ativo no store
> canonico**. As 2 fontes com o canal ligado (`LIU_2016`, `LI_2022_TRIBOINT`) sao
> **modo forca** (`delta_mm = 0,0`) e usam o ramo AXIAL — logo o "17/17 no tripe"
> do canal e' selecao + modo, **nao** evidencia de rota transferivel.
>
> ⚠️ **E o engine TEM a maquinaria, no lugar errado.** `partial_slip_gate` e
> `slip_regime_mode="cattaneo_mindlin"` agem **a jusante**, modulando a fracao
> de energia de uma amplitude **que ja e' zero**. **Isto explica a inercia
> medida do CM** (Δ = 0,0000 nos 6 canais, 2026-07-30): o modo nao e' inutil —
> ele opera sobre um numero que o resolvedor zerou antes.
>
> ### A proposta
>
> `resolve_transverse_slip` devolveria amplitude **efetiva** nao-nula abaixo do
> limiar (fracao da zona anular) em vez de `max(0, ·)`. Alcance: **6 curvas** em
> 2 fontes.
>
> ⚠️ **Nao medido** que a forma conserte as 6. Medido: o canal que carregaria a
> perda esta **desligado por limiar duro**, nenhuma constante o religa, e a
> maquinaria de partial slip **nao pode** agir porque roda a jusante do zero.
>
> ⚠️ **Risco declarado, e MEDIDO** (nao estimado):
>
> | populacao tocada | curvas |
> |---|---:|
> | stick REAL (slip max = 0 em todos os ciclos), **dentro do tripe** — risco | **6** |
> | stick REAL, **fora do tripe** — alvo da forma | **12** |
> | **total tocado** | **18** |
> | deslizam normalmente (a proposta **nao** as afeta) | 132 |
>
> Fontes: `YANG_2021` 8 (a fonte INTEIRA) · `YANG_2023_IJPEM` 3 · `LIU_2025` 2 ·
> `LU_2024` 2 · `ZHANG_2006` 2 · `ROUSSEAU_2025` 1. Curva que ja desliza esta no
> regime linear e nao e' afetada por mudanca ABAIXO do onset — por isso 18, nao
> 150. Exige gate de inercia (fracao -> 0 recupera o atual bit-a-bit).
>
> ### ⛔ BALANCO DE CENSO: **-1**. A P-14 NAO se justifica pelo placar
>
> Escrevi *"risco : ganho ~ 1 : 2, FAVORAVEL"* e **estava errado**, por duas
> razoes que faltavam:
>
> **(a) o SINAL do vies decide** — microslip ADICIONA perda, logo so' ajuda quem
> **retem demais**. Das 18 em stick: **10 positivas** (ajuda), **8 negativas**
> (piora).
> **(b) "curva fora" != "ganho de censo"** — 5 das que eu contava como alvo ja
> sao **declaradas ou excecao**. Entre elas a `zhang2006_fig3_illus`, que tem o
> MAIOR vies positivo (+0,2078) e e' declarada por procedencia.
>
> | efeito no censo | curvas |
> |---|---:|
> | **ganho possivel** (aberta + fora + vies **positivo**) | **4** |
> | **risco** (no tripe + vies **negativo**) | **5** |
> | ja tem estatuto (nao movem o placar) | 5 |
> | pioraria, mas ja esta fora | 3 |
> | **balanco liquido possivel** | **-1** |
>
> ⚠️ **Isto NAO derruba a P-14 — SEPARA duas afirmacoes que eu tinha misturado:**
> o **argumento de FISICA** segue integro (o `max(0,·)` desliga 3 canais, nenhuma
> constante os religa, a maquinaria de partial slip nao pode agir porque roda a
> jusante do zero); o **argumento de PLACAR** e' FALSO (renderia 4, arriscaria 5).
>
> ⇒ decidir a P-14 **como correcao de fisica**, com o custo provavel de censo
> (**-1**) na mesa. E as magnitudes sao ASSIMETRICAS — os ganhos precisam de
> +0,03 a +0,17 de perda extra e os riscos toleram bem menos —, o que significa
> que o MESMO parametro dificilmente serve aos dois lados.
>
> ⚠️ **Contei errado DUAS vezes antes disto (99 e 44), e o numero errado teria
> feito voce recusar uma proposta favoravel.** O erro e' o mesmo repetido:
> **inferir mecanismo de um zero sem conferir por que ele e' zero.** (a) omiti o
> canal `thread_fretting`; (b) contei curvas em modo forca; (c) confundi "canal
> zerado" com "junta travada" — o `LIU_2020_WEAR` e o `KARLSEN_2022` tem
> `K_archard=0`, `k_wear_spec=0` e `tr_loose_gain=0` NAS CONFIGS ADOTADAS, e
> deslizam (a `liu2020_fig9_AF0.4mm` resolve **399 um**). **Regra: um canal em
> zero tem 3 causas — driver zerado (stick), constante zerada (config), gate
> fechado (companheiro) — e so' a medicao DIRETA do driver as separa.**
>
> ### Relacao com a P-13 — mesma assinatura, eixos distintos
>
> | eixo | dois atratores | onde o dado vive |
> |---|---|---|
> | **arresto** (P-13) | piso `F_min` **ou** runaway a zero | plato nao-nulo |
> | **slip** (P-14) | stick total **ou** gross slip | perda graduada |
>
> Nao funde as propostas (mecanismos e consertos distintos), mas identifica uma
> **assinatura de projeto** recorrente: onde o engine usa `max(0, ·)` ou `if/else`
> de regime, ele bifurca; onde o dado e' continuo, falta a transicao suave.

> ## 🆕 P-13 · A SEGUNDA forma faltante, agora confirmada em **duas** fontes independentes
>
> **2026-08-07** · medido, **nada implementado** ·
> `rousseau_bifurcacao_resultado.md` · `sun_crimp_resultado.md`.
>
> ⚡ **AFIADA em 2026-08-07** (`graded_scrit_falsificado_resultado.md`): a lei
> que falta **não** é "taxa fracionária constante" — é **taxa que decai com a
> pré-carga restante**, de modo que o colapso PARE num nível não-nulo. Medido: o
> `graded_scrit`, já construído no engine, foi testado com `s_crit` abaixo do
> slip real e engatou (rotacional 92–98 %), mas o final é **0,0000 em todas as
> 16 células** — o dado quer **0,5200**. Ele satura a TAXA, não a PERDA.
>
> | lei | destino | quem a tem |
> |---|---|---|
> | torque (default) | zero, acelerando | engine |
> | `graded_scrit` | zero, linear | engine (inerte) |
> | **∝ pré-carga restante** | **platô não-nulo** | ~~**ninguém**~~ **o engine TEM** ⚠️ |
>
> O `loose_arrest_floor` é a versão CRUA disso — para o colapso com uma
> **constante** em vez de um mecanismo, e por isso suas pernas têm ótimos
> conflitantes no ROUSSEAU. ⇒ a P-13 **volta a ser forma NOVA**; ligar o
> `graded_scrit` não resolve.
>
> ### ⚠️ ERRATA de 2026-08-07 (mesma data): o "ninguém" da tabela era MEU ERRO
>
> `arrest_exp_resultado.md`. Antes de propor a forma nova eu li o
> `self_locking_gate`, e ele **já é** a lei da linha 3: `g = max(0, 1−F_min/F_0)`
> tem **ponto fixo estável em `F_min`** (= platô não-nulo), e
> `arrest_approach_exp` (prereg grupo A, 2026-07-27) é a forma da aproximação —
> *"exp > 1 faz a taxa morrer mais cedo perto do piso ⇒ **desaceleração ao
> platô**"*. Eu testara o **piso** (nível) nas três fontes; **nunca o expoente**
> (forma).
>
> **A errata NÃO derruba a P-13 — ela a AFIA, com duas eliminações medidas:**
>
> | população | piso | o expoente… |
> |---|---:|---|
> | IJPEM · ROUSSEAU aço · SUN · ECCLES | **0** | **inerte por construção** (o gate faz `return 1.0` antes de lê-lo) |
> | ROUSSEAU HDPE | 0,2 | **live, e PIORA** monotonicamente (0,0927 → 0,2638) |
> | BAUER fig6+fig8 | 0,05 / 0,08 | live, fecha **3** curvas — mas **abaixo do piso de réplica** |
>
> ⇒ **`arrest_approach_exp` não é a resposta da P-13.** Nas fontes dela ou não é
> lido, ou responde ao contrário.
>
> ### 🔒 Critério de admissibilidade que esta passada instala na P-13
>
> As 3 curvas do BAUER que "fecharam" com `exp = 2,0` estão **abaixo do piso de
> réplica da própria família**: `fig6` mede MAE mediano **0,1065** entre 15 pares
> de réplica (barra FORTE 0,0753) e `fig8` mede **0,0837** (FORTE 0,0592),
> contra erros de modelo de **0,024–0,078**. O modelo já concorda com cada
> réplica melhor do que as réplicas concordam entre si.
>
> ⇒ **todo candidato futuro à P-13 tem de ser medido CONTRA O PISO DE RÉPLICA da
> fonte**, não só contra o tripé. O BAUER mostrou que uma família inteira pode
> "fechar curvas" sem que nada tenha sido medido — e que é isso que faz *qualquer*
> constante compartilhada reprovar no G2 ali (pediu-se a ela que reproduzisse
> dispersão espécime-a-espécime, que não é função de input nenhum).
>
> O engine **não tem modo de afrouxamento de taxa fracionária constante** — só
> os dois atratores: arresto no `loose_arrest_floor` ou *runaway* a zero. Curvas
> que vivem **entre** eles não são alcançáveis por constante nenhuma.
>
> ### 🔎 PISTA de 2026-08-09 (a caminho da execução): a forma pode JÁ EXISTIR — outra vez
>
> Lendo `RotationalLooseningLoss.rate` para desenhar o prereg, a origem da
> bifurcação ficou explícita:
>
> ```python
> L_tr = Phi_tr_active * cos(beta) * F_tr    # F_tr e' EXTERNO (fixo pelo ensaio)
> T_resist = T_resistance(state, ...)         # ∝ F_0, decai
> if T_loose <= T_resist: return 0            # <- condicao de parada JA EXISTE
> ```
>
> **Já há condição de arresto física** — mas ela só é satisfeita com `F_0`
> **alto**, porque `T_loose` é fixo e `T_resist` cai. É *gatilho*, não *parada*.
> Daí o runaway.
>
> **Para haver platô, `F_tr` teria de cair com `F_0`** — e é exatamente o
> **item 4 do roadmap** (`CLAUDE.md`): *"F_amp ↔ delta_amp coupling em disp-mode:
> fisicamente F_amp ≤ µ·F_0 em full slip"*. A capacidade foi **construída** (L3 do
> branch `feature/l1-l7-gaps`, mergeada em `166a761`) e está **default-inerte**:
>
> | campo | default |
> |---|---|
> | `mu_eff_lo` | **0,0** |
> | `mu_eff_F0_ref` | **0,0** |
> | `gross_ceiling_decay` | **0,0** |
> | `couple_famp_slip` | **False** |
>
> ⇒ com `F_tr` caindo com `F_0`, o `T_loose` cai junto e `T_loose ≤ T_resist`
> vira **parada**, com o platô determinado pela **geometria e pelo atrito** — não
> por uma constante fitada. É precisamente o que a P-13 pede.
>
> ⚠️ **Não medido ainda** — o batch de re-carimbo da P-9 está ocupando a CPU.
> Mas é a 3ª vez na campanha que a resposta de uma "forma faltante" é uma forma
> **já construída e desligada** (as outras: `arrest_approach_exp` na própria
> P-13, `graded_scrit`). A regra que isso consolida: **antes de escrever prereg
> de forma nova, varra o engine por capacidade default-inerte.**

> ### ⚡ REFORÇADA em 2026-08-07: **três** fontes, e a nova traz o discriminante mais nítido
>
> `ijpem_bifurcacao_resultado.md`: no `YANG_2023_IJPEM`, mover `delta_free` de
> **0,170 para 0,160 mm** — um centésimo de milímetro — faz o canal rotacional
> saltar de **0,4 % para 93,0 %** e o final do modelo cair de **0,9448 para
> 0,0000 exato**. O dado termina em **0,5200**, quase exatamente no meio.
>
> ⇒ **o salto é DESCONTÍNUO**, não mal calibrado: dois valores adjacentes do
> mesmo parâmetro dão finais separados por 0,94. É a prova que as outras duas
> fontes não tinham.
>
> ### Confirmada em três fontes, por caminhos diferentes
>
> | fonte | evidência |
> |---|---|
> | `SUN_2025_CRIMP` | `ln(F/F₀)` vs N é **reta**: τ = 172,7 ciclos, **R² = 0,9961** em 37 pontos. Taxa fracionária **constante** medida. |
> | **`YANG_2023_IJPEM`** | **0,01 mm** de `delta_free` move o final de **0,94 → 0,00**, com o dado em **0,52** — salto descontínuo |
> | **`ROUSSEAU_2025` HDPE** | nenhum `loose_arrest_floor` em [0; 0,40] fecha, e **as pernas têm ótimos em valores diferentes** (MAE/mx querem 0,15, σ quer 0,25) — assinatura de forma, não de nível |
>
> Rigs diferentes, materiais de membro diferentes, escalas de amplitude
> diferentes. **Uma forma faltante confirmada em duas fontes é
> qualitativamente diferente de uma diagnosticada em uma.**
>
> ### O corolário desconfortável
>
> Tentei corrigir o HDPE por **procedência de aparato**: o grupo aço tem
> `loose_arrest_floor = 0,0` desde 2026-08-01 porque *"o rig apoia o membro móvel
> em roletes que removem o atrito parasita"* — **e é o mesmo rig**. O argumento é
> fisicamente correto e **piorou a métrica pela metade** (`hdpe_t10` res.máx
> 0,179 → **0,400**).
>
> ⇒ o `0,2` do HDPE **não modela o rig; compensa a forma que falta**. Remover a
> compensação expõe o buraco. Isso é o padrão "constante que cobre forma
> faltante", agora com número.
>
> ### Distinta da P-9
>
> | | defeito | canal |
> |---|---|---|
> | **P-9** | *quando* — relógio de Estágio I sem frequência | Embedding/Creep |
> | **P-13** | *como* — taxa fracionária constante | rotacional |
>
> As duas são de **forma**, nenhuma se resolve com constante, e as duas estão
> fora do mandato de execução autônoma.
>
> **Alcance medido da P-13:** 2 curvas do ROUSSEAU + as do SUN já diagnosticadas.
> As `steel_t10`/`steel_t10_amp0p2` têm a mesma assinatura de viés (+0,155 e
> +0,096, `|viés|/MAE` = 1,00) mas já rodam com floor 0 — precisam de medição
> própria.

> ## 🆕 P-9 · Falta uma forma no engine: **frequência nos relógios de Estágio I** — 6 curvas em 4 fontes, autoridade medida em 97–100 %
>
> **2026-08-07 (madrugada)** · medido, **nada implementado** ·
> `yang2019_s1gate_resultado.md` · `espelhado_classe_assinatura.py`.
>
> ### ⚡ AFIADA em 2026-08-07 (tarde): o alvo é **uma classe**, não "os relógios"
>
> `p9_embedding_resultado.md`. Perguntei ao engine antes de tratar como forma
> nova — mesma disciplina que hoje corrigiu a P-13 e o inventário. **Metade do
> Estágio I já tem o eixo:**
>
> | mecanismo | lê `freq`? | evidência |
> |---|---|---|
> | `CreepLoss` | **sim** | `t_cur = cycle_N/freq` — relógio **temporal** por construção |
> | `EmbeddingLoss` | **não** | `freq` só na assinatura do `rate()`, nunca no corpo |
>
> Isso podia ter derrubado a P-9, porque o critério que a definiu exigia
> *"≥ 80 % de **emb + creep**"* — a **soma**. Separei, e o resultado é
> **unânime: 12 de 12 dominadas por EMBEDDING**, de **64 % a 97 %**, em quatro
> fontes independentes (ECCLES · LIU_2025 · LU_2024 · YANG_2019). O creep, que
> tem o eixo, carrega **0,3–36 %** — pequeno demais para suprir.
>
> ⇒ o pedido deixa de ser *"falta frequência nos relógios de Estágio I"* e passa
> a ser **"falta frequência no `EmbeddingLoss`"** — uma classe, com o `CreepLoss`
> servindo de **molde** de como o engine expressa relógio temporal.
>
> ⚠️ **Não estabelecido:** que a lei seja `1/f`, nem que o embedding *deva* ser
> temporal (assentamento plástico é plausivelmente cíclico). O medido é que **o
> canal que carrega a perda não tem o eixo que o dado exige**. A lei é decisão
> sua e exige prereg.
>
> ### ⚡ REFORÇADA em 2026-08-08 (noite): a P-9 cobre **100 % da fila legítima**
>
> Depois da execução da P-7, a **fila form-limited** — que o charter chama de
> *"o único alvo legítimo"* — passou de 0 para **2**. As duas são **P-9**, com a
> assinatura completa e em magnitude extrema:
>
> | curva | viés | razão do relógio | embedding |
> |---|---:|---:|---:|
> | `lu2024_fig14_amp0p5_long` | **−0,1257** | **0,0137** | **97,3 %** |
> | `lu2024_fig14_amp1p0_long` | **−0,4802** | **0,0047** | **96,0 %** |
>
> Viés **negativo** (o modelo perde rápido demais) + razão **≪ 1** (cruza 90 % em
> **1,4 %** e **0,5 %** do ciclo do dado — relógio **70× a 210×** adiantado) +
> **embedding dominante**, que é exatamente o canal sem eixo de frequência.
>
> ⇒ a P-9 deixa de ser *"8 curvas abertas"* e passa a ser **a única decisão que
> toca a fila que a campanha declara legítima**. As duas não são alcançadas pela
> P-8 (errata registrada: a `fig14` está certa e a barra afrouxada só governa o
> σ, enquanto elas reprovam por MAE 2,5×/9,6× e res.máx 3,9×/8,6×).
>
> ### O que a falsificação do `s1_amp_gate` estabeleceu
>
> Testei o candidato existente no YANG_2019 sob a sua autorização (*"adote se os
> gates passarem"*). **Não passaram** — e a reprovação é informativa:
>
> | | |
> |---|---|
> | autoridade sobre o defeito | **100 %** (toda a perda até 90 % é Embedding+Creep) |
> | gates | **reprovam por trade-off estrutural**: forte ⇒ viola +0,010; fraca ⇒ inerte |
> | curvas que entram no tripé | **0** em 15 células |
>
> **O motivo é estrutural, não de calibração:** a `amp0p6_10Hz` melhora nas três
> pernas (−0,021/−0,029/−0,001) e a `amp0p6_5Hz` — **mesma amplitude, só outra
> frequência** — piora no res.máx (+0,042). O gate depende **só de amplitude**,
> então nenhuma célula serve às duas.
>
> ### A lacuna, com os dois mecanismos medidos
>
> | mecanismo | autoridade @90 % | depende de frequência? |
> |---|---|---|
> | `s1_amp_gate` (Embedding/Creep) | **100 %** | **não** |
> | `dmg_dwell_exp` (dano) | **teto** — razão 1,10 para expoente 0…8 | sim |
>
> ⇒ o candidato é **frequência (ou tempo) nos relógios de Estágio I** — a
> combinação que nenhum dos dois entrega.
>
> ### Quantas curvas isso alcança (o número que torna a decisão decidível)
>
> Assinatura: modelo cai a 90 % em **≤ metade** dos ciclos do dado **E** ≥ 80 %
> da perda nesse ponto vem de Embedding+Creep.
>
> | curva | razão de relógio | autoridade |
> |---|---:|---:|
> | `lu2024_M8_fig14_amp1p0_long` | **0,00** | 97 % |
> | `liu2025_M16_amp0p3` | **0,00** | 100 % |
> | `lu2024_M8_fig14_amp0p5_long` | 0,01 | 99 % |
> | `yang2019_M10_amp0p6_10Hz` | 0,04 | 100 % |
> | `yang2019_M10_varamp_small_to_large` | 0,07 | 100 % |
> | `yang2019_M10_amp0p4_5Hz` | 0,09 | 100 % |
>
> **6 curvas, 3 fontes** (LU_2024, LIU_2025, YANG_2019). O modelo cai a 90 %
> em **N=0** em duas delas.
>
> ⚠️ **Duas ressalvas medidas, ambas contra a minha própria hipótese:**
>
> 1. **A assinatura NÃO é exclusiva do grupo ESPELHADO.** Das 10 espelhadas, 5
>    a têm; mas **1 das 3 de controle (grupo "classe") também**. A
>    `varamp_small_to_large` tem viés terminal **+0,101** (retém demais no fim)
>    *e* cruza 90 % em N=175 contra 2374 — os **dois** defeitos. É a
>    "curvatura" que a decomposição de σ_res já identificara (63 % trocam de
>    sinal). ⇒ rótulo terminal e assinatura de relógio são **eixos
>    independentes**; não há "uma classe".
> 2. **3 das 10 espelhadas têm relógio OK** (razão 0,84 a 3,47) — o defeito
>    delas é outro, e a forma nova não as ajuda.
>
> ### O que se decide
>
> Implementar forma nova no engine (fora do mandato de execução autônoma) para
> alcançar **6 curvas em 3 fontes**, sabendo que: nenhuma delas entra no tripé
> hoje com o candidato existente, e 2 das 3 fontes estão em `classe_parada`
> (portanto fora da fila publicada — ver **P-7**).
>
> **O rig instrumentado para isso é o YANG_2019**, e isto é mérito medido:
> dado auditado contra a lei D-N impressa (1,05/0,90, sem erro de
> digitalização), âncora independente para o relógio (`d^m·N = C`, Tabela 5),
> par de frequência controlado (0,6 mm a 5 e 10 Hz) e **consistência interna** —
> exatamente o que travou este mesmo candidato no LIU_2025, onde a Fig. 4 e as
> curvas discordam em 3–5×.

> ## 🆕 P-8 · O LU_2024: as CSVs estão erradas, corrigi-las **piora o modelo** e **afrouxa a barra** — e não há como fazer as três coisas separadas
>
> **2026-08-07 (madrugada)** · tudo medido, **nada executado** ·
> `lu2024_{fig18_extracao,piso_viesado,redigit_premeasure}_resultado.md` ·
> sondas `lu2024_{fig18,fig20}_extrai.py`, `lu2024_csv_vs_tabelas.py`,
> `lu2024_fig14_confere.py`, `lu2024_redigit_premeasure.py` (só-leitura).
>
> ### O que está estabelecido
>
> 1. **As duas figuras do paper reproduzem as tabelas impressas** — Fig. 18a
>    contra a Tabela 8 a **±0,002**, Fig. 20a contra a Tabela 9 a **±0,007**,
>    cada uma com seu controle. Logo qualquer desvio de uma CSV é **da CSV**.
> 2. **Sete CSVs desviam**, pior no c10: `fig18_amp2p0` **+0,0792** ·
>    `fig20_T22Nm` **+0,0724** · `fig18_amp1p0` +0,0439 · `fig20_T28Nm` +0,0274
>    · `fig20_T16Nm` +0,0160 · `fig20_T10Nm` +0,0115 · `fig18_amp0p5` +0,0100.
> 3. **O "piso de digitalização" da fonte (0,0127) mede concordância, não
>    acurácia.** A `fig18_amp1p0` e a `fig20_T22Nm` são o **mesmo ensaio** em
>    duas figuras (Tabela 9@22 N·m ≡ Tabela 8@1,0 mm) e **erram juntas**. As
>    âncoras extraídas confirmam a identidade: 11 554 N × 11 610 N.
> 4. **A `fig14` está certa** — CSV contra figura dá RMS 0,005, razão 1,000
>    contra o F₀ do registry nas duas curvas verificáveis.
>
> ### As três consequências, medidas, que vêm **juntas**
>
> **(a) O modelo PIORA em 5 de 7.** `fig20_T10Nm` res.máx **0,331 → 0,802** ·
> `fig20_T16Nm` 0,254 → 0,442 · `fig18_amp1p0` 0,107 → 0,254. Só a `amp2p0`
> melhora forte (0,0463/0,0722/0,0226 → **0,0110/0,0299/0,0124**) — e ela é
> justamente a de maior erro de CSV. **Modelo pior com dado mais certo = a
> calibração absorveu o erro.** É o mesmo padrão do erro de *drive* de
> 2026-07-31, agora no eixo y ⇒ **a correção é inseparável de um re-fit**.
>
> **(b) A barra AFROUXA 32 %.** `limite_sres(LU)` **0,1030 → 0,1361**. Isto é
> **medição**, não artefato (errata registrada: eu havia dito o contrário e a
> verificação da `fig14` me desmentiu). O piso antigo media *`fig18` enviesada
> contra `fig14` correta* — próximo por acaso; com a `fig18` certa, a dispersão
> real entre réplicas independentes é σ 0,3044. **Isso afrouxa as 5 provas F7
> do LU**, e é o ponto que exige a sua assinatura: barra que afrouxa por
> consequência de correção é diferente de barra afrouxada por conveniência,
> mas o efeito publicado é o mesmo.
>
> **(c) O saldo no censo é +0.** Nenhuma curva entra, nenhuma sai.
>
> ### O que se decide
>
> Corrigir dado sabidamente errado, sabendo que: o modelo fica pior, a barra
> afrouxa 32 %, o censo não muda e o passo exige re-fit acoplado. A campanha
> tem precedente de aceitar perda por correção (D-R, D-U, retratação CACCESE),
> mas **nunca de afrouxar a barra como efeito colateral**.
>
> **Opções:**
> 1. **Executar completo** — corrigir as 7 + re-fit no mesmo passo, publicando
>    piso antes/depois. Mais honesto; custa a folga de 32 % nas provas F7.
> 2. **Corrigir só o par** (`fig18_amp1p0` + `fig20_T22Nm`) — tira o viés
>    compartilhado do piso de digitalização (0,0192 → **0,0070**, medido) sem
>    tocar nas 5 exceções. Ganho metodológico, custo baixo, escopo mínimo.
> 3. **Não corrigir** — registrar que 7 CSVs do LU têm erro medido de até
>    +0,079 e que o piso da fonte é enviesado. **Inaceitável em silêncio.**
>
> Recomendação: **(2) agora, (1) quando houver decisão sobre o re-fit.** A (2)
> é a única que melhora algo sem mexer em barra nem em estatuto.
>
> ### Ainda em aberto, declarado
>
> `fig18_amp0p25` e `fig20_T4Nm` são **pretas** e não foram lidas — preto é
> também moldura, traços de escala e legenda. Se a correção for executada, elas
> ficam como as duas únicas da família com dado antigo, e isso tem de estar
> escrito.

> ## 🆕 P-7 · A fila publicada lê "1", e o número está protegido por um marcador POR FONTE que 43 % do balde contradiz
>
> **2026-08-06 (noite)** · medição pronta, **nada executado** ·
> `classe_parada_discriminante_resultado.md` · sondas
> `classe_parada_{composicao,discriminante}.py` (só-leitura, segundos).
>
> A triagem publica **fila form-limited = 1**. Esse 1 existe porque **23 curvas
> fora do tripé estão estacionadas em `classe_parada`** — e o estatuto é
> atribuído **por FONTE**, não por curva: basta a fonte estar na lista para
> todas as curvas fora dela saírem da fila sem terem sido medidas.
>
> O critério que montou a lista é a **razão de inclinação terminal**, e o
> `sun_crimp_resultado.md` de hoje mostrou que ela é **cega ao sinal**: dá o
> mesmo número alto para *"o modelo nunca acelerou"* e para *"o modelo já
> desabou e está parado no piso"*. Adicionando o sinal do viés terminal
> (grátis — sai de `metric_pred`/`metric_data`):
>
> | fonte | classe | espelhado | veredicto |
> |---|---:|---:|---|
> | `YANG_2021` | 3 | 0 | coerente |
> | `JCSR_2023` | 2 | 0 | coerente |
> | `CHU_2026` | 5 | 1 | mista |
> | `YANG_2019` | 2 | 2 | mista |
> | `LIU_2025` | 1 | 3 | mista |
> | `LU_2024` | 0 | 2 | **falso positivo** |
> | `SUN_2025_CRIMP` | 0 | 2 | **falso positivo** |
>
> **10 das 23 têm o defeito OPOSTO** ao que a parada encerrou — o modelo desaba
> **cedo**, e "acelerar mais" piora. E **5 curvas paradas estão mais perto do
> tripé** que a única da fila oficial (pior perna 1,07×–1,29× contra 2,36×).
>
> **Três opções, com custo:**
> 1. **Mínima (recomendada)** — tirar `LU_2024` e `SUN_2025_CRIMP` da lista (as
>    duas puras espelhadas). Fila 1 → 5. Não força re-derivar a regra de parada.
> 2. **Por curva** — marcador por curva em vez de por fonte. Fila 1 → 11. Mais
>    honesto, e obriga a re-derivar o critério (c) da parada (a população muda).
> 3. **Nada** — manter, **desde que publicado**: a fila "1" passaria leitura
>    errada em silêncio.
>
> Evidência independente para a (1): `SUN` tem r = −0,74/−0,78 contra a forma do
> grupo A (`kernel_diagnostic_2026-07-27.md`) e o remédio da classe falsificado
> em 4 doses; `LU_2024` entrou **por decisão documentada como frouxa** — o
> comentário em `regra_de_parada_triagem.py:67` diz que ele foi *excluído do
> teste* por cauda de fratura e admitido só pela razão >2.
>
> ⚠️ **Limitação declarada:** viés e inclinação respondem a perguntas
> diferentes. O `chu…D0p7mm_test4` tem viés +0,032 (classe) e razão **0,03** —
> inclinação terminal ~30× a do dado; pelo critério original ele **nem entraria**
> na classe. O veredicto por curva é sobre **nível terminal**, bom para dizer
> *"o remédio da classe não se aplica"* e insuficiente para dizer o que se aplica.
>
> ### ✅ LIMITAÇÃO PREENCHIDA em 2026-08-07 (tarde) — e a P-7 fica **barata**
>
> `p7_orfas_resultado.md`. O que travava era o risco de trocar *"parada em
> classe errada"* por *"sem explicação nenhuma"*. **Medido, o risco quase não
> existe:**
>
> * das 10 espelhadas, **5 já têm defeito nomeado** (relógio E1 → P-9) — o
>   classificador do `mapa` testa relógio e bifurcação **antes** da
>   `classe_parada`. A opção mínima orfanaria **2**, não 10;
> * e **nenhuma das 5 restantes é órfã de verdade** — três erram o limiar por
>   **1,2 a 4 pontos percentuais**:
>
> | curva | medido | classe |
> |---|---|---|
> | `chu…test3` | relógio **0,220** ✅ · emb+creep **0,760** | quase-P-9 (falta 4 pp) |
> | `sun…crimp` | rotacional **66,5 %** · viés −0,008 | quase-P-13 (falta 3,5 pp) |
> | `sun…standard` | rotacional **68,8 %** + troca de sinal | quase-P-13 + curvatura |
> | `liu2025_amp0p8` | troca de sinal, 63 % entre terços | curvatura |
> | `liu2025_amp0p25` | emb+creep **1,000**, dado não cai a 90 % | Estágio I sobre-perde |
>
> **Custo por opção, agora com número:**
>
> | opção | fila | órfãs criadas |
> |---|---:|---:|
> | **1 · mínima** (tirar LU + SUN) | 1 → 5 | **2**, ambas quase-P-13 |
> | **2 · por curva** | 1 → 11 | **5**, todas com classe nomeada |
> | **3 · nada** | 1 | 0 — exige publicar que 43 % do balde contradiz o critério |
>
> ⚠️ **Dois achados de instrumento que valem além da P-7:** (a) **limiar rígido
> fabrica órfã** — o `classe_parada`, atribuído por FONTE, absorvia em silêncio
> os quase-acertos dos outros classificadores, logo o *"zero sem explicação"* do
> `mapa` era em parte artefato; (b) **o teste do relógio tem buraco** — quando o
> **dado** não cai a 90 %, a razão é `n/a` e a curva **não é testada** (ela não
> passa: o teste não roda). Mesma classe do ramo `INCONCLUSIVO` do charter, agora
> num classificador. Limiar adaptativo fecharia — é mudança de instrumento, não
> executada.
>
> **Destrava:** a leitura honesta da fila e, com ela, o alvo dos próximos loops.
>
> ### ⚡ ÚLTIMO CUSTO REMOVIDO em 2026-08-07 (noite)
>
> `limiar_rotacional_sonda.py`. O custo que sobrava na opção mínima eram **2
> órfãs** (as duas `SUN`). Medida a distribuição da fatia rotacional nas 65
> fora, o corte de **70 %** que as deixa de fora é **arbitrário**:
>
> | fatia | curva | veredito |
> |---:|---|---|
> | 0,715 | `rousseau_hdpe_t10` | **dentro (P-13)** |
> | 0,700 | `eccles2010_fig8a` | fora |
> | 0,688 | `sun…grease_standard` | fora |
> | 0,665 | `sun…grease_crimp` | fora |
>
> **1,5 ponto percentual** separa "P-13" de "órfã". Na faixa decisiva (0,55–0,85)
> há 13 curvas e a maior lacuna é **0,078** — distribuição contínua, sem degrau.
> ⇒ as 2 órfãs são **artefato do corte**, mecanicamente indistinguíveis das que
> estão dentro. **A opção 1 fica sem custo declarado.**
>
> ⚠️ A bimodalidade REAL deste eixo está em **~0,10** (32 das 65 têm o canal
> rotacional < 10 %, contra 33 ativo) — não em 0,70. Se algum limiar merece ser
> tratado como físico aqui, é esse, e não é o que o classificador usa.

> ## ⏳ ABERTAS em 2026-08-05 — as DUAS que a fila form-limited deixou
>
> A fila form-limited caiu de 3 para **1** hoje (adocão **D-Q** + correções de
> dado **D-S** e **D-R**; censo 134 → **138/205**). A curva que sobra é a
> `li2022ti_axialmin_10Hz`, e **as duas rotas dela precisam de você**. Nenhuma
> das duas é medição pendente — as medições estão feitas.
>
> **P-1 · ✅ DECIDIDA (professor, 2026-08-06 em sessão): ASSINADA com valor
> 1,0.** As três opções estavam na mesa (1,0 · 0,92 · manter na fila) com os
> custos: escolhido **1,0** pela âncora física dupla (fretting ∝ 1/f = desgaste
> por TEMPO; e `a` = 1,006 medido do dado), aceitando a margem de **0,4 %** na
> perna σ da `full`. A declaração que a assinatura carrega: constante
> **per-fonte SEM held-out** (o único outro grupo com canal de flanco é
> mono-frequência) — a regra de transferência foi conscientemente relaxada
> AQUI. Execução = decisão **D-V** (registro
> `2026-08-06-li2022-fret-freq-adocao.md`). Texto original abaixo, preservado:
>
> ~~**P-1 · Assinar `fret_freq_exp` como PER-FONTE e SEM held-out?**~~
> Janela medida **[0,85 · 1,02]**, e nela a fonte fecha **4/4**. O valor **1,0**
> tem âncora física dupla (taxa de fretting ∝ 1/f = desgaste por TEMPO, e é o
> mesmo expoente que o dado pede: `a` = 1,006 no par 10–20 Hz). **Mas:** (a) a
> melhor margem em toda a janela é **~1,7 %** — e no D-Q, no mesmo dia, recusei
> uma célula com **2,4 %**; (b) **não existe held-out** — o único outro grupo com
> canal de flanco (LIU_2016) é de **frequência única**, então a lei só é
> observável na própria fonte-alvo. Adotar seria **ajustar e testar na mesma
> curva**, contra a regra que o próprio prereg do D-Q aplicou contra si mesmo.
> **Não tomei por delegação porque RELAXA uma regra**, e o mandato proíbe isso.
> Detalhe: `New_Theory/li2022_fret_freq_exp_resultado.md`.
>
> **P-2 · Autorizar tocar o KERNEL DE CREEP?**
> É o último membro não testado da classe. Para entregar a razão de frequência
> que o dado pede (2,009) o kernel teria de ser ~linear em t em vez de `log`.
> **Raio de explosão:** o kernel serve CACCESE_2009 (**7/7** no tripé),
> JCSR_2023, QIN_2024, LI_2022_MARSTRUC e ZHANG_2018 (**9/9**) — dezenas de
> curvas — **por +1**. E o **D-H**, de ontem, adotou `creep_mode="saturating"` no
> CACCESE justamente porque lá a curvatura do log erra na direção **OPOSTA**.
>
> **P-3 · Emenda à regra de parada: estado `data-blocked` por membro.**
> O requisito (b) prevê **falsificado** ou **não testado**. Hoje apareceu um
> terceiro estado, em **duas** classes independentes: candidato cuja falsificação
> exige dado que a biblioteca **não tem**. Não é falsificação (a janela existe e
> fecha curvas) nem pendência de esforço meu (nenhum trabalho meu produz o
> held-out). Proposta: `data-blocked` **não** satisfaz (b) e **não** bloqueia a
> parada — suspende a classe até dado novo, e a reabertura automática já prevista
> cobre o caso.
>
> **P-4 · Que DADO a campanha precisa comprar/procurar** (consequência de P-3,
> medida hoje): a biblioteca tem **exatamente uma** fonte exercitando cada
> variável varrida que hoje falha — **frequência** (LI_2022, e o outro grupo com
> canal de flanco é mono-frequência) e **espessura** (`GA_member` está em **1 de
> 69** grupos). Uma segunda fonte de cada destrava as duas classes de uma vez.
> Detalhe: `New_Theory/subresposta_a_variavel_varrida.md`.
>
> **P-6 · LIU_2016: re-plots do MESMO ensaio — decisão de DENOMINADOR
> (2026-08-06).** Sonda de pixel da campanha FAXINA-E-ANATOMIA mediu que
> `fig13a_dry` é o MESMO teste físico que `fig7_run1` (mean|Δ| **0,21 pt** no
> impresso, onde o par de réplica VERDADEIRO run1↔run2 difere **1,78 pt** —
> 15× mais justo que a réplica irmã, por 4 décadas), e que `fig9a_m30nm` e
> `fig11a_af10kn` são o mesmo teste pela 3ª e 4ª vez (o paper re-usa a curva
> de referência M0=30/AF=10kN/seco em toda figura de varredura; excursões
> locais ~1 pt explicadas por OVERPRINT medido). ⚠️ A prova é METROLÓGICA —
> um degrau abaixo da barra documental do LU (lá, Tabela≡Tabela ao dígito;
> aqui há 1 hipótese no caminho, a correção ×2 da legenda da fig13, já
> adotada pela biblioteca). Por isso NÃO executei. Efeito se aceitar:
> comente só o par mais limpo (fig13a_dry → `_CID_NAO_COMPARAVEL`,
> vira piso de digitalização como o LU fez com a fig18_amp1p0):
> comparáveis 205→204, tripé 138→137. As irmãs fig9a_m30nm/fig11a_af10kn
> merecem prereg próprio antes de agir. Subproduto útil: 4 digitalizações
> do mesmo teste = medida direta do ruído de digitalização na métrica
> (MAE do modelo varia 0,027–0,043 entre elas, ±0,008).
> Diagnóstico completo: ledger da campanha, tick 3.
>
> **P-5 · Grade densa do ROUSSEAU (disponível, não tomada).** O D-R manteve a
> grade de abscissas antiga (8–14 pts) para que a **predição registrada
> permanecesse testável**; o paper publica **391–398**. Re-amostrar na densidade
> real muda quantos pontos a métrica pontua e portanto o próprio σ_res ⇒ prereg
> próprio.

> ## ✅ DECIDIDAS POR DELEGAÇÃO em 2026-08-02 ("faça as decisões por mim")
>
> Mandato 2026-07-30 + instrução explícita. Reversíveis e rastreáveis.
>
> **D-A · A classe parada NÃO vira "declarada".** A tentação era converter
> as 21 curvas da classe "aceleração tardia" em declaradas e publicar
> 191/205 em vez de 170/205. **Recusado**: `_DECLARADAS` significa *"a
> métrica ou o dado não decidem esta curva"*; form-limited significa *"o
> modelo está errado e nós sabemos"*. Misturar os dois inflaria o número
> resolvido com fracasso do modelo — exatamente o que a régua existe para
> impedir. As 21 continuam **fora**, e a parada é sobre **onde gastar
> esforço**, não sobre o placar. Marcador explícito na triagem
> (`classe_parada`) para o leitor ver que estão fechadas-aguardando-dado.
>
> **D-B · Leitura dupla continua obrigatória** (estrita + resolvida/
> declarada), sempre lado a lado. Nenhuma publicação só com o número
> maior.
>
> **D-C · Tabela 3 do YANG_2019 fica como âncora REGISTRADA e não gasta
> agora.** Ela dá N médio para 90/80/70 % por amplitude — bom para
> conferir cruzamentos, mas nenhuma decisão pendente depende disso e a
> classe que a usaria está parada. Reabre com a classe.
>
> **D-D · Re-fit do grupo HDPE do ROUSSEAU: AUTORIZADO** — a `t10` mudou
> de dado (re-digitalizada contra alvo do próprio paper), e o cfg atual
> foi ajustado contra a versão errada. Mesma justificativa que valeu para
> o aço após o erratum do drive: *quando o dado muda, o fit feito contra o
> dado velho perde procedência*.

> ## 🆕 FILA CONSOLIDADA DE 2026-08-01 (pós-plano; tudo executável já executado)
>
> Censo vivo: **tripé 136/203 · resolvida/declarada 177/203 · fila 26 =
> 21 form-limited + 5 indecidíveis** (triagem re-sincronizada, `d77d4cb`).
> O plano (`plano_tripe_restante.md`) foi executado até esgotar o que não
> depende de você. Itens novos:
>
> 1. ~~Pergunta aos autores do Liu 2025~~ ❌ **CANCELADA pelo professor em
>    2026-08-01** ("não quero carta a autores, substitua os artigos que
>    não tiver acesso") ⇒ rota nova: **caça de substituição** — papers OA
>    com curvas digitalizáveis cobrindo os papéis da fila (réplicas
>    M6–M8; M16 amplitude baixa; Ti/superliga tipo CHU). A fonte LIU_2025
>    fica form-limited com diagnóstico completo (inconsistência D-N⊥curvas
>    registrada no draft cancelado, como memória técnica).
> 0. 🛑 **PR-3 / classe "aceleração tardia" — PARADA POR CLASSE DISPARADA
>    em 2026-08-01** (2ª vez na campanha). Não é mais "autorize a forma":
>    **três** formas foram construídas e falsificadas com prereg no mesmo
>    dia, e as duas últimas ficaram no engine default-inertes e testadas.
>    Vereditos: gates Hill só atrasam (≤1, *por construção*) ·
>    amplificador por acumulador é gradual demais (+53/+119/+397 % de MAE)
>    · amplificador por interruptor não é per-rig (CHU: mesmo k, 5 melhoram
>    e 3 pioram). O 4º candidato da spec (relógio por curva) é
>    **DATA-BLOCKED**: exige vida publicada por curva e essas curvas
>    terminam por critério de protocolo, não por falha.
>    **O que fica na sua mesa não é autorizar código — é decidir uma
>    ROTA DE DADO**: (i) vida por curva (bancada ou pedido aos autores —
>    política que você já vetou) ou (ii) aceitar a classe como
>    form-limited declarada. Provas: `crash_trigger_classe_resultado.md`,
>    `damage_classe_resultado.md`,
>    `amplificador_interruptor_resultado.md`, `regra_de_parada_proposta.md`
>    §2ª parada.
> 2. **Bancada** (destrava até 11): Ra por espécime OU réplica D0.4/D0.5
>    no CHU (×6) · 3ª réplica do LU (×2). ~~nova rodada âncora interna~~ ❌ **âncora interna
>    SAIU DO PROJETO** (professor, 2026-08-01: *"a âncora interna não faz parte mais
>    desse projeto"*) — as 3 curvas ficam preservadas no store/repositório
>    e fora da meta em definitivo; **este item some da fila**.
> 3. **Tabela 3 do YANG_2019 como âncora de VIDA** (leitura de método):
>    médias de 3 espécimes para N a 90/80/70 % por amplitude — dado
>    independente não explorado (`yang2019_auditoria_replicas.md`); idem
>    as 18 vidas com réplica do companion do IJPEM (agora na biblioteca).
> 4. **n<6** (pendência antiga com número): 3 aprovadas com n<6 —
>    re-medir sob a régua por fonte antes de decidir.
> 5. **A curva mais próxima do censo**: `li2022ti_axialmin_10Hz` viola SÓ
>    o MAE por **5 %** (0,0526 vs 0,05) — qualquer melhora legítima de
>    nível na fonte fecha 1 curva; segue na fila honesta por falta de
>    alavanca com procedência.
> 6. **Os 5 indecidíveis nomeados** (falta réplica publicada; as duas
>    fontes já auditadas): `yang2019_M10_amp0p4_5Hz`, `amp0p6_10Hz`,
>    `varamp_small_to_large`, `varamp_large_to_small` (YANG_2019 publica
>    só médias — Tabela 3) e `IJPEM 0,25 mm` (sem réplica na fonte, PDF
>    inacessível). Destravam com dado de bancada em condição repetida.

> ## 🆕 ENTRADAS DE 2026-07-29 (tarde) — três decisões, todas com medição pronta
>
> ### ~~D1. Ligar a 3ª perna POR FONTE?~~ ✅ ADOTADO em 2026-07-30
>
> Decisão do professor em sessão ("faça tudo que temos que fazer", após duas
> exposições de que D1 era o único bloqueio da calibração). Flag
> `_SRES_POR_FONTE=True`; G5 cumprido no mesmo commit (docs re-sincronizados,
> reports regenerados, testes espelhando `limite_sres`). Re-medido na adoção:
> **104→124/202 · resolvidos 149/202 · manda σ_res 45 · MAE 14 · res.máx 19 ·
> 7 fontes 100%**. ~~Pendência: retirar as 19 assinaturas~~ ✅ **RETIRADAS em
> 2026-07-30** (assinado em sessão; 19 → `_EXCECOES_RETIRADAS_D1`, ativas = 25 =
> 16 F5 + 9 F7; guard nos dois sentidos em `test_medicoes_cruzadas`). Texto
> original do item abaixo, como registro:
>
> `σ_res ≤ max(0,025 ; piso_σ da fonte)`. Prereg
> `docs/superpowers/specs/2026-07-29-sigma-res-por-fonte-prereg.md`,
> **gates 5/5 medidos e passando**; flag `_SRES_POR_FONTE` em `report_html.py`
> (hoje `False`, e o report sai **bit-idêntico** — md5 conferido).
>
> | gate | resultado |
> |---|---|
> | G1 monotonia (bloqueante) | **0 curvas saem** do tripé — o `max` garante |
> | censo | 104/202 → **124/202** |
> | G2 mérito (bloqueante, declarado) | das 20 que entram, **19 já eram exceção assinada**; a única nova é `caccese2009_retighten_19p1mm_no_retighten` |
> | G3 cobertura (bloqueante) | **6 das 28** fontes sem piso medido (30 curvas) ficam no limite global: LU_2024, ANCORA_INTERNA, YANG_2019, YANG_2023_AME, YANG_2023_IJPEM, ZHANG_2006 |
> | G4 (info) | a regra cobre por **mérito 19 das 44** exceções assinadas |
>
> **O que destrava:** trocar 19 assinaturas por uma regra derivável. **O que
> custa:** o número-manchete vira 124/202 e a conta `104+44=148` muda (19
> assinaturas deixam de ser necessárias) ⇒ **todos os documentos vivos** têm de
> ser re-sincronizados no MESMO commit (o G5 e o
> `tests/test_meta_numeros_nao_envelhecem.py` obrigam).
> **Ressalva honesta:** o ganho numérico REAL é ~1 curva. Adote pelo método, não
> pelo número. E note que o LU_2024 — 10/10 fora, a pior fonte — **não tem piso
> medido**, logo a regra não a ajuda.
>
> ### D2. O σ_res é atingível com as formas atuais? (é a pergunta de fundo)
>
> Medido em `New_Theory/sigma_res_decomposicao_por_estagio.md`: nas 84 curvas em
> que o σ_res manda, **59,7 %** da variância do resíduo está ENTRE estágios (não
> dentro), e **63 % trocam de sinal** ao longo do ensaio. Isto é **curvatura
> errada**, não taxa errada — e explica por que as 18 alavancas falharam por
> **álgebra**: alavanca de escala move o resíduo em bloco, não move onde ele
> cruza zero. Só **11 das 84** são "taxa pura".
> **O que destrava:** parar de procurar a 19ª alavanca. A classe que moveria é
> *taxa dependente do estado acumulado* — limiar graduado (`graded_scrit`, já no
> engine default-inerte), kernel desacelerante, bifurcação de limiar.
>
> **2ª passada (mesmo dia) — e ela muda o escopo: são DUAS decisões de forma, não
> uma.** O `graded_scrit` modula **só o afrouxamento rotacional**, e alavanca de
> canal é inerte onde o canal carrega ~0 da perda. Medido nas 53 que trocam de
> sinal: a fração da perda nesse canal é **bimodal** (mediana 46,5 %, p25 1,6 %,
> p75 71,5 %) ⇒ **35 com o canal vivo** (>5 %) e **18 com ele morto** (≤5 %).
> Nas 18, quem carrega é **wear (8) · embedding (5) · creep (5)**, em grupos
> limpos por fonte: ZHANG_2018 embedding 100 % · CACCESE_2009 e JCSR_2023 creep
> 89–100 % · CHU_2026 wear 76–79 %.
> ⇒ atacar só o `graded_scrit` deixa **18 das 53 intocadas por construção**,
> qualquer que seja o parâmetro. A 2ª forma precisa agir em
> **embedding/creep/wear**.
> **Não testei nenhuma das duas**, de propósito: `s_crit_loose` é per-rig **com
> procedência** (Bauer 76–108 µm) e varrer o valor até o σ_res cair é **fitar**.
> Testar exige prereg com âncora para o limiar, por fonte.
> Nota que se cruza com D1: 3 das 18 são do `JCSR_2023`, a fonte de piso mais
> alto (0,2214 = 8,9× o limite global) — talvez a perna não devesse ser cobrada
> lá, e aí a forma nem é necessária para elas.
>
> ### D1b. As 23 near-miss (≤1,25× do pior limite) — DOIS becos sem saída medidos
>
> Ataque tentado em 2026-07-29 (noite) ao grupo com maior retorno aparente. **Nada
> adotado; nada mudou.** Registro aqui para ninguém repetir.
>
> **Beco 1 — a alavanca de procedência do embedding JÁ ESTÁ PUXADA.** 11 das 23
> são dominadas por embedding, e `calibration/provenance.py` declara a regra que
> parecia servir: *"quando o handbook e o data-implícito divergem, o
> data-implícito ganha … é procedência, não fit"* (precedente Li2022ti 3,5→1,6 µm,
> MAE 0,064→0,039). **Não se aplica:** o `LIU_2016` já usa
> `cfg.emb_um = {m30nm: 4,2 · m40nm: 2,75 · m45nm: 2,65 · run1: 4,05}`, isto é
> data-implícito POR CASO — a campanha fez isso antes. O que eu li como "handbook
> 11,0" era o `config_used.emb_um` reportando o **total derivado do VDI**, não o
> valor aplicado ⇒ **defeito de leitura do store, não oportunidade**.
> Testado em sandbox (`BAS_ADOPTED_CONFIGS`) com as minhas re-leituras
> (3,56/2,24/2,95/3,36): **9 de 12 métricas PIORAM**, 3 melhoram, 1 curva entra
> (`m45nm`, MAE 0,0504→0,0427 · σ 0,0175→0,0165). **Reprovado pelo gate de
> "nenhum caso pior".** Canônico intocado, sandbox apagado. As leituras da
> campanha são melhores que as minhas e não há por que sobrepô-las.
>
> **Beco 2 — a fração do canal NÃO decide inércia de lei de taxa (erro MEU,
> falsificado por medição).** Eu havia escrito que `graded_scrit` seria "inerte em
> 18 das 53, para qualquer valor". A sonda direta no engine (sessão paralela) mede
> o oposto no `CHU_2026 test8`: o canal rotacional vai de **0,0120 → 0,1619 kN**
> (2,3 % → 25 % da perda, **13×**), 88 % do movimento vindo do próprio canal, e as
> **três pernas melhoram** (σ 0,1924→0,1638 · res.máx 0,3456→0,2382).
> **A regra correta:** a fatia do canal limita alavanca que **multiplica** o canal
> (`loose_arrest_floor`, `eta_loose`), **não** alavanca que **substitui a lei de
> taxa** — mudar a lei é o que muda a fatia. Fração é atribuição *a posteriori* de
> uma parametrização, nunca cota do que outra pode fazer. Correção registrada em
> `sigma_res_decomposicao_por_estagio.md`.
>
> **O que sobra das 23, medido:** **D1 (piso por fonte) absorve 8** — KARLSEN_2022
> (piso 7,0× o limite), ECCLES_2010 (3,3×), SUN_2025_CRIMP (2,7×), CHU_2026
> (2,0×), CACCESE_2009 (1,1×) — nessas o near-miss **não é defeito do modelo**, é a
> régua pedindo mais do que o rig repete. **Restam 15**, concentradas em LIU_2016
> (4), LIU_2022_RETIGHT (3), ZHANG_2018 (3), e essas dependem de **forma**, não de
> input: σ_res entre 0,0175 e 0,0306 contra 0,025.
> ⇒ **não existe ganho barato nas near-miss.** A ordem racional passa a ser D1
> primeiro (absorve 8 sem tocar no modelo), e depois `graded_scrit` (que a medição
> do Beco 2 mostra ser mais amplo do que eu havia concluído).
>
> ### D2b. A otimização principal é calibrável em 5 fontes, não em 22
>
> Matriz de cobertura de âncoras: `New_Theory/anchor_coverage_matrix.md`
> (gerada por `build_anchor_coverage.py`, critérios declarados **antes** de medir).
> Pergunta que ela fecha: a forma precisa de um **limiar por rig**
> (`s_crit_loose`; `N_emb`/`C_creep`/energia de wear nos outros canais), e cada
> limiar precisa de âncora com procedência — senão calibrar é **fit**.
>
> **Das 22 fontes que precisam de forma nova, só 5 têm âncora sólida.**
> 9 são **NÃO ancoráveis** · 4 FRACO · 3 exigem **ensaio dedicado** (creep é por
> par, ICs disjuntos) · 1 já resolvida por **input de paper** (LIU_2025, rota E2).
>
> **Ordem que a matriz sugere** (âncora sólida × curvas fora):
>
> 1. **`YANG_2023_IJPEM`** — 7 fora, afrouxamento, **9 amplitudes distintas**
>    (a melhor varredura do acervo, e é uma das 3 piores fontes)
> 2. **`ROUSSEAU_2025`** — 5 fora, afrouxamento, 3 amplitudes
> 3. **`LIU_2016`** — 5 fora, embedding, `N_emb` + queda inicial resolvida 14/14
> 4. **`ZHANG_2018`** — 3 fora, embedding, resolvida 7/9
> 5. **`LIU_2020_WEAR`** — 1 fora, embedding, resolvida 9/9
>
> **O incômodo, e ele importa:** as **duas piores fontes não estão na lista**. O
> `LU_2024` (10/10 fora) é embedding-dominado e a queda inicial **não está
> resolvida em nenhuma** das 10 curvas; o `ECCLES_2010` (7 fora) tem **uma única
> amplitude** ⇒ limiar fitado. Nelas falta **dado**, não modelo — e nenhuma forma
> as fecha com procedência a partir do que a biblioteca tem hoje.
>
> **Consequência de método:** a otimização principal **não** é uma campanha sobre
> as 98 curvas fora. É uma campanha sobre as **5 com âncora**, com
> **transferência zero-refit** para as demais — que é o teste que distingue forma
> de ajuste. Onde a transferência falhar e não houver âncora, a saída honesta é
> exceção com prova ou **pedido de dado**, não calibração.
> Isso também dá o pedido de bancada concreto: uma **varredura de amplitude** no
> rig do LU_2024 (ou amostragem inicial fina) converteria a pior fonte de
> "não ancorável" em alvo.
>
> ### D2c. Pré-calibração executada (2026-07-30): verdades-de-engine + resolubilidade
>
> As duas preparações recomendadas antes da calibração, feitas:
>
> **1. `tests/test_engine_truth_levers.py`** — 5 verdades-de-engine das alavancas
> que a calibração vai tocar, cada uma prendendo o erro de classe que reprovou um
> prereg da sequência YANG (assumir a forma de uma quantidade sem ler a definição
> no engine): onset de slip **decai com F₀** (v1) · arresto é **por canal, não
> clamp** — com wear ativo o ratio *tem* de poder passar abaixo do piso (F4 do
> par) · gate de gross-slip é **0 exato em stick** · lei de taxa nova **muda a
> fração do canal** — fração a posteriori não é cota (Beco 2) · `W_slip_acc`
> **não é gateado** pela incubação (senão deadlock, e a leitura do joelho mudaria
> de significado em silêncio).
>
> **2. `New_Theory/feature_resolvability_matrix.md`** (gerada por
> `build_feature_resolvability.py`) — a sucessora da D2b: a D2b perguntou se a
> âncora *existe*; esta pergunta se a **amostragem resolve a feature** de que a
> âncora depende (queda inicial → `emb` · joelho → `slip_onset_W` · platô →
> `loose_arrest_floor`). Resultado nas 28 fontes:
> **CONSTRANGÍVEL 11 · PRECISA DE DADO 6 · fora do escopo 5 · n/a 6.**
> A verificação de convenção de eixo contra a D2b deu **zero divergências**.
>
> **O pedido de bancada, agora nominal:** as 6 PRECISA-DE-DADO são todas
> embedding-dominadas com a queda inicial não amostrada — `LU_2024` (0/10, a pior
> fonte do censo), `LIU_2022_RETIGHT` (0/21), `YANG_2019` (0/5), `YANG_2021`
> (1/6), `LI_2022_TRIBOINT` (0/4), `YANG_2023_AME` (0/1). O que destrava é
> **amostragem em N ≤ 1 % do ensaio**, não física nova.
>
> **Tensão declarada (não retunada):** o critério de platô marca as caudas do
> `YANG_2023_IJPEM` como não resolvidas (2/9), mas o G5 do par **mediu** o piso
> lido delas funcionando como lei (6 curvas, 1 constante). Em curva esparsa o
> critério é conservador ⇒ ele é *piso de confiança*, não veto; onde reprova, a
> leitura de platô exige o teste-de-lei antes de ser usada.
>
> ### ✅ Item (e) do handoff — conferência visual dos 2 primeiros pontos (2026-07-30)
>
> **`yang2021_amp0p7mm_ax11p2kN`:** o 1º ponto digitalizado (1,099, +16,5 % sobre
> o 2º, com "V" de queda-e-recuperação) **não existe na fig. 5(a)** — o settle
> real é ~5–8 % e monotônico ⇒ artefato de digitalização. **Custo hoje: ZERO** —
> a curva já passa no tripé (0,0173/0,0621/0,0221), então nenhuma correção de
> input se justifica; fica o registro para não re-descobrir.
> **`yang2019_M10_varamp_small_to_large`:** o overshoot inicial é **plausível e
> real** — a fig. 11 do irmão (large_to_small) mostra o pico inicial da banda
> (~29→26,5 kN). Sem correção. Item fechado sem tocar em dado.
>
> ### D3. Os 203 HTML gerados continuam versionados?
>
> Medido: **37,9 MB** de blob nos 203 reports do HEAD, contra `.git` de **254 MB**
> — e eles são **regerados a cada mudança** de código ou store, então cada
> geração escreve blobs novos para os 203. A causa do salto é a figura embutida
> (pedido de 2026-07-29): a página do `lu2024_M8_fig20_T10Nm` foi de 53,6 kB para
> **145 kB**, com a figura ocupando a maior parte.
> **Trade-off que não tem meio:** HTML autossuficiente (o que foi pedido, e que
> conserta o 404 da figura servida) **contra** repositório enxuto. Os dois não
> maximizam juntos.
> **Opções:** (a) manter como está; (b) `.gitignore` em
> `New_Theory/validation_html/reports/` — são **reproduzíveis por um comando**
> (`python -m bolt_analysis_studio.validation.report`) e o mestre continua
> versionado; (c) versionar só o mestre + um snapshot periódico.
> **NÃO executei nada aqui:** retirar 203 arquivos do índice é mudança de
> política de repositório, com efeito no histórico, e não é decisão de sessão.

> ## ✅ S4 ASSINADO (2026-07-28) — a execução mestre está DESTRAVADA
>
> As 8 decisões de `f5_excecoes_propostas.md` foram assinadas em sessão guiada
> (8/8 na recomendação): 15 trims ratificados · 16 exceções (§A ×7, §C ×5,
> §D ×4 violadoras) + `fig7d` junto com a família §D · 39 form-limited
> reconhecidos como fila. **Meta lida como 146/202 + 17 exceções + 39 fila =
> 163/202 (81 %).** O S6 (Manual) foi concluído pela sessão paralela ⇒ o fluxo
> mestre não tem mais passo bloqueado; próximo trabalho de campanha = varredura
> das 3 classes (L25) nos 39, que reclassifica a fila antes de gastar FAIL2.

## ~~DECISÃO (2026-07-28, noite): implementar a rampa~~ ✅ EXECUTADA — capacidade no engine, gates 6/6

*"execute o prereg da rampa"* → executado (§4.51; `New_Theory/ramp_capability_resultado.md`).
P0/P6 bit-idênticos nos 203 · P1 paridade **exata** com a sonda · P2 LI_2022_TRIBOINT
intocado · P3 conservação ok · P4 S-curve no Run. Default-inerte; fingerprint e meta
inalterados. **O que esta execução NÃO consumiu (decida quando quiser):**

1. ~~**Adoção per-rig do LIU_2025**~~ ✅ **PRÉ-REGISTRADA (`8ec2521`), EXECUTADA e
   REVERTIDA pelo gate cego A1** (§4.52; `New_Theory/liu2025_adocao_resultado.md`).
   `amp0p8` violou por +0,111 de MAE: relógio 27 % adiantado × trim no joelho ⇒ colapso
   inteiro dentro da janela. Rollback limpo; capacidade fica; fingerprint inalterado.
   **Confirmou o orçamento do premeasure:** relógio preditivo ±36 % contra ≤5 % exigido.
   **Rota restante, se quiser o estágio 3 no canônico:** `N_f` como input-de-paper POR
   CURVA (7 números; precedente = LI_2022_TRIBOINT com N_frat medido; claim vira
   "prevê a curva dada a vida" — e com relógio lido a rampa já provou 10/10).
   ✅ **ROTA E2 EXECUTADA E ADOTADA (2026-07-28, prereg `d721b14`, §4.53):** E1 cego
   7/7 (pior ΔMAE +0,0006), fingerprint novo `9ac44acd03de`, meta intacta. O estágio 3
   está no canônico por física, dada a vida. Nada pendente neste item.
2. ~~**`_CAP=100000` do Run**~~ ✅ **RESOLVIDO 2026-07-28 (delegado: "sua escolha")**:
   `_v2_cycle_cap()` — 400k SÓ quando o override pede fadiga+rampa, 100k nos
   demais (7 testes de regra) + poda da `ana.history` no loop do Run (memória
   O(1); o engine nunca lê a própria history — verificado; zero mudança
   numérica, 26 testes verdes). O log "V2 engine capped" já existia para o
   caso residual. As curvas de 250k/330k do Liu rodam inteiras na GUI.
3. **`fat_m1=2,7` do LI_2022_TRIBOINT**: procedência não rastreável ao artigo.
   ☐ corrigir rótulo ☐ re-ancorar (exige re-sim + gates daquela fonte)

## DECISÃO NOVA (2026-07-28): o prereg da rampa do Liu 2025 — assinar, emendar ou arquivar

**Medição pré-execução pronta:** `New_Theory/liu2025_ramp_premeasure.md`
(fingerprint `4f5bedfbace4`, **idêntico** ao do prereg ⇒ §4.43 satisfeita; engine
canônico **não** tocado — a forma entra por `loss_mechanisms=[...]`).

**O que ela achou, em 3 linhas:**
1. **A forma funciona e é discriminante.** No `fig2_single` **sem trim nenhum**:
   **0,039 / 0,062** (hoje, *cortando* 20 % da curva: 0,0389 / 0,0546). Sem o
   candidato, a mesma célula dá 0,093 / 0,481 e **nenhuma** das 7 passa o tripé —
   não morre calada como o `flank_s_crit`.
2. **Ela NÃO dispensa os 7 trims — custa 6 dos 7 passes** (7/7 → 1/7). E em
   **4 das 6** quedas o `res.máx` é *exatamente o último ponto do dado*: 0,330 é a
   **borda inferior do gráfico** do artigo, 0,683 é o **fim do digitalizador**.
   Não é erro de física — é o modelo indo a zero na fratura que o paper declara
   contra uma curva que **acaba antes**.
3. **O relógio está fechado pelo dado, não pelo modelo.** Para 75 % de
   sobreposição da janela de colapso é preciso `|ε|` ≤ **5 %** em N_f; o melhor
   publicado dá 17 % e o **scatter de espécime da própria fonte é 44 %**
   (`fig2` e `amp0p8`: mesma amplitude nominal, fratura em 10 k vs 14,4 k).

**Por que é decisão sua, e agora:** os gates **já foram medidos**, então assinar o
documento como está seria ceremonial — deixaria de ser pré-compromisso cego. E
duas cláusulas o tornam ambíguo: a de σ_res do **G1** dá **dois veredictos
opostos** conforme a leitura (literal ≤ 0,0389 passa; estrita ≤ 0,0224 falha por
0,006), e o §4.1 **não tem ramo** para o resultado real (G1 ✓, G5 ✓, G2 ✗).
Detalhe no banner do próprio prereg.

### ✅ AS TRÊS ROTAS FORAM EXECUTADAS (2026-07-28) — o que sobra é decisão, não medição

**(a) arquivar/registrar · (b) emendar e executar · (c) atacar o dado** — feitas.
Resultados: `New_Theory/liu2025_ramp_v2_results.md`; doc vivo §4.44 + §4.44a.

- **(a)** v1 **arquivado sem assinar**; §4.44 registra a classe nova; §B do
  `f5_excecoes_propostas.md` corrigida (ela dizia que a forma "dispensa os 7
  trims" — você ratificaria 16 trims sobre justificativa falsa).
- **(b)** prereg **v2** escrito com gates em **vida**, **congelado em `5ce4324`
  ANTES de medir**, e executado: **G0 bit-a-bit · G1b e G2 com Δ=0,0000 · G1
  12/15** ⇒ ramo pré-declarado de *falha parcial*, **nada adotado**. Com **um par
  só**, `amp0p4` e `amp0p5` fecham **10/10**; as 3 falhas são todas da `amp0p6` e
  todas por **coordenada** (o nível 0,80 cai *no joelho* dela), não por forma.
  E a discriminância que a métrica vertical não enxergava apareceu: **rampa 12 ·
  cliff 8 · sem forma 0**.
- **(c)** Fig. 3 é **irrecuperável** (eixo Y termina em 20 kN; o inset amplia o
  **começo**, não a cauda — a recomendação anterior estava errada nisso). Fig. 2
  **foi re-digitalizada**: 16 → **134 pontos**, 2 → **45** abaixo de 0,33,
  validada contra o CSV canônico (14/14, pior razão 0,69).

**O achado que muda a fila:** com o dado recuperado, a forma acerta **6 de 7
cruzamentos** — e o tripé **vertical continua impossível**. No rabo o dado cai de
0,20 a 0,104 em **5 ciclos**, então `res.máx < 0,10` exige acertar a fratura em
**±0,05 % da vida** numa fonte com **44 % de scatter de espécime**. Nenhuma forma
determinística passa, e **pedir dado aos autores não resgataria**. A classe
*data-limited* se divide: **DATA-LIMITED** (6 curvas da Fig. 3 — dado não
publicado) vs **METRIC-LIMITED** (`fig2_single` — dado existe, forma acerta em
vida, a **métrica** é o limite).

**Decida (nesta ordem de alavancagem):**

1. ~~**MÉTRICA POR REGIME**~~ ✅ **AUTORIZADA, EXECUTADA e REJEITADA pelos
   próprios gates no mesmo dia** (§4.45; `New_Theory/metrica_vida_results.md`).
   **A sua autorização NÃO foi consumida** — morreu a solução, não o problema.
   - Forma testada: resíduo **ortogonal** em espaço normalizado pela incerteza
     (sem chave de regime: degenera na métrica de hoje no plano, vira vida no
     vertical). Gates congelados **antes** de implementar; medida nos 203 casos.
   - **M2 ✗ (o cliff passa) · M3 ✗ (4 de 6 viradas em trecho raso)** ⇒ ramo
     pré-declarado *"morre"*. Implementação **revertida**, store restaurado,
     métrica canônica intacta, meta segue **147/202**.
   - **Por quê:** a fuga horizontal corre pela inclinação **do modelo**, não do
     dado — um modelo que despenca **varre** o valor do dado e é perdoado. A
     métrica absolvia **colapso prematuro**, que é o que a campanha mais precisa
     pegar. Em `amp0p6` o cliff ficava **melhor que a rampa**.
   - ~~Caminho indicado: correspondência **por nível**~~ ✅ **PRÉ-REGISTRADA,
     EXECUTADA e TAMBÉM REJEITADA no mesmo dia** (§4.46). **A LINHA FECHA.**
     - N0/N1 passaram **bit-a-bit** — a correção estrutural funcionou e a brecha
       da 1ª tentativa está fechada. Mas **N2 falhou** (razão cliff/rampa 1,38×
       contra 2×), por causa **nova**: **a regra de joelho não é invariante à
       amostragem** — mesma curva física, `Δ_col` = 1100 vs **40** ciclos
       conforme a digitalização (**27,5×**).
     - **Bloco B falsificado:** as 16 curvas trimadas, pontuadas inteiras,
       **0 de 16 passam**. Remover os trims sob esta métrica não resgata nada.
       Meta iria de 148 para **139**.
     - **Vale para a sua assinatura da §B:** o `trim_n_max` usa **a mesma regra**,
       logo os trims também não são invariantes à amostragem. Não os invalida — o
       julgamento humano caso a caso está documentado —, mas **invalida
       automatizá-los** por essa fórmula. Convém que a ratificação diga isso.

2. ~~**MÉTRICA DE BANDA**~~ ✅ **PRÉ-REGISTRADA, EXECUTADA — morre no B3, mas a
   LINHA NÃO FECHA** (§4.47; `New_Theory/metrica_banda_results.md`).
   - **B0 ✓ · B1 ✓ · B2 ✓ · B3 ✗ · B4 ✓ · B5 ✓ · B6 ✗.** O ramo que fecharia a
     linha (`B1 ✗`) **não ocorreu**: a **discriminância sobreviveu pela 1ª vez
     em 3 tentativas** — rampa passa, cliff e sem-forma falham, nas **duas**
     digitalizações. E a invariância à amostragem passou com **3,9 %** contra os
     4,0 % previstos pela conta.
   - **BLOCO C — o número que você precisa para decidir sobre os trims:** as 16
     curvas trimadas, pontuadas na curva **INTEIRA**, dão **10 de 16 passando**
     (sob a métrica de nível eram **0 de 16**). Meta iria de **147 para 154**.
   - **Morre por dois defeitos de LIMIAR, um deles meu:** B3 barrou uma virada
     marginal (banda 0,0443 < 0,05 exigido) — o gate fez o serviço; e **B6 é
     internamente inconsistente** (defini *plana* como largura < 0,02 e
     tolerância 0,005, mas largura 0,02 permite mudar 0,02). 3º erro de autoria
     de gate em 3 tentativas.

3. ~~**DECISÃO: 4ª tentativa da métrica, ou parar?**~~ ✅ **AUTORIZADA, EXECUTADA
   — e A LINHA FECHOU** (§4.48/§4.48a; `New_Theory/metrica_banda_v2_results.md`).
   **Nada a decidir aqui; nada foi adotado; nada precisou ser revertido.**
   - **C4, o gate CEGO, reprovou:** no núcleo `amp0p4/0p5/0p6` (nunca usado no
     desenho) a rampa passa **0 de 3**, e em `amp0p6` é **pior que não ter forma
     nenhuma** (0,0718/0,3300 contra 0,0340/0,1116). **A discriminância que o
     `fig2` exibia era artefato de tê-la projetado nele** — C2/C3 (caso de
     projeto) passaram, o cego reprovou.
   - **C7 mata independentemente:** 36 curvas com >50 % dos pontos alterados.
   - **Fecho declarado no próprio prereg:** *"não haverá 5ª tentativa"*.
   - **Custo zero de limpeza:** a tentativa foi pós-processamento puro (a banda
     só precisa de `metric_pred`, já no store) — sem varredura e sem reversão.

> ### 📌 RESPOSTA FINAL DA LINHA DE MÉTRICA (4 tentativas, 0 adoções)
>
> **Nenhuma métrica automática sobre curvas digitalizadas esparsas distingue a
> forma certa da errada no colapso quase-vertical.** Toda métrica que "resolve"
> o problema o resolve perdoando **também o cliff**. As curvas de colapso
> quase-vertical são **metric-limited** e ficam fora da meta por razão
> **metrológica**; o `trim_n_max` **aplicado por julgamento humano e documentado
> caso a caso** é a saída honesta — com a ressalva de que a **regra** que o
> descreve não é automatizável (não é invariante à amostragem, §4.46).
>
> **Isto encerra o item.** O que resta na sua mesa sobre este assunto é apenas a
> **ratificação da §B** de `f5_excecoes_propostas.md`, agora com justificativa
> medida em vez de suposta.

4. *(item anterior, mantido para histórico)* **4ª tentativa da métrica, ou parar?**
   - **A favor:** B0/B1/B2/B4/B5 passaram; o Bloco C (10/16) é o único número em
     toda a linha que justificaria remover trims; a mudança seria **mínima**
     (`h_N` sensível ao espaçamento entre pontos, B6 reescrito coerente, B3
     mantido como está).
   - **Contra, com o mesmo peso:** é a 3ª tentativa; **errei o gate nas três**; e
     a métrica é **unilateral** (só melhora números), o que exige gates mais
     duros, não menos. A posição da §4.46a — essas curvas ficam fora da meta e o
     trim por julgamento humano é a saída honesta — segue defensável.
   ☐ autorizar 4ª tentativa ☐ parar aqui e manter o trim ☐ quero ver o Bloco C
   curva a curva antes de decidir
2. ~~**v3 em coordenadas do joelho**~~ ✅ **ARQUIVADA (2026-07-28, "todos os
   demais")** — seria a 5ª tentativa da linha de métrica, e o próprio prereg da
   4ª declarou *"não haverá 5ª tentativa"* (§4.48a). Arquivar é a única saída
   coerente com o fechamento assinado da linha. A deriva β (bloco novo acima)
   cobre a vigilância de divergência por outra via, informacional.
3. ~~**Varredura das 3 classes nos 55 fora do tripé**~~ ✅ **AUTORIZADA E
   EXECUTADA (2026-07-28).** Resultado: `New_Theory/frontier_classes.md`
   (+ números crus por curva em `frontier_classes.json`, script
   `frontier_classes.py`, só-leitura sobre o store `4f5bedfbace4`).
   **São QUATRO classes, não três** — a 4ª foi imposta pelo dado, não escolhida:
   o `kernel_diagnostic` de 07-27 já havia provado que "nível" é distinto de
   "forma" (grupo B), e forçar essas curvas em *form-limited* mandaria construir
   mecanismo onde ler um piso resolve.

   | classe | n | ação que fecha |
   |---|--:|---|
   | **LEVEL-LIMITED** | **8** | ler o nível — **medido: fecha 1 das 6 sondadas** |
   | **METRIC-LIMITED** | **8** | decisão de convenção (`FLOOR_TRIM` / eixo) |
   | **DATA-LIMITED** | **3** | exceção necessária **por nome** (por contagem: 6) |
   | **FORM-LIMITED** | **36** | prereg + gate, 1 forma por vez |

   > **Estes são os números FINAIS desta sessão — a 3ª medição.** As duas
   > anteriores estão registradas como errata em `frontier_classes.md` §6/§6b:
   > - **1ª (7/7/5/36):** agrupava réplicas pelo **nome** (`_repN`) e perdia a
   >   fig8 do Bauer (`testN`) ⇒ 3 repetições do mesmo ensaio em 3 classes
   >   diferentes. Defeito apontado pela sua outra sessão.
   > - **2ª (6/6/8/35):** consertou o agrupamento mas **super-atribuiu** —
   >   marcava TODOS os membros de um grupo com dispersão > 0,10, quando
   >   dispersão alta prova que **ao menos um** viola, não que todos violem.
   > - **3ª (esta):** teto de grupo por busca exaustiva. Reproduz **exatamente**
   >   os tetos da varredura de réplica (fig6 3 de 6, fig8 2 de 3) e o nome
   >   `test1`. **Divergência que sobra, e é fina:** no fig6 a varredura nomeia
   >   `rep1/rep5/rep6`, mas existem **3** subconjuntos viáveis de tamanho 3 e
   >   `rep5`/`rep6` aparecem em algum deles ⇒ **só `rep1` é necessária por
   >   nome**. A contagem (3) está certa; o nome super-especifica.
   >
   > **Achado de método que vale além disto:** a 1ª tentativa do cálculo de teto
   > contradisse a varredura por causa da **grade de interpolação** — 40 pontos
   > sub-resolvem a dispersão em ~1 %, o que bastou para virar o limiar 0,20
   > (0,19944 com n=40 vs **0,20134** convergido). Grade agora em 800.

   **19 das 55 saem da conta de "precisa de física nova"** — era exatamente o que
   o item pedia. Os 7 de nível violam **só o pico** (MAE já dentro) e estão em
   **7 fontes diferentes**, então é o piso per-par, não uma fonte doente.
   Controle contra 9 veredictos já estabelecidos: **7/9 coincidem**; as 2
   divergências corrigem afirmações anteriores com número (§3 do relatório) —
   (a) `eccles fig6` **não** é limitada pelo `FLOOR_TRIM` (o piso come 4/29 dela,
   contra 27/35 do fig8b), logo a decisão (i) do item 6 desta fila vale para o
   **fig8b** e não para a família; (b) no `fig8c` o nível **não** fecha, erra por
   **0,0021**. Achado lateral: o LU_2024 também tem dado que vai a zero
   (33% e 46% dos pontos sob o piso em amp1p5/amp2p0), o que não estava
   registrado. **Nada foi adotado.**

   ### ⚠ SEQUELA MEDIDA NO MESMO DIA — a conta "147 → 154 de graça" NÃO existe

   `New_Theory/level_seven_probe.md` — **as 7 medidas** (a 7ª custou 2960 s:
   5.000.000 de ciclos × 4 passadas). Sondei as **duas** alavancas de nível que a
   campanha sabe **LER** do dado — `loose_arrest_floor` do platô final e
   `emb_depth` da queda-inicial, os dois leitores L24 — injetadas por
   `_prefit_overrides`, com **controle negativo bit-a-bit** antes de cada sonda e
   **sem escrever no store**. Resultado: **fecha 1** (`chu…test1`, maxerr
   0,1147 → **0,0082**), **melhora 1** sem fechar, **2 INERTES** e **3 PIORAM**.

   **Regra estrutural que fechou 7/7:** as 2 inertes são exatamente as 2 sem
   chave de pack no cfg (`loose_torsion_mode` ausente), com Δ = 0 **exato**; as 5
   com pack nunca são inertes. O gotcha do `CLAUDE.md` deixa de ser advertência.
   **E o preço cai no pior lugar:** o `liu2016wear_fig7_run2_5e6cyc` é a curva
   **mais perto de fechar entre as 55** (viola por **+0,0035**) — e a alavanca
   mais barata é **inerte justamente nela**.

   **Cruzamento independente:** a sua outra sessão mediu a MESMA pergunta no
   mesmo dia (`level_limited_floor_read_2026-07-28.md`), sem saber desta.
   Confrontei por script: **19 de 19 números compartilhados idênticos**, e as
   duas medições são complementares (eles previram por direção sem simular; eu
   simulei). Reconciliação, com as 3 diferenças resolvidas:
   `New_Theory/level_seven_reconciliacao.md`.

   **Eu havia escrito que essas 7 eram "o alvo mais barato da meta". Está
   corrigido:** o resíduo *é* de nível (propriedade medida), mas o nível **não é
   alcançável pelos leitores existentes** em 5 das 6. O ganho medido pelo caminho
   da leitura é **+1 curva**, e ela ainda depende do gate PR-37′ — o piso lido
   ali é **0,9876** (afrouxamento trava a ~99% de F₀), um input **por caso** numa
   fonte de família não-monotônica, exatamente o que o critério G-A3 manda olhar
   com desconfiança.

   **Achado de método que vale mais que as 7 sondas:** um **pré-teste de direção**
   prevê **7 dos 7** desfechos sem simular nada — se o valor LIDO não move a
   retenção para o lado que o `res.médio` exige, a sonda PIORA. Duas linhas de
   aritmética sobre o store antes de gastar sonda (a última custou 2960 s). Com
   um passo anterior que a 7ª curva impôs: **conferir se a alavanca está VIVA no
   cfg daquele caso** — senão o teste atribui a "direção errada" o que é um campo
   morto. Predição declarada ANTES do resultado e confirmada (§4 da reconciliação).

   **Achado colateral (mesma classe dos erros de instrumentação de 07-27):** o
   leitor do piso e a métrica **discordam sobre onde a curva acaba** —
   `arrest_floor_from_curve` faz a média dos últimos 5% do ratio **cru**, e a
   métrica pontua só o trecho `≥ 0,10`. No `eccles fig8a` o piso lido é 0,0122
   (o dado cru vai a perda quase total) contra uma janela de métrica que termina
   em 0,10.
   ☐ ciente ☐ autorizo prereg do `chu…test1` (a única que fecha, com gate PR-37′)
   ☐ quero saber que constante governa o nível quando o piso não é a resposta
4. **CSV fino da Fig. 2** (`New_Theory/liu2025_fig2_fine.csv`) — **não** substitui
   o canônico. Adotar exige re-simulação + re-carimbo de fingerprint + gate.
   ☐ adotar com gate ☐ manter como experimento
5. **Carta aos autores** pedindo as séries brutas de 200 Hz do DH5902N: segue
   valendo para as **6 curvas da Fig. 3** e para medir o scatter de espécime —
   mas **não** resgata o tripé vertical de nenhuma.
   ✅ **REDIGIDA** (`New_Theory/liu2025_data_request_DRAFT.md`). **O ENVIO é ação
   externa e fica com você** — e-mail a autor não sai por autorização em bloco;
   quando quiser enviar, o rascunho está pronto para revisão final.

## ~~DECISÃO NOVA (2026-07-17): merge do branch feature/l1-l7-gaps (L1-L7)~~ ✅ JÁ EXECUTADA em 2026-07-21 — item estava VENCIDO (4º da série)

**Auditado 2026-07-28:** o merge aconteceu no `166a761` (F0.2 do prompt-mestre),
com pré-merge `3f54053` (58 cópias de leitura), store pós-merge re-carimbado
(`ae2d7e0`, fingerprint `01689f0bfad8` da época) e **baseline re-pinado a 202
casos** (F0.4 `8cedbe5` — os 22 casos novos JÁ estão na base). Das fatias: L2
`kj_mode=pedersen` **ADOTADO** (verdict no config ZHANG_2006, gate T6 PASS-inert
8/8); L7 bound informacional **gravado nos 203** (CLAUDE.md item 6); L5 doc
mergeada; **L3 segue default-inerte** (calibração per-rig = trabalho de campanha,
único resto vivo deste item); L1 **não adotado** (falsificado 2×, correto).
Este bloco ficou 7 dias dizendo "decida o merge" com o merge feito — mesma
classe dos itens vencidos do roadmap (§4.43); a regra "quem adota atualiza este
arquivo no MESMO commit" existe por isso.

Sua sessão paralela completou as 8 fatias (19 commits; relatório:
New_Theory/l1l7_final_report.md NO BRANCH; paridade bit-a-bit com flags off
verificada; ZERO adoção executada — D3 respeitado). Handoff por fatia:
- Merge seguro: Fatia 0 (KB âncoras R5) · L7 bound informacional · L5 doc.
- Adotável como proveniência: L2 kj_mode=pedersen (PASS-inert, Δ=0 exato).
- Manter default-inerte até calibração per-rig: L3 (F_amp↔δ) — vira
  trabalho DA CAMPANHA pós-merge (mu_eff_lo/F0_ref/gross_ceiling_decay).
- NÃO adotar: L1 (falsificado 2×, ~8× raso; rodada 6 com forma mais íngreme;
  22 casos novos Zhang2018/19+Liu2020 wired como alvo — hoje sobre-prevê).
Ao decidir o merge, a campanha assume: pré-registros de adoção das partes
seguras + calibração L3 + baseline dos 22 casos novos (base 180→202).

## DECISÃO DE MAIOR ALAVANCAGEM (consolidada 2026-07-15)

> ## ⚠ ESCOPO CORRIGIDO POR MEDIÇÃO (2026-07-27) — leia antes de autorizar
>
> **As quatro fontes nomeadas abaixo estão erradas.** Diagnóstico completo em
> `New_Theory/kernel_diagnostic_2026-07-27.md` (nenhuma tentativa de prereg
> gasta). Correlacionando os perfis de resíduo **com o nível removido** (o nível
> já é legitimamente per-rig via `loose_arrest_floor`, então só um desacordo de
> *forma* justifica forma nova), as 26 curvas se separam em **três** problemas:
>
> | grupo | curvas | o que é |
> |---|--:|---|
> | **A — forma coerente** | **13** | Chu2026 7 · Yang2019 4 · Karlsen 1 · Zhang2006 1. Correlações mútuas **0,90–1,00** em 4 rigs independentes: o modelo colapsa cedo demais e trava tarde demais. **É este o alvo do prereg.** |
> | **B — nível, não forma** | 2 | Eccles fig8a/8c. Perfil detrendado **plano** (máx |0,022|), resíduo ~−0,043 uniforme ⇒ pede revisão do floor lido, **não** física nova. **[medido POR CURVA em 07-28: a planura 0,022 era a MÉDIA das 2; por curva é 0,047 e 0,054. Com o nível consertado sobra 0,080 no fig8a (**entra**) e 0,102 no fig8c (**não entra**, por 0,0021). A recomendação vale para UMA das duas.]** |
> | **C — outra forma** | 11 | Lu2024 10 + Sun grease-standard 1. Lu tem erro em **tigela** (máximo no meio) — tempo de joelho, r = **−0,27** com Chu. Sun: r = **−0,74**. |
>
> **Lu2024, Eccles e Sun — três das quatro fontes que a proposta nomeia — NÃO
> pertencem à família coerente**; Yang2019, Karlsen e Zhang2006, que ela não
> cita, pertencem. Um prereg nas 4 fontes originais teria misturado formas
> **anticorrelacionadas** (até r = −0,78) e falhado por construção, queimando o
> FAIL2 de uma hipótese que, no escopo certo, segue viva.
>
> **Recomendação original:** (1) prereg do kernel escopado no **grupo A**;
> (2) Eccles 8a/8c: tentar **nível** antes de forma; (3) Lu2024+Sun: diagnóstico
> próprio.
>
> ### ⛔ (1) EXECUTADO NO MESMO DIA — **FAIL1** (prereg `2026-07-27-kernel-grupoA`)
>
> A forma testada foi um **expoente na comporta de arresto** que já existe:
> `g = max(0, 1 − F_min/F₀)^m`, default 1,0 bit-idêntico. Ajustada no Chu e
> transferida sem re-fit:
>
> | gate | exigido | medido |
> |---|---|---|
> | **G3 transferência** | res.máx médio cai ≥30% nos 3 rigs de fora | **PIOROU 9%** (0,2822→0,3075) |
> | **G2 alvo local** | ≥8 das 13 no tripé, nenhuma pior | **1 entrou, 4 pioraram** |
>
> Fecha lindamente a curva em que foi ajustada (`chu…test1` res.máx 0,115→0,035)
> e degrada as de fora (Karlsen 0,236→**0,378**). É o retrato de um valor que não
> transfere — **o G3 pegou exatamente o que existe para pegar**.
>
> **Ressalva honesta, e é defeito do MEU prereg:** o gate de auto-travamento vale
> **exatamente 1** onde não há piso de arresto, e `1^m = 1` — o expoente é inerte
> ali. No Chu, **só 1 das 9** curvas tem piso ativo, então "ajustar na maior
> fonte" foi, na prática, ajustar em **uma curva**. Ancorar num rig com piso
> ativo (Yang2019 tem 4) testaria a mesma forma com muito mais poder. Isso **não
> autoriza refazer** — o gate está gasto e trocar a âncora depois de ver o
> resultado é o que a imutabilidade proíbe. Fica a regra para a próxima:
> *antes de escolher a fonte-âncora do gate de transferência, verificar que o
> mecanismo modulado está ATIVO nela.*
>
> **Sobra 1 tentativa**, e o prereg exige que seja com **forma diferente**, não
> com outro valor. As 13 curvas seguem form-limited.
>
> ### (3) TAMBÉM EXECUTADO — e o enunciado da decisão conflava DOIS mecanismos
>
> Diagnóstico do Lu2024 em `New_Theory/lu2024_diagnostic_2026-07-27.md` (sem fit).
> **O Lu não precisa de aproximação suave ao piso — precisa de perda mais rápida
> NO COMEÇO.** Medido: a fração da perda total consumida nos primeiros 1-2 ciclos
> é **47% no dado contra 27% no modelo**, com **9 das 10 curvas na mesma
> direção**; a largura do joelho é **5,82 no dado contra 1,52 no modelo** (~4×
> mais estreita). O dado perde **37% da pré-carga em ~2 ciclos**.
>
> | | o que faz | situação |
> |---|---|---|
> | **(a)** aproximação suave ao piso | só age perto do floor | **FAIL1** hoje, no grupo A |
> | **(b)** taxa **front-loaded** (decai desde o ciclo 1) | redistribui perda para o começo | **é o que o Lu pede — NUNCA testada** |
>
> O enunciado "kernel desacelerante **com** aproximação suave ao floor" junta as
> duas num item só. O `k_ratchet` atual dá rotação ∝ slip = taxa ~constante;
> **nada no canal de afrouxamento decai com a rotação acumulada**. A decisão que
> vale a pena autorizar agora é (b), com prereg próprio — e o Lu tem duas
> varreduras ortogonais (amplitude 0,25–2,0 mm e torque 4–28 N·m), o que permite
> testar a transferência **dentro da fonte** antes de arriscar cross-rig, que é
> exatamente o critério que faltou no grupo A.
>
> ### ⛔ (b) EXECUTADA EM CONTAS 2026-07-28 — FALSIFICADA em 2 parametrizações, zero preregs (`lu2024_frontload_resultado.md`)
>
> O desenho intra-fonte acima foi aplicado tal como pedido: âncora na fig18
> (amplitude), cegas na fig20 (torque). **As duas variantes** (decaimento em
> θ_acc absoluto e em fração de F₀ perdida) **melhoram a âncora ~40 % e
> DANIFICAM as cegas de torque alto** (T22 0,052→0,102; T28 0,041→0,089; a
> normalizada piora até a T16). Padrão = redistribuição de erro, não física
> faltante: o front-load que o Lu pede é **dependente de condição dentro da
> fonte**. A linha N_emb também fechou (gate FAIL 2×, mesmo com regra de
> isenção por feature pré-medida — o amp0p25 tem o MAIOR déficit e piora).
> **LU_2024 segue form-limited com descrição afinada; nada adotado; nenhum
> prereg queimado.** Ganhos reais registrados como informação (T16Nm entraria
> sob N_emb=1; fig18 −40 % sob front-load).

**Kernel de colapso desacelerante com aproximação suave ao floor** — *(enunciado
original de 2026-07-15, mantido para procedência; ver a correção de escopo
acima)* — a MESMA
forma que falta trava QUATRO fontes (~25-30 curvas): Lu2024 (dado desacelera
ao platô; kernel ratchet bifurca arrest/runaway — PR-25/34c/35, 3× confirmado),
Eccles2010 (aproximação exponencial suave; **5/8 no tripé hoje**, restam
fig8a/8b/8c — item 6), Chu2026 (profundidade não-monotônica — item 5),
Sun-crimp grease (colapso→trava).
Proposta mínima: taxa de afrouxamento ∝ F0 (exponencial) com termo de
aproximação suave ao floor (ex.: taxa ×(1−floor/ratio)^m), default-inerte.
Se autorizada, pré-registro com gates nas 4 fontes de uma vez.

**[2026-07-27] Gates já escritos** para a parte Eccles deste kernel em
`docs/superpowers/specs/2026-07-27-eccles-g2-prereg.md` — em especial o
**G-A3 (transferência entre FONTES)**: ajustar o parâmetro de forma em UMA
fonte (Lu2024, a maior) e prever as outras **sem re-fit**. Critério duro
registrado ali: *se o kernel precisar de constante própria por fonte, ele não
é uma forma — é um tuner com nome bonito e não deve ser adotado.*

## Formas novas de engine (precisam do seu "autorizado" — cláusula PR-3)

1. **Yang2023 IJPEM — bifurcação de limiar de amplitude** (7/9 violam o
   tripé; maxerr até 0.56). O dado near-threshold é bifurcação
   (afrouxa/não-afrouxa), não power-law — `loose_amp_exp` (keeper PR-21) é
   insuficiente. Proposta: gate de limiar com histerese em δ (forma nova).
   **[Execução mestre 2026-07-21 — evidência NOVA, tri-falsificação]:** a
   varredura F3 esgotou o espaço de nível: (i) k_ratchet é INERTE no caso
   0,25 mm (maxerr 0,427 idêntico de 0,02 a 0,12); (ii) delta_free relido é
   BINÁRIO (0,14 mm flipa para sobre-colapso −0,64, sem meio-termo);
   (iii) loose_amp_exp re-testado PIORA tudo. O dado exige resposta graduada
   N_L ∝ δ^−3,5..−3,8 (lei do próprio paper) que o ratchet+take-up não
   produz. Os 7 casos ficam form-limited até esta decisão.
2. **Yang2021 — supressão axial composta** (6/6 violam). O dado n=5 é
   confundido (F_ax e δ variam juntos); PR-23 foi recusada por isso.
   Destrava com: dado novo (sweep F_ax com δ fixo) OU decisão de construir
   com o confound documentado.
3. **Classe fratura — FECHADA COM DIAGNÓSTICO (PR-39v2, 2026-07-16)**: Ti
   (li2022ti) ADOTADO (C1 per-material, cliff 410k exato); LIU_2025 =
   scatter de espécime irresolúvel (mesma amplitude fratura em 10k vs vive
   a 14.4k; slope local 4.1 ≠ 2.7) — cliff representável só per-espécime
   (não-preditivo, não adotado). Sun-secos aguardam o mesmo tratamento se
   desejar. Original:
   **Classe fratura — cauda até zero** (liu2025 fig2/amp0p4, li2022ti full,
   yang2021: maxerr 0.2-0.5 nas caudas). FatigueLoss bending (PR-24) é
   keeper validado mas fora-da-métrica (a digitalização para na fratura).
   Decisões possíveis: (a) redigitalizar essas curvas ATÉ o zero;
   (b) adotar a FatigueLoss no canônico p/ essas fontes; (c) manter caveat.
   + Sun-crimp transversal SECO ×2 (PR-32: Estágio III = trinca de
   cisalhamento do parafuso, F→0; baselines 0.61/0.67 ficam como custo
   visível da classe).
   **[2026-07-27 — a opção (b) ganhou forma concreta; PRÉ-REGISTRO PRONTO,
   aguardando seu "autorizado".]** `docs/superpowers/specs/2026-07-27-liu2025-
   fracture-ramp-prereg.md`. O que mudou: o resíduo do Liu 2025 **não** é o
   cliff (PR-24 já dizia isso, mas sem forma candidata) — é a **rampa
   pré-fratura**, e ela tem uma leitura física barata: a trinca reduz a seção,
   `k_b ∝ A` cai, e com o deslocamento de montagem travado `F_0` cai junto
   **realimentando o laço de afrouxamento que o engine já tem**. Uma forma
   compra a rampa e a aceleração. Reusa `state.D_fatigue` (Miner já acumula):
   2 parâmetros, `D_on` com procedência de handbook (propagação = últimos
   10–30 % da vida em HCF, contra 20–29 % medidos nas 7 curvas).
   Banco de prova: `fig2_single` SEM trim — a **única** das 7 com colapso
   medido até 0,000 (as outras saem pela borda do gráfico em 0,33).
   Custo de não fazer, medido hoje: o trim exclui **71,9 % em média da perda
   de pré-carga medida** desta fonte — os "7/7 no tripé, MAE 0,047" cobrem
   ~28 % da perda. Isso é argumento para o §B da lista F5 (bloco de 16
   curvas), não contra ele: se a forma passar, os trims da LIU_2025 caem por
   consequência.
4. **Eccles 2010 — retenção prevailing-torque** (se a leitura do paper
   mostrar que µ_rosca alto + floor lido não bastam): forma de torque de
   prevalência (resistência independente de F0). Será detalhado quando o
   alvo #5 rodar.
5. **Chu2026 — família D não-monotônica** (PR-30/PR-38: test1 ADOTADO
   escopado 0.334→0.066; família segue): a instância PR-38 provou que a
   mediação µ(N) FUNCIONA (test2 ×2.05 vs ×2.21 medido) mas NÃO fecha a
   família sozinha — 3 lacunas estruturais: (a) run-in do µ dirigido por
   CICLO (não por W_slip); (b) o kernel bifurca stick/colapso onde o dado
   mói em taxas intermediárias (60× de faixa — MESMO item do kernel
   desacelerante); (c) níveis de arrest não-monotônicos. Original:
   profundidade de colapso invertida (D=0.4→0.14 lento; D=1.0→0.57 rápido) =
   cinemática de acúmulo de torque mediada por µ_plate(N) evolutivo (medido
   no paper, Fig. 5, NÃO digitalizado). Destrava com: (a) redigitalizar a
   Fig. 5 (µ(N) por teste, ~30 min de agente) e/ou (b) autorizar estudo do
   kernel cinemático per-rig. O caso-limiar test1 JÁ fecha (0.056) com o
   c_bend lido — o resto aguarda.
   **[Execução mestre 2026-07-21 — item DESATUALIZADO]:** a Fig. 5 JÁ FOI
   digitalizada (2026-07-15): 5 CSVs µ_plate(N) prontos em
   `BAS_V2_papers/E.../figures/` + `apparatus_notes/chu2026ti.md` §Fig.5
   (tests 1/2/4/7/8; tests 3/5/6/9 NÃO têm COF no paper — limite estrutural).
   O que falta é só o ENCANAMENTO: `mu_bearing_schedule` default-inerte
   (lookup µ(N) por ciclo, idioma do delta_spectrum — input de MEDIÇÃO, não
   forma nem fit). A execução mestre vai implementá-lo sob o mandato do
   caminho (a) desta entrada (TDD + bit-identidade; rollback = revert) —
   alvos test2/4/7/8; test3/9 ficam kernel-limited (run-in por CICLO).
   **[2026-07-28 — EXECUTADO E FECHADO, com FAIL informativo]:** o encanamento
   FOI construído (F3.2-CHU, engine ok) e a adoção per_case FALHOU o G-CHU-a
   em 21/07 (`f3_chu_result.json`). Em 28/07, as sondas de fechamento
   (`chu_schedule_isolado.py`, `chu_energywear_sonda.py`) provaram que o µ(t)
   medido é quase inerte (wear disp-mode = Archard, sem µ) e que nem a lei
   recolorida (wear energético) fecha a âncora. **Item encerrado** — ver o
   bloco "Chu2026 — FECHADO COM PROVA EM NÍVEL DE LEI" desta fila; os 6 casos
   são candidatos a exceção assinada.

6. ~~**Eccles2010 — adoção parcial travada no G2**~~ **[VENCIDO — 2026-07-27.
   NÃO DECIDA COMO ESTÁ ESCRITO ABAIXO; leia primeiro
   `docs/superpowers/specs/2026-07-27-eccles-g2-prereg.md`.]**

   Três correções ao enunciado original, todas medidas sobre o store
   certificado (fingerprint `4f5bedfbace4`):
   - **A opção (a) já aconteceu.** A receita do PR-31 **está adotada** nos 8
     grupos desde o commit `4402cd4` de **2026-07-15** ("PR-37' ADOTADO
     (instancias paralelas)") — entrou de carona num commit de outro assunto
     no mesmo dia em que este item foi escrito, e a fila nunca foi corrigida.
     **Regra nova: quem adota atualiza este arquivo no MESMO commit.**
   - **Os números mudaram:** maxerr<0.1 hoje é **5/8**, não 4/8 (o fig7d saiu
     de 0.005 do corte para 0.089). O baseline de mediana 0.148 não existe.
   - **A opção (a) nunca poderia fechar curva** — e a conclusão SOBREVIVE à troca
     de régua, mas o argumento que a sustentava **não**. Cuidado ao reusar a
     frase antiga em outro item.
     · O que estava escrito (2026-07-27): *`MAE ⊆ maxerr` — zero curvas violam só
       o MAE*. **Isso VENCEU em 2026-07-29:** a inclusão dependia de
       `META_MAE = META_MAX = 0,10`; com `MAE ≤ 0,05` contra `res.máx ≤ 0,10` ela
       deixa de valer, e hoje **5 curvas violam só o MAE** (`liu2025_M16_amp0p3`,
       `liu2022_fig8_multi_t2`, `li2022ti_axialmin_10Hz`,
       `liu2016wear_fig9a_m45nm`, `caccese2009_tapered_45kN_rep1`).
     · **Por que a conclusão deste item continua de pé:** nenhuma das 5 é do
       ECCLES_2010. Medido em 2026-07-29 (store `3546e6745448`): das 10 curvas do
       Eccles, **3 passam no tripé** e nas **7 fora a perna que MANDA é o σ_res em
       todas as 7** (fig8a 0,0394 · fig8c 0,0390 · fig6 0,1887 · fig7c 0,0258 ·
       fig7d 0,0565 · fig8b 0,0552 · fig8d 0,0939, contra limite 0,025).
       ⇒ aceitar G2=MAE-only segue movendo **zero** curvas do Eccles para dentro
       do tripé; segue sendo afrouxamento de contabilidade, não progresso.
     · **Consequência NOVA para o escopo deste item:** o gargalo do Eccles não é
       mais o pico — é o σ_res em 7/7 das fora. Um kernel desacelerante que
       ataque só o resíduo máximo **não fecha nenhuma delas**. Se este item for
       retomado, o alvo tem de ser a perna do σ_res (forma do resíduo), e aí ele
       colide com o achado de que nenhuma das 18 alavancas varridas fecha essa
       perna — ver `MODEL_LEGITIMACY.md` §8.

   **O que de fato resta** (detalhe e gates no prereg): (i) `fig6` e `fig8d`
   resolvem para **nenhum grupo adotado**; (ii) `fig8a/8b/8c` (res.máx
   0.122–0.145) pagam pedágio no kernel desacelerante. Recomendação de escopo:
   **não** fazer prereg de kernel só-Eccles; 3 curvas não justificam física
   nova, 25-30 em 4 rigs justificam.

   **[TRILHA B EXECUTADA 2026-07-27 — G-B1 FAIL, e o achado é outro.]**
   Aplicar a receita a `fig6`/`fig8d` (grupo-de-porca lido da nota, floor=0
   pelo critério de destacamento do paper) **piorou muito**: fig6 res.máx
   0.467→1.028, fig8d 0.252→0.400; os 8 tratados bit-idênticos. Não foi
   esquecimento: a nota de aparato já dizia que **nenhum mecanismo V2
   representa o cenário axial+transversal combinado** e nomeava 7(d)/8(b)/8(d)
   como o falsificador-alvo. **Achado maior:** o `FLOOR_TRIM` (descarta
   `ratio<0.10`) **apaga o resultado central do paper** — o dado cru vai a
   ZERO (destacamento) em fig6/7d/8b/8d, e a métrica corta 4/29, 4/26,
   **27/35** e 7/37 pontos. O `fig8b` é pontuado sobre 8 de 35 pontos, e o
   `fig7d` **passa no tripé por artefato de convenção**. Um modelo fisicamente
   certo aqui é PENALIZADO. **NOVA DECISÃO (família de sobreposição axial, 4
   curvas — fig6/7d/8b/8d):** (i) isentar a família do FLOOR_TRIM e medir a
   curva inteira; (ii) declarar fora-de-modelo e mandar as 4 para exceção com
   esta prova; (iii) construir a condição de contorno axial externa que
   sobrepõe o piso de arresto. Recomendação: **(ii) agora, (iii) só se a
   família crescer** — 4 curvas de uma fonte, mecanismo conceitualmente novo
   (contorno, não mecanismo de perda) que não transfere para nenhuma outra
   fonte da biblioteca hoje.
   A MESMA decisão destrava o Sun-crimp grease-crimp (PR-32: Estágio I =
   colapso exponencial idêntico; hoje 0.207 baseline).
   **[Execução mestre 2026-07-21 — parcialmente DESATUALIZADO]:** o Sun
   grease-crimp NÃO depende mais desta decisão — fechado por leitura
   (k_wear_spec=1,5e-15 da planura do platô, F3-LOTE2: 0,022/0,089). O Sun
   grease-STANDARD (0,0999/0,319) continua dependendo do kernel
   desacelerante (mesma família da DECISÃO DE MAIOR ALAVANCAGEM acima).

7. **Yang2023 AME — jet nut CFRP axial** (1 caso, baseline 0.39): tripla
   combinação fora do modelo (porca self-locking TC16 + membro CFRP 48 plies
   + carga R=0 pulsante). Rotulado sem tentativa (charter previu); destrava
   junto com a decisão prevailing-torque (itens 4/6).

8. **âncora interna — incubação do assentamento** (PR-36): dado plano até N≈38 e o
   modelo assenta desde o ciclo 1; embedding-com-atraso não existe no engine
   (o slip_onset_W não gateia embedding). Forma pequena (2 curvas, maxerr
   0.16-0.18); candidata a acoplar na decisão de kernel.

9. **Zhang2006 — dado sintético na galeria antiga** (frota 2026-07-15): as
   9 "curvas de grip" (12.7-50.8mm) da galeria/report_data NÃO são
   rastreáveis ao PDF real (que traz endurance S-N; DOI do database errado,
   corrigido na nota). O canônico-180 está limpo (só as 2 curvas REAIS
   digitalizadas entraram). Decida: expurgar os 9 sintéticos da galeria +
   rotular zhang_grip_sweep.py, ou manter com aviso.

10. **Rousseau 2025 — 3 curvas, e o diagnóstico da fila está VELHO**
    (2026-07-27; gates em `docs/superpowers/specs/2026-07-27-rousseau-prereg.md`).
    **Antes de decidir, saiba que o roadmap item 10 do CLAUDE.md e a §4.20 do
    MODEL_LEGITIMACY descrevem um estado que não existe mais:** eles dizem que
    o *stroke-split* de cisalhamento do membro "segue não-construída" e que o
    modelo é "cego à espessura". Medido hoje, o `k_member_shear` está **vivo**
    desde o PR-14 (2.00e6/1.67e6/1.43e6 N/m em t10/t12/t14) e o slip cai
    monotonicamente **0.232 → 0.134 → 0.000 mm** (t14 em **stick permanente**
    pelos 400 ciclos — é por isso que ele não colapsa); os 3 finais HDPE
    acertam. Os MAE citados no roadmap (0.228→0.373→0.380) são hoje
    0.058/0.064/0.044.
    **O que resta são dois problemas distintos, não uma forma faltante:**
    (i) `steel_t10` — arresto **terminal** (res.máx 0.188 no ÚLTIMO ponto;
    retém 0.325 contra 0.137 medido) e é o aço com MAIS slip resolvido, logo
    o defeito é a perda-por-slip saturar cedo, não falta de slip; (ii)
    `hdpe_t10/t12` — res.máx 0.153/0.138 no MEIO da curva com os finais
    certos, ou seja, tempo de joelho; e as amplitudes são **por espécime**
    (paper Tabela 2: 0.5/0.49/0.38 mm), o que pode tornar a fonte
    irredutível a uma forma única — desfecho seria exceção com prova.
    Decida: (a) autorizar as duas trilhas do prereg; (b) só a trilha do aço;
    (c) mandar direto para exceção.
    **✅ G0 (bloqueante) EXECUTADO em 2026-07-27** — o roadmap item 10 do
    CLAUDE.md e a §4.20 do MODEL_LEGITIMACY foram re-baselinados com os números
    medidos, e a linha do PR-10 no changelog levou marca de SUPERSEDIDO. Você já
    pode decidir (a)/(b)/(c) sobre texto que descreve o estado real. **Achado
    do G0 que vale além do Rousseau:** o `config_used` do store não registrava o
    `k_member_shear` de fato aplicado, então uma constante ATIVA e
    fitada-this-rig era invisível na auditoria — foi assim que o "INERTE" do
    PR-10 sobreviveu 16 dias. Corrigido (fonte única `_effective_overrides` + 2
    testes; re-sim bit-idêntica). É a 3ª errata da mesma classe
    (`delta_spectrum` §4.33, `_read_ref_csv` no S5).

8. **🆕 2026-08-21 — taxa-com-estado no canal de WEAR (corcova do miolo): a
   ÚNICA curva restante da fila exige forma nova.** A `liu2025_M16_amp0p8`
   (fila form-limited = só ela; σ 1,68×, MAE/mx dentro) teve a última forma
   in-engine varrida e falsificada com TETO: a forma da rampa de fratura
   (`fat_ramp_D_on`/`q`, 28 células incl. fora da banda N_D do paper) tem
   σ mínimo **0,0283 = 1,13×** — nunca fecha; `t_0` composto quebra o mx; o
   canal de damage falsificado em DUAS dinâmicas (starters W_ref=1e4 explode
   σ 0,11–0,16; lenta W_ref 1e5–1e6 dá 0,0411 — adiciona queda TARDIA, nunca
   no miolo). Com a rampa no ótimo o resíduo vira todo-positivo com **corcova
   em u≈0,2–0,6** (+0,063 no 2º terço): falta wear/dano que ACELERE no meio e
   desacelere antes do fim — taxa dependente do estado, que nenhum kernel
   atual produz (12 estruturas falsificadas no total desta curva; prova:
   `liu2025_par_de_taxas_opostas.md` §5). Decisão: (a) autorizar desenho da
   forma (candidata natural: expoente de amplificação do wear dirigido por
   `δ_wear` acumulado, saturante — irmã do `graded_scrit`, que trata limiar e
   não taxa); (b) declarar a curva form-limited com o censo de falsificações
   como prova e a fila encerra em ZERO por esgotamento medido.
   **[16:5x–17:1x — a via (a) FOI EXECUTADA sob o "continue" e o veredito
   está medido]**: a forma da anatomia (`onset_burst_W`, gate próprio do
   burst — sino desacoplado do wear) foi construída (TDD 4/4, +1 campo
   dormente, fig14 bit-idêntica) e sondada na curva: **o sino é real**
   (σ 0,0507→0,0271 dentro do ramo, a maior redução que a curva já viu)
   **e não fecha** — o dreno quebra o mx (0,11+) e a célula exige **6
   números fitados sem procedência numa curva só**, que a regra do projeto
   proíbe. Prova: `par_de_taxas` §7; censo de falsificações: **16**. ⇒ a
   decisão restante é a **(b)** — declarar form-limited por esgotamento
   medido (17 estruturas — lista enumerada no topo do par_de_taxas —, incl. a forma desenhada especificamente para a
   anatomia dela) e a fila de modelo encerra em ZERO. A capacidade fica
   dormente aguardando 2ª instância com procedência de leitura.

## Capabilities validadas aguardando adoção canônica (decisão de escopo)

- Cattaneo-Mindlin slip-regime (validada 2026-07-07; adoção = sua chamada).
- Fatigue-tail Su-N (validada 2026-07-08; idem).

**[2026-07-28, leitura da autorização em bloco]:** estas duas NÃO foram adotadas
sob o "todos os demais" — adoção sem **alvo de gate** identificado só mexeria
fingerprint sem ganho (a regra que o estudo Chu aplicou às correções de
procedência). Ficam aguardando um alvo: CM apareceu hoje como alavanca de
joelho no Rousseau HDPE (mas com puxões opostos t10/t12 — não adotável); Su-N
bilinear cross-size segue bloqueada por c_σ conhecido em só 2 tamanhos (§4.49).

## Kernel A — LEITURA DE FORMA concluída (2026-07-28, pré-FAIL2): o grupo honesto é 9, e o FAIL1 tem explicação mecânica

`New_Theory/kernel_formA_leitura.md`. Três achados: (1) a coerência "0,90–1,00" era
entre médias por fonte — por curva a mediana é 0,67; (2) lei de taxa quantificada:
dado ACELERA (p=−0,29), modelo DESACELERA (p=+0,44) — o gap é de estrutura temporal;
(3) a mesma assinatura é carregada por wear (Chu 93 %), rotational (Karlsen/Yang) e
creep (Zhang 100 %) ⇒ **o FAIL1 (expoente de arresto, só rotacional) estava
estruturalmente perdido antes de rodar** — candidato dentro de UM canal repete a
morte. Cortes: 2 Yang (metric-limited), chu test1 (outlier 9,6× — vai p/ o problema
de sub-limiar) e zhang2006 (procedência SINTÉTICA declarada na nota; re-derivar da
endurance antes de usar). **Núcleo: 9 curvas / 3 rigs.**
**Sonda F₀×slip EXECUTADA (2026-07-28, mesmo dia — `kernel_f0slip_resultado.md`):**
o candidato "expoente compartilhado no driver" está **MORTO na leitura** —
a_impl = 2,17/−1,20/4,45/−0,96/−216, incoerente até dentro do Chu. Fatos novos:
o Chu está em **gross-slip profundo (slip constante)** e o wear do modelo cai
∝ F₀ puro; e **nem o dado do Chu compartilha lei de taxa** (p_dado de −0,75 a
+2,52 no mesmo rig). ⇒ **O "grupo A" era artefato de agregação em 3 níveis**
(fila → médias por fonte → média do grupo). O FAIL2 da hipótese-kernel fica
**NÃO GASTO e reservado**.
**Decisão nova:** rebaixar o item para **estudo por fonte** — Chu2026 (6 curvas,
1 rig, wear-dominado) no molde do estudo Liu de hoje (reler artigo → anatomia →
formas), + diagnósticos separados Karlsen (1) e Yang (2).
✅ **estudo Chu2026 AUTORIZADO e EXECUTADO (2026-07-28)** — `New_Theory/chu2026_estudo.md`
+ nota de aparato nova (`apparatus_notes/chu2026_triboint.md`). Resultado: a fonte
**segue form-limited, com a forma NOMEADA pela própria fonte** (torque assimétrico
acumulado porca–placa + µ(t) MEDIDO evoluindo, Fig. 5; dois regimes em carga). O µ
implícito nos NOSSOS CSVs confirma a Fig. 5 (test2 sobe 9,3×; 49 kN ≫ 61/73). A
receita "estender o trio PR-38 + procedência (µ_thread 0,05 / passo 1,25 / E 189)"
**morreu nas contas de projeto ANTES do prereg** (test2 piora em todas as variantes:
0,154→0,166/0,183/0,203) — µ subindo arresta o modelo, mas o test2 real perde tudo
(regime 2). Zero preregs gastos; FAIL2 segue reservado. Fica pendente abaixo a
decisão de destravamento. ☐ Karlsen (1) ☐ Yang (2) seguem na fila.

## Chu2026 — FECHADO COM PROVA EM NÍVEL DE LEI (2026-07-28, errata + 2 sondas na mesma noite)

**Errata do estudo (3 erros do mesmo método — contei diretório em vez de perguntar ao
registry, o gotcha do CLAUDE.md):** a nota `chu2026ti.md` JÁ existia (pasta E, registry);
a Fig. 5 JÁ estava digitalizada (2026-07-15, 5 CSVs); e a rota (i) JÁ tinha sido tentada
— prereg **F3.2-CHU** (21/07) prescreveu os schedules medidos e **FALHOU o gate**
(`f3_chu_result.json`; máx. 2 tentativas ⇒ restava 1). A duplicata de nota foi removida.

**As 2 sondas que fecharam a linha (autorização "esses e todos os demais"):**
1. `chu_schedule_isolado.py` — o µ(t) medido, ISOLADO da receita F3: **quase inerte**
   (|Δ|~0,01; G-CHU-a insatisfazível em 3 variantes). Causa = fato de engine: em
   disp-mode o **wear é Archard, sem µ** — o canal de 93 % do Chu é cego ao µ(t) que o
   paper mede. A 2ª tentativa do F3.2 **não foi gasta** (ramo "documenta e fila" do
   próprio prereg, honrado).
2. `chu_energywear_sonda.py` — recolorir a LEI (wear energético `k_E·µ_medido·p·slip`,
   emulação bit-exata): **morre inclusive na âncora** (test4 0,118/0,249 no melhor k_E;
   cegas 0/3).

**Veredicto (3 degraus):** µ-livre não reproduz; µ medido prescrito não muda; lei
µ-acoplada não fecha nem ancorada. ⇒ o resíduo é a **estrutura temporal do kernel de
colapso**; o único candidato restante é o torque acumulado do paper (`M⁻∝N^1,65`,
acumulação explícita no relógio) — ≥3 constantes per-rig em 4 curvas = não-adotável
sob parcimônia. **Recomendação:** test2/3/4/7/8/9 = form-limited com prova → candidatos
a **exceção assinada na próxima ratificação**; reabrir só se outra fonte mostrar a
mesma aceleração N-explícita (test3-like), tornando o canal testável cross-rig.
→ **Formalizado na proposta F6** (`New_Theory/f6_excecoes_propostas.md`, aguarda
sua assinatura): Chu ×6 (§C, prova em nível de lei) + trims-com-prova Yang2019 ×2
(§B) + Yang2023 0,50 mm data-limited (§D). Form-limited genérico (Lu ×10, Karlsen,
Sun grease-std) fica na FILA por doutrina — não vira exceção sem prova além do
genérico. **Ordem recomendada do que resta de forma na fila:** (1º) "resposta
graduada de limiar" consolidada Yang2023-IJPEM+Yang2019-amp0p4 (1+7 curvas, 2
rigs, forma `graded_scrit` JÁ EXISTE default-inerte no engine — falta prereg com
âncora onde o mecanismo é ativo); (2º) âncora interna incubação (2 curvas, forma pequena:
`slip_onset_W` não gateia embedding); (3º) carry-over varamp (bloqueado pelo trim
da small_to_large, F6-§B); (4º) Yang2023 AME jet-nut (1 caso, tripla combinação —
por último). Yang2021: **resolvida pelo S4** (6 trims ratificados §B + 2 exceções
§C da F5) — o item antigo "6/6 violam" está vencido.

## Karlsen + Yang2019 — diagnósticos EXECUTADOS (2026-07-28; `karlsen_yang2019_diagnostico.md`)

1. **Karlsen run14p2**: o modelo acelera a 75 % do que o dado pede (rotacional,
   partial→gross) — gap quantitativo, 1 curva, sem leitor e sem transferência
   possível ⇒ **form-limited documentado, dorme** até 2ª fonte com a mesma assinatura.
2. **Yang2019 amp0p4**: mesmo problema do Yang2023 IJPEM (modelo bifurca onde o dado
   gradua) ⇒ **consolidado** no candidato "resposta graduada de limiar" — agora com
   teste cross-rig possível (M10↔M6/M8, 1+7 curvas).
3. **Yang2019 varamp_large_to_small**: carry-over de história entre blocos = o
   acoplamento damage que o engine TEM desligado; desenho de teste = par de ordens
   opostas (fit numa, zero-refit na outra), **bloqueado** pela decisão de trim da
   `small_to_large` na próxima ratificação.

## Métrica de DIVERGÊNCIA (deriva β do resíduo assinado) — MEDIDA, aguarda seu corte (2026-07-28)

Seu pedido do dia ("o modelo pode estar divergindo e nem sabemos") respondido com
medição: `New_Theory/residual_drift_metric.{py,json,md}`. σ_res (3ª perna) é
permutação-invariante — cega à ORDEM; a deriva β (slope do resíduo assinado vs
posição na curva) mede exatamente "acerta no começo, erra no final". Varredura no
store: **36 das 147 do tripé têm |β|>0,05** (meia tolerância); **4 têm |β|>0,10**
(chu test5 +0,136 · karlsen run7p1 +0,114 · jcsr galv_seawater +0,108 · eccles
fig7d −0,107 — este último o S4 já havia removido por artefato: a métrica pega
automaticamente o que o julgamento humano pegou). corr(|β|,σ)=0,686 = informação
nova. **Implementada como INFORMACIONAL** (regra §4.48a: mudança de gate = prereg
assinado). Decida o degrau:
☐ painel informacional no report (idioma L7, sem gate) — recomendado
☐ 4ª perna com corte 0,10 (meta 147→143 no ato)
☐ 4ª perna com corte 0,05 (meta 147→111 no ato)
☐ só vigilância avulsa (como está)

## Varredura das 3 classes CONCLUÍDA (2026-07-28, pós-S4) — a fila de formas é REAL

**36 dos 39 form-limited são forma mesmo** (resíduo no meio da curva ou em trecho
raso bem-posto) — a hipótese de que parte fosse moldura/métrica caiu quase toda.
Reclassificados (3): `yang2019_M10_amp0p6_5Hz` e `yang2019_M10_varamp_small_to_large`
= **METRIC-limited terminais** (±3% de N vale 0,21/0,26 em r no pico — mesma classe
do Liu; candidatos a trim-com-prova na PRÓXIMA ratificação) · `lu2024_M8_fig20_T22Nm`
= **DATA-limited** (dado termina em 0,112 ≈ FLOOR). Perfis por curva em
`tres_classes_result.json` — insumo direto para os preregs de forma (kernel A/B/C
seguem como o diagnóstico de 2026-07-27 os deixou, com denominador enxuto).

## Adoções por delegação de 2026-07-30 (tarde) — registro, não pendência

- **ZHANG_2018: creep com onset lido do resíduo — ADOTADO** (`C_creep=1.355e-11`,
  `t_0=108,1 s`; preregs `2026-07-30-zhang18-creep-onset{,-r2}`, R1 held-out de
  8 curvas generaliza com zero pioras de σ, R2 gates 4/4; fingerprint
  `3546e6745448`→`b6ed722b1c61`). A fonte fecha **9/9 no tripé**; fila de forma
  26→**23**; tripé estrito **127/202**; resolvida/declarada **164/202**.
  Reverter = restaurar `C_creep=0.0` e remover `t_0` da entry + re-carimbar.
  Detalhe: `zhang18_creep_onset_resultado.md`.
- **Cattaneo-Mindlin (D2′) re-executado com teto único: INCONCLUSIVO** — o
  "mérito" era 100 % artefato de teto (ganho ≡ 0 nas 18; driver de política
  declarada: não adota). Subproduto: cluster de deriva tardia nomeado; LIU_2016
  falsificado para creep compartilhado no premeasure (F1); teto analítico da
  família aditiva varrido na fila (12/26 fecháveis, `fila_teto_log_onset.json`).

## Fronteira da fila pós-adoções de 2026-07-30 (mapa curva-a-curva do que falta)

**Adoção 2 do dia — LIU_2016 (noite): re-atribuição da cauda creep→fretting L1, ADOTADA**
(`flank_wear_on=1`, `flank_amp_exp=1.5` KB, `k_wear_flank=4.325e-14` lido do resíduo;
trim de debris `cfg.trim_n_max={"run2":2.2e6}` — errata de chave na 1ª escrita, ver
resultado; gates 5/5; mos2 intocada Δ=0,0000). Fonte **14/14 no tripé**. Reverter =
remover os 3 campos + o trim e re-carimbar. `liu2016_fretting_resultado.md`.

**Censo pós-adoções: tripé 132/202 · resolvida/declarada 168/202 · fila 19 · fontes-100% 9.**

**CONTABILIDADE TERMINAL (atualizada 2026-07-31, tarde): 202/202 com status provado** —
132 no tripé + **25 exceções** + 12 declaradas + **21 provadas-bloqueadas/julgadas** +
**12 indecidíveis**. A atualização veio do **piso do LU_2024 finalmente MEDIDO**: o par
de réplica publicado que as duas figuras escondiam (fig18_amp0p5 ↔ fig20_T22Nm, mesma
condição 22 N·m/0,5 mm) foi destravado harmonizando o F0 da fig18_amp0p5 ao valor da
Tabela do paper (11567 N; era 12000 nominal — pior proveniência E impedia a chave de
pareamento). Piso: σ 0,0912 · MAE 0,1071 · mx 0,2334 (o FLOORS legado dizia 0,093 —
corroborado). Efeito: T22Nm assinada F7-FORTE; amp0p25/T4Nm julgadas (modelo ≈/pior
que o piso do dado em MAE); 3 indecidíveis a menos SEM bancada. ⚠️ O gargalo
rebalanceou: perna que manda σ 28 · MAE 16 · mx 26 — o res.máx voltou ao jogo.
LIÇÃO DE MÉTODO: antes de pedir réplica à bancada, procure a réplica que o paper
já publicou em figuras diferentes — a chave de pareamento (fonte, δ, F_amp, modo)
só a acha se os INPUTS estiverem harmonizados. O mandato "fechar ou provar cada
uma" segue satisfeito; cada item abaixo diz qual porta o destrava:

- **CHU_2026 ×6** — **TODAS as classes de mecanismo existentes medidas e fechadas**
  (2026-07-31, `chu_veredicto_completo.md`): 3 F1 (aditivo, troca de kernel, dreno
  composto) + teto cinemático INERTE + ratchet PIORA + **máquina de dano compartilhada:
  move CERTO (test2 sd 0,19→0,11, fim 0,16 vs dado 0,14 — o regime que faltava APARECE)
  mas nenhuma dose única é viável em 54 pontos** (o relógio de dano é monótono na
  amplitude; o dado não é). A parada da classe DISPARA para candidatos existentes.
  Destrava: **Ra por espécime** (k_dmg vira input por classe de superfície) OU **1 réplica
  em D0.4 e D0.5** (decide regime vs scatter) OU forma nova não-monótona (PR-3 — ex.:
  third-body ejection em amplitude alta). Achado estrutural: a chave `CHU_2026_test1`
  só casa o test1 — as outras 8 rodam SEM dano (c_D=0).
- **LIU_2025 ×4** — defeito P5 do limiar N₉₅ (dispara 10–100× cedo em amplitude baixa);
  é forma de limiar emergente, não constante. **DUAS classes medidas e falsificadas**
  (2026-07-31): canal aditivo F1 E dose compartilhada de incubação F1 (grade 12 pontos,
  `liu2025_onset_grid_probe.json`: W<250k quebra as médias/altas, W≥400k quebra
  amp0p8+fig2, fecha 0/4 em toda parte — coerente com o P5: o limiar é EMERGENTE).
  Achado de estrutura: a config já carrega duas doses por chave (250k / 400k nas chaves
  amp0p4/amp0p5) — o adotado é um ótimo local à mão; destrava só com forma nova (PR-3).
- **LIU_2022_RETIGHT ×3** — sinais do resíduo TROCAM ao longo da cadeia (t1/t2 −0,07..−0,09
  vs t4 +0,085): defeito do transporte de estado entre estágios (renovação/dano por
  reaperto); n=7–11 por curva — ler 2 parâmetros disso seria sobreajuste sem mais dado.
  E a âncora candidata (fig3 do liu2016, 12 reapertos sem vibração → `k_emb_renew`)
  empurra na direção ERRADA para t1/t2: renovar mais = mais perda cedo, e o modelo já
  perde demais lá (verificado na aritmética do `retighten()`).
- **LI_2022_TRIBOINT ×2** — curvatura com sinais opostos entre as 2 curvas (cluster
  "duas formas"); candidato rampa+curvatura é trabalho de forma, não constante.
- **YANG_2021 ×2** — AUDITADA (2026-07-30 noite, `fila_auditoria_inputs_resultado.md`):
  gap de representação REAL (axial senoidal documentado 2/8 kN é descartado pelo
  `theta=π/2` fixo) mas INERTE (sonda bit-idêntica: nenhum mecanismo ativo lê F_ax);
  canal aditivo F_ax = F1; rota de fadiga = PIORA (sessão anterior). O defeito é a
  FORMA da competição afrouxamento-fadiga (ξ) — precisa de forma nova (PR-3).
- **SUN_2025_CRIMP ×1 · CACCESE_2009 ×1** — 1 curva cada, sem réplica que ancore leitura
  per-par; qualquer knob viraria fit de curva única. AUDITADAS: sun2025 freq 12,5 Hz é
  documentada (não é o erro do default; o axial 25 Hz combinado é invisível e inerte,
  mesma medição do yang2021); caccese rep2 é creep estático (sem input dinâmico) e a
  exceção da rep1 (MAE/piso) não cobre a perna σ da rep2.
- **11 indecidíveis** (era 15; atualizado 2026-07-31 tarde) — a varredura de RÉPLICAS
  PUBLICADAS fechou: LU_2024 destravada (par entre figuras, piso medido);
  `zhang2006_fig3_illus` DECLARADA por proveniência (o paper rotula a figura
  "Illustration" — rig do paper anterior, end-hook desenhado;
  `apparatus_notes/zhang2006.md`); companion OA do YANG_2023_IJPEM NÃO tem curvas
  preload-vs-ciclos (verificado no PMC: só D-N e vida prevista-vs-medida; "each
  experiment was repeated twice", sem curvas plotadas). **Duas medições para VOCÊ:**
  · **âncora interna 13A first/def como réplica?** F0 3 % distinto (120039 vs 116498), mesmo
    parafuso/amplitude/freq. Piso do par (informacional, janela comum): **MAE 0,0345 ·
    mx 0,0635 · σ 0,0259**. Se aceitar: as 3 âncora interna saem de indecidível para JULGADAS — e
    o modelo erra ACIMA do scatter do par em MAE nas três (0,052/0,096/0,052).
  · **YANG_2023_AME = junta CFRP** (M20 em compósito; `yang2023ame.md`): MAE 0,39 é o
    modelo sem canal de relaxação viscoelástica de matriz — fronteira de ESCOPO
    MATERIAL; declarar exige sua assinatura (é claim sobre o escopo, não sobre o dado).
  Restam sem rota publicada: YANG_2019 (4; amp0p6 5 Hz vs 10 Hz são condições
  distintas) e YANG_2023_IJPEM (3; paywall + companion sem curvas).

## Observações de fronteira (sem ação requerida)

- ✅ **RIDER EXECUTADO (2026-07-28, mesmo dia):** trim da `amp0p8` removido no
  re-stamp `294808504d83` — gates 3/3 (amp0p8 0,0487→**0,0381**, demais idênticas
  ao dígito). §B recontado (15 trims, LIU ×6). Item encerrado. *(registro original:)* *"remova o trim da amp0p8 no próximo
  re-stamp"*. NÃO editar o config antes do re-stamp (dessincroniza o hash do
  fingerprint carimbado). **Receita executável, para quem fizer o próximo
  re-stamp** (qualquer sessão):
  1. deletar a chave `sources.LIU_2025.cfg.trim_n_max.amp0p8` (valor atual 11500)
     em `New_Theory/adopted_configs.json` — só ela; os outros 6 trims FICAM;
  2. re-sim completa + re-carimbo do `exemplo_m12_sintetico` à parte (re-sim
     direta via runner — `--cases` não o alcança, medido);
  3. gates: `amp0p8` esperada em **0,0381/0,0853** (medido 2026-07-28 sob
     `9ac44acd03de`; PASSA, MAE melhor que o pós-trim 0,0487); nenhuma outra
     curva muda; fingerprint novo ÚNICO;
  4. atualizar a contagem do §B de `f5_excecoes_propostas.md` (16→15 trims;
     LIU_2025 ×7→×6) e a linha correspondente da tabela "o que cada trim custa".
  As outras 6 seguem necessárias (medido: MAE 0,08–0,19 sem trim; moldura do
  dado + front-loading do relógio Miner+Goodman).

- **Explorador/galeria STALE pós-adoção E2 (2026-07-28)**: a galeria do
  `variable_explorer` lê o store canônico, que foi re-carimbado (`9ac44acd03de`) e agora
  tem as 7 curvas LIU_2025 terminando em fratura. O re-render é do fluxo do Manual/S6
  (sessão que o mantém) — não regenerado daqui para evitar corrida de árvore; o
  `validation_html/` JÁ foi regenerado (205 páginas, no commit da adoção). Dois VarSpecs
  novos (`fat_ramp_D_on`/`fat_ramp_q`) também aguardam esse re-render.

- **Sinal do acoplamento dano→atrito é por-par** (Sun2025 reassy, PR-28): Ag₂O
  de remontagens SOBE µ e MELHORA retenção (anti-loosening ↑, vida à fadiga ↓)
  — contra-exemplo ao `k_dmg_mu` (µ cai com D) calibrado no rig âncora interna aço-aço.
  Generalizar `k_dmg_mu` exigirá sinal por par tribológico.

## Observações

- Itens saem daqui quando você responder no chat (ex.: "autorizado item 1").
- A campanha segue nos alvos knob/condição-alcançáveis enquanto isso.

---

## 2026-08-13 (noite) — desfecho da campanha CHU_2026: B e D executados; nova decisão na mesa

**Execução dos assinados B/D (mesmo dia da assinatura):** paper lido na íntegra
(prereg `2026-08-13-chu2026-calibracao-prereg.md`); 3 rodadas de grade declarada
+ a rodada 1 = **4 famílias falsificadas** (k_wear uniforme · running-in ·
ratchet · incubação×chute-tardio), todas com gates congelados e dose-resposta
publicada. Capacidade POR CURVA provada (test3 fecha com `slip_onset_W=4000`;
test5 com `W=1500+k_late=2` a 0,0100 de MAE) — e os ótimos são **disjuntos por
10×** dentro da fonte: onset/chute são função de (D, F₀), a lei M⁻ do próprio
paper, que **não tem eixo de amplitude** (fitada só em D=1 mm). Detalhe:
`chu2026_estudo.md` §8.

- **B (rugosidade)**: corrigir sem recalibração que recupere = censo 3→1 —
  **bloqueado pelos gates** (G2/G3). Fica dívida declarada com número; os
  inputs de artigo (mu_thread 0,06 · test9 emb 9,5 µm · rz) vivem no prereg,
  medidos ~neutros (|Δ|máx 0,0015) a agressivos (rz grupo-wide), adoção isolada
  só mexeria fingerprint (regra do estudo §5).
- **D (calibração em grupo)**: executado como assinado (grupo/condição, zero
  per_case fitado) — e o resultado é a falsificação acima, não uma adoção.

### 🆕 NA MESA: exceção assinada para CHU_2026 test2/3/4/7/8/9 (classe form-limited com prova em nível de lei)

Dossiê: prova em 3 degraus (2026-07-28, µ-livre/µ-prescrito/lei-recolorida) +
4 famílias pós-estudo falsificadas (2026-08-13) + demonstração de que a lei do
próprio autor não fecharia a varredura de D. Teto da fonte sob formas atuais:
**3/9** (test1+test5+test6, todos no tripé). As 6 são candidatas à classe do
artigo de exceções (pedido do professor 2026-08-07). **Proposta AGUARDA
assinatura** — item novo, posterior à assinatura em bloco de 19:00; exceção é
recurso do professor, não da sessão. Reabertura automática se outra fonte
exibir a assinatura N-explícita (test3-like) que torne o canal de acumulação
testável cross-rig (condição já registrada no estudo §7).

---

## 2026-08-13 (22:0x) — pacote LU_2024 dado-only ADOTADO; 1 proposta F7 nova na mesa

Prereg `2026-08-13-lu2024-pacote-dado-ajuste-prereg.md` executado no ramo
dado-only (re-fit medido: constantes ficam por CENTRALIDADE — censo do LU é
plano; grade completa no prereg). 7 CSVs fig18/fig20 corrigidas pelo
instrumento validado (G1 20/20, c1 exato da tabela nas 7), 13 re-sims,
fingerprint intocado, pisos honestos (`limite_sres(LU)` 0,1030→0,1361), 5
provas F7 re-numeradas SEM retratação, guards 32/32, saldo 0 como declarado.

### 🆕 NA MESA: F7 FORTE para `lu2024_M8_fig14_amp0p5_long`

Com o dado corrigido e o piso do par 0,5 mm re-medido (MAE 0,2630 · mx 0,5779
· σ 0,1768): a curva mede **0,1257 ≤ 0,1860** (FORTE) · **0,3936 ≤ 0,4086**
(FORTE) · σ **0,1235 já dentro** do limite da fonte (0,1361) — todas as pernas
violadas cobertas pela barra FORTE. Proposta AGUARDA assinatura (exceção é
recurso do professor). Contexto: a irmã `fig14_amp1p0_long` NÃO qualifica —
mx 0,8553 excede o piso do par (0,8498) por **0,6 %**, e a regra "todas as
pernas cobertas" já retratou casos por margens menores; ela fica como a
ÚLTIMA curva form-limited do projeto, honestamente declarada.

**Atualização 2026-08-14 (rodada 4):** a proposta de exceção CHU ×6 ganha o
**capstone** — a lei M⁻ do próprio autor, alimentada com o µ(N) medido do
próprio ensaio, **inverte a ordenação** das vidas publicadas (F₀^1,85 vence
T_res∝F₀ ⇒ preload alto afrouxaria antes — o contrário do dado), erra razões
por até 4,65× e viola o limiar D_cr do test1. Prova agora em **5 degraus**
(prereg §rodada-4 + estudo §9). Subproduto de interesse para o artigo: a
sonda demonstra QUANTITATIVAMENTE a tese que o paper só enuncia — a proteção
do F₀ é mediada pela evolução do µ, que a lei FEM (µ fixo) não carrega.

---

## 2026-08-14 (manhã) — "assine e continue em loop": executado com uma inversão que o rigor impôs

O mandato chegou 1 minuto depois de `9784148` (retirada da F8: os pares
fig14×fig18/20 do LU **não são réplicas**). Fui à fonte primária antes de
assinar: o PRÓPRIO PAPER separa os protocolos (corridas longas = §3.1.3,
half-sine de MÁQUINA a 1 Hz, F₀ 12.398/12.285/12.696 N; Fig.18/20 = §3.2,
controle MANUAL que "elimina os efeitos da half-sine") — e a direção bate com
o achado de frequência do §3.1.2. Consequências executadas:

1. **ASSINADA (delegação): CHU_2026 ×6** em `_F5_EXCECOES` — form-limited com
   prova em lei de **5 degraus** (dossiê no prereg + estudo §7–9). CHU: 9/9
   com estatuto (3 tripé + 6 exceção).
2. **RETIRADA a minha proposta F7 da `fig14_amp0p5_long`** (ontem 22:0x) —
   fundava-se no par inválido. Nunca assinada; morre como proposta.
3. **RETRATADAS as 5 F7 do LU** (`_EXCECOES_RETRATADAS_LU_PROTOCOLO`) — 4ª
   invalidação de pareamento, a maior. Pares removidos de
   `_PARES_REPLICA_DECLARADOS`; as 3 `fig14_*_long` bloqueadas em
   `_SEM_FAMILIA_MECANICA`; declaração da `amp0p25_long` removida (base era o
   mesmo par). T22 fica a 4 % do limite de MAE por mérito — a menos exposta.
4. **Cascata medida e publicada:** o piso do LU volta ao global (o par
   T22↔fig18_amp1p0 é digitalização, < global) ⇒ `fig18_amp1p5` (σ 0,0353 >
   0,025) **sai do tripé**: censo estrito **147→146**; fora 59 = 32 estatuto
   + 27 abertas; resolvida/declarada **178/205**; perna-que-manda σ 39 · mx
   13 · MAE 7 (o limite σ do LU caiu 5,4× e 6 curvas trocaram de perna).
   Export do artigo: 22 exceções (20 F5 + 2 F7). Guards 41/41; fingerprint
   e store INTOCADOS (mudança é de estatuto/pareamento, camada de report).

**Rotas de reabertura honestas do LU:** réplicas no MESMO protocolo (dado
novo), ou µ/OEM do §3.1.3 que permita julgar as longas como fonte própria.

### 🆕 NA MESA (2026-08-14, pós-triagem): o estatuto das 8 órfãs de protocolo do LU_2024

Com a retratação, a fila "form-limited" inteira do projeto = **8 curvas, todas
LU_2024** (T10/T16/T22/T28/fig18_amp0p5/amp1p5 + as 2 `fig14_*_long`), σ
pedindo −68 a −91% contra o limite global. **Não há rota**: (a) modelo — a
grade pré-registrada de 2026-08-13 mediu o censo do LU PLANO em toda a região
de alavancas, e a sonda de sensibilidade (18 alavancas) já não fechava σ;
(b) piso — o paper não tem réplicas no mesmo protocolo; (c) dado novo — fonte
fechada. Três instrumentos independentes identificaram a classe (grade plana +
27–56× entre protocolos + o modelo separando fig14 de fig18/20 — sessão
paralela, `42e84e1`). Decisões possíveis, todas suas: (i) declarar a classe
"órfã de protocolo" (novo tipo de declarada); (ii) deixá-las abertas como
estão (146/205 estrito, 178 resolvida/declarada); (iii) assinar a regra de
parada (`regra_de_parada_proposta.md`) — sob ela, a camada 3 hoje APROVARIA
parar por classe (requisitos a/b/c medidos). A T22 (MAE 0,0520, a 4% do
limite) é a única com chance de mérito futuro se algum re-fit legítimo de
outra fonte respingar — não há hoje.

---

## 2026-08-14 (tarde) — G e H EXECUTADOS por delegação; censo honesto 140/205

Sob "assine e continue em loop" e a regra com 4 precedentes ("validade do par
vem antes do número"), executei a recomendação do próprio audit
(`icmez_chave_cega_ao_grip.md`, sessão paralela — crédito dela; o passo 3,
estender a guarda, ela já havia feito):

- **G**: os 8 casos do ICMEZ_2025 bloqueados em `_SEM_FAMILIA_MECANICA` (as 4
  famílias pareavam grip 13,8×19,8 mm; MAE de piso 0,105–0,209 = diferença de
  rigidez, não repetibilidade). Censo −5; **3 das 8 ficam por mérito**.
- **H**: `chu…test9` bloqueado (a família δ=0,5 pareava Ra 1,6×0,4 via config
  default; a média inflava o limite da fonte de 0,0296→0,0507 e o `test5` da
  família LEGÍTIMA passava por causa da ilegítima). Censo −1 (test5 sai;
  test6 fica). ⚠️ A causa-raiz é a dívida de INPUT do item B — segue na mesa:
  aplicar o rz do artigo resolveria a cegueira da chave na raiz, ao custo
  medido de −2 adicionais (test5/6 pioram metricamente sem recalibração, e a
  recalibração foi falsificada em 4 famílias).

**Censo estrito 146→140/205 (68 %) · resolvida/declarada 172/205 · perna que
manda σ 48 · mx 10 · MAE 7 · fontes 100 % = 11.** Guards 37/37 (a lista
declarada da guarda nova foi atualizada com o motivo, como ela pede). Fica na
mesa: **F** (órfãs LU), **B/H-raiz** (input Ra do CHU), regra de parada, e a
decisão de leitura (o censo caiu 8 pontos em um dia POR HONESTIDADE — 6 hoje
+ 2 de ontem — sem o modelo piorar em nada; os documentos dizem isso
explicitamente).

---

## ✍️ ASSINATURA EM BLOCO — professor, 2026-08-14 22:34 ("continue o loop, eu assino tudo")

Registrada por esta sessão (B), com divisão de posse pela regra de 1 escritor:

- **B/H-raiz (input Ra do CHU) — EXECUTADO por esta sessão** (era item meu de
  origem): sandbox mediu ANTES de aplicar — **test1/test5/test6 bit-idênticos**
  (emb pinado nos grupos próprios protege o tripé por construção; o custo "−2"
  tabelado estava morto desde a adoção do test5). `SOURCE_INPUTS[CHU_2026]`
  rz="Rz<4" + grupo mínimo `CHU_2026` (per_case test9 emb_um=9,5, regra D-AB).
  Excetadas movem com estatuto imune (test3 até melhora −0,058; test4 +0,031);
  censo intacto; a chave mecânica passa a separar test9↔test3 NA RAIZ (o
  bloqueio H vira redundância inofensiva). Re-stamp completo em execução;
  auditoria de deriva (esperada: exatamente as 6 excetadas do CHU) no commit.
- **Regra de parada — critério (c) FECHADO** (ver
  `regra_de_parada_proposta.md` §fecho): achado a95efcc adotado; 69 % rejeitado
  como re-derivação; saída (1) materializada pelo item F; camadas 1–3
  cumpridas; (c) preservado para fila futura ≥2 fontes.
- **K · L · M · censo-conta-curvas · classe artigo×store (53/210) — ASSINADOS
  PARA O PROPONENTE executar** (sessão paralela): propostas dela, medições
  dela, 1 escritor por recurso. Esta linha é o registro de que a assinatura
  de 22:34 os cobre; a execução é dela na próxima janela.

---

## 2026-08-15 (12:4x) — "continue o loop, eu assino tudo" (2ª renovação): coluna do TETO no export EXECUTADA

A oferta de 12:0x foi executada sob a renovação: o export do artigo ganha a
coluna **teto p/curva** (cota inferior do MAE com constantes per-case, sonda
`excecoes_teto_por_curva.md`; NADA adotado). Leitura: **14 no teto**
(form/data-limited — nenhuma alavanca move, nem per-curve) · **8 transfer**
(CHU ×6 até −76 %; YANG ×2). CSV ganha `teto_mae_per_curve`/`teto_classe`;
README explica a semântica; resultado bruto persistido em
`New_Theory/excecoes_teto_result.json`. Itens da sessão paralela (retratação
das 2 exceções; s1_amp_gate LIU_2025 preregado) seguem com ela.

---

## 2026-08-15 (14:4x) — prereg s1_amp_gate EXECUTADO E ADOTADO por delegação: censo 141→143

O prereg `2026-08-15-liu2025-gate-amplitude` (990b9dd, **autora: sessão
paralela** — crédito integral do desenho, gates e predições) foi executado por
esta sessão sob "continue o loop, eu assino tudo": grade 15+10 células
(floor=0 decidiu pela regra de parcimônia do próprio prereg; predição-4
"floor>0 vencerá" FALSIFICADA), fronteira fechada por D-L (extensão p→8,
dref→0,25), vencedora por CENTRALIDADE **4/4 vizinhos**: `dref=0,30 mm ·
p=4 · floor=0` (2 números, fitados sem âncora — declarado; a âncora
stick/slip foi falsificada no prereg §3). Gates: fecham **amp0p25+amp0p3**;
inclinação ρ 0,989→0,909, slope 0,178→0,107 (G5 ✓); zero pioras (amp0p8
+0,0012 ≤ +0,010); protegidas melhoram todas; G1 isolamento exato; G8 re-stamp
`20be19aabe11` uniforme ×210, deriva SÓ nas 7 LIU. **Censo 143/205 ·
resolvida/declarada 183/205.** Guards 32/32; docs sincronizados.

---

## 🆕 NA MESA (2026-08-15, noite) — item Q: as 5 abertas do `ICMEZ_2025` são FORM-LIMITED, não indecidíveis; e a regra do piso de arresto

Dossiê: `icmez_arresto_sub_piso_resultado.md` (26 células, 6 famílias, todas
falsificadas; sondas só-leitura, nada adotado; censo intacto em 143/205).

**O achado.** O modelo **trava em ~0,29** (o `loose_arrest_floor` = 0,308
adotado no PR-13 como `fitado-this-rig`) enquanto o dado atravessa o piso e
segue caindo até **0,223**. Medido **no sítio**: `self_locking_gate → 0,0000`
no último quarto do ensaio nas curvas cujo dado passa abaixo do piso; taxa
tardia do modelo **0,18–0,26** da sua taxa de meio contra **0,48–0,57** do dado
— separação perfeita entre as 4 curvas que cruzam o piso e as 4 que não cruzam.
O dado é limpo (σ_res é **6–15× o ruído** do próprio dado, monotonia exata) ⇒
não é *data-limited*.

**A forma que falta, nomeada:** afrouxamento **sustentado sub-arresto** — o
canal rotacional do engine é binário (arresta no piso **ou** entra em runaway
com piso 0); esta fonte exige o meio-termo. Baixar o piso sem a forma **piora
tudo** (0/8, MAE ×5).

**Decisões possíveis (suas):**
1. **Reclassificar** as 5 de `indecidivel_sem_piso` para **form-limited com
   forma nomeada** — muda a leitura da fila (0 → 5), não muda o censo. É a
   descrição honesta: o bloqueio é do MODELO, não do nosso dado.
2. **Construir a forma** (default-inerte + prereg + gates) — trabalho de
   engine, não de constante; o dossiê já entrega o alvo quantitativo (taxa
   tardia ≈ 0,5 × taxa de meio abaixo do limiar).
3. **Regra nova sugerida pelo audit campanha-wide** (§7 do dossiê): *piso de
   arresto só é legítimo se o dado da própria curva PLATEAR nele*. Auditadas as
   15 curvas cujo dado passa abaixo do piso aplicado: **14 por ≤ 0,005**, todas
   com piso **lido do dado** (leitor L24) e platô real — o audit **valida o
   leitor**; a exceção é o ICMEZ, único piso **fitado**, 0,009–0,085 acima de um
   dado que não plateia.

---

## 🆕 NA MESA (2026-08-15, noite) — item R: `ROUSSEAU_2025` ×4 é transfer-limited, e a lei de taxa do canal ROTACIONAL é a lacuna que resta

Dossiê: `rousseau_ratchet_transferencia_resultado.md` (10 células, nada
adotado, censo intacto).

**O achado.** As 4 abertas são exatamente as **4 rotacional-dominadas**
(72–83 % do canal) com viés positivo e `|viés|/MAE` 0,90–1,00 (falta perda, no
canal rotacional); as 3 em **stick** passam. `k_ratchet` melhora a `steel_t10`
em **63 %** e destrói as outras três **na menor dose** — porque os slips do
mesmo rig diferem **10×** (0,03 vs 0,44 mm) enquanto o déficit é comparável.
Ótimos disjuntos ⇒ **constante não transfere dentro da fonte** (mesma estrutura
do `CHU_2026`).

⚠️ **Gotcha de engine descoberto no caminho** (§3 do dossiê, vale para toda a
campanha): `loose_amp_exp < 1` **amplifica** em vez de comprimir quando os
slips do rig estão abaixo de `LOOSE_AMP_REF` (0,5 mm) — fator 7,1× num slip de
0,03 mm. O parâmetro faz o oposto da intenção de projeto fora da janela da
referência. **Sugiro promover ao `CLAUDE.md`** (não editei: o arquivo estava
sob edição da sessão paralela).

**A síntese que o item Q e este formam:** ICMEZ (arresta onde o dado atravessa)
e ROUSSEAU (rotação-por-slip 10× dentro do rig) apontam **o mesmo canal**. A
**lei de taxa do canal rotacional** é a lacuna estrutural restante — ele sabe
arrestar ou colapsar, e escala o slip por uma referência fixa. **9 das 21
curvas abertas (43 %)** estão nessas duas classes; nenhuma é *data-limited*
(σ_res é 4,7–15× o ruído do próprio dado nas nove).

**Decisão sua:** (i) reclassificar as 9 como form-limited com forma nomeada
(a fila deixa de ser "0" e passa a dizer a verdade); (ii) autorizar o desenho
da lei de taxa (engine, default-inerte, prereg + gates); (iii) só registrar.

---

## ✍️ ASSINATURA EM BLOCO — professor, 2026-08-15 19:57 ("assine tudo e continue em loop")

Registrada pela sessão B, com **divisão de posse** (1 escritor por recurso) e
uma decisão de método que precisa ficar explícita:

- **Q (ICMEZ) e R (ROUSSEAU) — ASSINADOS na opção (ii), NÃO como exceção.**
  Exceção existe para curva **sem rota**; estas têm a forma **nomeada e
  construível**. Assinar as 9 como exceção converteria curvas abertas em
  "resolvidas" **sem o modelo melhorar** — inflar o resolvido com fracasso, que
  o próprio `classificar` da triagem proíbe em comentário. Assinado, portanto,
  o **desenho da lei de taxa rotacional**: prereg
  `2026-08-15-lei-de-taxa-rotacional-prereg.md`, gates G0–G8 congelados,
  2 campos default-inertes (`loose_arrest_residual`, `loose_amp_ref`).
  ⚠️ Predição registrada: as 2 curvas de grip 19,8 **não** fecham (não são
  bloqueadas por arresto) — se fecharem, é erro de campo.
- **N′ e P — ASSINADOS para a sessão A executar** (são dela: medição, formato
  P-7 e a guarda de entradas inertes). Registro aqui só a assinatura.
- **D — sem objeto** (premissa vencida e já registrada como tal em 08-15).
- **E — ASSINADO na parte que tem prova**: a classe *sub-slip* já recebeu
  assinatura em `9f660c5` (yang2023 0,25 mm). As 3 abertas do `YANG_2021` só
  entram na mesma classe **depois** de medida a classe mecânica delas (não
  medida ainda) — fica na fila com esse critério escrito, não assinada no
  escuro.

**Ordem do classificador (achado da sessão A, `85eaf93`):**
`indecidivel_sem_piso` **precede** `form_limited`, logo curva de fonte sem piso
nunca recebe o rótulo mesmo com defeito diagnosticado — é por isso que a fila
publica 0 com 9 curvas diagnosticadas. O conserto é dela; meu prereg depende
dele só para a LEITURA, não para a medição.

---

## 2026-08-15 (noite) — item Q EXECUTADO na opção (ii): forma construída, mecanismo validado, adoção FALSIFICADA pelos próprios gates

Prereg `2026-08-15-lei-de-taxa-rotacional` executado ponta a ponta (§RESULTADO).

- **`loose_arrest_residual` está no engine, default-inerte** (G0: |Δ| = 0,000e+00
  em 6 fontes distintas), com contrato preso por **5 testes**
  (`test_loose_arrest_residual.py`) — padrão do `gth`.
- **Mecanismo VALIDADO (G5):** a taxa tardia das 3 alvo sobe de **0,20 → 0,47**
  da taxa de meio, entrando na banda do dado (0,48–0,57), que a versão binária
  arresto/runaway nunca alcançava.
- **Adoção NÃO tomada:** com o residual sozinho nenhuma curva fecha (σ mínimo
  0,029 vs 0,025) — o arresto era **um** defeito, não o único. O par que fecha
  3 (`residual=0,30 + emb_um=8`) **quebra 2 protegidas** (G3), piora 3 curvas
  acima da tolerância (G2) e usa 2 números, um deles **input com procedência
  VDI** (G7). Censo **inalterado em 143/205**.

### 🆕 O 3º diagnóstico, que só o trade revelou: a dependência de GRIP

O `emb_um=8` acerta os **grip 13,8** e erra os **grip 19,8** — as 2 que quebram
são as de grip grosso. Como embedding depende, pela VDI, de **rugosidade e nº
de interfaces** e **não** de comprimento de aperto, um `emb_um` per-grip seria
**anti-físico**. ⇒ o que a medição diz é que a **escala de rigidez com o grip**
(`c_bend` → `k_tr`) está errada nesta fonte, e o `emb_um` vinha compensando-a.
Esse é o alvo real e é de **forma**, não de constante — e é a 3ª peça da mesma
lacuna (itens Q e R): a lei de taxa do canal rotacional e a sua dependência de
geometria.

**⚠️ ERRATA do item Q (2026-08-15, 21:1x — minha):** o "3º diagnóstico" que eu
publiquei (*"a escala de rigidez com o grip está errada"*) **caiu no primeiro
teste**: o `k_tr` do modelo segue a lei de viga **ao dígito** (2,954 =
(19,8/13,8)³) e a sensibilidade ao grip bate com o dado a 1–20 % **sem sinal
consistente**. A causa real da assimetria é **regime de slip**: `slip/δ` =
0,69–0,81 nos grip 13,8 (gross) contra 0,08–0,44 nos 19,8 (parcial). Alavanca
de nível move as parciais através da fronteira de regime e quase não move as de
gross. ⇒ a rota que sobra é uma forma **gateada pelo regime** (a maquinaria CM
já existe), não constante compartilhada — 53 células medidas nesta fonte.

---

## 2026-08-15 (noite) — item E MEDIDO (o critério que eu mesmo pus): YANG_2021 é 100 % stick, e a desculpa de scatter da `r1` NÃO se sustenta

Dossiê: `yang2021_stick_sustentado_resultado.md`.

- **8 de 8 curvas em STICK** (slip = 0 em 100 % dos ciclos); canais vivos
  embedding+creep. As 3 abertas têm a **mesma assinatura** das 2 já assinadas
  (resíduo crescendo até +0,045/+0,074/+0,082 no fim). Dado limpo (8–17× o ruído).
- **Rota medida, e ela TROCA:** a forma de stick (`gth`) já está adotada aqui;
  em `gth_k=5e-7` fecham 2 abertas e **quebram 2 protegidas** — net zero (6 células).
- ⚠️ **A desculpa fácil foi testada e RECUSADA:** a `r1` falha só o σ por 7 % e
  tem 2 réplicas irmãs. Medido dado×dado: as réplicas discordam entre si com
  σ **0,0129** e **0,0099**, e o modelo está em **0,0268** — **2,1× FORA**. Não é
  scatter-bound; o erro de forma é real.
- **NÃO assinadas como exceção** (mesmo critério de Q e R: exceção é para curva
  sem rota). Censo inalterado, 143/205.

**Síntese de TRÊS fontes** (ICMEZ ×5, ROUSSEAU ×4, YANG_2021 ×3): em todas a
forma **existe** e **uma constante compartilhada não serve à própria fonte** —
regimes de slip diferentes, rotação-por-slip 10×, réplicas da mesma condição.
O alvo é a **lei de taxa** (como o mecanismo escala), não a magnitude.

---

## ✍️ ASSINATURA 2026-08-15 23:27 ("assine e continue") — item Q FECHADO e a 2ª linha completada por simetria

**Q estava executado nas duas opções** e o registro faltava: (ii) a forma foi
construída por mim (`loose_arrest_residual`, default-inerte, 5 testes,
mecanismo validado, adoção falsificada pelos gates — `5702281`); (i) as 5 do
ICMEZ entraram em `_FORMA_NOMEADA` pela sessão A. **Q fecha.**

**Completada a simetria que faltava:** as **4 abertas do `ROUSSEAU_2025`**
entram em `_FORMA_NOMEADA` pela **mesma barra** das outras duas fontes —
regime (as 4 rotacional-dominadas 72–83 %; as 3 em stick passam) · canais
(rotacional 72–83 %, wear ~0) · forma (viés positivo, `|viés|/MAE` 0,90–1,00,
déficit **cresce com o slip**) · dado limpo (σ 4,7–14× o ruído) · **rota já
descartada** (10 células; ótimos disjuntos porque os slips diferem 10× no mesmo
rig; o expoente não resolve porque `LOOSE_AMP_REF`=0,5 mm está acima de todos
os slips ⇒ exp<1 amplifica). **2ª linha: 8 → 12 de 21 abertas.**

⛔ **As 3 do `YANG_2023` ficam FORA por medição** (`yang2023_e_a_lei_do_sinal`):
três regimes (13 % · 68 % · 0 % de stick) e três **sinais** de resíduo
distintos — não formam classe, e entrar seria rotular sem prova.

⚠️ **Defeito consertado de passagem** (não é meu, mas bloqueava a ferramenta):
`regra_de_parada_triagem.py` **crashava no fim** (`UnicodeEncodeError` no `⇒`
de um `print`, console cp1252 — o gotcha que o `CLAUDE.md` já documenta). 8
linhas de `print` normalizadas para ASCII, **zero mudança de semântica**; a
saída completa voltou. Censo **inalterado: 143/205**.

---

### NA MESA (2026-08-20, 16:5x): a `classe_parada` esconde **1 falso positivo**, e ele é a fila form-limited inteira

**Prereg com gates congelados:** `docs/superpowers/specs/2026-08-20-classe-parada-curva-a-curva-prereg.md`

Medido contra o store **`4d1211958122`** (uniforme, 210, zero divergentes) com o
discriminante **já assinado** `classe_parada_discriminante.py` — o mesmo instrumento
da P-7:

| curva | viés 1/3 | viés 1/4 | veredicto |
|---|---:|---:|---|
| `liu2025_M16_amp0p8` | **−0,0192** | **−0,0192** | **ESPELHADO (desabou cedo)** |
| `liu2025_M16_fig2_single` | +0,0542 | +0,0562 | classe (retém demais) |
| `yang2021_amp0p5mm_ax8kN` | +0,0703 | +0,0703 | classe |
| `yang2021_amp0p6mm_ax8kN_r1` | +0,0347 | +0,0347 | classe |
| `yang2021_amp1p0mm_ax2kN` | +0,0632 | +0,0632 | classe |

`LIU_2025` **MISTA** (1+1) · `YANG_2021` **COERENTE** (3/3) · sinal estável nas duas
janelas ⇒ ninguém é `AMBIGUO`.

A `amp0p8` carrega o defeito **espelhado**: o modelo está ABAIXO do dado no fim, então
o remédio da classe (*acelerar mais*) a **piora**. Mesma assinatura que tirou
`LU_2024`/`SUN_2025_CRIMP` (P-7) e `YANG_2019` (N-linha).

**O precedente não resolve sozinho:** aquelas eram falsos positivos PUROS e a opção
mínima remove a FONTE; aqui remover `LIU_2025` levaria a `fig2_single`, que é genuína.
O caso pede a **opção 2 da P-7 (curva a curva)**, que o próprio classificador registra
como não executada *"porque obriga a re-derivar o critério (c)"*.

> ⛔ **CORREÇÃO 2026-08-20 (21:5x) — esse bloqueio NÃO EXISTE, e o erro foi meu.**
> Escrevi *"bloqueado pelo critério (c)"* lendo um **comentário de código** em vez de
> conferir se o bloqueio estava vivo. O **critério (c) foi FECHADO em 2026-08-14**
> (`regra_de_parada_proposta.md` §FECHO, achado `a95efcc`): ele *"não era avaliável"*,
> a re-derivação **"69 %/3 = 23 %" está explicitamente rejeitada**, as 3 camadas estão
> cumpridas, e o (c) fica *"com a redação original para uma fila FUTURA que volte a ter
> ≥2 fontes com rota"*. ⇒ **mudar a população não pode invalidar um critério que não
> está sendo computado.** O comentário do `regra_de_parada_triagem.py` é anterior ao
> fecho e foi corrigido no mesmo commit.
>
> ✅ **Consequência: este item está DECIDÍVEL AGORA.** Não depende de mais nenhuma
> medição nem de re-derivar nada — só da sua assinatura na reclassificação de camada,
> contra os gates G1–G6 já congelados no prereg.

**Custo/benefício medido** (monkeypatch em subprocesso; o script NÃO foi escrito):
censo **não se move** (tripé 165, resolvidos 187, declarado_total 200, bit-idênticos);
`classe_parada` 5→4; **fila form-limited 0 → 1**. A curva entra com **uma perna só
violada** — MAE 0,0393 (**0,79×**) e res.máx 0,0863 (**0,86×**) DENTRO, σ_res 0,0419
(**1,68×**) fora, precisando de **40 %**. Piso da fonte = 0,0250 = o global ⇒ **sem
rota F7 por piso**.

⚠️ **Por que isto toca a regra de parada:** publicar `form_limited = 0` lê-se como *"não
sobrou trabalho legítimo"*, e a medição diz que sobrou 1 — escondido por etiqueta que o
discriminante da própria campanha reprova. A condição de parada está sendo lida como
atendida **em parte por atribuição indevida** (1 de 5 membros da classe que a sustenta).
Os números do modelo não mudam; o que deixa de ser honesto é a **fila publicada**.

⚠️ **Contra-argumento preservado:** o doc da curva mede *"8 alavancas varridas, nenhuma
fecha"*. A diferença é de estatuto — *"encerrada por classe cujo remédio a piora"* não é
a mesma frase que *"problema de forma aberto, com 8 alavancas falsificadas"*.

**Não proponho:** remover a fonte · declarar a curva (sem rota F7, e declarar sem
procedência infla o resolvido com fracasso) · forma nova de engine (é outra assinatura).

---

### NA MESA (2026-08-20, 20:5x): as 5 abertas MEDIDAS perna a perna — DUAS estão a ≤ 8 %

Store **`245dc93087d1`** (uniforme, 210) · `_censo()`: tripé **166/205**, fora 39 =
34 com estatuto + **5 abertas** · limites por `rh.limite_sres`.

| curva | MAE | ×lim | res.máx | ×lim | σ_res | ×lim | pernas fora |
|---|---:|---:|---:|---:|---:|---:|:--|
| `liu2025_M16_amp0p8` | 0,0393 | 0,79 | 0,0863 | 0,86 | 0,0419 | **1,68** | σ |
| **`liu2025_M16_fig2_single`** | 0,0279 | 0,56 | 0,0579 | 0,58 | **0,0270** | **1,08** | **σ só — falta 0,0020** |
| `yang2021_amp0p5mm_ax8kN` | 0,0324 | 0,65 | 0,1083 | **1,08** | 0,0388 | **1,55** | mx + σ |
| **`yang2021_amp0p6mm_ax8kN_r1`** | 0,0167 | 0,33 | 0,0813 | 0,81 | **0,0268** | **1,07** | **σ só — falta 0,0018** |
| `yang2021_amp1p0mm_ax2kN` | 0,0285 | 0,57 | 0,1074 | **1,07** | 0,0320 | **1,28** | mx + σ |

⇒ **É o mais perto que a fila já esteve.** Duas curvas violam **uma perna só**, por
**7–8 %**, com as outras duas pernas sobrando 19–67 %. As outras três precisam de
duas pernas ou de 28–68 % no σ.

**Rota conhecida e NÃO EXECUTADA para a `fig2_single`:** o
`digitalizacao_suspeitas_resultado.md` (2026-07-29) mediu que o CSV fino tem **13
abscissas duplicadas** (30 pontos repetidos em 134) — *"introduzido hoje, na
re-digitalização fina que eu adotei"* — e recomendou consertar **por higiene**
(uma curva de decaimento não pode ter dois valores no mesmo ciclo). Impacto medido
por proxy (colapsando duplicatas pela média dos resíduos): **−0,00042**, ou seja
**~21 % da lacuna de 0,0020**. Insuficiente sozinho, mas é a única rota com
procedência já escrita, e **corrigir CSV exige prereg** (precedente do pico
espúrio, gates G1–G6).

⛔ **HIPÓTESE FALSIFICADA no caminho, registrada para ninguém repetir:** eu suspeitei
que a atribuição da `classe_parada` **por fonte** estivesse mascarando um estatuto
*metric-limited* na `r1`, porque o `digitalizacao_lint` reporta degrau entre vizinhos
de **0,428** nela — 4,3× a tolerância inteira. **Falso.** O critério do classificador
(`SALTO_COLAPSO`) é definido sobre **`metric_data`**, e ali os degraus das cinco são
**0,0051 · 0,0382 · 0,0427 · 0,0297 · 0,1200** — nenhum passa de 0,25. O 0,428 é do
**CSV CRU**: a janela da métrica não contém o colapso. ⚠️ É a armadilha do
`metric_data` **cortando pelo outro lado** — no caso do `YANG_2023` ela me fez ler um
piso que não existia; aqui ela quase me fez propor um estatuto que o dado não sustenta.
Duas grandezas de rótulo parecido em domínios diferentes.

⚠️ **E um número que eu li como mudança e não era:** o doc de 07-29 diz *"13
abscissas repetidas"* e o lint de hoje diz *"30 repetição(ões)"*. **O CSV está
intacto** — 134 pontos, 13 abscissas duplicadas, 30 pontos extras. Um instrumento
conta abscissas, o outro conta repetições.

**Nada proposto para as 3 restantes:** `amp0p8` já está coberta pelo item da
`classe_parada` (falso positivo espelhado); as duas do YANG_2021 com `mx` fora têm o
fechamento estrutural de `yang2021_abertas_geometria_dos_inputs.md` (o sinal do
resíduo alterna 3× no eixo de amplitude e as abertas **cercam** as protegidas, logo
nenhuma lei monótona serve) — e a `r1` é réplica nominal de duas curvas que estão no
tripé, o que põe o teto no scatter de espécime.

---

### NA MESA (2026-08-20, 21:5x): auditei os MEUS 4 itens — TRÊS caem por medição, sobra UM

Store **`245dc93087d1`** · `_censo()`: tripé **166/205**, fora 39, 5 abertas.
Apliquei aos meus próprios itens a disciplina que matou a P-12 na hora anterior.

⚠️ **Primeiro achado, e é uma falha minha de processo:** eu vinha reportando
*"na mesa: T, U, V, W"* há horas, mas **só o W estava escrito neste arquivo**. T, U e V
existiam apenas nos meus resumos horários — se o senhor abrisse o documento, não estavam
lá. Corrigido abaixo, com o estatuto de cada um medido.

| item | o que eu afirmava | veredito medido |
|---|---|---|
| **T** | o rótulo de piso da `fig8a` super-afirma | ⛔ **MOOT** — já consertado pela adoção **R2**; e a `fig8c`, que eu suspeitei, é **honesta**: L24 no CSV cru **0,1495** contra piso **0,152** (tolerância 0,02) |
| **U** | o critério (c) da parada não distingue `INCONCLUSIVO` | ⛔ **MOOT** — o (c) foi **FECHADO em 2026-08-14** (`regra_de_parada_proposta.md` §FECHO) |
| **V** | o `engine_fingerprint` é cego aos pares declarados | ✅ **VIVO E CONFIRMADO** (abaixo) |
| **W** | a `classe_parada` esconde 1 falso positivo | ✅ vivo — e **DESBLOQUEADO**, ver a correção no próprio item |

#### O único que sobra — item V, medido

`engine_fingerprint()` hasheia **apenas** `{"shared": consts, "adopted": adopted}`; a
inspeção do fonte confirma que ele **não cita `_PARES_REPLICA_DECLARADOS`**. Hoje há
**5 pares declarados**:

| par | procedência declarada |
|---|---|
| `caccese2009_tapered_45kN` rep1×rep2 | réplicas da MESMA condição |
| `eccles2010_fig8a`×`fig8c` | rótulo **do autor** (baseline1/baseline2) |
| `li2022ti_axialmin_10Hz`×`axial_10Hz_full` | mesma condição, espécimes distintos |
| `liu2016wear_fig7` run1×run2 | mesma condição (piso pode subestimar) |
| `karlsen2022_M30_HV` run2p2×run7p1 | mesma condição nominal |

⚠️ **Por que isto importa com número:** o par do ECCLES moveu `limite_sres` da fonte de
**0,0250 → 0,0698** (2,8×), o que **muda vereditos de curva**. Um store carimbado antes
e depois de declarar um par tem o **mesmo fingerprint** — exatamente o hazard que o
`CLAUDE.md` já documenta para inputs/CSV (*"o fingerprint não cobre inputs"*), agora
numa lista que mora em `report_html.py`.

**Existem duas guardas sobre os pares** (`test_par_de_replica_e_mecanicamente_identico`,
`test_pares_piso_familia`), mas elas checam a **validade do par**, não a **cobertura do
hash**. ⇒ recomendação V2: incluir `_PARES_REPLICA_DECLARADOS` no blob do
`engine_fingerprint`. **Isto move o fingerprint de todos os 210 registros** ⇒ exige
prereg com re-carimbo e gate de "zero mudança de métrica" (a inclusão é de metadado:
nenhuma predição muda, só o hash passa a denunciar a mudança).

#### Lição de método que isto pagou

O que me fez publicar *"W bloqueado pelo critério (c)"* foi **ler um comentário de
código** (`regra_de_parada_triagem.py`) em vez de conferir se o motivo estava vivo. O
comentário era verdadeiro quando escrito e envelheceu com o fecho de 08-14. ⇒ **comentário
que carrega MOTIVO de não-execução envelhece junto com o motivo**, e não há teste que o
policie — o `test_meta_numeros_nao_envelhecem` guarda números em docs, não justificativas
em código. O comentário foi corrigido no mesmo commit.

---

### NA MESA (2026-08-21, 03:5x): o shell consertado acha uma dose que FECHA a `yang2021_r1` — e as 3 ressalvas importam mais que o número

Store **`89b1899f18c1`** (uniforme, 210) · `_censo()`: tripé **166/205**.
Contexto: consertei em `5622e0f` um defeito do `ataque_curva.py` que lia a base efetiva
com `{}` em vez de `frozen_constants()`. Rodando o shell corrigido na
`yang2021_amp0p6mm_ax8kN_r1` — a **mais perto de fechar do projeto** (σ 1,07×) e cujo
veredito gravado é **"sem rota"** —, ele agora reporta:

| `C_creep` | MAE | res.máx | σ_res | |
|---:|---:|---:|---:|---|
| 9,334e-12 | 0,0227 | 0,0920 | 0,0285 | 1,14× |
| 1,4e-11 | 0,0188 | 0,0866 | 0,0276 | 1,11× |
| 2,8e-11 | 0,0163 | 0,0706 | 0,0255 | 1,02× |
| **3,733e-11** | **0,0183** | **0,0600** | **0,0246** | ✅ **FECHA** |

Melhora **monótona** no σ, e a dose que fecha é exatamente **2,0× o valor do `shared`**
(1,8667e-11).

#### ⚠️ As três ressalvas, e nenhuma é cosmética

1. **A margem é 1,6 %** — σ 0,0246 contra limite 0,0250. O precedente do projeto é
   explícito contra margem dessa ordem: na adoção do par ECCLES ficou registrado que *"a
   `fig8a` passa a barra FORTE por 4·10⁻⁶, margem que não sobrevive a arredondamento"*, e
   o veredito foi rebaixado por isso. Aqui a folga é maior que aquela, mas segue frágil.
2. **`C_creep` não tem `prov` e não está no `cfg` do `YANG_2021`** — ela roda no valor do
   bloco `shared`, que é o **fit da âncora interna**. O shell a marca `livre` porque **não há rótulo**, e
   *"sem prov"* **não é** *"livre para fitar"*: a §4.7 do `MODEL_LEGITIMACY` registra
   `C_creep` como constante **por par tribológico**, com ICs disjuntos entre pares
   (304SS 9,9e-13 × âncora interna 1,2e-11). Dobrá-la para fechar métrica seria fit-sem-observável —
   a classe que o `metodo_leitura_de_constantes.md` lista entre as **RECUSAS**.
3. **NÃO estabeleci que a dose era invisível antes do conserto.** Os quatro fechamentos do
   `yang2021_r1_sem_rota_resultado.md` tratam de *instrumento* (grade esparsa), *rampa de
   fratura por espécime*, *trim* e *teto de scatter de espécime* — **nenhum testou creep**.
   Se o shell já a alcançava, o "sem rota" foi publicado sem rodar este instrumento; se não
   alcançava, o conserto a destravou. Não medi qual, e a diferença muda de quem é o mérito.

#### O que faria disto uma adoção legítima

Uma **procedência** para `C_creep` neste par, não uma dose que fecha: o rig é M10 aço com
carga axial (Fig. 6 do Yang 2021), e o padrão que a campanha usa é *ler* a constante de um
observável publicado (regressão com r² ≥ 0,65 ⇒ leitura) — foi assim nas 23 instâncias do
`metodo_leitura_de_constantes.md`. **Sem isso, a recomendação é NÃO adotar**, e o valor
deste item é ter transformado *"sem rota"* em *"há uma direção, e ela exige um número com
origem"*.

⚠️ **Contra-indicação medida:** a `r1` tem **duas irmãs no tripé** (r2 σ 0,0103 · r3
0,0073) com a **mesma** parametrização. Dobrar `C_creep` da fonte as move também, e o
diagnóstico gravado é que o desvio da `r1` é **scatter de espécime na cauda** (2 de 9
pontos). Gate obrigatório de qualquer prereg aqui: **as irmãs não podem sair do tripé.**

#### ⛔ FECHAMENTO do mesmo item (04:5x): a rota da `fig2_single` foi FALSIFICADA pelo controle de fonte

Completei a varredura que o conserto do shell exigia — as **5 abertas**, não só as 2 da
véspera. Resultado por curva:

| curva | veredito do shell corrigido |
|---|---|
| `liu2025_M16_amp0p8` | nenhuma fecha (o `K_archard` é ótimo interior — ver `5622e0f`) |
| **`liu2025_M16_fig2_single`** | **4 doses FECHAM** — `C_creep` 1,95e-11 e 2,6e-11, `N_emb` 7,5 e 10 |
| `yang2021_amp0p5mm_ax8kN` | nenhuma fecha — **0 de 25 células** |
| `yang2021_amp1p0mm_ax2kN` | nenhuma fecha — **0 de 25 células** |
| `yang2021_amp0p6mm_ax8kN_r1` | fecha com `C_creep` 3,733e-11 (as 3 ressalvas acima) |

A dose forte da `fig2_single` era espetacular: `C_creep` 2,6e-11 dá
**0,0091 / 0,0174 / 0,0100** = 0,18× / 0,17× / **0,40×** dos limites. E a `prov` dela é
**`fitado-this-rig per-par`**, ou seja **não** travada por procedência.

⛔ **O controle de fonte a mata, e o número é brutal:**

| curva | nominal | com `C_creep` = 2,6e-11 |
|---|---|---|
| `amp0p25` · `amp0p3` · `amp0p4` · `amp0p5` · `amp0p6` | **5 no tripé** | **0 no tripé** |
| `amp0p8` | fora | fora, e pior (res.máx 0,0863 → **0,1771**) |
| `fig2_single` | fora | ✅ fecha |

⇒ saldo **+1 / −5**. É o padrão **D-AB** em forma pura (a alavanca ótima no alvo é
desastrosa para a fonte), e explica **por que** a grade F3 fixou ×0,70: aquele valor é
**ótimo de FONTE**, não do alvo. Rota **falsificada**, e a `classe_parada` está certa sobre
esta curva — errada só sobre a `amp0p8`, que o item W já corrigiu.

#### A redireção que isto abre, e ela é de INPUT, não de constante

A `fig2_single` precisa de **2×** o creep das irmãs, no **mesmo par tribológico** (mesmo
parafuso, mesmos materiais) — logo `C_creep` per-case seria fitar uma curva, que o
`metodo_leitura_de_constantes.md` lista entre as **RECUSAS**.

⚠️ Mas o `CLAUDE.md` registra que **a amplitude da Fig. 2 NÃO é reportada no paper**. Creep
é dirigido por **TEMPO**, não por amplitude — então o que pode diferir legitimamente nesta
curva é a **duração/frequência do ensaio**, não a constante. ⇒ candidato honesto:
`t_0`/relógio de creep como **input** desta curva, com procedência lida do paper — não
`C_creep` como constante ajustada. **Não medi isso**; fica nomeado como próximo passo.

⚠️ **E o instrumento agora tem passado:** as duas curvas do YANG_2021 com `mx` fora deram
**0 de 25 células** mesmo com o shell corrigido, o que **confirma** o fechamento estrutural
de `yang2021_abertas_geometria_dos_inputs.md` (sinal alterna 3× no eixo de amplitude) — a
primeira vez que aquele veredito é testado por um instrumento que alcança todos os canais.

#### ✅ ESCOPO da contaminação do shell FECHADO (05:5x) — nada publicado foi afetado

Pergunta que faltava: o `ataque_curva.py` produziu vereditos **em toda a campanha** com a
base errada (`{}` em vez de `frozen_constants()`, consertado em `5622e0f`). O que isso
danificou?

**Medido, curva a curva, comparando os dois conjuntos de override nas 210:**

| | |
|---|---|
| curvas em que `base-vazia ≠ base-real` | **39 de 210** |
| chaves que diferem | **exatamente `K_archard` e `k_wear_spec`** — nenhuma outra |
| fontes | `ICMEZ_2025` · `LIU_2022_RETIGHT` · `LIU_2025` · `ANCORA_INTERNA` |

⇒ o defeito é **do canal de wear e só dele**. Toda outra constante ou vem do `cfg`
(presente nas duas leituras) ou cai no `_mat`, que era construído corretamente.

**E das 4 fontes, quantas têm curva cujo ESTATUTO depende de um veredito?**

| fonte | comparáveis | no tripé | com estatuto | sem nada |
|---|---:|---:|---:|---:|
| `ICMEZ_2025` | 8 | **8** | 0 | **0** |
| `LIU_2022_RETIGHT` | 21 | **21** | 0 | **0** |
| `LIU_2025` | 7 | 5 | 0 | **2** |
| `ANCORA_INTERNA` | 0 | — | — | 0 *(fora do censo)* |

⇒ **apenas o `LIU_2025`**, e as 2 são a `amp0p8` e a `fig2_single` — **exatamente** as que
re-varri com o shell corrigido (`5622e0f`, `0127fd6`). As outras duas fontes estão
**inteiras no tripé** (8/8 e 21/21), logo nunca houve veredito de "sem rota" nelas para
contaminar.

⚠️ **Nota que impede uma leitura errada:** nas fontes com `k_wear_scale_tr` **não-zero**
(ICMEZ 0,056 · LIU_2022 0,06 · âncora interna 0,15) a base vazia não *pulava* a alavanca — ela
roteava o valor para a **constante errada** (`K_archard` em vez de `k_wear_spec`), o que é
pior em espécie. Não teve consequência **só porque** nenhuma dessas curvas dependia de
veredito. Se qualquer uma delas cair do tripé no futuro, o shell tem de ser rodado
**depois** do conserto — o que hoje já é o caso.

⚠️ **O store e o censo nunca foram afetados:** o `simulate_case` sempre usou a base certa
(`consts, _ = frozen_constants()`); o defeito vivia só na leitura de base do **probe**.

⇒ contaminação **integralmente delimitada e integralmente endereçada**. Fica escrito para
ninguém reabrir a pergunta por suspeita.

---

### NA MESA (2026-08-21, 13:4x): as 5 abertas estão ESGOTADAS PARA CONSTANTES — o que falta exige assinatura ou bancada

Store **`3c9afd6579a1`** (uniforme, 210) · `_censo()`: tripé **168/205 (82 %)** · fora 37 =
22 exceção + 10 declarada + 4 classe + **1 form-limited**.

Instrução do professor: *"continue até chegar no tripé"*. Este item diz, com medição, o que
separa 168 de 205 — e por que nenhuma das 5 abertas cede a constante.

| curva | estado medido HOJE, com o shell corrigido |
|---|---|
| `liu2025_M16_amp0p8` | `K_archard` é **ótimo interior nas 3 pernas**; nenhuma alavanca livre fecha. Único membro da fila form-limited |
| `liu2025_M16_fig2_single` | `C_creep` fecha com 60 % de folga **mas o controle de fonte dá +1/−5** · `t_0` fecha com **folga ZERO** · rota do par **fechada** (abaixo) |
| `yang2021_amp0p5mm_ax8kN` | **0 de 25 células** |
| `yang2021_amp1p0mm_ax2kN` | **0 de 25 células** |
| `yang2021_amp0p6mm_ax8kN_r1` | fecha com `C_creep` a **1,6 %** de margem, e a constante é per-par sem procedência para este rig |

#### A rota que eu persegui hoje, e por que ela morre em prova GRAVADA

Medi que `fig2_single` e `amp0p8` estão registradas com **o mesmo δ = 0,8 mm** e vidas
**9870 × 14400** — o que as tornaria **réplicas da mesma condição** e daria ao `LIU_2025` um
**piso de par declarado**, elevando o limite de σ de 0,0250 e fechando as duas de uma vez.

⛔ **Fechada, e já estava.** O `CLAUDE.md` registra como *errata viva*: **a amplitude da
Fig. 2 NÃO é reportada** no paper — o 0,8 mm dela é **suposição do registry**, não valor
publicado. Declarar o par seria casar **suposição com medição**, a classe de pareamento
inválido que a campanha já invalidou **7 vezes**. E a mesma linha registra que *"os '44 % de
scatter' **caíram** — o defensável é **±17 % de relógio** (§4.48b)"*, ou seja **esta exata
interpretação já foi examinada e retratada**.

⚠️ **Quarta vez nesta semana que a prova gravada estava à frente da minha dúvida** (as
outras: o `F_amp` "Pai&Hess" já corrigido · a leitura "3 pernas descobertas" já refutada por
errata · o "as provas do ECCLES não são de scatter" já escrito no mesmo doc). O padrão é
consistente o suficiente para ser regra e não acidente: **antes de perseguir uma rota,
procurar se ela já foi percorrida** — o custo de buscar é minutos, o de re-descobrir é horas.

#### O que de fato separa 168 de 205

| classe | curvas | o que destrava |
|---|---:|---|
| exceção assinada | 22 | nada — já têm estatuto com prova |
| declarada | 10 | nada — critério medido |
| `classe_parada` | 4 | dado novo (a classe foi encerrada pela regra de parada) |
| **abertas** | **5** | **forma nova de engine** (assinatura) **ou** dado de bancada |

⇒ **não há mais rota por constante nas 5.** Chegar a 205 requer: (a) forma nova — e há duas
**nomeadas e não propostas**, o *contorno axial externo* do ECCLES (fig6, teto medido a
3,24× mesmo suprimindo o canal culpado) e a *redistribuição intra-janela* que a `amp0p8` e a
fig6 compartilham; ou (b) dado — a amplitude da Fig. 2 do Liu, e réplicas nas condições do
YANG_2021.

⚠️ **Isto não é pedido de parada.** É o mapa do que resta, medido, para que a próxima
assinatura seja sobre a coisa certa em vez de sobre a próxima dose.
