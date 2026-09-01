# PRÉ-REGISTRO — o PAR `delta_free` + `loose_arrest_floor` (um passo, não dois)

**Escrito em 2026-07-30, ANTES de medir o resultado.** Gates IMUTÁVEIS.
Store de base: `3546e6745448` · censo 104/202.

Vem de `New_Theory/yang2023_delta_free_v2_resultado.md`, que provou a cinemática
(G2/G3 passaram, ramo sub-crítico **bit-idêntico**) e reprovou a adoção isolada
(G4/F3): destravar o 0,25 mm troca *stick permanente* por *runaway a zero*, e o
dado quer o meio. A conclusão de lá é a premissa daqui: **os dois são um passo
só** — adotar o `delta_free` sem o piso troca um erro por um pior.

---

## 1. Os dois valores, e de onde cada um vem

### `delta_free` — já derivado e já provado cinematicamente

```
delta_free(m6) = 122.96e-6 m        delta_free(m8) = 129.18e-6 m
```

Média geométrica da janela admissível, receita e medição em
`2026-07-30-yang2023ijpem-delta-free-v2-prereg.md`. **Não se recalcula aqui** —
o v2 mediu G2 (slip 0 em *todos* os 2000 ciclos do ramo sub-crítico, 0,25 mm
escorregando do ciclo 1) e G3 (bit-idêntico). Esta parte está estabelecida.

### `loose_arrest_floor` — UM número, lido do platô final

Lido pelo reader do próprio repo, `kb.floor_from_curve` (procedência
`data_end_plateau`, L24), nas 9 curvas:

| δ | piso lido | ramo |
|---:|---:|---|
| 0,15 · 0,18 | 0,9325 · 0,9350 | sub-crítico (nunca escorrega ⇒ piso **inerte** nelas) |
| **0,25** | **0,5800** | **transição** |
| 0,30 · 0,35 · 0,45 · 0,50 · 0,55 · 0,65 | 0,1400 · 0,1000 · 0,1050 · 0,0700 · 0,1150 · 0,0950 | **saturado** |

O ramo saturado é um platô com dispersão, não uma tendência: mediana **0,1025**,
sd 0,0231, faixa 0,070–0,140. Portanto:

```
loose_arrest_floor = 0.1025      (UM valor per-rig)
```

procedência: *mediana do platô final medido nas 6 curvas de δ ≥ 0,30
(`kb.floor_from_curve`)*.

**Por que UM valor e não nove.** Nove pisos per-curva fecharia mais curvas e não
seria uma lei — seria a resposta escrita no gabarito. Um valor per-rig é a
hipótese **parcimoniosa e falsificável**: *o núcleo auto-travado tem uma fração de
F₀ própria da bancada, não da amplitude*. Se as 6 saturadas fecharem com um
número só, isso é evidência de lei; se cada uma pedir o seu, a hipótese morre — e
morrer é um resultado.

**Ressalva declarada:** sd 0,0231 é **5× o piso de digitalização** (±0,005,
Liu 2017), logo a dispersão do ramo saturado **não** é só leitura de figura. Pode
ser espécime, pode ser dependência residual de amplitude. Um valor único assume
que é dispersão; o G5 abaixo é o que testa isso.

---

## 2. GATES (imutáveis)

**G1 — VALORES CONGELADOS (bloqueante).** `delta_free` 122,96/129,18 µm e
`loose_arrest_floor` **0,1025**, aplicado a **todas as 9 curvas** da fonte (nas
duas sub-críticas ele é inerte por construção, já que slip ≡ 0). Nenhum ajuste
após ver métrica; nenhum valor per-curva.

**G2 — O RAMO SATURADO MELHORA (bloqueante, é o gate principal).** Mediana do
res.máx das **6** curvas de δ ≥ 0,30 tem de **cair** em relação ao baseline
(hoje: 0,2200 · 0,5600 · 0,3600 · 0,4098 · 0,3426 · 0,1600 ⇒ mediana 0,3513).
Aqui exigir melhora **é** legítimo, ao contrário do v2: estamos dando ao modelo o
patamar que ele não tinha, e se dar o patamar não melhora o ajuste, a hipótese do
piso está errada.

**G3 — SUB-CRÍTICO BIT-IDÊNTICO (bloqueante).** `0,15` e `0,18` têm de sair com
**os mesmos dígitos** de hoje (MAE 0,0093/0,0076 · res.máx 0,0241/0,0156). Não é
"continuar no tripé": é bit-idêntico, porque com slip ≡ 0 nem o `delta_free` novo
nem o piso podem tocá-las. Qualquer diferença revela acoplamento não previsto.

**G4 — NENHUMA DAS 7 PIOR QUE +0,01 (bloqueante), COM UMA EXCEÇÃO DECLARADA.**
A curva de **transição (0,25 mm)** está **fora** deste gate, e a razão está escrita
antes: o piso único de 0,1025 é 5,7× menor que o piso medido dela (0,58), logo o
modelo vai sub-prever o patamar dela **por construção**. Incluí-la seria reprovar
o prereg por uma consequência que eu já sei que ele tem. Ela entra no **G6**, como
medição.

**G5 — O PISO ÚNICO BASTA? (bloqueante — é o teste de lei).** Para cada uma das 6
saturadas, comparar o res.máx obtido com o piso único (0,1025) contra o obtido
com o **piso próprio** daquela curva. Se o piso próprio for melhor por **mais de
0,05 de res.máx em ≥3 das 6**, o piso **não** é constante da bancada e a hipótese
parcimoniosa morre — registrar e não adotar.

**G6 — A TRANSIÇÃO (informacional).** Registrar o `ratio` final previsto do
0,25 mm contra 0,520 medido e contra o piso lido 0,580. Serve para dimensionar o
que falta: se o modelo agora para em ~0,10, a lacuna é a **dependência de
amplitude do piso**, e ela fica quantificada.

**G7 — RESTO DO STORE BIT-IDÊNTICO (bloqueante).**

---

## 3. Expectativa DECLARADA

* as **6 saturadas** devem melhorar — é o que G2 exige;
* a **transição (0,25 mm)** deve continuar errada, agora por baixo (previsto
  ~0,10 contra 0,520 medido) em vez de por cima (hoje trava em ~1,0). O erro
  troca de sinal e pode até ficar de magnitude parecida;
* as **duas sub-críticas** não devem mudar em nada;
* **a fonte provavelmente NÃO entra no tripé**: σ_res dela é 0,10–0,21 contra
  0,025, e ela não tem réplicas (D1 não a socorre). Sucesso aqui é
  `G2 ∧ G3 ∧ G4 ∧ G5 ∧ G7` — o par descrever o ramo saturado com **duas
  constantes lidas do dado** —, não fechar curva.

## 4. Falsificadores

* **F1** — G3 falha (sub-crítica muda) ⇒ há acoplamento de `delta_free`/piso fora
  do canal de slip; reabrir antes de qualquer conclusão.
* **F2** — G2 falha ⇒ dar o patamar não melhora o ajuste: o defeito do ramo
  saturado não é o piso, é a **trajetória** até ele.
* **F3** — G5 falha ⇒ o piso é função da amplitude, não constante da bancada. É a
  hipótese mais interessante a morrer, e mata o par como está: a forma passa a
  precisar de `piso(δ)`, que é forma nova e não input.
* **F4** — alguma das 6 saturadas vai a `ratio` final **abaixo** do piso imposto
  ⇒ o piso não está travando o dreno; o gate `loose_arrest_floor` não é o que eu
  suponho, e a leitura do engine precisa ser refeita (armadilha já registrada:
  esta alavanca é *channel-gated* e eu já errei sobre ela hoje).

## 5. Decisão

⛔ **NÃO ASSINADO**. A execução mede os gates; a adoção é do professor.
