# PREREG — a partição axial JÁ EXISTE no engine e não alimenta os canais de perda

## Estado

**PENDENTE — gates congelados, nada implementado.** Escrito em 2026-08-21 (15:3x) contra o
store **`3c9afd6579a1`** (uniforme, 210), censo `_censo()` tripé **168/205**.

Assinatura do professor (*"assinado, e prossiga"*) cobre a forma nomeada no mapa de
`9c19779`. Este prereg existe porque **forma nova de engine exige gates ANTES**, e porque a
medição mudou o que a forma é.

---

## 1. O achado que reformula a tarefa

A exceção da `eccles2010_fig6_annotated_4kN_axial` diz *"o engine não tem contorno axial
externo"*. Medindo o fonte, **a partição existe e está correta**:

```python
# dynamic_stiffness_analyzer.py, U_loaded(...)
F_bolt  = state.F_0 + Phi * F_ax_ext
F_joint = state.F_0 - (1 - Phi) * F_ax_ext          # partição LINEAR (VDI 2230)
#   ou, com phi_load_dep > 0, a forma ELÍPTICA de Grosse (1990) no lado do membro
```

⚠️ **Mas ela vive só em `U_loaded`** — uma função de **ENERGIA**. O comentário do campo
`phi_load_dep` diz textualmente:

> *"Só afeta `U_loaded` (**o ÚNICO local do engine onde Φ particiona um `F_ax_ext` explícito
> entre parafuso/junta**; `RotationalLooseningLoss` usa `Phi_ax`/`Phi_tr` como GANHOS do
> torque de afrouxamento — forma diferente, não tocada por este campo)."*

⇒ os **canais de perda** (embedding, creep, wear, rotacional) são dirigidos por `state.F_0`
**cru**. A forma que falta **não é um mecanismo novo**: é ligar ao caminho de perda uma
partição **já implementada e já testada** para a energia.

## 2. Por que o sinal fecha com o defeito medido

Diagnóstico da `fig6` (ataque de 2026-08-21, `113cbb0`):

| | |
|---|---|
| erro nasce em | **u = 0,00** (maior salto entre os ciclos 0 e 62, Δ = −0,2839) |
| resíduo 1º terço | **−0,2930** ⇒ o modelo está **abaixo** do dado: perde DEMAIS cedo |
| canal do início | **embedding** (ABS total 0,268; único com relógio de dezenas de ciclos) |
| teto de autoridade | suprimir embedding leva res.máx 4,74× → **3,24×** ⇒ alvo **fora do alcançável** por constante |

Com 4 kN axiais externos, `F_joint = F_0 − (1−Φ)·F_ax < F_0`. Embedding é dirigido por
**pressão de contato do lado do MEMBRO** ⇒ com `F_joint` a pressão cai, o embedding cai, e a
perda cedo cai. **A direção é a do defeito**, e isso é predição, não ajuste.

## 3. Desenho — mínimo, default-inerte, com isolamento ESTRUTURAL

Campo novo em `JointMaterial`:

```
ax_partition_on: float = 0.0    # 0 = OFF EXATO (canais seguem em state.F_0)
```

Quando `> 0`, os canais de perda passam a ser dirigidos pela força **particionada** do lado
que fisicamente os governa — `F_joint` para o que depende de pressão de contato de membro
(embedding), `F_bolt` para o que depende de tensão no parafuso — reusando a **mesma**
expressão de `U_loaded` (nenhuma fórmula nova; um helper extraído dela).

⚠️ **Isolamento estrutural, e é forte:** em fonte **transversal** `F_ax_ext ≈ 0` ⇒ a
partição é a **identidade** (`F_joint = F_bolt = F_0`) ⇒ **inerte por construção**, não por
default. É a mesma propriedade que deu isolamento ao `emb_pressure_exp` (o `min(1,·)`
deixando 5 de 7 curvas do LU em S = 1 exato).

## 4. Gates CONGELADOS

| # | gate | critério |
|---|---|---|
| **G1** | OFF é bit-idêntico | com `ax_partition_on = 0`, **Δ = 0,0000 nas 210** curvas |
| **G2** | isolamento estrutural | com o campo LIGADO, as curvas de fonte **transversal** (F_ax ≈ 0) seguem **bit-idênticas** — a identidade tem de ser exata, não aproximada |
| **G3** | predição de SINAL, registrada aqui | na `fig6`, ligar o campo tem de **reduzir** o res.máx (o modelo perde menos cedo). Se **aumentar**, a forma está errada e o item morre — não se ajusta o expoente para salvar a direção |
| **G4** | teto respeitado | o alvo é ficar **abaixo de 3,24×** (o teto medido com embedding suprimido). Chegar a 3,24× não é sucesso: é empatar com desligar o canal |
| **G5** | controle de fonte | as **outras 9** curvas do `ECCLES_2010` não podem piorar >+0,01 no MAE; as 4 que estão no tripé não podem sair |
| **G6** | conservação | o residual de energia não degrada: a partição já é a de `U_loaded`, então usar a MESMA expressão nos canais tem de manter `W_ext + ΔU = Σ W_diss` |
| **G7** | teste próprio | `tests/test_particao_axial.py` com OFF-exato, identidade transversal e a direção do G3 |
| **G8** | suíte | completa, comparada ao baseline |

**Ramos:** `ADOTA` (gates 8/8) · `CAPACIDADE FICA, NÃO ADOTA` (a forma funciona mas o G4 ou
o G5 reprovam ⇒ default-inerte no main, como `emb_pressure_exp`) · **`FALSIFICADA`** (o G3
inverte) · `INCONCLUSIVO`.

## 5. O que este item NÃO faz

- **Não** inventa mecanismo: usa a partição já existente e testada de `U_loaded`.
- **Não** toca `RotationalLooseningLoss`, que usa `Phi_ax`/`Phi_tr` como **ganhos de
  torque** — forma diferente, e mexer nela seria outro item.
- **Não** promete fechar a `fig6`: o teto medido diz que 3,24× é o melhor que **constantes**
  alcançam, e esta forma existe para ir **abaixo** disso. Se não for, o G4 a barra.
- **Não** altera o estatuto da exceção assinada — se a curva fechar por mérito, a retirada
  segue o precedente **K6** (prova preservada).

---

## 6. ⛔ ITEM MORTO ANTES DA IMPLEMENTAÇÃO — a lacuna é de INPUT, não de forma

**Medido em 2026-08-21 (15:3x), antes de escrever uma linha de engine.** A checagem que
precede qualquer forma nova é *"o canal tem driver?"*. Não tem.

`to_solver_config()` das **10** curvas do `ECCLES_2010`:

| curva | axial no NOME | campos de carga no config |
|---|---|---|
| `fig3_typical_no_axial` | — | `initial_preload 15000` · `transverse_force 195000` |
| **`fig6_annotated_4kN_axial`** | **4 kN** | `initial_preload 15000` · `transverse_force 195000` |
| `fig7a_no_axial` | — | idem |
| **`fig7b_axial_1p1kN`** | **1,1 kN** | idem |
| **`fig7c_axial_2p7kN`** | **2,7 kN** | idem |
| **`fig7d_axial_3p1kN`** | **3,1 kN** | idem |
| `fig8a_no_axial_baseline1` | — | idem |
| **`fig8b_axial_0p7kN`** | **0,7 kN** | idem |
| `fig8c_no_axial_baseline2` | — | idem |
| **`fig8d_axial_3p5kN`** | **3,5 kN** | idem |

⇒ **os 10 configs são IDÊNTICOS.** A carga axial externa — **a variável que o paper varre** —
**não entra no modelo**. As 6 curvas axiais são simuladas como se fossem as baselines.

### Por que isso mata este prereg

A forma proposta parte de `F_ax_ext` para calcular `F_joint = F_0 − (1−Φ)·F_ax_ext`. Com
`F_ax_ext = 0` a partição é a **identidade** ⇒ a forma nasceria **inerte na própria curva que
ela visa**. É o modo de falha que este repositório documenta em três lugares — *canal sem
driver* — e que eu teria pago com uma implementação inteira.

⚠️ **A premissa da §1 continua VERDADEIRA e deixa de ser o gargalo:** a partição de fato só
vive em `U_loaded` e de fato não alimenta os canais de perda. Só que isso não importa
enquanto não houver carga axial para particionar. **Descobrir que a resposta certa é para
outra pergunta é resultado, não fracasso** — e custou uma leitura, não um dia.

**Ramo: `INCONCLUSIVO`** — com a ressalva de que o rótulo subestima: não é que o teste não
tenha decidido, é que a **premissa apontava para o lugar errado**.

### O que isto explica de uma vez (e reenquadra o estatuto de 6 curvas)

1. **Por que as 6 axiais falham:** o modelo não as distingue das baselines, então produz
   trajetória ~igual para condições que o paper mostra diferentes.
2. **Por que existe o texto *"sobreposição axial"*** nas provas de exceção: alguém observou
   a sobreposição e a atribuiu a forma faltante. A sobreposição é **literal** — os inputs são
   os mesmos.
3. **Por que o `_SEM_FAMILIA_MECANICA` bloqueia a família por *"cegueira à carga axial"*:**
   a chave de pareamento era cega, e agora se sabe que **o modelo também é**.
4. **Por que o `excecoes_f5_teste_premissa` via `eccles2010_fig7` como ensemble de 4
   réplicas:** aos olhos do modelo elas **são** réplicas — configs idênticos.

### O item que fica na mesa, e é de DADO

**Levar a carga axial por curva para o registry**, com procedência do paper (os valores estão
nos próprios nomes, o que sugere que já foram lidos uma vez e se perderam no caminho do
`to_solver_config`). Classe: **correção de input** — a mesma que rendeu a maior parte dos
fechamentos da campanha (23 por leitura).

⚠️ **Só depois disso a forma da §3 volta a ser testável**, e então com driver real. A ordem
importa: com input errado, qualquer forma que "funcionasse" estaria compensando o input.

⚠️ **Não executo:** correção de input em 6 curvas muda trajetória e exige re-carimbo +
gates + assinatura. E há uma pergunta anterior à minha competência aqui: **como o rig aplica
o axial** (constante × intermitente, os nomes distinguem os dois) determina se ele entra como
`F_amp·cos(θ)` ou como um termo estático — e isso se lê na nota de aparato, não se supõe.
