# CHU: o input de rugosidade está ERRADO nas 9 curvas — e **corrigi-lo piora a métrica**

**2026-08-10** · só-leitura · **nada adotado** · store `9696038085e0`, censo 143/205.

## Como cheguei aqui — e o atalho que quase tomei

A varredura das 29 abertas apontou `chu2026ti_D0p5mm_F0_49kN_Ra1p6um_test9` como adotável via
`N_emb`=100 (×2): CHU 3→4 no tripé, **zero** pioras na fonte. Ia escrever o prereg.

Antes disso, a disciplina de *ler a prova gravada* mandou olhar a **nota de aparato**. Ela diz:

> **Surface finish**: Ra = 0.4 μm baseline (Tests 1-8); Ra = 1.6 μm rougher variant (Test 9
> only) […] candidate for cross-checking the VDI-2230-table-driven `emb_depth_vdi(Ra)` mapping
> **rather than fitting a new roughness tuner**

A nota, escrita meses antes, **nomeava o atalho que eu estava prestes a tomar**.

## O input está errado — nas nove

Todas as 9 curvas do CHU estão registradas com `rz` = **`Rz10-40`**, que é o
`RZ_DEFAULT` — ou seja, **ninguém declarou a rugosidade desta fonte**. Pelo paper:

| curvas | Ra | classe VDI correta | `emb_um` (n_inner=1) |
|---|---|---|---|
| tests 1–8 | 0,4 µm | **`Rz<4`** | **3,5** |
| test 9 | 1,6 µm | **`Rz<10`** | **9,5** |
| *registrado hoje* | — | `Rz10-40` | **11,0** |

⇒ o `emb_depth` das 8 curvas-base está **3,1× alto** (1,1e-05 contra 3,5e-06).

## ⛔ E a correção REPROVA no controle da fonte

| curva | antes | com rugosidade do paper | ΔMAE |
|---|---|---|---:|
| `test1` (D0,3) | 0,0035/0,0082/0,0032 ✅ | 0,0035/0,0082/0,0032 ✅ | +0,0000 |
| `test3` (D0,5) | 0,1381/0,1741/0,0369 | **0,0800/0,1139/0,0303** | **−0,0581** |
| `test8` (F0 73) | 0,1640/0,3456/0,1924 | 0,1613/0,3932/0,1935 | −0,0028 |
| `test9` (Ra1,6) | 0,0449/0,1173/0,0547 | 0,0459/**0,1053**/0,0549 | +0,0010 |
| `test4` (D0,7) | 0,1043/0,2708/0,1255 | 0,1352/0,2264/0,1250 | +0,0310 |
| **`test6_repeat`** (D1,0) | 0,0266/0,0513/0,0285 ✅ | 0,0479/0,1064/0,0362 | +0,0213 |
| **`test5`** (D1,0) | 0,0402/0,0880/0,0436 ✅ | 0,0753/0,1508/0,0546 | +0,0350 |

**Tripé 3 → 1.** Duas curvas **saem** (as duas de D=1,0 mm) e três pioram >+0,01.

## ⚠️ O que isto significa, dito sem suavizar

Não é um botão fitado sendo rejeitado — é o **input correto do paper** sendo rejeitado pela
métrica. **O modelo precisa hoje da rugosidade ERRADA para manter 2 curvas no tripé.**

E o sinal tem forma: a correção **ajuda as amplitudes baixas** (`test3` a D=0,5 mm melhora
0,058) e **prejudica as altas** (as duas de D=1,0 mm degradam 0,021–0,035). Ou seja, com o
`emb_depth` fisicamente correto o modelo passa a errar **na direção da amplitude** — o que
aponta para a dependência de amplitude do embedding (`emb_amp_exp`/ρ-unificação, §4.18) e não
para a profundidade em si.

## ⛔ Consequência imediata: o candidato `N_emb`=100 está RETIRADO

Ele era um ajuste empilhado **sobre um input reconhecidamente errado**. Adotá-lo teria fitado
em torno do erro de input — exatamente o que a disciplina de procedência existe para impedir, e
o que a nota de aparato já advertia por escrito.

Custo declarado: o CHU_2026 fica em **3/9**, e a `test9` volta para as abertas.

## ⚠️ Dois erros meus de instrumento, no mesmo dia, na mesma classe

1. A **primeira** versão deste teste deu **dMAE = +0,0000 nas nove**, idêntico ao dígito. Quase
   escrevi *"a correção de rugosidade é inerte"*. Era **no-op**: eu patchei `inputs_for`, e
   `simulate_case` **não chama** `inputs_for` — ele lê `inp = load["inputs"]`, vindo de
   `_loading_for`. (Havia um segundo defeito latente na mesma linha: escrevi a chave
   `provenance` quando o dicionário real usa `prov`.)
2. A versão correta traz uma **sonda do instrumento antes do veredito** — imprime
   `Rz10-40 -> Rz<4 VIVO`. Sem ela eu teria publicado um null de um teste que nunca rodou.

É a terceira vez hoje que "resultado idêntico ao dígito" era instrumento morto (as outras: o
shell cego para alavancas no default, e o `emb_depth` não-injetável). A regra que sobrevive:
**null só vale com prova de que o instrumento move alguma coisa.**

## O que fica para decisão

O input de rugosidade do CHU está **documentadamente errado** e o registro deveria refleti-lo.
Mas corrigi-lo **sozinho** custa 2 curvas do tripé. As opções são do professor:

* **(a)** corrigir o input e aceitar 143 → 141, registrando que a métrica piorou porque o
  modelo compensava o erro — honestidade acima do número;
* **(b)** corrigir o input **junto** com a dependência de amplitude do embedding, que é o que a
  forma do resíduo aponta — mas isso é **forma nova de engine**, fora do mandato autônomo;
* **(c)** manter como está e registrar a divergência input-vs-paper como dívida conhecida.

Nenhuma delas é adoção de conveniência; a (a) **piora** o número publicado.

## Reprodutibilidade

`chu_rz2.py` no scratchpad — patch em `rn._loading_for` (o ponto certo), com sonda do
instrumento antes de medir. ~4 min, só-leitura.
