# Wear saturante FALSIFICADO — e a falsificação corrige a leitura da sub-classe B

**2026-08-09** · só-leitura · **nada adotado** · testa a proposta que o
`curvatura_causa_mecanica_resultado.md` deixara em aberto.

## O candidato

O doc anterior mediu que na sub-classe **B** o rotacional arresta (37 % → 2 %) e
o **wear assume 57 %** do incremento tardio — e propôs: *"o wear deveria
desacelerar quando o slip para"*. Testado por monkeypatch:

```
d_wear *= 1/(1 + δ_wear_acumulado / W_sat)      (W_sat → ∞ ⇒ idêntico)
```

com **discriminante embutido**: a forma tem de ajudar **B** e **não** ajudar
**A**. Se ajudar as duas, é botão genérico.

## ⛔ Falsificada em três doses

| W_sat | ganho médio de σ em **B** | em **A** | veredito |
|---|---:|---:|---|
| 2e-6 m | **−35,6 %** | −2,0 % | não discrimina |
| 5e-6 m | −17,9 % | −1,0 % | não discrimina |
| 2e-5 m | −2,2 % | −0,3 % | não discrimina |

Curva a curva: **3 das 5 curvas B movem +0,0 % a +0,8 %** — inertes. A `fig7c`
vai de σ 0,0258 para **0,0256** na dose mais forte, contra os **3 %** que faltam.
E a `liu2025_amp0p8` **colapsa** (σ 0,0396 → 0,1105).

## ⚠️ A causa: eu li **fatia** como se fosse **capacidade**

| curva | incremento tardio **total** | wear absoluto |
|---|---:|---:|
| `eccles2010_fig7c` | **0,0053** | 0,0048 |
| `eccles2010_fig7d` | 0,0038 | 0,0034 |
| `sun…grease_standard` | 0,0043 | 0,0024 |
| `jcsr2023_stainless` | 0,0812 | **0,0000** |
| `liu2025_M16_amp0p8` | 0,4566 | 0,2176 |

Em **3 das 5**, o terço final **inteiro** move menos de **0,5 %** da pré-carga.
O wear é 91 % disso — **91 % de quase nada**. E no `jcsr_stainless` o canal é
**exatamente zero**: os 57 % médios vinham de outras curvas.

Só a `liu2025_amp0p8` tem magnitude real — e é justamente a que colapsa.

⇒ **acertei qual canal domina o fim e errei se ele poderia importar.** É a
armadilha que o `CLAUDE.md` registra (*"a decomposição não decide"*), que eu
**citei no meu próprio doc** e não apliquei ao desenhar o teste. Fatia é
atribuição; capacidade é magnitude, e só a segunda decide se uma forma pode mover
a curva.

## ✅ O que a falsificação ENSINA sobre a sub-classe B

Se o terço final move **0,005** e o resíduo lá é **−0,022**, então o erro **não
se forma tarde** — ele já está presente, e o fim simplesmente **não tem
movimento suficiente para corrigi-lo**.

⇒ **a leitura "o modelo perde rápido demais no fim" está errada para 3 das 5.**
O correto é: *o modelo chega ao terço final já deslocado, e ali a curva está
praticamente parada nos dois lados.*

Isso reorienta a busca: para essas 3, o alvo é o **meio** do ensaio, onde ainda
há movimento — não o fim.

⚠️ **A sub-classe B se parte de novo:** `liu2025_amp0p8` (incremento tardio
0,46) e `jcsr_stainless` (0,08) são casos de movimento real; as outras 3
(0,004–0,005) são casos de **curva parada**. Um candidato para "B" tem de
escolher entre os dois.

## O que NÃO muda

O split **A × B** em si continua de pé — ele foi medido no sinal do resíduo e
confirmado pelo controle interno do `JCSR_2023` (mesma fonte, sinais opostos).
O que caiu foi a **explicação mecânica proposta para a B**, e a queda veio do
mesmo lugar de onde ela tinha vindo: a decomposição.

## Reprodutibilidade

Monkeypatch de `WearLoss.rate` com fator `1/(1+δ_w/W_sat)`, 3 doses × 9 curvas,
mais a leitura do incremento tardio absoluto do `decomp`. Scratchpad, minutos.
