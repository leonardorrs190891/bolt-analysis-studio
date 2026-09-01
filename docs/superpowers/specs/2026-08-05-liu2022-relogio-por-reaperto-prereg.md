# Prereg — relógio por CONTAGEM DE REAPERTOS (o membro não testado da classe)

**2026-08-05** · decisão D-J (por delegação, MANDATO PERMANENTE do charter) ·
gates escritos **antes** de implementar. Fingerprint de partida:
`98fd6c462968`.

## Por que a classe NÃO estava esgotada

`liu2022_fig8_cadeia_resultado.md` (D-E) matou a família de constantes (10
parametrizações) e disse que o relógio por contagem de reapertos morria por
**contradição intra-fonte**. Sob a cláusula do mandato — *candidato inerte ou
gate nunca chamado é INCONCLUSIVO, não falsificação* — essa morte **não
qualifica**, por dois motivos medidos hoje:

1. A contradição prova que um relógio **GLOBAL** não serve (o dado varre de
   0,75× a 2,05× entre as 4 cadeias). Ela **não** prova que um relógio **por
   protocolo** não serve: as duas cadeias que **não soltam** aceleram na mesma
   direção e com a mesma magnitude.
2. O **`k_gall`** — a constante cujo nome é a física da classe — foi
   **CONGELADO** no D-E por decisão minha. Medido hoje por sonda de 2 pontos
   (0,0 e 12,0 contra o vigente 3,0): **Δ = 0,000000 exato**. É **INERTE por
   construção** nesta cadeia, e a inércia é decidível do config: `k_gall` só
   age em `tightening_torque`, e o **F₀ por estágio é lido do 1º ponto do
   dado**, sobrepondo a recuperação que o modelo calcularia. ⇒ `k_gall` **não
   é membro** da classe. Congelamento inócuo.

## O defeito, convertido em fator necessário por estágio

Decomposição medida: **embedding + wear carregam ~90 %** de cada estágio
reapertado, e o embedding é praticamente **constante** (0,046/0,056/0,060/
0,056 kN normalizado) — `k_emb_renew=1,0` em regime de dano alto reseta a
capacidade de assentamento a cada reaperto.

| estágio | perda dado | perda modelo | fator necessário | razão vs anterior |
|---|---:|---:|---:|---:|
| t0 (virgem, n=0) | 11,10 % | 14,90 % | 0,745 | — |
| t1 (n=1) | 2,22 % | 10,96 % | **0,203** | — |
| t2 (n=2) | 3,96 % | 11,17 % | 0,354 | **1,75×** |
| t3 (n=3) | 7,91 % | 11,01 % | 0,719 | **2,03×** |

**É um V, não uma rampa.** O 1º reaperto deixa a junta ~5× mais estável e
depois ela degrada de volta. Relógio monotônico não produz V; **queda em n=1
(o `k_emb_renew`, que já existe) + crescimento por evento** produz — e deixa o
**t0 intocado por construção** (n=0 ⇒ multiplicador 1).

## O teste de MECANISMO (a razão de este prereg existir)

Mesma conta no `fig7a_oil_direct` (óleo, também **sem soltar**):

| | fator n=1 | fator n=2 | fator n=3 | razões |
|---|---:|---:|---:|---|
| fig8 (seco) | 0,203 | 0,354 | 0,719 | **1,75× · 2,03×** |
| fig7a (óleo) | 0,483 | 0,720 | 1,464 | **1,49× · 2,03×** |

**O CRESCIMENTO é o mesmo nas duas lubrificações (~1,8–1,9); só a QUEDA
difere.** Isso é o que permite **1 número compartilhado** com predição de
transferência cross-lubrificação. A queda fica no `k_emb_renew` **por grupo**
(que já é por-lubrificação, como `c_D` e `mu`).

## Implementação (default-inerte, bit-idêntica com o número em 0)

- `SlowState.n_retighten: int = 0` — incrementado em `retighten()`. (Medido
  hoje: o `SlowState` **não tem** contador; é campo novo.)
- `JointMaterial.retight_loss_growth: float = 0.0` — **0,0 = OFF exato**.
- Multiplicador `(1 + retight_loss_growth) ** n_retighten` sobre o `dF_0`
  **dirigido por slip** (wear + afrouxamento rotacional), seguindo o padrão
  estabelecido do `slip_onset_gate`: **`dF_0` sim, `dE` de wear não** (o
  micro-slip segue dissipando calor real; amplificar `dE` quebra conservação).
- **NÃO** aplicar ao embedding: assentamento é conformação plástica, que
  **decresce** com carregamento repetido — crescer nele seria física ao
  contrário. É o `k_emb_renew` que trata o embedding.

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (inércia exata):** com `retight_loss_growth=0,0`, as **210** curvas do
  store ficam **bit-idênticas**. Sem isso a implementação não entra.
- **G1 (MECANISMO — o gate que decide):** **um único** valor de
  `retight_loss_growth`, compartilhado por fig8 (seco) **e** fig7a (óleo), tem
  de melhorar as **duas** cadeias. Fitar valores diferentes por lubrificação
  **é proibido** — mataria a claim, que é justamente a transferência.
- **G2 (t0 protegido):** as curvas com n=0 (`fig8_t0`, `fig7a_t0`, e as 4 do
  `fig5`) ficam **bit-idênticas**. Se mudarem, o multiplicador vazou para o
  estado virgem.
- **G3 (controle de protocolo):** as **8** curvas que **soltam**
  (`fig6a` ×4, `fig6b` ×4) ficam **bit-idênticas** — elas não recebem o
  número. Se mudarem, vazou de grupo.
- **G4 (nenhum caso pior):** nenhuma das 9 curvas dos grupos alterados piora
  > **+0,010** em qualquer perna; as **4** do fig7a e a `fig8_t3`, hoje no
  tripé, **permanecem**.
- **G5 (ganho):** ≥ **2** das 3 curvas de fila do fig8 entram no tripé. Uma só
  ⇒ adoção **parcial declarada**. Zero ⇒ não adota.
- **G6 (procedência):** o valor é **fit de 1 número** sobre 2 cadeias, e o
  `prov` diz isso. Se o valor adotado ficar **fora** da faixa que a aritmética
  prevê (1,49–2,03 ⇒ `growth` entre **0,49 e 1,03**), **declarar** — porque
  aí a alavanca não faz o que a conta supõe, e isso é informação sobre a
  alavanca, não sobre o dado.
- **G7 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos 210 +
  censo/docs/páginas/testes no MESMO commit; e o campo novo exige `VarSpec` no
  explorador (`_ve_content.py`) senão `test_all_fields_covered` falha, mais
  entrada no teto de DOF com o motivo (`_sem_dof_fitado`).

### Ramos

- **ADOTA** — G0..G5.
- **FALSIFICADO (não transfere)** — nenhum valor único melhora as duas
  cadeias ⇒ o crescimento é por-lubrificação, logo é ajuste e não mecanismo.
  Registrar com os dois ótimos separados para mostrar a distância.
- **FALSIFICADO (canal errado)** — o multiplicador no canal de slip não
  produz o V nem com `k_emb_renew` ajustado ⇒ a forma faltante não está neste
  canal.
- **NÃO ADOTA (t0 ou controle pagam)** — G2/G3/G4 reprovam.
- **INCONCLUSIVO** — o campo sai inerte por companheiro desligado, ou o
  canal de slip carrega ~0 da perda no estágio (conferir a decomposição
  DEPOIS, não antes: alavanca que troca a lei de taxa não está limitada pela
  fatia do nominal — §6 do `chu_segundo_defeito_resultado.md`).

## Previsão registrada

Espero `retight_loss_growth` ≈ **0,8–0,9** (razão 1,8–1,9), **um só valor**
para seco e óleo, com `k_emb_renew` caindo para ~**0,2–0,3** no fig8 e ~**0,5**
no fig7a. Espero **t1 e t2 fecharem** e a **t4 não** (é a curva de fratura, e o
canal de fadiga está desligado neste grupo). Espero a `fig8_t3` **continuar** no
tripé — ela é hoje a mais folgada da cadeia e o multiplicador cresce justamente
nela (n=3), então é o ponto de tensão real do G4.

**Se o crescimento não transferir entre as lubrificações, eu prefiro o ramo
FALSIFICADO a fitar dois números** — o valor deste candidato está inteiro na
transferência.
