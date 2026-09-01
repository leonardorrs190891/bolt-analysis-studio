# PR-3 `k_dmg_all` — forma construída, G0/G1 passam, **G2 falha 3/5**: a classe se PARTE em duas

**2026-08-01** · autorização *"faça a opção mais robusta"*; prereg
`2026-08-01-amplificador-tardio-pr3`. **Nenhuma adoção**; censo
`129/205` e fingerprint `a410d6537c83` intactos. A forma fica no engine,
**default-inerte e testada**.

## A escolha de projeto (por que esta é a robusta)

A classe exige agir no **canal dominante de cada fonte**, e ele muda. Um
amplificador **por canal** exigiria escolher o "dominante" caso a caso —
atribuição *a posteriori* que a própria regra do repo desautoriza. O
amplificador do **total** não precisa saber qual é:

```
dF_0_total ·= (1 + k_dmg_all · D)        # D = surface_damage existente
```

Um número, nenhum estado novo, `dF_0` sim / `dE` não (padrão do
`k_dmg_wear`, conservação por `U_released`).

## Gates

| gate | resultado |
|---|---|
| **G0 inércia** | ✅ `k_dmg_all=0` ⇒ trajetória **array-equal** |
| **G1 conservação** | ✅ residual 1,06 → 1,60 J (base 0,69 J) — mesma ordem |
| **G2 direção (≥4/5)** | ❌ **3/5** |
| G3–G6 | não executados (G2 é bloqueante) |

Onde AGE, age forte e na direção certa: YANG_2019 fim 0,843 → 0,594
(dado 0,727 — **passa pelo valor medido**), CHU 0,606 → 0,115 (dado
0,142), SUN 0,048 → 0,045.

## Por que falha nas outras duas — e é diagnóstico, não azar

Medi o acumulador, que é o companheiro obrigatório do amplificador:

| fonte | D final | δ imposto | age? |
|---|---:|---:|:--:|
| YANG_2019 | **0,939** | 0,4 mm | ✅ |
| CHU_2026 | **0,612** | 0,4 mm | ✅ |
| SUN | 0,019 | 0,3 mm | ✅ (fraco) |
| LIU_2025 | **0,000** | 0,3 mm | ❌ |
| JCSR_2023 | **0,000** | 0,0 mm | ❌ |

`D` cresce **da dissipação por slip**. No JCSR não há slip nenhum
(δ = 0: é creep em ambiente corrosivo) e no LIU_2025 a incubação adotada
(`slip_onset_W = 250 kJ`) mantém o canal de slip fechado nessa amplitude.
⇒ **o amplificador é estruturalmente inerte onde a perda não é dirigida
por slip** — exatamente o que o prereg registrou como previsão antes de
medir ("fontes de creep puro podem ter D≈0 e o amplificador nasce inerte
lá").

## O achado: "aceleração tardia" NÃO é uma classe, são DUAS

| sub-classe | fontes | acumulador possível |
|---|---|---|
| **dirigida por slip** | YANG_2019, CHU_2026, SUN (e LU/YANG_2021, fora por fratura) | `D` (existe e funciona) |
| **não dirigida por slip** | JCSR_2023 (creep+corrosão, δ=0), LIU_2025 (fadiga, slip incubado) | **não existe** — precisaria de acumulador de TEMPO/ambiente |

Isso reinterpreta o veredicto de ontem: a busca no engine não fechou
porque falta "um" mecanismo — falta **um acumulador para a sub-classe
sem slip**. Para a sub-classe COM slip, o mecanismo agora existe.

## Próximo passo legítimo (não é gate-shopping)

Um prereg **re-escopado à sub-classe dirigida por slip** é honesto porque
o critério de escopo é **mecanicista e verificável a priori** (`D` só
cresce com dissipação de slip; JCSR tem δ=0 por definição do ensaio), não
"as fontes onde melhorou". O resultado de hoje fica registrado como está:
**G2 falhou no escopo que eu mesmo declarei**.
