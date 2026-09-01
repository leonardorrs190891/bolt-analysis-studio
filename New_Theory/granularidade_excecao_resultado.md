# 3ª classe de prova por granularidade — **não existe** (atividade E)

**Data:** 2026-07-29 · **Store:** `3546e6745448` · resultado **NULO**, e o null é
o produto: fecha uma classe de exceção que eu próprio havia sugerido.

## A ideia, e por que ela morre

O estudo de granularidade achou que **1** curva tem ruído de dado acima do limite
do σ_res (0,0363 contra 0,025) e **4** com ruído entre metade e o limite. Eu
sugeri que essas 5 fossem candidatas a um terceiro tipo de prova — piso de
**granularidade**, ao lado do piso de **repetibilidade** (F7) e do julgamento
humano (S4).

**Errado, e pelo motivo que a própria F7 §1 já enuncia:** *o piso não absolve a
curva se o erro do modelo estiver acima dele.* Medido:

| curva | σ_res | ruído do dado | razão | veredicto |
|---|--:|--:|--:|---|
| `10_Yang_2023…0_35_mm` | 0,2118 | 0,0242 | **8,8×** | não absolve |
| `10_Yang_2023…0_30_mm` | 0,1312 | 0,0182 | 7,2× | não absolve |
| `10_Yang_2023…0_55_mm` | 0,1287 | 0,0242 | 5,3× | não absolve |
| `10_Yang_2023…0_45_mm` | 0,1344 | 0,0363 | 3,7× | não absolve |
| `caccese2009_tapered_45kN_rep2` | 0,0354 | 0,0154 | 2,3× | não absolve |

Mesmo a mais favorável erra **2,3×** o ruído do próprio dado. Nenhuma passa nem a
barra generosa (`σ_res ≤ ruído`), muito menos a barra correta (`≤ ruído/√2`).

## O que eu confundi, e a regra que fica

Confundi **"o piso é alto"** com **"a curva está desculpada"**. São coisas
diferentes: o piso alto reduz a margem *alcançável*, mas só absolve quem já está
dentro dele. É exatamente o erro que a F7 evita ao exigir a prova **por curva** em
vez de por fonte — e eu o cometi uma seção depois de escrevê-la.

**Regra:** um piso (de repetibilidade, de granularidade, de digitalização) só gera
exceção quando o erro medido **cabe dentro dele**. Piso alto sozinho é caveat de
interpretação, não perdão.

## Consequência para o pipeline

- **A fila de forma continua em 51.** Nenhuma sai por granularidade.
- **As 4 do Yang2023 ficam com margem apertada**, não perdão: com ruído 0,018–0,036
  contra limite 0,025, a margem útil delas é pequena — mas o modelo está 5–9× fora,
  então a granularidade não é o que as impede.
- **Sobra um caveat honesto para o número publicado:** 1 curva
  (`10_Yang_2023…0_45_mm`) tem ruído de dado **acima** do limite do σ_res. Para
  ela, mesmo um modelo perfeito ficaria em ~0,036 e não passaria. É a única do
  acervo nessa condição, e ela deve ser nomeada quando a meta for reportada — não
  como exceção, como limite declarado.
