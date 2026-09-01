# ROUSSEAU_2025 — não há piso de repetibilidade, e a `steel_t10` está ERRADA

**2026-08-05** · investigação só-leitura por subagente delegado, sob o MANDATO
PERMANENTE (regra de VAZÃO: subagentes só-leitura, um por fonte). Fingerprint
`b072b24fd3a8`. **NADA FOI ALTERADO** — nem CSV, nem config, nem store.

## Pergunta que motivou

Seis curvas do ROUSSEAU_2025 estão como **indecidíveis** na triagem porque a
fonte não tem piso de repetibilidade medido. Existe piso obtenível?

## Resposta 1: NÃO existe piso de repetibilidade, e não é obtenível

O paper publica **uma corrida por condição**. Varredura do texto completo:
`repeat`, `average`, `mean`, `std`, `standard deviation`, `deviation`,
`scatter`, `error bar`, `uncertain`, `variability`, `repeatab`, `twice`,
`three times` — **zero ocorrências**. A **Tabela 2** tem exatamente **seis
linhas**, uma por (material, espessura), sem coluna de réplica e sem `±`. Os
únicos `±` do paper são faixas de instrumento (RVDT ±45°, LVDT ±0,63 mm). O
abstract fala em *"each test resulting in complete preload loss"*, singular.
Data Availability: *"available on request (...) due to privacy"* — nada
depositado.

Figuras conferidas **na imagem** (renderizadas a 4×, não por resumo): Figs. 4,
5, 6 têm **uma curva por condição, sem whiskers**; e as **Figs. 7 e 8** —
exatamente onde barras de erro morariam — têm **um marcador por ponto, sem
barra nenhuma**.

## Resposta 2: existe piso de DIGITALIZAÇÃO, e ele é insuficiente

A mesma condição aparece em **duas** figuras (série temporal na Fig. 4/5 ×
resumo de rigidez na Fig. 7/8). A diferença mede piso de **digitalização**,
não de repetibilidade. Medido em **10 checkpoints** (5 curvas × 2 valores de
Nb), com as figuras extraídas como **vetor** e calibradas pelos rótulos de
eixo:

| | MAE | res.máx | σ |
|---|---:|---:|---:|
| piso bruto (n=10) | 0,0098 | 0,0200 | **0,0068** |
| sob a normalização que melhor casa cada figura | 0,0042 | 0,0125 | 0,0051 |

Como `limite_sres = max(0,025; piso)`, um piso de **0,007 deixa o limite em
0,025** ⇒ **não afrouxa nenhuma perna de nenhuma das 6 curvas.** Mesmo desfecho
do par LU_2024 fig18↔fig20 (σ 0,0192).

**O ganho é de ESTATUTO:** as 6 saem de *"indecidível — piso desconhecido"*
para **"piso medido e insuficiente"**. A barra não pode ser baixada por esta
fonte, e agora isso é uma medição, não uma suposição.

## Resposta 3 (não pedida, mais grave): a `steel_t10` está ERRADA

Nossa `digitized_csv/rousseau2025_steel_t10.csv` em N=100 lê **0,6634**. Três
instrumentos independentes do paper dizem **0,507–0,52** (traço vetorial da
Fig. 5: 0,507 · marcador da Fig. 8: 0,512 · leitura visual do render: ≈0,52).
**Erro de +0,157.**

E há **evidência interna** que dispensa o paper — verificada nesta sessão:

```
passos da nossa CSV entre N=100 e 160:
  −0,0780  −0,0781  −0,0780  −0,0781  −0,0780  −0,0781
desvio-padrão dos passos:  0,000050
```

**Seis passos consecutivos idênticos a quatro decimais.** Digitalização à mão
não produz isso: é uma **reta traçada entre dois pontos**, sobre a região onde o
paper mostra colapso **convexo**. Mesmo removendo o melhor fator de F₀, sobram
**0,057 de MAE puramente de forma**.

Mesma classe do defeito da `hdpe_t10` achado em 2026-08-02 — e a fonte tem
histórico: o **erratum de 2026-08-01** já corrigiu o drive do aço (10× errado).

## Resposta 4: nada mesclado, nada faltando

O paper tem exatamente **8 curvas F/F₀-vs-N** (3 HDPE + 3 aço + 2 da Fig. 6), e
**todas as 8 estão** em `digitized_csv/`. As 8 de rotação estão em `theta_csv/`,
os laços em `loops_csv/`. A Fig. 10 é laço força×deslocamento — **não pode** dar
curva F/F₀.

## O dado do paper é recuperável EXATO — e corrigi-lo piora o modelo

Figs. 4 e 5 são **polilinhas vetoriais com 1 amostra/ciclo**: **391–398 pontos**
(HDPE, 0→399 ciclos) e **183** (aço). Nossa biblioteca tem **9–16 pontos** em
quatro das cinco. Exceção: o Fb(14 mm) do aço é **raster** (1479×151) e exigiria
digitalização por pixel.

Efeito estimado da troca (aproximado — reusa `metric_pred`/`metric_x` do store e
substitui `metric_data`):

| curva | store (mae/mx/σ) | com o dado do paper |
|---|---|---|
| hdpe_t10 | 0,0919 / 0,1754 / 0,0712 | 0,1144 / 0,2028 / 0,0711 |
| hdpe_t12 | 0,0527 / 0,1074 / 0,0537 | 0,0570 / 0,1132 / 0,0534 |
| hdpe_t14 | 0,0440 / 0,0770 / 0,0299 | 0,0378 / 0,0637 / **0,0255** (erra por 2 %) |
| steel_t10 | 0,0725 / 0,1402 / 0,0803 | 0,1259 / 0,2396 / 0,0991 |
| **steel_t12** | 0,0451 / 0,0721 / 0,0292 | **0,0312 / 0,0486 / 0,0179 — ENTRARIA no tripé** |

**Três pioram, duas melhoram, uma entra.** É o padrão de 2026-08-02: corrigir o
dado piora o modelo, honestamente. E o precedente já foi estabelecido lá — a
`hdpe_t10` foi corrigida mesmo saindo de MAE 0,058 para 0,101.

⚠️ **A troca é aproximada.** Uma re-simulação real com 183–398 pontos muda a
janela da métrica, a âncora de alinhamento e o `n_max` do `FLOOR_TRIM`. Os
números acima são estimativa, não medição de adoção.

## Por que NÃO corrigi agora

Re-digitalizar muda o **dado**, que muda as métricas. A adoção **D-Q**
(saturação do flanco) está em voo, e o re-stamp dela pegaria as duas mudanças
juntas — tornando impossível atribuir qual efeito veio de qual. É a mesma razão
que separou D-H (forma) de D-I (nível) em passos com re-stamp próprio.

**Enfileirado como próximo passo após o D-Q fechar**, com prereg próprio.

## Risco latente que a investigação levantou

`hdpe_t10` e `hdpe_t12` **não** estão em `_SEM_FAMILIA_MECANICA`
(`report_html.py:2222`) e só ficam fora de uma família falsa pela diferença
**0,5 vs 0,49 mm** da Tabela 2 — a mesma sorte dos "1,6 N" que o próprio
comentário do código registra para o par `amp0p2`. **Arredondar esses deltas
ressuscita o defeito do erratum**, e a proteção atual é acidental, não
declarada.

## Uma medição que NÃO proponho como piso

Ripple intra-corrida do traço do paper (resíduo contra mediana móvel de 9 pts):
σ **0,0030–0,0127** em F/F₀, com a `hdpe_t10` sendo a pior (p95 |r| 0,0331). É
**ruído por ciclo**, não repetibilidade pela definição da campanha — e não o
proponho como piso. Mas é **limite inferior duro** de σ_res para um modelo suave
na `hdpe_t10`: nenhuma forma contínua pode ficar abaixo do ruído do próprio
traço. Se essa classe de medição pode ancorar piso é **decisão do professor**.
