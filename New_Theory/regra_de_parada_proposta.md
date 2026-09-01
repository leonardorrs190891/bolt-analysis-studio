# Regra de parada da campanha — ✅ ASSINADA (por delegação, 2026-07-30)

> ## Assinatura e atualização à régua D1
>
> **Assinada por delegação em 2026-07-30** (mandato do professor em sessão:
> *"fique à vontade para tomar quaisquer decisões que achar prudente"*), com as
> três decisões que o handoff deixou:
>
> * **(a) regra assinada**, com o critério (c) **re-derivado sobre a mediana
>   pós-D1**: a triagem sob `limite_sres` mede fila de **26** e mediana de
>   redução necessária **13 %** (era 18 e 9 % na régua global — a diferença são
>   as ex-data-limited que o D1 absorveu como regra e seguem fora por outras
>   pernas). Mesma derivação declarada (mediana/3): **o limiar do retorno
>   marginal passa de 3 % para 4 %** por candidato. Números vivos:
>   `triagem_posD1.json` (reproduz: `py -3.12 New_Theory/regra_de_parada_triagem.py`).
> * **(b) SIM** — `n < 6` vira classe **declarada "não-julgável"** (σ_res sem
>   suporte estatístico em 4–5 pontos); 3 curvas hoje.
> * **(c) SEMPRE OS DOIS, JUNTOS** — estrito (tripé) e resolvido/declarado, com
>   a tabela de camadas ao lado. Pós-D1: **estrito 124** · resolvido/declarado
>   **124 + 25 exceções + 12 declaradas = 161 de 202 (80 %)**.
>
> Camada 2 **executada** na mesma assinatura: as 12 declaradas (3 n<6 + 9
> colapso) estão em `_DECLARADAS` no `report_html.py`, com badge próprio e a
> leitura dupla publicada no cabeçalho do report mestre. As **15 indecidíveis**
> ficam fora de tudo, como a regra manda — 1 réplica por fonte destrava (item
> (d), ação de bancada). Os §§1 e 5 abaixo preservam os números da régua global
> como registro datado.
>
> **Atualização 2026-07-30 (tarde), pós-adoção ZHANG_2018** (creep com onset,
> preregs R1/R2 gates 4/4, `zhang18_creep_onset_resultado.md`): tripé estrito
> **127/202** · resolvida/declarada **164/202** · fila de forma **23** (−3
> zhang) · mediana de redução de σ_res necessária **11 %** (o critério (c)
> re-derivado dá 11/3 ≈ 3,7 ⇒ o limiar de 4 % **fica**). O membro
> Cattaneo-Mindlin da classe fechou INCONCLUSIVO no re-run com teto único
> (ganho ≡ 0; não conta para (b)); o candidato creep-onset NÃO era membro da
> classe (canal aditivo existente) e foi adotado por constantes per-par.
>
> **Atualização 2026-07-30 (noite), pós-adoção LIU_2016** (re-atribuição da
> cauda creep→fretting L1, gates 5/5, `liu2016_fretting_resultado.md`): tripé
> estrito **132/202** · resolvida/declarada **168/202** (exceções ativas
> 25→**24**: a assinatura da `fig9a_m45nm` foi retirada porque a curva passou
> por mérito — detectada pelo invariante, `_EXCECOES_RETIRADAS_ADOCAO_LIU2016`)
> · fila de forma
> **19** (−4 liu2016; a fonte fechou 14/14) · mediana de redução necessária
> **24 %** — subiu porque as duas adoções removeram as curvas próximas do
> limite e sobrou o núcleo duro (CHU ×6 a 3,3–3,8×) ⇒ **critério (c)
> re-derivado: 24/3 = 8 %/candidato**. Fronteira da delegação atingida: os
> 19 restantes exigem forma nova de engine (PR-3), dado de bancada (Ra por
> espécime no CHU; réplicas) ou decisão do professor — mapa curva-a-curva em
> `DECISOES_PENDENTES` ("Fronteira da fila pós-adoções").
>
> **Atualização 2026-07-31 — a parada por classe DISPAROU pela 1ª vez, e o
> §4 abaixo fica como registro datado.** Classe "regime intermediário CHU
> com mecanismos EXISTENTES": (a) ✓ ≥2 instrumentos; (b) ✓ todos os membros
> exequíveis medidos (3 F1 analíticos + teto cinemático inerte + ratchet
> piora + grade de dano 54 pontos sem dose viável — a máquina de dano MOVE
> certo, test2 fim 0,16 vs 0,14, mas o relógio é monótono na amplitude e o
> dado não é); (c) ✓ retorno do último candidato: 0 fechamentos.
> **Reabre com:** Ra por espécime, réplica em D0.4/D0.5, ou forma nova
> não-monótona (PR-3). Idem "dose compartilhada de incubação LIU_2025"
> (grade 12 pontos, F1). `chu_veredicto_completo.md` +
> `liu2025_onset_grid_probe.json`. No mesmo dia: piso do LU_2024 medido do
> par publicado entre figuras (σ 0,0912) ⇒ T22Nm exceção F7-FORTE,
> indecidíveis 15→12→11 (`zhang2006_fig3` declarada por proveniência), e o
> gargalo rebalanceou (σ 28 · MAE 16 · mx 26). Censo NAQUELE momento
> (antes dos 3 casos da Fig.14, da adoção final LU_2024 e da saída
> temporária da UFU_LAB no mesmo dia): estrita **132** ·
> resolvida/declarada **170** de 202 — o vivo está no CLAUDE.md.

> ## 🛑 2ª PARADA POR CLASSE — "aceleração tardia" (2026-08-01)
>
> Os três requisitos, com evidência:
>
> **(a) ≥2 instrumentos independentes** ✅ **três**: razão de inclinação
> terminal dado÷modelo (2× a 225× em 7 fontes) · decomposição de variância
> do σ_res ("curvatura, não taxa": 59,7 % ENTRE estágios) · janela de
> truncamento (excesso de σ inteiro além de 200 k ciclos).
>
> **(b) todo membro falsificado por predição pré-registrada** ✅ **três
> candidatos, três preregs, três mecanismos nomeados**:
> gates Hill só ATRASAM (contradomínio (0,1] — falsificação *por
> construção*, `crash_trigger_classe_resultado.md`) · amplificador por
> acumulador é GRADUAL demais (D vai 0→0,9; +53 %/+119 %/+397 % de MAE,
> `amplificador_tardio_resultado.md`) · amplificador por interruptor tem
> sinal e perfil certos mas **não é per-rig** (CHU: mesmo k, 5 curvas
> melhoram e 3 pioram, `amplificador_interruptor_resultado.md`).
>
> **(c) retorno marginal nulo** ✅ os **3 últimos candidatos** deram
> **zero** saídas por mérito.
>
> **O 4º candidato da spec (relógio por curva) é DATA-BLOCKED, não
> "não tentado"**: exige vida publicada por curva, e as curvas da classe
> terminam em razões arbitrárias (YANG_2019 0,73/0,75/0,21; CHU
> 0,99/0,14/0,18) porque o ensaio é interrompido por critério de protocolo,
> não por falha. Usar as médias da Tabela 3 do Yang seria importar número
> medido em OUTROS espécimes.
>
> **Reabre automaticamente com**: vida por curva publicada/medida, dado de
> bancada, ou uma forma cujo relógio não seja `D` (gradual) nem `F₀`
> (realimenta o que amplifica). As duas capacidades ficam no engine,
> default-inertes e testadas.

**Data:** 2026-07-30 · **Store:** `3546e6745448` · régua de 3 pernas
(`res.máx ≤ 0,10 · MAE ≤ 0,05 · σ_res ≤ 0,025`). Todos os números abaixo são
**medidos**, não estimados, e o comando que os reproduz está na §7.

---

## 1. Por que a pergunta estava mal posta (e o que a medição mostrou)

A regra de parada foi pedida sob a leitura *"o σ_res domina 89 % das reprovações,
18 alavancas não o fecham, três candidatos morreram — talvez a perna seja
inalcançável"*. **A triagem das 98 curvas fora do tripé desmente a premissa:**

| categoria | n | % das fora | remédio |
|---|--:|--:|---|
| **exceção já assinada** (F5 + F7) | **44** | 45 % | nenhum — resolvida |
| metric-limited: `n < 6` pontos | 3 | 3 % | declarar; a perna não é julgável |
| metric-limited: colapso quase-vertical (Δdado > 0,25 entre pontos) | 9 | 9 % | declarar; §4.44–§4.48a |
| data-limited: piso medido da fonte **acima** do limite | 9 | 9 % | novo dado, não novo modelo |
| **sem piso medido** (indecidível hoje) | 15 | 15 % | 1 réplica por fonte |
| **FORM-LIMITED — alvo legítimo** | **18** | **18 %** | é aqui que o pipeline gasta |

**A fila real é 18 curvas, não 98 nem 51.** E a distância delas ao limite é pequena:

| redução de σ_res necessária | curvas |
|---|--:|
| já dentro (reprovam só no MAE) | **3** |
| ≤ 5 % | 4 |
| ≤ 10 % | **9** |
| ≤ 20 % | 13 |
| ≤ 50 % | 18 (todas) |

**Mediana: 9 %. Máxima: 47 %.** E das 18: **9 violam o MAE**, 15 o σ_res, **1** o
res.máx. Nove violam **só** o σ_res.

⇒ A perna **não** é globalmente inalcançável. O que existe é uma fila curta, com
distância pequena, e uma narrativa construída sobre a população errada (as 98, das
quais 45 % já estão resolvidas e 21 % são limitadas por dado ou métrica).

**Consequência para a regra:** uma parada global do tipo *"a perna é inatingível"*
seria **errada hoje**. A regra tem de ser **por classe de forma**, com triagem por
curva antes, e ter condição de reabertura.

## 2. Os três candidatos de parada que descartei, e por quê

- **Contagem** (*"após K candidatos, pare"*) — arbitrário e **gameável**: trata igual
  um candidato bem posto e um chute. Não distingue "falhou" de "foi falsificado".
- **Orçamento** (*"após X horas"*) — mede esforço, não informação. Um orçamento gasto
  em candidatos sem predição não ensina nada; foi o gasto de 10 linhas de predição
  que matou a incubação com proveito.
- **"Piso acima do limite ⇒ pare"** — já é o mecanismo de exceção (F7) e é **por
  curva**, não regra de campanha. E a atividade E mediu o erro de confundir os dois:
  piso alto **não** absolve quem está fora dele.

## 3. A regra recomendada — três camadas

### Camada 1 · conclusão POR CURVA (já existe; manter)

Uma curva está **resolvida** quando passa o tripé **ou** o erro cabe em
`piso_fonte/√2` (barra FORTE da F7, já assinada). Nada a acrescentar.

### Camada 2 · saída da FILA por curva (novo — é o que a triagem compra)

Uma curva **sai da fila de forma** — e é declarada, não escondida — quando satisfaz
um critério **medido**:

| rótulo | critério | hoje |
|---|---|--:|
| σ não julgável | `n < 6` pontos na janela da métrica | 3 |
| metric-limited | `max|Δdado| > 0,25` entre pontos consecutivos (colapso que a métrica não resolve) | 9 |
| data-limited | piso de σ medido da fonte **>** `META_SRES` | 9 |

Total: **21 curvas declaradas sem tocar o modelo**. As **15 sem piso medido** ficam
**fora da fila e fora das declaradas** — rótulo `indecidível`, com a ação nomeada
(uma réplica na mesma condição por fonte). Não podem ser contadas como resolvidas
nem como falha do modelo.

### Camada 3 · PARADA por CLASSE DE FORMA (o núcleo)

Pare de gastar numa classe quando **as três** valerem:

**(a) A classe foi identificada por ≥ 2 instrumentos independentes.**
*Satisfeito hoje:* projeção polinomial (atividade F) e lei da variância por estágio
(sessão paralela) concordam que a 2ª forma é **curvatura**.

**(b) Todo membro enumerado da classe foi FALSIFICADO por predição
pré-registrada** — não apenas "não melhorou". A predição tem de ser um
discriminante escrito antes, que separe *o mecanismo alegado* de *a alavanca mexeu
no número*.
*Estado hoje na classe "taxa dependente do estado acumulado":*

| membro | estado |
|---|---|
| `graded_scrit` | **componente** (trata a rampa; sobra a curvatura) |
| incubação `slip_onset_W` | **FALSIFICADO** (predição de ordenação por amplitude caiu: +32 % vs +47 %) |
| Cattaneo-Mindlin (D2′) | **INCONCLUSIVO** (re-run teto único 2026-07-30: ganho ≡ 0, mérito era artefato de teto; não conta para (b)) |
| kernel desacelerante | **FALSIFICADO** (G2: 8 pioram, uma 0,0396→0,2232 — pioras em curvas curtas, sem truncamento) |
| bifurcação de limiar | **nunca sondado** |

**(c) O retorno marginal é medido e nulo:** após os **3** candidatos mais recentes,
(i) **zero** curvas saíram da fila por mérito **e** (ii) a **mediana da distância ao
limite** da fila caiu **menos de 3 % relativos**.

> **Por que 3 % e não outro número:** a mediana da fila precisa de **9 %**. Um ritmo
> abaixo de 3 % por candidato não fecha a curva mediana em três tentativas — é a
> definição operacional de "não está indo". O número sai da fila medida, não de
> convenção.

### Reabertura (uma regra de parada sem isto é armadilha)

A parada é **provisória** e reabre **automaticamente** se: o `engine_fingerprint`
mudar · um instrumento novo mudar a decomposição · o `n` ou o piso de qualquer curva
da fila mudar (dado novo) · a régua mudar. É a §4.43 aplicada à parada: *toda
pendência carrega o fingerprint contra o qual foi medida e vira suspeita quando ele
muda.*

## 4. O que a regra diz HOJE

**Ela NÃO dispara.** Requisito (b) falha: **dois** dos quatro membros da classe
— kernel desacelerante e bifurcação de limiar — **nunca foram sondados**. Requisito
(c) também não está satisfeito, porque a incubação foi o 1º candidato com predição
pré-registrada; faltam dois para o contador de 3.

⇒ A resposta honesta a *"devemos parar?"* é **ainda não**, e a regra diz exatamente
o que falta: **duas sondas**, cada uma com discriminante escrito antes.

O que a regra **já** autoriza sem esperar: declarar as **21** curvas da camada 2
(3 + 9 + 9), o que move a meta de **149 para 170 de 202 (84 %)** sem tocar no
modelo — não por indulgência, mas porque *"o modelo errou"* e *"a métrica/o dado não
decide"* são coisas diferentes e hoje estão somadas.

## 5. Efeito de cada camada no número publicado

| passo | resolvidas | de 202 |
|---|--:|--:|
| hoje (tripé 105 + 44 exceções) | **149** | 74 % |
| + declarar `n < 6` (3) | 152 | 75 % |
| + declarar metric-limited de colapso (9) | 161 | 80 % |
| + declarar data-limited por piso (9) | **170** | **84 %** |
| fila de forma que sobra | **18** | 9 % |
| indecidível (falta réplica) | 15 | 7 % |

⚠️ **Isto muda o SIGNIFICADO do número, e é decisão sua:** 170/202 lê-se *"resolvidas
ou declaradas com procedência"*, não *"o modelo acerta 170"*. A leitura estrita
(passa o tripé) continua **105**. Recomendo publicar **os dois**, sempre juntos, com
a tabela desta seção ao lado — é o que impede o 84 % de ser lido como acurácia.

## 6. Por que esta é a melhor regra disponível

1. **É falsificável:** cada cláusula tem um número medido no store; nenhuma depende
   de julgamento sobre "esforço suficiente".
2. **Não é gameável:** (b) exige predição *antes*, o que impede transformar uma
   alavanca que mexe no número em "mecanismo validado" — o erro exato que a sonda da
   incubação evitou (68 % de redução de `|a|` na `test7` que teria passado por
   confirmação).
3. **Separa os três motivos de não fechar** (forma / métrica / dado), que têm
   remédios diferentes e estavam somados numa fila de 98.
4. **Tem custo de manutenção baixo:** as três camadas se computam do store, e o
   `test_meta_numeros_nao_envelhecem.py` já existe para impedir que os números
   envelheçam em silêncio.
5. **Não autoriza o que a evidência não sustenta:** aplicada hoje, ela **recusa**
   parar. Uma regra que justificasse a parada imediata seria conveniente e errada.

## 7. Reprodutibilidade

```bash
py -3.12 New_Theory/regra_de_parada_triagem.py     # a triagem e as distancias
```

---

## FECHO DO CRITÉRIO (c) — 2026-08-14 (noite), sob "continue o loop, eu assino tudo"

O achado `a95efcc` (sessão paralela) fica ADOTADO como está: **o (c) não era
avaliável** com fila monofonte e data-blocked, e a re-derivação "69 %/3 = 23 %"
fica **explicitamente rejeitada** — o número mede ausência de dado numa fonte,
não retorno marginal de ideias. A saída (1) da própria proposta
materializou-se no mesmo dia: **o item F foi executado** (8 órfãs de protocolo
declaradas) e a **fila form-limited é ZERO**.

Estado da regra: **as 3 camadas cumpridas** — (1) conclusão por curva: toda
curva comparável tem tripé, exceção com prova, declaração com critério, ou
classificação de bloqueio (indecidível-sem-piso = falta réplica, ação de
bancada); (2) saídas declaradas; (3) parada por classe: a classe form-limited
FECHOU por esvaziamento (todo membro com estatuto ou falsificação
pré-registrada), não por (c). **O (c) permanece com a redação original para
uma fila FUTURA** que volte a ter ≥2 fontes com rota — reabertura automática
pelos gatilhos já escritos (fingerprint/instrumento/dado/régua).
