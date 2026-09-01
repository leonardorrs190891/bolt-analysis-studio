# A exceção per-espécime do KARLSEN **não** é curativo de erro de base — falsificada pelo controle

**2026-08-06 (noite)** · sonda `karlsen_run2p2_sonda.py` (só-leitura, 4
simulações) · store `5916d8be0510` · **nada adotado, nada corrigido**.

## A hipótese, e por que ela era plausível

O D-X corrigiu a `run1p2` (F₀ 315 → 331 kN) e ela passou a **MAE 0,0171 sem
parâmetro nenhum** — roda no config de grupo. A `run2p2`, medida no mesmo passo
como **6,6 % baixa** (312 → 332,7), **não** foi corrigida e carrega um
`k_ratchet = 0,003` per-espécime cuja procedência diz:

> *"scatter de coating HV medido 3× (PR-11/11b/11c — vidas 195/230/340 a
> **312-315 kN nominais**)"*

Esses 312–315 kN são justamente os F₀ que o D-X mediu como baixos. Daí a
hipótese: **parte do que foi atribuído a dispersão de espécime é erro de base**,
e a exceção seria um curativo — o que a tornaria removível, ganhando parcimônia.

## O discriminante, escrito antes de medir

CSV grava `F(N)/315` onde deveria gravar `F(N)/331` ⇒ os valores registrados são
**~5 % ALTOS** ⇒ o modelo pareceria cair rápido demais ⇒ **viés NEGATIVO**,
quase uniforme, de 5–6 %.

Controle: a `run7p1` tem F₀ **correto** (+0,4 %) e **também** carrega
`k_ratchet` per-espécime. Se ela mostrar o mesmo perfil, o padrão não
discrimina base de espécime.

## Medido — e o sinal está trocado

| curva | | MAE | viés | mesmo-sinal | nível |
|---|---|---:|---:|---:|---:|
| `run2p2` | com `k_ratchet` | 0,0488 | −0,0194 (−3,2 %) | 57 % | 11 % |
| `run2p2` | **sem** (grupo) | 0,1074 | **+0,0953 (+15,5 %)** | 57 % | 38 % |
| `run7p1` | com `k_ratchet` | 0,0410 | +0,0048 (+0,8 %) | 43 % | 1 % |
| `run7p1` | **sem** (grupo) | 0,1592 | **+0,1542 (+25,1 %)** | 71 % | 50 % |

**Previsto −5 a −6 %; medido +15,5 %.** Sinal trocado e 2,6× a magnitude que o
erro de base poderia explicar. E o **controle mata em definitivo**: a `run7p1`,
cuja base está certa, precisa **mais** do parâmetro (+25,1 %) que a `run2p2`
(+15,5 %).

⇒ **HIPÓTESE FALSIFICADA.** O `k_ratchet` per-espécime cobre um défice **real e
compartilhado**: sem ele o modelo **retém demais** nos espécimes HV — sub-afrouxa.
A exceção não é curativo de dado.

## ⚠️ O que isto NÃO falsifica

**A base da `run2p2` continua errada.** As duas afirmações são independentes: o
+6,6 % foi medido contra o impresso com calibração validada (rms 0,39 px em 46
rótulos), e sobrevive intacto. O que morreu foi a explicação *"a exceção existe
por causa dele"*.

## Subproduto: uma predição de PARCIMÔNIA, agora testável

O défice sem parâmetro ordena-se `run7p1` 25,1 % > `run2p2` 15,5 %, e a
`run2p2` é justamente a que tem dado **artificialmente alto** (menos
afrouxamento aparente). Os valores adotados seguem a mesma ordem —
`run7p1` 0,005 > `run2p2` 0,003.

**Predição registrada:** corrigida a base da `run2p2`, o `k_ratchet` que ela
pede **sobe na direção de 0,005**. Se convergir, os dois espécimes passam a
compartilhar **um** valor — a exceção per-espécime vira exceção **de classe**,
com um parâmetro a menos no total.

Isso reenquadra a dívida do D-X: re-digitalizar a `run2p2` deixa de ser
"correção com risco de −1 no censo" e passa a ser **teste de uma hipótese de
parcimônia**. Estimativa de 1ª ordem para o risco: hoje o viés é −0,0194
(−3,2 %); deflacionar o dado em ~4,9 % moveria o viés para ≈ **+0,011**, ou
seja, **menor em módulo** ⇒ o prognóstico é neutro-a-favorável, não a perda que
eu havia assumido. (1ª ordem só: F₀ também entra na física — pressão, slip,
dano —, então isto orienta, não decide.)

## Custo e ordem

Executar exige extração de pixel da Fig. 10 para a `run2p2` (a correção **não**
é reescala: a `run1p2` teve de ser re-lida porque o ponto âncora estava no
ciclo ~26, o que muda a forma no início). Prereg próprio, com o re-fit do
`k_ratchet` no mesmo passo e a predição de parcimônia como gate.

## Reprodutibilidade

```bash
py -3.12 New_Theory/karlsen_run2p2_sonda.py --json New_Theory/karlsen_run2p2_sonda.json
```

A sonda confere primeiro que o `k_ratchet` **chega** ao runner (`assert kr`) —
sem isso, "sem efeito" se leria como "parâmetro inútil" quando seria "override
nunca aplicado", a armadilha que o `CLAUDE.md` registra em três variantes.
