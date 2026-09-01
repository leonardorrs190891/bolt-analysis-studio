# O item N está **refutado pelo próprio controle** — o defeito do `LIU_2025` é uma **inclinação em amplitude**, não um nível por curva

**2026-08-15** · só-leitura · **nada adotado** · store `85e8104420b0`, censo **141/205**
(intacto), fila form-limited **0**.

---

## 1. O que o item N afirmava

Da auditoria de `classe_parada` (2026-08-14): a `liu2025_M16_amp0p3` está na camada **sem a
assinatura da classe**, e **fecha o tripé** com `C_creep`×0,5 ou `emb_depth`×0,5 ⇒
fila 0→2, censo 141→**142**.

**A premissa é verdadeira.** O `ataque_curva.py` confirma: `C_creep = 6,5e-12` leva a curva
de `0,0645/0,0865/0,0249` para **`0,0360/0,0511/0,0183`** — fecha nas três pernas.

**E a proposta ainda assim é refutada** — pelo controle da fonte, que é gate padrão.

## 2. O diagnóstico por curva **esconde** o defeito

Cada curva do `LIU_2025`, isolada, tem `|viés|/MAE = 1,00` — resíduo de **sinal único**, o
diagnóstico canônico de *"erro puro de NÍVEL, alavanca de nível ainda tem o que dar"*. Na
alvo, `ρ(resíduo, N) = −0,23` ⇒ **OFFSET**, não rampa. Tudo aponta para uma constante.

⚠️ **Olhando a fonte inteira, o quadro inverte:**

| amplitude [mm] | 0,25 | 0,30 | 0,40 | 0,50 | 0,60 | 0,80 |
|---|---:|---:|---:|---:|---:|---:|
| **viés** | −0,0757 | −0,0645 | −0,0462 | −0,0292 | −0,0234 | **+0,0278** |
| no tripé? | não | não | **sim** | **sim** | **sim** | não |

**`ρ(amplitude, viés) = +1,000` — exato, nas 6.** Regressão: `+0,178 /mm`, **R² 0,978**,
p = 0,0002. O modelo perde **demais** em amplitude baixa e **de menos** em amplitude alta,
cruzando zero em **≈0,66 mm**.

⇒ o que cada curva exibe como *nível* é, na fonte, **uma inclinação**. O `|viés|/MAE = 1,00`
por curva não distingue as duas — é preciso olhar a **família**.

## 3. O controle: a constante plana quebra o que já passava

`C_creep = 6,5e-12` (a dose que fecha a alvo) aplicada a **toda** a fonte:

| curva | nominal (MAE/mx/σ) | com a dose | ΔMAE | efeito |
|---|---|---|---:|---|
| `amp0p25` | 0,0757/0,0945/0,0267 | 0,0458/0,0553/0,0160 | **−0,0299** | ✅ **fecha** |
| `amp0p3` (alvo) | 0,0645/0,0865/0,0249 | 0,0360/0,0511/0,0183 | **−0,0284** | ✅ **fecha** |
| `amp0p4` | 0,0462/0,0623/0,0202 | 0,0224/0,0439/0,0149 | −0,0238 | melhora |
| `amp0p5` | 0,0292/0,0516/0,0183 | 0,0152/0,0369/0,0170 | −0,0140 | melhora |
| `amp0p6` | 0,0234/0,0695/0,0213 | 0,0272/**0,1238**/**0,0447** | +0,0038 | ⛔ **SAI do tripé** |
| `amp0p8` | 0,0381/0,0853/0,0396 | **0,1225/0,3271/0,1568** | **+0,0844** | ⛔ MAE ×3,2 |
| `fig2_single` | 0,0276/0,0571/0,0268 | 0,0381/0,0836/0,0356 | +0,0105 | piora |

**Saldo de censo: +2 −1 = +1.** ⛔ **Mas o gate G2 vigente** (*nenhuma curva piora mais que
+0,01 de MAE*) **reprova**: `amp0p8` +0,0844 e `fig2_single` +0,0105.

A dose mais branda (`9,75e-12`) é **estritamente pior**: **0 fecham**, `amp0p6` sai igual.

## 4. ⚠️ A tabela de doses **é a inclinação, medida de novo**

O ganho decresce monotonicamente com a amplitude e **vira dano** exatamente onde o viés cruza
zero:

```
Δ MAE:  −0,0299  −0,0284  −0,0238  −0,0140  +0,0038  +0,0844
amp:      0,25     0,30     0,40     0,50     0,60     0,80
```

⇒ **dois instrumentos independentes** — regressão viés×amplitude e resposta-a-dose por
amplitude — dão o mesmo resultado. É isso que separa achado estrutural de coincidência de fit,
e é por isso que o veredito não é *"a dose custa caro"*, e sim **"a alavanca é da classe
errada"**: constante plana move a família em bloco, e o defeito é uma **inclinação**.

## 5. Precedentes que isto repete

| lição | como reaparece aqui |
|---|---|
| **D-AB** — o controle inverteu a escolha | a alavanca de melhor ajuste na alvo é a que explode a `amp0p8` |
| **D-I** — o alvo legítimo é o **centro** da família, não um membro | fechar a `amp0p3` sozinha é fitar um membro de família monótona |
| **D-Z/D-AA** — varredura marginal acha ótimo **condicional** | `C_creep` "no ótimo" por curva ≠ ótimo da fonte |
| **§4.7** — `C_creep` é por **par tribológico** | por isso a constante é *elegível*; a refutação é de **classe**, não de procedência |

## 6. Veredito e reorientação

⛔ **Item N — RECUSADO como proposto.** A curva fecha; a fonte paga. Nenhuma constante plana
pode fechar uma família cujo viés é monótono em amplitude, porque a correção necessária varia
de **−49 %** da perda (0,25 mm) a **+4 %** (0,8 mm).

✅ **O candidato legítimo já existe no engine, default-inerte:** `s1_amp_gate_*`
(PR-3, 2026-08-01) — gate Hill de **regime de amplitude** que multiplica o `d_delta` de
Embedding **e** Creep, `g = floor + (1−floor)·δ^p/(δ^p + dref^p)`. É **crescente em δ**: reduz
perda em amplitude baixa e satura em 1 — a direção exata que a inclinação pede.

Correção necessária, lida da tabela acima (fração da perda do modelo):

| amp | 0,25 | 0,30 | 0,40 | 0,50 | 0,60 | 0,80 |
|---|---:|---:|---:|---:|---:|---:|
| `g` alvo | 0,51 | 0,65 | 0,72 | 0,83 | 0,91 | 1,04 |

⚠️ **Duas ressalvas registradas antes de qualquer prereg:** (a) o gate **satura em 1** e não
sabe *aumentar* perda, então a `amp0p8` (que precisa de **+4 %**) fica no melhor caso
inalterada — o gate não pode fechá-la; (b) a adoção do `s1_amp_gate` foi deixada
**INCONCLUSIVA** em 08-01 porque a Fig. 4 do próprio Liu discorda das curvas digitalizadas no
N₉₅ em 3–5×. ⚠️ Aquele veredito é sobre o **relógio** (quando o joelho chega); este achado é
sobre o **nível** e não usa a Fig. 4 — mas usar a mesma forma para as duas coisas exige dizer
qual das duas ela está servindo.

## 7. O que NÃO mudou

Censo **141/205**, fingerprint `85e8104420b0`, fila form-limited **0**, mesa com os mesmos 4
itens — o N agora com **veredito medido** em vez de premissa. Nada foi adotado, nenhuma config
tocada.

## Reprodutibilidade

`py -3.12 New_Theory/ataque_curva.py liu2025_M16_amp0p3` (diagnóstico + doses) e sonda inline
de controle no corpo do commit, que embrulha `rn._effective_overrides` para a fonte inteira —
idioma de `ataque_curva.py`, com o mesmo guarda de constante derivada. Limites sempre por
`rh.limite_sres`; censo sempre por `T.classificar`.
