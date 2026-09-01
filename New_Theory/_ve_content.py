# -*- coding: utf-8 -*-
"""Conteudo autorado (74 campos) do Explorador de Variaveis.

NAO importar diretamente. build_variable_explorer._load_content() executa este
modulo injetando VarSpec e VARIABLE_SPECS no namespace. A prosa usa tags/entidades
que podem vir duplo-escapadas; o render (_norm) normaliza na hora de emitir.
"""

# =============================== EMBEDDING + CREEP-TAIL (9) ===============================
VARIABLE_SPECS.extend([
    VarSpec(name="N_emb", symbol="N_emb", unit="ciclos", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(5, 200, 15, "log"), anchor_key="N_emb", lessons=[], related=["emb_depth"],
        equation="delta_emb(N) = delta_target * (1 - exp(-N/N_emb))   [N_emb = constante de tempo em ciclos]",
        physics_pt=(
            "&lt;p&gt;Se &lt;code&gt;emb_depth&lt;/code&gt; diz &lt;b&gt;quanto&lt;/b&gt; a junta assenta, "
            "&lt;code&gt;N_emb&lt;/code&gt; diz &lt;b&gt;em quantos ciclos&lt;/b&gt;. É a constante de tempo da "
            "exponencial de assentamento: o número característico de ciclos que as "
            "asperezas levam para escoar e a junta acomodar (não a profundidade, só o "
            "ritmo).&lt;/p&gt;"
            "&lt;p&gt;No modelo ela vive no expoente de &amp;delta;emb(N) = &amp;delta;target&amp;middot;"
            "(1&amp;minus;e^(&amp;minus;N/N_emb)); a cada ciclo o incremento é o que resta do "
            "reservatório vezes (1&amp;minus;e^(&amp;minus;1/N_emb)). Mover o slider muda a "
            "&lt;b&gt;nitidez do joelho inicial&lt;/b&gt;, NÃO a sua profundidade final: N_emb pequeno "
            "concentra toda a queda nos primeiros ciclos (degrau abrupto), N_emb grande "
            "espalha a mesma queda por muitos ciclos (rampa suave). A assíntota &amp;minus; e a "
            "F/F0 final &amp;minus; ficam praticamente iguais.&lt;/p&gt;"
            "&lt;p&gt;É uma constante &lt;b&gt;compartilhada do Estágio A&lt;/b&gt; (fitada uma única vez no "
            "dataset inteiro, não por condição); o default de 50 ciclos vale para o rig UFU. "
            "Trabalha em par com &lt;code&gt;emb_depth&lt;/code&gt;: um fixa a escala de tempo, o outro a "
            "profundidade.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;If &lt;code&gt;emb_depth&lt;/code&gt; says &lt;b&gt;how much&lt;/b&gt; the joint beds in, "
            "&lt;code&gt;N_emb&lt;/code&gt; says &lt;b&gt;over how many cycles&lt;/b&gt;. It is the time constant of "
            "the settling exponential: the characteristic number of cycles the asperities "
            "take to yield and the joint to accommodate (not the depth, only the pace).&lt;/p&gt;"
            "&lt;p&gt;In the model it lives in the exponent of &amp;delta;emb(N) = &amp;delta;target&amp;middot;"
            "(1&amp;minus;e^(&amp;minus;N/N_emb)); each cycle the increment is the remaining reservoir "
            "times (1&amp;minus;e^(&amp;minus;1/N_emb)). Moving the slider changes the &lt;b&gt;sharpness of "
            "the initial knee&lt;/b&gt;, NOT its final depth: a small N_emb concentrates the whole "
            "drop in the first few cycles (abrupt step), a large N_emb spreads the same drop "
            "over many cycles (gentle ramp). The asymptote &amp;minus; and the final F/F0 &amp;minus; "
            "stay essentially the same.&lt;/p&gt;"
            "&lt;p&gt;It is a &lt;b&gt;Stage-A shared constant&lt;/b&gt; (fitted once over the whole dataset, "
            "not per condition); the default of 50 cycles fits the UFU rig. It works as a "
            "pair with &lt;code&gt;emb_depth&lt;/code&gt;: one sets the timescale, the other the "
            "depth.&lt;/p&gt;"),
        refs=[("&amp;sect;4.1 EmbeddingLoss &amp;minus; constante de tempo da exponencial de Norton",
               "&amp;sect;4.1 EmbeddingLoss &amp;minus; time constant of the Norton exponential",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;8.1 Estágio A &amp;minus; constante compartilhada (fit único)",
               "&amp;sect;8.1 Stage A &amp;minus; shared constant (single fit)",
               "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="emb_clock_delta_ref", symbol="delta_ref", unit="m", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0, 4e-3, 9, "lin"), related=["N_emb", "emb_depth"],
        equation="N_emb_eff(delta) = N_emb * (delta_ref / |delta_amp|)   [delta_ref = 0 => OFF exato]",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;N_emb&lt;/code&gt; sozinho supõe que o assentamento leva &lt;b&gt;o mesmo "
            "número de ciclos&lt;/b&gt; qualquer que seja o deslocamento imposto. Isso não pode "
            "estar certo: se o que consome o assentamento é o &lt;b&gt;deslizamento&lt;/b&gt;, uma junta "
            "que desliza o dobro por ciclo assenta na metade dos ciclos.&lt;/p&gt;"
            "&lt;p&gt;Este campo torna o relógio dependente da amplitude: N_emb_eff = "
            "N_emb&amp;middot;(&amp;delta;ref/&amp;delta;). &lt;b&gt;O expoente é 1 e NÃO é ajustável&lt;/b&gt; — ele "
            "não foi escolhido, ele cai da mecânica: se o assentamento se esgota depois de "
            "uma distância de slip acumulada S (asperezas achatadas até a área real de "
            "contato saturar), então N_emb = S/(slip por ciclo) e slip por ciclo &amp;prop; "
            "&amp;delta;, logo N_emb &amp;prop; 1/&amp;delta;. Não existe campo para mudar esse expoente, "
            "e um teste proíbe que apareça: transformá-lo em parâmetro converteria uma "
            "&lt;i&gt;consequência&lt;/i&gt; em &lt;i&gt;ajuste&lt;/i&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;&amp;delta;ref não é um parâmetro livre&lt;/b&gt;, é uma escolha de unidade: diz "
            "em qual amplitude o &lt;code&gt;N_emb&lt;/code&gt; que você digitou vale literalmente. "
            "Fixar o par (&amp;delta;ref, N_emb) é o mesmo que fixar N_emb numa amplitude "
            "qualquer. O default 0 desliga a forma de modo &lt;b&gt;exato&lt;/b&gt; (o ramo nem roda).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Irmã da &amp;rho;-unificação, não substituta:&lt;/b&gt; aquela modula o &lt;i&gt;alvo&lt;/i&gt; "
            "do assentamento pela razão de &lt;b&gt;força&lt;/b&gt;; esta modula o &lt;i&gt;relógio&lt;/i&gt; pelo "
            "&lt;b&gt;deslocamento&lt;/b&gt;. Só é identificável em bancada que varre &amp;delta; com força "
            "de excitação fixa — a assinatura do ensaio Junker. Em modo força ela não age.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Estado: validada e NÃO adotada.&lt;/b&gt; Prediz zero-refit 4 de 4 curvas fora "
            "do ajuste (&amp;sigma; &amp;minus;12 a &amp;minus;27%), mas aplicá-la à fonte inteira do "
            "CHU 2026 piorava uma curva acima da tolerância dos gates. O defeito que sobra "
            "naquela fonte é do &lt;i&gt;alvo&lt;/i&gt;, não do relógio.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;N_emb&lt;/code&gt; alone assumes bedding-in takes &lt;b&gt;the same number of "
            "cycles&lt;/b&gt; whatever the imposed displacement. That cannot be right: if slip is "
            "what consumes the settling, a joint sliding twice as far per cycle beds in over "
            "half as many cycles.&lt;/p&gt;"
            "&lt;p&gt;This field makes the clock amplitude-dependent: N_emb_eff = "
            "N_emb&amp;middot;(&amp;delta;ref/&amp;delta;). &lt;b&gt;The exponent is 1 and is NOT "
            "adjustable&lt;/b&gt; — it was not chosen, it falls out of the mechanism: if settling "
            "exhausts after an accumulated slip distance S (asperities flattened until the "
            "real contact area saturates), then N_emb = S/(slip per cycle) and slip per cycle "
            "&amp;prop; &amp;delta;, hence N_emb &amp;prop; 1/&amp;delta;. There is no field to change that "
            "exponent, and a test forbids one appearing: making it a parameter would turn a "
            "&lt;i&gt;consequence&lt;/i&gt; into a &lt;i&gt;fit&lt;/i&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;&amp;delta;ref is not a free parameter&lt;/b&gt;, it is a choice of unit: it says "
            "at which amplitude the &lt;code&gt;N_emb&lt;/code&gt; you typed holds literally. Fixing the "
            "pair (&amp;delta;ref, N_emb) is the same as fixing N_emb at some amplitude. The "
            "default 0 switches the form off &lt;b&gt;exactly&lt;/b&gt; (the branch never runs).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Sister of the &amp;rho;-unification, not a replacement:&lt;/b&gt; that one modulates "
            "the settling &lt;i&gt;target&lt;/i&gt; by a &lt;b&gt;force&lt;/b&gt; ratio; this one modulates the "
            "&lt;i&gt;clock&lt;/i&gt; by &lt;b&gt;displacement&lt;/b&gt;. It is only identifiable on a rig that sweeps "
            "&amp;delta; at fixed excitation force — the Junker signature. In force mode it does "
            "nothing.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Status: validated and NOT adopted.&lt;/b&gt; It predicts 4 of 4 held-out curves "
            "zero-refit (&amp;sigma; &amp;minus;12 to &amp;minus;27%), but applying it to the whole CHU "
            "2026 source degraded one curve beyond the gate tolerance. What remains wrong in "
            "that source is the &lt;i&gt;target&lt;/i&gt;, not the clock.&lt;/p&gt;"),
        refs=[("&amp;sect;4.1 EmbeddingLoss &amp;minus; relógio do assentamento",
               "&amp;sect;4.1 EmbeddingLoss &amp;minus; settling clock",
               "MODEL_MATH_REFERENCE.md"),
              ("Derivação, predição zero-refit e razão da não-adoção",
               "Derivation, zero-refit prediction and why it was not adopted",
               "New_Theory/lei_relogio_implementada_e_nao_adotada.md")]),

    VarSpec(name="emb_conform_exp", symbol="n_conf", unit="-", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0, 3, 13, "lin"), related=["p_ref_emb", "emb_depth"],
        equation="delta_target *= S_conf;   S_conf = min(1, (p_ref_emb / p_init)^n_conf),   p_init = F0_init / A_contact",
        physics_pt=(
            "&lt;p&gt;Apertar a junta com torque alto já achata parte das asperezas antes de "
            "qualquer ciclo (a área real de contato cresce ~F0/H). Uma junta muito "
            "pré-carregada, então, chega ao ensaio com &lt;b&gt;menos assentamento residual&lt;/b&gt; a "
            "consumir. Este expoente controla o quão forte a assíntota de embedding encolhe "
            "com a pressão de aperto.&lt;/p&gt;"
            "&lt;p&gt;Ele multiplica a profundidade-alvo por S_conf = min(1, (p_ref_emb/p_init)^"
            "n_conf), com p_init = F0_init/A_contact fixado no INÍCIO do run (nunca o F_0 "
            "corrente &amp;minus; sem realimentação, a forma fechada de Norton é preservada). No "
            "slider: em &lt;code&gt;0&lt;/code&gt; o fator vale 1 (inerte, a curva-padrão); ao subir "
            "n_conf a queda inicial encolhe, porque a assíntota é escalada para baixo.&lt;/p&gt;"
            "&lt;p&gt;Capability &lt;b&gt;opt-in, default 0 = OFF&lt;/b&gt; (bit-idêntica quando desligada), "
            "&lt;b&gt;per-rig&lt;/b&gt; como &lt;code&gt;emb_depth&lt;/code&gt;/&lt;code&gt;c_bend&lt;/code&gt;. Foi nomeada para "
            "inclinar d(final)/dP0 no Liu2017; depois a unificação &amp;rho; "
            "(&lt;code&gt;emb_amp_exp&lt;/code&gt;) mostrou que ela é o &lt;b&gt;caso especial a A_F fixo&lt;/b&gt; da "
            "mesma física &amp;minus; usa-se UMA das duas por rig (redução de variável).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Tightening the joint at high torque already flattens some asperities before "
            "any cycle (the real contact area grows ~F0/H). A heavily preloaded joint "
            "therefore arrives at the test with &lt;b&gt;less residual settling&lt;/b&gt; left to consume. "
            "This exponent controls how strongly the embedding asymptote shrinks with clamp "
            "pressure.&lt;/p&gt;"
            "&lt;p&gt;It multiplies the target depth by S_conf = min(1, (p_ref_emb/p_init)^n_conf), "
            "with p_init = F0_init/A_contact fixed at the START of the run (never the current "
            "F_0 &amp;minus; no feedback, so the closed Norton form is preserved). On the slider: "
            "at &lt;code&gt;0&lt;/code&gt; the factor is 1 (inert, the standard curve); raising n_conf "
            "shrinks the initial drop, because the asymptote is scaled down.&lt;/p&gt;"
            "&lt;p&gt;An &lt;b&gt;opt-in capability, default 0 = OFF&lt;/b&gt; (bit-identical when off), "
            "&lt;b&gt;per-rig&lt;/b&gt; like &lt;code&gt;emb_depth&lt;/code&gt;/&lt;code&gt;c_bend&lt;/code&gt;. It was named to "
            "tilt d(final)/dP0 in Liu2017; the &amp;rho;-unification "
            "(&lt;code&gt;emb_amp_exp&lt;/code&gt;) later showed it is the &lt;b&gt;fixed-A_F special case&lt;/b&gt; of "
            "the same physics &amp;minus; use ONE of the two per rig (variable reduction).&lt;/p&gt;"),
        refs=[("&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; fator de conformação de pressão (reescala a assíntota)",
               "&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; pressure conformance factor (rescales the asymptote)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.18 &amp;minus; caso especial de S_rho (a unificação rho o subsome no eixo axial)",
               "&amp;sect;4.18 &amp;minus; special case of S_rho (the rho-unification subsumes it on the axial axis)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="emb_pressure_exp", symbol="n_p", unit="-", group="embedding", category="form",
        # A junta-padrão está a p = 50 kN / 1,0e-4 m² = 5,0e8 Pa, MUITO acima da
        # referência default (1,5e8) — e acima da referência esta lei é inerte
        # por construção (o `min(1, ·)`). Para a página ENSINAR o que o campo
        # faz, a demo sobe a referência a 1,0e9 e põe a junta a p/p_ref = 0,5.
        # Mesmo idioma de `p_ref_emb` (que liga `emb_conform_exp`) e de
        # `s1_freq_exp` (que fixa `s1_freq_ref`).
        context={"baseline": "transverse", "overrides": {"p_ref_emb": 1.0e9}},
        sweep=(0, 3, 13, "lin"), related=["p_ref_emb", "emb_conform_exp", "emb_depth"],
        equation="delta_target *= S_p;   S_p = min(1, (p_init / p_ref_emb)^n_p),   p_init = F0_init / A_contact",
        physics_pt=(
            "&lt;p&gt;É o &lt;b&gt;ramo oposto&lt;/b&gt; do &lt;code&gt;emb_conform_exp&lt;/code&gt;, e as duas coisas "
            "acontecem de verdade numa junta. Aquele diz que apertar forte já gastou aspereza "
            "&amp;minus; sobra menos para o ciclo consumir. Este diz que o achatamento plástico "
            "&lt;b&gt;precisa de pressão para acontecer&lt;/b&gt;: numa junta pouco apertada o escoamento "
            "das asperezas é pequeno, então o reservatório de assentamento é mais &lt;b&gt;raso&lt;/b&gt;. "
            "Um faz a assíntota encolher quando a pressão SOBE; o outro, quando ela CAI.&lt;/p&gt;"
            "&lt;p&gt;Por que isso importa na prática: sem este fator, a perda de encaixe é uma "
            "profundidade quase &lt;b&gt;absoluta&lt;/b&gt;, e a mesma profundidade vira uma fração muito "
            "maior de uma pré-carga pequena. O resultado é o modelo perder pré-carga demais "
            "justamente nos apertos baixos &amp;minus; medido no LU_2024, cuja varredura de torque "
            "mostra o excesso de perda no 1º ciclo indo com 1/F0 a r = +0,995.&lt;/p&gt;"
            "&lt;p&gt;O &lt;code&gt;min(1, &amp;middot;)&lt;/code&gt; não é enfeite: toda junta com pressão acima da "
            "referência fica em S_p = 1 &lt;b&gt;exato&lt;/b&gt;, então ligar a lei numa fonte não mexe, "
            "nem por arredondamento, nas juntas mais apertadas dela. Capability "
            "&lt;b&gt;opt-in, default 0 = OFF&lt;/b&gt; (bit-idêntica quando desligada), per-rig.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This is the &lt;b&gt;opposite branch&lt;/b&gt; of &lt;code&gt;emb_conform_exp&lt;/code&gt;, and both "
            "effects are real in a joint. That one says hard tightening already consumed "
            "asperities, so less is left for cycling. This one says plastic flattening "
            "&lt;b&gt;needs pressure to happen&lt;/b&gt;: in a lightly tightened joint asperity yielding "
            "is small, so the settling reservoir is &lt;b&gt;shallower&lt;/b&gt;. One shrinks the "
            "asymptote when pressure RISES; the other, when it FALLS.&lt;/p&gt;"
            "&lt;p&gt;Why it matters: without this factor the embedding loss is a nearly "
            "&lt;b&gt;absolute&lt;/b&gt; depth, and the same depth is a much larger fraction of a small "
            "preload &amp;minus; so the model over-loses exactly at low tightening torque. "
            "Measured on LU_2024, whose torque sweep shows the excess first-cycle loss "
            "scaling as 1/F0 with r = +0.995.&lt;/p&gt;"
            "&lt;p&gt;The &lt;code&gt;min(1, &amp;middot;)&lt;/code&gt; is load-bearing: any joint above the reference "
            "pressure sits at S_p = 1 &lt;b&gt;exactly&lt;/b&gt;, so enabling the law in a source cannot "
            "disturb its tighter joints even by rounding. Opt-in capability, "
            "&lt;b&gt;default 0 = OFF&lt;/b&gt; (bit-identical when off), per-rig.&lt;/p&gt;"),
        refs=[("&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; fatores que reescalam a assíntota",
               "&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; factors that rescale the asymptote",
               "MODEL_MATH_REFERENCE.md"),
              ("Diagnóstico da fonte: encaixe que não sabe da pré-carga (r = +0,995 contra 1/F0)",
               "Source diagnosis: embedding that ignores preload (r = +0.995 against 1/F0)",
               "New_Theory/lu2024_T10Nm_embedding_sem_pressao_resultado.md")]),

    VarSpec(name="p_ref_emb", symbol="p_ref,emb", unit="Pa", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {"emb_conform_exp": 2.0}},
        sweep=(5e7, 4e8, 15, "log"), related=["emb_conform_exp"],
        equation="S_conf = min(1, (p_ref_emb / p_init)^n_conf),   p_init = F0_init / A_contact",
        physics_pt=(
            "&lt;p&gt;É a &lt;b&gt;pressão de referência&lt;/b&gt; da conformação de embedding: a pressão de "
            "aperto na qual o fator S_conf vale 1. Abaixo dela a junta ainda tem assentamento "
            "residual pleno; acima, o assentamento vai sendo progressivamente pré-consumido "
            "no torque. Fixa &lt;b&gt;onde&lt;/b&gt; fica o joelho de pressão.&lt;/p&gt;"
            "&lt;p&gt;S_conf depende da RAZÃO p_ref_emb/p_init, então subir &lt;code&gt;p_ref_emb&lt;/code&gt; "
            "empurra o fator na direção de 1 (mais embedding residual, queda inicial mais "
            "funda) e baixa-lo encolhe o embedding. Nesta página o companheiro "
            "&lt;code&gt;emb_conform_exp&lt;/code&gt;=2 está ligado para o fator agir; o slider desloca a "
            "pressão em que o reservatório se enche. Um detalhe: esta mesma âncora é "
            "&lt;b&gt;reusada&lt;/b&gt; pelo canal lento (&lt;code&gt;creep_conform_exp&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Só é LIDA se algum expoente de conformação for &amp;gt; 0 (senão inerte). É uma "
            "&lt;b&gt;âncora per-rig&lt;/b&gt;, como &lt;code&gt;emb_depth&lt;/code&gt;; o default de 1.5e8 Pa "
            "(~150 MPa) vale para o rig UFU.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This is the &lt;b&gt;reference pressure&lt;/b&gt; of the embedding conformance: the clamp "
            "pressure at which the factor S_conf equals 1. Below it the joint still has full "
            "residual settling; above it, settling is progressively pre-consumed at torque. "
            "It sets &lt;b&gt;where&lt;/b&gt; the pressure knee sits.&lt;/p&gt;"
            "&lt;p&gt;S_conf depends on the RATIO p_ref_emb/p_init, so raising &lt;code&gt;p_ref_emb&lt;/code&gt; "
            "pushes the factor toward 1 (more residual embedding, deeper initial drop) and "
            "lowering it shrinks embedding. On this page the companion "
            "&lt;code&gt;emb_conform_exp&lt;/code&gt;=2 is enabled so the factor is active; the slider "
            "shifts the pressure at which the reservoir fills. One subtlety: this same anchor "
            "is &lt;b&gt;reused&lt;/b&gt; by the slow channel (&lt;code&gt;creep_conform_exp&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;It is only READ if some conformance exponent is &amp;gt; 0 (inert otherwise). It is "
            "a &lt;b&gt;per-rig anchor&lt;/b&gt;, like &lt;code&gt;emb_depth&lt;/code&gt;; the default of 1.5e8 Pa "
            "(~150 MPa) fits the UFU rig.&lt;/p&gt;"),
        refs=[("&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; âncora de pressão (reusada pelo canal lento)",
               "&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; pressure anchor (reused by the slow channel)",
               "MODEL_MATH_REFERENCE.md"),
              ("Design da conformação dependente de pressão",
               "Pressure-conformation design",
               "specs/2026-07-04-pressure-conformation-design.md")]),

    VarSpec(name="creep_conform_exp", symbol="n_slow", unit="-", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0, 3, 13, "lin"), related=["p_ref_emb", "C_creep"],
        equation="delta_creep *= S_creep;   S_creep = min(1, (p_ref_emb / p_init)^n_slow)",
        physics_pt=(
            "&lt;p&gt;Nesta classe de junta o que o modelo chama de &lt;code&gt;creep&lt;/code&gt; é, na "
            "verdade, &lt;b&gt;assentamento lento log-t da interface&lt;/b&gt; (não creep de bulk). O "
            "torque de aperto pré-conforma também esse reservatório lento, mas com um "
            "expoente de pressão &lt;b&gt;mais fraco&lt;/b&gt; que o do embedding rápido (n_slow~2 vs "
            "n_fast~3&amp;minus;4), porque atinge escalas de aspereza mais profundas.&lt;/p&gt;"
            "&lt;p&gt;Ele multiplica o incremento por-ciclo do &lt;code&gt;CreepLoss&lt;/code&gt; por S_creep, "
            "reusando a âncora &lt;code&gt;p_ref_emb&lt;/code&gt;. No slider: em &lt;code&gt;0&lt;/code&gt; a cauda "
            "lenta fica sem escala (padrão); ao subir n_slow a &lt;b&gt;CAUDA&lt;/b&gt; inclina para "
            "baixo sob pressão de aperto alta. Lido em F0_init (sem realimentação).&lt;/p&gt;"
            "&lt;p&gt;Capability &lt;b&gt;opt-in, default 0 = OFF&lt;/b&gt; (bit-idêntica), &lt;b&gt;per-rig&lt;/b&gt;. "
            "Lido do dado Liu2017: a perda lenta absoluta cai ~F0^&amp;minus;1 (fracional "
            "~F0^&amp;minus;2) &amp;#8658; n_slow~2. NOTA: em rigs onde a perda lenta é creep de BULK "
            "genuíno (gaxetas, alta T) manter 0 &amp;minus; a reinterpretação interface-settlement "
            "é por classe de junta.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;In this joint class what the model calls &lt;code&gt;creep&lt;/code&gt; is really &lt;b&gt;slow "
            "log-t interface settlement&lt;/b&gt; (not bulk creep). The clamp torque pre-conforms "
            "that slow reservoir too, but with a &lt;b&gt;weaker&lt;/b&gt; pressure exponent than the fast "
            "embedding channel (n_slow~2 vs n_fast~3&amp;minus;4), because it reaches deeper "
            "asperity scales.&lt;/p&gt;"
            "&lt;p&gt;It multiplies the per-cycle &lt;code&gt;CreepLoss&lt;/code&gt; increment by S_creep, "
            "reusing the &lt;code&gt;p_ref_emb&lt;/code&gt; anchor. On the slider: at &lt;code&gt;0&lt;/code&gt; the "
            "slow tail is unscaled (standard); raising n_slow tilts the slow &lt;b&gt;TAIL&lt;/b&gt; down "
            "at high clamp pressure. Read on F0_init (no feedback).&lt;/p&gt;"
            "&lt;p&gt;An &lt;b&gt;opt-in capability, default 0 = OFF&lt;/b&gt; (bit-identical), &lt;b&gt;per-rig&lt;/b&gt;. "
            "Read from Liu2017 data: the absolute slow loss falls ~F0^&amp;minus;1 (fractional "
            "~F0^&amp;minus;2) &amp;#8658; n_slow~2. NOTE: in rigs where the slow loss is genuine BULK "
            "creep (gaskets, high T) keep 0 &amp;minus; the interface-settlement reinterpretation "
            "is per joint class.&lt;/p&gt;"),
        refs=[("&amp;sect;4.2 CreepLoss / &amp;sect;6 &amp;minus; conformação do reservatório lento (reusa p_ref_emb)",
               "&amp;sect;4.2 CreepLoss / &amp;sect;6 &amp;minus; slow-reservoir conformance (reuses p_ref_emb)",
               "MODEL_MATH_REFERENCE.md"),
              ("Design do assentamento (canal lento, spec 2026-07-08)",
               "Settling design (slow channel, spec 2026-07-08)",
               "specs/2026-07-08-amplitude-gated-settling-design.md")]),

    VarSpec(name="emb_amp_exp", symbol="q_amp", unit="-", group="embedding", category="form",
        context={"baseline": "axial", "overrides": {}},
        sweep=(0, 4, 13, "lin"), lessons=["L18"], related=["rho_ref_emb"],
        equation="delta_target *= S_rho;   S_rho = min(1, (rho / rho_ref_emb)^q_amp),   rho = F_ax_amp / F0_init",
        physics_pt=(
            "&lt;p&gt;O reservatório de assentamento consumido escala com a &lt;b&gt;amplitude relativa&lt;/b&gt; "
            "&amp;rho; = F_ax_amp/F0 &amp;minus; a amplitude cíclica dividida pela pré-carga. "
            "Amplitude relativa maior significa plasticidade cíclica / shakedown mais intenso "
            "das asperezas, que assentam mais fundo. É o mesmo fenômeno da conformação de "
            "pressão, visto pelo eixo da amplitude.&lt;/p&gt;"
            "&lt;p&gt;Ele multiplica a assíntota de embedding por S_&amp;rho; = min(1, (&amp;rho;/rho_ref)^"
            "q_amp). O baseline aqui é &lt;b&gt;AXIAL&lt;/b&gt; (em transversal F_ax~0 &amp;#8658; S=1, inerte). "
            "No slider: em &lt;code&gt;0&lt;/code&gt; a curva é amplitude-cega (padrão axial); ao subir "
            "q_amp a queda inicial passa a escalar de forma íngreme com a amplitude &amp;minus; o "
            "dado pede q~3.4.&lt;/p&gt;"
            "&lt;p&gt;Capability &lt;b&gt;opt-in, default 0&lt;/b&gt;. Lida dos DOIS sweeps do Liu2017 "
            "(fast-loss ~ &amp;rho;^3.4, R2~0.89, 5 pares, 4 em &amp;plusmn;5%). É uma &lt;b&gt;redução de "
            "variável&lt;/b&gt;: subsome o &lt;code&gt;emb_conform_exp&lt;/code&gt; no eixo axial (usa-se uma das "
            "duas por rig). Lição &lt;code&gt;L18&lt;/code&gt;, &amp;sect;4.18.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The consumed settling reservoir scales with the &lt;b&gt;relative amplitude&lt;/b&gt; "
            "&amp;rho; = F_ax_amp/F0 &amp;minus; the cyclic amplitude divided by the preload. A larger "
            "relative amplitude means more intense cyclic plasticity / shakedown of the "
            "asperities, which bed in deeper. It is the same phenomenon as the pressure "
            "conformance, seen along the amplitude axis.&lt;/p&gt;"
            "&lt;p&gt;It multiplies the embedding asymptote by S_&amp;rho; = min(1, (&amp;rho;/rho_ref)^"
            "q_amp). The baseline here is &lt;b&gt;AXIAL&lt;/b&gt; (in transverse F_ax~0 &amp;#8658; S=1, "
            "inert). On the slider: at &lt;code&gt;0&lt;/code&gt; the curve is amplitude-blind (standard "
            "axial); raising q_amp makes the initial drop scale steeply with amplitude &amp;minus; "
            "the data calls for q~3.4.&lt;/p&gt;"
            "&lt;p&gt;An &lt;b&gt;opt-in capability, default 0&lt;/b&gt;. Read from BOTH Liu2017 sweeps "
            "(fast-loss ~ &amp;rho;^3.4, R2~0.89, 5 pairs, 4 within &amp;plusmn;5%). It is a &lt;b&gt;variable "
            "reduction&lt;/b&gt;: it subsumes &lt;code&gt;emb_conform_exp&lt;/code&gt; on the axial axis (use one "
            "of the two per rig). Lesson &lt;code&gt;L18&lt;/code&gt;, &amp;sect;4.18.&lt;/p&gt;"),
        refs=[("&amp;sect;4.18 MODEL_LEGITIMACY &amp;minus; unificação rho (Liu2017 dois sweeps, R2~0.89)",
               "&amp;sect;4.18 MODEL_LEGITIMACY &amp;minus; rho-unification (Liu2017 two sweeps, R2~0.89)",
               "MODEL_LEGITIMACY.md"),
              ("Design do assentamento gateado por amplitude (rho = A_F/F0)",
               "Amplitude-gated settling design (rho = A_F/F0)",
               "specs/2026-07-08-amplitude-gated-settling-design.md")]),

    VarSpec(name="rho_ref_emb", symbol="rho_ref", unit="-", group="embedding", category="form",
        context={"baseline": "axial", "overrides": {"emb_amp_exp": 3.0}},
        sweep=(0.2, 1.2, 15, "lin"), related=["emb_amp_exp"],
        equation="S_rho = min(1, (rho / rho_ref_emb)^q_amp),   rho = F_ax_amp / F0_init",
        physics_pt=(
            "&lt;p&gt;É a &lt;b&gt;amplitude relativa de referência&lt;/b&gt; da unificação &amp;rho;: o valor de "
            "&amp;rho; = F_ax_amp/F0 no qual o fator de assentamento por amplitude satura em 1. "
            "Define a &lt;b&gt;escala de amplitude&lt;/b&gt; sobre a qual o assentamento extra se "
            "acumula.&lt;/p&gt;"
            "&lt;p&gt;S_&amp;rho; depende de &amp;rho;/rho_ref_emb, então um &lt;code&gt;rho_ref_emb&lt;/code&gt; maior "
            "empurra o fator para baixo (menos assentamento dirigido por amplitude para a "
            "mesma amplitude) e um menor o aumenta. Nesta página o companheiro "
            "&lt;code&gt;emb_amp_exp&lt;/code&gt;=3 está ligado; o slider desloca a amplitude em que o "
            "reservatório se enche &amp;minus; quando rho_ref se iguala ao &amp;rho; do ensaio, S=1 e a "
            "queda inicial é máxima.&lt;/p&gt;"
            "&lt;p&gt;Só é LIDA se &lt;code&gt;emb_amp_exp&lt;/code&gt; &amp;gt; 0 (senão inerte). É uma &lt;b&gt;âncora "
            "per-rig&lt;/b&gt;; o default é 0.667.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This is the &lt;b&gt;reference relative amplitude&lt;/b&gt; of the &amp;rho;-unification: the "
            "value of &amp;rho; = F_ax_amp/F0 at which the amplitude settling factor saturates to "
            "1. It sets the &lt;b&gt;amplitude scale&lt;/b&gt; over which the extra settling "
            "accumulates.&lt;/p&gt;"
            "&lt;p&gt;S_&amp;rho; depends on &amp;rho;/rho_ref_emb, so a larger &lt;code&gt;rho_ref_emb&lt;/code&gt; "
            "pushes the factor down (less amplitude-driven settling for the same amplitude) and "
            "a smaller one raises it. On this page the companion &lt;code&gt;emb_amp_exp&lt;/code&gt;=3 is "
            "enabled; the slider shifts the amplitude at which the reservoir fills &amp;minus; when "
            "rho_ref matches the test &amp;rho;, S=1 and the initial drop is maximal.&lt;/p&gt;"
            "&lt;p&gt;It is only READ if &lt;code&gt;emb_amp_exp&lt;/code&gt; &amp;gt; 0 (inert otherwise). It is a "
            "&lt;b&gt;per-rig anchor&lt;/b&gt;; the default is 0.667.&lt;/p&gt;"),
        refs=[("&amp;sect;4.18 MODEL_LEGITIMACY &amp;minus; âncora rho_ref da unificação rho (per-rig)",
               "&amp;sect;4.18 MODEL_LEGITIMACY &amp;minus; rho_ref anchor of the rho-unification (per-rig)",
               "MODEL_LEGITIMACY.md"),
              ("&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; fator de amplitude do assentamento",
               "&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; settling amplitude factor",
               "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="emb_load_frac", symbol="f_load", unit="-", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0, 1.0, 15, "lin"), lessons=["L19"], related=["emb_depth"],
        equation="delta_target += emb_load_frac * F0_init / k_b   =>   fracao de queda rapida CONSTANTE = emb_load_frac",
        physics_pt=(
            "&lt;p&gt;É um reservatório de assentamento &lt;b&gt;proporcional a carga&lt;/b&gt; de aperto, e não "
            "uma profundidade absoluta fixa. Fisicamente: a profundidade do leito de asperezas "
            "escala com o clamp (o próprio f_Z da VDI cresce com a classe de carga). Com ele, "
            "a queda rápida FRACIONAL fica &lt;b&gt;constante&lt;/b&gt; (= emb_load_frac), independente de "
            "F0.&lt;/p&gt;"
            "&lt;p&gt;Ele soma emb_load_frac&amp;middot;F0_init/k_b a profundidade-alvo, de modo que a "
            "fração de queda inicial é exatamente emb_load_frac (F0-independente). No slider: "
            "em &lt;code&gt;0&lt;/code&gt; a curva-padrão; ao subir, a queda inicial aprofunda como uma "
            "&lt;b&gt;fração fixa&lt;/b&gt; da pré-carga (aqui k_b~6.3e8 N/m, então f_load=0.5 adiciona "
            "~40 &amp;micro;m ao alvo).&lt;/p&gt;"
            "&lt;p&gt;Capability &lt;b&gt;opt-in, default 0 = OFF&lt;/b&gt;. Fecha a falsificação Lu fig20: o "
            "reservatório de profundidade-absoluta preve fração ~1/F0 (1.39&amp;#8594;0.195), mas "
            "o dado é F0-flat (~0.55 num sweep de 7&amp;times; em F0). Mesma família da unificação "
            "&amp;rho; (reservatório &amp;prop; severidade &amp;minus; aqui a severidade é a própria carga "
            "de aperto). Lição &lt;code&gt;L19&lt;/code&gt;, &amp;sect;4.19.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This is a settling reservoir &lt;b&gt;proportional to the clamp load&lt;/b&gt;, not a fixed "
            "absolute depth. Physically: the asperity-bed depth scales with the clamp (VDI's "
            "own f_Z grows with the load class). With it, the fast FRACTIONAL drop stays "
            "&lt;b&gt;constant&lt;/b&gt; (= emb_load_frac), independent of F0.&lt;/p&gt;"
            "&lt;p&gt;It adds emb_load_frac&amp;middot;F0_init/k_b to the target depth, so the initial "
            "drop fraction is exactly emb_load_frac (F0-independent). On the slider: at "
            "&lt;code&gt;0&lt;/code&gt; the standard curve; raising it deepens the initial drop as a "
            "&lt;b&gt;fixed fraction&lt;/b&gt; of preload (here k_b~6.3e8 N/m, so f_load=0.5 adds ~40 "
            "&amp;micro;m to the target).&lt;/p&gt;"
            "&lt;p&gt;An &lt;b&gt;opt-in capability, default 0 = OFF&lt;/b&gt;. It closes the Lu fig20 "
            "falsification: the absolute-depth reservoir predicts fraction ~1/F0 "
            "(1.39&amp;#8594;0.195), but the data is F0-flat (~0.55 over a 7&amp;times; F0 sweep). Same "
            "family as the &amp;rho;-unification (reservoir &amp;prop; severity &amp;minus; here the "
            "severity is the clamp load itself). Lesson &lt;code&gt;L19&lt;/code&gt;, &amp;sect;4.19.&lt;/p&gt;"),
        refs=[("&amp;sect;4.19 MODEL_LEGITIMACY &amp;minus; assentamento proporcional a carga (fecha a falsificação Lu fig20)",
               "&amp;sect;4.19 MODEL_LEGITIMACY &amp;minus; load-proportional settling (closes the Lu fig20 falsification)",
               "MODEL_LEGITIMACY.md"),
              ("&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; termo proporcional a carga no delta_target",
               "&amp;sect;4.1 / &amp;sect;6 EmbeddingLoss &amp;minus; load-proportional term in delta_target",
               "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="s1_amp_gate_dref", symbol="delta*_S1", unit="m", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0.0002, 0.001, 13, "lin"), related=["s1_amp_gate_p", "s1_amp_gate_floor"],
        equation="g = floor + (1-floor) * d^p / (d^p + dref^p);  d_delta(emb, creep) *= g   (dref=0 -> OFF exato)",
        physics_pt=(
            "&lt;p&gt;Amplitude de &lt;b&gt;transição de regime&lt;/b&gt; dos relógios de estágio I "
            "(PR-3 2026-08-01, forma B do N&lt;sub&gt;95&lt;/sub&gt; do LIU_2025): abaixo de "
            "&lt;code&gt;dref&lt;/code&gt; os relógios de bedding E creep-de-interface quase param "
            "(assentamento vibração-dirigido exige escorregamento macro); acima, taxa plena. "
            "O gate Hill multiplica SÓ o incremento d&amp;delta; dos dois mecanismos — dF&lt;sub&gt;0&lt;/sub&gt; "
            "e dE derivam dele, então a conservação fica intacta.&lt;/p&gt;"
            "&lt;p&gt;Motivação medida: o N&lt;sub&gt;95&lt;/sub&gt; do modelo era CONSTANTE (~108 ciclos) onde "
            "o dado da Fig. 4 do Liu 2025 varre 850&amp;times; (16.157 &amp;rarr; 19) — relógio cego à "
            "amplitude; o dado exige expoente efetivo ~11, e o candidato com campos existentes "
            "foi falsificado no G1 (1/6). No slider: dref abaixo da amplitude do baseline "
            "deixa o gate ~1 (nada muda); dref acima dela suprime o estágio I.&lt;/p&gt;"
            "&lt;p&gt;Capability &lt;b&gt;opt-in, default 0 = OFF&lt;/b&gt; (bit-idêntica; "
            "modo força também inerte). Prereg specs/2026-08-01-s1-amp-gate-pr3.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;b&gt;Regime-transition&lt;/b&gt; amplitude of the stage-I clocks (PR-3 2026-08-01, "
            "form B of the LIU_2025 N&lt;sub&gt;95&lt;/sub&gt;): below &lt;code&gt;dref&lt;/code&gt; the bedding AND "
            "interface-creep clocks nearly stop (vibration-driven settlement requires macro slip); "
            "above it, full rate. The Hill gate multiplies ONLY the d&amp;delta; increment of the two "
            "mechanisms — dF&lt;sub&gt;0&lt;/sub&gt; and dE derive from it, so conservation is preserved.&lt;/p&gt;"
            "&lt;p&gt;Measured motivation: the model N&lt;sub&gt;95&lt;/sub&gt; was CONSTANT (~108 cycles) where "
            "the Liu 2025 Fig. 4 data spans 850&amp;times; — an amplitude-blind clock; the data demands "
            "an effective exponent of ~11 and the existing-fields candidate was falsified at G1 (1/6). "
            "On the slider: dref below the baseline amplitude leaves the gate ~1; above it, stage I "
            "is suppressed.&lt;/p&gt;"
            "&lt;p&gt;Capability &lt;b&gt;opt-in, default 0 = OFF&lt;/b&gt; (bit-identical; force mode also inert).&lt;/p&gt;"),
    ),
    VarSpec(name="s1_amp_gate_p", symbol="p_S1", unit="-", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {"s1_amp_gate_dref": 0.00055, "s1_amp_gate_floor": 0.01}},
        sweep=(2, 16, 15, "lin"), related=["s1_amp_gate_dref", "s1_amp_gate_floor"],
        equation="g = floor + (1-floor) * d^p / (d^p + dref^p)   (so lido se s1_amp_gate_dref > 0)",
        physics_pt=(
            "&lt;p&gt;&lt;b&gt;Nitidez&lt;/b&gt; da transição de regime do gate de estágio I: p pequeno faz a "
            "supressão crescer suavemente com a amplitude; p grande vira um degrau em "
            "&lt;code&gt;dref&lt;/code&gt;. É o número que carrega a exigência do dado do Liu 2025 "
            "(expoente efetivo ~11 do N&lt;sub&gt;95&lt;/sub&gt; sobre a amplitude — nenhum campo "
            "pré-existente alcança; medido no prereg do PR-3).&lt;/p&gt;"
            "&lt;p&gt;Só é lido quando &lt;code&gt;s1_amp_gate_dref&lt;/code&gt; &amp;gt; 0 (aqui o companheiro "
            "está ligado em 0,55 mm, com floor 0,01, para o efeito aparecer). No slider: com o "
            "baseline perto de dref, subir p muda pouco EM dref (g(dref)=meio caminho por "
            "construção) mas afia as duas pontas.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;b&gt;Sharpness&lt;/b&gt; of the stage-I regime transition: small p makes suppression "
            "grow smoothly with amplitude; large p turns it into a step at &lt;code&gt;dref&lt;/code&gt;. "
            "This number carries the Liu 2025 data requirement (effective N&lt;sub&gt;95&lt;/sub&gt;-vs-amplitude "
            "exponent ~11 — no pre-existing field reaches it; measured in the PR-3 prereg).&lt;/p&gt;"
            "&lt;p&gt;Only read when &lt;code&gt;s1_amp_gate_dref&lt;/code&gt; &amp;gt; 0 (companion enabled here at "
            "0.55 mm with floor 0.01 so the effect is visible).&lt;/p&gt;"),
    ),
    VarSpec(name="s1_amp_gate_floor", symbol="g_min_S1", unit="-", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {"s1_amp_gate_dref": 0.0009, "s1_amp_gate_p": 8.0}},
        sweep=(0.0, 0.3, 13, "lin"), related=["s1_amp_gate_dref", "s1_amp_gate_p"],
        equation="g = floor + (1-floor) * d^p / (d^p + dref^p)   (so lido se s1_amp_gate_dref > 0)",
        physics_pt=(
            "&lt;p&gt;&lt;b&gt;Taxa remanescente sub-limiar&lt;/b&gt; do gate de estágio I: mesmo sem "
            "escorregamento macro, bedding e creep de interface não param DE TODO — sobra uma "
            "fração &lt;code&gt;floor&lt;/code&gt; da taxa plena. É o que deixa o fundo da curva "
            "N&lt;sub&gt;95&lt;/sub&gt;-vs-amplitude PLANO (no Liu 2025, 0,25 e 0,30 mm têm N&lt;sub&gt;95&lt;/sub&gt; "
            "quase iguais — os dois estão no floor), enquanto o Hill domina o meio.&lt;/p&gt;"
            "&lt;p&gt;Só é lido quando &lt;code&gt;s1_amp_gate_dref&lt;/code&gt; &amp;gt; 0 (aqui 0,9 mm — acima da "
            "amplitude do baseline, então o baseline está sub-limiar e o floor é A alavanca "
            "visível). No slider: floor 0 congela o estágio I sub-limiar; subir o floor devolve "
            "assentamento ao platô.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;b&gt;Sub-threshold residual rate&lt;/b&gt; of the stage-I gate: even without macro slip, "
            "bedding and interface creep do not FULLY stop — a fraction &lt;code&gt;floor&lt;/code&gt; of the "
            "full rate remains. It is what keeps the bottom of the N&lt;sub&gt;95&lt;/sub&gt;-vs-amplitude curve "
            "FLAT (in Liu 2025, 0.25 and 0.30 mm have nearly equal N&lt;sub&gt;95&lt;/sub&gt; — both sit on the "
            "floor) while the Hill term rules the middle.&lt;/p&gt;"
            "&lt;p&gt;Only read when &lt;code&gt;s1_amp_gate_dref&lt;/code&gt; &amp;gt; 0 (here 0.9 mm — above the "
            "baseline amplitude, so the baseline is sub-threshold and the floor is THE visible "
            "lever).&lt;/p&gt;"),
    ),
    VarSpec(name="s1_freq_exp", symbol="n_f,S1", unit="-", group="embedding",
        category="form", context={"baseline": "transverse",
                                  "overrides": {"s1_freq_ref": 5.0}},
        sweep=(0.0, 2.0, 11, "lin"),
        related=["s1_freq_ref", "fret_freq_exp", "N_emb"],
        equation="target(emb) *= (s1_freq_ref/freq)^s1_freq_exp   (exp=0 -> 1.0 exato, OFF)",
        physics_pt=('&lt;p&gt;&lt;b&gt;Expoente de frequencia do relogio de estagio I&lt;/b&gt; (P-9, assinada 2026-08-09). Se o assentamento tem componente dependente do TEMPO (consolidacao de asperezas), o mesmo numero de ciclos a 10 Hz dispoe de METADE do tempo de 5 Hz — e consolida MENOS. O fator entra no ALVO do embedding, nao no incremento.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Por que no alvo:&lt;/b&gt; o gate de amplitude irmao esta no incremento de proposito (sub-limiar o assentamento fica lento, nao menor). Para frequencia o argumento INVERTE. E foi medido: com N_emb=50 e curvas de 5300 ciclos (106x), gatear o incremento e um NO-OP — a fracao do alvo atingida e 1,0000 com e sem gate.&lt;/p&gt;&lt;p&gt;A lei e a mesma que o D-V assinou para o fretting de flanco (fret_freq_exp=1, taxa ~1/f), TRANSFERIDA — zero numeros fitados. So e identificavel onde a fonte VARRE frequencia: em fonte mono-frequencia ele e inseparavel de N_emb.&lt;/p&gt;'),
        physics_en=('&lt;p&gt;&lt;b&gt;Frequency exponent of the stage-I clock&lt;/b&gt; (P-9, signed 2026-08-09). If settling has a TIME-dependent component, the same cycle count at 10 Hz has half the time of 5 Hz and consolidates LESS. The factor multiplies the embedding TARGET, not the increment — gating the increment of a saturated channel is a measured no-op (N_emb=50 vs 5300 cycles).&lt;/p&gt;&lt;p&gt;Same law the D-V signed for flank fretting, transferred; zero fitted numbers. Only identifiable where the source SWEEPS frequency.&lt;/p&gt;'),
    ),
    VarSpec(name="s1_freq_ref", symbol="f_ref,S1", unit="Hz", group="embedding",
        category="form", context={"baseline": "transverse",
                                  "overrides": {"s1_freq_exp": 1.0}},
        sweep=(2.0, 20.0, 10, "lin"), related=["s1_freq_exp", "f_ref_fret"],
        equation="target(emb) *= (s1_freq_ref/freq)^s1_freq_exp   (em f=f_ref o fator e 1 exato)",
        physics_pt=('&lt;p&gt;&lt;b&gt;Frequencia de referencia&lt;/b&gt; do gate de estagio I: e a frequencia em que emb_depth foi calibrado. Em f = f_ref o fator vale 1,0 EXATO, entao as curvas dessa frequencia ficam BIT-IDENTICAS — a inercia e por construcao, nao por sorte.&lt;/p&gt;&lt;p&gt;E INPUT, nao parametro fitado: no YANG_2019 vale 5 Hz porque 4 das 5 curvas da fonte rodam a 5 Hz. Escolher f_ref errado moveria justamente as curvas que deveriam servir de controle.&lt;/p&gt;'),
        physics_en=('&lt;p&gt;&lt;b&gt;Reference frequency&lt;/b&gt; of the stage-I gate — the frequency at which emb_depth was calibrated. At f = f_ref the factor is exactly 1.0, so curves at that frequency stay BIT-IDENTICAL: inertia by construction. It is an INPUT, not a fitted parameter.&lt;/p&gt;'),
    ),
    VarSpec(name="emb_slip_gate", symbol="q_bed", unit="-", group="embedding", category="form",
        context={"baseline": "transverse", "overrides": {"emb_load_frac": 0.3}},
        sweep=(0, 4, 13, "lin"), related=["emb_load_frac"],
        equation="g_slip = (slip / (slip + delta_t))^q_bed;   delta_target += emb_load_frac * g_slip * F0_init / k_b",
        physics_pt=(
            "&lt;p&gt;Torna o reservatório de assentamento &lt;b&gt;proporcional a carga&lt;/b&gt; "
            "(&lt;code&gt;emb_load_frac&lt;/code&gt;) dependente do &lt;b&gt;escorregamento&lt;/b&gt; cíclico: é um "
            "assentamento dirigido por vibração (ratcheting), não puramente estático. Abaixo "
            "de um limiar de slip só a profundidade estática assenta; ciclos de escorregamento "
            "destravam o reservatório extra proporcional a carga.&lt;/p&gt;"
            "&lt;p&gt;Ele gateia emb_load_frac por g_slip = (slip/(slip+&amp;delta;t))^q_bed, com "
            "&amp;delta;t a capacidade de micro-slip. Nesta página o companheiro "
            "&lt;code&gt;emb_load_frac&lt;/code&gt;=0.3 está ligado (há um reservatório a gatear). No "
            "slider: em &lt;code&gt;0&lt;/code&gt; o gate vale 1 (reservatório de carga sempre pleno); ao "
            "subir q_bed a exigência de slip fica mais íngreme (menos assentamento com pouco "
            "escorregamento). Exige o slip do modo deslocamento.&lt;/p&gt;"
            "&lt;p&gt;Capability &lt;b&gt;opt-in, default 0 = OFF&lt;/b&gt; (bit-idêntica). Proveniência dupla: "
            "a porca COLADA de Jiang isola o bedding como ratcheting sob ciclos de "
            "escorregamento; o trade frac&amp;#8596;amplitude da &amp;sect;4.19 apontava o mesmo. "
            "&amp;sect;4.29.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;It makes the &lt;b&gt;load-proportional&lt;/b&gt; settling reservoir "
            "(&lt;code&gt;emb_load_frac&lt;/code&gt;) depend on cyclic &lt;b&gt;slip&lt;/b&gt;: it is a "
            "vibration-driven (ratcheting) settlement, not a purely static one. Below a slip "
            "threshold only the static depth beds; slip cycles unlock the extra "
            "load-proportional reservoir.&lt;/p&gt;"
            "&lt;p&gt;It gates emb_load_frac by g_slip = (slip/(slip+&amp;delta;t))^q_bed, with &amp;delta;t "
            "the micro-slip capacity. On this page the companion &lt;code&gt;emb_load_frac&lt;/code&gt;=0.3 "
            "is enabled (there is a reservoir to gate). On the slider: at &lt;code&gt;0&lt;/code&gt; the "
            "gate is 1 (load reservoir always fully available); raising q_bed sharpens the slip "
            "requirement (less settling at small slip). It requires the displacement-mode "
            "slip.&lt;/p&gt;"
            "&lt;p&gt;An &lt;b&gt;opt-in capability, default 0 = OFF&lt;/b&gt; (bit-identical). Double provenance: "
            "Jiang's GLUED nut isolates bedding as ratcheting under slip cycles; the "
            "frac&amp;#8596;amplitude trade of &amp;sect;4.19 pointed to the same. &amp;sect;4.29.&lt;/p&gt;"),
        refs=[("&amp;sect;4.1 EmbeddingLoss &amp;minus; bedding gateado por slip (gate sobre o reservatório fracional)",
               "&amp;sect;4.1 EmbeddingLoss &amp;minus; slip-gated bedding (gate on the fractional reservoir)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.29 MODEL_LEGITIMACY &amp;minus; porca colada de Jiang isola o bedding como ratcheting",
               "&amp;sect;4.29 MODEL_LEGITIMACY &amp;minus; Jiang glued-nut isolates bedding as ratcheting",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="t_0", symbol="t_0", unit="s", group="creep", category="form",
        context={"baseline": "creep", "overrides": {}},
        sweep=(0.1, 100, 15, "log"), related=["C_creep"],
        equation="delta_creep(t) = C_creep * F_0 * log(t/t_0 + 1)",
        physics_pt=(
            "&lt;p&gt;É o &lt;b&gt;tempo de referência&lt;/b&gt; que fixa a origem do relógio logarítmico do "
            "creep. O creep log-t não tem zero natural (log(0) diverge); t_0 regulariza a "
            "expressão e determina quanto do assentamento lento acontece nos primeiros "
            "segundos versus ao longo de horas/décadas.&lt;/p&gt;"
            "&lt;p&gt;Ele aparece dentro do log, como t/t_0 + 1 (no código, log(t+t_0)). Um t_0 "
            "maior &lt;b&gt;atrasa e achata&lt;/b&gt; o creep inicial (o argumento do log fica perto de 1 "
            "por mais tempo); um t_0 menor antecipa a cauda lenta. O baseline aqui é de "
            "&lt;b&gt;creep&lt;/b&gt; (freq = 1/60 Hz, de modo que ciclo/freq dá segundos reais); o slider "
            "remodela a rapidez com que a cauda lenta se desenvolve.&lt;/p&gt;"
            "&lt;p&gt;Default 1.0 s. Trabalha em par com &lt;code&gt;C_creep&lt;/code&gt;: t_0 ajusta o "
            "&lt;b&gt;relógio&lt;/b&gt;, C_creep ajusta a &lt;b&gt;inclinação&lt;/b&gt; da cauda &amp;minus; juntos são "
            "por par tribológico.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This is the &lt;b&gt;reference time&lt;/b&gt; that fixes the origin of the logarithmic "
            "creep clock. Log-t creep has no natural zero (log(0) diverges); t_0 regularizes "
            "the expression and sets how much of the slow settling happens in the first seconds "
            "versus over hours/decades.&lt;/p&gt;"
            "&lt;p&gt;It appears inside the log, as t/t_0 + 1 (in code, log(t+t_0)). A larger t_0 "
            "&lt;b&gt;delays and flattens&lt;/b&gt; the early creep (the log argument stays near 1 longer); "
            "a smaller t_0 front-loads the slow tail. The baseline here is a &lt;b&gt;creep&lt;/b&gt; one "
            "(freq = 1/60 Hz, so cycle/freq gives real seconds); the slider reshapes how quickly "
            "the slow tail develops.&lt;/p&gt;"
            "&lt;p&gt;Default 1.0 s. It works as a pair with &lt;code&gt;C_creep&lt;/code&gt;: t_0 sets the "
            "&lt;b&gt;clock&lt;/b&gt;, C_creep sets the &lt;b&gt;slope&lt;/b&gt; of the tail &amp;minus; together they are "
            "per tribological pair.&lt;/p&gt;"),
        refs=[("&amp;sect;4.2 CreepLoss &amp;minus; Norton-Bailey logarítmico, tempo de referência do log",
               "&amp;sect;4.2 CreepLoss &amp;minus; logarithmic Norton-Bailey, reference time of the log",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.7 MODEL_LEGITIMACY &amp;minus; canal de creep por par tribológico",
               "&amp;sect;4.7 MODEL_LEGITIMACY &amp;minus; creep channel is per tribological pair",
               "MODEL_LEGITIMACY.md")]),
])

# =============================== WEAR + STIFFNESS + FRICTION + AXIAL FRETTING (11) ===============================
VARIABLE_SPECS.extend([
    VarSpec(
        name="K_archard", symbol="K", unit="-", group="wear", category="physical",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(1e-5, 1e-3, 15, "log"), related=["hardness", "k_wear_spec"],
        equation="d_wear = K_archard * F_0 * (4*slip) / (hardness * A_contact);   dF_0 = -k_b * d_wear",
        physics_pt=(
            "&lt;p&gt;O coeficiente de Archard &lt;code&gt;K&lt;/code&gt; é a probabilidade adimensional "
            "de que um encontro entre asperezas gere uma partícula de desgaste. É o "
            "parâmetro clássico da lei de Archard: multiplicado pela carga normal e "
            "pela distância deslizada e dividido pela dureza, dá o volume de material "
            "removido. Para aço com lubrificação de contorno vale ~1e-4; 1e-3 já é "
            "desgaste de fretting severo.&lt;/p&gt;"
            "&lt;p&gt;No modelo ele entra na WearLoss (face de bearing): d_wear = "
            "K&amp;middot;F_0&amp;middot;(4&amp;middot;slip)/(H&amp;middot;A_contact), e a remoção vira "
            "perda de aperto por &amp;Delta;F_0 = &amp;minus;k_b&amp;middot;d_wear. Em modo de "
            "deslocamento o wear DOMINA a perda de pré-carga (dirigido por K, não pelo "
            "atrito), então subir &lt;code&gt;K&lt;/code&gt; aprofunda a queda no trecho médio/tardio "
            "da curva. O slider mostra isso diretamente: mais K = decaimento mais "
            "íngreme.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: K aparece SEMPRE junto com a dureza H, e SÓ como a razão "
            "K/H &amp;minus; dobrar os dois não muda nada bit-a-bit (não-identificáveis em "
            "separado, merge &amp;sect;4.42a). Por isso o parâmetro canônico é "
            "&lt;code&gt;k_wear_spec&lt;/code&gt; = K/H [1/Pa]; a razão é por par tribológico, não "
            "universal. O default 1e-4 é valor de literatura para aço lubrificado de "
            "contorno.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The Archard coefficient &lt;code&gt;K&lt;/code&gt; is the dimensionless probability "
            "that an asperity encounter produces a wear particle. It is the classic "
            "parameter of Archard's law: multiplied by the normal load and the sliding "
            "distance and divided by hardness, it gives the removed material volume. For "
            "boundary-lubricated steel it is ~1e-4; 1e-3 is already severe fretting "
            "wear.&lt;/p&gt;"
            "&lt;p&gt;In the model it enters WearLoss (bearing face): d_wear = "
            "K&amp;middot;F_0&amp;middot;(4&amp;middot;slip)/(H&amp;middot;A_contact), and the removal "
            "becomes a preload loss via &amp;Delta;F_0 = &amp;minus;k_b&amp;middot;d_wear. In "
            "displacement mode wear DOMINATES the preload loss (driven by K, not by "
            "friction), so raising &lt;code&gt;K&lt;/code&gt; deepens the drop in the mid/late part "
            "of the curve. The slider shows it directly: more K = steeper decay.&lt;/p&gt;"
            "&lt;p&gt;Provenance: K ALWAYS appears together with the hardness H, and ONLY as "
            "the ratio K/H &amp;minus; doubling both changes nothing bit-for-bit (not separately "
            "identifiable, merge &amp;sect;4.42a). That is why the canonical parameter is "
            "&lt;code&gt;k_wear_spec&lt;/code&gt; = K/H [1/Pa]; the ratio is per tribological pair, "
            "not universal. The 1e-4 default is a literature value for boundary-"
            "lubricated steel.&lt;/p&gt;"),
        refs=[("&amp;sect;4.3 WearLoss &amp;minus; Archard (d_wear = K&amp;middot;F&amp;middot;s/(H&amp;middot;A))",
               "&amp;sect;4.3 WearLoss &amp;minus; Archard (d_wear = K&amp;middot;F&amp;middot;s/(H&amp;middot;A))",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.42a &amp;minus; K e H só aparecem como razão K/H (não-identificáveis)",
               "&amp;sect;4.42a &amp;minus; K and H appear only as the ratio K/H (non-identifiable)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="hardness", symbol="H", unit="Pa", group="wear", category="physical",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(1e9, 4e9, 15, "log"), related=["K_archard", "k_wear_spec"],
        equation="d_wear = K_archard * F_0 * (4*slip) / (hardness * A_contact);   dF_0 = -k_b * d_wear",
        physics_pt=(
            "&lt;p&gt;A dureza &lt;code&gt;H&lt;/code&gt; (Pa) é a resistência do material mais mole do "
            "contato (a face de bearing) ao escoamento plástico. Na mecânica de Archard, "
            "material mais duro forma menos área real de contato sob a mesma carga e "
            "portanto remove menos material por ciclo &amp;minus; a dureza está no DENOMINADOR do "
            "desgaste.&lt;/p&gt;"
            "&lt;p&gt;Entra na WearLoss como d_wear = K&amp;middot;F_0&amp;middot;(4&amp;middot;slip)/"
            "(H&amp;middot;A_contact): subir &lt;code&gt;H&lt;/code&gt; reduz d_wear e deixa a curva mais "
            "rasa; é o inverso exato de &lt;code&gt;K&lt;/code&gt;. Em modo de deslocamento, onde o "
            "wear domina a perda, o slider de H atua com força, porém em sentido oposto "
            "ao de K.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: H só aparece como a razão K/H no engine (WearLoss E "
            "ThreadFrettingLoss) &amp;minus; subir H é bit-a-bit idêntico a baixar K pelo mesmo "
            "fator, então H NÃO é identificável separadamente de K (merge &amp;sect;4.42a). O "
            "parâmetro canônico é &lt;code&gt;k_wear_spec&lt;/code&gt; = K/H. O default 2e9 Pa é "
            "dureza de aço típico.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The hardness &lt;code&gt;H&lt;/code&gt; (Pa) is the resistance of the softer contact "
            "material (the bearing face) to plastic yielding. In Archard mechanics a "
            "harder material forms less real contact area under the same load and thus "
            "removes less material per cycle &amp;minus; hardness sits in the DENOMINATOR of "
            "wear.&lt;/p&gt;"
            "&lt;p&gt;It enters WearLoss as d_wear = K&amp;middot;F_0&amp;middot;(4&amp;middot;slip)/"
            "(H&amp;middot;A_contact): raising &lt;code&gt;H&lt;/code&gt; lowers d_wear and flattens the "
            "curve; it is the exact inverse of &lt;code&gt;K&lt;/code&gt;. In displacement mode, "
            "where wear dominates the loss, the H slider acts strongly but in the "
            "opposite direction to K.&lt;/p&gt;"
            "&lt;p&gt;Provenance: H appears only as the ratio K/H in the engine (WearLoss AND "
            "ThreadFrettingLoss) &amp;minus; raising H is bit-for-bit identical to lowering K by "
            "the same factor, so H is NOT separately identifiable from K (merge "
            "&amp;sect;4.42a). The canonical parameter is &lt;code&gt;k_wear_spec&lt;/code&gt; = K/H. The "
            "2e9 Pa default is a typical steel hardness.&lt;/p&gt;"),
        refs=[("&amp;sect;4.3 WearLoss &amp;minus; H no denominador de Archard",
               "&amp;sect;4.3 WearLoss &amp;minus; H in the Archard denominator",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.42a &amp;minus; (2K,2H) equivalente a (K,H): H não-identificável separado de K",
               "&amp;sect;4.42a &amp;minus; (2K,2H) equals (K,H): H not identifiable apart from K",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="k_wear_spec", symbol="k_wear", unit="1/Pa", group="wear", category="physical",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0, 5e-13, 15, "lin"), related=["K_archard", "hardness"],
        equation="d_wear = k_wear_spec * F_0 * (4*slip) / A_contact   [k_wear_spec>0];   = K_archard*F_0*(4*slip)/(hardness*A_contact)   [=0, legado]",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;k_wear_spec&lt;/code&gt; é a razão de desgaste específica K/H [1/Pa] &amp;minus; "
            "a ÚNICA combinação de K e da dureza que o dado consegue restringir. Como "
            "Archard só usa K e H através da razão K/H, colapsar os dois num único número "
            "é a forma honesta de parametrizar o desgaste (merge &amp;sect;4.42a, "
            "2026-07-09).&lt;/p&gt;"
            "&lt;p&gt;Quando &lt;code&gt;k_wear_spec&lt;/code&gt; &amp;gt; 0 ele SOBREPÕE o caminho legado K/H "
            "nos DOIS mecanismos de desgaste (WearLoss no bearing e ThreadFrettingLoss no "
            "flanco): d_wear = k_wear_spec&amp;middot;F_0&amp;middot;(4&amp;middot;slip)/A_contact. "
            "Quando = 0 (default) usa K_archard/hardness com a aritmética ORIGINAL "
            "(bit-a-bit idêntico, backward-compat). O slider parte de 0 (via legada, "
            "K/H = 5e-14) e, subindo, aprofunda o decaimento por wear.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: é o parâmetro CANÔNICO do desgaste; o bloco 'shared' "
            "canônico usa 5e-14 (= 1e-4/2e9, migrado 2026-07-09). K/H é por par "
            "tribológico &amp;minus; a magnitude segue per-rig até ter procedência por par completa "
            "(dívida declarada &amp;sect;4.42c).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;k_wear_spec&lt;/code&gt; is the specific wear ratio K/H [1/Pa] &amp;minus; the "
            "ONLY combination of K and hardness that the data can constrain. Since "
            "Archard uses K and H only through the ratio K/H, collapsing the two into a "
            "single number is the honest way to parametrize wear (merge &amp;sect;4.42a, "
            "2026-07-09).&lt;/p&gt;"
            "&lt;p&gt;When &lt;code&gt;k_wear_spec&lt;/code&gt; &amp;gt; 0 it OVERRIDES the legacy K/H path in "
            "BOTH wear mechanisms (WearLoss at the bearing and ThreadFrettingLoss at the "
            "flank): d_wear = k_wear_spec&amp;middot;F_0&amp;middot;(4&amp;middot;slip)/A_contact. "
            "When = 0 (default) it uses K_archard/hardness with the ORIGINAL arithmetic "
            "(bit-for-bit identical, backward-compat). The slider starts at 0 (legacy "
            "path, K/H = 5e-14) and, as it rises, deepens the wear-driven decay.&lt;/p&gt;"
            "&lt;p&gt;Provenance: it is the CANONICAL wear parameter; the canonical 'shared' "
            "block uses 5e-14 (= 1e-4/2e9, migrated 2026-07-09). K/H is per tribological "
            "pair &amp;minus; its magnitude remains per-rig until it has full per-pair provenance "
            "(a declared debt, &amp;sect;4.42c).&lt;/p&gt;"),
        refs=[("&amp;sect;4.3 + &amp;sect;4.42a &amp;minus; k_wear_spec = K/H [1/Pa] canônico",
               "&amp;sect;4.3 + &amp;sect;4.42a &amp;minus; k_wear_spec = K/H [1/Pa] canonical",
               "MODEL_MATH_REFERENCE.md"),
              ("bloco 'shared' canônico usa 5e-14 (= 1e-4/2e9, migrado 2026-07-09)",
               "canonical 'shared' block uses 5e-14 (= 1e-4/2e9, migrated 2026-07-09)",
               "joint_calibrations.json")]),

    VarSpec(
        name="k_wear_running", symbol="k_run", unit="-", group="wear", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(1.0, 5.0, 14, "lin"), related=["N_wear_run"],
        equation="K_eff = K * (1 + (k_run - 1) * exp(-N / N_run));   k_run <= 1  =>  OFF (K_eff = K)",
        physics_pt=(
            "&lt;p&gt;Superfícies novas desgastam mais rápido no início (running-in / "
            "amaciamento): os picos de aspereza mais altos são removidos primeiro, e só "
            "depois o desgaste assenta num regime estacionário. O desgaste medido é "
            "sublinear no número de ciclos (~N^0.53, Zhang 2019), não linear.&lt;/p&gt;"
            "&lt;p&gt;O &lt;code&gt;k_wear_running&lt;/code&gt; é o multiplicador do coeficiente de wear em "
            "N=0: K_eff = K&amp;middot;(1 + (k_run&amp;minus;1)&amp;middot;e^(&amp;minus;N/N_run)), "
            "decaindo para K com constante de ciclos &lt;code&gt;N_wear_run&lt;/code&gt;. Subir k_run "
            "realça o desgaste inicial (queda mais íngreme cedo, que depois relaxa para a "
            "taxa estacionária). k_run &amp;le; 1 = DESLIGADO (K_eff = K exato, "
            "bit-a-bit).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: forma opt-in, default 1.0 (inerte). Nomeada pela "
            "sublinearidade medida do wear (Zhang 2019) e pelo par K_running_in/K_steady "
            "do V1. Ligar NÃO é fitar um tuner &amp;minus; é suprir o transiente de amaciamento que "
            "o dado mostra.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Fresh surfaces wear faster at the start (running-in / break-in): the "
            "tallest asperity peaks are removed first, and only then does wear settle "
            "into a steady regime. Measured wear is sublinear in cycle count (~N^0.53, "
            "Zhang 2019), not linear.&lt;/p&gt;"
            "&lt;p&gt;The &lt;code&gt;k_wear_running&lt;/code&gt; is the multiplier on the wear coefficient "
            "at N=0: K_eff = K&amp;middot;(1 + (k_run&amp;minus;1)&amp;middot;e^(&amp;minus;N/N_run)), "
            "decaying to K with the cycle constant &lt;code&gt;N_wear_run&lt;/code&gt;. Raising k_run "
            "boosts the early wear (a steeper early drop that then relaxes to the steady "
            "rate). k_run &amp;le; 1 = OFF (K_eff = K exactly, bit-for-bit).&lt;/p&gt;"
            "&lt;p&gt;Provenance: opt-in form, default 1.0 (inert). Named after the measured "
            "sublinearity of wear (Zhang 2019) and the V1 K_running_in/K_steady pair. "
            "Turning it on is NOT fitting a tuner &amp;minus; it supplies the break-in transient "
            "that the data shows.&lt;/p&gt;"),
        refs=[("&amp;sect;4.3 running-in &amp;minus; K_eff = K&amp;middot;(1+(k_run&amp;minus;1)e^{&amp;minus;N/N_run})",
               "&amp;sect;4.3 running-in &amp;minus; K_eff = K&amp;middot;(1+(k_run&amp;minus;1)e^{&amp;minus;N/N_run})",
               "MODEL_MATH_REFERENCE.md"),
              ("Zhang et al. (2019) &amp;minus; wear sublinear ~N^0.53 (running-in)",
               "Zhang et al. (2019) &amp;minus; sublinear wear ~N^0.53 (running-in)",
               "Zhang2019")]),

    VarSpec(
        name="N_wear_run", symbol="N_run", unit="ciclos", group="wear", category="form",
        context={"baseline": "transverse", "overrides": {"k_wear_running": 3.0}},
        sweep=(10, 1000, 15, "log"), related=["k_wear_running"],
        equation="K_eff = K * (1 + (k_run - 1) * exp(-N / N_run))   (so lido se k_wear_running > 1)",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;N_wear_run&lt;/code&gt; é a constante de tempo (em ciclos) do "
            "amaciamento: quantos ciclos o desgaste elevado do running-in dura antes de "
            "assentar na taxa estacionária. É o companheiro de &lt;code&gt;k_wear_running&lt;/code&gt; "
            "&amp;minus; um diz QUANTO mais rápido, o outro por QUANTO tempo.&lt;/p&gt;"
            "&lt;p&gt;Entra no fator exponencial K_eff = K&amp;middot;(1 + (k_run&amp;minus;1)&amp;middot;"
            "e^(&amp;minus;N/N_run)): N_run pequeno confina o excesso de desgaste aos "
            "primeiros ciclos; N_run grande estende o transiente, removendo mais material "
            "no total. Só é lido quando &lt;code&gt;k_wear_running&lt;/code&gt; &amp;gt; 1 (aqui o "
            "companheiro está ligado em 3.0 para o efeito aparecer). O slider desloca a "
            "extensão do trecho íngreme inicial.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: forma opt-in, default 200 ciclos. Provém da forma de "
            "running-in de Archard; a constante é per-rig (lida da própria curva de wear "
            "do ensaio).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;N_wear_run&lt;/code&gt; is the time constant (in cycles) of "
            "break-in: how many cycles the elevated running-in wear lasts before settling "
            "into the steady rate. It is the companion of &lt;code&gt;k_wear_running&lt;/code&gt; &amp;minus; "
            "one says HOW MUCH faster, the other for HOW LONG.&lt;/p&gt;"
            "&lt;p&gt;It enters the exponential factor K_eff = K&amp;middot;(1 + (k_run&amp;minus;1)"
            "&amp;middot;e^(&amp;minus;N/N_run)): a small N_run confines the excess wear to the "
            "first cycles; a large N_run stretches the transient, removing more material "
            "overall. It is only read when &lt;code&gt;k_wear_running&lt;/code&gt; &amp;gt; 1 (here the "
            "companion is enabled at 3.0 so the effect shows). The slider shifts how far "
            "the steep early segment extends.&lt;/p&gt;"
            "&lt;p&gt;Provenance: opt-in form, default 200 cycles. It comes from the Archard "
            "running-in form; the constant is per-rig (read from the test's own wear "
            "curve).&lt;/p&gt;"),
        refs=[("&amp;sect;4.3 running-in &amp;minus; constante de ciclos do transiente",
               "&amp;sect;4.3 running-in &amp;minus; cycle constant of the transient",
               "MODEL_MATH_REFERENCE.md"),
              ("Zhang et al. (2019) &amp;minus; duração do amaciamento medida",
               "Zhang et al. (2019) &amp;minus; measured break-in duration", "Zhang2019")]),

    VarSpec(
        name="k_j_init", symbol="k_j0", unit="N/m", group="stiffness", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(1e9, 8e9, 15, "log"), related=["alpha_GW"],
        equation="k_j_ax(F_0) = k_j_init * (F_0 / F_0_init)^alpha_GW;   Phi_eff = k_b / (k_b + k_j_ax)",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;k_j_init&lt;/code&gt; (N/m) é a rigidez de contato inicial da junta "
            "(os membros comprimidos), a plena pré-carga, no modelo de "
            "Greenwood-Williamson. É a rigidez do 'colchão' de asperezas em contato, que "
            "responde de forma não-linear a carga porque a área real de contato cresce "
            "sublinearmente com a força.&lt;/p&gt;"
            "&lt;p&gt;Entra em duas frentes: (1) no Fator 1 da teoria two-factor, "
            "Phi_eff = k_b/(k_b + k_j_ax) &amp;minus; junta mais rígida (k_j maior) reduz Phi_eff "
            "e a força motriz do afrouxamento; (2) na rigidez torsional/transversal "
            "(k_torsional = k_j_init&amp;middot;d_2/2 no modo legado; k_tr = 0.3&amp;middot;"
            "k_j_init no modo axial_frac). Na prática, porém, o slider quase não move a "
            "curva de ensaio.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: &lt;code&gt;k_j_init&lt;/code&gt; está em FROZEN_S_ZERO (&amp;sect;4.42c) &amp;minus; "
            "a sensibilidade S&amp;asymp;0 no estudo tornado, logo o dado NÃO o identifica e "
            "ele é CONGELADO por procedência (nunca oferecido ao otimizador). Não é "
            "inerte (participa da física), mas é fixo por design.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;k_j_init&lt;/code&gt; (N/m) is the joint's initial contact stiffness "
            "(the clamped members) at full preload, in the Greenwood-Williamson model. It "
            "is the stiffness of the asperity contact 'cushion', which responds "
            "non-linearly to load because the real contact area grows sublinearly with "
            "force.&lt;/p&gt;"
            "&lt;p&gt;It enters on two fronts: (1) in Factor 1 of the two-factor theory, "
            "Phi_eff = k_b/(k_b + k_j_ax) &amp;minus; a stiffer joint (higher k_j) lowers Phi_eff "
            "and the loosening driving force; (2) in the torsional/transverse stiffness "
            "(k_torsional = k_j_init&amp;middot;d_2/2 in legacy mode; k_tr = 0.3&amp;middot;"
            "k_j_init in axial_frac mode). In practice, however, the slider barely moves "
            "the test curve.&lt;/p&gt;"
            "&lt;p&gt;Provenance: &lt;code&gt;k_j_init&lt;/code&gt; is in FROZEN_S_ZERO (&amp;sect;4.42c) &amp;minus; its "
            "sensitivity is S&amp;asymp;0 in the tornado study, so the data does NOT identify "
            "it and it is FROZEN by provenance (never offered to the optimizer). It is "
            "not inert (it takes part in the physics), but it is fixed by design.&lt;/p&gt;"),
        refs=[("&amp;sect;3 Greenwood-Williamson &amp;minus; k_j_ax(F_0)=k_j_init&amp;middot;(F_0/F_init)^&amp;alpha;",
               "&amp;sect;3 Greenwood-Williamson &amp;minus; k_j_ax(F_0)=k_j_init&amp;middot;(F_0/F_init)^&amp;alpha;",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.42c FROZEN_S_ZERO &amp;minus; S&amp;asymp;0, congelado por procedência",
               "&amp;sect;4.42c FROZEN_S_ZERO &amp;minus; S&amp;asymp;0, frozen by provenance",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="alpha_GW", symbol="alpha", unit="-", group="stiffness", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0.1, 1.0, 15, "lin"), related=["k_j_init"], negligible=True,
        equation="k_j_ax(F_0) = k_j_init * (F_0 / F_0_init)^alpha_GW",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;alpha_GW&lt;/code&gt; (adimensional) é o expoente de amolecimento de "
            "Greenwood-Williamson: com que rapidez a rigidez de contato da junta CAI "
            "conforme a pré-carga diminui. Na mecânica de contato de superfícies rugosas "
            "a rigidez escala com a carga elevada a um expoente &amp;lt; 1, porque a área de "
            "contato de asperezas cresce sublinearmente.&lt;/p&gt;"
            "&lt;p&gt;Entra em k_j_ax(F_0) = k_j_init&amp;middot;(F_0/F_0_init)^&amp;alpha;: conforme "
            "F_0 cai, k_j_ax cai, o que SOBE o Phi_eff (Fator 1) e realimenta o "
            "afrouxamento (junta amolecida afrouxa mais fácil). &amp;alpha; maior = mais "
            "amolecimento = realimentação mais forte. Ainda assim, o slider mal move a "
            "curva neste ensaio.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: como o &lt;code&gt;k_j_init&lt;/code&gt;, o &lt;code&gt;alpha_GW&lt;/code&gt; está "
            "em FROZEN_S_ZERO (&amp;sect;4.42c): S&amp;asymp;0, não-identificável neste dataset, "
            "congelado por procedência. A forma vem da teoria de Greenwood &amp;amp; "
            "Williamson (1966).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;alpha_GW&lt;/code&gt; (dimensionless) is the Greenwood-Williamson "
            "softening exponent: how fast the joint contact stiffness FALLS as preload "
            "decreases. In rough-surface contact mechanics the stiffness scales with load "
            "raised to an exponent &amp;lt; 1, because the asperity contact area grows "
            "sublinearly.&lt;/p&gt;"
            "&lt;p&gt;It enters k_j_ax(F_0) = k_j_init&amp;middot;(F_0/F_0_init)^&amp;alpha;: as F_0 "
            "falls, k_j_ax falls, which RAISES Phi_eff (Factor 1) and feeds back into "
            "loosening (a softened joint loosens more easily). Larger &amp;alpha; = more "
            "softening = stronger feedback. Even so, the slider barely moves the curve in "
            "this test.&lt;/p&gt;"
            "&lt;p&gt;Provenance: like &lt;code&gt;k_j_init&lt;/code&gt;, &lt;code&gt;alpha_GW&lt;/code&gt; is in "
            "FROZEN_S_ZERO (&amp;sect;4.42c): S&amp;asymp;0, not identifiable on this dataset, "
            "frozen by provenance. The form comes from Greenwood &amp;amp; Williamson (1966) "
            "theory.&lt;/p&gt;"),
        refs=[("&amp;sect;3 softening GW &amp;minus; expoente de k_j com F_0",
               "&amp;sect;3 GW softening &amp;minus; k_j exponent with F_0",
               "MODEL_MATH_REFERENCE.md"),
              ("Greenwood &amp;amp; Williamson (1966) &amp;minus; contato de superfícies rugosas; &amp;sect;4.42c congelado",
               "Greenwood &amp;amp; Williamson (1966) &amp;minus; rough-surface contact; &amp;sect;4.42c frozen",
               "GW1966")]),

    VarSpec(
        name="mu_bearing", symbol="mu_b", unit="-", group="friction", category="physical",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0.05, 0.30, 15, "lin"), anchor_key="mu_dry", related=["mu_thread"],
        equation="T_resist = mu_thread*F_0*d_2/(2 cos30) + mu_bearing_eff*F_0*r_bearing;   mu_bearing_eff = mu_bearing*(1 - k_dmg_mu*D)",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;mu_bearing&lt;/code&gt; é o coeficiente de atrito na face de bearing &amp;minus; "
            "sob a cabeça do parafuso (ou a porca) contra a arruela/membro. É uma das "
            "duas interfaces de atrito da junta; a outra é o flanco de rosca "
            "(&lt;code&gt;mu_thread&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Tem dois papéis: (1) fixa o torque resistivo que se opõe ao afrouxamento "
            "rotacional, T_resist = &amp;micro;_thread&amp;middot;F_0&amp;middot;d_2/(2cos30&amp;deg;) + "
            "&amp;micro;_bearing_eff&amp;middot;F_0&amp;middot;r_bearing &amp;minus; mais atrito segura o "
            "parafuso (curva mais rasa); (2) dirige o trabalho de atrito dE = "
            "&amp;micro;_bearing_eff&amp;middot;F_0&amp;middot;slip no wear e o onset de "
            "escorregamento F_slip = 0.46&amp;middot;&amp;micro;_bearing_eff&amp;middot;F_0 "
            "(Pai-Hess). Nota: em modo de deslocamento a PROFUNDIDADE de wear é dirigida "
            "por K/H, não por &amp;micro;, então o &lt;code&gt;mu_bearing&lt;/code&gt; atua sobretudo pelo "
            "balanço de torque e pelo onset, não pela taxa de remoção.&lt;/p&gt;"
            "&lt;p&gt;A leitura de proveniência abaixo do gráfico avisa quando o valor sai da "
            "banda MEDIDA de aço seco (âncora &lt;code&gt;mu_dry&lt;/code&gt;). É um INPUT medido "
            "(Motosh de T e F_0), não um botão livre &amp;minus; de fato é o parâmetro de MAIOR "
            "sensibilidade do modelo, o que reforça le-lo do dado em vez de fita-lo.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;mu_bearing&lt;/code&gt; is the friction coefficient at the bearing "
            "face &amp;minus; under the bolt head (or nut) against the washer/member. It is one of "
            "the joint's two friction interfaces; the other is the thread flank "
            "(&lt;code&gt;mu_thread&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;It has two roles: (1) it sets the resisting torque that opposes "
            "rotational loosening, T_resist = &amp;micro;_thread&amp;middot;F_0&amp;middot;d_2/"
            "(2cos30&amp;deg;) + &amp;micro;_bearing_eff&amp;middot;F_0&amp;middot;r_bearing &amp;minus; more "
            "friction holds the bolt (a shallower curve); (2) it drives the friction work "
            "dE = &amp;micro;_bearing_eff&amp;middot;F_0&amp;middot;slip in wear and the slip onset "
            "F_slip = 0.46&amp;middot;&amp;micro;_bearing_eff&amp;middot;F_0 (Pai-Hess). Note: in "
            "displacement mode the wear DEPTH is driven by K/H, not by &amp;micro;, so "
            "&lt;code&gt;mu_bearing&lt;/code&gt; acts mostly through the torque balance and the onset, "
            "not through the removal rate.&lt;/p&gt;"
            "&lt;p&gt;The provenance readout under the plot flags when the value leaves the "
            "MEASURED dry-steel band (anchor &lt;code&gt;mu_dry&lt;/code&gt;). It is a measured INPUT "
            "(Motosh from T and F_0), not a free knob &amp;minus; in fact it is the model's "
            "HIGHEST-sensitivity parameter, which is exactly why it is read from the data "
            "rather than fitted.&lt;/p&gt;"),
        refs=[("&amp;sect;3/&amp;sect;5 T_resistance + F_slip_transverse (Pai-Hess 0.46)",
               "&amp;sect;3/&amp;sect;5 T_resistance + F_slip_transverse (Pai-Hess 0.46)",
               "MODEL_MATH_REFERENCE.md"),
              ("Pai &amp;amp; Hess (2002) &amp;minus; atrito de bearing e afrouxamento por slip",
               "Pai &amp;amp; Hess (2002) &amp;minus; bearing friction and slip loosening",
               "pai2002")]),

    VarSpec(
        name="k_thread_fret", symbol="k_fret", unit="-", group="axial_fretting", category="form",
        context={"baseline": "axial", "overrides": {}},
        sweep=(0, 1.0, 15, "lin"), related=["fret_freq_exp"],
        equation="d_fret = k_thread_fret * (K/H) * F_0 * (4*F_ax/k_b) / A_s;   dF_0 = -k_b*d_fret ~ -F_0*A_F   (A_F = F_amp*|cos theta|)",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;k_thread_fret&lt;/code&gt; é o fator geométrico/de engajamento do "
            "fretting de FLANCO DE ROSCA dirigido pela amplitude de carga AXIAL, "
            "A_F = F_amp&amp;middot;|cos&amp;theta;|. É a forma que a falsificação axial "
            "(&amp;sect;4.6) apontou como FALTANTE: no modelo transversal, wear, creep e "
            "embedding são todos cegos a amplitude, mas o dado axial mostra o "
            "afrouxamento crescendo com A_F.&lt;/p&gt;"
            "&lt;p&gt;Entra na ThreadFrettingLoss, irmã da WearLoss mas no flanco da rosca, "
            "dirigida pelo micro-slip de flanco s_flank = F_ax/k_b: d_fret = "
            "k_thread_fret&amp;middot;(K/H)&amp;middot;F_0&amp;middot;(4&amp;middot;s_flank)/A_s. Como "
            "&amp;Delta;F_0 = &amp;minus;k_b&amp;middot;d_fret e d_fret &amp;prop; F_ax/k_b, o k_b cancela "
            "e &amp;Delta;F_0 &amp;prop; &amp;minus;F_0&amp;middot;A_F. Subir &lt;code&gt;k_thread_fret&lt;/code&gt; "
            "aprofunda o decaimento axial. Em transversal é inerte (F_ax &amp;asymp; 0 em "
            "&amp;theta;=90&amp;deg;); a curva aqui usa baseline AXIAL.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: forma opt-in, default 0 (DESLIGADO). Foi construída para "
            "suprir a forma que a falsificação &amp;sect;4.6 de 03/07/2026 "
            "(&amp;part;(fim)/&amp;part;A_F &amp;equiv; 0 no modelo vs &amp;minus;2.2e-5/N no Liu2017) "
            "exigia &amp;minus; não é um tuner. &lt;b&gt;Atenção (re-baseline de 27/07, "
            "&amp;sect;4.43): essa falsificação está VENCIDA&lt;/b&gt; &amp;minus; a unificação "
            "&amp;rho; adotada em 08/07 já dá ao modelo &amp;minus;1,72e-5/N contra "
            "&amp;minus;2,22e-5/N medido (78% da sensibilidade), com as duas fontes axiais 100% "
            "dentro da meta &lt;i&gt;sem&lt;/i&gt; esta capability. Ela permanece disponível e "
            "desligada; ligá-la hoje exigiria demonstrar que fecha os ~22% restantes da "
            "inclinação sem piorar o resto. A magnitude é fitada por par ao Liu2017 axial "
            "(procedência = fitted).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;k_thread_fret&lt;/code&gt; is the geometric/engagement factor of "
            "THREAD-FLANK fretting driven by the AXIAL load amplitude, "
            "A_F = F_amp&amp;middot;|cos&amp;theta;|. It is the form the axial falsification "
            "(&amp;sect;4.6) flagged as MISSING: in the transverse model, wear, creep and "
            "embedding are all amplitude-blind, but the axial data shows loosening "
            "growing with A_F.&lt;/p&gt;"
            "&lt;p&gt;It enters ThreadFrettingLoss, a sibling of WearLoss but on the thread "
            "flank, driven by the flank micro-slip s_flank = F_ax/k_b: d_fret = "
            "k_thread_fret&amp;middot;(K/H)&amp;middot;F_0&amp;middot;(4&amp;middot;s_flank)/A_s. Since "
            "&amp;Delta;F_0 = &amp;minus;k_b&amp;middot;d_fret and d_fret &amp;prop; F_ax/k_b, k_b "
            "cancels and &amp;Delta;F_0 &amp;prop; &amp;minus;F_0&amp;middot;A_F. Raising "
            "&lt;code&gt;k_thread_fret&lt;/code&gt; deepens the axial decay. It is inert in transverse "
            "(F_ax &amp;asymp; 0 at &amp;theta;=90&amp;deg;); the curve here uses an AXIAL "
            "baseline.&lt;/p&gt;"
            "&lt;p&gt;Provenance: opt-in form, default 0 (OFF). It was built to supply the form "
            "that the &amp;sect;4.6 falsification of 2026-07-03 (&amp;part;(final)/&amp;part;A_F "
            "&amp;equiv; 0 in the model vs &amp;minus;2.2e-5/N on Liu2017) demanded &amp;minus; it is "
            "not a tuner. &lt;b&gt;Note (2026-07-27 re-baseline, &amp;sect;4.43): that falsification "
            "is SUPERSEDED&lt;/b&gt; &amp;minus; the &amp;rho;-unification adopted on 2026-07-08 "
            "already gives the model &amp;minus;1.72e-5/N against &amp;minus;2.22e-5/N measured (78% "
            "of the sensitivity), with both axial sources fully inside the goal &lt;i&gt;without&lt;/i&gt; "
            "this capability. It stays available and off; turning it on today would require showing "
            "it closes the remaining ~22% of the slope without degrading the rest. "
            "The magnitude is fitted per pair to the Liu2017 axial data (provenance = "
            "fitted).&lt;/p&gt;"),
        refs=[("&amp;sect;4.5 ThreadFrettingLoss &amp;minus; perda &amp;prop; A_F (flanco de rosca)",
               "&amp;sect;4.5 ThreadFrettingLoss &amp;minus; loss &amp;prop; A_F (thread flank)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.6 falsificação axial apontou esta forma &amp;mdash; VENCIDA em &amp;sect;4.43 (27/07)",
               "&amp;sect;4.6 axial falsification pointed to this form &amp;mdash; SUPERSEDED by &amp;sect;4.43 (2026-07-27)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="fret_freq_exp", symbol="p_fret", unit="-", group="axial_fretting", category="form",
        context={"baseline": "axial", "overrides": {"k_thread_fret": 0.5}},
        sweep=(0, 2.0, 13, "lin"), related=["f_ref_fret", "k_thread_fret"],
        equation="d_fret *= (f_ref_fret / freq)^fret_freq_exp;   fret_freq_exp = 0  =>  factor = 1 (OFF)",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;fret_freq_exp&lt;/code&gt; é o expoente da dependência de FREQUÊNCIA do "
            "fretting axial (efeito de dwell). Em frequência mais baixa há mais tempo de "
            "contato por ciclo &amp;minus; mais oxidação e formação de debris &amp;minus; logo mais material "
            "removido por ciclo. O dado Li2022ti (M10, A_F=10 kN, 10/15/20 Hz) mostra a "
            "perda crescendo quando a frequência cai.&lt;/p&gt;"
            "&lt;p&gt;Entra como fator (f_ref_fret/f)^p sobre d_fret: em f = f_ref o fator é 1; "
            "abaixo de f_ref passa de 1 (mais perda), acima de f_ref fica abaixo de 1. "
            "Como o baseline axial roda a 30 Hz &amp;minus; ACIMA da referência default de 15 Hz &amp;minus; "
            "subir &lt;code&gt;fret_freq_exp&lt;/code&gt; aqui REDUZ levemente o fretting (o ensaio "
            "está no ramo de alta frequência/pouco dwell). O expoente é LIDO do próprio "
            "sweep de frequência (perda &amp;prop; 1/f &amp;rArr; p &amp;asymp; 1), não fitado ao "
            "MAE.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: forma opt-in, default 0 (fator = 1, freq-independente, "
            "bit-a-bit). &amp;sect;4.39. Aqui o companheiro &lt;code&gt;k_thread_fret&lt;/code&gt; = 0.5 "
            "está ligado para o termo existir. Só afeta o fretting axial "
            "(ThreadFrettingLoss).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;fret_freq_exp&lt;/code&gt; is the exponent of the FREQUENCY "
            "dependence of axial fretting (dwell effect). At lower frequency there is "
            "more contact time per cycle &amp;minus; more oxidation and debris formation &amp;minus; hence "
            "more material removed per cycle. The Li2022ti data (M10, A_F=10 kN, 10/15/20 "
            "Hz) shows the loss growing as frequency drops.&lt;/p&gt;"
            "&lt;p&gt;It enters as the factor (f_ref_fret/f)^p on d_fret: at f = f_ref the "
            "factor is 1; below f_ref it exceeds 1 (more loss), above f_ref it is below "
            "1. Because the axial baseline runs at 30 Hz &amp;minus; ABOVE the 15 Hz default "
            "reference &amp;minus; raising &lt;code&gt;fret_freq_exp&lt;/code&gt; here slightly REDUCES the "
            "fretting (the test sits on the high-frequency/low-dwell branch). The exponent "
            "is READ from the frequency sweep itself (loss &amp;prop; 1/f &amp;rArr; p &amp;asymp; 1), "
            "not fitted to the MAE.&lt;/p&gt;"
            "&lt;p&gt;Provenance: opt-in form, default 0 (factor = 1, frequency-independent, "
            "bit-for-bit). &amp;sect;4.39. Here the companion &lt;code&gt;k_thread_fret&lt;/code&gt; = 0.5 "
            "is enabled so the term exists. It only affects axial fretting "
            "(ThreadFrettingLoss).&lt;/p&gt;"),
        refs=[("&amp;sect;4.5 fator de dwell &amp;minus; (f_ref/f)^exp sobre d_fret",
               "&amp;sect;4.5 dwell factor &amp;minus; (f_ref/f)^exp on d_fret",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.39 &amp;minus; Li2022ti 10/15/20 Hz: perda &amp;prop; 1/f (dwell/oxidação, r=&amp;minus;0.99)",
               "&amp;sect;4.39 &amp;minus; Li2022ti 10/15/20 Hz: loss &amp;prop; 1/f (dwell/oxidation, r=&amp;minus;0.99)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="f_ref_fret", symbol="f_ref,fret", unit="Hz", group="axial_fretting", category="form",
        context={"baseline": "axial", "overrides": {"k_thread_fret": 0.5, "fret_freq_exp": 1.0}},
        sweep=(5, 30, 15, "lin"), related=["fret_freq_exp"],
        equation="d_fret *= (f_ref_fret / freq)^fret_freq_exp   (so lido se fret_freq_exp != 0)",
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;f_ref_fret&lt;/code&gt; (Hz) é a frequência de referência do fator de "
            "dwell do fretting: a frequência em que o fator (f_ref/f)^p vale exatamente 1. "
            "É uma âncora por rig &amp;minus; abaixo dela o fretting é amplificado, acima dela é "
            "atenuado.&lt;/p&gt;"
            "&lt;p&gt;Entra no mesmo fator (f_ref_fret/f)^p sobre d_fret. Com o expoente ligado "
            "em 1.0 (aqui) o fator é linear em f_ref: (f_ref/30) no baseline de 30 Hz. "
            "Subir &lt;code&gt;f_ref_fret&lt;/code&gt; em direção a (e acima de) 30 Hz eleva o fator "
            "acima de 1 e aprofunda a curva; baixa-lo atenua o fretting. Só é lido quando "
            "&lt;code&gt;fret_freq_exp&lt;/code&gt; != 0 (aqui a forma de frequência está ligada em "
            "1.0).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: forma opt-in, default 15 Hz, âncora per-rig do sweep de "
            "frequência (&amp;sect;4.39). Só tem sentido físico com a forma de frequência "
            "(&lt;code&gt;fret_freq_exp&lt;/code&gt;) ligada.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;code&gt;f_ref_fret&lt;/code&gt; (Hz) is the reference frequency of the "
            "fretting dwell factor: the frequency at which the factor (f_ref/f)^p equals "
            "exactly 1. It is a per-rig anchor &amp;minus; below it the fretting is amplified, above "
            "it it is attenuated.&lt;/p&gt;"
            "&lt;p&gt;It enters the same factor (f_ref_fret/f)^p on d_fret. With the exponent "
            "enabled at 1.0 (here) the factor is linear in f_ref: (f_ref/30) on the 30 Hz "
            "baseline. Raising &lt;code&gt;f_ref_fret&lt;/code&gt; toward (and above) 30 Hz lifts the "
            "factor above 1 and deepens the curve; lowering it attenuates the fretting. It "
            "is only read when &lt;code&gt;fret_freq_exp&lt;/code&gt; != 0 (here the frequency form is "
            "enabled at 1.0).&lt;/p&gt;"
            "&lt;p&gt;Provenance: opt-in form, default 15 Hz, a per-rig anchor from the "
            "frequency sweep (&amp;sect;4.39). It only has physical meaning with the frequency "
            "form (&lt;code&gt;fret_freq_exp&lt;/code&gt;) turned on.&lt;/p&gt;"),
        refs=[("&amp;sect;4.5 frequência de referência do fator de dwell",
               "&amp;sect;4.5 reference frequency of the dwell factor",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.39 &amp;minus; âncora per-rig do sweep de frequência (Li2022ti)",
               "&amp;sect;4.39 &amp;minus; per-rig anchor of the frequency sweep (Li2022ti)",
               "MODEL_LEGITIMACY.md")]),
])

# =============================== LOOSENING CORE + SLIP REGIME (13) ===============================
VARIABLE_SPECS.extend([
    VarSpec(name="tr_loose_gain", symbol="Phi_gain", unit="-", group="loosening", category="physical", context={"baseline":"transverse","overrides":{}}, sweep=(0.5,5.0,15,"lin"), related=[],
        equation="Phi_tr_active = tr_loose_gain if F_tr >= F_slip else 0.01;  L_total = hypot(Phi_ax*sin(beta)*F_ax, Phi_tr*cos(beta)*F_tr);  T_loose = L_total*d_2/2",
        physics_pt=(
            "&lt;p&gt;O afrouxamento rotacional no modelo é o produto de DOIS fatores (teoria "
            "two-factor): um &lt;b&gt;Fator 1&lt;/b&gt; anisotrópico, a razão de rigidez "
            "&lt;code&gt;&amp;Phi;_eff&lt;/code&gt;, e um &lt;b&gt;Fator 2&lt;/b&gt; de projeção pela hélice. O "
            "parâmetro &lt;code&gt;tr_loose_gain&lt;/code&gt; é o ganho do Fator 1 na direção "
            "TRANSVERSAL: enquanto a força transversal do ciclo não vence o limiar de "
            "escorregamento (&lt;code&gt;F_tr &amp;lt; F_slip&lt;/code&gt;) a junta está praticamente "
            "travada (&lt;code&gt;&amp;Phi;_tr_active = 0.01&lt;/code&gt;); assim que há gross slip, "
            "&lt;code&gt;&amp;Phi;_tr_active&lt;/code&gt; salta para &lt;code&gt;tr_loose_gain&lt;/code&gt;, "
            "refletindo a amplificação dinâmica do backing-off sob vibração transversal "
            "(ensaio Junker).&lt;/p&gt;"
            "&lt;p&gt;Na equação, &lt;code&gt;&amp;Phi;_tr_active&lt;/code&gt; multiplica a perna transversal do "
            "torque de afrouxamento (&lt;code&gt;L_total = hypot(&amp;Phi;_ax&amp;middot;sin&amp;beta;"
            "&amp;middot;F_ax, &amp;Phi;_tr&amp;middot;cos&amp;beta;&amp;middot;F_tr)&lt;/code&gt;). Subir o slider "
            "aumenta o torque motor transversal &amp;rarr; o afrouxamento dispara antes e "
            "desce mais fundo; reduzir aproxima a curva de uma junta que resiste ao "
            "afrouxamento. É o único acoplamento axial-torsional de &lt;code&gt;[K]&lt;/code&gt; que "
            "a hélice fornece.&lt;/p&gt;"
            "&lt;p&gt;Historicamente estava hardcoded em 0.95 dentro do mecanismo; hoje é um "
            "campo de &lt;code&gt;JointMaterial&lt;/code&gt; com default 2.0 (o Estágio B foldou a "
            "antiga &lt;code&gt;Phi_tr_correction&lt;/code&gt; aqui). No estudo de sensibilidade "
            "(OAT) é o knob de maior &lt;code&gt;S&lt;/code&gt; (0.054) que ainda NÃO tem âncora "
            "medida &amp;rarr; é o &lt;b&gt;alvo #1 de proveniência&lt;/b&gt; do modelo.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Rotational loosening in the model is the product of TWO factors "
            "(two-factor theory): an anisotropic &lt;b&gt;Factor 1&lt;/b&gt;, the stiffness ratio "
            "&lt;code&gt;&amp;Phi;_eff&lt;/code&gt;, and a helix-projection &lt;b&gt;Factor 2&lt;/b&gt;. The "
            "parameter &lt;code&gt;tr_loose_gain&lt;/code&gt; is the Factor-1 gain in the TRANSVERSE "
            "direction: while the cycle transverse force does not beat the slip threshold "
            "(&lt;code&gt;F_tr &amp;lt; F_slip&lt;/code&gt;) the joint is essentially locked "
            "(&lt;code&gt;&amp;Phi;_tr_active = 0.01&lt;/code&gt;); once gross slip occurs, "
            "&lt;code&gt;&amp;Phi;_tr_active&lt;/code&gt; jumps to &lt;code&gt;tr_loose_gain&lt;/code&gt;, reflecting "
            "the dynamic amplification of backing-off under transverse vibration (Junker "
            "test).&lt;/p&gt;"
            "&lt;p&gt;In the equation, &lt;code&gt;&amp;Phi;_tr_active&lt;/code&gt; multiplies the transverse "
            "leg of the loosening torque (&lt;code&gt;L_total = hypot(&amp;Phi;_ax&amp;middot;sin&amp;beta;"
            "&amp;middot;F_ax, &amp;Phi;_tr&amp;middot;cos&amp;beta;&amp;middot;F_tr)&lt;/code&gt;). Raising the "
            "slider increases the transverse driving torque &amp;rarr; loosening fires earlier "
            "and drops deeper; lowering it makes the curve look like a joint that resists "
            "loosening. It is the only axial-torsional &lt;code&gt;[K]&lt;/code&gt; coupling the helix "
            "provides.&lt;/p&gt;"
            "&lt;p&gt;It used to be hardcoded at 0.95 inside the mechanism; today it is a "
            "&lt;code&gt;JointMaterial&lt;/code&gt; field with default 2.0 (Stage B folded the old "
            "&lt;code&gt;Phi_tr_correction&lt;/code&gt; into it). In the sensitivity study (OAT) it is "
            "the highest-&lt;code&gt;S&lt;/code&gt; knob (0.054) that still has NO measured anchor "
            "&amp;rarr; it is the model's &lt;b&gt;#1 provenance target&lt;/b&gt;.&lt;/p&gt;"),
        refs=[("&amp;sect;4.4 RotationalLooseningLoss &amp;minus; Fator 1 (razão de rigidez Phi_eff)",
               "&amp;sect;4.4 RotationalLooseningLoss &amp;minus; Factor 1 (stiffness ratio Phi_eff)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.42/&amp;sect;8.4 &amp;minus; tr_loose_gain é o alvo #1 de proveniência (S=0.054, sem âncora)",
               "&amp;sect;4.42/&amp;sect;8.4 &amp;minus; tr_loose_gain is the #1 provenance target (S=0.054, no anchor)",
               "MODEL_LEGITIMACY.md"),
              ("Teoria two-factor (Phi x hélice)", "Two-factor theory (Phi x helix)",
               "specs/2026-05-16-two-factor-loosening-theory.md")]),

    VarSpec(name="free_spin", symbol="f_spin", unit="-", group="loosening", category="form", context={"baseline":"transverse","overrides":{}}, sweep=(0,1.0,15,"lin"), related=[], negligible=True,
        equation="d_theta_free = free_spin * max(drive_free - d_theta, 0);  dF_0 = -k_b*(p/2pi)*d_theta (unchanged);  dE = T_resist*(d_theta + d_theta_free)",
        physics_pt=(
            "&lt;p&gt;Depois que o gate de arresto auto-travante fecha, a porca ainda pode "
            "micro-girar de ida-e-volta sem drenar pré-carga líquida &amp;minus; fisicamente é a "
            "folga de rosca em que a porca gira LIVRE. &lt;code&gt;free_spin&lt;/code&gt; é a fração "
            "do drive rotacional NÃO-arrestado que segue como essa rotação livre.&lt;/p&gt;"
            "&lt;p&gt;Na equação, &lt;code&gt;d_theta_free = free_spin&amp;middot;max(drive_free &amp;minus; "
            "d_theta, 0)&lt;/code&gt; soma-se só a &lt;code&gt;&amp;theta;_loose&lt;/code&gt; e ao calor de "
            "atrito &lt;code&gt;dE = T_resist&amp;middot;(d_theta + d_theta_free)&lt;/code&gt;; a perda de "
            "pré-carga &lt;code&gt;dF_0&lt;/code&gt; contínua BIT-IDÊNTICA (a hélice só drena a parte "
            "arrestada). Por isso mover o slider muda o ângulo acumulado e a energia, mas "
            "quase NÃO mexe na curva F/F0.&lt;/p&gt;"
            "&lt;p&gt;A forma foi nomeada pelo confronto do &lt;code&gt;&amp;theta;(N)&lt;/code&gt; do Rousseau "
            "(steel_t10 média 3.3x mais rotação medida do que a perda de pré-carga "
            "explica). Opt-in, default 0 = OFF (bit-identical).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;After the self-locking arrest gate closes, the nut can still micro-rotate "
            "back-and-forth without draining net preload &amp;minus; physically it is the thread "
            "play in which the nut spins FREE. &lt;code&gt;free_spin&lt;/code&gt; is the fraction of "
            "the NON-arrested rotational drive that continues as that free rotation.&lt;/p&gt;"
            "&lt;p&gt;In the equation, &lt;code&gt;d_theta_free = free_spin&amp;middot;max(drive_free "
            "&amp;minus; d_theta, 0)&lt;/code&gt; adds only to &lt;code&gt;&amp;theta;_loose&lt;/code&gt; and to the "
            "friction heat &lt;code&gt;dE = T_resist&amp;middot;(d_theta + d_theta_free)&lt;/code&gt;; the "
            "preload loss &lt;code&gt;dF_0&lt;/code&gt; stays BIT-IDENTICAL (the helix only drains the "
            "arrested part). So moving the slider changes the accumulated angle and the "
            "energy, but barely touches the F/F0 curve.&lt;/p&gt;"
            "&lt;p&gt;The form was named by the Rousseau &lt;code&gt;&amp;theta;(N)&lt;/code&gt; confront "
            "(steel_t10 measured on average 3.3x more rotation than the preload loss "
            "explains). Opt-in, default 0 = OFF (bit-identical).&lt;/p&gt;"),
        refs=[("&amp;sect;6 / &amp;sect;4.23 &amp;minus; free-spin pós-arresto (confronto theta(N) do Rousseau)",
               "&amp;sect;6 / &amp;sect;4.23 &amp;minus; post-arrest free spin (Rousseau theta(N) confront)",
               "MODEL_MATH_REFERENCE.md"),
              ("Junker (1969) &amp;minus; afrouxamento por vibração transversal",
               "Junker (1969) &amp;minus; transverse vibration loosening", "junker1969")]),

    VarSpec(name="free_spin_kin", symbol="f_kin", unit="-", group="loosening", category="form",
        # O kernel graded_scrit precisa estar LIGADO para o campo agir (só esse
        # ramo o lê) — mesmo idioma do emb_pressure_exp, que sobe p_ref para a
        # página ensinar a lei. Sem os overrides o slider seria morto.
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit",
                                "k_loose_graded": 0.05, "s_crit_loose": 0.0,
                                "loose_arrest_floor": 0.0}},
        sweep=(0, 0.9, 13, "lin"), related=["free_spin", "k_loose_graded", "loose_rate_mode"],
        equation="dF_0 = -k_b*(p/2pi)*d_theta*(1 - f_kin);  theta_loose e dE ficam com d_theta TOTAL",
        physics_pt=(
            "&lt;p&gt;A hélice do engine drena pré-carga a &lt;code&gt;k_b&amp;middot;(p/2&amp;pi;)&lt;/code&gt; por "
            "radiano de rotação relativa &amp;minus; como se todo o laço fora do parafuso fosse "
            "infinitamente rígido. Numa junta real a rigidez de dreno é a &lt;b&gt;série&lt;/b&gt; "
            "parafuso + membro + compliances de interface, sempre MENOR que &lt;code&gt;k_b&lt;/code&gt;. "
            "&lt;code&gt;free_spin_kin&lt;/code&gt; é a fração da rotação que NÃO drena &amp;minus; o "
            "complemento da razão entre a rigidez de dreno real e a da hélice pura.&lt;/p&gt;"
            "&lt;p&gt;Ela é &lt;b&gt;LIDA de dois observáveis publicados&lt;/b&gt;, não fitada: "
            "&lt;code&gt;f_kin = 1 &amp;minus; (dF/d&amp;theta;)_medido / (k_b&amp;middot;p/2&amp;pi;)&lt;/code&gt;. No "
            "Rousseau 2025 a Fig. 5 (aço) dá dF/d&amp;theta; = 920/894 N/grau em t10/t12 "
            "(r&amp;sup2; 0,9997/0,9969) contra 3278 da hélice pura &amp;rArr; f_kin &amp;asymp; 0,72; a "
            "no aço a constante é POR JUNTA (o HDPE, re-extraído do PDF por ticks, dá "
            "138/207 &amp;minus; varia com a espessura).&lt;/p&gt;"
            "&lt;p&gt;&lt;code&gt;&amp;theta;_loose&lt;/code&gt; e &lt;code&gt;dE&lt;/code&gt; ficam com a rotação TOTAL (o "
            "filete atrita na rotação relativa inteira). Só o ramo &lt;code&gt;graded_scrit&lt;/code&gt; "
            "lê o campo. Default 0 = OFF (bit-idêntico).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The engine helix drains preload at &lt;code&gt;k_b&amp;middot;(p/2&amp;pi;)&lt;/code&gt; per "
            "radian of relative rotation &amp;minus; as if the whole loop outside the bolt were "
            "infinitely stiff. In a real joint the drain stiffness is the &lt;b&gt;series&lt;/b&gt; of "
            "bolt + member + interface compliances, always SMALLER than &lt;code&gt;k_b&lt;/code&gt;. "
            "&lt;code&gt;free_spin_kin&lt;/code&gt; is the rotation fraction that does NOT drain &amp;minus; "
            "the complement of the ratio between the real drain stiffness and the pure-helix "
            "one.&lt;/p&gt;"
            "&lt;p&gt;It is &lt;b&gt;READ from two published observables&lt;/b&gt;, not fitted: "
            "&lt;code&gt;f_kin = 1 &amp;minus; (dF/d&amp;theta;)_measured / (k_b&amp;middot;p/2&amp;pi;)&lt;/code&gt;. In "
            "Rousseau 2025, Fig. 5 (steel) gives dF/d&amp;theta; = 920/894 N/deg for t10/t12 "
            "(r&amp;sup2; 0.9997/0.9969) against 3278 for the pure helix &amp;rArr; f_kin &amp;asymp; "
            "0.72; in steel the constant is PER-JOINT (HDPE, re-extracted from the PDF via "
            "ticks, gives 138/207 &amp;minus; it varies with thickness).&lt;/p&gt;"
            "&lt;p&gt;&lt;code&gt;&amp;theta;_loose&lt;/code&gt; and &lt;code&gt;dE&lt;/code&gt; keep the TOTAL rotation "
            "(the thread flank rubs over the whole relative rotation). Only the "
            "&lt;code&gt;graded_scrit&lt;/code&gt; branch reads the field. Default 0 = OFF "
            "(bit-identical).&lt;/p&gt;"),
        refs=[("&amp;sect;4.56 &amp;minus; free-spin cinemático (rigidez de dreno lida do Rousseau Fig. 4/5)",
               "&amp;sect;4.56 &amp;minus; kinematic free spin (drain stiffness read from Rousseau Fig. 4/5)",
               "MODEL_LEGITIMACY.md"),
              ("Rousseau &amp; Bouzid (2025) &amp;minus; rotação relativa parafuso-porca medida com a pré-carga",
               "Rousseau &amp; Bouzid (2025) &amp;minus; bolt-nut relative rotation measured with preload",
               "rousseau2025")]),

    VarSpec(name="ax_floor_override", symbol="&kappa;_ax", unit="-",
        group="loosening", category="form",
        context={"baseline":"transverse","overrides":{"loose_arrest_floor":0.137}},
        sweep=(0.0, 1.0, 11, "lin"),
        related=["loose_arrest_floor", "arrest_approach_exp"],
        negligible=True,
        equation=("f_min &lt;- f_min * max(0, 1 - F_ax_ext/(kappa_ax * F_sep));  "
                  "F_sep = F_0/(1-Phi).  kappa_ax=0 OU F_ax_ext=0 => piso intacto"),
        physics_pt=(
            "&lt;p&gt;O &lt;code&gt;loose_arrest_floor&lt;/code&gt; e' um piso &lt;b&gt;auto-gerado&lt;/b&gt;: o "
            "afrouxamento para sozinho quando a pre-carga cai ao ponto em que o nucleo "
            "auto-travado resiste. Este campo o torna &lt;b&gt;anulavel por uma condicao de "
            "contorno EXTERNA&lt;/b&gt; &amp;minus; uma tracao axial imposta de fora consome o "
            "aperto residual e, no limite, separa a interface: nada arresta, e a porca "
            "segue girando abaixo de onde teria parado.&lt;/p&gt;"
            "&lt;p&gt;&amp;#9888; &lt;b&gt;FALSIFICADA como rota no ECCLES_2010&lt;/b&gt; (2026-08-21, prereg "
            "&lt;code&gt;2026-08-21-eccles-axial-tres-camadas&lt;/code&gt;, G3 reprovado em 4 doses). "
            "A curva-alvo &lt;code&gt;fig7d&lt;/code&gt; PIORA (res.max 0,0901 &amp;rarr; 0,22&amp;ndash;0,25) e "
            "os controles pioram junto. O motivo e' aritmetico: os pisos adotados daquela "
            "fonte JA decrescem com a carga axial (0,232 / 0,182 / 0,137 para 1,1 / 2,7 / "
            "3,1 kN, com &lt;code&gt;prov&lt;/code&gt; de &lt;i&gt;fitado-this-rig&lt;/i&gt;) &amp;minus; o efeito do "
            "axial JA estava absorvido no piso, e anula-lo aplica o desconto DUAS VEZES. "
            "A capacidade fica default-inerte; a rota que sobra e' &lt;b&gt;derivar&lt;/b&gt; o piso do "
            "axial com um numero compartilhado, substituindo os fitados.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;loose_arrest_floor&lt;/code&gt; is a &lt;b&gt;self-generated&lt;/b&gt; floor. This "
            "field makes it overridable by an &lt;b&gt;external boundary condition&lt;/b&gt;: an "
            "imposed axial tension consumes the residual clamp and, in the limit, separates "
            "the interface &amp;minus; nothing arrests, and the nut keeps turning below where it "
            "would have stopped (Eccles 2010's central finding).&lt;/p&gt;"
            "&lt;p&gt;&amp;#9888; &lt;b&gt;FALSIFIED as a route&lt;/b&gt; on ECCLES_2010: the adopted floors "
            "already decrease with axial load, so annulling them double-counts the effect. "
            "Capability stays default-inert.&lt;/p&gt;"),
        refs=["Eccles, Sherrington &amp; Arnell (2010), Proc IMechE C 224:483-495",
              "VDI 2230 (particao de carga externa entre parafuso e membro)"]),
    VarSpec(name="arrest_approach_exp", symbol="m", unit="-", group="loosening", category="form", context={"baseline":"transverse","overrides":{"loose_torsion_mode":"bolt_torsion","loosening_slip_coupling":"gross_fraction","k_tr_mode":"bending","eta_loose":8.0,"loose_arrest_floor":0.10}}, sweep=(1.0,4.0,13,"lin"), related=["loose_arrest_floor"],
        equation="g_arrest = max(0, 1 - F_min/F_0) ** arrest_approach_exp   (m=1 => expressao anterior, bit-identica)",
        physics_pt=(
            "&lt;p&gt;O piso de arresto (&lt;code&gt;loose_arrest_floor&lt;/code&gt;) diz ONDE a curva "
            "para; este expoente diz &lt;b&gt;COMO ela chega lá&lt;/b&gt;. O gate de auto-travamento "
            "já era suave &amp;minus; &lt;code&gt;g = 1 &amp;minus; F_min/F_0&lt;/code&gt; &amp;minus; mas linear no "
            "excesso drenável. Elevar &lt;code&gt;g&lt;/code&gt; a &lt;code&gt;m &amp;gt; 1&lt;/code&gt; faz a taxa "
            "morrer mais cedo conforme &lt;code&gt;F_0&lt;/code&gt; se aproxima do piso: a curva "
            "&lt;b&gt;desacelera até o platô&lt;/b&gt; em vez de descer reto e bater.&lt;/p&gt;"
            "&lt;p&gt;Repare no que ele NÃO faz: não mexe no nível final (isso é o piso, lido do "
            "dado por par) nem na perda total &amp;minus; ele &lt;b&gt;redistribui&lt;/b&gt; a perda do "
            "início para o fim da curva. Por isso o slider quase não move o ponto final e "
            "muda bastante o meio.&lt;/p&gt;"
            "&lt;p&gt;Procedência: forma proposta no pré-registro do grupo A (2026-07-27) depois "
            "de um diagnóstico medir que 13 curvas em &lt;b&gt;4 rigs independentes&lt;/b&gt; "
            "(Chu2026, Yang2019, Karlsen, Zhang2006) têm o MESMO perfil de resíduo "
            "&amp;minus; colapso cedo demais, arresto tarde demais &amp;minus; com correlação "
            "0,90 a 1,00. Adimensional. Default &lt;code&gt;1.0&lt;/code&gt; = expressão anterior, "
            "bit-idêntica.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;RESULTADO: FALHOU o gate e NÃO está adotada.&lt;/b&gt; Ajustada no Chu2026 e "
            "aplicada sem re-fit aos outros 3 rigs, ela &lt;b&gt;piorou&lt;/b&gt; o resíduo máximo "
            "médio em 9% (exigia-se queda de 30%): fecha lindamente a única curva em que foi "
            "ajustada (res.máx 0,115 &amp;rarr; 0,035) e degrada as de fora &amp;minus; o Karlsen vai "
            "de 0,236 a 0,378. É o retrato de um valor que não transfere, e o gate de "
            "transferência existe exatamente para pegá-lo. O campo fica aqui, desligado, "
            "&lt;b&gt;documentando um FAIL medido em vez de apagar a evidência&lt;/b&gt;.&lt;/p&gt;"
            "&lt;p&gt;Detalhe que explica a falha e vale como lição: o gate de auto-travamento "
            "vale &lt;b&gt;exatamente 1&lt;/b&gt; quando não há piso de arresto, e &lt;code&gt;1^m = 1&lt;/code&gt; "
            "&amp;minus; ou seja, o expoente é inerte onde o piso está desligado. No Chu2026 só "
            "&lt;b&gt;1 das 9&lt;/b&gt; curvas tinha piso ativo, então o \"ajuste na maior fonte\" foi, "
            "na prática, um ajuste sobre uma curva só.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The arrest floor (&lt;code&gt;loose_arrest_floor&lt;/code&gt;) says WHERE the curve "
            "stops; this exponent says &lt;b&gt;HOW it gets there&lt;/b&gt;. The self-locking gate was "
            "already smooth &amp;minus; &lt;code&gt;g = 1 &amp;minus; F_min/F_0&lt;/code&gt; &amp;minus; but linear "
            "in the drainable excess. Raising &lt;code&gt;g&lt;/code&gt; to &lt;code&gt;m &amp;gt; 1&lt;/code&gt; "
            "makes the rate die earlier as &lt;code&gt;F_0&lt;/code&gt; approaches the floor: the curve "
            "&lt;b&gt;decelerates into the plateau&lt;/b&gt; instead of running straight down into "
            "it.&lt;/p&gt;"
            "&lt;p&gt;Note what it does NOT do: it does not move the final level (that is the "
            "floor, read per pair from the data) nor the total loss &amp;minus; it "
            "&lt;b&gt;redistributes&lt;/b&gt; loss from the start of the curve to the end. That is why "
            "the slider barely moves the endpoint and changes the middle a lot.&lt;/p&gt;"
            "&lt;p&gt;Provenance: form proposed in the group-A pre-registration (2026-07-27) after "
            "a diagnosis measured that 13 curves across &lt;b&gt;4 independent rigs&lt;/b&gt; "
            "(Chu2026, Yang2019, Karlsen, Zhang2006) share the SAME residual profile "
            "&amp;minus; collapsing too early, arresting too late &amp;minus; at correlation "
            "0.90 to 1.00. Dimensionless. Default &lt;code&gt;1.0&lt;/code&gt; = the previous "
            "expression, bit-identical.&lt;/p&gt;"),
        refs=[("&amp;sect;6 &amp;minus; self_locking_gate (agora com expoente de aproximação)",
               "&amp;sect;6 &amp;minus; self_locking_gate (now with an approach exponent)",
               "MODEL_MATH_REFERENCE.md"),
              ("diagnóstico das 26 curvas: 3 grupos, não 1 (r = 0,90&amp;ndash;1,00 no grupo A)",
               "diagnosis of the 26 curves: 3 groups, not 1 (r = 0.90&amp;ndash;1.00 in group A)",
               "New_Theory/kernel_diagnostic_2026-07-27.md")]),

    VarSpec(name="loose_arrest_residual", symbol="r", unit="-", group="loosening", category="form", context={"baseline":"transverse","overrides":{"loose_torsion_mode":"bolt_torsion","loosening_slip_coupling":"gross_fraction","k_tr_mode":"bending","eta_loose":8.0,"loose_arrest_floor":0.10}}, sweep=(0.0,0.6,13,"lin"), related=["loose_arrest_floor","arrest_approach_exp"],
        equation="g = max(r*(1 - loose_arrest_floor), max(0, 1 - F_min/F_0)**m)   (r=0 =&gt; expressao anterior, bit-identica)",
        physics_pt=(
            "&lt;p&gt;O piso de arresto diz ONDE a curva para e o expoente diz COMO ela "
            "chega lá. Este campo responde a uma terceira pergunta: &lt;b&gt;e se ela não "
            "parar?&lt;/b&gt;&lt;/p&gt;"
            "&lt;p&gt;Sem ele, o gate de auto-travamento &lt;b&gt;zera&lt;/b&gt; quando "
            "&lt;code&gt;F_0&lt;/code&gt; alcança o piso: o canal rotacional morre e o ponto fixo "
            "é absoluto. O engine só oferecia dois extremos &amp;minus; piso zero "
            "(&lt;i&gt;runaway&lt;/i&gt;, colapso) ou piso positivo (parada dura). Este campo põe o "
            "&lt;b&gt;meio-termo&lt;/b&gt;: abaixo do limiar o canal retém a fração "
            "&lt;code&gt;r&lt;/code&gt; da sua &lt;i&gt;própria taxa inicial&lt;/i&gt; em vez de morrer, e o "
            "arresto deixa de ser barreira para virar &lt;b&gt;joelho&lt;/b&gt;.&lt;/p&gt;"
            "&lt;p&gt;A leitura física é que o núcleo auto-travado de Cattaneo&amp;ndash;Mindlin "
            "&lt;b&gt;não é rígido&lt;/b&gt;: ele cede lentamente sob ciclagem continuada. O que "
            "trava não é um batente, é um contato que ainda flui.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Medido, e é por isso que existe:&lt;/b&gt; no ICMEZ_2025 o dado "
            "&lt;b&gt;atravessa&lt;/b&gt; o piso adotado (0,308) e segue caindo até 0,223, mantendo "
            "cerca de metade da taxa de meio-ensaio, enquanto o modelo achata em 0,29 "
            "(gate medido no sítio: 0,0000). Com o residual a taxa tardia das 3 curvas-alvo "
            "sobe de 0,20 para 0,47, dentro da banda do dado (0,48&amp;ndash;0,57) que o "
            "binário nunca alcançava.&lt;/p&gt;"
            "&lt;p&gt;⚠️ &lt;b&gt;Mecanismo validado, adoção FALSIFICADA&lt;/b&gt; (2026-08-15). Ligá-lo "
            "sozinho reprova o gate de isolamento, e o par que fecha 3 curvas quebra 2 "
            "protegidas, piora outras 3 e desancora um input de tabela VDI. Fica "
            "&lt;b&gt;default-inerte&lt;/b&gt; (&lt;code&gt;r = 0&lt;/code&gt;, caminho antigo bit-idêntico): o "
            "arresto era &lt;i&gt;um&lt;/i&gt; defeito daquela fonte, não o único.&lt;/p&gt;"
        ),
        physics_en=(
            "&lt;p&gt;The arrest floor says WHERE the curve stops; the approach exponent says "
            "HOW it gets there. This field answers a third question: &lt;b&gt;what if it does "
            "not stop?&lt;/b&gt;&lt;/p&gt;"
            "&lt;p&gt;Without it the self-locking gate &lt;b&gt;goes to zero&lt;/b&gt; once "
            "&lt;code&gt;F_0&lt;/code&gt; reaches the floor: the rotational channel dies and the "
            "fixed point is absolute. With &lt;code&gt;r &amp;gt; 0&lt;/code&gt; the channel keeps a "
            "fraction of its own initial rate below threshold, turning the arrest from a "
            "barrier into a &lt;b&gt;knee&lt;/b&gt;. Physically: the self-locked "
            "Cattaneo&amp;ndash;Mindlin core is not rigid &amp;minus; it creeps under continued "
            "cycling.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Mechanism validated, adoption falsified&lt;/b&gt; (2026-08-15): it stays "
            "default-inert because the arrest was &lt;i&gt;one&lt;/i&gt; defect of that source, not "
            "the only one.&lt;/p&gt;"
        ),
        refs=["Cattaneo (1938) / Mindlin (1949) — partial slip", "Jiang et al. (2003) — two-stage loosening"]),
    VarSpec(name="loose_arrest_floor", symbol="F_min/F0", unit="-", group="loosening", category="form", context={"baseline":"transverse","overrides":{"loose_torsion_mode":"bolt_torsion","loosening_slip_coupling":"gross_fraction","k_tr_mode":"bending","eta_loose":8.0}}, sweep=(0,0.15,15,"lin"), related=["loose_torsion_mode"],
        equation="F_min = loose_arrest_floor*F_0_init;  g_arrest = max(0, 1 - F_min/F_0);  d_theta *= g_arrest  (stable fixed point at F_min)",
        physics_pt=(
            "&lt;p&gt;Quando o afrouxamento é do tipo runaway (o torque resistivo "
            "&lt;code&gt;T_resist&lt;/code&gt; cai proporcionalmente a &lt;code&gt;F_0&lt;/code&gt;, então quanto "
            "mais afrouxa mais fácil afrouxar), a curva desabaria até zero. Fisicamente "
            "isso não acontece: a zona de stick central do contato (Cattaneo-Mindlin) "
            "restaura o atrito estático da rosca e trava um clamp residual contra o "
            "off-torque da hélice. &lt;code&gt;loose_arrest_floor&lt;/code&gt; é esse piso, como "
            "fração da pré-carga inicial: &lt;code&gt;F_min = loose_arrest_floor&amp;middot;"
            "F_0_init&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Na equação o gate &lt;code&gt;g = max(0, 1 &amp;minus; F_min/F_0)&lt;/code&gt; multiplica "
            "&lt;code&gt;d_theta&lt;/code&gt;: o ratcheting só drena o EXCESSO acima de "
            "&lt;code&gt;F_min&lt;/code&gt;, então quando &lt;code&gt;F_0 &amp;rarr; F_min&lt;/code&gt; a rotação "
            "para. O runaway vira uma &lt;b&gt;S-curve com ponto fixo ESTÁVEL&lt;/b&gt; em "
            "&lt;code&gt;F_min&lt;/code&gt;. Subir o slider levanta o platô final da curva. O contexto "
            "liga o runaway (&lt;code&gt;bolt_torsion&lt;/code&gt; + &lt;code&gt;gross_fraction&lt;/code&gt; + "
            "&lt;code&gt;bending&lt;/code&gt;) para o arresto ser visível.&lt;/p&gt;"
            "&lt;p&gt;Lido do fim do dado (o platô residual), O(0.05&amp;ndash;0.10) por par. É o "
            "que torna o modo &lt;code&gt;bolt_torsion&lt;/code&gt; ADOTÁVEL &amp;minus; remove o over-collapse "
            "do #10 (&amp;sect;4.10). Opt-in, default 0 = OFF (sem arresto, runaway).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;When loosening is of the runaway type (the resisting torque "
            "&lt;code&gt;T_resist&lt;/code&gt; falls proportionally to &lt;code&gt;F_0&lt;/code&gt;, so the more "
            "it loosens the easier it loosens), the curve would collapse to zero. "
            "Physically it does not: the central stick zone of the contact "
            "(Cattaneo-Mindlin) restores static thread friction and locks a residual clamp "
            "against the helix off-torque. &lt;code&gt;loose_arrest_floor&lt;/code&gt; is that floor, "
            "as a fraction of the initial preload: &lt;code&gt;F_min = loose_arrest_floor"
            "&amp;middot;F_0_init&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;In the equation the gate &lt;code&gt;g = max(0, 1 &amp;minus; F_min/F_0)&lt;/code&gt; "
            "multiplies &lt;code&gt;d_theta&lt;/code&gt;: ratcheting only drains the EXCESS above "
            "&lt;code&gt;F_min&lt;/code&gt;, so when &lt;code&gt;F_0 &amp;rarr; F_min&lt;/code&gt; the rotation stops. "
            "The runaway becomes an &lt;b&gt;S-curve with a STABLE fixed point&lt;/b&gt; at "
            "&lt;code&gt;F_min&lt;/code&gt;. Raising the slider lifts the curve's final plateau. The "
            "context turns the runaway on (&lt;code&gt;bolt_torsion&lt;/code&gt; + "
            "&lt;code&gt;gross_fraction&lt;/code&gt; + &lt;code&gt;bending&lt;/code&gt;) so the arrest is "
            "visible.&lt;/p&gt;"
            "&lt;p&gt;Read from the tail of the data (the residual plateau), O(0.05&amp;ndash;0.10) "
            "per pair. It is what makes the &lt;code&gt;bolt_torsion&lt;/code&gt; mode ADOPTABLE &amp;minus; it "
            "removes the over-collapse of #10 (&amp;sect;4.10). Opt-in, default 0 = OFF (no arrest, "
            "runaway).&lt;/p&gt;"),
        refs=[("&amp;sect;6 &amp;minus; self_locking_gate (S-curve com ponto fixo F_min)",
               "&amp;sect;6 &amp;minus; self_locking_gate (S-curve with fixed point F_min)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.10 &amp;minus; arresto auto-travante (#10 adotável; remove o over-collapse)",
               "&amp;sect;4.10 &amp;minus; self-locking arrest (#10 adoptable; removes over-collapse)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="loosening_slip_coupling", symbol="", unit="", group="loosening", category="mode", context={"baseline":"transverse","overrides":{"k_tr_mode":"bending"}}, choices=["off","gross_fraction"], related=["k_tr_mode"],
        equation='g_loose = slip/(slip + delta_t)  ("gross_fraction")  |  g_loose = 1  ("off");  delta_t = F_slip/k_tr',
        physics_pt=(
            "&lt;p&gt;Este seletor decide COMO o afrouxamento rotacional le o regime de "
            "escorregamento. O afrouxamento tipo Junker exige GROSS slip (o curso completo "
            "desliza e a porca ratcheteia); em partial slip (a zona central fica em stick) "
            "o backing-off é suprimido.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;off&lt;/b&gt; (default): o afrouxamento usa o critério de força puro (dispara "
            "quando &lt;code&gt;T_loose &amp;gt; T_resist&lt;/code&gt;), backward-compat bit-identical. "
            "&lt;b&gt;gross_fraction&lt;/b&gt;: multiplica a rotação pela fração de gross-slip do "
            "curso &lt;code&gt;g = slip/(slip + &amp;delta;_t)&lt;/code&gt;, com &lt;code&gt;&amp;delta;_t = "
            "F_slip/k_tr&lt;/code&gt; o take-up até o início do escorregamento. O seletor troca "
            "entre as duas curvas pré-computadas.&lt;/p&gt;"
            "&lt;p&gt;Só faz sentido com &lt;code&gt;k_tr_mode = bending&lt;/code&gt; (senão &lt;code&gt;&amp;delta;_t "
            "&amp;asymp; 0&lt;/code&gt; e &lt;code&gt;g &amp;asymp; 1&lt;/code&gt;, sem efeito); por isso o contexto "
            "liga o modo bending. Opt-in (spec 2026-07-06).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This selector decides HOW the rotational loosening reads the slip regime. "
            "Junker-type loosening requires GROSS slip (the full stroke slides and the nut "
            "ratchets); in partial slip (the central zone stays stuck) the backing-off is "
            "suppressed.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;off&lt;/b&gt; (default): loosening uses the pure force criterion (fires when "
            "&lt;code&gt;T_loose &amp;gt; T_resist&lt;/code&gt;), backward-compat bit-identical. "
            "&lt;b&gt;gross_fraction&lt;/b&gt;: multiplies the rotation by the gross-slip fraction of "
            "the stroke &lt;code&gt;g = slip/(slip + &amp;delta;_t)&lt;/code&gt;, with &lt;code&gt;&amp;delta;_t = "
            "F_slip/k_tr&lt;/code&gt; the take-up up to slip onset. The selector switches between "
            "the two pre-computed curves.&lt;/p&gt;"
            "&lt;p&gt;It only makes sense with &lt;code&gt;k_tr_mode = bending&lt;/code&gt; (otherwise "
            "&lt;code&gt;&amp;delta;_t &amp;asymp; 0&lt;/code&gt; and &lt;code&gt;g &amp;asymp; 1&lt;/code&gt;, no effect); "
            "that is why the context enables the bending mode. Opt-in (spec 2026-07-06).&lt;/p&gt;"),
        refs=[("&amp;sect;5.1 &amp;minus; loosening gateado pela fração de gross-slip",
               "&amp;sect;5.1 &amp;minus; loosening gated by gross-slip fraction", "MODEL_MATH_REFERENCE.md"),
              ("Junker (1969) &amp;minus; ratcheting exige gross slip",
               "Junker (1969) &amp;minus; ratcheting requires gross slip", "junker1969")]),

    VarSpec(name="loose_torsion_mode", symbol="", unit="", group="loosening", category="mode", context={"baseline":"transverse","overrides":{"loosening_slip_coupling":"gross_fraction","k_tr_mode":"bending","eta_loose":8.0}}, choices=["legacy","bolt_torsion"], related=["eta_loose"],
        equation='k_torsional = k_j_init*d_2/2  ("legacy")  |  eta_loose*G*J/L_eff, J=pi*d_2^4/32  ("bolt_torsion");  d_theta = gates*slip_fraction*(T_loose-T_resist)/k_torsional',
        physics_pt=(
            "&lt;p&gt;A rotação de afrouxamento por ciclo é o excesso de torque dividido pela "
            "rigidez torsional: &lt;code&gt;d_theta &amp;prop; (T_loose &amp;minus; T_resist)/"
            "k_torsional&lt;/code&gt;. Este seletor escolhe COMO &lt;code&gt;k_torsional&lt;/code&gt; é "
            "calculada.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;legacy&lt;/b&gt; (default): &lt;code&gt;k_torsional = k_j_init&amp;middot;d_2/2 &amp;asymp; "
            "2e7&lt;/code&gt; N&amp;middot;m/rad (rigidez GW da junta escalada) &amp;minus; enorme, então a "
            "rotação por ciclo é minúscula; backward-compat bit-identical. "
            "&lt;b&gt;bolt_torsion&lt;/b&gt;: usa a rigidez torsional FÍSICA do corpo do parafuso, "
            "&lt;code&gt;k_torsional = eta_loose&amp;middot;G&amp;middot;J/L_eff&lt;/code&gt; com &lt;code&gt;J = "
            "&amp;pi;&amp;middot;d_2^4/32&lt;/code&gt; (&amp;asymp; 4e3, ~5000x menor) &amp;rarr; um dado excesso "
            "de torque produz muito mais rotação, e o runaway &lt;code&gt;T_resist &amp;prop; "
            "F_0&lt;/code&gt; que já existe no modelo consegue disparar.&lt;/p&gt;"
            "&lt;p&gt;Só faz sentido com o gate de onset ligado (&lt;code&gt;gross_fraction&lt;/code&gt; + "
            "&lt;code&gt;bending&lt;/code&gt;), senão dispara em toda junta que escorrega; o contexto "
            "liga esses companheiros. É a forma do roadmap #10 / &amp;sect;4.8 (member-stiffness). "
            "Opt-in.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The per-cycle loosening rotation is the torque excess divided by the "
            "torsional stiffness: &lt;code&gt;d_theta &amp;prop; (T_loose &amp;minus; T_resist)/"
            "k_torsional&lt;/code&gt;. This selector chooses HOW &lt;code&gt;k_torsional&lt;/code&gt; is "
            "computed.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;legacy&lt;/b&gt; (default): &lt;code&gt;k_torsional = k_j_init&amp;middot;d_2/2 &amp;asymp; "
            "2e7&lt;/code&gt; N&amp;middot;m/rad (scaled joint GW stiffness) &amp;minus; huge, so the per-cycle "
            "rotation is tiny; backward-compat bit-identical. &lt;b&gt;bolt_torsion&lt;/b&gt;: uses the "
            "PHYSICAL torsional stiffness of the bolt shank, &lt;code&gt;k_torsional = "
            "eta_loose&amp;middot;G&amp;middot;J/L_eff&lt;/code&gt; with &lt;code&gt;J = &amp;pi;&amp;middot;"
            "d_2^4/32&lt;/code&gt; (&amp;asymp; 4e3, ~5000x smaller) &amp;rarr; a given torque excess "
            "produces much more rotation, and the runaway &lt;code&gt;T_resist &amp;prop; F_0&lt;/code&gt; "
            "that already exists in the model can fire.&lt;/p&gt;"
            "&lt;p&gt;It only makes sense with the onset gate on (&lt;code&gt;gross_fraction&lt;/code&gt; + "
            "&lt;code&gt;bending&lt;/code&gt;), otherwise it fires on every slipping joint; the context "
            "enables those companions. It is the roadmap #10 / &amp;sect;4.8 form "
            "(member-stiffness). Opt-in.&lt;/p&gt;"),
        refs=[("&amp;sect;5.1 (#10) &amp;minus; rigidez torsional do loosening (legacy vs bolt_torsion)",
               "&amp;sect;5.1 (#10) &amp;minus; loosening torsional stiffness (legacy vs bolt_torsion)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.10 member-stiffness &amp;minus; runaway T_resist prop F_0",
               "&amp;sect;4.10 member-stiffness &amp;minus; runaway T_resist prop F_0", "MODEL_LEGITIMACY.md")]),

    VarSpec(name="eta_loose", symbol="eta_loose", unit="-", group="loosening", category="form", context={"baseline":"transverse","overrides":{"loose_torsion_mode":"bolt_torsion","loosening_slip_coupling":"gross_fraction","k_tr_mode":"bending"}}, sweep=(1.0,15.0,15,"lin"), related=["loose_torsion_mode"],
        equation="k_torsional = eta_loose*G*J/L_eff  (bolt_torsion only);  J = pi*d_2^4/32,  G = 77e9 Pa",
        physics_pt=(
            "&lt;p&gt;No modo &lt;code&gt;bolt_torsion&lt;/code&gt;, &lt;code&gt;eta_loose&lt;/code&gt; é a eficiência "
            "efetiva de travamento torsional que escala a rigidez &lt;code&gt;k_torsional = "
            "eta_loose&amp;middot;G&amp;middot;J/L_eff&lt;/code&gt;. O corpo nu do parafuso "
            "(&lt;code&gt;eta = 1&lt;/code&gt;) colapsa rápido demais (~25 ciclos); o auto-travamento "
            "real da rosca mais a restrição do membro elevam a rigidez torsional efetiva, "
            "e &lt;code&gt;eta &amp;asymp; 7&amp;ndash;15&lt;/code&gt; estica o colapso até o observado (~180 "
            "ciclos).&lt;/p&gt;"
            "&lt;p&gt;Subir o slider enrijece a resposta torsional &amp;rarr; menos rotação por "
            "ciclo &amp;rarr; o colapso demora mais. Só é lido em &lt;code&gt;bolt_torsion&lt;/code&gt; "
            "(ignorado em &lt;code&gt;legacy&lt;/code&gt;, onde o default é irrelevante); por isso o "
            "contexto liga &lt;code&gt;bolt_torsion&lt;/code&gt; + os gates de onset.&lt;/p&gt;"
            "&lt;p&gt;É uma constante por par, O(1&amp;ndash;10), análoga a &lt;code&gt;tr_loose_gain&lt;/code&gt; "
            "&amp;minus; uma escala per-rig com proveniência pendente, não uma forma. Opt-in (spec "
            "2026-07-07).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;In &lt;code&gt;bolt_torsion&lt;/code&gt; mode, &lt;code&gt;eta_loose&lt;/code&gt; is the effective "
            "torsional locking efficiency that scales the stiffness &lt;code&gt;k_torsional = "
            "eta_loose&amp;middot;G&amp;middot;J/L_eff&lt;/code&gt;. The bare bolt shank "
            "(&lt;code&gt;eta = 1&lt;/code&gt;) collapses too fast (~25 cycles); the real thread "
            "self-locking plus member restraint raise the effective torsional stiffness, "
            "and &lt;code&gt;eta &amp;asymp; 7&amp;ndash;15&lt;/code&gt; stretches the collapse out to the "
            "observed value (~180 cycles).&lt;/p&gt;"
            "&lt;p&gt;Raising the slider stiffens the torsional response &amp;rarr; less rotation per "
            "cycle &amp;rarr; the collapse takes longer. It is only read in "
            "&lt;code&gt;bolt_torsion&lt;/code&gt; (ignored in &lt;code&gt;legacy&lt;/code&gt;, where the default "
            "is irrelevant); that is why the context enables &lt;code&gt;bolt_torsion&lt;/code&gt; + "
            "the onset gates.&lt;/p&gt;"
            "&lt;p&gt;It is a per-pair constant, O(1&amp;ndash;10), analogous to "
            "&lt;code&gt;tr_loose_gain&lt;/code&gt; &amp;minus; a per-rig scale with pending provenance, not a "
            "form. Opt-in (spec 2026-07-07).&lt;/p&gt;"),
        refs=[("&amp;sect;5.1 &amp;minus; eficiência de travamento torsional (só bolt_torsion)",
               "&amp;sect;5.1 &amp;minus; torsional locking efficiency (bolt_torsion only)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.10 member-stiffness &amp;minus; eta estica o colapso ~25-&gt;180 ciclos",
               "&amp;sect;4.10 member-stiffness &amp;minus; eta stretches collapse ~25-&gt;180 cycles",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="c_bend", symbol="c_bend", unit="-", group="slip_regime", category="form", context={"baseline":"transverse","overrides":{"k_tr_mode":"bending"}}, sweep=(0.2,3.0,15,"lin"), related=["k_tr_mode"],
        equation="k_tr = c_bend*E*I/L_eff^3,  I = pi*d_2^4/64  (k_tr_mode=bending);  delta_t = F_slip/k_tr",
        physics_pt=(
            "&lt;p&gt;Quando &lt;code&gt;k_tr_mode = bending&lt;/code&gt;, a rigidez transversal de onset de "
            "slip vem da FLEXÃO do parafuso, &lt;code&gt;k_tr = c_bend&amp;middot;E&amp;middot;I/"
            "L_eff^3&lt;/code&gt; com &lt;code&gt;I = &amp;pi;&amp;middot;d_2^4/64&lt;/code&gt;. &lt;code&gt;c_bend&lt;/code&gt; "
            "é o fator adimensional de contorno/compliance que corrige a condição de "
            "contorno real do engaste (biengastado vs em balanço) e a complacência do "
            "membro.&lt;/p&gt;"
            "&lt;p&gt;Ele escala &lt;code&gt;k_tr&lt;/code&gt;, que fixa &lt;code&gt;&amp;delta;_t = F_slip/k_tr&lt;/code&gt; "
            "&amp;minus; o separador entre micro-slip e gross-slip. &lt;code&gt;c_bend&lt;/code&gt; maior &amp;rarr; "
            "junta mais rígida &amp;rarr; &lt;code&gt;&amp;delta;_t&lt;/code&gt; menor &amp;rarr; mais do curso "
            "vira gross slip &amp;rarr; afrouxamento mais rápido. É o parâmetro calibrado aos "
            "amplitude sweeps.&lt;/p&gt;"
            "&lt;p&gt;É o ÚNICO knob transversal do modelo (&amp;sect;4.35), per-rig; só atua em "
            "&lt;code&gt;bending&lt;/code&gt;, por isso o contexto liga esse modo. Opt-in (spec "
            "2026-07-05).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;When &lt;code&gt;k_tr_mode = bending&lt;/code&gt;, the transverse slip-onset stiffness "
            "comes from the bolt BENDING, &lt;code&gt;k_tr = c_bend&amp;middot;E&amp;middot;I/"
            "L_eff^3&lt;/code&gt; with &lt;code&gt;I = &amp;pi;&amp;middot;d_2^4/64&lt;/code&gt;. &lt;code&gt;c_bend&lt;/code&gt; "
            "is the dimensionless boundary/compliance factor that corrects for the real "
            "clamping boundary condition (fixed-fixed vs cantilever) and the member "
            "compliance.&lt;/p&gt;"
            "&lt;p&gt;It scales &lt;code&gt;k_tr&lt;/code&gt;, which sets &lt;code&gt;&amp;delta;_t = F_slip/k_tr&lt;/code&gt; "
            "&amp;minus; the separator between micro-slip and gross-slip. Larger &lt;code&gt;c_bend&lt;/code&gt; "
            "&amp;rarr; stiffer joint &amp;rarr; smaller &lt;code&gt;&amp;delta;_t&lt;/code&gt; &amp;rarr; more of the "
            "stroke becomes gross slip &amp;rarr; faster loosening. It is the parameter "
            "calibrated to the amplitude sweeps.&lt;/p&gt;"
            "&lt;p&gt;It is the ONLY transverse knob in the model (&amp;sect;4.35), per-rig; it acts only "
            "in &lt;code&gt;bending&lt;/code&gt;, which is why the context enables that mode. Opt-in "
            "(spec 2026-07-05).&lt;/p&gt;"),
        refs=[("&amp;sect;5.1 &amp;minus; k_tr por flexão do parafuso (E*I/L^3)",
               "&amp;sect;5.1 &amp;minus; bending-based k_tr (E*I/L^3)", "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.35 &amp;minus; c_bend é o único knob transversal (per-rig)",
               "&amp;sect;4.35 &amp;minus; c_bend is the only transverse knob (per-rig)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="slip_regime_mode", symbol="", unit="", group="slip_regime", category="mode", context={"baseline":"transverse","overrides":{"k_tr_mode":"bending"}}, choices=["off","cattaneo_mindlin"], related=["slip_capacity_coeff"],
        equation='r = Q/(mu*F_0*slip_capacity_coeff);  "off": all gates = 1  |  "cattaneo_mindlin": g_gross and g_partial active',
        physics_pt=(
            "&lt;p&gt;Um contato carregado sob força tangencial &lt;code&gt;Q&lt;/code&gt; não desliza como "
            "um bloco rígido: desenvolve uma zona central de STICK cercada por um anel de "
            "micro-slip, e só quando &lt;code&gt;Q&lt;/code&gt; atinge &lt;code&gt;&amp;mu;&amp;middot;F_0&lt;/code&gt; "
            "todo o contato entra em gross slip (contato de Cattaneo-Mindlin). A razão "
            "&lt;code&gt;r = Q/(&amp;mu;&amp;middot;F_0&amp;middot;&amp;kappa;)&lt;/code&gt; mede quão perto do gross "
            "slip está o contato.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;off&lt;/b&gt; (default): todos os gates = 1, backward-compat bit-identical. "
            "&lt;b&gt;cattaneo_mindlin&lt;/b&gt; liga TRÊS efeitos: (1) o afrouxamento passa a ser "
            "gateado pela fração de gross-slip afiada &lt;code&gt;g_gross&lt;/code&gt;; (2) wear e "
            "fretting são multiplicados pelo &lt;code&gt;partial_slip_gate&lt;/code&gt; (mais "
            "&lt;code&gt;F_0&lt;/code&gt; &amp;rarr; menor &lt;code&gt;r&lt;/code&gt; &amp;rarr; menos fretting, "
            "reproduzindo o slope do Liu2017); (3) habilita &lt;code&gt;k_partial_slip&lt;/code&gt; e "
            "&lt;code&gt;couple_famp_slip&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Opt-in; é a forma-mãe do regime de escorregamento (spec 2026-07-07). O "
            "seletor troca entre as duas curvas pré-computadas.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;A contact loaded by a tangential force &lt;code&gt;Q&lt;/code&gt; does not slide as a "
            "rigid block: it develops a central STICK zone surrounded by a micro-slip "
            "annulus, and only when &lt;code&gt;Q&lt;/code&gt; reaches &lt;code&gt;&amp;mu;&amp;middot;F_0&lt;/code&gt; "
            "does the whole contact enter gross slip (Cattaneo-Mindlin contact). The ratio "
            "&lt;code&gt;r = Q/(&amp;mu;&amp;middot;F_0&amp;middot;&amp;kappa;)&lt;/code&gt; measures how close the "
            "contact is to gross slip.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;off&lt;/b&gt; (default): all gates = 1, backward-compat bit-identical. "
            "&lt;b&gt;cattaneo_mindlin&lt;/b&gt; turns on THREE effects: (1) loosening becomes gated by "
            "the sharpened gross-slip fraction &lt;code&gt;g_gross&lt;/code&gt;; (2) wear and fretting "
            "are multiplied by the &lt;code&gt;partial_slip_gate&lt;/code&gt; (higher &lt;code&gt;F_0&lt;/code&gt; "
            "&amp;rarr; lower &lt;code&gt;r&lt;/code&gt; &amp;rarr; less fretting, reproducing the Liu2017 "
            "slope); (3) it enables &lt;code&gt;k_partial_slip&lt;/code&gt; and "
            "&lt;code&gt;couple_famp_slip&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Opt-in; it is the parent form of the slip regime (spec 2026-07-07). The "
            "selector switches between the two pre-computed curves.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 &amp;minus; regime Cattaneo-Mindlin (partial/gross slip)",
               "&amp;sect;5.2 &amp;minus; Cattaneo-Mindlin regime (partial/gross slip)",
               "MODEL_MATH_REFERENCE.md"),
              ("Cattaneo (1938) / Mindlin (1949) &amp;minus; contato tangencial",
               "Cattaneo (1938) / Mindlin (1949) &amp;minus; tangential contact", "cattaneo_mindlin")]),

    VarSpec(name="slip_regime_sharpness", symbol="k_sr", unit="-", group="slip_regime", category="form", context={"baseline":"transverse","overrides":{"slip_regime_mode":"cattaneo_mindlin","k_tr_mode":"bending","loosening_slip_coupling":"gross_fraction"}}, sweep=(0.5,4.0,15,"lin"), related=["slip_regime_mode"],
        equation="g_gross = (slip/(slip + delta_t))^slip_regime_sharpness",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;slip_regime_sharpness&lt;/code&gt; é o expoente &lt;code&gt;k&lt;/code&gt; na fração de "
            "gross-slip que gateia o afrouxamento: &lt;code&gt;g_gross = (slip/(slip + &amp;delta;_t)"
            ")^k&lt;/code&gt;. Ele afia a transição stick&amp;rarr;slip vista pelo afrouxamento "
            "rotacional.&lt;/p&gt;"
            "&lt;p&gt;Com &lt;code&gt;k = 1&lt;/code&gt; reproduz a fração de gross-slip linear atual; "
            "&lt;code&gt;k &amp;gt; 1&lt;/code&gt; suprime o partial slip, de modo que só o gross slip "
            "profundo afrouxa (Rousseau: passo fino colapsa, passo grosso trava). Subir o "
            "slider adia o afrouxamento para cursos mais profundos e agucha o joelho da "
            "curva. Só é lido com &lt;code&gt;slip_regime_mode = cattaneo_mindlin&lt;/code&gt;, por "
            "isso o contexto liga o modo CM.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;slip_regime_sharpness&lt;/code&gt; is the exponent &lt;code&gt;k&lt;/code&gt; in the "
            "gross-slip fraction that gates loosening: &lt;code&gt;g_gross = (slip/(slip + "
            "&amp;delta;_t))^k&lt;/code&gt;. It sharpens the stick&amp;rarr;slip transition seen by the "
            "rotational loosening.&lt;/p&gt;"
            "&lt;p&gt;With &lt;code&gt;k = 1&lt;/code&gt; it reproduces the current linear gross-slip "
            "fraction; &lt;code&gt;k &amp;gt; 1&lt;/code&gt; suppresses partial slip so only deep gross "
            "slip loosens (Rousseau: fine pitch collapses, coarse pitch locks). Raising the "
            "slider delays loosening to deeper strokes and sharpens the curve's knee. It is "
            "only read with &lt;code&gt;slip_regime_mode = cattaneo_mindlin&lt;/code&gt;, which is why "
            "the context enables the CM mode.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 / loosening_slip_gate &amp;minus; expoente da fração de gross-slip",
               "&amp;sect;5.2 / loosening_slip_gate &amp;minus; gross-slip fraction exponent",
               "MODEL_MATH_REFERENCE.md"),
              ("Cattaneo-Mindlin &amp;minus; transição stick-&gt;gross slip",
               "Cattaneo-Mindlin &amp;minus; stick-&gt;gross slip transition", "cattaneo_mindlin")]),

    VarSpec(name="slip_capacity_coeff", symbol="c_cap", unit="-", group="slip_regime", category="form", context={"baseline":"transverse","overrides":{"slip_regime_mode":"cattaneo_mindlin"}}, sweep=(0.3,3.0,15,"lin"), related=["slip_regime_mode"], negligible=True,
        equation="r = Q/(mu*F_0*slip_capacity_coeff);  g_partial = 1 - (1 - min(r,1))^partial_slip_exp",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;slip_capacity_coeff&lt;/code&gt; é o coeficiente &lt;code&gt;&amp;kappa;&lt;/code&gt; que "
            "escala a capacidade tangencial &lt;code&gt;&amp;mu;&amp;middot;F_0&lt;/code&gt; em que o contato "
            "satura em gross slip &amp;minus; na prática, quanto curso de stick o contato aguenta "
            "antes de deslizar por inteiro. Entra na razão de slip &lt;code&gt;r = Q/(&amp;mu;"
            "&amp;middot;F_0&amp;middot;&amp;kappa;)&lt;/code&gt; do &lt;code&gt;partial_slip_gate&lt;/code&gt; para wear "
            "e fretting.&lt;/p&gt;"
            "&lt;p&gt;&lt;code&gt;&amp;kappa;&lt;/code&gt; maior &amp;rarr; &lt;code&gt;r&lt;/code&gt; menor &amp;rarr; mais partial "
            "slip &amp;rarr; menos perda de pré-carga dirigida por wear/fretting; &lt;code&gt;"
            "g_partial = 1 &amp;minus; (1 &amp;minus; min(r,1))^partial_slip_exp&lt;/code&gt;. Só atua "
            "com &lt;code&gt;slip_regime_mode = cattaneo_mindlin&lt;/code&gt;, por isso o contexto liga "
            "o modo CM.&lt;/p&gt;"
            "&lt;p&gt;Faz parte do conjunto FROZEN_S_ZERO (&amp;sect;4.42c): a sensibilidade &lt;code&gt;S "
            "&amp;asymp; 0&lt;/code&gt; no dataset atual, então é CONGELADA por proveniência "
            "(não-fittavel; &lt;code&gt;active_candidates&lt;/code&gt; levanta erro se oferecida ao "
            "otimizador). Participa da física, mas o dado não a identifica &amp;minus; por isso o "
            "slider quase não move a curva.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;slip_capacity_coeff&lt;/code&gt; is the coefficient &lt;code&gt;&amp;kappa;&lt;/code&gt; "
            "that scales the tangential capacity &lt;code&gt;&amp;mu;&amp;middot;F_0&lt;/code&gt; at which the "
            "contact saturates into gross slip &amp;minus; in practice, how much stick stroke the "
            "contact can take before it slides entirely. It enters the slip ratio &lt;code&gt;r "
            "= Q/(&amp;mu;&amp;middot;F_0&amp;middot;&amp;kappa;)&lt;/code&gt; of the &lt;code&gt;partial_slip_gate&lt;/code&gt; "
            "for wear and fretting.&lt;/p&gt;"
            "&lt;p&gt;Larger &lt;code&gt;&amp;kappa;&lt;/code&gt; &amp;rarr; smaller &lt;code&gt;r&lt;/code&gt; &amp;rarr; more "
            "partial slip &amp;rarr; less wear/fretting-driven preload loss; &lt;code&gt;g_partial = "
            "1 &amp;minus; (1 &amp;minus; min(r,1))^partial_slip_exp&lt;/code&gt;. It only acts with "
            "&lt;code&gt;slip_regime_mode = cattaneo_mindlin&lt;/code&gt;, which is why the context "
            "enables the CM mode.&lt;/p&gt;"
            "&lt;p&gt;It belongs to the FROZEN_S_ZERO set (&amp;sect;4.42c): its sensitivity is &lt;code&gt;S "
            "&amp;asymp; 0&lt;/code&gt; on the current dataset, so it is FROZEN by provenance "
            "(non-fittable; &lt;code&gt;active_candidates&lt;/code&gt; raises if it is offered to the "
            "optimizer). It participates in the physics, but the data does not identify "
            "it &amp;minus; hence the slider barely moves the curve.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 partial_slip_gate &amp;minus; capacidade kappa do contato",
               "&amp;sect;5.2 partial_slip_gate &amp;minus; contact capacity kappa", "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.42c FROZEN_S_ZERO &amp;minus; S~0, congelada por proveniência",
               "&amp;sect;4.42c FROZEN_S_ZERO &amp;minus; S~0, frozen by provenance", "MODEL_LEGITIMACY.md")]),

    VarSpec(name="partial_slip_exp", symbol="n_ps", unit="-", group="slip_regime", category="form", context={"baseline":"transverse","overrides":{"slip_regime_mode":"cattaneo_mindlin","k_partial_slip":0.5}}, sweep=(0.5,3.0,15,"lin"), related=["k_partial_slip"], negligible=True,
        equation="g_partial = 1 - (1 - min(r,1))^partial_slip_exp,  r = Q/(mu*F_0*kappa)",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;partial_slip_exp&lt;/code&gt; é o expoente &lt;code&gt;m&lt;/code&gt; da fração de "
            "energia de partial slip do anel de micro-slip de Cattaneo-Mindlin: &lt;code&gt;"
            "g_partial = 1 &amp;minus; (1 &amp;minus; min(r,1))^m&lt;/code&gt;, com &lt;code&gt;r = Q/(&amp;mu;"
            "&amp;middot;F_0&amp;middot;&amp;kappa;)&lt;/code&gt;. Ele governa quão rápido o desgaste/"
            "dissipação do anel de micro-slip cresce conforme o contato se aproxima do "
            "gross slip.&lt;/p&gt;"
            "&lt;p&gt;Esse gate multiplica o &lt;code&gt;dF_0&lt;/code&gt; de wear e fretting e também "
            "alimenta a energia &lt;code&gt;dE_partial&lt;/code&gt;; &lt;code&gt;m&lt;/code&gt; maior torna o onset "
            "mais abrupto. O contexto liga &lt;code&gt;cattaneo_mindlin&lt;/code&gt; e &lt;code&gt;"
            "k_partial_slip = 0.5&lt;/code&gt; para o efeito ser visível na curva.&lt;/p&gt;"
            "&lt;p&gt;Como &lt;code&gt;slip_capacity_coeff&lt;/code&gt;, é do conjunto FROZEN_S_ZERO "
            "(&amp;sect;4.42c): &lt;code&gt;S &amp;asymp; 0&lt;/code&gt; no dataset, congelada por proveniência "
            "(não-fittavel). É física, mas não identificável aqui &amp;minus; o slider quase não "
            "move a curva.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;partial_slip_exp&lt;/code&gt; is the exponent &lt;code&gt;m&lt;/code&gt; of the "
            "partial-slip energy fraction of the Cattaneo-Mindlin micro-slip annulus: "
            "&lt;code&gt;g_partial = 1 &amp;minus; (1 &amp;minus; min(r,1))^m&lt;/code&gt;, with &lt;code&gt;r = "
            "Q/(&amp;mu;&amp;middot;F_0&amp;middot;&amp;kappa;)&lt;/code&gt;. It governs how fast the "
            "wear/dissipation of the micro-slip annulus grows as the contact approaches "
            "gross slip.&lt;/p&gt;"
            "&lt;p&gt;That gate multiplies the wear and fretting &lt;code&gt;dF_0&lt;/code&gt; and also feeds "
            "the &lt;code&gt;dE_partial&lt;/code&gt; energy; larger &lt;code&gt;m&lt;/code&gt; makes the onset more "
            "abrupt. The context enables &lt;code&gt;cattaneo_mindlin&lt;/code&gt; and &lt;code&gt;"
            "k_partial_slip = 0.5&lt;/code&gt; so the effect is visible on the curve.&lt;/p&gt;"
            "&lt;p&gt;Like &lt;code&gt;slip_capacity_coeff&lt;/code&gt;, it is in the FROZEN_S_ZERO set "
            "(&amp;sect;4.42c): &lt;code&gt;S &amp;asymp; 0&lt;/code&gt; on the dataset, frozen by provenance "
            "(non-fittable). It is physical, but not identifiable here &amp;minus; the slider "
            "barely moves the curve.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 partial_slip_gate &amp;minus; expoente m (anel de micro-slip)",
               "&amp;sect;5.2 partial_slip_gate &amp;minus; exponent m (micro-slip annulus)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.42c FROZEN_S_ZERO &amp;minus; S~0, congelada por proveniência",
               "&amp;sect;4.42c FROZEN_S_ZERO &amp;minus; S~0, frozen by provenance", "MODEL_LEGITIMACY.md")]),

    VarSpec(name="couple_famp_slip", symbol="", unit="", group="slip_regime", category="mode", context={"baseline":"transverse","overrides":{"slip_regime_mode":"cattaneo_mindlin"}}, choices=[False,True], related=[],
        equation="F_amp_eff = min(F_amp, mu*F_0)  (gross-slip Coulomb saturation, disp-mode)",
        physics_pt=(
            "&lt;p&gt;Em disp-mode o deslocamento imposto e a força transversal de excitação "
            "(&lt;code&gt;F_amp&lt;/code&gt;) são, hoje, setados de forma INDEPENDENTE. Fisicamente, "
            "uma vez que o contato atinge gross slip, a força transversal satura no atrito "
            "de Coulomb &lt;code&gt;&amp;mu;&amp;middot;F_0&lt;/code&gt; e não pode exceder isso.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;False&lt;/b&gt; (default): &lt;code&gt;F_amp&lt;/code&gt; e &lt;code&gt;delta_amp&lt;/code&gt; "
            "independentes, backward-compat. &lt;b&gt;True&lt;/b&gt;: limita a força transversal "
            "motriz do afrouxamento a &lt;code&gt;min(F_amp, &amp;mu;&amp;middot;F_0)&lt;/code&gt; em gross "
            "slip &amp;rarr; o drive fica atado a &lt;code&gt;F_0&lt;/code&gt;. Só é ativo com &lt;code&gt;"
            "slip_regime_mode = cattaneo_mindlin&lt;/code&gt;, por isso o contexto liga o modo "
            "CM.&lt;/p&gt;"
            "&lt;p&gt;É o acoplamento do roadmap #4. Opt-in; o seletor troca entre as duas curvas "
            "pré-computadas.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;In disp-mode the imposed displacement and the transverse excitation force "
            "(&lt;code&gt;F_amp&lt;/code&gt;) are, today, set INDEPENDENTLY. Physically, once the "
            "contact reaches gross slip, the transverse force saturates at the Coulomb "
            "friction &lt;code&gt;&amp;mu;&amp;middot;F_0&lt;/code&gt; and cannot exceed it.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;False&lt;/b&gt; (default): &lt;code&gt;F_amp&lt;/code&gt; and &lt;code&gt;delta_amp&lt;/code&gt; "
            "independent, backward-compat. &lt;b&gt;True&lt;/b&gt;: caps the loosening driving "
            "transverse force at &lt;code&gt;min(F_amp, &amp;mu;&amp;middot;F_0)&lt;/code&gt; in gross slip "
            "&amp;rarr; the drive becomes tied to &lt;code&gt;F_0&lt;/code&gt;. It is only active with "
            "&lt;code&gt;slip_regime_mode = cattaneo_mindlin&lt;/code&gt;, which is why the context "
            "enables the CM mode.&lt;/p&gt;"
            "&lt;p&gt;It is the roadmap #4 coupling. Opt-in; the selector switches between the "
            "two pre-computed curves.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 (#4) &amp;minus; saturação de Coulomb F_amp&amp;lt;=mu*F_0 em gross slip",
               "&amp;sect;5.2 (#4) &amp;minus; Coulomb saturation F_amp&amp;lt;=mu*F_0 in gross slip",
               "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="k_partial_slip", symbol="k_ps", unit="-", group="slip_regime", category="form", context={"baseline":"transverse","overrides":{}}, sweep=(0,2.0,15,"lin"), related=["partial_slip_exp"], negligible=True,
        equation="dE_partial = k_partial_slip * g_partial * 4 * mu_bearing_eff * F_0 * delta_t;  delta_t = F_slip/k_tr",
        physics_pt=(
            "&lt;p&gt;Mesmo sem gross slip, o anel de micro-slip de Cattaneo-Mindlin dissipa "
            "energia a cada ciclo (o loop de histerese fechado). &lt;code&gt;k_partial_slip&lt;/code&gt; "
            "escala essa energia de partial slip por ciclo: &lt;code&gt;dE_partial = "
            "k_partial_slip&amp;middot;g_partial&amp;middot;4&amp;middot;&amp;mu;_bearing_eff&amp;middot;F_0"
            "&amp;middot;&amp;delta;_t&lt;/code&gt;, com &lt;code&gt;&amp;delta;_t = F_slip/k_tr&lt;/code&gt; a amplitude "
            "do micro-slip.&lt;/p&gt;"
            "&lt;p&gt;Ela NÃO tem &lt;code&gt;dF_0&lt;/code&gt; direto (a pré-carga fica intocada); entra no "
            "DRIVER do dano (então &lt;code&gt;D&lt;/code&gt; cresce durante o platô e dispara o joelho "
            "tardio, resolvendo o &amp;sect;4.31 do Bauer) e no budget de energia (fecha os loops de "
            "histerese que mediam 7&amp;ndash;8x o modelo, &amp;sect;4.25). &lt;b&gt;Nesta curva-padrão NÃO há "
            "dano ativo&lt;/b&gt; (c_D=0), então a energia de partial-slip não realimenta F/F0 e o "
            "slider fica praticamente parado &amp;minus; por isso a página é marcada como "
            "negligível.&lt;/p&gt;"
            "&lt;p&gt;Para ver o efeito na curva é preciso &lt;code&gt;slip_regime_mode=cattaneo_mindlin&lt;/code&gt; "
            "E dano ligado (c_D&amp;gt;0). Opt-in, default 0 = OFF exato (dupla falsificação "
            "&amp;sect;4.25 + &amp;sect;4.31).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Even without gross slip, the Cattaneo-Mindlin micro-slip annulus dissipates "
            "energy every cycle (the closed hysteresis loop). &lt;code&gt;k_partial_slip&lt;/code&gt; "
            "scales that per-cycle partial-slip energy: &lt;code&gt;dE_partial = k_partial_slip"
            "&amp;middot;g_partial&amp;middot;4&amp;middot;&amp;mu;_bearing_eff&amp;middot;F_0&amp;middot;"
            "&amp;delta;_t&lt;/code&gt;, with &lt;code&gt;&amp;delta;_t = F_slip/k_tr&lt;/code&gt; the micro-slip "
            "amplitude.&lt;/p&gt;"
            "&lt;p&gt;It has NO direct &lt;code&gt;dF_0&lt;/code&gt; (preload is untouched); it enters the "
            "damage DRIVER (so &lt;code&gt;D&lt;/code&gt; grows during the plateau and triggers the "
            "late knee, resolving Bauer's &amp;sect;4.31) and the energy budget (it closes the "
            "hysteresis loops that measured 7&amp;ndash;8x the model, &amp;sect;4.25). &lt;b&gt;On this "
            "standard curve there is NO active damage&lt;/b&gt; (c_D=0), so the partial-slip energy "
            "does not feed back into F/F0 and the slider is essentially still &amp;minus; hence the "
            "page is marked negligible.&lt;/p&gt;"
            "&lt;p&gt;To see the curve effect you need &lt;code&gt;slip_regime_mode=cattaneo_mindlin&lt;/code&gt; "
            "AND damage on (c_D&amp;gt;0). Opt-in, default 0 = exact OFF (double falsification "
            "&amp;sect;4.25 + &amp;sect;4.31).&lt;/p&gt;"),
        refs=[("&amp;sect;6 (&amp;sect;4.25/&amp;sect;4.31) &amp;minus; energia dE_partial do anel de micro-slip",
               "&amp;sect;6 (&amp;sect;4.25/&amp;sect;4.31) &amp;minus; dE_partial micro-slip annulus energy",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.25 loops Rousseau + &amp;sect;4.31 joelho Bauer (dupla falsificação)",
               "&amp;sect;4.25 Rousseau loops + &amp;sect;4.31 Bauer knee (double falsification)",
               "MODEL_LEGITIMACY.md")]),
])

# =============================== RATCHET / GRADED LOOSENING (7) ===============================
VARIABLE_SPECS.extend([
    VarSpec(name="k_ratchet", symbol="k_ratchet", unit="-", group="ratchet", category="form", context={"baseline":"transverse","overrides":{}}, sweep=(0,2.0,15,"lin"), related=["delta_free"],
        equation="Delta_theta += gates * k_ratchet * 4*slip/(d_2/2)   (aditivo; * slip_fraction se ratchet_torque_coupled)",
        physics_pt=(
            "&lt;p&gt;Num ensaio tipo Junker a porca não começa a afrouxar apenas quando o torque de "
            "afrouxamento vence o de resistência: a cada ciclo de escorregamento transversal ela "
            "avança uma FRAÇÃO do caminho de gross-slip, como uma catraca (ratchet). O parâmetro "
            "&lt;code&gt;k_ratchet&lt;/code&gt; é essa fração &amp;minus; quanto do caminho de slip por ciclo se converte "
            "em rotação de afrouxamento.&lt;/p&gt;"
            "&lt;p&gt;No modelo ele entra como um termo ADITIVO a rotação por ciclo, &amp;Delta;&amp;theta; += "
            "gates &amp;times; k_ratchet &amp;times; 4&amp;middot;slip/(d_2/2), convertendo a distância de slip "
            "em rotação no raio de passo. Isso dá ao afrouxamento a proporcionalidade com a "
            "AMPLITUDE que o drive de torque assumido (F_amp) não possui &amp;minus; o diagnóstico do Lu2024 "
            "mostra T_loose/T_resist ~ 1.57 fixo para toda amplitude, enquanto o dado colapsa com a "
            "amplitude. Mover o slider acelera o colapso dirigido pelo caminho de slip; em 0 o termo "
            "desaparece.&lt;/p&gt;"
            "&lt;p&gt;É uma forma opt-in, default-inerte: &lt;code&gt;k_ratchet=0&lt;/code&gt; deixa o engine "
            "bit-idêntico ao kernel de torque puro. Representa um REGIME de colapso distinto do "
            "runaway por excesso de torque (dois regimes de colapso, &amp;sect;4.15). Só age "
            "em disp-mode (o slip vem do curso imposto) e além do onset T_loose &amp;gt; T_resist. "
            "Per-par, O(0.005-0.1).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;In a Junker-type test the nut does not begin to loosen only once the loosening "
            "torque beats the resisting torque: on every transverse slip cycle it advances a "
            "FRACTION of the gross-slip path, like a ratchet. The parameter &lt;code&gt;k_ratchet&lt;/code&gt; "
            "is that fraction &amp;minus; how much of the per-cycle slip path turns into loosening rotation.&lt;/p&gt;"
            "&lt;p&gt;In the model it enters as an ADDITIVE term to the per-cycle rotation, &amp;Delta;&amp;theta; "
            "+= gates &amp;times; k_ratchet &amp;times; 4&amp;middot;slip/(d_2/2), converting slip distance into "
            "rotation at the pitch radius. This gives loosening the AMPLITUDE proportionality the "
            "assumed torque drive (F_amp) lacks &amp;minus; the Lu2024 diagnostic shows T_loose/T_resist ~ 1.57 "
            "fixed for every amplitude while the data collapses with amplitude. Moving the slider "
            "accelerates the slip-path-driven collapse; at 0 the term vanishes.&lt;/p&gt;"
            "&lt;p&gt;It is an opt-in, default-inert form: &lt;code&gt;k_ratchet=0&lt;/code&gt; leaves the engine "
            "bit-identical to the pure torque kernel. It represents a collapse REGIME distinct from "
            "the torque-excess runaway (two collapse regimes, &amp;sect;4.15). It acts only in "
            "disp-mode (slip from the imposed stroke) and beyond the onset T_loose &amp;gt; T_resist. "
            "Per-pair, O(0.005-0.1).&lt;/p&gt;"),
        refs=[("Diagnóstico Lu2024: T_loose/T_resist fixo vs colapso ~amplitude (ratcheting cinemático)",
               "Lu2024 diagnostic: fixed T_loose/T_resist vs amplitude-collapse (kinematic ratcheting)",
               "MODEL_LEGITIMACY.md 4.15"),
              ("&amp;sect;4.4 kernel de loosening (+ termo cinemático ratchet)",
               "&amp;sect;4.4 loosening kernel (+ kinematic ratchet term)", "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="loose_amp_exp", symbol="p_A", unit="-", group="ratchet", category="form", context={"baseline":"transverse","overrides":{"k_ratchet":0.05,"loose_arrest_floor":0.4,"loose_torsion_mode":"bolt_torsion","loosening_slip_coupling":"gross_fraction","k_tr_mode":"bending","eta_loose":8.0}}, sweep=(0.5,4.0,15,"lin"), related=["k_ratchet"],
        equation="d_theta += kin;   kin *= (slip / LOOSE_AMP_REF)^(loose_amp_exp - 1),   LOOSE_AMP_REF = 5e-4 m   (exp=1 => linear, bit-idêntico)",
        physics_pt=(
            "&lt;p&gt;O ratchet cinemático (&lt;code&gt;k_ratchet&lt;/code&gt;) converte o caminho de gross-slip em "
            "rotação de afrouxamento de forma LINEAR na amplitude: dobrar o slip por ciclo dobra o "
            "avanço por ciclo. Só que o dado de vida-vs-amplitude é muito mais íngreme que linear "
            "&amp;minus; Yang2023 mede o número de ciclos até a falha caindo como N &amp;prop; "
            "&amp;delta;^&amp;minus;3.8 com a amplitude. &lt;code&gt;loose_amp_exp&lt;/code&gt; é o expoente que "
            "confere ao termo cinemático essa não-linearidade de amplitude.&lt;/p&gt;"
            "&lt;p&gt;No modelo ele reescala o termo do ratchet por (slip/LOOSE_AMP_REF)^(exp&amp;minus;1), "
            "com a escala de referência LOOSE_AMP_REF = 5&amp;times;10^&amp;minus;4 m (o curso "
            "&amp;plusmn;0.5 mm de referência do rig UFU). Em exp = 1 o fator é exatamente 1 e o engine "
            "fica bit-idêntico ao ratchet linear; em exp &amp;gt; 1 a resposta fica ÍNGREME &amp;minus; "
            "amplitudes acima da referência afrouxam desproporcionalmente mais e as abaixo, muito "
            "menos &amp;minus; reproduzindo a inclinação forte da curva D-N (na parcela excedente do "
            "slip a lei efetiva vira ~excesso^&amp;minus;2.6). O mesmo expoente é aplicado ao termo "
            "&lt;code&gt;graded_scrit&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Mover o slider acima de 1 torna o joelho da curva mais abrupto; abaixo de 1 o "
            "afrouxamento fica quase-independente da amplitude. É uma forma opt-in, default-inerte "
            "(&lt;code&gt;loose_amp_exp = 1&lt;/code&gt; é bit-idêntico) e só age quando o ratchet está ativo "
            "(&lt;code&gt;k_ratchet&lt;/code&gt; &amp;gt; 0; aqui o contexto fixa k_ratchet=0.05 e um piso de "
            "auto-travamento para deixar a curva parar num patamar visível) e em disp-mode. "
            "Per-par.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The kinematic ratchet (&lt;code&gt;k_ratchet&lt;/code&gt;) turns the gross-slip path into "
            "loosening rotation LINEARLY in amplitude: doubling the per-cycle slip doubles the "
            "per-cycle advance. But the life-vs-amplitude data is far steeper than linear &amp;minus; "
            "Yang2023 measures the cycles-to-failure dropping as N &amp;prop; &amp;delta;^&amp;minus;3.8 "
            "with amplitude. &lt;code&gt;loose_amp_exp&lt;/code&gt; is the exponent that gives the kinematic "
            "term that amplitude non-linearity.&lt;/p&gt;"
            "&lt;p&gt;In the model it rescales the ratchet term by (slip/LOOSE_AMP_REF)^(exp&amp;minus;1), "
            "with the reference scale LOOSE_AMP_REF = 5&amp;times;10^&amp;minus;4 m (the &amp;plusmn;0.5 mm "
            "reference stroke of the UFU rig). At exp = 1 the factor is exactly 1 and the engine is "
            "bit-identical to the linear ratchet; at exp &amp;gt; 1 the response becomes STEEP &amp;minus; "
            "amplitudes above the reference loosen disproportionately more and those below far less "
            "&amp;minus; reproducing the strong slope of the D-N curve (on the excess slip the effective "
            "law becomes ~excess^&amp;minus;2.6). The same exponent is applied to the "
            "&lt;code&gt;graded_scrit&lt;/code&gt; term.&lt;/p&gt;"
            "&lt;p&gt;Moving the slider above 1 sharpens the knee of the curve; below 1 loosening becomes "
            "nearly amplitude-independent. It is an opt-in, default-inert form "
            "(&lt;code&gt;loose_amp_exp = 1&lt;/code&gt; is bit-identical) and only acts when the ratchet is "
            "active (&lt;code&gt;k_ratchet&lt;/code&gt; &amp;gt; 0; here the context fixes k_ratchet=0.05 and a "
            "self-locking floor so the curve settles at a visible plateau) and in disp-mode. "
            "Per-pair.&lt;/p&gt;"),
        refs=[("Yang2023: N &amp;prop; &amp;delta;^&amp;minus;3.8 (resposta de amplitude íngreme, D-N)",
               "Yang2023: N &amp;prop; &amp;delta;^&amp;minus;3.8 (steep amplitude response, D-N)",
               "MODEL_LEGITIMACY.md"),
              ("Expoente de amplitude do ratchet cinemático (spec 2026-07-12, PR-21)",
               "Kinematic-ratchet amplitude exponent (spec 2026-07-12, PR-21)",
               "&amp;sect;4.4 MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="delta_free", symbol="delta_free", unit="m", group="ratchet", category="form", context={"baseline":"transverse","overrides":{"k_ratchet":0.5}}, sweep=(0,1e-3,15,"lin"), related=["k_ratchet"],
        equation="slip = max(0, delta_amp - delta_free - F_slip/k_tr)",
        physics_pt=(
            "&lt;p&gt;O curso transversal imposto não vira todo escorregamento na interface. Uma parcela "
            "FIXA é absorvida antes, independente da pré-carga: a folga do furo sendo engajada mais a "
            "complacência da própria fixação. &lt;code&gt;delta_free&lt;/code&gt; (em m) é esse take-up fixo &amp;minus; o "
            "quanto do curso é consumido antes de haver slip real no contato.&lt;/p&gt;"
            "&lt;p&gt;Ele entra na lei de slip do disp-mode, slip = max(0, delta_amp &amp;minus; delta_free "
            "&amp;minus; F_slip/k_tr): tudo abaixo de &lt;code&gt;delta_free&lt;/code&gt; produz slip zero (nada de "
            "wear nem afrouxamento), e só o excesso dirige os mecanismos. Mover o slider desloca a "
            "curva para um platô mais longo e raso conforme &lt;code&gt;delta_free&lt;/code&gt; cresce; num "
            "take-up grande o suficiente a junta praticamente nunca escorrega.&lt;/p&gt;"
            "&lt;p&gt;Default-inerte (&lt;code&gt;delta_free=0&lt;/code&gt; é bit-idêntico). NÃO é um botão fitado: é "
            "LIDO do dado. A assinatura é N_falha ~ 1/(delta &amp;minus; delta_0) (Liu2025 delta_0 = 0.30 "
            "mm, 4 pares +-3%) e N_falha ~plano vs torque (Lu fig20) &amp;minus; um limiar que escala com a "
            "pré-carga não reproduz nenhum dos dois. Per-rig, limitado pela folga do furo.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The imposed transverse stroke does not all become slip at the interface. A FIXED "
            "share is taken up first, independent of preload: the hole clearance being engaged plus "
            "the compliance of the fixture itself. &lt;code&gt;delta_free&lt;/code&gt; (in m) is that fixed "
            "take-up &amp;minus; how much of the stroke is consumed before there is real slip at the contact.&lt;/p&gt;"
            "&lt;p&gt;It enters the disp-mode slip law, slip = max(0, delta_amp &amp;minus; delta_free &amp;minus; "
            "F_slip/k_tr): everything below &lt;code&gt;delta_free&lt;/code&gt; yields zero slip (no wear, no "
            "loosening), and only the excess drives the mechanisms. Moving the slider shifts the "
            "curve toward a longer, flatter plateau as &lt;code&gt;delta_free&lt;/code&gt; grows; with a large "
            "enough take-up the joint essentially never slips.&lt;/p&gt;"
            "&lt;p&gt;Default-inert (&lt;code&gt;delta_free=0&lt;/code&gt; is bit-identical). It is NOT a fitted knob: "
            "it is READ from the data. The signature is N_fail ~ 1/(delta &amp;minus; delta_0) (Liu2025 "
            "delta_0 = 0.30 mm, 4 pairs +-3%) and N_fail ~flat vs torque (Lu fig20) &amp;minus; a "
            "preload-scaled threshold reproduces neither. Per-rig, bounded by the hole clearance.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 lei de slip do disp-mode (resolve_transverse_slip)",
               "&amp;sect;5.2 disp-mode slip law (resolve_transverse_slip)", "MODEL_MATH_REFERENCE.md"),
              ("Take-up fixo lido do onset: Liu2025 delta_0=0.30mm; Lu fig20 plano vs torque",
               "Fixed take-up read from onset: Liu2025 delta_0=0.30mm; Lu fig20 flat vs torque",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="ratchet_torque_coupled", symbol="", unit="", group="ratchet", category="mode", context={"baseline":"transverse","overrides":{"k_ratchet":0.1}}, choices=[False,True], related=["k_ratchet"],
        equation="kin *= slip_fraction  (True)  |  kin  (False);   slip_fraction = (T_loose - T_resist)/T_loose",
        physics_pt=(
            "&lt;p&gt;Este seletor decide se o termo cinemático do ratchet (&lt;code&gt;k_ratchet&lt;/code&gt;) é "
            "multiplicado pelo excesso de torque adimensional slip_fraction = (T_loose &amp;minus; "
            "T_resist)/T_loose. Ou seja, se o ratchet é puramente cinemático ou se ganha um peso que "
            "cresce conforme a junta perde aperto.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;False&lt;/b&gt; (default): termo cinemático puro, proporcional só ao caminho de slip &amp;minus; "
            "uma catraca de passo constante. &lt;b&gt;True&lt;/b&gt;: o termo também cresce conforme F_0 cai "
            "(slip_fraction sobe rumo a 1), de modo que o colapso ACELERA no fim (forma back-loaded). "
            "Como slip_fraction depende só de F_0/F_0_init, a dinâmica fracional fica invariante na "
            "escala de pré-carga, dando N_falha ~plano vs torque.&lt;/p&gt;"
            "&lt;p&gt;Só tem efeito quando &lt;code&gt;k_ratchet&lt;/code&gt; &amp;gt; 0 (aqui o contexto fixa "
            "k_ratchet=0.5); &lt;b&gt;False&lt;/b&gt; é bit-idêntico ao ratchet puro. A forma-produto foi "
            "apontada por duas falhas de gate: a forma back-loaded do Liu2025 (que falsificou os "
            "carriers exponencial E linear) e o gate de flatness do Lu. O seletor troca entre as "
            "duas curvas pré-computadas.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This selector decides whether the kinematic ratchet term (&lt;code&gt;k_ratchet&lt;/code&gt;) is "
            "multiplied by the dimensionless torque excess slip_fraction = (T_loose &amp;minus; "
            "T_resist)/T_loose. That is, whether the ratchet is purely kinematic or gains a weight "
            "that grows as the joint loses clamp.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;False&lt;/b&gt; (default): pure kinematic term, proportional only to the slip path &amp;minus; a "
            "constant-step ratchet. &lt;b&gt;True&lt;/b&gt;: the term also grows as F_0 falls (slip_fraction "
            "rises toward 1), so the collapse ACCELERATES late (back-loaded shape). Because "
            "slip_fraction depends only on F_0/F_0_init, the fractional dynamics stay invariant in "
            "preload scale, giving N_fail ~flat vs torque.&lt;/p&gt;"
            "&lt;p&gt;It only has an effect when &lt;code&gt;k_ratchet&lt;/code&gt; &amp;gt; 0 (here the context sets "
            "k_ratchet=0.5); &lt;b&gt;False&lt;/b&gt; is bit-identical to the pure ratchet. The product form was "
            "pointed at by two failed gates: the Liu2025 back-loaded shape (which falsified both the "
            "exponential AND linear carriers) and the Lu flatness gate. The selector switches between "
            "the two pre-computed curves.&lt;/p&gt;"),
        refs=[("&amp;sect;4.15 forma-produto do ratchet (back-loaded do Liu2025; gate de flatness do Lu)",
               "&amp;sect;4.15 product-form ratchet (Liu2025 back-loaded; Lu flatness gate)",
               "MODEL_LEGITIMACY.md"),
              ("&amp;sect;4.4 kernel de loosening", "&amp;sect;4.4 loosening kernel", "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="loose_kin_ceiling", symbol="ceil_kin", unit="-", group="ratchet", category="form", context={"baseline":"transverse","overrides":{"loose_torsion_mode":"bolt_torsion","loosening_slip_coupling":"gross_fraction","k_tr_mode":"bending","eta_loose":8.0}}, sweep=(0,1.0,15,"lin"), related=["loose_rate_mode"],
        equation="d_eff = d_torque*d_kin/(d_torque + d_kin);   d_kin = gates * loose_kin_ceiling * 4*slip/(d_2/2)",
        physics_pt=(
            "&lt;p&gt;A rotação de afrouxamento por ciclo é limitada em SÉRIE por dois efeitos: o excesso "
            "de torque (o drive de (T_loose &amp;minus; T_resist)) e a DISPONIBILIDADE cinemática de "
            "slip &amp;minus; a porca não pode girar mais do que o caminho de gross-slip permite. O teto "
            "&lt;code&gt;loose_kin_ceiling&lt;/code&gt; (ceil_kin) escala essa disponibilidade cinemática (O(1), "
            "~caminho de slip por raio).&lt;/p&gt;"
            "&lt;p&gt;Os dois limitadores se combinam como uma média harmônica, d_eff = "
            "d_torque&amp;middot;d_kin/(d_torque + d_kin), com d_kin = gates &amp;times; ceil_kin &amp;times; "
            "4&amp;middot;slip/(d_2/2). Quando o excesso de torque dispara (F_0 &amp;rarr; 0, runaway), d_kin "
            "satura o termo e o colapso abrupto em S vira uma transição GRADUAL &amp;minus; corrige o erro de "
            "perda-a-mais no meio da curva (35/82 curvas). Mover o slider afrouxa o teto (mais "
            "parecido com o runaway de torque puro) ou o aperta (segura o meio da curva).&lt;/p&gt;"
            "&lt;p&gt;Default-inerte: &lt;code&gt;loose_kin_ceiling=0&lt;/code&gt; é sem teto (bit-idêntico). É um TETO "
            "SUAVE sobre o drive de torque, aplicado ANTES do termo aditivo &lt;code&gt;k_ratchet&lt;/code&gt;. A "
            "forma (dois limitadores em série) é transferível; só age em disp-mode. Ver "
            "&amp;sect;4.35.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The per-cycle loosening rotation is limited in SERIES by two effects: the torque "
            "excess (the drive of (T_loose &amp;minus; T_resist)) and the kinematic AVAILABILITY of "
            "slip &amp;minus; the nut cannot rotate more than the gross-slip path allows. The ceiling "
            "&lt;code&gt;loose_kin_ceiling&lt;/code&gt; (ceil_kin) scales that kinematic availability (O(1), "
            "~slip path per radius).&lt;/p&gt;"
            "&lt;p&gt;The two limiters combine as a harmonic mean, d_eff = "
            "d_torque&amp;middot;d_kin/(d_torque + d_kin), with d_kin = gates &amp;times; ceil_kin &amp;times; "
            "4&amp;middot;slip/(d_2/2). When the torque excess fires (F_0 &amp;rarr; 0, runaway), d_kin "
            "saturates the term and the abrupt S-collapse becomes a GRADUAL transition &amp;minus; fixing the "
            "mid-curve over-loss error (35/82 curves). Moving the slider loosens the ceiling (more "
            "like the pure torque runaway) or tightens it (holds the mid-curve).&lt;/p&gt;"
            "&lt;p&gt;Default-inert: &lt;code&gt;loose_kin_ceiling=0&lt;/code&gt; means no ceiling (bit-identical). It "
            "is a SOFT CEILING on the torque drive, applied BEFORE the additive &lt;code&gt;k_ratchet&lt;/code&gt; "
            "term. The form (two limiters in series) is transferable; it acts only in disp-mode. See "
            "&amp;sect;4.35.&lt;/p&gt;"),
        refs=[("&amp;sect;4.4 / &amp;sect;4.35 blend contínuo de fases (dois limitadores em série)",
               "&amp;sect;4.4 / &amp;sect;4.35 continuous phase blend (two limiters in series)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.35 erro sistemático de mid-curva &amp;minus; teto cinemático",
               "&amp;sect;4.35 systematic mid-curve error &amp;minus; kinematic ceiling", "MODEL_LEGITIMACY.md")]),

    VarSpec(name="loose_rate_mode", symbol="", unit="", group="ratchet", category="mode", context={"baseline":"transverse","overrides":{"s_crit_loose":2e-4,"k_loose_graded":1.0}}, choices=["torque","graded_scrit"], related=["s_crit_loose"],
        equation="torque: Delta_theta = gates*slip_fraction*(T_loose-T_resist)/k_torsional   |   graded_scrit: Delta_theta = gates*k_loose_graded*max(0, slip-s_crit_loose)/(d_2/2)",
        physics_pt=(
            "&lt;p&gt;Este seletor escolhe QUAL kernel produz a rotação de afrouxamento por ciclo &amp;minus; a forma "
            "matemática da taxa, não apenas o seu valor.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;torque&lt;/b&gt; (default): o kernel clássico dirigido pelo excesso de torque, "
            "&amp;Delta;&amp;theta; = gates &amp;times; slip_fraction &amp;times; (T_loose &amp;minus; "
            "T_resist)/k_torsional. Em disp-mode ele é RUNAWAY-até-zero uma vez disparado, porque o "
            "slip crítico efetivo (s_crit = delta_t = &amp;mu;&amp;middot;F_0/k_tr) CAI conforme F_0 cai &amp;minus; a "
            "amplitude decide SE dispara, não a trajetória. &lt;b&gt;graded_scrit&lt;/b&gt;: troca por uma taxa "
            "cinemática no EXCESSO de slip sobre um s_crit FIXO (não ~F_0), &amp;Delta;&amp;theta; = gates "
            "&amp;times; k_loose_graded &amp;times; max(0, slip &amp;minus; s_crit_loose)/(d_2/2). É "
            "amplitude-sensível a cada ciclo (um espectro morde), NÃO tem runaway (s_crit fixo + slip "
            "limitado pelo curso), sub-crítico dá zero (platô/não-inicia do Bauer) e produz colapso "
            "quase-linear (Karlsen).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;torque&lt;/b&gt; é bit-idêntico ao motor pré-feature. &lt;b&gt;graded_scrit&lt;/b&gt; só age com "
            "&lt;code&gt;s_crit_loose&lt;/code&gt; e &lt;code&gt;k_loose_graded&lt;/code&gt; setados (&amp;sect;4.37); "
            "do contrario o branch nunca roda. O seletor troca entre as duas curvas "
            "pré-computadas.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;This selector chooses WHICH kernel produces the per-cycle loosening rotation &amp;minus; the "
            "mathematical form of the rate, not just its value.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;torque&lt;/b&gt; (default): the classic torque-excess-driven kernel, &amp;Delta;&amp;theta; = "
            "gates &amp;times; slip_fraction &amp;times; (T_loose &amp;minus; T_resist)/k_torsional. In disp-mode "
            "it is RUNAWAY-to-zero once fired, because the effective critical slip (s_crit = delta_t = "
            "&amp;mu;&amp;middot;F_0/k_tr) FALLS as F_0 falls &amp;minus; amplitude decides WHETHER it fires, not the "
            "trajectory. &lt;b&gt;graded_scrit&lt;/b&gt;: replaces it with a kinematic rate on the EXCESS of slip "
            "over a FIXED s_crit (not ~F_0), &amp;Delta;&amp;theta; = gates &amp;times; k_loose_graded &amp;times; "
            "max(0, slip &amp;minus; s_crit_loose)/(d_2/2). It is amplitude-sensitive each cycle (a "
            "spectrum bites), has NO runaway (fixed s_crit + stroke-bounded slip), sub-critical gives "
            "zero (Bauer plateau/non-start), and yields a near-linear collapse (Karlsen).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;torque&lt;/b&gt; is bit-identical to the pre-feature engine. &lt;b&gt;graded_scrit&lt;/b&gt; only "
            "acts with &lt;code&gt;s_crit_loose&lt;/code&gt; and &lt;code&gt;k_loose_graded&lt;/code&gt; set "
            "(&amp;sect;4.37); otherwise the branch never runs. The selector switches between "
            "the two pre-computed curves.&lt;/p&gt;"),
        refs=[("&amp;sect;5.1 modos de formulação &amp;minus; kernel do loosening",
               "&amp;sect;5.1 formulation modes &amp;minus; loosening kernel", "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.37 taxa graduada amplitude-sensível (Bauer platô; Karlsen quase-linear)",
               "&amp;sect;4.37 graded amplitude-sensitive rate (Bauer plateau; Karlsen near-linear)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="s_crit_loose", symbol="s_crit", unit="m", group="ratchet", category="form", context={"baseline":"transverse","overrides":{"loose_rate_mode":"graded_scrit","k_loose_graded":1.0}}, sweep=(1e-5,5e-4,15,"log"), related=["k_loose_graded"],
        equation="Delta_theta = gates * k_loose_graded * max(0, slip - s_crit_loose)/(d_2/2)   (slip <= s_crit_loose => 0)",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;s_crit_loose&lt;/code&gt; é a amplitude crítica de slip que precisa ser excedida para "
            "o afrouxamento graduado começar. Abaixo de s_crit a interface micro-escorrega mas não "
            "gira a porca (platô / não-inicia); acima dele, só o excesso slip &amp;minus; s_crit dirige a "
            "rotação.&lt;/p&gt;"
            "&lt;p&gt;Ele entra no kernel graduado, &amp;Delta;&amp;theta; = gates &amp;times; k_loose_graded &amp;times; "
            "max(0, slip &amp;minus; s_crit_loose)/(d_2/2). Como o slip corrente modula a taxa a cada "
            "ciclo, um espectro de amplitudes morde de forma diferente; como s_crit é FIXO (não "
            "~F_0), não há runaway. Mover o slider (log) alonga o platô e pode suprimir o colapso por "
            "completo (todos os ciclos sub-críticos) ao subir, ou deixar até curso pequeno afrouxar "
            "ao descer.&lt;/p&gt;"
            "&lt;p&gt;Só age quando &lt;code&gt;loose_rate_mode=graded_scrit&lt;/code&gt; (o contexto liga o modo e "
            "fixa k_loose_graded=1.0). PER-RIG com proveniência: lido da curva amplitude-vs-vida "
            "(Bauer 76-108 &amp;micro;m, s_crit ~99 &amp;micro;m). Em 0 volta ao kernel de torque.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;s_crit_loose&lt;/code&gt; is the critical slip amplitude that must be exceeded for "
            "graded loosening to start. Below s_crit the interface micro-slips but does not turn the "
            "nut (plateau / non-start); above it, only the excess slip &amp;minus; s_crit drives "
            "rotation.&lt;/p&gt;"
            "&lt;p&gt;It enters the graded kernel, &amp;Delta;&amp;theta; = gates &amp;times; k_loose_graded &amp;times; "
            "max(0, slip &amp;minus; s_crit_loose)/(d_2/2). Because the current slip modulates the rate "
            "each cycle, a spectrum of amplitudes bites differently; because s_crit is FIXED (not "
            "~F_0), there is no runaway. Moving the slider (log) lengthens the plateau and can "
            "suppress the collapse entirely (all cycles sub-critical) when raised, or let even a "
            "small stroke loosen when lowered.&lt;/p&gt;"
            "&lt;p&gt;It acts only when &lt;code&gt;loose_rate_mode=graded_scrit&lt;/code&gt; (the context enables the "
            "mode and sets k_loose_graded=1.0). PER-RIG with provenance: read from the "
            "amplitude-vs-life curve (Bauer 76-108 &amp;micro;m, s_crit ~99 &amp;micro;m). At 0 it falls back "
            "to the torque kernel.&lt;/p&gt;"),
        refs=[("&amp;sect;4.37 slip crítico do onset graduado (Bauer 76-108um, curva amplitude-vs-vida)",
               "&amp;sect;4.37 graded onset critical slip (Bauer 76-108um, amplitude-vs-life)",
               "MODEL_LEGITIMACY.md"),
              ("&amp;sect;4.4 kernel alternativo graded_scrit", "&amp;sect;4.4 alternative graded_scrit kernel",
               "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="k_loose_graded", symbol="k_graded", unit="-", group="ratchet", category="form", context={"baseline":"transverse","overrides":{"loose_rate_mode":"graded_scrit","s_crit_loose":2e-4}}, sweep=(0,2.0,15,"lin"), related=["s_crit_loose"],
        equation="Delta_theta = gates * k_loose_graded * max(0, slip - s_crit_loose)/(d_2/2)",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;k_loose_graded&lt;/code&gt; é o coeficiente de taxa do afrouxamento graduado: quanta "
            "rotação (rad) a junta perde por rad de excesso-de-slip-sobre-raio a cada ciclo. Ele fixa "
            "a INCLINAÇÃO do colapso quase-linear depois que o slip excede s_crit.&lt;/p&gt;"
            "&lt;p&gt;Aparece no mesmo kernel graduado, &amp;Delta;&amp;theta; = gates &amp;times; k_loose_graded "
            "&amp;times; max(0, slip &amp;minus; s_crit_loose)/(d_2/2); k_graded escala o excesso (slip "
            "&amp;minus; s_crit_loose)/(d_2/2). Mover o slider: 0 DESLIGA o branch graduado (volta ao "
            "kernel de torque, bit-idêntico); subir aumenta a taxa de afrouxamento. Diferente do "
            "kernel de torque, esta taxa não dispara em runaway &amp;minus; ela satura porque o slip é limitado "
            "pelo curso imposto.&lt;/p&gt;"
            "&lt;p&gt;Só age quando &lt;code&gt;loose_rate_mode=graded_scrit&lt;/code&gt; (o contexto liga o modo e "
            "fixa s_crit_loose=2e-4). Coeficiente [rad por rad de excesso/raio], per-rig. Junto com o "
            "input de espectro, as duas formas fazem o que nenhuma faz sozinha (&amp;sect;4.37).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;k_loose_graded&lt;/code&gt; is the rate coefficient of graded loosening: how much "
            "rotation (rad) the joint sheds per rad of slip-excess-over-radius each cycle. It sets "
            "the SLOPE of the near-linear collapse once slip exceeds s_crit.&lt;/p&gt;"
            "&lt;p&gt;It appears in the same graded kernel, &amp;Delta;&amp;theta; = gates &amp;times; k_loose_graded "
            "&amp;times; max(0, slip &amp;minus; s_crit_loose)/(d_2/2); k_graded scales the excess (slip "
            "&amp;minus; s_crit_loose)/(d_2/2). Moving the slider: 0 turns the graded branch OFF (back to "
            "the torque kernel, bit-identical); raising it steepens the loosening rate. Unlike the "
            "torque kernel, this rate does not run away &amp;minus; it saturates because slip is bounded by the "
            "imposed stroke.&lt;/p&gt;"
            "&lt;p&gt;It acts only when &lt;code&gt;loose_rate_mode=graded_scrit&lt;/code&gt; (the context enables the "
            "mode and sets s_crit_loose=2e-4). Coefficient [rad per rad of excess/radius], per-rig. "
            "Together with the spectrum input, the two forms do what neither does alone "
            "(&amp;sect;4.37).&lt;/p&gt;"),
        refs=[("&amp;sect;4.37 ganho da taxa graduada (destrava o espectro; Karlsen quase-linear)",
               "&amp;sect;4.37 graded rate gain (unlocks the spectrum; Karlsen near-linear)",
               "MODEL_LEGITIMACY.md"),
              ("&amp;sect;4.4 kernel alternativo graded_scrit", "&amp;sect;4.4 alternative graded_scrit kernel",
               "MODEL_MATH_REFERENCE.md")]),
])

# =============================== SURFACE DAMAGE + CONFORMATION/ONSET (14) ===============================
VARIABLE_SPECS.extend([
    VarSpec(
        name="W_ref", symbol="W_ref", unit="J", group="damage", category="form",
        context={"baseline": "transverse",
                 "overrides": {"c_D": 2.0, "k_dmg_mu": 1.0, "k_dmg_wear": 4.0}},
        sweep=(1e3, 1e5, 15, "log"), related=["c_D"],
        equation="dD/dN = c_D * (W_slip / W_ref) * (1 - D);   W_slip = dE_wear + dE_loose (+ dE_partial)",
        physics_pt=(
            "&lt;p&gt;Escala de energia de referência do dano de superfície &lt;code&gt;D&lt;/code&gt;. "
            "A cada ciclo o modelo mede quanta energia foi dissipada por escorregamento "
            "(o trabalho de atrito do wear + do afrouxamento rotacional, mais o anel de "
            "micro-slip quando ligado) e divide essa dose pela constante &lt;code&gt;W_ref&lt;/code&gt; "
            "para saber quanto o dano avança. Fisicamente é o quanto de energia dissipada "
            "corresponde a uma unidade de dose de dano &amp;minus; quanto MAIOR &lt;code&gt;W_ref&lt;/code&gt;, "
            "mais devagar D cresce.&lt;/p&gt;"
            "&lt;p&gt;Na equação dD/dN = c_D&amp;middot;(W_slip/W_ref)&amp;middot;(1&amp;minus;D), o fator "
            "(1&amp;minus;D) satura D em [0,1]. Mover o slider mostra isso direto: aumentar "
            "&lt;code&gt;W_ref&lt;/code&gt; achata e adia o COLAPSO tardio (a queda abrupta de F/F0 "
            "vai para mais longe ou some da janela); reduzir &lt;code&gt;W_ref&lt;/code&gt; traz o "
            "colapso para os primeiros ciclos. Os companheiros &lt;code&gt;c_D&lt;/code&gt;, "
            "&lt;code&gt;k_dmg_mu&lt;/code&gt; e &lt;code&gt;k_dmg_wear&lt;/code&gt; estão ligados aqui para o "
            "dano de fato crescer e acoplar.&lt;/p&gt;"
            "&lt;p&gt;É uma &lt;b&gt;forma opt-in&lt;/b&gt; (default 1e4 J, dano inativo por "
            "&lt;code&gt;c_D&lt;/code&gt;=0). No regime de dano pequeno só a RAZÃO c_D/W_ref importa "
            "(ambos escalam dD linearmente), logo &lt;code&gt;W_ref&lt;/code&gt; não é identificável "
            "sozinho ali &amp;minus; é por par tribológico, sem âncora medida na biblioteca.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Reference energy scale of the surface damage &lt;code&gt;D&lt;/code&gt;. Each cycle "
            "the model measures how much energy was dissipated by slip (the friction work "
            "of wear + rotational loosening, plus the micro-slip ring when enabled) and "
            "divides that dose by the constant &lt;code&gt;W_ref&lt;/code&gt; to know how far damage "
            "advances. Physically it is how much dissipated energy corresponds to one unit "
            "of damage dose &amp;minus; the LARGER &lt;code&gt;W_ref&lt;/code&gt;, the slower D grows.&lt;/p&gt;"
            "&lt;p&gt;In dD/dN = c_D&amp;middot;(W_slip/W_ref)&amp;middot;(1&amp;minus;D), the (1&amp;minus;D) "
            "factor saturates D in [0,1]. Moving the slider shows it directly: raising "
            "&lt;code&gt;W_ref&lt;/code&gt; flattens and delays the late COLLAPSE (the abrupt F/F0 "
            "drop moves further out or leaves the window); lowering &lt;code&gt;W_ref&lt;/code&gt; "
            "brings the collapse into the early cycles. The companions &lt;code&gt;c_D&lt;/code&gt;, "
            "&lt;code&gt;k_dmg_mu&lt;/code&gt; and &lt;code&gt;k_dmg_wear&lt;/code&gt; are enabled here so damage "
            "actually grows and couples.&lt;/p&gt;"
            "&lt;p&gt;It is an &lt;b&gt;opt-in form&lt;/b&gt; (default 1e4 J, damage off via "
            "&lt;code&gt;c_D&lt;/code&gt;=0). In the small-damage regime only the RATIO c_D/W_ref "
            "matters (both scale dD linearly), so &lt;code&gt;W_ref&lt;/code&gt; is not identifiable "
            "on its own there &amp;minus; it is per tribological pair, with no measured library "
            "anchor.&lt;/p&gt;"),
        refs=[("&amp;sect;4 surface_damage &amp;minus; dose de energia de slip que faz D crescer",
               "&amp;sect;4 surface_damage &amp;minus; slip-energy dose driving D growth",
               "MODEL_MATH_REFERENCE.md"),
              ("staged-calibration-leverage &amp;minus; design do surface_damage",
               "staged-calibration-leverage &amp;minus; surface_damage design",
               "specs/2026-06-20-staged-calibration-leverage-design.md")]),

    VarSpec(
        name="k_late_amp", symbol="k_late_amp", unit="-", group="damage", category="form",
        context={"baseline": "transverse",
                 "overrides": {"crash_trigger_frac": 0.60,
                               "crash_trigger_sharpness": 8.0}},
        sweep=(0, 3.0, 13, "lin"),
        related=["crash_trigger_frac", "crash_trigger_sharpness", "k_dmg_all"],
        equation="dF_0_total *= (1 + k_late_amp * g);  g = ft/(ft + (F_0/F_0_init)^k)  (0 = OFF exato)",
        physics_pt=(
            "&lt;p&gt;&lt;b&gt;Amplifica&amp;ccedil;&amp;atilde;o TARDIA com interruptor&lt;/b&gt; — a s&amp;iacute;ntese de duas "
            "medi&amp;ccedil;&amp;otilde;es de 2026-08-01: o gatilho de criticalidade tinha o PERFIL certo "
            "(quase inerte enquanto a pr&amp;eacute;-carga est&amp;aacute; alta, pleno depois do limiar) mas "
            "s&amp;oacute; sabia SUPRIMIR; o amplificador por dano tinha o SINAL certo mas era "
            "gradual demais e estragava o in&amp;iacute;cio da curva. Este usa o interruptor para "
            "AMPLIFICAR.&lt;/p&gt;"
            "&lt;p&gt;Companheiro obrigat&amp;oacute;rio: &lt;code&gt;crash_trigger_frac&lt;/code&gt; (sem limiar n&amp;atilde;o "
            "h&amp;aacute; interruptor e o slider fica inerte). No slider: valores at&amp;eacute; ~1 d&amp;atilde;o joelho "
            "tardio; acima de ~3 a realimenta&amp;ccedil;&amp;atilde;o em F&amp;#8320; vira runaway e a junta morre em "
            "poucas dezenas de ciclos (bifurca&amp;ccedil;&amp;atilde;o medida).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;N&amp;Atilde;O adotado em fonte nenhuma&lt;/b&gt;: o gate de classe reprovou — dentro da "
            "MESMA fonte umas curvas melhoram e outras pioram com o mesmo valor, ou seja, "
            "n&amp;atilde;o &amp;eacute; constante por rig. Default 0 = OFF exato.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;b&gt;Switch-gated LATE amplification&lt;/b&gt; — the synthesis of two measurements "
            "(2026-08-01): the criticality trigger had the right PROFILE (nearly inert while "
            "preload is high, full after the threshold) but could only SUPPRESS; the "
            "damage-driven amplifier had the right SIGN but was too gradual and ruined the "
            "early curve. This one uses the switch to AMPLIFY.&lt;/p&gt;"
            "&lt;p&gt;Mandatory companion: &lt;code&gt;crash_trigger_frac&lt;/code&gt; (no threshold, no switch, "
            "slider inert). Values up to ~1 give a late knee; above ~3 the feedback through "
            "F&amp;#8320; becomes runaway (measured bifurcation).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;NOT adopted anywhere&lt;/b&gt;: the class gate failed — within the SAME source "
            "some curves improve and others worsen at the same value, i.e. it is not a "
            "per-rig constant. Default 0 = exact OFF.&lt;/p&gt;"),
    ),

    VarSpec(
        name="gth_k", symbol="k_gth", unit="rad/ciclo", group="loosening", category="form",
        context={"baseline": "transverse", "overrides": {"gth_A0": 100.0}},
        sweep=(0.0, 2e-4, 13, "lin"), related=["gth_q", "gth_dref", "gth_A0"],
        negligible=True,
        equation="EM STICK (slip&le;1e-9): A += (&delta;/dref)^q; se A&ge;A0: d&theta; = k_gth&middot;(&delta;/dref)^q  (0 = OFF exato)",
        physics_pt=(
            "&lt;p&gt;&lt;b&gt;Ratchet de regime de STICK com incuba&amp;ccedil;&amp;atilde;o&lt;/b&gt; (2026-08-10, "
            "dossi&amp;ecirc; YANG_2019 amp0p4): micro-slip de flanco em stick macro produz "
            "rota&amp;ccedil;&amp;atilde;o incremental com depend&amp;ecirc;ncia &amp;iacute;ngreme de amplitude (lei IJPEM "
            "N_L~&amp;delta;^-3,8); o acumulador A_gth carrega a incuba&amp;ccedil;&amp;atilde;o (o plat&amp;ocirc; do dado). "
            "Ativo SOMENTE em stick — em regime de slip &amp;eacute; 0 EXATO, e curvas que "
            "deslizam ficam bit-id&amp;ecirc;nticas por constru&amp;ccedil;&amp;atilde;o.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;N&amp;Atilde;O adotado&lt;/b&gt;: a 6&amp;ordf; falsifica&amp;ccedil;&amp;atilde;o do dossi&amp;ecirc; &amp;eacute; ESTRUTURAL — o corte "
            "de stick limita o mecanismo ao limiar de slip; abaixo dele os canais macro "
            "n&amp;atilde;o produzem a cauda da 0,4 mm com constantes compartilhadas. Slider "
            "inerte no baseline UFU (0,65 mm = regime de slip), por isso honesto "
            "negligible.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;b&gt;Stick-regime ratchet with incubation&lt;/b&gt; (2026-08-10): flank micro-slip "
            "under macro stick drives incremental rotation with steep amplitude "
            "dependence (IJPEM law); accumulator A_gth carries the incubation plateau. "
            "Active ONLY in stick — exact zero under slip, so slipping curves are "
            "bit-identical by construction. Not adopted: the stick cut-off caps the "
            "mechanism at the slip threshold (structural boundary, dossier #6).&lt;/p&gt;"),
    ),

    VarSpec(
        name="gth_q", symbol="q_gth", unit="-", group="loosening", category="form",
        context={"baseline": "transverse", "overrides": {"gth_k": 5e-5, "gth_A0": 100.0}},
        sweep=(1.0, 6.0, 11, "lin"), related=["gth_k"], negligible=True,
        equation="A += (&delta;/dref)^q — expoente da lei de amplitude (proced&ecirc;ncia IJPEM: 3,8)",
        physics_pt=(
            "&lt;p&gt;Expoente da lei de amplitude do gth. Proced&amp;ecirc;ncia: Yang2023 IJPEM, "
            "N_L ~ &amp;delta;^-3,5..-3,8 (vida de onset). Ingreme = amplitude baixa quase n&amp;atilde;o "
            "acumula — &amp;eacute; a incuba&amp;ccedil;&amp;atilde;o longa da 0,4 mm.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Amplitude-law exponent (IJPEM provenance 3.5-3.8).&lt;/p&gt;"),
    ),

    VarSpec(
        name="gth_dref", symbol="dref_gth", unit="m", group="loosening", category="form",
        context={"baseline": "transverse", "overrides": {"gth_k": 5e-5, "gth_A0": 100.0}},
        sweep=(1e-4, 1e-3, 11, "log"), related=["gth_k"], negligible=True,
        equation="raz&atilde;o = &delta;/dref (= LOOSE_AMP_REF por conven&ccedil;&atilde;o)",
        physics_pt=("&lt;p&gt;Escala de refer&amp;ecirc;ncia da raz&amp;atilde;o de amplitude (conven&amp;ccedil;&amp;atilde;o "
                    "LOOSE_AMP_REF do PR-21).&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Reference scale of the amplitude ratio (PR-21 convention).&lt;/p&gt;"),
    ),

    VarSpec(
        name="gth_A0", symbol="A0_gth", unit="ciclos-eq", group="loosening", category="form",
        context={"baseline": "transverse", "overrides": {"gth_k": 5e-5}},
        sweep=(0.0, 5000.0, 11, "lin"), related=["gth_k"], negligible=True,
        equation="termo ativo s&oacute; com A_gth &ge; A0 — a INCUBA&Ccedil;&Atilde;O (0 = sem incuba&ccedil;&atilde;o)",
        physics_pt=("&lt;p&gt;Limiar do acumulador — o plat&amp;ocirc; do dado antes do onset "
                    "(YANG_2019 amp0p4: ~N&amp;asymp;5000 a 0,4 mm).&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Accumulator threshold — the data plateau before onset.&lt;/p&gt;"),
    ),

    VarSpec(
        name="mu_kinetic_frac", symbol="mu_k/mu_s", unit="-", group="loosening", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0.5, 1.0, 11, "lin"), related=["mu_bearing"], negligible=True,
        equation="mu_eff *= mu_kinetic_frac ap&oacute;s a 1&ordf; abertura do slip (latch stick_broken; 1.0 = OFF exato)",
        physics_pt=("&lt;p&gt;HISTERESE DE STICK (2026-08-20): f&iacute;sica de livro &mu;_est&aacute;tico &gt; "
                    "&mu;_cin&eacute;tico — a 1&ordf; abertura do slip rompe o travamento (interlock/&oacute;xido) "
                    "e o &mu; de bearing cai SEM VOLTA. Motivada pela &lt;code&gt;yang2019_amp0p4&lt;/code&gt;: o "
                    "modelo alcan&ccedil;a a transi&ccedil;&atilde;o no joelho real (F=0,916&middot;F&#8320;) mas o "
                    "[K(s)] re-trava. N&Atilde;O adotada: a avalanche p&oacute;s-ruptura do modelo &eacute; mais "
                    "r&aacute;pida que a real (falta amortecimento da transi&ccedil;&atilde;o).&lt;/p&gt;"),
        physics_en=("&lt;p&gt;STICK HYSTERESIS: textbook static&gt;kinetic friction — the first slip opening "
                    "breaks the interlock and bearing friction drops for good. NOT adopted yet: the "
                    "post-rupture avalanche is faster than the real one.&lt;/p&gt;"),
    ),

    VarSpec(
        name="loose_F_exp", symbol="fe", unit="-", group="loosening", category="form",
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit",
                                "k_loose_graded": 0.02, "s_crit_loose": 0.0,
                                "loose_arrest_floor": 0.0}},
        sweep=(0.0, 3.0, 13, "lin"), related=["k_loose_graded", "loose_rate_mode"],
        equation="d_theta *= (F0/F0_init)^fe   [fe&gt;0; fe=0 = OFF exato]",
        physics_pt=("&lt;p&gt;TAXA FRACION&Aacute;RIA (P-13, adotada 2026-08-20 no YANG_2023): a taxa "
                    "do ratchet cai com a pr&eacute;-carga remanescente — fe=1 d&aacute; decay "
                    "exponencial (dF/dN &prop; F), fe&gt;1 sub-exponencial. &Eacute; o meio-termo entre "
                    "os dois atratores do canal rotacional (runaway-a-zero &prop;slip &times; arresto "
                    "pelo re-travamento do [K(s)]). A EDO tem solu&ccedil;&atilde;o fechada — as "
                    "constantes s&atilde;o LID&Aacute;VEIS por LSQ ao F(N) publicado (r&amp;sup2; "
                    "0,997&ndash;0,9999 nas 3 curvas adotadas).&lt;/p&gt;"),
        physics_en=("&lt;p&gt;FRACTIONAL RATE (P-13, adopted 2026-08-20 on YANG_2023): the ratchet "
                    "rate falls with remaining preload — fe=1 gives exponential decay, fe&gt;1 "
                    "sub-exponential. The middle ground between the two attractors of the "
                    "rotational channel. Closed-form ODE — constants READABLE via LSQ to the "
                    "published F(N).&lt;/p&gt;"),
    ),

    VarSpec(
        name="gth_accel_p", symbol="p_gth", unit="-", group="loosening", category="form",
        # so age com gth ligado E pos-onset E em STICK — na junta-padrao
        # (transverse, slip aberto) o gth nao roda: slider estruturalmente
        # inerte, honesto como os demais campos de regime nao-excitado.
        context={"baseline": "transverse", "overrides": {"gth_k": 5e-5, "gth_A0": 100.0}},
        sweep=(0.0, 4.0, 9, "lin"), related=["gth_k", "gth_A0"], negligible=True,
        equation="d_theta = gth_k &middot; rq &middot; ((A_gth &minus; A0)/max(A0,1))^p   [p&gt;0; p=0 = OFF exato]",
        physics_pt=("&lt;p&gt;ACELERA&Ccedil;&Atilde;O progressiva do ratchet de stick: p&oacute;s-onset a taxa "
                    "cresce com o ACUMULADO (dano de flanco progressivo). Lida da "
                    "&lt;code&gt;yang2019_amp0p4&lt;/code&gt;: taxa 11,6&times; para N-efetivo 3,8&times; "
                    "&amp;rArr; p&amp;asymp;2&ndash;2,9 (LSQ na integral, r&amp;sup2;=0,969). p=0 (default) = "
                    "taxa constante p&oacute;s-onset, bit-id&ecirc;ntico.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Progressive acceleration of the stick ratchet: past onset the rate "
                    "grows with the ACCUMULATOR (progressive flank damage). Read from "
                    "&lt;code&gt;yang2019_amp0p4&lt;/code&gt; (p&amp;asymp;2&ndash;2.9, integral LSQ r&amp;sup2;=0.969). "
                    "p=0 (default) = constant post-onset rate, bit-identical.&lt;/p&gt;"),
    ),

    VarSpec(
        name="loose_runaway_frac", symbol="r_c", unit="-", group="loosening", category="form",
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit", "k_loose_graded": 0.02,
                                "loose_F_exp": 4.0, "loose_runaway_gain": 13.0,
                                "loose_arrest_floor": 0.0}},
        sweep=(0.0, 0.5, 11, "lin"), related=["loose_runaway_gain", "loose_F_exp"],
        equation="d_theta *= 1 + gain &middot; r_c^k/(r_c^k + (F&#8320;/F&#8320;&#8330;)^k)   [frac=0 OU gain=0 = OFF exato]",
        physics_pt=("&lt;p&gt;RUNAWAY DE PORCA SOLTA (2026-08-20, zhang2006_fig3 &sect;9): fra&ccedil;&atilde;o "
                    "cr&iacute;tica de F&#8320; abaixo da qual o auto-travamento residual deixa de segurar "
                    "o backoff e a taxa DISPARA. Lida da Fig. 3 do Zhang 2006: o paper DEFINE o fim do "
                    "Est&aacute;gio II em P=25% — exatamente porque dali a porca solta; o tra&ccedil;o &theta; "
                    "digitalizado dispara 10&rarr;42&deg; com raz&atilde;o de taxas ~14&times; onde a lei F^fe "
                    "LIDA desacelera por constru&ccedil;&atilde;o. &Eacute; o ESPELHO do crash_trigger (que "
                    "suprime antes): aqui a taxa do meio fica INTACTA.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;LOOSE-NUT RUNAWAY: critical preload fraction below which residual "
                    "self-locking stops holding the back-off and the rate takes off. Read from Zhang "
                    "2006 Fig. 3 (Stage II ends at P=25% by the paper's own definition; digitized "
                    "&theta; trace fires 10&rarr;42&deg;, ~14&times; rate ratio).&lt;/p&gt;"),
    ),

    VarSpec(
        name="loose_runaway_gain", symbol="R_run", unit="-", group="loosening", category="form",
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit", "k_loose_graded": 0.02,
                                "loose_F_exp": 4.0, "loose_runaway_frac": 0.25,
                                "loose_arrest_floor": 0.0}},
        sweep=(0.0, 40.0, 11, "lin"), related=["loose_runaway_frac", "loose_runaway_sharpness"],
        equation="ganho m&aacute;ximo extra da taxa no runaway (0 = OFF exato)",
        physics_pt=("&lt;p&gt;Ganho do disparo: raz&atilde;o de taxas do runaway menos 1. Lido do tra&ccedil;o "
                    "&theta; da Fig. 3 (taxa 14&times; a do miolo &rArr; gain&asymp;13).&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Runaway gain: rate ratio minus one, read from the &theta; trace "
                    "(&asymp;14&times; &rArr; gain&asymp;13).&lt;/p&gt;"),
    ),

    VarSpec(
        name="loose_runaway_sharpness", symbol="k_run", unit="-", group="loosening", category="form",
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit", "k_loose_graded": 0.02,
                                "loose_F_exp": 4.0, "loose_runaway_frac": 0.25,
                                "loose_runaway_gain": 13.0, "loose_arrest_floor": 0.0}},
        sweep=(2.0, 16.0, 8, "lin"), related=["loose_runaway_frac"], negligible=True,
        equation="nitidez do Hill do disparo (s&oacute; lido se frac&gt;0; default 6)",
        physics_pt=("&lt;p&gt;Abruptez da transi&ccedil;&atilde;o para o runaway. Default 6 (o mesmo idioma "
                    "dos outros Hill do engine); acima do limiar o boost decai ~(r_c/r)^k — suave, "
                    "n&atilde;o zero.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Sharpness of the runaway transition (Hill exponent, default 6).&lt;/p&gt;"),
    ),

    VarSpec(
        name="onset_burst_frac", symbol="f_burst", unit="-", group="loosening", category="form",
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit", "k_loose_graded": 0.01,
                                "loose_F_exp": 1.24, "slip_onset_W": 150.0,
                                "slip_onset_sharpness": 20.0, "onset_burst_rate": 0.3,
                                "loose_arrest_floor": 0.0, "emb_depth": 1e-6, "C_creep": 0.0}},
        sweep=(0.0, 0.8, 9, "lin"), related=["onset_burst_rate", "slip_onset_W"],
        equation="d&theta;_burst = g_onset &middot; rate &middot; max(0, F&#8320; &minus; (1&minus;frac)&middot;F&#8320;&#8330;)/(k_b&middot;lead)   [frac=0 OU rate=0 = OFF exato]",
        physics_pt=("&lt;p&gt;BURST DE RUPTURA (2026-08-21, fig14 do LU_2024): quando a INCUBA&Ccedil;&Atilde;O "
                    "abre (o mesmo gate Hill de slip_onset_W), a energia acumulada no travamento "
                    "libera num dreno r&aacute;pido e LIMITADO — exponencial em dire&ccedil;&atilde;o ao alvo "
                    "(1&minus;frac)&middot;F&#8320;, que DESACELERA sozinho. As duas fig14_long mostram o "
                    "perfil plat&ocirc;&rarr;burst&rarr;cauda; frac &eacute; LIDO da inflex&atilde;o do burst "
                    "(amp1p0: 0,62). 3&ordf; inst&acirc;ncia da classe transi&ccedil;&atilde;o-entre-regimes.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;RUPTURE BURST: when incubation opens, the stored interlock energy releases "
                    "as a fast, LIMITED drain toward the target (1&minus;frac)&middot;F&#8320; — decelerating "
                    "on arrival. frac is READ from the burst inflection of the data.&lt;/p&gt;"),
    ),

    VarSpec(
        name="onset_burst_rate", symbol="r_burst", unit="1/ciclo", group="loosening", category="form",
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit", "k_loose_graded": 0.01,
                                "loose_F_exp": 1.24, "slip_onset_W": 150.0,
                                "slip_onset_sharpness": 20.0, "onset_burst_frac": 0.5,
                                "loose_arrest_floor": 0.0, "emb_depth": 1e-6, "C_creep": 0.0}},
        sweep=(0.0, 0.6, 9, "lin"), related=["onset_burst_frac"],
        equation="fra&ccedil;&atilde;o da lacuna (F&#8320; &minus; alvo) drenada por ciclo no burst (0 = OFF exato)",
        physics_pt=("&lt;p&gt;Velocidade do burst: fra&ccedil;&atilde;o da lacuna at&eacute; o alvo drenada por "
                    "ciclo. O dado da amp1p0 pede ~0,30 (colapso de 0,42 de F&#8320; em ~5 ciclos); a "
                    "amp0p5, mais gradual, ~0,15.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Burst speed: fraction of the gap to target drained per cycle.&lt;/p&gt;"),
    ),

    VarSpec(
        name="onset_burst_W", symbol="W_burst", unit="J", group="loosening", category="form",
        context={"baseline": "transverse",
                 "overrides": {"loose_rate_mode": "graded_scrit", "k_loose_graded": 0.01,
                                "loose_F_exp": 1.24, "slip_onset_W": 150.0,
                                "slip_onset_sharpness": 20.0, "onset_burst_frac": 0.5,
                                "onset_burst_rate": 0.3,
                                "loose_arrest_floor": 0.0, "emb_depth": 1e-6, "C_creep": 0.0}},
        sweep=(0.0, 300.0, 9, "lin"), related=["onset_burst_frac", "slip_onset_W"],
        equation="g_burst = W&#8347;&#8202;&#7500;/(W&#8347;&#7500; + W_burst&#7500;)   [0 = usa o g compartilhado de slip_onset_W = BIT-ID&Ecirc;NTICO]",
        physics_pt=("&lt;p&gt;GATE PR&Oacute;PRIO do burst (2026-08-21, anatomia da liu2025 amp0p8): "
                    "os 3 gates de estado do engine s&atilde;o mon&oacute;tonos E COMPARTILHADOS entre "
                    "canais — um burst gateado pelo g do slip_onset s&oacute; abre onde o WEAR tamb&eacute;m "
                    "abre. W_burst &gt; 0 troca o gate por um Hill pr&oacute;prio sobre o MESMO W_slip_acc: "
                    "o limiar de ADES&Atilde;O (burst) separa-se do limiar de ABRAS&Atilde;O (wear), duas "
                    "escalas de energia da mesma interface. Sondado na amp0p8: o sino &eacute; real "
                    "(&sigma; 0,0507&rarr;0,0271) e n&atilde;o fecha — DORMENTE at&eacute; 2&ordf; inst&acirc;ncia "
                    "com leitura.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;Burst-specific onset gate: decouples the adhesion (burst) threshold from "
                    "the abrasion (wear) threshold — its own Hill over the same W_slip_acc. 0 = shared "
                    "gate, bit-identical.&lt;/p&gt;"),
    ),

    VarSpec(
        name="emb_clock_m", symbol="m_emb", unit="-", group="settling", category="form",
        context={"baseline": "transverse", "overrides": {"N_emb": 300.0}},
        sweep=(0.5, 4.0, 8, "lin"), related=["N_emb", "emb_depth"], negligible=True,
        equation="&delta;_emb(N) = alvo &middot; (1 &minus; e^{&minus;(N/N_emb)^m})   [m=1 = forma atual BIT-ID&Ecirc;NTICA]",
        physics_pt=("&lt;p&gt;REL&Oacute;GIO SIGMOIDE do embedding (2026-08-21): expoente de Weibull no "
                    "rel&oacute;gio de Est&aacute;gio I — m&gt;1 d&aacute; plat&ocirc; inicial + joelho + "
                    "satura&ccedil;&atilde;o. Implementa&ccedil;&atilde;o state-based exata via N impl&iacute;cito. "
                    "Constru&iacute;da para a fig14_amp0p25_long e N&Atilde;O usada nela (a errata do "
                    "pr&oacute;prio ataque mediu degrau+arresto = exponencial curto); fica DORMENTE "
                    "at&eacute; um plat&ocirc; real exigi-la.&lt;/p&gt;"),
        physics_en=("&lt;p&gt;SIGMOID embedding clock: Weibull exponent on the Stage-I clock — m&gt;1 "
                    "gives plateau + knee + saturation. Built and left DORMANT (the target curve "
                    "turned out to be step+arrest, closed by the short exponential clock).&lt;/p&gt;"),
    ),

    VarSpec(
        name="k_dmg_all", symbol="k_dmg_all", unit="-", group="damage", category="form",
        context={"baseline": "transverse",
                 "overrides": {"c_D": 2.0, "k_dmg_mu": 1.0, "k_dmg_wear": 4.0}},
        sweep=(0, 8.0, 15, "lin"), related=["c_D", "k_dmg_wear", "W_ref"],
        equation="dF_0_total *= (1 + k_dmg_all * D)   (dF_0 SIM, dE NAO; 0 = OFF exato)",
        physics_pt=(
            "&lt;p&gt;&lt;b&gt;Amplificador tardio agnóstico de canal&lt;/b&gt; (PR-3, 2026-08-01): o dano "
            "acumulado acelera &lt;b&gt;toda&lt;/b&gt; a perda de pré-carga, não só o desgaste. "
            "Fisicamente: a junta degradada perde mais rápido por todos os caminhos "
            "abertos — não existe razão para o dano tocar a face de apoio e poupar o "
            "assentamento, o creep de interface ou o afrouxamento rotacional.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Por que ele existe:&lt;/b&gt; 7 fontes do acervo mostram o dado desabando no "
            "fim 2&amp;times; a 225&amp;times; mais rápido que o modelo, e o engine não tinha como "
            "reproduzir isso — todos os gates (incubação, conformação, regime de slip, "
            "auto-travamento, gatilho de criticalidade) valem no máximo 1, ou seja, só "
            "sabem ATRASAR; e o único amplificador existente multiplica o desgaste, que "
            "está morto em 4 dessas 5 fontes. Este multiplica o TOTAL, então não precisa "
            "saber qual mecanismo domina — e o dominante MUDA de fonte para fonte.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Limite medido:&lt;/b&gt; ele depende de &lt;code&gt;D&lt;/code&gt;, que só cresce com "
            "dissipação por escorregamento. Onde a perda não é dirigida por slip (creep "
            "puro, corrosão, fadiga com slip incubado) o D fica em zero e este slider "
            "não faz nada — foi o que reprovou o gate de adoção em 2 de 5 fontes. "
            "&lt;b&gt;Default 0 = OFF exato&lt;/b&gt; (bit-idêntico); não adotado em nenhuma fonte.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;b&gt;Channel-agnostic late amplifier&lt;/b&gt; (PR-3, 2026-08-01): accumulated "
            "damage accelerates &lt;b&gt;all&lt;/b&gt; preload loss, not just wear. Physically, a "
            "degraded joint loses faster through every open path — there is no reason for "
            "damage to touch the bearing face and spare embedding, interface creep or "
            "rotational loosening.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Why it exists:&lt;/b&gt; in 7 library sources the data collapses at the end "
            "2&amp;times;–225&amp;times; faster than the model, and the engine had no way to "
            "reproduce it: every gate (incubation, conformance, slip regime, self-locking, "
            "criticality trigger) is at most 1 — they can only DELAY — and the single "
            "existing amplifier multiplies wear, which is dead in 4 of those 5 sources. "
            "This one multiplies the TOTAL, so it needs no knowledge of which mechanism "
            "dominates — and the dominant one changes across sources.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Measured limit:&lt;/b&gt; it rides on &lt;code&gt;D&lt;/code&gt;, which only grows from "
            "slip dissipation. Where loss is not slip-driven (pure creep, corrosion, "
            "fatigue with incubated slip) D stays at zero and this slider does nothing — "
            "that is what failed the adoption gate in 2 of 5 sources. &lt;b&gt;Default 0 = exact "
            "OFF&lt;/b&gt;; not adopted in any source.&lt;/p&gt;"),
    ),

    VarSpec(
        name="k_dmg_mu", symbol="k_dmg_mu", unit="-", group="damage", category="form",
        context={"baseline": "transverse", "overrides": {"c_D": 2.0, "k_dmg_wear": 4.0}},
        sweep=(0, 3.0, 15, "lin"), related=["c_D"],
        equation="mu_bearing_eff = mu_bearing * max(1 - k_dmg_mu * D, 0)",
        physics_pt=(
            "&lt;p&gt;Acoplamento do dano ao ATRITO da face de bearing. Conforme a superfície "
            "se danifica (D cresce), o atrito efetivo de assentamento cai: a face "
            "amassada/adesivada perde capacidade de segurar o parafuso. O coeficiente "
            "&lt;code&gt;k_dmg_mu&lt;/code&gt; fixa a intensidade desse efeito; 0 = OFF (o atrito "
            "não se degrada).&lt;/p&gt;"
            "&lt;p&gt;Na equação &amp;mu;_bearing_eff = &amp;mu;&amp;middot;max(1 &amp;minus; k_dmg_mu&amp;middot;D, 0), "
            "o &amp;mu; efetivo é lido no INÍCIO do ciclo pelo torque resistivo e pelo wear. "
            "Menos atrito significa menos torque resistindo ao afrouxamento &amp;rarr; o "
            "afrouxamento rotacional acelera e a curva desaba. Subir o slider (0&amp;hellip;3) "
            "faz o atrito colapsar mais cedo a medida que o dano avança. O sinal é OPOSTO "
            "ao galling de flanco de rosca (&lt;code&gt;k_gall&lt;/code&gt;), que ELEVA o atrito visto "
            "no aperto.&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in do &lt;b&gt;colapso de reaperto/TP7&lt;/b&gt; &amp;minus; a queda abrupta que o "
            "conjunto pré-dano não reproduzia. Companheiros &lt;code&gt;c_D&lt;/code&gt;=2 e "
            "&lt;code&gt;k_dmg_wear&lt;/code&gt;=4 ligados para o acoplamento aparecer.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Coupling of damage to bearing-face FRICTION. As the surface is damaged "
            "(D grows), the effective seating friction falls: the battered/galled face "
            "loses its grip on the bolt. The coefficient &lt;code&gt;k_dmg_mu&lt;/code&gt; sets the "
            "strength of this effect; 0 = OFF (friction does not degrade).&lt;/p&gt;"
            "&lt;p&gt;In &amp;mu;_bearing_eff = &amp;mu;&amp;middot;max(1 &amp;minus; k_dmg_mu&amp;middot;D, 0), the "
            "effective &amp;mu; is read at the START of the cycle by the resisting torque and "
            "by wear. Less friction means less torque opposing loosening &amp;rarr; rotational "
            "loosening accelerates and the curve collapses. Raising the slider (0&amp;hellip;3) "
            "makes friction collapse earlier as damage advances. The sign is OPPOSITE to "
            "thread-flank galling (&lt;code&gt;k_gall&lt;/code&gt;), which RAISES the friction seen "
            "during tightening.&lt;/p&gt;"
            "&lt;p&gt;Opt-in form of the &lt;b&gt;retighten/TP7 collapse&lt;/b&gt; &amp;minus; the abrupt drop the "
            "pre-damage set could not reproduce. Companions &lt;code&gt;c_D&lt;/code&gt;=2 and "
            "&lt;code&gt;k_dmg_wear&lt;/code&gt;=4 are enabled so the coupling shows.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 mu_bearing_eff &amp;minus; dano reduz o atrito de bearing",
               "&amp;sect;5.2 mu_bearing_eff &amp;minus; damage lowers bearing friction",
               "MODEL_MATH_REFERENCE.md"),
              ("staged-calibration-leverage &amp;minus; surface_damage (colapso reaperto/TP7)",
               "staged-calibration-leverage &amp;minus; surface_damage (retighten/TP7 collapse)",
               "specs/2026-06-20-staged-calibration-leverage-design.md")]),

    VarSpec(
        name="k_dmg_wear", symbol="k_dmg_wear", unit="-", group="damage", category="form",
        context={"baseline": "transverse", "overrides": {"c_D": 2.0, "k_dmg_mu": 1.0}},
        sweep=(0, 8.0, 15, "lin"), related=["c_D"],
        equation="d_wear *= (1 + k_dmg_wear * D)   (amplifica dF_0, NAO dE)",
        physics_pt=(
            "&lt;p&gt;Acoplamento do dano a AMPLIFICAÇÃO do desgaste. Uma superfície danificada "
            "(mais debris, mais aspera) remove material mais rápido para o mesmo slip. O "
            "coeficiente &lt;code&gt;k_dmg_wear&lt;/code&gt; multiplica a profundidade de wear por "
            "ciclo pelo fator (1 + k_dmg_wear&amp;middot;D); 0 = OFF.&lt;/p&gt;"
            "&lt;p&gt;Ponto sutil de conservação: a amplificação entra no dF_0 (a perda extra "
            "de pré-carga por remoção de material, balanceada via U_released) mas NÃO no "
            "dE &amp;minus; o calor de atrito contínua sendo o trabalho real; amplificar dE também "
            "quebraria a conservação (~40% de residual). Em modo de deslocamento o wear "
            "DOMINA a perda de pré-carga, por isso o dano acopla ao wear e não só ao "
            "atrito. Subir o slider (0&amp;hellip;8) deixa o colapso tardio mais íngreme.&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in do colapso reaperto/TP7; companheiros &lt;code&gt;c_D&lt;/code&gt;=2 e "
            "&lt;code&gt;k_dmg_mu&lt;/code&gt;=1 ligados.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Coupling of damage to wear AMPLIFICATION. A damaged surface (more debris, "
            "rougher) removes material faster for the same slip. The coefficient "
            "&lt;code&gt;k_dmg_wear&lt;/code&gt; multiplies the per-cycle wear depth by the factor "
            "(1 + k_dmg_wear&amp;middot;D); 0 = OFF.&lt;/p&gt;"
            "&lt;p&gt;Subtle conservation point: the amplification enters dF_0 (the extra "
            "preload loss from material removal, balanced via U_released) but NOT dE &amp;minus; the "
            "friction heat stays the real work; amplifying dE too would break conservation "
            "(~40% residual). In displacement mode wear DOMINATES the preload loss, which "
            "is why damage couples to wear and not only to friction. Raising the slider "
            "(0&amp;hellip;8) makes the late collapse steeper.&lt;/p&gt;"
            "&lt;p&gt;Opt-in form of the retighten/TP7 collapse; companions &lt;code&gt;c_D&lt;/code&gt;=2 "
            "and &lt;code&gt;k_dmg_mu&lt;/code&gt;=1 are enabled.&lt;/p&gt;"),
        refs=[("&amp;sect;4.3 WearLoss &amp;minus; d_wear *= (1 + k_dmg_wear*D) (dF_0 sim, dE não)",
               "&amp;sect;4.3 WearLoss &amp;minus; d_wear *= (1 + k_dmg_wear*D) (dF_0 yes, dE no)",
               "MODEL_MATH_REFERENCE.md"),
              ("staged-calibration-leverage &amp;minus; design do surface_damage",
               "staged-calibration-leverage &amp;minus; surface_damage design",
               "specs/2026-06-20-staged-calibration-leverage-design.md")]),

    VarSpec(
        name="W_crit", symbol="W_crit", unit="J", group="damage", category="form",
        context={"baseline": "transverse",
                 "overrides": {"c_D": 2.0, "k_dmg_mu": 1.0, "k_dmg_wear": 4.0}},
        sweep=(0, 5e4, 15, "lin"), related=["dmg_onset_sharpness"],
        equation="g_onset = x^k / (x^k + 1),  x = W_slip_acc / W_crit,  k = dmg_onset_sharpness",
        physics_pt=(
            "&lt;p&gt;Dose CRÍTICA de fretting para o início do dano. O crescimento de D fica "
            "represado enquanto o trabalho de slip cru acumulado (&lt;code&gt;W_slip_acc&lt;/code&gt;) "
            "não cruza &lt;code&gt;W_crit&lt;/code&gt; &amp;minus; modela a incubação antes de o dano ficar "
            "ativo. É um gate de Hill sobre o incremento de dano.&lt;/p&gt;"
            "&lt;p&gt;Na equação g_onset = x^k/(x^k+1) com x = W_slip_acc/W_crit, o fator g_onset "
            "multiplica dD. &lt;code&gt;W_crit&lt;/code&gt;=0 deixa o gate transparente "
            "(retrocompatível). Aumentar &lt;code&gt;W_crit&lt;/code&gt; alonga a incubação &amp;rarr; o "
            "joelho do colapso vem mais tarde. Só é lido no caminho legado "
            "(&lt;code&gt;dmg_gross_exp&lt;/code&gt;=0). A nitidez do gate é o companheiro "
            "&lt;code&gt;dmg_onset_sharpness&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in do gatilho preditivo de dano (spec 2026-07-05). Depois "
            "FALSIFICADO como chave por-caso (a dose é dominada por F_0, não separa "
            "colapso de platô) e SUPERADO pelo onset contínuo &lt;code&gt;dmg_gross_exp&lt;/code&gt;; "
            "mantido como opção.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;CRITICAL fretting dose for damage onset. The growth of D is held back "
            "while the accumulated raw slip work (&lt;code&gt;W_slip_acc&lt;/code&gt;) has not crossed "
            "&lt;code&gt;W_crit&lt;/code&gt; &amp;minus; it models the incubation before damage becomes active. "
            "It is a Hill gate on the damage increment.&lt;/p&gt;"
            "&lt;p&gt;In g_onset = x^k/(x^k+1) with x = W_slip_acc/W_crit, the g_onset factor "
            "multiplies dD. &lt;code&gt;W_crit&lt;/code&gt;=0 leaves the gate transparent "
            "(backward-compat). Raising &lt;code&gt;W_crit&lt;/code&gt; lengthens the incubation "
            "&amp;rarr; the collapse knee comes later. It is only read on the legacy path "
            "(&lt;code&gt;dmg_gross_exp&lt;/code&gt;=0). The gate sharpness is the companion "
            "&lt;code&gt;dmg_onset_sharpness&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Opt-in form of the predictive damage trigger (spec 2026-07-05). Later "
            "FALSIFIED as a per-case switch (the dose is F_0-dominated, it cannot separate "
            "collapse from plateau) and SUPERSEDED by the continuous "
            "&lt;code&gt;dmg_gross_exp&lt;/code&gt; onset; kept as an option.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 damage_onset_gate &amp;minus; dose crítica de fretting",
               "&amp;sect;5.2 damage_onset_gate &amp;minus; critical fretting dose",
               "MODEL_MATH_REFERENCE.md"),
              ("predictive damage trigger &amp;minus; design (depois falsificado como chave per-caso)",
               "predictive damage trigger &amp;minus; design (later falsified as a per-case switch)",
               "specs/2026-07-05-predictive-damage-trigger-design.md")]),

    VarSpec(
        name="dmg_onset_sharpness", symbol="k_onset", unit="-", group="damage",
        category="form",
        context={"baseline": "transverse",
                 "overrides": {"c_D": 2.0, "k_dmg_wear": 4.0, "W_crit": 1e4}},
        sweep=(1.0, 8.0, 15, "lin"), related=["W_crit"],
        equation="g_onset = x^k / (x^k + 1),  x = W_slip_acc / W_crit,  k = dmg_onset_sharpness",
        physics_pt=(
            "&lt;p&gt;Nitidez do gate de Hill que liga o dano em &lt;code&gt;W_crit&lt;/code&gt;. Controla "
            "quão ABRUPTA é a transição de dano-suprimido (platô) para dano-ativo "
            "(colapso): é o expoente k na sigmoide g_onset = x^k/(x^k+1), com "
            "x = W_slip_acc/W_crit. Só é lido se &lt;code&gt;W_crit&lt;/code&gt; &amp;gt; 0.&lt;/p&gt;"
            "&lt;p&gt;Mover o slider (1&amp;hellip;8) muda a forma do joelho: k grande = platô mais "
            "chato seguido de disparo súbito; k pequeno = rampa suave. É a mesma forma de "
            "Hill do &lt;code&gt;slip_onset_sharpness&lt;/code&gt; (incubação de estágio 1). Default "
            "4; companheiro &lt;code&gt;W_crit&lt;/code&gt;, que fixa ONDE o gate liga.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Sharpness of the Hill gate that turns damage on at &lt;code&gt;W_crit&lt;/code&gt;. It "
            "controls how ABRUPT the transition from damage-suppressed (plateau) to "
            "damage-active (collapse) is: it is the exponent k in the sigmoid "
            "g_onset = x^k/(x^k+1), with x = W_slip_acc/W_crit. It is only read if "
            "&lt;code&gt;W_crit&lt;/code&gt; &amp;gt; 0.&lt;/p&gt;"
            "&lt;p&gt;Moving the slider (1&amp;hellip;8) changes the knee shape: large k = a flatter "
            "plateau then a sudden trigger; small k = a gentle ramp. It is the same Hill "
            "form as &lt;code&gt;slip_onset_sharpness&lt;/code&gt; (stage-1 incubation). Default 4; "
            "companion &lt;code&gt;W_crit&lt;/code&gt;, which sets WHERE the gate turns on.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 damage_onset_gate &amp;minus; nitidez do gate Hill de onset",
               "&amp;sect;5.2 damage_onset_gate &amp;minus; onset Hill-gate sharpness",
               "MODEL_MATH_REFERENCE.md"),
              ("predictive damage trigger &amp;minus; design",
               "predictive damage trigger &amp;minus; design",
               "specs/2026-07-05-predictive-damage-trigger-design.md")]),

    VarSpec(
        name="dmg_gross_exp", symbol="n_gross", unit="-", group="damage", category="form",
        context={"baseline": "transverse",
                 "overrides": {"c_D": 2.0, "k_dmg_mu": 1.0, "k_dmg_wear": 4.0, "k_tr_mode": "bending", "W_crit": 8000.0}},
        sweep=(0, 3.0, 15, "lin"), related=["c_D"],
        equation="onset = g_gross ^ dmg_gross_exp,  g_gross = slip/(slip + delta_t),  delta_t = mu*F_0/k_tr",
        physics_pt=(
            "&lt;p&gt;Onset CONTÍNUO do dano pela fração de gross-slip, substituindo o limiar de "
            "energia &lt;code&gt;W_crit&lt;/code&gt;. A fração g_gross = slip/(slip + &lt;code&gt;delta_t&lt;/code&gt;) "
            "é a razão física de super-criticalidade s_a/s_crit, onde s_crit = "
            "&lt;code&gt;delta_t&lt;/code&gt; = &amp;mu;&amp;middot;F_0/k_tr CAI com F_0 (o falling F_V do "
            "Bauer). É, portanto, dependente de F_0.&lt;/p&gt;"
            "&lt;p&gt;Na equação onset = g_gross^n, o fator multiplica dD: ~0 no platô (F_0 "
            "alto, sub-crítico) e &amp;rarr;1 quando F_0 cai (super-crítico), gerando um "
            "joelho cuja NITIDEZ emerge da própria trajetória de g_gross. Aumentar o "
            "expoente afia o joelho. &lt;code&gt;dmg_gross_exp&lt;/code&gt;=0 volta ao "
            "&lt;code&gt;W_crit&lt;/code&gt; legado. Usa o baseline com &lt;code&gt;k_tr_mode&lt;/code&gt;="
            "&lt;code&gt;bending&lt;/code&gt; para que &lt;code&gt;delta_t&lt;/code&gt; seja não-nulo (senão "
            "g_gross&amp;approx;1).&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in (spec 2026-07-08, pedido do professor: fig6 e fig8 do Bauer = "
            "MESMA física, joelho contínuo, não chave por-caso). Companheiro "
            "&lt;code&gt;c_D&lt;/code&gt;.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;CONTINUOUS damage onset via the gross-slip fraction, replacing the energy "
            "threshold &lt;code&gt;W_crit&lt;/code&gt;. The fraction g_gross = slip/(slip + "
            "&lt;code&gt;delta_t&lt;/code&gt;) is the physical super-criticality ratio s_a/s_crit, "
            "where s_crit = &lt;code&gt;delta_t&lt;/code&gt; = &amp;mu;&amp;middot;F_0/k_tr FALLS with F_0 "
            "(Bauer's falling F_V). It is therefore F_0-dependent.&lt;/p&gt;"
            "&lt;p&gt;In onset = g_gross^n, the factor multiplies dD: ~0 on the plateau (F_0 "
            "high, sub-critical) and &amp;rarr;1 once F_0 falls (super-critical), producing a "
            "knee whose SHARPNESS emerges from the g_gross trajectory itself. Raising the "
            "exponent sharpens the knee. &lt;code&gt;dmg_gross_exp&lt;/code&gt;=0 reverts to the "
            "legacy &lt;code&gt;W_crit&lt;/code&gt;. The baseline uses &lt;code&gt;k_tr_mode&lt;/code&gt;="
            "&lt;code&gt;bending&lt;/code&gt; so &lt;code&gt;delta_t&lt;/code&gt; is nonzero (otherwise "
            "g_gross&amp;approx;1).&lt;/p&gt;"
            "&lt;p&gt;Opt-in form (spec 2026-07-08, professor's request: Bauer fig6 and fig8 = "
            "the SAME physics, a continuous knee, not a per-case switch). Companion "
            "&lt;code&gt;c_D&lt;/code&gt;.&lt;/p&gt;"),
        refs=[("&amp;sect;4 onset contínuo do dano por fração de gross-slip",
               "&amp;sect;4 continuous damage onset via gross-slip fraction",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.33 MODEL_LEGITIMACY &amp;minus; joelho de Bauer (fig6 e fig8 = mesma física)",
               "&amp;sect;4.33 MODEL_LEGITIMACY &amp;minus; Bauer knee (fig6 and fig8 = same physics)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="dmg_dwell_exp", symbol="p_dwell", unit="-", group="damage", category="form",
        context={"baseline": "transverse",
                 "overrides": {"c_D": 2.0, "k_dmg_wear": 4.0}},
        sweep=(0, 2.0, 15, "lin"), related=["f_ref_dmg"],
        equation="dD *= (f_ref_dmg / f) ^ dmg_dwell_exp",
        physics_pt=(
            "&lt;p&gt;Fator de DWELL do dano (fretting-corrosão). Frequência menor significa "
            "mais tempo de contato por ciclo, mais oxidação durante o dwell, e portanto "
            "mais dano por ciclo. O expoente &lt;code&gt;dmg_dwell_exp&lt;/code&gt; mede a força "
            "dessa dependência de frequência; 0 = OFF (fator = 1).&lt;/p&gt;"
            "&lt;p&gt;Na equação dD *= (&lt;code&gt;f_ref_dmg&lt;/code&gt;/f)^p, o fator só vale 1 quando a "
            "frequência do ensaio iguala a de referência. No baseline a 0.5 Hz (bem "
            "abaixo do f_ref padrão de 10 Hz) a razão (10/0.5) é grande, então subir o "
            "slider amplifica fortemente o dano. Foi nomeado pelo par Yang 5/10 Hz: as "
            "curvas ~coincidem no TEMPO até o ramo de 5 Hz entrar em colapso terminal que "
            "o de 10 Hz nunca alcança &amp;rarr; dose vezes dwell, não só tempo.&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in; companheiro &lt;code&gt;f_ref_dmg&lt;/code&gt; (a âncora de "
            "frequência).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Damage DWELL factor (fretting-corrosion). Lower frequency means more "
            "contact time per cycle, more oxidation during the dwell, and therefore more "
            "damage per cycle. The exponent &lt;code&gt;dmg_dwell_exp&lt;/code&gt; sets the strength "
            "of that frequency dependence; 0 = OFF (factor = 1).&lt;/p&gt;"
            "&lt;p&gt;In dD *= (&lt;code&gt;f_ref_dmg&lt;/code&gt;/f)^p, the factor is 1 only when the test "
            "frequency equals the reference. At the 0.5 Hz baseline (well below the "
            "default 10 Hz f_ref) the ratio (10/0.5) is large, so raising the slider "
            "strongly amplifies damage. It was named by the Yang 5/10 Hz pair: the curves "
            "~coincide in TIME until the 5 Hz branch enters a terminal collapse the 10 Hz "
            "never reaches &amp;rarr; dose times dwell, not just time.&lt;/p&gt;"
            "&lt;p&gt;Opt-in form; companion &lt;code&gt;f_ref_dmg&lt;/code&gt; (the frequency anchor).&lt;/p&gt;"),
        refs=[("&amp;sect;6 fator de dwell do dano (fretting-corrosão)",
               "&amp;sect;6 damage dwell factor (fretting-corrosion)",
               "MODEL_MATH_REFERENCE.md"),
              ("Vingsbo &amp;amp; Soderberg (1988) &amp;minus; mapas de fretting / dose de óxido no dwell",
               "Vingsbo &amp;amp; Soderberg (1988) &amp;minus; fretting maps / oxide dose during dwell",
               "vingsbo1988")]),

    VarSpec(
        name="f_ref_dmg", symbol="f_ref,dmg", unit="Hz", group="damage", category="form",
        context={"baseline": "transverse",
                 "overrides": {"c_D": 2.0, "k_dmg_wear": 4.0, "dmg_dwell_exp": 1.0}},
        sweep=(5, 20, 15, "lin"), related=["dmg_dwell_exp"],
        equation="dD *= (f_ref_dmg / f) ^ dmg_dwell_exp   (= 1 quando f = f_ref_dmg)",
        physics_pt=(
            "&lt;p&gt;Frequência de REFERÊNCIA do fator de dwell do dano. O multiplicador "
            "(&lt;code&gt;f_ref_dmg&lt;/code&gt;/f)^p vale exatamente 1 quando a frequência do ensaio "
            "iguala &lt;code&gt;f_ref_dmg&lt;/code&gt;; abaixo dela o dano por ciclo sobe (mais dwell, "
            "mais óxido), acima dela cai. É a âncora per-rig que fixa onde o dwell é "
            "neutro.&lt;/p&gt;"
            "&lt;p&gt;Só é lido se &lt;code&gt;dmg_dwell_exp&lt;/code&gt; &amp;gt; 0 (aqui o companheiro está "
            "em 1.0). No baseline a 0.5 Hz, aumentar &lt;code&gt;f_ref_dmg&lt;/code&gt; aumenta a "
            "razão (f_ref/0.5) &amp;rarr; mais dano por ciclo, então o slider desloca a "
            "posição do colapso. Default 10 Hz.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;REFERENCE frequency of the damage dwell factor. The multiplier "
            "(&lt;code&gt;f_ref_dmg&lt;/code&gt;/f)^p equals exactly 1 when the test frequency equals "
            "&lt;code&gt;f_ref_dmg&lt;/code&gt;; below it the damage per cycle rises (more dwell, more "
            "oxide), above it falls. It is the per-rig anchor that sets where the dwell is "
            "neutral.&lt;/p&gt;"
            "&lt;p&gt;It is only read if &lt;code&gt;dmg_dwell_exp&lt;/code&gt; &amp;gt; 0 (the companion is "
            "1.0 here). At the 0.5 Hz baseline, raising &lt;code&gt;f_ref_dmg&lt;/code&gt; raises the "
            "ratio (f_ref/0.5) &amp;rarr; more damage per cycle, so the slider shifts the "
            "collapse position. Default 10 Hz.&lt;/p&gt;"),
        refs=[("&amp;sect;6 frequência de referência do dwell do dano (âncora per-rig)",
               "&amp;sect;6 reference frequency of the damage dwell (per-rig anchor)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.39 MODEL_LEGITIMACY &amp;minus; emb prop 1/freq (dwell/oxidação, r=-0.99)",
               "&amp;sect;4.39 MODEL_LEGITIMACY &amp;minus; emb prop 1/freq (dwell/oxidation, r=-0.99)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="slip_onset_W", symbol="W_onset", unit="J", group="conformation",
        category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0, 5e4, 15, "lin"), related=["slip_onset_sharpness"],
        equation="g = x^k / (x^k + 1),  x = W_slip_acc / slip_onset_W,  k = slip_onset_sharpness",
        physics_pt=(
            "&lt;p&gt;Limiar de INCUBAÇÃO do estágio 1 (forma de 3 estágios do Junker). A perda "
            "de pré-carga dirigida por slip (wear + afrouxamento rotacional) fica "
            "suprimida até o trabalho de slip CRU acumulado (&lt;code&gt;W_slip_acc&lt;/code&gt;) "
            "cruzar &lt;code&gt;slip_onset_W&lt;/code&gt; &amp;minus; é o platô chato antes do colapso.&lt;/p&gt;"
            "&lt;p&gt;O gate de Hill g = x^k/(x^k+1), com x = W_slip_acc/slip_onset_W, gateia o "
            "dF_0 mas NÃO o dE: o micro-slip ainda dissipa calor e alimenta "
            "&lt;code&gt;W_slip_acc&lt;/code&gt;, logo o onset não se desloca ao ajustar k_wear/"
            "k_loose (o acumulador é cru, independente dos tuners de mecanismo). "
            "&lt;code&gt;slip_onset_W&lt;/code&gt;=0 = sem incubação (gate = 1). Aumentar "
            "&lt;code&gt;slip_onset_W&lt;/code&gt; alonga o platô, produzindo platô &amp;rarr; colapso "
            "&amp;rarr; saturação.&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in (estágio I de Jiang no ensaio Junker); companheiro "
            "&lt;code&gt;slip_onset_sharpness&lt;/code&gt;.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Stage-1 INCUBATION threshold (Junker 3-stage shape). The slip-driven "
            "preload loss (wear + rotational loosening) stays suppressed until the "
            "accumulated RAW slip work (&lt;code&gt;W_slip_acc&lt;/code&gt;) crosses "
            "&lt;code&gt;slip_onset_W&lt;/code&gt; &amp;minus; it is the flat plateau before the collapse.&lt;/p&gt;"
            "&lt;p&gt;The Hill gate g = x^k/(x^k+1), with x = W_slip_acc/slip_onset_W, gates "
            "dF_0 but NOT dE: micro-slip still dissipates heat and feeds "
            "&lt;code&gt;W_slip_acc&lt;/code&gt;, so the onset does not move when k_wear/k_loose are "
            "tuned (the accumulator is raw, tuner-independent). &lt;code&gt;slip_onset_W&lt;/code&gt;=0 "
            "= no incubation (gate = 1). Raising &lt;code&gt;slip_onset_W&lt;/code&gt; lengthens the "
            "plateau, producing plateau &amp;rarr; collapse &amp;rarr; saturation.&lt;/p&gt;"
            "&lt;p&gt;Opt-in form (Jiang stage I of the Junker test); companion "
            "&lt;code&gt;slip_onset_sharpness&lt;/code&gt;.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 slip_onset_gate &amp;minus; incubação do estágio I (Junker 3-estágios)",
               "&amp;sect;5.2 slip_onset_gate &amp;minus; stage-I incubation (Junker 3-stage)",
               "MODEL_MATH_REFERENCE.md"),
              ("Junker (1969) &amp;minus; ensaio de vibração transversal (base do DIN 65151)",
               "Junker (1969) &amp;minus; transverse vibration test (basis of DIN 65151)",
               "junker1969")]),

    VarSpec(
        name="slip_onset_sharpness", symbol="k_slip", unit="-", group="conformation",
        category="form",
        context={"baseline": "transverse", "overrides": {"slip_onset_W": 1e4}},
        sweep=(1.0, 8.0, 15, "lin"), related=["slip_onset_W"],
        equation="g = x^k / (x^k + 1),  x = W_slip_acc / slip_onset_W,  k = slip_onset_sharpness",
        physics_pt=(
            "&lt;p&gt;Nitidez do gate de incubação do estágio 1. É o expoente k na sigmoide de "
            "Hill g = x^k/(x^k+1), com x = W_slip_acc/&lt;code&gt;slip_onset_W&lt;/code&gt;, que "
            "controla quão ABRUPTA é a passagem do platô (estágio 1) para o colapso "
            "(estágio 2). Só é lido se &lt;code&gt;slip_onset_W&lt;/code&gt; &amp;gt; 0.&lt;/p&gt;"
            "&lt;p&gt;Mover o slider (1&amp;hellip;8) muda a forma do joelho: k grande = platô mais "
            "chato e queda súbita; k pequeno = transição gradual. Default 4; companheiro "
            "&lt;code&gt;slip_onset_W&lt;/code&gt;, que fixa QUANDO (em dose de slip acumulada) a "
            "incubação termina.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Sharpness of the stage-1 incubation gate. It is the exponent k in the Hill "
            "sigmoid g = x^k/(x^k+1), with x = W_slip_acc/&lt;code&gt;slip_onset_W&lt;/code&gt;, which "
            "controls how ABRUPT the passage from plateau (stage 1) to collapse (stage 2) "
            "is. It is only read if &lt;code&gt;slip_onset_W&lt;/code&gt; &amp;gt; 0.&lt;/p&gt;"
            "&lt;p&gt;Moving the slider (1&amp;hellip;8) changes the knee shape: large k = a flatter "
            "plateau and a sudden drop; small k = a gradual transition. Default 4; "
            "companion &lt;code&gt;slip_onset_W&lt;/code&gt;, which sets WHEN (in accumulated slip "
            "dose) the incubation ends.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 slip_onset_gate &amp;minus; nitidez do gate Hill de incubação",
               "&amp;sect;5.2 slip_onset_gate &amp;minus; incubation Hill-gate sharpness",
               "MODEL_MATH_REFERENCE.md")]),

    VarSpec(
        name="W_conf_ref", symbol="W_conf", unit="J", group="conformation",
        category="physical",
        context={"baseline": "transverse",
                 "overrides": {"conform_driver": "effective", "conform_pressure_exp": 2.0}},
        sweep=(0, 2e4, 15, "lin"), related=["conform_driver"],
        equation="conformation_gate = W_conf_ref/(W_conf + W_conf_ref);   dW_conf = (p/p_ref)^n * (4*mu*F_0*slip)",
        physics_pt=(
            "&lt;p&gt;Energia de referência do ARRESTO por conformação dependente de pressão. O "
            "contato de alta pressão se conforma (assenta/plateia) e arresta "
            "progressivamente a perda de pré-carga dirigida por slip. O acumulador "
            "&lt;code&gt;W_conf&lt;/code&gt; soma o trabalho de slip ponderado pela pressão, e o gate "
            "W_conf_ref/(W_conf + W_conf_ref) FECHA de 1 para 0.&lt;/p&gt;"
            "&lt;p&gt;Maior &lt;code&gt;W_conf_ref&lt;/code&gt; mantém o gate aberto por mais tempo &amp;rarr; "
            "menos arresto &amp;rarr; mais afrouxamento; menor arresta mais cedo (platô mais "
            "alto). 0 = OFF. É o mecanismo que resolve o SOBRETORQUE (pré-carga alta): "
            "em F_0 alto a ponderação de pressão enche &lt;code&gt;W_conf&lt;/code&gt; rápido e a "
            "perda se auto-arresta. Companheiro &lt;code&gt;conform_driver&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Constante física ADOTADA no bloco &lt;code&gt;shared&lt;/code&gt; canônico "
            "(2026-07-04; sobretorque 0.138&amp;rarr;0.030 &amp;minus; primeira promoção de um "
            "experimento ao canônico). Valor UFU por-par ~7671 J. A âncora da Fase 3 "
            "FALHOU (nenhum dado da biblioteca a isola), então permanece por-par, um "
            "degrau abaixo do C_creep; calibrada na escala UFU (caveat de escala).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Reference energy of the pressure-dependent conformation ARREST. The "
            "high-pressure contact conforms (beds/plateaus) and progressively arrests the "
            "slip-driven preload loss. The accumulator &lt;code&gt;W_conf&lt;/code&gt; sums the "
            "pressure-weighted slip work, and the gate W_conf_ref/(W_conf + W_conf_ref) "
            "CLOSES from 1 to 0.&lt;/p&gt;"
            "&lt;p&gt;Larger &lt;code&gt;W_conf_ref&lt;/code&gt; keeps the gate open longer &amp;rarr; less "
            "arrest &amp;rarr; more loosening; smaller arrests earlier (higher plateau). "
            "0 = OFF. It is the mechanism that resolves the OVERTORQUE (high-preload) "
            "case: at high F_0 the pressure weighting fills &lt;code&gt;W_conf&lt;/code&gt; fast and "
            "the loss self-arrests. Companion &lt;code&gt;conform_driver&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Physical constant ADOPTED into the canonical &lt;code&gt;shared&lt;/code&gt; block "
            "(2026-07-04; overtorque 0.138&amp;rarr;0.030 &amp;minus; the first promotion of an "
            "experiment to canonical). UFU per-pair value ~7671 J. The Phase-3 anchor "
            "FAILED (no library data isolates it), so it stays per-pair, one step below "
            "C_creep; calibrated at the UFU scale (scale caveat).&lt;/p&gt;"),
        refs=[("&amp;sect;6 / &amp;sect;4.9 conformação dependente de pressão (ADOTADA no shared)",
               "&amp;sect;6 / &amp;sect;4.9 pressure-dependent conformation (ADOPTED in shared)",
               "MODEL_MATH_REFERENCE.md"),
              ("pressure-conformation &amp;minus; design (resolve o sobretorque)",
               "pressure-conformation &amp;minus; design (resolves overtorque)",
               "specs/2026-07-04-pressure-conformation-design.md"),
              ("&amp;sect;4.9 MODEL_LEGITIMACY &amp;minus; âncora de W_conf_ref FALHOU (per-par)",
               "&amp;sect;4.9 MODEL_LEGITIMACY &amp;minus; W_conf_ref anchor FAILED (per-pair)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(
        name="conform_pressure_exp", symbol="n_conf,p", unit="-", group="conformation",
        category="form",
        context={"baseline": "transverse",
                 "overrides": {"conform_driver": "effective", "W_conf_ref": 7671.0}},
        sweep=(1.0, 3.0, 15, "lin"), anchor_key="conform_pressure_exp",
        related=["W_conf_ref"],
        equation="dW_conf = (p / p_ref_conform) ^ conform_pressure_exp * (4*mu*F_0*slip),  p = F_0/A_contact",
        physics_pt=(
            "&lt;p&gt;Expoente de PRESSÃO que pondera o trabalho de slip no acumulador de "
            "conformação: dW_conf = (p/&lt;code&gt;p_ref_conform&lt;/code&gt;)^n com p = F_0/A_contact. "
            "Controla quão fortemente a alta pressão de contato acelera a conformação.&lt;/p&gt;"
            "&lt;p&gt;Maior n faz o caso de sobretorque (pressão elevada) conformar/arrestar "
            "muito mais rápido que o caso nominal &amp;minus; é a SEPARAÇÃO por pré-carga entre as "
            "condições. n=2 é FIXO (VDI) no bloco &lt;code&gt;shared&lt;/code&gt; canônico; o baseline "
            "liga &lt;code&gt;conform_driver&lt;/code&gt;=&lt;code&gt;effective&lt;/code&gt; e "
            "&lt;code&gt;W_conf_ref&lt;/code&gt;=7671. A leitura de proveniência abaixo do gráfico "
            "avisa quando o valor sai da banda medida.&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in com âncora &lt;code&gt;conform_pressure_exp&lt;/code&gt; = "
            "liu2021 (perda estática de 48h sem carga vs pré-carga): o expoente medido "
            "confirma o crescimento superlinear com F_0, banda n em [1.4, 2.0] (veredicto "
            "BANDA).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;PRESSURE exponent that weights the slip work in the conformation "
            "accumulator: dW_conf = (p/&lt;code&gt;p_ref_conform&lt;/code&gt;)^n with p = "
            "F_0/A_contact. It controls how strongly high contact pressure accelerates "
            "conformation.&lt;/p&gt;"
            "&lt;p&gt;A larger n makes the overtorque (high-pressure) case conform/arrest much "
            "faster than the nominal case &amp;minus; this is the SEPARATION by preload between the "
            "conditions. n=2 is FIXED (VDI) in the canonical &lt;code&gt;shared&lt;/code&gt; block; "
            "the baseline enables &lt;code&gt;conform_driver&lt;/code&gt;=&lt;code&gt;effective&lt;/code&gt; and "
            "&lt;code&gt;W_conf_ref&lt;/code&gt;=7671. The provenance readout under the plot flags "
            "when the value leaves the measured band.&lt;/p&gt;"
            "&lt;p&gt;Opt-in form with anchor &lt;code&gt;conform_pressure_exp&lt;/code&gt; = liu2021 (48 h "
            "static no-load loss vs preload): the measured exponent confirms the "
            "super-linear growth with F_0, band n in [1.4, 2.0] (verdict BANDA).&lt;/p&gt;"),
        refs=[("&amp;sect;6 expoente de pressão (p/p_ref)^n da conformação",
               "&amp;sect;6 conformation pressure exponent (p/p_ref)^n",
               "MODEL_MATH_REFERENCE.md"),
              ("Liu et al. (2021) &amp;minus; perda sem carga vs pré-carga (banda medida n in [1.4, 2.0])",
               "Liu et al. (2021) &amp;minus; no-load loss vs preload (measured band n in [1.4, 2.0])",
               "liu2021")]),

    VarSpec(
        name="p_ref_conform", symbol="p_ref,conf", unit="Pa", group="conformation",
        category="form",
        context={"baseline": "transverse",
                 "overrides": {"conform_driver": "effective", "W_conf_ref": 7671.0,
                               "conform_pressure_exp": 2.0}},
        sweep=(1e8, 1e9, 15, "log"), related=["W_conf_ref"],
        equation="dW_conf = (p / p_ref_conform) ^ n * (4*mu*F_0*slip),  p = F_0 / A_contact",
        physics_pt=(
            "&lt;p&gt;Pressão de REFERÊNCIA da ponderação de conformação (~80% da tensão de "
            "prova). A pressão de contato p = F_0/A_contact é medida contra "
            "&lt;code&gt;p_ref_conform&lt;/code&gt;; em p = p_ref o peso (p/p_ref)^n vale 1.&lt;/p&gt;"
            "&lt;p&gt;Na equação dW_conf = (p/p_ref_conform)^n&amp;middot;(trabalho de slip), maior "
            "&lt;code&gt;p_ref_conform&lt;/code&gt; diminui a pressão relativa &amp;rarr; conformação mais "
            "fraca (menos arresto); menor deixa mais forte. Default 5e8 Pa (~80% proof, "
            "consistente entre rigs quando A_contact é a área real do anel de bearing). No "
            "Run ela é COMPUTADA do %escoamento da pré-carga (pct/70, roadmap 11f), não "
            "fixa. Companheiro &lt;code&gt;W_conf_ref&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Forma opt-in; a referência de ~80% da carga de prova vem da VDI 2230.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;REFERENCE pressure of the conformation weighting (~80% of proof stress). "
            "The contact pressure p = F_0/A_contact is measured against "
            "&lt;code&gt;p_ref_conform&lt;/code&gt;; at p = p_ref the weight (p/p_ref)^n equals 1.&lt;/p&gt;"
            "&lt;p&gt;In dW_conf = (p/p_ref_conform)^n&amp;middot;(slip work), a larger "
            "&lt;code&gt;p_ref_conform&lt;/code&gt; lowers the relative pressure &amp;rarr; weaker "
            "conformation (less arrest); a smaller one makes it stronger. Default 5e8 Pa "
            "(~80% proof, consistent across rigs once A_contact is the real bearing-ring "
            "area). In the Run it is COMPUTED from the preload %yield (pct/70, roadmap "
            "11f), not fixed. Companion &lt;code&gt;W_conf_ref&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Opt-in form; the ~80% proof-load reference comes from VDI 2230.&lt;/p&gt;"),
        refs=[("&amp;sect;6 pressão de referência da conformação (~80% proof)",
               "&amp;sect;6 conformation reference pressure (~80% proof)",
               "MODEL_MATH_REFERENCE.md"),
              ("VDI 2230 &amp;minus; carga de prova / ~80% do escoamento como referência de pressão",
               "VDI 2230 &amp;minus; proof load / ~80% yield as the pressure reference",
               "VDI 2230")]),

    VarSpec(
        name="conform_driver", symbol="", unit="", group="conformation", category="mode",
        context={"baseline": "transverse",
                 "overrides": {"W_conf_ref": 7671.0, "conform_pressure_exp": 2.0}},
        choices=["raw", "effective"], related=["W_conf_ref"],
        equation='raw: W_conf += dW_conf   |   effective: W_conf += dW_conf * conformation_gate',
        physics_pt=(
            "&lt;p&gt;Seleciona COMO o acumulador de conformação &lt;code&gt;W_conf&lt;/code&gt; é dirigido. "
            "&lt;b&gt;raw&lt;/b&gt; (default): acumula monotonicamente o trabalho de slip cru "
            "ponderado por pressão (retrocompatível bit-a-bit). &lt;b&gt;effective&lt;/b&gt;: "
            "auto-limitante &amp;minus; o incremento é ponderado pelo gate de conformação do INÍCIO "
            "de ciclo, então &lt;code&gt;W_conf&lt;/code&gt; tende a um platô (um plateau, não "
            "um equilíbrio verdadeiro).&lt;/p&gt;"
            "&lt;p&gt;O seletor troca entre as duas curvas pré-computadas. &lt;b&gt;effective&lt;/b&gt; é o "
            "driver de equilíbrio ADOTADO no bloco &lt;code&gt;shared&lt;/code&gt; canônico &amp;minus; é o que "
            "RESOLVE o sobretorque. Companheiro &lt;code&gt;W_conf_ref&lt;/code&gt; (=0 desliga toda "
            "a conformação, independentemente do driver escolhido).&lt;/p&gt;"
            "&lt;p&gt;Modo discreto (spec &amp;sect;7). Um dos três fortalecimentos da Fase 2; adotado "
            "em 2026-07-04 (ver &amp;sect;4.9 do MODEL_LEGITIMACY).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Selects HOW the conformation accumulator &lt;code&gt;W_conf&lt;/code&gt; is driven. "
            "&lt;b&gt;raw&lt;/b&gt; (default): monotonically accumulates the raw pressure-weighted "
            "slip work (bit-identical backward-compat). &lt;b&gt;effective&lt;/b&gt;: self-limiting &amp;minus; "
            "the increment is weighted by the START-of-cycle conformation gate, so "
            "&lt;code&gt;W_conf&lt;/code&gt; approaches a plateau (a plateau, not a true "
            "equilibrium).&lt;/p&gt;"
            "&lt;p&gt;The selector switches between the two pre-computed curves. &lt;b&gt;effective&lt;/b&gt; "
            "is the equilibrium driver ADOPTED into the canonical &lt;code&gt;shared&lt;/code&gt; "
            "block &amp;minus; it is what RESOLVES the overtorque. Companion &lt;code&gt;W_conf_ref&lt;/code&gt; "
            "(=0 turns the whole conformation off, regardless of the chosen driver).&lt;/p&gt;"
            "&lt;p&gt;Discrete mode (spec &amp;sect;7). One of the three Phase-2 strengthenings; adopted "
            "on 2026-07-04 (see MODEL_LEGITIMACY &amp;sect;4.9).&lt;/p&gt;"),
        refs=[("&amp;sect;5.1 driver da conformação: raw (monotônico) vs effective (auto-limitante)",
               "&amp;sect;5.1 conformation driver: raw (monotonic) vs effective (self-limiting)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.9 MODEL_LEGITIMACY &amp;minus; driver effective ADOTADO (3 fortalecimentos)",
               "&amp;sect;4.9 MODEL_LEGITIMACY &amp;minus; effective driver ADOPTED (3 strengthenings)",
               "MODEL_LEGITIMACY.md")]),
])

# =============================== MEMBER + RETIGHTEN + CRASH + NUMERICAL (10) ===============================
VARIABLE_SPECS.extend([
    VarSpec(name="k_member_shear", symbol="k_ms", unit="N/m", group="member", category="form",
        context={"baseline":"transverse","overrides":{"k_tr_mode":"bending"}},
        sweep=(0,5e8,15,"lin"), related=["member_loss_eta"],
        equation="k_tr_eff = 1 / (1/k_tr + 1/k_member_shear);   k_member_shear = G_member * A_shear / t",
        physics_pt=(
            "&lt;p&gt;Nenhuma junta prende o parafuso num apoio infinitamente rígido: o próprio "
            "&lt;b&gt;membro&lt;/b&gt; (as placas apertadas) tem complacência de cisalhamento. Quando a "
            "amplitude transversal é imposta, parte do curso é absorvida pela deformação "
            "elástica do membro e só o restante chega a interface como escorregamento. "
            "&lt;code&gt;k_member_shear&lt;/code&gt; (k_ms = G_membro&amp;middot;A_cisalh/t) é a rigidez de "
            "cisalhamento desse membro, colocada &lt;b&gt;em série&lt;/b&gt; com a rigidez transversal "
            "k_tr: k_tr_eff = 1/(1/k_tr + 1/k_ms).&lt;/p&gt;"
            "&lt;p&gt;Direção física: um membro &lt;b&gt;complacente&lt;/b&gt; (k_ms baixo) rebaixa k_tr_eff, o "
            "que eleva o limiar de escorregamento &amp;delta;_t = &amp;mu;&amp;middot;F_0/k_tr e reduz o "
            "slip por ciclo &amp;rarr; menos wear e menos afrouxamento (curva mais rasa). Um membro "
            "&lt;b&gt;rígido&lt;/b&gt; (k_ms alto) repassa quase todo o curso a interface. Por isso o valor "
            "0 significa &lt;b&gt;OFF&lt;/b&gt; (série ignorada = membro rígido, bit-idêntico); esta página "
            "usa o modo &lt;code&gt;k_tr_mode=bending&lt;/code&gt; para que a série tenha efeito visível.&lt;/p&gt;"
            "&lt;p&gt;Para aço esta pista é &lt;b&gt;desprezível&lt;/b&gt; &amp;minus; o membro metálico é ordens de grandeza "
            "mais rígido que a flexão do parafuso, então a série mal muda k_tr. A forma foi "
            "suprida para membros MOLES: é a chave do caso &lt;b&gt;HDPE&lt;/b&gt; (&amp;sect;4.20), onde o membro "
            "polimérico absorve o curso e explica por que a placa espessa NÃO colapsa (a "
            "hipótese só-flexão ~1/L^3 previa a ordem invertida). O produto G&amp;middot;A é por "
            "par/rig, computado por-caso pelo harness &amp;minus; não um botão universal.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;No joint clamps the bolt against an infinitely rigid support: the &lt;b&gt;member&lt;/b&gt; "
            "(the clamped plates) itself has shear compliance. When the transverse amplitude is "
            "imposed, part of the stroke is absorbed by the member's elastic deformation and only "
            "the remainder reaches the interface as slip. &lt;code&gt;k_member_shear&lt;/code&gt; "
            "(k_ms = G_member&amp;middot;A_shear/t) is that member's shear stiffness, placed &lt;b&gt;in "
            "series&lt;/b&gt; with the transverse stiffness k_tr: k_tr_eff = 1/(1/k_tr + 1/k_ms).&lt;/p&gt;"
            "&lt;p&gt;Physical direction: a &lt;b&gt;compliant&lt;/b&gt; member (low k_ms) lowers k_tr_eff, which "
            "raises the slip onset threshold &amp;delta;_t = &amp;mu;&amp;middot;F_0/k_tr and cuts per-cycle "
            "slip &amp;rarr; less wear and less loosening (shallower curve). A &lt;b&gt;stiff&lt;/b&gt; member "
            "(high k_ms) passes almost the whole stroke to the interface. This is why 0 means "
            "&lt;b&gt;OFF&lt;/b&gt; (series ignored = rigid member, bit-identical); this page uses "
            "&lt;code&gt;k_tr_mode=bending&lt;/code&gt; so the series term has a visible effect.&lt;/p&gt;"
            "&lt;p&gt;For steel this lead is &lt;b&gt;negligible&lt;/b&gt; &amp;minus; the metallic member is orders of "
            "magnitude stiffer than the bolt bending, so the series barely changes k_tr. The form "
            "was supplied for SOFT members: it is the key to the &lt;b&gt;HDPE&lt;/b&gt; case (&amp;sect;4.20), where "
            "the polymeric member absorbs the stroke and explains why the thick plate does NOT "
            "collapse (the bending-only ~1/L^3 hypothesis predicted the inverted order). The "
            "product G&amp;middot;A is per pair/rig, computed per-case by the harness &amp;minus; not a "
            "universal knob.&lt;/p&gt;"),
        refs=[("&amp;sect;5.1 rigidez transversal em série com o cisalhamento de membro",
               "&amp;sect;5.1 transverse stiffness in series with member shear",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.20 HDPE &amp;minus; membro complacente absorve o curso (só-flexão invertia a ordem)",
               "&amp;sect;4.20 HDPE &amp;minus; compliant member absorbs the stroke (bending-only inverted the order)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="member_loss_eta", symbol="eta_m", unit="-", group="member", category="form",
        context={"baseline":"transverse","overrides":{"k_member_shear":1e8,"k_tr_mode":"bending"}},
        sweep=(0,1.0,15,"lin"), related=["k_member_shear"], negligible=True,
        equation="W_m = pi * eta_m * F_tr^2 / k_member_shear   (por ciclo; so se k_member_shear>0 e modo-deslocamento)",
        physics_pt=(
            "&lt;p&gt;Um membro real não só se deforma &amp;minus; ele &lt;b&gt;dissipa&lt;/b&gt;. &lt;code&gt;member_loss_eta&lt;/code&gt; "
            "(&amp;eta;_m) é o fator de perda viscoelástico do membro: por ciclo ele drena um loop de "
            "histerese W_m = &amp;pi;&amp;middot;&amp;eta;_m&amp;middot;F_tr^2/k_member_shear (F_tr = força "
            "transversal). Foi nomeado pelos loops MEDIDOS em polímero, que dissipam 7-8&amp;times; o "
            "que a interface do modelo contabiliza &amp;minus; o excesso é a perda no próprio material do "
            "membro.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Esta variável NÃO move a curva F/F0.&lt;/b&gt; Ela é &lt;b&gt;SÓ energia&lt;/b&gt;: o trabalho "
            "W_m é suprido por W_ext e somado ao canal viscoso, fechando o balanço energético, mas "
            "&lt;b&gt;não toca F_0&lt;/b&gt; (a pré-carga fica bit-idêntica). Ou seja, &amp;eta;_m muda a ÁREA do "
            "loop de histerese (calor dissipado), não a perda de aperto. Mover o slider aqui deixa "
            "a curva de afrouxamento parada &amp;minus; por isso a página está marcada como negligível.&lt;/p&gt;"
            "&lt;p&gt;Quem move a curva é o companheiro &lt;code&gt;k_member_shear&lt;/code&gt; (a rigidez em série, "
            "que muda o slip na interface e portanto F_0). &lt;code&gt;member_loss_eta&lt;/code&gt; só acende "
            "quando k_member_shear&amp;gt;0 e em modo de deslocamento; com &amp;eta;_m=0 o termo é "
            "exatamente OFF. Serve ao orçamento de energia (&amp;sect;4.25) e a comparação com loops de "
            "histerese medidos, não a predição de F/F0.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;A real member does not only deform &amp;minus; it &lt;b&gt;dissipates&lt;/b&gt;. "
            "&lt;code&gt;member_loss_eta&lt;/code&gt; (&amp;eta;_m) is the member's viscoelastic loss factor: each "
            "cycle it drains a hysteresis loop W_m = &amp;pi;&amp;middot;&amp;eta;_m&amp;middot;F_tr^2/k_member_shear "
            "(F_tr = transverse force). It was named by the MEASURED polymer loops, which dissipate "
            "7-8&amp;times; what the model interface accounts for &amp;minus; the excess is the loss in the member "
            "material itself.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;This variable does NOT move the F/F0 curve.&lt;/b&gt; It is &lt;b&gt;ENERGY-ONLY&lt;/b&gt;: the "
            "work W_m is sourced by W_ext and added to the viscous channel, closing the energy "
            "budget, but it &lt;b&gt;never touches F_0&lt;/b&gt; (preload stays bit-identical). That is, "
            "&amp;eta;_m changes the AREA of the hysteresis loop (heat dissipated), not the preload "
            "loss. Moving the slider here leaves the loosening curve unchanged &amp;minus; hence the page is "
            "marked negligible.&lt;/p&gt;"
            "&lt;p&gt;What moves the curve is the companion &lt;code&gt;k_member_shear&lt;/code&gt; (the series "
            "stiffness, which changes interface slip and therefore F_0). "
            "&lt;code&gt;member_loss_eta&lt;/code&gt; only switches on when k_member_shear&amp;gt;0 and in "
            "displacement mode; with &amp;eta;_m=0 the term is exactly OFF. It serves the energy budget "
            "(&amp;sect;4.25) and the comparison with measured hysteresis loops, not the F/F0 "
            "prediction.&lt;/p&gt;"),
        refs=[("&amp;sect;7 roteamento de energia &amp;minus; dissipação SÓ energia (F_0 intocado, suprida por W_ext)",
               "&amp;sect;7 energy routing &amp;minus; energy-only dissipation (F_0 untouched, sourced by W_ext)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.25 MODEL_LEGITIMACY &amp;minus; loops medidos em polímero (7-8x o do modelo)",
               "&amp;sect;4.25 MODEL_LEGITIMACY &amp;minus; measured polymer loops (7-8x the model)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="k_emb_renew", symbol="k_renew", unit="-", group="retighten", category="form",
        context={"baseline":"transverse","overrides":{"c_D":2.0,"k_dmg_mu":1.0,"k_dmg_wear":4.0}},
        sweep=(0,1.0,15,"lin"), related=["k_gall"], negligible=True,
        equation="retighten(): delta_emb <- delta_emb * (1 - k_emb_renew * D),  clamp em [0, delta_target]",
        physics_pt=(
            "&lt;p&gt;Quando uma junta danificada é &lt;b&gt;re-apertada&lt;/b&gt;, as superfícies já machucadas "
            "expõem capacidade de assentamento fresca: o achatamento das asperezas pode "
            "recomeçar. &lt;code&gt;k_emb_renew&lt;/code&gt; controla quanto do embedding já consumido é "
            "&lt;b&gt;reaberto&lt;/b&gt; no re-aperto, proporcional ao dano D: &amp;delta;_emb &amp;larr; "
            "&amp;delta;_emb&amp;middot;(1 &amp;minus; k_emb_renew&amp;middot;D). Com k_emb_renew=0 o re-aperto "
            "preserva o &amp;delta;_emb (backward-compat exato); com valor &amp;gt;0 parte da folga de "
            "assentamento volta a estar disponível.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Esta variável NÃO move ESTA curva.&lt;/b&gt; Ela atua &lt;b&gt;exclusivamente dentro de "
            "&lt;code&gt;retighten()&lt;/code&gt;&lt;/b&gt; &amp;minus; um evento discreto de re-aperto entre fases de "
            "ciclagem. O ensaio-padrão desta página é uma &lt;b&gt;corrida contínua única&lt;/b&gt;, que "
            "nunca chama retighten(), então o slider não tem por onde agir e a curva fica parada "
            "(por isso: negligível). O dano foi ligado no baseline (c_D, k_dmg_mu, k_dmg_wear) só "
            "para que houvesse D&amp;gt;0 caso um re-aperto ocorresse.&lt;/p&gt;"
            "&lt;p&gt;Para ver o efeito é preciso o ciclo &lt;code&gt;t0 &amp;rarr; retighten() &amp;rarr; tN&lt;/code&gt;, "
            "como no caso Liu2022 de re-aperto (roadmap #5, &amp;sect;4.10): ali a renovação de embedding "
            "reabre a queda inicial no segundo estágio. O companheiro no re-aperto é "
            "&lt;code&gt;k_gall&lt;/code&gt; (atrito de flanco no aperto). Fora de retighten(), ambos são "
            "inertes.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;When a damaged joint is &lt;b&gt;re-tightened&lt;/b&gt;, the already-scarred surfaces expose "
            "fresh bedding capacity: asperity flattening can restart. &lt;code&gt;k_emb_renew&lt;/code&gt; "
            "controls how much of the already-consumed embedding is &lt;b&gt;reopened&lt;/b&gt; at "
            "re-tightening, proportional to damage D: &amp;delta;_emb &amp;larr; "
            "&amp;delta;_emb&amp;middot;(1 &amp;minus; k_emb_renew&amp;middot;D). With k_emb_renew=0 the "
            "re-tighten preserves &amp;delta;_emb (exact backward-compat); with a value &amp;gt;0 part of "
            "the bedding slack becomes available again.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;This variable does NOT move THIS curve.&lt;/b&gt; It acts &lt;b&gt;exclusively inside "
            "&lt;code&gt;retighten()&lt;/code&gt;&lt;/b&gt; &amp;minus; a discrete re-tightening event between cycling phases. "
            "This page's standard test is a &lt;b&gt;single continuous run&lt;/b&gt; that never calls "
            "retighten(), so the slider has nothing to act on and the curve stays put (hence: "
            "negligible). Damage was switched on in the baseline (c_D, k_dmg_mu, k_dmg_wear) only "
            "so that D&amp;gt;0 would exist if a re-tighten occurred.&lt;/p&gt;"
            "&lt;p&gt;To see the effect you need the &lt;code&gt;t0 &amp;rarr; retighten() &amp;rarr; tN&lt;/code&gt; chain, "
            "as in the Liu2022 re-tighten case (roadmap #5, &amp;sect;4.10): there the embedding renewal "
            "reopens the initial drop in the second stage. Its re-tighten companion is "
            "&lt;code&gt;k_gall&lt;/code&gt; (thread-flank friction at tightening). Outside retighten(), both "
            "are inert.&lt;/p&gt;"),
        refs=[("&amp;sect;4.1 EmbeddingLoss &amp;minus; k_emb_renew reabre delta_emb SÓ em retighten()",
               "&amp;sect;4.1 EmbeddingLoss &amp;minus; k_emb_renew reopens delta_emb ONLY in retighten()",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.10 MODEL_LEGITIMACY &amp;minus; Liu2022 re-aperto (renovação de embedding)",
               "&amp;sect;4.10 MODEL_LEGITIMACY &amp;minus; Liu2022 retighten (embedding renewal)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="k_gall", symbol="k_gall", unit="-", group="retighten", category="form",
        context={"baseline":"transverse","overrides":{"c_D":2.0,"k_dmg_mu":1.0,"k_dmg_wear":4.0}},
        sweep=(0,5.0,15,"lin"), related=["k_emb_renew"], negligible=True,
        equation="mu_thread_tighten_eff = mu_thread * (1 + k_gall * D)   (so em tightening_torque, i.e. retighten())",
        physics_pt=(
            "&lt;p&gt;Superfície danificada engripa: no re-aperto de uma junta já machucada o atrito de "
            "FLANCO DE ROSCA visto durante o aperto sobe. &lt;code&gt;k_gall&lt;/code&gt; modela esse galling: "
            "&amp;mu;_thread_aperto = &amp;mu;_thread&amp;middot;(1 + k_gall&amp;middot;D). Um nut factor maior "
            "significa que, para o mesmo torque aplicado, a pré-carga &lt;b&gt;recuperada cai&lt;/b&gt; &amp;minus; a "
            "junta re-apertada nunca volta ao aperto original. Sinal OPOSTO ao "
            "&lt;code&gt;k_dmg_mu&lt;/code&gt; (que baixa o atrito de FACE DE BEARING durante a ciclagem).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Esta variável NÃO move ESTA curva.&lt;/b&gt; Ela entra apenas em "
            "&lt;code&gt;tightening_torque&lt;/code&gt;, ou seja, &lt;b&gt;só quando &lt;code&gt;retighten()&lt;/code&gt; é "
            "chamado&lt;/b&gt;. O ensaio-padrão é uma corrida contínua sem re-aperto: o slider não tem "
            "gatilho e a curva fica idêntica (por isso: negligível). O colapso durante a ciclagem "
            "(via k_dmg_mu/k_dmg_wear) fica intacto &amp;minus; k_gall nunca toca T_resistance no "
            "step_cycle.&lt;/p&gt;"
            "&lt;p&gt;O efeito aparece só no cenário de re-aperto: com o MESMO k_gall, uma junta seca "
            "declina o aperto recuperado a cada re-aperto enquanto uma lubrificada fica ~plana &amp;minus; "
            "o contraste dry-vs-oil (&amp;sect;4.11) sai de um k_gall único com c_D &lt;b&gt;por lubrificação&lt;/b&gt;. "
            "Companheiro: &lt;code&gt;k_emb_renew&lt;/code&gt; (renovação de embedding no mesmo evento). Com "
            "k_gall=0 é inerte.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;A damaged surface galls: on re-tightening an already-scarred joint the "
            "THREAD-FLANK friction seen during tightening rises. &lt;code&gt;k_gall&lt;/code&gt; models that "
            "galling: &amp;mu;_thread_tighten = &amp;mu;_thread&amp;middot;(1 + k_gall&amp;middot;D). A higher nut "
            "factor means that, for the same applied torque, the &lt;b&gt;recovered preload drops&lt;/b&gt; &amp;minus; "
            "the re-tightened joint never returns to its original clamp. This is the OPPOSITE sign "
            "to &lt;code&gt;k_dmg_mu&lt;/code&gt; (which lowers the BEARING-FACE friction during cycling).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;This variable does NOT move THIS curve.&lt;/b&gt; It enters only in "
            "&lt;code&gt;tightening_torque&lt;/code&gt;, i.e. &lt;b&gt;only when &lt;code&gt;retighten()&lt;/code&gt; is "
            "called&lt;/b&gt;. The standard test is a continuous run with no re-tighten: the slider has "
            "no trigger and the curve stays identical (hence: negligible). The collapse during "
            "cycling (via k_dmg_mu/k_dmg_wear) is intact &amp;minus; k_gall never touches T_resistance in "
            "step_cycle.&lt;/p&gt;"
            "&lt;p&gt;The effect shows only in the re-tighten scenario: with the SAME k_gall a dry joint "
            "declines its recovered clamp at each re-tighten while a lubricated one stays ~flat &amp;minus; "
            "the dry-vs-oil contrast (&amp;sect;4.11) comes from a single k_gall with c_D &lt;b&gt;per "
            "lubrication&lt;/b&gt;. Companion: &lt;code&gt;k_emb_renew&lt;/code&gt; (embedding renewal in the same "
            "event). With k_gall=0 it is inert.&lt;/p&gt;"),
        refs=[("&amp;sect;5.2 mu_thread_tighten = mu_thread&amp;middot;(1+k_gall&amp;middot;D), só no aperto",
               "&amp;sect;5.2 mu_thread_tighten = mu_thread*(1+k_gall*D), tightening only",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.11 MODEL_LEGITIMACY &amp;minus; declínio dry-vs-oil (c_D por lubrificação)",
               "&amp;sect;4.11 MODEL_LEGITIMACY &amp;minus; dry-vs-oil decline (per-lube c_D)",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="retight_loss_base", symbol="f&#8321;", unit="-", group="retighten", category="form",
        context={"baseline":"transverse","overrides":{"c_D":2.0,"k_dmg_mu":1.0,"k_dmg_wear":4.0}},
        sweep=(0.1,1.0,15,"lin"), related=["retight_loss_gain","k_emb_renew"], negligible=True,
        equation="perda por slip &amp;times; fator(n);  fator(0)=1,  fator(n&amp;ge;1)=retight_loss_base&amp;middot;(1+retight_loss_gain)^(n&amp;minus;1)",
        physics_pt=(
            "&lt;p&gt;A &lt;b&gt;queda no PRIMEIRO re-aperto&lt;/b&gt;. Num protocolo que &lt;b&gt;não solta&lt;/b&gt; o "
            "parafuso (aperta direto ao torque), a interface segue engajada e o primeiro "
            "re-aperto a &lt;b&gt;assenta&lt;/b&gt;: o dado do Liu 2022 mostra a junta perdendo &lt;b&gt;5&amp;times; "
            "menos&lt;/b&gt; depois dele (2,22&amp;#37; contra 11,10&amp;#37; na corrida virgem). É esse fator "
            "que &lt;code&gt;retight_loss_base&lt;/code&gt; representa.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Por que ele existe separado do ganho:&lt;/b&gt; o fator que o dado pede é "
            "&lt;b&gt;menor que 1&lt;/b&gt; em todo estágio re-apertado e &lt;b&gt;cresce&lt;/b&gt; de volta "
            "(0,203 &amp;rarr; 0,355 &amp;rarr; 0,719). Um amplificador puro &lt;code&gt;(1+g)^n&lt;/code&gt; tem "
            "contradomínio [1,&amp;infin;) e por isso &lt;b&gt;começa do lado errado&lt;/b&gt; &amp;minus; foi assim "
            "que a primeira forma morreu, por álgebra e não por medição. É a imagem espelhada "
            "da família de &lt;i&gt;gates&lt;/i&gt;, cujo contradomínio (0,1] só sabe &lt;b&gt;atrasar&lt;/b&gt;. Este "
            "operador &lt;b&gt;atravessa o 1&lt;/b&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Esta variável NÃO move ESTA curva&lt;/b&gt; (por isso: negligível). Ela só age com "
            "&lt;code&gt;n_retighten &amp;ge; 1&lt;/code&gt;, e o ensaio-padrão desta página é uma corrida "
            "contínua única, que nunca chama &lt;code&gt;retighten()&lt;/code&gt;. Em n=0 o fator vale "
            "1,0 exato &amp;minus; é isso que protege o estágio virgem &lt;b&gt;por construção&lt;/b&gt;, sem "
            "precisar de gate de escopo.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;b&gt;drop at the FIRST re-tightening&lt;/b&gt;. In a protocol that does &lt;b&gt;not "
            "release&lt;/b&gt; the bolt, the interface stays engaged and the first re-tightening "
            "&lt;b&gt;beds it in&lt;/b&gt;: Liu 2022 data shows the joint losing &lt;b&gt;5&amp;times; less&lt;/b&gt; "
            "afterwards (2.22&amp;#37; vs 11.10&amp;#37; virgin).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Why it is separate from the gain:&lt;/b&gt; the factor the data requires is "
            "&lt;b&gt;below 1&lt;/b&gt; at every re-tightened stage and &lt;b&gt;grows&lt;/b&gt; back "
            "(0.203 &amp;rarr; 0.355 &amp;rarr; 0.719). A pure amplifier &lt;code&gt;(1+g)^n&lt;/code&gt; has range "
            "[1,&amp;infin;) and so &lt;b&gt;starts on the wrong side&lt;/b&gt; &amp;minus; the mirror image of the "
            "&lt;i&gt;gate&lt;/i&gt; family, whose (0,1] range can only &lt;b&gt;delay&lt;/b&gt;. This operator "
            "&lt;b&gt;crosses 1&lt;/b&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;It does NOT move THIS curve&lt;/b&gt; (hence: negligible) &amp;minus; it needs "
            "&lt;code&gt;n_retighten &amp;ge; 1&lt;/code&gt;, and the standard run never calls "
            "&lt;code&gt;retighten()&lt;/code&gt;.&lt;/p&gt;"),
        refs=[("Liu 2022 (Structures) &amp;minus; re-aperto: 'directly to torque' restaura 88&amp;ndash;90&amp;#37; de F&amp;#8320;",
               "Liu 2022 (Structures) &amp;minus; retightening: 'directly to torque' restores 88&amp;ndash;90&amp;#37; of F&amp;#8320;",
               "apparatus_notes/liu2022_istruc_retightening.md"),
              ("D-L 2026-08-05 &amp;minus; 3 números compartilhados, transferência seco&amp;harr;óleo",
               "D-L 2026-08-05 &amp;minus; 3 shared numbers, dry&amp;harr;oil transfer",
               "liu2022_relogio_reaperto_resultado.md")]),

    VarSpec(name="retight_loss_gain", symbol="g&#8331;1", unit="-", group="retighten", category="form",
        context={"baseline":"transverse","overrides":{"c_D":2.0,"k_dmg_mu":1.0,"k_dmg_wear":4.0}},
        sweep=(0,2.0,15,"lin"), related=["retight_loss_base","k_emb_renew"], negligible=True,
        equation="fator(n&amp;ge;1) = retight_loss_base&amp;middot;(1+retight_loss_gain)^(n&amp;minus;1);  g = 1+gain",
        physics_pt=(
            "&lt;p&gt;O &lt;b&gt;re-dano por evento&lt;/b&gt;: depois que o primeiro re-aperto assenta a "
            "interface, cada re-aperto seguinte a &lt;b&gt;danifica de novo&lt;/b&gt;, e a perda por "
            "estágio volta a crescer &amp;minus; medida em &lt;b&gt;&amp;asymp;1,9&amp;times; por evento&lt;/b&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;O que faz este número valer:&lt;/b&gt; ele é o &lt;b&gt;mesmo&lt;/b&gt; nas duas "
            "lubrificações. O dado dá 1,75&amp;times;/2,03&amp;times; na cadeia &lt;b&gt;seca&lt;/b&gt; e "
            "1,49&amp;times;/2,03&amp;times; na de &lt;b&gt;óleo&lt;/b&gt; &amp;minus; 8&amp;#37; de diferença. E é "
            "&lt;b&gt;plano ou decrescente&lt;/b&gt; (1,09/1,17 e 0,75/0,93) nos dois protocolos que "
            "&lt;b&gt;soltam&lt;/b&gt; o parafuso 30&amp;ndash;60&amp;deg; antes de reapertar. Ou seja: a taxa de "
            "re-dano é propriedade da &lt;b&gt;superfície&lt;/b&gt;, não do lubrificante nem da figura &amp;minus; "
            "e as diferenças por lubrificação saem do &lt;code&gt;c_D&lt;/code&gt; já adotado, porque "
            "&lt;code&gt;k_emb_renew&lt;/code&gt; multiplica &lt;i&gt;D&lt;/i&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Esta variável NÃO move ESTA curva&lt;/b&gt; (negligível): exige "
            "&lt;code&gt;n_retighten &amp;ge; 2&lt;/code&gt;, e o ensaio-padrão é uma corrida única.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;b&gt;re-damage per event&lt;/b&gt;: once the first re-tightening beds the "
            "interface in, each subsequent one &lt;b&gt;damages it again&lt;/b&gt; and the per-stage loss "
            "grows back &amp;minus; measured at &lt;b&gt;&amp;asymp;1.9&amp;times; per event&lt;/b&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;What makes this number worth having:&lt;/b&gt; it is the &lt;b&gt;same&lt;/b&gt; for both "
            "lubrications &amp;minus; 1.75/2.03&amp;times; dry, 1.49/2.03&amp;times; oil (8&amp;#37; apart) &amp;minus; "
            "and &lt;b&gt;flat or decreasing&lt;/b&gt; (1.09/1.17 and 0.75/0.93) in both protocols that "
            "&lt;b&gt;release&lt;/b&gt; the bolt first. The re-damage rate is a property of the "
            "&lt;b&gt;surface&lt;/b&gt;, not of the lubricant.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;It does NOT move THIS curve&lt;/b&gt; (negligible): needs "
            "&lt;code&gt;n_retighten &amp;ge; 2&lt;/code&gt;.&lt;/p&gt;"),
        refs=[("Liu 2022 &amp;minus; 4 cadeias do mesmo rig: 2 aceleram, 2 desaceleram (o protocolo decide)",
               "Liu 2022 &amp;minus; 4 chains, same rig: 2 accelerate, 2 decelerate (protocol decides)",
               "liu2022_fig8_cadeia_resultado.md"),
              ("D-L 2026-08-05 &amp;minus; G1 transferência: 14 de 24 células, 3 números compartilhados",
               "D-L 2026-08-05 &amp;minus; G1 transfer: 14 of 24 cells, 3 shared numbers",
               "liu2022_relogio_reaperto_resultado.md")]),

    VarSpec(name="crash_trigger_frac", symbol="r_crash", unit="-", group="crash", category="form",
        context={"baseline":"transverse","overrides":{}},
        sweep=(0,0.9,15,"lin"), related=["crash_trigger_sharpness"],
        equation="g_trig = r_crash^k / (r_crash^k + (F_0/F_0_init)^k);  loosening dF_0 *= g_trig,  k = crash_trigger_sharpness",
        physics_pt=(
            "&lt;p&gt;Algumas juntas não afrouxam gradualmente: ficam num &lt;b&gt;platô&lt;/b&gt; quase estável por "
            "milhares de ciclos e então &lt;b&gt;desabam de repente&lt;/b&gt; (o joelho tardio). "
            "&lt;code&gt;crash_trigger_frac&lt;/code&gt; (r_crash) é a fração de pré-carga em que esse "
            "colapso dispara. O afrouxamento rotacional fica SUPRIMIDO enquanto F_0 está alto e só "
            "acende quando a razão F_0/F_0_init cruza r_crash, via um gate de Hill "
            "g_trig = r_crash^k/(r_crash^k + (F_0/F_0_init)^k).&lt;/p&gt;"
            "&lt;p&gt;Enquanto embedding e wear trazem F_0 lentamente até o limiar, o gate mantém o "
            "loosening quase desligado (platô); ao cruzar r_crash o gate abre e o runaway toma "
            "conta (queda abrupta). Aumentar r_crash faz o joelho acontecer &lt;b&gt;mais cedo&lt;/b&gt; "
            "(dispara com menos perda acumulada); r_crash=0 desliga o gatilho e volta ao colapso "
            "gradual atual (bit-idêntico). É chaveado em F_0/F_0_init, não em Q/&amp;mu;F_0k (que é "
            "F_0-independente em disp-mode).&lt;/p&gt;"
            "&lt;p&gt;A forma foi suprida sob dupla falsificação (&amp;sect;4.30, lição L14): o joelho de "
            "estágio-3 do Bauer fig8 e o início-plano do Liu2025 &amp;minus; ambos exigiam separar "
            "&amp;quot;platô enquanto forte&amp;quot; de &amp;quot;runaway quando fraco&amp;quot;. A nitidez do "
            "joelho é o companheiro &lt;code&gt;crash_trigger_sharpness&lt;/code&gt;. É uma criticalidade tipo "
            "grip-runaway, distinta do colapso cinemático (proporcional ao caminho de slip).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Some joints do not loosen gradually: they sit on a near-stable &lt;b&gt;plateau&lt;/b&gt; for "
            "thousands of cycles and then &lt;b&gt;collapse suddenly&lt;/b&gt; (the late knee). "
            "&lt;code&gt;crash_trigger_frac&lt;/code&gt; (r_crash) is the preload fraction at which that "
            "collapse fires. Rotational loosening stays SUPPRESSED while F_0 is high and only "
            "switches on once the ratio F_0/F_0_init crosses r_crash, via a Hill gate "
            "g_trig = r_crash^k/(r_crash^k + (F_0/F_0_init)^k).&lt;/p&gt;"
            "&lt;p&gt;While embedding and wear slowly bring F_0 down to the threshold, the gate keeps "
            "loosening nearly off (plateau); on crossing r_crash the gate opens and the runaway "
            "takes over (abrupt drop). Raising r_crash makes the knee happen &lt;b&gt;earlier&lt;/b&gt; (it "
            "fires with less accumulated loss); r_crash=0 disables the trigger and returns to the "
            "current gradual collapse (bit-identical). It is keyed on F_0/F_0_init, not on "
            "Q/&amp;mu;F_0k (which is F_0-independent in disp-mode).&lt;/p&gt;"
            "&lt;p&gt;The form was supplied under double falsification (&amp;sect;4.30, lesson L14): the stage-3 "
            "knee of Bauer fig8 and the flat-early start of Liu2025 &amp;minus; both required separating "
            "&amp;quot;plateau while strong&amp;quot; from &amp;quot;runaway when weak&amp;quot;. The knee "
            "sharpness is the companion &lt;code&gt;crash_trigger_sharpness&lt;/code&gt;. It is a "
            "grip-runaway-type criticality, distinct from the kinematic collapse (proportional to slip "
            "path).&lt;/p&gt;"),
        refs=[("&amp;sect;4.4 loosening &amp;minus; gatilho de crash (gate Hill em F_0/F_0_init)",
               "&amp;sect;4.4 loosening &amp;minus; crash trigger (Hill gate on F_0/F_0_init)",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.30 MODEL_LEGITIMACY (L14) &amp;minus; joelho tardio Bauer fig8 + Liu2025 flat-early",
               "&amp;sect;4.30 MODEL_LEGITIMACY (L14) &amp;minus; late knee Bauer fig8 + Liu2025 flat-early",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="crash_trigger_sharpness", symbol="k_crash", unit="-", group="crash", category="form",
        context={"baseline":"transverse","overrides":{"crash_trigger_frac":0.6}},
        sweep=(1.0,16.0,15,"lin"), related=["crash_trigger_frac"],
        equation="g_trig = r_crash^k / (r_crash^k + (F_0/F_0_init)^k),  k = crash_trigger_sharpness",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;crash_trigger_sharpness&lt;/code&gt; (k) é o EXPOENTE do gate de Hill do colapso: "
            "g_trig = r_crash^k/(r_crash^k + (F_0/F_0_init)^k). Ele fixa quão ABRUPTO é o joelho "
            "quando a pré-carga cruza o limiar &lt;code&gt;crash_trigger_frac&lt;/code&gt;. k pequeno (~1) dá "
            "uma transição suave (o loosening acende gradualmente perto do limiar); k grande "
            "(~16) dá um degrau quase liga/desliga &amp;minus; o clássico penhasco do colapso tardio.&lt;/p&gt;"
            "&lt;p&gt;Este parâmetro &lt;b&gt;só tem efeito se &lt;code&gt;crash_trigger_frac&lt;/code&gt; &amp;gt; 0&lt;/b&gt; "
            "(por isso o baseline desta página fixa r_crash=0.6 para o gate existir). Com o "
            "gatilho ligado, deslizar k afia ou suaviza o mesmo joelho sem mover sua POSIÇÃO em "
            "F_0 &amp;minus; quem escolhe ONDE o colapso ocorre é r_crash; k escolhe QUÃO rápido. Sozinho "
            "(r_crash=0) não faz nada.&lt;/p&gt;"
            "&lt;p&gt;A função Hill é a mesma família dos outros gates de incubação/onset do modelo "
            "(slip_onset, onset de dano): um interruptor suave é parametrizado em vez de um "
            "degrau descontínuo, o que mantém o solver estável e a derivada bem-comportada. "
            "Companheiro: &lt;code&gt;crash_trigger_frac&lt;/code&gt;.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;crash_trigger_sharpness&lt;/code&gt; (k) is the EXPONENT of the collapse Hill gate: "
            "g_trig = r_crash^k/(r_crash^k + (F_0/F_0_init)^k). It sets how ABRUPT the knee is when "
            "preload crosses the &lt;code&gt;crash_trigger_frac&lt;/code&gt; threshold. Small k (~1) gives a "
            "smooth transition (loosening switches on gradually near the threshold); large k (~16) "
            "gives an almost on/off step &amp;minus; the classic late-collapse cliff.&lt;/p&gt;"
            "&lt;p&gt;This parameter &lt;b&gt;only has an effect if &lt;code&gt;crash_trigger_frac&lt;/code&gt; &amp;gt; 0&lt;/b&gt; "
            "(hence this page's baseline fixes r_crash=0.6 so the gate exists). With the trigger "
            "on, sliding k sharpens or softens the same knee without moving its POSITION in F_0 &amp;minus; "
            "r_crash chooses WHERE the collapse happens; k chooses HOW fast. On its own "
            "(r_crash=0) it does nothing.&lt;/p&gt;"
            "&lt;p&gt;The Hill function is the same family as the model's other incubation/onset gates "
            "(slip_onset, damage onset): a smooth parameterized switch instead of a discontinuous "
            "step, which keeps the solver stable and the derivative well-behaved. Companion: "
            "&lt;code&gt;crash_trigger_frac&lt;/code&gt;.&lt;/p&gt;"),
        refs=[("&amp;sect;4.4 loosening &amp;minus; nitidez k do gate Hill do crash",
               "&amp;sect;4.4 loosening &amp;minus; sharpness k of the crash Hill gate",
               "MODEL_MATH_REFERENCE.md"),
              ("&amp;sect;4.30 MODEL_LEGITIMACY (L14) &amp;minus; criticalidade do colapso tardio",
               "&amp;sect;4.30 MODEL_LEGITIMACY (L14) &amp;minus; late-collapse criticality",
               "MODEL_LEGITIMACY.md")]),

    VarSpec(name="rayleigh_alpha", symbol="alpha_R", unit="1/s", group="numerical", category="numerical",
        context={"baseline":"transverse","overrides":{}},
        sweep=(0,0.1,8,"lin"), negligible=True, related=["rayleigh_beta"],
        equation="[C(s)] = alpha_R*[M] + beta_R*[K(s)]   (amortecimento proporcional de Rayleigh)",
        physics_pt=(
            "&lt;p&gt;O amortecimento do modelo dinâmico é do tipo &lt;b&gt;Rayleigh proporcional&lt;/b&gt;: "
            "[C] = &amp;alpha;_R&amp;middot;[M] + &amp;beta;_R&amp;middot;[K]. &lt;code&gt;rayleigh_alpha&lt;/code&gt; "
            "(&amp;alpha;_R) é o coeficiente proporcional a MASSA &amp;minus; domina o amortecimento dos modos "
            "de baixa frequência. Tem unidade 1/s.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Esta variável praticamente NÃO move a curva F/F0.&lt;/b&gt; O modelo de afrouxamento "
            "é &lt;b&gt;QUASE-ESTÁTICO por ciclo&lt;/b&gt;: a evolução lenta de F_0 vem dos mecanismos de "
            "perda (embedding, creep, wear, loosening), não do transiente inercial/amortecido "
            "dentro de um ciclo. O canal viscoso é contabilizado no balanço de energia (suprido "
            "por W_ext), mas não realimenta F_0 de forma sensível. Por isso a página está marcada "
            "como negligível &amp;minus; assim como &lt;code&gt;m_x&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Existe para completar o operador dinâmico [M]/[C]/[K] e para runs de integração no "
            "tempo (Newmark/HHT). O companheiro proporcional a rigidez é &lt;code&gt;rayleigh_beta&lt;/code&gt;; "
            "juntos fixam a razão de amortecimento em duas frequências-alvo.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The dynamic model's damping is &lt;b&gt;Rayleigh proportional&lt;/b&gt;: "
            "[C] = &amp;alpha;_R&amp;middot;[M] + &amp;beta;_R&amp;middot;[K]. &lt;code&gt;rayleigh_alpha&lt;/code&gt; "
            "(&amp;alpha;_R) is the MASS-proportional coefficient &amp;minus; it dominates the damping of "
            "low-frequency modes. Its unit is 1/s.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;This variable barely moves the F/F0 curve.&lt;/b&gt; The loosening model is "
            "&lt;b&gt;QUASI-STATIC per cycle&lt;/b&gt;: the slow F_0 evolution comes from the loss mechanisms "
            "(embedding, creep, wear, loosening), not from the inertial/damped transient within a "
            "cycle. The viscous channel is booked in the energy budget (sourced by W_ext) but does "
            "not feed back into F_0 in any sensible way. That is why the page is marked negligible "
            "&amp;minus; just like &lt;code&gt;m_x&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;It exists to complete the dynamic [M]/[C]/[K] operator and for time-integration "
            "runs (Newmark/HHT). Its stiffness-proportional companion is &lt;code&gt;rayleigh_beta&lt;/code&gt;; "
            "together they set the damping ratio at two target frequencies.&lt;/p&gt;"),
        refs=[("&amp;sect;3 / C_matrix &amp;minus; Rayleigh [C]=alpha[M]+beta[K] (canal viscoso no budget)",
               "&amp;sect;3 / C_matrix &amp;minus; Rayleigh [C]=alpha[M]+beta[K] (viscous channel in the budget)",
               "MODEL_MATH_REFERENCE.md"),
              ("Amortecimento proporcional (Rayleigh) em dinâmica estrutural",
               "Proportional (Rayleigh) damping in structural dynamics",
               "Clough &amp;amp; Penzien, Dynamics of Structures")]),

    VarSpec(name="rayleigh_beta", symbol="beta_R", unit="s", group="numerical", category="numerical",
        context={"baseline":"transverse","overrides":{}},
        sweep=(0,1e-4,8,"lin"), negligible=True, related=["rayleigh_alpha"],
        equation="[C(s)] = alpha_R*[M] + beta_R*[K(s)]   (amortecimento proporcional de Rayleigh)",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;rayleigh_beta&lt;/code&gt; (&amp;beta;_R) é o coeficiente do amortecimento de Rayleigh "
            "proporcional a RIGIDEZ: [C] = &amp;alpha;_R&amp;middot;[M] + &amp;beta;_R&amp;middot;[K]. Ao contrario "
            "de &amp;alpha;_R, ele amortece preferencialmente os modos de ALTA frequência. Tem unidade "
            "de segundos.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Praticamente NÃO move a curva F/F0.&lt;/b&gt; Como o afrouxamento é resolvido de forma "
            "&lt;b&gt;quase-estática por ciclo&lt;/b&gt;, o termo de amortecimento entra no balanço de energia "
            "(via W_ext) mas não altera de modo sensível a trajetória lenta de F_0 &amp;minus; que é ditada "
            "pelos mecanismos de perda. Por isso é marcada como negligível (mesma situação de "
            "&lt;code&gt;m_x&lt;/code&gt;, &lt;code&gt;m_y&lt;/code&gt;, &lt;code&gt;I_theta&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Serve ao operador dinâmico [C(s)] e a integração no tempo. Como [K(s)] é "
            "reavaliado a cada ciclo (softening Greenwood-Williamson), o [C] proporcional a "
            "rigidez também acompanha o estado. Companheiro: &lt;code&gt;rayleigh_alpha&lt;/code&gt; "
            "(proporcional a massa).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;rayleigh_beta&lt;/code&gt; (&amp;beta;_R) is the STIFFNESS-proportional Rayleigh "
            "damping coefficient: [C] = &amp;alpha;_R&amp;middot;[M] + &amp;beta;_R&amp;middot;[K]. Unlike "
            "&amp;alpha;_R, it preferentially damps HIGH-frequency modes. Its unit is seconds.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;It barely moves the F/F0 curve.&lt;/b&gt; Since loosening is solved "
            "&lt;b&gt;quasi-statically per cycle&lt;/b&gt;, the damping term enters the energy budget (via "
            "W_ext) but does not sensibly change the slow F_0 trajectory &amp;minus; which is dictated by the "
            "loss mechanisms. Hence it is marked negligible (same situation as &lt;code&gt;m_x&lt;/code&gt;, "
            "&lt;code&gt;m_y&lt;/code&gt;, &lt;code&gt;I_theta&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;It serves the dynamic [C(s)] operator and time integration. Because [K(s)] is "
            "re-evaluated each cycle (Greenwood-Williamson softening), the stiffness-proportional "
            "[C] tracks the state too. Companion: &lt;code&gt;rayleigh_alpha&lt;/code&gt; "
            "(mass-proportional).&lt;/p&gt;"),
        refs=[("&amp;sect;3 / C_matrix &amp;minus; Rayleigh [C]=alpha[M]+beta[K], beta proporcional a [K(s)]",
               "&amp;sect;3 / C_matrix &amp;minus; Rayleigh [C]=alpha[M]+beta[K], beta proportional to [K(s)]",
               "MODEL_MATH_REFERENCE.md"),
              ("Amortecimento proporcional (Rayleigh) em dinâmica estrutural",
               "Proportional (Rayleigh) damping in structural dynamics",
               "Clough &amp;amp; Penzien, Dynamics of Structures")]),

    VarSpec(name="m_y", symbol="m_y", unit="kg", group="numerical", category="numerical",
        context={"baseline":"transverse","overrides":{}},
        sweep=(0.1,2.0,8,"lin"), negligible=True, related=["m_x","I_theta"],
        equation="[M] = diag(m_x, m_y, I_theta)   - massa efetiva do no (GDL x, y, theta)",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;m_y&lt;/code&gt; é a massa efetiva na direção transversal (y) da matriz de massa "
            "[M] = diag(m_x, m_y, I_theta) do modelo dinâmico de 3 GDL (x, y, &amp;theta;). Governa a "
            "inércia do nó na direção do carregamento transversal imposto.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Variar m_y praticamente NÃO muda a curva F/F0.&lt;/b&gt; O modelo de afrouxamento é "
            "&lt;b&gt;quase-estático por ciclo&lt;/b&gt;: o escorregamento vem do deslocamento imposto e as "
            "perdas vêm dos mecanismos lentos, não da resposta inercial dentro do ciclo. A massa "
            "só importaria perto de uma ressonância, fora do regime de baixa frequência (0.5 Hz) "
            "do ensaio-padrão. Por isso é negligível &amp;minus; exatamente como &lt;code&gt;m_x&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Existe para montar [M] e o amortecimento de Rayleigh ([C]=&amp;alpha;[M]+&amp;beta;[K]) e "
            "para integração no tempo. Companheiros: &lt;code&gt;m_x&lt;/code&gt; (axial/x) e "
            "&lt;code&gt;I_theta&lt;/code&gt; (rotacional).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;m_y&lt;/code&gt; is the effective mass in the transverse direction (y) of the mass "
            "matrix [M] = diag(m_x, m_y, I_theta) of the 3-DOF dynamic model (x, y, &amp;theta;). It "
            "governs the node's inertia along the imposed transverse loading direction.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Varying m_y barely changes the F/F0 curve.&lt;/b&gt; The loosening model is "
            "&lt;b&gt;quasi-static per cycle&lt;/b&gt;: slip comes from the imposed displacement and the losses "
            "from the slow mechanisms, not from the inertial response within a cycle. Mass would "
            "only matter near a resonance, outside the low-frequency regime (0.5 Hz) of the "
            "standard test. Hence it is negligible &amp;minus; exactly like &lt;code&gt;m_x&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;It exists to assemble [M] and the Rayleigh damping ([C]=&amp;alpha;[M]+&amp;beta;[K]) and "
            "for time integration. Companions: &lt;code&gt;m_x&lt;/code&gt; (axial/x) and &lt;code&gt;I_theta&lt;/code&gt; "
            "(rotational).&lt;/p&gt;"),
        refs=[("&amp;sect;3 massa efetiva / [M] = diag(m_x, m_y, I_theta)",
               "&amp;sect;3 effective mass / [M] = diag(m_x, m_y, I_theta)",
               "MODEL_MATH_REFERENCE.md")]),

    VarSpec(name="I_theta", symbol="I_theta", unit="kg.m^2", group="numerical", category="numerical",
        context={"baseline":"transverse","overrides":{}},
        sweep=(1e-6,1e-4,8,"log"), negligible=True, related=["m_x","m_y"],
        equation="[M] = diag(m_x, m_y, I_theta)   - inercia rotacional (GDL theta)",
        physics_pt=(
            "&lt;p&gt;&lt;code&gt;I_theta&lt;/code&gt; é a inércia rotacional do nó em torno do eixo do parafuso (o "
            "GDL &amp;theta;), o terceiro termo da matriz de massa [M] = diag(m_x, m_y, I_theta). É o "
            "análogo rotacional da massa: resiste a aceleração angular da porca/parafuso.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Praticamente NÃO move a curva F/F0.&lt;/b&gt; O afrouxamento rotacional no modelo é "
            "dirigido por torque quase-estático (T_loose vs T_resist) e pela hélice, não pela "
            "dinâmica angular transitória; a evolução lenta de &amp;theta;_loose e de F_0 não depende "
            "de forma sensível de I_theta. Assim como &lt;code&gt;m_x&lt;/code&gt;/&lt;code&gt;m_y&lt;/code&gt;, é um "
            "parâmetro inercial mostrado por completude &amp;minus; logo, negligível.&lt;/p&gt;"
            "&lt;p&gt;Entra em [M] e no amortecimento de Rayleigh, e importa em análises de resposta em "
            "frequência / integração no tempo. Companheiros: &lt;code&gt;m_x&lt;/code&gt;, &lt;code&gt;m_y&lt;/code&gt;. "
            "A varredura é em escala log porque I_theta cobre várias ordens de grandeza "
            "(kg&amp;middot;m^2).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;&lt;code&gt;I_theta&lt;/code&gt; is the node's rotational inertia about the bolt axis (the "
            "&amp;theta; DOF), the third term of the mass matrix [M] = diag(m_x, m_y, I_theta). It is "
            "the rotational analogue of mass: it resists angular acceleration of the nut/bolt.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;It barely moves the F/F0 curve.&lt;/b&gt; Rotational loosening in the model is driven "
            "by quasi-static torque (T_loose vs T_resist) and by the helix, not by transient "
            "angular dynamics; the slow evolution of &amp;theta;_loose and F_0 does not depend "
            "sensibly on I_theta. Like &lt;code&gt;m_x&lt;/code&gt;/&lt;code&gt;m_y&lt;/code&gt;, it is an inertial "
            "parameter shown for completeness &amp;minus; hence negligible.&lt;/p&gt;"
            "&lt;p&gt;It enters [M] and the Rayleigh damping, and matters in frequency-response / "
            "time-integration analyses. Companions: &lt;code&gt;m_x&lt;/code&gt;, &lt;code&gt;m_y&lt;/code&gt;. The sweep "
            "is on a log scale because I_theta spans several orders of magnitude "
            "(kg&amp;middot;m^2).&lt;/p&gt;"),
        refs=[("&amp;sect;3 massa efetiva / inércia rotacional em [M]",
               "&amp;sect;3 effective mass / rotational inertia in [M]",
               "MODEL_MATH_REFERENCE.md")]),
])

# =============================== FATIGUE (S-N, fracture tail) (10) ===============================
VARIABLE_SPECS.extend([
    VarSpec(name="fatigue_enabled", symbol="", unit="", group="fatigue", category="mode",
            context={"baseline": "fatigue", "overrides": {}}, choices=[False, True],
            related=["fat_Kt"],
            equation="if fatigue_enabled: D_fat += 1/N_f each cycle, fracture (F_0 -> f_res*F_0_init) at D_fat >= 1;  else: dF_0 = 0 (inert, bit-identical)",
            physics_pt=(
                "&lt;p&gt;A tensão cíclica na raiz da rosca (o entalhe mais solicitado do parafuso) "
                "nucleia e propaga uma trinca de fadiga. Quando a trinca vence a seção, o "
                "parafuso &lt;b&gt;fratura&lt;/b&gt; e o aperto cai de forma abrupta para quase zero: é o "
                "&lt;b&gt;cliff&lt;/b&gt; (penhasco) &amp;minus; um evento estrutural, não uma perda gradual como "
                "embedding ou creep. O campo &lt;code&gt;fatigue_enabled&lt;/code&gt; liga ou desliga esse "
                "mecanismo por inteiro.&lt;/p&gt;"
                "&lt;p&gt;Com &lt;code&gt;False&lt;/code&gt; (default) a &lt;code&gt;FatigueLoss&lt;/code&gt; é inerte &amp;minus; zero "
                "exato, bit-identical ao motor sem o mecanismo. Com &lt;code&gt;True&lt;/code&gt;, cada "
                "ciclo acumula dano de Miner &amp;Delta;D_fat = 1/N_f (N_f = vida da curva S-N); "
                "quando D_fat atinge 1 o cliff dispara. Como a fadiga só morde &lt;b&gt;perto da "
                "fratura&lt;/b&gt; (contagens de ciclo altas), esta página usa um baseline &lt;b&gt;axial&lt;/b&gt; "
                "com janela LONGA (N = 6000 ciclos) &amp;minus; diferente da curva-padrão de cisalhamento &amp;minus; "
                "para que o cliff caiba na janela e os sliders mostrem &lt;b&gt;onde&lt;/b&gt; ele acontece.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: inerte por default. A forma bilinear Su-N transfere "
                "cross-material a ~2.3&amp;times; (melhor que o &lt;code&gt;C_creep&lt;/code&gt;), e reproduz o "
                "cliff do Li2022ti (fratura em ~410 mil ciclos). É uma capacidade &lt;b&gt;validada, "
                "porém NÃO adotada&lt;/b&gt; no canônico &amp;minus; as constantes S-N são por material.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;Cyclic stress at the thread root (the most loaded notch of the bolt) "
                "nucleates and grows a fatigue crack. When the crack overcomes the section the "
                "bolt &lt;b&gt;fractures&lt;/b&gt; and clamp drops abruptly to near zero: the &lt;b&gt;cliff&lt;/b&gt; &amp;minus; "
                "a structural event, not a gradual loss like embedding or creep. The field "
                "&lt;code&gt;fatigue_enabled&lt;/code&gt; switches this whole mechanism on or off.&lt;/p&gt;"
                "&lt;p&gt;With &lt;code&gt;False&lt;/code&gt; (default) &lt;code&gt;FatigueLoss&lt;/code&gt; is inert &amp;minus; exactly "
                "zero, bit-identical to the engine without the mechanism. With &lt;code&gt;True&lt;/code&gt;, "
                "each cycle accumulates Miner damage &amp;Delta;D_fat = 1/N_f (N_f = life on the S-N "
                "curve); when D_fat reaches 1 the cliff fires. Because fatigue only bites &lt;b&gt;near "
                "fracture&lt;/b&gt; (high cycle counts), this page uses an &lt;b&gt;axial&lt;/b&gt; baseline with a "
                "LONG window (N = 6000 cycles) &amp;minus; unlike the standard shear curve &amp;minus; so the cliff "
                "fits inside the window and the sliders show &lt;b&gt;where&lt;/b&gt; it happens.&lt;/p&gt;"
                "&lt;p&gt;Provenance: inert by default. The bilinear Su-N form transfers cross-material "
                "to ~2.3&amp;times; (better than &lt;code&gt;C_creep&lt;/code&gt;) and reproduces the Li2022ti "
                "cliff (fracture near 410k cycles). It is a &lt;b&gt;validated but NOT adopted&lt;/b&gt; "
                "capability in the canonical model &amp;minus; the S-N constants are per-material.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; fadiga de raiz de rosca -> fratura (cliff)",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; thread-root fatigue -> fracture (cliff)",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Design da cauda de fadiga/fratura (Miner + Su-N bilinear + Goodman)",
                   "Fatigue/fracture tail design (Miner + bilinear Su-N + Goodman)",
                   "specs/2026-07-08-fatigue-fracture-tail-design.md")]),

    VarSpec(name="fat_stress_mode", symbol="", unit="", group="fatigue", category="mode",
            context={"baseline": "transverse", "overrides": {"fatigue_enabled": True}},
            choices=["axial", "bending"], related=["fatigue_enabled"],
            equation='sigma_a = F_amp/A_s   ("axial")   |   sigma_a = K_t*E*d_2*delta/L_eff^2   ("bending", so disp-mode);   sigma_a -> S-N -> N_f (dano de Miner)',
            physics_pt=(
                "&lt;p&gt;Este seletor decide QUAL tensão cíclica dirige a fadiga da raiz de rosca. Em "
                "&lt;b&gt;axial&lt;/b&gt; a amplitude é &amp;sigma;_a = F_amp/A_s (tração cíclica pela força axial) &amp;minus; "
                "o certo para um ensaio servo-hidráulico axial. Em &lt;b&gt;bending&lt;/b&gt; a amplitude vem da "
                "FLEXÃO do parafuso sob o deslocamento transverso IMPOSTO, &amp;sigma;_a &amp;asymp; "
                "K_t&amp;middot;E&amp;middot;d_2&amp;middot;&amp;delta;/L_eff&amp;sup2; &amp;minus; o certo para um ensaio "
                "transversal (Junker), onde a fratura escala com &amp;delta;, não com F_amp.&lt;/p&gt;"
                "&lt;p&gt;Na curva-padrão (transversal, &amp;delta; = 0.5 mm) a tensão de flexão é bem MAIOR que "
                "a axial (centenas de MPa vs ~130 MPa), então trocar para &lt;b&gt;bending&lt;/b&gt; antecipa "
                "muito o &lt;b&gt;cliff&lt;/b&gt; de fratura &amp;minus; o colapso muda de posição. Por isso o parafuso "
                "pode falhar por fadiga mesmo ABAIXO do limiar de slip: ele flexiona pelo &amp;delta; "
                "imposto ainda que o contato não escorregue.&lt;/p&gt;"
                "&lt;p&gt;Só tem efeito com &lt;code&gt;fatigue_enabled = True&lt;/code&gt; (aqui o contexto o liga) e, "
                "em &lt;b&gt;bending&lt;/b&gt;, só em disp-mode (precisa do &amp;delta; imposto). É uma escolha de "
                "FÍSICA do driver de tensão, não um número ajustável. Default &lt;code&gt;axial&lt;/code&gt; &amp;minus; "
                "backward-compat.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;This selector decides WHICH cyclic stress drives thread-root fatigue. In "
                "&lt;b&gt;axial&lt;/b&gt; the amplitude is &amp;sigma;_a = F_amp/A_s (cyclic tension from the axial "
                "force) &amp;minus; right for an axial servo-hydraulic test. In &lt;b&gt;bending&lt;/b&gt; the amplitude "
                "comes from BENDING of the bolt under the IMPOSED transverse displacement, &amp;sigma;_a "
                "&amp;asymp; K_t&amp;middot;E&amp;middot;d_2&amp;middot;&amp;delta;/L_eff&amp;sup2; &amp;minus; right for a transverse "
                "(Junker) test, where fracture scales with &amp;delta;, not with F_amp.&lt;/p&gt;"
                "&lt;p&gt;On the standard curve (transverse, &amp;delta; = 0.5 mm) the bending stress is far "
                "HIGHER than the axial one (hundreds of MPa vs ~130 MPa), so switching to "
                "&lt;b&gt;bending&lt;/b&gt; brings the fracture &lt;b&gt;cliff&lt;/b&gt; much earlier &amp;minus; the collapse moves. "
                "That is why the bolt can fail by fatigue even BELOW the slip threshold: it bends "
                "under the imposed &amp;delta; even if the contact does not slip.&lt;/p&gt;"
                "&lt;p&gt;It only acts with &lt;code&gt;fatigue_enabled = True&lt;/code&gt; (the context turns it on) "
                "and, in &lt;b&gt;bending&lt;/b&gt;, only in disp-mode (it needs the imposed &amp;delta;). It is a "
                "PHYSICS choice of the stress driver, not a tunable number. Default "
                "&lt;code&gt;axial&lt;/code&gt; &amp;minus; backward-compatible.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss: driver de tensão axial vs flexão (PR-24)",
                   "&amp;sect;4.6 FatigueLoss: axial vs bending stress driver (PR-24)",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Fratura transversal escala com &amp;delta; (flexão), não com F_amp",
                   "Transverse fracture scales with &amp;delta; (bending), not F_amp",
                   "MODEL_LEGITIMACY.md")]),

    VarSpec(name="fatigue_residual_frac", symbol="f_res", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(0, 0.5, 15, "lin"), related=["fatigue_enabled"],
            equation="at fracture (D_fat >= 1):  dF_0 = -(F_0 - f_res*F_0_init)  =>  F_0 -> f_res*F_0_init",
            physics_pt=(
                "&lt;p&gt;Depois que o cliff dispara, sobra algum aperto? &lt;code&gt;fatigue_residual_frac&lt;/code&gt; "
                "(f_res) é a fração da pré-carga ORIGINAL (F_0_init) que sobrevive a fratura. "
                "f_res = 0 é fratura total (o parafuso solta, F_0 &amp;rarr; 0); f_res &amp;gt; 0 modela "
                "uma fratura parcial ou um caminho de carga residual (engajamento de rosca "
                "remanescente, um segundo parafuso, um batente) que ainda segura parte da força.&lt;/p&gt;"
                "&lt;p&gt;No ciclo de fratura o modelo aplica &amp;Delta;F_0 = &amp;minus;(F_0 &amp;minus; "
                "f_res&amp;middot;F_0_init), ou seja F_0 salta direto para f_res&amp;middot;F_0_init. "
                "Mover o slider levanta o &lt;b&gt;piso&lt;/b&gt; em que o cliff aterrissa &amp;minus; quanto mais fundo "
                "cai a curva. Ele NÃO muda &lt;b&gt;onde&lt;/b&gt; o cliff acontece (isso é governado pelos "
                "parâmetros da S-N e pela tensão); só muda a profundidade da queda.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: é um clamp fenomenológico do evento estrutural (a energética do "
                "cliff é a energia elástica liberada, roteada para W_diss_fracture). Default 0 = "
                "fratura total, o caso conservador.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;After the cliff fires, does any clamp survive? &lt;code&gt;fatigue_residual_frac&lt;/code&gt; "
                "(f_res) is the fraction of the ORIGINAL preload (F_0_init) that outlives fracture. "
                "f_res = 0 is total fracture (the bolt lets go, F_0 &amp;rarr; 0); f_res &amp;gt; 0 models "
                "a partial fracture or a residual load path (remaining thread engagement, a second "
                "bolt, a stop) that still carries some force.&lt;/p&gt;"
                "&lt;p&gt;On the fracture cycle the model applies &amp;Delta;F_0 = &amp;minus;(F_0 &amp;minus; "
                "f_res&amp;middot;F_0_init), so F_0 jumps straight to f_res&amp;middot;F_0_init. Moving the "
                "slider raises the &lt;b&gt;floor&lt;/b&gt; the cliff lands on &amp;minus; how deep the curve drops. It "
                "does NOT move &lt;b&gt;where&lt;/b&gt; the cliff happens (that is set by the S-N parameters and "
                "the stress); it only sets the depth of the fall.&lt;/p&gt;"
                "&lt;p&gt;Provenance: a phenomenological clamp on the structural event (the cliff "
                "energetics are the released elastic energy, routed to W_diss_fracture). Default 0 = "
                "total fracture, the conservative case.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; cliff de fratura e residual f_res",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; fracture cliff and f_res residual",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Design da cauda de fadiga (fratura de Estágio III, energética do cliff)",
                   "Fatigue-tail design (Stage-III fracture, cliff energetics)",
                   "specs/2026-07-08-fatigue-fracture-tail-design.md")]),


    VarSpec(name="fat_ramp_D_on", symbol="D_on", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(0.6, 1.0, 9, "lin"), related=["fat_ramp_q", "fatigue_residual_frac"],
            equation="A_eff/A_s = 1 - ((D_fat - D_on)/(1 - D_on))^q   (D_fat > D_on;  D_on = 1.0 -> cliff de 1 ciclo)",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_ramp_D_on&lt;/code&gt; (D_on) escolhe ONDE, na vida de fadiga, a fratura "
                "deixa de ser um degrau e vira uma RAMPA de perda progressiva de se&amp;ccedil;&amp;atilde;o. "
                "Enquanto o dano de Miner D_fat fica abaixo de D_on, nada muda; acima, a &amp;aacute;rea "
                "resistente A_eff encolhe, k_b &amp;prop; A_eff cai e a pr&amp;eacute;-carga &amp;eacute; liberada "
                "pela s&amp;eacute;rie parafuso&amp;ndash;junta (g = (1&amp;minus;&amp;alpha;)(1+&amp;rho;)/((1&amp;minus;&amp;alpha;)+&amp;rho;)). "
                "Com D_on = 1.0 (default) a rampa NUNCA liga e o comportamento &amp;eacute; o cliff cl&amp;aacute;ssico, "
                "bit-id&amp;ecirc;ntico &amp;mdash; &amp;eacute; assim que as fontes adotadas com cliff ficam protegidas.&lt;/p&gt;"
                "&lt;p&gt;Proveni&amp;ecirc;ncia: classe handbook &amp;mdash; em HCF a propaga&amp;ccedil;&amp;atilde;o de trinca ocupa os "
                "&amp;uacute;ltimos ~10&amp;ndash;30% da vida, e no Liu 2025 o joelho medido fica em N_D/N_f = 0,72&amp;ndash;0,80 "
                "(coerente com D_on &amp;asymp; 0,75). A fratura em rampa ignora o auto-travamento "
                "(&lt;code&gt;loose_arrest_floor&lt;/code&gt;) por constru&amp;ccedil;&amp;atilde;o: perda de se&amp;ccedil;&amp;atilde;o n&amp;atilde;o &amp;eacute; atrito.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_ramp_D_on&lt;/code&gt; (D_on) picks WHERE in the fatigue life the fracture stops "
                "being a one-cycle cliff and becomes a progressive section-loss RAMP. While Miner damage "
                "D_fat stays below D_on nothing changes; above it the resisting area A_eff shrinks, "
                "k_b &amp;prop; A_eff drops and preload is released through the bolt&amp;ndash;joint series "
                "(g = (1&amp;minus;&amp;alpha;)(1+&amp;rho;)/((1&amp;minus;&amp;alpha;)+&amp;rho;)). With D_on = 1.0 (default) the ramp never "
                "fires and behaviour is the classic cliff, bit-identical &amp;mdash; protecting sources adopted with the cliff.&lt;/p&gt;"
                "&lt;p&gt;Provenance: handbook class &amp;mdash; in HCF crack propagation takes the last ~10&amp;ndash;30% of life, "
                "and the measured Liu 2025 knee sits at N_D/N_f = 0.72&amp;ndash;0.80 (consistent with D_on &amp;asymp; 0.75). "
                "The ramp bypasses self-locking (&lt;code&gt;loose_arrest_floor&lt;/code&gt;) by construction: section loss is not friction.&lt;/p&gt;"),
            refs=[("Rampa de perda de se&amp;ccedil;&amp;atilde;o &amp;mdash; prereg 2026-07-28 (Op&amp;ccedil;&amp;atilde;o A/A1, medida A-vs-B)",
                   "Section-loss ramp &amp;mdash; prereg 2026-07-28 (Option A/A1, measured A-vs-B)",
                   "liu2025_rampAB_resultado.md"),
                  ("Propaga&amp;ccedil;&amp;atilde;o = &amp;uacute;ltimos 10&amp;ndash;30% da vida (HCF)",
                   "Propagation = last 10&amp;ndash;30% of life (HCF)", "handbook")]),

    VarSpec(name="fat_ramp_q", symbol="q", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue",
                     "overrides": {"fatigue_enabled": True, "fat_ramp_D_on": 0.75}},
            sweep=(2.0, 12.0, 11, "lin"), related=["fat_ramp_D_on"],
            equation="alpha = ((D_fat - D_on)/(1 - D_on))^q ;  g = (1-alpha)(1+rho)/((1-alpha)+rho),  rho = k_j/k_b",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_ramp_q&lt;/code&gt; (q) &amp;eacute; a CONCAVIDADE da rampa de fratura: quanto maior, "
                "mais tempo a se&amp;ccedil;&amp;atilde;o resiste quase intacta e mais abrupto &amp;eacute; o mergulho final "
                "&amp;mdash; q &amp;rarr; &amp;infin; degenera no cliff, q pequeno espalha a perda pela janela toda. "
                "No Liu 2025 o par (D_on = 0,75, q = 8) reproduziu 10/10 cruzamentos de vida no n&amp;uacute;cleo "
                "amp0p4/amp0p5 e 6/7 no fig2 re-digitalizado.&lt;/p&gt;"
                "&lt;p&gt;S&amp;oacute; &amp;eacute; lido quando &lt;code&gt;fat_ramp_D_on&lt;/code&gt; &amp;lt; 1 (por isso esta curva "
                "usa D_on = 0,75). A energ&amp;eacute;tica &amp;eacute; a do cliff por incremento: cada passo libera "
                "&amp;Delta;U_internal para W_diss_fracture &amp;mdash; residual de conserva&amp;ccedil;&amp;atilde;o medido "
                "0,017&amp;ndash;0,151 J nos 4 casos da sonda A/B.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_ramp_q&lt;/code&gt; (q) is the CONCAVITY of the fracture ramp: the larger it is, "
                "the longer the section holds nearly intact and the steeper the final dive &amp;mdash; "
                "q &amp;rarr; &amp;infin; degenerates into the cliff, small q spreads the loss over the whole window. "
                "On Liu 2025 the pair (D_on = 0.75, q = 8) reproduced 10/10 life crossings on the "
                "amp0p4/amp0p5 core and 6/7 on the re-digitized fig2.&lt;/p&gt;"
                "&lt;p&gt;Only read when &lt;code&gt;fat_ramp_D_on&lt;/code&gt; &amp;lt; 1 (hence this page uses D_on = 0.75). "
                "Energetics follow the cliff per increment: each step releases &amp;Delta;U_internal into "
                "W_diss_fracture &amp;mdash; measured conservation residual 0.017&amp;ndash;0.151 J on the 4 A/B-probe cases.&lt;/p&gt;"),
            refs=[("Sonda A-vs-B: forma id&amp;ecirc;ntica, energia decide (&amp;sect;4.50)",
                   "A-vs-B probe: identical shape, energy decides (&amp;sect;4.50)",
                   "MODEL_LEGITIMACY.md &amp;sect;4.50")]),

    VarSpec(name="fat_Kt", symbol="K_t", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(1.0, 5.0, 15, "lin"), related=["fatigue_enabled"],
            equation="sigma_a = K_t * |F_amp| / A_s   (thread-root stress amplitude)",
            physics_pt=(
                "&lt;p&gt;A raiz da rosca é um entalhe agudo: a tensão local ali é muito maior que a "
                "tensão nominal F_amp/A_s da seção. &lt;code&gt;fat_Kt&lt;/code&gt; (K_t) é o fator de "
                "concentração de tensão geométrico que traduz essa amplificação. É na raiz que a "
                "trinca de fadiga nucleia, então K_t controla a severidade real do carregamento "
                "de fadiga. Default 3.5 = rosca laminada classe 10.9.&lt;/p&gt;"
                "&lt;p&gt;Na equação, K_t entra na amplitude de tensão: &amp;sigma;_a = "
                "K_t&amp;middot;|F_amp|/A_s. Um K_t maior aumenta &amp;sigma;_a, logo (via Goodman e a "
                "curva S-N) diminui a vida N_f &amp;minus; o cliff vem &lt;b&gt;mais cedo&lt;/b&gt; (move para a "
                "esquerda). Reduzir K_t suaviza o entalhe e adia a fratura. É uma das alavancas "
                "mais diretas sobre a posição do cliff nesta curva de amplitude alta.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: fator de raiz de rosca de handbook (depende da forma e do "
                "processo &amp;minus; laminada vs usinada); é um input por junta, não um botão livre.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;The thread root is a sharp notch: local stress there is far larger than the "
                "section's nominal stress F_amp/A_s. &lt;code&gt;fat_Kt&lt;/code&gt; (K_t) is the geometric "
                "stress-concentration factor that captures that amplification. Fatigue cracks "
                "nucleate at the root, so K_t sets the true severity of the fatigue loading. "
                "Default 3.5 = rolled class-10.9 thread.&lt;/p&gt;"
                "&lt;p&gt;In the equation K_t enters the stress amplitude: &amp;sigma;_a = "
                "K_t&amp;middot;|F_amp|/A_s. A larger K_t raises &amp;sigma;_a, so (via Goodman and the "
                "S-N curve) it shortens life N_f &amp;minus; the cliff comes &lt;b&gt;earlier&lt;/b&gt; (moves left). "
                "Lowering K_t softens the notch and delays fracture. It is one of the most direct "
                "levers on cliff position for this high-amplitude curve.&lt;/p&gt;"
                "&lt;p&gt;Provenance: a handbook thread-root factor (depends on form and process &amp;minus; "
                "rolled vs cut); a per-joint input, not a free knob.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; sigma_a = Kt*|F_amp|/A_s (raiz de rosca)",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; sigma_a = Kt*|F_amp|/A_s (thread root)",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Su-N bilinear classe 10.9 (Kt de raiz de rosca)",
                   "Bilinear Su-N class 10.9 (thread-root Kt)", "Yang (cl. 10.9)")]),

    VarSpec(name="fat_sigma_uts", symbol="sigma_uts", unit="Pa", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(8e8, 1.2e9, 15, "lin"), related=["fat_sigma_endurance"],
            equation="sigma_ar = sigma_a / (1 - sigma_m/sigma_uts),   sigma_m = F_0/A_s",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_sigma_uts&lt;/code&gt; (&amp;sigma;_uts) é a resistência última a tração do "
                "material do parafuso. Ela ancora a correção de Goodman de tensão MÉDIA: a fadiga "
                "não depende só da amplitude &amp;sigma;_a, mas também do nível médio &amp;sigma;_m = "
                "F_0/A_s em torno do qual o ciclo oscila. Como o afrouxamento faz F_0 (logo "
                "&amp;sigma;_m) cair ao longo do ensaio, a penalidade de Goodman evolui ciclo a ciclo. "
                "Default 1040 MPa (classe 10.9).&lt;/p&gt;"
                "&lt;p&gt;Na equação, &amp;sigma;_uts entra no denominador de Goodman: &amp;sigma;_ar = "
                "&amp;sigma;_a/(1 &amp;minus; &amp;sigma;_m/&amp;sigma;_uts), a tensão equivalente totalmente "
                "reversa que alimenta a S-N. Um &amp;sigma;_uts maior aproxima o denominador de 1, "
                "reduz a penalidade de tensão média, aumenta N_f &amp;minus; o cliff vem &lt;b&gt;mais tarde&lt;/b&gt;. "
                "Um &amp;sigma;_uts menor amplifica o efeito da média e antecipa a fratura.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: constante de material de handbook (por classe do parafuso); é "
                "por material. Aparece só via a razão &amp;sigma;_m/&amp;sigma;_uts, nunca sozinho.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_sigma_uts&lt;/code&gt; (&amp;sigma;_uts) is the ultimate tensile strength of "
                "the bolt material. It anchors the Goodman MEAN-stress correction: fatigue depends "
                "not only on the amplitude &amp;sigma;_a but also on the mean level &amp;sigma;_m = F_0/A_s "
                "the cycle oscillates about. Because loosening drives F_0 (hence &amp;sigma;_m) down "
                "over the test, the Goodman penalty evolves cycle by cycle. Default 1040 MPa "
                "(class 10.9).&lt;/p&gt;"
                "&lt;p&gt;In the equation &amp;sigma;_uts sits in the Goodman denominator: &amp;sigma;_ar = "
                "&amp;sigma;_a/(1 &amp;minus; &amp;sigma;_m/&amp;sigma;_uts), the fully-reversed equivalent stress "
                "that feeds the S-N curve. A larger &amp;sigma;_uts pushes the denominator toward 1, "
                "cuts the mean-stress penalty, raises N_f &amp;minus; the cliff comes &lt;b&gt;later&lt;/b&gt;. A smaller "
                "&amp;sigma;_uts amplifies the mean effect and brings fracture forward.&lt;/p&gt;"
                "&lt;p&gt;Provenance: a handbook material constant (per bolt class); it is per-material. "
                "It only appears through the ratio &amp;sigma;_m/&amp;sigma;_uts, never on its own.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; correção de Goodman de tensão média",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; Goodman mean-stress correction",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Design da cauda de fadiga (Goodman: sigma_ar = sigma_a/(1-sigma_m/uts))",
                   "Fatigue-tail design (Goodman: sigma_ar = sigma_a/(1-sigma_m/uts))",
                   "specs/2026-07-08-fatigue-fracture-tail-design.md")]),

    VarSpec(name="fat_sigma_knee", symbol="sigma_knee", unit="Pa", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(3e7, 8e7, 15, "lin"), related=["fat_sigma_endurance"], negligible=True,
            equation="N_f = C1*sigma_ar^(-m1)  if sigma_ar >= sigma_knee;  C2*sigma_ar^(-m2)  otherwise",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_sigma_knee&lt;/code&gt; (&amp;sigma;_knee) é o joelho da curva S-N (Wohler) "
                "bilinear: a tensão em que a inclinação muda de m_1 (ramo de alta tensão / baixo "
                "ciclo) para m_2 (ramo pós-joelho / alto ciclo). É a fronteira entre os dois "
                "regimes de fadiga. Default 50 MPa (parametrização Yang).&lt;/p&gt;"
                "&lt;p&gt;Na equação, o joelho escolhe QUAL ramo de &lt;code&gt;sun_life&lt;/code&gt; vale: "
                "&amp;sigma;_ar &amp;ge; &amp;sigma;_knee usa C_1/m_1; abaixo usa C_2/m_2. Mover o joelho "
                "muda em que regime a tensão equivalente de operação cai, alterando N_f e, com "
                "isso, a posição do cliff. &lt;b&gt;Ressalva desta curva:&lt;/b&gt; no baseline axial de "
                "amplitude alta &amp;sigma;_ar fica bem ACIMA de qualquer valor da faixa (30&amp;ndash;80 "
                "MPa), então o ponto de operação permanece no ramo C_1/m_1 e mover o joelho quase "
                "não reforma ESTA curva &amp;minus; ele decide o regime só em carregamento de baixa "
                "amplitude / vida muito longa.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: joelho da bilinear de Yang; é por material.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_sigma_knee&lt;/code&gt; (&amp;sigma;_knee) is the knee of the bilinear S-N "
                "(Wohler) curve: the stress where the slope switches from m_1 (high-stress / "
                "low-cycle branch) to m_2 (post-knee / high-cycle branch). It is the boundary "
                "between the two fatigue regimes. Default 50 MPa (Yang parametrization).&lt;/p&gt;"
                "&lt;p&gt;In the equation the knee chooses WHICH branch of &lt;code&gt;sun_life&lt;/code&gt; "
                "applies: &amp;sigma;_ar &amp;ge; &amp;sigma;_knee uses C_1/m_1; below it uses C_2/m_2. Moving "
                "the knee changes which regime the operating equivalent stress sits in, altering "
                "N_f and thereby cliff position. &lt;b&gt;Caveat for this curve:&lt;/b&gt; in the "
                "high-amplitude axial baseline &amp;sigma;_ar sits well ABOVE the whole range "
                "(30&amp;ndash;80 MPa), so the operating point stays on the C_1/m_1 branch and moving "
                "the knee barely reshapes THIS curve &amp;minus; it only picks the regime under low-amplitude "
                "/ very-long-life loading.&lt;/p&gt;"
                "&lt;p&gt;Provenance: the knee of Yang's bilinear curve; it is per-material.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; Su-N bilinear (transição m1->m2 no joelho)",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; bilinear Su-N (m1->m2 transition at the knee)",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Su-N bilinear classe 10.9 (joelho da Wohler)",
                   "Bilinear Su-N class 10.9 (Wohler knee)", "Yang (cl. 10.9)")]),

    VarSpec(name="fat_C1", symbol="C_1", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(1e32, 1e33, 9, "log"), related=["fat_m1"],
            equation="N_f = C1 * sigma_ar^(-m1)   (high-stress / low-cycle branch, sigma_ar >= sigma_knee)",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_C1&lt;/code&gt; (C_1) é o coeficiente (intercepto) do ramo de ALTA tensão / "
                "baixo ciclo da lei de Basquin bilinear, N_f = C_1&amp;middot;&amp;sigma;_ar^(&amp;minus;m_1). "
                "Em log-log da S-N, C_1 fixa a posição vertical da reta de alto ciclo; junto com o "
                "expoente m_1 define quantos ciclos o parafuso aguenta numa dada amplitude alta. É "
                "o ramo ATIVO nesta curva, onde a tensão equivalente é alta.&lt;/p&gt;"
                "&lt;p&gt;Um C_1 maior desloca a reta S-N para cima: mais vida N_f na mesma tensão, logo "
                "o dano de Miner acumula mais devagar e o cliff vem &lt;b&gt;mais tarde&lt;/b&gt;. Um C_1 menor "
                "antecipa a fratura. O slider é logarítmico (1e32&amp;ndash;1e33) porque a vida é "
                "extremamente sensível a esse coeficiente.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: é a curva de Wohler do material &amp;minus; o par (C_1, m_1) não é "
                "identificável isoladamente de um único ensaio; é o centro S-N do material, nunca "
                "um botão livre (as constantes S-N são por material).&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_C1&lt;/code&gt; (C_1) is the coefficient (intercept) of the HIGH-stress / "
                "low-cycle branch of the bilinear Basquin law, N_f = "
                "C_1&amp;middot;&amp;sigma;_ar^(&amp;minus;m_1). On a log-log S-N plot C_1 fixes the vertical "
                "position of the high-cycle line; with the exponent m_1 it sets how many cycles the "
                "bolt survives at a given high amplitude. This is the ACTIVE branch on this curve, "
                "where the equivalent stress is high.&lt;/p&gt;"
                "&lt;p&gt;A larger C_1 shifts the S-N line up: more life N_f at the same stress, so Miner "
                "damage accrues more slowly and the cliff comes &lt;b&gt;later&lt;/b&gt;. A smaller C_1 brings "
                "fracture forward. The slider is logarithmic (1e32&amp;ndash;1e33) because life is "
                "extremely sensitive to this coefficient.&lt;/p&gt;"
                "&lt;p&gt;Provenance: it is the material's Wohler curve &amp;minus; the pair (C_1, m_1) is not "
                "identifiable on its own from a single test; it is the material's S-N center, never "
                "a free knob (the S-N constants are per-material).&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; ramo alto-ciclo N_f = C1*sigma^-m1",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; high-cycle branch N_f = C1*sigma^-m1",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Su-N bilinear classe 10.9 (transfere cross-material a ~2.3x)",
                   "Bilinear Su-N class 10.9 (transfers cross-material to ~2.3x)",
                   "Yang (cl. 10.9)")]),

    VarSpec(name="fat_m1", symbol="m_1", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(3.0, 5.0, 15, "lin"), related=["fat_C1"],
            equation="N_f = C1 * sigma_ar^(-m1)   (high-cycle slope; steeper m1 = stronger stress sensitivity)",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_m1&lt;/code&gt; (m_1) é o expoente de Basquin (inclinação) do ramo de alta "
                "tensão da S-N. Ele mede quão rápido a vida cai quando a tensão sobe: um m_1 maior "
                "significa uma reta S-N mais íngreme, típico de aços (m_1 ~ 3&amp;ndash;5). Default "
                "3.5. Junto com C_1 forma o par que descreve o regime de baixo ciclo, o ramo "
                "ATIVO nesta curva de amplitude alta.&lt;/p&gt;"
                "&lt;p&gt;Na equação N_f = C_1&amp;middot;&amp;sigma;_ar^(&amp;minus;m_1). Como a tensão equivalente "
                "de operação é &amp;gt; 1 Pa, um m_1 maior reduz N_f fortemente &amp;minus; o cliff vem &lt;b&gt;mais "
                "cedo&lt;/b&gt;. Reduzir m_1 achata a S-N e adia a fratura. Junto com &amp;sigma;_uts e K_t, "
                "é um dos parâmetros que mais desloca a POSIÇÃO do cliff nesta curva.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: expoente de Wohler por material; anda em par com C_1 (a "
                "continuidade no joelho amarra os dois ramos). Não é um botão livre.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_m1&lt;/code&gt; (m_1) is the Basquin exponent (slope) of the high-stress "
                "branch of the S-N curve. It measures how fast life drops as stress rises: a "
                "larger m_1 means a steeper S-N line, typical of steels (m_1 ~ 3&amp;ndash;5). Default "
                "3.5. With C_1 it forms the pair that describes the low-cycle regime, the ACTIVE "
                "branch on this high-amplitude curve.&lt;/p&gt;"
                "&lt;p&gt;In the equation N_f = C_1&amp;middot;&amp;sigma;_ar^(&amp;minus;m_1). Since the operating "
                "equivalent stress is &amp;gt; 1 Pa, a larger m_1 sharply cuts N_f &amp;minus; the cliff comes "
                "&lt;b&gt;earlier&lt;/b&gt;. Lowering m_1 flattens the S-N and delays fracture. With &amp;sigma;_uts "
                "and K_t, it is one of the parameters that most shifts the cliff POSITION on this "
                "curve.&lt;/p&gt;"
                "&lt;p&gt;Provenance: a per-material Wohler exponent; it moves in a pair with C_1 "
                "(continuity at the knee ties the two branches). Not a free knob.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; inclinação S-N acima do joelho (m1)",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; S-N slope above the knee (m1)",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Su-N bilinear classe 10.9 (expoente de Basquin)",
                   "Bilinear Su-N class 10.9 (Basquin exponent)", "Yang (cl. 10.9)")]),

    VarSpec(name="fat_C2", symbol="C_2", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(1e49, 1e50, 9, "log"), related=["fat_m2"], negligible=True,
            equation="N_f = C2 * sigma_ar^(-m2)   (post-knee / high-cycle branch, sigma_ar < sigma_knee)",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_C2&lt;/code&gt; (C_2) é o coeficiente do ramo PÓS-joelho (alto ciclo, "
                "perto do limite de resistência) da S-N bilinear, N_f = "
                "C_2&amp;middot;&amp;sigma;_ar^(&amp;minus;m_2). Governa o regime de vida longa: tensões "
                "abaixo do joelho, onde a curva desce muito mais íngreme. O valor é enorme "
                "(~1e49) porque, com o expoente m_2 grande, C_2 precisa ser alto para casar com "
                "C_1 na continuidade do joelho.&lt;/p&gt;"
                "&lt;p&gt;Um C_2 maior alonga a vida abaixo do joelho, empurrando o cliff para &lt;b&gt;mais "
                "tarde&lt;/b&gt; (ou para fora da janela). &lt;b&gt;Ressalva desta curva:&lt;/b&gt; no baseline "
                "axial de amplitude alta &amp;sigma;_ar fica ACIMA do joelho, então &lt;code&gt;sun_life&lt;/code&gt; "
                "usa sempre o ramo C_1/m_1 &amp;minus; mover C_2 quase não reforma ESTA curva. Ele importa "
                "em carregamento de baixa amplitude / vida muito longa.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: por material; a continuidade com C_1/m_1 no joelho é uma "
                "restrição do ajuste, não um grau de liberdade independente.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_C2&lt;/code&gt; (C_2) is the coefficient of the POST-knee (high-cycle, "
                "near the endurance limit) branch of the bilinear S-N, N_f = "
                "C_2&amp;middot;&amp;sigma;_ar^(&amp;minus;m_2). It governs the long-life regime: stresses "
                "below the knee, where the curve drops much more steeply. The value is huge "
                "(~1e49) because, with the large exponent m_2, C_2 must be high to match C_1 for "
                "continuity at the knee.&lt;/p&gt;"
                "&lt;p&gt;A larger C_2 stretches life below the knee, pushing the cliff &lt;b&gt;later&lt;/b&gt; (or "
                "out of the window). &lt;b&gt;Caveat for this curve:&lt;/b&gt; in the high-amplitude axial "
                "baseline &amp;sigma;_ar sits ABOVE the knee, so &lt;code&gt;sun_life&lt;/code&gt; always uses the "
                "C_1/m_1 branch &amp;minus; moving C_2 barely reshapes THIS curve. It matters under "
                "low-amplitude / very-long-life loading.&lt;/p&gt;"
                "&lt;p&gt;Provenance: per-material; continuity with C_1/m_1 at the knee is a fit "
                "constraint, not an independent degree of freedom.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; ramo pós-joelho N_f = C2*sigma^-m2",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; post-knee branch N_f = C2*sigma^-m2",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Su-N bilinear classe 10.9 (ramo de alto ciclo)",
                   "Bilinear Su-N class 10.9 (high-cycle branch)", "Yang (cl. 10.9)")]),

    VarSpec(name="fat_m2", symbol="m_2", unit="-", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(5.0, 7.0, 15, "lin"), related=["fat_C2"], negligible=True,
            equation="N_f = C2 * sigma_ar^(-m2)   (post-knee slope, steeper than m1)",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_m2&lt;/code&gt; (m_2) é o expoente (inclinação) do ramo pós-joelho da S-N. "
                "É mais íngreme que m_1 (default 6.0 vs 3.5): perto do limite de resistência a "
                "curva de Wohler desce muito mais rápido, então pequenas variações de tensão "
                "mudam a vida em ordens de grandeza. Descreve a alta sensibilidade da vida no "
                "regime de alto ciclo.&lt;/p&gt;"
                "&lt;p&gt;Na equação N_f = C_2&amp;middot;&amp;sigma;_ar^(&amp;minus;m_2), valida abaixo do joelho. "
                "Um m_2 maior torna a vida (e a posição do cliff) extremamente sensível a tensão "
                "nesse regime. &lt;b&gt;Ressalva desta curva:&lt;/b&gt; como o baseline axial opera ACIMA do "
                "joelho, o ramo C_2/m_2 não é acionado e mover m_2 quase não reforma ESTA curva &amp;minus; "
                "seu efeito aparece em amplitudes baixas.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: expoente de Wohler por material; m_2 &amp;gt; m_1 por construção "
                "(a S-N dobra para baixo perto do limite de resistência).&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_m2&lt;/code&gt; (m_2) is the exponent (slope) of the post-knee branch of "
                "the S-N curve. It is steeper than m_1 (default 6.0 vs 3.5): near the endurance "
                "limit the Wohler curve drops much faster, so small stress changes swing life by "
                "orders of magnitude. It describes the high sensitivity of life in the high-cycle "
                "regime.&lt;/p&gt;"
                "&lt;p&gt;In the equation N_f = C_2&amp;middot;&amp;sigma;_ar^(&amp;minus;m_2), valid below the knee. "
                "A larger m_2 makes life (and cliff position) extremely sensitive to stress in that "
                "regime. &lt;b&gt;Caveat for this curve:&lt;/b&gt; since the axial baseline operates ABOVE the "
                "knee, the C_2/m_2 branch is not engaged and moving m_2 barely reshapes THIS curve "
                "&amp;minus; its effect shows at low amplitudes.&lt;/p&gt;"
                "&lt;p&gt;Provenance: a per-material Wohler exponent; m_2 &amp;gt; m_1 by construction (the "
                "S-N bends down near the endurance limit).&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; inclinação S-N abaixo do joelho (m2)",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; S-N slope below the knee (m2)",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Su-N bilinear classe 10.9 (m2 > m1)",
                   "Bilinear Su-N class 10.9 (m2 > m1)", "Yang (cl. 10.9)")]),

    VarSpec(name="fat_sigma_endurance", symbol="sigma_e", unit="Pa", group="fatigue", category="form",
            context={"baseline": "fatigue", "overrides": {"fatigue_enabled": True}},
            sweep=(4.6e7, 6.3e7, 15, "lin"), anchor_key="fat_sigma_endurance",
            related=["fat_sigma_knee"], negligible=True,
            equation="N_f = infinity  if sigma_ar <= sigma_e   (endurance limit -> infinite life, no cliff)",
            physics_pt=(
                "&lt;p&gt;&lt;code&gt;fat_sigma_endurance&lt;/code&gt; (&amp;sigma;_e) é o limite de resistência a "
                "fadiga: abaixo dessa tensão equivalente a curva S-N é plana e a vida é infinita &amp;minus; "
                "nenhuma trinca nucleia, não há dano de Miner, o cliff &lt;b&gt;nunca acontece&lt;/b&gt;. É o "
                "gatilho que decide se a fadiga ocorre. Default do engine 50 MPa (classe 10.9 "
                "handbook).&lt;/p&gt;"
                "&lt;p&gt;Na equação, &lt;code&gt;sun_life&lt;/code&gt; devolve N_f = &amp;#8734; (logo &amp;Delta;D_fat = 0) "
                "sempre que &amp;sigma;_ar &amp;le; &amp;sigma;_e. Se o ponto de operação estiver acima do "
                "limite, o dano acumula e o cliff existe; elevar &amp;sigma;_e pode empurrar a tensão "
                "para baixo do limite e fazer o cliff &lt;b&gt;desaparecer&lt;/b&gt; da janela &amp;minus; é a alavanca "
                "mais forte sobre a EXISTÊNCIA do cliff. &lt;b&gt;Ressalva desta curva:&lt;/b&gt; no baseline "
                "axial de amplitude alta &amp;sigma;_ar fica muito acima da faixa (46&amp;ndash;63 MPa), "
                "então varrer &amp;sigma;_e dentro da banda quase não move ESTA curva &amp;minus; o limite é "
                "decisivo em amplitude baixa.&lt;/p&gt;"
                "&lt;p&gt;Proveniência: ancorado em schaumann2015 &amp;minus; banda MEDIDA 46&amp;ndash;63 MPa (M36/M64; "
                "o zinco penaliza ~12%). O default de 50 MPa cai DENTRO da banda para parafusos "
                "grandes; a VDI sobrestima 19&amp;ndash;50% (não-conservador). É por tamanho e por "
                "revestimento, logo um input por junta &amp;minus; a leitura de proveniência abaixo do "
                "gráfico avisa quando o valor sai da banda medida.&lt;/p&gt;"),
            physics_en=(
                "&lt;p&gt;&lt;code&gt;fat_sigma_endurance&lt;/code&gt; (&amp;sigma;_e) is the fatigue (endurance) limit: "
                "below this equivalent stress the S-N curve is flat and life is infinite &amp;minus; no crack "
                "nucleates, no Miner damage, the cliff &lt;b&gt;never happens&lt;/b&gt;. It is the gate that "
                "decides whether fatigue occurs at all. Engine default 50 MPa (class 10.9 "
                "handbook).&lt;/p&gt;"
                "&lt;p&gt;In the equation &lt;code&gt;sun_life&lt;/code&gt; returns N_f = &amp;#8734; (so &amp;Delta;D_fat = "
                "0) whenever &amp;sigma;_ar &amp;le; &amp;sigma;_e. If the operating point sits above the limit, "
                "damage accumulates and the cliff exists; raising &amp;sigma;_e can push the stress "
                "below the limit and make the cliff &lt;b&gt;disappear&lt;/b&gt; from the window &amp;minus; the strongest "
                "lever on the EXISTENCE of the cliff. &lt;b&gt;Caveat for this curve:&lt;/b&gt; in the "
                "high-amplitude axial baseline &amp;sigma;_ar sits far above the range (46&amp;ndash;63 MPa), "
                "so sweeping &amp;sigma;_e within the band barely moves THIS curve &amp;minus; the limit is "
                "decisive at low amplitude.&lt;/p&gt;"
                "&lt;p&gt;Provenance: anchored to schaumann2015 &amp;minus; MEASURED band 46&amp;ndash;63 MPa (M36/M64; "
                "zinc coating penalizes ~12%). The 50 MPa default sits INSIDE the band for large "
                "bolts; VDI overestimates by 19&amp;ndash;50% (non-conservative). It is per-size and "
                "per-coating, hence a per-joint input &amp;minus; the provenance readout under the plot flags "
                "values leaving the measured band.&lt;/p&gt;"),
            refs=[("&amp;sect;4.6 FatigueLoss &amp;minus; limite de resistência (vida infinita abaixo dele)",
                   "&amp;sect;4.6 FatigueLoss &amp;minus; endurance limit (infinite life below it)",
                   "MODEL_MATH_REFERENCE.md"),
                  ("Limites de fadiga medidos 46-63 MPa (M36/M64; penalidade de zinco ~12%)",
                   "Measured fatigue limits 46-63 MPa (M36/M64; zinc penalty ~12%)",
                   "schaumann2015")]),
])

# =============================== L1-L7 GAPS (12) — plano 2026-07-16, fix wave final ===============================
VARIABLE_SPECS.extend([
    VarSpec(
        name="creep_mode", symbol="", unit="", group="creep", category="mode",
        context={"baseline": "creep", "overrides": {"creep_t_c": 1e4}},
        choices=["", "saturating"], related=["creep_t_c", "creep_alpha_sat", "C_creep"],
        equation='"": delta_creep=C_creep*F_0*ln(t/t0+1) (ilimitado)   |   "saturating": delta_creep=C_creep*F_0*(1-exp[-(t/creep_t_c)^creep_alpha_sat]) (limitado)',
        physics_pt=(
            "&lt;p&gt;Seleciona a LEI CINÉTICA do creep/assentamento log-tempo. &lt;b&gt;&amp;quot;&amp;quot;&lt;/b&gt; "
            "(default): log-t ILIMITADO (cresce para sempre, cada vez mais devagar) &amp;minus; coincide, "
            "por coincidência feliz, com a regressão de relaxação por coating do Nah 2014 para "
            "faiamento (&lt;code&gt;Creep = &amp;alpha; + &amp;beta;&amp;middot;log&amp;#8321;&amp;#8320;t&lt;/code&gt;). "
            "&lt;b&gt;&amp;quot;saturating&amp;quot;&lt;/b&gt;: forma de 1&amp;ordm;s princípios de Alamos "
            "(2021+2022) para creep de contato &amp;minus; &amp;delta;_creep tende a um teto "
            "&amp;delta;_max = C_creep&amp;middot;F_0 (bounded).&lt;/p&gt;"
            "&lt;p&gt;Entra em &lt;code&gt;CreepLoss.rate()&lt;/code&gt;; no gráfico, a curva log-t continua "
            "perdendo pré-carga na cauda enquanto a saturante achata (compare em t grande, este "
            "baseline roda a 1/60 Hz &amp;minus; janela temporal longa). O seletor troca entre as duas "
            "curvas pré-computadas.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: modo discreto (string), NUNCA fittable (mesmo idioma de "
            "&lt;code&gt;kj_mode&lt;/code&gt;/&lt;code&gt;conform_driver&lt;/code&gt;/&lt;code&gt;k_tr_mode&lt;/code&gt; &amp;minus; "
            "mode switches nunca entram no PARAMETER_REGISTRY como fittable=True). Capacidade "
            "validada (&lt;code&gt;tests/test_l5_creep_saturating.py&lt;/code&gt;, 9 testes, sem regressão "
            "nos casos de creep JCSR/Caccese/Qin/li2022marstruc) mas NÃO adotada &amp;minus; o default "
            "segue log-t; a decisão de usar a saturante fica com o calibrador se uma curva mostrar "
            "platô claro.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Selects the KINETIC LAW of the log-time creep/settling. &lt;b&gt;&amp;quot;&amp;quot;&lt;/b&gt; "
            "(default): UNBOUNDED log-t (grows forever, ever more slowly) &amp;minus; it happens to "
            "coincide, by a happy coincidence, with the Nah 2014 coating-relaxation regression for "
            "faying surfaces (&lt;code&gt;Creep = &amp;alpha; + &amp;beta;&amp;middot;log&amp;#8321;&amp;#8320;t&lt;/code&gt;). "
            "&lt;b&gt;&amp;quot;saturating&amp;quot;&lt;/b&gt;: Alamos (2021+2022) first-principles form for "
            "contact creep &amp;minus; &amp;delta;_creep approaches a ceiling &amp;delta;_max = "
            "C_creep&amp;middot;F_0 (bounded).&lt;/p&gt;"
            "&lt;p&gt;It enters &lt;code&gt;CreepLoss.rate()&lt;/code&gt;; in the plot, the log-t curve keeps "
            "losing preload in the tail while the saturating one flattens out (compare at large t, "
            "this baseline runs at 1/60 Hz &amp;minus; a long time window). The selector switches between "
            "the two pre-computed curves.&lt;/p&gt;"
            "&lt;p&gt;Provenance: discrete mode (string), NEVER fittable (same idiom as "
            "&lt;code&gt;kj_mode&lt;/code&gt;/&lt;code&gt;conform_driver&lt;/code&gt;/&lt;code&gt;k_tr_mode&lt;/code&gt; &amp;minus; mode "
            "switches never enter PARAMETER_REGISTRY as fittable=True). Validated capability "
            "(&lt;code&gt;tests/test_l5_creep_saturating.py&lt;/code&gt;, 9 tests, no regression on the creep "
            "cases JCSR/Caccese/Qin/li2022marstruc) but NOT adopted &amp;minus; the default stays log-t; "
            "using the saturating form is the calibrator's call if a curve shows a clear plateau.&lt;/p&gt;"),
        refs=[("&amp;sect;4.2 CreepLoss &amp;minus; log-t vs forma saturante opt-in",
               "&amp;sect;4.2 CreepLoss &amp;minus; log-t vs opt-in saturating form",
               "MODEL_MATH_REFERENCE.md"),
              ("Alamos 2021+2022 &amp;minus; creep de contato de 1&amp;ordm;s princípios (Ti superplástico, so' a forma transfere)",
               "Alamos 2021+2022 &amp;minus; first-principles contact creep (superplastic Ti, only the form transfers)",
               "alamos2021"),
              ("Nah 2014 &amp;minus; regressão log-t de faiamento por coating (mesma forma, achado feliz)",
               "Nah 2014 &amp;minus; log-t faying-relaxation regression by coating (same form, happy find)",
               "nah2014")]),

    VarSpec(
        name="creep_t_c", symbol="t_c", unit="s", group="creep", category="form",
        context={"baseline": "creep", "overrides": {"creep_mode": "saturating"}},
        sweep=(1e2, 1e6, 13, "log"), related=["creep_mode", "creep_alpha_sat"],
        equation="delta_creep(t) = C_creep*F_0*(1-exp[-(t/creep_t_c)^creep_alpha_sat]);  S(t=creep_t_c) = 1-1/e (independente de creep_alpha_sat)",
        physics_pt=(
            "&lt;p&gt;Constante de tempo da forma saturante do creep (só é lida quando "
            "&lt;code&gt;creep_mode&amp;quot;saturating&amp;quot;&lt;/code&gt;, pré-ligado aqui via overrides). Marca "
            "o instante em que o creep atinge 1&amp;minus;1/e &amp;asymp; 63% do seu teto "
            "&amp;delta;_max = C_creep&amp;middot;F_0.&lt;/p&gt;"
            "&lt;p&gt;&lt;code&gt;creep_t_c&lt;/code&gt; pequeno satura cedo (o creep acha que é log-t só no "
            "início, depois achata rápido); &lt;code&gt;creep_t_c&lt;/code&gt; grande empurra a saturação "
            "para fora da janela de teste (parece log-t quase o tempo todo, só diverge quando t se "
            "aproxima dele). Design de Alamos: t_c &amp;prop; 1/(a&amp;middot;p&amp;#8319;) &amp;minus; pressão "
            "ACELERA a depleção (mesma ideia do gate de conformação, mas aqui &lt;code&gt;creep_t_c&lt;/code&gt; "
            "é uma CONSTANTE, não uma função de p &amp;minus; o acoplamento a pressão não foi "
            "implementado).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: Alamos 2021+2022 (creep de contato de 1&amp;ordm;s princípios, Ti "
            "superplástico 10&amp;ndash;30 MPa &amp;minus; só a FORMA transfere, não o valor). Default 0.0 "
            "(=OFF, cai no log-t). Capacidade opt-in default-inerte, validada mas não adotada.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Time constant of the saturating creep form (only read when "
            "&lt;code&gt;creep_mode=&amp;quot;saturating&amp;quot;&lt;/code&gt;, pre-enabled here via overrides). It "
            "marks the instant the creep reaches 1&amp;minus;1/e &amp;asymp; 63% of its ceiling "
            "&amp;delta;_max = C_creep&amp;middot;F_0.&lt;/p&gt;"
            "&lt;p&gt;A small &lt;code&gt;creep_t_c&lt;/code&gt; saturates early (the creep looks log-t only at "
            "first, then flattens fast); a large &lt;code&gt;creep_t_c&lt;/code&gt; pushes the saturation past "
            "the test window (it looks log-t almost the whole time, only diverging as t approaches "
            "it). Alamos design: t_c &amp;prop; 1/(a&amp;middot;p&amp;#8319;) &amp;minus; pressure ACCELERATES the "
            "depletion (same idea as the conformation gate, but here &lt;code&gt;creep_t_c&lt;/code&gt; is a "
            "CONSTANT, not a function of p &amp;minus; the pressure coupling was not implemented).&lt;/p&gt;"
            "&lt;p&gt;Provenance: Alamos 2021+2022 (first-principles contact creep, superplastic Ti "
            "10&amp;ndash;30 MPa &amp;minus; only the FORM transfers, not the value). Default 0.0 (=OFF, falls "
            "to log-t). Opt-in default-inert capability, validated but not adopted.&lt;/p&gt;"),
        refs=[("&amp;sect;4.2 CreepLoss &amp;minus; constante de tempo da saturante (Alamos)",
               "&amp;sect;4.2 CreepLoss &amp;minus; saturating form time constant (Alamos)",
               "MODEL_MATH_REFERENCE.md"),
              ("Alamos 2021+2022 &amp;minus; t_c &amp;prop; 1/(a&amp;middot;p&amp;#8319;), pressão acelera a depleção",
               "Alamos 2021+2022 &amp;minus; t_c &amp;prop; 1/(a&amp;middot;p&amp;#8319;), pressure accelerates depletion",
               "alamos2021")]),

    VarSpec(
        name="creep_alpha_sat", symbol="alpha_sat", unit="-", group="creep", category="form",
        context={"baseline": "creep", "overrides": {"creep_mode": "saturating", "creep_t_c": 1e4}},
        sweep=(0.3, 3.0, 15, "lin"), related=["creep_t_c"],
        equation="delta_creep(t) = C_creep*F_0*(1-exp[-(t/creep_t_c)^creep_alpha_sat])   (stretched exponential)",
        physics_pt=(
            "&lt;p&gt;Expoente de FORMA (stretched exponential) da transição da saturante &amp;minus; molda "
            "a NITIDEZ do joelho log-t&amp;rarr;platô, não a escala (o valor de S no instante "
            "t=creep_t_c vale sempre 1&amp;minus;1/e, independente de &lt;code&gt;creep_alpha_sat&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;&lt;code&gt;creep_alpha_sat&lt;/code&gt;&amp;lt;1 = transição alongada (cauda mais gorda antes "
            "do platô); &lt;code&gt;creep_alpha_sat&lt;/code&gt;&amp;gt;1 = transição mais abrupta (quase um "
            "degrau). Só tem efeito com &lt;code&gt;creep_mode=&amp;quot;saturating&amp;quot;&lt;/code&gt; E "
            "&lt;code&gt;creep_t_c&lt;/code&gt;&amp;gt;0 (ambos pré-ligados aqui via overrides).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: parte da mesma forma de Alamos 2021+2022 (stretched exponential é "
            "uma generalização comum de relaxação sub-difusiva em creep de contato). Default 1.0 "
            "(exponencial simples, &amp;alpha;=1). Capacidade opt-in, validada "
            "(&lt;code&gt;tests/test_l5_creep_saturating.py&lt;/code&gt;) mas não adotada.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Shape exponent (stretched exponential) of the saturating transition &amp;minus; it "
            "shapes the SHARPNESS of the log-t&amp;rarr;plateau knee, not the scale (the value of S at "
            "t=creep_t_c is always 1&amp;minus;1/e, independent of &lt;code&gt;creep_alpha_sat&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;&lt;code&gt;creep_alpha_sat&lt;/code&gt;&amp;lt;1 = a stretched transition (a fatter tail "
            "before the plateau); &lt;code&gt;creep_alpha_sat&lt;/code&gt;&amp;gt;1 = a sharper transition (almost "
            "a step). It only has an effect with &lt;code&gt;creep_mode=&amp;quot;saturating&amp;quot;&lt;/code&gt; AND "
            "&lt;code&gt;creep_t_c&lt;/code&gt;&amp;gt;0 (both pre-enabled here via overrides).&lt;/p&gt;"
            "&lt;p&gt;Provenance: part of the same Alamos 2021+2022 form (a stretched exponential is a "
            "common generalization of sub-diffusive relaxation in contact creep). Default 1.0 "
            "(plain exponential, &amp;alpha;=1). Opt-in capability, validated "
            "(&lt;code&gt;tests/test_l5_creep_saturating.py&lt;/code&gt;) but not adopted.&lt;/p&gt;"),
        refs=[("&amp;sect;4.2 CreepLoss &amp;minus; expoente de forma da saturante (stretched exponential)",
               "&amp;sect;4.2 CreepLoss &amp;minus; saturating form shape exponent (stretched exponential)",
               "MODEL_MATH_REFERENCE.md"),
              ("Alamos 2021+2022 &amp;minus; forma saturante de 1&amp;ordm;s princípios",
               "Alamos 2021+2022 &amp;minus; first-principles saturating form",
               "alamos2021")]),

    VarSpec(
        name="famp_couple_on", symbol="", unit="", group="slip_regime", category="mode",
        context={"baseline": "transverse", "overrides": {}},
        choices=[0.0, 1.0],
        related=["mu_eff_lo", "mu_eff_F0_ref", "gross_ceiling_decay", "couple_famp_slip"],
        equation="delta_amp is not None E famp_couple_on>0: F_amp <- min(F_amp, mu_eff(F0)*F0)   (teto de Coulomb, ANTES de qualquer mecanismo)",
        physics_pt=(
            "&lt;p&gt;Liga o teto FÍSICO de Coulomb sobre a amplitude de força &lt;code&gt;F_amp&lt;/code&gt; em "
            "modo deslocamento-controlado (disp-mode): fisicamente &lt;code&gt;F_amp&lt;/code&gt; não pode "
            "superar &amp;mu;_eff(F0)&amp;middot;F0 &amp;minus; acima disso a junta já está em gross slip "
            "pleno e o excesso IMPOSTO não vira mais força TRANSMITIDA, só mais deslocamento "
            "relativo (já contabilizado via &lt;code&gt;delta_amp&lt;/code&gt;). É um clamp GERAL, aplicado "
            "no topo de &lt;code&gt;step_cycle&lt;/code&gt; antes de qualquer mecanismo ler &lt;code&gt;F_amp&lt;/code&gt; "
            "&amp;minus; diferente de &lt;code&gt;couple_famp_slip&lt;/code&gt; (existente, só dentro de "
            "&lt;code&gt;RotationalLooseningLoss&lt;/code&gt;, só em regime Cattaneo-Mindlin).&lt;/p&gt;"
            "&lt;p&gt;Neste baseline (F_amp=20 kN, F0=50 kN, &amp;mu;_bearing=0,15 &amp;rArr; teto &amp;asymp; 7,5 "
            "kN), ligar o clamp reduz bastante o &lt;code&gt;F_amp&lt;/code&gt; que alimenta o afrouxamento "
            "rotacional &amp;minus; a curva &amp;quot;ligado&amp;quot; perde MENOS pré-carga que a "
            "&amp;quot;desligado&amp;quot; (o excesso de força imposta acima do teto físico não drenava "
            "pré-carga real). 0.0 (default) mantém &lt;code&gt;F_amp&lt;/code&gt; e &lt;code&gt;delta_amp&lt;/code&gt; "
            "independentes (retrocompatível, bit-idêntico).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: forma com 3 fontes (ver &lt;code&gt;mu_eff_lo&lt;/code&gt;/&lt;code&gt;mu_eff_F0_ref&lt;/code&gt;/"
            "&lt;code&gt;gross_ceiling_decay&lt;/code&gt;). Switch BINÁRIO, NUNCA fittable (sem sinal de "
            "gradiente entre &amp;quot;ligado&amp;quot; e &amp;quot;mais ligado&amp;quot; &amp;minus; mesmo idioma de "
            "&lt;code&gt;kj_mode&lt;/code&gt;/&lt;code&gt;flank_wear_on&lt;/code&gt;). Capacidade default-inerte, testada "
            "(11 testes, &lt;code&gt;tests/test_l3_famp_coupling.py&lt;/code&gt;: fórmula, bit-identidade, "
            "guarda de caminho de código, efeito físico), NÃO calibrada per-rig &amp;minus; nenhuma "
            "adoção comportamental feita ainda.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Turns on the PHYSICAL Coulomb ceiling over the force amplitude &lt;code&gt;F_amp&lt;/code&gt; "
            "in displacement-controlled mode (disp-mode): physically &lt;code&gt;F_amp&lt;/code&gt; cannot "
            "exceed &amp;mu;_eff(F0)&amp;middot;F0 &amp;minus; above that the joint is already in full gross "
            "slip and the IMPOSED excess does not turn into more TRANSMITTED force, only more "
            "relative displacement (already accounted for via &lt;code&gt;delta_amp&lt;/code&gt;). It is a "
            "GENERAL clamp, applied at the top of &lt;code&gt;step_cycle&lt;/code&gt; before any mechanism "
            "reads &lt;code&gt;F_amp&lt;/code&gt; &amp;minus; different from &lt;code&gt;couple_famp_slip&lt;/code&gt; (existing, "
            "only inside &lt;code&gt;RotationalLooseningLoss&lt;/code&gt;, only in Cattaneo-Mindlin regime).&lt;/p&gt;"
            "&lt;p&gt;In this baseline (F_amp=20 kN, F0=50 kN, &amp;mu;_bearing=0.15 &amp;rArr; ceiling &amp;asymp; "
            "7.5 kN), turning the clamp on greatly reduces the &lt;code&gt;F_amp&lt;/code&gt; that feeds "
            "rotational loosening &amp;minus; the &amp;quot;on&amp;quot; curve loses LESS preload than the "
            "&amp;quot;off&amp;quot; one (the imposed-force excess above the physical ceiling was not "
            "draining real preload). 0.0 (default) keeps &lt;code&gt;F_amp&lt;/code&gt; and &lt;code&gt;delta_amp&lt;/code&gt; "
            "independent (backward-compatible, bit-identical).&lt;/p&gt;"
            "&lt;p&gt;Provenance: a 3-source form (see &lt;code&gt;mu_eff_lo&lt;/code&gt;/&lt;code&gt;mu_eff_F0_ref&lt;/code&gt;/"
            "&lt;code&gt;gross_ceiling_decay&lt;/code&gt;). BINARY switch, NEVER fittable (no gradient signal "
            "between &amp;quot;on&amp;quot; and &amp;quot;more on&amp;quot; &amp;minus; same idiom as "
            "&lt;code&gt;kj_mode&lt;/code&gt;/&lt;code&gt;flank_wear_on&lt;/code&gt;). Default-inert capability, tested (11 "
            "tests, &lt;code&gt;tests/test_l3_famp_coupling.py&lt;/code&gt;: formula, bit-identity, code-path "
            "guard, physical effect), NOT calibrated per-rig &amp;minus; no behavioral adoption made "
            "yet.&lt;/p&gt;"),
        refs=[("&amp;sect;7.2 step_cycle &amp;minus; acoplamento F_amp&amp;harr;&amp;delta; em disp-mode (roadmap #4)",
               "&amp;sect;7.2 step_cycle &amp;minus; F_amp&amp;harr;&amp;delta; coupling in disp-mode (roadmap #4)",
               "MODEL_MATH_REFERENCE.md"),
              ("Murai/IJAMT-2023 &amp;minus; &amp;mu;_eff medido caindo 0,46&amp;rarr;0,24 com F0 crescente",
               "Murai/IJAMT-2023 &amp;minus; measured &amp;mu;_eff falling 0.46&amp;rarr;0.24 with rising F0",
               "murai2023"),
              ("Measurement-2021 &amp;minus; limiares de slip proporcionais a F0 (Fa, Fb)",
               "Measurement-2021 &amp;minus; slip thresholds proportional to F0 (Fa, Fb)",
               "measurement2021"),
              ("JMP/Li&amp;amp;Hao-2021 &amp;minus; gross-slip F_S&amp;rarr;F_R residual 70-86% do pico",
               "JMP/Li&amp;amp;Hao-2021 &amp;minus; gross-slip F_S&amp;rarr;F_R residual 70-86% of peak",
               "jmp2021")]),

    VarSpec(
        name="mu_eff_lo", symbol="mu_lo", unit="-", group="slip_regime", category="form",
        context={"baseline": "transverse",
                 "overrides": {"famp_couple_on": 1.0, "mu_eff_F0_ref": 50000.0}},
        sweep=(0.0, 1.0, 15, "lin"), related=["famp_couple_on", "mu_eff_F0_ref"],
        negligible=True,
        equation="mu_eff *= mu_eff_lo + (1-mu_eff_lo)*min(1, F_0/mu_eff_F0_ref)   (so' se mu_eff_lo>0 E mu_eff_F0_ref>0)",
        physics_pt=(
            "&lt;p&gt;Knockdown do &amp;mu; efetivo do teto de Coulomb quando F0 cai (F0&amp;rarr;0): "
            "&lt;code&gt;mu_eff_lo&lt;/code&gt; é o PISO da interpolação (fração de &amp;mu;_bearing retida no "
            "limite F0=0); &lt;code&gt;mu_eff_lo&lt;/code&gt;=1 = sem knockdown algum (&amp;mu;_eff=&amp;mu;_bearing "
            "sempre, idêntico ao guard desligado); &lt;code&gt;mu_eff_lo&lt;/code&gt;=0 = knockdown TOTAL "
            "possível (&amp;mu;_eff&amp;rarr;0 quando F0&amp;rarr;0). Só é lido quando "
            "&lt;code&gt;mu_eff_F0_ref&lt;/code&gt; TAMBÉM é &amp;gt;0 (pré-ligado aqui via overrides, junto com "
            "&lt;code&gt;famp_couple_on&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: Murai/IJAMT-2023 mede &amp;mu;_eff caindo experimentalmente de "
            "0,46&amp;rarr;0,24 conforme F0 sobe (o oposto do que o FE previa, &amp;mu;=const).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Achado desta revisão, verificado no engine (não só na fórmula):&lt;/b&gt; neste "
            "baseline (&amp;mu;_bearing=0,15 default), o teto de Coulomb SEM knockdown "
            "(&lt;code&gt;mu_eff_lo&lt;/code&gt;=1) já fica abaixo do limiar T_loose&amp;gt;T_resist que dispara "
            "o afrouxamento rotacional &amp;minus; logo, assim que &lt;code&gt;famp_couple_on&lt;/code&gt; liga, o "
            "mecanismo já fica inerte, e &lt;code&gt;mu_eff_lo&lt;/code&gt; (que só pode reduzir o teto AINDA "
            "MAIS) não move a curva NESTE baseline. Não é falha da forma &amp;minus; é sinal de que a "
            "calibração per-rig (&amp;mu;_bearing mais alto, ou outro F0) ainda não foi feita (ver o "
            "relatório final: &amp;quot;L3 &amp;hellip; não calibrada per-rig&amp;quot;). Marcado sem efeito "
            "visível aqui; a forma é testada isoladamente em "
            "&lt;code&gt;tests/test_l3_famp_coupling.py&lt;/code&gt;.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Knockdown of the effective &amp;mu; of the Coulomb ceiling as F0 falls (F0&amp;rarr;0): "
            "&lt;code&gt;mu_eff_lo&lt;/code&gt; is the FLOOR of the interpolation (fraction of &amp;mu;_bearing "
            "retained at the F0=0 limit); &lt;code&gt;mu_eff_lo&lt;/code&gt;=1 = no knockdown at all "
            "(&amp;mu;_eff=&amp;mu;_bearing always, identical to the guard being off); "
            "&lt;code&gt;mu_eff_lo&lt;/code&gt;=0 = full possible knockdown (&amp;mu;_eff&amp;rarr;0 as F0&amp;rarr;0). "
            "Only read when &lt;code&gt;mu_eff_F0_ref&lt;/code&gt; is ALSO &amp;gt;0 (pre-enabled here via "
            "overrides, together with &lt;code&gt;famp_couple_on&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Provenance: Murai/IJAMT-2023 measures &amp;mu;_eff experimentally falling from "
            "0.46&amp;rarr;0.24 as F0 rises (the opposite of what FE predicted, &amp;mu;=const).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Finding from this review, verified in the engine (not just the formula):&lt;/b&gt; "
            "in this baseline (&amp;mu;_bearing=0.15 default), the Coulomb ceiling WITHOUT knockdown "
            "(&lt;code&gt;mu_eff_lo&lt;/code&gt;=1) already sits below the T_loose&amp;gt;T_resist threshold that "
            "triggers rotational loosening &amp;minus; so as soon as &lt;code&gt;famp_couple_on&lt;/code&gt; turns "
            "on, the mechanism is already inert, and &lt;code&gt;mu_eff_lo&lt;/code&gt; (which can only reduce "
            "the ceiling FURTHER) does not move the curve in THIS baseline. It is not a failure of "
            "the form &amp;minus; it is a sign that the per-rig calibration (higher &amp;mu;_bearing, or a "
            "different F0) has not been done yet (see the final report: &amp;quot;L3 &amp;hellip; not "
            "calibrated per-rig&amp;quot;). Marked with no visible effect here; the form is tested in "
            "isolation in &lt;code&gt;tests/test_l3_famp_coupling.py&lt;/code&gt;.&lt;/p&gt;"),
        refs=[("&amp;sect;7.2 step_cycle &amp;minus; knockdown de &amp;mu;_eff em F0 baixo",
               "&amp;sect;7.2 step_cycle &amp;minus; &amp;mu;_eff knockdown at low F0",
               "MODEL_MATH_REFERENCE.md"),
              ("Murai/IJAMT-2023 &amp;minus; &amp;mu;_eff medido 0,46&amp;rarr;0,24 com F0",
               "Murai/IJAMT-2023 &amp;minus; measured &amp;mu;_eff 0.46&amp;rarr;0.24 with F0",
               "murai2023")]),

    VarSpec(
        name="mu_eff_F0_ref", symbol="F0_ref,mu", unit="N", group="slip_regime", category="form",
        context={"baseline": "transverse",
                 "overrides": {"famp_couple_on": 1.0, "mu_eff_lo": 0.3}},
        sweep=(1e4, 2e5, 15, "log"), related=["mu_eff_lo", "famp_couple_on"],
        negligible=True,
        equation="k = min(1, F_0/mu_eff_F0_ref);  mu_eff *= mu_eff_lo + (1-mu_eff_lo)*k   (so' se mu_eff_lo>0 E mu_eff_F0_ref>0)",
        physics_pt=(
            "&lt;p&gt;F0 de referência do knockdown de &amp;mu;_eff: a pré-carga acima da qual o "
            "knockdown desliga (k satura em 1 &amp;rArr; &amp;mu;_eff=&amp;mu;_bearing cheio); abaixo dela, "
            "&amp;mu;_eff interpola linearmente até o piso &lt;code&gt;mu_eff_lo&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: Measurement-2021 mede dois limiares de slip proporcionais à "
            "pré-carga (Fa=0,199&amp;middot;F0&amp;minus;5,3 kN, slip local; Fb=0,347&amp;middot;F0&amp;minus;5,9 kN, "
            "slip completo) &amp;minus; os limiares de slip-onset escalam com F0, motivando uma "
            "referência de F0 explícita em vez de um &amp;mu; constante.&lt;/p&gt;"
            "&lt;p&gt;Mesmo &lt;b&gt;achado&lt;/b&gt; desta revisão que &lt;code&gt;mu_eff_lo&lt;/code&gt;: neste baseline "
            "(&amp;mu;_bearing=0,15 default), o teto de Coulomb já fica abaixo do limiar de "
            "engajamento do afrouxamento rotacional mesmo no extremo &amp;quot;sem knockdown&amp;quot; "
            "(k=1) &amp;minus; variar ONDE o knockdown liga/desliga não muda uma curva que já está "
            "clampada abaixo do limiar. Estrutural, não um bug (ver a nota de "
            "&lt;code&gt;mu_eff_lo&lt;/code&gt;). Marcado sem efeito visível aqui; forma testada "
            "isoladamente em &lt;code&gt;tests/test_l3_famp_coupling.py&lt;/code&gt;.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Reference F0 of the &amp;mu;_eff knockdown: the preload above which the knockdown "
            "turns off (k saturates at 1 &amp;rArr; &amp;mu;_eff=&amp;mu;_bearing in full); below it, &amp;mu;_eff "
            "interpolates linearly down to the floor &lt;code&gt;mu_eff_lo&lt;/code&gt;.&lt;/p&gt;"
            "&lt;p&gt;Provenance: Measurement-2021 measures two slip thresholds proportional to "
            "preload (Fa=0.199&amp;middot;F0&amp;minus;5.3 kN, local slip; Fb=0.347&amp;middot;F0&amp;minus;5.9 kN, "
            "full slip) &amp;minus; slip-onset thresholds scale with F0, motivating an explicit F0 "
            "reference instead of a constant &amp;mu;.&lt;/p&gt;"
            "&lt;p&gt;Same &lt;b&gt;finding&lt;/b&gt; from this review as &lt;code&gt;mu_eff_lo&lt;/code&gt;: in this baseline "
            "(&amp;mu;_bearing=0.15 default), the Coulomb ceiling already sits below the rotational-"
            "loosening engagement threshold even at the &amp;quot;no knockdown&amp;quot; extreme (k=1) "
            "&amp;minus; varying WHERE the knockdown turns on/off does not change a curve that is "
            "already clamped below threshold. Structural, not a bug (see the &lt;code&gt;mu_eff_lo&lt;/code&gt; "
            "note). Marked with no visible effect here; the form is tested in isolation in "
            "&lt;code&gt;tests/test_l3_famp_coupling.py&lt;/code&gt;.&lt;/p&gt;"),
        refs=[("&amp;sect;7.2 step_cycle &amp;minus; F0 de referência do knockdown de &amp;mu;_eff",
               "&amp;sect;7.2 step_cycle &amp;minus; reference F0 of the &amp;mu;_eff knockdown",
               "MODEL_MATH_REFERENCE.md"),
              ("Measurement-2021 &amp;minus; limiares de slip Fa/Fb proporcionais a F0",
               "Measurement-2021 &amp;minus; slip thresholds Fa/Fb proportional to F0",
               "measurement2021")]),

    VarSpec(
        name="gross_ceiling_decay", symbol="k_gcd", unit="-", group="slip_regime", category="form",
        context={"baseline": "transverse",
                 "overrides": {"famp_couple_on": 1.0, "c_D": 2.0}},
        sweep=(0.0, 2.0, 15, "lin"), related=["famp_couple_on", "c_D"],
        negligible=True,
        equation="ceiling *= max(0, 1 - gross_ceiling_decay*D)   (so' se gross_ceiling_decay>0; D cresce via c_D)",
        physics_pt=(
            "&lt;p&gt;Decaimento do teto de gross-slip com o desgaste superficial acumulado "
            "(&lt;code&gt;state.D&lt;/code&gt;): conforme a superfície se degrada, o teto de Coulomb fica "
            "ainda MENOR (achatamento/desgaste reduzem a força de gross-slip disponível).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: JMP/Li&amp;amp;Hao-2021 mede a força de gross-slip caindo do pico F_S "
            "para um residual F_R = 70&amp;ndash;86% do pico conforme a interface se desgasta "
            "(backbone Iwan de 5 parâmetros) &amp;minus; um decaimento direto e monotônico com o dano, "
            "complementar ao knockdown por F0 (&lt;code&gt;mu_eff_lo&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Mesmo &lt;b&gt;achado estrutural&lt;/b&gt; desta revisão: o teto já fica abaixo do limiar "
            "de engajamento do afrouxamento assim que &lt;code&gt;famp_couple_on&lt;/code&gt; liga "
            "(&amp;mu;_bearing default); decair ainda MAIS um teto que já é sub-limiar não move a "
            "curva. Aqui &lt;code&gt;c_D&lt;/code&gt;=2,0 (mesmo &amp;quot;starter&amp;quot; físico do perfil de dano) "
            "ativa o crescimento de D só para exercitar o caminho de código &amp;minus; sem efeito "
            "visível por essa razão estrutural. &lt;b&gt;Nota de sobreposição&lt;/b&gt; (ledger da fatia "
            "L3): se &lt;code&gt;gross_ceiling_decay&lt;/code&gt; E &lt;code&gt;k_dmg_mu&lt;/code&gt; estiverem ligados "
            "simultaneamente, o dano afeta o teto por DOIS caminhos independentes (via &amp;mu;_eff E "
            "via decaimento direto) &amp;minus; não é um bug, mas é uma sobreposição a documentar antes "
            "de adotar os dois juntos.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Decay of the gross-slip ceiling with accumulated surface damage "
            "(&lt;code&gt;state.D&lt;/code&gt;): as the surface degrades, the Coulomb ceiling gets even "
            "SMALLER (flattening/wear reduce the available gross-slip force).&lt;/p&gt;"
            "&lt;p&gt;Provenance: JMP/Li&amp;amp;Hao-2021 measures the gross-slip force falling from the "
            "peak F_S to a residual F_R = 70&amp;ndash;86% of the peak as the interface wears "
            "(5-parameter Iwan backbone) &amp;minus; a direct, monotonic decay with damage, "
            "complementary to the F0 knockdown (&lt;code&gt;mu_eff_lo&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Same &lt;b&gt;structural finding&lt;/b&gt; from this review: the ceiling already sits "
            "below the loosening engagement threshold as soon as &lt;code&gt;famp_couple_on&lt;/code&gt; turns "
            "on (default &amp;mu;_bearing); decaying an already sub-threshold ceiling even further "
            "does not move the curve. Here &lt;code&gt;c_D&lt;/code&gt;=2.0 (the same physical damage-profile "
            "starter) turns on D's growth just to exercise the code path &amp;minus; no visible effect "
            "for this structural reason. &lt;b&gt;Overlap note&lt;/b&gt; (L3 slice ledger): if "
            "&lt;code&gt;gross_ceiling_decay&lt;/code&gt; AND &lt;code&gt;k_dmg_mu&lt;/code&gt; are both on at once, damage "
            "affects the ceiling through TWO independent paths (via &amp;mu;_eff AND via direct decay) "
            "&amp;minus; not a bug, but an overlap to document before adopting both together.&lt;/p&gt;"),
        refs=[("&amp;sect;7.2 step_cycle &amp;minus; decaimento do teto de gross-slip com o dano",
               "&amp;sect;7.2 step_cycle &amp;minus; gross-slip ceiling decay with damage",
               "MODEL_MATH_REFERENCE.md"),
              ("JMP/Li&amp;amp;Hao-2021 &amp;minus; F_S&amp;rarr;F_R residual 70-86% do pico, backbone Iwan",
               "JMP/Li&amp;amp;Hao-2021 &amp;minus; F_S&amp;rarr;F_R residual 70-86% of peak, Iwan backbone",
               "jmp2021")]),

    VarSpec(
        name="flank_wear_on", symbol="", unit="", group="axial_fretting", category="mode",
        context={"baseline": "axial", "overrides": {"k_wear_flank": 8.34e-15}},
        choices=[0.0, 1.0], related=["k_wear_flank", "flank_amp_exp", "k_thread_fret"],
        negligible=True,
        equation="flank_wear_on>0 E F_ax>1e-6 E delta_amp is None: liga o canal L1 (flank_wear_axial_term) dentro de ThreadFrettingLoss",
        physics_pt=(
            "&lt;p&gt;Liga o segundo canal, INDEPENDENTE, de desgaste de flanco de rosca &amp;prop; "
            "amplitude de carga axial A_F (complementar ao &lt;code&gt;k_thread_fret&lt;/code&gt; legado, "
            "hardcoded linear em F_ax). Mesma interface física (flanco de rosca), forma diferente: "
            "parametrizada por PRESSÃO de flanco p_flank=F_0/A_s (não força) com um expoente de "
            "amplitude ajustável (&lt;code&gt;flank_amp_exp&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Limitação estrutural deste explorador&lt;/b&gt; (achado da revisão, verificado no "
            "código, não uma suposição): o guard do canal L1 exige &lt;code&gt;delta_amp is None&lt;/code&gt; "
            "(modo força puro); mas o harness deste explorador "
            "(&lt;code&gt;calibration.server.handle_simulate&lt;/code&gt;) SEMPRE converte "
            "&lt;code&gt;delta_amp&lt;/code&gt; para float antes de chamar &lt;code&gt;step_cycle&lt;/code&gt; &amp;minus; nunca "
            "passa &lt;code&gt;None&lt;/code&gt;, mesmo no baseline &amp;quot;axial&amp;quot; (que usa "
            "&lt;code&gt;delta_amp=0.0&lt;/code&gt;, um FLOAT, não &lt;code&gt;None&lt;/code&gt;). Logo este canal NUNCA "
            "pode ser demonstrado por este explorador, em NENHUM baseline &amp;minus; é uma limitação "
            "do harness de simulação interativa, não do mecanismo (que É exercitado de verdade em "
            "&lt;code&gt;tests/test_l1_flank_wear_axial.py&lt;/code&gt;, chamando &lt;code&gt;step_cycle&lt;/code&gt; "
            "diretamente com &lt;code&gt;delta_amp=None&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: forma Zhang 2019 (EFA, k_wear_spec rosca 35CrMo/SCM435=8,34e-15 "
            "1/Pa) + escala super-linear candidata do Liu 2020 (expoente 1,5&amp;ndash;1,6). &lt;b&gt;GATE B1&lt;/b&gt; "
            "(falsificação-alvo, MODEL_LEGITIMACY §4.6): re-executado 2x (2026-07-17), FALHOU as "
            "duas vezes (slope Liu2017 ficou &amp;asymp;8&amp;times; raso demais mesmo com o expoente livre "
            "ou fixo em 1,5) &amp;minus; capacidade validada e testada, mas NÃO adotada; permanece "
            "como pesquisa aberta (forma ainda mais íngreme em A_F é necessária).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Turns on the second, INDEPENDENT channel of thread-flank wear &amp;prop; axial load "
            "amplitude A_F (complementary to the legacy &lt;code&gt;k_thread_fret&lt;/code&gt;, hardcoded "
            "linear in F_ax). Same physical interface (thread flank), different form: "
            "parametrized by flank PRESSURE p_flank=F_0/A_s (not force) with an adjustable "
            "amplitude exponent (&lt;code&gt;flank_amp_exp&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Structural limitation of this explorer&lt;/b&gt; (a finding from this review, "
            "verified in code, not an assumption): the L1 channel's guard requires "
            "&lt;code&gt;delta_amp is None&lt;/code&gt; (pure force mode); but this explorer's harness "
            "(&lt;code&gt;calibration.server.handle_simulate&lt;/code&gt;) ALWAYS converts "
            "&lt;code&gt;delta_amp&lt;/code&gt; to a float before calling &lt;code&gt;step_cycle&lt;/code&gt; &amp;minus; it never "
            "passes &lt;code&gt;None&lt;/code&gt;, even in the &amp;quot;axial&amp;quot; baseline (which uses "
            "&lt;code&gt;delta_amp=0.0&lt;/code&gt;, a FLOAT, not &lt;code&gt;None&lt;/code&gt;). So this channel can NEVER be "
            "demonstrated by this explorer, in ANY baseline &amp;minus; it is a limitation of the "
            "interactive simulation harness, not of the mechanism (which IS genuinely exercised in "
            "&lt;code&gt;tests/test_l1_flank_wear_axial.py&lt;/code&gt;, calling &lt;code&gt;step_cycle&lt;/code&gt; directly "
            "with &lt;code&gt;delta_amp=None&lt;/code&gt;).&lt;/p&gt;"
            "&lt;p&gt;Provenance: Zhang 2019 form (EFA, thread k_wear_spec 35CrMo/SCM435=8.34e-15 "
            "1/Pa) + Liu 2020's candidate super-linear scale (exponent 1.5&amp;ndash;1.6). &lt;b&gt;GATE B1&lt;/b&gt; "
            "(target falsification, MODEL_LEGITIMACY §4.6): re-run 2x (2026-07-17), FAILED both "
            "times (the Liu2017 slope came out &amp;asymp;8&amp;times; too shallow even with the exponent "
            "free or fixed at 1.5) &amp;minus; validated and tested capability, but NOT adopted; it "
            "remains open research (a steeper form in A_F is needed).&lt;/p&gt;"),
        refs=[("&amp;sect;4.5 ThreadFrettingLoss &amp;minus; canal L1 independente ~ A_F",
               "&amp;sect;4.5 ThreadFrettingLoss &amp;minus; independent L1 channel ~ A_F",
               "MODEL_MATH_REFERENCE.md"),
              ("Gate B1 FAIL2 (2026-07-17) &amp;minus; slope ~8x raso demais, falsificação documentada",
               "Gate B1 FAIL2 (2026-07-17) &amp;minus; slope ~8x too shallow, documented falsification",
               "l1l7_final_report.md"),
              ("Zhang 2019 EFA &amp;minus; k_wear_spec rosca 35CrMo/SCM435",
               "Zhang 2019 EFA &amp;minus; thread k_wear_spec 35CrMo/SCM435",
               "zhang2019"),
              ("Liu 2020 Wear &amp;minus; escala super-linear candidata (expoente 1,5-1,6)",
               "Liu 2020 Wear &amp;minus; candidate super-linear scale (exponent 1.5-1.6)",
               "liu2020")]),

    VarSpec(
        name="k_wear_flank", symbol="k_wf", unit="1/Pa", group="axial_fretting", category="form",
        context={"baseline": "axial", "overrides": {"flank_wear_on": 1.0}},
        sweep=(1e-15, 1e-13, 15, "log"), related=["flank_wear_on", "flank_amp_exp"],
        negligible=True,
        equation="d_w = k_wear_flank * p_flank * slip_dist^flank_amp_exp,  p_flank=F_0/A_s,  slip_dist=2*F_ax/k_b",
        physics_pt=(
            "&lt;p&gt;Razão de wear específica do flanco de rosca [1/Pa] &amp;minus; a MAGNITUDE do canal "
            "L1 (a FORMA/expoente vive em &lt;code&gt;flank_amp_exp&lt;/code&gt;). Maior "
            "&lt;code&gt;k_wear_flank&lt;/code&gt; = mais profundidade de desgaste por unidade de "
            "pressão&amp;middot;deslocamento&amp;#8319;.&lt;/p&gt;"
            "&lt;p&gt;Mesma limitação estrutural do harness descrita em &lt;code&gt;flank_wear_on&lt;/code&gt;: o "
            "guard &lt;code&gt;delta_amp is None&lt;/code&gt; nunca é satisfeito por este explorador (que "
            "sempre passa um float), então este slider é INERTE em qualquer página deste site "
            "&amp;minus; não porque a magnitude seja pequena, mas porque o canal inteiro nunca é sequer "
            "chamado aqui.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: semeado do &lt;code&gt;knowledge_base&lt;/code&gt; "
            "(&lt;code&gt;kb.wear_spec_anchor(&amp;quot;thread&amp;quot;,&amp;quot;35CrMo-SCM435&amp;quot;)&lt;/code&gt;=8,34e-15, "
            "Zhang 2019 EFA doi 10.1016/j.engfailanal.2019.05.001) &amp;minus; a leitura do KB acontece "
            "na CALIBRAÇÃO (gate B1), nunca no engine (que só recebe a constante). Fitado per-rig "
            "no gate B1 (tentativa 1: satura no limite inferior da busca; tentativa 2, expoente "
            "fixo 1,5: 1,676e-14 rig A / 1,890e-13 rig B) mas o gate de forma (slope) FALHOU "
            "(FAIL2) &amp;minus; capacidade validada, não adotada.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Thread-flank specific wear ratio [1/Pa] &amp;minus; the MAGNITUDE of the L1 channel "
            "(the FORM/exponent lives in &lt;code&gt;flank_amp_exp&lt;/code&gt;). A larger "
            "&lt;code&gt;k_wear_flank&lt;/code&gt; means more wear depth per unit of "
            "pressure&amp;middot;displacement&amp;#8319;.&lt;/p&gt;"
            "&lt;p&gt;Same harness structural limitation described under &lt;code&gt;flank_wear_on&lt;/code&gt;: the "
            "&lt;code&gt;delta_amp is None&lt;/code&gt; guard is never satisfied by this explorer (which "
            "always passes a float), so this slider is INERT on any page of this site &amp;minus; not "
            "because the magnitude is small, but because the whole channel is never even called "
            "here.&lt;/p&gt;"
            "&lt;p&gt;Provenance: seeded from the &lt;code&gt;knowledge_base&lt;/code&gt; "
            "(&lt;code&gt;kb.wear_spec_anchor(&amp;quot;thread&amp;quot;,&amp;quot;35CrMo-SCM435&amp;quot;)&lt;/code&gt;=8.34e-15, "
            "Zhang 2019 EFA doi 10.1016/j.engfailanal.2019.05.001) &amp;minus; the KB read happens at "
            "CALIBRATION time (gate B1), never in the engine (which only receives the constant). "
            "Fitted per-rig in gate B1 (attempt 1: saturates at the search's lower bound; attempt "
            "2, exponent fixed at 1.5: 1.676e-14 rig A / 1.890e-13 rig B) but the form (slope) gate "
            "FAILED (FAIL2) &amp;minus; validated capability, not adopted.&lt;/p&gt;"),
        refs=[("&amp;sect;6 razão de wear específica do flanco (âncora Zhang 2019)",
               "&amp;sect;6 thread-flank specific wear ratio (Zhang 2019 anchor)",
               "MODEL_MATH_REFERENCE.md"),
              ("Gate B1 FAIL2 &amp;minus; k_wear_flank fitado per-rig, slope ainda ~8x raso",
               "Gate B1 FAIL2 &amp;minus; k_wear_flank fitted per-rig, slope still ~8x shallow",
               "l1l7_final_report.md"),
              ("Zhang 2019 EFA &amp;minus; k_wear_spec(rosca, 35CrMo-SCM435)=8,34e-15 1/Pa",
               "Zhang 2019 EFA &amp;minus; k_wear_spec(thread, 35CrMo-SCM435)=8.34e-15 1/Pa",
               "zhang2019")]),

    VarSpec(
        name="flank_amp_exp", symbol="n_flank", unit="-", group="axial_fretting", category="form",
        context={"baseline": "axial",
                 "overrides": {"flank_wear_on": 1.0, "k_wear_flank": 8.34e-15}},
        sweep=(0.5, 3.0, 15, "lin"), related=["k_wear_flank", "flank_wear_on"],
        negligible=True,
        equation="d_w = k_wear_flank * p_flank * slip_dist^flank_amp_exp   (1.0=linear, backward-compat da FORMA)",
        physics_pt=(
            "&lt;p&gt;Expoente de amplitude do desgaste de flanco &amp;minus; 1,0 (default) = linear no "
            "deslocamento de flanco; &amp;gt;1 = super-linear (mais sensível ao aumento de "
            "amplitude).&lt;/p&gt;"
            "&lt;p&gt;Mesma limitação estrutural do harness (&lt;code&gt;delta_amp&lt;/code&gt; nunca é "
            "&lt;code&gt;None&lt;/code&gt; neste explorador) &amp;minus; slider estruturalmente inerte AQUI, "
            "embora testado e fitado de verdade fora deste site "
            "(&lt;code&gt;test_flank_amp_exp_is_super_linear_when_above_one&lt;/code&gt; em "
            "&lt;code&gt;tests/test_l1_flank_wear_axial.py&lt;/code&gt; prova a super-linearidade num único "
            "ciclo, isolando a fórmula da dinâmica multi-ciclo).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: Liu 2020 (Wear) mede a escala experimental "
            "d(afrouxamento)/d(amplitude) super-linear &amp;minus; 1,2%&amp;rarr;16,9% para 0,1&amp;rarr;0,4 mm, "
            "expoente log-log 1,5&amp;ndash;1,6 (subindo a &amp;asymp;3,2 na mudança de regime). O gate B1 "
            "testou exatamente esse candidato (&lt;code&gt;flank_amp_exp&lt;/code&gt;=1,5 fixo) e FALHOU "
            "(slope ainda &amp;asymp;8&amp;times; raso demais) &amp;minus; mesmo o expoente super-linear da "
            "literatura não basta; o mecanismo real precisa de uma forma ainda mais íngreme em "
            "A_F.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Amplitude exponent of the flank wear &amp;minus; 1.0 (default) = linear in the flank "
            "displacement; &amp;gt;1 = super-linear (more sensitive to rising amplitude).&lt;/p&gt;"
            "&lt;p&gt;Same harness structural limitation (&lt;code&gt;delta_amp&lt;/code&gt; is never "
            "&lt;code&gt;None&lt;/code&gt; in this explorer) &amp;minus; the slider is structurally inert HERE, "
            "although it is genuinely tested and fitted outside this site "
            "(&lt;code&gt;test_flank_amp_exp_is_super_linear_when_above_one&lt;/code&gt; in "
            "&lt;code&gt;tests/test_l1_flank_wear_axial.py&lt;/code&gt; proves the super-linearity in a "
            "single cycle, isolating the formula from multi-cycle dynamics).&lt;/p&gt;"
            "&lt;p&gt;Provenance: Liu 2020 (Wear) measures the experimental scale "
            "d(loosening)/d(amplitude) as super-linear &amp;minus; 1.2%&amp;rarr;16.9% for 0.1&amp;rarr;0.4 mm, "
            "log-log exponent 1.5&amp;ndash;1.6 (rising to &amp;asymp;3.2 at the regime change). Gate B1 "
            "tested exactly this candidate (&lt;code&gt;flank_amp_exp&lt;/code&gt;=1.5 fixed) and FAILED "
            "(slope still &amp;asymp;8&amp;times; too shallow) &amp;minus; even the literature's super-linear "
            "exponent is not enough; the real mechanism needs a still steeper form in A_F.&lt;/p&gt;"),
        refs=[("&amp;sect;4.5 ThreadFrettingLoss &amp;minus; expoente de amplitude do canal L1",
               "&amp;sect;4.5 ThreadFrettingLoss &amp;minus; L1 channel amplitude exponent",
               "MODEL_MATH_REFERENCE.md"),
              ("Liu 2020 Wear &amp;minus; expoente log-log 1,5-1,6 (super-linear)",
               "Liu 2020 Wear &amp;minus; log-log exponent 1.5-1.6 (super-linear)",
               "liu2020")]),

    VarSpec(
        name="kj_mode", symbol="", unit="", group="stiffness", category="mode",
        context={"baseline": "transverse", "overrides": {}},
        choices=["", "pedersen", "wileman"], related=["k_j_init", "phi_load_dep"],
        negligible=True,
        equation='kj_mode in ("pedersen","wileman") E geometria fornece d_hole>0 E d_washer>0: k_j_init <- kj_from_geometry(...) 1x no __init__;  senao cai silenciosamente no k_j_init atual',
        physics_pt=(
            "&lt;p&gt;Lei k_j(geometria, material) &amp;minus; substitui a constante fixa "
            "&lt;code&gt;k_j_init&lt;/code&gt; pela rigidez de contato FÍSICA calculada da geometria real "
            "(diâmetro/grip/furo/arruela). &lt;b&gt;&amp;quot;&amp;quot;&lt;/b&gt; (default): comportamento atual, "
            "&lt;code&gt;k_j_init&lt;/code&gt; como dado/fitado. &lt;b&gt;&amp;quot;pedersen&amp;quot;&lt;/b&gt;: Pedersen 2008 "
            "Eq.31 (assíntota + transição de largura finita), a forma primária. "
            "&lt;b&gt;&amp;quot;wileman&amp;quot;&lt;/b&gt;: Wileman 1991 (A,B por material), cross-check.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Limitação estrutural deste explorador&lt;/b&gt; (achado da revisão): a lei só "
            "engata se a geometria do run fornecer &lt;code&gt;d_hole&lt;/code&gt;/&lt;code&gt;d_washer&lt;/code&gt; "
            "(&amp;gt;0); mas o payload deste explorador "
            "(&lt;code&gt;calibration.server._geom&lt;/code&gt;) só extrai os 6 campos de "
            "&lt;code&gt;_GEOM_KEYS&lt;/code&gt; (A_s, L_eff, d_2, pitch, r_bearing, A_contact) &amp;minus; "
            "&lt;code&gt;d_hole&lt;/code&gt;/&lt;code&gt;d_washer&lt;/code&gt; NUNCA são lidos daqui, então caem sempre "
            "no default 0,0 (&lt;code&gt;JointGeometry&lt;/code&gt;), e o modo cai SEMPRE no fallback "
            "silencioso (&lt;code&gt;k_j_init&lt;/code&gt; inalterado), qualquer que seja o valor de "
            "&lt;code&gt;kj_mode&lt;/code&gt;. Isto reflete honestamente o próprio código-fonte (&amp;quot;nenhuma "
            "geometria existente na biblioteca os preenche hoje&amp;quot;), não é um bug deste "
            "explorador especificamente.&lt;/p&gt;"
            "&lt;p&gt;Proveniência: Pedersen 2008 é a forma mais próxima da verdade (+24% de erro, "
            "ranking Rousseau 2024); Wileman 1991 superestima (+45&amp;ndash;59%). &lt;b&gt;GATE D5&lt;/b&gt; "
            "(Rousseau steel/HDPE t10/12/14 + Zhang2006, 8 casos): resultado &lt;b&gt;PASS-inert&lt;/b&gt; "
            "&amp;minus; &amp;Delta;MAE = 0,0 EXATO em todos os 8 (&lt;code&gt;k_j_init&lt;/code&gt; muda de fato, "
            "4,0e9&amp;rarr;2,90&amp;ndash;3,35e9 N/m, e &amp;Phi;_eff_0 muda +0,02 a +0,03 &amp;minus; a lei "
            "ENGATA de verdade, não é um no-op disfarçado &amp;minus; mas o PACK adotado usa "
            "&amp;theta;=&amp;pi;/2 exato + &lt;code&gt;k_tr_mode=&amp;quot;bending&amp;quot;&lt;/code&gt;, que faz o termo axial "
            "de &lt;code&gt;RotationalLooseningLoss&lt;/code&gt; cair abaixo da precisão double, blindando a "
            "trajetória). Seguro adotar como proveniência (substituição sem risco numérico nos 8 "
            "casos-gate), mas NÃO fecha sozinho a falsificação de escala-com-espessura "
            "(&lt;code&gt;JointGeometry.E&lt;/code&gt; é um único campo usado tanto pelo parafuso quanto "
            "pelo membro &amp;minus; não captura o contraste HDPE-vs-aço &amp;asymp;100&amp;times; em E que "
            "motivou a série Rousseau).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;k_j(geometry, material) law &amp;minus; replaces the fixed &lt;code&gt;k_j_init&lt;/code&gt; "
            "constant with the PHYSICAL contact stiffness computed from the real geometry "
            "(diameter/grip/hole/washer). &lt;b&gt;&amp;quot;&amp;quot;&lt;/b&gt; (default): current behavior, "
            "&lt;code&gt;k_j_init&lt;/code&gt; as given/fitted. &lt;b&gt;&amp;quot;pedersen&amp;quot;&lt;/b&gt;: Pedersen 2008 "
            "Eq.31 (asymptote + finite-width transition), the primary form. "
            "&lt;b&gt;&amp;quot;wileman&amp;quot;&lt;/b&gt;: Wileman 1991 (per-material A,B), cross-check.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Structural limitation of this explorer&lt;/b&gt; (a finding from this review): the "
            "law only engages if the run's geometry supplies &lt;code&gt;d_hole&lt;/code&gt;/&lt;code&gt;d_washer&lt;/code&gt; "
            "(&amp;gt;0); but this explorer's payload (&lt;code&gt;calibration.server._geom&lt;/code&gt;) only "
            "extracts the 6 &lt;code&gt;_GEOM_KEYS&lt;/code&gt; fields (A_s, L_eff, d_2, pitch, r_bearing, "
            "A_contact) &amp;minus; &lt;code&gt;d_hole&lt;/code&gt;/&lt;code&gt;d_washer&lt;/code&gt; are NEVER read from here, so "
            "they always fall to the 0.0 &lt;code&gt;JointGeometry&lt;/code&gt; default, and the mode ALWAYS "
            "falls to the silent fallback (&lt;code&gt;k_j_init&lt;/code&gt; unchanged), whatever "
            "&lt;code&gt;kj_mode&lt;/code&gt; is set to. This honestly reflects the source code itself (&amp;quot;no "
            "existing geometry in the library fills them in today&amp;quot;), it is not a bug specific "
            "to this explorer.&lt;/p&gt;"
            "&lt;p&gt;Provenance: Pedersen 2008 is the form closest to the truth (+24% error, Rousseau "
            "2024 ranking); Wileman 1991 overestimates (+45&amp;ndash;59%). &lt;b&gt;GATE D5&lt;/b&gt; (Rousseau "
            "steel/HDPE t10/12/14 + Zhang2006, 8 cases): result &lt;b&gt;PASS-inert&lt;/b&gt; &amp;minus; "
            "&amp;Delta;MAE = 0.0 EXACT on all 8 (&lt;code&gt;k_j_init&lt;/code&gt; genuinely changes, "
            "4.0e9&amp;rarr;2.90&amp;ndash;3.35e9 N/m, and &amp;Phi;_eff_0 changes +0.02 to +0.03 &amp;minus; the "
            "law does ENGAGE for real, not a disguised no-op &amp;minus; but the adopted PACK uses "
            "&amp;theta;=&amp;pi;/2 exactly + &lt;code&gt;k_tr_mode=&amp;quot;bending&amp;quot;&lt;/code&gt;, which drops "
            "&lt;code&gt;RotationalLooseningLoss&lt;/code&gt;'s axial term below double precision, shielding "
            "the trajectory). Safe to adopt as provenance (a swap with no numerical risk in the 8 "
            "gate cases), but it does NOT close the thickness-scaling falsification by itself "
            "(&lt;code&gt;JointGeometry.E&lt;/code&gt; is a single field used by both the bolt and the "
            "member &amp;minus; it cannot capture the &amp;asymp;100&amp;times; HDPE-vs-steel contrast in E that "
            "motivated the Rousseau series).&lt;/p&gt;"),
        refs=[("&amp;sect;3 constantes k_j &amp;minus; lei k_j(geometria,material) opt-in",
               "&amp;sect;3 k_j constants &amp;minus; opt-in k_j(geometry,material) law",
               "MODEL_MATH_REFERENCE.md"),
              ("Gate D5 &amp;minus; PASS-inert, 8/8 casos, &amp;Delta;MAE=0,0 exato (Rousseau/Zhang2006)",
               "Gate D5 &amp;minus; PASS-inert, 8/8 cases, exact &amp;Delta;MAE=0.0 (Rousseau/Zhang2006)",
               "l1l7_final_report.md"),
              ("Pedersen 2008 Eq.31 &amp;minus; forma mais próxima da verdade (+24%, ranking Rousseau 2024)",
               "Pedersen 2008 Eq.31 &amp;minus; form closest to truth (+24%, Rousseau 2024 ranking)",
               "pedersen2008"),
              ("Wileman 1991 &amp;minus; cross-check por material (superestima +45-59%)",
               "Wileman 1991 &amp;minus; per-material cross-check (overestimates +45-59%)",
               "wileman1991")]),

    VarSpec(
        name="phi_load_dep", symbol="lambda_crit", unit="-", group="stiffness", category="form",
        context={"baseline": "axial", "overrides": {}},
        sweep=(0.2, 3.0, 15, "lin"), related=["kj_mode"],
        negligible=True,
        equation="F_joint/F_i = 1 - sqrt(max(0, 2*lambda - lambda^2)),  lambda = F_ax_ext/(phi_load_dep*F_i)   [lambda clipado em [0,1]]",
        physics_pt=(
            "&lt;p&gt;Dependência de CARGA da partição &amp;Phi; via forma ELÍPTICA de Grosse (1990) "
            "&amp;minus; 1 parâmetro por-junta (a deformação/carga crítica de separação). Substitui a "
            "partição LINEAR padrão (1&amp;minus;&amp;Phi;) do lado do membro/junta por uma curva "
            "elíptica que colapsa perto da carga crítica.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Limitação estrutural, verificada no código&lt;/b&gt; (não uma suposição): "
            "&lt;code&gt;phi_load_dep&lt;/code&gt; só é lido dentro de &lt;code&gt;U_loaded()&lt;/code&gt;, que é exposta "
            "apenas como um MÉTODO DIAGNÓSTICO do analyzer "
            "(&lt;code&gt;DynamicStiffnessAnalyzer.U_loaded(F_ax_ext)&lt;/code&gt;) &amp;minus; nenhum lugar do "
            "laço de simulação (&lt;code&gt;step_cycle&lt;/code&gt;, os 6 mecanismos) CHAMA "
            "&lt;code&gt;U_loaded&lt;/code&gt; internamente. Como este explorador só varre a trajetória de "
            "F_0/ratio (nunca chama &lt;code&gt;.U_loaded()&lt;/code&gt; explicitamente), "
            "&lt;code&gt;phi_load_dep&lt;/code&gt; é estruturalmente inerte em QUALQUER curva deste site "
            "&amp;minus; não porque a forma seja fraca, mas porque a variável ainda não alimenta o "
            "objetivo/fit (mesma leitura do próprio &lt;code&gt;parameter_registry&lt;/code&gt;: "
            "&amp;quot;declarado, ainda não identificável&amp;quot;).&lt;/p&gt;"
            "&lt;p&gt;Proveniência: Grosse 1990 (tese FE não-linear de contato/separação, 171 páginas) "
            "mede a rigidez da junta colapsando &amp;asymp;50&amp;times; da pré-carga plena até a separação "
            "&amp;minus; a forma elíptica F_m/F_i=1&amp;minus;&amp;radic;(2&amp;lambda;&amp;minus;&amp;lambda;&amp;sup2;) é a versão "
            "barata (1 parâmetro) dessa física. Introduzida na mesma fatia (Task 5) que "
            "&lt;code&gt;kj_mode&lt;/code&gt;, como capacidade OPT-IN separada; ainda não entra em nenhum "
            "gate/objetivo de calibração &amp;minus; reavaliar quando (e se) entrar.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Load dependence of the &amp;Phi; partition via Grosse's (1990) ELLIPTICAL form "
            "&amp;minus; 1 per-joint parameter (the critical separation deformation/load). It "
            "replaces the standard LINEAR partition (1&amp;minus;&amp;Phi;) on the member/joint side with "
            "an elliptical curve that collapses near the critical load.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Structural limitation, verified in code&lt;/b&gt; (not an assumption): "
            "&lt;code&gt;phi_load_dep&lt;/code&gt; is only read inside &lt;code&gt;U_loaded()&lt;/code&gt;, which is "
            "exposed only as a DIAGNOSTIC method of the analyzer "
            "(&lt;code&gt;DynamicStiffnessAnalyzer.U_loaded(F_ax_ext)&lt;/code&gt;) &amp;minus; no part of the "
            "simulation loop (&lt;code&gt;step_cycle&lt;/code&gt;, the 6 mechanisms) CALLS &lt;code&gt;U_loaded&lt;/code&gt; "
            "internally. Since this explorer only sweeps the F_0/ratio trajectory (never calls "
            "&lt;code&gt;.U_loaded()&lt;/code&gt; explicitly), &lt;code&gt;phi_load_dep&lt;/code&gt; is structurally inert on "
            "ANY curve on this site &amp;minus; not because the form is weak, but because the variable "
            "does not yet feed the objective/fit (the same reading as the "
            "&lt;code&gt;parameter_registry&lt;/code&gt; itself: &amp;quot;declared, not yet identifiable&amp;quot;).&lt;/p&gt;"
            "&lt;p&gt;Provenance: Grosse 1990 (171-page nonlinear FE contact/separation dissertation) "
            "measures joint stiffness collapsing &amp;asymp;50&amp;times; from full preload to separation "
            "&amp;minus; the elliptical form F_m/F_i=1&amp;minus;&amp;radic;(2&amp;lambda;&amp;minus;&amp;lambda;&amp;sup2;) is the cheap "
            "(1-parameter) version of that physics. Introduced in the same slice (Task 5) as "
            "&lt;code&gt;kj_mode&lt;/code&gt;, as a separate OPT-IN capability; it does not yet enter any "
            "calibration gate/objective &amp;minus; reassess when (and if) it does.&lt;/p&gt;"),
        refs=[("&amp;sect;2 vetor de estado &amp;minus; U_loaded (energia elástica com F_ax_ext), diagnóstico",
               "&amp;sect;2 state vector &amp;minus; U_loaded (elastic energy with F_ax_ext), diagnostic",
               "MODEL_MATH_REFERENCE.md"),
              ("Grosse 1990 &amp;minus; colapso de rigidez ~50x da pré-carga plena a separação",
               "Grosse 1990 &amp;minus; stiffness collapse ~50x from full preload to separation",
               "grosse1990")]),
])

# ====== F3/F4 execução mestre (3) — mu(N) medido, limiar de flanco, rota transversal ======
VARIABLE_SPECS.extend([
    VarSpec(
        name="mu_bearing_schedule", symbol="", unit="", group="friction", category="mode",
        context={"baseline": "transverse", "overrides": {}},
        choices=[], related=["mu_bearing", "k_dmg_mu"],
        negligible=True,
        equation='schedule [(N, mu)] presente: mu_bearing_eff = interp(state.n_cycle) e BYPASSA constante+dano; vazio (default) = caminho antigo bit-idêntico',
        physics_pt=(
            "&lt;p&gt;&amp;micro;_bearing(N) MEDIDO como input variável no tempo (mesmo idioma do "
            "&lt;code&gt;delta_spectrum&lt;/code&gt;): tupla de pares (N, &amp;micro;) &amp;minus; ex. a Fig. 5 do "
            "Chu 2026 digitalizada (5 testes). Presente, substitui a constante E a modulação de "
            "dano (o &amp;micro; medido já contém a evolução real da interface). NUNCA fittable "
            "&amp;minus; é medição, não ajuste; flui por per_case do cfg adotado. Slider morto neste "
            "explorador (input estruturado, não escalar).&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;MEASURED &amp;micro;_bearing(N) as a time-varying input (same idiom as "
            "&lt;code&gt;delta_spectrum&lt;/code&gt;): a tuple of (N, &amp;micro;) pairs &amp;minus; e.g. the "
            "digitized Chu 2026 Fig. 5 (5 tests). When present it replaces both the constant and "
            "the damage modulation (the measured &amp;micro; already carries the real interface "
            "evolution). NEVER fittable &amp;minus; it is a measurement, not a knob; flows via the "
            "adopted cfg per_case. Dead slider here (structured input, not a scalar).&lt;/p&gt;"),
        refs=[("Chu 2026 Tribol Int &amp;minus; &amp;micro;_plate(N) medido (Fig. 5, digitalizada 2026-07-15)",
               "Chu 2026 Tribol Int &amp;minus; measured &amp;micro;_plate(N) (Fig. 5, digitized 2026-07-15)",
               "chu2026")]),

    VarSpec(
        name="flank_s_crit", symbol="s_crit", unit="m", group="axial_fretting", category="physical",
        context={"baseline": "axial", "overrides": {"flank_wear_on": 1.0, "k_wear_flank": 1e-14,
                                                    "flank_amp_exp": 1.5}},
        sweep=(0.0, 3e-5, 13, "lin"), related=["k_wear_flank", "flank_amp_exp", "flank_wear_on"],
        negligible=True,   # mesmo motivo estrutural do flank_wear_on: o harness
                           # do explorador SEMPRE roda disp-mode => canal L1
                           # (so' modo forca axial) nunca engaja AQUI. Slider
                           # morto honesto; a fisica vive no gate B1-v3.
        equation="s_eff = max(s_th - s_crit, 0); d_w = k_wear_flank*p_flank*(2*s_eff)^flank_amp_exp; dE usa o slip REAL (sem limiar)",
        physics_pt=(
            "&lt;p&gt;LIMIAR de slip do flanco (L1 v2, F4 da execução mestre): abaixo de s_crit o "
            "regime é stick/shakedown (fretting sem transporte líquido de material &amp;minus; "
            "Mäntylä 2020, Juoksukangas 2016); o desgaste é dirigido pelo EXCESSO s&amp;minus;s_crit. "
            "Resolve a falsificação T4: um power-law puro não consegue ser fraco no NÍVEL e forte "
            "no SLOPE simultaneamente (o fit saturava k no limite inferior); com limiar, "
            "d(wear)/dA_F é máximo perto do limiar. &lt;b&gt;Gate B1-v3 G4-a PASS&lt;/b&gt;: slope do "
            "Liu2017 dentro da banda medida ([&amp;minus;4,4e-5, &amp;minus;1,1e-5]/N) com k_wear_flank "
            "DENTRO da âncora física Zhang [4e-15, 2e-14] (o v1 exigia 22&amp;times; a âncora). "
            "0.0 (default) = bit-idêntico ao v1, sem flag.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;Flank slip THRESHOLD (L1 v2, F4 of the master run): below s_crit the regime is "
            "stick/shakedown (fretting without net material transport &amp;minus; Mäntylä 2020, "
            "Juoksukangas 2016); wear is driven by the EXCESS s&amp;minus;s_crit. It resolves the T4 "
            "falsification: a pure power law cannot be weak in LEVEL and steep in SLOPE at once "
            "(the fit saturated k at the lower bound); with a threshold, d(wear)/dA_F peaks near "
            "it. &lt;b&gt;Gate B1-v3 G4-a PASS&lt;/b&gt;: the Liu2017 slope lands inside the measured band "
            "([&amp;minus;4.4e-5, &amp;minus;1.1e-5]/N) with k_wear_flank INSIDE the physical Zhang "
            "anchor [4e-15, 2e-14] (v1 needed 22&amp;times; the anchor). 0.0 (default) = "
            "bit-identical to v1, no flag.&lt;/p&gt;"),
        refs=[("Gate B1-v3 (New_Theory/f4_b1v3_result.json) &amp;minus; slope &amp;minus;1,77e-5/N na banda",
               "Gate B1-v3 (New_Theory/f4_b1v3_result.json) &amp;minus; slope &amp;minus;1.77e-5/N in band",
               "liu2017"),
              ("Mäntylä 2020 / Juoksukangas 2016 &amp;minus; regimes de fretting stick/shakedown",
               "Mäntylä 2020 / Juoksukangas 2016 &amp;minus; stick/shakedown fretting regimes",
               "mantyla2020")]),

    VarSpec(
        name="flank_transverse_on", symbol="", unit="", group="axial_fretting", category="mode",
        context={"baseline": "transverse", "overrides": {}},
        choices=[0.0, 1.0], related=["flank_wear_on", "flank_s_crit", "k_wear_flank"],
        negligible=True,
        equation="switch da ROTA TRANSVERSAL do canal de flanco v2 (prereg-2 do l1-v2); default 0.0 = OFF bit-idêntico",
        physics_pt=(
            "&lt;p&gt;Extensão TRANSVERSAL do canal de flanco v2 (prereg-2 do branch l1-v2): habilita "
            "o micro-slip de flanco de rosca também sob excitação de cisalhamento. Switch de "
            "forma: &lt;code&gt;fittable=False&lt;/code&gt; de propósito &amp;minus; ligar exige pré-registro "
            "(regra permanente dos switches). Default OFF = bit-idêntico; o painel R5 do prereg-2 "
            "decide a adoção per-rig.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;TRANSVERSE extension of the v2 flank channel (l1-v2 prereg-2): enables thread-"
            "flank micro-slip under shear excitation too. Form switch: "
            "&lt;code&gt;fittable=False&lt;/code&gt; on purpose &amp;minus; turning it on requires a "
            "preregistration (standing switch rule). Default OFF = bit-identical; the prereg-2 "
            "R5 panel decides per-rig adoption.&lt;/p&gt;"),
        refs=[("Prereg-2 do l1-v2 (429c272) &amp;minus; rota transversal + painel R5",
               "l1-v2 prereg-2 (429c272) &amp;minus; transverse route + R5 panel",
               "liu2020")]),

    VarSpec(
        name="flank_fret_depth", symbol="d_fret&#8734;", unit="m",
        group="axial_fretting", category="form",
        context={"baseline": "transverse", "overrides": {}},
        sweep=(0.0, 2e-5, 15, "lin"),
        related=["k_wear_flank", "flank_wear_on", "flank_amp_exp"],
        negligible=True,
        equation="SATURA&Ccedil;&Atilde;O do canal de flanco: d_w &amp;times;= max(0, 1 &amp;minus; &amp;delta;_thread_fret / flank_fret_depth);  0 = OFF exato",
        physics_pt=(
            "&lt;p&gt;A &lt;b&gt;profundidade-alvo&lt;/b&gt; do fretting de flanco. O incremento por ciclo "
            "passa a depender do que &lt;b&gt;ainda falta&lt;/b&gt; remover, e não do relógio: mesma "
            "estrutura &lt;i&gt;state-based&lt;/i&gt; que o &lt;code&gt;EmbeddingLoss&lt;/code&gt; recebeu em "
            "2026-07-02.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Física:&lt;/b&gt; o fretting remove material até a folga acomodar o movimento; "
            "então o contato re-conforma, a área cresce, a pressão cai e o transporte líquido "
            "&lt;b&gt;para&lt;/b&gt;. É o regime de &lt;b&gt;shakedown&lt;/b&gt; que o próprio docstring de "
            "&lt;code&gt;flank_wear_from_slip&lt;/code&gt; já citava (Mantyla 2020 / Juoksukangas 2016), "
            "e que a lei ainda não implementava.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;O laço que isto fecha:&lt;/b&gt; &lt;code&gt;delta_thread_fret&lt;/code&gt; já era "
            "acumulado como estado e lido &lt;b&gt;só&lt;/b&gt; para contabilidade de energia &amp;minus; "
            "nunca realimentava a lei que o alimenta. Era acumulador de saída; virou estado.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Esta variável NÃO move ESTA curva&lt;/b&gt; (por isso: negligível). O canal de "
            "flanco exige o companheiro &lt;code&gt;flank_wear_on=1&lt;/code&gt;, que está OFF no ensaio-"
            "padrão desta página &amp;minus; sem ele &lt;code&gt;flank_wear_from_slip&lt;/code&gt; nunca é "
            "chamada e o fator nem é avaliado. Medido em 2026-08-05: das 29 fontes da campanha, "
            "só &lt;b&gt;duas&lt;/b&gt; têm o canal ativo (LIU_2016 e LI_2022_TRIBOINT), e nas 21 curvas da "
            "classe &lt;i&gt;aceleração tardia&lt;/i&gt; o efeito é &amp;Delta;=0 &lt;b&gt;exato&lt;/b&gt;.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Limite de escopo, medido:&lt;/b&gt; o contradomínio é &lt;b&gt;[0,1]&lt;/b&gt; &amp;minus; ele "
            "só sabe &lt;b&gt;desacelerar&lt;/b&gt;. Logo não serve à classe que precisa de &lt;b&gt;aceleração&lt;/b&gt; "
            "tardia (o modelo é 15&amp;times;&amp;ndash;225&amp;times; lento demais no fim daquelas curvas), "
            "que foi falsificada por construção em 2026-08-02. Serve à classe oposta: dado que "
            "&lt;b&gt;satura&lt;/b&gt; e modelo que não.&lt;/p&gt;"),
        physics_en=(
            "&lt;p&gt;The &lt;b&gt;target depth&lt;/b&gt; of flank fretting. The per-cycle increment now depends "
            "on what &lt;b&gt;remains&lt;/b&gt; to be removed rather than on the clock &amp;minus; the same "
            "&lt;i&gt;state-based&lt;/i&gt; structure &lt;code&gt;EmbeddingLoss&lt;/code&gt; got on 2026-07-02.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Physics:&lt;/b&gt; fretting removes material until the clearance accommodates the "
            "motion; the contact then re-conforms, area grows, pressure drops and net transport "
            "&lt;b&gt;stops&lt;/b&gt; &amp;minus; the &lt;b&gt;shakedown&lt;/b&gt; regime already cited in the docstring of "
            "&lt;code&gt;flank_wear_from_slip&lt;/code&gt; (Mantyla 2020 / Juoksukangas 2016) but not "
            "implemented in the law.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;The loop it closes:&lt;/b&gt; &lt;code&gt;delta_thread_fret&lt;/code&gt; was already "
            "accumulated as state and read &lt;b&gt;only&lt;/b&gt; for energy bookkeeping &amp;minus; it never "
            "fed back into the law feeding it.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;It does NOT move THIS curve&lt;/b&gt; (hence: negligible): the flank channel needs "
            "the companion &lt;code&gt;flank_wear_on=1&lt;/code&gt;, OFF in this page's standard run. Only "
            "&lt;b&gt;two&lt;/b&gt; of 29 campaign sources have the channel active.&lt;/p&gt;"
            "&lt;p&gt;&lt;b&gt;Measured scope limit:&lt;/b&gt; its range is &lt;b&gt;[0,1]&lt;/b&gt; &amp;minus; it can only "
            "&lt;b&gt;decelerate&lt;/b&gt;, so it cannot serve the class needing late &lt;b&gt;acceleration&lt;/b&gt;. "
            "It serves the opposite class: data that &lt;b&gt;saturates&lt;/b&gt; where the model does "
            "not.&lt;/p&gt;"),
        refs=[("Regime de shakedown &amp;minus; fretting para de transportar material",
               "Shakedown regime &amp;minus; fretting stops net material transport",
               "Mantyla 2020 / Juoksukangas 2016"),
              ("D-Q 2026-08-05 &amp;minus; motiva&ccedil;&atilde;o medida: o dado satura e o modelo n&atilde;o",
               "D-Q 2026-08-05 &amp;minus; measured motivation: data saturates, model does not",
               "li2022_deriva_tardia_resultado.md")]),
])



