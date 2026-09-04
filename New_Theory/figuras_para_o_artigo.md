# Figuras para o artigo — plano medido, 2026-08-25

**Pergunta do professor:** *"para mostrar o funcionamento do software em um artigo, o que me
sugere de gráficos e imagens?"*

Censo **171/205**, fingerprint `db7de97e682a`. Só-leitura.

> ## ✅ Status 2026-08-28 — as 10 figuras EXISTEM no anexo (`build_annex_docx.py`)
>
> Todas geradas em inglês, 300 dpi, mathtext (sem glifo fora do STIX), recomputadas do
> store a cada build — `py -3.12 New_Theory/build_annex_docx.py` → `New_Theory/annex/`.
> Numeração na ORDEM do argumento do anexo (a legenda é automática):
>
> | plano | anexo | arquivo | nota |
> |---|---|---|---|
> | Fig. 1 esquema MSD | Figure 1 (§2) | `fig_msd_schematic.png` | desenhado; corte da junta + cadeia com contatos |
> | Fig. 2 laço de acoplamento | Figure 2 (§2.3) | `fig_coupling_loop.png` | mecanismos em paralelo + D modulando; "runaway/self-arrest" |
> | Fig. 3 cadeia de extração | Figure 3 (§5) | `fig_extraction_chain.png` | 4 painéis; curva escolhida por REGRA (`_exemplo_cadeia`: align≠1, ponto fora da janela, n_max≤1000, tripé, recorte), hoje `bauer2024_M12_fig8_test1`; a legenda declara o efeito de borda (873,2 > n_max 873) |
> | Fig. 4 uma curva em detalhe (resíduo, 3 pernas) | Figure 4 (§6) | `fig_residual_three_legs.png` | 2 colunas: uma que fecha + a de MENOR MAE que reprova SÓ no σ (escolha programática, hoje `yang2021_amp0p6mm_ax8kN_r1`) |
> | Fig. 5 ⭐ uma física, N comportamentos | Figure 5 (§8.1) | `fig_one_physics.png` | já existia |
> | Fig. 10 custo de calibração | Figure 6 (§8.4) | `fig_calibration_cost.png` | já existia (curvas/GRUPO) |
> | (extra) | Figure 7 (§10.2) | `fig_binding_leg.png` | perna que decide + severidade |
> | Fig. 8 ⚠️ decisão ISO/DIN | Figure 8 (§11) | `fig_engineering_decision.png` | já existia |
> | Fig. 6 paridade | Figure 9 (§12.1) | `fig_parity.png` | já existia |
> | (extra) | Figure 10 (§12.2) | `fig_median_mae_by_source.png` | mediana por fonte |
> | Fig. 7 envelope | Figure 11 (§12.3) | `fig_validity_envelope.png` | já existia |
> | Fig. 9 decomposição | Figure 12 (§12.4) | `fig_mechanism_decomposition.png` | 1 curva (liu2016 fig11a), não 4 painéis; os 4 painéis por mecanismo dominante seguem como opção |
> | opcional: tornado OAT | Figure 13 (§12.5) | `fig_sensitivity_tornado.png` | `kb.sensitivity` por família (7 transversais, 2 axiais); congeladas S≈0 marcadas |
>
> **Seções acrescentadas em 2026-08-28 (parecer de referee):** §2.5 equações governantes, §2.6
> esquema numérico/custo/verificação (Norton fechado 3e-20 m, resíduo de energia, throughput e
> contagem de testes medidos NO build), §4 corpus com condições e [n], §5.1 incerteza da
> digitalização (par duplicado do Lu recomputado), §5.2 janelas por julgamento (21 curvas com
> motivo lido do `prov`), §9.3 classes de procedência CONTADAS (leitor conservador: a classe mais
> fraca vence), §12.5 sensibilidade, Apêndice C ledger das 609 constantes, capa com autor/
> afiliação/revisão git. Falta só a DISPONIBILIDADE (URL, licença, DOI), que é decisão do professor.
>
> Nomes de arquivo em INGLÊS desde 2026-08-28 (pedido do professor: "tudo em inglês,
> incluindo figura"; num docx o nome é invisível, numa submissão de figuras separadas não).
>
> **Artigo PRINCIPAL (2026-08-28, tarde):** `New_Theory/paper/BAS_V2_main_paper.docx`, gerado por
> `build_paper_docx.py` a partir do anexo (mesmos dados/figuras/auditorias). Usa 11 das 13
> figuras, renumeradas na ordem do argumento: esquema MSD (1), laço (2), cadeia (3), resíduo
> 3 pernas (4), paridade (5), uma física (6), decomposição (7), decisão ISO/DIN (8), tornado (9),
> custo (10), envelope (11). Ficam fora do artigo (só no anexo): perna que manda, mediana por
> fonte. Referências no texto por `prox_fig()`, nunca digitadas.
>
> **Tabelas do plano:** (1) corpus = §4 do anexo; (3) critério = §6; (2) constantes com
> procedência = §9.1/§9.3 + **Apêndice A (205 linhas, uma por curva: carga, F₀, f, n, MAE,
> res.máx, σ_res, estatuto)** e **Apêndice B (5 registros fora do censo, com motivo)**. A
> procedência das 147 `per_case` foi FUNDIDA ao `adopted_configs.json` em 2026-08-28 (decisão
> do professor; ITEM AA fechado), junto com as 11 constantes compartilhadas que não tinham texto.
>
> ⚠️ **Armadilha medida ao fazer a Fig. 3:** `store[cid]["cycles"]` é grade LINEAR de 400
> amostras (`np.linspace(0, n_max, 400)`) — em n_max = 10⁶ a 2ª amostra é N = 2506, logo a
> curva "raw" do store NÃO resolve o transiente de embedding e, em eixo log, parece um patamar
> em 1,0 até ~2500 ciclos. Para o transiente use `metric_pred` (resolução cheia nas abscissas
> do dado) ou escolha curva com n_max ≤ ~1000. Foi por isso que o exemplo saiu do liu2016.

---

## O enquadramento, porque ele decide as figuras

Artigo tem **orçamento**: 8–12 figuras, e cada uma tem de responder uma pergunta que o
revisor vai fazer. A tentação é mostrar o software; o que convence é mostrar o **argumento**.

⚠️ **E o argumento mais forte deste projeto não é "ajustamos 205 curvas bem".** É:

> *ajustamos 205 curvas de 27 fontes com uma física só, **medimos quanto custou** em
> constantes, e **registramos o que falhou**.*

As figuras de **limitação honesta** são o que faz o revisor acreditar no resto. Um artigo com
só as figuras boas gera a pergunta *"onde estão os casos ruins?"* — e aí o revisor procura, e
a resposta chega dele em vez de vir de você.

---

## As 10 figuras, na ordem do argumento

### Fig. 1 — O modelo massa-mola-amortecedor (esquemático)

**Argumenta:** que existe um modelo físico, não uma função de ajuste.
**Revisor pergunta:** *"o que exatamente está sendo validado?"*
**Existe:** SVG em `variable_explorer/concept_msd-model.html`.
**Falta:** versão para impressão (traço, sem cor de tema).

### Fig. 2 — O laço de acoplamento `F₀ → [K(s)] → Φ → afrouxamento → F₀`

**Argumenta:** a não-linearidade que distingue o V2 — a rigidez é reavaliada a cada ciclo, e
é por isso que o modelo pode produzir *runaway* e *auto-travamento* sem um parâmetro para
cada.
**Revisor pergunta:** *"qual é a contribuição teórica?"*
**Existe:** SVG em `variable_explorer/concept_coupling.html`.
**Nota:** esta é a figura de **contribuição**. Se o artigo tiver uma só figura conceitual,
é esta, não a Fig. 1.

### Fig. 3 — A cadeia de extração, em 4 painéis

Figura do artigo → CSV digitalizada → janela da métrica → os três vetores comparados.
**Argumenta:** que a comparação é reprodutível e que os filtros são declarados.
**Revisor pergunta:** *"como vocês compararam com a figura publicada?"* — e esta é a pergunta
que **derruba** artigos de validação por digitalização quando não há resposta.
**Existe:** `metodologia/index.html`, 10 seções — condensar em 4 painéis.

### Fig. 4 — Uma curva em detalhe: modelo, dado e resíduo

Painel superior modelo × dado; inferior o resíduo com as três pernas anotadas.
**Argumenta:** que o erro é pequeno **e de que tipo** ele é.
**Revisor pergunta:** *"o que significa MAE 0,012 nesta curva?"*
**Existe:** `metodologia/index.html` §4 e §7. Curva sugerida:
`liu2016wear_fig11a_af7p5kn` (MAE **0,0121**, fonte 14/14).

### Fig. 5 — ⭐ Uma física, N comportamentos

As 4 curvas da fig. 18 do `LU_2024` com **constantes idênticas**: retenção final de **0,771 a
0,113**, 3 no tripé.
**Argumenta:** que não é ajuste por curva — a diferença vem **inteira** da entrada.
**Revisor pergunta:** *"vocês não estão apenas ajustando cada curva?"*
**Existe:** `metodologia/modelo_nao_fit.html`.
**Nota:** ⭐ **é a figura central do artigo.** Se o revisor só olhar uma, que seja esta.
Acompanha bem a predição zero-refit do ROUSSEAU HDPE (0,267 × 0,799, condição inédita sem
tocar em constante) como painel (b).

### Fig. 6 — Paridade: previsto × observado, 205 curvas

R² **0,9455** contra a reta 1:1, viés **+0,0083**, 78 % dentro de ±0,05.
**Argumenta:** acurácia global num painel.
**Revisor pergunta:** *"e no conjunto todo?"*
**Existe:** `metodologia/qualificacao.html` §2.

### Fig. 7 — Envelope de validade

Amplitude × F₀ e diâmetro × frequência, um ponto por curva, vazios visíveis.
**Argumenta:** o domínio em que a afirmação vale.
**Revisor pergunta:** *"sobre que faixa isto foi validado?"* — pergunta **certa** de vir, e
sem a figura a resposta é uma tabela que ninguém lê.
**Existe:** `metodologia/qualificacao.html` §3.

### Fig. 8 — ⚠️ Decisão de engenharia e os falsos seguros

Matriz ISO 16130 / DIN 25201-4: acerto 94,1 % / 95,6 %, com **7 falsos seguros** nomeados —
e **3 deles passam o tripé**.
**Argumenta:** honestidade, e que vocês sabem onde o software erra do lado perigoso.
**Revisor pergunta:** *"qual a consequência de engenharia do erro?"*
**Existe:** `metodologia/qualificacao.html` §1.
**Nota:** ⚠️ **é a figura que compra credibilidade.** Publicar que 3 curvas aprovadas pela
própria régua dizem *"seguro"* onde o ensaio diz o contrário é o tipo de coisa que um revisor
não espera encontrar — e que muda a leitura de todo o resto.

### Fig. 9 — Decomposição por mecanismo

Área empilhada: quanto cada um dos 6 mecanismos tirou de pré-carga, por fonte.
**Argumenta:** que o modelo tem **estrutura interna** — não é um ajuste com N botões, é uma
soma de canais com significado.
**Revisor pergunta:** *"o modelo é interpretável?"*
**Existe:** `metodologia/artigo_<FONTE>.html`. Sugestão: 4 painéis com fontes de mecanismo
dominante diferente (embedding · creep · wear · rotacional).

### Fig. 10 — Custo de calibração

Curvas por constante por fonte, e a fração com procedência declarada (**53 de 200**).
**Argumenta:** o preço do ajuste, publicado ao lado do erro.
**Revisor pergunta:** *"quantos parâmetros livres?"* — a pergunta **mais perigosa** para um
modelo com muitos parâmetros, e respondê-la antes de ser perguntada desarma a objeção.
**Existe:** relatório mestre (gráfico "custo × qualidade do dado") + as páginas por artigo.

---

## Opcional, se houver espaço

| figura | argumenta | onde está |
|---|---|---|
| Sensibilidade OAT (tornado) | quais parâmetros importam — e que na família **axial 14 de 17 são inertes** | `global_parametros.html` |
| Erro contra réplica × contra condição | que parte do erro publicado é espalhamento do ensaio | `metodologia/replicas_<FONTE>.html` |
| Fluxograma do método | reprodutibilidade | `metodologia/fluxo.html` |
| Captura da GUI | que é software usável, não script | `scripts/export_thesis_figures.py --show` |

⚠️ **A captura da GUI é a única "imagem de software" que recomendo, e no máximo uma.** Um
artigo de modelo não ganha nada com telas; ele ganha com o modelo. Se a revista pedir
evidência de implementação, uma tela do Solver com a curva na Results resolve.

## Tabelas (não figuras)

1. **O corpus:** fonte, N curvas, condição, faixa, DOI. Sem ela, "27 fontes" é alegação.
2. **As constantes:** símbolo, valor, unidade, **procedência** (lida do paper / de norma /
   fitada). ⚠️ Esta é a tabela que separa o artigo de um exercício de ajuste — e hoje
   **147 de 200** entradas `per_case` não têm procedência declarada, o que significa que a
   tabela **ainda não pode ser escrita por inteiro**.
3. **O critério:** as três pernas, os limites, e a âncora de cada limite (ISO 16130 85 % /
   DIN 25201-4 80 % para o MAE; piso de repetibilidade medido para o σ_res).

---

## ⚠️ O que falta de verdade: caminho de exportação

Existe `scripts/export_thesis_figures.py` — 19,6 KB, com `--dpi 300 --pdf` e captura de GUI
offscreen. **Mas:**

| problema | medido |
|---|---|
| **não está versionado** | `git log` não tem nenhum commit dele |
| **6 semanas desatualizado** | de 14/jul; nada do que foi medido desde então |
| ⚠️ **tem figura VENCIDA** | `ancora_interna` — a `ANCORA_INTERNA` **saiu do projeto** em 01/08; as 3 curvas seguem no store (**0 comparáveis pelo censo**), então a figura **ainda gera**, com dado fora do projeto |
| cobre 5 tipos | grid por fonte · decomposição · âncora interna · ledger MEM · medianas por fonte |
| **não cobre** | paridade · envelope · decisão ISO/DIN · uma-física-N-comportamentos · custo de calibração · cadeia de extração |

⇒ **das 10 figuras acima, o exportador cobre 2** (Fig. 9 e parte da Fig. 4). As outras 8
existem como **SVG de tela** — cor de tema escuro, fonte de 10 px, sem numeração. Para
revista precisam de traço/escala de cinza, fonte legível em largura de coluna, e PDF vetorial.

**A recomendação, então, tem duas partes:** as 10 figuras acima (o *que*), e um exportador
que as produza em qualidade de publicação a partir das mesmas medições (o *como*). O segundo
é o trabalho real — hoje o material existe e o caminho para o PDF não.

⚠️ E antes de qualquer coisa: **remover ou marcar a figura da âncora interna**. Um artigo com uma figura
de dado que o próprio projeto retirou é erro material, e é o tipo de coisa que um revisor
atento encontra.
