# A fila em régua uniforme: quanto cada proposta pode **de fato** subir o censo

**2026-08-07** · só-leitura · `censo_por_proposta.py` (segundos).

## Por que

Ao corrigir a P-14 apareceu uma distinção que a fila não fazia: **"curva fora" ≠
"ganho de censo"**. Consertar uma curva que já é **exceção** ou **declarada** não
move o placar. E há um segundo filtro que nenhuma proposta declarava: o **sinal
do viés** — uma forma que *adiciona* perda só ajuda quem **retém demais**.

Aplicados os dois filtros às quatro propostas:

> ⚠️ **RE-MEDIDO em 2026-08-08, após a execução da P-7 e da P-15.** A tabela
> original (de 07-08, com censo 140) fica logo abaixo como registro datado.
>
> | decisão | **ABERTAS** | viés + | viés − |
> |---|---:|---:|---:|
> | **P-7** (o que resta na classe) | **10** | 7 | 3 |
> | **P-9** | 8 | 2 | **6** |
> | **P-13** | 7 | **6** | 1 |
> | **P-14** | 4 | **4** | 0 |
> | **dado** (sem rota de modelo) | **3** | 0 | **3** |
>
> **66 fora = 34 com estatuto + 32 abertas.**
>
> ⚠️ A categoria **"dado"** — que este documento havia visto vazia — tem **3**, e
> **todas com viés negativo**: a `fig7c` (perdeu o piso na P-15) e as 2 do `SUN`
> (saíram da classe parada na P-7, e a fonte não tem piso). Viés negativo
> significa que **o modelo já perde demais** nelas ⇒ nenhuma das formas propostas,
> que todas *adicionam* perda, as ajudaria. São genuinamente sem rota.

### Tabela original (2026-08-07, censo 140) — registro datado

| decisão | fora | c/ estatuto | **ABERTAS** | viés + | viés − |
|---|---:|---:|---:|---:|---:|
| **P-7** | 12 | 0 | **12** | 7 | 5 |
| **P-9** | 8 | 0 | **8** | 2 | **6** |
| **P-13** | 7 | 0 | **7** | **6** | 1 |
| **P-14** | 4 | 0 | **4** | **4** | 0 |
| (já com estatuto) | 34 | 34 | 0 | — | — |

**As 34 fora = 30 com estatuto + 4 abertas — as 4 classe-encerrada (vigente 2026-08-23 21:2x — as 2 do ECCLES retratadas FECHARAM POR MÉRITO (`arrest_approach_exp` por protocolo) ⇒ censo 171/205, fila ZERO; antes, no mesmo dia — as 2 provas de piso do ECCLES foram RETRATADAS em 2026-08-23 — o denominador estava inflado por contagem dupla do par declarado, prereg `fecha-tickets-e-dedup`; era 32 + 4 até 2026-08-21 17:0x — a fila de forma
encerrou em ZERO com a 11ª declarada, `liu2025_M16_amp0p8` por esgotamento medido;
as 4 "abertas" restantes são classe-encerrada, pós as VINTE E SEIS
adoções de 19-20/08 — SUN ×2, LU T10, ROUSSEAU ×4, ICMEZ ×5, YANG_2023 ×3, YANG_2019 amp0p4; era 61 = 40+21** O `mapa` já era honesto nisso (só
atribui decisão a curva sem estatuto) — o erro de misturar as duas coisas foi
**meu**, na primeira versão da P-14.

## O que a coluna do SINAL revela — e não é redundância

| proposta | sinal dominante | leitura |
|---|---|---|
| **P-9** | **negativo** (6 de 8) | o modelo perde **rápido demais** — coerente com *"relógio de Estágio I adiantado"* |
| **P-13** | **positivo** (6 de 7) | o modelo **retém demais** — coerente com *"falta o platô, sobra o arresto"* |
| **P-14** | **positivo** (4 de 4) | o modelo retém demais **por estar travado** |

⇒ **P-9 e P-13 têm defeitos de sinal OPOSTO.** Isso é evidência de que são
propostas distintas, não duas descrições do mesmo problema — o que não estava
demonstrado antes.

E a P-7, sendo reclassificação de camada (não forma nova), tem os dois sinais
misturados (7 × 5), como se espera de um balde heterogêneo — é exatamente o
argumento que a sustenta.

## Uma validação cruzada que valeu a pena

O conjunto-alvo da P-14 foi obtido por **duas rotas independentes**:

* **A** — classificador do `mapa`: `alcance is False` (o modelo nunca chega ao
  nível que o dado alcança) **e** sem estatuto;
* **B** — medição **direta** do slip resolvido (`resolve_transverse_slip`
  instrumentado nas 150 curvas disp-mode) `== 0`, **e** viés positivo, **e**
  aberta.

**Chegam exatamente às mesmas 4 curvas** — `yang2021_amp0p5mm_ax8kN` ·
`yang2021_amp0p6mm_ax8kN_r1` · `yang2021_amp1p0mm_ax2kN` ·
`10_Yang_2023_…_0_25_mm__2`. Dois instrumentos que não compartilham premissa
convergindo é o que faltava para confiar no número depois de três correções.

## ⚠️ Correção de atribuição no `mapa`

A classe `sub-perda` apontava para a **P-7** — **erro meu**: a P-7 é sobre
**reclassificar a camada `classe_parada`** e não tem relação com *"o modelo não
alcança o dado"*. Reapontada para a **P-14**, que é a proposta que endereça esse
defeito. Efeito: P-7 16 → **12**, P-14 0 → **4**.

⚠️ **Não é identidade.** A P-14 mira `slip == 0` (18 curvas, medidas); o teste do
mapa mira *"não alcança o nível do dado"*. As populações se sobrepõem sem
coincidir — a `liu2020_fig9` não alcança **e** desliza 399 µm, porque os canais
dela estão desligados por **config**. O store não guarda slip, então o teste
exato exige re-simular; o do mapa é a aproximação barata, e isso está dito no
código.

## Reprodutibilidade

```bash
py -3.12 New_Theory/mapa_das_65_fora.py --json New_Theory/mapa_das_65_fora.json
py -3.12 New_Theory/censo_por_proposta.py
```
