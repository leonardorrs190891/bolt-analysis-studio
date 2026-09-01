# `sun…grease_crimp` — o cadeado de procedência **estava certo**, e verificá-lo virou a forma nomeada

**2026-08-16 (01:1x)** · só-leitura · **nada adotado** · store `20be19aabe11`,
censo **143/205**, 2ª linha **16 → 17**.

---

## 1. Por que esta curva

É **a mais perto de fechar de todo o conjunto aberto**: MAE **0,44×** ✅ ·
res.máx **0,89×** ✅ · σ **1,21×** ⛔ — falha **só o σ, por 21 %**.

## 2. O shell diz que ela FECHA — com uma constante travada

| alavanca | dose | MAE | res.máx | σ | |
|---|---:|---:|---:|---:|---|
| `loose_arrest_floor` | **0,162** | 0,0212 | 0,0551 | **0,0247** | ✅ **FECHA as 3** |
| todas as livres | — | — | — | ≥1,11× | ⛔ nenhuma fecha |

⚠️ Mas a procedência do `loose_arrest_floor` é **TRAVADA**: *"lido-do-dado
(assíntota final crua)"*. Mover constante com procedência para fechar métrica é
o que a lição da `fig7c` proíbe.

## 3. A pergunta legítima não é *"posso mover?"* — é ***"foi lido certo?"***

Isso é checagem de **procedência**, não caça a métrica: é a classe das correções
**D-W / D-X / D-U**, em que re-ler o registro corrigiu o valor.

**Medido:**

| | valor |
|---|---:|
| `loose_arrest_floor` vigente | **0,142** |
| assíntota do dado — média dos últimos 10 % | **0,1422** |
| mínimo dos últimos 10 % · último ponto | 0,1420 · **0,1420** |
| últimos 5 pontos do dado | 0,1432 · 0,1426 · 0,1426 · 0,1420 · 0,1420 |

⇒ **o cadeado está CERTO.** A leitura confere na 3ª casa, e a curva de fato
platoou.

## 4. E é isso que torna o `0,162` inaceitável

O valor que fecha a métrica **não é o piso do dado**: ele faria o modelo **parar
acima** de onde o ensaio parou. Fecharia o σ tornando o modelo **errado sobre o
ponto final** — trocaria uma perna da métrica por um erro físico.

⚠️ E o ponto final **já está certo**: `metric_pred` último = **0,1400** contra
dado **0,1420** — diferença de **0,002**.

## 5. A forma nomeada

Com o fim verificado correto e todas as alavancas livres esgotadas, o defeito
fica isolado:

> **o modelo chega ao valor final certo, pela perda total certa, mas por um
> CAMINHO diferente** — um **offset formado nos primeiros ciclos** (`ρ(res,N)`
> = **−0,10** ⇒ nível uniforme; maior salto em **u = 0,00**) que nunca se
> resolve.

Canais: rotacional **0,574** do total mas **0 % do tardio**; embedding **0 %**
tardio. O incremento tardio inteiro vale **0,00133** ⇒ *forma sobre o fim não
move esta curva* — coerente com o fim já estar certo.

⇒ **entra em `_FORMA_NOMEADA`**: forma = *offset inicial com extremidade
correta*; rota por `loose_arrest_floor` **recusada por procedência VERIFICADA**,
não apenas bloqueada.

## 6. O que isto ensina sobre cadeados

O shell marca `[PROV TRAVADA]` e segue. Fácil ler isso como *"não há rota"* e
parar. **Havia uma pergunta a mais**, e ela custou 30 segundos: *o valor travado
está certo?* A resposta (sim) **não** liberou a alavanca — mas converteu um
`sem rota` num **defeito nomeado**, porque provou que o erro não está no
extremo.

⇒ **cadeado verificado vale mais que cadeado respeitado.**

## Reprodutibilidade

`py -3.12 New_Theory/ataque_curva.py sun2025efa109235_transverse_grease_crimp`;
assíntota lida de `load_full_curve` com a normalização do runner (`r/r[0]`),
floor vigente de `rn._effective_overrides` — nenhum valor suposto.
