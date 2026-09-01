# Fase 1 — as 5 fontes sem piso: medido que **não há par válido**, e por quê

**2026-08-16 (noite)** · store `7a60cacb72de`, censo 144/205 · sondas
**só-leitura**, nada adotado · plano: `New_Theory/plano_das_21_abertas.md`.

Fecha a pergunta que deixava 15 das 21 abertas em `indecidivel_sem_piso` — um
rótulo que se lê como *"ainda não olhamos"*.

## 1. A pergunta foi feita na ordem certa: existe par VÁLIDO não explorado?

Valia perguntar, e não por formalidade: horas antes a sessão A **adotou** o par
`fig8a`×`fig8c` do `ECCLES_2010` (item O, gates 8/8) e o limite daquela fonte
saltou de **0,025 para 0,0698**. Declarar par válido funciona e move a régua.

**Método:** para cada fonte, enumerar *todos* os pares de curvas na mesma
condição nominal (`delta_mm`, `F_amp_N`, `mode`) e **diferenciar o vetor de
input inteiro** — não decidir de memória qual grandeza invalida qual par.

## 2. A resposta, por fonte

| fonte | abertas | pares candidatos | veredito |
|---|--:|--:|---|
| `ICMEZ_2025` | 5 | 4 | **todos** diferem em `grip_mm` **13,8 × 19,8 mm** |
| `ROUSSEAU_2025` | 4 | 1 | difere em `grip_mm` **25 × 29 mm** (espessura t10/t12) |
| `SUN_2025_CRIMP` | 2 | 8 | cruzam **tratamento** (crimp/standard, grease/nogrease) |
| `YANG_2023_IJPEM` | 3 | **0** | 9 curvas em **9 condições distintas** |
| `YANG_2019` | 1 | **0** | 5 curvas em **5 condições distintas** |

⇒ **nas cinco, não existe par válido.** Nas duas últimas o piso é impossível
*por construção* — não há nenhuma condição repetida no experimento publicado.
Nas três primeiras existem pares, e todos cruzam uma grandeza que muda a junta.

**"Indecidível" passa a significar "medido, e não há"** — não "ainda não
olhamos". Para essas 15 curvas não se sabe se o modelo erra ou se a barra de
0,025 é dura, e **a resposta não está no modelo**.

## 3. O caso `SUN_2025_CRIMP` merece registro à parte

As **quatro** curvas transversais compartilham a condição nominal (δ=0,3 mm,
F=6 000 N, disp) e o vetor de input **físico** inteiro. O que as separa são
constantes **fitadas por curva**:

| curva | `loose_arrest_floor` | `tr_loose_gain` | `k_wear_spec` | `emb_depth` |
|---|---:|---:|---:|---:|
| `grease_crimp` | **0,142** | 2,44 | 1,5e-15 | — |
| `grease_standard` | **0,060** | 2,94 | — | — |
| `nogrease_crimp` | (0,08 default) | 0,60 | 2,5e-14 | 1,1e-06 |
| `nogrease_standard` | (0,08 default) | 0,60 | 2,5e-14 | 2,25e-06 |

O piso varia **2,4×** e o ganho **4,9×** entre curvas cuja única diferença
declarada no registry é o caminho da CSV. Isso **não** as torna réplicas — crimp
e graxa são tratamentos físicos reais, e parear seria o mesmo erro do ICMEZ.
Mas registra que a diferença física está codificada **só** como constante
ajustada, sem input que a carregue.

⚠️ Não avanço aqui: a auditoria de procedência das constantes adotadas está
sendo feita pela sessão A (`0dd6534`, `0902639`) e duplicar seria colidir.

## 4. A guarda — `tests/test_par_de_replica_e_mecanicamente_identico.py`

A campanha já **invalidou seis pareamentos**, cada um *depois* de ter sido usado
para assinar exceção (ROUSSEAU, CACCESE, LU ×2, ICMEZ, CHU). Sempre o mesmo
defeito: duas juntas fisicamente distintas tratadas como réplicas. A lição virou
invariante.

**O que se exige** (medido: idêntico em **5/5** dos pares declarados vigentes):
`grip_mm`, `bolt_size`, `rz`, `mu`, `mode`, `frequency_hz` e o drive.

⚠️ **A CARGA fica de fora, de propósito.** O par `karlsen…run2p2`×`run7p1`
difere em F₀ — **333 × 312 kN**, 6,7 % — e a razão declarada diz isso com todas
as letras (*"mesma condição nominal, F₀ alcançado 333 × 313 kN"*). Réplica de
ensaio tensionado **tem** dispersão de pré-carga alcançada, e essa dispersão é
parte do que o piso mede; exigir F₀ idêntico proibiria o par certo. O que se
exige é que a diferença seja **≤ 10 %** — acima disso não é dispersão de aperto,
é outra condição (foi assim que o par `0,5 × 1,0 mm` do LU entrou em 2026-07-31).

**Validada por perturbação:** injetando o par bloqueado do ICMEZ em memória, o
teste falha por **duas** vias independentes — o invariante geral
(`grip_mm 13.8 != 19.8`) e a guarda de regressão nominal (*"foi INVALIDADO e
voltou"*). Ela falha **também** se a diferença sumir do store, para que o
bloqueio não perca a base em silêncio.

## 5. O que isto muda, e o que não muda

**Não muda o censo.** 144/205, nenhuma curva entra ou sai.

**Muda o que a fila significa:** de 21 curvas "em aberto" para **6** onde o
modelo comprovadamente erra (Grupo A do plano, σ 1,8–23× o ruído do próprio
dado) e **15** onde falta dado para julgar.

**E fecha a Fase 1 do plano com um NÃO**, que é resultado: a rota barata de
destravar essas 15 declarando um par não existe. Sobra a Fase 3 — dado novo — e
o alvo mais barato segue sendo o `ICMEZ_2025`: mesmo rig, 8 curvas já
publicadas, e basta **repetir uma condição sem mudar o grip**.

## 6. Reprodutibilidade

```bash
py -3.12 -m pytest tests/test_par_de_replica_e_mecanicamente_identico.py -q
py -3.12 New_Theory/lista_abertas.py
```
A enumeração de pares e o diff de inputs são sondas de sessão sobre o
`validation_store.json` e o `case_registry`; nada foi escrito.
