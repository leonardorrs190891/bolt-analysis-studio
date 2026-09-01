# PRÉ-REGISTRO — correção algébrica do `delta_free` no YANG_2023_IJPEM

**Escrito em 2026-07-30, ANTES de medir o resultado.** Gates IMUTÁVEIS a partir
daqui. Store de base: `3546e6745448` · censo 104/202.

Vem do falsificador **F2** da execução anterior
(`New_Theory/yang2023_scrit_resultado.md`, prereg
`2026-07-29-yang2023ijpem-scrit-prereg.md`), que mandou explicitamente
*"corrigir a conversão antes de qualquer conclusão sobre a forma"*.

---

## 1. O defeito, e ele NÃO é a rota de procedência

A procedência registrada do `delta_free` desta fonte é:

> `input-de-paper: limiar DECLARADO na matriz do artigo (0.18mm M8 / 0.15mm M6,
> rótulos 'below threshold')`

A rota é **boa**: o artigo declara quais amplitudes não afrouxam, e o modelo deve
reproduzir esse limiar. O erro está na **aplicação**: foi posto

```
delta_free  :=  δ_limiar                       ← o que está no config
```

quando o limiar cinemático do engine em disp-mode não é `delta_free`, e sim

```
onset  =  delta_free + F_slip/k_tr             ← quem tem de valer δ_limiar
```

O termo elástico (`F_slip/k_tr` ≈ 84 µm nos dois tamanhos) ficou **de fora**, e o
limiar do modelo saiu deslocado para cima:

| subgrupo | δ_limiar declarado | `delta_free` atual | **onset resultante** | erro |
|---|---:|---:|---:|---:|
| M6 (11,0 kN) | 150,0 µm | 150,000 µm | **234,226 µm** | +56 % |
| M8 (14,3 kN) | 180,0 µm | 180,000 µm | **264,032 µm** | +47 % |

**Consequência medida:** em 0,25 mm (M8) o engine diz *stick* enquanto o dado
colapsa de 1,00 para 0,52 — é a pior curva do subgrupo (MAE 0,166 · res.máx
0,426). É um erro de **um termo**, não de calibração.

Isto é um **erro de aplicação de input, não de física**, e por isso a correção
tem zero grau de liberdade.

## 2. A correção — determinada, sem escolha

```
delta_free  :=  δ_limiar − F_slip/k_tr
```

| subgrupo | conta | `delta_free` NOVO | onset resultante |
|---|---|---:|---:|
| M6 | 150,000 − 84,226 | **65,774 µm** | **150,0 µm** (exato) |
| M8 | 180,000 − 84,032 | **95,968 µm** | **180,0 µm** (exato) |

Os dois valores são **positivos** (F3 não dispara) e **menores** que os atuais,
logo o limite superior de folga do furo — que é a cota física do `delta_free` —
continua satisfeito trivialmente.

**Não há média, ajuste, grade ou janela.** Os dois números acima estão escritos
aqui, antes de qualquer simulação, e a execução não pode trocá-los. Se o
resultado for ruim, o resultado é ruim: não se mexe no valor.

**Os DOIS subgrupos entram**, não só o M8. A rota é a mesma; aplicar em um e não
no outro deixaria o `delta_free` do M6 com a mesma inconsistência, escondida
apenas porque a varredura do M6 (0,15 / 0,30 / 0,50) não a discrimina — com
apenas essas três amplitudes, o limiar em 150 µm e em 234 µm dão o mesmo veredito
qualitativo. Corrigir só o que o dado denuncia é deixar o defeito onde ele não é
visto.

---

## 3. GATES (imutáveis)

**G1 — VALORES CONGELADOS (bloqueante).** `delta_free` = 65,774 µm (M6) e
95,968 µm (M8), exatamente como no §2. Qualquer ajuste depois de ver métrica
invalida a execução.

**G2 — ALINHAMENTO CINEMÁTICO (bloqueante, e é verificável SEM olhar erro).**
Depois da troca:

* `onset(M6) = 150,0 µm` e `onset(M8) = 180,0 µm`, com tolerância 0,1 µm;
* `slip(0,15 mm) = 0` e `slip(0,18 mm) = 0` — exatamente, no limiar;
* `slip(0,25 mm) > 0` — a curva que o dado manda afrouxar passa a escorregar.

Este é o gate **primário** de propósito: ele mede se a correção fez o que se
propôs, e é independente de MAE. Uma correção de input tem de ser julgada pela
grandeza que ela corrige, não pelo erro que ela por acaso move.

**G3 — O RAMO SUB-CRÍTICO NÃO PODE SAIR DO TRIPÉ (bloqueante).** `0,15 mm` e
`0,18 mm` passam hoje. Depois têm de continuar passando. **Atenção ao mecanismo:**
`delta_free` também alimenta `delta_t` (o curso de gross-slip do gate de
auto-travamento), então **não** se pode assumir que essas duas curvas ficam
bit-idênticas só porque o slip continua zero nelas. É um gate real, não formal.

**G4 — NENHUMA CURVA DA FONTE PIOR QUE +0,01 (bloqueante).** Nas 7 curvas acima
do limiar, nenhuma das três pernas pode piorar mais de 0,01. A mediana do
res.máx da fonte é **reportada, não exigida**: esta é correção de procedência, e
exigir melhora seria assumir que o desalinhamento era o defeito dominante — o que
é exatamente o que a execução vai descobrir.

**G5 — RESTO DO STORE BIT-IDÊNTICO (bloqueante).** A mudança é per-subgrupo.
Qualquer diferença fora do YANG_2023_IJPEM indica que a chave de config pegou
fonte alheia — a armadilha de empate de tokens já registrada nos gotchas.

---

## 4. Falsificadores declarados

* **F1** — `0,15` ou `0,18` sai do tripé ⇒ a rota "onset = limiar declarado" está
  errada, ou há um terceiro termo no limiar que também ficou de fora. Reverter e
  reabrir a leitura do limiar.
* **F2** — o onset medido não bate com o limiar declarado (tol. 0,1 µm) ⇒ erro de
  aritmética ou o `F_slip/k_tr` muda entre a leitura e a simulação (dependência de
  estado que eu tratei como constante).
* **F3** — `delta_free` negativo em algum subgrupo ⇒ o termo elástico já excede o
  limiar declarado, e aí o problema é em `µ` ou `k_tr`, não no take-up. (Medido:
  não ocorre — 65,8 e 96,0 µm.)
* **F4** — a mediana do res.máx da fonte **piora** ⇒ o desalinhamento não era o
  defeito dominante. Registrar e parar: a correção continua certa como
  procedência, mas a fonte precisa de outra coisa, e a forma volta para a fila.

---

## 5. O que este prereg NÃO promete

Que alguma curva entre no tripé. As 7 acima do limiar têm σ_res 0,10–0,21 contra
0,025, e a fonte **não tem réplicas** ⇒ sem piso medido ⇒ a D1 não a socorre.
O objetivo é **alinhar o limiar cinemático com o limiar declarado pelo artigo** —
uma correção de procedência que vale por si, e que precisa estar feita **antes**
de qualquer forma nova ser calibrada em cima, sob pena de o coeficiente da forma
absorver o erro de take-up e escondê-lo.

## 6. Decisão

⛔ **NÃO ASSINADO** no momento da escrita. A execução mede os gates; a adoção no
canônico é do professor.
