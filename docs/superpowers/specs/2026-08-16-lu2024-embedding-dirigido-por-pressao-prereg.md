# PREREG — encaixe DIRIGIDO POR PRESSÃO no `LU_2024` (ramo oposto da pré-conformação)

**2026-08-16 (madrugada)** · **gates congelados neste commit** · store
`20be19aabe11` · alvo `lu2024_M8_fig20_T10Nm`, a **única** curva form-limited
do projeto. Diagnóstico:
`New_Theory/lu2024_T10Nm_embedding_sem_pressao_resultado.md`.

## Estado — **EXECUTADO · FALSIFICADO (ramo G8)**, capacidade fica default-inerte

> Registrado em 2026-08-16 (04:5x) pela **sessão A**, a partir dos commits e da medição
> da sessão B — a seção faltava e o `test_prereg_declara_estado` a exigia.

| gate | resultado |
|---|---|
| **G0** inércia | ✅ **PASSA** — `emb_pressure_exp = 0` reproduz o store bit-a-bit: pior `|Δ|` = **0,000e+00** nas **210** curvas (`d70a38f`) |
| **G1** alvo | ⛔ **FALHA** — *"a lei conserta o defeito que nomeou e **NÃO fecha a curva**"* (`945f363`) |
| **G7** guardas de campo novo | `VarSpec` ✅ feito; **tripwire de contagem de campos** fechado pela sessão A neste commit |
| **G8** falsificação honesta | ✅ **acionado** — é o ramo que vale: a curva volta à fila com **uma rota a menos** |

⇒ **capacidade construída, adoção NÃO tomada.** `emb_pressure_exp` fica **default-inerte**
no engine, no mesmo estatuto de `emb_clock_delta_ref`, `s1_amp_gate_floor` e
`loose_arrest_residual`. A `fig20_T10Nm` **segue** na fila `form_limited` (a única).

⚠️ **A não-adoção é o resultado, não a ausência dele**: a lei foi construída, medida, e
reprovou no gate que ela mesma declarou antes. Isso é uma rota fechada com número — o que
o G8 existe para produzir.

## 1. O defeito, e por que a rota é FORMA e não constante

O modelo perde pré-carga **demais** na `T10Nm` (viés −0,2514 = −MAE ⇒ resíduo
de sinal único), o erro **se forma no 1º ciclo** (salto −0,2650) e o canal é
**embedding** (62 % da perda da fonte). A fonte varre F₀ em **7×** e o excesso
de perda no 1º ciclo vai com **1/F₀ a r = +0,995**; no extremo superior o sinal
**inverte** (`T28Nm` perde de menos). Controle negativo: no `CACCESE_2009`
(embedding 0,2 % da perda) o sinal some.

**Falsificado antes deste prereg** (não é rota): 4 alavancas livres varridas;
grade `emb_depth` × `N_emb` 0 de 25; e o **split** `emb_depth` ×
`emb_load_frac` em 16 células — subir o termo proporcional **piora** a alvo, e
o `emb_depth` que ela pede é **2,7× menor** do que a `fig18_amp0p25`
(protegida) tolera.

## 2. A forma proposta, e por que ela não existe hoje

O engine tem a lei de pressão do encaixe **com o sinal oposto**:

```python
S = min(1, (p_ref_emb / p_init) ** emb_conform_exp)   # pré-conformação
```

cuja física declarada é *"torque maior pré-conforma mais asperezas ⇒ menos
resíduo cíclico"* — e cuja consequência, escrita na própria docstring, é
*"fracional cai mais rápido que 1/F₀"*, isto é, **agravar** o defeito medido.
O outro ramo, igualmente clássico, é o **achatamento plástico dirigido por
pressão**: abaixo de uma pressão de referência o escoamento plástico das
asperezas é menor, logo o reservatório de encaixe é **mais raso**. Ele é
inalcançável hoje porque `_conformance_S` faz `if exp <= 0: return 1.0`.

**Campo novo, default-inerte** (idioma padrão do engine):

```python
emb_pressure_exp: float = 0.0     # n [-]; 0 => 1.0 EXATO (inerte)
# S_p = min(1, (p_init / p_ref_emb) ** n)     — compõe (multiplica) com o
# fator de pré-conformação, que trata física distinta e fica intocado.
```

**Parcimônia: UM número fitado.** `p_ref_emb` fica no **default do engine
(1,5e8 Pa)**, sem declaração nova no grupo do `LU_2024`.

## 3. Por que o isolamento é ESTRUTURAL (e não sorte)

Pressões medidas (`p = F₀/A_contact`, `geometry_for_case`):

| curva | p (MPa) | p/p_ref | efeito de `S_p` | papel |
|---|---:|---:|---|---|
| `fig20_T4Nm` | 40,3 | 0,27 | reduz | declarada (escopo) |
| **`fig20_T10Nm`** | **114,1** | **0,76** | **reduz** | **ALVO** |
| `fig20_T16Nm` | 160,7 | 1,07 | **S = 1 exato** | declarada (órfã) |
| `fig20_T22Nm` | 221,3 | 1,48 | **S = 1 exato** | tripé |
| `fig20_T28Nm` | 287,5 | 1,92 | **S = 1 exato** | declarada (órfã) |
| `fig18_amp0p25` | 229,6 | 1,53 | **S = 1 exato** | **tripé (protegida)** |
| `fig18_amp2p0` | 221,9 | 1,48 | **S = 1 exato** | **tripé (protegida)** |

O `min(1, ·)` põe **todas** as curvas com p ≥ p_ref em S = 1 **exatamente** ⇒
as três que não podem piorar são bit-idênticas **por construção**. Só duas
curvas da fonte estão abaixo da referência, e uma delas é a alvo.

⚠️ **Isto é um risco tanto quanto uma vantagem, e fica declarado:** com o
`p_ref` no default, a lei **não tem como** consertar a `T28Nm` (que perde de
menos) nem melhorar as demais. Se a única curva que se move é a alvo, o
resultado **não é evidência de generalidade** — é ajuste local com procedência
física. A generalidade tem de vir do G6.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G0** | **inércia** | `emb_pressure_exp=0` reproduz o store **bit-a-bit** (Δ = 0,0000) nas 210 curvas |
| **G1** | **alvo** | `fig20_T10Nm` fecha o tripé: MAE ≤ 0,05 **E** res.máx ≤ 0,10 **E** σ_res ≤ `limite_sres(LU_2024)` |
| **G2** | **controle da fonte** (precedente D-AB) | nenhuma das 12 irmãs piora > **+0,01** de MAE; as 3 no tripé (`fig18_amp0p25`, `fig18_amp2p0`, `fig20_T22Nm`) **seguem** no tripé |
| **G3** | **isolamento** | Δ = **0,0000 exato** em toda curva fora do `LU_2024` |
| **G4** | **procedência** | `p_ref_emb` fica no default 1,5e8; **nenhum** número novo além do expoente. Se a grade exigir mover `p_ref`, o passo **não é este** — vira prereg próprio |
| **G5** | **regra de escolha declarada ANTES** | havendo >1 célula aprovada, vence a **mais CENTRAL** (mais vizinhas que também fecham; desempate pela **pior perna**) — precedente D-I/D-AA. **NUNCA por MAE** |
| **G6** | **fronteira de grade** | se o ótimo cair na borda, **estender** a grade antes de adotar (disciplina D-L) |
| **G7** | **guardas de campo novo** | `VarSpec` em `New_Theory/_ve_content.py` (senão `test_variable_explorer::test_all_fields_covered` falha) + testes de contrato do campo, no padrão de `test_loose_arrest_residual.py` |
| **G8** | **falsificação honesta** | se nenhuma célula fechar G1 sem violar G2, declarar **FALSIFICADO** com número; a curva volta à fila com uma rota **a menos** |

Grade inicial: `emb_pressure_exp` ∈ {0,5 · 1,0 · 1,5 · 2,0 · 3,0}. Alvo
aritmético: a alvo precisa de ~36 % menos encaixe, e `0,76^n = 0,64` dá
**n ≈ 1,6** — o meio da grade, de propósito.

## 5. Predição registrada

1. **MAE e res.máx da alvo melhoram forte** em n ≈ 1,5–2,0 (o resíduo é de
   sinal único e a alavanca é de nível — casam).
2. ⚠️ **O σ_res é a perna de risco.** Ele mede *dispersão*, não nível, e é
   invariante a deslocamento constante. Ele só cai porque o 1º ponto está
   ancorado em resíduo 0 por construção — logo **é ele que decide**, e é
   plausível que a curva feche MAE e res.máx e **reprove no σ**. Se isso
   ocorrer, o resultado é *"a rota está certa e é insuficiente"*, não sucesso.
3. **A `T4Nm` melhora muito** (p/p_ref = 0,27 ⇒ corte grande) — mas ela é
   **declarada por escopo** e **não conta** para nada aqui; se eu a citar como
   ganho, é auto-engano.
4. **`T16Nm`, `T22Nm`, `T28Nm` e as duas `fig18` não se movem NADA** (Δ exato).
   Qualquer movimento nelas é **bug**, não resultado — e reprova o G0/G3.
