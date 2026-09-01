# A camada `classe_parada` atribui **por fonte**, e o membro novo não tem o defeito da classe

**2026-08-14** · só-leitura · **nada adotado** · store `cb019d75c6c2`, censo **140/205** ·
módulos limpos no HEAD `c006cf6` (conferido antes de medir).

## O gatilho

Depois do G+H, a camada `classe_parada (aceleração tardia)` foi **8 → 9**. Ela é a camada que
diz *"esta classe de defeito foi encerrada pela regra de parada — as curvas estão erradas e
nós sabemos; declará-las inflaria o 'resolvido' com fracasso"*. **Ganhar membro em silêncio é
o oposto do que ela existe para fazer**, então fui ver quem entrou.

## O membro novo entrou por PERTENCER À FONTE, não por ter o defeito

`chu2026ti_D1p0mm_F0_49kN_test5`. O `classificar` da triagem roteia por
`_FONTES_CLASSE_PARADA` — uma lista de **fontes** (`CHU_2026`, `JCSR_2023`, `LIU_2025`,
`YANG_2019`, `YANG_2021`) — então qualquer curva dessas fontes que passe a falhar herda o
rótulo *"aceleração tardia"* **sem que isso seja verificado**.

E a `test5` não passou a falhar por acelerar tarde: passou a falhar porque o **limite da
fonte apertou** de 0,0507 para 0,0296 quando o piso ilegítimo caiu. O σ dela sempre foi
0,0436.

## A medição que desqualifica o rótulo

| curva | MAE | \|viés\|/MAE | ρ(resíduo, N) | leitura | passa? |
|---|---:|---:|---:|---|---|
| **`chu…test5`** | 0,0402 | 0,48 | **+0,94** | rampa (taxa) | não |
| **`chu…test6_repeat`** | 0,0266 | 0,40 | **+0,86** | rampa (taxa) | ✅ **sim** |
| `chu…test2` | 0,1543 | 0,36 | +0,91 | rampa | não |
| `chu…test4` | 0,1043 | 0,24 | +0,21 | **offset** | não |
| `liu2025_amp0p25` (classe canônica) | 0,0757 | 1,00 | **−0,73** | rampa, **sinal OPOSTO** | não |
| `yang2021_amp0p5mm` | 0,0324 | 0,89 | +0,89 | rampa | não |

**Dois fatos, e o segundo é o que decide:**

1. **Os membros canônicos da classe nem compartilham o sinal de ρ** (`liu2025` em −0,73
   contra `yang2021` em +0,89), e dentro do próprio CHU há offset puro (`test4`, ρ +0,21).
   ⇒ a classe, como conjunto, **não tem assinatura única de resíduo** — atribuir por fonte
   não é obviamente pior que atribuir por assinatura, porque a assinatura não separa.
2. ⚠️ **A `test5` tem a MESMA assinatura da sua própria réplica — e a réplica PASSA.**
   `test6_repeat`: ρ +0,86, |viés|/MAE 0,40, MAE 0,0266. São a mesma condição, o mesmo
   comportamento, e a diferença é de **magnitude** (σ 0,0436 × 0,0285), não de **espécie**.

⇒ chamar a `test5` de *"aceleração tardia, classe encerrada"* afirma *"sabemos que está
errada e paramos de trabalhá-la"*. O enunciado honesto é **"é o pior lado de um par de
réplicas cujo lado bom passa"** — que é dispersão entre espécimes, não classe de defeito
fechada.

## O que isto é, e o que não é

**Não é** proposta de mover a curva: reclassificação de camada **exige assinatura**, e o
efeito no censo seria zero (ela fica fora do tripé de qualquer modo).

**É** um aviso de que a camada tem um **modo de erro por construção**: ela absorve, com
rótulo de "classe encerrada", qualquer curva que passe a falhar numa das 5 fontes — inclusive
por motivo alheio ao defeito da classe, como uma correção de piso. Uma curva estacionada ali
**não volta a ser olhada**, e é esse o custo.

⚠️ **Rota F7 medida, para o registro:** a `test5` **não** tem. Sua família legítima
(`test5` × `test6_repeat`) dá piso σ **0,0296**, e o σ dela é **0,0436** = **1,47×** o piso —
ela falha até contra a própria réplica.

## Sugestão (barata, sem assinatura)

Fazer o `classificar` exigir, além da fonte, que a curva **não tenha entrado por mudança de
limite** — ou, mais simples, que a triagem **imprima** quando um membro é novo na camada.
Hoje o número 8 → 9 aparece sem que ninguém saiba que mudou de composição, e foi só porque
eu estava rastreando as consequências do G+H que isto apareceu.

## Reprodutibilidade

`classificar`/`_FONTES_CLASSE_PARADA` de `regra_de_parada_triagem.py`; ρ de Spearman e
`|viés|/MAE` sobre `metric_pred`/`metric_data` do store. Segundos, só-leitura.
