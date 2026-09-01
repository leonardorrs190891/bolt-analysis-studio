# `eccles2010_fig6_annotated_4kN_axial` — o alvo está **FORA do alcançável**, e agora com teto medido

**2026-08-21 (12:5x)** · só-leitura · **nada adotado** · store **`2b862e94aaec`**
(uniforme, 210 registros) · árvore limpa dos artefatos compartilhados.

Ataque pedido pelo professor. A curva é **exceção F5 assinada** com a prova
*"sobreposição axial (G-B1 FAIL: receita PR-31 levou o res.máx de 0,467 a 1,028) — o
engine não tem contorno axial externo"*.

---

## 1. Por que valia re-atacar uma curva com teto já registrado

O `excecoes_teto_por_curva.md` registra, para as 6 exceções do ECCLES:

> `eccles ×6 | 0,043–0,147 | **= vigente** | **zero alavanca move** (contorno axial inexistente)`

⚠️ Mas aquele teto foi medido com o `ataque_curva.py` **antes** dos consertos de
2026-08-21, e um deles atinge esta fonte: a alavanca **`t_0` estava MORTA** em toda a
campanha (a tabela dosava `t_0_creep`, campo que não existe em `JointMaterial`, e a injeção
era filtrada em silêncio). O ECCLES é **exatamente** a fonte onde o `C_creep` per-par foi
adotado (D-AB) ⇒ o **relógio de creep estava insondável numa fonte de creep**.

*(O outro conserto — base vazia ⇒ canal de wear insondável — **não** atinge o ECCLES: ele
não está entre as 4 fontes afetadas.)*

## 2. Diagnóstico: o erro se forma em **u = 0,00**

| | |
|---|---|
| pernas | MAE 0,1466 (**2,93×**) · res.máx 0,4737 (**4,74×**) · σ 0,1892 (**2,71×**) |
| perna que manda | **res.máx** |
| viés | −0,0895 · resíduo por terço **−0,2930** / +0,0884 / −0,0386 · troca de sinal **SIM** |
| maior salto | entre os ciclos **0 e 62**, Δ = **−0,2839**, em **u = 0,00** |
| curvatura | **A** (rápido cedo, devagar tarde) |

⇒ *"o erro se forma CEDO — mexer no fim não adianta"*. O modelo perde ~0,28 de pré-carga a
mais que o dado nos **primeiros 62 ciclos**, que é a leitura física de *"falta o contorno
axial externo"*: com 4 kN axiais superpostos a junta retém mais do que o modelo prevê.

## 3. A varredura com o instrumento CORRIGIDO

O `t_0`, agora vivo, **não é a resposta** — e isso passou a ser medido em vez de não-testado:

| alavanca | dose | MAE | res.máx | σ | |
|---|---|---:|---:|---:|---|
| `t_0` | 0,3 · 3,0 | 0,1480 · 0,1455 | 0,4824 · 0,4664 | 0,1905 · 0,1881 | quase não move |
| `emb_depth` | **7,7e-06** | 0,1381 | **0,4075** | 0,1806 | melhor livre |
| `N_emb` | 100 | 0,1392 | 0,4630 | 0,1785 | — |
| `C_creep` · `k_wear_spec` · `loose_arrest_floor` | — | — | — | — | **TRAVADAS** (procedência) |
| `K_archard` | 4 doses | **bit-idêntico** | | | **INERTE** — e isto é correto |

⚠️ **O `K_archard` inerte aqui é confirmação do conserto, não falha dele:** no ECCLES o
`k_wear_spec` está **ativo** no cfg (com procedência), então a via legada K/H não é usada e
`K_archard` genuinamente não faz nada. O conserto de 2026-08-21 só acrescenta a alavanca
**onde a via legada está viva** — não cria alavanca falsa onde não está.

## 4. ⚠️ TETO DE AUTORIDADE — o alvo não está no alcançável

Método D-L: suprimir o canal **por inteiro** e perguntar se o alvo é sequer atingível.

| cenário | MAE | res.máx | σ |
|---|---:|---:|---:|
| NOMINAL | 0,1466 | 0,4737 | 0,1892 |
| **embedding OFF** (`emb_depth = 0`) | 0,1442 | **0,3242** | 0,1681 |
| creep OFF (`C_creep = 0`) | 0,1439 | 0,4528 | 0,1878 |
| wear OFF (`k_wear_spec = K_archard = 0`) | 0,3488 | 0,5448 | 0,3073 |
| **TUDO OFF** menos rotacional | 0,5149 | **0,8583** | 0,3341 |

**Duas conclusões, e a segunda é a que fecha o caso:**

1. **O canal culpado do início é o EMBEDDING.** Suprimi-lo leva o res.máx de 4,74× a
   **3,24×** — a maior melhora de qualquer intervenção, e coerente com o erro nascer em
   u = 0 (embedding é o único canal com relógio de dezenas de ciclos).
2. **Mesmo com o canal culpado ZERADO, o alvo fica a 3,24× do limite** ⇒ o alvo
   (res.máx ≤ 0,10) está **FORA do conjunto alcançável** por qualquer combinação destas
   constantes. Não é "nenhuma dose fecha": é **o teto do canal não chega lá**.

⚠️ **E "tudo off" PIORA** (0,4737 → 0,8583): o modelo não perde demais em bloco — ele perde
**demais cedo** (embedding) e **de menos tarde** (o wear é necessário: desligá-lo leva o MAE
de 0,1466 a 0,3488). É problema de **redistribuição dentro da janela**, a mesma classe da
`liu2025_M16_amp0p8`, e nenhuma constante o resolve porque cada canal é **monótono** na
janela.

## 5. O que isto acrescenta ao estatuto (e o que não muda)

A exceção **não muda** — segue assinada, e a prova gravada segue verdadeira. O que este
ataque acrescenta é **força**: de *"zero alavanca move"* (afirmação sobre as doses testadas,
com uma alavanca morta entre elas) para *"**o alvo está fora do alcançável mesmo com o canal
culpado suprimido**"* — que é uma cota, não uma varredura.

⇒ para o material de artigo, isto converte a exceção de *"não achamos rota"* em *"há um
limite superior medido, e ele está 3,2× acima da meta"*.

**A forma que faltaria, nomeada:** contorno axial externo — a parcela do carregamento axial
de 4 kN que **alivia** o parafuso em vez de somar-se a ele. Não é constante: é um caminho
de carga que o engine não representa (`F_ax` entra só via `L_ax = Φ·sin(β)·F_ax`, sem
divisão de carga com o membro). Forma nova ⇒ **assinatura**, e não proponho aqui.

## Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/ataque_curva.py eccles2010_fig6_annotated_4kN_axial
```
mais sonda de teto embrulhando `rn._effective_overrides` com `{emb_depth:0}`, `{C_creep:0}`,
`{k_wear_spec:0, K_archard:0}` e a união — nada escrito no store nem no config.
