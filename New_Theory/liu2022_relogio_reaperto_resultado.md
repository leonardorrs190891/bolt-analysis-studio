# Relógio por reaperto no LIU_2022 — 3 tentativas, e a TRANSFERÊNCIA confirmada

**2026-08-05** · preregs D-J, D-K, D-L (relógio) + D-M (estatuto do `t4`), todos
por delegação sob o MANDATO PERMANENTE. Fingerprint `98fd6c462968`.

## Por que a classe foi reaberta

O `liu2022_fig8_cadeia_resultado.md` (D-E) declarava o relógio por contagem de
reapertos morto por **contradição intra-fonte**. Sob a cláusula do mandato —
*candidato inerte ou gate nunca chamado é INCONCLUSIVO, não falsificação* —
essa morte não qualificava:

1. A contradição prova que um relógio **GLOBAL** não serve (o dado varre 0,75×
   a 2,05× entre as 4 cadeias). Não diz nada sobre um relógio **por
   protocolo**: as duas cadeias que **não soltam** aceleram na mesma direção.
2. O **`k_gall`** — a constante cujo nome é a física da classe — estava
   **congelado** por decisão minha no D-E. Medido agora por sonda de 2 pontos
   (0,0 e 12,0 contra o vigente 3,0): **Δ = 0,000000 exato**. **INERTE por
   construção**: só age em `tightening_torque`, e o **F₀ por estágio é lido do
   1º ponto do dado**, sobrepondo a recuperação que o modelo calcularia. ⇒
   `k_gall` **não é membro** da classe; o congelamento foi inócuo.

## As três tentativas, e o que cada uma matou

| | escopo | veredicto | razão |
|---|---|---|---|
| **D-J** | `(1+g)^n` no slip + `renew` | **FALSIFICADO** | o fator necessário é **< 1** em todo estágio reapertado, e um amplificador puro tem contradomínio **[1, ∞)** |
| **D-K** | `base·(1+g)^(n−1)` no slip, 3 nº | **FALSIFICADO** | **teto de autoridade**: slip suprimido por inteiro dá 0,460 no t1, alvo 0,203 — **2,3× curto** |
| **D-L** | os 2 canais, 3 números **compartilhados** | **NÃO ADOTA** | G1 **passa** em 12 células; bloqueia no G4 pelo `t4` |

### A simetria que o D-J revelou

O fator necessário por estágio (fig8): **0,203 · 0,355 · 0,719** — todos **< 1**
e **crescendo para 1**. Um multiplicador `(1+g)^n` cresce na direção certa mas
**começa acima de 1**.

**É a imagem espelhada da falsificação de 2026-08-02**: lá a família de gates
tinha contradomínio (0,1] e por isso *só sabia atrasar*; aqui o amplificador
tem [1, ∞) e *só sabe amplificar*. O dado pede um operador que **atravesse o
1** — e agora o engine tem um (`retight_loss_base` × `(1+gain)^(n−1)`).

### Falha de método minha, que vale mais que os dois preregs

**Não fiz a sonda de TETO DE AUTORIDADE antes de escrever D-J e D-K.**
Suprimir o canal inteiro e perguntar *"o alvo está dentro do alcançável?"*
custa **uma** simulação. Ela mostraria, antes de qualquer código, que:

* slip sozinho: teto 0,460 · alvo 0,203 ⇒ **impossível**;
* renew sozinho: teto 0,586 ⇒ **impossível**;
* **os dois juntos**: 0,040 / 0,023 / 0,016 ⇒ **alcançável com folga**.

Ou seja: D-J e D-K testaram **metades diferentes** da mesma composição, porque
eu fatiei errado o escopo. A sonda de teto entra no charter como pré-teste
obrigatório — é o análogo, no eixo da **magnitude**, do que a sonda de 2 pontos
é no eixo do **sinal**.

## O resultado que vale: a TRANSFERÊNCIA (G1) foi confirmada

**12 de 48 células** do D-L passam o G1 com **3 números COMPARTILHADOS** entre
seco e óleo. Nas 12: G2 (virgem intocado) e G3 (as 8 curvas que **soltam**)
**bit-idênticos**, e **`t1` e `t2` fecham**.

A parcimônia veio de uma observação sobre o canônico, não de um número novo:
`k_emb_renew` entra como `delta_emb ·= (1 − k_emb_renew·D)` — **multiplicando
`D`**, que já é por-lubrificação (`c_D` = 0,5 seco / 0,03 óleo). Logo **um só**
`k_emb_renew` produz renovação muito diferente entre as cadeias **sem número
novo**. As diferenças entre seco e óleo ficam **explicadas** pelo que já estava
adotado, não fitadas.

Melhores células (todas com o `t4` como **única** violação do G4):

| base | gain | renew | Δ soma MAE fig8 | Δ fig7a | fecha | t4 |
|---:|---:|---:|---:|---:|---:|---:|
| 0,45 | 1,00 | 0,00 | **−0,1076** | −0,0157 | t1,t2 | +0,0275 |
| 0,45 | 1,00 | 0,35 | −0,0825 | **−0,0197** | t1,t2 | **+0,0105** |
| 0,30 | 1,00 | 0,35 | −0,0992 | −0,0013 | t1,t2 | +0,0202 |

## Por que NÃO ADOTA, e o que fica pendente

O G4 do D-L incluía o `t4` **explicitamente**, e gates são imutáveis. **Zero**
células passam incluindo-o. Ramo aplicado: **NÃO ADOTA (controle paga)**.

## D-M — estatuto do `t4`, decidido em prereg próprio

**DECLARADA por escopo de mecanismo** (fratura por fadiga a ~1500 ciclos).
Gates:

* **G1 (procedência anterior):** ✅ verificada por `git log -S` — os **três**
  registros da fratura (nota do caso, nota de aparato, gotchas do `CLAUDE.md`)
  entraram em **2026-07-03**, commits `3931f1c` e `8acad71`, **33 dias** antes
  desta linha de trabalho.
* **G2 (inproduzibilidade estrutural):** ✅ o cfg do grupo tem **zero** chaves
  `fat*` ⇒ o mergulho é inproduzível por construção.
* **G3 (precedente):** ✅ `lu2024_fig20_T4Nm`, `yang2023ame_axial`.
* **G4 (independência):** ✅ nenhum número do D-L na justificativa gravada.
* **G5:** ⚠️ **erro aritmético meu**, corrigido à vista no prereg: estimei
  "estrita cai de 131 para 130" — errado, o `t4` **nunca estava no tripé**.
  Efeito real: estrita **131 inalterada**, resolvida/declarada **171 → 172**,
  declaradas 15 → 16.

### ⚠️ Disclosure que a validade não exige, mas o leitor merece

O D-M satisfaz o G4 **literalmente** e a procedência é anterior por 33 dias.
Mas **eu vi, numa conferência parcial da saída do D-L, que o `t4` era o
bloqueio ANTES de escrever o D-M**. A validade da declaração não depende disso
— a procedência é independente e verificável —, porém *o momento em que minha
atenção foi para ela* foi provocado pelo D-L. São coisas distintas, e só a
primeira decide o mérito. A segunda fica escrita para você julgar.

## ✅ ADOTADO — a fronteira de grade era o passo que faltava

A disciplina de fronteira (`bounds_saturated`, pré-teste 3 do charter) mudou o
veredicto, e mudou para melhor. **Duas** extensões:

| grade | base | gain | renew | resultado |
|---|---|---|---|---|
| D-L original | 0,15–**0,45** | 0,6–1,0 | 0,0–0,35 | 12 células passam G1, **todas bloqueadas pelo `t4`** |
| ext 1 | **0,45**–0,9 | 0,88–1,0 | 0,15–**0,5** | aparece célula com **zero violações** |
| ext 2 | 0,35–0,6 | 0,88–1,0 | 0,5–**1,0** (limite físico) | **14 de 24** passam tudo; **11 fecham 3/3** |

**Valores adotados — os três COMPARTILHADOS entre seco e óleo:**

```
retight_loss_base = 0,45     (queda no 1º reaperto: a interface assenta)
retight_loss_gain = 0,88     (re-dano por evento; g = 1,88)
k_emb_renew       = 0,65     (renovação PARCIAL do assentamento)
```

Todos **interiores** à união das grades varridas (base 0,15–0,9 · gain 0,6–1,0 ·
renew 0,0–1,0) — nenhum em fronteira. O desempate do mandato escolheu
`gain=0,88` sobre `0,95`/`1,0` porque **1,0 é o topo das duas grades**.

### As 9 curvas, TODAS no tripé

| curva | MAE | res.máx | σ_res |
|---|---:|---:|---:|
| `fig7a_t0` | 0,0149 | 0,0344 | 0,0110 |
| `fig7a_t1` | 0,0130 → **0,0046** | 0,0298 → 0,0122 | 0,0135 → 0,0052 |
| `fig7a_t2` | 0,0069 → **0,0028** | 0,0153 → 0,0055 | 0,0061 → 0,0035 |
| `fig7a_t3` | 0,0101 → **0,0016** | 0,0258 → 0,0053 | 0,0082 → 0,0017 |
| `fig8_t0` | 0,0155 | 0,0380 | 0,0137 |
| **`fig8_t1`** | 0,0533 → **0,0250** | 0,0874 → 0,0389 | 0,0269 → 0,0119 ✅ |
| **`fig8_t2`** | 0,0582 → **0,0361** | 0,0720 → 0,0440 | 0,0193 → 0,0119 ✅ |
| `fig8_t3` | 0,0404 → **0,0350** | 0,0497 → 0,0432 | 0,0135 → 0,0112 |
| **`fig8_t4`** | 0,0371 → 0,0380 | 0,0850 → **0,0787** | 0,0270 → **0,0235** ✅ |

**+3 no tripé** (t1, t2, t4). Controles: as **8** curvas que **soltam** e as
**4** virgens do `fig5` **bit-idênticas**; `t0` de cada cadeia bit-idêntica
(n=0 ⇒ fator 1,0 exato, proteção por construção).

### A claim de física, e o que a testa

**A taxa de re-dano por evento de reaperto é propriedade da SUPERFÍCIE, não do
lubrificante.** O G1 é o teste: os três números são os **mesmos** para seco e
óleo, e as diferenças entre as cadeias saem do `c_D` **já adotado**
(0,5 / 0,03), porque `k_emb_renew` entra multiplicando `D`.

Evidência independente na direção oposta: os **dois** protocolos que
**soltam** o parafuso 30–60° são **planos ou decrescentes** (1,09/1,17 e
0,75/0,93) e ficam **bit-idênticos** — eles não recebem os números, e não
precisam.

### ⚠️ O `t4` fecha por MÉRITO — e a declaração foi RETIRADA

O `t4` entra no tripé com σ **0,0235** (era 0,0270). Portanto a declaração por
escopo (D-M), proposta horas antes, **deixou de ser necessária** e foi
**retirada no mesmo dia**.

Isto **vindica a regra do mandato de forma concreta**: porque me recusei a
declarar-para-desbloquear e em vez disso apliquei a disciplina de fronteira,
cheguei à parametrização que **não precisa de declaração nenhuma** — e que
ainda fecha uma curva a mais. A regra não custou rigor; ela **produziu** o
resultado melhor.

O argumento de escopo do `t4` era válido (os gates G1–G4 do D-M o
confirmaram, com procedência git-verificada a 33 dias) e ficou preservado em
`_DECLARACAO_DISPONIVEL_NAO_TOMADA` — disponível, não tomada. Custo da
retirada: resolvida/declarada 172 → 171; declaradas 16 → 15.

## (registro) A pendência que a extensão resolveu: `base = 0,45` era FRONTEIRA

As **12** células aprovadas estão todas em `base = 0,45`, que é o **topo** da
grade declarada no D-L (0,15 · 0,2 · 0,3 · 0,45). Isso é saturação de limite:
**o ótimo pode estar fora**, e adotar valor de fronteira sem estendê-la é
adotar uma constante cujo ótimo real nunca foi visto — a disciplina de
`bounds_saturated` deste repo existe para isso.

**Próximo passo obrigatório antes de qualquer adoção:** estender a grade
(`base` 0,45 → 0,9) e verificar se o ótimo é interior. Se saturar em 0,9, a
"queda no 1º reaperto" é quase dispensável e a história muda — seria o `renew`
carregando quase tudo, o que é uma claim **diferente** e precisa de prereg
diferente.
