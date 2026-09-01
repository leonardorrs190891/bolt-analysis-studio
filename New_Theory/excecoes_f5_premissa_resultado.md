# Camada F5 auditada — a prova cobre **uma perna**, e 1 exceção está acima da própria barra

**2026-08-07 (manhã)** · `excecoes_f5_teste_premissa.py` (só-leitura) ·
**nada retratado**. Fecha a auditoria das quatro classes de estatuto.

## O que a prova F5 afirma, e o que ela não afirma

`f5_excecoes_propostas.md`: *"quando réplicas nominalmente idênticas divergem
mais que a meta, nenhum modelo determinístico único pode ficar dentro dela. A
prova é o **desvio máximo à mediana do ensemble** — o **res.máx** que a curva
ideal (a própria mediana dos dados) já teria contra alguma réplica."*

⇒ a prova, como enunciada, cobre **res.máx**. Não diz nada sobre MAE nem σ_res.

## ⛔ ERRATA (mesma manhã): esta seção está ERRADA de categoria

O que segue publicou que a `bauer2024_M12_fig8_test1` *"excede a barra da
prova"*. **Não há barra por curva a exceder.** Medido em
`f5_sem_limite_superior_resultado.md`:

1. **Não houve deriva** — o doc F5 registra res.máx **0,3965**, o valor de hoje;
   ela foi assinada assim.
2. **O argumento F5 de *scatter* é de FAMÍLIA, não de curva:** *"nenhum modelo
   determinístico único pode ficar dentro da meta"*. É unalcançabilidade, não
   cobertura individual.

Foi a **5ª** vez nesta passada que testei um estatuto contra o critério errado.

⚠️ **E a errata expõe algo pior que o defeito que eu acusei:** a classe F5 de
*scatter* **não tem limite superior algum** — formalmente cobriria uma curva com
res.máx 1,0. Proposta **P-11** em `f5_sem_limite_superior_resultado.md`.

### (registro) O que esta seção dizia

## O achado real: 1 exceção acima da barra que ela própria cita

| exceção | perna | valor atual | barra na prova | |
|---|---|---:|---:|---|
| **`bauer2024_M12_fig8_test1`** | res.máx | **0,3965** | **0,349** | **13,6 % acima** |
| `bauer2024_M8_fig6_rep4` | res.máx | 0,1709 | 0,328 | coberta |
| `bauer2024_M8_fig6_rep1/5/6` | res.máx | 0,112–0,130 | 0,328 | cobertas |
| `bauer2024_M12_fig8_test2/3` | res.máx | 0,120–0,180 | 0,349 | cobertas |
| ~~`jcsr2023_plain_outdoor`~~ | ~~3 pernas~~ | 0,062/0,131/0,060 | ~~0,373/0,565/0,220~~ | ⛔ **barra INVÁLIDA** |

> ⛔ **ERRATA 2026-08-20 — a linha do JCSR saiu de um PAREAMENTO INVÁLIDO.** A barra
> `0,373/0,565/0,220` foi computada poolando `plain_indoor` · `plain_outdoor` ·
> `plain_seawater` como se fossem réplicas. **São três AMBIENTES** — a variável
> *varrida* do estudo de corrosão. É a 7ª ocorrência da classe que já invalidou 6
> pareamentos e retratou 5 exceções, e aqui ela corre no **sentido grave**: barra
> inflada não produz só falso alarme, ela **aprova** (o mesmo padrão dos bloqueios
> G/H de 08-14, onde a família δ=0,5 do CHU pareava Ra 1,6×0,4 e inflava o limite
> que aprovava o `test5`). Uma barra de **MAE 0,373** é 7,5× a meta: nada reprovaria
> contra ela.
>
> ⚠️ **A exceção em si NÃO cai por isto**, e a distinção importa: a prova assinada da
> `jcsr2023_plain_outdoor` é **`cliff/rebound de corrosão (forma faltante)`** — não é
> de *scatter*. A linha acima era observação de auditoria, não o fundamento do
> estatuto. O mesmo vale para as ECCLES do §seguinte (`fig7d`/`fig8b`/`fig8d`/`fig6`),
> cujas provas dizem **`sobreposição axial`**.
>
> ✅ **Consertado no INSTRUMENTO, não só na prosa:** `excecoes_f5_teste_premissa.py`
> agrupava por **rótulo de figura**, e figura que é *varredura* não é ensemble de
> réplicas (ECCLES `fig7`/`fig8` varrem carga axial; JCSR `plain` varre ambiente). O
> bloqueio canônico `_SEM_FAMILIA_MECANICA` **já continha** todas essas curvas, e o
> script o consultava **zero vezes**. Agora ele imprime `FAMILIA BLOQUEADA … barra
> NAO calculada` + a prova assinada de cada uma, em vez de um número. Famílias que
> **sobrevivem** ao bloqueio: BAUER `M8_fig6` (`rep1`…`rep6`) e `M12_fig8`
> (`test1`…`test3`) — réplicas de verdade, só índice de repetição.

⇒ **`bauer2024_M12_fig8_test1` é a única cuja perna coberta pela prova excede a
barra da prova.** Candidata a revisão — não retratada aqui.

## A lacuna estrutural, irmã da que a P-10 nomeia

Três exceções F5 violam pernas que a prova **não endereça**:

| exceção | além do res.máx |
|---|---|
| `bauer2024_M12_fig8_test1` | MAE 0,0745 · σ 0,0928 |
| `bauer2024_M8_fig6_rep4` | MAE 0,0783 · σ 0,0932 |
| `bauer2024_M8_fig6_rep6` | MAE 0,0757 |

O argumento de que *"nenhum modelo determinístico único fica dentro da meta"*
pode muito bem valer para MAE e σ também — mas **a prova não o computa**, e a
campanha já retratou 5 exceções F7 exatamente por perna não coberta. É a mesma
estrutura da lacuna do critério de resolução (**P-10**): o argumento cobre a
perna que motivou a proposta e cala sobre as outras.

**Recomputar as barras nas três pernas é barato** — o script já o faz — mas os
números que eu computo **não** reproduzem os do doc (mx do fig6: eu 0,2605, o
doc 0,328), porque a grade de interpolação e a janela diferem. O próprio doc F5
já registra essa sensibilidade: *"o spread bruto depende da grade de
interpolação e por isso difere"*. ⇒ **as barras autoritativas são as do doc**, e
estender a prova às outras pernas exige refazê-la com o método original, não com
o meu.

## ⚠️ Terceira vez que o mesmo erro me pega, em forma nova

Duas das quatro que meu script sinalizou têm justificativa F5 **completamente
diferente** de *scatter*:

* `eccles2010_fig7d` — *"sobreposição axial — PASSA no tripé por ARTEFATO: o
  FLOOR_TRIM corta os 4 pontos da cauda a zero"*;
* `eccles2010_fig8d` — *"sobreposição axial (G-B1 FAIL: res.máx 0,252 → 0,400
  com a receita)"*.

Meu teste de desvio-à-mediana **não se aplica** a elas. Foi o terceiro erro da
mesma família nesta madrugada: **testar uma exceção contra o critério errado**
(antes: média-da-fonte em vez de piso-por-condição; F7 aplicado a F5;
primeiro-critério-que-casa em vez de qualquer-um). A regra que fica é sempre a
mesma — **leia a prova gravada antes de escolher o teste**.

## Estado final das quatro camadas de estatuto

| camada | n | premissa se sustenta? |
|---|---:|---|
| exceções **F7** (piso por perna) | 7 | **7/7** — 0 pernas descobertas |
| exceções **F5** (scatter) | 9 | **8/9** — `M12_fig8_test1` 13,6 % acima |
| exceções **F5** (outros argumentos) | 7 | argumentos próprios, não testáveis por scatter |
| declarações — colapso | 3 | **3/3** |
| declarações — `n<6` | 3 | **3/3** |
| declarações — resolução | 6 | **3/6** ⇒ **P-10** |
| declarações — escopo | 4 | sem premissa numérica |

**Duas pendências para o professor:** a lacuna do critério de resolução
(**P-10**, já na fila) e a `bauer2024_M12_fig8_test1`. Nenhuma outra camada tem
defeito.

## Reprodutibilidade

```bash
py -3.12 New_Theory/excecoes_f5_teste_premissa.py --json New_Theory/excecoes_f5_teste_premissa.json
```
