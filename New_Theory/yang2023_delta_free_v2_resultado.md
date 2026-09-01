# Execução v2 do `delta_free` — **cinemática CERTA, adoção REPROVADA (G4/F3)**

**Executado em 2026-07-30.** Prereg:
`docs/superpowers/specs/2026-07-30-yang2023ijpem-delta-free-v2-prereg.md`.
Sonda: `New_Theory/yang2023_delta_free_v2_exec.py`.
**Nada adotado.** Store e `adopted_configs.json` intocados.
Valores congelados no G1: `delta_free` = **122,96 µm** (m6) · **129,18 µm** (m8).

| gate | resultado |
|---|---|
| **G2** cinemática em TODOS os ciclos | **PASSA** |
| **G3** ramo sub-crítico no tripé | **PASSA** — e **bit-idêntico** |
| **G4** nenhuma pior que +0,01 | **REPROVA** — 5 das 7 pioram |
| **G5** escopo | **PASSA** |
| **G6** regime (informacional) | 0,25 mm prevê **0,000** contra 0,520 medido |

⇒ Como o prereg definiu sucesso como `G2 ∧ G3 ∧ G4 ∧ G5`, **o prereg reprova**, e
o falsificador **F3** dispara (G4 falhou em ≥3 das 7).

---

## O que funcionou, e funcionou exatamente como escrito

**G2 — o interior da janela é estável, a borda não era.** Com o valor no interior,
`slip = 0` em **todos os 2000 ciclos** de 0,15 e 0,18 mm, e 0,25 mm passa a
escorregar **do ciclo 1** (213 ciclos com slip, máx 119,8 µm):

| amp | ciclos com slip | 1º slip | slip máx |
|---:|---:|---:|---:|
| 0,15 | **0** | — | 0,00 µm |
| 0,18 | **0** | — | 0,00 µm |
| 0,25 | 213 | 1 | 119,83 µm |
| 0,30 | 96 | 1 | 177,03 µm |

**G3 — bit-idêntico.** 0,15 e 0,18 saem com MAE 0,0093 e 0,0076, res.máx 0,0241 e
0,0156 — **os mesmos dígitos de antes**. Baixar o take-up de 180 → 129 µm não
tocou o ramo sub-crítico, porque ele continua em stick permanente. É a
confirmação direta do diagnóstico do v1: o problema do v1 era a **borda**, não a
rota.

## O que reprovou, e era o previsto

**G4 — 5 das 7 pioram.** Mediana do res.máx da fonte 0,3600 → 0,4200 (+0,06).
A única que melhora é 0,50 mm (MAE 0,2386 → 0,1890 · res.máx 0,4098 → 0,3473);
0,65 mm fica praticamente igual.

**G6 diz por quê, e é a bimodalidade:**

| amp | ratio final previsto | medido | erro |
|---:|---:|---:|---:|
| 0,25 mm | **0,000** | 0,520 | −0,520 |
| 0,30 mm | **0,000** | 0,220 | −0,220 |

Destravar o 0,25 mm não o levou ao decaimento gradual do dado — levou ao
**runaway até zero**. O modelo troca "stick permanente" por "perda total", e o
dado quer o meio. Antes o erro era *não afrouxar*; agora é *afrouxar demais*, e a
segunda forma de errar é maior.

**Isto estava escrito no prereg antes de rodar:** *"destravar o 0,25 provavelmente
o joga no runaway: acerta o início e erra o fim (~0 contra 0,520 medido). Se for
isso, o `delta_free` correto é condição necessária e NÃO suficiente."* Foi isso.

## Veredicto

A correção do `delta_free` está **certa como procedência** (G2 e G3 provam: o
limiar cinemático passa a coincidir com o limiar declarado pelo artigo, sem tocar
o ramo sub-crítico) e **não é adotável sozinha** (G4/F3). Ela remove um defeito
real e expõe outro que estava escondido atrás dele — o modelo não tem regime
intermediário entre arresto e zero.

Adotar só ela pioraria o store, e é por isso que o gate existe.

## O que isto entrega para o passo seguinte

O `loose_arrest_floor` (piso de arresto: fração de F₀ onde o dreno trava) passa a
ter **premeasure direto**: o dado pede piso **0,520** em 0,25 mm e **0,220** em
0,30 mm.

E já entrega o problema: **os dois pisos são diferentes na mesma bancada**. Um
`loose_arrest_floor` constante per-rig **não** reproduz os dois — ele teria de
depender da amplitude, ou do estado acumulado. Isso é exatamente a classe de forma
que a decomposição do σ_res apontou como a única capaz de mover a curvatura
(`New_Theory/sigma_res_decomposicao_por_estagio.md`), e as duas linhas de
investigação convergem aqui, por caminhos independentes.

**Ordem que isto sugere:** o `delta_free` corrigido e o piso de arresto
dependente de amplitude são **um único passo**, não dois — adotar o primeiro sem
o segundo é trocar um erro por um pior. O prereg desse par precisa de âncora para
o piso, e a varredura de 9 amplitudes desta fonte é candidata a fornecê-la.

## Custo e ganho

Zero curvas fechadas, zero adoções, dois preregs reprovados (v1 por erro meu de
borda; v2 pelo modelo). Estabelecido com medição: a janela admissível é real e o
seu interior é estável; o `delta_free` adotado hoje trava o 0,25 mm; e o que
falta na fonte não é limiar, é **regime intermediário** — com os dois pisos que
ele teria de reproduzir já medidos.
