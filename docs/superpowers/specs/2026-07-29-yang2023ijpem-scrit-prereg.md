# PRÉ-REGISTRO — `s_crit_loose` ancorado no YANG_2023_IJPEM

**Escrito em 2026-07-29, ANTES de medir o resultado.** Gates IMUTÁVEIS a partir
daqui (regra do repo). Store de base: `3546e6745448` · censo 104/202.

Primeiro passo da **otimização principal** (formas de taxa dependente do estado).
Alvo escolhido pela matriz de âncoras (`New_Theory/anchor_coverage_matrix.md`,
D2b): esta é a fonte com a melhor varredura de amplitude do acervo **e** uma das
três piores em curvas fora.

---

## 1. Premeasure (feito antes, e é input — não resultado)

Os dois desacordos de input que a nota de aparato registrava **já estão
resolvidos no store**: `freq = 10 Hz` (não 12,5 nem 5) e `F0(M6) = 11 kN` (não
8 500 N). Conferido caso a caso. ⚠️ A seção **FALTA** da nota
(`apparatus_notes/yang2023ijpem.md`) ainda os lista como pendentes — **está
vencida**, e corrigi-la é parte da execução deste prereg.

| amplitude imposta | F₀ | retenção final | tripé | σ_res |
|---:|---:|---:|:--:|---:|
| **0,15 mm** ("below_threshold") | 11,0 kN | 0,925 | **passa** | 0,0103 |
| **0,18 mm** ("below_threshold") | 14,3 kN | 0,930 | **passa** | 0,0087 |
| 0,25 mm | 14,3 kN | 0,520 | fora | 0,1452 |
| 0,30 mm | 11,0 kN | 0,220 | fora | 0,1312 |
| 0,35 mm | 14,3 kN | 0,150 | fora | 0,2118 |
| 0,45 mm | 14,3 kN | 0,160 | fora | 0,1344 |
| 0,50 mm | 11,0 kN | 0,120 | fora | 0,1404 |
| 0,55 mm | 14,3 kN | 0,180 | fora | 0,1287 |
| 0,65 mm | 14,3 kN | 0,160 | fora | 0,1017 |

**A âncora existe e é uma BRACKET, não um fit:** a transição está **entre 0,18 e
0,25 mm** de amplitude imposta. As duas curvas abaixo dela perdem ~7 % em todo o
ensaio; as sete acima perdem 48–88 %. O próprio artigo nomeia as duas primeiras
como *below threshold* — o limiar é **declarado pela fonte**, não inferido por nós.

**Correção da matriz de âncoras:** classifiquei esta fonte como `FORTE-` ("sem
curva sub-crítica na varredura") porque usei retenção final ≥ 0,95 como corte, e
0,925/0,930 ficaram de fora. O corte estava errado: essas duas **são** o ramo que
não afrouxa (7 % contra 48–88 %). A fonte é **FORTE** — a bracket está *dentro*
da varredura, não extrapolada. Corrigir o critério em `build_anchor_coverage.py`
faz parte da execução.

---

## 2. O que vai ser feito (e o que NÃO vai)

Ligar, **só nesta fonte**, o modo de taxa graduada já existente no engine:

```
loose_rate_mode = "graded_scrit"
s_crit_loose    = <lido da bracket, ver §3>       # ANCORADO
k_loose_graded  = <1 coeficiente por rig>          # FITADO — declarado
```

**Honestidade sobre os graus de liberdade:** a forma tem **dois** parâmetros e a
varredura ancora **apenas um**. O `k_loose_graded` é coeficiente de taxa e não
sai da bracket — ele será **fitado**, 1 valor para as 9 curvas. Isso é 1 DOF para
9 curvas em 7 amplitudes distintas, o que é defensável, **mas não é procedência**.
É por isso que o teste que decide não é o MAE desta fonte: é a **generalização**
(G2) e a **transferência** (G5).

**Fora de escopo, explicitamente:** adoção no canônico; mexer em `META_SRES` ou
na perna por fonte (D1); tocar em qualquer outra fonte; a segunda forma
(embedding/creep/wear) da D2b; re-simular o store inteiro antes dos gates.

---

## 3. Como `s_crit_loose` é LIDO (não ajustado)

`s_crit_loose` é amplitude de **slip**, não de deslocamento imposto. A conversão
é a cinemática do próprio engine em disp-mode:

```
slip = max(0, δ − F_slip/k_tr)        com  F_slip = µ·F₀
```

Procedimento, fixado aqui:

1. rodar o engine no **primeiro ciclo** de cada uma das 9 curvas, com os inputs
   adotados, e registrar o `slip` resolvido de cada amplitude imposta;
2. `s_crit_loose` := **média geométrica** do slip de 0,18 mm (último que não
   afrouxa) e de 0,25 mm (primeiro que afrouxa). Média **geométrica** e não
   aritmética porque a bracket é multiplicativa (0,18→0,25 é ×1,39) e a
   geométrica é o centro invariante à escala;
3. o valor e a bracket `[slip(0,18), slip(0,25)]` vão **escritos** no
   `adopted_configs.json` com procedência `bracket_amplitude_yang2023ijpem`, e a
   largura da bracket é a **incerteza declarada** do limiar.

Nenhum passo acima olha o MAE. Se olhasse, seria fit com nome de âncora.

---

## 4. GATES (imutáveis)

**G1 — A ÂNCORA NÃO OLHOU O ERRO (bloqueante).** `s_crit_loose` tem de ser o
valor do procedimento §3, calculado **antes** de qualquer métrica. Se for
ajustado depois de ver MAE/σ_res, ainda que "só um pouco", a execução está
reprovada e o resultado é descartado.

**G2 — GENERALIZAÇÃO POR AMPLITUDE HELD-OUT (bloqueante, é o gate principal).**
`k_loose_graded` é fitado **só em 3 amplitudes** — `0,25 · 0,35 · 0,50` — e as
outras **4 acima do limiar** (`0,30 · 0,45 · 0,55 · 0,65`) são **held-out**: não
entram no fit, nem para escolher, nem para desempatar. Critério: a **mediana do
res.máx das 4 held-out tem de cair** em relação ao baseline. Se só as 3 fitadas
melhorarem, é ajuste por curva, não lei — reprovado.

**G3 — O RAMO SUB-CRÍTICO NÃO PODE QUEBRAR (bloqueante).** `0,15 mm` e `0,18 mm`
passam hoje no tripé. Depois da mudança **têm de continuar passando**. Uma forma
com limiar que estraga justamente as curvas abaixo do limiar está falsificada —
e este é o gate mais fácil de violar, porque `s_crit` mal lido derruba as duas.

**G4 — NADA PIOR NO RESTO DO STORE (bloqueante).** Fora do YANG_2023_IJPEM,
nenhuma curva pode piorar mais de **+0,01** em nenhuma das três pernas. Como a
mudança é per-source, o esperado é **zero** diferença; qualquer vazamento indica
que a chave de config pegou fonte alheia (a armadilha de empate de tokens já
registrada nos gotchas).

**G5 — TRANSFERÊNCIA ZERO-REFIT (informacional, NÃO bloqueante).** Aplicar a
**mesma** `k_loose_graded` ao `ROUSSEAU_2025` (3 amplitudes, canal de
afrouxamento, âncora FORTE-) lendo o `s_crit` dele pela mesma receita §3, **sem
refit**. Medir e publicar. Não bloqueia porque uma constante de taxa por par pode
legitimamente não transferir (é o veredicto §8: formas transferem, constantes
não) — mas é o número que diz se ganhamos uma **lei** ou um **ajuste de rig**.

---

## 5. Falsificadores declarados

* **F1** — `k_loose_graded` ótimo das 3 fitadas difere por **mais de 2×** do que
  as 4 held-out pediriam ⇒ a forma está absorvendo variação por curva; abandonar.
* **F2** — `s_crit_loose` lido cai **fora** da bracket `[slip(0,18), slip(0,25)]`
  ⇒ a conversão δ→slip está inconsistente com a cinemática do engine; corrigir a
  conversão antes de qualquer conclusão sobre a forma.
* **F3** — G3 viola ⇒ o limiar não separa os ramos; a forma não descreve esta
  fonte.
* **F4** — o canal de afrouxamento **não cresce** ao ligar o modo (delta ≈ 0 nas
  9 curvas) ⇒ a alavanca está inerte aqui por gate de modo, e o premeasure de
  canal foi mal lido (a lição do Beco 2 da D1b: fração *a posteriori* não decide
  inércia de lei de taxa — verificar com sonda direta no engine, 2 pontos).

---

## 6. O que este prereg NÃO promete

Que a fonte entre no tripé. **σ_res dela é 0,10–0,21 contra limite 0,025** (4–8×),
e ela **não tem réplicas** ⇒ não tem piso medido ⇒ a D1 não a ajuda. Fechar as 7
curvas exigiria uma redução de ~5× no σ_res, que nenhuma medição até aqui sugere
ser alcançável com uma forma só. O resultado esperado e aceitável é **a forma
descrever o ramo afrouxante e generalizar por amplitude** (G2), com o tripé
reportado como consequência, não como meta.

Prometer o tripé aqui seria montar o prereg para falhar — ou, pior, para ser
salvo depois com um refit que os gates existem para proibir.

---

## 7. Decisão

⛔ **NÃO ASSINADO** no momento da escrita. A execução mede os gates; a adoção no
canônico é do professor.
