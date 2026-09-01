# YANG_2019 auditado contra a lei D-N impressa — o dado está BOM, e apareceu uma corroboração de outra fonte

**2026-08-07 (madrugada)** · `yang2019_dn_auditoria.py` (só-leitura) ·
**nada adotado**.

## Antes: o padrão de auditoria está esgotado, medido

Varri os **11 PDFs** de `pdfs_open_access/` procurando tabela numérica de
retenção/decaimento (`ancoras_prosa_sweep.py`): **só o LU_2024 tem**. O padrão
"auditar CSV contra tabela impressa", que rendeu o bloco do LU nesta campanha,
não tem uma segunda aplicação.

Rede mais larga — frases numéricas no corpo do texto — por fonte:
`liu2017` 12 · `bauer2024` 8 · `karlsen2022` 5 · `lu2024` 5 · **`yang2019` 5** ·
`demir2024`/`liu2025`/`yang2021` 1 · `rousseau`/`yang2025` **0**.

As duas com mais âncoras (`liu2017`, `bauer2024`) **já fecham 100 %** no tripé.
⇒ o único alvo com âncora **e** curvas fora é o **YANG_2019**.

## A âncora do Yang 2019

Tabela 5 publica a "loosening D-N curve" como **`d^m · N = C`**, para três
níveis de pré-carga residual e **dois ramos** com inflexão em N ≈ 2500 (Fig. 8):

| ramo | 90 % | 80 % | 70 % |
|---|---|---|---|
| baixo ciclo | m 20,732 C 12 | m 15,526 C 63 | m 11,010 C 193 |
| alto ciclo | m 2,386 C 963,8 | m 2,028 C 1674,9 | m 2,028 C 1825,3 |

É previsão dos **próprios autores** a partir dos **próprios ensaios** — âncora
independente da digitalização. Escolha de ramo pelo lado certo de N=2500; se
os dois ou nenhum couberem, o script marca **AMBIGUO** em vez de escolher
(ramo mal escolhido inventaria discordância — acontece em d=0,8 mm).

## Resultado

| curva | 90 % | 80 % | 70 % |
|---|---:|---:|---:|
| `amp0p4_5Hz` | **1,05** | **0,90** | — |
| `amp0p6_10Hz` | 1,31 | 1,09 | — |
| `amp0p6_5Hz` | 0,58 | 0,87 | 0,95 |
| `varamp_large_to_small` | 0,20 | 0,25 | 0,40 |
| `varamp_small_to_large` | 0,67 | 0,55 | 0,51 |

**O que a lei pode auditar, e o que não pode:**

* **`amp0p4_5Hz` — auditável e PASSA** (1,05 / 0,90). A digitalização concorda
  com a lei dentro de 10 %.
* **As duas `varamp` — a lei NÃO se aplica.** São corridas de amplitude
  variável (blocos); uma lei D-N de amplitude constante não as descreve. O
  desvio de 0,20–0,67 **não é evidência de nada** e não deve ser citado como
  erro de dado.
* **As duas de 0,6 mm — a lei não resolve FREQUÊNCIA.** Ver abaixo.

⇒ **nenhum erro de digitalização encontrado no YANG_2019.** Ao contrário do
KARLSEN e do LU, o problema desta fonte **não é o dado**. Isso é consistente
com a classificação da triagem (as 4 fora estão em `classe_parada`) e reforça
que o alvo lá é forma, não input.

## ⚠️ Corroboração cruzada que apareceu de graça

As duas curvas de **0,6 mm** cruzam 90 % em **1900** ciclos (5 Hz) e **4263**
ciclos (10 Hz) — razão **2,24×** — com a previsão da lei (3261) caindo entre
elas. Isto explica por que a lei não as audita: ela foi ajustada sem a
frequência como variável.

Mas o número vale por si. **Se a perda for governada por TEMPO e não por
ciclo, dobrar a frequência dobra a vida em ciclos.** Medido: **2,24×**.

É exatamente a âncora física do **`fret_freq_exp = 1,0`** assinado na
adoção **D-V** (fretting ∝ 1/f = desgaste por tempo). A P-1 registrou como
custo que *"não existe held-out — o único outro grupo com canal de flanco é de
frequência única"*. Esta medição é **de outra fonte** e **não entrou** naquela
decisão.

⚠️ **Não é held-out formal e não deve ser vendido como tal:** o canal do
YANG_2019 pode não ser fretting, o par 5/10 Hz tem n=1 de cada lado, e a
comparação é de vidas, não de trajetória. É **corroboração**, e o que ela
autoriza é uma sonda dedicada — não um relaxamento da declaração da P-1.

## Reprodutibilidade

```bash
py -3.12 New_Theory/ancoras_prosa_sweep.py --json New_Theory/ancoras_prosa_sweep.json
py -3.12 New_Theory/yang2019_dn_auditoria.py --json New_Theory/yang2019_dn_auditoria.json
```
