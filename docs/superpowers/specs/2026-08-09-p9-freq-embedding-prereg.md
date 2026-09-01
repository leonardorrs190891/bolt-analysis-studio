# Prereg — **P-9**: frequência no `EmbeddingLoss`, como **predição zero-refit**

**2026-08-09** · assinatura *"assino tudo"* · gates **IMUTÁVEIS**.

## A forma, e por que esta e não outra

`EmbeddingLoss.rate` calcula `d_delta = remaining·(1−e^{−1/N_emb})` — relógio
**puramente cíclico** — e já tem um gate multiplicativo default-inerte no mesmo
sítio (`stage1_amp_gate`, PR-3). A P-9 acrescenta o irmão de **frequência**:

```python
def stage1_freq_gate(mat, freq):
    n = mat.s1_freq_exp
    if n <= 0.0 or not freq or freq <= 0.0:
        return 1.0                      # DEFAULT: inerte, bit-idêntico
    return (max(mat.s1_freq_ref, 1e-9) / float(freq)) ** n
...
d_delta *= stage1_freq_gate(mat, freq)   # logo após o gate de amplitude
```

**A lei não é minha:** é a mesma que o **D-V** assinou para o canal de flanco —
`d_fret *= (f_ref_fret/freq)**fret_freq_exp` com `fret_freq_exp = 1,0`, *"taxa
de fretting proporcional a 1/f"*. Aqui ela é transferida ao canal de embedding,
com a mesma forma e o mesmo idioma de inércia.

**Leitura física:** se o assentamento tem componente dependente do **tempo**
(consolidação de asperezas), então a frequência maior dá menos tempo por ciclo ⇒
menos embedding por ciclo.

## Identificabilidade — medida ANTES, e ela desenha o teste

| fonte da P-9 | frequências |
|---|---|
| **`YANG_2019`** | **5 Hz (4 curvas) · 10 Hz (1)** ← única que varre |
| `ECCLES_2010` · `LIU_2025` · `LU_2024` · `YANG_2023_AME` | mono-frequência |

Existe **um** contraste limpo: `amp0p6_5Hz` × `amp0p6_10Hz` — **mesma amplitude,
2× em frequência**. Nas mono-frequência o parâmetro só re-escalaria `N_emb`:
não é falsificável lá, e por isso **não é aplicado lá**.

## Zero números fitados

| constante | valor | procedência |
|---|---|---|
| `s1_freq_exp` | **1,0** | **D-V, assinado pelo professor** (1/f no canal de flanco) |
| `s1_freq_ref` | **5,0 Hz** | frequência de calibração do `YANG_2019` — **input**, não fit |

Com `f_ref` = 5 Hz o gate vale **1,0 exato** nas 4 curvas de 5 Hz ⇒ inércia **por
construção**, não por sorte. Só a de **10 Hz** se move, e nada é ajustado nela:
ela é **predição**.

## A direção está NO DADO, medida antes

Mesma amplitude (0,6 mm): viés **+0,0339** a 5 Hz (modelo retém demais) e
**−0,0524** a 10 Hz (modelo perde demais). Ou seja, **o dado perde mais a baixa
frequência** — exatamente o que `(f_ref/f)^n` com n>0 produz. Se fosse o
contrário, esta proposta cairia aqui, sem implementar nada.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **F1** | default `s1_freq_exp=0` ⇒ engine **bit-idêntico** | Δ = 0,000000 nas 205 |
| **F2** | as 4 curvas do `YANG_2019` a **5 Hz** | **bit-idênticas** (gate = 1,0 exato) |
| **F3** | `amp0p6_10Hz` — o viés anda **para zero** | de **−0,0524** para menos negativo |
| **F4** | `amp0p6_10Hz` — melhora em **≥2 das 3** pernas | de 0,0552 / 0,0886 / 0,0365 |
| **F5** | censo | **não cai** (139) |
| **F6** | suíte completa | verde |

⚠️ **F3 é o gate que mata a proposta.** Se o viés da curva de 10 Hz se afastar
de zero, a lei 1/f está errada **neste canal** e a P-9 é falsificada — a
transferência do D-V não vale, e isso é resultado, não fracasso.

⚠️ **Um held-out não existe, e está declarado.** Com um único contraste de
frequência na biblioteca, não há segunda curva de 10 Hz para reter. É a mesma
situação que o D-V declarou (*"o único outro grupo com canal de flanco é
mono-frequência"*). A mitigação é que **nada é fitado**: os dois números vêm de
fora da curva testada.

## Rollback

`.bkp_p9` no engine e no store. Qualquer gate divergente ⇒ restaura e registra.
