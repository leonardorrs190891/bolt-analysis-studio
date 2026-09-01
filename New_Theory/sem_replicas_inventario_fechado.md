# "Faça tudo que puder sem réplicas" — o inventário, executado até fechar

**2026-08-19 (15:2x–16:0x)** · store `7a60cacb72de`, censo **144/205**
inalterado · sondas **só-leitura**, nada adotado · mandato das 15:22: *"faça
tudo que puder sem que dependa de réplicas, fique com os ensaios que temos"*.

## 0. O método

Inventariei **tudo** que restava executável sobre os ensaios existentes —
começando por conferir o histórico antes de re-propor (dois candidatos que eu
ia sondar **já estavam falsificados**: `graded_scrit` no YANG_2023 *"piorou a
0,50 nas três"* em 2026-07-29, e no YANG_2019 *"quebra o grupo"* em
2026-08-10). Sobraram três frentes não medidas. As três foram medidas.

## 1. YANG_2023 — `floor+residual` numa fonte SEM tripé a proteger

A ideia: o `loose_arrest_residual` morreu no ICMEZ **pelo trade com as
protegidas**; no YANG_2023 não há nada no tripé (0/9), as duas declaradas nunca
chegam ao piso (inertes por construção) e a exceção 0,25 idem. Sonda de 2
células, as 9 curvas:

| curva | baseline (mae/mx/σ) | (0,15, 0,5) | (0,20, 0,4) |
|---|---|---|---|
| 0,30 mm | 0,120/0,220/0,131 | 0,121/0,216/**0,106** | 0,124/0,246/**0,089** |
| 0,35 mm | 0,179/0,560/0,212 | **0,127/0,380/0,152** | **0,115/0,380/0,147** |
| 0,45 mm | 0,104/0,360/0,134 | 0,084/0,244/0,110 | **0,073/0,160/0,088** |
| 0,55 mm | 0,119/0,343/n<6 | **0,062/0,180** | **0,056/0,180** |
| 0,50 mm | 0,239/0,410/n<6 | 0,283 **piora** | 0,296 **piora** |
| 0,65 mm | 0,082/0,160/n<6 | 0,097 piora | 0,115 piora |
| 0,15 · 0,18 · 0,25 | — | **inertes bit-a-bit** ✓ | idem ✓ |

**Veredito: direção certa, ordem de grandeza insuficiente.** Melhoras de
30–50 % em quatro curvas — e o melhor σ pós-forma é **0,088 = 3,5×** o limite.
A 0,50 piora (retém demais; o piso freia mais — predito). **Zero células
fecham; ganho de censo zero.** E as três com n<6 nunca entram no tripé por
regra. A forma vale nota para o artigo (o meio-termo existe e o residual o
produz), não para o censo.

## 2. ICMEZ — a rota "gateada pelo regime" morre ANTES de ser construída

A rota que sobrou das **53 células** falsificadas estava nomeada com precisão
no prereg da lei de taxa (2026-08-15): *"a redução de perda no meio tem de agir
só no regime de gross slip — uma forma gateada pelo regime, não uma constante
compartilhada"*. Antes de construir a capacidade, medi a premissa: **o regime
separa alvos de protegidas?**

Instrumentando `resolve_transverse_slip` nas 8 (slip/δ mediano):

| curva | grip | slip/δ | regime | estatuto |
|---|---:|---:|---|---|
| amp0p3_F14p3_lk13p8 | 13,8 | 0,90 | GROSS | aberta |
| amp0p3_F17p6_lk13p8 | 13,8 | 0,87 | GROSS | aberta |
| amp0p4_F17p6_lk13p8 | 13,8 | 0,91 | GROSS | aberta |
| **amp0p4_F14p3_lk13p8** | 13,8 | 0,92 | **GROSS** | **TRIPÉ** |
| **amp0p4_F14p3_lk19p8** | 19,8 | 0,69 | **GROSS** | **TRIPÉ** |
| amp0p3_F14p3_lk19p8 | 19,8 | 0,56 | PARCIAL | aberta |
| amp0p3_F17p6_lk19p8 | 19,8 | 0,36 | PARCIAL | aberta |
| **amp0p4_F17p6_lk19p8** | 19,8 | 0,58 | PARCIAL | **TRIPÉ** |

⇒ **NÃO separa.** Duas das três protegidas estão em GROSS junto com três
abertas; a terceira protegida está em PARCIAL junto com duas abertas. Uma forma
só-gross pagaria as duas protegidas gross — o mesmo trade das 53 células, agora
provado inevitável por **qualquer** gate de regime.

E o quadro completo: abertas e protegidas se entrelaçam em **todos** os eixos
observáveis — amplitude (0,3 aberta / 0,4 mista), carga (F14p3 e F17p6 nos dois
grupos), grip (13,8 e 19,8 nos dois) e agora regime. **É a geometria dos inputs
do YANG_2021, na 4ª fonte.** Nenhuma f(inputs) separa os grupos.

## 3. SUN — os dois vereditos já estavam medidos e conferem

- `grease_crimp` (1,21×): o `loose_arrest_floor=0,142` está **lido certo** do
  dado (platô confere na 3ª casa — `sun_crimp_o_cadeado_estava_certo.md`); o
  0,162 que fecharia é caça a métrica sobre constante com procedência. Fechada.
- `grease_standard` (4,7×): canal rotacional morre cedo, dado atravessa; melhor
  alavanca chega a 3,2× e a dose seguinte explode. Fechada.

## 4. O que o dia inteiro estabelece — e é a afirmação central para o artigo

Com as medições de hoje, o fenômeno unificador tem **quatro fontes
independentes**:

> **Curvas abertas e curvas no tripé da mesma fonte se entrelaçam em todos os
> eixos observáveis dos inputs** (amplitude, carga, grip, regime de slip — e,
> nas fontes com réplicas, até dentro da mesma célula de inputs, com sinais de
> resíduo opostos). Nenhuma função determinística dos inputs separa os dois
> grupos. O que os separa é dispersão de espécime — vidas 15–46 % apart,
> pré-colapsos individuais, terminais não-monótonos publicados.

Consequência prática: **144/205 é o teto determinístico do corpus atual**, e
agora isso está medido por exaustão — não por desânimo: 53+7 células no ICMEZ,
6+4 no YANG_2023, 10 no ROUSSEAU, 6 no gth do YANG_2021, 16+25 no LU, 5 formas
de rampa no par LIU, e as rotas de exceção e de piso testadas às cegas e vazias.

## 5. O que segue disponível (nenhum item é de sessão)

1. **Réplica no ICMEZ** (experimento): destrava 5 curvas, 4 já passam MAE+mx.
2. **Decisão de régua** sobre dispersão de espécime (evidência em 4 fontes).
3. Nota de artigo: o meio-termo do YANG_2023 (§1) e o teto determinístico (§4)
   são material de publicação — exceções e limites medidos são o produto.
