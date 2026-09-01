# Pré-registro — MÉTRICA DE BANDA v2 (4ª tentativa da linha)

**Data:** 2026-07-28 · **Autorização:** professor, *"autorize a 4ª tentativa"*
**Antecessora:** `2026-07-28-metrica-banda-prereg.md` (3ª, morta no B3 — §4.47)
**Fingerprint:** `4f5bedfbace4` · **Status:** PROPOSTO — gates IMUTÁVEIS depois de assinados

---

## 0. Declaração de perda de cegueira — leia antes dos gates

Para desenhar esta versão testei **três** variantes de correção no caso de
referência (`fig2_single`, nas duas digitalizações) **antes** de congelar:

| variante | resultado no caso de referência |
|---|---|
| **cap por espaçamento** (`h_N ≤ 0,5·gap`) | **ELIMINADA** — inverte o efeito: na curva fina o colapso tem 35 pontos em 15 ciclos, o espaçamento ali é ~0 e a janela **desaparece justamente onde é necessária**. A rampa cai de 0,0542 para **0,3371** e o veredicto passa a depender da densidade (0,0521 vs 0,3371) ⇒ quebraria B0 **e** B1 |
| **v4b** (interpolada, exige ≥2 pontos **medidos** na janela) | **ESCOLHIDA** — B0 3,7 %, B1 preservado |
| **v4c** (só pontos medidos) | equivalente em veredicto, menos estável na magnitude (2× vs 1,35× entre digitalizações) |

**Consequência, dita sem rodeio:** o `fig2_single` **deixou de ser teste cego** e
virou **caso de projeto**. Os gates C2 e C3, que rodam nele, valem como
verificação de implementação — **não** como evidência independente. Para
recuperar cegueira, o gate de discriminância que de fato conta é o **C4**, no
núcleo `amp0p4/0p5/0p6`, que **não foi usado no desenho e cuja conta NÃO foi
rodada**.

---

## 1. O que muda em relação à 3ª tentativa

A 3ª morreu no **B3** (uma virada marginal com banda estreita, 0,0443 < 0,05) e
reprovou o **B6** por defeito de autoria (escopo `< 0,02` incompatível com
tolerância `0,005`). Diagnóstico: as 3 curvas culpadas são **esparsas** (25, 7 e
9 pontos) — a janela interpolava por cima de segmentos **não medidos**, criando
banda onde não há variação medida.

**Correção única, na forma:** a banda passa a exigir **evidência medida**.

```
h_N   = FRAC_N * N_fim                       FRAC_N = 0.03  (input-de-paper)
S_i   = pontos MEDIDOS com |N_j - N_i| <= h_N
|S_i| < 2  ->  banda = [r_i, r_i]      => resíduo = |Δr| EXATO (métrica de hoje)
|S_i| >= 2 ->  banda = [min,max] do dado INTERPOLADO na janela (grade de 64)
resíduo_i = 0 dentro da banda; senão a distância à borda mais próxima, em N_i
```

Ou seja: **onde a janela não alcança nenhum ponto vizinho medido, não há
variação medida a invocar, e a métrica é a de hoje, exatamente.** Nada mais
muda: `FRAC_N`, o limiar do C6 (0,05, herdado do B3 **sem relaxamento**), a
ausência de dilatação vertical, e a avaliação em `N_i` seguem idênticos.

### 1.1 Custo de implementação — e por que não há varredura

A banda precisa do modelo **apenas nos ciclos do dado**, que é exatamente o vetor
`metric_pred` já gravado no store desde o conserto de 2026-07-27. Logo esta
tentativa é **100 % computável do store**: **nenhuma linha de código canônico é
tocada e não há re-simulação** (as três anteriores gastaram 25 min de varredura
e um ciclo de reversão cada, desnecessariamente). Só o **Bloco D** (curvas sem
trim) exige simular — 16 curvas.

### 1.2 Risco herdado, declarado de novo

`r_i` pertence sempre à banda ⇒ `resíduo ≤ |Δr|` em todo ponto: a métrica é
**unilateral**, só pode melhorar números. "Melhorou" não é evidência de nada;
C5/C6/C7 atacam o *onde*.

---

## 2. GATES — cada um com a conta, cobrindo o PIOR CASO DO PRÓPRIO ESCOPO

> **Regra reforçada (§4.47), aplicada:** não basta a conta num exemplo; é preciso
> verificar o **extremo admitido pelo escopo do gate**. Foi a ausência disso que
> produziu o `B6` auto-inconsistente da 3ª tentativa.

**C0 — nada de canônico é tocado.** `git status` em `src/` e no store deve ficar
limpo ao fim. *Conta:* a métrica é pós-processamento do store ⇒ ✔ por construção.

**C1 — inércia EXATA onde não há vizinho medido.** Em todo ponto com `|S_i| < 2`:
`|resíduo_banda − |Δr|| ≤ 1e-12`. *Pior caso do escopo:* qualquer ponto assim tem
banda `[r_i, r_i]`, logo o resíduo é `|pred − r_i|` **literalmente** ⇒ igualdade
exata, não assintótica. ✔ satisfazível (diferente do `M0` da 1ª tentativa).

**C2 — invariância à amostragem.** `fig2` em 15 vs 124 pontos: veredictos
idênticos e res.máx da rampa dentro de 20 %. *Conta rodada:* **0,0546 vs 0,0567
= 3,7 %**, veredictos F/P/F em ambas. ✔ — **mas é caso de projeto** (§0).

**C3 — discriminância no `fig2`.** Rampa passa; cliff e sem-forma falham, nas
duas digitalizações. *Conta rodada:* rampa 0,0285/0,0546 (P) e 0,0138/0,0567 (P);
cliff 0,0520/0,1783 (F) e 0,0760/0,1319 (F). ✔ — **caso de projeto** (§0).

**C4 — DISCRIMINÂNCIA CEGA no núcleo `amp0p4` / `amp0p5` / `amp0p6`.**
*Critério:* nas três curvas, com o par (`D_on`=0,75, `q`=8) e **sem trim**, a
**rampa** deve passar o tripé em pelo menos **2 das 3**, e o **cliff** deve
falhar nas **3**. *Conta:* **NÃO RODADA — este é o gate cego, e é ele que vale
como evidência.** Não há inconsistência de escopo: o critério é sobre 3 curvas
nomeadas, sem cláusula condicional.

**C5 — não é afrouxamento cego.** Mediana da melhora em res.máx nas 202 < 0,005.
*Conta:* na 3ª tentativa deu **0,00374** com bandas **mais largas**; o v4b só
estreita ⇒ a mediana só pode cair. ✔ satisfazível, e segue falseável.

**C6 — toda virada exige banda LARGA (> 0,05) no ponto crítico.** *Herdado do B3
sem relaxamento.* *Conta:* a curva que o reprovou na 3ª tentativa
(`chu2026ti_..._test9`) tem **25 de 25 pontos sem vizinho medido** sob v4b ⇒
banda zero ⇒ resíduo idêntico ao vertical ⇒ **não vira mais**. ✔ — e o gate
continua podendo falhar por outra curva.

**C7 — o ganho é concentrado, não difuso.** Em toda curva, a fração de pontos
cujo resíduo muda mais que 0,005 deve ser **< 50 %**. *Escopo:* todas as curvas,
sem cláusula condicional ⇒ **sem inconsistência interna possível**;
satisfazibilidade é a pergunta empírica que o gate faz. *(Substitui o `B6`
auto-inconsistente: o antigo definia "plana" por largura < 0,02 e exigia
|Δ| ≤ 0,005, e largura 0,02 admite Δ de 0,02.)*

**C8 — teto de 25 viradas.** Ponto de parada obrigatória, não critério.

**C9 — fingerprint inalterado** (`4f5bedfbace4`). ✔ por construção (C0).

### Bloco D — a pergunta que motiva a linha (medição declarada, não gate)

As **16 curvas com `trim_n_max`**, pontuadas na curva **inteira** sob a banda v4b.
Referências: **0 de 16** sob a métrica de nível; **10 de 16** sob a banda v1.

### 2.1 Interpretação pré-declarada

| resultado | leitura |
|---|---|
| C0–C3, C4, C5–C7, C9 ✓ e C8 ✓ | métrica **adotável**; Bloco D vira insumo da decisão sobre os trims |
| **C4 ✗** | o gate cego reprova ⇒ a discriminância do `fig2` era artefato de projeto ⇒ **a linha fecha em definitivo** |
| **C6 ✗** | ainda há virada de baixo conteúdo ⇒ **morre**; 4 tentativas bastam |
| **C5 ✗** ou **C7 ✗** | é desconto disfarçado ⇒ **morre** |
| **C1 ✗** ou **C0 ✗** ou **C9 ✗** | bug; consertar e re-rodar sem reinterpretar gate |
| **C8 ✗** (> 25) | **PARAR** e reportar |

---

## 3. O que NÃO está sendo proposto

- **Não** relaxar o limiar do C6 (0,05) — seria mover a trave sobre a curva que
  matou a 3ª tentativa.
- **Não** mexer em `FRAC_N`, `align`, `FLOOR_TRIM`, `trim_n_max`, física ou
  fingerprint.
- **Não** remover trim algum (Bloco D é medição).
- **Não** tocar em `src/` (C0).
- **Não** haverá 5ª tentativa: se esta morrer, a linha fecha e a posição da
  §4.46a (trim por julgamento humano) passa a ser a resposta final.

---

## 4. Reprodutibilidade

```bash
py -3.12 New_Theory/metrica_banda_v2_gates.py     # C0-C9 + Bloco D (sem varredura)
```
