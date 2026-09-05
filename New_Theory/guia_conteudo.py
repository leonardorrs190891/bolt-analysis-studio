# -*- coding: utf-8 -*-
"""Conteudo do guia narrado: um passo por aba do programa, PT e EN.

Separado do gerador (`build_guia_narrado.py`) pelo mesmo motivo do
`help_content.py`: aqui e' texto, la' e' montagem. Cada passo tem

  chave      — nome do arquivo HTML e do print;
  print_     — chave da captura que o gerador tira do app naquele idioma;
  titulo     — (pt, en);
  narracao   — (pt, en): o que a voz diz. Escrito para ser OUVIDO: frases
               curtas, sem parenteses, sem siglas soltas, numeros por extenso
               quando a fala pede;
  controles  — lista de (nome_do_controle, (pt, en)): cada botao, campo e
               variavel visivel na tela daquele passo, um por linha. E' a parte
               que o pedido de 2026-09-04 exige: "explicando cada variavel e
               botao que aparecer". O NOME e' str quando o rotulo da tela e' o
               mesmo nas duas linguas (o inspector, a paleta e os dialogos
               legados sao em ingles nos dois idiomas) e (pt, en) quando a
               tela traduz — a pagina EN mostra o nome EN, como no print EN
               (defeito da 1a versao, 2026-09-05: nomes PT em paginas EN);
  erro_comum — (pt, en) opcional: o tropeco tipico e como sair.

Lexico (revisado em 2026-09-05, cruzado com os textos da tela e com o artigo):
  · os quatro mecanismos sao assentamento/embedding, fluencia/creep,
    desgaste/wear e rotacao da porca/nut rotation — os nomes do artigo e das
    chaves do motor; "settlement" nao se usa;
  · junta APARAFUSADA (nao "parafusada"); membros apertados/clamped members;
  · nomes de modulo (Model … Report) e os botoes Run, Stop e Step ficam em
    ingles nas duas linguas: substantivos proprios da interface;
  · ingles britanico, como nos menus (Analyse, digitised, metre).
O GLOSSARIO no fim e' a lista desses termos, com definicao, e vira uma pagina
propria em cada idioma.

A narracao e' sintetizada com a voz pt-BR-AntonioNeural (PT) e
en-US-AndrewNeural (EN); o texto escrito aparece na pagina como transcricao,
para quem le em vez de ouvir.
"""

VOZES = {"pt": "pt-BR-AntonioNeural", "en": "en-US-AndrewNeural"}

PASSOS = [
    dict(
        chave="00_introducao", print_="chrome_model",
        titulo=("O que o Bolt Analysis Studio faz", "What Bolt Analysis Studio does"),
        narracao=(
            "Bem-vindo ao Bolt Analysis Studio. Este programa prevê a perda de "
            "pré-carga em juntas aparafusadas: quanto um parafuso afrouxa, ciclo a "
            "ciclo, quando a junta vibra ou recebe carga repetida. Ele representa a "
            "junta como uma cadeia de massas, molas e amortecedores — a cabeça, a "
            "haste, a rosca, a porca, os membros apertados, e as interfaces de "
            "contato entre eles. Quatro mecanismos retiram pré-carga em paralelo: "
            "o assentamento das superfícies, a fluência, o desgaste nas faces que "
            "escorregam e a rotação da porca. O programa foi validado contra "
            "duzentas e sete curvas publicadas na literatura, e cada uma delas "
            "vem pronta para você abrir, olhar e modificar. Neste guia, uma "
            "página por aba, você vai ver o que cada botão e cada campo fazem.",
            "Welcome to Bolt Analysis Studio. This program predicts preload loss "
            "in bolted joints: how much a bolt loosens, cycle by cycle, when the "
            "joint vibrates or carries repeated load. It represents the joint as a "
            "chain of masses, springs and dampers — the head, the shank, the "
            "thread, the nut, the clamped members, and the contact interfaces "
            "between them. Four mechanisms remove preload in parallel: embedding "
            "of the surfaces, creep, wear on the faces that slip, and rotation of "
            "the nut. The program was validated against two hundred and seven "
            "curves published in the literature, and every one of them comes "
            "ready for you to open, inspect and modify. In this guide, one page "
            "per tab, you will see what every button and every field does."),
        controles=[
            (("Barra de módulos (1 Model … 6 Report)",
              "Module bar (1 Model … 6 Report)"),
             ("A trilha de trabalho, da esquerda para a direita. Cada número é "
              "um módulo; o passo atual fica destacado.",
              "The workflow track, left to right. Each number is a module; the "
              "current step is highlighted.")),
            (("Próximo →", "Next →"),
             ("Avança para o módulo seguinte sem procurar no menu.",
              "Advances to the next module without hunting through the menu.")),
            ("Step", ("O tipo de análise: Static-Preload calcula a pré-carga "
                      "estática; Coupled-Loosening simula o afrouxamento ciclo a "
                      "ciclo.",
                      "The analysis type: Static-Preload computes the static "
                      "preload; Coupled-Loosening simulates loosening cycle by "
                      "cycle.")),
            ("Run / Stop", ("Roda e interrompe a análise. Só ficam ativos no "
                            "módulo Analysis.",
                            "Runs and stops the analysis. Only enabled in the "
                            "Analysis module.")),
        ],
    ),
    dict(
        chave="01_comecar", print_="dialog_case_picker",
        titulo=("Três maneiras de começar", "Three ways to start"),
        narracao=(
            "Há três maneiras de colocar um modelo na tela. A primeira é o "
            "assistente de nova análise, no menu Arquivo ou pelo atalho control "
            "shift N: ele faz cinco perguntas e monta a cadeia completa. A segunda "
            "é abrir um projeto seu, salvo antes, com control O. A terceira, e a "
            "mais rápida para aprender, é importar um caso do artigo com control "
            "I: uma lista com as duzentas e cinco curvas do censo, cada uma com o "
            "artigo de origem, o erro do modelo e se ela atende ao critério. "
            "Escolha uma, e o modelo chega montado, com as constantes exatamente "
            "como foram adotadas no artigo. Comece por aqui: é a melhor maneira de "
            "ver um modelo bom antes de construir o seu.",
            "There are three ways to put a model on screen. The first is the "
            "new-analysis wizard, in the File menu or with control shift N: it "
            "asks five questions and assembles the whole chain. The second is to "
            "open a project of your own, saved earlier, with control O. The third, "
            "and the fastest way to learn, is to import a case from the paper "
            "with control I: a list of the two hundred and five curves of the "
            "census, each with its source paper, the model error and whether it "
            "meets the criterion. Pick one and the model arrives assembled, with "
            "the constants exactly as adopted in the paper. Start here: it is the "
            "best way to see a good model before building your own."),
        controles=[
            (("Arquivo → Nova análise… (Ctrl+Shift+N)",
              "File → New analysis… (Ctrl+Shift+N)"),
             ("Abre o assistente de cinco páginas.", "Opens the five-page wizard.")),
            (("Arquivo → Abrir projeto… (Ctrl+O)", "File → Open project… (Ctrl+O)"),
             ("Abre um arquivo .msd salvo por você.",
              "Opens an .msd file you saved.")),
            (("Arquivo → Importar caso da validação… (Ctrl+I)",
              "File → Import validation case… (Ctrl+I)"),
             ("Lista os casos do artigo por nome, com busca.",
              "Lists the paper's cases by name, with search.")),
            (("Campo de busca", "Search field"),
             ("Filtra por artigo, caso, referência ou DOI. "
              "Exemplos: lu2024, M8, Sensors.",
              "Filters by paper, case, reference or DOI. "
              "Examples: lu2024, M8, Sensors.")),
            (("Somente o censo do artigo", "Paper census only"),
             ("Marcado, mostra as duzentas e cinco curvas que o manuscrito conta; "
              "desmarcado, todas as duzentas e sete.",
              "Ticked, shows the two hundred and five curves the manuscript "
              "counts; unticked, all two hundred and seven.")),
            (("Coluna Censo", "Census column"),
             ("Se a curva entra nos números do artigo.",
              "Whether the curve is counted in the paper.")),
            (("Coluna Critério", "Criterion column"),
             ("Se o modelo atende às três pernas do critério de aceitação "
              "naquela curva.",
              "Whether the model meets the three legs of the acceptance "
              "criterion on that curve.")),
            (("Coluna MAE", "MAE column"),
             ("Erro médio absoluto do modelo, em fração da pré-carga. Quanto "
              "menor, melhor.",
              "Mean absolute error of the model, as a fraction of preload. "
              "Lower is better.")),
            (("Rodapé", "Footer"),
             ("A referência completa e o DOI clicável do caso selecionado.",
              "The full reference and clickable DOI of the selected case.")),
            (("Abrir", "Open"),
             ("Carrega o caso no módulo Model.",
              "Loads the case into the Model module.")),
        ],
        erro_comum=(
            "Ao salvar depois de importar, o programa pede um destino novo. Não é "
            "erro: os casos do artigo são reinstalados a cada atualização, então "
            "a sua cópia precisa morar em outro lugar.",
            "When you save after importing, the program asks for a new "
            "destination. That is not an error: the paper's cases are reinstalled "
            "on every update, so your copy must live somewhere else."),
    ),
    dict(
        chave="02_wizard", print_="wizard_p1",
        titulo=("O assistente de nova análise", "The new-analysis wizard"),
        narracao=(
            "O assistente monta um modelo em cinco páginas. Na primeira, você dá "
            "um nome ao projeto e escolhe a topologia da junta: parafuso único "
            "axial, junta de cisalhamento simples, flange, e assim por diante. "
            "Cada topologia já traz os elementos certos, inclusive as duas "
            "ligações de apoio, sob a cabeça e sob a porca, que são onde o "
            "afrouxamento acontece. Na segunda página, a bitola e a classe do "
            "parafuso, a espessura do flange e a pré-carga como fração do "
            "escoamento. Na terceira, o carregamento: transversal, axial ou "
            "combinado, controlado por deslocamento ou por força, com amplitude, "
            "frequência e número de ciclos. A quarta é opcional: um CSV de "
            "laboratório para calibrar depois. A quinta resume tudo. Clique em "
            "gerar modelo e ele abre no módulo Model.",
            "The wizard builds a model in five pages. On the first, you name the "
            "project and choose the joint topology: single axial bolt, single "
            "shear joint, flange, and so on. Each topology already carries the "
            "right elements, including the two bearing connections, under the "
            "head and under the nut, which are where loosening happens. On the "
            "second page, the bolt size and grade, the flange thickness and the "
            "preload as a fraction of yield. On the third, the loading: "
            "transverse, axial or combined, displacement- or force-controlled, "
            "with amplitude, frequency and number of cycles. The fourth is "
            "optional: a laboratory CSV to calibrate against later. The fifth "
            "summarises everything. Click generate model and it opens in the "
            "Model module."),
        controles=[
            (("Nome do projeto", "Project name"),
             ("Nome do modelo gerado; vazio usa o padrão.",
              "Name of the generated model; empty uses the default.")),
            (("Tipo de junta", "Joint type"),
             ("Lista de topologias; a descrição e os elementos gerados aparecem "
              "abaixo.",
              "List of topologies; the description and the generated elements "
              "appear below.")),
            (("Bitola do parafuso", "Bolt size"),
             ("M6 a M42; diâmetro e passo saem automaticamente.",
              "M6 to M42; diameter and pitch follow automatically.")),
            (("Classe do material", "Material grade"),
             ("Define escoamento e ruptura, e com eles a pré-carga em newtons.",
              "Sets yield and ultimate strength, and with them the preload in "
              "newtons.")),
            (("Espessura do flange (cada)", "Flange thickness (each)"),
             ("Espessura de cada membro apertado.",
              "Thickness of each clamped member.")),
            (("Pré-carga (% escoamento)", "Preload (% yield)"),
             ("Fração do escoamento aplicada no aperto. Setenta por cento é o "
              "típico da VDI 2230.",
              "Fraction of yield applied at tightening. Seventy percent is the "
              "VDI 2230 typical.")),
            (("Tipo de carregamento", "Loading type"),
             ("Transversal Junker, axial pulsante ou combinado.",
              "Transverse Junker, axial pulsating or combined.")),
            (("Modo de controle", "Control mode"),
             ("Deslocamento imposto, como numa bancada Junker, ou força imposta, "
              "como numa servo-hidráulica. O campo que não comanda fica cinza.",
              "Imposed displacement, as on a Junker rig, or imposed force, as on "
              "a servo-hydraulic one. The field that is not the driver is greyed "
              "out.")),
            (("Amplitude transversal δ", "Transverse amplitude δ"),
             ("Deslocamento de pico, em milímetros. Junker típico: zero vírgula "
              "três a um.",
              "Peak displacement, in millimetres. Typical Junker: 0.3 to 1.0.")),
            (("Amplitude da força axial", "Axial force amplitude"),
             ("Força dinâmica de pico, em newtons.",
              "Peak dynamic force, in newtons.")),
            (("Frequência / Ciclos", "Frequency / Cycles"),
             ("Frequência do ensaio e quantos ciclos simular.",
              "Test frequency and how many cycles to simulate.")),
            (("CSV de referência", "Reference CSV"),
             ("Opcional: curva de laboratório para calibração.",
              "Optional: laboratory curve for calibration.")),
            (("Gerar modelo", "Generate model"),
             ("Materializa a cadeia e abre o módulo Model.",
              "Materialises the chain and opens the Model module.")),
        ],
    ),
    dict(
        chave="03_anatomia", print_="chrome_model",
        titulo=("Anatomia da janela", "Anatomy of the window"),
        narracao=(
            "A janela tem seis regiões. No topo, os menus e a barra de módulos. "
            "À esquerda, a árvore do modelo: cada nó é um elemento, um contato ou "
            "uma etapa, e clicar num elemento o seleciona no desenho. No centro, "
            "o viewport, onde a junta aparece como uma cadeia vertical de blocos: "
            "cada bloco mostra o nome, a rigidez e a fração de carga que carrega. "
            "À direita, o painel de propriedades, com três abas: Element, Loading "
            "e Contact. Embaixo, a área de mensagens, com o registro do trabalho e "
            "o log de cada análise. E, na base, a linha de prompt: uma frase que "
            "diz o que fazer agora. Todos os painéis laterais podem ser fechados "
            "no xis do título e reabertos em Exibir, Painéis.",
            "The window has six regions. At the top, the menus and the module "
            "bar. On the left, the model tree: each node is an element, a "
            "contact or a step, and clicking an element selects it in the "
            "drawing. In the centre, the viewport, where the joint appears as a "
            "vertical chain of blocks: each block shows the name, the stiffness "
            "and the share of load it carries. On the right, the properties "
            "panel, with three tabs: Element, Loading and Contact. At the bottom, "
            "the message area, with the work log and the log of each analysis. "
            "And at the base, the prompt line: one sentence saying what to do "
            "now. Every side panel can be closed with the cross in its title and "
            "reopened under View, Panels."),
        controles=[
            ("Model Tree", ("Árvore de navegação; fonte de verdade do que existe "
                            "no modelo.",
                            "Navigation tree; the source of truth for what "
                            "exists in the model.")),
            ("Viewport", ("O desenho da cadeia. Shift+F enquadra tudo; a roda do "
                          "mouse aproxima.",
                          "The drawing of the chain. Shift+F frames everything; "
                          "the mouse wheel zooms.")),
            ("Fit / Zoom In / Zoom Out / Screenshot",
             ("Botões do viewport: enquadrar, aproximar, afastar e salvar uma "
              "imagem do desenho.",
              "Viewport buttons: frame, zoom in, zoom out and save an image of "
              "the drawing.")),
            ("Properties", ("Painel de propriedades do que está selecionado, em "
                            "três abas.",
                            "Properties of whatever is selected, in three tabs.")),
            ("Elements", ("A paleta: arraste um tipo para o viewport para "
                          "acrescentá-lo à cadeia. Só aparece no módulo Model.",
                          "The palette: drag a type onto the viewport to add it "
                          "to the chain. Only shown in the Model module.")),
            (("Mensagens / Log do job", "Messages / Job Log"),
             ("Duas abas: avisos do programa e a saída da análise em andamento.",
              "Two tabs: program notices and the output of the running "
              "analysis.")),
            (("Linha de prompt", "Prompt line"),
             ("Uma instrução contextual, sempre atualizada.",
              "One contextual instruction, always current.")),
            (("Exibir → Tema", "View → Theme"),
             ("Paletas claras e escuras; a escolha fica salva.",
              "Light and dark palettes; the choice is saved.")),
            (("Ajuda → Idioma", "Help → Language"),
             ("Alterna toda a interface entre português e inglês, ao vivo.",
              "Switches the whole interface between Portuguese and English, "
              "live.")),
        ],
    ),
    dict(
        chave="04_model", print_="chrome_model",
        titulo=("Model — montar a cadeia", "Model — building the chain"),
        narracao=(
            "O módulo Model é onde a junta vira uma cadeia. Da paleta à direita, "
            "arraste um tipo de elemento para o viewport. Há corpos, que carregam "
            "massa e rigidez: o Ground, que é a fronteira fixa; a cabeça; a haste; "
            "a rosca; a porca; a arruela; o flange; a gaxeta. E há ligações, que "
            "carregam a tribologia: o contato de rosca, o contato sob a cabeça, o "
            "contato sob a porca, o contato entre flanges. A regra que mais "
            "importa: sem as duas ligações de apoio, Bearing Head e Bearing Nut, "
            "o modelo não afrouxa, porque é nelas que a face escorrega, assenta e "
            "desgasta. A ordem na cadeia importa: corpos em série somam "
            "flexibilidade, e cada ligação fica entre os dois corpos que ela "
            "conecta. Clique duas vezes num elemento para editá-lo.",
            "The Model module is where the joint becomes a chain. From the "
            "palette on the right, drag an element type onto the viewport. There "
            "are bodies, which carry mass and stiffness: the Ground, the fixed "
            "boundary; the head; the shank; the thread; the nut; the washer; the "
            "flange; the gasket. And there are connections, which carry the "
            "tribology: the thread contact, the contact under the head, the "
            "contact under the nut, the contact between flanges. The rule that "
            "matters most: without the two bearing connections, Bearing Head and "
            "Bearing Nut, the model does not loosen, because that is where the "
            "face slips, embeds and wears. Order in the chain matters: bodies in "
            "series add flexibility, and each connection sits between the two "
            "bodies it joins. Double-click an element to edit it."),
        controles=[
            ("Joint Wizard / Configure Joint…",
             ("Abre o assistente a partir da paleta.",
              "Opens the wizard from the palette.")),
            ("Quick Presets", ("Cadeias prontas: parafuso único, junta "
                               "flangeada, bancada Junker.",
                               "Ready-made chains: single bolt, flanged joint, "
                               "Junker rig.")),
            ("Bolt Head / Shank / Nut / Washer",
             ("Corpos do parafuso. Rigidez calculada da geometria e do material "
              "quando o cálculo automático está ligado.",
              "Bolt bodies. Stiffness computed from geometry and material when "
              "auto-calculate is on.")),
            ("Flange / Gasket", ("Membros apertados. A gaxeta é uma ordem de "
                                 "grandeza mais flexível e domina o assentamento "
                                 "quando existe.",
                                 "Clamped members. The gasket is an order of "
                                 "magnitude more flexible and dominates "
                                 "embedding when present.")),
            ("Bearing (Head) / Bearing (Nut)",
             ("As duas interfaces que decidem o afrouxamento. Obrigatórias.",
              "The two interfaces that decide loosening. Mandatory.")),
            ("Flange-Flange / Washer Contact / Thread Contact",
             ("Demais interfaces de atrito da junta.",
              "The remaining friction interfaces of the joint.")),
            (("Bloco no viewport", "Block in the viewport"),
             ("Mostra nome, k em newtons por metro e a fração da carga que o "
              "elemento carrega.",
              "Shows the name, k in newtons per metre and the share of load the "
              "element carries.")),
        ],
        erro_comum=(
            "Modelo que não perde pré-carga nenhuma: quase sempre faltam as "
            "ligações Bearing Head e Bearing Nut, ou a amplitude em Loads está "
            "zerada.",
            "A model that loses no preload at all: almost always the Bearing "
            "Head and Bearing Nut connections are missing, or the amplitude in "
            "Loads is zero."),
    ),
    dict(
        chave="05_inspector_element", print_="inspector_element",
        titulo=("Propriedades — aba Element", "Properties — Element tab"),
        narracao=(
            "Com um elemento selecionado, a aba Element mostra tudo o que ele é. "
            "Em cima, o tipo. Em Grid Position, a linha e a coluna na cadeia: "
            "linha é a posição em série; coluna, em paralelo. Em MSD Parameters, "
            "as três constantes da física: k, a rigidez em newtons por metro; c, "
            "o amortecimento; e m, a massa. Cada uma tem um interruptor de cálculo "
            "automático: ligado, o valor sai da geometria e do material e se "
            "recalcula sempre que eles mudam; desligado, você digita. Em Material "
            "Properties, a classe do aço, o módulo de elasticidade, o escoamento, "
            "a ruptura e a densidade. Em Tribological Properties, o atrito na "
            "rosca, o atrito sob a cabeça e o acabamento da superfície. Em "
            "Preload, a fração do escoamento e a força resultante. Mais abaixo, "
            "as propriedades térmicas e a geometria do elemento. Se o selecionado "
            "for uma ligação, aparecem no lugar as rigidezes e os atritos da "
            "interface e a geometria da rosca, do apoio ou da gaxeta. Digitar k à "
            "mão desacopla o modelo da geometria: prefira o automático.",
            "With an element selected, the Element tab shows everything it is. "
            "At the top, the type. Under Grid Position, the row and column in "
            "the chain: row is the position in series; column, in parallel. "
            "Under MSD Parameters, the three constants of the physics: k, the "
            "stiffness in newtons per metre; c, the damping; and m, the mass. "
            "Each has an auto-calculate switch: on, the value comes from geometry "
            "and material and is recomputed whenever they change; off, you type "
            "it. Under Material Properties, the steel grade, Young's modulus, "
            "yield, ultimate strength and density. Under Tribological "
            "Properties, thread friction, bearing friction and the surface "
            "finish. Under Preload, the fraction of yield and the resulting "
            "force. Further down, the thermal properties and the element "
            "geometry. If the selection is a connection, the interface "
            "stiffnesses and frictions and the thread, bearing or gasket geometry "
            "appear instead. Typing k by hand decouples the model from the "
            "geometry: prefer automatic."),
        controles=[
            ("Type", ("O tipo do elemento selecionado.", "The selected element's type.")),
            ("Row (series) / Column (parallel)",
             ("Posição na cadeia. Elementos na mesma coluna estão em paralelo.",
              "Position in the chain. Elements in the same column are in "
              "parallel.")),
            ("k (N/m)", ("Rigidez axial. Do parafuso: E vezes área resistente "
                         "sobre comprimento de aperto.",
                         "Axial stiffness. For the bolt: E times stress area over "
                         "grip length.")),
            ("c (N·s/m)", ("Amortecimento viscoso. Efeito quase nulo na perda de "
                           "pré-carga quase-estática.",
                           "Viscous damping. Near-zero effect on quasi-static "
                           "preload loss.")),
            ("m", ("Massa do elemento, em quilogramas.", "Element mass, in kilograms.")),
            (("≡ / ▾ ao lado de k, c, m", "≡ / ▾ next to k, c, m"),
             ("Ligam ou desligam o cálculo automático e abrem as opções de "
              "cálculo.",
              "Turn auto-calculate on or off and open the calculation options.")),
            ("Grade", ("Classe do material, do banco de dados embutido.",
                       "Material grade, from the bundled database.")),
            ("E, Sy, Su, ρ", ("Módulo de elasticidade, escoamento, ruptura e "
                              "densidade.",
                              "Young's modulus, yield, ultimate strength and "
                              "density.")),
            ("μ thread / μ bearing", ("Coeficientes de atrito iniciais na rosca "
                                      "e sob a cabeça.",
                                      "Initial friction coefficients at the "
                                      "thread and under the head.")),
            ("Surface", ("Acabamento: aço nu, zincado, lubrificado…",
                         "Finish: bare steel, zinc-plated, lubricated…")),
            ("Preload & Yield › Mode / % Yield / Force / Result",
             ("Pré-carga por fração do escoamento ou por força direta; a área "
              "resistente e a força resultante aparecem em Result.",
              "Preload by fraction of yield or by direct force; stress area and "
              "the resulting force appear under Result.")),
            ("Thermal Properties › α (expansion) / T reference / T operating",
             ("Coeficiente de dilatação e temperaturas de referência e de "
              "operação; a diferença entre elas gera pré-carga térmica.",
              "Expansion coefficient and reference and operating temperatures; "
              "their difference produces thermal preload.")),
            ("Geometry › Diameter / Length / Pitch",
             ("Diâmetro, comprimento e passo do elemento; alimentam o cálculo "
              "automático de k.",
              "Element diameter, length and pitch; they feed the automatic "
              "calculation of k.")),
            ("Contact Interface Properties › k normal / k tangential / c normal / "
             "c tangential / μ static / μ kinetic",
             ("Só para uma ligação selecionada: rigidezes e amortecimentos normal "
              "e tangencial, atrito estático e cinético.",
              "Only for a selected connection: normal and tangential stiffness "
              "and damping, static and kinetic friction.")),
            ("Thread Contact Parameters › Pitch / Helix angle / Mean radius / "
             "Engagement",
             ("Rosca: passo, ângulo de hélice, raio médio e comprimento engajado.",
              "Thread: pitch, helix angle, mean radius and engaged length.")),
            ("Bearing Contact Parameters › Inner radius / Outer radius / "
             "Effective r / Roughness",
             ("Apoio: raios interno e externo da face, raio efetivo de atrito e "
              "rugosidade.",
              "Bearing: inner and outer radius of the face, effective friction "
              "radius and roughness.")),
            ("Gasket Contact Parameters › Gasket type / Thickness / Compression E / "
             "Hertz exponent / Creep coeff",
             ("Gaxeta: tipo, espessura, módulo de compressão, expoente de Hertz e "
              "coeficiente de fluência.",
              "Gasket: type, thickness, compression modulus, Hertz exponent and "
              "creep coefficient.")),
        ],
    ),
    dict(
        chave="06_contacts", print_="inspector_contact",
        titulo=("Contacts — atrito e tribologia", "Contacts — friction and tribology"),
        narracao=(
            "O módulo Contacts mostra a mesma cadeia com as interfaces em foco, e "
            "a aba Contact do painel de propriedades traz as constantes que a "
            "validação calibra. O atrito inicial mi é o coeficiente antes do "
            "ensaio começar. A caixa Lubricated muda o regime. O diâmetro e o "
            "passo do parafuso definem os diâmetros efetivos da rosca. O "
            "escoamento define a área resistente e, com a fração escolhida, a "
            "força de aperto, mostrada em verde. Num caso importado do artigo, "
            "esses valores já são os adotados; num modelo seu, é aqui que você "
            "coloca o que mediu. Se você mediu o atrito, digite e não mexa mais: "
            "o calibrador respeita o que não estiver marcado.",
            "The Contacts module shows the same chain with the interfaces in "
            "focus, and the Contact tab of the properties panel carries the "
            "constants the validation calibrates. Initial friction mu is the "
            "coefficient before the test starts. The Lubricated box changes the "
            "regime. Bolt diameter and pitch define the effective thread "
            "diameters. Yield defines the stress area and, with the chosen "
            "fraction, the clamping force, shown in green. In a case imported "
            "from the paper these values are already the adopted ones; in a model "
            "of your own, this is where you enter what you measured. If you "
            "measured the friction, type it and leave it alone: the calibrator "
            "respects whatever is not ticked."),
        controles=[
            ("Initial μ", ("Coeficiente de atrito inicial da interface.",
                           "Initial friction coefficient of the interface.")),
            ("Lubricated", ("Interface lubrificada: muda o regime de atrito.",
                            "Lubricated interface: changes the friction regime.")),
            ("Bolt diameter / Pitch", ("Geometria da rosca; os diâmetros efetivos "
                                       "d2 e d3 aparecem embaixo.",
                                       "Thread geometry; the effective diameters "
                                       "d2 and d3 appear below.")),
            ("Sy (yield)", ("Escoamento do parafuso; define a área resistente e a "
                            "pré-carga nominal.",
                            "Bolt yield; defines the stress area and the nominal "
                            "preload.")),
            ("A_s / F₀", ("Área resistente e força de aperto resultante, em "
                          "verde.",
                          "Stress area and resulting clamping force, in green.")),
            ("Applied Loads / Edit Loads…",
             ("Lista das cargas e restrições aplicadas ao elemento selecionado; "
              "Edit Loads… abre o editor.",
              "List of the loads and constraints applied to the selected "
              "element; Edit Loads… opens the editor.")),
            ("Actions › Apply Load/Constraint… / Recalculate MSD / "
             "Duplicate Element / Delete Element",
             ("Aplica uma carga ou restrição; recalcula k, c e m da geometria; "
              "duplica; exclui o elemento selecionado.",
              "Applies a load or constraint; recomputes k, c and m from geometry; "
              "duplicates; deletes the selected element.")),
            ("Global / Per-Element", ("Abas de baixo: constantes globais da junta "
                                      "ou por elemento.",
                                      "Bottom tabs: joint-wide constants or "
                                      "per-element ones.")),
        ],
    ),
    dict(
        chave="07_loads", print_="inspector_loading",
        titulo=("Loads — o carregamento", "Loads — the loading"),
        narracao=(
            "Em Loads você define o que excita a junta. Escolha o tipo de "
            "carregamento: transversal, que é a condição Junker, ou axial. Escolha "
            "o modelo de atrito: em três fases, o padrão, que representa o "
            "amaciamento, o pico e o patamar do coeficiente. Dê a pré-carga F "
            "zero em newtons ou como fração do escoamento; a linha verde confirma "
            "área, fração e força. Escolha o modo de controle: deslocamento "
            "imposto ou força imposta. Dê a amplitude, a frequência e a duração, "
            "em ciclos ou em segundos. Força externa, torque e variação de "
            "temperatura são opcionais. A regra: o campo que não comanda fica "
            "cinza, para você ver o que é imposto e o que é consequência. Mais "
            "abaixo há três grupos avançados: o dispositivo de travamento, os "
            "fatores de carga da VDI dois mil duzentos e trinta e a forma da "
            "curva na segunda fase. Deixe-os como estão até precisar deles.",
            "In Loads you define what excites the joint. Choose the loading type: "
            "transverse, which is the Junker condition, or axial. Choose the "
            "friction model: three-phase, the default, representing run-in, peak "
            "and plateau of the coefficient. Give the preload F zero in newtons or "
            "as a fraction of yield; the green line confirms area, fraction and "
            "force. Choose the control mode: imposed displacement or imposed "
            "force. Give the amplitude, the frequency and the duration, in cycles "
            "or in seconds. External force, torque and temperature change are "
            "optional. The rule: the field that is not the driver is greyed out, "
            "so you see what is imposed and what follows. Further down there are "
            "three advanced groups: the locking device, the VDI twenty-two "
            "thirty load factors and the curve shape of the second stage. Leave "
            "them as they are until you need them."),
        controles=[
            ("Preset", ("Condições experimentais prontas; Custom para as suas.",
                        "Ready experimental conditions; Custom for your own.")),
            ("Load type", ("Transverse, Axial ou Combined.",
                           "Transverse, Axial or Combined.")),
            ("Friction model", ("Three-Phase é o padrão validado.",
                                "Three-Phase is the validated default.")),
            ("Preload F₀ / % Yield", ("Pré-carga em newtons, ou a fração do "
                                      "escoamento; um recalcula o outro.",
                                      "Preload in newtons, or the fraction of "
                                      "yield; each recomputes the other.")),
            ("Control mode", ("Displacement-controlled impõe δ; force-controlled "
                              "impõe a força.",
                              "Displacement-controlled imposes δ; "
                              "force-controlled imposes the force.")),
            ("Transverse disp. / Transverse force",
             ("A amplitude do que é imposto; o outro campo fica cinza.",
              "The amplitude of what is imposed; the other field is greyed out.")),
            ("Frequency", ("Frequência do ensaio, em hertz.",
                           "Test frequency, in hertz.")),
            ("Duration mode / Duration", ("Em ciclos ou em segundos; N é "
                                          "mostrado embaixo.",
                                          "In cycles or in seconds; N is shown "
                                          "below.")),
            ("External force / Torque / ΔT",
             ("Carga axial externa constante, torque aplicado e variação térmica. "
              "Opcionais.",
              "Constant external axial load, applied torque and thermal change. "
              "Optional.")),
            ("Locking Device › Device / Slip onset / Δμ / Junker class",
             ("Dispositivo de travamento, como porca autotravante ou arruela de "
              "pressão: mostra o início do deslizamento, o acréscimo de atrito Δμ "
              "e a classe Junker. Informativo: some o Δμ em Contact, Initial μ, se "
              "quiser o efeito.",
              "Locking device, such as a prevailing-torque nut or a lock washer: "
              "shows slip onset, the friction increment Δμ and the Junker class. "
              "Informational: add the Δμ under Contact, Initial μ, if you want the "
              "effect.")),
            ("VDI 2230 Load Factors › Stress ratio R / Dyn. factor φ / "
             "Load-plane n / Waveform",
             ("Fatores de carga da VDI 2230: razão de tensões, fator dinâmico, "
              "plano de introdução da carga n e forma de onda da excitação.",
              "VDI 2230 load factors: stress ratio, dynamic factor, load-"
              "introduction plane n and excitation waveform.")),
            ("Curve Shape (Stage II) › F∞ ratio / μ recovery gain / Creep ε₀ / "
             "Noise σ",
             ("Forma da curva na segunda fase: patamar final como fração de F₀, "
              "ganho de recuperação do atrito, fluência inicial e ruído para "
              "curvas sintéticas.",
              "Second-stage curve shape: final plateau as a fraction of F₀, "
              "friction recovery gain, initial creep and noise for synthetic "
              "curves.")),
        ],
    ),
    dict(
        chave="08_analysis", print_="chrome_analysis",
        titulo=("Analysis — rodar", "Analysis — running"),
        narracao=(
            "O módulo Analysis é onde a simulação acontece. O painel à direita "
            "traz as escolhas recomendadas a partir do modelo: o integrador, o "
            "modo de controle e o modelo de atrito. O Step no topo escolhe entre "
            "a pré-carga estática e o afrouxamento acoplado. Clique em Run, ou "
            "pressione control R de qualquer módulo. A área de mensagens abre "
            "sozinha na aba Log do job e mostra o progresso, ciclo a ciclo. O "
            "distintivo na barra diz RUNNING, depois DONE. Se disser ERROR, o "
            "motivo está no log, na última linha. Uma análise de cem ciclos leva "
            "um segundo; de cem mil, alguns minutos.",
            "The Analysis module is where the simulation happens. The panel on "
            "the right carries the recommended choices derived from the model: "
            "the integrator, the control mode and the friction model. The Step at "
            "the top chooses between static preload and coupled loosening. Click "
            "Run, or press control R from any module. The message area opens on "
            "its own at the Job Log tab and shows progress, cycle by cycle. The "
            "badge on the bar says RUNNING, then DONE. If it says ERROR, the "
            "reason is in the log, on the last line. An analysis of a hundred "
            "cycles takes a second; of a hundred thousand, a few minutes."),
        controles=[
            ("Step", ("Static-Preload ou Coupled-Loosening.",
                      "Static-Preload or Coupled-Loosening.")),
            ("Integrator", ("Newmark-β ou HHT-α; o recomendado vem marcado.",
                            "Newmark-β or HHT-α; the recommended one is "
                            "pre-selected.")),
            ("Control mode / Friction model",
             ("Repetem as escolhas de Loads para conferência.",
              "Repeat the Loads choices for checking.")),
            ("Run (Ctrl+R)", ("Inicia a análise.", "Starts the analysis.")),
            ("Stop", ("Interrompe uma análise em andamento.",
                      "Interrupts a running analysis.")),
            (("Distintivo RUNNING / DONE / ERROR", "RUNNING / DONE / ERROR badge"),
             ("Estado do job, na barra de módulos.",
              "Job state, on the module bar.")),
            (("Log do job", "Job Log"),
             ("A saída da análise, linha a linha.",
              "The analysis output, line by line.")),
        ],
        erro_comum=(
            "Run desabilitado: você não está no módulo Analysis, ou não há "
            "modelo carregado.",
            "Run disabled: you are not in the Analysis module, or no model is "
            "loaded."),
    ),
    dict(
        chave="09_results", print_="chrome_results",
        titulo=("Results — ler o resultado", "Results — reading the result"),
        narracao=(
            "Em Results, a aba Run mostra o que a análise produziu. O gráfico "
            "principal é a pré-carga contra os ciclos: a curva que o parafuso "
            "descreveu. Abaixo, a decomposição por mecanismo: quanto da perda veio "
            "do assentamento, quanto da fluência, quanto do desgaste, quanto da "
            "rotação da porca. É essa decomposição que diz se a junta perdeu força "
            "no começo, por assentamento das superfícies, ou ao longo do ensaio, "
            "por desgaste. Há também os gráficos de atrito e de fase. A barra de "
            "contexto acima do gráfico troca a família de plots sem sair do "
            "módulo.",
            "In Results, the Run tab shows what the analysis produced. The main "
            "plot is preload against cycles: the curve the bolt described. Below, "
            "the decomposition by mechanism: how much of the loss came from "
            "embedding, how much from creep, how much from wear, how much from "
            "nut rotation. That decomposition is what tells you whether the joint "
            "lost force at the start, from surface embedding, or along the test, "
            "from wear. There are also the friction and phase plots. The context "
            "bar above the plot switches between plot families without leaving "
            "the module."),
        controles=[
            (("Aba Run", "Run tab"),
             ("Resultados da análise que você acabou de rodar.",
              "Results of the analysis you just ran.")),
            (("Aba Validation", "Validation tab"),
             ("O navegador do corpus, explicado na próxima página.",
              "The corpus browser, explained on the next page.")),
            ("Preload", ("Pré-carga contra ciclos.", "Preload against cycles.")),
            ("Friction / Phase", ("Evolução do atrito e retrato de fase.",
                                  "Friction evolution and phase portrait.")),
            ("Miner / Layout / Overlay / Export",
             ("Acúmulo de dano, arranjo dos painéis, sobreposição com o dado e "
              "exportação.",
              "Damage accumulation, panel layout, overlay with the data and "
              "export.")),
        ],
    ),
    dict(
        chave="10_validation", print_="chrome_results_validation",
        titulo=("Results › Validation — o corpus", "Results › Validation — the corpus"),
        narracao=(
            "A aba Validation é o corpus inteiro: uma árvore de artigo e curva, "
            "vinte e oito fontes, duzentas e sete curvas, cada uma com o erro do "
            "modelo ao lado. Selecione uma curva e o gráfico mostra o dado "
            "digitalizado contra a previsão do modelo, com a decomposição por "
            "mecanismo e as três métricas do critério. Abrir no Model traz aquele "
            "caso como modelo editável, com as constantes adotadas. Re-simular "
            "roda o motor de novo e regrava o resultado. Report HTML abre o "
            "relatório completo daquele caso: condições, modelo, resíduo, e cada "
            "constante com a sua procedência. Report geral abre o documento "
            "mestre. No painel destacado, o intake: copie o prompt, leve a "
            "qualquer inteligência artificial com a sua curva experimental, e "
            "importe o resultado.",
            "The Validation tab is the whole corpus: a tree of paper and curve, "
            "twenty-eight sources, two hundred and seven curves, each with the "
            "model's error beside it. Select a curve and the plot shows the "
            "digitised data against the model's prediction, with the "
            "decomposition by mechanism and the three metrics of the criterion. "
            "Open in Model brings that case in as an editable model, with the "
            "adopted constants. Re-simulate runs the engine again and rewrites "
            "the result. HTML report opens the full report of that case: "
            "conditions, model, residual, and every constant with its "
            "provenance. Master report opens the master document. In the "
            "highlighted panel, the intake: copy the prompt, take it to any AI "
            "with your experimental curve, and import the result."),
        controles=[
            (("Árvore fonte → curva", "Source → curve tree"),
             ("Clique numa curva para vê-la.", "Click a curve to view it.")),
            (("Gráfico", "Plot"),
             ("Dado digitalizado, modelo alinhado e, tracejada, a curva crua do "
              "motor.",
              "Digitised data, aligned model and, dashed, the engine's raw "
              "curve.")),
            (("Métricas", "Metrics"),
             ("MAE, resíduo máximo e σ dos resíduos, com os limites do critério.",
              "MAE, maximum residual and residual σ, with the criterion limits.")),
            (("Abrir no Model/Run", "Open in Model/Run"),
             ("Carrega o caso como modelo editável.",
              "Loads the case as an editable model.")),
            (("Re-simular caso / Re-simular tudo", "Re-simulate case / Re-simulate all"),
             ("Roda o motor de novo para um caso ou para o corpus.",
              "Runs the engine again for one case or the whole corpus.")),
            (("Report HTML / Report geral", "HTML report / Master report"),
             ("Relatório do caso; documento mestre do corpus.",
              "Case report; master document of the corpus.")),
            (("Salvar caso como .msd…", "Save case as .msd…"),
             ("Grava o modelo do caso onde você quiser.",
              "Writes the case model wherever you like.")),
            (("1. Copiar prompt / Salvar prompt… / 3. Importar caso…",
              "1. Copy prompt / Save prompt… / 3. Import case…"),
             ("O fluxo de intake: prompt para a IA, e importação do JSON que ela "
              "devolve.",
              "The intake flow: prompt for the AI, and import of the JSON it "
              "returns.")),
        ],
    ),
    dict(
        chave="11_calibrar", print_="dialog_calibrate",
        titulo=("Calibrar parâmetros (Ctrl+K)", "Calibrate parameters (Ctrl+K)"),
        narracao=(
            "Analisar, Calibrar parâmetros do modelo, ou control K. Primeiro o "
            "programa pergunta contra qual curva ajustar: o caso do artigo de onde "
            "o modelo veio, ou um CSV seu. Depois abre o diálogo de calibração. À "
            "esquerda, a lista de parâmetros, cada um com uma caixa de seleção e "
            "dois limites. A regra é simples e é o que faz tudo funcionar: o que "
            "você não marca fica exatamente no valor que está no modelo. É assim "
            "que se trava o que já foi medido. O que você marca é procurado entre "
            "o limite inferior e o superior. Marque poucos por vez. À direita, a "
            "prévia mostra a curva experimental, o modelo atual e o ajuste "
            "candidato. Aplicar grava o resultado no modelo; Descartar não deixa "
            "vestígio. O motor que ajusta é o mesmo que roda a análise: o que "
            "fecha aqui se reproduz no Run.",
            "Analyse, Calibrate model parameters, or control K. First the program "
            "asks which curve to fit against: the paper case the model came from, "
            "or a CSV of yours. Then the calibration dialogue opens. On the left, "
            "the list of parameters, each with a checkbox and two bounds. The rule "
            "is simple and it is what makes everything work: what you do not tick "
            "stays exactly at the value in the model. That is how you lock what "
            "has already been measured. What you tick is searched between the "
            "lower and the upper bound. Tick few at a time. On the right, the "
            "preview shows the experimental curve, the current model and the "
            "candidate fit. Apply writes the result into the model; Discard "
            "leaves no trace. The engine that fits is the same one that runs the "
            "analysis: what closes here is reproduced in the Run."),
        controles=[
            (("Curva de referência: Caso da validação / Arquivo CSV…",
              "Reference curve: Validation case / CSV file…"),
             ("A origem da curva experimental. O caso só aparece se o modelo "
              "veio de um.",
              "The source of the experimental curve. The case option only "
              "appears if the model came from one.")),
            ("Optimization Agent / Run Agent",
             ("Modo autônomo: detecta o regime, escolhe um prior da literatura e "
              "ajusta em duas etapas.",
              "Autonomous mode: detects the regime, picks a literature prior and "
              "fits in two stages.")),
            ("Trim cycles", ("Recorta a janela de ciclos usada no ajuste: tira "
                             "uma cauda ruidosa ou um reaperto.",
                             "Crops the cycle window used in the fit: removes a "
                             "noisy tail or a re-tightening.")),
            ("Engine", ("V2 não linear é o recomendado; é o motor do artigo.",
                        "V2 non-linear is recommended; it is the paper's "
                        "engine.")),
            ("Wizard — load literature priors…",
             ("Carrega limites típicos da literatura para os parâmetros.",
              "Loads typical literature bounds for the parameters.")),
            ("Parameter / Lo / Hi", ("A caixa trava ou libera; Lo e Hi são os "
                                     "limites da busca.",
                                     "The box locks or frees; Lo and Hi are the "
                                     "search bounds.")),
            ("Live Preview", ("Experimental, modelo atual e ajuste; MAE e RMSE no "
                              "topo.",
                              "Experimental, current model and fit; MAE and RMSE "
                              "at the top.")),
            ("Preview Current / Run Calibration / Cancel",
             ("Desenha o modelo atual; inicia o ajuste; interrompe.",
              "Draws the current model; starts the fit; interrupts.")),
            ("Apply to Model / Apply & Re-run / Discard",
             ("Grava no modelo; grava e roda a análise; descarta.",
              "Writes to the model; writes and runs the analysis; discards.")),
        ],
        erro_comum=(
            "Um ajuste que fecha bem contra uma única curva não é uma "
            "configuração adotada do artigo: aquelas foram fixadas por bancada e "
            "validadas por validação cruzada. Trate o seu ajuste como hipótese.",
            "A fit that closes well against a single curve is not an adopted "
            "configuration of the paper: those were fixed per rig and "
            "cross-validated. Treat your fit as a hypothesis."),
    ),
    dict(
        chave="12_report", print_="chrome_report",
        titulo=("Report — o documento", "Report — the document"),
        narracao=(
            "O módulo Report monta um documento a partir da análise corrente. "
            "Escolha as seções, o formato e veja a prévia. O relatório da sua "
            "junta tem as mesmas seções dos relatórios dos casos do artigo, porque "
            "sai da mesma máquina: condições do ensaio, modelo, curva, "
            "decomposição por mecanismo e a lista de constantes. Exporte em HTML; "
            "ele abre no navegador do sistema.",
            "The Report module assembles a document from the current analysis. "
            "Choose the sections, the format and see the preview. Your joint's "
            "report has the same sections as the reports of the paper's cases, "
            "because it comes from the same machinery: test conditions, model, "
            "curve, decomposition by mechanism and the list of constants. Export "
            "as HTML; it opens in the system browser."),
        controles=[
            ("Template / Sections", ("Modelo do documento e quais seções entram.",
                                     "Document template and which sections go in.")),
            ("Format", ("HTML é o formato de exportação.",
                        "HTML is the export format.")),
            ("Preview", ("Prévia do documento montado.",
                         "Preview of the assembled document.")),
        ],
    ),
    dict(
        chave="13_ajuda", print_="documentation_tab",
        titulo=("Ajuda — documentação e idioma", "Help — documentation and language"),
        narracao=(
            "O menu Ajuda abre a documentação com F1: vinte e cinco seções, entre "
            "elas a revisão da literatura sobre afrouxamento, o resumo de cada "
            "artigo do corpus, os tipos de elemento e de ligação, o guia para "
            "construir um modelo do zero e o catálogo de todas as mensagens que o "
            "programa pode mostrar, com causa e ação. A busca encontra qualquer "
            "palavra em qualquer seção. Guia de uso narrado abre este guia, no "
            "idioma da interface. Idioma alterna toda a interface entre "
            "português e inglês. Reports de validação abre o documento mestre dos "
            "duzentos e sete casos no navegador.",
            "The Help menu opens the documentation with F1: twenty-five "
            "sections, among them the literature review on self-loosening, the "
            "summary of every paper in the corpus, the element and connection "
            "types, the guide to building a model from scratch and the catalogue "
            "of every message the program can show, with cause and action. Search "
            "finds any word in any section. Narrated user guide opens this guide, "
            "in the language of the interface. Language switches the whole "
            "interface between Portuguese and English. Validation reports opens "
            "the master document of the two hundred and seven cases in the "
            "browser."),
        controles=[
            (("Documentação (F1)", "Documentation (F1)"),
             ("Abre a documentação numa janela própria.",
              "Opens the documentation in its own window.")),
            (("Buscar na documentação", "Search documentation"),
             ("Procura em todas as seções.", "Searches every section.")),
            (("Árvore de seções", "Section tree"),
             ("As vinte e cinco seções, numeradas.",
              "The twenty-five sections, numbered.")),
            (("Atalhos", "Quick Links"),
             ("Botões para as seções mais usadas.",
              "Buttons to the most used sections.")),
            (("Imprimir", "Print"),
             ("Imprime a seção aberta.", "Prints the open section.")),
            (("Guia de uso narrado", "Narrated user guide"),
             ("Abre este guia no navegador, no idioma da interface.",
              "Opens this guide in the browser, in the interface language.")),
            (("Idioma: Português / English", "Language: Português / English"),
             ("Alterna o idioma ao vivo; a escolha fica salva.",
              "Switches the language live; the choice is saved.")),
            (("Reports de validação", "Validation reports"),
             ("Documento mestre do corpus, no navegador.",
              "Master document of the corpus, in the browser.")),
            (("Prompt de intake (IA) — copiar", "Intake prompt (AI) — copy"),
             ("Copia o prompt do fluxo de intake.",
              "Copies the intake-flow prompt.")),
        ],
    ),
    dict(
        chave="14_salvar_atalhos", print_="chrome_loads",
        titulo=("Salvar, reabrir e atalhos", "Saving, reopening and shortcuts"),
        narracao=(
            "Salve com control S. Na primeira vez o programa pergunta onde; depois "
            "grava no mesmo arquivo. Salvar como, control shift S, escolhe outro "
            "destino. O arquivo ponto m s d guarda tudo: a cadeia, o carregamento "
            "e as constantes calibradas, então reabrir devolve o modelo inteiro. "
            "Se o modelo veio de um caso do artigo, salvar pede um destino novo, "
            "porque os casos do artigo são reinstalados a cada atualização. Os "
            "atalhos que valem a pena: control um a control seis trocam de "
            "módulo; control R roda; shift F enquadra o desenho; F1 abre a "
            "documentação; control I importa um caso; control K calibra.",
            "Save with control S. The first time the program asks where; after "
            "that it writes to the same file. Save as, control shift S, picks "
            "another destination. The dot m s d file keeps everything: the chain, "
            "the loading and the calibrated constants, so reopening returns the "
            "whole model. If the model came from a paper case, saving asks for a "
            "new destination, because the paper's cases are reinstalled on every "
            "update. The shortcuts worth knowing: control one to control six "
            "switch module; control R runs; shift F frames the drawing; F1 opens "
            "the documentation; control I imports a case; control K calibrates."),
        controles=[
            ("Ctrl+S / Ctrl+Shift+S", ("Salvar; salvar como.", "Save; save as.")),
            ("Ctrl+O / Ctrl+I", ("Abrir projeto; importar caso do artigo.",
                                 "Open project; import paper case.")),
            ("Ctrl+1 … Ctrl+6", ("Model, Contacts, Loads, Analysis, Results, "
                                 "Report.",
                                 "Model, Contacts, Loads, Analysis, Results, "
                                 "Report.")),
            ("Ctrl+R", ("Roda a análise de qualquer módulo.",
                        "Runs the analysis from any module.")),
            ("Shift+F", ("Enquadra o desenho.", "Frames the drawing.")),
            ("F1 / Ctrl+K", ("Documentação; calibrar.",
                             "Documentation; calibrate.")),
            ("Ctrl+Shift+N", ("Assistente de nova análise.",
                              "New-analysis wizard.")),
        ],
    ),
]

# (termo_pt, termo_en, definicao_pt, definicao_en) — a pagina glossario.html
# de cada idioma. Termos como o programa e o artigo os usam.
GLOSSARIO = [
    ("pré-carga", "preload",
     "Força de tração instalada no parafuso pelo aperto; a grandeza que o programa "
     "acompanha ciclo a ciclo.",
     "Tensile force installed in the bolt by tightening; the quantity the program "
     "tracks cycle by cycle."),
    ("perda de pré-carga", "preload loss",
     "Queda da pré-carga ao longo do ensaio, medida em fração de F₀.",
     "Drop of the preload along the test, measured as a fraction of F₀."),
    ("afrouxamento (autoafrouxamento)", "self-loosening",
     "Perda de pré-carga por rotação da porca sob carga cíclica, sem ninguém soltar "
     "o parafuso.",
     "Preload loss by nut rotation under cyclic load, with nobody undoing the bolt."),
    ("assentamento", "embedding",
     "Achatamento das asperezas nas interfaces nos primeiros ciclos; o mecanismo "
     "dominante no início da curva.",
     "Flattening of the asperities at the interfaces in the first cycles; the "
     "dominant mechanism at the start of the curve."),
    ("fluência", "creep",
     "Deformação lenta dos membros sob carga constante, que relaxa a pré-carga com "
     "o tempo.",
     "Slow deformation of the members under constant load, relaxing the preload "
     "over time."),
    ("desgaste", "wear",
     "Remoção de material nas faces que escorregam, proporcional ao trabalho de "
     "atrito.",
     "Removal of material at the slipping faces, proportional to the friction work."),
    ("rotação da porca", "nut rotation",
     "Giro relativo entre porca e parafuso que converte deslizamento em perda de "
     "aperto.",
     "Relative turning between nut and bolt that converts slip into loss of clamp."),
    ("decomposição por mecanismo", "decomposition by mechanism",
     "Quanto da perda veio de assentamento, fluência, desgaste e rotação da porca.",
     "How much of the loss came from embedding, creep, wear and nut rotation."),
    ("junta aparafusada", "bolted joint",
     "Conjunto parafuso, porca e membros apertados, com as interfaces entre eles.",
     "The assembly of bolt, nut and clamped members, with the interfaces between "
     "them."),
    ("membros apertados", "clamped members",
     "As peças comprimidas entre a cabeça e a porca: flanges, chapas, gaxeta.",
     "The parts compressed between head and nut: flanges, plates, gasket."),
    ("cabeça", "head",
     "Extremidade do parafuso que se apoia no primeiro membro.",
     "The end of the bolt that bears on the first member."),
    ("haste", "shank",
     "Trecho liso do parafuso entre a cabeça e a rosca; a mola principal da cadeia.",
     "The plain length of the bolt between head and thread; the main spring of the "
     "chain."),
    ("rosca", "thread",
     "Trecho roscado do parafuso, engajado na porca.",
     "The threaded length of the bolt, engaged in the nut."),
    ("porca", "nut",
     "Elemento roscado que fecha a junta; a sua rotação é o afrouxamento.",
     "The threaded element that closes the joint; its rotation is the loosening."),
    ("arruela", "washer",
     "Anel entre a porca ou a cabeça e o membro; muda o atrito de apoio.",
     "Ring between the nut or head and the member; changes the bearing friction."),
    ("flange", "flange",
     "Membro apertado rígido; chapa ou aba de tubo.",
     "A stiff clamped member; a plate or a pipe flange."),
    ("gaxeta", "gasket",
     "Membro apertado flexível de vedação; uma ordem de grandeza mais macio que o "
     "flange.",
     "A flexible clamped sealing member; an order of magnitude softer than the "
     "flange."),
    ("ligação de apoio (Bearing Head, Bearing Nut)", "bearing connection (Bearing Head, Bearing Nut)",
     "Interface sob a cabeça ou sob a porca; é onde a face escorrega, assenta e "
     "desgasta.",
     "Interface under the head or under the nut; where the face slips, embeds and "
     "wears."),
    ("contato de rosca", "thread contact",
     "Interface entre os filetes do parafuso e da porca.",
     "Interface between the bolt and nut threads."),
    ("cadeia massa-mola-amortecedor (MSD)", "mass-spring-damper chain (MSD)",
     "Representação da junta como corpos com massa e rigidez ligados por "
     "interfaces; o modelo do programa.",
     "Representation of the joint as bodies with mass and stiffness joined by "
     "interfaces; the program's model."),
    ("rigidez k", "stiffness k",
     "Força por deslocamento do elemento, em newtons por metro.",
     "Force per displacement of the element, in newtons per metre."),
    ("amortecimento c", "damping c",
     "Resistência viscosa ao movimento, em newton-segundo por metro; efeito pequeno "
     "no afrouxamento quase-estático.",
     "Viscous resistance to motion, in newton-seconds per metre; small effect on "
     "quasi-static loosening."),
    ("massa m", "mass m",
     "Massa do elemento, em quilogramas.",
     "Mass of the element, in kilograms."),
    ("coeficiente de atrito μ", "friction coefficient μ",
     "Razão entre força tangencial e força normal numa interface; inicial na rosca e "
     "sob a cabeça.",
     "Ratio of tangential to normal force at an interface; initial at the thread and "
     "under the head."),
    ("modelo de atrito em três fases", "three-phase friction model",
     "Amaciamento, pico e patamar do coeficiente ao longo dos ciclos; o padrão "
     "validado.",
     "Run-in, peak and plateau of the coefficient along the cycles; the validated "
     "default."),
    ("área resistente A_s", "stress area A_s",
     "Seção efetiva da rosca usada para converter tensão em força.",
     "Effective thread section used to convert stress into force."),
    ("escoamento Sy", "yield strength Sy",
     "Tensão em que o aço começa a deformar permanentemente; base da pré-carga "
     "nominal.",
     "Stress at which the steel starts to deform permanently; the basis of the "
     "nominal preload."),
    ("ruptura Su", "ultimate strength Su",
     "Tensão máxima que o aço suporta.",
     "The highest stress the steel withstands."),
    ("módulo de elasticidade E", "Young's modulus E",
     "Rigidez do material; com a área e o comprimento, dá o k do elemento.",
     "Stiffness of the material; with area and length, gives the element's k."),
    ("classe do material", "material grade",
     "Designação do aço, como 8.8, 10.9 ou A193 B7, que fixa Sy e Su.",
     "Steel designation, such as 8.8, 10.9 or A193 B7, which fixes Sy and Su."),
    ("bitola", "bolt size",
     "Diâmetro nominal métrico, como M8 ou M12; define passo e áreas.",
     "Nominal metric diameter, such as M8 or M12; defines pitch and areas."),
    ("passo", "pitch",
     "Distância entre filetes consecutivos da rosca.",
     "Distance between consecutive threads."),
    ("amplitude transversal δ", "transverse amplitude δ",
     "Deslocamento de pico imposto entre os membros, em milímetros; a excitação do "
     "ensaio Junker.",
     "Peak displacement imposed between the members, in millimetres; the excitation "
     "of the Junker test."),
    ("controle por deslocamento / por força", "displacement- / force-controlled",
     "Qual grandeza a máquina impõe; a outra é consequência e aparece em cinza.",
     "Which quantity the machine imposes; the other one follows and is greyed out."),
    ("ensaio Junker", "Junker test",
     "Ensaio padronizado de vibração transversal para autoafrouxamento.",
     "The standard transverse-vibration test for self-loosening."),
    ("ciclo", "cycle",
     "Uma oscilação completa da excitação; o eixo horizontal das curvas.",
     "One full oscillation of the excitation; the horizontal axis of the curves."),
    ("curva de referência", "reference curve",
     "Dado experimental, do artigo ou de um CSV seu, contra o qual o modelo é "
     "comparado ou ajustado.",
     "Experimental data, from the paper or from a CSV of yours, against which the "
     "model is compared or fitted."),
    ("caso da validação", "validation case",
     "Uma curva publicada com o modelo adotado e a procedência de cada constante.",
     "A published curve with the adopted model and the provenance of every "
     "constant."),
    ("censo", "census",
     "As curvas comparáveis que entram nos números do artigo.",
     "The comparable curves that enter the paper's numbers."),
    ("critério de aceitação (três pernas)", "acceptance criterion (three legs)",
     "MAE, resíduo máximo e desvio dos resíduos, cada um com o seu limite.",
     "MAE, maximum residual and residual spread, each with its own limit."),
    ("MAE, erro médio absoluto", "MAE, mean absolute error",
     "Média do módulo da diferença entre modelo e dado, em fração de F₀.",
     "Mean of the absolute difference between model and data, as a fraction of F₀."),
    ("resíduo", "residual",
     "Diferença entre o modelo e o dado num ciclo.",
     "Difference between model and data at one cycle."),
    ("alinhamento", "alignment",
     "Divisão do modelo pelo seu valor no primeiro ciclo medido; o MAE cru é "
     "reportado ao lado.",
     "Division of the model by its value at the first measured cycle; the raw MAE "
     "is reported beside it."),
    ("calibração", "calibration",
     "Busca dos parâmetros marcados, entre os limites, que minimizam o erro contra a "
     "curva de referência.",
     "Search for the ticked parameters, within their bounds, that minimise the error "
     "against the reference curve."),
    ("limites Lo / Hi", "bounds Lo / Hi",
     "Menor e maior valor que a calibração pode dar a um parâmetro.",
     "Lowest and highest value the calibration may give a parameter."),
    ("procedência", "provenance",
     "De onde veio cada constante adotada: medida, literatura ou ajuste.",
     "Where each adopted constant came from: measurement, literature or fit."),
    ("motor V2", "V2 engine",
     "O solucionador não linear do artigo; o mesmo no Run e na calibração.",
     "The paper's non-linear solver; the same one in Run and in calibration."),
    ("Step", "Step",
     "Tipo de análise: Static-Preload, a pré-carga estática, ou Coupled-Loosening, o "
     "afrouxamento acoplado.",
     "Analysis type: Static-Preload, the static preload, or Coupled-Loosening, the "
     "coupled loosening."),
    ("módulo", "module",
     "Cada etapa da barra: Model, Contacts, Loads, Analysis, Results, Report.",
     "Each stage of the bar: Model, Contacts, Loads, Analysis, Results, Report."),
    ("viewport", "viewport",
     "A área central onde a cadeia é desenhada.",
     "The central area where the chain is drawn."),
    ("linha de prompt", "prompt line",
     "A frase na base da janela que diz o que fazer agora.",
     "The sentence at the base of the window saying what to do now."),
    ("intake", "intake",
     "Fluxo para trazer o seu ensaio: prompt para uma IA, arquivo .bascase.json de "
     "volta, importação.",
     "The flow that brings your test in: prompt to an AI, .bascase.json file back, "
     "import."),
    ("VDI 2230", "VDI 2230",
     "Diretriz alemã de cálculo de juntas aparafusadas; origem dos setenta por cento "
     "do escoamento como pré-carga típica.",
     "German guideline for bolted-joint design; the origin of seventy percent of "
     "yield as the typical preload."),
]
