# Duas exceções assinadas repousam num piso que a **própria campanha já declarou inválido**

**2026-08-15 (manhã)** · só-leitura · **nada retratado** · store `85e8104420b0`, censo
**141/205** · **6ª ocorrência da mesma estrutura**.

---

## 1. Como cheguei aqui

Auditei a camada `excecao_assinada` (22 curvas) porque ela tem o **pior histórico**: cinco
retratações por piso inválido (`_EXCECOES_RETRATADAS_*`), e os pisos **se moveram duas vezes
em 24 h** — a correção de `rz` do CHU (sessão B) e a adoção do canal de flanco no
`LIU_2020`. Prova cujo denominador mudou é suspeita.

## 2. ⚠️ Primeiro achado, estrutural: **20 das 22 provas não são conferíveis por máquina**

As exceções guardam a prova **em prosa**. Só **2** trazem o formato `valor/piso` por perna
(`prova de piso (FORTE): res.máx 0.122/0.257 · σ 0.039/0.083`); as outras **20** dizem coisas
como *"scatter de réplicas (desvio-à-mediana 0.349)"* ou *"form-limited com prova em lei
(5 degraus)"*.

⇒ **a camada com o pior histórico de invalidação é a menos verificável automaticamente.**
Não é defeito de quem escreveu — provas de lei e de escopo não têm a forma `valor/piso`. Mas
significa que a campanha **não consegue perguntar à máquina** se as suas próprias exceções
ainda valem.

## 3. O que as 2 conferíveis revelaram

`eccles2010_fig8a_no_axial_baseline1` e `eccles2010_fig8c_no_axial_baseline2`, ambas FORTE,
citam **piso res.máx 0,257 · σ 0,083**.

### ⚠️ Esse piso **já foi declarado inválido pela campanha**, em 2026-08-08

O comentário da **P-15** (assinada e executada), preservado em `report_html.py`:

> *"A retirada D1 desta curva se apoiava no piso σ **0,083** do ECCLES … Aquele 0,083 era
> **dispersão entre cargas AXIAIS de 0 a 3,5 kN — a variável varrida do paper** —, com σ
> indo de 0,0195 a 0,1887 e MONOTÔNICO com a carga. Removido o piso falso, a curva volta a
> falhar."*

A `eccles2010_fig7c` **foi retratada** por isso. **A `fig8a` e a `fig8c` continuam assinadas
sobre o mesmo piso.**

E o instrumento de hoje confirma: `pisos['por_fonte']['ECCLES_2010']` é **`None`** — não há
família nenhuma para a fonte. O denominador das duas provas **não é reproduzível**.

## 4. O piso VÁLIDO existe — e as duas falham nele

O ECCLES tem **4 curvas sem carga axial**, que são réplicas da mesma condição
(`F_amp` 6000 N, δ 0,65 mm em todas):

| par | MAE | res.máx | σ |
|---|---:|---:|---:|
| `fig3_typical` × `fig7a` | 0,0488 | 0,1160 | 0,0213 |
| `fig3_typical` × `fig8a` | 0,0501 | 0,1109 | 0,0577 |
| `fig3_typical` × `fig8c` | 0,0293 | 0,0755 | 0,0356 |
| `fig7a` × `fig8a` | 0,0548 | 0,1846 | 0,0531 |
| `fig7a` × `fig8c` | 0,0482 | 0,0640 | 0,0196 |
| `fig8a` × `fig8c` | 0,0532 | 0,1866 | 0,0687 |
| **mediana (piso)** | **0,0494** | **0,1134** | **0,0443** |

⇒ o piso legítimo é **0,1134 / 0,0443**, contra os **0,257 / 0,083** citados — **3× menor**,
porque o citado media a variável que o experimento varre.

| curva | res.máx | barra FORTE **0,0802** | σ | barra **0,0314** |
|---|---:|:--:|---:|:--:|
| `fig8a` | 0,1320 | ⛔ | 0,0395 | ⛔ |
| `fig8c` | 0,1463 | ⛔ | 0,0386 | ⛔ |

**Nenhuma das duas sobrevive** — e nem na barra mais fraca (PROVA = piso, 0,1134): 0,1320 e
0,1463 excedem-na.

## 5. Proposta (item O — **não executada**, retratação exige assinatura)

Retratar as duas exceções, preservando a prova em `_EXCECOES_RETRATADAS_ECCLES_PISO_INVALIDO`
com a medição acima, **no mesmo idioma das cinco anteriores**.

⚠️ **A assinatura NÃO é devolvida por mérito** — o precedente é explícito nas retratações
anteriores: *"a curva volta a falhar por motivo NOVO, então a assinatura não é devolvida;
seria re-assinar contra piso inválido"*. Aqui elas falham contra o piso **válido**, medido.

**Custo:** `declarado_total` **181 → 179**; **censo 141 inalterado** (as duas já estão fora
do tripé). Exceções ativas **22 → 20**.

⚠️ **E há um ganho junto:** com a família `no_axial` medida, o `ECCLES_2010` **deixa de ter
piso `None`** — o que reabre a possibilidade de prova F7 legítima para as curvas da fonte,
que a nota da P-15 dava por impossível (*"a fonte perdeu o piso junto com a família falsa,
logo prova F7 é impossível para ela até haver réplica de condição repetida"*). **A réplica
existe**: são as 4 `no_axial`.

## 6. O que NÃO se afirma

Não se afirma que a família `no_axial` é automaticamente admissível como piso — isso é
julgamento de pareamento, e a campanha já bloqueou famílias por chave cega **seis vezes**.
O que se mede é que as 4 compartilham `F_amp`, `δ` e a ausência de carga axial, que é a
variável que invalidou o piso anterior.

## Reprodutibilidade

`audit_excecoes.py` no scratchpad + as medições do par inline. Só-leitura, ~30 s.
