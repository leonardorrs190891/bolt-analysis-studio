# Métrica em vida no trecho vertical — EXECUTADA e **REJEITADA** pelos próprios gates

**Data:** 2026-07-28 · **Autorização:** professor, *"autorizado item 1 — métrica em vida no trecho vertical"*
**Pré-registro:** `specs/2026-07-28-metrica-em-vida-prereg.md`, gates **congelados em `3a26b4a`**, antes de uma linha de implementação
**Estado final:** implementação **REVERTIDA**; métrica canônica **inalterada**; store restaurado (203 casos, `4f5bedfbace4`)

---

## 0. Veredicto

| gate | resultado |
|---|---|
| **M0** identidade no trecho plano | **FALHA** — pior desvio 4,70e-2 (limiar 1e-6) |
| **M1** curva plana não se mexe | **FALHA** — 3 de 94 curvas planas mudam (até 0,0013) |
| **M2** discriminância vs cliff | **FALHA** — **o cliff passa** nas 4 curvas |
| **M3** virada só em trecho íngreme | **FALHA** — **4 de 6** viradas em trecho **raso** |
| M4 teto de 25 viradas | OK (6 viradas) |
| M5 fingerprint inalterado | OK (`4f5bedfbace4`) |
| M6 nenhuma curva piora | OK (202 comparadas) |

**Ramo pré-declarado que se aplica** (§4.1): *"**M2 ✗** ⇒ a métrica não distingue
mais formas ⇒ **morre**, independentemente do resto."* Honrado: a implementação
foi revertida no mesmo dia, sem adoção.

A meta teria ido de **147 → 153**. Esse número **não é o resultado** — 4 das 6
viradas são ilegítimas pelo M3, e o M2 mostra que a métrica deixou de distinguir
a forma certa da forma errada. Uma métrica que sobe a meta em 6 curvas e ao mesmo
tempo aprova um cliff instantâneo não mediu nada.

---

## 1. O que matou: uma causa única para as quatro falhas

> **A fuga horizontal corre pela inclinação do MODELO, não pela do DADO.**

Meus gates M0/M1 condicionavam a "planura" à inclinação **do dado**. A brecha se
abre pela inclinação **do modelo**. Medido, no pior ponto do M0:

```
jcsr2023_plain_outdoor, N = 150
  dado   r = 0,7287   (inclinação 0,000/ciclo — PLANO, já estabilizou)
  modelo r = 0,6006   (inclinação 5,2e-3/ciclo — DESPENCANDO)
  resíduo vertical .... 0,1282     <- o modelo colapsou cedo demais
  resíduo em vida ..... 0,0811     <- 37% menor, sem que nada melhorasse
  vizinhança do modelo: (133; 0,694) (140; 0,654) (145; 0,626) (150; 0,601)
  vizinhança do dado:   (133; 0,750) (140; 0,734) (145; 0,729) (150; 0,729)
```

O modelo, ao despencar, **varre** o valor 0,729 poucos ciclos antes. A distância
ortogonal acha esse ponto e reporta um resíduo pequeno. Ou seja: **a métrica
perdoa colapso prematuro** — precisamente o modo de falha que a campanha mais
precisa detectar (§4.8, *"colapso por wear excessivo"*).

O mesmo mecanismo explica tudo:

- **M2** — o cliff cai verticalmente no fim, então sua queda varre **todos** os
  valores de `r` do colapso do dado. Cada ponto acha um vizinho.
- **M3** — as 4 viradas em trecho raso são curvas (`bauer2024_M8_fig6`,
  `eccles2010_fig8a/8b`) onde o dado é raso e o modelo tem estrutura vertical.
- **M0/M1** — o desvio de 4,7e-2 é grande demais para o déficit analítico em
  curva plana (`≤ 0,5 %·|Δr|`); só se explica pela inclinação do modelo.

### 1.1 A tabela que decide (reproduzível em ~2 min, sem patch)

`py -3.12 New_Theory/metrica_vida_rejeitada.py` — P = passa o tripé:

| curva / forma | **vertical** (canônica) | **em vida** (rejeitada) |
|---|---|---|
| amp0p4 sem forma | 0,101/0,452 **F** | 0,100/0,450 **F** |
| amp0p4 rampa | 0,051/0,148 **F** | 0,030/0,062 **P** |
| amp0p4 **CLIFF** | 0,101/0,452 **F** | 0,035/0,062 **P** |
| amp0p5 **CLIFF** | 0,075/0,330 **F** | 0,025/0,052 **P** |
| **amp0p6 rampa** | 0,085/0,330 **F** | 0,030/0,070 **P** |
| **amp0p6 CLIFF** | 0,065/0,330 **F** | **0,028/0,070 P** ← *melhor que a rampa* |
| fig2 (fino) rampa | 0,101/0,337 **F** | 0,019/0,057 **P** |
| fig2 (fino) **CLIFF** | 0,229/0,681 **F** | 0,034/0,079 **P** |

Em `amp0p6` o **cliff fica melhor que a rampa**. E no `fig2` fino o cliff
melhora **8,6×** — uma forma que despenca num ciclo, contra um dado que colapsa
ao longo de 2 600. Não há como chamar isso de métrica.

---

## 2. Por que o gate G1 do prereg v2 conseguiu, e este não

Os dois pontuam "em vida", e um discrimina (rampa 12 · cliff 8 · nada 0) e o
outro não (todos passam). A diferença é **o objeto comparado**:

| | prereg v2 G1 | métrica rejeitada |
|---|---|---|
| objeto | **cruzamento de nível**: o `N` em que o **dado** atinge `r*` contra o `N` em que o **modelo** atinge `r*` | **distância ao conjunto** de pontos da curva do modelo |
| correspondência | **fixada pelo nível** — 1 para 1, sem escolha | escolhida pela minimização, e o modelo escolhe |
| normalizador | `0,15·Δ_col` (largura do colapso) | `σ_N = 3 %·N` (cresce com a vida) |

**A lição de forma:** distância ao *conjunto* deixa o modelo "chegar perto" por
um caminho que não corresponde ao mesmo instante. Correspondência **por nível**
não deixa. Quem tentar de novo deve partir do cruzamento de nível, e normalizar
pela **janela de colapso**, não por `N` — o mesmo erro de normalizador que eu já
tinha pego ao desenhar o G1 do v2 e reintroduzi aqui por outra porta.

---

## 3. O que eu errei no processo, e a regra que sai disso

**M0 era insatisfazível como escrito, e eu não conferi.** Ele exige identidade a
`1e-6` no trecho plano; a fórmula escolhida entrega identidade só
**assintótica** (déficit ≈ `|Δr|·(inclinação·σ_N/σ_r)²/2`). M0 só passaria com a
chave de regime que a §2 do prereg deliberadamente evitou — ou seja, **o gate
contradizia o design no mesmo documento**.

O constrangedor: dois dias atrás escrevi um premeasure inteiro criticando o v1
por congelar uma cláusula que dava dois veredictos, e **inventei** a etapa de
*medir a mensurabilidade antes de congelar*. Aqui pulei exatamente essa etapa.

> **Regra proposta:** todo gate deve vir com a **conta de satisfazibilidade** —
> o valor que a forma proposta produziria no caso ideal. Um gate sem essa conta
> não está pré-registrado, está apenas escrito. Custo de aplicá-la: minutos.
> Custo de pular: este documento.

**O que o processo acertou, e vale registrar:** os gates que protegiam contra
mover a trave (**M2** discriminância e **M3** viradas em trecho raso) **fizeram
exatamente o trabalho para o qual foram escritos** e mataram uma mudança que eu
próprio propus, implementei e teria adotado olhando só para "147 → 153". Foram
escritos **antes** de qualquer número existir. É o argumento mais forte
disponível a favor de pré-registrar.

---

## 4. Estado final e o que fica aberto

**Revertido, sem resíduo:**
- `runner.py` de volta ao canônico (a implementação **nunca** chegou a ser commitada);
- store restaurado do backup — verificado: **zero divergências** nos campos
  verticais (`mae`, `maxerr`, `resid_std`, `rmse`, `final_pred`, `align`,
  `maxerr_at`) nos 203 casos, e a re-simulação de 202 casos confirmou que a
  mudança era puramente aditiva;
- fingerprint segue `4f5bedfbace4`; a meta segue **147/202**.

**Preservado fora do caminho canônico:** `metrica_vida_rejeitada.py` (a forma +
a reprodução barata do M2), `metrica_vida_output.txt` (saída verbatim da
varredura), `metrica_vida_result.json`, `metrica_vida_gates.py` (o arnês da
varredura; **precisa do patch revertido** para rodar inteiro).

**Segue aberto — e a autorização do professor não foi consumida.** O problema que
motivou o pedido continua real e medido (`MODEL_LEGITIMACY` §4.44a): há curvas
**metric-limited**, em que o dado existe, a forma acerta em vida e o tripé
vertical é inatingível por construção. O que morreu foi **esta** forma de
resolver, não o problema. O caminho que o próprio fracasso indica — cruzamento
de nível normalizado pela janela de colapso — está descrito no §2 e exige
**pré-registro novo**, com a conta de satisfazibilidade do §3.
