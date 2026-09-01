# LIU_2022_RETIGHT — re-atribuição bearing→flanco FALSIFICADA (sinais opostos ao longo da cadeia)

**2026-08-01** · prereg `2026-08-01-liu2022-fretting-de-rosca`. Receita do
Rousseau aplicada à fonte mais próxima do tripé (3 curvas a 1,07–1,16×).
**Nenhuma adoção**; fingerprint `a410d6537c83` intacto.

## O desacordo que motivou (real, e continua de pé)

Os autores atribuem a cauda ao **fretting entre flancos de rosca**; o
modelo a atribui a **wear de bearing** (49 % / 42 % / 18 % nas três) —
com o estágio inicial batendo (embedding = deformação plástica ✓) e creep
irrelevante (1–4 %, então a re-atribuição do LIU_2016 não é esta).

## ⚠️ O primeiro G0 foi INVÁLIDO — e teria virado "parâmetro morto"

Ligar `flank_wear_on`+`k_wear_flank` deu **Δ = 0,0000 exato** nas duas
doses: a assinatura clássica de parâmetro morto. **Era teste inválido**:
o canal de flanco é **axial-force-mode-only por default** e, numa fonte
transversal disp-mode, exige o companheiro **`flank_transverse_on`**
(engine, linha ~1737). Sem ele o canal não pode agir — o teste não
testou. É a mesma classe do Cattaneo-Mindlin de 2026-07-30 (gates nunca
chamados) e da armadilha `emb_um`/`emb_depth` de hoje de manhã.
**Regra reforçada: Δ=0 exato só é "morto" depois de conferir que TODOS os
companheiros do canal estão ligados.**

## G0 válido — FALSIFICADO por sinais opostos

| dose `k_wear_flank` | t1 (MAE/σ) | t2 (MAE/σ) | t4 (MAE/σ) |
|---|---|---|---|
| base | 0,0533 / 0,0269 | 0,0582 / 0,0193 | 0,0371 / 0,0270 |
| 5e-15 | 0,0539 / 0,0273 | 0,0588 / 0,0196 | 0,0369 / 0,0269 |
| 2e-14 | 0,0556 / 0,0286 | 0,0609 / 0,0205 | 0,0361 / 0,0265 |
| 8e-14 | 0,0626 / 0,0339 | 0,0689 / 0,0246 | **0,0331 / 0,0250** |

**t4 melhora (e o σ cruza o limite de 0,025); t1 e t2 pioram
monotonicamente.** Nenhuma dose única serve ⇒ redistribuição de erro, não
correção. G0 falha ⇒ **PARA, sem adoção** (ramo do prereg).

## O achado que fica (e o que ele proíbe)

O sinal **inverte com o índice de reaperto**: o flanco ajuda exatamente na
curva de superfície mais castigada (4º reaperto) e atrapalha nas
primeiras. Isso é fisicamente coerente com o que os autores descrevem
(dano de rosca ACUMULA a cada reaperto) — mas capturá-lo exigiria uma
**intensidade de flanco crescente com o dano acumulado**, isto é, uma
FORMA nova (`k_wear_flank` gateado por `D`), não uma constante.

Pelo critério do dia (a forma de amplitude foi recusada pelo mesmo
motivo): **não abrir forma sem dado que a exija além de uma fonte**.
Registrado como candidato com evidência — se outra fonte de reaperto
mostrar o mesmo sinal, aí há classe, não caso.

## Estado

As 3 seguem na fila (1,07–1,16×), agora com diagnóstico: **não é
constante faltando, é a dependência do canal com o histórico de
reapertos**. Censo inalterado: 132/205 · 173/205.
