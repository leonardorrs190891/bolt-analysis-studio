# Verificação D-X/D-Y contra o PDF — **INCONCLUSIVA**, e o controle é que diz isso

**2026-08-07 (madrugada)** · `karlsen_fig10_pdf_verifica.py` (só-leitura) ·
**nada revisto, nada adotado**.

## Por que se tentou

As adoções **D-X** (base da `run1p2` 315 → 331 kN) e **D-Y** (base da `run2p2`
312 → 333 kN) foram medidas num raster de **1252×790**
(`paper_figures/karlsen_2022__m30.png`). Só depois notei que há um **PDF
open-access no próprio repositório**
(`pdfs_open_access/karlsen2022_M30M42.pdf`), que a zoom 8 rende **3580×2126** —
cerca de **8× a resolução linear**.

Duas adoções assinadas com o pior instrumento disponível quando havia um
melhor. Verificar era obrigação, não opção.

## A calibração nova é excelente

**17 gridlines a 108,16 ± 0,91 px**, `kN/px` 0,2311, topo **400 kN exato** —
reproduz a estrutura que o PNG dera. A figura do Karlsen **não tem moldura
escura** (plota com grade cinza-clara), então o detector do LU não transporta:
procurar `dark` devolve zero linhas.

## O resultado, e por que ele não decide

| curva | adotado | PDF @ciclo 1 | razão | |
|---|---:|---:|---:|---|
| `run1.2` | 331 | 333,7 | **1,008** | confirma |
| `run6.2` (controle) | 340 | 343,6 | **1,011** | confirma |
| `run7.1` (controle) | 312 | 333,9 | 1,070 | **diverge** |
| `run2.2` | 333 | 370,2 | 1,112 | **diverge** |

O script declarou o critério **antes** de rodar: *"`run6.2` e `run7.1` tiveram
a base medida como CERTA pelo D-X; se divergirem aqui, o instrumento novo é que
está errado."* Um controle confirma, o outro falha ⇒ **inconclusivo por
construção**.

## E a assinatura da falha aponta para o meu instrumento

`run1.2` → **333,7** e `run7.1` → **333,9**: praticamente o **mesmo valor**. As
duas são azuis quase idênticas — **(87, 128, 202)** e **(87, 152, 212)**,
diferindo só no canal G — e no feixe inicial elas se sobrepõem. A atribuição por
vizinho-mais-próximo colapsou as duas no mesmo traço, e o valor que ambas
reportam é o topo do azul mais alto do feixe.

⇒ **resolução maior não resolve ambiguidade de cor.** O ganho de 8× em pixels
não ajuda onde o problema é que duas séries têm quase a mesma cor e se cruzam.

## O que fica de pé

As adoções **não** são revistas, e a razão não é conveniência:

1. **Duas extrações independentes** já concordaram na `run1.2` — o subagente do
   D-X (atribuição por swatch da legenda + vidas impressas) deu **332,7** e a
   minha do PNG deu **332,0**.
2. **Controles limpos naquela leitura**: `run7.1` +0,4 % e `run6.2` −0,2 %,
   medidos na **mesma coluna x**, o que provava que a coluna era o ciclo 1.
3. **Predição registrada e cravada**: o D-Y previu 0,0319/0,0569/0,0364 e mediu
   0,0315/0,0583/0,0364 — desvio máximo **0,0014**.

Contra isso, esta passada tem um controle falhando com assinatura de defeito
próprio. O ônus fica com ela.

## O que faltaria para a verificação valer

Desambiguar as duas azuis **antes** de ler o ciclo 1: traçar cada uma a partir
da região onde elas já se separaram (ciclos altos) e seguir para trás, em vez de
classificar pixel a pixel por cor. É trabalho de instrumento, não de física, e
fica registrado como pendência — não como dúvida sobre as adoções.

⚠️ **Lição de método que fica:** *procurar o PDF antes de digitalizar*. O
inventário `pdfs_open_access/` tem **11 papers** e eu não o consultei antes de
extrair do PNG. Não custou correção — custou uma verificação inconclusiva e o
tempo dela.

## Reprodutibilidade

```bash
py -3.12 New_Theory/karlsen_fig10_pdf_verifica.py --json New_Theory/karlsen_fig10_pdf_verifica.json
```
