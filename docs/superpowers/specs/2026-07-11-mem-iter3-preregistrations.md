# MEM Iteração 3 — Pré-registros de Falsificação

**Data:** 2026-07-11 · **Regra:** gates escritos ANTES de qualquer
implementação/fit (METHODOLOGY §1 Etapa 2.4). Nenhum número abaixo pode ser
ajustado depois de rodar — se o gate falhar, falhou, e a falha é registrada
no MODEL_LEGITIMACY §4.x. Baseline de referência: ledger #35 (mediana
canônica 0.1392; n=114 comparáveis).

---

## PR-1 — Colapso HV dirigido por dano de asperezas (Karlsen 2022)

**Motivação (iter.2):** com o C_creep físico do par (1e-12, medido no branch
travado Vibralock), nenhum c_bend reproduz o colapso HV (melhor 0.127 vs
0.094 do statu quo). O statu quo usa C_creep da âncora interna 1.87e-11 (par ERRADO, 19×) —
um proxy que absorve outro mecanismo. O paper aponta o mecanismo: "immediate
reduction of asperities … **not creep**".

**Hipótese H1:** no branch HV, a perda catastrófica (vida 195–480 ciclos,
queda quase-linear sem platô) é dominada pela variável de dano `D` crescendo
do trabalho de slip (modulando µ_bearing e amplificando wear), não por creep.

**Protocolo (pré-registrado):**
1. Fixar `C_creep = 1e-12` (constante do par, classe fitado-this-rig/par,
   medida na iter.1) — NÃO é livre.
2. Ativar dano no grupo `KARLSEN_2022` (HV): partir dos starters físicos
   documentados (`k_dmg_mu=1, k_dmg_wear=4, W_ref=1e4`); **máximo 2
   constantes livres** (`c_D` e, se necessário, `W_ref`), fit CONJUNTO nas 7
   curvas HV (nunca per-curva). `dmg_gross_exp` só se herdado de valor já
   adotado (Bauer §4.33), não refitado aqui.
3. LOCO interno: refit com 5 curvas, predizer as 2 excluídas.

**GATE (todos os critérios, avaliados exatamente como escritos):**
- (a) mediana HV ≤ 0.094 (não pior que o proxy de creep);
- (b) branch Vibralock INTOCADO: mediana ≤ 0.015;
- (c) caráter do colapso reproduzido: vida predita (ciclo em que F/F₀ cruza
  0.2) dentro de 2× da observada em ≥ 5 das 7 curvas;
- (d) LOCO: mediana das 2 curvas preditas ≤ 0.12.

**Interpretação pré-comprometida:** PASSA → promover grupo HV com dano +
C_creep do par (consistência §4.7 restaurada no rig inteiro); registrar §4.x.
FALHA → colapso HV exige forma além de D (ex. back-off rotacional
catastrófico); manter statu quo, registrar a falsificação.

---

## PR-2 — Caminho de creep estático no runner (Li2022 marstruc)

**Motivação (iter.1/2):** família creep a 0.649 com a âncora DO PAR
(9.9e-13); grip de paper PIORA (0.85) — evidência de que o erro é o CAMINHO
(runner genérico com pseudo-ciclos + mecanismos transversais residuais), não
constante. O harness da âncora (Fase 1C, `anchor_creep.py`) reproduziu estas
mesmas curvas com residual de conservação ~3e-4.

**Hipótese H2:** reproduzindo no runner o caminho do harness da âncora
(família creep = modo estático: geometria de paper M16×80 / E=193 GPa /
L=20 mm; só creep+embedding ativos — wear/loosening/conformação inertes;
dt = 60 s por passo), as curvas fecham SEM refit de C_creep.

**Protocolo:** implementar o modo estático como ramo da família `creep` no
runner (default-inerte para as demais famílias); comparar curva a curva
contra o harness da âncora.

**GATE:**
- (a) mediana marstruc ≤ 0.10 com `C_creep = 9.917e-13` (âncora, SEM refit);
- (b) desvio runner-vs-harness < 0.01 em cada curva (mesma física, dois
  códigos);
- (c) nenhuma outra família muda (bit-idêntico fora de creep).

**Interpretação:** PASSA → família creep ganha caminho documentado (leitura
de harness, não fit); âncora §4.7 vira consumível pelo canônico. FALHA (em
especial se exigir C_creep > 2× fora do IC da âncora) → âncora e engine
discordam: reabrir a Fase 1C antes de qualquer promoção.

---

## PR-3 — Forma do protocolo composto (Yang 2021, 2 estágios)

**Motivação (iter.2):** F_amp real do protocolo é INERTE em disp-mode
(0.6760 → 0.6771) — falsificação de que o canal axial simultâneo esteja
representado. Fonte a 0.65 e fora de alcance de qualquer constante.

**Hipótese H3:** a excitação composta (δ transversal + F axial, 90° de fase)
adiciona perda dependente da amplitude AXIAL simultânea — modulação do
preload efetivo durante o slip (µ·N(t) variável no ciclo) — que nenhuma
constante atual representa (∂fim/∂F_ax ≡ 0 no modelo atual).

**Estágio 1 (leitura do dado, SEM mexer no modelo):** medir no dado a
ordenação e o gradiente ∂(vida ou fim)/∂F_ax nas 5 curvas ax2–ax11.2 kN
(controlando amplitude transversal). Registrar o número ANTES do estágio 2.
Se o dado NÃO mostrar dependência de F_ax → H3 morre aqui (registrar; a
fonte vira caso de nível/trim, não forma).

**Estágio 2 (só se E1 confirmar):** implementar modulação default-inerte
(campo novo, default 0 = comportamento atual bit-idêntico; ex.
`ax_mod_amp`), predição-primeiro com F_ax do protocolo e ZERO fit novo.
GATE: (a) reproduz o SINAL e ≥ 50% da magnitude do gradiente medido no E1;
(b) mediana da fonte ≤ 0.45 (de 0.65) sem piorar nenhuma outra fonte
> 0.005; (c) cauda de fratura excluída da métrica por trim pré-registrado no
ponto de fratura declarado (nota de aparato: ensaios até falha do parafuso),
com o ciclo de trim documentado por curva ANTES do fit.

**Interpretação:** E1 nega → registrar e reclassificar a fonte. E2 falha →
protocolo composto permanece out-of-model declarado; candidato a sair do
conjunto comparável (mesma regra aplicada hoje aos Sandia).

---

## Ordem de execução e orçamento

PR-2 primeiro (menor risco, caminho já validado no harness), PR-1 em seguida
(2 constantes, gate duplo), PR-3 por último (2 estágios, toca o engine).
Cada PR = commits separados, medição gateada, ledger próprio. Nenhum PR
altera constantes de outras fontes.


---

## RESULTADOS (registrados na execução, 2026-07-11)

- **PR-2: PASSOU** (ledger #36) — mediana marstruc 0.0034 (≤0.10) com âncora
  SEM refit; desvio runner-vs-harness 2.1e-4 (<0.01); bit-idêntico fora.
  H2 confirmada: era o caminho, não a constante.
- **PR-1: PASSOU** (ledger #37) — (a) HV 0.061 (≤0.094); (b) vibralock 0.0101
  (≤0.015); (c) vidas 7/7 dentro de 2× (195→195, 230→230, 340→340);
  (d) LOCO 0.053 (≤0.12). c_D=0.3 única livre; starters não fitados.
  H1 (a do paper: "not creep") confirmada.
- **PR-3: H3 MORREU NO ESTÁGIO 1** (leitura do dado, engine intocado):
  vida50 = {27800, 12400, 14700, 5700, 3250} p/ (δ,F_ax) = (0.5,8), (0.6,8),
  (0.7,11.2), (0.8,6), (1.0,2). Expoente de F_ax INSTÁVEL EM SINAL: +0.29 no
  log-log conjunto vs −0.30 com b_δ fixado no par isolado ax8kN
  (b_δ = −4.43); magnitude ≪ efeito do δ; desenho confundido (δ e F_ax
  covariam) com n=5 e scatter de ~2× entre repetições. Pela regra
  pré-comprometida: SEM forma nova — a fonte é reclassificada como
  nível/trim (c_bend nunca fitado + trim de fratura documentado).


---

## Análise pós-iteração (pergunta do professor, 2026-07-11): rigidez das bancadas

**Pergunta:** "está considerando que as bancadas dos artigos podem ter rigidez
maior ou menor em média?"

**Resposta medida:** sim, POR BANCADA (c_bend × flexão do parafuso = único DOF
transversal), mas de forma cega. A rigidez de caminho implícita nos c_bend
adotados: BAUER 2.1e7 · ICMEZ 1.0e7 · KARLSEN 4.1e7 · LIU_2022 5.1e6 ·
LIU_2025 3.6e8 · LU 1.6e7 · ROUSSEAU 2.6e6 · âncora interna 8.3e6 · YANG_2019 4.2e6 ·
YANG_2021 3.3e5 · YANG_2023 9.8e5 [N/m] — faixa de ~1000×, mediana 8.3e6.

**Três achados:**
1. O default c_bend=1.0 está CENTRADO: a mediana entre bancadas ≈ flexão pura
   do parafuso — a "média" está bem posta; o espalhamento per-rig é o sinal
   real (bancadas industriais pesadas no topo, fixtures acadêmicas leves na
   base — plausível).
2. **Saturação nos extremos**: Yang2021 tem banda insensível 0.02–0.15
   (limite MOLE: slip dominado pela complacência); Liu2025 c_bend=50
   provavelmente satura no limite RÍGIDO (slip ≈ δ p/ qualquer c_bend alto —
   verificar e registrar a banda). Fora da janela ~µF₀/δ, o dado só informa
   "mais rígida que X" ou "mais mole que Y" — as bandas devem constar na
   proveniência.
3. **c_bend é um absorvedor cego**: captura fixture+placas+célula+parafuso
   sem decomposição, e nunca foi confrontado com as descrições dos rigs.

**Alavanca aberta (iter.4 — upgrade de procedência):** classificar as
bancadas pelas notas de aparato (industrial-pesada / média / acadêmica-leve)
e testar correlação com o k_tr implícito; se correlacionar, c_bend vira
INPUT por classe de bancada (como Rz p/ embedding), com o fit per-rig só
como refinamento — menos um DOF cego, e a pergunta "maior ou menor que a
média" ganha resposta a priori, antes de fitar.
