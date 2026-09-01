# PROMPT MESTRE — copiar e colar num único prompt (execução completa L1–L7 → meta tripé <0,1)

> Este arquivo é o prompt a ser colado numa sessão do Claude Code aberta em
> `C:\Users\leo_r\OneDrive\BPL\Analitical\BAS_V2`. Ele executa TODAS as fases na ordem certa,
> com gates, retomada automática e paradas só onde a decisão é do professor.

---

Execute o plano-mestre de aplicação dos modelos L1–L7 e convergência à meta de validação
(tripé por curva: MAE<0,1 E maxerr<0,1 em todas as curvas comparáveis), do início ao fim,
na sequência abaixo. Trabalhe de forma autônoma; só pare nos pontos marcados PARE.

## PRÉ-CONDIÇÕES (verificar antes de qualquer escrita; se falhar → PARE e me avise)
1. QUIESCÊNCIA: nenhuma outra sessão/campanha ativa — `git log -1 --date=iso` no main sem commit
   de terceiros na última hora e nenhum python alheio rodando. Esta sessão passa a ser a ÚNICA
   escritora (ela absorve o papel da campanha durante a execução).
2. O worktree `C:\bas2l17` existe no branch `feature/l1-l7-gaps` com a onda final de fixes
   concluída (ver `.superpowers/sdd/progress.md` lá). Se a onda final não terminou, conclua-a
   primeiro (2 MUST-FIX do review: DOF-guard 94 campos; VarSpecs dos 12 campos novos; +
   `flank_wear_on fittable=False`; + pasta F versionada por `git add -f`).
3. Limite de gasto elevado. PROTOCOLO DE QUEDA: se um subagente morrer com "monthly spend limit",
   registre no ledger, tente concluir o passo INLINE se for mecânico; senão pare e me avise.

## AUTORIZAÇÕES CONCEDIDAS POR ESTE PROMPT (standing, válidas para toda a execução)
- Merge de `feature/l1-l7-gaps` no main; commits no main; regeneração do store canônico.
- Executar preregs e ADOTAR (escrever `New_Theory/adopted_configs.json` /
  `New_Theory/joint_calibrations.json` pelas convenções da campanha) SEMPRE QUE o gate do prereg
  passar no tripé contra o baseline vigente. Gate FAIL → não adota, documenta no ledger e segue.
- Rodar as skills `converge-model` / `paper-study` como veículo da Fase 3.
- Fase 4 (L1 v2): implementar candidatos default-inertes em branch gateado e ADOTAR se o gate
  passar; máximo 2 preregs por candidato (FAIL2 = falsificação documentada).
- NÃO AUTORIZADO (exige minha resposta): assinar exceções do ledger (proponha, não assine);
  deletar dados/curvas; qualquer push remoto; mudanças fora deste escopo.

## INTENSIDADE DE EXECUÇÃO E ORQUESTRAÇÃO (política de tokens)
- Controlador e agentes de JULGAMENTO (gates, design de F4, review final de branch): esforço max.
- Tarefas MECÂNICAS (wiring, git, transcrição, docs simples): modelo barato + esforço baixo —
  esforço max aqui é desperdício, não rigor.
- GASTAR tokens em profundidade (Workflow/fan-out + verificação adversarial) SÓ nestas fases:
  - F3 diagnóstico: um agente por fonte EM PARALELO (paper-study ponto-a-ponto) → passada MAE →
    passada maxerr. (A campanha já validou 4–5× shells paralelos.)
  - F4: painel de candidatos de mecanismo (gerar N em paralelo → julgar → sintetizar) +
    verificação adversarial do gate.
  - TODO gate: ≥3 votos adversariais tentando REFUTAR o "passou" antes de qualquer adoção.
  - F5: crítico de completude (que curva ficou de fora? que número não foi verificado?).
  - Rodada 6 (se F4 falhar): varredura multi-modal de literatura.
- NÃO usar ultracode global "workflow para tudo" — muitas tarefas (escritas, merges, fixes
  mecânicos) NÃO devem ser workflow. Orquestração é dirigida às fases acima.
- CERCA — NUNCA paralelizar (disciplina de escritor único do plano):
  - ESCRITAS de adoção (`adopted_configs.json`/`joint_calibrations.json`/store): os FITS podem
    rodar em paralelo (leitura); a ESCRITA é sequencial, um escritor por vez.
  - MERGES: só em janela de vigília, um de cada vez.
  - Pontos PARE: checkpoints humanos, sequenciais por design.
- CUSTO: esta política bate no limite de gasto mais rápido (risco nº 1). É segura AQUI só porque
  o plano é retomável pelo ledger — se cair, reinvocar retoma. Elevar o teto ANTES de F3 e F4.

## ESTADO E RETOMADA
Ledger mestre: `.superpowers/master-0p1-progress.md` (crie no repo main se não existir; uma linha
por passo concluído, com números). AO INICIAR, LEIA O LEDGER e retome do primeiro passo incompleto —
nunca re-execute fase concluída. Referências canônicas: plano detalhado
`docs/superpowers/plans/2026-07-17-plano-mestre-aplicacao-e-meta-0p1.md`; tabela de adoção
`New_Theory/l1l7_final_report.md` §2; histórico do branch `C:\bas2l17\.superpowers\sdd\progress.md`.
Fits longos: FOREGROUND ou background com retomada (`--resume` do report; PYTHONPATH=src quando
rodar módulos). Staging sempre por arquivo explícito. Commits com trailer
`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## SEQUÊNCIA (cada fase: executar → commit(s) → linha no ledger → painel quando indicado)

### F0 — Integração
0.1 Concluir/verificar a onda final do branch (pré-condição 2); review de branch deve constar
    READY (os 2 MUST-FIX resolvidos; suíte alvo verde).
0.2 Merge no main (`git merge --no-ff feature/l1-l7-gaps`), resolvendo conflitos triviais
    (esperados ~zero; `test_transfer_validation` já corrigido no main prevalece). Se o merge
    reclamar de untracked files que seriam sobrescritos (cópias de leitura na árvore main:
    este prompt, o plano-mestre, `.claude/skills/prompt-mestre/SKILL.md`), apague as cópias e
    refaça — as versões do branch aterrissam idênticas nos mesmos caminhos.
0.3 No main: suíte 27-arquivos + `python -m bolt_analysis_studio.validation.report --all`
    (202 casos; UFU presentes). Commit do store.
0.4 RE-PIN: gerar baseline novo (`scripts/l1l7_baseline.py` adaptado ao main) + CENSO do tripé
    (rodar `validation.error_budget`; listar TODAS as curvas com MAE>0,1 e/ou maxerr>0,1 —
    esta lista é a lista-mestre da meta). Ledger + commit.
0.5 Limpar: remover worktree `C:\bas2l17` (`git worktree remove`) após confirmar merge íntegro.

### F1 — Onda A (adoções risco-zero, 1 prereg em lote)
`kj_mode="pedersen"` como proveniência de geometria; check L7 default-on (informacional);
bandas KB no `check_input`. Gate: paridade exata do painel (nada muda por construção).
Adotar, ledger, commit.

### F2 — Onda B (adoções comportamentais per-rig, 3 preregs NA ORDEM)
2.1 Canal de flanco per-rig H.Li2022 (`flank_wear_on=1` como config da fonte + `k_wear_flank`
    fitado per-rig; partida do gate T4: 1,89e-13; alvo: os 4 casos axial×freq <0,1 no tripé).
2.2 Creep saturante vs log-t por fonte de creep (JCSR/Caccese/Qin/Nah/li2022marstruc): adotar
    `creep_mode="saturating"` só nas fontes onde o tripé melhorar.
2.3 Clamp L3 (`famp_couple_on=1`) COM re-fit conjunto de `tr_loose_gain` nas fontes força-mode
    transversais com F_amp registrado. Cuidado documentado: não co-habilitar canais de rosca
    legado+L1 (overlap de dE); dupla via de dano no teto (k_dmg_mu × gross_ceiling_decay).
Cada prereg: fit em curvas completas → gate tripé vs baseline → adoção por-fonte → ledger+commit
→ re-run parcial do report nas fontes afetadas.

### F3 — Varredura sistemática (o grosso; loop até critério de parada)
3.1 `error_budget` pós-F2 → classificar cada violador (MAE ou maxerr >0,1) em:
    A-fitável (nível/constante) · B-forma (hoje = L1; casos R5 + sweeps axiais) · C-irredutível
    (caudas de fratura → trim registrado; scatter de réplicas demonstrado; ex. já provado:
    Bauer fig6 maxerr 0,157 = dispersão entre réplicas).
3.2 Loop no bloco A com `paper-study` por fonte (diagnóstico ponto-a-ponto início/taxa/forma/piso
    ANTES de fitar — lição da campanha): primeiro passada MAE, depois passada dedicada de maxerr.
    Cada melhoria = prereg+gate+adoção por-fonte+ledger.
3.3 PARADA da F3: (i) bloco A vazio, OU (ii) 3 preregs consecutivos com ganho de mediana <0,005 e
    sem redução do count de violadores. Painel + commit.

### F4 — L1 mecanismo v2 (única física nova; branch gateado novo `feature/l1-v2`)
4.1 Candidatos na ordem (da falsificação B1, não do zero): (a) expoente de amplitude no slip de
    flanco ≥1,5 (medido Liu2020: 1,5–1,6→3,2), (b) termo de onset/terceiro-corpo (debris),
    (c) acoplamento slip-limiar. Cada candidato: default-inerte + TDD + registry.
4.2 Gate (prereg): slope Liu2017 ∈ [−4,4e-5, −1,1e-5]/N E os 22 casos R5 com tripé <0,1 E zero
    regressão transversal. Máx. 2 preregs por candidato.
4.3 Se TODOS os candidatos derem FAIL2 → documentar, disparar a rodada 6 de literatura focada
    (leads: Mäntylä 2020 Tribology Int; Juoksukangas 2016; Jiménez-Peña 2017) e **PARE** para
    minha decisão (é o único caminho para a meta nos casos R5).
4.4 Se PASS → merge no main (mesmo protocolo F0) + adoção per-rig gateada.

### F5 — Certificação
5.1 `report --all` + `error_budget` finais: meta = 100% das curvas comparáveis com tripé <0,1,
    exceto a LISTA DE EXCEÇÕES PROPOSTAS (cada uma com prova quantitativa: dispersão de réplicas
    medida OU trecho out-of-model com trim registrado). **PARE: apresente-me a lista para
    assinatura** — não assine por mim.
5.2 Atualizar os docs vivos: `concept_coverage.html` (estado final), `MODEL_LEGITIMACY.md`
    (§ do estado da meta), `CLAUDE.md` (roadmap: itens 4/9/10 reescritos; nota C2 stale removida).

### F6 — Documentação completa do processo (o Manual; último passo, após a certificação)
Produzir `docs/MANUAL_BAS_V2/` (pt-BR com acentos, MD no repo) + página-hub `manual.html` no
explorador de variáveis (linkada do índice e da landing "comece por aqui"). NÃO duplicar conteúdo
existente: o manual é o FIO CONDUTOR e linka o que já existe (concept_*.html, estudos por fonte,
MODEL_MATH_REFERENCE, MODEL_LEGITIMACY, METHODOLOGY/MEM, reports de validação). Três volumes:

6.1 **ENTENDER o modelo** (`01-entender-o-modelo.md`):
    - O paradigma: modelo massa-mola-amortecedor com estado lento `s=(F_0, δ_emb, δ_creep,
      δ_wear, θ_loose, D)`, [K(s)] dinâmico, 4 mecanismos de perda em paralelo + dano D como
      modulador — e por que NÃO é um fit (as 6 provas, com link p/ concept_not_a_fit).
    - Contabilidade de energia (conservação como invariante de projeto) e two-factor loosening.
    - A tese central do projeto: **formas transferem entre rigs; constantes são por-par/por-rig**
      — como ela foi estabelecida (B/C/A da Fase 1) e como governa a calibração.
    - Tabela de TODAS as constantes ativas com proveniência (medida | âncora de literatura |
      handbook/VDI | fitada — e ONDE cada valor vive: shared/adopted_configs/KB).
    - As limitações L1–L7: o que cada uma era, qual forma a supriu, qual gate a validou.
    - Histórico de falsificações (B1 axial, k_j-scaling, damage-trigger preditivo, δ_t-separator,
      L4 null) — o que foi tentado, por que morreu, e por que isso é força do método (MEM/FAIL2).
6.2 **EXPLICAR o modelo** (`02-explicar-o-modelo.md` — material para terceiros: aula, defesa,
    paper, revisor cético):
    - A narrativa em 3 níveis: elevator (1 parágrafo), 10 minutos (com as 5 figuras-chave),
      seminário completo (roteiro seção-a-seção apontando os docs).
    - As 5 figuras-chave GERADAS DO STORE REAL por script versionado (`scripts/manual_figs.py`):
      anatomia da curva (estágios/joelho/piso), decomposição por mecanismo empilhada, painel de
      validação (202 casos, antes/depois da meta), tornado de sensibilidade (§4.42), mapa
      formas×fontes (que forma fecha que família de dado).
    - FAQ de objeções, cada uma com resposta E evidência citável: "não é overfitting?"
      (parcimônia, identifiabilidade, LOCO, switches fittable=False); "por que N estados?";
      "por que exceções?"; "o que o modelo NÃO cobre?" (honestidade = concept_coverage).
    - Glossário e notação (link p/ concept_glossary; completar termos novos L1–L7).
6.3 **APLICAR o software** (`03-aplicar-o-software.md` — manual do usuário):
    - Instalação, comandos canônicos (run_app, server de calibração, report, explorador).
    - Fluxo completo com telas: launch → wizard → MSD Builder (PropertyInspector) → Solver →
      Results (módulo V2: browser de casos, re-sim, "Abrir no Model/Run").
    - **Como analisar uma JUNTA NOVA passo-a-passo**: inputs mínimos e de onde tirar cada um
      (VDI/Rz p/ emb_depth, bandas do KB, presets adotados por rig via `suggest_overrides`),
      o que os avisos do `check_input` significam, como ler decomposição/estágios/energia.
    - **Como adicionar um PAPER NOVO fim-a-fim**: digitalizar → apparatus_note → caso no
      registry → fit gateado (tripé) → adoção → report. Com os comandos reais de cada passo.
    - Reprodutibilidade (regenerar tudo: store, explorador, figuras do manual) e
      troubleshooting (gotchas reais do CLAUDE.md, ex.: encoding, casos em minutos, force-mode).
    Gate da F6: toda afirmação numérica do manual sai do store/ledger real (nada de número
    solto); figuras por script versionado; todos os links verificados; commit.
6.4 RELATÓRIO EXECUTIVO final para mim: painel por fase; adoções realizadas (cada uma com gate);
    falsificações; exceções propostas/assinadas; apontador para o Manual; o que ficou aberto
    (e.g. experimento-âncora W_conf_ref).

## REGRAS TRANSVERSAIS
- Tripé em todo gate; baseline vigente = o último re-pin do ledger.
- Formas novas SEMPRE default-inertes com bit-identidade testada; switches `fittable=False`.
- Nunca fitar scatter (coerência preditiva antes de promover per-curva).
- Um escritor por vez; sem worktree paralelo durante fases no main; OneDrive: staging explícito.
- A cada fase: se algo contradisser o esperado (ex. conflito de merge não-trivial, gate ambíguo),
  registre e PARE com um resumo do impasse em vez de improvisar.
