# Prereg — YANG_2019 até o tripé (3 trilhos, gates IMUTÁVEIS)

**2026-08-10, sessão de docs sob mandato do professor** (“deep work… in loop,
non-stop until all cases are in tripe”). Estado de partida (store
`e01d597c5037`): **1/5 no tripé** (`amp0p6_10Hz`). Limite σ da fonte = 0,025
(global; a fonte não tem piso medível — auditoria B3, rota (a) esgotada).

Diagnóstico herdado da campanha (não re-descoberto): F6 ② (2 metric-limited
terminais, prova ±3 % N ⇒ 0,21/0,26 em r), `karlsen_yang2019_diagnostico.md`
§2a (limiar graduado) e §2b (carry-over de história). A classe “aceleração
tardia” está **ENCERRADA** (`aceleracao_tardia_classe.md`) — nenhum trilho
abaixo é alavanca de fim de curva; os trims são a saída sancionada para
colapso terminal.

## T1 — trims F6 ② (`amp0p6_5Hz`, `varamp_small_to_large`)

Janela por **regra declarada** (medida ANTES deste prereg, congelada aqui):
colapso terminal = o **sufixo contíguo** de passos com |inclinação local| >
5× a mediana das inclinações da curva; a janela vai até o ponto anterior ao
início do sufixo. Medido: `small_to_large` sufixo começa em N=3700
(7,5×/25,3×/213,8×) ⇒ **trim_n_max=3700**; `amp0p6_5Hz` sufixo começa em
N=4800 (8,7×/29,9×/49,8×) ⇒ **trim_n_max=4800**. (O degrau 0→200 da
`amp0p6_5Hz`, 6,0×, não é sufixo terminal — excluído por construção.)

- G1-T1: janelas exatamente as acima (nenhum ajuste pós-medição).
- G2-T1: a curva trimada fecha o TRIPÉ inteiro na própria janela (3 pernas).
  Se não fechar, o trim NÃO é adotado para aquela curva.
- G3-T1: as 3 curvas não tocadas da fonte bit-idênticas (per_case por token).
- G4-T1: prov registra F6 ② + a regra do sufixo + assinatura por delegação.

## T2 — carry-over de história (`varamp_large_to_small`)

Desenho §2b: **transferência intra-fonte**. Fit do trio de dano
(`c_D, W_ref, k_dmg_wear`) SÓ na `small_to_large` (janela trimada do T1);
`large_to_small` é **held-out zero-refit**.

- G1-T2: o fit não lê a `large_to_small` (split mecânico).
- G2-T2: `large_to_small` zero-refit entra no tripé (3 pernas).
- G3-T2: `small_to_large` trimada continua no tripé com o trio fitado.
- G4-T2: `amp0p4_5Hz`/`amp0p6_5Hz`/`amp0p6_10Hz` não pioram > +0,01 em
  nenhuma perna (o trio entra só no grupo varamp se G4 falhar no grupo fixo).
- Ramo INCONCLUSIVO declarado: se o fit degenerar (trio no bound ou
  σ_fit > σ_atual na própria small_to_large), o T2 é INCONCLUSIVO, não
  falsificado.

## T3 — limiar graduado (`amp0p4_5Hz`)

Candidato §2a consolidado (cross-rig com Yang2023 fica para a campanha; aqui
só per-rig). Alavanca: `s1_amp_gate_dref/p/floor` (PR-3, default-inerte,
conservação intacta) e/ou `loose_rate_mode="graded_scrit"`.

- G1-T3: sonda de 2 pontos ANTES de qualquer bisseção (direção da
  monotonicidade); n_cap = n_max do store (10 000) nas DUAS pontas.
- G2-T3: `amp0p4_5Hz` entra no tripé (3 pernas).
- G3-T3: as outras 4 (com T1/T2 aplicados) não pioram > +0,01 em nenhuma
  perna.
- G4-T3: no máximo **2 números fitados** neste trilho; procedência declarada
  (fitado-this-rig); se precisar de mais, o trilho para e é declarado.
- Ramo INCONCLUSIVO: se a alavanca for inerte no regime (Δ<0,001 nos 2
  pontos), declarar inerte — não escalar para outra alavanca sem novo prereg.

## Adoção e contagem

Ordem: T1 → T2 → T3, cada um medido em CÓPIA (`BAS_ADOPTED_CONFIGS`), adoção
real single-writer no arquivo canônico SÓ com os gates do trilho verdes.
Re-stamp uniforme do store (batch 202 + re-sim direta do
`exemplo_m12_sintetico`) UMA vez ao final, depois report/explorador/export.
Curva que falhar seu gate fica como está e a falha é declarada — o mandato é
“até o tripé”, mas gate reprovado não vira adoção.

A `amp0p6_5Hz` está DECLARADA (camada 2): se G2-T1 passar, a declaração é
RETIRADA no mesmo commit (métrica passa a decidir a curva).

Assinaturas deste prereg: **por delegação** (mandato de 2026-08-10, “assine
automaticamente” reafirmado por “non-stop until all cases are in tripe”),
com escopo já ratificado em 2026-08-07 18:03 e registrado em
`New_Theory/loop_24h_2026-08-07.md`.

---

## RODADA 2 (mesma sessão, gates congelados ANTES da execução)

**Resultados da rodada 1, para o registro:** T1 sozinho não fecha G2-T1
(σ 0,0347/0,0477). T2 completo com mínimo interior: fit σ=0,0297
(c_D=0,1 · W_ref=2250 · k_dmg_wear=32), held-out 0,0305/0,0633/0,0362 —
todas as pernas melhoram, σ não fecha. T3 FALHA declarada: `s1_amp_gate`
move MAE e piora σ; `graded_scrit` quebra o grupo (10Hz σ 0,0228→0,21+).

### T4 — trio de dano no grupo FIXO (alvo: `amp0p6_5Hz` trimada)

- G1-T4: fit (grade) SÓ na `amp0p6_5Hz` com trim 4800; grade fechada até
  mínimo interior ou saturação declarada.
- G2-T4: `amp0p6_5Hz` entra no tripé (3 pernas, janela trimada).
- G3-T4: `amp0p6_10Hz` PERMANECE no tripé (3 pernas) — não basta "não piorar".
- G4-T4: `amp0p4_5Hz` não piora > +0,01 em nenhuma perna.

### Regra de adoção da janela (declarada agora)

Independente de G2s: o MELHOR estado combinado medido (trims + trios) é
adotado sob o gate PADRÃO PR-37′ (nenhum caso pior +0,01; mediana da fonte
−30% ou ≤0,05) — melhorias reais não ficam na cópia. Curva que não fechar o
tripé fica declarada com o número e a perna que resta.

---

## RODADA 3 — T5: expoente de dwell do dano (1 número, separa 5Hz de 10Hz)

**T4 para o registro:** G2-T4 passa (trio uniforme fecha a alvo, σ 0,0248)
mas G3-T4 REPROVA — o trio expulsa a `amp0p6_10Hz` do tripé
(0,0586/0,1103/0,0313). Trio uniforme no grupo fixo: MORTO.

Racional T5: o grupo já carrega `dmg_dwell_exp=1,0 · f_ref_dmg=10`. Em
f=f_ref o gate vale 1 EXATO ⇒ a 10Hz é intocável por construção; elevar o
expoente fortalece o dano só nas 5Hz — a separação que o T4 mediu faltar.

- G1-T5: alavanca ÚNICA `dmg_dwell_exp` (grade {1,5 · 2 · 2,5 · 3}, refino
  só entre pontos já medidos); nenhum outro campo do grupo fixo muda.
- G2-T5: `amp0p6_5Hz` (trim 4800) entra no tripé.
- G3-T5: `amp0p6_10Hz` bit-idêntica (gate=1 em f_ref — conferir, não assumir).
- G4-T5: `amp0p4_5Hz` não piora > +0,01 em nenhuma perna.
- Procedência: expoente fitado-this-rig, 1 número; a FORMA (dwell por
  frequência) já era adotada.

---

## RESULTADOS FINAIS (execução 2026-08-10)

| trilho | veredicto |
|---|---|
| T1 trims | G1 ✓ G3 ✓; G2 REPROVA isolado (σ 0,0347/0,0477) — adotados pela regra de adoção com o T2 |
| T2 trio varamp | mínimo INTERIOR (c_D 0,1 · W_ref 2250 · k_dmg 32); held-out melhora nas 3 pernas; G2-T2 REPROVA (σ 0,0362) |
| T3 limiar amp0p4 | FALHA declarada: s1_amp_gate move MAE e piora σ; graded_scrit quebra o grupo (10Hz σ→0,21+) |
| T4 trio grupo fixo | G2 ✓ (σ 0,0248) mas G3 REPROVA — expulsa a 10Hz; trio uniforme morto |
| T5 dmg_dwell_exp | FALHA declarada: direção INVERTIDA (σ 5Hz piora monotônico); 10Hz bit-idêntica ✓ |

**Adoção executada** (regra declarada na rodada 2, PR-37′: mediana 0,0609→
0,0342 = −44 % ≤0,05; nenhum caso pior): trims 4800/3700 + trio varamp v2.

**Estado final da fonte:** 1/5 no tripé (10Hz). As 4 restantes, com o número
e a perna que falta: amp0p6_5Hz σ 0,0347 (1,39×) · small_to_large σ 0,0297
(1,19×) · large_to_small σ 0,0362 (1,45×) · amp0p4 σ 0,0764 + MAE 1,99×.

**O muro, com prova:** o σ restante é rampa/curvatura (0–1 cruzamentos de
sinal) — a classe que alavanca de NÍVEL não fecha (lei da variância, estudo
de 2026-07-29); a fonte NÃO tem piso medível (auditoria B3: paper publica só
médias) ⇒ sem rota de exceção; per_case de trio fitado = problema-Karlsen,
vetado pelo próprio diagnóstico. O que destrava: (a) o candidato de FORMA
cross-rig "resposta graduada de limiar" (amp0p4 + Yang2023, fila da
campanha); (b) reabertura da classe "aceleração tardia" pela cláusula
automática (fingerprint mudou desde o fechamento) — decisão de campanha;
(c) réplicas de bancada (âncora interna) para dar piso à fonte.

---

## RODADA 4 — T6: slip_onset_W no grupo varamp (1 número; rampa ≠ curvatura)

Racional: a small_to_large pós-adoção tem **0 cruzamentos** de sinal (rampa
monótona, viés −0,046) — não é a classe sem-esperança (sinal alternante).
`slip_onset_W` (herdado 40000) desloca o início das perdas por slip; é a
única alavanca de 1 número do grupo ainda não sondada.

- G1-T6: sonda de 2 pontos {20000, 80000}; refino só se direção certa; fit
  SÓ na small_to_large (trimada); large_to_small held-out zero-refit.
- G2-T6: small_to_large entra no tripé (σ ≤0,025 — falta −16%).
- G3-T6: large_to_small zero-refit não piora > +0,01 em nenhuma perna
  (fecha = bônus).
- G4-T6: grupo fixo intocado por construção.
- INCONCLUSIVO: Δσ<0,001 nos 2 pontos = inerte, declarar.

**T6: FALHA declarada** — sonda de 2 pontos: W=20000 catastrófico
(σ 0,245), W=80000 piora (σ 0,0540). O 40000 herdado é ótimo local; a rampa
da small_to_large não cede a nenhuma alavanca de 1 número do grupo. Espaço
per-rig legítimo EXAURIDO: 6 trilhos, 4 falsificações declaradas, 1 adoção.

---

## RODADA 5 — mandato refinado (professor, 08:54): as 3 SEM estatuto no tripé

Diagnóstico novo (pós-adoção): as 5 curvas têm viés inicial NEGATIVO
(−0,134/−0,090/−0,062/−0,028/−0,024) e a decomposição da amp0p4 é 92 %
Estágio I. `N_emb` efetivo = 50 (default): o modelo assenta em degrau
(~150 ciclos) onde o dado cai em rampa (milhares). Não é gate de amplitude
— é o RELÓGIO do rig.

### T7 — N_emb rig-wide (1 número físico, os DOIS grupos)

- G1-T7: grade {250, 500, 1000, 2000, 4000}; refino só entre pontos
  medidos; `emb_um` intocado salvo contingência DECLARADA (máx. 2 números
  no trilho, orçamento G4-T3 herdado).
- G2-T7: nenhuma das 5 piora > +0,01 em nenhuma perna; `amp0p6_10Hz`
  PERMANECE no tripé.
- G3-T7: pelo menos 2 das 3 alvo melhoram em σ (senão FALHA declarada).

### T8 — trim da amp0p4 pela MESMA regra congelada do T1

Sufixo terminal medido: começa em N=9000 (8,6×/21,9× a mediana)
⇒ trim_n_max=9000. Consistência: é a regra do T1 aplicada sem ajuste; o
fechamento da classe registra que os ensaios YANG param por protocolo em
razões arbitrárias — a cauda é o começo do runaway que o protocolo cortou.

- G1-T8: janela exatamente 9000.
- G2-T8: amp0p4 melhora nas 3 pernas com o trim (senão não adota).
- G3-T8: demais curvas bit-idênticas.

Alvo combinado da rodada: `small_to_large`, `large_to_small` e `amp0p4`
no tripé com T7(+T8). Falha em fechar = números e pernas declarados.

---

## RESULTADO RODADA 5 + RODADA 6

**T7 PASSA (N_emb=1000, os dois grupos):** 4/5 no tripé —
amp0p6_10Hz 0,0235/0,0365/0,0210 ✓ · amp0p6_5Hz 0,0158/0,0394/0,0190 ✓
(a DECLARADA entra por mérito!) · large_to_small 0,0190/0,0691/0,0217 ✓ ·
small_to_large 0,0282/0,0474/0,0154 ✓ · amp0p4 0,0966/0,1411/0,0761 ✗.
Nenhuma pior; mediana 0,0609→0,0235. Procedência: relógio de assentamento
vibração-dirigido deste rig é ~20× o default (N_emb 50→1000,
fitado-this-rig, 1 número; grade com mínimo interior — 2000/4000 degradam a
large_to_small).

**T8 FALHA declarada:** o trim da amp0p4 piora o MAE (0,0996→0,108) —
G2-T8 exigia melhora nas 3 pernas. Não adotado.

### T9 — amp0p4 via s1_amp_gate SOBRE o relógio corrigido

- G1-T9: `s1_amp_gate_p=12` FIXADO por procedência (expoente efetivo ~11 do
  N95, Fig. 4 D-N do LIU_2025 — comentário do PR-3), NÃO fitado. Fitados
  (máx. 2): `s1_amp_gate_dref` ∈ {0,42; 0,45; 0,48} mm ·
  `s1_amp_gate_floor` ∈ {0; 0,1; 0,2; 0,3}. Grade 12 pontos, refino só
  interior.
- G2-T9: amp0p4 entra no tripé.
- G3-T9: as outras 4 PERMANECEM no tripé (margens: σ 0,0217 na
  large_to_small é a apertada).
- FALHA/INCONCLUSIVO: melhor célula não fecha ⇒ declarar números; gate de
  0,6 mm mordendo demais (alguma das 4 sai) ⇒ célula morta, não a rodada.

---

## RODADA 7 — T10: incubação completa da amp0p4 (o dado é 3 estágios de manual)

**T9 FALHA declarada** (nenhuma célula fecha; MAE→0,045 mas res.máx→0,21):
retardar só o Estágio I descobre a perda TARDIA ausente. Anatomia no relógio
novo: dado em PLATÔ (1,004) até N≈5000 e depois queda acelerando; modelo com
97 % da perda em embedding+creep precoce e wear 1 %. As duas metades da
forma já existem: `s1_amp_gate` (mata o S1 precoce em 0,4 mm) e
`slip_onset_W` (incubação do S2 — está em 40000, alto demais para o W_acc
da 0,4 mm destravar dentro do ensaio).

- G1-T10: TRÊS números fitados, declarados: `s1_amp_gate_dref` ∈ {0,45;
  0,48} · `s1_amp_gate_floor` ∈ {0; 0,1} · `slip_onset_W` ∈ {5000; 10000;
  20000} (p=12 segue fixo por procedência). Grade 12 células.
- G2-T10: amp0p4 entra no tripé.
- G3-T10: as outras 4 PERMANECEM no tripé (o slip_onset_W é do grupo fixo;
  o varamp tem o dele próprio, intocado).
- FALHA: melhor célula não fecha ⇒ declarar e ENCERRAR a fonte com o mapa
  (o que falta é a forma cross-rig da fila).

---

## RODADA 8 — T11: o LIMIAR do rig (µ dentro da banda) + cascata compensada

**T10 FALHA/INERTE declarado** (12 células idênticas ao dígito): com µ=0,150
default o δ_t=0,4369 mm mantém a amp0p4 em stick e o W_acc em ~0 — o gate
nunca vê trabalho. Medição nova: o DADO afrouxa com F₀≈0,996 ⇒ o limiar real
está em cima de 0,4 mm. µ é DEFAULT (não medido); banda medida da KB:
[0,14; 0,19].

- G1-T11: TRÊS números, grades fechadas: `mu` ∈ {0,150; 0,145; 0,140}
  (dentro da banda por construção) · `k_wear_spec` ∈ {1,5e-13; 1,2e-13;
  1,0e-13} (compensa o excesso +17 % nas 0,6) · `slip_onset_W` ∈ {10000;
  25000; 40000} (vivo agora que há slip). µ e W do grupo FIXO e do varamp
  IGUAIS (é o rig, não a curva).
- G2-T11: amp0p4 entra no tripé.
- G3-T11: as 4 do tripé PERMANECEM no tripé.
- G4-T11: procedência: µ input-dentro-da-banda-medida (qiao2025+lu2024);
  k_wear_spec re-fit this-rig; slip_onset_W re-fit this-rig.
- FALHA: melhor célula não fecha ⇒ fonte encerrada com o mapa (falta a
  forma cross-rig da fila) e números declarados.

---

## RODADA 9 — T12: ADOÇÃO DA FORMA PR-21 (autorização total do professor, 10:03)

A forma já existia: `k_ratchet` (ratcheting cinemático, spec 2026-07-08) ×
`loose_amp_exp` (PR-21, spec 2026-07-12, procedência IJPEM "N_L~δ^−3.8" no
próprio docstring) — construída e nunca adotada neste rig. A incubação nasce
da lei de potência (slip 0,03 mm ⇒ ratchet ~190× menor que a 0,2 mm) e a
aceleração do feedback F₀↓ ⇒ slip↑ ⇒ taxa↑. Zero código novo de engine.

**Inputs FIXOS (procedência, não fitados):** µ=0,14 (piso da banda medida
[0,14–0,19], qiao2025+lu2024) · loose_amp_exp=3,8 (IJPEM) · N_emb=1000 (T7).

**Fitados (grades fechadas, rig-wide nos DOIS grupos):**
`slip_onset_W` ∈ {4000; 8000; 15000} (W_acc da 0,4 ≈ 4,4 kJ no ensaio — o
gate tem de abrir no meio, onset observado N≈5000) · `k_ratchet` ∈ {0,003;
0,01; 0,03} (docstring O(0,005–0,1)) · `tr_loose_gain` ∈ {0,5; 1,0; 2,0}
(compensa o kernel de torque nas 0,6) · `k_wear_spec` ∈ {1,0e-13; 1,5e-13}
(só grupo fixo; varamp mantém a via legada + trio v2).

- G1-T12: grade completa, 54 células × 5 curvas; refino só interior.
- G2-T12: amp0p4 ENTRA no tripé.
- G3-T12: as 4 atuais PERMANECEM no tripé.
- G4-T12: verificação cross-rig POSTERIOR no YANG_2023_IJPEM (mesmo exp,
  k_ratchet per-rig): nenhuma comparável piora > +0,01 — senão a adoção é
  revertida (o exp é da fonte deles; a forma tem de pelo menos não ferir).
- FALHA: nenhuma célula 5/5 ⇒ melhor célula declarada e fonte encerrada.

**T12: FALHA TOTAL declarada** — 54 células, melhor célula 0/5 (µ=0,14 +
W baixo desmonta a fonte inteira; amp0p4 também piora: 0,162/0,306/0,080).
Quinta falsificação preregistrada do dossiê.

---

# FECHO DA FONTE (2026-08-10)

**Estado final: 4/5 no tripé** (adotado em 6e19494+4ab020e, store
`ca1473211659`, censo 147/205). Mandato "sem estatuto no tripé": 2 de 3
(small_to_large ✓, large_to_small ✓; bônus amp0p6_5Hz por mérito).

**amp0p4_5Hz: FORM-LIMITED com dossiê de CINCO falsificações** (T3, T9,
T10, T11, T12 — todas preregistradas, gates congelados antes do dado):
1. `s1_amp_gate`/`graded_scrit` — perna errada / quebra o grupo;
2. retardar S1 sozinho — explode o fim (falta perda tardia);
3. gate por trabalho acumulado — inerte em stick;
4. destravar o slip via µ na banda — cascata destrói as 0,6;
5. forma PR-21 completa (ratchet × δ^3,8) — nenhuma célula 5/5.

O dado exige onset por amplitude POR CICLO com incubação (~N≈5000 a
0,4 mm, F₀≈0,996) que NÃO passe pelo estado de slip — nenhum mecanismo do
engine atual tem essa assinatura sem ferir a família 0,6. Não é declarável
pelos critérios assinados (n=12; Δdado máx 0,125 < 0,25). Destrava por:
(a) réplica de bancada (piso à fonte); (b) vida por curva (bloqueada:
ensaios param por protocolo); (c) forma NOVA de engine com incubação
amplitude-dirigida sub-slip — projeto de campanha, com este dossiê como
caderno de contorno.

---

## RODADA 10 — T13: a FORMA NOVA (gth — ratchet de stick com incubação)

Construída em 2026-08-10 (default-inerte, `gth_k=0` = OFF exato): rotação
incremental amplitude-dirigida ((δ/dref)^q, q=3,8 IJPEM) ATIVA SOMENTE EM
STICK (slip ≤ 1e-9) com incubação por acumulador (A_gth ≥ gth_A0). Em
regime de slip o termo é 0 exato ⇒ as 0,6 ficam bit-idênticas POR
CONSTRUÇÃO — o defeito que matou T12 é impossível aqui. dF₀/dE do mesmo dθ
(hélice+filete) ⇒ conservação intacta.

- G1-T13: fixos por procedência: gth_q=3,8 (IJPEM) · gth_dref=5e-4
  (=LOOSE_AMP_REF) · s1_amp_gate_p=12, floor=0 (T9). Fitados (grades):
  s1_amp_gate_dref ∈ {0,45; 0,48} mm · gth_k ∈ {2e-5; 5e-5; 1e-4; 2e-4} ·
  gth_A0 ∈ {800; 1500; 3000}.
- G2-T13: amp0p4 entra no tripé.
- G3-T13: as 4 atuais PERMANECEM no tripé (esperado: bit-idênticas no gth;
  o s1_gate com p=12 toca as 0,6 em ~3% — medir, não assumir).
- G4-T13: testes de engine ANTES da adoção: OFF bit-idêntico · stick-only ·
  incubação · conservação. Se o fit falhar, a capacidade fica default-inerte
  no engine (padrão crash_trigger/k_late_amp) e o dossiê ganha a 6ª.

**T13: FALHA declarada + fronteira ESTRUTURAL (a 6ª do dossiê).** O gth
funciona exatamente como especificado (sonda unitária: acumula (δ/dref)^q em
stick, drena pós-A0, zero exato em slip) — e por isso a falha é informativa:
o corte de stick limita o mecanismo AO LIMIAR de slip (F₀ ratio 0,916 no
rig); abaixo dele os canais macro a slip 0,01–0,03 mm não produzem a cauda
(k_ratchet precisaria de ~40 = 400× fora da faixa física O(0,005–0,1)).
Rastro no fit: mx 0,21→0,177 e estaciona — o modelo para em ~0,92 onde o
dado vai a 0,727. O T13 tampouco passa o gate padrão (mx piora +0,036 vs
adotado) ⇒ SEM adoção.

**Capacidade embarcada default-inerte** (padrão crash_trigger/k_late_amp):
gth_k/q/dref/A0 + SlowState.A_gth; 7 testes de contrato
(`test_gth_stick_ratchet.py`) incluindo bit-identidade OFF (3 casos do store
ao dígito), stick-only, incubação, lei de amplitude e conservação (dE de
atrito suprido por W_ext no idioma do thread_fretting + ΔU elástico no dE —
residual próprio 0,894→0,014 J, abaixo do piso da banda tolerada do engine).

**Fecho definitivo da amp0p4:** form-limited com 6 falsificações; o que
destrava é dado (réplica de bancada / vida por curva), não mais mecânica de
engine — a assinatura que falta (perda amplitude-dirigida ABAIXO do limiar
de slip E além dele com constantes compartilhadas) contradiz a separação
stick/slip que protege o resto da fonte.
