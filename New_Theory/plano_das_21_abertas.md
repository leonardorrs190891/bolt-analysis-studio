# Plano de trabalho das 21 curvas abertas

**2026-08-16 (noite)** · store `7a60cacb72de`, censo **144/205** · lista viva em
`New_Theory/lista_abertas.md` (gerada por `lista_abertas.py`, não digitada).

> **A conclusão, antes do plano:** as 21 **não formam uma fila**. Uma única
> pergunta medível — *a fonte tem piso de repetibilidade?* — as parte em dois
> grupos com trabalhos completamente diferentes, e em **nenhum** dos dois o
> próximo passo é "atacar a curva".

## 1. A partição, medida

### Grupo A — 6 curvas: o piso EXISTE e as CONDENA

Nestas fontes o piso de repetibilidade foi medido, e ele está **abaixo** do
limite global de 0,025. Ou seja: o dado é **mais** repetível que a barra, a
barra é generosa, e o σ do modelo é erro real.

| curva | σ_res | piso da fonte | σ / piso |
|---|---:|---:|---:|
| `lu2024_M8_fig20_T10Nm` | 0,0749 | 0,0033 | **23,0×** |
| `yang2021_amp0p5mm_ax8kN` | 0,0388 | 0,0103 | 3,8× |
| `yang2021_amp1p0mm_ax2kN` | 0,0320 | 0,0103 | 3,1× |
| `liu2025_M16_amp0p8` | 0,0419 | 0,0149 | 2,8× |
| `yang2021_amp0p6mm_ax8kN_r1` | 0,0268 | 0,0103 | 2,6× |
| `liu2025_M16_fig2_single` | 0,0270 | 0,0149 | 1,8× |

⚠️ **Isto corrige o que eu havia dito ao apresentar a lista.** Eu escrevi que as
mais próximas *"podem estar reprovando contra uma barra mais dura do que a
repetibilidade do ensaio permitiria"*. Para estas seis é o **oposto**: a
`yang2021_r1` está a 1,07× do limite, mas a **2,6×** do ruído do próprio dado.

### Grupo B — 15 curvas: o piso NÃO EXISTE, e não é falta de procurar

| fonte | abertas | por quê não há piso |
|---|--:|---|
| `ICMEZ_2025` | 5 | 4 condições × 2 curvas, mas **todo** par difere no **grip** (13,8 × 19,8 mm) — bloqueado em 2026-08-14 |
| `ROUSSEAU_2025` | 4 | o único par (`steel_t10`↔`t12`) difere em **espessura** — bloqueado no erratum de 2026-08-04 |
| `YANG_2023_IJPEM` | 3 | **9 curvas em 9 condições distintas** — nenhuma repetição existe |
| `SUN_2025_CRIMP` | 2 | os pares são `standard`↔`crimp` e `grease`↔`nogrease` — **tratamentos**, não réplicas |
| `YANG_2019` | 1 | **5 curvas em 5 condições** — nenhuma repetição existe |

⇒ para **15 das 21** não se sabe se o modelo erra ou se a barra é dura, e a
resposta **não está no modelo**.

## 2. Fase 1 — converter "indecidível" em DECIDIDO (minha, ~2 h, só-leitura)

Hoje a triagem rotula essas 15 como `indecidivel_sem_piso`, e esse rótulo se lê
como *"ainda não olhamos"*. A tabela acima mostra que é **"olhamos e não há"**.

**Entregável:** um registro por fonte com (a) os pares candidatos que existem,
(b) a grandeza física que invalida cada um, (c) o commit que o bloqueou; mais
uma guarda que falha se um pareamento já bloqueado voltar a entrar. Não muda
censo — muda o que a fila **significa**, de 21 para 6.

⚠️ **Mas a Fase 1 tem de fazer a pergunta oposta primeiro, porque o log de hoje
mostra que ela às vezes tem resposta:** a sessão A acabou de adotar o par
`fig8a`×`fig8c` do `ECCLES_2010` (item O, gates 8/8) e o limite daquela fonte
saltou de 0,025 para **0,0698**. Então "declarar par válido" **funciona** e não é
formalidade. Para cada uma das 5 fontes, a Fase 1 pergunta: *existe par válido
não explorado?* Pela medição acima a resposta parece ser **não** nas cinco — mas
"parece" não é registro, e é isso que a fase produz.

## 3. Fase 2 — o Grupo A é onde o modelo erra, e as rotas estão FECHADAS

- **`lu2024_M8_fig20_T10Nm`** (23× o ruído do dado, a pior das 21): dois defeitos
  caracterizados hoje. O de 1º ciclo **tem lei e tem alavanca** —
  `emb_pressure_exp`, construída default-inerte, conserta a queda inicial
  (0,627 → 0,344 contra 0,362 do dado) e **não fecha** a curva (3,2×). O
  terminal **não tem lei** nesta fonte: o dado é não-monótono e publicado, e o
  modelo é plano ali por construção.
- **`yang2021` ×3 e `liu2025` ×2**: camada `classe_parada` — a classe
  "aceleração tardia" foi **encerrada** por 3 falsificações com prereg e um 4º
  candidato bloqueado por dado.

⇒ **não há trabalho de modelo aberto com justificativa medida.** Propor atacar
essas seis agora seria ignorar as falsificações que a própria campanha
registrou. **Recomendo não fazê-lo.**

## 4. Fase 3 — o que só DADO NOVO resolve

Uma réplica real, mesma condição nominal, em qualquer fonte do Grupo B converte
"indecidível" em julgável — e o precedente do ECCLES mostra o tamanho do efeito
(limite 0,025 → 0,0698).

**Alvo mais barato: `ICMEZ_2025`.** O rig é o mesmo, as 8 curvas já existem, e
falta apenas **repetir uma condição** sem mudar o grip. Cinco curvas dependem
disso, e quatro delas passam MAE e res.máx — reprovam **só** no σ_res.

⚠️ Isto é pedido de **experimento**, não tarefa de sessão. Fica na sua mesa.

## 5. Fase 4 — a decisão que é sua: rodar a regra de parada

Os três critérios da regra (`regra_de_parada_proposta.md`) parecem satisfeitos, e
vale medir formalmente em vez de supor:

- **(a) classe identificada por ≥2 instrumentos** — 18 das 21 têm forma nomeada
  com documento.
- **(b) todo membro falsificado por predição pré-registrada** — as candidaturas
  recentes (`emb_pressure_exp`, piso do `YANG_2023`, `loose_arrest_residual`,
  `k_ratchet` do ROUSSEAU) caíram **todas** por gate próprio, nenhuma por
  "não melhorou".
- **(c) retorno marginal nulo** — nenhuma saída do tripé por mérito de modelo
  desde então; os ganhos recentes vieram de **dado** (pico espúrio) e de
  **procedência** (par do ECCLES), não de forma nova.

**Se a regra disparar, o resultado é uma conclusão, não uma desistência:** o
modelo está no limite do que este corpus consegue julgar, e o que resta é dado
novo e decisão de régua.

## 6. O que eu NÃO recomendo

**Atacar as 21 como fila.** Quinze não são julgáveis por falta de réplica válida
e seis têm rota fechada com número. Uma varredura de alavancas sobre elas
produziria o que as últimas quatro produziram: falsificações — que são úteis,
mas já temos as suficientes para (b).

**Baixar a barra de σ_res.** A auditoria do piso mostra que para o Grupo A o dado
é 1,8–23× mais repetível que o limite; afrouxar a régua esconderia erro real.

**Declarar as 15 para inflar o "resolvido".** Declaração é *"não dá para
julgar"*, e aqui isso é verdade — mas somá-las ao número publicado
transformaria uma limitação de dado em aparência de acerto.

## 7. Ordem sugerida

1. **Fase 1** (minha, ~2 h, sem risco): fechar a pergunta do piso por fonte.
2. **Fase 4** (minha medir, sua decidir): rodar a regra de parada com número.
3. **Fase 3** (sua): decidir se vale uma réplica no `ICMEZ_2025`.
4. **Fase 2**: parada, salvo se a Fase 3 trouxer dado que reabra uma classe.
