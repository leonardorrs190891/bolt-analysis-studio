# PREREG — `s1_amp_gate` no `LIU_2025`: fechar a **inclinação de amplitude**, não uma curva

**Data:** 2026-08-15 · **Autorização:** assinatura em bloco do professor
(*"continue o loop, eu assino tudo"*) · **Store de partida:** `85e8104420b0`, censo
**141/205**, fila form-limited **0**.

⚠️ **Gates IMUTÁVEIS depois de escritos.** Nada abaixo pode ser alterado após a primeira
medição da grade.

---

## 1. O defeito, já medido (não é hipótese)

`liu2025_inclinacao_amplitude_resultado.md`, commit `34c92e2`:

- **`ρ(amplitude, viés) = +1,000` exato nas 6 amplitudes**, R² 0,978, p 0,0002.
- Viés de **−0,0757** (0,25 mm) a **+0,0278** (0,8 mm); zero em **≈0,66 mm**.
- Cada curva, isolada, tem `|viés|/MAE = 1,00` — parece **nível**; a família mostra
  **inclinação**.
- Constante plana (`C_creep`) **refutada pelo controle**: fecha 2, **tira a `amp0p6`**,
  explode a `amp0p8` (+0,0844) ⇒ G2 reprova.

## 2. A forma proposta — já existe no engine, default-inerte

`stage1_amp_gate` (PR-3, 2026-08-01), `dynamic_stiffness_analyzer.py:1721`:

```
g = floor + (1 − floor) · δ^p / (δ^p + dref^p)
```

`dref ≤ 0` (default) **ou** modo força ⇒ `g = 1,0` **exato**. Multiplica **só** o `d_delta`
de Embedding e Creep — `dF_0`/`dE` derivam dele nos dois, então a **conservação de energia
fica intacta por construção**. Nenhuma linha de engine muda: a adoção é de **config**.

## 3. ⚠️ PROCEDÊNCIA — declarada como AUSENTE, antes de medir

A hipótese de âncora física foi **levantada e FALSIFICADA na mesma sessão**, e fica
registrada porque a alternativa seria descartá-la em silêncio:

> *"Embedding exige re-engajamento de asperezas, que exige escorregamento; em stick
> permanente as asperezas não se reengajam ⇒ `dref` = amplitude de transição stick→slip."*

**Medido** (instrumentando `resolve_transverse_slip` nas 6):

| amp [mm] | 0,25 | 0,30 | 0,40 | 0,50 | 0,60 | 0,80 |
|---|---|---|---|---|---|---|
| classe | STICK | STICK | PARCIAL | PARCIAL | PARCIAL | PARCIAL |
| `slip/δ` | 0,000 | 0,000 | 0,225 | 0,380 | 0,484 | 0,613 |

⇒ transição stick→slip entre **0,30 e 0,40 mm**; zero do viés em **0,66 mm**. **Não
coincidem** — a âncora está **falsificada**.

**Consequência assumida:** `dref` (e `floor`, se usado) entram como **constantes fitadas sem
âncora**, per-fonte. Isso é o mesmo estatuto da magnitude do canal de flanco adotada em
2026-08-14 (canal com procedência de artigo, magnitude sem âncora) — legítimo **desde que
declarado**, e está declarado aqui.

## 4. PARCIMÔNIA — quantos números, e por quê

`p` **FIXO no default 8,0** não serve (gate quase-degrau: `g(0,25)=0,06` mataria a curva).
São, portanto, **no máximo 3** números para 6 curvas — menos parcimonioso que o padrão da
campanha (3 números para o dataset inteiro no bloco `shared`).

**Regra de parcimônia, declarada antes:** adota-se a célula com **menos números diferentes do
default**. Se uma célula com `floor = 0` (2 números: `dref`, `p`) passar todos os gates,
ela **vence** qualquer célula de 3 números, ainda que esta tenha MAE melhor.

## 5. Grade

- `dref` ∈ {0,30 · 0,35 · 0,40 · 0,45 · 0,50} [mm → m no config]
- `p` ∈ {1,5 · 2 · 3}
- `floor` ∈ {0 · 0,2 · 0,35 · 0,5}

⚠️ **Disciplina de fronteira (D-L):** se a célula vencedora cair na **borda** de qualquer
eixo, a grade **tem de ser estendida** naquele eixo antes de adotar.

## 6. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | **isolamento** | Δ = **0,0000 exato** em todas as curvas **fora** do `LIU_2025` (o gate é per-fonte; qualquer vazamento reprova) |
| **G2** | **nenhuma piora** | nenhuma curva do `LIU_2025` piora mais que **+0,010** de MAE |
| **G3** | **nenhuma saída** | nenhuma curva que hoje passa o tripé pode sair — `amp0p4`, `amp0p5`, `amp0p6` |
| **G4** | **ganho líquido** | ≥ **2** curvas fecham o tripé por mérito |
| **G5** | **a inclinação tem de cair** | `\|ρ(amp, viés)\|` **e** `\|slope\|` da regressão têm de **diminuir** — fechar curva sem achatar a inclinação é fitar, não consertar |
| **G6** | **inércia declarada** | a célula adotada **não** pode dar resultado idêntico ao dígito ao nominal em nenhuma curva que ela deveria mover (empate perfeito = parâmetro morto, `CLAUDE.md`) |
| **G7** | **conservação** | resíduo de conservação de energia não degrada além do nominal em nenhuma curva |
| **G8** | **fingerprint** | store re-carimbado **uniforme** nas 205+ curvas após a adoção |

## 7. Predições registradas ANTES da medição

1. **`amp0p8` NÃO fecha.** O gate satura em 1 e ela precisa de **mais** perda (viés
   **+0,0278**). Se ela fechar, o teste está inválido — procure erro de campo.
2. **`amp0p25` e `amp0p3` são as que podem fechar** (as duas STICK, viés mais negativo).
3. **`fig2_single` mal se move**: `slip/δ` = 0,612, o mesmo regime da `amp0p8`, logo
   `g ≈ 1`.
4. O `floor` vencedor será **> 0**: sem ele, `g(0,25)` cai demais e a `amp0p25`
   **sobre-corrige** (viés vira positivo).

## 8. Ramos possíveis do veredito

- **ADOTA** — alguma célula passa G1–G8 e a regra de parcimônia escolhe entre as que passam.
- **FALSIFICADO** — nenhuma célula passa G2/G3/G4 ⇒ o gate de amplitude **não** é a forma
  certa para esta inclinação; registrar e devolver o item à mesa.
- **INCONCLUSIVO** — o teste não testou (grade inteira inerte, campo errado, `dref` em unidade
  trocada). ⚠️ Este ramo **existe de propósito**: sem ele o script é forçado a escolher entre
  PASSA e FALSIFICADO e escreve veredito sobre teste vazio (aconteceu 2× em 2026-07-30).

## 9. ⚠️ Ressalva de escopo que NÃO se resolve aqui

A adoção do `s1_amp_gate` ficou **INCONCLUSIVA em 2026-08-01** porque a Fig. 4 do próprio Liu
discorda das curvas digitalizadas no **N₉₅** em 3–5×. Aquele veredito é sobre o **relógio**
(quando o joelho chega); **este** prereg é sobre o **nível** e **não usa a Fig. 4**.

⇒ se esta adoção passar, o `LIU_2025` passa a ter o `s1_amp_gate` ligado **servindo ao
nível**, e qualquer trabalho futuro sobre o relógio nesta fonte herda a constante. Isso fica
escrito na procedência, não resolvido.

## 10. Unidade — armadilha específica

`s1_amp_gate_dref` está em **metros** (`# amplitude de transicao [m]`), e as amplitudes do
`LIU_2025` estão em **mm** no nome da curva. `dref = 0,35 mm` ⇒ **`3,5e-4`**. Escrever `0,35`
seria um gate que nunca dispara (`g ≈ 0` em toda a fonte) — e apareceria como **catástrofe
uniforme**, que por regra da campanha se lê como **teste inválido**, não falsificação.
