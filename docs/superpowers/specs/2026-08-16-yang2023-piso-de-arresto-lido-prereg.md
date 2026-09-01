# ⛔ PREREG MORTO — PREMISSA FALSIFICADA em 2026-08-16 (13:5x), ~1 h depois de congelado

> ⚠️ **NÃO EXECUTE ESTE PREREG.** Os gates da §4 seguem **intocados** (gate congelado é
> imutável — a retratação se anexa, não se edita). O que caiu foi a **premissa** da §1.
>
> **A afirmação morta** é esta, da §1: *"o dado **arresta** em 0,12–0,22 — seis curvas
> concordantes, média **0,165**. Não é dispersão: é platô."*
>
> **A coluna "fim do dado" daquela tabela é o último valor de `metric_data`**, isto é, o
> dado **DEPOIS do `FLOOR_TRIM` = 0,10**. Por construção o mínimo daquele vetor é ≥ 0,10.
> O "platô em 0,165" é o piso da **janela da métrica**, não do dado. Retratação integral:
> `New_Theory/yang2023_piso_nunca_lido.md`; gotcha no `CLAUDE.md`.
>
> **E o leitor canônico já dizia isso.** `floor_from_curve` (= `arrest_floor_from_curve`)
> sobre o CSV **cru**, nas 9 curvas da fonte:
>
> | δ (mm) | floor lido | fim do **cru** | `plateau` |
> |---:|---:|---:|:--:|
> | 0,15 | 0,9325 | 0,9250 | ✅ True |
> | 0,18 | 0,9350 | 0,9300 | ✅ True |
> | 0,25 | 0,5800 | 0,5200 | ❌ **False** |
> | 0,30 | 0,1400 | **0,0600** | ❌ **False** |
> | 0,35 | 0,1000 | **0,0500** | ❌ **False** |
> | 0,45 | 0,1050 | **0,0500** | ❌ **False** |
> | 0,50 | 0,0700 | **0,0200** | ❌ **False** |
> | 0,55 | 0,1150 | **0,0500** | ❌ **False** |
> | 0,65 | 0,0950 | **0,0300** | ❌ **False** |
>
> ⇒ **TODAS as 7 curvas que afrouxam devolvem `plateau=False`** — o helper canônico
> literalmente **se recusa** a chamar aquilo de platô, e rotularia qualquer valor lido
> ali como *"LIMITE INFERIOR — curva termina em queda"*. As duas únicas com
> `plateau=True` são as **abaixo do limiar**, que não afrouxam (piso 0,93). O dado não
> arresta: colapsa a **0,02–0,06**.
>
> ⇒ `loose_arrest_floor = 0,0` (o default do engine, que a §1 chamava de defeito) está
> **CERTO** para esta fonte. **Não há input não lido.** A §2 (*"a rota é leitura de
> input, não fit"*) fica sem objeto: o leitor devolve `plateau=False`, ou seja, **não há
> o que ler**.
>
> ⚠️ **A lição de método, e ela vale além desta fonte:** a auto-guarda `plateau` **já
> existia e teria matado esta proposta em 1 comando**. Eu não a consultei porque não usei
> o leitor — olhei `metric_data` a olho nu. A mesma guarda, aplicada aos 33 pisos
> adotados, encontrou o defeito espelhado no `ECCLES_2010_fig7d`
> (`New_Theory/eccles_piso_nao_sustentado_pelo_dado.md`, item **R** da mesa): lá um piso
> de 0,137 foi **gravado** como *"assíntota final crua"* sobre uma curva que colapsa a
> zero, porque a flag foi descartada entre ler e adotar. **Mesma flag, duas direções.**
>
> **Estado:** nada foi executado deste prereg. Censo **144/205** inalterado; store
> `20be19aabe11` intocado.

---

# PREREG — LER o piso de arresto do `YANG_2023_IJPEM` (input não lido, não constante fitada)

**2026-08-16 (tarde)** · **gates congelados neste commit** · store
`20be19aabe11`, censo 144/205. Origem do achado: sessão A (`a5d35d7`, `e04a312`)
mediu que a fonte roda com `loose_arrest_floor` no **default do engine** e
deixou a adoção como **proposta não executada** ("adoção de config exige
assinatura"). Conferido por mim em 2026-08-16: os **3** grupos adotados
(`YANG_2023_IJPEM`, `_m6`, `_m8`) seguem sem declarar o campo.

## 1. O defeito

`loose_arrest_floor` ausente ⇒ **0,0** ⇒ o `self_locking_gate` devolve 1,0 e o
canal rotacional vira **runaway puro**: bifurcação arrest/zero **sem
meio-termo**, como o `CLAUDE.md` já documenta. Medido no store:

| δ (mm) | MAE | res.máx | σ_res | fim do dado | **fim do modelo** | estatuto |
|---:|---:|---:|---:|---:|---:|---|
| 0,15 | 0,0093 | 0,0241 | n<6 | 0,925 | 0,949 | declarada |
| 0,18 | 0,0076 | 0,0156 | n<6 | 0,930 | 0,946 | declarada |
| 0,25 | 0,1664 | 0,4256 | 0,1452 | 0,520 | **0,946** | exceção |
| 0,30 | 0,1200 | 0,2200 | 0,1312 | 0,220 | **0,000** | **ABERTA** |
| 0,35 | 0,1788 | 0,5600 | 0,2118 | 0,150 | **0,000** | **ABERTA** |
| 0,45 | 0,1042 | 0,3600 | 0,1344 | 0,160 | **0,000** | declarada |
| 0,50 | 0,2386 | 0,4098 | n<6 | 0,120 | **0,367** | **ABERTA** |
| 0,55 | 0,1192 | 0,3426 | n<6 | 0,180 | **0,000** | declarada |
| 0,65 | 0,0822 | 0,1600 | n<6 | 0,160 | **0,000** | declarada |

**As 9 estão fora do tripé.** O modelo termina em **0,000 exato** em cinco
delas, enquanto o dado **arresta** em 0,12–0,22 — seis curvas concordantes,
média **0,165**. Não é dispersão: é platô.

## 2. A rota é LEITURA DE INPUT, não fit

`calibration/provenance.py::floor_from_curve` já existe e lê o piso do platô
final da própria curva de referência (disciplina L24, "ler em vez de fitar").
**Nenhum número novo é inventado**: o valor vem do dado que já está no repo.

**Valor a adotar: um só, por fonte**, lido dos platôs. A escolha entre
"um por fonte" e "um por curva" está decidida **antes** de medir: **por fonte**,
porque um por curva seria fit disfarçado de leitura (item D da doutrina), e
porque os seis platôs concordam dentro de ±0,05.

## 3. ⚠️ O baseline já mostra que isto NÃO é ganho garantido

O gate é `g = max(0, 1 − floor·F₀_init/F_0)`: ele **só reduz** a taxa de
afrouxamento. Logo ele **ajuda** quem colapsa demais e **piora** quem já retém
demais. Nas 9 curvas há dos dois:

| classe | curvas | efeito esperado |
|---|---|---|
| modelo vai a **0,000**, dado arresta em 0,12–0,22 | 0,30 · 0,35 · 0,45 · 0,55 · 0,65 | **melhora forte** |
| modelo **retém demais** (0,367 contra 0,120) | **0,50** | **piora** — o gate o freia ainda mais |
| modelo quase não afrouxa (0,946 contra 0,520) | **0,25** | **piora** (fator ≈0,83 na taxa) |
| modelo já ótimo (MAE 0,008–0,009) | 0,15 · 0,18 | piora leve; são as mais frágeis |

⇒ **o resultado é genuinamente incerto**, e é por isso que isto é prereg e não
"executar direto". Se eu tivesse olhado só as cinco que melhoram, teria proposto
uma adoção que quebra as duas melhores curvas da fonte.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G0** | **procedência** | o valor adotado é **LIDO** por `floor_from_curve` dos platôs das curvas da própria fonte, e o número lido é registrado no `prov`. **Proibido** ajustá-lo depois de ver a métrica — se o lido não servir, o veredito é falsificação, não busca |
| **G1** | **alvo** | pelo menos **2 das 3 ABERTAS** (0,30 · 0,35 · 0,50) fecham o tripé |
| **G2** | **controle — as boas não podem quebrar** | `0,15 mm` e `0,18 mm` não pioram mais que **+0,010** de MAE (hoje 0,0093 e 0,0076) |
| **G3** | **controle da fonte** | a soma dos MAE das 9 **melhora**; nenhuma curva piora mais que **+0,05** de MAE |
| **G4** | **isolamento** | Δ = **0,0000 exato** em toda curva fora do `YANG_2023_IJPEM` |
| **G5** | **um número, por fonte** | um único `loose_arrest_floor` nos 3 grupos. Valor por curva = **reprovado por construção** |
| **G6** | **catraca de estatuto** | se alguma declarada/exceção passar a fechar **por mérito**, a assinatura é **retirada** com prova preservada (precedente K6) — e se alguma parar de fechar, isso conta como piora no G3 |
| **G7** | **re-stamp íntegro** | adoção muda o `engine_fingerprint`: re-simular os **210** e conferir fingerprint **único** no store antes de publicar qualquer número |
| **G8** | **falsificação honesta** | se G1 falhar, ou se G2/G3 forem violados, declarar **FALSIFICADO** com número. A fonte volta à fila com a rota de piso **fechada** |

## 5. Predição registrada

1. **As cinco que vão a 0,000 melhoram forte** — o terminal sai de 0,000 para
   ≈0,16 contra dado 0,12–0,22.
2. ⚠️ **A `0,50 mm` PIORA.** O modelo já retém 3× demais lá (0,367 vs 0,120) e o
   gate só sabe frear. Se ela melhorar, procurar erro de instrumento.
3. ⚠️ **A `0,25 mm` piora** (exceção assinada; o gate a freia em ≈17 %).
4. **`0,15`/`0,18` pioram pouco** — a questão é se cabem nos +0,010 do G2.
5. **Censo:** as `0,50`, `0,55`, `0,65`, `0,15`, `0,18` têm **n < 6** ⇒ σ_res
   não-julgável ⇒ **não podem entrar no tripé** de qualquer modo. O ganho
   possível de censo está em **0,25 · 0,30 · 0,35 · 0,45** — no máximo **+4**.
   Dizer "+7" seria auto-engano, e eu quase disse.

## 6. O que este passo NÃO é

Não é a mesma coisa que o piso do `LU_2024`, fechado hoje de manhã. Lá o piso
**existe** (0,10) e é uma fração única servindo terminais de 0,006 a 0,309 —
sem lei possível, porque o dado é **não-monótono**. Aqui ele **nunca foi lido**,
e o dado oferece um platô **concordante** em seis curvas. Um é forma faltante; o
outro é input não lido. Só o segundo tem rota.
