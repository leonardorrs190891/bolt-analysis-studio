# P-7 EXECUTADA (opção mínima) — a fila publicada deixa de esconder 4 curvas

**2026-08-08** · assinada pelo professor · prereg
`docs/superpowers/specs/2026-08-08-p7-p15-execucao-prereg.md` · **gates 4/4**.

## O que mudou

`_FONTES_CLASSE_PARADA` perde **`LU_2024`** e **`SUN_2025_CRIMP`**:

```
antes:  CHU_2026 · JCSR_2023 · LIU_2025 · LU_2024 · SUN_2025_CRIMP · YANG_2019 · YANG_2021
depois: CHU_2026 · JCSR_2023 · LIU_2025 ·                            YANG_2019 · YANG_2021
```

**Razão:** as duas são **falsos positivos puros** — 0 curvas com o defeito da
classe e **2 com o defeito oposto**. O critério que as pôs ali é a razão de
inclinação terminal, que é **cega ao sinal**: dá o mesmo número alto para *"o
modelo nunca acelerou"* e para *"o modelo já desabou e está parado no piso"*.

Evidência independente por fonte: o `SUN` tem r = −0,74/−0,78 contra a forma do
grupo A e o remédio da classe falsificado em 4 doses; o `LU_2024` entrou por
decisão **documentada como frouxa** no próprio código.

## Qual das três opções, e por quê

A assinatura não nomeou uma. Executei a **mínima**, que é a marcada
*"(recomendada)"* no texto da P-7 e a única cujo custo foi medido **e
dissolvido**: as "2 órfãs" que ela criaria são artefato de um corte arbitrário de
70 % no classificador de bifurcação — 1,5 ponto percentual separa "P-13" de
"órfã", e na faixa decisiva a maior lacuna é 0,078 (`p7_orfas_resultado.md`).

A **opção 2** (marcador por curva) **não** foi executada: ela obriga a
re-derivar o critério (c) da regra de parada, o que é decisão nova e não
execução desta assinatura.

## Gates — 4 de 4

| gate | esperado | medido |
|---|---|---|
| **H1** censo | inalterado | **139**, intacto ✅ |
| **H2** as 4 curvas saem da classe | 4 | `classe_parada` **23 → 19** ✅ |
| **H3** cada uma cai em camada **nomeada** | 4/4 | 2 `LU` → **form_limited**, 2 `SUN` → **indecidível** ✅ |
| **H4** fila form-limited | *sem número previsto* | **2** |

⚠️ **O H4 não fixava número de propósito, e foi bom.** A P-7 previa *"fila
1→5"* — medido quando a fila era 1. Hoje ela sai de **0 para 2**. Ter escrito "5"
no prereg teria sido citar número de memória (§4.43) e teria dado gate falhado
por uma previsão que envelheceu, não por defeito da execução.

## O que a fila publica agora

| | |
|---|---:|
| fila form-limited | **2** — `lu2024_fig14_amp0p5_long` e `amp1p0_long` |
| redução de σ necessária | mediana **41 %**, máxima **64 %** |
| pernas violadas nas 2 | MAE 2 · res.máx 2 · σ 2 |

**As duas são as corridas longas do LU.** A P-7 não as conserta; ela as torna
**visíveis**, que é o que a proposta prometia: *"a leitura honesta da fila"*.

### ⚠️ ERRATA (mesma noite): elas **não** são o alvo da P-8

Escrevi aqui e na mensagem de commit que as duas eram *"exatamente o alvo da
P-8"*. **É falso**, e a própria P-8 diz por quê, no item 4 do que ela estabelece:

> *"**A `fig14` está certa** — CSV contra figura dá RMS 0,005, razão 1,000 contra
> o F₀ do registry nas duas curvas verificáveis."*

As **7** CSVs que desviam são todas `fig18` e `fig20`. As duas da fila são
**`fig14`** — que a P-8 mediu e considerou **corretas**.

**E a via indireta também não fecha.** A P-8 afrouxa `limite_sres(LU)` de 0,1030
para **0,1361**, e as duas são julgadas contra esse limite — mas ele só governa o
**σ**, e elas reprovam nas outras duas pernas:

| curva | MAE | res.máx | σ | passaria com 0,1361? |
|---|---:|---:|---:|---|
| `fig14_amp0p5_long` | 0,1257 (**2,51×**) | 0,3936 (**3,94×**) | 0,1235 | **não** |
| `fig14_amp1p0_long` | 0,4802 (**9,60×**) | 0,8553 (**8,55×**) | 0,2894 | **não** |

⇒ a P-8 **não** move nenhuma das duas, nem corrigindo o dado nem afrouxando a
barra. Dizer que ela ficou "mais relevante" por causa da P-7 foi **conclusão
minha sem medição**, e ela superestimava a proposta justamente onde isso poderia
enviesar a decisão. O que a P-8 decide segue sendo o que ela já dizia: **estar
certo**, com censo **+0**.

## Contagem por decisão, re-medida

| decisão | abertas |
|---|---:|
| **P-7** (o que resta na classe) | **10** |
| **P-9** | 8 |
| **P-13** | 7 |
| **P-14** | 4 |
| dado (sem rota de modelo) | **3** |

⚠️ A categoria **"dado"** subiu de 1 para **3**: além da `fig7c` (que perdeu o
piso na P-15), entram as **2 do SUN**, cuja fonte não tem piso medido — sair da
classe parada não lhes dá rota, só lhes tira o rótulo que dizia que não
precisavam de uma. Isso é honesto e era previsto: a P-7 troca *"parado numa
classe cujo remédio foi falsificado"* por *"sem rota, e sabemos disso"*.

## Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/regra_de_parada_triagem.py
py -3.12 New_Theory/mapa_das_65_fora.py --json New_Theory/mapa_das_65_fora.json
```
