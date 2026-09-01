# O canal de flanco **não** é rota alternativa ao stick — ele está a jusante do **mesmo zero**

**2026-08-07** · só-leitura · **nada adotado** · hipótese minha, falsificada
**pelo código**. Fortalece a P-14.

## A hipótese, e por que era boa

A auditoria de bifurcação de hoje mediu, nos 6 canais:

| canal | zerado | **ativo** (tripé/fora) |
|---|---:|---|
| `wear` | 99 | 106 → 60/46 (57 %) |
| `rotational_loosening` | 101 | 104 → 58/46 (56 %) |
| **`thread_fretting`** | 188 | **17 → 17/0 (100 %)** |

**Toda curva com o canal de flanco ativo passa o tripé.** E havia um casamento
físico aparente com o achado do dia: o `YANG_2021` está em **stick transversal
permanente** (slip 0,0000 µm), o que mata `wear` e `rotational_loosening` por
construção — mas o flanco é dirigido por carga **axial**, então pareceria uma
rota que o stick **não bloqueia**.

## ⛔ FALSIFICADA — e o guarda do próprio script pegou

Varredura de `k_wear_flank` (banda KB `[4e-15; 2e-14]` **mais** os 2 valores
adotados), com as constantes **compartilhadas** fixas (`flank_fret_depth`=2,5e-6,
`flank_amp_exp`=1,5) e o companheiro `flank_transverse_on`=1:

| `k_wear_flank` | procedência | tripé | soma MAE | **fret %** |
|---:|---|---:|---:|---:|
| 4,000e-15 | BANDA | 3/8 | 0,3328 | **0,0 %** |
| 2,000e-14 | BANDA | 3/8 | 0,3328 | **0,0 %** |
| 4,325e-14 | fora | 3/8 | 0,3328 | **0,0 %** |
| 2,154e-13 | fora | 3/8 | 0,3328 | **0,0 %** |

**Resultado bit-idêntico em 5 doses de 2 ordens de grandeza** ⇒ o canal **não
engatou** ⇒ **teste inválido**, não candidato morto. O script imprimiu o aviso
sozinho porque a checagem `fret_med < 1e-9` estava escrita nele — a lição de
2026-08-01 (Δ=0,0000 lido como "morto" quando era teste inválido) virou guarda.

## O código diz exatamente por quê — e é o oposto da hipótese

`ThreadFrettingLoss.rate()`, ramo transversal (L1862–1864):

```python
if (mat.flank_wear_on > 0.0 and mat.flank_transverse_on > 0.0
        and delta_amp is not None and slip_amp_override is not None
        and slip_amp_override > 1e-12 and F_clamp > 0.0):
```

**`slip_amp_override > 1e-12`** — o ramo transversal é gateado pelo **mesmo slip
resolvido** que está zerado. E o ramo axial (L1844–1845) exige
`delta_amp is None`, ou seja, **modo força** — fechado numa fonte disp-mode.

⇒ **em `YANG_2021` as duas rotas do flanco estão fechadas**: a axial porque a
fonte é disp-mode, a transversal porque o slip é zero.

## O que isto faz com a P-14: **fortalece**

O `max(0, ·)` do `resolve_transverse_slip` não desliga **dois** canais — desliga
**três**:

| canal | como o zero o mata |
|---|---|
| `wear` | `slip_amp` é o driver direto |
| `rotational_loosening` | `loosening_slip_gate` recebe slip 0 |
| **`thread_fretting`** (ramo transversal) | **gate explícito `slip_amp_override > 1e-12`** |

**Um único limiar duro desliga a física dissipativa inteira** em disp-mode. Isso
não estava na P-14 quando a escrevi, e é o argumento mais forte dela.

## Corolário verificado: o ramo transversal **nunca** esteve ativo no canônico

| verificação | resultado |
|---|---|
| chaves adotadas com `flank_wear_on > 0` | `LI_2022_TRIBOINT`, `LIU_2016` |
| chaves adotadas com **`flank_transverse_on > 0`** | **NENHUMA** |
| modo das 2 fontes com o canal ativo | `delta_mm = 0,0` ⇒ **modo força**, ramo **axial** |

⇒ **o "17/17 no tripé" é inteiramente do ramo AXIAL, em 2 fontes axiais.** Ele
não é evidência de rota transferível para disp-mode — é seleção (D-Q e D-V o
ligaram onde ajudava) **mais** modo. Ler aquele 100 % como mérito do canal em
geral teria sido erro de leitura de população, do mesmo tipo que o piso de
réplica do BAUER expôs hoje de manhã.

E o ramo transversal, construído em 2026-08-01, é **código sem uso canônico** —
gateado atrás de um slip que é zero em **18** curvas (medido direto, das 150
disp-mode).

⚠️ **Errata da mesma tarde:** a versão original desta frase dizia *"zero em **99
das 205**"*. Aquele 99 era a **primeira** contagem, e estava errada — vinha de
inferir stick da **decomposição** (`wear + rotational == 0`), o que confunde três
causas distintas: driver zerado (stick de verdade), constante zerada em config
(`LIU_2020_WEAR`/`KARLSEN_2022` têm `K_archard=0` e **deslizam 399 µm**) e gate
fechado. A contagem correta sai de instrumentar `resolve_transverse_slip`:
**18**. O argumento desta página não depende do número — o ramo segue sem uso
canônico porque **nenhuma config adotada liga `flank_transverse_on`** —, mas o
número tinha de ser o certo.

## Reprodutibilidade

```bash
py -3.12 New_Theory/flanco_transferencia_premeasure.py
```

A auditoria dos 6 canais e a checagem das chaves adotadas saem do store e do
`adopted_configs.json`, em segundos.
