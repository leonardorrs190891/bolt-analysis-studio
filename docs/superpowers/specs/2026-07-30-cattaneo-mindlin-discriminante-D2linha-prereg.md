# PRÉ-REGISTRO — discriminante **D2′** para o Cattaneo-Mindlin

**Escrito em 2026-07-30, ANTES de medir.** Congelado no commit que o introduz.
Substitui o **D2** do prereg `4086ca9`, que foi **retirado por falha de
instrumento** (não por resultado) — a justificativa está na §1 e é obrigatória:
retirar um discriminante depois de ver o resultado é exatamente o que um
pré-registro existe para impedir, então o motivo tem de ser um defeito
**verificável do instrumento**, não o veredicto que ele deu.

---

## 1. Por que o D2 foi retirado (três defeitos, todos verificáveis)

O D2 pedia: *"a melhora tem de ordenar pela proximidade do limiar `r = F_amp/cap`
no 1º ciclo; Spearman(|log r|, ganho) ≤ −0,50"*.

1. **Preditor sem variância.** Medido na fila inteira: `r` tem **dois valores
   distintos** (1,69 e 2,67). Motivo estrutural — `Q = F_amp·|sin θ|` e o
   `F_amp` da maioria dos casos é uma **razão fixa de F₀**, então
   `r ≈ razão/(µ·κ)` não depende da curva. Spearman sobre 8 pontos com 2 valores
   distintos não mede ordenação.
2. **`nan` em 10 das 18.** O espião de `partial_slip_gate` não registrou nada
   nessas curvas ⇒ o gate **não foi chamado**.
3. **O sítio observado é o errado — e este é o defeito grave.** O
   `slip_regime_mode="cattaneo_mindlin"` age em **DOIS** lugares do engine:

   | sítio | o que gateia | fórmula | condição |
   |---|---|---|---|
   | `partial_slip_gate` | **wear / fretting** | `g = 1−(1−r)^m`, `r = Q/(µ·F₀·κ)`; `g=1` se `r ≥ 1` | sempre que o canal é avaliado |
   | `loosening_slip_gate` | **afrouxamento rotacional** | `g = frac^k`, `frac = slip/(slip+δ_t) = max(0, 1−1/r)`, `k = slip_regime_sharpness` | só com `slip_amp ≠ None` |

   **Em 5 das 7 curvas que FECHARAM o tripé o `partial_slip_gate` nunca foi
   chamado** ⇒ quem agiu foi o segundo sítio. O D2 media um gate que não estava
   operando naquelas curvas.

⇒ O D2 é **inconclusivo por instrumento**. Nem PASSA nem FALSIFICADO: o teste não
testou. (E o prereg `4086ca9` não tinha ramo para isso — lição registrada: a lista
de ramos precisa sempre incluir *"o teste não testou"*.)

## 2. O que o candidato tem de mérito, e por que ele não basta

Medido (prereg `4086ca9`, fila de 18 form-limited): **7 curvas fecham o tripé,
0 pioram > +0,01**, as demais em Δ = 0,0000 exato. Levaria o tripé de 105 para 112.

**Mérito não é mecanismo.** Adotar isto sem discriminante é adotar número — o erro
que a incubação ensinou a custo de 10 linhas. Daí o D2′.

## 3. O mecanismo alegado, dito com precisão

Não é "menos wear". É **taxa dependente do estado acumulado**: como
`cap ∝ F₀` e `δ_t = δ_free + F_slip/k_tr` encolhe conforme F₀ cai, ambos os gates
**abrem ao longo do ensaio**. A perda é **suprimida cedo** (partial slip / stick) e
**liberada tarde** (gross slip) ⇒ a distribuição temporal da perda muda, que é a
única coisa capaz de mexer no σ_res sem mexer no nível (achado da atividade F: 53 %
da dispersão é rampa, 16 % curvatura).

## 4. D2′ — três testes. Imutáveis a partir deste commit.

### Teste A · ATRIBUIÇÃO (condição necessária, binária por curva)

Instrumentar **os dois** sítios e registrar, por curva: se cada um foi chamado, e a
média/trajetória de `g`.

**FALSIFICA se:** alguma curva melhora (`Δσ_res > 0,002`) com **ambos** os gates
em `g ≡ 1,0` — sem gating não pode haver efeito do mecanismo, e a melhora vinda de
outro lugar é confusão de identificação.

Sem problema de spread: é presença/ausência.

### Teste B · CONTROLE DE GATE CONGELADO — o teste decisivo

Para cada curva: (i) rodar CM e gravar a trajetória `g(n)` do sítio que age;
(ii) computar a média temporal `ḡ`; (iii) re-rodar com o gate **congelado em `ḡ`**
(mesma média, **sem migração**), tudo o mais idêntico.

- Se o mecanismo é a **migração**, congelar destrói a melhora.
- Se a melhora **sobrevive** congelada, o CM está agindo como **reescala constante**
  de um canal — alavanca de NÍVEL disfarçada, não bifurcação.

**PASSA se:** `(Δσ_CM − Δσ_congelado) / Δσ_CM ≥ 0,50` na **mediana** das curvas que
melhoram (a migração responde por ≥ metade do ganho).
**FALSIFICA se:** < 0,25 (o ganho é essencialmente reescala).
Entre 0,25 e 0,50: **PARCIAL** — componente misto, declarar as duas frações.

> O gate congelado **não é modelo físico**; é *controle*, e existe só para isolar a
> componente temporal. Isto fica dito para ninguém o adotar por engano.

### Teste C · ORDENAÇÃO PELA MIGRAÇÃO (o D2 consertado)

Preditor novo: `Δg = g(último ciclo) − g(1º ciclo)`, **medido** por curva no sítio
que age. Ele varia por construção (é trajetória, não constante estrutural).

**PASSA se:** Spearman(`Δg`, ganho de σ_res) **≥ +0,50** **e** as curvas com
`Δg ≤ 0,02` ficam inertes (|Δσ| ≤ 0,002).
**FALSIFICA se:** |ρ| < 0,30 (melhora uniforme, indiferente à migração) ou ρ ≤ −0,30
(ordenação invertida).

⚠️ **Guarda contra o erro que já cometi duas vezes hoje:** se o preditor sair com
menos de **4 valores distintos** ou `nan` em mais de 1/3 da fila, o Teste C é
declarado **INCONCLUSIVO** e **não** conta como falsificação. A verificação do
spread é feita e impressa **antes** de calcular o ρ.

## 5. Gates de mérito (inalterados do `4086ca9`)

**G1** ≥ 1 curva fecha · **G2** ninguém do acervo piora > +0,01 · **G3**
`Δσ/ΔMAE ≥ 1` · **G4** **uma única parametrização por fonte** (se o melhor `(κ, m,
k)` variar por curva dentro da fonte, é fit).

## 6. Ramos — agora com o quinto

- **PASSA** — A ok, B ≥ 0,50, C ok, G1–G4 ok ⇒ propor adoção gateada.
- **PARCIAL** — B entre 0,25 e 0,50 ⇒ componente misto (migração + reescala), com as
  duas frações declaradas; adoção exige decisão explícita.
- **NÍVEL DISFARÇADO** — B < 0,25 ⇒ o ganho é reescala de canal. **Não adotar como
  forma**; se for adotado algum dia, que seja com o nome certo (alavanca de nível) e
  procedência de constante.
- **FALSIFICADO** — Teste A viola, ou C dá ordenação invertida com spread válido.
- **INCONCLUSIVO** — spread insuficiente em C, ou os dois sítios sem trajetória.
  **Não conta como falsificação** para o requisito (b) da regra de parada.

## 7. Efeito na regra de parada, declarado antes

- **PASSA / PARCIAL** ⇒ a classe "taxa dependente do estado acumulado" está **VIVA**;
  a parada não se aplica e o pipeline tem alvo com mecanismo.
- **NÍVEL DISFARÇADO / FALSIFICADO** ⇒ o membro está medido de verdade e conta para o
  requisito (b); junto com o kernel desacelerante (reprovado no G2: 8 pioram, uma de
  0,0396→0,2232), a classe fica com 4 de 4 membros medidos e a parada pode disparar.
- **INCONCLUSIVO** ⇒ nada conta; projetar o instrumento de novo.

## 8. Reprodutibilidade

```bash
py -3.12 New_Theory/cm_discriminante_d2linha.py [--quick]
```
