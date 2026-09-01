# A **P-8 opção 1 está OBSOLETA** — e o script que a mediria pareava protocolos errados

**2026-08-16 (15:5x)** · só-leitura sobre CSV + 1 conserto de **script de sonda** ·
**nada adotado, nada reclassificado** · store `20be19aabe11`, censo **144/205**, fora 61,
abertas 21, `form_limited` 1.

---

## 1. Por que reabri isto: §4.43 aplicado a uma pendência

`New_Theory/lu2024_fig18_familia_tab8.md` (2026-08-06) media a família fig18 contra a
**Tabela 8** do paper e concluía: *"o defeito é da FAMÍLIA — 4 das 5 falham em pelo menos
uma âncora"*, com a `amp2p0` a **+0,0792** em c10 e risco declarado de **sair do tripé** se
re-digitalizada. Virou a **P-8 opção 1**, pendente *"exige prereg próprio do re-fit"*.

⚠️ Aquilo foi medido contra o store **`5916d8be0510`**. Desde então **as CSVs do `LU_2024`
foram corrigidas** (pico espúrio, 2026-08-16, dado-only). §4.43: *pendência registrada
carrega o fingerprint contra o qual foi medida, e vira suspeita quando ele muda*. Re-medir
custa um comando — é round-trip CSV↔impresso, **sem simular**.

## 2. Re-medido hoje: **a família fig18 está LIMPA**

| curva | c10 em 2026-08-06 | **c10 hoje** | pior hoje |
|---|---:|---:|---:|
| `amp2p0` | **+0,0792** ⚠️ | **+0,0031** | 0,0031 ✅ |
| `amp1p0` | +0,0439 ⚠️ | **+0,0036** | 0,0036 ✅ |
| `amp0p5` | +0,0100 ⚠️ | **+0,0023** | 0,0023 ✅ |
| `amp1p5` | −0,0003 | −0,0003 | 0,0032 ✅ |
| `amp0p25` | −0,0125 ⚠️ | −0,0125 | 0,0125 ~ |

⇒ **4 das 5 passaram a casar a Tabela 8 dentro da barra de 0,01**, e a que mais preocupava
(`amp2p0`, a "evidência forte") caiu de **+0,0792 para +0,0031** — fator **25**.

⇒ **a P-8 opção 1 não tem mais objeto.** O trabalho que ela pediria já foi feito, e não por
ela: a **correção do pico espúrio** de hoje mexeu exatamente nestas curvas. Sobra a
`amp0p25` com −0,0125 sistemático nas três âncoras — offset uniforme pequeno, que quase não
move σ (a própria doc de 08-06 já previa "risco baixo").

## 3. ⛔ O script pareava PROTOCOLOS DIFERENTES — e nomeava as vítimas como as piores

Rodando `New_Theory/lu2024_csv_vs_tabelas.py` apareceram três linhas catastróficas:

```
lu2024_M8_fig14_amp0p25_long   +0.1827
lu2024_M8_fig14_amp0p5_long    +0.5187
lu2024_M8_fig14_amp1p0_long    +0.8370   <- "pior" do relatório
```

**Não é defeito de digitalização. É comparação inválida.** O matcher era:

```python
for k, v in list(TAB8.items()) + list(TAB9.items()):
    tok = f"_{k}" if k.startswith("T") else f"amp{k}"
    if tok in cid:          # <-- casa SO' pelo token de amplitude
```

⇒ `lu2024_M8_fig14_amp0p25_long` contém `amp0p25` ⇒ recebia a **TAB8**, que é a tabela da
**Fig. 18**.

⚠️ E isso é **exatamente o pareamento que a RETRATAÇÃO de 2026-08-14 invalidou**: a `fig14`
roda o **§3.1.3** (half-sine de máquina a 1 Hz) e a `fig18`/`fig20` rodam o **§3.2**
(manual) — dito pelo **texto do próprio paper**. Aquela retratação custou **5 exceções F7**
e tirou uma curva do tripé (147→146). A doutrina foi corrigida; **o script não**.

**Gravidade prática:** a linha `piores:` do relatório listava as três `fig14` no topo ⇒ o
próximo leitor sairia caçando um defeito de digitalização **que não existe**, numa
comparação que não tem direito de ser feita. É a mesma família dos gotchas de matcher por
substring que este repositório já paga caro (empate `YANG_2019`, token `delta_amp_mm`).

### 3a. Conserto

Guarda de figura: `TAB8` só se aplica a cid com `fig18`, `TAB9` só a `fig20`; o resto entra
numa lista **`sem_tabela`** que é **impressa explicitamente**, com o motivo. Ausência tem de
ser visível — curva que sai da conferência em silêncio parece *"conferida e OK"* para quem
lê só as linhas impressas (mesmo defeito das barras por fonte que sumiam quando valiam zero).

## 4. O que o conserto REVELOU

Com as 3 linhas inválidas fora, o pior **real** aparece — e estava mascarado:

| curva | pior |Δ| | onde | estatuto |
|---|---:|---|---|
| `fig20_T4Nm` | **0,0557** | c50 | **declarada** (escopo — o paper diz *"does not reach the tightening effect"*) |
| `fig18_amp0p25` | 0,0125 | c10 | tripé |
| `fig20_T22Nm` | 0,0040 | c10 | tripé |
| demais 7 | ≤ 0,0036 | | |

⇒ **10 das 13 curvas do `LU_2024` conferem contra o impresso a ≤0,004.** O único desvio
grande é numa curva **já declarada fora de escopo**, então não há consequência de censo.

## 5. O que NÃO fiz

Não re-digitalizei, não adotei, não reclassifiquei camada, não mexi em config. O conserto é
num **script de sonda** — não é estatuto, não é engine, não é config adotada. A `amp0p25`
com −0,0125 fica registrada como resíduo conhecido, **abaixo** da barra que justificaria um
prereg de re-digitalização.

## Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/lu2024_csv_vs_tabelas.py
```

Compara `load_full_curve` (CSV **cru**) contra `TAB8`/`TAB9` transcritas do PDF, por
interpolação nas âncoras c1/c10/c50/c100.
