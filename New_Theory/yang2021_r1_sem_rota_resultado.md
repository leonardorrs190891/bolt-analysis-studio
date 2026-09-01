# `yang2021_amp0p6mm_ax8kN_r1` — a mais perto de fechar do projeto (1,07×) está SEM ROTA, por quatro fechamentos medidos

> ✅ **RE-VERIFICADO em 2026-08-20 (22:4x) contra o store `245dc93087d1`, censo
> `_censo()` = 166/205** — 22 curvas de censo depois, e **22 adoções** pelo meio. Os três
> números que sustentam o argumento voltaram **bit-idênticos**:
>
> | | doc (censo 144) | hoje (censo 166) |
> |---|---:|---:|
> | `r1` σ_res | 0,0268 | **0,0268** |
> | `r2` σ_res *(no tripé)* | 0,0103 | **0,0103** |
> | `r3` σ_res *(no tripé)* | 0,0073 | **0,0073** |
>
> ⇒ **os quatro fechamentos seguem de pé**, e a `r1` continua a mais perto do projeto
> (1,07×) sem rota. Isto é o que o §4.43 pede de um veredito datado: não *"foi medido
> um dia"*, e sim **reproduz no fingerprint vigente**. A imobilidade também é
> informativa — as 22 adoções do intervalo tocaram outras fontes, e nenhuma alcançou
> esta família, o que é consistente com o diagnóstico de que o desvio é **scatter de
> espécime na cauda** (2 de 9 pontos) e não forma do modelo.

**2026-08-19** · store `7a60cacb72de`, censo 144/205 · sondas **só-leitura**
(instrumental reusado de `yang2021_fratura_probe.py`) · **nada adotado, nada
mudou no store** · alvo 1 da sequência de ataque
(`New_Theory/PROMPT_ATACAR_AS_ABERTAS.md`).

## 1. Por que ela era o alvo 1 — e o que há de único nela

σ_res **0,0268** contra limite 0,025 (**1,07×**, a menor distância das 21
abertas); MAE 0,0167 e res.máx 0,0813 **passam**. E é a única aberta cuja
condição tem **três réplicas reais** — r2 e r3 estão **no tripé** (σ 0,0103 e
0,0073) com a **mesma** parametrização do modelo.

O resíduo mora na cauda: **±0,004 em 7 dos 9 pontos**, +0,040 em N=11300 e
+0,081 em N=11800.

## 2. Fechamento 1 — instrumento (grade esparsa): FALSIFICADO

Hipótese: o σ da r1 é medido em 9 pontos esparsos e o piso da família em grades
densas (57/56 pts) — maçã-com-laranja da classe do `n_cap`.

**Medido na própria grade de 9 pontos da r1** (interpolando as irmãs):

| par | σ na grade da r1 |
|---|---:|
| r1 vs r2 | 0,0129 |
| r1 vs r3 | 0,0099 |
| **modelo vs r1** | **0,0268** |
| modelo vs r2 (mesma grade) | 0,0070 |
| modelo vs r3 (mesma grade) | 0,0062 |

A grade não explica nada: mesmo nela, as irmãs concordam entre si 2–2,7× melhor
do que o modelo concorda com a r1. ⇒ **F7 pelo piso segue fechada**
(0,0268 = 2,6× o piso 0,0103), agora com a versão em grade esparsa também
medida.

## 3. A física do desvio, lida do dado cru

As vidas são **por espécime**: r1 morre em **12400**, r2 em **14649**, r3 em
**16251** (critério F/F₀<0,5). E o dado cru mostra a r1 **acima** das irmãs no
meio e mergulhando antes:

| N | r1 − média(irmãs) |
|---:|---:|
| 10500 | **+0,067** |
| 11300 | +0,049 |
| 11800 | +0,013 |
| 12200 | **−0,076** |

⇒ o resíduo da cauda é o **pré-colapso do espécime 1** invadindo a janela da
métrica (que vai até 11800 = 95 % da vida DELE, mas só 73–80 % da vida das
irmãs).

## 4. Fechamento 2 — rampa de fratura POR ESPÉCIME: âncora perfeita, métrica PIORA

A rota E2 do LIU_2025 (N_f como input por curva) aplicada aqui: C1 bisseccionado
para D(N_frat)=1 com a vida **lida do dado de cada espécime** — e o veredito de
29/07 não é reciclado, porque o escopo é outro (por condição, não global) e o
dado mudou (D-U re-ancorou; r2/r3 nem existiam).

**A âncora reconfirma o 6/6:** zero do modelo a 0,0–0,3 % da vida nas três
(C1 = 1,56e33 / 1,84e33 / 2,03e33 — monótono na vida, como deve).

**Mas a métrica da r1, na janela canônica:**

| forma | MAE | res.máx | σ_res |
|---|---:|---:|---:|
| baseline (sem fadiga) | 0,0167 | 0,0813 | 0,0268 |
| cliff (`D_on`=1,0) | **bit-idêntico** — predição registrada e confirmada |
| rampa (0,75, 16) — vencedora do treino de 29/07 | 0,0284 | 0,2155 | **0,0689** |
| rampa (0,85, 8) — a alternativa do treino | 0,0296 | 0,2369 | **0,0752** |

E r2/r3 com seus C1: **bit-idênticas** (os joelhos delas caem fora das janelas —
o isolamento por espécime funciona).

**Por que piora, e é geométrico:** o dado da r1 segura 0,878 até N=11800 e
despenca a 0,353 em 600 ciclos — um penhasco. Qualquer rampa suave o bastante
para zerar em 12400 já desceu em 11300–11800 (overshoot de até 0,22); o cliff,
que respeitaria o penhasco, cai **depois** do último ponto pontuado e é inerte
por construção. Uma forma intermediária fitada por curva é o que o G3 de 29/07
já falsificou (*"a melhor forma varia por curva"*) e o que o item D proíbe.

## 5. Fechamento 3 — trim: o vigente é CONSISTENTE com a convenção da fonte

A convenção dos trims do YANG_2021, medida nos 6 vigentes: cortar **o(s)
ponto(s) de queda terminal** (fig2 5850/CSV 5950 · amp1p0 3150/3250 · amp0p8
5450/5600 · amp0p5 27000/27400). O trim da condição (11800) corta exatamente a
queda terminal da r1 (11800→12400, 0,878→0,353). O ponto N=11800 retém 0,878 —
não é queda terminal, e cortá-lo seria um segundo corte escolhido para fechar a
curva: trave móvel sobre exceção assinada. **Não proposto.**

## 6. A leitura que fica

**O modelo está no CENTRO das três réplicas** — σ 0,0070 contra r2, 0,0062
contra r3, 0,0268 contra r1, na mesma grade. Movê-lo para fechar a r1 quebraria
as duas que fecham. O desvio da r1 é **dispersão de vida entre espécimes**
(15–25 %) invadindo a janela: real, física, e **não coberta pelo piso** da
condição, porque o piso é medido na janela comum onde as irmãs ainda estão no
platô.

⇒ a r1 segue **aberta e sem rota**, agora com o mapa completo: F7 fechada
(2,6×), forma de fratura fechada (2 formas pioram, cliff inerte), trim
consistente, instrumento descartado. O que a destravaria não é modelo: é ou uma
régua que reconheça dispersão de vida na cauda (decisão de régua = do
professor), ou nada — e "nada" é uma resposta que a regra de parada já
contempla.

## 7. Reprodutibilidade

Sondas do scratchpad da sessão reusando `yang2021_fratura_probe.py`
(`_instalar_ganchos`, `ancorar`, janela cheia para ancorar e canônica para
medir). Nada escrito no store; `FLOOR_TRIM` restaurado.
