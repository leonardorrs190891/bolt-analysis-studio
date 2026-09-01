# LU_2024 `fig20_T10Nm` — a forma faltante é **embedding que não sabe da pré-carga**, e a prova é a própria varredura de torque da fonte

**2026-08-16 (madrugada)** · store `20be19aabe11` · sondas **só-leitura** ·
**nada adotado**. Esta é a **única** curva form-limited do projeto depois da
correção do pico espúrio (`lu2024_pico_espurio_resultado.md`) — e, com este
documento, **as 21 curvas abertas passam a ter forma nomeada**.

## 1. O diagnóstico da curva (protocolo padrão)

| perna | valor | limite | múltiplo |
|---|---:|---:|---:|
| MAE | 0,2514 | 0,050 | **5,03×** (manda) |
| res.máx | 0,3146 | 0,100 | 3,15× |
| σ_res | 0,0749 | 0,025 | 3,00× |

- **viés −0,2514 = −MAE exatamente** ⇒ `|viés|/MAE` = **1,00**: resíduo de
  sinal único, o modelo está **abaixo do dado em todo ponto** — ele perde
  pré-carga demais.
- **O erro se forma no PRIMEIRO ciclo**: o maior salto do resíduo é entre os
  dois primeiros pontos da métrica (**−0,2650**). Resíduo por terço −0,2293 /
  −0,2859 / −0,2359: depois do 1º ciclo as duas curvas correm quase paralelas.
- **Incremento tardio total = 0,0034** ⇒ *nenhuma* forma sobre o fim da curva
  move esta reprovação. Isso mata, por aritmética, a família inteira de
  candidatos de cauda.
- **Canal dominante: embedding**, 0,698 de perda absoluta contra 0,189 do
  rotacional, 0,012 do wear e 0,009 do creep.

**Alavancas varridas (2 pontos cada): nenhuma livre fecha.** `C_creep`,
`k_wear_spec`, `tr_loose_gain` e `arrest_approach_exp` movem 1–8 % com as três
pernas ainda em 2,7–3,0×; `creep_conform_exp` é **inerte por construção** aqui
(a fonte não declara `W_conf_ref`/`conform_driver`, então o gate de conformação
está desligado — é o gotcha de *companheiro de canal*, não parâmetro morto). A
grade **conjunta** nível × forma do canal dominante (`emb_depth` × `N_emb`,
25 células) fecha **0 de 25**, melhor 3,85×.

## 2. A prova: a fonte varre a PRÉ-CARGA, e o erro se ordena com ela

A `fig20` é uma varredura de torque à mesma amplitude — ou seja, uma varredura
de F₀ de **7×**:

| curva | F₀ (N) | viés | salto no 1º ciclo | \|salto\|·F₀ (kN) | estatuto |
|---|---:|---:|---:|---:|---|
| `T4Nm` | 2 105 | −0,3424 | **−0,7601** | 1,60 | declarada (escopo) |
| `T10Nm` | 5 963 | −0,2514 | −0,2650 | 1,58 | **fila form-limited** |
| `T16Nm` | 8 402 | −0,1572 | −0,1383 | 1,16 | declarada (órfã) |
| `T22Nm` | 11 567 | −0,0364 | −0,0418 | 0,48 | **tripé** |
| `T28Nm` | 15 027 | −0,0901 | **+0,0273** | 0,41 | declarada (órfã) |

- **`corr(|salto no 1º ciclo|, 1/F₀) = +0,995`** — praticamente uma reta.
- `corr(|viés|, 1/F₀) = +0,874`.
- ⚠️ **O sinal INVERTE na maior pré-carga**: em `T28Nm` o modelo **perde de
  menos** no 1º ciclo. Um erro que troca de sinal ao longo da varredura não é
  "constante mal ajustada" — é **lei faltante**: uma única profundidade
  absoluta, ajustada no meio da faixa, sobra embaixo e falta em cima.

**Por que isso aponta o embedding.** O `emb_depth` adotado da fonte é **um só
número** (8e-6 m) para as 7 curvas, e a procedência registra que ele foi
ancorado justamente **nos c1 das Tabelas 8/9**. Uma profundidade *absoluta*
produz perda absoluta ~constante ⇒ perda **fracionária** ∝ 1/F₀ — que é o
`+0,995` medido. A fisica que falta é conhecida: o encaixe é achatamento
plástico de asperezas, **dirigido por pressão de contato**; a 25 % do
escoamento (o caso `T10Nm`) a pressão é baixa e o achatamento deveria ser
menor.

## 3. Controle negativo — e ele PASSA

Se o sinal vem do embedding, ele tem de sumir onde o embedding não carrega.
Medido nas 4 fontes que varrem pré-carga ≥2× com ≥4 curvas:

| fonte | fatia do embedding | `corr(\|salto\|, 1/F₀)` |
|---|---:|---:|
| `LU_2024` | **62,0 %** | **+0,883** |
| `LIU_2020_WEAR` | 52,2 % | +0,262 |
| `LI_2022_MARSTRUC` | 21,0 % | +0,707 |
| `CACCESE_2009` | **0,2 %** | **−0,447** |

`CACCESE_2009` é 99,5–99,9 % creep — o embedding responde por **0,2 %** da
perda — e é exatamente lá que o sinal **desaparece e troca de sinal**. A
ausência está onde o canal está ausente, que é o que um controle negativo tem
de mostrar.

⚠️ **O ponto fraco fica declarado:** `LIU_2020_WEAR` tem 52 % de embedding e só
**+0,262**. A correlação não é função monótona da fatia, então a leitura
honesta é *"o sinal exige o canal, mas o canal não garante o sinal"* — há outra
coisa modulando, e um prereg de adoção tem de tratar essa fonte como risco, não
como confirmação.

## 4. Barra de forma nomeada (o mesmo formato do ICMEZ/YANG_2021)

- **REGIME**: transversal, δ=1,0 mm; varredura de F₀ de **7×** dentro da fonte.
- **CANAIS**: embedding **62 %** da perda (0,698 absoluto contra 0,189 do
  rotacional).
- **FORMA**: profundidade de encaixe **independente da pré-carga** ⇒ excesso de
  perda no 1º ciclo ∝ **1/F₀** (r = +0,995), com **inversão de sinal** no
  extremo superior da varredura.
- **DADO**: limpo — e agora conferido, já que esta fonte acabou de passar por
  correção de pico espúrio com guarda permanente de monotonicidade.
- **ROTA JÁ DESCARTADA**: nenhuma alavanca livre fecha (4 varridas); a grade
  conjunta `emb_depth` × `N_emb` fecha 0 de 25; forma de cauda é impossível por
  aritmética (incremento tardio 0,0034); e o **split absoluto↔proporcional**
  está falsificado em 16 células (§5).

## 5. A rota que eu próprio propus PRIMEIRO — e a medição que a matou

O alvo do embedding no engine é

```
target = emb_depth · conformance(p) · settling(ρ) · freq_gate(f)
       + emb_load_frac · g_slip · F₀_init / k_b
```

ou seja **um termo absoluto** (fração ∝ 1/F₀) **somado a um termo proporcional
a F₀** (fração *constante*). Isso me deu a hipótese óbvia: se a fração cai
rápido demais com F₀, basta mover o *split* — baixar `emb_depth`, subir
`emb_load_frac`. A grade `emb_depth` × `emb_load_frac` (16 células, 7 curvas)
**falsifica a hipótese em ambos os eixos**:

| | efeito medido |
|---|---|
| subir `emb_load_frac` a `emb_depth` fixo | a `T10Nm` **piora** monotonicamente (0,2514 → 0,3440 em 0,40 → 0,85) |
| baixar `emb_depth` | a `T10Nm` melhora (até 0,1596) mas **nunca fecha** (3,2× o limite) |
| melhor célula para a alvo | fecha **0 de 7** — destrói as duas protegidas |
| célula nominal (vigente) | fecha **3 de 7** — nenhuma célula da grade a supera |

**Por que subir o termo proporcional piora:** ele *adiciona* perda, e o modelo
já perde demais. O sinal do meu raciocínio estava errado — eu pensei em achatar
a lei em F₀ e o que a curva pede é **menos perda total, só nas pré-cargas
baixas**.

**E por que baixar `emb_depth` não serve:** a `fig18_amp0p25` **pinça** esse
número (0,0337 → 0,0975 quando ele cai a 3e-6) e é **insensível ao
`emb_load_frac`** — a 0,25 mm o gate de slip fecha o termo proporcional, então
ela vê só o reservatório estático. A alvo precisa de `emb_depth` ≈ **2,7×
menor** do que a protegida permite. Mesma estrutura do `CHU_2026` e do
`ROUSSEAU_2025`: **a forma existe, a constante não transfere dentro da própria
fonte.**

## 6. A rota que sobra é FORMA, e a geometria das alavancas favorece

O engine **já tem** a lei de pressão para o encaixe — e ela está com o **sinal
oposto** ao que esta curva pede:

```python
S = min(1, (p_ref_emb / p_init) ** emb_conform_exp)     # exp <= 0 -> 1.0 exato
```

A docstring é explícita sobre a física que implementa: *"torque maior
pré-conforma mais asperezas ⇒ menos resíduo cíclico"*, e conclui *"fracional
cai mais rápido que 1/F₀"* — que é **agravar** exatamente o defeito medido. A
física que a `T10Nm` pede é o outro ramo, igualmente clássico: o achatamento
plástico é **dirigido por pressão**, logo a pré-carga baixa deveria produzir
encaixe **menor**. Isso é `S = min(1, (p/p_ref)^n)` — inalcançável hoje, porque
`_conformance_S` faz `if exp <= 0: return 1.0`, **curto-circuitando o expoente
negativo para inerte**.

**A geometria das alavancas é favorável, e isso é medição, não torcida:**

| curva | F₀ | papel |
|---|---:|---|
| `fig18_amp0p25` | 12 000 N | protegida (tripé) |
| `fig18_amp2p0` | 11 600 N | protegida (tripé) |
| `fig20_T22Nm` | 11 567 N | tripé (recém-entrada) |
| **`fig20_T10Nm`** | **5 963 N** | **alvo** |

As três que não podem piorar vivem **todas** em ~11,6–12 kN; a alvo está a
**metade** disso. Uma lei ancorada em pré-carga separa a alvo das protegidas
**por construção** — o que nenhuma das constantes atuais faz, porque todas
agem igualmente sobre as quatro.

## 7. ✅ EXECUTADO no mesmo dia — a lei está certa e **não basta**

O prereg `2026-08-16-lu2024-embedding-dirigido-por-pressao` foi escrito, o campo
`emb_pressure_exp` implementado default-inerte e a grade medida. Resultado
completo em **`lu2024_embedding_pressao_resultado.md`**; o essencial:

- **A lei conserta o que este documento disse que ela consertaria.** Queda no 1º
  ciclo: dado **0,362**, modelo antes **0,627**, modelo com a lei **0,344** — o
  resíduo em N=1 vai de **−0,265 para +0,018**.
- **O isolamento é exato**: as 12 irmãs movem **+0,0000** em toda a grade,
  porque 5 das 7 curvas da varredura (incluindo as 3 do tripé) estão acima da
  pressão de referência e o `min(1,·)` as deixa em S = 1 **exato**.
- ⚠️ **E mesmo assim a curva NÃO fecha sozinha** (melhor MAE 0,1599 = 3,2×): ao
  arrumar o 1º ciclo, aparece **um segundo defeito** que estava escondido atrás
  dele — o modelo colapsa até o `loose_arrest_floor` = 0,10 da fonte e trava
  lá, enquanto o dado retém **0,310**.
- Corrigindo os dois juntos a curva **fecha com folga** (0,0112/0,0284/0,0138,
  pior perna 0,55×) — mas o piso terminal **não tem lei de pré-carga** nesta
  fonte (retenção do dado **0,037/0,309/0,187/0,064/0,234** pela Tabela 9 do
  paper, não-monótona, `corr` com 1/F₀ = −0,51, núcleo absoluto variando **45×**)
  ⇒ seria fit por curva, e **nada foi adotado**. A não-monotonicidade é
  **física e publicada** (`lu2024_fig20_nao_monotonia_e_fisica.md`), o que fecha
  a rota por argumento estrutural: um piso *fracionário único* não gera terminal
  não-monótono.

**A leitura que fica:** esta curva tem **dois** defeitos, não um. O que este
documento nomeou é real, tem lei e tem alavanca. O outro é o piso terminal, e
ele é hoje uma pergunta sobre o **dado da fonte**, não sobre o modelo.

## 6. Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/ataque_curva.py lu2024_M8_fig20_T10Nm
```
A varredura de F₀ e o controle negativo são sondas de sessão sobre
`validation_store.json` + `initial_preload_N` do `ValidationCase`; a fatia por
canal vem da decomposição gravada no store.
