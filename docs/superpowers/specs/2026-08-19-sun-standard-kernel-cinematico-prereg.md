# PREREG — `sun…transverse_grease_standard`: kernel CINEMÁTICO no lugar do runaway (troca de forma, mesmo DOF)

**2026-08-19 (16:0x)** · **gates congelados neste commit** · store
`7a60cacb72de`, censo 144/205 · mandato das 15:39: *"melhore a modelagem de
…grease_standard.html"*.

## 1. O defeito, medido

A curva perde quase-linearmente (1,000 → 0,111 em 369 ciclos na janela; o cru
segue até um **platô em 0,028**). O modelo faz a forma S do torque-runaway:
quase certo até N≈88 (+0,05), **despenca** em N≈100–170 (resíduo −0,32) e
**trava** no floor. σ 0,1182 = **4,73×** — a pior perna das duas abertas do SUN.

**E a procedência do floor vigente está FALSA no valor** (classe do item R): o
adotado é **0,06** rotulado *"lido-do-dado (assíntota final crua)"*, mas o
leitor canônico (`arrest_floor_from_curve`) devolve **0,0284** — com
`plateau=False` (limite inferior; o critério de 2 % relativo numa base de 0,028
é apertado, e os 4 últimos pontos são 0,036/0,029/0,027/0,028). O irmão crimp
confere ao dígito (0,142, platô verdadeiro), o que valida o instrumento.

## 2. O pacote — e a conta de DOF que o legitima

| | vigente | proposto |
|---|---|---|
| kernel rotacional | torque-runaway (forma S) | `loose_rate_mode="graded_scrit"` — taxa **cinemática**, sem runaway (capacidade existente, default-inerte) |
| fitado 1 | `tr_loose_gain = 2,94` (*"fitado-this-rig POR PORCA"*) | `k_loose_graded = 0,020` (fitado, declarado) |
| fitado 2 | `loose_arrest_floor = 0,06` (**mal-rotulado** como lido) | `arrest_approach_exp = 8,0` (fitado, declarado) |
| lido | — | `loose_arrest_floor = 0,0284` — **do leitor canônico**, com a flag `plateau=False` declarada (limite inferior) |
| `s_crit_loose` | — | 0,0 (sem limiar; o excesso é o próprio slip) |

**Dois fitados trocam dois fitados** — DOF igual, forma certa no lugar da
errada, e o floor *ganha* procedência. A grade foi estendida **três vezes**
pela disciplina D-L; o ótimo legítimo é **interior** (vizinhos 1,66–2,09×).
⚠️ Células com floor 0,10–0,14 dão até 1,39× e foram **recusadas**: o dado cru
atravessa 0,14 (vale 0,080 em N=440) — seria a "barreira artificial" que a
regra do §7 do doc ICMEZ proíbe. A legitimidade custa 0,23× e está paga.

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | **a curva melhora nas 3 pernas** | valores preditos: MAE 0,0999→**0,0604** · res.máx 0,3193→**0,1103** · σ 0,1182→**0,0404**. Reproduzir a ±0,0005 |
| **G2** | **irmãs bit-idênticas** | as outras 7 do SUN não mudam NADA (per_case com token que NÃO case `nogrease` — conferir o matcher substring: "grease_standard" ⊂ "nogrease_standard"!) |
| **G3** | **isolamento** | Δ = 0 exato fora do `SUN_2025_CRIMP` |
| **G4** | **re-stamp íntegro** | adoção muda o fingerprint ⇒ re-simular os 210 e conferir fingerprint único |
| **G5** | **censo não encolhe** | 144/205 (a curva NÃO fecha — predição: σ 1,62× — e nada muda de estatuto) |
| **G6** | **rótulo do item R** | a prov do floor antigo (0,06 *"lido"*) é corrigida no mesmo ato — o valor que era "lido" não era |
| **G7** | **relatórios** | HTML regenerado; aging test verde |

## 4. Predições registradas

1. G1 reproduz a sonda ao dígito (mesmo caminho de override).
2. **A curva NÃO fecha** (σ 0,0404 = 1,62× contra limite 0,025) — isto é
   melhoria de modelagem, não fechamento; se fechar, investigar.
3. As 7 irmãs: Δ = 0,0000 (per_case bem tokenizado).
4. O censo fica 144; a `grease_standard` sai de 4,73× para 1,62× e deixa de ser
   a pior aberta do SUN (a crimp, 1,21×, passa a ser).


## Estado

EXECUTADO 2026-08-19 (16:3x): gates G1/G2/G6 verdes na hora; G3-G5 fechados no re-stamp e6b18851a6af. Resultado em sun_standard_kernel_cinematico_resultado.md (kernel adotado; a curva fechou no passo 2).
