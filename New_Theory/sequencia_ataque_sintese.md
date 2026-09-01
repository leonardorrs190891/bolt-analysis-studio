# Sequência de ataque das abertas (2026-08-19) — 6 alvos, 0 adoções, e UM fenômeno em três fontes

**2026-08-19** · store `7a60cacb72de` intacto, censo **144/205** inalterado ·
tudo só-leitura · mandato: *"inicie o plano de ataque em sequência e loop"*.
Protocolo: `PROMPT_ATACAR_AS_ABERTAS.md` (Grupo A; o Grupo B segue bloqueado
por dado).

## 1. O placar, alvo a alvo

| # | curva | pior perna | veredito | doc |
|---|---|---:|---|---|
| 1 | `yang2021_amp0p6mm_ax8kN_r1` | 1,07× | **sem rota** — 4 fechamentos | `yang2021_r1_sem_rota_resultado.md` |
| 2 | `liu2025_M16_fig2_single` | 1,08× | **sem rota com procedência** — a direção existe (D_on↓ melhora as 3 pernas) e morre no joelho medido (0,89, o mais tardio da fonte) | `liu2025_fig2_forma_rampa_fechada.md` |
| 3–4 | `yang2021_amp1p0` · `amp0p5` | 1,28× · 1,55× | **sem rota determinística** — geometria dos inputs (sinal alterna 3×; réplicas nominais com sinais opostos) | `yang2021_abertas_geometria_dos_inputs.md` |
| 5 | `liu2025_M16_amp0p8` | 1,68× | **INCONCLUSIVO** — ver §3; instrumento não isola a forma | (esta página, §3) |
| 6 | `lu2024_fig20_T10Nm` | 5,03× | já mapeado em 16–17/08: dois defeitos, rotas fechadas (`emb_pressure_exp` reprovou no G1; piso sem lei — dado não-monótono **publicado**) | `lu2024_embedding_pressao_resultado.md` |

**Zero adoções — e zero é o resultado certo:** cada rota morreu por medição com
número, não por desânimo. A regra de parada, medida em 16/08, **continua
disparando** para esta fila; a sequência a **confirmou por extenso** em vez de
assumi-la.

## 2. O fenômeno que apareceu em TRÊS fontes independentes

**Dispersão de ESPÉCIME invadindo a janela da métrica** — sempre com a mesma
anatomia:

| fonte | evidência | tamanho |
|---|---|---|
| `YANG_2021` (0,6 mm/8 kN) | vidas **12400 / 14649 / 16251** entre réplicas; o pré-colapso do espécime 1 invade a janela; réplicas nominais com resíduos de **sinais opostos** (r1 +0,045 · r2 −0,052 · r3 −0,027) | 15–25 % em vida |
| `LIU_2025` (0,8 mm/24 kN) | o par da mesma condição morre em **9870 / 14400** | **46 %** em vida |
| `LU_2024` (fig20) | retenção terminal **não-monótona publicada** (Tabela 9: 0,037–0,309), núcleo travado absoluto variando **45×** | — |

E o ponto estrutural, que nenhuma forma contorna: **o piso de σ por condição é
medido na janela comum, onde os espécimes ainda coexistem no platô — a
dispersão de vida na cauda NÃO entra nele.** Por isso curvas a 1,07–1,68× do
limite estão simultaneamente *acima do piso formal* e *dentro do scatter real
dos espécimes*. O modelo, com uma parametrização por fonte, está **no centro**:
no YANG ele concorda com r2/r3 a σ 0,006–0,007 e "erra" a r1 por 0,027 — mover
o modelo quebraria as duas que fecham.

**Se isto um dia virar régua** (um piso que reconheça dispersão de vida na
cauda), é decisão do professor — três fontes de evidência estão medidas e
citadas. Não proponho a régua: seria eu desenhando a barra que me aprova.

## 3. Alvo 5 (`liu2025_M16_amp0p8`) — INCONCLUSIVO, com um número novo

A hipótese era `D_on` no **joelho medido** do espécime (0,82 contra 0,75
adotado). O instrumento: re-ancorar `fat_C1` por bisseção de simulação a cada
forma. **Ele não serve aqui, e a sanidade o provou:**

- reproduzir o adotado **explícito** (0,75/8/5,22562e32) = **bit-idêntico** ✓;
- re-ancorar a **mesma forma** pela minha bisseção = MAE 0,0393 → **0,1088** ✗.

Causa: a âncora da rota E2 é **analítica** (*"fat_C1 fixados nas contas"*, do
σ_root da Table 2), e a bisseção-de-simulação produz outro relógio (o Goodman
vivo realimenta σ_ar). Como o rider de 07-28 removeu o trim, a amp0p8 é
pontuada **com o colapso inteiro na janela** — e aí vale o número novo:

> **C1 −6,5 % ⇒ MAE 3,4× pior (0,039 → 0,134), medido com sanidade
> bit-a-bit.** O σ de 0,0419 desta curva é o resíduo *depois* de alinhar o
> colapso ao fio; qualquer perturbação de (forma, relógio) o desalinha.

⇒ testar `D_on`-no-joelho de verdade exigiria reproduzir a conta analítica do
E2 — e o teto do ganho é o próprio 0,0419 do adotado, que já é o mínimo da
vizinhança medida. Ramo **INCONCLUSIVO** (o teste não testou a forma isolada;
a lição de 2026-07-30 sobre ramos de prereg, aplicada a uma sonda). Não conta
para o requisito (b) de nenhuma parada — e não precisa: a curva já está em
`classe_parada`.

## 4. Gotchas novos que a sequência pagou

1. **Δ=0 exige conferir o RAMO, não só os companheiros** — o rótulo
   `rotational_loosening` da decomposição é do *mecanismo*; em disp-mode+stick a
   lei ativa é o **gth**, e as alavancas rotacionais clássicas
   (`eta_loose`, `k_j_init`+`kj_mode`, `phi_load_dep`, `I_theta`) nunca são
   lidas.
2. **`F_amp` é estruturalmente inerte em fonte transversal-pura**
   (θ=90° ⇒ cos=0 ⇒ guard 1,0) — medido com gancho validando o valor recebido.
   No YANG_2021 o registro carrega `F_amp=0,4·F₀` com proveniência
   *"Pai&Hess"* enquanto o paper publica 2–11,2 kN por ensaio: proveniência
   errada, efeito **zero** (correção documental; fila de dado). E a excitação
   **composta** (axial 90° defasada) é forma faltante declarável — que **não**
   destravaria as abertas (réplicas da mesma célula têm sinais opostos).
3. **Âncora analítica ≠ âncora de simulação** quando o Goodman está vivo — e
   com colapso na janela, 7 % de relógio custam 3,4× de MAE.

## 5. O que resta na fila depois desta sequência

- **Grupo A: esgotado.** As 6 têm veredito individual com número.
- **Grupo B (15): segue bloqueado por dado** — a ação nomeada é a réplica no
  `ICMEZ_2025` (Fase 3 do plano, decisão do professor).
- **Correção documental**: proveniência do `F_amp` do YANG_2021 (Δ=0, higiene).
- **A decisão de régua do §2**, se o professor quiser tomá-la.
