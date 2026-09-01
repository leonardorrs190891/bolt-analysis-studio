# Prereg — CHU_2026: inputs de artigo + calibração de GRUPO (B+D assinados)

**2026-08-13 19:0x, mandato "assino tudo, continue o loop sem parar".**
Estado: 3/9 no tripé (test1 calibrada 15 chaves; test5/6 em defaults), 6 fora.
Achado-base `03c471b`: 8 de 9 rodam em DEFAULTS; classe 8 GROSS + 1 PARCIAL
(test1); k_wear_spec per-fonte FALSIFICADO (classe mista).

## Correções de INPUT (verdade de artigo, prov=paper — não são fit)

- `rz`: `Rz10-40 assumed` → dos Ra do artigo (nota chu2026ti.md): tests 1–8
  Ra 0,4 µm ⇒ Rz ≈ 1,6 µm; test9 Ra 1,6 µm ⇒ Rz ≈ 6,4 µm (convenção Rz≈4·Ra).
- `mu_thread`: 0,15 assumed → **0,06** (paper: µ_thread ≈ 0,05–0,07, não
  varrido). `mu_bearing` segue 0,15 salvo banda em contrário.

## Desenho da calibração (emenda de parcimônia da assinatura D)

- **test1 (PARCIAL) INTOCADA** — bit-idêntica (gate).
- **UM conjunto compartilhado** para o sub-grupo GROSS (test2..test9, 8
  curvas), inputs por curva (D, F₀, rz) do artigo. Canais candidatos (≤3
  fitados, grades fechadas): `k_wear_spec` (agora legítimo: sub-grupo
  homogêneo de classe E modo) · `tr_loose_gain` · `N_emb`/`emb_um` via VDI é
  INPUT (não fitado).

## Gates

- G1: correções de input aplicadas ANTES de qualquer fit; baseline medido e
  registrado (a piora prevista das D=1,0 é aceita NESTA fase — a
  calibração vem depois; o gate final é o conjunto).
- G2: estado final — nenhuma curva HOJE no tripé sai (test1/5/6); test1
  bit-idêntica.
- G3: censo da fonte só cresce; global nenhum caso pior >+0,01.
- G4: ≤3 constantes fitadas no sub-grupo; procedência completa (catraca
  2e71dd0); âncora da Tabela 1 (ciclos até 0,9·F₀) reportada por curva como
  verificação INDEPENDENTE (informacional nesta rodada).
- FALHA: se o conjunto compartilhado não fechar ≥2 das 6 fora sem violar
  G2/G3, declarar e voltar o input-fix ao estado de dívida documentada.

---

## RODADA 1 (2026-08-13 19:2x) — resultados

**G1 executado em CÓPIA** (inputs.py revertido até gates verdes — um re-stamp
alheio não pode aterrissar a regressão do paradoxo sem a calibração):
- test1 bit-idêntica ✓ (grupo próprio vence o matcher).
- test3 0,1381→**0,0813** (a previsão do achado 03c471b) · test9 mx melhora.
- test5/6 pioram como previsto (0,040→0,075 · 0,027→0,048) — G2 exige
  reconquistá-las.
- Entry SOURCE_INPUTS a re-aplicar na adoção:
  `"CHU_2026": dict(grip=None, mu=(0.15,"assumed"), rz="Rz<4")` + cfg
  `mu_thread=0.06 (paper)` + per_case `test9 emb_um=9.5 (Ra 1,6=>Rz<10)`.

**FALSIFICADO nesta rodada:** `k_wear_spec` UNIFORME sobre os inputs
corrigidos (8 doses ×2 tr_loose_gain): a menor dose (1e-13) já troca a via
legada não-linear por linear — test5 fecha (0,032/0,047/0,011) mas test3
explode (0,081→0,270); doses maiores afundam tudo (mae médio 0,32–0,57).
⚠️ Distinto da falsificação pré-inputs (03c471b): esta vale PARA os inputs
novos. A anatomia manda: viés POSITIVO com ρ(res,N) 0,43–0,99 e wear
77–87 % ⇒ falta perda, mas com ESCALA DE AMPLITUDE não-linear — candidatos
da rodada 2: `flank_amp_exp` (Liu2020 1,5–1,6, já no engine) sobre a via
legada, e/ou `N_wear_run`/`k_wear_running`.

---

## LEITURA DO PAPER (pedido do professor, 2026-08-13) — verdades estruturais

PDF lido na íntegra (Tribology International 223 (2026) 112193, Chu et al.):

| verdade | valor | consequência p/ o modelo |
|---|---|---|
| Materiais | bolt GH159; porca 12-pt + placa GH4169; **rosca PRATEADA**; sem arruela | µ_thread baixo é físico, não anômalo |
| µ_thread | handbook 0,08; FE 0,05; faixa 0,05–0,07 (slope T–F ±10 %) | `mu_thread=0,06 (paper)` confirmado |
| **µ_plate** | FE/handbook **0,2**; MEDIDO por ciclo (µ=(R_max−R_min)/…); **sobe monotonicamente durante o afrouxamento e estabiliza quando ele cessa**; F₀ maior retarda a subida | `mu_bearing≈0,2 (paper)` e **k_dmg_mu NEGATIVO** (µ sobe com D) — sinal por par tribológico; a lei do aço (µ cai) não vale em GH |
| Limiar crítico | **D_cr/P ≈ 0,24** ⇒ P=1,25 mm; δ_t(49 kN)≈0,3 mm | âncora INDEPENDENTE de µ_b/k_tr: k_tr ≈ µ_b·F₀/δ_t ≈ 3,3e7 N/m com µ_b=0,2 |
| Geometria | d_w=17 mm, d_h=10,5 mm (p_max 520 MPa @73 kN); placa E=189 GPa | `d_washer_mm/d_hole_mm/E` viram inputs de paper |
| Âncoras | Tabela 1: ciclos até 0,9F₀ por teste (278/325/406/72/…) | verificação independente por curva (G4) |

### RODADA 2 (a executar) — config física completa do paper

Inputs (prov=paper): mu_thread 0,06 · mu_bearing 0,2 · d_w/d_h 17/10,5 ·
E 189 GPa · rz "Rz<4" (Ra 0,4; test9 Rz<10) · P=1,25 (conferir registry).
Forma: **k_dmg_mu negativo** (µ sobe com D — c_D/W_ref/k_dmg_mu do grupo,
≤3 fitados) — o mecanismo que o paper NOMEIA como regulador do longo prazo.
Gates: os do prereg (G2 test1 bit-id + test5/6 reconquistadas; G3 censo só
cresce; G4 âncoras da Tabela 1 reportadas).

### Rodada 2 — grade DECLARADA antes da medição (2026-08-13, pós-leitura do paper)

Base: `adopted_CHU0.json` (inputs corrigidos). Grupo `CHU_2026` (test2..test9);
`CHU_2026_test1` intocado. Candidatos (constantes COMPARTILHADAS do grupo, formas
que pós-datam a prova de lei de 2026-07-28 — o objeto da falsificação mudou):

- **Estágio A (desaceleração no canal dominante):** `k_wear_running` ∈ {3, 6, 12}
  × `N_wear_run` ∈ {60, 150, 300} — kernel running-in Archard (Zhang2019 N^0.53),
  front-loaded: ataca o viés positivo + rampa ρ(res,N)>0 medidos na rodada 1.
- **Estágio B (diferenciação de amplitude):** `k_ratchet` ∈ {0.005, 0.02, 0.05}
  × `loose_amp_exp` ∈ {1.0, 3.8} — ratchet cinemático (PR-21, âncora IJPEM δ^−3.8);
  responde à não-monotonicidade N₉₀ (278/325/406/72) que lei uniforme não tem.
- **Estágio C:** cruzamento só dos top-2 de cada estágio.

Gates: os G1–G4 já congelados neste prereg (inalterados). Leitura por célula:
census tripé (MAE≤0.05 · mx≤0.10 · σ≤limite_sres da fonte) nos 8 + G2 (test5/6
≥ store) + soma global. NÃO re-trilhar: trio PR-38 estendido (§4 do estudo),
µ-schedule prescrito (§7a), lei energética µ-acoplada (§7b), k_wear uniforme
(rodada 1), k_dmg_all cru (PR-3: +53% no CHU).

### Rodada 2 — RESULTADO (2026-08-13): as duas famílias FALSIFICADAS em todas as doses

Baseline CHU0 re-medido: **~neutro vs store** (|ΔMAE|máx 0,0015; census 2/8 =
test5+test6; σ_lim fonte 0,0507). ⚠️ Os números da rodada 1 (test3 0,081 etc.)
vieram de um estado de arquivo mais agressivo que o CHU0 atual não reproduz —
baseline vigente é o desta medição.

- **Estágio A (running-in):** menor dose (k_run=3, N_run=60) já derruba census
  2/8→0/8 (test5 0,040→0,055; test6 0,027→0,087) e o gradiente piora
  monotonicamente até +0,50 de MAE. FALSIFICADO (G2 inatingível na família).
- **Estágio B (ratchet):** k_ratchet=0,005 destrói (MAE 0,44–0,71, mx≈1,0) —
  na escala de gross-slip do rig (slip 0,3–0,9 mm), dθ=k·4·slip/r drena
  ~10²–10³ N/ciclo. FALSIFICADO em toda a grade; estágio C cancelado (não há
  top-2 para cruzar).

**Leitura estrutural (dose-resposta, não ajuste):** o modelo perde RÁPIDO
demais cedo (qualquer forma front-loaded piora já na menor dose) e DEVAGAR
demais tarde (r@fim ≈ +0,5 nas colapsantes). O defeito é a FASE do colapso
(S deslocado), não a magnitude — consistente com o veredicto do estudo
2026-07-28 ("estrutura temporal do kernel").

### Rodada 3 — grade DECLARADA antes da medição (mesmo dia)

Par supressão-cedo + chute-tarde (as duas formas construídas para esta classe,
ambas default-inertes; k_dmg_all cru NÃO re-testado — já falsificado por perfil):

- `slip_onset_W` ∈ {500, 1500, 4000} J (incubação Hill sobre W_slip_acc, gate
  em wear dF₀ E loosening — os canais do CHU; escala: W_slip/ciclo ≈ 9–27 J).
- × `k_late_amp` ∈ {0, 2, 5, 10} × `crash_trigger_frac` ∈ {0.7, 0.85}
  (amplificador tardio com interruptor Hill em F₀/F₀_init — emenda PR-3).

Gates G1–G4 congelados inalterados. Mesma leitura por célula (census, G2
test5/6, pior ΔMAE vs store).

### Rodada 3 — RESULTADO (2026-08-13): FALSIFICADA para constantes compartilhadas; capacidade POR CURVA provada

21 células medidas (`chu_r3.txt`). Achados:

- `slip_onset_W=4000` puro: **test3 PASSA o tripé** (0,1381→0,0402/0,0666/0,0264)
  — 1ª captura de curva distante do CHU na campanha. Custa test5 (mx 0,204) e
  test9 (+0,064): G2 quebra.
- `W=1500 · k_late=2 · trigger=0,7`: **test5 0,0100/0,0207/0,0115** (de 0,0402)
  — e test3 explode (0,3056). `W=4000 · k=5`: test2 0,1543→0,0821; test8 melhora
  com `k=2` (0,1231). `trigger=0,85` piora tudo (chuta cedo demais).
- **Ótimos por curva CONFLITAM estruturalmente:** o W* puro que preserva test5
  (mx<0,10 exige W≲350 J) e o que fecha test3 (4000 J) são **disjuntos por 10×**;
  o chute tardio que fecha test5 destrói test3. Não existe célula compartilhada
  na grade — census máx. 1/8 em toda parte.

**Veredicto (ramo FALHA):** 4 famílias falsificadas hoje (k_wear uniforme,
running-in, ratchet, onset×chute-tardio) SOBRE a prova em nível de lei de
2026-07-28 — todas com formas que pós-datam aquele estudo. A capacidade por
curva existe (2 constantes fecham qualquer uma), mas as constantes **não
transferem dentro da própria fonte**: onset e chute são função explícita de
(D, F₀), que é exatamente a lei M⁻=(F₀/ξ)^1,85·(N^1,65+η) do paper. E a M⁻
publicada **não tem eixo de amplitude** (fitada só em D=1 mm, µ=0,2) — nem a
instanciação fiel do candidato do próprio autor fecharia a varredura de D.
CHU_2026 test2/3/4/7/8/9 permanecem **form-limited**; teto da fonte sob formas
atuais = **3/9** (test1 + test5 + test6). Correções de input (mu_thread 0,06;
test9 emb 9,5 µm) ficam registradas: ~neutras em métrica (|Δ|máx 0,0015),
adoção isolada só mexeria fingerprint sem ganho de gate (mesma regra do estudo
§5). Proposta de exceção formal → DECISOES_PENDENTES.

---

## RODADA 4 (2026-08-14, mandato renovado do professor) — canal M⁻ do próprio paper; ESTÁGIO 0 = teto de autoridade, DECLARADO ANTES

Única rota não-falsificada (rodadas 1–3 + estudo §7/§8): instanciar o canal de
acumulação de torque assimétrico do paper com µ_plate(N) MEDIDO como input.
Antes de engine: **sonda de teto de autoridade** (precedente D-L) — a lei
publicada M⁻=(F₀/ξ)^a·(N^b+η) (ξ=12,39 kN · a=1,85 · b=1,65 · η=30, FEM do
paper a µ=0,2/D=1 mm) alimentada com os µ(N) digitalizados
(`chu2026ti_fig5_muplate_test{1,2,4,7,8}.csv`) contra o T_res do engine
(µ_th·F₀·d₂/(2cosα) + µ_pl(N)·F₀·r_b; MJ10: d₂=9,188 mm, r_b=(17+10,5)/4 mm).

**Predição-alvo (gate G0, congelado):** o cruzamento M⁻(N)=T_res(N) tem de
REPRODUZIR A ORDENAÇÃO dos N₉₀ da Tabela 1 no conjunto com µ medido
{test2: 278 · test4: 406 · test7: 1050 · test8: 936} **e** manter test1
(D=0,3, abaixo do limiar) sem cruzamento na janela de 2500 ciclos. Duas
estruturas testadas (a a posição do µ na lei é ambígua no paper): (i) µ só no
T_res; (ii) µ multiplicando também o M⁻. Tolerância de razão: fator ≤2 nas
razões par-a-par (o scatter declarado do rig é 25%; 2× é generoso de
propósito — reprovar aqui é reprovar com folga).

**Ramos:** G0 PASSA em (i) ou (ii) ⇒ construir a forma default-inerte
(SlowState acumulador + 1 constante compartilhada fitada k_asym; ξ/a/b/η
prov=paper) e grade sob os gates G1–G4 já congelados. G0 FALHA nas duas ⇒
**capstone do dossiê de exceção**: nem a lei quantitativa do próprio autor,
com o µ medido do próprio ensaio, ordena as vidas publicadas — form-limited
com prova de 5 degraus; nenhuma instanciação nossa é tentada.

### RODADA 4 — RESULTADO (2026-08-14): G0 FALHA nas DUAS estruturas; ramo capstone

Sonda `chu_r4_teto.py` (numpy puro, µ dos 5 CSVs digitalizados, Tabela 1):

| teste | F₀ | previsto (i) | previsto (ii) | dado N₉₀ |
|---|---|---|---|---|
| 1 (D=0,3) | 49 kN | **cruza 159** | **cruza 219** | sem queda (2500) |
| 2 | 49 kN | 170 | 215 | 278 |
| 4 | 49 kN | 183 | 211 | 406 |
| 7 | 61 kN | 142 | 197 | **1050** |
| 8 | 73 kN | 123 | 184 | **936** |

Três falhas independentes: **ordenação invertida** ([8,7,2,4] vs [2,4,8,7] —
M⁻∝F₀^1,85 vence T_res∝F₀ ⇒ a lei faz F₀ alto afrouxar ANTES, o contrário do
ensaio do próprio paper); **razões par-a-par até 4,65×** (gate 2×); **test1
cruza** onde o dado é plano. Insensível à unidade (N·mm↔N·m = fator 66×
uniforme, ordenação intacta; em N·m NINGUÉM cruza na janela — falha na outra
direção) e a µ_th 0,05↔0,06. A falha é ESTRUTURAL: a lei publicada não carrega
D (limiar) nem a mediação do F₀ pelo µ(N) — que o próprio paper declara ser o
mecanismo ("the effect of initial preload... involves its influence on the
nut-plate COF"; o FEM roda a µ fixo).

**Ramo capstone aplicado (nenhuma instanciação tentada): a prova da exceção
vira 5 degraus** — (1) µ-livre não reproduz; (2) µ medido prescrito ≈ inerte;
(3) lei de wear µ-acoplada morre na âncora; (4) 4 famílias estado-dirigidas
falsificadas em grade (rodadas 1–3); (5) **a lei quantitativa do PRÓPRIO
AUTOR, alimentada com o µ MEDIDO do próprio ensaio, inverte a ordenação das
vidas publicadas, erra razões por até 4,65× e viola o próprio limiar D_cr**.
Teto da fonte confirmado: 3/9. A proposta de exceção (DECISOES 2026-08-13)
ganha este capstone.
