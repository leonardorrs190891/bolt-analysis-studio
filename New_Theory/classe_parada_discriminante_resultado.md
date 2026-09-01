# A classe "aceleração tardia" foi montada com um número CEGO AO SINAL — 10 das 23 têm o defeito ESPELHADO

**2026-08-06 (noite)** · sonda só-leitura `classe_parada_discriminante.py` ·
store `5916d8be0510` · **PROPOSTA, não adoção** (reclassificação de camada da
triagem exige assinatura — charter).

## O que motivou medir

O `sun_crimp_resultado.md` de hoje encontrou que `SUN_2025_CRIMP` é falso
positivo em `_FONTES_CLASSE_PARADA`: a razão de inclinação terminal vale 25,0
não porque o modelo deixe de acelerar, mas porque ele **já desabou e está
estacionado no `loose_arrest_floor` desde N=167**.

Isso não é um acidente de uma fonte. É uma propriedade do **critério de
entrada**: inclinação terminal ~0 tem duas causas opostas, e a razão dá o mesmo
número alto para as duas. Um estatístico que não distingue *"nunca acelerou"* de
*"já acabou"* não classifica — ordena.

## O desempate, e por que ele é grátis

Sinal do viés terminal `mean(modelo − dado)` no último terço dos pontos da
métrica (confirmado no último quarto; divergência de sinal ⇒ `AMBIGUO`, nenhuma
ocorreu):

* **> 0** — modelo RETÉM mais que o dado no fim ⇒ faltou acelerar ⇒ **classe**.
* **< 0** — modelo ABAIXO do dado ⇒ desabou cedo ⇒ **ESPELHADO**; o remédio da
  classe (acelerar mais) **piora**.

Sai de `metric_pred`/`metric_data` já gravados no store — zero simulação.

## Resultado: 13 classe · 10 ESPELHADO · 0 ambíguo

| fonte | classe | espelhado | veredicto |
|---|---:|---:|---|
| `YANG_2021` | 3 | 0 | **coerente** |
| `JCSR_2023` | 2 | 0 | **coerente** |
| `CHU_2026` | 5 | 1 | mista |
| `YANG_2019` | 2 | 2 | mista |
| `LIU_2025` | 1 | 3 | mista |
| `LU_2024` | 0 | 2 | ***falso positivo*** |
| `SUN_2025_CRIMP` | 0 | 2 | ***falso positivo*** |

**Só 2 das 7 fontes são coerentes com a classe que as parkou.** As duas puras
espelhadas confirmam o achado do SUN e o estendem: o `LU_2024` está documentado
como tendo entrado **pela razão sozinha** (o comentário em
`regra_de_parada_triagem.py:67` diz que ele e o `YANG_2021` foram *excluídos do
TESTE* por cauda de fratura e entraram só por `razão terminal > 2`). O
`YANG_2021` sobreviveu a essa entrada frouxa; o `LU_2024` não.

## ⚠️ O que isto NÃO diz — limitação do instrumento, nomeada

Viés e inclinação respondem a **perguntas diferentes**, e uma curva pode estar
*acima* do dado e ainda assim *caindo mais rápido*. O caso extremo está na
tabela: `chu2026ti_D0p7mm_F0_49kN_test4` tem viés **+0,032** (classe) e razão
**0,03** — a inclinação terminal do modelo é ~30× a do dado, o oposto de "não
acelera". Pelo critério original ele **nem entraria** na classe (exige razão >2);
está parado só porque a FONTE está.

⇒ o veredicto por curva acima é sobre **nível terminal**, não sobre forma
completa. Ele é suficiente para dizer *"o remédio da classe não se aplica"*
(a direção está errada), e **insuficiente** para dizer o que se aplica.

## As espelhadas do `LIU_2025` já têm diagnóstico E capacidade construída

Não é resíduo aleatório. As 3 espelhadas são `amp0p25` (−0,0893), `amp0p3`
(−0,0717) e `amp0p8` (−0,0139): **o viés cresce quando a amplitude cai**, e o
modelo fica **abaixo** do dado — perde pré-carga cedo demais.

Isso é, na direção e na ordenação, o defeito que o `s1_amp_gate_resultado.md`
já nomeou nesta fonte: **N₉₅ constante-108 onde o dado varre 850×**, disparando
cedo em amplitude baixa. A capacidade existe no engine
(`s1_amp_gate_*`, gate Hill de regime de amplitude nos relógios de Estágio I,
**default-inerte**) e a adoção está **INCONCLUSIVA** por motivo de dado, não de
modelo: a Fig. 4 e as curvas digitalizadas da MESMA fonte discordam do N₉₅ em
3–5× **nas duas direções**.

⇒ o bloco `LIU_2025` do balde parado não é "forma faltante encerrada"; é
**candidato com remédio construído, travado por inconsistência interna da
fonte**. Estatuto mais próximo: `data-blocked`, não `classe_parada`.

⚠️ **Não medido aqui:** que ligar o `s1_amp_gate` fecharia estas 3. A afirmação
é sobre **direção e ordenação do viés**, que coincidem; fechar exige a sonda de
2 pontos e um prereg próprio.

## Consequência para a leitura da fila

A triagem publica **fila form-limited = 1**. Esse 1 é a
`karlsen2022_M30_HVtorqued_run14p2`, pior perna **2,36×**. No balde parado há
**5 curvas mais perto do tripé do que ela**:

| curva | pior perna | veredicto |
|---|---:|---|
| `liu2025_M16_fig2_single` | 1,07× | classe |
| `chu…Ra1p6um_test9` | 1,17× | classe |
| `sun…transverse_grease_crimp` | 1,21× | **espelhado** |
| `yang2021_amp0p6mm_ax8kN_r1` | 1,27× | classe |
| `liu2025_M16_amp0p3` | 1,29× | **espelhado** |

⇒ **"a fila é 1" é artefato de estacionamento POR FONTE.** A parada por classe
foi assinada sobre a classe; ela não autoriza parar curva cujo defeito é o
oposto do da classe.

## PROPOSTA ao professor (3 opções, nenhuma executada)

1. **Mínima** — retirar `LU_2024` e `SUN_2025_CRIMP` de `_FONTES_CLASSE_PARADA`
   (as duas puras espelhadas). Custo: fila 1 → 5. Ganho: para de esconder 4
   curvas cujo defeito é o oposto do que a parada encerrou.
2. **Por curva** — trocar o marcador de por-fonte para por-curva, usando este
   discriminante. Fila 1 → 11 (as 10 espelhadas + a `karlsen`). Mais honesto e
   mais caro; exige re-derivar o critério (c) da regra de parada, cuja mediana
   muda de população.
3. **Nada** — manter, registrando que o marcador é por fonte e que 43 % do
   balde tem defeito oposto. Aceitável se a decisão for que nenhuma das duas
   classes é atacável hoje; **inaceitável em silêncio**, porque a fila publicada
   passaria a leitura errada.

Recomendação: **(1)**. É a que tem evidência independente nas duas fontes
(`SUN`: r = −0,74/−0,78 contra a forma do grupo A em
`kernel_diagnostic_2026-07-27.md`, remédio da classe falsificado em 4 doses;
`LU_2024`: entrada documentada como frouxa) e a que não força re-derivar a
regra de parada no mesmo passo.

## Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/classe_parada_composicao.py
PYTHONPATH=src py -3.12 New_Theory/classe_parada_discriminante.py
```

Os dois importam `_FONTES_CLASSE_PARADA` e `pisos_medidos` **do arquivo da
triagem** — nenhuma regra de limite reimplementada (a advertência de
`regra_de_parada_triagem.pisos_medidos`).
