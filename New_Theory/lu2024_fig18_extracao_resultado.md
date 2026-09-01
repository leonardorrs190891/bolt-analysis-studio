# Fig. 18a do LU_2024 extraída — as CSVs de **1,0 e 2,0 mm** têm erro real, medido contra instrumento validado a ±0,002

**2026-08-07 (madrugada)** · sonda `lu2024_fig18_extrai.py` (só-leitura, não
grava CSV nenhuma) · store `1c118e405a42` · **nada adotado**.

## Instrumento: calibração do D-W reusada de propósito

Página 16 (0-based), zoom 8, `px_por_ciclo` 14,495, `N_por_px` 11,5875 — os
mesmos números do `lu2024_fig18a_amp1p5_pixel.json`. Reusar em vez de
re-derivar é deliberado: a linha de **1,5 mm já tem round-trip validado** contra
a Tabela 8, então ela é o **CONTROLE** desta execução.

| amplitude | cor na figura |
|---|---|
| 0,25 mm | **preto** |
| 0,5 mm | vermelho (255, 61, 61) |
| 1,0 mm | azul (0, 102, 225) |
| 1,5 mm | verde (0, 172, 98) — controle |
| 2,0 mm | violeta (208, 120, 225) |

Tabela 8 (p. 17, "Specific attenuation of the bolt"), retenção = 1 − atenuação:
0,25 → 0,829/0,795/0,782/0,780 · 0,5 → 0,638/0,465/0,344/0,126 · 1,0 →
0,632/0,429/0,121/0,064 · 1,5 → 0,504/0,302/0,079/0,004 · 2,0 →
0,498/0,173/0,007/— (célula vazia: a curva termina em ~50 ciclos).

## ⚠️ O controle reprovou a 1ª passada — e o defeito NÃO era o que eu disse

A 1ª versão desta sonda deu **+0,4581** no c1 do controle. Escrevi que era o
"artefato do penhasco" (média por coluna caindo no meio da queda vertical).
**Estava errado.** Era **off-by-one no eixo x**, e o próprio JSON do D-W já o
registrava: *"ciclo do paper = x_plotado − 1 (âncora em x=1; ciclo c plotado em
x=c+1)"* — eu li isso como convenção da CSV quando é da **figura**.

A prova está no traço do verde: fica em **11 700 N** (ratio ~1,00) até x=1,35,
salta, e assenta em **5 920 N = 0,504** a partir de x≈1,7 — e 0,504 é
exatamente o **1º ciclo** da Tabela 8. Assinatura do off-by-one, visível nos
resíduos da 1ª passada: erro **grande** onde a curva é íngreme (c1 +0,458,
c10 +0,010) e **pequeno** onde é plana (c50 +0,0008). O penhasco não precisava
de tratamento nenhum.

**Controle depois do conserto:** −0,0046 / −0,0022 / −0,0023 / +0,0001 nas
quatro âncoras — reproduz os resíduos do D-W. Instrumento validado a **±0,005**,
e a ±0,002 fora do c1.

## Resultado

| curva | CSV − Tab8 @c10 | **figura − Tab8 @c10** | figura @c50 | figura @c100 |
|---|---:|---:|---:|---:|
| 0,5 mm | +0,0100 | **+0,0012** | +0,0002 | −0,0006 |
| 1,0 mm | +0,0439 | **+0,0013** | +0,0010 | +0,0005 |
| 1,5 mm (controle) | −0,0003 | −0,0022 | −0,0023 | +0,0001 |
| 2,0 mm | +0,0792 | **+0,0000** | −0,0007 | — |

**A figura reproduz a Tabela 8 a ±0,002 nas quatro curvas.** Logo o desvio das
CSVs é inteiramente delas:

* **2,0 mm — erro de +0,0792 no c10**, ~40× o ruído do instrumento. Era a
  evidência "forte" do `lu2024_fig18_familia_tab8.md`, e **confirma-se com
  folga**.
* **1,0 mm — erro de +0,0439**, ~20× o ruído. Confirma-se.
* **0,5 mm — erro de +0,0100**, ~5× o ruído. Pequeno mas **real** — o doc
  o listava como "pode melhorar" e a medição concorda.

⚠️ Correção de um número que EU publiquei há uma hora: a 1ª versão deste
documento dizia que os erros das CSVs eram ~+0,03 (1,0 mm) e ~+0,06 (2,0 mm), e
que a de 0,5 mm estava "dentro do ruído". Aquelas estimativas saíam do
instrumento com off-by-one; com o instrumento certo os erros são **maiores**
(+0,044 e +0,079) e o da 0,5 mm é **real**, não ruído.

## Resíduo honesto no c1, que o controle NÃO cobre

Nas três curvas não-controle o c1 desvia **+0,027 a +0,047**, enquanto o
controle desvia −0,0046. Não tenho explicação para a assimetria: um erro de x
sub-pixel produziria desvios proporcionais à inclinação local, e as magnitudes
não seguem esse padrão. ⇒ **o c1 carrega incerteza de até ±0,05 que o controle
não denuncia**; c10–c100 são sólidos a ±0,002. Qualquer CSV nova deve declarar
isso, e o 1º ponto deve vir da Tabela 8, não do pixel.

## A curva de 0,25 mm NÃO foi lida — declarado, com o que se sabe dela

A série é preta, e preto também é a moldura (linhas 0–2 e 1122, colunas 0–2 e
1477 — medidas), os traços de escala e o texto da legenda. Duas tentativas:

1. corte por **densidade de coluna** (>18 px) — comeu o penhasco inicial; o
   traço passou a começar no ciclo 2,1 e a âncora saiu 9851 N. Densidade não
   separa texto de penhasco: **os dois são colunas densas**.
2. exclusão da legenda por **retângulo** (y<300, x>1100, medido; não encosta na
   curva, que vive em y≈328) — âncora saiu **6528 N**, pior. A causa provável é
   que, no penhasco, o cruzamento das cinco curvas coloridas produz pixels
   **escuros e de baixa saturação** que caem na máscara preta.

**O que se sabe apesar disso:** a *forma* está certa. A razão
`medido(c50)/medido(c10)` dá **0,984**, e a Tabela 8 dá 0,782/0,795 = **0,984**
— igual à 3ª casa. Só a **âncora** é ilegível. Invertendo pela Tabela 8,
`anchor = 9415/0,795 ≈ 11 843 N`, dentro da faixa das outras quatro
(11 554–12 099). ⚠️ Essa derivação **usa** a Tabela 8, então **não pode**
depois ser gateada contra ela — fica como coerência, não como medição.

## O que isto habilita, e o que ainda falta

Alvo agora é **nomeado por curva**, não "a família": **1,0 mm** e **2,0 mm** têm
erro medido a 20–40× o ruído; **0,5 mm** tem erro pequeno mas real; **1,5 mm**
já está consertada (D-W); **0,25 mm** não é decidível com este instrumento.

Falta antes do prereg:
1. **1º ponto vem da Tabela 8**, não do pixel (o c1 tem ±0,05 não coberto).
2. **Medir o efeito no piso**: a `amp1p0` é metade do par `amp1p0 ↔
   fig20_T22Nm`, então corrigi-la move `limite_sres(LU_2024)` — a mesma
   armadilha que a `run2p2` ensinou no D-Y, e ali custou um par declarado.
3. **Saldo declarado ANTES**: a `amp2p0` está **no tripé hoje** e é a de maior
   erro de CSV; corrigi-la pode tirá-la, como o D-U tirou a `yang2021_r1`.

## Reprodutibilidade

```bash
py -3.12 New_Theory/lu2024_fig18_extrai.py --json New_Theory/lu2024_fig18_extrai.json
```
