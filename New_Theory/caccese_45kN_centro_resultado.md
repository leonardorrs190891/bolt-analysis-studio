# O grupo 45kN do CACCESE estava FORA da banda de réplicas — ADOTADO

**2026-08-04** · prereg
`2026-08-04-caccese-45kN-centro-replicas-prereg.md` (decisão D-I, por
delegação). Executor `New_Theory/caccese_45kN_centro_exec.py`.

## Veredicto: ADOTA `C_creep = 5,477047e-10` (C₀ × **0,85**)

O defeito não era "erro grande": os viesses do modelo contra as **duas**
réplicas eram **ambos negativos** (−0,0635 e −0,0253) ⇒ o modelo estava
**abaixo das duas**, fora da banda que o próprio dado não consegue distinguir
(piso |rep1−rep2| = **0,0382**).

| | MAE | res.máx | σ_res | tripé |
|---|---|---|---|:--:|
| **tapered_rep1** | 0,0602 → **0,0203** | 0,0677 → **0,0260** | 0,0137 → **0,0054** | ❌→**✅** |
| tapered_rep2 | 0,0254 → 0,0292 | 0,0651 → **0,0468** | 0,0270 → **0,0258** | ❌ (σ 3 % fora) |
| protruding_45kN (controle) | 0,0157 → 0,0242 | 0,0567 → **0,0294** | 0,0201 → **0,0054** | ✅→✅ |

Posição na banda: **0,0206** (vs rep1) e **0,0271** (vs rep2), ambas ≤ piso
0,0382 ⇒ **o modelo entrou na banda de dispersão do dado**. Era isso o G1, e
não o MAE.

## Por que a escolha do valor não foi por MAE

O G5 **proibia** escolher o valor que minimiza o MAE de uma das réplicas —
foi exatamente essa escolha implícita que produziu o defeito (o ajuste
anterior colou o modelo na `rep2`). Das **2** células que passam todos os
gates, o critério foi **a mais centrada**:

| célula | vs rep1 | vs rep2 | \|b1−b2\| | protruding |
|---|---:|---:|---:|---|
| C×0,90 | 0,0352 | 0,0223 | 0,0129 | mae 0,0106 |
| **C×0,85** | 0,0206 | 0,0271 | **0,0065** | mae 0,0242 |

C×0,80 entrava na banda com centro quase perfeito (0,0057/0,0333) e **foi
reprovada pelo G2**: a `protruding` piorava +0,0222 no MAE, o dobro da
tolerância. O controle da mesma config é que fixa o limite — não o alvo.

## Predição registrada: acertou nos três pontos

1. `C_creep` **menor** fecharia a `rep1` ✅
2. a `protruding` **se manteria** ✅ (folga de MAE era 0,0343, o custo foi
   0,0085)
3. a `rep2` **não fecharia** ✅ — σ é quase invariante à alavanca (0,0270 →
   0,0258; mudou 4 %, porque `C_creep` também altera levemente a forma, não
   só o nível)
4. e o valor ótimo ficaria **próximo da previsão aritmética** de 11–15 % de
   redução ✅ — deu exatamente **15 %**.

Que a aritmética da translação previsse o valor da alavanca dentro da faixa é
evidência de que, **neste regime**, `C_creep` age quase puramente sobre o
nível. Isso não era garantido: a mesma alavanca sob outro kernel poderia
deformar a curva.

## O que sobra na `rep2`, com número

σ **0,0258** contra o limite 0,0250 — **3 % fora**, o mais perto que qualquer
curva da fila já chegou. E ela **não tem rota F7**: o piso de σ do par é
**0,0233** (medido 2026-08-04, `_SEM_ROTA_F7_MEDIDO`), abaixo do limite global
e abaixo do erro do modelo. Ou seja: as duas réplicas do dado concordam entre
si melhor do que o modelo concorda com elas, nessa perna específica. Não há
exceção a assinar; é forma que falta.

### E o excesso da `rep2` é menor que a incerteza do próprio σ

Medido, com n=26 pontos na janela da métrica. O erro padrão de amostragem de
um desvio-padrão é `s/√(2(n−1))`:

| | valor | distância até σ=0,0258 |
|---|---:|---:|
| σ_res do modelo | **0,0258** | — |
| **SE do próprio σ** | **0,0036 (14 %)** | — |
| limite da 3ª perna | 0,0250 | +0,0008 = **0,21 SE** |
| piso de réplica do par | 0,0233 | +0,0025 = **0,68 SE** |

⇒ **a curva reprova por 0,21 desvios-padrão da incerteza da própria
estatística**, e está a 0,68 SE do piso de repetibilidade. Isto **não** é
exceção — a prova F7 é comparação pontual e o erro excede o piso, então a
assinatura não está disponível. Mas o registro honesto é que o excesso **não é
distinguível de zero** com este número de pontos.

Não proponho estatuto novo aqui: inventar categoria estatística no meio de uma
execução seria o oposto da disciplina de pré-registro. O número fica no
registro, para a decisão de quem lê.

## Sequência das duas adoções do dia nesta fonte

O D-H (kernel saturante, **forma**) e o D-I (nível dentro da banda) foram
executados e adotados **em passos separados, com re-stamp e commit próprios**,
de propósito: o D-H mexeu em `creep_mode`/`α`/`t_c` e o D-I só em `C_creep`.
Misturá-los tornaria impossível dizer qual mudou o quê — e o D-H é o que
carrega a claim de mecanismo (σ cai nas 7), enquanto o D-I é ajuste de nível
com alvo declarado.
