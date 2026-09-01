# Banda v2 (4ª tentativa) — o GATE CEGO reprovou. **A linha fecha.**

**Data:** 2026-07-28 · **Pré-registro:** `specs/2026-07-28-metrica-banda-v2-prereg.md`, gates **congelados em `af711b8`**
**Estado final:** nada a reverter — **nenhuma linha de código canônico foi tocada**, store intacto, fingerprint `4f5bedfbace4`, meta **147/202**

---

## 0. Veredicto

| gate | resultado |
|---|---|
| C1 inércia exata sem vizinho medido | **OK — 0,00e+00** em **1952** pontos |
| C2 invariância à amostragem | OK — 3,7 % (previsto 3,7 %) · *caso de projeto* |
| C3 discriminância no `fig2` | OK · *caso de projeto* |
| **C4 DISCRIMINÂNCIA CEGA no núcleo** | **FALHA — rampa 0 de 3** |
| C5 não é afrouxamento cego | OK — mediana **0,00000** |
| C6 virada exige banda larga | OK (4 viradas, larguras 0,055–0,45) |
| **C7 ganho concentrado** | **FALHA — 36 curvas com >50 % dos pontos alterados** |
| C8 teto de viradas | OK (4) |
| C9 fingerprint | OK |
| C0 nada de canônico tocado | **FALHA — mas por causa externa** (§3) |

**Ramo pré-declarado:** *"**C4 ✗** ⇒ o gate cego reprova ⇒ a discriminância do
`fig2` era **artefato de projeto** ⇒ **a linha fecha em definitivo**."*
E o prereg declarou: *"**Não** haverá 5ª tentativa."* **Cumprido: a linha fecha.**

---

## 1. O gate cego, e por que ele vale mais que os outros nove

O §0 do pré-registro declarou, antes de medir, que o `fig2_single` havia deixado
de ser teste cego — três variantes de correção foram testadas nele. Por isso C2 e
C3 foram rotulados **caso de projeto**, e a evidência real foi jogada no **C4**:
as três curvas do núcleo `amp0p4/0p5/0p6`, **nunca usadas no desenho**.

Medido, **sem trim**:

| curva | sem forma | rampa | CLIFF |
|---|---|---|---|
| amp0p4 | 0,0552/0,1547 F | 0,0388/**0,1476** F | 0,0552/0,1547 F |
| amp0p5 | 0,0457/0,1706 F | 0,0437/**0,3300** F | 0,0571/0,3300 F |
| **amp0p6** | **0,0340/0,1116** F | **0,0718/0,3300** F | 0,0594/0,3300 F |

**A rampa passa em 0 de 3** (critério ≥ 2). E em `amp0p6` a rampa é **pior que
não ter forma nenhuma** — 0,0718/0,3300 contra 0,0340/0,1116. A banda não
distingue nada no núcleo.

> **A discriminância que o `fig2` exibia era artefato de ter sido projetada
> nele.** Os gates C2/C3 passaram; o C4, cego, reprovou. É a demonstração mais
> limpa que esta campanha produziu de por que projetar e testar na mesma curva
> não vale nada — e ela só existe porque a perda de cegueira foi **declarada
> por escrito antes**, o que obrigou a criar um gate cego separado.

---

## 2. C7 mata independentemente

**36 curvas** têm **mais de 50 %** dos pontos com resíduo alterado — até **94 %**
(`UFU_13A_first_preload_decay`, `UFU_13A_def_preload_decay`), 85 %
(`UFU_5A_preload_decay`), 73 % (`liu2016wear_*`). O ganho é **difuso**, não
concentrado no colapso: é desconto disfarçado, exatamente o que o gate foi
escrito para pegar. Ramo pré-declarado: **morre**.

Note a coexistência aparentemente contraditória, e ela é informativa: **C5 passou
com mediana 0,00000** (a curva mediana não muda **nada**) enquanto **C7 falha em
36 curvas**. Ou seja, o efeito não é um desconto uniforme sobre todas — é
**concentrado num terço das curvas e difuso dentro delas**. As duas medições
juntas dizem mais que qualquer uma sozinha.

---

## 3. C0 — falhou por causa externa, e o gate era defeituoso

C0 pedia `git status` limpo em `src/`. Reprovou apontando
`calibration/knowledge_base.py` e `calibration/parameter_registry.py`. **Ambos
modificados às 13:10 pela sessão paralela** — esta tentativa é pós-processamento
puro e não toca `src/`; nenhuma commit minha existe depois do prereg.

**Mas o gate também está mal escrito:** ele testa o estado de uma *árvore de
trabalho compartilhada*, não uma propriedade da minha mudança. Num repositório
com duas sessões — hazard documentado no `CLAUDE.md` — isso nunca poderia ser um
teste válido. O certo seria enumerar os arquivos que **esta** tentativa toca
(nenhum).

**Quarto defeito de autoria de gate em quatro tentativas.** A regra reforçada da
§4.47 (*cobrir o pior caso admitido pelo escopo*) não pega este, porque o defeito
não está no escopo lógico e sim na **premissa ambiental**.

> **Segundo reforço da regra:** um gate tem de medir uma propriedade **da
> mudança**, nunca do ambiente em que ela roda. Se o critério pode ser
> violado por algo que o autor não fez, ele não é gate.

---

## 4. O que funcionou, e vale guardar

- **C1 exato: 0,00e+00 em 1952 pontos.** A conta de satisfazibilidade previu
  igualdade **literal** (banda `[r_i, r_i]` ⇒ resíduo `|pred − r_i|`) e foi isso
  que saiu. Contraste com o `M0` da 1ª tentativa, que pedia igualdade exata de
  uma fórmula só assintoticamente idêntica.
- **C2 acertou a previsão na casa decimal:** 3,7 % medido contra 3,7 % previsto.
- **C6 passou** — a correção "exigir evidência medida" removeu a virada marginal
  que matou a 3ª tentativa, como a conta antecipou (25/25 pontos de
  `chu2026ti_..._test9` ficam sem vizinho ⇒ banda zero ⇒ não vira mais).
- **Custo: segundos, e zero limpeza.** A percepção de que a banda só precisa de
  `metric_pred` (já no store) tornou a tentativa **pós-processamento puro** —
  sem varredura de 25 min e sem ciclo de reversão, ao contrário das três
  anteriores. **Método a reusar:** antes de patchear o runner, verificar se a
  métrica proposta é computável dos vetores que o store já guarda.

**Bloco D** (moot, mas registrado): 7 de 16 curvas trimadas passariam inteiras
sob a banda v4b — contra 10/16 da v1 e 0/16 da métrica de nível.

---

## 5. A LINHA FECHA — balanço das quatro tentativas

| # | forma | morreu por | causa raiz |
|---|---|---|---|
| 1 | resíduo ortogonal | **M2** discriminância | o **modelo** escolhia a correspondência; despencar era perdoado |
| 2 | correspondência de nível | **N2** discriminância | normalizador (`Δ_col`) **não invariante à amostragem**: 1100 vs 40 ciclos |
| 3 | banda v1 | **B3** virada estreita | janela interpolava sobre segmentos **não medidos** |
| 4 | banda v2 | **C4** discriminância **CEGA** + **C7** ganho difuso | a discriminância anterior era **artefato de projeto** |

Quatro pré-registros, quatro execuções, quatro reprovações — **três delas no
gate de discriminância**. Registro final:

> **Nenhuma métrica automática sobre curvas digitalizadas esparsas distingue a
> forma certa da forma errada no trecho de colapso quase-vertical.** O que existe
> ali é a moldura da figura, o scatter de espécime de 44 % e as escolhas do
> digitalizador. Toda métrica que "resolve" o problema o resolve perdoando
> também o cliff.

**A posição da §4.46a passa a ser a resposta final:** essas curvas são
**metric-limited**, ficam fora da meta por razão **metrológica**, e o
**`trim_n_max` aplicado por julgamento humano, documentado caso a caso**, é a
saída honesta — com a ressalva da §4.46 de que a regra que o descreve **não é
automatizável** (não é invariante à amostragem).

**Custo total da linha:** 4 preregs, 4 execuções, 3 varreduras de ~25 min, 3
reversões, **zero adoções** — e 4 defeitos de autoria de gate, cada um gerando
uma regra: (1) conta de satisfazibilidade; (2) cobrir o pior caso do escopo;
(3) medir a mudança, não o ambiente; e a mais cara de todas, (4) **um gate cego
vale mais que nove gates no caso de projeto**.
