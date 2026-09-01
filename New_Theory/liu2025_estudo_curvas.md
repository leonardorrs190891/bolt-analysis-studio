# Estudo v2 — GERAR as curvas do Liu 2025 no software

**Data:** 2026-07-28 · **Refaz e supera:** `liu2025_estudo_modelagem.md` (que mirava a VIDA;
este mira a **CURVA**) · **Fingerprint do estado:** `4f5bedfbace4`
**Pergunta do professor:** *"nosso modelo deve ser capaz de criar essas curvas no software"*
**Status:** ESTUDO — nada implementado, nada adotado, canônico intocado.

---

## 0. A reorientação, e o que ela muda

O estudo anterior perguntou *"a vida transfere?"* (resposta: joelho sim a 5,9 %, ramo de
baixo ciclo não). A pergunta agora é outra: **o `DynamicStiffnessAnalyzer`, rodando no
Run/galeria, produz a curva em S completa — platô → declínio → joelho → colapso a zero —
por física?**

A resposta curta deste estudo: **dois terços da curva ele já produz e estão validados
(7/7 no tripé pós-trim). O que falta é UMA capacidade — o estágio de fratura — e ela já
existe como sonda validada, mas não como código do engine.** E há um resultado de escopo
que enxuga a implementação: **o joelho da Su–N não precisa ser implementado — ele é
EMERGENTE dos mecanismos que já temos** (§4).

### Erratas absorvidas (para este documento ser autossuficiente)

| afirmação anterior | estado |
|---|---|
| "44 % de dispersão de espécime" | **não estabelecida** — amplitude da Fig. 2 não é declarada; o defensável é ±17 % de relógio |
| `m = 3,01 / R² = 0,9894` como "a Su–N do artigo" | **inválida como leitura do artigo** (Table 2 casa com N₉₅, não com fratura) — mas §3 abaixo a reabilita como **lei nossa**, declarada como tal |
| Fig. 4 = vidas de fratura | **errado** — Fig. 4 é vida até `F/F₀ = 0,95` |
| `fat_m1 = 2,7` com procedência "D–N Liu2025" | **não rastreável** ao texto do artigo |

---

## 1. Anatomia medida da curva — o alvo que o software tem de reproduzir

A curva do Liu 2025 (e da família toda: Yang, Jiang, competitive-failure) tem **três
estágios com três fronteiras**, e cada fronteira tem um relógio próprio:

```
r = F/F₀
1.00 ┤●— estágio 1: assentamento (material-loosening) ....... fim em N_M ≈ 7×10²
     │    queda rápida ~2–5 %: embedding + conformação
0.95 ┤     — — — — — — — — — — — — — — — — — — — — — [N₉₅: relógio do LIMIAR]
     │   estágio 2: afrouxamento estrutural (fretting/slip/creep)
     │    declínio suave quase-linear em log N
 r_D ┤————————————— joelho N_D (tangente 45° do paper) [N_D: relógio do JOELHO]
     │   estágio 3: fratura por fadiga — rampa lisa ACELERANTE
0.00 ┤______________________________________ fratura M2      [N_f: relógio da FRATURA]
```

**Os três relógios, medidos (M16):**

| δ (mm) | N₉₅ (Fig. 4) | N_D (joelho) | N_f (fratura) | N₉₅/N_f | N_D/N_f |
|---:|---:|---:|---:|---:|---:|
| 0,25 | 16 157 | 240 000 | 330 000 | 0,049 | 0,727 |
| 0,30 | 13 516 | 180 000 | 250 000 | 0,054 | 0,720 |
| 0,40 | 9 099 | 60 000 | 77 000 | 0,118 | 0,779 |
| 0,50 | 2 745 | 30 000 | 38 000 | 0,072 | 0,789 |
| 0,60 | 460 | 18 000 | 24 200 | 0,019 | 0,744 |
| 0,80 | 19 | 11 500 | 14 400 | 0,001 | 0,799 |

Três regularidades que o software deve honrar:

1. **N_D/N_f = 0,72–0,80** (média 0,76): o colapso ocupa sempre o último quarto da vida.
2. **N₉₅ ≪ N_D**: o limiar de 95 % é atravessado *cedíssimo* (0,1–12 % da vida) — ele
   pertence ao **fim do estágio 1**, não ao colapso.
3. **O nível do joelho segue uma lei em amplitude:**
   `1 − r_D = 0,414·δ − 0,031` (**R² = 0,957**, 6 pontos) — quanto maior a amplitude,
   mais pré-carga se perde por afrouxamento antes de a trinca assumir. É a versão
   quantitativa da lei de forma da linha *competitive-failure* do mesmo grupo
   (transversal dominante ⇒ estágio 2 curto e fundo; axial dominante ⇒ o inverso).

---

## 2. Confirmação independente do ajuste cego — a Fig. 7 do próprio artigo

Ontem ajustei a Su–N bilinear **às cegas** sobre Table 2 × Fig. 4. Hoje abri a **Fig. 7**
(a curva normalizada que o artigo publica, nunca antes extraída por nós):

| grandeza | Fig. 7 (leitura direta) | nosso ajuste cego (ontem) |
|---|---:|---:|
| joelho | ~(N = 7×10³, **σ ≈ 560 MPa**) | **513,5 (M16) / 544,0 (M10) MPa** |
| m ramo baixo-ciclo (tensão alta) | **12,1** | **12,03 / 10,07** |
| m ramo alto-ciclo (tensão baixa) | 0,92 | 1,38 / 1,61 |

O expoente do ramo íngreme bate na **casa decimal** (12,1 vs 12,03). O joelho, a 3–9 %.
A estrutura bilinear que medimos é a que o artigo publica — validação cruzada fechada.

---

## 3. Os TRÊS relógios são físicas distintas — o aviso central de implementação

Este é o ponto que o estudo anterior conflava e que decide o desenho:

| relógio | o que cronometra | lei medida | é para implementar? |
|---|---|---|---|
| **N₉₅** | travessia do limiar de 95 % (fim do assentamento) | Su–N **bilinear**: joelho 513–560 MPa, m₁≈10–12, m₂≈1–1,6 | **NÃO — é EMERGENTE** (§4) |
| **N_D** | início do colapso | N_D ≈ 0,76·N_f (fração estável) | não diretamente — sai de `D_on` |
| **N_f** | fratura | `N_f = 1,56e13·σ_root^−3,12`, **R²(log) = 0,9905** | **SIM — é o relógio do estágio 3** |

**Sobre a lei de N_f:** este é um pareamento **nosso** (tensão de raiz da Table 2 ×
vidas de fratura da matriz de ensaios), não a Su–N do artigo — a errata de ontem matou a
leitura errada, não a regressão. Como lei empírica declarada como nossa, ela é excelente:
`m ≈ 3,1` é a inclinação clássica de propagação de trinca (Paris-consistente), e como
σ ∝ δ (Table 2, linear a 2,9 %), ela equivale à D–N de fratura `N_f ∝ δ^−2,9` que já
medíamos. **Dois processos, dois expoentes: afrouxamento tem joelho bilinear 12→1,4;
fratura tem potência única m≈3.** O software precisa dos dois — e já tem o primeiro.

**Goodman vivo importa aqui, com número:** σ_m = F₀/A_s cai de 382 → 325 → 260 MPa
conforme r cai 1,00 → 0,85 → 0,68; o denominador de Goodman sobe 0,522 → 0,594 → 0,675.
Com m≈3,1, calibrar `fat_C1` a σ_m constante contra o contexto vivo erra a vida por
~50 % — é a razão de a âncora ter de ser o **N_f medido no contexto canônico** (lição já
registrada no CLAUDE.md, agora com a conta).

---

## 4. O que o engine JÁ gera — e o resultado de escopo

Contra a anatomia da §1, mecanismo a mecanismo:

| trecho da curva | físico | engine hoje | estado |
|---|---|---|---|
| estágio 1 (até N_M) | assentamento | `EmbeddingLoss` (state-based, `N_emb`) + conformação (`W_conf_ref`) | ✅ **validado** — LIU_2025 adotado tem `N_emb`, `emb_um` |
| **cruzamento de N₉₅** | fim do assentamento | consequência dos de cima | ✅ **emergente** |
| estágio 2 (até N_D) | fretting/slip/creep | `WearLoss` + `CreepLoss` + `RotationalLoosening` c/ `loose_arrest_floor`, `slip_onset_W`, `c_bend`, `k_ratchet` | ✅ **validado 7/7 pós-trim** |
| **joelho da Su–N (513 MPa ↔ δ≈0,44 mm)** | limiar de afrouxamento | é o que `slip_onset_W` + arresto + Cattaneo–Mindlin **já modelam** | ✅ **emergente** — não implementar |
| **estágio 3 (N_D→N_f)** | trinca → perda de seção → F₀→0 | `FatigueLoss` = **cliff** de 1 ciclo | ⚠️ **falta a RAMPA** |
| relógio de N_f | Miner + Goodman sobre Su–N | `sun_life()` + Goodman vivo + energética do cliff (U liberado → `W_diss_fracture`) | ✅ existe; falta **âncora per-rig** com procedência |

O resultado de escopo: **a única física ausente é a rampa do estágio 3.** E ela já está
**validada como forma** — sonda B1 (`A_eff/A_s = 1 − ((D−D_on)/(1−D_on))^q`):
10/10 cruzamentos em vida em `amp0p4`/`amp0p5` com um par único (`D_on`=0,75, `q`=8);
6/7 no `fig2` fino; universalidade u–v (σ≈0,01–0,02) no núcleo. O que nunca foi feito é
**promovê-la de sonda a capacidade**.

O joelho bilinear — que parecia "algo a implementar" — **não é**: `m₂≈1,4` quase plano é
a assinatura do limiar de afrouxamento, exatamente o regime que `slip_onset_W`/arresto/
Cattaneo–Mindlin produzem. Implementá-lo de novo via Su–N seria **duplicar física por
outra via** — o erro que o paradigma das três camadas proíbe.
*(Honestidade: a fidelidade do N₉₅ emergente nunca foi medida como número — os 7/7 são
MAE de curva. Vira check informacional no plano de validação, §7.)*

---

## 5. O que falta, exatamente — quatro lacunas medidas nesta sessão

1. **A rampa não existe no engine.** `FatigueLoss` é cliff. A rampa vive em
   `liu2025_ramp_v2_gates.py` via `loss_mechanisms=[...]` injetado.
2. **O driver de tensão tem a escala de tamanho errada por 2,1×.** O modo `bending`
   (`σ_a = Kt·E·d₂·δ/L_eff²`) exigiria `Kt` = 1,15 no M10 e 2,40 no M16 para bater a
   Table 2 — um `Kt` único não existe sob essa fórmula. Para **reproduzir as curvas do
   Liu** isso não bloqueia (per-rig, `fat_C1` absorve); para **generalizar** entre rigs,
   bloqueia (é o `c_σ` da Table 2, que só existe para 2 tamanhos).
3. **Plumbing da GUI:** `fat_*` **não está** em `V2_PARAM_NAMES` (dialog não expõe) — mas
   `_v2_tuner_overrides` os deixa passar (filtro por `__dataclass_fields__`), então
   Run e galeria funcionam via config adotado. O Run **já passa** `delta_amp` ao
   `step_cycle` (verificado: `step_cycle(F_amp, theta, freq, delta_amp=dd)`).
4. **`_CAP = 100000` no Run** — as curvas de 0,25/0,30 mm precisam de 330k/250k ciclos.
   No Run/GUI elas sairiam truncadas a um terço; a galeria (runner) não tem esse cap.

E uma decisão de arquitetura, com o trade-off medido:

**Opção A — rampa aplica `dF_0` direto** (como a sonda): mínima, energética por
incremento análoga à do cliff (liberar `ΔU_internal` por passo → `W_diss_fracture`),
**não** toca `[K]`. Custo: o acoplamento "menos F₀ → k_b menor → mais slip → mais wear"
NÃO acontece — a rampa fica cega ao resto.
**Opção B — perda de seção entra no `[K(s)]`**: `A_eff` vira estado que **modula `k_b`**
por ciclo — filosoficamente é O paradigma V2 (*"[K(s)] dinâmico re-avaliado a cada
ciclo"*), o acoplamento com slip/wear vem de graça, e `U_internal` já usa `k_b` (a
energética fecha por construção). Custo: `geom.k_b` hoje é **estático** (verificado:
nunca reatribuído); dinamizá-lo toca `Phi`, `k_tr`, `k_j` em série — mudança larga, a
validar contra os 203.
**Recomendação: A primeiro** (reproduz a sonda validada bit a bit, risco mínimo),
**B como candidato de forma** para a família competitive-failure (é B que produziria o
acoplamento transversal/axial que explicaria a `amp0p6`).

---

## 6. Procedência das constantes do estágio 3 (o que um prereg de implementação fitaria)

| constante | valor de partida | classe | origem |
|---|---|---|---|
| `fat_m1` | **3,12** | **medido-de-dados-do-paper** (nosso pareamento, declarado) | regressão N_f × σ_root, R²=0,9905 — substitui o 2,7 sem procedência |
| `fat_C1` | re-ancorar **no contexto canônico** | fitado-this-rig | âncora = N_f medido; Goodman vivo muda ~50 % (§3) |
| `fat_Kt`/driver | per-rig via `c_σ` = 1081 MPa/mm (M16) | input-de-paper (Table 2) | só 2 tamanhos; generalização = pesquisa futura |
| `D_on` | 0,70–0,90 | handbook | propagação = últimos 10–30 % da vida HCF; N_D/N_f medido 0,72–0,80 ✓ |
| `q` | ~5–8 | fitado-this-rig | um valor para a fonte (validado no núcleo) |
| `fatigue_residual_frac` | 0 | — | fratura = separação |

**Restrições duras de compatibilidade:** `LI_2022_TRIBOINT` está **adotado com o cliff**
(`fatigue_enabled=True`) — a rampa tem de ser **opt-in** (campo novo, default = cliff
**bit-idêntico**), e `fatigue_enabled=False` continua zero exato nos 203.

---

## 7. Plano de validação para o prereg de implementação (contas a rodar ANTES de congelar)

- **P0 — inércia:** defaults reproduzem o store `4f5bedfbace4` bit a bit (203 casos).
- **P1 — paridade com a sonda:** o engine com rampa reproduz `liu2025_ramp_v2_gates.py`
  (mesmos cruzamentos 10/10 no núcleo) — a capacidade É a sonda, sem deriva.
- **P2 — cliff preservado:** `LI_2022_TRIBOINT` bit-idêntico com a rampa desligada.
- **P3 — energia:** residual de conservação ≈ 0 com a rampa ativa (o cliff já roteia
  `ΔU → W_diss_fracture`; a rampa precisa do mesmo por incremento).
- **P4 — curva inteira no software:** o Run gera as 7 curvas em S até a fratura
  (exige tratar o `_CAP=100000` para as duas lentas — decisão: subir cap / decimar).
- **P5 — informacional:** fidelidade do N₉₅ emergente e do N_D (não-gate; primeiro número
  dessa fidelidade).
- **O que NÃO entra:** ganho de tripé (linha de métrica fechada — §4.48a; os trims da
  §B ficam), acoplamento transversal/axial (forma futura, opção B), generalização do
  driver cross-rig (bloqueada pelos 2 pontos da Table 2).

---

## 8. Decisões abertas para o professor

1. **Autorizar o prereg de implementação** do estágio 3 (Opção A, escopo §7)?
2. **Opção B** ([K(s)] com `A_eff`) — registrar como candidato de forma para a família
   competitive-failure, ou arquivar?
3. **`_CAP` do Run:** subir para 400k só quando fadiga ativa, ou decimar?
4. **`fat_m1=2,7` do `LI_2022_TRIBOINT`:** manter (funciona, calibrado com seu `fat_C1`)
   e só corrigir o rótulo de procedência, ou re-ancorar com 3,12? *(Recomendo: corrigir
   só o rótulo agora; re-ancorar exigiria re-simular e gatear aquela fonte.)*

---

## 9. Reprodutibilidade

Números novos desta sessão: três relógios (§1), lei do joelho (§1), leitura da Fig. 7
(§2), lei de N_f (§3), fatores de Goodman (§3) — todos reproduzíveis pelos blocos de
código no histórico da sessão; dados em `liu2025_fig4_DN.json`, Table 2 (§2 do estudo
anterior) e `curve_library/digitized_csv/liu2025_M16_*.csv`. Fatos de engine verificados
por leitura direta: `FatigueLoss` (cliff + Goodman + energética), `step_cycle(...,
delta_amp=dd)` no solver_worker, `_CAP = 100000`, `geom.k_b` estático, `fat_*` fora de
`V2_PARAM_NAMES`.
