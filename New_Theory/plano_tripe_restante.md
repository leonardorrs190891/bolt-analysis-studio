# Plano — o caminho das 29 não-resolvidas para o tripé (ou estatuto)

**2026-08-01** · pedido do professor: *"vamos ver nosso plano para o resto
ficar no tripé"*, após a exclusão temporária da ANCORA_INTERNA (3 ensaios
preservados para nova rodada experimental). Baseline: **tripé 134/201
(67 %) · resolvida/declarada 172/201** · 67 fora = 29 exceções + 9
declaradas + **29 não-resolvidas** (a fila deste plano), fingerprint
`3d432a65c7e8`.

Verdade estrutural que o plano respeita: **o tripé só cresce por física
certa** (adoção gateada); exceção/declaração dão *estatuto*, não acerto.
Cada bloco abaixo diz a rota, o dono e o teto realista.

## Bloco 1 — LIU_2025 ×4 (mae 1,3–1,5× nas amplitudes baixas; sd 1,1–1,6×)

* **Medido hoje**: o par publicado da própria fonte (fig2↔amp0p8, mesma
  condição 0,8 mm) tem piso σ **0,0172** — os misfits (0,0268/0,0396)
  excedem o scatter das gêmeas em 1,6×/2,3× ⇒ **rota F7 NÃO cobre**; é
  forma de verdade (e a dose de incubação compartilhada já foi falsificada
  em grade 12 pontos).
* **Rota**: forma do limiar emergente N₉₅ (P5 do estudo Liu2025: dispara
  10–100× cedo em amplitude baixa). É trabalho de física com âncora rica
  (a fonte tem vidas por curva como input e o par 0,8 mm como régua).
  **Dono: campanha, com PR-3 sua** para a forma. Teto: 4 no tripé.
* ✅ **INSTRUMENTO + FALSIFICAÇÃO executados 2026-07-31 (noite)**
  (`liu2025_n95_resultado.md`, prereg próprio): o N₉₅ do modelo é
  **CONSTANTE (108)** onde o dado varre **850×** (Fig. 4 D-N) — relógio
  de estágio I cego à amplitude (decomposição: 59 % embedding + 41 %
  creep em 0,25 mm). Candidato A (campos existentes, bedding slip-gated
  + t_0) **FALSIFICADO no G1 (1/6)** — o gate tem expoente efetivo ~2–4
  e o dado exige ~11.
* ✅ **PR-3 EXECUTADO 2026-08-01** (`s1_amp_gate_resultado.md`, commit
  `2c5c17c`): forma construída default-inerte (3 campos + testes +
  VarSpecs), **G1 PASSOU 5/6** (relógio acompanha o span de 850× com 3
  números lidos da D-N) — mas **G2/G3 FALHARAM ⇒ INCONCLUSIVO, zero
  adoção**: a D-N e as curvas digitalizadas da MESMA fonte **discordam
  do N₉₅ em 3–5× nas duas direções** — nenhum relógio satisfaz ambas.
  Diagnóstico novo: o ganho em amplitude baixa é real (MAE −61/−67 %) e
  o bloqueio é inconsistência interna do dado publicado.
* ✅ **EMENDA "curvas mandam" EXECUTADA 2026-08-01** (decisão sua em
  sessão): **G1c 6/6** (o gate expressa também a escada das curvas,
  todas dentro de 1,7×) mas **G2c FALHOU com TODAS as 7 curvas piorando**
  — casar o N₉₅ quebra a forma inteira; o dado exige re-tempo COORDENADO
  (estágios I+II) com a amplitude, e um fit conjunto seria ≥5 números em
  7 curvas (tortura de parâmetro, vetada). 3ª falsificação pré-registrada
  do dia na classe "relógio de estágio I" ⇒ requisitos de parada por
  classe em cumprimento. **A fila LIU_2025 fica form-limited com
  diagnóstico completo; rotas restantes são suas**: pergunta aos autores
  ou forma coordenada nova (com o aviso de identificabilidade).

## Bloco 2 — CHU_2026 ×6 (as 3 D0.4 a 3–4,6×; test3/test4/test9)

* **Estado**: TODAS as classes de mecanismo existentes varridas e fechadas
  (`chu_veredicto_completo.md`); a máquina de dano PRODUZ o regime que
  falta (test2 fim 0,16 vs 0,14) mas nenhuma dose única é viável — o
  relógio de dano é monótono na amplitude e o padrão do dado não é.
* **Rota**: (a) **bancada** — Ra por espécime OU 1 réplica em D0.4/D0.5
  (decide regime vs scatter de espécime; pode transformar as 3 D0.4 em
  prova de piso); ou (b) **forma não-monótona** (third-body ejection,
  PR-3). **Dono: professor (bancada/autorização).** Teto: 6 com estatuto,
  1–2 no tripé (test9 está a 1,1–1,2×).

## Bloco 3 — YANG_2019 ×4 (sd 1,5–3,2×; SEM piso) — rota (a) ESGOTADA 2026-07-31

* **Auditoria executada e NEGATIVA** (`yang2019_auditoria_replicas.md`):
  o paper rodou 3 espécimes/amplitude mas publica só MÉDIAS (Tabela 3) e
  1 curva por condição (Fig. 6 = três condições, não réplicas) ⇒ piso não
  medível do publicado; as 4 ficam SEM piso honestamente. Bônus: Tabela 3
  = âncora independente (médias de N a 90/80/70 %) para uso futuro —
  decisão de método na fila do professor.
* **Resta a rota (b)**: forma de espectro/kernel-A (fila antiga) ou
  bancada.

## Bloco 4 — YANG_2023_IJPEM ×3 — ✅ FECHADO SEM O PDF (2026-08-01)

* **Professor decidiu: o PDF não virá.** Análise de substituibilidade
  executada função a função: input-truth já coberta pelo companion
  (correções de 2026-07-28); aparato Junker CONFIRMADO pela Fig. 1 do
  companion (agora NA biblioteca: `yang2025_materials_M8.pdf`, baixado
  via browser+PoW); **curvas NÃO são substituíveis** — verificado no PDF
  que o companion só publica VIDAS (Fig. 9 = scatter vida-vs-vida com
  2 réplicas/caso; um resumo de WebFetch dizia "curvas" e estava ERRADO).
* **As 2 de resolução grossa DECLARADAS** pelo critério pré-registrado
  (`2026-08-01-resolucao-do-dado-prereg.md`, varredura GLOBAL): 0,30 mm
  (mediana |Δdado| 0,180) e 0,35 mm (0,140) — o passo do próprio dado ≥ a
  tolerância inteira. A **0,25 mm (salto 0,08) fica na fila por mérito**,
  como o prereg previu. Reabrem com dado denso.
* Bônus registrado: as 6 vidas multi-parafuso + 12 vidas VAL do companion
  são âncora de VIDA com réplica (classe do instrumento N₉₅) para uso
  futuro.

## Bloco 5 — LU_2024 ×2 (fig14_amp0p5/amp1p0; pernas além do scatter n=2)

* **Rota**: 3ª réplica de bancada (re-mede os pisos n=2 — a mx/σ dessas
  curvas está na fronteira) OU a forma de colapso P6 se um dia valer as 2
  curvas. **Dono: professor (bancada).**

## Bloco 6 — YANG_2021 ×2 (sd 1,8–1,9×) — ✅ EXECUTADO 2026-07-31 (noite)

* **Feito** (`yang2021_replicas_resultado.md`, prereg gates G1–G4): reps
  2–3 digitalizadas (round-trip 1,2 % vs Tabela 3), entraram como casos e
  **AMBAS no tripé por mérito** (MAE 0,0403/0,0209 — modelo-vs-dado ≈
  dado-vs-dado, piso da família 0,028 na janela). Censo 201→**203**,
  tripé 134→**136**.
* **Veredicto da rota F7: FECHADA por medição** — na janela da métrica a
  bancada repete a σ 0,0071 (o scatter grande, 0,079, é todo do colapso
  crack-driven que o trim assinado exclui) ⇒ o σ das 2 da fila é 6,5× o
  ruído do dado: **form-limited de verdade**. Rota restante = forma da
  competição afrouxamento×fadiga (F1 aditivo e fadiga-PIORA já
  falsificados) ou fila honesta.

## Bloco 7 — as unitárias (LIU_2022_RETIGHT ×3 · LI_2022_TRIBOINT ×2 ·
SUN ×1 · CACCESE ×1 · YANG_2023_AME ×1)

* **RETIGHT (1,1–1,2×)**: transporte de estado da cadeia com sinais
  opostos — estrutural; distâncias mínimas sugerem que QUALQUER melhora
  de forma global pode fechá-las de carona. Aguardar as formas dos blocos
  1/2.
* **TRIBOINT (1,1–1,5×)**: curvatura com sinais opostos entre 2 curvas
  (cluster "duas formas") — idem, carona.
* **SUN/CACCESE (únicas)**: sem réplica que ancore; CACCESE rep2 está a
  1,3× do piso da PRÓPRIA réplica (31 % além do scatter) — micro-gap de
  forma de creep; ficam.
* **YANG_2023_AME**: junta CFRP — ✅ **DECLARADA fora de escopo de
  material em 2026-07-31** (aprovação do professor: "concordo" sobre a
  recomendação explícita deste plano; entrada em `_DECLARADAS` com
  cláusula de reabertura se uma forma de membro viscoelástico entrar no
  engine).

## Bloco 8 (NOVO, 2026-08-01) — ROUSSEAU: erratum → recuperação → forma recusada

Não estava no plano original (a fonte tinha 3 exceções assinadas e
parecia fechada). A Rodada 6 reencontrou o PDF oficial e a fonte virou o
bloco mais produtivo do dia:

1. **Erratum** (`rousseau_erratum_resultado.md`): drive do aço 10× errado
   + piso de par FALSO ⇒ 3 exceções retratadas, bloqueio
   `_SEM_FAMILIA_MECANICA`.
2. **Recuperação** (`rousseau_recuperacao_resultado.md`): Fig. 6
   digitalizada (condição inédita) ⇒ **HDPE no TRIPÉ por predição
   zero-refit**; aço re-fitado (1 número) com o **G2 falhado declarado**.
3. **Forma de amplitude RECUSADA** antes de existir
   (`forma-amplitude-rousseau-prereg`): a tabulação mostrou que o dado
   quase não varia com 4× de amplitude — o déficit era de **nível**, e a
   constante que o carrega (`loose_arrest_floor`=0) tem **procedência de
   aparato** (roletes que removem o atrito parasita ⇒ sem
   auto-travamento), não de fit.

**Lição transferível**: a fonte "fechada por exceção" era a que tinha o
maior retorno — porque o que faltava era LER o paper, não modelar. Vale
re-perguntar isso das outras fontes com exceção assinada e PDF na
biblioteca.

## Resumo executivo do plano

| rota | curvas | dono | prazo |
|---|--:|---|---|
| digitalizar réplicas publicadas (YANG_2021; auditar YANG_2019) | até 6 | campanha | dias |
| declarar CFRP fora de escopo | 1 | professor (assinatura) | imediato |
| PDF do YANG_2023_IJPEM | 3 | professor (acesso) | ? |
| bancada: Ra/réplicas CHU · 3ª réplica LU · (âncora interna quando voltar) | 8–11 | professor | semanas |
| formas com âncora (N₉₅ LIU_2025 · dano não-monótono CHU) | 10+carona | campanha + PR-3 | semanas |

**Teto realista sem bancada e sem formas novas: ~172→176/201 resolvidas.**
**Com as duas formas + bancada: o tripé pode passar de 150 e o
resolvido/declarado de 190.** A ordem que recomendo: YANG_2021 (dias,
ferramental pronto) → auditoria YANG_2019 → forma N₉₅ (a mais ancorada)
→ CHU conforme a bancada responder.
