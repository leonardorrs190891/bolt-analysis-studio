# O relógio de cauda: **sub-população de 5 em 18**, não classe — e o `KARLSEN` é o controle

**2026-08-16 (15:0x)** · só-leitura · **nada executado** · store `20be19aabe11`, censo
**144/205**, fora 61, abertas 21, `form_limited` 1.

---

## 1. A pergunta

O item **R** produziu uma forma nomeada — *"desaceleração de cauda no canal rotacional"* —
medida com relógio na `eccles2010_fig7d`: o modelo bate o dado a **1,01×** em ratio 0,60 e
a **0,08×** em 0,10 (130 ciclos contra **1643**). A regra de parada exige que uma classe
seja identificada por **≥2 instrumentos independentes**, então a pergunta é direta:

> a assinatura é do `ECCLES`, ou é classe?

**Instrumento:** razão `N_modelo / N_dado` no cruzamento de dois níveis (0,60 = cabeça,
0,25 = cauda), e a **degradação** = `r@0,25 / r@0,60`. Degradação < 1 significa que o
modelo se adianta progressivamente conforme a curva desce.

## 2. Medido nas 18 abertas com faixa suficiente

| case_id | r@0,60 | r@0,25 | degradação |
|---|---:|---:|---:|
| `eccles2010_fig7b` | 0,96 | 0,31 | **0,32** |
| `Yang_2023 … 0,30 mm` | 0,60 | 0,22 | **0,36** |
| `eccles2010_fig7a` | 0,92 | 0,44 | **0,48** |
| `Yang_2023 … 0,3x` | 1,58 | 0,82 | **0,52** |
| `sun2025 … grease_standard` | 1,06 | 0,62 | **0,59** |
| `sun2025 … grease_crimp` | 1,07 | 0,87 | 0,81 |
| `rousseau2025_steel_t10` | 1,37 | 1,15 | 0,84 |
| `eccles2010_fig3` | 0,94 | 0,80 | 0,84 |
| `eccles2010_fig7c` | 1,06 | 0,93 | 0,87 |
| `lu2024_fig18_amp2p0` | 0,99 | 0,96 | 0,97 |
| `karlsen2022_M42_HV_run20p0` | 1,00 | 1,05 | 1,05 |
| `karlsen2022_M30_HVtorqued_run14p2` | 0,90 | 0,95 | 1,06 |
| `karlsen2022_M30_HV_run2p2` | 0,93 | 1,00 | 1,08 |
| `karlsen2022_M30_HV_run7p1` | 0,99 | 1,07 | 1,08 |
| `karlsen2022_M30_HV_run1p2` | 0,93 | 1,01 | 1,09 |
| `karlsen2022_M30_HV_run6p2` | 0,91 | 0,99 | 1,09 |
| `karlsen2022_M42_HV_run21p0` | 0,85 | 1,02 | 1,20 |
| `lu2024_fig20_T22Nm` | 0,57 | 0,77 | 1,34 |

## 3. Veredito: **sub-população, não classe**

**5 de 18** (28 %) degradam abaixo de 0,8 — e elas atravessam **3 fontes**: `ECCLES` (×2,
com a `fig3` a 0,84 na fronteira), `YANG_2023` (×2), `SUN_2025` (×1, mais a `grease_crimp`
a 0,81). ⇒ **não é peculiaridade do `ECCLES`.**

⚠️ **Mas o controle negativo é forte e fecha a porta para "classe":** as **7** curvas do
`KARLSEN_2022` ficam **planas ou levemente invertidas** (1,05 · 1,06 · 1,08 · 1,08 · 1,09 ·
1,09 · 1,20) — o modelo **não** se adianta na cauda delas, ele até atrasa. Uma família
inteira sem o sinal, medida pelo mesmo instrumento, é o que separa *"sub-população com
assinatura comum"* de *"defeito estrutural do canal"*.

⇒ **a forma nomeada do item R vale para as 5, não para o engine.** Registrar como candidata
de escopo limitado, não como forma faltante universal.

## 4. ⚠️ VIÉS DE SELEÇÃO que este instrumento tem — declarado antes de citar o número

O modelo entra pela janela **trimada** (`metric_x`/`metric_pred`) e o dado pelo **CSV cru**.
Consequência: **curva em que o modelo é lento demais para cruzar 0,25 dentro da janela é
excluída em silêncio** (o cruzamento devolve `None`). ⇒ a amostra pende para curvas de
modelo **rápido**, que são justamente as que degradam.

**Logo os "5 de 18" são um TETO, não uma estimativa centrada.** O número honesto é *"pelo
menos 5 de 18 entre as que o instrumento consegue medir"*.

⚠️ É a **quarta** vez hoje que a assimetria janela-da-métrica × dado-cru contamina uma
leitura minha (`metric_data` como piso; mediana da fonte como proxy; `plateau` como
critério; agora seleção). O padrão não é descuido pontual — é que **quase toda sonda desta
campanha mistura as duas populações por default**, porque o store guarda a janela e o CSV
guarda o cru. Vale mais como aviso de instrumento do que como erro meu.

## 5. O que NÃO fiz

Não propus forma nova (assinatura), não mexi em config, não reclassifiquei camada. O item
**R** segue com recomendação **R2** e esta medição **reduz** o escopo do que ele expõe: a
desaceleração de cauda não é déficit universal do canal rotacional, é assinatura de uma
sub-população de 5 curvas em 3 fontes.

## Reprodutibilidade

Sonda inline no corpo do commit. Usa `T.classificar`, `T.pisos_medidos`,
`rh.caso_comparavel`, `load_full_curve` (CRU) e `CaseResult.from_dict` — nenhuma
reimplementa regra. O cruzamento é interpolação linear no primeiro ponto que desce abaixo
do nível.
