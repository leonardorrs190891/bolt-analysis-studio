# Estudo Chu 2026 (Tribol. Int.) — a fonte ganhou anatomia, procedência e um veredicto honesto: segue form-limited, agora com a forma NOMEADA pela própria fonte

**Data:** 2026-07-28 · **Molde:** estudo Liu (paper integral → anatomia → confronto → contas)
**Custo de preregs: ZERO** — a receita candidata morreu nas contas de projeto, antes de congelar.
**Artefatos:** sondas `kernel_f0slip_sonda.py` (§2) e `chu_mu_implicito.py` (§3), contas de projeto (§5).

> ## ⚠ ERRATA (2026-07-28, mesma noite — três erros do MESMO método, corrigidos)
>
> Este estudo partiu de uma contagem de diretório em vez de perguntar ao registry —
> **exatamente o gotcha que o CLAUDE.md já registrava** ("NÃO conte notas de aparato
> listando aquele diretório"). Três afirmações caíram:
>
> 1. **"Nota de aparato NOVA (não existia)" — FALSO.** `chu2026ti.md` existe desde a
>    Rodada 4 em `BAS_V2_papers/E.../apparatus_notes/` (é a que o registry resolve), e é
>    MAIS completa que a que escrevi (rig, matriz, caveats de digitalização ponto a
>    ponto, inconsistências Table-1-vs-figura). A duplicata que criei foi **removida**.
> 2. **"Fig. 5 não digitalizada" — FALSO.** Digitalizada em **2026-07-15**: 5 CSVs
>    µ_plate(N) (`digitized_csv/chu2026ti_fig5_muplate_test{1,2,4,7,8}.csv`); tests
>    3/5/6/9 não têm COF no paper (limite estrutural, não lacuna nossa).
> 3. **A rota de destravamento (i) que propus JÁ FOI TENTADA — e falhou o gate.**
>    Prereg **F3.2-CHU** (2026-07-21, `docs/superpowers/specs/2026-07-21-master-f3-preregs.md`):
>    o encanamento `mu_bearing_schedule` foi construído (default-inerte, bit-idêntico) E
>    a adoção per_case (schedules medidos test2/4/7/8 + floors lidos + receita F3) rodou
>    o gate G-CHU-a: **FAIL** (test4 0,183/0,284; test2 0,170/0,569; test7 0,148/0,291;
>    test8 0,155/0,398 — nenhum fecha; `f3_chu_result.json`). O prereg permite **máx. 2
>    tentativas** ⇒ **resta 1**, e ela só deve ser gasta se contas de projeto isolando o
>    schedule da receita F3 (que carregava c_bend=1,881/C_creep=0/emb 1,6µm juntos)
>    mostrarem G-CHU-a satisfazível. §7 abaixo registra essa medição.
>
> A conclusão central do estudo **sobrevive** (a fonte é form-limited; µ(t) é real e
> tem os dois papéis) — mas a fronteira correta é: *µ(N) MEDIDO e PRESCRITO já foi
> necessário-mas-insuficiente uma vez; o resíduo é a taxa de colapso do kernel.*

---

## 0. Errata de partida

**"ti" nos case_ids é *Tribology International*, não titânio.** O rig é superliga:
parafuso **GH159**, porca MJ10 12-pontos + placa **GH4169**, rosca interna **prateada**
(µ_thread ≈ 0,05 selecionado pelo paper), Junker ISO 16130 a 10 Hz.

## 1. O que o paper é (e o que ele entrega de dado)

Experimentos + FEM em contexto de rotor de turbina. Tese: o mecanismo dominante é o
**torque de afrouxamento assimétrico acumulado** na interface **porca–placa** (assimetria
estrutural), com **limiar crítico de deslocamento** dependente de F₀ e atrito, e **dois
regimes** — em carga baixa o atrito governa; em carga alta a carga vence. Conclusão
central para nós: **F₀ regula o afrouxamento de longo prazo indiretamente, via evolução
do COF e do wear** — e o próprio FEM do paper diverge do ensaio, nas palavras deles,
pela natureza **tempo-dependente do coeficiente de atrito**.

**Dados com procedência que o paper entrega:** matriz com **N₉₀ por curva** (cycles to
0,9·F₀: 278/325/406/72/54/1050/936/180 — a mesma classe do N_f do Liu/E2); limiar
experimental D ≤ 0,3 mm @49 kN; **Fig. 5 = COF MEDIDO evoluindo durante a vibração**
(não digitalizada — candidata a âncora quantitativa futura).

## 2. Anatomia medida (sondas de hoje)

- **Gross-slip profundo:** slip **constante** (s_slip ≈ 0,001) em 0,4–0,7 mm ⇒ a perda
  slip-driven do modelo cai ∝ F₀ puro.
- **Três cinéticas no mesmo rig:** test3 acelera (p=−0,42), test7 desacelera (+0,83),
  test4 desacelera forte (+2,53) — regime dependente de amplitude dentro da fonte.
- **µ implícito no dado confirma a Fig. 5:** no test2 (a curva que o paper destaca)
  µ_impl sobe **9,3×** (slope +1,86); test3 6,0×; ordenação em 0,4 mm com 49 kN
  subindo ≫ 61/73 — como o paper prevê. No test4, a taxa colapsa (arresto): µ como
  **resistor** vencendo — os dois papéis do µ (driver de wear × resistência ao
  torque) aparecem separados nos dados.

## 3. O gap de config, documentado (e por que ele NÃO explica sozinho)

8 das 9 curvas rodam **sem chave per-rig**: µ=0,15 default (paper: 0,05 rosca /
~0,2 apoio), **passo 1,50** no registry (paper: MJ10×**1,25**), **E=200** (paper: 189),
overrides `{}`. Só o `test1` (limiar) tem adoção (PR-38: `c_D=5,5, k_dmg_mu=−2,43,
W_ref=1e4` — µ **subindo** com o dano, o sinal per-par da L7 confirmado pela Fig. 5).

## 4. A receita candidata mais limpa — e as contas que a mataram

Candidata: **estender o trio PR-38 ao grupo + correções de procedência** (zero fit
novo). Contas de projeto em 2 curvas (6 cegas), contra o store:

| curva | store | A: µ_thread=0,05 | B: A+trio PR-38 | C: B+c_bend/emb F3 |
|---|---|---|---|---|
| test2 (0,4/49) | 0,154/0,464 | 0,166/0,486 **pior** | 0,183/0,552 **pior** | 0,203/0,637 **pior** |
| test3 (0,5/49) | 0,138/0,174 | 0,136/0,176 ≈ | 0,083/0,142 melhor, F | 0,033/0,229 MAE↓ pico↑ |

**Veredicto: a receita NÃO congela.** O trio do limiar não transfere para as curvas que
soltam — µ subindo arresta o modelo, mas o **test2 real perde tudo** (regime 2: a carga
vence o atrito que sobe). Um `k_dmg_mu` único não carrega os **dois papéis** do µ nos
**dois regimes**. (O F3 de 21/07 já havia falhado gate pela via dos floors — segunda
via morta.)

## 5. Estado final da fonte e a forma NOMEADA — *(§5 original; ver errata no topo e o §7)*

- **CHU_2026 segue form-limited (6 violadoras)** — com a forma nomeada **pela própria
  fonte**: *acúmulo de torque assimétrico na interface porca–placa com µ(t) medido
  evoluindo e dois regimes em carga*.
- ~~O que destravaria: (i) digitalizar a Fig. 5~~ **ERRATA: já estava digitalizada
  (2026-07-15) e já foi prescrita 1× dentro do F3.2-CHU — FAIL.** Ver §7.
- Correções de procedência (µ_thread/pitch/E) ficam **registradas mas não adotadas** —
  sozinhas são ~neutras (variante A) e adoção parcial sem ganho de gate só mexeria
  fingerprint.

## 7. FECHAMENTO (mesma noite): três famílias falsificadas COM o µ medido em mãos — o resíduo é o kernel temporal, provado no nível de lei

Depois da errata, as duas medições que faltavam (`chu_schedule_isolado.py`,
`chu_energywear_sonda.py`):

**(a) O schedule isolado é quase inerte** — separado da receita F3 (que o embrulhava
com c_bend=1,881/C_creep=0/emb 1,6 µm), o µ(t) medido prescrito sobre os defaults dá
|Δ| ~0,01 nas 4 curvas (test2 0,165/0,483; test4 0,115/0,273; test7 0,148/0,262;
test8 0,165/0,298 — G-CHU-a insatisfazível em A/B/C). **Causa, e é fato de engine:**
em disp-mode o wear é **Archard (`K/H·p·slip`), sem µ** — o canal que carrega 93 % da
perda do Chu é por construção cego ao µ(t) que o paper mede; µ só alcança arresto/
rotacional (~7 %) e dano (desligado). A 1ª tentativa do F3.2 não falhou "pela
receita": **falharia de qualquer jeito**.

**(b) Recolorir a LEI também morre — inclusive na âncora.** Wear energético
(`d_wear = k_E·µ_medido(t)·p·slip`, emulado bit-exato mutando `k_wear_spec` por ciclo,
K_archard=0): varredura 1D de k_E no test4 dá **0,118/0,249 no melhor ponto**
(k_E=2–3e-13) — nem a curva de projeto fecha; transferência zero-refit nas 3 cegas:
0/3, todas piores que o store. Protocolo anti-FAIL1 respeitado (âncora onde o
mecanismo é ativo; cegas declaradas antes).

**Veredicto final, três degraus de prova:** (1) µ-livre (Archard, estado atual) não
reproduz; (2) µ medido prescrito não muda; (3) lei µ-acoplada com µ medido não fecha
nem onde foi ancorada. ⇒ **O resíduo do Chu não é o µ e não é a lei de wear — é a
estrutura temporal do kernel de colapso** (test3 acelera, test4/7/8 desaceleram, com
slip constante e µ conhecido). O único candidato restante é o canal do próprio paper
— torque acumulado `M⁻=(F₀/ξ)^a·(N^b+η)` com **b=1,65 superlinear em N** (acumulação
explícita no relógio, estrutura que NENHUM mecanismo estado-dirigido nosso tem) — mas
instanciá-lo pede ≥3 constantes per-rig sobre 4 curvas = **não-adotável sob
parcimônia**. A 2ª tentativa do F3.2 **não foi gasta** (contas insatisfazíveis = o
ramo "documenta e fila" do próprio prereg).

**Recomendação à fila:** CHU_2026 (test2/3/4/7/8/9) = form-limited **com prova em
nível de lei** — candidato natural a exceção assinada na próxima ratificação;
reabrir só se outra fonte exibir a mesma assinatura de aceleração N-explícita
(test3-like), o que tornaria o canal de acumulação testável cross-rig.

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/chu_mu_implicito.py          # mu implicito por curva (§2)
py -3.12 New_Theory/kernel_f0slip_sonda.py       # slip/taxas por canal
py -3.12 New_Theory/chu_schedule_isolado.py      # §7a: schedule isolado (A/B/C)
py -3.12 New_Theory/chu_energywear_sonda.py      # §7b: lei energetica, ancora+cegas
# contas de projeto (§4): bloco inline no historico da sessao (2 curvas x 3 receitas)
```
Nota de aparato canônica (registry): `BAS_V2_papers/E. Rodada 4 (…)/apparatus_notes/chu2026ti.md`
(inclui §Fig. 5 digitalizada). A duplicata `curve_library/apparatus_notes/chu2026_triboint.md`
foi removida (errata).

## 8. Adendo 2026-08-13 — a campanha re-testou com as formas NOVAS; o veredicto §7 SOBREVIVE e ganha 4 falsificações

Prereg `docs/superpowers/specs/2026-08-13-chu2026-calibracao-prereg.md` (3 rodadas
de grade declarada, gates G1–G4 congelados, baseline re-medido ~neutro vs store):

1. **k_wear_spec uniforme** (rodada 1) — menor dose fecha test5 e explode test3.
2. **Running-in** (`k_wear_running`/`N_wear_run`, forma pós-estudo) — menor dose
   derruba census 2/8→0/8; gradiente de piora monotônico. O modelo já perde
   rápido demais CEDO: qualquer forma front-loaded piora.
3. **Ratchet cinemático** (`k_ratchet`×`loose_amp_exp`, PR-21) — catastrófico na
   escala de gross-slip do rig (drena 10²–10³ N/ciclo já em k=0,005).
4. **Incubação × chute tardio** (`slip_onset_W` × `k_late_amp`+`crash_trigger_frac`,
   emenda PR-3) — **cada curva fecha isolada** (test3 0,0402 PASS com W=4000;
   test5 0,0100 com W=1500+k=2), mas os ótimos são disjuntos por 10× em W.

Leitura estrutural que fecha o caso: onset e taxa de colapso são função explícita
de (D, F₀) — a lei M⁻ do paper — e a M⁻ publicada não tem eixo de D. O resíduo
segue sendo o kernel temporal, agora com a prova adicional de que **nem supressão
+amplificação estado-dirigidas com constantes compartilhadas o reproduzem**.
Teto da fonte: **3/9** (test1+test5+test6). Recomendação §7 (exceção assinada
p/ test2/3/4/7/8/9) REITERADA com dossiê reforçado.

## 9. Capstone (2026-08-14) — a lei M⁻ do próprio paper reprova no teto de autoridade

Rodada 4 (prereg G0 congelado antes): M⁻=(F₀/ξ)^1,85·(N^1,65+30) com o
µ_plate(N) MEDIDO (5 CSVs) contra o T_res do rig — ordenação das vidas
INVERTIDA ([8,7,2,4] vs [2,4,8,7] do dado), razões até 4,65× (gate 2×), e o
test1 abaixo do limiar cruza onde o dado é plano. Robusto a unidade e a µ_th.
A prova form-limited da fonte fecha em **5 degraus** (ver prereg §rodada-4);
o teto 3/9 é definitivo sob qualquer forma hoje nomeável — inclusive a do
próprio autor.
