# As **cinco camadas de estatuto**, auditadas curva a curva — visão consolidada

**2026-08-15 (manhã)** · só-leitura · **nada reclassificado** · store `85e8104420b0`,
censo **141/205**, fora **64**.

Consolida seis auditorias feitas nesta sessão. A campanha nunca teve uma visão única de
**quão verificável é cada camada** e **o que a verificação encontrou**.

---

## 1. O quadro

| camada | curvas | afirmações **conferíveis por máquina** | resultado da auditoria |
|---|---:|---:|---|
| `excecao_assinada` | **22** | **2** (9 %) | ⛔ **as 2 conferíveis FALHARAM** — repousam num piso que a P-15 já declarou inválido (6ª ocorrência) |
| `declarada` | **18** | **7** (39 %) | ✅ **7 de 7 conferem** — `n=4`/`n=5` exatos, mediana 0,2100 em 4 casas |
| `classe_parada` | **8** | 8 (via discriminante ρ/razão) | ⛔ **3 sem a assinatura da classe**; 2 com ela **invertida**; **1 tem rota e fecha** |
| `indecidivel_sem_piso` | **15** | 15 (via busca de réplica) | ✅ **15 de 15 legítimas** — nenhuma fonte repete a condição |
| `metric_limited_colapso` | **1** | 1 | ✅ confere (`max|Δdado|` = 0,264 > 0,25) |

Somam **64** = as fora do tripé.

## 2. ⚠️ O número que mais incomoda

Nas exceções, **as duas únicas provas conferíveis foram as duas que falharam**.

Isso não prova que as outras 20 estejam erradas — mas destrói a leitura oposta. Com 2 de 2
falhando na amostra verificável, o correto é tratar as 20 restantes como **não verificadas**,
não como corretas. E elas não são verificáveis por construção: dizem *"prova em lei
(5 degraus)"*, *"scatter de réplicas (desvio-à-mediana 0,349)"*, *"sobreposição axial"* —
afirmações legítimas, mas sem forma que a máquina confira.

⇒ **a camada com o pior histórico (6 retratações) é a menos verificável.**

## 3. O contraste que sugere o conserto

As **declaradas** são 4× mais verificáveis (39 % × 9 %) e conferem **100 %**. A diferença não
é rigor de quem escreveu — é **forma**: a declaração diz *"n=4 < 6"* ou *"mediana = 0,2100"*,
que a máquina recomputa; a exceção diz *"prova de piso (FORTE): res.máx 0,122/0,257"* só em
**2** casos, e prosa nos outros 20.

⇒ **candidato de guarda (não executado, exige assinatura):** exigir que toda exceção
NOVA registre, além da prosa, o **trio `(perna, valor, piso)`** que a sustenta — no idioma
que 2 delas já usam. Não reescreve as antigas; impede que a próxima entre inauditável.

## 4. O que a auditoria mudou na fila

Nada, ainda — as três consequências dependem de assinatura:

| item | consequência medida |
|---|---|
| **N** | 3 curvas mal rotuladas; **1 fecha** com meia constante ⇒ fila 0 → 2, censo 141 → **142** |
| **O** | 2 exceções sobre piso inválido ⇒ `declarado_total` 181 → **179**, censo inalterado; e o `ECCLES` **recupera piso** (4 réplicas `no_axial`) |

## 5. ⚠️ O que aprendi sobre as minhas próprias sondas

**Três** das seis auditorias precisaram de um segundo teste porque a sonda não separava
**ausência de sinal** de **ausência de instrumento**:

1. tupla de condição cega a graxa/crimp → marcou fatorial 2×2 como réplica;
2. veredito por diferença-de-conjuntos → um outlier fez o conjunto diferir;
3. `curvas → chaves de config` → confundiu "chave não vê" com "não há o que ver"
   (`BAUER`: `rep1..rep6` **são** réplicas).

Nas três o discriminante custou **uma leitura** — a nota de aparato ou o nome da curva. É a
mesma classe de erro que a auditoria estava procurando nas camadas, cometida pela ferramenta
que a procurava.

## Reprodutibilidade

`audit_classe_parada.py` · `audit_indecidiveis.py` · `audit_excecoes.py` ·
`audit_excecoes2.py` · `audit_declaradas.py` · `probe_classe_parada_3.py`, todos no
scratchpad e todos só-leitura. Cada um usa o classificador **canônico** (`T.classificar`)
para achar os membros da sua camada — nenhum reimplementa a regra.
