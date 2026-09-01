# PREREG — lei de taxa do canal ROTACIONAL: taxa residual sub-arresto (+ referência de slip per-rig)

**Data:** 2026-08-15 (noite) · **Sessão B** · store `20be19aabe11` ·
**gates congelados neste commit** · autoria do diagnóstico: itens **Q**
(`icmez_arresto_sub_piso_resultado.md`) e **R**
(`rousseau_ratchet_transferencia_resultado.md`); reconciliação de classificador
por sessão A (`85eaf93`).

## 0. Por que NÃO estou assinando exceção para as 9

O professor assinou tudo ("assine tudo", 19:57). Para os itens Q e R a
assinatura **não** é exceção, e o motivo é de método: exceção existe para
curva **sem rota** — e estas têm a rota **nomeada e construível**. Assiná-las
converteria 9 curvas abertas em "resolvidas" **sem o modelo melhorar**, que é
exatamente o que a doutrina chama de inflar o resolvido com fracasso (o próprio
comentário do `classificar` da triagem diz isso). Assino, portanto, a
**opção (ii) dos dois itens: autorizar o desenho da lei de taxa** — com prereg
e gates, como qualquer forma nova.

## 1. O que está medido (não se re-mede aqui)

| medição | fonte | número |
|---|---|---|
| canal rotacional **morre** no piso (`self_locking_gate → 0,0000`) enquanto o dado atravessa | ICMEZ ×3 (grip 13,8) | taxa tardia do modelo **0,18–0,26** da sua taxa de meio vs **0,48–0,57** do dado |
| dado é **limpo** (não é *data-limited*) | ICMEZ ×5, ROUSSEAU ×4 | σ_res **4,7–15×** o ruído da própria curva |
| rotação-por-slip exigida varia **10×** dentro do mesmo rig | ROUSSEAU ×4 | slips 0,03 vs 0,44 mm, déficit comparável (+0,05…+0,16) |
| `loose_amp_exp<1` **amplifica** abaixo de `LOOSE_AMP_REF`=0,5 mm | ROUSSEAU | fator **7,1×** em slip 0,03 mm contra 1,09× em 0,44 mm |
| falsificados como constante compartilhada | ambas | **41 células**: N_emb, wear, amplificador tardio, piso↓, piso+teto cinemático, gain+piso, k_ratchet (7), k_ratchet×exp (3), 5 de nível no ICMEZ |

## 2. A forma proposta — DOIS campos, ambos default-inertes

**(a) `loose_arrest_residual` [0,1)** — taxa residual sub-arresto.
Hoje `self_locking_gate` devolve `g = max(0, 1 − F_min/F_0)`, que **zera** em
`F_0 → F_min` (ponto fixo estável = arresto duro). Passa a devolver

```
g = max(loose_arrest_residual · g0, 1 − F_min/F_0)       # g0 = g(N=1)
```

⇒ abaixo do limiar o canal mantém uma **fração da sua própria taxa inicial**
em vez de morrer. **0,0 (default) = comportamento atual, bit-idêntico.**
Leitura física: o núcleo auto-travado de Cattaneo–Mindlin **não é rígido** —
ele cede lentamente sob ciclagem continuada (o dado do ICMEZ atravessa o piso
mantendo ~50 % da taxa de meio).

**(b) `loose_amp_ref` [m]** — referência de slip **per-rig**, hoje a constante
de módulo `LOOSE_AMP_REF = 5e-4`. Vira campo de `JointMaterial` com default
`5e-4` (**bit-idêntico**), lido por `loose_amp_exp` no lugar da constante.
Leitura física: a amplitude em que a resposta de amplitude "vira" é do PAR
(passo, folga, rigidez), não uma constante universal — e com todos os slips de
um rig abaixo dela o expoente inverte o sinal do seu efeito (§3 do item R).

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G0** | **inércia** | com os defaults (`loose_arrest_residual=0`, `loose_amp_ref=5e-4`) o store re-simulado é **bit-idêntico** nas 210 (mae/maxerr/resid_std, |Δ| = 0 exato) |
| **G1** | **alvo** | ≥ **2** das 3 ICMEZ bloqueadas por arresto (`amp0p3_F14p3_lk13p8`, `amp0p3_F17p6_lk13p8`, `amp0p4_F17p6_lk13p8`) **fecham o tripé** |
| **G2** | **nenhuma piora** | nenhuma curva do `ICMEZ_2025` piora mais que **+0,010** de MAE |
| **G3** | **protegidas** | as 3 do ICMEZ hoje no tripé (`amp0p4_F14p3_lk13p8`, `amp0p4_F14p3_lk19p8`, `amp0p4_F17p6_lk19p8`) **continuam** no tripé |
| **G4** | **isolamento** | Δ = **0,0000 exato** em TODAS as curvas fora das fontes que receberem a constante |
| **G5** | **mecanismo, não número** | a taxa tardia do modelo (fim÷meio) nas 3 alvo tem de subir de 0,18–0,26 para dentro de **[0,40 ; 0,70]** — a banda do dado (0,48–0,57) ±0,1. Fechar MAE sem corrigir a taxa é fitar |
| **G6** | **conservação** | resíduo de conservação não degrada além do nominal em nenhuma curva tocada |
| **G7** | **parcimônia** | **1 número por fonte** (o residual). O `loose_amp_ref` só entra se o ROUSSEAU for atacado, e aí com **1 número** também (a referência), reusando o `k_ratchet`/`exp` já existentes |
| **G8** | **fingerprint** | store re-carimbado uniforme nos 210 + guards verdes |

## 4. Predições registradas ANTES de medir

1. **O ICMEZ fecha ≥2 com residual entre 0,15 e 0,45.** Abaixo de 0,10 o efeito
   é pequeno demais (a taxa tardia sobe pouco); acima de 0,6 vira quase-runaway
   e o MAE dispara — a mesma bifurcação já medida com o piso.
2. **As 2 do ICMEZ de grip 19,8 NÃO fecham** — elas não são bloqueadas por
   arresto (o dado termina em 0,381 e 0,549, acima do piso 0,308) e o defeito
   delas é excesso de perda no meio. Se fecharem, **procurar erro de campo**.
3. **O ROUSSEAU não se move com (a)** — nenhuma das 4 é bloqueada por arresto
   (`loose_arrest_floor` = 0,0 no grupo do aço). Só (b) as alcança.
4. **Nenhuma curva fora do ICMEZ/ROUSSEAU muda** (G4), porque os campos são
   per-fonte e default-inertes.

## 5. Ramos

- **ADOTA** — G0–G8 verdes; célula escolhida por **CENTRALIDADE** (D-AA:
  mais vizinhos aprovados; desempate pela pior perna), nunca por MAE.
- **FALSIFICADO** — nenhuma célula passa G1/G2/G3 ⇒ a taxa residual não é a
  forma certa; registrar com números e devolver os itens Q/R à mesa.
- **INCONCLUSIVO** — grade inteira inerte, campo errado, unidade trocada
  (ramo obrigatório desde 2026-07-30).

## 6. Grade

`loose_arrest_residual` ∈ {0,05 · 0,10 · 0,20 · 0,30 · 0,45 · 0,60},
aplicado ao grupo `ICMEZ_2025`. **Disciplina de fronteira (D-L):** se a
vencedora cair na borda, estender antes de adotar.

---

## RESULTADO (2026-08-15, noite) — forma CONSTRUÍDA, mecanismo VALIDADO, adoção **FALSIFICADA** pelos próprios gates

Campo `loose_arrest_residual` implementado (default 0,0 = **bit-idêntico**,
early-return explícito; contrato preso em `tests/test_loose_arrest_residual.py`,
5 testes). O `loose_amp_ref` **não** foi implementado: o ROUSSEAU não seria
alcançado por (a) e a decisão de (b) depende do resultado de (a).

**G0 — inércia: VERDE.** 6 casos de 6 fontes distintas re-simulados com o
código novo: |Δ| = **0,000e+00** em mae/maxerr/resid_std.

**G5 — mecanismo: VERDE, e é o achado principal.** A taxa tardia do modelo
(fim÷meio) nas 3 alvo sobe monotonicamente com o residual:

| residual | 0,00 | 0,05 | 0,10 | 0,20 | 0,30 | 0,45 |
|---|---:|---:|---:|---:|---:|---:|
| taxa alvo | 0,20 | 0,22 | 0,26 | **0,35** | **0,47** | 0,69 |
| σ da 1ª alvo | 0,043 | 0,040 | 0,036 | **0,029** | 0,031 | 0,057 |

⇒ a forma **faz exatamente o que foi desenhada para fazer**: em residual 0,30 a
taxa tardia (0,47) entra na banda do dado (0,48–0,57), que a versão binária
nunca alcançava.

**G1 — alvo: VERMELHO com o residual sozinho.** Nenhuma das 3 fecha em
nenhuma dose (σ mínimo 0,029 contra 0,025). ⇒ **o arresto era UM defeito, não
o único**: sobra o excesso de perda no terço do meio (−0,077).

**O par que fecha — e por que NÃO é adotável.** `residual=0,30 + emb_um=8`
(contra 11,0 vigente) leva o tripé da fonte de **3 → 5**: fecham as 3 alvo
(0,0092 · 0,0131 · 0,0346) **e** a `amp0p3_F17p6_lk19p8`. Mas:

| gate | veredito | número |
|---|---|---|
| G1 | ✅ | 3 de 3 alvo fecham |
| **G2** | ❌ | 3 curvas pioram >+0,010 de MAE (+0,0194 · +0,0335 · +0,0402) |
| **G3** | ❌ | **2 das 3 protegidas quebram** (`amp0p4_F14p3_lk19p8` σ 1,62×; `amp0p4_F17p6_lk19p8` MAE 1,36× · mx 1,37× · σ 1,70×) |
| **G7** | ❌ | 2 números, e um deles é **input com procedência VDI** (`emb_um` da classe de rugosidade), que perderia a procedência ao virar knob |

⇒ **NÃO ADOTADO.** Trocar 2 curvas que passam por 3 que fecham é exatamente o
que G2/G3 existem para impedir; e o ganho líquido (+2) viria com um input
desancorado. Censo **inalterado em 143/205**.

## O que o trade REVELA (3º diagnóstico, mais profundo que os dois primeiros)

O `emb_um=8` acerta os **grip 13,8** e erra os **grip 19,8** — as duas que
quebram são as de grip grosso. Mas embedding, pela VDI, depende de
**rugosidade e número de interfaces**, **não** de comprimento de aperto: um
`emb_um` per-grip seria **anti-físico**, não só anti-parcimonioso. ⇒ o que a
medição está dizendo é que a **dependência de grip do modelo** (via `c_bend` →
`k_tr`) está errada nesta fonte, e o `emb_um` estava compensando-a. Este é o
alvo real, e é de FORMA (escala de rigidez com o grip), não de constante.

## Predição registrada — leitura honesta

A predição 2 dizia *"as 2 de grip 19,8 NÃO fecham; se fecharem, procurar erro
de campo"*. Com o **residual sozinho** (grade §6) elas de fato não fecham. No
par com `emb_um`, **uma delas fecha** — e a investigação exigida pela própria
predição mostra que **não é erro de campo**: o defeito dela é de NÍVEL
(viés −0,030), alcançável por embedding, e não pelo arresto. A predição
estava certa sobre o residual e cega quanto ao par; fica registrada assim.

## Estado da capacidade

`loose_arrest_residual` fica no engine **default-inerte**, com contrato preso
por 5 testes (mesmo padrão do `gth`/`fat_ramp_D_on`). Reabre quando a escala de
rigidez com o grip tiver forma — aí o par (residual + grip correto) pode fechar
sem pagar as protegidas.

---

## ⚠️ ERRATA (mesma noite, 21:1x) — a MINHA hipótese do 3º diagnóstico está FALSIFICADA pela medição

O §"O que o trade REVELA" afirmou que *"a dependência de grip do modelo
(`c_bend` → `k_tr`) está errada nesta fonte, e o `emb_um` estava
compensando-a"*. **Medido, e não é isso:**

| medida | resultado |
|---|---|
| `k_tr(13,8)/k_tr(19,8)` no modelo | **2,954** — igual à lei de viga `(19,8/13,8)³` = 2,954, ao dígito |
| sensibilidade ao grip (perda fino ÷ perda grosso), modelo × dado | 1,155×1,248 · 1,371×1,642 · 1,111×1,094 · 1,123×1,108 |
| erro dessa sensibilidade | **1 a 20 %, SEM sinal consistente** (sub em amp0p3, super em amp0p4) |

⇒ a escala de rigidez com o grip **não está errada**. A hipótese caiu no
primeiro teste, e fica registrada como caída.

**O que a medição diz no lugar — e é mais útil:** os dois grips estão em
**REGIMES DE SLIP DIFERENTES**. `slip/δ` medido: **0,69–0,81** nos grip 13,8
(gross) contra **0,08–0,44** nos grip 19,8 (parcial, um deles a 0,08 = quase
stick). Toda alavanca de NÍVEL (embedding, ganho rotacional) muda `F_0`, e
`F_0` desloca as parciais **através da fronteira de regime** enquanto quase não
move as de gross slip. É por isso que `emb_um=8` fecha as finas e quebra as
grossas — e não por erro de geometria.

**Mais 7 células falsificadas** (par residual × ganho rotacional, a alavanca
regime-seletiva óbvia): `res=0,45 gain=1,5` fecha **1** alvo (0,020/0,023) e
quebra **as 3 protegidas** (tripé 1/8); `gain=1,0` dá resultado **idêntico ao
dígito** com residual 0,30 · 0,45 · 0,60 — assinatura de *parâmetro morto* (com
o ganho pela metade o modelo nunca chega ao piso, e o residual deixa de existir).

**Total medido nesta fonte: 53 células** (26 + 5 + 7 + 8 + 7).

**⛔ ADENDO 2026-08-19 (16:0x) — a rota abaixo foi MEDIDA e MORREU antes de
ser construída.** A premissa era que o regime separasse alvos de protegidas.
Instrumentado `resolve_transverse_slip` nas 8: **não separa** — 2 das 3
protegidas estão em GROSS (slip/δ 0,92 e 0,69) junto com 3 abertas, e a 3ª
protegida em PARCIAL junto com 2 abertas. Uma forma só-gross pagaria as duas
protegidas gross: o MESMO trade das 53 células, inevitável para **qualquer**
gate de regime. Abertas e protegidas se entrelaçam em TODOS os eixos
observáveis (amplitude, carga, grip, regime) — a geometria dos inputs do
YANG_2021, na 4ª fonte. Registro:
`New_Theory/sem_replicas_inventario_fechado.md` §2.

**A rota que sobra, nomeada com precisão:** a redução de perda no terço do meio
tem de agir **só no regime de gross slip** — uma forma **gateada pelo regime**
(a maquinaria Cattaneo–Mindlin já existe no engine), não uma constante
compartilhada. Qualquer constante escalar move os dois regimes juntos, e é
exatamente isso que as 53 células mostram.
