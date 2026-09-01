# ADOÇÃO D-AC — `YANG_2019`: a regra do **artigo** escolheu, e não a métrica

**2026-08-10** · prereg `f236e34` (gates e **regra de escolha** congelados antes de medir) ·
executada sob a delegação permanente.

## A curva, e por que só o σ

`yang2019_M10_amp0p6_10Hz` reprovava **só no σ_res** (0,0351 contra 0,0250 = 1,40×); MAE
(0,0310) e res.máx (0,0665) passavam com folga. O resíduo dos 10 pontos é **negativo** de
N=200 a 4600 (−0,0426 a −0,0187), cruza zero em N≈5000 e vira **positivo** no joelho (+0,0400,
+0,0665) ⇒ **curvatura**, não nível. O diagnóstico independente concorda: |viés|/MAE = **0,31**.

O `YANG_2019` tinha **0 de 5** no tripé — esta é a **primeira** da fonte.

## Prova gravada, lida ANTES de propor (a disciplina que ontem retirou o candidato do CHU)

1. **Artefato de sensor.** A nota registra: *"0.6 mm/10 Hz trace has a **sensor artifact after
   5,300 cycles**"*. ✅ **Já tratado na origem** — a janela da métrica é N ∈ [0, 5300], 10
   pontos, **zero** após 5300. Não havia o que trimar, e a checagem custou minutos.
2. **P-9.** É a única curva a 10 Hz e a única em que a P-9 age; ela já havia cortado o viés de
   −0,0524 para −0,0097, então o que restava era **forma**
   (`p9_auditoria_contra_o_paper_resultado.md`).
3. **Rugosidade.** O cfg declara `emb_um = 5,0` — a fonte **tem** rugosidade declarada, ao
   contrário do CHU, onde essa mesma checagem invalidou um candidato meu.

## ⚠️ Duas alavancas empatavam no gate — e a regra é do ARTIGO, não da métrica

Ambas fechavam com **custo zero** na fonte, então o gate do D-AB não decidia. A regra declarada
no prereg usa o **invariante impresso** do próprio paper (Fig. 6: *frequência 5 vs 10 Hz quase
não importa*): vence quem deixar menor o `|Δviés|` do par casado `amp0p6_5Hz ↔ amp0p6_10Hz`.

| alavanca | `|Δviés|` do par | σ na curva-alvo | soma da pior perna (5 curvas) |
|---|---|---|---|
| **`k_wear_spec` = 1,5e-13** | **0,0455** ✅ | 0,0228 | 14,735 |
| `tr_loose_gain` = 2,6 | 0,0479 | **0,0214** | 14,683 |
| *(nominal)* | *0,0436* | *0,0351* | *16,162* |

⇒ **a regra escolheu `k_wear_spec`; a de melhor σ na curva-alvo era a outra.** Precedente D-I e
D-AA: quando regra e métrica discordam, **vale a regra**.

## ⚠️ Custo que a própria regra expôs — e que fica escrito

**As duas alavancas PIORAM o `|Δviés|` do par** contra o nominal (0,0436 → 0,0455 / 0,0479).
O critério físico diz que ambos os candidatos são levemente **anti-físicos**: eles afastam o
modelo da insensibilidade a frequência que o artigo reporta. A escolhida degrada **+4,4 %**,
enquanto o agregado da fonte melhora **8,8 %** (16,162 → 14,735).

⚠️ **Não adicionei gate sobre o `|Δviés|` depois de ver isso** — seria mover a trave após o
resultado. O prereg não o gateava, os gates congelados decidem a adoção, e o custo entra na
procedência gravada em vez de desaparecer.

## Gates — medidos

| # | gate | resultado |
|---|---|---|
| **Y1** | alvo fecha o tripé | ✅ **0,0292 / 0,0443 / 0,0228** |
| **Y2** | nenhuma piora MAE >+0,01 | ✅ **0** |
| **Y3** | nenhuma sai do tripé | ✅ 0 → **1** |
| **Y4** | isolamento fora do `YANG_2019` | ✅ Δ = **0,000000000** em 7 curvas |
| **Y5** | censo 143 → 144 | (abaixo) |
| **Y6** | suíte completa | (abaixo) |
| *extra* | predição da regra reproduzida nas 5 | ✅ ao dígito |

## Efeito nas 5 — **todas melhoram**

| curva | antes | depois | ΔMAE |
|---|---|---|---:|
| `amp0p4_5Hz` | 0,0995/0,1423/0,0773 | 0,0996/0,1423/0,0764 | +0,0001 |
| **`amp0p6_10Hz`** | 0,0310/0,0665/**0,0351** | **0,0292/0,0443/0,0228** ✅ | −0,0018 |
| `amp0p6_5Hz` | 0,0857/**0,5170**/0,1534 | 0,0744/**0,4638**/0,1378 | **−0,0113** |
| `varamp_large_to_small` | 0,0519/0,1364/0,0580 | 0,0492/0,1227/0,0546 | −0,0027 |
| `varamp_small_to_large` | 0,0636/0,1939/0,0803 | 0,0609/0,1839/0,0768 | −0,0027 |

Nenhuma piora além do ruído; **a maior melhora é numa curva que não era o alvo** (`amp0p6_5Hz`,
−0,0113 no MAE e −0,053 no res.máx). Isso é sinal favorável: uma constante que só servisse ao
alvo teria deixado as irmãs paradas.

## O que NÃO fica resolvido

A `amp0p6_5Hz` segue com res.máx **0,4638** (4,6× o limite) — a adoção a melhora, não a
conserta. E a `amp0p4_5Hz` fica praticamente intacta (+0,0001): ela é o alvo do candidato
"limiar graduado", não deste.

## Escopo

A fonte tem **2 grupos** (`YANG_2019`, `YANG_2019_varamp`) e a constante entrou nos **dois** —
verificado curva a curva (5/5 recebem 1,5e-13). Os grupos **já existiam**, então não se repetiu
o erro do D-AB (grupo novo criado por cópia de molde, que importava 11 constantes).

## Reprodutibilidade

```bash
py -3.12 New_Theory/ataque_curva.py yang2019_M10_amp0p6_10Hz
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
py -3.12 -m pytest tests/ -q
```
