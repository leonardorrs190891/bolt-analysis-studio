# Fecha os 3 tickets + DEDUP de par declarado — 2026-08-23

**Assinado** (*"resolva o que tá aberto"*). Prereg:
`docs/superpowers/specs/2026-08-23-fecha-tickets-e-dedup-prereg.md`.

**Resultado em uma linha:** o bloqueio manual de pareamento vai a **ZERO**, e o conserto de
um defeito **meu** custa **duas exceções assinadas**.

---

## 1. Os 3 tickets fecharam — e não pelo campo óbvio

| fonte | o que a resolveu |
|---|---|
| `LI_2022_TRIBOINT` | **`frequency_Hz`** na chave (10 / 15 / 20 Hz) |
| `KARLSEN_2022` | rótulo de **dispositivo de travamento** (`hv` / `hvtorqued` / `vibralock` / `vibralock_torqued`) |
| `LI_2022_MARSTRUC` | rótulo de **pré-carga NOMINAL** (5 / 10 / 15 kN) |

⇒ `_SEM_FAMILIA_MECANICA` **ativo = 0** (era 81, depois 14). Os **81 motivos escritos ficam**
— são procedência, e registram por que o pareamento era falso em cada fonte.

## 2. ⛔ `initial_preload_N` na chave: FALSIFICADO, e a prova estava no repositório

Era a rota óbvia para as duas fontes numéricas. **Está errada**, e quem diz é o
`_PARES_REPLICA_DECLARADOS`: ele existe para *"réplicas cujo F₀ **ALCANÇADO** difere
(aperto nunca repete: 4–14 % nos pares do LU)"*. Ou seja **toda réplica real tem F₀
diferente** ⇒ pôr F₀ na chave destruiria pareamento legítimo em todo o projeto.

E não resolveria o KARLSEN: `M42_HV_run21p0` e `M42_vibralock_torqued_run29p0` têm **F₀
idêntico (685 kN)** e diferem no travamento. Os 11 F₀ da fonte são distintos, e justamente
os dois que importam empatam.

⇒ **Regra que fica: na chave entram grandezas AJUSTADAS, nunca ALCANÇADAS.**
`frequency_Hz` é ajustada (medido: quebra **zero** pares, 225 → 225). `initial_preload_N` é
alcançada.

## 3. O defeito que EU introduzi, e o que ele custou

O par declarado entra em `grupos` sob chave própria `(src, "DECL", rótulo, None)`. Quando a
chave automática **também** agrupa os dois membros, **o mesmo par conta duas vezes**. Antes
do ITEM X isso não ocorria (as curvas estavam bloqueadas); depois dele **3 de 5** pares
ficaram duplicados, e com o fecho dos tickets seriam **4 de 5**.

Não era um par qualquer. Medidos os **6 pares dado-contra-dado** da família sem axial do
ECCLES:

| par | MAE | res.máx | σ |
|---|---:|---:|---:|
| fig3 × fig7a | 0,0479 | 0,1104 | 0,0214 |
| fig3 × fig8a | 0,0502 | 0,1109 | 0,0592 |
| fig3 × fig8c | 0,0288 | 0,0756 | 0,0357 |
| fig7a × fig8a | 0,0556 | 0,1846 | 0,0552 |
| fig7a × fig8c | 0,0478 | 0,0640 | 0,0203 |
| **fig8a × fig8c — o DECLARADO** | 0,0541 | **0,1866** | **0,0707** |

⚠️ **O par declarado pelo autor é o PIOR dos seis** — máximo em res.máx *e* em σ. E nenhum
par é outlier (MAE 0,029–0,056 · mx 0,064–0,187 · σ 0,020–0,071) ⇒ `fig3` e `fig7a`
concordam com os baselines tanto quanto os baselines concordam entre si: **a família de 4 é
legítima, medida e não assumida.**

⇒ contar em dobro justamente o par mais frouxo inflava o piso. Piso correto:
**0,0474 / 0,1220 / 0,0432**, não 0,0507 / 0,1543 / 0,0565.

### O custo: duas exceções retratadas

| curva | MAE | res.máx | σ | veredito |
|---|---|---|---|---|
| `fig8a` | 0,0489 / 0,0474 **FALHA** | 0,1320 / 0,1220 **FALHA** | 0,0395 / 0,0432 PROVA | **FALHA** |
| `fig8c` | 0,0456 / 0,0474 PROVA | 0,1463 / 0,1220 **FALHA** | 0,0386 / 0,0432 PROVA | **FALHA** |

**`declarado_total` 201 → 199**, `fora_aberta` 4 → 6, **tripé intacto em 169/205**. As
provas ficaram **preservadas verbatim** em `_EXCECOES_RETRATADAS_ECCLES_PAR_DUPLICADO`.

A alternativa era manter um piso que eu **sabia** inflado, para proteger duas exceções que
dependiam exatamente da inflação. Precedentes de retratação por base inválida: ROUSSEAU,
CACCESE, LU.

## 4. A ironia do arco do ECCLES, em três medições

| quando | piso σ | por quê |
|---|---:|---|
| até 2026-08-15 | 0,083 | piso **inválido** (dispersão entre cargas axiais — a variável varrida) |
| 08-15 → hoje | 0,0698 | par declarado pelo autor, à mão |
| ITEM X (hoje, manhã) | 0,0565 | a carga axial entra na chave ⇒ família por mecanismo |
| **este prereg** | **0,0432** | o par declarado deixa de contar em dobro |

Cada aperto veio de **remover uma distorção**, nunca de melhorar o modelo. E o modelo não
mudou uma linha: as três medições são do mesmo store.

## 5. Gates

| gate | veredito |
|---|---|
| **G1** exatamente 2 retratadas, prova preservada, outras 19 intactas | ✅ 21 → **19** |
| **G2** censo: tripé 169, `declarado` 201→199, `fora_aberta` 4→6 | ✅ exato |
| **G3** nenhum limite afrouxa | ✅ só o ECCLES move, e **aperta** |
| **G4** zero pares declarados duplicados | ✅ 0; sobra 1 família DECL (KARLSEN HV M30, que a chave não faz) |
| **G5** tickets sem família espúria | ✅ KARLSEN 0 · MARSTRUC 0 · TRIBOINT = o par declarado |
| **G6′** toda mudança de piso ATRIBUÍVEL | ✅ uma fonte, atribuída ao dedup |
| **G7** bloqueio ativo = 0, 81 motivos preservados | ✅ |
| **G8** suíte | ✅ (ver §7) |
| **G9** `initial_preload_N` fora da chave, falsificação escrita | ✅ §2 |

**As 6 predições bateram**, incluindo o piso ao 4º decimal e o custo no censo.

⚠️ **O G6′ é o gate que o ITEM X deveria ter tido.** O G6 antigo exigia piso bit-idêntico
em fontes fora do bloqueio, o que proibia a chave de agir e contradizia o próprio prereg.
Reescrito como *atribuibilidade*, ele passa — e teria pegado o defeito de contagem dupla,
que o antigo não pegava.

## 6. Erros meus no caminho, os dois do mesmo tipo

**(a) A terceira ocorrência do colapso de barra invertida no heredoc**, hoje. Um
`[^"\\]` num regex de script virou `[^"\]` — classe não terminada, `re.error`. Nada foi
escrito porque falhou antes. A lição do gotcha do `\b` se estende: **não use barra
invertida em Python escrito via heredoc**, nem para regex de trabalho. Refiz com operações
de string.

**(b) Eu disse ao professor que regenerar o explorador varreria mudanças da sessão
paralela.** Medido: **todos** os commits que tocam o que ele lê desde 21/08 são meus
(`53996b7`, `695dd55`, `e0082b3`, `49e66c6`, `940a2c0`). A ressalva estava errada, e o
explorador foi regenerado no mesmo passo.

## 7. Reprodutibilidade

```bash
py -3.12 -m pytest tests/test_chave_estendida_pareamento.py \
                   tests/test_variavel_varrida_nao_e_replica.py \
                   tests/test_provas_de_excecao_nao_envelhecem.py \
                   tests/test_meta_numeros_nao_envelhecem.py -q
```

Sem engine, config, store ou fingerprint. Rollback = `git revert`.
