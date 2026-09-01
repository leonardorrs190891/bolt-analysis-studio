# O "piso de digitalização" do LU mede CONCORDÂNCIA, não acurácia — as duas curvas erram juntas

**2026-08-07 (madrugada)** · sonda `lu2024_csv_vs_tabelas.py` (só-leitura,
segundos) · store `1c118e405a42` · **nada adotado**.

## O que ficou estabelecido antes

A sonda de pixel (`lu2024_fig18_extracao_resultado.md`) provou que a **figura**
reproduz a Tabela 8 a **±0,002** nas quatro curvas medidas, com o controle de
1,5 mm validado. Logo qualquer desvio de uma CSV contra a tabela impressa é
**da CSV**.

## Round-trip de todas as CSVs do LU contra as Tabelas 8 e 9

Lendo apenas **c10 e c50** — o c1 carrega o artefato de interpolação no
penhasco (+0,17 a +0,36 em várias) e não é evidência:

| curva | c10 | c50 |
|---|---:|---:|
| `fig18_amp0p25` | −0,0125 | −0,0103 |
| `fig18_amp0p5` | +0,0100 | +0,0118 |
| **`fig18_amp1p0`** | **+0,0439** | +0,0207 |
| `fig18_amp1p5` (D-W) | −0,0003 | +0,0002 |
| **`fig18_amp2p0`** | **+0,0792** | — |
| `fig20_T10Nm` | +0,0115 | +0,0069 |
| `fig20_T16Nm` | +0,0160 | +0,0103 |
| **`fig20_T22Nm`** | **+0,0724** | +0,0161 |
| `fig20_T28Nm` | +0,0274 | −0,0061 |
| `fig20_T4Nm` | +0,0078 | +0,0557 |

## ⚠️ O achado: o piso de digitalização da fonte é CEGO a viés compartilhado

A linha **22 N·m da Tabela 9 é idêntica à linha 1,0 mm da Tabela 8**
(36,8/57,1/87,9/93,6) — é o **mesmo ensaio publicado em duas figuras**, e o
`CLAUDE.md` já registra a `fig18_amp1p0` como `_CID_NAO_COMPARAVEL` por isso.
As duas formam a família mecânica `δ=1 F=4627`, que dá o **piso de
digitalização** da fonte:

```
piso do par:  MAE 0,0127   mx 0,0718   sigma 0,0192
```

Concordância excelente. Mas contra a tabela impressa **as duas desviam na mesma
direção**: +0,0439 e +0,0724 no c10 — e diferem entre si por só ~0,028.

⇒ **um piso construído com duas digitalizações da mesma família de figuras não
detecta viés compartilhado.** Ele mede *concordância*, e as duas concordam em
estar erradas juntas. É o análogo, um nível acima, do que a chave cega faz com
condições diferentes: ali o piso pareava coisas distintas; aqui pareia coisas
iguais **demais**.

Consequência prática para o LU: o número 0,0127, citado como "piso de
digitalização" da fonte desde 2026-07-31, **subestima o erro de digitalização
real por um fator de ~4** (0,0127 contra ~0,05 medido contra a tabela).

## ✅ A OUTRA METADE DO PAR, medida (2026-08-07) — a figura 20 também está certa

`lu2024_fig20_extrai.py`, calibração **própria** (outra página, outro clip),
validada por **controle interno**: as 4 séries coloridas contra as 4 linhas da
Tabela 9.

| série | c10 | c50 | c100 |
|---|---:|---:|---:|
| T10Nm | −0,0014 | +0,0065 | +0,0015 |
| T16Nm | +0,0017 | +0,0018 | +0,0026 |
| **T22Nm** | **−0,0040** | −0,0010 | −0,0016 |
| T28Nm | −0,0004 | −0,0001 | — |

Calibração: y **149,36 ± 0,44 px**/2000 N · x **142,40 ± 0,30 px**/10 ciclos ·
borda direita em 105,0 ciclos (eixo 0–100 com margem). **Âncoras confirmam o
par**: T22Nm **11 610 N** contra **11 554 N** da `fig18_amp1p0` — 0,5 %, o
mesmo ensaio em duas figuras.

⇒ **as duas metades do par estão medidas contra o impresso, e as duas figuras
concordam com as tabelas.** O desvio das CSVs (+0,0439 e +0,0724) é
inteiramente delas. O achado do viés compartilhado fica **confirmado com as
duas pontas**, não inferido de uma.

Resíduo declarado: o c1 da Fig. 20 desvia **+0,019 a +0,021 nas quatro séries**
— pequeno, uniforme e sem explicação medida. Como no c1 da Fig. 18, o 1º ponto
de qualquer CSV nova deve vir da **tabela**, não do pixel.

### ⚠️ Três defeitos de instrumento nesta extração, todos pegos pelo controle

1. **Ticks apontam para DENTRO** na Fig. 20 (a faixa externa tem zero escuros).
   Sondar a faixa errada devolve "0 ticks" — falha ruidosa, aceitável.
2. **Faixa larga captura as CURVAS que a cruzam.** Assinatura: espaçamento
   **128,6 ± 30,9 px** (24 %) onde o D-W registrou 145,0 ± 0,5. *Tick é
   uniforme; desvio-padrão grande significa que não são só ticks.* Conserto:
   exigir que o tick preencha ≥85 % da faixa — a curva só a **cruza**.
3. **A retícula tem de ser varrida do MAIOR passo para o menor.** Varrendo
   ascendente escolhe-se 71 px, que é **metade** do passo real (142) e portanto
   explica *todos* os pontos, inclusive os espúrios. Um divisor do passo
   verdadeiro é sempre um "ajuste perfeito" — e é sempre errado.

## Ranking honesto do erro de CSV (c10, contra instrumento de ±0,002)

1. `fig18_amp2p0` **+0,0792** — e ela está **no tripé hoje**
2. `fig20_T22Nm` **+0,0724** — exceção F7 hoje
3. `fig18_amp1p0` **+0,0439** — fora do censo (`_CID_NAO_COMPARAVEL`)
4. `fig20_T28Nm` +0,0274 — exceção F7
5. `fig20_T16Nm` +0,0160 — exceção F7
6. `fig18_amp0p25` −0,0125 · `fig20_T10Nm` +0,0115 · `fig18_amp0p5` +0,0100

As `fig14_*_long` ficam **fora desta leitura**: são a Fig. 14 (janelas 3–10×) e
comparar as âncoras c1–c100 da Tabela 8 com elas não é válido — o desvio
aparente de +0,18 a +0,84 é de janela, não de digitalização. Registrado para
que ninguém o cite como erro de dado.

## O que isto muda no plano

O prereg de re-digitalização do LU **não pode** tratar `fig18_amp1p0` e
`fig20_T22Nm` separadamente: corrigir uma sem a outra quebra o par, e corrigir
as duas muda o piso da fonte (que entra em `limite_sres` e nas 5 provas F7 do
LU). Mesma armadilha que a `run2p2` ensinou no D-Y, com um agravante: aqui o
par **é** a fonte do piso, não apenas metade dele.

Ordem que isso impõe, e que fica registrada antes de qualquer execução:

1. Re-digitalizar **as duas** do par no mesmo passo, com o 1º ponto vindo da
   **tabela** (o c1 de pixel tem ±0,05 não coberto pelo controle).
2. Re-medir o piso **depois**, e publicar antes/depois — ele vai **subir**, e
   subir piso afrouxa as 5 provas F7 do LU. Isso precisa ser dito, não
   descoberto depois.
3. Saldo declarado **antes**: a `amp2p0` é a de maior erro e está no tripé;
   corrigi-la pode tirá-la, como o D-U tirou a `yang2021_r1`.

## Reprodutibilidade

```bash
py -3.12 New_Theory/lu2024_csv_vs_tabelas.py
py -3.12 New_Theory/lu2024_fig18_extrai.py --json New_Theory/lu2024_fig18_extrai.json
```
