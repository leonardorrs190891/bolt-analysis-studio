# Campanha de validação de generalização — varredura paramétrica

**Data:** 2026-06-20
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (PhD) + Claude Code
**Status:** Protocolo experimental. Habilita a prova decisiva "modelo vs curve-fitting".
**Relacionado:** `New_Theory/MODEL_LEGITIMACY.md` (§4.2, §6), `cross_validation.py`,
`New_Theory/parametric_validation.py` (o arnês que consome estes dados),
`docs/superpowers/specs/2026-05-17-calibration-experiments.md` (Exp 1–5, complementar).

---

## 0. Por que esta campanha existe

A validação atual (`cross_validation.py`) mostrou: o modelo **reproduz** dentro de
uma condição, mas os 4 estudos que temos (nova/reusada/sobretorque/reaperto) são
**estados físicos distintos num só carregamento** — não dá pra separar
"curve-fitting" de "estados diferentes". A prova decisiva de **generalização**
exige variar o **carregamento controlável** mantendo o **estado de superfície
fixo**, calibrar num subconjunto e **predizer** o resto.

Isto é **diferente** de Exp 1–5 (aquele spec **mede** as constantes físicas
isoladamente). Aqui a meta é **predizer**, não ajustar.

**Princípio-chave:** fixar a condição de superfície (sempre **nova**, montagem
fresca, mesmo par tribológico) para que a *única* coisa que varia seja o
carregamento que o modelo recebe como entrada (δ, F₀, f). Assim qualquer falha de
predição é do modelo, não de um estado físico diferente.

---

## 1. Matriz mínima (fatorial reduzido)

Junta: **M16 nova**, montagem fresca a cada corpo de prova, mesmo lote/lubrificação.
Carregamento: cisalhante (Junker), disp-controlled, N = 2500 ciclos, f = 0.5 Hz.

| Fator | Níveis | Por quê |
|---|---|---|
| δ (amplitude transversal) | **0.30, 0.50, 0.70 mm** | driver primário de slip/wear; testa a escala da taxa |
| F₀ (pré-carga) | **40, 60 kN** | testa a dependência de pré-carga (Φ, F_slip, k_j) |
| f (frequência) | 0.5 Hz (fixo) | dependência fraca (só creep ~log t); opcional 2º nível |

**Matriz:** 3 (δ) × 2 (F₀) = **6 células**, cada uma com **3 réplicas** (corpos de
prova independentes) → **18 ensaios**. As réplicas dão a escala de ruído (a barra
contra a qual o erro de predição é julgado).

Opcional (reforço): +1 nível de f (ex. 5 Hz) em 1 célula → testa o ramo de creep.

---

## 2. Medições por ensaio

1. **Curva de decaimento F₀(N)** — `cycle, F_over_F0` (CSV 2 colunas, como os atuais
   em `New_Theory/`). É o observável primário.
2. **Ângulo de afrouxamento θ_loose(N)** (se instrumentável) — observável
   **secundário independente**. O modelo prediz θ_loose junto com F₀; acertar os
   DOIS com o mesmo parâmetro é evidência forte de física (curve-fit de uma curva
   não prediz a outra).
3. Metadados: δ, F₀ medido, f, lote, lubrificação, temperatura.

---

## 3. Testes de predição que isto habilita (o decisivo)

Rodados por `parametric_validation.py`:

| Teste | Treina em | Prediz | O que prova |
|---|---|---|---|
| **Interpolação δ** | δ∈{0.30, 0.70} | δ=0.50 | a escala wear∝slip está certa |
| **Extrapolação δ** | δ∈{0.30, 0.50} | δ=0.70 | extrapola fora do range (mais duro) |
| **Cross-pré-carga** | F₀=40 kN | F₀=60 kN | dependência de F₀ (Φ, F_slip) |
| **Leave-one-cell-out** | 5 células | a 6ª | generalização geral |
| **Observável secundário** | F₀ curves | θ_loose | física, não ajuste de 1 curva |

**Regra:** o parâmetro físico é calibrado **uma vez** no conjunto de treino; só
estado físico nomeado pode mudar (aqui, nada muda — superfície fixa). Predição com
os **mesmos** tuners.

---

## 4. Critério de aceite (quando dizer "é modelo")

- **MAE de predição OOS ≤ ~1.5× o scatter entre réplicas** da célula predita.
  (Não dá pra prever melhor que o próprio ruído experimental.)
- O **mesmo** conjunto de tuners (≤3 livres, identificáveis) serve todas as células.
- θ_loose predito dentro da incerteza de medição.

Se cumprido: a calibração é **estimação de parâmetro físico**, não curve-fitting —
porque um único conjunto prediz carregamentos não vistos + um observável que não
foi ajustado.

Se falhar de forma sistemática (não aleatória): aponta **mecanismo errado** (não
"mais um tuner"). Ver `MODEL_LEGITIMACY.md` §7 (o que falsificaria).

---

## 5. Formato dos dados para o arnês

Manifesto `New_Theory/sweep_manifest.csv` (uma linha por ensaio):

```
id, delta_mm, F0_N, freq_Hz, n_cycles, csv_path[, theta_csv_path]
S01, 0.30, 40000, 0.5, 2500, sweep/S01.csv
S02, 0.50, 40000, 0.5, 2500, sweep/S02.csv
...
```

Cada `csv_path`: 2 colunas `cycle, F_over_F0` (header opcional). Quando o manifesto
existir, `parametric_validation.py` roda os testes da §3 automaticamente. Sem
manifesto, ele roda um **auto-teste sintético** (gera dados do próprio modelo +
ruído) que prova que o arnês funciona e que o modelo generaliza pra sua própria
varredura.

---

## 6. Custo / esforço

18 ensaios × ~2500 ciclos a 0.5 Hz ≈ 1h25 de bancada cada (≈ 2500/0.5/3600). Em
paralelo/lotes, ~1–2 semanas de bancada. É a campanha **mínima** que converte o
argumento estrutural (formas + acoplamentos + parcimônia) em **evidência numérica
de generalização** — o único passo que ainda falta para fechar a questão
"modelo vs ajuste de curva".
