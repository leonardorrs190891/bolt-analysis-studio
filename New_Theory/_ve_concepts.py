# -*- coding: utf-8 -*-
"""Paginas conceituais 'Fundamentos' do Explorador de Variaveis.

NAO importar diretamente. build_variable_explorer._load_content() executa este
modulo injetando CONCEPT_PAGES. Corpos = HTML bilingue (PT/EN via <span data-l>),
inseridos RAW (tags reais + entidades simples). '<div id="cw"></div>' marca onde
o widget interativo e montado. widget = string do sim (_widget_data).
"""

CONCEPT_PAGES.extend([

    # ------------------------------------------------------------ Hub do Manual
    # Pagina-hub da F6 (S6). Nao repete conteudo: aponta os 3 volumes em
    # docs/MANUAL_BAS_V2/ e mostra as 5 figuras GERADAS do store por
    # scripts/manual_figs.py (as mesmas que o Manual cita, servidas do mesmo
    # arquivo — nunca uma segunda copia).
    dict(
        slug="manual",
        nav_pt="Manual do BAS V2 (3 volumes)", nav_en="BAS V2 Manual (3 volumes)",
        title_pt="Manual do BAS V2", title_en="BAS V2 Manual",
        hook_pt="entender &middot; explicar &middot; aplicar &mdash; com os n&uacute;meros do store",
        hook_en="understand &middot; explain &middot; apply &mdash; with the store's numbers",
        body='''
<div class="sub"><span data-l="pt">O Manual &eacute; o <b>fio condutor</b> do projeto: tr&ecirc;s
volumes em pt-BR que costuram o que j&aacute; existe (equa&ccedil;&otilde;es, legitimidade,
metodologia, galeria) em vez de duplicar. Os arquivos vivem em
<code>docs/MANUAL_BAS_V2/</code>.</span><span data-l="en">The Manual is the project's
<b>through-line</b>: three volumes (pt-BR) that stitch together what already exists
(equations, legitimacy, methodology, gallery) instead of duplicating it. Files live under
<code>docs/MANUAL_BAS_V2/</code>.</span></div>

<h2 class="sec"><span data-l="pt">Os tr&ecirc;s volumes</span><span data-l="en">The three volumes</span></h2>
<ul class="refs">
<li><a href="../../docs/MANUAL_BAS_V2/01-entender-o-modelo.md"><b>Volume 1 &mdash;
<span data-l="pt">Entender o modelo</span><span data-l="en">Understand the model</span></b></a>
&ndash; <span class="src"><span data-l="pt">o paradigma MSD com estado lento, a energia como
invariante, a tese <i>formas transferem / constantes n&atilde;o</i>, a tabela de TODAS as
constantes com proced&ecirc;ncia, as limita&ccedil;&otilde;es L1&ndash;L7 e o hist&oacute;rico de
falsifica&ccedil;&otilde;es.</span><span data-l="en">the MSD paradigm with slow state, energy as an
invariant, the <i>shapes transfer / constants don't</i> thesis, the table of ALL constants with
provenance, limitations L1&ndash;L7 and the falsification record.</span></span></li>
<li><a href="../../docs/MANUAL_BAS_V2/02-explicar-o-modelo.md"><b>Volume 2 &mdash;
<span data-l="pt">Explicar o modelo</span><span data-l="en">Explain the model</span></b></a>
&ndash; <span class="src"><span data-l="pt">material para terceiros: narrativa em 3 n&iacute;veis
(par&aacute;grafo &rarr; 10 minutos &rarr; semin&aacute;rio), as 5 figuras com o que cada uma
prova, e um FAQ de obje&ccedil;&otilde;es em que cada resposta traz evid&ecirc;ncia
cit&aacute;vel.</span><span data-l="en">material for third parties: a 3-level narrative
(paragraph &rarr; 10 minutes &rarr; seminar), the 5 figures with what each proves, and an
objections FAQ where every answer carries citable evidence.</span></span></li>
<li><a href="../../docs/MANUAL_BAS_V2/03-aplicar-o-software.md"><b>Volume 3 &mdash;
<span data-l="pt">Aplicar o software</span><span data-l="en">Apply the software</span></b></a>
&ndash; <span class="src"><span data-l="pt">instalar e rodar, o fluxo tela por tela, analisar uma
junta nova (de onde vem cada input), acrescentar um artigo fim-a-fim,
reprodutibilidade e as armadilhas reais.</span><span data-l="en">install and run, the flow screen
by screen, analysing a new joint (where each input comes from), adding a paper end-to-end,
reproducibility and the real gotchas.</span></span></li>
</ul>

<h2 class="sec"><span data-l="pt">O estado do modelo, do store real</span>
<span data-l="en">Model state, from the real store</span></h2>
<p class="intro"><span data-l="pt">Fingerprint <code>4f5bedfbace4</code>. Todo n&uacute;mero do
Manual sai daqui &mdash; o gate da F6 pro&iacute;be n&uacute;mero solto.</span>
<span data-l="en">Fingerprint <code>4f5bedfbace4</code>. Every number in the Manual comes from
here &mdash; the F6 gate forbids loose numbers.</span></p>
<ul class="refs">
<li><b>147 / 202</b> <span data-l="pt">curvas de artigo no <b>trip&eacute;</b>
(<code>MAE&lt;0,10</code> E <code>res.m&aacute;x&lt;0,10</code>) = <b>73&nbsp;%</b>, de 28
fontes.</span><span data-l="en">paper curves inside the <b>tripod</b>
(<code>MAE&lt;0.10</code> AND <code>maxerr&lt;0.10</code>) = <b>73&nbsp;%</b>, from 28
sources.</span></li>
<li><b><span data-l="pt">mediana</span><span data-l="en">median</span> 0,0315</b> ·
<span data-l="pt">m&eacute;dia</span><span data-l="en">mean</span> 0,0445 ·
<span data-l="pt">mediana do res.m&aacute;x</span><span data-l="en">median maxerr</span> 0,0623</li>
<li><b><span data-l="pt">o gargalo &eacute; o PICO</span><span data-l="en">the bottleneck is the
PEAK</span></b> &ndash; <span class="src"><span data-l="pt">das 55 curvas fora, <b>34 violam s&oacute;
o res.m&aacute;x</b> e <b>0 violam s&oacute; o MAE</b>. Esfor&ccedil;o medido em MAE m&eacute;dio
n&atilde;o move a meta.</span><span data-l="en">of the 55 outside, <b>34 violate only maxerr</b> and
<b>0 violate only MAE</b>. Effort measured in mean MAE does not move the goal.</span></span></li>
<li><b>3</b> <span data-l="pt">constantes fitadas no dataset inteiro</span>
<span data-l="en">constants fitted over the whole dataset</span>
(<code>W_conf_ref</code>, <code>C_creep</code>, <code>F0_test</code>)</li>
</ul>

<style>
/* As figuras foram GERADAS em duas variantes (clara e escura) — os passos
   escuros sao os da propria paleta para superficie escura, nao uma inversao
   automatica. Qual servir aqui foi MEDIDO na pagina gerada, nao suposto:
   o post-processing "chrome do tutorial" acrescenta um `:root{--bg:#15161b}`
   INCONDICIONAL depois do CSS base do explorador, e o <html> sai SEM
   `data-theme`. Logo estas paginas de Fundamentos sao SEMPRE escuras — nao ha
   toggle, e nao ha `prefers-color-scheme` em jogo. Default = variante escura;
   as regras `[data-theme=...]` ficam para o dia em que o chrome virar
   alternavel (custam 2 linhas e evitam a caixa branca no meio da pagina, que
   foi exatamente o defeito visto na 1a tentativa). */
.mfig{margin:1.5rem 0}
.mfig img{width:100%;max-width:780px;display:block;border-radius:6px}
.mfig .fig-light{display:none}
.mfig .fig-dark{display:block}
[data-theme="light"] .mfig .fig-light{display:block}
[data-theme="light"] .mfig .fig-dark{display:none}
.mfig figcaption{max-width:780px}
.mfig pre,.mrepro pre{overflow-x:auto}
</style>

<h2 class="sec"><span data-l="pt">As cinco figuras</span><span data-l="en">The five figures</span></h2>
<p class="intro"><span data-l="pt">Geradas por <code>scripts/manual_figs.py</code> a partir do
store; o gate <code>--check</code> re-renderiza num tempor&aacute;rio e exige os 11 artefatos
<b>byte-id&ecirc;nticos</b>. Cada figura carrega <code>variaveis</code>,
<code>como_ler</code> e, onde couber, <code>ressalva</code> no
<code>numbers.json</code>.</span><span data-l="en">Generated by
<code>scripts/manual_figs.py</code> from the store; the <code>--check</code> gate re-renders into a
temp dir and requires all 11 artefacts <b>byte-identical</b>. Each figure carries
<code>variaveis</code>, <code>como_ler</code> and, where relevant, <code>ressalva</code> in
<code>numbers.json</code>.</span></p>
<figure class="mfig"><img class="fig-light" src="../../docs/MANUAL_BAS_V2/figs/fig1_anatomia.svg" alt="anatomia da curva"><img class="fig-dark" src="../../docs/MANUAL_BAS_V2/figs/fig1_anatomia-dark.svg" alt="anatomia da curva">
<figcaption><b>1</b> &mdash; <span data-l="pt">anatomia da curva: pat&atilde;o, joelho e piso saem da
f&iacute;sica. O piso &eacute; a comporta de auto-travamento, n&atilde;o um ajuste. <i>Caso escolhido
por regra determin&iacute;stica para EXIBIR a anatomia &mdash; &eacute; um caso bem ajustado, n&atilde;o
um caso m&eacute;dio; o n&uacute;mero para julgar o modelo &eacute; a mediana.</i></span>
<span data-l="en">curve anatomy: plateau, knee and floor come from physics. The floor is the
self-locking gate, not a fit. <i>Case picked by a deterministic rule to SHOW the anatomy &mdash; it is
a well-fitted case, not an average one; judge the model by the median.</i></span></figcaption></figure>
<figure class="mfig"><img class="fig-light" src="../../docs/MANUAL_BAS_V2/figs/fig2_decomposicao.svg" alt="decomposicao por mecanismo"><img class="fig-dark" src="../../docs/MANUAL_BAS_V2/figs/fig2_decomposicao-dark.svg" alt="decomposicao por mecanismo">
<figcaption><b>2</b> &mdash; <span data-l="pt">decomposi&ccedil;&atilde;o: a espessura de cada faixa
&eacute; quanto aquele mecanismo j&aacute; tirou; a soma fecha <b>exatamente</b> com 1&minus;F/F&#8320;.
A previs&atilde;o &eacute; atribu&iacute;vel.</span><span data-l="en">decomposition: each band's
thickness is how much that mechanism has taken; the sum closes <b>exactly</b> with
1&minus;F/F&#8320;. The prediction is attributable.</span></figcaption></figure>
<figure class="mfig"><img class="fig-light" src="../../docs/MANUAL_BAS_V2/figs/fig3_painel.svg" alt="painel das 202 curvas"><img class="fig-dark" src="../../docs/MANUAL_BAS_V2/figs/fig3_painel-dark.svg" alt="painel das 202 curvas">
<figcaption><b>3</b> &mdash; <span data-l="pt">as 202 curvas: MAE &times; res.m&aacute;x. S&oacute; o
que cai no ret&acirc;ngulo cumpriu a meta; todo ponto est&aacute; acima da diagonal (o pico &eacute;
&ge; a m&eacute;dia, por defini&ccedil;&atilde;o).</span><span data-l="en">the 202 curves: MAE
&times; maxerr. Only what falls inside the box met the goal; every point sits above the diagonal
(the peak is &ge; the mean, by definition).</span></figcaption></figure>
<figure class="mfig"><img class="fig-light" src="../../docs/MANUAL_BAS_V2/figs/fig4_tornado.svg" alt="tornado de sensibilidade"><img class="fig-dark" src="../../docs/MANUAL_BAS_V2/figs/fig4_tornado-dark.svg" alt="tornado de sensibilidade">
<figcaption><b>4</b> &mdash; <span data-l="pt">sensibilidade OAT: as barras cinza t&ecirc;m
sensibilidade nula e est&atilde;o <b>travadas no c&oacute;digo</b> &mdash; par&acirc;metro que
n&atilde;o move nada n&atilde;o &eacute; grau de liberdade escondido.</span>
<span data-l="en">OAT sensitivity: grey bars have zero sensitivity and are <b>locked in code</b>
&mdash; a parameter that moves nothing is not a hidden degree of freedom.</span></figcaption></figure>
<figure class="mfig"><img class="fig-light" src="../../docs/MANUAL_BAS_V2/figs/fig5_formas_fontes.svg" alt="formas x fontes"><img class="fig-dark" src="../../docs/MANUAL_BAS_V2/figs/fig5_formas_fontes-dark.svg" alt="formas x fontes">
<figcaption><b>5</b> &mdash; <span data-l="pt">formas &times; fontes: leia por LINHA &mdash; linha
cheia &eacute; forma que reaparece em bancadas independentes. O que ela n&atilde;o mostra, de
prop&oacute;sito, &eacute; o VALOR das constantes: essa &eacute; a outra metade da tese.</span>
<span data-l="en">shapes &times; sources: read by ROW &mdash; a full row is a shape that recurs on
independent rigs. What it deliberately does not show is the constants' VALUES: that is the other
half of the thesis.</span></figcaption></figure>

<h2 class="sec"><span data-l="pt">Regenerar</span><span data-l="en">Regenerate</span></h2>
<pre><code>py -3.12 New_Theory/parallel_batch.py --workers 6 --store
py -3.12 -m bolt_analysis_studio.validation.report
py -3.12 New_Theory/build_variable_explorer.py
py -3.12 scripts/manual_figs.py
py -3.12 scripts/manual_figs.py --check</code></pre>
'''),

    # ---------------------------------------------------------------- Guia de uso
    dict(
        slug="usage",
        nav_pt="Guia de uso do programa", nav_en="How to use the program",
        title_pt="Guia de uso do programa", title_en="How to use the program",
        hook_pt="do lançamento ao resultado, passo a passo",
        hook_en="from launch to result, step by step",
        body='''
<div class="sub"><span data-l="pt">As outras páginas explicam o MODELO. Esta explica o
PROGRAMA (Bolt Analysis Studio) &mdash; como montar uma junta, rodar e ler o resultado, com os nomes
reais de abas e botões.</span><span data-l="en">The other pages explain the MODEL. This one explains
the PROGRAM (Bolt Analysis Studio) &mdash; how to build a joint, run it and read the result, with the
real tab and button names.</span></div>

<div class="panel" style="border-color:var(--accent)">
<span data-l="pt">&#128247; <b>Prefere ver <a href="../tutorial_uso/index.html">prints reais de cada tela</a>?</b>
O tutorial visual percorre este mesmo fluxo em telas de verdade do app, do lançamento ao relatório.</span>
<span data-l="en">&#128247; <b>Prefer <a href="../tutorial_uso/index.html">real screenshots of every screen</a>?</b>
The visual tutorial walks this same flow on actual app screens, from launch to report.</span></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">1. Lançar</span><span data-l="en">1. Launch</span></h2>
<ul class="refs">
<li><code>python run_app.py</code> &mdash; <span data-l="pt">chrome V2 (shell CAE estilo Abaqus; engine energético) &mdash; <b>padrão</b>.</span><span data-l="en">V2 chrome (Abaqus-style CAE shell; energetic engine) &mdash; <b>default</b>.</span></li>
<li><code>python run_app.py --v1</code> &mdash; <span data-l="pt">janela clássica V1 (7 abas: I/O, MSD Builder, Solver, Results&hellip;) &mdash; fallback.</span><span data-l="en">classic V1 window (7 tabs: I/O, MSD Builder, Solver, Results&hellip;) &mdash; fallback.</span></li>
<li><code>python run_app.py --builder</code> &mdash; <span data-l="pt">só o MSD Model Builder.</span><span data-l="en">MSD Model Builder only.</span></li>
<li><code>python -m bolt_analysis_studio.calibration.server</code> &mdash; <span data-l="pt">servidor do tuner de calibração; abra <code>http://localhost:8765/</code> (cliente fino, engine real).</span><span data-l="en">calibration tuner server; open <code>http://localhost:8765/</code> (thin client, real engine).</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">2. O fluxo</span><span data-l="en">2. The flow</span></h2>
<svg viewBox="0 0 640 300" class="schema" xmlns="http://www.w3.org/2000/svg" role="img">
<defs><marker id="ar" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
<path d="M0,0 L7,3 L0,6 Z" fill="var(--accent)"/></marker></defs>
<g font-family="'Segoe UI',sans-serif" font-size="12">
<rect class="box" x="20" y="20" width="150" height="44" rx="8"/><text x="95" y="38" text-anchor="middle" fill="var(--ink)" font-weight="600">Nova Análise</text><text x="95" y="54" text-anchor="middle" fill="var(--muted)" font-size="10.5">wizard (preset de junta)</text>
<rect class="box" x="20" y="98" width="150" height="44" rx="8"/><text x="95" y="116" text-anchor="middle" fill="var(--ink)" font-weight="600">MSD Builder</text><text x="95" y="132" text-anchor="middle" fill="var(--muted)" font-size="10.5">PropertyInspector</text>
<rect class="box" x="20" y="176" width="150" height="44" rx="8"/><text x="95" y="194" text-anchor="middle" fill="var(--ink)" font-weight="600">Solver</text><text x="95" y="210" text-anchor="middle" fill="var(--muted)" font-size="10.5">configurar + executar</text>
<rect class="box" x="20" y="254" width="150" height="36" rx="8"/><text x="95" y="276" text-anchor="middle" fill="var(--ink)" font-weight="600">Results</text>
<rect class="box" x="360" y="98" width="260" height="44" rx="8"/><text x="490" y="116" text-anchor="middle" fill="var(--ink)" font-weight="600">Loading / Contact</text><text x="490" y="132" text-anchor="middle" fill="var(--muted)" font-size="10.5">F0, amplitude, freq, ciclos, &mu;, lubrif. (fonte única)</text>
<rect class="box" x="360" y="254" width="260" height="36" rx="8"/><text x="490" y="276" text-anchor="middle" fill="var(--ink)" font-weight="600">Calibrate Model&hellip; · Validation</text>
<line x1="95" y1="64" x2="95" y2="96" stroke="var(--accent)" stroke-width="2" marker-end="url(#ar)"/>
<line x1="95" y1="142" x2="95" y2="174" stroke="var(--accent)" stroke-width="2" marker-end="url(#ar)"/>
<line x1="95" y1="220" x2="95" y2="252" stroke="var(--accent)" stroke-width="2" marker-end="url(#ar)"/>
<line x1="170" y1="120" x2="358" y2="120" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="170" y1="272" x2="358" y2="272" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="4 3"/>
</g></svg>
<ol class="steps">
<li><span data-l="pt"><b>Nova Análise</b> (File &rarr; wizard de 5 páginas): escolha o preset de junta; ele gera um modelo inicial editável (já com o GROUND no topo da cadeia).</span><span data-l="en"><b>New Analysis</b> (File &rarr; 5-page wizard): pick a joint preset; it generates an editable starter model (GROUND already at the top of the chain).</span></li>
<li><span data-l="pt"><b>MSD Builder &rarr; PropertyInspector</b> é a FONTE ÚNICA da configuração. Aba <b>Loading</b>: tipo de carga (TRANSVERSE/&hellip;), F0, amplitude (&delta; ou F_amp), frequência, ciclos, &Delta;T. Aba <b>Contact</b>: atrito &mu;, lubrificação, diâmetro, passo. (No modo Junker use <b>displacement</b> + &delta;.)</span><span data-l="en"><b>MSD Builder &rarr; PropertyInspector</b> is the SINGLE SOURCE of the setup. <b>Loading</b> tab: load type (TRANSVERSE/&hellip;), F0, amplitude (&delta; or F_amp), frequency, cycles, &Delta;T. <b>Contact</b> tab: friction &mu;, lubrication, diameter, pitch. (For Junker use <b>displacement</b> + &delta;.)</span></li>
<li><span data-l="pt"><b>&#9654; Send to Solver</b> exporta o modelo e troca para a aba Solver (que mostra o resumo do carregamento em modo leitura).</span><span data-l="en"><b>&#9654; Send to Solver</b> exports the model and switches to the Solver tab (which shows a read-only loading summary).</span></li>
<li><span data-l="pt"><b>Solver</b>: confirme e execute a análise.</span><span data-l="en"><b>Solver</b>: confirm and run the analysis.</span></li>
<li><span data-l="pt"><b>Results</b>: sub-abas <b>Summary</b>, <b>Model Analysis</b>, <b>Plot View</b> (curva F/F0, decaimento, decomposição por mecanismo), <b>Miner's Rule</b> e <b>Diagnostics</b>.</span><span data-l="en"><b>Results</b>: sub-tabs <b>Summary</b>, <b>Model Analysis</b>, <b>Plot View</b> (F/F0 curve, decay, mechanism decomposition), <b>Miner's Rule</b> and <b>Diagnostics</b>.</span></li>
</ol>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">3. Calibrar e validar</span><span data-l="en">3. Calibrate and validate</span></h2>
<p><span data-l="pt"><b>Calibrar</b>: em Results, <b>&#9881; Calibrate Model&hellip;</b> abre o diálogo (ajusta &mu; e overrides V2 contra uma curva de referência com janela de trim). Para explorar constantes físicas ao vivo, use o <b>tuner</b> (servidor acima): o HTML é um cliente fino que faz POST em <code>/simulate</code> e <code>/calibrate</code> no engine real &mdash; nada de física em JS.</span>
<span data-l="en"><b>Calibrate</b>: in Results, <b>&#9881; Calibrate Model&hellip;</b> opens the dialog (fits &mu; and V2 overrides against a reference curve with a trim window). To explore physical constants live, use the <b>tuner</b> (server above): the HTML is a thin client that POSTs to <code>/simulate</code> and <code>/calibrate</code> on the real engine &mdash; no physics in JS.</span></p>
<p><span data-l="pt"><b>Validar</b>: o módulo <b>Results &rarr; Validation</b> traz os 128 casos consultáveis; <b>Abrir no Model/Run</b> monta exatamente o caso escolhido (a mesma <a href="concept_gallery.html">galeria de validação</a> deste guia).</span>
<span data-l="en"><b>Validate</b>: the <b>Results &rarr; Validation</b> module lists the 128 consultable cases; <b>Open in Model/Run</b> builds the chosen case exactly (the same <a href="concept_gallery.html">validation gallery</a> as in this guide).</span></p>
<p class="intro"><span data-l="pt">V1 (7 abas) cuida de I/O e montagem de matrizes; o <b>V2</b> (este guia) é o engine energético (DynamicStiffnessAnalyzer) + o chrome CAE. Cada campo que você edita aqui está documentado nas páginas de variáveis.</span>
<span data-l="en">V1 (7 tabs) handles I/O and matrix assembly; <b>V2</b> (this guide) is the energetic engine (DynamicStiffnessAnalyzer) + the CAE chrome. Every field you edit here is documented in the variable pages.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 1
    dict(
        slug="not-a-fit",
        nav_pt="1 · Não é um fit", nav_en="1 · Not a fit",
        title_pt="Isto não é um ajuste de curva", title_en="This is not a curve fit",
        hook_pt="por que o modelo PREVÊ, não interpola",
        hook_en="why the model PREDICTS rather than interpolates",
        widget="predict_liu2025",
        body='''
<div class="sub"><span data-l="pt">O afrouxamento é a evolução de um modelo físico &mdash; no
gráfico abaixo a LINHA CHEIA é a saída do modelo, a LINHA TRACEJADA é uma interpolação ajustada a
UM ensaio (0.25 mm) e os PONTOS são medidas de um estudo independente (Liu 2025). Troque a
amplitude: a interpolação só acerta onde foi ajustada; a MESMA física PREVÊ todas as
condições.</span><span data-l="en">Loosening is the evolution of a physical model &mdash; in the
plot below the SOLID line is the model output, the DASHED line is an interpolation fitted to ONE
test (0.25 mm), and the DOTS are measurements from an independent study (Liu 2025). Switch the
amplitude: the interpolation is right only where it was fitted; the SAME physics PREDICTS every
condition.</span></div>

<div id="cw"></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Fit x modelo físico</span><span data-l="en">Fit vs physical model</span></h2>
<p><span data-l="pt">Um <b>ajuste de curva</b> escolhe coeficientes de uma função genérica (ex.:
um polinômio ou exponencial) para passar pelos pontos de UM ensaio. Ele descreve aquele
ensaio, mas não sabe física: mude a pré-carga, a amplitude ou o material e os coeficientes
não valem mais &mdash; é preciso re-ajustar.</span>
<span data-l="en">A <b>curve fit</b> picks coefficients of a generic function (e.g. a polynomial
or exponential) to pass through the points of ONE test. It describes that test but knows no
physics: change the preload, amplitude or material and the coefficients no longer hold &mdash;
you must re-fit.</span></p>
<p><span data-l="pt">Aqui é o contrário. O afrouxamento é resolvido por um <b>modelo
massa-mola-amortecedor</b> (próxima página) cujas constantes têm significado físico e
<b>procedência declarada</b>. Por isso ele <b>prevê</b>: no gráfico acima, UMA configuração
física acerta os pontos medidos de SEIS amplitudes diferentes SEM re-ajustar &mdash; um ajuste de
curva precisaria de seis conjuntos de coeficientes. O MAE por amplitude é mostrado honestamente
(não é perfeito).</span>
<span data-l="en">Here it is the opposite. Loosening is solved by a <b>mass-spring-damper
model</b> (next page) whose constants carry physical meaning and <b>declared provenance</b>.
That is why it <b>predicts</b>: in the plot above, ONE physical configuration lands on the
measured points of SIX different amplitudes WITHOUT re-fitting &mdash; a curve fit would need six
separate coefficient sets. The MAE per amplitude is shown honestly (not perfect).</span></p>
<p class="intro"><span data-l="pt">Este é um estudo entre muitos: a <a href="concept_gallery.html">galeria de
validação</a> confronta o modelo com as {{N_CURVAS}} curvas de {{N_FONTES}} aparatos independentes.</span>
<span data-l="en">This is one study among many: the <a href="concept_gallery.html">validation gallery</a>
confronts the model with all {{N_CURVAS}} curves from {{N_FONTES}} independent apparatuses.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Seis provas de que é modelo, não interpolação</span>
<span data-l="en">Six tests that this is a model, not interpolation</span></h2>
<ul class="refs">
<li><span data-l="pt"><b>1. Prevê condições não medidas.</b> No gráfico acima, UMA configuração física
acerta as 6 amplitudes de Liu 2025. Uma interpolação precisaria dos pontos de cada amplitude para
existir.</span><span data-l="en"><b>1. Predicts unmeasured conditions.</b> In the plot above, ONE
physical configuration lands on all 6 Liu 2025 amplitudes. An interpolation would need the points of
each amplitude to exist at all.</span></li>
<li><span data-l="pt"><b>2. A interpolação falha fora do ajuste.</b> A linha tracejada acima é ajustada
ao ensaio de 0.25 mm: o MAE dela vai de <b>0.00</b> em 0.25 mm a <b>0.20</b> em 0.80 mm, enquanto o
do modelo fica em 0.05&ndash;0.10 em todas. Fitar uma curva não é prever as outras.</span>
<span data-l="en"><b>2. Interpolation fails off its fit.</b> The dashed line above is fitted to the
0.25 mm test: its MAE goes from <b>0.00</b> at 0.25 mm to <b>0.20</b> at 0.80 mm, while the model's
stays 0.05&ndash;0.10 throughout. Fitting one curve is not predicting the others.</span></li>
<li><span data-l="pt"><b>3. Transfere entre rigs e tamanhos.</b> As MESMAS formas preveem de
<a href="study_bauer_2024.html">M8 (Bauer, ~20 kN)</a> a <a href="study_karlsen_2022.html">M30/M42
(Karlsen, ~500 kN)</a> &mdash; ~5&times; em diâmetro, ~25&times; em carga. Uma interpolação de um
tamanho não vale para outro.</span><span data-l="en"><b>3. Transfers across rigs and sizes.</b> The
SAME forms predict from <a href="study_bauer_2024.html">M8 (Bauer, ~20 kN)</a> to
<a href="study_karlsen_2022.html">M30/M42 (Karlsen, ~500 kN)</a> &mdash; ~5&times; in diameter,
~25&times; in load. An interpolation of one size does not hold for another.</span></li>
<li><span data-l="pt"><b>4. Uma equação, formas qualitativamente diferentes.</b> Runaway, S-curve
(auto-travamento) e platô&rarr;colapso (incubação) saem da MESMA física mudando só entradas físicas
&mdash; veja os 3 cenários na <a href="concept_anatomy.html">anatomia da curva</a>. Uma interpolação
tem uma forma só.</span><span data-l="en"><b>4. One equation, qualitatively different shapes.</b>
Runaway, S-curve (self-locking) and plateau&rarr;collapse (incubation) all come from the SAME physics
by changing only physical inputs &mdash; see the 3 scenarios in the
<a href="concept_anatomy.html">curve anatomy</a>. An interpolation has a single shape.</span></li>
<li><span data-l="pt"><b>5. Decompõe em mecanismos nomeados.</b> A perda é atribuída a
embedding/creep/desgaste/afrouxamento (leis de Norton, Archard, two-factor) &mdash; veja
<a href="concept_mechanisms.html">estado + mecanismos</a>. Uma interpolação não tem mecanismos, só
coeficientes.</span><span data-l="en"><b>5. Decomposes into named mechanisms.</b> The loss is
attributed to embedding/creep/wear/loosening (Norton, Archard, two-factor laws) &mdash; see
<a href="concept_mechanisms.html">state + mechanisms</a>. An interpolation has no mechanisms, only
coefficients.</span></li>
<li><span data-l="pt"><b>6. Fecha o balanço de energia.</b> O modelo satisfaz W_ext + &Delta;U =
&Sigma; W_diss (residual ~0) &mdash; veja <a href="concept_energy.html">energia</a>. Uma
interpolação não conserva nada; é uma linha.</span><span data-l="en"><b>6. Closes the energy
balance.</b> The model satisfies W_ext + &Delta;U = &Sigma; W_diss (residual ~0) &mdash; see
<a href="concept_energy.html">energy</a>. An interpolation conserves nothing; it is just a
line.</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">O paradigma de três camadas</span><span data-l="en">The three-layer paradigm</span></h2>
<ul class="refs">
<li><span data-l="pt"><b>Analítica</b> &mdash; Hooke (rigidez do parafuso k_b), Coulomb (atrito),
hélice (rotação&harr;pré-carga), conservação de energia.</span>
<span data-l="en"><b>Analytical</b> &mdash; Hooke (bolt stiffness k_b), Coulomb (friction), helix
(rotation&harr;preload), energy conservation.</span></li>
<li><span data-l="pt"><b>Empírica</b> &mdash; leis de literatura NOMEADAS: Norton (embedding),
Norton-Bailey (creep log-t), Archard (desgaste), Greenwood-Williamson (softening),
Cattaneo-Mindlin (slip), Su-N/Goodman (fadiga). Não são curvas livres: são leis publicadas.</span>
<span data-l="en"><b>Empirical</b> &mdash; NAMED literature laws: Norton (embedding), Norton-Bailey
(log-t creep), Archard (wear), Greenwood-Williamson (softening), Cattaneo-Mindlin (slip),
Su-N/Goodman (fatigue). Not free curves: published laws.</span></li>
<li><span data-l="pt"><b>Constantes com procedência</b> &mdash; cada constante é medida, de handbook,
lida de uma feature do dado, ou fitada-neste-rig, com a procedência <b>declarada</b>. Desde o
Estágio B <b>não há nenhum multiplicador adimensional livre</b>.</span>
<span data-l="en"><b>Constants with provenance</b> &mdash; each constant is measured, handbook, read
from a data feature, or fitted-this-rig, with the provenance <b>declared</b>. Since Stage B
there are <b>no free dimensionless multipliers</b>.</span></li>
</ul>
<p class="intro"><span data-l="pt">Doutrina (reconfirmada 5x): <b>"formas transferem cross-rig;
níveis/constantes são per-rig"</b>. A forma (o mecanismo, o expoente, o acoplamento) é física e
transferível; a constante que a escala é medida por rig. Ver a página <a href="concept_methodology.html">Metodologia</a>.</span>
<span data-l="en">Doctrine (reconfirmed 5x): <b>"forms transfer cross-rig; levels/constants are
per-rig"</b>. The form (mechanism, exponent, coupling) is physical and transferable; the constant
that scales it is measured per rig. See the <a href="concept_methodology.html">Methodology</a> page.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 2
    dict(
        slug="msd-model",
        nav_pt="2 · Modelo MSD", nav_en="2 · MSD model",
        title_pt="O modelo massa-mola-amortecedor", title_en="The mass-spring-damper model",
        hook_pt="a equação de movimento e a cadeia da junta",
        hook_en="the equation of motion and the joint chain",
        body='''
<div class="panel">
<h2 class="sec"><span data-l="pt">Equação de movimento</span><span data-l="en">Equation of motion</span></h2>
<p><span data-l="pt">A junta é um sistema de <b>massa-mola-amortecedor</b> de 3 graus de liberdade
(x, y, &theta;). A cada ciclo o modelo resolve:</span>
<span data-l="en">The joint is a 3-DOF <b>mass-spring-damper</b> system (x, y, &theta;). Each cycle the
model solves:</span></p>
<div class="eq">[M]&middot;x&Prime; + [C(s)]&middot;x&prime; + [K(s)]&middot;x = F(t)</div>
<p class="intro"><span data-l="pt">x&Prime; = aceleração, x&prime; = velocidade, x = deslocamento.
[M] massa efetiva; [C] amortecimento de Rayleigh (&alpha;[M]+&beta;[K]); [K(s)] rigidez;
F(t) a carga cíclica (transversal e/ou axial). Os graus x, y são translações; &theta; é a rotação
da porca (o que afrouxa).</span>
<span data-l="en">x&Prime; = acceleration, x&prime; = velocity, x = displacement. [M] effective mass;
[C] Rayleigh damping (&alpha;[M]+&beta;[K]); [K(s)] stiffness; F(t) the cyclic load (transverse
and/or axial). The x, y DOFs are translations; &theta; is the nut rotation (what loosens).</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">A cadeia física da junta</span><span data-l="en">The joint's physical chain</span></h2>
<svg class="schema" viewBox="0 0 660 210" role="img" aria-label="MSD chain">
  <defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="var(--accent)"/></marker></defs>
  <!-- ground -->
  <line x1="26" y1="20" x2="26" y2="150" stroke="var(--muted)" stroke-width="2"/>
  <line x1="14" y1="30" x2="26" y2="18" stroke="var(--muted)"/><line x1="14" y1="55" x2="26" y2="43" stroke="var(--muted)"/>
  <line x1="14" y1="80" x2="26" y2="68" stroke="var(--muted)"/><line x1="14" y1="105" x2="26" y2="93" stroke="var(--muted)"/>
  <line x1="14" y1="130" x2="26" y2="118" stroke="var(--muted)"/>
  <!-- spring k_b (zigzag) -->
  <polyline points="26,60 60,60 72,44 96,76 120,44 144,76 168,44 186,60 210,60"
    fill="none" stroke="var(--ink)" stroke-width="2"/>
  <text class="lab" x="105" y="34" text-anchor="middle">k_b = E&middot;A_s / L</text>
  <!-- mass block -->
  <rect class="box" x="210" y="36" width="86" height="48" rx="5"/>
  <text x="253" y="65" text-anchor="middle" font-size="13">massa m</text>
  <!-- damper -->
  <line x1="60" y1="115" x2="120" y2="115" stroke="var(--ink)" stroke-width="2"/>
  <rect class="box" x="120" y="104" width="34" height="22"/>
  <line x1="137" y1="115" x2="210" y2="115" stroke="var(--ink)" stroke-width="2"/>
  <line x1="210" y1="84" x2="210" y2="126" stroke="var(--ink)" stroke-width="2"/>
  <line x1="26" y1="84" x2="26" y2="126" stroke="var(--muted)"/>
  <text class="lab" x="120" y="146" text-anchor="middle">[C] amortecimento / damping</text>
  <!-- force -->
  <line class="edge" x1="360" y1="60" x2="300" y2="60"/>
  <text x="368" y="64" font-size="13">F(t)</text>
  <!-- chain mapping -->
  <text class="lab" x="26" y="176" >GROUND</text>
  <text class="lab" x="120" y="176" text-anchor="middle">parafuso k_b / bolt</text>
  <text class="lab" x="253" y="176" text-anchor="middle">rosca+helice / thread+helix</text>
  <text class="lab" x="430" y="176" text-anchor="middle">apoio &mu;/wear &middot; membro</text>
  <text class="lab" x="330" y="198" text-anchor="middle">a tribologia (atrito, wear) vive nos CONTATOS &mdash; tribology lives in the CONTACTS</text>
</svg>
<p><span data-l="pt">A cadeia: <code>GROUND &mdash; parafuso (mola k_b) &mdash; rosca (helice
&lambda;, atrito de filete) &mdash; apoio (&mu;, wear) &mdash; membro(s)</code>. O parafuso é a mola
principal (<code>k_b = E&middot;A_s/L_eff</code>); a hélice (<code>&beta; = arctan(p/&pi;d&#8322;)</code>)
é o ÚNICO acoplamento entre o eixo axial e a rotação.</span>
<span data-l="en">The chain: <code>GROUND &mdash; bolt (spring k_b) &mdash; thread (helix &lambda;,
flank friction) &mdash; bearing (&mu;, wear) &mdash; member(s)</code>. The bolt is the main spring
(<code>k_b = E&middot;A_s/L_eff</code>); the helix (<code>&beta; = arctan(p/&pi;d&#8322;)</code>) is
the ONLY coupling between the axial axis and rotation.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Rigidez dinâmica [K(s)] e a redução quase-estática</span>
<span data-l="en">Dynamic stiffness [K(s)] and the quasi-static reduction</span></h2>
<p><span data-l="pt">A rigidez <b>não é constante</b>: <code>[K(s)]</code> é reavaliada a cada ciclo
(softening de Greenwood-Williamson &mdash; a rigidez de contato cai conforme a pré-carga F0 cai).
O <code>(s)</code> é o <b>vetor de estado lento</b> (próxima página). Dentro de um ciclo o problema
é dinâmico rápido; entre ciclos, o modelo é <b>quase-estático</b>: resolve o slip e a perda de
pré-carga por ciclo e integra o estado lento por milhares de ciclos.</span>
<span data-l="en">Stiffness is <b>not constant</b>: <code>[K(s)]</code> is re-evaluated each cycle
(Greenwood-Williamson softening &mdash; contact stiffness falls as preload F0 falls). The
<code>(s)</code> is the <b>slow-state vector</b> (next page). Within a cycle the problem is fast and
dynamic; between cycles the model is <b>quasi-static</b>: it resolves the per-cycle slip and preload
loss and integrates the slow state over thousands of cycles.</span></p>
<p class="intro"><span data-l="pt">É por isso que variáveis puramente inerciais (<code>m_x</code>,
<code>rayleigh_*</code>) quase não movem a curva de afrouxamento: a evolução lenta é ditada pelos
mecanismos de perda, não pelo transiente inercial de um ciclo.</span>
<span data-l="en">That is why purely inertial variables (<code>m_x</code>, <code>rayleigh_*</code>)
barely move the loosening curve: the slow evolution is set by the loss mechanisms, not by a single
cycle's inertial transient.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 3
    dict(
        slug="mechanisms",
        nav_pt="3 · Estado + mecanismos", nav_en="3 · State + mechanisms",
        title_pt="Estado lento e os mecanismos de perda", title_en="Slow state and the loss mechanisms",
        hook_pt="a curva = soma de mecanismos físicos (toggle)",
        hook_en="the curve = sum of physical mechanisms (toggle)",
        widget="decomp",
        body='''
<div class="sub"><span data-l="pt">A curva de afrouxamento não é uma função ajustada: é a SOMA de
mecanismos físicos em paralelo. Ligue/desligue cada um para ver sua parcela.</span>
<span data-l="en">The loosening curve is not a fitted function: it is the SUM of physical mechanisms
in parallel. Toggle each to see its share.</span></div>

<div id="cw"></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">O vetor de estado lento</span><span data-l="en">The slow-state vector</span></h2>
<p><span data-l="pt">O que evolui ciclo a ciclo é um vetor de estado:</span>
<span data-l="en">What evolves cycle by cycle is a state vector:</span></p>
<div class="eq">s = ( F_0, &delta;_emb, &delta;_creep, &delta;_wear, &delta;_fret, &theta;_loose, D, D_fat, ... )</div>
<p><span data-l="pt">F_0 = pré-carga residual (o que medimos como F/F0); os <code>&delta;</code> são
profundidades (assentamento, creep, wear, fretting); <code>&theta;_loose</code> a rotação da porca;
<code>D</code> o dano de superfície. A cada ciclo, <b>seis mecanismos em paralelo</b> devolvem seu
<code>&Delta;F_0</code> vendo o MESMO F_0 de início (sem dependência de ordem); F_0 só muda depois de
somados todos os <code>&Delta;F_0</code>.</span>
<span data-l="en">F_0 = residual preload (what we read as F/F0); the <code>&delta;</code> are depths
(embedding, creep, wear, fretting); <code>&theta;_loose</code> the nut rotation; <code>D</code> the
surface damage. Each cycle, <b>six parallel mechanisms</b> return their <code>&Delta;F_0</code>
seeing the SAME start-of-cycle F_0 (no ordering dependence); F_0 only changes after all
<code>&Delta;F_0</code> are summed.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">As seis leis de perda (cada uma de literatura)</span>
<span data-l="en">The six loss laws (each from literature)</span></h2>
<ul class="refs">
<li><b>Embedding</b> (Norton) &mdash; <span class="mono">&delta;_emb(N)=&delta;&infin;(1&minus;e^(&minus;N/N_emb))</span></li>
<li><b>Creep</b> (Norton-Bailey) &mdash; <span class="mono">&delta;_creep=C_creep&middot;F_0&middot;ln(t/t_0+1)</span></li>
<li><b>Wear</b> (Archard) &mdash; <span class="mono">d_wear=(K/H)&middot;F_0&middot;4&middot;slip/A_contact</span></li>
<li><b>Rotational loosening</b> (two-factor) &mdash; <span class="mono">&Delta;&theta;&prop;(T_loose&minus;T_resist)</span> <span data-l="pt">(ver Acoplamento)</span><span data-l="en">(see Coupling)</span></li>
<li><b>Thread fretting</b> (axial) &mdash; <span class="mono">d_fret&prop;F_0&middot;A_F</span></li>
<li><b>Fatigue</b> (Su-N + Goodman) &mdash; <span class="mono">&Delta;D_fat=1/N_f</span> <span data-l="pt">(cliff de fratura)</span><span data-l="en">(fracture cliff)</span></li>
</ul>
<p><span data-l="pt">Os quatro mecanismos de "profundidade" convertem o recalque em perda pelo
<b>encurtamento da pilha</b>: <code>&Delta;F_0 = &minus;k_b&middot;&Delta;&delta;</code>. O afrouxamento
converte rotação via a hélice; a fadiga é um evento discreto. No gráfico acima, as quatro faixas
somam <b>exatamente</b> a perda total <code>1 &minus; F/F0</code> (linha tracejada).</span>
<span data-l="en">The four "depth" mechanisms convert settlement into loss by <b>shortening the
stack</b>: <code>&Delta;F_0 = &minus;k_b&middot;&Delta;&delta;</code>. Loosening converts rotation via
the helix; fatigue is a discrete event. In the plot above, the four bands sum <b>exactly</b> to the
total loss <code>1 &minus; F/F0</code> (dashed line).</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 4
    dict(
        slug="coupling",
        nav_pt="4 · Acoplamento", nav_en="4 · Coupling",
        title_pt="Acoplamento das equações", title_en="Coupling of the equations",
        hook_pt="hélice, two-factor e o laço de realimentação",
        hook_en="helix, two-factor and the feedback loop",
        widget="runaway",
        body='''
<div class="panel">
<h2 class="sec"><span data-l="pt">A hélice: o único acoplamento axial&harr;torsional</span>
<span data-l="en">The helix: the only axial&harr;torsional coupling</span></h2>
<p><span data-l="pt">Numa junta aparafusada, girar a porca muda a pré-carga e vice-versa &mdash; é a
<b>hélice</b> da rosca. Ela é o único termo fora da diagonal de <code>[K]</code> (acopla o eixo axial
ao grau de rotação &theta;). A conversão rotação&rarr;pré-carga usa o avanço por radiano:</span>
<span data-l="en">In a bolted joint, turning the nut changes the preload and vice-versa &mdash; that is
the thread <b>helix</b>. It is the only off-diagonal term of <code>[K]</code> (it couples the axial
axis to the rotation DOF &theta;). The rotation&rarr;preload conversion uses the lead per radian:</span></p>
<div class="eq">&Delta;F_0 = &minus;k_b &middot; (p / 2&pi;) &middot; &Delta;&theta;_loose &nbsp;&nbsp;&middot;&nbsp;&nbsp; &beta; = arctan( p / (&pi;&middot;d&#8322;) )</div>
<svg class="schema" viewBox="0 0 660 250" role="img" aria-label="helice">
<defs><marker id="hxb" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="var(--accent)"/></marker>
<marker id="hxt" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="var(--warn)"/></marker></defs>
<path class="fill" d="M100,190 L430,190 L430,80 Z"/>
<line stroke="var(--muted)" stroke-width="1.5" x1="100" y1="190" x2="430" y2="190"/>
<line stroke="var(--muted)" stroke-width="1.5" x1="430" y1="190" x2="430" y2="80"/>
<line stroke="var(--accent)" stroke-width="2.5" x1="100" y1="190" x2="430" y2="80"/>
<path d="M150,190 A50,50 0 0,0 148,174" fill="none" stroke="var(--muted)"/>
<text x="163" y="182" font-size="13" class="cplt">&beta;</text>
<rect x="250" y="128" width="26" height="16" rx="3" transform="rotate(-18 263 136)" fill="var(--accent)" fill-opacity=".35" stroke="var(--accent)"/>
<text x="265" y="212" text-anchor="middle" class="lab">1 volta = 2&pi;&middot;r &rarr; rota&ccedil;&atilde;o &theta;</text>
<text x="452" y="140" class="lab" font-size="12" transform="rotate(90 452 140)">avan&ccedil;o axial = passo p</text>
<text x="255" y="118" text-anchor="middle" class="lab" font-size="11">flanco da rosca</text>
<line class="edge" x1="486" y1="190" x2="486" y2="96" marker-end="url(#hxb)"/><text x="500" y="150" font-size="12">F_0, &delta;</text><text x="500" y="166" class="lab" font-size="11">axial</text>
<line stroke="var(--warn)" stroke-width="2" x1="100" y1="222" x2="360" y2="222" marker-end="url(#hxt)"/><text x="230" y="240" text-anchor="middle" class="lab">T, &theta; (tor&ccedil;&atilde;o)</text>
<rect class="box" x="470" y="30" width="176" height="52" rx="6"/><text x="558" y="52" text-anchor="middle" class="cplt" font-size="13">&Delta;&delta; = (p/2&pi;)&middot;&Delta;&theta;</text><text x="558" y="70" text-anchor="middle" font-size="12">&Delta;F_0 = &minus;k_b&middot;&Delta;&delta;</text>
</svg>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">A matriz [K(s)]: onde vivem os acoplamentos</span><span data-l="en">The [K(s)] matrix: where the couplings live</span></h2>
<svg class="schema" viewBox="0 0 660 320" role="img" aria-label="matriz K">
<text x="330" y="30" text-anchor="middle" class="lab">graus de liberdade (colunas) &mdash; u=axial &middot; &theta;=rota&ccedil;&atilde;o &middot; x=transversal</text>
<text x="248" y="60" text-anchor="middle" font-size="15">u</text><text x="348" y="60" text-anchor="middle" font-size="15">&theta;</text><text x="448" y="60" text-anchor="middle" font-size="15">x</text>
<text x="188" y="107" text-anchor="middle" font-size="15">u</text><text x="188" y="173" text-anchor="middle" font-size="15">&theta;</text><text x="188" y="239" text-anchor="middle" font-size="15">x</text>
<path class="brk" d="M208,68 h-8 v198 h8"/><path class="brk" d="M488,68 h8 v198 h-8"/>
<rect class="diag" x="200" y="72" width="96" height="60" rx="6"/><text x="248" y="107" text-anchor="middle">k_b</text>
<rect class="cpl" x="300" y="72" width="96" height="60" rx="6"/><text x="348" y="102" text-anchor="middle" class="cplt">k_b&middot;&lambda;</text><text x="348" y="120" text-anchor="middle" class="lab">h&eacute;lice</text>
<rect x="400" y="72" width="96" height="60" rx="6" stroke="var(--line)" fill="none"/><text x="448" y="107" text-anchor="middle" class="zero">0</text>
<rect class="cpl" x="200" y="138" width="96" height="60" rx="6"/><text x="248" y="168" text-anchor="middle" class="cplt">k_b&middot;&lambda;</text><text x="248" y="186" text-anchor="middle" class="lab">h&eacute;lice</text>
<rect class="diag" x="300" y="138" width="96" height="60" rx="6"/><text x="348" y="173" text-anchor="middle">k_&theta;</text>
<rect x="400" y="138" width="96" height="60" rx="6" stroke="var(--line)" fill="none"/><text x="448" y="173" text-anchor="middle" class="zero">0</text>
<rect x="200" y="204" width="96" height="60" rx="6" stroke="var(--line)" fill="none"/><text x="248" y="239" text-anchor="middle" class="zero">0</text>
<rect x="300" y="204" width="96" height="60" rx="6" stroke="var(--line)" fill="none"/><text x="348" y="239" text-anchor="middle" class="zero">0</text>
<rect class="diag" x="400" y="204" width="96" height="60" rx="6"/><text x="448" y="239" text-anchor="middle">k_tr</text>
<text x="524" y="96" font-size="13" class="cplt">(s)</text><text x="516" y="128" class="lab" font-size="11">amolece com</text><text x="516" y="144" class="lab" font-size="11">F_0&darr; (GW)</text>
<line class="dash" x1="514" y1="102" x2="298" y2="102"/>
<text x="330" y="300" text-anchor="middle" class="lab">A h&eacute;lice k_b&middot;&lambda; (&lambda; = p/2&pi;) &eacute; o &Uacute;NICO termo fora da diagonal &mdash; o resto &eacute; zero.</text>
</svg>
<p><span data-l="pt">A h&eacute;lice acopla o eixo axial (u) ao grau de rota&ccedil;&atilde;o (&theta;) &mdash; &eacute; o &uacute;nico termo fora da diagonal de <code>[K]</code>. A rigidez transversal (x) e as demais entradas cruzadas s&atilde;o nulas. O <code>(s)</code> marca a depend&ecirc;ncia do estado lento: <code>[K]</code> amolece conforme <code>F_0</code> cai (Greenwood-Williamson), fechando o la&ccedil;o abaixo.</span>
<span data-l="en">The helix couples the axial axis (u) to the rotation DOF (&theta;) &mdash; it is the only off-diagonal term of <code>[K]</code>. Transverse (x) stiffness and the other cross entries are zero. The <code>(s)</code> marks the slow-state dependence: <code>[K]</code> softens as <code>F_0</code> falls (Greenwood-Williamson), closing the loop below.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Two-factor: rigidez &times; hélice</span><span data-l="en">Two-factor: stiffness &times; helix</span></h2>
<p><span data-l="pt">O afrouxamento rotacional (mecanismo central) é o <b>produto de dois fatores</b>:</span>
<span data-l="en">Rotational loosening (the central mechanism) is the <b>product of two factors</b>:</span></p>
<div class="eq">T_loose = |( &Phi;_ax&middot;sin&beta;&middot;F_ax , &Phi;_tr&middot;cos&beta;&middot;F_tr )| &middot; d&#8322;/2
&nbsp;&nbsp; vs &nbsp;&nbsp; T_resist = &mu;&middot;F_0&middot;(...)</div>
<svg class="schema" viewBox="0 0 660 250" role="img" aria-label="two-factor">
<defs><marker id="tfa" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="var(--accent)"/></marker></defs>
<rect class="dash" x="110" y="80" width="220" height="120"/>
<line class="edge" x1="110" y1="200" x2="326" y2="200" marker-end="url(#tfa)"/><text x="218" y="220" text-anchor="middle" class="lab">&Phi;_tr&middot;cos&beta;&middot;F_tr</text>
<line class="edge" x1="110" y1="200" x2="110" y2="84" marker-end="url(#tfa)"/><text x="60" y="140" text-anchor="middle" class="lab" transform="rotate(-90 60 140)">&Phi;_ax&middot;sin&beta;&middot;F_ax</text>
<line stroke="var(--ok)" stroke-width="2.6" x1="110" y1="200" x2="322" y2="86"/><text x="232" y="118" class="cplt" fill="var(--ok)" font-size="13">L_total</text>
<rect class="box" x="378" y="86" width="118" height="48" rx="6"/><text x="437" y="108" text-anchor="middle" class="cplt">T_loose</text><text x="437" y="125" text-anchor="middle" class="lab" font-size="11">= L&middot;d&#8322;/2</text>
<text x="518" y="116" text-anchor="middle" font-size="18">&hArr;</text>
<rect class="box" x="540" y="86" width="110" height="48" rx="6"/><text x="595" y="108" text-anchor="middle">T_resist</text><text x="595" y="125" text-anchor="middle" class="lab" font-size="11">= &mu;&middot;F_0&middot;(&hellip;)</text>
<text x="437" y="172" text-anchor="middle" class="lab">se T_loose &gt; T_resist</text>
<line class="edge" x1="437" y1="180" x2="437" y2="206" marker-end="url(#tfa)"/>
<rect class="cpl" x="360" y="210" width="154" height="30" rx="6"/><text x="437" y="230" text-anchor="middle" class="cplt">a porca gira: &Delta;&theta; &gt; 0</text>
</svg>
<p><span data-l="pt"><b>Fator 1</b> = razão de rigidez <code>&Phi;_eff = k_b/(k_b+k_j(F_0))</code>, que
<b>SOBE conforme F_0 cai</b> (a junta amolece). <b>Fator 2</b> = projeção pela hélice
(<code>sin&beta;</code>/<code>cos&beta;</code>). Quando o torque de afrouxamento vence o resistivo
(<code>T_loose &gt; T_resist</code>), a porca gira e drena pré-carga.</span>
<span data-l="en"><b>Factor 1</b> = stiffness ratio <code>&Phi;_eff = k_b/(k_b+k_j(F_0))</code>, which
<b>RISES as F_0 falls</b> (the joint softens). <b>Factor 2</b> = helix projection
(<code>sin&beta;</code>/<code>cos&beta;</code>). When the loosening torque beats the resisting one
(<code>T_loose &gt; T_resist</code>), the nut turns and drains preload.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">O laço de realimentação</span><span data-l="en">The feedback loop</span></h2>
<svg class="schema" viewBox="0 0 640 210" role="img" aria-label="feedback loop">
  <defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="var(--accent)"/></marker></defs>
  <rect class="box" x="40" y="24" width="150" height="42" rx="6"/><text x="115" y="50" text-anchor="middle" font-size="13">F_0 (pre-carga)</text>
  <rect class="box" x="450" y="24" width="150" height="42" rx="6"/><text x="525" y="50" text-anchor="middle" font-size="13">[K(s)] softening GW</text>
  <rect class="box" x="450" y="150" width="150" height="42" rx="6"/><text x="525" y="176" text-anchor="middle" font-size="13">&Phi;_eff (Fator 1)</text>
  <rect class="box" x="40" y="150" width="150" height="42" rx="6"/><text x="115" y="171" text-anchor="middle" font-size="12">afrouxamento &Delta;&theta;</text><text x="115" y="185" text-anchor="middle" font-size="11" class="lab">loosening</text>
  <line class="edge" x1="190" y1="45" x2="448" y2="45"/><text class="edge-lab" x="320" y="38" text-anchor="middle">F_0 baixa &rarr; rigidez cai</text>
  <line class="edge" x1="525" y1="66" x2="525" y2="148"/><text class="edge-lab" x="600" y="110" text-anchor="middle">&Phi;=k_b/(k_b+k_j)</text>
  <line class="edge" x1="448" y1="171" x2="192" y2="171"/><text class="edge-lab" x="320" y="164" text-anchor="middle">two-factor &times; helice</text>
  <line class="edge" x1="115" y1="148" x2="115" y2="68"/><text class="edge-lab" x="115" y="112" text-anchor="middle">&Delta;F_0=&minus;k_b(p/2&pi;)&Delta;&theta;</text>
</svg>
<p><span data-l="pt">Este laço é a essência do modelo: F_0 cai &rarr; <code>[K(s)]</code> amolece &rarr;
<code>&Phi;_eff</code> sobe &rarr; o afrouxamento acelera &rarr; F_0 cai mais. Se nada o segura, vira um
<b>runaway até zero</b>. A física real tem um freio (o núcleo de stick auto-travado), que o modelo
captura como um <b>piso de arresto</b> &mdash; transformando o runaway numa <b>S-curve estável</b>.
Compare os dois no gráfico abaixo:</span>
<span data-l="en">This loop is the essence of the model: F_0 falls &rarr; <code>[K(s)]</code> softens &rarr;
<code>&Phi;_eff</code> rises &rarr; loosening accelerates &rarr; F_0 falls further. Unchecked, it becomes
a <b>runaway to zero</b>. Real physics has a brake (the self-locked stick core), which the model
captures as a <b>self-locking floor</b> &mdash; turning the runaway into a <b>stable S-curve</b>.
Compare the two below:</span></p>
<div id="cw"></div>
</div>
'''),

    # ---------------------------------------------------------------- 5
    dict(
        slug="energy",
        nav_pt="5 · Energia", nav_en="5 · Energy",
        title_pt="Balanço de energia e conservação", title_en="Energy balance and conservation",
        hook_pt="a perda como soma de dissipações físicas",
        hook_en="loss as a sum of physical dissipations",
        widget="energy",
        body='''
<div class="sub"><span data-l="pt">A perda de pré-carga não é postulada: cada mecanismo entrega uma
parcela FÍSICA, e o modelo fecha um balanço de energia rigoroso.</span>
<span data-l="en">Preload loss is not postulated: each mechanism delivers a PHYSICAL share, and the
model closes a rigorous energy balance.</span></div>

<div id="cw"></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Conservação de energia</span><span data-l="en">Energy conservation</span></h2>
<div class="eq">W_ext + &Delta;U_elastica = &Sigma; W_dissipada &nbsp;&nbsp;&middot;&nbsp;&nbsp; U(F) = F&sup2; / (2&middot;k_b)</div>
<p><span data-l="pt">O trabalho externo mais a variação da energia elástica armazenada na pilha
(<code>U=F&sup2;/2k_b</code>) igualam a soma das dissipações: embedding, creep, wear, afrouxamento,
fretting, fratura. O engine mantém esse budget a cada ciclo e expõe o <b>residual de conservação</b>
(&asymp; 0 no regime normal). Um ajuste de curva não teria &mdash; nem precisaria de &mdash; um balanço
de energia; um modelo físico tem.</span>
<span data-l="en">The external work plus the change in stored elastic energy (<code>U=F&sup2;/2k_b</code>)
equal the sum of dissipations: embedding, creep, wear, loosening, fretting, fracture. The engine
keeps this budget every cycle and exposes the <b>conservation residual</b> (&asymp; 0 in the normal
regime). A curve fit would not have &mdash; nor need &mdash; an energy balance; a physical model
does.</span></p>
<p class="intro"><span data-l="pt">Detalhe honesto: no regime agressivo de colapso por dano, a
energética de remoção abrasiva é fenomenológica e o residual degrada &mdash; registrado AS-IS (ver
Metodologia).</span>
<span data-l="en">Honest caveat: in the aggressive damage-collapse regime the abrasive-removal
energetics are phenomenological and the residual degrades &mdash; recorded AS-IS (see
Methodology).</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 6
    dict(
        slug="methodology",
        nav_pt="6 · Metodologia", nav_en="6 · Methodology",
        title_pt="Metodologia: procedência e falsificação", title_en="Methodology: provenance and falsification",
        hook_pt="como sabemos que a física é legítima",
        hook_en="how we know the physics is legitimate",
        body='''
<div class="panel">
<h2 class="sec"><span data-l="pt">Procedência por constante</span><span data-l="en">Provenance per constant</span></h2>
<p><span data-l="pt">Cada constante do modelo tem uma <b>classe de procedência declarada</b> &mdash; ela
NÃO é um botão livre ajustado ao dado:</span>
<span data-l="en">Every model constant has a <b>declared provenance class</b> &mdash; it is NOT a free
knob tuned to the data:</span></p>
<ul class="refs">
<li><span data-l="pt"><b>Medida</b> &mdash; ex.: atrito &mu; (Motosh de torque+F0), limite de fadiga (schaumann2015).</span><span data-l="en"><b>Measured</b> &mdash; e.g. friction &mu; (Motosh from torque+F0), fatigue limit (schaumann2015).</span></li>
<li><span data-l="pt"><b>Handbook</b> &mdash; ex.: <code>emb_depth</code> pela classe de rugosidade Rz (tabela f_Z da VDI 2230).</span><span data-l="en"><b>Handbook</b> &mdash; e.g. <code>emb_depth</code> from the Rz roughness class (VDI 2230 f_Z table).</span></li>
<li><span data-l="pt"><b>Lida do dado</b> &mdash; ex.: <code>emb_depth</code> implícito na queda inicial; expoentes lidos de sweeps.</span><span data-l="en"><b>Data-implied</b> &mdash; e.g. <code>emb_depth</code> implied by the early drop; exponents read from sweeps.</span></li>
<li><span data-l="pt"><b>Fitada-neste-rig</b> &mdash; ex.: <code>c_bend</code>, <code>W_conf_ref</code> (magnitude por par/rig; a FORMA transfere).</span><span data-l="en"><b>Fitted-this-rig</b> &mdash; e.g. <code>c_bend</code>, <code>W_conf_ref</code> (per pair/rig magnitude; the FORM transfers).</span></li>
</ul>
<p class="intro"><span data-l="pt">Nas páginas de variáveis, quando há uma banda medida, o gráfico
avisa se o valor sai dela &mdash; a proveniência é visível, não implícita.</span>
<span data-l="en">On the variable pages, when a measured band exists, the plot flags values that leave
it &mdash; provenance is visible, not implicit.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Falsificação e capabilities default-inertes</span><span data-l="en">Falsification and default-inert capabilities</span></h2>
<p><span data-l="pt">O modelo cresce por <b>falsificação</b>: quando uma predição (zero-refit) falha um
gate contra um dado, isso aponta uma <b>forma faltante</b> &mdash; não um coeficiente a ajustar. A
forma nova entra como uma <b>capability opt-in default-inerte</b>: com o valor default ela é
<b>bit-idêntica</b> ao motor sem a feature (garantido por teste). Ligar uma NÃO é fitar um tuner &mdash;
é suprir uma forma que uma falsificação exigiu, com um número de procedência declarada.</span>
<span data-l="en">The model grows by <b>falsification</b>: when a (zero-refit) prediction fails a gate
against data, that points to a <b>missing form</b> &mdash; not a coefficient to tune. The new form
enters as an <b>opt-in, default-inert capability</b>: at its default value it is <b>bit-identical</b>
to the engine without the feature (test-guaranteed). Turning one on is NOT fitting a tuner &mdash; it
supplies a form a falsification demanded, with a declared-provenance number.</span></p>
<p><span data-l="pt">No Estágio B, a antiga camada de 9 multiplicadores adimensionais foi
<b>removida</b>: o engine lê só constantes físicas. Isso é o oposto de um fit &mdash; não há ganho livre
para "encaixar" a curva.</span>
<span data-l="en">In Stage B, the old layer of 9 dimensionless multipliers was <b>removed</b>: the
engine reads only physical constants. This is the opposite of a fit &mdash; there is no free gain to
"snap" the curve into place.</span></p>
<p class="intro"><span data-l="pt">Doutrina central (reconfirmada 5x): <b>"formas transferem
cross-rig; níveis/constantes são per-rig"</b>. As páginas de variáveis marcam cada campo como
constante física, forma opt-in, modo ou numérico &mdash; a categoria diz o papel de cada um.</span>
<span data-l="en">Core doctrine (reconfirmed 5x): <b>"forms transfer cross-rig; levels/constants are
per-rig"</b>. The variable pages tag each field as physical constant, opt-in form, mode or numerical
&mdash; the category states each one's role.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- Cobertura & limitações
    dict(
        slug="coverage",
        nav_pt="Cobertura & limitações", nav_en="Coverage & limits",
        title_pt="Cobertura e limitações", title_en="Coverage and limits",
        hook_pt="o que o modelo ainda NÃO fecha — honestamente",
        hook_en="what the model does NOT yet close — honestly",
        body='''
<div class="sub"><span data-l="pt">Um modelo honesto declara onde falha. Esta página lista as
lacunas conhecidas &mdash; falsificações registradas e o que ainda falta &mdash; ao lado da página
<a href="concept_not-a-fit.html">Não é um fit</a>.</span><span data-l="en">An honest model states where
it fails. This page lists the known gaps &mdash; recorded falsifications and what is still missing
&mdash; alongside the <a href="concept_not-a-fit.html">Not a fit</a> page.</span></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Formas que faltam (falsificações)</span>
<span data-l="en">Missing forms (falsifications)</span></h2>
<p><span data-l="pt">Quando uma predição zero-refit falha um gate contra o dado, isso aponta uma FORMA
faltante &mdash; não um coeficiente a ajustar. As abertas:</span>
<span data-l="en">When a zero-refit prediction fails a gate against data, it points to a missing FORM
&mdash; not a coefficient to tune. The open ones:</span></p>
<ul class="refs">
<li><span data-l="pt"><b>Aceleração tardia &mdash; classe ENCERRADA em 2026-08-02 com três
falsificações</b> (21 curvas em 7 fontes). O dado desaba no fim <b>2&times; a 225&times; mais
rápido</b> que o modelo (razão entre as inclinações terminais), e três instrumentos independentes
apontam o mesmo estágio. Nenhum mecanismo do engine atual alcança isso, e agora sabemos por quê:
<b>(1)</b> toda a família de gates (incubação, conformação, regime de slip, auto-travamento,
gatilho de criticalidade) tem contradomínio (0,1] &mdash; só sabe <b>atrasar</b>, nunca acelerar,
o que é falsificação <b>por construção</b>, não por tentativa; <b>(2)</b> um amplificador guiado
pelo dano acumulado tem o sinal certo mas é <b>gradual demais</b> (piora o MAE em +53&nbsp;% a
+397&nbsp;%, porque para consertar o fim destrói o começo); <b>(3)</b> um amplificador com
interruptor tem sinal e perfil certos mas <b>não é constante por rig</b> (na mesma fonte, com o
mesmo valor, umas curvas melhoram e outras pioram). O quarto candidato &mdash; um relógio por
curva &mdash; está <b>bloqueado por dado</b>: essas curvas param por critério de protocolo, não
por falha, então não existe "fração de vida". As duas capacidades novas ficam no engine,
<b>desligadas por padrão</b>, à espera de dado que as sustente.</span>
<span data-l="en"><b>Late acceleration &mdash; class CLOSED on 2026-08-02 with three
falsifications</b> (21 curves across 7 sources). The data collapses at the end <b>2&times; to
225&times; faster</b> than the model, and three independent instruments point at the same stage.
No mechanism in the current engine reaches it, and we now know why: <b>(1)</b> the whole gate
family has range (0,1] &mdash; it can only <b>delay</b>, never accelerate, which is falsification
<b>by construction</b>; <b>(2)</b> a damage-driven amplifier has the right sign but is <b>too
gradual</b> (+53&nbsp;% to +397&nbsp;% MAE: fixing the end destroys the start); <b>(3)</b> a
switch-gated amplifier has the right sign and profile but <b>is not a per-rig constant</b> (same
source, same value: some curves improve, others worsen). The fourth candidate &mdash; a per-curve
clock &mdash; is <b>data-blocked</b>: these tests stop by protocol criterion, not by failure, so
there is no "fraction of life". Both new capabilities stay in the engine, <b>off by default</b>.</span></li>
<li><span data-l="pt"><b>O que uma forma teria de ter</b> (especificação medida, não desejo):
amplificar (fator&nbsp;&gt;&nbsp;1, não gatear) &middot; perfil tardio (interruptor, não
acumulador) &middot; e um relógio que <b>não</b> seja o dano (gradual demais) nem a própria
pré-carga (realimenta o que amplifica: acima de um limiar a junta morre em 30 ciclos, bifurcação
medida).</span>
<span data-l="en"><b>What a working form would need</b> (measured spec, not a wish): amplify
(factor&nbsp;&gt;&nbsp;1, not gate) &middot; late profile (switch, not accumulator) &middot; and a
clock that is <b>neither</b> damage (too gradual) nor preload itself (it feeds back into what it
amplifies: past a threshold the joint dies in 30 cycles &mdash; measured bifurcation).</span></li>
<li><span data-l="pt"><b>Kernel de colapso desacelerante</b> (aproximação suave ao piso de arresto).
<b>A maior lacuna isolada: 26 curvas em 7 fontes</b> (Lu2024 10, Chu2026 7, Yang2019 4, Eccles
fig8a/8c 2, Karlsen 1, Sun 1, Zhang2006 1). O dado desacelera até um platô; o kernel de catraca
atual <b>bifurca</b> entre travar e disparar, sem meio-termo.</span>
<span data-l="en"><b>Decelerating-collapse kernel</b> (smooth approach to the arrest floor). <b>The
single largest gap: 26 curves across 7 sources</b> (Lu2024 10, Chu2026 7, Yang2019 4, Eccles
fig8a/8c 2, Karlsen 1, Sun 1, Zhang2006 1). The data decelerates to a plateau; the current ratchet
kernel <b>bifurcates</b> between arrest and runaway, with nothing in between.</span></li>
<li><span data-l="pt"><b>Bifurcação de limiar de amplitude</b> (Yang2023 IJPEM, 7 curvas). Perto do
limiar o dado afrouxa-ou-não (bifurcação), não segue lei de potência. <b>Tri-falsificado:</b> nem
catraca, nem take-up relido, nem expoente de amplitude reproduzem a resposta graduada
N_L &prop; &delta;<sup>&minus;3.5</sup> que o próprio artigo mede.</span>
<span data-l="en"><b>Amplitude-threshold bifurcation</b> (Yang2023 IJPEM, 7 curves). Near threshold the
data either loosens or does not (a bifurcation), rather than following a power law.
<b>Triply falsified:</b> neither ratchet, re-read take-up, nor amplitude exponent reproduces the
graded N_L &prop; &delta;<sup>&minus;3.5</sup> response the paper itself measures.</span></li>
<li><span data-l="pt"><b>Condição de contorno axial externa</b> (Eccles 2010, 4 curvas). Quando a força
axial aplicada <b>excede</b> o torque de prevalência, a porca gira até zero e se destaca &mdash; o
engine não tem esse conceito (é contorno, não mecanismo de perda). Aplicar a receita existente
<b>piorou</b> o resíduo máximo de 0.47 para 1.03.</span>
<span data-l="en"><b>External axial boundary condition</b> (Eccles 2010, 4 curves). When the applied axial
force <b>exceeds</b> the prevailing torque, the nut rotates to zero and detaches &mdash; the engine has
no such concept (it is a boundary condition, not a loss mechanism). Applying the existing recipe made
the peak residual <b>worse</b>, from 0.47 to 1.03.</span></li>
<li><span data-l="pt"><b>Menores, com prova:</b> cliff/rebound de corrosão (JCSR, 2 &mdash; o dado
<i>recupera</i> pré-carga e nenhum mecanismo do engine recupera), incubação do assentamento (UFU, 2
&mdash; o dado fica plano até N&asymp;38 e o modelo assenta desde o ciclo 1), canal estrutural
&xi;-dependente (Yang2021, 2 &mdash; o dado confunde F_ax e &delta;).</span>
<span data-l="en"><b>Smaller, with evidence:</b> corrosion cliff/rebound (JCSR, 2 &mdash; the data
<i>recovers</i> preload and no engine mechanism recovers it), seating incubation (UFU, 2 &mdash; the data
stays flat to N&asymp;38 while the model seats from cycle 1), &xi;-dependent structural channel
(Yang2021, 2 &mdash; the data confounds F_ax and &delta;).</span></li>
</ul>
<p class="note"><span data-l="pt"><b>Três falsificações desta lista foram FECHADAS &mdash; e vale
registrar como, porque duas ficaram escritas aqui depois de resolvidas.</b> (1) <i>Amplitude axial</i>
(&prop; A_F): o Gate B1 mediu &part;(fim)/&part;A_F &equiv; 0 em 03/07/2026 contra um baseline genérico;
a &rho;-unificação foi adotada cinco dias depois e hoje o modelo entrega
&minus;1.72&times;10<sup>&minus;5</sup>/N contra &minus;2.22&times;10<sup>&minus;5</sup> no dado &mdash;
<b>78% da sensibilidade, não zero</b>, com as duas fontes axiais fechando 100% da meta. (2)
<i>Espessura do membro</i>: a forma foi construída &mdash; o cisalhamento do membro em série põe o
espécime mais espesso em <b>stick permanente</b>, que é exatamente por que ele não colapsa. (3)
<i>Acoplamento F_amp&harr;&delta;</i>: a capacidade existe no engine, <b>desligada por padrão</b>, à
espera de calibração. Nos três casos a afirmação envelheceu porque ninguém a re-mediu depois da
mudança que a resolveu &mdash; a regra que adotamos é que <b>toda falsificação carrega a versão do
modelo contra a qual foi medida</b>.</span>
<span data-l="en"><b>Three falsifications on this list have been CLOSED &mdash; and how is worth
recording, because two stayed written here after being resolved.</b> (1) <i>Axial amplitude</i>
(&prop; A_F): Gate B1 measured &part;(final)/&part;A_F &equiv; 0 on 2026-07-03 against a generic
baseline; the &rho;-unification was adopted five days later, and today the model delivers
&minus;1.72&times;10<sup>&minus;5</sup>/N against &minus;2.22&times;10<sup>&minus;5</sup> in the data
&mdash; <b>78% of the sensitivity, not zero</b>, with both axial sources fully inside the goal. (2)
<i>Member thickness</i>: the form was built &mdash; member shear in series puts the thickest specimen in
<b>permanent stick</b>, which is precisely why it does not collapse. (3) <i>F_amp&harr;&delta;
coupling</i>: the capability exists in the engine, <b>off by default</b>, awaiting calibration. In all
three the claim aged because nobody re-measured it after the change that resolved it &mdash; the rule
we adopted is that <b>every falsification carries the model version it was measured against</b>.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Constantes por par/rig (não universais)</span>
<span data-l="en">Per-pair/rig constants (not universal)</span></h2>
<p><span data-l="pt">A doutrina &mdash; <b>formas transferem cross-rig; níveis/constantes são por
rig</b> &mdash; tem um custo honesto: constantes como <code>W_conf_ref</code>, <code>C_creep</code> e
<code>K_archard</code> têm MAGNITUDE por par tribológico/rig, não um valor universal. A âncora de creep
304SS (9.9&times;10<sup>&minus;13</sup>) e o fit UFU (1.2&times;10<sup>&minus;11</sup>) têm intervalos de
confiança DISJUNTOS; o <code>W_conf_ref</code> não foi ancorável em nenhum dado da biblioteca. Fora do
par calibrado, a magnitude é aproximada.</span>
<span data-l="en">The doctrine &mdash; <b>forms transfer cross-rig; levels/constants are per-rig</b> &mdash;
has an honest cost: constants like <code>W_conf_ref</code>, <code>C_creep</code> and
<code>K_archard</code> have per-tribo-pair/rig MAGNITUDE, not a universal value. The 304SS creep anchor
(9.9&times;10<sup>&minus;13</sup>) and the UFU fit (1.2&times;10<sup>&minus;11</sup>) have DISJOINT
confidence intervals; <code>W_conf_ref</code> could not be anchored on any library dataset. Off the
calibrated pair, the magnitude is approximate.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Numérico e energia</span><span data-l="en">Numerics and energy</span></h2>
<ul class="refs">
<li><span data-l="pt"><b>Conservação no colapso por dano.</b> A energética da remoção abrasiva é
fenomenológica; o residual de conservação degrada quando o dano leva F0&rarr;0.</span>
<span data-l="en"><b>Conservation in damage-collapse.</b> The abrasive-removal energetics are
phenomenological; the conservation residual degrades when damage drives F0&rarr;0.</span></li>
<li><span data-l="pt"><b>Bookkeeping viscoso no modo axial-força.</b> O termo viscoso de Rayleigh acumula
sem contraparte em W_ext (residual &minus;242 a &minus;12 J); NÃO afeta F0 nem os MAEs, mas o budget de
energia axial fica aberto.</span>
<span data-l="en"><b>Viscous bookkeeping in axial force mode.</b> The Rayleigh viscous term accumulates
with no W_ext counterpart (residual &minus;242 to &minus;12 J); it does NOT affect F0 or the MAEs, but the
axial energy budget stays open.</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Como isso aparece no guia</span><span data-l="en">How this shows up in the guide</span></h2>
<ul class="refs">
<li><span data-l="pt">Sliders <b>"mortos"</b> honestos (marcados <code>negligible</code>) &mdash; o campo existe mas quase não move a curva-padrão.</span><span data-l="en">Honest <b>"dead" sliders</b> (marked <code>negligible</code>) &mdash; the field exists but barely moves the standard curve.</span></li>
<li><span data-l="pt">O <b>MAE é mostrado sem esconder</b> (overlay e galeria); os casos com MAE &gt; 0.10 são marcados; cada caso tem seus <b>caveats</b>.</span><span data-l="en">The <b>MAE is shown, not hidden</b> (overlay and gallery); cases with MAE &gt; 0.10 are flagged; each case carries its <b>caveats</b>.</span></li>
<li><span data-l="pt">A <a href="concept_gallery.html">galeria</a> confronta o modelo com {{N_CURVAS}} curvas &mdash; incluindo onde ele erra. Ver também a <a href="concept_methodology.html">Metodologia</a> (falsificação, procedência).</span><span data-l="en">The <a href="concept_gallery.html">gallery</a> confronts the model with {{N_CURVAS}} curves &mdash; including where it misses. See also the <a href="concept_methodology.html">Methodology</a> (falsification, provenance).</span></li>
</ul>
</div>
'''),

    # ---------------------------------------------------------------- 7 (galeria)
    dict(
        slug="gallery",
        nav_pt="7 · Galeria de validação", nav_en="7 · Validation gallery",
        title_pt="Galeria de validação: modelo vs dado", title_en="Validation gallery: model vs data",
        hook_pt="o modelo confrontado com a biblioteca inteira",
        hook_en="the model confronted with the whole library",
        widget="gallery",
        body='''
<div class="sub"><span data-l="pt">Cada card abaixo confronta a PREVISÃO do modelo (linha) com os
PONTOS medidos de uma curva digitalizada da literatura. São {{N_CURVAS}} curvas de {{N_FONTES}} estudos
independentes; a linha vem do store canônico (configuração adotada por fonte, com procedência
declarada), os pontos vêm dos CSVs digitalizados. Nada foi re-simulado aqui &mdash; é o resultado
canônico do pacote de validação.</span>
<span data-l="en">Each card below confronts the model PREDICTION (line) with the measured POINTS of a
digitized literature curve. There are {{N_CURVAS}} curves from {{N_FONTES}} independent studies; the line comes from
the canonical store (adopted per-source configuration, with declared provenance), the dots from the
digitized CSVs. Nothing was re-simulated here &mdash; it is the canonical validation-package
result.</span></div>

<div id="cw"></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Como ler</span><span data-l="en">How to read</span></h2>
<ul class="refs">
<li><span data-l="pt"><b>Linha</b> = saída do modelo; <b>pontos</b> = dado experimental. O eixo Y é F/F0
(pré-carga normalizada); o X é o ciclo.</span><span data-l="en"><b>Line</b> = model output; <b>dots</b>
= experimental data. Y is F/F0 (normalized preload); X is the cycle.</span></li>
<li><span data-l="pt">O <b>badge</b> é o MAE (erro absoluto médio) daquela curva: verde &le; 0.05,
âmbar &le; 0.10, vermelho &gt; 0.10.</span><span data-l="en">The <b>badge</b> is that curve's MAE (mean
absolute error): green &le; 0.05, amber &le; 0.10, red &gt; 0.10.</span></li>
<li><span data-l="pt">Filtre por família (transversal / axial / creep) ou mostre só os casos com MAE
&gt; 0.10.</span><span data-l="en">Filter by family (transverse / axial / creep) or show only the cases
with MAE &gt; 0.10.</span></li>
<li><span data-l="pt">O símbolo &#9888; marca um <b>caveat declarado</b> (par polimérico, cauda com
fratura por fadiga, dispositivo de travamento, creep estático, etc.) &mdash; casos fora do domínio
puro de afrouxamento.</span><span data-l="en">The &#9888; symbol marks a <b>declared caveat</b> (polymer
pair, fatigue-fracture tail, locking device, static creep, etc.) &mdash; cases outside the pure
loosening domain.</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">O que a galeria mostra (e o que não mostra)</span>
<span data-l="en">What the gallery shows (and what it doesn't)</span></h2>
<p><span data-l="pt">Uma única física, com constantes de procedência declarada, reproduz a MEDIANA da
biblioteca com MAE baixo &mdash; e faz isso PREVENDO cada estudo, não ajustando curva a curva. Os
poucos casos com MAE alto são <b>honestos</b>: em geral são limitados por uma FORMA faltante (um
mecanismo que o modelo ainda não representa) ou por dispersão do próprio dado digitalizado, não por um
coeficiente mal ajustado.</span>
<span data-l="en">One physics, with declared-provenance constants, reproduces the library MEDIAN at low
MAE &mdash; by PREDICTING each study, not fitting curve by curve. The few high-MAE cases are
<b>honest</b>: they are usually limited by a missing FORM (a mechanism the model does not yet
represent) or by scatter in the digitized data itself, not by a mis-tuned coefficient.</span></p>
<p class="intro"><span data-l="pt">Isto materializa a doutrina: <b>as formas (mecanismos, expoentes,
acoplamentos) transferem entre rigs; os níveis/constantes são por rig</b>. A galeria é o teste dessa
afirmação em 15 aparatos diferentes. Ver <a href="concept_methodology.html">Metodologia</a>.</span>
<span data-l="en">This materializes the doctrine: <b>forms (mechanisms, exponents, couplings) transfer
across rigs; levels/constants are per-rig</b>. The gallery is the test of that claim across 15
different apparatuses. See <a href="concept_methodology.html">Methodology</a>.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 8 (revisao)
    dict(
        slug="review",
        nav_pt="8 · Revisão da literatura", nav_en="8 · Literature review",
        title_pt="Revisão da literatura", title_en="Literature review",
        hook_pt="o que os artigos ensinam sobre auto-afrouxamento",
        hook_en="what the papers teach about self-loosening",
        body='''
<div class="sub"><span data-l="pt">Síntese do tema a partir do corpus de artigos da biblioteca de
validação (ver <a href="concept_references.html">Referências</a>): fenomenologia, fases, variáveis
de controle, achados por fonte, lacunas em aberto e como o modelo V2 se posiciona.</span>
<span data-l="en">Synthesis of the topic from the validation-library corpus (see
<a href="concept_references.html">References</a>): phenomenology, phases, controlling variables,
findings by source, open gaps, and how the V2 model stands.</span></div>
<div class="panel">
<h2 class="sec"><span data-l="pt">O fenômeno do auto-afrouxamento</span><span data-l="en">The self-loosening phenomenon</span></h2>
<p><span data-l="pt">O auto-afrouxamento é a perda progressiva da pré-carga de aperto (F0) de uma junta aparafusada sob carregamento cíclico. Ele cobre desde perdas micrométricas sem qualquer giro da porca até o back-off macroscópico em que a porca desrosqueia e a junta abre.</span><span data-l="en">Self-loosening is the progressive loss of a bolted joint's clamp preload (F0) under cyclic loading. It spans everything from micrometric losses with no nut rotation at all to the macroscopic back-off in which the nut unscrews and the joint opens.</span></p>
<p><span data-l="pt">O driver dominante é a vibração <b>TRANSVERSAL</b> de Junker (1969): o deslocamento cíclico perpendicular ao eixo do parafuso afrouxa muito mais rápido que a excitação axial. Quase toda a base usa o ensaio de Junker controlado por deslocamento (DIN 65151) -- Bauer (2024), Liu (2025) e Karlsen (2022). A excitação axial é mais branda: Liu (2017) (axial ~30 Hz, M12), H. Li (2022) e a excitação modal de Sandia (2021), cujo modo-1 de flexão resolve-se em cisalhamento na junta.</span><span data-l="en">The dominant driver is Junker's <b>TRANSVERSE</b> vibration (1969): cyclic displacement perpendicular to the bolt axis loosens far faster than axial excitation. Almost the whole corpus uses the displacement-controlled Junker test (DIN 65151) -- Bauer (2024), Liu (2025) and Karlsen (2022). Axial excitation is milder: Liu (2017) (axial ~30 Hz, M12), H. Li (2022) and the modal excitation of Sandia (2021), whose mode-1 bending resolves into shear at the joint.</span></p>
<p><span data-l="pt">Duas famílias coexistem. (a) <b>RELAXAÇÃO</b> de pré-carga <i>sem</i> giro da porca: embedding (achatamento plástico das asperezas, primeiros ciclos) e creep (viscoelástico, log-tempo). Y. Li (2022) isola o creep de contato a temperatura ambiente sem vibração; Yang (2023) mediu perda em junta de CFRP "sem rotação"; Karlsen (2022) atribui a queda inicial a "redução imediata das asperezas, não a creep". (b) Afrouxamento <b>ROTACIONAL</b>: a porca de fato recua, convertendo a torção armazenada em giro pela hélice da rosca -- o mecanismo two-factor (razão de rigidez anisotrópica &middot; projeção pela hélice), o destrutivo.</span><span data-l="en">Two families coexist. (a) preload <b>RELAXATION</b> with <i>no</i> nut rotation: embedding (plastic flattening of asperities, first cycles) and creep (viscoelastic, log-time). Y. Li (2022) isolates contact creep at ambient temperature with no vibration; Yang (2023) measured CFRP-joint loss "without rotation"; Karlsen (2022) attributes the early drop to "immediate reduction of asperities, not creep". (b) <b>ROTATIONAL</b> loosening: the nut actually backs off, converting stored torsion into rotation through the thread helix -- the two-factor mechanism (anisotropic stiffness ratio &middot; helix projection), and the destructive one.</span></p>
<p><span data-l="pt">O cisalhamento transversal é tão daninho porque, quando o deslocamento leva a face do bearing ao slip completo (gross slip), a margem de atrito que trava o giro desaparece. Abaixo de um deslocamento crítico s_crit (fator de Pai-Hess 0.46; s_crit = 99 &micro;m em Bauer 2024) a junta só assenta; acima dele, a hélice destrava a porca ciclo a ciclo -- e o processo vira runaway, pois s_crit encolhe junto com F0.</span><span data-l="en">Transverse slip is so damaging because, once the displacement drives the bearing face into complete (gross) slip, the friction margin that locks rotation vanishes. Below a critical slip s_crit (Pai-Hess factor 0.46; s_crit = 99 &micro;m in Bauer 2024) the joint only settles; above it, the helix unlocks the nut cycle by cycle -- and the process becomes runaway, since s_crit shrinks together with F0.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Fases da curva: 2 estágios vs 3 estágios</span><span data-l="en">Curve phases: 2-stage vs 3-stage</span></h2>
<p><span data-l="pt">O padrão mais comum é de <b>DUAS RETAS</b>: uma queda rápida inicial (embedding/assentamento, primeiros ~5-10 ciclos) seguida de um declínio gradual quase-linear (desgaste + afrouxamento rotacional). Demir (2024) descreve a "queda rápida inicial" explicitamente; Rousseau (2025) e Liu (2017) mostram o mesmo formato de dois estágios. É o comportamento que o motor V2 reproduz nativamente.</span><span data-l="en">The commonest pattern is <b>TWO STRAIGHT LINES</b>: a fast initial drop (embedding/settling, first ~5-10 cycles) followed by a gradual, near-linear decline (wear + rotational loosening). Demir (2024) describes the "rapid initial drop" explicitly; Rousseau (2025) and Liu (2017) show the same two-stage shape. This is what the V2 engine reproduces natively.</span></p>
<p><span data-l="pt">Um subconjunto exibe <b>TRÊS ESTÁGIOS</b>: incubação lenta &rarr; afrouxamento intermediário &rarr; colapso re-acelerado. Bauer (2024), Fig. 8 (M12x1.5, 50 kN), mostra o terceiro estágio explícito quando a força de aperto cai abaixo de um valor crítico; o estágio III de Yang (2021) é fratura por fadiga (excitação composta, fase 90&deg;). Liu (2025) exibe a assinatura fast-slow-fast: queda inicial de embedding, meio lento e colapso re-acelerado ao final.</span><span data-l="en">A subset shows <b>THREE STAGES</b>: slow incubation &rarr; intermediate loosening &rarr; re-accelerating collapse. Bauer (2024), Fig. 8 (M12x1.5, 50 kN), shows the explicit third stage once the clamp force falls below a critical value; Yang (2021)'s stage III is fatigue fracture (composite excitation, 90&deg; phase). Liu (2025) shows the fast-slow-fast signature: an initial embedding drop, a slow middle, and a re-accelerating collapse at the end.</span></p>
<p><span data-l="pt">Fisicamente: o Estágio I é embedding/incubação (só assentamento, quase sem perda de aperto); o II é erosão estável (desgaste de Archard + afrouxamento graduado); o III é o colapso por dano de superfície (erosão das asperezas &rarr; queda do atrito &rarr; runaway) ou fratura por fadiga da raiz da rosca.</span><span data-l="en">Physically: Stage I is embedding/incubation (settling only, almost no clamp loss); II is steady erosion (Archard wear + graded loosening); III is surface-damage collapse (asperity erosion &rarr; friction drop &rarr; runaway) or thread-root fatigue fracture.</span></p>
<p><span data-l="pt">As curvas de três estágios são as <b>únicas</b> que restringem o limiar de incubação (<code>slip_onset_W</code>) e o colapso por dano de superfície (<code>D</code>) do modelo -- curvas de duas retas não excitam esses recursos. O s_crit = 99 &micro;m de Bauer (2024) é uma âncora direta desse limiar.</span><span data-l="en">Three-stage curves are the <b>only</b> ones that constrain the model's incubation threshold (<code>slip_onset_W</code>) and its surface-damage collapse (<code>D</code>) -- two-line curves never excite those features. Bauer (2024)'s s_crit = 99 &micro;m is a direct anchor for that threshold.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Variáveis que controlam o afrouxamento</span><span data-l="en">Variables controlling loosening</span></h2>
<p><span data-l="pt">O que a base experimental mostra sobre cada variável de controle:</span><span data-l="en">What the experimental corpus shows about each controlling variable:</span></p>
<ul class="refs">
<li><span data-l="pt"><b>Amplitude transversal.</b> Maior amplitude &rarr; afrouxamento mais rápido, mas há um limiar s_crit abaixo do qual o processo estagna: Bauer (2024) quantifica s_crit = 99 &micro;m; Liu (2025) varre 0.25-0.8 mm; no caso de 0.25 mm de Yang (2024) a junta perde só ~22% e satura.</span><span data-l="en"><b>Transverse amplitude.</b> Larger amplitude &rarr; faster loosening, but there is a threshold s_crit below which the process stalls: Bauer (2024) quantifies s_crit = 99 &micro;m; Liu (2025) sweeps 0.25-0.8 mm; in Yang (2024)'s 0.25 mm case the joint loses only ~22% and saturates.</span></li>
<li><span data-l="pt"><b>Pré-carga F0.</b> Aperto maior resiste mais ao afrouxamento (Liu 2017, varredura 10/15/18 kN), mas os ciclos-até-a-falha vs pré-carga costumam ser planos (Lu 2024) -- mais aperto atrasa, não impede.</span><span data-l="en"><b>Preload F0.</b> Higher clamp resists loosening (Liu 2017, 10/15/18 kN sweep), yet cycles-to-failure vs preload are often flat (Lu 2024) -- more clamp delays, it does not prevent.</span></li>
<li><span data-l="pt"><b>Frequência.</b> Em modo deslocamento é majoritariamente um confundidor (o decaimento de pré-carga é pouco sensível à frequência; Yang 2024 testou 0.1/1/5 Hz); mas em fretting, frequência menor piora por mais dwell/oxidação (H. Li 2022).</span><span data-l="en"><b>Frequency.</b> In displacement mode it is mostly a confounder (preload decay is largely insensitive to frequency; Yang 2024 tested 0.1/1/5 Hz); but in fretting, lower frequency is worse via more dwell/oxidation (H. Li 2022).</span></li>
<li><span data-l="pt"><b>Rigidez/material do membro e comprimento de aperto.</b> Juntas mais rígidas afrouxam mais rápido; Rousseau (2025) contrasta aço (E~200 GPa) vs HDPE (E~1 GPa) e varre espessura t = 10/12/14 mm e grip 25/29/33 mm.</span><span data-l="en"><b>Member stiffness/material and grip length.</b> Stiffer joints loosen faster; Rousseau (2025) contrasts steel (E~200 GPa) vs HDPE (E~1 GPa) and sweeps thickness t = 10/12/14 mm and grip 25/29/33 mm.</span></li>
<li><span data-l="pt"><b>Dispositivos de travamento.</b> Karlsen (2022) mostra o parafuso HV padrão afrouxando em 200-400 ciclos contra ~3000 do Vibralock; Eccles (2010) caracteriza porcas de torque prevalecente e um limiar quantitativo de destacamento.</span><span data-l="en"><b>Locking devices.</b> Karlsen (2022) shows the standard HV bolt loosening in 200-400 cycles against ~3000 for Vibralock; Eccles (2010) characterises prevailing-torque nuts and a quantitative detachment threshold.</span></li>
<li><span data-l="pt"><b>Lubrificação.</b> Seco vs MoS2 vs óleo muda o atrito e a retenção: Alsardia (2024) mede as-is 22.8&rarr;15.7 kN, MoS2 -44.7%, enquanto o oleado <i>sobe</i> ~20% e estabiliza; Liu (2017) varre revestimentos PTFE/MoS2/TiN.</span><span data-l="en"><b>Lubrication.</b> Dry vs MoS2 vs oiled changes both friction and retention: Alsardia (2024) measures as-is 22.8&rarr;15.7 kN, MoS2 -44.7%, while the oiled case <i>rises</i> ~20% and stabilises; Liu (2017) sweeps PTFE/MoS2/TiN coatings.</span></li>
<li><span data-l="pt"><b>Temperatura / creep.</b> Lakes (2007) mede a perda de carga em juntas de alumínio a 220/240/260 &deg;C (constantes de creep por temperatura); Y. Li (2022) isola o creep de contato a temperatura ambiente (Norton/Burgers), sem vibração.</span><span data-l="en"><b>Temperature / creep.</b> Lakes (2007) measures load loss in aluminium joints at 220/240/260 &deg;C (temperature-dependent creep constants); Y. Li (2022) isolates ambient-temperature contact creep (Norton/Burgers) with no vibration.</span></li>
<li><span data-l="pt"><b>Tamanho.</b> A base cobre de M6 (Yang 2023) a M42 (Karlsen 2022), com pré-cargas de 3.5 kN (Rousseau 2025) a 706 kN (Karlsen M42); o ponto nativo de calibração é M16 (Liu 2025).</span><span data-l="en"><b>Size.</b> The corpus spans M6 (Yang 2023) to M42 (Karlsen 2022), with preloads from 3.5 kN (Rousseau 2025) to 706 kN (Karlsen M42); the native calibration point is M16 (Liu 2025).</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Achados-chave por fonte</span><span data-l="en">Key findings by source</span></h2>
<ul class="refs">
<li><b>Liu (2017) / Liu (2016)</b> &mdash; <span data-l="pt">trilha AXIAL. Sob excitação axial cíclica (M12, ~30 Hz), a força de aperto cai em dois estágios (assentamento plástico rápido + cauda lenta de fretting de flanco de rosca) e o afrouxamento CRESCE com a amplitude axial A_F (gradiente medido &asymp; &minus;2.2e-5/N); preload maior afrouxa menos. A varredura de amplitude de Liu (2016) no mesmo rig (torque &times; A_F, MoS2 vs seco) confirma a tendência e alimenta a unificação &rho; = A_F/F_0.</span><span data-l="en">AXIAL track. Under cyclic axial excitation (M12, ~30 Hz), clamp force drops in two stages (fast plastic settling + slow thread-flank fretting tail) and loosening GROWS with axial amplitude A_F (measured gradient &asymp; &minus;2.2e-5/N); higher preload loosens less. Liu (2016)'s amplitude sweep on the same rig (torque &times; A_F, MoS2 vs dry) confirms the trend and feeds the &rho; = A_F/F_0 unification.</span></li>
<li><b>Bauer (2024)</b> &mdash; <span data-l="pt">colapso explícito de terceiro estágio. Fig. 8 (M12&times;1.5, base 80 &micro;m + picos 150 &micro;m, espectro) mostra o joelho lento&rarr;acelerado&rarr;íngreme; quantifica um slip crítico s_crit &asymp; 99 &micro;m (faixa 76&ndash;108 &micro;m). O colapso é F_V-crítico: espera a pré-carga cair o suficiente para a amplitude crítica descer abaixo da base do espectro. Fig. 6 (M8, 6 curvas) dá o regime quase-linear de contraponto.</span><span data-l="en">explicit third-stage collapse. Fig. 8 (M12&times;1.5, 80 &micro;m base + 150 &micro;m peaks, spectrum) shows the slow&rarr;accelerating&rarr;steep knee; quantifies a critical slip s_crit &asymp; 99 &micro;m (76&ndash;108 &micro;m band). Collapse is F_V-critical: it waits for preload to fall until the critical amplitude drops below the spectrum base. Fig. 6 (M8, 6 curves) gives the near-linear counterpoint regime.</span></li>
<li><b>Lu (2024)</b> &mdash; <span data-l="pt">ratchet cinemático. A razão T_loose/T_resist fica ~fixa (&asymp; 1.57) através da amplitude enquanto o dado colapsa, e a vida N_falha é ~plana acima de um onset de torque (snap): torque alto arresta (T28Nm ~0.23 a 71% da prova), torque baixo colapsa (T4Nm ~0.04 a 10%). Evidência de que a rotação é &prop; ao caminho de slip (Junker clássico), não um runaway de torque.</span><span data-l="en">kinematic ratchet. The T_loose/T_resist ratio stays ~fixed (&asymp; 1.57) across amplitude while the data collapses, and life N_fail is ~flat above a torque onset (snap): high torque arrests (T28Nm ~0.23 at 71% proof), low torque collapses (T4Nm ~0.04 at 10%). Evidence the rotation is &prop; slip path (classic Junker), not a torque runaway.</span></li>
<li><b>Rousseau (2025)</b> &mdash; <span data-l="pt">rigidez/material do membro controla a ordem do afrouxamento. Única varredura de espessura da biblioteca (t = 10/12/14 mm) com &theta;(N) medido; aço colapsa enquanto o par HDPE NÃO colapsa (assentamento plástico do polímero desacopla da rotação). A ordem é governada pela complacência do membro, não pela amplitude.</span><span data-l="en">member stiffness/material controls the loosening order. The library's only thickness sweep (t = 10/12/14 mm) with measured &theta;(N); steel collapses while the HDPE pair does NOT collapse (the polymer's plastic settling decouples from rotation). Order is governed by member compliance, not amplitude.</span></li>
<li><b>Karlsen (2022)</b> &mdash; <span data-l="pt">tamanho extremo. M30 (F_0 = 353 kN, 70% do escoamento, &plusmn;1.0 mm) e M42 (706 kN, &plusmn;1.5 mm) a 1 Hz; parafuso padrão HV afrouxa em 200&ndash;400 ciclos enquanto o dispositivo Vibralock (cunha) sobrevive ~3000. Grande dispersão por espécime (c_bend per-especime); a fonte fica no piso de repetibilidade.</span><span data-l="en">extreme size. M30 (F_0 = 353 kN, 70% yield, &plusmn;1.0 mm) and M42 (706 kN, &plusmn;1.5 mm) at 1 Hz; the standard HV bolt loosens in 200&ndash;400 cycles while the Vibralock (wedge) device survives ~3000. Large per-specimen scatter (per-specimen c_bend); this source sits at the repeatability floor.</span></li>
<li><b>Yang (2019 / 2021 / 2023)</b> &mdash; <span data-l="pt">amplitude variável em blocos (2019, M10); excitação composta transversal+axial a 90&deg; de fase (2021), acoplando F_amp&harr;&delta;_amp com falha competitiva afrouxamento/fadiga; e um modelo fenomenológico de curva-mestra M6/M8 (2023) com ratchet + onset de slip.</span><span data-l="en">block variable-amplitude loading (2019, M10); composite transverse+axial excitation at 90&deg; phase (2021), coupling F_amp&harr;&delta;_amp with competitive loosening/fatigue failure; and a phenomenological master-curve model M6/M8 (2023) with ratchet + slip onset.</span></li>
<li><b>Y. Li (2022)</b> &mdash; <span data-l="pt">creep estático de contato a temperatura ambiente, SEM vibração (M16 304SS, eixo em minutos) — isola o creep puro (wear/loosening estruturalmente inertes). Estabelece que C_creep é POR PAR tribológico: a âncora estática discorda do valor dinâmico por ~11.7&times; com ICs disjuntos.</span><span data-l="en">static contact creep at ambient temperature, WITHOUT vibration (M16 304SS, minutes axis) — isolates pure creep (wear/loosening structurally inert). Establishes that C_creep is PER tribological pair: the static anchor disagrees with the dynamic value by ~11.7&times; with disjoint CIs.</span></li>
<li><b>H. Li (2022)</b> &mdash; <span data-l="pt">axial &times; frequência (10/15/20 Hz, mesmo grupo do Liu 2017). O assentamento escala com o dwell do fretting (embedding &prop; 1/freq, r = &minus;0.99), e a cauda de titânio termina num cliff de fadiga — a fonte da forma freq-dependente e do fim por fratura.</span><span data-l="en">axial &times; frequency (10/15/20 Hz, same group as Liu 2017). Settling scales with fretting dwell (embedding &prop; 1/freq, r = &minus;0.99), and the titanium tail ends in a fatigue cliff — the source of the freq-dependent form and the fracture endpoint.</span></li>
<li><b>Z. Liu (2022)</b> &mdash; <span data-l="pt">reaperto sucessivo sob carga transversal: após o 3&ordm; reaperto o afrouxamento acelera e no 4&ordm; a força colapsa. Motiva a renovação de embedding (o reaperto reabre o reservatório de assentamento) + galling (o dano acumulado degrada o atrito de rosca) — cadeia t_0&rarr;retighten()&rarr;t_N.</span><span data-l="en">successive retightening under transverse load: after the 3rd retighten loosening accelerates and at the 4th the force collapses. Motivates embedding renewal (retightening reopens the settling reservoir) + galling (accumulated damage degrades thread friction) — chain t_0&rarr;retighten()&rarr;t_N.</span></li>
<li><b>Baydoun / Fouvry (2019, 2007)</b> &mdash; <span data-l="pt">fretting flat-on-flat com pressão quase-constante controlada + formulação de energia friccional ponderada e "capacidade de energia de wear" por par. Dá a FORMA do expoente de pressão do gate de conformação (n_p &asymp; 0.5&ndash;0.6), mas aço e coatings ficam sub-GPa — a forma transfere, a magnitude (~1.2 GPa) não.</span><span data-l="en">flat-on-flat fretting with controlled quasi-constant pressure + a weighted friction-energy formulation and a per-pair "wear energy capacity". It gives the FORM of the conformation gate's pressure exponent (n_p &asymp; 0.5&ndash;0.6), but steel and coatings stay sub-GPa — the form transfers, the magnitude (~1.2 GPa) does not.</span></li>
<li><b>Alsardia (2024) / Sun (2025)</b> &mdash; <span data-l="pt">reaperto &times; lubrificação. Alsardia (M8&times;40 10.9, 20 reapertos): as-is 22.8&rarr;15.7 kN, MoS2 &minus;44.7%, mas OLEADO SOBE ~20% e estabiliza. Sun (porca auto-frenante crimpada): óxido de prata SOBE o atrito e mantém o preload. Âncoram a renovação de embedding e o atrito/galling por lubrificante.</span><span data-l="en">retighten &times; lubrication. Alsardia (M8&times;40 10.9, 20 retightenings): as-is 22.8&rarr;15.7 kN, MoS2 &minus;44.7%, but OILED RISES ~20% and stabilizes. Sun (crimping self-locking nut): silver oxide RAISES friction and holds preload. They anchor embedding renewal and per-lube friction/galling.</span></li>
<li><b>Grzejda (2026)</b> &mdash; <span data-l="pt">controle NULO. Conexão multi-parafuso assimétrica sob carga cíclica (Instron, 22 kN de preload, amplitude 10/20 kN): NENHUMA perda de preload (&plusmn;2%). Não é curva de decaimento — é o controle negativo: o modelo deve prever ~zero perda nessas condições.</span><span data-l="en">NULL control. Asymmetric multi-bolt connection under cyclic load (Instron, 22 kN preload, 10/20 kN amplitude): NO preload loss (&plusmn;2%). Not a decay curve — it is the negative control: the model must predict ~zero loss under these conditions.</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Lacunas em aberto e falsificações</span><span data-l="en">Open gaps and falsifications</span></h2>
<p><span data-l="pt"><b>Duas falsificações históricas desta página já FECHARAM — e o ciclo completo é a melhor ilustração da doutrina.</b> (1) <b>Amplitude axial.</b> A confrontação zero-refit de 03/07/2026 (&sect;4.6) falsificou o conjunto AS-IS: nenhum mecanismo era dirigido pela amplitude de carga axial (wear = slip transversal; creep = só F_0; embedding = amplitude-cego), e o modelo dava &part;(fim)/&part;A_F &equiv; 0 — as cinco predições do sweep eram a MESMA curva — contra &minus;2,2e-5/N no dado (Liu 2017). A forma foi então suprida: a unificação &rho; tornou o assentamento dependente da amplitude, e <b>hoje o modelo dá &minus;1,72e-5/N contra &minus;2,22e-5/N medido — 78% da sensibilidade, com as duas fontes axiais 100% dentro da meta</b> (&sect;4.43, re-baseline de 27/07). Resta ~22% da inclinação: resíduo quantitativo, não ausência de resposta. (2) <b>Escala com a espessura do membro.</b> Na única varredura de espessura da biblioteca (Rousseau 2025, t = 10/12/14 mm) o modelo era cego à espessura; a forma foi construída — o <b>cisalhamento do membro em série</b> com a rigidez transversal absorve o curso imposto, e o espécime mais espesso vai a <b>stick permanente</b>, que é exatamente por que ele não colapsa (previsto 0,882 contra 0,875 medido). Os MAE caíram para 0,058/0,064/0,044, e agora <b>diminuem</b> com a espessura.</span><span data-l="en"><b>Two historical falsifications on this page have CLOSED — and the full cycle is the best illustration of the doctrine.</b> (1) <b>Axial amplitude.</b> The zero-refit confrontation of 2026-07-03 (&sect;4.6) falsified the AS-IS set: no mechanism was driven by axial load amplitude (wear = transverse slip; creep = F_0 only; embedding = amplitude-blind), and the model gave &part;(final)/&part;A_F &equiv; 0 — the five sweep predictions were the SAME curve — against &minus;2.2e-5/N in the data (Liu 2017). The form was then supplied: the &rho;-unification made settling amplitude-dependent, and <b>today the model gives &minus;1.72e-5/N against &minus;2.22e-5/N measured — 78% of the sensitivity, with both axial sources fully inside the goal</b> (&sect;4.43, re-baselined 2026-07-27). About 22% of the slope remains: a quantitative residual, not an absent response. (2) <b>Member-thickness scaling.</b> In the library's only thickness sweep (Rousseau 2025, t = 10/12/14 mm) the model was thickness-blind; the form was built — <b>member shear in series</b> with the transverse stiffness absorbs the imposed stroke, and the thickest specimen goes into <b>permanent stick</b>, which is precisely why it does not collapse (0.882 predicted vs 0.875 measured). MAEs fell to 0.058/0.064/0.044 and now <b>decrease</b> with thickness.</span></p>
<p><span data-l="pt"><b>O que continua aberto, medido em 27/07 sobre as 40 curvas fora da meta.</b> A maior lacuna é um <b>kernel de colapso desacelerante</b>: o dado desacelera até um platô enquanto o kernel de catraca atual bifurca entre travar e disparar. O diagnóstico, porém, mostrou que <b>não é uma forma só</b>: correlacionando os perfis de resíduo com o nível removido, quatro rigs independentes (Chu2026, Yang2019, Karlsen, Zhang2006 — <b>13 curvas</b>) compartilham o MESMO erro de forma com r = 0,90 a 1,00, enquanto Lu2024 (10 curvas) tem um erro em <b>tigela</b> anticorrelacionado (r = &minus;0,27) e Eccles fig8a/8c tem erro de <b>nível</b>, não de forma (perfil plano, |0,022|). Ou seja: são três problemas, e um prereg único teria misturado formas anticorrelacionadas. Também abertos: <b>bifurcação de limiar</b> de amplitude (Yang2023 IJPEM, 7 curvas, tri-falsificada) e <b>condição de contorno axial externa</b> (Eccles 2010, 4 curvas — quando a força axial excede o torque de prevalência a porca gira até se destacar; é contorno, não mecanismo de perda).</span><span data-l="en"><b>What remains open, measured on 2026-07-27 across the 40 curves outside the goal.</b> The largest gap is a <b>decelerating-collapse kernel</b>: the data decelerates to a plateau while the current ratchet kernel bifurcates between arrest and runaway. The diagnosis, however, showed it is <b>not a single form</b>: correlating the residual profiles with the level removed, four independent rigs (Chu2026, Yang2019, Karlsen, Zhang2006 — <b>13 curves</b>) share the SAME shape error at r = 0.90 to 1.00, while Lu2024 (10 curves) has an anticorrelated <b>bowl</b>-shaped error (r = &minus;0.27) and Eccles fig8a/8c has a <b>level</b> error, not a shape one (flat profile, |0.022|). That is three problems, and a single prereg would have mixed anticorrelated shapes. Also open: amplitude <b>threshold bifurcation</b> (Yang2023 IJPEM, 7 curves, triply falsified) and an <b>external axial boundary condition</b> (Eccles 2010, 4 curves — when the axial force exceeds the prevailing torque the nut rotates until it detaches; a boundary condition, not a loss mechanism).</span></p>
<p><span data-l="pt">Constantes são propriedade por par tribológico/rig, não universais. A âncora estática de creep (Y. Li 2022) discorda do valor dinâmico por ~11.7&times; com ICs disjuntos (&sect;4.7). A escala de energia de conformação W_conf_ref, que resolve o sobretorque (&sect;4.9), permanece SEM âncora independente: a busca dedicada fechou os dois caminhos — nenhuma curva cross-rig a isola, e o número de Fouvry disponível (&alpha; &asymp; 4.23e-5 mm&sup3;/J) é análogo do K_archard, não do W_conf_ref. Baydoun/Fouvry dão a FORMA do expoente de pressão (n_p &asymp; 0.5&ndash;0.6), mas não a magnitude (~1.2 GPa do apoio pequeno do rig UFU) — W_conf_ref fica um degrau abaixo do creep na escala de procedência.</span><span data-l="en">Constants are per tribological-pair/rig properties, not universal. The static creep anchor (Y. Li 2022) disagrees with the dynamic value by ~11.7&times; with disjoint CIs (&sect;4.7). The conformation energy scale W_conf_ref, which resolves overtorque (&sect;4.9), remains WITHOUT an independent anchor: the dedicated hunt closed both paths — no cross-rig curve isolates it, and the available Fouvry number (&alpha; &asymp; 4.23e-5 mm&sup3;/J) is a K_archard analog, not W_conf_ref. Baydoun/Fouvry give the FORM of the pressure exponent (n_p &asymp; 0.5&ndash;0.6), but not the magnitude (~1.2 GPa of the small UFU-rig bearing) — W_conf_ref sits one step below creep on the provenance ladder.</span></p>
<p><span data-l="pt">O acoplamento F_amp&harr;&delta;_amp segue em aberto (roadmap #4), mas com uma precisão importante: a <b>capacidade já existe no engine, desligada por padrão</b> — em modo deslocamento os dois são tratados como independentes <i>no default</i>, embora fisicamente F_amp &le; &mu;&middot;F_0 em slip pleno. O que falta não é construir, é <b>calibrar per-rig e adotar sob gate</b>; a excitação composta de Yang (2021) é o alvo natural. Em todos estes pontos vale a mesma doutrina: uma falsificação aponta uma FORMA faltante — um mecanismo, um expoente, um acoplamento — não um coeficiente a ajustar. Por isso o refit (B2) NÃO foi rodado onde nenhuma constante congelada carrega a dependência: registrar a falsificação AS-IS é o resultado científico.</span><span data-l="en">The F_amp&harr;&delta;_amp coupling stays open (roadmap #4), with one important precision: the <b>capability already exists in the engine, off by default</b> — in displacement mode the two are treated as independent <i>in the default</i>, though physically F_amp &le; &mu;&middot;F_0 in full slip. What is missing is not building it but <b>calibrating it per rig and adopting it under a gate</b>; Yang (2021)'s composite excitation is the natural target. At all these points the same doctrine holds: a falsification points to a MISSING FORM — a mechanism, an exponent, a coupling — not a coefficient to tune. That is why the refit (B2) was NOT run where no frozen constant carries the dependence: recording the falsification AS-IS is the scientific result.</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Como o modelo V2 se posiciona</span><span data-l="en">How the V2 model stands</span></h2>
<p><span data-l="pt">O modelo V2 (<code>DynamicStiffnessAnalyzer</code>) é um sistema massa-mola-amortecedor energético: um vetor de estado lento evolui ciclo a ciclo sob uma matriz [K(s)] reavaliada (softening de Greenwood-Williamson), com seis mecanismos de perda em paralelo e um balanço de energia rigoroso (W_ext + &Delta;U = &Sigma; W_dissipado). As três camadas — analítica (Hooke, Coulomb, hélice, conservação), empírica (Norton, Norton-Bailey, Archard, Cattaneo-Mindlin, Su-N) e constantes físicas com procedência declarada — significam que, desde o Estágio B, não há nenhum multiplicador adimensional livre: cada constante é medida, de handbook, lida de uma feature do dado, ou fitada-este-rig, com a procedência declarada.</span><span data-l="en">The V2 model (<code>DynamicStiffnessAnalyzer</code>) is an energetic mass-spring-damper system: a slow state vector evolves cycle by cycle under a re-evaluated [K(s)] matrix (Greenwood-Williamson softening), with six loss mechanisms in parallel and a rigorous energy budget (W_ext + &Delta;U = &Sigma; W_dissipated). The three layers — analytical (Hooke, Coulomb, helix, conservation), empirical (Norton, Norton-Bailey, Archard, Cattaneo-Mindlin, Su-N) and physical constants with declared provenance — mean that, since Stage B, there is no free dimensionless multiplier: each constant is measured, from a handbook, read off a data feature, or fitted-this-rig, with its provenance declared.</span></p>
<p><span data-l="pt">A doutrina que emerge da confrontação com a biblioteca (&sect;8, reconfirmada 5&times;) é uma só: FORMAS e acoplamentos transferem cross-rig; NÍVEIS e constantes são por rig/par/junta. Com constantes congeladas de um único rig, o modelo vence o baseline no-loss em 34/46 curvas de M8 a M42, com gradientes de sinal certo — a generalização é das formas, não dos números. Cada fenômeno da literatura mapeia num mecanismo/capability: embedding &larr; fontes de relaxação/assentamento (Norton; tabela f_Z da VDI 2230); afrouxamento two-factor &larr; Junker/amplitude; surface_damage &larr; colapso de terceiro estágio (reaperto/TP7; Bauer 2024); conformação &larr; sobretorque/pressão (&sect;4.9, adotada no bloco canônico); taxa graduada e ratchet cinemático &larr; Lu 2024 e Bauer 2024; fretting &larr; Baydoun/Fouvry e H. Li 2022.</span><span data-l="en">The doctrine that emerges from the library confrontation (&sect;8, reconfirmed 5&times;) is a single one: FORMS and couplings transfer cross-rig; LEVELS and constants are per rig/pair/joint. With constants frozen from a single rig, the model beats the no-loss baseline on 34/46 curves from M8 to M42, with right-sign gradients — the generalization is of the forms, not the numbers. Each literature phenomenon maps to a mechanism/capability: embedding &larr; relaxation/settling sources (Norton; VDI 2230 f_Z table); two-factor loosening &larr; Junker/amplitude; surface_damage &larr; third-stage collapse (retighten/TP7; Bauer 2024); conformation &larr; overtorque/pressure (&sect;4.9, adopted into the canonical block); graded rate and kinematic ratchet &larr; Lu 2024 and Bauer 2024; fretting &larr; Baydoun/Fouvry and H. Li 2022.</span></p>
<p><span data-l="pt">Além dos seis mecanismos nucleares, o engine carrega ~44 capabilities opt-in default-inertes: bit-idênticas quando desligadas, ligadas só com dupla falsificação + gate pré-declarado + um número de procedência declarada. Ligar uma NÃO é fitar um tuner — é suprir uma forma faltante que uma falsificação apontou. Por isso o programa de legitimidade migrou de "fitar menos" para "prover procedência por constante", e o benchmark nulo de Grzejda (2026) fica como guarda: perda ~zero deve ser prevista como ~zero.</span><span data-l="en">Beyond the six core mechanisms, the engine carries ~44 default-inert opt-in capabilities: bit-identical when off, turned on only with double falsification + a pre-declared gate + a number with declared provenance. Turning one on is NOT fitting a tuner — it supplies a missing form a falsification pointed to. That is why the legitimacy program moved from "fit less" to "provide provenance per constant", and Grzejda (2026)'s null benchmark stands as a guard: ~zero loss must be predicted as ~zero.</span></p>
<p><span data-l="pt">Para o detalhamento, veja os demais Fundamentos: as <a href="concept_equations.html">equações</a> de cada mecanismo e o <a href="concept_coupling.html">acoplamento</a> two-factor que torna o sistema mais que a soma das partes; e as páginas por-variável para a procedência de cada constante.</span><span data-l="en">For the detail, see the other Foundations pages: the <a href="concept_equations.html">equations</a> of each mechanism and the two-factor <a href="concept_coupling.html">coupling</a> that makes the system more than the sum of its parts; and the per-variable pages for the provenance of each constant.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 8
    dict(
        slug="equations",
        nav_pt="9 · Equacionamento", nav_en="9 · Equations",
        title_pt="Equacionamento completo", title_en="Complete formulation",
        hook_pt="toda a matemática do engine, em um lugar",
        hook_en="the full engine math, in one place",
        body='''
<div class="sub"><span data-l="pt">Formulação completa do <code>DynamicStiffnessAnalyzer</code>.
Fonte canônica: <code>New_Theory/MODEL_MATH_REFERENCE.md</code>. Notação: x&prime;=velocidade,
x&Prime;=aceleração; d&#8322;=diâmetro de passo; slip=escorregamento por ciclo.</span>
<span data-l="en">Complete formulation of the <code>DynamicStiffnessAnalyzer</code>. Canonical source:
<code>New_Theory/MODEL_MATH_REFERENCE.md</code>. Notation: x&prime;=velocity, x&Prime;=acceleration;
d&#8322;=pitch diameter; slip=per-cycle slip.</span></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">1. Geometria e rigidezes derivadas</span><span data-l="en">1. Geometry and derived stiffnesses</span></h2>
<div class="eq">k_b = E &middot; A_s / L_eff            (rigidez axial do parafuso / bolt axial stiffness)
&beta;   = arctan( p / (&pi; &middot; d&#8322;) )      (angulo de helice / helix angle)
lead/rad = p / (2&pi;)                (avanco por radiano / lead per radian)
d&#8322;  = d &minus; 0.6495 &middot; p            (ISO 724);   A_contact = &pi;( r_bearing&sup2; &minus; r_furo&sup2; )
k_j_ax(F_0) = k_j_init &middot; (F_0 / F_0_init)^&alpha;_GW      (softening Greenwood-Williamson)
&Phi;_eff = min( k_b / (k_b + k_j_ax) , 1 )                 (Fator 1 / Factor 1)</div>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">2. Equação de movimento e estado lento</span><span data-l="en">2. Equation of motion and slow state</span></h2>
<div class="eq">[M] &middot; x&Prime; + [C(s)] &middot; x&prime; + [K(s)] &middot; x = F(t)      ([C] = &alpha;[M] + &beta;[K])
s = ( F_0, &delta;_emb, &delta;_creep, &delta;_wear, &delta;_fret, &theta;_loose, D, D_fat, W_slip_acc, W_conf )</div>
<p><span data-l="pt">Conversão comum dos 4 mecanismos de profundidade (encurtamento da pilha):</span>
<span data-l="en">Common conversion of the 4 depth mechanisms (stack shortening):</span></p>
<div class="eq">&Delta;F_0 = &minus; k_b &middot; &Delta;&delta;        (F_0 &larr; max(F_0 + &Sigma; &Delta;F_0, 0) apos somar os 6 mecanismos)</div>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">3. Os seis mecanismos de perda</span><span data-l="en">3. The six loss mechanisms</span></h2>
<p><b>Embedding</b> (Norton):</p>
<div class="eq">&delta;_target = emb_depth &middot; S_conf &middot; S_&rho; + emb_load_frac &middot; g_slip &middot; F_0_init / k_b
&Delta;&delta;     = max(&delta;_target &minus; &delta;_emb, 0) &middot; (1 &minus; e^(&minus;1/N_emb))
&delta;_emb(N)  = &delta;_target &middot; (1 &minus; e^(&minus;N/N_emb))       (junta virgem / virgin joint)
S_conf = min(1, (p_ref_emb / p_init)^emb_conform_exp),  p_init = F_0_init / A_contact
S_&rho;   = min(1, (&rho; / rho_ref_emb)^emb_amp_exp),      &rho; = F_ax_amp / F_0_init</div>
<p><b>Creep</b> (Norton-Bailey log-t),  t = N/f:</p>
<div class="eq">&Delta;&delta; = C_creep &middot; F_0 &middot; [ ln(t + t_0) &minus; ln(t &minus; 1/f + t_0) ] &middot; S_creep</div>
<p><b>Wear</b> (Archard),  K/H = k_wear_spec (ou K_archard/hardness):</p>
<div class="eq">d_wear = (K/H) &middot; F_0 &middot; (4 &middot; slip) / A_contact
d_wear &middot;= (1 + k_dmg_wear &middot; D);   K_eff = K &middot; (1 + (k_run &minus; 1) &middot; e^(&minus;N/N_wear_run))</div>
<p><b>Rotational loosening</b> (two-factor):</p>
<div class="eq">F_ax = F_amp &middot; cos&theta;;   F_tr = F_amp &middot; sin&theta;
&Phi;_tr_active = tr_loose_gain  (se F_tr &ge; F_slip)  senao 0.01
L_total = hypot( &Phi;_ax &middot; sin&beta; &middot; F_ax , &Phi;_tr &middot; cos&beta; &middot; F_tr );   T_loose = L_total &middot; d&#8322;/2
T_resist = &mu;_th &middot; F_0 &middot; d&#8322;/(2 cos30&deg;) + &mu;_brg_eff &middot; F_0 &middot; r_bearing
se T_loose &gt; T_resist:  &Delta;&theta; = gates &middot; (T_loose &minus; T_resist) / k_torsional
&Delta;F_0 = &minus; k_b &middot; (p / 2&pi;) &middot; &Delta;&theta;
k_torsional = k_j_init &middot; d&#8322;/2  (legacy)  |  &eta; &middot; G &middot; J / L_eff, J = &pi; d&#8322;&#8308;/32  (bolt_torsion)
graded_scrit:  &Delta;&theta; = gates &middot; k_loose_graded &middot; max(0, slip &minus; s_crit_loose) / (d&#8322;/2)</div>
<p><b>Thread fretting</b> (axial, &prop; A_F),  fret_dist = 4 &middot; F_ax / k_b:</p>
<div class="eq">d_fret = k_thread_fret &middot; (K/H) &middot; F_0 &middot; fret_dist / A_s &middot; (f_ref_fret/f)^fret_freq_exp &middot; g_partial
&Delta;F_0 = &minus; k_b &middot; d_fret     &rArr;   &Delta;F_0 &prop; &minus; F_0 &middot; A_F   (k_b cancela)</div>
<p><b>Fatigue</b> (Su-N bilinear + Goodman + Miner),  &sigma;_m = F_0/A_s:</p>
<div class="eq">&sigma;_a = K_t &middot; |F_amp| / A_s;   &sigma;_ar = &sigma;_a / (1 &minus; &sigma;_m/&sigma;_uts)
N_f = &infin; (&sigma;_ar &le; &sigma;_e)  |  C_1 &middot; &sigma;_ar^(&minus;m_1) (&ge; knee)  |  C_2 &middot; &sigma;_ar^(&minus;m_2)
&Delta;D_fat = 1/N_f;   fratura (D_fat &ge; 1):  &Delta;F_0 = &minus;(F_0 &minus; fatigue_residual_frac &middot; F_0_init)</div>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">4. Gates e funções constitutivas</span><span data-l="en">4. Gates and constitutive functions</span></h2>
<div class="eq">F_slip = 0.46 &middot; &mu;_brg_eff &middot; F_0                         (Pai-Hess 2002)
&delta;_t = F_slip / k_tr;   k_tr = 0.3 &middot; k_j_init (axial_frac) | c_bend &middot; E &middot; I / L_eff&sup3; (bending), I = &pi; d&#8322;&#8308;/64
slip = max(0, &delta;_amp &minus; &delta;_free &minus; F_slip/k_tr)          (disp-mode)
&mu;_brg_eff = &mu;_bearing &middot; max(1 &minus; k_dmg_mu &middot; D, 0)
slip_onset_gate:     g = x^k/(x^k+1),  x = W_slip_acc/slip_onset_W        (incubacao)
conformation_gate:   g = W_conf_ref/(W_conf + W_conf_ref)                 (arresto, fecha 1&rarr;0)
self_locking_gate:   g = max(0, 1 &minus; F_min/F_0),  F_min = loose_arrest_floor &middot; F_0_init
partial_slip_gate:   r = Q/(&mu; &middot; F_0 &middot; &kappa;);  g = 1 &minus; (1 &minus; r)^partial_slip_exp   (r&lt;1)
damage:  dD = c_D &middot; dwell &middot; (W_slip_cycle / W_ref) &middot; (1 &minus; D) &middot; onset,  dwell = (f_ref_dmg/f)^dmg_dwell_exp
W_slip_cycle = dE_wear + dE_loose (+ dE_partial);   W_slip_acc += 4 &middot; &mu;_eff &middot; F_0 &middot; slip</div>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">5. Balanço de energia e o laço step_cycle</span><span data-l="en">5. Energy balance and the step_cycle loop</span></h2>
<div class="eq">W_ext + &Delta;U_elastica = &Sigma; W_dissipada;    U(F) = F&sup2; / (2 &middot; k_b);    residual &asymp; 0</div>
<p><span data-l="pt">Um ciclo do laço lento (<code>step_cycle</code>):</span>
<span data-l="en">One slow-loop cycle (<code>step_cycle</code>):</span></p>
<ol class="refs">
<li><span data-l="pt">lê o estado de início (F_0, D, W_slip_acc, W_conf);</span><span data-l="en">read start-of-cycle state (F_0, D, W_slip_acc, W_conf);</span></li>
<li><span data-l="pt">resolve o slip transversal;</span><span data-l="en">resolve transverse slip;</span></li>
<li><span data-l="pt">consulta os 6 mecanismos em paralelo (mesmo F_0 de início) + gates;</span><span data-l="en">query the 6 mechanisms in parallel (same start F_0) + gates;</span></li>
<li><span data-l="pt">soma os &Delta;F_0 e atualiza F_0;</span><span data-l="en">sum the &Delta;F_0 and update F_0;</span></li>
<li><span data-l="pt">atualiza os estados de profundidade;</span><span data-l="en">update the depth states;</span></li>
<li><span data-l="pt">atualiza D e os acumuladores (lidos no próximo ciclo);</span><span data-l="en">update D and the accumulators (read next cycle);</span></li>
<li><span data-l="pt">fecha o budget de energia;</span><span data-l="en">close the energy budget;</span></li>
<li><span data-l="pt">emite o CycleSnapshot (ratio, decomposição, D, ângulo, energias).</span><span data-l="en">emit the CycleSnapshot (ratio, decomposition, D, angle, energies).</span></li>
</ol>
<p class="intro"><span data-l="pt">Os campos individuais (constantes, modos, capabilities) e suas
equações específicas estão em cada página de variável; a referência matemática completa é
<code>MODEL_MATH_REFERENCE.md</code>.</span>
<span data-l="en">The individual fields (constants, modes, capabilities) and their specific equations are on
each variable page; the complete math reference is <code>MODEL_MATH_REFERENCE.md</code>.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 8
    dict(
        slug="references",
        nav_pt="10 · Referências", nav_en="10 · References",
        title_pt="Referências", title_en="References",
        hook_pt="leis clássicas, normas e fontes de calibração",
        hook_en="classical laws, standards and calibration sources",
        body='''
<div class="sub"><span data-l="pt">Cada forma do modelo vem de uma lei publicada; cada constante de
uma fonte com procedência. Bibliografia por papel.</span>
<span data-l="en">Every model form comes from a published law; every constant from a source with
provenance. Bibliography by role.</span></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Leis constitutivas (formas empíricas)</span><span data-l="en">Constitutive laws (empirical forms)</span></h2>
<ul class="refs">
<li><b>Norton</b> &mdash; <span data-l="pt">assentamento/embedding (relaxação exponencial).</span><span data-l="en">embedding (exponential relaxation).</span></li>
<li><b>Norton &amp; Bailey</b> &mdash; <span data-l="pt">creep logarítmico no tempo.</span><span data-l="en">logarithmic-in-time creep.</span></li>
<li><b>Archard, J.F. (1953)</b>, <i>J. Appl. Phys.</i> 24(8) &mdash; <span data-l="pt">lei de desgaste (volume &prop; carga &middot; distância / dureza).</span><span data-l="en">wear law (volume &prop; load &middot; distance / hardness).</span></li>
<li><b>Greenwood, J.A. &amp; Williamson, J.B.P. (1966)</b>, <i>Proc. R. Soc. A</i> 295 &mdash; <span data-l="pt">contato de superfícies rugosas (softening da rigidez com a carga).</span><span data-l="en">rough-surface contact (load-dependent stiffness softening).</span></li>
<li><b>Cattaneo, C. (1938)</b> / <b>Mindlin, R.D. (1949)</b>, <i>J. Appl. Mech.</i> 16 &mdash; <span data-l="pt">contato tangencial: micro-slip parcial vs gross slip.</span><span data-l="en">tangential contact: partial micro-slip vs gross slip.</span></li>
<li><b>Basquin (1910)</b> / <b>Wohler</b> + <b>Goodman</b> + <b>Miner (1945)</b>, <i>J. Appl. Mech.</i> 12 &mdash; <span data-l="pt">curva S-N, correção de tensão média, dano acumulado (fadiga).</span><span data-l="en">S-N curve, mean-stress correction, cumulative damage (fatigue).</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Atrito, escorregamento e afrouxamento</span><span data-l="en">Friction, slip and loosening</span></h2>
<ul class="refs">
<li><b>Pai, N.G. &amp; Hess, D.P. (2002)</b>, <i>J. Sound Vib.</i> &mdash; <span data-l="pt">afrouxamento por cargas de cisalhamento dinâmicas; onset de slip (fator 0.46).</span><span data-l="en">loosening under dynamic shear loads; slip onset (factor 0.46).</span></li>
<li><b>Junker, G.H. (1969)</b>, <i>SAE 690055</i> (base do <b>DIN 65151</b>) &mdash; <span data-l="pt">ensaio de vibração transversal (o ensaio-padrão aqui).</span><span data-l="en">transverse-vibration test (the standard test here).</span></li>
<li><b>Vingsbo, O. &amp; Soderberg, S. (1988)</b>, <i>Wear</i> 126 &mdash; <span data-l="pt">mapas de fretting (dose de óxido/dwell &prop; 1/freq).</span><span data-l="en">fretting maps (oxide dose/dwell &prop; 1/freq).</span></li>
<li><b>Zhang et al. (2019)</b> &mdash; <span data-l="pt">desgaste sublinear no running-in (~N^0.53).</span><span data-l="en">sublinear running-in wear (~N^0.53).</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Dinâmica estrutural e normas</span><span data-l="en">Structural dynamics and standards</span></h2>
<ul class="refs">
<li><b>Clough, R.W. &amp; Penzien, J.</b>, <i>Dynamics of Structures</i> &mdash; <span data-l="pt">amortecimento proporcional de Rayleigh [C]=&alpha;[M]+&beta;[K].</span><span data-l="en">Rayleigh proportional damping [C]=&alpha;[M]+&beta;[K].</span></li>
<li><b>VDI 2230</b> &mdash; <span data-l="pt">cálculo de juntas aparafusadas: tabela f_Z de assentamento por rugosidade, carga de prova.</span><span data-l="en">bolted-joint design: f_Z embedding table by roughness, proof load.</span></li>
<li><b>ISO 724</b> &mdash; <span data-l="pt">geometria de rosca métrica (área de tensão A_s, d&#8322;).</span><span data-l="en">metric thread geometry (stress area A_s, d&#8322;).</span></li>
<li><b>Schaumann, P. et al. (2015)</b> &mdash; <span data-l="pt">limite de fadiga de parafusos grandes (banda 46&ndash;63 MPa, âncora <code>fat_sigma_endurance</code>).</span><span data-l="en">large-bolt fatigue limit (band 46&ndash;63 MPa, anchor <code>fat_sigma_endurance</code>).</span></li>
<li><b>Qiao (2025)</b> + <b>Lu (2024) K-factor</b> &mdash; <span data-l="pt">atrito de aço seco (âncora <code>mu_dry</code> = 0.14&ndash;0.19).</span><span data-l="en">dry-steel friction (anchor <code>mu_dry</code> = 0.14&ndash;0.19).</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Fontes de calibração/validação (biblioteca BAS_V2)</span><span data-l="en">Calibration/validation sources (BAS_V2 library)</span></h2>
<p class="intro"><span data-l="pt">Curvas digitalizadas em <code>curve_library/digitized_csv/</code>; aparato e
matriz de ensaios em <code>curve_library/apparatus_notes/</code>; PDFs em <code>BAS_V2_papers/</code>.</span>
<span data-l="en">Digitized curves in <code>curve_library/digitized_csv/</code>; apparatus and test matrix in
<code>curve_library/apparatus_notes/</code>; PDFs in <code>BAS_V2_papers/</code>.</span></p>
<ul class="refs">
<li><b>Liu et al. (2025)</b>, <i>Sci. Rep.</i> &mdash; doi:10.1038/s41598-025-02936-6 &mdash; <span data-l="pt">M16 transversal, 3 estágios; take-up fixo &delta;_0.</span><span data-l="en">M16 transverse, 3 stages; fixed take-up &delta;_0.</span></li>
<li><b>Bauer et al. (2024)</b>, <i>Eng. Fail. Anal.</i> &mdash; doi:10.1016/j.engfailanal.2024.108404 &mdash; <span data-l="pt">joelho de colapso, s_crit&asymp;99&micro;m, espectro.</span><span data-l="en">collapse knee, s_crit&asymp;99&micro;m, spectrum.</span></li>
<li><b>Liu et al. (2017)</b>, <i>Tribol. Int.</i> &mdash; doi:10.1016/j.triboint.2017.05.037 &mdash; <span data-l="pt">AXIAL 30 Hz; abre o trilho axial e a unificação &rho;.</span><span data-l="en">AXIAL 30 Hz; opens the axial track and the &rho;-unification.</span></li>
<li><b>Lu et al. (2024)</b>, <i>Sensors</i> &mdash; doi:10.3390/s24113306 &mdash; <span data-l="pt">ratchet cinemático (T_loose/T_resist fixo vs colapso ~amplitude).</span><span data-l="en">kinematic ratchet (fixed T_loose/T_resist vs amplitude-collapse).</span></li>
<li><b>Rousseau et al. (2025)</b>, <i>Materials</i> &mdash; doi:10.3390/ma18020462 &mdash; <span data-l="pt">rigidez de membro (aço vs HDPE, t=10/12/14); &theta;(N).</span><span data-l="en">member stiffness (steel vs HDPE, t=10/12/14); &theta;(N).</span></li>
<li><b>Demir (2024)</b>, <i>EJRND</i> &mdash; doi:10.56038/ejrnd.v5i1.693 &mdash; <span data-l="pt">M8 fatorial (DIN 65151); &mu; do paper.</span><span data-l="en">M8 factorial (DIN 65151); paper &mu;.</span></li>
<li><b>Yang et al. (2021)</b>, <i>Shock &amp; Vib.</i> &mdash; doi:10.1155/2021/1441122 &mdash; <span data-l="pt">carregamento composto (acopla F_amp&harr;&delta;_amp).</span><span data-l="en">composite loading (couples F_amp&harr;&delta;_amp).</span></li>
<li><b>Yang et al. (2019)</b>, <i>Shock &amp; Vib.</i> &mdash; doi:10.1155/2019/2036509 &mdash; <span data-l="pt">amplitude variável em blocos.</span><span data-l="en">variable-amplitude blocks.</span></li>
<li><b>Karlsen et al. (2022)</b>, <i>Eng. Fail. Anal.</i> &mdash; doi:10.1016/j.engfailanal.2022.106590 &mdash; <span data-l="pt">M30/M42 (efeito de tamanho); HV vs Vibralock; c_bend per-especime.</span><span data-l="en">M30/M42 (size effect); HV vs Vibralock; per-specimen c_bend.</span></li>
<li><b>Sandia (2021)</b>, C-beam &mdash; doi:10.1007/978-3-030-47626-7_30 &mdash; <span data-l="pt">modal/flexão, baixa amplitude (modo força).</span><span data-l="en">modal/bending, low amplitude (force mode).</span></li>
<li><b>Z. Liu et al. (2022)</b>, <i>Structures</i> &mdash; doi:10.1016/j.istruc.2022.08.049 &mdash; <span data-l="pt">reaperto sucessivo (renovação de embedding, galling).</span><span data-l="en">successive retightening (embedding renewal, galling).</span></li>
<li><b>Y. Li et al. (2022)</b>, <i>Marine Structures</i> &mdash; doi:10.1016/j.marstruc.2022.103263 &mdash; <span data-l="pt">creep estático de contato (M16 304SS; eixo em minutos); âncora C_creep.</span><span data-l="en">static contact creep (M16 304SS; minutes axis); C_creep anchor.</span></li>
<li><b>H. Li et al. (2022)</b>, <i>Tribol. Int.</i> &mdash; doi:10.1016/j.triboint.2022.107933 &mdash; <span data-l="pt">axial &times; frequência (10/15/20 Hz); dwell do fretting; cliff Ti.</span><span data-l="en">axial &times; frequency (10/15/20 Hz); fretting dwell; Ti cliff.</span></li>
<li><b>Yang et al. (2023)</b>, <i>IJPEM</i> &mdash; doi:10.1007/s12541-023-00783-x &mdash; <span data-l="pt">modelo fenomenológico M8/M6 (ratchet + slip_onset).</span><span data-l="en">phenomenological model M8/M6 (ratchet + slip_onset).</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Biblioteca estendida (rodadas de deep-research)</span><span data-l="en">Extended library (deep-research rounds)</span></h2>
<p class="intro"><span data-l="pt">Fontes adicionais varridas nas rodadas de deep-research (lacunas G1&ndash;G8), além das 14 primárias
digitalizadas acima. DOIs e rotas de acesso em <code>curve_library/DEEP_RESEARCH_REPORT{,_R2,_R3,_R4}.md</code>.</span>
<span data-l="en">Additional sources swept in the deep-research rounds (gaps G1&ndash;G8), beyond the 14 primary digitized
ones above. DOIs and access routes in <code>curve_library/DEEP_RESEARCH_REPORT{,_R2,_R3,_R4}.md</code>.</span></p>
<ul class="refs">
<li class="refhead">Fretting &amp; energia (âncoras de pressão/wear) / Fretting &amp; energy (pressure/wear anchors)</li>
<li><b>Baydoun &amp; Fouvry (2019)</b>, <i>Wear 426&ndash;427:676&ndash;693</i> &mdash; doi:10.1016/j.wear.2018.12.022 &mdash; <span data-l="pt">Fretting flat-on-flat 35NCD16 com pressão quase-constante controlada + varredura de pressão/amplitude/frequência; melhor âncora do expoente de pressão do gate de conformação (regime abrasivo&rarr;adesivo condiciona o expoente).</span><span data-l="en">Flat-on-flat 35NCD16 fretting at controlled near-constant pressure with pressure/amplitude/frequency sweeps; best anchor for the conformance-gate pressure exponent (abrasive&rarr;adhesive regime conditions it).</span></li>
<li><b>Arnaud, Baydoun &amp; Fouvry (2021)</b>, <i>Tribology International 161:107077</i> &mdash; doi:10.1016/j.triboint.2021.107077 &mdash; <span data-l="pt">Coeficientes de desgaste energético separados por regime (adesivo vs abrasivo) dirigidos por oxigenação do contato; base física candidata p/ gate dependente de pressão. SIMULAÇÃO/modelagem (sem curvas F/F0).</span><span data-l="en">Energy wear coefficients split by regime (adhesive vs abrasive) driven by contact oxygenation; candidate physics for a pressure-dependent gate. Modeling only (no F/F0 curves).</span></li>
<li><b>Baydoun et al. (2021, companion)</b>, <i>arXiv preprint</i> &mdash; arXiv:2101.12014 &mdash; <span data-l="pt">Companion OA que estende Baydoun2019 e confirma a pressão constante do contato flat-on-flat.</span><span data-l="en">OA companion extending Baydoun2019; confirms the flat-on-flat constant-pressure setup.</span></li>
<li><b>Fouvry et al. (2007)</b>, <i>Tribology International 40:1428</i> &mdash; doi:10.1016/j.triboint.2007.02.011 &mdash; <span data-l="pt">Capacidade energética de desgaste (chi) por par tribológico; complemento da âncora G2 (âncora K_archard, não W_conf_ref).</span><span data-l="en">Energetic wear capacity (chi) per tribo-pair; G2 anchor complement (anchors K_archard, not W_conf_ref).</span></li>
<li><b>Fouvry et al. (2011)</b>, <i>Wear 271:1535</i> &mdash; doi:10.1016/j.wear.2011.01.060 &mdash; <span data-l="pt">Fretting com força normal variável em Ti64; história de pressão para a âncora de desgaste energético.</span><span data-l="en">Fretting under variable normal force on Ti64; pressure-history input for the energy-wear anchor.</span></li>
<li><b>Fouvry et al. (2017)</b>, <i>Tribology International 113:460</i> &mdash; doi:10.1016/j.triboint.2016.12.049 &mdash; <span data-l="pt">Expoente de potência friccional em Ti64 (par G8); refina a forma do expoente de pressão/wear.</span><span data-l="en">Frictional-power exponent on Ti64 (G8 pair); refines the pressure/wear exponent form.</span></li>
<li><b>Chu, Liu, Qin &amp; Yuan (2026)</b>, <i>Tribology International 223:112193</i> &mdash; doi:10.1016/j.triboint.2026.112193 &mdash; <span data-l="pt">Experimentos + FEM; limiar crítico de deslocamento transversal dependente de F0 e atrito (estilo s_crit do Bauer), acopla com o surface_damage D via evolução de mu/desgaste.</span><span data-l="en">Experiments + FEM; F0/friction-dependent transverse critical-displacement threshold (Bauer-style s_crit); couples to surface_damage D through mu/wear evolution.</span></li>

<li class="refhead">Creep / relaxação &amp; temperatura / Creep / relaxation &amp; temperature</li>
<li><b>Lakes group, UW-Madison (2007)</b>, <i>J. Eng. Mater. Technol. 129:48&ndash;54</i> &mdash; doi:10.1115/1.2400262 &mdash; <span data-l="pt">Tensão do parafuso in-situ por 1 semana a 220/240/260 &deg;C, aço sobre Al-Si fundido; Tabela 1 = constantes de compliance de creep por temperatura (proveniência estilo C_creep por par) + embedding ~10% + protocolo de reaperto.</span><span data-l="en">In-situ bolt stress over 1 week at 220/240/260 &deg;C, steel on cast Al-Si; Table 1 = creep-compliance constants per temperature (per-pair C_creep provenance) + ~10% embedding + retighten protocol.</span></li>
<li><b>(autores n/d) (2023)</b>, <i>J. Constr. Steel Res. 211:108211</i> &mdash; doi:10.1016/j.jcsr.2023.108211 &mdash; <span data-l="pt">4 materiais de parafuso (comum/galvanizado/inox/GFRP) &times; 3 ambientes; clamp force vs tempo + termo de settling inicial (creep por par + ambiente).</span><span data-l="en">4 bolt materials (plain/galvanized/stainless/GFRP) &times; 3 environments; clamp force vs time + initial settling term (per-pair creep + environment).</span></li>
<li><b>(autores n/d) (2020)</b>, <i>Advances in Mechanical Engineering 12(12)</i> &mdash; doi:10.1177/1687814020975919 &mdash; <span data-l="pt">Pré-aperto e mecanismo de relaxação sob carga transversal (Gold OA SAGE); relaxação transversal complementar.</span><span data-l="en">Bolt pre-tightening and relaxation mechanism under transverse load (Gold OA); complementary transverse relaxation.</span></li>

<li class="refhead">Juntas compósitas/CFRP / Composite/CFRP joints</li>
<li><b>Pelletier, Caccese &amp; Berube (2009)</b>, <i>Composite Structures 89(2):285&ndash;293</i> &mdash; doi:10.1016/j.compstruct.2008.07.031 &mdash; <span data-l="pt">Relaxação de clamp-up &ge;3 meses (regimes primário+secundário) em par compósito-metal, com sequências de reaperto e efeitos térmicos; 3 formas funcionais ajustadas (relatório companion DTIC ADA429921 = programa experimental completo).</span><span data-l="en">Clamp-up stress relaxation &ge;3 months (primary+secondary) in a composite-metal pair, with retighten sequences and thermal effects; 3 fitted forms (companion DTIC report ADA429921 = full experimental program).</span></li>
<li><b>Yang, An, Chen &amp; Zou (2023)</b>, <i>Advances in Mechanical Engineering 15(1)</i> &mdash; doi:10.1177/16878132221145342 &mdash; <span data-l="pt">Rig biaxial (2 atuadores MTS), CFRP 48 plies&ndash;aço, jet nut MJ6 SEM rotação; curvas em tempo real + varredura de F0 (6/8/10 kN); decomposição de embedment por modo (transversal/axial/biaxial no mesmo rig).</span><span data-l="en">Biaxial rig (2 MTS actuators), CFRP 48-ply&ndash;steel, MJ6 jet nut (no rotation); real-time curves + F0 sweep (6/8/10 kN); embedment decomposition by load mode (transverse/axial/biaxial, one rig).</span></li>
<li><b>Tong (2024)</b>, <i>Polymer Composites</i> &mdash; doi:10.1002/pc.28378 &mdash; <span data-l="pt">Relaxação de preload em juntas CFRTP-SMC vs temperatura e preload inicial, 240 h.</span><span data-l="en">Preload relaxation in CFRTP-SMC joints vs temperature and initial preload, 240 h.</span></li>
<li><b>(autores n/d) (2024)</b>, <i>Applied Composite Materials</i> &mdash; doi:10.1007/s10443-024-10214-3 &mdash; <span data-l="pt">Relaxação de preload em juntas CFRP em ambiente térmico-oxigênio, 25&rarr;150 &deg;C (retenção 95,0&rarr;79,8%) + varredura de interferência; modelo + experimento.</span><span data-l="en">CFRP bolted-joint preload relaxation under thermal-oxygen environment, 25&rarr;150 &deg;C (retention 95.0&rarr;79.8%) + interference sweep; model + experiment.</span></li>
<li><b>(autores n/d) (2018)</b>, <i>venue n/d</i> &mdash; ResearchGate 322431887 &mdash; <span data-l="pt">Resposta tempo-temperatura da relaxação de preload em juntas compósitas parafusadas; curvas F(t) vs temperatura (térmico/compósito).</span><span data-l="en">Time-temperature response of preload relaxation in bolted composite joints; F(t) vs temperature curves (thermal/composite).</span></li>

<li class="refhead">Reaperto &amp; lubrificação / Retightening &amp; lubrication</li>
<li><b>Alsardia (2024)</b>, <i>Acta Polytechnica Hungarica 21(2):133&ndash;150</i> &mdash; acta.uni-obuda.hu (OA) &mdash; <span data-l="pt">20 reapertos &times; 4 lubrificações (as-is/seco/MoS2/oleado), M8&times;40 10.9, ISO 16047; oleado SOBE ~20% e estabiliza &mdash; âncora direta de k_emb_renew + atrito por lube. Estático (não Junker).</span><span data-l="en">20 retightenings &times; 4 lubrications (as-is/dry/MoS2/oiled), M8&times;40 10.9, ISO 16047; oiled RISES ~20% and stabilizes &mdash; direct anchor for k_emb_renew + per-lube friction. Static (not Junker).</span></li>
<li><b>Sun et al. (2025)</b>, <i>Engineering Failure Analysis :110030</i> &mdash; doi:10.1016/j.engfailanal.2025.110030 &mdash; <span data-l="pt">Reapertos cíclicos de porca auto-frenante MJ8 prateada; óxido de prata sobe o atrito e mantém preload &mdash; reaperto por-lube além do Z.Liu2022 (parte FEM; preprint SSRN 5347913).</span><span data-l="en">Cyclic retightenings of silvered self-locking MJ8 nut; silver oxide raises friction and holds preload &mdash; per-lube retighten beyond Z.Liu2022 (partly FEM; SSRN preprint 5347913).</span></li>
<li><b>Sun et al. (2025)</b>, <i>Engineering Failure Analysis 169:109235</i> &mdash; doi:10.1016/j.engfailanal.2024.109235 &mdash; <span data-l="pt">Junker M8/M10/M12 porca crimpada vs padrão (série de tamanho num rig); ramo axial é S-N (fadiga), não decaimento de preload.</span><span data-l="en">Junker M8/M10/M12 crimped nut vs standard (size series, one rig); axial branch is S-N (fatigue), not preload decay.</span></li>
<li><b>Eccles, Sherrington &amp; Arnell (2010)</b>, <i>Proc. IMechE Part C 224(2):483&ndash;495</i> &mdash; doi:10.1243/09544062JMES1493 &mdash; <span data-l="pt">Junker modificado (macacos hidráulicos): transversal + axial constante/intermitente, porcas nylon-insert novas vs reusadas; limiar quantitativo de destacamento (forma falsificável p/ rotation-onset/colapso).</span><span data-l="en">Modified Junker (hydraulic jacks): transverse + constant/intermittent axial, nylon-insert nuts new vs reused; quantitative detachment threshold (falsifiable form for rotation-onset/collapse).</span></li>
<li><b>(autores n/d) (2022)</b>, <i>Chinese Journal of Aeronautics 35(2)</i> &mdash; doi:10.1016/j.cja.2020.12.038 &mdash; <span data-l="pt">Review de métodos anti-afrouxamento; compila curvas Junker de múltiplos dispositivos (referência p/ locking_device_type).</span><span data-l="en">Review of anti-loosening methods; compiles Junker curves for multiple devices (reference for locking_device_type).</span></li>

<li class="refhead">Axial &amp; sinal de A_F / Axial &amp; the A_F signal</li>
<li><b>Liu et al. (2016)</b>, <i>Wear 346&ndash;347:66&ndash;77</i> &mdash; doi:10.1016/j.wear.2015.10.012 &mdash; <span data-l="pt">Mesmo grupo/rig do Liu2017, paper anterior e distinto; decaimento de clamp force axial com varredura de torque &times; amplitude + contraste MoS2 vs seco (estende d(afrouxamento)/d(A_F) num rig já calibrado).</span><span data-l="en">Same group/rig as Liu2017, earlier distinct paper; axial clamp-force decay with torque &times; amplitude sweep + MoS2 vs dry contrast (extends d(loosening)/d(A_F) on an already-calibrated rig).</span></li>
<li><b>Basava &amp; Hess (1998)</b>, <i>J. Sound and Vibration 210(2):255&ndash;265</i> &mdash; doi:10.1006/jsvi.1997.1330 &mdash; <span data-l="pt">CONTROLE de sinal (SIMULAÇÃO &mdash; reclassificado, não experimental): clamp force axial pode ficar estável, CAIR ou SUBIR &mdash; restrição que o mecanismo proporcional a A_F deve respeitar. Transientes curtos.</span><span data-l="en">Sign CONTROL (SIMULATION &mdash; reclassified, not experimental): axial clamp force can stay, DROP or RISE &mdash; constraint the A_F-proportional mechanism must respect. Short transients.</span></li>
<li><b>Liu/Zhu group (torsional study)</b>, <i>lead menor</i> &mdash; ResearchGate 329654266 &mdash; <span data-l="pt">Lead menor (não priorizado): afrouxamento sob carga torsional &mdash; modo de carga NÃO modelado pelo V2.</span><span data-l="en">Minor lead (deprioritized): loosening under torsional load &mdash; load mode NOT modeled by V2.</span></li>

<li class="refhead">Tamanho/material &amp; controles / Size/material &amp; controls</li>
<li><b>Grzejda, Parus &amp; Kwiatkowski (2026)</b>, <i>Materials 19:1414</i> &mdash; doi:10.3390/ma19071414 &mdash; <span data-l="pt">CONTROLE NEGATIVO: 9 variantes cíclicas (Instron 8850, 22 kN, amplitude 10/20 kN) SEM perda de preload (&plusmn;2%); o modelo deve prever ~zero perda.</span><span data-l="en">NEGATIVE control: 9 cyclic variants (Instron 8850, 22 kN, 10/20 kN amplitude) with NO preload loss (&plusmn;2%); model must predict ~zero loss.</span></li>
<li><b>Yang et al. (2025)</b>, <i>Materials</i> &mdash; doi:10.3390/ma18051069 &mdash; <span data-l="pt">Companion OA do modelo fenomenológico IJPEM (paywall): fornece as condições de ensaio M6/M8 (proveniência das condições, não curvas novas).</span><span data-l="en">OA companion of the IJPEM phenomenological model (paywalled): supplies the M6/M8 test conditions (conditions provenance, not new curves).</span></li>
<li><b>(autores n/d) (2024)</b>, <i>Structures</i> &mdash; Elsevier PII S2352012424016382 &mdash; <span data-l="pt">Lead menor (não priorizado, confirmar curvas): estudo teórico+experimental do comportamento de dano de juntas parafusadas sob cargas cíclicas.</span><span data-l="en">Minor lead (deprioritized, curves unconfirmed): theoretical+experimental study of bolted-joint damage behavior under cyclic loads.</span></li>
<li><b>Rafik et al. (2018)</b>, <i>JCM 2018 (AMDEM)</i> &mdash; HAL hal-02119945 &mdash; <span data-l="pt">Lead menor (não priorizado; HAL bloqueado por Anubis): grupo Rafik/AMDEM.</span><span data-l="en">Minor lead (deprioritized; HAL bot-blocked): Rafik/AMDEM group.</span></li>
</ul>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Documentos internos</span><span data-l="en">Internal documents</span></h2>
<ul class="refs">
<li><code>New_Theory/MODEL_MATH_REFERENCE.md</code> &mdash; <span data-l="pt">referência matemática completa.</span><span data-l="en">complete math reference.</span></li>
<li><code>New_Theory/MODEL_LEGITIMACY.md</code> &mdash; <span data-l="pt">física-vs-overfitting, falsificações (&sect;4.x), procedência.</span><span data-l="en">physics-vs-overfitting, falsifications (&sect;4.x), provenance.</span></li>
<li><code>Models/CALIBRATION_AND_VALIDATION/curve_library/</code> &mdash; <span data-l="pt">200 curvas extraídas + 108 digitalizadas + apparatus_notes.</span><span data-l="en">200 extracted + 108 digitized curves + apparatus_notes.</span></li>
</ul>
</div>
'''),

    # ---------------------------------------------------------------- 11 (anatomia)
    dict(
        slug="anatomy",
        nav_pt="11 · Anatomia da curva", nav_en="11 · Anatomy of the curve",
        title_pt="Anatomia de uma curva de afrouxamento", title_en="Anatomy of a loosening curve",
        hook_pt="ler a forma: estágios, joelho e piso",
        hook_en="reading the shape: stages, knee and floor",
        widget="anatomy",
        body='''
<div class="sub"><span data-l="pt">Toda curva de F/F0 conta a mesma história física. Abaixo, a
curva-padrão (M16, ±0.5 mm) é dissecada: o eixo X está em escala <b>logarítmica</b> para separar as
fases, e cada faixa traz o mecanismo que domina a perda ali.</span>
<span data-l="en">Every F/F0 curve tells the same physical story. Below, the standard curve (M16, ±0.5
mm) is dissected: the X axis is <b>logarithmic</b> to separate the phases, and each band names the
mechanism that dominates the loss there.</span></div>

<div id="cw"></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Os três estágios</span><span data-l="en">The three stages</span></h2>
<ul class="refs">
<li><span data-l="pt"><b>I &mdash; Assentamento</b>: nos primeiros ciclos a pré-carga cai rápido porque as
asperezas das superfícies se acomodam (embedding, lei de Norton) somadas à fluência inicial (creep).
É a queda íngreme à esquerda.</span><span data-l="en"><b>I &mdash; Settling</b>: in the first cycles the
preload drops fast as the surface asperities bed in (embedding, Norton law) plus initial creep. It is
the steep drop on the left.</span></li>
<li><span data-l="pt"><b>II &mdash; Afrouxamento</b>: o <b>joelho</b> marca a virada para o regime dirigido
por escorregamento &mdash; desgaste (Archard) e rotação da porca (two-factor) sustentam o
declínio.</span><span data-l="en"><b>II &mdash; Loosening</b>: the <b>knee</b> marks the turn into the
slip-driven regime &mdash; wear (Archard) and nut rotation (two-factor) sustain the decline.</span></li>
<li><span data-l="pt"><b>III &mdash; Cauda</b>: a curva se aproxima do seu destino; a linha tracejada
marca o F/F0 final.</span><span data-l="en"><b>III &mdash; Tail</b>: the curve approaches its fate; the
dashed line marks the final F/F0.</span></li>
</ul>
<p class="intro"><span data-l="pt">As fronteiras aqui são por FRAÇÃO DE PERDA (45% / 80% do total), não
por ciclo fixo; o rótulo de cada faixa é o mecanismo dominante LIDO da decomposição real (ver
<a href="concept_mechanisms.html">Estado + mecanismos</a>).</span>
<span data-l="en">The boundaries here are by LOSS FRACTION (45% / 80% of the total), not a fixed cycle;
each band's label is the dominant mechanism READ from the real decomposition (see
<a href="concept_mechanisms.html">State + mechanisms</a>).</span></p>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Runaway ou saturação?</span><span data-l="en">Runaway or saturation?</span></h2>
<p><span data-l="pt">A cauda tem dois destinos possíveis, decididos pelo mesmo laço de realimentação
F0&rarr;[K]&rarr;&Phi;&rarr;afrouxamento&rarr;F0. Sem auto-travamento ela cai até ~0 (<b>runaway</b>).
Com um piso de auto-travamento (<code>loose_arrest_floor</code>) o laço encontra um ponto fixo estável e
a curva <b>satura</b> num patamar &mdash; vira uma S-curve. Veja a demonstração na página
<a href="concept_coupling.html">Acoplamento</a>.</span>
<span data-l="en">The tail has two possible fates, set by the same feedback loop
F0&rarr;[K]&rarr;&Phi;&rarr;loosening&rarr;F0. Without self-locking it falls to ~0 (<b>runaway</b>). With
a self-locking floor (<code>loose_arrest_floor</code>) the loop finds a stable fixed point and the curve
<b>saturates</b> at a plateau &mdash; it becomes an S-curve. See the demo on the
<a href="concept_coupling.html">Coupling</a> page.</span></p>
</div>
'''),

    # ---------------------------------------------------------------- 12 (glossario)
    dict(
        slug="glossary",
        nav_pt="12 · Glossário", nav_en="12 · Glossary",
        title_pt="Glossário: notação e termos", title_en="Glossary: notation and terms",
        hook_pt="símbolos, unidades e conceitos num só lugar",
        hook_en="symbols, units and concepts in one place",
        body='''
<div class="sub"><span data-l="pt">Os símbolos e termos usados no modelo e nas páginas de variáveis,
reunidos como referência rápida.</span><span data-l="en">The symbols and terms used across the model and
the variable pages, gathered as a quick reference.</span></div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Notação</span><span data-l="en">Notation</span></h2>
<div class="gloss-wrap"><table class="gloss-tbl">
<thead><tr>
<th><span data-l="pt">símbolo</span><span data-l="en">symbol</span></th>
<th><span data-l="pt">nome</span><span data-l="en">name</span></th>
<th><span data-l="pt">unid.</span><span data-l="en">unit</span></th>
<th><span data-l="pt">significado</span><span data-l="en">meaning</span></th>
</tr></thead><tbody>
<tr><td class="sym">F&#8320;</td><td><span data-l="pt">pré-carga</span><span data-l="en">preload</span></td><td class="unit">N</td><td><span data-l="pt">força de aperto axial atual do parafuso</span><span data-l="en">current axial clamp force of the bolt</span></td></tr>
<tr><td class="sym">F/F&#8320;</td><td><span data-l="pt">pré-carga normalizada</span><span data-l="en">normalized preload</span></td><td class="unit">&ndash;</td><td><span data-l="pt">eixo Y de todas as curvas (1 = aperto pleno)</span><span data-l="en">Y axis of every curve (1 = full clamp)</span></td></tr>
<tr><td class="sym">&delta;_emb</td><td><span data-l="pt">assentamento</span><span data-l="en">embedding depth</span></td><td class="unit">m</td><td><span data-l="pt">profundidade acomodada nas asperezas (Norton)</span><span data-l="en">depth bedded into the asperities (Norton)</span></td></tr>
<tr><td class="sym">&delta;_creep</td><td><span data-l="pt">fluência</span><span data-l="en">creep</span></td><td class="unit">m</td><td><span data-l="pt">escoamento viscoplástico log-t (Norton-Bailey)</span><span data-l="en">log-t viscoplastic flow (Norton-Bailey)</span></td></tr>
<tr><td class="sym">&delta;_wear</td><td><span data-l="pt">desgaste</span><span data-l="en">wear</span></td><td class="unit">m</td><td><span data-l="pt">material removido no contato (Archard)</span><span data-l="en">material removed at the contact (Archard)</span></td></tr>
<tr><td class="sym">&theta;_loose</td><td><span data-l="pt">ângulo de afrouxamento</span><span data-l="en">loosening angle</span></td><td class="unit">rad</td><td><span data-l="pt">rotação acumulada da porca</span><span data-l="en">accumulated nut rotation</span></td></tr>
<tr><td class="sym">D</td><td><span data-l="pt">dano de superfície</span><span data-l="en">surface damage</span></td><td class="unit">&ndash;</td><td><span data-l="pt">estado [0,1]; reduz &mu; e amplifica o desgaste</span><span data-l="en">state [0,1]; lowers &mu; and amplifies wear</span></td></tr>
<tr><td class="sym">[K(s)]</td><td><span data-l="pt">rigidez dinâmica</span><span data-l="en">dynamic stiffness</span></td><td class="unit">N/m</td><td><span data-l="pt">matriz reavaliada a cada ciclo (Greenwood-Williamson)</span><span data-l="en">matrix re-evaluated each cycle (Greenwood-Williamson)</span></td></tr>
<tr><td class="sym">k_b</td><td><span data-l="pt">rigidez do parafuso</span><span data-l="en">bolt stiffness</span></td><td class="unit">N/m</td><td><span data-l="pt">rigidez axial do parafuso (Hooke)</span><span data-l="en">axial bolt stiffness (Hooke)</span></td></tr>
<tr><td class="sym">k_j</td><td><span data-l="pt">rigidez dos membros</span><span data-l="en">member stiffness</span></td><td class="unit">N/m</td><td><span data-l="pt">rigidez do pacote de membros/juntas</span><span data-l="en">clamped-member stack stiffness</span></td></tr>
<tr><td class="sym">k_tr</td><td><span data-l="pt">rigidez transversal de onset</span><span data-l="en">transverse onset stiffness</span></td><td class="unit">N/m</td><td><span data-l="pt">define o slip de onset (modo bending)</span><span data-l="en">sets the slip onset (bending mode)</span></td></tr>
<tr><td class="sym">&lambda;</td><td><span data-l="pt">passo da hélice</span><span data-l="en">helix lead</span></td><td class="unit">&ndash;</td><td><span data-l="pt">acoplamento axial-torcional (única fonte off-diagonal)</span><span data-l="en">axial-torsional coupling (the only off-diagonal source)</span></td></tr>
<tr><td class="sym">&Phi;</td><td><span data-l="pt">fator de afrouxamento</span><span data-l="en">loosening factor</span></td><td class="unit">&ndash;</td><td><span data-l="pt">ganho anisotrópico do afrouxamento (two-factor)</span><span data-l="en">anisotropic loosening gain (two-factor)</span></td></tr>
<tr><td class="sym">&mu;</td><td><span data-l="pt">atrito</span><span data-l="en">friction</span></td><td class="unit">&ndash;</td><td><span data-l="pt">coeficiente de Coulomb (Motosh, de torque+F&#8320;)</span><span data-l="en">Coulomb coefficient (Motosh, from torque+F&#8320;)</span></td></tr>
<tr><td class="sym">slip</td><td><span data-l="pt">escorregamento</span><span data-l="en">slip</span></td><td class="unit">m</td><td><span data-l="pt">curso relativo na interface por ciclo</span><span data-l="en">relative interface stroke per cycle</span></td></tr>
<tr><td class="sym">W_slip_acc</td><td><span data-l="pt">trabalho de slip acumulado</span><span data-l="en">accumulated slip work</span></td><td class="unit">J</td><td><span data-l="pt">dirige a incubação e o dano</span><span data-l="en">drives incubation and damage</span></td></tr>
<tr><td class="sym">C_creep</td><td><span data-l="pt">coeficiente de creep</span><span data-l="en">creep coefficient</span></td><td class="unit">&ndash;</td><td><span data-l="pt">Norton-Bailey; por par tribológico</span><span data-l="en">Norton-Bailey; per tribological pair</span></td></tr>
<tr><td class="sym">K_archard</td><td><span data-l="pt">coeficiente de Archard</span><span data-l="en">Archard coefficient</span></td><td class="unit">&ndash;</td><td><span data-l="pt">desgaste &prop; K&middot;(carga&middot;dist.)/dureza</span><span data-l="en">wear &prop; K&middot;(load&middot;dist.)/hardness</span></td></tr>
<tr><td class="sym">W_ext, &Delta;U, &Sigma;W_diss</td><td><span data-l="pt">energias</span><span data-l="en">energies</span></td><td class="unit">J</td><td><span data-l="pt">conservação: W_ext + &Delta;U = &Sigma;W_diss (residual ~0)</span><span data-l="en">conservation: W_ext + &Delta;U = &Sigma;W_diss (residual ~0)</span></td></tr>
<tr><td class="sym">MAE / RMSE</td><td><span data-l="pt">erro médio</span><span data-l="en">mean error</span></td><td class="unit">&ndash;</td><td><span data-l="pt">|modelo &minus; dado| médio / raiz do quadrático</span><span data-l="en">mean |model &minus; data| / root-mean-square</span></td></tr>
</tbody></table></div>
</div>

<div class="panel">
<h2 class="sec"><span data-l="pt">Termos</span><span data-l="en">Terms</span></h2>
<ul class="refs">
<li><span data-l="pt"><b>Assentamento (embedding)</b> &mdash; acomodação plástica das asperezas sob a pré-carga; forma de Norton que satura numa profundidade-alvo.</span><span data-l="en"><b>Embedding</b> &mdash; plastic bedding-in of the asperities under preload; a Norton form saturating at a target depth.</span></li>
<li><span data-l="pt"><b>Creep</b> &mdash; fluência viscoplástica dependente do tempo (log-t, Norton-Bailey), função da tensão de contato.</span><span data-l="en"><b>Creep</b> &mdash; time-dependent viscoplastic flow (log-t, Norton-Bailey), a function of contact stress.</span></li>
<li><span data-l="pt"><b>Desgaste (Archard)</b> &mdash; remoção de material &prop; carga &times; distância de slip / dureza.</span><span data-l="en"><b>Wear (Archard)</b> &mdash; material removal &prop; load &times; slip distance / hardness.</span></li>
<li><span data-l="pt"><b>Afrouxamento rotacional (two-factor)</b> &mdash; rotação da porca dirigida pela hélice &times; &Phi;, além do onset T_loose &gt; T_resist.</span><span data-l="en"><b>Rotational loosening (two-factor)</b> &mdash; nut rotation driven by the helix &times; &Phi;, beyond the onset T_loose &gt; T_resist.</span></li>
<li><span data-l="pt"><b>Gross-slip &times; micro-slip</b> &mdash; escorregamento macroscópico total vs parcial (regime de Cattaneo-Mindlin).</span><span data-l="en"><b>Gross-slip vs micro-slip</b> &mdash; full macroscopic sliding vs partial (Cattaneo-Mindlin regime).</span></li>
<li><span data-l="pt"><b>Incubação</b> &mdash; platô inicial antes do colapso; gate de Hill sobre W_slip_acc.</span><span data-l="en"><b>Incubation</b> &mdash; initial plateau before collapse; a Hill gate on W_slip_acc.</span></li>
<li><span data-l="pt"><b>Piso de auto-travamento (arrest floor)</b> &mdash; F_min/F&#8320; onde o afrouxamento estabiliza (S-curve, não runaway).</span><span data-l="en"><b>Self-locking arrest floor</b> &mdash; F_min/F&#8320; where loosening stabilizes (S-curve, not runaway).</span></li>
<li><span data-l="pt"><b>Ratchet cinemático (k_ratchet)</b> &mdash; rotação por ciclo &prop; caminho de gross-slip, como uma catraca.</span><span data-l="en"><b>Kinematic ratchet (k_ratchet)</b> &mdash; per-cycle rotation &prop; gross-slip path, like a ratchet.</span></li>
<li><span data-l="pt"><b>Conformação dependente de pressão</b> &mdash; perda extra sob alta pressão de contato; resolve o sobretorque.</span><span data-l="en"><b>Pressure-dependent conformance</b> &mdash; extra loss under high contact pressure; resolves the overtorque case.</span></li>
<li><span data-l="pt"><b>Runaway</b> &mdash; colapso realimentado F&#8320;&rarr;[K]&rarr;&Phi;&rarr;afrouxamento&rarr;F&#8320; até ~0.</span><span data-l="en"><b>Runaway</b> &mdash; feedback collapse F&#8320;&rarr;[K]&rarr;&Phi;&rarr;loosening&rarr;F&#8320; down to ~0.</span></li>
<li><span data-l="pt"><b>Disp-mode &times; force-mode</b> &mdash; controle por deslocamento imposto (Junker) vs por força (servo-hidráulico).</span><span data-l="en"><b>Disp-mode vs force-mode</b> &mdash; imposed-displacement control (Junker) vs force control (servo-hydraulic).</span></li>
<li><span data-l="pt"><b>Procedência (provenance)</b> &mdash; classe de origem de cada constante: medida, handbook, lida-do-dado ou fitada-neste-rig.</span><span data-l="en"><b>Provenance</b> &mdash; each constant's origin class: measured, handbook, data-implied or fitted-this-rig.</span></li>
<li><span data-l="pt"><b>Default-inerte</b> &mdash; capability opt-in que, no valor default, é bit-idêntica ao motor sem ela.</span><span data-l="en"><b>Default-inert</b> &mdash; an opt-in capability that, at its default, is bit-identical to the engine without it.</span></li>
</ul>
<p class="intro"><span data-l="pt">Definições completas campo a campo estão nas páginas de variáveis; a
matemática, na página <a href="concept_equations.html">Equacionamento</a>.</span>
<span data-l="en">Full field-by-field definitions live on the variable pages; the mathematics on the
<a href="concept_equations.html">Equations</a> page.</span></p>
</div>
'''),
])
