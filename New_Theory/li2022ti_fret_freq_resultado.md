# `fret_freq_exp` no LI_2022_TRIBOINT — a forma está CERTA, e o G3 barra

**2026-08-04** · prereg `2026-08-04-li2022ti-fret-freq-prereg.md` (decisão
D-G, por delegação). Fingerprint intacto: `63722b266dc0`. Executor:
`New_Theory/li2022ti_fret_freq_exec.py`.

## Veredicto: NÃO ADOTA — `axial_10Hz_full` estoura o G3 em +0,054

Dose **LIDA** do dado (`exp = 1,0065`, `f_ref = 15 Hz`):

| curva | MAE | res.máx | σ_res | leitura |
|---|---|---|---|---|
| `axialmin_10Hz` (alvo) | 0,0526 → **0,0384** (−27 %) | 0,0779 → 0,0686 | 0,0242 → **0,0296** | melhora o nível, **estoura o σ** |
| `axialmin_15Hz` (held-out) | **+0,0000** | **+0,0000** | **+0,0000** | **bit-idêntico** |
| `axialmin_20Hz` | 0,0201 → **0,0139** | 0,0643 → **0,0433** | 0,0248 → **0,0181** | **melhora nas 3** |
| `axial_10Hz_full` | 0,0317 → 0,0491 | 0,0517 → **0,1057** | 0,0365 → 0,0572 | **destruída** (viola o res.máx) |

* **G1 falha**: o 10 Hz não fecha. O MAE cai 27 %, mas o σ sobe de 0,0242 para
  0,0296 e a perna que manda **troca** de MAE para σ.
* **G2 passa, e de forma notável**: o held-out de 15 Hz saiu **bit-idêntico**
  (`+0,0000` nas três pernas), exatamente como previsto — o fator nele é
  1,000. Isso valida o instrumento: não há acoplamento espúrio.
* **G3 FALHA**: `axial_10Hz_full` piora **+0,0540** no res.máx (limite
  +0,010) e passa a violar o teto de 0,10.

## O que ficou CONFIRMADO, e é resultado de física

A dependência de frequência é **real** e o expoente lido está na direção
certa. A prova mais limpa é o **20 Hz**, que melhora nas **três** pernas ao
mesmo tempo (MAE −31 %, res.máx −33 %, σ −27 %) — isso não é o que uma
alavanca arbitrária faz; é o que faz uma alavanca cuja forma corresponde ao
defeito.

E a magnitude do defeito segue medida: expoente **1,0065** no dado contra
**0,0038** no modelo ⇒ o modelo entrega **0 %** da dependência de frequência
de uma fonte cujo próprio artigo diz *"wear debris + spalling grows as
frequency decreases"*.

## Por que a curva longa quebra — e por que NÃO se conserta por config

`axialmin_10Hz` (janela 200..**200 000**) e `axial_10Hz_full` (200..**330 000**)
são o **mesmo ensaio a 10 Hz**, com janelas diferentes. Logo recebem o
**mesmo** fator 1,504. Uma melhora o nível; a outra é destruída.

O motivo está registrado desde 2026-07-30: a `axial_10Hz_full` pertence ao
cluster de **deriva TARDIA** (`cm_d2linha_resultado.md`), cujo excesso de σ
está **inteiro além de 200 k ciclos**. Amplificar o fretting em 50 % amplifica
justamente essa cauda.

Separar as duas em grupos de config diferentes **fecharia o gate e seria
fraude de escopo**: são o mesmo ensaio, e a única diferença é até onde a
figura foi digitalizada. Um coeficiente de desgaste não depende de onde a
curva foi cortada. Recusado sem medir.

## Custo do G5, medido (a varredura de controle)

A varredura de controle existia para **medir** o custo de escolher por
procedência, não para escolher. Nenhum expoente da grade (0,5 · 0,75 · 1,0 ·
1,25 · 1,5 · 2,0) fecha o alvo, e **todos** estouram o G3 na curva longa —
o menor estrago é `exp=0,5` com +0,0205 no res.máx, ainda o dobro da
tolerância. Ou seja: **não havia escolha melhor a ser feita por MAE**, e o
valor lido não custou nada em relação a um fit. Bom de registrar: aqui
procedência e ajuste não estavam em conflito.

## Consequência

A capacidade `fret_freq_exp` segue **construída e não adotada** — agora com
número: ela conserta o 20 Hz nas três pernas e é incompatível, nesta fonte,
com a cauda tardia da curva longa. O caminho para adotá-la passa por
**resolver a deriva tardia primeiro**, não por afrouxar o gate.

A predição registrada acertou 2 de 3: o 15 Hz ficou intacto (previsto), o
20 Hz melhorou (previsto), o 10 Hz **não fechou** (eu previa que fecharia — o
MAE caiu como esperado, mas eu não previ que o σ subiria acima do limite).
