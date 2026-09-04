# Campanha MEM contínua e autônoma (diretiva do professor, 2026-07-14)

> "gostaria que essa otimização e as campanhas rodassem continuamente, sem que
> seja necessário eu interferir."

> **QUIESCÊNCIA — EXECUÇÃO MESTRE EM CURSO (2026-07-21):** a execução única do
> prompt-mestre (`docs/superpowers/plans/2026-07-17-PROMPT-MESTRE-execucao-unica.md`,
> ledger `.superpowers/master-0p1-progress.md`) ABSORVEU o papel da campanha e é a
> ÚNICA escritora de `adopted_configs.json`/`joint_calibrations.json`/store até o
> ledger mestre registrar F5 concluída. Vigílias/batimentos: NÃO pré-registrar, NÃO
> adotar, NÃO fazer merge — checagem de integridade read-only e encerrar.

Este arquivo é o **programa durável** da campanha: qualquer sessão do Claude
(esta, pós-compactação, ou uma nova) retoma daqui. Estado vivo: ledger
(`convergence_ledger.json`), configs (`adopted_configs.json`), pré-registros
(`docs/superpowers/specs/2026-07-11-mem-iter4-preregistrations.md` e
sucessores), fila do professor (`New_Theory/DECISOES_PENDENTES.md`).

## Objetivo (tripé por curva — meta permanente 2026-07-14)

MAE ≤ 0.10 **E** `maxerr` < 0.10 (resíduo assinado |modelo−artigo| < 0.1 em
TODOS os pontos) **E** `resid_std` minimizado — para as **202 comparáveis**
(180 herdadas + 22 R5 pós-merge L1-L7).
**Baseline re-pinado 2026-07-21 (F0.4 da execução mestre, store ae2d7e0,
engine 01689f0bfad8):** mediana 0,04713; MAE>0,1: **54**/202; maxerr>0,1:
**99**/202; lista-mestre = 99 violadores (46 no_piso-mas-maxerr / 37 nível /
16 forma). Censo: `Models/CALIBRATION_AND_VALIDATION/error_budget.json`;
tripé por caso: `New_Theory/l1l7_baseline.json`.
(Histórico: ledger #48 media 65/178 e 110/178 na base antiga de 178.)
**Alavancas novas do branch L1-L7** (tabela mestre: `l1l7_final_report.md`
§2): kj_mode=pedersen como proveniência (PASS-inert); canal de flanco L1
per-rig NÃO adotado (gate B1 FAIL2 — falsificação; 22 casos R5 são o alvo);
creep saturante opt-in per-fonte; clamp L3 (famp_couple_on) aguarda
calibração per-rig de mu_eff_lo/mu_eff_F0_ref/gross_ceiling_decay; L7 bound
informacional; âncoras R5 no KB (wear_spec/mu_thread/creep_class/kj_law).
**REGRA DOS SWITCHES (permanente):** switches de forma são `fittable=False`
DE PROPÓSITO — a otimização nunca pode "descobri-los"; ligar qualquer switch
(flank_wear_on, famp_couple_on, creep_mode, kj_mode…) = pré-registro
explícito com gate de tripé, nunca fit.

## Protocolo por iteração (MEM, sem intervenção)

1. **Escolher alvo** pela ordem abaixo (impacto × tratabilidade).
2. **Ler primeiro**: nota de aparato (`apparatus_notes/`, pasta E p/ R4) e,
   se preciso, o PDF (`BAS_V2_papers/`). Constantes lidas ATRAVÉS do engine.
3. **Pré-registrar** gates ANTES de mexer (tripé + "nenhuma curva regride
   >0.1 + mediana da fonte não piora >0.005"), no doc de pré-registros.
   Gates são imutáveis depois de escritos.
4. **Ajustar** só o que tem classe de procedência promovível (METHODOLOGY §2):
   lido-do-dado (L24: emb da queda inicial, floor do platô, W do joelho),
   input-de-paper (µ, grip, amplitudes, F0 por estágio), fitado-this-rig no
   DOF legítimo (c_bend, C_creep POR PAR, k_ratchet). Fit per-curva sem
   feature identificável NÃO promove — rotular o resíduo.
5. **Verificar em curva cheia** (short-smoke mente — lição slip-regime 1e6).
6. **Adotar** o que passa: `adopted_configs.json` (com `prov`), batch do
   store, ledger, reports regenerados, commit.
7. **Form-limited** → registrar diagnóstico + entrada na fila do professor;
   NUNCA construir forma nova de engine sem autorização (cláusula PR-3).

## Paralelismo (professor 2026-07-15: "multiple shells")

- **Verificações/batches**: `python New_Theory/parallel_batch.py
  [--sources X,Y] [--cases id1,id2] [--workers N] [--store]` — fan-out por
  PROCESSOS (default núcleos−2 = 6; maiores casos primeiro p/ balancear).
  Sims só LEEM configs; store gravado 1× no pai (single-writer preservado).
  Ganho medido: Liu2016 63→22.6 min (2.8×, teto = caso 5e6);
  FULL 178 em 29.8 min (~4× vs ~2h; ZERO deriva vs store = determinismo
  bit-igual confirmado em escala, auditoria 2026-07-15).
- **Fits em paralelo**: SÓ fontes distintas, cada processo com sandbox via
  env `BAS_ADOPTED_CONFIGS=<cópia>.json` (kb redireciona; testado). A ADOÇÃO
  real no canônico continua single-writer no processo principal, após gates.
- Prosa com backticks/crases NUNCA via string bash (executam!) — usar Edit.
- NUNCA: 2 escritores no adopted_configs canônico, nem sandbox p/ adoção.

## MANDATO PERMANENTE (professor, 2026-08-05) — o que NÃO precisa de assinatura

Escrito a pedido do professor, a partir das **cinco** vezes em que a sessão de
2026-08-04 parou ou improvisou. Cada regra abaixo fecha uma dessas lacunas —
não é autonomia genérica, é autorização nos pontos onde ela faltou.

### Autoridade de decisão

**DELEGADO — execute e registre, não pergunte:**

- escrever pré-registro e **fixar os gates** (eles ficam imutáveis depois);
- executar, medir, e **adotar** quando os gates cumpridos mandam adotar;
- **falsificar** candidato e registrar com o mecanismo nomeado;
- **retratar** exceção cuja prova ficou inválida — **mesmo quando custa censo**
  (aconteceu 2026-08-04: −1 resolvida, e a retratação estava certa);
- construir e **consertar instrumento** (sonda, teste-invariante, script);
- re-stamp, regeneração de páginas, sincronia de documentos, commit;
- **aplicar a regra de parada por classe** quando os 3 requisitos estiverem
  medidos (≥2 instrumentos independentes · todo membro falsificado por
  predição pré-registrada · retorno marginal nulo). Aplicar ≠ encerrar
  assunto: é reversível e fica registrado;
- **reabrir** qualquer conclusão quando fingerprint, dado, instrumento ou
  régua mudarem (§4.43).

**DO PROFESSOR — pare e pergunte (não são medíveis):**

- **régua** (os limites do tripé) — define o que significa "bom";
- **escopo do projeto** — material/fonte dentro ou fora (CFRP, âncora interna);
- **estatuto NOVO** — criar categoria que ainda não existe;
- **rodada experimental** — bancada, dinheiro, tempo de terceiros;
- **publicação / comunicação externa**;
- **política de repositório** (ex.: os ~38 MB de HTML versionado).

### Hierarquia da "decisão mais científica" (ordem de precedência)

Não é uma lista de virtudes; é a ordem que produziu os bons resultados de
2026-08-04 e recusou os três candidatos que "funcionavam" pelo MAE:

1. **mecanismo > número** — o gate que decide é uma predição estrutural, nunca
   o erro. *Melhorar o erro sem reproduzir a estrutura é sobreajuste com
   aparência de progresso.*
2. **procedência > ajuste** — lido do dado > ancorado em norma/handbook >
   fitado. Sempre declarar **qual dos três** no `prov`.
3. **parcimônia > contagem** — menos parâmetros **efetivos** (identificabilidade
   conta: 2 parâmetros não-identificáveis valem 1). Fechar mais curvas **não**
   é critério de escolha.
4. **controle > alvo** — a curva que não pode quebrar fixa o limite do ajuste,
   não a curva que se quer fechar.
5. **contra o próprio interesse tem precedência** — achado que reduz o placar
   entra com a mesma prioridade de um que o aumenta, e com o número.

### Pré-testes OBRIGATÓRIOS antes de escrever um prereg de alavanca

Custam 1–2 simulações cada e teriam poupado **dois** preregs inteiros em
2026-08-05 (D-J e D-K, que testaram metades diferentes da mesma composição
porque eu fatiei errado o escopo):

1. **Sonda de 2 pontos — eixo do SINAL.** Já era regra. Direção antes de
   qualquer bisseção; Δ = 0 exato não autoriza "morto" sem conferir
   companheiros e se a chave é campo do engine ou de cfg.
2. **Sonda de TETO DE AUTORIDADE — eixo da MAGNITUDE.** *(nova, 2026-08-05)*
   **Suprima o canal por inteiro** e pergunte: *"o alvo está sequer dentro do
   alcançável?"* Se o fator mínimo com o canal zerado ainda estiver do lado
   errado do necessário, **nenhum valor** da alavanca chega — e o prereg morre
   na mesa, sem código. Medido no LIU_2022: slip sozinho tem teto 0,460 e
   `renew` sozinho 0,586, contra alvo **0,203** ⇒ os dois são impossíveis
   isolados; **juntos** dão 0,040 ⇒ alcançável. Nenhum dos dois preregs
   anteriores teria sido escrito com essa medição na mão.
3. **Fronteira da grade.** Se o ótimo cair no **extremo** da grade declarada,
   **estenda antes de adotar**. Valor de fronteira é ótimo que você não viu —
   é a disciplina de `bounds_saturated` que este repo já aplica aos fits.
4. **Teto em PARES, não só isolado.** *(nova, 2026-08-05)* Duas alavancas podem
   ser **individualmente inertes e conjuntamente decisivas** — e nesse caso a
   sonda de 2 pontos, que testa uma por vez, **não as vê**. Medido no
   LI_2022: a razão de perda 20 Hz/10 Hz vai de **1,005** (base) para
   **1,000** com `C_creep=0` isolado (nada), **0,716** com só o input
   corrigido, e **0,539** com os **dois juntos** — 92 % da lacuna. O input
   errado tornava a re-atribuição invisível; a atribuição errada tornava a
   correção de input insuficiente. **Quatro tentativas nessa fonte falharam
   por testar uma metade de cada vez.** Regra: quando duas hipóteses tocam o
   mesmo canal, mede-se o teto **do par**.
5. **A banda do gate vem do TETO medido, não do dado.** *(nova, 2026-08-05)*
   Pedir no gate o valor do dado reprova alavanca que entrega o máximo dela e
   escreve "falsificado" onde o certo é "chega até aqui". Aconteceu no D-N:
   pedi 0,478 (o que só um flanco de 100 % daria) contra um teto de 0,703 — e
   a alavanca acertou 0,710. **Meça o teto, ponha a banda nele, e declare o
   resíduo com o número e a atribuição.**

### Desempate padrão (fecha a lacuna medida no prereg do D-H)

Quando **mais de uma** parametrização passa **todos** os gates e o prereg não
declarou regra de escolha, use nesta ordem, e **declare o vice e por que
perdeu**:

1. menos parâmetros efetivos;
2. **nenhuma constante coincidindo com artefato do aparato ou do ensaio** —
   duração da janela, teto de simulação, número de pontos, extensão da
   digitalização. *Constante de tempo igual à duração do ensaio é fit da
   janela, não do material.*
3. melhor desempenho na perna que manda.

### Uma ordem que não se inverte

**Estatuto de curva decide-se pelos méritos dela, antes e independentemente de
qualquer gate que ele desbloqueie.** Se um gate só passa declarando uma curva
fora do censo, o ramo é **NÃO ADOTA** — e o estatuto vai para prereg próprio.
Declarar por conveniência inverte a ordem da prova.

### Não inventar estatuto no meio da execução

Se a medição sugerir uma categoria nova (ex.: *"o excesso é menor que o erro
padrão do próprio σ_res"* — medido em 0,21 SE na `tapered_rep2`), **meça,
registre o número, e siga**. Criar categoria durante a execução é o oposto do
pré-registro. A proposta vira item da fila do professor.

### O que "até esgotar as técnicas" significa, operacionalmente

Não é "tentei e não melhorou". É a **regra de parada por classe** já escrita
(`regra_de_parada_proposta.md`): a classe de forma só fecha quando foi
identificada por ≥2 instrumentos independentes, **todo** membro dela foi morto
por **predição pré-registrada** (candidato inerte ou gate nunca chamado **não
conta** — é INCONCLUSIVO, não falsificação), e o retorno marginal é nulo.
Enquanto houver membro não testado com discriminante válido, a classe **não**
está esgotada.

### Não ficar parado esperando job de fundo (2026-08-05)

**Diagnóstico honesto:** quase todos os pedidos de *"continue"* do professor em
2026-08-04/05 caíram **enquanto eu tinha tarefa longa em background** —
re-stamp (24 min), suíte (14 min), varredura (20 min) — e eu reportava status e
**esperava**, tendo trabalho independente disponível.

Job de fundo que termina **me re-invoca sozinho**; o intervalo é que estava
sendo desperdiçado. Regra:

1. **Com job de fundo rodando, pegue o próximo item INDEPENDENTE da fila** —
   sonda só-leitura, leitura de PDF, escrita de prereg, doc, teste de
   invariante. Nunca reportar-e-esperar.
2. **Não toque no que o job mede.** Se a única coisa disponível interage com a
   medição em curso (ex.: `Φ`/`k_j` enquanto uma varredura de `k_wear_flank`
   roda), **declare e pare de tocar** — confundir duas mudanças é pior que
   esperar. Foi por isso que D-H (forma) e D-I (nível) foram passos separados.
3. **Um relatório por marco, não por intervalo.** Reportar quando um veredicto
   fecha, não a cada conferência de progresso.
4. **Sem trabalho independente e sem job pendente:** aí sim é ponto de parada
   legítimo — e a fila do professor deve receber o item, não uma pergunta.

### VAZÃO: paralelizar o diagnóstico, serializar a adoção (2026-08-05)

**Diagnóstico honesto do gargalo:** não é orçamento de tokens — é
**serialização**. Cada ciclo era ~2 min de trabalho meu e ~20 min esperando
**uma** sonda. O consertável é quantas coisas correm ao mesmo tempo.

**1. Lote de sondas, não uma.** Lançar **3–4 jobs de fundo independentes** por
turno, cobrindo hipóteses diferentes, em vez de uma grade por vez. A máquina
tem núcleos (o `parallel_batch` já usa 6); as sondas eram single-process.
Regra: se duas medições não dependem uma da outra, **saem no mesmo turno**.

**2. Subagentes só-leitura, um por FONTE.** Autorizado pelo professor em
2026-08-05 (*"rodando múltiplas instâncias para diferentes artigos"*).
Cada subagente pode:

* ler PDF, extrair e **conferir figura na imagem** (nunca em resumo);
* medir piso de réplica / de digitalização;
* rodar triagem, anatomia, decomposição — tudo só-leitura;
* redigir **rascunho** de prereg com a procedência que achou.

**O que subagente NÃO faz — single-writer, e a razão é medida:** escrever
`adopted_configs.json`, escrever o store, ou commitar. Duas sessões no mesmo
recurso já custaram commits perdidos e `fatal: unable to write new index file`
(medido 2026-07-17), e a memória do projeto registra a regra:
**diagnóstico em paralelo, adoção em série.**

**3. Nunca encerrar turno só para esperar.** Antes de terminar, lançar a
próxima coisa independente. A suíte é gate de **commit**, não de continuar
diagnosticando — enquanto ela roda, a sonda seguinte já pode estar no ar.

**Limite que continua valendo (pré-teste 2 do charter):** não paralelizar duas
alavancas que tocam o **mesmo canal** sem antes medir o **teto do par** — senão
o resultado de cada uma fica atribuído errado. Paralelismo é entre **fontes** e
entre **hipóteses independentes**, nunca entre metades de uma composição.

### Invocação

Uma linha basta, porque o mandato vive aqui e não no prompt:

> **"Siga o MANDATO PERMANENTE do charter. Não pare, não peça assinatura para
> o que está delegado, e registre as decisões como *por delegação (mandato
> 2026-08-05)*."**

## CAMPANHA FAXINA-E-ANATOMIA (professor, 2026-08-06) — pipeline por fonte

**Decisão em sessão** (brainstorm 2026-08-06): escopo **C** (pipeline por fonte)
com a re-auditoria dos pisos F7 como **última fase**. Sob o MANDATO PERMANENTE
acima — mesmas delegações, mesmas proibições, mesma disciplina de gates.

**Contexto que motivou:** a fila form-limited fechou em 1 curva (P-1/P-2 na fila
do professor), mas o mapa de 2026-08-06 (`New_Theory/anatomia_mapa_fora.py`,
re-rode antes de citar) mediu **64 curvas fora mapeáveis, das quais 32 são
viés-dominadas** (|viés| > 80 % do MAE, ≤1 cruzamento de sinal) — exatamente a
assinatura que em 2026-08-05 rendeu **+5 no censo por correção de DADO/INPUT**
(D-S, D-R, erratum de drive), não de modelo. E `classe_parada` é rótulo **por
FONTE**, não por curva: membros podem ter defeito de outra classe sem que
ninguém tenha olhado o resíduo deles.

### Objetivo e condição de parada

Toda curva fora do tripé termina em UM de três estados, com número:
 (a) **tripé por mérito** (conserto de dado/input via prereg);
 (b) **causa nomeada + rota esgotada** (anatomia + teto de autoridade quando
     for modelo; `data-blocked` quando faltar held-out na biblioteca);
 (c) **item na fila do professor** (`DECISOES_PENDENTES.md`), com o diagnóstico
     pronto.
Parada da campanha: **3 fontes consecutivas** com zero saídas por mérito E zero
defeitos de dado achados ⇒ relatório de fecho e parar. (Reabre se
dado/instrumento/régua mudarem — a regra de reabertura da parada vale aqui.)

### O pipeline, por fonte (ordem = nº de viés-dominadas do mapa; re-medir)

Prioridade no mapa de 2026-08-06: **LU_2024 (9 de 10!)** · YANG_2023_IJPEM (5)
· YANG_2021 (3) · ECCLES/KARLSEN/LIU_2025/YANG_2019/ROUSSEAU (2) · resto.

1. **ANATOMIA por curva** — decomposição viés/σ (σ é invariante por translação),
   padrão de sinais, cruzamentos ⇒ classe: nível / forma / dado-suspeito.
   Instrumento: o idioma de `fila_form_limited_3_anatomia.md`.
2. **FIDELIDADE DE DADO** — (i) PDF vetorial? extrair polilinhas
   (`page.get_drawings()`), calibrar nos rótulos de tick, **atribuição por RMS
   objetivo com unicidade POR FIGURA** (bug medido: índices são locais à
   figura); (ii) assinaturas internas: réplica **idêntica ao dígito** a outra,
   **não-monotonicidade** em ensaio estático, **reta** (σ dos passos <1e-3),
   base múltipla exata de 1/N; (iii) round-trip contra tabelas/prosa do paper.
3. **AUDITORIA DE INPUT** — registry × nota de aparato × paper: freq, F₀,
   drive/δ_amp, `csv_x_scale/offset`, base de normalização. A classe dos
   erros 10×/2× e das bases 12,0/11,5. **Pergunte à nota antes de propor
   correção** (27 de 29 fontes têm nota; `rec.apparatus_note_path`).
4. **CONSERTO por prereg** (classe *dado*, molde D-S/D-R): gates imutáveis
   ANTES, predição registrada por curva, "G2 não se aplica a correção de dado"
   declarado, isolamento bit-idêntico das não tocadas (G3), piso re-medido
   (G5), fingerprint NÃO muda com CSV ⇒ validar re-simulando, nunca por hash.
   **Um conserto por vez** (single-writer); censo/docs/testes no MESMO commit.
5. **SEM ROTA** — documentar com número (piso, teto de autoridade, held-out
   inexistente). Reclassificação de camada da triagem é **proposta**, nunca
   edição de código sem assinatura.

### Última fase — pisos sob as 25 exceções F7 (rigor contra nós)

Re-medir os pisos que sustentam exceções assinadas com os instrumentos da fase
2 (o piso do CACCESE era **87 % artefato de digitalização**). Piso corrigido
pode **retratar** exceção (resolvido cai) ou passar curva por mérito — os dois
desfechos se publicam com o mesmo destaque.

### Fora de escopo DESTE loop (não re-tentar, não re-decidir)

- Candidatos **falsificados** da classe parada (incubação, kernel saturante nas
  18 transversais, CM) e o **valor 3,57** de `fret_freq_exp`.
- **P-1..P-5** da fila do professor (incl. kernel de creep e `fret_freq_exp`
  per-fonte — ambos exigem assinatura).
- Formas de engine novas sem os 5 pré-testes do charter; adoção de constante
  sem held-out.

## CAMPANHA MARGENS (professor, 2026-08-06 tarde) — census-positiva, A depois B

**Decisão em sessão**: escopo **A depois B**; e o **P-1 foi ASSINADO com valor
1,0** (`fret_freq_exp` = 1,0 per-fonte no LI_2022, declarando por escrito que
não há held-out na biblioteca — o único outro grupo com canal de flanco é
mono-frequência). Objetivo da campanha: **subir o censo ESTRITO**, com a
disciplina intacta (preregs, gates imutáveis, predição registrada, single-writer,
leitura dupla).

### Ordem de partida (pendências que rodam ANTES da fase A)

1. **Executar o D-U** (prereg `2026-08-06-yang2021-ancora-prereg.md`, dry
   PASSA) — custo declarado **−1** (r1 sai; estava dentro por artefato de
   âncora). CSVs + re-sim da fonte + G5 + nota de aparato (3 correções) +
   censo/docs no MESMO commit. Fingerprint NÃO muda.
2. **Adotar o P-1 assinado**: `fret_freq_exp = 1,0` no grupo LI_2022_TRIBOINT.
   Predições JÁ medidas na varredura (grade de 8 pontos, commit `da5a93a`):
   full 0,0217/0,0533*/0,0249 · axialmin_10Hz 0,0481/—/0,0215 · 15 Hz
   inalterada 0,0323/0,0166 · 20 Hz 0,0110/0,0140 ⇒ **fonte 4/4, censo +1**.
   (*mx da full na célula 1,0 a conferir na execução; a varredura registrou
   mae/σ.) Adoção muda o fingerprint ⇒ **re-stamp uniforme dos 210** + censo +
   docs + suíte no mesmo commit. Registrar em DECISOES_PENDENTES: P-1 →
   DECIDIDA (professor, 2026-08-06, valor 1,0 pela âncora física dupla; margem
   0,4 % declarada e aceita em sessão).
3. **Retomar o agente LIU_2025** (morreu no limite de sessão; contexto
   preservado — SendMessage, não relançar).

### Fase A — MARGENS (a fila quase-lá)

População medida em 2026-08-06 (re-rankear a cada tick — o censo muda):
**11 curvas com pior perna ≤1,30×**, 3 delas ≤1,15× (`lu2024_fig18_amp1p5`
1,05× mx, declarada · `liu2025_fig2_single` 1,07× σ, parada · `bauer_rep5`
1,12× mx, exceção). 7 das 11 são exceções/declaradas ⇒ passar por mérito =
**+1 estrito cada**.

Pipeline por curva, da mais próxima para a mais distante:
1. **Nomear a perna que reprova e OS PONTOS que a carregam** (mx = o argmáximo;
   σ = os maiores saltos de resíduo). É pontual por natureza — mx é UM ponto.
2. **Fidelidade DESSES pontos** contra o traço (vetor se houver;
   render/pixel se raster) + assinaturas internas. A pergunta é estreita: *o
   ponto que reprova existe no impresso, na posição digitalizada?* (classe
   CACCESE-rep2: 9 pontos errados seguravam a curva fora por 3 %).
3. **Artefato real ⇒ conserto por prereg** (molde D-S/D-U: gates imutáveis,
   predição por curva, isolamento bit-idêntico, G5 piso re-medido, censo/docs
   no mesmo commit). **Ponto confirmado no impresso ⇒ causa nomeada, próxima
   curva** — sem inventar rota de modelo para curva de exceção.
4. Exceção que passar por mérito ⇒ **retirar a assinatura** no mesmo commit
   (precedente `_EXCECOES_RETIRADAS_D1`: retirada com prova preservada).

### Fase A′ — FECHAMENTO DE FONTES (re-priorização do professor, 2026-08-06 noite)

Decisão em sessão: *"seria bom finalizar os que têm poucas curvas longe do
tripé"* — a fila da fase A passa a ordenar por **nº de curvas que faltam para
a fonte fechar 100 %** (desempate: menor multiplicador). Medido no store
139/205 (fontes 100 % = 12):

1. **KARLSEN_2022 (2/11)** — `run1p2` 1,21× · `run14p2` 2,36×, ambas exceções
   viés-dominadas (perfil de base/input). A run1p2 já tem agente em voo.
2. **LIU_2020_WEAR (1/9)** — `zinc_AF0.4mm_P0-18kN` 1,46×, exceção
   viés-dominada nas TRÊS pernas.
3. **SUN_2025_CRIMP (1/8)** — `standard` 3,19×, parada; anatomia decide.
4. Depois: o resto da fila quase-lá original (CHU 1,17×, ECCLES par, ...).

Fechar 1–3 leva fontes 100 % de 12 → **15**. NÃO-acionáveis do tier 1-fora,
declarados: YANG_2023_AME (1/1, CFRP fora de escopo por aprovação do
professor) e ZHANG_2006 (fig. "Illustration") — finalizadas por estatuto, sem
ação possível sem mudança de escopo.

### Fase B — LU_2024 re-fit P3 (depois que A esgotar)

O maior alvo único: 10 fora, viés monótono no TORQUE já nomeado (fig20: −0,34 →
−0,10). Plano vivo: `lu2024_plano_melhoria.md` P3 — re-ler constantes com as
âncoras NOVAS do paper (rigidez por torque Fig. 21, µ_eff(N) Fig. 19, 3
réplicas reais da Fig. 14). **Adoção gateada MEM**: split leitura/held-out
mecânico (`8336437`), prereg com gates antes de fitar, nenhum caso pior +0,01,
procedência por constante. Se os gates reprovarem, o resultado é o número, não
a adoção.

### Fora de escopo

Candidatos falsificados; P-2..P-6 (seguem na fila); mudança de régua; formas de
engine novas sem os 5 pré-testes. A campanha FAXINA-E-ANATOMIA fica **em pausa**
(retoma se a MARGENS secar antes da fase B).

### Parada

Fase A esgota quando toda curva ≤1,30× tiver conserto executado ou causa
nomeada com o ponto confirmado no impresso. Fase B termina em adoção ou
reprovação pelos gates. Depois disso: relatório de fecho e parar o loop.

## Regras operacionais (lições acumuladas — não violar)

- Fits que escrevem `adopted_configs.json` em FOREGROUND (colisão em bg).
- Batches longos em background COM notificação; `--resume` p/ retomar.
- Commits com arquivos EXPLÍCITOS (WIP paralelo do professor no worktree).
- Retry-guard PermissionError (OneDrive) em toda escrita de JSON.
- `importlib.reload` não recarrega transitivos → processo fresco por fit.
- pt-BR com acentos em tudo que o professor lê.
- NUNCA `pytest | tail` antes de commit sem ver o exit code real.
- Curvas com fratura/corrosão/térmica: out-of-model declarado — trim/caveat,
  não fitar o que o modelo não representa.

## Estado (2026-07-15, ledger #52): PASSADA R4 COMPLETA
Global 178: mediana 0.0465 · >0.1: 37 · maxerr>0.1: 81. R4-64: 0.179→0.0471
(paridade com a base tratada). Adotados: LIU_2016 (PR-27b, 0.041),
SUN_REASSY (PR-28, 0.018), QIN (PR-29b, 0.005), CACCESE+JCSR-indoor (PR-33,
0.018/0.0009). GRZEJDA passa no default (0.035). Na fila do professor: CHU
(µ(N)/kernel), ECCLES+SUN-crimp grease (decisão G2/kernel exponencial),
YANG_2023_AME (jet nut CFRP, 1 caso — combinação self-locking+composto+R=0,
rotulado sem tentativa), classe fratura (secos do Sun-crimp).
ESTADO 2026-07-15 (fim do dia): QUASE-ESTACIONÁRIA (Etapa 4b) — varredura
maxerr 100% classificada, knobs exauridos, fits PAUSADOS aguardando a fila
(kernel desacelerante = maior alavancagem). Batimentos vigiam; qualquer
resposta do professor na fila retoma imediatamente. Se surgir dado novo
(ex.: redigitalização Fig. 5 do Chu), a ordem recalcula.

## ESTADO 2026-07-16: 2ª QUASE-ESTACIONARIEDADE (nível novo)
Retomada pós-limite CONCLUÍDA: PR-38 test1 (Chu limiar 0.334→0.066),
PR-39v2 (FatigueLoss Ti adotado, cliff 410k exato; Goodman-vivo resolvido;
Liu2025 = scatter irresolúvel), PR-40 (Karlsen run20p0 tripé), PR-41 (morte:
alavanca inerte), PR-42 (varamp spectrum), PR-43b (Zhang −68%). Ledger #59:
180 comparáveis · mediana 0.0429 · MAE>0.1: 32 · maxerr>0.1: 77 · MAE médio
0.0659±0.089. TUDO knob/leitura-alcançável esgotado DE NOVO — o restante
concentra-se na fila do professor (kernel desacelerante ≈30+ curvas no topo;
Yang2023 bifurcação; Yang2021; expurgo zhang sintético; capabilities).
Vigília 6h; qualquer resposta na fila retoma na hora.

## PAUSA POR LIMITE DE GASTOS (2026-07-15, fim do dia — histórico)
O agente do PR-39 morreu no LIMITE MENSAL de gastos da org; sem margem para
novos agentes. Estado congelado no ledger #57 (mediana 0.0429 · MAE>0.1:
33/180 · maxerr>0.1: 77/180). RETOMADA (quando o professor elevar o limite
em /usage-credits ou claude.ai/admin-settings/usage): (1) PR-39 fratura —
dados _tozero prontos (liu2025 amp0p4, li2022ti, sun-secos), receita PR-24
no doc, rodar em sandbox e apresentar adoção; (2) PR-41 li2022ti canal de
freq (fret_freq_exp, gates 15/20Hz); (3) PR-43 zhang fig16 runout (caso-
limiar, c_bend lido — receita do PR-38 test1); (4) fila do professor
(kernel desacelerante = maior alavancagem). Cron desta sessao morre com
ela; o charter retoma tudo.

## Ordem de alvos (recalcular a cada ciclo pelo ledger; estado 2026-07-14)

1. **LIU_2016** (14 casos, med 0.18, sobre-afrouxa): receita do Liu2017
   §4.14a-rev — emb lido da queda inicial (L24) + C_creep per-rig da cauda;
   fig11a dá o sweep A_F (evidência G1). Fit em curva cheia (casos 1e6-5e6
   ciclos ~4 min/sim → ler features primeiro, verificar 1x no fim).
2. **SUN_2025_REASSY** (5, 0.35): estado de reuso NOMEADO
   (`emb_consumed_frac`/`D_init` já existem) — input-de-estado, zero forma.
3. **QIN_2024** (3, 0.54): C_creep POR PAR CFRP-Ti (precedente §4.7) da
   cauda 25C; interference como estado inicial (F0 por caso já difere).
4. **CHU_2026** (9, 0.14): caso-limiar D0.3 (slip threshold) + c_bend
   per-rig; superligas µ do paper se reportado.
5. **ECCLES_2010** (10, 0.148): porca prevailing-torque — ler o paper
   (torque de prevalência 1.5-2.3 N·m medido) → entra como atrito de rosca
   retentor/floor lido do dado; se pedir FORMA nova → fila do professor.
6. **SUN_2025_CRIMP** (8, 0.15): transversal dry colapsa rápido (0.6+) —
   amplitude/µ do paper; axial já ≤0.10.
7. **CACCESE_2009** (7, 0.127) + **JCSR_2023** (5, 0.28): C_creep por par;
   corrosão (outdoor/seawater) = caveat out-of-model, reportar honesto.
8. **YANG_2023_AME** (1, 0.39): jet nut CFRP — provável fila (self-locking).
9. **Varredura maxerr base-114** (52 violam; mediana 0.088): atacar os
   knob-alcançáveis (Lu curvatura, Karlsen run14p2, Chu picos); joelhos de
   espectro/caudas de fratura/limiar Yang2023 = form-limited já mapeados →
   fila + documentação.

## Parada / throttle

- Fonte fecha quando: todos os casos no tripé OU resíduo rotulado
  form-limited/out-of-model com diagnóstico escrito.
- Campanha estaciona (METHODOLOGY Etapa 4b): Δ(média global) < 0.002 por 3
  entradas consecutivas do ledger → escrever síntese, parar de fitar, e
  aguardar o professor (fila cheia de propostas de forma).
- Cada iteração fecha com: ledger + commit + resumo legível no chat.
- Entradas novas do ledger DEVEM incluir mean, mae_std, maxerr_mean,
  maxerr_std (formato de acompanhamento pedido 2026-07-15: gráfico 1 = MAE
  médio ± σ; gráfico 2 = res.máx médio ± σ; computar do store no momento).
