# Prereg — relógio por reaperto: TRÊS números, todos COMPARTILHADOS

**2026-08-05** · decisão D-L (por delegação, MANDATO PERMANENTE) · gates
escritos **antes** de medir. Fingerprint de partida: `98fd6c462968`.

## O que as duas tentativas anteriores estabeleceram (e não repetir)

| | escopo testado | veredicto |
|---|---|---|
| **D-J** | `(1+g)^n` no slip **+ renew** | FALSIFICADO — amplificador puro tem contradomínio [1,∞) e o fator necessário é **< 1** em todo estágio reapertado |
| **D-K** | `base·(1+g)^(n-1)` no slip, **sem renew** (3 nº) | FALSIFICADO por **teto de autoridade**: slip suprimido por inteiro dá 0,460 no t1, e o alvo é **0,203** — 2,3× curto |

**Falha de método minha, registrada:** eu não fiz a sonda de **teto de
autoridade** antes de escrever os preregs. Suprimir o canal e perguntar *"o
alvo está dentro do alcançável?"* custa 1 simulação e teria poupado os dois —
cada um testou **metade** da composição porque eu fatiei errado o escopo.

**Teto conjunto, medido agora** (slip suprimido **e** `renew=0`): fatores
**0,040 / 0,023 / 0,016** contra os necessários 0,203 / 0,355 / 0,719 ⇒ o alvo
está dentro do alcançável com folga, e **nenhum canal sozinho chega ao t1**
(slip só: 0,460; renew só: 0,586).

## A forma, e a parcimônia que o dano já adotado entrega

```
fator_slip(0)    = 1                                  (virgem intocado)
fator_slip(n≥1)  = retight_loss_base · (1+retight_loss_gain)^(n-1)
embedding        : delta_emb ·= (1 − k_emb_renew · D)   [já existe]
```

**`k_emb_renew` multiplica `D`, que já é por-lubrificação no canônico**
(`c_D` = 0,5 seco / 0,03 óleo). Logo **um único** `k_emb_renew` compartilhado
produz renovação muito diferente entre as cadeias **sem número novo**.

⇒ Escopo: **3 números, TODOS COMPARTILHADOS** por seco e óleo
(`retight_loss_base`, `retight_loss_gain`, `k_emb_renew`), para **9 curvas**.
Toda a diferenciação por lubrificação vem de `c_D`/`mu`, já adotados.

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (inércia exata):** `base=1,0 ∧ gain=0` ⇒ 21 curvas bit-idênticas;
  `n=0` ⇒ fator 1,0 para quaisquer valores.
- **G1 (MECANISMO — o gate que decide):** os **três** valores são
  **compartilhados**. As **duas** cadeias têm de melhorar (soma de MAE cai em
  cada uma). **Valor por grupo é PROIBIDO** — a claim é que o que difere entre
  seco e óleo já está no `D`. Se precisar soltar por grupo, o ramo é
  **FALSIFICADO**, e eu prefiro isso a 5 números.
- **G2 (virgem intocado):** `fig8_t0`, `fig7a_t0` e as 4 do `fig5`
  **bit-idênticas**.
- **G3 (protocolo que SOLTA):** as 8 do `fig6a`/`fig6b` **bit-idênticas**
  (não recebem os números).
- **G4 (nenhum caso pior):** nenhuma das 9 piora > **+0,010** em qualquer
  perna; as 4 do `fig7a` e a `fig8_t3`, hoje no tripé, **permanecem**.
- **G5 (ganho):** ≥ **2** das 3 de fila entram. Uma só ⇒ parcial declarada.
- **G6 (procedência + desempate):** 3 números fitados no conjunto das 2
  cadeias, declarado como fit. Entre células que passam todos os gates, vale o
  **desempate padrão do mandato**: menos parâmetros efetivos > nenhuma
  constante coincidindo com artefato do ensaio > melhor na perna que manda.
- **G7 (higiene do campo novo):** `VarSpec` no explorador para os 2 campos
  novos, teto de DOF revisto com motivo, teste de invariante dedicado, e
  `_sem_dof_fitado` se não adotado.
- **G8 (sincronia):** adoção ⇒ re-stamp uniforme dos 210 + censo/docs/páginas
  no MESMO commit.

### Ramos

- **ADOTA** — G0..G5.
- **FALSIFICADO (precisa de valor por grupo)** — G1 falha; registrar os ótimos
  separados para mostrar a distância.
- **FALSIFICADO (controle paga)** — a `fig8_t3` ou o `fig7a` saem do tripé em
  toda célula que fecha a fila. ⇒ **a classe FECHA**: o membro foi testado com
  discriminante válido, teto de autoridade confirmado, composição correta, e
  ainda assim o preço é uma curva por outra.
- **INCONCLUSIVO** — campo inerte por companheiro.

## Previsão registrada

Espero `base ≈ 0,2–0,3`, `gain ≈ 0,8` (g≈1,8), `k_emb_renew ≈ 0,0–0,15`; **t1
e t2 fechando**, a **t4 não** (fratura). Espero a **`fig8_t3` como o ponto de
tensão** — ela é n=3, onde o fator é maior, e foi ela que o D-J destruiu
(+0,127).

⚠️ E espero **algum** custo no `fig7a`: as três curvas dele em n≥1 estão hoje
no tripé com MAE 0,0069–0,0130, folga grande em MAE mas o `t3` dele precisa
**perder MAIS** (fator 1,464 > 1) — o único ponto de todo o conjunto onde o
modelo precisa acelerar. Se o `g` compartilhado não der conta dele sem
estourar o `fig8_t3`, é aí que a classe fecha.
