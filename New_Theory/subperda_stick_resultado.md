# A classe **sub-perda**: o slip do engine é binário por construção — e é a **mesma** bifurcação da P-13, no outro eixo

**2026-08-07** · só-leitura · **nada adotado** · origem: o conserto do
classificador em `mapa_das_65_fora.py`.

## Como esta classe apareceu

Ao consertar o buraco do classificador (o teste do relógio não rodava quando o
dado não caía a 90 %), **7 curvas** ganharam assinatura própria em vez de cair
caladas em `classe_parada`: **o modelo nunca alcança o nível que o dado
alcança**.

| curva | fim do modelo | fim do dado |
|---|---:|---:|
| `10_Yang_2023_…_0_25_mm` | **0,9456** | **0,5200** |
| `yang2021_amp0p8mm_ax6kN` | 0,9796 | 0,7718 |
| `yang2021_fig2_typical` | 0,9834 | 0,7864 |
| `yang2021_amp1p0mm_ax2kN` | 0,9602 | 0,8075 |

O caso extremo perde **5 %** onde o dado perde **48 %**.

## O mecanismo, medido: **stick permanente**

Instrumentando `resolve_transverse_slip`: **6 das 7 têm slip exatamente
`0,0000 µm`**, com `delta_amp` imposto de **0,25 a 1,0 mm**. (A sétima,
`liu2020_fig9`, desliza 399 µm — causa diferente, sai da classe.)

Consequência direta na decomposição: **wear 0 % e rotacional 0 %** nas sete. Os
dois canais dirigidos por slip estão zerados e sobram embedding + creep, que
**saturam por construção** (assíntota em `emb_depth`; log no creep). Um modelo
cujos únicos canais ativos saturam **não pode** produzir perda sustentada — a
sub-perda é consequência, não coincidência.

## A procedência do `c_bend` registrava o sintoma sem reconhecê-lo

O `adopted_configs.json` do YANG_2021 diz:

> *"`c_bend` fitado-this-rig (1º DOF da fonte, PR-3/reclassificação; **banda
> INSENSÍVEL 0,02–0,15** — valor no centro, **não identificado além da banda**)"*

Em toda essa banda a junta está travada ⇒ nada muda ⇒ o parâmetro **parece**
insensível. É a regra do `CLAUDE.md` — *"grade que dá resultado IDÊNTICO =
INÉRCIA, não robustez"* — acontecendo dentro de uma adoção assinada. A banda não
era robustez: era **parâmetro morto**, e o fit ficou preso dentro dela.

## ⛔ Destravar NÃO conserta — e o negativo é o achado

Varredura de `c_bend` **muito além** da banda, nas 8 curvas comparáveis da fonte
(as 3 que passam servem de controle):

| `c_bend` | slip mediano | soma de MAE | tripé |
|---:|---:|---:|---:|
| **0,1** (vigente) | 0,00 µm | **0,3328** | **3/8** |
| 0,3 | 0,00 µm | 1,9622 | 3/8 |
| **1,0** | **432,85 µm** | **6,0281** | **0/8** |
| 3,0 | 537,39 µm | 6,1187 | 0/8 |
| 100,0 | 597,94 µm | 6,1519 | 0/8 |

**O stick não é bug — é o que torna a fonte ajustável.** Fora dele o modelo cai
direto em gross slip (433–598 µm de um curso de 0,5–1,0 mm) e perde tudo: a soma
de MAE piora **18×** e as 3 curvas que passavam caem.

⇒ não há valor de `c_bend` que sirva. O defeito não é de **constante**.

## Onde está o defeito, com endereço exato

`resolve_transverse_slip`, no modo deslocamento:

```python
delta_slip_onset = mat.delta_free + F_slip / k_tr
return max(0.0, delta_amp - delta_slip_onset)
#   docstring: "Zero significa stick (SEM HYSTERESIS)"
```

**Limiar duro por construção.** Abaixo do onset o slip é exatamente zero e a
dissipação é **nula**; acima, linear no excesso. Não existe microslip graduado.

Isso é fisicamente falso: em **partial slip** (Cattaneo–Mindlin) a zona anular
escorrega e dissipa **antes** do gross slip — é o regime de *fretting*, o
mesmo que a literatura da fonte descreve.

⚠️ **E o engine TEM a maquinaria — no lugar errado.** `partial_slip_gate` e
`slip_regime_mode="cattaneo_mindlin"` agem **a jusante**, modulando a *fração de
energia* de uma amplitude de slip que **já é zero**. Multiplicar 0 por qualquer
gate dá 0. **É por isso que o CM foi medido INERTE** (Δ = 0,0000 nos 6 canais,
2026-07-30): não é que o modo não faça nada — é que ele opera sobre um número
que o resolvedor já zerou.

## A unificação: é a **mesma** bifurcação da P-13

| eixo | dois atratores do modelo | onde o dado vive |
|---|---|---|
| **arresto** (P-13) | piso `F_min` **ou** *runaway* a zero | entre eles, platô não-nulo |
| **slip** (esta classe) | stick total **ou** gross slip | entre eles, perda graduada |

Os dois são *"o modelo é **bimodal** onde o dado é **graduado**"*. Isso não
funde as duas propostas — os mecanismos e os consertos são distintos —, mas
identifica uma **assinatura de projeto** que se repete: onde o engine usa
`max(0, ·)` ou `if/else` de regime, ele produz bifurcação; onde o dado é
contínuo, falta a transição suave.

## O que proponho registrar (P-14) — decisão sua

> **Microslip abaixo do onset de gross slip.** `resolve_transverse_slip`
> devolveria uma amplitude **efetiva** não-nula abaixo do limiar (fração de
> Cattaneo–Mindlin da zona anular), em vez de `max(0, ·)`. Alcance medido: **6
> curvas** em 2 fontes com slip exatamente 0 e δ de 0,25–1,0 mm; e resolve por
> construção a inércia do `slip_regime_mode`, que hoje modula zero.

⚠️ **Não medido:** que a forma conserte as 6. O que está medido é que **o
canal que carregaria a perda está desligado por um limiar duro**, que nenhuma
constante o religa (varredura de 3 ordens de grandeza), e que a maquinaria de
partial slip existente **não pode** agir porque roda a jusante do zero.

⚠️ **Risco MEDIDO — pela medição DIRETA do slip resolvido**, instrumentando
`resolve_transverse_slip` nas **150** curvas disp-mode:

| população tocada | curvas |
|---|---:|
| stick real (slip **máx** = 0 em **todos** os ciclos), **dentro do tripé** — risco | **6** |
| stick real, **fora do tripé** — alvo da forma | **12** |
| **total tocado** | **18** |
| deslizam normalmente (proposta **não** as afeta) | 132 |

Fontes: `YANG_2021` 8 (a fonte **inteira**) · `YANG_2023_IJPEM` 3 · `LIU_2025` 2
· `LU_2024` 2 · `ZHANG_2006` 2 · `ROUSSEAU_2025` 1.

### ⛔ E o BALANÇO DE CENSO é **−1** — a P-14 não se justifica pelo placar

Escrevi *"risco : ganho ≈ 1 : 2, favorável"* e **estava errado**. Duas coisas
faltavam:

**(a) O SINAL do viés decide.** Microslip **adiciona** perda ⇒ só ajuda quem
**retém demais** (viés positivo). Das 18 em stick: **10 positivas** (ajuda) e
**8 negativas** (piora).

**(b) "Curva fora" ≠ "ganho de censo".** Cinco das que eu contava como alvo já
são **declaradas ou exceção** — consertá-las não move o placar. Entre elas a
`zhang2006_fig3_illus`, que tem o **maior** viés positivo (+0,2078) e é
declarada por procedência (figura rotulada *"Illustration"*).

| efeito no censo | curvas |
|---|---:|
| **ganho possível** (aberta + fora + viés **positivo**) | **4** |
| **risco** (no tripé + viés **negativo**) | **5** |
| já têm estatuto (não movem o placar) | 5 |
| piorariam, mas já estão fora | 3 |
| neutra | 1 |
| **balanço líquido possível** | **−1** |

As 4 de ganho: `yang2021_amp0p5mm_ax8kN` (+0,0433) · `yang2021_amp0p6mm_r1`
(+0,0264) · `yang2021_amp1p0mm_ax2kN` (+0,0541) · `10_Yang_2023_…_0_25_mm`
(+0,1664). As 5 de risco: `lu2024_fig18_amp0p25` · `rousseau_steel_t14` ·
`yang2021_amp0p6mm_r2` · `r3` · `zhang2006_fig16_runout`.

⚠️ **Isto NÃO derruba a P-14 — separa duas afirmações que eu tinha misturado:**

* **argumento de FÍSICA (íntegro):** o `max(0, ·)` desliga três canais de uma
  vez, nenhuma constante o religa (varredura de 3 ordens de grandeza), e a
  maquinaria de partial slip existente não pode agir porque roda a jusante do
  zero. Isso é defeito estrutural, medido;
* **argumento de PLACAR (falso):** *"a forma renderia curvas"*. Renderia **4** e
  arriscaria **5**.

⇒ a P-14 deve ser decidida **como correção de física**, e o custo provável no
censo (−1) tem de estar na mesa. As magnitudes são assimétricas — os ganhos
precisam de +0,03 a +0,17 de perda extra, os riscos toleram bem menos —, o que
significa que o **mesmo** parâmetro dificilmente serve aos dois lados.

Curva que já desliza está no regime linear e **não** é afetada por uma mudança
*abaixo* do onset — por isso o alcance é 18, não 150. Ainda assim exige gate de
inércia (fração → 0 recupera o atual bit-a-bit) antes de medir mérito.

Nota lateral que vale registrar: as **8** curvas do `YANG_2021` estão em stick,
**incluindo as 3 que passam o tripé** — elas são reproduzidas por embedding +
creep sozinhos.

### ⚠️ TRÊS correções do meu próprio instrumento, no caminho

As contagens intermediárias foram **99** e depois **44**, ambas erradas, e o erro
é o mesmo repetido: **inferir mecanismo de um zero sem conferir por que ele é
zero.**

1. **Omiti o `thread_fretting`.** Contei só `wear + rotational_loosening` como
   "canais de slip", e há um terceiro. A `liu2016wear_fig7_run1` o tem a
   **12,6 %** — não está em stick. Só no `LIU_2016` isso inflava de **1 para 14**.
2. **Contei curvas em modo FORÇA**, onde `resolve_transverse_slip` toma o ramo de
   força e a proposta não se aplica.
3. **Confundi "canal zerado" com "junta travada".** O `LIU_2020_WEAR` e o
   `KARLSEN_2022` têm `K_archard = 0`, `k_wear_spec = 0` e `tr_loose_gain = 0`
   **nas configs adotadas** — canais desligados **de propósito**. Essas curvas
   deslizam: a `liu2020_fig9_AF0.4mm` resolve **399 µm** de slip. O que denunciou
   foi medir o *onset* e ver razão `onset/δ` de **0,00×** numa curva que eu havia
   classificado como travada.

**Regra que fica:** um canal em zero tem três causas distintas — driver zerado
(stick), constante zerada (config) e gate fechado (companheiro) — e só a medição
**direta do driver** as separa. A decomposição não distingue nenhuma delas.

## Reprodutibilidade

```bash
py -3.12 New_Theory/yang2021_stick_premeasure.py    # varredura de c_bend
py -3.12 New_Theory/mapa_das_65_fora.py             # a classe sub-perda
```

A medição de slip é instrumentação de `dsa.resolve_transverse_slip` (wrapper que
registra o retorno), no scratchpad.
