# O canal de frequência do YANG_2019 tem TETO DE AUTORIDADE — e a causa raiz é o relógio de Estágio I

**2026-08-07 (madrugada)** · `yang2019_freq_sonda.py` + varredura de teto ·
só-leitura · **nada adotado**.

## ⛔ Errata de um número que eu publiquei há uma hora

`yang2019_dn_auditoria_resultado.md` cita *"razão **2,24×**"* como se fosse **a**
razão de vida entre 10 Hz e 5 Hz. **É a razão num nível só.** Medida em três:

| nível | razão do dado |
|---|---:|
| 0,90 | **2,24×** |
| 0,85 | 1,68× |
| 0,80 | **1,26×** |

Uma lei 1/f pura daria **2,00 em todos**. ⇒ **o dado também não é 1/f puro**: o
efeito de frequência é **forte no Estágio I e fraco no II**. Citar 2,24 sozinho
foi seleção involuntária do nível mais favorável à corroboração que eu estava
propondo. A corroboração fica **enfraquecida**, não anulada.

## Teto de autoridade: o canal não alcança o alvo

`dmg_dwell_exp = 1,0` com `f_ref_dmg = 10,0` está **adotado** nesta fonte.
Varredura (5 pontos):

| `dmg_dwell_exp` | MAE 5 Hz | MAE 10 Hz | razão @90 % |
|---|---:|---:|---:|
| 0 (canal OFF) | 0,0867 | 0,0552 | **1,10** |
| 1 (adotado) | 0,0857 | 0,0552 | **1,10** |
| 2 | 0,0941 | 0,0552 | **1,10** |
| 4 | 0,1101 | 0,0552 | 1,06 |
| 8 | 0,1120 | 0,0552 | 0,93 |

Três leituras, nenhuma delas "parâmetro morto":

1. **A razão @90 % é 1,10 para TODO expoente, inclusive 0 e 8.** O alvo (2,24×,
   ou mesmo a mediana 1,68×) está **fora do alcançável** ⇒ teto de autoridade.
2. **O lado 10 Hz é bit-idêntico em todos os expoentes** (MAE 0,0552), e isso é
   **por construção**: `f_ref_dmg = 10`, logo o fator `(f_ref/f)^exp` vale 1 na
   própria referência, qualquer que seja o expoente. Não é inércia — é o ponto
   fixo da lei.
3. **No lado 5 Hz o canal AGE** (MAE 0,0867 → 0,1120) e **piora
   monotonicamente**. Então não é canal morto; é canal que atua no lugar errado.

## A causa raiz, que os números absolutos entregam

| | N @90 % |
|---|---:|
| modelo 5 Hz | **160** |
| modelo 10 Hz | **175** |
| dado 5 Hz | 1900 |
| dado 10 Hz | 4263 |

O modelo cruza 90 % **11× a 25× cedo demais**. Um canal de **dano acumulado**
não pode produzir efeito de frequência num ponto que o modelo atinge antes de
haver dano acumulado — daí o teto. **O defeito não é a lei de frequência; é o
relógio de Estágio I.**

## Convergência de classe, entre fontes

Isto é o **mesmo defeito** que o `s1_amp_gate_resultado.md` nomeou no LIU_2025
(N₉₅ constante-108 onde o dado varre 850×) e que o
`classe_parada_discriminante_resultado.md` mediu como **ESPELHADO** nas 3 curvas
de baixa amplitude daquela fonte: **o modelo perde pré-carga cedo demais no
Estágio I.**

E a capacidade existe: **`s1_amp_gate_*`** (gate Hill de regime de amplitude nos
relógios de Estágio I), **default-inerte**, com adoção declarada
**INCONCLUSIVA** no LIU_2025 porque *a Fig. 4 e as curvas digitalizadas daquela
fonte discordam do N₉₅ em 3–5× nas duas direções*.

⇒ **o YANG_2019 pode ser a fonte que faltava**: a auditoria da lei D-N de hoje
mostrou que o **dado dele está bom** (nenhum erro de digitalização), e ele tem
âncora impressa independente (`d^m·N = C`) para o relógio. É a consistência
interna que o LIU_2025 não tem.

⚠️ **Não medido:** que o `s1_amp_gate` feche estas curvas. A afirmação é sobre
**identificação de classe** e sobre **disponibilidade de âncora**, não sobre
resultado. Exige prereg próprio com o gate escrito antes.

## O que isto NÃO autoriza

Não relaxa a declaração da **P-1** (`fret_freq_exp` per-fonte sem held-out). A
corroboração que eu propus há uma hora sai **mais fraca** desta medição, não
mais forte: o dado não é 1/f puro, e o canal do YANG não reproduz a razão nem
com autoridade 8×.

## Reprodutibilidade

```bash
py -3.12 New_Theory/yang2019_freq_sonda.py --json New_Theory/yang2019_freq_sonda.json
```
