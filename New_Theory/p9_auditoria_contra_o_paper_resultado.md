# Auditoria da P-9 contra o **paper**: parecia contradição, e é o contrário

**2026-08-10** · só-leitura · **nada mudado** · store `9696038085e0`, censo 143/205.

## A suspeita

A nota de aparato do `YANG_2019` diz, sobre a fonte:

> *"Paper first shows (Fig 6) that **frequency (5 vs 10 Hz) barely matters** while displacement
> amplitude dominates — justifying displacement amplitude as the damage driver (V2 disp-mode
> premise)."*

E a config adotada carrega **`s1_freq_exp = 1.0`, `s1_freq_ref = 5.0`** — a **P-9, adotada por
mim em 2026-08-09** —, que faz o alvo do embedding escalar com `(f_ref/f)`. À primeira leitura:
introduzi dependência de frequência numa fonte cujo próprio artigo reporta
**insensibilidade** a frequência.

## A medição — e ela inverte a leitura

Sonda do instrumento primeiro (lição do CHU): `s1_freq_exp` = 1,0 no cfg efetivo, curvas em
5 Hz, 10 Hz e varamp. Depois, as 5 curvas com a P-9 **desligada**:

| curva | freq | P-9 ligada (hoje) | P-9 desligada | viés |
|---|---|---|---|---|
| `amp0p4_5Hz` | 5 Hz | 0,0995/0,1423/0,0773 | **idêntico ao dígito** | −0,0803 → −0,0803 |
| `amp0p6_5Hz` | 5 Hz | 0,0857/0,5170/0,1534 | **idêntico ao dígito** | +0,0339 → +0,0339 |
| `varamp_large_to_small` | — | 0,0519/0,1364/0,0580 | **idêntico** | +0,0188 → +0,0188 |
| `varamp_small_to_large` | — | 0,0636/0,1939/0,0803 | **idêntico** | +0,0006 → +0,0006 |
| **`amp0p6_10Hz`** | **10 Hz** | **0,0310/0,0665/0,0351** | 0,0552/0,0886/0,0365 | **−0,0097 → −0,0524** |

⚠️ Aqui o "idêntico ao dígito" **não** é instrumento morto — é **por construção**: com
`f_ref = 5 Hz`, o fator `(5/5)^1 = 1` exatamente nas curvas de 5 Hz, e a P-9 foi desenhada
default-inerte. A sonda confirmou que o campo está no cfg e que a curva de 10 Hz **move**.

## O veredito: a P-9 torna o modelo MAIS insensível à frequência

O par casado do paper é `amp0p6_5Hz` ↔ `amp0p6_10Hz` (mesma amplitude, frequências diferentes).
A distância entre os viesses do modelo nesse par:

| | 5 Hz | 10 Hz | **|Δviés| no par** |
|---|---|---|---|
| **sem** P-9 | +0,0339 | −0,0524 | **0,0863** |
| **com** P-9 | +0,0339 | −0,0097 | **0,0436** |

⇒ a P-9 **corta pela metade** a discrepância que o modelo cria entre as duas frequências. O
paper diz que frequência quase não importa **no dado**; sem a P-9, o modelo dizia que importa
0,086 de pré-carga. Com ela, 0,044.

**Resolução da aparente contradição:** o que precisa ser pequeno é a sensibilidade **total** do
modelo, não a de cada termo. O engine já tinha dependência de frequência **implícita** — o
creep é dirigido por **tempo**, não por ciclo, então a 10 Hz o mesmo número de ciclos vale
metade do tempo e metade da fluência. A P-9 entra no embedding em sentido **oposto** e cancela
parte disso. Um termo com dependência de frequência tornando o conjunto menos dependente de
frequência não é paradoxo; é compensação de um viés que já existia sem nome.

## Escopo real da P-9, medido

**1 curva de 205.** Ela é inerte por construção em tudo que roda a 5 Hz (o `f_ref`) e nas
varamp. Isso é mais estreito do que a adoção sugeria, e é bom que esteja escrito: qualquer
leitura futura de *"a P-9 mudou a fonte"* está errada — ela mudou **a única curva a 10 Hz**.

## O que a auditoria NÃO absolve

O par casado segue mal modelado em termos absolutos: a `amp0p6_5Hz` tem res.máx **0,5170** (5,2×
o limite). A P-9 não toca nela e não pretendia. O que esta auditoria estabelece é que a P-9 não
contradiz o achado impresso do artigo — **não** que a fonte esteja bem representada.

## Método

Terceira vez em dois dias que abrir a **prova gravada** antes de agir mudou o resultado: no CHU
ela retirou um candidato meu; aqui ela levantou uma suspeita legítima contra uma adoção minha
de ontem, e a medição a resolveu **a favor** da adoção. Nos dois casos o custo foi de minutos e
o erro evitado seria de dias.

## Reprodutibilidade

`p9_audit.py` no scratchpad — override `s1_freq_exp = 0.0` nas 5 curvas do `YANG_2019`, com
sonda do instrumento antes do veredito. ~3 min, só-leitura.
