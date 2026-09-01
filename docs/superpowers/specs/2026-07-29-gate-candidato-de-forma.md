# Template de GATE para candidato de FORMA (régua de 3 pernas)

**Escrito em 2026-07-29, antes de qualquer candidato ser medido** — que é a
condição para ele valer. Um gate escrito *depois* da medição é cerimonial, e a
campanha já pagou por isso uma vez (§4.44: o prereg v1 da rampa do Liu teve os
gates medidos antes de assinar e virou inútil como pré-compromisso).

**Para que serve:** o pipeline vai propor formas novas para a fila de 51 curvas
que violam o σ_res. Este documento diz o que cada proposta tem de prometer
**antes** de rodar, e o que a derruba. Copie a §5 para o prereg do candidato,
preencha os alvos, congele em commit, e só então meça.

---

## 1. Por que um gate só de MAE não serve mais

A régua tem três pernas (`res.máx ≤ 0,10 · MAE ≤ 0,05 · σ_res ≤ 0,025`) e a que
reprova é a terceira: **30 curvas violam SÓ o σ_res** e **zero** violam só o
res.máx. Três medições de 2026-07-29 delimitam o espaço de soluções:

- **Nenhuma das 18 alavancas existentes fecha a perna** (`sensitivity_sres`). As
  que têm magnitude são de NÍVEL (`emb_depth` move o MAE 3,7× mais que o σ); as
  de FORMA são 1–2 ordens fracas demais (precisariam de +355 % a +1 347 %).
- **O gap não é artefato de dado** (`sres_granularidade`): 46 das 51 têm o piso de
  granularidade abaixo de metade do limite.
- **A assinatura do resíduo PREDIZ onde um candidato morde**
  (`forma_residuo_classes` + `graded_scrit_alcance`): o `graded_scrit` melhorou as
  três pernas em 10 células, **todas** no cluster cuja assinatura casava, e
  **piorou** o caso cuja assinatura não casava.

Consequência: o gate tem de separar *"endireitou a rampa"* de *"consertou a
forma"*, senão um candidato que só remove deriva passa parecendo solução.

## 2. Os quatro números que todo candidato de forma declara ANTES

Para cada curva-alvo, o prereg declara o valor esperado e o ramo de decisão:

| # | grandeza | por que ela |
|---|---|---|
| **G1** | `Δσ_res` por curva | é a perna que reprova; sem queda aqui não há caso |
| **G2** | `Δσ/ΔMAE` | separa forma de nível. **< 1 reprova**: significa que o candidato está pagando o σ com MAE, que é o que `emb_depth` já fazia de graça |
| **G3** | `R²` da tendência linear do resíduo, **depois** | se o R² CAIU muito e o σ caiu pouco, o candidato só endireitou a rampa. Para o cluster ONDULADO (R² < 0,3) o gate exige **σ caindo com R² mantido baixo** |
| **G4** | contagem **Pareto** (curvas em que as TRÊS pernas melhoram ou empatam) | é o único número que impede troca disfarçada entre pernas |

## 3. Guardas obrigatórios (herdados de erros medidos)

1. **Nenhum caso piora mais de +0,01** em qualquer perna, em TODO o acervo — não
   só nos alvos (gate PR-37′). O `graded_scrit` piorou o `Yang2023 0,50` nas três
   pernas; sem varredura completa isso passaria.
2. **`Δ = 0` tem TRÊS significados** e o prereg tem de dizer qual está alegando:
   (a) nome que não é campo de `JointMaterial` — **bug**, confira contra
   `__dataclass_fields__`; (b) **gate de modo** — o campo é lido só num ramo, e o
   modo efetivo não o seleciona (`kb.inert_levers`); (c) **magnitude pequena** —
   grau de liberdade real e fraco. Só (c) autoriza conclusão sobre física.
   *Custou uma auditoria em 2026-07-29: `mu` não existe (são `mu_bearing`/
   `mu_thread`), `K_archard` está morto porque o `shared` adota `k_wear_spec`, e
   `slip_regime_sharpness` é gate de modo — quase congelado por engano.*
3. **Constante nova exige procedência ou vira dívida declarada.** Se o melhor
   valor variar entre curvas da MESMA fonte, é constante por-curva, não física
   compartilhada — declare isso (o `k_loose_graded` varia 1e-3…1e-1 dentro do
   CHU).
4. **Comparar com o PISO da fonte, não com zero.** Curva cujo erro cabe no piso
   medido de repetibilidade (F7) está **pronta**, não imperfeita. E piso alto
   sozinho **não** absolve: só absolve quem cabe dentro dele (erro medido em
   2026-07-29, atividade E).
5. **σ_res com menos de 6 pontos não é julgável.** Três aprovações atuais repousam
   sobre 4–5 pontos; um candidato não pode ser creditado por mover σ_res ali.
6. **Store e `adopted_configs.json` intocados** durante a medição. Probe é
   só-leitura; adoção é passo separado, com gate próprio e re-carimbo do batch.

## 4. Ramos de decisão (escreva-os ANTES, com o número)

O prereg tem de ter um ramo para cada resultado possível — inclusive os
desconfortáveis. Modelo mínimo:

- **PASSA** — G1 negativo nos alvos, G2 ≥ 1, G4 ≥ (nº de alvos), guardas 1–6 ok
  ⇒ segue para adoção gateada (que é outro documento).
- **PARCIAL** — melhora Pareto num subconjunto e é neutro no resto ⇒ o candidato é
  **componente**, não solução; registrar como tal e NÃO adotar sozinho. *É onde o
  `graded_scrit` caiu.*
- **TROCA** — σ_res cai mas G2 < 1 ⇒ **falha**. Não relatar como progresso: é a
  mesma troca que uma alavanca de nível faz sem forma nova.
- **COSMÉTICO** — R² cai, σ_res quase não ⇒ **falha**. Endireitou a rampa e
  deixou o defeito.
- **PIORA** — qualquer caso além de +0,01 ⇒ **falha**, com o caso nomeado.

## 5. Bloco para copiar no prereg

```markdown
### Gate do candidato <NOME> (congelado em <commit>, ANTES de medir)
Alvos: <case_ids>  ·  Classe da assinatura: <DERIVA | ONDULADO | mista>
Mecanismo alegado: <uma frase física>  ·  Constantes novas: <nome: procedência>

G1 Δσ_res esperado por alvo: <valores>            (queda mínima aceita: <v>)
G2 Δσ/ΔMAE >= 1 em <n> dos <N> alvos
G3 R² depois: <esperado>; para alvos ONDULADO o R² fica < 0,3
G4 Pareto (3 pernas melhoram/empatam) em >= <n> alvos
Guardas: nenhum caso do acervo piora > +0,01 · "Δ=0" classificado (a/b/c) ·
         procedência declarada · comparado ao piso da fonte · n >= 6 pontos ·
         store intocado
Ramos: PASSA / PARCIAL / TROCA / COSMÉTICO / PIORA -> <ação para cada um>
```

## 6. O que já se sabe sobre os alvos (não precisa re-medir)

> **Esta seção é BACKGROUND factual, não gate — e foi corrigida em 2026-07-29 (noite),
> depois da atividade F.** Os critérios **G1–G4 da §2 e os ramos da §4 não foram
> tocados**: mexer neles depois de medir seria mover a trave, que é exatamente o que
> este documento existe para impedir. O que mudou aqui foi um **número retratado** —
> a tabela dizia "sobra σ_res ≈ 0,11 e domina", herdado de um erro de célula no
> relatório da atividade B (detalhe em `graded_scrit_alcance_resultado.md`, seção ⚠️).
> Um gate que carrega um fato falso desvia o próximo prereg em vez de discipliná-lo.

| cluster | curvas | assinatura | estado |
|---|--:|---|---|
| **DERIVA** | 16 | resíduo em rampa (R² ≥ 0,7); CHU ×3 com β ≈ +0,58 | orçamento **medido** (atividade F): 53 % rampa + 16 % curvatura + 31 % resto; **12 das 16 passariam a 3ª perna** se as duas formas fossem capturadas. O `graded_scrit` trata a rampa mas **nenhuma célula dele a remove sem triplicar o MAE** ⇒ é componente. A 2ª forma é **curvatura lisa** (joelho adiantado) que **ordena pela amplitude** ⇒ candidato nomeado: incubação `slip_onset_W` (no engine, desligada) |
| mista | 23 | rampa + ondulação | LU_2024 ×5, YANG_2023 ×4, LIU_2016 ×4 |
| **ONDULADO** | 18 | R² < 0,3 — nenhuma constante remove | LU_2024 ×5, LIU_2025 ×2, YANG_2019 ×2 |

Caveat nomeado: `10_Yang_2023…0_45_mm` tem ruído de dado (0,0363) **acima** do
limite do σ_res — nem modelo perfeito passa ali. Não é exceção; é limite
declarado, e nenhum candidato deve ser cobrado por ela.
