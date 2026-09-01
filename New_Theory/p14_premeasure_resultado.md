# P-14 premedida — a forma **troca réplica por réplica**, e o saldo é zero

**2026-08-09** · assinada (*"assino tudo"*) · **premeasure só-leitura, nada
implementado, nada adotado** · monkeypatch de `resolve_transverse_slip`.

## A forma testada

```
atual:  slip = max(0, δ − δ_t)
P-14 :  slip = max(ε·δ·(δ/δ_t)^q , δ − δ_t)     (ε = 0 ⇒ idêntico ao atual)
```

Microslip sub-limiar: abaixo do onset de gross slip, a zona anular escorrega e
dissipa (Cattaneo–Mindlin), em vez de dissipação **nula**.

## O resultado, em três doses

| ε | alvos que **entram** | riscos que **saem** | saldo no censo |
|---:|---:|---:|---:|
| 0,02 | 1 (`yang2021_r1`) | 1 (`yang2021_r2`) | **0** |
| 0,05 | 2 (`r1`, `amp1p0`) | 2 (`r2`, `r3`) | **0** |
| 0,10 | 0 | 2 | **−2** |

**Nenhuma dose tem saldo positivo.** Isso confirma o balanço que a própria P-14
já declarava (−1), agora medido com a forma real em vez de estimado pelo sinal
do viés.

## ⚠️ O achado que decide: a forma **troca réplica por réplica**

As curvas que mudam de lado são `yang2021_amp0p6mm_ax8kN` **r1, r2 e r3** —
**réplicas da mesma condição** (0,6 mm, 8 kN). O microslip adiciona perda às três
**igualmente** (mesmo config), e o efeito é oposto:

| réplica | antes | ε=0,02 | |
|---|---|---|---|
| `r1` | 0,0264 / 0,1012 / 0,0317 | **0,0156 / 0,0576 / 0,0225** | **entra** |
| `r2` | 0,0403 / 0,0487 / 0,0088 | 0,0577 / 0,0740 / 0,0153 | **sai** |
| `r3` | 0,0209 / 0,0387 / 0,0093 | 0,0381 / 0,0496 / 0,0104 | piora |

⇒ a `r1` precisava de **mais** perda e as irmãs **não**. Como o modelo as trata
identicamente, o que a forma está ajustando é a **dispersão entre réplicas**, não
um mecanismo. É a mesma armadilha que o piso de réplica do BAUER expôs em
2026-08-07: melhoria abaixo do ruído do próprio dado não é medição de física.

## ✅ O que sobrevive: um ganho físico grande, fora do placar

`10_Yang_2023_..._0_25_mm` (IJPEM) com ε = 0,05:

| | antes | depois |
|---|---:|---:|
| MAE | 0,1664 | **0,0831** |
| res.máx | 0,4256 | **0,1627** |
| σ | 0,1452 | **0,0555** |

**Metade do erro nas três pernas** — é a curva em stick mais extrema
(o modelo perde 5 % onde o dado perde 48 %). A física do microslip **funciona**
onde o stick é grosseiro; ela só não rende censo porque essa curva está
declarada por resolução e continua longe do tripé.

## Veredicto

**P-14 não é adotável como está.** Qualquer gate honesto exigiria *"os alvos
melhoram E os riscos não saem"*, e **isso falha em todas as doses testadas** — em
ε=0,02, a `r2` sai.

O que fica estabelecido, e é resultado:

1. **A física é real** — onde o stick é grosseiro (IJPEM), o microslip corta o
   erro pela metade nas três pernas;
2. **o alcance útil é minúsculo** — a população em stick com viés positivo e sem
   estatuto são 4 curvas, e 3 delas são réplicas que se anulam;
3. **a forma não é o gargalo** — o gargalo é que o modelo não distingue réplicas
   que o dado distingue.

⚠️ **Não descartar a forma:** ela deve ser reconsiderada se aparecer fonte em
stick grosseiro **com réplicas concordantes**. O IJPEM sozinho já justifica
mantê-la na fila como capacidade, não como adoção.

## Reprodutibilidade

Monkeypatch de `dsa.resolve_transverse_slip` com
`micro = ε·δ·min(δ/δ_t,1)^q`; 3 doses × 9 curvas. Scratchpad, minutos.
