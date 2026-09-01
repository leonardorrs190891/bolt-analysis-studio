# Reconciliação: duas sessões mediram a mesma pergunta, sem saber uma da outra

> **2026-07-28.** Store `4f5bedfbace4`. Duas sessões paralelas atacaram a mesma
> pergunta — *"a leitura do nível fecha as 7 LEVEL-LIMITED?"* — no mesmo dia,
> independentemente, e escreveram dois documentos que não se citam:
>
> | doc | o que fez |
> |---|---|
> | [`level_limited_floor_read_2026-07-28.md`](level_limited_floor_read_2026-07-28.md) | pré-teste de **direção**, **sem simular** |
> | [`level_seven_probe.md`](level_seven_probe.md) | pré-teste de direção **+ simulação** de 3 alavancas lidas, com controle negativo bit-a-bit |
>
> Isto é duplicação de esforço — e também, de graça, o cruzamento mais forte que
> esta campanha já teve sobre um leitor de proveniência. Este documento fecha as
> duas medições numa só e resolve as três diferenças.

---

## 1. Os números batem: 19 de 19

Comparando célula a célula (piso **lido**, piso **aplicado**, **res.médio**) das
7 curvas, com tolerância 5e-4:

| curva | lido | aplicado | res.médio | bate |
|---|--:|--:|--:|:--:|
| `chu2026ti_D0p3mm_F0_49kN_test1` | 0,9876 | 0,0800 | −0,0663 | ✅✅✅ |
| `eccles2010_fig8a_no_axial_baseline1` | 0,0122 | 0,0590 | −0,0426 | ✅✅✅ |
| `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | 0,8351 | — | +0,0729 | ✅✅✅ |
| `bauer2024_M12_fig8_test3` | 0,2389 | 0,0800 | +0,0228 | ✅✅✅ |
| `lu2024_M8_fig20_T22Nm` | 0,0626 | 0,2100 | +0,0517 | ✅✅✅ |
| `rousseau2025_hdpe_t12` | 0,3395 | 0,2000 | +0,0572 | ✅✅✅ |
| `liu2016wear_fig7_run2_5e6cyc` | 0,6478 | — | +0,0603 | ✅✅✅ |

**19 de 19 números compartilhados idênticos**, verificado por script contra os
dois JSONs — não a olho. Duas implementações escritas em separado produzem o
mesmo valor de `arrest_floor_from_curve` e a mesma leitura do `config_used`.
Isso é validação independente do leitor **e** do caminho de leitura do store.

---

## 2. As duas medições são complementares, e juntas dizem mais

Uma **previu**, a outra **mediu** — e a previsão acertou tudo:

| | previsão (direção) | medição (simulação) |
|---|---|---|
| `chu…test1` | direção certa | **FECHA** — maxerr 0,1147 → **0,0082** |
| `lu2024_T22Nm` | direção certa | MELHORA, não fecha (0,1248 → 0,1166) |
| `eccles fig8a` | direção errada | **PIORA** (0,1223 → 0,2133) |
| `bauer test3` | direção errada | **PIORA** (0,1198 → 0,3984) |
| `rousseau hdpe_t12` | direção errada | **PIORA** (0,1375 → 0,2123) |
| `liu2020_fig9` | sem piso no cfg | **INERTE** — Δ = 0 exato |
| `liu2016wear` | sem piso no cfg | **INERTE** — Δ = 0 exato (§4) |

**7 de 7.** O pré-teste de direção — duas linhas de aritmética sobre o store —
prevê o desfecho de uma sonda que custa uma simulação por alavanca (a última
delas custou **2960 s**). É a regra que sobra deste par de documentos: *antes de
gastar sonda numa alavanca de nível, conferir (i) que a alavanca está **viva** no
cfg daquele caso e (ii) que o valor lido move a retenção para o lado que o
`res.médio` exige.* O item (i) veio da 7ª curva — ver §4.

---

## 3. As três diferenças, resolvidas

**(a) O veredicto não é "1 de 4" — é "1 fecha de 6, e a direção acerta 6/6".**
O outro documento pôs **3 curvas fora do veredicto** porque o leitor marcou
`plateau=False` (a curva termina em queda ⇒ o valor é *limite inferior* ⇒
comparar **magnitude** é inválido). A cautela está certa quanto à magnitude —
mas a **direção** continua legítima num limite inferior, e as simulações
mostraram que ela acertou nas 3: `bauer` PIORA, `rousseau` PIORA, `lu` MELHORA.
Então o `plateau=False` **não** invalida o pré-teste; invalida só a comparação de
quanto.

**(b) A localização deles é mais precisa que a minha.** Eu escrevi que "o leitor
do piso e a métrica discordam sobre onde a curva acaba". Eles nomearam o caso e
os ciclos: no `lu2024_T22Nm` o platô é lido em **N = 90** enquanto a métrica
termina em **N = 54** — o piso vem de uma região que a métrica **não pontua**.
É a versão útil do mesmo achado.

**(c) A anomalia de eixo que eles acharam NÃO invalida nenhum dos dois
resultados — e a razão precisa ser escrita, porque não é óbvia.**
`load_full_curve` devolve x **sem** aplicar `csv_x_scale` (eccles: segundos →
ciclos ×12,5), o que dá N cru 114 contra N métrica 225 no `fig8a`. Os dois
leitores usados aqui são **independentes de x**:

- `arrest_floor_from_curve` usa **só** `ratio` (`provenance.py:91-103`);
- `emb_depth_from_curve` recebe `cyc` mas o usa **apenas** para gravar
  `prov["early_cycle"]` — o valor sai de `drop = 1 − r[early_index]`
  (`provenance.py:68-76`).

Logo os valores estão certos. Mas qualquer leitor futuro que dependa do eixo
tem de aplicar `(x − offset)·scale` antes — a regra que o `CLAUDE.md` já dá para
consumidores de CSV cru, agora com um leitor de proveniência que a viola em
silêncio.

---

## 4. A predição foi declarada antes, e MEDIDA depois: `INERTE`

O `liu2016wear_fig7_run2_5e6cyc` tem **5.000.000 de ciclos** por passada
(**2960 s** de simulação para controle + 3 alavancas). As duas leituras
divergiam, e os dois palpites foram escritos **antes** de o resultado existir:

| | previu | por quê |
|---|---|---|
| outro doc | **❌** (pioraria) | direção errada: piso lido 0,6478 num caso que precisa reter **menos** |
| este doc | **`INERTE`** | estrutural: o cfg do `liu2016` **não tem chave de pack**, e o piso é inerte sem pack — já medido com Δ = 0 exato no `liu2020` |

**Medido: `INERTE`.** maxerr **0,1035 → 0,1035**, Δ = 0 exato. (A alavanca do
`emb` nessa curva PIORA: 0,1035 → 0,1146.)

Então o ❌ da tabela de direção estava **certo pelo motivo errado** naquela
célula, e a lição é a que estava anotada: **o pré-teste de direção precisa de um
passo anterior — conferir se a alavanca está VIVA antes de conferir a direção
dela.** Sem isso, ele atribui a uma direção errada o que é simplesmente um campo
morto.

### A regra estrutural fecha 7/7 — sem exceção

Com a 7ª curva medida, a separação é perfeita:

| `loose_torsion_mode` no cfg | curvas | desfecho da sonda do piso |
|---|--:|---|
| **ausente** | 2 (`liu2016`, `liu2020`) | **INERTE nas duas**, Δ = 0 exato |
| presente | 5 | FECHA 1 · MELHORA 1 · PIORA 3 — nunca inerte |

O gotcha do `CLAUDE.md` ("`c_bend`/`loose_arrest_floor` INERTES sem pack na
ENTRY") deixa de ser advertência e passa a **fato medido, 2/2 e 5/5**.

### E o preço disso é alto, porque cai na curva mais próxima da meta

O `liu2016wear_fig7_run2_5e6cyc` viola o tripé por **+0,0035** (mae 0,0603,
maxerr 0,1035) — é a **curva mais perto de fechar entre as 55**. Ela é
LEVEL-LIMITED, e a alavanca de nível mais barata é **inerte exatamente nela**.
Fechá-la exige ou ligar o pack (mudança de configuração, não leitura) ou achar a
constante de nível que o piso não é.

### Placar final das 7

| desfecho | n | curvas |
|---|--:|---|
| **FECHA** | 1 | `chu…test1` (0,1147 → 0,0082) |
| MELHORA, não fecha | 1 | `lu2024_T22Nm` (0,1248 → 0,1166) |
| **INERTE** | 2 | `liu2016`, `liu2020` (sem pack) |
| **PIORA** | 3 | `eccles fig8a`, `bauer test3`, `rousseau hdpe_t12` |

---

## 5. O que fica para a fila

1. **A ação prescrita para a classe LEVEL-LIMITED está morta como estava
   escrita** ("ler o `loose_arrest_floor` com procedência — zero física nova").
   As duas medições concordam. O Manual (`docs/MANUAL_BAS_V2/`) carrega essa
   ação na tabela das classes e precisa da mesma correção.
2. **A classificação segue válida.** O resíduo dessas curvas *é* de nível — o
   que caiu foi a alavanca, não o diagnóstico.
3. **Pergunta aberta, agora precisa:** que constante governa o nível quando o
   piso de arresto não é a resposta? Os dois documentos convergem nos mesmos
   candidatos e no mesmo alerta: `emb_depth` é **input** por junta (exige a
   rugosidade do paper), `tr_loose_gain` é **forma compartilhada** (mexer per-rig
   é fit, não leitura), `C_creep` tem precedente de leitura por par. Nenhum
   testado.
4. **Custo de coordenação, registrado:** duas sessões gastaram esforço na mesma
   pergunta. O que salvou o dia foi os dois trabalhos serem **só-leitura** — a
   colisão custou tokens, não integridade. Se as duas tivessem escrito no store
   ou no `adopted_configs.json`, o resultado seria corrupção silenciosa.
