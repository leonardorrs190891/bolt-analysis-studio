# Prereg — kernel de creep no CACCESE: a FORMA, com o ponto final preservado

**2026-08-04** · decisão D-H (por delegação, mandato 2026-07-30) · gates
escritos **antes** de medir. Fingerprint de partida: `63722b266dc0`.

## Por que isto não é reciclar uma falsificação

`creep_mode="saturating"` foi **reprovado no G2 em 2026-07-30** (8 de 18
curvas pioram > +0,01, uma de 0,0396 → 0,2232). Aquela medição foi feita
sobre as 18 form-limited de então — **curvas transversais onde o creep NÃO
domina**, e as pioras foram em curvas curtas.

O CACCESE_2009 é a população oposta, medida hoje: **as 7 curvas são
99,5–99,9 % creep** (o canal carrega 0,385 de 0,385 kN), num ensaio de
relaxação estática de 2000 **horas**. A forma nunca foi testada onde ela é
a única coisa que age.

## O defeito é SISTEMÁTICO na fonte, não de uma curva

Resíduo médio do 1º e do 5º quinto (modelo − dado):

| curva | creep | 1º quinto | 5º quinto | σ_res | tripé |
|---|---:|---:|---:|---:|:--:|
| compblock_34kPa | 99,5 % | **+0,0109** | −0,0028 | 0,0100 | ✅ |
| compblock_71kPa | 99,8 % | **+0,0117** | −0,0037 | 0,0094 | ✅ |
| protruding_45kN | 99,9 % | **+0,0245** | −0,0206 | 0,0201 | ✅ |
| retighten_12p7mm | 99,9 % | **+0,0163** | −0,0234 | 0,0172 | ✅ |
| **retighten_19p1mm** | 99,9 % | **+0,0284** | −0,0352 | **0,0263** | ❌ |
| tapered_45kN_rep1 | 99,9 % | −0,0158 | −0,0632 | 0,0218 | ❌ (MAE) |
| **tapered_45kN_rep2** | 99,9 % | **+0,0329** | −0,0081 | **0,0354** | ❌ |

**Seis das sete** têm o mesmo sinal: o modelo relaxa **devagar demais no
início** e **rápido demais no fim**. As 4 aprovadas têm o mesmo defeito, só
menor. Isso é curvatura do kernel `δ = C·log(t/t₀+1)`, não erro de curva.

## A comparação tem de ser de FORMA, e isso exige renormalizar

Os dois ramos têm amplitude com significados diferentes:

* log: `δ(t) = C·F₀·log(t/t₀+1)` ⇒ em t=2000 h com t₀=7200 s, o fator é
  `log(1001) ≈ 6,909`
* saturante: `δ(t) = C·F₀·(1 − e^{−(t/t_c)^α})` ⇒ máximo **1,0**·C·F₀

Usar o mesmo `C_creep` nos dois faria o saturante perder **~6,9× menos** —
compararia amplitude, não forma. Então o executor aplica a renormalização
**determinística e preservadora do ponto final**:

```
C_sat = C_log · log(t_end/t₀ + 1) / (1 − e^{−(t_end/t_c)^α})
```

**Zero números fitados por curva.** O `C_creep` per-par (procedência
existente) entra como está e sai transformado por aritmética fechada; a
perda total no fim da janela é preservada por construção. Logo **só a forma
é testada** — e como σ_res é invariante por translação, ele é a métrica
certa para isso.

⚠️ Isto **não** é a escala que o docstring do engine proíbe (`δ_max ·
creep_t_c/t₀`, que casa a derivada em t=0 e amplifica δ_max por até
`t_c/t₀`). Preservar o **ponto final** é o oposto: nunca amplifica o total.

## Espaço de forma, e a região que a física indica

Para `t_c ≫ t_end`, `1 − e^{−(t/t_c)^α} ≈ (t/t_c)^α` ⇒ o kernel vira **lei
de potência** com expoente α (família Norton-Bailey). Com **α < 1** a curva
é côncava: rápida no início, lenta no fim — **exatamente a direção do
defeito**. Varredura declarada: `α ∈ {0,15 · 0,2 · 0,3 · 0,4 · 0,6 · 1,0}`
× `t_c/t_end ∈ {1 · 10 · 100}`. **2 números, compartilhados pelas 7 curvas**
(uma física, N estados — princípio do Estágio A).

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (instrumento):** baseline re-simulado bate com o store a 1e-9; e a
  renormalização é conferida medindo a perda no ponto final — se ela mudar
  mais de **2 %** em relação ao log, a aritmética está errada e o ramo é
  INCONCLUSIVO (não "a forma falhou").
- **G1 (o gate que decide — predição de forma):** o σ_res tem de **cair nas
  7 curvas**. O defeito foi medido como sistemático; se a correção de forma
  ajudar umas e piorar outras, a leitura "curvatura do kernel" está
  **falsificada** e o que houver é ajuste por curva.
- **G2 (nenhum caso pior):** nenhuma das 7 piora > **+0,010** em qualquer
  perna, e as **4 que estão no tripé permanecem**. Elas são o controle: um
  kernel melhor não pode custar as aprovadas.
- **G3 (ganho):** ao menos **1** das 3 fora entra no tripé. A `rep1` está
  **fora do alcance por construção** e isso está dito antes de medir: o
  problema dela é NÍVEL (viés −0,0508, resíduo negativo em toda a curva) e
  a renormalização preserva o total — declarar isso, não usá-lo como
  surpresa.
- **G4 (isolamento):** todas as outras fontes **bit-idênticas**.
- **G5 (procedência):** os 2 números são de **forma**, fitados no conjunto
  da fonte, e o `prov` tem de dizer exatamente isso — não fingir âncora de
  handbook. O `C_creep` per-par **não é refitado**; se a adoção exigir
  refitá-lo, o escopo mudou e vira outro prereg.
- **G6 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos 210
  + censo/docs/páginas/testes no MESMO commit.

### Ramos

- **ADOTA** — G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4.
- **FALSIFICADO** — G1 falha: o σ não cai nas 7 ⇒ a curvatura não é do
  kernel, e a reprovação de 2026-07-30 passa a valer também na população
  creep-dominada (resultado forte, vale registrar).
- **NÃO ADOTA (forma certa, ganho nulo)** — G1 e G2 passam mas nenhuma
  curva fecha: registrar a melhora de σ e não adotar por ganho nulo, **ou**
  adotar por procedência de forma se a melhora for sistemática e grande —
  decisão declarada com os números na mão, não antecipada aqui.
- **INCONCLUSIVO** — renormalização fora de 2 % (G0), ou `creep_mode` inerte
  (conferir `creep_t_c > 0`, o companheiro obrigatório do switch).

## Previsão registrada

Espero que **α ≈ 0,2–0,3 com t_c ≥ 10·t_end** reduza o σ nas 7, feche a
`retighten_19p1mm` (precisa −5 %) e provavelmente a `rep2` (precisa −29 %,
mais duvidoso). Espero que a **`rep1` não feche** (é nível). Se o σ cair nas
4 aprovadas junto, é evidência de que o defeito era mesmo do kernel — e essa
é a parte que eu não posso fabricar depois.
