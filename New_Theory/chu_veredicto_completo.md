# CHU_2026 — veredicto completo: TODAS as classes de mecanismo existentes, medidas e fechadas

**2026-07-31** · continuação sob "continue"×3 do professor sobre a fronteira.
Sondas: `chu_graded_scrit_premeasure` · `chu_kin_ceiling_probe` ·
`chu_damage_grid_probe` (+ scans analíticos no teto aditivo). Nada adotado.

## A pergunta e a resposta

*"O regime intermediário do CHU (D0.4–0.7, 6 curvas na fila, σ até 3,8×) é
alcançável com o que o engine JÁ tem?"* — **Não. E agora é medido, classe a
classe:**

| classe | instrumento | veredicto |
|---|---|---|
| canal lento aditivo (log-onset) | teto analítico per-curva | **F1** — mae_teto 0,086–0,25 ≫ 0,05 |
| troca de kernel (graded_scrit fonte-inteira) | grade 7×8 nas leituras | **F1** — test3/test5 dependem do kernel de torque (0,037→0,17+); k≥0,26 = inércia bit-idêntica |
| dreno graduado ADITIVO (composição) | premeasure analítico 37×59 | **F1** — fecha 0/6; dreno superposto não move N50 204→737 |
| teto cinemático (`loose_kin_ceiling`) | grade 7 valores, sims | **INERTE** bit-idêntico — o canal rotacional carrega ~0 no CHU |
| ratchet aditivo (`k_ratchet`) | mesma grade | **PIORA** as 8 uniformemente |
| máquina de DANO compartilhada (c_D, W_ref, k_dmg_wear, k_dmg_mu) | grade 54 pontos × 9 curvas | **move CERTO e não fecha**: nenhuma dose viável (mín. 3 pioras; fecha 0/6) |

## O achado que muda a leitura (não é beco: é porta com cadeado)

1. **A chave adotada `CHU_2026_test1` só casa o test1** — as outras 8 curvas
   rodam SEM máquina de dano (c_D=0 default). O colapso delas no modelo é
   wear auto-limitante (taxa ∝ F₀ ⇒ achata) — por isso o shape do modelo é
   igual em toda amplitude (frac2 ≈ 0,27) enquanto o dado varia (0,02–0,71).
2. **Ativar o dano produz o regime que falta**: `k_dmg_wear=4` leva o test2
   (D0.4) de sd 0,1897/fim 0,60 para **0,1077/fim 0,16** (dado: 0,14) — o
   colapso profundo sustentado que três famílias superponíveis não davam.
   Ti-on-Ti (galling/terceiro corpo) é exatamente a física que o
   `surface_damage` foi construído para carregar (TP7/reaperto).
3. **Mas o relógio de dano é monótono na amplitude e o dado NÃO é**:
   profundo em D0.4 (fim 0,14–0,18), raso em D0.5 (0,47–0,54), profundo em
   D0.7 (0,29), raso-truncado em D1.0 (0,58 a 319 ciclos). Dose única quebra
   sempre alguém (test5/test9 pioram quando test2 acerta). Dose
   POR-AMPLITUDE fecharia — e é a armadilha "7 números disfarçados de
   constante", vetada sem âncora por espécime.

## O que destrava (pedido de bancada agora PRECISO)

* **Ra por espécime** (só test9 tem, 1,6 µm): com rugosidade medida, o
  k_dmg/W_ref por classe de superfície vira INPUT (como emb_um via VDI), não
  fit — e a não-monotonicidade pode ser espécime, não amplitude.
* **1 réplica em D0.4 e D0.5**: decide se o padrão profundo/raso/profundo é
  física de regime ou scatter de espécime (o par D1.0 test5/test6 tem
  réplica e concorda a 0,003 — scatter existe e é pequeno LÁ; nada se sabe
  dos outros níveis).
* Alternativa de modelagem (decisão do professor, PR-3): estado de dano com
  dependência NÃO-monótona da amplitude (ex.: dano de interface que a
  amplitude alta LIMPA — third-body ejection), forma nova de engine.

## Regra de parada (aplicada)

Membro "dose compartilhada da máquina de dano" da classe CHU: **falsificado
por varredura completa com gates declarados** (54 pontos, critério de sonda
+0,01). A classe de forma "regime intermediário CHU" fica com TODOS os
membros exequíveis medidos ⇒ requisito (a) ✓ (≥2 instrumentos), (b) ✓ para
os membros existentes, (c) ✓ (retorno marginal do último candidato: 0
fechamentos). **Parada da classe DISPARA para candidatos de engine
existentes** — reabre com Ra/réplicas ou forma nova autorizada. As 6 curvas
permanecem na fila como form-limited com procedência completa.
