# Métrica de banda — a discriminância SOBREVIVEU, e mesmo assim ela morre no B3

**Data:** 2026-07-28 · **Pré-registro:** `specs/2026-07-28-metrica-banda-prereg.md`, gates **congelados em `0e97d6a`**
**Estado final:** implementação **REVERTIDA**; métrica canônica inalterada; store restaurado (203 casos, `4f5bedfbace4`, 0 divergências verticais)
**Antecessoras:** §4.45 (ortogonal) · §4.46 (nível) — ambas rejeitadas

---

## 0. Veredicto

| gate | resultado |
|---|---|
| **B0** invariância à amostragem | **OK** — veredictos idênticos; res.máx da rampa **3,9 %** de diferença (previsto 4,0 %) |
| **B1** discriminância | **OK** — 1ª vez em 3 tentativas |
| **B2** não é afrouxamento cego | **OK** — mediana da melhora **0,00374** (critério < 0,005) |
| **B3** virada exige banda larga | **FALHA** — 1 virada com banda **0,0443** (critério > 0,05) |
| **B4** teto de 25 viradas | OK (**7** viradas, 0 perdas) |
| **B5** fingerprint | OK |
| **B6** inércia em curva plana | **FALHA** — 2 de 35 planas mudam mais que 0,005 |

**Ramo pré-declarado que se aplica:** *"**B3 ✗** ⇒ há virada sem banda larga ⇒
brecha ⇒ **morre**."* Honrado — revertido.
Para o B6 o ramo é diferente e **não mata**: *"revisar `FRAC_N` em prereg novo,
não aqui."*

**E o ramo que NÃO se aplica importa tanto quanto:** o B1 ✗ diria *"3ª morte pela
mesma causa ⇒ a linha fecha em definitivo"*. **B1 passou.** A linha **não** está
fechada.

---

## 1. O que funcionou — e é novo

**B1, a discriminância, sobreviveu pela primeira vez.** As duas mortes anteriores
foram exatamente aqui. No `fig2_single`, nas **duas** digitalizações:

| forma | canônica 15 pts | fina 124 pts |
|---|---|---|
| sem forma | 0,0479/0,1783 **F** | 0,0759/0,1319 **F** |
| **rampa** | **0,0243/0,0521 P** | **0,0137/0,0542 P** |
| **CLIFF** | 0,0479/0,1783 **F** | 0,0759/0,1319 **F** |

**B0 também passou, e com precisão notável:** o res.máx da rampa difere **3,9 %**
entre 15 e 124 pontos, contra os **4,0 %** que a conta de satisfazibilidade
previu no pré-registro. A dependência de amostragem que matou a 2ª tentativa
(27,5× em `Δ_col`) está resolvida — a banda usa o dado **interpolado** e uma
janela derivada de **um número por curva**.

**Bloco C — a pergunta que motiva a linha inteira:**

> As 16 curvas trimadas, pontuadas na curva **INTEIRA** sob a banda:
> **10 de 16 passam** o tripé. Sob a métrica de nível eram **0 de 16**.

Passam: `liu2025` amp0p25 · amp0p3 · amp0p6 · amp0p8 · `yang2021` amp1p0 ·
amp0p6_r1 · amp0p7 · amp0p5 · `li2022ti` full · `sun2025` nogrease_crimp.
Falham: `liu2025` amp0p4 (0,1547) · amp0p5 (0,1706) · fig2 (0,1783) ·
`yang2021` fig2_typical · amp0p8 · `sun2025` nogrease_standard.

Meta nas janelas de hoje: **147 → 154**.

---

## 2. Por que morre assim mesmo

**B3 — uma virada com banda estreita.** `chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9`
foi de 0,0449/**0,1173** para 0,0319/**0,0949**, com largura de banda **0,0443**
no ponto crítico — abaixo do 0,05 exigido. É uma virada de baixo conteúdo:
falhava por 0,017 e passa por 0,005, sobre uma banda de 0,044. **O gate fez
exatamente o que foi escrito para fazer** — impedir que a métrica compre curvas
no limiar.

**B6 — e aqui o defeito é MEU, não da métrica.** Duas curvas "planas" mudam mais
que 0,005: `liu2022_fig8_multi_t4` (0,0098) e
`karlsen2022_M42_vibralock_torqued_run29p0` (0,0078). Mas eu defini *plana* como
**largura de banda < 0,02** e a tolerância como **0,005** — e uma curva com
largura até 0,02 pode, por construção, mudar o res.máx em até 0,02. **As duas
cláusulas do próprio gate são incompatíveis entre si.** A conta de
satisfazibilidade que rodei usou duas curvas com largura minúscula e não expôs
a inconsistência.

Nota diagnóstica: as 3 curvas que reprovaram B3/B6 são **esparsas** (25, 7 e 9
pontos), não longas — `h_N` é 3 % da curva em todas. O problema não é janela
absoluta grande; é janela grande **relativa ao espaçamento entre pontos**.

---

## 3. A lição de processo — e ela é sobre mim, pela terceira vez

Três pré-registros, três defeitos de autoria de gate:

| tentativa | defeito do gate |
|---|---|
| 1ª (§4.45) | **M0 insatisfazível** — exigia identidade exata de uma forma só assintoticamente idêntica |
| 2ª (§4.46) | **N2 com premissa errada** — a conta foi feita de cabeça e errou por 45× |
| 3ª (esta) | **B6 internamente inconsistente** — o escopo (< 0,02) admite mais variação que a tolerância (0,005) |

A regra que criei depois da 1ª (*"todo gate carrega a conta de
satisfazibilidade"*) pegou o caso 2 quando a rodei numericamente — mas **não
pega o caso 3**, porque a conta valida o gate contra *um caso*, não contra
*si mesmo*.

> **Reforço proposto da regra:** a conta de satisfazibilidade tem de incluir o
> **pior caso admitido pelo próprio escopo do gate** — não um exemplo. Se o gate
> diz "para curvas em que X < a, exigir |Δ| ≤ b", é preciso verificar que
> **X = a** ainda produz `|Δ| ≤ b`. Um gate cujo escopo admite violação do
> próprio critério não é um gate, é uma armadilha.

---

## 4. Estado final

Revertido: `runner.py` ao canônico (nunca commitado); store restaurado —
**0 divergências** nos campos verticais nos 203; fingerprint `4f5bedfbace4`;
meta segue **147/202**.

Preservado: este documento, `metrica_banda_gates.py`, `metrica_banda_result.json`,
`metrica_banda_batch.log`, e o pré-registro congelado.

---

## 5. O que isto deixa para decidir

**A linha NÃO fechou** — o B1 ✗ é que a fecharia, e ele passou. O que morreu foi
**esta parametrização**, por dois defeitos de **limiar**, um deles meu:

- **B3**: uma virada marginal com banda de 0,0443. Pergunta aberta: o limiar
  0,05 estava certo e a métrica é permissiva demais nas esparsas, ou o limiar
  era arbitrário?
- **B6**: gate internamente inconsistente — precisa ser reescrito coerente,
  não relaxado.

**Sinal favorável que uma 4ª tentativa herdaria:** B0, B1, B2, B4 e B5 passaram,
e o Bloco C deu **10 de 16** — o único número em toda a linha que justificaria
remover trims. Uma 4ª tentativa mudaria o mínimo: `h_N` sensível ao
**espaçamento entre pontos** (não só a `N_fim`), B6 reescrito coerente, B3
mantido como está.

**Sinal desfavorável, dito com o mesmo peso:** é a 3ª tentativa, o autor errou o
gate nas 3, e a métrica é **unilateral** (só melhora números) — o que exige
gates ainda mais duros, não menos. Há um argumento honesto para **parar aqui** e
aceitar que essas curvas fiquem fora da meta com o trim por julgamento humano,
que é a posição registrada em §4.46a.

**Decisão do professor.** Não inicio a 4ª sem sua palavra.
