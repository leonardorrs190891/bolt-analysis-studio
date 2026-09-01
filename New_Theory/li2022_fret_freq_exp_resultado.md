# D-T — `fret_freq_exp`: o VALOR 3,57 falsificado, o MEMBRO **data-blocked**

**2026-08-05** · prereg `docs/superpowers/specs/2026-08-05-li2022-fret-freq-exp-prereg.md`,
escrito **antes** da medição. Store `b70276f2fa43` (pós-D-Q e D-S). Rota
**override**; nada adotado, nada escrito.

## O teste

`fret_freq_exp = 3,57`, **derivado da conta**, não varrido:

```
e = ln[(r_alvo − 1)/s + 1] / ln(f_hi/f_lo) = ln(11,80)/ln(2) = 3,57
```

com `s = 0,093` (fatia do flanco a 10 Hz, decomposição pós-D-Q) e
`r_alvo = 2,009` (razão de perda 10 Hz ÷ 20 Hz que o dado pede).

## Resultado

| curva | MAE antes | MAE depois | σ antes | σ depois | perda | estado |
|---|---:|---:|---:|---:|---:|---|
| `axial_10Hz_full` | 0,0227 | 0,0292 | **0,0214** | **0,0284** | 0,2121 | **SAIU** |
| `axialmin_10Hz` | 0,0589 | **0,0220** | 0,0226 | 0,0233 | 0,1984 | **ENTROU** |
| `axialmin_15Hz` | 0,0323 | 0,0323 | 0,0166 | 0,0166 | 0,1325 | ok |
| `axialmin_20Hz` | 0,0146 | **0,0081** | 0,0179 | **0,0073** | 0,0956 | ok |

* **G0** instrumento ✅ (`fret_freq_exp`=3,57 chega ao runner, `flank_wear_on`=1)
* **G4** isolamento ✅ (o LIU_2016 recebe `None` — verificado, não assumido)
* **G5** razão do modelo: **2,076** contra alvo **2,009** (base 1,003)
* **G1** a alvo entra no tripé: **PASSA**
* **G3** nenhum pior > +0,010: **PASSA**
* **G2** nenhuma aprovada sai: **FALHA** — `axial_10Hz_full`, σ 0,0214 → **0,0284**

⇒ **RAMO: FALSIFICADO**, pelo gate escrito antes — **do VALOR 3,57**.

## ⚠️ CORREÇÃO, medida logo depois: o MEMBRO não está falsificado

O prereg testou **um** valor derivado e o falsificou. Isso mata o **valor**, não a
alavanca — e a curva-alvo entrou com MAE **0,0220** contra um limite de 0,05,
folga enorme. Declarar o membro morto sem varrer seria conclusão sobre a
população errada (mesma classe do erro de 2026-07-30, quando a triagem julgou
contra a régua vencida). Varri:

| exp | `full` mae/σ | `axialmin_10Hz` | `15Hz` | `20Hz` | tripé |
|---:|---|---|---|---|:---:|
| base | 0,0227/0,0214 | 0,0589/0,0226 | 0,0323/0,0166 | 0,0146/0,0179 | 3/4 |
| 0,50 | 0,0211/0,0230 | 0,0538/0,0219 | 0,0323/0,0166 | 0,0125/0,0158 | 3/4 |
| **1,00** | **0,0217/0,0249** | **0,0481/0,0215** | 0,0323/0,0166 | **0,0110/0,0140** | **4/4** |
| 1,50 | 0,0233/0,0266 | 0,0420/0,0215 | 0,0323/0,0166 | 0,0101/0,0123 | 3/4 |
| 2,00 | 0,0243/0,0279 | 0,0354/0,0219 | 0,0323/0,0166 | 0,0094/0,0107 | 3/4 |
| 2,50 | 0,0256/0,0287 | 0,0292/0,0224 | 0,0323/0,0166 | 0,0087/0,0094 | 3/4 |
| 3,00 | 0,0278/0,0290 | 0,0249/0,0229 | 0,0323/0,0166 | 0,0081/0,0083 | 3/4 |
| 3,57 | 0,0292/0,0284 | 0,0220/0,0233 | 0,0323/0,0166 | 0,0081/0,0073 | 3/4 |

**Existe janela, e ela fecha as 4 curvas da fonte.** O requisito (b) da regra de
parada **NÃO** está cumprido para este membro.

### E o valor tem âncora FÍSICA, não é melhor-placar

`fret_freq_exp = 1` significa taxa de fretting **∝ 1/f**, isto é, desgaste por
unidade de **TEMPO** constante em vez de por ciclo — a leitura padrão de efeito de
frequência em fretting (ejeção de detritos e oxidação são processos temporais, não
cíclicos). E é **o mesmo expoente que o DADO pede independentemente**: `a = 1,006`
no par 10–20 Hz e 0,978 no ajuste global. Duas derivadas independentes apontam
para 1.

### ⚠️ Mas a janela é estreitíssima, e isso põe a decisão em outro lugar

Em `exp = 1,00` a `full` fica com σ **0,0249** contra o limite 0,025 — **0,4 % de
margem**. No **D-Q**, horas antes, recusei a célula 3,5e-6 exatamente por ter
**2,4 %** de margem, com o argumento de que re-carimbos movem σ em 0,001–0,003.
**0,4 % é seis vezes mais frágil que o que recusei.** Aplicar meu próprio
critério de forma consistente exige ou (i) achar uma borda de janela com margem
utilizável, ou (ii) não adotar.

Refinamento das bordas (7 expoentes a mais):

| exp | `axialmin` MAE (÷0,05) | `full` σ (÷0,025) | margem da perna que aperta |
|---:|---|---|---:|
| 0,70 | 0,0516 (1,03×) | 0,0238 | — (fora) |
| 0,80 | 0,0504 (1,01×) | 0,0241 | — (fora) |
| **0,90** | 0,0493 (0,986×) | 0,0245 (0,980×) | **1,4 %** |
| 0,95 | 0,0487 (0,974×) | 0,0247 (0,988×) | 1,2 % |
| 1,00 | 0,0481 (0,962×) | 0,0249 (0,996×) | 0,4 % |
| 1,05 | 0,0475 | 0,0250 (1,00×) | — (fora) |
| 1,10 | 0,0469 | 0,0252 | — (fora) |

**Janela = [0,85 · 1,02]**, e a melhor margem obtenível em toda ela é
**~1,7 %** (perto de exp 0,92). Menor que os **2,4 %** que recusei no D-Q horas
antes. E o valor com âncora física (1,0) é justamente o de **pior** margem.

## ⛔ O QUE DECIDE NÃO É A MARGEM — é que a biblioteca NÃO PODE TESTAR esta forma

O canal de flanco está ativo em **2 de 69** grupos: `LI_2022_TRIBOINT` (o alvo) e
`LIU_2016`. E o `LIU_2016` é de **frequência ÚNICA** — medido: as 14 curvas têm
`frequency_Hz` idêntico (nenhuma varredura de f).

⇒ aplicar `fret_freq_exp` ao LIU_2016 testaria se um **rescale uniforme** do
canal quebra a fonte — **não** se a lei de frequência transfere. **Não existe
held-out na biblioteca capaz de falsificar esta forma.** A lei só é observável na
própria fonte-alvo; adotá-la seria **ajustar e testar na mesma curva**.

O próprio prereg do **D-Q** fixou a regra, e ela vale aqui com mais força porque
um **expoente de lei** é afirmação de FORMA, não constante per-rig:

> *"Prefiro este ramo [FALSIFICADO] a soltar um segundo `flank_fret_depth` por
> fonte — o valor do candidato está na transferência."*

### Isto revela um BURACO na regra de parada

O requisito (b) prevê dois estados por membro: **falsificado** ou **não testado**.
Este membro é um **terceiro**: **NÃO-TESTAÁVEL COM A BIBLIOTECA**. Não é
falsificação — a janela existe, é fisicamente ancorada e fecha **4/4**. E não é
pendência de trabalho — **nenhum esforço meu produz o held-out**; só uma fonte
nova, com canal de flanco **e** varredura de frequência, o produziria.

**Proposta de emenda à regra** (`regra_de_parada_proposta.md`, aguarda
assinatura): acrescentar o estado **`data-blocked` por membro** — candidato cuja
falsificação exige dado que a biblioteca não tem. Um membro `data-blocked`
**não** satisfaz (b) e **não** bloqueia a parada indefinidamente: ele suspende a
classe até que dado novo entre, e a reabertura automática já prevista na regra
(mudança de dado) cobre exatamente isso.

## As três predições registradas acertaram

1. *"a razão sobe muito mas fica ABAIXO de 2,009; palpite entre 1,5 e 2,5"* →
   **2,076**. Dentro da faixa; e note que ela ficou ligeiramente **acima** de
   2,009, não abaixo — a atribuição *a posteriori* subestimou de pouco a
   capacidade do canal, coerente com a regra de 2026-07-29 (alavanca que troca a
   LEI pode mover a própria fatia).
2. *"a `axial_10Hz_full` PIORA"* → **sim, e é ela que reprova o teste**.
3. *"a `axialmin_20Hz` melhora"* → **sim, e muito** (MAE 0,0146 → 0,0081;
   σ 0,0179 → 0,0073).

**O mecanismo FUNCIONA.** O que ele não faz é caber no orçamento de dano.

## O que a falsificação revela — e é mais do que "não deu"

### (a) O troco é UM-POR-UM: censo líquido ZERO

Entra `axialmin_10Hz`, sai `axial_10Hz_full`. Mesmo **ignorando** o G2, o censo
não se move. Não há versão desta adoção que dê +1.

### (b) O troco é a AMBIGUIDADE DE BASE reaparecendo

As duas curvas que trocam de lado são **as duas de 10 Hz**, e os dados delas
discordam em nível por **4,2 %** (medido em
`fila_form_limited_3_anatomia.md` §3): a Fig. 8(c) normaliza por **12,0 kN**
(base validada 3×) e a digitalização da Fig. 8(a) por **11,5 kN**.

Com `fret_freq_exp` o modelo **caminha para a base da `axialmin` e se afasta da
base da `full`**. Não é coincidência de parametrização: o modelo dá **uma** curva
para a condição, e a fonte publica **duas** que diferem por mais que a
tolerância. Qualquer alavanca de nível a 10 Hz vai trocar uma pela outra.

⇒ **a última curva da fila não é fechável enquanto a base de 10 Hz da fonte
estiver ambígua.** Isso é questão de DADO, e o paper não a resolve: a Fig. 8(a)
não tem rótulo que valide sua base, e as duas curvas foram medidas em
**espécimes distintos** (falsificada a hipótese de duplicata — nenhuma
atribuição de base faz as trajetórias absolutas coincidirem).

### (c) O pivô em 15 Hz

A `axialmin_15Hz` fica **exatamente** igual (0,0323 / 0,0166, perda 0,1325). A lei
de `fret_freq_exp` pivota em ~15 Hz nesta configuração — as perdas vão
0,1327/0,1325/0,1323 (base) → 0,1984/**0,1325**/0,0956. Registrado como fato do
instrumento; não foi previsto e não afeta o veredicto.

## Estado da regra de parada para a classe "lei de frequência"

| requisito | estado |
|---|---|
| (a) classe identificada por ≥2 instrumentos independentes | ✅ re-atribuição creep→flanco (0 %→93 %) + invariância de perda/teto de autoridade |
| (b) **todo** membro falsificado por predição pré-registrada | **re-pesagem de canais**: ✅ falsificada por **álgebra** (teto 1,0753 a 100 % de fatia contra alvo 2,009) · **`fret_freq_exp`**: ⛔ **DATA-BLOCKED** — o valor 3,57 foi falsificado, mas existe janela [0,85·1,02] que fecha 4/4, e **não há held-out** capaz de testá-la (o único outro grupo com canal de flanco é de frequência única) · **kernel de creep**: ❌ não testado, fora de escopo por raio de explosão |
| (c) retorno marginal nulo | a fila é 1 curva; em `exp=3,57` este membro dá **+1 −1 = 0**, mas na janela [0,85·1,02] daria **+1** (4/4 na fonte) |

**Falta exatamente um membro**, e ele está **fora de escopo de sessão por raio de
explosão**: trocar o kernel de creep de `log` para ~linear em t atinge toda a
população dominada por creep (CACCESE_2009 7/7, JCSR_2023, QIN_2024,
LI_2022_MARSTRUC, ZHANG_2018 9/9) — dezenas de curvas — por **+1**, e o **D-H
acabou de adotar `creep_mode="saturating"` no CACCESE porque lá a curvatura do
log erra na direção OPOSTA**. É decisão do professor, com estes números na mão.

## Recomendação (não executada)

**Não adotar**, e o motivo principal **não é** a margem — é que a biblioteca não
tem held-out para esta forma. Adotar seria soltar um **expoente de lei por
fonte**, ajustado e testado na mesma curva, contra a regra que o D-Q acabou de
aplicar contra si mesmo.

Três rotas que **destravariam** o candidato, em ordem de custo:

1. **Fonte nova com canal de flanco E varredura de frequência.** É o held-out que
   falta. Sem ela o membro fica `data-blocked` por tempo indeterminado.
2. **Resolver a base de 10 Hz** (o troco de `exp=3,57` era a ambiguidade de base
   reaparecendo): digitalizar a Fig. 8(a) por pixel com calibração validada — o
   pixel do traço dá **11,18 kN**, nem 11,5 nem 12,0 — ou declarar uma das duas
   fora do censo por procedência de base. **É medição que posso fazer**, mas
   nenhuma das duas fecha a curva sozinha: elas mudam **qual** das duas o modelo
   erra, não o fato de haver duas.
3. **Assinar a adoção do jeito que está**, declarando por escrito que
   `fret_freq_exp` é per-fonte e sem held-out, e escolhendo o valor entre a
   âncora física (1,0; margem 0,4 %) e o centro da janela (~0,92; margem ~1,7 %).
   Decisão sua — eu não a tomo por delegação, porque ela **relaxa uma regra**, e o
   mandato me proíbe exatamente isso.
