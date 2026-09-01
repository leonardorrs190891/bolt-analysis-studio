# PREREG — exceção por DISPERSÃO DE VIDA entre réplicas (classe nova, protocolo CEGO)

## Estado — **EXECUTADO · CLASSE VAZIA (ramo G6)** — a classe NÃO entra

> Registrado em 2026-08-19 (15:4x), mesma sessão, ~30 min após o congelamento.

**Sob a B1 ESTRITA** (réplica = mesmo stem após remover sufixo `_rN`/`repN`/
`baselineN`/`runN`, OU par em `_PARES_REPLICA_DECLARADOS`): **8 famílias**, das
quais **5 elegíveis** por vida (yang2021 0,6mm · bauer fig6 ×6 · karlsen M30 ·
karlsen M42 · eccles 8a×8c) — e **UMA única candidata aberta**: a
`yang2021_amp0p6mm_ax8kN_r1`.

**A r1 reprova a B4.** Na janela comum ela passa tudo com folga (n=8, MAE
0,0086 · mx 0,0397 · σ 0,0138) — mas na cauda excluída (11300–11800) o
dado-vs-dado da família **NÃO viola a meta**: as irmãs concordam com a r1 a
+0,006..+0,024 ali. Quem diverge na cauda é o **modelo** (+0,040/+0,081). A
divergência de vida da r1 só vira violação de meta **depois de 11800** — região
que o trim já exclui da métrica. ⇒ a exceção não é provável pelo dado na região
em que a curva é julgada, e isso **reconfirma por um segundo ângulo** o
fechamento do alvo 1: o erro da r1 na janela é do modelo mesmo.

**Predições: 1 errada, 4 certas.** A nº 1 ("r1 qualifica") errou exatamente na
B4, e o erro é o achado. As nº 2–5 (fig2 fora, famílias de creep inelegíveis,
tripé em 144) confirmaram.

⚠️ **O 1º run do protocolo violou a B1 do próprio prereg** — o agrupador usou
fonte+condição sem o filtro de junta, e "qualificou" os pares do ICMEZ (grip
13,8×19,8, bloqueados na Fase 1) e os tratamentos do SUN (crimp×standard).
Teria sido o **7º pareamento inválido** da campanha. O run estrito acima é o
que vale; o frouxo fica como registro de que a B1 *precisa* do filtro de junta
— e de que a guarda `test_par_de_replica_e_mecanicamente_identico` não cobre
famílias implícitas, só pares declarados.

**Consequência da delegação:** a melhor decisão para chegar ao tripé foi
**testada e é NÃO mexer** — nem na régua, nem por exceção. O 144/205 é o teto
de (dado + régua atuais); os destravadores reais permanecem os dois já na mesa:
a **réplica no ICMEZ** (experimento) e qualquer decisão de régua maior — agora
com a prova de que a versão "exceção por dispersão de vida" **não é** o
instrumento.

**2026-08-19 (15:2x)** · **barras e gates congelados neste commit, ANTES de
qualquer medição de candidata** · store `7a60cacb72de`, censo 144/205 ·
mandato: *"tome a melhor decisão para chegar no tripé"* (delegação explícita,
15:11), sob a doutrina de delegação vigente (memória `mandato-continuo`,
precedente da regra n<6 assinada por "tudo assinado").

## 0. Por que ESTA é a decisão, e o que ela não é

A sequência de ataque (e41bc4b) esgotou o Grupo A com número e mediu o mesmo
fenômeno em **três fontes independentes**: espécimes da mesma condição nominal
divergem na CAUDA porque **morrem em momentos diferentes** (YANG_2021
12400/14649/16251; LIU_2025 9870/14400; LU_2024 terminal não-monótono
publicado). O piso de σ por condição, medido na janela comum, **não carrega**
essa dispersão — e o modelo está no **centro** das réplicas (σ 0,006–0,007
contra r2/r3). As alternativas: mudar a MÉTRICA (janela de vida comum para
todos) mexeria em dezenas de curvas e no significado do censo — grande demais
para delegação; não fazer nada deixa curvas reprovando por não prever **qual
espécime morre primeiro**, que nenhum modelo determinístico único pode.

A via escolhida é o instrumento que a campanha **desenhou para isto**: a
**exceção com prova** — que retira da fila SEM fechar curva (o tripé **não**
sobe; *resolvidos* sobe). É a leitura honesta de "chegar no tripé": mover o que
é movível sem tocar na régua de quem passa.

## 1. A classe — definida ANTES de olhar candidatas

Uma curva qualifica para a exceção **"dispersão de vida entre réplicas"** sse
**todas** as barras abaixo valem:

**B1 — família elegível.** A condição (fonte + mesma junta + mesmo drive, os
invariantes da guarda de pares) tem **≥ 2 réplicas** com **vidas medidas** pelo
critério já em uso (N onde F/F₀ < 0,5, o mesmo de 2026-08-19), e as vidas
diferem em **≥ 10 %** (dispersão real, não ruído de leitura). Família cujas
curvas não zeram é **inelegível** (sem vida, não há dispersão de vida).

**B2 — janela de vida comum.** Definida como N ≤ **N_D do espécime de menor
vida**, com N_D medido pelo **kneedle** (máxima distância à corda até N_f) — o
critério **pré-existente**, commitado em `b5e0bae` ANTES desta proposta, o que
impede que a janela seja desenhada para a curva.

**B3 — o modelo passa onde a física é comum.** Na janela de vida comum, a
candidata passa **as três pernas** da meta vigente (MAE ≤ 0,05 · res.máx ≤ 0,10
· σ ≤ `limite_sres` da fonte) com **n ≥ 6** pontos (regra assinada de
2026-08-01 — sem suporte estatístico não há prova).

**B4 — a cauda excluída é indecidível PELO DADO.** No trecho excluído
(N > N_D(min), até o fim da janela da métrica da candidata), o **dado-vs-dado**
da própria família (candidata × cada irmã, interpolação na grade da candidata)
**viola ao menos uma perna** da meta. É a prova estilo F5-família: naquela
região as réplicas discordam entre si além da meta ⇒ nenhum modelo
determinístico único poderia servir a todas ali.

**B5 — trio conferível.** A assinatura registra, por perna violada na janela
CHEIA, o par `valor/piso` exigido pela catraca
(`test_excecao_catraca_auditavel`).

## 2. GATES da execução — congelados

| # | gate | critério |
|---|---|---|
| **G1** | **cegueira** | o protocolo roda sobre **TODAS** as famílias com ≥2 réplicas do store — a lista de famílias sai do agrupador canônico, não de uma lista minha |
| **G2** | **catraca** | toda assinatura nova carrega o trio conferível; `test_excecao_catraca_auditavel` verde |
| **G3** | **o tripé NÃO sobe** | censo tripé = 144 antes e depois (exceção retira da fila, não fecha curva); `resolvidos` sobe exatamente pelo nº de assinadas |
| **G4** | **store intocado** | fingerprint `7a60cacb72de` e métricas bit-idênticas (a classe vive no report, não na física) |
| **G5** | **guardas espelho verdes** | `test_medicoes_cruzadas` (exceção de fato fora do tripé) e `test_instrumentos_de_censo_concordam` |
| **G6** | **falsificação honesta** | se **nenhuma** curva qualificar sob as barras congeladas, a classe **não entra** — o registro vira "classe proposta e vazia", e as barras NÃO são afrouxadas para admitir alguém |

## 3. Predições registradas (antes de medir as barras)

1. `yang2021_amp0p6mm_ax8kN_r1` **qualifica**: janela ≈ joelho do espécime 1
   (~10 500–10 800); os 7 primeiros resíduos são ±0,004–0,015; a cauda excluída
   contém o par r1×r3 com MAE ~0,05+ (a conferir contra a meta).
2. `liu2025_M16_fig2_single` **NÃO qualifica**: o déficit dela (ρ=+0,97) mora
   DENTRO da janela comum — a B3 reprova. Se qualificar, suspeitar do
   instrumento.
3. `liu2025_M16_amp0p8` — **incerta** (é o caso que decide se a classe é
   informativa ou só re-embala a r1).
4. Famílias de creep/sem colapso (CACCESE, ECCLES baselines, JCSR, KARLSEN,
   LIU_2016, BAUER) — **inelegíveis pela B1** (não zeram) ou sem dispersão
   ≥10 %.
5. O tripé fica em **144** (G3, por construção).
