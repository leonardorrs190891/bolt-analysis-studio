# As 29 abertas são **TRÊS populações mecânicas**, não uma fila de "form-limited"

**2026-08-10** · só-leitura · **nada adotado** · store `d197fc4c491c`, censo 144/205 ·
auditoria da premissa nunca testada: **o modelo escorrega onde o dado escorrega?**

## Método — instrumentação, não inferência

Envolvi `resolve_transverse_slip` num wrapper e re-simulei **as 29 abertas**, registrando
`slip` e `delta_amp` a cada chamada. Não usei a decomposição: neste mesmo mês eu contei
"curvas em stick" pelo `decomp` e errei **três vezes** (99 → 44 → 18), e o `CLAUDE.md`
registra a regra — *instrumente o resolvedor, não infira do decomp*.

## O resultado

| classe | n | fração | quem |
|---|---:|---:|---|
| **STICK** (slip = 0 em 100 % dos ciclos) | **6** | 21 % | `YANG_2021` ×3 · `LIU_2025` amp0p25/amp0p3 · `YANG_2023_IJPEM` 0,25 mm |
| **GROSS SLIP** (slip ≥ 0,95 δ) | **7** | 24 % | **as 6 do `CHU_2026`** + `rousseau steel_t10_amp0p2` |
| **PARCIAL** (0 < slip < 0,95 δ) | **16** | 55 % | `LU_2024` ×2 · `ROUSSEAU` ×3 · `SUN` ×2 · `YANG_2019` ×4 · `YANG_2023` ×3 · `LIU_2025` ×2 |
| modo-força | 0 | — | — |

## ⚠️ Isto CORRIGE uma conclusão minha de ontem

No trabalho profundo do `YANG_2021` eu escrevi que *"não existe regime intermediário: o modelo
só sabe travado ou gross slip pleno"*. **Verdade para aquela fonte, falso como generalização:**
o regime parcial ocorre em **16 das 29** abertas, com razões `slip/δ` de 0,44 a 0,89. O engine
**tem** graduação; o `YANG_2021` está num extremo (`onset/δ` = 2,97 a 4,95) onde a graduação
fica inalcançável. A correção importa porque a versão generalizada condenaria o engine por um
defeito que é de **uma fonte**.

## ✅ E explica mecanicamente DOIS nulls que eu havia registrado como "as curvas discordam"

**1. `LIU_2025` — o `C_creep` per-fonte falsificado (2026-08-09).** Eu medi que `amp0p25` e
`amp0p3` pedem `C_creep` **×0,5** e a `fig2_single` pede **×1,5**, e escrevi que *"as curvas da
fonte discordam sobre o valor da constante"*. Agora a razão é física:

| curva | classe | canais ativos |
|---|---|---|
| `amp0p25` (δ=0,25 mm) | **STICK** | só embedding + creep |
| `amp0p3` (δ=0,30 mm) | **STICK** | só embedding + creep |
| `amp0p8` (δ=0,80 mm) | PARCIAL (0,62 δ) | + wear + rotacional |
| `fig2_single` (δ=0,80 mm) | PARCIAL (0,62 δ) | + wear + rotacional |

⇒ **as duas populações não têm a mesma física**, então uma constante de creep compartilhada
tem de servir a "creep é tudo o que existe" e a "creep é um canal entre quatro". A discordância
não era das curvas: era do **regime**.

**2. `CHU_2026` — a correção de rugosidade que piorava (2026-08-10).** As 6 abertas do CHU
estão em **gross slip a 0,995–0,999 δ**. A correção que eu media mexia em `emb_depth` — e em
gross slip pleno o embedding **não é o canal dominante**. Não era "o modelo precisa da
rugosidade errada": era eu ajustando o canal errado para aquela população.

## O que isto reorienta na fila

A fila de 29 vinha sendo tratada como um bucket único de *form-limited*. São três alvos com
**alavancas disjuntas**:

* **STICK (6)** — nenhuma alavanca de slip alcança; só embedding/creep, e ambos saturam ou
  são compartilhados. Precisa de **perda sustentada sob stick** (a forma que o YANG_2021
  isolou). É a única classe realmente bloqueada por forma.
* **GROSS (7)** — o slip já é máximo; mexer em embedding é mexer no canal errado. Aqui as
  alavancas certas são as de **wear/rotacional** e o **teto** de slip.
* **PARCIAL (16)** — a maior classe, e a **menos investigada**. Tem os dois grupos de canais
  ativos ao mesmo tempo, então responde a alavancas de slip **e** de embedding — e é onde a
  varredura conjunta (lição D-AA) tem mais chance de pagar.

⚠️ **Consequência de método:** classificar por classe mecânica **antes** de escolher alavanca é
mais barato que descobrir depois que a alavanca não alcança o canal. Custo desta auditoria:
uma re-simulação instrumentada das 29 (~15 min, só-leitura).

## Limitações declaradas

* Só as **29 abertas** foram medidas. O censo completo em disp-mode (205 curvas) ficou fora por
  custo (instrumentação serial ≈ 2,5 h); as classes das que **passam** o tripé são desconhecidas.
* `slip/δ` é a razão do **máximo** ao δ imposto, não um perfil temporal — uma curva que começa
  em stick e termina em gross slip aparece como PARCIAL.
* O `frac>0` (fração de ciclos com slip) separa isso em parte: `yang2019_amp0p4_5Hz` tem
  `frac` 0,93 e `yang2023_0_35mm` 0,32 — a segunda passa **dois terços** do ensaio travada.

## Reprodutibilidade

Sonda no scratchpad (`stick_abertas.txt`): wrapper em `resolve_transverse_slip` sobre as
abertas obtidas pelo helper canônico. Só-leitura, ~15 min.
