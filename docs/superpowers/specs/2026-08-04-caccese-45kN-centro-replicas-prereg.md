# Prereg — o grupo 45kN do CACCESE está FORA da banda de réplicas

**2026-08-04** · decisão D-I (por delegação, mandato 2026-07-30) · gates
escritos **antes** de medir. Fingerprint de partida: `8f4b29218b6e` (pós-D-H).

## O defeito não é "erro grande" — é modelo fora da dispersão do dado

`caccese2009_tapered_45kN_rep1` e `rep2` são **réplicas da MESMA condição**
(par declarado em `_PARES_REPLICA_DECLARADOS`). Medido na janela comum
(60 pts):

| | MAE | viés |
|---|---:|---:|
| **piso** \|rep1−rep2\| (dado-vs-dado) | **0,0382** | — |
| modelo vs rep1 | 0,0635 | **−0,0635** |
| modelo vs rep2 | 0,0260 | **−0,0253** |

**Os dois viesses são negativos** ⇒ o modelo não está *entre* as réplicas: ele
está **abaixo das duas**, perdendo mais pré-carga que qualquer dos dois
ensaios. Ele está **fora da banda que o próprio dado não consegue
distinguir**.

Isso é diferente de "o erro é grande". Quando a condição tem réplicas, o alvo
legítimo é o **centro** delas — fitar contra uma das duas é uma escolha
arbitrária que o ajuste anterior fez implicitamente, e neste caso o resultado
caiu fora das duas.

## O que a translação ideal entrega (aritmética, antes de simular)

Deslocamento para o centro: **+0,0444** em retenção.

| | MAE resultante | vs piso 0,0382 | vs tripé 0,05 |
|---|---:|---|---|
| rep1 | **0,0206** | **FORTE** (≤0,0270) | passa |
| rep2 | 0,0276 | PROVA | passa |

⚠️ σ_res é **invariante por translação**: a `rep2` continua reprovando no σ
(0,0270 contra 0,0250). Ganho esperado: **1 curva (rep1)**, não 2. Declarado
antes de medir para não virar surpresa favorável.

## Escopo: 1 número, e ele move uma curva de controle

`C_creep` do grupo **`CACCESE_2009_45kN`** — que serve **3** curvas:
`protruding_45kN` (cabeça saliente, **no tripé**, MAE 0,0157), `tapered_rep1`
e `tapered_rep2`. Não há como mover as tapered sem mover a protruding, e é
por isso que ela é o gate.

**O `creep_mode`/`α`/`t_c` adotados hoje no D-H ficam CONGELADOS.** Isto é
ajuste de **nível**, não de forma; misturar os dois no mesmo passo tornaria
impossível dizer qual mudou o quê.

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (direção, 2 pontos):** confirmar por sonda que reduzir `C_creep`
  **sobe** a retenção do modelo. Δ = 0 exato ⇒ INCONCLUSIVO, não "morto".
- **G1 (o gate que decide — dentro da banda):** o modelo tem de ficar
  **dentro da banda de réplicas**: `|erro| ≤ 0,0382` contra **rep1 E rep2**
  simultaneamente. Este é o critério de mecanismo; um MAE menor sem entrar na
  banda não conta.
- **G2 (controle da mesma config):** `protruding_45kN` **permanece no
  tripé** e não piora > **+0,010** em nenhuma perna.
- **G3 (isolamento):** as outras 4 curvas do CACCESE (grupos `compblock`,
  `12p7mm`, `19p1mm`) e todas as outras fontes ficam **bit-idênticas**.
- **G4 (ganho):** `rep1` **entra no tripé**.
- **G5 (procedência):** o valor adotado é declarado como *"fit de 1 número
  com alvo no CENTRO das réplicas"*, com o piso medido citado. Escolher o
  valor que minimiza o MAE de **uma** das réplicas é **proibido** — foi
  exatamente isso que produziu o defeito.
- **G6 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos 210
  + censo/docs/páginas/testes no MESMO commit.

### Ramos

- **ADOTA** — G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4.
- **NÃO ADOTA (a protruding paga)** — G1/G4 passam mas a `protruding` sai do
  tripé ou piora > +0,010: trocar uma curva por outra não é progresso.
- **NÃO ADOTA (não entra na banda)** — nenhum `C_creep` põe o modelo dentro
  de 0,0382 das duas réplicas ao mesmo tempo ⇒ a dispersão entre as réplicas
  tem estrutura que uma translação não alcança (ex.: elas divergem em forma,
  não em nível). Registrar com o número.
- **INCONCLUSIVO** — alavanca inerte ou G0 sem direção definida.

## Previsão registrada

Espero que `C_creep` **menor** feche a `rep1` e mantenha a `protruding` (ela
tem 0,0343 de folga no MAE, mais que o deslocamento pedido). Espero que a
`rep2` **não feche** (σ). E espero que o valor ótimo fique **próximo** do que
a aritmética prevê (redução de ~11–15 % na perda de creep); se ele ficar
muito longe disso, a translação não é uma boa aproximação do que a alavanca
faz, e isso é informação sobre a alavanca.
