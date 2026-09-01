# A família fig18 do LU_2024 contra a Tabela 8 — só a consertada casa

**2026-08-06 (noite)** · campanha MARGENS, subproduto do **D-W** quantificado
nas 5 curvas. Só-leitura sobre o store `5916d8be0510`. Nada escrito.

## A medição

Tabela 8 do paper ("Specific attenuation of the bolt", p. 18) lida do PDF;
retenção = 1 − atenuação. Round-trip do CSV cru (x = ciclo+1) nas 4 âncoras:

| amp | c1 | c10 | c50 | c100 | estatuto |
|---:|---:|---:|---:|---:|---|
| 0,25 | −0,0123 ⚠️ | −0,0125 ⚠️ | −0,0103 ⚠️ | −0,0092 | **TRIPÉ** |
| 0,50 | +0,1786 ⚠️ | +0,0100 ⚠️ | +0,0118 ⚠️ | −0,0010 | fora |
| 1,00 | +0,1721 ⚠️ | +0,0439 ⚠️ | +0,0207 ⚠️ | −0,0057 | fora (não-comparável) |
| **1,50** | **−0,0032** | **−0,0003** | **+0,0002** | +0,0119 ⚠️ | **TRIPÉ (D-W)** |
| 2,00 | +0,0279 ⚠️ | +0,0792 ⚠️ | −0,0001 | — | **TRIPÉ** |

⚠️ = |Δ| > 0,01 (a barra do G1 do D-W).

## Três leituras

**1. O conserto do D-W se valida DE FORA.** A `amp1p5` é a única que casa a
Tabela 8 nas três âncoras dentro da janela da métrica (−0,0032/−0,0003/+0,0002).
Antes do conserto ela falhava c10/c50 por +0,021/+0,025. Isto é confirmação
independente: o gate não foi desenhado para favorecer o resultado — as outras
quatro, intocadas, continuam reprovando.

**2. O defeito é da FAMÍLIA, não de uma curva.** Quatro das cinco falham em pelo
menos uma âncora dentro da janela. Não é caso isolado de digitalização ruim: é
uma passada inteira com deriva.

**3. Duas das que falham estão NO TRIPÉ — e o rigor vale contra nós.**
`amp2p0` (+0,0792 em c10!) e `amp0p25` (−0,011 sistemático nas três).
Re-digitalizar pode **tirá-las**, exatamente como o D-U tirou a `yang2021_r1`.

## Ressalva de instrumento (não confundir com evidência)

Os **c1 de `amp0p5` e `amp1p0` (+0,178/+0,172) NÃO são evidência de defeito** —
são artefato de interpolação no penhasco: no 1º ciclo a curva despenca ~36 % e
interpolar em x=1 sobre grade esparsa dá erro grande por construção. O
subagente do D-W já havia registrado isso. **O que conta nessas duas é c10/c50**
(amp1p0 +0,0439/+0,0207; amp0p5 +0,0100/+0,0118).

Já a `amp2p0` tem +0,0792 em **c10**, longe do penhasco — essa é evidência.

## Estado de cada uma, e o que a correção implicaria

| curva | evidência | efeito plausível de re-digitalizar |
|---|---|---|
| `amp2p0` | +0,0792 em c10 (forte) | **risco de SAIR do tripé** (−1) |
| `amp0p25` | −0,011 nas 3 (sistemático, pequeno) | risco baixo; offset uniforme quase não move σ |
| `amp0p5` | +0,010/+0,012 em c10/c50 | pode melhorar (está fora a 2,49×) |
| `amp1p0` | +0,044/+0,021 | **não move o censo** (é `_CID_NAO_COMPARAVEL`, duplicata da fig20_T22Nm) — mas é **metade do par do piso de digitalização** da fonte ⇒ corrigi-la muda o PISO |
| `amp1p5` | limpa | já consertada |

## Recomendação (não executada — precisa de extração de pixel das 4)

Prereg único para a família (molde D-W: pixel calibrado nas âncoras da Tabela 8
+ predição por curva + isolamento), com o **saldo declarado ANTES**: pode ser
**negativo** (−1 se a `amp2p0` sair, +1 se a `amp0p5` entrar, `amp0p25`
provavelmente neutra, `amp1p0` fora do censo). Não é campanha de censo — é de
**estar certo**, e o par do piso muda junto.

⚠️ Ordem importa: corrigir a `amp1p0` **muda o piso de digitalização** da fonte
(o par amp1p0↔fig20_T22Nm), que por sua vez entra em `limite_sres` e nas provas
F7 do LU_2024. Fazer as 4 num passo só, com o piso re-medido no mesmo commit.
