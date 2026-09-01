# A grade completa achou uma célula de **UM número** — proposta de refino sobre a D-AD já adotada

**2026-08-15 (tarde)** · **nada escrito em config** · store **`20be19aabe11`**, censo
**143/205**.

---

## 1. O que aconteceu

Nesta sessão eu (a) refutei o item N pelo controle, (b) nomeei o defeito do `LIU_2025` como
**inclinação em amplitude** (`ρ = +1,000` exato) e (c) escrevi o prereg
`2026-08-15-liu2025-gate-amplitude` (`990b9dd`, gates congelados).

**A sessão paralela executou esse prereg** (`42568f4`, 12:41) e adotou
`dref = 3e-4 m (0,30 mm)` + `p = 4,0`, floor 0 — **censo 141 → 143**, `amp0p25` e `amp0p3`
fechando. O resultado que eu perseguia foi entregue; isto aqui é **refino**, não disputa.

## 2. O achado: existe célula de 1 número, e ela passa tudo

Rodei a grade declarada **inteira** (60 células) mais **27 de extensão D-L em dois eixos**
(o `p` saturou no topo; depois o `dref` saturou embaixo). Isso cobriu `p = 8,0`, que a grade
declarada não alcançava.

⚠️ **`p = 8,0` e `floor = 0,0` são os DEFAULTS do engine** (`s1_amp_gate_p: float = 8.0`).
Pela regra de parcimônia **do próprio prereg** — *"vence a célula com menos números diferentes
do default"* — uma célula em `p = 8` custa **1 número** (só `dref`), contra **2** de qualquer
célula com `p ≠ 8`.

| célula | nºs ≠ default | pior ΔMAE | fecham | saem | ρ | slope |
|---|---:|---:|---:|---:|---:|---:|
| **`dref 0,35 · p 8,0 · floor 0`** | **1** | **+0,0000** | 2 | 0 | **0,54** | **0,0855** |
| `dref 0,30 · p 8,0 · floor 0` | **1** | +0,0000 | 2 | 0 | 0,77 | 0,1034 |
| `dref 0,30 · p 4,0 · floor 0` **(ADOTADA)** | 2 | zero pioras | 2 | 0 | 0,909¹ | 0,107¹ |

¹ números da procedência da D-AD; a minha linha de base de `ρ` é 1,000 e a delas 0,989 — a
diferença é de composição do conjunto, não de resultado.

⇒ **as duas células de 1 número passam G1–G7** e a melhor delas achata **mais** que a adotada
(slope 0,0855 contra 0,107) com **metade dos números**.

## 3. Como a região ficou interior (as duas extensões D-L)

| passo | eixo saturado | o que a extensão achou |
|---|---|---|
| grade declarada (60) | `p` no topo (3,0) — **as 2 sobreviventes lá** | `p` 4→8 melhora a pior piora de **+0,0083 → +0,0000** |
| 1ª extensão (24) | `dref` embaixo (0,35) | `dref` 0,30 também passa; 0,25 e 0,20 **não** (fecham 1 e 0) |
| 2ª extensão (3) | — | região **INTERIOR** `{0,30 · 0,35}`, cercada por reprovação nos dois lados |

Sem as extensões eu teria adotado a célula de fronteira `p = 3,0` (pior piora +0,0083) — **83×
pior** na perna que o G2 mede, e com um número a mais.

## 4. Desempate entre as duas de 1 número

A regra de parcimônia **empata** (1 e 1). Desempatei pela quantidade que o **G5** mede — o
achatamento, que é o objetivo declarado da adoção —, **não** por MAE: `dref 0,35` dá
ρ 0,54 / slope 0,0855 contra 0,77 / 0,1034.

## 5. ⚠️ O que NÃO estou fazendo, e por quê

**Não escrevo em `adopted_configs.json`.** A adoção é de hoje, de outra sessão, e a regra do
projeto é **um escritor por recurso, adoção em série**. Isto vai para a mesa como proposta de
refino: trocar `{dref 0,30 ; p 4,0}` por `{dref 0,35}`, mantendo `p` e `floor` nos defaults.

**Custo/benefício honesto:** o censo **não muda** (as mesmas 2 curvas fecham nas duas). O ganho
é **parcimônia** (2 números → 1) e achatamento (slope 0,107 → 0,0855). Numa campanha cujo
padrão de qualidade é *"3 números fitados no dataset inteiro"*, remover um número fitado
**sem âncora** de uma fonte tem valor próprio — mas é decisão de coordenação, não de medição.

## 6. ⚠️ Erro meu no caminho — e o modo como ele quase passou

Comecei a escrever a adoção **sem re-checar o `git log`** desde o meu último commit, e inseri
`s1_amp_gate_dref` no **topo** do `cfg` dos 3 grupos, onde a sessão paralela já o tinha escrito
no **fim**. Resultado: **chave duplicada no mesmo objeto JSON**, onde **a última vence** —
o meu `0,00035` foi **descartado em silêncio** e o arquivo seguia sintaticamente válido.

O que denunciou foi a asserção de verificação pós-escrita: imprimi o valor lido de volta e
veio **`0.0003`**, não `0.00035`. Sem essa leitura-de-volta eu teria commitado um arquivo com
chave duplicada acreditando ter mudado a constante.

**Duas regras que isto reforça:**
1. **`json.loads` não reclama de chave duplicada** — nem `json.dumps` depois. Um arquivo com
   chave repetida atravessa validação de sintaxe, `assert` de unicidade de *âncora de texto*
   e até `git diff` de olho humano.
2. **`git log` imediatamente antes de escrever**, não só no início do ciclo. Entre o meu
   `990b9dd` (11:0x) e a minha tentativa de escrita passaram ~2 h de grade — tempo em que a
   outra sessão leu o meu prereg, mediu e adotou.

Revertido do backup; `git status` do arquivo **vazio** contra o HEAD.

## 7. ⚠️ O meu G5 está mal desenhado — e o defeito é aritmético, não de gosto

O G5 que congelei exige que **`|ρ|` e `|slope|` diminuam**. A cláusula do `slope` está certa.
A do `ρ` **não mede o que eu quis medir**:

`ρ` de Spearman com n = 6 é **quantizado**, e vale **1,0000 para qualquer sequência
estritamente crescente**. Os valores possíveis abaixo de 1 são 0,9429 · 0,8857 · 0,8286 …,
e **0,9429 = exatamente uma troca de pares adjacentes** (`ρ = 1 − 6·Σd²/210`, Σd² = 2).

⇒ exigir que `|ρ|` caia é exigir que a **ordem se quebre**. É critério de **embaralhamento**,
não de **achatamento**: um gate que corta o slope pela metade preservando a monotonicidade
mantém `ρ = 1,0000` exato e **reprova**.

**Medido na grade:** 5 células passaram G2+G3+G4+G6 e travaram **só** na cláusula do `ρ` —
entre elas `dref 0,30 · p 3,0 · floor 0,20`, com pior piora de **+0,0037**. O gate barrou
células boas por uma propriedade que não é a que ele diz medir.

⚠️ **Não retrofitei o gate.** Ele estava congelado antes da primeira medição, e o precedente
**D-AA** é explícito (*"regra e gate discordaram e o gate congelado mandou"*). O conserto é
para um prereg **futuro**: a cláusula deve ser **só o `slope`** (e, se quiser um segundo
sinal, o `R²` da regressão, que cai quando o padrão deixa de ser linear — `ρ` de rank não
serve). Registrado aqui para que a próxima versão não repita.

## 8. E a minha lista de ramos tinha uma lacuna

Declarei três ramos: `ADOTA` · `FALSIFICADO` (*nenhuma célula passa G2/G3/G4*) ·
`INCONCLUSIVO`. A grade produziu células que **passam G2/G3/G4 e falham no G5** — que não é
nenhum dos três. A ação continua determinada (gates são conjuntivos ⇒ não adota), mas o
**rótulo faltava**, e é a mesma classe do ramo `INCONCLUSIVO` que faltou 2× em 2026-07-30.

⇒ **regra para os próximos preregs:** a lista de ramos tem de cobrir *falha em cada gate
isoladamente*, não só o veredito agregado.

## Reprodutibilidade

`grade_gate_amplitude.py` (60), `grade_gate_ext.py` (24), `grade_gate_ext2.py` (3), no
scratchpad, com os JSONs. Todos embrulham `rn._effective_overrides` por fonte e leem os
limites de `rh.limite_sres`. Gates aplicados exatamente como congelados em `990b9dd`.
