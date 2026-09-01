# Prereg — a dependência de frequência do LI_2022 é INPUT, não tribologia

**2026-08-05** · decisão D-N (por delegação, MANDATO PERMANENTE) · gates
escritos **antes** de medir. Fingerprint de partida: `e38eed05fa47`.

## O que a leitura do PDF estabeleceu (Fig. 8 do Li 2022)

A **Fig. 8(b)** traz a envoltória **medida** da força axial do parafuso no 1º
ciclo do estágio II, com os valores **anotados no gráfico**:

| f | F_B,max | F_B,min | **oscilação ΔF_B** | razão vs 10 Hz |
|---:|---:|---:|---:|---:|
| 10 Hz | 19,10 kN | 9,76 kN | **9,34 kN** | 1,000 |
| 15 Hz | 17,53 kN | 10,22 kN | **7,31 kN** | **0,783** |
| 20 Hz | 16,53 kN | 10,82 kN | **5,71 kN** | **0,611** |

E os autores escrevem a cadeia causal, duas vezes:

> p5: *"as the frequency of the load increases, **F_B−min increases, whereas
> F_B−max decreases**. This indicates **the higher the frequency, the smaller
> the change amplitude of the bolt axial force** under the same amplitude"*
>
> p6: *"**With the decrease of the load frequency, the change amplitude of the
> axial force of the bolt increases, resulting in aggravation of the fretting
> wear** at the contact interface"*

**O modelo recebe `F_amp = 10 000 N` nas TRÊS frequências**
(`runner._AXIAL_F_AMP = {"LI_2022_TRIBOINT": 10e3}`, um valor por fonte). Daí
a cegueira medida: expoente de frequência **0,0038** no modelo contra
**1,0065** no dado, com perdas 15,39 / 15,37 / 15,35 %.

## Isto INVALIDA a premissa do D-G, que o gate barrou

O D-G propunha `fret_freq_exp` — um expoente tribológico "lido do dado". Ele
estava fitando a **consequência**, não a causa. O gate G3 barrou por outro
motivo (a curva longa piorava), mas a recusa estava certa: adotá-lo teria
enterrado a causa real sob um expoente que a compensa.

## A previsão de forma, com ZERO números novos

A lei do canal de flanco é `d_w ∝ p · slip^flank_amp_exp`, e
**`flank_amp_exp = 1,5` JÁ é o valor adotado** para esta fonte. Logo, se a
amplitude transmitida for o input correto, a perda deve escalar como
`razão^1,5`:

| f | razão de amplitude | **previsto: razão^1,5** | razão de perda MEDIDA |
|---:|---:|---:|---:|
| 15 Hz | 0,783 | **0,693** | 0,788 |
| 20 Hz | 0,611 | **0,478** | **0,497** |

O 20 Hz fecha quase exato (0,478 vs 0,497). **A ordenação e o vão de
frequência saem do input, sem constante nova.**

## Escopo

1. **Correção de input (0 números fitados):** `F_amp` por caso, escalado pelas
   razões da Fig. 8(b) — 10 Hz fica em 10 000 N (**referência, bit-idêntico**),
   15 Hz → 7 830 N, 20 Hz → 6 110 N. As razões vêm da figura; a escala
   absoluta **não muda**.
2. **Re-fit de 1 número:** `k_wear_flank`. O valor vigente foi ajustado contra
   uma estrutura de frequência **plana**, que era artefato do input. Mesma
   regra da re-adoção do HDPE do Rousseau: **quando o input muda, o fit contra
   o input velho perde procedência.**

⚠️ **NÃO entra neste prereg:** (a) o Φ absoluto — o modelo calcula 0,104 ⇒
1,04 kN de oscilação contra **9,34 kN medidos**, discrepância de ~9× que
depende da convenção de A_F (pico ou pico-a-pico) e é questão separada;
(b) a **saturação tardia** do canal de flanco; (c) o **nível** da
`axial_10Hz_full`, digitalizada da Fig. 8(a) (eixo 0–24 kN, ~10× mais grosso
que o da 8c) — os 0,0315 de discrepância são 1,6 % da altura daquele eixo.

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (referência intacta):** o caso de **10 Hz** fica **bit-idêntico** antes
  do re-fit (a razão dele é 1,000 por construção).
- **G1 (o gate que decide — VÃO DE FREQUÊNCIA):** a razão de perda do modelo
  entre 20 Hz e 10 Hz tem de cair de **0,997** (hoje) para dentro de
  **0,478 ± 0,08** — a faixa prevista pela lei `razão^1,5` com o expoente **já
  adotado**. Isto é predição de **forma**, medida **antes** de qualquer re-fit
  de nível. Se o vão não aparecer, o input não é a causa e o ramo é
  FALSIFICADO.
- **G2 (ordenação):** perda(10 Hz) > perda(15 Hz) > perda(20 Hz), estritamente.
- **G3 (isolamento):** as outras 4 fontes de `_AXIAL_F_AMP`
  (`LIU_2017_AXIAL`, `LIU_2016`, `GRZEJDA_2026`, `YANG_2023_AME`) ficam
  **bit-idênticas** — a correção é por caso do LI_2022, não na tabela global.
- **G4 (ganho):** a `axialmin_10Hz` **entra no tripé**; as `axialmin_15Hz` e
  `axialmin_20Hz`, hoje no tripé, **permanecem**.
- **G5 (nenhum caso pior):** nenhuma das 4 curvas da fonte piora > **+0,010**
  em qualquer perna. **Inclui a `axial_10Hz_full`** — e o prereg **proíbe**
  resolver isso declarando-a por causa da ambiguidade de nível da Fig. 8(a):
  se ela bloquear, o ramo é NÃO ADOTA e o estatuto vai para prereg próprio
  (regra do mandato).
- **G6 (procedência escrita):** as razões vêm da **Fig. 8(b), valores
  anotados**, citada no `prov` junto com as duas frases dos autores. O
  `k_wear_flank` é declarado **fit de 1 número sob o input corrigido**.
- **G7 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos 210 +
  censo/docs/páginas/testes no MESMO commit.

### Ramos

- **ADOTA** — G0..G5.
- **FALSIFICADO (input não é a causa)** — G1 falha: o vão não aparece mesmo
  com a amplitude corrigida ⇒ a dependência de frequência tem outra origem, e
  o `fret_freq_exp` volta a ser candidato legítimo.
- **NÃO ADOTA (a curva longa paga)** — G5 reprova na `axial_10Hz_full`.
- **INCONCLUSIVO** — o `F_amp` por caso não chega ao engine (conferir que a
  injeção não morre no filtro, como `emb_um`/`GA_member`/`trim_n_max` já
  morreram).

## Previsão registrada

Espero o vão aparecer **antes** do re-fit, próximo de 0,478. Espero que as três
`axialmin` fiquem **sub-prevendo** por ~2,5 pontos percentuais depois só da
correção de input (o nível vem do `k_wear_flank` velho, fitado contra a
estrutura plana), e que **1** número o resolva. Espero a `axial_10Hz_full`
como o ponto de tensão do G5 — ela é 10 Hz, logo o input dela **não muda**,
mas o re-fit do nível a atinge.

⚠️ **Se o vão aparecer e o re-fit não fechar a 10 Hz, eu prefiro ADOÇÃO
PARCIAL DECLARADA a soltar um segundo número** — o valor deste achado está na
**causa medida**, não no placar.
