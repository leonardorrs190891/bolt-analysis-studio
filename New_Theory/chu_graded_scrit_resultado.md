# CHU graded_scrit — F1 no premeasure: troca de kernel FONTE-INTEIRA é inviável

**2026-07-30** · `chu_graded_scrit_premeasure.py` (+ `.json`) · custo: ~280
sims curtas, zero adoção, zero prereg queimado.

## O alvo e por quê

Fila-23 pós-zhang: CHU_2026 ×6 é o maior bloco (σ até 3,8× o limite POR FONTE
0,0507). Assinatura medida antes: o modelo tem o MESMO shape de colapso em
todas as amplitudes (fração da perda na 2ª metade ≈ 0,26–0,28) enquanto o
dado varia (D0.4 sustentado 0,51–0,71; D0.7 tudo-cedo 0,02) — o kernel de
torque bifurca arrest/runaway e o regime intermediário não existe. O teto da
família aditiva já tinha provado que canal lento não fecha CHU. Candidato:
`loose_rate_mode="graded_scrit"` (taxa ∝ excesso sobre s_crit fixo,
default-inerte no engine) — o membro "bifurcação de limiar" da classe.

## O que a sonda mediu

1. **Bracket de s_crit por identidade do dado**: bisseção no próprio branch
   (referência = graded SUB-crítico, s_crit enorme) dá slip(D0.3) ≈ 66 µm ≤
   s_crit < slip(D0.4) ≈ 398 µm — fisicamente plausível (Bauer: 76–108 µm).
   ⚠️ A 1ª sonda usou `k_loose_graded=0` como referência e convergiu no teto
   das DUAS pontas: **k=0 não é referência válida** — o branch graded é
   early-return e k=0 CAI NO KERNEL DE TORQUE (a sonda media troca de kernel,
   não excesso). 3º exemplar da família de erro per-channel-vs-global.
2. **Grade (s_crit×k) 7×8 nas 4 leituras** (test2 D0.4, test3 D0.5, test4
   D0.7, test5 D1.0; split por identidade — primeiro teste de cada nível):
   **NENHUM ponto viável** (toleração +0,01 por perna). Dois porquês, ambos
   informativos:
   * `test3`/`test5` (hoje SÃOS: σ 0,037/0,044) saltam para 0,17–0,20 em
     TODO ponto da grade — o modo troca o kernel da fonte inteira e o fit
     atual dessas curvas DEPENDE do kernel de torque (+ máquina de dano).
     O candidato não falha por dose: falha por REMOVER o que funcionava.
   * para k ≥ 0,26 todas as linhas são idênticas ao dígito (J=0,22330) —
     assinatura de INÉRCIA (runaway até o gate de arresto clampar), a mesma
     armadilha catalogada em 2026-07-30 de manhã ("grade idêntica = inércia").

## Veredicto e o que ele NÃO diz

* **F1**: a parametrização "trocar o kernel da fonte inteira por graded no
  bracket físico" está morta ANTES de prereg — mesmo padrão do LIU_2016
  (F1 do creep compartilhado) e do LIU_2025 (F1 da família aditiva, medido
  no mesmo dia: melhor ponto viável fecha 0 curvas novas — o nível de MAE
  em amp0p25/0p3 é o defeito P5 do limiar N₉₅, não canal lento).
* **Não falsifica o MECANISMO graded para a família D0.4** — falsifica a
  aplicação fonte-inteira a (s,k) constantes. Para contar no requisito (b)
  da regra de parada, "bifurcação de limiar" ainda exigiria um teste
  pré-registrado de um desenho que não quebre test3/test5 por construção —
  e o único desenho assim é per-amplitude (flag de forma POR CURVA), que é
  exatamente a armadilha "7 números disfarçados de constante" salvo se
  ganhar fundamento físico (ex.: s_crit por rugosidade medida — test9 é
  Ra1,6 µm e os outros não têm Ra publicado ⇒ **data-limited para âncora**).
* CHU_2026 ×6 permanece form-limited com o diagnóstico MAIS fino do dia:
  regime intermediário inalcançável por (i) canal aditivo, (ii) troca
  fonte-inteira de kernel. O que resta é forma NOVA de engine (cláusula
  PR-3: autorização do professor) ou âncora nova de dado (Ra por espécime).

## Estado da classe (regra de parada, requisito b)

incubação FALSIFICADA · kernel desacelerante FALSIFICADO · CM INCONCLUSIVO
(não conta) · graded_scrit fonte-inteira **inviável no premeasure** (não
conta como falsificação pré-registrada) · bifurcação por-amplitude
**data-limited** (âncora Ra ausente). A parada continua NÃO disparando —
mas a fila de candidatos exequíveis desta classe no CHU esgotou; o pipeline
segue nos alvos tratáveis (LIU_2016 wear-anchored; LIU_2022_RETIGHT
near-miss; YANG_2021; CACCESE).
