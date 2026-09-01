# Prereg — `fret_freq_exp` no LI_2022_TRIBOINT: a capacidade existe e nunca foi adotada

**2026-08-04** · decisão D-G (por delegação, mandato 2026-07-30) · gates
escritos **antes** de medir. Fingerprint de partida: `63722b266dc0`.

## O defeito, medido

Varredura de frequência do LI_2022_TRIBOINT (`axialmin`, mesmo rig, mesmo
parafuso, 200 000 ciclos, só a frequência muda):

| f | perda no dado | perda no modelo | viés médio | tripé |
|---:|---:|---:|---:|:--:|
| 10 Hz | **17,92 %** | 15,39 % | +0,0526 | ❌ (MAE 1,05×) |
| 15 Hz | 14,17 % | 15,37 % | +0,0271 | ✅ |
| 20 Hz | **8,92 %** | 15,35 % | −0,0158 | ✅ |

**O modelo é cego à frequência.** Expoente de frequência medido:

* no dado: `ln(17,92/8,92) / ln(20/10)` = **1,0065**
* no modelo: **0,0038** ⇒ o modelo entrega **0 %** da dependência

## A capacidade já existe, com o expoente já derivado DESTE dado

`JointMaterial.fret_freq_exp` (default **0,0 = OFF, bit-idêntico**) +
`f_ref_fret` (default 15,0 Hz). O fator é `(f_ref/f)^exp` sobre o incremento
de fretting/flanco. O **docstring do próprio engine** (linhas 133–142) já
registra a derivação a partir desta mesma varredura: *"10Hz −17,9 % / 15Hz
−14,1 % / 20Hz −8,9 % (…) O expoente é LIDO do próprio sweep de frequência
(ln(perda_10/perda_20)/ln(20/10) ~ 1,0)"*, e cita a observação dos autores
(*"wear debris + spalling grows as frequency decreases"*).

O cfg adotado do `LI_2022_TRIBOINT` **não seta `fret_freq_exp`** ⇒ a
capacidade foi construída, documentada, e nunca promovida. Padrão conhecido
do roadmap (item 4): *capacidade default-inerte esperando adoção gateada*.

## Direção — confere nos dois extremos, neutra no meio

| f | precisa | fator `(15/f)^1,0065` | confere? |
|---:|---|---:|:--:|
| 10 Hz | **mais** perda | **1,504** | ✅ |
| 15 Hz | menos perda | 1,000 (neutro) | — não ajuda, não atrapalha |
| 20 Hz | **menos** perda | **0,749** | ✅ |

## Escopo e procedência do número

* **1 número adotado**: `fret_freq_exp`. Valor **LIDO** da razão entre as
  perdas de 10 e 20 Hz (**1,0065**, ou 1,0 arredondado), **não** otimizado.
* `f_ref_fret = 15,0` — o **meio** do sweep e o default do campo. Não é
  escolha livre: é o ponto onde o fator vale 1 e a curva do meio fica
  intacta, o que é o que a torna held-out.
* ⇒ **o 15 Hz é predição ZERO-REFIT**: o expoente usa só 10 e 20 Hz.

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (instrumento):** sonda de 2 pontos (`exp` 0 → 1,0065). Se Δ = 0,0000
  exato, **não** concluir "inerte": conferir os companheiros do canal
  (`flank_wear_on` está em 1,0 no cfg; fonte é AXIAL, e o canal de flanco é
  axial-force-mode por default) e se o fator é lido no sítio que carrega a
  perda desta fonte. Ramo INCONCLUSIVO se o canal não for chamado.
- **G1 (ganho):** `axialmin_10Hz` **entra no tripé**.
- **G2 (HELD-OUT zero-refit — o gate que decide):** `axialmin_15Hz`
  **permanece** no tripé. Ele não participou da leitura do expoente e o
  fator nele é exatamente 1,000, então qualquer mudança nele denuncia
  acoplamento não previsto. `axialmin_20Hz` também permanece.
- **G3 (nenhum caso pior):** nenhuma das 4 curvas da fonte piora > **+0,010**
  em qualquer perna — **inclui** `axial_10Hz_full` (hoje fora por σ 1,46×,
  e o fator nela é 1,504, então ela vai mudar).
- **G4 (isolamento):** todas as outras fontes **bit-idênticas**. A chave é
  da fonte; se algo mais mudar, vazou.
- **G5 (procedência acima de MAE):** o valor adotado tem de ser o **LIDO**
  (1,0065 / 1,0). Se uma varredura mostrar que outro expoente dá MAE menor,
  **reportar os dois e adotar o lido** — e dizer no `prov` que foi lido, não
  fitado. Fit que vence procedência aqui destruiria justamente o que faz
  este número valer.
- **G6 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos 210
  + censo/docs/páginas/testes no MESMO commit.

### Ramos do veredicto

- **ADOTA** — G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5.
- **ADOTA PARCIAL DECLARADO** — G2/G3/G4 passam mas o 10 Hz não fecha: a
  forma está certa (dependência de frequência real, lida do dado) e o
  resíduo é de magnitude. Adotar **só** se G3 e G4 estiverem limpos, e
  declarar que não fechou.
- **FALSIFICADO** — a direção não confere na medição, ou o held-out de
  15 Hz sai do tripé (⇒ o fator está acoplado a algo não previsto).
- **INCONCLUSIVO** — canal não chamado / Δ = 0 exato com companheiro
  desligado. Ramo obrigatório: sem ele o script escreve veredicto sobre
  teste vazio.

## Previsão registrada

Espero que o **10 Hz feche** (precisa de −0,0026 no MAE e o fator lhe dá
+50 % de fretting) e que o **20 Hz melhore** (fator 0,749 na direção certa).
Espero o **15 Hz praticamente inalterado** (fator 1,000). **Não sei** o que
acontece com `axial_10Hz_full`: o fator nela é 1,504 e ela já está fora por
forma (σ 1,46×) — pode melhorar por nível e piorar por forma. Se ela estourar
o G3, o ramo é não-adotar, e isso está escrito antes de medir.
