# **85 % das afirmações de procedência são infalsificáveis** — e o R2 de hoje é o caso-prova

**2026-08-16 (18:0x)** · só-leitura · **nada executado** · store `7a60cacb72de`, censo
**144/205**, fora 61, abertas 21, `form_limited` 1 · **proposta aguarda assinatura**.

---

## 1. A pergunta veio da adoção de hoje

O **item R / rota R2** (adotado às 17:2x, gates 6/6) estabeleceu um fato incômodo: o
`prov.loose_arrest_floor` de dois grupos do `ECCLES_2010` **afirmava** *"lido-do-dado
(assíntota final crua ≥0,03)"* sobre valores (0,137 e 0,059) que o dado **não sustenta** —
a leitura L24 do CSV cru dá **0,0000** e **0,0122**.

A pergunta imediata: **quantas outras afirmações de procedência não descrevem seus
números?** E, antes disso: **quantas dessas afirmações alguém consegue sequer checar?**

## 2. Medido — e o denominador foi limpo antes de publicar

Varrendo `New_Theory/adopted_configs.json` por `prov` cujo texto **afirma** origem de dado
(`lido-do-dado`, `ancora`, `handbook`, `VDI`, `medido`, `paper`, `tabela`):

⚠️ A 1ª contagem deu 198, e estava **suja**: incluía **71** chaves de texto livre ou
compostas (`grupo`, `leituras`, `secos`, `per_case`, `grip/mu/E`) e **12** entradas
string/flag (`creep_mode`, `fatigue_enabled`), às quais banda numérica não se aplica.
Denominador honesto = chave que é **campo de `JointMaterial`** e valor **numérico**:

| | n |
|---|---:|
| pares (grupo, constante) numéricos afirmando dado/âncora/handbook | **115** |
| que a guarda `check_input` **consegue** checar | **17 (15 %)** |
| **INFALSIFICÁVEIS pela guarda existente** | **98 (85 %)** |
| constantes distintas sem checagem possível | **29** |

`checkable_inputs()` conhece **7** nomes: `F_amp_ratio` · `conform_pressure_exp` ·
`fat_sigma_endurance` · `k_wear_spec` · `mu_bearing` · `mu_dry` · `mu_thread`.

## 3. O caso-prova: a guarda não poderia ter pego o defeito do R2

```
>>> 'loose_arrest_floor' in checkable_inputs()
False
>>> check_input('loose_arrest_floor', 0.137)
None
```

⚠️ E esse `None` **não é aval** — o próprio docstring de `check_input` avisa que ele é
ambíguo por contrato (*"dentro da banda" OU "não sei checar"*), e manda usar
`checkable_inputs()` para desambiguar.

⇒ o `loose_arrest_floor` afirma procedência de dado em **10 grupos**, e **em nenhum deles a
afirmação é verificável** pelo instrumento existente. Hoje se descobriu, por medição
manual, que **2 dessas 10** eram falsas.

**Isto não diz que as outras 8 estão erradas.** Diz que ninguém saberia se estivessem.

## 4. As 29 constantes sem checagem, por peso

| constante | grupos que afirmam procedência |
|---|---:|
| `C_creep` | **17** |
| `loose_arrest_floor` | **10** |
| `tr_loose_gain` | **10** |
| `emb_depth` | 8 |
| `c_bend` | 5 |
| `N_emb` · `fat_m1` · `K_archard` | 4 cada |
| `fat_Kt` · `fat_ramp_D_on` · `fat_sigma_uts` · `fat_C1` | 3 cada |
| +18 constantes | 1–2 cada |

⚠️ **`C_creep` lidera com 17** — e é justamente a constante que a §4.7 do
`MODEL_LEGITIMACY.md` documenta como **por par tribológico**, com ICs disjuntos entre a
âncora 304SS e o fit da âncora interna. ⇒ uma banda global para ela seria **errada por construção**; a
checagem correta teria de ser **por par**, que é informação que o repositório ainda não
organiza.

## 5. ⚠️ O que este documento NÃO afirma

**Não afirma que 98 valores estão errados.** `check_input` devolve **sinalização**, não
veredito, e fora-da-banda pode ser legítimo por construção — o `k_wear_spec = 0` é idioma
documentado de *"wear desligado"*, e tribologia por par legitimamente sai de banda global.
Publiquei uma 1ª leitura como *"15 de 17 fora da banda"* e a **retirei** ao ler a semântica
da função: seria contagem de bandeira apresentada como contagem de defeito.

O que se afirma é **estrutural**: 85 % das afirmações de procedência das configs adotadas
**não podem ser contraditas por nenhum instrumento automático**. Elas valem exatamente o
que vale a disciplina de quem as escreveu — e o R2 mostrou que essa disciplina falha.

## 6. Proposta — **aguarda assinatura** (mexe no gate de adoção)

Três rotas, em ordem de custo crescente:

| # | ação | custo | o que compra |
|---|---|---|---|
| **S1** | **guarda auto-referente para `loose_arrest_floor`**: piso rotulado `lido-do-dado` que fique **ACIMA** da leitura L24 do CSV cru **falha**. Não precisa de banda de literatura — **a referência é a própria curva**. | baixo (1 teste) | fecha a classe exata do defeito do R2; **2 casos hoje**, ambos já tratados |
| **S2** | estender `checkable_inputs()` para as constantes **com âncora publicada** (`emb_depth` tem tabela VDI 2230 por classe de rugosidade; `fat_*` têm handbook) | médio | tira ~15–20 pares do infalsificável |
| **S3** | `C_creep` **por par tribológico** — exige organizar a informação de par, que o repo hoje não tem estruturada | alto | tira os 17 do topo |

**Recomendo S1.** É a única que fecha um defeito **medido**, custa um teste, e não depende
de âncora nova. ⚠️ Direção importa: piso **abaixo** da leitura é escolha conservadora e não
deve disparar alarme — a regra é unilateral (medido em `eccles_piso_nao_sustentado_pelo_dado.md`
§6a: das 21 curvas com rótulo `lido-do-dado`, **7 ficam abaixo** — todas `SUN_2025`, e são
legítimas — e só **2 acima**).

⛔ **Não executo nenhuma das três** — mexer no gate de adoção exige assinatura (protocolo do
cron, passo 4).

## Reprodutibilidade

Sonda inline no corpo do commit. Usa `kb.checkable_inputs()`, `kb.check_input` e
`JointMaterial.__dataclass_fields__` — nenhuma reimplementa regra. O filtro de denominador
(campo de dataclass **e** valor numérico) está no script e é o que separa 115 de 198.
