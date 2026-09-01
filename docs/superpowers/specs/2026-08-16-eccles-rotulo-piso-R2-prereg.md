# ✅ EXECUTADO — ramo **ADOTADO**, gates **6/6**, predições **4/4**

> **Fechado 2026-08-16 (17:2x).** Fingerprint `20be19aabe11` → **`7a60cacb72de`**
> (210 registros, **1** fingerprint). Resultado: `New_Theory/eccles_rotulo_R2_resultado.md`.
>
> | gate | resultado |
> |---|---|
> | **G1** censo intacto | ✅ **144/205**, fora 61, abertas 21, `form_limited` 1 |
> | **G2** métricas bit-idênticas nas 2 | ✅ **Δ = 0,00e+00** nas três pernas |
> | **G3** isolamento | ✅ **0** de 210 com métrica alterada (contra `git show HEAD:` do store) |
> | **G4** fingerprint uniforme | ✅ **210 / 1** |
> | **G5** suíte completa | ✅ **988 passed · 1 skipped**, idêntico ao baseline |
> | **G6** o rótulo não mente | ✅ |
>
> **Predições 4/4**, incluindo a que testava a própria doutrina: o fingerprint **mudou**,
> confirmando que `prov` entra no hash. Se não tivesse mudado, o ramo seria `INCONCLUSIVO`
> e o `CLAUDE.md` estaria errado nesse ponto.
>
> ⚠️ **Duas armadilhas documentadas foram atravessadas e vale registrar que ambas mordiam:**
> (a) o rótulo antigo era **compartilhado por 8 grupos** do `ECCLES` — substituição ingênua
> teria mudado os 8; escopei aos 2 e reli o arquivo comparando com o que quis escrever.
> (b) o `parallel_batch` cobre **209** e o corpus tem **210** — o `exemplo_m12_sintetico`
> ficou com o fingerprint velho e **sozinho reprovaria o G4**; conserto por re-sim direta
> com carimbo manual, como o `CLAUDE.md` prescreve (`--cases` não o alcança).

---

# PREREG — item **R**, rota **R2**: re-rotular os 2 pisos do `ECCLES_2010`

**2026-08-16 (16:4x)** · **gates congelados neste commit** · store `20be19aabe11`,
censo **144/205**, fora 61, abertas 21, `form_limited` 1 · assinatura do professor
*"assine tudo e continue"* (16:37).

---

## 1. O que se muda, exatamente

**Só o rótulo de procedência.** Dois campos de texto em `New_Theory/adopted_configs.json`:

| grupo | `cfg.loose_arrest_floor` | `prov.loose_arrest_floor` hoje |
|---|---:|---|
| `ECCLES_2010_fig7d` | **0,137** (INALTERADO) | `"lido-do-dado (assintota final crua >=0.03; fisica=torque de prevalencia)"` |
| `ECCLES_2010_fig8a` | **0,059** (INALTERADO) | idem |

⛔ **Nenhum número de `cfg` é tocado.** Nenhuma outra fonte é tocada.

## 2. Por que R2 e não R1 — a medição inverteu a recomendação

A proposta original (13:4x) recomendava **R1** (corrigir os números para a leitura L24 do
cru, 0,0 e 0,0122), sob a leitura *"o piso não é sustentado pelo dado, logo está errado"*.

**O relógio (14:5x) mostrou outra coisa** (`eccles_piso_nao_sustentado_pelo_dado.md` §4b):

| nível | dado cru | modelo (piso 0) | razão |
|---:|---:|---:|---:|
| 0,60 | 64 | 65 | **1,01×** |
| 0,40 | 100 | 96 | 0,96× |
| 0,25 | 153 | 114 | 0,75× |
| **0,10** | **1643** | **130** | **0,08×** |

⇒ **não é erro de nível** — o modelo bate o dado ao dígito até 0,40. É **desaceleração de
cauda** ausente: o dado leva 1643 ciclos de 0,25 a 0,10; o modelo cobre em **16**.

`loose_arrest_floor` é a **única alavanca anti-runaway** do engine (`self_locking_gate`), e
quem adotou a usou para **imitar essa desaceleração** — tendo de inflá-la acima da assíntota
para morder a tempo. ⇒ **o número faz trabalho físico real; o rótulo é que mente.**

R1 corrigiria a procedência e deixaria as 2 curvas **piores e sem alavanca** (MAE
0,0665→0,1641 e 0,0489→0,0945) — honesto e sem rota. **R2 preserva a física e conserta a
afirmação**, que é o defeito de fato.

## 3. Rótulo NOVO (texto exato a gravar)

```
proxy-de-desaceleracao-de-cauda (fitado-this-rig; NAO e leitura do dado:
a leitura L24 do CSV cru da 0.0000 na fig7d e 0.0122 na fig8a, com
plateau=True. O valor aqui imita a desaceleracao MEDIDA da cauda -- dado
leva 1643 ciclos de 0.25 a 0.10 e o modelo 16 -- porque
loose_arrest_floor e' a unica alavanca anti-runaway do engine.
Escopo medido: sub-populacao de 5 curvas em 3 fontes, NAO classe --
o KARLSEN_2022 (7 curvas) e' controle negativo.
Ver New_Theory/eccles_piso_nao_sustentado_pelo_dado.md)
```

## 4. GATES — congelados

| # | gate | critério | bloqueante |
|---|---|---|:--:|
| **G1** | **censo intacto** | `_censo()` devolve **144/205**, fora **61**, abertas **21**, `form_limited` **1** — idêntico | ✅ |
| **G2** | **métricas bit-idênticas** | re-simulando as **2** curvas do `ECCLES` tocadas: `mae`/`maxerr`/`resid_std` **iguais ao dígito** ao store atual (rótulo não é física) | ✅ |
| **G3** | **isolamento** | nenhuma outra das 210 muda de `mae`/`maxerr`/`resid_std` | ✅ |
| **G4** | **fingerprint uniforme** | depois do re-carimbo, **todos os 210** registros carregam o MESMO fingerprint novo (≠ `20be19aabe11`), zero mosaico | ✅ |
| **G5** | **suíte completa** | `py -3.12 -m pytest tests/ -q` sem falha nova (baseline **988 passed / 1 skipped**) | ✅ |
| **G6** | **o rótulo não mente** | o texto gravado (a) nega explicitamente ser leitura do dado, (b) traz os 2 valores L24 reais, (c) declara o escopo medido como sub-população e não classe | ✅ |

**Ramos possíveis:** `ADOTADO` · `REPROVADO` (qualquer gate) · **`INCONCLUSIVO`** (o teste não
testou — p.ex. re-carimbo parcial, ou o fingerprint não mudar, o que significaria que o
`prov` **não** entra no hash e a premissa da §5 está errada).

## 5. Predição registrada — ANTES de executar

1. O fingerprint **muda** (o `CLAUDE.md` afirma que o hash cobre a entry inteira, incl.
   `prov`). ⚠️ Se **não** mudar, o ramo é `INCONCLUSIVO` e vira achado próprio: a doutrina
   documentada estaria errada.
2. **Zero** curvas mudam qualquer métrica — rótulo não é física.
3. Censo permanece **144/205**.
4. As 2 curvas seguem **fora** do tripé (`fig7d` MAE 0,0665 = 1,33× · `fig8a` res.máx
   0,1320 = 1,32×) — R2 **não** compra censo, e não deve.

## 6. O que este passo NÃO é

Não é adoção de constante (nenhum `cfg` muda), não é forma nova de engine, não é
reclassificação de camada. É **conserto de uma afirmação de procedência** que a medição
contradiz. A forma faltante que a medição nomeou — *desaceleração de cauda no canal
rotacional* — fica registrada como **candidata de escopo limitado** (5 curvas em 3 fontes;
`relogio_de_cauda_e_subpopulacao.md`), **não** proposta aqui.
