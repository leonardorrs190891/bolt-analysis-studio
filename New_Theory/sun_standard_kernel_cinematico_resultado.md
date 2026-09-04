# `sun…transverse_grease_standard` — kernel CINEMÁTICO adotado: pior perna 4,73× → 1,62×, mesmo DOF

**2026-08-19 (16:0x–16:3x)** · prereg
`2026-08-19-sun-standard-kernel-cinematico` (gates congelados antes) · mandato
das 15:39: *"melhore a modelagem de …grease_standard.html"* · **ADOTADO** no
`per_case` `_grease_standard` do `SUN_2025_CRIMP`.

## 1. O defeito, e por que era de FORMA

O dado desce **quase-linear** (1,000 → 0,111 em 369 ciclos na janela; o cru
continua até um **platô em 0,028**). O modelo fazia a forma S do
torque-runaway: certo até N≈88, **despencava** em N≈100–170 (resíduo −0,32) e
**travava** no floor. As varreduras anteriores de constante (shell canônico)
paravam em 3,2× — porque nenhuma constante conserta a *forma*.

## 2. Dois achados de procedência no caminho

1. **O floor 0,06 estava mal-rotulado** (classe do item R): a prov dizia
   *"lido-do-dado (assíntota final crua)"* e o leitor canônico
   (`arrest_floor_from_curve`) devolve **0,0284** — com `plateau=False` (fim
   ainda em queda ⇒ limite inferior). O irmão crimp confere ao dígito (0,142,
   platô verdadeiro), o que valida o instrumento. Errata gravada na prov.
2. **`tr_loose_gain` é inerte sob o kernel graded** (medido: idêntico com
   2,94 / 2,0 / 0,0) — removido do per_case sem resíduo.

## 3. O pacote adotado, e a conta de DOF

```
loose_rate_mode  = "graded_scrit"   (capacidade existente, default-inerte)
k_loose_graded   = 0,02             (fitado, declarado)
arrest_approach_exp = 8,0           (fitado, declarado)
loose_arrest_floor  = 0,0284        (LIDO do leitor canônico; plateau=False declarado)
s_crit_loose     = 0,0
```

**Dois fitados trocam dois fitados** (gain 2,94 + floor falso-rotulado ⟶
k_graded + aexp), e o floor *ganha* procedência. A grade foi estendida **três
vezes** (disciplina D-L); o ótimo é **interior** (vizinhos 1,66–2,09×).

⚠️ **O que foi RECUSADO, e custou 0,23× recusar:** células com floor 0,10–0,14
davam até **1,39×** — e são ilegítimas: o dado cru **atravessa** 0,14 (vale
0,080 em N=440) e plateia em 0,028. Floor fitado acima de dado que passa por
ele é a "barreira artificial" que a regra do §7 do doc ICMEZ proíbe. A
legitimidade custa a diferença entre 1,39× e 1,62×, e está paga de propósito.

## 4. Gates

| # | gate | resultado |
|---|---|---|
| G1 | a curva melhora nas 3 pernas, reproduzindo a sonda ±0,0005 | ✅ **0,0999/0,3193/0,1182 → 0,0604/0,1103/0,0404** ao dígito, pelo caminho canônico |
| G2 | as 7 irmãs bit-idênticas | ✅ **IDENTICA nas 7** (token `_grease_standard` não casa `nogrease` — o underscore é o que o separa) |
| G3/G4 | isolamento + re-stamp íntegro | re-stamp dos 210 em andamento; fingerprint novo uniforme a conferir |
| G5 | censo não encolhe | predito 144 (a curva não fecha) |
| G6 | rótulo do item R corrigido | ✅ errata na prov do grupo |
| G7 | HTML + aging | após o re-stamp |

## 5. Predições do prereg — todas confirmadas até aqui

1. G1 ao dígito ✓. 2. **NÃO fecha** (σ 0,0404 = 1,62×) ✓ — melhoria de
modelagem, não fechamento. 3. Irmãs Δ=0 ✓. 4. A `grease_standard` deixa de ser
a pior aberta do SUN; a crimp (1,21×) assume ✓.

## 6. ✅ O resíduo restante foi FECHADO no mesmo dia (passo 2)

A leitura original desta seção ("curvatura tardia") foi refinada pela medição
seguinte: o que sobrava era um **arco** — modelo 23 % lento no 1º terço, 53 %
rápido no último — e a alavanca com procedência era o **creep**: a curva
herdava o `C_creep` do shared da âncora interna (1,87e-11) enquanto **os dois axiais standard
da própria fonte já usam 9e-11** (per-token, proxy L1).

**Passo 2** (prereg `2026-08-19-sun-standard-ccreep-token`): estender o valor do
token ao terceiro membro standard — **zero número novo, k intocado**. A greased
crimp rejeita o valor (medido antes: 3× pior), consistente com os axiais crimp
que nunca o receberam.

**Resultado final: 0,0191 / 0,0431 / 0,0223 — a curva FECHA O TRIPÉ** (censo
144 → 145). Trajetória completa do dia: σ **4,73× → 1,62× → 0,89×**, em dois
passos gateados, cada um com sua procedência.
