# -*- coding: utf-8 -*-
"""Prosa PT/EN das secoes 23-25 do help (2026-09-02).

Separado do gerador de proposito: aqui e' texto, la' e' montagem. O gerador
cruza este dicionario com o que EXTRAI do codigo (o enum ElementType, o mapa
ELEMENT_VISUALS, os titulos de QMessageBox) e o teste exige que todo item
extraido tenha entrada aqui. Item novo no codigo aparece como lacuna, nao como
silencio.

Idioma: cada entrada e' (pt, en). O mecanismo e' o `Lang.tr` que ja' existia em
gui/i18n.py sem nenhum consumidor.
"""

# ---------------------------------------------------------------------------
# 23. Tipos de elemento e de ligacao
# ---------------------------------------------------------------------------
# Ancorado no que o codigo diz: nome e simbolo da paleta, rigidez padrao e a
# descricao de uma linha do ELEMENT_VISUALS. O texto abaixo acrescenta o PAPEL
# de cada tipo na cadeia e quando usa-lo, que e' o que a descricao de uma linha
# nao cabe.
#
# `papel`: "corpo" (carrega massa e rigidez) ou "ligacao" (carrega a tribologia)
ELEMENTOS = {
    "GROUND": dict(papel="fronteira", pt=(
        "A fronteira fixa da cadeia. Rigidez praticamente infinita "
        "(1e15 N/m) de proposito: e' o que impede a cadeia de flutuar. Todo "
        "modelo tem exatamente um, e o solver o usa como referencia de "
        "deslocamento.",
        "Nao se edita a rigidez do Ground. Se voce precisa de um apoio "
        "flexivel, modele-o como um elemento de corpo entre o Ground e a "
        "junta."), en=(
        "The fixed boundary of the chain. Its stiffness is deliberately "
        "near-infinite (1e15 N/m): it is what keeps the chain from floating. "
        "Every model has exactly one, and the solver uses it as the "
        "displacement reference.",
        "Do not edit the Ground stiffness. If you need a compliant support, "
        "model it as a body element between the Ground and the joint.")),

    "HEAD": dict(papel="corpo", pt=(
        "A cabeca do parafuso, com a superficie de apoio. Carrega a massa da "
        "cabeca e a rigidez local do material.",
        "A perda de pre-carga NAO acontece aqui: acontece na INTERFACE sob a "
        "cabeca, que e' o elemento Bearing (Head). Confundir os dois e' o erro "
        "mais comum ao montar a cadeia."), en=(
        "The bolt head, with its bearing surface. It carries the mass of the "
        "head and the local stiffness of the material.",
        "Preload loss does NOT happen here: it happens at the INTERFACE under "
        "the head, which is the Bearing (Head) element. Confusing the two is "
        "the commonest mistake when assembling the chain.")),

    "SHANK": dict(papel="corpo", pt=(
        "O trecho liso do parafuso. E' a mola principal da junta: a rigidez "
        "padrao (2,32 GN/m) sai do diametro, do comprimento de aperto e do "
        "modulo, e e' ela que define quanto a pre-carga cai por unidade de "
        "assentamento.",
        "Com o calculo automatico ligado, mudar diametro ou comprimento "
        "recalcula k. E' o caminho recomendado: digitar k a mao desacopla o "
        "modelo da geometria."), en=(
        "The unthreaded portion of the bolt. It is the main spring of the "
        "joint: the default stiffness (2.32 GN/m) follows from diameter, grip "
        "length and modulus, and it sets how much preload falls per unit of "
        "settlement.",
        "With auto-calculate on, changing diameter or length recomputes k. "
        "That is the recommended path: typing k by hand decouples the model "
        "from the geometry.")),

    "THREAD": dict(papel="corpo", pt=(
        "O trecho rosqueado, ou o proprio prisioneiro. Rigidez padrao bem "
        "menor que a do trecho liso (66 MN/m) porque a area resistente e' a "
        "da secao de rosca.",
        "Nao confundir com o contato de rosca: este elemento e' o CORPO "
        "rosqueado; o atrito e o escorregamento entre flancos vivem na "
        "ligacao."), en=(
        "The threaded portion, or the stud itself. Its default stiffness is "
        "far lower than the plain shank (66 MN/m) because the resisting area "
        "is that of the thread section.",
        "Not to be confused with the thread contact: this element is the "
        "threaded BODY; friction and slip between flanks live in the "
        "connection.")),

    "NUT": dict(papel="corpo", pt=(
        "A porca, com o engajamento de rosca. Carrega massa e a rigidez do "
        "engajamento.",
        "A rotacao de afrouxamento e' um estado do modelo, nao um parametro "
        "deste elemento: ela aparece nos resultados como o canal "
        "'rotational_loosening'."), en=(
        "The nut, with its thread engagement. It carries mass and the "
        "stiffness of the engagement.",
        "Loosening rotation is a state of the model, not a parameter of this "
        "element: it appears in the results as the 'rotational_loosening' "
        "channel.")),

    "WASHER": dict(papel="corpo", pt=(
        "Arruela lisa ou elastica, como CORPO. Rigidez padrao alta "
        "(5 GN/m) para arruela lisa de aco.",
        "Arruela elastica NAO e' modelada baixando esta rigidez as cegas: "
        "reduza-a com o valor da propria arruela, e lembre que a interface "
        "que ela cria e' o Washer Contact."), en=(
        "Plain or spring washer, as a BODY. The default stiffness is high "
        "(5 GN/m), for a plain steel washer.",
        "A spring washer is NOT modelled by lowering this stiffness blindly: "
        "reduce it with the washer's own value, and remember that the "
        "interface it creates is the Washer Contact.")),

    "FLANGE": dict(papel="corpo", pt=(
        "Membro flangeado apertado pela junta. Rigidez padrao 3 GN/m.",
        "Em juntas de varios membros, um elemento por membro, em serie. A "
        "soma em serie e' o que produz o comprimento de aperto efetivo."), en=(
        "Clamped flange member. Default stiffness 3 GN/m.",
        "In multi-member joints, one element per member, in series. The "
        "series sum is what produces the effective grip length.")),

    "GASKET": dict(papel="corpo", pt=(
        "Junta de vedacao compressivel. Rigidez padrao 500 MN/m, uma ordem "
        "abaixo dos membros metalicos, e e' por isso que a gaxeta domina o "
        "assentamento quando esta' presente.",
        "Se o modelo tem gaxeta e o assentamento medido e' pequeno, "
        "desconfie da rigidez antes de mexer nos coeficientes de "
        "embedding."), en=(
        "Compressible gasket. Default stiffness 500 MN/m, an order below the "
        "metallic members, which is why a gasket dominates settlement when it "
        "is present.",
        "If the model has a gasket and the measured settlement is small, "
        "suspect the stiffness before touching the embedding "
        "coefficients.")),

    "BEARING_HEAD": dict(papel="ligacao", pt=(
        "A interface sob a cabeca do parafuso. E' UMA DAS DUAS LIGACOES QUE "
        "DECIDEM O AFROUXAMENTO: e' aqui que a face de apoio escorrega, "
        "assenta e desgasta. Rigidez de contato padrao 10 GN/m, alta porque "
        "contato metal-metal e' rigido em compressao.",
        "Os parametros que a validacao calibra vivem neste elemento e no "
        "Bearing (Nut): coeficiente de atrito, profundidade de assentamento e "
        "coeficientes de desgaste. Um modelo sem estas duas ligacoes nao "
        "afrouxa, por construcao."), en=(
        "The interface under the bolt head. It is ONE OF THE TWO CONNECTIONS "
        "THAT DECIDE LOOSENING: this is where the bearing face slips, beds in "
        "and wears. Default contact stiffness 10 GN/m, high because "
        "metal-to-metal contact is stiff in compression.",
        "The parameters the validation calibrates live in this element and in "
        "Bearing (Nut): friction coefficient, embedding depth and wear "
        "coefficients. A model without these two connections does not loosen, "
        "by construction.")),

    "BEARING_NUT": dict(papel="ligacao", pt=(
        "A interface sob a porca. A OUTRA ligacao que decide o afrouxamento, "
        "simetrica a da cabeca e com a mesma rigidez padrao.",
        "Em ensaio Junker tipico as duas faces de apoio nao veem a mesma "
        "condicao: e' comum atrito diferente na cabeca e na porca, e o "
        "inspector permite valores distintos."), en=(
        "The interface under the nut. The OTHER connection that decides "
        "loosening, symmetric to the head one and with the same default "
        "stiffness.",
        "In a typical Junker test the two bearing faces do not see the same "
        "condition: different friction at head and nut is common, and the "
        "inspector allows distinct values.")),

    "FLANGE_FLANGE": dict(papel="ligacao", pt=(
        "Contato metal-metal entre dois membros apertados. Rigidez padrao "
        "10 GN/m.",
        "Esta ligacao transmite a carga transversal entre membros. Em ensaio "
        "de deslocamento controlado e' por aqui que o deslocamento imposto "
        "entra na junta."), en=(
        "Metal-to-metal contact between two clamped members. Default "
        "stiffness 10 GN/m.",
        "This connection transmits the transverse load between members. In a "
        "displacement-controlled test it is through here that the imposed "
        "displacement enters the joint.")),

    "WASHER_CONTACT": dict(papel="ligacao", pt=(
        "A interface de apoio criada pela arruela. Rigidez padrao 8 GN/m.",
        "Uma arruela acrescenta DUAS interfaces, nao uma: entre cabeca e "
        "arruela e entre arruela e membro. Modelar so' uma subestima o "
        "assentamento total."), en=(
        "The bearing interface created by the washer. Default stiffness "
        "8 GN/m.",
        "A washer adds TWO interfaces, not one: between head and washer, and "
        "between washer and member. Modelling only one underestimates the "
        "total settlement.")),

    "GASKET_CONTACT": dict(papel="ligacao", pt=(
        "A interface de compressao da gaxeta. Rigidez padrao 500 MN/m, igual "
        "a da gaxeta como corpo, porque compressao e interface se confundem "
        "num material macio.",
        "E' o caminho por onde a fluencia da gaxeta entra no modelo. Junta "
        "com gaxeta polimerica sob carga sustentada perde pre-carga por aqui "
        "mesmo sem vibracao."), en=(
        "The gasket compression interface. Default stiffness 500 MN/m, the "
        "same as the gasket body, because in a soft material compression and "
        "interface merge.",
        "It is the route by which gasket creep enters the model. A joint with "
        "a polymer gasket under sustained load loses preload here even "
        "without vibration.")),

    "GENERIC_CONTACT": dict(papel="ligacao", pt=(
        "Interface generica, para um par de superficies que nao cai nos "
        "casos acima. Rigidez padrao 10 GN/m.",
        "Use quando a geometria real nao e' nenhuma das interfaces nomeadas. "
        "Como e' generica, nao carrega nenhuma hipotese sobre a geometria: "
        "todos os parametros tribologicos precisam ser informados."), en=(
        "A generic interface, for a pair of surfaces that does not fall into "
        "the cases above. Default stiffness 10 GN/m.",
        "Use it when the real geometry is none of the named interfaces. Being "
        "generic, it carries no assumption about geometry: every tribological "
        "parameter has to be supplied.")),

    "MEMBER": dict(papel="corpo", pt=(
        "Membro apertado, generico. EXISTE NO MODELO MAS NAO ESTA' NA PALETA: "
        "voce nao consegue arrasta-lo, e ele aparece em modelos montados por "
        "codigo ou pelo wizard.",
        "Na pratica, use Flange para membro metalico e Gasket para "
        "compressivel; os dois cobrem o que Member faria."), en=(
        "A generic clamped member. IT EXISTS IN THE MODEL BUT IS NOT IN THE "
        "PALETTE: you cannot drag it, and it appears in models assembled by "
        "code or by the wizard.",
        "In practice use Flange for a metallic member and Gasket for a "
        "compressible one; between them they cover what Member would do.")),

    "THERMAL": dict(papel="corpo", pt=(
        "Elemento termico. EXISTE NO MODELO MAS NAO ESTA' NA PALETA.",
        "A dilatacao termica dos elementos e' tratada pelo coeficiente alpha "
        "de cada material, no inspector. Este tipo esta' reservado para "
        "acoplamento termico explicito, que o solver atual nao usa."), en=(
        "A thermal element. IT EXISTS IN THE MODEL BUT IS NOT IN THE PALETTE.",
        "Thermal expansion of the elements is handled by each material's "
        "alpha coefficient, in the inspector. This type is reserved for "
        "explicit thermal coupling, which the current solver does not use.")),

    "BEAM_CONNECTOR": dict(papel="ligacao", pt=(
        "Conector de viga, para juntas de varios parafusos. EXISTE NO MODELO "
        "MAS NAO ESTA' NA PALETA.",
        "Em analise multi-parafuso ele liga as cadeias individuais a "
        "estrutura. Modelos de um parafuso, que sao os 210 da validacao, nao "
        "o usam."), en=(
        "A beam connector, for multi-bolt joints. IT EXISTS IN THE MODEL BUT "
        "IS NOT IN THE PALETTE.",
        "In a multi-bolt analysis it ties the individual chains to the "
        "structure. Single-bolt models, which is what the 210 validation "
        "cases are, do not use it.")),
}

# ---------------------------------------------------------------------------
# 24. Construir um modelo do zero
# ---------------------------------------------------------------------------
# O fluxo REAL, nomeando as portas de entrada. A secao 9 que ja' existia fala
# de paleta e arrastar sem nomear nem o New Analysis Wizard nem o MSD Builder,
# que sao as duas formas de comecar.
PASSOS = [
    dict(chave="wizard", print_="chrome_model", pt=(
        "1. Comece pelo wizard, nao pela tela vazia",
        "<b>Arquivo &rarr; Nova analise</b> abre o <i>New Analysis Wizard</i>. "
        "Ele pergunta o essencial (diametro do parafuso, comprimento de "
        "aperto, material, tipo de ensaio) e monta a cadeia completa, com "
        "GROUND, corpos e as duas ligacoes de apoio ja' no lugar. Comecar "
        "assim evita o erro mais comum de quem monta a mao: esquecer as "
        "interfaces Bearing (Head) e Bearing (Nut), sem as quais o modelo "
        "nao afrouxa.",
        "Se voce quer partir de um caso conhecido em vez de responder "
        "perguntas, va' ao modulo <b>Results &rarr; Validation</b>, escolha "
        "uma curva e clique em <b>Abrir no Model/Run</b>: o modelo chega "
        "montado e com as constantes adotadas daquele artigo."), en=(
        "1. Start from the wizard, not from an empty canvas",
        "<b>File &rarr; New analysis</b> opens the <i>New Analysis Wizard</i>. "
        "It asks for the essentials (bolt diameter, grip length, material, "
        "test type) and assembles the whole chain, with GROUND, bodies and "
        "the two bearing connections already in place. Starting this way "
        "avoids the commonest mistake of assembling by hand: forgetting the "
        "Bearing (Head) and Bearing (Nut) interfaces, without which the model "
        "does not loosen.",
        "If you would rather start from a known case than answer questions, "
        "go to <b>Results &rarr; Validation</b>, pick a curve and press "
        "<b>Abrir no Model/Run</b>: the model arrives assembled and with the "
        "adopted constants of that paper.")),

    dict(chave="builder", print_="chrome_model", pt=(
        "2. Ajuste a cadeia no MSD Builder",
        "O modulo <b>Model</b> (<kbd>Ctrl</kbd>+<kbd>1</kbd>) E' o MSD "
        "Builder: o canvas onde a junta aparece como cadeia de elementos. "
        "Arraste da paleta a direita para acrescentar, clique duas vezes para "
        "editar. A ordem na cadeia importa: corpos em serie somam "
        "flexibilidade, e cada ligacao fica ENTRE os dois corpos que ela "
        "conecta.",
        "Regra de sanidade antes de seguir: a cadeia tem de ter um GROUND, "
        "pelo menos um corpo de parafuso, pelo menos um membro, e as duas "
        "ligacoes de apoio. <kbd>Shift</kbd>+<kbd>F</kbd> enquadra o desenho "
        "se ele sair de vista."), en=(
        "2. Adjust the chain in the MSD Builder",
        "The <b>Model</b> module (<kbd>Ctrl</kbd>+<kbd>1</kbd>) IS the MSD "
        "Builder: the canvas where the joint appears as a chain of elements. "
        "Drag from the palette on the right to add, double-click to edit. "
        "Order in the chain matters: bodies in series add compliance, and "
        "each connection sits BETWEEN the two bodies it joins.",
        "A sanity rule before moving on: the chain must have a GROUND, at "
        "least one bolt body, at least one member, and the two bearing "
        "connections. <kbd>Shift</kbd>+<kbd>F</kbd> frames the drawing if it "
        "drifts out of view.")),

    dict(chave="element", print_="inspector_element", pt=(
        "3. Deixe a geometria calcular a rigidez",
        "Selecione um elemento e abra a aba <b>Element</b> do inspector. "
        "Prefira ligar o <i>auto-calculate</i> de k, c e m e informar "
        "geometria e material: a rigidez de um parafuso segue do diametro, do "
        "comprimento de aperto e do modulo, e digitar k a mao desacopla o "
        "modelo da geometria que voce vai variar depois.",
        "O material vem da base embutida. Se o seu aco nao esta' la', "
        "informe E, Sy, Su e densidade a mao; alpha so' importa se houver "
        "variacao de temperatura."), en=(
        "3. Let the geometry compute the stiffness",
        "Select an element and open the <b>Element</b> tab of the inspector. "
        "Prefer switching <i>auto-calculate</i> on for k, c and m and "
        "supplying geometry and material: a bolt's stiffness follows from "
        "diameter, grip length and modulus, and typing k by hand decouples "
        "the model from the geometry you will vary later.",
        "The material comes from the bundled database. If your steel is not "
        "there, supply E, Sy, Su and density by hand; alpha only matters if "
        "there is a temperature change.")),

    dict(chave="contact", print_="inspector_contact", pt=(
        "4. Preencha a tribologia das ligacoes",
        "No modulo <b>Contacts</b> (<kbd>Ctrl</kbd>+<kbd>2</kbd>), selecione "
        "cada interface e abra a aba <b>Contact</b>. Aqui vivem o coeficiente "
        "de atrito, a rigidez de contato, os parametros de assentamento e os "
        "de desgaste. E' o passo que a maioria pula e o que mais muda o "
        "resultado: sao estas constantes que a validacao calibra.",
        "Se voce nao tem valores medidos, comece pelos padroes e compare com "
        "um caso do corpus que se pareca com a sua junta: a secao 20 lista as "
        "29 fontes com as condicoes de cada uma."), en=(
        "4. Fill in the tribology of the connections",
        "In the <b>Contacts</b> module (<kbd>Ctrl</kbd>+<kbd>2</kbd>), select "
        "each interface and open the <b>Contact</b> tab. Friction "
        "coefficient, contact stiffness, embedding parameters and wear "
        "coefficients live here. This is the step most people skip and the "
        "one that changes the result most: these are the constants the "
        "validation calibrates.",
        "If you have no measured values, start from the defaults and compare "
        "with a corpus case that resembles your joint: Section 20 lists the "
        "29 sources with the conditions of each.")),

    dict(chave="loads", print_="chrome_loads", pt=(
        "5. Defina a carga e a pre-carga",
        "No modulo <b>Loads</b> (<kbd>Ctrl</kbd>+<kbd>3</kbd>): pre-carga em "
        "newtons ou como percentual do escoamento, e a excitacao. "
        "Deslocamento transversal controlado e' a condicao Junker, que e' a "
        "severa; forca axial controlada e' a outra familia do corpus.",
        "Deixar a forca de pre-carga em zero faz o modelo calcula-la do "
        "percentual. O overlay de fluxo de carga anota a cadeia com a parcela "
        "que cada elemento carrega, e e' a maneira mais rapida de ver uma "
        "particao de rigidez implausivel ANTES de rodar."), en=(
        "5. Define the load and the preload",
        "In the <b>Loads</b> module (<kbd>Ctrl</kbd>+<kbd>3</kbd>): preload "
        "in newtons or as a percentage of yield, and the excitation. "
        "Displacement-controlled transverse loading is the Junker condition, "
        "the severe one; force-controlled axial loading is the other family "
        "in the corpus.",
        "Leaving the preload force at zero makes the model compute it from "
        "the percentage. The load-flow overlay annotates the chain with the "
        "share each element carries, and is the quickest way to see an "
        "implausible stiffness partition BEFORE running anything.")),

    dict(chave="analysis", print_="chrome_analysis", pt=(
        "6. Rode",
        "No modulo <b>Analysis</b> (<kbd>Ctrl</kbd>+<kbd>4</kbd>) escolha o "
        "numero de ciclos e quais mecanismos de perda ficam ativos. Os quatro "
        "atuam em paralelo: assentamento, fluencia, desgaste por fretting e "
        "rotacao. <kbd>Ctrl</kbd>+<kbd>R</kbd> roda de qualquer modulo.",
        "Desligar um mecanismo de cada vez e' a forma mais direta de "
        "entender de onde vem a perda no SEU modelo. A secao 14 explica o "
        "acoplamento entre eles."), en=(
        "6. Run",
        "In the <b>Analysis</b> module (<kbd>Ctrl</kbd>+<kbd>4</kbd>) choose "
        "the cycle count and which loss mechanisms stay active. The four act "
        "in parallel: embedding, creep, fretting wear and rotation. "
        "<kbd>Ctrl</kbd>+<kbd>R</kbd> runs from any module.",
        "Switching one mechanism off at a time is the most direct way to see "
        "where the loss in YOUR model comes from. Section 14 explains the "
        "coupling between them.")),

    dict(chave="results", print_="chrome_results", pt=(
        "7. Leia o resultado, e salve",
        "O modulo <b>Results</b> (<kbd>Ctrl</kbd>+<kbd>5</kbd>), aba "
        "<b>Run</b>, traz pre-carga contra ciclos e a decomposicao por "
        "mecanismo: e' a decomposicao que diz se a perda foi assentamento no "
        "inicio ou desgaste ao longo do ensaio.",
        "Salve o modelo em <code>.msd</code>. A partir da correcao de "
        "2026-09-02 o arquivo preserva os dois canais de override, entao "
        "reabrir devolve a configuracao inteira; antes dela, as constantes "
        "adotadas se perdiam em silencio."), en=(
        "7. Read the result, and save",
        "The <b>Results</b> module (<kbd>Ctrl</kbd>+<kbd>5</kbd>), <b>Run</b> "
        "tab, shows preload against cycles and the mechanism decomposition: "
        "it is the decomposition that tells you whether the loss was "
        "settlement at the start or wear along the test.",
        "Save the model as <code>.msd</code>. Since the fix of 2026-09-02 the "
        "file preserves both override channels, so reopening returns the "
        "whole configuration; before it, the adopted constants were lost "
        "silently.")),
]

# ---------------------------------------------------------------------------
# 25. Catalogo de dialogos e erros
# ---------------------------------------------------------------------------
# Cobertura COMPLETA com profundidade proporcional: o que e' falha (critical e
# warning) ganha causa e acao; o que e' informativo ou pergunta ganha uma
# linha. O gerador cruza com os titulos extraidos do codigo e marca como
# "sem entrada revisada" o que nao estiver aqui, em vez de omitir.
DIALOGOS = {
    # --- falhas de analise e solver ---
    "Analysis Error": dict(pt=("A analise parou com excecao.",
        "Causa usual: cadeia incompleta (sem GROUND, ou sem uma das ligacoes "
        "de apoio) ou constante fora de faixa. Abra o painel Messages: a "
        "excecao original vai para o crash_log.txt na pasta do programa."),
        en=("The analysis stopped with an exception.",
        "Usual cause: an incomplete chain (no GROUND, or one of the bearing "
        "connections missing) or a constant out of range. Open the Messages "
        "panel: the original exception goes to crash_log.txt in the program "
        "folder.")),
    "Run Analysis": dict(pt=("Nao foi possivel iniciar a analise.",
        "Verifique se ha' um modelo carregado e um step selecionado. Sem "
        "modelo o botao Run fica ativo mas nao ha' o que integrar."),
        en=("The analysis could not be started.",
        "Check that a model is loaded and a step is selected. With no model "
        "the Run button is still enabled but there is nothing to "
        "integrate.")),
    "Send to Solver": dict(pt=("O modelo nao chegou ao solver.",
        "Acontece quando a cadeia tem elemento sem k valido. Rode "
        "'Recalculate All Elements' e veja quais falham."),
        en=("The model did not reach the solver.",
        "This happens when the chain has an element with no valid k. Run "
        "'Recalculate All Elements' and see which ones fail.")),
    "No Results": dict(pt=("Nao ha' resultado para mostrar.",
        "Rode uma analise no modulo Analysis (Ctrl+R) antes de abrir os "
        "plots."),
        en=("There is no result to show.",
        "Run an analysis in the Analysis module (Ctrl+R) before opening the "
        "plots.")),
    "No Plot": dict(pt=("O plot pedido nao existe para este resultado.",
        "Alguns plots dependem de canais que so' existem com o mecanismo "
        "correspondente ativo. Verifique quais mecanismos foram rodados."),
        en=("The requested plot does not exist for this result.",
        "Some plots depend on channels that only exist with the matching "
        "mechanism active. Check which mechanisms were run.")),
    # --- modelo e elementos ---
    "Recalculate Error": dict(pt=("Um ou mais elementos nao recalcularam.",
        "Falta geometria ou material no elemento. Abra a aba Element do "
        "inspector e preencha diametro, comprimento e material antes de "
        "religar o auto-calculate."),
        en=("One or more elements failed to recompute.",
        "The element is missing geometry or material. Open the Element tab of "
        "the inspector and supply diameter, length and material before "
        "switching auto-calculate back on.")),
    "Recalculation Completed with Errors": dict(pt=(
        "O recalculo terminou, mas alguns elementos ficaram sem valor.",
        "Os que falharam mantem o valor anterior. A lista aparece no painel "
        "Messages; corrija a geometria deles antes de rodar."),
        en=("The recomputation finished, but some elements were left without "
            "a value.",
        "The ones that failed keep their previous value. The list appears in "
        "the Messages panel; fix their geometry before running.")),
    "No Selection": dict(pt=("Nenhum elemento selecionado.",
        "A acao pedida age sobre o elemento selecionado no canvas. Clique num "
        "elemento primeiro."),
        en=("No element is selected.",
        "The requested action acts on the element selected in the canvas. "
        "Click an element first.")),
    "Builder load": dict(pt=("O modelo nao pode ser desenhado no canvas.",
        "O arquivo abriu, mas a topologia nao pode ser reconstruida. Um .msd "
        "de versao antiga pode carecer da grade; reabra pelo wizard e "
        "reaplique os parametros."),
        en=("The model could not be drawn on the canvas.",
        "The file opened, but the topology could not be rebuilt. A .msd from "
        "an older version may lack the grid; reopen through the wizard and "
        "reapply the parameters.")),
    "Wizard error": dict(pt=("O wizard falhou ao montar o modelo.",
        "Combinacao de entradas que nao produz cadeia valida, em geral "
        "comprimento de aperto menor que a soma das espessuras. Revise as "
        "dimensoes."),
        en=("The wizard failed to assemble the model.",
        "A combination of inputs that does not produce a valid chain, "
        "usually a grip length shorter than the sum of the thicknesses. "
        "Review the dimensions.")),
    "Wizard unavailable": dict(pt=("O wizard nao pode ser aberto.",
        "Modulo ausente na instalacao. Rode BAS-console.cmd para ver o erro "
        "de import."),
        en=("The wizard could not be opened.",
        "The module is missing from the installation. Run BAS-console.cmd to "
        "see the import error.")),
    # --- arquivos ---
    "Save Failed": dict(pt=("O arquivo nao foi gravado.",
        "Permissao de escrita, caminho inexistente, ou arquivo aberto em "
        "outro programa. Em caminho muito longo, o Windows corta em 260 "
        "caracteres: escolha um destino mais curto."),
        en=("The file was not written.",
        "Write permission, a path that does not exist, or the file open in "
        "another program. On a very long path Windows cuts off at 260 "
        "characters: choose a shorter destination.")),
    "Salvar caso": dict(pt=("O caso da validacao nao foi salvo como .msd.",
        "Mesmas causas de 'Save Failed'. Os 210 casos ja' vem salvos em "
        "Models/SAVED_CASES, entao voce pode abrir de la' em vez de "
        "regravar."),
        en=("The validation case was not saved as .msd.",
        "Same causes as 'Save Failed'. The 210 cases already ship saved in "
        "Models/SAVED_CASES, so you can open from there instead of writing "
        "again.")),
    "CSV Import Error": dict(pt=("O CSV nao pode ser lido.",
        "O leitor espera duas colunas numericas. Cabecalho com nome "
        "inesperado, separador decimal por virgula ou linha em branco no meio "
        "derrubam a leitura."),
        en=("The CSV could not be read.",
        "The reader expects two numeric columns. An unexpected header name, "
        "a comma decimal separator or a blank line in the middle will break "
        "it.")),
    "Save Fixture Profile": dict(pt=("O perfil de bancada nao foi gravado.",
        "Verifique permissao de escrita na pasta de configuracao do "
        "programa."),
        en=("The fixture profile was not written.",
        "Check write permission in the program's configuration folder.")),
    "CMMS Export Failed": dict(pt=("A exportacao para CMMS falhou.",
        "Destino nao gravavel ou resultado incompleto. Rode a analise antes "
        "de exportar."),
        en=("The CMMS export failed.",
        "The destination is not writable or the result is incomplete. Run "
        "the analysis before exporting.")),
    # --- validacao de entrada ---
    "Validation Failed": dict(pt=("A validacao das entradas reprovou.",
        "O painel lista o campo e o motivo. Reprovacao aqui impede a analise "
        "de propósito: e' mais barato corrigir a entrada que interpretar um "
        "resultado sem sentido."),
        en=("Input validation failed.",
        "The panel lists the field and the reason. Failing here blocks the "
        "analysis on purpose: fixing the input is cheaper than interpreting a "
        "meaningless result.")),
    "Validation Passed with Warnings": dict(pt=(
        "As entradas passaram, com ressalvas.",
        "A analise roda, mas algum valor esta' fora da faixa em que o modelo "
        "foi confrontado com experimento. A secao 20 mostra as faixas "
        "cobertas por fonte."),
        en=("The inputs passed, with reservations.",
        "The analysis will run, but some value is outside the range where the "
        "model was confronted with experiment. Section 20 shows the ranges "
        "covered per source.")),
    "Validation": dict(pt=("Aviso do modulo de validacao.",
        "Em geral um caso que nao pode ser simulado (familia 'other') ou "
        "store sem resultado. Re-simule o caso."),
        en=("A warning from the validation module.",
        "Usually a case that cannot be simulated (family 'other') or a store "
        "with no result. Re-simulate the case.")),
    # --- outros avisos ---
    "No Thread Model": dict(pt=("Nao ha' modelo de rosca definido.",
        "A analise pedida depende da geometria de rosca. Defina o passo e o "
        "tipo de rosca no elemento Thread."),
        en=("There is no thread model defined.",
        "The requested analysis depends on the thread geometry. Set the pitch "
        "and thread type on the Thread element.")),
    "No Scaled Model": dict(pt=("Nao ha' modelo escalado.",
        "O modulo de similitude precisa de um modelo base e de um fator de "
        "escala antes de gerar o escalado."),
        en=("There is no scaled model.",
        "The similitude module needs a base model and a scale factor before "
        "it can produce the scaled one.")),
    "Similitude Module Not Loaded": dict(pt=(
        "O modulo de similitude nao esta' carregado.",
        "Funcionalidade opcional; ausencia nao afeta a analise de "
        "afrouxamento."),
        en=("The similitude module is not loaded.",
        "An optional feature; its absence does not affect the loosening "
        "analysis.")),
    "No URL Available": dict(pt=("Nao ha' endereco para abrir.",
        "O item nao tem DOI ou link registrado. Os casos que nao sao "
        "publicacao (UFU_LAB, USER) nao tem DOI por natureza."),
        en=("There is no address to open.",
        "The item has no DOI or link on record. Cases that are not "
        "publications (UFU_LAB, USER) have no DOI by nature.")),
    "Pin Limit Reached": dict(pt=("Limite de itens fixados atingido.",
        "Solte um item antes de fixar outro."),
        en=("The limit of pinned items has been reached.",
        "Release one before pinning another.")),
    "Unsaved Changes": dict(pt=("Ha' alteracoes nao salvas.",
        "Escolha salvar, descartar ou cancelar. O programa tambem grava "
        "auto-save, oferecido em 'Restore Auto-Save' na proxima abertura."),
        en=("There are unsaved changes.",
        "Choose to save, discard or cancel. The program also writes an "
        "auto-save, offered as 'Restore Auto-Save' the next time it "
        "opens.")),
}

# Titulos que sao confirmacao, aviso de conclusao ou pergunta de rotina: uma
# linha basta, e o gerador as marca como tal em vez de fingir analise.
DIALOGOS_SIMPLES = {
    "About Bolt Analysis Studio": ("Sobre o programa: versao, autores e licenca.",
                                   "About the program: version, authors and licence."),
    "Report Generated": ("O relatorio foi gerado; a mensagem traz o caminho.",
                         "The report was generated; the message gives the path."),
    "Recalculation Complete": ("Todos os elementos recalcularam sem erro.",
                               "Every element recomputed without error."),
    "Recalculate All Elements": ("Pergunta de confirmacao antes de recalcular a cadeia inteira.",
                                 "A confirmation before recomputing the whole chain."),
    "Restore Auto-Save": ("Oferece recuperar o trabalho da sessao anterior.",
                          "Offers to recover the work of the previous session."),
    "Transfer Complete": ("Os valores foram transferidos entre modulos.",
                          "The values were transferred between modules."),
    "Threads Expanded": ("A rosca foi expandida em elementos individuais.",
                         "The thread was expanded into individual elements."),
    "Thread Contacts Expanded": ("Os contatos de rosca foram expandidos.",
                                 "The thread contacts were expanded."),
    "Validation Passed": ("As entradas passaram na validacao.",
                          "The inputs passed validation."),
    "Validation Gallery": ("Informa o caminho da galeria de validacao gerada.",
                           "Reports the path of the generated validation gallery."),
    "CMMS Export": ("Confirma a exportacao para o sistema de manutencao.",
                    "Confirms the export to the maintenance system."),
    "Calibration Tuner": ("Informa que o servidor do tuner subiu e o endereco.",
                          "Reports that the tuner server started, and its address."),
    "Apply & Re-run": ("Pergunta se deve aplicar os valores e rodar de novo.",
                       "Asks whether to apply the values and run again."),
    "Apply Stored Values?": ("Pergunta se deve usar as constantes gravadas do caso.",
                             "Asks whether to use the case's stored constants."),
    "Auto-calibrate μ": ("Pergunta de confirmacao antes de calibrar o atrito.",
                         "A confirmation before calibrating the friction."),
    "Calibrate": ("Confirmacao do inicio da calibracao.",
                  "Confirmation that the calibration is starting."),
    "Agent": ("Mensagem do agente de calibracao.",
              "A message from the calibration agent."),
}
