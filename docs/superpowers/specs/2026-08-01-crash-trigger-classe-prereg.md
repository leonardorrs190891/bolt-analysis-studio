# Prereg — `crash_trigger_frac` contra a classe "aceleração tardia" (forma EXISTENTE)

**2026-08-01** · o critério de forma foi satisfeito por **7 fontes**
(`aceleracao_tardia_classe.md`). Este prereg testa a forma que **já existe
no engine e nunca foi adotada** — não abre forma nova. Gates antes de medir.

## A forma

`crash_trigger_frac` (§4.30/L14, default **0 = inerte**): gate Hill em
`F_0/F_0_init` que **suprime** o afrouxamento enquanto a pré-carga está
alta e **dispara runaway** ao cruzar a fração. É literalmente o "joelho
tardio" que a classe pede.

## Universo do teste (declarado ANTES)

Fontes com razão de inclinação terminal (dado/modelo) > 2 **e** sem cauda
de fratura declarada — a exclusão é a ressalva do próprio documento da
classe, porque fratura infla o numerador:

- **EXCLUÍDAS por fratura**: LU_2024, YANG_2021 (cauda de fratura
  documentada nas notas de aparato).
- **DENTRO**: YANG_2019 (4), CHU_2026 (6), LIU_2025 (4), SUN (1),
  JCSR (2) — mais as 2 curvas que a triagem marca com razão > 2 nas
  fontes já lidas (liu2022_fig8_t4, rousseau2025_hdpe_t14).

## Gates (imutáveis)

- **G0 (direção, 2 pontos)**: em UMA curva por fonte, `crash_trigger_frac`
  ∈ {0,80; 0,60} tem de mover o fim da curva para BAIXO (mais perda
  tardia). Δ=0 exato ⇒ conferir companheiros ANTES de declarar inerte
  (lição do canal de flanco, hoje). Se agir em <2 fontes: PARA.
- **G1 (classe, o gate que decide)**: com **UM** valor por fonte (1
  número, per-rig), a soma dos MAE das curvas da fonte cai ≥15 % em
  **≥2 fontes independentes**. Menos que isso = não é classe, é caso.
- **G2 (nenhum caso pior)**: nenhuma curva da fonte piora >+0,01 em
  qualquer perna — incluindo as que hoje passam.
- **G3 (procedência)**: `crash_trigger_frac` é fração de F₀ com
  significado físico (limiar de perda de auto-travamento); o valor por
  fonte tem de ser **lido do dado** (fração de F₀ onde a inclinação
  dobra), não varrido às cegas.
- **G4**: adoção ⇒ fingerprint muda ⇒ re-stamp uniforme + censo/_VIVAS/
  docs/páginas/suíte no mesmo commit.
- **INCONCLUSIVO**: se o gate agir mas exigir valor diferente por curva
  DENTRO da mesma fonte, não é constante per-rig — documentar e parar.

## Previsão registrada

O gate suprime cedo e acelera tarde ⇒ espera-se **melhora do σ_res**
(a perna que domina 50 % das reprovações) e **piora possível do início**
das curvas que já batem o começo. O risco real é o G2: as fontes têm
curvas que já passam, e o gate mexe em todas.
