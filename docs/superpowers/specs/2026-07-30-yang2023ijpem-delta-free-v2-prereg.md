# PRÉ-REGISTRO v2 — `delta_free` no interior da janela admissível

**Escrito em 2026-07-30, ANTES de medir o resultado.** Gates IMUTÁVEIS.
Store de base: `3546e6745448` · censo 104/202.

Substitui o prereg v1 (`2026-07-30-yang2023ijpem-delta-free-prereg.md`), que
**reprovou em G3/G4** por um erro meu: congelei a **borda** de um intervalo
aberto (95,968 µm), e a borda é instável porque o termo elástico decai.
Diagnóstico completo: `New_Theory/yang2023_delta_free_resultado.md`.

---

## ⚠️ Correção do número que eu mesmo pedi para congelar

O professor pediu **129,86 µm**, que é o valor que **eu** havia calculado. Ele
está **errado por ~0,7 µm**, e a causa é minha: derivei o piso da janela de uma
sonda que rodou **20 000 ciclos**, quando o `n_max` real dessas curvas é **2 000**.
Rodar 10× além decaiu o elástico mais do que o ensaio decai (78,4 µm em vez de
79,46 µm) e baixou o piso da janela.

Recalculado sobre a corrida **completa e correta**:

| subgrupo | curva sub-crítica | elástico (início → fim, n=2000) | janela admissível | **média geométrica** |
|---|---|---|---|---|
| **m8** | 0,18 mm | 84,032 → **79,457** µm | (100,54 ; 165,97) µm | **129,18 µm** |
| **m6** | 0,15 mm | 84,226 → **79,936** µm | (70,06 ; 215,77) µm | **122,96 µm** |

Uso **129,18 µm**, não 129,86. A diferença é imaterial para o veredito (os dois
caem dentro da janela), mas o valor adotado tem de ser o que a **receita
declarada** produz sobre a corrida certa — senão a procedência aponta para uma
medição que não existe. Se o professor preferir 129,86 mesmo assim, é uma linha
para trocar, mas aí o `prov` tem de dizer "20 000 ciclos", não "n_max".

---

## 1. A regra (a mesma do v1, com a aritmética corrigida)

Sub-criticidade não é uma condição no instante inicial, é uma condição **para todo
t** — e o elástico `µ·F₀/k_tr` **decai** junto com F₀:

```
sub-crítica:  delta_free + F_slip(t)/k_tr  >  δ_sub     para TODO t
              ⇒ manda o elástico MÍNIMO (o final)  ⇒ delta_free > δ_sub − el_fim

próxima escorrega: delta_free + F_slip(0)/k_tr < δ_prox
              ⇒ manda o elástico INICIAL          ⇒ delta_free < δ_prox − el_ini
```

Valor := **média geométrica da janela**. Geométrica, e não aritmética, pela mesma
razão do prereg do `s_crit`: a janela é multiplicativa e a média geométrica é o
centro invariante à escala. Nenhuma métrica de erro entra na conta.

## 2. GATES (imutáveis)

**G1 — VALORES CONGELADOS (bloqueante).**

```
delta_free(m6) = 122.96e-6 m
delta_free(m8) = 129.18e-6 m
```

Qualquer alteração após ver métrica invalida a execução. **Se reprovar, reprova** —
não há terceira tentativa com o valor ajustado.

**G2 — CINEMÁTICA, verificável sem olhar erro (bloqueante).**
* `slip(0,15 mm) = 0` e `slip(0,18 mm) = 0` **em todos os ciclos** da corrida —
  não só no primeiro. É a correção direta do que o v1 errou: o v1 checou o ciclo 1
  e a curva destravou depois.
* `slip(0,25 mm) > 0` em algum ciclo, e `slip(0,30 mm) > 0`.

**G3 — RAMO SUB-CRÍTICO NO TRIPÉ (bloqueante).** `0,15` e `0,18` passam hoje e
têm de continuar passando. Foi o gate que matou o v1.

**G4 — NENHUMA DAS 7 PIOR QUE +0,01 (bloqueante).** Mediana do res.máx da fonte
**reportada, não exigida** (correção de procedência, não otimização).

**G5 — RESTO DO STORE BIT-IDÊNTICO (bloqueante).**

**G6 — LEITURA DO REGIME (informacional, NÃO bloqueante).** Registrar o
`ratio` final previsto de 0,25 mm e 0,30 mm contra o medido (0,520 e 0,220).
Serve de premeasure do passo seguinte, e existe porque a expectativa declarada
abaixo precisa ser confrontada com número, não lembrada de memória.

## 3. Expectativa DECLARADA (para o prereg não ser inflado depois)

O modelo é **bimodal** aqui — stick permanente **ou** runaway a zero (medido:
0,30 mm vai a F₀=0 em ~1000 ciclos). Destravar o 0,25 mm provavelmente o joga no
**runaway**: acerta o início da curva e erra o fim, previsto ~0 contra 0,520
medido. **Se for isso, o `delta_free` correto é condição necessária e NÃO
suficiente**, e G4 pode passar com a fonte ainda inteira fora do tripé.

Escrevo isto **antes** para que um resultado assim não seja apresentado depois
como sucesso parcial nem como surpresa. O sucesso deste prereg é
`G2 ∧ G3 ∧ G4 ∧ G5` — alinhar o limiar sem quebrar nada —, não fechar curva.

## 4. Falsificadores

* **F1** — `0,15` ou `0,18` escorrega em algum ciclo ⇒ o piso da janela está
  subestimado; provável causa: o elástico decai mais do que a corrida atual
  mostra porque o próprio destravamento acelera a queda de F₀ (realimentação que
  a conta estática não captura). Reverter e recalcular com a corrida nova.
* **F2** — `0,25` continua com slip 0 em todos os ciclos ⇒ o teto da janela está
  sobrestimado, ou há um terceiro termo no limiar.
* **F3** — G4 reprova em ≥3 das 7 ⇒ o desalinhamento não era o defeito dominante
  e a correção, ainda que certa como procedência, não é adotável sozinha.

## 5. Decisão

⛔ **NÃO ASSINADO**. A execução mede os gates; a adoção é do professor.
