# O piso de 0,10 da métrica — quanto erro do modelo ele esconde, medido nas 38 curvas afetadas

**2026-08-16 (manhã)** · sonda só-leitura (`FLOOR_TRIM = 0` num sandbox) ·
**nada adotado, nada mudado no store** · censo intacto em 144/205.

## 1. A pergunta, e por que ela não era retórica

`runner.FLOOR_TRIM = 0.10` retira da métrica todo ponto com F/F₀ < 0,10 — e,
como o `CLAUDE.md` já registra, **encurta a simulação junto** (o `n_max` passa a
ser o último ponto sobrevivente do dado). O censo de curvas afetadas estava
documentado; **o erro escondido nelas, não**.

Isso importa porque um piso de métrica não é um filtro de dado: é uma **decisão
de modelagem disfarçada de filtro** — ele decide o que conta como "errado".

## 2. Escopo medido

**38 curvas** (fora as 3 do `UFU_LAB`, que saiu do projeto), **662 pontos
ocultos**, **12 fontes**: `LU_2024` 7 · `YANG_2023_IJPEM` 6 · `BAUER_2024` 5 ·
`SUN_2025_CRIMP` 5 · `ECCLES_2010` 4 · `KARLSEN_2022` 3 · `YANG_2019` 2 ·
`YANG_2021` 2 · `ROUSSEAU_2025`/`LI_2022_TRIBOINT`/`LIU_2025`/`ZHANG_2006` 1.

## 3. A resposta principal: na mediana, o piso é BENIGNO

| | MAE |
|---|---:|
| mediana na janela **julgada** | **0,0580** |
| mediana na região **oculta** | **0,0500** |
| razão | **0,86×** |

Em metade das curvas afetadas o modelo é **igual ou melhor** onde não é medido.
**10 de 30** têm erro oculto maior que o julgado. ⇒ a leitura *"o piso esconde
sistematicamente o pior do modelo"* está **refutada**.

## 4. Os três maiores desacordos ocultos — e dois deles são o piso FUNCIONANDO

| curva | pts julgados | pts ocultos | MAE julgado | **MAE oculto** | razão |
|---|---:|---:|---:|---:|---:|
| `sun2025efa109235_axial_F17.5kN_crimp` | 25 | 1 | 0,0316 | **0,9160** | **29×** |
| `sun2025efa109235_axial_F17.5kN_standard` | 24 | 1 | 0,0330 | **0,8593** | **26×** |
| `zhang2006_fig3_illus_M12x125_20kN_amp0p35` | 32 | 9 | 0,2110 | **0,7591** | 3,6× |

> ⚠️ **A 1ª redação chamou isto de "três desacordos catastróficos" e disse que
> *"um erro de 0,92 numa curva aprovada não é detalhe de contabilidade"*. Errado
> nos dois primeiros — bastou olhar os pontos.**

**As duas do `SUN` são FRATURA, e o piso está certo em descartá-las.** Ensaios
axiais (δ=0) a F₀=15 kN por 25–41 mil ciclos; o dado desce suave até **0,855**
(crimp) / **0,814** (standard) e o **último ponto cai a exatamente 0,000** num
único passo. Isso é ruptura do parafuso, e o modelo dessas configs **não tem
fratura ligada** — é *out-of-model* por decisão registrada (o `CLAUDE.md` já
lista fratura terminal entre os motivos de trim). Descartar um ponto de fratura
de um modelo sem fratura é o piso fazendo exatamente o trabalho dele. **Não é
achado.**

**A `zhang2006` é real, mas está DECLARADA.** Ali o dado desce a 0,012 enquanto o
modelo fica em **0,793** — 9 pontos, desacordo sustentado, sem fratura. O modelo
simplesmente nunca colapsa. A curva é *data-limited por procedência* desde
2026-07-31 (a Fig. 3 é rotulada "Illustration" e vem do rig do paper anterior),
logo está fora do censo por decisão anterior, não por causa do piso.

## 5. O ACHADO de verdade: os dois pisos são o MESMO NÚMERO, e isso torna o
limite estrutural do modelo invisível por construção

| curva | julgados | ocultos | MAE julgado | MAE oculto | razão | estatuto |
|---|---:|---:|---:|---:|---:|---|
| **`lu2024_M8_fig18_amp2p0`** | **6** | **7** | **0,0110** | 0,0695 | **6,3×** | **TRIPÉ** |
| `bauer2024_M8_fig6_rep3` | 12 | 2 | 0,0336 | 0,0815 | 2,4× | — |
| `karlsen2022_M42_HV_run20p0` | 7 | 1 | 0,0155 | 0,0413 | 2,7× | — |
| `lu2024_M8_fig20_T22Nm` | 13 | 4 | 0,0364 | 0,0209 | **0,57×** | **TRIPÉ** |

A `fig18_amp2p0` fecha o tripé com **0,0110** sendo julgada em **6 de 13
pontos**. Olhando a metade oculta, o erro não é ruído — ele **cresce
monotonicamente**:

| N | dado | modelo | erro |
|---:|---:|---:|---:|
| 15 | 0,083 | 0,114 | +0,031 |
| 24 | 0,029 | 0,099 | +0,070 |
| 34 | 0,013 | 0,097 | +0,084 |
| 47 | **0,006** | **0,093** | **+0,087** |

O dado vai a **0,006** e o modelo **para em 0,093–0,095**. Esse patamar não é
ajuste: é o **`loose_arrest_floor` = 0,10** adotado no `LU_2024` — o modelo não
consegue descer abaixo dele, **por construção**.

⚠️ **E aqui os dois pisos se encontram: `FLOOR_TRIM` = 0,10 (métrica) e
`loose_arrest_floor` = 0,10 (modelo, nesta fonte) são o MESMO NÚMERO.** A
consequência é exata: a região em que o modelo é **estruturalmente incapaz** de
seguir o dado é **precisamente** a região que a métrica não pontua. O limite
duro do modelo fica invisível não por acaso, mas porque os dois cortes coincidem.

Isso amarra três curvas da mesma fonte num **único** defeito estrutural: o
`loose_arrest_floor` é **uma fração única de F₀** servindo terminais que, dentro
do `LU_2024`, vão de **0,006** (`fig18_amp2p0`) a **0,309** (`fig20_T10Nm`) —
uma faixa de **50×**. Ele é simultaneamente alto demais para uma e baixo demais
para a outra.

⚠️ **A `T22Nm`, que entrou no tripé hoje, sai LIMPA deste exame** (razão 0,57 —
o modelo é melhor onde não é medido). A qualificação que eu havia levantado
sobre ela estava errada, e a correção está em
`lu2024_fig20_nao_monotonia_e_fisica.md` §4.

Nota de contexto: 6 pontos é **exatamente** o mínimo da regra `n < 6` (assinada
2026-08-01), então a `fig18_amp2p0` passa raspando em dois critérios ao mesmo
tempo.

## 6. O que isto NÃO autoriza

**Não autoriza baixar o piso.** As curvas afetadas foram *calibradas* sob esta
janela; mudá-la torna os 205 números não-comparáveis com todo o histórico da
campanha, e o `CLAUDE.md` já avisa: *"ao baixar o piso, os números deixam de ser
comparáveis ao publicado — medir nas duas janelas"*. Isto é uma **auditoria**,
não uma proposta.

**Não autoriza retirar curva do tripé.** O piso é regra global, aplicada
igualmente às 205, e as duas curvas citadas fecham na janela que a métrica
define. O que a auditoria produz é **procedência**: quem publicar
`fig18_amp2p0` como sucesso deve publicar junto que ela é medida em 6 de 13
pontos.

## 7. O que ele muda, na prática

1. **Proposta para a fila do professor (não executada):** o report por caso já
   imprime o tripé; passar a imprimir **"julgada em N de M pontos"** quando
   M > N tornaria a limitação visível onde ela é lida, sem mexer em régua
   nenhuma. Custa uma linha por página e nenhum número muda.
2. **Regra de sonda, esta sim imediata:** *toda leitura de terminal — do dado ou
   do modelo — exige `FLOOR_TRIM = 0` no sandbox.* Eu errei **duas** leituras
   hoje por não fazer isso (o terminal do dado, lido no último ponto acima do
   piso; e o do modelo, grampeado pelo `np.interp` sobre simulação truncada), e
   a segunda me fez publicar um resultado positivo que era falso.
3. ~~**Alvo nomeado para quem for atacar o `SUN_2025_CRIMP`**~~ ⛔ **retirado
   na conferência**: as duas curvas terminam em **fratura** (último ponto a
   0,000 num passo, depois de 25–41 mil ciclos), e o modelo dessas configs não
   tem fratura ligada. É *out-of-model*, e o piso está certo. Deixo o item
   riscado em vez de apagado porque ele mostra o que a auditoria por si só **não**
   decide: razão alta de MAE oculto **não** implica defeito de modelo — é preciso
   olhar os pontos.
4. **Alvo real, este sim:** o `loose_arrest_floor` do `LU_2024` é uma fração
   única servindo terminais de **0,006 a 0,309** na mesma fonte (50×), e por
   coincidir numericamente com o `FLOOR_TRIM` ele fica invisível. Três curvas da
   fonte apontam para a mesma constante — `fig18_amp2p0` (alto demais),
   `fig20_T10Nm` (baixo demais) e `fig20_T22Nm` (perto). Nenhuma lei de
   pré-carga serve, porque o dado é **não-monótono** (§ `lu2024_fig20_nao_
   monotonia_e_fisica.md`).

## 8. Reprodutibilidade

Sonda: re-simula as 38 afetadas com `runner.FLOOR_TRIM = 0` num pool de 6
processos e compara MAE dentro × fora da janela atual. Nada escrito no store; o
`engine_fingerprint` não é tocado (o piso é da métrica, não da física).
