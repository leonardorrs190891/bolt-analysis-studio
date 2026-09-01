# As 7 LEVEL-LIMITED — a leitura do piso NÃO fecha 6 delas

**Data:** 2026-07-28 · **Store:** `4f5bedfbace4` (snapshot do HEAD) ·
**Só-leitura: nenhuma simulação, nenhum fit, nenhuma adoção, nada escrito em
`adopted_configs.json` nem no store.**

Continuação direta de [`frontier_classes.md`](frontier_classes.md), que
classificou 7 das 55 curvas fora do tripé como **LEVEL-LIMITED** com a ação
"**ler o nível (`loose_arrest_floor`) com procedência — zero física nova**". Aquele
documento já declarou que a classe é **condição necessária, não prova**. Este
transforma a ressalva em número: **a leitura ingênua do piso move 3 das 4 leituras
sólidas na direção ERRADA.**

---

## 1. O teste

Para cada uma das 7, três coisas medidas de forma independente:

- **lido** — `arrest_floor_from_curve(ratio)` (`calibration/provenance.py`), o
  mesmo caminho canônico que o `validation/prefit.py` usa: média da cauda
  normalizada por `ratio[0]`, via `load_full_curve`;
- **aplicado** — o `loose_arrest_floor` que o store registra em `config_used`
  como de fato aplicado (não o que um `suggest_overrides` sugeriria);
- **direção necessária** — o sinal do `res.médio` do `frontier_classes`:
  positivo = o modelo retém **mais** que o dado ⇒ precisa de piso **menor**;
  negativo = retém menos ⇒ piso **maior**.

O leitor marca `plateau=False` quando a curva termina **em queda**; nesse caso o
valor é **limite inferior**, e comparar magnitude é inválido. Isso vale para 3 das
7, que ficam fora do veredicto.

| curva | lido | platô | aplicado | res.médio | precisa | a leitura aponta | coerente |
|---|---:|:--:|---:|---:|---|---|:--:|
| `chu2026ti_D0p3mm_F0_49kN_test1` | 0,9876 | sim | 0,0800 | −0,0663 | **maior** | maior | **✅** |
| `eccles2010_fig8a_no_axial_baseline1` | 0,0122 | sim | 0,0590 | −0,0426 | **maior** | menor | **❌** |
| `liu2016wear_fig7_run2_5e6cyc` | 0,6478 | sim | — | +0,0603 | **menor** | adicionar 0,65 | **❌** |
| `liu2020_fig9_zinc_AF0.4mm_P0-18kN` | 0,8351 | sim | — | +0,0729 | **menor** | adicionar 0,84 | **❌** |
| `bauer2024_M12_fig8_test3` | 0,2389 | **não** | 0,0800 | +0,0228 | menor | *limite inferior* | n/a |
| `lu2024_M8_fig20_T22Nm` | 0,0626 | **não** | 0,2100 | +0,0517 | menor | *limite inferior* | n/a |
| `rousseau2025_hdpe_t12` | 0,3395 | **não** | 0,2000 | +0,0572 | menor | *limite inferior* | n/a |

**Veredicto: 1 de 4** — e **este enunciado foi corrigido**, ver §1.1.

### 1.1 Correção pela reconciliação cruzada (commit `63dab38`)

Uma **segunda sessão** atacou esta mesma pergunta no mesmo dia, sem saber desta
(`level_seven_probe.md`), e **simulou** onde eu só pré-testei direção. O
cruzamento: **19 de 19 números compartilhados idênticos** (piso lido, piso
aplicado e `res.médio` nas 7, tolerância 5e-4), verificado **por script** contra os
dois JSONs — duas implementações escritas em separado dão o mesmo valor de
`arrest_floor_from_curve` e a mesma leitura de `config_used`. É o cruzamento mais
forte que a campanha já teve sobre um leitor de proveniência.

**Três correções ao que este documento afirmava:**

1. **O veredicto certo é "1 fecha de 6, e a direção acerta 6/6"**, não "1 de 4". O
   `plateau=False` invalida comparar **magnitude**, **não** direção — e as
   simulações mostraram que a direção acertou também nas 3 curvas que eu tirei do
   veredicto. Ou seja: o pré-teste de direção é **mais** forte do que eu concedi,
   e a conclusão de fundo não muda (ler o piso fecha **1** das 6).
2. **Falta um passo ANTES do teste de direção, e este documento tinha o dado na
   tela sem usá-lo:** a sonda imprimiu a coluna `pack` como `-` nas **sete**
   curvas, e o `loose_arrest_floor` é **inerte sem pack** (medido pela outra
   sessão: `delta = 0` exato no `liu2020`). Então em parte das 7 a alavanca pode
   estar **morta**, e "a direção está errada" seria o diagnóstico errado para
   "a alavanca não move nada". **Regra que fica: conferir que a alavanca está VIVA
   antes de conferir a direção** — e a evidência de vida é o pack na entry, não o
   campo no config.
3. **A anomalia de eixo (§3) não invalida resultado nenhum, e a razão precisa
   estar escrita:** `arrest_floor_from_curve` usa **só** `ratio`, e
   `emb_depth_from_curve` usa `cyc` apenas para gravar `prov["early_cycle"]`, não
   para o valor. Era o que eu tinha suposto sem verificar.

**Custo de coordenação, registrado:** duas sessões duplicaram o esforço. O que
salvou foi ambos os trabalhos serem **só-leitura** — a colisão custou tokens,
não integridade.

### 1.2 O universo correto é 6, não 7

[`replicate_impossibility_sweep_2026-07-28.md`](replicate_impossibility_sweep_2026-07-28.md)
provou que **`bauer2024_M12_fig8_test3` é inalcançável por qualquer curva** — ela é
uma de 3 réplicas da mesma condição (M12×1,5, 50 kN, espectro 80/150 µm) cujo teto
de passes é **0 de 3**. Ela não deveria estar neste conjunto: o problema dela não é
o nível, é scatter de espécime. Era, aliás, uma das 3 com `plateau=False` que já
tinham ficado fora do veredicto de direção.

O veredicto deste documento (**1 fecha de 6, direção acerta 6/6**) **não muda de
valor** — mas o universo correto das LEVEL é **6**, não 7.

---

## 2. Por que os dois sinais discordam — e o argumento é estrutural

`sobra = max|res − média(res)| < 0,10` diz que o erro é de **nível**: removido um
deslocamento **uniforme**, o pico entra no tripé. Mas o `loose_arrest_floor` **não
produz deslocamento uniforme** — ele é um piso de **arresto**, age na **cauda**.

Os dois casos mais claros são `liu2016wear` e `liu2020`: são curvas que **quase não
decaem**, então a cauda do próprio dado está alta (0,65 e 0,84) e o piso lido é
alto. Ao mesmo tempo, o `res.médio` positivo diz que o modelo **já retém mais** que
o dado. Adicionar um piso alto faz o modelo perder **menos** ainda — o oposto do
necessário. Os sinais não se contradizem por ruído: eles medem coisas diferentes
(o **nível final do dado** vs. o **erro do modelo ao longo da curva**).

Conclusão: para essas 6, o nível que está errado **não é o piso de arresto**. A
classificação LEVEL-LIMITED continua correta (o erro é de nível, não de forma); o
que **não** se sustenta é a ação prescrita.

---

## 3. Uma hipótese minha que a medição matou

Suspeitei que o leitor estivesse contaminado pelo **trim**: ele consome a curva
**crua**, enquanto a métrica só pontua até `trim_n_max` — a mesma doença já
documentada no report ("a métrica NÃO compara a curva crua"). Medido, ciclo do
platô lido vs. último ciclo da métrica:

| curva | N cru | N métrica | platô lido em N | fora do trim? |
|---|--:|--:|--:|:--:|
| `lu2024_M8_fig20_T22Nm` | 100 | 54 | 90 | **SIM** |
| as outras 6 | — | — | — | não |

**Apenas 1 das 7.** A hipótese não explica o resultado geral e foi descartada —
mas vale registrada por duas razões: ela é real naquele caso (o piso do
`lu2024_T22Nm` é lido de uma região que a métrica **não pontua**), e mostra que o
leitor de piso e a métrica não compartilham janela.

Anomalia de eixo achada de passagem: `eccles2010_fig8a` tem N cru **114** e N
métrica **225**, porque a fonte tem `csv_x_scale` (segundos→ciclos ×12,5) que
`load_full_curve` devolve sem aplicar. Não afeta o valor do piso (o leitor só usa
`ratio`), mas **afetaria** qualquer leitor que dependa do eixo x.

---

## 4. O que isto economiza, e o que fica

**Economiza uma rodada de adoção inútil.** A ação "ler o piso nas 7" parecia o
passo mais barato dos 19 que não pedem física nova. Executada às cegas, ela
pioraria pelo menos 3 curvas e produziria um gate FAIL cujo diagnóstico custaria
mais que esta medição.

**Fica aberto** — e agora com pergunta precisa: se o erro dessas 6 é de nível e
**não** é o piso de arresto, qual constante o governa? Candidatos, em ordem de
proveniência (nenhum testado aqui):

1. **assíntota de assentamento** (`emb_depth`) — é um **input** por junta (VDI
   2230, tabela f_Z por Rz), então "consertar o nível" por aqui exige a
   rugosidade do paper, não um ajuste;
2. **`tr_loose_gain`** — 2ª maior sensibilidade no tornado (0,123), mas é
   **forma** compartilhada: mexer nela per-rig é fit, não leitura;
3. **`C_creep` per-par** — já tem precedente de leitura por par.

**Nada proposto para adoção neste documento.** O passo seguinte honesto é um
prereg com alvo declarado **antes** — e o alvo não pode ser o MAE.
