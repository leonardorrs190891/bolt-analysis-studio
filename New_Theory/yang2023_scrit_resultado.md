# Execução do prereg `s_crit_loose` no YANG_2023_IJPEM — **F2 FALSIFICOU na Fase A**

**Executado em 2026-07-29.** Prereg:
`docs/superpowers/specs/2026-07-29-yang2023ijpem-scrit-prereg.md`.
Sonda reproduzível: `New_Theory/yang2023_scrit_exec.py`.
Store de base `3546e6745448`. **Nada adotado. Nada fitado.** A execução parou no
falsificador F2, na fase da âncora, **antes** de qualquer métrica ser lida — que
é exatamente o que o gate G1 e o falsificador F2 existem para fazer.

## O que o F2 pegou

O prereg mandava ler `s_crit_loose` como a média geométrica do **slip resolvido**
em 0,18 mm (último que não afrouxa) e 0,25 mm (primeiro que afrouxa). Medido com
a função do próprio engine (`resolve_transverse_slip`, disp-mode):

| δ imposto | F₀ | slip resolvido (ciclo 1) |
|---:|---:|---:|
| 0,15 mm | 11,0 kN | **0,00 µm** |
| **0,18 mm** | 14,3 kN | **0,00 µm** |
| **0,25 mm** | 14,3 kN | **0,00 µm** |
| 0,30 mm | 11,0 kN | 65,8 µm |
| 0,35 mm | 14,3 kN | 86,0 µm |
| 0,45 / 0,50 / 0,55 / 0,65 | — | 186 / 266 / 286 / 386 µm |

A bracket colapsa para `[0, 0]`: **o engine põe 0,25 mm em STICK**. Média
geométrica de zeros não é âncora, e o F2 disparou.

## A causa — e ela é um desalinhamento de primeira ordem

O onset de slip do engine em disp-mode é
`onset = delta_free + F_slip/k_tr`. Decomposto nesta fonte:

| subgrupo | `delta_free` adotado | `F_slip/k_tr` | **onset** |
|---|---:|---:|---:|
| m6 (F₀ 11,0 kN) | 150 µm | 84,2 µm | **234 µm** |
| m8 (F₀ 14,3 kN) | **180 µm** | 84,0 µm | **264 µm** |

O onset é dominado pelo **take-up**, não pelo termo elástico. E aí está o
problema:

* o **DADO** troca de regime **entre 0,18 e 0,25 mm** — 0,18 retém 0,93, 0,25
  colapsa para 0,52 (e o próprio artigo chama 0,15/0,18 de *below threshold*);
* o **ENGINE** põe o onset **entre 0,25 e 0,30 mm** (264 µm no m8).

⇒ **desalinhado por ~um passo de amplitude.** Em 0,25 mm o modelo diz *stick*
enquanto o rig colapsa — e é por isso que essa curva é a pior do subgrupo
(MAE 0,166 · res.máx 0,426). Nenhuma forma nova conserta isso: a curva está do
lado errado do limiar **cinemático** antes de qualquer lei de taxa entrar.

## O que a varredura ANCORA de fato (e não era o que eu supunha)

`delta_free` tem procedência declarada **"lido-do-dado (take-up, regressão de
onset §4.19)"**, per-rig, limitado pela folga do furo. A varredura de amplitude
**é** o dado de onset. Então ela impõe uma restrição direta sobre ele:

```
o onset tem de cair entre 180 µm (0,18: não afrouxa) e 250 µm (0,25: colapsa)
onset = delta_free + 84 µm
  =>   delta_free  ∈  (96 , 166) µm      [subgrupo m8]
```

* **m8 adotado = 180 µm → FORA da faixa**, por ~8 % acima do teto.
* **m6 adotado = 150 µm → dentro** (96, 166) ✓.

A varredura ancora **`delta_free`**, não `s_crit_loose`. E diz que o valor
adotado do m8 é **inconsistente com a própria rota de procedência dele** — foi
lido por regressão de onset, mas não reproduz o onset que as duas curvas que o
cercam mostram.

## Por que eu paro aqui

O F2 do prereg é explícito: *"corrigir a conversão antes de qualquer conclusão
sobre a forma"*. Seguir em frente e fitar `k_loose_graded` com o limiar
cinemático desalinhado produziria um coeficiente que compensa um take-up errado —
um número que "funciona" e não significa nada. É o modo de falha que a campanha já
catalogou (`k_loose` saturando em 10 no reaperto, antes do `surface_damage`).

**Não** escolhi um `delta_free` novo nesta passada, de propósito: trocar o valor é
adoção, e adoção precisa dos seus gates. Escolher agora, olhando o MAE, seria fit
com nome de âncora — o mesmo G1 que respeitei na Fase A.

## Follow-up proposto (precisa de prereg próprio)

1. **Reler `delta_free` do m8 pela rota declarada** (regressão de onset sobre a
   varredura), com a bracket `(96, 166) µm` como restrição, e a média geométrica
   do intervalo como valor — mesma receita da Fase A, agora no parâmetro certo.
2. Gates análogos: G1 (a leitura não olha o erro) · **G3 continua sendo o mais
   crítico** — 0,15 e 0,18 passam hoje, e baixar o take-up **aumenta** o slip,
   logo pode quebrá-las · G4 nada pior no resto do store.
3. **Só depois** disso o `s_crit_loose` volta a fazer sentido: com o onset
   alinhado, a bracket de slip deixa de ser `[0, 0]` e a âncora original do
   prereg passa a ser calculável.

## Ganho desta execução

Zero curvas fechadas — e um defeito de input encontrado numa fonte que estava na
fila para receber **forma nova**. A ordem de causa importa: se a forma tivesse
sido ajustada primeiro, ela teria absorvido o erro de take-up e o defeito ficaria
escondido dentro de um coeficiente calibrado, com o `delta_free` errado
preservado. O prereg pagou-se aqui.
