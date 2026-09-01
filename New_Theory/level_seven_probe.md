# As 7 LEVEL-LIMITED — o nível lido do dado fecha, ou não?

> **2026-07-28.** Continuação de `frontier_classes.md`. Store
> `4f5bedfbace4`. **Nenhum fit** (as duas constantes vêm de leitores de
> proveniência L24) e **nenhuma escrita no store** (`simulate_case` não
> grava). Controle negativo bit-a-bit antes de cada sonda: as
> 7 curvas reproduziram o store exatamente.
> Script: `New_Theory/level_seven_probe.py`; números: `.json`.

> **RECLASSIFICAÇÃO POSTERIOR (mesma data, errata 2ª de
> `frontier_classes.md` §6):** o `bauer2024_M12_fig8_test3` **não é mais
> LEVEL-LIMITED** — ele é uma das 3 réplicas do mesmo ensaio do Bauer, e
> passou a **DATA-LIMITED** (scatter irredutível, provado em
> `replicate_impossibility_sweep_2026-07-28.md`). A classe LEVEL tem **6
> curvas**, não 7. As medições abaixo continuam válidas como medições — o
> `bauer test3` sondado PIOROU, e agora se sabe que ele nunca foi candidato
> a nível. Isso **reforça** o resultado negativo: das 6 curvas de nível de
> fato, **1 fecha**.

---

## 1. Resultado — e a correção de uma leitura minha

**Das 7 curvas, ler o nível fecha 1.**
1 melhora sem fechar, 2 é inerte e
**3 PIORAM**.

Isto **corrige** o que eu escrevi ao entregar a varredura das 4 classes
("as 7 de nível são o alvo mais barato da meta, 147 → potencialmente
154"). A classificação está certa — o resíduo *é* de nível, e isso é uma
propriedade medida do resíduo. Mas **as duas constantes de nível que a
campanha sabe LER do dado não são a alavanca** em 5 das 6. O caveat que
acompanhava a classe ("condição necessária, não prova") era o certo, e
agora está medido em vez de suposto.

| curva | maxerr | via piso | via emb | via ambos | veredicto |
|---|--:|--:|--:|--:|---|
| `bauer2024_M12_fig8_test3` | 0.1198 | 0.3984 | 0.1313 | 0.4039 | **PIORA** |
| `chu2026ti_D0p3mm_F0_49kN_test1` | 0.1147 | 0.0082 | 0.1152 | 0.0082 | **FECHA** |
| `eccles2010_fig8a_no_axial_baseline1` | 0.1223 | 0.2133 | 0.2577 | 0.2253 | **PIORA** |
| `liu2016wear_fig7_run2_5e6cyc` | 0.1035 | 0.1035 | 0.1146 | 0.1146 | **INERTE** |
| `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | 0.1339 | 0.1339 | 0.1530 | 0.1530 | **INERTE** |
| `lu2024_M8_fig20_T22Nm` | 0.1248 | 0.1166 | 0.1708 | 0.2316 | **MELHORA, NAO FECHA** |
| `rousseau2025_hdpe_t12` | 0.1375 | 0.2123 | 0.1583 | 0.2296 | **PIORA** |

---

## 2. O motivo: um pré-teste de direção que custa ZERO simulação

`res.médio` = média(modelo − dado). Positivo ⇒ o modelo **retém mais** que
o dado ⇒ precisa de piso **menor**. O piso lido só pode ajudar se andar
para o lado que o resíduo pede.

| curva | res.médio | precisa | piso lido vs cfg | bate? | desfecho |
|---|--:|---|---|:--:|---|
| `bauer2024_M12_fig8_test3` | +0.0228 | piso MENOR | piso MAIOR | ❌ | PIORA |
| `chu2026ti_D0p3mm_F0_49kN_test1` | -0.0663 | piso MAIOR | piso MAIOR | ✅ | FECHA |
| `eccles2010_fig8a_no_axial_baseline` | -0.0426 | piso MAIOR | piso MENOR | ❌ | PIORA |
| `liu2016wear_fig7_run2_5e6cyc` | +0.0603 | piso MENOR | sem piso no cfg (default 0 = sem arresto) | — | INERTE |
| `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | +0.0729 | piso MENOR | sem piso no cfg (default 0 = sem arresto) | — | INERTE |
| `lu2024_M8_fig20_T22Nm` | +0.0517 | piso MENOR | piso MENOR | ✅ | MELHORA, NAO FECHA |
| `rousseau2025_hdpe_t12` | +0.0572 | piso MENOR | piso MAIOR | ❌ | PIORA |

**O pré-teste prevê os 6 desfechos, 6/6** — direção bate ⇒ FECHA ou
MELHORA; não bate ⇒ PIORA; sem piso no cfg ⇒ INERTE. Ou seja: as 6 sondas
eram dispensáveis, o sinal já dizia. **Regra para a campanha:** antes de
gastar sonda numa alavanca de nível, conferir que o valor LIDO move a
retenção para o lado que o `res.médio` exige. Duas linhas de aritmética
sobre o store.

---

## 3. Três achados que sobram do caminho

**(a) O leitor do piso e a métrica discordam sobre onde a curva ACABA.**
`arrest_floor_from_curve` faz a média dos últimos 5% do ratio **cru**;
a métrica pontua só o trecho `>= 0,10` (`FLOOR_TRIM`). No
`eccles fig8a` o piso lido é **0,0122** — o dado cru vai a perda quase
total —, enquanto a visão que a métrica tem da curva termina em 0,10.
Injetar o piso lido faz o modelo colapsar até o fim e o `maxerr` sai de
0,122 para **0,213**. Não é o leitor que está errado nem a métrica: é a
MESMA classe de inconsistência dos achados de `FLOOR_TRIM` de 07-27
(instrumentação e métrica medindo trechos diferentes da mesma curva).

**(b) `loose_arrest_floor` INERTE sem pack — confirmado com Δ = 0 exato.**
O `liu2020_fig9` não tem `loose_torsion_mode` no cfg e a sonda do piso deu
MAE e maxerr **bit-idênticos** ao controle. O gotcha do `CLAUDE.md`
("`c_bend`/`loose_arrest_floor` INERTES sem pack na ENTRY") passa de
advertência a fato medido nesta curva.

**(c) A única que fecha, fecha MUITO — e por isso merece cuidado.**
`chu2026ti_D0p3mm_F0_49kN_test1`: maxerr **0.1147 → 0.0082** com piso lido **0.9876** contra 0.08 do cfg.
Um piso de ~0,99 significa "o afrouxamento trava a 99% de F₀", isto é,
quase nenhum afrouxamento — coerente com esta ser a curva mais RASA da
família (D = 0,3 mm), mas é um input **por caso**, e o CHU é justamente
a fonte de família não-monotônica. Pelo critério G-A3 já escrito
("constante própria por fonte não é forma, é tuner com nome bonito"),
adotar isto exige o gate PR-37′: procedência + nenhum caso pior +
mediana da fonte. **Não adotei nada.**

---

## 4. O que isto muda na fila

1. **A conta "147 → 154 de graça" não existe.** Pelo caminho da leitura,
   o ganho medido é **+1** curva
   (e ela ainda depende do gate de adoção).
2. **As 5 restantes continuam LEVEL-LIMITED** — o resíduo segue de nível —
   **mas o nível não é alcançável pelos leitores existentes.** Isso as
   move de "alvo barato" para uma pergunta nova: *que constante governa o
   nível quando o piso de arresto não é a resposta?*
3. **Candidata que este trabalho NÃO testou:** o `eccles fig8a` e o
   `bauer test3` pedem o nível no sentido oposto ao do platô medido, o que
   sugere que o desvio é de **retenção durante o trecho pontuado**, não de
   patamar final — território de `tr_loose_gain`/`eta_loose`, que são
   FITADOS, não lidos. Ou seja: sairia da doutrina "ler em vez de fitar"
   e viraria prereg, não leitura.

