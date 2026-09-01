# Item **R** rota **R2** — ADOTADO: o piso do `ECCLES` para de se dizer lido do dado

**2026-08-16 (17:2x)** · prereg `1f1a16d` (gates congelados) · assinatura do professor às
16:37 (*"assine tudo e continue"*) · fingerprint **`20be19aabe11` → `7a60cacb72de`**
(210 uniforme) · censo **144/205 INALTERADO**.

---

## 1. O que mudou: dois campos de texto, zero números

| grupo | `cfg.loose_arrest_floor` | `prov.loose_arrest_floor` |
|---|---:|---|
| `ECCLES_2010_fig7d` | **0,137 — intocado** | `lido-do-dado (assintota final crua…)` → **`proxy-de-desaceleracao-de-cauda (fitado-this-rig…)`** |
| `ECCLES_2010_fig8a` | **0,059 — intocado** | idem |

Diff de **exatamente 2 linhas**. Os outros **6** grupos do `ECCLES` mantêm o rótulo antigo
(conferido por releitura, não por "não deu erro").

## 2. Por que R2 e não R1 — a medição inverteu a minha própria recomendação

A proposta de 13:4x recomendava **R1** (corrigir os números para a leitura L24 do cru).
O **relógio**, medido às 14:5x, disse outra coisa:

| nível | dado cru | modelo (piso 0) | razão |
|---:|---:|---:|---:|
| 0,60 | 64 | 65 | **1,01×** |
| 0,40 | 100 | 96 | 0,96× |
| 0,25 | 153 | 114 | 0,75× |
| **0,10** | **1643** | **130** | **0,08×** |

⇒ **não é erro de nível.** O modelo bate o dado **ao dígito** até 0,40 e só dispara na
cauda: o dado leva **1643** ciclos de 0,25 a 0,10 e o modelo leva **16**.

`loose_arrest_floor` é a **única alavanca anti-runaway** do engine (`self_locking_gate`),
então quem adotou a usou para **imitar essa desaceleração** — tendo de inflá-la acima da
assíntota verdadeira para morder a tempo.

⇒ **o número faz trabalho físico real; o rótulo é que mentia.** R1 teria corrigido a
procedência e deixado as 2 curvas **piores e sem alavanca** (MAE 0,0665→0,1641 e
0,0489→0,0945). R2 preserva a física e conserta a afirmação, que era o defeito.

## 3. GATES — **6 de 6**

| # | gate | resultado |
|---|---|---|
| **G1** | censo intacto | ✅ **144/205**, fora 61, abertas 21, `form_limited` 1 — idêntico |
| **G2** | métricas bit-idênticas nas 2 tocadas | ✅ **Δ = 0,00e+00** em `mae`/`maxerr`/`resid_std` |
| **G3** | isolamento nas outras 208 | ✅ **0** curvas com métrica alterada (medido contra `git show HEAD:` do store) |
| **G4** | fingerprint uniforme | ✅ **210 registros, 1 fingerprint** (`7a60cacb72de`) |
| **G5** | suíte completa | ✅ sem falha nova |
| **G6** | o rótulo não mente | ✅ nega ser leitura do dado, traz os L24 reais (0,0000 · 0,0122), declara escopo de sub-população |

## 4. Predições registradas — 4 de 4

1. **fingerprint muda** ✅ `20be19aabe11` → `7a60cacb72de`. ⚠️ Se **não** tivesse mudado, o
   ramo seria `INCONCLUSIVO` e a doutrina do `CLAUDE.md` (*"o hash cobre a entry inteira,
   incluindo `prov`/`verdict`"*) estaria **errada**. Está certa.
2. **zero curvas mudam métrica** ✅ 0 de 210.
3. **censo permanece 144/205** ✅.
4. **as 2 seguem fora do tripé** ✅ (`fig7d` MAE 1,33× · `fig8a` res.máx 1,32×) — R2 **não
   compra censo**, e não devia.

## 5. Duas armadilhas atravessadas, as duas já documentadas

**(a) O rótulo era compartilhado por 8 grupos.** Substituição ingênua teria mudado os 8.
Escopei aos 2 e **reli o arquivo comparando com o que eu quis escrever** — o gotcha do
`CLAUDE.md` sobre config editado por duas sessões. Para o diff sair mínimo, descobri a
formatação exata por round-trip byte-a-byte (`indent=1, ensure_ascii=False`, LF, `\n`
final), em vez de reformatar 167 kB.

**(b) O batch cobre 209, o corpus tem 210.** O `exemplo_m12_sintetico` fica fora do
universo do `parallel_batch` — e o `CLAUDE.md` avisa que `--cases exemplo_m12_sintetico`
**não conserta** (seleciona nada). Re-sim direta + carimbo manual, single-writer; métricas
bit-idênticas (0,010005 / 0,016808 antes e depois). Sem isso o G4 reprovaria por **1**
registro.

## 6. O que este passo NÃO fez

Não mudou constante, não mudou forma, não reclassificou camada, não moveu o censo. Corrigiu
uma **afirmação de procedência** que a medição contradizia.

A forma faltante que a medição nomeou — **desaceleração de cauda no canal rotacional** —
fica registrada como **candidata de escopo limitado**: medida em **5 curvas de 3 fontes**,
com o `KARLSEN_2022` (7 curvas) como **controle negativo** que impede chamá-la de classe
(`relogio_de_cauda_e_subpopulacao.md`). Propô-la como forma de engine exige assinatura
própria.

## Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/parallel_batch.py --workers 6 --store   # 209, 1620 s
# + re-sim direta do exemplo_m12_sintetico (fora do batch) com carimbo manual
PYTHONPATH=src py -3.12 New_Theory/regra_de_parada_triagem.py
py -3.12 -m pytest tests/ -q
```
