# O critério de "data-limited por resolução" tem uma LACUNA — e ela já produziu 3 declarações sem premissa

**2026-08-07 (madrugada)** · só-leitura · **nada declarado, nada retratado** —
alteração de camada de declaração é **proposta**, nunca edição sem assinatura.

## Como cheguei aqui

Procurando alvo dentro do mandato, achei que a `YANG_2023_IJPEM 0,2 mm` fosse a
única curva `indecidível` fora do ROUSSEAU e pensei em aplicar-lhe o critério
**assinado** de 2026-08-01 (mediana |Δ(F/F₀)| entre pontos consecutivos ≥
META_MAX = 0,10). O critério é explicitamente **global**, então varri as 205.

**A curva que qualifica não é a do Yang — é a
`karlsen2022_M30_HVtorqued_run14p2`** (mediana **0,1216**, n=7), exatamente a
única sobrevivente da fila form-limited e a curva cuja exceção F7 eu retratei
duas vezes esta noite.

Declará-la fecharia a fila em **zero** — que era a condição de parada original
do loop. É por isso que fui verificar em vez de executar.

## Por que NÃO declarei: o controle da própria fonte refuta o argumento

O critério justifica-se assim: *"entre dois pontos medidos o dado não restringe
a curva a menos do que o passo, então res.máx e σ_res medem o espaçamento da
amostragem, não o modelo."* Isso **exige que o erro seja da ordem do passo**.

| curva (KARLSEN) | passo | res.máx | **mx/passo** | tripé |
|---|---:|---:|---:|---|
| `run7p1` | 0,1603 | 0,0916 | **0,57** | SIM |
| `M42_run20p0` | 0,1515 | 0,0558 | 0,37 | SIM |
| `run2p2` | 0,1503 | 0,0583 | 0,39 | SIM |
| `run6p2` | 0,1470 | 0,0489 | 0,33 | SIM |
| `M42_run21p0` | 0,1131 | 0,0777 | 0,69 | SIM |
| **`run14p2`** | 0,1216 | 0,2363 | **1,94** | não |

**Quatro curvas da mesma fonte têm amostragem MAIS GROSSA e passam**, com erro
em 0,33–0,57 do passo. A `run14p2` erra **1,94× o passo**. ⇒ a amostragem não é
o que a impede; o erro dela é mensurável **apesar** do passo grosso.

E há um argumento independente que não depende de razão nenhuma: o **MAE** dela
é 0,0898 = **1,80×** o limite, e MAE **não** é inflado por passo grosso do jeito
que res.máx é. A perna que a reprova sobrevive inteira ao argumento de
resolução.

## ⛔ ERRATA (mesma madrugada): são **3** declarações sem premissa, não 5

A seção seguinte publicou **5**. O número está **errado** e a causa é de método:
eu testei cada declaração contra **um** critério — o primeiro que casava na
ordem do report. **Uma declaração está justificada se QUALQUER critério assinado
se sustentar.** Refeito em `declaracoes_teste_premissa.py`, testando todos os
aplicáveis por curva:

| curva | critérios aplicáveis | veredicto |
|---|---|---|
| `0,30 mm` | resolução | **FALHA** (mx/passo 1,22) — sem alternativa |
| `0,35 mm` | resolução | **FALHA** (4,00) — sem alternativa |
| `0,50 mm` | n<6 + resolução | **FALHA nos dois** (viola MAE+mx; 1,82) |
| `0,45 mm` | colapso + resolução | **colapso OK** (res.máx a 1 índice do penhasco) |
| `0,55 mm` | n<6 + colapso + resolução | **colapso OK** (a 0 índice) |
| `0,65 mm` | n<6 + resolução | **resolução OK** (mx/passo 0,76) |

⇒ **3 sem cobertura**, e o custo real da emenda P-10 é
**176 → 173**, não 176 → 171.

**Subproduto:** o critério de **colapso** se sustenta em 100 % dos casos onde se
aplica (0,45 · 0,55 · `yang2019_amp0p6_5Hz`, todos com res.máx a 0–1 índice do
maior salto do dado). O `n<6` também: as **3** curvas declaradas sob ele
(`0,15` · `0,18` · `zhang19_fig4`) têm mae/mx passando com folga, exatamente
como a assinatura registrou. **A lacuna é só do critério de resolução.**

## ⚠️ A lacuna, e o que ela já custou

O critério mede **só o passo do dado** e **nunca** o compara ao erro do modelo.
Auditando as **6 declarações já assinadas** sob ele com o mesmo teste:

| curva declarada | passo | res.máx | **mx/passo** |
|---|---:|---:|---:|
| `Yang2023 0,35 mm` | 0,1400 | 0,5600 | **4,00** |
| `Yang2023 0,45 mm` | 0,1600 | 0,3600 | **2,25** |
| `Yang2023 0,50 mm` | 0,2250 | 0,4098 | **1,82** |
| `Yang2023 0,55 mm` | 0,2000 | 0,3426 | **1,71** |
| `Yang2023 0,30 mm` | 0,1800 | 0,2200 | **1,22** |
| `Yang2023 0,65 mm` | 0,2100 | 0,1600 | 0,76 ✓ |

**5 das 6 têm a premissa falhando**, uma delas por **4×**. Elas contam hoje na
leitura publicada *"resolvido ou declarado"*.

## PROPOSTA (P-10) — emenda ao critério, com o custo declarado

Acrescentar ao critério assinado a guarda que falta:

> uma curva é data-limited por resolução quando a mediana |Δdado| ≥ META_MAX
> **E** `res.máx ≤ mediana |Δdado|` — isto é, o erro do modelo não excede o
> passo. Sem a segunda condição o argumento afirma que o erro é invisível
> quando ele é maior que a régua que o esconderia.

**Custo medido, se a emenda for assinada:**

* `run14p2` **não** é declarada (fila form-limited fica em **1**, não em 0);
* **3 declarações do IJPEM são retratadas** (`0,30` · `0,35` · `0,50`) ⇒
  leitura *resolvido-ou-declarado* cai de **176/205** para **173/205**;
* censo estrito **inalterado em 139/205** (declaração nunca contou nele).

**Não executo nada disso.** As 5 foram assinadas por você, e o teste que as
acusa é **novo** — não é medição que mudou, é critério que ganharia condição.
Isso é emenda de política, e o charter reserva-a à sua assinatura.

⚠️ **Registro do meu próprio viés:** eu fui aplicar o critério esperando fechar
a fila em zero, que é o objetivo declarado do loop. Foi a desconfiança com a
conveniência do resultado que me fez testar a premissa — e o mesmo teste voltou
contra 5 números que já estavam publicados a nosso favor.

## Reprodutibilidade

Os três passos estão no scratchpad da sessão e são recomputáveis do store em
segundos: varredura global do critério, controle por fonte (`mx/passo` nas 11
do KARLSEN) e auditoria das declaradas.
