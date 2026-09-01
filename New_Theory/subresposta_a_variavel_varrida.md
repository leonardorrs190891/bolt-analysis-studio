# Duas fontes, duas variáveis varridas, **o mesmo defeito estrutural**

**2026-08-05** · sondas só-leitura sobre o store `b70276f2fa43` (pós-D-Q, D-S,
D-R). Nada escrito.

## O padrão

Em **LI_2022_TRIBOINT** (varre **frequência**) e em **ROUSSEAU_2025** (varre
**espessura**), o modelo **sub-responde à variável varrida**: o viés é monótono
na variável e **troca de sinal no meio da varredura**. Não é erro de nível — é
erro de **inclinação da resposta**.

### LI_2022 — frequência

| f (Hz) | perda do DADO | perda do MODELO | viés |
|---:|---:|---:|---:|
| 10 | 0,1792 | **0,1539** | +0,0526 |
| 15 | 0,1417 | **0,1537** | +0,0271 |
| 20 | 0,0892 | **0,1535** | **−0,0158** |

Perda do modelo: espalhamento **0,03 %**. Do dado: **2,0×**. Ajuste
`perda ∝ f^−a` dá **a = 0,978** no dado (banda [0,603 · 1,415] com a dispersão
publicada, **excluindo zero**) contra **a = 0,000** no modelo.

### ROUSSEAU — espessura

| curva | t (mm) | viés | cruzamentos de sinal | σ_res |
|---|---:|---:|---:|---:|
| `steel_t10` | 10 | **+0,1548** | **0** | 0,0994 |
| `steel_t12` | 12 | +0,0016 | 1 | 0,0138 |
| `steel_t14` | 14 | **−0,0198** | 1 | 0,0130 |
| `hdpe_t10` | 10 | +0,0834 | 15 | 0,0691 |
| `hdpe_t12` | 12 | +0,0521 | 2 | 0,0456 |
| `hdpe_t14` | 14 | **−0,0413** | 0 | 0,0211 |

Nas duas curvas de aço 10 mm (`steel_t10` e `steel_t10_amp0p2`, viés **+0,1548** e
**+0,0957**) o **viés é exatamente o MAE** e há **zero cruzamentos**: todos os
resíduos positivos, o modelo retém demais em todos os pontos. Ao engrossar o
membro o sinal **inverte** — em 14 mm ele perde demais, nos dois materiais.

Zero do viés: **≈12 mm** no aço, **≈13 mm** no HDPE.

## Por que isto NÃO é "o modelo é cego à espessura"

O `k_member_shear` (= `GA_member`/t, em série com `k_tr`) **existe e funciona** —
o re-baseline de 2026-07-27 (item 10 do roadmap) mediu que o slip resolvido cai
0,232 / 0,134 / **0,000** mm do t10 ao t14, e que o t14 fica em **stick
permanente** pelos 400 ciclos. A resposta existe; o que a medição de hoje diz é
que a **magnitude** dela está errada, e errada de forma **monótona e com troca de
sinal** — assinatura de **expoente**, não de constante.

A forma vigente é `k_member ∝ 1/t`. Um expoente diferente de 1 daria resposta
diferencial. Isso é **exatamente** a estrutura do `fret_freq_exp` no LI_2022, cuja
janela viável foi medida hoje em [0,85 · 1,02].

## A simetria, e o que ela implica

| | LI_2022 | ROUSSEAU |
|---|---|---|
| variável varrida | frequência (10→20 Hz) | espessura (10→14 mm) |
| resposta do modelo | ~zero (0,03 %) | existe, mas fraca |
| viés | +0,053 → −0,016 | +0,155 → −0,020 |
| onde cruza zero | ~15 Hz | ~12–13 mm |
| lei candidata | `fret_freq_exp` | expoente de `k_member_shear` |
| janela medida | [0,85 · 1,02], fecha 4/4 | **não medida** |
| held-out para a lei | **não existe** (a outra fonte com canal de flanco é de frequência única) | ? |

⚠️ **A pergunta que decide a rota do ROUSSEAU é a mesma que matou a do
LI_2022: existe held-out? MEDIDO: NÃO.**

```
grupos que setam GA_member (k_member_shear): 1 de 69   (só ROUSSEAU_HDPE)
```

**Uma lei de espessura teria exatamente zero curvas fora da fonte-alvo para ser
testada** — a mesma trava estrutural do `fret_freq_exp`, por um caminho
independente.

### E há um segundo achado, que descarta a rota óbvia por ARITMÉTICA

O canal **não está ativo nas curvas de AÇO**, que são justamente as de maior
déficit:

| curva | `k_member_shear` |
|---|---|
| `hdpe_t10` / `t12` / `t14` | 2,20e6 / 1,83e6 / 1,57e6 N/m |
| `steel_t10` / `t12` / `t14` | **None** (canal desligado) |

A rota óbvia seria "ative-o também no aço". **Não funciona, e dá para saber sem
simular:** `GA_member` = 22 000 N no HDPE implica área de cisalhamento ≈ 44 mm²
com G ≈ 0,5 GPa. Com a MESMA área e o G do aço (≈ 79 GPa), `k_member_shear` a
10 mm daria **3,5e8 N/m** — cerca de **160×** o do HDPE. Em série com `k_tr`, um
elemento 160× mais rígido é **inerte**. O canal existe, mas para o aço ele **não
pode** carregar a resposta — nem com constante de procedência de handbook.

⇒ o déficit de espessura do aço vem de outro lugar (o grip entra em `k_b` via
`L_eff`), e nomear esse lugar exige sonda própria. **Não a fiz aqui para não
abrir candidato sem o pré-teste completo do charter.**

## Ressalva honesta sobre a `hdpe_t10`

Ela tem **15 cruzamentos de sinal** em 165 pontos e σ 0,0691. Não é nível puro:
tem ruído de traçado real (é a curva com amostragem densa, re-digitalizada em
2026-08-02) **e** erro de forma. Agrupá-la com as de aço seria forçar a classe;
ela entra na tabela pelo viés, que é grande (+0,0834), mas o diagnóstico de
"nível puro" vale para as **duas de aço 10 mm**, não para ela.

## Estatuto atual das 6

Todas as 6 estão em `indecidivel_sem_piso` na triagem — rótulo que se lê como
*"falta uma medição"* e que para esta fonte está **VENCIDO**: o paper publica
**uma corrida por condição** (varredura de texto por *repeat / average / std /
scatter / error bar / variability* devolve **zero**; Figs. 7/8, onde barras
morariam, têm marcador sem barra). **Não é pendência, é impossibilidade.**

Depois do **D-R** duas delas (`hdpe_t14`, `steel_t12`) saíram por **mérito** e o
grupo caiu de 6 para 4 na fonte (5 no total, com a IJPEM 0,25 mm). As 4 que ficam
são falhas de modelo reais, e agora com causa **nomeada e medida**.
