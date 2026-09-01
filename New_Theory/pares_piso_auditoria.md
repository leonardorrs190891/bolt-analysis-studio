# Auditoria dos PARES que medem o piso: 4 famílias atravessam variável varrida, e **uma** importa

**2026-08-07** · só-leitura · **nada alterado** · a medição sustenta uma
proposta (**P-15**), não uma edição.

## Por que esta premissa, e por que ela não tinha sido testada

As cinco camadas de estatuto já têm auditoria. Mas há uma premissa **adjacente**
que decide o veredito de curvas sem ser nenhuma delas: **quais curvas o
`_pisos_medidos` agrupa como réplicas**. Um pareamento errado **infla** o piso da
fonte, e piso inflado **afrouxa** `limite_sres` — o que aprova curva que não
deveria passar.

Essa classe de erro já custou **três** blocos de retratação (ROUSSEAU, CACCESE,
SUN). Nunca foi varrida sistematicamente.

## O teste

A chave mecânica é, lida no sítio (não reimplementada):

```python
k = (src, round(delta_mm, 4), round(F_amp_N, 1), mode)
```

⇒ cega a espessura, material, frequência, torque, rugosidade **e carga axial**.

Critério: numa família automática, se os membros diferem em campo de config que
codifica **geometria ou condição** (`c_bend`, `emb_depth`, `GA_member`,
`delta_free`, `k_tr_mode`, `conform_driver`, `mu_*`), eles não são réplicas —
são condições distintas. *Dispersão de espécime* (p.ex. o `tr_loose_gain`
per-réplica do BAUER, lido da vida N50) **não** conta e não dispara.

## O resultado: 4 de 20 famílias, e só 1 tem efeito

| fonte | n | o que difere | limite hoje | limite sem ela |
|---|---:|---|---:|---:|
| **`ECCLES_2010`** | **10** | `conform_driver`, `k_tr_mode`, μ | **0,0828** | **0,0250** |
| `LIU_2022_RETIGHT` | 18 | μ 0,176 × 0,236 (óleo × seco) | 0,0250 | 0,0250 |
| `SUN_2025_REASSY` | 5 | `emb_depth`, μ (nº de remontagens) | 0,0250 | 0,0250 |
| `LIU_2020_WEAR` | 3 | `mu_thread` | 0,0250 | 0,0250 |

**Três das quatro não têm efeito nenhum:** o piso medido delas já é *menor* que o
global, então `max(0,025; piso)` devolve 0,025 de qualquer modo. O pareamento é
conceitualmente errado nas três, e **inócuo** — vale registrar, não agir.

## A que importa: `ECCLES_2010`

A família junta **10 curvas de "sem axial" a 3,5 kN axial** — a **variável
varrida do paper** — como se fossem réplicas:

| curva | carga axial | σ_res |
|---|---|---:|
| `fig7a_no_axial` | sem axial | 0,0195 |
| `fig7b_axial_1p1kN` | 1,1 kN | 0,0218 |
| `fig7c_axial_2p7kN` | 2,7 kN | 0,0258 |
| `fig7d_axial_3p1kN` | 3,1 kN | 0,0565 |
| `fig8d_axial_3p5kN` | 3,5 kN | 0,0939 |
| `fig6_annotated_4kN` | 4 kN | **0,1887** |

Os σ variam **quase 10×** e são **monotônicos com a carga axial**. Isso não é
dispersão de réplica: é o efeito que o paper estava medindo. Agrupá-los produz um
"piso" de **0,0828** — 3,3× o limite global.

⚠️ **E há inconsistência interna:** as exceções F5 assinadas do próprio ECCLES
argumentam **"sobreposição axial"** — ou seja, a campanha trata a carga axial
como variável **distintiva** quando prova exceção, e a agrupa como **irrelevante**
quando mede piso. As duas coisas não podem valer juntas.

## Impacto medido — e ele é contra nós

| | censo |
|---|---:|
| hoje | **140** |
| com as 4 famílias bloqueadas | **139** |

**Exatamente uma curva** passa só por causa do piso inflado:
`eccles2010_fig7c_axial_2p7kN_constant`, σ **0,0258** contra limite 0,0828 — ela
está **3 % acima** do limite global de 0,025.

⇒ a correção **custa −1 no censo**. É a direção que não precisa de proteção
contra interesse próprio, e é por isso que ela deve ser considerada.

## P-15 — ✅ ASSINADA e EXECUTADA em 2026-08-08 (gates 6/6)

> A proposta abaixo foi **assinada pelo professor e executada** — prereg
> `2026-08-08-p7-p15-execucao-prereg.md`, resultado em
> `p15_execucao_resultado.md`. Censo **140 → 139**, exatamente o custo
> previsto. O texto original fica como registro do que foi proposto.


> Acrescentar as **10 curvas do `ECCLES_2010` δ=0,65/F=6000** a
> `_SEM_FAMILIA_MECANICA`, pelo mesmo argumento e com a mesma maquinaria dos três
> bloqueios anteriores: a chave mecânica é cega à variável varrida da fonte.
> Custo: **−1 no censo** (`fig7c`, 3 % sobre o limite global).

> ⚠️ ~~**Não executei.** Bloquear família muda `limite_sres`, que muda o censo —
> é mudança de estatuto, e a regra permanente desta sessão é *reclassificação de
> camada é PROPOSTA, nunca edição sem assinatura*.~~ — **vencido**: a assinatura
> veio em 08-08 e a execução está feita.

⚠️ **O que NÃO foi medido** (segue valendo): se as 3 famílias inócuas ficariam
inócuas para sempre. Elas dependem de o piso medido seguir abaixo de 0,025; se
uma curva nova entrar numa delas e subir o piso, o pareamento errado passa a
morder **sem aviso**.

✅ **Este resíduo foi FECHADO em 2026-08-07 (noite)**, antes da assinatura: o
invariante `tests/test_pares_piso_familia.py` denuncia família divergente nova,
declaração que virou ficção, e — desde a execução da P-15 — exige que **nenhuma**
família divergente afrouxe o limite. É ele que avisa se uma das 3 inócuas subir.

---

# Segunda metade: os **PARES DECLARADOS** — auditados, e todos se sustentam

As famílias automáticas são metade da história. A outra são os **7 pares
declarados** (`_PARES_REPLICA_DECLARADOS`), o override manual usado quando a
chave mecânica não pareia réplicas legítimas — p.ex. quando o **F₀ alcançado**
difere. É uma afirmação **mais forte** que a automática: alguém assinou *"estes
dois são réplicas"*.

## Eles importam: **5 curvas** passam só por causa deles

| fonte | limite com os pares | sem eles |
|---|---:|---:|
| **`KARLSEN_2022`** | **0,0903** | 0,0250 |
| **`LU_2024`** | **0,1030** | 0,0250 |
| `CACCESE_2009` · `LIU_2016` · `LI_2022_TRIBOINT` | 0,0250 | 0,0250 |

Censo **140 → 135** sem eles. As 5: `karlsen_M30_HV_run2p2` (σ 0,0364) ·
`run6p2` (0,0300) · `run7p1` (0,0504) · `karlsen_M42_HV_run21p0` (0,0337) ·
`lu2024_fig18_amp1p5` (0,0353).

## O que exigia escrutínio meu

O par `karlsen run2p2 × run7p1` **fui eu que declarei**, hoje, com o rótulo
*"mesma condição nominal, F₀ alcançado 333 × 313 kN"* — **6,4 %** de diferença.
Ele sozinho afrouxa o limite da fonte **3,6×** e sustenta **4** aprovações.
Declaração minha que passa curvas minhas é exatamente o que precisa de
verificação independente.

**Teste discriminante:** o σ desse par é típico da família, ou é um outlier que
infla? Medidas **todas** as 6 comparações dentro de `M30 HV`:

| par | σ |
|---|---:|
| `run1p2 × run6p2` | 0,0133 |
| **`run2p2 × run7p1`** (declarado) | **0,0897** |
| `run1p2 × run2p2` | 0,1076 |
| `run2p2 × run6p2` | 0,1126 |
| `run1p2 × run7p1` | 0,1541 |
| `run6p2 × run7p1` | 0,1622 |

**Mediana da família: 0,1126.** O par declarado está em **0,0897 — abaixo dela.**

⇒ ele **não infla** o piso; usar a mediana da família o afrouxaria *mais*. A
declaração é **conservadora**, e as 4 aprovações que dependem dela estão
legitimamente sustentadas. Controle coerente: os pares `vibralock` (dispositivo
de travamento) medem σ 0,0081 e 0,0017 — muito mais apertados, como se espera de
outra classe de junta.

## Uma divergência de config, na direção inócua

Pelo mesmo critério da primeira metade, **1 dos 7** pares tem campo de condição
divergente: `liu2016 run1 × run2` diverge em **`emb_depth`**. Mas o piso do par é
**0,0046** — ele *aperta*, não afrouxa, e o `LIU_2016` fica no global 0,025 de
qualquer modo. Registrado, sem ação.

## Conclusão das duas metades

| camada | achado |
|---|---|
| famílias **automáticas** (20) | 4 divergentes; **1 importa** (`ECCLES_2010`) ⇒ **P-15**, custo −1 |
| pares **declarados** (7) | **todos se sustentam**; o mais consequente é conservador contra a própria família |

**Auditoria que confirma é resultado.** A metade que eu tinha motivo para
duvidar — a que eu mesmo escrevi — é a que passou com folga.

## Reprodutibilidade

Sondas no scratchpad e em `New_Theory/pares_piso_{sonda,impacto}.py`:
reconstroem os grupos com a chave **copiada do sítio**, marcam famílias com campo
de condição divergente, e re-medem `limite_sres` e o censo com as suspeitas em
`_SEM_FAMILIA_MECANICA` / com `_PARES_REPLICA_DECLARADOS` vazio (monkeypatch em
processo, nada escrito).
