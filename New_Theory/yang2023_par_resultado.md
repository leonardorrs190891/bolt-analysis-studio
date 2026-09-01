# Execução do PAR `delta_free` + `loose_arrest_floor` — **G2/G3/G5/G7 passam; G4 e F4 reprovam**

**Executado em 2026-07-30.** Prereg:
`docs/superpowers/specs/2026-07-30-yang2023ijpem-par-deltafree-arresto-prereg.md`.
Sonda: `New_Theory/yang2023_par_exec.py`. **Nada adotado**; store e
`adopted_configs.json` intocados. Congelados: `delta_free` 122,96/129,18 µm ·
`loose_arrest_floor` **0,1025**.

| gate | resultado |
|---|---|
| **G2** ramo saturado melhora | **PASSA** — mediana res.máx 0,3513 → **0,2928** (−0,0585) |
| **G3** sub-crítico bit-idêntico | **PASSA** — mesmos dígitos |
| **G4** nenhuma pior que +0,01 | **REPROVA** — 1 curva, 1 perna |
| **G5** o piso único basta (teste de lei) | **PASSA** — 1 de 6 |
| **G7** resto do store | **PASSA** |
| **F4** ninguém abaixo do piso | **FALSIFICA** — 5 de 6 |

⇒ **O prereg reprova** (G4 era bloqueante). Mas o conteúdo é majoritariamente
positivo, e uma das duas reprovações é **erro meu de especificação**.

---

## O que passou, e é resultado de verdade

**G2 — as 6 saturadas melhoram, todas.** Nenhuma exceção:

| δ | res.máx |
|---:|---|
| 0,30 | 0,2200 → 0,1990 |
| 0,35 | 0,5600 → 0,5100 |
| 0,45 | 0,3600 → **0,2613** |
| 0,50 | 0,4098 → 0,3913 |
| 0,55 | 0,3426 → 0,3243 |
| 0,65 | 0,1600 → **0,0906** |

**G5 — o piso é aproximadamente uma constante da bancada.** Comparado o piso único
(0,1025) contra o piso **próprio** de cada curva, o próprio só ganha por >0,05 em
**1 de 6** (0,30 mm, +0,068). Nas outras cinco a diferença é ≤0,02. Isto é o achado
com mais valor da execução: **um número lido do platô descreve seis curvas em cinco
amplitudes diferentes** — é comportamento de lei, não de ajuste. A hipótese
parcimoniosa sobreviveu ao teste que existia para matá-la.

**G3 — bit-idêntico.** 0,15 e 0,18 saem com os mesmos dígitos, confirmando que
nem o `delta_free` novo nem o piso tocam o ramo que nunca escorrega.

**Curva 0,65 mm é a que mais se aproximou** — e é preciso ser exato sobre quanto:
res.máx **0,0906 passa** (era 0,1600), MAE **0,0532 NÃO passa** (limite 0,05, erra
por 0,0032) e σ_res **0,0612 não passa** (limite 0,025). Ela deixou de violar o
pico e passou a violar **duas** pernas, não uma. Severidade **4,07× → 2,45×**
(a perna que manda segue sendo o σ_res, nos dois casos).

## O que reprovou

**G4 — uma curva, uma perna.** `0,35 mm` tem MAE 0,1788 → 0,2103 (+0,0315),
**enquanto o res.máx dela melhora** (0,5600 → 0,5100). Ou seja: o pico encolheu e
a média cresceu — mudança de **forma** do resíduo, não de nível. É uma regressão
real e o gate a pegou; não é erro de especificação.

**F4 — e aqui o erro é MEU.** Escrevi *"nenhuma das saturadas pode terminar abaixo
do piso imposto"*. Cinco terminam: 0,0997 · 0,0854 · 0,0908 · 0,0942 · 0,1008
contra 0,1025 (excesso de 0,003 a 0,017). Mas o `self_locking_gate` do engine é

```
g = max(0, 1 − F_min/F_0)     e  g  MULTIPLICA d_theta
```

isto é, ele arresta **só o canal rotacional**. Wear, creep e embedding continuam
drenando depois que a rotação para, então o `ratio` total **pode** passar abaixo
do piso — é comportamento documentado ("S-curve com ponto fixo estável em F_min"
para *aquele canal*), não defeito. Eu tratei um arresto **por canal** como se
fosse um **clamp global**.

F4 disparou, e o registro tem de dizer isso; mas o que ele detectou foi a minha
especificação, não o modelo. A versão correta do falsificador limitaria a
**contribuição do canal rotacional**, não o `ratio` total — e isso é para um
prereg novo, não para reinterpretar este.

**Terceiro erro de especificação meu nesta sequência**, e vale nomear o padrão:
borda-de-intervalo (v1) · instantâneo-vs-trajetória (v2) · agora
por-canal-vs-global. Os três são a mesma falha: assumir a forma de uma quantidade
sem ler a definição dela no engine.

## G6 — a transição, como declarado

`0,25 mm`: ratio final previsto **0,0808** contra **0,520** medido (piso lido dela
0,580). Erro −0,439. Exatamente o previsto no prereg: com piso único de 0,1025,
o modelo sub-prevê o patamar dela por construção. A lacuna está **quantificada**:
a transição precisa de piso ~0,58 enquanto o ramo saturado pede ~0,10.

## Veredicto

O par **funciona no ramo saturado com duas constantes lidas do dado** e não é
adotável como está, por uma regressão localizada (0,35 mm) que o G4 pegou.
Nenhuma curva entra no tripé — como declarado antes de rodar.

**O que ficou estabelecido:**

1. o piso de arresto é **≈ constante da bancada** (G5, 5 de 6) — evidência de lei;
2. as duas constantes juntas tiram a fonte do regime binário: 6 curvas melhoram,
   e a 0,65 passa a violar **só** o σ_res;
3. a **transição continua sem forma**: piso 0,58 vs 0,10 no mesmo rig ⇒ é aqui, e
   só aqui, que a dependência de amplitude é necessária;
4. o falsificador F4 tem de ser reescrito em termos do canal rotacional.

## Follow-up

Prereg novo com (a) F4 corrigido para o canal, (b) diagnóstico do porquê a
`0,35 mm` piora em MAE enquanto melhora em pico — provavelmente a mesma
curvatura que a decomposição do σ_res mediu —, e (c) a decisão sobre a transição:
piso dependente de amplitude é **forma nova**, e a matriz de âncoras (D2b) diz que
esta fonte tem 9 amplitudes para ancorá-la.
